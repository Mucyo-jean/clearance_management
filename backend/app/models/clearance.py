"""The clearance spine: ClearanceRequest and ClearanceTask.

Two business rules are enforced here at database level, not only in Python:

  R1  a student may hold only one active request  -> partial unique index
  R5  a rejection must carry a reason             -> CHECK constraint

Application checks guard the HTTP boundary; these guard the data against a
seed script, a migration, or a psql session that never goes through the API.
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin
from app.models.enums import ClearanceReason, ClearanceStatus, TaskStatus

if TYPE_CHECKING:
    from app.models.certificate import Certificate
    from app.models.department import Department
    from app.models.document import Document
    from app.models.officer import Officer
    from app.models.student import Student

MIN_REJECTION_REASON_LENGTH = 10


class ClearanceRequest(Base, TimestampMixin):
    __tablename__ = "clearance_requests"
    __table_args__ = (
        # Rule R1. A partial unique index permits many historical rows per
        # student but at most one whose status is still open. An application
        # check alone loses to a double-submitted form; this does not.
        Index(
            "uq_one_active_request_per_student",
            "student_id",
            unique=True,
            postgresql_where=text(
                "status IN ('PENDING', 'IN_PROGRESS', 'REQUIRES_ATTENTION')"
            ),
        ),
        Index("ix_clearance_requests_student_status", "student_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(
        BigInteger,
        # RESTRICT, not CASCADE: a cleared student's record must survive.
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )

    reference_number: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, nullable=False
    )
    status: Mapped[ClearanceStatus] = mapped_column(
        Enum(ClearanceStatus, name="clearance_status"),
        default=ClearanceStatus.PENDING,
        nullable=False,
    )
    reason: Mapped[ClearanceReason] = mapped_column(
        Enum(ClearanceReason, name="clearance_reason"), nullable=False
    )
    academic_year: Mapped[str] = mapped_column(String(9), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()"), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    student: Mapped["Student"] = relationship(back_populates="clearance_requests")
    tasks: Mapped[list["ClearanceTask"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="ClearanceTask.id",
    )
    documents: Mapped[list["Document"]] = relationship(
        back_populates="request", cascade="all, delete-orphan"
    )
    certificate: Mapped["Certificate | None"] = relationship(
        back_populates="request", uselist=False, cascade="all, delete-orphan"
    )

    @property
    def is_active(self) -> bool:
        return self.status.value in ClearanceStatus.active_values()

    def __repr__(self) -> str:
        return f"<ClearanceRequest {self.reference_number} {self.status.value}>"


class ClearanceTask(Base, TimestampMixin):
    __tablename__ = "clearance_tasks"
    __table_args__ = (
        # One task per department per request.
        UniqueConstraint("request_id", "department_id", name="uq_task_request_department"),
        # Rule R5, at database level.
        CheckConstraint(
            "status <> 'REJECTED' OR "
            "(rejection_reason IS NOT NULL AND "
            f"char_length(btrim(rejection_reason)) >= {MIN_REJECTION_REASON_LENGTH})",
            name="ck_rejection_requires_reason",
        ),
        # The officer queue query: "my departments, still pending".
        Index("ix_clearance_tasks_department_status", "department_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger,
        # CASCADE here is correct: a task has no meaning without its request.
        ForeignKey("clearance_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    department_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("departments.id", ondelete="RESTRICT"), nullable=False
    )

    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"), default=TaskStatus.PENDING, nullable=False
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)

    # Null until a decision is made — that nullness is what distinguishes an
    # undecided task from a decided one.
    reviewed_by_officer_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("officers.id", ondelete="SET NULL")
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    request: Mapped["ClearanceRequest"] = relationship(back_populates="tasks")
    department: Mapped["Department"] = relationship(back_populates="tasks", lazy="joined")
    reviewed_by: Mapped["Officer | None"] = relationship(back_populates="reviewed_tasks")

    @property
    def is_decided(self) -> bool:
        return self.status is not TaskStatus.PENDING

    def __repr__(self) -> str:
        return f"<ClearanceTask req={self.request_id} dept={self.department_id} {self.status.value}>"
