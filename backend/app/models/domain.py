from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import (
    AssetType,
    ExternalSource,
    GradingCompany,
    ImageType,
    PriceSource,
    RawCardCondition,
    SealedProductType,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def enum_values(enum_class: type[Enum]) -> list[str]:
    return [str(member.value) for member in enum_class]


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_type: Mapped[AssetType] = mapped_column(
        SqlEnum(
            AssetType,
            name="asset_type",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    user_note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    card_metadata: Mapped[CardMetadata | None] = relationship(
        back_populates="asset", cascade="all, delete-orphan", uselist=False
    )
    raw_card_details: Mapped[RawCardDetails | None] = relationship(
        back_populates="asset", cascade="all, delete-orphan", uselist=False
    )
    graded_card_details: Mapped[GradedCardDetails | None] = relationship(
        back_populates="asset", cascade="all, delete-orphan", uselist=False
    )
    sealed_product_metadata: Mapped[SealedProductMetadata | None] = relationship(
        back_populates="asset", cascade="all, delete-orphan", uselist=False
    )
    purchase_lots: Mapped[list[PurchaseLot]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )
    images: Mapped[list[AssetImage]] = relationship(
        back_populates="asset",
        cascade="all, delete-orphan",
        order_by="AssetImage.id",
    )
    price_snapshots: Mapped[list[PriceSnapshot]] = relationship(
        back_populates="asset", cascade="all, delete-orphan"
    )


class CardMetadata(Base):
    __tablename__ = "card_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    external_source: Mapped[ExternalSource] = mapped_column(
        SqlEnum(
            ExternalSource,
            name="external_source",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        default=ExternalSource.MANUAL,
        nullable=False,
    )
    external_id: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_id: Mapped[str | None] = mapped_column(String(100))
    year: Mapped[int | None] = mapped_column(Integer)
    card_number: Mapped[str] = mapped_column(String(50), nullable=False)
    set_total: Mapped[str | None] = mapped_column(String(50))
    rarity: Mapped[str | None] = mapped_column(String(100))
    variant: Mapped[str | None] = mapped_column(String(100))
    image_url: Mapped[str | None] = mapped_column(Text)

    asset: Mapped[Asset] = relationship(back_populates="card_metadata")


class RawCardDetails(Base):
    __tablename__ = "raw_card_details"

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True
    )
    condition: Mapped[RawCardCondition] = mapped_column(
        SqlEnum(
            RawCardCondition,
            name="raw_card_condition",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )

    asset: Mapped[Asset] = relationship(back_populates="raw_card_details")


class GradedCardDetails(Base):
    __tablename__ = "graded_card_details"
    __table_args__ = (
        CheckConstraint("grade > 0 AND grade <= 10", name="valid_grade"),
    )

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), primary_key=True
    )
    grading_company: Mapped[GradingCompany] = mapped_column(
        SqlEnum(
            GradingCompany,
            name="grading_company",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    grade: Mapped[Decimal] = mapped_column(Numeric(3, 1), nullable=False)
    cert_number: Mapped[str | None] = mapped_column(String(100))

    asset: Mapped[Asset] = relationship(back_populates="graded_card_details")


class SealedProductMetadata(Base):
    __tablename__ = "sealed_product_metadata"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    set_name: Mapped[str | None] = mapped_column(String(255))
    year: Mapped[int | None] = mapped_column(Integer)
    sealed_product_type: Mapped[SealedProductType] = mapped_column(
        SqlEnum(
            SealedProductType,
            name="sealed_product_type",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    is_pokemon_center_exclusive: Mapped[bool | None] = mapped_column(Boolean)
    external_source: Mapped[ExternalSource | None] = mapped_column(
        SqlEnum(
            ExternalSource,
            name="sealed_external_source",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        )
    )
    external_id: Mapped[str | None] = mapped_column(String(255))
    image_url: Mapped[str | None] = mapped_column(Text)

    asset: Mapped[Asset] = relationship(back_populates="sealed_product_metadata")


class PurchaseLot(Base):
    __tablename__ = "purchase_lots"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="positive_purchase_quantity"),
        CheckConstraint(
            "purchase_price_per_unit >= 0", name="nonnegative_purchase_price"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    purchase_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    purchase_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="CAD", server_default="CAD", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    asset: Mapped[Asset] = relationship(back_populates="purchase_lots")


class AssetImage(Base):
    __tablename__ = "asset_images"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    image_type: Mapped[ImageType] = mapped_column(
        SqlEnum(
            ImageType,
            name="image_type",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        nullable=False,
    )
    url_or_path: Mapped[str] = mapped_column(Text, nullable=False)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    asset: Mapped[Asset] = relationship(back_populates="images")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    __table_args__ = (
        CheckConstraint(
            "market_price_per_unit >= 0", name="nonnegative_market_price"
        ),
        CheckConstraint(
            "confidence IS NULL OR (confidence >= 0 AND confidence <= 1)",
            name="valid_price_confidence",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    market_price_per_unit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(
        String(3), default="CAD", server_default="CAD", nullable=False
    )
    source: Mapped[PriceSource] = mapped_column(
        SqlEnum(
            PriceSource,
            name="price_source",
            native_enum=False,
            create_constraint=True,
            values_callable=enum_values,
        ),
        default=PriceSource.MANUAL,
        nullable=False,
    )
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(4, 3))
    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False, index=True
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    asset: Mapped[Asset] = relationship(back_populates="price_snapshots")
