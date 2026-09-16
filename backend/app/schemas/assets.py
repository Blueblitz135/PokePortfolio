"""Validate asset create/update requests and serialize hydrated asset responses."""

from datetime import datetime

from pydantic import Field, model_validator

from app.models.enums import AssetType
from app.schemas.asset_images import AssetImageResponse
from app.schemas.calculations import AssetCalculationSummary
from app.schemas.domain import (
    AssetBase,
    CardMetadataBase,
    DomainSchema,
    GradedCardDetailsBase,
    RawCardDetailsBase,
    SealedProductMetadataBase,
)
from app.schemas.purchase_lots import PurchaseLotResponse
from app.schemas.price_snapshots import PriceSnapshotResponse


class CardMetadataPayload(CardMetadataBase):
    """Card metadata accepted while creating a raw or graded asset."""

    pass


class RawCardDetailsPayload(RawCardDetailsBase):
    """Raw-card condition accepted during asset creation."""

    pass


class GradedCardDetailsPayload(GradedCardDetailsBase):
    """Grading details accepted during asset creation."""

    pass


class SealedProductMetadataPayload(SealedProductMetadataBase):
    """Sealed-product metadata accepted during asset creation."""

    pass


class AssetCreateRequest(AssetBase):
    """Create payload whose nested metadata must match the selected asset type."""

    card_metadata: CardMetadataPayload | None = None
    raw_details: RawCardDetailsPayload | None = None
    graded_details: GradedCardDetailsPayload | None = None
    sealed_product_metadata: SealedProductMetadataPayload | None = None

    @model_validator(mode="after")
    def validate_metadata_for_asset_type(self) -> "AssetCreateRequest":
        """Reject missing or mixed raw, graded, and sealed metadata."""

        if self.asset_type == AssetType.RAW_CARD:
            if self.card_metadata is None or self.raw_details is None:
                raise ValueError("Raw cards require card_metadata and raw_details.")
            if self.graded_details is not None or self.sealed_product_metadata is not None:
                raise ValueError("Raw cards cannot include graded or sealed metadata.")
        elif self.asset_type == AssetType.GRADED_CARD:
            if self.card_metadata is None or self.graded_details is None:
                raise ValueError(
                    "Graded cards require card_metadata and graded_details."
                )
            if self.raw_details is not None or self.sealed_product_metadata is not None:
                raise ValueError("Graded cards cannot include raw or sealed metadata.")
        elif self.asset_type == AssetType.SEALED_PRODUCT:
            if self.sealed_product_metadata is None:
                raise ValueError("Sealed products require sealed_product_metadata.")
            if (
                self.card_metadata is not None
                or self.raw_details is not None
                or self.graded_details is not None
            ):
                raise ValueError("Sealed products cannot include card metadata.")

        return self


class AssetUpdateRequest(DomainSchema):
    """Supported partial edits for an existing asset's user-facing fields."""

    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    user_note: str | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "AssetUpdateRequest":
        """Require at least one field and prevent a null display name."""

        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        if "display_name" in self.model_fields_set and self.display_name is None:
            raise ValueError("display_name cannot be null.")
        return self


class CardMetadataResponse(CardMetadataBase):
    """Persisted card metadata including its identifier."""

    id: int


class RawCardDetailsResponse(RawCardDetailsBase):
    """Persisted raw-card details embedded in an asset response."""

    pass


class GradedCardDetailsResponse(GradedCardDetailsBase):
    """Persisted graded-card details embedded in an asset response."""

    pass


class SealedProductMetadataResponse(SealedProductMetadataBase):
    """Persisted sealed-product metadata including its identifier."""

    id: int


from app.schemas.market_pricing import MarketPricing


class AssetResponse(AssetBase):
    """Complete asset representation including children and calculated fields."""

    id: int
    created_at: datetime
    updated_at: datetime
    images: list[AssetImageResponse] = Field(default_factory=list)
    primary_image_url: str
    purchase_lots: list[PurchaseLotResponse] = Field(default_factory=list)
    latest_price_snapshot: PriceSnapshotResponse | None = None
    summary: AssetCalculationSummary
    market_pricing: MarketPricing | None = None
    card_metadata: CardMetadataResponse | None = None
    raw_details: RawCardDetailsResponse | None = Field(
        default=None, validation_alias="raw_card_details"
    )
    graded_details: GradedCardDetailsResponse | None = Field(
        default=None, validation_alias="graded_card_details"
    )
    sealed_product_metadata: SealedProductMetadataResponse | None = None
