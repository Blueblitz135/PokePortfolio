from datetime import datetime

from app.schemas.domain import AssetImageBase


class AssetImageResponse(AssetImageBase):
    id: int
    asset_id: int
    created_at: datetime
