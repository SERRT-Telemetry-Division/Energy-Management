"""
SIMPLE DEMO FOR THE PIT CREW DISPLAY

"""

import pandas as pd
import streamlit as st

connected = True             # Boolean to confirm car connection to pits

st.set_page_config(page_title="Solar Car Dashboard", page_icon="☀️", layout="wide")

# ----------------------------------------------------------------------
# MOCK DATA (replace these variables with live data later)
# ----------------------------------------------------------------------
weather_data = {
    "ghi": 845,              # Global Horizontal Irradiance (W/m²)
    "cloudiness": 20,        # %
    "temperature": 31.5,     # °C
    "rain_chance": 10,       # %
}

car_data = {
    "speed": 78,             # km/h
    "inclination": 2.4,      # degrees (+ uphill, - downhill)
    "soc": 72,               # state of charge, %
    "battery_voltage": 128.6,  # V
    "battery_current": -34.2,  # A (negative = discharging)
    "latitude": -23.6980,
    "longitude": 133.8807,
}

# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
st.title("☀️ Solar Car Team Dashboard")

tab_live, tab_predictions, = st.tabs(["Live Telemetry", "EMS Predictions"])

with tab_live:
    weather_col, car_col = st.columns(2, gap="large")

    # ---------------- Weather ----------------
    with weather_col:
        st.subheader("🌤️ Current Weather")
        w1, w2 = st.columns(2)
        w1.metric("GHI", f"{weather_data['ghi']} W/m²")
        w2.metric("Cloudiness", f"{weather_data['cloudiness']} %")
        w3, w4 = st.columns(2)
        w3.metric("Temperature", f"{weather_data['temperature']} °C")
        w4.metric("Chance of Rain", f"{weather_data['rain_chance']} %")

        st.caption("Cloud cover")
        st.progress(weather_data["cloudiness"] / 100)
        st.caption("Rain probability")
        st.progress(weather_data["rain_chance"] / 100)

    # ---------------- Car ----------------
    with car_col:
        st.subheader("🏎️ Car Data")
        if connected:
            c1, c2 = st.columns(2)
            c1.metric("Current Speed", f"{car_data['speed']} km/h")
            c2.metric("Inclination", f"{car_data['inclination']}°")
            c3, c4 = st.columns(2)
            c3.metric("State of Charge", f"{car_data['soc']} %")
            c4.metric("Battery Voltage", f"{car_data['battery_voltage']} V")
            c5, c6 = st.columns(2)
            c5.metric("Battery Current", f"{car_data['battery_current']} A")
            c6.metric(
                "GPS Location",
                f"{car_data['latitude']:.4f}, {car_data['longitude']:.4f}",
            )

            st.caption("State of charge")
            st.progress(car_data["soc"] / 100)

            # st.map(
            #     pd.DataFrame(
            #         {"lat": [car_data["latitude"]], "lon": [car_data["longitude"]]}
            #     ),
            #     zoom=8,
            # )
        else:
            st.subheader("Waiting for Connection...")

with tab_predictions:
    st.subheader("Coming Soon")