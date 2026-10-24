# 🌱 Farm-to-Market AI

An Intelligent Agricultural Decision-Support System that bridges **Agronomic Suitability** with **Mandi Market Economics**.

---

## 🚀 Key Features

### 1. 🌾 Step 1: 5 Crop Recommendation by Soil & Climate Suitability
Evaluates 12 regional crops across South Indian & Andhra Pradesh agro-climatic conditions:
- **Water Availability**: Low (Dryland/Rainfed), Medium (Borewell/Semi-irrigated), High (Canal/Perennial).
- **Weather & Climate**: Temperature (°C), Relative Humidity (%), and Annual/Seasonal Rainfall (mm).
- **Nutrients (N-P-K)**: Soil Nitrogen, Phosphorus, Potassium levels (kg/ha).
- **Soil pH**: Optimal acidity/alkalinity tolerance ranges.
- **Soil Type**: Red, Black (Regur), Alluvial, Sandy, Loamy, Clay.
- **Cropping Season**: Kharif, Rabi, Summer.

Outputs the **Top 5 Most Suitable Crops** with compatibility score percentages (0–100%), matching badges, and agronomic advisory.

---

### 2. 💰 Step 2: 3 Crop Ranking by Market Price & Net Profit
Takes the candidate crops from Step 1 and evaluates financial viability:
- **Mandi Market Price**: Latest reported prices (₹ / quintal).
- **Average Yield**: Expected regional productivity (quintals / acre).
- **Cultivation Cost**: Input and operational expenses (₹ / acre).
- **Gross Revenue**: `Yield × Market Price`.
- **Estimated Net Profit**: `Gross Revenue − Cultivation Cost`.
- **Return on Investment (ROI %)** and **Profit per Quintal**.
- **Interactive Farm Scale Multiplier**: Drag the acreage slider to instantly view scaled totals for any farm size (e.g. 1 acre, 2.5 acres, 5 acres).

Outputs the **Top 3 Most Profitable Crops** with ranking badges (#1 Highest Earner, #2 High Return, #3 Strong Potential).

---

### 3. 🌦️ Real-Time Weather Intelligence
- City / District search powered by Open-Meteo.
- **⚡ "Apply Weather to Farm Inputs"** feature: auto-fills current temperature, humidity, and rainfall directly into the crop recommendation form with 1 click.

---

### 4. 🏪 Live Mandi Rates & Custom Profit Calculator
- Search commodity prices across Andhra Pradesh and Indian mandis.
- Fine-tune exact projected returns by entering custom yield, transport charges, and mandi fees.

---

## 🛠️ How to Run

### 1. Start the Flask Backend
Open a terminal in the project directory:
```powershell
cd "c:\Users\G samatha sreeja\Desktop\Farm-to-Market-AI\backend"
python app.py
```
The backend server runs on `http://127.0.0.1:5000`.

### 2. Launch the Frontend Website
Open `frontend/index.html` in any modern web browser, or serve it using Python's built-in HTTP server:
```powershell
cd "c:\Users\G samatha sreeja\Desktop\Farm-to-Market-AI\frontend"
python -m http.server 8000
```
Then visit: `http://127.0.0.1:8000`

---

## 📡 API Endpoints

- `GET /api/health` — Backend health and supported crops list
- `POST /api/recommend` — 2-stage recommendation pipeline (Top 5 Suitable + Top 3 Profitable)
- `POST /api/profit-estimate` — Dynamic farm profit calculator
- `GET /api/mandi-prices?crop=...&state=...` — Government / regional mandi prices
- `GET /api/market-summary` — Complete economic profiles for all crops
