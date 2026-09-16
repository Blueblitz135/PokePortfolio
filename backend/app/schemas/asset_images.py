"""Response schema for images stored against portfolio assets."""

from datetime import datetime

from app.schemas.domain import AssetImageBase


class AssetImageResponse(AssetImageBase):
    """Serialized asset image including database identity and creation time."""

    id: int
    asset_id: int
    created_at: datetime
