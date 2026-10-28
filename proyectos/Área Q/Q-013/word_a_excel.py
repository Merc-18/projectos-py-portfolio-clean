"""Offline extraction of event details from Word tables to Excel.

Sanitized, portable adaptation of the original event-table extraction workflow.
No internal paths, accounts, organization names or data are required.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
from typing import Iterable

from docx import Document
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

EVENT_RE = re.compile(r"\b(?:EVENTO|CASO)\s+(\d+)\s*:\s*", re.IGNORECASE)
STAMP_RE = re.compile(
    r"(?P<datefirst>\b\d{1,2}/\d{1,2}/\d{4}\s+\d{2}:\d{2}:\d{2}\b)"
    r"|(?P<timefirst>\b\d{2}:\d{2}:\d{2}\s+(?:del\s+)?\d{1,2}/\d{1,2}/\d{4}\b)",
    re.IGNORECASE,
)
URL_RE = re.compile(r"https?://[^\s<>]+", re.IGNORECASE)
HEADINGS = ("OBSERVACIONES", "ACCIONES", "RESULTADO")
HEAD_RE = re.compile(r"(?im)^\s*(OBSERVACIONES|ACCIONES|RESULTADO)\s*:\s*")
OUTPUT_HEADERS = (
    "Zona", "Lugar", "Caso", "Inicio", "Fin", "Observaciones", "Acciones",
    "Resultado", "Enlaces",
)


def safe_cell(value: object) -> str:
    """Protect text from accidental spreadsheet formula execution."""
    s = str(value or "")
    return "'" + s if s.lstrip().startswith(("=", "+", "-", "@")) else s


def stamps(text: str) -> list[str]:
    found = []
    for match in STAMP_RE.finditer(text):
        raw = match.group(0)
        if match.group("timefirst"):
            hour, date = re.split(r"\s+(?:del\s+)?", raw, maxsplit=1)
        else:
            date, hour = raw.split(None, 1)
        day, month, year = date.split("/")
        found.append(f"{int(day):02d}/{int(month):02d}/{year} {hour}")
    return found


def fields(text: str) -> dict[str, str]:
    tokens = list(HEAD_RE.finditer(text))
    out = {k: "" for k in HEADINGS}
    for i, match in enumerate(tokens):
        key = match.group(1).upper()
        end = tokens[i + 1].start() if i + 1 < len(tokens) else len(text)
        out[key] = text[match.end():end].strip()
    return out


def parse_events(description: str, zone: str = "", location: str = "") -> list[dict[str, str]]:
    positions = list(EVENT_RE.finditer(description))
    rows: list[dict[str, str]] = []
    for i, match in enumerate(positions):
        end = positions[i + 1].start() if i + 1 < len(positions) else len(description)
        body = description[match.end():end]
        date_values = stamps(body)
        parsed = fields(body)
        links = [url.rstrip(".,);") for url in URL_RE.findall(body)]
        rows.append({
            "Zona": zone, "Lugar": location, "Caso": match.group(1),
            "Inicio": date_values[0] if date_values else "",
            "Fin": date_values[1] if len(date_values) > 1 else "",
            "Observaciones": parsed["OBSERVACIONES"],
            "Acciones": parsed["ACCIONES"],
            "Resultado": parsed["RESULTADO"],
            "Enlaces": "\n".join(links),
        })
    return rows


def from_docx(file: Path) -> list[dict[str, str]]:
    """Read document tables; first row is a heading row, first three cells hold data."""
    doc = Document(file)
    if not doc.tables:
        raise ValueError("El documento no tiene tablas")
    records = []
    for table in doc.tables:
        for row in table.rows[1:]:
            if len(row.cells) < 3:
                continue
            zone, location, description = [cell.text.strip() for cell in row.cells[:3]]
            if description:
                records.extend(parse_events(description, zone, location))
    return records


def export_xlsx(records: Iterable[dict[str, str]], output: Path, *, overwrite=False) -> int:
    rows = list(records)
    if output.suffix.lower() != ".xlsx":
        raise ValueError("La salida debe ser .xlsx")
    if output.exists() and not overwrite:
        raise FileExistsError("La salida ya existe; indicar --overwrite para reemplazar")
    wb = Workbook()
    ws = wb.active
    ws.title = "Casos"
    ws.append(OUTPUT_HEADERS)
    for item in rows:
        ws.append(tuple(safe_cell(item.get(k, "")) for k in OUTPUT_HEADERS))
    for cell in ws[1]:
        cell.font = Font(name="Aptos", bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="20354D")
        cell.alignment = Alignment(vertical="center")
    for col, width in zip("ABCDEFGHI", (18, 22, 10, 23, 23, 45, 45, 45, 40)):
        ws.column_dimensions[col].width = width
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:I{max(2, len(rows) + 1)}"
    output.parent.mkdir(parents=True, exist_ok=True)
    wb.save(output)
    return len(rows)


def process(input_file: Path, output_file: Path, *, overwrite=False) -> int:
    source = input_file.resolve()
    dest = output_file.resolve()
    if not source.is_file() or source.suffix.lower() != ".docx":
        raise ValueError("Indicar un archivo .docx existente")
    if source == dest:
        raise ValueError("La entrada y salida deben ser distintas")
    if dest.exists() and not overwrite:
        raise FileExistsError("La salida ya existe")
    rows = from_docx(source)
    if not rows:
        raise ValueError("No se encontraron casos: esperado CASO 1: / EVENTO 1:")
    return export_xlsx(rows, dest, overwrite=overwrite)


def main():
    parser = argparse.ArgumentParser(description="Word a Excel: eventos en tablas (offline)")
    parser.add_argument("input", type=Path, help="Archivo Word de prueba")
    parser.add_argument("output", type=Path, help="Nuevo archivo XLSX")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    count = process(args.input, args.output, overwrite=args.overwrite)
    print(f"Casos exportados: {count} → {args.output}")


if __name__ == "__main__":
    main()
