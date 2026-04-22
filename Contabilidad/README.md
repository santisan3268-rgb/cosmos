# 📊 COSMOS - Sistema de Reportes de Labor

**Informe de Trabajo · Siesa Access**

Dashboard interactivo y profesional para transformar reportes de labor de **Siesa Access** en análisis visuales filtrados por persona, período y turno.

---

## 📋 Tabla de contenidos

1. [Descripción general](#descripción-general)
2. [Características](#características)
3. [Requisitos técnicos](#requisitos-técnicos)
4. [Instalación](#instalación)
5. [Uso](#uso)
6. [Estructura de archivos](#estructura-de-archivos)
7. [Datos y columnas](#datos-y-columnas)
8. [KPIs del dashboard](#kpis-del-dashboard)
9. [Exportación](#exportación)
10. [Personalización](#personalización)
11. [Soporte técnico](#soporte-técnico)

---

## 📖 Descripción general

**COSMOS** es un aplicativo web (Streamlit) que automatiza el procesamiento de reportes laborales exportados desde **Siesa Access**. Transforma datos complejos del archivo Excel en un **tablero interactivo** con:

- Carga de archivos Excel por drag & drop (sin archivo por defecto)
- Filtros dinámicos por empleado, rango de fechas y período
- KPIs de resumen con desglose por tipo de hora (crítico para liquidación de nómina)
- Verificación automática de que la suma de parciales cuadra con el TOTAL del archivo
- Tarjeta de detalle individual al filtrar un solo empleado
- Análisis por período (diario, semanal, mensual)
- Control de cumplimiento de horas extras (Ley 2466 de 2025)
- Exportación a Excel (.xlsx) y PDF

**Paleta de colores corporativa**: Terracota, Café y Crema.

> ⚠️ **Nota sobre JORNADA vs DO**: La columna `JORNADA` del reporte Siesa representa las horas del turno asignado (referencia), mientras que `DO` (código 001) representa las horas efectivamente laboradas en jornada ordinaria. El dashboard usa `DO` como base de cálculo. `JORNADA` se excluye de los totales para evitar duplicación.

---

## ✨ Características

### 📊 Análisis de datos

- ✅ **Por día**: Todas las columnas de horas por cada día laborado
- ✅ **Por semana**: Sumarizado de lunes a domingo con todas las categorías
- ✅ **Por mes**: Consolidado mensual por empleado
- ✅ **Detalle completo**: Registro individual de cada empleado por cada día
- ✅ **⚖️ Cumplimiento Ley 2466**: Alertas de límite diario (2 h) y semanal (12 h) de horas extras
- ✅ **Total laborado**: Resumen por empleado con 3 subtabs (Resumen / Ordinario vs Extra / Detalle completo)

### 📈 KPIs del dashboard

El dashboard muestra los indicadores en **3 filas**:

**Fila 1 – Resumen general**
| KPI | Descripción |
|-----|-------------|
| ✅ Total horas | Suma de la columna TOTAL del archivo Siesa |
| DO – Jornada ordinaria | Suma de la columna DO (horas efectivamente laboradas) |
| Días laborados | Días donde DO > 0 |

**Fila 2 – Horas extras (cada tipo por separado, distinto valor en nómina)**
| KPI | Código Siesa | Descripción |
|-----|-------------|-------------|
| HEDO | 008 | H. Extra diurna en día ordinario |
| HENO | 009 | H. Extra nocturna en día ordinario |
| HEDF | 010 | H. Extra diurna en día festivo |
| HENF | 011 | H. Extra nocturna en día festivo |

**Fila 3 – Otros tipos de hora**
| KPI | Código Siesa | Descripción |
|-----|-------------|-------------|
| RNO | 007 | Recargo nocturno ordinario |
| DOM | 012 | Dominical |
| RNF | 022 | Recargo nocturno festivo |
| FEST | 013 | Festivo |
| RNDOM/RDOM | 014 | Rec. noct. dom. + Rec. dom. |

### 🔍 Verificación de sumatoria

Debajo de los KPIs aparece automáticamente:
- ✔ Verde: suma de parciales == TOTAL del archivo (cuadra)
- ⚠️ Amarillo: diferencia detectada (puede indicar columnas adicionales en el archivo)

### 🎛️ Filtros interactivos

- Selección de empleados (multiselect)
- Rango de fechas configurable
- Agrupación por Día / Semana / Mes
- Métrica de horas seleccionable para la gráfica principal

### 💾 Exportación

- **Excel (.xlsx)**: Estructurado por empleado con totales y colores corporativos
- **PDF**: Con estructura de tabla, títulos y formatos

### 🔄 Carga de archivos

- Carga por el sidebar (drag & drop o clic)
- No se guarda en servidor — solo se procesa en memoria
- Compatible con archivos que tienen estructura de columnas variable por empleado

---

## 🛠️ Requisitos técnicos

- **Python**: 3.9 o superior (probado en 3.14)
- **Sistema operativo**: Windows, macOS, Linux
- **Navegador**: Chrome, Firefox, Safari (con JavaScript habilitado)

### Dependencias Python

```
streamlit==1.55.0
pandas==2.3.3
plotly==6.6.0
openpyxl==3.1.5
fpdf==1.7.2
streamlit-js-eval==1.0.0
```

---

## 📦 Instalación

### 1. Ubicación del proyecto

```
C:\Users\Equipo\Desktop\Cosmos\Contabilidad\
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 🚀 Uso

### Ejecutar la aplicación

```bash
cd "C:\Users\Equipo\Desktop\Cosmos\Contabilidad"
python -m streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

> ⚠️ **Importante**: ejecutar siempre desde la carpeta `Contabilidad` para que los assets (logo, isotipo) se resuelvan correctamente.

### En producción (sin abrir navegador)

```bash
python -m streamlit run app.py --server.headless true
```

### Acceder desde otra máquina

```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

---

## 📁 Estructura de archivos

```
Contabilidad/
├── app.py                    # Aplicación Streamlit principal
├── estilos.css              # Hoja de estilos corporativa
├── COSMOS.jpg.jpeg          # Logo COSMOS (header)
├── isotipo-png.png          # Isotipo (sidebar)
├── requirements.txt         # Dependencias Python
├── README.md                # Este archivo
├── ARQUITECTURA.md          # Documentación técnica interna
├── CHANGELOG.md             # Historial de cambios
└── .venv/                   # Entorno virtual (no subir a repo)
```

> El archivo Excel de datos se carga desde la interfaz — no es necesario colocarlo en la carpeta del proyecto.

---

## 📊 Datos y columnas

### Estructura del archivo Excel

- **Hoja requerida**: `ReporteXML`
- **Formato**: Filas con encabezados por empleado (Nombre, Documento, Grupo)
- **Datos**: Registros diarios con columnas de horas
- **Importante**: Cada empleado puede tener columnas en posiciones distintas según el tipo de jornada — el parser detecta la posición de cada columna dinámicamente por empleado

### Columnas procesadas

| Columna   | Código | Descripción                       | Incluida en TOTAL |
| --------- | ------ | --------------------------------- | :---------------: |
| JORNADA   | —      | Horas del turno asignado (ref.)   | ❌ Solo referencia |
| DO        | 001    | Jornada ordinaria efectiva        | ✅ |
| RNO       | 007    | Recargo nocturno ordinario        | ✅ |
| HEDO      | 008    | H. extra diurna ordinaria         | ✅ |
| HENO      | 009    | H. extra nocturna ordinaria       | ✅ |
| DOM       | 012    | Dominical                         | ✅ |
| RNF       | 022    | Recargo nocturno festivo          | ✅ |
| HEDF      | 010    | H. extra diurna festivo           | ✅ |
| HENF      | 011    | H. extra nocturna festivo         | ✅ |
| FEST      | 013    | Festivo                           | ✅ |
| RNDOM     | 014    | Recargo nocturno dominical        | ✅ |
| RDOM      | 014    | Recargo dominical                 | ✅ |
| ODOM      | 013    | Otras horas extra dominical       | ✅ |
| ORNF      | —      | Otras recargas nocturnas festivo  | ✅ |
| OEDF      | 010    | Otras horas extra diurnas festivo | ✅ |
| OFEST     | —      | Otras horas festivo               | ✅ |
| TOTAL     | —      | Total horas del día               | — |

---

## 💾 Exportación

### Excel (.xlsx)

- **Formato**: Libro estructurado con fila de encabezado en rojo corporativo
- **Por empleado**: Fila de nombre + registros + fila TOTAL con suma
- **Colores**: Verde para OK, Rojo para excesos (en reporte de cumplimiento)
- **Disponible en**: Todas las pestañas (Por día, Por semana, Por mes, Detalle completo, Total laborado)

### PDF

- **Formato**: Tabla con encabezados y datos
- **Uso**: Botón "Descargar PDF" en cada pestaña

---

## 🎨 Personalización

### Cambiar colores corporativos

Editar `:root` en `estilos.css`:

```css
:root {
  --primary: #9c4a38;   /* Terracota */
  --secondary: #a68070; /* Café */
  --accent: #d4a399;    /* Rosa terracota */
  --bg: #f5f0eb;        /* Crema */
}
```

### Cambiar logos

- **Header**: Reemplazar `COSMOS.jpg.jpeg`
- **Sidebar**: Reemplazar `isotipo-png.png`

### Agregar nuevas columnas de horas

Editar el diccionario `HORA_COLS` en `app.py`:

```python
HORA_COLS = {
    "NUEVA_COL": "Descripción para mostrar",
    # ...
}
```

---

## 🔧 Soporte técnico

### Problemas comunes

#### 1. Error: "No such file or directory: app.py"

Ejecutar desde la carpeta correcta:
```bash
cd "C:\Users\Equipo\Desktop\Cosmos\Contabilidad"
python -m streamlit run app.py
```

#### 2. Error: "No module named 'streamlit'"

```bash
pip install streamlit
```

#### 3. Diferencia entre suma parciales y TOTAL del archivo

El dashboard muestra una alerta automática. Causas posibles:
- El archivo tiene columnas adicionales que el parser no reconoce
- `JORNADA` no debe sumarse (ya está excluida desde la versión actual)
- Columnas con nombre diferente al estándar Siesa

#### 4. Columnas en posición incorrecta para algunos empleados

El parser detecta la posición de las columnas de forma dinámica por cada bloque de empleado. Cada empleado puede tener su propio header con columnas adicionales (ODOM, ORNF, OEDF) desplazando el índice de TOTAL.

#### 5. Error: "UnicodeDecodeError"

- Verificar que `estilos.css` tiene encoding UTF-8

#### 6. Warning: "`preventOverflow` modifier required"

- Es warning interno de Streamlit/Popper.js — no afecta funcionalidad


---

## 📖 Descripción general

**COSMOS** es un aplicativo web (Streamlit) que automatiza el procesamiento de reportes laborales exportados desde **Siesa Access**. Transforma datos complejos del archivo Excel en un **tablero interactivo** con:

- Filtros dinámicos por empleado, rango de fechas, grupo y turno
- Visualizaciones gráficas de jornada, horas extras y dominicales
- Análisis por período (diario, semanal, mensual)
- Exportación a CSV y PDF
- Carga de archivos Excel externos sin necesidad de acceso directo al servidor

**Paleta de colores corporativa**: Terracota, Café y Crema.

---

## ✨ Características

### 📊 Análisis de datos

- ✅ **Por día**: Jornada ordinaria, horas extras, dominicales por cada día
- ✅ **Por semana**: Sumarizado de lunes a domingo
- ✅ **Por mes**: Consolidado mensual
- ✅ **Detalle completo**: Registro individual de cada empleado por cada día

### 🎛️ Filtros interactivos

- Selección de empleados (multiselect)
- Rango de fechas configurable
- Filtro por grupo
- Clasificación por turno

### 📈 Visualizaciones

- Gráficos Plotly (barras, líneas, pie charts)
- KPIs en tarjetas destacadas
- Tablas interactivas y ordenables
- Información resumida

### 💾 Exportación

- **CSV**: Formato UTF-8-SIG, compatible con Excel
- **PDF**: Con estructura de tabla, títulos y formatos

### 🔄 Carga de archivos

- Interfaz para cargar archivos Excel sin reemplazar el archivo por defecto
- Soporte para múltiples archivos en sesión

### 🎨 Diseño corporativo

- Header con logo COSMOS
- Isotipo en sidebar
- Colores: Terracota (#9C4A38), Café (#A68070), Crema (#F5F0EB)
- Interfaz moderna y profesional

---

## 🛠️ Requisitos técnicos

- **Python**: 3.9 o superior
- **Sistema operativo**: Windows, macOS, Linux
- **Navegador**: Chrome, Firefox, Safari (con JavaScript habilitado)

### Dependencias Python

```
streamlit==1.55.0
pandas==2.3.3
plotly==6.6.0
openpyxl==3.1.5
fpdf==1.7.2
```

---

## 📦 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\Users\Equipo\Desktop\Cosmos
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install streamlit==1.55.0 pandas==2.3.3 plotly==6.6.0 openpyxl==3.1.5 fpdf==1.7.2
```

### 4. Preparar archivos

- Coloca tu archivo Excel `1-31 octubre.xlsx` en la carpeta raíz
- Asegúrate de que incluya la hoja `ReporteXML` con datos de Siesa

---

## 🚀 Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`

### En producción (sin abrir navegador)

```bash
streamlit run app.py --server.headless true
```

### Acceder desde otra máquina

```bash
streamlit run app.py --server.address 0.0.0.0
```

---

## 📁 Estructura de archivos

```
Cosmos/
├── app.py                    # Aplicación Streamlit principal
├── estilos.css              # Hoja de estilos corporativa
├── COSMOS.jpg.jpeg          # Logo COSMOS (header)
├── isotipo-png.png          # Isotipo (sidebar)
├── 1-31 octubre.xlsx        # Archivo de datos por defecto
├── README.md                # Este archivo
├── INSTRUCCIONES.md         # Guía de uso (legacy)
└── .venv/                   # Entorno virtual (no subir a repo)
```

---

## 📊 Datos y columnas

### Estructura del archivo Excel

- **Hoja requerida**: `ReporteXML`
- **Formato**: Filas con encabezados por empleado (Nombre, Documento, Grupo)
- **Datos**: Registros diarios con columnas de horas

### Columnas procesadas

| Columna   | Descripción                       |
| --------- | --------------------------------- |
| Nombre    | Nombre del empleado               |
| Documento | Número de documento               |
| Grupo     | Grupo/departamento                |
| Día       | Día de la semana                  |
| Fecha     | Fecha del registro (MM/DD/YYYY)   |
| Turno     | Turno asignado                    |
| JORNADA   | Horas de jornada ordinaria        |
| DO        | Horas dominical ordinario         |
| RNO       | Recargo nocturno ordinario        |
| HEDO      | Horas extra diurna ordinaria      |
| HENO      | Horas extra nocturna ordinaria    |
| DOM       | Horas dominical                   |
| RNF       | Recargo nocturno festivo          |
| HEDF      | Horas extra diurna festivo        |
| HENF      | Horas extra nocturna festivo      |
| FEST      | Horas festivo                     |
| RNDOM     | Recargo nocturno dominical        |
| RDOM      | Recargo dominical                 |
| ODOM      | Otras horas extra dominical       |
| ORNF      | Otras recargas nocturnas festivo  |
| OEDF      | Otras horas extra diurnas festivo |
| OFEST     | Otras horas festivo               |
| TOTAL     | Total horas del día               |

---

## 💾 Exportación

### CSV

- **Formato**: UTF-8-SIG (compatible con Excel)
- **Contenido**: Según la vista activa (Día/Semana/Mes/Detalle)
- **Uso**: Botón "Descargar CSV" en cada pestaña

### PDF

- **Formato**: Tabla con encabezados y datos
- **Contenido**: Según la vista activa
- **Uso**: Botón "Descargar PDF" en cada pestaña

### Proceso de exportación a PDF

```python
# Genera tabla con diseño profesional
# Codifica a base64 para descarga en navegador
# Soporta caracteres especiales y acentos
```

---

## 🎨 Personalización

### Cambiar colores corporativos

Editar `:root` en `estilos.css`:

```css
:root {
  --primary: #9c4a38; /* Terracota */
  --secondary: #a68070; /* Café */
  --accent: #d4a399; /* Rosa terracota */
  --light: #ffffff; /* Blanco */
  --bg: #f5f0eb; /* Crema */
  --text: #5a5555; /* Gris */
}
```

### Cambiar logos

- **Header**: Reemplazar `COSMOS.jpg.jpeg` con nueva imagen
- **Sidebar**: Reemplazar `isotipo-png.png` con nuevo isotipo
- Formatos soportados: PNG, JPG, JPEG

### Ajustar filtros y KPIs

Editar secciones en `app.py`:

- `HORA_COLS`: Agregar/quitar columnas de horas
- `st.sidebar.multiselect()`: Personalizar filtros
- `st.metric()`: Agregar/quitar KPIs

---

## 🔧 Soporte técnico

### Problemas comunes

#### 1. Error: "No module named 'streamlit'"

```bash
pip install streamlit==1.55.0
```

#### 2. Error: "UnicodeDecodeError: 'charmap' codec..."

- Verificar que `estilos.css` tiene encoding UTF-8
- En `app.py`, está configurado: `encoding="utf-8"`

#### 3. Error: "Invalid binary format bytearray"

- Causado por fpdf retornando `bytearray`
- Ya corregido en `df_to_pdf()` con: `bytes(out.getvalue())`

#### 4. Warning: "`preventOverflow` modifier required"

- Es warning de Popper.js (Streamlit interno)
- No afecta funcionalidad
- Ignorar o suprimir en consola

#### 5. Archivo Excel no se carga

- Verificar que existe `1-31 octubre.xlsx` en la carpeta raíz
- O usar cargador de archivos en la sidebar

### Archivos de log

- Streamlit guarda logs en: `.streamlit/logs/`
- Ver errores con: `streamlit run app.py --logger.level=debug`

---

## 📝 Notas técnicas

### Parser de Excel

- Detecta empleados por marcador "Nombre:"
- Detecta filas de datos por día de semana en español
- Maneja múltiples empleados y períodos

### Caché de datos

- `@st.cache_data`: Carga de Excel se cachea por sesión
- Evita recargas innecesarias
- Se limpia al cambiar archivo

### Codificación de archivos

- Entrada: Excel (openpyxl)
- Procesamiento: pandas (UTF-8)
- Salida: CSV (UTF-8-SIG), PDF (bytecode)

### Visualizaciones

- Plotly Express para gráficos dinámicos
- Responsive design (adapta a tamaño pantalla)
- Interactivo (hover, zoom, descargar como PNG)

---

## 👥 Historial de desarrollo

| Fase | Descripción                         | Estado        |
| ---- | ----------------------------------- | ------------- |
| 1    | Parser Excel y extracción de datos  | ✅ Completado |
| 2    | Dashboard con filtros básicos       | ✅ Completado |
| 3    | Exportación CSV y PDF               | ✅ Completado |
| 4    | Cargador de archivos externos       | ✅ Completado |
| 5    | Branding y CSS corporativo          | ✅ Completado |
| 6    | Colores suaves y mejorado contraste | ✅ Completado |
| 7    | Integración de logos                | ✅ Completado |
| 8    | Botones y inputs en terracota       | ✅ Completado |
| 9    | Documentación completa              | ✅ Completado |

---

## 📞 Contacto y feedback

Para reportar bugs o sugerir mejoras:

- Revisar logs en consola del navegador (F12)
- Verificar que el archivo Excel cumple formato Siesa
- Contactar al equipo técnico con screenshot del error

---

## 📜 Licencia

Proyecto desarrollado para **FYC Calzado**.
Uso interno únicamente.

---

## ✅ Checklist de implementación

- [x] Parser de Excel funcional (279 registros)
- [x] Dashboard con 4 vistas (día/semana/mes/detalle)
- [x] Filtros: empleados, rango de fechas, grupo, turno
- [x] KPIs: Total horas, Jornada, Extras, Dominicales, Días laborados
- [x] Exportación CSV (UTF-8-SIG)
- [x] Exportación PDF (tablas con diseño)
- [x] Cargador de archivos Excel en sidebar
- [x] CSS corporativo con paleta terracota/café/crema
- [x] Header con logo COSMOS
- [x] Sidebar con isotipo
- [x] Botones e inputs en terracota
- [x] Documentación completa

---

**Última actualización**: 18 de marzo de 2026  
**Versión**: 1.0 (Release)
