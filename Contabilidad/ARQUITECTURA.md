# 🏗️ ARQUITECTURA TÉCNICA - COSMOS Dashboard

Documentación interna de la estructura, flujo de datos y decisiones técnicas.

**Ubicación del proyecto**: `C:\Users\Equipo\Desktop\Cosmos\Contabilidad\`
**Comando de ejecución**: `cd "C:\Users\Equipo\Desktop\Cosmos\Contabilidad" && python -m streamlit run app.py`

---

## 📋 Tabla de contenidos

1. [Arquitectura general](#arquitectura-general)
2. [Flujo de datos](#flujo-de-datos)
3. [Módulos principales](#módulos-principales)
4. [Especificaciones de datos](#especificaciones-de-datos)
5. [KPIs y verificación de totales](#kpis-y-verificación-de-totales)
6. [Pestañas del dashboard](#pestañas-del-dashboard)
7. [Decisiones técnicas](#decisiones-técnicas)
8. [Optimizaciones](#optimizaciones)
9. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura general

### Stack tecnológico

```
┌─────────────────────────────────────────────┐
│      Navegador (HTML/CSS/JavaScript)        │
│  ┌──────────────────────────────────────┐   │
│  │    Interfaz Streamlit Renderizada    │   │
│  │  - Header (logo COSMOS)             │   │
│  │  - Sidebar (filtros + isotipo)      │   │
│  │  - KPIs (3 filas: resumen/extras/   │   │
│  │    otros) + verificación de totales │   │
│  │  - Gráficos + 6 pestañas de tablas  │   │
│  └──────────────────────────────────────┘   │
└─────────────┬───────────────────────────────┘
              │ WebSocket (Streamlit Protocol)
              ▼
┌─────────────────────────────────────────────┐
│     Streamlit Server (localhost:850X)       │
│  ┌──────────────────────────────────────┐   │
│  │ app.py (Lógica del aplicativo)       │   │
│  │ ├─ Parser dinámico de Excel          │   │
│  │ ├─ Filtros y transformaciones        │   │
│  │ ├─ KPIs con verificación de sumas    │   │
│  │ ├─ Generación de visualizaciones     │   │
│  │ ├─ Cumplimiento Ley 2466             │   │
│  │ └─ Exportación (Excel/PDF)           │   │
│  └──────────────────────────────────────┘   │
│  ┌──────────────────────────────────────┐   │
│  │ estilos.css (Inyectado vía HTML)     │   │
│  └──────────────────────────────────────┘   │
└─────────────┬───────────────────────────────┘
              │ Lectura en memoria (no disco)
              ▼
┌─────────────────────────────────────────────┐
│         Archivo Excel subido por usuario    │
│  ├─ Hoja: ReporteXML                       │
│  ├─ Estructura: bloques por empleado       │
│  └─ Columnas variables según empleado      │
└─────────────────────────────────────────────┘
```

---

## 🔄 Flujo de datos

### 1. Carga inicial

```
Usuario sube archivo .xlsx desde el sidebar
    ↓
parse_excel(uploaded_file)  ← @st.cache_data
    ├─ Para cada fila del worksheet:
    │    ├─ Detectar "Nombre:" → nuevo bloque empleado + reset col_map
    │    ├─ Detectar "Documento:" → guardar doc
    │    ├─ Detectar "Grupo:" → guardar grupo
    │    ├─ Detectar fila con "Fecha" y "TOTAL" → construir col_map dinámico
    │    │   (posición de cada columna varía por empleado)
    │    └─ Detectar día semana (lunes→domingo) → extraer registro usando col_map
    ├─ Normalizar fechas (MM/DD/YYYY → datetime)
    ├─ Agregar Semana, Semana_etiqueta, Mes, Mes_num
    └─ Convertir columnas de horas a float
    ↓
DataFrame cacheado en sesión
    ↓
Renderizar sidebar (filtros)
```

### 2. Interacción con filtros

```
Usuario selecciona filtros
    ↓
st.multiselect("Empleado(s)")     → filtra por Nombre
st.date_input("Rango fechas")     → filtra por Fecha
st.radio("Agrupar por")           → controla vista Día/Semana/Mes
st.selectbox("Métrica de horas")  → selecciona columna para gráfica
    ↓
dff = df[condiciones].copy()
    ↓
KPIs  →  Gráfica principal  →  6 pestañas de tablas
```

### 3. Exportación

```
Usuario hace click en "Descargar Excel" o "Descargar PDF"
    ↓
Excel: df_to_excel_grouped(df, título)
    ├─ Crear Workbook openpyxl
    ├─ Fila de encabezado (rojo corporativo)
    ├─ Por empleado: fila nombre (salmon) + datos + fila TOTAL
    └─ Retorna bytes para st.download_button()
    ↓
PDF: df_to_pdf(df, título)
    ├─ Crear objeto FPDF
    ├─ Agregar filas desde DataFrame
    ├─ Generar bytes (maneja bytearray → bytes)
    └─ Retorna bytes para st.download_button()
```

---

## 📦 Módulos principales

### app.py — Estructura de secciones

#### 1. Imports y config de página

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from pathlib import Path
```

#### 2. Assets visuales (logo + isotipo)

```python
LOGO_PATH = Path(__file__).parent / "COSMOS.jpg.jpeg"
ISOTIPO_PATH = Path(__file__).parent / "isotipo-png.png"
# Codificados en base64 para inyección HTML
```

#### 3. Diccionario HORA_COLS

Mapea código interno → descripción legible. Usado para:
- Selector de métrica en sidebar
- Renombrado de columnas en tablas
- Construcción dinámica de listas de columnas

```python
HORA_COLS = {
    "JORNADA": "Jornada ordinaria",   # ← referencia, NO en TOTAL
    "DO":      "D. ordinario",        # ← base de cálculo
    "RNO":     "Recargo nocturno ord.",
    "HEDO":    "H. extra diurna ord.",
    "HENO":    "H. extra nocturna ord.",
    "DOM":     "Dominical",
    "RNF":     "Rec. noct. festivo",
    "HEDF":    "H. extra diurna festivo",
    "HENF":    "H. extra noct. festivo",
    "FEST":    "Festivo",
    "RNDOM":   "Rec. noct. dominical",
    "RDOM":    "Rec. dominical",
    "ODOM":    "Hora extra dominical",
    "ORNF":    "Otra rec. noct. festivo",
    "OEDF":    "Otra h. ext. diurna fest.",
    "OFEST":   "Otras horas festivo",
    "TOTAL":   "Total horas",
}
```

#### 4. Parser de Excel (parse_excel)

**Clave técnica**: El parser es **dinámico por empleado**. Siesa genera un header diferente para cada empleado según los tipos de hora que apliquen. Por ejemplo:

- Empleado A → TOTAL en col[30] (sin columnas ODOM/ORNF/OEDF)
- Empleado B → TOTAL en col[35] (con columnas ODOM, ORNF, OEDF adicionales)

El `col_map` se reconstruye en cada bloque de empleado al detectar la fila con "Fecha" y "TOTAL".

También se ignoran las filas de subtotales por empleado (fila "TOTAL" del Excel) porque la primera columna sería "TOTAL" en mayúsculas, y no está en el conjunto `DIAS`.

#### 5. Sidebar y filtros

```python
uploaded_file = st.file_uploader(...)   # Carga desde sidebar
sel_personas  = st.multiselect(...)     # Empleados
rango         = st.date_input(...)      # Fechas
vista         = st.radio(...)           # Día/Semana/Mes
tipo_hora     = st.selectbox(...)       # Métrica para gráfica
```

#### 6. KPIs y verificación de totales

Ver sección específica más adelante.

#### 7. Gráfica principal

Barras agrupadas por empleado (desktop) o dona (móvil), usando la métrica seleccionada en el sidebar. Utiliza `streamlit_js_eval` para detectar ancho de pantalla.

#### 8. Pestañas (6 en total)

Ver sección específica más adelante.

#### 9. Funciones de exportación

- `df_to_excel_grouped(df, title)` — Excel estructurado con openpyxl
- `df_to_pdf(df, title)` — PDF simple con fpdf
- `excel_cumplimiento(df_diario, df_semanal)` — Excel de 2 hojas para reporte Ley 2466
- `calcular_cumplimiento(df)` — Calcula alertas de límites legales

#### 10. Gráfica comparativa

Distribución de tipos de horas por empleado (barras apiladas o dona).

---

## 📊 Especificaciones de datos

### DataFrame estructura

**Tabla de origen**: hoja `ReporteXML` del Excel

**Columnas del DataFrame resultante**:

| # | Columna | Tipo | Notas |
|---|---------|------|-------|
| 1 | Nombre | str | Nombre del empleado |
| 2 | Documento | str | Cédula/documento |
| 3 | Grupo | str | Departamento/sede |
| 4 | Día | str | Lunes…Domingo (capitalizado) |
| 5 | Fecha | datetime | Normalizada desde MM/DD/YYYY |
| 6 | Turno | str | Turno asignado |
| 7-23 | Horas* | float | Ver HORA_COLS |
| 24 | Semana | Int64 | Semana ISO del año |
| 25 | Semana_etiqueta | str | Período ISO ("2025-W40") |
| 26 | Mes | str | "October 2025" |
| 27 | Mes_num | int | Número de mes (1-12) |

### Transformaciones aplicadas

1. **Fechas**: `"10/1/2025 " → datetime(2025, 10, 1)` (strip + formato MM/DD/YYYY)
2. **Horas**: `pd.to_numeric(errors='coerce').fillna(0.0)` — valores vacíos se convierten a 0
3. **Redondeo**: todas las columnas de horas se redondean a 2 decimales al aplicar filtros
4. **Derivadas**: Semana, Semana_etiqueta, Mes, Mes_num calculadas desde Fecha

### Nota crítica: JORNADA ≠ DO

| Columna | Qué representa | Incluida en TOTAL |
|---------|---------------|:-----------------:|
| JORNADA | Horas del turno asignado (estimado) | ❌ |
| DO | Horas ordinarias efectivamente laboradas | ✅ |

`JORNADA` puede ser igual o diferente a `DO` (compensatorios, incapacidades, sin programación). Nunca se suma para verificación de totales.

---

## 📈 KPIs y verificación de totales

### Fila 1 — Resumen general (3 columnas)

```
✅ Total horas  |  DO – Jornada ordinaria  |  Días laborados
```

### Fila 2 — Horas extras separadas (4 columnas)

Cada tipo tiene valor de liquidación diferente en nómina:

```
HEDO (008)  |  HENO (009)  |  HEDF (010)  |  HENF (011)
```

### Fila 3 — Otros tipos de hora (5 columnas)

```
RNO  |  DOM  |  RNF  |  FEST  |  RNDOM/RDOM
```

### Verificación automática de sumatoria

```python
_cols_verificar = ["DO", "RNO", "HEDO", "HENO", "DOM", "RNF",
                   "HEDF", "HENF", "FEST", "RNDOM", "RDOM",
                   "ODOM", "ORNF", "OEDF", "OFEST"]
# JORNADA excluida ← causa de diferencias de ~22 h en versiones anteriores
_suma_parciales = sum(_col_sum(c) for c in _cols_verificar)
```

Tolerancia de 0.5 h para diferencias por redondeo.

### Tarjeta de detalle por empleado

Cuando `len(sel_personas) == 1`, aparece una tabla con cada categoría de hora como fila individual, subtotales por grupo y fila final TOTAL GENERAL.

---

## 📑 Pestañas del dashboard

| # | Pestaña | Contenido | Exporta |
|---|---------|-----------|---------|
| 1 | Por día | Tabla con todas las columnas de horas por día | Excel + PDF |
| 2 | Por semana | Groupby Nombre+Semana con suma de todas las columnas | Excel |
| 3 | Por mes | Groupby Nombre+Mes con suma de todas las columnas | Excel |
| 4 | Detalle completo | Datos crudos filtrados con todas las columnas | Excel |
| 5 | ⚖️ Cumplimiento Ley 2466 | Alertas diarias (máx 2 h extras/día) y semanales (máx 12 h/semana) | Excel (2 hojas) |
| 6 | Total laborado | 3 subtabs: Resumen / Ordinario vs Extra / Detalle completo | Excel |

### Tab "Total laborado" — 3 subtabs

**Resumen**: DO + RNO + HEDO + HENO + DOM + FEST + RNF + HEDF + HENF + RNDOM + RDOM + ODOM + ORNF + OEDF + OFEST + TOTAL

**Ordinario vs Extra**: Tiempo_Ordinario (todo menos extras) | Tiempo_Extra (HEDO+HENO+HEDF+HENF) | TOTAL

**Detalle completo**: Todas las columnas individuales del archivo

> `JORNADA` excluida de los tres subtabs para que los subtotales cuadren con TOTAL.

---

## 🎯 Decisiones técnicas

### 1. Parser dinámico por empleado (no pandas.read_excel)

**Por qué**: Siesa genera headers diferentes por empleado. Cada bloque tiene su propio `col_map` reconstruido al encontrar la fila "Fecha + TOTAL". Un archivo puede tener TOTAL en col[30] para unos empleados y col[35] para otros.

**Alternativa rechazada**: `pandas.read_excel` — no maneja estructura de bloques anidados con metadata en filas.

### 2. Exclusión de JORNADA de todos los totales

**Por qué**: `JORNADA` es la jornada del turno asignado, no las horas trabajadas. En días de compensatorio o incapacidad, `JORNADA > 0` pero `DO = 0`. Incluirla duplicaba ~22 h en la verificación de totales.

**Regla**: TOTAL Siesa = DO + RNO + HEDO + HENO + DOM + RNF + HEDF + HENF + FEST + RNDOM + RDOM + ODOM + ORNF + OEDF + OFEST

### 3. Cache con @st.cache_data

Evita re-parsear el Excel en cada interacción. El cache se invalida automáticamente si cambia el argumento (archivo diferente).

### 4. Exportación a bytes en memoria

No se escribe ningún archivo temporal en disco. El flujo es:
```
DataFrame → openpyxl/fpdf → BytesIO → bytes → st.download_button()
```

### 5. Base64 para logos

Funciona offline y sin dependencias externas.

### 6. streamlit_js_eval para detectar móvil

```python
_screen_width = streamlit_js_eval(js_expressions="window.innerWidth")
is_mobile = (_screen_width is not None and int(_screen_width) < 700)
```

En móvil: gráficas de dona con top-5 empleados. En desktop: barras agrupadas completas.

---

## ⚡ Optimizaciones

### 1. Caching del parser

```python
@st.cache_data(show_spinner="Leyendo archivo Siesa…")
def parse_excel(path_or_file) -> pd.DataFrame:
```

Primera carga: 1-3 s. Carga subsecuente: < 100 ms.

### 2. Filtrado vectorizado en una sola pasada

```python
dff = df[
    df["Nombre"].isin(sel_personas)
    & (df["Fecha"].dt.date >= fecha_ini)
    & (df["Fecha"].dt.date <= fecha_fin)
].copy()
```

### 3. Columnas de exportación condicionales

Se construyen con list comprehension filtrando solo columnas que existen en `dff.columns`, evitando KeyError si un archivo no tiene ciertas columnas.

---

## 🔧 Troubleshooting

### Error: "No such file or directory: app.py"

Ejecutar desde la carpeta correcta:
```bash
cd "C:\Users\Equipo\Desktop\Cosmos\Contabilidad"
python -m streamlit run app.py
```

### Diferencia entre suma parciales y TOTAL del archivo

La alerta en el dashboard indica diferencia > 0.5 h. Causas:
1. `JORNADA` incluida en la suma (ya corregido — no debería ocurrir)
2. Columna en el archivo con nombre diferente al estándar Siesa
3. Filas de totales intermedios del Excel siendo parseadas como datos

### Columnas en posición incorrecta para algunos empleados

El parser reconstruye `col_map` por empleado. Verificar que la fila de encabezado de cada bloque contiene "Fecha" y "TOTAL" como marcadores. Si un empleado tiene un header no estándar, sus columnas de horas quedarán en 0.

### Error: "bytearray object has no attribute X"

fpdf puede retornar `bytearray`. El código lo convierte:
```python
out = pdf.output(dest="S")
if isinstance(out, bytearray):
    return bytes(out)
```

### Puerto ocupado al iniciar

Si el puerto 8501 está ocupado (instancia anterior), Streamlit abre automáticamente en 8502, 8503, etc. Ver en la consola la URL real.



    ├─ Buscar logo COSMOS (base64)
    ├─ Buscar isotipo (base64)
    └─ Renderizar header
    ↓
Parser de Excel (@cache_data)
    ├─ Detectar empleados (Nombre:)
    ├─ Detectar columnas (Fecha, TOTAL)
    ├─ Extraer registros (días laborados)
    ├─ Convertir fechas (datetime)
    └─ Retornar DataFrame (279 rows)
    ↓
DataFrame cacheado en sesión
    ↓
Renderizar sidebar (filtros)
```

### 2. Interacción con filtros

```
Usuario selecciona filtros
    ↓
st.multiselect("Empleado")       → Actualiza dff_filtered
st.date_input("Rango fechas")    → Actualiza dff_filtered
st.selectbox("Grupo")            → Actualiza dff_filtered
st.radio("Turno")                → Actualiza dff_filtered
    ↓
Filtrar DataFrame: dff = df.filter(condiciones)
    ↓
Generar visualizaciones
    ├─ KPIs (st.metric)
    ├─ Gráficos (plotly)
    └─ Tablas (st.dataframe)
```

### 3. Exportación

```
Usuario hace click en "Descargar CSV" o "Descargar PDF"
    ↓
CSV: dff.to_csv(encoding='utf-8-sig')
    ↓
PDF: df_to_pdf(dff, titulo)
    ├─ Crear FPDF object
    ├─ Agregar filas desde DataFrame
    ├─ Generar bytes
    └─ Convertir bytearray → bytes
    ↓
st.download_button()
    └─ Descarga en navegador
```

---

## 📦 Módulos principales

### app.py - Estructura de secciones

#### 1. Imports y config (líneas 1-20)

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from pathlib import Path

st.set_page_config(page_title="...", layout="wide")
```

#### 2. CSS e identidad visual (líneas 21-50)

```python
# Cargar estilos.css
with open("estilos.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>")

# Cargar y codificar logo COSMOS
LOGO_PATH = Path("COSMOS.jpg.jpeg")
if LOGO_PATH.exists():
    logo_b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
    # Renderizar en HTML
```

#### 3. Parser de Excel (líneas 51-150)

```python
@st.cache_data(show_spinner="Leyendo archivo Siesa…")
def parse_excel(path_or_file) -> pd.DataFrame:
    # Lógica de parseo
    # Retorna DataFrame con columnas normalizadas
```

**Lógica del parser**:

1. Detecta "Nombre:" para identificar empleado
2. Detecta "Documento:" para número de documento
3. Detecta "Grupo:" para clasificación
4. Busca fila con "Fecha" y "TOTAL" para mapeo de columnas
5. Detecta días (lunes→domingo) para identificar registros de datos
6. Extrae valores por índice de columna
7. Normaliza fechas a datetime

**Entradas**: Ruta de archivo o archivo subido (file-like object)
**Salidas**: DataFrame limpio con 279 registros

#### 4. Sidebar y filtros (líneas 151-250)

```python
# Isotipo en sidebar
if ISOTIPO_PATH.exists():
    st.sidebar.markdown(isotipo_html)

# Filtros
st.sidebar.markdown("### Subir archivo de Siesa")
uploaded_file = st.file_uploader()

sel_personas = st.multiselect("Empleado(s)")
date_range = st.date_input("Rango de fechas")
sel_grupo = st.selectbox("Grupo")
# etc...
```

#### 5. Procesamiento de datos (líneas 251-300)

```python
# Aplicar filtros al DataFrame
dff_global = df[condiciones_filtro]

# Generar KPIs
st.metric("Total horas", sum_total)
st.metric("Jornada ordinaria", sum_jornada)
# etc...
```

#### 6. Pestañas (líneas 301-450)

```python
tab1, tab2, tab3, tab4 = st.tabs(["Por día", "Por semana", "Por mes", "Detalle"])

with tab1:
    # Filtro por persona en esta columna
    # Gráficos y tabla por día
    # Botón descargar CSV
    # Botón descargar PDF

# Mismo patrón para tab2, tab3, tab4
```

#### 7. Función de exportación PDF (líneas 300-350)

```python
def df_to_pdf(df, title):
    # Crear objeto FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)

    # Agregar filas
    for row in df.itertuples():
        pdf.cell(...)

    # Retornar bytes
    out = pdf.output()
    return bytes(out) if isinstance(out, bytearray) else out
```

### estilos.css - Paleta corporativa

```css
:root {
  --primary: #b8927f; /* Terracota suave */
  --secondary: #a68070; /* Café */
  --accent: #d4a399; /* Rosa terracota */
  --light: #ffffff; /* Blanco */
  --bg: #f5f0eb; /* Crema */
  --text: #5a5555; /* Gris */
  --white: #ffffff;
  --cta: #c9765f; /* CTA */
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
```

**Secciones CSS**:

1. Fondo general
2. Header Streamlit
3. Sidebar
4. Títulos
5. Tarjetas KPI
6. Gráficos
7. Pestañas
8. Botones (terracota)
9. Selects e inputs (terracota)
10. Dataframe
11. Radio buttons
12. HR separadores

---

## 📊 Especificaciones de datos

### DataFrame estructura

**Tabla de origen**: `ReporteXML` en Excel

**Columnas procesadas** (23 totales):

| #    | Columna   | Tipo     | Rango       | Notas                                                                                                 |
| ---- | --------- | -------- | ----------- | ----------------------------------------------------------------------------------------------------- |
| 1    | Nombre    | str      | Variable    | Nombre del empleado                                                                                   |
| 2    | Documento | str      | Variable    | Cédula/documento                                                                                      |
| 3    | Grupo     | str      | Variable    | Departamento                                                                                          |
| 4    | Día       | str      | Lun-Dom     | Día de la semana                                                                                      |
| 5    | Fecha     | datetime | 01/10-31/10 | Formato MM/DD/YYYY                                                                                    |
| 6    | Turno     | str      | Variable    | Turno asignado                                                                                        |
| 7-23 | Horas\*   | float    | 0.0-24.0    | JORNADA, DO, RNO, HEDO, HENO, DOM, RNF, HEDF, HENF, FEST, RNDOM, RDOM, ODOM, ORNF, OEDF, OFEST, TOTAL |

### Transformaciones aplicadas

1. **Fechas**: `str("01/10/2025") → datetime(2025, 1, 10)`
2. **Nulos**: Se preservan como `None` (para sumas con pandas)
3. **Agrupaciones**: `groupby("Nombre").sum()` para sumarizados
4. **Períodos**: Extracción de semana/mes desde fecha

### Validaciones

```python
# Validar que fecha sea válida
df['Fecha'] = pd.to_datetime(df['Fecha'].str.strip(),
                             errors='coerce',
                             format='%m/%d/%Y')

# Validar que empleados no estén vacíos
assert df['Nombre'].notna().all()

# Validar rangos de horas
assert (df[HORA_COLS] >= 0).all().all()
```

---

## 🎯 Decisiones técnicas

### 1. Parser manual (no pandas.read_excel directamente)

**Por qué**:

- Excel de Siesa tiene estructura compleja con múltiples tablas anidadas
- Necesita detección de marcadores ("Nombre:", "Fecha", etc.)
- Metadata en filas específicas, no en headers tradicionales

**Alternativa rechazada**: pandas.io.excel

- No puede parsear estructura horizontal (empleados como bloques)

### 2. Cache con @st.cache_data

**Por qué**:

- Excel parsing es costoso
- Usuarios a menudo hacen varias sesiones
- Archivos no cambian dentro de una sesión

**Límite**: Cache se limpia cuando:

- Usuario carga nuevo archivo
- Sesión de Streamlit termina
- Timeout (default 3600s)

### 3. Exportación a bytes en lugar de archivos temporales

**Por qué**:

- Streamlit es sin estado (stateless)
- No hay filesystem persistente en algunos deployments
- Más seguro (sin archivos huérfanos)

**Flujo**:

```
DataFrame → FPDF.output() → bytes → st.download_button()
```

### 4. Colores suaves (no colores oscuros)

**Por qué**:

- Mejor legibilidad en pantalla
- Interfaz moderna y profesional
- Menos fatiga visual en uso prolongado

**Paleta elegida**:

- Terracota suave: #B8927F (no #8A2F1F)
- Café: #A68070 (no #7A4F32)
- Fondos claros: #F5F0EB

### 5. Base64 para logos en lugar de URLs externas

**Por qué**:

- No requiere conexión a internet
- Funciona offline
- Más seguro (no dependencia externa)

**Proceso**:

```python
file_bytes = Path("COSMOS.jpg.jpeg").read_bytes()
b64_string = base64.b64encode(file_bytes).decode()
html = f"<img src='data:image/jpeg;base64,{b64_string}'>"
```

### 6. Inyección de CSS vía st.markdown() HTML

**Por qué**:

- Evita polluting del DOM de Streamlit
- Controlamos exactamente qué se aplica
- Fácil de mantener en archivo separado

**Alternativa rechazada**: Classes y st.write()

- Menos control sobre estilos finales
- Más código en Python

---

## ⚡ Optimizaciones

### 1. Caching de datos

```python
@st.cache_data(show_spinner="Leyendo archivo Siesa…")
def parse_excel(path_or_file) -> pd.DataFrame:
    # Parsing costoso
    return df
```

**Efecto**: Primera carga 2-3s, carga subsecuente <100ms

### 2. Caching de visualizaciones

```python
@st.cache_data
def generate_chart(df, chart_type):
    return px.bar(df, ...)
```

**Efecto**: No regenera gráfico si datos no cambian

### 3. Filtrado eficiente

```python
# Una pasada de filtrado
dff = df[
    (df['Nombre'].isin(sel_personas)) &
    (df['Fecha'] >= date_start) &
    (df['Fecha'] <= date_end) &
    (df['Grupo'] == sel_grupo)
]
```

**Efecto**: O(n) en lugar de múltiples filters() anidados

### 4. Lazy rendering

```python
# Solo renderiza tab activa
with tab1:
    if st.checkbox("Ver detalles"):  # Renderiza under demand
        st.dataframe(large_df)
```

---

## 🔧 Troubleshooting

### Problemas de encoding

**Error**: `UnicodeDecodeError: 'charmap' codec can't decode`

**Causa**: Windows usa encoding cp1252 por defecto

**Solución**:

```python
with open("file.txt", encoding="utf-8") as f:  # Explicit UTF-8
    content = f.read()
```

### Problemas de tipos de datos

**Error**: `AttributeError: 'bytearray' object has no attribute 'encode'`

**Causa**: fpdf retorna bytearray, no bytes

**Solución**:

```python
out = pdf.output()
if isinstance(out, bytearray):
    out = bytes(out)
return out
```

### Problemas de archivo no encontrado

**Error**: `FileNotFoundError: [Errno 2] No such file or directory`

**Causa**: Ruta relativa no es correcta

**Solución**:

```python
# Usar Path() relativa al script
LOGO_PATH = Path(__file__).parent / "COSMOS.jpg.jpeg"
if LOGO_PATH.exists():
    # ...
```

### Problemas de memoria

**Síntoma**: App lenta con muchas filas

**Solución**: Usar `.iloc[:100]` para preview

```python
st.dataframe(dff.iloc[:100])  # Mostrar primeras 100 filas
```

### Problemas de sesión

**Síntoma**: Filtros se pierden al recargar

**Causa**: Streamlit reruns el script completo

**Solución**: Usar `st.session_state`

```python
if 'selected' not in st.session_state:
    st.session_state.selected = []
st.session_state.selected = st.multiselect("...", value=st.session_state.selected)
```

---

## 📈 Métricas de rendimiento

| Operación               | Tiempo    | Caché      |
| ----------------------- | --------- | ---------- |
| Parse Excel (primera)   | 2-3s      | ✅ 1h      |
| Parse Excel (caché hit) | <100ms    | N/A        |
| Filtrado DataFrame      | <50ms     | ✅ 1h      |
| Generar gráfico         | 100-200ms | ✅ 1h      |
| Exportar CSV            | 50-100ms  | ❌         |
| Exportar PDF            | 200-500ms | ❌         |
| Render página completa  | 500ms-2s  | 🔄 Dynamic |

---

## 🚀 Escalabilidad futura

### Limitaciones actuales

1. **Excel único**, no base de datos
2. **259 registros max**, limitado por memoria
3. **Datos estáticos**, no tiempo real
4. **Offline only**, sin servidor remoto

### Mejoras propuestas

**Corto plazo** (1-2 semanas):

- [ ] SQLite para persistencia
- [ ] Histórico de archivos subidos
- [ ] Caché en disco

**Mediano plazo** (1-2 meses):

- [ ] API REST (FastAPI)
- [ ] Autenticación (JWT)
- [ ] Base de datos PostgreSQL

**Largo plazo** (3-6 meses):

- [ ] Dashboard en tiempo real (WebSockets)
- [ ] Predicciones con ML
- [ ] Mobile app (React Native)

---

**Documento**: Arquitectura Técnica COSMOS  
**Versión**: 1.0  
**Fecha**: 18 de Marzo de 2026  
**Autor**: Equipo de desarrollo
