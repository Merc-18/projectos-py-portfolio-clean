"""Plan and safely organize generic document files from an Excel mapping."""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
from openpyxl import load_workbook

VALID_SEGMENT = re.compile(r'^[\w -]{1,55}$', re.UNICODE)
ALLOWED_EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg'}


def safe_segment(value) -> str:
    text = str(value or '').strip()
    if not text or text in ('.', '..') or not VALID_SEGMENT.fullmatch(text):
        raise ValueError('Segmento inválido en el Excel; se bloquea navegación relativa')
    return text


def read_mapping(xlsx: Path):
    wb = load_workbook(xlsx, read_only=True, data_only=True)
    try:
        sheet = wb.active
        sheet.reset_dimensions()
        it = sheet.iter_rows(values_only=True)
        columns = next(it, None)
        if not columns:
            raise ValueError('La planilla está vacía')
        index = {str(value).strip().casefold(): i for i, value in enumerate(columns) if value is not None}
        required = ('tipo', 'zona', 'codigo')
        if any(key not in index for key in required):
            raise ValueError('Requiere columnas Tipo, Zona y Codigo')
        for row in it:
            if not row or all(v is None for v in row):
                continue
            yield tuple(safe_segment(row[index[key]] if len(row) > index[key] else None) for key in required)
    finally:
        wb.close()


def plan(mapping: Path, documents: Path, output: Path):
    root, dest = documents.resolve(), output.resolve()
    if not root.is_dir():
        raise ValueError('Falta la carpeta de documentos')
    if root == dest or root in dest.parents or dest in root.parents:
        raise ValueError('El destino no debe estar anidado en el origen')
    if not mapping.is_file() or mapping.suffix.lower() != '.xlsx':
        raise ValueError('Es necesario un Excel existente')
    index = {}
    for doc in sorted(root.rglob('*')):
        if doc.is_symlink() or not doc.is_file() or doc.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        index.setdefault(doc.stem.casefold(), doc)
    commands, missing, output_seen = [], [], set()
    for kind, zone, code in read_mapping(mapping):
        source = index.get(code.casefold()) or index.get(code.zfill(8).casefold())
        if not source:
            missing.append(code)
            continue
        dest_file = dest / kind / zone / code / source.name
        if dest_file.exists() or dest_file in output_seen:
            raise FileExistsError(f'Destino duplicado: {dest_file.name}')
        output_seen.add(dest_file)
        commands.append((source, dest_file))
    return commands, missing


def copy_documents(commands, *, execute=False):
    if not execute:
        return 0
    for src, dst in commands:
        dst.parent.mkdir(parents=True, exist_ok=True)
        with src.open('rb') as inp, dst.open('xb') as out:
            shutil.copyfileobj(inp, out)
    return len(commands)


def main():
    parser = argparse.ArgumentParser(description='Organiza documentos mediante Excel ficticio')
    parser.add_argument('mapping', type=Path)
    parser.add_argument('documents', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    steps, missing = plan(args.mapping, args.documents, args.output)
    print('Coincidencias:', len(steps), 'No encontrados:', len(missing))
    for src, dst in steps:
        print(f'{src.name} -> {dst}')
    print('Copiados:', copy_documents(steps, execute=args.execute))


if __name__ == '__main__':
    main()
