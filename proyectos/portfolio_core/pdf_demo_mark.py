"""Add an explicit non-signature demonstration mark to a copy of a PDF."""
from __future__ import annotations
from pathlib import Path
import fitz

POSITIONS={
    'lower-left':lambda page: fitz.Point(42,page.rect.height-58),
    'lower-right':lambda page: fitz.Point(max(42,page.rect.width-240),page.rect.height-58),
    'upper-right':lambda page: fitz.Point(max(42,page.rect.width-240),68),
}


def mark_demo(src:Path,dest:Path,position:str):
    if position not in POSITIONS:raise ValueError('Posición inválida')
    if src.resolve()==dest.resolve() or src.suffix.lower()!='.pdf' or dest.suffix.lower()!='.pdf':
        raise ValueError('Origen y destino deben ser PDFs diferentes')
    if dest.exists():raise FileExistsError('El PDF de salida ya existe')
    with fitz.open(src) as document:
        if not document.page_count:raise ValueError('No hay páginas')
        total_pages=document.page_count
        for page in document:
            page.insert_text(POSITIONS[position](page),'MUESTRA - SIN FIRMA',fontsize=11,color=(0.8,0.12,0.12))
            # The overlay is intentional text, never a scanned or electronic signature
        dest.parent.mkdir(parents=True,exist_ok=True)
        document.save(dest)
    return total_pages
