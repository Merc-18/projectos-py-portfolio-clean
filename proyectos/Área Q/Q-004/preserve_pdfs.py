"""Non-destructive PDF selection and flattening, defaulting to dry-run."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def plan(root: Path, target: Path, keyword: str = "APROBADO") -> list[tuple[Path, Path]]:
    root, target = root.resolve(), target.resolve()
    if not root.is_dir():
        raise ValueError("La carpeta de origen no existe")
    if target == root or root in target.parents or target in root.parents:
        raise ValueError("Origen y destino no deben estar anidados ni coincidir")
    if not keyword or len(keyword) > 60:
        raise ValueError("Especifica una palabra clave de 1 a 60 caracteres")
    selected = []
    names = set()
    for p in sorted(root.rglob('*'), key=lambda x: str(x).casefold()):
        if p.is_symlink() or not p.is_file() or p.suffix.lower() != '.pdf':
            continue
        if keyword.casefold() not in p.name.casefold():
            continue
        rel = p.relative_to(root)
        group = rel.parts[0] if len(rel.parts) > 1 else 'general'
        out_dir = target / group
        dst = out_dir / p.name
        counter = 2
        while str(dst).casefold() in names or dst.exists():
            dst = out_dir / f'{p.stem}_{counter}.pdf'
            counter += 1
        names.add(str(dst).casefold())
        selected.append((p, dst))
    return selected


def execute(items: list[tuple[Path, Path]], *, commit: bool = False) -> int:
    if not commit:
        return 0
    copied = 0
    for src, dest in items:
        dest.parent.mkdir(parents=True, exist_ok=True)
        # exclusive create prevents clobber and avoids removing source files
        with src.open('rb') as old, dest.open('xb') as new:
            shutil.copyfileobj(old, new)
        copied += 1
    return copied


def main():
    parser = argparse.ArgumentParser(description='Selección de PDF sin eliminaciones')
    parser.add_argument('input', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--keyword', default='APROBADO')
    parser.add_argument('--execute', action='store_true', help='Copia los archivos; por defecto solo muestra un plan')
    a = parser.parse_args()
    items = plan(a.input, a.output, a.keyword)
    for src, dest in items:
        print(f'{src.name} -> {dest}')
    print(f'Encontrados: {len(items)}; copiados: {execute(items, commit=a.execute)}')


if __name__ == '__main__':
    main()
