import requests

from langchain_core.tools import tool

from app.config.constants import TOOL_WEATHER


@tool
def weather(city: str) -> str:
    """
    Get the current weather for a given city.

    Use this tool when the user asks about current weather,
    temperature, or wind speed for a specific city.

    Args:
        city: Name of the city.
    """

    if not city:
        return "City name is required."

    try:

        # ====================================================
        # Step 1: Convert city name to coordinates
        # ====================================================

        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
            },
            timeout=10,
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return f"City '{city}' not found."

        location = geo_data["results"][0]

        latitude = location["latitude"]
        longitude = location["longitude"]

        # ====================================================
        # Step 2: Fetch current weather
        # ====================================================

        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,wind_speed_10m",
            },
            timeout=10,
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data["current"]

        # ====================================================
        # Step 3: Format result
        # ====================================================

        result = (
            f"City: {city}\n"
            f"Temperature: {current['temperature_2m']}°C\n"
            f"Wind Speed: {current['wind_speed_10m']} km/h"
        )

        return result

    except requests.RequestException as e:

        return f"Weather service error: {str(e)}"

    except Exception as e:

        return f"Unable to retrieve weather: {str(e)}"

