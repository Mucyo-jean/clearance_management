"""Student profile."""

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.clearance import ClearanceRequest
    from app.models.payment import Payment
    from app.models.user import User

# Fields that must be filled before a clearance request may be submitted.
# Business rule R2 reads this list so the error message can name exactly
# which fields are missing rather than saying "profile incomplete".
REQUIRED_PROFILE_FIELDS: tuple[str, ...] = (
    "registration_number",
    "programme",
    "faculty",
    "year_of_study",
)


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,          # enforces the 1:1 with users
        nullable=False,
    )

    registration_number: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    programme: Mapped[str | None] = mapped_column(String(160))
    faculty: Mapped[str | None] = mapped_column(String(160))
    year_of_study: Mapped[int | None] = mapped_column(Integer)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    address: Mapped[str | None] = mapped_column(String(255))

    user: Mapped["User"] = relationship(back_populates="student", lazy="joined")
    clearance_requests: Mapped[list["ClearanceRequest"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    def missing_profile_fields(self) -> list[str]:
        """Return the required fields that are still empty (rule R2)."""
        return [f for f in REQUIRED_PROFILE_FIELDS if not getattr(self, f, None)]

    @property
    def is_profile_complete(self) -> bool:
        return not self.missing_profile_fields()

    def __repr__(self) -> str:
        return f"<Student {self.registration_number}>"
