"""Password hashing.

JWT creation and decoding join this module in the authentication step; for
now it holds only what the seed script and the auth service both need.

Passwords are stored as bcrypt hashes and never in any reversible form, so
even someone holding a dump of the database cannot recover them.
"""

from passlib.context import CryptContext

# cost=12 is the NFR-03 target: slow enough to make offline guessing
# expensive, fast enough that a login still feels instant.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)

# bcrypt hashes only the first 72 bytes of input and silently ignores the
# rest, which would make two long passwords sharing a prefix equivalent.
# Rejecting them outright is safer than truncating.
BCRYPT_MAX_BYTES = 72


class PasswordTooLongError(ValueError):
    """Raised when a password exceeds what bcrypt can actually hash."""


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given password."""
    if len(plain_password.encode("utf-8")) > BCRYPT_MAX_BYTES:
        raise PasswordTooLongError(
            f"Password must be at most {BCRYPT_MAX_BYTES} bytes when UTF-8 encoded"
        )
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a password against a stored hash.

    Returns False rather than raising on a malformed hash, so a corrupted
    row cannot turn a failed login into a 500.
    """
    try:
        return pwd_context.verify(plain_password, password_hash)
    except (ValueError, TypeError):
        return False
