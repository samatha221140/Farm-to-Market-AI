"use strict";

// Target Flask backend server on port 5000
let API_BASE = "http://127.0.0.1:5000";
if (typeof window !== "undefined" && window.location && window.location.protocol.startsWith("http")) {
    if (window.location.port === "5000") {
        API_BASE = "";
    } else {
        API_BASE = `http://${window.location.hostname || "127.0.0.1"}:5000`;
    }
}

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
   GLOBAL PHASE NAVIGATION (Phase 1 -> Phase 2 -> Phase 3)
   ========================================================================== */
function switchPhase(phaseNum) {
    currentPhase = Number(phaseNum);

    // Update Nav Buttons
    const navBtns = [
        getElement("navPhase1Btn"),
        getElement("navPhase2Btn"),
        getElement("navPhase3Btn")
    ];
    navBtns.forEach((btn, idx) => {
        if (btn) btn.classList.toggle("active", idx + 1 === currentPhase);
    });

    // Update Phase Containers
    const containers = [
        getElement("phase1Container"),
        getElement("phase2Container"),
        getElement("phase3Container")
    ];
    containers.forEach((c, idx) => {
        if (c) c.classList.toggle("active", idx + 1 === currentPhase);
    });

    // Update Active Crop Bar
    const activeBar = getElement("activeCropBar");
    if (activeBar) {
        activeBar.style.display = (currentPhase >= 2 && currentPhase <= 3 && selectedCrop) ? "block" : "none";
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

    // 2. Fetch Smart Irrigation & IoT Sensor Advisory
    await calculateSmartIrrigationUI();
    await fetchLiveSensors();

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
                    <div style="font-size: 0.78rem; background: #eff6ff; color: #1e40af; border: 1px solid #bfdbfe; padding: 3px 8px; border-radius: 4px; margin: 6px 0 8px 0; font-weight: 700;">
                        🤖 Pretrained MobileNetV2: ${escapeHTML(item.deep_learning_class || item.name)}
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
   SMART IRRIGATION & IOT SENSOR CONTROLLER ENGINE
   ========================================================================== */
let currentPumpRelayState = "OFF";
let currentSensorReadings = {};

async function fetchLiveSensors() {
    try {
        const res = await fetchJSON(`${API_BASE}/api/sensors/latest`);
        if (res.success && res.sensors) {
            currentSensorReadings = res.sensors;
            const s = res.sensors;
            if (getElement("sensorLiveMoisture")) getElement("sensorLiveMoisture").textContent = `${s.soil_moisture_pct}%`;
            if (getElement("sensorLiveN")) getElement("sensorLiveN").textContent = `${s.N} kg/ha`;
            if (getElement("sensorLiveP")) getElement("sensorLiveP").textContent = `${s.P} kg/ha`;
            if (getElement("sensorLiveK")) getElement("sensorLiveK").textContent = `${s.K} kg/ha`;
            if (getElement("sensorLivePH")) getElement("sensorLivePH").textContent = `${s.pH}`;
            if (getElement("sensorLiveRain")) getElement("sensorLiveRain").textContent = `${s.rainfall_today_mm} mm`;
            
            currentPumpRelayState = s.pump_relay_state || "OFF";
            updatePumpRelayButtonUI();
        }
    } catch (e) {
        console.warn("Sensor fetch notice:", e);
    }
}

function updatePumpRelayButtonUI() {
    const btn = getElement("togglePumpRelayBtn");
    if (!btn) return;
    if (currentPumpRelayState === "ON") {
        btn.textContent = "🛑 Switch Pump Relay OFF";
        btn.classList.add("active-on");
    } else {
        btn.textContent = "⚡ Switch Pump Relay ON";
        btn.classList.remove("active-on");
    }
}

async function togglePumpRelay() {
    const nextState = currentPumpRelayState === "ON" ? "OFF" : "ON";
    try {
        const res = await fetchJSON(`${API_BASE}/api/irrigation/pump-control`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ state: nextState })
        });
        if (res.success) {
            currentPumpRelayState = res.pump_relay_state;
            updatePumpRelayButtonUI();
            alert(`Pump Relay switched to: ${currentPumpRelayState}`);
        }
    } catch (e) {
        alert("Failed to toggle pump relay: " + e.message);
    }
}

async function calculateSmartIrrigationUI() {
    const crop = selectedCrop || getElement("careCropSelector")?.value || "Groundnut";
    const stage = getElement("careGrowthStage")?.value || "Flowering & Pegging / Tasseling (35-65 DAS)";
    const soilType = farmerSoilData.soil_type || getElement("soil_type")?.value || "Red";
    const soilMoisture = Number(getElement("irrSoilMoisture")?.value || 21.5);
    const rainToday = Number(getElement("irrRainToday")?.value || 0.0);
    const rainForecast = Number(getElement("irrRainForecast")?.value || 0.0);
    const pumpRating = getElement("irrPumpRating")?.value || "1.0 HP";
    const irrMethod = getElement("irrMethod")?.value || "Drip Irrigation";
    const acres = Number(getElement("irrLandAcres")?.value || selectedAcreage || 2.0);

    setButtonLoading("calcSmartIrrigationBtn", true, "Calculating Water Balance...", "💧 Calculate Water Requirement & Pump Run-Time");

    try {
        const res = await fetchJSON(`${API_BASE}/api/phase2/irrigation-advisory`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                crop: crop,
                soil_type: soilType,
                growth_stage: stage,
                soil_moisture_pct: soilMoisture,
                rainfall_today_mm: rainToday,
                forecast_rain_mm: rainForecast,
                temperature: farmerSoilData.temperature || 31.0,
                humidity: farmerSoilData.humidity || 58.0,
                pump_rating: pumpRating,
                irrigation_method: irrMethod,
                acres: acres
            })
        });

        if (res.success && res.advisory) {
            renderSmartIrrigation(res.advisory);
        }
    } catch (e) {
        console.error("Irrigation calculation error:", e);
    } finally {
        setButtonLoading("calcSmartIrrigationBtn", false, "Calculating...", "💧 Calculate Water Requirement & Pump Run-Time");
    }
}

function renderSmartIrrigation(adv) {
    const pump = adv.pump_operation || {};
    const water = adv.water_calculation || {};
    const soil = adv.soil_water_status || {};

    // 1. Pump Decision Banner
    const banner = getElement("pumpDecisionBanner");
    const statusBadge = getElement("pumpStatusBadge");
    const actionHeadline = getElement("pumpActionHeadline");
    const reasonText = getElement("pumpReasonText");
    const runtimeVal = getElement("pumpRuntimeDisplay");
    const timingTip = getElement("pumpTimingTip");

    if (banner && statusBadge) {
        if (pump.pump_state === "RECOMMENDED_ON" && pump.runtime_minutes > 0) {
            banner.className = "pump-decision-card pump-running";
            statusBadge.textContent = "⚡ PUMP ON — RUNNING REQUIRED";
            statusBadge.style.color = "#15803d";
            if (actionHeadline) actionHeadline.textContent = pump.action_headline;
            if (reasonText) reasonText.textContent = `Root zone moisture is ${soil.sensor_moisture_pct}% (${soil.moisture_health}). ${water.total_water_liters.toLocaleString('en-IN')} L required for ${adv.land_acres} Acres.`;
            if (runtimeVal) runtimeVal.textContent = pump.runtime_hours_str;
            if (timingTip) timingTip.textContent = pump.recommended_timing;
        } else {
            banner.className = "pump-decision-card pump-stopped";
            statusBadge.textContent = "⏹️ KEEP PUMP OFF — NO WATER NEEDED";
            statusBadge.style.color = "#475569";
            if (actionHeadline) actionHeadline.textContent = pump.action_headline;
            if (reasonText) reasonText.textContent = `Soil moisture is at ${soil.sensor_moisture_pct}%. Rain/moisture balance is adequate today.`;
            if (runtimeVal) runtimeVal.textContent = "0 Mins";
            if (timingTip) timingTip.textContent = "Irrigation paused";
        }
    }

    // 2. Metrics Cards
    if (getElement("dailyWaterLiters")) {
        getElement("dailyWaterLiters").textContent = `${water.total_water_liters.toLocaleString('en-IN')} L`;
    }
    if (getElement("dailyWaterMm")) {
        getElement("dailyWaterMm").textContent = `${water.net_water_depth_mm} mm net depth (${adv.irrigation_method})`;
    }
    if (getElement("soilMoistureStatus")) {
        getElement("soilMoistureStatus").textContent = `${soil.moisture_health} (${soil.sensor_moisture_pct}%)`;
    }
    if (getElement("soilRetentionInfo")) {
        getElement("soilRetentionInfo").textContent = `Field Capacity: ${soil.field_capacity_pct}% | Wilting Point: ${soil.permanent_wilting_point_pct}%`;
    }
    if (getElement("pumpEnergyKwh")) {
        getElement("pumpEnergyKwh").textContent = `${pump.estimated_kwh || 0} kWh`;
    }

    // 3. Tip text
    if (getElement("irrigationTipText")) {
        getElement("irrigationTipText").textContent = `Crop coefficient Kc=${adv.weather_factors.crop_coefficient_kc}. ${adv.irrigation_method} operates at ${adv.irrigation_efficiency_pct}% efficiency. ${pump.action_headline}.`;
    }
}

// 1-Click Sync Sensor Readings to Forms
function syncSensorsToForms() {
    if (!currentSensorReadings || Object.keys(currentSensorReadings).length === 0) {
        alert("Please click 'Read Live Sensors' first to connect to the node.");
        return;
    }
    const s = currentSensorReadings;
    if (getElement("irrSoilMoisture")) getElement("irrSoilMoisture").value = s.soil_moisture_pct;
    if (getElement("irrRainToday")) getElement("irrRainToday").value = s.rainfall_today_mm;
    
    // Also sync to Soil Health Card form in Module 2
    if (getElement("soilN")) getElement("soilN").value = s.N;
    if (getElement("soilP")) getElement("soilP").value = s.P;
    if (getElement("soilK")) getElement("soilK").value = s.K;
    if (getElement("soilPH")) getElement("soilPH").value = s.pH;

    // Trigger recalculation
    calculateSmartIrrigationUI();
    alert(`Synced live IoT sensors to Smart Irrigation & Soil Health forms:\n• Soil Moisture: ${s.soil_moisture_pct}%\n• N-P-K: ${s.N}-${s.P}-${s.K} kg/ha\n• pH: ${s.pH}`);
}

getElement("calcSmartIrrigationBtn")?.addEventListener("click", calculateSmartIrrigationUI);
getElement("togglePumpRelayBtn")?.addEventListener("click", togglePumpRelay);
getElement("syncSensorBtn")?.addEventListener("click", async () => {
    await fetchLiveSensors();
    alert("Live sensor telemetry refreshed from IoT Node.");
});
getElement("fillFromSensorBtn")?.addEventListener("click", syncSensorsToForms);


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


/* ==========================================================================
   PHASE 2: AI CROP PHOTO SCANNER (DISEASE, PEST & WEED DETECTION)
   ========================================================================== */
let currentUploadedImageBase64 = null;

const cropPhotoInput = getElement("cropPhotoInput");
const cropDropzone = getElement("cropDropzone");
const cropImagePreview = getElement("cropImagePreview");
const imagePreviewContainer = getElement("imagePreviewContainer");
const removeImageBtn = getElement("removeImageBtn");

// Click on dropzone opens file dialog
cropDropzone?.addEventListener("click", (e) => {
    if (e.target.id !== "removeImageBtn" && !e.target.closest("#removeImageBtn")) {
        cropPhotoInput?.click();
    }
});

// Drag and drop handlers
cropDropzone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    cropDropzone.classList.add("dragover");
});

cropDropzone?.addEventListener("dragleave", () => {
    cropDropzone.classList.remove("dragover");
});

cropDropzone?.addEventListener("drop", (e) => {
    e.preventDefault();
    cropDropzone.classList.remove("dragover");
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleImageFile(e.dataTransfer.files[0]);
    }
});

cropPhotoInput?.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
        handleImageFile(e.target.files[0]);
    }
});

function handleImageFile(file) {
    if (!file.type.startsWith("image/")) {
        setStatus("visionStatus", "Please select a valid image file (JPG, PNG, WEBP).", "error");
        return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
        currentUploadedImageBase64 = event.target.result;
        if (cropImagePreview) cropImagePreview.src = currentUploadedImageBase64;
        if (imagePreviewContainer) imagePreviewContainer.style.display = "block";
        const dropContent = cropDropzone?.querySelector(".dropzone-content");
        if (dropContent) dropContent.style.display = "none";
        setStatus("visionStatus", `Photo loaded (${(file.size / 1024).toFixed(1)} KB). Click "Scan & Diagnose Crop Photo".`, "success");
    };
    reader.readAsDataURL(file);
}

removeImageBtn?.addEventListener("click", (e) => {
    e.stopPropagation();
    currentUploadedImageBase64 = null;
    if (cropPhotoInput) cropPhotoInput.value = "";
    if (imagePreviewContainer) imagePreviewContainer.style.display = "none";
    const dropContent = cropDropzone?.querySelector(".dropzone-content");
    if (dropContent) dropContent.style.display = "block";
    const resContainer = getElement("visionResultContainer");
    if (resContainer) resContainer.style.display = "none";
    setStatus("visionStatus", "Photo removed.");
});

// Helper to create synthetic demo canvas images for 1-click test buttons
function generateDemoImage(type) {
    const canvas = document.createElement("canvas");
    canvas.width = 256;
    canvas.height = 256;
    const ctx = canvas.getContext("2d");

    if (type === "chilli_rot") {
        // Red chilli with brown rot spots
        ctx.fillStyle = "#1e6b2c"; // green background
        ctx.fillRect(0, 0, 256, 256);
        ctx.fillStyle = "#b91c1c"; // red fruit
        ctx.beginPath();
        ctx.ellipse(128, 128, 60, 100, Math.PI / 6, 0, 2 * Math.PI);
        ctx.fill();
        // Necrotic brown sunken lesions
        ctx.fillStyle = "#451a03";
        ctx.beginPath();
        ctx.arc(110, 100, 22, 0, 2 * Math.PI);
        ctx.arc(140, 140, 28, 0, 2 * Math.PI);
        ctx.arc(120, 180, 18, 0, 2 * Math.PI);
        ctx.fill();
    } else if (type === "groundnut_tikka") {
        // Groundnut green leaf with dark circular spots & yellow halo
        ctx.fillStyle = "#22c55e"; // bright leaf green
        ctx.fillRect(0, 0, 256, 256);
        // Yellow halos
        ctx.fillStyle = "#eab308";
        ctx.beginPath();
        ctx.arc(70, 80, 32, 0, 2 * Math.PI);
        ctx.arc(170, 130, 38, 0, 2 * Math.PI);
        ctx.arc(100, 190, 30, 0, 2 * Math.PI);
        ctx.fill();
        // Dark brown necrotic centers
        ctx.fillStyle = "#291505";
        ctx.beginPath();
        ctx.arc(70, 80, 20, 0, 2 * Math.PI);
        ctx.arc(170, 130, 24, 0, 2 * Math.PI);
        ctx.arc(100, 190, 18, 0, 2 * Math.PI);
        ctx.fill();
    } else if (type === "pest_curl") {
        // Curled yellow chlorotic leaf with sucking pest sheen
        ctx.fillStyle = "#ca8a04"; // yellow chlorosis
        ctx.fillRect(0, 0, 256, 256);
        ctx.fillStyle = "#65a30d";
        ctx.beginPath();
        ctx.ellipse(128, 128, 90, 50, Math.PI / 4, 0, 2 * Math.PI);
        ctx.fill();
        // Pest speckles
        ctx.fillStyle = "#1e293b";
        for (let i = 0; i < 60; i++) {
            ctx.fillRect(50 + Math.random() * 150, 50 + Math.random() * 150, 3, 3);
        }
    } else if (type === "rice_blast") {
        ctx.fillStyle = "#15803d"; // paddy leaf blade
        ctx.fillRect(0, 0, 256, 256);
        // Spindle shaped diamond lesions
        ctx.fillStyle = "#78350f";
        ctx.beginPath();
        ctx.ellipse(128, 128, 40, 15, Math.PI / 4, 0, 2 * Math.PI);
        ctx.ellipse(80, 70, 30, 12, Math.PI / 4, 0, 2 * Math.PI);
        ctx.fill();
        ctx.fillStyle = "#e2e8f0"; // gray center
        ctx.beginPath();
        ctx.ellipse(128, 128, 24, 8, Math.PI / 4, 0, 2 * Math.PI);
        ctx.ellipse(80, 70, 18, 6, Math.PI / 4, 0, 2 * Math.PI);
        ctx.fill();
    } else if (type === "weed_overgrowth") {
        ctx.fillStyle = "#166534";
        ctx.fillRect(0, 0, 256, 256);
        // Random wild weed blades and flowering heads
        ctx.fillStyle = "#84cc16";
        for (let i = 0; i < 20; i++) {
            ctx.beginPath();
            ctx.moveTo(10 + i * 12, 250);
            ctx.lineTo(20 + i * 12, 30 + Math.random() * 40);
            ctx.lineTo(30 + i * 12, 250);
            ctx.fill();
        }
    } else {
        // Healthy lush green leaf
        ctx.fillStyle = "#15803d";
        ctx.fillRect(0, 0, 256, 256);
        ctx.fillStyle = "#22c55e";
        ctx.beginPath();
        ctx.ellipse(128, 128, 85, 55, Math.PI / 6, 0, 2 * Math.PI);
        ctx.fill();
    }

    return canvas.toDataURL("image/jpeg", 0.9);
}

// Wire up Demo Sample Photo Buttons
function loadSamplePhoto(type, crop, notes) {
    const dataUrl = generateDemoImage(type);
    currentUploadedImageBase64 = dataUrl;
    if (cropImagePreview) cropImagePreview.src = dataUrl;
    if (imagePreviewContainer) imagePreviewContainer.style.display = "block";
    const dropContent = cropDropzone?.querySelector(".dropzone-content");
    if (dropContent) dropContent.style.display = "none";
    if (getElement("visionCropSelect")) getElement("visionCropSelect").value = crop;
    if (getElement("visionFarmerNotes")) getElement("visionFarmerNotes").value = notes;
    setStatus("visionStatus", `Loaded sample photo for ${crop} (${notes}). Click "Scan & Diagnose Crop Photo" below.`, "success");
}

getElement("sampleChilliAnthracnose")?.addEventListener("click", () => loadSamplePhoto("chilli_rot", "Chilli", "dark necrotic lesions & dieback"));
getElement("sampleRiceBlast")?.addEventListener("click", () => loadSamplePhoto("rice_blast", "Rice", "spindle shaped diamond lesions on leaf blades"));
getElement("sampleGroundnutTikka")?.addEventListener("click", () => loadSamplePhoto("groundnut_tikka", "Groundnut", "brown spots with yellow halo"));
getElement("sampleCottonBlight")?.addEventListener("click", () => loadSamplePhoto("chilli_rot", "Cotton", "angular water-soaked black spots"));
getElement("sampleMaizeRust")?.addEventListener("click", () => loadSamplePhoto("rice_blast", "Maize", "elongated reddish-brown powdery rust pustules"));
getElement("samplePestSpiderMites")?.addEventListener("click", () => loadSamplePhoto("pest_curl", "Pest", "yellow stippling, webbing & tiny crawling mites"));
getElement("samplePestAphids")?.addEventListener("click", () => loadSamplePhoto("pest_curl", "Pest", "clusters of sucking aphids under leaves"));
getElement("sampleWeedNutgrass")?.addEventListener("click", () => loadSamplePhoto("weed_overgrowth", "Weed", "invasive nutgrass sedge tubers and shoots"));
getElement("sampleHealthyCrop")?.addEventListener("click", () => loadSamplePhoto("healthy", "Groundnut", "vigorous green foliage"));

// Scan & Diagnose Button Handler
getElement("scanCropPhotoBtn")?.addEventListener("click", async () => {
    if (!currentUploadedImageBase64) {
        setStatus("visionStatus", "Please upload a photo of your crop or click one of the sample test photos above.", "error");
        return;
    }

    const crop = getElement("visionCropSelect")?.value || "Chilli";
    const notes = getElement("visionFarmerNotes")?.value || "";

    setButtonLoading("scanCropPhotoBtn", true, "Scanning Image Pixels & Lesions...", "🔍 Scan & Diagnose Crop Photo");
    setStatus("visionStatus", "Running computer vision feature extraction & disease matching...", "loading");

    try {
        const data = await fetchJSON(`${API_BASE}/api/phase2/diagnose-image`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                image_base64: currentUploadedImageBase64,
                crop: crop,
                notes: notes
            })
        });

        if (!data.success) {
            throw new Error(data.error || "Image diagnosis failed.");
        }

        renderVisionDiagnosis(data);
        setStatus("visionStatus", "Diagnosis completed! Review organic and chemical remedies below.", "success");

    } catch (err) {
        setStatus("visionStatus", `Error: ${err.message}`, "error");
    } finally {
        setButtonLoading("scanCropPhotoBtn", false, "Scanning Image Pixels & Lesions...", "🔍 Scan & Diagnose Crop Photo");
    }
});

function renderVisionDiagnosis(data) {
    const card = getElement("visionResultContainer");
    if (!card) return;

    if (getElement("diagTitle")) getElement("diagTitle").textContent = data.diagnosis_name;
    if (getElement("diagPathogen")) getElement("diagPathogen").textContent = `Pathogen / Species: ${data.pathogen_species}`;
    if (getElement("diagConfidence")) getElement("diagConfidence").textContent = `${data.confidence_pct}%`;
    if (getElement("diagSummary")) getElement("diagSummary").textContent = data.summary;

    if (getElement("diagModelBadge") && data.model_engine) {
        getElement("diagModelBadge").textContent = `🤖 ${data.model_engine}`;
    }

    const candidatesWrap = getElement("diagTopCandidatesWrap");
    if (candidatesWrap) {
        if (data.top_candidates && data.top_candidates.length > 0) {
            candidatesWrap.innerHTML = `<strong>🧠 Top Neural Network Probabilities:</strong> ` +
                data.top_candidates.map(c => {
                    const cName = c.condition || c.class_name || "Disorder";
                    const prob = c.probability_pct ?? c.confidence_pct ?? 0;
                    return `<span style="display: inline-block; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 4px; margin: 2px 4px; font-weight: 600;">${escapeHTML(cName)} (${prob}%)</span>`;
                }).join("");
        } else {
            candidatesWrap.innerHTML = "";
        }
    }

    const catBadge = getElement("diagCategoryBadge");
    if (catBadge) {
        catBadge.textContent = data.category;
        catBadge.className = "badge " + (data.category === "Disease" ? "badge-warning" : (data.category === "Pest" ? "badge-market" : (data.category === "Weed" ? "badge-soil" : "badge-success")));
    }

    const sevBadge = getElement("diagSeverityBadge");
    if (sevBadge) {
        sevBadge.textContent = `Severity: ${data.severity}`;
        sevBadge.className = "badge " + (data.severity === "Severe" ? "badge-warning" : "badge-soil");
    }

    const vm = data.visual_metrics || {};
    if (getElement("metricGreen")) getElement("metricGreen").textContent = `${vm.healthy_green_pct ?? 0}%`;
    if (getElement("metricNecrotic")) getElement("metricNecrotic").textContent = `${vm.necrotic_lesion_pct ?? 0}%`;
    if (getElement("metricYellow")) getElement("metricYellow").textContent = `${vm.chlorotic_yellowing_pct ?? 0}%`;

    if (getElement("solOrganicText")) getElement("solOrganicText").textContent = data.organic_solution;
    if (getElement("solChemicalText")) getElement("solChemicalText").textContent = data.chemical_solution;
    if (getElement("solCulturalText")) getElement("solCulturalText").textContent = data.preventive_advisory;

    card.style.display = "block";
    card.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Solution Tabs (Organic vs Chemical)
getElement("tabOrganicSolBtn")?.addEventListener("click", () => {
    getElement("tabOrganicSolBtn")?.classList.add("active");
    getElement("tabChemicalSolBtn")?.classList.remove("active");
    getElement("viewOrganicSol")?.classList.add("active");
    getElement("viewChemicalSol")?.classList.remove("active");
});

getElement("tabChemicalSolBtn")?.addEventListener("click", () => {
    getElement("tabChemicalSolBtn")?.classList.add("active");
    getElement("tabOrganicSolBtn")?.classList.remove("active");
    getElement("viewChemicalSol")?.classList.add("active");
    getElement("viewOrganicSol")?.classList.remove("active");
});


/* ==========================================================================
   PHASE 2: SOIL HEALTH CARD TEST RESULTS & DUAL FERTILIZER RECOMMENDER
   ========================================================================== */
function applySoilPreset(type) {
    if (type === "red") {
        getElement("soilN").value = 24;
        getElement("soilP").value = 16;
        getElement("soilK").value = 32;
        getElement("soilPH").value = 5.8; // slightly acidic
        getElement("soilOC").value = 0.42; // low organic carbon
        getElement("soilEC").value = 0.4;
        getElement("soilZinc").value = 0.45; // deficient zinc
        getElement("soilCropTarget").value = "Groundnut";
        setStatus("soilAnalysisStatus", "Loaded AP Red Soil test card values (Deficient Nitrogen, Low Zinc, Acidic).", "success");
    } else if (type === "black") {
        getElement("soilN").value = 42;
        getElement("soilP").value = 28;
        getElement("soilK").value = 65; // high potassium
        getElement("soilPH").value = 8.3; // alkaline
        getElement("soilOC").value = 0.58;
        getElement("soilEC").value = 0.8;
        getElement("soilZinc").value = 0.50; // low zinc
        getElement("soilCropTarget").value = "Cotton";
        setStatus("soilAnalysisStatus", "Loaded Black Cotton Soil test card values (Alkaline, High K, Needs Zinc).", "success");
    } else if (type === "delta") {
        getElement("soilN").value = 55;
        getElement("soilP").value = 35;
        getElement("soilK").value = 45;
        getElement("soilPH").value = 7.1; // neutral
        getElement("soilOC").value = 0.72; // good organic carbon
        getElement("soilEC").value = 0.5;
        getElement("soilZinc").value = 0.75; // sufficient
        getElement("soilCropTarget").value = "Rice";
        setStatus("soilAnalysisStatus", "Loaded Delta Alluvial Soil test card values (Balanced N-P-K, Optimal pH).", "success");
    }
}

getElement("presetSoilRed")?.addEventListener("click", () => applySoilPreset("red"));
getElement("presetSoilBlack")?.addEventListener("click", () => applySoilPreset("black"));
getElement("presetSoilDelta")?.addEventListener("click", () => applySoilPreset("delta"));

const soilAnalysisForm = getElement("soilAnalysisForm");

soilAnalysisForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const acres = Number(getElement("soilAcres")?.value || 2.0);
    const crop = getElement("soilCropTarget")?.value || "Chilli";

    const payload = {
        crop: crop,
        acres: acres,
        N: Number(getElement("soilN")?.value),
        P: Number(getElement("soilP")?.value),
        K: Number(getElement("soilK")?.value),
        pH: Number(getElement("soilPH")?.value),
        organic_carbon: Number(getElement("soilOC")?.value),
        ec: Number(getElement("soilEC")?.value),
        zinc: Number(getElement("soilZinc")?.value)
    };

    setButtonLoading("analyzeSoilBtn", true, "Analyzing Soil & Calculating Dosages...", "🧪 Analyze Soil & Recommend Dual Fertilizers");
    setStatus("soilAnalysisStatus", "Evaluating nutritional status against ICAR crop targets...", "loading");

    try {
        const data = await fetchJSON(`${API_BASE}/api/phase2/analyze-soil-fertilizer`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!data.success) {
            throw new Error(data.error || "Soil analysis failed.");
        }

        renderSoilAndFertilizerResults(data, acres);
        setStatus("soilAnalysisStatus", "Soil health evaluated! Dual Organic and Chemical packages generated.", "success");

    } catch (err) {
        setStatus("soilAnalysisStatus", `Error: ${err.message}`, "error");
    } finally {
        setButtonLoading("analyzeSoilBtn", false, "Analyzing Soil & Calculating Dosages...", "🧪 Analyze Soil & Recommend Dual Fertilizers");
    }
});

function renderSoilAndFertilizerResults(data, acres) {
    const outcomeWrap = getElement("soilOutcomeContainer");
    if (!outcomeWrap) return;

    // Update acres labels
    document.querySelectorAll(".soil-acres-label").forEach(el => el.textContent = acres.toFixed(1));

    // 1. Render Soil Ratings Grid
    const ratingsGrid = getElement("soilRatingsGrid");
    if (ratingsGrid && data.soil_health_ratings) {
        ratingsGrid.innerHTML = Object.entries(data.soil_health_ratings).map(([elem, info]) => `
            <div class="rating-chip ${info.color}">
                <div class="rating-chip-label">${escapeHTML(elem.replace('_', ' '))}</div>
                <div class="rating-chip-value">${escapeHTML(info.rating)}</div>
                <small style="font-size: 0.74rem; color: var(--text-muted); display: block;">${escapeHTML(info.note)}</small>
            </div>
        `).join("");
    }

    // Soil Conditioner Alert (Lime / Gypsum)
    const alertBox = getElement("soilConditionerAlert");
    if (alertBox) {
        if (data.soil_conditioner_advisory) {
            alertBox.style.display = "block";
            alertBox.textContent = data.soil_conditioner_advisory;
        } else {
            alertBox.style.display = "none";
        }
    }

    // 2. Render Organic Components Table
    const orgBody = getElement("organicComponentsBody");
    if (orgBody && data.organic_package && data.organic_package.components) {
        orgBody.innerHTML = data.organic_package.components.map(c => `
            <tr>
                <td><strong>${escapeHTML(c.input)}</strong></td>
                <td>${escapeHTML(c.per_acre)}</td>
                <td><strong style="color: #15803d;">${escapeHTML(c.total_farm)}</strong></td>
                <td>${escapeHTML(c.timing)}</td>
            </tr>
        `).join("");
    }

    // 3. Render Chemical Components & Bag Summary
    const chemBagsGrid = getElement("chemicalBagsGrid");
    if (chemBagsGrid && data.chemical_package && data.chemical_package.bag_summary) {
        const bs = data.chemical_package.bag_summary;
        chemBagsGrid.innerHTML = `
            <div class="fert-bag-card">
                <div class="bag-icon">🧪</div>
                <div class="bag-name">DAP (18-46-0)</div>
                <div class="bag-count">${bs.dap_50kg_bags} Bags</div>
                <small>50 kg bags</small>
            </div>
            <div class="fert-bag-card">
                <div class="bag-icon">⚪</div>
                <div class="bag-name">Urea (46% N)</div>
                <div class="bag-count">${bs.urea_50kg_bags} Bags</div>
                <small>50 kg bags</small>
            </div>
            <div class="fert-bag-card">
                <div class="bag-icon">🔴</div>
                <div class="bag-name">MOP / Potash (60%)</div>
                <div class="bag-count">${bs.mop_50kg_bags} Bags</div>
                <small>50 kg bags</small>
            </div>
            <div class="fert-bag-card">
                <div class="bag-icon">⚡</div>
                <div class="bag-name">Zinc Sulfate (ZnSO₄)</div>
                <div class="bag-count">${bs.zinc_sulfate_kg} kg</div>
                <small>Micronutrient</small>
            </div>
            ${bs.gypsum_50kg_bags > 0 ? `
            <div class="fert-bag-card">
                <div class="bag-icon">🪨</div>
                <div class="bag-name">Gypsum (CaSO₄)</div>
                <div class="bag-count">${bs.gypsum_50kg_bags} Bags</div>
                <small>Soil amendment / Pod calcium</small>
            </div>` : ''}
        `;
    }

    const chemBody = getElement("chemicalComponentsBody");
    if (chemBody && data.chemical_package && data.chemical_package.components) {
        chemBody.innerHTML = data.chemical_package.components.map(c => `
            <tr>
                <td><strong>${escapeHTML(c.fertilizer)}</strong></td>
                <td><strong style="color: #0369a1;">${escapeHTML(c.quantity)}</strong></td>
                <td>${escapeHTML(c.dose_rate)}</td>
                <td>${escapeHTML(c.stage)}</td>
            </tr>
        `).join("");
    }

    // 4. Render INM summary
    if (getElement("inmText")) {
        getElement("inmText").textContent = data.integrated_nutrient_management || "";
    }

    outcomeWrap.style.display = "block";
    outcomeWrap.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// Soil Tabs (Organic vs Chemical vs INM)
getElement("tabOrganicFertBtn")?.addEventListener("click", () => {
    getElement("tabOrganicFertBtn")?.classList.add("active");
    getElement("tabChemicalFertBtn")?.classList.remove("active");
    getElement("tabInmFertBtn")?.classList.remove("active");
    getElement("viewOrganicFert")?.classList.add("active");
    getElement("viewChemicalFert")?.classList.remove("active");
    getElement("viewInmFert")?.classList.remove("active");
});

getElement("tabChemicalFertBtn")?.addEventListener("click", () => {
    getElement("tabChemicalFertBtn")?.classList.add("active");
    getElement("tabOrganicFertBtn")?.classList.remove("active");
    getElement("tabInmFertBtn")?.classList.remove("active");
    getElement("viewChemicalFert")?.classList.add("active");
    getElement("viewOrganicFert")?.classList.remove("active");
    getElement("viewInmFert")?.classList.remove("active");
});

getElement("tabInmFertBtn")?.addEventListener("click", () => {
    getElement("tabInmFertBtn")?.classList.add("active");
    getElement("tabOrganicFertBtn")?.classList.remove("active");
    getElement("tabChemicalFertBtn")?.classList.remove("active");
    getElement("viewInmFert")?.classList.add("active");
    getElement("viewOrganicFert")?.classList.remove("active");
    getElement("viewChemicalFert")?.classList.remove("active");
});

