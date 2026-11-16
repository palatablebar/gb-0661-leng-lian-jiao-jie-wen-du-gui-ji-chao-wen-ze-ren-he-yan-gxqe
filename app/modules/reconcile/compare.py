from decimal import Decimal

def compare(intake,model,quarantine,calculation):
    row_delta=intake['input']-len(model['rows'])-quarantine['total']-intake['blank']
    t=calculation['totals'];minute_delta=Decimal(t['coverage'])-sum((Decimal(t[k]) for k in ('normal','excess','unknown')),Decimal(0))
    degree_delta=Decimal(t['degree_minutes'])-sum((Decimal(r['degree_minutes']) for r in calculation['owners']),Decimal(0))
    tolerance=Decimal('0.00001')
    return {'input':intake['input'],'output':len(model['rows']),'isolated':quarantine['total'],'blank':intake['blank'],'row_delta':row_delta,'minute_delta':str(minute_delta),'degree_delta':str(degree_delta),'balanced':row_delta==0 and abs(minute_delta)<=tolerance and abs(degree_delta)<=tolerance,'ownership_issues':len(model['handover_issues']),'conclusion':'待补测' if Decimal(t['unknown']) else ('待复核' if model['handover_issues'] else '可归档')}
