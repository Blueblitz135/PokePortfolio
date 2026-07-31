from decimal import Decimal

from app.models import Asset, PriceSnapshot
from app.schemas.calculations import AssetCalculationSummary


def get_latest_price_snapshot(asset: Asset) -> PriceSnapshot | None:
    if not asset.price_snapshots:
        return None

    return max(
        asset.price_snapshots,
        key=lambda snapshot: (snapshot.observed_at, snapshot.id),
    )


def calculate_asset_summary(asset: Asset) -> AssetCalculationSummary:
    total_quantity = sum(lot.quantity for lot in asset.purchase_lots)
    total_cost = sum(
        lot.purchase_price_per_unit * lot.quantity for lot in asset.purchase_lots
    )
    average_cost_per_unit = (
        total_cost / total_quantity if total_quantity > 0 else None
    )

    latest_snapshot = get_latest_price_snapshot(asset)
    market_price_per_unit = (
        latest_snapshot.market_price_per_unit if latest_snapshot is not None else None
    )
    total_market_value = (
        market_price_per_unit * total_quantity
        if market_price_per_unit is not None
        else None
    )
    profit_loss = (
        total_market_value - total_cost if total_market_value is not None else None
    )
    roi_percent = (
        profit_loss / total_cost * Decimal("100")
        if profit_loss is not None and total_cost > 0
        else None
    )

    return AssetCalculationSummary(
        total_quantity=total_quantity,
        total_cost=total_cost,
        average_cost_per_unit=average_cost_per_unit,
        market_price_per_unit=market_price_per_unit,
        total_market_value=total_market_value,
        profit_loss=profit_loss,
        roi_percent=roi_percent,
    )
