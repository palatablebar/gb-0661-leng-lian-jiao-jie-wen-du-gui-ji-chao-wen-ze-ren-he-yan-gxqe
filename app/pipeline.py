import json,hashlib,time
from app.config import SAMPLES,MAX_BYTES
from app.errors import RuleError
from app.manifest import make_manifest
from app.modules.intake.service import ingest
from app.modules.contract.service import normalize
from app.modules.model.service import partition
from app.modules.calculate.service import calculate
from app.modules.quarantine.service import quarantine
from app.modules.reconcile.service import reconcile

def execute(raw,threshold='8',max_gap=15):
    from app.modules.contract.normalize import number
    limit=number(threshold)
    if limit < -80 or limit > 80 or not 1<=max_gap<=120:raise RuleError('PARAMETER','阈值或缺测分钟超出范围')
    started=time.perf_counter();calraw=(SAMPLES/'calibrations.json').read_bytes();handraw=(SAMPLES/'handovers.json').read_bytes()
    calibration=json.loads(calraw);handovers=json.loads(handraw)
    intake=ingest(raw);contract=normalize(intake['rows'],calibration,handovers)
    model=partition(contract['rows'],handovers,max_gap);calc=calculate(model['segments'],str(limit))
    isolated=quarantine(intake['issues'],contract['issues'],model['issues'])
    checked=reconcile(intake,model,isolated,calc)
    manifest=make_manifest(raw,{'threshold':str(limit),'max_gap':max_gap},{'calibrations':hashlib.sha256(calraw).hexdigest(),'handovers':hashlib.sha256(handraw).hexdigest()})
    manifest['elapsed_ms']=round((time.perf_counter()-started)*1000,3)
    return {'manifest':manifest,'intake':intake,'contract':contract,'model':model,'calculate':calc,'quarantine':isolated,'reconcile':checked}

def sample_bytes(name='dirty'):
    if name not in ('dirty','clean','gb18030'):raise RuleError('SAMPLE','样例不存在',404)
    return (SAMPLES/(name+'.csv')).read_bytes()
