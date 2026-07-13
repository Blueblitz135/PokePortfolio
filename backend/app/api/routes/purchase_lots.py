from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.purchase_lots import (
    PurchaseLotResponse,
    PurchaseLotUpdateRequest,
)
from app.services import purchase_lots as purchase_lot_service


router = APIRouter(prefix="/purchase-lots", tags=["purchase lots"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _not_found(lot_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Purchase lot {lot_id} was not found.",
    )


@router.patch("/{lot_id}", response_model=PurchaseLotResponse)
def update_purchase_lot(
    lot_id: int, data: PurchaseLotUpdateRequest, db: DatabaseSession
) -> PurchaseLotResponse:
    try:
        return purchase_lot_service.update_purchase_lot(db, lot_id, data)
    except purchase_lot_service.PurchaseLotNotFoundError:
        raise _not_found(lot_id) from None


@router.delete("/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase_lot(lot_id: int, db: DatabaseSession) -> Response:
    try:
        purchase_lot_service.delete_purchase_lot(db, lot_id)
    except purchase_lot_service.PurchaseLotNotFoundError:
        raise _not_found(lot_id) from None
    return Response(status_code=status.HTTP_204_NO_CONTENT)
