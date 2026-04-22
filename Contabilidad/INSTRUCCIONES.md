# FYC Calzado – Tablero de Reporte de Labor

## ¿Qué hace esta aplicación?

Toma el archivo generado por **Siesa Access** (`1-31 octubre.xlsx`) y lo convierte en un tablero interactivo con filtros y gráficas.

## Cómo ejecutar

1. Abre una terminal (CMD o PowerShell) en la carpeta `Cosmos`.
2. Escribe el siguiente comando y presiona Enter:

```
streamlit run app.py
```

3. El navegador se abrirá automáticamente en `http://localhost:8501`.

## Funcionalidades del tablero

| Sección                        | Descripción                                                                                     |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| **Filtros (barra lateral)**    | Selecciona empleado(s), rango de fechas y tipo de agrupación                                    |
| **KPIs**                       | Total horas, jornada ordinaria, horas extras, dominicales, días laborados                       |
| **Gráfica por día/semana/mes** | Barras comparativas entre empleados según la agrupación elegida                                 |
| **Tab "Por día"**              | Tabla filtrable con detalle diario por persona                                                  |
| **Tab "Por semana"**           | Resumen de horas por semana ISO por persona                                                     |
| **Tab "Por mes"**              | Resumen de horas mensual por persona                                                            |
| **Tab "Detalle completo"**     | Todos los campos del reporte + botón de exportar a CSV                                          |
| **Distribución de horas**      | Gráfica apilada que muestra la composición de horas (ordinarias, extras, dominicales, festivos) |

## Para nuevos archivos de Siesa

Simplemente reemplaza el archivo `1-31 octubre.xlsx` con el nuevo archivo y vuelve a ejecutar `streamlit run app.py`.  
El sistema detecta automáticamente los empleados y columnas del reporte.

## Dependencias instaladas

- `streamlit`
- `pandas`
- `plotly`
- `openpyxl`
