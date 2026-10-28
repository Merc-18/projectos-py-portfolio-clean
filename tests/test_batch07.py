"""Fixtures entirely artificial. No network, company data or official documents."""
import csv
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

import fitz
from PIL import Image
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1] / 'proyectos'
sys.path.insert(0, str(ROOT))
# When running all batches from separate fixture folders, extend the shared package path.
import portfolio_core
if str(ROOT / 'portfolio_core') not in portfolio_core.__path__:
    portfolio_core.__path__.append(str(ROOT / 'portfolio_core'))


def load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


stamps = load('stamp_core', 'portfolio_core/pdf_demo_mark.py')
a1 = load('A001', 'Área A/A-001/demo_pdf.py')
a2 = load('A002', 'Área A/A-002/demo_pdf.py')
a3 = load('A003', 'Área A/A-003/demo_pdf.py')
a4 = load('A004', 'Área A/A-004/offline_form_bot.py')
d5 = load('D005', 'Área D/D-005/pdf_audit.py')
q20 = load('Q020', 'Área Q/Q-020/inspect_solution.py')
q21 = load('Q021', 'Área Q/Q-021/image_metadata.py')
g1 = load('G001', 'Área G/G-001/generate_pdf.py')


def pdf(path, lines=('Demo data',)):
    c = canvas.Canvas(str(path))
    for i,line in enumerate(lines):
        c.drawString(42, 690 - i*32, line)
    c.showPage()
    c.save()


class DemoStampTests(unittest.TestCase):
    def test_all_three_positions_create_marked_copy_without_changing_original(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            src=root/'source.pdf'
            pdf(src)
            before=src.read_bytes()
            for i,pos in enumerate(stamps.POSITIONS):
                dest=root/f'out-{i}.pdf'
                count=stamps.mark_demo(src,dest,pos)
                self.assertEqual(count,1)
                with fitz.open(dest) as document:
                    self.assertIn('MUESTRA - SIN FIRMA',document[0].get_text())
            self.assertEqual(src.read_bytes(),before)

    def test_refuse_same_path_and_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/'demo.pdf';pdf(p)
            with self.assertRaises(ValueError):stamps.mark_demo(p,p,'upper-right')
            out=root/'new.pdf';out.write_bytes(b'KEEP')
            with self.assertRaises(FileExistsError):stamps.mark_demo(p,out,'upper-right')
            self.assertEqual(out.read_bytes(),b'KEEP')

    def test_reject_unknown_position(self):
        with self.assertRaises(ValueError):stamps.mark_demo(Path('a.pdf'),Path('b.pdf'),'invalid')

    def test_three_ticket_wrappers_import_without_company_deps(self):
        self.assertTrue(callable(a1.main) and callable(a2.main) and callable(a3.main))


class ReadonlyPDFTests(unittest.TestCase):
    def test_detect_labeled_page_without_modification(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);pdf_path=root/'a.pdf';pdf(pdf_path,('DOCUMENTO FICTICIO','Fecha de registro: 01 Jan 2026'))
            before=pdf_path.read_bytes();data=d5.inspect_pdf(pdf_path)
            self.assertEqual(data[0][0],1);self.assertEqual(data[0][1],1)
            self.assertIn('documento ficticio',data[0][2]);self.assertEqual(pdf_path.read_bytes(),before)

    def test_export_audit_csv(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);folder=root/'source';folder.mkdir();pdf(folder/'a.pdf')
            target=root/'result.csv';self.assertEqual(d5.audit(folder,target),1)
            with target.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
            self.assertEqual(len(rows),1)
            with self.assertRaises(FileExistsError):d5.audit(folder,target)

    def test_audit_rejects_empty_folder(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaises(ValueError):d5.audit(root,root/'out.csv')


class XMLSummaryTests(unittest.TestCase):
    def test_anonymized_summary(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);p=root/'sample.xml';p.write_text('<Solution><Publisher>SECRET_NAME</Publisher><RootComponent/><Workflow/><MissingDependency/></Solution>',encoding='utf8')
            summary=q20.inspect(p)
            self.assertEqual(summary['identificadores_exportados'],0)
            self.assertEqual(summary['elementos_relevantes']['RootComponent'],1)
            self.assertNotIn('SECRET_NAME',str(summary))
            out=root/'summary.json';q20.save_summary(summary,out)
            self.assertNotIn('SECRET_NAME',out.read_text(encoding='utf8'))
            with self.assertRaises(FileExistsError):q20.save_summary(summary,out)

    def test_reject_entity_expansion(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'bad.xml';p.write_text('<!DOCTYPE a [<!ENTITY x SYSTEM "file:///etc/passwd">]><a>&x;</a>',encoding='utf8')
            with self.assertRaises(ValueError):q20.inspect(p)

    def test_reject_too_large_xml(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'huge.xml';p.write_bytes(b'X'*(q20.MAX_BYTES+1))
            with self.assertRaises(ValueError):q20.inspect(p)


class EXIFTests(unittest.TestCase):
    def test_image_metadata_does_not_export_coordinates(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);file=root/'demo.png';Image.new('RGB',(27,19),'white').save(file)
            data=q21.inspect(file)
            self.assertEqual(data[2:4],(27,19))
            self.assertEqual(data[5],'NO')
            out=root/'metadata.csv';self.assertEqual(q21.audit(root,out),1)
            self.assertNotIn('GPSLatitude',out.read_text(encoding='utf-8-sig'))

    def test_image_empty_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaises(ValueError):q21.audit(root,root/'x.csv')

    def test_reports_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);Image.new('RGB',(10,10)).save(root/'i.jpg');t=root/'out.csv';t.write_text('KEEP',encoding='utf8')
            with self.assertRaises(FileExistsError):q21.audit(root,t)
            self.assertEqual(t.read_text(),'KEEP')


class OfflineFormTests(unittest.TestCase):
    def test_validator_rejects_bad_field_sets(self):
        with self.assertRaises(ValueError):a4.validate({'codigo':'DEMO-1','fecha':'2026-01-01','password':'unsafe'})
        with self.assertRaises(ValueError):a4.validate({'codigo':'../','fecha':'2026-01-01','asunto':'Demo'})

    def test_local_chromium_fills_form_and_screenshots(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'filled.png'
            values={'codigo':'DEMO-001','fecha':'2026-01-15','asunto':'Formulario de ensayo'}
            result=a4.fill_demo(values,target,chromium_path='/usr/bin/chromium')
            self.assertEqual(result['campos_verificados'],3)
            self.assertEqual(result['servidores_consultados'],0)
            with Image.open(target) as im:self.assertGreater(im.width,500)
            with self.assertRaises(FileExistsError):a4.fill_demo(values,target,chromium_path='/usr/bin/chromium')


class StreamlitAlternativeTests(unittest.TestCase):
    def test_demo_pdf_content_and_watermark(self):
        with tempfile.TemporaryDirectory() as td:
            target=Path(td)/'demo.pdf'
            out=g1.create_demo_pdf('Registro totalmente ficticio','42.50',target)
            self.assertEqual(out,target)
            with fitz.open(target) as f:
                text=f[0].get_text()
                self.assertIn('DEMO - SIN VALIDEZ OFICIAL',text)
                self.assertIn('Registro totalmente ficticio',text)
                self.assertIn('42.50',text)

    def test_reject_invalid_amount(self):
        for amount in ['NaN','Infinity','-4','1000001','not a number']:
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):g1.validate('Demo',amount)

    def test_no_output_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'demo.pdf';out.write_bytes(b'PRESERVED')
            with self.assertRaises(FileExistsError):g1.create_demo_pdf('Demo','5.00',out)
            self.assertEqual(out.read_bytes(),b'PRESERVED')

    def test_invalid_extension(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):g1.create_demo_pdf('Demo','5.00',Path(td)/'demo.txt')


if __name__ == '__main__':unittest.main()
