# ============================================================
# utils/password.py — Password hashing utilities
#
# Uses bcrypt directly (passlib is broken on Python 3.12+).
# bcrypt is slow BY DESIGN — that's what makes it secure.
# ============================================================

import bcrypt


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    bcrypt automatically generates a random salt and embeds it
    in the output, so the same password hashes differently each time.

    Returns a string like "$2b$12$..." safe to store in MongoDB.
    """
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a stored bcrypt hash.

    bcrypt.checkpw() is timing-safe — always takes the same time
    regardless of where the mismatch occurs (prevents timing attacks).

    Returns True if password matches, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )
