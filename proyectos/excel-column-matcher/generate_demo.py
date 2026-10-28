"""Create a synthetic Excel example. No company files or network access."""
import argparse
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def generate(path):
    out = Path(path)
    if out.exists():
        raise FileExistsError(f"Example already exists: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Demostracion"
    ws.append(["Catalogo", "Consultas"])
    for row in [
        ("Cafe Central", "cafe central"),
        ("Biblioteca Norte", "biblioteca norte"),
        ("Parque Verde", "parque ver"),
        ("Museo Azul", "nombre inexistente"),
    ]:
        ws.append(row)
    for cell in ws[1]:
        cell.font = Font(color="FFFFFF", bold=True)
        cell.fill = PatternFill("solid", fgColor="20334B")
    ws.column_dimensions["A"].width = 28
    ws.column_dimensions["B"].width = 28
    ws.freeze_panes = "A2"
    wb.save(out)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="demo_entrada.xlsx")
    args = parser.parse_args()
    print(f"Created: {generate(args.output)}")
