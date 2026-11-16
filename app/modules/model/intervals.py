from datetime import datetime
from decimal import Decimal
from app.errors import RuleError
def span(start,end):
    a=datetime.fromisoformat(start);b=datetime.fromisoformat(end)
    if b<=a:raise RuleError('INTERVAL','交接结束必须晚于开始')
    return a,b

def owner_at(t,handovers):
    matches=[h['owner'] for h in handovers if datetime.fromisoformat(h['start'])<=t<datetime.fromisoformat(h['end'])]
    return matches[0] if len(matches)==1 else ('责任争议' if matches else '未交接')

def interpolate(a,b,t):
    left=datetime.fromisoformat(a['at']);right=datetime.fromisoformat(b['at'])
    ratio=Decimal(str((t-left).total_seconds()))/Decimal(str((right-left).total_seconds()))
    return Decimal(a['temperature'])+(Decimal(b['temperature'])-Decimal(a['temperature']))*ratio
