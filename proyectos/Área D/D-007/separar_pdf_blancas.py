"""Separar PDF por paginas en blanco; adaptacion del clasificador original.

Mantiene el analisis de pixeles oscuros y los estados BLANCO, CONTENIDO
INDEFINIDO. Los bloques ambiguos se separan para revision manual.
"""
from pathlib import Path
import argparse

import fitz
import numpy as np

MARGEN_CORTE_PCT = 0.06
UMBRAL_LUMINOSIDAD_OSCURO = 200
PCT_PIXELES_BLANCO_MAX = 0.0025
PCT_PIXELES_CONTENIDO_MIN = 0.010


def analizar_pagina(page: fitz.Page, dpi: int = 100) -> tuple[str, float]:
    """Clasifica una pagina segun el porcentaje de pixeles oscuros."""
    pix = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
    image = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)
    gris = np.dot(image, [0.2989, 0.5870, 0.1140])
    alto, ancho = gris.shape
    corte_h = int(alto * MARGEN_CORTE_PCT)
    corte_w = int(ancho * MARGEN_CORTE_PCT)
    if alto > 2 * corte_h and ancho > 2 * corte_w:
        gris = gris[corte_h:alto-corte_h, corte_w:ancho-corte_w]
    porcentaje = float(np.mean(gris < UMBRAL_LUMINOSIDAD_OSCURO)) if gris.size else 0
    if porcentaje <= PCT_PIXELES_BLANCO_MAX:
        return "BLANCO", porcentaje
    if porcentaje >= PCT_PIXELES_CONTENIDO_MIN:
        return "CONTENIDO", porcentaje
    return "INDEFINIDO", porcentaje


def bloques_de_contenido(estados: list[str]) -> list[tuple[list[int], bool]]:
    """Agrupa indices de paginas separadas por blancos; marca ambiguedad."""
    bloques, actual = [], []
    for indice, estado in enumerate(estados):
        if estado == "BLANCO":
            if actual:
                bloques.append((actual, any(estados[i] == "INDEFINIDO" for i in actual)))
                actual = []
        elif estado in {"CONTENIDO", "INDEFINIDO"}:
            actual.append(indice)
        else:
            raise ValueError(f"Estado desconocido: {estado}")
    if actual:
        bloques.append((actual, any(estados[i] == "INDEFINIDO" for i in actual)))
    return bloques


def procesar_pdf(archivo: Path, destino: Path, dpi: int = 100) -> dict:
    archivo, destino = Path(archivo).resolve(), Path(destino).resolve()
    if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
        raise ValueError("Se requiere un PDF existente")
    if dpi < 40 or dpi > 250:
        raise ValueError("DPI fuera del intervalo de seguridad 40-250")
    with fitz.open(archivo) as doc:
        estados = [analizar_pagina(page, dpi)[0] for page in doc]
        bloques = bloques_de_contenido(estados)
        nombres = []
        for n, (indices, dudoso) in enumerate(bloques, start=1):
            tipo = "revisar" if dudoso else "documentos"
            nombre = f"{archivo.stem}_bloque_{n:03d}.pdf"
            nombres.append((destino / tipo / nombre, indices))
        existentes = [p for p, _ in nombres if p.exists()]
        if existentes:
            raise FileExistsError(f"Hay {len(existentes)} salida(s) existentes; no se sobrescriben")
        for ruta, indices in nombres:
            ruta.parent.mkdir(parents=True, exist_ok=True)
            with fitz.open() as nuevo:
                for index in indices:
                    nuevo.insert_pdf(doc, from_page=index, to_page=index)
                nuevo.save(ruta)
    return {"estados": estados, "bloques": [str(ruta) for ruta, _ in nombres]}


def main():
    parser = argparse.ArgumentParser(description="Separador PDF con detector de paginas vacias")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    parser.add_argument("--dpi", type=int, default=100)
    args = parser.parse_args()
    resultado = procesar_pdf(args.pdf, args.output, args.dpi)
    for nombre in resultado["bloques"]:
        print(nombre)
    print("Clasificacion:", ", ".join(resultado["estados"]))


if __name__ == "__main__":
    main()
