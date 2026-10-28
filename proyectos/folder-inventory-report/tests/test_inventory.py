import sys
from pathlib import Path
import tempfile
import unittest
from openpyxl import load_workbook

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from inventory import leaf_folders,create_report


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory(); self.addCleanup(self.t.cleanup)
        self.base=Path(self.t.name); self.root=self.base/'source'; self.root.mkdir()
        self.output=self.base/'report.xlsx'

    def test_empty_root_is_leaf(self):
        self.assertEqual(leaf_folders(self.root), [('.',0,0)])

    def test_leaf_only_and_counts(self):
        (self.root/'A'/'B').mkdir(parents=True)
        (self.root/'C').mkdir()
        (self.root/'A'/'B'/'x.pdf').write_bytes(b'demo')
        (self.root/'A'/'B'/'Y.PDF').write_bytes(b'demo')
        (self.root/'A'/'B'/'notes.txt').write_text('demo')
        (self.root/'C'/'desktop.ini').write_text('system')
        self.assertEqual(leaf_folders(self.root), [('A/B',3,2),('C',0,0)])

    def test_xlsx_export_relative_only(self):
        (self.root/'Demo').mkdir(); (self.root/'Demo'/'example.pdf').write_text('demo')
        create_report(self.root,self.output)
        wb=load_workbook(self.output)
        self.assertEqual([c.value for c in wb.active[1]],['Relative Directory','File Count','PDF Count'])
        self.assertEqual([c.value for c in wb.active[2]],['Demo',1,1])
        self.assertNotIn(str(self.root),str(wb.active['A2'].value))
        self.assertEqual(wb.active.freeze_panes,'A2')

    def test_no_overwrite(self):
        self.output.write_bytes(b'existing')
        with self.assertRaises(FileExistsError): create_report(self.root,self.output)
        self.assertEqual(self.output.read_bytes(),b'existing')

    def test_explicit_overwrite(self):
        create_report(self.root,self.output)
        create_report(self.root,self.output,overwrite=True)
        self.assertTrue(self.output.is_file())

    def test_skip_symlink_file(self):
        (self.root/'original.pdf').write_bytes(b'test')
        (self.root/'link.pdf').symlink_to(self.root/'original.pdf')
        self.assertEqual(leaf_folders(self.root),[('.',1,1)])

    def test_skip_symlink_folder(self):
        outside=self.base/'outside'; outside.mkdir(); (outside/'secret.pdf').write_bytes(b'x')
        (self.root/'shortcut').symlink_to(outside,target_is_directory=True)
        self.assertEqual(leaf_folders(self.root),[('.',0,0)])

    def test_missing_root(self):
        with self.assertRaises(ValueError): leaf_folders(self.base/'absent')

    def test_reject_csv(self):
        with self.assertRaises(ValueError): create_report(self.root,self.base/'wrong.csv')

    def test_ignores_system_files_case_insensitive(self):
        (self.root/'Thumbs.DB').write_text('tmp')
        (self.root/'.DS_Store').write_text('tmp')
        self.assertEqual(leaf_folders(self.root),[('.',0,0)])


if __name__=='__main__':unittest.main()
