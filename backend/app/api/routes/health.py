"""Expose a lightweight endpoint used to verify that the backend is reachable."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a stable success payload without accessing the database."""

    return HealthResponse(status="ok")
