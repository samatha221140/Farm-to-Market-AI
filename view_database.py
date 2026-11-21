"""
Farm-to-Market AI - Database Viewer CLI Utility
================================================
Quick interactive or command-line inspector to view all stored inputs,
physical image uploads, and AI outputs across Phase 1, Phase 2, and Phase 3.

Usage:
  python view_database.py              # Interactive menu or full summary
  python view_database.py --stats      # Row counts & file stats
  python view_database.py --phase 1    # View Phase 1 crop recommendations
  python view_database.py --phase 2    # View Phase 2 irrigation, soil & diagnoses
  python view_database.py --phase 3    # View Phase 3 marketplace & inquiries
  python view_database.py --uploads    # List physically saved images
"""

import sys
import json
import argparse
from pathlib import Path

# Add backend directory to path
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import config
import database


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)


def show_stats():
    print_header("Database System & Storage Summary")
    stats = database.get_database_stats()
    print(f"  Database Engine        : {stats.get('database_type', 'sqlite').upper()}")
    print(f"  Active Database Path   : {stats.get('db_file_path')}")
    print(f"  Database File Size     : {stats.get('db_file_size_kb')} KB")
    print(f"  Audit Stream Log       : {stats.get('audit_log_path')}")
    print(f"  Audit Log Size         : {stats.get('audit_log_size_kb')} KB")
    print(f"  Uploads Directory      : {stats.get('uploads_directory')}")
    print(f"  Saved Crop Photos      : {stats.get('saved_crop_photos_count')} images on disk")
    print(f"  Remote Cloud Connected : {stats.get('is_remote_connected')}")
    print(f"  Loaded Config File     : {stats.get('env_file_loaded') or 'System Environment'}")
    print("\n  Recorded Transaction Counts:")
    print(f"    - Phase 1 Crop Recommendations   : {stats.get('phase1_recommendations', 0)}")
    print(f"    - Phase 2 Smart Irrigation Logs  : {stats.get('phase2_smart_irrigation', 0)}")
    print(f"    - Phase 2 Soil & Fertilizer Logs : {stats.get('phase2_soil_fertilizer', 0)}")
    print(f"    - Phase 2 Crop Vision Diagnoses  : {stats.get('phase2_diagnoses', 0)}")
    print(f"    - Phase 3 Marketplace Listings   : {stats.get('phase3_marketplace_listings', 0)}")
    print(f"    - Phase 3 Buyer Inquiries        : {stats.get('phase3_buyer_inquiries', 0)}")
    print(f"    --------------------------------------------------")
    print(f"    Total Activities Logged          : {stats.get('total_activities_logged', 0)}\n")


def show_phase1(limit: int = 5):
    print_header(f"Phase 1: Crop Suitability & Profit Recommendations (Latest {limit})")
    records = database.get_all_records(phase="1", limit=limit).get("phase1_recommendations", [])
    if not records:
        print("  No Phase 1 records found.")
        return

    for r in records:
        print(f"\n[ID #{r['id']}] {r['timestamp']} | Acres: {r['input_land_acres']}")
        print(f"  Inputs  : N={r['input_n']}, P={r['input_p']}, K={r['input_k']}, pH={r['input_ph']}, Soil={r['input_soil_type']}, Water={r['input_water_availability']}, Season={r['input_season']}")
        try:
            top3 = json.loads(r.get("top_3_profitable_crops") or "[]")
            crops = [f"{c.get('crop')} (Net: Rs {c.get('expected_net_profit_rs', 0):,})" for c in top3]
            print(f"  Outputs : Top 3 Profitable -> {', '.join(crops)}")
        except Exception:
            print(f"  Outputs : {r.get('top_3_profitable_crops')}")


def show_phase2(limit: int = 5):
    print_header(f"Phase 2: Vision Diagnosis, Irrigation & Soil Health (Latest {limit})")
    data = database.get_all_records(phase="2", limit=limit)

    # 1. Vision Diagnoses (with uploaded photos)
    diags = data.get("phase2_diagnoses", [])
    print(f"\n--- Crop Vision Diagnoses ({len(diags)} shown) ---")
    if not diags:
        print("  No diagnosis records.")
    for d in diags:
        print(f"[ID #{d['id']}] {d['timestamp']} | Crop: {d['input_crop']} | Notes: {d.get('input_farmer_notes') or 'None'}")
        print(f"  Condition Diagnosed  : {d['output_condition']} ({d['output_category']}) - Confidence: {d['output_confidence_pct']}% | Severity: {d['output_severity']}")
        print(f"  Pathogen Species     : {d.get('output_pathogen') or 'N/A'}")
        print(f"  Saved Image File     : {d.get('image_filename')} ({d.get('image_size_bytes', 0):,} bytes)")
        print(f"  Image Server URL     : {d.get('image_url')}")
        print(f"  Organic Solution     : {str(d.get('output_organic_cure'))[:75]}...")
        print(f"  Chemical Solution    : {str(d.get('output_chemical_cure'))[:75]}...\n")

    # 2. Smart Irrigation
    irrs = data.get("phase2_smart_irrigation", [])
    print(f"\n--- Smart Irrigation & Pump Advisories ({len(irrs)} shown) ---")
    if not irrs:
        print("  No irrigation records.")
    for i in irrs:
        print(f"[ID #{i['id']}] {i['timestamp']} | Crop: {i['input_crop']} ({i['input_land_acres']} ac) | Moisture: {i['input_soil_moisture_pct']}% | Rain Today: {i['input_rainfall_today_mm']} mm")
        print(f"  Pump Action  : {i['output_pump_status']} | Runtime: {i['output_runtime_minutes']} mins | Water Needed: {i['output_water_needed_litres']} L | Power: {i['output_power_kwh']} kWh")
        print(f"  Advisory     : {i.get('output_summary')}\n")

    # 3. Soil Fertilizer
    soils = data.get("phase2_soil_fertilizer", [])
    print(f"\n--- Soil Tests & Dual Fertilizer Packages ({len(soils)} shown) ---")
    if not soils:
        print("  No soil fertilizer records.")
    for s in soils:
        print(f"[ID #{s['id']}] {s['timestamp']} | Crop: {s['input_crop']} ({s['input_acres']} ac) | Soil NPK: {s['input_soil_n']}/{s['input_soil_p']}/{s['input_soil_k']}, pH: {s['input_soil_ph']}")
        print(f"  Chemical Bags : {s.get('output_chemical_bags_json')}")
        print(f"  Organic Pkg   : {s.get('output_organic_package_json')}")
        print(f"  INM Advisory  : {s.get('output_schedule_inm')}\n")


def show_phase3(limit: int = 5):
    print_header(f"Phase 3: Farmer Marketplace & Buyer Inquiries (Latest {limit})")
    data = database.get_all_records(phase="3", limit=limit)

    listings = data.get("phase3_marketplace_listings", [])
    print(f"\n--- Farmer Harvest Produce Listings ({len(listings)} shown) ---")
    if not listings:
        print("  No produce listings.")
    for l in listings:
        print(f"[{l.get('listing_code')}] {l['timestamp']} | Farmer: {l['farmer_name']} ({l['phone_number']}) | Location: {l['village']}, {l['district']}")
        print(f"  Produce       : {l['crop']} ({l.get('variety') or 'Standard'}) - Grade: {l['quality_grade']}")
        print(f"  Quantity/Price: {l['quantity_quintals']} Qtl @ Rs {l['price_rs_per_quintal']:,}/Qtl | Est. Total Value: Rs {l.get('total_estimated_value_rs', 0):,}")
        print(f"  Lot Image URL : {l.get('produce_image_url') or 'None'}")
        print(f"  Status        : {l.get('status')}\n")

    inquiries = data.get("phase3_buyer_inquiries", [])
    print(f"\n--- Direct Buyer Inquiries ({len(inquiries)} shown) ---")
    if not inquiries:
        print("  No buyer inquiries.")
    for q in inquiries:
        print(f"[{q.get('inquiry_code')}] {q['timestamp']} | Buyer: {q['buyer_name']} ({q['buyer_phone']}) | APMC/City: {q.get('buyer_location')}")
        print(f"  Lot Reference : {q.get('listing_code')} | Crop: {q['crop']}")
        print(f"  Offer Details : {q.get('quantity_requested_quintals')} Qtl @ Rs {q.get('offered_price_rs_per_quintal', 0):,}/Qtl")
        print(f"  Buyer Message : \"{q.get('message')}\"")
        print(f"  Status        : {q.get('status')}\n")


def show_saved_uploads():
    print_header("Physically Saved Uploaded Crop & Marketplace Photos")
    upload_dir = config.UPLOAD_BASE_DIR
    diag_dir = config.DIAGNOSES_UPLOAD_DIR
    market_dir = config.MARKETPLACE_UPLOAD_DIR

    diag_files = sorted(diag_dir.glob("*.jpg"), key=lambda f: f.stat().st_mtime, reverse=True) if diag_dir.exists() else []
    market_files = sorted(market_dir.glob("*.jpg"), key=lambda f: f.stat().st_mtime, reverse=True) if market_dir.exists() else []

    print(f"  Upload Storage Root: {upload_dir}")
    print(f"\n  [Diagnoses Folder: {diag_dir}] ({len(diag_files)} photos)")
    for f in diag_files[:10]:
        size_kb = round(f.stat().st_size / 1024, 1)
        url = f"/uploads/diagnoses/{f.name}"
        print(f"    - {f.name} ({size_kb} KB) -> URL: {url}")

    print(f"\n  [Marketplace Folder: {market_dir}] ({len(market_files)} photos)")
    for f in market_files[:10]:
        size_kb = round(f.stat().st_size / 1024, 1)
        url = f"/uploads/marketplace/{f.name}"
        print(f"    - {f.name} ({size_kb} KB) -> URL: {url}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Farm-to-Market AI Database Inspector")
    parser.add_argument("--stats", action="store_true", help="Display storage and database statistics")
    parser.add_argument("--phase", choices=["1", "2", "3", "all"], help="Filter by Phase (1, 2, 3, or all)")
    parser.add_argument("--uploads", action="store_true", help="List physically saved upload photos")
    parser.add_argument("--limit", type=int, default=5, help="Number of latest records to display per table")

    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    if args.uploads:
        show_saved_uploads()
        return

    if args.phase:
        if args.phase in ["1", "all"]:
            show_phase1(limit=args.limit)
        if args.phase in ["2", "all"]:
            show_phase2(limit=args.limit)
        if args.phase in ["3", "all"]:
            show_phase3(limit=args.limit)
        return

    # Default if no arguments: show stats and recent activity across all phases
    show_stats()
    show_phase1(limit=3)
    show_phase2(limit=3)
    show_phase3(limit=3)
    show_saved_uploads()


if __name__ == "__main__":
    main()
