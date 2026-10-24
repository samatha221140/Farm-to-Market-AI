
import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


VIJAYAWADA = {
    "name": "Vijayawada",
    "latitude": 16.5075,
    "longitude": 80.6466,
}


def get_vijayawada_weather():
    """Fetch current and 3-day forecast data from Open-Meteo."""

    params = {
        "latitude": VIJAYAWADA["latitude"],
        "longitude": VIJAYAWADA["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "weather_code"
        ),
        "daily": (
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "precipitation_probability_max"
        ),
        "forecast_days": 3,
        "timezone": "Asia/Kolkata",
    }

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        + urlencode(params)
    )

    req = Request(
        url,
        headers={"User-Agent": "Farm-to-Market-AI/1.0"},
    )

    try:
        with urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

        current = data.get("current", {})
        daily = data.get("daily", {})

        # Keep the forecast data aligned by date.
        forecast = []

        dates = daily.get("time", [])

        for index, date in enumerate(dates):
            forecast.append({
                "date": date,
                "temperature_max_C": daily[
                    "temperature_2m_max"
                ][index],
                "temperature_min_C": daily[
                    "temperature_2m_min"
                ][index],
                "precipitation_mm": daily[
                    "precipitation_sum"
                ][index],
                "precipitation_probability_percent": daily[
                    "precipitation_probability_max"
                ][index],
            })

        return {
            "success": True,
            "location": VIJAYAWADA["name"],
            "coordinates": {
                "latitude": VIJAYAWADA["latitude"],
                "longitude": VIJAYAWADA["longitude"],
            },
            "timezone": data.get("timezone", "Asia/Kolkata"),
            "source": "Open-Meteo",
            "current": {
                "time": current.get("time"),
                "temperature_C": current.get("temperature_2m"),
                "humidity_percent": current.get(
                    "relative_humidity_2m"
                ),
                "precipitation_mm": current.get("precipitation"),
                "weather_code": current.get("weather_code"),
            },
            "forecast": forecast,
        }

    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        return {
            "success": False,
            "location": VIJAYAWADA["name"],
            "error": "Weather service is temporarily unavailable.",
            "details": str(exc),
        }
    @app.route("/api/weather", methods=["GET"])
    def api_weather():
        result = get_vijayawada_weather()

        if not result["success"]:
            return jsonify(result), 502

        return jsonify(result), 200 