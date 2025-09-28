"""Initialize database schema and seed baseline data."""
from __future__ import annotations

from sqlalchemy import select

from db import Base, engine, session_scope
from models import Partner

DEFAULT_PARTNERS = (
    ("Rafael", 0.5),
    ("Guilherme", 0.5),
)


def initialize() -> None:
    """Create tables and ensure default partners exist."""

    Base.metadata.create_all(engine)
    with session_scope() as session:
        existing = set(session.execute(select(Partner.name)).scalars())
        for name, ratio in DEFAULT_PARTNERS:
            if name in existing:
                continue
            session.add(Partner(name=name, split_ratio=ratio))

    print("Database initialized with default partners.")


if __name__ == "__main__":
    initialize()
