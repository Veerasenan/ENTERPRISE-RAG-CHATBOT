"""
SQLAlchemy engine, session factory, and declarative Base for PostgreSQL.
This is the identity/roles database — separate from ChromaDB (which stores vectors).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create all tables if they don't exist.
    For real production use, prefer Alembic migrations instead of create_all —
    this is provided for fast local bootstrap only.
    """
    from app.models import user  # noqa: F401  (ensure models are registered)
    Base.metadata.create_all(bind=engine)
