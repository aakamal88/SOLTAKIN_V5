import streamlit as st
from .location_utils import load_json, save_json, FILE_LOCATION, AREAS

def render_location():
    loc = load_json(FILE_LOCATION, {
        "area": AREAS[0],
        "station": "",
        "lat": 0,
        "lon": 0
    })

    st.subheader("📍 Location Configuration")

    area = st.selectbox("Area", AREAS, index=AREAS.index(loc["area"]), key="loc_area")
    station = st.text_input("Station", value=loc["station"], key="loc_station")
    lat = st.text_input("Latitude", value=str(loc["lat"]), key="loc_lat")
    lon = st.text_input("Longitude", value=str(loc["lon"]), key="loc_lon")

    if st.button("💾 Save Location"):
        save_json(FILE_LOCATION, {
            "area": area,
            "station": station,
            "lat": float(lat),
            "lon": float(lon)
        })