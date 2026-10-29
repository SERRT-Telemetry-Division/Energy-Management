# """
# SIMPLE DEMO FOR THE PIT CREW DISPLAY

# """

# import pandas as pd
# import streamlit as st

# connected = True             # Boolean to confirm car connection to pits

# st.set_page_config(page_title="Solar Car Dashboard", page_icon="☀️", layout="wide")

# # ----------------------------------------------------------------------
# # MOCK DATA (replace these variables with live data later)
# # ----------------------------------------------------------------------
# weather_data = {
#     "ghi": 845,              # Global Horizontal Irradiance (W/m²)
#     "cloudiness": 20,        # %
#     "temperature": 31.5,     # °C
#     "rain_chance": 10,       # %
# }

# car_data = {
#     "speed": 78,             # km/h
#     "inclination": 2.4,      # degrees (+ uphill, - downhill)
#     "soc": 72,               # state of charge, %
#     "battery_voltage": 128.6,  # V
#     "battery_current": -34.2,  # A (negative = discharging)
#     "latitude": -23.6980,
#     "longitude": 133.8807,
# }

# # ----------------------------------------------------------------------
# # LAYOUT
# # ----------------------------------------------------------------------
# st.title("☀️ Solar Car Team Dashboard")

# tab_live, tab_predictions, = st.tabs(["Live Telemetry", "EMS Predictions"])

# with tab_live:
#     weather_col, car_col = st.columns(2, gap="large")

#     # ---------------- Weather ----------------
#     with weather_col:
#         st.subheader("🌤️ Current Weather")
#         w1, w2 = st.columns(2)
#         w1.metric("GHI", f"{weather_data['ghi']} W/m²")
#         w2.metric("Cloudiness", f"{weather_data['cloudiness']} %")
#         w3, w4 = st.columns(2)
#         w3.metric("Temperature", f"{weather_data['temperature']} °C")
#         w4.metric("Chance of Rain", f"{weather_data['rain_chance']} %")

#         st.caption("Cloud cover")
#         st.progress(weather_data["cloudiness"] / 100)
#         st.caption("Rain probability")
#         st.progress(weather_data["rain_chance"] / 100)

#     # ---------------- Car ----------------
#     with car_col:
#         st.subheader("🏎️ Car Data")
#         if connected:
#             c1, c2 = st.columns(2)
#             c1.metric("Current Speed", f"{car_data['speed']} km/h")
#             c2.metric("Inclination", f"{car_data['inclination']}°")
#             c3, c4 = st.columns(2)
#             c3.metric("State of Charge", f"{car_data['soc']} %")
#             c4.metric("Battery Voltage", f"{car_data['battery_voltage']} V")
#             c5, c6 = st.columns(2)
#             c5.metric("Battery Current", f"{car_data['battery_current']} A")
#             c6.metric(
#                 "GPS Location",
#                 f"{car_data['latitude']:.4f}, {car_data['longitude']:.4f}",
#             )

#             st.caption("State of charge")
#             st.progress(car_data["soc"] / 100)

#             # st.map(
#             #     pd.DataFrame(
#             #         {"lat": [car_data["latitude"]], "lon": [car_data["longitude"]]}
#             #     ),
#             #     zoom=8,
#             # )
#         else:
#             st.subheader("Waiting for Connection...")

# with tab_predictions:
#     st.subheader("Coming Soon")








































# MainDisplay.py

import math
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from streamlit_autorefresh import st_autorefresh
from streamlit_geolocation import streamlit_geolocation


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Solar Car Dashboard",
    page_icon="☀️",
    layout="wide",
)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_LAT = 18.2013
DEFAULT_LON = -67.1452

REFRESH_SECONDS = 30

# Mock telemetry until the solar car is connected.
car_data = {
    "speed": 78.0,
    "soc": 72.0,
    "battery_voltage": 128.6,
    "battery_current": -34.2,
    "inclination": 2.4,
    "latitude": -23.6980,
    "longitude": 133.8807,
}

# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "latitude": DEFAULT_LAT,
    "longitude": DEFAULT_LON,
    "location_name": "Default location",
    "search_text": "",
    "location_mode": "Search location",
    "weather_connected": False,
    "weather_error": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# WEATHER FUNCTIONS — SALVAGED FROM OLD CODE
# ============================================================

def calculate_air_density(temperature_c, pressure_hpa):
    """Calculate dry-air density in kg/m³ using the ideal gas law."""
    temperature_k = temperature_c + 273.15
    pressure_pa = pressure_hpa * 100
    return pressure_pa / (287.05 * temperature_k)


def search_location(query):
    """Convert a city or location name into latitude and longitude."""
    response = requests.get(
        GEOCODING_URL,
        params={
            "name": query,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )
    response.raise_for_status()

    results = response.json().get("results", [])

    if not results:
        return None

    place = results[0]
    parts = [
        place.get("name"),
        place.get("admin1"),
        place.get("country"),
    ]

    return {
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "name": ", ".join(dict.fromkeys(p for p in parts if p)),
    }


@st.cache_data(ttl=25, show_spinner=False)
def get_weather(lat, lon):
    """Retrieve current weather and hourly forecast from Open-Meteo."""
    response = requests.get(
        WEATHER_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "surface_pressure,"
                "cloud_cover,"
                "precipitation,"
                "wind_speed_10m,"
                "wind_direction_10m,"
                "shortwave_radiation"
            ),
            "hourly": (
                "temperature_2m,"
                "shortwave_radiation,"
                "precipitation_probability,"
                "wind_speed_10m"
            ),
            "forecast_days": 2,
            "wind_speed_unit": "ms",
            "timezone": "auto",
        },
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    temperature = current["temperature_2m"]
    pressure = current["surface_pressure"]

    current_weather = {
        "temperature": temperature,
        "humidity": current["relative_humidity_2m"],
        "pressure": pressure,
        "cloud_cover": current["cloud_cover"],
        "precipitation": current["precipitation"],
        "wind_speed": current["wind_speed_10m"],
        "wind_direction": current["wind_direction_10m"],
        "ghi": current["shortwave_radiation"],
        "air_density": calculate_air_density(temperature, pressure),
        "time": current["time"],
    }

    forecast = pd.DataFrame(data["hourly"])
    forecast["time"] = pd.to_datetime(forecast["time"])

    return current_weather, forecast


def wind_direction_label(degrees):
    """Convert compass degrees into a readable direction."""
    directions = [
        "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
    ]
    return directions[round(degrees / 22.5) % 16]


# ============================================================
# HEADER
# ============================================================

st.title("☀️ Solar Car Team Dashboard")

# ============================================================
# PHASE 1: HORIZONTAL LOCATION CONTROLS
# ============================================================

st.subheader("Location & Data Controls")

location_col, search_col, search_button_col, refresh_col = st.columns(
    [1.2, 2.5, 0.8, 1],
    vertical_alignment="bottom",
)

with location_col:
    location_mode = st.selectbox(
        "Location mode",
        ["Search location", "Precise location"],
        key="location_mode",
    )

with search_col:
    with st.form("location_search_form"):
        query_col, submit_col = st.columns(
            [4, 1],
            vertical_alignment="bottom",
        )

        with query_col:
            search_text = st.text_input(
                "City / location",
                key="search_text",
                placeholder="e.g. Mayagüez, Puerto Rico",
            )

        with submit_col:
            search_clicked = st.form_submit_button(
                "Search",
                use_container_width=True,
            )

with refresh_col:
    refresh_clicked = st.button(
        "🔄 Refresh now",
        use_container_width=True,
    )

if search_clicked:
    if not search_text.strip():
        st.warning("Enter a city or location first.")
    else:
        try:
            place = search_location(search_text.strip())

            if place:
                st.session_state.latitude = place["latitude"]
                st.session_state.longitude = place["longitude"]
                st.session_state.location_name = place["name"]
                get_weather.clear()
                st.rerun()
            else:
                st.error("Location not found. Try another search.")

        except requests.RequestException as exc:
            st.error(f"Location search failed: {exc}")

# Browser geolocation is requested only in precise-location mode.
if location_mode == "Precise location":
    st.caption(
        "Allow location access in your browser when prompted. "
        "Your previous location remains active if permission is denied."
    )

    try:
        position = streamlit_geolocation()

        if (
            position
            and position.get("latitude") is not None
            and position.get("longitude") is not None
        ):
            new_lat = position["latitude"]
            new_lon = position["longitude"]

            if (
                new_lat != st.session_state.latitude
                or new_lon != st.session_state.longitude
            ):
                st.session_state.latitude = new_lat
                st.session_state.longitude = new_lon
                st.session_state.location_name = "Precise browser location"
                get_weather.clear()
                st.rerun()

    except Exception:
        st.info("Browser geolocation is unavailable. Search by city instead.")

if refresh_clicked:
    get_weather.clear()
    st.rerun()

st.caption(
    f"Active location: {st.session_state.location_name} | "
    f"Latitude: {st.session_state.latitude:.5f} | "
    f"Longitude: {st.session_state.longitude:.5f}"
)

# ============================================================
# PHASE 2: SYSTEM STATUS AND AUTO-REFRESH
# ============================================================

st_autorefresh(
    interval=REFRESH_SECONDS * 1000,
    limit=None,
    key="dashboard_autorefresh",
)

try:
    weather_data, forecast_data = get_weather(
        st.session_state.latitude,
        st.session_state.longitude,
    )
    st.session_state.weather_connected = True
    st.session_state.weather_error = None

except (requests.RequestException, KeyError, ValueError) as exc:
    weather_data = None
    forecast_data = pd.DataFrame()
    st.session_state.weather_connected = False
    st.session_state.weather_error = str(exc)

status_col, api_col, refresh_status_col, mode_col = st.columns(4)

with status_col:
    st.markdown("**System status**")
    st.success("Online")

with api_col:
    st.markdown("**Open-Meteo**")
    if st.session_state.weather_connected:
        st.success("Connected")
    else:
        st.error("Disconnected")

with refresh_status_col:
    st.markdown("**Auto-refresh**")
    st.caption(f"Every {REFRESH_SECONDS} seconds")

with mode_col:
    st.markdown("**Data source**")
    st.caption("Live weather / Mock car data")

if not st.session_state.weather_connected:
    st.warning(
        "Weather data could not be retrieved. Check your internet "
        "connection or try Refresh now."
    )

# ============================================================
# PHASE 3: DISPLAY MODE AND MAIN TABS
# ============================================================

display_mode = st.radio(
    "Display mode",
    ["Default", "Advanced"],
    horizontal=True,
    help="Advanced displays additional engineering data and analytics.",
)

tab_predictions, tab_live = st.tabs(
    ["EMS Predictions (Theoretical)", "Live Telemetry"]
)

# ============================================================
# PHASE 4: EMS PREDICTIONS
# ============================================================

with tab_predictions:
    if weather_data is None:
        st.info("Weather data is unavailable. Try refreshing the dashboard.")

    else:
        weather_col, car_col = st.columns(2, gap="large")

        # ----------------------------------------------------
        # CURRENT WEATHER
        # ----------------------------------------------------

        with weather_col:
            st.subheader("🌤️ Current Weather")

            w1, w2 = st.columns(2)
            w1.metric(
                "Temperature",
                f"{weather_data['temperature']:.1f} °C",
            )
            w2.metric(
                "Solar Radiation",
                f"{weather_data['ghi']:.0f} W/m²",
            )

            w3, w4 = st.columns(2)
            w3.metric(
                "Wind Speed",
                f"{weather_data['wind_speed']:.1f} m/s",
            )
            w4.metric(
                "Wind Direction",
                f"{wind_direction_label(weather_data['wind_direction'])} "
                f"({weather_data['wind_direction']:.0f}°)",
            )

            st.caption("Cloud cover")
            st.progress(
                max(0.0, min(1.0, weather_data["cloud_cover"] / 100))
            )

            if display_mode == "Advanced":
                st.divider()
                st.markdown("**Advanced weather measurements**")

                a1, a2 = st.columns(2)
                a1.metric("Relative Humidity", f"{weather_data['humidity']} %")
                a2.metric("Surface Pressure", f"{weather_data['pressure']:.1f} hPa")

                a3, a4 = st.columns(2)
                a3.metric("Precipitation", f"{weather_data['precipitation']} mm")
                a4.metric("Air Density", f"{weather_data['air_density']:.4f} kg/m³")

                st.caption(
                    "Air density is calculated from temperature and "
                    "surface pressure using the ideal gas law."
                )

                # Forecast analytics
                st.divider()
                st.subheader("Forecast Analytics")

                temperature_chart = px.line(
                    forecast_data,
                    x="time",
                    y="temperature_2m",
                    title="Temperature Forecast",
                    labels={
                        "time": "Time",
                        "temperature_2m": "Temperature (°C)",
                    },
                )
                st.plotly_chart(
                    temperature_chart,
                    use_container_width=True,
                )

                solar_chart = px.line(
                    forecast_data,
                    x="time",
                    y="shortwave_radiation",
                    title="Solar Radiation Forecast",
                    labels={
                        "time": "Time",
                        "shortwave_radiation": "Solar radiation (W/m²)",
                    },
                )
                st.plotly_chart(
                    solar_chart,
                    use_container_width=True,
                )

                st.subheader("Forecast Data Stream")
                st.dataframe(
                    forecast_data,
                    use_container_width=True,
                    hide_index=True,
                )

                st.caption(
                    "Forecast values are hourly API data, not vehicle "
                    "measurements. Shortwave radiation is used as a "
                    "solar-radiation indicator; it is not identical to "
                    "panel-plane irradiance."
                )

        # ----------------------------------------------------
        # CAR DATA
        # ----------------------------------------------------

        with car_col:
            st.subheader("🏎️ Car Data")

            st.caption(
                "Mock telemetry — replace with the actual vehicle data feed."
            )

            c1, c2 = st.columns(2)
            c1.metric("Current Speed", f"{car_data['speed']:.1f} km/h")
            c2.metric("State of Charge", f"{car_data['soc']:.0f} %")

            st.caption("Battery state of charge")
            st.progress(
                max(0.0, min(1.0, car_data["soc"] / 100))
            )

            st.metric(
                "Vehicle Location",
                f"{car_data['latitude']:.4f}, {car_data['longitude']:.4f}",
            )

            if display_mode == "Advanced":
                st.divider()
                st.markdown("**Advanced vehicle measurements**")

                c3, c4 = st.columns(2)
                c3.metric(
                    "Battery Voltage",
                    f"{car_data['battery_voltage']:.1f} V",
                )
                c4.metric(
                    "Battery Current",
                    f"{car_data['battery_current']:.1f} A",
                )

                st.metric(
                    "Inclination",
                    f"{car_data['inclination']:.1f}°",
                )

                st.caption(
                    "Negative battery current represents discharge in "
                    "this demo's convention. Verify the convention with "
                    "the actual telemetry source."
                )

# ============================================================
# PHASE 3: LIVE TELEMETRY PLACEHOLDER
# ============================================================

with tab_live:
    st.subheader("📡 Live Telemetry")

    st.info(
        "The Live Telemetry interface is reserved for future integration. "
        "The current vehicle readings are mock data and are not a live feed."
    )

    st.markdown(
        """
        **Planned live data**
        - Vehicle speed and GPS position
        - Battery state of charge, voltage, and current
        - Vehicle inclination
        - Live connection and telemetry status
        """
    )
