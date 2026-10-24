
"use strict";

// ==================================================
// 11. Government mandi price search
// ==================================================

const MANDI_URL = "http://127.0.0.1:5000/api/mandi-prices";
const PROFIT_URL = "http://127.0.0.1:5000/api/profit-estimate";

const mandiForm = document.getElementById("mandiForm");
const mandiStatus = document.getElementById("mandiStatus");
const mandiResults = document.getElementById("mandiResults");
const searchMandiButton = document.getElementById("searchMandiButton");

const profitForm = document.getElementById("profitForm");
const selectedModalPrice = document.getElementById("selectedModalPrice");
const profitResults = document.getElementById("profitResults");
const calculateProfitButton =
    document.getElementById("calculateProfitButton");

let currentMandiPrices = [];

// Format rupee values for Indian number grouping.
function formatRupees(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "Unavailable";
    }

    return "₹" + number.toLocaleString("en-IN", {
        maximumFractionDigits: 2
    });
}

function showMandiMessage(message, type = "info") {
    mandiStatus.replaceChildren();

    const element = createElement(
        "p",
        `message ${type}`,
        message
    );

    mandiStatus.appendChild(element);
}

function renderMandiPrices(prices) {
    mandiResults.replaceChildren();

    if (!Array.isArray(prices) || prices.length === 0) {
        mandiResults.appendChild(
            createElement(
                "p",
                "empty-state",
                "No matching reported mandi prices were found. " +
                "Try another district or crop."
            )
        );
        return;
    }

    const grid = createElement("div", "crop-grid");

    prices.forEach((item, index) => {
        const card = createElement("article", "crop-card");

        card.appendChild(
            createElement(
                "h3",
                "crop-name",
                `${item.commodity_reported || item.crop} — ` +
                `${item.market || "Unknown market"}`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "market-price",
                `Modal price: ${formatRupees(
                    item.modal_price_rs_per_quintal
                )} per quintal`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "",
                `Minimum price: ${formatRupees(
                    item.min_price_rs_per_quintal
                )}`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "",
                `Maximum price: ${formatRupees(
                    item.max_price_rs_per_quintal
                )}`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "",
                `District: ${item.district || "Not provided"}`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "",
                `Arrival date: ${item.arrival_date || "Not provided"}`
            )
        );

        card.appendChild(
            createElement(
                "p",
                "prototype-note",
                "Source: Government of India data.gov.in / AGMARKNET"
            )
        );

        const chooseButton = createElement(
            "button",
            "",
            "Use This Price"
        );

        chooseButton.type = "button";

        chooseButton.addEventListener("click", () => {
            const price = Number(item.modal_price_rs_per_quintal);

            if (!Number.isFinite(price) || price <= 0) {
                showMandiMessage(
                    "This record does not have a valid modal price.",
                    "error"
                );
                return;
            }

            selectedModalPrice.value = price;
            profitResults.replaceChildren();

            const selectionMessage = createElement(
                "p",
                "message info",
                `Selected ${item.commodity_reported || item.crop} at ` +
                `${item.market || "unknown market"}, ` +
                `${formatRupees(price)} per quintal.`
            );

            profitResults.appendChild(selectionMessage);

            profitForm.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });
        });

        card.appendChild(chooseButton);
        grid.appendChild(card);
    });

    mandiResults.appendChild(grid);
}

// Search the government mandi API.
mandiForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!mandiForm.reportValidity()) {
        return;
    }

    const crop = document.getElementById("mandiCrop").value;
    const state = document.getElementById("mandiState").value;
    const district = document.getElementById("mandiDistrict")
        .value.trim();

    const params = new URLSearchParams({
        crop,
        state
    });

    if (district) {
        params.set("district", district);
    }

    searchMandiButton.disabled = true;
    searchMandiButton.textContent = "Searching...";
    mandiResults.replaceChildren();
    profitResults.replaceChildren();
    selectedModalPrice.value = "";
    currentMandiPrices = [];

    showMandiMessage(
        "Fetching reported mandi prices. Please wait...",
        "loading"
    );

    try {
        const response = await fetch(`${MANDI_URL}?${params}`);

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || `Mandi API failed with HTTP ${response.status}.`
            );
        }

        currentMandiPrices = Array.isArray(data.prices)
            ? data.prices
            : [];

        showMandiMessage(
            `${data.count ?? currentMandiPrices.length} reported records found. ` +
            "Check each record's arrival date before using its price.",
            "info"
        );

        renderMandiPrices(currentMandiPrices);

    } catch (error) {
        console.error("Mandi search failed:", error);

        showMandiMessage(
            error.message ||
            "Could not load mandi prices. Check Flask, your API key, " +
            "and your internet connection.",
            "error"
        );
    } finally {
        searchMandiButton.disabled = false;
        searchMandiButton.textContent = "Search Mandi Prices";
    }
});

// ==================================================
// 12. Profit calculation using the selected price
// ==================================================

profitForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!profitForm.reportValidity()) {
        return;
    }

    const price = Number(selectedModalPrice.value);

    if (!Number.isFinite(price) || price <= 0) {
        profitResults.replaceChildren(
            createElement(
                "p",
                "message error",
                "Search mandi prices and click Use This Price first."
            )
        );
        return;
    }

    const body = {
        modal_price: price,
        expected_yield_quintals:
            Number(document.getElementById("expectedYield").value),
        cultivation_cost:
            Number(document.getElementById("cultivationCost").value),
        transport_cost:
            Number(document.getElementById("transportCost").value),
        other_costs:
            Number(document.getElementById("otherCosts").value)
    };

    for (const [name, value] of Object.entries(body)) {
        if (!Number.isFinite(value) || value < 0) {
            profitResults.replaceChildren(
                createElement(
                    "p",
                    "message error",
                    `Please enter a valid non-negative number for ${name}.`
                )
            );
            return;
        }
    }

    if (body.expected_yield_quintals <= 0) {
        profitResults.replaceChildren(
            createElement(
                "p",
                "message error",
                "Expected yield must be greater than zero."
            )
        );
        return;
    }

    calculateProfitButton.disabled = true;
    calculateProfitButton.textContent = "Calculating...";
    profitResults.replaceChildren(
        createElement("p", "message loading", "Calculating estimated profit...")
    );

    try {
        const response = await fetch(PROFIT_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.error || `Profit calculation failed: HTTP ${response.status}.`
            );
        }

        profitResults.replaceChildren();

        const result = createElement("section", "crop-card");

        result.appendChild(
            createElement("h3", "crop-name", data.result_type)
        );

        result.appendChild(
            createElement(
                "p",
                "market-price",
                `Estimated net profit/loss: ${
                    formatRupees(data.estimated_net_profit_rs)
                }`
            )
        );

        const rows = [
            ["Selected modal price", `${formatRupees(data.modal_price_rs_per_quintal)} / quintal`],
            ["Expected yield", `${data.expected_yield_quintals} quintals`],
            ["Gross revenue", formatRupees(data.gross_revenue_rs)],
            ["Cultivation cost", formatRupees(data.cultivation_cost_rs)],
            ["Transport cost", formatRupees(data.transport_cost_rs)],
            ["Other expenses", formatRupees(data.other_costs_rs)],
            ["Total costs", formatRupees(data.total_cost_rs)],
            [
                "Profit/loss per quintal",
                data.estimated_profit_per_quintal_rs === null
                    ? "Unavailable"
                    : formatRupees(data.estimated_profit_per_quintal_rs)
            ]
        ];

        const list = document.createElement("ul");

        rows.forEach(([label, value]) => {
            list.appendChild(
                createElement("li", "", `${label}: ${value}`)
            );
        });

        result.appendChild(list);

        result.appendChild(
            createElement(
                "p",
                "prototype-note",
                data.warning || "This is an estimate, not a guaranteed return."
            )
        );

        profitResults.appendChild(result);

    } catch (error) {
        console.error("Profit calculation failed:", error);

        profitResults.replaceChildren(
            createElement(
                "p",
                "message error",
                error.message || "Could not calculate estimated profit."
            )
        );
    } finally {
        calculateProfitButton.disabled = false;
        calculateProfitButton.textContent = "Calculate Estimated Profit";
    }
});
