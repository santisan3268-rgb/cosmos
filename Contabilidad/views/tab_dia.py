"""
views/tab_dia.py – Tab "Por día".
"""
import pandas as pd
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped


def render(dff: pd.DataFrame) -> None:
    st.subheader("Resumen por persona / día")

    cols_show = ["Nombre", "Fecha", "Día", "Turno"] + [
        c for c in [
            "DO", "RNO", "HEDO", "HENO", "DOM", "RNF",
            "HEDF", "HENF", "FEST", "RNDOM", "RDOM",
            "ODOM", "ORNF", "OEDF", "OFEST", "TOTAL",
        ]
        if c in dff.columns
    ]
    t_dia = dff[cols_show].copy()
    t_dia["Fecha"] = t_dia["Fecha"].dt.strftime("%d/%m/%Y")

    per_dia = st.selectbox(
        "Filtrar empleado (día)",
        ["Todos"] + sorted(dff["Nombre"].unique()),
        key="sel_dia",
    )
    if per_dia != "Todos":
        t_dia = t_dia[t_dia["Nombre"] == per_dia]

    t_dia_sorted = t_dia.sort_values(["Nombre", "Fecha"]).reset_index(drop=True)
    _num_dia = [c for c in t_dia_sorted.columns if t_dia_sorted[c].dtype.kind in ("f", "i") and c != "Fecha"]
    _fmt_dia = {c: "{:.2f}" for c in _num_dia}

    if per_dia != "Todos":
        st.markdown(f"#### {per_dia}")
        st.dataframe(
            t_dia_sorted.drop(columns=["Nombre"]).style.format(_fmt_dia),
            use_container_width=True, height=400,
        )
    else:
        st.dataframe(t_dia_sorted.style.format(_fmt_dia), use_container_width=True, height=400)

    xlsx_dia = df_to_excel_grouped(t_dia_sorted, "Por día")
    st.download_button(
        label="Descargar Excel",
        icon=":material/download:",
        data=xlsx_dia,
        file_name="reporte_labor_dia.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
