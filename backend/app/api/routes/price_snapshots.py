from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.adapters.justtcg import JustTCGConfigurationError, JustTCGError
from app.db.session import get_db
from app.schemas.price_snapshots import (
    PriceSnapshotCreateRequest,
    PriceSnapshotResponse,
)
from app.services import assets as asset_service
from app.services import price_snapshots as price_snapshot_service


router = APIRouter(
    prefix="/assets/{asset_id}/price-snapshots", tags=["price snapshots"]
)
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.post(
    "", response_model=PriceSnapshotResponse, status_code=status.HTTP_201_CREATED
)
def create_manual_price_snapshot(
    asset_id: int, data: PriceSnapshotCreateRequest, db: DatabaseSession
) -> PriceSnapshotResponse:
    try:
        return price_snapshot_service.create_manual_price_snapshot(
            db, asset_id, data
        )
    except asset_service.AssetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} was not found.",
        ) from None


@router.post(
    "/justtcg",
    response_model=PriceSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_justtcg_price_snapshot(
    asset_id: int, db: DatabaseSession
) -> PriceSnapshotResponse:
    try:
        return await price_snapshot_service.create_justtcg_price_snapshot(
            db, asset_id
        )
    except asset_service.AssetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Asset {asset_id} was not found.",
        ) from None
    except price_snapshot_service.ExternalPriceNotSupportedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except price_snapshot_service.ExternalPriceNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="JustTCG has no exact raw-card price match for this asset.",
        ) from None
    except (JustTCGConfigurationError, JustTCGError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="JustTCG pricing is temporarily unavailable.",
        ) from None
