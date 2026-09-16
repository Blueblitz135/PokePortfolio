"""Search TCGdex and normalize provider card/set payloads for the application."""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import httpx

from app.models.enums import ExternalSource
from app.schemas.card_search import CardSearchResult
from app.schemas.market_pricing import TCGPlayerComparison, TCGPlayerVariant
from app.adapters.card_identity import card_name_matches, card_number_matches, set_name_matches


class TCGdexError(Exception):
    """Raised when TCGdex cannot provide a valid response."""


class TCGdexAdapter:
    """Async metadata client that enriches search hits with card and set details."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        max_results: int = 20,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Configure the provider base URL, timeout, result limit, and test transport."""

        if max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

        self.base_url = f"{base_url.rstrip('/')}/"
        self.timeout_seconds = timeout_seconds
        self.max_results = max_results
        self.transport = transport
        self._set_year_cache: dict[str, int] = {}

    async def search_cards(self, query: str) -> list[CardSearchResult]:
        """Search names, fetch details concurrently, and return normalized cards."""

        normalized_query = query.strip()
        if not normalized_query:
            return []

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            search_payload = await self._request_json(
                client,
                "cards",
                params={
                    "name": normalized_query,
                    "pagination:page": 1,
                    "pagination:itemsPerPage": self.max_results,
                },
            )
            if not isinstance(search_payload, list):
                raise TCGdexError("TCGdex returned an invalid card search response.")

            card_ids = _card_ids(search_payload, self.max_results)
            if not card_ids:
                return []

            card_payloads = await asyncio.gather(
                *(self._get_card(client, card_id) for card_id in card_ids)
            )
            set_years = await self._get_set_years(client, card_payloads)

        results: list[CardSearchResult] = []
        for card_payload in card_payloads:
            if card_payload is None:
                continue
            result = _normalize_card(card_payload, set_years)
            if result is not None:
                results.append(result)
        return results

    async def fetch_tcgplayer_prices(self, metadata, rate: Decimal) -> TCGPlayerComparison:
        """Read only TCGPlayer prices after verifying the local card identity."""
        if not rate.is_finite() or rate <= 0:
            raise TCGdexError("A positive USD to CAD conversion rate is required.")
        card_id = metadata.external_id if metadata.external_source == ExternalSource.TCGDEX else None
        if not card_id:
            candidates = await self.search_cards(metadata.name)
            matches = [c for c in candidates if set_name_matches(c.set_name, metadata.set_name)
                       and card_number_matches(c.card_number, metadata.card_number, metadata.set_total)
                       and card_name_matches(c.name, metadata.name)]
            if len(matches) != 1:
                return TCGPlayerComparison(note="No unique card identity match was found.")
            card_id = matches[0].external_id
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds, transport=self.transport) as client:
            card = await self._get_card(client, card_id)
        if not card or not card_name_matches(card.get("name"), metadata.name) or not set_name_matches((card.get("set") or {}).get("name"), metadata.set_name) or not card_number_matches(card.get("localId"), metadata.card_number, metadata.set_total):
            return TCGPlayerComparison(note="Card identity could not be verified.")
        pricing = (card.get("pricing") or {}).get("tcgplayer") or {}
        if pricing.get("unit") != "USD":
            return TCGPlayerComparison(note="USD TCGPlayer pricing is unavailable.")
        variants = []
        for printing, values in pricing.items():
            if not isinstance(values, dict):
                continue
            fields = {target: _cad_price(values.get(key), rate) for key, target in {
                "marketPrice": "market_price_cad", "lowPrice": "low_price_cad",
                "midPrice": "median_price_cad", "highPrice": "high_price_cad",
            }.items()}
            if any(value is not None for value in fields.values()):
                variants.append(TCGPlayerVariant(printing=printing, **fields))
        updated = pricing.get("updated")
        try:
            observed = datetime.fromisoformat(updated.replace("Z", "+00:00")) if isinstance(updated, str) else datetime.fromtimestamp(updated, timezone.utc)
        except (ValueError, TypeError, OSError, OverflowError):
            observed = None
        return TCGPlayerComparison(state="available" if variants else "unavailable", observed_at=observed, usd_to_cad_rate=rate, variants=variants)

    async def _get_card(
        self, client: httpx.AsyncClient, card_id: str
    ) -> dict[str, Any] | None:
        """Fetch one card payload, treating provider 404 as an absent result."""

        payload = await self._request_json(
            client, f"cards/{card_id}", allow_not_found=True
        )
        if payload is None:
            return None
        if not isinstance(payload, dict):
            raise TCGdexError("TCGdex returned an invalid card detail response.")
        return payload

    async def _get_set_years(
        self,
        client: httpx.AsyncClient,
        card_payloads: list[dict[str, Any] | None],
    ) -> dict[str, int | None]:
        """Fetch release years once per unique set represented in the result batch."""

        set_ids = _set_ids(card_payloads)
        uncached_set_ids = [
            set_id for set_id in set_ids if set_id not in self._set_year_cache
        ]
        uncached_years = await asyncio.gather(
            *(self._get_set_year(client, set_id) for set_id in uncached_set_ids)
        )

        for set_id, year in zip(uncached_set_ids, uncached_years, strict=True):
            if year is not None:
                self._set_year_cache[set_id] = year

        return {set_id: self._set_year_cache.get(set_id) for set_id in set_ids}

    async def _get_set_year(
        self, client: httpx.AsyncClient, set_id: str
    ) -> int | None:
        """Fetch and parse one set's release year, tolerating missing set details."""

        try:
            payload = await self._request_json(
                client, f"sets/{set_id}", allow_not_found=True
            )
        except TCGdexError:
            return None

        if not isinstance(payload, dict):
            return None
        return _year_from_release_date(payload.get("releaseDate"))

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        *,
        params: dict[str, str | int] | None = None,
        allow_not_found: bool = False,
    ) -> Any:
        """Send a GET and translate transport or invalid-JSON errors."""

        try:
            response = await client.get(path, params=params)
            if allow_not_found and response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise TCGdexError("TCGdex request failed.") from exc


def _card_ids(search_payload: list[Any], max_results: int) -> list[str]:
    """Extract unique non-empty card IDs up to the configured result limit."""

    card_ids: list[str] = []
    seen_ids: set[str] = set()

    for item in search_payload[:max_results]:
        if not isinstance(item, dict):
            continue
        card_id = _text(item.get("id"))
        if card_id is None or card_id in seen_ids:
            continue
        card_ids.append(card_id)
        seen_ids.add(card_id)

    return card_ids


def _set_ids(card_payloads: list[dict[str, Any] | None]) -> list[str]:
    """Extract unique set IDs needed for release-year enrichment."""

    set_ids: list[str] = []

    for card in card_payloads:
        if card is None or not isinstance(card.get("set"), dict):
            continue
        set_id = _text(card["set"].get("id"))
        if set_id is not None and set_id not in set_ids:
            set_ids.append(set_id)

    return set_ids


def _normalize_card(
    card: dict[str, Any], set_years: dict[str, int | None]
) -> CardSearchResult | None:
    """Convert a complete enough TCGdex card payload into the internal schema."""

    set_data = card.get("set")
    if not isinstance(set_data, dict):
        return None

    external_id = _text(card.get("id"))
    name = _text(card.get("name"))
    set_name = _text(set_data.get("name"))
    set_id = _text(set_data.get("id"))
    card_number = _text(card.get("localId"))
    if (
        external_id is None
        or name is None
        or set_name is None
        or set_id is None
        or card_number is None
    ):
        return None

    card_count = set_data.get("cardCount")
    set_total = (
        _text(card_count.get("official")) if isinstance(card_count, dict) else None
    )
    image_base = _text(card.get("image"))

    return CardSearchResult(
        external_source=ExternalSource.TCGDEX,
        external_id=external_id,
        name=name,
        set_name=set_name,
        set_id=set_id,
        year=set_years.get(set_id),
        card_number=card_number,
        set_total=set_total,
        rarity=_text(card.get("rarity")),
        image_url=f"{image_base.rstrip('/')}/high.webp" if image_base else None,
    )


def _text(value: Any) -> str | None:
    """Coerce provider string/integer values to trimmed, non-empty text."""

    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (str, int)):
        return None

    text = str(value).strip()
    return text or None


def _year_from_release_date(value: Any) -> int | None:
    """Parse the year from an ISO date string, returning None when malformed."""

    release_date = _text(value)
    if release_date is None:
        return None

    year = release_date[:4]
    return int(year) if len(year) == 4 and year.isdigit() else None


def _cad_price(value: Any, rate: Decimal) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        amount = Decimal(str(value))
        return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) if amount.is_finite() and amount >= 0 else None
    except (InvalidOperation, ValueError):
        return None
