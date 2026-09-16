"""Regression coverage based on the live Umbreon 215/203 provider formats."""

import asyncio
from dataclasses import replace
from decimal import Decimal

import httpx
import pytest

from app.adapters.justtcg import JustTCGAdapter, RawCardPriceLookup, _find_exact_variant
from app.adapters.poketrace import PokeTraceAdapter, PokeTraceAssetLookup, _find_exact_card
from app.models import RawCardCondition


JUST_LOOKUP = RawCardPriceLookup(
    name="Umbreon VMAX", set_name="Evolving Skies", card_number="215",
    set_total="203", condition=RawCardCondition.NM,
)
POKE_LOOKUP = PokeTraceAssetLookup(
    name="Umbreon VMAX", set_name="Evolving Skies", card_number="215",
    set_total="203", product_type="single", product_family="card", tier="NEAR_MINT",
)


def just_card():
    return {
        "id": "umbreon", "name": "Umbreon VMAX (Alternate Art Secret)",
        "game": "Pokemon", "set_name": "SWSH07: Evolving Skies", "number": "215/203",
        "variants": [{
            "id": "umbreon-nm-holo", "condition": "Near Mint", "printing": "Holofoil",
            "price": 120, "lastUpdated": 1_700_086_400,
            "priceHistory": [{"p": 100, "t": 1_700_000_000}, {"p": 110, "t": 1_700_086_400}],
        }],
    }


def poke_card():
    return {
        "id": "umbreon", "name": "Umbreon VMAX (Alternate Art Secret)",
        "set": {"name": "SWSH07: Evolving Skies"}, "cardNumber": "215/203",
        "productType": "single", "variant": "Holofoil", "currency": "USD",
    }


def test_real_catalog_format_returns_current_price_and_history():
    def handler(request):
        assert request.url.params["q"] == "Umbreon VMAX"
        assert "query" not in request.url.params
        return httpx.Response(200, json={"data": [just_card()]})

    adapter = JustTCGAdapter("test", Decimal("1.35"), transport=httpx.MockTransport(handler))
    result = asyncio.run(adapter.fetch_raw_card_price_history(JUST_LOOKUP))
    assert result.current_price_cad == Decimal("162.00")
    assert result.points[-1].market_price_per_unit == Decimal("148.50")
    assert result.growth_percent == Decimal("10")


@pytest.mark.parametrize("field,value", [
    ("number", "214/203"), ("number", "215/204"),
    ("set_name", "Brilliant Stars"), ("name", "Umbreon V"),
    ("name", "Umbreon VMAX (World Championship)"), ("game", "Magic"),
])
def test_justtcg_rejects_different_card(field, value):
    card = just_card()
    card[field] = value
    assert _find_exact_variant({"data": [card]}, JUST_LOOKUP) == (None, None)


def test_ambiguous_printings_require_explicit_printing():
    card = just_card()
    card["variants"].append({**card["variants"][0], "id": "reverse", "printing": "Reverse Holofoil"})
    assert _find_exact_variant({"data": [card]}, JUST_LOOKUP) == (None, None)
    _, variant = _find_exact_variant({"data": [card]}, replace(JUST_LOOKUP, printing="Holofoil"))
    assert variant["id"] == "umbreon-nm-holo"


def test_poketrace_fetches_price_details_after_matching_search():
    calls = []

    def handler(request):
        calls.append(request.url.path)
        card = poke_card()
        if request.url.path == "/v1/cards":
            assert request.url.params["card_number"] == "215/203"
            return httpx.Response(200, json={"data": [card]})
        card["prices"] = {"tcgplayer": {"NEAR_MINT": {"avg": 120}, "PSA_10": {"avg": 500}}}
        return httpx.Response(200, json={"data": card})

    adapter = PokeTraceAdapter("test", Decimal("1.35"), transport=httpx.MockTransport(handler))
    result = asyncio.run(adapter.fetch_market_data(POKE_LOOKUP))
    assert calls == ["/v1/cards", "/v1/cards/umbreon"]
    assert len(result.quotes) == 1
    assert result.quotes[0].average_price_cad == Decimal("162.00")


@pytest.mark.parametrize("field,value", [
    ("cardNumber", "214/203"), ("cardNumber", "215/204"),
    ("set", {"name": "Brilliant Stars"}), ("productType", "sealed"),
])
def test_poketrace_rejects_different_identity(field, value):
    card = poke_card()
    card[field] = value
    assert _find_exact_card({"data": [card]}, POKE_LOOKUP) is None


def test_poketrace_rejects_ambiguous_printings():
    card = poke_card()
    other = {**card, "id": "reverse", "variant": "Reverse_Holofoil"}
    assert _find_exact_card({"data": [card, other]}, POKE_LOOKUP) is None


def test_current_quote_survives_missing_history():
    card = just_card()
    del card["variants"][0]["priceHistory"]
    adapter = JustTCGAdapter("test", Decimal("1.35"), transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"data": [card]})
    ))
    result = asyncio.run(adapter.fetch_raw_card_price_history(JUST_LOOKUP))
    assert result.current_price_cad == Decimal("162.00")
    assert result.points == ()
    assert result.growth_percent is None
