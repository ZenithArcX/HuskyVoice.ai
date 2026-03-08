# ============================================================
# models/user.py — Pydantic schemas for User-related requests
#
# Pydantic models validate incoming request data AUTOMATICALLY.
# If a required field is missing or wrong type → FastAPI returns
# HTTP 422 without even running your route function.
# ============================================================

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
import re


class UserRegister(BaseModel):
    """
    Schema for POST /api/auth/register request body.

    All fields are required (no defaults = required in Pydantic).
    Pydantic validates types and constraints before route code runs.
    """

    # str — any text. Field() adds extra constraints beyond just type.
    # min_length=2 → rejects empty or single-character names
    # example= → shown in Swagger UI as the demo value
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Ravi Kumar"
    )

    # EmailStr — special Pydantic type that validates email format
    # Checks for "@" and a valid domain. "notanemail" → 422 error
    email: EmailStr = Field(..., example="ravi@example.com")

    # Password requires at least 8 characters (enforced by Field)
    # Additional complexity check is done in the @field_validator below
    password: str = Field(..., min_length=8, example="StrongPass@123")

    # Literal["a", "b"] — value MUST be one of these exact strings
    # Anything else (like "admin") → 422 error automatically
    role: Literal["employee", "employer"] = Field(..., example="employee")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, password: str) -> str:
        """
        Custom validator for password complexity.

        Runs AFTER the basic type check passes.
        Must contain: uppercase, lowercase, and a digit.
        Returns the password unchanged if valid, raises ValueError if not.
        ValueError gets converted to a 422 response by FastAPI.
        """
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
        return password

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        """
        Convert email to lowercase before saving.

        Prevents "Ravi@Email.com" and "ravi@email.com" being treated
        as different accounts. Consistency is important for lookups.
        """
        return email.lower().strip()


class UserLogin(BaseModel):
    """
    Schema for POST /api/auth/login request body.

    Minimal — just email and password.
    No role needed (we fetch it from the database).
    """
    email: EmailStr = Field(..., example="ravi@example.com")
    password: str = Field(..., example="StrongPass@123")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, email: str) -> str:
        """Normalize email to lowercase for consistent lookup."""
        return email.lower().strip()


class UserResponse(BaseModel):
    """
    Schema for user data returned in API responses.

    CRITICAL: 'password' is intentionally NOT included here.
    When FastAPI serializes a response using this model, the hashed
    password field is automatically stripped — it never reaches the client.
    """
    id: str
    name: str
    email: str
    role: str
