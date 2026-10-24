"""
Phase 3: Selling Phase - Direct Farmer-to-Buyer Marketplace
Allows farmers to list harvested produce with photos, location, and price,
and enables buyers to view lots and connect directly with farmers.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).resolve().parent / "data" / "marketplace_listings.json"
INQUIRIES_FILE = Path(__file__).resolve().parent / "data" / "buyer_inquiries.json"

DEFAULT_LISTINGS = [
    {
        "id": "LOT-1001",
        "crop": "Chilli",
        "variety": "Teja / Guntur Sannam (Dry Red)",
        "quantity_quintals": 45.0,
        "asking_price_per_quintal": 19200.0,
        "quality_grade": "Grade A (Export Quality)",
        "harvest_date": "2026-10-18",
        "farmer_name": "K. Venkateswara Rao",
        "phone_number": "9848022334",
        "village": "Medikonduru",
        "district": "Guntur",
        "state": "Andhra Pradesh",
        "photo_url": "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80",
        "notes": "Naturally sun-dried on clean tarpaulins, moisture below 10%, deep red color.",
        "created_at": "2026-10-20T10:30:00"
    },
    {
        "id": "LOT-1002",
        "crop": "Groundnut",
        "variety": "K6 (Kadiri-6 Bold Pods)",
        "quantity_quintals": 60.0,
        "asking_price_per_quintal": 8400.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-10-22",
        "farmer_name": "B. Ramanjaneyulu",
        "phone_number": "9440156789",
        "village": "Kalyandurg Rural",
        "district": "Anantapur",
        "state": "Andhra Pradesh",
        "photo_url": "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?auto=format&fit=crop&w=600&q=80",
        "notes": "Freshly machine-threshed pods, clean without soil clods, high oil content.",
        "created_at": "2026-10-22T14:15:00"
    },
    {
        "id": "LOT-1003",
        "crop": "Cotton",
        "variety": "Bt Cotton (Medium Staple)",
        "quantity_quintals": 35.0,
        "asking_price_per_quintal": 8900.0,
        "quality_grade": "Grade A",
        "harvest_date": "2026-10-21",
        "farmer_name": "M. Subba Reddy",
        "phone_number": "9989045612",
        "village": "Rompicherla",
        "district": "Palnadu",
        "state": "Andhra Pradesh",
        "photo_url": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=600&q=80",
        "notes": "First picking cotton, zero yellow staining, clean hand-picked lint.",
        "created_at": "2026-10-21T09:00:00"
    },
    {
        "id": "LOT-1004",
        "crop": "Rice",
        "variety": "BPT 5204 (Samba Mahsuri)",
        "quantity_quintals": 120.0,
        "asking_price_per_quintal": 2900.0,
        "quality_grade": "Grade A (Fine Grain)",
        "harvest_date": "2026-10-19",
        "farmer_name": "Ch. Satyanarayana",
        "phone_number": "9866123450",
        "village": "Gudivada",
        "district": "Krishna",
        "state": "Andhra Pradesh",
        "photo_url": "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
        "notes": "Paddy bagged in 75 kg gunny bags, stored in covered warehouse, moisture 13%.",
        "created_at": "2026-10-23T11:45:00"
    },
    {
        "id": "LOT-1005",
        "crop": "Black Gram",
        "variety": "LBG 752 (Urad Dal)",
        "quantity_quintals": 25.0,
        "asking_price_per_quintal": 9800.0,
        "quality_grade": "Grade A Bold",
        "harvest_date": "2026-10-23",
        "farmer_name": "G. Mallikarjuna",
        "phone_number": "9701239874",
        "village": "Parchur",
        "district": "Bapatla",
        "state": "Andhra Pradesh",
        "photo_url": "https://images.unsplash.com/photo-1599940824399-b87987ceb72a?auto=format&fit=crop&w=600&q=80",
        "notes": "Cleaned and graded black gram, high protein content, ready for millers.",
        "created_at": "2026-10-23T16:20:00"
    }
]


def _load_listings():
    if not DATA_FILE.exists():
        _save_listings(DEFAULT_LISTINGS)
        return DEFAULT_LISTINGS
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else DEFAULT_LISTINGS
    except Exception:
        return DEFAULT_LISTINGS


def _save_listings(listings):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)


def get_all_listings(crop=None, district=None):
    listings = _load_listings()
    if crop:
        crop_clean = crop.strip().lower()
        listings = [item for item in listings if crop_clean in item["crop"].lower()]
    if district:
        dist_clean = district.strip().lower()
        listings = [item for item in listings if dist_clean in item.get("district", "").lower()]
    
    # Sort newest first
    listings.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return listings


def create_new_listing(payload):
    listings = _load_listings()
    new_id = f"LOT-{1000 + len(listings) + 1}"
    
    listing = {
        "id": new_id,
        "crop": str(payload.get("crop", "Produce")).strip(),
        "variety": str(payload.get("variety", "Standard Hybrid")).strip(),
        "quantity_quintals": float(payload.get("quantity_quintals", 10.0)),
        "asking_price_per_quintal": float(payload.get("asking_price_per_quintal", 3000.0)),
        "quality_grade": str(payload.get("quality_grade", "Grade A")).strip(),
        "harvest_date": str(payload.get("harvest_date", datetime.now().strftime("%Y-%m-%d"))).strip(),
        "farmer_name": str(payload.get("farmer_name", "Farmer")).strip(),
        "phone_number": str(payload.get("phone_number", "")).strip(),
        "village": str(payload.get("village", "")).strip(),
        "district": str(payload.get("district", "Andhra Pradesh")).strip(),
        "state": str(payload.get("state", "Andhra Pradesh")).strip(),
        "photo_url": str(payload.get("photo_url", "")).strip() or "https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80",
        "notes": str(payload.get("notes", "")).strip(),
        "created_at": datetime.now().isoformat()
    }

    listings.insert(0, listing)
    _save_listings(listings)
    return listing


def save_buyer_inquiry(inquiry):
    inquiries = []
    if INQUIRIES_FILE.exists():
        try:
            with open(INQUIRIES_FILE, "r", encoding="utf-8") as f:
                inquiries = json.load(f)
        except Exception:
            inquiries = []

    record = {
        "inquiry_id": f"INQ-{len(inquiries) + 1}",
        "listing_id": inquiry.get("listing_id"),
        "buyer_name": inquiry.get("buyer_name"),
        "buyer_phone": inquiry.get("buyer_phone"),
        "offer_price_per_quintal": inquiry.get("offer_price"),
        "quantity_needed": inquiry.get("quantity_needed"),
        "message": inquiry.get("message"),
        "timestamp": datetime.now().isoformat()
    }

    inquiries.insert(0, record)
    INQUIRIES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(INQUIRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(inquiries, f, indent=2)

    return record
