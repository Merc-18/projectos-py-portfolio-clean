"""Generate synthetic one-page text PDFs for an offline demo."""
import argparse
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def make_pdf(path, values):
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"Example already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(path), pagesize=A4)
    pdf.setTitle("Synthetic example document")
    pdf.setAuthor("Portfolio Demo")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(56, 780, "Synthetic Document")
    pdf.setFont("Helvetica", 12)
    for i, (name, value) in enumerate(values.items()):
        pdf.drawString(56, 730 - i * 34, f"{name}: {value}")
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(56, 560, "All names, references and dates are fictitious.")
    pdf.save()
    return path


def generate(directory):
    folder = Path(directory)
    return [
        make_pdf(folder / "example_complete.pdf", {
            "Title": "Equipment Inspection Example",
            "Reference": "DEMO-2026-001",
            "Date": "2026-01-15",
            "Location": "Example City",
        }),
        make_pdf(folder / "example_partial.pdf", {
            "Title": "Incomplete Example",
            "Reference": "DEMO-2026-002",
        }),
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default="demo_pdfs")
    args = parser.parse_args()
    for file in generate(args.dir):
        print(f"Created: {file}")
