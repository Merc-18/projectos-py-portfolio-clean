"""Extract resource metadata from local HTML fixtures, no external requests."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from bs4 import BeautifulSoup


def scan_html(source:Path):
    soup=BeautifulSoup(source.read_text(encoding='utf8'),'html.parser')
    found=[]
    for card in soup.select('article[data-demo-id]'):
        id=card.get('data-demo-id','').strip()
        title=card.select_one('h2, h3, [data-title]')
        desc=card.select_one('p, [data-description]')
        link=card.select_one('a[href]')
        if id and title:
            href=link.get('href','') if link else ''
            # Strip any links that are not HTTPS or relative example paths
            if not href.startswith('https://example.org/') and not href.startswith('/'):
                href=''
            found.append((source.name,id,title.get_text(' ',strip=True),desc.get_text(' ',strip=True) if desc else '',href))
    return found


def csv_text(text):
    s=str(text)
    return "'"+s if s.lstrip().startswith(('=','+','-','@')) else s


def extract(folder:Path,out:Path):
    if not folder.is_dir():raise ValueError('No existe la carpeta HTML')
    if out.suffix.lower()!='.csv':raise ValueError('Salida CSV requerida')
    if out.exists():raise FileExistsError('El CSV ya existe')
    if folder.resolve()==out.parent.resolve():raise ValueError('Mantenga la salida fuera de la carpeta fuente')
    paths=sorted(p for p in folder.glob('*.html') if p.is_file() and not p.is_symlink())
    if not paths:raise ValueError('No hay HTML de prueba')
    values=[]
    for p in paths:values.extend(scan_html(p))
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f);writer.writerow(('Archivo','ID','Título','Descripción','Enlace'))
        for row in values:writer.writerow(tuple(csv_text(x) for x in row))
    return len(values)


def main():
    parser=argparse.ArgumentParser(description='Extracción de recursos desde HTML local')
    parser.add_argument('html_folder',type=Path);parser.add_argument('output_csv',type=Path)
    a=parser.parse_args();print('Recursos:',extract(a.html_folder,a.output_csv))


if __name__=='__main__':main()
