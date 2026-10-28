import sys
from pathlib import Path
import tempfile
import unittest
from openpyxl import Workbook

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from organize import safe_group, safe_source,plan,organize


def make_excel(path, rows):
    book=Workbook(); ws=book.active; ws.append(['Group ID','PDF 1','PDF 2'])
    for row in rows:ws.append(row)
    book.save(path)


class OrganizerTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.base=Path(self.t.name); self.root=self.base/'source'; self.root.mkdir()
        self.target=self.base/'dest'; self.excel=self.base/'mapping.xlsx'
        (self.root/'a.pdf').write_bytes(b'FIRST')
        (self.root/'b.pdf').write_bytes(b'SECOND')

    def test_basic_preview_no_changes(self):
        make_excel(self.excel,[('GRP01','a.pdf','b.pdf')])
        actions=organize(self.excel,self.root,self.target)
        self.assertEqual(len(actions),2)
        self.assertFalse(self.target.exists())

    def test_execute_copies_without_modifying_sources(self):
        make_excel(self.excel,[('GRP01','a.pdf','b.pdf')])
        actions=organize(self.excel,self.root,self.target,execute=True)
        self.assertEqual(len(actions),2)
        self.assertEqual((self.target/'GRP01'/'a.pdf').read_bytes(),b'FIRST')
        self.assertEqual((self.root/'a.pdf').read_bytes(),b'FIRST')

    def test_duplicate_names_in_one_group_auto_suffix(self):
        (self.root/'sub').mkdir();(self.root/'sub'/'a.pdf').write_bytes(b'THIRD')
        make_excel(self.excel,[('GRP','a.pdf','sub/a.pdf')])
        organize(self.excel,self.root,self.target,execute=True)
        self.assertEqual((self.target/'GRP'/'a.pdf').read_bytes(),b'FIRST')
        self.assertEqual((self.target/'GRP'/'a_2.pdf').read_bytes(),b'THIRD')

    def test_existing_target_is_not_overwritten(self):
        old=self.target/'GRP';old.mkdir(parents=True);(old/'a.pdf').write_bytes(b'OLD')
        make_excel(self.excel,[('GRP','a.pdf',None)])
        organize(self.excel,self.root,self.target,execute=True)
        self.assertEqual((old/'a.pdf').read_bytes(),b'OLD')
        self.assertEqual((old/'a_2.pdf').read_bytes(),b'FIRST')

    def test_traversal_group_rejected(self):
        make_excel(self.excel,[('../ESCAPE','a.pdf',None)])
        with self.assertRaises(ValueError):organize(self.excel,self.root,self.target,execute=True)
        self.assertFalse(self.target.exists())

    def test_absolute_source_rejected(self):
        make_excel(self.excel,[('G','/etc/passwd',None)])
        with self.assertRaises(ValueError):organize(self.excel,self.root,self.target,execute=True)

    def test_parent_source_traversal_rejected(self):
        make_excel(self.excel,[('G','../mapping.xlsx',None)])
        with self.assertRaises(ValueError):organize(self.excel,self.root,self.target,execute=True)

    def test_symlink_source_outside_rejected(self):
        other=self.base/'other.pdf';other.write_bytes(b'SECRET')
        (self.root/'escape.pdf').symlink_to(other)
        make_excel(self.excel,[('G','escape.pdf',None)])
        with self.assertRaises(ValueError):organize(self.excel,self.root,self.target,execute=True)

    def test_missing_source_fails_before_writes(self):
        make_excel(self.excel,[('G','a.pdf',None),('G','missing.pdf',None)])
        with self.assertRaises(FileNotFoundError):organize(self.excel,self.root,self.target,execute=True)
        self.assertFalse(self.target.exists())

    def test_invalid_header(self):
        book=Workbook();book.active.append(['Bad','PDF 1','PDF 2']);book.save(self.excel)
        with self.assertRaisesRegex(ValueError,'headers'):plan(self.excel,self.root,self.target)

    def test_blank_rows_ignored(self):
        make_excel(self.excel,[(None,None,None),('G','a.pdf',None)])
        self.assertEqual(len(plan(self.excel,self.root,self.target)),1)

    def test_source_nested_folder(self):
        (self.root/'sub').mkdir();(self.root/'sub'/'c.PDF').write_bytes(b'NESTED')
        make_excel(self.excel,[('G','sub/c.PDF',None)])
        organize(self.excel,self.root,self.target,execute=True)
        self.assertEqual((self.target/'G'/'c.PDF').read_bytes(),b'NESTED')

    def test_reject_output_inside_input(self):
        make_excel(self.excel,[('G','a.pdf',None)])
        with self.assertRaises(ValueError):plan(self.excel,self.root,self.root/'dest')

    def test_reject_bad_id(self):
        for value in ['../escape','A/B','A\\B','bad name','.', '']:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):safe_group(value)

    def test_reject_output_symlink(self):
        other=self.base/'outside';other.mkdir();self.target.symlink_to(other,target_is_directory=True)
        make_excel(self.excel,[('G','a.pdf',None)])
        with self.assertRaises(ValueError):plan(self.excel,self.root,self.target)

    def test_multiple_groups(self):
        make_excel(self.excel,[('A','a.pdf',None),('B','b.pdf',None)])
        organize(self.excel,self.root,self.target,execute=True)
        self.assertEqual((self.target/'B'/'b.pdf').read_bytes(),b'SECOND')


if __name__=='__main__':unittest.main()
