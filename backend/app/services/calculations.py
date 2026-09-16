"""Calculate per-asset holdings and performance using normalized CAD values."""

from decimal import Decimal

from app.models import Asset, PriceSnapshot
from app.schemas.calculations import AssetCalculationSummary
from app.services.currency import DEFAULT_CURRENCY, require_normalized_currency


def get_latest_price_snapshot(asset: Asset) -> PriceSnapshot | None:
    """Select the newest snapshot, using its ID to break timestamp ties."""

    if not asset.price_snapshots:
        return None

    return max(
        asset.price_snapshots,
        key=lambda snapshot: (snapshot.observed_at, snapshot.id),
    )


def _require_normalized_currency(currency: str | None) -> None:
    """Guard calculations against accidentally mixing non-CAD stored values."""

    require_normalized_currency(
        currency if currency is not None else DEFAULT_CURRENCY
    )


def calculate_asset_summary(
    asset: Asset, market_price_override: Decimal | None = None
) -> AssetCalculationSummary:
    """Derive quantity, cost basis, market value, profit/loss, and ROI for one asset."""

    total_quantity = sum(lot.quantity for lot in asset.purchase_lots)
    total_cost = Decimal("0")
    for lot in asset.purchase_lots:
        _require_normalized_currency(lot.currency)
        total_cost += lot.purchase_price_per_unit * lot.quantity

    average_cost_per_unit = (
        total_cost / total_quantity if total_quantity > 0 else None
    )

    latest_snapshot = get_latest_price_snapshot(asset)
    if market_price_override is not None:
        market_price_per_unit = market_price_override
    elif latest_snapshot is None:
        market_price_per_unit = None
    else:
        _require_normalized_currency(latest_snapshot.currency)
        market_price_per_unit = latest_snapshot.market_price_per_unit
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
        currency=DEFAULT_CURRENCY,
        total_quantity=total_quantity,
        total_cost=total_cost,
        average_cost_per_unit=average_cost_per_unit,
        market_price_per_unit=market_price_per_unit,
        total_market_value=total_market_value,
        profit_loss=profit_loss,
        roi_percent=roi_percent,
    )
