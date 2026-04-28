"""
views/tab_cumplimiento.py – Tab "Cumplimiento Ley 2466".
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from conta_core.export_utils import calcular_cumplimiento, df_to_excel_grouped, excel_cumplimiento


def render(dff: pd.DataFrame) -> None:
    st.subheader("Cumplimiento normativo – Horas extras")
    st.markdown(
        """
        **Norma aplicada:** Ley 2466 de 2025 / Código Sustantivo del Trabajo
        - Máximo **2 horas extras** por día por empleado.
        - Máximo **12 horas extras** por semana por empleado.

        Las filas resaltadas indican incumplimiento del límite legal.
        """,
    )

    cump_diario, cump_semanal = calcular_cumplimiento(dff)

    for _col in ["H. Extra del dia", "Exceso diario"]:
        if _col in cump_diario.columns:
            cump_diario[_col] = cump_diario[_col].round(2)
    for _col in ["H. Extra semana", "Exceso semanal"]:
        if _col in cump_semanal.columns:
            cump_semanal[_col] = cump_semanal[_col].round(2)

    # Versiones sin filtro de empleado (para análisis por tienda)
    _cump_dia_all = cump_diario.copy()
    _cump_sem_all = cump_semanal.copy()

    _nombre_grupo = (
        dff[["Nombre", "Grupo"]].drop_duplicates()
        .set_index("Nombre")["Grupo"].to_dict()
    )
    _cump_dia_all["Tienda"] = _cump_dia_all["Nombre"].map(_nombre_grupo).fillna("(Sin grupo)")
    _cump_sem_all["Tienda"] = _cump_sem_all["Nombre"].map(_nombre_grupo).fillna("(Sin grupo)")

    # ── Filtro por empleado ──
    per_cump = st.selectbox(
        "Filtrar empleado",
        ["Todos"] + sorted(dff["Nombre"].unique()),
        key="sel_cump",
    )
    if per_cump != "Todos":
        cump_diario  = cump_diario[cump_diario["Nombre"] == per_cump]
        cump_semanal = cump_semanal[cump_semanal["Nombre"] == per_cump]

    # ── Resumen de alertas ──
    n_excesos_dia = (cump_diario["Estado"] == "EXCEDE LIMITE").sum()
    n_excesos_sem = (cump_semanal["Estado"] == "EXCEDE LIMITE").sum()
    c1, c2 = st.columns(2)
    with c1:
        if n_excesos_dia > 0:
            st.error(f"{n_excesos_dia} día(s) con más de 2 h extras")
        else:
            st.success("Sin infracciones diarias")
    with c2:
        if n_excesos_sem > 0:
            st.error(f"{n_excesos_sem} semana(s) con más de 12 h extras")
        else:
            st.success("Sin infracciones semanales")

    solo_incumplimientos = st.toggle(
        "Mostrar solo incumplimientos",
        value=True,
        help="Activa para ver únicamente los registros que exceden el límite legal.",
    )

    def _color_estado(val: str) -> str:
        if "EXCEDE" in str(val):
            return "background-color: #FFEBEE; color: #B71C1C; font-weight: bold"
        return "background-color: #E8F5E9; color: #1B5E20"

    def _color_tienda(row):
        return ["background-color:#FFEBEE; color:#B71C1C; font-weight:bold"] * len(row)

    # ── Tabla diaria ──
    st.markdown("#### Detalle diario")
    disp_dia = cump_diario.copy()
    if solo_incumplimientos:
        disp_dia = disp_dia[disp_dia["Estado"] == "EXCEDE LIMITE"]
    if per_cump != "Todos":
        disp_dia = disp_dia.drop(columns=["Nombre"])
    if disp_dia.empty:
        st.success("Sin infracciones diarias en el período seleccionado.")
    else:
        _num_dia_c = [c for c in disp_dia.columns if disp_dia[c].dtype.kind in ("f", "i")]
        st.dataframe(
            disp_dia.style
                .format({c: "{:.2f}" for c in _num_dia_c})
                .map(_color_estado, subset=["Estado"]),
            use_container_width=True,
            height=min(60 + len(disp_dia) * 36, 420),
        )
        _xlsx_cump_dia = df_to_excel_grouped(
            disp_dia.reset_index(drop=True), "Cumplimiento diario", group_col="_none_"
        )
        st.download_button(
            "Descargar Excel (diario)", icon=":material/download:",
            data=_xlsx_cump_dia,
            file_name="cumplimiento_diario.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_cump_dia",
        )

    # ── Tabla semanal ──
    st.markdown("#### Detalle semanal")
    disp_sem = cump_semanal.copy()
    if solo_incumplimientos:
        disp_sem = disp_sem[disp_sem["Estado"] == "EXCEDE LIMITE"]
    if per_cump != "Todos":
        disp_sem = disp_sem.drop(columns=["Nombre"])
    if disp_sem.empty:
        st.success("Sin infracciones semanales en el período seleccionado.")
    else:
        _num_sem_c = [c for c in disp_sem.columns if disp_sem[c].dtype.kind in ("f", "i")]
        st.dataframe(
            disp_sem.style
                .format({c: "{:.2f}" for c in _num_sem_c})
                .map(_color_estado, subset=["Estado"]),
            use_container_width=True,
            height=min(60 + len(disp_sem) * 36, 360),
        )
        _xlsx_cump_sem = df_to_excel_grouped(
            disp_sem.reset_index(drop=True), "Cumplimiento semanal", group_col="_none_"
        )
        st.download_button(
            "Descargar Excel (semanal)", icon=":material/download:",
            data=_xlsx_cump_sem,
            file_name="cumplimiento_semanal.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_cump_sem",
        )

    # ── Descarga Excel doble hoja (sin filtro de empleado) ──
    xlsx_cump = excel_cumplimiento(cump_diario, cump_semanal)
    st.download_button(
        label="Descargar reporte de cumplimiento (Excel)",
        icon=":material/download:",
        data=xlsx_cump,
        file_name="cumplimiento_horas_extras.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # ── Análisis de incumplimiento por Tienda ──
    st.divider()
    st.markdown("### Incumplimiento por Tienda")
    st.caption("Consolidado de infracciones de horas extras agrupado por tienda/grupo.")

    _exc_dia_tienda = (
        _cump_dia_all[_cump_dia_all["Estado"] == "EXCEDE LIMITE"]
        .groupby("Tienda")
        .agg(
            Infracciones_diarias=("Nombre", "count"),
            Empleados_con_exceso=("Nombre", "nunique"),
            Exceso_total_horas=("Exceso diario", "sum"),
        )
        .reset_index()
        .sort_values("Infracciones_diarias", ascending=False)
        .reset_index(drop=True)
    )
    _exc_dia_tienda["Exceso_total_horas"] = _exc_dia_tienda["Exceso_total_horas"].round(2)

    _exc_sem_tienda = (
        _cump_sem_all[_cump_sem_all["Estado"] == "EXCEDE LIMITE"]
        .groupby("Tienda")
        .agg(
            Infracciones_semanales=("Nombre", "count"),
            Empleados_con_exceso=("Nombre", "nunique"),
            Exceso_total_horas=("Exceso semanal", "sum"),
        )
        .reset_index()
        .sort_values("Infracciones_semanales", ascending=False)
        .reset_index(drop=True)
    )
    _exc_sem_tienda["Exceso_total_horas"] = _exc_sem_tienda["Exceso_total_horas"].round(2)

    _t_inf1, _t_inf2 = st.columns(2)
    with _t_inf1:
        if len(_exc_dia_tienda) > 0:
            st.error(f"{len(_exc_dia_tienda)} tienda(s) con infracciones diarias")
        else:
            st.success("Ninguna tienda supera el límite diario")
    with _t_inf2:
        if len(_exc_sem_tienda) > 0:
            st.error(f"{len(_exc_sem_tienda)} tienda(s) con infracciones semanales")
        else:
            st.success("Ninguna tienda supera el límite semanal")

    _sub_tienda = st.tabs([
        "Infracciones diarias por tienda",
        "Infracciones semanales por tienda",
    ])

    # ── Subtab: Diario ──
    with _sub_tienda[0]:
        if _exc_dia_tienda.empty:
            st.success("Ninguna tienda con infracciones diarias.")
        else:
            _fig_h_dia = max(300, len(_exc_dia_tienda) * 48 + 80)
            _fig_tid = px.bar(
                _exc_dia_tienda.sort_values("Infracciones_diarias"),
                x="Infracciones_diarias", y="Tienda", orientation="h",
                color="Infracciones_diarias",
                color_continuous_scale=[[0, "#FFEBEE"], [0.5, "#EF9A9A"], [1, "#B71C1C"]],
                text="Infracciones_diarias", height=_fig_h_dia,
                labels={"Infracciones_diarias": "N° infracciones", "Tienda": "Tienda"},
                title="Tiendas con infracciones diarias (> 2 h extras/día)",
            )
            _fig_tid.update_traces(textposition="outside")
            _fig_tid.update_layout(
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_size=12, margin=dict(l=10, r=60, t=50, b=30),
            )
            st.plotly_chart(_fig_tid, use_container_width=True)

            st.markdown("##### Detalle por tienda")
            _exc_dia_tienda.insert(0, "#", range(1, len(_exc_dia_tienda) + 1))
            _exc_dia_tienda_disp = _exc_dia_tienda.rename(columns={
                "Infracciones_diarias": "N° infracciones",
                "Empleados_con_exceso": "Empleados afectados",
                "Exceso_total_horas": "Total horas exceso",
            })
            st.dataframe(
                _exc_dia_tienda_disp.style
                    .apply(_color_tienda, axis=1)
                    .format({"Total horas exceso": "{:.2f}"}),
                use_container_width=True, hide_index=True,
                height=min(80 + len(_exc_dia_tienda_disp) * 38, 420),
            )
            _xlsx_tienda_dia = df_to_excel_grouped(
                _exc_dia_tienda_disp.drop(columns=["#"]),
                "Infracciones diarias por tienda", group_col="_none_",
            )
            st.download_button(
                "Descargar Excel (infracciones diarias por tienda)",
                icon=":material/download:", data=_xlsx_tienda_dia,
                file_name="infracciones_diarias_tienda.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_inf_dia_tienda",
            )

            st.markdown("##### Empleados con infracciones diarias por tienda")
            _tiendas_inf_dia = ["Todas"] + sorted(
                _cump_dia_all[_cump_dia_all["Estado"] == "EXCEDE LIMITE"]["Tienda"].unique()
            )
            _sel_t_dia = st.selectbox("Ver tienda", _tiendas_inf_dia, key="sel_tienda_inf_dia")
            _det_emp_dia = _cump_dia_all[_cump_dia_all["Estado"] == "EXCEDE LIMITE"].copy()
            if _sel_t_dia != "Todas":
                _det_emp_dia = _det_emp_dia[_det_emp_dia["Tienda"] == _sel_t_dia]
            _det_emp_dia = _det_emp_dia.sort_values(["Tienda", "Nombre", "Fecha"]).reset_index(drop=True)
            _num_det_dia = [c for c in _det_emp_dia.columns if _det_emp_dia[c].dtype.kind in ("f", "i")]
            st.dataframe(
                _det_emp_dia.style
                    .format({c: "{:.2f}" for c in _num_det_dia})
                    .map(_color_estado, subset=["Estado"]),
                use_container_width=True,
                height=min(80 + len(_det_emp_dia) * 36, 420),
            )

    # ── Subtab: Semanal ──
    with _sub_tienda[1]:
        if _exc_sem_tienda.empty:
            st.success("Ninguna tienda con infracciones semanales.")
        else:
            _fig_h_sem = max(300, len(_exc_sem_tienda) * 48 + 80)
            _fig_tis = px.bar(
                _exc_sem_tienda.sort_values("Infracciones_semanales"),
                x="Infracciones_semanales", y="Tienda", orientation="h",
                color="Infracciones_semanales",
                color_continuous_scale=[[0, "#FFEBEE"], [0.5, "#EF9A9A"], [1, "#B71C1C"]],
                text="Infracciones_semanales", height=_fig_h_sem,
                labels={"Infracciones_semanales": "N° infracciones", "Tienda": "Tienda"},
                title="Tiendas con infracciones semanales (> 12 h extras/semana)",
            )
            _fig_tis.update_traces(textposition="outside")
            _fig_tis.update_layout(
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font_size=12, margin=dict(l=10, r=60, t=50, b=30),
            )
            st.plotly_chart(_fig_tis, use_container_width=True)

            st.markdown("##### Detalle por tienda")
            _exc_sem_tienda.insert(0, "#", range(1, len(_exc_sem_tienda) + 1))
            _exc_sem_tienda_disp = _exc_sem_tienda.rename(columns={
                "Infracciones_semanales": "N° infracciones",
                "Empleados_con_exceso": "Empleados afectados",
                "Exceso_total_horas": "Total horas exceso",
            })
            st.dataframe(
                _exc_sem_tienda_disp.style
                    .apply(_color_tienda, axis=1)
                    .format({"Total horas exceso": "{:.2f}"}),
                use_container_width=True, hide_index=True,
                height=min(80 + len(_exc_sem_tienda_disp) * 38, 420),
            )
            _xlsx_tienda_sem = df_to_excel_grouped(
                _exc_sem_tienda_disp.drop(columns=["#"]),
                "Infracciones semanales por tienda", group_col="_none_",
            )
            st.download_button(
                "Descargar Excel (infracciones semanales por tienda)",
                icon=":material/download:", data=_xlsx_tienda_sem,
                file_name="infracciones_semanales_tienda.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="dl_inf_sem_tienda",
            )

            st.markdown("##### Empleados con infracciones semanales por tienda")
            _tiendas_inf_sem = ["Todas"] + sorted(
                _cump_sem_all[_cump_sem_all["Estado"] == "EXCEDE LIMITE"]["Tienda"].unique()
            )
            _sel_t_sem = st.selectbox("Ver tienda", _tiendas_inf_sem, key="sel_tienda_inf_sem")
            _det_emp_sem = _cump_sem_all[_cump_sem_all["Estado"] == "EXCEDE LIMITE"].copy()
            if _sel_t_sem != "Todas":
                _det_emp_sem = _det_emp_sem[_det_emp_sem["Tienda"] == _sel_t_sem]
            _det_emp_sem = _det_emp_sem.sort_values(["Tienda", "Nombre"]).reset_index(drop=True)
            _num_det_sem = [c for c in _det_emp_sem.columns if _det_emp_sem[c].dtype.kind in ("f", "i")]
            st.dataframe(
                _det_emp_sem.style
                    .format({c: "{:.2f}" for c in _num_det_sem})
                    .map(_color_estado, subset=["Estado"]),
                use_container_width=True,
                height=min(80 + len(_det_emp_sem) * 36, 420),
            )
