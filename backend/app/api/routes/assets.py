from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.assets import AssetCreateRequest, AssetResponse, AssetUpdateRequest
from app.schemas.purchase_lots import PurchaseLotCreateRequest, PurchaseLotResponse
from app.services import assets as asset_service
from app.services import purchase_lots as purchase_lot_service


router = APIRouter(prefix="/assets", tags=["assets"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _not_found(asset_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Asset {asset_id} was not found.",
    )


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
def create_asset(data: AssetCreateRequest, db: DatabaseSession) -> AssetResponse:
    return asset_service.create_asset(db, data)


@router.get("", response_model=list[AssetResponse])
def list_assets(db: DatabaseSession) -> list[AssetResponse]:
    return asset_service.list_assets(db)


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(asset_id: int, db: DatabaseSession) -> AssetResponse:
    try:
        return asset_service.get_asset(db, asset_id)
    except asset_service.AssetNotFoundError:
        raise _not_found(asset_id) from None


@router.patch("/{asset_id}", response_model=AssetResponse)
def update_asset(
    asset_id: int, data: AssetUpdateRequest, db: DatabaseSession
) -> AssetResponse:
    try:
        return asset_service.update_asset(db, asset_id, data)
    except asset_service.AssetNotFoundError:
        raise _not_found(asset_id) from None


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_asset(asset_id: int, db: DatabaseSession) -> Response:
    try:
        asset_service.delete_asset(db, asset_id)
    except asset_service.AssetNotFoundError:
        raise _not_found(asset_id) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{asset_id}/purchase-lots",
    response_model=PurchaseLotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_purchase_lot(
    asset_id: int, data: PurchaseLotCreateRequest, db: DatabaseSession
) -> PurchaseLotResponse:
    try:
        return purchase_lot_service.create_purchase_lot(db, asset_id, data)
    except asset_service.AssetNotFoundError:
        raise _not_found(asset_id) from None
