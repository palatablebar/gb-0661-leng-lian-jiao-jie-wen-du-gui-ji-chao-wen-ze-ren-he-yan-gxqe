import csv,io
from app.config import MAX_BYTES,MAX_ROWS
from app.errors import RuleError
COLUMNS=['shipment','probe','at','value','unit']
def read(raw):
    if len(raw)>MAX_BYTES:raise RuleError('LIMIT','文件超过2MB')
    encoding=None
    for candidate in ('utf-8-sig','gb18030'):
        try:text=raw.decode(candidate);encoding=candidate;break
        except UnicodeDecodeError:continue
    if encoding is None:raise RuleError('ENCODING','文件编码无法识别')
    if not text:return {'rows':[],'issues':[],'blank':0,'headers':0,'encoding':encoding,'state':'EMPTY_FILE','input':0}
    reader=csv.reader(io.StringIO(text,newline=''),strict=True)
    try:header=next(reader)
    except (StopIteration,csv.Error):raise RuleError('HEADER','缺少表头')
    if header!=COLUMNS:raise RuleError('HEADER','表头必须匹配五列字段')
    rows=[];issues=[];blank=0;headers=0;total=0
    try:
        for record in reader:
            total+=1;line=reader.line_num
            if total>MAX_ROWS:raise RuleError('LIMIT','记录超过10000行')
            if not record or all(not str(x).strip() for x in record):blank+=1;continue
            if record==header:headers+=1;total-=1;continue
            if len(record)!=5:issues.append({'line':line,'code':'COLUMN_COUNT','raw':record});continue
            rows.append(dict(zip(COLUMNS,record),line=line))
    except csv.Error:raise RuleError('TRUNCATED','引号未闭合，请重新导出')
    state='READY' if rows or issues else ('BLANK_ROWS' if blank else 'HEADER_ONLY')
    return {'rows':rows,'issues':issues,'blank':blank,'headers':headers,'encoding':encoding,'state':state,'input':total}
