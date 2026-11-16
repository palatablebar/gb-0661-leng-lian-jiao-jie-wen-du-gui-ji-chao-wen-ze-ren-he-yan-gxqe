from copy import deepcopy
from app.modules.model.service import partition
from app.modules.model.intervals import owner_at
from datetime import datetime

def test_dedup(dirty):
    assert sum(i['code']=='DUPLICATE' for i in dirty['model']['issues'])==1

def test_conflict_all_isolated(dirty):
    """TRAP-14"""
    assert sum(i['code']=='CONFLICT' for i in dirty['model']['issues'])==2

def test_late_kept(dirty):
    """TRAP-13"""
    assert dirty['model']['late_count']>=1;assert any(r['temperature']=='5.5' for r in dirty['model']['rows'])

def test_half_open_owner():
    """TRAP-23"""
    hs=[{'start':'2026-01-01T09:00:00+00:00','end':'2026-01-01T09:30:00+00:00','owner':'甲'},{'start':'2026-01-01T09:30:00+00:00','end':'2026-01-01T10:00:00+00:00','owner':'乙'}]
    assert owner_at(datetime.fromisoformat('2026-01-01T09:30:00+00:00'),hs)=='乙'

def test_gap_unknown(clean):
    assert len([s for s in clean['model']['segments'] if s['left'] is None])==8

def test_owner_overlap():
    hs={'00001':[{'start':'2026-01-01T00:00:00+00:00','end':'2026-01-01T01:00:00+00:00','owner':'甲'},{'start':'2026-01-01T00:30:00+00:00','end':'2026-01-01T01:30:00+00:00','owner':'乙'}]}
    r=partition([],hs);assert r['handover_issues'][0]['code']=='HANDOVER_OVERLAP'

def test_no_duplicate_segments(clean):
    segments=clean['model']['segments'];assert len(segments)==40;assert len(set((s['shipment'],s['start']) for s in segments))==40
