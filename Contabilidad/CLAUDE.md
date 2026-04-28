# CLAUDE.md – Contabilidad / COSMOS Dashboard

Guía de referencia para agentes de IA que trabajen en este proyecto.

---

## Comandos esenciales

```powershell
# Activar entorno virtual (desde la raíz del workspace)
Unblock-File .\.venv\Scripts\Activate.ps1
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force
& .\.venv\Scripts\Activate.ps1

# Ejecutar la aplicación (siempre desde Contabilidad/)
cd "C:\Users\Santiago Sanchez\Desktop\cosmos\Contabilidad"
python -m streamlit run app.py

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar tests
python -m pytest tests/ -v

# Ejecutar quality checks
.\scripts\run_quality_checks.ps1
```

---

## Configuración de Seguridad (Contraseñas)

La aplicación requiere configuración de credenciales antes de ejecutarse. Hay **dos métodos**:

### Método 1: Variables de Entorno (Recomendado para desarrollo/servidor propio)

Usa el script automatizado:
```powershell
.\scripts\setup-secrets.ps1 -Password "TuContraseñaSuperFuerte" -SessionHours 8 -AllowedIPs "127.0.0.1,192.168.1.0/24"
```

O configura manualmente en PowerShell:
```powershell
setx CONTA_APP_PASSWORD "TuContraseña"
setx CONTA_SESSION_HOURS "8"
setx CONTA_ALLOWED_IPS "127.0.0.1,192.168.1.0/24"
```

**Variables disponibles:**
- `CONTA_APP_PASSWORD` (requerido): Contraseña de acceso
- `CONTA_SESSION_HOURS` (opcional, default: 8): Duración de sesión en horas
- `CONTA_ALLOWED_IPS` (opcional, default: localhost + redes internas): IPs permitidas (CSV o CIDR)

### Método 2: Streamlit Secrets (Recomendado para Streamlit Community Cloud)

**Para desarrollo local:**
1. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`
2. Edita con tus valores:
```toml
APP_PASSWORD = "TuContraseña"
APP_SESSION_HOURS = 8
APP_ALLOWED_IPS = "127.0.0.1,192.168.1.0/24"
```
3. El archivo `.streamlit/secrets.toml` está en `.gitignore` y NO se subirá a GitHub

**Para Streamlit Community Cloud:**
1. Despliega la aplicación en https://streamlit.io/cloud
2. En Settings → Secrets (parte derecha), pega:
```
APP_PASSWORD = "TuContraseña"
APP_SESSION_HOURS = 8
APP_ALLOWED_IPS = ""
```

**Prioridad de configuración:**
1. `st.secrets` (secrets.toml o Streamlit Cloud)
2. Variables de entorno (`CONTA_*`)
3. Valores por defecto hardcoded

---

## Arquitectura del proyecto

```
Contabilidad/
├── app.py                   # Punto de entrada Streamlit — lógica UI y orquestación
├── estilos.css              # Estilos corporativos inyectados vía st.markdown
├── requirements.txt
├── data/
│   └── registros.db         # SQLite local (se crea automáticamente al primer guardado)
├── conta_core/
│   ├── parser_utils.py      # parse_excel_file(), HORA_COLS, DIAS — NO modificar sin tests
│   ├── export_utils.py      # df_to_excel_grouped(), excel_cumplimiento(), calcular_cumplimiento()
│   └── db_utils.py          # SQLite local: guardar_registro(), comparaciones, calcular_variacion()
├── tests/
│   ├── test_parser_utils.py
│   ├── test_export_utils.py
│   └── test_db_utils.py
└── scripts/
    ├── run_quality_checks.ps1
    └── rotate_db_secrets.ps1
```

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| UI | Streamlit 1.55.0 |
| Datos | pandas 2.3.3 |
| Gráficos | Plotly 6.6.0 |
| Excel I/O | openpyxl 3.1.5 |
| PDF | fpdf2 2.8.7 |
| BD local | SQLite (stdlib) — archivo `data/registros.db` |
| Python | 3.9+ (probado en 3.14) |

---

## Módulos críticos

### `conta_core/parser_utils.py`

- `parse_excel_file(path_or_file)` — lee la hoja `ReporteXML`; detecta bloques de empleado por marcador `"Nombre:"` y mapea columnas dinámicamente por bloque. Cada empleado puede tener columnas en posiciones distintas.
- `HORA_COLS` — diccionario canónico de columnas de horas. Agregar aquí cualquier columna nueva antes de usarla en `app.py`.
- `DIAS` — set de nombres de días en español (con y sin tilde) para detectar filas de datos.
- `prepare_loaded_dataframe(df)` — normaliza y limpia el DataFrame ya parseado.

### `conta_core/export_utils.py`

- `df_to_excel_grouped(df, ...)` — genera `.xlsx` estructurado por empleado con colores corporativos.
- `calcular_cumplimiento(df)` — aplica reglas de Ley 2466 (límite 2 h/día, 12 h/semana de extras).
- `excel_cumplimiento(df)` — exporta reporte de cumplimiento con celdas en verde/rojo.

### `conta_core/db_utils.py`

- BD local en `Contabilidad/data/registros.db` (SQLite). Se crea sola la primera vez.
- Tablas: `registros_mensuales` (totales globales por año-mes, único `(anio, mes)`) y `registros_tienda_mes` (totales por tienda, único `(anio, mes, tienda)`). Sobrescriben si el período ya existe.
- `guardar_registro(df, anio, mes, archivo_origen)` — filtra el DataFrame al período seleccionado y persiste totales globales y por tienda (campo `Grupo` del Excel).
- `listar_meses_guardados()` — devuelve los registros existentes, ordenados desc.
- `obtener_registro_global(anio, mes)` / `obtener_registros_tienda(anio, mes)` — lectura.
- `calcular_variacion(valor_anterior, valor_actual, umbral_pct=2.0)` — devuelve `{diff, pct, estado, emoji}` con estado `crecio` / `bajo` / `se_sostuvo`.
- Constantes: `HORAS_GUARDADAS`, `HORAS_EXTRAS`, `RECARGOS`, `CONCEPTOS_COMPARACION`, `MESES_ES`.

---

## Convenciones de código

- **CSS**: inyectado siempre con `st.markdown(..., unsafe_allow_html=True)`; no usar `st.html()`.
- **Colores corporativos**: `#9C4A38` (terracota), `#A68070` (café), `#F5F0EB` (crema), `#FFFFFF` (blanco).
- **Caché**: usar `@st.cache_data` en funciones de carga y transformación pesada.
- **Rutas de assets**: resolverlas siempre con `Path(__file__).parent / "archivo"`, nunca rutas absolutas.
- **SQL**: usar consultas parametrizadas; nunca concatenar strings de usuario en queries.
- **SQLite**: las conexiones se abren con el contextmanager `_connect()` que cierra siempre (Windows bloquea archivos si la conexión queda abierta).
- **JORNADA**: excluir de totales. `DO` (código 001) es la jornada efectiva; `JORNADA` es solo referencia.

---

## Columnas de horas (HORA_COLS)

| Columna | Código Siesa | Incluida en TOTAL |
|---------|-------------|:-----------------:|
| JORNADA | — | ❌ |
| DO | 001 | ✅ |
| RNO | 007 | ✅ |
| HEDO | 008 | ✅ |
| HENO | 009 | ✅ |
| HEDF | 010 | ✅ |
| HENF | 011 | ✅ |
| DOM | 012 | ✅ |
| FEST | 013 | ✅ |
| RNDOM/RDOM | 014 | ✅ |
| RNF | 022 | ✅ |
| ODOM, ORNF, OEDF, OFEST | varios | ✅ |

---

## Consideraciones importantes

- El archivo Excel **no se guarda en disco**; se procesa solo en memoria. Lo único que se persiste son los **totales mensuales** (global y por tienda) cuando el usuario presiona "Guardar en base de datos".
- La hoja requerida del Excel es exactamente `ReporteXML`.
- La verificación de sumatoria (parciales vs TOTAL) se muestra automáticamente bajo los KPIs.
- Ejecutar siempre desde la carpeta `Contabilidad/` para que los assets (logo, isotipo) y la BD (`data/registros.db`) se resuelvan con `Path(__file__).parent`.

---

## Pestaña "📊 Comparaciones"

- Compara **el mismo mes en dos años distintos** (ej. Enero 2025 vs Enero 2026), enfocada en horas extras.
- Requiere al menos dos registros guardados del mismo mes en años diferentes.
- Muestra: KPIs (TOTAL y horas extras), tabla de variación por concepto (HEDO/HENO/HEDF/HENF + recargos), gráfico de barras agrupadas, gráfico de Δ%, y comparación por tienda (incluye "tienda con más horas extras" en cada año).
