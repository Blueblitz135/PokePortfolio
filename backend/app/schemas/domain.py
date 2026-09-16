"""Define reusable Pydantic fields shared by persistence-oriented API schemas."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import (
    AssetType,
    ExternalSource,
    GradingCompany,
    ImageType,
    PriceSource,
    RawCardCondition,
    SealedProductType,
)
from app.services.currency import DEFAULT_CURRENCY, normalize_currency


CurrencyCode = Literal["CAD"]


class DomainSchema(BaseModel):
    """Base schema that can validate from dictionaries or SQLAlchemy attributes."""

    model_config = ConfigDict(from_attributes=True)


class AssetBase(DomainSchema):
    """Fields shared by all portfolio asset types."""

    asset_type: AssetType
    display_name: str = Field(min_length=1, max_length=255)
    user_note: str | None = None


class AssetCreate(AssetBase):
    """Persistence-oriented asset creation schema."""

    pass


class AssetRead(AssetBase):
    """Persisted asset identity and audit timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime


class CardMetadataBase(DomainSchema):
    """Structured card identity independent of raw or graded ownership details."""

    external_source: ExternalSource = ExternalSource.MANUAL
    external_id: str | None = Field(default=None, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    set_name: str = Field(min_length=1, max_length=255)
    set_id: str | None = Field(default=None, max_length=100)
    year: int | None = None
    card_number: str = Field(min_length=1, max_length=50)
    set_total: str | None = Field(default=None, max_length=50)
    rarity: str | None = Field(default=None, max_length=100)
    variant: str | None = Field(default=None, max_length=100)
    image_url: str | None = None


class CardMetadataCreate(CardMetadataBase):
    """Card metadata tied to an existing asset."""

    asset_id: int


class CardMetadataRead(CardMetadataCreate):
    """Persisted card metadata with its row identifier."""

    id: int


class RawCardDetailsBase(DomainSchema):
    """Condition data specific to an ungraded card."""

    condition: RawCardCondition


class RawCardDetailsCreate(RawCardDetailsBase):
    """Raw-card details tied one-to-one to an asset."""

    asset_id: int


class RawCardDetailsRead(RawCardDetailsCreate):
    """Persisted raw-card details."""

    pass


class GradedCardDetailsBase(DomainSchema):
    """Grader, numeric grade, and optional certificate for a slabbed card."""

    grading_company: GradingCompany
    grade: Decimal = Field(gt=0, le=10, max_digits=3, decimal_places=1)
    cert_number: str | None = Field(default=None, max_length=100)


class GradedCardDetailsCreate(GradedCardDetailsBase):
    """Graded-card details tied one-to-one to an asset."""

    asset_id: int


class GradedCardDetailsRead(GradedCardDetailsCreate):
    """Persisted graded-card details."""

    pass


class SealedProductMetadataBase(DomainSchema):
    """Catalog-like identity fields specific to a sealed product."""

    product_name: str = Field(min_length=1, max_length=255)
    set_name: str | None = Field(default=None, max_length=255)
    year: int | None = None
    sealed_product_type: SealedProductType
    is_pokemon_center_exclusive: bool | None = None
    external_source: ExternalSource | None = None
    external_id: str | None = Field(default=None, max_length=255)
    image_url: str | None = None


class SealedProductMetadataCreate(SealedProductMetadataBase):
    """Sealed metadata tied one-to-one to an asset."""

    asset_id: int


class SealedProductMetadataRead(SealedProductMetadataCreate):
    """Persisted sealed metadata with its row identifier."""

    id: int


class PurchaseLotBase(DomainSchema):
    """Acquisition facts used to calculate quantity and cost basis."""

    purchase_date: date
    quantity: int = Field(gt=0)
    purchase_price_per_unit: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode = DEFAULT_CURRENCY

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        """Canonicalize string currency codes before Literal validation."""

        if isinstance(value, str):
            return normalize_currency(value)
        return value


class PurchaseLotCreate(PurchaseLotBase):
    """Purchase-lot data tied to an existing asset."""

    asset_id: int


class PurchaseLotRead(PurchaseLotCreate):
    """Persisted purchase lot with identity and audit timestamps."""

    id: int
    created_at: datetime
    updated_at: datetime


class AssetImageBase(DomainSchema):
    """Image location, provenance type, and primary-display flag."""

    image_type: ImageType
    url_or_path: str = Field(min_length=1)
    is_primary: bool = False


class AssetImageCreate(AssetImageBase):
    """Image metadata tied to an existing asset."""

    asset_id: int


class AssetImageRead(AssetImageCreate):
    """Persisted image metadata with identity and creation time."""

    id: int
    created_at: datetime


class PriceSnapshotBase(DomainSchema):
    """Point-in-time market price with source and confidence metadata."""

    market_price_per_unit: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode = DEFAULT_CURRENCY
    source: PriceSource = PriceSource.MANUAL
    confidence: Decimal | None = Field(
        default=None, ge=0, le=1, max_digits=4, decimal_places=3
    )
    observed_at: datetime | None = None
    metadata_json: dict[str, Any] | None = None

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        """Canonicalize string currency codes before Literal validation."""

        if isinstance(value, str):
            return normalize_currency(value)
        return value


class PriceSnapshotCreate(PriceSnapshotBase):
    """Price observation tied to an existing asset."""

    asset_id: int


class PriceSnapshotRead(PriceSnapshotCreate):
    """Persisted price observation with identity and resolved timestamp."""

    id: int
    observed_at: datetime
