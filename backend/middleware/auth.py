# ============================================================
# middleware/auth.py — JWT creation and verification
#
# Every protected route uses Depends() to call get_current_user().
# This file is the single source of truth for auth logic.
# ============================================================

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os

load_dotenv()

# ── Config from .env ──────────────────────────────────────────
SECRET_KEY = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"  # HMAC-SHA256 — standard for JWT
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

# ── OAuth2PasswordBearer ──────────────────────────────────────
# This tells FastAPI where to expect the token.
# When a request hits a protected route, FastAPI reads the
# "Authorization: Bearer <token>" header using this scheme.
# tokenUrl is the login endpoint (shown in Swagger UI's Authorize button)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def create_access_token(data: dict) -> str:
    """
    Create a signed JWT token containing user data.

    Steps:
    1. Copy the payload dict to avoid mutating the original
    2. Add 'exp' (expiry) timestamp to the payload
    3. Encode + sign with SECRET_KEY using HMAC-SHA256
    4. Return the token string (3 base64url parts separated by '.')

    The payload typically contains:
        sub   → user's MongoDB _id (the "subject" standard claim)
        email → user's email address
        name  → user's display name
        role  → "employee" or "employer"
        exp   → Unix timestamp when this token expires

    Args:
        data: dict of claims to embed in the token

    Returns:
        Encoded JWT string like "eyJhbGci..."
    """
    payload = data.copy()

    # Set expiry time: current UTC time + configured minutes
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload["exp"] = expire

    # jwt.encode signs the payload with our SECRET_KEY
    # If SECRET_KEY leaks, attackers can forge tokens — keep it secret!
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Verify the JWT token and return the decoded user payload.

    This is a FastAPI DEPENDENCY — routes use it like:
        @router.get("/protected")
        async def protected_route(user = Depends(get_current_user)):
            ...

    FastAPI automatically:
    1. Extracts the Bearer token from the Authorization header
    2. Passes it to this function
    3. Injects the return value into the route handler

    What happens here:
    - If token is missing → OAuth2PasswordBearer raises 401 automatically
    - If token signature is invalid → JWTError → we raise 401
    - If token is expired → ExpiredSignatureError (subclass of JWTError) → 401
    - If 'sub' claim is missing → we raise 401
    - If all good → return the decoded payload dict

    Args:
        token: JWT string extracted from Authorization header

    Returns:
        dict with keys: sub, email, name, role, exp

    Raises:
        HTTPException 401 if token is invalid or expired
    """
    # Pre-define the exception to raise if anything fails.
    # WWW-Authenticate header tells the client it needs a Bearer token.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode and verify the token. jose checks:
        # - signature validity (was it signed with OUR secret key?)
        # - expiry (has the 'exp' timestamp passed?)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 'sub' is the standard JWT claim for the subject (our user's ID)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        return payload  # Return the full payload dict to the route

    except JWTError:
        # Catches: ExpiredSignatureError, InvalidSignatureError, etc.
        raise credentials_exception


async def require_employer(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that ONLY allows employer-role users.

    Chains on top of get_current_user:
    1. get_current_user runs first (validates JWT)
    2. Then this function checks the role

    Usage in routes:
        @router.get("/all")
        async def all_leaves(user = Depends(require_employer)):
            ...  # only employers reach this code

    Raises:
        HTTPException 403 if the authenticated user is not an employer
        (403 = "I know who you are, but you're not allowed")
    """
    if user.get("role") != "employer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to employer accounts only"
        )
    return user


async def require_employee(user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency that ONLY allows employee-role users.

    Same pattern as require_employer but checks for 'employee' role.
    Prevents employers from accidentally applying for leave.
    """
    if user.get("role") != "employee":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to employee accounts only"
        )
    return user
