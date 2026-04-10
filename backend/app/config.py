"""
Application configuration.

Loads all required environment variables from the .env file.
Raises RuntimeError on startup if any required variable is missing.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the project root (one level above backend/)
_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_env_path)

# --- Required keys (app will not start without these) --------------------

_REQUIRED = [
    "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
    "SECRET_KEY", "JWT_SECRET",
    "REDIS_URL",
    "CELERY_BROKER_URL", "CELERY_RESULT_BACKEND",
]

_missing = [k for k in _REQUIRED if not os.getenv(k)]
if _missing:
    raise RuntimeError(f"Missing required env vars: {', '.join(_missing)}")

# --- Database -------------------------------------------------------------
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Flask ----------------------------------------------------------------
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY")

# --- JWT ------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET")
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

# --- Redis ----------------------------------------------------------------
REDIS_URL = os.getenv("REDIS_URL")

# --- Celery ---------------------------------------------------------------
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

# --- Google OAuth (optional — app starts without these) -------------------
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "")
