"""Audit trail.

Insert-only by convention: no service updates or deletes these rows, and no
endpoint exposes a way to. An audit log that can be edited is not evidence.

Note the deliberate absence of TimestampMixin — an audit row is never
updated, so an `updated_at` column would be a lie. It carries its own
`created_at` instead.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.enums import AuditAction

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = (
        # Looking up "everything that happened to request #12".
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
    )
    # The admin log view is newest-first, served by the plain ascending index
    # on created_at below: PostgreSQL scans a btree backwards just as fast,
    # so a separate DESC index would cost writes and buy nothing.

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # Nullable: actions the system performs on its own have no human actor.
    # Those are attributed to SYSTEM in the description.
    actor_user_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction, name="audit_action"), nullable=False
    )
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(BigInteger)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    ip_address: Mapped[str | None] = mapped_column(String(45))  # 45 fits IPv6

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    actor: Mapped["User | None"] = relationship(back_populates="audit_logs")

    def __repr__(self) -> str:
        return f"<AuditLog {self.action.value} {self.entity_type}#{self.entity_id}>"
