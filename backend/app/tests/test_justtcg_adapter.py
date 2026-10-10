import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import httpx
import pytest

from app.adapters.justtcg import (
    JustTCGAdapter,
    JustTCGConfigurationError,
    JustTCGError,
    JustTCGQuotaError,
    JustTCGRateLimitError,
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


@pytest.mark.parametrize(
    ("code", "error_type"),
    [
        ("RATE_LIMIT_EXCEEDED", JustTCGRateLimitError),
        ("DAILY_LIMIT_EXCEEDED", JustTCGQuotaError),
        ("REQUEST_LIMIT_EXCEEDED", JustTCGQuotaError),
    ],
)
def test_adapter_classifies_provider_limits(code, error_type) -> None:
    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                429, json={"error": "limit reached", "code": code}
            )
        ),
    )

    with pytest.raises(error_type):
        _fetch(adapter)


def test_adapter_uses_stable_tcgplayer_id_instead_of_catalog_names() -> None:
    def handle_request(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v2/cards"
        assert request.url.params["tcgplayer_id"] == "502558"
        return httpx.Response(200, json={"data": [{
            "id": "card-uuid",
            "name": "Charizard ex - 006/165",
            "game": {"id": "pokemon"},
            "set": {"name": "SV: Scarlet & Violet 151"},
            "number": "006/165",
            "external_ids": {"tcgplayer": "502558"},
            "variants": [{
                "id": "psa-10", "type": "graded", "printing": "Holofoil",
                "grading": {"company": "PSA", "grade": 10},
                "markets": [{
                    "region": "NA", "currency": "USD", "price": 100,
                    "updated_at": 1_700_000_000, "price_history": [],
                }],
            }],
        }]})

    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )
    lookup = RawCardPriceLookup(
        name="Charizard ex", set_name="151", card_number="006",
        set_total="165", condition=None, printing="Holofoil",
        grading_company="PSA", grade="10", tcgplayer_id="502558",
    )

    result = asyncio.run(adapter.fetch_raw_card_price_history(lookup))

    assert result is not None
    assert result.current_price_cad == Decimal("135.00")


def test_price_history_is_cached_for_repeated_refreshes() -> None:
    requests = 0

    def handle_request(request: httpx.Request) -> httpx.Response:
        nonlocal requests
        requests += 1
        return httpx.Response(200, json={"data": []})

    adapter = JustTCGAdapter(
        api_key="test-key",
        usd_to_cad_rate=Decimal("1.35"),
        transport=httpx.MockTransport(handle_request),
    )

    assert asyncio.run(adapter.fetch_raw_card_price_history(LOOKUP)) is None
    assert asyncio.run(adapter.fetch_raw_card_price_history(LOOKUP)) is None
    assert requests == 1


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
