"""
views/navbar.py – Barra de navegación corporativa + bloqueo de traducción.
"""
from pathlib import Path
import base64

import streamlit as st

_STYLES_DIR = Path(__file__).parent.parent / "styles"


def inject_styles() -> None:
    """Carga y concatena los módulos CSS de styles/ e inyecta en la página."""
    if not _STYLES_DIR.is_dir():
        return
    parts = [
        f.read_text(encoding="utf-8")
        for f in sorted(_STYLES_DIR.glob("*.css"))
    ]
    if parts:
        st.markdown(f"<style>{''.join(parts)}</style>", unsafe_allow_html=True)


def inject_no_translate() -> None:
    """Inyecta meta + JS para bloquear la traducción automática del navegador."""
    st.markdown(
        """
        <meta name='google' content='notranslate'>
        <script>
            (function(){
                var h = document.documentElement;
                h.setAttribute('translate', 'no');
                h.setAttribute('lang', 'es');
            })();
        </script>
        """,
        unsafe_allow_html=True,
    )


def render_navbar() -> None:
    """Renderiza el banner corporativo con logo y título."""
    LOGO_PATH = Path(__file__).parent.parent / "COSMOS.jpg.jpeg"
    if LOGO_PATH.exists():
        logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        logo_html = (
            f"<div class='cosmos-navbar__logo'>"
            f"<img src='data:image/jpeg;base64,{logo_b64}' alt='FYC Calzado'>"
            f"</div>"
        )
    else:
        logo_html = "<div class='cosmos-navbar__logo cosmos-navbar__logo--text'>FYC</div>"

    st.markdown(
        f"""
        <nav class='cosmos-navbar'>
            <div class='cosmos-navbar__inner'>
                {logo_html}
                <div class='cosmos-navbar__divider' aria-hidden='true'></div>
                <div class='cosmos-navbar__titles'>
                    <span class='cosmos-navbar__eyebrow'>Sistema de Reportes</span>
                    <h1 class='cosmos-navbar__title'>Informe de Trabajo</h1>
                    <span class='cosmos-navbar__subtitle'>Siesa Access · FYC Calzado</span>
                </div>
                <div class='cosmos-navbar__badge'>
                    <span class='cosmos-navbar__badge-dot'></span>
                    <span class='cosmos-navbar__badge-text'>En línea</span>
                </div>
            </div>
            <div class='cosmos-navbar__accent' aria-hidden='true'></div>
        </nav>
        """,
        unsafe_allow_html=True,
    )
