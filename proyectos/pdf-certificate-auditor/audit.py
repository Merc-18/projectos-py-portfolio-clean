"""Read-only inventory of candidate certificate PDFs and unrelated files."""

import argparse
import csv
import os
from pathlib import Path
import re
import unicodedata

MAX_FILES = 10000


def normalized_name(name):
    text = unicodedata.normalize("NFKD", name.casefold())
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def is_certificate_pdf(filename):
    if not filename.lower().endswith(".pdf"):
        return False
    base = normalized_name(Path(filename).stem)
    return bool(re.search(r"certificad[oa]s?|certificacion(?:es)?|certificates?|\bcert\b", base))


def scan(root):
    folder = Path(root).resolve()
    if not folder.is_dir():
        raise ValueError("Input must be an existing directory")
    findings = []
    for current, dirs, files in os.walk(folder, followlinks=False):
        dirs[:] = sorted((name for name in dirs if not (Path(current) / name).is_symlink()), key=str.casefold)
        for filename in sorted(files, key=str.casefold):
            full = Path(current) / filename
            if full.is_symlink():
                continue
            candidate = is_certificate_pdf(filename)
            findings.append({"Relative Path": full.relative_to(folder).as_posix(),
                             "PDF": "YES" if filename.lower().endswith(".pdf") else "NO",
                             "Classification": "CERTIFICATE_CANDIDATE" if candidate else "MANUAL_REVIEW"})
            if len(findings) > MAX_FILES:
                raise ValueError(f"Too many files (limit {MAX_FILES})")
    return findings


def report(root, output, overwrite=False):
    target = Path(output).resolve()
    folder = Path(root).resolve()
    if target.suffix.lower() != ".csv":
        raise ValueError("Output must be .csv")
    if target == folder or target.is_relative_to(folder):
        raise ValueError("Output must be outside scanned directory to avoid recursive findings")
    if target.exists() and not overwrite:
        raise FileExistsError("Output exists; use --overwrite to replace it")
    findings = scan(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=["Relative Path", "PDF", "Classification"])
        writer.writeheader()
        for finding in findings:
            row = dict(finding)
            for key, value in row.items():
                if value.lstrip().startswith(("=", "+", "-", "@")):
                    row[key] = "'" + value
            writer.writerow(row)
    return findings


def main(argv=None):
    parser = argparse.ArgumentParser(description="Report certificate PDF candidates without deleting files")
    parser.add_argument("root", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)
    findings = report(args.root, args.output, args.overwrite)
    print(f"Audited {len(findings)} files; NO files deleted")


if __name__ == "__main__":
    main()
