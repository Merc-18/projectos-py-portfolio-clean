"""Classify exact PDF duplicates and visual-review candidates; read-only."""
from __future__ import annotations

import argparse
import csv
import hashlib
from itertools import combinations
from pathlib import Path

import fitz
import numpy as np
from PIL import Image


def sha256_file(path:Path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(128*1024),b''):
            h.update(chunk)
    return h.hexdigest()


def image_hash(pdf:Path,*,first=True):
    with fitz.open(pdf) as doc:
        if doc.page_count<1:raise ValueError('PDF sin páginas')
        page=doc[0 if first else -1]
        pix=page.get_pixmap(dpi=64,colorspace=fitz.csRGB,alpha=False)
        img=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L')
        a=np.asarray(img.resize((9,8),Image.Resampling.LANCZOS))
        return sum(int(b)<<i for i,b in enumerate((a[:,1:]>a[:,:-1]).reshape(-1)))


def compare(root:Path,*,threshold:int=6,max_files:int=200):
    if not root.is_dir():raise ValueError('Origen no existe')
    if threshold<0 or threshold>64:raise ValueError('Umbral fuera de 0..64')
    if max_files<1:raise ValueError('max_files debe ser positivo')
    paths=sorted(p for p in root.rglob('*') if p.is_file() and not p.is_symlink() and p.suffix.lower()=='.pdf')
    if len(paths)>max_files:raise ValueError('Demasiados PDFs; dividir en lotes')
    exact={};visual={};invalid=[]
    for f in paths:
        try:exact[f]=sha256_file(f);visual[f]=(image_hash(f,first=True),image_hash(f,first=False))
        except (ValueError,RuntimeError):invalid.append(f.name)
    pairs=[]
    for a,b in combinations(visual,2):
        d1=(visual[a][0]^visual[b][0]).bit_count()
        d2=(visual[a][1]^visual[b][1]).bit_count()
        if exact[a]==exact[b]:label='IDENTICO'
        elif max(d1,d2)<=threshold:label='REVISAR_SIMILITUD'
        else:continue
        pairs.append((a.name,b.name,label,d1,d2))
    return pairs,invalid,len(paths)


def safe_csv(v):
    text=str(v)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) else text


def write_report(pairs,invalid,count,output:Path):
    if output.suffix.lower()!='.csv':raise ValueError('La salida debe ser .csv')
    if output.exists():raise FileExistsError('Reporte ya existe')
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(('Archivo A','Archivo B','Estado','Distancia primera','Distancia última'))
        for row in pairs:writer.writerow([safe_csv(x) for x in row])
    return {'pares':len(pairs),'pdfs':count,'invalidos':invalid}


def main():
    p=argparse.ArgumentParser(description='Duplicados exactos y similitud de PDF; no autentica firmas')
    p.add_argument('folder',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--threshold',type=int,default=6)
    a=p.parse_args();print(write_report(*compare(a.folder,threshold=a.threshold),a.output))


if __name__=='__main__':main()
