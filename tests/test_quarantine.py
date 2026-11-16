from app.modules.quarantine.rules import summarize
from app.modules.quarantine.service import evidence_csv

def test_codes(dirty):
    assert dirty['quarantine']['counts']['CONFLICT']==2

def test_filter(dirty):
    r=summarize(dirty['quarantine']['rows'],'CONFLICT');assert r['selected']==2;assert r['total']==dirty['quarantine']['total']

def test_reason_present(dirty):
    assert all(r['reason'] and r['line']>0 for r in dirty['quarantine']['rows'])

def test_raw_preserved(dirty):
    assert any(i['raw'].get('value')=='wrong' for i in dirty['quarantine']['rows'] if isinstance(i['raw'],dict))

def test_csv_headers(dirty):
    assert evidence_csv(dirty['quarantine']['rows']).startswith('\ufeffline,code,reason,raw')

def test_clean_empty(clean):
    assert clean['quarantine']['total']==0;assert evidence_csv([]).count('\n')==1

def test_counts_conserve(dirty):
    assert sum(dirty['quarantine']['counts'].values())==dirty['quarantine']['total']
