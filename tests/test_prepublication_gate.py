"""Release candidate gate: read-only, no publication or remote writes."""
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
class PrepublicationGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog=json.loads((ROOT/'catalogo/unidades.json').read_text(encoding='utf-8'))
        cls.hist=json.loads((ROOT/'proyectos/historicos/historical_manifest.json').read_text(encoding='utf-8'))
        cls.rows=cls.catalog['registros']

    def test_inventory_and_unique_ids(self):
        self.assertEqual(len(self.rows),103)
        self.assertEqual(len({r['id'] for r in self.rows}),103)
        self.assertEqual(sum(r['grupo']=='ticket' for r in self.rows),34)
        self.assertEqual(sum(r['grupo']!='ticket' for r in self.rows),69)
        self.assertEqual(len(self.hist['records']),69)
        self.assertEqual(len({r['id'] for r in self.hist['records']}),69)
        self.assertEqual(self.catalog['resumen']['total'],105)

    def test_every_record_not_publicly_approved(self):
        for row in self.rows:
            with self.subTest(id=row['id']):
                self.assertIs(row['codigo_original_incluido'],False)
                if row['grupo']=='ticket':
                    self.assertIs(row['apto_para_publicar'],False)
                else:
                    self.assertIs(row['publicacion_aprobada'],False)
        for row in self.hist['records']:
            with self.subTest(id=row['id']):
                self.assertIs(row['public_approved'],False)
                self.assertIs(row['source_code_copied'],False)

    def test_no_external_code_links_or_missing_wrapper(self):
        for row in self.rows:
            link=row.get('enlace_codigo')
            if link:
                with self.subTest(id=row['id']):
                    self.assertFalse('://' in link)
                    target=(ROOT/link).resolve()
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file(),str(target))
        for row in self.hist['records']:
            if row['status']=='OFFLINE_RECONSTRUCTION':
                path=(ROOT/row['code']).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(),row['id'])

    def test_prepublication_stays_private_and_unlicensed(self):
        self.assertNotEqual(self.catalog['estado'],'PUBLICADO')
        self.assertFalse(any((ROOT/x).exists() for x in ('LICENSE','LICENSE.md','COPYING')))
        self.assertTrue((ROOT/'docs/AUTORIZACION_PREPUBLICACION_2026-11-02.md').is_file())

if __name__=='__main__':unittest.main()
