import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from app.adapters.poketrace import (
    PokeTraceAdapter,
    PokeTraceAssetLookup,
    PokeTraceConfigurationError,
)


LOOKUP = PokeTraceAssetLookup(
    name="Umbreon VMAX",
    set_name="Evolving Skies",
    card_number="215",
    set_total="203",
    product_type="single",
    product_family="card",
    tier="NEAR_MINT",
)


def _fetch(adapter: PokeTraceAdapter):
    return asyncio.run(adapter.fetch_market_data(LOOKUP))


def test_adapter_returns_exact_tier_quotes_normalized_to_cad() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/cards"
        assert request.headers["X-API-Key"] == "test-key"
        assert request.url.params["card_number"] == "215/203"
        assert request.url.params["product_type"] == "single"
        return httpx.Response(
            200,
            json={
                "data": [
                    {
                        "id": "wrong-card",
                        "name": "Umbreon VMAX",
                        "cardNumber": "214/203",
                        "set": {"name": "Evolving Skies"},
                        "productType": "single",
                    },
                    {
                        "id": "poketrace-card-id",
                        "name": "Umbreon VMAX",
                        "cardNumber": "215/203",
                        "set": {"name": "Evolving Skies"},
                        "productType": "single",
                        "currency": "USD",
                        "lastUpdated": "2026-01-29T12:00:00Z",
                        "prices": {
                            "tcgplayer": {
                                "NEAR_MINT": {
                                    "avg": 100,
                                    "low": 90,
                                    "high": 110,
                                    "saleCount": 12,
                                    "trend": "up",
                                    "confidence": "high",
                                },
                                "LIGHTLY_PLAYED": {"avg": 80},
                            }
                        },
                    },
                ]
            },
        )

    adapter = PokeTraceAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )

    result = _fetch(adapter)

    assert result is not None
    assert result.provider_card_id == "poketrace-card-id"
    assert result.observed_at == datetime(
        2026, 1, 29, 12, 0, tzinfo=timezone.utc
    )
    assert len(result.quotes) == 1
    quote = result.quotes[0]
    assert quote.source == "tcgplayer"
    assert quote.tier == "NEAR_MINT"
    assert quote.average_price_cad == Decimal("135.00")
    assert quote.low_price_cad == Decimal("121.50")
    assert quote.high_price_cad == Decimal("148.50")


def test_adapter_treats_placeholder_key_as_unconfigured() -> None:
    adapter = PokeTraceAdapter(
        api_key="replace_with_poketrace_api_key",
        usd_to_cad_rate=Decimal("1.35"),
    )

    assert adapter.is_configured is False
    with pytest.raises(PokeTraceConfigurationError):
        _fetch(adapter)
