"""Refresh every card independently and persist normalized, attributed quotes."""

import asyncio
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.adapters.justtcg import JustTCGError, RawCardPriceLookup
from app.adapters.tcgdex import TCGdexAdapter, TCGdexError
from app.config import settings
from app.models import Asset, AssetType, PriceSnapshot, PriceSource
from app.schemas.market_pricing import MarketPoint, MarketPricing, TCGPlayerComparison
from app.services import assets as asset_service
from app.services.price_snapshots import justtcg_adapter
from app.services.calculations import calculate_asset_summary


tcgdex_adapter = TCGdexAdapter(settings.tcgdex_base_url, settings.tcgdex_timeout_seconds)


def card_lookup(asset: Asset) -> RawCardPriceLookup | None:
    card = asset.card_metadata
    if card is None or asset.asset_type == AssetType.SEALED_PRODUCT:
        return None
    raw, graded = asset.raw_card_details, asset.graded_card_details
    if not raw and not graded:
        return None
    return RawCardPriceLookup(
        name=card.name, set_name=card.set_name, card_number=card.card_number,
        set_total=card.set_total, printing=card.variant,
        condition=raw.condition if raw else None,
        grading_company=graded.grading_company.value if graded else None,
        grade=format(graded.grade.normalize(), "f") if graded else None,
    )


async def fetch_pricing(asset: Asset, duration: str, comparison: bool) -> MarketPricing:
    result = MarketPricing(state="unavailable", detail="Current market data is unavailable; saved values may be older.", fetched_at=datetime.now(timezone.utc), history_duration=duration)
    lookup = card_lookup(asset)
    if lookup is None:
        result.state = "unsupported"
        result.detail = "Automatic card pricing does not cover this asset; saved prices are shown."
        return result
    rate = settings.justtcg_usd_to_cad_rate
    result.usd_to_cad_rate = rate

    async def market():
        if not justtcg_adapter.is_configured:
            result.state = "not_configured"
            result.detail = "Market pricing is not configured; saved prices are shown."
            return
        try:
            history = await justtcg_adapter.fetch_raw_card_price_history(lookup, duration)
            if history is None:
                result.state = "unmatched"
                result.detail = "No unique price for this card, condition/grade and printing. Specify the printing if multiple versions exist. Saved prices are shown."
                return
            result.printing = history.printing
            result.history = [MarketPoint(observed_at=p.observed_at, price_cad=p.market_price_per_unit) for p in history.points]
            result.growth_percent = history.growth_percent
            result.market_price_cad = history.current_price_cad
            result.observed_at = history.current_observed_at
            if result.market_price_cad is not None and result.observed_at:
                result.state = "available"
                result.detail = "Latest available market estimate, matched to your card condition or grade."
            else:
                result.detail = "No current quote is available; any returned history is shown separately."
        except JustTCGError:
            pass

    async def tcgplayer():
        if not comparison:
            return
        if rate is None or rate <= 0:
            result.tcgplayer = TCGPlayerComparison(note="CAD conversion is not configured.")
            return
        try:
            result.tcgplayer = await tcgdex_adapter.fetch_tcgplayer_prices(asset.card_metadata, rate)
        except TCGdexError:
            result.tcgplayer = TCGPlayerComparison(note="TCGPlayer reference prices could not be fetched.")

    await asyncio.gather(market(), tcgplayer())
    return result


async def refresh_assets(db: Session, assets: list[Asset], *, duration: str = "90d", comparison: bool = False) -> list[Asset]:
    """Bound concurrency, not collection size; one failed card cannot hide the others."""
    semaphore = asyncio.Semaphore(3)

    async def fetch(asset):
        async with semaphore:
            return await fetch_pricing(asset, duration, comparison)

    results = await asyncio.gather(*(fetch(asset) for asset in assets))
    # Another refresh may have saved the same observations while HTTP calls ran.
    # Reload relationships before duplicate checks; persistence below has no awaits.
    db.expire_all()
    for asset, result in zip(assets, results, strict=True):
        if result.state == "available":
            # Keep repeated reads of the same provider observation idempotent.
            observed = result.observed_at.replace(tzinfo=None)
            duplicate = any(
                p.source == PriceSource.JUSTTCG
                and p.observed_at.replace(tzinfo=None) == observed
                and p.market_price_per_unit == result.market_price_cad
                for p in asset.price_snapshots
            )
            if not duplicate:
                asset.price_snapshots.append(PriceSnapshot(
                    market_price_per_unit=result.market_price_cad, currency="CAD",
                    source=PriceSource.JUSTTCG, observed_at=result.observed_at,
                    metadata_json={"pricing_source": result.source, "source_url": result.source_url,
                                   "usd_to_cad_rate": str(result.usd_to_cad_rate), "printing": result.printing},
                ))
        asset.market_pricing = result
    db.commit()
    # Reload persisted snapshots to avoid mixing SQLite naive and aware timestamps.
    ids = [asset.id for asset in assets]
    db.expire_all()
    refreshed = [asset_service.get_asset(db, asset_id) for asset_id in ids]
    for asset, result in zip(refreshed, results, strict=True):
        asset.market_pricing = result
        if result.state == "available":
            # A later manual snapshot must not replace the requested market estimate.
            asset.summary = calculate_asset_summary(asset, result.market_price_cad)
    return refreshed
