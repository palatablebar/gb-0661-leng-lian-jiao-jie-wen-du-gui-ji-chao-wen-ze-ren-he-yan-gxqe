from decimal import Decimal
from copy import deepcopy
from app.modules.reconcile.compare import compare

def test_row_balance(dirty):
    r=dirty['reconcile'];assert r['input']==r['output']+r['isolated']+r['blank'];assert r['balanced']

def test_minute_balance(clean):
    t=clean['calculate']['totals'];assert abs(Decimal(t['coverage'])-sum(Decimal(t[k]) for k in ['normal','excess','unknown']))<Decimal('.00001')

def test_integral_owners(clean):
    assert abs(Decimal(clean['reconcile']['degree_delta']))<Decimal('.00001')

def test_bad_ledger_detected(dirty):
    intake=deepcopy(dirty['intake']);intake['input']+=1
    r=compare(intake,dirty['model'],dirty['quarantine'],dirty['calculate']);assert not r['balanced'];assert r['row_delta']==1

def test_missing_measurement_conclusion(clean):
    assert clean['reconcile']['conclusion']=='待补测'

def test_clean_counts(clean):
    assert clean['reconcile']['output']==48;assert clean['reconcile']['isolated']==0

def test_dirty_differs(clean,dirty):
    assert clean['calculate']['totals']!=dirty['calculate']['totals'];assert dirty['reconcile']['isolated']>0
