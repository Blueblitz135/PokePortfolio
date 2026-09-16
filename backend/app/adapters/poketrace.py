"""Fetch PokeTrace card/sealed evidence and normalize USD price tiers to CAD."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import httpx
from app.adapters.card_identity import (
    card_name_matches,
    card_number_matches,
    set_name_matches,
)


CAD_QUANTUM = Decimal("0.01")


class PokeTraceError(Exception):
    """Raised when PokeTrace cannot provide valid market data."""


class PokeTraceConfigurationError(PokeTraceError):
    """Raised when the PokeTrace integration is not configured."""


@dataclass(frozen=True)
class PokeTraceAssetLookup:
    """Local identity, product classification, and optional price tier to match."""

    name: str
    set_name: str | None
    product_type: str
    product_family: str
    card_number: str | None = None
    set_total: str | None = None
    tier: str | None = None
    printing: str | None = None


@dataclass(frozen=True)
class PokeTraceTierQuote:
    """One source/tier quote normalized to CAD with supporting market signals."""

    source: str
    tier: str
    average_price_cad: Decimal
    low_price_cad: Decimal | None
    high_price_cad: Decimal | None
    sale_count: int | None
    trend: str | None
    confidence: str | None


@dataclass(frozen=True)
class PokeTraceMarketData:
    """Matched provider item and its normalized current quotes."""

    provider_card_id: str
    provider_card_name: str
    source_currency: str
    observed_at: datetime | None
    quotes: tuple[PokeTraceTierQuote, ...]


class PokeTraceAdapter:
    """Fetch PokeTrace card and sealed-product market data in normalized CAD."""

    def __init__(
        self,
        api_key: str | None,
        usd_to_cad_rate: Decimal | None,
        base_url: str = "https://api.poketrace.com/v1",
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        """Configure credentials, explicit FX normalization, and HTTP behavior."""

        self.api_key = api_key.strip() if api_key else None
        self.usd_to_cad_rate = usd_to_cad_rate
        self.base_url = f"{base_url.rstrip('/')}/"
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    @property
    def is_configured(self) -> bool:
        """Require both a real API key and positive USD-to-CAD rate."""

        return _is_usable_key(self.api_key) and bool(
            self.usd_to_cad_rate and self.usd_to_cad_rate > 0
        )

    async def fetch_market_data(
        self, lookup: PokeTraceAssetLookup
    ) -> PokeTraceMarketData | None:
        """Return exact asset evidence, or None when the search has no exact match."""

        self._validate_configuration()
        params: dict[str, str | int] = {
            "search": lookup.name,
            "game": "pokemon",
            "market": "US",
            "product_type": lookup.product_type,
            "product_family": lookup.product_family,
            "limit": 20,
        }
        if lookup.card_number and lookup.set_total:
            params["card_number"] = f"{lookup.card_number}/{lookup.set_total}"

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            payload = await self._request_json(client, "cards", params=params)
            card = _find_exact_card(payload, lookup)
            if card is None:
                return None
            # Search results may omit price tiers. Retrieve the matched card.
            if "prices" not in card:
                card_id = _text(card.get("id"))
                if not card_id:
                    raise PokeTraceError("PokeTrace returned an invalid card identifier.")
                detail = await self._request_json(client, f"cards/{card_id}", params={})
                if not isinstance(detail, dict):
                    raise PokeTraceError("PokeTrace returned an invalid card response.")
                card = _find_exact_card({"data": [detail.get("data")]}, lookup)
                if card is None:
                    return None

        currency = _text(card.get("currency")) or "USD"
        if currency.upper() != "USD":
            raise PokeTraceError("PokeTrace returned an unsupported currency.")

        quotes = _parse_quotes(
            card.get("prices"), lookup.tier, self.usd_to_cad_rate or Decimal("0")
        )
        provider_card_id = _text(card.get("id"))
        provider_card_name = _text(card.get("name"))
        if provider_card_id is None or provider_card_name is None:
            raise PokeTraceError("PokeTrace returned an invalid card identifier.")

        return PokeTraceMarketData(
            provider_card_id=provider_card_id,
            provider_card_name=provider_card_name,
            source_currency=currency.upper(),
            observed_at=_datetime(card.get("lastUpdated")),
            quotes=quotes,
        )

    def _validate_configuration(self) -> None:
        """Fail before network access when credentials or FX rate are unusable."""

        if not _is_usable_key(self.api_key):
            raise PokeTraceConfigurationError("POKETRACE_API_KEY is not configured.")
        if self.usd_to_cad_rate is None or self.usd_to_cad_rate <= 0:
            raise PokeTraceConfigurationError(
                "POKETRACE_USD_TO_CAD_RATE must be a positive number."
            )

    async def _request_json(
        self,
        client: httpx.AsyncClient,
        path: str,
        *,
        params: dict[str, str | int],
    ) -> Any:
        """Send an authenticated GET and translate transport/JSON failures."""

        try:
            response = await client.get(
                path,
                params=params,
                headers={"X-API-Key": self.api_key or ""},
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise PokeTraceError("PokeTrace request failed.") from exc


def _is_usable_key(value: str | None) -> bool:
    """Treat missing and documented sample values as unconfigured credentials."""

    if not value:
        return False
    normalized = value.strip().casefold()
    return normalized not in {
        "dummy",
        "placeholder",
        "replace_with_poketrace_api_key",
    }


def _find_exact_card(
    payload: Any, lookup: PokeTraceAssetLookup
) -> dict[str, Any] | None:
    """Select only a provider result matching the local asset identity."""

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise PokeTraceError("PokeTrace returned an invalid card response.")

    matches = []
    for item in payload["data"]:
        if not isinstance(item, dict):
            continue
        name_matches = (
            card_name_matches(item.get("name"), lookup.name)
            if lookup.card_number
            else _normalized_text(item.get("name")) == _normalized_text(lookup.name)
        )
        if not name_matches:
            continue
        if _normalized_text(item.get("productType")) != _normalized_text(
            lookup.product_type
        ):
            continue
        provider_set = item.get("set")
        provider_set_name = (
            provider_set.get("name") if isinstance(provider_set, dict) else None
        )
        if lookup.set_name and not set_name_matches(provider_set_name, lookup.set_name):
            continue
        if lookup.card_number and not _matches_card_number(
            item.get("cardNumber"), lookup.card_number, lookup.set_total
        ):
            continue
        if lookup.printing and _normalized_text(
            item.get("variant")
        ) != _normalized_text(lookup.printing):
            continue
        matches.append(item)
    return matches[0] if len(matches) == 1 else None


def _matches_card_number(
    provider_value: Any, card_number: str, set_total: str | None
) -> bool:
    """Compare structured card number and optional set total."""

    return card_number_matches(provider_value, card_number, set_total)


def _parse_quotes(
    prices: Any, requested_tier: str | None, usd_to_cad_rate: Decimal
) -> tuple[PokeTraceTierQuote, ...]:
    """Validate provider price tiers, filter if requested, and normalize to CAD."""

    if not isinstance(prices, dict):
        return ()

    quotes: list[PokeTraceTierQuote] = []
    for source, tiers in prices.items():
        if not isinstance(tiers, dict):
            continue
        for tier, price_data in tiers.items():
            if requested_tier and _normalized_text(tier) != _normalized_text(
                requested_tier
            ):
                continue
            if not isinstance(price_data, dict):
                continue
            average = _decimal(price_data.get("avg"))
            if average is None or average < 0:
                continue
            quotes.append(
                PokeTraceTierQuote(
                    source=str(source),
                    tier=str(tier),
                    average_price_cad=_to_cad(average, usd_to_cad_rate),
                    low_price_cad=_optional_cad(
                        price_data.get("low"), usd_to_cad_rate
                    ),
                    high_price_cad=_optional_cad(
                        price_data.get("high"), usd_to_cad_rate
                    ),
                    sale_count=_integer(price_data.get("saleCount")),
                    trend=_text(price_data.get("trend")),
                    confidence=_text(price_data.get("confidence")),
                )
            )
            if len(quotes) == 12:
                return tuple(quotes)
    return tuple(quotes)


def _to_cad(value: Decimal, rate: Decimal) -> Decimal:
    """Convert USD to a two-decimal CAD monetary amount."""

    return (value * rate).quantize(CAD_QUANTUM, rounding=ROUND_HALF_UP)


def _optional_cad(value: Any, rate: Decimal) -> Decimal | None:
    """Parse and convert an optional non-negative provider price."""

    parsed = _decimal(value)
    return _to_cad(parsed, rate) if parsed is not None and parsed >= 0 else None


def _text(value: Any) -> str | None:
    """Coerce provider string/integer identifiers to non-empty text."""

    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (str, int)):
        return None
    text = str(value).strip()
    return text or None


def _normalized_text(value: Any) -> str:
    """Produce case-insensitive comparison text from an external value."""

    return (_text(value) or "").casefold().replace("_", " ")


def _decimal(value: Any) -> Decimal | None:
    """Parse an external numeric value without binary floating-point conversion."""

    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _integer(value: Any) -> int | None:
    """Parse an integer-like provider value, returning None when invalid."""

    try:
        return int(value) if value is not None and not isinstance(value, bool) else None
    except (TypeError, ValueError):
        return None


def _datetime(value: Any) -> datetime | None:
    """Parse an ISO timestamp and normalize a trailing UTC Z marker."""

    text = _text(value)
    if text is None:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
