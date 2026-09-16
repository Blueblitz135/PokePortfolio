"""Canonical string enums persisted by models and exposed through API schemas."""

from enum import Enum


class AssetType(str, Enum):
    """Top-level categories whose prices and performance stay separate."""
    RAW_CARD = "raw_card"
    GRADED_CARD = "graded_card"
    SEALED_PRODUCT = "sealed_product"


class ExternalSource(str, Enum):
    """Providers from which asset identity metadata may originate."""
    MANUAL = "manual"
    TCGDEX = "tcgdex"
    POKEMON_TCG_API = "pokemon_tcg_api"


class RawCardCondition(str, Enum):
    """Supported physical conditions for ungraded cards."""
    NM = "NM"
    LP = "LP"
    MP = "MP"
    DMG = "DMG"


class GradingCompany(str, Enum):
    """Supported authentication and grading companies."""
    PSA = "PSA"
    BGS = "BGS"
    CGC = "CGC"
    TAG = "TAG"
    OTHER = "OTHER"


class SealedProductType(str, Enum):
    """Supported sealed-product form factors."""
    BOOSTER_BOX = "booster_box"
    BOOSTER_PACK = "booster_pack"
    ELITE_TRAINER_BOX = "elite_trainer_box"
    BOOSTER_BUNDLE = "booster_bundle"
    TIN = "tin"
    COLLECTION_BOX = "collection_box"
    OTHER = "other"


class ImageType(str, Enum):
    """Distinguishes provider images from user-uploaded images."""
    UPLOADED = "uploaded"
    API = "api"
    GENERATED_OVERLAY = "generated_overlay"
    PLACEHOLDER = "placeholder"


class PriceSource(str, Enum):
    """Identifies how a normalized market price was obtained."""
    MANUAL = "manual"
    TCGDEX = "tcgdex"
    POKEMON_TCG_API = "pokemon_tcg_api"
    JUSTTCG = "justtcg"
    EBAY = "ebay"
    BLENDED = "blended"
