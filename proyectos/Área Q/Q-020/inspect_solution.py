"""Inspect generic solution XML without exposing publisher or solution identities."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET

MAX_BYTES=2*1024*1024


def inspect(xml_file:Path):
    if not xml_file.is_file() or xml_file.suffix.lower()!='.xml':raise ValueError('Se necesita .xml')
    raw=xml_file.read_bytes()
    if len(raw)>MAX_BYTES:raise ValueError('XML demasiado grande')
    if b'<!ENTITY' in raw.upper() or b'<!DOCTYPE' in raw.upper():
        raise ValueError('Entidades XML externas o DTD no permitidas')
    root=ET.fromstring(raw)
    type_count={}
    for e in root.iter():
        tag=e.tag.split('}')[-1]
        if tag in ('RootComponent','MissingDependency','Workflow'):
            type_count[tag]=type_count.get(tag,0)+1
    # Intentionally suppress names, IDs, email, publisher, domains and XML contents
    return {'formato':'XML_LOCAL','elementos_relevantes':type_count,
            'total_nodos':sum(1 for _ in root.iter()),'identificadores_exportados':0}


def save_summary(data:dict,out:Path):
    if out.suffix.lower()!='.json':raise ValueError('Salida .json')
    if out.exists():raise FileExistsError('El informe ya existe')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf8')


def main():
    p=argparse.ArgumentParser(description='Resumen anónimo de un XML de solución local')
    p.add_argument('xml_file',type=Path);p.add_argument('output_json',type=Path)
    a=p.parse_args();save_summary(inspect(a.xml_file),a.output_json)
    print('Resumen creado sin nombres ni identificadores')


if __name__=='__main__':main()
