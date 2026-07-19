from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.asset_images import AssetImageResponse
from app.services import asset_images as image_service
from app.services import assets as asset_service


router = APIRouter(prefix="/assets/{asset_id}/images", tags=["asset images"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def _asset_not_found(asset_id: int) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Asset {asset_id} was not found.",
    )


@router.post("", response_model=AssetImageResponse, status_code=status.HTTP_201_CREATED)
async def upload_asset_image(
    asset_id: int,
    file: Annotated[UploadFile, File()],
    db: DatabaseSession,
    is_primary: Annotated[bool, Form()] = False,
) -> AssetImageResponse:
    try:
        return await image_service.create_asset_image(db, asset_id, file, is_primary)
    except asset_service.AssetNotFoundError:
        raise _asset_not_found(asset_id) from None
    except image_service.ImageTooLargeError as exc:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(exc)
        ) from None
    except image_service.InvalidImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from None


@router.get("", response_model=list[AssetImageResponse])
def list_asset_images(
    asset_id: int, db: DatabaseSession
) -> list[AssetImageResponse]:
    try:
        return image_service.list_asset_images(db, asset_id)
    except asset_service.AssetNotFoundError:
        raise _asset_not_found(asset_id) from None
