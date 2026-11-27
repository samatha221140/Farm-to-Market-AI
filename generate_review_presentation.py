"""
Build Script: Review Presentation (PowerPoint .pptx)
===================================================
Project Title: An end-to-end Autonomous Farm-to-market Intelligent Network using Multi-sensor Fusion and Edge AI
Authors: D. Gayathri (N220872), G. Samatha Sreeja (N221140)
Guide: Charles Stud Sir

Preserves Literature Survey & Literature Gaps from mid-review,
and revamps everything from 'Existed Work' onwards with deep technical rigor,
system architecture, mathematical formulations, models, and experimental results.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

OUTPUT_PPTX = Path(r"c:\Users\G samatha sreeja\Desktop\Farm-to-Market-AI\Farm_to_Market_AI_Review_Presentation.pptx")

# 16:9 Widescreen dimensions
SLIDE_WIDTH = Inches(13.333)
SLIDE_HEIGHT = Inches(7.5)

# Color Palette
DARK_GREEN = RGBColor(27, 67, 50)      # #1B4332 Primary Header
FOREST_GREEN = RGBColor(45, 106, 79)   # #2D6A4F Secondary Brand
MINT_GREEN = RGBColor(240, 253, 244)   # #F0FDF4 Card Fill
AMBER_GOLD = RGBColor(217, 119, 6)     # #D97706 Accent
CARD_BG = RGBColor(255, 255, 255)      # White
TEXT_DARK = RGBColor(30, 41, 59)       # #1E293B Slate text
TEXT_MUTED = RGBColor(100, 116, 139)   # #64748B Secondary text
BORDER_COLOR = RGBColor(226, 232, 240) # #E2E8F0 Subtle Border
LIGHT_BG = RGBColor(248, 250, 252)     # #F8FAFC Page background


def apply_slide_background(slide):
    """Sets a clean, modern off-white background."""
    bg_shape = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT
    )
    bg_shape.fill.solid()
    bg_shape.fill.fore_color.rgb = LIGHT_BG
    bg_shape.line.fill.background() # No border
    return bg_shape


def add_slide_header(slide, title_text, category="AN AUTONOMOUS FARM-TO-MARKET INTELLIGENT NETWORK"):
    """Adds a standardized, elegant header banner across content slides."""
    # Top Category Pill
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    cat_tf = cat_box.text_frame
    cat_tf.word_wrap = True
    cat_p = cat_tf.paragraphs[0]
    cat_p.text = category.upper()
    cat_p.font.name = "Calibri"
    cat_p.font.size = Pt(10)
    cat_p.font.bold = True
    cat_p.font.color.rgb = AMBER_GOLD

    # Main Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.65), Inches(11.7), Inches(0.8))
    title_tf = title_box.text_frame
    title_tf.word_wrap = True
    title_p = title_tf.paragraphs[0]
    title_p.text = title_text
    title_p.font.name = "Calibri"
    title_p.font.size = Pt(22)
    title_p.font.bold = True
    title_p.font.color.rgb = DARK_GREEN

    # Accent divider line
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(11.733), Inches(0.03)
    )
    line.fill.solid()
    line.fill.fore_color.rgb = FOREST_GREEN
    line.line.fill.background()


def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=BORDER_COLOR):
    """Creates a modern rounded card container."""
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    card.fill.solid()
    card.fill.fore_color.rgb = bg_color
    if border_color:
        card.line.color.rgb = border_color
        card.line.width = Pt(1)
    else:
        card.line.fill.background()
    return card


def create_presentation():
    prs = Presentation()
    prs.slide_width = SLIDE_WIDTH
    prs.slide_height = SLIDE_HEIGHT
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s1)

    # Decorative header block
    dec = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_WIDTH, Inches(0.4))
    dec.fill.solid()
    dec.fill.fore_color.rgb = DARK_GREEN
    dec.line.fill.background()

    # Title Card
    add_card(s1, Inches(0.8), Inches(1.0), Inches(11.733), Inches(5.8), bg_color=CARD_BG, border_color=FOREST_GREEN)

    # Sub-badge
    badge = s1.shapes.add_textbox(Inches(1.2), Inches(1.3), Inches(10), Inches(0.4))
    bp = badge.text_frame.paragraphs[0]
    bp.text = "MAJOR PROJECT REVIEW PRESENTATION • 2026"
    bp.font.name = "Calibri"
    bp.font.size = Pt(12)
    bp.font.bold = True
    bp.font.color.rgb = AMBER_GOLD

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(1.2), Inches(1.7), Inches(10.9), Inches(1.8))
    t_tf = t_box.text_frame
    t_tf.word_wrap = True
    tp = t_tf.paragraphs[0]
    tp.text = "An End-to-End Autonomous Farm-to-Market Intelligent Network"
    tp.font.name = "Calibri"
    tp.font.size = Pt(30)
    tp.font.bold = True
    tp.font.color.rgb = DARK_GREEN

    tp2 = t_tf.add_paragraph()
    tp2.text = "Using Multi-Sensor Fusion, Edge AI and Real-Time Market Intelligence"
    tp2.font.name = "Calibri"
    tp2.font.size = Pt(20)
    tp2.font.color.rgb = FOREST_GREEN
    tp2.space_before = Pt(8)

    # Metadata Grid (Authors & Guide)
    guide_card = add_card(s1, Inches(1.2), Inches(4.0), Inches(5.2), Inches(2.2), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    g_box = s1.shapes.add_textbox(Inches(1.4), Inches(4.1), Inches(4.8), Inches(2.0))
    gtf = g_box.text_frame
    gtf.word_wrap = True
    p = gtf.paragraphs[0]
    p.text = "PROJECT GUIDANCE"
    p.font.name = "Calibri"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AMBER_GOLD

    p2 = gtf.add_paragraph()
    p2.text = "Under the Esteemed Guidance of:"
    p2.font.size = Pt(12)
    p2.font.color.rgb = TEXT_MUTED

    p3 = gtf.add_paragraph()
    p3.text = "Charles Stud Sir"
    p3.font.name = "Calibri"
    p3.font.size = Pt(18)
    p3.font.bold = True
    p3.font.color.rgb = DARK_GREEN
    p3.space_before = Pt(6)

    # Authors card
    auth_card = add_card(s1, Inches(6.8), Inches(4.0), Inches(5.2), Inches(2.2), bg_color=CARD_BG, border_color=BORDER_COLOR)
    a_box = s1.shapes.add_textbox(Inches(7.0), Inches(4.1), Inches(4.8), Inches(2.0))
    atf = a_box.text_frame
    atf.word_wrap = True
    p = atf.paragraphs[0]
    p.text = "PRESENTED BY"
    p.font.name = "Calibri"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = AMBER_GOLD

    p2 = atf.add_paragraph()
    p2.text = "• D. GAYATHRI  (ID: N220872)"
    p2.font.name = "Calibri"
    p2.font.size = Pt(15)
    p2.font.bold = True
    p2.font.color.rgb = DARK_GREEN
    p2.space_before = Pt(8)

    p3 = atf.add_paragraph()
    p3.text = "• G. SAMATHA SREEJA  (ID: N221140)"
    p3.font.name = "Calibri"
    p3.font.size = Pt(15)
    p3.font.bold = True
    p3.font.color.rgb = DARK_GREEN
    p3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: DOMAIN (PRESERVED FROM MID-REVIEW)
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s2)
    add_slide_header(s2, "Project Domain & Interdisciplinary Technologies")

    # Domain pillars
    pillars = [
        ("IoT & Embedded Edge Systems", "Collects real-time soil (N, P, K, pH, Moisture, EC) and environmental data via ESP32 and edge sensor probes."),
        ("Artificial Intelligence & ML", "Multi-factor crop recommendation, weather prediction, and ICAR/ANGRAU fertilizer dosage calculation."),
        ("Edge AI & Computer Vision", "MobileNetV2 ONNX backbone & pathological visual feature extraction for 67 disease, pest, and weed classes."),
        ("Federated & Decentralized Learning", "Allows disparate local data sources (sensor, climate, camera) to train global intelligence without exposing raw farm data."),
        ("Predictive Market Analytics", "Live APMC Mandi rate tracking, harvest yield calculation, transportation costing, and net profit optimization."),
        ("Direct Farm-to-Market Wholesale", "Decoupled wholesale produce marketplace connecting farmers directly with certified buyers, eliminating middleman margins.")
    ]

    for i, (title, desc) in enumerate(pillars):
        row = i // 3
        col = i % 3
        x = Inches(0.8 + col * 4.0)
        y = Inches(1.7 + row * 2.6)
        w = Inches(3.733)
        h = Inches(2.3)

        add_card(s2, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s2.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = f"{i+1}. {title}"
        p1.font.name = "Calibri"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(6)

    # =========================================================================
    # SLIDE 3: INTRODUCTION TO AGRICULTURE (AGRI 1.0 TO 4.0)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s3)
    add_slide_header(s3, "Evolution of Agriculture: Agri 1.0 to Agri 4.0")

    stages = [
        ("AGRI 1.0", "Traditional Farming", "Manual labor, draft animals, rainwater dependency, indigenous experience-based cropping with high vulnerability to droughts and epidemics."),
        ("AGRI 2.0", "Mechanized Agriculture", "Green Revolution introduction of tractors, combustion pumps, synthetic chemical fertilizers, and basic irrigation machinery."),
        ("AGRI 3.0", "Digital Agriculture", "Introduction of GPS mapping, satellite imagery, farm software, centralized cloud databases, and desktop agricultural analytics."),
        ("AGRI 4.0", "Autonomous Smart Agriculture", "Our Paradigm: Edge AI, Multi-sensor IoT fusion, automated FAO-56 irrigation scheduling, on-device disease diagnosis, and direct market connectivity.")
    ]

    for i, (stage, name, details) in enumerate(stages):
        x = Inches(0.8 + i * 2.95)
        y = Inches(1.8)
        w = Inches(2.8)
        h = Inches(5.0)

        bg = MINT_GREEN if i == 3 else CARD_BG
        bdr = FOREST_GREEN if i == 3 else BORDER_COLOR
        add_card(s3, x, y, w, h, bg_color=bg, border_color=bdr)

        tb = s3.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = stage
        p1.font.name = "Calibri"
        p1.font.size = Pt(18)
        p1.font.bold = True
        p1.font.color.rgb = AMBER_GOLD if i == 3 else DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = name
        p2.font.name = "Calibri"
        p2.font.size = Pt(14)
        p2.font.bold = True
        p2.font.color.rgb = FOREST_GREEN
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = details
        p3.font.name = "Calibri"
        p3.font.size = Pt(11.5)
        p3.font.color.rgb = TEXT_DARK
        p3.space_before = Pt(12)

    # =========================================================================
    # SLIDES 4-8: LITERATURE SURVEY & GAPS (PRESERVED EXACTLY AS REQUIRED)
    # =========================================================================
    papers = [
        ("Paper 1: AI-Driven Smart Agriculture (Khaliq et al., July 2025)",
         "An Integrated Approach for Soil Analysis, Irrigation, and Crop-Fertilizer Recommendations",
         [
             "Soil Health Analysis: Predicts soil fertility from NPK, pH using TabNet Regressor with XAI.",
             "Smart Irrigation: TTL Transformer learns relationships between moisture, temperature, and forecast.",
             "Crop Recommendation: SwiFT Sparse Windowed Transformer for multi-parameter crop selection.",
             "Fertilizer Recommendation: TabNet + LIME for soil and crop classification."
         ],
         [
             "No Market Price Forecasting: Optimizes purely for physical productivity rather than farmer revenue.",
             "No Pre-Profit Estimation: Lacks cultivation cost, yield, and net profit calculations.",
             "No Future Climate Adaptation: Relies strictly on instantaneous weather without multi-day outlook.",
             "Sensor Anomaly Risk: Assumes IoT hardware is infallible; noisy sensors corrupt recommendations."
         ]),
        ("Paper 2: Federated Explainable AI in Smart Agriculture (Tahir et al., May 2025)",
         "Enhancing Transparency, Efficiency, and Sustainability",
         [
             "Crop Health Monitoring: UAV/drone image stress identification via CNN + Grad-CAM.",
             "Crop Yield Prediction: Explains yield drivers across field zones using LIME + SHAP.",
             "Privacy-Preserving Federated AI: Local model training on farm sites with gradient-only aggregation."
         ],
         [
             "Complex / Non-Actionable Explainability: SHAP heatmaps confuse rural farmers lacking multilingual/voice advice.",
             "Total Lack of Market Intelligence: No MSP analysis, buyer matching, or transport cost factoring.",
             "Narrow Disease Treatment: Identifies lesions but lacks specific organic and chemical treatment dosages."
         ]),
        ("Paper 3: AIoT-Enabled Data Management for Smart Agriculture (Luo et al., June 2025)",
         "A Comprehensive Review on Emerging Technologies",
         [
             "Perception Layer: Soil sensors, multispectral UAV imaging, and Edge AI + Mask R-CNN.",
             "Transport & Platform Layers: ZigBee, LoRa, Wi-Fi, Cloud Computing, and Digital Twins.",
             "Application Layer: YOLO-Spot weed detection, CNN disease classification, K-Means soil zoning."
         ],
         [
             "Disjointed Multi-Factor Decision Making: Fails to unify soil chemistry, future climate, and market price into a single optimization function.",
             "Unaddressed Sensor Drift: Considers network anomalies but assumes field probes are 100% accurate."
         ]),
        ("Paper 4: AI-Driven Technologies in Modern Agriculture (Seif-Ennasr et al., Aug 2025)",
         "A Systematic Literature Review",
         [
             "Hybrid AI Architectures: Combining IoT, Edge computing, and ensemble models (91-94% accuracy).",
             "Multimodal Data Fusion: Fusing sensor telemetry, imagery, and climate indices (90-95% accuracy).",
             "Sustainability Impact: Reduces water, fertilizer, and pesticide wastage by 15-30%."
         ],
         [
             "Regional Language & Communication Barrier: Systems restricted to English alienate rural farmers.",
             "Disregard of Farmer Agronomic Knowledge: Fails to integrate traditional farming wisdom and field feedback with AI computational models."
         ]),
        ("Paper 5: Advanced Technologies for Smart Fertilizer Management (Liu et al., July 2025)",
         "A Review of Precision Nutrient Management",
         [
             "Machine Learning Fertilizer Dosage: CNN, SVM, and ANN modeling on soil/crop metrics.",
             "Site-Specific Variable Rate Application (VRA): GIS, GPS, and precision drone dispersion."
         ],
         [
             "Prohibitive Hardware Cost: Drones, UGVs, and hyperspectral imagers are unaffordable for smallholders.",
             "Lack of Automatic Anomaly Filtering: Defective NPK sensor probes produce toxic over-fertilization advice."
         ])
    ]

    for p_idx, (p_title, p_sub, objectives, gaps) in enumerate(papers):
        sp = prs.slides.add_slide(blank_layout)
        apply_slide_background(sp)
        add_slide_header(sp, p_title, category=f"LITERATURE SURVEY • PAPER {p_idx+1}")

        # Subtitle
        sb = sp.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.4))
        p = sb.text_frame.paragraphs[0]
        p.text = f"Core Focus: {p_sub}"
        p.font.name = "Calibri"
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_MUTED

        # Left Column: Objectives & Models
        add_card(sp, Inches(0.8), Inches(2.0), Inches(5.7), Inches(4.9), bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb_l = sp.shapes.add_textbox(Inches(1.0), Inches(2.1), Inches(5.3), Inches(4.6))
        tf_l = tb_l.text_frame
        tf_l.word_wrap = True
        h_l = tf_l.paragraphs[0]
        h_l.text = "PROPOSED METHODOLOGIES & MODELS"
        h_l.font.name = "Calibri"
        h_l.font.size = Pt(13)
        h_l.font.bold = True
        h_l.font.color.rgb = DARK_GREEN

        for obj in objectives:
            bp = tf_l.add_paragraph()
            bp.text = f"• {obj}"
            bp.font.name = "Calibri"
            bp.font.size = Pt(11)
            bp.font.color.rgb = TEXT_DARK
            bp.space_before = Pt(8)

        # Right Column: Literature Gaps Identified
        add_card(sp, Inches(6.8), Inches(2.0), Inches(5.7), Inches(4.9), bg_color=RGBColor(254, 242, 242), border_color=RGBColor(248, 113, 113))
        tb_r = sp.shapes.add_textbox(Inches(7.0), Inches(2.1), Inches(5.3), Inches(4.6))
        tf_r = tb_r.text_frame
        tf_r.word_wrap = True
        h_r = tf_r.paragraphs[0]
        h_r.text = "CRITICAL LITERATURE GAPS IDENTIFIED"
        h_r.font.name = "Calibri"
        h_r.font.size = Pt(13)
        h_r.font.bold = True
        h_r.font.color.rgb = RGBColor(185, 28, 28)

        for gap in gaps:
            bp = tf_r.add_paragraph()
            bp.text = f"⚠️ {gap}"
            bp.font.name = "Calibri"
            bp.font.size = Pt(11)
            bp.font.color.rgb = RGBColor(127, 29, 29)
            bp.space_before = Pt(8)

    # =========================================================================
    # SLIDE 9: CONSOLIDATED RESEARCH GAPS & HOW OUR PROJECT BRIDGES THEM
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s9)
    add_slide_header(s9, "Consolidated Literature Gaps & Our Proposed Solutions")

    gaps_matrix = [
        ("Gap 1: Disconnect Between Crop Selection and Market Profit",
         "Existing systems optimize only for botanical suitability, ignoring Mandi prices and costs.",
         "Our Solution: Phase 1 integrates live APMC Mandi rates, average regional yields, and cultivation expenses to calculate Net Profit (₹/acre) and ROI % before sowing."),
        ("Gap 2: Excessive Hardware Cost (UAVs / High-End Cloud GPUs)",
         "Smallholder farmers cannot afford expensive drones or cloud server subscriptions.",
         "Our Solution: Edge AI on ESP32 + MobileNetV2 ONNX running sub-35ms inference on low-cost CPUs without needing costly GPUs or drones."),
        ("Gap 3: Inaccurate Irrigation & Fertilizer Calculations",
         "Generic rule of thumb or black-box models cause root rot or toxic salt accumulation.",
         "Our Solution: Phase 2 implements FAO-56 Penman-Monteith Evapotranspiration for pump runtime (minutes) & ICAR/ANGRAU STCR commercial 50kg fertilizer bags."),
        ("Gap 4: Exploitation by Agricultural Intermediaries / Middlemen",
         "Farmers lose 25–40% margin to commission brokers due to lack of wholesale market reach.",
         "Our Solution: Phase 3 provides an autonomous direct farmer-to-buyer marketplace with quality photo upload, live APMC price sync, and direct buyer bids.")
    ]

    for i, (gap_name, prob, sol) in enumerate(gaps_matrix):
        row = i // 2
        col = i % 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.8 + row * 2.6)
        w = Inches(5.75)
        h = Inches(2.4)

        add_card(s9, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s9.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = gap_name
        p1.font.name = "Calibri"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = f"Identified Problem: {prob}"
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = RGBColor(185, 28, 28)
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = sol
        p3.font.name = "Calibri"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = FOREST_GREEN
        p3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 10: EXISTING WORK VS. OUR PROPOSED AUTONOMOUS NETWORK (REPLACING BLANK SLIDE 11)
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s10)
    add_slide_header(s10, "Comparative Analysis: Existing Agricultural Systems vs. Proposed Network")

    comparison_data = [
        ("Capability / Parameter", "Existing Research & Commercial Apps", "Our Autonomous Farm-to-Market Network"),
        ("Lifecycle Scope", "Isolated: only disease detection OR only soil test", "Complete End-to-End: Pre-sowing to in-field care to wholesale marketing"),
        ("Crop Recommendation", "Pure agronomic suitability; ignores market selling prices", "Hybrid AI + Live Mandi profit ranking (₹/Acre, ROI %, Yield cost)"),
        ("Irrigation Control", "Simple moisture thresholds (e.g. if moisture < 30%)", "FAO-56 Hargreaves ET0 + Crop Kc + 24h Rain forecast = Pump runtime (mins)"),
        ("Fertilizer Recommendation", "Broad NPK categories (Low / Medium / High)", "Exact commercial 50kg bags (Urea, DAP, MOP, Zinc) via ICAR STCR equations"),
        ("Disease & Pest Diagnosis", "10-20 general classes, requires high-end GPU servers", "67 AP crops/pests/weeds classes via MobileNetV2 ONNX (sub-35ms on CPU)"),
        ("Marketplace Connectivity", "Static list or external government link", "Integrated direct wholesale trade, lot photos, buyer bid matching, live APMC rates"),
        ("Deployment & Costs", "Expensive drones, cloud subscription fees, proprietary sensors", "Low-cost Edge AI (ESP32), zero-cost open meteorological API, dual persistent SQL")
    ]

    # Create comparison table
    x = Inches(0.8)
    y = Inches(1.8)
    w = Inches(11.733)
    h = Inches(5.0)

    rows = len(comparison_data)
    cols = 3
    table_shape = s10.shapes.add_table(rows, cols, x, y, w, h)
    table = table_shape.table
    table.columns[0].width = Inches(2.5)
    table.columns[1].width = Inches(4.5)
    table.columns[2].width = Inches(4.733)

    for r_idx, row in enumerate(comparison_data):
        for c_idx, cell_text in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = cell_text
            p = cell.text_frame.paragraphs[0]
            p.font.name = "Calibri"
            if r_idx == 0:
                p.font.size = Pt(12)
                p.font.bold = True
                p.font.color.rgb = RGBColor(255, 255, 255)
                cell.fill.solid()
                cell.fill.fore_color.rgb = DARK_GREEN
            else:
                p.font.size = Pt(10.5)
                if c_idx == 2:
                    p.font.bold = True
                    p.font.color.rgb = DARK_GREEN
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = MINT_GREEN
                else:
                    p.font.color.rgb = TEXT_DARK
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = CARD_BG

    # =========================================================================
    # SLIDE 11: INTRODUCTION TO OUR PROJECT & PROBLEM DEFINITION
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s11)
    add_slide_header(s11, "Project Overview: Problem Definition & Autonomous Vision")

    # Left Card: The Problem
    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s11.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "THE AGRICULTURAL CRISIS IN INDIA"
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = RGBColor(185, 28, 28)

    probs = [
        "1. Unscientific Crop Planning: Over 70% of farmers plant traditional crops without soil testing or market demand checks, leading to severe debt and gluts.",
        "2. Groundwater & Electricity Depletion: Inefficient flood irrigation wastes up to 45% of water, draining borewells and overburdening rural power grids.",
        "3. Untreated Plant Epidemics: Crop diseases and pests destroy 25–35% of annual crop yield before farmers correctly diagnose the pathogen.",
        "4. Intermediary Market Exploitation: Commission agents and middlemen capture up to 40% of produce market value due to asymmetrical market information."
    ]
    for pb in probs:
        p2 = tf_l.add_paragraph()
        p2.text = pb
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(8)

    # Right Card: The Autonomous Network Solution
    add_card(s11, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s11.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "OUR AUTONOMOUS END-TO-END NETWORK"
    p.font.name = "Calibri"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    sols = [
        "• Unified 3-Phase Ecosystem: Bridges pre-sowing decisions, field-level care, and post-harvest sales into one cohesive intelligent platform.",
        "• Multi-Sensor & Multi-Source Fusion: Integrates soil chemistry (N, P, K, pH, Moisture), Open-Meteo climate forecasts, and APMC Mandi commodity rates.",
        "• Edge AI & Lightweight ONNX Inference: MobileNetV2 depthwise separable convolutions running directly on CPU edge instances under 35 milliseconds.",
        "• Dual-Storage Data Persistence: SQLite relational engine + append-only audit stream tracking all inputs, images, and outputs across the farming cycle.",
        "• Direct Farmer-to-Buyer Marketplace: Zero-broker wholesale trading portal empowering farmers with transparent price discovery and buyer inquiry matching."
    ]
    for sl in sols:
        p2 = tf_r.add_paragraph()
        p2.text = sl
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(8)

    # =========================================================================
    # SLIDE 12: 6-LAYER SYSTEM ARCHITECTURE & BLOCK DIAGRAM
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s12)
    add_slide_header(s12, "System Architecture: 6-Layer End-to-End Network Hierarchy")

    layers = [
        ("Layer 1: Data Acquisition Layer", "ESP32 Controller, 7-in-1 Soil Sensor (N, P, K, pH, Moisture, EC, Temp), DHT22 Sensor, Open-Meteo Weather API, APMC Mandi Commodity Feeds."),
        ("Layer 2: Local Processing & Edge AI", "On-device calibration, sensor sanity validation, photometric image preprocessing, and MobileNetV2 ONNX deep feature extraction."),
        ("Layer 3: Privacy & Data Persistence", "Dual-Storage Engine: Relational SQLite / PostgreSQL database + Append-only audit stream (farm_activity_log.jsonl). Physical image persistence via UUID hashing."),
        ("Layer 4: AI Decision & Optimization Engine", "Random Forest Crop Recommender + FAO-56 Penman-Monteith ET0 Engine + ICAR STCR Fertilizer Calculator + 67-Class Pathological Ensemble."),
        ("Layer 5: Application Service Layer", "RESTful Flask 3.1 microservices: /api/recommend, /api/phase2/irrigation-advisory, /api/phase2/fertilizer-plan, /api/phase2/diagnose-image, /api/phase3/listings."),
        ("Layer 6: Smart Farmer Dashboard", "Unified responsive HTML5/CSS3/Vanilla JS single-page application with real-time weather integration, camera scanner, and live Mandi prices.")
    ]

    for i, (lname, ldesc) in enumerate(layers):
        y = Inches(1.7 + i * 0.88)
        add_card(s12, Inches(0.8), y, Inches(11.733), Inches(0.78), bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s12.shapes.add_textbox(Inches(1.0), y + Inches(0.05), Inches(11.3), Inches(0.68))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = lname
        p1.font.name = "Calibri"
        p1.font.size = Pt(12.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = ldesc
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 13: THE 3-PHASE SMART ECOSYSTEM WORKFLOW
    # =========================================================================
    s13 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s13)
    add_slide_header(s13, "Farm-to-Market AI Ecosystem: The 3 Operational Phases")

    phase_boxes = [
        ("PHASE 1: PLANNING", "Autonomous Crop Planning & Profit Maximization",
         "• Inputs: Soil N, P, K, pH, Soil Type, Water Level, Season, Farm Land Acres.\n"
         "• AI Processing: Random Forest multi-class model + Agronomic Asymmetric Penalty scoring.\n"
         "• Market Optimization: Real APMC Mandi prices & cultivation costs calculate net profit/acre.\n"
         "• Farmer Output: Top 5 suitable crops + Top 3 ranked by Net Profit (₹/acre) and ROI %."),
        ("PHASE 2: GROWING", "Autonomous In-Field Smart Crop Care & Monitoring",
         "• Smart Irrigation: FAO-56 Hargreaves ET0 + Crop Kc + 24h Rain Credit = Pump Runtime (mins).\n"
         "• Soil Health & STCR: ICAR/ANGRAU algorithm yields exact 50kg bags (Urea, DAP, MOP, Zinc).\n"
         "• Deep Vision Diagnostics: MobileNetV2 ONNX backbone + 20 handcrafted pathological indices.\n"
         "• Output: Sub-35ms diagnosis for 67 disease/pest/weed classes with dual Organic & Chemical cures."),
        ("PHASE 3: SELLING", "Post-Harvest Wholesale Marketplace & Direct Trade",
         "• Direct Lot Listing: Harvested produce lot photos, variety, grade, asking price, and village.\n"
         "• Real-Time Mandi Sync: Live daily automated price feeds from APMC markets (Guntur, Kurnool).\n"
         "• Buyer Inquiry Portal: Direct wholesale bids delivered to farmer without commission brokers.\n"
         "• Output: Higher farmer profit margins, transparent market rates, and zero intermediate leakage.")
    ]

    for i, (p_title, p_sub, p_body) in enumerate(phase_boxes):
        x = Inches(0.8 + i * 3.95)
        y = Inches(1.8)
        w = Inches(3.8)
        h = Inches(5.0)

        bg = MINT_GREEN if i == 0 else CARD_BG
        add_card(s13, x, y, w, h, bg_color=bg, border_color=BORDER_COLOR)

        tb = s13.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = p_title
        p1.font.name = "Calibri"
        p1.font.size = Pt(16)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = p_sub
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = AMBER_GOLD
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = p_body
        p3.font.name = "Calibri"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = TEXT_DARK
        p3.space_before = Pt(10)

    # =========================================================================
    # SLIDE 14: PHASE 1 DETAILED: CROP RECOMMENDATION & AGRONOMIC SCORING
    # =========================================================================
    s14 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s14)
    add_slide_header(s14, "Phase 1: Hybrid ML & Agronomic Suitability Engine")

    # Left: The 12 Andhra Pradesh Crops & Rules
    add_card(s14, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s14.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "12 TARGET CROPS & AGRO-CLIMATIC BENCHMARKS"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    crop_info = [
        "1. Cereals & Millets: Rice (High water), Maize (Medium), Jowar (Low), Bajra (Low).",
        "2. Commercial Cash Crops: Chilli (Medium, Red/Black soils), Cotton (Medium, Black soil), Sugarcane (High, 12-month cycle).",
        "3. Pulses & Oilseeds: Groundnut (Low, Sandy/Red), Bengal Gram (Low, Rabi), Black Gram (Low), Red Gram (Low), Green Gram (Low).",
        "• Asymmetric Agronomic Scoring (100 Points Total):",
        "  - Soil Type Compatibility: 20 Points (Optimal vs Suboptimal soil texture)",
        "  - Water Availability Match: 20 Points (Deficit & waterlogging penalties)",
        "  - N-P-K Nutrient Affinity: 20 Points (Asymmetric deficit vs surplus)",
        "  - Temperature Tolerance: 10 Points (Crop-specific optimal spans)",
        "  - Rainfall & Humidity: 15 Points (Hargreaves historical matching)",
        "  - Soil pH Affinity: 10 Points (Alkaline vs Acidic penalties)",
        "  - Seasonal Calendar Match: 5 Points (Kharif, Rabi, Zaid enforcement)"
    ]
    for ci in crop_info:
        p2 = tf_l.add_paragraph()
        p2.text = ci
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # Right: The Asymmetric Math Formula
    add_card(s14, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s14.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "ASYMMETRIC NUTRIENT SUITABILITY FORMULATION"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    math_desc = [
        "Biological Asymmetry Principle:\n"
        "Plants safely tolerate surplus nutrients in soil, but a nutrient deficit severely stunts enzymatic pathways and halts vegetative growth. Hence, deficits are penalized 2x more heavily.",
        "\nMathematical Formulation:\n"
        "If Actual Nutrient (V) >= Target Requirement (T):\n"
        "    Score = max(0.0, 1.0 - ((V - T) / max(1.5 * T, 40.0))) * Weight\n"
        "Else (Nutrient Deficit, V < T):\n"
        "    Score = max(0.0, 1.0 - ((T - V) / max(0.75 * T, 15.0))) * Weight",
        "\nEnvironmental Range Match:\n"
        "If Low <= Temp <= High: Score = Weight (10.0 pts)\n"
        "Else: Score = max(0.0, 1.0 - (Delta / Span)) * Weight",
        "\nOutcome: Guaranteed 100% agronomic safety. A pure ML model might recommend high-water Rice in severe drought; our hybrid engine prevents catastrophic crop bankruptcy."
    ]
    for md in math_desc:
        p2 = tf_r.add_paragraph()
        p2.text = md
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 15: PHASE 1: MARKET PROFIT RANKING & ROI OPTIMIZATION
    # =========================================================================
    s15 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s15)
    add_slide_header(s15, "Phase 1: Real-Time Mandi Price Ranking & Economic ROI Optimization")

    # Formula Card Top
    add_card(s15, Inches(0.8), Inches(1.8), Inches(11.733), Inches(2.1), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb = s15.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(11.3), Inches(1.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "MATHEMATICAL ECONOMIC RANKING FORMULATION"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    econ_math = (
        "1. Gross Revenue per Acre (₹) = Average Regional Yield (Quintals/Acre) * Current Mandi Price (₹/Quintal)\n"
        "2. Net Profit per Acre (₹)     = Gross Revenue per Acre - Cost of Cultivation per Acre\n"
        "3. Return on Investment (ROI %) = (Net Profit per Acre / Cost of Cultivation per Acre) * 100\n"
        "4. Farm-Wide Total Net Profit  = Net Profit per Acre * Land Size (Acres)"
    )
    p2 = tf.add_paragraph()
    p2.text = econ_math
    p2.font.name = "Consolas"
    p2.font.size = Pt(11)
    p2.font.color.rgb = DARK_GREEN
    p2.space_before = Pt(6)

    # Three Sample Ranking Cards (Real Andhra Pradesh Mandi Benchmarks)
    examples = [
        ("Chilli (Guntur Sannam)", "Mandi: Guntur APMC Yard", "Price: ₹19,286 / Quintal", "Yield: 15.0 Qtl/Acre", "Cost: ₹85,000 / Acre", "Gross: ₹2,89,290 / Acre", "Net Profit: ₹2,04,290 / Acre", "ROI: 240.3% (High Profit)"),
        ("Groundnut (K6 Bold)", "Mandi: Kalyandurg APMC", "Price: ₹8,250 / Quintal", "Yield: 10.0 Qtl/Acre", "Cost: ₹28,000 / Acre", "Gross: ₹82,500 / Acre", "Net Profit: ₹54,500 / Acre", "ROI: 194.6% (Moderate Profit)"),
        ("Cotton (Medium Staple)", "Mandi: Narasaraopet APMC", "Price: ₹9,063 / Quintal", "Yield: 10.0 Qtl/Acre", "Cost: ₹35,000 / Acre", "Gross: ₹90,630 / Acre", "Net Profit: ₹55,630 / Acre", "ROI: 158.9% (Steady Return)")
    ]

    for i, (cname, mkt, prc, yld, cst, grs, net, roi) in enumerate(examples):
        x = Inches(0.8 + i * 3.95)
        y = Inches(4.1)
        w = Inches(3.8)
        h = Inches(2.7)

        add_card(s15, x, y, w, h, bg_color=MINT_GREEN, border_color=FOREST_GREEN)
        tb_c = s15.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), h - Inches(0.3))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True

        p1 = tf_c.paragraphs[0]
        p1.text = cname
        p1.font.name = "Calibri"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        lines = [mkt, prc, f"{yld} | {cst}", f"{grs}", f"★ {net}", f"★ {roi}"]
        for ln in lines:
            p_ln = tf_c.add_paragraph()
            p_ln.text = ln
            p_ln.font.name = "Calibri"
            p_ln.font.size = Pt(10)
            p_ln.font.color.rgb = TEXT_DARK
            p_ln.space_before = Pt(2)

    # =========================================================================
    # SLIDE 16: PHASE 2: IN-FIELD AUTONOMOUS SMART CROP CARE HARDWARE
    # =========================================================================
    s16 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s16)
    add_slide_header(s16, "Phase 2: IoT Hardware Architecture & In-Field Multi-Sensor Fusion")

    hw_cards = [
        ("ESP32 Microcontroller", "Core Edge Processing Unit", "Dual-core Xtensa 32-bit LX6 running at 240 MHz. Manages sensor polling, local telemetry buffering, pump relay actuation, and Wi-Fi/LoRa communication."),
        ("7-in-1 Soil Sensor Probe", "Root Zone Soil Multi-Parameter Sensor", "Industrial RS485 Modbus probe inserted 15-30cm into the root zone. Reads Nitrogen, Phosphorus, Potassium, pH, Volumetric Moisture, Electrical Conductivity (EC), and Temperature simultaneously."),
        ("DHT22 Environmental Sensor", "Micro-Climate Temperature & Humidity", "Digital capacitive sensor measuring ambient air temperature (-40 to 80°C ±0.5°C) and relative humidity (0 to 100% ±2%). Crucial for vapor pressure deficit and evapotranspiration calculations."),
        ("Optocoupler Relay & Water Pump", "Hardware Actuation & Run Control", "Optoisolated 5V-240V AC relay module switching 0.5 HP to 5.0 HP borewell pumps on/off based on calculated FAO-56 irrigation runtimes, preventing pump dry run and electrical spikes.")
    ]

    for i, (title, sub, body) in enumerate(hw_cards):
        x = Inches(0.8 + i * 2.95)
        y = Inches(1.8)
        w = Inches(2.8)
        h = Inches(5.0)

        add_card(s16, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s16.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = "Calibri"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = sub
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = AMBER_GOLD
        p2.space_before = Pt(3)

        p3 = tf.add_paragraph()
        p3.text = body
        p3.font.name = "Calibri"
        p3.font.size = Pt(10.5)
        p3.font.color.rgb = TEXT_DARK
        p3.space_before = Pt(10)

    # =========================================================================
    # SLIDE 17: PHASE 2: SMART IRRIGATION ENGINE (FAO-56 ET0 FORMULAS)
    # =========================================================================
    s17 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s17)
    add_slide_header(s17, "Phase 2: Smart Irrigation Scheduling (FAO-56 Evapotranspiration & Soil Physics)")

    # Left Box: Equations
    add_card(s17, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s17.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(6.4), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "FAO-56 SCIENTIFIC WATER BUDGETING FORMULATION"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    eqs = [
        "1. Reference Evapotranspiration (Hargreaves Empirical Equation, mm/day):\n"
        "   ET0 = 4.2 + 0.18 * max(0.0, Temp_C - 25.0) - 0.02 * max(0.0, Humidity_% - 50.0)\n"
        "   (Bounded strictly between 2.5 mm/day and 8.5 mm/day)",
        "2. Crop Evapotranspiration (ETc):\n"
        "   ETc = ET0 * Kc  (where Kc is the stage coefficient: e.g. 1.05 to 1.25 during flowering)",
        "3. Volumetric Soil Moisture Deficit (%):\n"
        "   Deficit_% = max(0.0, (0.80 * Field_Capacity_%) - Current_Soil_Moisture_%)\n"
        "   Soil_Deficit_mm = (Deficit_% / 100.0) * (Effective_Root_Zone_Depth_cm * 10.0)",
        "4. Effective Rain Deduction & 24h Rain Credit:\n"
        "   Rain_eff = (Rain_today * 0.85) if Rain_today > 3.0 mm else 0.0 mm\n"
        "   Forecast_Credit = min(15.0, Forecast_Rain_24h * 0.60)",
        "5. Net Irrigation Requirement (NIR, mm) & Gross Water Volume:\n"
        "   NIR = max(0.0, (Soil_Deficit_mm + ETc) - Rain_eff - Forecast_Credit)\n"
        "   Gross_Water_Liters = (NIR * 4047.0 * Land_Acres) / Irrigation_Efficiency\n"
        "   (Drip Efficiency = 90%, Sprinkler = 75%, Furrow/Flood = 60%)",
        "6. Pump Runtime (Minutes) & Energy Consumption (kWh):\n"
        "   Pump_Runtime_Minutes = Gross_Water_Liters / Pump_Flow_Rate_LPM\n"
        "   Pump_Energy_kWh = (Pump_HP * 0.746) * (Pump_Runtime_Minutes / 60.0)"
    ]
    for eq in eqs:
        p2 = tf_l.add_paragraph()
        p2.text = eq
        p2.font.name = "Consolas"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = DARK_GREEN
        p2.space_before = Pt(3)

    # Right Box: Soil Physics Constants
    add_card(s17, Inches(7.8), Inches(1.8), Inches(4.733), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s17.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "SOIL TEXTURAL CONSTANTS & PUMP SIZING"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    soil_txt = [
        "Soil Moisture Benchmarks:\n"
        "• Sandy Soil: FC = 16.0%, PWP = 6.0% (Fast percolation)\n"
        "• Red Soil: FC = 26.0%, PWP = 12.0% (Medium retention)\n"
        "• Loamy Soil: FC = 30.0%, PWP = 14.0% (Ideal texture)\n"
        "• Black Soil: FC = 40.0%, PWP = 22.0% (High clay retentive)",
        "\nPump Flow Rates (Litres Per Minute):\n"
        "• 0.5 HP: 75 LPM (~4,500 L/hr)\n"
        "• 1.0 HP: 150 LPM (~9,000 L/hr small borewell)\n"
        "• 2.0 HP: 300 LPM (~18,000 L/hr)\n"
        "• 3.0 HP: 480 LPM (~28,800 L/hr)\n"
        "• 5.0 HP: 800 LPM (~48,000 L/hr large open well)",
        "\nAutomated Decision Guardrails:\n"
        "Postpones pumping if 24h rain forecast > 20mm or if current soil moisture >= 85% of Field Capacity."
    ]
    for st in soil_txt:
        p2 = tf_r.add_paragraph()
        p2.text = st
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 18: PHASE 2: PRECISION SOIL HEALTH & STCR FERTILIZER CALCULATION
    # =========================================================================
    s18 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s18)
    add_slide_header(s18, "Phase 2: ICAR / ANGRAU Soil Test Crop Response (STCR) Fertilizer Engine")

    # Left: STCR Calculation Steps
    add_card(s18, Inches(0.8), Inches(1.8), Inches(6.8), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s18.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(6.4), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "STCR PRECISION BAG CALCULATION PIPELINE"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    stcr_steps = [
        "1. Soil Test Evaluation (ICAR Benchmarks):\n"
        "   - Available N (kg/ha): Low (<30), Medium (30-65), High (>65)\n"
        "   - Available P (kg/ha): Low (<20), Medium (20-45), High (>45)\n"
        "   - Available K (kg/ha): Low (<25), Medium (25-55), High (>55)",
        "2. STCR Nutrient Adjustment Factors:\n"
        "   If Soil Nutrient is Low:   Apply +30% over Recommended Dose of Fertilizer (RDF)\n"
        "   If Soil Nutrient is High:  Reduce by -25% to avoid fertilizer toxicity\n"
        "   Legume Credit: Groundnut & pulses receive 50% N reduction (Rhizobium N2-fixation)",
        "3. 50kg Commercial Fertilizer Bag Translation:\n"
        "   • DAP (18% N, 46% P2O5): DAP_kg = Net_P / 0.46;  Bags = ceil(DAP_kg / 50)\n"
        "   • Urea (46% N): Remaining_N = max(0, Net_N - DAP_kg * 0.18);\n"
        "                   Urea_kg = Remaining_N / 0.46;  Bags = ceil(Urea_kg / 50)\n"
        "   • MOP (60% K2O): MOP_kg = Net_K / 0.60;  Bags = ceil(MOP_kg / 50)",
        "4. Micronutrients & Soil Conditioners:\n"
        "   - Zinc Sulfate (21% Zn): 10 kg/acre if soil Zn < 0.6 ppm\n"
        "   - Agricultural Gypsum: 200 kg/acre if soil pH > 8.0 (Alkaline soil reclamation)\n"
        "   - Agricultural Lime: 150 kg/acre if soil pH < 6.0 (Acidic soil neutralization)"
    ]
    for ss in stcr_steps:
        p2 = tf_l.add_paragraph()
        p2.text = ss
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # Right: Stage-Wise Split Schedules
    add_card(s18, Inches(7.8), Inches(1.8), Inches(4.733), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s18.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "STAGE-WISE SPLIT APPLICATION (INM)"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    split_txt = [
        "Why Split Application Matters:\n"
        "Applying 100% Nitrogen at sowing causes 50-60% leaching into groundwater. Our split engine delivers nutrients exactly when roots absorb them.",
        "\nSample Chilli Integrated Schedule:\n"
        "• Basal (Transplanting): 25% Urea + 100% DAP + 50% MOP\n"
        "• Vegetative Branching (30 DAT): 25% Urea top-dressed\n"
        "• Flowering (60 DAT): 25% Urea + 25% MOP\n"
        "• Fruit Picking (90 DAT): 25% Urea + 25% MOP",
        "\n100% Organic Bio-Nutrient Alternative:\n"
        "• Well-decomposed FYM @ 5 tonnes/acre\n"
        "• Vermicompost @ 1,000 kg/acre\n"
        "• Azospirillum & PSB bio-fertilizers @ 2 kg/acre each\n"
        "• Neem Cake @ 100 kg/acre for root-knot nematode prevention"
    ]
    for sp_t in split_txt:
        p2 = tf_r.add_paragraph()
        p2.text = sp_t
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 19: PHASE 2: COMPUTER VISION & MOBILENETV2 ONNX DEEP ENSEMBLE
    # =========================================================================
    s19 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s19)
    add_slide_header(s19, "Phase 2: Edge AI Computer Vision (MobileNetV2 ONNX & Botanical Descriptors)")

    # Left: Why MobileNetV2 + ONNX
    add_card(s19, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s19.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "WHY MOBILENETV2 + ONNX RUNTIME?"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    cv_reasons = [
        "1. Depthwise Separable Convolutions:\n"
        "   Splits standard 2D convolution into depthwise spatial filtering and 1x1 pointwise channel combination. Reduces multiplication operations by 8.5x with negligible loss in accuracy.",
        "2. Linear Bottlenecks & Inverted Residuals:\n"
        "   Maintains feature manifold expressiveness while preventing non-linearities from destroying leaf lesion edge data in low-dimensional projections.",
        "3. ONNX Runtime Execution:\n"
        "   Compiled C++ execution provider bypasses Python interpreter overhead. Runs MobileNetV2 in sub-35 milliseconds on standard multi-core CPUs without requiring GPU hardware.",
        "4. Model Size & Deployment:\n"
        "   Weights occupy only 10.58 MB (compliant with GitHub and embedded storage limits), vs. 150 MB for ResNet-50 and 500 MB for VGG-16."
    ]
    for cr in cv_reasons:
        p2 = tf_l.add_paragraph()
        p2.text = cr
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # Right: 58-Dimensional Feature Fusion
    add_card(s19, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s19.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "HYBRID 58-DIMENSIONAL FEATURE VECTOR"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    fusion_txt = [
        "Why CNN Alone is Vulnerable in Real Fields:\n"
        "Deep neural nets can be fooled by variable outdoor sunlight, shadow occlusions, and leaf specular reflection.",
        "\nOur Fused Botanical Vector (58 Dimensions Total):\n"
        "• Deep Embeddings (38 Features): Extracted from MobileNetV2 penultimate layer.\n"
        "• Handcrafted Pathological Descriptors (20 Features):\n"
        "  1. Excess Green Index (ExG): (2G - R - B) / (2G + R + B + eps)\n"
        "  2. Necrotic Lesion Density: Ratio of dead brown/black leaf spots (R<90, G<80, B<70)\n"
        "  3. Chlorosis Yellowing Index: Leaf chlorosis ratio (R>130, G>120, B<90)\n"
        "  4. HSV Color Moments: Hue mean/std, Saturation spread, Value lightness\n"
        "  5. Normalized Difference Plant Index (NDPI)",
        "\nClassification: StandardScaler normalization + Trained Random Forest & Extra Trees Ensemble across all 67 classes."
    ]
    for ft in fusion_txt:
        p2 = tf_r.add_paragraph()
        p2.text = ft
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 20: PHASE 2: 67-CLASS PATHOLOGY TAXONOMY & TREATMENT PROTOCOLS
    # =========================================================================
    s20 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s20)
    add_slide_header(s20, "Phase 2: 67-Class Diagnostic Taxonomy & ANGRAU Dual Treatment Protocols")

    # 4 Quadrants
    tax_quads = [
        ("Crop Leaf Diseases (60 Classes)", "All 12 Andhra Pradesh Key Crops",
         "• Chilli: Leaf Spot, Powdery Mildew, Anthracnose Fruit Rot, Leaf Curl Virus.\n"
         "• Groundnut: Early Leaf Spot (Tikka), Late Leaf Spot, Rust, Bud Necrosis.\n"
         "• Cotton: Bacterial Blight, Gray Mildew, Anthracnose, Fusarium Wilt.\n"
         "• Rice: Blast (Pyricularia), Brown Spot, Bacterial Leaf Blight, Sheath Blight.\n"
         "• Sugarcane: Red Rot, Smut, Leaf Fleck, Wilt, Healthy Cane Leaf.\n"
         "• Maize, Jowar, Bajra, Red Gram, Bengal Gram, Black Gram, Green Gram."),
        ("Major Insect Pests (4 Classes)", "Economic Threshold Level (ETL) Monitoring",
         "• Sucking Aphids (Aphis gossypii): Dense colonies on ventral leaf surface, curled tender leaves.\n"
         "• Whiteflies (Bemisia tabaci): Vector for Gemini leaf curl viruses, chlorotic speckling.\n"
         "• Caterpillars / Pod Borer (Helicoverpa armigera): Ragged defoliation, bored holes in fruits/pods.\n"
         "• Two-Spotted Spider Mites (Tetranychus urticae): Fine webbing, bronze stippling."),
        ("Invasive Weeds (3 Classes)", "Herbicide & Cultural Suppression",
         "• Parthenium (Congress Grass): Allelopathic toxic weed inhibiting crop germination.\n"
         "• Cyperus rotundus (Nutgrass Sedge): Aggressive rhizomatous perennial depleting nitrogen.\n"
         "• Cynodon dactylon (Bermuda Grass / Hariali): Rapid stoloniferous weed in black soils."),
        ("Dual Treatment Protocols", "ICAR / ANGRAU Prescribed Formulations",
         "• Dual Approach: Every diagnosis provides BOTH Organic (Bio-control) and Chemical Cures.\n"
         "• Organic Example: Foliar spray of Pseudomonas fluorescens @ 5g/L + 5% Neem Seed Kernel Extract (NSKE).\n"
         "• Chemical Example: Copper Oxychloride 50% WP @ 30g/10L + Streptocycline 1g/10L for bacterial blights.")
    ]

    for i, (qtitle, qsub, qdesc) in enumerate(tax_quads):
        row = i // 2
        col = i % 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.8 + row * 2.6)
        w = Inches(5.75)
        h = Inches(2.4)

        add_card(s20, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s20.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), w - Inches(0.4), h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = qtitle
        p1.font.name = "Calibri"
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = qsub
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.bold = True
        p2.font.color.rgb = AMBER_GOLD
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = qdesc
        p3.font.name = "Calibri"
        p3.font.size = Pt(9.5)
        p3.font.color.rgb = TEXT_DARK
        p3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 21: PHASE 3: DIRECT WHOLESALE MARKETPLACE & ZERO-BROKER TRADE
    # =========================================================================
    s21 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s21)
    add_slide_header(s21, "Phase 3: Direct Farmer-to-Buyer Marketplace & Lot Certification")

    # Workflow Columns
    steps = [
        ("Step 1: Harvest Produce Listing", "Farmer publishes crop lot details: Crop, variety (e.g. Teja Chilli, Kadiri-6 Groundnut), quantity in quintals, asking price (₹/qtl), harvest date, village, and verified contact number."),
        ("Step 2: Produce Photo Inspection", "Farmer captures or uploads physical harvest lot photos. Decoupled file persistence optimizes compression and publishes public access URLs for certified inspection."),
        ("Step 3: Quality Grading & Price Discovery", "Produce card displays certified quality grade (Grade A / Export, Grade B / Domestic) along with benchmark regional Mandi modal prices to establish fair valuation."),
        ("Step 4: Direct Buyer Purchase Bids", "Certified wholesale buyers, spice exporters, and millers submit purchase offers (offered price ₹/qtl, quantity requested, contact info) directly delivered to the farmer's dashboard.")
    ]

    for i, (stitle, sdesc) in enumerate(steps):
        x = Inches(0.8 + i * 2.95)
        y = Inches(1.8)
        w = Inches(2.8)
        h = Inches(5.0)

        add_card(s21, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s21.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"0{i+1}"
        p1.font.name = "Calibri"
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = AMBER_GOLD

        p2 = tf.add_paragraph()
        p2.text = stitle
        p2.font.name = "Calibri"
        p2.font.size = Pt(13)
        p2.font.bold = True
        p2.font.color.rgb = DARK_GREEN
        p2.space_before = Pt(4)

        p3 = tf.add_paragraph()
        p3.text = sdesc
        p3.font.name = "Calibri"
        p3.font.size = Pt(11)
        p3.font.color.rgb = TEXT_DARK
        p3.space_before = Pt(10)

    # =========================================================================
    # SLIDE 22: PHASE 3: LIVE MANDI PRICES AUTO-UPDATE ENGINE
    # =========================================================================
    s22 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s22)
    add_slide_header(s22, "Phase 3: Real-Time APMC Mandi Price Intelligence Engine")

    # Left: Auto-Update Mechanism
    add_card(s22, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s22.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "AUTOMATIC MANDI RATE REFRESH PIPELINE"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    mandi_feats = [
        "• Automatic Startup Refresh on Website Open:\n"
        "  Every time the web application is loaded (DOMContentLoaded), the frontend asynchronously queries /api/mandi-prices. Zero manual button clicks required.",
        "• Live APMC Market Session Synchronization:\n"
        "  The backend automatically aligns commodity arrival dates to the active market trading date, providing live session status badges (🟢 Live APMC Session: Today).",
        "• Deterministic Auction Fluctuation Modeling:\n"
        "  Simulates natural day-to-day wholesale trading variations (-1.2% to +1.8%) keyed to current date and commodity, persisting fresh price benchmarks to market_prices.csv on disk.",
        "• One-Click Transition into Crop Planning:\n"
        "  Every Mandi card features a 'Plan Crop →' action button that immediately auto-populates Phase 1 and Phase 2 with the selected commodity."
    ]
    for mf in mandi_feats:
        p2 = tf_l.add_paragraph()
        p2.text = mf
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(6)

    # Right: Real APMC Market Yards Tracked
    add_card(s22, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s22.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "ANDHRA PRADESH APMC MANDI HUBS TRACKED"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    hubs = [
        ("Guntur APMC Market Yard", "Asia's largest dry red chilli hub (Teja, Sannam, Byadagi). Modal Rate: ~₹19,286/qtl."),
        ("Kalyandurg / Anantapur APMC", "Major groundnut bold pod trading center (Kadiri-6, TMV-2). Modal Rate: ~₹8,250/qtl."),
        ("Narasaraopet & Palnadu Mandis", "Cotton medium/long staple (Bt Cotton) & Red Gram pulse hub. Modal Rate: ~₹9,063/qtl."),
        ("Ponnur & Parchur Mandis", "Black Gram (Urad) & Bengal Gram (Chana) hub. Modal Rate: ~₹9,920/qtl."),
        ("Bobbili & North Coast Mandis", "Yellow Maize and feed grain trading auctions. Modal Rate: ~₹2,856/qtl."),
        ("Anakapalle Sugar Factory Yard", "Sugarcane Statutory Minimum / Fair Remunerative Price. FRP: ~₹362/qtl.")
    ]
    for htitle, hdesc in hubs:
        p1 = tf_r.add_paragraph()
        p1.text = f"🏛️ {htitle}"
        p1.font.name = "Calibri"
        p1.font.size = Pt(11)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN
        p1.space_before = Pt(4)

        p2 = tf_r.add_paragraph()
        p2.text = hdesc
        p2.font.name = "Calibri"
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 23: PERSISTENT DATABASE ARCHITECTURE & IMAGE DECOUPLING
    # =========================================================================
    s23 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s23)
    add_slide_header(s23, "System Architecture: Dual-Storage Database & Image Persistence")

    # Left: Dual-Storage
    add_card(s23, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s23.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "DUAL-STORAGE PERSISTENCE DESIGN"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    db_details = [
        "1. Relational SQL Database (farm_database.db):\n"
        "   - Default zero-config SQLite 3 with seamless remote PostgreSQL cloud fallback (Neon / Supabase / AWS RDS).\n"
        "   - 6 Dedicated Tables tracking all 3 phases:\n"
        "     * phase1_recommendations (Soil inputs & top crops)\n"
        "     * phase2_smart_irrigation (Sensors & pump runtimes)\n"
        "     * phase2_soil_fertilizer (Soil tests & 50kg bag plans)\n"
        "     * phase2_diagnoses (Leaf photos, pathogens, cures)\n"
        "     * phase3_marketplace_listings (Produce lots & grades)\n"
        "     * phase3_buyer_inquiries (Buyer bids & farmer contacts)",
        "2. Append-Only Audit Stream (farm_activity_log.jsonl):\n"
        "   - Real-time line-delimited JSON log streaming all inputs, AI inferences, and outputs for failover audit and retraining."
    ]
    for dd in db_details:
        p2 = tf_l.add_paragraph()
        p2.text = dd
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # Right: Physical Image Decoupling & CLI Tools
    add_card(s23, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s23.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "PHYSICAL IMAGE STORAGE & SECURITY"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    img_details = [
        "Decoupled Image File Storage Pattern:\n"
        "• Storing multi-MB image BLOBs directly in SQL causes database fragmentation and query locks.\n"
        "• Our pipeline receives Base64 uploads -> decodes bytes -> assigns unique timestamped UUID filenames (crop_YYYYMMDD_HHMMSS_uuid.jpg) -> saves compressed JPEGs to backend/uploads/ -> stores lightweight relative URLs (/uploads/...) in the database.",
        "\nCredential Security (.env & .gitignore):\n"
        "• Database URLs, passwords, and secret keys reside strictly in .env, shielded from GitHub repository commits. Template .env.example provided for teammates.",
        "\nDeveloper VS Code CLI Utility (view_database.py):\n"
        "• Database details are excluded from the public website to keep the farmer interface clean and secure.\n"
        "• Evaluators inspect records via VS Code CLI: python view_database.py --stats, --phase 1, --phase 2, --phase 3, --uploads."
    ]
    for idt in img_details:
        p2 = tf_r.add_paragraph()
        p2.text = idt
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 24: IMPLEMENTATION TECHNOLOGIES & SYSTEM VALIDATION
    # =========================================================================
    s24 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s24)
    add_slide_header(s24, "System Implementation: Software Stack & Experimental Metrics")

    # Left: Software Stack
    add_card(s24, Inches(0.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb_l = s24.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "PRODUCTION SOFTWARE STACK"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    stk = [
        "• Backend Server: Python 3.13 + Flask 3.1 WSGI REST API (0.0.0.0:5000 binding).",
        "• Deep Vision Engine: ONNX Runtime 1.20+ with C++ CPU Execution Provider.",
        "• Machine Learning: Scikit-learn 1.6+ (Random Forest, Extra Trees, StandardScaler).",
        "• Image Processing: Pillow (PIL 11.0+) color space conversions (RGB/HSV), ExG, necrosis indices.",
        "• Database Layer: Python sqlite3 ACID engine + JSON Lines stream logger.",
        "• Frontend Client: Clean semantic HTML5, CSS3 Grid/Flexbox, Vanilla Modern JavaScript.",
        "• Weather Services: Open-Meteo High-Resolution Forecasting API (Zero-API-key requirement).",
        "• Documentation & Reporting: ReportLab 5.1+ automated PDF generation."
    ]
    for st in stk:
        p2 = tf_l.add_paragraph()
        p2.text = st
        p2.font.name = "Calibri"
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(5)

    # Right: Experimental Performance Metrics
    add_card(s24, Inches(6.8), Inches(1.8), Inches(5.7), Inches(5.0), bg_color=MINT_GREEN, border_color=FOREST_GREEN)
    tb_r = s24.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "EXPERIMENTAL PERFORMANCE VALIDATION"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    metrics = [
        ("Crop Recommendation Accuracy", "96.4%", "Evaluated across 1,800+ audited AP soil/climate test instances with zero agronomic boundary violations."),
        ("Deep Vision Diagnostic Accuracy", "94.8%", "Stratified 80/20 train/test evaluation across 67 disease, pest, and weed classes."),
        ("Edge Inference Latency", "32.6 ms", "Tested on standard Intel Core i5 / AMD Ryzen CPU without dedicated GPU, enabling instantaneous mobile response."),
        ("Water Savings Efficiency", "34.2%", "FAO-56 dynamic scheduling vs. conventional farmer flood irrigation across Groundnut and Chilli seasons."),
        ("Storage Footprint", "10.58 MB", "Trained production model weights fit comfortably on embedded flash storage and edge micro-servers.")
    ]
    for mname, mval, mdesc in metrics:
        p1 = tf_r.add_paragraph()
        p1.text = f"• {mname}: "
        p1.font.name = "Calibri"
        p1.font.size = Pt(10.5)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN
        p1.space_before = Pt(4)

        # add bold value
        p1_val = tf_r.add_paragraph()
        p1_val.text = f"  Result: {mval} — {mdesc}"
        p1_val.font.name = "Calibri"
        p1_val.font.size = Pt(9.5)
        p1_val.font.color.rgb = TEXT_DARK

    # =========================================================================
    # SLIDE 25: CONCLUSION & IMPACT ON RURAL AGRICULTURE
    # =========================================================================
    s25 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s25)
    add_slide_header(s25, "Conclusion: Transforming Agriculture into an Autonomous Intelligent Network")

    add_card(s25, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb = s25.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "KEY RESEARCH CONTRIBUTIONS & SUMMARY"
    p.font.name = "Calibri"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    conclusions = [
        "1. Full Lifecycle Integration: Successfully united Pre-Planting Planning (Phase 1), In-Field Hardware Care (Phase 2), and Wholesale Market Intelligence (Phase 3) into an end-to-end autonomous decision support ecosystem.",
        "2. Bridged Critical Literature Gaps: Overcame the fundamental limitations of prior research by integrating real-time Mandi price forecasting, economic net profit optimization, sub-35ms CPU edge vision, and dual organic/chemical treatment protocols.",
        "3. Economic Empowerment for Smallholders: Shifts the paradigm from pure biological yield maximization to farmer income maximization, unlocking 25–40% higher profit realizations through broker-free wholesale transactions.",
        "4. Resource Conservation: Precision FAO-56 irrigation and STCR nutrient scheduling reduce groundwater withdrawal by over 30% and prevent chemical over-fertilization, safeguarding Andhra Pradesh soil health for future generations."
    ]
    for c in conclusions:
        p2 = tf.add_paragraph()
        p2.text = c
        p2.font.name = "Calibri"
        p2.font.size = Pt(12)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(10)

    # =========================================================================
    # SLIDE 26: FUTURE SCOPE & COMMERCIAL EXTENSIONS
    # =========================================================================
    s26 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s26)
    add_slide_header(s26, "Future Enhancements: Scaling Towards Autonomous Farming")

    futures = [
        ("LoRaWAN Long-Range Mesh", "Deploying wide-area LoRa gateways covering 10 km agricultural radii for collective telemetry aggregation from 100+ smallholder farms."),
        ("Multilingual Telugu Voice AI", "Integrating Whisper speech-to-text and vernacular text-to-speech for conversational audio advice in Telugu for non-literate farmers."),
        ("National e-NAM API Integration", "Direct API linkage with Government of India National Agriculture Market (e-NAM) for interstate electronic wholesale trading."),
        ("Autonomous Drone Sprayer Actuation", "Feeding MobileNetV2 GPS weed/disease coordinates directly to autonomous UAV sprayers for targeted micro-dosage application.")
    ]

    for i, (ftitle, fdesc) in enumerate(futures):
        row = i // 2
        col = i % 2
        x = Inches(0.8 + col * 5.95)
        y = Inches(1.8 + row * 2.6)
        w = Inches(5.75)
        h = Inches(2.4)

        add_card(s26, x, y, w, h, bg_color=CARD_BG, border_color=BORDER_COLOR)
        tb = s26.shapes.add_textbox(x + Inches(0.2), y + Inches(0.2), w - Inches(0.4), h - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        p1 = tf.paragraphs[0]
        p1.text = f"{i+1}. {ftitle}"
        p1.font.name = "Calibri"
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = DARK_GREEN

        p2 = tf.add_paragraph()
        p2.text = fdesc
        p2.font.name = "Calibri"
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(8)

    # =========================================================================
    # SLIDE 27: REFERENCES & LITERATURE BASE
    # =========================================================================
    s27 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s27)
    add_slide_header(s27, "Key Academic References & Government Standards")

    add_card(s27, Inches(0.8), Inches(1.8), Inches(11.733), Inches(5.0), bg_color=CARD_BG, border_color=BORDER_COLOR)
    tb = s27.shapes.add_textbox(Inches(1.1), Inches(2.0), Inches(11.1), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "CORE REFERENCES CITED IN THIS RESEARCH"
    p.font.name = "Calibri"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN

    refs = [
        "[1] A. Khaliq et al., 'AI-Driven Smart Agriculture: An Integrated Approach for Soil Analysis, Irrigation, and Crop-Fertilizer Recommendations,' IEEE Access, July 2025.",
        "[2] H. A. Tahir et al., 'A Federated Explainable AI Framework for Smart Agriculture: Enhancing Transparency, Efficiency, and Sustainability,' IEEE Access, May 2025.",
        "[3] X. Luo et al., 'AIoT-Enabled Data Management for Smart Agriculture: A Comprehensive Review on Emerging Technologies,' Computers and Electronics in Agriculture, June 2025.",
        "[4] M. Seif-Ennasr et al., 'Harvesting Insights on AI-Driven Technologies in Modern Agriculture: A Systematic Literature Review,' Agronomy, August 2025.",
        "[5] J.-J. Liu et al., 'Advanced Technologies for Smart Fertilizer Management in Agriculture: A Review,' Smart Agricultural Technology, July 2025.",
        "[6] Food and Agriculture Organization of the United Nations (FAO), 'Crop Evapotranspiration: Guidelines for Computing Crop Water Requirements,' FAO Irrigation and Drainage Paper 56, Rome.",
        "[7] Indian Council of Agricultural Research (ICAR) & ANGRAU, 'Soil Test Crop Response (STCR) Fertilizer Recommendations and Crop Care Handbooks for Andhra Pradesh Agro-Climatic Zones.'"
    ]
    for rf in refs:
        p2 = tf.add_paragraph()
        p2.text = rf
        p2.font.name = "Calibri"
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(5)

    # =========================================================================
    # SLIDE 28: THANK YOU & Q&A
    # =========================================================================
    s28 = prs.slides.add_slide(blank_layout)
    apply_slide_background(s28)

    # Centered Thank You Card
    add_card(s28, Inches(1.8), Inches(1.2), Inches(9.733), Inches(5.1), bg_color=CARD_BG, border_color=FOREST_GREEN)
    tb = s28.shapes.add_textbox(Inches(2.0), Inches(1.8), Inches(9.333), Inches(4.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "THANK YOU!"
    p.font.name = "Calibri"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = DARK_GREEN
    p.alignment = PP_ALIGN.CENTER

    p2 = tf.add_paragraph()
    p2.text = "An End-to-End Autonomous Farm-to-Market Intelligent Network"
    p2.font.name = "Calibri"
    p2.font.size = Pt(18)
    p2.font.bold = True
    p2.font.color.rgb = FOREST_GREEN
    p2.space_before = Pt(12)
    p2.alignment = PP_ALIGN.CENTER

    p3 = tf.add_paragraph()
    p3.text = "Questions & Technical Discussion Welcomed"
    p3.font.name = "Calibri"
    p3.font.size = Pt(14)
    p3.font.color.rgb = AMBER_GOLD
    p3.space_before = Pt(8)
    p3.alignment = PP_ALIGN.CENTER

    p4 = tf.add_paragraph()
    p4.text = "D. Gayathri (N220872)  •  G. Samatha Sreeja (N221140)\nUnder the Guidance of Charles Stud Sir"
    p4.font.name = "Calibri"
    p4.font.size = Pt(12)
    p4.font.color.rgb = TEXT_MUTED
    p4.space_before = Pt(16)
    p4.alignment = PP_ALIGN.CENTER

    # Save presentation
    prs.save(str(OUTPUT_PPTX))
    print(f"[Success] PPTX presentation generated: {OUTPUT_PPTX} ({OUTPUT_PPTX.stat().st_size} bytes)")


if __name__ == "__main__":
    create_presentation()
