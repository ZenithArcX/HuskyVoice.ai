# ============================================================
# routes/auth.py — Authentication endpoints
#
# POST /api/auth/register → create a new user
# POST /api/auth/login    → verify credentials, return JWT
# ============================================================

from fastapi import APIRouter, HTTPException, status
from datetime import datetime, timezone

from models.user import UserRegister, UserLogin, UserResponse
from middleware.auth import create_access_token
from utils.password import hash_password, verify_password
from database import get_db

# APIRouter groups related endpoints.
# In main.py we do: app.include_router(auth_router, prefix="/api/auth")
# So every route here gets the /api/auth prefix automatically.
router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,  # 201 = resource created (not just 200)
    summary="Register a new user (employee or employer)"
)
async def register(user: UserRegister):
    """
    Create a new user account.

    Steps:
    1. Pydantic auto-validates the request body via UserRegister schema
    2. Check if email is already taken (prevent duplicates)
    3. Hash the password with bcrypt (NEVER store plain text)
    4. Insert user document into MongoDB 'users' collection
    5. Return success message with the new user's ID

    Error cases:
    - 409 Conflict → email already exists
    - 422 Unprocessable → Pydantic validation failed (missing fields, etc.)
    """
    db = get_db()

    # Check if a user with this email already exists.
    # find_one returns the document if found, or None if not.
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )

    # Build the document to insert.
    # IMPORTANT: store the hashed password, NOT user.password (plain text)
    user_doc = {
        "name": user.name,
        "email": user.email,             # already normalized to lowercase by validator
        "password": hash_password(user.password),  # bcrypt hash
        "role": user.role,
        "created_at": datetime.now(timezone.utc)   # UTC timestamp
    }

    # insert_one returns an InsertOneResult with the new document's _id
    result = await db["users"].insert_one(user_doc)

    return {
        "message": "Registration successful",
        "id": str(result.inserted_id)   # ObjectId → string for JSON
    }


@router.post(
    "/login",
    summary="Login and receive a JWT access token"
)
async def login(credentials: UserLogin):
    """
    Verify user credentials and return a JWT token.

    Steps:
    1. Find user by email in MongoDB
    2. Verify the submitted password against the stored bcrypt hash
    3. If valid, create a JWT containing the user's id, email, name, role
    4. Return the JWT and basic user info to the frontend

    Security notes:
    - We return the SAME error message whether email or password is wrong.
      This prevents email enumeration (attacker can't tell if email exists).
    - Password verification is timing-safe (Passlib handles this).

    Error cases:
    - 401 Unauthorized → email not found OR wrong password (same message)
    """
    db = get_db()

    # Look up the user by email
    db_user = await db["users"].find_one({"email": credentials.email})

    # SECURITY: Use the same error for "email not found" AND "wrong password"
    # This prevents an attacker from discovering which emails are registered
    if not db_user or not verify_password(credentials.password, db_user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}   # HTTP spec requirement for 401
        )

    # Build the JWT payload.
    # 'sub' (subject) is the standard JWT claim for the user identifier.
    # We use the MongoDB _id as it's guaranteed unique.
    token_payload = {
        "sub": str(db_user["_id"]),    # user's MongoDB ID
        "email": db_user["email"],
        "name": db_user["name"],
        "role": db_user["role"]
        # 'exp' (expiry) is added automatically in create_access_token()
    }

    access_token = create_access_token(token_payload)

    # Return the token AND a basic user object.
    # The frontend saves both: token → localStorage, user → Pinia store
    return {
        "access_token": access_token,
        "token_type": "bearer",        # standard OAuth2 token type
        "user": {
            "id": str(db_user["_id"]),
            "name": db_user["name"],
            "email": db_user["email"],
            "role": db_user["role"]
        }
    }
