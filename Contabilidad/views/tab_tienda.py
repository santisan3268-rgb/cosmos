"""
views/tab_tienda.py – Tab "Por Tienda".
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped
from conta_core.parser_utils import HORA_COLS

_HORA_COLS_TIENDA = [
    "DO", "RNO", "HEDO", "HENO", "DOM",
    "RNF", "HEDF", "HENF", "FEST", "RNDOM",
    "RDOM", "ODOM", "ORNF", "OEDF", "OFEST", "TOTAL",
]


def render(dff: pd.DataFrame) -> None:
    st.subheader("Análisis por Tienda / Grupo")
    st.caption("Agrupación basada en el campo 'Grupo' del documento Siesa Access.")

    hora_cols_tienda = [c for c in _HORA_COLS_TIENDA if c in dff.columns]

    t_tienda = (
        dff.groupby("Grupo")[hora_cols_tienda]
        .sum()
        .reset_index()
        .rename(columns={"Grupo": "Tienda"})
        .sort_values(
            "TOTAL" if "TOTAL" in hora_cols_tienda else hora_cols_tienda[-1],
            ascending=False,
        )
        .reset_index(drop=True)
    )
    _total_col_t = "TOTAL" if "TOTAL" in t_tienda.columns else (hora_cols_tienda[-1] if hora_cols_tienda else None)

    # ── KPIs de tiendas ──
    if not t_tienda.empty and _total_col_t:
        top_t = t_tienda.iloc[0]
        _prom = t_tienda[_total_col_t].mean()
        _ti1, _ti2, _ti3 = st.columns(3)
        _ti1.metric("Tienda con más horas", str(top_t["Tienda"]), f"{top_t[_total_col_t]:,.2f} h")
        _ti2.metric("Número de tiendas", len(t_tienda))
        _ti3.metric("Promedio horas / tienda", f"{_prom:,.2f}")

    # ── Gráfica ranking horizontal ──
    if not t_tienda.empty and _total_col_t:
        _fig_tienda_h = max(350, len(t_tienda) * 42 + 100)
        fig_rank = px.bar(
            t_tienda.sort_values(_total_col_t, ascending=True),
            x=_total_col_t, y="Tienda", orientation="h",
            color=_total_col_t,
            color_continuous_scale=[[0, "#F0DDD6"], [0.5, "#C9765F"], [1, "#8A2F1F"]],
            labels={_total_col_t: "Total horas", "Tienda": "Tienda"},
            title="Ranking de tiendas por horas totales",
            height=_fig_tienda_h,
            text=_total_col_t,
        )
        fig_rank.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
        fig_rank.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            coloraxis_showscale=False, font_size=12,
            margin=dict(l=10, r=60, t=50, b=30),
        )
        st.plotly_chart(fig_rank, use_container_width=True)

    # ── Gráfica barras apiladas: composición de horas por tienda ──
    if not t_tienda.empty and len(hora_cols_tienda) > 1:
        _comp_cols = [
            c for c in ["DO", "HEDO", "HENO", "DOM", "HEDF", "HENF", "FEST", "RNO", "RNF"]
            if c in t_tienda.columns
        ]
        if _comp_cols:
            _melt_t = t_tienda[["Tienda"] + _comp_cols].melt(
                id_vars="Tienda", var_name="Tipo", value_name="Horas"
            )
            _melt_t = _melt_t[_melt_t["Horas"] > 0]
            _melt_t["Tipo_desc"] = _melt_t["Tipo"].map(lambda x: HORA_COLS.get(x, x))
            if not _melt_t.empty:
                fig_comp_t = px.bar(
                    _melt_t, x="Tienda", y="Horas", color="Tipo_desc",
                    barmode="stack", height=420,
                    labels={"Tienda": "Tienda", "Horas": "Horas", "Tipo_desc": "Tipo"},
                    title="Composición de horas por tienda",
                )
                fig_comp_t.update_layout(
                    xaxis_tickangle=-30,
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    legend_title="Tipo de hora", font_size=12,
                )
                st.plotly_chart(fig_comp_t, use_container_width=True)

    # ── Tabla resumen por tienda ──
    st.markdown("#### Tabla resumen por tienda")
    t_tienda["#"] = range(1, len(t_tienda) + 1)
    _cols_disp_t = ["#", "Tienda"] + [c for c in t_tienda.columns if c not in ("#", "Tienda")]
    t_tienda_disp = t_tienda[_cols_disp_t]
    _fmt_tienda = {
        c: "{:.2f}" for c in t_tienda_disp.columns
        if t_tienda_disp[c].dtype.kind in ("f", "i") and c != "#"
    }
    st.dataframe(
        t_tienda_disp.style.format(_fmt_tienda),
        use_container_width=True,
        height=min(80 + len(t_tienda_disp) * 36, 500),
    )

    # ── Detalle empleados por tienda ──
    st.divider()
    st.markdown("#### Detalle de empleados por tienda")
    _tiendas_list = ["Todas"] + sorted(dff["Grupo"].dropna().unique().tolist())
    sel_tienda_det = st.selectbox("Seleccionar tienda", _tiendas_list, key="sel_tienda_det")

    _det_src = dff if sel_tienda_det == "Todas" else dff[dff["Grupo"] == sel_tienda_det]
    _emp_tienda = (
        _det_src.groupby(["Nombre", "Grupo"])[hora_cols_tienda]
        .sum()
        .reset_index()
        .rename(columns={"Grupo": "Tienda"})
        .sort_values(_total_col_t if _total_col_t else "Nombre", ascending=False)
        .reset_index(drop=True)
    )
    _fmt_emp_t = {c: "{:.2f}" for c in _emp_tienda.columns if _emp_tienda[c].dtype.kind in ("f", "i")}
    st.dataframe(
        _emp_tienda.style.format(_fmt_emp_t),
        use_container_width=True,
        height=min(80 + len(_emp_tienda) * 36, 500),
    )
    _xlsx_emp_tienda = df_to_excel_grouped(_emp_tienda, "Empleados por tienda", group_col="Tienda")
    st.download_button(
        "Descargar Excel (empleados por tienda)",
        icon=":material/download:", data=_xlsx_emp_tienda,
        file_name=f"empleados_{sel_tienda_det.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_emp_tienda",
    )

    # ── Descarga Excel resumen ──
    _t_tienda_exp = t_tienda_disp.drop(columns=["#"])
    _xlsx_tienda = df_to_excel_grouped(_t_tienda_exp, "Por tienda", group_col="Tienda")
    st.download_button(
        "Descargar Excel (resumen por tienda)",
        icon=":material/download:", data=_xlsx_tienda,
        file_name="reporte_por_tienda.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_tienda",
    )
