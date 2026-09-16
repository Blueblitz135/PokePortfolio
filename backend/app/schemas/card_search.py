"""Normalized card-search result returned independently of provider JSON."""

from pydantic import Field

from app.models.enums import ExternalSource
from app.schemas.domain import DomainSchema


class CardSearchResult(DomainSchema):
    """Card identity and image fields used by the add-to-collection workflow."""

    external_source: ExternalSource
    external_id: str = Field(min_length=1, max_length=255)
    name: str = Field(min_length=1, max_length=255)
    set_name: str = Field(min_length=1, max_length=255)
    set_id: str = Field(min_length=1, max_length=100)
    year: int | None = None
    card_number: str = Field(min_length=1, max_length=50)
    set_total: str | None = Field(default=None, max_length=50)
    rarity: str | None = Field(default=None, max_length=100)
    image_url: str | None = None
