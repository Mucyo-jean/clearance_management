"""Digital clearance certificate.

The snapshot columns are a deliberate departure from normalisation, and the
reason is worth stating in the defence: a certificate is a historical
assertion that a named person was cleared on a given date. If it read the
student's name by join at print time, a later profile edit would silently
rewrite an already-issued document. Copying the values in freezes them.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.clearance import ClearanceRequest


class Certificate(Base):
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clearance_requests.id", ondelete="CASCADE"),
        unique=True,          # one certificate per request (rule R7)
        nullable=False,
    )

    # Random, never sequential. A guessable code would not be a check at all.
    verification_code: Mapped[str] = mapped_column(
        String(24), unique=True, index=True, nullable=False
    )

    # ---- Frozen at issue time ----
    student_name_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    registration_number_snapshot: Mapped[str] = mapped_column(String(32), nullable=False)
    programme_snapshot: Mapped[str | None] = mapped_column(String(160))
    faculty_snapshot: Mapped[str | None] = mapped_column(String(160))
    academic_year_snapshot: Mapped[str] = mapped_column(String(9), nullable=False)

    # Comma-separated department names cleared, frozen at issue time so the
    # certificate stays truthful if a department is later renamed.
    departments_snapshot: Mapped[str] = mapped_column(Text, nullable=False)

    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    request: Mapped["ClearanceRequest"] = relationship(back_populates="certificate")

    def __repr__(self) -> str:
        return f"<Certificate {self.verification_code}>"
