"""Clasificar y copiar PDF por tipo y periodo; adaptado de utilidad previa.

Conserva busqueda recursiva, deteccion de mes y sufijos anticolision.
Nombres de categorias y carpetas son ficticios e independientes del origen.
"""
from pathlib import Path
import argparse
import shutil

MESES = ("ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", "JULIO", "AGOSTO",
         "SETIEMBRE", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE")
CATEGORIAS = ("TIPO_A", "TIPO_B")


def extraer_mes(carpeta: Path) -> str:
    nombre = Path(carpeta).name.upper()
    return next((mes for mes in MESES if mes in nombre), "SIN_MES")


def destino_disponible(ruta: Path, salida: Path, mes: str, ocupados: set[Path]) -> Path:
    stem, ext = ruta.stem, ruta.suffix
    destino = salida / f"{stem}_{mes}{ext}"
    contador = 1
    while destino in ocupados or destino.exists():
        destino = salida / f"{stem}_{mes}_{contador}{ext}"
        contador += 1
    ocupados.add(destino)
    return destino


def plan_copias(entrada: Path, salida: Path) -> list[tuple[Path, Path]]:
    entrada, salida = Path(entrada).resolve(), Path(salida).resolve()
    if not entrada.is_dir():
        raise ValueError("La carpeta raiz no existe")
    if entrada == salida or entrada in salida.parents or salida in entrada.parents:
        raise ValueError("La carpeta de salida debe ser independiente de la entrada")
    plan, ocupados = [], set()
    for mes_carpeta in sorted((x for x in entrada.iterdir() if x.is_dir())):
        mes = extraer_mes(mes_carpeta)
        for carpeta in sorted(mes_carpeta.rglob("DOCUMENTOS")):
            if not carpeta.is_dir():
                continue
            for archivo in sorted(carpeta.rglob("*")):
                if not archivo.is_file() or archivo.suffix.lower() != ".pdf":
                    continue
                nombre = archivo.name.upper()
                categoria = next((cat for cat in CATEGORIAS if cat in nombre), None)
                if categoria is None:
                    continue
                target = destino_disponible(archivo, salida / categoria, mes, ocupados)
                plan.append((archivo, target))
    return plan


def copiar_documentos(entrada: Path, salida: Path, ejecutar=False) -> list[tuple[Path, Path]]:
    plan = plan_copias(entrada, salida)
    if ejecutar:
        for origen, destino in plan:
            destino.parent.mkdir(parents=True, exist_ok=True)
            if destino.exists():
                raise FileExistsError(f"El destino ya existe: {destino}")
            shutil.copy2(origen, destino)
    return plan


def main():
    parser = argparse.ArgumentParser(description="Copiador PDF seguro por categorias ficticias")
    parser.add_argument("entrada", type=Path)
    parser.add_argument("salida", type=Path)
    parser.add_argument("--execute", action="store_true", help="Copiar archivos; por defecto solo planificar")
    args = parser.parse_args()
    plan = copiar_documentos(args.entrada, args.salida, ejecutar=args.execute)
    for origen, destino in plan:
        print(f"{origen.name} -> {destino}")
    print(f"Total: {len(plan)} | Modo: {'COPIA' if args.execute else 'SIMULACION'}")


if __name__ == "__main__":
    main()
