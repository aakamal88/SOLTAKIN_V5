from core.data_loader import load_settings

def get_alarm_setting():
    return load_settings().get("alarm_setting", {})

def get_status(val, key):

    alarm = get_alarm_setting().get(key, {})

    warn = alarm.get("warning")
    crit = alarm.get("critical")
    alert = alarm.get("alert")

    # =========================
    # 🔥 DEFAULT FALLBACK (WAJIB)
    # =========================
    if warn is None or crit is None or alert is None:

        if key == "soc":
            warn, crit, alert = 50, 20, 10

        elif key == "soh":
            warn, crit, alert = 80, 50, 30

        elif key == "ir":
            warn, crit, alert = 1.1, 1.5, 1.8

        elif key == "temp":
            warn, crit, alert = 35, 45, 48

    # =========================
    # SAFE COMPARISON
    # =========================
    try:
        val = float(val)
    except:
        return "UNKNOWN", "#6b7280"

    if key in ["soc","soh","voltage"]:
        if val <= alert: return "ALERT","#7f1d1d"
        elif val <= crit: return "CRITICAL","#ef4444"
        elif val <= warn: return "WARNING","#f59e0b"
        else: return "GOOD","#22c55e"
    else:
        if val >= alert: return "ALERT","#7f1d1d"
        elif val >= crit: return "CRITICAL","#ef4444"
        elif val >= warn: return "WARNING","#f59e0b"
        else: return "GOOD","#22c55e"

def get_perf_color(data):
    if data["soc"] < 20 or data["temp"] > 45:
        return "#fee2e2"
    elif data["temp"] > 35:
        return "#fef3c7"
    return "#ecfdf5"