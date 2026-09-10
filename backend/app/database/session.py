"""Database engine and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # verify a connection is alive before using it
    echo=False,           # set True to watch the SQL SQLAlchemy generates
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed.

    Services own transactions — they call commit(). This dependency only
    guarantees the session is released back to the pool afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
