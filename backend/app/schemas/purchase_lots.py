from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from app.schemas.domain import DomainSchema, PurchaseLotBase


class PurchaseLotCreateRequest(PurchaseLotBase):
    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class PurchaseLotUpdateRequest(DomainSchema):
    purchase_date: date | None = None
    quantity: int | None = Field(default=None, gt=0)
    purchase_price_per_unit: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    currency: str | None = Field(default=None, min_length=3, max_length=3)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.upper()

    @model_validator(mode="after")
    def validate_update_fields(self) -> "PurchaseLotUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        return self


class PurchaseLotResponse(DomainSchema):
    id: int
    asset_id: int
    purchase_date: date
    quantity: int
    purchase_price_per_unit: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime
