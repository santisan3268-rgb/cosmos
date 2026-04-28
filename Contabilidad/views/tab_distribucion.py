"""
views/tab_distribucion.py – Gráfica "Distribución de tipos de horas por empleado".
Se renderiza en el área principal fuera de los tabs.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from conta_core.parser_utils import HORA_COLS

_DIST_COLS = ["JORNADA", "HEDO", "HENO", "DOM", "HEDF", "HENF", "FEST"]


def render(dff: pd.DataFrame) -> None:
    st.divider()
    st.subheader("Distribución de tipos de horas por empleado")

    dist_cols = [c for c in _DIST_COLS if c in dff.columns]
    dist_df   = dff.groupby("Nombre")[dist_cols].sum().reset_index()
    dist_melt = dist_df.melt(id_vars="Nombre", var_name="Tipo", value_name="Horas")
    dist_melt["Tipo_desc"]  = dist_melt["Tipo"].map(lambda x: HORA_COLS.get(x, x))
    dist_melt_filtered = dist_melt[dist_melt["Horas"] > 0]

    if dist_df.shape[0] == 1:
        fig = px.pie(
            dist_melt_filtered,
            values="Horas", names="Tipo_desc",
            hole=0.4,
            labels={"Horas": "Horas", "Tipo_desc": "Tipo"},
            height=420,
            title="Composición de horas por empleado (período seleccionado)",
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend_title="Tipo de hora",
        )
    else:
        fig = px.bar(
            dist_melt_filtered,
            x="Nombre", y="Horas", color="Tipo_desc",
            barmode="stack", height=420,
            labels={"Nombre": "Empleado", "Horas": "Horas", "Tipo_desc": "Tipo"},
            title="Composición de horas por empleado (período seleccionado)",
        )
        fig.update_layout(
            xaxis_tickangle=-30,
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            legend_title="Tipo de hora", font_size=12,
        )

    st.plotly_chart(fig, use_container_width=True)
