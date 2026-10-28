"""Auditing and safe selection of folders based on synthetic Excel IDs."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill


def codes_from_excel(file:Path, selected_group:str):
    wb=load_workbook(file,read_only=True,data_only=True)
    try:
        ws=wb.active;ws.reset_dimensions();it=ws.iter_rows(values_only=True)
        header=next(it,None)
        if not header:raise ValueError('Planilla vacía')
        cols={str(v).strip().casefold():i for i,v in enumerate(header) if v is not None}
        if any(k not in cols for k in ('grupo','codigo')):raise ValueError('Columnas requeridas: Grupo, Codigo')
        selected=set()
        for row in it:
            group=str(row[cols['grupo']] if len(row)>cols['grupo'] else '').strip()
            code=str(row[cols['codigo']] if len(row)>cols['codigo'] else '').strip()
            if group.casefold()==selected_group.casefold() and code:
                if '/' in code or '\\' in code or code in ('.','..'):raise ValueError('Código de carpeta inválido')
                selected.add(code.casefold())
        return selected
    finally:wb.close()


def plan(source:Path,excel:Path,target:Path,group:str):
    src,dst=source.resolve(),target.resolve()
    if not src.is_dir():raise ValueError('Carpeta de entrada no existe')
    if src==dst or src in dst.parents or dst in src.parents:raise ValueError('Origen y destino deben estar separados')
    if not group.strip():raise ValueError('Grupo vacío')
    accepted=codes_from_excel(excel,group)
    folders=sorted((p for p in src.rglob('*') if p.is_dir() and not p.is_symlink() and p.name.casefold() in accepted),key=str)
    commands=[]
    for folder in folders:
        # Direct folders nested under another selected folder are not selected twice
        if any(other in folder.parents for other in folders if other!=folder):continue
        for file in folder.rglob('*'):
            if file.is_file() and not file.is_symlink():
                dest=dst/file.relative_to(src)
                if dest.exists():raise FileExistsError(f'Ya existe: {dest.name}')
                commands.append((file,dest))
    return commands


def safe_cell(value):
    s=str(value)
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s

def report(plan_items,output:Path,*,overwrite=False):
    if output.suffix.lower()!='.xlsx':raise ValueError('Reporte .xlsx')
    if output.exists() and not overwrite:raise FileExistsError('Reporte existente')
    wb=Workbook();ws=wb.active;ws.title='Inventario';ws.append(('Archivo','Carpeta destino','Estado'))
    for src,dst in plan_items:
        ws.append((safe_cell(src.name), safe_cell(dst.parent.name), 'PLANIFICADO'))
    for cell in ws[1]:cell.font=Font(bold=True,color='FFFFFF');cell.fill=PatternFill('solid',fgColor='20354D')
    ws.column_dimensions['A'].width=40;ws.column_dimensions['B'].width=35;ws.column_dimensions['C'].width=18
    output.parent.mkdir(parents=True,exist_ok=True);wb.save(output)


def copy(plan_items,*,execute=False):
    if not execute:return 0
    for source,target in plan_items:
        target.parent.mkdir(parents=True,exist_ok=True)
        with source.open('rb') as old,target.open('xb') as new:shutil.copyfileobj(old,new)
    return len(plan_items)


def main():
    parser=argparse.ArgumentParser(description='Auditoría no destructiva de carpetas y Excel')
    parser.add_argument('source',type=Path);parser.add_argument('mapping',type=Path)
    parser.add_argument('destination',type=Path);parser.add_argument('report',type=Path)
    parser.add_argument('--group',default='DEMO');parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    cmds=plan(args.source,args.mapping,args.destination,args.group)
    report(cmds,args.report)
    print('Archivos previstos:',len(cmds),'Copiados:',copy(cmds,execute=args.execute))


if __name__=='__main__':main()
