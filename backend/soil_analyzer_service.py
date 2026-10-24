"""
Soil Analyzer Service: Comprehensive Soil Health Card Analysis & Dual Fertilizer Recommendations
Takes soil laboratory test values (N, P, K, pH, Organic Carbon, Electrical Conductivity, Zinc)
and produces:
1. Complete 100% Organic & Bio-Fertilizer Formulation
2. Complete Chemical Fertilizer Formulation
3. Integrated Nutrient Management (INM) Package
4. Specific Soil Conditioning (Gypsum / Lime / Micronutrient zinc correction)
"""

# Crop Base Nutritional Demand (kg / acre)
CROP_NUTRIENT_DEMAND = {
    "Chilli":       {"N": 120, "P": 60, "K": 60, "type": "Cash Crop", "legume": False},
    "Groundnut":    {"N": 12, "P": 24, "K": 20, "type": "Oilseed / Legume", "legume": True},
    "Cotton":       {"N": 60, "P": 30, "K": 30, "type": "Cash Crop", "legume": False},
    "Rice":         {"N": 48, "P": 24, "K": 24, "type": "Cereal", "legume": False},
    "Maize":        {"N": 50, "P": 24, "K": 20, "type": "Cereal", "legume": False},
    "Black Gram":   {"N": 10, "P": 20, "K": 10, "type": "Pulse / Legume", "legume": True},
    "Green Gram":   {"N": 8, "P": 18, "K": 10, "type": "Pulse / Legume", "legume": True},
    "Bengal Gram":  {"N": 10, "P": 20, "K": 10, "type": "Pulse / Legume", "legume": True},
    "Red Gram":     {"N": 10, "P": 22, "K": 12, "type": "Pulse / Legume", "legume": True},
    "Bajra":        {"N": 32, "P": 16, "K": 16, "type": "Millet", "legume": False},
    "Jowar":        {"N": 35, "P": 18, "K": 16, "type": "Millet", "legume": False},
    "Sugarcane":    {"N": 110, "P": 45, "K": 50, "type": "Sugar Crop", "legume": False},
}


def evaluate_soil_health(soil_data):
    """Evaluate soil parameters according to Indian Council of Agricultural Research (ICAR) benchmarks."""
    n = float(soil_data.get("N", 45))
    p = float(soil_data.get("P", 25))
    k = float(soil_data.get("K", 35))
    ph = float(soil_data.get("pH", 7.0))
    oc = float(soil_data.get("organic_carbon", 0.55))
    ec = float(soil_data.get("ec", 0.6))
    zn = float(soil_data.get("zinc", 0.55))

    status = {}

    # Nitrogen
    if n < 30:
        status["nitrogen"] = {"rating": "Low / Deficient", "color": "danger", "note": "Deficient in available nitrogen; limits vegetative growth."}
    elif n <= 65:
        status["nitrogen"] = {"rating": "Medium / Optimal", "color": "success", "note": "Adequate nitrogen reserve."}
    else:
        status["nitrogen"] = {"rating": "High / Abundant", "color": "info", "note": "High nitrogen; avoid excessive nitrogenous fertilizers."}

    # Phosphorus
    if p < 20:
        status["phosphorus"] = {"rating": "Low / Deficient", "color": "danger", "note": "Low available P; root establishment will be sluggish."}
    elif p <= 45:
        status["phosphorus"] = {"rating": "Medium / Optimal", "color": "success", "note": "Good phosphorus availability."}
    else:
        status["phosphorus"] = {"rating": "High / Abundant", "color": "info", "note": "High phosphorus level."}

    # Potassium
    if k < 25:
        status["potassium"] = {"rating": "Low / Deficient", "color": "danger", "note": "Deficient potassium; plants will have weak stems and poor disease resistance."}
    elif k <= 55:
        status["potassium"] = {"rating": "Medium / Optimal", "color": "success", "note": "Sufficient potassium for grain/fruit development."}
    else:
        status["potassium"] = {"rating": "High / Abundant", "color": "info", "note": "Rich in exchangeable potassium."}

    # pH
    if ph < 6.0:
        status["ph"] = {"rating": "Acidic (pH < 6.0)", "color": "warning", "note": "Acidic soil fixes phosphorus and reduces nutrient uptake. Lime application recommended."}
    elif ph <= 7.8:
        status["ph"] = {"rating": "Neutral & Ideal (6.0 – 7.8)", "color": "success", "note": "Optimal pH for maximum nutrient availability."}
    elif ph <= 8.5:
        status["ph"] = {"rating": "Moderately Alkaline (7.8 – 8.5)", "color": "warning", "note": "Alkaline soil; trace elements (Zinc, Iron) become less available."}
    else:
        status["ph"] = {"rating": "Sodic / Highly Alkaline (> 8.5)", "color": "danger", "note": "High alkalinity and sodium hazards. Gypsum application mandatory."}

    # Organic Carbon (OC %)
    if oc < 0.5:
        status["organic_carbon"] = {"rating": "Low (< 0.5%)", "color": "danger", "note": "Poor soil biology and water holding capacity. Heavy organic manuring needed."}
    elif oc <= 0.75:
        status["organic_carbon"] = {"rating": "Medium (0.5 – 0.75%)", "color": "success", "note": "Fair organic matter content."}
    else:
        status["organic_carbon"] = {"rating": "High (> 0.75%)", "color": "success", "note": "Rich organic matter with active microbial ecosystem."}

    # Zinc (ppm)
    if zn < 0.6:
        status["zinc"] = {"rating": "Deficient (< 0.6 ppm)", "color": "danger", "note": "Zinc deficiency causes khaira disease in rice, little leaf in cotton/chilli."}
    else:
        status["zinc"] = {"rating": "Sufficient (>= 0.6 ppm)", "color": "success", "note": "Adequate micronutrient zinc."}

    return status


def generate_fertilizer_recommendation(crop_name, soil_data, acres=1.0):
    """
    Generate complete Organic, Chemical, and Integrated Fertilizer Packages based on soil test.
    """
    demand = CROP_NUTRIENT_DEMAND.get(crop_name, {"N": 40, "P": 20, "K": 20, "type": "Field Crop", "legume": False})
    
    n_val = float(soil_data.get("N", 45))
    p_val = float(soil_data.get("P", 25))
    k_val = float(soil_data.get("K", 35))
    ph_val = float(soil_data.get("pH", 7.0))
    oc_val = float(soil_data.get("organic_carbon", 0.55))
    zn_val = float(soil_data.get("zinc", 0.55))

    # Soil Health Status Rating
    health_status = evaluate_soil_health(soil_data)

    # Calculate nutrient adjustments based on soil status
    n_adj = 1.25 if n_val < 30 else (0.75 if n_val > 65 else 1.0)
    p_adj = 1.25 if p_val < 20 else (0.75 if p_val > 45 else 1.0)
    k_adj = 1.25 if k_val < 25 else (0.75 if k_val > 55 else 1.0)

    # If it is a legume (Groundnut, Black Gram, Red Gram), it fixes nitrogen naturally
    if demand["legume"]:
        n_adj *= 0.6  # Reduce chemical N requirement

    req_n_acre = round(demand["N"] * n_adj, 1)
    req_p_acre = round(demand["P"] * p_adj, 1)
    req_k_acre = round(demand["K"] * k_adj, 1)

    # -------------------------------------------------------------
    # 1. 100% ORGANIC & BIO-FERTILIZER PACKAGE
    # -------------------------------------------------------------
    # High organic carbon requirement if OC < 0.5%
    fym_tonnes_per_acre = 4.0 if oc_val < 0.5 else 2.5
    vermicompost_tonnes = 1.5 if oc_val < 0.5 else 1.0
    neem_cake_kg = 150 if demand["type"] == "Cash Crop" else 100

    bio_nitrogen = "Rhizobium culture @ 2 kg/acre" if demand["legume"] else "Azotobacter / Azospirillum biofertilizer @ 2 kg/acre"

    organic_package = {
        "title": "🌿 100% Organic & Bio-Nutrient Package",
        "description": "Restores soil microbial ecology, increases water retention, and eliminates chemical residues.",
        "components": [
            {
                "input": "Well-Decomposed Farmyard Manure (FYM)",
                "per_acre": f"{fym_tonnes_per_acre} Tonnes / acre",
                "total_farm": f"{round(fym_tonnes_per_acre * acres, 1)} Tonnes for {acres} Acres",
                "timing": "Incorporate during last plowing 15-20 days before sowing."
            },
            {
                "input": "Enriched Vermicompost",
                "per_acre": f"{vermicompost_tonnes} Tonnes / acre",
                "total_farm": f"{round(vermicompost_tonnes * acres, 1)} Tonnes for {acres} Acres",
                "timing": "Apply in seed furrows at the time of sowing/transplanting."
            },
            {
                "input": "Neem Cake (De-oiled)",
                "per_acre": f"{neem_cake_kg} kg / acre",
                "total_farm": f"{round(neem_cake_kg * acres, 1)} kg for {acres} Acres",
                "timing": "Basal application; inhibits nitrification and repels soil termites/nematodes."
            },
            {
                "input": "Nitrogen-Fixing Biofertilizer",
                "per_acre": bio_nitrogen,
                "total_farm": f"{round(2 * acres, 1)} kg for {acres} Acres",
                "timing": "Seed treatment (slurry with jaggery water) or mix with moist compost and broadcast."
            },
            {
                "input": "Phosphate Solubilizing Bacteria (PSB) & VAM",
                "per_acre": "PSB culture @ 2 kg/acre + VAM @ 5 kg/acre",
                "total_farm": f"{round(2 * acres, 1)} kg PSB for {acres} Acres",
                "timing": "Converts insoluble native soil phosphorus into plant-available orthophosphate."
            },
            {
                "input": "Liquid Bio-stimulants (Jeevamrutham / Panchagavya)",
                "per_acre": "200 Liters Jeevamrutham OR 3% Panchagavya (6 L/acre)",
                "total_farm": f"{int(200 * acres)} Liters per irrigation cycle",
                "timing": "Apply with irrigation water at 21, 45, and 65 days after sowing."
            }
        ]
    }

    # -------------------------------------------------------------
    # 2. CHEMICAL FERTILIZER PACKAGE
    # -------------------------------------------------------------
    # P from DAP (18-46-0)
    dap_kg_acre = round(req_p_acre / 0.46, 1)
    n_from_dap = round(dap_kg_acre * 0.18, 1)
    
    # Remaining N from Urea (46% N)
    rem_n = max(0.0, req_n_acre - n_from_dap)
    urea_kg_acre = round(rem_n / 0.46, 1)

    # K from Muriate of Potash (MOP: 60% K2O)
    mop_kg_acre = round(req_k_acre / 0.60, 1)

    dap_bags = round((dap_kg_acre * acres) / 50.0, 1)
    urea_bags = round((urea_kg_acre * acres) / 50.0, 1)
    mop_bags = round((mop_kg_acre * acres) / 50.0, 1)

    # Zinc sulfate if deficient
    zn_kg_acre = 10.0 if zn_val < 0.6 else 0.0

    # Soil conditioners (Gypsum for alkaline, Lime for acidic)
    conditioner_note = None
    if ph_val > 8.0:
        conditioner_note = f"Alkaline Soil Amendment: Apply Agricultural Gypsum @ {int(200 * acres)} kg ({int(4 * acres)} bags) to neutralize sodium salts and improve water percolation."
    elif ph_val < 6.0:
        conditioner_note = f"Acid Soil Amendment: Apply Agricultural Lime / Dolomite @ {int(150 * acres)} kg to raise soil pH and prevent phosphorus fixation."

    chemical_package = {
        "title": "🧪 Chemical Fertilizer Precision Package",
        "description": "Calculated to fulfill exact nutritional deficits through commercial fertilizers.",
        "bag_summary": {
            "dap_50kg_bags": dap_bags,
            "urea_50kg_bags": urea_bags,
            "mop_50kg_bags": mop_bags,
            "zinc_sulfate_kg": round(zn_kg_acre * acres, 1)
        },
        "components": [
            {
                "fertilizer": "Di-Ammonium Phosphate (DAP 18-46-0)",
                "quantity": f"{dap_bags} Bags ({round(dap_kg_acre * acres, 1)} kg for {acres} Acres)",
                "dose_rate": f"{dap_kg_acre} kg / acre",
                "stage": "100% as Basal dose at the time of sowing/planting."
            },
            {
                "fertilizer": "Urea (46% Nitrogen)",
                "quantity": f"{urea_bags} Bags ({round(urea_kg_acre * acres, 1)} kg for {acres} Acres)",
                "dose_rate": f"{urea_kg_acre} kg / acre",
                "stage": "Split application: 1/3 at basal, 1/3 at active tillering (30 DAS), 1/3 at flowering."
            },
            {
                "fertilizer": "Muriate of Potash (MOP 60% K₂O)",
                "quantity": f"{mop_bags} Bags ({round(mop_kg_acre * acres, 1)} kg for {acres} Acres)",
                "dose_rate": f"{mop_kg_acre} kg / acre",
                "stage": "Apply 50% basal and 50% at flowering/grain formation."
            }
        ]
    }

    if zn_kg_acre > 0:
        chemical_package["components"].append({
            "fertilizer": "Zinc Sulfate Heptahydrate (ZnSO₄ 21%)",
            "quantity": f"{round(zn_kg_acre * acres, 1)} kg for {acres} Acres",
            "dose_rate": f"{zn_kg_acre} kg / acre",
            "stage": "Basal broadcast; DO NOT mix directly with DAP to avoid zinc-phosphate precipitation."
        })

    # -------------------------------------------------------------
    # 3. INTEGRATED NUTRIENT MANAGEMENT (INM - BEST ECO-YIELD)
    # -------------------------------------------------------------
    inm_summary = (
        f"Apply 2 tonnes/acre of FYM/compost + biofertilizers (Azotobacter/Rhizobium + PSB) "
        f"combined with 75% of the recommended chemical dose ({round(dap_bags * 0.75, 1)} bags DAP, "
        f"{round(urea_bags * 0.75, 1)} bags Urea, {round(mop_bags * 0.75, 1)} bags Potash). "
        f"This yields highest crop productivity while preventing soil exhaustion."
    )

    return {
        "success": True,
        "crop": crop_name,
        "land_acres": acres,
        "soil_health_ratings": health_status,
        "soil_conditioner_advisory": conditioner_note,
        "organic_package": organic_package,
        "chemical_package": chemical_package,
        "integrated_nutrient_management": inm_summary
    }
