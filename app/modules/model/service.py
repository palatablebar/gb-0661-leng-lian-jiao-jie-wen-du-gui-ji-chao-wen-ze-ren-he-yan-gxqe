from collections import defaultdict
from datetime import datetime,timedelta
from decimal import Decimal
from app.modules.model.intervals import span,owner_at,interpolate

def partition(rows,handovers,max_gap=15):
    grouped=defaultdict(list);issues=[];seen={}
    for r in rows:grouped[(r['shipment'],r['at'])].append(r)
    dedup=[]
    for key,items in sorted(grouped.items()):
        if len({r['temperature'] for r in items})>1:
            issues.extend({'line':r['line'],'code':'CONFLICT','raw':r} for r in items)
        else:
            winner=min(items,key=lambda r:r['line']);dedup.append(winner)
            issues.extend({'line':r['line'],'code':'DUPLICATE','raw':r} for r in items if r is not winner)
    by_ship=defaultdict(list)
    for r in dedup:by_ship[r['shipment']].append(r)
    segments=[];handover_issues=[]
    for ship,hs in sorted(handovers.items()):
        hs=[dict(h,start=span(h['start'],h['end'])[0].isoformat(),end=span(h['start'],h['end'])[1].isoformat()) for h in hs]
        if not hs:continue
        begin=min(datetime.fromisoformat(h['start']) for h in hs);end=max(datetime.fromisoformat(h['end']) for h in hs)
        rs=sorted(by_ship.get(ship,[]),key=lambda r:r['at'])
        cuts=sorted({begin,end,*[datetime.fromisoformat(r['at']) for r in rs if begin<datetime.fromisoformat(r['at'])<end],*[datetime.fromisoformat(h[k]) for h in hs for k in ('start','end')]})
        for left,right in zip(cuts,cuts[1:]):
            if left<begin or right>end:continue
            mid=left+(right-left)/2;owner=owner_at(mid,hs)
            if owner in ('责任争议','未交接'):handover_issues.append({'shipment':ship,'start':left.isoformat(),'end':right.isoformat(),'code':'HANDOVER_OVERLAP' if owner=='责任争议' else 'HANDOVER_GAP'})
            pair=next(((a,b) for a,b in zip(rs,rs[1:]) if datetime.fromisoformat(a['at'])<=left and right<=datetime.fromisoformat(b['at'])),None)
            known=bool(pair and (datetime.fromisoformat(pair[1]['at'])-datetime.fromisoformat(pair[0]['at'])).total_seconds()<=max_gap*60)
            segments.append({'shipment':ship,'start':left.isoformat(),'end':right.isoformat(),'owner':owner,'minutes':str(Decimal(str((right-left).total_seconds()))/60),'left':str(interpolate(*pair,left)) if known else None,'right':str(interpolate(*pair,right)) if known else None,'sources':[r['line'] for r in pair] if pair else []})
    return {'rows':dedup,'issues':issues,'segments':segments,'handover_issues':handover_issues,'late_count':sum(1 for index,r in enumerate(rows) if any(p['shipment']==r['shipment'] and p['at']>r['at'] for p in rows[:index]))}
