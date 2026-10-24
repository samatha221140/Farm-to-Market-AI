
import os
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
import json


API_URL = (
    "https://api.data.gov.in/resource/"
    "9ef84268-d588-465a-a308-a864a43d0070"
)

CROP_ALIASES = {
    "bajra": ["Bajra", "Pearl Millet"],
    "bengal gram": ["Bengal Gram", "Gram", "Chana"],
    "black gram": ["Black Gram", "Blackgram", "Urad"],
    "chilli": ["Chilli", "Chillies", "Dry Chilli"],
    "cotton": ["Cotton"],
    "green gram": ["Green Gram", "Greengram", "Moong"],
    "groundnut": ["Groundnut", "Peanut"],
    "jowar": ["Jowar", "Sorghum"],
    "maize": ["Maize"],
    "red gram": ["Red Gram", "Arhar", "Tur", "Pigeon Pea"],
    "rice": ["Rice", "Paddy"],
    "sugarcane": ["Sugarcane"],
}


def _fetch_records(params):
    """Fetch records from the Government of India's data.gov.in API."""

    api_key = os.getenv("DATA_GOV_IN_API_KEY")

    if not api_key:
        raise RuntimeError(
            "DATA_GOV_IN_API_KEY is missing. Configure your "
            "data.gov.in API key in the backend environment."
        )

    query = {
        "api-key": api_key,
        "format": "json",
        "limit": 1000,
        **params,
    }

    url = f"{API_URL}?{urlencode(query)}"
    request = Request(
        url,
        headers={"User-Agent": "Farm-to-Market-AI/1.0"}
    )

    try:
        with urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise RuntimeError(
            f"Mandi API returned HTTP {error.code}."
        ) from error
    except URLError as error:
        raise RuntimeError(
            "Could not connect to the mandi API. Check your internet."
        ) from error
    except (TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(
            "Mandi API timed out or returned invalid JSON."
        ) from error

    records = payload.get("records", [])

    if not isinstance(records, list):
        raise RuntimeError("Unexpected mandi API response format.")

    return records


def get_mandi_prices(crop, state="Andhra Pradesh", district=None):
    """Return matching mandi records with prices in rupees per quintal."""

    if not isinstance(crop, str) or not crop.strip():
        raise ValueError("Crop name is required.")

    crop = crop.strip()
    aliases = CROP_ALIASES.get(crop.lower(), [crop])
    all_records = []

    # Query each known crop name because government commodity
    # labels may differ from the names used in our recommendation UI.
    for commodity in aliases:
        params = {
            "filters[state.keyword]": state,
            "filters[commodity]": commodity,
        }

        if district:
            params["filters[district]"] = district

        all_records.extend(_fetch_records(params))

    # Some API records may match more than one alias.
    unique = {}
    for record in all_records:
        key = (
            record.get("state"),
            record.get("district"),
            record.get("market"),
            record.get("commodity"),
            record.get("variety"),
            record.get("arrival_date"),
        )
        unique[key] = record

    results = []

    for record in unique.values():
        try:
            minimum = float(record["min_price"])
            maximum = float(record["max_price"])
            modal = float(record["modal_price"])
        except (KeyError, TypeError, ValueError):
            continue

        if minimum <= 0 or maximum <= 0 or modal <= 0:
            continue

        results.append({
            "crop": crop,
            "commodity_reported": record.get("commodity"),
            "state": record.get("state"),
            "district": record.get("district"),
            "market": record.get("market"),
            "variety": record.get("variety"),
            "grade": record.get("grade"),
            "arrival_date": record.get("arrival_date"),
            "min_price_rs_per_quintal": minimum,
            "max_price_rs_per_quintal": maximum,
            "modal_price_rs_per_quintal": modal,
            "source": "Government of India data.gov.in / AGMARKNET",
        })

    # Most recent reported dates first. Dates with an unrecognized
    # format remain in the results but are sorted after valid dates.
    def date_key(item):
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(
                    item["arrival_date"] or "", fmt
                )
            except ValueError:
                pass
        return datetime.min

    results.sort(key=date_key, reverse=True)
    return results


def calculate_profit(
    modal_price,
    expected_yield_quintals,
    cultivation_cost,
    transport_cost=0,
    other_costs=0,
):
    """Estimate farm revenue and net profit using user-supplied values."""

    values = {
        "modal_price": modal_price,
        "expected_yield_quintals": expected_yield_quintals,
        "cultivation_cost": cultivation_cost,
        "transport_cost": transport_cost,
        "other_costs": other_costs,
    }

    for name, value in values.items():
        if isinstance(value, bool):
            raise ValueError(f"{name} must be a number.")
        try:
            number = float(value)
        except (TypeError, ValueError):
            raise ValueError(f"{name} must be a number.")

        if not (number >= 0 and number < float("inf")):
            raise ValueError(f"{name} must be finite and non-negative.")

        values[name] = number

    price = values["modal_price"]
    yield_q = values["expected_yield_quintals"]

    gross_revenue = price * yield_q
    total_cost = (
        values["cultivation_cost"]
        + values["transport_cost"]
        + values["other_costs"]
    )
    net_profit = gross_revenue - total_cost

    return {
        "modal_price_rs_per_quintal": price,
        "expected_yield_quintals": yield_q,
        "gross_revenue_rs": round(gross_revenue, 2),
        "cultivation_cost_rs": round(values["cultivation_cost"], 2),
        "transport_cost_rs": round(values["transport_cost"], 2),
        "other_costs_rs": round(values["other_costs"], 2),
        "total_cost_rs": round(total_cost, 2),
        "estimated_net_profit_rs": round(net_profit, 2),
        "estimated_profit_per_quintal_rs": (
            round(net_profit / yield_q, 2) if yield_q > 0 else None
        ),
        "result_type": (
            "Estimated profit" if net_profit >= 0 else "Estimated loss"
        ),
        "warning": (
            "This is an estimate based on the reported mandi modal price "
            "and your inputs. Actual sale price, yield, quality, fees, "
            "and costs may differ."
        ),
    }
