import streamlit as st
from .location_utils import load_json, save_json, FILE_GATEWAY, ping_ip

def render_gateway():
    st.subheader("🧠 Soltakin Gateway Setting")

    gw = load_json(FILE_GATEWAY, {"controllers": []})
    controllers = gw.get("controllers", [])

    # ✅ AUTO MIGRASI (tanpa merusak struktur lama)
    for c in controllers:
        if "name" not in c:
            c["name"] = c.get("node", "")
        if "slave_id" not in c:
            try:
                c["slave_id"] = int(c.get("subnet", 1))
            except:
                c["slave_id"] = 1
        if "port" not in c:
            c["port"] = c.get("gateway", "")

    if "edit_idx" not in st.session_state:
        st.session_state.edit_idx = None

    col1, col2 = st.columns([1, 2])

    # ================= FORM =================
    with col1:
        st.markdown("### ➕ Add / Edit")

        if st.session_state.edit_idx is not None:
            c = controllers[st.session_state.edit_idx]
            default_name = c.get("name", "")
            default_ip = c.get("ip", "")
            default_slave = c.get("slave_id", 1)
            default_port = c.get("port", "")
        else:
            default_name = ""
            default_ip = ""
            default_slave = 1
            default_port = ""

        name = st.text_input("Gateway Name", value=default_name)
        ip_ctrl = st.text_input("IP Soltakin Gateway (xxx.xxx.xxx.xxx)", value=default_ip)
        slave_id = st.number_input("Slave ID (0-100)", min_value=0, max_value=100, value=default_slave)
        port = st.text_input("Port", value=default_port)

        if st.button("💾 Save Gateway"):
            error = False

            if not name or not ip_ctrl:
                st.error("Gateway Name & IP wajib")
                error = True

            for i, c in enumerate(controllers):
                if st.session_state.edit_idx == i:
                    continue
                if c.get("name") == name:
                    st.error("❌ Gateway Name sudah ada")
                    error = True
                if c.get("ip") == ip_ctrl:
                    st.error("❌ IP sudah digunakan")
                    error = True

            if not error:
                data = {
                    "name": name,
                    "ip": ip_ctrl,
                    "slave_id": slave_id,
                    "port": port,
                    "status": "-"
                }

                if st.session_state.edit_idx is not None:
                    controllers[st.session_state.edit_idx] = data
                    st.session_state.edit_idx = None
                else:
                    controllers.append(data)

                save_json(FILE_GATEWAY, {"controllers": controllers})
                st.rerun()

    # ================= TABLE =================
    with col2:
        st.markdown("### 📋 Gateway List")

        display = [{
            "Select": False,
            "Gateway Name": c.get("name", ""),
            "IP Soltakin Gateway": c.get("ip", ""),
            "Slave ID": c.get("slave_id", 1),
            "Port": c.get("port", ""),
            "Status": c.get("status", "-")
        } for c in controllers]

        edited = st.data_editor(display, use_container_width=True, height=300)

        selected = [i for i, r in enumerate(edited) if r["Select"]]

        colA, colB, colC, colD = st.columns(4)

        with colA:
            if st.button("🔍 Ping"):
                for i in selected:
                    controllers[i]["status"] = (
                        "Connected" if ping_ip(controllers[i]["ip"]) else "Not Connected"
                    )
                save_json(FILE_GATEWAY, {"controllers": controllers})
                st.rerun()

        with colB:
            if st.button("✏️ Edit"):
                if len(selected) == 1:
                    st.session_state.edit_idx = selected[0]
                    st.rerun()
                else:
                    st.warning("Pilih 1 data")

        with colC:
            if st.button("💾 Save Edit"):
                for i in selected:
                    controllers[i]["name"] = edited[i]["Gateway Name"]
                    controllers[i]["ip"] = edited[i]["IP Soltakin Gateway"]
                    controllers[i]["slave_id"] = edited[i]["Slave ID"]
                    controllers[i]["port"] = edited[i]["Port"]

                st.session_state.edit_idx = None
                save_json(FILE_GATEWAY, {"controllers": controllers})
                st.success("✅ Perubahan tabel disimpan")
                st.rerun()

        with colD:
            if st.button("🗑 Delete"):
                for i in sorted(selected, reverse=True):
                    controllers.pop(i)

                save_json(FILE_GATEWAY, {"controllers": controllers})
                st.rerun()