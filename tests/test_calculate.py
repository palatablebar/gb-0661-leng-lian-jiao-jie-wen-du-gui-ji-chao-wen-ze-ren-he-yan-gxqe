from decimal import Decimal
from app.modules.calculate.integral import excess

def test_crossing_counterexample():
    over,area=excess('5','12','10','8');assert abs(over-Decimal(40)/7)<Decimal('1e-20');assert area==over*2

def test_flat_above():
    assert excess('12','12','10','8')==(Decimal(10),Decimal(40))

def test_below():
    assert excess('2','5','10','8')==(Decimal(0),Decimal(0))

def test_at_boundary():
    assert excess('8','8','10','8')==(Decimal(0),Decimal(0))

def test_integral_clean(clean):
    assert clean['calculate']['totals']['degree_minutes']=='491.428571';assert clean['calculate']['totals']['unknown']=='160.000000'

def test_owner_split(clean):
    owners=clean['calculate']['owners'];assert owners[0]['owner']=='北岸冷运';assert owners[1]['degree_minutes']=='10.000000'

def test_sample_coverage(clean):
    assert clean['calculate']['totals']['coverage']=='480.000000';assert len(clean['calculate']['owners'])==16
