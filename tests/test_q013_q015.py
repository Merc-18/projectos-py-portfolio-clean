from __future__ import annotations

import importlib.util
import csv
from pathlib import Path
import tempfile

import fitz
import pytest
from docx import Document
from openpyxl import load_workbook
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1] / 'proyectos' / 'Área Q'


def load(name: str, filename: str):
    p = ROOT / name / filename
    spec = importlib.util.spec_from_file_location('module_' + name, p)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


word = load('Q-013', 'word_a_excel.py')
pdf = load('Q-015', 'pdf_similarity.py')


def make_word(file: Path, desc: str):
    doc = Document()
    tab = doc.add_table(rows=1, cols=3)
    for cell, val in zip(tab.rows[0].cells, ('Zona', 'Lugar', 'Descripción')):
        cell.text = val
    cells = tab.add_row().cells
    for c, v in zip(cells, ('Zona demo', 'Sitio demo', desc)):
        c.text = v
    doc.save(file)


def make_pdf(file: Path, code: int):
    with fitz.open() as d:
        p = d.new_page(width=360, height=480)
        p.insert_text((25, 50), 'DOCUMENTO FICTICIO / NO REAL')
        p.insert_text((25, 425), f'BLOQUE {code}')
        if code % 2:
            p.draw_rect(fitz.Rect(50, 405, 120, 440), color=(0, 0, 0), fill=(0, 0, 0))
        else:
            p.draw_circle((230, 430), 30, color=(0, 0, 0), fill=(0, 0, 0))
        d.save(file)


def test_q013_dates_both_formats():
    assert word.stamps('01/02/2026 12:13:14; 13:30:00 del 01/02/2026') == [
        '01/02/2026 12:13:14', '01/02/2026 13:30:00'
    ]


def test_q013_no_records():
    assert word.parse_events('Texto sin eventos') == []


def test_q013_multiple_cases():
    s = ('CASO 1: 01/02/2026 12:00:00 y 01/02/2026 13:00:00\n'
         'OBSERVACIONES: Prueba A\nACCIONES: Revisado\nRESULTADO: Correcto\n'
         'CASO 2: 03/02/2026 10:00:00\nOBSERVACIONES: Prueba B\n')
    rows = word.parse_events(s, 'Zona X', 'Lugar Y')
    assert len(rows) == 2
    assert rows[0]['Inicio'] == '01/02/2026 12:00:00'
    assert rows[0]['Fin'] == '01/02/2026 13:00:00'
    assert rows[0]['Observaciones'] == 'Prueba A'
    assert rows[0]['Acciones'] == 'Revisado'
    assert rows[1]['Inicio'] == '03/02/2026 10:00:00'
    assert rows[1]['Fin'] == ''


def test_q013_formula_escape():
    assert word.safe_cell(' =2+2').startswith("'")
    assert word.safe_cell('@SUM') == "'@SUM"
    assert word.safe_cell('texto') == 'texto'


def test_q013_full_docx_to_xlsx(tmp_path):
    i, o = tmp_path/'input.docx', tmp_path/'out.xlsx'
    make_word(i, 'CASO 1: 15/02/2026 10:00:00\nOBSERVACIONES: =1+2\nACCIONES: Verificar')
    assert word.process(i, o) == 1
    wb = load_workbook(o)
    assert wb.active['C2'].value == '1'
    assert wb.active['F2'].value == "'=1+2"
    assert wb.active['F2'].data_type == 's'
    assert wb.active.freeze_panes == 'A2'
    with pytest.raises(FileExistsError):
        word.process(i, o)
    wb.close()


def test_q013_reject_invalid_input(tmp_path):
    with pytest.raises(ValueError):
        word.process(tmp_path/'absent.docx', tmp_path/'out.xlsx')


def test_q013_document_without_table(tmp_path):
    inp=tmp_path/'without.docx';Document().save(inp)
    with pytest.raises(ValueError):
        word.process(inp,tmp_path/'out.xlsx')


def test_q015_hash_identical(tmp_path):
    a,b=tmp_path/'original.pdf', tmp_path/'copy.pdf'
    make_pdf(a, 1)
    b.write_bytes(a.read_bytes())
    assert pdf.hash_distance(pdf.perceptual_hash(a),pdf.perceptual_hash(b))==0


def test_q015_hash_changes(tmp_path):
    a,b=tmp_path/'a.pdf',tmp_path/'b.pdf'
    make_pdf(a,1); make_pdf(b,2)
    assert pdf.hash_distance(pdf.perceptual_hash(a),pdf.perceptual_hash(b)) > 0


def test_q015_pairs_and_ambiguous(tmp_path):
    for name in ('document_abc_01.pdf','document_abc_02.pdf','other_001_1.pdf'):
        (tmp_path/name).write_bytes(b'placeholder')
    pairs,unused=pdf.find_pairs(tmp_path)
    assert len(pairs)==1 and len(unused)==1
    (tmp_path/'document_abc_03.pdf').write_bytes(b'placeholder')
    pairs,unused=pdf.find_pairs(tmp_path)
    assert len(pairs)==0 and len(unused)==4


def test_q015_report_and_no_overwrite(tmp_path):
    dst=tmp_path/'report'
    result=pdf.report([{'Archivo_A':'first.pdf','Archivo_B':'second.pdf','Distancia_pHash':0},
                       {'Archivo_A':'another.pdf','Archivo_B':'other.pdf','Distancia_pHash':20}],dst)
    assert result['p95']>=19
    assert result['chart'].is_file() and result['csv'].is_file()
    with (dst/'distancias.csv').open(encoding='utf-8-sig') as f:
        assert len(list(csv.DictReader(f)))==2
    with pytest.raises(FileExistsError):
        pdf.report([{'Archivo_A':'x','Archivo_B':'y','Distancia_pHash':2}],dst)


def test_q015_formula_csv(tmp_path):
    result=pdf.report([{'Archivo_A':'=SUM(1).pdf','Archivo_B':'-2.pdf','Distancia_pHash':8}],tmp_path)
    with result['csv'].open(encoding='utf-8-sig') as f:
        r=list(csv.DictReader(f))[0]
    assert r['Archivo_A'].startswith("'") and r['Archivo_B'].startswith("'")


def test_q015_prefix_validation(tmp_path):
    with pytest.raises(ValueError):
        pdf.find_pairs(tmp_path,minimum_prefix=0)


def test_q015_real_pdf_end_to_end(tmp_path):
    source=tmp_path/'in';source.mkdir()
    for name,code in [('document_demo_001.pdf',1),('document_demo_002.pdf',2)]:
        make_pdf(source/name,code)
    pairs,unused=pdf.find_pairs(source,minimum_prefix=12)
    assert len(pairs)==1 and not unused
    rows=pdf.compare_pairs(pairs)
    assert len(rows)==1 and rows[0]['Distancia_pHash'] > 0
    result=pdf.report(rows,tmp_path/'out')
    assert result['csv'].exists()
