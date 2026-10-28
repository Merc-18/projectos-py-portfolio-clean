"""Consolidar series Excel contenidas en ZIP mediante claves compartidas.

Adaptacion funcional del flujo original: leer hojas por periodo, unir
horizontalmente indicadores y concatenar verticalmente los periodos.
"""
from collections import defaultdict
from io import BytesIO
from pathlib import Path
import argparse
import zipfile

import pandas as pd

# Etiquetas tecnicas neutras. Para nuevos indicadores modifique esta tabla.
ARCHIVOS_HOJAS = {
    "serie_a.xlsx": "SERIE_A",
    "serie_b.xlsx": "SERIE_B",
    "serie_c.xlsx": "SERIE_C",
}
COLUMNAS_CLAVE = ["ID", "PERIODO"]
MAX_FILE_SIZE = 20 * 1024 * 1024


def leer_excel(contenido_bytes: bytes, hoja: str) -> pd.DataFrame:
    df = pd.read_excel(BytesIO(contenido_bytes), sheet_name=hoja, engine="openpyxl", header=0)
    df = df[[c for c in df.columns if isinstance(c, str) and not c.startswith("Nota")]]
    return df.dropna(how="all")


def consolidar_zip(ruta_zip: Path, salida: Path, archivos_hojas=None, claves=None) -> pd.DataFrame:
    ruta_zip, salida = Path(ruta_zip).resolve(), Path(salida).resolve()
    if ruta_zip.suffix.lower() != ".zip" or not ruta_zip.is_file():
        raise ValueError("Se requiere un archivo ZIP existente")
    if salida.suffix.lower() != ".xlsx":
        raise ValueError("La salida debe ser Excel .xlsx")
    if salida.exists():
        raise FileExistsError("La salida ya existe y no se sobreescribe")
    archivos_hojas = archivos_hojas or ARCHIVOS_HOJAS
    claves = claves or COLUMNAS_CLAVE
    por_tipo = defaultdict(list)
    with zipfile.ZipFile(ruta_zip) as z:
        for info in z.infolist():
            # Los nombres pueden repetirse en carpetas de periodos; solo leer
            # archivos esperados. No se extraen rutas a disco.
            nombre = Path(info.filename).name
            if nombre in archivos_hojas:
                if info.file_size > MAX_FILE_SIZE:
                    raise ValueError("Archivo de Excel demasiado grande en ZIP")
                por_tipo[nombre].append((info.filename, z.read(info)))
    if set(por_tipo) != set(archivos_hojas):
        raise ValueError("Faltan archivos de indicador requeridos")
    tamaños = {len(x) for x in por_tipo.values()}
    if len(tamaños) != 1 or not tamaños or 0 in tamaños:
        raise ValueError("Todos los indicadores deben tener la misma cantidad de periodos")
    for datos in por_tipo.values():
        datos.sort(key=lambda pair: pair[0])
    periodos = []
    for i in range(next(iter(tamaños))):
        base = None
        for nombre, hoja in archivos_hojas.items():
            df = leer_excel(por_tipo[nombre][i][1], hoja)
            faltantes = set(claves) - set(df.columns)
            if faltantes:
                raise ValueError(f"Columnas clave ausentes: {sorted(faltantes)}")
            metricas = [c for c in df.columns if c not in claves]
            df = df[claves + metricas].rename(
                columns={c: f"{hoja.replace(' ', '_')}_{c}" for c in metricas}
            )
            base = df if base is None else pd.merge(base, df, on=claves, how="outer")
        periodos.append(base)
    result = pd.concat(periodos, ignore_index=True)
    # Evitar que un valor de una fuente de datos se interprete como formula.
    for col in result.select_dtypes(include=["object"]).columns:
        result[col] = result[col].map(
            lambda v: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v
        )
    salida.parent.mkdir(parents=True, exist_ok=True)
    result.to_excel(salida, index=False)
    return result


def main():
    parser = argparse.ArgumentParser(description="Consolidacion horizontal y vertical de indicadores Excel")
    parser.add_argument("zip", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    df = consolidar_zip(args.zip, args.output)
    print(f"Consolidado: {len(df)} filas y {len(df.columns)} columnas")


if __name__ == "__main__":
    main()
