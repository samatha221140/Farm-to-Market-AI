"""
Smart Irrigation Service: IoT Sensor-Driven Irrigation & Pump Control Engine
Calculates real-time crop water requirements, root zone moisture deficit,
effective daily rainfall deduction, and precise water pump run-time in minutes.
"""

# Soil physical water constants by soil texture
# FC = Field Capacity (% vol), PWP = Permanent Wilting Point (% vol), Root Depth (cm)
SOIL_WATER_PROPERTIES = {
    "Sandy":       {"FC": 16.0, "PWP": 6.0,  "retention_days": 2.5, "percolation": "Very High"},
    "Red":         {"FC": 26.0, "PWP": 12.0, "retention_days": 4.0, "percolation": "Moderate to High"},
    "Loamy":       {"FC": 30.0, "PWP": 14.0, "retention_days": 5.0, "percolation": "Balanced / Ideal"},
    "Alluvial":    {"FC": 32.0, "PWP": 15.0, "retention_days": 6.0, "percolation": "Moderate"},
    "Black":       {"FC": 40.0, "PWP": 22.0, "retention_days": 8.0, "percolation": "Low / High Retentive"},
    "Clay":        {"FC": 38.0, "PWP": 20.0, "retention_days": 7.5, "percolation": "Low"}
}

# Crop Growth Stage Coefficients (Kc) and Water Sensitivities
CROP_STAGE_KC = {
    "Rice": {
        "Germination & Seedling": 0.90, "Vegetative & Tillering": 1.10,
        "Flowering & Panicle": 1.25, "Grain / Pod Filling": 1.15, "Maturity & Ripening": 0.85,
        "critical_stages": ["Tillering", "Panicle Initiation", "Flowering", "Milking"],
        "min_moisture_threshold": 45.0, "target_moisture": 75.0, "max_depth_cm": 30
    },
    "Chilli": {
        "Germination & Seedling": 0.50, "Vegetative & Tillering": 0.75,
        "Flowering & Fruit Setting": 1.05, "Fruit Development": 0.95, "Maturity & Ripening": 0.70,
        "critical_stages": ["Transplanting establishment", "Flowering", "Fruit Setting"],
        "min_moisture_threshold": 30.0, "target_moisture": 60.0, "max_depth_cm": 45
    },
    "Cotton": {
        "Germination & Seedling": 0.45, "Vegetative & Squaring": 0.75,
        "Flowering & Boll Formation": 1.15, "Boll Maturation": 0.85, "Maturity & Ripening": 0.60,
        "critical_stages": ["Square formation", "Flowering & Boll formation"],
        "min_moisture_threshold": 28.0, "target_moisture": 58.0, "max_depth_cm": 60
    },
    "Groundnut": {
        "Germination & Seedling": 0.40, "Vegetative & Tillering": 0.70,
        "Flowering & Pegging": 1.05, "Pod Development & Filling": 0.95, "Maturity & Ripening": 0.60,
        "critical_stages": ["Flowering", "Peg Penetration", "Pod Development"],
        "min_moisture_threshold": 28.0, "target_moisture": 55.0, "max_depth_cm": 50
    },
    "Maize": {
        "Germination & Seedling": 0.45, "Vegetative & Knee-High": 0.80,
        "Tasseling & Silking": 1.20, "Grain / Cob Filling": 1.05, "Maturity & Ripening": 0.65,
        "critical_stages": ["Tasseling", "Silking", "Grain Filling"],
        "min_moisture_threshold": 32.0, "target_moisture": 62.0, "max_depth_cm": 60
    },
    "Sugarcane": {
        "Germination & Tillering": 0.55, "Formative Phase": 0.95,
        "Grand Growth Phase": 1.25, "Ripening & Maturity": 0.75,
        "critical_stages": ["Formative phase", "Grand growth"],
        "min_moisture_threshold": 35.0, "target_moisture": 65.0, "max_depth_cm": 75
    },
    "Default": {
        "Germination & Seedling": 0.45, "Vegetative & Tillering": 0.75,
        "Flowering & Fruit Setting": 1.05, "Grain / Pod Filling": 0.90, "Maturity & Ripening": 0.65,
        "critical_stages": ["Flowering", "Yield formation"],
        "min_moisture_threshold": 30.0, "target_moisture": 60.0, "max_depth_cm": 50
    }
}

# Standard Farm Water Pumps Flow Rate in Litres per Minute (L/min)
PUMP_CAPACITY_LPM = {
    "0.5 HP": 75.0,     # ~4,500 L/hr
    "1.0 HP": 150.0,    # ~9,000 L/hr (Standard small farmer borewell)
    "2.0 HP": 300.0,    # ~18,000 L/hr
    "3.0 HP": 480.0,    # ~28,800 L/hr
    "5.0 HP": 800.0,    # ~48,000 L/hr (Large open well / canal lift)
    "7.5 HP": 1200.0    # ~72,000 L/hr
}

# Irrigation System Efficiencies
METHOD_EFFICIENCY = {
    "Drip Irrigation": 0.90,         # 90% water directly reaches root zone
    "Sprinkler Irrigation": 0.75,    # 75% efficiency (minor wind drift/evaporation)
    "Furrow / Flood Irrigation": 0.60 # 60% efficiency (conveyance & deep percolation losses)
}


def compute_smart_irrigation_schedule(
    crop_name="Groundnut",
    land_acres=2.0,
    soil_type="Red",
    growth_stage="Flowering & Pegging / Tasseling (35-65 DAS)",
    soil_moisture_pct=22.0,
    rainfall_today_mm=0.0,
    forecast_rain_24h_mm=0.0,
    temperature_c=31.0,
    humidity_pct=58.0,
    pump_rating="1.0 HP",
    irrigation_method="Drip Irrigation"
):
    """
    Computes exact water requirement, moisture deficit, pump runtime (minutes),
    and automated pump control recommendation.
    """
    soil_data = SOIL_WATER_PROPERTIES.get(soil_type, SOIL_WATER_PROPERTIES["Red"])
    fc = soil_data["FC"]
    pwp = soil_data["PWP"]

    # 1. Available Water Capacity (AWC) in the root zone
    crop_cfg = CROP_STAGE_KC.get(crop_name, CROP_STAGE_KC["Default"])
    root_depth_cm = crop_cfg.get("max_depth_cm", 50)

    # Determine Crop Kc
    kc = 1.0
    for stage_key, stage_kc in crop_cfg.items():
        if isinstance(stage_kc, (int, float)) and stage_key.lower()[:8] in growth_stage.lower():
            kc = stage_kc
            break
    if kc == 1.0 and "flowering" in growth_stage.lower():
        kc = 1.05

    # 2. Reference Evapotranspiration (ET0) using Hargreaves approximation
    # Higher temp and lower humidity increase ET0
    base_et0 = 4.2 + (max(0.0, temperature_c - 25.0) * 0.18) - (max(0.0, humidity_pct - 50.0) * 0.02)
    et0 = max(2.5, min(8.5, round(base_et0, 2)))

    # Crop Evapotranspiration (ETc) = ET0 * Kc
    etc_mm = round(et0 * kc, 2)

    # 3. Moisture Evaluation from Sensor Reading
    # Available Water Percentage: (Current - PWP) / (FC - PWP) * 100
    if soil_moisture_pct <= pwp:
        moisture_fraction = 0.0
        moisture_health = "Critical Wilt Stress (< PWP)"
        moisture_color = "danger"
    elif soil_moisture_pct >= fc:
        moisture_fraction = 1.0
        moisture_health = "Field Capacity / Saturated"
        moisture_color = "success"
    else:
        moisture_fraction = (soil_moisture_pct - pwp) / (fc - pwp)
        if moisture_fraction < 0.40:
            moisture_health = "Moisture Deficit (Dry Root Zone)"
            moisture_color = "warning"
        elif moisture_fraction <= 0.80:
            moisture_health = "Optimal Available Moisture"
            moisture_color = "success"
        else:
            moisture_health = "Well Watered"
            moisture_color = "info"

    target_moisture_pct = crop_cfg.get("target_moisture", 58.0)
    # Soil moisture deficit in volumetric % to reach 75% of Field Capacity
    deficit_pct = max(0.0, (fc * 0.80) - soil_moisture_pct)
    # Deficit in mm of water over effective root zone: (deficit% / 100) * root_depth_mm
    root_depth_mm = root_depth_cm * 10.0
    soil_deficit_mm = round((deficit_pct / 100.0) * root_depth_mm, 2)

    # 4. Effective Rainfall Deduction
    # Rain < 3mm mostly evaporates; rain > 3mm contributes ~80%
    if rainfall_today_mm > 3.0:
        eff_rain_today_mm = min(rainfall_today_mm * 0.85, rainfall_today_mm - 2.0)
    else:
        eff_rain_today_mm = 0.0

    # 5. Net Irrigation Requirement (mm)
    # If substantial rain is forecasted in next 24h (>15mm), deduct from urgent need
    anticipated_rain_credit = min(15.0, forecast_rain_24h_mm * 0.6)

    net_water_need_mm = max(0.0, (soil_deficit_mm + etc_mm) - eff_rain_today_mm - anticipated_rain_credit)
    net_water_need_mm = round(net_water_need_mm, 2)

    # 6. Gross Water Volume in Liters
    # 1 mm water over 1 acre = 4,047 Litres
    irrigation_efficiency = METHOD_EFFICIENCY.get(irrigation_method, 0.90)
    gross_water_liters_per_acre = round((net_water_need_mm * 4047.0) / irrigation_efficiency)
    total_water_liters = round(gross_water_liters_per_acre * land_acres)

    # 7. Pump Runtime Calculation
    pump_flow_lpm = PUMP_CAPACITY_LPM.get(pump_rating, 150.0)
    
    # Decision: Should pump run?
    # If rain today >= 25mm OR forecast rain >= 20mm OR soil is above 75% FC
    pump_needed = True
    delay_reason = None

    if rainfall_today_mm >= 25.0:
        pump_needed = False
        delay_reason = f"Heavy rainfall today ({rainfall_today_mm} mm) has satisfied root zone moisture."
    elif forecast_rain_24h_mm >= 20.0:
        pump_needed = False
        delay_reason = f"Forecast predicts {forecast_rain_24h_mm} mm rain in next 24h. Pump postponed to conserve electricity."
    elif soil_moisture_pct >= (fc * 0.85):
        pump_needed = False
        delay_reason = f"Soil moisture is at {soil_moisture_pct:.1f}% (adequate for {crop_name}). No irrigation required today."
    elif total_water_liters < 1000:
        pump_needed = False
        delay_reason = "Soil moisture is near optimal field capacity. Watering can wait for next scheduled cycle."

    if pump_needed and total_water_liters > 0:
        runtime_minutes = round(total_water_liters / pump_flow_lpm, 1)
        pump_status = "RUN PUMP"
        pump_state = "RECOMMENDED_ON"
        action_headline = f"Turn Water Pump ON for {int(runtime_minutes)} Minutes"
    else:
        runtime_minutes = 0.0
        pump_status = "KEEP PUMP OFF"
        pump_state = "OFF"
        total_water_liters = 0
        action_headline = delay_reason or "Keep Pump OFF. Soil moisture is currently adequate."

    # Estimated Electricity (kWh) = (HP * 0.746 / efficiency) * (minutes / 60)
    try:
        hp_val = float(pump_rating.split()[0])
    except Exception:
        hp_val = 1.0
    kwh_consumed = round((hp_val * 0.746 / 0.85) * (runtime_minutes / 60.0), 2)

    return {
        "success": True,
        "crop": crop_name,
        "land_acres": land_acres,
        "soil_type": soil_type,
        "growth_stage": growth_stage,
        "irrigation_method": irrigation_method,
        "irrigation_efficiency_pct": int(irrigation_efficiency * 100),
        "soil_water_status": {
            "sensor_moisture_pct": round(soil_moisture_pct, 1),
            "field_capacity_pct": fc,
            "permanent_wilting_point_pct": pwp,
            "available_water_pct": round(moisture_fraction * 100, 1),
            "moisture_health": moisture_health,
            "moisture_color": moisture_color,
            "root_depth_cm": root_depth_cm
        },
        "weather_factors": {
            "temperature_c": temperature_c,
            "humidity_pct": humidity_pct,
            "et0_evapotranspiration_mm_day": et0,
            "crop_coefficient_kc": round(kc, 2),
            "crop_etc_mm_day": etc_mm,
            "rainfall_today_mm": rainfall_today_mm,
            "effective_rain_today_mm": round(eff_rain_today_mm, 2),
            "forecast_rain_24h_mm": forecast_rain_24h_mm
        },
        "water_calculation": {
            "net_water_depth_mm": net_water_need_mm,
            "water_volume_liters_per_acre": gross_water_liters_per_acre,
            "total_water_liters": total_water_liters
        },
        "pump_operation": {
            "pump_rating": pump_rating,
            "pump_flow_rate_lpm": pump_flow_lpm,
            "pump_status": pump_status,
            "pump_state": pump_state,
            "runtime_minutes": runtime_minutes,
            "runtime_hours_str": f"{int(runtime_minutes // 60)}h {int(runtime_minutes % 60)}m" if runtime_minutes >= 60 else f"{int(runtime_minutes)} mins",
            "action_headline": action_headline,
            "estimated_kwh": kwh_consumed,
            "recommended_timing": "Early Morning (6:00 AM – 8:30 AM) or Evening (5:00 PM – 7:00 PM) to avoid daytime evaporation"
        }
    }


# In-memory store for active IoT Sensor telemetry and relay state
LIVE_SENSOR_DATA = {
    "N": 38.0,
    "P": 22.0,
    "K": 34.0,
    "pH": 6.8,
    "soil_moisture_pct": 21.5,
    "soil_temp_c": 27.2,
    "air_temp_c": 31.0,
    "air_humidity_pct": 58.0,
    "rainfall_today_mm": 0.0,
    "pump_relay_state": "OFF",
    "last_updated": "2026-11-04 15:00:00",
    "device_status": "Online (ESP32-MODBUS-SoilNode-1)"
}


def update_live_sensor_data(data):
    """Update sensor telemetry from IoT hardware or UI simulator."""
    import datetime
    global LIVE_SENSOR_DATA
    for key in ["N", "P", "K", "pH", "soil_moisture_pct", "soil_temp_c", "air_temp_c", "air_humidity_pct", "rainfall_today_mm"]:
        if key in data:
            try:
                LIVE_SENSOR_DATA[key] = float(data[key])
            except (ValueError, TypeError):
                pass
    if "pump_relay_state" in data:
        LIVE_SENSOR_DATA["pump_relay_state"] = "ON" if str(data["pump_relay_state"]).upper() in ["ON", "TRUE", "1"] else "OFF"
    LIVE_SENSOR_DATA["last_updated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return LIVE_SENSOR_DATA


def get_current_sensor_data():
    """Retrieve latest sensor readings."""
    return LIVE_SENSOR_DATA
