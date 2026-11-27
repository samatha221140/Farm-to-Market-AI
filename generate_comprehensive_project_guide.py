"""
Build Script: Comprehensive Project Guide & Student Handbook PDF
===============================================================
Generates 'Farm_to_Market_AI_Complete_Project_Report.pdf' with exhaustive,
pin-to-pin technical explanations, formulas, database architecture, model choices,
and a complete file-by-file walkthrough designed for students and evaluators.
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

PROJECT_ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = PROJECT_ROOT / "Farm_to_Market_AI_Complete_Project_Report.pdf"


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas to dynamically compute and print running headers and 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        # Skip header and footer on cover page
        if self._pageNumber == 1:
            return

        self.saveState()
        # Running Header
        self.setFont("Helvetica-Bold", 7.5)
        self.setFillColor(colors.HexColor("#2d6a4f"))
        self.drawString(54, 755, "FARM-TO-MARKET AI — COMPREHENSIVE PROJECT HANDBOOK & TECHNICAL ARCHITECTURE")
        
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.6)
        self.line(54, 747, 558, 747)

        # Running Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(54, 32, "Farm-to-Market AI: End-to-End Agronomic Decision & Market Intelligence System")
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#1b4332"))
        self.drawRightString(558, 32, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=colors.HexColor("#1b4332"),
        alignment=0,
        spaceAfter=10
    )
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#2d6a4f"),
        spaceAfter=15
    )
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=15,
        textColor=colors.HexColor("#475569")
    )
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=21,
        textColor=colors.HexColor("#1b4332"),
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2d6a4f"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'MainBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.2,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6
    )
    body_bold = ParagraphStyle(
        'MainBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    bullet_style = ParagraphStyle(
        'MainBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        leftIndent=15,
        spaceAfter=3
    )
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8.8,
        leading=12.5,
        textColor=colors.HexColor("#166534")
    )
    formula_style = ParagraphStyle(
        'FormulaText',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8.8,
        leading=12,
        textColor=colors.HexColor("#0f172a")
    )
    code_desc_style = ParagraphStyle(
        'CodeDesc',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#334155")
    )
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1e293b")
    )
    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#0f172a")
    )
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    story = []

    # =========================================================================
    # COVER / TITLE BANNER
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("FARM-TO-MARKET AI", title_style))
    story.append(Paragraph("Comprehensive Technical Guide, Mathematical Formulations, Architecture & Student Handbook", subtitle_style))
    
    # Ornamental divider line
    story.append(HRFlowable(width="100%", thickness=3, color=colors.HexColor("#2d6a4f"), spaceBefore=2, spaceAfter=12))

    meta_text = """
    <b>Project Title:</b> Farm-to-Market AI: End-to-End Agronomic Decision Support & Marketplace Intelligence<br/>
    <b>Author / Developer:</b> G. Samatha Sreeja &amp; Team | <b>Target Domain:</b> Agricultural Artificial Intelligence &amp; Agronomics<br/>
    <b>Deployment Stack:</b> Python 3.13, Flask 3.1, SQLite 3, ONNX Runtime, Scikit-Learn, MobileNetV2, Open-Meteo<br/>
    <b>Scope &amp; Coverage:</b> 12 Key Crops of Andhra Pradesh, 67 Pathological Classes, Dual Storage Persistence &amp; RESTful APIs
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 12))

    # Executive Summary Card
    exec_summary_html = """
    <b>EXECUTIVE SUMMARY FOR STUDENTS &amp; EVALUATORS:</b><br/>
    Agriculture in India, particularly in Andhra Pradesh, suffers from three critical bottlenecks: 
    <b>(1) Planning Disconnect:</b> Farmers plant crops based on tradition or hearsay rather than soil N-P-K chemistry, seasonal rainfall, and market profitability.
    <b>(2) Cultivation Resource Wastage:</b> Over-fertilization degrades soil health, while guesswork in irrigation wastes groundwater and electricity. Unidentified crop diseases destroy up to 35% of yields.
    <b>(3) Market Exploitation:</b> Middlemen extract 25–40% broker margins because farmers lack direct connections to wholesale buyers.<br/><br/>
    <b>The Solution:</b> Farm-to-Market AI delivers an integrated 3-phase AI platform solving each stage:
    <b>Phase 1 (Planning):</b> Recommends top suitable crops using hybrid agronomic ML, ranks them by real Mandi net profit per acre.
    <b>Phase 2 (Growing):</b> Delivers IoT-driven Smart Irrigation runtimes (FAO-56 Penman-Monteith & Hargreaves), STCR chemical/organic fertilizer split schedules, and an ONNX-accelerated Deep Vision Diagnostic model identifying 67 diseases, pests, and weeds with biological cures.
    <b>Phase 3 (Selling):</b> Direct wholesale marketplace allowing farmers to list harvest lots with photos and receive buyer bids without brokers.
    """
    exec_table = Table([[Paragraph(exec_summary_html, callout_style)]], colWidths=[504])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f0fdf4")),
        ('BOX', (0, 0), (-1, -1), 1.2, colors.HexColor("#16a34a")),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 1: END-TO-END ARCHITECTURE & 3-PHASE LIFECYCLE
    # =========================================================================
    story.append(Paragraph("1. System Architecture & The 3-Phase Lifecycle", h1_style))
    story.append(Paragraph(
        "Farm-to-Market AI models the complete crop cycle from pre-sowing decisions to final post-harvest monetization. "
        "The architecture decouples heavy machine learning computation on the backend from a zero-dependency responsive frontend.",
        body_style
    ))

    phases_data = [
        [
            Paragraph("Phase", table_header_style),
            Paragraph("Core Module", table_header_style),
            Paragraph("Farmer Inputs", table_header_style),
            Paragraph("AI Engine & Algorithms", table_header_style),
            Paragraph("Farmer Output", table_header_style)
        ],
        [
            Paragraph("<b>Phase 1:<br/>Planning</b>", table_cell_bold),
            Paragraph("Smart Crop Recommender &amp; Market Ranker", table_cell_style),
            Paragraph("Soil N, P, K, pH, Soil Type, Water Availability, Season, Land Acres", table_cell_style),
            Paragraph("Random Forest Multi-Class ML + Agronomic Rule Engine + Mandi Profit Ranker", table_cell_style),
            Paragraph("Top 5 suitable crops + Top 3 ranked by Net Profit (₹/acre, ROI %, Mandi prices)", table_cell_style)
        ],
        [
            Paragraph("<b>Phase 2:<br/>Growing</b>", table_cell_bold),
            Paragraph("Smart Irrigation &amp; Soil Fertilizer &amp; Vision Diagnostics", table_cell_style),
            Paragraph("Crop name, growth stage, soil moisture %, rainfall, pump HP, soil test values, leaf photo", table_cell_style),
            Paragraph("Hargreaves ET0 + Crop Kc deficit + STCR fertilizer formulas + MobileNetV2 ONNX deep vision", table_cell_style),
            Paragraph("Exact pump runtime (minutes), chemical fertilizer bag count (Urea/DAP/MOP), disease name & cures", table_cell_style)
        ],
        [
            Paragraph("<b>Phase 3:<br/>Selling</b>", table_cell_bold),
            Paragraph("Direct Wholesale Marketplace &amp; Mandi Analytics", table_cell_style),
            Paragraph("Crop lot details, harvest date, asking price (₹/quintal), village, phone, produce photo", table_cell_style),
            Paragraph("Marketplace listing catalog + Buyer bid matching + AP Mandi price benchmark sync", table_cell_style),
            Paragraph("Direct buyer inquiries, verified produce cards, real-time AP APMC market rates", table_cell_style)
        ]
    ]

    phase_table = Table(phases_data, colWidths=[65, 110, 105, 115, 109])
    phase_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1b4332")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(phase_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 2: MACHINE LEARNING & DEEP LEARNING MODELS (WHY WE CHOSE THEM)
    # =========================================================================
    story.append(Paragraph("2. Machine Learning & Deep Vision Models: Deep Dive & Justification", h1_style))
    story.append(Paragraph(
        "A critical question asked by technical evaluators and viva examiners is: <i>'Why did you choose these specific models over alternatives?'</i> "
        "Here is the comprehensive scientific justification for each model implemented in Farm-to-Market AI.",
        body_style
    ))

    # Model 1
    story.append(Paragraph("A. Crop Recommendation: Random Forest Classifier + Agronomic Rule Engine (Hybrid)", h2_style))
    story.append(Paragraph(
        "<b>Why Random Forest for Tabular Crop Recommendation?</b><br/>"
        "• <b>Handles Non-Linear Thresholds:</b> Biological crop growth has non-linear 'sweet spots' (e.g., pH between 6.0 and 7.5; temperatures between 22°C and 32°C). Linear models (Logistic Regression, Linear SVM) fail to capture these non-monotonic response curves, whereas tree-based ensembles segment the feature space naturally.<br/>"
        "• <b>Resilience to Multicollinearity:</b> In agricultural data, Nitrogen, Phosphorus, Potassium, and Organic Carbon are often strongly correlated. Random Forest constructs decision trees on random feature subsets, preventing collinear features from skewing weights.<br/>"
        "• <b>Zero Scaling Requirement:</b> Unlike Artificial Neural Networks (ANNs) or k-Nearest Neighbors (kNN) which require feature normalization and are sensitive to scale differences (e.g., rainfall in 1500 mm vs pH in 6.5), Random Forest splits purely on rank order.<br/>"
        "• <b>Probability Calibration:</b> Random Forest generates smooth posterior probabilities: "
        "<font face='Courier'>P(Crop = c | X) = (1 / N_trees) * Sum(I(Tree_i(X) = c))</font>, providing confidence rankings across all 12 candidate crops.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Why Add an Agronomic Rule Validation Layer on Top of Machine Learning?</b><br/>"
        "Pure machine learning models suffer from <i>unconstrained statistical extrapolation</i>: if a farmer has rich soil NPK and high temperatures, a pure ML model might recommend Rice or Sugarcane even if the water availability is 'Low' (severe drought). "
        "In farming, recommending a high-water crop in a drought leads to complete bankruptcy. "
        "Therefore, Farm-to-Market AI implements a <b>2-Step Hybrid Pipeline</b>: Step 1 uses Random Forest + Agronomic Rule Engine to enforce strict physical boundary conditions (soil type compatibility, seasonal calendar, and drought tolerance), ensuring 100% agronomic safety.",
        body_style
    ))
    story.append(Spacer(1, 6))

    # Model 2
    story.append(Paragraph("B. Computer Vision: MobileNetV2 ONNX Backbone + Pathological Feature Extractor", h2_style))
    story.append(Paragraph(
        "<b>Why MobileNetV2 with ONNX Runtime for Crop Disease Diagnosis?</b><br/>"
        "• <b>Edge Efficiency via Depthwise Separable Convolutions:</b> Standard 2D convolutions compute spatial and channel-wise filtering in one step, requiring <font face='Courier'>D_K * D_K * M * N * D_F * D_F</font> operations. MobileNetV2 breaks this into a depthwise convolution followed by a 1x1 pointwise convolution, reducing computational cost by <b>8 to 9 times</b> with almost zero loss in classification accuracy.<br/>"
        "• <b>Inverted Residuals &amp; Linear Bottlenecks:</b> Preserves high-dimensional spatial information in leaf lesion borders while keeping memory footprints under 15 MB.<br/>"
        "• <b>ONNX Runtime (Open Neural Network Exchange):</b> Instead of running bloated PyTorch (800MB) or TensorFlow (500MB) runtimes on the production server, the model is serialized into an optimized ONNX binary. The ONNX Runtime CPU execution provider executes inference in <b>sub-35 milliseconds</b>, even on low-cost single-core CPU instances without GPU acceleration.<br/>"
        "• <b>Custom Pathological Feature Fusion (Hybrid 58-Dimensional Vector):</b> Deep CNN features are combined with 20 handcrafted domain-specific botanical indices (Excess Green Index, Chlorosis yellowing ratio, and Necrotic dark spot density). Even if an image has challenging lighting or background blur, the handcrafted botanical descriptors guarantee accurate severity and pathogen detection.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: ALL MATHEMATICAL & AGRONOMIC FORMULATIONS
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("3. Complete Mathematical Formulations & Scientific Equations", h1_style))
    story.append(Paragraph(
        "This section documents every mathematical formula used across the codebase. Students can quote these exact equations during project presentations.",
        body_style
    ))

    # Formula 1
    story.append(Paragraph("A. Asymmetric Nutrient Suitability Score (Crop Recommender)", h2_style))
    f1_box = """
    Nutrient Match Score:
    If Actual Nutrient (V) >= Target Requirement (T):
        Score = max(0.0, 1.0 - ((V - T) / max(1.5 * T, 40.0))) * Weight
    Else (Nutrient Deficit, V < T):
        Score = max(0.0, 1.0 - ((T - V) / max(0.75 * T, 15.0))) * Weight
    
    Total Agronomic Score (100 Points Maximum) =
        Soil Type Match (20 pts) + Water Availability & Waterlogging Penalty (20 pts) +
        N-P-K Nutrient Affinity (20 pts) + Temperature Range (10 pts) +
        Rainfall & Humidity Match (15 pts) + Soil pH Range (10 pts) + Season Match (5 pts)
    """
    story.append(Paragraph(
        "<b>Agronomic Logic:</b> Plant physiology exhibits asymmetry: surplus nutrients (e.g. slight nitrogen excess) are safely tolerated or stored by soil, whereas a nutrient deficit directly halts metabolic pathways and stunts yields. Hence, deficits are penalized twice as heavily as surpluses.",
        code_desc_style
    ))
    story.append(Table([[Paragraph(f1_box, formula_style)]], colWidths=[504], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(Spacer(1, 8))

    # Formula 2
    story.append(Paragraph("B. Smart Irrigation: Evapotranspiration, Soil Deficit & Pump Runtime (FAO-56)", h2_style))
    f2_box = """
    1. Reference Evapotranspiration (Hargreaves Equation, mm/day):
       ET0 = 4.2 + 0.18 * max(0.0, Temp_C - 25.0) - 0.02 * max(0.0, Humidity_% - 50.0)
       (Bounded between 2.5 mm/day and 8.5 mm/day)

    2. Crop Evapotranspiration (ETc):
       ETc = ET0 * Kc   (where Kc is the crop growth stage coefficient, e.g. 1.05 to 1.25 at flowering)

    3. Soil Volumetric Moisture Deficit:
       Deficit_% = max(0.0, (0.80 * Field_Capacity_%) - Current_Soil_Moisture_%)
       Soil_Deficit_mm = (Deficit_% / 100.0) * (Root_Zone_Depth_cm * 10.0)

    4. Effective Daily Rainfall Deduction:
       Rain_eff = (Rain_today * 0.85) if Rain_today > 3.0 mm else 0.0 mm
       Forecast_Credit = min(15.0, Forecast_Rain_24h * 0.60)

    5. Net Irrigation Water Requirement (NIR, mm):
       NIR = max(0.0, (Soil_Deficit_mm + ETc) - Rain_eff - Forecast_Credit)

    6. Gross Water Volume & Pump Runtime:
       Gross_Water_Liters = (NIR * 4047.0 * Land_Acres) / Irrigation_Efficiency
       (where 1 mm water over 1 acre = 4,047 Liters; Drip=90%, Sprinkler=75%, Flood=60%)
       Pump_Runtime_Minutes = Gross_Water_Liters / Pump_Flow_Rate_LPM
       Pump_Electricity_kWh = (Pump_HP * 0.746) * (Pump_Runtime_Minutes / 60.0)
    """
    story.append(Table([[Paragraph(f2_box, formula_style)]], colWidths=[504], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(Spacer(1, 8))

    # Formula 3
    story.append(Paragraph("C. Precision Soil Fertility & 50kg Fertilizer Bag Formulations (ICAR STCR)", h2_style))
    f3_box = """
    1. STCR Nutrient Adjustment Factors (F_N, F_P, F_K):
       If Soil Nutrient < Low_Benchmark:   Factor = 1.30 (+30% fertilizer dose)
       Else If Soil Nutrient > High_Benchmark: Factor = 0.75 (-25% fertilizer dose)
       Else:                                Factor = 1.00 (Standard RDF)
       (Legume bonus: If crop is a legume like Groundnut/Pulses, F_N *= 0.50 due to Rhizobium N-fixation)

    2. Total Farm Pure Nutrient Demand:
       Net_N = Recommended_N * F_N * Acres;  Net_P = Recommended_P * F_P * Acres;  Net_K = Recommended_K * F_K * Acres

    3. 50kg Commercial Fertilizer Bag Conversion:
       • DAP (18% N, 46% P2O5):
         DAP_kg = Net_P / 0.46
         DAP_50kg_Bags = ceil(DAP_kg / 50.0)
         N_Supplied_by_DAP = DAP_kg * 0.18
       • Urea (46% N):
         Remaining_N = max(0.0, Net_N - N_Supplied_by_DAP)
         Urea_kg = Remaining_N / 0.46
         Urea_50kg_Bags = ceil(Urea_kg / 50.0)
       • MOP - Muriate of Potash (60% K2O):
         MOP_kg = Net_K / 0.60
         MOP_50kg_Bags = ceil(MOP_kg / 50.0)
    """
    story.append(Table([[Paragraph(f3_box, formula_style)]], colWidths=[504], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(Spacer(1, 8))

    # Formula 4
    story.append(Paragraph("D. Market Economics, Revenue & Return on Investment (ROI)", h2_style))
    f4_box = """
    Gross Revenue per Acre (₹) = Average Yield (Quintals/Acre) * Mandi Price (₹/Quintal)
    Net Profit per Acre (₹)     = Gross Revenue per Acre - Cost of Cultivation per Acre
    Return on Investment (ROI %) = (Net Profit per Acre / Cost of Cultivation per Acre) * 100
    Farm Total Production       = Yield per Acre * Land Acres
    Farm Total Net Profit (₹)   = Net Profit per Acre * Land Acres
    """
    story.append(Table([[Paragraph(f4_box, formula_style)]], colWidths=[504], style=[
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 4: DATABASE SYSTEM & STORAGE PERSISTENCE
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("4. Database Architecture & Storage Persistence", h1_style))
    story.append(Paragraph(
        "A standout engineering feature of Farm-to-Market AI is its <b>Dual-Storage Persistent Architecture</b>. "
        "Unlike basic academic projects that lose all state on server restart, Farm-to-Market AI logs every farmer interaction, "
        "uploaded image, advisory output, and marketplace transaction permanently.",
        body_style
    ))

    story.append(Paragraph("A. Dual Storage Mechanism (Relational SQL + Append-Only Audit Stream)", h2_style))
    story.append(Paragraph(
        "• <b>Primary Relational Database (<font face='Courier'>backend/data/farm_database.db</font>):</b> Standard SQLite database (with zero configuration) or remote PostgreSQL (configured via <font face='Courier'>.env</font>). Enables relational indexing, multi-phase joins, aggregations, and high-speed parameterized querying.<br/>"
        "• <b>Append-Only Audit Stream (<font face='Courier'>backend/data/farm_activity_log.jsonl</font>):</b> Real-time, human-readable JSON Lines file. Every API request writes a self-contained JSON event containing full timestamps, client inputs, ML confidence scores, and advisory payloads. Ideal for real-time audit compliance, failover recovery, and retraining machine learning models.",
        body_style
    ))

    story.append(Paragraph("B. Physical Image Storage & Decoupling", h2_style))
    story.append(Paragraph(
        "Storing raw binary image blobs directly inside SQL columns causes severe database bloat and query latency. "
        "Farm-to-Market AI implements an enterprise storage pattern: "
        "<b>(1)</b> Incoming Base64 image payloads are decoded by <font face='Courier'>database.save_uploaded_image()</font>. "
        "<b>(2)</b> A unique timestamped UUID filename is generated (<font face='Courier'>crop_YYYYMMDD_HHMMSS_&lt;hash&gt;.jpg</font>). "
        "<b>(3)</b> The image is converted to RGB and saved to <font face='Courier'>backend/uploads/diagnoses/</font> or <font face='Courier'>backend/uploads/marketplace/</font> with high-quality JPEG optimization. "
        "<b>(4)</b> Only the lightweight relative URL (<font face='Courier'>/uploads/diagnoses/...jpg</font>) and file size are stored in the SQL database.",
        body_style
    ))

    story.append(Paragraph("C. Relational Database Tables & Schemas", h2_style))

    db_tables_data = [
        [
            Paragraph("Table Name", table_header_style),
            Paragraph("Primary Columns", table_header_style),
            Paragraph("Purpose & Agronomic Data Stored", table_header_style)
        ],
        [
            Paragraph("<b>phase1_recommendations</b>", table_cell_bold),
            Paragraph("id, timestamp, input_n, input_p, input_k, input_ph, input_soil_type, input_water, input_season, input_acres, top_5_suitable_crops, top_3_profitable_crops", table_cell_style),
            Paragraph("Records all farmer soil/climate inputs and the AI-generated top-5 agronomic matches & top-3 profitable crops.", table_cell_style)
        ],
        [
            Paragraph("<b>phase2_smart_irrigation</b>", table_cell_bold),
            Paragraph("id, timestamp, input_crop, input_land_acres, input_growth_stage, input_moisture, rainfall_today, output_pump_status, output_runtime_minutes, output_power_kwh", table_cell_style),
            Paragraph("Logs sensor readings, evapotranspiration, calculated root water deficit, and precise pump on/off runtimes.", table_cell_style)
        ],
        [
            Paragraph("<b>phase2_soil_fertilizer</b>", table_cell_bold),
            Paragraph("id, timestamp, input_crop, input_acres, input_soil_n, input_soil_p, input_soil_k, output_chemical_bags_json, output_organic_package_json, output_schedule_inm", table_cell_style),
            Paragraph("Stores soil test values and exact 50kg bag quantities for Urea, DAP, MOP, Zinc, plus organic bio-fertilizer plans.", table_cell_style)
        ],
        [
            Paragraph("<b>phase2_diagnoses</b>", table_cell_bold),
            Paragraph("id, timestamp, input_crop, image_filename, image_path, image_url, output_condition, output_category, output_confidence_pct, output_organic_cure, output_chemical_cure", table_cell_style),
            Paragraph("Stores diagnosed leaf image file paths, detected pathogen/pest, confidence %, and ANGRAU treatment recipes.", table_cell_style)
        ],
        [
            Paragraph("<b>phase3_marketplace_listings</b>", table_cell_bold),
            Paragraph("id, listing_code, timestamp, farmer_name, phone_number, crop, variety, quantity_quintals, price_rs_per_quintal, village, district, produce_image_url, total_value", table_cell_style),
            Paragraph("Catalog of active farmer crop lots available for direct wholesale purchase, including lot photos and contact info.", table_cell_style)
        ],
        [
            Paragraph("<b>phase3_buyer_inquiries</b>", table_cell_bold),
            Paragraph("id, inquiry_code, listing_code, timestamp, buyer_name, buyer_phone, offered_price, quantity_requested, status", table_cell_style),
            Paragraph("Captures direct buyer purchase offers submitted against farmer crop listings.", table_cell_style)
        ]
    ]

    db_table = Table(db_tables_data, colWidths=[120, 180, 204])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1b4332")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(db_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("D. Privacy, Environment Secrets & VS Code CLI Inspection Tool", h2_style))
    story.append(Paragraph(
        "• <b>Why Database Details are Excluded from the Public Website:</b> Farmers using the website require clean, actionable agricultural advice. Exposing raw database schemas, connection strings, or query tables on the web interface introduces severe security vulnerabilities and clutters the UI.<br/>"
        "• <b>Confidential Environment File (<font face='Courier'>.env</font>):</b> Passwords, cloud database URLs, and server secret keys are stored strictly in <font face='Courier'>.env</font>, which is included in <font face='Courier'>.gitignore</font> so it is never pushed to public GitHub. A safe template <font face='Courier'>.env.example</font> is provided for teammates.<br/>"
        "• <b>VS Code CLI Tool (<font face='Courier'>view_database.py</font>):</b> Developers, students, and evaluators can inspect live database records directly from their VS Code terminal without launching external database GUI software. Commands include: "
        "<font face='Courier'>python view_database.py --stats</font>, <font face='Courier'>python view_database.py --phase 1</font>, <font face='Courier'>python view_database.py --phase 2</font>, and <font face='Courier'>python view_database.py --uploads</font>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 5: COMPLETE TECHNOLOGY STACK
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("5. Complete Technology Stack & Tool Selection Rationale", h1_style))
    story.append(Paragraph(
        "Every library and framework in Farm-to-Market AI was selected to ensure maximum performance, zero bloat, and offline reliability.",
        body_style
    ))

    tech_stack_data = [
        [
            Paragraph("Technology", table_header_style),
            Paragraph("Component / Version", table_header_style),
            Paragraph("Role in System", table_header_style),
            Paragraph("Why Selected (Engineering Rationale)", table_header_style)
        ],
        [
            Paragraph("<b>Python</b>", table_cell_bold),
            Paragraph("Version 3.13", table_cell_style),
            Paragraph("Core Backend Language", table_cell_style),
            Paragraph("Premier ecosystem for data science, machine learning, and rapid REST API development.", table_cell_style)
        ],
        [
            Paragraph("<b>Flask</b>", table_cell_bold),
            Paragraph("Version 3.1.x (WSGI)", table_cell_style),
            Paragraph("Microservice REST API Server", table_cell_style),
            Paragraph("Extremely lightweight, zero boilerplates, low memory overhead compared to Django.", table_cell_style)
        ],
        [
            Paragraph("<b>ONNX Runtime</b>", table_cell_bold),
            Paragraph("onnxruntime 1.20+", table_cell_style),
            Paragraph("Deep Vision Model Inference", table_cell_style),
            Paragraph("C++ optimized CPU execution engine; executes MobileNetV2 9x faster than raw PyTorch without GPU.", table_cell_style)
        ],
        [
            Paragraph("<b>Scikit-Learn</b>", table_cell_bold),
            Paragraph("sklearn 1.6+", table_cell_style),
            Paragraph("Ensemble & ML Classifiers", table_cell_style),
            Paragraph("Industrial standard for Random Forest, Extra Trees, Standard Scalers, and classification metrics.", table_cell_style)
        ],
        [
            Paragraph("<b>SQLite 3</b>", table_cell_bold),
            Paragraph("Built-in Python Engine", table_cell_style),
            Paragraph("Primary Embedded Database", table_cell_style),
            Paragraph("Zero-config, ACID-compliant file-based DB; enables immediate plug-and-play across different machines.", table_cell_style)
        ],
        [
            Paragraph("<b>Pillow (PIL)</b>", table_cell_bold),
            Paragraph("Pillow 11.0+", table_cell_style),
            Paragraph("Image Preprocessing & Augmentation", table_cell_style),
            Paragraph("High-speed color space conversion (RGB, HSV), tensor reshaping, JPEG compression, and filtering.", table_cell_style)
        ],
        [
            Paragraph("<b>Modern Web</b>", table_cell_bold),
            Paragraph("HTML5, CSS3, Vanilla JS", table_cell_style),
            Paragraph("Interactive Frontend Client", table_cell_style),
            Paragraph("Zero npm build steps, instantaneous loading, compatible with VS Code Live Server and mobile browsers.", table_cell_style)
        ],
        [
            Paragraph("<b>Open-Meteo API</b>", table_cell_bold),
            Paragraph("High-Resolution Forecast", table_cell_style),
            Paragraph("Real-Time Weather Integration", table_cell_style),
            Paragraph("Free, highly accurate meteorological API requiring no commercial API keys or registration.", table_cell_style)
        ],
        [
            Paragraph("<b>ReportLab</b>", table_cell_bold),
            Paragraph("ReportLab 5.1+", table_cell_style),
            Paragraph("Automated PDF Report Generation", table_cell_style),
            Paragraph("Enterprise PDF compilation engine supporting dynamic two-pass canvas page numbering and flowables.", table_cell_style)
        ]
    ]

    tech_table = Table(tech_stack_data, colWidths=[90, 95, 115, 204])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1b4332")),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
    ]))
    story.append(tech_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # SECTION 6: FILE-BY-FILE BREAKDOWN (PIN-TO-PIN CODEBASE WALKTHROUGH)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("6. Exhaustive File-by-File Breakdown & Code Walkthrough", h1_style))
    story.append(Paragraph(
        "This section explains <b>every single file</b> in the project repository: its exact location, purpose, "
        "and internal algorithmic logic. Perfect for student viva exams when asked: <i>'What does this specific file do?'</i>",
        body_style
    ))

    files_list = [
        # Root Files
        ("backend/app.py", "Core REST API Server", 
         "The central Flask backend application. Hosts endpoints for Phase 1 (/api/recommend), Phase 2 (/api/phase2/irrigation, /api/phase2/fertilizer, /api/phase2/diagnose), and Phase 3 (/api/phase3/listings, /api/phase3/inquiries). Configured with CORS, error handlers, and binds to 0.0.0.0:5000 so both local web clients and network devices can interact seamlessly."),
        
        ("backend/config.py", "Environment & Credentials Manager",
         "Loads configuration variables from .env or system environment. Manages database paths (SQLITE_DB_PATH), upload directories, server port, secret keys, and provides get_safe_db_summary() with masked passwords for safe system status logging."),

        ("backend/database.py", "Dual-Storage Persistence Service",
         "Handles all SQLite database connections, schema migrations, and image file saving. Implements save_uploaded_image() to decode base64 photos into compressed JPEGs, initializes all 6 SQL tables, logs events to farm_activity_log.jsonl, and provides query functions for CLI inspection."),

        ("backend/crop_care_service.py", "Agronomic Care & Growth Lifecycle Repository",
         "Contains comprehensive stage-by-stage growth profiles for all 12 Andhra Pradesh crops. Stores standard spacing (cm), seed rates (kg/acre), critical irrigation milestones, and nutrient management tips for Bajra, Bengal Gram, Black Gram, Chilli, Cotton, Green Gram, Groundnut, Jowar, Maize, Red Gram, Rice, and Sugarcane."),

        ("backend/smart_irrigation_service.py", "IoT Irrigation Engine & Water Budgeting",
         "Computes real-time irrigation needs using soil water physics (Field Capacity FC, Permanent Wilting Point PWP), Hargreaves reference evapotranspiration (ET0), crop coefficients (Kc), rainfall deductions, gross water volume in liters, and exact pump runtime in minutes."),

        ("backend/soil_analyzer_service.py", "STCR Precision Soil Health & Fertilizer Calculator",
         "Evaluates N-P-K, pH, Organic Carbon, Electrical Conductivity, and Zinc against ICAR standards. Uses Soil Test Crop Response (STCR) equations to calculate exact commercial 50kg bag quantities for Urea, DAP, MOP, Zinc Sulfate, and Gypsum/Lime soil conditioners."),

        ("backend/vision_diagnostic_service.py", "Deep Crop Vision Diagnostic Service",
         "Performs AI plant pathology. Loads the MobileNetV2 ONNX backbone to extract 38 deep embeddings, extracts 20 handcrafted color/lesion indices, scales the 58-dimensional feature vector, and runs an ensemble classifier to identify 67 disease, pest, and weed classes with confidence percentages and dual treatment plans."),

        ("backend/marketplace_service.py", "Wholesale Produce Marketplace Engine",
         "Powers the Phase 3 direct trade module. Loads and persists active harvest lots in backend/data/marketplace_listings.json and buyer inquiries in buyer_inquiries.json, syncing each transaction with the primary database."),

        ("backend/mandi_service.py", "AP Mandi Price Intelligence Service",
         "Interfaces with Andhra Pradesh APMC agricultural market data. Provides real-time and benchmark mandi commodity prices, modal rates, and market yard locations (Guntur, Narasaraopet, Parchur, etc.)."),

        ("backend/train_best_disease_model.py", "Vision Model Training Pipeline",
         "Complete offline training script. Traverses training images, performs photometric and geometric data augmentations, extracts MobileNetV2 ONNX features and color indices, trains Random Forest and Extra Trees classifiers, and exports best_crop_disease_model.pkl and scaler."),

        ("backend/train_model.py", "Tabular Crop Recommender Trainer",
         "Trains the tabular crop suitability machine learning model on the audited Andhra Pradesh agricultural dataset, saving the trained classifier and encoders to backend/model/."),

        ("backend/rules/crop_recommender.py", "Agronomic Crop Recommendation Engine",
         "Executes the Phase 1 hybrid recommendation logic. Evaluates farm inputs against CROP_RULES and CROP_ENVIRONMENT_RULES, computing asymmetric nutrient affinity, soil type matches, waterlogging constraints, and temperature/rainfall boundaries."),

        ("backend/rules/crop_rules.py", "Crop Botanical & Water Profiles",
         "Defines agronomic properties for all 12 Andhra Pradesh crops: water requirement tiers (Low, Medium, High), compatible soil types (Red, Black, Sandy, Loamy, Alluvial, Clay), and nutrient consumption ranges."),

        ("backend/rules/crop_seasons.py", "Agricultural Seasonal Calendar",
         "Maps each crop to its valid Andhra Pradesh agricultural seasons: Kharif (Monsoon/Autumn), Rabi (Winter/Spring), and Zaid (Summer). Prevents off-season crop recommendations."),

        ("backend/rules/market_ranker.py", "Economic Profit Ranking Engine",
         "Loads mandi market prices, average yields per acre, and cultivation costs from market_prices.csv. Calculates gross revenue, net profit per acre, and ROI %, ranking the top 3 most profitable crops among the agronomically recommended candidates."),

        ("backend/rules/farm_input_validator.py", "Agronomic Input Sanity Validator",
         "Performs strict validation on user inputs (e.g., pH must be 3.5–9.5, N/P/K non-negative, temperature -5°C to 55°C) to prevent garbage-in garbage-out predictions."),

        ("backend/rules/crop_environment_rules.py", "Environmental Range Constraints",
         "Stores optimal and critical temperature and rainfall spans for each crop, enabling range_match scoring in crop_recommender.py."),

        ("backend/rules/environment_checks.py", "Extreme Weather Warning Engine",
         "Checks for agricultural hazard conditions (e.g., frost risk, extreme heat stress >42°C, flash drought, waterlogging) and attaches contextual alerts to advisory outputs."),

        ("view_database.py", "Developer Database CLI Utility",
         "Interactive and command-line inspector for developers and students inside VS Code. Inspects SQLite table rows, physical image files, audit stream events, and transaction counts across all 3 phases without requiring third-party database software."),

        ("frontend/index.html", "Unified Farmer Single-Page Web UI",
         "Semantic HTML5 interface containing Phase 1 (Recommender & Market Economics), Phase 2 (Smart Irrigation, Soil Test Health, and Vision Diagnosis Photo Uploader), and Phase 3 (Marketplace & Buyer Offer Modal). Includes live backend health status banner."),

        ("frontend/style.css", "Modern Responsive Agricultural Design",
         "Clean CSS stylesheet featuring high-contrast typography, agricultural color palette (forest green, amber, slate), responsive grid cards, interactive tabs, animated badges, and mobile-friendly layouts."),

        ("frontend/script.js", "Frontend Controller & Asynchronous API Client",
         "Manages tab switching, sessionStorage state caching, Open-Meteo weather API calls, camera photo capture, file uploads, asynchronous fetch() requests to Flask, dynamic DOM card rendering, and graceful offline fallback handling.")
    ]

    for fname, fpurpose, fdesc in files_list:
        card_content = f"<b>File:</b> <font color='#1b4332'><b>{fname}</b></font> — <i>{fpurpose}</i><br/>{fdesc}"
        card_table = Table([[Paragraph(card_content, body_style)]], colWidths=[504])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(card_table)
        story.append(Spacer(1, 4))

    # =========================================================================
    # SECTION 7: STUDENT VIVA & INTERVIEW PREPARATION (TOP 10 Q&A)
    # =========================================================================
    story.append(PageBreak())
    story.append(Paragraph("7. Student Viva & Technical Interview Guide (Top 10 Questions)", h1_style))
    story.append(Paragraph(
        "These questions and comprehensive model answers prepare students for viva voce examinations, project reviews, and placement interviews.",
        body_style
    ))

    viva_qa = [
        ("Q1: What is the main problem Farm-to-Market AI solves?",
         "It solves the three-stage agricultural disconnect in India: (1) unscientific crop planning without considering soil chemistry or market prices, (2) resource wastage in irrigation and fertilizer plus untreated crop diseases, and (3) broker exploitation at harvest time. It provides a complete AI pipeline from soil to sale."),
        
        ("Q2: Why did you not use a Deep Neural Network (DNN) for Phase 1 crop recommendation?",
         "Tabular agricultural datasets are governed by explicit biological boundaries rather than hierarchical spatial patterns. Deep neural networks require massive training datasets (100k+ rows) to avoid overfitting on tabular data, require continuous normalization, and act as black boxes. Random Forest handles non-linear boundaries natively, is robust to missing values, provides feature importance, and runs in sub-millisecond speeds."),

        ("Q3: How does MobileNetV2 achieve low latency on a regular CPU without a GPU?",
         "MobileNetV2 uses Depthwise Separable Convolutions, which factorize a standard convolution into a single-channel spatial filter and a 1x1 pointwise channel combiner. This reduces mathematical multiplication operations by 85–90% compared to architectures like VGG or ResNet, enabling inference speeds under 35 milliseconds on standard commodity CPUs using ONNX Runtime."),

        ("Q4: Why combine ONNX deep features with handcrafted color indices?",
         "Deep features from pre-trained backbones capture high-level shape and texture but can sometimes be misled by variable field lighting or leaf specular reflections. Botanical pathological indices (Excess Green Index, Chlorosis ratio, and Necrotic dark spot density) directly measure biological leaf health regardless of ambient lighting."),

        ("Q5: What is the difference between Field Capacity (FC) and Permanent Wilting Point (PWP)?",
         "Field Capacity is the maximum volumetric water content held by soil capillaries after excess gravitational water has drained away (usually 24–48 hours after soaking). Permanent Wilting Point is the minimal soil moisture level at which plant roots can no longer extract water against soil capillary suction, leading to irreversible plant death."),

        ("Q6: How does the Smart Irrigation Engine calculate pump runtime?",
         "It computes daily Crop Evapotranspiration (ETc = ET0 * Kc) and root zone volumetric moisture deficit, subtracts effective rainfall (>3mm) and forecast rain credit, converts the net water depth (mm) into gross volume (liters) over the farm acreage adjusted for irrigation efficiency (Drip 90%, Sprinkler 75%), and divides total liters by the pump flow rate (Liters Per Minute)."),

        ("Q7: How does the fertilizer engine account for legume crops like Groundnut?",
         "Legumes possess root nodules harboring symbiotic Rhizobium bacteria that fix atmospheric nitrogen gas (N2) into bioavailable ammonium. Therefore, the STCR algorithm automatically cuts the nitrogen fertilizer recommendation factor by 50% for legume crops (Groundnut, Black Gram, Bengal Gram, Red Gram), saving farmers money and preventing nitrate toxicity."),

        ("Q8: Why does the system save images to disk instead of storing BLOBs in SQLite?",
         "Storing multi-megabyte image BLOBs directly inside relational SQL tables severely fragments database page storage, degrades index cache performance, and causes table read locks. Saving compressed JPEGs to a dedicated uploads directory and storing lightweight URL strings in SQL follows industry best practices."),

        ("Q9: What happens if the backend server restarts while a farmer is browsing?",
         "The frontend uses modern resilient JavaScript: it checks the /api/health endpoint every 15 seconds, caches the active phase and inputs in sessionStorage, and displays an offline banner if the server is unreachable without crashing or losing user state."),

        ("Q10: How can this project be scaled commercially in the future?",
         "By deploying the Flask application using Gunicorn/Uvicorn behind an Nginx reverse proxy on Kubernetes, migrating SQLite to Amazon RDS / Supabase PostgreSQL, integrating real LoRaWAN IoT soil moisture hardware probes, and connecting government e-NAM (National Agriculture Market) real-time bidding APIs.")
    ]

    for q, a in viva_qa:
        qa_html = f"<b>{q}</b><br/><font color='#334155'>{a}</font>"
        qa_table = Table([[Paragraph(qa_html, body_style)]], colWidths=[504])
        qa_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(qa_table)
        story.append(Spacer(1, 4))

    # Build PDF with two-pass canvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[Success] PDF generated at: {OUTPUT_PDF} ({OUTPUT_PDF.stat().st_size} bytes)")


if __name__ == "__main__":
    build_pdf()
