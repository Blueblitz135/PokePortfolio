"""Public pricing evidence and refresh status, with explicit source attribution."""

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class MarketPoint(BaseModel):
    observed_at: datetime
    price_cad: Decimal


class TCGPlayerVariant(BaseModel):
    printing: str
    market_price_cad: Decimal | None = None
    low_price_cad: Decimal | None = None
    median_price_cad: Decimal | None = None
    high_price_cad: Decimal | None = None


class TCGPlayerComparison(BaseModel):
    source: str = "TCGPlayer"
    source_url: str = "https://tcgdex.dev/reference/card#tcgplayer-pricing"
    state: str = "unavailable"
    observed_at: datetime | None = None
    currency: str = "CAD"
    source_currency: str = "USD"
    usd_to_cad_rate: Decimal | None = None
    note: str = "Raw-card marketplace reference; not a graded or condition-specific valuation."
    variants: list[TCGPlayerVariant] = Field(default_factory=list)


class MarketPricing(BaseModel):
    state: Literal["available", "unavailable", "unmatched", "unsupported", "not_configured"]
    detail: str
    source: str = "Marketplace and verified store sales"
    source_url: str = "https://justtcg.com/features"
    fetched_at: datetime
    observed_at: datetime | None = None
    currency: str = "CAD"
    source_currency: str = "USD"
    usd_to_cad_rate: Decimal | None = None
    printing: str | None = None
    market_price_cad: Decimal | None = None
    history_duration: str = "90d"
    history: list[MarketPoint] = Field(default_factory=list)
    growth_percent: Decimal | None = None
    tcgplayer: TCGPlayerComparison | None = None
