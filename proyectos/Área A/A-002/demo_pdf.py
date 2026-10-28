"""Marcado de PDF de ejemplo — posición inferior derecha. Nunca inserta firmas reales."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from portfolio_core.pdf_demo_mark import mark_demo


def main(argv=None):
    p=argparse.ArgumentParser(description="Marcado de PDF DEMO, sin firmas")
    p.add_argument("input",type=Path);p.add_argument("output",type=Path)
    a=p.parse_args(argv)
    print("Páginas marcadas:",mark_demo(a.input,a.output,'lower-right'))

if __name__=="__main__":main()
