def test_all_pages(client):
    for slug in ['intake','contract','model','calculate','quarantine','reconcile','batches']:
        r=client.get('/'+slug);assert r.status_code==200;assert '<nav>' in r.text;assert 'statusbar' in r.text

def test_all_module_trials(client):
    for slug in ['intake','contract','model','calculate','quarantine','reconcile']:
        assert client.post('/api/'+slug,json={'sample':'dirty'}).status_code==200

def test_export_matches(client):
    q=client.get('/api/quarantine').json();csv=client.get('/api/quarantine/export');assert csv.status_code==200;assert csv.text.count('\n')==q['total']+1

def test_empty_input(client):
    r=client.post('/api/runs',json={'csv_text':''});assert r.status_code==200;assert r.json()['intake']['state']=='EMPTY_FILE'
