"""Generate fictitious folder content, including a valid sample PDF."""
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas


def generate(root):
    root = Path(root)
    if root.exists():
        raise FileExistsError('Demo root already exists')
    north = root / 'region_alpha' / 'records'
    south = root / 'region_beta'
    north.mkdir(parents=True)
    south.mkdir(parents=True)
    document = north / 'example.pdf'
    pdf = canvas.Canvas(str(document))
    pdf.setTitle('Synthetic example')
    pdf.drawString(45, 760, 'Example PDF - no actual business records')
    pdf.save()
    (north / 'notes.txt').write_text('Fully synthetic folder example.\n', encoding='utf-8')
    (south / 'readme.txt').write_text('Test inventory.\n', encoding='utf-8')
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='demo_tree')
    args = parser.parse_args()
    print('Created:', generate(args.root))
