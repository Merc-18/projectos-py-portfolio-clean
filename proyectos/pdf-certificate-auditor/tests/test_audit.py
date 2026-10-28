import csv
import sys
from pathlib import Path
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from audit import is_certificate_pdf, normalized_name,scan,report

class AuditTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.root=Path(self.t.name)/'in'; self.root.mkdir(); self.output=Path(self.t.name)/'report.csv'

    def test_accented_and_case_insensitive_pdf(self):
        self.assertTrue(is_certificate_pdf('CERTIFICACIÓN Académica.PDF'))
        self.assertTrue(is_certificate_pdf('Certificados Generados.pdf'))
        self.assertTrue(is_certificate_pdf('certificate.pdf'))
        self.assertTrue(is_certificate_pdf('cert.pdf'))

    def test_non_pdf_not_certificate(self):
        self.assertFalse(is_certificate_pdf('certificado.xlsx'))
        self.assertFalse(is_certificate_pdf('misc.pdf'))

    def test_unicode_normalization(self):
        self.assertEqual(normalized_name('Ñandú'),'nandu')

    def test_all_files_present_not_deleted(self):
        (self.root/'certificación.pdf').write_bytes(b'fake pdf')
        (self.root/'notes.txt').write_text('demo')
        before={x.name:x.read_bytes() for x in self.root.iterdir()}
        results=report(self.root,self.output)
        after={x.name:x.read_bytes() for x in self.root.iterdir()}
        self.assertEqual(before,after)
        self.assertEqual(len(results),2)
        with self.output.open(encoding='utf-8-sig',newline='') as file:
            self.assertEqual(len(list(csv.DictReader(file))),2)

    def test_others_are_review_not_delete(self):
        (self.root/'photo.png').write_bytes(b'png')
        self.assertEqual(scan(self.root)[0]['Classification'],'MANUAL_REVIEW')

    def test_reject_output_in_scan_root(self):
        with self.assertRaises(ValueError):report(self.root,self.root/'report.csv')

    def test_no_overwrite(self):
        self.output.write_text('EXISTING')
        with self.assertRaises(FileExistsError):report(self.root,self.output)
        self.assertEqual(self.output.read_text(),'EXISTING')

    def test_output_overwrite(self):
        report(self.root,self.output)
        report(self.root,self.output,overwrite=True)
        self.assertIn('Relative Path',self.output.read_text(encoding='utf-8-sig'))

    def test_subfolders_and_relative_paths(self):
        (self.root/'A').mkdir();(self.root/'A'/'certificado.pdf').write_bytes(b'x')
        self.assertEqual(scan(self.root)[0]['Relative Path'],'A/certificado.pdf')

    def test_csv_formula_injection_from_filename(self):
        (self.root/'=cmd.pdf').write_bytes(b'x')
        report(self.root,self.output)
        with self.output.open(encoding='utf-8-sig',newline='') as file:
            record=list(csv.DictReader(file))[0]
        self.assertEqual(record['Relative Path'],"'=cmd.pdf")

    def test_symlink_is_ignored(self):
        x=self.root/'cert.pdf'; x.write_bytes(b'x');(self.root/'link.pdf').symlink_to(x)
        self.assertEqual(len(scan(self.root)),1)

    def test_root_missing(self):
        with self.assertRaises(ValueError):scan(self.root/'missing')

if __name__=='__main__':unittest.main()
