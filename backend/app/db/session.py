"""Configure the SQLAlchemy engine, session factory, and FastAPI DB dependency."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings


connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

# SQLite needs same-thread checks disabled because FastAPI may move synchronous
# dependency work between threads. Other database engines need no special options.
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a request-scoped database session and always close it afterward."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
