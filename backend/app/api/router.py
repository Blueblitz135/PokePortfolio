from fastapi import APIRouter

from app.api.routes import asset_images, assets, health, purchase_lots


api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(assets.router)
api_router.include_router(asset_images.router)
api_router.include_router(purchase_lots.router)
