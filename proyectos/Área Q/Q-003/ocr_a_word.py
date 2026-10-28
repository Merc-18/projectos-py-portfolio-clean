"""Transcripcion local de imagenes a Word, adaptada de un proyecto original.

Conserva Otsu, mejora de contraste, ordenamiento numerico y salida DOCX.
Nunca envia imagenes a servicios externos.
"""
import argparse
from datetime import datetime
import os
from pathlib import Path
import re

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from docx import Document
from docx.shared import Inches, Pt

ESCALA = 3.0
CONTRASTE = 1.8


def _otsu_umbral(arr: np.ndarray) -> int:
    histograma, _ = np.histogram(arr.flatten(), bins=256, range=(0, 256))
    total = arr.size
    suma = np.dot(np.arange(256), histograma)
    suma_fondo = peso_fondo = varianza_max = 0
    umbral = 128
    for t in range(256):
        peso_fondo += histograma[t]
        if not peso_fondo:
            continue
        peso_frente = total - peso_fondo
        if not peso_frente:
            break
        suma_fondo += t * histograma[t]
        media_fondo = suma_fondo / peso_fondo
        media_frente = (suma - suma_fondo) / peso_frente
        varianza = peso_fondo * peso_frente * (media_fondo - media_frente) ** 2
        if varianza > varianza_max:
            varianza_max, umbral = varianza, t
    return umbral


def preprocesar_imagen(ruta_img: Path) -> Image.Image:
    with Image.open(ruta_img) as original:
        img = original.convert("L")
    w, h = img.size
    img = img.resize((max(1, int(w * ESCALA)), max(1, int(h * ESCALA))), Image.Resampling.LANCZOS)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = ImageEnhance.Contrast(img).enhance(CONTRASTE)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    umbral = _otsu_umbral(np.array(img))
    return img.point(lambda pixel: 0 if pixel < umbral else 255, "1")


def _clave_imagen(ruta: Path) -> tuple[int, int, str]:
    match = re.search(r"(\d+)(?:\.(\d+))?", ruta.stem)
    if not match:
        return (0, 0, ruta.name.casefold())
    return (int(match.group(1)), int(match.group(2) or 0), ruta.name.casefold())


def ocr_imagen(img: Image.Image, idioma: str = "spa") -> str:
    ejecutable = os.environ.get("TESSERACT_CMD")
    if ejecutable:
        pytesseract.pytesseract.tesseract_cmd = ejecutable
    return pytesseract.image_to_string(img, config="--oem 1 --psm 6", lang=idioma)


def texto_a_word(transcripciones: list[tuple[str, str]], ruta_salida: Path) -> None:
    ruta_salida = Path(ruta_salida)
    if ruta_salida.exists():
        raise FileExistsError(f"No se sobreescribe el archivo: {ruta_salida}")
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.2)
        section.right_margin = Inches(1.0)
    for i, (nombre, texto) in enumerate(transcripciones):
        if i:
            doc.add_page_break()
        if len(transcripciones) > 1:
            p = doc.add_paragraph(f"Imagen: {nombre}")
            p.runs[0].bold = True
            p.runs[0].font.size = Pt(9)
        for linea in texto.splitlines():
            doc.add_paragraph(linea.strip())
    doc.save(ruta_salida)


def transcribir_carpeta(carpeta: Path, destino: Path, idioma="spa") -> Path:
    carpeta = Path(carpeta).resolve()
    destino = Path(destino).resolve()
    if not carpeta.is_dir():
        raise ValueError("La carpeta de imagenes no existe")
    imagenes = sorted((p for p in carpeta.rglob("*")
                       if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg"}),
                      key=_clave_imagen)
    if not imagenes:
        raise ValueError("No se encontraron imagenes")
    # Se conserva el esquema de nombre por fecha, sin acceder a carpetas corporativas.
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    outfile = destino / f"transcripcion_{stamp}.docx"
    if outfile.exists():
        raise FileExistsError(f"El archivo ya existe: {outfile}")
    transcripciones = [(p.name, ocr_imagen(preprocesar_imagen(p), idioma)) for p in imagenes]
    texto_a_word(transcripciones, outfile)
    return outfile


def main():
    parser = argparse.ArgumentParser(description="OCR local de imagenes y salida Word")
    parser.add_argument("carpeta", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--lang", default="spa", help="Idioma instalado en Tesseract")
    args = parser.parse_args()
    print(transcribir_carpeta(args.carpeta, args.output, args.lang))


if __name__ == "__main__":
    main()
