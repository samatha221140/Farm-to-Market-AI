"""
Farm-to-Market AI Persistent Multi-Phase Database Service
==========================================================
Manages persistent document and relational storage across:
  - Phase 1: Crop Recommendation & Economic Profit Ranking
  - Phase 2: Smart Irrigation, Soil Health / Fertilizer Planning, and Crop Disease / Pest / Weed Diagnoses
  - Phase 3: Direct Marketplace Produce Listings & Buyer Inquiries

Database Architecture:
  1. Primary Document Database: MongoDB (MongoDB Atlas / Local MongoDB)
     - Stores rich, nested JSON/BSON documents natively.
     - Powers high-performance real-time UI filtering, deep querying, and synchronized state.
  2. Automatic Local Fallback: SQLite (`farm_database.db`)
     - If MongoDB server is offline or not configured, seamlessly records to local SQLite without disruption.
  3. Structured Audit Trail:
     - Human-readable append-only JSON Lines stream (`farm_activity_log.jsonl`).
  4. Physical Asset Storage:
     - Uploaded crop diagnosis and harvest lot produce photos saved to `backend/uploads/` with unique UUIDs.
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

# MongoDB optional import
try:
    import pymongo
    from bson import ObjectId
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

DB_PATH = config.SQLITE_DB_PATH
LOG_PATH = config.AUDIT_LOG_PATH
DIAGNOSES_UPLOAD_DIR = config.DIAGNOSES_UPLOAD_DIR
MARKETPLACE_UPLOAD_DIR = config.MARKETPLACE_UPLOAD_DIR

import time

# Global cached MongoDB client and cooldown manager
_mongo_client = None
_mongo_db = None
_mongo_connected = False
_last_mongo_check_time = 0.0
MONGO_CHECK_INTERVAL = 30.0  # seconds between retry attempts if offline


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
        img = Image.open(io.BytesIO(image_input)).convert("RGB")
    elif isinstance(image_input, str):
        raw_b64 = image_input
        if raw_b64.startswith("data:image"):
            try:
                raw_b64 = raw_b64.split(",", 1)[1]
            except IndexError:
                pass
        try:
            img_bytes = base64.b64decode(raw_b64)
            img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        except Exception as e:
            p = Path(image_input)
            if p.exists() and p.is_file():
                img = Image.open(p).convert("RGB")
            else:
                raise ValueError(f"Could not decode image input: {e}")

    if img is None:
        raise ValueError("Unsupported image input format.")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_suffix = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{ts}_{unique_suffix}.jpg"
    abs_file_path = target_dir / filename

    img.save(str(abs_file_path), "JPEG", quality=88, optimize=True)
    file_size = abs_file_path.stat().st_size

    relative_url = f"/uploads/{category}/{filename}"
    return relative_url, str(abs_file_path), file_size


# =========================================================================
# DATABASE CONNECTION & SCHEMA INITIALIZATION (MONGODB & SQLITE)
# =========================================================================

def get_mongodb_connection(force_retry: bool = False):
    """
    Attempts to connect to MongoDB (Atlas or Local) using pymongo.
    Returns (db_instance, True) if connected, else (None, False).
    Employs cooldown caching to eliminate latency when MongoDB is offline.
    """
    global _mongo_client, _mongo_db, _mongo_connected, _last_mongo_check_time

    if not PYMONGO_AVAILABLE:
        return None, False

    if _mongo_connected and _mongo_db is not None:
        return _mongo_db, True

    now = time.time()
    if not force_retry and not _mongo_connected and (now - _last_mongo_check_time < MONGO_CHECK_INTERVAL):
        return None, False

    _last_mongo_check_time = now

    if config.DATABASE_TYPE in ["mongodb", "mongo"] and config.MONGODB_URI:
        try:
            client = pymongo.MongoClient(
                config.MONGODB_URI,
                serverSelectionTimeoutMS=2000,
                connectTimeoutMS=2000
            )
            client.admin.command("ping")
            db = client[config.MONGODB_DB_NAME]
            _mongo_client = client
            _mongo_db = db
            _mongo_connected = True
            print(f"[Success] Connected to MongoDB database '{config.MONGODB_DB_NAME}'")
            return db, True
        except Exception as err:
            _mongo_connected = False
            return None, False

    return None, False


def get_db_connection():
    """
    Primary database connection dispatcher.
    Returns:
      (conn_or_db, "mongodb") if MongoDB is active,
      OR (conn, "sqlite") if falling back to local SQLite.
    """
    db, is_mongo = get_mongodb_connection()
    if is_mongo:
        return db, "mongodb"

    # SQLite Connection Fallback
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn, "sqlite"


def init_database() -> None:
    """Initializes collections and indexes in MongoDB or tables in SQLite."""
    db, db_type = get_db_connection()

    if db_type == "mongodb":
        try:
            # Ensure MongoDB indexes for rapid querying in UI
            db.phase1_recommendations.create_index([("timestamp", -1)])
            db.phase2_smart_irrigation.create_index([("timestamp", -1)])
            db.phase2_soil_fertilizer.create_index([("timestamp", -1)])
            db.phase2_diagnoses.create_index([("timestamp", -1)])
            db.phase3_marketplace_listings.create_index([("listing_code", 1)], unique=True, sparse=True)
            db.phase3_marketplace_listings.create_index([("timestamp", -1)])
            db.phase3_buyer_inquiries.create_index([("inquiry_code", 1)], unique=True, sparse=True)
            db.phase3_buyer_inquiries.create_index([("timestamp", -1)])
        except Exception as e:
            print(f"[Warning] MongoDB index creation note: {e}")
        return

    # SQLite Tables Initialization
    cursor = db.cursor()

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

    # Schema column verification for SQLite
    try:
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
    except Exception as e:
        print(f"[Warning] SQLite migration note: {e}")

    db.commit()
    db.close()


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
# PHASE 1 RECORDING: CROP RECOMMENDATION & PROFIT RANKING
# =========================================================================

def record_phase1_recommendation(
    farm_inputs: Dict[str, Any],
    land_acres: float,
    top5: List[Any],
    top3: List[Any],
    economics: List[Any],
    message: str = ""
) -> str:
    """Records Phase 1 Crop Recommendation inputs and AI-ranked outputs to MongoDB / SQLite."""
    init_database()
    db, db_type = get_db_connection()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if db_type == "mongodb":
        doc = {
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 1,
            "event_type": "CROP_RECOMMENDATION",
            "farm_inputs": farm_inputs,
            "land_acres": land_acres,
            "top_5_suitable_crops": top5,
            "top_3_profitable_crops": top3,
            "all_candidate_economics": economics,
            "message": message
        }
        res = db.phase1_recommendations.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
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
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_1_CROP_RECOMMENDATION", {
        "id": record_id,
        "database_engine": db_type,
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
# PHASE 2 RECORDING: SMART IRRIGATION, SOIL HEALTH & VISION DIAGNOSES
# =========================================================================

def record_phase2_smart_irrigation(inputs: Dict[str, Any], advisory: Dict[str, Any]) -> str:
    """Records Phase 2 Smart Irrigation inputs, weather sensor metrics, and pump decisions."""
    init_database()
    db, db_type = get_db_connection()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sched = advisory.get("pump_operation") or advisory.get("pump_schedule") or {}
    output_status = sched.get("pump_status") or sched.get("pump_action") or advisory.get("status", "OFF")
    litres = float(sched.get("total_litres_needed", 0.0))
    minutes = float(sched.get("runtime_minutes", 0.0))
    kwh = float(sched.get("kwh_consumed") or sched.get("energy_consumption_kwh", 0.0))
    summary = advisory.get("advisory_message") or advisory.get("irrigation_advisory_text", "")

    if db_type == "mongodb":
        doc = {
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 2,
            "event_type": "SMART_IRRIGATION",
            "crop": inputs.get("crop"),
            "inputs": inputs,
            "output_pump_status": output_status,
            "output_water_needed_litres": litres,
            "output_runtime_minutes": minutes,
            "output_power_kwh": kwh,
            "output_summary": summary,
            "advisory": advisory
        }
        res = db.phase2_smart_irrigation.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
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
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_2_SMART_IRRIGATION", {
        "id": record_id,
        "database_engine": db_type,
        "timestamp": now_ts,
        "inputs": inputs,
        "outputs": advisory
    })
    return record_id


def record_phase2_soil_fertilizer(crop: str, acres: float, soil_data: Dict[str, Any], result: Dict[str, Any]) -> str:
    """Records Phase 2 Soil test inputs, NPK gaps, and dual Organic/Chemical packages."""
    init_database()
    db, db_type = get_db_connection()
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if db_type == "mongodb":
        doc = {
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 2,
            "event_type": "SOIL_FERTILIZER_PLAN",
            "crop": crop,
            "acres": acres,
            "soil_inputs": soil_data,
            "soil_health_ratings": result.get("soil_health_ratings", {}),
            "chemical_package": result.get("chemical_package", {}),
            "organic_package": result.get("organic_package", {}),
            "schedule_inm": str(result.get("integrated_nutrient_management") or result.get("inm_guidance", "")),
            "full_result": result
        }
        res = db.phase2_soil_fertilizer.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
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
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_2_SOIL_FERTILIZER", {
        "id": record_id,
        "database_engine": db_type,
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
) -> Tuple[str, str]:
    """
    Saves the physical uploaded crop image to `backend/uploads/diagnoses/`
    and records inputs, image metadata, and diagnosis outputs to MongoDB / SQLite.
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

    db, db_type = get_db_connection()
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

    if db_type == "mongodb":
        doc = {
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 2,
            "event_type": "CROP_VISION_DIAGNOSIS",
            "crop": crop,
            "farmer_notes": farmer_notes,
            "image_filename": image_filename,
            "image_path": image_path,
            "image_url": image_url,
            "image_size_bytes": file_size,
            "condition": condition,
            "category": category,
            "pathogen": pathogen,
            "confidence_pct": confidence,
            "severity": severity,
            "organic_cure": organic,
            "chemical_cure": chemical,
            "cultural_prevention": cultural,
            "full_diagnosis": diagnosis
        }
        res = db.phase2_diagnoses.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
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
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_2_CROP_DIAGNOSIS", {
        "id": record_id,
        "database_engine": db_type,
        "timestamp": now_ts,
        "crop": crop,
        "farmer_notes": farmer_notes,
        "image_file": image_filename,
        "image_url": image_url,
        "outputs": diag_result
    })
    return record_id, image_url


# =========================================================================
# PHASE 3 RECORDING: DIRECT FARMER-TO-BUYER MARKETPLACE
# =========================================================================

def record_phase3_listing(listing: Dict[str, Any], produce_image_input: Optional[Any] = None) -> Tuple[str, Optional[str]]:
    """Records a new harvest produce lot posted by a farmer, saving optional produce photo."""
    init_database()

    image_url = None
    if produce_image_input:
        image_url, _, _ = save_uploaded_image(produce_image_input, category="marketplace", prefix="lot")

    db, db_type = get_db_connection()
    now_ts = listing.get("posted_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    qty = float(listing.get("quantity_quintals") or listing.get("quantity", 0))
    price = float(listing.get("price_per_quintal") or listing.get("asking_price_per_quintal", 0))
    total_val = listing.get("total_value_rs") or (qty * price)

    if db_type == "mongodb":
        doc = {
            "listing_code": listing.get("id") or f"LOT-{uuid.uuid4().hex[:6].upper()}",
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 3,
            "event_type": "MARKETPLACE_LISTING",
            "farmer_name": listing.get("farmer_name"),
            "phone_number": listing.get("phone_number"),
            "crop": listing.get("crop"),
            "variety": listing.get("variety"),
            "quantity_quintals": qty,
            "price_rs_per_quintal": price,
            "village": listing.get("village"),
            "district": listing.get("district"),
            "state": listing.get("state", "Andhra Pradesh"),
            "quality_grade": listing.get("grade") or listing.get("quality_grade", "Grade A"),
            "harvest_date": listing.get("harvest_date"),
            "produce_image_url": image_url or listing.get("produce_image_url") or listing.get("photo_url"),
            "notes": listing.get("notes", ""),
            "status": listing.get("status", "ACTIVE"),
            "total_estimated_value_rs": total_val
        }
        res = db.phase3_marketplace_listings.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
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
            qty,
            price,
            listing.get("village"),
            listing.get("district"),
            listing.get("state", "Andhra Pradesh"),
            listing.get("grade") or listing.get("quality_grade", "Grade A"),
            listing.get("harvest_date"),
            image_url or listing.get("produce_image_url") or listing.get("photo_url"),
            listing.get("status", "ACTIVE"),
            total_val
        ))
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_3_MARKETPLACE_LISTING", {
        "id": record_id,
        "database_engine": db_type,
        "listing": listing,
        "image_url": image_url
    })
    return record_id, image_url


def record_phase3_inquiry(inquiry: Dict[str, Any]) -> str:
    """Records a buyer's direct purchasing inquiry delivered to a farmer."""
    init_database()
    db, db_type = get_db_connection()
    now_ts = inquiry.get("created_at") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    offered_p = float(inquiry.get("offered_price_rs_per_quintal") or inquiry.get("offer_price", 0))
    req_qty = float(inquiry.get("quantity_requested_quintals") or inquiry.get("quantity", 0))

    if db_type == "mongodb":
        doc = {
            "inquiry_code": inquiry.get("inquiry_id") or f"INQ-{uuid.uuid4().hex[:6].upper()}",
            "listing_code": inquiry.get("listing_id") or inquiry.get("lot_id"),
            "timestamp": now_ts,
            "created_at": datetime.now().isoformat(),
            "phase": 3,
            "event_type": "BUYER_INQUIRY",
            "buyer_name": inquiry.get("buyer_name"),
            "buyer_phone": inquiry.get("buyer_phone"),
            "buyer_location": inquiry.get("buyer_location"),
            "crop": inquiry.get("crop"),
            "offered_price_rs_per_quintal": offered_p,
            "quantity_requested_quintals": req_qty,
            "message": inquiry.get("message"),
            "status": inquiry.get("status", "DELIVERED_TO_FARMER")
        }
        res = db.phase3_buyer_inquiries.insert_one(doc)
        record_id = str(res.inserted_id)
    else:
        cursor = db.cursor()
        cursor.execute("""
        INSERT INTO phase3_buyer_inquiries (
            inquiry_code, listing_code, timestamp, buyer_name, buyer_phone,
            buyer_location, crop, offered_price_rs_per_quintal,
            quantity_requested_quintals, message, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inquiry.get("inquiry_id"),
            inquiry.get("listing_id") or inquiry.get("lot_id"),
            now_ts,
            inquiry.get("buyer_name"),
            inquiry.get("buyer_phone"),
            inquiry.get("buyer_location"),
            inquiry.get("crop"),
            offered_p,
            req_qty,
            inquiry.get("message"),
            inquiry.get("status", "DELIVERED_TO_FARMER")
        ))
        record_id = str(cursor.lastrowid)
        db.commit()
        db.close()

    _append_to_file_log("PHASE_3_BUYER_INQUIRY", {
        "id": record_id,
        "database_engine": db_type,
        "inquiry": inquiry
    })
    return record_id


# =========================================================================
# QUERY & AUDIT RETRIEVAL (FORMATTED FOR RICH UI RENDERING)
# =========================================================================

def get_database_stats() -> Dict[str, Any]:
    """Returns row/document counts, storage engine metadata, and upload directory metrics."""
    init_database()
    db, db_type = get_db_connection()

    stats = {}
    table_keys = [
        "phase1_recommendations",
        "phase2_smart_irrigation",
        "phase2_soil_fertilizer",
        "phase2_diagnoses",
        "phase3_marketplace_listings",
        "phase3_buyer_inquiries"
    ]

    if db_type == "mongodb":
        for k in table_keys:
            try:
                stats[k] = db[k].count_documents({})
            except Exception:
                stats[k] = 0
        stats["database_type"] = "mongodb"
        stats["engine_name"] = "MongoDB NoSQL Document Database"
        stats["mongodb_connected"] = True
        stats["mongodb_database"] = config.MONGODB_DB_NAME
    else:
        cursor = db.cursor()
        for k in table_keys:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {k}")
                stats[k] = cursor.fetchone()[0]
            except Exception:
                stats[k] = 0
        stats["database_type"] = "sqlite"
        stats["engine_name"] = "SQLite Local Embedded Engine (Fallback)"
        stats["mongodb_connected"] = False
        stats["mongodb_database"] = "N/A"
        db.close()

    stats["total_activities_logged"] = sum(stats[k] for k in table_keys)
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
    stats["masked_database_url"] = safe_summary["masked_database_url"]
    stats["env_file_loaded"] = safe_summary["env_file_loaded"]
    return stats


def _serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Serializes MongoDB document into JSON-safe dictionary, converting ObjectId to str."""
    clean = {}
    for k, v in doc.items():
        if k == "_id":
            clean["id"] = str(v)
        elif isinstance(v, datetime):
            clean[k] = v.isoformat()
        elif isinstance(v, dict):
            clean[k] = _serialize_mongo_doc(v)
        elif isinstance(v, list):
            clean[k] = [_serialize_mongo_doc(item) if isinstance(item, dict) else item for item in v]
        else:
            clean[k] = v
    return clean


def get_all_records(phase: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
    """
    Retrieves chronological activity records across all phases.
    Returns rich, nested JSON objects (either directly from MongoDB or parsed from SQLite).
    """
    init_database()
    db, db_type = get_db_connection()
    records = {
        "database_type": db_type,
        "phase1_recommendations": [],
        "phase2_smart_irrigation": [],
        "phase2_soil_fertilizer": [],
        "phase2_diagnoses": [],
        "phase3_marketplace_listings": [],
        "phase3_buyer_inquiries": []
    }

    if db_type == "mongodb":
        if phase in [None, "all", "1", "phase1"]:
            docs = db.phase1_recommendations.find().sort("timestamp", -1).limit(limit)
            records["phase1_recommendations"] = [_serialize_mongo_doc(d) for d in docs]

        if phase in [None, "all", "2", "phase2", "phase2_irr"]:
            docs = db.phase2_smart_irrigation.find().sort("timestamp", -1).limit(limit)
            records["phase2_smart_irrigation"] = [_serialize_mongo_doc(d) for d in docs]

        if phase in [None, "all", "2", "phase2", "phase2_soil"]:
            docs = db.phase2_soil_fertilizer.find().sort("timestamp", -1).limit(limit)
            records["phase2_soil_fertilizer"] = [_serialize_mongo_doc(d) for d in docs]

        if phase in [None, "all", "2", "phase2", "phase2_diag"]:
            docs = db.phase2_diagnoses.find().sort("timestamp", -1).limit(limit)
            records["phase2_diagnoses"] = [_serialize_mongo_doc(d) for d in docs]

        if phase in [None, "all", "3", "phase3"]:
            docs = db.phase3_marketplace_listings.find().sort("timestamp", -1).limit(limit)
            records["phase3_marketplace_listings"] = [_serialize_mongo_doc(d) for d in docs]

            docs_inq = db.phase3_buyer_inquiries.find().sort("timestamp", -1).limit(limit)
            records["phase3_buyer_inquiries"] = [_serialize_mongo_doc(d) for d in docs_inq]

        return records

    # SQLite retrieval with JSON parsing for uniform rich UI data
    cursor = db.cursor()

    if phase in [None, "all", "1", "phase1"]:
        cursor.execute(f"SELECT * FROM phase1_recommendations ORDER BY id DESC LIMIT {limit}")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            for json_field in ["top_5_suitable_crops", "top_3_profitable_crops", "all_candidate_economics"]:
                if r.get(json_field) and isinstance(r[json_field], str):
                    try:
                        r[json_field] = json.loads(r[json_field])
                    except Exception:
                        pass
        records["phase1_recommendations"] = rows

    if phase in [None, "all", "2", "phase2", "phase2_irr"]:
        cursor.execute(f"SELECT * FROM phase2_smart_irrigation ORDER BY id DESC LIMIT {limit}")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if r.get("output_advisory_json") and isinstance(r["output_advisory_json"], str):
                try:
                    r["advisory"] = json.loads(r["output_advisory_json"])
                except Exception:
                    pass
        records["phase2_smart_irrigation"] = rows

    if phase in [None, "all", "2", "phase2", "phase2_soil"]:
        cursor.execute(f"SELECT * FROM phase2_soil_fertilizer ORDER BY id DESC LIMIT {limit}")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            for json_field in ["output_soil_ratings_json", "output_chemical_bags_json", "output_organic_package_json", "output_full_json"]:
                if r.get(json_field) and isinstance(r[json_field], str):
                    try:
                        r[json_field] = json.loads(r[json_field])
                    except Exception:
                        pass
        records["phase2_soil_fertilizer"] = rows

    if phase in [None, "all", "2", "phase2", "phase2_diag"]:
        cursor.execute(f"SELECT * FROM phase2_diagnoses ORDER BY id DESC LIMIT {limit}")
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if r.get("output_full_json") and isinstance(r["output_full_json"], str):
                try:
                    r["full_diagnosis"] = json.loads(r["output_full_json"])
                except Exception:
                    pass
        records["phase2_diagnoses"] = rows

    if phase in [None, "all", "3", "phase3"]:
        cursor.execute(f"SELECT * FROM phase3_marketplace_listings ORDER BY id DESC LIMIT {limit}")
        records["phase3_marketplace_listings"] = [dict(r) for r in cursor.fetchall()]

        cursor.execute(f"SELECT * FROM phase3_buyer_inquiries ORDER BY id DESC LIMIT {limit}")
        records["phase3_buyer_inquiries"] = [dict(r) for r in cursor.fetchall()]

    db.close()
    return records
