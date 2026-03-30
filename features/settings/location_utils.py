import json
import os
import socket
import psutil
import platform
import streamlit as st

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FILE_LOCATION = os.path.join(ROOT_DIR, "config", "ptg_location.json")
FILE_LAN = os.path.join(ROOT_DIR, "config", "ptg_lan.json")
FILE_GATEWAY = os.path.join(ROOT_DIR, "config", "ptg_gateway.json")

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

def load_json(path, default):
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except:
        pass
    return default

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)
    st.success("✅ Tersimpan")

def get_network_interfaces():
    interfaces = []
    addrs = psutil.net_if_addrs()

    for iface_name, iface_data in addrs.items():
        ipv4 = None
        for addr in iface_data:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                ipv4 = addr.address

        interfaces.append({
            "name": iface_name,
            "ipv4": ipv4 if ipv4 else "-"
        })

    return interfaces

def ping_ip(ip):
    param = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    command = f"ping {param} {ip} > nul 2>&1" if platform.system().lower() == "windows" else f"ping {param} {ip} > /dev/null 2>&1"
    return os.system(command) == 0