# ============================================================
# main.py — Entry point of the FastAPI application
# Every request enters through here first
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# load_dotenv() reads the .env file and puts all KEY=VALUE pairs
# into the environment so os.getenv() can access them.
# MUST be called before importing anything that uses env vars.
load_dotenv()

# Import routers — each router is a group of related endpoints
# auth_router handles /api/auth/register and /api/auth/login
# leave_router handles all /api/leave/* endpoints
from routes.auth import router as auth_router
from routes.leave import router as leave_router

# Import DB lifecycle functions to connect/disconnect on start/stop
from database import connect_db, disconnect_db

# ── Create the FastAPI app instance ──────────────────────────
# title and version appear in the auto-generated /docs Swagger UI
app = FastAPI(
    title="HuskyVoice Leave Management API",
    description="REST API for employee leave applications and employer approvals",
    version="1.0.0"
)

# ── CORS Middleware ───────────────────────────────────────────
# CORS (Cross-Origin Resource Sharing) allows the frontend (on a
# different domain/port) to call this backend.
# Without this, browsers block the requests by default.
#
# ALLOWED_ORIGINS env var = comma-separated list of allowed frontend URLs
# e.g. "http://localhost:5173,https://myapp.vercel.app"
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173"  # default for local development
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,   # which frontend URLs are allowed
    allow_credentials=True,          # allow Authorization header cookies
    allow_methods=["*"],             # allow GET, POST, PATCH, DELETE, etc.
    allow_headers=["*"],             # allow all headers including Authorization
)

# ── Register Routers ─────────────────────────────────────────
# prefix="/api/auth" means all routes in auth_router are prefixed:
#   register → POST /api/auth/register
#   login    → POST /api/auth/login
# tags appear as section names in Swagger /docs UI
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(leave_router, prefix="/api/leave", tags=["Leave"])

# ── App Lifecycle Events ──────────────────────────────────────
# startup runs once when the server first starts
# We connect to MongoDB here (async connection must happen after server starts)
@app.on_event("startup")
async def on_startup():
    """Connect to MongoDB Atlas when the server starts."""
    await connect_db()

# shutdown runs once when the server is shutting down
@app.on_event("shutdown")
async def on_shutdown():
    """Close MongoDB connection when the server shuts down."""
    await disconnect_db()

# ── Health Check Endpoint ─────────────────────────────────────
# Simple endpoint to verify the server is running.
# Used by Render to check if the service is alive.
@app.get("/", tags=["Health"])
async def root():
    """Returns a simple message to confirm the API is running."""
    return {
        "message": "HuskyVoice Leave Management API is running",
        "docs": "/docs",        # Swagger UI URL
        "redoc": "/redoc"       # ReDoc UI URL
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for deployment platform monitoring."""
    return {"status": "healthy"}
