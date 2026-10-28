import csv
import sys
from pathlib import Path
import tempfile
import unittest
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from extractor import extract_pdf, list_pdfs, parse_text, process, safe_csv


def pdf_with_lines(path, lines):
    pdf = canvas.Canvas(str(path))
    for i, line in enumerate(lines):
        pdf.drawString(54, 750 - i * 25, line)
    pdf.save()


class ExtractorTests(unittest.TestCase):
    def test_parse_all_labeled_fields(self):
        text = "Title: Test Document\nReference: DEMO-8\nDate: 2026-03-01\nLocation: Example Town"
        self.assertEqual(parse_text(text)["Reference"], "DEMO-8")
        self.assertEqual(len([v for v in parse_text(text).values() if v]), 4)

    def test_parse_case_insensitive(self):
        self.assertEqual(parse_text("title: hello")["Title"], "hello")

    def test_empty_fields(self):
        self.assertEqual(parse_text("Some text without fields")["Date"], "")

    def test_csv_formula_safety(self):
        self.assertEqual(safe_csv("=SUM(1,2)"), "'=SUM(1,2)")
        self.assertEqual(safe_csv(" @cmd"), "' @cmd")

    def test_complete_pdf(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "demo.pdf"
            pdf_with_lines(p, ["Title: Demo", "Reference: DEMO-1", "Date: 2026-01-15", "Location: Example City"])
            record = extract_pdf(p)
            self.assertEqual(record["Status"], "COMPLETE")
            self.assertEqual(record["Reference"], "DEMO-1")

    def test_partial_pdf(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "partial.pdf"
            pdf_with_lines(p, ["Title: Incomplete"])
            self.assertEqual(extract_pdf(p)["Status"], "PARTIAL")

    def test_blank_pdf_not_misreported_complete(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "blank.pdf"
            pdf_with_lines(p, [])
            self.assertEqual(extract_pdf(p)["Status"], "NO_TEXT")

    def test_batch_csv_and_overwrite_protection(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pdf_with_lines(root / "A.pdf", ["Title: Example", "Reference: DEMO", "Date: 2026-01-01", "Location: One"])
            pdf_with_lines(root / "B.PDF", ["Title: Another"])
            self.assertEqual(len(list_pdfs(root)), 2)
            out = root / "out.csv"
            records = process(root, out)
            self.assertEqual([r["File"] for r in records], ["A.pdf", "B.PDF"])
            with out.open(encoding="utf-8-sig", newline="") as f:
                self.assertEqual(len(list(csv.DictReader(f))), 2)
            with self.assertRaises(FileExistsError):
                process(root, out)

    def test_reject_non_pdf_input(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                list_pdfs(Path(td) / "missing.txt")

    def test_page_limit(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "demo.pdf"
            pdf_with_lines(p, ["Title: Demo"])
            with self.assertRaises(ValueError):
                extract_pdf(p, max_pages=0)


if __name__ == "__main__":
    unittest.main()
