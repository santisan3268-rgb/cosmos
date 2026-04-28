"""
generar_manual.py — Genera el Manual de Usuario de FYC Calzado Dashboard en PDF.
Requiere: fpdf2 >= 2.7
Uso: python scripts/generar_manual.py
Salida: docs/Manual_Usuario_FYC_Dashboard.pdf
"""

from pathlib import Path
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import datetime

# ── Colores corporativos ──────────────────────────────────────────────────────
TERRACOTA   = (156, 74, 56)     # #9C4A38
CAFE        = (166, 128, 112)   # #A68070
CREMA       = (245, 240, 235)   # #F5F0EB
BLANCO      = (255, 255, 255)
GRIS_OSCURO = (45, 45, 45)
GRIS_MEDIO  = (110, 110, 110)
GRIS_CLARO  = (220, 215, 210)

APP_URL    = "https://santisan3268-rgb-cosmos-contabilidadapp-qnttxg.streamlit.app/"
ISOTIPO    = Path(__file__).parent.parent / "isotipo-png.png"
LOGO_FULL  = Path(__file__).parent.parent / "COSMOS.jpg.jpeg"
FECHA   = datetime.date.today().strftime("%d de %B de %Y").replace(
    "January","enero").replace("February","febrero").replace("March","marzo"
    ).replace("April","abril").replace("May","mayo").replace("June","junio"
    ).replace("July","julio").replace("August","agosto").replace("September","septiembre"
    ).replace("October","octubre").replace("November","noviembre").replace("December","diciembre")


def _s(text: str) -> str:
    """Sanitiza texto para latin-1: reemplaza caracteres fuera de rango."""
    replacements = {
        "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
        "\u201c": '"', "\u201d": '"', "\u2026": "...", "\u00e9": "e",
        "\u00f3": "o", "\u00fa": "u", "\u00ed": "i", "\u00e1": "a",
        "\u00f1": "n", "\u00e3": "a", "\u00e0": "a", "\u00fc": "u",
        # emojis -> texto plano
        "\U0001f512": "[*]", "\U0001f4a1": "[!]", "\u26a0": "[!]",
        "\u2139": "[i]", "\u2753": "[?]",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    # Fallback: elimina cualquier char fuera de latin-1
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ManualPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=22)
        self._page_label = ""

    # Sanitizacion automatica en cell y multi_cell
    def cell(self, *args, **kwargs):
        if args and isinstance(args[2], str):
            args = list(args); args[2] = _s(args[2]); args = tuple(args)
        if "text" in kwargs:
            kwargs["text"] = _s(kwargs["text"])
        return super().cell(*args, **kwargs)

    def multi_cell(self, *args, **kwargs):
        if args and len(args) >= 3 and isinstance(args[2], str):
            args = list(args); args[2] = _s(args[2]); args = tuple(args)
        if "text" in kwargs:
            kwargs["text"] = _s(kwargs["text"])
        return super().multi_cell(*args, **kwargs)

    # ── Encabezado de página interior ────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return
        # Banda superior terracota
        self.set_fill_color(*TERRACOTA)
        self.rect(0, 0, 210, 10, "F")
        # Isotipo a la izquierda
        if ISOTIPO.exists():
            self.image(str(ISOTIPO), x=3, y=1, h=8)
        # Título a la derecha
        self.set_font("Helvetica", "B", 7)
        self.set_text_color(*BLANCO)
        self.set_y(2.5)
        self.cell(0, 5, "FYC Calzado · Manual de Usuario · Dashboard de Reportes de Labor",
                  align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_OSCURO)
        self.ln(4)

    # ── Pie de página ─────────────────────────────────────────────────────────
    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_draw_color(*CAFE)
        self.set_line_width(0.4)
        self.line(14, self.get_y(), 196, self.get_y())
        self.ln(1)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRIS_MEDIO)
        self.cell(0, 5, f"Página {self.page_no()} · Uso interno — Confidencial · FYC Calzado {datetime.date.today().year}",
                  align="C")

    # ── Helpers de tipografía ─────────────────────────────────────────────────
    def h1(self, text: str):
        """Titulo de seccion grande con banda lateral."""
        text = _s(text)
        self.ln(4)
        x, y = self.get_x(), self.get_y()
        self.set_fill_color(*TERRACOTA)
        self.rect(14, y, 4, 9, "F")
        self.set_x(20)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*TERRACOTA)
        self.cell(0, 9, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_OSCURO)
        self.ln(2)

    def h2(self, text: str):
        """Subtítulo."""
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(*CAFE)
        self.cell(0, 6, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_OSCURO)
        self.ln(1)

    def body(self, text: str, indent: float = 0):
        """Párrafo de cuerpo."""
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GRIS_OSCURO)
        self.set_x(14 + indent)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def bullet(self, text: str, level: int = 0):
        """Ítem de lista con viñeta."""
        indent = 6 + level * 6
        bullet_char = "•" if level == 0 else "–"
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(*GRIS_OSCURO)
        self.set_x(14 + indent)
        self.cell(5, 5.5, bullet_char)
        self.multi_cell(0, 5.5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def tag(self, text: str, color=TERRACOTA):
        """Etiqueta pill de color."""
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(*color)
        self.set_text_color(*BLANCO)
        self.set_x(14)
        self.cell(len(text) * 2.8, 5.5, text, fill=True, align="C",
                  new_x=XPos.END, new_y=YPos.LAST)
        self.set_text_color(*GRIS_OSCURO)
        self.ln(7)

    def info_box(self, text: str, color=CREMA, border_color=CAFE):
        """Caja de información destacada."""
        self.ln(2)
        self.set_fill_color(*color)
        self.set_draw_color(*border_color)
        self.set_line_width(0.5)
        x, y = 14, self.get_y()
        self.set_x(x)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS_OSCURO)
        self.multi_cell(182, 5.5, text, border=1, fill=True,
                        new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*GRIS_CLARO)
        self.set_line_width(0.2)
        self.ln(2)

    def step_box(self, num: str, title: str, desc: str):
        """Bloque de paso numerado."""
        self.ln(2)
        y = self.get_y()
        # Círculo numerado
        self.set_fill_color(*TERRACOTA)
        self.ellipse(14, y, 8, 8, "F")
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*BLANCO)
        self.set_xy(14, y + 1.5)
        self.cell(8, 5, num, align="C")
        # Título del paso
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(*TERRACOTA)
        self.set_xy(25, y)
        self.cell(0, 5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # Descripción
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS_OSCURO)
        self.set_x(25)
        self.multi_cell(0, 5, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def divider(self):
        self.ln(3)
        self.set_draw_color(*GRIS_CLARO)
        self.set_line_width(0.3)
        self.line(14, self.get_y(), 196, self.get_y())
        self.ln(3)

    def two_col_row(self, label: str, value: str):
        """Fila de tabla de dos columnas."""
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*GRIS_OSCURO)
        self.set_x(14)
        self.cell(45, 6, label, border="B")
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRIS_MEDIO)
        self.cell(0, 6, value, border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(*GRIS_OSCURO)


# ── Construcción del documento ────────────────────────────────────────────────
def build():
    pdf = ManualPDF()
    pdf.set_margins(14, 14, 14)

    # ═══════════════════════════════════════════════════════════════════════════
    # PORTADA
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Fondo superior terracota
    pdf.set_fill_color(*TERRACOTA)
    pdf.rect(0, 0, 210, 100, "F")

    # Decoración geométrica
    pdf.set_fill_color(*CAFE)
    pdf.rect(0, 85, 210, 6, "F")
    pdf.set_fill_color(180, 100, 80)
    pdf.rect(0, 91, 210, 2, "F")

    # Logo centrado en la portada
    _logo_path = LOGO_FULL if LOGO_FULL.exists() else (ISOTIPO if ISOTIPO.exists() else None)
    if _logo_path:
        # Centrar horizontalmente: ancho imagen ~40mm
        pdf.image(str(_logo_path), x=85, y=8, h=28)
        _titulo_y = 42
    else:
        _titulo_y = 18

    # Título principal
    pdf.set_font("Helvetica", "B", 26)
    pdf.set_text_color(*BLANCO)
    pdf.set_xy(0, _titulo_y)
    pdf.cell(0, 12, "MANUAL DE USUARIO", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_font("Helvetica", "", 13)
    pdf.set_xy(0, _titulo_y + 14)
    pdf.cell(0, 8, "Dashboard de Reportes de Labor", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Línea decorativa blanca
    pdf.set_draw_color(*BLANCO)
    pdf.set_line_width(0.8)
    pdf.line(60, _titulo_y + 24, 150, _titulo_y + 24)

    # Empresa
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_xy(0, _titulo_y + 28)
    pdf.cell(0, 7, "FYC Calzado", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Fondo crema
    pdf.set_fill_color(*CREMA)
    pdf.rect(0, 103, 210, 175, "F")

    # Ficha técnica en tarjeta
    pdf.set_fill_color(*BLANCO)
    pdf.set_draw_color(*GRIS_CLARO)
    pdf.set_line_width(0.3)
    pdf.rect(25, 110, 160, 75, "FD")

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(*CAFE)
    pdf.set_xy(25, 116)
    pdf.cell(160, 6, "INFORMACIÓN DEL DOCUMENTO", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_draw_color(*GRIS_CLARO)
    pdf.set_line_width(0.2)
    pdf.line(35, 124, 185, 124)

    ficha = [
        ("Version",       "1.0"),
        ("Fecha",         FECHA),
        ("Clasificacion", "Uso interno - Confidencial"),
        ("Audiencia",     "Equipo administrativo FYC Calzado"),
        ("Plataforma",    "Streamlit Cloud"),
        ("URL de acceso", APP_URL),
    ]
    pdf.set_xy(35, 127)
    for label, val in ficha:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*GRIS_OSCURO)
        pdf.set_x(35)
        pdf.cell(42, 6.5, label + ":", border="B")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*GRIS_MEDIO)
        pdf.cell(0, 6.5, val, border="B", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Nota confidencialidad
    pdf.set_xy(25, 178)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*CAFE)
    pdf.multi_cell(160, 5,
        "Este documento contiene información confidencial. "
        "No distribuir fuera del equipo autorizado de FYC Calzado.",
        align="C")

    # Pie portada
    pdf.set_fill_color(*TERRACOTA)
    pdf.rect(0, 280, 210, 17, "F")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(*BLANCO)
    pdf.set_xy(0, 285)
    pdf.cell(0, 6, f"FYC Calzado · {datetime.date.today().year} · Todos los derechos reservados", align="C")

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 2 — ÍNDICE
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.ln(2)
    pdf.h1("Tabla de Contenidos")

    secciones = [
        ("1.", "Objetivo del documento",            "3"),
        ("2.", "Alcance y audiencia",                "3"),
        ("3.", "Acceso a la plataforma",             "4"),
        ("4.", "Guía de uso paso a paso",            "5"),
        ("5.", "Descripción de funcionalidades",     "7"),
        ("6.", "Base de datos interna",              "9"),
        ("7.", "Exportaciones disponibles",          "10"),
        ("8.", "Seguridad y gestión de sesión",      "11"),
        ("9.", "Preguntas frecuentes",               "12"),
        ("10.","Soporte y contacto",                 "12"),
    ]
    pdf.ln(2)
    for num, titulo, pag in secciones:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*TERRACOTA)
        pdf.set_x(14)
        pdf.cell(10, 7, num)
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(*GRIS_OSCURO)
        pdf.cell(145, 7, titulo)
        # Puntos de relleno
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*GRIS_CLARO)
        pdf.cell(0, 7, pag, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_draw_color(*GRIS_CLARO)
        pdf.set_line_width(0.1)
        pdf.line(14, pdf.get_y(), 196, pdf.get_y())

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 3 — OBJETIVO Y ALCANCE
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()

    pdf.h1("1. Objetivo del Documento")
    pdf.body(
        "Este manual describe el uso del Dashboard de Reportes de Labor de FYC Calzado, "
        "una aplicación web interna desarrollada con Streamlit que permite al equipo "
        "administrativo cargar, visualizar y analizar los reportes de horas laboradas "
        "generados desde el sistema Siesa Access."
    )
    pdf.body(
        "El objetivo principal es que cualquier miembro autorizado del equipo pueda "
        "operar la herramienta de forma autónoma, sin requerir conocimientos técnicos "
        "adicionales."
    )

    pdf.divider()
    pdf.h1("2. Alcance y Audiencia")

    pdf.h2("2.1 Audiencia")
    pdf.body("Este documento está dirigido a:")
    pdf.bullet("Personal del área administrativa y de nómina de FYC Calzado.")
    pdf.bullet("Supervisores y jefes de tienda que requieran consultar reportes de labor.")
    pdf.bullet("Administradores del sistema responsables del mantenimiento de la plataforma.")

    pdf.h2("2.2 Qué cubre este manual")
    pdf.bullet("Acceso y autenticación en la plataforma.")
    pdf.bullet("Carga de archivos Excel generados por Siesa Access.")
    pdf.bullet("Análisis de horas por día, semana, mes y tienda.")
    pdf.bullet("Verificación de cumplimiento legal (Ley 2466).")
    pdf.bullet("Guardado y consulta de históricos en base de datos interna.")
    pdf.bullet("Comparación entre períodos guardados.")
    pdf.bullet("Exportación de reportes en Excel y PDF.")
    pdf.bullet("Gestión de sesión y cierre seguro.")

    pdf.h2("2.3 Qué NO cubre")
    pdf.bullet("Configuración técnica del servidor o entorno de despliegue.")
    pdf.bullet("Modificación del código fuente de la aplicación.")
    pdf.bullet("Administración del repositorio GitHub.")

    pdf.info_box(
        "ℹ  La aplicación está diseñada para ser utilizada en un navegador web estándar "
        "(Chrome, Edge o Firefox). No requiere instalación local."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 4 — ACCESO
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("3. Acceso a la Plataforma")

    pdf.h2("3.1 URL de acceso")
    pdf.body("La aplicación está disponible en la siguiente dirección web:")

    # Caja URL destacada
    pdf.ln(2)
    pdf.set_fill_color(*TERRACOTA)
    pdf.set_text_color(*BLANCO)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_x(14)
    pdf.cell(182, 10, APP_URL, fill=True, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_text_color(*GRIS_OSCURO)
    pdf.ln(3)

    pdf.body("Pasos para acceder:")
    pdf.step_box("1", "Abrir el navegador",
        "Abre Google Chrome, Microsoft Edge o Mozilla Firefox.")
    pdf.step_box("2", "Ingresar la URL",
        "Copia y pega la dirección anterior en la barra de búsqueda del navegador.")
    pdf.step_box("3", "Pantalla de login",
        "Aparecerá el formulario de acceso con el campo 'Contraseña'.")
    pdf.step_box("4", "Ingresar contraseña",
        "Escribe la contraseña de acceso (ver sección 3.2) y presiona el botón 'Ingresar'.")

    pdf.h2("3.2 Contraseña de acceso")
    pdf.info_box(
        "🔒  La contraseña de acceso es de uso interno y se entrega directamente por el "
        "administrador del sistema. Por política de seguridad, no se incluye en este "
        "documento ni se envía por correo electrónico ni mensajería digital.\n\n"
        "Para solicitar o restablecer la contraseña, contacte al administrador del sistema.",
        color=CREMA,
        border_color=TERRACOTA,
    )

    pdf.h2("3.3 Duración de la sesión")
    pdf.body(
        "La sesión tiene una duración máxima de 8 horas. Transcurrido ese tiempo, "
        "el sistema cerrará la sesión automáticamente y solicitará autenticación nuevamente."
    )
    pdf.body("Para cerrar la sesión manualmente, utilice el botón 'Cerrar sesión' en la parte inferior del panel lateral izquierdo.")

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 5-6 — GUÍA PASO A PASO
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("4. Guía de Uso Paso a Paso")
    pdf.body("A continuación se describe el flujo principal de trabajo con la aplicación.")

    pdf.h2("4.1 Flujo básico de análisis")
    pdf.step_box("1", "Acceder e iniciar sesión",
        "Navega a la URL de la aplicación e ingresa la contraseña de acceso. "
        "La pantalla de login desaparecerá y se cargará el dashboard completo.")
    pdf.step_box("2", "Subir el archivo Excel de Siesa",
        "En el panel lateral izquierdo, sección 'Datos de Origen', haz clic en "
        "'Browse files' o arrastra el archivo .xlsx exportado desde Siesa Access. "
        "El sistema procesará el archivo automáticamente.")
    pdf.step_box("3", "Revisar el resumen de KPIs",
        "En la parte superior del dashboard aparecerán tarjetas con los indicadores "
        "clave: total de horas, horas extras, número de empleados y tiendas.")
    pdf.step_box("4", "Explorar las pestañas de análisis",
        "Utiliza las pestañas horizontales para ver el análisis que necesitas: "
        "Por día, Por semana, Por mes, Detalle completo, Cumplimiento Ley 2466, "
        "Total laborado, Por Tienda y Comparaciones.")
    pdf.step_box("5", "Aplicar filtros",
        "En el panel lateral, sección 'Filtros', puedes ajustar el rango de fechas, "
        "seleccionar tiendas específicas o filtrar por empleados individuales.")
    pdf.step_box("6", "Guardar en base de datos",
        "Para conservar los totales del mes para futuras comparaciones, despliega "
        "'Registro Histórico' en el panel lateral, selecciona el año y mes "
        "correspondiente y presiona 'Guardar en BD'.")
    pdf.step_box("7", "Exportar reportes",
        "Usa los botones de descarga disponibles en cada pestaña para exportar "
        "el reporte en formato Excel o PDF según necesites.")
    pdf.step_box("8", "Cerrar sesión",
        "Al terminar, presiona el botón 'Cerrar sesión' en la sección 'Seguridad' "
        "del panel lateral para finalizar la sesión de forma segura.")

    pdf.add_page()
    pdf.h2("4.2 Consultar datos históricos desde la base de datos")
    pdf.body(
        "Si ya tienes meses guardados en la base de datos y quieres consultarlos "
        "sin necesidad de subir un nuevo archivo Excel, sigue estos pasos:"
    )
    pdf.step_box("1", "Abrir el expander 'Archivos ya subidos (BD)'",
        "En el panel lateral, haz clic en la sección 'Archivos ya subidos (BD)' "
        "para expandirla.")
    pdf.step_box("2", "Ver la mini-tabla de registros",
        "Se mostrará una tabla con todos los períodos guardados, incluyendo el "
        "nombre del archivo, la fecha de subida y el período.")
    pdf.step_box("3", "Seleccionar el período",
        "En la columna '↗' de la tabla, marca el checkbox del período que deseas "
        "consultar (por ejemplo, Febrero 2026).")
    pdf.step_box("4", "Vista automática del período",
        "El dashboard cargará automáticamente el resumen del período seleccionado "
        "con KPIs, desglose por concepto, detalle por tienda y acceso a comparaciones.")
    pdf.step_box("5", "Cerrar la vista",
        "Desmarca el checkbox del mismo período en la tabla para cerrar la vista "
        "y volver a la pantalla principal.")

    pdf.info_box(
        "💡  Puedes tener abierta la vista de BD y al mismo tiempo subir un nuevo Excel "
        "para comparar datos actuales con históricos usando la pestaña 'Comparaciones'."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 7 — FUNCIONALIDADES
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("5. Descripción de Funcionalidades")

    tabs = [
        ("Por día",
         "Muestra el total de horas trabajadas agrupado por fecha. Permite "
         "identificar días con alta concentración de horas extras o picos de labor."),
        ("Por semana",
         "Agrupa las horas por semana del año. Útil para detectar semanas con "
         "exceso de horas extras y planificar ajustes de turnos."),
        ("Por mes",
         "Resumen mensual de todas las categorías de horas (jornada ordinaria, "
         "horas extras diurnas y nocturnas, dominicales, festivos, etc.)."),
        ("Detalle completo",
         "Tabla con el desglose a nivel de empleado, con cada categoría de hora "
         "disponible. Permite buscar, ordenar y filtrar por nombre o tienda."),
        ("Cumplimiento Ley 2466",
         "Analiza el cumplimiento de los límites legales de horas extras "
         "(máximo 2 horas/día y 12 horas/semana). Resalta en rojo los empleados "
         "que superan los límites."),
        ("Total laborado",
         "Vista consolidada del total de horas por categoría para el período "
         "seleccionado. Incluye gráfica de distribución de conceptos."),
        ("Por Tienda",
         "Comparativa de horas entre tiendas. Permite identificar cuáles tiendas "
         "concentran mayor carga de horas extras."),
        ("Comparaciones",
         "Herramienta de análisis entre dos períodos guardados en la base de datos. "
         "Muestra variaciones absolutas y porcentuales por concepto y por tienda, "
         "con gráficas de barras agrupadas y tendencia."),
    ]

    for nombre, desc in tabs:
        pdf.h2(f"Pestaña: {nombre}")
        pdf.body(desc)

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 8 — PANEL LATERAL
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("Panel Lateral — Resumen de Secciones")

    secciones_sidebar = [
        ("Datos de Origen",
         "Uploader del archivo Excel de Siesa Access. Muestra el nombre del archivo "
         "cargado en memoria y tiene botones de Recargar y Limpiar."),
        ("Registro Histórico",
         "Permite seleccionar el año y mes correspondiente al archivo cargado "
         "y guardarlo en la base de datos interna para análisis comparativo futuro."),
        ("Archivos ya subidos (BD)",
         "Lista todos los períodos guardados con nombre de archivo y fecha de carga. "
         "Permite abrir cualquier período haciendo clic en el checkbox '↗' de la tabla."),
        ("Filtros",
         "Permite acotar el análisis por rango de fechas (con atajos 'Este mes', "
         "'Mes previo', 'Completo'), por tienda/grupo y por empleado."),
        ("Configuración",
         "Permite seleccionar el tipo de hora a visualizar en las gráficas y ajustar "
         "la vista de análisis."),
        ("Seguridad",
         "Muestra la IP de la sesión activa, el tiempo restante de sesión y el botón "
         "de cierre de sesión."),
    ]

    for nombre, desc in secciones_sidebar:
        pdf.set_fill_color(*CREMA)
        pdf.set_draw_color(*CAFE)
        pdf.set_line_width(0.3)
        y = pdf.get_y()
        pdf.rect(14, y, 182, 18, "FD")
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*TERRACOTA)
        pdf.set_xy(19, y + 2)
        pdf.cell(0, 5, nombre, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(*GRIS_OSCURO)
        pdf.set_x(19)
        pdf.multi_cell(172, 4.5, desc, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 9 — BASE DE DATOS
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("6. Base de Datos Interna")

    pdf.body(
        "La aplicación cuenta con una base de datos SQLite interna que almacena "
        "los totales mensuales de horas por categoría, tanto a nivel global "
        "como desglosado por tienda."
    )

    pdf.h2("¿Qué se guarda?")
    pdf.bullet("Total de cada categoría de horas (DO, RNO, HEDO, HENO, HEDF, HENF, DOM, FEST, etc.).")
    pdf.bullet("Totales desglosados por tienda (campo Grupo del Excel de Siesa).")
    pdf.bullet("Nombre del archivo Excel de origen y fecha/hora de la carga.")

    pdf.h2("¿Qué NO se guarda?")
    pdf.bullet("El archivo Excel original — solo se procesa en memoria.")
    pdf.bullet("Datos individuales por empleado — solo totales agregados.")
    pdf.bullet("Contraseñas ni información de sesión.")

    pdf.h2("Comportamiento al guardar")
    pdf.body(
        "Si ya existe un registro para el mismo año y mes, se sobrescribe con los "
        "nuevos datos. Esto permite corregir una carga incorrecta simplemente "
        "volviendo a subir el archivo correcto y guardando con los mismos parámetros."
    )

    pdf.info_box(
        "⚠  En el entorno de Streamlit Cloud, la base de datos se reinicia con cada "
        "nuevo despliegue. Los datos históricos se conservan mientras la instancia "
        "esté activa. Para persistencia permanente, contacte al administrador del sistema."
    )

    pdf.h2("Comparaciones entre períodos")
    pdf.body(
        "Una vez guardados al menos dos períodos, la pestaña 'Comparaciones' permite "
        "seleccionar cualquier par (por ejemplo, Febrero 2026 vs Marzo 2026) y obtener:"
    )
    pdf.bullet("Variación absoluta y porcentual por concepto de hora.")
    pdf.bullet("Clasificación automática: Creció / Bajó / Se sostuvo.")
    pdf.bullet("Gráficas de barras agrupadas y de variación porcentual.")
    pdf.bullet("Comparativo de horas extras por tienda.")

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 10 — EXPORTACIONES
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("7. Exportaciones Disponibles")

    exportaciones = [
        ("Excel estructurado por empleado",
         "Genera un archivo .xlsx con el detalle completo de horas por empleado, "
         "organizado con colores corporativos FYC. Disponible en la pestaña 'Detalle completo'."),
        ("Reporte de Cumplimiento Ley 2466",
         "Exporta en Excel el análisis de cumplimiento legal, con celdas en verde "
         "(cumple) y rojo (supera límites). Disponible en la pestaña 'Cumplimiento Ley 2466'."),
        ("PDF del reporte",
         "Genera una versión PDF del reporte de labor con formato corporativo. "
         "Disponible en pestañas seleccionadas mediante el botón de descarga."),
    ]

    for nombre, desc in exportaciones:
        pdf.h2(nombre)
        pdf.body(desc)
        pdf.divider()

    pdf.h2("Formato del archivo Excel de entrada (Siesa Access)")
    pdf.body("El archivo de entrada debe cumplir los siguientes requisitos:")
    pdf.bullet("Formato: .xlsx (Excel).")
    pdf.bullet("Debe contener la hoja 'ReporteXML'.")
    pdf.bullet("Los bloques de empleado deben estar marcados con el encabezado 'Nombre:'.")
    pdf.bullet("Las columnas de horas deben corresponder a los códigos estándar de Siesa (001, 007, 008, etc.).")

    pdf.info_box(
        "💡  No modifiques la estructura del archivo antes de subirlo. "
        "El sistema detecta automáticamente las columnas de cada empleado aunque "
        "estén en posiciones distintas en el Excel."
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 11 — SEGURIDAD
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("8. Seguridad y Gestión de Sesión")

    pdf.h2("Medidas de seguridad implementadas")
    pdf.bullet("Autenticación por contraseña en cada acceso.")
    pdf.bullet("Sesión con tiempo de expiración automático (8 horas por defecto).")
    pdf.bullet("Detección de cambio de IP: si la IP cambia durante la sesión, se cierra automáticamente.")
    pdf.bullet("Fail-closed: si la contraseña no está configurada, la app bloquea el acceso completamente.")
    pdf.bullet("Los archivos Excel se procesan solo en memoria — nunca se escriben en disco.")
    pdf.bullet("Las credenciales de acceso no están incluidas en el código fuente ni en el repositorio.")

    pdf.h2("Buenas prácticas para el usuario")
    pdf.bullet("No compartir la contraseña de acceso por medios digitales (correo, WhatsApp, etc.).")
    pdf.bullet("Siempre cerrar sesión al terminar, especialmente en equipos compartidos.")
    pdf.bullet("No dejar la aplicación abierta en el navegador sin supervisión.")
    pdf.bullet("Si sospechas que la contraseña fue comprometida, notifica al administrador inmediatamente.")
    pdf.bullet("Usar conexiones de red confiables (red corporativa o VPN).")

    pdf.h2("Tabla de roles")
    pdf.ln(2)
    encabezados = ["Rol", "Acceso", "Puede guardar en BD", "Puede exportar"]
    anchos = [45, 40, 45, 45]
    pdf.set_fill_color(*TERRACOTA)
    pdf.set_text_color(*BLANCO)
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_x(14)
    for h, w in zip(encabezados, anchos):
        pdf.cell(w, 7, h, fill=True, align="C", border=1)
    pdf.ln()

    filas_roles = [
        ["Administrador", "Completo", "Sí", "Sí"],
        ["Usuario estándar", "Completo", "Sí", "Sí"],
        ["Solo lectura*", "Completo", "No", "Sí"],
    ]
    pdf.set_fill_color(*CREMA)
    pdf.set_text_color(*GRIS_OSCURO)
    pdf.set_font("Helvetica", "", 8.5)
    for i, fila in enumerate(filas_roles):
        pdf.set_fill_color(CREMA if i % 2 == 0 else BLANCO)
        pdf.set_x(14)
        for val, w in zip(fila, anchos):
            pdf.cell(w, 6.5, val, fill=True, border=1, align="C")
        pdf.ln()

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(*GRIS_MEDIO)
    pdf.set_x(14)
    pdf.cell(0, 5, "* El rol de solo lectura debe configurarse a nivel de credenciales por el administrador.")
    pdf.ln(6)

    # ═══════════════════════════════════════════════════════════════════════════
    # PÁGINA 12 — FAQ Y CONTACTO
    # ═══════════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.h1("9. Preguntas Frecuentes")

    faqs = [
        ("¿Qué hago si el archivo no se carga correctamente?",
         "Verifica que el archivo sea .xlsx y que contenga la hoja 'ReporteXML'. "
         "Si el problema persiste, revisa que no haya modificado la estructura del "
         "reporte en Siesa antes de exportarlo."),
        ("¿Puedo subir varios archivos al mismo tiempo?",
         "No. La aplicación procesa un archivo a la vez. Para comparar dos meses, "
         "debes guardar cada uno en la base de datos y usar la pestaña 'Comparaciones'."),
        ("¿Se pierden los datos si cierro el navegador?",
         "El archivo Excel en memoria se elimina al cerrar la pestaña. Los datos "
         "guardados en la base de datos persisten mientras la instancia del servidor "
         "esté activa. En Streamlit Cloud los datos de BD persisten entre sesiones "
         "del mismo despliegue."),
        ("La sesión se cerró sola, ¿es normal?",
         "Sí. La sesión expira automáticamente después de 8 horas de inactividad "
         "o cuando se detecta un cambio de IP. Vuelve a ingresar la contraseña."),
        ("¿Cómo corrijo un registro guardado por error?",
         "Sube el archivo correcto, selecciona el mismo año y mes en 'Registro "
         "Histórico' y presiona 'Guardar en BD'. El sistema sobrescribirá "
         "el registro anterior automáticamente."),
        ("¿La aplicación funciona en el celular?",
         "Sí, es responsive y funciona en navegadores móviles, aunque la experiencia "
         "está optimizada para pantallas de escritorio debido al volumen de datos."),
    ]

    for pregunta, respuesta in faqs:
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(*TERRACOTA)
        pdf.set_x(14)
        pdf.multi_cell(0, 6, f"❓  {pregunta}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*GRIS_OSCURO)
        pdf.set_x(20)
        pdf.multi_cell(0, 5.5, respuesta, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(3)

    pdf.divider()
    pdf.h1("10. Soporte y Contacto")
    pdf.body(
        "Para solicitar soporte técnico, reportar errores o gestionar accesos, "
        "contacta directamente al administrador del sistema de FYC Calzado."
    )
    pdf.info_box(
        "🔒  Recuerda: la contraseña de acceso se entrega directamente y de forma "
        "personal por el administrador del sistema. Nunca se envía por medios digitales.",
        color=CREMA,
        border_color=TERRACOTA,
    )

    # ── Guardar ───────────────────────────────────────────────────────────────
    out_dir = Path(__file__).parent.parent / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "Manual_Usuario_FYC_Dashboard.pdf"
    pdf.output(str(out_path))
    print(f"✓ PDF generado en: {out_path}")
    return out_path


if __name__ == "__main__":
    build()
