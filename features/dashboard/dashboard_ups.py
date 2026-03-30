import streamlit as st
import streamlit.components.v1 as components

def create_card(title, value, color="#1f2937", icon="⚡"):
    return f"""
    <div style="width:100%;height:120px;display:flex;align-items:center;justify-content:center;">
        <div style='
            width:100%;
            background: linear-gradient(135deg, {color}, #111827);
            border-radius:16px;
            padding:12px;
            text-align:center;
            box-shadow:0 6px 18px rgba(0,0,0,0.5);
            border:1px solid rgba(255,255,255,0.08);
        '>

            <div style='font-size:20px;'>{icon}</div>

            <div style='
                font-size:12px;
                color:#9ca3af;
                margin-top:2px;
            '>
                {title}
            </div>

            <div style='
                font-size:18px;
                font-weight:700;
                color:white;
                margin-top:4px;
            '>
                {value}
            </div>

        </div>
    </div>
    """

def render_ups(data, cfg):
    st.markdown("---")

    st.markdown(f"""
    <div class="scada-card">
        <div class="scada-title">UPS System Monitor</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")

    # 🔥 FULL ORIGINAL CARDS (BALIKIN SEMUA)
    cards = [
        ("Est. Capacity", f"{data['capacity']} Ah", "#2563eb", "🔋"),
        ("String Voltage", f"{round(sum(data['cell_voltage']), 2)} V", "#7c3aed", "⚡"),
        ("Cycle", data['cycle'], "#0ea5e9", "🔄"),
        ("String Current", f"{data['current']} A", "#f59e0b", "🔌"),
        ("Battery Series", f"{cfg['series']} Cell", "#10b981", "🧱"),
        ("Status", data['status'], "#ef4444", "🚨"),

        # ✅ YANG HILANG → BALIKIN
        ("Ambient", f"{data['ambient']} °C", "#22c55e", "🌡"),
        ("Pressure", data['pressure'], "#eab308", "📊"),
    ]

    cols = st.columns(len(cards))

    for i, (t, v, c, ic) in enumerate(cards):
        with cols[i]:
            components.html(create_card(t, v, c, ic), height=140)