"""Conciliación multiclave con fechas. Adaptación genérica sin esquemas empresariales."""
import argparse
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from portfolio_core.enrichment import process,autodetect_master


def main(argv=None):
    parser=argparse.ArgumentParser(description='Conciliación multiclave con fechas')
    parser.add_argument('--master',type=Path)
    parser.add_argument('--master-folder',type=Path)
    parser.add_argument('--reports',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args(argv)
    if False:
        if not args.master_folder:parser.error('Usa --master-folder')
        reference=autodetect_master(args.master_folder)
    else:
        if not args.master:parser.error('Usa --master')
        reference=args.master
    result=process(reference,args.reports,args.out,normalize_dates=True,multi_codes=True)
    for file,count in result.items():print(file,count)
    return result

if __name__=='__main__':main()
