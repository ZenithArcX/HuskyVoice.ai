# ============================================================
# routes/leave.py — Leave management endpoints
#
# POST   /api/leave/apply          → employee applies for leave
# GET    /api/leave/my             → employee views own leaves
# GET    /api/leave/all            → employer views all leaves
# PATCH  /api/leave/{id}/status   → employer approves/rejects
# ============================================================

from fastapi import APIRouter, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

from models.leave import LeaveApply, LeaveStatusUpdate
from middleware.auth import get_current_user, require_employer, require_employee
from database import get_db
from fastapi import Depends

router = APIRouter()


def serialize_leave(doc: dict) -> dict:
    """
    Convert a MongoDB leave document into a JSON-serializable dict.

    MongoDB stores '_id' as an ObjectId type, which JSON can't serialize.
    We convert it to a string and rename it to 'id' (frontend-friendly).
    Dates are converted to ISO format strings.

    Args:
        doc: Raw MongoDB document dict

    Returns:
        Clean dict safe to return as JSON response
    """
    return {
        "id": str(doc["_id"]),
        "user_id": doc.get("user_id", ""),
        "user_name": doc.get("user_name", ""),
        "user_email": doc.get("user_email", ""),
        "leave_type": doc.get("leave_type", ""),
        "start_date": doc.get("start_date", ""),
        "end_date": doc.get("end_date", ""),
        "reason": doc.get("reason", ""),
        "status": doc.get("status", "Pending"),
        "note": doc.get("note"),
        "created_at": doc["created_at"].isoformat() if isinstance(doc.get("created_at"), datetime) else str(doc.get("created_at", ""))
    }


@router.post(
    "/apply",
    status_code=status.HTTP_201_CREATED,
    summary="Employee applies for leave"
)
async def apply_leave(
    data: LeaveApply,                                   # request body, Pydantic validated
    current_user: dict = Depends(require_employee)      # JWT auth + employee-only guard
):
    """
    Submit a new leave application.

    Depends(require_employee) does two things automatically:
    1. Validates the JWT Bearer token (returns 401 if invalid/missing)
    2. Checks role == "employee" (returns 403 if employer tries this)

    The leave is stored with:
    - user_id, user_name, user_email from the JWT payload
    - leave details from the request body
    - status = "Pending" (always starts as pending)
    - created_at = current UTC timestamp

    Error cases:
    - 401 → missing/invalid JWT
    - 403 → user is an employer, not an employee
    - 422 → Pydantic validation failed (missing fields, bad dates, etc.)
    """
    db = get_db()

    # Build the document to insert into 'leaves' collection
    leave_doc = {
        # Who is applying? — taken from the decoded JWT payload
        "user_id": current_user["sub"],
        "user_name": current_user["name"],
        "user_email": current_user["email"],

        # What kind of leave? — from the validated request body
        "leave_type": data.leave_type,

        # Dates stored as ISO format strings for easy sorting and display
        "start_date": data.start_date.isoformat(),   # "2026-03-15"
        "end_date": data.end_date.isoformat(),

        "reason": data.reason,

        # New applications always start as "Pending"
        # Employers change this via PATCH /{id}/status
        "status": "Pending",

        "note": None,  # employer note — filled when approved/rejected

        # Timestamp for sorting (newest first)
        "created_at": datetime.now(timezone.utc)
    }

    result = await db["leaves"].insert_one(leave_doc)

    return {
        "message": "Leave application submitted successfully",
        "id": str(result.inserted_id)
    }


@router.get(
    "/my",
    summary="Employee views their own leave applications"
)
async def get_my_leaves(
    current_user: dict = Depends(get_current_user)  # any logged-in user
):
    """
    Return all leave applications belonging to the currently logged-in employee.

    Uses current_user["sub"] (the user's MongoDB _id stored in JWT)
    to filter only that user's leaves.

    Leaves are sorted newest-first (-1 = descending order).

    Error cases:
    - 401 → missing/invalid JWT
    """
    db = get_db()

    # find() returns a cursor (like a lazy list), not actual data.
    # .sort("created_at", -1) = newest first (-1 = descending)
    cursor = db["leaves"].find(
        {"user_id": current_user["sub"]}   # only this user's leaves
    ).sort("created_at", -1)

    # to_list(None) fetches ALL matching documents (no limit).
    # Use a number like to_list(100) to limit results for large datasets.
    leaves = await cursor.to_list(None)

    # Serialize each document for JSON response
    return [serialize_leave(leave) for leave in leaves]


@router.get(
    "/all",
    summary="Employer views all employee leave applications"
)
async def get_all_leaves(
    current_user: dict = Depends(require_employer)  # employer-only
):
    """
    Return ALL leave applications across all employees.

    Only accessible to employer accounts (require_employer dependency
    automatically returns 403 for employees).

    Sorted newest-first so urgent/latest requests appear at top.

    Error cases:
    - 401 → not logged in
    - 403 → logged in but not an employer
    """
    db = get_db()

    # {} = no filter = match ALL documents in the collection
    cursor = db["leaves"].find({}).sort("created_at", -1)
    leaves = await cursor.to_list(None)

    return [serialize_leave(leave) for leave in leaves]


@router.patch(
    "/{leave_id}/status",
    summary="Employer approves or rejects a leave application"
)
async def update_leave_status(
    leave_id: str,                                     # from URL path e.g. /abc123/status
    data: LeaveStatusUpdate,                           # body: { "status": "Approved", "note": "..." }
    current_user: dict = Depends(require_employer)     # employer-only
):
    """
    Update the status of a leave application (Approved or Rejected).

    Steps:
    1. Validate leave_id is a valid MongoDB ObjectId format
    2. Update the document's status field in MongoDB
    3. Also store: who reviewed it, when, and any optional note
    4. Return 404 if the leave_id doesn't exist

    '$set' operator in MongoDB updates ONLY the specified fields.
    Other fields (user_name, leave_type, etc.) remain unchanged.

    Error cases:
    - 400 → invalid leave_id format (not a valid ObjectId)
    - 401 → not logged in
    - 403 → not an employer
    - 404 → leave with this ID not found
    """
    db = get_db()

    # Validate that leave_id is a valid ObjectId before querying
    # An invalid format would cause a server error (500) if not caught
    try:
        object_id = ObjectId(leave_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )

    # Update only the status-related fields using $set operator.
    # $set means: update ONLY these fields. Without $set, the entire
    # document would be replaced with just these fields (destructive!).
    result = await db["leaves"].update_one(
        {"_id": object_id},   # find the document by its _id
        {
            "$set": {
                "status": data.status,
                "note": data.note,
                "reviewed_by": current_user["email"],   # who approved/rejected
                "reviewed_at": datetime.now(timezone.utc)   # when
            }
        }
    )

    # modified_count = 0 means no document matched the filter
    # This happens when the leave_id doesn't exist in the database
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )

    return {
        "message": f"Leave application {data.status.lower()} successfully"
    }


@router.delete(
    "/{leave_id}",
    summary="Employee cancels their own pending leave"
)
async def cancel_leave(
    leave_id: str,
    current_user: dict = Depends(require_employee)
):
    """
    Cancel a pending leave application.

    Only the employee who submitted the leave can cancel it,
    and only while the status is still 'Pending'.

    Error cases:
    - 400 → invalid leave ID format
    - 403 → trying to cancel someone else's leave
    - 409 → leave is already Approved or Rejected (can't cancel)
    - 404 → leave not found
    """
    db = get_db()

    try:
        object_id = ObjectId(leave_id)
    except InvalidId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid leave ID format"
        )

    leave = await db["leaves"].find_one({"_id": object_id})

    if not leave:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Leave application not found"
        )

    if leave["user_id"] != current_user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own leave applications"
        )

    if leave["status"] != "Pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot cancel a leave that is already {leave['status']}"
        )

    await db["leaves"].delete_one({"_id": object_id})

    return {"message": "Leave application cancelled successfully"}
