from datetime import date, datetime, timezone
from decimal import Decimal

from app.models import Asset, AssetType, PriceSnapshot, PurchaseLot
from app.services.calculations import calculate_asset_summary


def test_calculation_summary_without_purchase_lots_or_price() -> None:
    asset = Asset(asset_type=AssetType.SEALED_PRODUCT, display_name="Booster Box")

    summary = calculate_asset_summary(asset)

    assert summary.total_quantity == 0
    assert summary.total_cost == Decimal("0")
    assert summary.average_cost_per_unit is None
    assert summary.market_price_per_unit is None
    assert summary.total_market_value is None
    assert summary.profit_loss is None
    assert summary.roi_percent is None


def test_calculation_summary_with_multiple_purchase_lots() -> None:
    asset = Asset(
        asset_type=AssetType.SEALED_PRODUCT,
        display_name="Booster Box",
        purchase_lots=[
            PurchaseLot(
                purchase_date=date(2025, 8, 1),
                quantity=1,
                purchase_price_per_unit=Decimal("750.00"),
            ),
            PurchaseLot(
                purchase_date=date(2026, 2, 15),
                quantity=2,
                purchase_price_per_unit=Decimal("900.00"),
            ),
        ],
    )

    summary = calculate_asset_summary(asset)

    assert summary.total_quantity == 3
    assert summary.total_cost == Decimal("2550.00")
    assert summary.average_cost_per_unit == Decimal("850.00")
    assert summary.market_price_per_unit is None
    assert summary.total_market_value is None
    assert summary.profit_loss is None
    assert summary.roi_percent is None


def test_calculation_summary_uses_latest_price_snapshot() -> None:
    asset = Asset(
        asset_type=AssetType.SEALED_PRODUCT,
        display_name="Booster Box",
        purchase_lots=[
            PurchaseLot(
                purchase_date=date(2025, 8, 1),
                quantity=2,
                purchase_price_per_unit=Decimal("750.00"),
            )
        ],
        price_snapshots=[
            PriceSnapshot(
                id=1,
                market_price_per_unit=Decimal("900.00"),
                observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ),
            PriceSnapshot(
                id=2,
                market_price_per_unit=Decimal("1000.00"),
                observed_at=datetime(2026, 2, 1, tzinfo=timezone.utc),
            ),
        ],
    )

    summary = calculate_asset_summary(asset)

    assert summary.market_price_per_unit == Decimal("1000.00")
    assert summary.total_market_value == Decimal("2000.00")
    assert summary.profit_loss == Decimal("500.00")
    assert summary.roi_percent == Decimal("33.33333333333333333333333333")
