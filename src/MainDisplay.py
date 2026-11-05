# ============================================================
# MAIN DISPLAY — SOLAR CAR DASHBOARD
# ============================================================

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

from pathlib import Path
from streamlit_autorefresh import st_autorefresh
from streamlit_geolocation import streamlit_geolocation


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Solar Car Dashboard",
    page_icon="☀️",
    layout="wide",
)


# ============================================================
# LOAD CSS
# ============================================================

CSS_PATH = Path(__file__).parent / "styles" / "MainDisplaystyle.css"
LOGO_PATH = Path(__file__).parent / "styles" / "Logo.png"


def load_css(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        css = file.read()

    st.markdown(
        f"<style>{css}</style>",
        unsafe_allow_html=True,
    )


load_css(CSS_PATH)

# Status strip styles live here so they can't get lost if the CSS file changes.
st.markdown(
    """
    <style>
    .status-strip {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        align-items: center;
        gap: 0.6rem 1.4rem;
    }
    .status-item {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.35rem 0.8rem;
        border-radius: 999px;
        background: rgba(128, 128, 128, 0.12);
        border: 1px solid rgba(128, 128, 128, 0.35);
        font-size: 0.78rem;
        white-space: nowrap;
    }
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00ff88;
        box-shadow: 0 0 8px #00ff88;
        flex-shrink: 0;
    }
    .status-label {
        opacity: 0.65;
        letter-spacing: 0.06em;
        font-weight: 500;
    }
    .status-value {
        font-weight: 700;
        letter-spacing: 0.04em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Search bar + display-mode toggle styles (kept here so they always load).
st.markdown(
    """
    <style>
    /* ---------- LOCATION SEARCH BAR ---------- */
    .st-key-location_section [data-testid="stForm"] {
        border: none !important;
        padding: 0 !important;
        background: transparent !important;
    }

    .st-key-location_section [data-testid="stTextInput"] label p {
        color: #FFE1E3 !important;
        font-weight: 600 !important;
        letter-spacing: 0.04em;
    }

    .st-key-location_section [data-testid="stTextInput"] [data-baseweb="input"],
    .st-key-location_section [data-testid="stTextInput"] [data-baseweb="base-input"] {
        background: #FFF1F2 !important;
        border-radius: 10px !important;
    }

    .st-key-location_section [data-testid="stTextInput"] [data-baseweb="input"] {
        border: 2px solid #FF5A63 !important;
        box-shadow: 0 0 14px rgba(255, 90, 99, 0.35);
        transition: box-shadow 0.2s ease, border-color 0.2s ease;
    }

    .st-key-location_section [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        border-color: #FF2D3A !important;
        box-shadow: 0 0 0 3px rgba(255, 90, 99, 0.35),
                    0 0 18px rgba(255, 90, 99, 0.55);
    }

    .st-key-location_section [data-testid="stTextInput"] input {
        background: #FFF1F2 !important;
        color: #3A0D12 !important;
        -webkit-text-fill-color: #3A0D12 !important;
        font-weight: 600 !important;
    }

    .st-key-location_section [data-testid="stTextInput"] input::placeholder {
        color: #B5656B !important;
        -webkit-text-fill-color: #B5656B !important;
        opacity: 1 !important;
    }

    .st-key-location_section [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(145deg, #FF4A55, #D9232D) !important;
        color: #FFFFFF !important;
        border: 1px solid #FF8A91 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 0.05em;
        box-shadow: 0 4px 14px rgba(217, 35, 45, 0.45);
        transition: transform 0.15s ease, box-shadow 0.2s ease;
    }

    .st-key-location_section [data-testid="stFormSubmitButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 6px 18px rgba(255, 74, 85, 0.65);
    }

    /* ---------- READABLE TEXT INSIDE THE COLORED SECTIONS ---------- */
    /* Forces light text so it works on both light and dark app themes */
    .st-key-location_section [data-testid="stMarkdownContainer"] p,
    .st-key-weather_section  [data-testid="stMarkdownContainer"] p,
    .st-key-car_section      [data-testid="stMarkdownContainer"] p,
    .st-key-location_section [data-testid="stCaptionContainer"],
    .st-key-weather_section  [data-testid="stCaptionContainer"],
    .st-key-car_section      [data-testid="stCaptionContainer"],
    .st-key-location_section [data-testid="stCaptionContainer"] p,
    .st-key-weather_section  [data-testid="stCaptionContainer"] p,
    .st-key-car_section      [data-testid="stCaptionContainer"] p,
    .st-key-location_section [data-testid="stWidgetLabel"] p,
    .st-key-weather_section  [data-testid="stWidgetLabel"] p,
    .st-key-car_section      [data-testid="stWidgetLabel"] p,
    .st-key-location_section [data-testid="stRadioOption"] p,
    .st-key-location_section label p {
        color: #F6EAEB !important;
    }

    .st-key-location_section hr,
    .st-key-weather_section hr,
    .st-key-car_section hr {
        border-color: rgba(255, 255, 255, 0.25) !important;
    }

    /* ---------- DEFAULT / ADVANCED TOGGLE SWITCH ---------- */
    /* Dark track so the text is readable on light AND dark themes */
    .st-key-mode_switch {
        position: relative;
        display: flex !important;
        flex-direction: row !important;
        gap: 0 !important;
        width: 320px;
        max-width: 100%;
        margin: 0.5rem auto 1rem auto;
        padding: 4px;
        border-radius: 999px;
        background: linear-gradient(145deg, #2A1215, #1B0C0F);
        border: 1px solid rgba(255, 90, 99, 0.50);
        box-shadow:
            inset 0 2px 8px rgba(0, 0, 0, 0.55),
            0 4px 14px rgba(0, 0, 0, 0.25);
    }

    /* the sliding knob (Default position) */
    .st-key-mode_switch::before {
        content: "";
        position: absolute;
        top: 4px;
        bottom: 4px;
        left: 4px;
        width: calc((100% - 8px) / 2);
        border-radius: 999px;
        background: linear-gradient(135deg, #FF4A55, #D9232D);
        box-shadow:
            0 0 16px rgba(255, 74, 85, 0.60),
            inset 0 1px 0 rgba(255, 255, 255, 0.35);
        transition:
            transform 0.30s cubic-bezier(0.4, 0, 0.2, 1),
            background 0.30s ease,
            box-shadow 0.30s ease;
    }

    .st-key-mode_switch > div {
        flex: 1 1 0 !important;
        width: auto !important;
        position: relative;
        z-index: 1;
    }

    .st-key-mode_switch [data-testid="stButton"],
    .st-key-mode_switch [data-testid="stButton"] button {
        width: 100% !important;
    }

    .st-key-mode_switch button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 999px !important;
        min-height: 0 !important;
        padding: 8px 0 !important;
    }

    .st-key-mode_switch button p {
        margin: 0;
        text-transform: uppercase;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.10em;
        color: rgba(255, 255, 255, 0.60) !important;
        transition: color 0.25s ease;
    }

    .st-key-mode_switch button:hover p {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONFIGURATION
# ============================================================

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

DEFAULT_LAT = 18.2013
DEFAULT_LON = -67.1452

REFRESH_SECONDS = 300  # 5 minutes


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
# WEATHER AND LOCATION FUNCTIONS
# ============================================================

def calculate_air_density(temperature_c, pressure_hpa):
    """Calculate dry-air density in kg/m³ using the ideal gas law."""

    temperature_k = temperature_c + 273.15
    pressure_pa = pressure_hpa * 100

    return pressure_pa / (287.05 * temperature_k)


def search_location(query):
    """Convert a city or location name into coordinates."""

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
        "name": ", ".join(
            dict.fromkeys(p for p in parts if p)
        ),
    }


@st.cache_data(ttl=REFRESH_SECONDS - 5, show_spinner=False)
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
        "air_density": calculate_air_density(
            temperature,
            pressure,
        ),
        "time": current["time"],
    }

    forecast = pd.DataFrame(data["hourly"])
    forecast["time"] = pd.to_datetime(forecast["time"])

    return current_weather, forecast


def wind_direction_label(degrees):
    """Convert compass degrees into a readable direction."""

    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW",
    ]

    return directions[round(degrees / 22.5) % 16]


# ============================================================
# AUTO-REFRESH AND WEATHER REQUEST
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

except (
    requests.RequestException,
    KeyError,
    ValueError,
) as exc:

    weather_data = None
    forecast_data = pd.DataFrame()

    st.session_state.weather_connected = False
    st.session_state.weather_error = str(exc)


# ============================================================
# DASHBOARD HEADER
# ============================================================

weather_connected = st.session_state.weather_connected

weather_status = "Connected" if weather_connected else "Disconnected"
status_color = "#00ff88" if weather_connected else "#ff6464"

refresh_label = (
    f"{REFRESH_SECONDS // 60} MIN"
    if REFRESH_SECONDS % 60 == 0
    else f"{REFRESH_SECONDS} SEC"
)

# IMPORTANT: build the HTML as one compact string.
# Markdown treats lines indented 4+ spaces (and blank lines inside
# HTML blocks) as code, which makes the raw HTML show up as text.
status_html = (
    '<div class="status-strip">'

    '<div class="status-item">'
    '<span class="status-dot"></span>'
    '<span class="status-label">SYSTEM</span>'
    '<span class="status-value">ONLINE</span>'
    '</div>'

    '<div class="status-item">'
    f'<span class="status-dot" style="background:{status_color};'
    f'box-shadow:0 0 8px {status_color};"></span>'
    '<span class="status-label">OPEN-METEO</span>'
    f'<span class="status-value">{weather_status}</span>'
    '</div>'

    '<div class="status-item">'
    '<span class="status-label">AUTO-REFRESH</span>'
    f'<span class="status-value">{refresh_label}</span>'
    '</div>'

    '<div class="status-item">'
    '<span class="status-label">SOURCE</span>'
    '<span class="status-value">LIVE / MOCK</span>'
    '</div>'

    '</div>'
)

# Status strip: centered, above the title
st.markdown(status_html, unsafe_allow_html=True)

# Logo on the left, dashboard title to its right
logo_col, header_col = st.columns(
    [1.3, 5],
    vertical_alignment="center",
)

with logo_col:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), use_container_width=True)

with header_col:
    st.title("Solar Car Team Dashboard")


# ============================================================
# GLOBAL DISPLAY MODE
# ============================================================

if "display_mode" not in st.session_state:
    st.session_state.display_mode = "Default"


def set_display_mode(mode):
    st.session_state.display_mode = mode


# Two buttons styled as a sliding toggle switch (CSS key: mode_switch).
with st.container(key="mode_switch"):
    st.button(
        "Default",
        key="mode_default",
        on_click=set_display_mode,
        args=("Default",),
    )
    st.button(
        "Advanced",
        key="mode_advanced",
        on_click=set_display_mode,
        args=("Advanced",),
    )

display_mode = st.session_state.display_mode

# Move the knob and highlight the active label
if display_mode == "Advanced":
    st.markdown(
        """
        <style>
        .st-key-mode_switch::before {
            transform: translateX(100%);
            background: linear-gradient(135deg, #3FD8EE, #1D93AB);
            box-shadow:
                0 0 16px rgba(63, 216, 238, 0.60),
                inset 0 1px 0 rgba(255, 255, 255, 0.35);
        }
        .st-key-mode_advanced button p { color: #FFFFFF !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <style>
        .st-key-mode_default button p { color: #FFFFFF !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOCATION & DATA CONTROLS
# ============================================================

with st.container(border=True, key="location_section"):

    st.subheader("Location & Data Controls")

    # --------------------------------------------------------
    # LOCATION SOURCE
    # --------------------------------------------------------

    if display_mode == "Advanced":

        location_mode = st.radio(
            "Location source",
            ["Search location", "Precise location"],
            horizontal=True,
            key="location_mode",
        )

    else:

        location_mode = "Search location"

    # --------------------------------------------------------
    # LOCATION SEARCH
    # --------------------------------------------------------

    with st.form("location_search_form"):

        search_col, button_col = st.columns(
            [5, 1],
            vertical_alignment="bottom",
        )

        with search_col:

            search_text = st.text_input(
                "City / location",
                key="search_text",
                placeholder="e.g. Fajardo, Puerto Rico",
            )

        with button_col:

            search_clicked = st.form_submit_button(
                "Search",
                use_container_width=True,
            )

    # --------------------------------------------------------
    # SEARCH PROCESSING
    # --------------------------------------------------------

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

                    st.error(
                        "Location not found. Try another search."
                    )

            except requests.RequestException as exc:

                st.error(f"Location search failed: {exc}")

    # --------------------------------------------------------
    # PRECISE BROWSER LOCATION
    # ADVANCED MODE ONLY
    # --------------------------------------------------------

    if (
        display_mode == "Advanced"
        and location_mode == "Precise location"
    ):

        st.caption(
            "Allow location access in your browser when prompted."
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

                    st.session_state.location_name = (
                        "Precise browser location"
                    )

                    get_weather.clear()
                    st.rerun()

        except Exception:

            st.info(
                "Browser location is unavailable. "
                "You can still search for a location."
            )

    # --------------------------------------------------------
    # ADVANCED MODE: INTERACTIVE MAP + LOCATION INFORMATION
    # --------------------------------------------------------

    if display_mode == "Advanced":

        st.divider()

        map_col, info_col = st.columns(
            [2.2, 1],
            gap="large",
        )

        with map_col:

            st.markdown("**Location Map**")

            map_data = pd.DataFrame({
                "latitude": [st.session_state.latitude],
                "longitude": [st.session_state.longitude],
            })

            st.map(
                map_data,
                zoom=11,
                use_container_width=True,
            )

            st.caption(
                "Drag the map to pan and use the map controls to zoom."
            )

        with info_col:

            st.markdown("**Active Location**")

            st.metric(
                "Location",
                st.session_state.location_name,
            )

            st.metric(
                "Latitude",
                f"{st.session_state.latitude:.5f}",
            )

            st.metric(
                "Longitude",
                f"{st.session_state.longitude:.5f}",
            )

    # --------------------------------------------------------
    # DEFAULT MODE: COMPACT LOCATION INFORMATION
    # --------------------------------------------------------

    else:

        st.divider()

        info_col1, info_col2, info_col3 = st.columns(3)

        info_col1.metric(
            "Location",
            st.session_state.location_name,
        )

        info_col2.metric(
            "Latitude",
            f"{st.session_state.latitude:.5f}",
        )

        info_col3.metric(
            "Longitude",
            f"{st.session_state.longitude:.5f}",
        )


# ============================================================
# WEATHER CONNECTION WARNING
# ============================================================

if not st.session_state.weather_connected:

    st.warning(
        "Weather data could not be retrieved. "
        "Check your internet connection. "
        "The dashboard will retry automatically."
    )


# ============================================================
# MAIN DASHBOARD TABS
# ============================================================

tab_predictions, tab_live = st.tabs(
    [
        "EMS Predictions (Theoretical)",
        "Live Telemetry",
    ]
)


# ============================================================
# EMS PREDICTIONS
# ============================================================

with tab_predictions:

    if weather_data is None:

        st.info(
            "Weather data is unavailable. "
            "The dashboard will retry automatically."
        )

    else:

        weather_col, car_col = st.columns(
            2,
            gap="large",
        )

        # ====================================================
        # CURRENT WEATHER
        # ====================================================

        with weather_col:

            with st.container(border=True, key="weather_section"):

                st.subheader("Current Weather")

                # Main weather measurements

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
                    (
                        f"{wind_direction_label(weather_data['wind_direction'])} "
                        f"({weather_data['wind_direction']:.0f}°)"
                    ),
                )

                st.caption("Cloud cover")

                st.progress(
                    max(
                        0.0,
                        min(
                            1.0,
                            weather_data["cloud_cover"] / 100,
                        ),
                    )
                )

                # ------------------------------------------------
                # ADVANCED WEATHER
                # ------------------------------------------------

                if display_mode == "Advanced":

                    st.divider()

                    st.markdown(
                        "**Advanced Weather Measurements**"
                    )

                    a1, a2 = st.columns(2)

                    a1.metric(
                        "Relative Humidity",
                        f"{weather_data['humidity']} %",
                    )

                    a2.metric(
                        "Surface Pressure",
                        f"{weather_data['pressure']:.1f} hPa",
                    )

                    a3, a4 = st.columns(2)

                    a3.metric(
                        "Precipitation",
                        f"{weather_data['precipitation']} mm",
                    )

                    a4.metric(
                        "Air Density",
                        f"{weather_data['air_density']:.4f} kg/m³",
                    )

                    st.caption(
                        "Air density is calculated using temperature "
                        "and surface pressure through the ideal gas law."
                    )

                    # ------------------------------------------------
                    # TEMPERATURE FORECAST
                    # ------------------------------------------------

                    st.divider()

                    st.markdown("**Forecast Analytics**")

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

                    # ------------------------------------------------
                    # SOLAR RADIATION FORECAST
                    # ------------------------------------------------

                    solar_chart = px.line(
                        forecast_data,
                        x="time",
                        y="shortwave_radiation",
                        title="Solar Radiation Forecast",
                        labels={
                            "time": "Time",
                            "shortwave_radiation": (
                                "Solar radiation (W/m²)"
                            ),
                        },
                    )

                    st.plotly_chart(
                        solar_chart,
                        use_container_width=True,
                    )

                    # ------------------------------------------------
                    # FORECAST DATA STREAM
                    # ------------------------------------------------

                    st.markdown("**Forecast Data Stream**")

                    st.dataframe(
                        forecast_data,
                        use_container_width=True,
                        hide_index=True,
                    )

                    st.caption(
                        "Forecast values are hourly API data, not vehicle "
                        "measurements. Shortwave radiation is a solar "
                        "radiation indicator, not identical to "
                        "panel-plane irradiance."
                    )

        # ====================================================
        # CAR DATA
        # ====================================================

        with car_col:

            with st.container(border=True, key="car_section"):

                st.subheader("Car Data")

                st.caption(
                    "Mock telemetry — replace with the actual "
                    "vehicle data feed."
                )

                # Main car measurements

                c1, c2 = st.columns(2)

                c1.metric(
                    "Current Speed",
                    f"{car_data['speed']:.1f} km/h",
                )

                c2.metric(
                    "State of Charge",
                    f"{car_data['soc']:.0f} %",
                )

                st.caption("Battery state of charge")

                st.progress(
                    max(
                        0.0,
                        min(
                            1.0,
                            car_data["soc"] / 100,
                        ),
                    )
                )

                st.metric(
                    "Vehicle Location",
                    (
                        f"{car_data['latitude']:.4f}, "
                        f"{car_data['longitude']:.4f}"
                    ),
                )

                # ------------------------------------------------
                # ADVANCED CAR MEASUREMENTS
                # ------------------------------------------------

                if display_mode == "Advanced":

                    st.divider()

                    st.markdown(
                        "**Advanced Vehicle Measurements**"
                    )

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
                        "Negative battery current represents discharge "
                        "in this demo's convention. Verify this convention "
                        "with the actual telemetry source."
                    )


# ============================================================
# LIVE TELEMETRY TAB
# ============================================================

with tab_live:

    st.subheader("Live Telemetry")

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