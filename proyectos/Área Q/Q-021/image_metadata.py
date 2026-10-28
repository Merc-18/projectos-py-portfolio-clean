"""Inspect non-sensitive image properties without exporting embedded EXIF data."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from PIL import Image, ExifTags

ORIENTATION_TAG=274
GPS_TAG=34853


def inspect(path:Path):
    with Image.open(path) as image:
        exif=image.getexif()
        return (path.name,image.format or '',image.width,image.height,
                str(exif.get(ORIENTATION_TAG,'')),
                'SI' if GPS_TAG in exif else 'NO',
                len(exif))


def audit(folder:Path,dest:Path):
    if not folder.is_dir():raise ValueError('No existe la carpeta de imágenes')
    if dest.suffix.lower()!='.csv':raise ValueError('Salida CSV requerida')
    if dest.exists():raise FileExistsError('No sobrescribir el reporte')
    files=sorted(p for p in folder.iterdir() if p.is_file() and not p.is_symlink() and p.suffix.lower() in ('.jpg','.jpeg','.png','.webp'))
    if not files:raise ValueError('No hay imágenes de entrada')
    rows=[]
    for p in files:
        try:rows.append(inspect(p))
        except (OSError,ValueError):continue
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(('Archivo','Formato','Ancho','Alto','Orientación','Contiene GPS','Cantidad campos EXIF'))
        for row in rows:
            w.writerow(["'"+str(v) if str(v).lstrip().startswith(('=','+','-','@')) else v for v in row])
    return len(rows)


def main():
    p=argparse.ArgumentParser(description='Metadatos inocuos; no exporta coordenadas ni EXIF sensible')
    p.add_argument('images',type=Path);p.add_argument('output_csv',type=Path)
    a=p.parse_args();print('Imágenes:',audit(a.images,a.output_csv))


if __name__=='__main__':main()
