"""
generate_project_ppt.py
Generates a 12-slide, 16:9 widescreen, 100% Canva-editable PowerPoint (.pptx)
for Farm-to-Market AI using a bright "Delight" color palette and native
vector shapes, flowcharts, block diagrams, and tables.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# =============================================================================
# DELIGHT COLOR PALETTE (Fresh, Bright, High-Contrast, Canva-Friendly)
# =============================================================================
BG_CREAM       = RGBColor(0xF6, 0xFB, 0xF8)   # Soft mint-cream slide background
BG_WHITE       = RGBColor(0xFF, 0xFF, 0xFF)   # Crisp card white
EMERALD_DARK   = RGBColor(0x15, 0x80, 0x3D)   # Deep emerald header/brand
EMERALD_MAIN   = RGBColor(0x16, 0xA3, 0x4A)   # Delight primary green
EMERALD_LIGHT  = RGBColor(0xDC, 0xFC, 0xE7)   # Soft mint fill
SKY_MAIN       = RGBColor(0x02, 0x84, 0xC7)   # Bright sky blue
SKY_LIGHT      = RGBColor(0xE0, 0xF2, 0xFE)   # Soft sky fill
AMBER_MAIN     = RGBColor(0xD9, 0x77, 0x06)   # Harvest gold/amber
AMBER_LIGHT    = RGBColor(0xFE, 0xF3, 0xC7)   # Soft warm cream
CORAL_MAIN     = RGBColor(0xE1, 0x1D, 0x48)   # Alert coral rose
CORAL_LIGHT    = RGBColor(0xFF, 0xE4, 0xE6)   # Soft rose fill
VIOLET_MAIN    = RGBColor(0x7C, 0x3A, 0xED)   # AI / Deep learning accent
VIOLET_LIGHT   = RGBColor(0xED, 0xE9, 0xFE)   # Soft lavender fill
TEXT_DARK      = RGBColor(0x1E, 0x29, 0x3B)   # Slate 800
TEXT_MUTED     = RGBColor(0x47, 0x55, 0x69)   # Slate 600
BORDER_SOFT    = RGBColor(0xCB, 0xD5, 0xE1)   # Light slate border

FONT_NAME = "Segoe UI"


def set_slide_bg(slide, color):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(slide, left, top, width, height, fill_color, border_color=None, border_pt=1.2, rounded=True):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, Inches(left), Inches(top), Inches(width), Inches(height))
    if rounded and len(shape.adjustments) > 0:
        shape.adjustments[0] = 0.06
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(border_pt)
    else:
        shape.line.fill.background()
    return shape


def add_arrow(slide, left, top, width, height, fill_color, direction="right"):
    shape_map = {
        "right": MSO_SHAPE.RIGHT_ARROW,
        "down": MSO_SHAPE.DOWN_ARROW,
        "left": MSO_SHAPE.LEFT_ARROW,
    }
    shape = slide.shapes.add_shape(shape_map[direction], Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.fill.background()
    return shape


def add_text_box(slide, left, top, width, height, text, font_size=12, bold=False,
                 color=TEXT_DARK, align=PP_ALIGN.LEFT, valign=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = Inches(0.06)
    tf.margin_right = Inches(0.06)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = FONT_NAME
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    return tb


def add_bullets(slide, left, top, width, height, items, font_size=11.5, color=TEXT_DARK, space_after=5):
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.03)
    tf.margin_bottom = Inches(0.03)
    for idx, item in enumerate(items):
        p = tf.paragraphs[0] if idx == 0 else tf.add_paragraph()
        p.space_after = Pt(space_after)
        if isinstance(item, tuple):
            lead, body = item
            r1 = p.add_run()
            r1.text = f"• {lead}: "
            r1.font.name = FONT_NAME
            r1.font.size = Pt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = color
            r2 = p.add_run()
            r2.text = body
            r2.font.name = FONT_NAME
            r2.font.size = Pt(font_size)
            r2.font.color.rgb = TEXT_MUTED
        else:
            r = p.add_run()
            r.text = f"• {item}"
            r.font.name = FONT_NAME
            r.font.size = Pt(font_size)
            r.font.color.rgb = color
    return tb


def add_header(slide, badge_text, title_text, subtitle_text, badge_color=EMERALD_MAIN, badge_bg=EMERALD_LIGHT):
    set_slide_bg(slide, BG_CREAM)
    # Top slim accent bar
    add_rect(slide, 0, 0, 13.333, 0.08, badge_color, rounded=False)
    # Pill badge
    badge = add_rect(slide, 0.55, 0.28, 2.35, 0.34, badge_bg, border_color=badge_color, border_pt=1.0)
    tf = badge.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = badge_text.upper()
    r.font.name = FONT_NAME
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = badge_color
    # Title & Subtitle
    add_text_box(slide, 0.55, 0.66, 12.2, 0.52, title_text, font_size=24, bold=True, color=TEXT_DARK)
    add_text_box(slide, 0.55, 1.15, 12.2, 0.34, subtitle_text, font_size=12, color=TEXT_MUTED)


def add_card(slide, left, top, width, height, title, accent_color=EMERALD_MAIN, fill_color=BG_WHITE, header_bg=None):
    card = add_rect(slide, left, top, width, height, fill_color, border_color=BORDER_SOFT, border_pt=1.0)
    if header_bg:
        add_rect(slide, left, top, width, 0.44, header_bg, border_color=None, rounded=False)
        add_rect(slide, left, top, 0.09, 0.44, accent_color, rounded=False)
        add_text_box(slide, left + 0.16, top + 0.05, width - 0.25, 0.36, title, font_size=13, bold=True, color=accent_color)
    else:
        add_rect(slide, left, top, width, 0.07, accent_color, rounded=False)
        add_text_box(slide, left + 0.14, top + 0.14, width - 0.28, 0.36, title, font_size=13, bold=True, color=accent_color)
    return card


def add_flow_node(slide, left, top, width, height, title, subtext, bg_color, border_color, title_color=TEXT_DARK):
    box = add_rect(slide, left, top, width, height, bg_color, border_color=border_color, border_pt=1.5)
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    p1 = tf.paragraphs[0]
    p1.alignment = PP_ALIGN.CENTER
    r1 = p1.add_run()
    r1.text = title
    r1.font.name = FONT_NAME
    r1.font.size = Pt(11.5)
    r1.font.bold = True
    r1.font.color.rgb = title_color
    if subtext:
        p2 = tf.add_paragraph()
        p2.alignment = PP_ALIGN.CENTER
        p2.space_before = Pt(3)
        r2 = p2.add_run()
        r2.text = subtext
        r2.font.name = FONT_NAME
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = TEXT_MUTED
    return box


def add_footer(slide, page_num):
    add_text_box(slide, 0.55, 7.12, 9.5, 0.28,
                 "Farm-to-Market AI  |  Phase 1–3 Precision Agriculture & Direct Marketplace",
                 font_size=9, color=TEXT_MUTED)
    add_text_box(slide, 11.8, 7.12, 1.0, 0.28, f"{page_num} / 12",
                 font_size=9, bold=True, color=EMERALD_MAIN, align=PP_ALIGN.RIGHT)


def build_presentation(output_path: Path):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE HERO SLIDE (DELIGHT PALETTE)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_bg(s1, BG_CREAM)
    # Decorative geometric shapes (Canva-editable)
    c1 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(9.8), Inches(-1.2), Inches(5.0), Inches(5.0))
    c1.fill.solid(); c1.fill.fore_color.rgb = EMERALD_LIGHT; c1.line.fill.background()
    c2 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.8), Inches(4.5), Inches(3.8), Inches(3.8))
    c2.fill.solid(); c2.fill.fore_color.rgb = SKY_LIGHT; c2.line.fill.background()
    c3 = s1.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1.0), Inches(5.2), Inches(3.0), Inches(3.0))
    c3.fill.solid(); c3.fill.fore_color.rgb = AMBER_LIGHT; c3.line.fill.background()

    add_rect(s1, 0, 0, 0.22, 7.5, EMERALD_MAIN, rounded=False)
    add_rect(s1, 0.9, 1.15, 3.2, 0.4, EMERALD_LIGHT, border_color=EMERALD_MAIN, border_pt=1.2)
    add_text_box(s1, 0.9, 1.18, 3.2, 0.35, "PRECISION AGRI-TECH ECOSYSTEM",
                 font_size=10.5, bold=True, color=EMERALD_DARK, align=PP_ALIGN.CENTER)

    add_text_box(s1, 0.9, 1.8, 9.2, 1.0, "Farm-to-Market AI", font_size=46, bold=True, color=TEXT_DARK)
    add_text_box(s1, 0.9, 2.75, 9.0, 0.9,
                 "End-to-End Intelligent Crop Planning, IoT & Vision Care,\nand Direct Farmer-to-Buyer Marketplace",
                 font_size=20, color=TEXT_MUTED)

    # 3 Phase Hero Pills
    phases = [
        ("PHASE 1: PLAN", "100-Pt Crop Suitability\n& Mandi Profit Ranking", EMERALD_MAIN, EMERALD_LIGHT),
        ("PHASE 2: CARE", "FAO-56 Irrigation, ICAR STCR\n& MobileNetV2 Vision AI", SKY_MAIN, SKY_LIGHT),
        ("PHASE 3: SELL", "Direct Harvest Lots (.jpg/.png)\n& MongoDB BSON Storage", AMBER_MAIN, AMBER_LIGHT),
    ]
    for i, (pt, ps, col, bg) in enumerate(phases):
        x = 0.9 + i * 3.85
        add_rect(s1, x, 4.25, 3.55, 1.45, BG_WHITE, border_color=col, border_pt=1.8)
        add_rect(s1, x, 4.25, 3.55, 0.42, bg, rounded=False)
        add_text_box(s1, x + 0.15, 4.3, 3.25, 0.32, pt, font_size=12, bold=True, color=col)
        add_text_box(s1, x + 0.15, 4.78, 3.25, 0.78, ps, font_size=12, color=TEXT_DARK)

    add_text_box(s1, 0.9, 6.45, 11.0, 0.4,
                 "Stack: Python Flask  •  MobileNetV2 ONNX + RandomForest  •  MongoDB NoSQL  •  HTML5 / JS",
                 font_size=11.5, bold=True, color=EMERALD_DARK)

    # =========================================================================
    # SLIDE 2: PROBLEM STATEMENT & WHY WE ARE DIFFERENT
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Overview", "Problem Statement & How Farm-to-Market AI Differs",
               "Bridging pre-sowing agronomy, real-time crop care, and middleman-free selling in one platform",
               EMERALD_MAIN, EMERALD_LIGHT)

    add_card(s2, 0.55, 1.75, 5.95, 5.1, "Traditional Farming Challenges", CORAL_MAIN, BG_WHITE, CORAL_LIGHT)
    add_bullets(s2, 0.75, 2.35, 5.55, 4.3, [
        ("Blind Crop Selection", "Farmers plant traditional crops without checking soil NPK deficits or mandi price trends."),
        ("Water & Fertilizer Waste", "Fixed pump schedules and uncalibrated urea/DAP dosing waste up to 40% water and capital."),
        ("Late Disease Diagnosis", "Pests, weeds, and fungal infections spread before local experts inspect leaves."),
        ("Middlemen Profit Cuts", "Farmers lose 20–35% of harvest value to aggregators and lack direct buyer visibility."),
        ("Disconnected Tools", "Separate apps for weather, soil cards, and markets force fragmented workflows."),
    ], font_size=12, space_after=10)

    add_card(s2, 6.8, 1.75, 5.95, 5.1, "Farm-to-Market AI Advantage", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s2, 7.0, 2.35, 5.55, 4.3, [
        ("Profit-Ranked Agronomy", "Scores 12 AP crops on 100-pt suitability, then ranks Top 3 by Net Profit (Rs/Acre)."),
        ("Physics + IoT Irrigation", "FAO-56 ETc water balance + soil FC/PWP calculates exact pump minutes & relay ON/OFF."),
        ("Hybrid Deep Vision AI", "MobileNetV2 ONNX + RandomForest + HSV pathology detects 67 Disease, Pest & Weed classes."),
        ("Dual Organic & Chemical Cures", "Every soil & disease result provides both organic bio-remedies and ICAR chemical doses."),
        ("Direct Marketplace + MongoDB", "Farmers upload .jpg/.png harvest photos; all 3 phases log cleanly into MongoDB Compass."),
    ], font_size=12, space_after=10)
    add_footer(s2, 2)

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE BLOCK DIAGRAM
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Architecture", "System Architecture Block Diagram",
               "Four-tier modular architecture connecting Farmer UI, Flask API, AI/Physics Engines, and MongoDB",
               SKY_MAIN, SKY_LIGHT)

    # Layer 1: Presentation
    add_rect(s3, 0.55, 1.7, 12.23, 1.05, EMERALD_LIGHT, border_color=EMERALD_MAIN, border_pt=1.5)
    add_text_box(s3, 0.7, 1.76, 2.5, 0.3, "1. PRESENTATION LAYER", font_size=10.5, bold=True, color=EMERALD_DARK)
    for i, (t, sub) in enumerate([
        ("Phase 1 UI", "Soil, Season & Profit"),
        ("Phase 2 UI", "Irrigation, STCR & Scanner"),
        ("Phase 3 UI", "Marketplace & .jpg/.png Lots"),
    ]):
        add_flow_node(s3, 3.2 + i * 3.15, 1.84, 2.9, 0.78, t, sub, BG_WHITE, EMERALD_MAIN, EMERALD_DARK)

    add_arrow(s3, 6.45, 2.8, 0.4, 0.3, SKY_MAIN, "down")

    # Layer 2: Flask API
    add_rect(s3, 0.55, 3.15, 12.23, 0.9, SKY_LIGHT, border_color=SKY_MAIN, border_pt=1.5)
    add_text_box(s3, 0.7, 3.22, 2.5, 0.3, "2. FLASK API GATEWAY", font_size=10.5, bold=True, color=SKY_MAIN)
    add_flow_node(s3, 3.2, 3.27, 9.2, 0.65,
                  "backend/app.py  (CORS Enabled  |  Threaded  |  Port 5000)",
                  "/api/recommend  •  /api/phase2/irrigation-advisory  •  /api/phase2/diagnose-image  •  /api/phase3/create-listing  •  /uploads/*",
                  BG_WHITE, SKY_MAIN, SKY_MAIN)

    add_arrow(s3, 6.45, 4.1, 0.4, 0.3, VIOLET_MAIN, "down")

    # Layer 3: AI & Domain Services
    add_rect(s3, 0.55, 4.45, 12.23, 1.2, VIOLET_LIGHT, border_color=VIOLET_MAIN, border_pt=1.5)
    add_text_box(s3, 0.7, 4.52, 2.8, 0.3, "3. AI & AGRONOMIC ENGINES", font_size=10.5, bold=True, color=VIOLET_MAIN)
    engines = [
        ("Crop + Market Ranker", "100-Pt Suitability\n+ Net Profit ROI"),
        ("Smart Irrigation", "FAO-56 ETc &\nPump Runtime"),
        ("STCR Soil Analyzer", "50 kg Bag Solver\n& Organic/INM"),
        ("Vision Deep Ensemble", "MobileNetV2 ONNX\n+ RF + HSV CV"),
    ]
    for i, (et, es) in enumerate(engines):
        add_flow_node(s3, 0.75 + i * 3.0, 4.85, 2.8, 0.7, et, es, BG_WHITE, VIOLET_MAIN, VIOLET_MAIN)

    add_arrow(s3, 6.45, 5.7, 0.4, 0.28, AMBER_MAIN, "down")

    # Layer 4: Persistence
    add_rect(s3, 0.55, 6.02, 12.23, 0.95, AMBER_LIGHT, border_color=AMBER_MAIN, border_pt=1.5)
    add_text_box(s3, 0.7, 6.08, 2.8, 0.3, "4. DATA & STORAGE LAYER", font_size=10.5, bold=True, color=AMBER_MAIN)
    add_flow_node(s3, 3.2, 6.14, 3.8, 0.72, "MongoDB (farm_to_market_ai)", "6 BSON Collections + Compass GUI", BG_WHITE, AMBER_MAIN, AMBER_MAIN)
    add_flow_node(s3, 7.2, 6.14, 2.6, 0.72, "SQLite Auto-Fallback", "farm_database.db + JSONL", BG_WHITE, AMBER_MAIN, TEXT_DARK)
    add_flow_node(s3, 10.0, 6.14, 2.5, 0.72, "Local Media Store", "uploads/diagnoses & marketplace", BG_WHITE, AMBER_MAIN, TEXT_DARK)
    add_footer(s3, 3)

    # =========================================================================
    # SLIDE 4: END-TO-END MASTER WORKFLOW FLOWCHART
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "Workflow", "End-to-End Master Workflow (Phase 1 → Phase 3)",
               "Seamless farmer journey from pre-sowing selection to field care and direct harvest sale",
               EMERALD_MAIN, EMERALD_LIGHT)

    # Row 1: Phase 1 -> Phase 2
    row1 = [
        ("1. Farm Inputs", "NPK, pH, Soil, Water,\nSeason, Acres", BG_WHITE, EMERALD_MAIN),
        ("2. Phase 1 Engine", "Suitability (100 pts)\n& Net Profit Rank", EMERALD_LIGHT, EMERALD_MAIN),
        ("3. Select Crop", "Pick Top Profit Crop\n-> Pass to Phase 2", BG_WHITE, EMERALD_MAIN),
        ("4. IoT & Soil Care", "FAO-56 Watering +\nSTCR Fertilizer Bags", SKY_LIGHT, SKY_MAIN),
    ]
    for i, (t, sub, bg, col) in enumerate(row1):
        x = 0.55 + i * 3.18
        add_flow_node(s4, x, 2.0, 2.65, 1.35, t, sub, bg, col, TEXT_DARK)
        if i < 3:
            add_arrow(s4, x + 2.72, 2.5, 0.38, 0.32, col, "right")

    # Connector down from Step 4 to Step 5
    add_arrow(s4, 11.2, 3.45, 0.38, 0.45, VIOLET_MAIN, "down")

    # Row 2: Right to Left or Left to Right? Left to Right is clearer with a clean return arrow, or 2nd row L->R!
    row2 = [
        ("5. Vision AI Scan", "Upload Crop Photo\nMobileNetV2 + CV", VIOLET_LIGHT, VIOLET_MAIN),
        ("6. Dual Cure Plan", "Organic Bio-Control\n& Chemical Spray", BG_WHITE, VIOLET_MAIN),
        ("7. List Harvest Lot", "Upload .jpg/.png\n& Asking Rs/Qtl", AMBER_LIGHT, AMBER_MAIN),
        ("8. Direct Sale", "Buyer Offer + WhatsApp\nLogged in MongoDB", EMERALD_LIGHT, EMERALD_MAIN),
    ]
    for i, (t, sub, bg, col) in enumerate(row2):
        x = 0.55 + i * 3.18
        add_flow_node(s4, x, 4.05, 2.65, 1.35, t, sub, bg, col, TEXT_DARK)
        if i < 3:
            add_arrow(s4, x + 2.72, 4.55, 0.38, 0.32, col, "right")

    # Bottom Summary Strip
    add_rect(s4, 0.55, 5.85, 12.23, 0.95, BG_WHITE, border_color=EMERALD_MAIN, border_pt=1.2)
    add_text_box(s4, 0.75, 5.95, 11.8, 0.3, "STATE CONTINUITY & PERSISTENCE ACROSS PHASES",
                 font_size=11.5, bold=True, color=EMERALD_DARK)
    add_text_box(s4, 0.75, 6.26, 11.8, 0.45,
                 "Selected crop, soil N-P-K, pH, and farm acreage carry automatically from Phase 1 into Phase 2 & Phase 3, while every transaction is stored in MongoDB (farm_to_market_ai).",
                 font_size=11, color=TEXT_MUTED)
    add_footer(s4, 4)

    # =========================================================================
    # SLIDE 5: PHASE 1 — CROP SUITABILITY MODEL & ALGORITHM
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Phase 1 • Part A", "Phase 1: Agronomic Crop Suitability Engine",
               "Evaluating 12 Andhra Pradesh crops using asymmetric nutrient matching & environmental guardrails",
               EMERALD_MAIN, EMERALD_LIGHT)

    add_card(s5, 0.55, 1.72, 4.0, 5.15, "What We Do in Phase 1", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s5, 0.72, 2.3, 3.65, 4.4, [
        ("Collect Farm Profile", "Soil N, P, K (kg/ha), pH, Soil Type, Water Level, Season, Temp, Rainfall, Humidity & Acres."),
        ("Validate Inputs", "farm_input_validator.py catches out-of-range pH or climate values."),
        ("Score 12 AP Crops", "Bajra, Bengal Gram, Black Gram, Chilli, Cotton, Green Gram, Groundnut, Jowar, Maize, Red Gram, Rice, Sugarcane."),
        ("Explainable Output", "Generates Top 5 Suitable Crops with per-factor score breakdown and stress warnings."),
    ], font_size=11.5, space_after=10)

    add_card(s5, 4.78, 1.72, 4.35, 5.15, "100-Point Scoring Algorithm", SKY_MAIN, BG_WHITE, SKY_LIGHT)
    add_bullets(s5, 4.95, 2.3, 4.0, 4.4, [
        ("Soil Compatibility (20 pts)", "Matches Red, Black, Loamy, Alluvial, Sandy soils against crop_rules.py."),
        ("Water & Waterlogging (20 pts)", "Penalizes deficit AND excess waterlogging (e.g., Bajra under high canal flow)."),
        ("Season Alignment (15 pts)", "Kharif, Rabi, Zaid suitability via crop_seasons.py."),
        ("Asymmetric nutrient_match()", "Penalizes N/P/K deficiencies steeply while tolerating mild nutrient surplus."),
        ("Climate range_match()", "Scores pH, Temp, Rainfall & Humidity against ICAR/APAU crop profiles."),
    ], font_size=11.5, space_after=8)

    add_card(s5, 9.35, 1.72, 3.43, 5.15, "Why This Model Is Used", AMBER_MAIN, BG_WHITE, AMBER_LIGHT)
    add_bullets(s5, 9.52, 2.3, 3.1, 4.4, [
        ("Transparent Decisions", "Farmers see exact reasons (e.g., 'pH too alkaline for Groundnut')."),
        ("Zero Black-Box Guesswork", "Guaranteed adherence to regional AP agricultural science."),
        ("Feeds Profit Ranker", "Top 5 biologically safe crops advance to economic profit ranking."),
    ], font_size=11.5, space_after=12)
    add_footer(s5, 5)

    # =========================================================================
    # SLIDE 6: PHASE 1 — MARKET ECONOMICS RANKER & FLOWCHART
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Phase 1 • Part B", "Phase 1: Market Economics Ranker & Workflow",
               "Combining agronomic suitability with AP Mandi price benchmarks to rank Top 3 Most Profitable Crops",
               EMERALD_MAIN, EMERALD_LIGHT)

    # Top cards: Formula + Use
    add_card(s6, 0.55, 1.7, 6.0, 2.55, "Market Profit Ranking Model (market_ranker.py)", AMBER_MAIN, BG_WHITE, AMBER_LIGHT)
    add_bullets(s6, 0.72, 2.25, 5.65, 1.9, [
        ("Data Source", "AP Mandi Benchmarks (Guntur, Kalyandurg, Kurnool, Ponnur) via market_prices.csv."),
        ("Gross Revenue", "Land Acres × Expected Yield (Qtl/Acre) × Modal Price (Rs/Qtl)."),
        ("Net Profit & ROI", "Net Profit = Gross Revenue − (Acres × Cultivation Cost/Acre)."),
    ], font_size=11.5, space_after=7)

    add_card(s6, 6.78, 1.7, 6.0, 2.55, "Use & Impact for Farmers", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s6, 6.95, 2.25, 5.65, 1.9, [
        ("Avoids Price Crashes", "Prevents farmers from picking high-yield crops with low market demand."),
        ("Live Acreage Slider", "Instant recalculation of total investment, revenue, and net profit as acres change."),
        ("1-Click Phase 2 Transition", "Clicking any ranked crop opens Phase 2 pre-loaded for that exact crop."),
    ], font_size=11.5, space_after=7)

    # Bottom Flowchart
    add_text_box(s6, 0.55, 4.45, 12.2, 0.32, "PHASE 1 WORKFLOW FLOWCHART", font_size=11.5, bold=True, color=EMERALD_DARK)
    p1_flow = [
        ("Farmer Inputs\n(NPK, Soil, Acres)", BG_WHITE, EMERALD_MAIN),
        ("validate_farm_inputs\n& check_environment", SKY_LIGHT, SKY_MAIN),
        ("recommend_crops()\n100-Pt Top 5 Crops", EMERALD_LIGHT, EMERALD_MAIN),
        ("market_ranker.py\nNet Profit Top 3", AMBER_LIGHT, AMBER_MAIN),
        ("MongoDB Log\nphase1_recommendations", BG_WHITE, VIOLET_MAIN),
    ]
    for i, (txt, bg, col) in enumerate(p1_flow):
        x = 0.55 + i * 2.52
        add_flow_node(s6, x, 4.88, 2.18, 1.45, txt, "", bg, col, TEXT_DARK)
        if i < 4:
            add_arrow(s6, x + 2.23, 5.45, 0.24, 0.28, col, "right")
    add_footer(s6, 6)

    # =========================================================================
    # SLIDE 7: PHASE 2 (PART A) — SMART IRRIGATION & IOT PUMP CONTROL
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Phase 2 • Irrigation", "Phase 2A: Smart Irrigation & IoT Pump Controller",
               "Physics-based FAO-56 evapotranspiration and soil-water balance for precision pump automation",
               SKY_MAIN, SKY_LIGHT)

    add_card(s7, 0.55, 1.7, 5.8, 2.85, "Algorithms & Models Used (smart_irrigation_service.py)", SKY_MAIN, BG_WHITE, SKY_LIGHT)
    add_bullets(s7, 0.72, 2.25, 5.45, 2.2, [
        ("FAO-56 Crop Evapotranspiration", "Computes ETc = ET0 × Kc using crop growth-stage Kc (0.40 to 1.25)."),
        ("Soil-Water Balance Model", "Uses soil Field Capacity (FC) & Wilting Point (PWP) across 6 soil textures."),
        ("Effective Rainfall Deduction", "Subtracts today's rain & 24h forecast before triggering irrigation."),
        ("Hydraulic Pump Runtime", "Adjusts litres by efficiency (Drip 90%, Sprinkler 75%, Flood 60%) ÷ Pump LPM."),
    ], font_size=11, space_after=6)

    add_card(s7, 6.55, 1.7, 6.23, 2.85, "What We Do & Why It Matters", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s7, 6.72, 2.25, 5.9, 2.2, [
        ("Live IoT Sensor Sync", "Reads soil moisture %, NPK, pH, and rainfall from /api/sensors/latest."),
        ("Exact Litres & Pump Minutes", "Tells farmer exact runtime (e.g., 'Turn Pump ON for 5h 22m') & kWh power."),
        ("Remote Relay Toggle", "1-Click Pump ON/OFF relay control via /api/irrigation/pump-control."),
        ("Saves Water & Energy", "Prevents root rot, nutrient leaching, and unnecessary borewell pumping."),
    ], font_size=11, space_after=6)

    # Flowchart
    add_text_box(s7, 0.55, 4.72, 12.2, 0.32, "SMART IRRIGATION DECISION FLOWCHART", font_size=11.5, bold=True, color=SKY_MAIN)
    irr_flow = [
        ("IoT Sensor / Input\nMoisture %, Rain, Temp", BG_WHITE, SKY_MAIN),
        ("FAO-56 ETc\nET0 × Stage Kc", SKY_LIGHT, SKY_MAIN),
        ("Root Zone Deficit\nFC − Current − Rain", EMERALD_LIGHT, EMERALD_MAIN),
        ("Pump Runtime\nLitres ÷ Eff ÷ LPM", AMBER_LIGHT, AMBER_MAIN),
        ("Relay ON/OFF &\nphase2_smart_irrigation", BG_WHITE, VIOLET_MAIN),
    ]
    for i, (txt, bg, col) in enumerate(irr_flow):
        x = 0.55 + i * 2.52
        add_flow_node(s7, x, 5.12, 2.18, 1.45, txt, "", bg, col, TEXT_DARK)
        if i < 4:
            add_arrow(s7, x + 2.23, 5.68, 0.24, 0.28, col, "right")
    add_footer(s7, 7)

    # =========================================================================
    # SLIDE 8: PHASE 2 (PART B) — SOIL HEALTH & DUAL FERTILIZER ENGINE
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_header(s8, "Phase 2 • Soil & NPK", "Phase 2B: ICAR Soil Health & Dual Fertilizer Engine",
               "Translating Soil Health Card lab readings into exact 50 kg fertilizer bags & organic bio-packages",
               AMBER_MAIN, AMBER_LIGHT)

    add_card(s8, 0.55, 1.72, 6.0, 2.75, "Models & Algorithms (soil_analyzer_service.py)", AMBER_MAIN, BG_WHITE, AMBER_LIGHT)
    add_bullets(s8, 0.72, 2.28, 5.65, 2.05, [
        ("ICAR / ANGRAU STCR Engine", "Soil Test Crop Response norms adjust pure N-P-K dose based on soil deficit."),
        ("Stoichiometric Bag Solver", "Converts kg N/P/K into exact 50 kg bags of DAP (18-46-0), Urea (46% N), MOP (60% K)."),
        ("pH & Micronutrient Guardrails", "Detects acidic (<6.0) or alkaline (>8.0) pH and Zinc (<0.6 ppm) deficiency."),
    ], font_size=11.5, space_after=8)

    add_card(s8, 6.78, 1.72, 6.0, 2.75, "Triple Output Package & Use", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s8, 6.95, 2.28, 5.65, 2.05, [
        ("Chemical Split Schedule", "Splits Urea/DAP/MOP across Basal, Vegetative, Flowering, and Picking stages."),
        ("100% Organic Package", "FYM/Compost tonnes, Vermicompost, Neem Cake, and Azospirillum/PSB biofertilizers."),
        ("INM + Soil Conditioners", "Prescribes Lime (acidic) or Gypsum (alkaline/Groundnut pegging) + logs to MongoDB."),
    ], font_size=11.5, space_after=8)

    # Visual Flow
    add_text_box(s8, 0.55, 4.65, 12.2, 0.32, "SOIL HEALTH TO FERTILIZER WORKFLOW", font_size=11.5, bold=True, color=AMBER_MAIN)
    soil_flow = [
        ("Soil Card Inputs\nN, P, K, pH, OC, EC, Zn", BG_WHITE, AMBER_MAIN),
        ("STCR Target Solver\nCrop Norm − Soil Credit", AMBER_LIGHT, AMBER_MAIN),
        ("50 kg Bag Calculator\nDAP, Urea, MOP, ZnSO4", SKY_LIGHT, SKY_MAIN),
        ("Dual Output Tabs\nOrganic / Chemical / INM", EMERALD_LIGHT, EMERALD_MAIN),
        ("MongoDB Storage\nphase2_soil_fertilizer", BG_WHITE, VIOLET_MAIN),
    ]
    for i, (txt, bg, col) in enumerate(soil_flow):
        x = 0.55 + i * 2.52
        add_flow_node(s8, x, 5.05, 2.18, 1.45, txt, "", bg, col, TEXT_DARK)
        if i < 4:
            add_arrow(s8, x + 2.23, 5.62, 0.24, 0.28, col, "right")
    add_footer(s8, 8)

    # =========================================================================
    # SLIDE 9: PHASE 2 (PART C) — AI CROP DISEASE, PEST & WEED DETECTION
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_header(s9, "Phase 2 • Vision AI", "Phase 2C: Hybrid Deep Ensemble for Disease, Pest & Weed Detection",
               "67-class domain-constrained MobileNetV2 ONNX + RandomForest + HSV Pathological Computer Vision",
               VIOLET_MAIN, VIOLET_LIGHT)

    # Left: 3 Model Pillar Cards
    add_card(s9, 0.55, 1.68, 6.1, 1.55, "1. MobileNetV2 ONNX Deep Backbone", VIOLET_MAIN, BG_WHITE, VIOLET_LIGHT)
    add_text_box(s9, 0.72, 2.2, 5.75, 0.9,
                 "plant_disease_mobilenet_v2.onnx extracts 38 deep convolutional logits from 224×224 normalized leaf/crop images via ONNX Runtime.",
                 font_size=11, color=TEXT_MUTED)

    add_card(s9, 0.55, 3.38, 6.1, 1.7, "2. HSV & RGB Pathological Segmentation", CORAL_MAIN, BG_WHITE, CORAL_LIGHT)
    add_text_box(s9, 0.72, 3.9, 5.75, 1.05,
                 "Measures Healthy Green (ExG), Chlorotic Yellowing, Necrotic Lesions, Rust Pustules, White Powdery/Whitefly Coatings, and Edge/Directional Texture (20-dim vector).",
                 font_size=11, color=TEXT_MUTED)

    add_card(s9, 0.55, 5.22, 6.1, 1.65, "3. Domain-Constrained Fusion + Remedies", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_text_box(s9, 0.72, 5.74, 5.75, 1.0,
                 "Filters 67 classes to the selected Crop/Pest/Weed, fuses RandomForest probabilities with biological symptom likelihoods, and outputs Organic & Chemical cures.",
                 font_size=11, color=TEXT_MUTED)

    # Right: Vertical Flowchart
    add_rect(s9, 6.9, 1.68, 5.88, 5.19, BG_WHITE, border_color=VIOLET_MAIN, border_pt=1.5)
    add_text_box(s9, 7.1, 1.8, 5.5, 0.34, "VISION DIAGNOSIS PIPELINE FLOWCHART",
                 font_size=12, bold=True, color=VIOLET_MAIN, align=PP_ALIGN.CENTER)

    v_steps = [
        ("Upload Image + Select Crop / Pest / Weed", VIOLET_LIGHT, VIOLET_MAIN),
        ("Feature Extraction: 38 CNN Logits + 20 CV Indices", SKY_LIGHT, SKY_MAIN),
        ("Domain Filter (67 Classes -> Target Crop / Category)", AMBER_LIGHT, AMBER_MAIN),
        ("Hybrid Fusion: ML Prob × Pathology Likelihood + Notes", EMERALD_LIGHT, EMERALD_MAIN),
        ("Save Image + Diagnose + Organic & Chemical Cures", CORAL_LIGHT, CORAL_MAIN),
    ]
    for i, (st, bg, col) in enumerate(v_steps):
        y = 2.25 + i * 0.9
        add_flow_node(s9, 7.25, y, 5.18, 0.62, st, "", bg, col, TEXT_DARK)
        if i < 4:
            add_arrow(s9, 9.7, y + 0.64, 0.28, 0.22, col, "down")
    add_footer(s9, 9)

    # =========================================================================
    # SLIDE 10: PHASE 3 — DIRECT MARKETPLACE & .JPG/.PNG UPLOAD WORKFLOW
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_header(s10, "Phase 3 • Marketplace", "Phase 3: Direct Farmer-to-Buyer Marketplace",
               "Middleman-free harvest lot publishing with .jpg/.png photo uploads, buyer bids, and WhatsApp connect",
               AMBER_MAIN, AMBER_LIGHT)

    add_card(s10, 0.55, 1.72, 6.0, 2.75, "What We Do in Phase 3", AMBER_MAIN, BG_WHITE, AMBER_LIGHT)
    add_bullets(s10, 0.72, 2.28, 5.65, 2.05, [
        ("Direct .jpg / .png Photo Upload", "Farmers upload real produce photos from phone/PC with instant thumbnail preview."),
        ("Server Storage & Serving", "Base64 images are decoded, saved in backend/uploads/marketplace/, and served via /uploads/."),
        ("Lot Valuation & Grading", "Tracks Crop, Variety, Grade A/A+, Quintals, Asking Rs/Qtl, and Total Lot Value."),
    ], font_size=11.5, space_after=8)

    add_card(s10, 6.78, 1.72, 6.0, 2.75, "Buyer Discovery & Direct Connect", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    add_bullets(s10, 6.95, 2.28, 5.65, 2.05, [
        ("Smart Search Filters", "Institutional buyers & millers filter live lots by Crop and District."),
        ("Direct Price Offer Modal", "Buyers submit offered Rs/Qtl & quantity needed via /api/phase3/buyer-inquiry."),
        ("1-Click WhatsApp Integration", "Pre-filled WhatsApp message opens direct chat with farmer's phone number."),
    ], font_size=11.5, space_after=8)

    # Phase 3 Flowchart
    add_text_box(s10, 0.55, 4.65, 12.2, 0.32, "PHASE 3 MARKETPLACE WORKFLOW", font_size=11.5, bold=True, color=AMBER_MAIN)
    p3_flow = [
        ("Farmer Harvest Form\nSpecs + .jpg/.png Photo", BG_WHITE, AMBER_MAIN),
        ("Save Image on Disk\n/uploads/marketplace/", SKY_LIGHT, SKY_MAIN),
        ("Publish Lot Card\nphase3_marketplace_listings", AMBER_LIGHT, AMBER_MAIN),
        ("Buyer Filter & Offer\nModal / WhatsApp", EMERALD_LIGHT, EMERALD_MAIN),
        ("MongoDB Inquiry Log\nphase3_buyer_inquiries", BG_WHITE, VIOLET_MAIN),
    ]
    for i, (txt, bg, col) in enumerate(p3_flow):
        x = 0.55 + i * 2.52
        add_flow_node(s10, x, 5.05, 2.18, 1.45, txt, "", bg, col, TEXT_DARK)
        if i < 4:
            add_arrow(s10, x + 2.23, 5.62, 0.24, 0.28, col, "right")
    add_footer(s10, 10)

    # =========================================================================
    # SLIDE 11: MONGODB DATABASE ARCHITECTURE & COMPASS INTEGRATION
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_header(s11, "Database", "MongoDB NoSQL Architecture & Resilient Fallback",
               "Structured BSON document storage across 6 collections inspectable via MongoDB Compass & mongosh",
               EMERALD_MAIN, EMERALD_LIGHT)

    # Left: 6 Collections grid
    add_card(s11, 0.55, 1.72, 7.6, 5.1, "6 Collections in Database: farm_to_market_ai", EMERALD_MAIN, BG_WHITE, EMERALD_LIGHT)
    cols_info = [
        ("phase1_recommendations", "Soil NPK, acres, Top 5 suitable & Top 3 profit rankings"),
        ("phase2_smart_irrigation", "ETc, moisture deficit, water litres & pump duration"),
        ("phase2_soil_fertilizer", "Soil ratings, 50 kg NPK bag counts & organic/INM plans"),
        ("phase2_diagnoses", "CNN + CV diagnosis, confidence, image path & dual cures"),
        ("phase3_marketplace_listings", "Lot ID, grade, quintals, price, farmer & .jpg/.png path"),
        ("phase3_buyer_inquiries", "Buyer name, phone, offered Rs/Qtl, quantity & status"),
    ]
    for i, (cname, cdesc) in enumerate(cols_info):
        col_x = 0.75 + (i % 2) * 3.68
        col_y = 2.35 + (i // 2) * 1.42
        add_flow_node(s11, col_x, col_y, 3.5, 1.22, cname, cdesc, BG_CREAM, EMERALD_MAIN, EMERALD_DARK)

    # Right: Why MongoDB + Resilience
    add_card(s11, 8.38, 1.72, 4.4, 2.45, "Why MongoDB NoSQL?", SKY_MAIN, BG_WHITE, SKY_LIGHT)
    add_bullets(s11, 8.55, 2.28, 4.05, 1.8, [
        ("Flexible Nested BSON", "Stores arrays of crops, split schedules & metadata without rigid SQL joins."),
        ("MongoDB Compass GUI", "Visual Tree/JSON/Table inspection without cluttering the farmer UI."),
    ], font_size=11, space_after=8)

    add_card(s11, 8.38, 4.35, 4.4, 2.47, "Zero-Downtime Fallback", AMBER_MAIN, BG_WHITE, AMBER_LIGHT)
    add_bullets(s11, 8.55, 4.9, 4.05, 1.8, [
        ("30s Cooldown Check", "Instant failover without request lag if MongoDB service is offline."),
        ("SQLite + JSONL Audit", "Auto-writes to farm_database.db & farm_activity_log.jsonl."),
    ], font_size=11, space_after=8)
    add_footer(s11, 11)

    # =========================================================================
    # SLIDE 12: SUMMARY MATRIX & FUTURE ROADMAP
    # =========================================================================
    s12 = prs.slides.add_slide(blank_layout)
    add_header(s12, "Summary", "Complete Model Matrix & Future Roadmap",
               "End-to-end summary of algorithms used across all 3 phases and upcoming enhancements",
               EMERALD_MAIN, EMERALD_LIGHT)

    # Native PowerPoint Table (Canva-editable!)
    rows, cols = 6, 4
    table_shape = s12.shapes.add_table(rows, cols, Inches(0.55), Inches(1.72), Inches(12.23), Inches(3.3))
    table = table_shape.table
    col_widths = [Inches(1.6), Inches(2.6), Inches(4.4), Inches(3.63)]
    for idx, w in enumerate(col_widths):
        table.columns[idx].width = w

    headers = ["Phase", "Module", "Model / Algorithm Used", "Core Purpose / Benefit"]
    matrix_data = [
        ["Phase 1", "Crop & Profit Engine", "100-Pt Asymmetric Scoring + Mandi Net Profit Ranker", "Selects biologically safe & highest-profit crops"],
        ["Phase 2A", "Smart Irrigation", "FAO-56 ETc + FC/PWP Soil-Water Balance + Pump LPM", "Saves 30–40% water & automates pump runtime"],
        ["Phase 2B", "Soil & Fertilizer", "ICAR/ANGRAU STCR + Stoichiometric 50 kg Bag Solver", "Delivers exact DAP/Urea/MOP bags + Organic/INM"],
        ["Phase 2C", "Vision AI Scanner", "MobileNetV2 ONNX + RandomForest + HSV Pathology CV", "Detects 67 Diseases, Pests & Weeds + dual cures"],
        ["Phase 3", "Direct Marketplace", "Image Upload (.jpg/.png) + MongoDB Document Store", "Middleman-free harvest sale & direct buyer offers"],
    ]

    for c_idx, h_text in enumerate(headers):
        cell = table.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = EMERALD_MAIN
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = cell.text_frame.paragraphs[0]
        r = p.add_run()
        r.text = h_text
        r.font.name = FONT_NAME; r.font.size = Pt(11.5); r.font.bold = True; r.font.color.rgb = BG_WHITE

    for r_idx, row_vals in enumerate(matrix_data, start=1):
        bg_c = BG_WHITE if r_idx % 2 == 1 else BG_CREAM
        for c_idx, val in enumerate(row_vals):
            cell = table.cell(r_idx, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_c
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.name = FONT_NAME; r.font.size = Pt(10.5)
            r.font.bold = (c_idx == 0)
            r.font.color.rgb = EMERALD_DARK if c_idx == 0 else TEXT_DARK

    # Future Scope Banner
    add_card(s12, 0.55, 5.22, 12.23, 1.65, "Future Roadmap & Scalability", SKY_MAIN, BG_WHITE, SKY_LIGHT)
    roadmap_items = [
        ("Live Agmarknet API", "Real-time mandi price feeds"),
        ("ESP32 MQTT Hardware", "Physical soil & relay sync"),
        ("Telugu Voice UI", "Vernacular audio guidance"),
        ("Satellite NDVI", "Regional crop health alerts"),
    ]
    for i, (rt, rs) in enumerate(roadmap_items):
        add_flow_node(s12, 0.75 + i * 3.0, 5.78, 2.8, 0.88, rt, rs, BG_CREAM, SKY_MAIN, SKY_MAIN)

    add_footer(s12, 12)

    prs.save(str(output_path))
    print(f"[Success] Generated Canva-editable presentation: {output_path} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "Farm_to_Market_AI_Presentation.pptx"
    build_presentation(out)
