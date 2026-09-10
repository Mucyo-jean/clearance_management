"""Fee payments.

Payments hang off the student rather than off a clearance request, because a
fee balance outlives any single application.

Every row carries `is_simulated`. This project performs no real financial
transaction, and the flag is what keeps that distinction visible in the data
itself rather than only in the documentation.
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import PaymentStatus

if TYPE_CHECKING:
    from app.models.student import Student


class Payment(Base, TimestampMixin):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_payment_amount_positive"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Numeric, never float: binary floating point cannot represent 0.10
    # exactly, and money must not drift.
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="RWF", nullable=False)

    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )
    method: Mapped[str | None] = mapped_column(String(64))
    reference: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    # DEMONSTRATION FLAG. True for every record this system creates.
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment {self.reference} {self.status.value}>"
