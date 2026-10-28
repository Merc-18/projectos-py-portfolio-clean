import sys
from pathlib import Path
import tempfile
import unittest
from openpyxl import Workbook, load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from consolidate import consolidate, discover_files, as_text


def make_book(path, sheets):
    book = Workbook()
    first = True
    for name, rows in sheets.items():
        ws = book.active if first else book.create_sheet()
        ws.title = name
        first = False
        for row in rows:
            ws.append(row)
    book.save(path)


class ConsolidateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'input'
        self.source.mkdir()
        self.out = self.root / 'result.xlsx'

    def test_discover_order(self):
        make_book(self.source / 'z.xlsx', {'Data': [['A'], [1]]})
        make_book(self.source / 'a.xlsx', {'Data': [['A'], [2]]})
        self.assertEqual([p.name for p in discover_files(self.source, self.out)], ['a.xlsx','z.xlsx'])

    def test_union_headers_and_provenance(self):
        make_book(self.source / 'first.xlsx', {'North': [['Name','Count'], ['Alpha', 3]]})
        make_book(self.source / 'second.xlsx', {'South': [['Name','Zone'], ['Beta','East']]})
        result = consolidate(self.source, self.out)
        self.assertEqual(result, {'files':2, 'rows':2, 'columns':3})
        ws = load_workbook(self.out, data_only=True).active
        self.assertEqual([c.value for c in ws[1]], ['Source File','Source Sheet','Name','Count','Zone'])
        self.assertEqual([c.value for c in ws[2]], ['first.xlsx','North','Alpha',3,None])
        self.assertEqual([c.value for c in ws[3]], ['second.xlsx','South','Beta',None,'East'])
        self.assertEqual(ws.freeze_panes, 'C2')

    def test_multiple_sheets(self):
        make_book(self.source / 'sample.xlsx', {'First': [['A'], [1]],'Second':[['A'],[2]]})
        self.assertEqual(consolidate(self.source,self.out)['rows'],2)

    def test_blank_rows_skipped(self):
        make_book(self.source / 'x.xlsx', {'Data':[['A'],[1],[None],[2]]})
        self.assertEqual(consolidate(self.source,self.out)['rows'],2)

    def test_input_not_modified(self):
        x=self.source/'x.xlsx'; make_book(x, {'Data':[['A'],[1]]}); orig=x.read_bytes()
        consolidate(self.source, self.out)
        self.assertEqual(x.read_bytes(),orig)

    def test_no_overwrite(self):
        make_book(self.source / 'x.xlsx', {'Data':[['A'],[1]]}); self.out.write_bytes(b'keep')
        with self.assertRaises(FileExistsError): consolidate(self.source, self.out)
        self.assertEqual(self.out.read_bytes(),b'keep')
        consolidate(self.source, self.out, overwrite=True)
        self.assertEqual(load_workbook(self.out).active['C2'].value,1)

    def test_excludes_output_in_source_folder(self):
        x=self.source/'x.xlsx'; make_book(x, {'Data':[['A'],[1]]})
        out=self.source/'output.xlsx'
        consolidate(self.source,out)
        self.assertEqual(consolidate(self.source,out,overwrite=True)['files'],1)

    def test_duplicate_headers_rejected(self):
        make_book(self.source/'x.xlsx', {'Data':[['A','A'],[1,2]]})
        with self.assertRaisesRegex(ValueError,'Duplicate'): consolidate(self.source,self.out)

    def test_empty_folder_rejected(self):
        with self.assertRaisesRegex(ValueError,'No XLSX'): consolidate(self.source,self.out)

    def test_reserved_column_rejected(self):
        make_book(self.source/'x.xlsx', {'Data':[['Source File'],['X']]})
        with self.assertRaisesRegex(ValueError,'reserved'): consolidate(self.source,self.out)

    def test_formula_like_string_escaped(self):
        self.assertEqual(as_text('=1+1'),"'=1+1")
        make_book(self.source/'x.xlsx', {'Data':[['A'],["@hello"]]})
        ws=load_workbook(self.source/'x.xlsx').active
        ws['A2'].data_type='s'
        ws.parent.save(self.source/'x.xlsx')
        consolidate(self.source,self.out)
        out_ws=load_workbook(self.out).active
        self.assertEqual(out_ws['C2'].value,"'@hello")

    def test_bad_output_extension(self):
        with self.assertRaisesRegex(ValueError, 'xlsx'): consolidate(self.source,self.root/'result.csv')


if __name__ == '__main__': unittest.main()
