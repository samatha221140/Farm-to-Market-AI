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

from crop_recommender import recommend_crops
from market_ranker import rank_crops_by_profit_and_market, load_market_data
from crop_rules import CROP_RULES

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return jsonify({
        "message": "Farm-to-Market-AI Backend is running",
        "endpoints": {
            "health": "/api/health",
            "recommend": "POST /api/recommend",
            "profit_estimate": "POST /api/profit-estimate",
            "mandi_prices": "GET /api/mandi-prices?crop=Rice&state=Andhra+Pradesh",
            "market_summary": "GET /api/market-summary"
        }
    })


@app.get("/api/health")
def health():
    market_data = load_market_data()
    return jsonify({
        "status": "healthy",
        "crops_supported": list(CROP_RULES.keys()),
        "crops_count": len(CROP_RULES),
        "market_dataset_loaded": len(market_data) > 0,
        "engine": "Agronomic Multi-Factor Suitability & Market Economics Engine"
    })


@app.post("/api/recommend")
def recommend_pipeline():
    """
    Two-stage recommendation pipeline:
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

    # Extract farm inputs with alias tolerance
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
        "result_type": "Net Profit" if net_profit >= 0 else "Net Loss",
        "warning": "Estimated returns depend on final realized market yield, transport expenses, and crop grade."
    })


@app.get("/api/mandi-prices")
def get_mandi_prices():
    """Retrieve market prices for specified crop and state."""
    crop_query = request.args.get("crop", "").strip()
    state_query = request.args.get("state", "Andhra Pradesh").strip()
    district_query = request.args.get("district", "").strip()

    # Try government API if configured
    api_key = os.getenv("DATA_GOV_IN_API_KEY") or os.getenv("DATA_GOV_API_KEY")
    if api_key:
        try:
            import mandi_service
            records = mandi_service.get_mandi_prices(crop_query, state=state_query, district=district_query)
            if records:
                return jsonify({
                    "success": True,
                    "source": "Government data.gov.in Live Mandi API",
                    "count": len(records),
                    "records": records
                })
        except Exception:
            pass

    # Seamless fallback to regional market database
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


@app.get("/api/market-summary")
def get_market_summary():
    """Return complete market and profit profiles for all supported crops."""
    market_db = load_market_data()
    crops = []
    for k, v in market_db.items():
        price = v["price_rs_per_quintal"]
        yield_val = v["avg_yield_quintals_per_acre"]
        cost = v["cultivation_cost_per_acre"]
        revenue = round(price * yield_val, 2)
        profit = round(revenue - cost, 2)
        roi = round((profit / cost) * 100, 1) if cost > 0 else 0
        crops.append({
            "crop": v["crop"],
            "market": v["market"],
            "price_rs_per_quintal": price,
            "avg_yield_quintals_per_acre": yield_val,
            "cultivation_cost_per_acre": cost,
            "gross_revenue_per_acre": revenue,
            "net_profit_per_acre": profit,
            "roi_pct": roi,
            "price_date": v.get("price_date", "")
        })

    crops.sort(key=lambda x: -x["net_profit_per_acre"])
    return jsonify({
        "success": True,
        "total_crops": len(crops),
        "crops": crops
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
