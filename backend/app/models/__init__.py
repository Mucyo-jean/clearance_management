"""Model registry.

Importing every model here matters for two reasons:

1. SQLAlchemy resolves relationships by string name ("Student", "Department").
   Those names only exist once the module defining them has been imported.
2. Alembic autogenerate compares the database against Base.metadata, and a
   model that was never imported is absent from that metadata — so Alembic
   would silently generate a migration that drops its table.
"""

from app.database.base import Base
from app.models.audit import AuditLog
from app.models.certificate import Certificate
from app.models.clearance import ClearanceRequest, ClearanceTask
from app.models.department import Department, officer_departments
from app.models.document import Document
from app.models.enums import (
    AuditAction,
    ClearanceReason,
    ClearanceStatus,
    NotificationType,
    PaymentStatus,
    RoleName,
    TaskStatus,
)
from app.models.notification import Notification
from app.models.officer import Officer
from app.models.payment import Payment
from app.models.student import Student
from app.models.user import Role, User

__all__ = [
    "AuditAction",
    "AuditLog",
    "Base",
    "Certificate",
    "ClearanceReason",
    "ClearanceRequest",
    "ClearanceStatus",
    "ClearanceTask",
    "Department",
    "Document",
    "Notification",
    "NotificationType",
    "Officer",
    "Payment",
    "PaymentStatus",
    "Role",
    "RoleName",
    "Student",
    "TaskStatus",
    "User",
    "officer_departments",
]
