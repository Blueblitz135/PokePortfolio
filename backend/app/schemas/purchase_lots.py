"""Validate purchase-lot creation, partial updates, and API responses."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import Field, field_validator, model_validator

from app.schemas.domain import CurrencyCode, DomainSchema, PurchaseLotBase
from app.services.currency import normalize_currency


class PurchaseLotCreateRequest(PurchaseLotBase):
    """Acquisition fields accepted beneath an asset route."""

    pass


class PurchaseLotUpdateRequest(DomainSchema):
    """Optional purchase fields for a non-empty PATCH operation."""

    purchase_date: date | None = None
    quantity: int | None = Field(default=None, gt=0)
    purchase_price_per_unit: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        """Canonicalize string currency codes before Literal validation."""

        if isinstance(value, str):
            return normalize_currency(value)
        return value

    @model_validator(mode="after")
    def validate_update_fields(self) -> "PurchaseLotUpdateRequest":
        """Reject an empty update document."""

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        if "currency" in self.model_fields_set and self.currency is None:
            raise ValueError("currency cannot be null.")
        return self


class PurchaseLotResponse(DomainSchema):
    """Persisted acquisition lot returned to API clients."""

    id: int
    asset_id: int
    purchase_date: date
    quantity: int
    purchase_price_per_unit: Decimal
    currency: CurrencyCode
    created_at: datetime
    updated_at: datetime
