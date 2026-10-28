"""Offline extraction of generic labeled fields from text-based PDFs."""
import argparse
import csv
from pathlib import Path
import re

import pdfplumber


FIELDS = ("Title", "Reference", "Date", "Location")
PATTERNS = {
    field: re.compile(rf"^\s*{re.escape(field)}\s*:\s*(\S.*)\s*$", re.IGNORECASE)
    for field in FIELDS
}
OUTPUT_COLUMNS = ("File", *FIELDS, "Status")


def safe_csv(value):
    """Stop spreadsheet apps treating extracted text as formulas."""
    text = str(value) if value is not None else ""
    return "'" + text if text.lstrip().startswith(("=", "+", "-", "@")) else text


def parse_text(text):
    fields = {field: "" for field in FIELDS}
    for line in text.splitlines():
        for field, pattern in PATTERNS.items():
            if not fields[field]:
                match = pattern.match(line)
                if match:
                    fields[field] = match.group(1).strip()
    return fields


def extract_pdf(path, max_pages=30):
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    source = Path(path)
    with pdfplumber.open(source) as pdf:
        pages = pdf.pages[:max_pages]
        text = "\n".join(page.extract_text() or "" for page in pages)
    fields = parse_text(text)
    status = "NO_TEXT" if not text.strip() else "COMPLETE" if all(fields.values()) else "PARTIAL"
    return {"File": source.name, **fields, "Status": status}


def list_pdfs(source):
    path = Path(source)
    if path.is_file() and path.suffix.lower() == ".pdf":
        return [path]
    if path.is_dir():
        return sorted((p for p in path.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"), key=lambda p: p.name.casefold())
    raise ValueError("Input must be a PDF file or a directory containing PDFs")


def process(source, output, overwrite=False, max_pages=30):
    target = Path(output).resolve()
    if target.suffix.lower() != ".csv":
        raise ValueError("Output must end with .csv")
    if target.exists() and not overwrite:
        raise FileExistsError("Output exists; use --overwrite to replace it")
    if max_pages < 1:
        raise ValueError("max_pages must be at least 1")
    paths = list_pdfs(source)
    if not paths:
        raise ValueError("Input directory contains no PDFs")
    rows = [extract_pdf(p, max_pages=max_pages) for p in paths]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: safe_csv(row[key]) for key in OUTPUT_COLUMNS})
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description="Extract generic fields from text PDFs (no OCR or network)")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--max-pages", type=int, default=30)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    rows = process(args.input, args.output, args.overwrite, args.max_pages)
    print(f"Processed {len(rows)} PDF(s); saved: {args.output}")


if __name__ == "__main__":
    main()
