"""
views/tab_total.py – Tab "Total laborado".
"""
import pandas as pd
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped
from conta_core.parser_utils import HORA_COLS

_ALL_HOUR_COLS = list(HORA_COLS.keys())

_EXTRAS_ORD   = ["HEDO", "HENO"]
_EXTRAS_FEST  = ["HEDF", "HENF"]
_DOM_FEST     = ["DOM", "FEST", "RNDOM", "RDOM"]
_RECARGOS     = ["RNO", "RNF", "ODOM", "ORNF", "OEDF", "OFEST"]


def render(dff: pd.DataFrame) -> None:
    st.subheader("Total de tiempo laborado")

    # JORNADA es columna de referencia del turno, no componente del TOTAL.
    _all_hour_cols_t   = [c for c in _ALL_HOUR_COLS if c not in ("TOTAL", "JORNADA") and c in dff.columns]
    _extras_ord_cols   = [c for c in _EXTRAS_ORD  if c in dff.columns]
    _extras_fest_cols  = [c for c in _EXTRAS_FEST  if c in dff.columns]

    _grp_t = (
        dff.groupby("Nombre")[_all_hour_cols_t + (["TOTAL"] if "TOTAL" in dff.columns else [])]
        .sum()
        .reset_index()
    )
    if "DO" in _grp_t.columns:
        _grp_t["DO"] = _grp_t["DO"].round(2)

    _grp_t["Extras_Ordinarias"] = (
        _grp_t[[c for c in _extras_ord_cols  if c in _grp_t.columns]].sum(axis=1).round(2)
    )
    _grp_t["Extras_Festivas"] = (
        _grp_t[[c for c in _extras_fest_cols if c in _grp_t.columns]].sum(axis=1).round(2)
    )
    _dom_fest_exist = [c for c in _DOM_FEST    if c in _grp_t.columns]
    _recargo_exist  = [c for c in _RECARGOS    if c in _grp_t.columns]
    _grp_t["Dom_Festivo"] = _grp_t[_dom_fest_exist].sum(axis=1).round(2) if _dom_fest_exist else 0
    _grp_t["Recargos"]    = _grp_t[_recargo_exist ].sum(axis=1).round(2) if _recargo_exist  else 0
    if "TOTAL" in _grp_t.columns:
        _grp_t["TOTAL"] = _grp_t["TOTAL"].round(2)

    subt = st.tabs(["Resumen", "Ordinario vs Extra", "Detalle completo"])

    # ── Subtab: Resumen ──
    with subt[0]:
        _he_cols_exist = [
            c for c in [
                "DO", "RNO", "HEDO", "HENO", "DOM", "FEST",
                "RNF", "HEDF", "HENF", "RNDOM", "RDOM",
                "ODOM", "ORNF", "OEDF", "OFEST",
            ]
            if c in _grp_t.columns
        ]
        _summary_cols = ["Nombre"] + _he_cols_exist
        if "TOTAL" in _grp_t.columns:
            _summary_cols.append("TOTAL")
        _disp_res = (
            _grp_t[_summary_cols].sort_values("Nombre").reset_index(drop=True)
            .rename(columns={
                "DO":    "DO (Jornada ord.)",
                "RNO":   "RNO (Rec. noct. ord.)",
                "HEDO":  "HEDO (H.E. Diurna Ord.)",
                "HENO":  "HENO (H.E. Noct. Ord.)",
                "DOM":   "DOM (Dominical)",
                "FEST":  "FEST (Festivo)",
                "RNF":   "RNF (Rec. noct. fest.)",
                "HEDF":  "HEDF (H.E. Diurna Fest.)",
                "HENF":  "HENF (H.E. Noct. Fest.)",
                "RNDOM": "RNDOM (Rec. noct. dom.)",
                "RDOM":  "RDOM (Rec. dom.)",
                "ODOM":  "ODOM (H.E. dom.)",
                "ORNF":  "ORNF (Rec. noct. fest.)",
                "OEDF":  "OEDF (H.E. diurna fest.)",
                "OFEST": "OFEST (Otras fest.)",
                "TOTAL": "TOTAL",
            })
        )
        st.caption("Cada columna es la suma de todas las horas del período. TOTAL = suma de todas las categorías.")
        st.dataframe(
            _disp_res.style.format({
                c: "{:.2f}" for c in _disp_res.columns
                if _disp_res[c].dtype.kind in ("f", "i")
            }),
            use_container_width=True,
            height=min(60 + len(_disp_res) * 36, 500),
        )
        _xlsx_res = df_to_excel_grouped(_disp_res, "Resumen laborado")
        st.download_button(
            "Descargar Excel", icon=":material/download:",
            data=_xlsx_res, file_name="total_resumen.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tot_res",
        )

    # ── Subtab: Ordinario vs Extra ──
    with subt[1]:
        _norm_cols = [c for c in _all_hour_cols_t if c not in (_extras_ord_cols + _extras_fest_cols)]
        _grp_t["Tiempo_Ordinario"] = (
            _grp_t[[c for c in _norm_cols if c in _grp_t.columns]].sum(axis=1).round(2)
        )
        _grp_t["Tiempo_Extra"] = (_grp_t["Extras_Ordinarias"] + _grp_t["Extras_Festivas"]).round(2)
        _disp_ord = (
            _grp_t[
                ["Nombre", "Tiempo_Ordinario", "Tiempo_Extra"]
                + (["TOTAL"] if "TOTAL" in _grp_t.columns else [])
            ]
            .sort_values("Nombre")
            .reset_index(drop=True)
        )
        st.dataframe(
            _disp_ord.style.format({
                c: "{:.2f}" for c in _disp_ord.columns
                if _disp_ord[c].dtype.kind in ("f", "i")
            }),
            use_container_width=True,
            height=min(60 + len(_disp_ord) * 36, 500),
        )
        _xlsx_ord = df_to_excel_grouped(_disp_ord, "Total Ordinario vs Extra")
        st.download_button(
            "Descargar Excel", icon=":material/download:",
            data=_xlsx_ord, file_name="total_ordinario_extra.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tot_ord",
        )

    # ── Subtab: Detalle completo ──
    with subt[2]:
        _det_cols = (
            ["Nombre"]
            + [c for c in _all_hour_cols_t if c in _grp_t.columns]
            + (["TOTAL"] if "TOTAL" in _grp_t.columns else [])
        )
        _disp_ext = _grp_t[_det_cols].sort_values("Nombre").reset_index(drop=True)
        st.caption("Todas las columnas de horas individuales del reporte Siesa.")
        st.dataframe(
            _disp_ext.style.format({
                c: "{:.2f}" for c in _disp_ext.columns
                if _disp_ext[c].dtype.kind in ("f", "i")
            }),
            use_container_width=True,
            height=min(60 + len(_disp_ext) * 36, 500),
        )
        _xlsx_ext = df_to_excel_grouped(_disp_ext, "Detalle completo laborado")
        st.download_button(
            "Descargar Excel", icon=":material/download:",
            data=_xlsx_ext, file_name="total_detalle_completo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_tot_ext",
        )
