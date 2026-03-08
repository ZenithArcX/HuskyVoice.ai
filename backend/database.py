# ============================================================
# database.py — MongoDB Atlas connection management
# One connection pool shared across the entire application.
# ============================================================

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

# ── Read config from environment ──────────────────────────────
# MONGO_URI — the full Atlas connection string from .env
# DB_NAME   — which database to use (default: "leavedb")
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "leavedb")

# ── Global references ─────────────────────────────────────────
# These are module-level variables (None until connect_db() runs).
# Using a global client means ONE connection pool for the whole app —
# not a new connection per request (that would be very slow).
client: AsyncIOMotorClient = None
db = None


async def connect_db():
    """
    Open the MongoDB connection when the FastAPI app starts.

    Called from main.py's @app.on_event("startup").
    AsyncIOMotorClient creates a connection pool automatically.
    The 'ping' command verifies the connection actually works.
    """
    global client, db

    if not MONGO_URI or "your_user" in MONGO_URI:
        print("⚠️  MONGO_URI not set in backend/.env — DB calls will fail.")
        print("   Copy backend/.env.example → backend/.env and fill in your Atlas URI.")
        return

    # Create an async MongoDB client (connection pool)
    client = AsyncIOMotorClient(MONGO_URI)

    # Select the database by name
    db = client[DB_NAME]

    # Send a ping to confirm connection to Atlas
    try:
        await client.admin.command("ping")
        print(f"✅ Connected to MongoDB Atlas — Database: {DB_NAME}")
        # Create indexes for performance and data integrity
        await _create_indexes()
    except Exception as e:
        # Don't crash on startup if Atlas is unreachable.
        # The server will start but API calls needing DB will return 503.
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   Update MONGO_URI in backend/.env to fix this.")


async def disconnect_db():
    """
    Close the MongoDB connection when the app shuts down.

    Called from main.py's @app.on_event("shutdown").
    """
    global client
    if client:
        client.close()
        print("🔌 MongoDB connection closed.")


async def _create_indexes():
    """
    Create database indexes on startup.

    Indexes speed up queries and enforce uniqueness.
    Running create_index on an already-existing index is safe (idempotent).

    Collections and their indexes:
      users  — unique index on email (prevents duplicate registrations)
      leaves — index on user_id (fast lookup of one employee's leaves)
               compound index on (user_id, created_at) for sorted queries
    """
    # Unique index on email — MongoDB will reject duplicate email inserts
    await db["users"].create_index("email", unique=True)

    # Index on user_id so fetching leaves for one employee is fast
    await db["leaves"].create_index("user_id")

    # Compound index: filter by user_id AND sort by created_at together
    await db["leaves"].create_index([("user_id", 1), ("created_at", -1)])

    print("📑 Database indexes created/verified.")


def get_db():
    """
    Return the database object for use inside route functions.

    This is a simple accessor function. It's called inside route handlers
    to get the 'db' reference without importing the global variable directly.

    Example usage in a route:
        from database import get_db
        db = get_db()
        user = await db["users"].find_one({"email": email})
    """
    if db is None:
        raise RuntimeError("Database not connected. Was connect_db() called?")
    return db
