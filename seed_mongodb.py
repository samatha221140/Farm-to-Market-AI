"""
seed_mongodb.py
Populates the MongoDB database 'farm_to_market_ai' with structured agricultural
records across all 6 collections for instant inspection in MongoDB Compass & mongosh.
"""

import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath("."))
from backend import database, config
import pymongo

def run_seed():
    print("=" * 70)
    print("  SEEDING MONGODB DATABASE: farm_to_market_ai")
    print("=" * 70)

    client = pymongo.MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=2000)
    client.admin.command("ping")
    db = client[config.MONGODB_DB_NAME]
    print(f"[*] Successfully connected to MongoDB at {config.MONGODB_URI}")
    print(f"[*] Targeting database: '{config.MONGODB_DB_NAME}'\n")

    # 1. Phase 1 Recommendations
    p1_collection = db["phase1_recommendations"]
    p1_sample = [
        {
            "timestamp": "2026-11-27 10:15:00",
            "acres": 2.5,
            "farm_inputs": {
                "N_kg_ha": 45.0,
                "P_kg_ha": 25.0,
                "K_kg_ha": 35.0,
                "pH": 6.8,
                "Soil_Type": "Red Sandy Loam",
                "Water_Availability": "Medium",
                "Season": "Kharif",
                "Rainfall_mm": 680.0
            },
            "top_5_suitable_crops": [
                {"crop": "Groundnut", "suitability_score": 92.4, "status": "Highly Suitable"},
                {"crop": "Red Gram", "suitability_score": 88.1, "status": "Highly Suitable"},
                {"crop": "Chilli", "suitability_score": 84.7, "status": "Suitable"},
                {"crop": "Black Gram", "suitability_score": 81.3, "status": "Suitable"},
                {"crop": "Jowar", "suitability_score": 76.5, "status": "Moderately Suitable"}
            ],
            "top_3_profitable_crops": [
                {
                    "rank": 1,
                    "crop": "Red Gram (Pigeonpea)",
                    "estimated_yield_qtl_per_acre": 7.5,
                    "total_production_quintals": 18.75,
                    "market_price_per_qtl": 8500.0,
                    "gross_revenue": 159375.0,
                    "input_cost": 40625.0,
                    "net_profit_estimate": 118750.0,
                    "profit_margin_percent": 74.5
                },
                {
                    "rank": 2,
                    "crop": "Black Gram (Urad)",
                    "estimated_yield_qtl_per_acre": 6.0,
                    "total_production_quintals": 15.0,
                    "market_price_per_qtl": 9200.0,
                    "gross_revenue": 138000.0,
                    "input_cost": 34500.0,
                    "net_profit_estimate": 103500.0,
                    "profit_margin_percent": 75.0
                },
                {
                    "rank": 3,
                    "crop": "Chilli (Guntur Red)",
                    "estimated_yield_qtl_per_acre": 12.0,
                    "total_production_quintals": 30.0,
                    "market_price_per_qtl": 14500.0,
                    "gross_revenue": 435000.0,
                    "input_cost": 185000.0,
                    "net_profit_estimate": 250000.0,
                    "profit_margin_percent": 57.4
                }
            ]
        },
        {
            "timestamp": "2026-11-27 11:30:20",
            "acres": 4.0,
            "farm_inputs": {
                "N_kg_ha": 60.0,
                "P_kg_ha": 30.0,
                "K_kg_ha": 40.0,
                "pH": 7.2,
                "Soil_Type": "Black Cotton Soil",
                "Water_Availability": "High (Canal / Borewell)",
                "Season": "Rabi",
                "Rainfall_mm": 450.0
            },
            "top_5_suitable_crops": [
                {"crop": "Cotton", "suitability_score": 94.0, "status": "Highly Suitable"},
                {"crop": "Bengal Gram (Chickpea)", "suitability_score": 91.2, "status": "Highly Suitable"},
                {"crop": "Maize", "suitability_score": 87.5, "status": "Suitable"},
                {"crop": "Sunflower", "suitability_score": 82.0, "status": "Suitable"},
                {"crop": "Jowar", "suitability_score": 79.1, "status": "Suitable"}
            ],
            "top_3_profitable_crops": [
                {
                    "rank": 1,
                    "crop": "Bengal Gram (Desi Chickpea)",
                    "estimated_yield_qtl_per_acre": 8.0,
                    "total_production_quintals": 32.0,
                    "market_price_per_qtl": 6200.0,
                    "gross_revenue": 198400.0,
                    "input_cost": 52000.0,
                    "net_profit_estimate": 146400.0,
                    "profit_margin_percent": 73.8
                },
                {
                    "rank": 2,
                    "crop": "Cotton (Medium Staple)",
                    "estimated_yield_qtl_per_acre": 9.5,
                    "total_production_quintals": 38.0,
                    "market_price_per_qtl": 7400.0,
                    "gross_revenue": 281200.0,
                    "input_cost": 105000.0,
                    "net_profit_estimate": 176200.0,
                    "profit_margin_percent": 62.6
                },
                {
                    "rank": 3,
                    "crop": "Maize (Hybrid Grain)",
                    "estimated_yield_qtl_per_acre": 22.0,
                    "total_production_quintals": 88.0,
                    "market_price_per_qtl": 2350.0,
                    "gross_revenue": 206800.0,
                    "input_cost": 72000.0,
                    "net_profit_estimate": 134800.0,
                    "profit_margin_percent": 65.2
                }
            ]
        }
    ]
    p1_collection.delete_many({})
    p1_collection.insert_many(p1_sample)
    print(f"[+] phase1_recommendations: Inserted {len(p1_sample)} documents")

    # 2. Phase 2 Smart Irrigation
    p2_irrig = db["phase2_smart_irrigation"]
    p2_irrig_sample = [
        {
            "timestamp": "2026-11-27 08:30:00",
            "crop": "Chilli",
            "growth_stage": "Flowering & Fruit Setting (Day 55-80)",
            "soil_type": "Sandy Loam",
            "acres": 2.0,
            "evapotranspiration_et0_mm": 4.6,
            "crop_coefficient_kc": 1.05,
            "crop_evapotranspiration_etc_mm": 4.83,
            "soil_moisture_depletion_percent": 42.0,
            "effective_root_depth_cm": 45.0,
            "net_irrigation_requirement_mm": 18.5,
            "water_needed_litres": 148000,
            "irrigation_method": "Drip Irrigation (90% Application Efficiency)",
            "pump_capacity_hp": 5.0,
            "pump_flow_rate_lph": 25000,
            "pump_duration_hours": 6.5,
            "solar_pump_kw_recommended": 3.7,
            "recommended_timing": "Morning 06:00 - 09:30 AM or Evening 04:30 - 07:30 PM",
            "weather_forecast_note": "Clear sky, max temp 33 C, wind 8 km/h. High transpiration."
        },
        {
            "timestamp": "2026-11-27 09:00:00",
            "crop": "Groundnut",
            "growth_stage": "Pegging & Pod Development (Day 40-70)",
            "soil_type": "Red Loam",
            "acres": 3.0,
            "evapotranspiration_et0_mm": 4.2,
            "crop_coefficient_kc": 0.95,
            "crop_evapotranspiration_etc_mm": 3.99,
            "soil_moisture_depletion_percent": 50.0,
            "effective_root_depth_cm": 35.0,
            "net_irrigation_requirement_mm": 22.0,
            "water_needed_litres": 264000,
            "irrigation_method": "Sprinkler / Micro-Sprinkler",
            "pump_capacity_hp": 7.5,
            "pump_flow_rate_lph": 38000,
            "pump_duration_hours": 7.0,
            "solar_pump_kw_recommended": 5.5,
            "recommended_timing": "Early Morning 05:30 - 09:00 AM (avoid midday evaporation)",
            "weather_forecast_note": "No rainfall predicted for next 5 days. Critical pegging phase."
        }
    ]
    p2_irrig.delete_many({})
    p2_irrig.insert_many(p2_irrig_sample)
    print(f"[+] phase2_smart_irrigation: Inserted {len(p2_irrig_sample)} documents")

    # 3. Phase 2 Soil Health & Fertilizer
    p2_fert = db["phase2_soil_fertilizer"]
    p2_fert_sample = [
        {
            "timestamp": "2026-11-27 10:18:45",
            "crop": "Chilli",
            "acres": 2.1,
            "soil_test_values": {
                "nitrogen_status": "Low (165 kg/ha)",
                "phosphorus_status": "Medium (18 kg/ha)",
                "potassium_status": "High (290 kg/ha)",
                "soil_ph": 6.8,
                "organic_carbon_percent": 0.42
            },
            "chemical_schedule": {
                "urea_kg": 140,
                "dap_kg": 95,
                "mop_potash_kg": 40,
                "application_splits": [
                    {"stage": "Basal Application", "dose": "Full DAP (95 kg) + 35 kg Urea + 20 kg MOP at transplanting"},
                    {"stage": "Vegetative (30 DAT)", "dose": "35 kg Urea top dressed with light irrigation"},
                    {"stage": "Flowering (60 DAT)", "dose": "35 kg Urea + 20 kg MOP to boost fruit setting"},
                    {"stage": "Fruit Picking (90 DAT)", "dose": "35 kg Urea spray / top-dress after 1st flush"}
                ]
            },
            "organic_schedule": {
                "farm_yard_manure_tonnes": 4.2,
                "vermicompost_kg": 500,
                "biofertilizers": "Azospirillum + PSB (Phosphorus Solubilizing Bacteria) @ 2 kg/acre each"
            },
            "inm_guidance": "Apply 2 tonnes/acre of well-rotted FYM/compost + biofertilizers (Azospirillum + PSB) combined with neem cake 100 kg to suppress soil nematodes."
        }
    ]
    p2_fert.delete_many({})
    p2_fert.insert_many(p2_fert_sample)
    print(f"[+] phase2_soil_fertilizer: Inserted {len(p2_fert_sample)} documents")

    # 4. Phase 2 Disease Diagnoses
    p2_diag = db["phase2_diagnoses"]
    p2_diag_sample = [
        {
            "timestamp": "2026-11-27 10:18:35",
            "crop": "Chilli",
            "notes": "Spotted yellowish chlorotic patches and downy white fungal growth on undersides of lower leaves.",
            "condition_diagnosed": "Maize Downy Mildew / Chilli Cercospora Leaf Spot",
            "pathogen_species": "Cercospora capsici / Peronosclerospora",
            "confidence_score": 86.4,
            "severity": "Moderate",
            "image_metadata": {
                "filename": "diag_chilli_20261127_101835_9365b8aa.jpg",
                "file_size_bytes": 100291,
                "mime_type": "image/jpeg",
                "server_url": "/uploads/diagnoses/diag_chilli_20261127_101835_9365b8aa.jpg"
            },
            "treatment_protocols": {
                "organic_solution": "Foliar spray with Trichoderma viride / Pseudomonas fluorescens @ 5 g/litre of water; spray 5% Neem Seed Kernel Extract (NSKE) every 10 days.",
                "chemical_solution": "Spray Mancozeb 75% WP @ 2.5 g/litre or Copper Oxychloride 50% WP @ 3.0 g/litre; for systemic protection use Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/litre."
            }
        },
        {
            "timestamp": "2026-11-27 11:45:10",
            "crop": "Groundnut",
            "notes": "Circular dark brown spots with bright yellow halos on upper leaf surfaces.",
            "condition_diagnosed": "Tikka Leaf Spot (Early & Late Leaf Spot)",
            "pathogen_species": "Cercospora arachidicola & Phaeoisariopsis personata",
            "confidence_score": 93.8,
            "severity": "High",
            "image_metadata": {
                "filename": "diag_groundnut_tikka_sample.jpg",
                "file_size_bytes": 142050,
                "mime_type": "image/jpeg",
                "server_url": "/uploads/diagnoses/diag_groundnut_tikka_sample.jpg"
            },
            "treatment_protocols": {
                "organic_solution": "Spray Panchagavya @ 3% or fermented buttermilk spray (50 ml/L) mixed with ginger-garlic extract; rogue out heavily infested bottom leaves.",
                "chemical_solution": "Foliar spray with Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2 g/litre water; repeat spray after 14 days if humid conditions persist."
            }
        }
    ]
    p2_diag.delete_many({})
    p2_diag.insert_many(p2_diag_sample)
    print(f"[+] phase2_diagnoses: Inserted {len(p2_diag_sample)} documents")

    # 5. Phase 3 Marketplace Listings
    p3_listings = db["phase3_marketplace_listings"]
    p3_listings_sample = [
        {
            "lot_id": "LOT-1016",
            "crop": "Groundnut",
            "variety": "K-6 (Kadiri 6 High Oil Content)",
            "quality_grade": "Grade A (Premium / Export Quality)",
            "quantity_quintals": 25.0,
            "expected_price_per_qtl": 8400.0,
            "total_lot_value": 210000.0,
            "harvest_date": "2026-11-27",
            "moisture_content_percent": 7.8,
            "oil_content_percent": 49.5,
            "farmer": {
                "name": "R. Srinivasulu",
                "phone": "9848012345",
                "village": "Singanamala",
                "mandal": "Singanamala",
                "district": "Anantapur",
                "state": "Andhra Pradesh"
            },
            "photos": [
                "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?auto=format&fit=crop&w=600&q=80"
            ],
            "status": "Active (Available for Bidding)",
            "created_at": "2026-11-27 09:15:00"
        },
        {
            "lot_id": "LOT-1017",
            "crop": "Chilli",
            "variety": "Teja (LCA 334 High Pungency)",
            "quality_grade": "Grade A+ (Deep Red, Stalkless)",
            "quantity_quintals": 18.0,
            "expected_price_per_qtl": 19500.0,
            "total_lot_value": 351000.0,
            "harvest_date": "2026-11-25",
            "moisture_content_percent": 9.2,
            "shus_pungency_units": 65000,
            "farmer": {
                "name": "K. Venkata Rao",
                "phone": "9440198765",
                "village": "Medikonduru",
                "mandal": "Medikonduru",
                "district": "Guntur",
                "state": "Andhra Pradesh"
            },
            "photos": [
                "https://images.unsplash.com/photo-1588252303782-cb80119abd6d?auto=format&fit=crop&w=600&q=80"
            ],
            "status": "Active (Available for Bidding)",
            "created_at": "2026-11-27 10:45:00"
        },
        {
            "lot_id": "LOT-1018",
            "crop": "Red Gram (Pigeonpea)",
            "variety": "ICPL 87119 (Asha Disease-Resistant)",
            "quality_grade": "Grade A (Cleaned, Destoned)",
            "quantity_quintals": 40.0,
            "expected_price_per_qtl": 8800.0,
            "total_lot_value": 352000.0,
            "harvest_date": "2026-11-20",
            "moisture_content_percent": 10.5,
            "farmer": {
                "name": "M. Anjaneyulu",
                "phone": "9988776655",
                "village": "Dhone",
                "mandal": "Dhone",
                "district": "Kurnool",
                "state": "Andhra Pradesh"
            },
            "photos": [],
            "status": "Active (Available for Bidding)",
            "created_at": "2026-11-27 11:20:00"
        }
    ]
    p3_listings.delete_many({})
    p3_listings.insert_many(p3_listings_sample)
    print(f"[+] phase3_marketplace_listings: Inserted {len(p3_listings_sample)} documents")

    # 6. Phase 3 Buyer Inquiries
    p3_inquiries = db["phase3_buyer_inquiries"]
    p3_inquiries_sample = [
        {
            "inquiry_id": "INQ-5001",
            "lot_id": "LOT-1016",
            "target_crop": "Groundnut",
            "offered_price_per_qtl": 8300.0,
            "quantity_requested_quintals": 25.0,
            "total_deal_value": 207500.0,
            "buyer": {
                "name": "Sunil Agrawal",
                "phone": "9823055443",
                "company": "Kaveri Agro Industries Pvt Ltd",
                "buyer_type": "Institutional Miller / Oil Mill",
                "location": "Hyderabad, Telangana"
            },
            "delivery_terms": "Ex-Farm gate / Truck provided by buyer",
            "payment_terms": "Immediate RTGS upon weighing at warehouse",
            "status": "Under Review by Farmer",
            "timestamp": "2026-11-27 11:35:00"
        },
        {
            "inquiry_id": "INQ-5002",
            "lot_id": "LOT-1017",
            "target_crop": "Chilli (Teja)",
            "offered_price_per_qtl": 19200.0,
            "quantity_requested_quintals": 18.0,
            "total_deal_value": 345600.0,
            "buyer": {
                "name": "P. Ramesh Reddy",
                "phone": "9703411223",
                "company": "Spices Export Consortium",
                "buyer_type": "Export Aggregator",
                "location": "Guntur Yard, AP"
            },
            "delivery_terms": "Delivered to Guntur Spices Yard",
            "payment_terms": "50% Advance via UPI, 50% at yard inspection",
            "status": "Accepted by Farmer",
            "timestamp": "2026-11-27 11:50:00"
        }
    ]
    p3_inquiries.delete_many({})
    p3_inquiries.insert_many(p3_inquiries_sample)
    print(f"[+] phase3_buyer_inquiries: Inserted {len(p3_inquiries_sample)} documents")

    print("\n" + "=" * 70)
    print("  SEEDING COMPLETE! ALL 6 COLLECTIONS POPULATED SUCCESSFULLY")
    print("=" * 70)
    cols = db.list_collection_names()
    print(f"Collections now in '{config.MONGODB_DB_NAME}': {cols}\n")
    for c in cols:
        count = db[c].count_documents({})
        print(f"  - {c.ljust(35)} : {count} documents")
    print("=" * 70)

if __name__ == "__main__":
    run_seed()
