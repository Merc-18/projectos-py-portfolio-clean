"""Generic secure HTTPS batch downloader with explicit domain and dry-run default."""
from __future__ import annotations

import argparse
import csv
import os
from pathlib import Path
from urllib.parse import urlsplit

import requests

MAX_BYTES=20*1024*1024


def safe_filename(filename:str)->str:
    if not filename or filename.strip()!=filename or len(filename)>120:
        raise ValueError('Nombre inválido')
    if filename in ('.','..') or any(c in filename for c in ('/','\\',':','\0')):
        raise ValueError('El nombre intenta salir del directorio')
    return filename


def authorized_url(uri:str,allow_domain:str)->str:
    parsed=urlsplit(uri)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Solo se admite HTTPS sin credenciales en la URL')
    if parsed.hostname.casefold()!=allow_domain.casefold():
        raise ValueError('Dominio no autorizado')
    if not allow_domain or '.' not in allow_domain or allow_domain.startswith('127.'):
        raise ValueError('Dominio de destino inválido')
    if parsed.port not in (None,443):raise ValueError('Puerto no autorizado')
    return uri


def read_manifest(csv_path:Path,host:str):
    with csv_path.open(newline='',encoding='utf-8-sig') as file:
        rows=csv.DictReader(file)
        if not rows.fieldnames or not {'Filename','URL'}.issubset(set(rows.fieldnames)):
            raise ValueError('CSV requiere Filename,URL')
        items=[];names=set()
        for row in rows:
            name=safe_filename((row['Filename'] or '').strip())
            url=authorized_url((row['URL'] or '').strip(),host)
            if name.casefold() in names:raise ValueError('Nombre de salida repetido')
            names.add(name.casefold());items.append((url,name))
    return items


def download(items,output:Path,*,execute=False,session=None,token=None):
    if not execute:return 0
    if not items:return 0
    if not token:raise ValueError('Token faltante; use la variable de entorno PORTFOLIO_TOKEN')
    if any((output/name).exists() for _,name in items):raise FileExistsError('Salida ya existe')
    output.mkdir(parents=True,exist_ok=True)
    client=session or requests.Session()
    count=0
    for url,name in items:
        response=client.get(url,headers={'Authorization':f'Bearer {token}'},timeout=20,stream=True,allow_redirects=False)
        response.raise_for_status()
        if response.status_code!=200:raise ValueError('Respuesta no autorizada o redirección')
        if int(response.headers.get('Content-Length','0') or 0)>MAX_BYTES:raise ValueError('Archivo demasiado grande')
        size=0
        dest=output/name
        try:
            with dest.open('xb') as out:
                for chunk in response.iter_content(chunk_size=65536):
                    if not chunk:continue
                    size+=len(chunk)
                    if size>MAX_BYTES:raise ValueError('Límite de 20 MiB superado')
                    out.write(chunk)
            count+=1
        except BaseException:
            dest.unlink(missing_ok=True)
            raise
        finally:response.close()
    return count


def main():
    p=argparse.ArgumentParser(description='Descarga HTTPS genérica con lista blanca y simulación')
    p.add_argument('manifest',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--domain',required=True);p.add_argument('--execute',action='store_true')
    a=p.parse_args();items=read_manifest(a.manifest,a.domain)
    print('Planificación de archivos:',len(items))
    print('Descargados:',download(items,a.output,execute=a.execute,token=os.environ.get('PORTFOLIO_TOKEN')))


if __name__=='__main__':main()
