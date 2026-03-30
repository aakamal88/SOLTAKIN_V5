from .dashboard_settings import get_alarm_setting

def get_status(val, key):
    alarm = get_alarm_setting().get(key, {})

    warn = alarm.get("warning")
    crit = alarm.get("critical")
    alert = alarm.get("alert")

    if warn is None:
        if key == "soc":
            if val < 10: return "ALERT","#7f1d1d"
            if val < 20: return "CRITICAL","#ef4444"
            elif val < 50: return "WARNING","#f59e0b"
            else: return "GOOD","#22c55e"

        if key == "soh":
            if val < 30: return "ALERT","#7f1d1d"
            if val < 50: return "CRITICAL","#ef4444"
            elif val < 80: return "WARNING","#f59e0b"
            else: return "GOOD","#22c55e"

        if key == "ir":
            if val > 1.8: return "ALERT","#7f1d1d"
            if val > 1.5: return "CRITICAL","#ef4444"
            elif val > 1.1: return "WARNING","#f59e0b"
            else: return "GOOD","#22c55e"

        if key == "temp":
            if val > 48: return "ALERT","#7f1d1d"
            if val > 45: return "CRITICAL","#ef4444"
            elif val > 35: return "WARNING","#f59e0b"
            else: return "GOOD","#22c55e"

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