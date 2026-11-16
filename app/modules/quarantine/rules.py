from collections import Counter
from app.reasons import REASONS
def summarize(issues,code=None):
    selected=[dict(i,reason=REASONS.get(i['code'],i['code'])) for i in issues if code is None or i['code']==code]
    return {'rows':selected,'counts':dict(sorted(Counter(i['code'] for i in issues).items())),'selected':len(selected),'total':len(issues)}
