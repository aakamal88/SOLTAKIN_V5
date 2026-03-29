import streamlit as st
import json
import os
import base64
import requests
import certifi

# =========================
# BASE PATH (ROOT PROJECT)
# =========================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
LOCATION_FILE = os.path.join(ROOT_DIR, "config", "ptg_location.json")

# =========================
# GITHUB CONFIG
# =========================
GITHUB_TOKEN = st.secrets.get("GITHUB_TOKEN", "")
GITHUB_REPO = "aakamal88/SOLTAKIN_V5"
GITHUB_FILE_PATH = "config/ptg_location.json"

GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"

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
# GITHUB LOAD
# =========================
def load_from_github():
    try:
        if not GITHUB_TOKEN:
            return {}

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        session = requests.Session()
        session.trust_env = False

        res = session.get(
            GITHUB_API_URL,
            headers=headers,
            verify=certifi.where(),
            timeout=10
        )

        if res.status_code == 200:
            content = res.json()["content"]
            decoded = base64.b64decode(content).decode("utf-8")
            return json.loads(decoded)

    except Exception as e:
        st.warning(f"Gagal load dari GitHub: {e}")

    return {}

# =========================
# GITHUB SAVE
# =========================
def save_to_github(data):
    try:
        if not GITHUB_TOKEN:
            return False

        headers = {"Authorization": f"token {GITHUB_TOKEN}"}

        session = requests.Session()
        session.trust_env = False

        # ambil SHA
        res = session.get(
            GITHUB_API_URL,
            headers=headers,
            verify=certifi.where(),
            timeout=10
        )

        sha = res.json().get("sha") if res.status_code == 200 else None

        content_encoded = base64.b64encode(
            json.dumps(data, indent=4).encode()
        ).decode()

        payload = {
            "message": "Update location config",
            "content": content_encoded,
            "sha": sha
        }

        res = session.put(
            GITHUB_API_URL,
            headers=headers,
            json=payload,
            verify=certifi.where(),
            timeout=10
        )

        return res.status_code in [200, 201]

    except Exception as e:
        st.error(f"Gagal save ke GitHub: {e}")
        return False

# =========================
# LOAD HYBRID
# =========================
def load_location():
    # 1. LOCAL
    try:
        if os.path.exists(LOCATION_FILE):
            with open(LOCATION_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Local load gagal: {e}")

    # 2. GITHUB
    data = load_from_github()

    # 3. CACHE KE LOCAL
    if data:
        try:
            os.makedirs(os.path.dirname(LOCATION_FILE), exist_ok=True)
            with open(LOCATION_FILE, "w") as f:
                json.dump(data, f, indent=4)
        except:
            pass

    return data

# =========================
# SAVE HYBRID
# =========================
def save_location(data):
    local_success = False

    # 1. LOCAL
    try:
        os.makedirs(os.path.dirname(LOCATION_FILE), exist_ok=True)

        with open(LOCATION_FILE, "w") as f:
            json.dump(data, f, indent=4)

        local_success = True

    except Exception as e:
        st.warning(f"Local save gagal: {e}")

    # 2. GITHUB
    github_success = save_to_github(data)

    # 3. RESULT
    if local_success and github_success:
        st.success("✅ Tersimpan (Local + GitHub)")
    elif local_success:
        st.success("✅ Tersimpan (Local only)")
    elif github_success:
        st.success("✅ Tersimpan (GitHub only)")
    else:
        st.error("❌ Gagal simpan ke semua storage")

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
            st.json(payload)

# =========================
# DEBUG
# =========================
if __name__ == "__main__":
    render_system_settings()
