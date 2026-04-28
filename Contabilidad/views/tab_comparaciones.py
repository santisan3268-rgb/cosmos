"""
views/tab_comparaciones.py – Tab "Comparaciones" (dos períodos libres).
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from conta_core.db_utils import (
    CONCEPTOS_COMPARACION,
    HORAS_EXTRAS,
    MESES_ES,
    calcular_variacion,
    listar_meses_guardados,
    obtener_registro_global,
    obtener_registros_tienda,
)
from conta_core.parser_utils import HORA_COLS


def render() -> None:
    st.subheader("Comparaciones — Horas extras entre períodos")
    st.caption(
        "Compara cualquier par de períodos guardados: mismo mes distinto año, "
        "o dos meses consecutivos del mismo año."
    )

    _meses_db = listar_meses_guardados()
    if _meses_db.empty:
        st.info(
            "No hay registros guardados todavía. Ve al panel izquierdo, sube un archivo, "
            "selecciona Año y Mes, y presiona **Guardar en base de datos**."
        )
        return

    with st.expander(f"Registros guardados ({len(_meses_db)})", expanded=False):
        _mostrar = _meses_db.copy()
        _mostrar["Mes"] = _mostrar["mes"].map(MESES_ES)
        _mostrar = _mostrar[["anio", "Mes", "fecha_carga", "archivo_origen"]].rename(
            columns={"anio": "Año", "fecha_carga": "Cargado", "archivo_origen": "Archivo"}
        )
        st.dataframe(_mostrar, use_container_width=True, hide_index=True)

    if len(_meses_db) < 2:
        st.warning(
            "Necesitas al menos **dos registros guardados** para poder comparar. "
            "Ve al panel izquierdo, carga otro mes y présiona **Guardar en BD**."
        )
        return

    # ── Selección de períodos ──
    _periodos = [
        (int(row["anio"]), int(row["mes"]))
        for _, row in _meses_db.sort_values(["anio", "mes"], ascending=[False, False]).iterrows()
    ]
    _periodo_labels = {(a, m): f"{MESES_ES[m]} {a}" for a, m in _periodos}

    st.markdown("#### Selección de períodos a comparar")
    _csel1, _csel2 = st.columns(2)
    with _csel1:
        _per_a = st.selectbox(
            "Período A (referencia)",
            options=_periodos,
            format_func=lambda p: _periodo_labels[p],
            index=min(1, len(_periodos) - 1),
            key="cmp_per_a",
        )
    with _csel2:
        _opciones_b = [p for p in _periodos if p != _per_a]
        _per_b = st.selectbox(
            "Período B (a comparar)",
            options=_opciones_b,
            format_func=lambda p: _periodo_labels[p],
            index=0,
            key="cmp_per_b",
        )
    _anio_a, _mes_a = _per_a
    _anio_b, _mes_b = _per_b

    _reg_a = obtener_registro_global(_anio_a, _mes_a)
    _reg_b = obtener_registro_global(_anio_b, _mes_b)

    if _reg_a is None or _reg_b is None:
        st.error("No se pudo recuperar uno de los registros seleccionados.")
        return

    _label_a = f"{MESES_ES[_mes_a]} {_anio_a}"
    _label_b = f"{MESES_ES[_mes_b]} {_anio_b}"

    # ── Tarjetas resumen ──
    _total_a = float(_reg_a.get("TOTAL", 0) or 0)
    _total_b = float(_reg_b.get("TOTAL", 0) or 0)
    _ext_a   = sum(float(_reg_a.get(c, 0) or 0) for c in HORAS_EXTRAS)
    _ext_b   = sum(float(_reg_b.get(c, 0) or 0) for c in HORAS_EXTRAS)
    _var_total = calcular_variacion(_total_a, _total_b)
    _var_ext   = calcular_variacion(_ext_a, _ext_b)

    _kpi1, _kpi2, _kpi3, _kpi4 = st.columns(4)
    _kpi1.metric(f"TOTAL horas {_label_a}", f"{_total_a:,.2f}")
    _kpi2.metric(
        f"TOTAL horas {_label_b}", f"{_total_b:,.2f}",
        delta=f"{_var_total['diff']:+,.2f} h ({_var_total['pct']:+.2f}%)",
    )
    _kpi3.metric(f"Horas extras {_label_a}", f"{_ext_a:,.2f}")
    _kpi4.metric(
        f"Horas extras {_label_b}", f"{_ext_b:,.2f}",
        delta=f"{_var_ext['diff']:+,.2f} h ({_var_ext['pct']:+.2f}%)",
    )

    # ── Tabla de variaciones por concepto ──
    st.markdown("#### Variación por concepto")
    _filas_var = []
    for _c in CONCEPTOS_COMPARACION:
        _va = float(_reg_a.get(_c, 0) or 0)
        _vb = float(_reg_b.get(_c, 0) or 0)
        _v  = calcular_variacion(_va, _vb)
        _grupo = "Hora extra" if _c in HORAS_EXTRAS else "Recargo"
        _filas_var.append({
            "Categoría":   _grupo,
            "Concepto":    _c,
            "Descripción": HORA_COLS.get(_c, ""),
            _label_a:      round(_va, 2),
            _label_b:      round(_vb, 2),
            "Δ horas":     _v["diff"],
            "Δ %":         _v["pct"],
            "Estado":      _v["estado"].replace("_", " ").capitalize(),
        })
    _df_var = pd.DataFrame(_filas_var)

    def _color_estado(val: str) -> str:
        if "crecio" in str(val).lower():
            return "color: #1f9d55; font-weight: 600"
        if "bajo" in str(val).lower():
            return "color: #d62728; font-weight: 600"
        return "color: #6b6b6b"

    st.dataframe(
        _df_var.style
            .format({_label_a: "{:.2f}", _label_b: "{:.2f}", "Δ horas": "{:+.2f}", "Δ %": "{:+.2f}"})
            .map(_color_estado, subset=["Estado"]),
        use_container_width=True, hide_index=True,
    )

    # ── Resumen narrativo ──
    _crecieron  = _df_var[_df_var["Estado"].str.contains("crecio",  case=False)]["Concepto"].tolist()
    _bajaron    = _df_var[_df_var["Estado"].str.contains("bajo",    case=False)]["Concepto"].tolist()
    _sostenidos = _df_var[_df_var["Estado"].str.contains("sostuvo", case=False)]["Concepto"].tolist()
    _r1, _r2, _r3 = st.columns(3)
    _r1.success(f"Crecieron ({len(_crecieron)}): "   + (", ".join(_crecieron)  or "—"))
    _r2.error(  f"Bajaron ({len(_bajaron)}): "        + (", ".join(_bajaron)    or "—"))
    _r3.info(   f"Se sostuvieron ({len(_sostenidos)}): " + (", ".join(_sostenidos) or "—"))

    # ── Gráfica 1: barras agrupadas A vs B por concepto ──
    st.markdown("#### Gráfica 1 · Horas extras y recargos por concepto")
    _df_long = _df_var.melt(
        id_vars=["Concepto", "Categoría"],
        value_vars=[_label_a, _label_b],
        var_name="Periodo", value_name="Horas",
    )
    fig_cmp = px.bar(
        _df_long, x="Concepto", y="Horas", color="Periodo",
        barmode="group", text="Horas",
        color_discrete_map={_label_a: "#A68070", _label_b: "#9C4A38"},
        height=420,
    )
    fig_cmp.update_traces(texttemplate="%{text:.0f}", textposition="outside")
    fig_cmp.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="", margin=dict(t=30, b=40, l=20, r=20),
        xaxis=dict(gridcolor="rgba(128,128,128,0.25)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    )
    st.plotly_chart(fig_cmp, use_container_width=True)

    # ── Gráfica 2: variación % por concepto ──
    st.markdown("#### Gráfica 2 · Variación % por concepto")
    _df_pct = _df_var.copy()
    _df_pct["Color"] = _df_pct["Estado"].apply(
        lambda s: "#1f9d55" if "crecio" in str(s).lower()
        else ("#d62728" if "bajo" in str(s).lower() else "#9e9e9e")
    )
    _df_pct = _df_pct.sort_values("Δ %", ascending=True)
    fig_var = go.Figure(
        go.Bar(
            x=_df_pct["Δ %"], y=_df_pct["Concepto"],
            orientation="h", marker_color=_df_pct["Color"],
            text=[f"{v:+.1f}%" for v in _df_pct["Δ %"]],
            textposition="outside",
        )
    )
    fig_var.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        height=420,
        xaxis_title=f"Δ % ({_label_b} vs {_label_a})", yaxis_title="",
        margin=dict(t=30, b=40, l=20, r=40),
        xaxis=dict(gridcolor="rgba(128,128,128,0.25)", zerolinecolor="rgba(128,128,128,0.4)"),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    )
    fig_var.add_vline(x=0, line_color="rgba(128,128,128,0.6)", line_width=1)
    st.plotly_chart(fig_var, use_container_width=True)

    # ── Comparación por tienda ──
    st.markdown("#### Comparación por tienda")
    _tdf_a = obtener_registros_tienda(_anio_a, _mes_a)
    _tdf_b = obtener_registros_tienda(_anio_b, _mes_b)

    if _tdf_a.empty and _tdf_b.empty:
        st.info("No se guardaron datos por tienda para estos meses.")
        return

    _tdf_a["Extras"] = _tdf_a[HORAS_EXTRAS].sum(axis=1) if not _tdf_a.empty else 0
    _tdf_b["Extras"] = _tdf_b[HORAS_EXTRAS].sum(axis=1) if not _tdf_b.empty else 0

    _agg_a = _tdf_a[["tienda", "Extras"]].rename(columns={"Extras": _label_a}) if not _tdf_a.empty else pd.DataFrame(columns=["tienda", _label_a])
    _agg_b = _tdf_b[["tienda", "Extras"]].rename(columns={"Extras": _label_b}) if not _tdf_b.empty else pd.DataFrame(columns=["tienda", _label_b])
    _tienda_cmp = _agg_a.merge(_agg_b, on="tienda", how="outer").fillna(0)
    _tienda_cmp["Δ horas extras"] = (_tienda_cmp[_label_b] - _tienda_cmp[_label_a]).round(2)
    _tienda_cmp["Δ %"] = _tienda_cmp.apply(
        lambda r: 0.0 if r[_label_a] == 0 else round((r["Δ horas extras"] / r[_label_a]) * 100, 2),
        axis=1,
    )
    _tienda_cmp = _tienda_cmp.sort_values(_label_b, ascending=False).rename(columns={"tienda": "Tienda"})

    _top_a = _tienda_cmp.sort_values(_label_a, ascending=False).head(1)
    _top_b = _tienda_cmp.sort_values(_label_b, ascending=False).head(1)
    _i1, _i2 = st.columns(2)
    if not _top_a.empty:
        _i1.info(
            f"En **{_label_a}** la tienda con más horas extras fue "
            f"**{_top_a.iloc[0]['Tienda']}** ({_top_a.iloc[0][_label_a]:,.2f} h)."
        )
    if not _top_b.empty:
        _i2.info(
            f"En **{_label_b}** la tienda con más horas extras fue "
            f"**{_top_b.iloc[0]['Tienda']}** ({_top_b.iloc[0][_label_b]:,.2f} h)."
        )

    st.dataframe(
        _tienda_cmp.style.format(
            {_label_a: "{:.2f}", _label_b: "{:.2f}", "Δ horas extras": "{:+.2f}", "Δ %": "{:+.2f}"}
        ),
        use_container_width=True, hide_index=True,
    )

    _tienda_long = _tienda_cmp.melt(
        id_vars=["Tienda"],
        value_vars=[_label_a, _label_b],
        var_name="Periodo", value_name="Horas extras",
    )
    fig_tienda = px.bar(
        _tienda_long, x="Horas extras", y="Tienda", color="Periodo",
        orientation="h", barmode="group",
        color_discrete_map={_label_a: "#A68070", _label_b: "#9C4A38"},
        height=max(360, 30 * len(_tienda_cmp) + 120),
    )
    fig_tienda.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="", margin=dict(t=30, b=40, l=20, r=40),
        xaxis=dict(
            gridcolor="rgba(128,128,128,0.25)",
            zerolinecolor="rgba(128,128,128,0.4)",
        ),
        yaxis=dict(gridcolor="rgba(128,128,128,0.15)"),
    )
    st.plotly_chart(fig_tienda, use_container_width=True)
