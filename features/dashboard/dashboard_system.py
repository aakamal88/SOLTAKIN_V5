import streamlit as st
import plotly.graph_objects as go
import streamlit.components.v1 as components

from .dashboard_utils import get_status, get_perf_color
from .dashboard_settings import get_alarm_setting


def create_gauge(val, minv, maxv, unit, key_type):
    steps = []

    if key_type == "soc":
        steps = [
            {'range':[0,20],'color':'red'},
            {'range':[20,50],'color':'orange'},
            {'range':[50,100],'color':'green'}
        ]

    elif key_type == "soh":
        steps = [
            {'range':[0,50],'color':'red'},
            {'range':[50,80],'color':'orange'},
            {'range':[80,100],'color':'green'}
        ]

    elif key_type == "ir":
        steps = [
            {'range':[0,1.1],'color':'green'},
            {'range':[1.1,1.5],'color':'orange'},
            {'range':[1.5,2],'color':'red'}
        ]

    elif key_type == "temp":
        steps = [
            {'range':[-10,0],'color':'red'},
            {'range':[0,30],'color':'green'},
            {'range':[30,40],'color':'orange'},
            {'range':[40,60],'color':'red'}
        ]

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=val,
        number={
            'suffix': f" {unit}",
            'valueformat': ".2f" if key_type == "ir"
                  else ".1f" if key_type == "temp"
                  else ".0f"
        },
        gauge={
            'axis': {'range': [minv, maxv]},
            'bar': {'color': "#00FFFF"},
            'steps': steps,
            'threshold': {
                'line': {'color': "white", 'width': 3},
                'value': val
            }
        }
    ))

    fig.update_layout(height=350)

    return fig


def render_system(data):
    st.markdown("---")

    perf_color = get_perf_color(data)

    st.markdown(f"""
    <div class="scada-card" style="background:{perf_color};">
        <div class="scada-title">Battery System Performance</div>
    </div>
    """, unsafe_allow_html=True)

    g1, g2, g3, g4 = st.columns(4)

    configs = [
        ("soc", "%", 0, 100, "State of Charge"),
        ("soh", "%", 0, 100, "State of Health"),
        ("ir", "mΩ", 0, 2, "Avg. Resistance"),
        ("temp", "°C", 0, 60, "Avg. Temperature"),
    ]

    for idx, (col, (k, u, minv, maxv, title)) in enumerate(zip([g1, g2, g3, g4], configs)):
        with col:
            st.markdown(f'<div class="gauge-title">{title}</div>', unsafe_allow_html=True)

            # format value
            if k == "ir":
                val = round(data[k], 2)
            elif k == "temp":
                val = round(data[k], 1)
            elif k in ["soc", "soh"]:
                val = int(round(data[k]))
            else:
                val = data[k]

            st.plotly_chart(
                create_gauge(val, minv, maxv, u, k),
                use_container_width=True,
                key=f"perf_{k}_{idx}"
            )

            label, color = get_status(data[k], k)

            alarm = get_alarm_setting().get(k, {})
            warn = alarm.get("warning")
            crit = alarm.get("critical")
            alert = alarm.get("alert")

            # fallback default
            if warn is None:
                if k == "soc":
                    warn, crit, alert = 50, 20, 10
                elif k == "soh":
                    warn, crit, alert = 80, 50, 30
                elif k == "ir":
                    warn, crit, alert = 1.1, 1.5, 1.8
                elif k == "temp":
                    warn, crit, alert = 35, 45, 48

            animation_style = ""
            if label == "ALERT":
                animation_style = "animation: blink 0.4s infinite;"
            elif label == "CRITICAL":
                animation_style = "animation: blink 0.8s infinite;"
            elif label == "WARNING":
                animation_style = "animation: blink 1.5s infinite;"

            html = f"""
            <div style="text-align:center;">

                <div style="
                    font-size:16px;
                    margin-top:2px;
                    margin-bottom:4px;
                    line-height:1.4;
                ">
                    ⚠ Warning: <b>{warn}</b><br>
                    🔥 Critical: <b>{crit}</b><br>
                    🚨 Alert: <b>{alert}</b>
                </div>

                <div style="
                    background:{color};
                    color:white;
                    padding:4px;
                    border-radius:6px;
                    font-size:12px;
                    text-align:center;
                    {animation_style}
                ">
                    {label}
                </div>

            </div>

            <style>
            @keyframes blink {{
                0% {{opacity:1;}}
                50% {{opacity:0.3;}}
                100% {{opacity:1;}}
            }}
            </style>
            """

            components.html(html, height=110)