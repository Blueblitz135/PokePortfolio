from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateTable

from app import models  # noqa: F401
from app.db.base import Base
from app.models import (
    Asset,
    AssetType,
    CardMetadata,
    PurchaseLot,
    RawCardCondition,
    RawCardDetails,
)


def test_all_domain_tables_can_be_created() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    assert set(inspect(engine).get_table_names()) == {
        "asset_images",
        "assets",
        "card_metadata",
        "graded_card_details",
        "price_snapshots",
        "purchase_lots",
        "raw_card_details",
        "sealed_product_metadata",
    }


def test_all_domain_tables_compile_for_postgresql() -> None:
    for table in Base.metadata.sorted_tables:
        ddl = str(CreateTable(table).compile(dialect=postgresql.dialect()))

        assert "CREATE TABLE" in ddl


def test_asset_can_store_card_details_and_multiple_purchase_lots() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    asset = Asset(
        asset_type=AssetType.RAW_CARD,
        display_name="Umbreon VMAX",
        card_metadata=CardMetadata(
            name="Umbreon VMAX",
            set_name="Evolving Skies",
            card_number="215",
            set_total="203",
        ),
        raw_card_details=RawCardDetails(condition=RawCardCondition.NM),
        purchase_lots=[
            PurchaseLot(
                purchase_date=date(2025, 8, 1),
                quantity=1,
                purchase_price_per_unit=Decimal("750.00"),
            ),
            PurchaseLot(
                purchase_date=date(2026, 2, 15),
                quantity=2,
                purchase_price_per_unit=Decimal("900.00"),
            ),
        ],
    )

    with Session(engine) as session:
        session.add(asset)
        session.commit()
        session.refresh(asset)

        assert asset.card_metadata.card_number == "215"
        assert asset.card_metadata.set_total == "203"
        assert len(asset.purchase_lots) == 2
        assert all(lot.currency == "CAD" for lot in asset.purchase_lots)
        stored_asset_type = session.execute(
            text("SELECT asset_type FROM assets WHERE id = :id"), {"id": asset.id}
        ).scalar_one()
        assert stored_asset_type == "raw_card"
