"""Provide the declarative base inherited by every SQLAlchemy model."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common SQLAlchemy metadata registry for the portfolio tables."""

    pass
