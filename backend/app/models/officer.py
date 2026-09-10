"""Department officer profile."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.department import officer_departments

if TYPE_CHECKING:
    from app.models.clearance import ClearanceTask
    from app.models.department import Department
    from app.models.user import User


class Officer(Base, TimestampMixin):
    __tablename__ = "officers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,          # enforces the 1:1 with users
        nullable=False,
    )
    staff_number: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    job_title: Mapped[str | None] = mapped_column(String(120))

    user: Mapped["User"] = relationship(back_populates="officer", lazy="joined")
    departments: Mapped[list["Department"]] = relationship(
        secondary=officer_departments, back_populates="officers", lazy="selectin"
    )
    reviewed_tasks: Mapped[list["ClearanceTask"]] = relationship(
        back_populates="reviewed_by"
    )

    @property
    def department_ids(self) -> set[int]:
        """The departments this officer may act on — the basis of rule R4."""
        return {d.id for d in self.departments}

    def can_act_on(self, department_id: int) -> bool:
        return department_id in self.department_ids

    def __repr__(self) -> str:
        return f"<Officer {self.staff_number}>"
