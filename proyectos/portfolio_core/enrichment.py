"""Reconcile synthetic report codes with a public, generic reference mapping.

Single common engine prevents duplicated logic across four historical variants.
"""
from __future__ import annotations

from datetime import date, datetime, time
from pathlib import Path
import re
import unicodedata

from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font


def key(value) -> str:
    if value is None:return ''
    text=unicodedata.normalize('NFKD',str(value))
    text=''.join(c for c in text if not unicodedata.combining(c))
    return re.sub(r'\s+',' ',text.strip()).casefold()


def literal(value):
    if value is None:return ''
    text=str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def read_rows(path:Path):
    if not path.is_file() or path.suffix.lower()!='.xlsx':raise ValueError('Se requiere un .xlsx existente')
    book=load_workbook(path,read_only=True,data_only=True)
    try:
        sheet=book.active;sheet.reset_dimensions();stream=sheet.iter_rows(values_only=True)
        headings=next(stream,None)
        if headings is None:raise ValueError('La planilla está vacía')
        heads=[str(x).strip() if x is not None else '' for x in headings]
        for row in stream:
            if not row or all(x is None for x in row):continue
            yield dict(zip(heads,row))
    finally:book.close()


def load_map(master:Path)->dict:
    values={}
    for row in read_rows(master):
        normalized={key(k):v for k,v in row.items()}
        code=key(normalized.get('codigo'))
        group=str(normalized.get('grupo') or '').strip()
        if not code or not group:continue
        if code in values and values[code]!=group:
            raise ValueError('El código de referencia tiene asignaciones contradictorias')
        values[code]=group
    if not values:raise ValueError('Archivo maestro sin referencias válidas')
    return values


def format_temporal(value,kind):
    if value is None:return ''
    if isinstance(value,datetime):return value.strftime('%d/%m/%Y' if kind=='date' else '%H:%M:%S')
    if isinstance(value,date) and kind=='date':return value.strftime('%d/%m/%Y')
    if isinstance(value,time) and kind=='time':return value.strftime('%H:%M:%S')
    text=str(value).strip()
    formats=('%d/%m/%Y','%Y-%m-%d','%d-%m-%Y') if kind=='date' else ('%H:%M:%S','%H:%M')
    for fmt in formats:
        try:return datetime.strptime(text,fmt).strftime('%d/%m/%Y' if kind=='date' else '%H:%M:%S')
        except ValueError:pass
    return text


def enrich_rows(rows,mapping,*,normalize_dates=False,multi_codes=False):
    output=[]
    for row in rows:
        lookup={key(k):k for k in row}
        col=lookup.get('codigo')
        if col is None:raise ValueError('El reporte debe tener columna Codigo')
        raw=str(row.get(col) or '').strip()
        codes=re.split(r'[,;|]',raw) if multi_codes else [raw]
        groups={mapping.get(key(c)) for c in codes if key(c) and mapping.get(key(c))}
        result=dict(row)
        if not groups:result['Grupo asignado']='';result['Estado']='SIN_MAPEO'
        elif len(groups)>1:result['Grupo asignado']='';result['Estado']='AMBIGUO'
        else:result['Grupo asignado']=next(iter(groups));result['Estado']='ASIGNADO'
        if normalize_dates:
            for k,v in list(result.items()):
                norm=key(k)
                if norm in ('inicio','fin','fecha inicio','fecha fin'):
                    result[k]=format_temporal(v,'date')
                elif norm in ('hora inicio','hora fin'):
                    result[k]=format_temporal(v,'time')
        output.append(result)
    return output


def save_excel(rows,path:Path):
    if not rows:raise ValueError('No hay filas válidas en el reporte')
    if path.exists():raise FileExistsError('El resultado ya existe')
    headers=list(rows[0].keys())
    for row in rows[1:]:
        for k in row:
            if k not in headers:headers.append(k)
    wb=Workbook();ws=wb.active;ws.title='Enriquecido';ws.append(headers)
    for row in rows:ws.append([literal(row.get(k)) for k in headers])
    ws.freeze_panes='A2';ws.auto_filter.ref=f'A1:{ws.cell(row=1,column=len(headers)).column_letter}{len(rows)+1}'
    for cell in ws[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='20354D')
    for column in ws.columns:
        col=column[0].column_letter;ws.column_dimensions[col].width=min(48,max(14,len(str(column[0].value))*1.3))
    path.parent.mkdir(parents=True,exist_ok=True);wb.save(path)


def process(master:Path,source:Path,output:Path,*,normalize_dates=False,multi_codes=False):
    reference=load_map(master)
    if not source.is_dir():raise ValueError('Carpeta de reportes inexistente')
    files=sorted(p for p in source.iterdir() if p.is_file() and p.suffix.lower()=='.xlsx' and not p.name.startswith('~$'))
    if not files:raise ValueError('No hay reportes de entrada')
    if source.resolve()==output.resolve() or source.resolve() in output.resolve().parents:
        raise ValueError('No escriba resultados dentro de la carpeta de entrada')
    destinations=[output/(p.stem+'_result.xlsx') for p in files]
    if any(p.exists() for p in destinations):raise FileExistsError('Un reporte ya existe')
    counts={}
    for file,dest in zip(files,destinations):
        result=enrich_rows(read_rows(file),reference,normalize_dates=normalize_dates,multi_codes=multi_codes)
        save_excel(result,dest)
        counts[file.name]={v:sum(r['Estado']==v for r in result) for v in ('ASIGNADO','SIN_MAPEO','AMBIGUO')}
    return counts


def autodetect_master(folder:Path):
    paths=sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower()=='.xlsx' and not p.name.startswith('~$'))
    if len(paths)!=1:raise ValueError('Debe haber un único Excel maestro en esta carpeta')
    return paths[0]
