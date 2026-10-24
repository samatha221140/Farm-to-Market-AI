import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

# Setup project and rules paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
RULES_DIR = BACKEND_DIR / "rules"
DATA_DIR = BACKEND_DIR / "data"

if str(RULES_DIR) not in sys.path:
    sys.path.insert(0, str(RULES_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from crop_recommender import recommend_crops
from market_ranker import rank_crops_by_profit_and_market, load_market_data
from crop_rules import CROP_RULES
import crop_care_service
import marketplace_service
import vision_diagnostic_service
import soil_analyzer_service

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return jsonify({
        "project": "Farm-to-Market-AI: 3-Phase Smart Agricultural Ecosystem",
        "phases": {
            "phase_1": "Crop Recommendation (Agronomic Suitability + Profit Ranking)",
            "phase_2": "Crop Growing Care (Smart Irrigation, Fertilizer Dosage, Weed/Pest Diagnostics)",
            "phase_3": "Farm-to-Market Direct Marketplace (Produce Listing & Buyer Direct Connect)"
        },
        "endpoints": {
            "phase1_recommend": "POST /api/recommend",
            "phase2_fertilizer": "POST /api/phase2/fertilizer-plan",
            "phase2_irrigation": "POST /api/phase2/irrigation-advisory",
            "phase2_pest_weed": "GET /api/phase2/pest-weed-advisory?crop=Chilli",
            "phase3_listings": "GET /api/phase3/listings",
            "phase3_create_listing": "POST /api/phase3/create-listing",
            "phase3_inquiry": "POST /api/phase3/buyer-inquiry"
        }
    })


@app.get("/api/health")
def health():
    market_data = load_market_data()
    return jsonify({
        "status": "healthy",
        "phase_1_engine": "Agronomic Multi-Factor Suitability & Market Economics",
        "phase_2_engine": "ICAR/ANGRAU Fertilizer Dosage & Smart Irrigation Advisory",
        "phase_3_engine": "Farmer-to-Buyer Marketplace & Direct Connect",
        "crops_supported": list(CROP_RULES.keys()),
        "crops_count": len(CROP_RULES),
        "market_dataset_loaded": len(market_data) > 0
    })


# =========================================================================
# PHASE 1: CROP RECOMMENDATION & PROFIT RANKING
# =========================================================================

@app.post("/api/recommend")
def recommend_pipeline():
    """
    Phase 1 Two-stage recommendation pipeline:
    1. Recommends top 5 crops based on Water Availability, Weather (Temperature, Humidity, Rainfall),
       N, P, K, pH, and Soil Type.
    2. Then ranks and recommends top 3 crops based on Market Price and Estimated Net Profit.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "Expected JSON payload with farm conditions."
        }), 400

    farm = {
        "N_kg_ha": data.get("N_kg_ha") or data.get("N") or data.get("nitrogen"),
        "P_kg_ha": data.get("P_kg_ha") or data.get("P") or data.get("phosphorus"),
        "K_kg_ha": data.get("K_kg_ha") or data.get("K") or data.get("potassium"),
        "pH": data.get("pH") or data.get("ph"),
        "Temperature_C": data.get("Temperature_C") or data.get("temperature") or data.get("temp"),
        "Rainfall_mm": data.get("Rainfall_mm") or data.get("rainfall") or data.get("rain"),
        "Humidity_pct": data.get("Humidity_pct") or data.get("humidity") or 65.0,
        "Soil_Type": data.get("Soil_Type") or data.get("soil_type") or data.get("soil"),
        "Water_Availability": data.get("Water_Availability") or data.get("water_availability") or data.get("water"),
        "Season": data.get("Season") or data.get("season") or "Kharif",
    }

    land_acres = data.get("land_acres", 1.0)
    try:
        land_acres = float(land_acres)
        if land_acres <= 0:
            land_acres = 1.0
    except (ValueError, TypeError):
        land_acres = 1.0

    # Step 1: Recommend 5 crops based on water, weather, N, P, K, pH, soil type
    suitability_result = recommend_crops(farm, top_n=5)

    if suitability_result.get("errors"):
        return jsonify({
            "success": False,
            "errors": suitability_result["errors"],
            "message": "Input validation failed. Please check your farm parameters."
        }), 400

    top_5_suitable = suitability_result.get("recommendations", [])

    # Step 2: Rank top 3 crops based on profit and market price
    economic_result = rank_crops_by_profit_and_market(
        top_5_suitable,
        top_n=3,
        land_acres=land_acres
    )

    top_3_profitable = economic_result.get("top_three", [])

    return jsonify({
        "success": True,
        "farm_inputs": farm,
        "land_acres": land_acres,
        "step_1_description": "Top 5 crops recommended based on Water Availability, Weather (Temp/Rainfall/Humidity), N, P, K, pH, and Soil Type",
        "top_5_suitable_crops": top_5_suitable,
        "step_2_description": "Top 3 crops ranked by Market Price & Estimated Net Profit",
        "top_3_profitable_crops": top_3_profitable,
        "all_candidate_economics": economic_result.get("all_ranked_candidates", []),
        "warnings": suitability_result.get("warnings", []),
        "message": "Crop recommendation and market profit analysis completed successfully."
    })


@app.post("/api/profit-estimate")
def profit_estimate():
    """Interactive profit calculation for custom farmer scenarios."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid JSON input."}), 400

    try:
        modal_price = float(data.get("modal_price", 0))
        expected_yield = float(data.get("expected_yield_quintals", 0))
        cultivation_cost = float(data.get("cultivation_cost", 0))
        transport_cost = float(data.get("transport_cost", 0))
        other_costs = float(data.get("other_costs", 0))
        land_acres = float(data.get("land_acres", 1.0))
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "All financial fields must be numbers."}), 400

    if modal_price <= 0 or expected_yield <= 0:
        return jsonify({
            "success": False,
            "error": "Modal price and expected yield must be greater than zero."
        }), 400

    gross_revenue = expected_yield * modal_price
    total_costs = cultivation_cost + transport_cost + other_costs
    net_profit = gross_revenue - total_costs
    profit_per_quintal = round(net_profit / expected_yield, 2) if expected_yield > 0 else 0
    roi_pct = round((net_profit / total_costs) * 100, 1) if total_costs > 0 else 0

    return jsonify({
        "success": True,
        "modal_price_rs_per_quintal": modal_price,
        "expected_yield_quintals": expected_yield,
        "land_acres": land_acres,
        "gross_revenue_rs": gross_revenue,
        "cultivation_cost_rs": cultivation_cost,
        "transport_cost_rs": transport_cost,
        "other_costs_rs": other_costs,
        "total_cost_rs": total_costs,
        "estimated_net_profit_rs": net_profit,
        "estimated_profit_per_quintal_rs": profit_per_quintal,
        "roi_pct": roi_pct,
        "result_type": "Net Profit" if net_profit >= 0 else "Net Loss"
    })


@app.get("/api/mandi-prices")
def get_mandi_prices():
    crop_query = request.args.get("crop", "").strip()
    state_query = request.args.get("state", "Andhra Pradesh").strip()
    district_query = request.args.get("district", "").strip()

    market_db = load_market_data()
    records = []

    for key, item in market_db.items():
        if not crop_query or crop_query.lower() in item["crop"].lower() or item["crop"].lower() in crop_query.lower():
            records.append({
                "commodity_reported": item["crop"],
                "crop": item["crop"],
                "market": item["market"],
                "district": district_query or "Regional AP Market",
                "state": state_query,
                "modal_price_rs_per_quintal": item["price_rs_per_quintal"],
                "min_price_rs_per_quintal": round(item["price_rs_per_quintal"] * 0.92, 0),
                "max_price_rs_per_quintal": round(item["price_rs_per_quintal"] * 1.08, 0),
                "arrival_date": item.get("price_date") or "2026-10-23",
                "avg_yield_quintals_per_acre": item.get("avg_yield_quintals_per_acre", 10),
                "cultivation_cost_per_acre": item.get("cultivation_cost_per_acre", 20000),
                "data_type": item.get("data_type", "AP Mandi Report")
            })

    return jsonify({
        "success": True,
        "source": "Regional Agricultural Mandi Database (Andhra Pradesh)",
        "count": len(records),
        "records": records
    })


# =========================================================================
# PHASE 2: CROP GROWING & MONITORING
# =========================================================================

@app.post("/api/phase2/fertilizer-plan")
def phase2_fertilizer():
    """Calculates custom N-P-K fertilizer bags and schedule for the selected crop."""
    data = request.get_json(silent=True) or {}
    crop = data.get("crop", "Groundnut")
    soil_n = float(data.get("soil_n", 40.0))
    soil_p = float(data.get("soil_p", 25.0))
    soil_k = float(data.get("soil_k", 35.0))
    acres = float(data.get("acres", 1.0))

    plan = crop_care_service.calculate_fertilizer_dosage(crop, soil_n, soil_p, soil_k, acres)
    return jsonify({"success": True, "plan": plan})


@app.post("/api/phase2/irrigation-advisory")
def phase2_irrigation():
    """Calculates smart irrigation need, water volume, and schedule."""
    data = request.get_json(silent=True) or {}
    crop = data.get("crop", "Groundnut")
    soil_type = data.get("soil_type", "Red")
    growth_stage = data.get("growth_stage", "Vegetative / Tillering")
    recent_rain = float(data.get("recent_rain_mm", 0.0))
    temp_c = float(data.get("temperature", 30.0))

    advisory = crop_care_service.calculate_smart_irrigation(crop, soil_type, growth_stage, recent_rain, temp_c)
    return jsonify({"success": True, "advisory": advisory})


@app.get("/api/phase2/pest-weed-advisory")
def phase2_pest_weed():
    """Returns pest, weed, and disease prevention protocol for the crop."""
    crop = request.args.get("crop", "Groundnut").strip()
    advisory = crop_care_service.get_pest_weed_advisory(crop)
    return jsonify({"success": True, "advisory": advisory})


@app.post("/api/phase2/diagnose-image")
def phase2_diagnose_image():
    """Analyzes an uploaded crop photo to identify disease, pest, or weed with dual organic/chemical cures."""
    data = request.get_json(silent=True) or {}
    image_data = data.get("image_base64")
    crop = data.get("crop", "Chilli")
    notes = data.get("notes", "")

    if not image_data:
        return jsonify({"success": False, "error": "No image data received."}), 400

    result = vision_diagnostic_service.analyze_crop_image(image_data, crop_name=crop, user_notes=notes)
    return jsonify(result)


@app.post("/api/phase2/analyze-soil-fertilizer")
def phase2_analyze_soil_fertilizer():
    """Analyzes soil health test values and generates dual Organic and Chemical fertilizer packages."""
    data = request.get_json(silent=True) or {}
    crop = data.get("crop", "Groundnut")
    acres = float(data.get("acres", 1.0))
    soil_data = {
        "N": float(data.get("N", 45.0)),
        "P": float(data.get("P", 25.0)),
        "K": float(data.get("K", 35.0)),
        "pH": float(data.get("pH", 7.0)),
        "organic_carbon": float(data.get("organic_carbon", 0.55)),
        "ec": float(data.get("ec", 0.6)),
        "zinc": float(data.get("zinc", 0.55))
    }

    result = soil_analyzer_service.generate_fertilizer_recommendation(crop, soil_data, acres=acres)
    return jsonify(result)


# =========================================================================
# PHASE 3: SELLING & DIRECT FARM-TO-MARKET MARKETPLACE
# =========================================================================

@app.get("/api/phase3/listings")
def phase3_get_listings():
    crop = request.args.get("crop")
    district = request.args.get("district")
    listings = marketplace_service.get_all_listings(crop=crop, district=district)
    return jsonify({
        "success": True,
        "count": len(listings),
        "listings": listings
    })


@app.post("/api/phase3/create-listing")
def phase3_create_listing():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid listing data."}), 400

    if not data.get("crop") or not data.get("phone_number"):
        return jsonify({"success": False, "error": "Crop name and farmer contact number are required."}), 400

    listing = marketplace_service.create_new_listing(data)
    return jsonify({
        "success": True,
        "message": "Harvest lot published successfully to the marketplace!",
        "listing": listing
    })


@app.post("/api/phase3/buyer-inquiry")
def phase3_buyer_inquiry():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "Invalid inquiry data."}), 400

    record = marketplace_service.save_buyer_inquiry(data)
    return jsonify({
        "success": True,
        "message": "Inquiry delivered to farmer!",
        "inquiry": record
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
