"""Generate fictitious Excel inputs for the offline consolidator."""
import argparse
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill


def generate(folder):
    folder = Path(folder)
    samples = {
        'first.xlsx': {'Inventory': [['Item', 'Quantity'], ['Pens', 15], ['Paper', 20]]},
        'second.xlsx': {'Supplies': [['Item', 'Warehouse'], ['Stapler', 'North'], ['Folders', 'South']]},
    }
    paths = [folder / filename for filename in samples]
    if any(path.exists() for path in paths):
        raise FileExistsError('One or more demo files already exist')
    folder.mkdir(parents=True, exist_ok=True)
    for filename, sheets in samples.items():
        wb = Workbook()
        for index, (name, rows) in enumerate(sheets.items()):
            ws = wb.active if index == 0 else wb.create_sheet()
            ws.title = name
            for row in rows:
                ws.append(row)
            for cell in ws[1]:
                cell.font = Font(bold=True, color='FFFFFF')
                cell.fill = PatternFill('solid', fgColor='20334B')
            ws.column_dimensions['A'].width = 24
            ws.column_dimensions['B'].width = 20
        wb.save(folder / filename)
    return paths


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dir', default='demo_input')
    args = parser.parse_args()
    for path in generate(args.dir):
        print('Created:', path)
