"""Response schema for quantity, cost basis, value, and return calculations."""

from decimal import Decimal

from app.schemas.domain import CurrencyCode, DomainSchema
from app.services.currency import DEFAULT_CURRENCY


class AssetCalculationSummary(DomainSchema):
    """Derived performance fields for one asset in normalized currency."""

    currency: CurrencyCode = DEFAULT_CURRENCY
    total_quantity: int
    total_cost: Decimal
    average_cost_per_unit: Decimal | None
    market_price_per_unit: Decimal | None
    total_market_value: Decimal | None
    profit_loss: Decimal | None
    roi_percent: Decimal | None
