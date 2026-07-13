from decimal import Decimal

from app.schemas.domain import DomainSchema


class AssetCalculationSummary(DomainSchema):
    total_quantity: int
    total_cost: Decimal
    average_cost_per_unit: Decimal | None
    market_price_per_unit: Decimal | None
    total_market_value: Decimal | None
    profit_loss: Decimal | None
    roi_percent: Decimal | None
