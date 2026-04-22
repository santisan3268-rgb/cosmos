import os

import pandas as pd

try:
    import pytds
except ImportError:
    pytds = None


def get_secret_or_env(key: str, default=None):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.getenv(key, default)


def db_cfg() -> dict:
    return {
        "server": get_secret_or_env("DB_SERVER"),
        "port": int(get_secret_or_env("DB_PORT", "1433")),
        "name": get_secret_or_env("DB_NAME"),
        "user": get_secret_or_env("DB_USER"),
        "password": get_secret_or_env("DB_PASSWORD"),
    }


def db_missing(cfg: dict) -> list:
    missing = []
    if not cfg.get("server"):
        missing.append("DB_SERVER")
    if not cfg.get("name"):
        missing.append("DB_NAME")
    if not cfg.get("user"):
        missing.append("DB_USER")
    if not cfg.get("password"):
        missing.append("DB_PASSWORD")
    return missing


def normalize_doc_series(s: pd.Series) -> pd.Series:
    return (
        s.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"[^0-9A-Z]", "", regex=True)
    )


def to_bool(value, default: bool = True) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "si", "on"}


def sql_connect(cfg: dict):
    if pytds is None:
        raise ImportError("python-tds no esta instalado")

    validate_host = to_bool(get_secret_or_env("DB_VALIDATE_HOST", True), True)
    return pytds.connect(
        server=cfg["server"],
        port=cfg["port"],
        database=cfg["name"],
        user=cfg["user"],
        password=cfg["password"],
        validate_host=validate_host,
    )


def classify_sql_concept(concept_id: str, concept_desc: str, concept_abbr: str) -> str:
    abbr = str(concept_abbr or "").upper().strip()
    txt = " ".join(str(x or "") for x in [concept_id, concept_desc, concept_abbr]).upper()
    txt = " ".join(txt.split())

    if abbr in {"SALBAS"}:
        return "DO"
    if abbr in {"REC NOCT", "RNO"}:
        return "RNO"
    if abbr in {"HED", "HEDO"}:
        return "HEDO"
    if abbr in {"HEN", "HENO"}:
        return "HENO"
    if abbr in {"RNF", "RNFS"}:
        return "RNF"
    if abbr in {"HEDF"}:
        return "HEDF"
    if abbr in {"HENF"}:
        return "HENF"
    if abbr in {"HEDN", "RNDOM"}:
        return "RNDOM"
    if abbr in {"HEDD", "RDOM"}:
        return "RDOM"
    if abbr in {"ODOM"}:
        return "ODOM"
    if abbr in {"FEST"}:
        return "FEST"
    if abbr in {"OFEST"}:
        return "OFEST"
    if abbr in {"ORNF"}:
        return "ORNF"
    if abbr in {
        "DOMCOMPE", "VAC", "VAC ", "CUOTA S", "LIC MATER", "LIC DFLIA",
        "LIC CAL DOM", "LIC N REM", "INCAP G 66%", "INCAP ACCI T", "HECAPAC",
    }:
        return "OTRAS"

    if "RNDOM" in txt or ("RECARGO" in txt and "NOCT" in txt and ("DOM" in txt or "DOMINICAL" in txt)):
        return "RNDOM"
    if "RDOM" in txt or ("RECARGO" in txt and ("DOM" in txt or "DOMINICAL" in txt)):
        return "RDOM"
    if "RNF" in txt or ("RECARGO" in txt and "NOCT" in txt and "FEST" in txt):
        return "RNF"
    if "HEDF" in txt or ("HORA EXTRA DIURNA" in txt and "FEST" in txt):
        return "HEDF"
    if "HENF" in txt or ("HORA EXTRA NOCTURNA" in txt and "FEST" in txt):
        return "HENF"
    if "OFEST" in txt:
        return "OFEST"
    if "RECARGO NOCTURNO" in txt and "DOM" not in txt and "FEST" not in txt:
        return "RNO"
    if "HORA EXTRA DIURNA" in txt and "DOM" not in txt and "FEST" not in txt:
        return "HEDO"
    if "HORA EXTRA NOCTURNA" in txt and "DOM" not in txt and "FEST" not in txt:
        return "HENO"
    if "DOMING" in txt or "DOMINICAL" in txt:
        return "DOM"
    if "FEST" in txt:
        return "FEST"
    if "SALARIO BASICO" in txt or "JORNADA" in txt:
        return "DO"
    return "OTRAS"


def fetch_sql_hours(cfg: dict, fecha_ini, fecha_fin) -> pd.DataFrame:
    conn = sql_connect(cfg)
    cur = conn.cursor()
    query = """
    SELECT
        CAST(m.c0602_fecha AS date) AS Fecha,
        t.f200_nit AS Documento,
        LTRIM(RTRIM(CONCAT(ISNULL(t.f200_nombres, ''), ' ', ISNULL(t.f200_apellido1, ''), ' ', ISNULL(t.f200_apellido2, '')))) AS Nombre,
        c.c0501_id AS ConceptoID,
        c.c0501_descripcion AS Concepto,
        c.c0501_abreviatura AS Abreviatura,
        SUM(ISNULL(m.c0602_horas, 0)) AS Horas
    FROM dbo.w0602_movto_nomina m
    INNER JOIN dbo.w0501_conceptos c ON c.c0501_rowid = m.c0602_rowid_concepto
    LEFT JOIN dbo.t200_mm_terceros t ON t.f200_rowid = m.c0602_rowid_tercero AND t.f200_id_cia = m.c0602_id_cia
    WHERE m.c0602_horas IS NOT NULL
      AND m.c0602_horas > 0
      AND CAST(m.c0602_fecha AS date) BETWEEN %s AND %s
    GROUP BY
        CAST(m.c0602_fecha AS date),
        t.f200_nit,
        t.f200_nombres,
        t.f200_apellido1,
        t.f200_apellido2,
        c.c0501_id,
        c.c0501_descripcion,
        c.c0501_abreviatura
    """
    cur.execute(query, (fecha_ini, fecha_fin))
    rows = cur.fetchall()
    conn.close()

    raw = pd.DataFrame(rows, columns=["Fecha", "Documento", "Nombre", "ConceptoID", "Concepto", "Abreviatura", "Horas"])
    if raw.empty:
        return raw

    raw["Fecha"] = pd.to_datetime(raw["Fecha"])
    raw["Categoria"] = raw.apply(
        lambda r: classify_sql_concept(r["ConceptoID"], r["Concepto"], r["Abreviatura"]),
        axis=1,
    )

    out = (
        raw.groupby(["Fecha", "Documento", "Nombre", "Categoria"], as_index=False)["Horas"]
        .sum()
        .pivot_table(index=["Fecha", "Documento", "Nombre"], columns="Categoria", values="Horas", fill_value=0)
        .reset_index()
    )
    out.columns = [str(c) for c in out.columns]
    for col in ["DO", "RNO", "HEDO", "HENO", "DOM", "RNF", "HEDF", "HENF", "FEST", "RNDOM", "RDOM", "ODOM", "ORNF", "OFEST", "OTRAS"]:
        if col not in out.columns:
            out[col] = 0.0
    out["TOTAL"] = out[["DO", "RNO", "HEDO", "HENO", "DOM", "RNF", "HEDF", "HENF", "FEST", "RNDOM", "RDOM", "ODOM", "ORNF", "OFEST"]].sum(axis=1)
    out["Mes"] = out["Fecha"].dt.to_period("M").astype(str)
    return out
