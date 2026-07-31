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
    model_config = ConfigDict(from_attributes=True)


class AssetBase(DomainSchema):
    asset_type: AssetType
    display_name: str = Field(min_length=1, max_length=255)
    user_note: str | None = None


class AssetCreate(AssetBase):
    pass


class AssetRead(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime


class CardMetadataBase(DomainSchema):
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
    asset_id: int


class CardMetadataRead(CardMetadataCreate):
    id: int


class RawCardDetailsBase(DomainSchema):
    condition: RawCardCondition


class RawCardDetailsCreate(RawCardDetailsBase):
    asset_id: int


class RawCardDetailsRead(RawCardDetailsCreate):
    pass


class GradedCardDetailsBase(DomainSchema):
    grading_company: GradingCompany
    grade: Decimal = Field(gt=0, le=10, max_digits=3, decimal_places=1)
    cert_number: str | None = Field(default=None, max_length=100)


class GradedCardDetailsCreate(GradedCardDetailsBase):
    asset_id: int


class GradedCardDetailsRead(GradedCardDetailsCreate):
    pass


class SealedProductMetadataBase(DomainSchema):
    product_name: str = Field(min_length=1, max_length=255)
    set_name: str | None = Field(default=None, max_length=255)
    year: int | None = None
    sealed_product_type: SealedProductType
    is_pokemon_center_exclusive: bool | None = None
    external_source: ExternalSource | None = None
    external_id: str | None = Field(default=None, max_length=255)
    image_url: str | None = None


class SealedProductMetadataCreate(SealedProductMetadataBase):
    asset_id: int


class SealedProductMetadataRead(SealedProductMetadataCreate):
    id: int


class PurchaseLotBase(DomainSchema):
    purchase_date: date
    quantity: int = Field(gt=0)
    purchase_price_per_unit: Decimal = Field(
        ge=0, max_digits=12, decimal_places=2
    )
    currency: CurrencyCode = DEFAULT_CURRENCY

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency_code(cls, value: object) -> object:
        if isinstance(value, str):
            return normalize_currency(value)
        return value


class PurchaseLotCreate(PurchaseLotBase):
    asset_id: int


class PurchaseLotRead(PurchaseLotCreate):
    id: int
    created_at: datetime
    updated_at: datetime


class AssetImageBase(DomainSchema):
    image_type: ImageType
    url_or_path: str = Field(min_length=1)
    is_primary: bool = False


class AssetImageCreate(AssetImageBase):
    asset_id: int


class AssetImageRead(AssetImageCreate):
    id: int
    created_at: datetime


class PriceSnapshotBase(DomainSchema):
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
        if isinstance(value, str):
            return normalize_currency(value)
        return value


class PriceSnapshotCreate(PriceSnapshotBase):
    asset_id: int


class PriceSnapshotRead(PriceSnapshotCreate):
    id: int
    observed_at: datetime
