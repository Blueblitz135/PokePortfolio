"""Create the FastAPI application and mount API and static-file routes."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.router import api_router
from app.config import settings


# All feature routers are exposed beneath /api; uploaded and bundled images remain
# separate static resources so the frontend can reference them directly.
app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix="/api")

settings.upload_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
