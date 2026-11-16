from app.modules.contract.normalize import instant,celsius
from app.errors import RuleError
from app.reasons import SENTINELS
def normalize(rows,calibrations,shipments):
    valid=[];issues=[]
    for row in rows:
        try:
            ship=row['shipment'].strip();probe=row['probe'].strip()
            if ship in SENTINELS:raise RuleError('MISSING','批号缺失')
            if ship not in shipments:raise RuleError('SHIPMENT','未登记货运批号')
            if probe not in calibrations:raise RuleError('PROBE','探头未校准')
            at=instant(row['at']);temp=celsius(row['value'],row['unit'],calibrations[probe])
            valid.append(dict(row,shipment=ship,probe=probe,at=at.isoformat(),temperature=str(temp)))
        except RuleError as e:issues.append({'line':row['line'],'code':e.code,'raw':row})
    return {'rows':valid,'issues':issues,'calibrations':calibrations,'unit':'°C'}
