"""Fetch JustTCG raw-card quotes/history and normalize supported prices to CAD."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import httpx
from app.adapters.card_identity import (
    card_name_matches,
    card_number_matches,
    set_name_matches,
)

from app.models.enums import RawCardCondition


USD_TO_CAD_QUANTUM = Decimal("0.01")
JUSTTCG_CONFIDENCE = Decimal("0.700")


class JustTCGError(Exception):
    """Raised when JustTCG cannot provide a valid raw-card price."""


class JustTCGConfigurationError(JustTCGError):
    """Raised when the optional JustTCG integration is not configured."""


@dataclass(frozen=True)
class RawCardPriceLookup:
    """Local card identity and condition required for an exact provider match."""

    name: str
    set_name: str
    card_number: str
    condition: RawCardCondition | None
    set_total: str | None = None
    printing: str | None = None
    grading_company: str | None = None
    grade: str | None = None


@dataclass(frozen=True)
class ExternalPriceQuote:
    """Normalized current quote plus confidence and provider traceability fields."""

    market_price_per_unit: Decimal
    currency: str
    confidence: Decimal
    observed_at: datetime
    metadata: dict[str, str]


@dataclass(frozen=True)
class PriceHistoryPoint:
    """One normalized observation in a raw-card price series."""

    observed_at: datetime
    market_price_per_unit: Decimal


@dataclass(frozen=True)
class RawCardPriceHistory:
    """Chronological CAD history and provider-period growth for one variant."""

    currency: str
    duration: str
    points: tuple[PriceHistoryPoint, ...]
    growth_percent: Decimal | None
    current_price_cad: Decimal | None = None
    current_observed_at: datetime | None = None
    printing: str | None = None
    provider_card_id: str | None = None
    provider_variant_id: str | None = None


class JustTCGAdapter:
    """Fetch and normalize JustTCG v1 raw-card prices.

    JustTCG v1 supplies USD market prices. The caller configures the explicit
    USD-to-CAD rate so this adapter never writes a non-CAD portfolio value.
    """

    def __init__(
        self,
        api_key: str | None,
        usd_to_cad_rate: Decimal | None,
        base_url: str = "https://api.justtcg.com/v1",
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

    async def fetch_raw_card_price(
        self, lookup: RawCardPriceLookup
    ) -> ExternalPriceQuote | None:
        """Return the exact card/condition quote, or None when no variant matches."""

        self._validate_configuration()
        payload = await self._fetch_card_payload(lookup)

        card, variant = _find_exact_variant(payload, lookup)
        if card is None or variant is None:
            return None

        usd_price = _decimal(variant.get("price"))
        updated_at = _timestamp(variant.get("lastUpdated"))
        if usd_price is None or usd_price < 0 or updated_at is None:
            raise JustTCGError("JustTCG returned an invalid price variant.")

        cad_price = (usd_price * self.usd_to_cad_rate).quantize(
            USD_TO_CAD_QUANTUM, rounding=ROUND_HALF_UP
        )
        card_id = _text(card.get("id"))
        variant_id = _text(variant.get("id"))
        if card_id is None or variant_id is None:
            raise JustTCGError("JustTCG returned an invalid card identifier.")

        return ExternalPriceQuote(
            market_price_per_unit=cad_price,
            currency="CAD",
            confidence=JUSTTCG_CONFIDENCE,
            observed_at=updated_at,
            metadata={
                "provider": "justtcg",
                "provider_card_id": card_id,
                "provider_card_uuid": _text(card.get("uuid")) or "",
                "provider_variant_id": variant_id,
                "provider_variant_uuid": _text(variant.get("uuid")) or "",
                "provider_condition": _text(variant.get("condition")) or "",
                "source_market_price_per_unit": str(usd_price),
                "source_currency": "USD",
                "usd_to_cad_rate": str(self.usd_to_cad_rate),
            },
        )

    async def fetch_raw_card_price_history(
        self, lookup: RawCardPriceLookup, duration: str = "90d"
    ) -> RawCardPriceHistory | None:
        """Return normalized chronological history for an exact raw-card variant."""

        self._validate_configuration()
        if duration not in {"7d", "30d", "90d", "180d", "1y"}:
            raise JustTCGError("JustTCG price history duration is invalid.")

        payload = await self._fetch_card_payload(
            lookup, extra_params={"priceHistoryDuration": duration}
        )
        card, variant = _find_exact_variant(payload, lookup)
        if card is None or variant is None:
            return None

        raw_points = variant.get("priceHistory", [])
        if not isinstance(raw_points, list):
            raise JustTCGError("JustTCG returned invalid price history.")

        points: list[PriceHistoryPoint] = []
        for raw_point in raw_points:
            if not isinstance(raw_point, dict):
                continue
            usd_price = _decimal(raw_point.get("p"))
            observed_at = _timestamp(raw_point.get("t"))
            if usd_price is None or usd_price < 0 or observed_at is None:
                continue
            points.append(
                PriceHistoryPoint(
                    observed_at=observed_at,
                    market_price_per_unit=(usd_price * self.usd_to_cad_rate).quantize(
                        USD_TO_CAD_QUANTUM, rounding=ROUND_HALF_UP
                    ),
                )
            )

        points.sort(key=lambda point: point.observed_at)
        first_price = points[0].market_price_per_unit if points else Decimal("0")
        growth_percent = (
            (points[-1].market_price_per_unit - first_price)
            / first_price
            * Decimal("100")
            if first_price > 0 and len(points) > 1
            else None
        )
        current_price = _decimal(variant.get("price"))
        current_observed_at = _timestamp(variant.get("lastUpdated"))
        current_price_cad = None
        if current_price is not None and current_price >= 0 and current_observed_at:
            current_price_cad = (current_price * self.usd_to_cad_rate).quantize(
                USD_TO_CAD_QUANTUM, rounding=ROUND_HALF_UP
            )
        return RawCardPriceHistory(
            currency="CAD",
            duration=duration,
            points=tuple(points),
            growth_percent=growth_percent,
            current_price_cad=current_price_cad,
            current_observed_at=current_observed_at,
            printing=_text(variant.get("printing")),
            provider_card_id=_text(card.get("id")),
            provider_variant_id=_text(variant.get("id")),
        )

    async def _fetch_card_payload(
        self,
        lookup: RawCardPriceLookup,
        extra_params: dict[str, str | int] | None = None,
    ) -> Any:
        """Build provider search parameters and retrieve the card payload."""

        params: dict[str, str | int] = {
            "q": lookup.name,
            "game": "pokemon",
            "number": lookup.card_number,
            "limit": 20,
        }
        if lookup.condition:
            params["condition"] = "D" if lookup.condition == RawCardCondition.DMG else lookup.condition.value
        if extra_params:
            params.update(extra_params)
        path = "cards"
        if lookup.grading_company:
            path = "../v2/cards"
            params.pop("condition", None)
            duration = params.pop("priceHistoryDuration", "90d")
            params.update({
                "graded": "only", "grading_company": lookup.grading_company,
                "grade": lookup.grade or "", "regions": "NA",
                "include": f"price_history.{duration}",
            })

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            if lookup.grading_company:
                # Resolve identity on stable v1 first: v2 search filters differ.
                candidates = await self._request_json(client, "cards", params={
                    "q": lookup.name, "game": "pokemon", "number": lookup.card_number, "limit": 20,
                })
                if not isinstance(candidates, dict) or not isinstance(candidates.get("data"), list):
                    raise JustTCGError("JustTCG returned an invalid card response.")
                cards = [c for c in candidates["data"] if isinstance(c, dict) and _matches_card(c, lookup)]
                if len(cards) != 1:
                    return {"data": []}
                params = {k: v for k, v in params.items() if k not in {"q", "number"}}
                params["card_id"] = cards[0]["id"]
            payload = await self._request_json(client, path, params=params)
            if lookup.grading_company:
                payload = _normalize_graded_payload(payload)
            return payload

    def _validate_configuration(self) -> None:
        """Fail before network access when credentials or FX rate are unusable."""

        if not _is_usable_key(self.api_key):
            raise JustTCGConfigurationError("JUSTTCG_API_KEY is not configured.")
        if self.usd_to_cad_rate is None or self.usd_to_cad_rate <= 0:
            raise JustTCGConfigurationError(
                "JUSTTCG_USD_TO_CAD_RATE must be a positive number."
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
                path, params=params, headers={"x-api-key": self.api_key or ""}
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise JustTCGError("JustTCG request failed.") from exc


def _is_usable_key(value: str | None) -> bool:
    """Treat missing and documented sample values as unconfigured credentials."""

    if not value:
        return False
    normalized = value.strip().casefold()
    return normalized not in {
        "dummy",
        "placeholder",
        "replace_with_justtcg_api_key",
    }


def _find_exact_variant(
    payload: Any, lookup: RawCardPriceLookup
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Find a card identity and condition variant without accepting fuzzy pricing."""

    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise JustTCGError("JustTCG returned an invalid card response.")

    matches = []
    for card in payload["data"]:
        if not isinstance(card, dict) or not _matches_card(card, lookup):
            continue
        variants = card.get("variants")
        if not isinstance(variants, list):
            continue
        for variant in variants:
            if isinstance(variant, dict) and _matches_price_category(variant, lookup):
                if lookup.printing and _normalized_text(
                    variant.get("printing")
                ) != _normalized_text(lookup.printing):
                    continue
                matches.append((card, variant))
    return matches[0] if len(matches) == 1 else (None, None)


def _matches_card(card: dict[str, Any], lookup: RawCardPriceLookup) -> bool:
    """Compare the provider card's normalized identity to the local lookup."""

    return (
        _normalized_text(card.get("game")) == "pokemon"
        and card_name_matches(card.get("name"), lookup.name)
        and set_name_matches(card.get("set_name"), lookup.set_name)
        and card_number_matches(card.get("number"), lookup.card_number, lookup.set_total)
    )


def _matches_condition(
    variant: dict[str, Any], condition: RawCardCondition
) -> bool:
    """Map local condition codes to accepted JustTCG condition labels."""

    provider_condition = _normalized_text(variant.get("condition"))
    expected_conditions = {
        RawCardCondition.NM: {"nm", "near mint"},
        RawCardCondition.LP: {"lp", "lightly played"},
        RawCardCondition.MP: {"mp", "moderately played"},
        RawCardCondition.DMG: {"d", "dmg", "damaged"},
    }
    return provider_condition in expected_conditions[condition]


def _matches_price_category(variant: dict[str, Any], lookup: RawCardPriceLookup) -> bool:
    if lookup.grading_company:
        grading = variant.get("grading") or {}
        return (
            variant.get("type") == "graded"
            and _normalized_text(grading.get("company")) == lookup.grading_company.casefold()
            and _decimal(grading.get("grade")) == _decimal(lookup.grade)
            and not grading.get("grade_label") and not grading.get("qualifier")
        )
    return lookup.condition is not None and variant.get("type") != "graded" and _matches_condition(variant, lookup.condition)


def _normalize_graded_payload(payload: Any) -> Any:
    """Adapt v2 USD graded markets to the common quote/history parser."""
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise JustTCGError("JustTCG returned an invalid graded response.")
    for card in payload["data"]:
        if not isinstance(card, dict):
            continue
        if isinstance(card.get("game"), dict):
            card["game"] = card["game"].get("id")
        if isinstance(card.get("set"), dict):
            card["set_name"] = card["set"].get("name")
        for variant in card.get("variants", []):
            if not isinstance(variant, dict):
                continue
            market = next((m for m in variant.get("markets", []) if m.get("region") == "NA" and m.get("currency") == "USD"), {})
            variant.update(price=market.get("price"), lastUpdated=market.get("updated_at"), priceHistory=market.get("price_history", []))
    return payload


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

    return (_text(value) or "").casefold()


def _decimal(value: Any) -> Decimal | None:
    """Parse an external numeric value without binary floating-point conversion."""

    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value))
        return parsed if parsed.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def _timestamp(value: Any) -> datetime | None:
    """Parse a Unix timestamp as timezone-aware UTC, returning None if invalid."""

    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None
