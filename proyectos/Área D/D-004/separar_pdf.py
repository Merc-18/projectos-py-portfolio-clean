"""Separador de PDF, adaptado de un desarrollo previo para uso independiente.

Trabaja exclusivamente con archivos proporcionados por el usuario. No modifica
la fuente, no sobrescribe resultados y no necesita red ni datos de empresas.
"""
from pathlib import Path
import argparse

import fitz


def separar_pdf(archivo: Path, salida: Path) -> list[Path]:
    """Crea un PDF por pagina y retorna las rutas generadas."""
    archivo, salida = Path(archivo).resolve(), Path(salida).resolve()
    if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
        raise ValueError("La entrada debe ser un PDF existente")
    if salida == archivo.parent:
        raise ValueError("Separe la salida de la carpeta del documento de entrada")
    with fitz.open(archivo) as doc:
        paginas = len(doc)
        if paginas == 0:
            return []
        ancho = max(3, len(str(paginas)))
        destinos = [salida / f"{archivo.stem}_pag_{i:0{ancho}d}.pdf"
                    for i in range(1, paginas + 1)]
        ocupados = [p for p in destinos if p.exists()]
        if ocupados:
            raise FileExistsError(f"La salida ya contiene {len(ocupados)} archivo(s) de resultado")
        salida.mkdir(parents=True, exist_ok=True)
        for i, destino in enumerate(destinos):
            with fitz.open() as nuevo_doc:
                nuevo_doc.insert_pdf(doc, from_page=i, to_page=i)
                nuevo_doc.save(destino)
    return destinos


def main():
    parser = argparse.ArgumentParser(description="Separar archivos PDF sin alterar originales")
    parser.add_argument("pdf", type=Path, help="Archivo PDF de entrada")
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    for archivo in separar_pdf(args.pdf, args.output):
        print(archivo)


if __name__ == "__main__":
    main()
