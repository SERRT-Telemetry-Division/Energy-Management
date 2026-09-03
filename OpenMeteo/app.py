from datetime import datetime, timedelta, timezone

import pandas as pd
import streamlit as st

from weather import fetch_weather, search_location


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="SERRT Energy Management",
    page_icon="⚡",
    layout="wide"
)


# --------------------------------------------------
# SESSION STATE DEFAULTS
# --------------------------------------------------

if "latitude" not in st.session_state:
    st.session_state.latitude = 18.21

if "longitude" not in st.session_state:
    st.session_state.longitude = -67.14

if "resolved_location" not in st.session_state:
    st.session_state.resolved_location = "Mayagüez, Puerto Rico"


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                #062a33 0%,
                #03171d 25%,
                #02090d 60%,
                #000000 100%
            );
        color: #dffcff;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #03171d 0%,
            #020d11 100%
        );

        border-right: 1px solid #00eaff;
    }

    [data-testid="stSidebar"] * {
        color: #dffcff;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;

        color: #00f5ff;

        letter-spacing: 2px;

        margin-bottom: 0;

        text-shadow:
            0 0 5px #00f5ff,
            0 0 15px rgba(0, 245, 255, 0.35);
    }

    .subtitle {
        color: #79e9f0;

        font-size: 14px;

        letter-spacing: 3px;

        margin-top: 4px;
        margin-bottom: 25px;
    }

    .system-status {
        display: inline-block;

        color: #68ff9d;

        border: 1px solid #2dff7a;

        background:
            rgba(0, 255, 100, 0.06);

        padding: 6px 12px;

        border-radius: 4px;

        font-size: 12px;

        letter-spacing: 1px;

        margin-bottom: 20px;

        box-shadow:
            0 0 10px rgba(0, 255, 100, 0.15);
    }

    .update-info {
        color: #61dce5;

        font-size: 12px;

        letter-spacing: 1px;

        margin-top: 5px;
        margin-bottom: 15px;
    }

    .location-box {
        background:
            rgba(0, 238, 255, 0.04);

        border:
            1px solid rgba(0, 234, 255, 0.35);

        border-radius: 6px;

        padding: 12px;

        margin-top: 10px;
        margin-bottom: 10px;
    }

    .location-name {
        color: #00eaff;

        font-size: 13px;

        font-weight: 700;

        letter-spacing: 1px;
    }

    .location-coordinates {
        color: #b7faff;

        font-size: 12px;

        margin-top: 4px;
    }

    .metric-card {
        background:
            linear-gradient(
                145deg,
                rgba(2, 30, 38, 0.95),
                rgba(2, 13, 17, 0.95)
            );

        border: 1px solid #00ddeb;

        border-radius: 8px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
            inset 0 0 20px rgba(0, 238, 255, 0.04),
            0 0 12px rgba(0, 238, 255, 0.10);
    }

    .metric-label {
        color: #63eaf3;

        font-size: 12px;

        font-weight: 700;

        letter-spacing: 1.5px;

        text-transform: uppercase;

        margin-bottom: 14px;
    }

    .metric-value {
        color: #efffff;

        font-size: 30px;

        font-weight: 700;

        margin-top: 8px;
    }

    .metric-unit {
        color: #00eaff;

        font-size: 15px;
    }

    .solar-value {
        color: #ffdf3a;

        text-shadow:
            0 0 10px rgba(255, 223, 58, 0.35);
    }

    .section-title {
        color: #00eaff;

        font-size: 18px;

        font-weight: 700;

        letter-spacing: 1.5px;

        text-transform: uppercase;

        border-left: 3px solid #00eaff;

        padding-left: 10px;

        margin-top: 25px;

        margin-bottom: 15px;
    }

    .stNumberInput input {
        background-color: #04181e;

        color: #dffcff;

        border: 1px solid #00b8c7;
    }

    .stTextInput input {
        background-color: #04181e;

        color: #dffcff;

        border: 1px solid #00b8c7;
    }

    .stButton > button {
        width: 100%;

        background:
            linear-gradient(
                90deg,
                #003f49,
                #006777
            );

        color: #ffffff;

        border: 1px solid #00eaff;

        border-radius: 5px;

        font-weight: 700;

        letter-spacing: 1px;

        transition: 0.2s;
    }

    .stButton > button:hover {
        background: #00cddd;

        color: #001014;

        border-color: #6affff;

        box-shadow:
            0 0 15px rgba(0, 238, 255, 0.4);
    }

    [data-testid="stDataFrame"] {
        border:
            1px solid rgba(0, 234, 255, 0.30);

        border-radius: 6px;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.html(
    """
    <div class="main-title">
        SERRT ENERGY MANAGEMENT
    </div>

    <div class="subtitle">
        WEATHER TELEMETRY SYSTEM // OPEN-METEO DATA LINK
    </div>

    <div class="system-status">
        ● SYSTEM ONLINE
        &nbsp;&nbsp; | &nbsp;&nbsp;
        AUTO REFRESH: 15 MIN
    </div>
    """
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("## ⚡ CONTROL PANEL")

    st.markdown("### LOCATION MODE")

    location_mode = st.radio(
        "Select location input method",
        [
            "Search by location",
            "Precise coordinates"
        ],
        label_visibility="collapsed"
    )

    st.divider()


    # --------------------------------------------------
    # SEARCH BY LOCATION MODE
    # --------------------------------------------------

    if location_mode == "Search by location":

        st.markdown("### LOCATION SEARCH")

        location_name = st.text_input(
            "City / Location",
            value=st.session_state.resolved_location,
            placeholder="Example: Mayagüez, Puerto Rico"
        )

        search_button = st.button(
            "⌖ SEARCH LOCATION",
            width="stretch"
        )

        if search_button:

            try:

                result = search_location(
                    location_name
                )

                if result:

                    st.session_state.latitude = (
                        result["latitude"]
                    )

                    st.session_state.longitude = (
                        result["longitude"]
                    )

                    resolved_name = result.get(
                        "name"
                    )

                    resolved_admin = result.get(
                        "admin1"
                    )

                    resolved_country = result.get(
                        "country"
                    )

                    location_parts = []

                    if resolved_name:
                        location_parts.append(
                            resolved_name
                        )

                    if resolved_admin:
                        location_parts.append(
                            resolved_admin
                        )

                    if resolved_country:
                        location_parts.append(
                            resolved_country
                        )

                    st.session_state.resolved_location = (
                        ", ".join(location_parts)
                    )

                    st.success(
                        "Location found successfully."
                    )

                else:

                    st.error(
                        "Location not found."
                    )

            except Exception as error:

                st.error(
                    f"Location search failed: {error}"
                )


        latitude = (
            st.session_state.latitude
        )

        longitude = (
            st.session_state.longitude
        )


        st.html(
            f"""
            <div class="location-box">

                <div class="location-name">
                    ⌖ {st.session_state.resolved_location}
                </div>

                <div class="location-coordinates">
                    LAT: {latitude:.6f}
                    <br>
                    LON: {longitude:.6f}
                </div>

            </div>
            """
        )


    # --------------------------------------------------
    # PRECISE COORDINATES MODE
    # --------------------------------------------------

    else:

        st.markdown(
            "### PRECISE COORDINATES"
        )

        latitude = st.number_input(
            "Latitude",
            min_value=-90.0,
            max_value=90.0,
            value=float(
                st.session_state.latitude
            ),
            format="%.6f"
        )

        longitude = st.number_input(
            "Longitude",
            min_value=-180.0,
            max_value=180.0,
            value=float(
                st.session_state.longitude
            ),
            format="%.6f"
        )

        st.session_state.latitude = latitude
        st.session_state.longitude = longitude


        st.html(
            f"""
            <div class="location-box">

                <div class="location-name">
                    ⌖ PRECISE GPS POSITION
                </div>

                <div class="location-coordinates">
                    LAT: {latitude:.6f}
                    <br>
                    LON: {longitude:.6f}
                </div>

            </div>
            """
        )


    # --------------------------------------------------
    # MANUAL REFRESH
    # --------------------------------------------------

    st.divider()

    refresh_now = st.button(
        "↻ REFRESH NOW",
        width="stretch"
    )


    # --------------------------------------------------
    # SYSTEM INFO
    # --------------------------------------------------

    st.divider()

    st.markdown("### SYSTEM INFO")

    st.markdown(
        """
        **Data Source**  
        Open-Meteo API

        **Forecast Type**  
        Hourly

        **Auto Refresh**  
        Every 15 minutes

        **Processing**  
        Pandas DataFrame

        **System**  
        SERRT Energy Management
        """
    )


# --------------------------------------------------
# WEATHER DASHBOARD
# --------------------------------------------------

@st.fragment(
    run_every="15m"
)
def weather_dashboard(
    latitude,
    longitude
):

    try:

        with st.spinner(
            "Receiving weather telemetry..."
        ):

            # ------------------------------------------
            # FETCH WEATHER
            # ------------------------------------------

            weather_df = fetch_weather(
                latitude,
                longitude
            )

            weather_df["time"] = (
                pd.to_datetime(
                    weather_df["time"]
                )
            )


            # ------------------------------------------
            # LOCAL TIME
            # ------------------------------------------

            utc_offset_seconds = (
                weather_df.attrs.get(
                    "utc_offset_seconds",
                    0
                )
            )

            local_timezone = timezone(
                timedelta(
                    seconds=utc_offset_seconds
                )
            )

            current_local_time = (
                datetime.now(
                    timezone.utc
                )
                .astimezone(
                    local_timezone
                )
            )

            current_local_time_naive = (
                current_local_time.replace(
                    tzinfo=None
                )
            )


            # ------------------------------------------
            # FIND CLOSEST FORECAST HOUR
            # ------------------------------------------

            time_difference = (
                weather_df["time"]
                - current_local_time_naive
            ).abs()

            closest_index = (
                time_difference.idxmin()
            )

            current = weather_df.loc[
                closest_index
            ]


            # ------------------------------------------
            # UPDATE TIMES
            # ------------------------------------------

            last_update = (
                current_local_time.strftime(
                    "%I:%M:%S %p"
                )
            )

            next_update_time = (
                current_local_time
                + timedelta(minutes=15)
            )

            next_update = (
                next_update_time.strftime(
                    "%I:%M %p"
                )
            )

            forecast_hour = (
                current["time"].strftime(
                    "%I:%M %p"
                )
            )


        # ----------------------------------------------
        # STATUS
        # ----------------------------------------------

        st.success(
            "Telemetry data received successfully."
        )

        st.html(
            f"""
            <div class="update-info">

                ● OPEN-METEO CONNECTED

                &nbsp;&nbsp; // &nbsp;&nbsp;

                LAST UPDATE:
                {last_update}

                &nbsp;&nbsp; // &nbsp;&nbsp;

                NEXT UPDATE:
                ~{next_update}

                &nbsp;&nbsp; // &nbsp;&nbsp;

                FORECAST HOUR:
                {forecast_hour}

            </div>
            """
        )


        # ----------------------------------------------
        # CURRENT LOCATION
        # ----------------------------------------------

        st.html(
            f"""
            <div class="update-info">

                ⌖ ACTIVE POSITION:

                {latitude:.6f},
                {longitude:.6f}

            </div>
            """
        )


        # ----------------------------------------------
        # LIVE WEATHER TELEMETRY
        # ----------------------------------------------

        st.html(
            """
            <div class="section-title">
                LIVE WEATHER TELEMETRY
            </div>
            """
        )

        col1, col2, col3, col4 = (
            st.columns(4)
        )


        with col1:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        🌡 TEMPERATURE
                    </div>

                    <div class="metric-value">

                        {current["temperature_2m"]}

                        <span class="metric-unit">
                            °C
                        </span>

                    </div>

                </div>
                """
            )


        with col2:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        💧 HUMIDITY
                    </div>

                    <div class="metric-value">

                        {current["relative_humidity_2m"]}

                        <span class="metric-unit">
                            %
                        </span>

                    </div>

                </div>
                """
            )


        with col3:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        💨 WIND SPEED
                    </div>

                    <div class="metric-value">

                        {current["wind_speed_10m"]}

                        <span class="metric-unit">
                            km/h
                        </span>

                    </div>

                </div>
                """
            )


        with col4:

            st.html(
                f"""
                <div class="metric-card">

                    <div class="metric-label">
                        ☀ SOLAR RADIATION
                    </div>

                    <div class="metric-value solar-value">

                        {current["shortwave_radiation"]}

                        <span class="metric-unit">
                            W/m²
                        </span>

                    </div>

                </div>
                """
            )


        # ----------------------------------------------
        # ENVIRONMENTAL CONDITIONS
        # ----------------------------------------------

        st.html(
            """
            <div class="section-title">
                ENVIRONMENTAL CONDITIONS
            </div>
            """
        )

        detail1, detail2, detail3 = (
            st.columns(3)
        )

        detail1.metric(
            "Cloud Cover",
            f'{current["cloud_cover"]} %'
        )

        detail2.metric(
            "Precipitation",
            f'{current["precipitation"]} mm'
        )

        detail3.metric(
            "Wind Direction",
            f'{current["wind_direction_10m"]}°'
        )


        # ----------------------------------------------
        # FORECAST ANALYTICS
        # ----------------------------------------------

        st.html(
            """
            <div class="section-title">
                FORECAST ANALYTICS
            </div>
            """
        )

        chart1, chart2 = (
            st.columns(2)
        )


        with chart1:

            st.markdown(
                "#### TEMPERATURE FORECAST"
            )

            st.line_chart(
                weather_df,
                x="time",
                y="temperature_2m"
            )


        with chart2:

            st.markdown(
                "#### SOLAR RADIATION FORECAST"
            )

            st.line_chart(
                weather_df,
                x="time",
                y="shortwave_radiation"
            )


        # ----------------------------------------------
        # FORECAST TABLE
        # ----------------------------------------------

        st.html(
            """
            <div class="section-title">
                FORECAST DATA STREAM
            </div>
            """
        )

        display_df = (
            weather_df.rename(
                columns={
                    "time":
                        "Time",

                    "temperature_2m":
                        "Temperature (°C)",

                    "relative_humidity_2m":
                        "Humidity (%)",

                    "wind_speed_10m":
                        "Wind Speed (km/h)",

                    "wind_direction_10m":
                        "Wind Direction (°)",

                    "cloud_cover":
                        "Cloud Cover (%)",

                    "precipitation":
                        "Precipitation (mm)",

                    "shortwave_radiation":
                        "Solar Radiation (W/m²)"
                }
            )
        )

        st.dataframe(
            display_df,
            width="stretch",
            hide_index=True
        )


    except Exception as error:

        st.error(
            "WEATHER DATA LINK FAILURE"
        )

        st.error(
            f"Unable to retrieve telemetry data: "
            f"{error}"
        )


# --------------------------------------------------
# RUN DASHBOARD
# --------------------------------------------------

weather_dashboard(
    latitude,
    longitude
)