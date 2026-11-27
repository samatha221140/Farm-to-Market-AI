"""
view_database.py
Unified Database Inspector for Farm-to-Market AI.
Inspects both MongoDB and SQLite fallback storage, displaying live transaction counts,
model predictions, and saved crop image records.
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from backend import database, config


def print_header(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()}")
    print("=" * 80)


def show_stats():
    print_header("Database System & Storage Summary (MongoDB / Document Engine)")
    stats = database.get_database_stats()
    print(f"  Database Engine        : {stats.get('engine_name', 'MongoDB NoSQL')}")
    print(f"  MongoDB Active         : {stats.get('mongodb_connected', False)}")
    print(f"  MongoDB Database       : {stats.get('mongodb_database', 'N/A')}")
    print(f"  Configured URI         : {stats.get('masked_database_url', 'N/A')}")
    print(f"  Local Fallback Path    : {stats.get('db_file_path')}")
    print(f"  Local Fallback Size    : {stats.get('db_file_size_kb')} KB")
    print(f"  Audit Stream Log       : {stats.get('audit_log_path')}")
    print(f"  Audit Log Size         : {stats.get('audit_log_size_kb')} KB")
    print(f"  Uploads Directory      : {stats.get('uploads_directory')}")
    print(f"  Saved Crop Photos      : {stats.get('saved_crop_photos_count')} images on disk")
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
        rec_id = r.get("id") or r.get("_id")
        inputs = r.get("farm_inputs") or r
        acres = r.get("acres") or r.get("land_acres") or r.get("input_land_acres") or 1.0
        print(f"\n[ID #{rec_id}] {r.get('timestamp')} | Acres: {acres}")
        print(f"  Inputs  : N={inputs.get('N_kg_ha') or inputs.get('input_n')}, P={inputs.get('P_kg_ha') or inputs.get('input_p')}, K={inputs.get('K_kg_ha') or inputs.get('input_k')}, pH={inputs.get('pH') or inputs.get('input_ph')}, Soil={inputs.get('Soil_Type') or inputs.get('input_soil_type')}, Water={inputs.get('Water_Availability') or inputs.get('input_water_availability')}, Season={inputs.get('Season') or inputs.get('input_season')}")
        top3 = r.get("top_3_profitable_crops") or []
        if isinstance(top3, str):
            try:
                top3 = json.loads(top3)
            except Exception:
                pass
        if isinstance(top3, list) and top3:
            crops = []
            for c in top3:
                if isinstance(c, dict):
                    profit = c.get("net_profit_estimate") or c.get("expected_net_profit_rs") or c.get("total_net_profit_rs", 0)
                    crops.append(f"{c.get('crop')} (Net: Rs {profit:,.0f})")
            print(f"  Outputs : Top 3 Profitable -> {', '.join(crops)}")
        else:
            print(f"  Outputs : {top3}")


def show_phase2(limit: int = 5):
    print_header(f"Phase 2: Vision Diagnosis, Irrigation & Soil Health (Latest {limit})")
    data = database.get_all_records(phase="2", limit=limit)

    # 1. Vision Diagnoses (with uploaded photos)
    diags = data.get("phase2_diagnoses", [])
    print(f"\n--- Crop Vision Diagnoses ({len(diags)} shown) ---")
    if not diags:
        print("  No diagnosis records.")
    for d in diags:
        rec_id = d.get("id") or d.get("_id")
        img_meta = d.get("image_metadata") or {}
        treatments = d.get("treatment_protocols") or {}
        filename = img_meta.get("filename") or d.get("image_filename") or "None"
        filesize = img_meta.get("file_size_bytes") or d.get("image_size_bytes") or 0
        img_url = img_meta.get("server_url") or d.get("image_url") or "None"
        condition = d.get("condition_diagnosed") or d.get("condition") or d.get("output_condition") or "Healthy"
        confidence = d.get("confidence_score") or d.get("confidence_pct") or d.get("output_confidence_pct") or 0
        pathogen = d.get("pathogen_species") or d.get("pathogen") or d.get("output_pathogen") or "N/A"
        organic = treatments.get("organic_solution") or d.get("organic_cure") or d.get("output_organic_cure") or "None"
        chemical = treatments.get("chemical_solution") or d.get("chemical_cure") or d.get("output_chemical_cure") or "None"

        print(f"[ID #{rec_id}] {d.get('timestamp')} | Crop: {d.get('crop') or d.get('input_crop')} | Notes: {d.get('notes') or d.get('farmer_notes') or 'None'}")
        print(f"  Condition Diagnosed  : {condition} - Confidence: {confidence}% | Severity: {d.get('severity') or d.get('output_severity')}")
        print(f"  Pathogen Species     : {pathogen}")
        print(f"  Saved Image File     : {filename} ({filesize:,} bytes)")
        print(f"  Image Server URL     : {img_url}")
        print(f"  Organic Solution     : {str(organic)[:75]}...")
        print(f"  Chemical Solution    : {str(chemical)[:75]}...\n")

    # 2. Smart Irrigation
    irrs = data.get("phase2_smart_irrigation", [])
    print(f"\n--- Smart Irrigation & Pump Advisories ({len(irrs)} shown) ---")
    if not irrs:
        print("  No irrigation records.")
    for irr in irrs:
        rec_id = irr.get("id") or irr.get("_id")
        method = irr.get("irrigation_method") or irr.get("output_pump_status") or "N/A"
        litres = irr.get("water_needed_litres") or irr.get("output_water_needed_litres", 0)
        hours = irr.get("pump_duration_hours") or round((irr.get("output_runtime_minutes", 0) / 60), 1)
        note = irr.get("recommended_timing") or irr.get("output_summary") or "Standard Irrigation"
        print(f"[ID #{rec_id}] {irr.get('timestamp')} | Crop: {irr.get('crop') or irr.get('input_crop')} | Method: {method}")
        print(f"  Water Requirement   : {litres:,} Litres | Pump Run Time: {hours} Hours")
        print(f"  Advisory / Timing   : {note}\n")

    # 3. Soil Health & Fertilizer
    soils = data.get("phase2_soil_fertilizer", [])
    print(f"\n--- Soil Health & Fertilizer Packages ({len(soils)} shown) ---")
    if not soils:
        print("  No soil analysis records.")
    for s in soils:
        rec_id = s.get("id") or s.get("_id")
        inm = s.get("inm_guidance") or s.get("schedule_inm") or s.get("output_schedule_inm") or "Balanced NPK application"
        print(f"[ID #{rec_id}] {s.get('timestamp')} | Crop: {s.get('crop') or s.get('input_crop')} | Acres: {s.get('acres') or s.get('input_acres')}")
        print(f"  INM Guidance        : {str(inm)[:90]}...\n")


def show_phase3(limit: int = 5):
    print_header(f"Phase 3: Direct Marketplace Produce Lots & Inquiries (Latest {limit})")
    data = database.get_all_records(phase="3", limit=limit)

    listings = data.get("phase3_marketplace_listings", [])
    print(f"\n--- Published Harvest Lots ({len(listings)} shown) ---")
    if not listings:
        print("  No marketplace listings found.")
    for l in listings:
        lot_id = l.get("lot_id") or l.get("listing_code")
        farmer = l.get("farmer") or {}
        farmer_name = farmer.get("name") or l.get("farmer_name")
        phone = farmer.get("phone") or l.get("phone_number")
        village = farmer.get("village") or l.get("village")
        district = farmer.get("district") or l.get("district")
        price = l.get("expected_price_per_qtl") or l.get("price_rs_per_quintal")
        val = l.get("total_lot_value") or l.get("total_estimated_value_rs", 0)
        photos = l.get("photos") or []
        photo_url = photos[0] if (photos and isinstance(photos, list)) else (l.get("produce_image_url") or "None")

        print(f"[{lot_id}] Crop: {l.get('crop')} ({l.get('variety')}) | Grade: {l.get('quality_grade')}")
        print(f"  Quantity: {l.get('quantity_quintals')} Quintals | Price: Rs {price}/Qtl | Value: Rs {val:,}")
        print(f"  Farmer: {farmer_name} (Phone: {phone}) | Village: {village}, {district}")
        print(f"  Harvest Date: {l.get('harvest_date')} | Photo URL: {photo_url}\n")

    inquiries = data.get("phase3_buyer_inquiries", [])
    print(f"\n--- Buyer Direct Inquiries ({len(inquiries)} shown) ---")
    if not inquiries:
        print("  No buyer inquiries recorded.")
    for inq in inquiries:
        inq_id = inq.get("inquiry_id") or inq.get("inquiry_code")
        lot_id = inq.get("lot_id") or inq.get("listing_code")
        buyer = inq.get("buyer") or {}
        b_name = buyer.get("name") or inq.get("buyer_name")
        b_phone = buyer.get("phone") or inq.get("buyer_phone")
        b_loc = buyer.get("location") or inq.get("buyer_location")
        price = inq.get("offered_price_per_qtl") or inq.get("offered_price_rs_per_quintal")
        qty = inq.get("quantity_requested_quintals")

        print(f"[{inq_id}] Inquiring on Lot: {lot_id} | Crop: {inq.get('target_crop') or inq.get('crop')}")
        print(f"  Buyer: {b_name} (Phone: {b_phone}, {b_loc})")
        print(f"  Offer: Rs {price}/Qtl for {qty} Qtl")
        print(f"  Terms / Message: \"{inq.get('payment_terms') or inq.get('message')}\" | Status: {inq.get('status')}\n")


def show_uploads():
    print_header("Physically Saved Image Uploads Repository")
    diag_files = list(config.DIAGNOSES_UPLOAD_DIR.glob("*.jpg")) if config.DIAGNOSES_UPLOAD_DIR.exists() else []
    market_files = list(config.MARKETPLACE_UPLOAD_DIR.glob("*.jpg")) if config.MARKETPLACE_UPLOAD_DIR.exists() else []

    print(f"\n  [Crop Diagnoses Uploads: {len(diag_files)} files in {config.DIAGNOSES_UPLOAD_DIR}]")
    for f in diag_files[:10]:
        size_kb = round(f.stat().st_size / 1024, 1)
        print(f"    - {f.name} ({size_kb} KB)")
    if len(diag_files) > 10:
        print(f"      ... and {len(diag_files) - 10} more files")

    print(f"\n  [Marketplace Produce Uploads: {len(market_files)} files in {config.MARKETPLACE_UPLOAD_DIR}]")
    for f in market_files[:10]:
        size_kb = round(f.stat().st_size / 1024, 1)
        print(f"    - {f.name} ({size_kb} KB)")
    if len(market_files) > 10:
        print(f"      ... and {len(market_files) - 10} more files")
    print()


def main():
    parser = argparse.ArgumentParser(description="Farm-to-Market AI - Database & MongoDB Viewer")
    parser.add_argument("--stats", action="store_true", help="Show system database statistics")
    parser.add_argument("--phase", choices=["1", "2", "3", "all"], help="Filter by agricultural phase")
    parser.add_argument("--uploads", action="store_true", help="List physical image files stored on disk")
    parser.add_argument("--limit", type=int, default=5, help="Number of latest records to show")
    args = parser.parse_args()

    if args.stats:
        show_stats()
    elif args.uploads:
        show_uploads()
    elif args.phase == "1":
        show_phase1(args.limit)
    elif args.phase == "2":
        show_phase2(args.limit)
    elif args.phase == "3":
        show_phase3(args.limit)
    elif args.phase == "all":
        show_stats()
        show_phase1(args.limit)
        show_phase2(args.limit)
        show_phase3(args.limit)
        show_uploads()
    else:
        # Default full overview
        show_stats()
        show_phase1(3)
        show_phase2(3)
        show_phase3(3)
        show_uploads()
        print("[*] Tip: Run 'python view_database.py --help' to see specific filters.\n")


if __name__ == "__main__":
    main()
