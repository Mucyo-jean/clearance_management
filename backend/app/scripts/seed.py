"""Seed the database with DEMONSTRATION data.

    py -m app.scripts.seed            # create anything missing
    py -m app.scripts.seed --reset    # delete seeded rows first, then create

Every account created here exists so the system can be demonstrated and
tested. They are not real people, and they must never be carried into a
production deployment.

What this script creates
------------------------
  3 roles         STUDENT, OFFICER, ADMIN
  4 departments   Library, Finance, Academic, ICT  (all required)
  1 administrator
  2 officers      covering two departments each, to exercise the
                  many-to-many officer/department relationship
  3 students      profiles complete, ready to submit a request

What it deliberately does NOT create
------------------------------------
Clearance requests. Creating one means fanning out a task per required
department, deriving the overall status, writing notifications and an audit
entry. That logic belongs to the clearance service, and seeding rows
directly would bypass it - producing data the application itself could never
have produced. Requests are created through the API instead.

The script is idempotent: running it twice creates nothing the second time.
"""

from __future__ import annotations

import argparse
import os
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.database.session import SessionLocal
from app.models import (
    Department,
    Officer,
    Role,
    RoleName,
    Student,
    User,
)

# Override with the SEED_PASSWORD environment variable. Shared by every
# demonstration account so the system is easy to walk through; this is
# acceptable precisely because these accounts are disposable.
DEFAULT_SEED_PASSWORD = "Clearance@2026"

DEPARTMENTS: list[dict] = [
    {
        "code": "LIB",
        "name": "Library",
        "description": "Confirms all borrowed books and materials are returned.",
        "sort_order": 1,
    },
    {
        "code": "FIN",
        "name": "Finance",
        "description": "Confirms tuition and other fees are fully settled.",
        "sort_order": 2,
    },
    {
        "code": "ACAD",
        "name": "Academic",
        "description": "Confirms academic records, results and thesis submission.",
        "sort_order": 3,
    },
    {
        "code": "ICT",
        "name": "ICT",
        "description": "Confirms return of loaned equipment and closure of accounts.",
        "sort_order": 4,
    },
]

ADMIN = {
    "email": "admin@ur.ac.rw",
    "full_name": "Registrar Administrator",
    "phone": "+250788000001",
}

OFFICERS: list[dict] = [
    {
        "email": "j.habimana@ur.ac.rw",
        "full_name": "Jean Habimana",
        "phone": "+250788000010",
        "staff_number": "UR-STF-0101",
        "job_title": "Senior Librarian",
        "departments": ["LIB", "ACAD"],
    },
    {
        "email": "a.uwase@ur.ac.rw",
        "full_name": "Alice Uwase",
        "phone": "+250788000011",
        "staff_number": "UR-STF-0102",
        "job_title": "Finance Officer",
        "departments": ["FIN", "ICT"],
    },
]

STUDENTS: list[dict] = [
    {
        "email": "k.mutesi@stud.ur.ac.rw",
        "full_name": "Claudine Mutesi",
        "phone": "+250788000020",
        "registration_number": "223014001",
        "programme": "BSc Software Engineering",
        "faculty": "Science and Technology",
        "year_of_study": 3,
    },
    {
        "email": "e.nkurunziza@stud.ur.ac.rw",
        "full_name": "Eric Nkurunziza",
        "phone": "+250788000021",
        "registration_number": "223014002",
        "programme": "BSc Information Systems",
        "faculty": "Science and Technology",
        "year_of_study": 4,
    },
    {
        "email": "s.ingabire@stud.ur.ac.rw",
        "full_name": "Sandrine Ingabire",
        "phone": "+250788000022",
        "registration_number": "223014003",
        "programme": "BSc Computer Science",
        "faculty": "Science and Technology",
        "year_of_study": 3,
    },
]


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _get_role(session: Session, name: RoleName) -> Role:
    role = session.scalar(select(Role).where(Role.name == name))
    if role is None:
        raise RuntimeError(f"Role {name.value} missing - seed roles first")
    return role


def _find_user(session: Session, email: str) -> User | None:
    return session.scalar(select(User).where(User.email == email))


def seed_roles(session: Session) -> int:
    created = 0
    descriptions = {
        RoleName.STUDENT: "Submits and tracks their own clearance request.",
        RoleName.OFFICER: "Reviews clearance tasks for assigned departments.",
        RoleName.ADMIN: "Configures the system and oversees all clearances.",
    }
    for name, description in descriptions.items():
        if session.scalar(select(Role).where(Role.name == name)) is None:
            session.add(Role(name=name, description=description))
            created += 1
    session.flush()
    return created


def seed_departments(session: Session) -> int:
    created = 0
    for spec in DEPARTMENTS:
        if session.scalar(select(Department).where(Department.code == spec["code"])) is None:
            session.add(
                Department(
                    code=spec["code"],
                    name=spec["name"],
                    description=spec["description"],
                    sort_order=spec["sort_order"],
                    is_required=True,
                    is_active=True,
                )
            )
            created += 1
    session.flush()
    return created


def seed_admin(session: Session, password: str) -> int:
    if _find_user(session, ADMIN["email"]) is not None:
        return 0
    session.add(
        User(
            email=ADMIN["email"],
            full_name=ADMIN["full_name"],
            phone=ADMIN["phone"],
            password_hash=hash_password(password),
            role_id=_get_role(session, RoleName.ADMIN).id,
            is_active=True,
        )
    )
    session.flush()
    return 1


def seed_officers(session: Session, password: str) -> int:
    created = 0
    role = _get_role(session, RoleName.OFFICER)
    by_code = {d.code: d for d in session.scalars(select(Department)).all()}

    for spec in OFFICERS:
        if _find_user(session, spec["email"]) is not None:
            continue
        user = User(
            email=spec["email"],
            full_name=spec["full_name"],
            phone=spec["phone"],
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
        )
        session.add(user)
        session.flush()

        officer = Officer(
            user_id=user.id,
            staff_number=spec["staff_number"],
            job_title=spec["job_title"],
        )
        officer.departments = [by_code[c] for c in spec["departments"] if c in by_code]
        session.add(officer)
        created += 1

    session.flush()
    return created


def seed_students(session: Session, password: str) -> int:
    created = 0
    role = _get_role(session, RoleName.STUDENT)

    for spec in STUDENTS:
        if _find_user(session, spec["email"]) is not None:
            continue
        user = User(
            email=spec["email"],
            full_name=spec["full_name"],
            phone=spec["phone"],
            password_hash=hash_password(password),
            role_id=role.id,
            is_active=True,
        )
        session.add(user)
        session.flush()

        session.add(
            Student(
                user_id=user.id,
                registration_number=spec["registration_number"],
                programme=spec["programme"],
                faculty=spec["faculty"],
                year_of_study=spec["year_of_study"],
            )
        )
        created += 1

    session.flush()
    return created


def reset(session: Session) -> None:
    """Delete only the rows this script creates, in foreign-key-safe order."""
    emails = [ADMIN["email"], *[o["email"] for o in OFFICERS], *[s["email"] for s in STUDENTS]]

    users = session.scalars(select(User).where(User.email.in_(emails))).all()
    for user in users:
        # Officer/Student rows cascade from User via the ORM relationship.
        session.delete(user)
    session.flush()

    for dept in session.scalars(
        select(Department).where(Department.code.in_([d["code"] for d in DEPARTMENTS]))
    ).all():
        if dept.tasks:
            print(f"  ! keeping department {dept.code}: it has clearance tasks attached")
            continue
        session.delete(dept)
    session.flush()
    print(f"  reset: removed {len(users)} demonstration user(s)")


# --------------------------------------------------------------------------
# entry point
# --------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="Seed demonstration data.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="delete previously seeded rows before creating them again",
    )
    args = parser.parse_args()

    password = os.getenv("SEED_PASSWORD", DEFAULT_SEED_PASSWORD)

    session = SessionLocal()
    try:
        if args.reset:
            print("Resetting demonstration data...")
            reset(session)

        print("Seeding...")
        counts = {
            "roles": seed_roles(session),
            "departments": seed_departments(session),
            "administrator": seed_admin(session, password),
            "officers": seed_officers(session, password),
            "students": seed_students(session, password),
        }
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    for label, n in counts.items():
        print(f"  {label:15} created {n}")
    if not any(counts.values()):
        print("  (nothing to do - the database was already seeded)")

    print()
    print("=" * 66)
    print("DEMONSTRATION ACCOUNTS - not real people, not for production use")
    print("=" * 66)
    print(f"  password for every account below: {password}")
    print()
    print(f"  ADMIN     {ADMIN['email']}")
    for spec in OFFICERS:
        print(f"  OFFICER   {spec['email']:32} {', '.join(spec['departments'])}")
    for spec in STUDENTS:
        print(f"  STUDENT   {spec['email']:32} {spec['registration_number']}")
    print("=" * 66)
    return 0


if __name__ == "__main__":
    sys.exit(main())
