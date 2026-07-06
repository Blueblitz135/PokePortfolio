from enum import Enum


class AssetType(str, Enum):
    RAW_CARD = "raw_card"
    GRADED_CARD = "graded_card"
    SEALED_PRODUCT = "sealed_product"


class ExternalSource(str, Enum):
    MANUAL = "manual"
    TCGDEX = "tcgdex"
    POKEMON_TCG_API = "pokemon_tcg_api"


class RawCardCondition(str, Enum):
    NM = "NM"
    LP = "LP"
    MP = "MP"
    DMG = "DMG"


class GradingCompany(str, Enum):
    PSA = "PSA"
    BGS = "BGS"
    CGC = "CGC"
    TAG = "TAG"
    OTHER = "OTHER"


class SealedProductType(str, Enum):
    BOOSTER_BOX = "booster_box"
    BOOSTER_PACK = "booster_pack"
    ELITE_TRAINER_BOX = "elite_trainer_box"
    BOOSTER_BUNDLE = "booster_bundle"
    TIN = "tin"
    COLLECTION_BOX = "collection_box"
    OTHER = "other"


class ImageType(str, Enum):
    UPLOADED = "uploaded"
    API = "api"
    GENERATED_OVERLAY = "generated_overlay"
    PLACEHOLDER = "placeholder"


class PriceSource(str, Enum):
    MANUAL = "manual"
    TCGDEX = "tcgdex"
    POKEMON_TCG_API = "pokemon_tcg_api"
    JUSTTCG = "justtcg"
    EBAY = "ebay"
    BLENDED = "blended"
