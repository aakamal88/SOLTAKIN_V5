import streamlit as st
from .location_utils import load_json, save_json, FILE_LAN, get_network_interfaces

def render_network():
    lan = load_json(FILE_LAN, {
        "mode": "DHCP",
        "interface": "",
        "ip": "",
        "subnet": "255.255.255.0",
        "gateway": "",
        "dns": ""
    })

    st.subheader("🌐 Local Network Configuration")

    interfaces = get_network_interfaces()
    iface_names = [f"{i['name']} ({i['ipv4']})" for i in interfaces]

    mode = st.radio("IP Mode", ["DHCP", "Static"],
                    index=0 if lan["mode"] == "DHCP" else 1,
                    key="lan_mode")

    selected_iface = st.selectbox("Interface", iface_names, key="lan_iface")

    ip = st.text_input("IP", value=lan["ip"], key="lan_ip")
    subnet = st.text_input("Subnet", value=lan["subnet"], key="lan_subnet")
    gateway = st.text_input("Gateway", value=lan["gateway"], key="lan_gateway")
    dns = st.text_input("DNS", value=lan["dns"], key="lan_dns")

    if st.button("💾 Save Network"):
        save_json(FILE_LAN, {
            "mode": mode,
            "interface": selected_iface.split(" ")[0],
            "ip": ip,
            "subnet": subnet,
            "gateway": gateway,
            "dns": dns
        })