"""Generate fictitious PDFs for testing classification; no real certificates."""
import argparse
from pathlib import Path
from reportlab.pdfgen import canvas


def generate(root):
    root = Path(root)
    if root.exists():
        raise FileExistsError('Demo root already exists')
    root.mkdir(parents=True)
    for filename, message in [('certificacion_demostracion.pdf', 'Demo certificate candidate'),
                              ('informacion_general.pdf', 'Other example document')]:
        pdf = canvas.Canvas(str(root / filename))
        pdf.setTitle('Synthetic PDF')
        pdf.drawString(48, 760, message)
        pdf.drawString(48, 730, 'For testing only - no real information')
        pdf.save()
    (root / 'instructions.txt').write_text('Synthetic example; never delete actual records.\n', encoding='utf-8')
    return root


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', default='demo_documents')
    args = parser.parse_args()
    print('Created:', generate(args.root))
