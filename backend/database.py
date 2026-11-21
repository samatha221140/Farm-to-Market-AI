"""
Farm-to-Market AI Persistent Multi-Phase Database Service
==========================================================
Manages persistent storage for all farmer interactions across:
  - Phase 1: Crop Recommendation & Economic Profit Ranking
  - Phase 2: Smart Irrigation, Soil Health / Fertilizer Planning, and Crop Disease / Pest / Weed Diagnoses
  - Phase 3: Direct Marketplace Produce Listings & Buyer Inquiries

Key Capabilities:
  1. Image File Storage: Uploaded crop photos are decoded and saved to `backend/uploads/`
     with timestamped unique IDs; file paths and web URLs are stored in the database.
  2. Environment & Credential Driven: Reads connection details, URLs, and passwords from `.env` via `config.py`.
  3. Team Collaboration Ready: Supports both local SQLite and remote cloud databases
     (PostgreSQL/Supabase/Neon/MySQL), so teammates/friends can update the exact same live data simultaneously.
  4. Dual Storage Architecture:
     - Relational Database (SQLite / Postgres)
     - Human-Readable Audit Stream File (`backend/data/farm_activity_log.jsonl`)
"""

import os
import io
import uuid
import json
import base64
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image

try:
    from backend import config
except ImportError:
    import config

DB_PATH = config.SQLITE_DB_PATH
LOG_PATH = config.AUDIT_LOG_PATH
DIAGNOSES_UPLOAD_DIR = config.DIAGNOSES_UPLOAD_DIR
MARKETPLACE_UPLOAD_DIR = config.MARKETPLACE_UPLOAD_DIR


# =========================================================================
# IMAGE PERSISTENCE & FILE STORAGE HANDLER
# =========================================================================

def save_uploaded_image(image_input: Any, category: str = "diagnoses", prefix: str = "crop") -> Tuple[str, str, int]:
    """
    Decodes and saves an uploaded crop image file to the physical upload directory.
    Accepts:
      - Base64 string (data URI or raw base64)
      - Raw bytes
      - PIL Image object
    Returns:
      (relative_web_url, absolute_file_path, file_size_bytes)
    """
    target_dir = MARKETPLACE_UPLOAD_DIR if category == "marketplace" else DIAGNOSES_UPLOAD_DIR
    target_dir.mkdir(parents=True, exist_ok=True)

    img = None
    if isinstance(image_input, Image.Image):
        img = image_input.convert("RGB")
    elif isinstance(image_input, bytes):
        try:
            img = Image.open(io.BytesIO(image_input)).convert("RGB")
        except Exception:
            img = None
    elif isinstance(image_input, str):
        if image_input.startswith("data:image"):
            image_input = image_input.split(",", 1)[1]
        try:
            raw_bytes = base64.b64decode(image_input)
            img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
        except Exception:
            # Check if it's already an existing file path
            p = Path(image_input)
            if p.exists() and p.is_file():
                try:
                    img = Image.open(p).convert("RGB")
                except Exception:
                    img = None

    if img is None:
        # Generate placeholder leaf if decoding failed
        img = Image.new("RGB", (256, 256), color=(40, 120, 60))

    # Generate unique filename: prefix_YYYYMMDD_HHMMSS_<short_uuid>.jpg
    now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{now_str}_{unique_suffix}.jpg"
    abs_path = target_dir / filename

    # Save as high-quality compressed JPEG
    img.save(abs_path, format="JPEG", quality=90, optimize=True)
    file_size = abs_path.stat().st_size

    subfolder = "marketplace" if category == "marketplace" else "diagnoses"
    rel_url = f"/uploads/{subfolder}/{filename}"
    return rel_url, str(abs_path), file_size


# =========================================================================
# DATABASE CONNECTION & SCHEMA INITIALIZATION
# =========================================================================

def get_db_connection():
    """
    Creates a connection to the configured database.
    Defaults to SQLite, with remote PostgreSQL fallback via psycopg2 if configured in .env.
    """
    if config.DATABASE_TYPE in ["postgres", "postgresql"] and config.DATABASE_URL:
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(config.DATABASE_URL)
            return conn, "postgres"
        except ImportError:
            print("[Info] 'psycopg2' not installed. Using local SQLite database file.")
        except Exception as err:
            print(f"[Warning] Remote PostgreSQL connection failed: {err}. Falling back to SQLite.")

    # SQLite Connection
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_database() -> None:
    """Initializes database tables across Phase 1, Phase 2, and Phase 3."""
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Phase 1 Recommendations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase1_recommendations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        input_n REAL,
        input_p REAL,
        input_k REAL,
        input_ph REAL,
        input_soil_type TEXT,
        input_water_availability TEXT,
        input_season TEXT,
        input_land_acres REAL,
        input_temperature REAL,
        input_rainfall REAL,
        input_humidity REAL,
        top_5_suitable_crops TEXT,
        top_3_profitable_crops TEXT,
        all_candidate_economics TEXT,
        message TEXT
    )
    """)

    # Table 2: Phase 2 Smart Irrigation Advisory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase2_smart_irrigation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        input_crop TEXT,
        input_land_acres REAL,
        input_soil_type TEXT,
        input_growth_stage TEXT,
        input_soil_moisture_pct REAL,
        input_rainfall_today_mm REAL,
        input_forecast_rain_mm REAL,
        input_temperature_c REAL,
        input_humidity_pct REAL,
        input_pump_rating TEXT,
        input_irrigation_method TEXT,
        output_pump_status TEXT,
        output_water_needed_litres REAL,
        output_runtime_minutes REAL,
        output_power_kwh REAL,
        output_summary TEXT,
        output_advisory_json TEXT
    )
    """)

    # Table 3: Phase 2 Soil Health & Fertilizer Dosage
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase2_soil_fertilizer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        input_crop TEXT,
        input_acres REAL,
        input_soil_n REAL,
        input_soil_p REAL,
        input_soil_k REAL,
        input_soil_ph REAL,
        input_organic_carbon REAL,
        input_ec REAL,
        input_zinc REAL,
        output_soil_ratings_json TEXT,
        output_chemical_bags_json TEXT,
        output_organic_package_json TEXT,
        output_schedule_inm TEXT,
        output_full_json TEXT
    )
    """)

    # Table 4: Phase 2 Vision Diagnosis (Includes Saved Image Path & URL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase2_diagnoses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        input_crop TEXT,
        input_farmer_notes TEXT,
        image_filename TEXT,
        image_path TEXT,
        image_url TEXT,
        image_size_bytes INTEGER,
        output_condition TEXT,
        output_category TEXT,
        output_pathogen TEXT,
        output_confidence_pct REAL,
        output_severity TEXT,
        output_organic_cure TEXT,
        output_chemical_cure TEXT,
        output_cultural_prevention TEXT,
        output_full_json TEXT
    )
    """)

    # Table 5: Phase 3 Produce Listings (Includes Optional Harvest Lot Photo)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase3_marketplace_listings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_code TEXT UNIQUE,
        timestamp TEXT NOT NULL,
        farmer_name TEXT,
        phone_number TEXT,
        crop TEXT,
        variety TEXT,
        quantity_quintals REAL,
        price_rs_per_quintal REAL,
        village TEXT,
        district TEXT,
        state TEXT,
        quality_grade TEXT,
        harvest_date TEXT,
        produce_image_url TEXT,
        status TEXT,
        total_estimated_value_rs REAL
    )
    """)

    # Table 6: Phase 3 Buyer Inquiries
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phase3_buyer_inquiries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        inquiry_code TEXT UNIQUE,
        listing_code TEXT,
        timestamp TEXT NOT NULL,
        buyer_name TEXT,
        buyer_phone TEXT,
        buyer_location TEXT,
        crop TEXT,
        offered_price_rs_per_quintal REAL,
        quantity_requested_quintals REAL,
        message TEXT,
        status TEXT
    )
    """)

    # Schema migration: Ensure any missing columns in pre-existing tables are safely added
    try:
        if db_type == "sqlite":
            cursor.execute("PRAGMA table_info(phase2_diagnoses)")
            p2_cols = [c[1] for c in cursor.fetchall()]
            if "image_filename" not in p2_cols:
                cursor.execute("ALTER TABLE phase2_diagnoses ADD COLUMN image_filename TEXT")
            if "image_path" not in p2_cols:
                cursor.execute("ALTER TABLE phase2_diagnoses ADD COLUMN image_path TEXT")
            if "image_url" not in p2_cols:
                cursor.execute("ALTER TABLE phase2_diagnoses ADD COLUMN image_url TEXT")
            if "image_size_bytes" not in p2_cols:
                cursor.execute("ALTER TABLE phase2_diagnoses ADD COLUMN image_size_bytes INTEGER")

            cursor.execute("PRAGMA table_info(phase3_marketplace_listings)")
            p3_cols = [c[1] for c in cursor.fetchall()]
            if "produce_image_url" not in p3_cols:
                cursor.execute("ALTER TABLE phase3_marketplace_listings ADD COLUMN produce_image_url TEXT")
        else:
            # PostgreSQL / generic SQL
            for col_def in [
                ("phase2_diagnoses", "image_filename", "TEXT"),
                ("phase2_diagnoses", "image_path", "TEXT"),
                ("phase2_diagnoses", "image_url", "TEXT"),
                ("phase2_diagnoses", "image_size_bytes", "BIGINT"),
                ("phase3_marketplace_listings", "produce_image_url", "TEXT"),
            ]:
                try:
                    cursor.execute(f"ALTER TABLE {col_def[0]} ADD COLUMN IF NOT EXISTS {col_def[1]} {col_def[2]}")
                except Exception:
                    pass
    except Exception as e:
        print(f"[Warning] DB column migration note: {e}")

    conn.commit()
    conn.close()


def _append_to_file_log(event_type: str, data: Dict[str, Any]) -> None:
    """Appends structured JSON entry to the human-readable audit stream file."""
    try:
        record = {
            "logged_at": datetime.now().isoformat(),
            "event_type": event_type,
            "payload": data
        }
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[Warning] Failed to append to audit log file: {e}")


# =========================================================================
# PHASE 1 RECORDING
# =========================================================================

def record_phase1_recommendation(farm_inputs: Dict[str, Any], land_acres: float, top5: List[Any], top3: List[Any], economics: List[Any], message: str = "") -> int:
    """Records Phase 1 Crop Recommendation inputs and AI-ranked outputs."""
    init_database()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO phase1_recommendations (
        timestamp, input_n, input_p, input_k, input_ph, input_soil_type,
        input_water_availability, input_season, input_land_acres,
        input_temperature, input_rainfall, input_humidity,
        top_5_suitable_crops, top_3_profitable_crops, all_candidate_economics, message
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_ts,
        farm_inputs.get("N_kg_ha"),
        farm_inputs.get("P_kg_ha"),
        farm_inputs.get("K_kg_ha"),
        farm_inputs.get("pH"),
        farm_inputs.get("Soil_Type"),
        farm_inputs.get("Water_Availability"),
        farm_inputs.get("Season"),
        land_acres,
        farm_inputs.get("Temperature_C"),
        farm_inputs.get("Rainfall_mm"),
        farm_inputs.get("Humidity_pct"),
        json.dumps(top5, ensure_ascii=False),
        json.dumps(top3, ensure_ascii=False),
        json.dumps(economics, ensure_ascii=False),
        message
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_1_CROP_RECOMMENDATION", {
        "id": record_id,
        "timestamp": now_ts,
        "inputs": farm_inputs,
        "land_acres": land_acres,
        "outputs": {
            "top_5_suitable": top5,
            "top_3_profitable": top3
        }
    })
    return record_id


# =========================================================================
# PHASE 2 RECORDING
# =========================================================================

def record_phase2_smart_irrigation(inputs: Dict[str, Any], advisory: Dict[str, Any]) -> int:
    """Records Phase 2 Smart Irrigation inputs, weather sensor metrics, and pump decisions."""
    init_database()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sched = advisory.get("pump_operation") or advisory.get("pump_schedule") or {}
    output_status = sched.get("pump_status") or sched.get("pump_action") or advisory.get("status", "OFF")
    litres = float(sched.get("total_litres_needed", 0.0))
    minutes = float(sched.get("runtime_minutes", 0.0))
    kwh = float(sched.get("kwh_consumed") or sched.get("energy_consumption_kwh", 0.0))
    summary = advisory.get("advisory_message") or advisory.get("irrigation_advisory_text", "")

    cursor.execute("""
    INSERT INTO phase2_smart_irrigation (
        timestamp, input_crop, input_land_acres, input_soil_type, input_growth_stage,
        input_soil_moisture_pct, input_rainfall_today_mm, input_forecast_rain_mm,
        input_temperature_c, input_humidity_pct, input_pump_rating, input_irrigation_method,
        output_pump_status, output_water_needed_litres, output_runtime_minutes,
        output_power_kwh, output_summary, output_advisory_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_ts,
        inputs.get("crop"),
        inputs.get("acres"),
        inputs.get("soil_type"),
        inputs.get("growth_stage"),
        inputs.get("soil_moisture_pct"),
        inputs.get("rainfall_today_mm"),
        inputs.get("forecast_rain_24h_mm"),
        inputs.get("temperature_c"),
        inputs.get("humidity_pct"),
        inputs.get("pump_rating"),
        inputs.get("irrigation_method"),
        output_status,
        litres,
        minutes,
        kwh,
        summary,
        json.dumps(advisory, ensure_ascii=False)
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_2_SMART_IRRIGATION", {
        "id": record_id,
        "timestamp": now_ts,
        "inputs": inputs,
        "outputs": advisory
    })
    return record_id


def record_phase2_soil_fertilizer(crop: str, acres: float, soil_data: Dict[str, Any], result: Dict[str, Any]) -> int:
    """Records Phase 2 Soil test inputs, NPK gaps, and dual Organic/Chemical packages."""
    init_database()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO phase2_soil_fertilizer (
        timestamp, input_crop, input_acres, input_soil_n, input_soil_p, input_soil_k,
        input_soil_ph, input_organic_carbon, input_ec, input_zinc,
        output_soil_ratings_json, output_chemical_bags_json, output_organic_package_json,
        output_schedule_inm, output_full_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_ts,
        crop,
        acres,
        soil_data.get("N"),
        soil_data.get("P"),
        soil_data.get("K"),
        soil_data.get("pH"),
        soil_data.get("organic_carbon"),
        soil_data.get("ec"),
        soil_data.get("zinc"),
        json.dumps(result.get("soil_health_ratings", {}), ensure_ascii=False),
        json.dumps(result.get("chemical_package", {}).get("bag_summary", result.get("chemical_fertilizer_schedule", {})), ensure_ascii=False),
        json.dumps(result.get("organic_package", result.get("organic_fertilizer_package", {})), ensure_ascii=False),
        str(result.get("integrated_nutrient_management") or result.get("inm_guidance", "")),
        json.dumps(result, ensure_ascii=False)
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_2_SOIL_FERTILIZER", {
        "id": record_id,
        "timestamp": now_ts,
        "crop": crop,
        "acres": acres,
        "inputs": soil_data,
        "outputs": result
    })
    return record_id


def record_phase2_diagnosis(
    crop: str,
    farmer_notes: str,
    image_input: Any,
    diagnosis: Dict[str, Any]
) -> Tuple[int, str]:
    """
    Saves the physical uploaded crop image to `backend/uploads/diagnoses/`
    and records inputs, image metadata, and diagnosis outputs to the database.
    Returns: (record_id, image_url)
    """
    init_database()

    # 1. Save uploaded image to physical file storage
    image_url, image_path, file_size = save_uploaded_image(
        image_input=image_input,
        category="diagnoses",
        prefix=f"diag_{crop.lower()[:8]}"
    )
    image_filename = Path(image_path).name

    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    diag_result = diagnosis.get("diagnosis", {}) if diagnosis.get("diagnosis") else diagnosis
    condition = (
        diag_result.get("diagnosis_name") or
        diag_result.get("condition") or
        diag_result.get("disease_detected") or
        "Unknown Condition"
    )
    category = diag_result.get("category", "Disease")
    pathogen = diag_result.get("pathogen_species") or diag_result.get("pathogen", "")
    confidence = float(diag_result.get("confidence_pct") or diag_result.get("confidence", 0.0))
    severity = diag_result.get("severity", "Moderate")
    organic = diag_result.get("organic_solution") or diag_result.get("organic_treatment", "")
    chemical = diag_result.get("chemical_solution") or diag_result.get("chemical_treatment", "")
    cultural = diag_result.get("preventive_advisory") or diag_result.get("cultural_prevention", "")

    cursor.execute("""
    INSERT INTO phase2_diagnoses (
        timestamp, input_crop, input_farmer_notes,
        image_filename, image_path, image_url, image_size_bytes,
        output_condition, output_category, output_pathogen, output_confidence_pct,
        output_severity, output_organic_cure, output_chemical_cure, output_cultural_prevention,
        output_full_json
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_ts,
        crop,
        farmer_notes,
        image_filename,
        image_path,
        image_url,
        file_size,
        condition,
        category,
        pathogen,
        confidence,
        severity,
        organic,
        chemical,
        cultural,
        json.dumps(diagnosis, ensure_ascii=False)
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_2_CROP_DIAGNOSIS", {
        "id": record_id,
        "timestamp": now_ts,
        "crop": crop,
        "farmer_notes": farmer_notes,
        "image_file": image_filename,
        "image_url": image_url,
        "outputs": diag_result
    })
    return record_id, image_url


# =========================================================================
# PHASE 3 RECORDING
# =========================================================================

def record_phase3_listing(listing: Dict[str, Any], produce_image_input: Optional[Any] = None) -> Tuple[int, Optional[str]]:
    """Records a new harvest produce lot posted by a farmer, saving optional produce photo."""
    init_database()

    image_url = None
    if produce_image_input:
        image_url, _, _ = save_uploaded_image(produce_image_input, category="marketplace", prefix="lot")

    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = listing.get("posted_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO phase3_marketplace_listings (
        listing_code, timestamp, farmer_name, phone_number, crop, variety,
        quantity_quintals, price_rs_per_quintal, village, district, state,
        quality_grade, harvest_date, produce_image_url, status, total_estimated_value_rs
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        listing.get("id"),
        now_ts,
        listing.get("farmer_name"),
        listing.get("phone_number"),
        listing.get("crop"),
        listing.get("variety"),
        listing.get("quantity_quintals"),
        listing.get("price_per_quintal"),
        listing.get("village"),
        listing.get("district"),
        listing.get("state", "Andhra Pradesh"),
        listing.get("grade", "Grade A"),
        listing.get("harvest_date"),
        image_url or listing.get("produce_image_url"),
        listing.get("status", "ACTIVE"),
        listing.get("total_value_rs") or (float(listing.get("quantity_quintals", 0)) * float(listing.get("price_per_quintal", 0)))
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_3_MARKETPLACE_LISTING", {
        "id": record_id,
        "listing": listing,
        "image_url": image_url
    })
    return record_id, image_url


def record_phase3_inquiry(inquiry: Dict[str, Any]) -> int:
    """Records a buyer's direct purchasing inquiry delivered to a farmer."""
    init_database()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    now_ts = inquiry.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO phase3_buyer_inquiries (
        inquiry_code, listing_code, timestamp, buyer_name, buyer_phone,
        buyer_location, crop, offered_price_rs_per_quintal,
        quantity_requested_quintals, message, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inquiry.get("inquiry_id"),
        inquiry.get("listing_id"),
        now_ts,
        inquiry.get("buyer_name"),
        inquiry.get("buyer_phone"),
        inquiry.get("buyer_location"),
        inquiry.get("crop"),
        inquiry.get("offered_price_rs_per_quintal"),
        inquiry.get("quantity_requested_quintals"),
        inquiry.get("message"),
        inquiry.get("status", "DELIVERED_TO_FARMER")
    ))
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()

    _append_to_file_log("PHASE_3_BUYER_INQUIRY", {
        "id": record_id,
        "inquiry": inquiry
    })
    return record_id


# =========================================================================
# QUERY & AUDIT RETRIEVAL
# =========================================================================

def get_database_stats() -> Dict[str, Any]:
    """Returns row counts, upload directory stats, and database metadata."""
    init_database()
    conn, db_type = get_db_connection()
    cursor = conn.cursor()

    stats = {}
    tables = [
        "phase1_recommendations",
        "phase2_smart_irrigation",
        "phase2_soil_fertilizer",
        "phase2_diagnoses",
        "phase3_marketplace_listings",
        "phase3_buyer_inquiries"
    ]
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        stats[table] = cursor.fetchone()[0]

    stats["total_activities_logged"] = sum(stats.values())
    stats["database_type"] = config.DATABASE_TYPE
    stats["db_file_path"] = str(DB_PATH)
    stats["db_file_size_kb"] = round(DB_PATH.stat().st_size / 1024, 2) if DB_PATH.exists() else 0
    stats["audit_log_path"] = str(LOG_PATH)
    stats["audit_log_size_kb"] = round(LOG_PATH.stat().st_size / 1024, 2) if LOG_PATH.exists() else 0

    # Count saved image uploads
    diag_imgs = len(list(DIAGNOSES_UPLOAD_DIR.glob("*.jpg"))) if DIAGNOSES_UPLOAD_DIR.exists() else 0
    market_imgs = len(list(MARKETPLACE_UPLOAD_DIR.glob("*.jpg"))) if MARKETPLACE_UPLOAD_DIR.exists() else 0
    stats["saved_crop_photos_count"] = diag_imgs + market_imgs
    stats["uploads_directory"] = str(config.UPLOAD_BASE_DIR)

    safe_summary = config.get_safe_db_summary()
    stats["is_remote_connected"] = safe_summary["is_remote_connected"]
    stats["masked_database_url"] = safe_summary["masked_database_url"]
    stats["env_file_loaded"] = safe_summary["env_file_loaded"]

    conn.close()
    return stats


def get_all_records(phase: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """Retrieves chronological activity records across all phases."""
    init_database()
    conn, _ = get_db_connection()
    cursor = conn.cursor()
    records = {}

    if phase in [None, "all", "1", "phase1"]:
        cursor.execute(f"SELECT * FROM phase1_recommendations ORDER BY id DESC LIMIT {limit}")
        records["phase1_recommendations"] = [dict(row) for row in cursor.fetchall()]

    if phase in [None, "all", "2", "phase2", "phase2_irr"]:
        cursor.execute(f"SELECT * FROM phase2_smart_irrigation ORDER BY id DESC LIMIT {limit}")
        records["phase2_smart_irrigation"] = [dict(row) for row in cursor.fetchall()]

    if phase in [None, "all", "2", "phase2", "phase2_soil"]:
        cursor.execute(f"SELECT * FROM phase2_soil_fertilizer ORDER BY id DESC LIMIT {limit}")
        records["phase2_soil_fertilizer"] = [dict(row) for row in cursor.fetchall()]

    if phase in [None, "all", "2", "phase2", "phase2_diag"]:
        cursor.execute(f"SELECT * FROM phase2_diagnoses ORDER BY id DESC LIMIT {limit}")
        records["phase2_diagnoses"] = [dict(row) for row in cursor.fetchall()]

    if phase in [None, "all", "3", "phase3"]:
        cursor.execute(f"SELECT * FROM phase3_marketplace_listings ORDER BY id DESC LIMIT {limit}")
        records["phase3_marketplace_listings"] = [dict(row) for row in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM phase3_buyer_inquiries ORDER BY id DESC LIMIT {limit}")
        records["phase3_buyer_inquiries"] = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return records
