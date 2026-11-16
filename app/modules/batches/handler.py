from fastapi import APIRouter,Request,Body
from app.web import page
from app import store
from app.errors import RuleError
router=APIRouter()
@router.get('/batches')
def view(request:Request):return page(request,'batches')
@router.get('/api/batches')
def result():return store.history()
@router.get('/api/batches/ledgers')
def ledger_list():return store.ledgers()
@router.post('/api/batches/review')
def review(payload:dict=Body(...)):
    from app.modules.batches.service import approve
    if not isinstance(payload.get('version'),int):raise RuleError('VERSION','版本必须为整数')
    return approve(payload.get('run_id',''),payload['version'])
@router.post('/api/batches/supplement')
def supplement(payload:dict=Body(...)):
    from app.modules.batches.service import sign
    return sign(payload)
@router.get('/api/batches/{run_id}')
def bundle(run_id:str):
    out=store.get(run_id)
    if not out:raise RuleError('NOT_FOUND','批次不存在',404)
    return out
