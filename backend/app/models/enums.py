"""Enumerations shared across the models.

These become native PostgreSQL ENUM types. Storing status as an enum rather
than a free string means the database itself rejects a typo such as
'APROVED', which a VARCHAR column would happily accept.
"""

import enum


class RoleName(str, enum.Enum):
    STUDENT = "STUDENT"
    OFFICER = "OFFICER"
    ADMIN = "ADMIN"


class ClearanceStatus(str, enum.Enum):
    """Overall status of a request. Always derived, never set by hand."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    REQUIRES_ATTENTION = "REQUIRES_ATTENTION"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

    @classmethod
    def active_values(cls) -> tuple[str, ...]:
        """Statuses that count as an open request, for business rule R1."""
        return (cls.PENDING.value, cls.IN_PROGRESS.value, cls.REQUIRES_ATTENTION.value)


class TaskStatus(str, enum.Enum):
    """One department's decision on one request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ClearanceReason(str, enum.Enum):
    GRADUATION = "GRADUATION"
    WITHDRAWAL = "WITHDRAWAL"
    TRANSFER = "TRANSFER"
    SUSPENSION = "SUSPENSION"


class PaymentStatus(str, enum.Enum):
    REQUIRED = "REQUIRED"
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"


class NotificationType(str, enum.Enum):
    CLEARANCE_SUBMITTED = "CLEARANCE_SUBMITTED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_APPROVED = "TASK_APPROVED"
    TASK_REJECTED = "TASK_REJECTED"
    TASK_RESUBMITTED = "TASK_RESUBMITTED"
    PAYMENT_UPDATED = "PAYMENT_UPDATED"
    CLEARANCE_COMPLETED = "CLEARANCE_COMPLETED"
    DOCUMENT_ATTENTION = "DOCUMENT_ATTENTION"


class AuditAction(str, enum.Enum):
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    CLEARANCE_SUBMITTED = "CLEARANCE_SUBMITTED"
    CLEARANCE_STATUS_CHANGED = "CLEARANCE_STATUS_CHANGED"
    CLEARANCE_REOPENED = "CLEARANCE_REOPENED"
    TASK_APPROVED = "TASK_APPROVED"
    TASK_REJECTED = "TASK_REJECTED"
    TASK_RESUBMITTED = "TASK_RESUBMITTED"
    DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED"
    DOCUMENT_DELETED = "DOCUMENT_DELETED"
    PAYMENT_SIMULATED = "PAYMENT_SIMULATED"
    CERTIFICATE_GENERATED = "CERTIFICATE_GENERATED"
    DEPARTMENT_CREATED = "DEPARTMENT_CREATED"
    DEPARTMENT_UPDATED = "DEPARTMENT_UPDATED"
    OFFICER_ASSIGNED = "OFFICER_ASSIGNED"
    USER_STATUS_CHANGED = "USER_STATUS_CHANGED"
