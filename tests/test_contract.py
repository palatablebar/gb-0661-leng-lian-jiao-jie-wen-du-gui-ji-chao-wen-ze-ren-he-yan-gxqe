import pytest
from decimal import Decimal
from app.modules.contract.normalize import number,instant,celsius
from app.errors import RuleError

def test_fullwidth():
    """TRAP-06"""
    assert number('１,２３４.５')==Decimal('1234.5')

def test_missing():
    """TRAP-07"""
    with pytest.raises(RuleError) as e:number('N/A')
    assert e.value.code=='MISSING'

def test_timezone_equivalence():
    """TRAP-11"""
    assert instant('2026-11-02T09:00:00+08:00')==instant('2026-11-02T01:00:00Z')

def test_fahrenheit_correction():
    """TRAP-15"""
    assert celsius('41','F','.5')==Decimal('5.5')

def test_sample_contract(dirty):
    assert dirty['contract']['unit']=='°C';assert any(r['temperature']=='5.5' for r in dirty['contract']['rows'])

def test_probe_isolated(dirty):
    assert any(i['code']=='PROBE' for i in dirty['contract']['issues'])

def test_nonfinite_rejected():
    with pytest.raises(RuleError):number('NaN')
