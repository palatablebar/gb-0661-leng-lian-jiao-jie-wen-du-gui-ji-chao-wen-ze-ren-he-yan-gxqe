from app import store

def payload(**over):
    base={'signature_id':'SIG-2026-0001','shipment':'00001','owner':'滨江仓储','start':'2026-11-02T09:20:00+08:00','end':'2026-11-02T10:00:00+08:00','signed_at':'2026-11-02T10:05:00+08:00','evidence':['POD-00001.jpg','签收单A-778']}
    base.update(over);return base

def test_supplement_publish(client):
    before=store.latest();rid=before['manifest']['run_id']
    r=client.post('/api/batches/supplement',json=payload())
    assert r.status_code==200;r=r.json()
    assert r['replayed'] is False and r['run_id']!=rid
    rows={(x['shipment'],x['owner']):x for x in r['diff']['rows']}
    assert rows[('00001','北岸冷运')]['delta']['coverage']=='-10.000000'
    assert rows[('00001','滨江仓储')]['delta']['coverage']=='10.000000'
    assert r['diff']['totals']['delta']['degree_minutes']=='0.000000'
    assert r['basis']['supplement']['signature_id']=='SIG-2026-0001'
    assert r['basis']['base']['run_id']==rid
    latest=store.latest()
    assert latest['manifest']['run_id']==r['run_id']
    assert latest['manifest']['base_run_id']==rid

def test_supplement_idempotent(client):
    first=client.post('/api/batches/supplement',json=payload()).json()
    runs=len(store.history())
    second=client.post('/api/batches/supplement',json=payload())
    assert second.status_code==200;second=second.json()
    assert second['replayed'] is True and second['run_id']==first['run_id']
    assert len(store.history())==runs and len(store.ledgers())==1

def test_supplement_same_key_conflict(client):
    client.post('/api/batches/supplement',json=payload())
    r=client.post('/api/batches/supplement',json=payload(owner='北岸冷运'))
    assert r.status_code==409 and r.json()['code']=='SUPPLEMENT_CONFLICT'
    assert len(store.ledgers())==1

def test_supplement_missing_evidence(client):
    rid=store.latest()['manifest']['run_id']
    for bad in [payload(evidence=[]),payload(signature_id=''),payload(start='2026-11-02 09:20'),payload(end='2026-11-02T09:00:00+08:00'),payload(shipment='99999')]:
        r=client.post('/api/batches/supplement',json=bad)
        assert r.status_code==422 and r.json()['code']=='SUPPLEMENT_EVIDENCE'
    assert store.ledgers()==[] and store.latest()['manifest']['run_id']==rid

def test_supplement_preserves_evidence_and_old_conclusion(client):
    base=store.latest();rid=base['manifest']['run_id']
    assert client.post('/api/batches/review',json={'run_id':rid,'version':base['version']}).status_code==200
    client.post('/api/batches/supplement',json=payload())
    new=store.latest()
    assert new['intake']==base['intake'] and new['contract']==base['contract'] and new['quarantine']==base['quarantine']
    old=client.get('/api/batches/'+rid).json()
    assert old['reviewed'] is True
    assert old['calculate']['owners']==base['calculate']['owners']
    assert old['reconcile']['conclusion']==base['reconcile']['conclusion']

def test_ledgers_chain(client):
    rid=store.latest()['manifest']['run_id']
    first=client.post('/api/batches/supplement',json=payload()).json()
    second=client.post('/api/batches/supplement',json=payload(signature_id='SIG-2026-0002',shipment='00002')).json()
    assert second['replayed'] is False
    assert store.latest()['manifest']['base_run_id']==first['run_id']
    ledgers=client.get('/api/batches/ledgers').json()
    assert len(ledgers)==2 and ledgers[-1]['base_run_id']==rid
    assert client.get('/api/batches/nope').status_code==404
