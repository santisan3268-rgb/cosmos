import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from conta_core.sql_utils import classify_sql_concept, db_missing, normalize_doc_series, to_bool


class SqlUtilsTests(unittest.TestCase):
    def test_db_missing_reports_required_keys(self):
        missing = db_missing({"server": "srv", "name": None, "user": "usr", "password": None})
        self.assertEqual(missing, ["DB_NAME", "DB_PASSWORD"])

    def test_normalize_doc_series_strips_noise(self):
        series = pd.Series([" 12345.0 ", "10-20 30", "ab-99 "])
        out = normalize_doc_series(series).tolist()
        self.assertEqual(out, ["12345", "102030", "AB99"])

    def test_to_bool_understands_common_truthy_values(self):
        self.assertTrue(to_bool("true"))
        self.assertTrue(to_bool("Si"))
        self.assertFalse(to_bool("0"))
        self.assertTrue(to_bool(None, True))

    def test_classify_sql_concept_maps_expected_categories(self):
        self.assertEqual(classify_sql_concept("", "SALARIO BASICO", "SALBAS"), "DO")
        self.assertEqual(classify_sql_concept("", "RECARGO NOCTURNO", "REC NOCT"), "RNO")
        self.assertEqual(classify_sql_concept("", "HORA EXTRA DIURNA", "HED"), "HEDO")
        self.assertEqual(classify_sql_concept("", "DOMINGO COMPENSADO", "DOMCOMPE"), "OTRAS")


if __name__ == "__main__":
    unittest.main()
