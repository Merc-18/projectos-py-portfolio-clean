"""Pruebas con fixtures sinteticos; no utilizan datos reales ni red."""
import importlib.util
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile
from io import BytesIO

import fitz
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from docx import Document

BASE = Path(__file__).resolve().parents[1] / "proyectos"
AREA_NOMBRES = {"Area_D": "Área D", "Area_Q": "Área Q"}


def load(area, ticket, file, namespace):
    path = BASE / AREA_NOMBRES[area] / ticket / file
    spec = importlib.util.spec_from_file_location(namespace, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_pdf(path, colors=(0,)):
    doc = fitz.open()
    for value in colors:
        page = doc.new_page(width=220, height=220)
        if value:
            shape = page.new_shape()
            shape.draw_rect(fitz.Rect(45, 45, 175, 175))
            shape.finish(fill=(0, 0, 0), color=(0, 0, 0))
            shape.commit()
        else:
            page.insert_text((80, 110), "ABC")
    doc.save(path)
    doc.close()


class SepararPdf(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("Area_D", "D-004", "separar_pdf.py", "d4")

    def test_por_pagina(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            sample_pdf(p / "demo.pdf", (0, 1, 0))
            paths = self.m.separar_pdf(p / "demo.pdf", p / "resultado")
            self.assertEqual(len(paths), 3)
            self.assertEqual([len(fitz.open(x)) for x in paths], [1, 1, 1])

    def test_no_sobrescribir(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            sample_pdf(p / "demo.pdf")
            self.m.separar_pdf(p / "demo.pdf", p / "resultado")
            with self.assertRaises(FileExistsError):
                self.m.separar_pdf(p / "demo.pdf", p / "resultado")

    def test_no_aceptar_extension_ajena(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            (p / "muestra.txt").write_text("texto")
            with self.assertRaises(ValueError):
                self.m.separar_pdf(p / "muestra.txt", p / "resultado")


class SegmentarPorBlancos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("Area_D", "D-007", "separar_pdf_blancas.py", "d7")

    def test_estados_ficticios(self):
        with TemporaryDirectory() as root:
            pdf = Path(root) / "demo.pdf"
            sample_pdf(pdf, (1, 0, 1))
            with fitz.open(pdf) as doc:
                a = self.m.analizar_pagina(doc[0])[0]
                b = self.m.analizar_pagina(doc[1])[0]
            self.assertEqual(a, "CONTENIDO")
            self.assertIn(b, {"BLANCO", "INDEFINIDO"})

    def test_bloques_con_indefinidos(self):
        result = self.m.bloques_de_contenido(["BLANCO", "CONTENIDO", "INDEFINIDO", "BLANCO", "CONTENIDO"])
        self.assertEqual(result, [([1, 2], True), ([4], False)])

    def test_segmentar_documento(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            sample_pdf(p / "demo.pdf", (1, 1, 1))
            out = self.m.procesar_pdf(p / "demo.pdf", p / "resultado")
            self.assertEqual(out["estados"], ["CONTENIDO"] * 3)
            self.assertEqual(len(out["bloques"]), 1)
            self.assertEqual(len(fitz.open(out["bloques"][0])), 3)

    def test_dpi_invalido(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            sample_pdf(p / "demo.pdf")
            with self.assertRaises(ValueError):
                self.m.procesar_pdf(p / "demo.pdf", p / "salida", dpi=20)


class OcrWord(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("Area_Q", "Q-003", "ocr_a_word.py", "q3")

    def test_umbral_otsu(self):
        a = np.array([[255] * 40 + [0] * 40] * 20, dtype=np.uint8)
        self.assertTrue(0 <= self.m._otsu_umbral(a) <= 255)

    def test_numeracion_orden(self):
        images = [Path("imagen10.png"), Path("imagen2.png"), Path("imagen3.1.png")]
        self.assertEqual([x.name for x in sorted(images, key=self.m._clave_imagen)], ["imagen2.png", "imagen3.1.png", "imagen10.png"])

    def test_word_local(self):
        with TemporaryDirectory() as root:
            target = Path(root) / "demo.docx"
            self.m.texto_a_word([("test.png", "HOLA\nMUNDO")], target)
            d = Document(target)
            self.assertIn("HOLA", [p.text for p in d.paragraphs])
            with self.assertRaises(FileExistsError):
                self.m.texto_a_word([("test.png", "otra")], target)

    def test_preprocesado_png(self):
        with TemporaryDirectory() as root:
            target = Path(root) / "img.png"
            Image.new("RGB", (40, 50), "white").save(target)
            out = self.m.preprocesar_imagen(target)
            self.assertEqual(out.size, (120, 150))


class ZipExcel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("Area_Q", "Q-002", "consolidar_indicadores.py", "q2")

    def make(self, path):
        with zipfile.ZipFile(path, "w") as z:
            for i in range(2):
                for n, sheet in self.m.ARCHIVOS_HOJAS.items():
                    df = pd.DataFrame({"ID": ["ID-A", "ID-B"], "PERIODO": [f"P{i+1}"] * 2, "Valor": [10+i, 20+i]})
                    buf = BytesIO()
                    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                        df.to_excel(writer, sheet_name=sheet, index=False)
                    z.writestr(f"periodo{i+1}/{n}", buf.getvalue())

    def test_union_horizontal_vertical(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            self.make(p / "series.zip")
            result = self.m.consolidar_zip(p / "series.zip", p / "result.xlsx")
            self.assertEqual(len(result), 4)
            self.assertEqual(set(["SERIE_A_Valor", "SERIE_B_Valor", "SERIE_C_Valor"]).issubset(result.columns), True)
            self.assertEqual(len(pd.read_excel(p / "result.xlsx")), 4)

    def test_no_sobrescribe(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            self.make(p / "series.zip")
            self.m.consolidar_zip(p / "series.zip", p / "result.xlsx")
            with self.assertRaises(FileExistsError):
                self.m.consolidar_zip(p / "series.zip", p / "result.xlsx")

    def test_rechaza_periodos_desbalanceados(self):
        with TemporaryDirectory() as root:
            p = Path(root)
            with zipfile.ZipFile(p / "series.zip", "w") as z:
                z.writestr("serie_a.xlsx", "ficticio")
            with self.assertRaises(ValueError):
                self.m.consolidar_zip(p / "series.zip", p / "out.xlsx")


class CopiaDocumentos(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = load("Area_Q", "Q-007", "copiar_documentos.py", "q7")

    def build(self, root):
        entrada = root / "entrada"
        for folder in [entrada / "ENERO-a" / "DOCUMENTOS", entrada / "ENERO-b" / "DOCUMENTOS"]:
            folder.mkdir(parents=True)
            (folder / "demo_TIPO_A.pdf").write_bytes(b"pdf ficticio")
        return entrada

    def test_mes(self):
        self.assertEqual(self.m.extraer_mes(Path("Marzo-01")), "MARZO")

    def test_simulacion_sin_copias(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            source = self.build(p)
            plan = self.m.copiar_documentos(source, p / "salida")
            self.assertEqual(len(plan), 2)
            self.assertFalse((p / "salida").exists())

    def test_ejecucion_y_nombres_colisionados(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            source = self.build(p)
            plan = self.m.copiar_documentos(source, p / "salida", ejecutar=True)
            self.assertEqual(len(plan), 2)
            self.assertTrue(all(dst.exists() for _, dst in plan))
            self.assertNotEqual(plan[0][1].name, plan[1][1].name)

    def test_rechaza_directorios_solapados(self):
        with TemporaryDirectory() as td:
            p = Path(td)
            source = self.build(p)
            with self.assertRaises(ValueError):
                self.m.plan_copias(source, source / "salida")


if __name__ == "__main__":
    unittest.main()
