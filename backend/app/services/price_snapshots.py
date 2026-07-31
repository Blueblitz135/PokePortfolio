from sqlalchemy.orm import Session

from app.models import PriceSnapshot, PriceSource
from app.schemas.price_snapshots import PriceSnapshotCreateRequest
from app.services import assets as asset_service


def create_manual_price_snapshot(
    db: Session, asset_id: int, data: PriceSnapshotCreateRequest
) -> PriceSnapshot:
    asset_service.get_asset(db, asset_id)

    price_snapshot = PriceSnapshot(
        asset_id=asset_id,
        market_price_per_unit=data.market_price_per_unit,
        currency=data.currency,
        source=PriceSource.MANUAL,
        confidence=data.confidence,
    )
    db.add(price_snapshot)
    db.commit()
    db.refresh(price_snapshot)
    return price_snapshot
