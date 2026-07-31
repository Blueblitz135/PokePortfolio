from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import ConfigDict, Field, field_validator

from app.models.enums import PriceSource
from app.schemas.domain import CurrencyCode, DomainSchema
from app.services.currency import DEFAULT_CURRENCY, normalize_currency


class PriceSnapshotCreateRequest(DomainSchema):
    model_config = ConfigDict(extra="forbid")

    market_price_per_unit: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode = DEFAULT_CURRENCY
    source: Literal["manual"] = "manual"
    confidence: Decimal = Field(
        default=Decimal("0.5"), ge=0, le=1, max_digits=4, decimal_places=3
    )

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_currency(value)
        return value


class PriceSnapshotResponse(DomainSchema):
    id: int
    asset_id: int
    market_price_per_unit: Decimal
    currency: CurrencyCode
    source: PriceSource
    confidence: Decimal | None
    observed_at: datetime
