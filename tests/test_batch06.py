import csv
import importlib.util
from pathlib import Path
import fitz
from openpyxl import Workbook,load_workbook
import pytest

ROOT=Path(__file__).resolve().parents[1]/'proyectos'

def load(area,id,file):
    path=ROOT/area/id/file;spec=importlib.util.spec_from_file_location(id.replace('-',''),path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

q016=load('Área Q','Q-016','pdf_duplicates.py')
q017=load('Área Q','Q-017','merge_reports.py')
d001=load('Área D','D-001','local_resources.py')
q018=load('Área Q','Q-018','secure_downloader.py')


def book(path,headers,items):
    w=Workbook();ws=w.active;ws.append(headers)
    for i in items:ws.append(i)
    w.save(path)


def pdf(path,code):
    with fitz.open() as d:
        p=d.new_page(width=420,height=500)
        p.insert_text((30,40),'DOCUMENTO FICTICIO')
        if code:p.draw_rect(fitz.Rect(50,320,180,420),color=(0,0,0),fill=(0,0,0))
        d.save(path)


def test_q016_exact_pdf_duplicates(tmp_path):
    folder=tmp_path/'docs';folder.mkdir()
    p=folder/'one.pdf';pdf(p,1)
    (folder/'copy.pdf').write_bytes(p.read_bytes())
    pairs,bad,count=q016.compare(folder)
    assert (len(pairs),bad,count)==(1,[],2)
    assert pairs[0][2]=='IDENTICO'
    report=tmp_path/'report.csv';q016.write_report(pairs,bad,count,report)
    assert len(list(csv.DictReader(report.open(encoding='utf-8-sig'))))==1


def test_q016_bad_limits(tmp_path):
    with pytest.raises(ValueError):q016.compare(tmp_path,threshold=-1)
    with pytest.raises(ValueError):q016.compare(tmp_path,max_files=0)


def test_q016_no_overwrite(tmp_path):
    p=tmp_path/'report.csv';q016.write_report([],[],0,p)
    with pytest.raises(FileExistsError):q016.write_report([],[],0,p)


def test_q017_merge_reports(tmp_path):
    src=tmp_path/'source';(src/'set1').mkdir(parents=True)
    book(src/'set1'/'one.xlsx',['Codigo','Observacion'],[['A','Ficticia'],['B','']])
    book(src/'set1'/'two.xlsx',['Codigo','Observacion'],[['B','']])
    observations,missing,count=q017.collect(src)
    assert count==2 and len(observations)==1 and len(missing)==1
    out=tmp_path/'out.xlsx';q017.export(observations,missing,count,out)
    wb=load_workbook(out)
    assert wb['Resumen']['B4'].value==1 and wb['Observaciones']['B2'].value=='A'
    with pytest.raises(FileExistsError):q017.export(observations,missing,count,out)


def test_q017_formula_safety():
    assert q017.literal('=1+1')=="'=1+1"


def test_q017_missing_columns(tmp_path):
    inp=tmp_path/'source';inp.mkdir();book(inp/'a.xlsx',['Nombre'],[['X']])
    with pytest.raises(ValueError):q017.collect(inp)


def test_d001_offline_scraper(tmp_path):
    source=tmp_path/'pages';source.mkdir()
    (source/'page.html').write_text('<article data-demo-id="R01"><h2>Recurso de prueba</h2><p>Descripción ficticia</p><a href="https://example.org/test">Ver</a></article>',encoding='utf8')
    report=tmp_path/'report.csv';assert d001.extract(source,report)==1
    rows=list(csv.DictReader(report.open(encoding='utf-8-sig')))
    assert rows[0]['ID']=='R01' and rows[0]['Enlace']=='https://example.org/test'
    with pytest.raises(FileExistsError):d001.extract(source,report)


def test_d001_link_filter(tmp_path):
    p=tmp_path/'a.html';p.write_text('<article data-demo-id="1"><h3>Test</h3><a href="https://private.example.com/abc">Link</a></article>')
    assert d001.scan_html(p)[0][-1]==''


def test_d001_formula_csv():
    assert d001.csv_text('@x')=="'@x"


class FakeResponse:
    status_code=200
    headers={'Content-Length':'5'}
    def iter_content(self,chunk_size):yield b'hello'
    def raise_for_status(self):pass
    def close(self):pass

class FakeSession:
    def get(self,url,**kw):
        assert kw['allow_redirects'] is False and kw['headers']['Authorization']=='Bearer synthetic_token'
        return FakeResponse()


def test_q018_parse_and_download_offline(tmp_path):
    manifest=tmp_path/'file.csv';manifest.write_text('Filename,URL\nfile.txt,https://example.org/one\n',encoding='utf8')
    items=q018.read_manifest(manifest,'example.org')
    assert len(items)==1
    assert q018.download(items,tmp_path/'out')==0
    assert not (tmp_path/'out').exists()
    assert q018.download(items,tmp_path/'out',execute=True,token='synthetic_token',session=FakeSession())==1
    assert (tmp_path/'out'/'file.txt').read_bytes()==b'hello'


def test_q018_unauthorized_domain(tmp_path):
    m=tmp_path/'file.csv';m.write_text('Filename,URL\na,https://elsewhere.org/file\n',encoding='utf8')
    with pytest.raises(ValueError):q018.read_manifest(m,'example.org')


def test_q018_bad_url_and_path():
    for name in ('../secret.txt','/abs.txt','',r'folder\file'):
        with pytest.raises(ValueError):q018.safe_filename(name)
    with pytest.raises(ValueError):q018.authorized_url('http://example.org/no','example.org')
    with pytest.raises(ValueError):q018.authorized_url('https://example.org:9999/no','example.org')


def test_q018_token_required(tmp_path):
    with pytest.raises(ValueError):q018.download([('https://example.org/a','a')],tmp_path/'out',execute=True,token=None)
