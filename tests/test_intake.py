import pytest
from app.modules.intake.reader import read
from app.pipeline import sample_bytes
from app.errors import RuleError

def test_bom_sample():
    """TRAP-02"""
    r=read(sample_bytes());assert r['rows'][0]['shipment']=='00001';assert r['input']==58

def test_legacy_encoding():
    """TRAP-01"""
    r=read(sample_bytes('gb18030'));assert r['encoding']=='gb18030';assert r['rows'][-1]['shipment']=='00007'

def test_source_lines():
    r=read(sample_bytes());assert r['rows'][0]['line']==2;assert r['rows'][2]['line']==4

def test_column_isolation():
    r=read(sample_bytes());assert r['issues'][0]['code']=='COLUMN_COUNT';assert r['blank']==1

def test_empty_states():
    assert read(b'')['state']=='EMPTY_FILE';assert read(b'shipment,probe,at,value,unit\n')['state']=='HEADER_ONLY'

def test_quoted_newline():
    r=read(b'shipment,probe,at,value,unit\n00001,P1,"2026-11-02\n09:00",4,C\n');assert len(r['rows'])==1;assert r['rows'][0]['line']==3

def test_truncated():
    with pytest.raises(RuleError,match='引号'):read(b'shipment,probe,at,value,unit\n"00001,')
