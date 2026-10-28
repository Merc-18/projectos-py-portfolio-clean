"""Compare the visual similarity of the lower part of PDF last pages.

Portable adaptation of the original PDF pHash comparison process. It does NOT
validate handwriting, legal signatures, identities or document authenticity.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.fft import dctn


def common_prefix_length(a: str, b: str) -> int:
    return next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))


def find_pairs(folder: Path, *, minimum_prefix: int = 10):
    """Consecutive pairs like the original, but reject ambiguous groups of 3+."""
    if minimum_prefix < 1:
        raise ValueError("minimum_prefix must be >= 1")
    pdfs = sorted((p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"),
                  key=lambda p: p.name.casefold())
    pairs, unused = [], []
    start = 0
    while start < len(pdfs):
        end = start + 1
        while end < len(pdfs) and common_prefix_length(
            pdfs[start].stem, pdfs[end].stem
        ) >= minimum_prefix:
            end += 1
        group = pdfs[start:end]
        if len(group) == 2:
            pairs.append((group[0], group[1]))
        else:
            unused.extend(group)
        start = end
    return pairs, unused


def perceptual_hash(pdf_file: Path, *, dpi: int = 80) -> int:
    """64-bit pHash of the bottom third of the final page, including DC exclusion."""
    if dpi < 40 or dpi > 300:
        raise ValueError("dpi must be between 40 and 300")
    with fitz.open(pdf_file) as doc:
        if not doc.page_count:
            raise ValueError("PDF has no pages")
        page = doc[-1]
        pixelmap = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
        image = Image.frombytes("RGB", (pixelmap.width, pixelmap.height), pixelmap.samples)
        width, height = image.size
        image = image.crop((0, int(height * 2 / 3), width, height)).convert("L")
        image = image.resize((32, 32), Image.Resampling.LANCZOS)
    dct = dctn(np.asarray(image, dtype=np.float32), type=2, norm="ortho")[:8, :8]
    median = float(np.median(dct.flatten()[1:]))
    bits = (dct > median).flatten()
    n = 0
    for bit in bits:
        n = (n << 1) | int(bit)
    return n


def hash_distance(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def csv_text(value: str) -> str:
    raw = str(value)
    return "'" + raw if raw.lstrip().startswith(("=", "+", "-", "@")) else raw


def compare_pairs(pairs):
    rows = []
    for one, two in pairs:
        h1 = perceptual_hash(one)
        h2 = perceptual_hash(two)
        rows.append({"Archivo_A": one.name, "Archivo_B": two.name,
                     "Distancia_pHash": hash_distance(h1, h2)})
    return rows


def report(rows: list[dict], destination: Path, *, overwrite: bool = False):
    """Generate summary CSV and chart from synthetic/authorized PDF pairs."""
    if not rows:
        raise ValueError("No PDF pairs to compare")
    destination = destination.resolve()
    csv_path, plot_path = destination / "distancias.csv", destination / "distribucion.png"
    if not overwrite and (csv_path.exists() or plot_path.exists()):
        raise FileExistsError("Output report exists; use --overwrite")
    destination.mkdir(parents=True, exist_ok=True)
    distances = np.array([r["Distancia_pHash"] for r in rows], dtype=float)
    threshold95 = int(np.ceil(np.percentile(distances, 95)))
    threshold99 = int(np.ceil(np.percentile(distances, 99)))
    with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=("Archivo_A", "Archivo_B", "Distancia_pHash"))
        writer.writeheader()
        writer.writerows({k: csv_text(v) if k != "Distancia_pHash" else v for k, v in row.items()} for row in rows)
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.hist(distances, bins=min(max(len(rows), 1), 15), edgecolor="white")
    ax.axvline(threshold95, linestyle="--", label=f"P95: {threshold95}")
    ax.axvline(threshold99, linestyle=":", label=f"P99: {threshold99}")
    ax.set(title="Diferencias visuales (pHash)", xlabel="Distancia Hamming (0 a 64)", ylabel="Pares")
    ax.legend()
    fig.tight_layout()
    fig.savefig(plot_path, dpi=120)
    plt.close(fig)
    return {"csv": csv_path, "chart": plot_path, "p95": threshold95, "p99": threshold99}


def main():
    parser = argparse.ArgumentParser(description="PDF pHash offline; solo similitud visual, no autenticidad")
    parser.add_argument("input_folder", type=Path)
    parser.add_argument("output_folder", type=Path)
    parser.add_argument("--prefix-length", type=int, default=10)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not args.input_folder.is_dir():
        parser.error("El directorio de entrada no existe")
    pairs, unused = find_pairs(args.input_folder, minimum_prefix=args.prefix_length)
    print(f"Pares: {len(pairs)}; sin pareja o ambiguos: {len(unused)}")
    result = report(compare_pairs(pairs), args.output_folder, overwrite=args.overwrite)
    print(f"CSV: {result['csv']} | Gráfico: {result['chart']}")


if __name__ == "__main__":
    main()
