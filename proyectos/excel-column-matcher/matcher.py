"""Offline Excel column matching demo. Processes only explicitly selected files."""

import argparse
from difflib import SequenceMatcher
from pathlib import Path
import re
import unicodedata

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill


HEADERS = ("Fila", "Valor B", "Mejor coincidencia A", "Similitud", "Resultado")


def normalize(value):
    """Case/diacritic/punctuation-insensitive comparison key."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value).casefold())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def safe_text(value):
    """Prevent untrusted spreadsheet text from becoming a formula."""
    result = str(value) if value is not None else ""
    if result.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + result
    return result


def match_rows(rows, threshold=0.80):
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")
    rows = list(rows)
    sources = []
    seen = set()
    for _, a, _ in rows:
        key = normalize(a)
        if key and key not in seen:
            sources.append((key, safe_text(a)))
            seen.add(key)

    results = []
    for row_number, _, query in rows:
        qkey = normalize(query)
        if not qkey:
            continue
        candidate = ""
        score = 0.0
        for key, raw in sources:
            current = SequenceMatcher(None, qkey, key).ratio()
            if current > score:
                candidate, score = raw, current
        status = "EXACTA" if candidate and score == 1 else "SIMILAR" if candidate and score >= threshold else "SIN_COINCIDENCIA"
        results.append((row_number, safe_text(query), candidate if candidate and score >= threshold else "", round(score, 4), status))
    return results


def process(input_path, output_path, threshold=0.80, sheet_name=None, overwrite=False):
    source = Path(input_path).resolve()
    target = Path(output_path).resolve()
    if not source.is_file() or source.suffix.lower() != ".xlsx":
        raise ValueError("Input must be an existing .xlsx file")
    if target.suffix.lower() != ".xlsx":
        raise ValueError("Output must end with .xlsx")
    if source == target:
        raise ValueError("Input and output must be different files")
    if target.exists() and not overwrite:
        raise FileExistsError("Output exists; use --overwrite to replace it")
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be between 0 and 1")

    book = load_workbook(source, read_only=True, data_only=True)
    try:
        if sheet_name and sheet_name not in book.sheetnames:
            raise ValueError("Requested sheet does not exist")
        sheet = book[sheet_name] if sheet_name else book.active
        if sheet.max_column < 2:
            raise ValueError("Input sheet requires columns A and B")
        records = [(i, row[0], row[1]) for i, row in enumerate(
            sheet.iter_rows(min_row=2, min_col=1, max_col=2, values_only=True), start=2)]
    finally:
        book.close()

    results = match_rows(records, threshold)
    result_book = Workbook()
    ws = result_book.active
    ws.title = "Coincidencias"
    ws.append(HEADERS)
    for record in results:
        ws.append(record)
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:E{max(2, len(results) + 1)}"
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="20334B")
        cell.alignment = Alignment(vertical="center")
    for col, width in {"A": 10, "B": 31, "C": 33, "D": 15, "E": 24}.items():
        ws.column_dimensions[col].width = width
    for row in ws.iter_rows(min_row=2, min_col=4, max_col=4):
        row[0].number_format = "0.0%"
    target.parent.mkdir(parents=True, exist_ok=True)
    result_book.save(target)
    return len(results)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Compare Excel columns A and B without network access")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--threshold", type=float, default=0.80)
    parser.add_argument("--sheet", default=None)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    count = process(args.input, args.output, args.threshold, args.sheet, args.overwrite)
    print(f"Processed {count} rows; saved: {args.output}")


if __name__ == "__main__":
    main()
