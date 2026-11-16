import time
from app import store
from app.errors import RuleError
from app.modules.batches.review import validate_review
from app.modules.batches.supplement import validate,apply,diff,basis

def persist(bundle):return store.save(bundle)

def approve(rid,version):
    bundle=store.latest()
    if not bundle or bundle['manifest']['run_id']!=rid:
        raise RuleError('NOT_FOUND','批次不存在或不是当前批次',404)
    validate_review(bundle)
    return store.review(rid,version)

def sign(payload):
    bundle=store.latest()
    if not bundle:raise RuleError('NOT_FOUND','当前没有可补签的批次',404)
    supplement=validate(payload)
    started=time.perf_counter()
    new_bundle=apply(bundle,supplement)
    new_bundle['manifest']['elapsed_ms']=round((time.perf_counter()-started)*1000,3)
    return store.publish(bundle,new_bundle,supplement,diff(bundle['calculate'],new_bundle['calculate']),basis(bundle,supplement,new_bundle['manifest']))
