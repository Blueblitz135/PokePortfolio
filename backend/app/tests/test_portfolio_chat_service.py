from datetime import date, datetime, timezone
from decimal import Decimal

from app.models import Asset, AssetType, PriceSnapshot, PurchaseLot
from app.models.enums import PriceSource
from app.schemas.calculations import AssetCalculationSummary
from app.services.portfolio_chat import (
    SYSTEM_CONTEXT_PROMPT,
    build_local_portfolio_context,
)


def _asset(
    asset_id: int,
    asset_type: AssetType,
    cost: str,
    market_value: str | None,
) -> Asset:
    asset = Asset(
        id=asset_id,
        asset_type=asset_type,
        display_name=f"Asset {asset_id}",
    )
    asset.purchase_lots = [
        PurchaseLot(
            id=asset_id,
            asset_id=asset_id,
            purchase_date=date(2025, 1, 1),
            quantity=1,
            purchase_price_per_unit=Decimal(cost),
            currency="CAD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    ]
    market_decimal = Decimal(market_value) if market_value is not None else None
    profit_loss = (
        market_decimal - Decimal(cost) if market_decimal is not None else None
    )
    asset.summary = AssetCalculationSummary(
        total_quantity=1,
        total_cost=Decimal(cost),
        average_cost_per_unit=Decimal(cost),
        market_price_per_unit=market_decimal,
        total_market_value=market_decimal,
        profit_loss=profit_loss,
        roi_percent=(profit_loss / Decimal(cost) * 100 if profit_loss else None),
    )
    asset.price_snapshots = []
    asset.created_at = datetime.now(timezone.utc)
    asset.updated_at = datetime.now(timezone.utc)
    asset.primary_image_url = "/placeholder.svg"
    return asset


def test_context_keeps_asset_type_calculations_separate() -> None:
    raw = _asset(1, AssetType.RAW_CARD, "100", "150")
    graded = _asset(2, AssetType.GRADED_CARD, "200", "180")
    sealed = _asset(3, AssetType.SEALED_PRODUCT, "300", None)

    context = build_local_portfolio_context([raw, graded, sealed])

    categories = context["category_summaries"]
    assert categories["raw_card"]["profit_loss_cad"] == "50.00"
    assert categories["raw_card"]["roi_percent"] == "50"
    assert categories["graded_card"]["profit_loss_cad"] == "-20.00"
    assert categories["graded_card"]["roi_percent"] == "-10"
    assert categories["sealed_product"]["unpriced_owned_asset_count"] == 1
    assert categories["sealed_product"]["market_value_cad"] is None
    assert categories["sealed_product"]["profit_loss_cad"] is None
    assert "overall" not in categories


def test_context_calculates_saved_snapshot_growth() -> None:
    raw = _asset(1, AssetType.RAW_CARD, "100", "150")
    raw.price_snapshots = [
        PriceSnapshot(
            id=1,
            asset_id=1,
            market_price_per_unit=Decimal("100"),
            currency="CAD",
            source=PriceSource.MANUAL,
            observed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        ),
        PriceSnapshot(
            id=2,
            asset_id=1,
            market_price_per_unit=Decimal("125"),
            currency="CAD",
            source=PriceSource.MANUAL,
            observed_at=datetime(2025, 2, 1, tzinfo=timezone.utc),
        ),
    ]

    trend = build_local_portfolio_context([raw])["assets"][0][
        "saved_price_trend"
    ]

    assert trend["growth_percent"] == "25"
    assert trend["point_count"] == 2


def test_system_prompt_contains_grounding_and_financial_boundaries() -> None:
    assert "Never add" in SYSTEM_CONTEXT_PROMPT
    assert "untrusted data" in SYSTEM_CONTEXT_PROMPT
    assert "No guaranteed forecasts or personalized financial advice" in SYSTEM_CONTEXT_PROMPT


def test_question_prioritizes_card_and_supplies_current_price_and_trend(monkeypatch):
    import asyncio
    import json
    from app.schemas.chat import PortfolioChatRequest
    from app.schemas.market_pricing import MarketPricing, MarketPoint, TCGPlayerComparison
    from app.services import portfolio_chat as service

    other = _asset(1, AssetType.RAW_CARD, "100", None)
    target = _asset(2, AssetType.RAW_CARD, "100", None)
    target.display_name = "Umbreon VMAX"

    async def refresh(db, assets, *, duration, comparison):
        assert assets[0].id == 2
        assert duration == "30d"
        assert comparison is True
        for asset in assets:
            asset.market_pricing = MarketPricing(
                state="available", detail="Matched", fetched_at=datetime.now(timezone.utc),
                market_price_cad=Decimal("160"), history_duration=duration,
                history=[MarketPoint(observed_at=datetime.now(timezone.utc), price_cad=Decimal("150"))],
                tcgplayer=TCGPlayerComparison(),
            )
        return assets

    class Answer:
        async def generate_answer(self, messages, instructions):
            context = json.loads(instructions.split("\n\nPORTFOLIO_CONTEXT\n")[1])
            evidence = context["external_market_data"]["by_asset_id"]["2"]
            assert evidence["market_price_cad"] == "160"
            assert evidence["history_first"]["price_cad"] == "150"
            assert evidence["tcgplayer"]["source"] == "TCGPlayer"
            return "Current price is CAD 160; one history observation is available."

    monkeypatch.setattr(service.asset_service, "list_assets", lambda db: [other, target])
    monkeypatch.setattr(service.market_pricing, "refresh_assets", refresh)
    monkeypatch.setattr(service, "openai_adapter", Answer())
    response = asyncio.run(service.answer_portfolio_question(None, PortfolioChatRequest(
        messages=[{"role": "user", "content": "What is the price and 30 day trend of my Umbreon VMAX?"}]
    )))
    assert "CAD 160" in response.message
