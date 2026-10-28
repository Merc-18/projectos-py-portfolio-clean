"""Generate a fictitious XLSX PDF mapping, with duplicate filenames to test safe copies."""
import argparse
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from reportlab.pdfgen import canvas


def generate(root):
    root = Path(root)
    if root.exists():
        raise FileExistsError('Demo root already exists')
    pdf_root = root / 'pdf_input'
    for name, label in [('first/a.pdf', 'Document A'), ('second/a.pdf', 'Document B')]:
        target = pdf_root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        pdf = canvas.Canvas(str(target))
        pdf.setTitle('Synthetic example')
        pdf.drawString(48, 760, label)
        pdf.save()
    book = Workbook()
    ws = book.active
    ws.title = 'Mappings'
    ws.append(['Group ID', 'PDF 1', 'PDF 2'])
    ws.append(['DEMO-001', 'first/a.pdf', 'second/a.pdf'])
    for cell in ws[1]:
        cell.font = Font(bold=True, color='FFFFFF')
        cell.fill = PatternFill('solid', fgColor='20334B')
    for column in ('A', 'B', 'C'):
        ws.column_dimensions[column].width = 27
    book.save(root / 'mapping.xlsx')
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='demo_mappings')
    args = parser.parse_args()
    print('Created:', generate(args.root))
