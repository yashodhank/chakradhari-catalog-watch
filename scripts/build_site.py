#!/usr/bin/env python3
import csv, json, statistics, re, math
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
DOCS=ROOT/'docs'

def number(v,positive=False):
 try:
  n=float(v) if v not in ('',None) else None
  return n if n is not None and math.isfinite(n) and (not positive or n>0) else None
 except (TypeError,ValueError): return None

from metal_valuation import metal_estimate

def gender_from_name(name):
 name=str(name or '').lower()
 male=bool(re.search(r'\b(?:men|mens|male|man)\b',name))
 female=bool(re.search(r'\b(?:women|womens|female|woman)\b',name))
 if re.search(r'\bunisex\b',name) or (male and female): return 'Unisex'
 if female: return 'Female'
 if male: return 'Male'
 return '-'

def display_title(raw):
 title=str(raw or '').strip().strip('"“”').strip()
 # The merchant occasionally appends editing instructions to a product title.
 title=re.split(r",\s*If it(?:'|’|&#39;)s specifically\b",title,maxsplit=1,flags=re.I)[0]
 return title.rstrip(' ,:-')

with (DATA/'current-products.csv').open(encoding='utf-8-sig',newline='') as f:
 rows=[r for r in csv.DictReader(f) if r.get('catalog_status','active')=='active']
metal_data={'latest':{'rates':{}}}
try: metal_data=json.loads((DATA/'metal-rates.json').read_text('utf-8'))
except Exception: pass

products=[]
for r in rows:
 p={
  'id':r.get('monitor_id',''), 'name':display_title(r.get('name_observed','')),
  'url':r.get('canonical_url',''), 'category':r.get('breadcrumb_category_observed',''),
  'categories':r.get('all_categories_observed',''), 'availability':r.get('availability_normalized','unknown'),
  'regular':number(r.get('regular_price_normalized'),True), 'sale':number(r.get('sale_price_normalized'),True),
  'material':r.get('material_observed',''), 'weightSize':r.get('weight_size_observed',''),
  'reviews':number(r.get('review_count_normalized')), 'rating':number(r.get('rating_normalized')),
  'image':r.get('primary_image_url',''), 'imageCandidates':[],
  'subtitle':r.get('subtitle_observed',''),
  'gender':r.get('gender_observed') or gender_from_name(r.get('name_observed')),
  'priceStatus':r.get('price_status_observed') or ('listed_unverified' if number(r.get('regular_price_normalized'),True) is not None else 'unknown'),
  'detailChecked':r.get('detail_last_checked',''),
  'firstSeen':r.get('first_seen',''), 'lastSeen':r.get('last_seen','')}
 try: p['imageCandidates']=json.loads(r.get('image_candidates_observed') or '[]')[:8]
 except (TypeError,ValueError): pass
 if p['image'] and p['image'] not in p['imageCandidates']: p['imageCandidates'].append(p['image'])
 if p['priceStatus']=='contact_for_price': p['regular']=p['sale']=None
 p['metalEstimate']=metal_estimate(p,metal_data.get('latest',{}).get('rates',{}))
 products.append(p)

product_by_url={p['url']:p for p in products}
historical_sales=set()
try:
 with (DATA/'price-history.csv').open(encoding='utf-8-sig',newline='') as f:
  for h in csv.DictReader(f):
   sale=number(h.get('sale_price_normalized'),True)
   if sale is not None: historical_sales.add((h.get('canonical_url',''),round(sale,2)))
except FileNotFoundError:
 pass

ins=sum(p['availability']=='in_stock' for p in products)
outs=sum(p['availability']=='out_of_stock' for p in products)
prices=[p['sale'] if p['sale'] is not None else p['regular'] for p in products]
prices=[p for p in prices if p is not None]
events=[]
try:
 with (DATA/'change-events.csv').open(encoding='utf-8-sig',newline='') as f:
  raw_events=list(csv.DictReader(f))[-250:]
 for e in reversed(raw_events):
  et=e.get('event_type')
  pct=number(e.get('percentage_change'))
  oldn=number(e.get('old_value_normalized'),True)
  current=product_by_url.get(e.get('canonical_url',''))
  if et=='price_increase' and oldn is not None and current and current.get('sale') is None and (e.get('canonical_url',''),round(oldn,2)) in historical_sales:
   et='sale_ended'
  # Retain anomalous rows in the audit CSV, but do not surface known
  # conversion-shaped localization artifacts as customer-facing changes.
  if et=='price_decrease' and pct is not None and -99.5<=pct<=-90 and not e.get('notes'):
   continue
  if et in {'added','removed_after_two_consecutive_successful_full_scans','back_in_catalog','out_of_stock','restocked','price_increase','price_decrease','sale_started','sale_ended'}:
   events.append({'at':e.get('event_at',''),'type':et,'name':e.get('name_observed',''),
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
         'productPagesEnriched':sum(bool(p['detailChecked']) for p in products),'onSale':sum(p['sale'] is not None for p in products),
         'contactForPrice':sum(p['priceStatus']=='contact_for_price' for p in products),'pricedCount':len(prices),
         'medianPrice':statistics.median(prices) if prices else None,'minPrice':min(prices) if prices else None,
         'maxPrice':max(prices) if prices else None,'eventCount':len(events)}
DOCS.mkdir(exist_ok=True)
for stale in DOCS.glob('products-*.json'):
 stale.unlink()
chunk_size=150
chunk_files=[]
for i in range(0,len(products),chunk_size):
 name=f'products-{i//chunk_size:02d}.json'
 chunk_files.append(name)
 (DOCS/name).write_text(json.dumps(products[i:i+chunk_size],ensure_ascii=False,separators=(',',':')),'utf-8')
payload={'generatedAt':datetime.now(timezone.utc).isoformat(),'summary':summary,'recentEvents':events[:80],
         'metalRates':metal_data.get('latest',{}),'productChunks':chunk_files}
(DOCS/'products-manifest.json').write_text(json.dumps(payload,ensure_ascii=False,separators=(',',':')),'utf-8')
print(f"Built {len(chunk_files)} product chunks with {len(products)} active products")
