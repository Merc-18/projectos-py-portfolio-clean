"""Offline directory inventory with relative paths and Excel export."""

import argparse
import os
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

MAX_FOLDERS = 10000


def leaf_folders(root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Input directory does not exist")
    result = []
    # No symlink traversal: never follow references outside the chosen root.
    for current, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted((name for name in dirs if not (Path(current) / name).is_symlink()), key=str.casefold)
        if dirs:
            continue
        here = Path(current)
        filtered = [name for name in files if not (here / name).is_symlink() and name.casefold() not in
                    ("thumbs.db", "desktop.ini", ".ds_store")]
        pdf_count = sum(name.lower().endswith(".pdf") for name in filtered)
        relative = here.relative_to(root).as_posix() if here != root else "."
        result.append((relative, len(filtered), pdf_count))
        if len(result) > MAX_FOLDERS:
            raise ValueError(f"Too many leaf folders (limit {MAX_FOLDERS})")
    return sorted(result, key=lambda row: row[0].casefold())


def create_report(root, output, overwrite=False):
    target = Path(output).resolve()
    if target.suffix.lower() != ".xlsx":
        raise ValueError("Output must be .xlsx")
    if target.exists() and not overwrite:
        raise FileExistsError("Output exists; use --overwrite to replace it")
    leaves = leaf_folders(root)
    book = Workbook()
    ws = book.active
    ws.title = "Leaf Folders"
    ws.append(["Relative Directory", "File Count", "PDF Count"])
    for row in leaves:
        # Only relative directory names; no user home directory or drive details.
        ws.append([("'" + row[0]) if row[0].lstrip().startswith(("=", "+", "-", "@")) else row[0], row[1], row[2]])
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="20334B")
    for letter, width in (("A", 55), ("B", 17), ("C", 17)):
        ws.column_dimensions[letter].width = width
    target.parent.mkdir(parents=True, exist_ok=True)
    book.save(target)
    return leaves


def main(argv=None):
    parser = argparse.ArgumentParser(description="Inventory leaf directories into XLSX")
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    print(f"Inventoried {len(create_report(args.root, args.output, args.overwrite))} leaf folders")


if __name__ == "__main__":
    main()
