from fastapi.templating import Jinja2Templates
from app.config import ROOT
from app import store
PAGES=[('intake','轨迹采信'),('contract','探头校准'),('model','交接区间'),('calculate','超温积分'),('quarantine','质量隔离'),('reconcile','责任对账'),('batches','批次复核')]
templates=Jinja2Templates(directory=str(ROOT/'app/templates'))
def page(request,slug):
    bundle=store.latest()
    return templates.TemplateResponse(request=request,name=slug+'.html',context={'bundle':bundle,'pages':PAGES,'slug':slug,'title':dict(PAGES)[slug],'history':store.history()})
