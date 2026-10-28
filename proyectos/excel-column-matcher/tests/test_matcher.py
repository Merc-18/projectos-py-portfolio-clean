import sys
from pathlib import Path
import tempfile
import unittest
from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from matcher import match_rows, normalize, process, safe_text


class MatcherTests(unittest.TestCase):
    def test_normalize_accents_and_punctuation(self):
        self.assertEqual(normalize(" Caf\u00e9 -- SUR! "), "cafe sur")

    def test_exact_match_after_normalization(self):
        self.assertEqual(match_rows([(2, "Caf\u00e9 Sur", "cafe sur")])[0][-1], "EXACTA")

    def test_similar_match(self):
        rows = [(2, "Biblioteca Norte", "Biblioteca Nort")]
        self.assertEqual(match_rows(rows)[0][-1], "SIMILAR")

    def test_unmatched_query(self):
        rows = [(2, "Mercado Rojo", "otra cosa")]
        self.assertEqual(match_rows(rows)[0][2], "")
        self.assertEqual(match_rows(rows)[0][-1], "SIN_COINCIDENCIA")

    def test_duplicate_queries_keep_rows(self):
        rows = [(2, "Casa Verde", "casa verde"), (3, "Casa Verde", "casa verde")]
        self.assertEqual([r[0] for r in match_rows(rows)], [2, 3])

    def test_skip_blank_query(self):
        self.assertEqual(len(match_rows([(2, "Casa", None)])), 0)

    def test_formula_safety(self):
        self.assertEqual(safe_text("=1+1"), "'=1+1")
        self.assertEqual(safe_text(" @SUM"), "' @SUM")

    def test_threshold_zero_has_no_false_match(self):
        self.assertEqual(match_rows([(2, None, "Unknown")], 0)[0][-1], "SIN_COINCIDENCIA")

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            match_rows([], 1.5)

    def test_end_to_end_xlsx(self):
        with tempfile.TemporaryDirectory() as td:
            inp, out = Path(td) / "input.xlsx", Path(td) / "result.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.append(["Catalog", "Query"])
            ws.append(["Alameda Este", "alameda este"])
            ws.append(["Valle Sur", "=1+1"])
            ws["B3"].data_type = "s"  # Treat synthetic formula-looking content as literal input text
            wb.save(inp)
            self.assertEqual(process(inp, out), 2)
            result = load_workbook(out)
            sheet = result.active
            self.assertEqual(sheet["E2"].value, "EXACTA")
            self.assertEqual(sheet["B3"].value, "'=1+1")
            self.assertEqual(sheet["B3"].data_type, "s")
            self.assertEqual(sheet.freeze_panes, "A2")
            self.assertTrue(inp.exists())
            with self.assertRaises(FileExistsError):
                process(inp, out)
            with self.assertRaises(ValueError):
                process(inp, inp)

    def test_reject_missing_sheet(self):
        with tempfile.TemporaryDirectory() as td:
            inp, out = Path(td) / "input.xlsx", Path(td) / "result.xlsx"
            wb = Workbook()
            wb.save(inp)
            with self.assertRaises(ValueError):
                process(inp, out, sheet_name="Unknown")


if __name__ == "__main__":
    unittest.main()
