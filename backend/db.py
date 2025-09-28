"""Database configuration and session management."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from settings import get_settings


def _format_database_url(raw_url: str) -> str:
    """Ensure the SQLAlchemy URL uses the psycopg driver when connecting to Postgres."""

    if raw_url.startswith("postgres://"):
        return raw_url.replace("postgres://", "postgresql+psycopg://", 1)
    if raw_url.startswith("postgresql://") and not raw_url.startswith("postgresql+psycopg://"):
        return raw_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw_url


settings = get_settings()
database_url = _format_database_url(settings.database_url)

engine = create_engine(database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Provide a SQLAlchemy session dependency."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Provide a transactional scope for scripts and utilities."""

    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

