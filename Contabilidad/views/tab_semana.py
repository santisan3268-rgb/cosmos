"""
views/tab_semana.py – Tab "Por semana".
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
    st.subheader("Resumen por persona / semana")

    hora_cols_sum = [c for c in _HORA_COLS_SUM if c in dff.columns]
    t_sem = (
        dff.groupby(["Nombre", "Semana_etiqueta"])[hora_cols_sum]
        .sum()
        .reset_index()
        .rename(columns={"Semana_etiqueta": "Semana"})
    )

    per_sem = st.selectbox(
        "Filtrar empleado (semana)",
        ["Todos"] + sorted(dff["Nombre"].unique()),
        key="sel_sem",
    )
    if per_sem != "Todos":
        t_sem = t_sem[t_sem["Nombre"] == per_sem]

    t_sem_sorted = t_sem.sort_values(["Nombre", "Semana"]).reset_index(drop=True)
    num_cols = [c for c in t_sem_sorted.columns if c not in ("Nombre", "Semana")]

    if per_sem != "Todos":
        st.markdown(f"#### {per_sem}")
        st.dataframe(
            t_sem_sorted.drop(columns=["Nombre"]).style.format({c: "{:.2f}" for c in num_cols}),
            use_container_width=True, height=400,
        )
    else:
        st.dataframe(
            t_sem_sorted.style.format({c: "{:.2f}" for c in num_cols}),
            use_container_width=True, height=400,
        )

    xlsx_sem = df_to_excel_grouped(t_sem_sorted, "Por semana")
    st.download_button(
        label="Descargar Excel",
        icon=":material/download:",
        data=xlsx_sem,
        file_name="reporte_labor_semana.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
