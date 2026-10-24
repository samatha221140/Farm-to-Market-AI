"use strict";

const API_BASE = "http://127.0.0.1:5000";

// Global cache for live economic calculations
let cachedEconomicResult = null;
let currentAcreage = 2.0;

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
   1. Weather Module with Auto-Fill Feature
   ========================================================================== */
const weatherCodes = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    80: "Rain Showers",
    95: "Thunderstorm"
};

let latestFetchedWeather = null;

async function loadWeather(city) {
    if (!city.trim()) {
        setStatus("weatherStatus", "Please enter a valid city or district name.", "error");
        return;
    }

    setButtonLoading("refreshWeatherButton", true, "Fetching...", "Fetch Weather");
    setStatus("weatherStatus", "Looking up location coordinates and live forecast...", "loading");

    try {
        const geoURL = new URL("https://geocoding-api.open-meteo.com/v1/search");
        geoURL.searchParams.set("name", city.trim());
        geoURL.searchParams.set("count", "1");
        geoURL.searchParams.set("language", "en");
        geoURL.searchParams.set("format", "json");

        const geo = await fetchJSON(geoURL.toString());
        const place = geo.results && geo.results[0];

        if (!place) {
            throw new Error(`Location "${city}" could not be found. Try another major town or district in Andhra Pradesh/India.`);
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

        if (!current || !data.daily) {
            throw new Error("Weather metrics unavailable for this coordinate.");
        }

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

        // Enable Apply Weather Button
        const applyBtn = getElement("applyWeatherBtn");
        if (applyBtn) {
            applyBtn.disabled = false;
        }

        setStatus("weatherStatus", `Weather synced for ${place.name}. You can click "Apply Weather to Farm Inputs".`, "success");
    } catch (err) {
        setStatus("weatherStatus", err.message, "error");
    } finally {
        setButtonLoading("refreshWeatherButton", false, "Fetching...", "Fetch Weather");
    }
}

// Apply Weather Button handler
getElement("applyWeatherBtn")?.addEventListener("click", () => {
    if (!latestFetchedWeather) return;

    if (getElement("Temperature_C")) getElement("Temperature_C").value = latestFetchedWeather.temperature;
    if (getElement("humidity")) getElement("humidity").value = latestFetchedWeather.humidity;
    
    // Estimate seasonal rainfall based on local climate if rain is low
    const rainInput = getElement("Rainfall_mm");
    if (rainInput && Number(rainInput.value) <= 0) {
        rainInput.value = 650;
    }

    setStatus("cropStatus", `Applied live weather (${latestFetchedWeather.temperature}°C, ${latestFetchedWeather.humidity}% humidity) to farm form!`, "success");
});

getElement("refreshWeatherButton")?.addEventListener("click", () => {
    loadWeather(getElement("weatherCity")?.value || "");
});

/* ==========================================================================
   2. Quick Regional Test Presets
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
   3. Main Recommendation Pipeline (Top 5 Suitable + Top 3 Profitable)
   ========================================================================== */
const farmForm = getElement("farmForm");

farmForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const payload = {
        soil_type: getElement("soil_type")?.value,
        water_availability: getElement("water_availability")?.value,
        season: getElement("season")?.value,
        land_acres: Number(getElement("land_acres")?.value || 2.0),
        N_kg_ha: Number(getElement("N_kg_ha")?.value),
        P_kg_ha: Number(getElement("P_kg_ha")?.value),
        K_kg_ha: Number(getElement("K_kg_ha")?.value),
        pH: Number(getElement("pH")?.value),
        Temperature_C: Number(getElement("Temperature_C")?.value),
        humidity: Number(getElement("humidity")?.value),
        Rainfall_mm: Number(getElement("Rainfall_mm")?.value),
    };

    if (!payload.soil_type || !payload.water_availability) {
        setStatus("cropStatus", "Please select Soil Type and Water Availability.", "error");
        return;
    }

    currentAcreage = payload.land_acres;
    if (getElement("liveAcreSlider")) getElement("liveAcreSlider").value = currentAcreage;
    if (getElement("liveAcreValue")) getElement("liveAcreValue").textContent = currentAcreage.toFixed(1);

    setButtonLoading("recommendButton", true, "Evaluating Suitability & Profit...", "🌾 Recommend 5 Suitable Crops & Top 3 Profitable Crops");
    setStatus("cropStatus", "Processing agronomic parameters & calculating mandi market returns...", "loading");

    try {
        const data = await fetchJSON(`${API_BASE}/api/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!data.success) {
            throw new Error(data.message || "Failed to retrieve crop recommendations.");
        }

        cachedEconomicResult = data;

        // Render Results
        renderTop5SuitableCrops(data.top_5_suitable_crops || []);
        renderTop3ProfitableCrops(data.top_3_profitable_crops || [], currentAcreage);
        renderEconomicsTable(data.all_candidate_economics || [], currentAcreage);

        // Show Results Section and Scroll Smoothly
        const resultsSection = getElement("resultsSection");
        if (resultsSection) {
            resultsSection.style.display = "block";
            resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }

        setStatus("cropStatus", "Recommendations generated! 5 Agronomically Suitable crops and 3 Market Profit leaders identified.", "success");

    } catch (err) {
        setStatus("cropStatus", `${err.message}. Make sure Flask backend is running at http://127.0.0.1:5000.`, "error");
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

/* ==========================================================================
   4. Render Step 1: Top 5 Suitable Crops Cards
   ========================================================================== */
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
                        <span class="tag tag-soil">🌱 Suitable: ${escapeHTML((item.suitable_soils || []).join(", "))}</span>
                    </div>

                    <div class="breakdown-bars">
                        <div class="breakdown-row">
                            <span>Soil Compatibility:</span>
                            <strong>${bd.soil_score ?? 20} / 20</strong>
                        </div>
                        <div class="breakdown-row">
                            <span>Water Availability Match:</span>
                            <strong>${bd.water_score ?? 20} / 20</strong>
                        </div>
                        <div class="breakdown-row">
                            <span>N-P-K Nutrient Alignment:</span>
                            <strong>${bd.npk_score ?? 20} / 20</strong>
                        </div>
                        <div class="breakdown-row">
                            <span>Temperature & Weather:</span>
                            <strong>${bd.temperature_score ?? 10} / 10</strong>
                        </div>
                        <div class="breakdown-row">
                            <span>Soil pH Compatibility:</span>
                            <strong>${bd.ph_score ?? 10} / 10</strong>
                        </div>
                    </div>

                    <ul class="reasons-list">
                        ${(item.reasons || []).slice(0, 4).map(r => `<li>${escapeHTML(r)}</li>`).join("")}
                    </ul>
                </div>

                <div class="crop-advisory">
                    <small style="color: var(--text-subtle); display: block; margin-top: 6px;">
                        📌 ${escapeHTML(item.description || "Thrives in designated agro-climatic conditions.")}
                    </small>
                </div>
            </div>
        `;
    }).join("");
}

/* ==========================================================================
   5. Render Step 2: Top 3 Profitable Crops Cards
   ========================================================================== */
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
        const totalRevenue = grossRevenuePerAcre * acres;
        const costPerAcre = Number(item.cultivation_cost_per_acre) || 0;
        const totalCost = costPerAcre * acres;
        const yieldVal = Number(item.avg_yield_quintals_per_acre) || 0;
        const price = Number(item.price_rs_per_quintal) || 0;

        return `
            <div class="profit-card rank-${idx + 1}">
                <div class="rank-badge">${rankTitles[idx] || `#${idx + 1}`}</div>
                
                <div class="profit-card-header">
                    <h3 class="profit-crop-title">${escapeHTML(item.crop)}</h3>
                    <div class="profit-market-loc">🏛️ Market: ${escapeHTML(item.market || "Regional AP Mandi")}</div>
                </div>

                <div class="profit-highlight-box">
                    <div class="profit-highlight-label">Estimated Net Profit / Acre</div>
                    <div class="profit-highlight-value">${formatRupees(netProfitPerAcre)}</div>
                    <div class="total-farm-profit-callout">
                        Total for ${acres} Acres: <strong>${formatRupees(totalProfit)}</strong>
                    </div>
                </div>

                <ul class="finance-metrics-list">
                    <li>
                        <span class="metric-name">Market Price:</span>
                        <span class="metric-num">${formatRupees(price)} / quintal</span>
                    </li>
                    <li>
                        <span class="metric-name">Average Yield:</span>
                        <span class="metric-num">${yieldVal} q / acre (${(yieldVal * acres).toFixed(1)} q total)</span>
                    </li>
                    <li>
                        <span class="metric-name">Cultivation Cost:</span>
                        <span class="metric-num">${formatRupees(costPerAcre)} / acre (${formatRupees(totalCost)} total)</span>
                    </li>
                    <li>
                        <span class="metric-name">Gross Revenue:</span>
                        <span class="metric-num">${formatRupees(grossRevenuePerAcre)} / acre (${formatRupees(totalRevenue)} total)</span>
                    </li>
                    <li>
                        <span class="metric-name">Return on Investment:</span>
                        <span class="metric-num" style="color: var(--primary);">${item.roi_pct ?? 0}% ROI</span>
                    </li>
                </ul>

                <button type="button" class="btn btn-secondary btn-sm" onclick="prefillProfitCalculator('${escapeHTML(item.crop)}', ${price}, ${yieldVal}, ${costPerAcre})">
                    🧮 Use in Custom Profit Calculator
                </button>
            </div>
        `;
    }).join("");
}

/* ==========================================================================
   6. Render Candidate Economics Table
   ========================================================================== */
function renderEconomicsTable(candidates, acres = 1.0) {
    const tbody = getElement("candidateEconomicsBody");
    if (!tbody) return;

    const acresLabels = document.querySelectorAll(".table-acres-label");
    acresLabels.forEach(el => el.textContent = acres.toFixed(1));

    if (!candidates || candidates.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8">No candidate records available.</td></tr>`;
        return;
    }

    tbody.innerHTML = candidates.map((item, idx) => {
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
                <td><span class="badge badge-success">${item.roi_pct}% ROI</span></td>
            </tr>
        `;
    }).join("");
}

/* ==========================================================================
   7. Interactive Dynamic Land Acreage Slider
   ========================================================================== */
const liveAcreSlider = getElement("liveAcreSlider");
liveAcreSlider?.addEventListener("input", (event) => {
    const acres = Number(event.target.value);
    currentAcreage = acres;
    if (getElement("liveAcreValue")) getElement("liveAcreValue").textContent = acres.toFixed(1);

    if (cachedEconomicResult && cachedEconomicResult.top_3_profitable_crops) {
        renderTop3ProfitableCrops(cachedEconomicResult.top_3_profitable_crops, acres);
        renderEconomicsTable(cachedEconomicResult.all_candidate_economics, acres);
    }
});

/* ==========================================================================
   8. Tabs Switcher
   ========================================================================== */
const tabTop5Btn = getElement("tabTop5Btn");
const tabTop3Btn = getElement("tabTop3Btn");
const viewTop5 = getElement("viewTop5");
const viewTop3 = getElement("viewTop3");

tabTop5Btn?.addEventListener("click", () => {
    tabTop5Btn.classList.add("active");
    tabTop3Btn?.classList.remove("active");
    viewTop5?.classList.add("active");
    viewTop3?.classList.remove("active");
});

tabTop3Btn?.addEventListener("click", () => {
    tabTop3Btn.classList.add("active");
    tabTop5Btn?.classList.remove("active");
    viewTop3?.classList.add("active");
    viewTop5?.classList.remove("active");
});

/* ==========================================================================
   9. Government & Regional Mandi Prices Lookup
   ========================================================================== */
const mandiForm = getElement("mandiForm");

mandiForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const crop = getElement("mandiCrop")?.value.trim() || "";
    const state = getElement("mandiState")?.value.trim() || "Andhra Pradesh";
    const district = getElement("mandiDistrict")?.value.trim() || "";

    setButtonLoading("searchMandiButton", true, "Searching Mandis...", "Search Mandi Rates");
    setStatus("mandiStatus", "Querying agricultural mandi records...", "loading");

    try {
        const queryParams = new URLSearchParams({ crop, state });
        if (district) queryParams.set("district", district);

        const data = await fetchJSON(`${API_BASE}/api/mandi-prices?${queryParams.toString()}`);

        const resultsContainer = getElement("mandiResults");
        if (!resultsContainer) return;

        if (!data.records || data.records.length === 0) {
            resultsContainer.innerHTML = `<p class="status">No matching mandi records found for "${escapeHTML(crop || 'all crops')}".</p>`;
            setStatus("mandiStatus", "Search finished with 0 records.", "error");
            return;
        }

        resultsContainer.innerHTML = data.records.map(record => {
            const price = Number(record.modal_price_rs_per_quintal) || 0;
            const cropName = record.commodity_reported || record.crop;

            return `
                <div class="mandi-record-card">
                    <div class="mandi-card-header">
                        <div>
                            <div class="mandi-crop-name">${escapeHTML(cropName)}</div>
                            <div class="mandi-market-name">🏛️ ${escapeHTML(record.market)}, ${escapeHTML(record.district || record.state)}</div>
                        </div>
                        <span class="badge badge-market">Mandi Price</span>
                    </div>

                    <div class="mandi-price-box">
                        <div class="mandi-modal-price">${formatRupees(price)} / qtl</div>
                        <div class="mandi-range">Range: ${formatRupees(record.min_price_rs_per_quintal)} – ${formatRupees(record.max_price_rs_per_quintal)}</div>
                    </div>

                    <div style="font-size: 0.8rem; color: var(--text-subtle); margin-bottom: 10px;">
                        📅 Arrival Date: ${escapeHTML(record.arrival_date || "Recent")}
                    </div>

                    <button type="button" class="btn btn-secondary btn-sm" onclick="prefillProfitCalculator('${escapeHTML(cropName)}', ${price}, 10, 25000)">
                        Use in Profit Calculator
                    </button>
                </div>
            `;
        }).join("");

        setStatus("mandiStatus", `Retrieved ${data.records.length} mandi records from ${data.source || 'Agricultural Database'}.`, "success");

    } catch (err) {
        setStatus("mandiStatus", `Error fetching mandi prices: ${err.message}`, "error");
    } finally {
        setButtonLoading("searchMandiButton", false, "Searching Mandis...", "Search Mandi Rates");
    }
});

/* ==========================================================================
   10. Custom Farm Profit Calculator
   ========================================================================== */
window.prefillProfitCalculator = function(crop, price, yieldVal, costVal) {
    if (getElement("calcCropName")) getElement("calcCropName").value = crop;
    if (getElement("calcModalPrice")) getElement("calcModalPrice").value = price;
    if (getElement("calcYield")) getElement("calcYield").value = yieldVal;
    if (getElement("calcCultivationCost")) getElement("calcCultivationCost").value = costVal;
    if (getElement("calcLandAcres")) getElement("calcLandAcres").value = currentAcreage;

    const calcSection = getElement("profitCalculatorSection");
    if (calcSection) {
        calcSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    // Auto calculate
    getElement("calculateProfitBtn")?.click();
};

const customProfitForm = getElement("customProfitForm");

customProfitForm?.addEventListener("submit", async (event) => {
    event.preventDefault();

    const price = Number(getElement("calcModalPrice")?.value || 0);
    const yieldVal = Number(getElement("calcYield")?.value || 0);
    const acres = Number(getElement("calcLandAcres")?.value || 1.0);
    const costPerAcre = Number(getElement("calcCultivationCost")?.value || 0);
    const transportTotal = Number(getElement("calcTransportCost")?.value || 0);
    const otherTotal = Number(getElement("calcOtherExpenses")?.value || 0);

    const totalYield = yieldVal * acres;
    const cultivationTotal = costPerAcre * acres;

    const body = {
        modal_price: price,
        expected_yield_quintals: totalYield,
        cultivation_cost: cultivationTotal,
        transport_cost: transportTotal,
        other_costs: otherTotal,
        land_acres: acres
    };

    setButtonLoading("calculateProfitBtn", true, "Calculating...", "Calculate Net Return");

    try {
        const data = await fetchJSON(`${API_BASE}/api/profit-estimate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        if (!data.success) {
            throw new Error(data.error || "Profit calculation failed.");
        }

        const outContainer = getElement("customProfitResult");
        if (!outContainer) return;

        const netProfit = data.estimated_net_profit_rs;
        const profitPerAcre = netProfit / acres;

        outContainer.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <h4 style="font-size: 1.2rem; color: var(--primary-dark);">
                    📊 Financial Projection: ${escapeHTML(getElement("calcCropName")?.value || "Selected Crop")} (${acres} Acres)
                </h4>
                <span class="badge ${netProfit >= 0 ? 'badge-success' : 'badge-warning'}">${escapeHTML(data.result_type)}</span>
            </div>

            <div class="outcome-grid">
                <div class="outcome-tile profit">
                    <div class="outcome-label">Total Net Profit / Return</div>
                    <div class="outcome-value">${formatRupees(netProfit)}</div>
                    <small>(${formatRupees(profitPerAcre)} / acre)</small>
                </div>
                <div class="outcome-tile">
                    <div class="outcome-label">Gross Revenue</div>
                    <div class="outcome-value">${formatRupees(data.gross_revenue_rs)}</div>
                    <small>${totalYield.toFixed(1)} quintals @ ${formatRupees(price)}</small>
                </div>
                <div class="outcome-tile">
                    <div class="outcome-label">Total Production Costs</div>
                    <div class="outcome-value">${formatRupees(data.total_cost_rs)}</div>
                    <small>Cultivation + Transport + Other</small>
                </div>
                <div class="outcome-tile">
                    <div class="outcome-label">Return on Investment (ROI)</div>
                    <div class="outcome-value" style="color: #15803d;">${data.roi_pct}%</div>
                    <small>${formatRupees(data.estimated_profit_per_quintal_rs)} profit/quintal</small>
                </div>
            </div>
        `;

    } catch (err) {
        alert(err.message);
    } finally {
        setButtonLoading("calculateProfitBtn", false, "Calculating...", "Calculate Net Return");
    }
});

// Auto-fetch default Vijayawada weather on startup
window.addEventListener("DOMContentLoaded", () => {
    loadWeather("Vijayawada");
});
