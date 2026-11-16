import unicodedata
from decimal import Decimal,InvalidOperation
from datetime import datetime,timezone
from app.reasons import SENTINELS
from app.errors import RuleError
def number(value):
    s=unicodedata.normalize('NFKC',str(value)).strip().replace(',','')
    if s in SENTINELS:raise RuleError('MISSING','温度缺失')
    try:n=Decimal(s)
    except InvalidOperation:raise RuleError('NUMBER','温度不是有效数值')
    if not n.is_finite():raise RuleError('NUMBER','温度不能是无穷或非数')
    return n

def instant(value):
    try:
        d=datetime.fromisoformat(value.replace('Z','+00:00'))
        if d.tzinfo is None:raise ValueError()
        return d.astimezone(timezone.utc)
    except (ValueError,TypeError):raise RuleError('TIME','时间必须带时区偏移')

def celsius(value,unit,offset):
    n=number(value)
    if unit.strip().upper() in ('C','℃'):pass
    elif unit.strip().upper() in ('F','℉'):n=(n-32)*Decimal(5)/Decimal(9)
    else:raise RuleError('UNIT','温度单位只能为C或F')
    n+=Decimal(str(offset))
    if not Decimal('-80')<=n<=Decimal('80'):raise RuleError('RANGE','温度超出探头量程')
    return n
