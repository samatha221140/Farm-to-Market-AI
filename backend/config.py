"""
Farm-to-Market AI Configuration & Environment Manager
======================================================
Loads environment variables from `.env` file (or system environment)
to manage database URLs, confidential credentials, upload paths, and server settings.

Supports:
  - Local SQLite Database (zero configuration, persistent file)
  - Remote Shared Cloud Databases (PostgreSQL / MySQL / Supabase / Neon / RDS)
    allowing multiple team members / friends to update and access live data simultaneously.
"""

import os
import sys
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
# DATABASE CONFIGURATION
# -----------------------------------------------------------------------------
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# Detailed DB fields (used if DATABASE_URL is not explicitly specified)
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", "5432" if DATABASE_TYPE == "postgres" else "3306")
DB_NAME = os.getenv("DB_NAME", "farm_database")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

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

# SQLite default file path
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
    has_remote_url = bool(DATABASE_URL)
    masked_url = ""
    if has_remote_url:
        try:
            # Mask password in URL (e.g. postgresql://user:***@host:port/db)
            prefix, rest = DATABASE_URL.split("://", 1)
            if "@" in rest:
                userpass, hostdb = rest.split("@", 1)
                user = userpass.split(":")[0] if ":" in userpass else userpass
                masked_url = f"{prefix}://{user}:******@{hostdb}"
            else:
                masked_url = f"{prefix}://{rest}"
        except Exception:
            masked_url = "configured (remote connection string)"

    return {
        "database_type": DATABASE_TYPE,
        "is_remote_connected": has_remote_url or (bool(DB_HOST) and DATABASE_TYPE != "sqlite"),
        "sqlite_file_path": str(SQLITE_DB_PATH),
        "sqlite_exists": SQLITE_DB_PATH.exists(),
        "sqlite_size_kb": round(SQLITE_DB_PATH.stat().st_size / 1024, 2) if SQLITE_DB_PATH.exists() else 0,
        "masked_database_url": masked_url,
        "remote_host": DB_HOST or "N/A",
        "remote_database": DB_NAME if DB_HOST else "N/A",
        "audit_log_path": str(AUDIT_LOG_PATH),
        "upload_directory": str(UPLOAD_BASE_DIR),
        "env_file_loaded": str(_loaded_env_path) if _loaded_env_path else "None (Using defaults/system env)"
    }
