# =========================
# MAP STYLE (CUSTOM MAPBOX)
# =========================
MAPBOX_STYLES = {
    "Streets": "mapbox://styles/mapbox/streets-v12",
    "Outdoors": "mapbox://styles/mapbox/outdoors-v12",
    "Light": "mapbox://styles/mapbox/light-v11",
    "Dark": "mapbox://styles/mapbox/dark-v11",
    "Satellite": "mapbox://styles/mapbox/satellite-v9",
    "Satellite Streets": "mapbox://styles/mapbox/satellite-streets-v12",
    "Navigation Day": "mapbox://styles/mapbox/navigation-day-v1",
    "Navigation Night": "mapbox://styles/mapbox/navigation-night-v1"
}

# =========================
# IMPORT
# =========================
import json
import os

# =========================
# LOAD LOCATION CONFIG
# =========================
def load_location_config():
    default = {
        "area": "Head Office Jakarta",
        "station": "Infrastructure Management",
        "lat": -6.1772,
        "lon": 106.8306
    }

    try:
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(ROOT_DIR, "config", "ptg_location.json")

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)

                return {
                    "area": data.get("area", default["area"]),
                    "station": data.get("station", default["station"]),
                    "lat": data.get("lat", default["lat"]),
                    "lon": data.get("lon", default["lon"])
                }
    except:
        pass

    return default

# =========================
# SITES
# =========================
def get_sites(data):

    # ✅ FIX: define loc properly
    loc = load_location_config()

    return [
        {
            "area": loc["area"],
            "station": loc["station"],
            "lat": loc["lat"],
            "lon": loc["lon"],

            # data existing tetap
            "soc": data.get("soc", 0),
            "soh": data.get("soh", 0),
            "temp": data.get("temp", 0),
            "ir": data.get("ir", 0)
        }
    ]

# =========================
# COLOR LOGIC (FIXED)
# =========================
def get_color_soc(soc):
    if soc < 20:
        return [255, 0, 0]
    elif soc < 50:
        return [255, 165, 0]
    else:
        return [0, 200, 0]

def get_color_soh(soh):
    if soh < 50:
        return [255, 0, 0]
    elif soh < 70:
        return [255, 165, 0]
    else:
        return [0, 200, 0]