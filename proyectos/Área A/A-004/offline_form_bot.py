"""Automatiza únicamente un formulario local y sintético; no conecta a portales."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

# The HTML is generated locally and never loaded from an external website.
FORM_HTML = """<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>
<title>Formulario ficticio</title><style>body{font-family:Arial;margin:60px auto;max-width:540px;
background:#f5f7fa;color:#142638}label{display:block;margin:24px 0 12px}
input{width:100%;padding:12px;border:1px solid #aaa;border-radius:6px}</style></head><body>
<h1>Formulario de prueba local</h1><p>DEMO / SIN CONEXION EXTERNA</p>
<form><label>Código<input name='codigo' autocomplete='off'></label>
<label>Fecha<input name='fecha' autocomplete='off'></label>
<label>Asunto<input name='asunto' autocomplete='off'></label></form></body></html>"""

ALLOWED = {'codigo', 'fecha', 'asunto'}


def validate(values: dict) -> dict:
    if not isinstance(values, dict) or set(values) != ALLOWED:
        raise ValueError('Proporcione exactamente los campos codigo, fecha y asunto')
    clean = {}
    for key, value in values.items():
        if not isinstance(value, str) or not 1 <= len(value) <= 120:
            raise ValueError(f'Campo no válido: {key}')
        clean[key] = value
    if not re.fullmatch(r'[A-Za-z0-9_-]{3,25}', clean['codigo']):
        raise ValueError('Código ficticio inválido')
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', clean['fecha']):
        raise ValueError('Formato fecha esperado AAAA-MM-DD')
    return clean


def fill_demo(values: dict, screenshot: Path, *, chromium_path: str | None = None) -> dict:
    """Rellena una página generada por el programa; no envía formulario alguno."""
    values = validate(values)
    if screenshot.suffix.lower() != '.png':
        raise ValueError('Salida .png requerida')
    if screenshot.exists():
        raise FileExistsError('No se sobreescribe la captura')
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        options = {'headless': True}
        if chromium_path:
            options['executable_path'] = chromium_path
        browser = pw.chromium.launch(**options)
        try:
            context = browser.new_context(viewport={'width': 950, 'height': 760})
            # Block all HTTP(S), file, data and other network requests from the page.
            context.route('**/*', lambda route: route.abort())
            page = context.new_page()
            page.set_content(FORM_HTML)
            for key, val in values.items():
                page.locator(f'input[name="{key}"]').fill(val)
            verified = {key: page.locator(f'input[name="{key}"]').input_value() for key in ALLOWED}
            if verified != values:
                raise RuntimeError('Los valores del formulario no coinciden')
            screenshot.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshot), full_page=True)
        finally:
            browser.close()
    return {'campos_verificados': len(verified), 'captura': str(screenshot), 'servidores_consultados': 0}


def main(argv=None):
    p = argparse.ArgumentParser(description='Bot local de formulario ficticio, sin red')
    p.add_argument('json_ficticio', type=Path)
    p.add_argument('captura_png', type=Path)
    p.add_argument('--chromium', help='Ruta opcional al ejecutable del navegador')
    args = p.parse_args(argv)
    data = json.loads(args.json_ficticio.read_text(encoding='utf8'))
    print(json.dumps(fill_demo(data, args.captura_png, chromium_path=args.chromium), ensure_ascii=False))


if __name__ == '__main__':
    main()
