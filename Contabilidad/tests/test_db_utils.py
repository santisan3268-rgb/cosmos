import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from conta_core.db_utils import (
    HORAS_GUARDADAS,
    calcular_variacion,
    eliminar_registro,
    guardar_registro,
    init_db,
    listar_meses_guardados,
    obtener_registro_global,
    obtener_registros_tienda,
)


def _df_demo() -> pd.DataFrame:
    fechas = pd.to_datetime(
        ["2025-01-05", "2025-01-12", "2025-01-19", "2025-02-02"]
    )
    return pd.DataFrame(
        {
            "Fecha": fechas,
            "Grupo": ["San Nicolás", "San Nicolás", "Centro", "Centro"],
            "Nombre": ["Ana", "Luis", "Marta", "Pedro"],
            "DO": [8.0, 8.0, 7.5, 8.0],
            "HEDO": [2.0, 1.5, 0.0, 0.5],
            "HENO": [0.5, 0.0, 0.0, 1.0],
            "HEDF": [0.0, 0.0, 1.0, 0.0],
            "HENF": [0.0, 0.0, 0.0, 0.0],
            "TOTAL": [10.5, 9.5, 8.5, 9.5],
        }
    )


class DbUtilsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "test.db"

    def tearDown(self):
        self._tmp.cleanup()

    def test_init_creates_tables(self):
        init_db(self.db_path)
        self.assertTrue(self.db_path.exists())

    def test_guardar_y_obtener_registro_global(self):
        info = guardar_registro(
            _df_demo(), 2025, 1, archivo_origen="test.xlsx", db_path=self.db_path
        )
        self.assertEqual(info["filas_periodo"], 3)  # solo enero
        self.assertEqual(info["n_tiendas"], 2)

        reg = obtener_registro_global(2025, 1, db_path=self.db_path)
        self.assertIsNotNone(reg)
        self.assertEqual(int(reg["anio"]), 2025)
        self.assertEqual(int(reg["mes"]), 1)
        self.assertAlmostEqual(float(reg["HEDO"]), 3.5)  # 2.0 + 1.5 + 0.0
        self.assertAlmostEqual(float(reg["TOTAL"]), 28.5)  # 10.5 + 9.5 + 8.5

    def test_obtener_tiendas(self):
        guardar_registro(_df_demo(), 2025, 1, db_path=self.db_path)
        tdf = obtener_registros_tienda(2025, 1, db_path=self.db_path)
        self.assertEqual(set(tdf["tienda"]), {"San Nicolás", "Centro"})
        san_nico = tdf[tdf["tienda"] == "San Nicolás"].iloc[0]
        self.assertAlmostEqual(float(san_nico["HEDO"]), 3.5)

    def test_sobrescribe_si_existe(self):
        guardar_registro(_df_demo(), 2025, 1, db_path=self.db_path)
        df_v2 = _df_demo()
        df_v2.loc[:, "HEDO"] = 99.0
        guardar_registro(df_v2, 2025, 1, db_path=self.db_path)

        reg = obtener_registro_global(2025, 1, db_path=self.db_path)
        # 3 filas en enero × 99
        self.assertAlmostEqual(float(reg["HEDO"]), 297.0)

        meses = listar_meses_guardados(db_path=self.db_path)
        self.assertEqual(len(meses), 1)  # no duplicó

    def test_eliminar_registro(self):
        guardar_registro(_df_demo(), 2025, 1, db_path=self.db_path)
        eliminar_registro(2025, 1, db_path=self.db_path)
        self.assertIsNone(obtener_registro_global(2025, 1, db_path=self.db_path))
        self.assertTrue(obtener_registros_tienda(2025, 1, db_path=self.db_path).empty)

    def test_error_si_no_hay_filas_en_periodo(self):
        with self.assertRaises(ValueError):
            guardar_registro(_df_demo(), 2030, 6, db_path=self.db_path)

    def test_listar_meses_ordenado(self):
        guardar_registro(_df_demo(), 2025, 1, db_path=self.db_path)
        guardar_registro(_df_demo(), 2025, 2, db_path=self.db_path)
        meses = listar_meses_guardados(db_path=self.db_path)
        self.assertEqual(list(meses["anio"]), [2025, 2025])
        self.assertEqual(list(meses["mes"]), [2, 1])  # desc

    def test_columnas_persistidas(self):
        guardar_registro(_df_demo(), 2025, 1, db_path=self.db_path)
        reg = obtener_registro_global(2025, 1, db_path=self.db_path)
        for c in HORAS_GUARDADAS:
            self.assertIn(c, reg.index)


class CalcularVariacionTests(unittest.TestCase):
    def test_crecimiento(self):
        v = calcular_variacion(100.0, 120.0)
        self.assertEqual(v["estado"], "crecio")
        self.assertEqual(v["diff"], 20.0)
        self.assertEqual(v["pct"], 20.0)

    def test_caida(self):
        v = calcular_variacion(100.0, 80.0)
        self.assertEqual(v["estado"], "bajo")
        self.assertEqual(v["pct"], -20.0)

    def test_se_sostuvo(self):
        v = calcular_variacion(100.0, 101.0, umbral_pct=2.0)
        self.assertEqual(v["estado"], "se_sostuvo")

    def test_division_por_cero(self):
        v = calcular_variacion(0.0, 50.0)
        self.assertEqual(v["pct"], 0.0)
        self.assertEqual(v["diff"], 50.0)


if __name__ == "__main__":
    unittest.main()
