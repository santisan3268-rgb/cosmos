"""
db_utils.py — Persistencia de registros mensuales en SQLite.

Almacena dos tablas:
- registros_mensuales:    totales globales por (año, mes)
- registros_tienda_mes:   totales por tienda (Grupo) por (año, mes)

La BD se crea automáticamente en `Contabilidad/data/registros.db`.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
import shutil

import pandas as pd

DB_PATH = Path(__file__).parent.parent / "data" / "registros.db"
BACKUP_DIR = Path(__file__).parent.parent / "data" / "backups"

# Columnas de horas que se persisten (orden estable para SQL).
HORAS_GUARDADAS = [
    "DO", "RNO", "HEDO", "HENO", "DOM", "RNF", "HEDF", "HENF",
    "FEST", "RNDOM", "RDOM", "ODOM", "ORNF", "OEDF", "OFEST", "TOTAL",
]

# Conceptos relevantes para análisis de horas extras.
HORAS_EXTRAS = ["HEDO", "HENO", "HEDF", "HENF"]
RECARGOS = ["RNO", "RNF", "DOM", "FEST", "RNDOM", "RDOM"]
CONCEPTOS_COMPARACION = HORAS_EXTRAS + RECARGOS

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
}


@contextmanager
def _connect(db_path: Path | None = None):
    """Context manager que abre conexión SQLite, hace commit y la cierra siempre."""
    path = Path(db_path) if db_path else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Path | None = None) -> None:
    cols_sql = ", ".join(f'"{c}" REAL DEFAULT 0' for c in HORAS_GUARDADAS)
    with _connect(db_path) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS registros_mensuales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anio INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                fecha_carga TEXT NOT NULL,
                archivo_origen TEXT,
                {cols_sql},
                UNIQUE(anio, mes)
            )
            """
        )
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS registros_tienda_mes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anio INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                tienda TEXT NOT NULL,
                fecha_carga TEXT NOT NULL,
                {cols_sql},
                UNIQUE(anio, mes, tienda)
            )
            """
        )


def backup_db(db_path: Path | None = None, keep_last: int = 30) -> Path | None:
    """Crea un backup timestamped de la BD SQLite y conserva los últimos N."""
    path = Path(db_path) if db_path else DB_PATH
    if not path.exists():
        return None

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    target = BACKUP_DIR / f"registros_{ts}.db"
    shutil.copy2(path, target)

    backups = sorted(BACKUP_DIR.glob("registros_*.db"), key=lambda p: p.stat().st_mtime, reverse=True)
    for old in backups[keep_last:]:
        old.unlink(missing_ok=True)

    return target


def guardar_registro(
    df: pd.DataFrame,
    anio: int,
    mes: int,
    archivo_origen: str = "",
    db_path: Path | None = None,
) -> dict:
    """Filtra el DataFrame al período seleccionado y guarda totales (global + por tienda).

    Sobrescribe el registro si ya existe para ese (año, mes).
    Devuelve {'totales': dict, 'n_tiendas': int, 'filas_periodo': int}.
    """
    init_db(db_path)
    backup_db(db_path)
    if "Fecha" not in df.columns:
        raise ValueError("El archivo no tiene columna 'Fecha' parseable.")

    df_periodo = df[
        (df["Fecha"].dt.year == anio) & (df["Fecha"].dt.month == mes)
    ].copy()
    if df_periodo.empty:
        raise ValueError(
            f"No se encontraron filas en el archivo para {MESES_ES[mes]} {anio}."
        )

    fecha_carga = datetime.now().isoformat(timespec="seconds")
    cols_disp = [c for c in HORAS_GUARDADAS if c in df_periodo.columns]
    totales = {c: float(df_periodo[c].sum()) for c in cols_disp}

    n_tiendas = 0
    with _connect(db_path) as conn:
        # Global
        col_names = '"anio", "mes", "fecha_carga", "archivo_origen", ' + ", ".join(
            f'"{c}"' for c in cols_disp
        )
        placeholders = ", ".join(["?"] * (4 + len(cols_disp)))
        conn.execute(
            "DELETE FROM registros_mensuales WHERE anio = ? AND mes = ?", (anio, mes)
        )
        conn.execute(
            f"INSERT INTO registros_mensuales ({col_names}) VALUES ({placeholders})",
            [anio, mes, fecha_carga, archivo_origen] + [totales[c] for c in cols_disp],
        )

        # Por tienda
        conn.execute(
            "DELETE FROM registros_tienda_mes WHERE anio = ? AND mes = ?", (anio, mes)
        )
        if "Grupo" in df_periodo.columns:
            df_periodo["_Tienda"] = (
                df_periodo["Grupo"].fillna("(Sin grupo)").astype(str).str.strip()
            )
            df_periodo.loc[df_periodo["_Tienda"] == "", "_Tienda"] = "(Sin grupo)"
            agrupado = df_periodo.groupby("_Tienda", as_index=False)[cols_disp].sum()
            col_names_t = '"anio", "mes", "tienda", "fecha_carga", ' + ", ".join(
                f'"{c}"' for c in cols_disp
            )
            placeholders_t = ", ".join(["?"] * (4 + len(cols_disp)))
            for _, fila in agrupado.iterrows():
                conn.execute(
                    f"INSERT INTO registros_tienda_mes ({col_names_t}) VALUES ({placeholders_t})",
                    [anio, mes, str(fila["_Tienda"]), fecha_carga]
                    + [float(fila[c]) for c in cols_disp],
                )
            n_tiendas = len(agrupado)

    return {
        "totales": totales,
        "n_tiendas": n_tiendas,
        "filas_periodo": len(df_periodo),
    }


def listar_meses_guardados(db_path: Path | None = None) -> pd.DataFrame:
    """Lista los registros mensuales guardados (anio, mes, fecha_carga, archivo_origen)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        return pd.read_sql_query(
            """
            SELECT anio, mes, fecha_carga, archivo_origen
            FROM registros_mensuales
            ORDER BY anio DESC, mes DESC
            """,
            conn,
        )


def obtener_registro_global(
    anio: int, mes: int, db_path: Path | None = None
) -> pd.Series | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM registros_mensuales WHERE anio = ? AND mes = ?",
            (anio, mes),
        ).fetchone()
    return pd.Series(dict(row)) if row is not None else None


def obtener_registros_tienda(
    anio: int, mes: int, db_path: Path | None = None
) -> pd.DataFrame:
    init_db(db_path)
    with _connect(db_path) as conn:
        return pd.read_sql_query(
            "SELECT * FROM registros_tienda_mes WHERE anio = ? AND mes = ? ORDER BY tienda",
            conn,
            params=(anio, mes),
        )


def eliminar_registro(anio: int, mes: int, db_path: Path | None = None) -> None:
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            "DELETE FROM registros_mensuales WHERE anio = ? AND mes = ?", (anio, mes)
        )
        conn.execute(
            "DELETE FROM registros_tienda_mes WHERE anio = ? AND mes = ?", (anio, mes)
        )


def calcular_variacion(valor_anterior: float, valor_actual: float, umbral_pct: float = 2.0) -> dict:
    """Compara dos valores y clasifica el cambio.

    `valor_anterior` es la referencia (año A); `valor_actual` el comparado (año B).
    Devuelve diff absoluta, % y estado: 'crecio' / 'bajo' / 'se_sostuvo'.
    """
    diff = float(valor_actual) - float(valor_anterior)
    pct = 0.0 if valor_anterior == 0 else (diff / float(valor_anterior)) * 100.0
    if abs(pct) < umbral_pct:
        estado, emoji = "se_sostuvo", "➖"
    elif pct > 0:
        estado, emoji = "crecio", "📈"
    else:
        estado, emoji = "bajo", "📉"
    return {"diff": round(diff, 2), "pct": round(pct, 2), "estado": estado, "emoji": emoji}
