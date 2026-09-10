"""Declarative base and shared column mixins."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """All models inherit from this. Alembic reads Base.metadata."""


class TimestampMixin:
    """created_at / updated_at, maintained by the database itself.

    Timezone-aware throughout (TIMESTAMPTZ), so a deployment in a different
    timezone from the demo machine cannot silently shift recorded times.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
