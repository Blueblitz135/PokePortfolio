from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

import httpx

from app.models.enums import RawCardCondition


USD_TO_CAD_QUANTUM = Decimal("0.01")
JUSTTCG_CONFIDENCE = Decimal("0.700")


class JustTCGError(Exception):
    """Raised when JustTCG cannot provide a valid raw-card price."""


class JustTCGConfigurationError(JustTCGError):
    """Raised when the optional JustTCG integration is not configured."""


@dataclass(frozen=True)
class RawCardPriceLookup:
    name: str
    set_name: str
    card_number: str
    condition: RawCardCondition


@dataclass(frozen=True)
class ExternalPriceQuote:
    market_price_per_unit: Decimal
    currency: str
    confidence: Decimal
    observed_at: datetime
    metadata: dict[str, str]


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
        self.api_key = api_key.strip() if api_key else None
        self.usd_to_cad_rate = usd_to_cad_rate
        self.base_url = f"{base_url.rstrip('/')}/"
        self.timeout_seconds = timeout_seconds
        self.transport = transport

    async def fetch_raw_card_price(
        self, lookup: RawCardPriceLookup
    ) -> ExternalPriceQuote | None:
        self._validate_configuration()

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout_seconds,
            transport=self.transport,
        ) as client:
            payload = await self._request_json(
                client,
                "cards",
                params={
                    "query": lookup.name,
                    "game": "Pokemon",
                    "number": lookup.card_number,
                    "condition": lookup.condition.value,
                    "limit": 20,
                },
            )

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

    def _validate_configuration(self) -> None:
        if not self.api_key:
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
        try:
            response = await client.get(
                path, params=params, headers={"x-api-key": self.api_key or ""}
            )
            response.raise_for_status()
            return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise JustTCGError("JustTCG request failed.") from exc


def _find_exact_variant(
    payload: Any, lookup: RawCardPriceLookup
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
        raise JustTCGError("JustTCG returned an invalid card response.")

    for card in payload["data"]:
        if not isinstance(card, dict) or not _matches_card(card, lookup):
            continue
        variants = card.get("variants")
        if not isinstance(variants, list):
            continue
        for variant in variants:
            if isinstance(variant, dict) and _matches_condition(
                variant, lookup.condition
            ):
                return card, variant
    return None, None


def _matches_card(card: dict[str, Any], lookup: RawCardPriceLookup) -> bool:
    return (
        _normalized_text(card.get("game")) == "pokemon"
        and _normalized_text(card.get("name")) == _normalized_text(lookup.name)
        and _normalized_text(card.get("set_name")) == _normalized_text(lookup.set_name)
        and _normalized_text(card.get("number"))
        == _normalized_text(lookup.card_number)
    )


def _matches_condition(
    variant: dict[str, Any], condition: RawCardCondition
) -> bool:
    provider_condition = _normalized_text(variant.get("condition"))
    expected_conditions = {
        RawCardCondition.NM: {"nm", "near mint"},
        RawCardCondition.LP: {"lp", "lightly played"},
        RawCardCondition.MP: {"mp", "moderately played"},
        RawCardCondition.DMG: {"dmg", "damaged"},
    }
    return provider_condition in expected_conditions[condition]


def _text(value: Any) -> str | None:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(value, (str, int)):
        return None
    text = str(value).strip()
    return text or None


def _normalized_text(value: Any) -> str:
    return (_text(value) or "").casefold()


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _timestamp(value: Any) -> datetime | None:
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except (TypeError, ValueError, OSError, OverflowError):
        return None
