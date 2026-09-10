"""Uploaded supporting documents."""

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.clearance import ClearanceRequest

MAX_DOCUMENT_BYTES = 5 * 1024 * 1024


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint(
            f"size_bytes > 0 AND size_bytes <= {MAX_DOCUMENT_BYTES}",
            name="ck_document_size",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    request_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("clearance_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The name the browser sent. Shown to humans, never used to build a path:
    # a filename such as "../../app/main.py" would otherwise escape the
    # upload directory.
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)

    # The name actually written to disk: a generated UUID plus a validated
    # extension. Unguessable, collision-free, and safe to join to a path.
    stored_filename: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False
    )

    mime_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    request: Mapped["ClearanceRequest"] = relationship(back_populates="documents")

    def __repr__(self) -> str:
        return f"<Document {self.original_filename}>"
