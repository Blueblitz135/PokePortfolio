"""Command-line helper that creates all tables registered on SQLAlchemy metadata."""

from app import models  # noqa: F401

from app.db.base import Base
from app.db.session import engine


def create_tables() -> None:
    """Create missing database tables without altering existing tables."""

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
