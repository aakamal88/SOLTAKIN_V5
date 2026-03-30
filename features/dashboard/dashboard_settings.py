import json, os
import streamlit as st

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETTINGS_FILE = os.path.join(ROOT_DIR, "../config", "settings.json")

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        st.error(f"Settings file tidak ditemukan: {SETTINGS_FILE}")
        return {}
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error baca settings.json: {e}")
        return {}

def save_settings(data):
    current = load_settings()
    current.update(data)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(current, f, indent=4)

def get_data():
    d = load_settings().get("data", {})
    return {
        "capacity": d.get("capacity", 21.64),
        "cycle": d.get("cycle", 1),
        "current": d.get("current", 0.00),
        "status": d.get("status", "Idle"),
        "soc": d.get("soc", 65),
        "soh": d.get("soh", 92),
        "ir": d.get("ir", 1.1),
        "temp": d.get("temp", 32),
        "ambient": d.get("ambient", 28),
        "pressure": d.get("pressure", 760),
        "cell_voltage": d.get("cell_voltage", []),
        "table_soc": d.get("table_soc", []),
        "table_soh": d.get("table_soh", []),
        "table_rint": d.get("table_rint", []),
        "table_temp": d.get("table_temp", []),
        "table_lvl": d.get("table_lvl", []),
    }

def get_config():
    c = load_settings().get("battery_config", {})
    return {"series": c.get("series", 0)}

def get_alarm_setting():
    return load_settings().get("alarm_setting", {})