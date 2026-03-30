import streamlit as st
import streamlit.components.v1 as components

def render_cells(cfg, data):
    render_cell_tables(cfg["series"], data)

def render_cell_tables(series, data):
    TOTAL_CELL = 100
    MAX_COL = 5

    st.markdown("### 🔋 Cells Performance")

    table_soc = data.get("table_soc", [])
    table_soh = data.get("table_soh", [])
    table_rint = data.get("table_rint", [])
    table_temp = data.get("table_temp", [])
    table_lvl = data.get("table_lvl", [])

    for row_start in range(0, TOTAL_CELL, MAX_COL):
        row_cells = range(row_start, min(row_start + MAX_COL, TOTAL_CELL))
        cols = st.columns(len(row_cells))

        for col, i in zip(cols, row_cells):
            cell_num = i + 1
            is_active = i < series

            if is_active:
                soc_val = f"{int(table_soc[i])}" if i < len(table_soc) else "-"
                soh_val = f"{int(table_soh[i])}" if i < len(table_soh) else "-"
                lvl_val = f"{int(table_lvl[i])}" if i < len(table_lvl) else "-"
                rint_val = f"{table_rint[i]:.2f}" if i < len(table_rint) else "-"
                temp_val = f"{table_temp[i]:.1f}" if i < len(table_temp) else "-"
            else:
                soc_val = soh_val = lvl_val = "-"
                rint_val = temp_val = "-"

            # ✅ STYLE FIX
            if not is_active:
                final_style = """
                    background-color:#111827 !important;
                    border:1px solid #374151;
                    box-shadow: inset 0 0 8px rgba(0,0,0,0.8);
                """
                text_opacity = "0.5"
            else:
                final_style = "background-color:#e5e7eb;"
                text_opacity = "1"

            with col:
                st.markdown(f"**Cell {cell_num}**")

                def get_cell_color(param, val):
                    if not is_active:
                        return "#6b7280"
                    try:
                        val = float(val)
                    except:
                        return "#374151"

                    if param == "SoC":
                        if val < 10: return "#7f1d1d"
                        elif val < 20: return "#ef4444"
                        elif val < 50: return "#f59e0b"
                        else: return "#22c55e"

                    if param == "SoH":
                        if val < 30: return "#7f1d1d"
                        elif val < 50: return "#ef4444"
                        elif val < 80: return "#f59e0b"
                        else: return "#22c55e"

                    if param == "Rint":
                        if val > 1.8: return "#7f1d1d"
                        elif val > 1.5: return "#ef4444"
                        elif val > 1.1: return "#f59e0b"
                        else: return "#22c55e"

                    if param == "Temp":
                        if val > 48: return "#7f1d1d"
                        elif val > 45: return "#ef4444"
                        elif val > 35: return "#f59e0b"
                        else: return "#22c55e"

                    return "#22c55e"

                rows_html = ""

                params = ["SoC","SoH","Rint","Temp","Level"]
                values = [soc_val, soh_val, rint_val, temp_val, lvl_val]
                units = ["%","%","mOhm","Deg.C","%"]

                for p,v,u in zip(params, values, units):
                    color = get_cell_color(p, v)
                    display_val = v if is_active else "Data N/A"

                    rows_html += f"""
                    <tr>
                        <td style="padding:6px;">{p}</td>
                        <td style="padding:6px;text-align:right;color:{color};">{display_val}</td>
                        <td style="padding:6px;text-align:right;color:#9ca3af;">{u if is_active else "-"}</td>
                    </tr>
                    """

                table_html = f"""
                <div style="
                    {final_style}
                    border-radius:12px;
                    padding:10px;
                    opacity:{text_opacity};
                    box-shadow:0 4px 12px rgba(0,0,0,0.4);
                ">
                    <table style="width:100%;border-collapse:collapse;font-size:13px;">
                        <thead>
                            <tr style="color:#9ca3af;text-align:left;border-bottom:1px solid #374151;">
                                <th>Param</th>
                                <th style="text-align:right;">Value</th>
                                <th style="text-align:right;">Unit</th>
                            </tr>
                        </thead>
                        <tbody>
                            {rows_html}
                        </tbody>
                    </table>
                </div>
                """

                components.html(table_html, height=220)