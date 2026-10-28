import importlib.util
from pathlib import Path
import sys
from datetime import datetime
from openpyxl import Workbook,load_workbook
import pytest
ROOT=Path(__file__).resolve().parents[1]/'proyectos'
sys.path.insert(0,str(ROOT))
from portfolio_core import enrichment as engine


def workbook(path,cols,records):
    wb=Workbook();ws=wb.active;ws.append(cols)
    for row in records:ws.append(row)
    wb.save(path)


def build_fixture(tmp_path):
    master=tmp_path/'reference.xlsx'
    workbook(master,['Codigo','Grupo'],[['NODE001','G_A'],['NODE002','G_B']])
    reports=tmp_path/'reports';reports.mkdir()
    workbook(reports/'r.xlsx',['Codigo','Inicio','Hora inicio','Notas'],[
        ['NODE001',datetime(2026,4,15),'10:11:22','Registro ficticio'],
        ['NODE002|NODE001','2026-04-16','10:12','Otro'],['UNKNOWN','2026-01-01','13:20','=1+1']])
    from openpyxl import load_workbook
    book=load_workbook(reports/'r.xlsx')
    book.active['D4'].data_type='s'  # Emulate incoming untrusted text, not a formula
    book.save(reports/'r.xlsx')
    return master,reports


def load_wrapper(name):
    p=ROOT/'Área Q'/name/'run.py';spec=importlib.util.spec_from_file_location(name.replace('-',''),p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_base_mapping(tmp_path):
    master,reports=build_fixture(tmp_path)
    output=tmp_path/'results'
    summary=engine.process(master,reports,output)
    assert summary['r.xlsx']=={'ASIGNADO':1,'SIN_MAPEO':2,'AMBIGUO':0}
    wb=load_workbook(output/'r_result.xlsx')
    header=[c.value for c in wb.active[1]]
    assert 'Grupo asignado' in header
    assert wb.active.cell(row=4,column=header.index('Notas')+1).data_type!='f'
    assert wb.active.cell(row=4,column=header.index('Notas')+1).value=="'=1+1"


def test_variant_dates(tmp_path):
    master,reports=build_fixture(tmp_path)
    output=tmp_path/'results'
    counts=engine.process(master,reports,output,normalize_dates=True)
    ws=load_workbook(output/'r_result.xlsx',data_only=True).active
    assert ws['B2'].value=='15/04/2026'
    assert ws['C3'].value=='10:12:00'
    assert counts['r.xlsx']['ASIGNADO']==1


def test_multicode_ambiguity(tmp_path):
    master,reports=build_fixture(tmp_path)
    output=tmp_path/'out';stats=engine.process(master,reports,output,multi_codes=True)
    assert stats['r.xlsx']['AMBIGUO']==1
    assert stats['r.xlsx']['ASIGNADO']==1


def test_autodetect_master(tmp_path):
    master,reports=build_fixture(tmp_path)
    assert engine.autodetect_master(tmp_path)==master
    workbook(tmp_path/'other.xlsx',['Codigo','Grupo'],[['X','Y']])
    with pytest.raises(ValueError):engine.autodetect_master(tmp_path)


def test_all_four_ticket_wrappers(tmp_path):
    for name in ['Q-001','Q-005','Q-006','Q-011']:
        wd=tmp_path/name;wd.mkdir()
        master,reports=build_fixture(wd)
        cmd=['--reports',str(reports),'--out',str(wd/'out')]
        if name=='Q-011':
            masters=wd/'refs';masters.mkdir();master.rename(masters/'master.xlsx');cmd+=['--master-folder',str(masters)]
        else:cmd+=['--master',str(master)]
        result=load_wrapper(name).main(cmd)
        assert result['r.xlsx']['ASIGNADO']>=1


def test_duplicate_reference_rejected(tmp_path):
    master=tmp_path/'map.xlsx'
    workbook(master,['Codigo','Grupo'],[['A','G1'],['a','G2']])
    with pytest.raises(ValueError):engine.load_map(master)


def test_empty_reference_rejected(tmp_path):
    p=tmp_path/'map.xlsx';workbook(p,['Codigo','Grupo'],[['','']])
    with pytest.raises(ValueError):engine.load_map(p)


def test_output_overwrite_refused(tmp_path):
    master,reports=build_fixture(tmp_path)
    out=tmp_path/'out';engine.process(master,reports,out)
    with pytest.raises(FileExistsError):engine.process(master,reports,out)


def test_output_nesting_rejected(tmp_path):
    master,reports=build_fixture(tmp_path)
    with pytest.raises(ValueError):engine.process(master,reports,reports/'out')


def test_format_temporal_invalid():
    assert engine.format_temporal('unknown','date')=='unknown'
    assert engine.format_temporal('16/04/2026','date')=='16/04/2026'
