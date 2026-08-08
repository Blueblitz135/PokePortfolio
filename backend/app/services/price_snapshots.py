from app.adapters.justtcg import (
    JustTCGAdapter,
    JustTCGConfigurationError,
    JustTCGError,
    RawCardPriceLookup,
)
from app.config import settings
from sqlalchemy.orm import Session

from app.models import AssetType, PriceSnapshot, PriceSource
from app.schemas.price_snapshots import PriceSnapshotCreateRequest
from app.services import assets as asset_service


class ExternalPriceNotFoundError(Exception):
    """Raised when an enabled provider has no exact match for an asset."""


class ExternalPriceNotSupportedError(Exception):
    """Raised when an adapter does not support an asset's pricing category."""


justtcg_adapter = JustTCGAdapter(
    api_key=settings.justtcg_api_key,
    usd_to_cad_rate=settings.justtcg_usd_to_cad_rate,
    base_url=settings.justtcg_base_url,
    timeout_seconds=settings.justtcg_timeout_seconds,
)


def create_manual_price_snapshot(
    db: Session, asset_id: int, data: PriceSnapshotCreateRequest
) -> PriceSnapshot:
    asset_service.get_asset(db, asset_id)

    price_snapshot = PriceSnapshot(
        asset_id=asset_id,
        market_price_per_unit=data.market_price_per_unit,
        currency=data.currency,
        source=PriceSource.MANUAL,
        confidence=data.confidence,
    )
    db.add(price_snapshot)
    db.commit()
    db.refresh(price_snapshot)
    return price_snapshot


async def create_justtcg_price_snapshot(
    db: Session, asset_id: int
) -> PriceSnapshot:
    asset = asset_service.get_asset(db, asset_id)
    if asset.asset_type != AssetType.RAW_CARD:
        raise ExternalPriceNotSupportedError(
            "JustTCG pricing currently supports raw cards only."
        )
    if asset.card_metadata is None or asset.raw_card_details is None:
        raise ExternalPriceNotSupportedError(
            "Raw card pricing requires card metadata and a condition."
        )

    quote = await justtcg_adapter.fetch_raw_card_price(
        RawCardPriceLookup(
            name=asset.card_metadata.name,
            set_name=asset.card_metadata.set_name,
            card_number=asset.card_metadata.card_number,
            condition=asset.raw_card_details.condition,
        )
    )
    if quote is None:
        raise ExternalPriceNotFoundError

    price_snapshot = PriceSnapshot(
        asset_id=asset_id,
        market_price_per_unit=quote.market_price_per_unit,
        currency=quote.currency,
        source=PriceSource.JUSTTCG,
        confidence=quote.confidence,
        observed_at=quote.observed_at,
        metadata_json=quote.metadata,
    )
    db.add(price_snapshot)
    db.commit()
    db.refresh(price_snapshot)
    return price_snapshot
