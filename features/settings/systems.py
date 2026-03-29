import streamlit as st
import json
import os

# =========================
# BASE PATH (ROOT PROJECT)
# =========================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOCATION_FILE = os.path.join(ROOT_DIR, "config", "ptg_location.json")

# =========================
# CONSTANT DATA
# =========================
AREAS = [
    "Pertamina Gas Operation North Sumatera",
    "Pertamina Gas Operation Central Sumatera",
    "Pertamina Gas Operation South Sumatera",
    "Pertamina Gas Operation Rokan",
    "Pertamina Gas Operation West Java",
    "Pertamina Gas Operation East Java",
    "Pertamina Gas Operation Kalimantan",
    "Pertamina Arun Gas",
    "PERTASAMTAN"
]

# =========================
# LOAD LOCATION
# =========================
def load_location():
    try:
        if os.path.exists(LOCATION_FILE):
            with open(LOCATION_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Gagal load config: {e}")
    return {}

# =========================
# SAVE LOCATION
# =========================
def save_location(data):
    try:
        os.makedirs(ROOT_DIR, exist_ok=True)

        with open(LOCATION_FILE, "w") as f:
            json.dump(data, f, indent=4)

    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# =========================
# MAIN UI
# =========================
def render_system_settings():

    st.title("⚙️ System Settings")

    data = load_location()

    default_area = data.get("area", AREAS[0])
    default_station = data.get("station", "")
    default_lat = data.get("lat", "")
    default_lon = data.get("lon", "")

    with st.form("system_form"):

        st.subheader("📍 Location Configuration")

        area = st.selectbox(
            "Area",
            AREAS,
            index=AREAS.index(default_area) if default_area in AREAS else 0
        )

        station = st.text_input("Station", value=default_station)

        lat = st.text_input("Latitude", value=str(default_lat))
        lon = st.text_input("Longitude", value=str(default_lon))

        submitted = st.form_submit_button("💾 Save")

        if submitted:

            try:
                lat_val = float(lat)
                lon_val = float(lon)
            except:
                st.error("Latitude dan Longitude harus berupa angka!")
                return

            if not station.strip():
                st.error("Station tidak boleh kosong!")
                return

            payload = {
                "area": area,
                "station": station.strip(),
                "lat": lat_val,
                "lon": lon_val
            }

            save_location(payload)

            st.success("✅ Setting berhasil disimpan!")
            st.json(payload)

# =========================
# DEBUG
# =========================
if __name__ == "__main__":
    render_system_settings()