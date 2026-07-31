from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models import AssetType, RawCardCondition
from app.schemas import AssetCreate, CardMetadataCreate, PurchaseLotCreate
from app.schemas.price_snapshots import PriceSnapshotCreateRequest
from app.schemas.purchase_lots import (
    PurchaseLotCreateRequest,
    PurchaseLotUpdateRequest,
)


def test_asset_schema_has_no_quantity_field() -> None:
    asset = AssetCreate(
        asset_type=AssetType.RAW_CARD,
        display_name="Umbreon VMAX",
    )

    assert "quantity" not in asset.model_dump()


def test_card_number_and_set_total_are_separate_fields() -> None:
    card = CardMetadataCreate(
        asset_id=1,
        name="Umbreon VMAX",
        set_name="Evolving Skies",
        card_number="215",
        set_total="203",
    )

    assert card.card_number == "215"
    assert card.set_total == "203"


def test_purchase_lot_defaults_to_cad_and_requires_positive_quantity() -> None:
    lot = PurchaseLotCreate(
        asset_id=1,
        purchase_date=date(2025, 8, 1),
        quantity=1,
        purchase_price_per_unit=Decimal("750.00"),
    )

    assert lot.currency == "CAD"

    with pytest.raises(ValidationError):
        PurchaseLotCreate(
            asset_id=1,
            purchase_date=date(2025, 8, 1),
            quantity=0,
            purchase_price_per_unit=Decimal("750.00"),
        )


def test_currency_schemas_normalize_cad_and_reject_unsupported_values() -> None:
    create_lot = PurchaseLotCreateRequest(
        purchase_date=date(2025, 8, 1),
        quantity=1,
        purchase_price_per_unit=Decimal("750.00"),
        currency="cad",
    )
    update_lot = PurchaseLotUpdateRequest(currency=" cad ")
    snapshot = PriceSnapshotCreateRequest(
        market_price_per_unit=Decimal("900.00"), currency="cad"
    )

    assert create_lot.currency == "CAD"
    assert update_lot.currency == "CAD"
    assert snapshot.currency == "CAD"

    with pytest.raises(ValidationError):
        PurchaseLotCreateRequest(
            purchase_date=date(2025, 8, 1),
            quantity=1,
            purchase_price_per_unit=Decimal("750.00"),
            currency="USD",
        )

    with pytest.raises(ValidationError):
        PurchaseLotUpdateRequest(currency=None)


def test_raw_card_condition_uses_supported_values() -> None:
    assert RawCardCondition.NM.value == "NM"
