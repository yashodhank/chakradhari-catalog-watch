#!/usr/bin/env python3
import json, re, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data'/'metal-rates.json'
URL='https://www.ibjarates.com/'
UA='Mozilla/5.0 (compatible; ChakradhariCatalogMonitor/1.0)'

html=urllib.request.urlopen(urllib.request.Request(URL,headers={'User-Agent':UA}),timeout=45).read().decode('utf-8','replace')
rows=[]
for block in re.findall(r'<tr>\s*<td[^>]+data-label="(?:AM|PM)".*?</tr>',html,re.I|re.S):
 date=re.search(r'<strong>(\d{2}/\d{2}/\d{4})</strong>',block)
 if not date: continue
 vals={k:int(re.search(r'data-label="'+re.escape(k)+r'"[^>]*>\s*([\d,]+)',block,re.I).group(1).replace(',',''))
       for k in ('Gold 999','Gold 995','Gold 916','Gold 750','Gold 585','Silver 999','Platinum 999')}
 session='PM' if 'data-label="PM"' in block else 'AM'
 rows.append((datetime.strptime(date.group(1),'%d/%m/%Y'),session,vals))
if not rows: raise SystemExit('No IBJA benchmark-rate row parsed; retaining previous file')
day=max(r[0] for r in rows); candidates=[r for r in rows if r[0]==day]
chosen=next((r for r in candidates if r[1]=='PM'),candidates[0])
old={'history':[]}
if OUT.exists():
 try: old=json.loads(OUT.read_text('utf-8'))
 except Exception: pass
record={'date':chosen[0].strftime('%Y-%m-%d'),'session':chosen[1],'observed_at':datetime.now(timezone.utc).isoformat(),
        'source':URL,'units':{'gold':'INR per 10 g','silver':'INR per kg','platinum':'INR per 10 g'},
        'gst_included':False,'rates':chosen[2]}
history=old.get('history',[])
if not any(x.get('date')==record['date'] and x.get('session')==record['session'] for x in history): history.append(record)
OUT.write_text(json.dumps({'latest':record,'history':history},ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(record))
