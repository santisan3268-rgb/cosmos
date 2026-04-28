"""
views/kpis.py – KPIs globales + tarjeta de detalle por empleado.
"""
import io

import pandas as pd
import streamlit as st

from conta_core.export_utils import df_to_excel_grouped


def render_kpis_and_detail(
    dff: pd.DataFrame,
    fecha_ini,
    fecha_fin,
    sel_personas: list,
) -> None:
    """Muestra métricas resumen, verificación de sumatoria y tarjeta de empleado."""

    def _col_sum(col: str) -> float:
        return float(dff[col].sum()) if col in dff.columns else 0.0

    total_horas = dff["TOTAL"].sum() if "TOTAL" in dff.columns else 0.0
    total_do    = _col_sum("DO")
    total_rno   = _col_sum("RNO")
    total_hedo  = _col_sum("HEDO")
    total_heno  = _col_sum("HENO")
    total_dom   = _col_sum("DOM")
    total_rnf   = _col_sum("RNF")
    total_hedf  = _col_sum("HEDF")
    total_henf  = _col_sum("HENF")
    total_fest  = _col_sum("FEST")
    total_rndom = _col_sum("RNDOM")
    total_rdom  = _col_sum("RDOM")

    dia_persona_laborados    = int((dff["DO"] > 0).sum()) if "DO" in dff.columns else len(dff)
    dias_calendario_periodo  = (pd.to_datetime(fecha_fin) - pd.to_datetime(fecha_ini)).days + 1

    # ── Fila 1: resumen principal ──
    st.markdown("##### Resumen general")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total horas", f"{total_horas:,.2f}")
    k2.metric("DO – Jornada ordinaria", f"{total_do:,.2f}")
    k3.metric("Jornadas (persona-día)", dia_persona_laborados,
              help="Conteo de registros con DO > 0. No son días calendario del mes.")
    k4.metric("Días calendario período", dias_calendario_periodo)

    # ── Fila 2: horas extras ──
    st.markdown("##### Horas extras – desglose por tipo de pago")
    e1, e2, e3, e4 = st.columns(4)
    e1.metric("HEDO – H. Extra diurna ord.",   f"{total_hedo:,.2f}", help="Hora extra diurna en día ordinario")
    e2.metric("HENO – H. Extra nocturna ord.", f"{total_heno:,.2f}", help="Hora extra nocturna en día ordinario")
    e3.metric("HEDF – H. Extra diurna fest.",  f"{total_hedf:,.2f}", help="Hora extra diurna en día festivo")
    e4.metric("HENF – H. Extra noct. fest.",   f"{total_henf:,.2f}", help="Hora extra nocturna en día festivo")

    # ── Fila 3: otros tipos de hora ──
    st.markdown("##### Otros tipos de hora")
    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("RNO",        f"{total_rno:,.2f}",                    help="Recargo nocturno ord.")
    d2.metric("DOM",        f"{total_dom:,.2f}",                    help="Dominical")
    d3.metric("RNF",        f"{total_rnf:,.2f}",                    help="Rec. noct. festivo")
    d4.metric("FEST",       f"{total_fest:,.2f}",                   help="Festivo")
    d5.metric("RNDOM/RDOM", f"{(total_rndom + total_rdom):,.2f}",   help="Rec. noct. dom. + Rec. dom.")

    # ── Verificación de sumatoria ──
    _cols_verificar = [
        "DO", "RNO", "HEDO", "HENO", "DOM", "RNF", "HEDF", "HENF",
        "FEST", "RNDOM", "RDOM", "ODOM", "ORNF", "OEDF", "OFEST",
    ]
    _suma_parciales = sum(_col_sum(c) for c in _cols_verificar)
    _diff = abs(total_horas - _suma_parciales)
    if total_horas > 0 and _diff > 0.5:
        st.warning(
            f"Diferencia de {_diff:,.2f} h entre la suma de columnas parciales "
            f"({_suma_parciales:,.2f} h) y el TOTAL del archivo ({total_horas:,.2f} h). "
            f"Verifique si el archivo tiene columnas adicionales no reconocidas."
        )
    else:
        st.success(
            f"Verificación OK: suma parciales = {_suma_parciales:,.2f} h  "
            f"═  TOTAL archivo = {total_horas:,.2f} h"
        )

    st.divider()

    # ── Tarjeta de detalle por empleado (solo cuando hay uno seleccionado) ──
    if len(sel_personas) != 1:
        return

    emp_name = sel_personas[0]
    st.markdown(f"### Detalle – {emp_name}")

    _detail_cols = [
        c for c in [
            "DO", "RNO", "HEDO", "HENO", "DOM", "RNF",
            "HEDF", "HENF", "FEST", "RNDOM", "RDOM",
            "ODOM", "ORNF", "OEDF", "OFEST", "TOTAL",
        ]
        if c in dff.columns
    ]
    _emp_totals = {c: dff[c].sum() for c in _detail_cols}

    _grupo_map = {
        "DO  – Jornada ordinaria":           ["DO"],
        "RNO – Recargo nocturno ord.":       ["RNO"],
        "HEDO – H. Extra diurna ord.":       ["HEDO"],
        "HENO – H. Extra nocturna ord.":     ["HENO"],
        "DOM  – Dominical":                  ["DOM"],
        "FEST – Festivo":                    ["FEST"],
        "RNF  – Rec. noct. festivo":         ["RNF"],
        "HEDF – H. Extra diurna fest.":      ["HEDF"],
        "HENF – H. Extra noct. fest.":       ["HENF"],
        "RNDOM – Rec. noct. dom.":           ["RNDOM"],
        "RDOM  – Rec. dom.":                 ["RDOM"],
        "Otros recargos":                    ["ODOM", "ORNF", "OEDF", "OFEST"],
    }
    _filas = []
    for grupo, cols_g in _grupo_map.items():
        subtotal = sum(_emp_totals.get(c, 0) for c in cols_g)
        if subtotal > 0:
            _filas.append({
                "Grupo": grupo,
                "Columnas": " + ".join(c for c in cols_g if c in dff.columns),
                "Total horas": round(subtotal, 2),
            })

    _suma_row  = {
        "Grupo": "∑ Suma parciales",
        "Columnas": " + ".join(c for c in _detail_cols if c != "TOTAL"),
        "Total horas": round(sum(v for k, v in _emp_totals.items() if k != "TOTAL"), 2),
    }
    _total_row = {
        "Grupo": "TOTAL GENERAL",
        "Columnas": "TOTAL",
        "Total horas": round(_emp_totals.get("TOTAL", 0), 2),
    }
    _df_detalle = pd.DataFrame(_filas + [_suma_row, _total_row])

    def _color_detalle(row):
        if row["Grupo"] == "TOTAL GENERAL":
            return ["background-color:#8A2F1F; color:white; font-weight:bold"] * len(row)
        if row["Grupo"] == "∑ Suma parciales":
            return ["background-color:#FFF3F0; color:#3D1A0E; font-weight:bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        _df_detalle.style.apply(_color_detalle, axis=1).format({"Total horas": "{:.2f}"}),
        use_container_width=True,
        hide_index=True,
        height=min(80 + len(_df_detalle) * 40, 500),
    )

    # Exportar detalle del empleado
    _buf = io.BytesIO()
    with pd.ExcelWriter(_buf, engine="openpyxl") as _w:
        _df_detalle.to_excel(_w, index=False, sheet_name=f"Detalle {emp_name}"[:31])
    _buf.seek(0)

    st.download_button(
        "Descargar Excel (detalle empleado)",
        icon=":material/download:",
        data=_buf.read(),
        file_name=f"detalle_{emp_name.replace(' ', '_')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_detalle_emp",
    )
    st.divider()
