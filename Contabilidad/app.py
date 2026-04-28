"""
app.py – Composition root · Dashboard de Reportes de Labor · FYC Calzado
=========================================================================
Este archivo sólo ensambla las piezas:
  1. Inyecta meta de no-traducción
  2. Renderiza la barra de navegación
  3. Gestiona carga de archivo y guardado en BD
  4. Aplica filtros del sidebar
  5. Delega cada sección de UI a los módulos de views/

Capas de la arquitectura:
  conta_core/  → dominio + adaptadores secundarios (DB, parser, exports)
  views/       → adaptadores primarios (Streamlit UI)
  sidebar_components.py → widgets del panel lateral
"""

import streamlit as st
import pandas as pd
import hmac
import os
import time
import ipaddress

from conta_core.db_utils import MESES_ES, guardar_registro
from conta_core.parser_utils import HORA_COLS, parse_excel_file, prepare_loaded_dataframe
from sidebar_components import (
    archivos_subidos_section,
    config_section,
    filtros_section,
    historial_section,
    render_brand,
    upload_section,
)
from views import (
    tab_comparaciones,
    tab_cumplimiento,
    tab_detalle,
    tab_dia,
    tab_distribucion,
    tab_mes,
    tab_semana,
    tab_tienda,
    tab_total,
)
from views.kpis import render_kpis_and_detail
from views.navbar import inject_no_translate, inject_styles, render_navbar


def _get_secret_or_env(secret_key: str, env_key: str, default: str = "") -> str:
    """Lee una configuración desde st.secrets o variable de entorno."""
    # Intenta primero st.secrets
    value = None
    try:
        if hasattr(st, "secrets") and st.secrets:
            value = st.secrets.get(secret_key)
    except Exception:
        pass
    
    # Si no hay valor en secrets, intenta variable de entorno
    if value in (None, ""):
        value = os.getenv(env_key, default)
    
    return str(value).strip()


def _get_client_ip() -> str:
    """Obtiene la IP cliente desde headers comunes de proxy; fallback localhost."""
    try:
        headers = st.context.headers  # Streamlit >= 1.29
    except Exception:
        headers = {}

    for key in ("x-forwarded-for", "x-real-ip", "cf-connecting-ip"):
        raw = headers.get(key) if headers else None
        if raw:
            return str(raw).split(",")[0].strip()

    return "127.0.0.1"


def _parse_allowed_networks(raw: str) -> list[ipaddress._BaseNetwork]:
    """Convierte CSV de IPs/redes a objetos ip_network.

    Si viene vacío, aplica whitelist local por defecto.
    Acepta hosts sueltos (ej: 192.168.1.15), interpretados como /32 o /128.
    """
    local_defaults = "127.0.0.1,::1,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16"
    text = raw.strip() if raw else local_defaults
    if text == "*":
        return []

    nets: list[ipaddress._BaseNetwork] = []
    for token in [x.strip() for x in text.split(",") if x.strip()]:
        try:
            if "/" in token:
                nets.append(ipaddress.ip_network(token, strict=False))
            else:
                ip_obj = ipaddress.ip_address(token)
                suffix = "/32" if ip_obj.version == 4 else "/128"
                nets.append(ipaddress.ip_network(f"{token}{suffix}", strict=False))
        except ValueError:
            st.warning(f"IP/red inválida en whitelist: {token}")
    return nets


def _is_ip_allowed(client_ip: str, allowed_nets: list[ipaddress._BaseNetwork]) -> bool:
    """Valida IP contra la lista blanca. Lista vacía = permitir todo."""
    if not allowed_nets:
        return True
    try:
        ip_obj = ipaddress.ip_address(client_ip)
    except ValueError:
        return False
    return any(ip_obj in net for net in allowed_nets)


def _clear_auth_state() -> None:
    """Elimina estado de autenticación de la sesión actual."""
    for key in ("_auth_ok", "_auth_ts", "_auth_ip", "_auth_input", "_logged_out"):
        st.session_state.pop(key, None)
    st.session_state["_logged_out"] = True


def _render_session_controls(client_ip: str, ttl_hours: int) -> None:
    """Renderiza el bloque de sesión en sidebar (alineado al diseño actual)."""
    st.markdown("#### Seguridad")
    st.markdown("<span class='filter-badge'>Sesión interna activa</span>", unsafe_allow_html=True)
    st.caption(f"IP: {client_ip}")

    auth_ts = float(st.session_state.get("_auth_ts", time.time()))
    remaining = max(0, int((ttl_hours * 3600) - (time.time() - auth_ts)))
    hours = remaining // 3600
    mins = (remaining % 3600) // 60
    st.caption(f"Expira en {hours:02d}:{mins:02d} (hh:mm)")

    if st.button(
        "Cerrar sesión",
        key="btn_logout_session",
        type="secondary",
        icon=":material/logout:",
        use_container_width=True,
    ):
        _clear_auth_state()
        st.info("✓ Sesión cerrada")
        st.rerun()


def _require_basic_auth() -> tuple[str, int]:
    """Bloqueo básico por contraseña para uso interno de 1 usuario.

    Prioridad de origen:
    1) st.secrets["APP_PASSWORD"]
    2) variable de entorno CONTA_APP_PASSWORD
    """
    pwd = _get_secret_or_env("APP_PASSWORD", "CONTA_APP_PASSWORD")
    ttl_hours_raw = _get_secret_or_env("APP_SESSION_HOURS", "CONTA_SESSION_HOURS", "8")
    allowed_ips_raw = _get_secret_or_env("APP_ALLOWED_IPS", "CONTA_ALLOWED_IPS", "")

    try:
        ttl_hours = max(1, int(float(ttl_hours_raw)))
    except ValueError:
        ttl_hours = 8

    client_ip = _get_client_ip()
    allowed_nets = _parse_allowed_networks(allowed_ips_raw)
    if not _is_ip_allowed(client_ip, allowed_nets):
        st.error(
            "Acceso denegado por lista blanca de IP. "
            f"IP detectada: {client_ip}."
        )
        st.stop()

    if not pwd:
        st.error(
            "APP_PASSWORD no está configurado. Define APP_PASSWORD en secrets "
            "o CONTA_APP_PASSWORD en variables de entorno antes de continuar."
        )
        st.stop()

    now = time.time()
    auth_ok = st.session_state.get("_auth_ok") is True
    auth_ts = float(st.session_state.get("_auth_ts", 0))
    auth_ip = str(st.session_state.get("_auth_ip", ""))
    logged_out = st.session_state.get("_logged_out") is True

    if logged_out:
        st.session_state.pop("_logged_out", None)
        st.session_state.pop("_auth_ok", None)
        auth_ok = False
    if auth_ok and (now - auth_ts) > (ttl_hours * 3600):
        _clear_auth_state()
        st.info("La sesión expiró por tiempo de inactividad. Vuelve a ingresar.")
        auth_ok = False

    if auth_ok and auth_ip and auth_ip != client_ip:
        _clear_auth_state()
        st.info("La sesión se cerró por cambio de IP. Vuelve a ingresar.")
        auth_ok = False

    if auth_ok:
        st.session_state["_auth_ts"] = now
        return client_ip, ttl_hours

    st.title("Acceso interno")
    st.info("Este tablero requiere contraseña de acceso.")
    entered = st.text_input("Contraseña", type="password", key="_auth_input")
    if st.button("Ingresar", use_container_width=True, type="primary"):
        st.session_state["_auth_ok"] = hmac.compare_digest(entered, str(pwd))
        if st.session_state["_auth_ok"]:
            st.session_state["_auth_ts"] = now
            st.session_state["_auth_ip"] = client_ip
            st.rerun()
        st.error("Contraseña incorrecta.")
    st.stop()

# ── Estilos corporativos ─────────────────────────────────────────────────────
inject_styles()

# ── Seguridad mínima (uso interno) ───────────────────────────────────────────
_client_ip, _ttl_hours = _require_basic_auth()

# ── Bloquear traducción automática del navegador ─────────────────────────────
inject_no_translate()

# ── Barra de navegación corporativa ──────────────────────────────────────────
render_navbar()

# ── Sidebar: marca + carga + historial ───────────────────────────────────────
with st.sidebar:
    render_brand()
    st.write("")
    uploaded_file = upload_section()
    historial_section(uploaded_file)
    archivos_subidos_section()
    _render_session_controls(_client_ip, _ttl_hours)
    st.divider()

# ── Parseo del archivo ────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Leyendo archivo Siesa…")
def _parse_excel(path_or_file) -> pd.DataFrame:
    return parse_excel_file(path_or_file)


if uploaded_file is None:
    st.info("Sube un archivo Excel de Siesa Access desde el panel izquierdo para comenzar.")
    st.stop()

try:
    df = _parse_excel(uploaded_file)
except Exception as e:
    st.error(f"No se pudieron extraer datos del archivo. Verifica el formato.\n\nError: {e}")
    st.stop()

if df.empty:
    st.error("No se pudieron extraer datos del archivo. Verifica el formato.")
    st.stop()

df, HORAS_DISPONIBLES = prepare_loaded_dataframe(df)

# ── Guardado en base de datos ─────────────────────────────────────────────────
_pending = st.session_state.pop("_pending_save", None)
if _pending:
    try:
        _info = guardar_registro(
            df=df,
            anio=int(_pending["anio"]),
            mes=int(_pending["mes"]),
            archivo_origen=str(_pending.get("archivo", "")),
        )
        st.success(
            f"Guardado **{MESES_ES[_pending['mes']]} {_pending['anio']}** "
            f"({_info['filas_periodo']:,} filas, {_info['n_tiendas']} tiendas). "
            f"Ya puedes verlo en la pestaña **Comparaciones**."
        )
    except ValueError as _e:
        st.error(f"{_e}")
    except Exception as _e:
        st.error(f"Error al guardar en base de datos: {_e}")

# ── Resetear filtros al cambiar de archivo ────────────────────────────────────
_current_file_id = uploaded_file.name if uploaded_file else ""
if st.session_state.get("_last_file_id") != _current_file_id:
    st.session_state["_last_file_id"] = _current_file_id
    for _k in ["sel_grupos_ms", "sel_personas_ms", "_prev_grupos"]:
        st.session_state.pop(_k, None)

# ── Sidebar: filtros + configuración ─────────────────────────────────────────
with st.sidebar:
    _filtros     = filtros_section(df)
    fecha_ini    = _filtros["fecha_ini"]
    fecha_fin    = _filtros["fecha_fin"]
    sel_grupos   = _filtros["sel_grupos"]
    sel_personas = _filtros["sel_personas"]

    st.divider()
    _config   = config_section(HORAS_DISPONIBLES)
    vista     = _config["vista"]
    tipo_hora = _config["tipo_hora"]

# ── Aplicar filtros ───────────────────────────────────────────────────────────
dff = df[
    df["Nombre"].isin(sel_personas)
    & df["Grupo"].fillna("(Sin grupo)").isin(sel_grupos)
    & (df["Fecha"].dt.date >= fecha_ini)
    & (df["Fecha"].dt.date <= fecha_fin)
].copy()
dff["Grupo"] = dff["Grupo"].fillna("(Sin grupo)")

# Redondear columnas numéricas de horas
_hora_num_cols = [c for c in list(HORA_COLS.keys()) + ["TOTAL"] if c in dff.columns]
for _c in _hora_num_cols:
    dff[_c] = dff[_c].round(2)

# ── Encabezado ────────────────────────────────────────────────────────────────
st.title("FYC Calzado – Reporte de Labor")
st.caption("Fuente: Siesa Access · Octubre 2025")

if dff.empty:
    st.warning("No hay datos para los filtros seleccionados.")
    st.stop()

# Tabs sticky
st.markdown(
    """
    <style>
    div[data-testid="stTabs"] > div[role="tablist"] {
        position: sticky; top: 0; z-index: 999;
        background: #F7F5F3; border-bottom: 1px solid #E4DDD7;
        padding-top: 0.35rem; padding-bottom: 0.25rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Por día",
    "Por semana",
    "Por mes",
    "Detalle completo",
    "Cumplimiento Ley 2466",
    "Total laborado",
    "Por Tienda",
    "Comparaciones",
])

# ── KPIs globales + tarjeta de empleado ──────────────────────────────────────
render_kpis_and_detail(dff, fecha_ini, fecha_fin, sel_personas)

# ── Tabs ──────────────────────────────────────────────────────────────────────
with tabs[0]:
    tab_dia.render(dff)

with tabs[1]:
    tab_semana.render(dff)

with tabs[2]:
    tab_mes.render(dff)

with tabs[3]:
    tab_detalle.render(dff)

with tabs[4]:
    tab_cumplimiento.render(dff)

with tabs[5]:
    tab_total.render(dff)

with tabs[6]:
    tab_tienda.render(dff)

with tabs[7]:
    tab_comparaciones.render()

# ── Gráfica de distribución (área principal, fuera de tabs) ──────────────────
tab_distribucion.render(dff)

st.caption("Desarrollado con Streamlit · Datos: Siesa Access")
