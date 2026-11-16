import os,sqlite3,json
from pathlib import Path
from app.errors import RuleError
def connect():
    path=os.environ.get('DB_PATH','/tmp/coldchain.sqlite3')
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    con=sqlite3.connect(path,timeout=15);con.row_factory=sqlite3.Row
    con.execute('CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, payload TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 1, reviewed INTEGER NOT NULL DEFAULT 0, created TEXT NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS supplements(key TEXT PRIMARY KEY, payload TEXT NOT NULL, created TEXT NOT NULL)')
    con.execute('CREATE TABLE IF NOT EXISTS ledgers(id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL UNIQUE, base_run_id TEXT NOT NULL, supplement_key TEXT NOT NULL UNIQUE, basis TEXT NOT NULL, diff TEXT NOT NULL, created TEXT NOT NULL)')
    return con

def save(bundle):
    rid=bundle['manifest']['run_id']
    with connect() as c:
        c.execute('INSERT OR IGNORE INTO runs(id,payload,created) VALUES(?,?,?)',(rid,json.dumps(bundle,ensure_ascii=False),bundle['manifest']['created_at']))
        row=c.execute('SELECT * FROM runs WHERE id=?',(rid,)).fetchone()
    out=json.loads(row['payload']);out['version']=row['version'];out['reviewed']=bool(row['reviewed'])
    return out

def latest():
    with connect() as c: row=c.execute('SELECT * FROM runs ORDER BY rowid DESC LIMIT 1').fetchone()
    if not row:return None
    out=json.loads(row['payload']);out['version']=row['version'];out['reviewed']=bool(row['reviewed']);return out

def history():
    with connect() as c: rows=c.execute('SELECT id,version,reviewed,created FROM runs ORDER BY rowid DESC').fetchall()
    return [dict(r) for r in rows]

def review(rid,version):
    with connect() as c:
        cur=c.execute('UPDATE runs SET version=version+1,reviewed=1 WHERE id=? AND version=?',(rid,version))
        if cur.rowcount!=1:raise RuleError('STALE','记录已变更，请刷新后复核',409)
    return {'run_id':rid,'version':version+1,'reviewed':True}

def get(rid):
    with connect() as c:row=c.execute('SELECT * FROM runs WHERE id=?',(rid,)).fetchone()
    if not row:return None
    out=json.loads(row['payload']);out['version']=row['version'];out['reviewed']=bool(row['reviewed']);return out

def ledgers():
    with connect() as c:rows=c.execute('SELECT * FROM ledgers ORDER BY id DESC').fetchall()
    return [{'id':r['id'],'run_id':r['run_id'],'base_run_id':r['base_run_id'],'supplement_key':r['supplement_key'],'created':r['created'],'basis':json.loads(r['basis']),'diff':json.loads(r['diff'])} for r in rows]

def publish(base,new_bundle,supplement,diff_result,basis):
    key=supplement['signature_id'];created=new_bundle['manifest']['created_at']
    try:
        with connect() as c:
            c.execute('INSERT INTO supplements(key,payload,created) VALUES(?,?,?)',(key,json.dumps(supplement,ensure_ascii=False),created))
            c.execute('INSERT OR IGNORE INTO runs(id,payload,created) VALUES(?,?,?)',(new_bundle['manifest']['run_id'],json.dumps(new_bundle,ensure_ascii=False),created))
            c.execute('INSERT INTO ledgers(run_id,base_run_id,supplement_key,basis,diff,created) VALUES(?,?,?,?,?,?)',(new_bundle['manifest']['run_id'],base['manifest']['run_id'],key,json.dumps(basis,ensure_ascii=False),json.dumps(diff_result,ensure_ascii=False),created))
        return {'run_id':new_bundle['manifest']['run_id'],'replayed':False,'basis':basis,'diff':diff_result}
    except sqlite3.IntegrityError:
        with connect() as c:
            srow=c.execute('SELECT payload FROM supplements WHERE key=?',(key,)).fetchone()
            ledger=c.execute('SELECT * FROM ledgers WHERE supplement_key=?',(key,)).fetchone()
        if srow is None or ledger is None:raise RuleError('PUBLISH','发布失败，已恢复旧版正式账',500)
        if json.loads(srow['payload'])!=supplement:raise RuleError('SUPPLEMENT_CONFLICT','同一签号的补签内容不一致，保留当前正式账',409)
        return {'run_id':ledger['run_id'],'replayed':True,'basis':json.loads(ledger['basis']),'diff':json.loads(ledger['diff'])}
    except sqlite3.Error:
        raise RuleError('PUBLISH','发布失败，已恢复旧版正式账',500)
