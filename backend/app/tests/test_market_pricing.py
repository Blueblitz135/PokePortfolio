import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal

import httpx
import pytest
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.adapters.justtcg import JustTCGAdapter, JustTCGError, RawCardPriceHistory, RawCardPriceLookup
from app.adapters.tcgdex import TCGdexAdapter
from app.db.base import Base
from app.models import Asset, AssetType, CardMetadata, RawCardDetails, RawCardCondition, PurchaseLot, PriceSnapshot
from app.schemas.market_pricing import TCGPlayerComparison
from app.services import market_pricing as service


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


def add_card(db, name="Umbreon VMAX", cost="100", quantity=2):
    asset = Asset(asset_type=AssetType.RAW_CARD, display_name=name)
    asset.card_metadata = CardMetadata(name=name, set_name="Evolving Skies", card_number="215", set_total="203", external_source="tcgdex", external_id="swsh7-215")
    asset.raw_card_details = RawCardDetails(condition=RawCardCondition.NM)
    asset.purchase_lots = [PurchaseLot(purchase_date=date(2025, 1, 1), quantity=quantity, purchase_price_per_unit=Decimal(cost), currency="CAD")]
    db.add(asset)
    db.commit()
    return service.asset_service.get_asset(db, asset.id)


class Pricing:
    is_configured = True

    async def fetch_raw_card_price_history(self, lookup, duration):
        if lookup.name == "Unavailable":
            raise JustTCGError("unavailable")
        return RawCardPriceHistory(
            currency="CAD", duration=duration, points=(), growth_percent=None,
            current_price_cad=Decimal("150"),
            current_observed_at=datetime(2026, 9, 15, tzinfo=timezone.utc), printing="Holofoil",
        )


def test_all_cards_refresh_and_persist_correct_lot_performance(db, monkeypatch):
    assets = [add_card(db, f"Card {i}") for i in range(21)]
    assets.append(add_card(db, "Unavailable"))
    assets[0].purchase_lots.append(PurchaseLot(purchase_date=date(2025, 2, 1), quantity=1, purchase_price_per_unit=Decimal("50"), currency="CAD"))
    db.commit()
    monkeypatch.setattr(service, "justtcg_adapter", Pricing())
    refreshed = asyncio.run(service.refresh_assets(db, assets))
    first = refreshed[0]
    assert first.summary.total_quantity == 3
    assert first.summary.total_cost == Decimal("250")
    assert first.summary.total_market_value == Decimal("450")
    assert first.summary.profit_loss == Decimal("200")
    assert first.summary.roi_percent == Decimal("80")
    assert refreshed[20].market_pricing.state == "available"
    assert refreshed[21].market_pricing.state == "unavailable"
    assert refreshed[21].summary.market_price_per_unit is None
    asyncio.run(service.refresh_assets(db, refreshed))
    assert db.scalar(select(func.count()).select_from(PriceSnapshot)) == 21


def test_zero_cost_roi_and_source_failure_preserve_saved_values(db, monkeypatch):
    asset = add_card(db, cost="0")
    monkeypatch.setattr(service, "justtcg_adapter", Pricing())
    result = asyncio.run(service.refresh_assets(db, [asset]))[0]
    assert result.summary.roi_percent is None
    result.card_metadata.name = "Unavailable"
    result = asyncio.run(service.refresh_assets(db, [result]))[0]
    assert result.market_pricing.state == "unavailable"
    assert result.summary.market_price_per_unit == Decimal("150")


def test_tcgplayer_fields_convert_usd_and_ignore_cardmarket(db):
    card = add_card(db).card_metadata
    def handler(request):
        return httpx.Response(200, json={
            "id": "swsh7-215", "name": "Umbreon VMAX", "localId": "215", "set": {"name": "Evolving Skies"},
            "pricing": {"cardmarket": {"low": 1}, "tcgplayer": {
                "unit": "USD", "updated": "2026-09-15T12:00:00Z",
                "holofoil": {"marketPrice": 100, "lowPrice": 90, "midPrice": 110, "highPrice": 200},
                "reverse-holofoil": {"marketPrice": None, "lowPrice": 10},
            }},
        })
    adapter = TCGdexAdapter("https://example.test/", transport=httpx.MockTransport(handler))
    result = asyncio.run(adapter.fetch_tcgplayer_prices(card, Decimal("1.35")))
    assert result.source == "TCGPlayer"
    assert result.variants[0].market_price_cad == Decimal("135")
    assert result.variants[0].median_price_cad == Decimal("148.50")
    assert result.variants[0].low_price_cad == Decimal("121.50")
    assert result.variants[0].high_price_cad == Decimal("270")
    assert result.variants[1].market_price_cad is None


def test_both_sources_are_requested_even_when_market_fails(db, monkeypatch):
    asset = add_card(db, "Unavailable")
    called = []
    class Reference:
        async def fetch_tcgplayer_prices(self, metadata, rate):
            called.append(metadata.name)
            return TCGPlayerComparison(state="available")
    monkeypatch.setattr(service, "justtcg_adapter", Pricing())
    monkeypatch.setattr(service, "tcgdex_adapter", Reference())
    monkeypatch.setattr(service.settings, "justtcg_usd_to_cad_rate", Decimal("1.35"))
    result = asyncio.run(service.refresh_assets(db, [asset], comparison=True))[0]
    assert called == ["Unavailable"]
    assert result.market_pricing.tcgplayer.state == "available"
    assert result.summary.market_price_per_unit is None


def test_graded_identity_is_resolved_before_v2_and_exact_grade_selected():
    def handler(request):
        if request.url.path == "/v1/cards":
            return httpx.Response(200, json={"data": [{"id": "umbreon-215", "name": "Umbreon VMAX", "game": "Pokemon", "set_name": "Evolving Skies", "number": "215/203"}]})
        assert request.url.path == "/v2/cards"
        assert request.url.params["card_id"] == "umbreon-215"
        assert request.url.params["graded"] == "only"
        def variant(grade, price):
            return {"id": f"psa-{grade}", "type": "graded", "grading": {"company": "PSA", "grade": grade}, "printing": "Holofoil", "markets": [{"region": "NA", "currency": "USD", "price": price, "updated_at": 1_700_000_000, "price_history": []}]}
        return httpx.Response(200, json={"data": [{
            "id": "umbreon-215", "name": "Umbreon VMAX", "game": {"id": "pokemon"},
            "set": {"name": "SWSH07: Evolving Skies"}, "number": "215/203",
            "variants": [variant(9, 100), variant(10, 300)],
        }]})
    adapter = JustTCGAdapter("test", Decimal("1.35"), transport=httpx.MockTransport(handler))
    lookup = RawCardPriceLookup(name="Umbreon VMAX", set_name="Evolving Skies", card_number="215", set_total="203", condition=None, grading_company="PSA", grade="10")
    result = asyncio.run(adapter.fetch_raw_card_price_history(lookup))
    assert result.current_price_cad == Decimal("405")


def test_refresh_endpoint_returns_ui_metrics_and_source(db, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.db.session import get_db
    add_card(db)
    monkeypatch.setattr(service, "justtcg_adapter", Pricing())
    monkeypatch.setitem(app.dependency_overrides, get_db, lambda: db)
    response = TestClient(app).post("/api/assets/refresh-prices")
    assert response.status_code == 200
    card = response.json()[0]
    assert card["summary"]["market_price_per_unit"] == "150"
    assert card["summary"]["total_market_value"] == "300"
    assert Decimal(card["summary"]["profit_loss"]) == Decimal("100")
    assert Decimal(card["summary"]["roi_percent"]) == Decimal("50")
    assert card["market_pricing"]["source"] == "Marketplace and verified store sales"


@pytest.mark.parametrize("question,expected", [
    ("How is my portfolio doing?", "90d"),
    ("Which card grew most in 7 days?", "7d"),
    ("Compare the last month", "30d"),
    ("Show six months of trends", "180d"),
    ("How did it do over the year?", "1y"),
])
def test_varied_questions_select_labeled_history_windows(question, expected):
    from app.services.portfolio_chat import _requested_duration
    assert _requested_duration(question.casefold()) == expected
