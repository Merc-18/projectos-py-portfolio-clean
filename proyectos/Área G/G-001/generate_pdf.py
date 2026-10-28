"""Generador PDF genérico de muestra sin plantillas ni tarifas corporativas."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def validate(description: str, amount: str) -> Decimal:
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 95:
        raise ValueError('La descripción debe tener entre 1 y 95 caracteres')
    try:
        value = Decimal(str(amount))
    except InvalidOperation as exc:
        raise ValueError('Importe inválido') from exc
    if not value.is_finite() or not (0 <= value <= 1000000):
        raise ValueError('Importe fuera del rango permitido')
    return value


def create_demo_pdf(description: str, amount: str, output: Path) -> Path:
    value = validate(description, amount)
    if output.suffix.lower() != '.pdf':
        raise ValueError('Se requiere un archivo PDF de salida')
    if output.exists():
        raise FileExistsError('No sobrescribir el PDF de salida')
    output.parent.mkdir(parents=True, exist_ok=True)
    page = canvas.Canvas(str(output), pagesize=A4)
    page.setTitle('Solicitud de muestra - Sin validez')
    page.setFont('Helvetica-Bold', 23)
    page.drawString(52, 760, 'SOLICITUD DE EJEMPLO')
    page.setFillColorRGB(.71, .16, .16)
    page.setFont('Helvetica-Bold', 17)
    page.drawString(52, 708, 'DEMO - SIN VALIDEZ OFICIAL')
    page.setFillColorRGB(.13, .2, .3)
    page.setFont('Helvetica', 12)
    # ReportLab's built-in Helvetica does not embed all accented characters.
    printable = description.encode('latin-1', 'replace').decode('latin-1')
    page.drawString(52, 633, 'Descripcion: ' + printable)
    page.drawString(52, 606, 'Monto ficticio: ' + format(value, '.2f'))
    page.drawString(52, 566, 'Este PDF fue creado solo para pruebas de software.')
    page.drawString(52, 545, 'No es un formato administrativo ni un documento autentico.')
    page.showPage()
    page.save()
    return output


def main(argv=None):
    p = argparse.ArgumentParser(description='Generador PDF de demostración')
    p.add_argument('salida', type=Path)
    p.add_argument('--descripcion', default='Registro ficticio')
    p.add_argument('--monto', default='0.00')
    a = p.parse_args(argv)
    print(create_demo_pdf(a.descripcion, a.monto, a.salida))


if __name__ == '__main__':
    main()
