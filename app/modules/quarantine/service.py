import csv,io,json
from app.modules.quarantine.rules import summarize
def quarantine(*groups,code=None):return summarize([i for group in groups for i in group],code)
def evidence_csv(issues):
    out=io.StringIO();writer=csv.writer(out);writer.writerow(['line','code','reason','raw'])
    for r in issues:
        raw=json.dumps(r['raw'],ensure_ascii=False)
        if raw.startswith(('=','+','-','@')):raw="'"+raw
        writer.writerow([r['line'],r['code'],r['reason'],raw])
    return '﻿'+out.getvalue()
