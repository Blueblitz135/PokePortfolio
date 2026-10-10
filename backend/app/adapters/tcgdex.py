"""Search TCGdex and normalize provider card/set payloads for the application."""

import asyncio
from dataclasses import dataclass
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


@dataclass(frozen=True)
class TCGdexCardReference:
    """Stable cross-provider identifiers and printing data for one card."""

    tcgplayer_id: str | None
    printings: tuple[str, ...]
    is_tcg_pocket: bool


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
        self._set_metadata_cache: dict[str, tuple[int | None, str | None]] = {}

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
            set_metadata = await self._get_set_metadata(client, card_payloads)

        results: list[CardSearchResult] = []
        for card_payload in card_payloads:
            if card_payload is None:
                continue
            result = _normalize_card(card_payload, set_metadata)
            if result is not None:
                results.append(result)
        return results

    async def fetch_card_reference(self, metadata) -> TCGdexCardReference | None:
        """Resolve one saved card to stable pricing IDs after verifying identity."""

        card = await self._fetch_verified_card(metadata)
        if card is None:
            return None
        printings = tuple(_card_printings(card))
        return TCGdexCardReference(
            tcgplayer_id=_tcgplayer_id(card, metadata.variant),
            printings=printings,
            is_tcg_pocket=_is_tcg_pocket_card(card),
        )

    async def fetch_tcgplayer_prices(self, metadata, rate: Decimal) -> TCGPlayerComparison:
        """Read only TCGPlayer prices after verifying the local card identity."""
        if not rate.is_finite() or rate <= 0:
            raise TCGdexError("A positive USD to CAD conversion rate is required.")
        card = await self._fetch_verified_card(metadata)
        if card is None:
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

    async def _fetch_verified_card(self, metadata) -> dict[str, Any] | None:
        """Fetch a card detail payload and reject a changed or ambiguous identity."""

        card_id = metadata.external_id if metadata.external_source == ExternalSource.TCGDEX else None
        if not card_id:
            candidates = await self.search_cards(metadata.name)
            matches = [c for c in candidates if set_name_matches(c.set_name, metadata.set_name)
                       and card_number_matches(c.card_number, metadata.card_number, metadata.set_total)
                       and card_name_matches(c.name, metadata.name)]
            if len(matches) != 1:
                return None
            card_id = matches[0].external_id
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout_seconds, transport=self.transport) as client:
            card = await self._get_card(client, card_id)
        if not card or not card_name_matches(card.get("name"), metadata.name) or not set_name_matches((card.get("set") or {}).get("name"), metadata.set_name) or not card_number_matches(card.get("localId"), metadata.card_number, metadata.set_total):
            return None
        return card

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

    async def _get_set_metadata(
        self,
        client: httpx.AsyncClient,
        card_payloads: list[dict[str, Any] | None],
    ) -> dict[str, tuple[int | None, str | None]]:
        """Fetch release year and series once per represented set."""

        set_ids = _set_ids(card_payloads)
        uncached_set_ids = [
            set_id for set_id in set_ids if set_id not in self._set_metadata_cache
        ]
        uncached_metadata = await asyncio.gather(
            *(self._get_set_details(client, set_id) for set_id in uncached_set_ids)
        )

        for set_id, metadata in zip(uncached_set_ids, uncached_metadata, strict=True):
            self._set_metadata_cache[set_id] = metadata

        return {set_id: self._set_metadata_cache.get(set_id, (None, None)) for set_id in set_ids}

    async def _get_set_details(
        self, client: httpx.AsyncClient, set_id: str
    ) -> tuple[int | None, str | None]:
        """Fetch a set's release year and series, tolerating missing details."""

        try:
            payload = await self._request_json(
                client, f"sets/{set_id}", allow_not_found=True
            )
        except TCGdexError:
            return (None, None)

        if not isinstance(payload, dict):
            return (None, None)
        series = payload.get("serie")
        series_id = _text(series.get("id")) if isinstance(series, dict) else None
        return (_year_from_release_date(payload.get("releaseDate")), series_id)

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
    card: dict[str, Any],
    set_metadata: dict[str, tuple[int | None, str | None]],
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
    year, series_id = set_metadata.get(set_id, (None, None))
    if series_id == "tcgp" or _is_tcg_pocket_card(card):
        return None

    return CardSearchResult(
        external_source=ExternalSource.TCGDEX,
        external_id=external_id,
        name=name,
        set_name=set_name,
        set_id=set_id,
        series_id=series_id,
        year=year,
        card_number=card_number,
        set_total=set_total,
        rarity=_text(card.get("rarity")),
        printings=_card_printings(card),
        image_url=f"{image_base.rstrip('/')}/high.webp" if image_base else None,
    )


def _card_printings(card: dict[str, Any]) -> list[str]:
    """Return canonical physical printings from TCGdex variant metadata."""

    printings: list[str] = []
    detailed = card.get("variants_detailed")
    if isinstance(detailed, list):
        for variant in detailed:
            if not isinstance(variant, dict):
                continue
            printing = _printing_label(variant.get("type"))
            if printing and printing not in printings:
                printings.append(printing)
    if printings:
        return printings

    variants = card.get("variants")
    if isinstance(variants, dict):
        for key, present in variants.items():
            printing = _printing_label(key) if present else None
            if printing and printing not in printings:
                printings.append(printing)
    return printings


def _printing_label(value: Any) -> str | None:
    normalized = (_text(value) or "").casefold().replace("_", "-")
    return {
        "holo": "Holofoil",
        "holofoil": "Holofoil",
        "reverse": "Reverse Holofoil",
        "reverse-holo": "Reverse Holofoil",
        "reverse-holofoil": "Reverse Holofoil",
        "normal": "Normal",
        "firstedition": "1st Edition",
        "first-edition": "1st Edition",
    }.get(normalized)


def _tcgplayer_id(card: dict[str, Any], requested_printing: str | None) -> str | None:
    """Extract one unambiguous TCGPlayer product ID from TCGdex detail data."""

    identifiers: list[str] = []
    detailed = card.get("variants_detailed")
    if isinstance(detailed, list):
        for variant in detailed:
            if not isinstance(variant, dict):
                continue
            printing = _printing_label(variant.get("type"))
            if requested_printing and printing != requested_printing:
                continue
            third_party = variant.get("thirdParty")
            identifier = (
                _text(third_party.get("tcgplayer"))
                if isinstance(third_party, dict)
                else None
            )
            if identifier and identifier not in identifiers:
                identifiers.append(identifier)
    return identifiers[0] if len(identifiers) == 1 else None


def _is_tcg_pocket_card(card: dict[str, Any]) -> bool:
    set_data = card.get("set")
    if not isinstance(set_data, dict):
        return False
    paths = [set_data.get("logo"), set_data.get("symbol"), card.get("image")]
    return any("/tcgp/" in str(value).casefold() for value in paths if value)


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
