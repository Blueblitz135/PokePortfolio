from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PurchaseLot
from app.schemas.purchase_lots import (
    PurchaseLotCreateRequest,
    PurchaseLotUpdateRequest,
)
from app.services.assets import get_asset


class PurchaseLotNotFoundError(Exception):
    pass


def create_purchase_lot(
    db: Session, asset_id: int, data: PurchaseLotCreateRequest
) -> PurchaseLot:
    get_asset(db, asset_id)
    purchase_lot = PurchaseLot(asset_id=asset_id, **data.model_dump())

    db.add(purchase_lot)
    db.commit()
    db.refresh(purchase_lot)
    return purchase_lot


def get_purchase_lot(db: Session, lot_id: int) -> PurchaseLot:
    purchase_lot = db.scalar(select(PurchaseLot).where(PurchaseLot.id == lot_id))
    if purchase_lot is None:
        raise PurchaseLotNotFoundError
    return purchase_lot


def update_purchase_lot(
    db: Session, lot_id: int, data: PurchaseLotUpdateRequest
) -> PurchaseLot:
    purchase_lot = get_purchase_lot(db, lot_id)
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(purchase_lot, field, value)

    db.commit()
    db.refresh(purchase_lot)
    return purchase_lot


def delete_purchase_lot(db: Session, lot_id: int) -> None:
    purchase_lot = get_purchase_lot(db, lot_id)
    db.delete(purchase_lot)
    db.commit()
