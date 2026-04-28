"""
views/tab_mes.py – Tab "Por mes".
"""
import pandas as pd
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped

_HORA_COLS_SUM = [
    "JORNADA", "DO", "RNO", "HEDO", "HENO", "DOM",
    "RNF", "HEDF", "HENF", "FEST", "RNDOM", "RDOM",
    "ODOM", "ORNF", "OFEST", "TOTAL",
]


def render(dff: pd.DataFrame) -> None:
    st.subheader("Resumen por persona / mes")

    hora_cols_sum = [c for c in _HORA_COLS_SUM if c in dff.columns]
    t_mes = (
        dff.groupby(["Nombre", "Mes"])[hora_cols_sum]
        .sum()
        .reset_index()
    )

    per_mes = st.selectbox(
        "Filtrar empleado (mes)",
        ["Todos"] + sorted(dff["Nombre"].unique()),
        key="sel_mes",
    )
    if per_mes != "Todos":
        t_mes = t_mes[t_mes["Nombre"] == per_mes]

    t_mes_sorted = t_mes.sort_values("Nombre").reset_index(drop=True)
    num_cols_mes = [c for c in t_mes_sorted.columns if c not in ("Nombre", "Mes")]

    if per_mes != "Todos":
        st.markdown(f"#### {per_mes}")
        st.dataframe(
            t_mes_sorted.drop(columns=["Nombre"]).style.format({c: "{:.2f}" for c in num_cols_mes}),
            use_container_width=True, height=400,
        )
    else:
        st.dataframe(
            t_mes_sorted.style.format({c: "{:.2f}" for c in num_cols_mes}),
            use_container_width=True, height=400,
        )

    xlsx_mes = df_to_excel_grouped(t_mes_sorted, "Por mes")
    st.download_button(
        label="Descargar Excel",
        icon=":material/download:",
        data=xlsx_mes,
        file_name="reporte_labor_mes.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
