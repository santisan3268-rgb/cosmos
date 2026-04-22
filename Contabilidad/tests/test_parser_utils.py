import io
import sys
import unittest
from pathlib import Path

from openpyxl import Workbook
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from conta_core.parser_utils import parse_excel_file, prepare_loaded_dataframe


class ParserUtilsTests(unittest.TestCase):
    def _build_excel(self) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "ReporteXML"
        rows = [
            ["Nombre: Ana Perez"],
            ["Documento: 12345"],
            ["Grupo:  Tienda   Centro  "],
            [None, "Fecha", "DO", "TOTAL"],
            ["lunes", "02/03/2026", 8, 8],
            ["martes", "02/04/2026", 7.5, 7.5],
        ]
        for row in rows:
            ws.append(row)
        data = io.BytesIO()
        wb.save(data)
        data.seek(0)
        return data

    def test_parse_excel_file_extracts_records_and_numeric_columns(self):
        excel_file = self._build_excel()
        df = parse_excel_file(excel_file)

        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["Nombre"], "Ana Perez")
        self.assertEqual(df.iloc[0]["Documento"], "12345")
        self.assertEqual(df.iloc[0]["Grupo"], "Tienda Centro")
        self.assertEqual(df.iloc[0]["Día"], "Lunes")
        self.assertAlmostEqual(df.iloc[0]["DO"], 8.0)
        self.assertAlmostEqual(df.iloc[1]["TOTAL"], 7.5)
        self.assertIn("Semana_etiqueta", df.columns)
        self.assertIn("Mes", df.columns)

    def test_prepare_loaded_dataframe_normalizes_group_and_hours(self):
        df = pd.DataFrame(
            {
                "Grupo": ["  Principal   Norte  ", None],
                "DO": [8, 6],
                "TOTAL": [8, 6],
            }
        )

        prepared, horas = prepare_loaded_dataframe(df)

        self.assertEqual(prepared.iloc[0]["Grupo"], "Principal Norte")
        self.assertEqual(prepared.iloc[1]["Grupo"], "(Sin grupo)")
        self.assertIn("DO", horas)
        self.assertIn("TOTAL", horas)


if __name__ == "__main__":
    unittest.main()
