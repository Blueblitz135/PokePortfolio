"""Validate image uploads, store files safely, and manage primary image records."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.models import AssetImage, ImageType
from app.services import assets as asset_service


ALLOWED_CONTENT_TYPES = {
    ".jpg": {"image/jpeg", "image/jpg"},
    ".jpeg": {"image/jpeg", "image/jpg"},
    ".png": {"image/png"},
    ".webp": {"image/webp"},
}
UPLOAD_URL_PREFIX = "/uploads"


class InvalidImageError(Exception):
    """Raised when an upload's extension, MIME type, or signature is invalid."""

    pass


class ImageTooLargeError(Exception):
    """Raised when an upload exceeds the configured byte limit."""

    pass


def _has_valid_signature(extension: str, content: bytes) -> bool:
    """Confirm that leading bytes match the claimed supported image format."""

    if extension in {".jpg", ".jpeg"}:
        return content.startswith(b"\xff\xd8\xff")
    if extension == ".png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == ".webp":
        return (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        )
    return False


async def _validate_and_read(file: UploadFile) -> tuple[str, bytes]:
    """Read at most the allowed size and validate extension, MIME type, and bytes."""

    extension = Path(file.filename or "").suffix.lower()
    allowed_content_types = ALLOWED_CONTENT_TYPES.get(extension)

    if allowed_content_types is None or file.content_type not in allowed_content_types:
        raise InvalidImageError("Only jpg, jpeg, png, and webp images are allowed.")

    content = await file.read(settings.max_upload_size_bytes + 1)
    if len(content) > settings.max_upload_size_bytes:
        max_size_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise ImageTooLargeError(f"Images must be {max_size_mb} MB or smaller.")
    if not _has_valid_signature(extension, content):
        raise InvalidImageError("The file contents do not match the selected image type.")

    return extension, content


async def create_asset_image(
    db: Session,
    asset_id: int,
    file: UploadFile,
    is_primary: bool,
) -> AssetImage:
    """Store an uploaded file and atomically register it against an asset."""

    asset = asset_service.get_asset(db, asset_id)
    extension, content = await _validate_and_read(file)

    filename = f"{uuid4().hex}{extension}"
    stored_path = settings.upload_dir / filename
    url_path = f"{UPLOAD_URL_PREFIX}/{filename}"
    should_be_primary = is_primary or not any(
        image.is_primary for image in asset.images
    )

    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    # If persistence fails after the file is written, roll back both database and
    # filesystem state so an orphaned upload is not left behind.
    try:
        stored_path.write_bytes(content)
        if should_be_primary:
            for existing_image in asset.images:
                existing_image.is_primary = False

        image = AssetImage(
            asset_id=asset_id,
            image_type=ImageType.UPLOADED,
            url_or_path=url_path,
            is_primary=should_be_primary,
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        return image
    except Exception:
        db.rollback()
        stored_path.unlink(missing_ok=True)
        raise


def list_asset_images(db: Session, asset_id: int) -> list[AssetImage]:
    """Return an existing asset's image records in deterministic ID order."""

    asset = asset_service.get_asset(db, asset_id)
    return sorted(asset.images, key=lambda image: image.id)
