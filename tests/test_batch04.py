from __future__ import annotations

import importlib.util
from pathlib import Path
import fitz
from openpyxl import Workbook,load_workbook
import pytest

ROOT=Path(__file__).resolve().parents[1]/'proyectos'


def load(area,name,script):
    p=ROOT/area/name/script
    spec=importlib.util.spec_from_file_location(name,p)
    mod=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

q004=load('Área Q','Q-004','preserve_pdfs.py')
q012=load('Área Q','Q-012','organize_from_excel.py')
d002=load('Área D','D-002','review_resources.py')
d003=load('Área D','D-003','make_demo_documents.py')
a005=load('Área A','A-005','folder_audit.py')


def excel(path,headers,rows):
    wb=Workbook();ws=wb.active;ws.append(headers)
    for row in rows:ws.append(row)
    wb.save(path)


def test_q004_safe_dry_run(tmp_path):
    root,dst=tmp_path/'root',tmp_path/'dest'
    (root/'one'/'deep').mkdir(parents=True)
    f=root/'one'/'deep'/'DEMO_APROBADO.pdf';f.write_bytes(b'pdf-data')
    (root/'one'/'deep'/'other.txt').write_text('keep')
    steps=q004.plan(root,dst,'APROBADO')
    assert len(steps)==1 and q004.execute(steps)==0
    assert f.read_bytes()==b'pdf-data' and not dst.exists()
    assert q004.execute(steps,commit=True)==1
    assert (dst/'one'/'DEMO_APROBADO.pdf').read_bytes()==b'pdf-data'
    assert (root/'one'/'deep'/'other.txt').exists()


def test_q004_collsions(tmp_path):
    root,dst=tmp_path/'root',tmp_path/'dest'
    for name in ['one','one_bis']:
        folder=root/name/'deep';folder.mkdir(parents=True)
        (folder/'APROBADO.pdf').write_bytes(name.encode())
    # both different groups, same name is safe; add duplicate within one group
    other=root/'one'/'sub2';other.mkdir()
    (other/'APROBADO.pdf').write_bytes(b'2')
    steps=q004.plan(root,dst)
    assert len(steps)==3
    assert len({str(dest) for _,dest in steps})==3


def test_q004_reject_nested(tmp_path):
    src=tmp_path/'root';src.mkdir()
    with pytest.raises(ValueError):q004.plan(src,src/'out')


def test_q012_plan_and_copy(tmp_path):
    src=tmp_path/'docs';src.mkdir();dest=tmp_path/'dest'
    (src/'DEMO001.pdf').write_bytes(b'pdf-1')
    mapping=tmp_path/'map.xlsx';excel(mapping,['Tipo','Zona','Codigo'],[['Ficha','Sitio','DEMO001'],['Ficha','Sitio','DEMO999']])
    steps,missing=q012.plan(mapping,src,dest)
    assert len(steps)==1 and missing==['DEMO999']
    assert q012.copy_documents(steps)==0 and not dest.exists()
    assert q012.copy_documents(steps,execute=True)==1
    assert (dest/'Ficha'/'Sitio'/'DEMO001'/'DEMO001.pdf').read_bytes()==b'pdf-1'


def test_q012_segment_traversal():
    for s in ('../escape','/root','', '..',r'..\escape'):
        with pytest.raises(ValueError):q012.safe_segment(s)


def test_q012_requires_columns(tmp_path):
    x=tmp_path/'a.xlsx';excel(x,['City','Code'],[['A','B']])
    with pytest.raises(ValueError):list(q012.read_mapping(x))


def test_q012_reject_nested(tmp_path):
    source=tmp_path/'in';source.mkdir()
    x=tmp_path/'a.xlsx';excel(x,['Tipo','Zona','Codigo'],[['A','B','C']])
    with pytest.raises(ValueError):q012.plan(x,source,source/'output')


def test_d002_url_normalization():
    assert d002.canonical_url('https://EXAMPLE.org/a?utm_source=demo&b=2')=='https://example.org/a?b=2'
    assert d002.canonical_url('ftp://example.org')==''
    assert d002.canonical_url('http://localhost/secure')==''


def test_d002_detect_duplicates(tmp_path):
    input=tmp_path/'urls.xlsx';output=tmp_path/'out.xlsx'
    excel(input,['URL','Autor'],[['https://example.org/a?utm_source=demo','A'],['https://example.org/a','B'],['unparsable','C']])
    count,dups=d002.process(input,output)
    assert (count,dups)==(3,1)
    wb=load_workbook(output)
    assert wb['Duplicados'].max_row==2 and wb['Resumen']['B2'].value==3
    with pytest.raises(FileExistsError):d002.process(input,output)


def test_d002_safe_formula():
    assert d002.safe_cell('=1+1')=="'=1+1"


def test_d002_missing_url_column(tmp_path):
    f=tmp_path/'a.xlsx';excel(f,['Name'],[['A']])
    with pytest.raises(ValueError):list(d002.read_rows(f))


def test_d003_generate_demo_pdf(tmp_path):
    x=tmp_path/'names.xlsx';excel(x,['Nombre','Codigo'],[['Persona Inventada','DEMO001']])
    result=d003.process(x,tmp_path/'out')
    assert result==1
    with fitz.open(tmp_path/'out'/'demo_DEMO001.pdf') as doc:
        text=doc[0].get_text()
        assert 'SIN VALIDEZ OFICIAL' in text
        assert 'Persona Inventada' in text
    with pytest.raises(FileExistsError):d003.process(x,tmp_path/'out')


def test_d003_bad_code(tmp_path):
    x=tmp_path/'names.xlsx';excel(x,['Nombre','Codigo'],[['Nombre','../unsafe']])
    with pytest.raises(ValueError):list(d003.entries(x))


def test_d003_duplicate_code(tmp_path):
    x=tmp_path/'names.xlsx';excel(x,['Nombre','Codigo'],[['Persona A','X'],['Persona B','X']])
    with pytest.raises(ValueError):d003.prepare(x,tmp_path/'dest')


def test_d003_missing_fields(tmp_path):
    x=tmp_path/'names.xlsx';excel(x,['Nombre','Otro'],[['Persona A','X']])
    with pytest.raises(ValueError):list(d003.entries(x))


def test_a005_dry_run_and_report(tmp_path):
    src=tmp_path/'src';(src/'year'/'AREA123').mkdir(parents=True)
    (src/'year'/'AREA123'/'document.pdf').write_bytes(b'content')
    (src/'year'/'OTRO999').mkdir()
    (src/'year'/'OTRO999'/'other.pdf').write_bytes(b'other')
    x=tmp_path/'list.xlsx';excel(x,['Grupo','Codigo'],[['DEMO','AREA123'],['OTRO','OTRO999']])
    dest=tmp_path/'dst';report=tmp_path/'audit.xlsx'
    steps=a005.plan(src,x,dest,'DEMO')
    assert len(steps)==1 and steps[0][0].name=='document.pdf'
    a005.report(steps,report)
    assert a005.copy(steps)==0 and not dest.exists()
    assert a005.copy(steps,execute=True)==1
    assert (dest/'year'/'AREA123'/'document.pdf').read_bytes()==b'content'
    assert (src/'year'/'OTRO999'/'other.pdf').exists()


def test_a005_group_missing(tmp_path):
    src=tmp_path/'src';src.mkdir();x=tmp_path/'a.xlsx';excel(x,['Grupo','Codigo'],[['X','A']])
    assert a005.plan(src,x,tmp_path/'dst','DEMO')==[]


def test_a005_reject_nested(tmp_path):
    src=tmp_path/'src';src.mkdir();x=tmp_path/'a.xlsx';excel(x,['Grupo','Codigo'],[['X','A']])
    with pytest.raises(ValueError):a005.plan(src,x,src/'dst','DEMO')


def test_a005_report_no_overwrite(tmp_path):
    p=tmp_path/'a.xlsx';a005.report([],p)
    with pytest.raises(FileExistsError):a005.report([],p)
