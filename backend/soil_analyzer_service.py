"""
Soil Analyzer Service: ICAR/ANGRAU Soil Test Crop Response (STCR) Engine
Produces precision fertilizer dosage (Urea, DAP, MOP, Zinc, Gypsum),
100% Organic Bio-nutrient package, and Integrated Nutrient Management (INM).
"""

# ICAR / ANGRAU Recommended Dose of Fertilizers (RDF) in kg / acre
CROP_FERTILIZER_NORMS = {
    "Chilli": {
        "N": 50.0, "P": 25.0, "K": 25.0, "type": "Cash Crop (Solanaceous)", "legume": False,
        "calcium_demand": "Moderate", "gypsum_kg_acre": 50.0,
        "splits": [
            {"stage": "Basal (At Transplanting)", "urea_pct": 25, "dap_pct": 100, "mop_pct": 50},
            {"stage": "Vegetative Branching (30 DAT)", "urea_pct": 25, "dap_pct": 0, "mop_pct": 0},
            {"stage": "Flowering & Fruit Initiation (60 DAT)", "urea_pct": 25, "dap_pct": 0, "mop_pct": 25},
            {"stage": "Peak Picking / Fruit Expansion (90 DAT)", "urea_pct": 25, "dap_pct": 0, "mop_pct": 25}
        ]
    },
    "Groundnut": {
        "N": 10.0, "P": 20.0, "K": 18.0, "type": "Oilseed / Legume", "legume": True,
        "calcium_demand": "Very High", "gypsum_kg_acre": 150.0,
        "splits": [
            {"stage": "Basal (At Sowing)", "urea_pct": 100, "dap_pct": 100, "mop_pct": 100},
            {"stage": "Peg Penetration & Pod Formation (40-45 DAS)", "urea_pct": 0, "dap_pct": 0, "mop_pct": 0, "gypsum_pct": 100}
        ]
    },
    "Cotton": {
        "N": 50.0, "P": 25.0, "K": 25.0, "type": "Commercial Fiber", "legume": False,
        "calcium_demand": "Moderate", "gypsum_kg_acre": 0.0,
        "splits": [
            {"stage": "Basal (At Sowing)", "urea_pct": 20, "dap_pct": 100, "mop_pct": 50},
            {"stage": "Square Formation (45 DAS)", "urea_pct": 40, "dap_pct": 0, "mop_pct": 25},
            {"stage": "Boll Development (75 DAS)", "urea_pct": 40, "dap_pct": 0, "mop_pct": 25}
        ]
    },
    "Rice": {
        "N": 48.0, "P": 24.0, "K": 20.0, "type": "Cereal (Paddy)", "legume": False,
        "calcium_demand": "Low", "gypsum_kg_acre": 0.0,
        "splits": [
            {"stage": "Basal (Last Puddling)", "urea_pct": 33, "dap_pct": 100, "mop_pct": 50},
            {"stage": "Active Tillering (21-25 DAT)", "urea_pct": 33, "dap_pct": 0, "mop_pct": 0},
            {"stage": "Panicle Initiation (40-45 DAT)", "urea_pct": 34, "dap_pct": 0, "mop_pct": 50}
        ]
    },
    "Maize": {
        "N": 50.0, "P": 24.0, "K": 20.0, "type": "Cereal Feed", "legume": False,
        "calcium_demand": "Low", "gypsum_kg_acre": 0.0,
        "splits": [
            {"stage": "Basal (At Sowing)", "urea_pct": 25, "dap_pct": 100, "mop_pct": 50},
            {"stage": "Knee-High Stage (30 DAS)", "urea_pct": 50, "dap_pct": 0, "mop_pct": 0},
            {"stage": "Tasseling & Silking (55 DAS)", "urea_pct": 25, "dap_pct": 0, "mop_pct": 50}
        ]
    },
    "Sugarcane": {
        "N": 100.0, "P": 40.0, "K": 48.0, "type": "Sugar Crop", "legume": False,
        "calcium_demand": "High", "gypsum_kg_acre": 100.0,
        "splits": [
            {"stage": "Basal (Planted Setts)", "urea_pct": 20, "dap_pct": 100, "mop_pct": 33},
            {"stage": "Tillering Phase (45 DAS)", "urea_pct": 40, "dap_pct": 0, "mop_pct": 33},
            {"stage": "Grand Growth (90-100 DAS)", "urea_pct": 40, "dap_pct": 0, "mop_pct": 34}
        ]
    },
    "Black Gram": {
        "N": 8.0, "P": 20.0, "K": 10.0, "type": "Pulse / Legume", "legume": True,
        "calcium_demand": "Low", "gypsum_kg_acre": 0.0,
        "splits": [{"stage": "Full Basal at Sowing", "urea_pct": 100, "dap_pct": 100, "mop_pct": 100}]
    },
    "Red Gram": {
        "N": 10.0, "P": 22.0, "K": 12.0, "type": "Pulse / Legume", "legume": True,
        "calcium_demand": "Moderate", "gypsum_kg_acre": 50.0,
        "splits": [{"stage": "Full Basal at Sowing", "urea_pct": 100, "dap_pct": 100, "mop_pct": 100}]
    },
    "Default": {
        "N": 40.0, "P": 20.0, "K": 20.0, "type": "Field Crop", "legume": False,
        "calcium_demand": "Low", "gypsum_kg_acre": 0.0,
        "splits": [
            {"stage": "Basal at Sowing", "urea_pct": 50, "dap_pct": 100, "mop_pct": 50},
            {"stage": "Vegetative / Flowering", "urea_pct": 50, "dap_pct": 0, "mop_pct": 50}
        ]
    }
}


def evaluate_soil_health(soil_data):
    """
    Evaluates soil parameters according to Indian Council of Agricultural Research (ICAR) benchmarks.
    """
    n = float(soil_data.get("N", 45))
    p = float(soil_data.get("P", 25))
    k = float(soil_data.get("K", 35))
    ph = float(soil_data.get("pH", 7.0))
    oc = float(soil_data.get("organic_carbon", 0.55))
    ec = float(soil_data.get("ec", 0.6))
    zn = float(soil_data.get("zinc", 0.55))

    status = {}

    # Nitrogen (kg/ha)
    if n < 30:
        status["nitrogen"] = {"rating": "Low / Deficient", "color": "danger", "note": "Low available N (<30 kg/ha). Stunts plant vegetative vigor."}
    elif n <= 65:
        status["nitrogen"] = {"rating": "Medium / Optimal", "color": "success", "note": "Balanced nitrogen reserve."}
    else:
        status["nitrogen"] = {"rating": "High / Abundant", "color": "info", "note": "High nitrogen reserve; chemical N fertilizer should be scaled down."}

    # Phosphorus (kg/ha)
    if p < 20:
        status["phosphorus"] = {"rating": "Low / Deficient", "color": "danger", "note": "Deficient available P (<20 kg/ha). Sluggish root establishment."}
    elif p <= 45:
        status["phosphorus"] = {"rating": "Medium / Optimal", "color": "success", "note": "Adequate phosphorus reserve."}
    else:
        status["phosphorus"] = {"rating": "High / Abundant", "color": "info", "note": "High phosphorus level."}

    # Potassium (kg/ha)
    if k < 25:
        status["potassium"] = {"rating": "Low / Deficient", "color": "danger", "note": "Low potassium (<25 kg/ha). Causes weak culms and poor pest resistance."}
    elif k <= 55:
        status["potassium"] = {"rating": "Medium / Optimal", "color": "success", "note": "Healthy potassium reserve."}
    else:
        status["potassium"] = {"rating": "High / Abundant", "color": "info", "note": "Rich potassium reserve."}

    # Soil pH
    if ph < 6.0:
        status["ph"] = {"rating": f"Acidic (pH {ph})", "color": "warning", "note": "Acidic soil fixes phosphorus. Agricultural lime / dolomite recommended."}
    elif ph <= 7.8:
        status["ph"] = {"rating": f"Neutral & Ideal (pH {ph})", "color": "success", "note": "Optimal pH range (6.0 – 7.8) for complete nutrient absorption."}
    elif ph <= 8.5:
        status["ph"] = {"rating": f"Moderately Alkaline (pH {ph})", "color": "warning", "note": "Alkaline soil. Zinc & Iron availability is suppressed."}
    else:
        status["ph"] = {"rating": f"Sodic / High Alkaline (pH {ph})", "color": "danger", "note": "High sodium and alkalinity. Agricultural gypsum application mandatory."}

    # Organic Carbon (OC %)
    if oc < 0.5:
        status["organic_carbon"] = {"rating": f"Low ({oc}%)", "color": "danger", "note": "Poor soil biology and low moisture retention. Organic compost required."}
    elif oc <= 0.75:
        status["organic_carbon"] = {"rating": f"Medium ({oc}%)", "color": "success", "note": "Satisfactory organic humus."}
    else:
        status["organic_carbon"] = {"rating": f"High ({oc}%)", "color": "success", "note": "Rich in organic carbon and beneficial soil microbes."}

    # Zinc (ppm)
    if zn < 0.6:
        status["zinc"] = {"rating": f"Deficient ({zn} ppm)", "color": "danger", "note": "Zinc < 0.6 ppm causes Khaira disease in rice and Little Leaf in cotton/chilli."}
    else:
        status["zinc"] = {"rating": f"Sufficient ({zn} ppm)", "color": "success", "note": "Adequate micronutrient zinc."}

    return status


def generate_fertilizer_recommendation(crop_name="Groundnut", soil_data=None, acres=2.0):
    """
    Computes exact chemical fertilizer bag requirements and 100% organic packages
    using Soil Test Crop Response (STCR) algorithms.
    """
    if soil_data is None:
        soil_data = {}

    crop_cfg = CROP_FERTILIZER_NORMS.get(crop_name, CROP_FERTILIZER_NORMS["Default"])

    n_val = float(soil_data.get("N", 45))
    p_val = float(soil_data.get("P", 25))
    k_val = float(soil_data.get("K", 35))
    ph_val = float(soil_data.get("pH", 7.0))
    oc_val = float(soil_data.get("organic_carbon", 0.55))
    zn_val = float(soil_data.get("zinc", 0.55))
    acres = max(0.1, float(acres))

    # STCR Adjustment Factors:
    # If soil is low, add +30% to base RDF; if high, deduct 25%
    n_factor = 1.30 if n_val < 30 else (0.75 if n_val > 65 else 1.0)
    p_factor = 1.30 if p_val < 20 else (0.75 if p_val > 45 else 1.0)
    k_factor = 1.30 if k_val < 25 else (0.75 if k_val > 55 else 1.0)

    # Legume biological nitrogen fixation credit:
    # Groundnut and pulses fix 50% of their nitrogen symbiotically
    if crop_cfg["legume"]:
        n_factor *= 0.50

    net_n_per_acre = round(crop_cfg["N"] * n_factor, 1)
    net_p_per_acre = round(crop_cfg["P"] * p_factor, 1)
    net_k_per_acre = round(crop_cfg["K"] * k_factor, 1)

    # Total Farm Pure Nutrient Requirements (kg)
    total_net_n = round(net_n_per_acre * acres, 1)
    total_net_p = round(net_p_per_acre * acres, 1)
    total_net_k = round(net_k_per_acre * acres, 1)

    # -------------------------------------------------------------------------
    # CHEMICAL PRECISION FERTILIZER PACKAGE (50kg Commercial Bags)
    # -------------------------------------------------------------------------
    # 1. P is supplied first via DAP (18% N, 46% P2O5)
    # Each 50kg bag of DAP delivers 23 kg P2O5 and 9 kg N
    dap_kg_total = round(total_net_p / 0.46, 1)
    dap_bags = round(dap_kg_total / 50.0, 1)
    n_supplied_by_dap = round(dap_kg_total * 0.18, 1)

    # 2. Remaining N is supplied via Urea (46% N)
    # Each 50kg bag of Urea delivers 23 kg N
    rem_n = max(0.0, total_net_n - n_supplied_by_dap)
    urea_kg_total = round(rem_n / 0.46, 1)
    urea_bags = round(urea_kg_total / 50.0, 1)

    # 3. K is supplied via Muriate of Potash (MOP: 60% K2O)
    # Each 50kg bag of MOP delivers 30 kg K2O
    mop_kg_total = round(total_net_k / 0.60, 1)
    mop_bags = round(mop_kg_total / 50.0, 1)

    # 4. Zinc Sulfate Heptahydrate (21% Zn)
    zinc_kg_per_acre = 10.0 if zn_val < 0.6 else 0.0
    zinc_kg_total = round(zinc_kg_per_acre * acres, 1)

    # 5. Soil Amendments: Gypsum or Lime
    conditioner_note = None
    gypsum_kg_total = 0.0
    lime_kg_total = 0.0

    if ph_val > 8.0:
        # Sodic / Alkaline Soil
        gypsum_kg_total = round(200.0 * acres, 1)
        conditioner_note = f"Alkaline Soil Amendment: Apply Agricultural Gypsum @ {int(gypsum_kg_total)} kg ({round(gypsum_kg_total/50, 1)} bags) to neutralize exchangeable sodium and improve water percolation."
    elif ph_val < 6.0:
        # Acidic Soil
        lime_kg_total = round(150.0 * acres, 1)
        conditioner_note = f"Acid Soil Amendment: Apply Agricultural Lime / Dolomite @ {int(lime_kg_total)} kg to raise soil pH to 6.5 and prevent phosphorus fixation."
    elif crop_cfg.get("gypsum_kg_acre", 0) > 0:
        # Crop-specific requirement (e.g. Groundnut pod filling)
        gypsum_kg_total = round(crop_cfg["gypsum_kg_acre"] * acres, 1)
        conditioner_note = f"{crop_name} Calcium Requirement: Apply Agricultural Gypsum @ {int(gypsum_kg_total)} kg ({round(gypsum_kg_total/50, 1)} bags) at 40-45 DAS for pod formation."

    # Chemical components list
    chemical_components = [
        {
            "fertilizer": "Di-Ammonium Phosphate (DAP 18-46-0)",
            "quantity": f"{dap_bags} Bags ({dap_kg_total} kg for {acres} Acres)",
            "dose_rate": f"{round(net_p_per_acre / 0.46, 1)} kg / acre",
            "stage": "Apply 100% as Basal dose at final land preparation / sowing."
        },
        {
            "fertilizer": "Urea (46% Nitrogen)",
            "quantity": f"{urea_bags} Bags ({urea_kg_total} kg for {acres} Acres)",
            "dose_rate": f"{round(rem_n / acres / 0.46, 1)} kg / acre",
            "stage": "Split application: 1/3 at basal, 1/3 at vegetative tillering, 1/3 at flowering."
        },
        {
            "fertilizer": "Muriate of Potash (MOP 60% K₂O)",
            "quantity": f"{mop_bags} Bags ({mop_kg_total} kg for {acres} Acres)",
            "dose_rate": f"{round(net_k_per_acre / 0.60, 1)} kg / acre",
            "stage": "Apply 50% basal and 50% at flowering / grain filling stage."
        }
    ]

    if zinc_kg_total > 0:
        chemical_components.append({
            "fertilizer": "Zinc Sulfate Heptahydrate (ZnSO₄ 21%)",
            "quantity": f"{zinc_kg_total} kg for {acres} Acres",
            "dose_rate": f"{zinc_kg_per_acre} kg / acre",
            "stage": "Basal broadcast; DO NOT mix directly with DAP in same basket to prevent zinc-phosphate precipitation."
        })

    if gypsum_kg_total > 0:
        chemical_components.append({
            "fertilizer": "Agricultural Gypsum (CaSO₄·2H₂O)",
            "quantity": f"{round(gypsum_kg_total / 50.0, 1)} Bags ({gypsum_kg_total} kg for {acres} Acres)",
            "dose_rate": f"{round(gypsum_kg_total / acres, 1)} kg / acre",
            "stage": "Apply at 40-45 DAS around root zone and hoe lightly before light irrigation."
        })

    # -------------------------------------------------------------------------
    # 100% ORGANIC & BIO-FERTILIZER PACKAGE
    # -------------------------------------------------------------------------
    fym_tonnes_acre = 4.0 if oc_val < 0.5 else 2.5
    vermicompost_tonnes_acre = 1.5 if oc_val < 0.5 else 1.0
    neem_cake_kg_acre = 150 if crop_cfg["type"].startswith("Cash") else 100

    bio_n = "Rhizobium culture @ 2 kg/acre (slurry seed treatment)" if crop_cfg["legume"] else "Azotobacter / Azospirillum @ 2 kg/acre"

    organic_package = {
        "title": "🌿 Complete 100% Organic & Bio-Fertilizer Package",
        "description": "Restores soil microbial biology, increases moisture retention, and delivers zero-chemical residue produce.",
        "components": [
            {
                "input": "Well-Decomposed Farmyard Manure (FYM)",
                "per_acre": f"{fym_tonnes_acre} Tonnes / acre",
                "total_farm": f"{round(fym_tonnes_acre * acres, 1)} Tonnes for {acres} Acres",
                "timing": "Incorporate during last plowing 15-20 days before sowing."
            },
            {
                "input": "Enriched Vermicompost",
                "per_acre": f"{vermicompost_tonnes_acre} Tonnes / acre",
                "total_farm": f"{round(vermicompost_tonnes_acre * acres, 1)} Tonnes for {acres} Acres",
                "timing": "Apply in seed furrows at sowing or transplanting."
            },
            {
                "input": "Neem Cake (De-oiled)",
                "per_acre": f"{neem_cake_kg_acre} kg / acre",
                "total_farm": f"{int(neem_cake_kg_acre * acres)} kg for {acres} Acres",
                "timing": "Basal application; repels soil nematodes/termites and slows nitrogen leaching."
            },
            {
                "input": "Nitrogen-Fixing Biofertilizer",
                "per_acre": bio_n,
                "total_farm": f"{round(2 * acres, 1)} kg for {acres} Acres",
                "timing": "Mix with jaggery water for seed coating or broadcast with moist vermicompost."
            },
            {
                "input": "Phosphate Solubilizing Bacteria (PSB) & VAM",
                "per_acre": "PSB culture @ 2 kg/acre + VAM @ 5 kg/acre",
                "total_farm": f"{round(2 * acres, 1)} kg PSB + {round(5 * acres, 1)} kg VAM",
                "timing": "Solubilizes locked native soil phosphorus into plant-available orthophosphate."
            },
            {
                "input": "Liquid Bio-stimulants (Jeevamrutham / Panchagavya)",
                "per_acre": "200 L Jeevamrutham OR 3% Panchagavya (6 L/acre in water)",
                "total_farm": f"{int(200 * acres)} Liters per irrigation cycle",
                "timing": "Apply with irrigation water at 21, 45, and 65 days after sowing."
            }
        ]
    }

    # -------------------------------------------------------------------------
    # INTEGRATED NUTRIENT MANAGEMENT (INM)
    # -------------------------------------------------------------------------
    inm_summary = (
        f"Apply 2 tonnes/acre of FYM/compost + biofertilizers (Azotobacter/Rhizobium + PSB) "
        f"combined with 75% of the calculated chemical fertilizer dose: "
        f"{round(dap_bags * 0.75, 1)} bags DAP, {round(urea_bags * 0.75, 1)} bags Urea, "
        f"and {round(mop_bags * 0.75, 1)} bags Potash for {acres} Acres. "
        f"This yields 15% higher returns than chemical alone while preserving living soil organic matter."
    )

    return {
        "success": True,
        "crop": crop_name,
        "land_acres": acres,
        "stcr_pure_nutrient_kg": {
            "nitrogen_n": total_net_n,
            "phosphorus_p": total_net_p,
            "potassium_k": total_net_k
        },
        "soil_health_ratings": evaluate_soil_health(soil_data),
        "soil_conditioner_advisory": conditioner_note,
        "organic_package": organic_package,
        "chemical_package": {
            "title": "🧪 Chemical Precision Fertilizer Package (ICAR/STCR)",
            "description": "Calculated to fulfill exact nutritional deficits through commercial fertilizers.",
            "bag_summary": {
                "dap_50kg_bags": dap_bags,
                "urea_50kg_bags": urea_bags,
                "mop_50kg_bags": mop_bags,
                "zinc_sulfate_kg": zinc_kg_total,
                "gypsum_50kg_bags": round(gypsum_kg_total / 50.0, 1) if gypsum_kg_total > 0 else 0.0
            },
            "components": chemical_components,
            "split_schedule": crop_cfg.get("splits", [])
        },
        "integrated_nutrient_management": inm_summary
    }
