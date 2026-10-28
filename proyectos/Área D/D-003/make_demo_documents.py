"""Create clearly non-official PDF demonstration documents from synthetic Excel."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
from openpyxl import load_workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CODE=re.compile(r'^[A-Za-z0-9_-]{1,32}$')


def entries(xlsx:Path):
    wb=load_workbook(xlsx,read_only=True,data_only=True)
    try:
        ws=wb.active;ws.reset_dimensions();it=ws.iter_rows(values_only=True)
        header=next(it,None)
        if not header:raise ValueError('Excel vacío')
        col={str(v).strip().casefold():i for i,v in enumerate(header) if v is not None}
        if any(c not in col for c in ('nombre','codigo')):raise ValueError('Requiere Nombre y Codigo')
        codes=set()
        for row in it:
            if not row or all(v is None for v in row):continue
            name=str(row[col['nombre']] or '').strip() if len(row)>col['nombre'] else ''
            code=str(row[col['codigo']] or '').strip() if len(row)>col['codigo'] else ''
            if not name or not CODE.fullmatch(code):raise ValueError('Fila sin nombre o código válido')
            if code in codes:raise ValueError('Código duplicado')
            codes.add(code)
            yield name,code
    finally:wb.close()


def prepare(xlsx:Path,output:Path):
    entries_list=list(entries(xlsx))
    if not entries_list:raise ValueError('No hay registros')
    targets=[output/f'demo_{code}.pdf' for _,code in entries_list]
    if len(set(targets))!=len(targets) or any(p.exists() for p in targets):
        raise FileExistsError('Hay archivos de salida existentes')
    return list(zip(entries_list,targets))


def draw_demo(file:Path,name:str,code:str):
    c=canvas.Canvas(str(file),pagesize=A4)
    w,h=A4
    c.setTitle('DOCUMENTO FICTICIO - SIN VALIDEZ')
    c.setFont('Helvetica-Bold',18)
    c.drawCentredString(w/2,h-125,'CONSTANCIA DE DEMOSTRACIÓN')
    c.setFont('Helvetica',12)
    c.drawCentredString(w/2,h-190,'Ejemplo local generado con datos sintéticos')
    # Use PDF-safe rendering for plain Latin characters; code/name are intentionally generic
    c.drawCentredString(w/2,h-245,'Registro: '+name[:58])
    c.drawCentredString(w/2,h-277,'Código ficticio: '+code)
    c.setFont('Helvetica-Bold',22)
    c.setFillColorRGB(.70,.14,.17)
    c.drawCentredString(w/2,h/2,'SIN VALIDEZ OFICIAL')
    c.setFillColorRGB(0,0,0)
    c.setFont('Helvetica',9)
    c.drawCentredString(w/2,100,'No contiene logos, firmas ni acreditaciones reales.')
    c.showPage();c.save()


def process(xlsx:Path,output:Path):
    plan=prepare(xlsx,output);output.mkdir(parents=True,exist_ok=True)
    for (name,code),dest in plan:draw_demo(dest,name,code)
    return len(plan)


def main():
    p=argparse.ArgumentParser(description='Generador de documentos PDF ficticios sin firmas')
    p.add_argument('excel',type=Path);p.add_argument('output_folder',type=Path)
    a=p.parse_args();print('PDF de demostración:',process(a.excel,a.output_folder))


if __name__=='__main__':main()
