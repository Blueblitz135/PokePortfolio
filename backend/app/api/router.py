from fastapi import APIRouter

from app.api.routes import (
    asset_images,
    assets,
    health,
    price_snapshots,
    purchase_lots,
    search,
)


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(asset_images.router)
api_router.include_router(price_snapshots.router)
api_router.include_router(purchase_lots.router)
api_router.include_router(search.router)
