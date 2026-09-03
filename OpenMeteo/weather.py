import requests
import pandas as pd

def search_location(location_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": location_name,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    results = data.get("results")

    if not results:
        return None

    location = results[0]

    return {
        "name": location.get("name"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "country": location.get("country"),
        "admin1": location.get("admin1")
    }


def fetch_weather(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover",
            "precipitation",
            "shortwave_radiation"
        ],
        "timezone": "auto"
    }

    response = requests.get(
        url,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data["hourly"])

    # Save useful Open-Meteo metadata inside the DataFrame
    df.attrs["timezone"] = data.get("timezone", "Unknown")
    df.attrs["utc_offset_seconds"] = data.get(
        "utc_offset_seconds",
        0
    )

    return df


if __name__ == "__main__":
    latitude = 18.21
    longitude = -67.14

    weather_df = fetch_weather(
        latitude,
        longitude
    )

    print(weather_df.head())