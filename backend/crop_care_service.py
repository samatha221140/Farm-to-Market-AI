"""
Phase 2: Crop Growing Phase - Agronomic Care, Smart Irrigation, Fertilizer Dosage & Pest/Weed Advisory
"""

# Standard Recommended Dose of Fertilizer (RDF) in kg/acre for major crops (ICAR / ANGRAU benchmarks)
CROP_FERTILIZER_TARGETS = {
    "Bajra":        {"N": 32, "P": 16, "K": 16, "gypsum_kg": 0, "split_stages": ["Basal (At Sowing)", "Tillering Stage (25-30 DAS)"]},
    "Bengal Gram":  {"N": 10, "P": 20, "K": 10, "gypsum_kg": 0, "split_stages": ["Full Basal at Sowing"]},
    "Black Gram":   {"N": 10, "P": 20, "K": 10, "gypsum_kg": 0, "split_stages": ["Full Basal at Sowing"]},
    "Chilli":       {"N": 120, "P": 60, "K": 60, "gypsum_kg": 50, "split_stages": ["Basal (At Transplanting)", "Vegetative (30 DAS)", "Flowering (60 DAS)", "Fruit Development (90 DAS)"]},
    "Cotton":       {"N": 60, "P": 30, "K": 30, "gypsum_kg": 0, "split_stages": ["Basal Dose", "Square Formation (45 DAS)", "Boll Development (75 DAS)"]},
    "Green Gram":   {"N": 8, "P": 18, "K": 10, "gypsum_kg": 0, "split_stages": ["Full Basal at Sowing"]},
    "Groundnut":    {"N": 12, "P": 24, "K": 20, "gypsum_kg": 150, "split_stages": ["Basal Dose", "Pegging & Pod Filling (45 DAS - Apply Gypsum)"]},
    "Jowar":        {"N": 35, "P": 18, "K": 16, "gypsum_kg": 0, "split_stages": ["Basal Dose", "30-35 DAS (Knee-high Stage)"]},
    "Maize":        {"N": 50, "P": 24, "K": 20, "gypsum_kg": 0, "split_stages": ["Basal Dose", "Knee-high Stage (30 DAS)", "Tasseling Stage (55 DAS)"]},
    "Red Gram":     {"N": 10, "P": 22, "K": 12, "gypsum_kg": 0, "split_stages": ["Full Basal at Sowing"]},
    "Rice":         {"N": 48, "P": 24, "K": 24, "gypsum_kg": 0, "split_stages": ["Basal Dose", "Active Tillering (21 DAT)", "Panicle Initiation (42 DAT)"]},
    "Sugarcane":    {"N": 110, "P": 45, "K": 50, "gypsum_kg": 100, "split_stages": ["Basal (Planted Setts)", "Tillering (45-60 DAS)", "Grand Growth (90-120 DAS)"]},
}

# Crop Growth Stages and Irrigation Sensitivity
CROP_IRRIGATION_PROFILES = {
    "Rice": {
        "daily_water_mm": 7.0,
        "critical_stages": ["Transplanting", "Tillering", "Panicle Initiation", "Flowering", "Milking"],
        "method": "Shallow water ponding (2-5 cm) during vegetative to grain filling; drain 10 days before harvest.",
        "drought_tolerance": "Low"
    },
    "Sugarcane": {
        "daily_water_mm": 6.5,
        "critical_stages": ["Formative Phase (60-120 DAS)", "Grand Growth (120-270 DAS)"],
        "method": "Furrow irrigation every 7-10 days in summer, 12-15 days in winter.",
        "drought_tolerance": "Moderate"
    },
    "Chilli": {
        "daily_water_mm": 4.5,
        "critical_stages": ["Transplanting establishment", "Flowering", "Fruit Setting"],
        "method": "Drip irrigation or light furrows; avoid standing water to prevent wilting and root rot.",
        "drought_tolerance": "Moderate"
    },
    "Cotton": {
        "daily_water_mm": 4.8,
        "critical_stages": ["Squaring (45 DAS)", "Flowering & Boll formation (70-110 DAS)"],
        "method": "Alternate furrow or drip; excess water induces vegetative growth over boll formation.",
        "drought_tolerance": "High"
    },
    "Groundnut": {
        "daily_water_mm": 3.8,
        "critical_stages": ["Flowering (20-30 DAS)", "Peg Penetration (40-50 DAS)", "Pod Development (60-80 DAS)"],
        "method": "Sprinkler or light border strip; ensure optimum moisture during pegging for pod entry.",
        "drought_tolerance": "High"
    },
    "Maize": {
        "daily_water_mm": 5.0,
        "critical_stages": ["Tasseling (45-55 DAS)", "Silking (55-65 DAS)", "Grain Filling"],
        "method": "Furrow or drip; extreme sensitivity to water stress during silking and cob development.",
        "drought_tolerance": "Moderate"
    },
    "Black Gram": {
        "daily_water_mm": 2.8,
        "critical_stages": ["Flowering (30-35 DAS)", "Pod Filling (45-50 DAS)"],
        "method": "1-2 protective irrigations only if rain fails; highly susceptible to water stagnation.",
        "drought_tolerance": "High"
    },
    "Green Gram": {
        "daily_water_mm": 2.6,
        "critical_stages": ["Pre-flowering (25 DAS)", "Pod Development (40 DAS)"],
        "method": "Light protective watering; rainfed crop under most conditions.",
        "drought_tolerance": "High"
    },
    "Red Gram": {
        "daily_water_mm": 3.2,
        "critical_stages": ["Branching", "Flowering & Pod Filling (100-130 DAS)"],
        "method": "Deep rooted; needs 1 or 2 lifesaving irrigations during dry spells at flowering.",
        "drought_tolerance": "Very High"
    },
    "Bajra": {
        "daily_water_mm": 2.5,
        "critical_stages": ["Tillering (20-25 DAS)", "Booting & Flowering (40-45 DAS)"],
        "method": "Drought-hardy millet; 1 protective irrigation during flowering secures good grain yield.",
        "drought_tolerance": "Very High"
    },
    "Jowar": {
        "daily_water_mm": 3.0,
        "critical_stages": ["Booting Stage (45-50 DAS)", "Grain Filling (65-70 DAS)"],
        "method": "Furrow or rainfed; withstands moisture stress well.",
        "drought_tolerance": "Very High"
    },
    "Bengal Gram": {
        "daily_water_mm": 2.5,
        "critical_stages": ["Pre-flowering (30-35 DAS)", "Pod Development (55-60 DAS)"],
        "method": "Conserve residual moisture; 1 light irrigation at pod formation is beneficial.",
        "drought_tolerance": "High"
    },
}

# Common Pests, Diseases, and Weeds with Organic and Chemical Solutions
PEST_DISEASE_DB = {
    "Chilli": [
        {
            "category": "Pest",
            "name": "Chilli Thrips & Yellow Mites",
            "symptoms": "Upward or downward leaf curling, boat-shaped leaves, bronzing on leaf undersides.",
            "organic_remedy": "Neem oil spray (10,000 ppm) @ 3 ml/L or Pongamia oil spray @ 5 ml/L.",
            "chemical_control": "Fipronil 5% SC @ 2 ml/L or Diafenthiuron 50% WP @ 1.25 g/L."
        },
        {
            "category": "Disease",
            "name": "Anthracnose / Fruit Rot (Dieback)",
            "symptoms": "Circular sunken spots on ripe fruits with black concentric rings, drying of branch tips.",
            "organic_remedy": "Seed treatment with Trichoderma viride @ 10 g/kg seed; spray Pseudomonas fluorescens @ 5 g/L.",
            "chemical_control": "Azoxystrobin 23% SC @ 1 ml/L or Mancozeb 75% WP @ 2.5 g/L."
        },
        {
            "category": "Weed",
            "name": "Broadleaf Weeds & Sedges (Parthenium & Cyperus)",
            "symptoms": "Crowding young chilli seedlings, absorbing nutrients and shading.",
            "organic_remedy": "Organic straw mulching or manual hoeing at 20 & 45 days after transplanting.",
            "chemical_control": "Pendimethalin 38.7% CS @ 1.5 L/acre as pre-emergence within 48 hours of planting."
        }
    ],
    "Groundnut": [
        {
            "category": "Disease",
            "name": "Tikka Leaf Spot (Early & Late Cercospora)",
            "symptoms": "Brown to dark circular spots with bright yellow halo on leaves, premature leaf defoliation.",
            "organic_remedy": "Spray Panchagavya 3% or Neem seed kernel extract (NSKE 5%) twice at 15-day intervals.",
            "chemical_control": "Carbendazim 12% + Mancozeb 63% WP (Saaf) @ 2 g/L or Tebuconazole @ 1 ml/L."
        },
        {
            "category": "Pest",
            "name": "Red Hairy Caterpillar & Aphids",
            "symptoms": "Gregarious caterpillars devouring leaves leaving only midribs; aphids sucking tender shoots.",
            "organic_remedy": "Install light traps in field @ 1/acre; spray Bacillus thuringiensis (Bt) @ 2 g/L.",
            "chemical_control": "Chlorpyrifos 20% EC @ 2.5 ml/L or Imidacloprid 17.8% SL @ 0.5 ml/L."
        },
        {
            "category": "Weed",
            "name": "Bermuda Grass & Pigweed (Cynodon & Amaranthus)",
            "symptoms": "Mat-forming grass choking groundnut pegs from penetrating into soil.",
            "organic_remedy": "Two hand weedings at 20 and 40 DAS; avoid disturbing soil after pegging starts (45+ DAS).",
            "chemical_control": "Imazethapyr 10% SL @ 300 ml/acre at 15-20 days after sowing."
        }
    ],
    "Cotton": [
        {
            "category": "Pest",
            "name": "Pink Bollworm (Pectinophora gossypiella)",
            "symptoms": "Rosetted flowers ('rosette bloom'), boreholes plugged with frass in bolls, stained lint.",
            "organic_remedy": "Install Pheromone traps @ 8-10 traps/acre; release Trichogramma egg parasitoids @ 60,000/acre.",
            "chemical_control": "Profenofos 50% EC @ 2 ml/L or Emamectin Benzoate 5% SG @ 0.5 g/L."
        },
        {
            "category": "Pest",
            "name": "Whitefly & Sucking Pests",
            "symptoms": "Leaves crinkled and chlorotic; honeydew secretion with black sooty mold on foliage.",
            "organic_remedy": "Install Yellow Sticky Traps @ 15/acre; spray Fish oil rosin soap @ 20 g/L.",
            "chemical_control": "Spiromesifen 22.9% SC @ 1.2 ml/L or Flonicamid 50% WG @ 0.4 g/L."
        }
    ],
    "Rice": [
        {
            "category": "Pest",
            "name": "Brown Plant Hopper (BPH)",
            "symptoms": "Yellowing and drying of rice clumps in circular patches known as 'Hopper Burn'.",
            "organic_remedy": "Alternate wetting and drying (AWD); avoid excess nitrogen; preserve natural predatory spiders.",
            "chemical_control": "Pymetrozine 50% WG @ 0.6 g/L or Triflumezopyrim 10% SC @ 0.5 ml/L."
        },
        {
            "category": "Disease",
            "name": "Rice Blast (Pyricularia oryzae)",
            "symptoms": "Spindle-shaped spots with gray-white centers and reddish-brown margins on leaf blades and neck.",
            "organic_remedy": "Seed treatment with Pseudomonas fluorescens @ 10 g/kg; spray fermented cow urine + vitex decoction.",
            "chemical_control": "Tricyclazole 75% WP @ 0.6 g/L or Isoprothiolane 40% EC @ 1.5 ml/L."
        }
    ],
    "Default": [
        {
            "category": "Pest",
            "name": "Stem Borer & Leaf Eating Caterpillars",
            "symptoms": "Holes in stems, dead heart formation, skeletonized or eaten leaves.",
            "organic_remedy": "Install pheromone traps @ 5/acre; spray NSKE 5% or Bacillus thuringiensis (Bt) @ 2 g/L.",
            "chemical_control": "Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Emamectin Benzoate @ 0.4 g/L."
        },
        {
            "category": "Disease",
            "name": "Fungal Leaf Spot & Powdery Mildew",
            "symptoms": "White powdery patches or dark necrotic spots on upper/lower leaf surfaces.",
            "organic_remedy": "Spray sour butter milk (chaas) @ 50 ml/L or sulfur wettable powder @ 2 g/L.",
            "chemical_control": "Carbendazim 50% WP @ 1 g/L or Hexaconazole 5% EC @ 1 ml/L."
        },
        {
            "category": "Weed",
            "name": "Annual Grasses & Broadleaf Weeds",
            "symptoms": "Aggressive weed population reducing light and fertilizer uptake by crop.",
            "organic_remedy": "Early mechanical inter-cultivation or hand weeding at 18-22 days after emergence.",
            "chemical_control": "Early post-emergence broad-spectrum selective herbicide recommended by local RBK."
        }
    ]
}


def calculate_fertilizer_dosage(crop, soil_n, soil_p, soil_k, land_acres=1.0):
    """
    Calculate tailored fertilizer bags (Urea, DAP, MOP) based on soil test deficits and crop targets.
    Urea: 46% N
    DAP: 18% N, 46% P2O5
    MOP (Potash): 60% K2O
    """
    target = CROP_FERTILIZER_TARGETS.get(crop, {"N": 40, "P": 20, "K": 20, "gypsum_kg": 0, "split_stages": ["Basal", "Vegetative"]})
    
    # Soil nutrient status factor (Low, Medium, High)
    # If soil is rich in N/P/K, reduce recommended dose by 25%; if deficient, increase by 25%
    n_factor = 1.25 if soil_n < 30 else (0.75 if soil_n > 70 else 1.0)
    p_factor = 1.25 if soil_p < 25 else (0.75 if soil_p > 50 else 1.0)
    k_factor = 1.25 if soil_k < 30 else (0.75 if soil_k > 65 else 1.0)

    target_n = round(target["N"] * n_factor, 1)
    target_p = round(target["P"] * p_factor, 1)
    target_k = round(target["K"] * k_factor, 1)

    # Convert pure N, P, K into commercial fertilizer fertilizers (DAP, Urea, MOP)
    # 1. P is supplied by DAP (100 kg DAP contains 46 kg P2O5 and 18 kg N)
    dap_kg_acre = round((target_p / 0.46), 1)
    n_from_dap = round(dap_kg_acre * 0.18, 1)

    # 2. Remaining N is supplied by Urea (100 kg Urea contains 46 kg N)
    remaining_n = max(0.0, target_n - n_from_dap)
    urea_kg_acre = round((remaining_n / 0.46), 1)

    # 3. K is supplied by Muriate of Potash (MOP: 100 kg MOP contains 60 kg K2O)
    mop_kg_acre = round((target_k / 0.60), 1)

    # Convert to 50 kg bags for the whole farm acreage
    dap_bags_total = round((dap_kg_acre * land_acres) / 50.0, 1)
    urea_bags_total = round((urea_kg_acre * land_acres) / 50.0, 1)
    mop_bags_total = round((mop_kg_acre * land_acres) / 50.0, 1)
    gypsum_bags_total = round((target["gypsum_kg"] * land_acres) / 50.0, 1)

    return {
        "crop": crop,
        "land_acres": land_acres,
        "nutrient_targets_per_acre": {"N_kg": target_n, "P_kg": target_p, "K_kg": target_k},
        "per_acre_requirements": {
            "dap_kg": dap_kg_acre,
            "urea_kg": urea_kg_acre,
            "mop_kg": mop_kg_acre,
            "gypsum_kg": target["gypsum_kg"]
        },
        "total_farm_bags_50kg": {
            "dap_bags": dap_bags_total,
            "urea_bags": urea_bags_total,
            "mop_bags": mop_bags_total,
            "gypsum_bags": gypsum_bags_total
        },
        "application_schedule": target["split_stages"],
        "advisory": f"Apply all DAP and 1/3 of Urea + Potash as Basal dose at sowing. Top dress remaining Urea in 2 splits during active vegetative and flowering stages."
    }


def calculate_smart_irrigation(crop, soil_type, growth_stage, recent_rain_mm=0.0, temp_c=30.0, soil_moisture_pct=22.0, pump_rating="1.0 HP", irrigation_method="Drip Irrigation", forecast_rain_mm=0.0, acres=1.0):
    """
    Calculate smart irrigation water quantity, moisture status, and watering schedule.
    Uses IoT sensor soil moisture, rainfall deduction, and pump runtime calculation.
    """
    try:
        import smart_irrigation_service
        return smart_irrigation_service.compute_smart_irrigation_schedule(
            crop_name=crop,
            land_acres=acres,
            soil_type=soil_type,
            growth_stage=growth_stage,
            soil_moisture_pct=soil_moisture_pct,
            rainfall_today_mm=recent_rain_mm,
            forecast_rain_24h_mm=forecast_rain_mm,
            temperature_c=temp_c,
            pump_rating=pump_rating,
            irrigation_method=irrigation_method
        )
    except Exception as e:
        # Fallback to base calculation
        profile = CROP_IRRIGATION_PROFILES.get(crop, {
            "daily_water_mm": 4.0,
            "critical_stages": ["Flowering", "Yield Formation"],
            "method": "Ensure adequate soil moisture without water stagnation.",
            "drought_tolerance": "Moderate"
        })

        daily_need_mm = profile["daily_water_mm"]
        if temp_c > 32:
            daily_need_mm *= 1.2
        elif temp_c < 22:
            daily_need_mm *= 0.85

        daily_liters_per_acre = round(daily_need_mm * 4047)
        return {
            "crop": crop,
            "growth_stage": growth_stage,
            "daily_water_need_liters_per_acre": daily_liters_per_acre,
            "daily_water_need_mm": round(daily_need_mm, 1),
            "moisture_status": "Calculated",
            "action_advisory": "Irrigate root zone as per schedule.",
            "next_irrigation_in_days": 2
        }


def get_pest_weed_advisory(crop):
    """Return pest, disease, and weed management protocol for selected crop."""
    items = PEST_DISEASE_DB.get(crop, PEST_DISEASE_DB["Default"])
    return {
        "crop": crop,
        "diagnostics": items
    }
