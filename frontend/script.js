"use strict";

const API_BASE = "http://127.0.0.1:5000";

// State Management across Phase 1, Phase 2, and Phase 3
let currentPhase = 1;
let selectedCrop = "Groundnut";
let selectedAcreage = 2.0;
let farmerSoilData = { N: 45, P: 28, K: 38, pH: 6.8, soil_type: "Red", water_availability: "Low", rainfall: 650, temperature: 28.5 };
let cachedEconomicResult = null;
let currentLotForInquiry = null;

function getElement(id) {
    return document.getElementById(id);
}

function setStatus(id, message, type = "") {
    const element = getElement(id);
    if (!element) return;
    element.textContent = message;
    element.className = "status" + (type ? " " + type : "");
}

function setButtonLoading(id, loading, loadingText, normalText) {
    const button = getElement(id);
    if (!button) return;
    button.disabled = loading;
    button.textContent = loading ? loadingText : normalText;
}

function formatRupees(amount) {
    const num = Number(amount);
    if (!Number.isFinite(num)) return "₹0";
    return "₹" + Math.round(num).toLocaleString("en-IN");
}

function escapeHTML(str) {
    return String(str ?? "").replace(/[&<>"']/g, c => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[c]);
}

async function fetchJSON(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
        throw new Error(data.error || data.message || `HTTP request failed (${response.status})`);
    }
    return data;
}

/* ==========================================================================
   GLOBAL PHASE NAVIGATION (1 -> 2 -> 3)
   ========================================================================== */
function switchPhase(phaseNum) {
    currentPhase = Number(phaseNum);

    // Update Nav Buttons
    const navBtns = [getElement("navPhase1Btn"), getElement("navPhase2Btn"), getElement("navPhase3Btn")];
    navBtns.forEach((btn, idx) => {
        if (btn) btn.classList.toggle("active", idx + 1 === currentPhase);
    });

    // Update Phase Containers
    const containers = [getElement("phase1Container"), getElement("phase2Container"), getElement("phase3Container")];
    containers.forEach((c, idx) => {
        if (c) c.classList.toggle("active", idx + 1 === currentPhase);
    });

    // Update Active Crop Bar
    const activeBar = getElement("activeCropBar");
    if (activeBar) {
        activeBar.style.display = (currentPhase >= 2 || selectedCrop) ? "block" : "none";
        if (getElement("activeCropNameDisplay")) getElement("activeCropNameDisplay").textContent = selectedCrop;
        if (getElement("activeCropAreaDisplay")) getElement("activeCropAreaDisplay").textContent = `${selectedAcreage.toFixed(1)} Acres`;
    }

    // Phase-specific initializations
    if (currentPhase === 2) {
        loadPhase2Data();
    } else if (currentPhase === 3) {
        loadMarketplaceListings();
    }

    window.scrollTo({ top: 0, behavior: "smooth" });
}

getElement("navPhase1Btn")?.addEventListener("click", () => switchPhase(1));
getElement("navPhase2Btn")?.addEventListener("click", () => switchPhase(2));
getElement("navPhase3Btn")?.addEventListener("click", () => switchPhase(3));

getElement("quickJumpPhase2Btn")?.addEventListener("click", () => switchPhase(2));
getElement("quickJumpPhase3Btn")?.addEventListener("click", () => switchPhase(3));

/* ==========================================================================
   PHASE 1: WEATHER MODULE & AUTO-FILL
   ========================================================================== */
const weatherCodes = {
    0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
    45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain", 63: "Moderate Rain",
    65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
};

let latestFetchedWeather = null;

async function loadWeather(city) {
    if (!city.trim()) {
        setStatus("weatherStatus", "Please enter a valid city or district name.", "error");
        return;
    }

    setButtonLoading("refreshWeatherButton", true, "Fetching...", "Fetch Weather");
    setStatus("weatherStatus", "Querying meteorological coordinates...", "loading");

    try {
        const geoURL = new URL("https://geocoding-api.open-meteo.com/v1/search");
        geoURL.searchParams.set("name", city.trim());
        geoURL.searchParams.set("count", "1");
        geoURL.searchParams.set("language", "en");
        geoURL.searchParams.set("format", "json");

        const geo = await fetchJSON(geoURL.toString());
        const place = geo.results && geo.results[0];

        if (!place) {
            throw new Error(`Location "${city}" could not be found. Try another city in Andhra Pradesh/India.`);
        }

        const weatherURL = new URL("https://api.open-meteo.com/v1/forecast");
        weatherURL.searchParams.set("latitude", place.latitude);
        weatherURL.searchParams.set("longitude", place.longitude);
        weatherURL.searchParams.set("current", "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m");
        weatherURL.searchParams.set("daily", "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum");
        weatherURL.searchParams.set("forecast_days", "5");
        weatherURL.searchParams.set("timezone", "auto");

        const data = await fetchJSON(weatherURL.toString());
        const current = data.current;

        latestFetchedWeather = {
            temperature: Math.round(current.temperature_2m * 10) / 10,
            humidity: Math.round(current.relative_humidity_2m),
            precipitation: current.precipitation || 0,
            location: [place.name, place.admin1, place.country].filter(Boolean).join(", ")
        };

        const weatherContainer = getElement("currentWeather");
        if (weatherContainer) {
            weatherContainer.innerHTML = `
                <div class="weather-header">
                    <div>
                        <div class="weather-location">📍 ${escapeHTML(latestFetchedWeather.location)}</div>
                        <div class="section-desc">${escapeHTML(weatherCodes[current.weather_code] || "Fair Weather")}</div>
                    </div>
                    <div class="weather-temp-badge">${latestFetchedWeather.temperature}°C</div>
                </div>
                <div class="weather-grid-metrics">
                    <div class="metric-pill">
                        <div class="metric-label">Relative Humidity</div>
                        <div class="metric-val">${latestFetchedWeather.humidity}%</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-label">Precipitation</div>
                        <div class="metric-val">${current.precipitation} mm</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-label">Wind Velocity</div>
                        <div class="metric-val">${current.wind_speed_10m} km/h</div>
                    </div>
                    <div class="metric-pill">
                        <div class="metric-label">Perceived Temp</div>
                        <div class="metric-val">${Math.round(current.apparent_temperature)}°C</div>
                    </div>
                </div>
            `;
        }

        const forecastContainer = getElement("weatherForecast");
        if (forecastContainer && data.daily.time) {
            forecastContainer.innerHTML = data.daily.time.map((date, idx) => `
                <div class="forecast-cell">
                    <strong>${escapeHTML(date.slice(5))}</strong>
                    <div>${escapeHTML(weatherCodes[data.daily.weather_code[idx]] || "Clear")}</div>
                    <div class="forecast-temp">${Math.round(data.daily.temperature_2m_max[idx])}° / ${Math.round(data.daily.temperature_2m_min[idx])}°C</div>
                    <small>Rain: ${data.daily.precipitation_sum[idx] ?? 0} mm</small>
                </div>
            `).join("");
        }

        const applyBtn = getElement("applyWeatherBtn");
        if (applyBtn) applyBtn.disabled = false;

        setStatus("weatherStatus", `Weather synced for ${place.name}. You can click "Apply Weather to Farm Inputs".`, "success");
    } catch (err) {
        setStatus("weatherStatus", err.message, "error");
    } finally {
        setButtonLoading("refreshWeatherButton", false, "Fetching...", "Fetch Weather");
    }
}

getElement("applyWeatherBtn")?.addEventListener("click", () => {
    if (!latestFetchedWeather) return;
    if (getElement("Temperature_C")) getElement("Temperature_C").value = latestFetchedWeather.temperature;
    if (getElement("humidity")) getElement("humidity").value = latestFetchedWeather.humidity;
    farmerSoilData.temperature = latestFetchedWeather.temperature;
    farmerSoilData.humidity = latestFetchedWeather.humidity;
    setStatus("cropStatus", `Applied live weather (${latestFetchedWeather.temperature}°C, ${latestFetchedWeather.humidity}%) to farm inputs!`, "success");
});

getElement("refreshWeatherButton")?.addEventListener("click", () => {
    loadWeather(getElement("weatherCity")?.value || "");
});

/* ==========================================================================
   PHASE 1: PRESETS BAR
   ========================================================================== */
function applyPreset(preset) {
    if (preset === "dryland") {
        getElement("soil_type").value = "Red";
        getElement("water_availability").value = "Low";
        getElement("season").value = "Kharif";
        getElement("N_kg_ha").value = 35;
        getElement("P_kg_ha").value = 25;
        getElement("K_kg_ha").value = 32;
        getElement("pH").value = 6.8;
        getElement("Temperature_C").value = 29.5;
        getElement("humidity").value = 58;
        getElement("Rainfall_mm").value = 520;
        getElement("land_acres").value = 2.0;
        setStatus("cropStatus", "Loaded Rayalaseema Dryland preset (Red Soil, Low Water availability).", "success");
    } else if (preset === "wetland") {
        getElement("soil_type").value = "Alluvial";
        getElement("water_availability").value = "High";
        getElement("season").value = "Kharif";
        getElement("N_kg_ha").value = 85;
        getElement("P_kg_ha").value = 42;
        getElement("K_kg_ha").value = 48;
        getElement("pH").value = 7.1;
        getElement("Temperature_C").value = 27.5;
        getElement("humidity").value = 72;
        getElement("Rainfall_mm").value = 1350;
        getElement("land_acres").value = 3.0;
        setStatus("cropStatus", "Loaded Coastal Delta Wetland preset (Alluvial Soil, High Water availability).", "success");
    } else if (preset === "commercial") {
        getElement("soil_type").value = "Black";
        getElement("water_availability").value = "Medium";
        getElement("season").value = "Kharif";
        getElement("N_kg_ha").value = 80;
        getElement("P_kg_ha").value = 38;
        getElement("K_kg_ha").value = 55;
        getElement("pH").value = 7.2;
        getElement("Temperature_C").value = 26.5;
        getElement("humidity").value = 64;
        getElement("Rainfall_mm").value = 850;
        getElement("land_acres").value = 2.5;
        setStatus("cropStatus", "Loaded Guntur Commercial Cash Crop preset (Black Soil, Medium Water).", "success");
    }
}

getElement("presetDryland")?.addEventListener("click", () => applyPreset("dryland"));
getElement("presetWetland")?.addEventListener("click", () => applyPreset("wetland"));
getElement("presetBlackCommercial")?.addEventListener("click", () => applyPreset("commercial"));

/* ==========================================================================
   PHASE 1: RECOMMENDATION SUBMISSION & RENDERING
   ========================================================================== */
const farmForm = getElement("farmForm");

farmForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    selectedAcreage = Number(getElement("land_acres")?.value || 2.0);
    farmerSoilData = {
        soil_type: getElement("soil_type")?.value,
        water_availability: getElement("water_availability")?.value,
        season: getElement("season")?.value,
        land_acres: selectedAcreage,
        N: Number(getElement("N_kg_ha")?.value),
        P: Number(getElement("P_kg_ha")?.value),
        K: Number(getElement("K_kg_ha")?.value),
        pH: Number(getElement("pH")?.value),
        temperature: Number(getElement("Temperature_C")?.value),
        humidity: Number(getElement("humidity")?.value),
        rainfall: Number(getElement("Rainfall_mm")?.value),
    };

    if (getElement("liveAcreSlider")) getElement("liveAcreSlider").value = selectedAcreage;
    if (getElement("liveAcreValue")) getElement("liveAcreValue").textContent = selectedAcreage.toFixed(1);

    setButtonLoading("recommendButton", true, "Evaluating Suitability & Profit...", "🌾 Recommend 5 Suitable Crops & Top 3 Profitable Crops");
    setStatus("cropStatus", "Running agronomic engine & mandi profit optimizer...", "loading");

    try {
        const payload = {
            ...farmerSoilData,
            N_kg_ha: farmerSoilData.N,
            P_kg_ha: farmerSoilData.P,
            K_kg_ha: farmerSoilData.K,
            Temperature_C: farmerSoilData.temperature,
            Rainfall_mm: farmerSoilData.rainfall,
            Humidity_pct: farmerSoilData.humidity
        };

        const data = await fetchJSON(`${API_BASE}/api/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!data.success) {
            throw new Error(data.message || "Failed to retrieve crop recommendations.");
        }

        cachedEconomicResult = data;

        // Default active crop to the #1 profitable crop
        if (data.top_3_profitable_crops && data.top_3_profitable_crops.length > 0) {
            selectedCrop = data.top_3_profitable_crops[0].crop;
        }

        renderTop5SuitableCrops(data.top_5_suitable_crops || []);
        renderTop3ProfitableCrops(data.top_3_profitable_crops || [], selectedAcreage);
        renderEconomicsTable(data.all_candidate_economics || [], selectedAcreage);

        const resultsSection = getElement("resultsSection");
        if (resultsSection) {
            resultsSection.style.display = "block";
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        setStatus("cropStatus", "Recommendations generated! 5 Suitable crops and 3 Market Profit leaders identified.", "success");

    } catch (err) {
        setStatus("cropStatus", `${err.message}. Ensure Flask backend is running on port 5000.`, "error");
    } finally {
        setButtonLoading("recommendButton", false, "Evaluating Suitability & Profit...", "🌾 Recommend 5 Suitable Crops & Top 3 Profitable Crops");
    }
});

getElement("resetButton")?.addEventListener("click", () => {
    farmForm.reset();
    setStatus("cropStatus", "Form cleared.");
    const resultsSection = getElement("resultsSection");
    if (resultsSection) resultsSection.style.display = "none";
});

/* RENDER STEP 1: TOP 5 SUITABLE CROPS */
function renderTop5SuitableCrops(crops) {
    const grid = getElement("top5CardsGrid");
    if (!grid) return;

    if (!crops || crops.length === 0) {
        grid.innerHTML = `<p class="status error">No crop recommendations met the criteria.</p>`;
        return;
    }

    grid.innerHTML = crops.map((item, idx) => {
        const score = Number(item.score) || 0;
        const bd = item.breakdown || {};
        
        return `
            <div class="crop-card">
                <div>
                    <div class="crop-card-top">
                        <div>
                            <span class="badge ${score >= 85 ? 'badge-success' : 'badge-warning'}">Rank #${idx + 1} Candidate</span>
                            <h3 class="crop-name">${escapeHTML(item.crop)}</h3>
                        </div>
                        <div class="suitability-score-box">
                            <div class="suitability-number">${score}%</div>
                            <span class="suitability-label">Suitability</span>
                        </div>
                    </div>

                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width: ${Math.min(100, Math.max(10, score))}%;"></div>
                    </div>

                    <div class="crop-tags">
                        <span class="tag tag-water">💧 Water: ${escapeHTML(item.water_requirement || "Moderate")}</span>
                        <span class="tag tag-soil">🌱 Soils: ${escapeHTML((item.suitable_soils || []).join(", "))}</span>
                    </div>

                    <div class="breakdown-bars">
                        <div class="breakdown-row"><span>Soil Compatibility:</span><strong>${bd.soil_score ?? 20} / 20</strong></div>
                        <div class="breakdown-row"><span>Water Availability Match:</span><strong>${bd.water_score ?? 20} / 20</strong></div>
                        <div class="breakdown-row"><span>N-P-K Nutrients:</span><strong>${bd.npk_score ?? 20} / 20</strong></div>
                        <div class="breakdown-row"><span>Temperature & Weather:</span><strong>${bd.temperature_score ?? 10} / 10</strong></div>
                        <div class="breakdown-row"><span>Soil pH Match:</span><strong>${bd.ph_score ?? 10} / 10</strong></div>
                    </div>

                    <ul class="reasons-list">
                        ${(item.reasons || []).slice(0, 3).map(r => `<li>${escapeHTML(r)}</li>`).join("")}
                    </ul>
                </div>

                <button type="button" class="btn btn-primary select-crop-btn" onclick="selectCropAndGoToPhase2('${escapeHTML(item.crop)}')">
                    🌱 Plant ${escapeHTML(item.crop)} & Enter Phase 2 ➔
                </button>
            </div>
        `;
    }).join("");
}

/* RENDER STEP 2: TOP 3 PROFITABLE CROPS */
function renderTop3ProfitableCrops(crops, acres = 1.0) {
    const grid = getElement("top3CardsGrid");
    if (!grid) return;

    if (!crops || crops.length === 0) {
        grid.innerHTML = `<p class="status error">No market profit data available.</p>`;
        return;
    }

    const rankTitles = ["🏆 #1 Highest Net Profit", "🥈 #2 High Return Crop", "🥉 #3 Strong Market Potential"];

    grid.innerHTML = crops.map((item, idx) => {
        const netProfitPerAcre = Number(item.net_profit_per_acre) || 0;
        const totalProfit = netProfitPerAcre * acres;
        const grossRevenuePerAcre = Number(item.gross_revenue_per_acre) || 0;
        const costPerAcre = Number(item.cultivation_cost_per_acre) || 0;
        const yieldVal = Number(item.avg_yield_quintals_per_acre) || 0;
        const price = Number(item.price_rs_per_quintal) || 0;

        return `
            <div class="profit-card rank-${idx + 1}">
                <div class="rank-badge">${rankTitles[idx] || `#${idx + 1}`}</div>
                
                <div class="profit-card-header">
                    <h3 class="profit-crop-title">${escapeHTML(item.crop)}</h3>
                    <div class="profit-market-loc">🏛️ Mandi: ${escapeHTML(item.market || "Regional AP Market")}</div>
                </div>

                <div class="profit-highlight-box">
                    <div class="profit-highlight-label">Estimated Net Profit / Acre</div>
                    <div class="profit-highlight-value">${formatRupees(netProfitPerAcre)}</div>
                    <div class="total-farm-profit-callout">
                        Total for ${acres} Acres: <strong>${formatRupees(totalProfit)}</strong>
                    </div>
                </div>

                <ul class="finance-metrics-list">
                    <li><span class="metric-name">Market Price:</span><span class="metric-num">${formatRupees(price)} / quintal</span></li>
                    <li><span class="metric-name">Average Yield:</span><span class="metric-num">${yieldVal} q / acre (${(yieldVal * acres).toFixed(1)} q total)</span></li>
                    <li><span class="metric-name">Cultivation Cost:</span><span class="metric-num">${formatRupees(costPerAcre)} / acre</span></li>
                    <li><span class="metric-name">Gross Revenue:</span><span class="metric-num">${formatRupees(grossRevenuePerAcre)} / acre</span></li>
                    <li><span class="metric-name">Profit Margin:</span><span class="metric-num" style="color: var(--primary);">${item.roi_pct ?? 0}% ROI</span></li>
                </ul>

                <button type="button" class="btn btn-primary select-crop-btn" onclick="selectCropAndGoToPhase2('${escapeHTML(item.crop)}')">
                    🌱 Choose ${escapeHTML(item.crop)} & Start Phase 2 Growing ➔
                </button>
            </div>
        `;
    }).join("");
}

function renderEconomicsTable(candidates, acres = 1.0) {
    const tbody = getElement("candidateEconomicsBody");
    if (!tbody) return;

    const acresLabels = document.querySelectorAll(".table-acres-label");
    acresLabels.forEach(el => el.textContent = acres.toFixed(1));

    tbody.innerHTML = (candidates || []).map((item, idx) => {
        const profitPerAcre = Number(item.net_profit_per_acre) || 0;
        const totalProfit = profitPerAcre * acres;

        return `
            <tr>
                <td><strong>#${idx + 1} ${escapeHTML(item.crop)}</strong></td>
                <td>${formatRupees(item.price_rs_per_quintal)}</td>
                <td>${item.avg_yield_quintals_per_acre} q</td>
                <td>${formatRupees(item.cultivation_cost_per_acre)}</td>
                <td>${formatRupees(item.gross_revenue_per_acre)}</td>
                <td><strong style="color: #15803d;">${formatRupees(profitPerAcre)}</strong></td>
                <td><strong style="color: #15803d;">${formatRupees(totalProfit)}</strong></td>
                <td>
                    <button type="button" class="btn btn-secondary btn-sm" onclick="selectCropAndGoToPhase2('${escapeHTML(item.crop)}')">
                        Plant Crop ➔
                    </button>
                </td>
            </tr>
        `;
    }).join("");
}

/* INTERACTIVE LIVE ACRE SLIDER */
getElement("liveAcreSlider")?.addEventListener("input", (event) => {
    const acres = Number(event.target.value);
    selectedAcreage = acres;
    if (getElement("liveAcreValue")) getElement("liveAcreValue").textContent = acres.toFixed(1);

    if (cachedEconomicResult && cachedEconomicResult.top_3_profitable_crops) {
        renderTop3ProfitableCrops(cachedEconomicResult.top_3_profitable_crops, acres);
        renderEconomicsTable(cachedEconomicResult.all_candidate_economics, acres);
    }
});

/* TABS SWITCHER (TOP 5 vs TOP 3) */
getElement("tabTop5Btn")?.addEventListener("click", () => {
    getElement("tabTop5Btn")?.classList.add("active");
    getElement("tabTop3Btn")?.classList.remove("active");
    getElement("viewTop5")?.classList.add("active");
    getElement("viewTop3")?.classList.remove("active");
});

getElement("tabTop3Btn")?.addEventListener("click", () => {
    getElement("tabTop3Btn")?.classList.add("active");
    getElement("tabTop5Btn")?.classList.remove("active");
    getElement("viewTop3")?.classList.add("active");
    getElement("viewTop5")?.classList.remove("active");
});

/* MANDI PRICES LOOKUP */
getElement("mandiForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const crop = getElement("mandiCrop")?.value.trim() || "";
    const state = getElement("mandiState")?.value.trim() || "Andhra Pradesh";
    const district = getElement("mandiDistrict")?.value.trim() || "";

    setButtonLoading("searchMandiButton", true, "Searching...", "Search Mandi Rates");
    setStatus("mandiStatus", "Loading mandi arrivals...", "loading");

    try {
        const q = new URLSearchParams({ crop, state });
        if (district) q.set("district", district);
        const data = await fetchJSON(`${API_BASE}/api/mandi-prices?${q.toString()}`);
        const container = getElement("mandiResults");
        if (!container) return;

        if (!data.records || data.records.length === 0) {
            container.innerHTML = `<p class="status">No matching records found.</p>`;
            setStatus("mandiStatus", "Zero records found.", "error");
            return;
        }

        container.innerHTML = data.records.map(record => `
            <div class="mandi-record-card">
                <div class="mandi-card-header">
                    <div>
                        <div class="mandi-crop-name">${escapeHTML(record.crop)}</div>
                        <div class="mandi-market-name">🏛️ ${escapeHTML(record.market)}, ${escapeHTML(record.district || record.state)}</div>
                    </div>
                    <span class="badge badge-market">Mandi Price</span>
                </div>
                <div class="mandi-price-box">
                    <div class="mandi-modal-price">${formatRupees(record.modal_price_rs_per_quintal)} / qtl</div>
                    <div class="mandi-range">Range: ${formatRupees(record.min_price_rs_per_quintal)} – ${formatRupees(record.max_price_rs_per_quintal)}</div>
                </div>
                <div style="font-size: 0.8rem; color: var(--text-subtle);">
                    📅 Date: ${escapeHTML(record.arrival_date || "Recent")}
                </div>
            </div>
        `).join("");

        setStatus("mandiStatus", `Loaded ${data.records.length} mandi records.`, "success");
    } catch (err) {
        setStatus("mandiStatus", err.message, "error");
    } finally {
        setButtonLoading("searchMandiButton", false, "Searching...", "Search Mandi Rates");
    }
});


/* ==========================================================================
   TRANSITION TO PHASE 2 (CROP SELECTED)
   ========================================================================== */
window.selectCropAndGoToPhase2 = function(cropName) {
    selectedCrop = cropName;
    if (getElement("careCropSelector")) getElement("careCropSelector").value = cropName;
    if (getElement("postCrop")) getElement("postCrop").value = cropName;
    switchPhase(2);
};


/* ==========================================================================
   PHASE 2: CROP GROWING CARE (IRRIGATION, FERTILIZER, PESTS)
   ========================================================================== */
async function loadPhase2Data() {
    const crop = selectedCrop || "Groundnut";
    if (getElement("phase2CropTitle")) getElement("phase2CropTitle").textContent = `Active Cultivation Care: ${crop}`;
    if (getElement("careCropSelector")) getElement("careCropSelector").value = crop;

    const stage = getElement("careGrowthStage")?.value || "Flowering & Pegging / Tasseling (35-65 DAS)";

    // 1. Fetch Fertilizer Plan
    try {
        const fertData = await fetchJSON(`${API_BASE}/api/phase2/fertilizer-plan`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                crop: crop,
                soil_n: farmerSoilData.N || 45,
                soil_p: farmerSoilData.P || 28,
                soil_k: farmerSoilData.K || 38,
                acres: selectedAcreage
            })
        });

        if (fertData.success && fertData.plan) {
            const p = fertData.plan;
            const bags = p.total_farm_bags_50kg;
            const kg = p.per_acre_requirements;

            if (getElement("dapBagsDisplay")) getElement("dapBagsDisplay").textContent = `${bags.dap_bags} Bags`;
            if (getElement("dapKgDisplay")) getElement("dapKgDisplay").textContent = `${(kg.dap_kg * selectedAcreage).toFixed(1)} kg total (${kg.dap_kg} kg/acre)`;

            if (getElement("ureaBagsDisplay")) getElement("ureaBagsDisplay").textContent = `${bags.urea_bags} Bags`;
            if (getElement("ureaKgDisplay")) getElement("ureaKgDisplay").textContent = `${(kg.urea_kg * selectedAcreage).toFixed(1)} kg total (${kg.urea_kg} kg/acre)`;

            if (getElement("mopBagsDisplay")) getElement("mopBagsDisplay").textContent = `${bags.mop_bags} Bags`;
            if (getElement("mopKgDisplay")) getElement("mopKgDisplay").textContent = `${(kg.mop_kg * selectedAcreage).toFixed(1)} kg total (${kg.mop_kg} kg/acre)`;

            if (getElement("gypsumBagsDisplay")) getElement("gypsumBagsDisplay").textContent = `${bags.gypsum_bags} Bags`;
            if (getElement("gypsumKgDisplay")) getElement("gypsumKgDisplay").textContent = `${(kg.gypsum_kg * selectedAcreage).toFixed(1)} kg total (${kg.gypsum_kg} kg/acre)`;

            const scheduleList = getElement("fertScheduleList");
            if (scheduleList) {
                scheduleList.innerHTML = p.application_schedule.map(st => `<li><strong>${escapeHTML(st)}:</strong> Follow split dose guidelines.</li>`).join("");
            }
        }
    } catch (e) {
        console.error("Fertilizer error:", e);
    }

    // 2. Fetch Smart Irrigation Advisory
    try {
        const irrData = await fetchJSON(`${API_BASE}/api/phase2/irrigation-advisory`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                crop: crop,
                soil_type: farmerSoilData.soil_type || "Red",
                growth_stage: stage,
                recent_rain_mm: 0.0,
                temperature: farmerSoilData.temperature || 29.5
            })
        });

        if (irrData.success && irrData.advisory) {
            const adv = irrData.advisory;
            if (getElement("dailyWaterLiters")) getElement("dailyWaterLiters").textContent = `${adv.daily_water_need_liters_per_acre.toLocaleString("en-IN")} L`;
            if (getElement("dailyWaterMm")) getElement("dailyWaterMm").textContent = `${adv.daily_water_need_mm} mm/day per acre`;

            if (getElement("soilMoistureStatus")) getElement("soilMoistureStatus").textContent = adv.moisture_status;
            if (getElement("soilRetentionInfo")) getElement("soilRetentionInfo").textContent = `Retention interval: ${adv.soil_retention_interval_days} days (${farmerSoilData.soil_type || 'Red'} Soil)`;

            if (getElement("nextIrrigationDays")) getElement("nextIrrigationDays").textContent = adv.next_irrigation_in_days === 1 ? "Due Today" : `In ${adv.next_irrigation_in_days} Days`;
            if (getElement("irrigationActionText")) getElement("irrigationActionText").textContent = adv.action_advisory;
            if (getElement("irrigationTipText")) getElement("irrigationTipText").textContent = adv.irrigation_method_tip;
        }
    } catch (e) {
        console.error("Irrigation error:", e);
    }

    // 3. Fetch Pest & Weed Advisory
    try {
        const pestData = await fetchJSON(`${API_BASE}/api/phase2/pest-weed-advisory?crop=${encodeURIComponent(crop)}`);
        const pGrid = getElement("pestDiagnosticsGrid");
        if (pGrid && pestData.success && pestData.advisory) {
            pGrid.innerHTML = pestData.advisory.diagnostics.map(item => `
                <div class="diagnostic-card">
                    <div class="diag-header">
                        <div class="diag-title">${escapeHTML(item.name)}</div>
                        <span class="badge ${item.category === 'Pest' ? 'badge-warning' : (item.category === 'Disease' ? 'badge-soil' : 'badge-market')}">
                            ${escapeHTML(item.category)}
                        </span>
                    </div>
                    <div class="diag-symptoms">
                        <strong>Symptoms:</strong> ${escapeHTML(item.symptoms)}
                    </div>
                    <div class="solution-box organic">
                        <strong>🌿 Organic / Bio Solution:</strong><br>
                        ${escapeHTML(item.organic_remedy)}
                    </div>
                    <div class="solution-box chemical">
                        <strong>🧪 Targeted Chemical Control:</strong><br>
                        ${escapeHTML(item.chemical_control)}
                    </div>
                </div>
            `).join("");
        }
    } catch (e) {
        console.error("Pest error:", e);
    }
}

getElement("careCropSelector")?.addEventListener("change", (e) => {
    selectedCrop = e.target.value;
    loadPhase2Data();
});

getElement("updateCareBtn")?.addEventListener("click", () => {
    loadPhase2Data();
});

getElement("changeCropBtn")?.addEventListener("click", () => {
    switchPhase(1);
});

getElement("markHarvestedBtn")?.addEventListener("click", () => {
    switchPhase(3);
    showMarketTab("list");
});

getElement("harvestReadyBannerBtn")?.addEventListener("click", () => {
    switchPhase(3);
    showMarketTab("list");
});


/* ==========================================================================
   PHASE 3: DIRECT SELLING & BUYER MARKETPLACE
   ========================================================================= */
function showMarketTab(tab) {
    if (tab === "browse") {
        getElement("tabBrowseLotsBtn")?.classList.add("active");
        getElement("tabListProduceBtn")?.classList.remove("active");
        getElement("viewBrowseLots")?.classList.add("active");
        getElement("viewListProduce")?.classList.remove("active");
        loadMarketplaceListings();
    } else {
        getElement("tabListProduceBtn")?.classList.add("active");
        getElement("tabBrowseLotsBtn")?.classList.remove("active");
        getElement("viewListProduce")?.classList.add("active");
        getElement("viewBrowseLots")?.classList.remove("active");

        // Pre-fill harvest form with current crop and default date
        if (getElement("postCrop")) getElement("postCrop").value = selectedCrop;
        if (getElement("postHarvestDate")) getElement("postHarvestDate").value = new Date().toISOString().slice(0, 10);
    }
}

getElement("tabBrowseLotsBtn")?.addEventListener("click", () => showMarketTab("browse"));
getElement("tabListProduceBtn")?.addEventListener("click", () => showMarketTab("list"));
getElement("openPostHarvestModalBtn")?.addEventListener("click", () => showMarketTab("list"));

async function loadMarketplaceListings() {
    const cropFilter = getElement("marketSearchCrop")?.value.trim() || "";
    const distFilter = getElement("marketSearchDistrict")?.value.trim() || "";
    const q = new URLSearchParams();
    if (cropFilter) q.set("crop", cropFilter);
    if (distFilter) q.set("district", distFilter);

    try {
        const data = await fetchJSON(`${API_BASE}/api/phase3/listings?${q.toString()}`);
        const grid = getElement("marketplaceLotsGrid");
        if (!grid) return;

        if (!data.listings || data.listings.length === 0) {
            grid.innerHTML = `<p class="status">No active harvest listings found matching the criteria.</p>`;
            return;
        }

        grid.innerHTML = data.listings.map(lot => {
            const price = Number(lot.asking_price_per_quintal) || 0;
            const safeLot = JSON.stringify(lot).replace(/"/g, '&quot;');

            return `
                <div class="lot-card">
                    <div class="lot-image-wrap">
                        <img src="${escapeHTML(lot.photo_url)}" alt="${escapeHTML(lot.crop)}" loading="lazy" onerror="this.src='https://images.unsplash.com/photo-1586201375761-83865001e31c?auto=format&fit=crop&w=600&q=80'">
                        <span class="lot-grade-badge">${escapeHTML(lot.quality_grade)}</span>
                    </div>

                    <div class="lot-content">
                        <div>
                            <div class="lot-top">
                                <div>
                                    <h3 class="lot-crop-name">${escapeHTML(lot.crop)}</h3>
                                    <div class="lot-variety">${escapeHTML(lot.variety || "Standard Hybrid")}</div>
                                </div>
                                <div class="lot-price-box">
                                    <div class="lot-price-amount">${formatRupees(price)}</div>
                                    <span class="lot-price-unit">per quintal</span>
                                </div>
                            </div>

                            <ul class="lot-specs-list">
                                <li><span>Available Lot Size:</span><strong>${lot.quantity_quintals} Quintals</strong></li>
                                <li><span>Harvest Date:</span><strong>${escapeHTML(lot.harvest_date)}</strong></li>
                                <li><span>Condition:</span><span style="font-size: 0.78rem;">${escapeHTML(lot.notes || "Sun dried & ready for dispatch")}</span></li>
                            </ul>

                            <div class="lot-farmer-box">
                                <div class="lot-farmer-name">👨‍🌾 ${escapeHTML(lot.farmer_name)}</div>
                                <div class="lot-farmer-loc">📍 ${escapeHTML(lot.village)}, ${escapeHTML(lot.district)}, ${escapeHTML(lot.state)}</div>
                            </div>
                        </div>

                        <div class="lot-actions">
                            <button type="button" class="btn btn-primary btn-sm" onclick='openInquiryModal(${safeLot})'>
                                📩 Contact Farmer
                            </button>
                            <a href="https://wa.me/91${lot.phone_number}?text=Hello%20${encodeURIComponent(lot.farmer_name)},%20I%20am%20interested%20in%20your%20listing%20of%20${lot.quantity_quintals}%20quintals%20of%20${encodeURIComponent(lot.crop)}%20at%20Rs.${price}/qtl%20on%20Farm-to-Market%20AI." target="_blank" rel="noopener noreferrer" class="btn btn-accent btn-sm">
                                💬 WhatsApp
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }).join("");
    } catch (err) {
        console.error("Marketplace fetch error:", err);
    }
}

getElement("applyMarketFilterBtn")?.addEventListener("click", loadMarketplaceListings);
getElement("clearMarketFilterBtn")?.addEventListener("click", () => {
    if (getElement("marketSearchCrop")) getElement("marketSearchCrop").value = "";
    if (getElement("marketSearchDistrict")) getElement("marketSearchDistrict").value = "";
    loadMarketplaceListings();
});

/* POST HARVEST FORM SUBMIT (FARMER PORTAL) */
getElement("postHarvestForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    setButtonLoading("publishLotBtn", true, "Publishing...", "📢 Publish Harvest Lot to Marketplace");
    setStatus("postStatus", "Registering lot in marketplace...", "loading");

    const payload = {
        crop: getElement("postCrop")?.value,
        variety: getElement("postVariety")?.value,
        quantity_quintals: Number(getElement("postQuantity")?.value),
        quality_grade: getElement("postGrade")?.value,
        asking_price_per_quintal: Number(getElement("postAskingPrice")?.value),
        harvest_date: getElement("postHarvestDate")?.value,
        photo_url: getElement("postPhotoUrl")?.value,
        notes: getElement("postNotes")?.value,
        farmer_name: getElement("postFarmerName")?.value,
        phone_number: getElement("postPhone")?.value,
        village: getElement("postVillage")?.value,
        district: getElement("postDistrict")?.value,
        state: "Andhra Pradesh"
    };

    try {
        const data = await fetchJSON(`${API_BASE}/api/phase3/create-listing`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!data.success) throw new Error(data.error || "Failed to post listing.");

        setStatus("postStatus", `Published successfully as Lot #${data.listing.id}! Redirecting to Marketplace...`, "success");
        setTimeout(() => {
            showMarketTab("browse");
            setStatus("postStatus", "");
        }, 1200);

    } catch (err) {
        setStatus("postStatus", err.message, "error");
    } finally {
        setButtonLoading("publishLotBtn", false, "Publishing...", "📢 Publish Harvest Lot to Marketplace");
    }
});

/* INQUIRY MODAL (BUYER CONNECT) */
window.openInquiryModal = function(lot) {
    currentLotForInquiry = lot;
    if (getElement("modalLotTitle")) getElement("modalLotTitle").textContent = `Contact Farmer for ${lot.crop} (${lot.quantity_quintals} qtl)`;
    if (getElement("inquiryLotId")) getElement("inquiryLotId").value = lot.id;
    if (getElement("inquiryOfferPrice")) getElement("inquiryOfferPrice").value = lot.asking_price_per_quintal;
    if (getElement("inquiryQuantity")) getElement("inquiryQuantity").value = lot.quantity_quintals;

    if (getElement("modalFarmerDetails")) {
        getElement("modalFarmerDetails").innerHTML = `
            ${escapeHTML(lot.farmer_name)} &bull; 📞 ${escapeHTML(lot.phone_number)} &bull; 📍 ${escapeHTML(lot.village)}, ${escapeHTML(lot.district)}
        `;
    }

    const waBtn = getElement("modalWhatsAppBtn");
    if (waBtn) {
        waBtn.href = `https://wa.me/91${lot.phone_number}?text=Hello%20${encodeURIComponent(lot.farmer_name)},%20I%20am%20interested%20in%20purchasing%20your%20harvested%20${encodeURIComponent(lot.crop)}%20lot%20(${lot.id})%20on%20Farm-to-Market%20AI.`;
    }

    const modal = getElement("buyerInquiryModal");
    if (modal) modal.style.display = "flex";
};

getElement("closeInquiryModalBtn")?.addEventListener("click", () => {
    const modal = getElement("buyerInquiryModal");
    if (modal) modal.style.display = "none";
});

getElement("buyerInquiryForm")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    setButtonLoading("sendInquiryBtn", true, "Sending...", "Send Direct Inquiry");

    const payload = {
        listing_id: getElement("inquiryLotId")?.value,
        buyer_name: getElement("inquiryBuyerName")?.value,
        buyer_phone: getElement("inquiryBuyerPhone")?.value,
        offer_price: Number(getElement("inquiryOfferPrice")?.value),
        quantity_needed: Number(getElement("inquiryQuantity")?.value),
        message: getElement("inquiryMessage")?.value
    };

    try {
        const data = await fetchJSON(`${API_BASE}/api/phase3/buyer-inquiry`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!data.success) throw new Error(data.error || "Failed to send inquiry.");

        setStatus("inquiryStatus", "Inquiry sent to farmer! You can also click 'Chat on WhatsApp'.", "success");
        setTimeout(() => {
            const modal = getElement("buyerInquiryModal");
            if (modal) modal.style.display = "none";
            setStatus("inquiryStatus", "");
        }, 1500);

    } catch (err) {
        setStatus("inquiryStatus", err.message, "error");
    } finally {
        setButtonLoading("sendInquiryBtn", false, "Sending...", "Send Direct Inquiry");
    }
});

// Default Startup
window.addEventListener("DOMContentLoaded", () => {
    loadWeather("Vijayawada");
    loadMarketplaceListings();
});
