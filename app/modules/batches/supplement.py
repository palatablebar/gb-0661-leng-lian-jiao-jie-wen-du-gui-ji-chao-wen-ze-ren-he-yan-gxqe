import hashlib,json,time
from datetime import datetime
from decimal import Decimal
from app.config import RULE_VERSION,SAMPLES
from app.errors import RuleError
from app.reasons import SENTINELS
from app.modules.contract.normalize import instant
from app.modules.model.intervals import span
from app.modules.model.service import partition
from app.modules.calculate.service import calculate
from app.modules.calculate.integral import fmt
from app.modules.reconcile.service import reconcile

FIELDS=('coverage','normal','excess','unknown','degree_minutes')

def _text(value,field):
    s=str(value or '').strip()
    if not s or s in SENTINELS:raise RuleError('SUPPLEMENT_EVIDENCE','补签缺少必要证据:'+field)
    return s

def _moment(value,field):
    try:return instant(_text(value,field)).isoformat()
    except RuleError as e:
        if e.code=='SUPPLEMENT_EVIDENCE':raise
        raise RuleError('SUPPLEMENT_EVIDENCE','补签缺少必要证据:'+field)

def validate(payload):
    if not isinstance(payload,dict):raise RuleError('SUPPLEMENT_EVIDENCE','补签内容必须为对象')
    supplement={f:_text(payload.get(f),f) for f in ('signature_id','shipment','owner')}
    refs=payload.get('evidence')
    refs=[str(r).strip() for r in refs if str(r).strip()] if isinstance(refs,list) else []
    if not refs:raise RuleError('SUPPLEMENT_EVIDENCE','补签缺少必要证据:evidence')
    supplement['evidence']=refs
    for f in ('start','end','signed_at'):supplement[f]=_moment(payload.get(f),f)
    try:span(supplement['start'],supplement['end'])
    except RuleError:raise RuleError('SUPPLEMENT_EVIDENCE','补签缺少必要证据:区间无效')
    return supplement

def merge(existing,supplement):
    s=datetime.fromisoformat(supplement['start']);e=datetime.fromisoformat(supplement['end'])
    kept=[]
    for h in existing:
        hs=datetime.fromisoformat(h['start']);he=datetime.fromisoformat(h['end'])
        if he<=s or hs>=e:kept.append(dict(h));continue
        if hs<s:kept.append({'start':hs.isoformat(),'end':s.isoformat(),'owner':h['owner']})
        if he>e:kept.append({'start':e.isoformat(),'end':he.isoformat(),'owner':h['owner']})
    kept.append({'start':s.isoformat(),'end':e.isoformat(),'owner':supplement['owner']})
    return sorted(kept,key=lambda h:h['start'])

def apply(bundle,supplement):
    handovers=bundle['model'].get('handovers') or json.loads((SAMPLES/'handovers.json').read_text(encoding='utf-8'))
    if supplement['shipment'] not in handovers:raise RuleError('SUPPLEMENT_EVIDENCE','补签缺少必要证据:shipment未登记')
    merged=dict(handovers);merged[supplement['shipment']]=merge(handovers[supplement['shipment']],supplement)
    params=bundle['manifest']['parameters']
    model=partition(bundle['contract']['rows'],merged,int(params['max_gap']))
    calc=calculate(model['segments'],params['threshold'])
    checked=reconcile(bundle['intake'],model,bundle['quarantine'],calc)
    if model['handover_issues']:raise RuleError('SUPPLEMENT_CONFLICT','补签导致交接责任冲突，保留当前正式账',409)
    if not checked['balanced']:raise RuleError('SUPPLEMENT_UNBALANCED','补签后对账不平，保留当前正式账',409)
    return {'manifest':_manifest(bundle,supplement,merged),'intake':bundle['intake'],'contract':bundle['contract'],'model':model,'calculate':calc,'quarantine':bundle['quarantine'],'reconcile':checked}

def _manifest(base,supplement,merged):
    canonical=json.dumps({'base':base['manifest']['run_id'],'supplement':supplement,'rule':RULE_VERSION},sort_keys=True,ensure_ascii=False)
    references=dict(base['manifest']['references'])
    references['handovers']=hashlib.sha256(json.dumps(merged,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {'run_id':hashlib.sha256(canonical.encode()).hexdigest()[:20],'sha256':base['manifest']['sha256'],'rule_version':RULE_VERSION,'parameters':base['manifest']['parameters'],'references':references,'created_at':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'base_run_id':base['manifest']['run_id'],'supplement_id':supplement['signature_id']}

def diff(before,after):
    def index(calc):return {(o['shipment'],o['owner']):o for o in calc['owners']}
    b=index(before);a=index(after);zero={f:'0' for f in FIELDS}
    rows=[]
    for ship,owner in sorted(set(b)|set(a)):
        x=b.get((ship,owner),zero);y=a.get((ship,owner),zero)
        delta={f:fmt(Decimal(y[f])-Decimal(x[f])) for f in FIELDS}
        rows.append({'shipment':ship,'owner':owner,'before':{f:x[f] for f in FIELDS},'after':{f:y[f] for f in FIELDS},'delta':delta,'changed':any(Decimal(v) for v in delta.values())})
    totals={'before':before['totals'],'after':after['totals'],'delta':{f:fmt(Decimal(after['totals'][f])-Decimal(before['totals'][f])) for f in FIELDS}}
    return {'rows':rows,'totals':totals}

def basis(base,supplement,manifest):
    return {'supplement':supplement,'base':{'run_id':base['manifest']['run_id'],'version':base.get('version',1),'reviewed':bool(base.get('reviewed'))},'rule_version':RULE_VERSION,'published_at':manifest['created_at']}
