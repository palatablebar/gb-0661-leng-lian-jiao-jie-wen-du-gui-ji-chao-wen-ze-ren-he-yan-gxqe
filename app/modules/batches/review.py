from app.errors import RuleError

def validate_review(bundle):
    if not bundle['reconcile']['balanced']:raise RuleError('UNBALANCED','对账不平，请先修正数据',409)
    if bundle['model']['handover_issues']:raise RuleError('OWNERSHIP','交接责任冲突，请先修正交接',409)
    return True
