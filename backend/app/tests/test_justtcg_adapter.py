import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from app.adapters.justtcg import (
    JustTCGAdapter,
    JustTCGConfigurationError,
    JustTCGError,
    RawCardPriceLookup,
)
from app.models import RawCardCondition


LOOKUP = RawCardPriceLookup(
    name="Umbreon VMAX",
    set_name="Evolving Skies",
    card_number="215",
    condition=RawCardCondition.NM,
)


def _fetch(adapter: JustTCGAdapter):
    return asyncio.run(adapter.fetch_raw_card_price(LOOKUP))


def test_adapter_normalizes_exact_raw_card_price_to_cad() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/cards"
        assert request.headers["x-api-key"] == "test-key"
        assert dict(request.url.params) == {
            "q": "Umbreon VMAX",
            "game": "pokemon",
            "number": "215",
            "condition": "NM",
            "limit": "20",
        }
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "pokemon-evolving-skies-umbreon-vmax-secret-rare",
                        "uuid": "card-uuid",
                        "name": "Umbreon VMAX",
                        "game": "Pokemon",
                        "set_name": "Evolving Skies",
                        "number": "215",
                        "variants": [
                            {
                                "id": "umbreon-nm",
                                "uuid": "variant-uuid",
                                "condition": "Near Mint",
                                "price": 100,
                                "lastUpdated": 1_700_000_000,
                            }
                        ],
                    }
                ]
            },
        )

    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )

    quote = _fetch(adapter)

    assert quote is not None
    assert quote.market_price_per_unit == Decimal("135.00")
    assert quote.currency == "CAD"
    assert quote.confidence == Decimal("0.700")
    assert quote.observed_at == datetime(2023, 11, 14, 22, 13, 20, tzinfo=timezone.utc)
    assert quote.metadata == {
        "provider": "justtcg",
        "provider_card_id": "pokemon-evolving-skies-umbreon-vmax-secret-rare",
        "provider_card_uuid": "card-uuid",
        "provider_variant_id": "umbreon-nm",
        "provider_variant_uuid": "variant-uuid",
        "provider_condition": "Near Mint",
        "source_market_price_per_unit": "100",
        "source_currency": "USD",
        "usd_to_cad_rate": "1.35",
    }


def test_adapter_returns_no_quote_when_the_match_is_not_exact() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "wrong-set",
                        "name": "Umbreon VMAX",
                        "game": "Pokemon",
                        "set_name": "Brilliant Stars",
                        "number": "215",
                        "variants": [],
                    }
                ]
            },
        )

    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )

    assert _fetch(adapter) is None


def test_adapter_raises_a_safe_error_for_upstream_failure() -> None:
    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, json={"error": "unavailable"})
        ),
    )

    with pytest.raises(JustTCGError, match="request failed"):
        _fetch(adapter)


def test_adapter_requires_an_api_key_and_conversion_rate() -> None:
    adapter = JustTCGAdapter(api_key=None, usd_to_cad_rate=None)

    with pytest.raises(JustTCGConfigurationError):
        _fetch(adapter)


def test_adapter_returns_price_history_in_cad() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.params["priceHistoryDuration"] == "90d"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "umbreon",
                        "name": "Umbreon VMAX",
                        "game": "Pokemon",
                        "set_name": "Evolving Skies",
                        "number": "215",
                        "variants": [
                            {
                                "id": "umbreon-nm",
                                "condition": "Near Mint",
                                "priceHistory": [
                                    {"p": 100, "t": 1_700_000_000},
                                    {"p": 110, "t": 1_700_086_400},
                                ],
                            }
                        ],
                    }
                ]
            },
        )

    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )

    history = asyncio.run(adapter.fetch_raw_card_price_history(LOOKUP, "90d"))

    assert history is not None
    assert history.currency == "CAD"
    assert history.points[0].market_price_per_unit == Decimal("135.00")
    assert history.points[1].market_price_per_unit == Decimal("148.50")
    assert history.growth_percent == Decimal("10.0")
