"""Departments and the officer-to-department assignment table.

Departments are configuration, not code. An administrator creates them and
decides which ones participate in clearance via `is_required`, which is what
keeps the system usable at an institution with a different set of offices.
"""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.clearance import ClearanceTask
    from app.models.officer import Officer


# Many-to-many: one officer may cover several offices, and an office has
# several officers. The composite primary key IS the fact being stored, so a
# surrogate id here would only permit meaningless duplicates.
officer_departments = Table(
    "officer_departments",
    Base.metadata,
    Column(
        "officer_id",
        BigInteger,
        ForeignKey("officers.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "department_id",
        BigInteger,
        ForeignKey("departments.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Department(Base, TimestampMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))

    # Required departments are the ones a new clearance request fans out to.
    is_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Soft delete. A hard delete would cascade into historical clearance tasks
    # and destroy the record of decisions already made.
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    officers: Mapped[list["Officer"]] = relationship(
        secondary=officer_departments, back_populates="departments"
    )
    tasks: Mapped[list["ClearanceTask"]] = relationship(back_populates="department")

    def __repr__(self) -> str:
        return f"<Department {self.code}>"
