"""Offline PDF organizer. Safe plan-only default; explicit --execute copies files."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from openpyxl import load_workbook

MAX_ROWS = 1000
MAX_PDF_BYTES = 100 * 1024 * 1024


@dataclass(frozen=True)
class PlannedCopy:
    group: str
    source: Path
    destination: Path


def safe_group(value):
    text = str(value).strip() if value is not None else ""
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", text):
        raise ValueError("Invalid group ID; use ASCII letters, numbers, '-' or '_'")
    return text


def safe_source(root, value):
    candidate = str(value).strip().replace("\\", "/")
    if not candidate or ":" in candidate:
        raise ValueError("Invalid PDF source path")
    relative = Path(candidate)
    if relative.is_absolute() or any(part in ("..", ".") for part in relative.parts):
        raise ValueError("Absolute paths and traversal are not allowed")
    source = (root / relative).resolve(strict=True)
    if not source.is_relative_to(root) or not source.is_file() or source.suffix.lower() != ".pdf":
        raise ValueError("PDF must be a file inside input root")
    if source.stat().st_size > MAX_PDF_BYTES:
        raise ValueError("PDF exceeds size limit")
    return source


def plan(excel_path, input_root, output_root):
    excel = Path(excel_path).resolve()
    root = Path(input_root).resolve()
    target_root = Path(output_root).resolve()
    if not excel.is_file() or excel.suffix.lower() != ".xlsx":
        raise ValueError("Excel source must be an existing .xlsx file")
    if not root.is_dir():
        raise ValueError("PDF input root must exist")
    if target_root == root or target_root.is_relative_to(root):
        raise ValueError("Output must be separate from input root")
    if Path(output_root).is_symlink():
        raise ValueError("Output must not be a symbolic link")
    book = load_workbook(excel, read_only=True, data_only=True)
    try:
        sheet = book.active
        if sheet.max_row > MAX_ROWS + 1:
            raise ValueError(f"Too many rows (limit {MAX_ROWS})")
        iterator = sheet.iter_rows(min_row=1, max_col=3, values_only=True)
        header = next(iterator, None)
        if not header or tuple(header[:3]) != ("Group ID", "PDF 1", "PDF 2"):
            raise ValueError("Excel headers must be Group ID / PDF 1 / PDF 2")
        reservations = set()
        operations = []
        for number, row in enumerate(iterator, start=2):
            group_raw = row[0]
            paths = [value for value in row[1:3] if value is not None and str(value).strip()]
            if group_raw is None and not paths:
                continue
            group = safe_group(group_raw)
            dest_dir = target_root / group
            if dest_dir.is_symlink():
                raise ValueError("Destination group folder must not be a symlink")
            for value in paths:
                source = safe_source(root, value)
                filename = source.name
                stem, suffix = Path(filename).stem, Path(filename).suffix
                number_suffix = 1
                destination = dest_dir / filename
                while destination in reservations or destination.exists() or destination.is_symlink():
                    number_suffix += 1
                    destination = dest_dir / f"{stem}_{number_suffix}{suffix}"
                reservations.add(destination)
                operations.append(PlannedCopy(group, source, destination))
    finally:
        book.close()
    return operations


def organize(excel, input_root, output_root, execute=False):
    operations = plan(excel, input_root, output_root)
    if not execute:
        return operations
    for operation in operations:
        operation.destination.parent.mkdir(parents=True, exist_ok=True)
        if operation.destination.parent.is_symlink():
            raise ValueError("Destination folder changed into symbolic link")
        # Exclusive create avoids overwriting a file created after planning.
        with operation.source.open("rb") as src, operation.destination.open("xb") as dst:
            shutil.copyfileobj(src, dst)
    return operations


def main(argv=None):
    parser = argparse.ArgumentParser(description="Plan safe PDF copies from an Excel mapping")
    parser.add_argument("excel", type=Path)
    parser.add_argument("pdf_root", type=Path)
    parser.add_argument("output_root", type=Path)
    parser.add_argument("--execute", action="store_true", help="Copy files after validating all mappings")
    args = parser.parse_args(argv)
    result = organize(args.excel, args.pdf_root, args.output_root, args.execute)
    print(f"{'Copied' if args.execute else 'Planned'} {len(result)} PDF(s)")
    for item in result:
        print(f"  {item.group}: {item.source.name} -> {item.destination.name}")


if __name__ == "__main__":
    main()
