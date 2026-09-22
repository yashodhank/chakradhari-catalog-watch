#!/usr/bin/env python3
import csv, json, statistics, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
DOCS=ROOT/'docs'

def number(v):
 try: return float(v) if v not in ('',None) else None
 except (TypeError,ValueError): return None

def metal_estimate(p,rates):
 text=' '.join(str(p.get(k) or '') for k in ('name','material','weightSize','subtitle'))
 metal=next((m for m in ('Gold','Silver','Platinum') if m.lower() in text.lower()),None)
 if not metal: return None
 weights=[]
 for value,unit in re.findall(r'(?<![\d.])(\d+(?:\.\d+)?)\s*(kg|grams?|gms?|gm|g)\b',text,re.I):
  grams=float(value)*(1000 if unit.lower()=='kg' else 1)
  if 0.01<=grams<=100000: weights.append(grams)
 if not weights: return {'metal':metal,'status':'weight_missing'}
 weight=min(weights)
 purity=None; basis='stated'
 for token,purity_value in [('999',999),('995',995),('925',925),('916',916),('22k',916),('750',750),('18k',750),('585',585),('14k',585),('24k',999)]:
  if re.search(r'(?<!\d)'+re.escape(token)+r'(?!\d)',text,re.I): purity=purity_value; break
 if purity is None:
  purity=916 if metal=='Gold' else 925 if metal=='Silver' else 999
  basis='assumed'
 source_key=f'{metal} {purity}'
 raw=rates.get(source_key)
 if raw is None:
  pure=rates.get(f'{metal} 999')
  raw=(pure*purity/999) if pure is not None else None
 if raw is None: return {'metal':metal,'weightGrams':weight,'purity':purity,'purityBasis':basis,'status':'rate_missing'}
 per_gram=raw/(1000 if metal=='Silver' else 10)
 metal_value=per_gram*weight
 listed=p.get('sale') if p.get('sale') is not None else p.get('regular')
 estimate={'metal':metal,'weightGrams':round(weight,3),'purity':purity,'purityBasis':basis,'ratePerGram':round(per_gram,2),
           'metalValue':round(metal_value,2),'status':'estimated'}
 if listed is not None:
  pretax=listed/1.03
  estimate.update({'listedPrice':listed,'estimatedGstIncluded':round(listed-pretax,2),
                   'nonMetalPremiumPreTax':round(pretax-metal_value,2),'metalSharePct':round(100*metal_value/listed,1) if listed else None})
 return estimate

with (DATA/'current-products.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=[r for r in csv.DictReader(f) if r.get('catalog_status','active')=='active']
metal_data={'latest':{'rates':{}}}
try: metal_data=json.loads((DATA/'metal-rates.json').read_text('utf-8'))
except Exception: pass

products=[]
for r in rows:
 p={
  'id':r.get('monitor_id',''), 'name':r.get('name_observed',''),
  'url':r.get('canonical_url',''), 'category':r.get('breadcrumb_category_observed',''),
  'categories':r.get('all_categories_observed',''), 'availability':r.get('availability_normalized','unknown'),
  'regular':number(r.get('regular_price_normalized')), 'sale':number(r.get('sale_price_normalized')),
  'material':r.get('material_observed',''), 'weightSize':r.get('weight_size_observed',''),
  'reviews':number(r.get('review_count_normalized')), 'rating':number(r.get('rating_normalized')),
  'image':r.get('primary_image_url',''), 'subtitle':r.get('subtitle_observed',''),
  'firstSeen':r.get('first_seen',''), 'lastSeen':r.get('last_seen','')}
 p['metalEstimate']=metal_estimate(p,metal_data.get('latest',{}).get('rates',{}))
 products.append(p)

ins=sum(p['availability']=='in_stock' for p in products)
outs=sum(p['availability']=='out_of_stock' for p in products)
prices=[p['sale'] if p['sale'] is not None else p['regular'] for p in products]
prices=[p for p in prices if p is not None]
events=[]
try:
 with (DATA/'change-events.csv').open(encoding='utf-8-sig',newline='') as f:
  raw_events=list(csv.DictReader(f))[-250:]
 for e in reversed(raw_events):
  if e.get('event_type') in {'added','removed_after_two_consecutive_successful_full_scans','back_in_catalog','out_of_stock','restocked','price_increase','price_decrease','sale_started','sale_ended'}:
   events.append({'at':e.get('event_at',''),'type':e.get('event_type',''),'name':e.get('name_observed',''),
                  'url':e.get('canonical_url',''),'old':e.get('old_value_observed',''),'new':e.get('new_value_observed',''),
                  'percent':e.get('percentage_change','')})
except FileNotFoundError:
 pass
try:
 sources=json.loads((DATA/'sources.json').read_text('utf-8')).get('sources',[])
except Exception:
 sources=[]
category_sources=[s for s in sources if s.get('type') in ('category','collection')]
summary={'total':len(products),'inStock':ins,'outOfStock':outs,'unknown':len(products)-ins-outs,
         'currency':'INR','categories':len(category_sources),'categorySuccess':sum(s.get('status')=='success' for s in category_sources),
         'productPagesEnriched':sum(bool(p['name']) for p in products),'onSale':sum(p['sale'] is not None for p in products),
         'medianPrice':statistics.median(prices) if prices else None,'minPrice':min(prices) if prices else None,
         'maxPrice':max(prices) if prices else None,'eventCount':len(events)}
payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'summary':summary,'recentEvents':events[:80],
         'metalRates':metal_data.get('latest',{}),'products':products}
DOCS.mkdir(exist_ok=True)
(DOCS/'products.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),'utf-8')
print(f"Built docs/products.json with {len(products)} active products")
