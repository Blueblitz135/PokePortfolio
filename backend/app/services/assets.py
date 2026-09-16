"""Implement asset persistence, eager loading, and response-only derived fields."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import (
    Asset,
    CardMetadata,
    GradedCardDetails,
    RawCardDetails,
    SealedProductMetadata,
)
from app.schemas.assets import AssetCreateRequest, AssetUpdateRequest
from app.services.calculations import (
    calculate_asset_summary,
    get_latest_price_snapshot,
)


PLACEHOLDER_IMAGE_URL = "/static/placeholders/asset.svg"


class AssetNotFoundError(Exception):
    """Raised when an asset identifier does not exist."""

    pass


def _asset_query():
    """Build the shared eager-loading query used by asset reads."""

    return select(Asset).options(
        selectinload(Asset.card_metadata),
        selectinload(Asset.raw_card_details),
        selectinload(Asset.graded_card_details),
        selectinload(Asset.sealed_product_metadata),
        selectinload(Asset.images),
        selectinload(Asset.purchase_lots),
        selectinload(Asset.price_snapshots),
    )


def _with_derived_fields(asset: Asset) -> Asset:
    """Attach summary, latest price, and preferred image fields for serialization."""

    primary_image = next((image for image in asset.images if image.is_primary), None)
    card_metadata_image = (
        asset.card_metadata.image_url if asset.card_metadata is not None else None
    )
    asset.summary = calculate_asset_summary(asset)
    asset.latest_price_snapshot = get_latest_price_snapshot(asset)
    asset.primary_image_url = (
        primary_image.url_or_path
        if primary_image is not None
        else card_metadata_image or PLACEHOLDER_IMAGE_URL
    )
    return asset


def create_asset(db: Session, data: AssetCreateRequest) -> Asset:
    """Persist an asset with only the metadata allowed for its validated type."""

    asset = Asset(
        asset_type=data.asset_type,
        display_name=data.display_name,
        user_note=data.user_note,
    )

    if data.card_metadata is not None:
        asset.card_metadata = CardMetadata(**data.card_metadata.model_dump())
    if data.raw_details is not None:
        asset.raw_card_details = RawCardDetails(**data.raw_details.model_dump())
    if data.graded_details is not None:
        asset.graded_card_details = GradedCardDetails(
            **data.graded_details.model_dump()
        )
    if data.sealed_product_metadata is not None:
        asset.sealed_product_metadata = SealedProductMetadata(
            **data.sealed_product_metadata.model_dump()
        )

    db.add(asset)
    db.commit()
    return get_asset(db, asset.id)


def list_assets(db: Session) -> list[Asset]:
    """Return all assets in stable insertion order with derived fields populated."""

    result = db.scalars(_asset_query().order_by(Asset.id))
    return [_with_derived_fields(asset) for asset in result.all()]


def get_asset(db: Session, asset_id: int) -> Asset:
    """Return a hydrated asset or raise AssetNotFoundError."""

    asset = db.scalar(_asset_query().where(Asset.id == asset_id))
    if asset is None:
        raise AssetNotFoundError
    return _with_derived_fields(asset)


def update_asset(db: Session, asset_id: int, data: AssetUpdateRequest) -> Asset:
    """Apply explicitly supplied editable fields and return the refreshed asset."""

    asset = get_asset(db, asset_id)
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(asset, field, value)

    db.commit()
    return get_asset(db, asset_id)


def delete_asset(db: Session, asset_id: int) -> None:
    """Delete an asset; ORM cascades remove its dependent records."""

    asset = get_asset(db, asset_id)
    db.delete(asset)
    db.commit()
