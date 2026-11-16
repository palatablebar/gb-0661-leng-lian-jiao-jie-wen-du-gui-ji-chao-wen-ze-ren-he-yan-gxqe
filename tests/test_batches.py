from app import store
from app.pipeline import execute,sample_bytes

def test_seed_idempotent(client):
    first=client.post('/api/runs',json={}).json();second=client.post('/api/runs',json={}).json();assert first['manifest']['run_id']==second['manifest']['run_id'];assert len(store.history())==1

def test_parameter_new_key(client):
    a=client.post('/api/runs',json={}).json();b=client.post('/api/runs',json={'threshold':'9'}).json();assert a['manifest']['run_id']!=b['manifest']['run_id'];assert len(store.history())==2

def test_optimistic_review(client):
    """TRAP-26"""
    b=store.latest();payload={'run_id':b['manifest']['run_id'],'version':b['version']}
    assert client.post('/api/batches/review',json=payload).status_code==200;assert client.post('/api/batches/review',json=payload).status_code==409

def test_manifest_has_digest(dirty):
    assert len(dirty['manifest']['sha256'])==64;assert dirty['manifest']['parameters']['max_gap']==15

def test_persist_reopen(client):
    rid=store.latest()['manifest']['run_id'];store.connect().close();assert store.latest()['manifest']['run_id']==rid

def test_failed_import_atomic(client):
    count=len(store.history());assert client.post('/api/runs',json={'csv_text':'invalid'}).status_code==422;assert len(store.history())==count

def test_unknown_sample(client):
    assert client.post('/api/runs',json={'sample':'../secret'}).status_code==404
