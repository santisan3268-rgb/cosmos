"""
sidebar_components.py — Componentes del panel lateral
=======================================================
Funciones puras que renderizan cada sección del sidebar.
Se importan en app.py para mantener el flujo principal limpio.
"""

import base64
import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from conta_core.db_utils import MESES_ES, listar_meses_guardados
from conta_core.parser_utils import HORA_COLS

# ─────────────────────────────────────────────────────────────────
# Rutas de assets
# ─────────────────────────────────────────────────────────────────
_BASE = Path(__file__).parent
LOGO_PATH = _BASE / "COSMOS.jpg.jpeg"
ISOTIPO_PATH = _BASE / "isotipo-png.png"


# ─────────────────────────────────────────────────────────────────
# 1. BRAND HEADER
# ─────────────────────────────────────────────────────────────────
def render_brand() -> None:
    """Renderiza la zona de marca en la parte superior del sidebar."""
    if ISOTIPO_PATH.exists():
        isotipo_b64 = base64.b64encode(ISOTIPO_PATH.read_bytes()).decode()
        brand_img = (
            f"<img src='data:image/png;base64,{isotipo_b64}' "
            f"class='sb-brand__logo' alt='FYC'>"
        )
    else:
        brand_img = "<div class='sb-brand__logo sb-brand__logo--text'>FYC</div>"

    st.markdown(
        f"""
        <div class='sb-brand'>
            <div class='sb-brand__mark'>{brand_img}</div>
            <div class='sb-brand__copy'>
                <div class='sb-brand__title'>FYC Calzado</div>
                <div class='sb-brand__sub'>Reportes de labor</div>
            </div>
            <div class='sb-brand__dot' aria-hidden='true'></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────
# 2. SECCIÓN DE CARGA DE DATOS
# ─────────────────────────────────────────────────────────────────
def upload_section():
    """
    Renderiza el uploader de archivo y los botones de control.

    Returns
    -------
    uploaded_file | None
    """
    st.markdown("#### Datos de Origen")

    uploaded_file = st.file_uploader(
        "Archivo Excel de Siesa",
        type=["xlsx"],
        help="El archivo solo se usa para el análisis temporal actual.",
        label_visibility="collapsed",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "Recargar",
            icon=":material/refresh:",
            use_container_width=True,
            help="Actualiza el dashboard",
            key="btn_reload",
            type="secondary",
        ):
            st.rerun()
    with col2:
        if st.button(
            "Limpiar",
            icon=":material/delete_outline:",
            use_container_width=True,
            help="Elimina el archivo cargado",
            key="btn_clear_file",
            type="secondary",
        ):
            for k in list(st.session_state.keys()):
                if "file_uploader" in k or "uploaded_file" in k:
                    del st.session_state[k]
            st.rerun()

    label = uploaded_file.name if uploaded_file else "Ninguno"
    st.caption(f"Archivo en memoria: **{label}**")

    return uploaded_file


# ─────────────────────────────────────────────────────────────────
# 3. SECCIÓN DE REGISTRO HISTÓRICO
# ─────────────────────────────────────────────────────────────────
def historial_section(uploaded_file) -> None:
    """
    Renderiza el expander de registro histórico en BD.
    Escribe ``st.session_state["_pending_save"]`` cuando el usuario confirma.
    """
    st.write("")
    with st.expander("Registro Histórico", icon=":material/database:"):
        st.caption("Guarda totales para comparaciones.")
        _today = pd.Timestamp.today()
        _anio_opciones = list(range(_today.year - 5, _today.year + 2))

        col_a, col_m = st.columns(2)
        with col_a:
            anio = st.selectbox(
                "Año",
                options=_anio_opciones,
                index=_anio_opciones.index(_today.year),
                key="db_anio_sel",
            )
        with col_m:
            mes = st.selectbox(
                "Mes",
                options=list(range(1, 13)),
                index=_today.month - 1,
                format_func=lambda m: MESES_ES[m],
                key="db_mes_sel",
            )

        if st.button(
            "Guardar en BD",
            icon=":material/save:",
            use_container_width=True,
            disabled=uploaded_file is None,
            type="primary",
            key="btn_guardar_bd",
        ):
            st.session_state["_pending_save"] = {
                "anio": anio,
                "mes": mes,
                "archivo": uploaded_file.name if uploaded_file else "",
            }
            st.success("Registro preparado para guardar.")


def archivos_subidos_section() -> tuple[int, int] | None:
    """Muestra registros guardados y permite seleccionar uno para cargar en la vista."""
    st.write("")
    with st.expander("Archivos ya subidos (BD)", icon=":material/folder_managed:"):
        try:
            hist = listar_meses_guardados()
        except Exception as exc:
            st.error(f"No se pudo leer la base de datos: {exc}")
            return None

        if hist.empty:
            st.caption("Aún no hay registros guardados en la base de datos.")
            return None

        hist = hist.copy()
        hist["periodo"] = hist["mes"].map(MESES_ES).fillna(hist["mes"].astype(str)) + " " + hist["anio"].astype(str)
        hist["archivo"] = hist["archivo_origen"].fillna("").replace("", "(Sin nombre)")

        if "fecha_carga" in hist.columns:
            dt = pd.to_datetime(hist["fecha_carga"], errors="coerce")
            hist["fecha"] = dt.dt.strftime("%Y-%m-%d %H:%M").fillna("-")
        else:
            hist["fecha"] = "-"

        total = len(hist)
        ultima_fecha = hist.iloc[0]["fecha"] if total > 0 else "-"
        st.caption(f"Registros guardados: **{total}** · Último: {ultima_fecha}")

        # Período activo actual
        actual = st.session_state.get("_selected_db_period")
        active_tuple = (
            (int(actual["anio"]), int(actual["mes"]))
            if isinstance(actual, dict) else None
        )

        # Tabla interactiva: columna "Abrir" como checkbox integrado
        hist["_abrir"] = hist.apply(
            lambda r: active_tuple == (int(r["anio"]), int(r["mes"])), axis=1
        )
        vista_edit = hist[["_abrir", "periodo", "archivo", "fecha"]].rename(
            columns={"_abrir": "Abrir", "periodo": "Período", "archivo": "Archivo", "fecha": "Subido"}
        ).reset_index(drop=True)

        resultado = st.data_editor(
            vista_edit,
            column_config={
                "Abrir": st.column_config.CheckboxColumn(
                    "↗",
                    help="Marca para abrir este período desde la BD",
                    default=False,
                    width="small",
                ),
                "Período": st.column_config.TextColumn(disabled=True, width="medium"),
                "Archivo": st.column_config.TextColumn(disabled=True, width="medium"),
                "Subido": st.column_config.TextColumn(disabled=True, width="medium"),
            },
            hide_index=True,
            use_container_width=True,
            height=min(220, 38 + 35 * total),
            key="data_editor_bd_hist",
        )

        # Detectar cambio en los checkboxes
        for idx, edit_row in resultado.iterrows():
            orig_row = hist.iloc[idx]
            key = (int(orig_row["anio"]), int(orig_row["mes"]))
            was_active = active_tuple == key
            is_checked = bool(edit_row["Abrir"])
            if is_checked and not was_active:
                # Usuario marcó una nueva fila → abrir ese período
                st.session_state["_selected_db_period"] = {
                    "anio": key[0],
                    "mes": key[1],
                }
                st.session_state.pop("_pending_save", None)
                st.rerun()
            elif not is_checked and was_active:
                # Usuario desmarcó el período activo → cerrar
                st.session_state.pop("_selected_db_period", None)
                st.rerun()

    selected = st.session_state.get("_selected_db_period")
    if isinstance(selected, dict) and "anio" in selected and "mes" in selected:
        return int(selected["anio"]), int(selected["mes"])
    return None


# ─────────────────────────────────────────────────────────────────
# 4. SECCIÓN DE FILTROS (tiendas + empleados + fechas)
# ─────────────────────────────────────────────────────────────────
def filtros_section(df: pd.DataFrame) -> dict:
    """
    Renderiza filtros de fechas, tiendas y empleados.

    Returns
    -------
    dict con claves: fecha_ini, fecha_fin, sel_grupos, sel_personas
    """
    min_fecha = df["Fecha"].min().date()
    max_fecha = df["Fecha"].max().date()
    grupos_raw = sorted(df["Grupo"].fillna("(Sin grupo)").unique())
    personas_all = sorted(df["Nombre"].unique())

    # ── Callbacks (modifican session_state ANTES de que los widgets se rendericen) ──
    def _reset_all():
        st.session_state["sel_grupos_ms"] = grupos_raw
        st.session_state["sel_personas_ms"] = personas_all
        st.session_state["_rango_fechas"] = (min_fecha, max_fecha)

    def _preset_este_mes():
        _hoy = datetime.date.today()
        st.session_state["_rango_fechas"] = (
            max(min_fecha, _hoy.replace(day=1)),
            min(max_fecha, _hoy),
        )

    def _preset_mes_ant():
        _hoy = datetime.date.today()
        _primer_actual = _hoy.replace(day=1)
        _fin_ant = _primer_actual - datetime.timedelta(days=1)
        _ini_ant = _fin_ant.replace(day=1)
        st.session_state["_rango_fechas"] = (
            max(min_fecha, _ini_ant),
            min(max_fecha, _fin_ant),
        )

    def _preset_completo():
        st.session_state["_rango_fechas"] = (min_fecha, max_fecha)

    def _set_grupos_todas():
        st.session_state["sel_grupos_ms"] = grupos_raw

    def _set_grupos_ninguna():
        st.session_state["sel_grupos_ms"] = []

    def _set_personas_todos():
        sel_g = st.session_state.get("sel_grupos_ms", grupos_raw)
        _df_f = df[df["Grupo"].fillna("(Sin grupo)").isin(sel_g)]
        st.session_state["sel_personas_ms"] = sorted(_df_f["Nombre"].unique())

    def _set_personas_ninguna():
        st.session_state["sel_personas_ms"] = []

    # ── Encabezado + Reiniciar ──────────────────────────────
    _hdr, _btn = st.columns([5, 1])
    _hdr.markdown("#### Filtros")
    _btn.button(
        "",
        icon=":material/filter_alt_off:",
        use_container_width=True,
        key="btn_clear_all_filters",
        type="secondary",
        help="Reiniciar todos los filtros",
        on_click=_reset_all,
    )

    # ── Fechas ──────────────────────────────────────────────
    st.caption("Período")
    _p1, _p2, _p3 = st.columns(3)
    with _p1:
        st.button("Este mes", key="preset_este_mes", use_container_width=True, on_click=_preset_este_mes)
    with _p2:
        st.button("Mes previo", key="preset_mes_ant", use_container_width=True, on_click=_preset_mes_ant)
    with _p3:
        st.button("Completo", key="preset_todo", use_container_width=True, on_click=_preset_completo)

    # Inicializar rango si no existe
    if "_rango_fechas" not in st.session_state:
        st.session_state["_rango_fechas"] = (min_fecha, max_fecha)

    # Clampear al rango disponible en los datos
    _r = st.session_state["_rango_fechas"]
    _r_clamped = (
        max(min_fecha, min(_r[0], max_fecha)),
        max(min_fecha, min(_r[1], max_fecha)),
    )

    rango = st.date_input(
        "Rango de Fechas",
        value=_r_clamped,
        min_value=min_fecha,
        max_value=max_fecha,
        label_visibility="collapsed",
        key="_rango_fechas",
    )
    if isinstance(rango, (list, tuple)) and len(rango) == 2:
        fecha_ini, fecha_fin = rango
    else:
        fecha_ini = fecha_fin = rango if not isinstance(rango, (list, tuple)) else min_fecha

    st.write("")

    # ── Tiendas / Grupos ────────────────────────────────────
    # Sólo inicializar si la clave no existe todavía (primera carga).
    # No se escribe sobre una clave ya ligada a un widget: los cambios
    # posteriores se hacen únicamente desde los callbacks on_click.
    if "sel_grupos_ms" not in st.session_state:
        st.session_state["sel_grupos_ms"] = grupos_raw

    # Badge: calcular conteo desde session_state (antes del widget)
    _n_g = len([g for g in st.session_state.get("sel_grupos_ms", grupos_raw) if g in grupos_raw])
    _g_hdr, _g_tag = st.columns([3, 1])
    _g_hdr.caption("Tiendas / Grupos")
    _g_tag.markdown(
        f"<div class='filter-badge'>{_n_g}/{len(grupos_raw)}</div>",
        unsafe_allow_html=True,
    )

    sel_grupos = st.multiselect(
        "Tienda(s) / Grupo(s)",
        grupos_raw,
        key="sel_grupos_ms",
        label_visibility="collapsed",
    )

    bt1, bt2 = st.columns(2)
    with bt1:
        st.button(
            "Todas",
            icon=":material/done_all:",
            key="btn_all_grupos",
            use_container_width=True,
            on_click=_set_grupos_todas,
        )
    with bt2:
        st.button(
            "Ninguna",
            icon=":material/clear_all:",
            key="btn_none_grupos",
            use_container_width=True,
            on_click=_set_grupos_ninguna,
        )

    # ── Empleados ───────────────────────────────────────────
    df_por_tienda = df[df["Grupo"].fillna("(Sin grupo)").isin(sel_grupos)]
    personas = sorted(df_por_tienda["Nombre"].unique())

    # Sólo inicializar si la clave no existe todavía.
    if "sel_personas_ms" not in st.session_state:
        st.session_state["sel_personas_ms"] = personas

    _n_p = len([p for p in st.session_state.get("sel_personas_ms", personas) if p in personas])
    _p_hdr, _p_tag = st.columns([3, 1])
    _p_hdr.caption("Empleados")
    _p_tag.markdown(
        f"<div class='filter-badge'>{_n_p}/{len(personas)}</div>",
        unsafe_allow_html=True,
    )

    sel_personas = st.multiselect(
        "Empleado(s)",
        personas,
        key="sel_personas_ms",
        label_visibility="collapsed",
    )

    be1, be2 = st.columns(2)
    with be1:
        st.button(
            "Todos",
            icon=":material/done_all:",
            key="btn_all_emp",
            use_container_width=True,
            on_click=_set_personas_todos,
        )
    with be2:
        st.button(
            "Ninguno",
            icon=":material/clear_all:",
            key="btn_none_emp",
            use_container_width=True,
            on_click=_set_personas_ninguna,
        )

    return {
        "fecha_ini": fecha_ini,
        "fecha_fin": fecha_fin,
        "sel_grupos": sel_grupos,
        "sel_personas": sel_personas,
    }


# ─────────────────────────────────────────────────────────────────
# 5. SECCIÓN DE CONFIGURACIÓN DE VISTA
# ─────────────────────────────────────────────────────────────────
def config_section(horas_disponibles: list) -> dict:
    """
    Renderiza controles de agrupación y métrica de horas.

    Returns
    -------
    dict con claves: vista, tipo_hora
    """
    st.markdown("#### Configuración")

    col1, col2 = st.columns(2)
    with col1:
        vista = st.radio("Agrupar por", ["Día", "Semana", "Mes"], index=0)
    with col2:
        tipo_hora = st.selectbox(
            "Métrica",
            horas_disponibles,
            index=horas_disponibles.index("TOTAL") if "TOTAL" in horas_disponibles else 0,
            format_func=lambda x: f"{x} – {HORA_COLS.get(x, '')}",
        )

    return {"vista": vista, "tipo_hora": tipo_hora}
