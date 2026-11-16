from decimal import Decimal
from collections import defaultdict
from app.modules.calculate.integral import excess,fmt

def calculate(segments,threshold='8'):
    rows=[];totals=defaultdict(lambda:{'coverage':Decimal(0),'normal':Decimal(0),'excess':Decimal(0),'unknown':Decimal(0),'degree_minutes':Decimal(0)})
    for seg in segments:
        duration=Decimal(seg['minutes']);t=totals[(seg['shipment'],seg['owner'])];t['coverage']+=duration
        if seg['left'] is None:over=area=Decimal(0);t['unknown']+=duration;normal=Decimal(0);state='缺测'
        else:
            over,area=excess(seg['left'],seg['right'],duration,threshold);normal=duration-over;t['excess']+=over;t['normal']+=normal;t['degree_minutes']+=area;state='超温' if over else '正常'
        rows.append(dict(seg,excess_minutes=fmt(over),degree_minutes=fmt(area),normal_minutes=fmt(normal),state=state))
    summary=[{'shipment':k[0],'owner':k[1],**{f:fmt(v) for f,v in values.items()}} for k,values in totals.items()]
    grand={f:fmt(sum((v[f] for v in totals.values()),Decimal(0))) for f in ('coverage','normal','excess','unknown','degree_minutes')}
    return {'rows':rows,'owners':summary,'totals':grand,'threshold':threshold,'unit':'°C·min'}
