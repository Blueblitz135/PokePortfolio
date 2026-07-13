from datetime import datetime

from pydantic import Field, model_validator

from app.models.enums import AssetType
from app.schemas.domain import (
    AssetBase,
    CardMetadataBase,
    DomainSchema,
    GradedCardDetailsBase,
    RawCardDetailsBase,
    SealedProductMetadataBase,
)
from app.schemas.calculations import AssetCalculationSummary
from app.schemas.purchase_lots import PurchaseLotResponse


class CardMetadataPayload(CardMetadataBase):
    pass


class RawCardDetailsPayload(RawCardDetailsBase):
    pass


class GradedCardDetailsPayload(GradedCardDetailsBase):
    pass


class SealedProductMetadataPayload(SealedProductMetadataBase):
    pass


class AssetCreateRequest(AssetBase):
    card_metadata: CardMetadataPayload | None = None
    raw_details: RawCardDetailsPayload | None = None
    graded_details: GradedCardDetailsPayload | None = None
    sealed_product_metadata: SealedProductMetadataPayload | None = None

    @model_validator(mode="after")
    def validate_metadata_for_asset_type(self) -> "AssetCreateRequest":
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
    display_name: str | None = Field(default=None, min_length=1, max_length=255)
    user_note: str | None = None

    @model_validator(mode="after")
    def validate_update_fields(self) -> "AssetUpdateRequest":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")
        if "display_name" in self.model_fields_set and self.display_name is None:
            raise ValueError("display_name cannot be null.")
        return self


class CardMetadataResponse(CardMetadataBase):
    id: int


class RawCardDetailsResponse(RawCardDetailsBase):
    pass


class GradedCardDetailsResponse(GradedCardDetailsBase):
    pass


class SealedProductMetadataResponse(SealedProductMetadataBase):
    id: int


class AssetResponse(AssetBase):
    id: int
    created_at: datetime
    updated_at: datetime
    purchase_lots: list[PurchaseLotResponse] = Field(default_factory=list)
    summary: AssetCalculationSummary
    card_metadata: CardMetadataResponse | None = None
    raw_details: RawCardDetailsResponse | None = Field(
        default=None, validation_alias="raw_card_details"
    )
    graded_details: GradedCardDetailsResponse | None = Field(
        default=None, validation_alias="graded_card_details"
    )
    sealed_product_metadata: SealedProductMetadataResponse | None = None
