from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from app.schemas.domain import CurrencyCode, DomainSchema, PurchaseLotBase
from app.services.currency import normalize_currency


class PurchaseLotCreateRequest(PurchaseLotBase):
    pass


class PurchaseLotUpdateRequest(DomainSchema):
    purchase_date: date | None = None
    quantity: int | None = Field(default=None, gt=0)
    purchase_price_per_unit: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_currency(value)
        return value

    @model_validator(mode="after")
    def validate_update_fields(self) -> "PurchaseLotUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        if "currency" in self.model_fields_set and self.currency is None:
            raise ValueError("currency cannot be null.")
        return self


class PurchaseLotResponse(DomainSchema):
    id: int
    asset_id: int
    purchase_date: date
    quantity: int
    purchase_price_per_unit: Decimal
    currency: CurrencyCode
    created_at: datetime
    updated_at: datetime
