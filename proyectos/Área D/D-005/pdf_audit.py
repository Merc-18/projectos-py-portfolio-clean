"""Read-only PDF audit for date markers and explicit validity legends.

No editing, redaction, insertion or removal of original PDF content.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import re
import fitz

DATE_RE=re.compile(r'\b\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\b')
MARKERS=('sin validez','sin valor oficial','documento de ejemplo','documento ficticio')


def inspect_pdf(path:Path):
    with fitz.open(path) as doc:
        flags=[]
        for i,page in enumerate(doc):
            txt=page.get_text()
            dates=DATE_RE.findall(txt)
            labels=[marker for marker in MARKERS if marker in txt.casefold()]
            flags.append((i+1,len(dates),','.join(labels),'REVISAR' if labels or dates else 'SIN_MARCADORES'))
    return flags


def safe_csv(v):
    text=str(v)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def audit(source:Path,dest:Path):
    if not source.is_dir():raise ValueError('Carpeta inexistente')
    if dest.suffix.lower()!='.csv':raise ValueError('Archivo CSV requerido')
    if dest.exists():raise FileExistsError('El informe ya existe')
    pdfs=sorted(p for p in source.glob('*.pdf') if p.is_file() and not p.is_symlink())
    if not pdfs:raise ValueError('No hay PDFs')
    rows=[]
    for p in pdfs:
        for page,dates,labels,status in inspect_pdf(p):
            rows.append((p.name,page,dates,labels,status))
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(('Archivo','Página','Fechas visibles','Leyendas detectadas','Estado'))
        for row in rows:writer.writerow(tuple(safe_csv(x) for x in row))
    return len(rows)


def main():
    p=argparse.ArgumentParser(description='Auditoría read-only de leyendas y fechas PDF')
    p.add_argument('pdf_folder',type=Path);p.add_argument('output_csv',type=Path)
    a=p.parse_args();print('Páginas revisadas:',audit(a.pdf_folder,a.output_csv))


if __name__=='__main__':main()
