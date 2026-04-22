# 🚀 GUÍA DE DESPLIEGUE - COSMOS Dashboard

Instrucciones paso a paso para instalar, configurar y ejecutar el dashboard.

---

## 🎯 Requisitos previos

- Python 3.9 o superior instalado
- pip (gestor de paquetes Python)
- Navegador web moderno (Chrome, Firefox, Safari, Edge)
- Acceso a terminal/PowerShell
- 100 MB de espacio en disco

### Verificar Python

Abre una terminal y ejecuta:

```bash
python --version
```

Debe mostrar: `Python 3.9.x` o superior

---

## 📦 Instalación paso a paso

### Paso 1: Preparar la carpeta del proyecto

```bash
# Navega a la carpeta de COSMOS
cd c:\Users\Equipo\Desktop\Cosmos

# Verifica que existan los archivos necesarios
dir
```

Deberías ver:

```
app.py
estilos.css
COSMOS.jpg.jpeg
isotipo-png.png
1-31 octubre.xlsx
README.md
CHANGELOG.md
ARQUITECTURA.md
requirements.txt
```

### Paso 2: Crear entorno virtual (recomendado)

Un entorno virtual aísla las dependencias de tu proyecto.

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\activate

# Deberías ver (.venv) al inicio de tu terminal
```

### Paso 3: Instalar dependencias

```bash
# Asegúrate de que .venv esté activado
pip install --upgrade pip

# Instalar desde requirements.txt
pip install -r requirements.txt
```

**Tiempo estimado**: 2-5 minutos

**Salida esperada**:

```
Successfully installed streamlit-1.55.0 pandas-2.3.3 ...
```

### Paso 4: Verificar instalación

```bash
python -c "import streamlit, pandas, plotly; print('✓ Todo instalado correctamente')"
```

Deberías ver: `✓ Todo instalado correctamente`

---

## ▶️ Ejecutar la aplicación

### Ejecución local

```bash
# Asegúrate de estar en la carpeta c:\Users\Equipo\Desktop\Cosmos
# Y que .venv esté activado

streamlit run app.py
```

**Salida esperada**:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### Acceder a la app

1. La app se abrirá automáticamente en tu navegador
2. Si no, copia la URL `http://localhost:8501` en tu navegador
3. Deberías ver el dashboard con:
   - Header con logo COSMOS
   - Sidebar con filtros e isotipo
   - Gráficos y tablas en la zona principal

### Detener la app

En la terminal, presiona: `Ctrl + C`

---

## 🎮 Uso de la aplicación

### Subir archivo Excel

1. En la **sidebar**, busca "Subir archivo de Siesa"
2. Haz click en "Browse files"
3. Selecciona tu archivo `.xlsx`
4. El archivo se carga automáticamente (sin reemplazar el por defecto)

### Aplicar filtros

**En la sidebar**:

- **Empleado(s)**: Selecciona uno o varios nombres
- **Rango de fechas**: Elige fecha inicio y fin
- **Grupo**: Filtro por departamento (dropdown)
- **Filtro por turno**: Radio buttons

Los datos se actualizan automáticamente.

### Ver diferentes perspectivas

Haz click en las **pestañas** superiores:

1. **Por día**: Detalle diario de horas
2. **Por semana**: Sumarizado semanal
3. **Por mes**: Datos consolidados del mes
4. **Detalle completo**: Registro individual por empleado

### Exportar datos

En cada pestaña encontrarás dos botones (terracota):

- **Descargar CSV**: Abre en Excel, Google Sheets, etc.
- **Descargar PDF**: Genera reporte imprimible

---

## ⚙️ Configuración avanzada

### Cambiar puerto

```bash
streamlit run app.py --server.port 8502
```

Accede en: `http://localhost:8502`

### Acceder desde otra máquina

```bash
streamlit run app.py --server.address 0.0.0.0
```

Desde otra PC en la red:

```
http://192.168.x.x:8501
# Reemplaza 192.168.x.x con la IP de tu máquina
```

Para encontrar tu IP:

```bash
ipconfig
# Busca "IPv4 Address"
```

### Modo headless (sin navegador)

```bash
streamlit run app.py --server.headless true
```

Accede manualmente en `http://localhost:8501`

### Debug mode

```bash
streamlit run app.py --logger.level=debug
```

---

## 🐛 Problemas comunes y soluciones

### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Causa**: Dependencias no instaladas

**Solución**:

```bash
# Verifica que .venv esté activado
pip install -r requirements.txt
```

### Error: "UnicodeDecodeError: 'charmap' codec..."

**Causa**: Problema de encoding en Windows

**Solución**:

- Está ya corregido en `app.py` (usa `encoding="utf-8"`)
- Si persiste, revisa que `estilos.css` este en UTF-8

### Error: "FileNotFoundError: 1-31 octubre.xlsx"

**Causa**: Archivo no existe en la carpeta

**Solución**:

1. Asegúrate de estar en: `c:\Users\Equipo\Desktop\Cosmos`
2. O usa el cargador de archivos en la app

### Warning: "`preventOverflow` modifier required"

**Causa**: Warning de Popper.js (Streamlit interno)

**Solución**: Ignorar, no afecta funcionalidad. Ver en F12 → Console

### App lenta al cargar

**Causas posibles**:

- Primera carga (normal, ~2-3 segundos)
- Archivo Excel muy grande
- PC con poca memoria RAM

**Soluciones**:

- Esperar a que cachee (carga siguiente es rápida)
- Usar archivo más pequeño
- Cerrar otras aplicaciones

### Estilos CSS no se aplican

**Causas posibles**:

- Navegador cache viejo
- CSS corrupto

**Soluciones**:

- Presiona: `Ctrl + F5` (hard refresh)
- Abre en navegación privada (Ctrl + Shift + P)
- Reinicia `streamlit run app.py`

---

## 📱 Uso en dispositivos diferentes

### Desde celular en la red local

1. En tu PC, obtén la IP:

```bash
ipconfig
```

2. En tu celular, conecta a la misma WiFi

3. En el navegador del celular, ingresa:

```
http://192.168.x.x:8501
```

(Reemplaza 192.168.x.x con tu IP)

---

## 🔐 Seguridad en producción

⚠️ **Advertencia**: Esta instalación es para desarrollo/uso interno.

Para producción, considera:

1. **Autenticación**: Agregar login

```python
import streamlit_authenticator as stauth
# Requiere contraseña
```

2. **HTTPS**: Usar servidor proxy (Nginx)

```bash
# No ejecutar directamente en puerto 80
streamlit run app.py --server.port 8501
```

3. **Base de datos segura**: No archivos Excel

- Migrar a PostgreSQL/SQLite con contraseña

4. **Validación de datos**: Verificar integridad de Excel

5. **Rate limiting**: Limitar descargas frecuentes

---

## 📝 Mantenimiento

### Actualizar dependencias (anual)

```bash
pip install --upgrade streamlit pandas plotly openpyxl fpdf
```

### Limpiar cache

```bash
# Windows
rmdir /s .streamlit\cache

# Mac/Linux
rm -rf .streamlit/cache
```

### Respaldar datos

Crear backup periódico de:

- `1-31 octubre.xlsx`
- `app.py`
- `estilos.css`
- Archivos Excel cargados

---

## ✅ Checklist de verificación

Después de instalar, verifica:

- [ ] Terminal sin errores
- [ ] Navegador abre automáticamente
- [ ] Logo COSMOS visible en header
- [ ] Isotipo visible en sidebar
- [ ] Filtros funcionan al cambiar valores
- [ ] Datos se actualizan en gráficos
- [ ] Botón "Descargar CSV" crea archivo
- [ ] Botón "Descargar PDF" crea reporte
- [ ] Puedo cargar archivo Excel externo
- [ ] Colores terracota en botones e inputs

Si todo ✅, ¡instalación completada!

---

## 📞 Soporte

### Ver logs en tiempo real

```bash
streamlit run app.py --logger.level=debug 2>&1 | tee app.log
```

### Datos de diagnóstico

Abre DevTools (F12) en el navegador → Console:

- Verifica que no haya errores rojos
- Presiona F5 si ves warnings

### Contacto

Para issues, verifica:

1. Que `1-31 octubre.xlsx` exista en carpeta root
2. Que todas las dependencias estén instaladas
3. Que el archivo Excel tenga la estructura correcta

---

**Documento**: Guía de Despliegue  
**Versión**: 1.0  
**Última actualización**: 18 de Marzo de 2026
