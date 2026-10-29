"""Offline and synthetic-data oriented demonstrations for a portfolio.

No network clients, no credentials, no deletion operations. Output paths are
explicit and never overwrite existing files. Not a replica of private systems.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime
from difflib import SequenceMatcher
import email
from email import policy
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import sys
import unicodedata


def clean_key(value):
    text = unicodedata.normalize('NFKD', str(value or '').casefold())
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return '_'.join(re.findall(r'[a-z0-9]+', text))


def safe_value(value):
    value = '' if value is None else str(value)
    return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) else value


def check_output(source, destination):
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination or source in destination.parents:
        raise ValueError('Output must be separate from input; no in-place changes.')
    if destination.exists():
        raise FileExistsError(f'Output already exists: {destination}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination


def load_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, headers=None):
    rows = list(rows)
    columns = list(headers or dict.fromkeys(k for row in rows for k in row))
    with Path(path).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({c: safe_value(row.get(c, '')) for c in columns})
    return len(rows)


def value_as_float(value):
    try:
        return float(str(value).replace(',', '.'))
    except (ValueError, TypeError):
        return None


def resolve_column(headers, wanted, fallback=0):
    if not headers:
        raise ValueError('Input has no columns')
    normalized = {clean_key(k): k for k in headers}
    if wanted and clean_key(wanted) in normalized:
        return normalized[clean_key(wanted)]
    if wanted:
        raise ValueError(f'Missing column: {wanted}')
    return list(headers)[min(fallback, len(headers)-1)]


def normalize_csv(source, target, args):
    data = load_csv(source)
    if not data:
        write_csv(target, [], headers=['item'])
        return 0
    mapped = {key: clean_key(key) for key in data[0]}
    columns = list(mapped.values())
    if len(set(columns)) != len(columns):
        raise ValueError('Normalized column names are not unique')
    rows = [{mapped[k]: value for k, value in row.items()} for row in data]
    return write_csv(target, rows, columns)


def join_csv(source, target, args):
    files = sorted(Path(source).glob('*.csv'))
    if len(files) != 2:
        raise ValueError('Input folder must contain exactly two CSV files')
    a, b = map(load_csv, files)
    if not a or not b:
        raise ValueError('Both CSV files need rows')
    key_a = resolve_column(a[0], args.key, 0)
    key_b = resolve_column(b[0], args.key, 0)
    index = defaultdict(list)
    for r in b:
        index[str(r[key_b]).strip()].append(r)
    result = []
    for row in a:
        matches = index.get(str(row[key_a]).strip()) or [None]
        for match in matches:
            item = {'key': row[key_a]}
            item.update({f'a_{k}': v for k, v in row.items()})
            if match:
                item.update({f'b_{k}': v for k, v in match.items() if k != key_b})
            result.append(item)
    return write_csv(target, result)


def fuzzy_csv(source, target, args):
    rows = load_csv(source)
    if not rows:
        return write_csv(target, [], ['query', 'closest', 'score'])
    first = resolve_column(rows[0], args.key, 0)
    second = resolve_column(rows[0], args.value, 1)
    sources = [(str(row[first]), clean_key(row[first])) for row in rows if row[first]]
    out = []
    for row in rows:
        value = str(row[second] or '')
        query = clean_key(value)
        comparisons = [(SequenceMatcher(None, query, k).ratio(), v) for v, k in sources] if query else []
        score, matched = max(comparisons, default=(0.0, ''), key=lambda t: t[0])
        out.append({'query': value, 'closest': matched if score >= args.threshold else '', 'score': round(score, 4)})
    return write_csv(target, out, ['query', 'closest', 'score'])


def numeric_summary(source, target, args):
    rows = load_csv(source)
    if not rows:
        return write_csv(target, [], ['group', 'count', 'sum', 'mean', 'min', 'max'])
    key = resolve_column(rows[0], args.key, 0)
    metric = resolve_column(rows[0], args.value, 1)
    grouped = defaultdict(list)
    for row in rows:
        value = value_as_float(row.get(metric))
        if value is not None:
            grouped[str(row.get(key, '')).strip()].append(value)
    out = [{'group': k, 'count': len(v), 'sum': round(sum(v), 4),
            'mean': round(sum(v)/len(v), 4), 'min': min(v), 'max': max(v)}
           for k, v in sorted(grouped.items())]
    return write_csv(target, out)


def period_window(source, target, args):
    rows = load_csv(source)
    if not rows:
        return write_csv(target, [], ['date', 'month', 'year'])
    key = resolve_column(rows[0], args.key, 0)
    out = []
    for row in rows:
        date = str(row.get(key, '')).strip()
        parsed = None
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y'):
            try:
                parsed = datetime.strptime(date, fmt)
                break
            except ValueError:
                pass
        out.append({'date': parsed.strftime('%Y-%m-%d') if parsed else '',
                    'month': parsed.month if parsed else '',
                    'year': parsed.year if parsed else ''})
    return write_csv(target, out)


def count_urls(source, target, args):
    rows = load_csv(source)
    if not rows:
        return write_csv(target, [], ['value', 'count'])
    key = resolve_column(rows[0], args.key, 0)
    counts = Counter(str(r.get(key) or '').strip() for r in rows)
    return write_csv(target, [{'value': k, 'count': v} for k, v in counts.most_common() if k])


def read_xlsx(path):
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True, read_only=True)
    try:
        ws = wb.active
        ws.reset_dimensions()
        values = ws.iter_rows(values_only=True)
        header = next(values, None)
        if not header:
            return []
        keys = [str(x) if x is not None else f'col_{i}' for i, x in enumerate(header)]
        return [dict(zip(keys, row)) for row in values if any(v is not None for v in row)]
    finally:
        wb.close()


def write_xlsx(path, rows):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font
    rows = list(rows)
    fields = list(dict.fromkeys(k for row in rows for k in row)) or ['item']
    wb = Workbook(); ws = wb.active; ws.title = 'Demo'
    ws.append(fields)
    for row in rows:
        ws.append([safe_value(row.get(k, '')) for k in fields])
    for cell in ws[1]:
        cell.font = Font(color='FFFFFF', bold=True)
        cell.fill = PatternFill('solid', fgColor='20334B')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = f'A1:{ws.cell(1,len(fields)).column_letter}{max(2,ws.max_row)}'
    for idx in range(1, len(fields)+1):
        ws.column_dimensions[ws.cell(1, idx).column_letter].width = 25
    wb.save(path)
    return len(rows)


def sort_xlsx(source, target, args):
    rows = read_xlsx(source)
    if not rows:
        return write_xlsx(target, [])
    key = resolve_column(rows[0], args.key, 0)
    rows.sort(key=lambda r: clean_key(r.get(key)))
    return write_xlsx(target, rows)


def concat_xlsx(source, target, args):
    folder = Path(source)
    files = sorted(p for p in folder.glob('*.xlsx') if p.is_file() and not p.is_symlink())
    if not files:
        raise ValueError('No XLSX files found')
    rows = []
    for file in files:
        rows.extend([{'file': file.name, **r} for r in read_xlsx(file)])
    return write_xlsx(target, rows)


def unpivot_xlsx(source, target, args):
    rows = read_xlsx(source)
    if not rows:
        return write_xlsx(target, [])
    key = resolve_column(rows[0], args.key, 0)
    out = [{'record': row.get(key), 'metric': name, 'value': value}
           for row in rows for name, value in row.items() if name != key and value is not None]
    return write_xlsx(target, out)


def compare_headers(source, target, args):
    paths = sorted(Path(source).glob('*.xlsx'))
    if len(paths) < 2:
        raise ValueError('Supply at least two XLSX files')
    from openpyxl import load_workbook
    rows = []
    for path in paths:
        wb = load_workbook(path, read_only=True, data_only=True)
        try:
            ws = wb.active; ws.reset_dimensions()
            keys = next(ws.iter_rows(min_row=1, max_row=1, values_only=True), ())
            rows.extend({'file': path.name, 'position': i, 'header': str(value)}
                        for i, value in enumerate(keys, start=1))
        finally:
            wb.close()
    return write_xlsx(target, rows)


def excel_template(source, target, args):
    rows = load_csv(source)
    return write_xlsx(target, rows or [{'task': 'Example task', 'state': 'Open'}])


def daily_csv(source, target, args):
    rows = load_csv(source)
    if not rows:
        return write_csv(target, [], ['date', 'count'])
    key = resolve_column(rows[0], args.key, 0)
    counts = Counter(str(r[key])[:10] for r in rows)
    return write_csv(target, [{'date': k, 'count': v} for k, v in sorted(counts.items())])


def scan_files(source, target, args):
    root = Path(source).resolve()
    if not root.is_dir():
        raise ValueError('Input must be a folder')
    out = []
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if not (Path(base)/d).is_symlink())
        for name in sorted(files):
            path = Path(base)/name
            if path.is_symlink():
                continue
            out.append({'relative': str(path.relative_to(root)), 'suffix': path.suffix.lower(), 'size': path.stat().st_size})
    return write_csv(target, out, ['relative', 'suffix', 'size'])


def rename_preview(source, target, args):
    root = Path(source)
    rows = [{'original': p.name, 'proposal': f'{i:03d}{p.suffix.lower()}'}
            for i,p in enumerate(sorted(root.glob('*.pdf')), start=1) if p.is_file() and not p.is_symlink()]
    return write_csv(target, rows)


def copy_pdfs(source, target, args):
    root=Path(source).resolve(); dest=Path(target).resolve()
    if not root.is_dir() or root==dest or root in dest.parents:
        raise ValueError('Input folder must be separate from output')
    files = [p for p in sorted(root.rglob('*')) if p.is_file() and not p.is_symlink() and p.suffix.lower()=='.pdf']
    plan = []
    for idx,p in enumerate(files, 1):
        name=f'{idx:04d}_{re.sub(r"[^a-zA-Z0-9_.-]", "_", p.name)}'
        plan.append({'source': str(p.relative_to(root)), 'destination': name})
    if args.execute:
        if dest.exists():
            raise FileExistsError('Output directory must not exist for --execute')
        dest.mkdir(parents=True)
        for p, item in zip(files, plan):
            shutil.copyfile(p, dest/item['destination'])
    else:
        print(json.dumps({'dry_run': True, 'files': plan}, ensure_ascii=True, indent=2))
    return len(files)


def pdf_pages(source, target, args):
    import fitz
    pdfs = [Path(source)] if Path(source).is_file() else sorted(Path(source).glob('*.pdf'))
    rows = []
    for p in pdfs:
        with fitz.open(p) as doc:
            for i, page in enumerate(doc):
                w, h = page.rect.width, page.rect.height
                label='A4' if abs(w-595)<14 and abs(h-842)<14 else 'A3' if abs(w-842)<20 and abs(h-1191)<20 else 'Other'
                rows.append({'file': p.name, 'page': i+1, 'width_pt': round(w,1), 'height_pt': round(h,1), 'format': label})
    return write_csv(target, rows)


def pdf_text(source, target, args):
    import fitz
    pdfs=[Path(source)] if Path(source).is_file() else sorted(Path(source).glob('*.pdf'))
    out=[]
    for file in pdfs:
        with fitz.open(file) as doc:
            text='\n'.join(p.get_text() for p in doc)
            out.append({'file': file.name, 'pages': len(doc), 'status': 'HAS_TEXT' if text.strip() else 'NO_TEXT', 'preview': text[:1500]})
    return write_csv(target, out)


def number_pdf(source, target, args):
    import fitz
    with fitz.open(source) as doc:
        for i, page in enumerate(doc,1):
            page.insert_text((32,page.rect.height-24), f'EXAMPLE - {i} / {len(doc)}', fontsize=8)
        doc.save(str(target))
    return 1


def ocr_pdf(source, target, args):
    import fitz
    import pytesseract
    from PIL import Image
    texts=[]
    with fitz.open(source) as doc:
        for page in doc:
            pix=page.get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False)
            img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            texts.append(pytesseract.image_to_string(img,lang='eng'))
    Path(target).write_text('\n\n'.join(texts),encoding='utf-8')
    return len(texts)


def ocr_image(source, target, args):
    import pytesseract
    from PIL import Image, ImageOps
    image = ImageOps.grayscale(Image.open(source))
    text = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
    Path(target).write_text(text, encoding='utf-8')
    return 1


def image_hash(source, target, args):
    from PIL import Image, ImageOps
    paths=[Path(source)] if Path(source).is_file() else sorted(Path(source).glob('*.png'))
    out=[]
    for p in paths:
        img=ImageOps.grayscale(Image.open(p)).resize((8,8))
        values=list(img.getdata()); avg=sum(values)/len(values)
        bits=''.join('1' if p>=avg else '0' for p in values)
        out.append({'file': p.name, 'ahash': hex(int(bits,2))[2:].zfill(16)})
    return write_csv(target,out)


def word_tables(source,target,args):
    from docx import Document
    doc=Document(source)
    rows=[]
    for idx,table in enumerate(doc.tables,1):
        for rno,row in enumerate(table.rows,1):
            rows.append({'table':idx,'row':rno,'text':' | '.join(c.text for c in row.cells)})
    return write_csv(target,rows)


def docx_paths(source,target,args):
    from docx import Document
    doc=Document(source)
    text='\n'.join(p.text for p in doc.paragraphs)
    matches=re.findall(r'[^\s<>"\']+\.pdf\b',text,re.IGNORECASE)
    return write_csv(target,[{'index':i,'document':Path(v).name} for i,v in enumerate(matches,1)])


def eml_summary(source,target,args):
    paths=[Path(source)] if Path(source).is_file() else sorted(Path(source).glob('*.eml'))
    out=[]
    for p in paths:
        msg=email.message_from_bytes(p.read_bytes(),policy=policy.default)
        subject=str(msg.get('subject',''))
        body=msg.get_body(preferencelist=('plain',))
        snippet=body.get_content()[:1000] if body else ''
        out.append({'file':p.name,'subject':subject,'body_preview':snippet,'attachments':sum(part.get_content_disposition()=='attachment' for part in msg.walk())})
    return write_csv(target,out)


def eml_to_docx(source,target,args):
    from docx import Document
    msg=email.message_from_bytes(Path(source).read_bytes(),policy=policy.default)
    doc=Document();doc.add_heading('Synthetic email example',0)
    doc.add_paragraph(str(msg.get('subject','')))
    body=msg.get_body(preferencelist=('plain',))
    if body:doc.add_paragraph(body.get_content()[:20000])
    doc.save(target)
    return 1


class LocalHTML(HTMLParser):
    def __init__(self):
        super().__init__();self._in_title=False;self.title='';self.links=[];self._in_a=False;self.href=''
    def handle_starttag(self,tag,attrs):
        if tag=='title':self._in_title=True
        if tag=='a':self._in_a=True;self.href=dict(attrs).get('href','')
    def handle_endtag(self,tag):
        if tag=='title':self._in_title=False
        if tag=='a':self._in_a=False
    def handle_data(self,data):
        if self._in_title:self.title+=data
        if self._in_a:self.links.append((self.href,data.strip()))


def html_extract(source,target,args):
    parser=LocalHTML();parser.feed(Path(source).read_text(encoding='utf-8'))
    return write_csv(target,[{'title':parser.title,'href':href,'label':label} for href,label in parser.links])


def mock_api(source,target,args):
    obj=json.loads(Path(source).read_text(encoding='utf-8'))
    if not isinstance(obj,dict):raise ValueError('Input must be a JSON object')
    result={'offline':True,'valid':all(k in obj for k in ('id','message')),'fields':sorted(obj)}
    Path(target).write_text(json.dumps(result,indent=2),encoding='utf-8')
    return 1


def dashboard_html(source,target,args):
    rows=load_csv(source)
    head=list(rows[0]) if rows else []
    table=''.join('<tr>'+''.join(f'<td>{escape(str(r.get(k,"")))}</td>' for k in head)+'</tr>' for r in rows)
    output='<!doctype html><meta charset="utf-8"><title>Demo dashboard</title><h1>Local summary</h1><table border="1"><tr>'+''.join(f'<th>{escape(k)}</th>' for k in head)+'</tr>'+table+'</table>'
    Path(target).write_text(output,encoding='utf-8')
    return len(rows)


OPERATIONS={
 'normalize_csv':normalize_csv,'join_csv':join_csv,'fuzzy_csv':fuzzy_csv,
 'numeric_summary':numeric_summary,'period_window':period_window,'count_urls':count_urls,
 'sort_xlsx':sort_xlsx,'concat_xlsx':concat_xlsx,'unpivot_xlsx':unpivot_xlsx,
 'compare_headers':compare_headers,'excel_template':excel_template,'daily_csv':daily_csv,
 'scan_files':scan_files,'rename_preview':rename_preview,'copy_pdfs':copy_pdfs,
 'pdf_pages':pdf_pages,'pdf_text':pdf_text,'number_pdf':number_pdf,
 'ocr_pdf':ocr_pdf,'ocr_image':ocr_image,'image_hash':image_hash,
 'word_tables':word_tables,'docx_paths':docx_paths,'eml_summary':eml_summary,
 'eml_to_docx':eml_to_docx,'html_extract':html_extract,'mock_api':mock_api,
 'dashboard_html':dashboard_html,
}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Offline portfolio demonstration. Use fictional input.')
    parser.add_argument('--mode',required=True,choices=sorted(OPERATIONS))
    parser.add_argument('--input',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--key',default=None)
    parser.add_argument('--value',default=None)
    parser.add_argument('--threshold',type=float,default=.80)
    parser.add_argument('--execute',action='store_true',help='Explicit opt-in for safe PDF copies only')
    args=parser.parse_args(argv)
    inp=Path(args.input).resolve()
    if not inp.exists():parser.error('Input not found')
    if not 0<=args.threshold<=1:parser.error('Threshold must be between 0 and 1')
    if args.mode=='copy_pdfs':
        result=copy_pdfs(inp,Path(args.output),args)
    else:
        out=check_output(inp,args.output)
        result=OPERATIONS[args.mode](inp,out,args)
    print(json.dumps({'mode':args.mode,'items':result,'dry_run':args.mode=='copy_pdfs' and not args.execute},ensure_ascii=True))


if __name__=='__main__':
    main()
