"""Merge simple nested spreadsheet reports and report missing/filled templates."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from openpyxl import Workbook,load_workbook
from openpyxl.styles import PatternFill, Font


def rows_from_excel(path:Path):
    wb=load_workbook(path,read_only=True,data_only=True)
    try:
        sheet=wb.active;sheet.reset_dimensions();it=sheet.iter_rows(values_only=True)
        heads=next(it,None)
        if not heads:raise ValueError('Planilla vacía')
        cols={str(x).strip().casefold():i for i,x in enumerate(heads) if x is not None}
        if 'codigo' not in cols or 'observacion' not in cols:
            raise ValueError('Se necesitan Codigo y Observacion')
        for row in it:
            if row and any(x is not None for x in row):
                yield {key:(row[i] if i<len(row) else None) for key,i in cols.items()}
    finally:wb.close()


def collect(root:Path):
    if not root.is_dir():raise ValueError('Directorio de entrada inexistente')
    files=sorted(p for p in root.rglob('*.xlsx') if p.is_file() and not p.is_symlink() and not p.name.startswith('~$'))
    if not files:raise ValueError('No hay planillas')
    collected=[];empty=[]
    for f in files:
        relative=f.relative_to(root)
        rows=list(rows_from_excel(f))
        if not any(str(r.get('observacion') or '').strip() for r in rows):
            empty.append(relative.as_posix())
        for row in rows:
            code=str(row.get('codigo') or '').strip()
            observation=str(row.get('observacion') or '').strip()
            if code and observation:
                collected.append((relative.as_posix(),code,observation))
    return collected,empty,len(files)


def literal(v):
    s=str(v)
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s


def export(items,empty,total,output:Path):
    if output.suffix.lower()!='.xlsx':raise ValueError('Salida debe ser .xlsx')
    if output.exists():raise FileExistsError('Reporte existente')
    wb=Workbook();ws=wb.active;ws.title='Observaciones';ws.append(('Archivo','Codigo','Observacion'))
    for record in items:ws.append(tuple(literal(x) for x in record))
    s=wb.create_sheet('Resumen');s.append(('Métrica','Total'));s.append(('Archivos',total));s.append(('Con observaciones',total-len(empty)));s.append(('Vacíos',len(empty)))
    e=wb.create_sheet('Archivos vacíos');e.append(('Archivo',))
    for f in empty:e.append((literal(f),))
    for sh in wb:
        sh.freeze_panes='A2'
        for cell in sh[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='20354D')
        sh.column_dimensions['A'].width=43;sh.column_dimensions['B'].width=24;sh.column_dimensions['C'].width=70
    output.parent.mkdir(parents=True,exist_ok=True);wb.save(output)


def main():
    parser=argparse.ArgumentParser(description='Consolidación de reportes tabulares ficticios')
    parser.add_argument('folder',type=Path);parser.add_argument('report',type=Path)
    args=parser.parse_args();values=collect(args.folder);export(*values,args.report)
    print('Observaciones:',len(values[0]),'Planillas vacías:',len(values[1]))


if __name__=='__main__':main()
