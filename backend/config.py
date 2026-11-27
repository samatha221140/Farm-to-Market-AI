"""
Farm-to-Market AI Configuration & Environment Manager
======================================================
Loads environment variables from `.env` file (or system environment)
to manage MongoDB URIs, database credentials, upload paths, and server settings.

Supports:
  - MongoDB (Native NoSQL Document Database: MongoDB Atlas / Local MongoDB instance)
    Stores rich, nested JSON/BSON documents directly for faster querying and better UI results.
  - Local SQLite Database fallback (zero-setup persistent file) if MongoDB is offline.
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, Any

# Root and directory paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent

# Search paths for .env
ENV_PATHS = [
    PROJECT_ROOT / ".env",
    BACKEND_DIR / ".env"
]


def load_dotenv_custom():
    """Lightweight, zero-dependency .env parser and environment loader."""
    loaded_from = None
    for env_path in ENV_PATHS:
        if env_path.exists() and env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, val = line.split("=", 1)
                            key = key.strip()
                            # Strip inline comment if present
                            if "#" in val:
                                val = val.split("#", 1)[0]
                            val = val.strip().strip("'\"")
                            # Only set if not already overridden by system env
                            if key not in os.environ:
                                os.environ[key] = val
                loaded_from = env_path
                break
            except Exception as e:
                print(f"[Warning] Failed loading .env from {env_path}: {e}")
    return loaded_from


_loaded_env_path = load_dotenv_custom()

# -----------------------------------------------------------------------------
# APPLICATION SETTINGS
# -----------------------------------------------------------------------------
FLASK_ENV = os.getenv("FLASK_ENV", "development")
DEBUG = os.getenv("DEBUG", "True").lower() in ["true", "1", "yes"]
PORT = int(os.getenv("PORT", "5000"))
SECRET_KEY = os.getenv("SECRET_KEY", "farm_to_market_ai_secret_key_2026_andhra_pradesh")

# -----------------------------------------------------------------------------
# DATABASE CONFIGURATION: MONGODB & HYBRID DOCUMENT STORE
# -----------------------------------------------------------------------------
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "mongodb").lower()

# MongoDB connection string (supports mongodb:// or mongodb+srv:// for MongoDB Atlas)
MONGODB_URI = os.getenv("MONGODB_URI") or os.getenv("DATABASE_URL") or "mongodb://127.0.0.1:27017/farm_to_market_ai"
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME") or os.getenv("DB_NAME") or "farm_to_market_ai"

def resolve_project_path(val: str, default: Path) -> Path:
    """Resolves relative paths against PROJECT_ROOT instead of arbitrary CWD."""
    if not val:
        return default.resolve()
    p = Path(val)
    if not p.is_absolute():
        p = (PROJECT_ROOT / p).resolve()
    else:
        p = p.resolve()
    return p

# SQLite fallback file path (used automatically if MongoDB connection is offline)
SQLITE_DB_PATH = resolve_project_path(os.getenv("SQLITE_DB_PATH", ""), BACKEND_DIR / "data" / "farm_database.db")

# Stream Audit log file
AUDIT_LOG_PATH = resolve_project_path(os.getenv("AUDIT_LOG_PATH", ""), BACKEND_DIR / "data" / "farm_activity_log.jsonl")

# -----------------------------------------------------------------------------
# UPLOAD FOLDERS (FOR INPUT CROP IMAGES & PRODUCE PHOTOS)
# -----------------------------------------------------------------------------
UPLOAD_BASE_DIR = resolve_project_path(os.getenv("UPLOAD_FOLDER", ""), BACKEND_DIR / "uploads")
DIAGNOSES_UPLOAD_DIR = UPLOAD_BASE_DIR / "diagnoses"
MARKETPLACE_UPLOAD_DIR = UPLOAD_BASE_DIR / "marketplace"

# Ensure upload directories exist
DIAGNOSES_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MARKETPLACE_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
SQLITE_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024)))  # 16 MB limit


def get_safe_db_summary() -> Dict[str, Any]:
    """Returns a sanitized summary of database connection details with masked passwords."""
    masked_url = "None"
    if MONGODB_URI:
        try:
            # Mask password in MongoDB URI (e.g. mongodb+srv://user:pass@cluster.mongodb.net/...)
            masked_url = re.sub(r":([^@]+)@", ":******@", MONGODB_URI)
        except Exception:
            masked_url = "configured (remote connection string)"

    return {
        "database_type": DATABASE_TYPE,
        "mongodb_uri_configured": bool(MONGODB_URI),
        "masked_database_url": masked_url,
        "mongodb_database_name": MONGODB_DB_NAME,
        "sqlite_fallback_file": str(SQLITE_DB_PATH),
        "sqlite_fallback_exists": SQLITE_DB_PATH.exists(),
        "sqlite_size_kb": round(SQLITE_DB_PATH.stat().st_size / 1024, 2) if SQLITE_DB_PATH.exists() else 0,
        "audit_log_path": str(AUDIT_LOG_PATH),
        "upload_directory": str(UPLOAD_BASE_DIR),
        "env_file_loaded": str(_loaded_env_path) if _loaded_env_path else "None (Using defaults/system env)"
    }
