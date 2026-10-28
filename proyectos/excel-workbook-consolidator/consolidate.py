"""Offline workbook consolidation from independently specified Excel files."""

import argparse
from pathlib import Path
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

MAX_FILES = 100
MAX_ROWS = 30000


def as_text(value):
    """Avoid Excel formula injection from untrusted source cells."""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


def discover_files(source, destination):
    folder = Path(source).resolve()
    target = Path(destination).resolve()
    if not folder.is_dir():
        raise ValueError("Input directory does not exist")
    files = sorted((p for p in folder.iterdir()
                    if p.is_file() and not p.is_symlink() and p.suffix.lower() == ".xlsx"
                    and not p.name.startswith("~$") and p.resolve() != target),
                   key=lambda p: p.name.casefold())
    if not files:
        raise ValueError("No XLSX files found")
    if len(files) > MAX_FILES:
        raise ValueError(f"Too many input files (limit {MAX_FILES})")
    return files


def consolidate(source, destination, overwrite=False):
    target = Path(destination).resolve()
    if target.suffix.lower() != ".xlsx":
        raise ValueError("Output must be .xlsx")
    if target.exists() and not overwrite:
        raise FileExistsError("Output exists; use --overwrite to replace it")
    inputs = discover_files(source, target)
    columns = []
    rows = []
    for file in inputs:
        book = load_workbook(file, read_only=True, data_only=True)
        try:
            for sheet in book.worksheets:
                data = sheet.iter_rows(values_only=True)
                header = next(data, None)
                if header is None or not any(x is not None for x in header):
                    continue
                keys = [str(v).strip() if v is not None and str(v).strip() else f"Col_{i}"
                        for i, v in enumerate(header, start=1)]
                if len(set(keys)) != len(keys):
                    raise ValueError("Duplicate column names in input")
                for name in keys:
                    if name not in columns:
                        columns.append(name)
                for values in data:
                    if all(value is None for value in values):
                        continue
                    rows.append((file.name, sheet.title, dict(zip(keys, values))))
                    if len(rows) > MAX_ROWS:
                        raise ValueError(f"Too many rows (limit {MAX_ROWS})")
        finally:
            book.close()
    if not columns:
        raise ValueError("No sheets with headers found")
    if any(col in ("Source File", "Source Sheet") for col in columns):
        raise ValueError("Input contains reserved provenance column name")
    out = Workbook()
    ws = out.active
    ws.title = "Consolidated"
    ws.append(["Source File", "Source Sheet", *[as_text(c) for c in columns]])
    for file_name, sheet_name, values in rows:
        ws.append([as_text(file_name), as_text(sheet_name), *[as_text(values.get(col)) for col in columns]])
    ws.freeze_panes = "C2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill("solid", fgColor="20334B")
        cell.alignment = Alignment(vertical="center")
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 25
    for idx in range(3, len(columns) + 3):
        ws.column_dimensions[ws.cell(1, idx).column_letter].width = 28
    target.parent.mkdir(parents=True, exist_ok=True)
    out.save(target)
    return {"files": len(inputs), "rows": len(rows), "columns": len(columns)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Consolidate XLSX files offline")
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    print(consolidate(args.input_dir, args.output, args.overwrite))


if __name__ == "__main__":
    main()
