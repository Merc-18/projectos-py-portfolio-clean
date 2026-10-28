"""Offline link normalization, duplicate reporting and structural URL review."""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

TRACKING = {'utm_source','utm_medium','utm_campaign','utm_term','utm_content','gclid','fbclid'}


def canonical_url(raw: str) -> str:
    text = str(raw or '').strip()
    p = urlsplit(text)
    if p.scheme.lower() not in ('https','http') or not p.hostname or p.username or p.password:
        return ''
    if p.hostname in ('localhost',) or p.hostname.startswith('127.'):
        return ''
    params = [(k, v) for k, v in parse_qsl(p.query,keep_blank_values=True)
              if k.casefold() not in TRACKING]
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path.rstrip('/') or '/',
                       urlencode(sorted(params)),''))


def safe_cell(v: object) -> str:
    text = str(v if v is not None else '')
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def read_rows(path: Path):
    wb=load_workbook(path,read_only=True,data_only=True)
    try:
        ws=wb.active;ws.reset_dimensions();it=ws.iter_rows(values_only=True)
        header=next(it,None)
        if not header:raise ValueError('Excel vacío')
        column={str(x).strip().casefold():i for i,x in enumerate(header) if x is not None}
        if 'url' not in column:raise ValueError('Falta columna URL')
        for no,row in enumerate(it,start=2):
            val=row[column['url']] if len(row)>column['url'] else None
            if val is not None and str(val).strip():
                yield (no, str(val).strip(), str(row[column['autor']]).strip() if 'autor' in column and len(row)>column['autor'] and row[column['autor']] is not None else '')
    finally:wb.close()


def inspect(rows):
    found=defaultdict(list)
    details=[]
    for number,url,author in rows:
        key=canonical_url(url)
        details.append((number,url,author,key,'URL_VALIDO' if key else 'REVISAR_FORMATO'))
        if key:found[key].append(number)
    duplicates=[(k,','.join(map(str, numbers))) for k,numbers in sorted(found.items()) if len(numbers)>1]
    return details,duplicates


def save_report(details,duplicates,output:Path,*,overwrite=False):
    if output.suffix.lower()!='.xlsx':raise ValueError('Se requiere archivo .xlsx')
    if output.exists() and not overwrite:raise FileExistsError('Reporte ya existe')
    wb=Workbook();ws=wb.active;ws.title='Revision'
    ws.append(('Fila','URL','Autor','URL normalizada','Estado de formato'))
    for item in details:ws.append(tuple(safe_cell(v) for v in item))
    ds=wb.create_sheet('Duplicados');ds.append(('URL normalizada','Filas'))
    for item in duplicates:ds.append(tuple(safe_cell(v) for v in item))
    ss=wb.create_sheet('Resumen');ss.append(('Métrica','Total'))
    for name,value in [('Recursos',len(details)),('Duplicados',len(duplicates)),('URLs con formato válido',sum(bool(x[3]) for x in details))]:ss.append((name,value))
    for sheet in wb:
        sheet.freeze_panes='A2'
        for c in sheet[1]:c.font=Font(bold=True,color='FFFFFF');c.fill=PatternFill('solid',fgColor='20354D')
        for col,width in zip('ABCDE',(14,55,32,55,25)):sheet.column_dimensions[col].width=width
    output.parent.mkdir(parents=True,exist_ok=True);wb.save(output)


def process(src:Path,dst:Path,overwrite=False):
    items,duplicates=inspect(read_rows(src));save_report(items,duplicates,dst,overwrite=overwrite)
    return len(items),len(duplicates)


def main():
    p=argparse.ArgumentParser(description='Revisión sintáctica de URLs sin internet')
    p.add_argument('input',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--overwrite',action='store_true');a=p.parse_args()
    count,duplicates=process(a.input,a.output,overwrite=a.overwrite)
    print(f'Recursos: {count}; duplicados normalizados: {duplicates}; reporte: {a.output}')


if __name__=='__main__':main()
