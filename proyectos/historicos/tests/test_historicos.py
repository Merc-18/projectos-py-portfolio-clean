"""Synthetic, no-network smoke tests for historical portfolio code."""
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from importlib.util import spec_from_file_location, module_from_spec

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location('portfolio_core', ROOT / '_shared' / 'core.py')
core = module_from_spec(spec)
spec.loader.exec_module(core)


class HistoricalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = tempfile.TemporaryDirectory()
        cls.base = Path(cls.context.name)
        cls.inputs = cls.base/'input'; cls.inputs.mkdir()
        cls.outputs = cls.base/'out'; cls.outputs.mkdir()
        f = cls.inputs
        with (f/'rows.csv').open('w', encoding='utf-8', newline='') as h:
            csv.writer(h).writerows([['id','source','target','amount','date','url'],['1','Cafe One','cafe one','5','2026-01-03','/a'],['2','Library','Librari','7','2026-01-04','/b'],['3','=1+1','x','8','2026-02-07','/a']])
        (f/'dates.csv').write_text('date\n2026-01-01\n31/01/2026\n', encoding='utf-8')
        a=f/'two_csv';a.mkdir();(a/'one.csv').write_text('id,val\n1,x\n2,y\n');(a/'two.csv').write_text('id,other\n1,a\n2,b\n')
        from openpyxl import Workbook
        d=f/'two_xlsx';d.mkdir()
        for path in (f/'one.xlsx',d/'a.xlsx',d/'b.xlsx'):
            wb=Workbook();ws=wb.active;ws.append(['id','name','amount']);ws.append([1,'alpha',4]);ws.append([2,'beta',2]);wb.save(path)
        import fitz
        doc=fitz.open();p=doc.new_page(width=595,height=842);p.insert_text((60,90),'Synthetic Example Document');doc.save(f/'sample.pdf');doc.close()
        pdfs=f/'pdfs';pdfs.mkdir();(pdfs/'a.pdf').write_bytes((f/'sample.pdf').read_bytes());(pdfs/'b.pdf').write_bytes((f/'sample.pdf').read_bytes())
        from PIL import Image,ImageDraw
        img=Image.new('RGB',(500,120),'white');ImageDraw.Draw(img).text((20,25),'DEMO 123',fill='black');img.save(f/'picture.png')
        from docx import Document
        docx=Document();docx.add_paragraph('This list includes example.pdf and sample.pdf');tbl=docx.add_table(rows=2,cols=2);tbl.cell(0,0).text='name';tbl.cell(0,1).text='value';tbl.cell(1,0).text='demo';tbl.cell(1,1).text='123';docx.save(f/'sample.docx')
        (f/'sample.eml').write_text('From: sender@example.test\nTo: recipient@example.test\nSubject: Synthetic item\nContent-Type: text/plain; charset=utf-8\n\nSynthetic email body.\n')
        (f/'sample.html').write_text('<!doctype html><title>Example</title><a href="/one">One</a><a href="/two">Two</a>')
        (f/'request.json').write_text('{"id":"demo","message":"example"}')
        (f/'inventory').mkdir();(f/'inventory'/'example.txt').write_text('hello')

    @classmethod
    def tearDownClass(cls):
        cls.context.cleanup()

    def source(self,mode):
        names={'normalize_csv':'rows.csv','join_csv':'two_csv','fuzzy_csv':'rows.csv','numeric_summary':'rows.csv','period_window':'dates.csv','count_urls':'rows.csv','sort_xlsx':'one.xlsx','concat_xlsx':'two_xlsx','unpivot_xlsx':'one.xlsx','compare_headers':'two_xlsx','excel_template':'rows.csv','daily_csv':'dates.csv','scan_files':'inventory','rename_preview':'pdfs','copy_pdfs':'pdfs','pdf_pages':'sample.pdf','pdf_text':'sample.pdf','number_pdf':'sample.pdf','ocr_pdf':'sample.pdf','ocr_image':'picture.png','image_hash':'picture.png','word_tables':'sample.docx','docx_paths':'sample.docx','eml_summary':'sample.eml','eml_to_docx':'sample.eml','html_extract':'sample.html','mock_api':'request.json','dashboard_html':'rows.csv'}
        return self.inputs/names[mode]

    def output(self,mode,id):
        ext='xlsx' if mode in ('sort_xlsx','concat_xlsx','unpivot_xlsx','compare_headers','excel_template') else 'pdf' if mode=='number_pdf' else 'docx' if mode=='eml_to_docx' else 'txt' if mode in ('ocr_pdf','ocr_image') else 'json' if mode=='mock_api' else 'html' if mode=='dashboard_html' else 'csv'
        return self.outputs/f'{id}.{ext}'

    def test_every_wrapper_with_fictional_inputs(self):
        manifest=json.loads((ROOT/'historical_manifest.json').read_text())
        total=0
        for row in manifest['records']:
            if row['status']!='OFFLINE_RECONSTRUCTION':continue
            id,mode=row['id'],row['method']
            src,dst=self.source(mode),self.output(mode,id)
            if mode=='copy_pdfs':dst=self.outputs/f'{id}_dry_run'
            args=[sys.executable,str(ROOT/id/'run.py'),'--input',str(src),'--output',str(dst)]
            if mode in ('numeric_summary',):args+=['--key','id','--value','amount']
            if mode in ('period_window','daily_csv'):args+=['--key','date']
            if mode=='count_urls':args+=['--key','url']
            if mode=='fuzzy_csv':args+=['--key','source','--value','target']
            print('RUN', id, mode, flush=True)
            proc=subprocess.run(args,capture_output=True,text=True,timeout=15)
            self.assertEqual(proc.returncode,0,f'{id} failed: {proc.stderr}')
            self.assertEqual(json.loads(proc.stdout.splitlines()[-1])['mode'],mode)
            self.assertEqual(dst.exists(),mode!='copy_pdfs',id)
            total+=1
        self.assertEqual(total,51)

    def test_no_overwrite(self):
        inp=self.inputs/'rows.csv';out=self.outputs/'overwrite.csv'
        core.main(['--mode','normalize_csv','--input',str(inp),'--output',str(out)])
        with self.assertRaises(FileExistsError):core.main(['--mode','normalize_csv','--input',str(inp),'--output',str(out)])

    def test_formula_injection_escape(self):
        inp=self.inputs/'rows.csv';out=self.outputs/'formula.csv'
        core.main(['--mode','normalize_csv','--input',str(inp),'--output',str(out)])
        self.assertEqual(core.load_csv(out)[2]['source'],"'=1+1")

    def test_copy_dry_run_then_execute(self):
        inp=self.inputs/'pdfs';dst=self.outputs/'copied'
        core.main(['--mode','copy_pdfs','--input',str(inp),'--output',str(dst)])
        self.assertFalse(dst.exists())
        core.main(['--mode','copy_pdfs','--input',str(inp),'--output',str(dst),'--execute'])
        self.assertEqual(len(list(dst.glob('*.pdf'))),2)
        with self.assertRaises(FileExistsError):core.main(['--mode','copy_pdfs','--input',str(inp),'--output',str(dst),'--execute'])

    def test_input_cannot_be_overwritten(self):
        inp=self.inputs/'rows.csv'
        with self.assertRaises(ValueError):core.main(['--mode','normalize_csv','--input',str(inp),'--output',str(inp)])
        d=self.inputs/'inventory'
        with self.assertRaises(ValueError):core.main(['--mode','scan_files','--input',str(d),'--output',str(d/'result.csv')])

    def test_inventory_counts_and_source_separation(self):
        j=json.loads((ROOT/'historical_manifest.json').read_text())
        self.assertEqual(len(j['records']),69)
        self.assertEqual(j['total_historical'],71)
        self.assertEqual(j['hidden_count'],2)
        self.assertEqual(j['role_counts'],{'SOLUCION':47,'VARIANTE':9,'COMPONENTE':6,'EXPERIMENTO':5,'DUPLICADO':2})
        self.assertEqual(sum(r['status']=='DUPLICATE_NO_CODE' for r in j['records']),2)
        self.assertEqual(sum(r['status']=='RESTRICTED_NO_SOURCE' for r in j['records']),2)
        self.assertTrue(all(not r['source_code_copied'] and not r['public_approved'] for r in j['records']))

    def test_basic_normalization(self):
        self.assertEqual(core.clean_key('Cafe One'), 'cafe_one')
        self.assertEqual(core.safe_value('=SUM(A1)'),"'=SUM(A1)")

if __name__=='__main__':unittest.main()
