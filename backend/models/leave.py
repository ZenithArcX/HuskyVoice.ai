# ============================================================
# models/leave.py — Pydantic schemas for Leave-related requests
# ============================================================

from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional
from datetime import date


class LeaveApply(BaseModel):
    """
    Schema for POST /api/leave/apply request body.

    An employee submits this when requesting a leave.
    Validates that all fields are present, dates are valid,
    and end_date is not before start_date.
    """

    # Literal restricts to exactly these strings.
    # The frontend dropdown should send one of these exact values.
    leave_type: Literal[
        "Casual Leave",
        "Sick Leave",
        "Paid Leave",
        "Unpaid Leave",
        "Emergency Leave"
    ] = Field(..., example="Sick Leave")

    # Pydantic's 'date' type automatically parses "2026-03-15"
    # → Python date(2026, 3, 15). Invalid dates cause 422.
    start_date: date = Field(..., example="2026-03-15")
    end_date: date = Field(..., example="2026-03-17")

    # Reason must be at least 10 chars — prevents "ok" or "idk" submissions
    reason: str = Field(
        ...,
        min_length=10,
        max_length=500,
        example="Suffering from fever and doctor has advised rest for 3 days"
    )

    @field_validator("start_date")
    @classmethod
    def start_date_must_not_be_past(cls, start_date: date) -> date:
        """
        Prevent applying for leave on a past date.

        Employees should apply before or on the day of leave.
        date.today() gives today's date in local time.
        """
        if start_date < date.today():
            raise ValueError("Start date cannot be in the past")
        return start_date

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_after_start(cls, end_date: date, info) -> date:
        """
        Ensure the leave end date is on or after the start date.

        'info.data' contains already-validated fields.
        We check start_date was already validated (it's in info.data)
        before comparing — if start_date validation failed,
        info.data won't have it and we skip this check.
        """
        start = info.data.get("start_date")
        if start and end_date < start:
            raise ValueError("End date must be on or after start date")
        return end_date

    @field_validator("reason")
    @classmethod
    def reason_must_not_be_placeholder(cls, reason: str) -> str:
        """
        Block placeholder reasons like 'NA', 'test', '-'.

        Strips whitespace first, then checks against a banned list.
        Returns the cleaned (stripped) reason string.
        """
        cleaned = reason.strip()
        banned = {"n/a", "na", "none", "test", "-", "nil", "no reason"}
        if cleaned.lower() in banned:
            raise ValueError("Please provide a meaningful reason for the leave")
        return cleaned


class LeaveStatusUpdate(BaseModel):
    """
    Schema for PATCH /api/leave/{id}/status request body.

    Employers send this to approve or reject a leave application.
    Only 'Approved' or 'Rejected' are valid values.
    """

    # Literal ensures only exact strings are accepted.
    # "approved" (lowercase) or "APPROVED" would fail — must match exactly.
    status: Literal["Approved", "Rejected"] = Field(..., example="Approved")

    # Optional note from employer (e.g., "Approved, enjoy your leave!")
    # Optional[str] = None means this field can be omitted entirely
    note: Optional[str] = Field(
        None,
        max_length=200,
        example="Approved. Please ensure handover before leaving."
    )


class LeaveResponse(BaseModel):
    """
    Schema for leave data returned in API responses.

    Maps database fields to the response shape the frontend expects.
    Dates are strings (ISO format) for easy JSON serialization.
    """
    id: str
    user_id: str
    user_name: str
    user_email: str
    leave_type: str
    start_date: str
    end_date: str
    reason: str
    status: str
    note: Optional[str] = None
    created_at: str
