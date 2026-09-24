#!/usr/bin/env python3
import csv, json, re, hashlib, urllib.request, urllib.error
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit, urljoin

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
NOW=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
RUN_ID=NOW.replace('-','').replace(':','')
UA='Mozilla/5.0 (compatible; ChakradhariCatalogMonitor/1.0)'

def norm(u):
 p=urlsplit(u.strip()); return urlunsplit(('https',p.netloc.lower(),re.sub(r'/+$','',p.path) or '/','',''))
def fetch(u,timeout=45):
 req=urllib.request.Request(u,headers={'User-Agent':UA,'Accept':'text/html,application/xml,text/plain,*/*'})
 with urllib.request.urlopen(req,timeout=timeout) as r: return r.status,r.read(),r.headers.get('content-type','')
def text(v): return re.sub(r'\s+',' ',str(v or '')).strip()
def money(v):
 try: return float(v)
 except: return None
def hashrow(r):
 keys=['name_observed','canonical_url','breadcrumb_category_observed','variant_attributes_observed','availability_normalized','regular_price_normalized','sale_price_normalized','price_status_observed','gender_observed','currency_normalized','material_observed','weight_size_observed','rating_normalized','review_count_normalized','primary_image_url','image_candidates_observed']
 return hashlib.sha256(json.dumps({k:r.get(k,'') for k in keys},sort_keys=True,ensure_ascii=False).encode()).hexdigest()

EXTRA_FIELDS=['gender_observed','price_status_observed','image_candidates_observed','detail_last_checked']
def valid_image(value,base):
 if not isinstance(value,str) or not value.strip(): return ''
 u=urljoin(base,value.strip()); p=urlsplit(u)
 if p.scheme!='https' or p.netloc.lower() not in ('www.chakradhari.com','chakradhari.com','cdn.shopaccino.com'): return ''
 if re.search(r'/img/x\.gif(?:$|\?)',u,re.I): return ''
 return u

def image_candidates(pdata,main,ld,html,url):
 candidates=[]
 def add(item):
  if isinstance(item,(list,tuple)):
   for v in item: add(v)
  elif isinstance(item,dict): add(item.get('url') or item.get('src') or item.get('image'))
  else:
   u=valid_image(item,url)
   if u and u not in candidates: candidates.append(u)
 for k in ('thumb_image','mini_image','big_image'): add(main.get(k))
 add(pdata.get('featured_image_url'))
 add(ld.get('image'))
 for m in re.finditer(r'<meta[^>]+(?:property|name)=["\'](?:og:image|twitter:image)["\'][^>]*>',html,re.I):
  a=re.search(r'content=["\']([^"\']+)',m.group(0),re.I)
  if a: add(a.group(1))
 return candidates[:8]

def gender_claim(pdata,main):
 variants=pdata.get('variants') or []
 genders=set()
 for v in variants:
  for key in ('size','color','material','title'):
   label=text(v.get(key)).lower()
   if label in ('male','men','mens','man'): genders.add('Male')
   if label in ('female','women','womens','woman'): genders.add('Female')
   if label in ('unisex','all genders'): genders.update(('Male','Female'))
 if genders=={'Male','Female'}: return 'Unisex'
 if genders: return next(iter(genders))
 name=text(pdata.get('product_name')).lower()
 if re.search(r'\b(?:men|mens|male)\b',name) and not re.search(r'\b(?:women|womens|female)\b',name): return 'Male'
 if re.search(r'\b(?:women|womens|female)\b',name) and not re.search(r'\b(?:men|mens|male)\b',name): return 'Female'
 return '-'

def product_page(u):
 try:
  status,b,ct=fetch(u); h=b.decode('utf-8','replace')
  m=re.search(r'Theme\.ProductData\s*=\s*(\{.*?\});\s*Theme\.Utils\.Product\.initProduct',h,re.S)
  pdata=json.loads(m.group(1))['product'] if m else {}
  lds=[]
  for raw in re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',h,re.I|re.S):
   try:
    x=json.loads(raw.strip()); lds += x if isinstance(x,list) else [x]
   except: pass
  ld=next((x for x in lds if isinstance(x,dict) and x.get('@type')=='Product'),{})
  offers=ld.get('offers') or {}; offers=offers[0] if isinstance(offers,list) and offers else offers
  crumbs=[]
  bc=next((x for x in lds if isinstance(x,dict) and x.get('@type')=='BreadcrumbList'),{})
  for x in bc.get('itemListElement',[]):
   n=text((x.get('item') or {}).get('name') if isinstance(x.get('item'),dict) else x.get('name'))
   if n and n.lower() not in ('home',text(ld.get('name')).lower()): crumbs.append(n)
  offer_price=money(offers.get('price'))
  variants=pdata.get('variants') or []
  main=next((v for v in variants if str(v.get('show_as_main'))=='1'),variants[0] if variants else {})
  main_regular=money(main.get('compare_at_price'))/100 if main and (money(main.get('compare_at_price')) or 0)>0 else None
  main_net=money(main.get('product_price'))/100 if main and money(main.get('product_price')) is not None else None
  # JSON-LD price and currency form one atomic observation. ProductData may be
  # localized independently by edge location, so only use it when compatible.
  if offer_price is not None and offer_price>0:
   net=offer_price
   regular=main_regular if main_regular and 0.5<=main_regular/offer_price<=5 else offer_price
  else:
   net=main_net
   regular=main_regular or main_net
  hidden=str(pdata.get('hide_price','')).strip().lower() in ('1','true','yes')
  contact=bool(re.search(r'Contact us for price',h,re.I))
  price_status='contact_for_price' if hidden or contact else 'listed' if net is not None and net>0 else 'unknown'
  if price_status!='listed': regular=None; net=None
  elif regular is None or regular<=0: regular=net
  sale=net if regular is not None and net is not None and net<regular else None
  available=pdata.get('available')
  avail=(available is True or str(available).lower() in ('1','true')) if available is not None else None
  if avail is None and isinstance(offers,dict):
   stated=str(offers.get('availability',''))
   avail=True if stated.endswith('/InStock') else False if stated.endswith('/OutOfStock') else None
  if price_status=='contact_for_price' and str(main.get('allow_purchase',pdata.get('allow_purchase',''))).lower() in ('0','false','no'): avail=None
  agg=ld.get('aggregateRating') or {}
  attrs=[]
  for k in ('size','color','title'):
   if main.get(k): attrs.append(f'{k}={main[k]}')
  desc=' '.join([text(ld.get('name')),text(ld.get('description')),text(pdata.get('product_name'))])
  mats=', '.join(x for x in ['Gold','Silver','Copper','Brass','Bronze','Kansa','Iron','Parad','Rudraksha','Sandalwood','Quartz','Gemstone'] if re.search(r'\b'+x+r'\b',desc,re.I))
  ws='; '.join(dict.fromkeys(re.findall(r'\b\d+(?:\.\d+)?\s*(?:kg|gms?|grams?|gm|ml|litres?|liters?|lt|mm|cm|inch(?:es)?|carats?|ct)\b',desc,re.I)))[:500]
  name=text(pdata.get('product_name') or ld.get('name'))
  images=image_candidates(pdata,main,ld,h,u)
  currency=text(offers.get('priceCurrency') or pdata.get('currency') or 'INR').upper()
  currency_mark={'INR':'₹','USD':'US $','EUR':'€','GBP':'£'}.get(currency,currency)
  row={'observed_product_id':text(pdata.get('id')),'observed_sku':text(main.get('sku') or ld.get('sku') or ld.get('productID')),'observed_variant_id':text(main.get('id')),'name_observed':name,'canonical_url':norm(ld.get('url') or u),'breadcrumb_category_observed':' > '.join(crumbs),'variant_attributes_observed':' | '.join(attrs),'availability_observed':text(offers.get('availability') if isinstance(offers,dict) else ''),'availability_normalized':'in_stock' if avail is True else 'out_of_stock' if avail is False else 'unknown','regular_price_observed':f"{currency_mark} {regular:,.2f}" if regular is not None else '','regular_price_normalized':regular if regular is not None else '','sale_price_observed':f"{currency_mark} {sale:,.2f}" if sale is not None else '','sale_price_normalized':sale if sale is not None else '','currency_observed':currency,'currency_normalized':currency,'discount_observed':f"{(regular-sale)*100/regular:.2f}%" if regular and sale is not None else '','discount_pct_normalized':round((regular-sale)*100/regular,2) if regular and sale is not None else '','material_observed':mats,'weight_size_observed':ws,'rating_observed':text(agg.get('ratingValue')),'rating_normalized':money(agg.get('ratingValue')) if agg else '','review_count_observed':text(agg.get('reviewCount')),'review_count_normalized':int(agg.get('reviewCount')) if str(agg.get('reviewCount','')).isdigit() else '','primary_image_url':images[0] if images else '','image_candidates_observed':json.dumps(images),'gender_observed':gender_claim(pdata,main),'price_status_observed':price_status,'detail_last_checked':NOW,'source_url':u,'all_source_urls':u,'subtitle_observed':text(ld.get('description'))}
  row['monitor_id']=hashlib.sha256(row['canonical_url'].encode()).hexdigest()[:20]; row['content_hash']=hashrow(row)
  return u,'success',row,None
 except Exception as e: return u,'error',None,f'{type(e).__name__}: {e}'

def run_scan():
 # Discover standard sources and sitemap children.
 source_obs=[]; errors=[]
 for u,t in [('https://www.chakradhari.com/robots.txt','robots'),('https://www.chakradhari.com/sitemap.xml','sitemap_index'),('https://www.chakradhari.com/','homepage')]:
  try: s,b,c=fetch(u); source_obs.append((u,t,'success',None,len(b)))
  except Exception as e: source_obs.append((u,t,'error',str(e),0)); errors.append(f'{u}: {e}')
 sidx=fetch('https://www.chakradhari.com/sitemap.xml')[1]
 root=ET.fromstring(sidx); smurls=[text(x.text) for x in root.findall('.//{*}loc')]
 sitemap_docs={}
 for u in smurls:
  try: s,b,c=fetch(u,60); sitemap_docs[u]=b; source_obs.append((u,'sitemap','success',None,len(b)))
  except Exception as e: source_obs.append((u,'sitemap','error',str(e),0)); errors.append(f'{u}: {e}')
 prod_sm=next((u for u in smurls if '/sitemap/products/' in u),None)
 if not prod_sm or prod_sm not in sitemap_docs: raise SystemExit('product sitemap unavailable; refusing comparison')
 pr=ET.fromstring(sitemap_docs[prod_sm]); product_urls=[]; lastmods={}
 for x in pr.findall('.//{*}url'):
  u=norm(x.findtext('{*}loc') or ''); product_urls.append(u); lastmods[u]=text(x.findtext('{*}lastmod'))
 product_urls=sorted(set(product_urls))
 # A sitemap listing is reliable source discovery even when a detail page is not
 # fetched on this run. Keep source last-seen coverage current for every product.
 for u in product_urls:
  source_obs.append((u,'product','listed_in_sitemap',None,1))

 # Load previous snapshot and only fetch new/recently modified pages; the complete sitemap is today's catalog boundary.
 cp=DATA/'current-products.csv'
 with cp.open(encoding='utf-8-sig',newline='') as f: rd=csv.DictReader(f); old=list(rd); fields=list(rd.fieldnames)
 fields += [key for key in EXTRA_FIELDS if key not in fields]
 byurl={norm(r['canonical_url']):r for r in old}; oldurls=set(byurl); newurls=set(product_urls)-oldurls; missing=oldurls-set(product_urls)
 # Refresh newly listed products and anything changed since the previous run.
 previous_run=''
 try:
  previous_run=json.loads((DATA/'sources.json').read_text('utf-8')).get('updated_at','')[:10]
 except Exception:
  pass
 # Detect conversion-shaped anomalies against prior same-currency observations.
 # This rechecks corrupted localized prices without declaring a price movement.
 history_reference={}
 ph_path=DATA/'price-history.csv'
 if ph_path.exists():
  with ph_path.open(encoding='utf-8-sig',newline='') as f:
   for hr in csv.DictReader(f):
    hu=norm(hr.get('canonical_url','')); hp=money(hr.get('sale_price_normalized')) or money(hr.get('regular_price_normalized'))
    hc=text(hr.get('currency_normalized')).upper()
    if hu and hp and hc:
     key=(hu,hc); history_reference[key]=max(hp,history_reference.get(key,0))
 suspicious_localized=set()
 for u in product_urls:
  r=byurl.get(u,{}); cpv=money(r.get('sale_price_normalized')) or money(r.get('regular_price_normalized')); cc=text(r.get('currency_normalized')).upper(); ref=history_reference.get((u,cc),0)
  if cpv and ref and 20<=ref/cpv<=100: suspicious_localized.add(u)
 tofetch=set(newurls | suspicious_localized | {u for u in product_urls if not previous_run or lastmods.get(u,'')>=previous_run})
 # Rotate older records that need image, gender or price-state validation, even when
 # the merchant's sitemap lastmod has not changed. Bound added traffic per scan.
 needs=[u for u in product_urls if u in byurl and u not in tofetch and (not valid_image(byurl[u].get('primary_image_url',''),u) or not byurl[u].get('gender_observed') or not byurl[u].get('price_status_observed'))]
 needs.sort(key=lambda u:(byurl[u].get('detail_last_checked') or byurl[u].get('last_changed') or '',u))
 tofetch=sorted(tofetch|set(needs[:80]))
 results=[]
 with ThreadPoolExecutor(max_workers=20) as ex:
  futs=[ex.submit(product_page,u) for u in tofetch]
  for f in as_completed(futs): results.append(f.result())
 success={u:r for u,s,r,e in results if s=='success'}
 for u,s,r,e in results:
  source_obs.append((u,'product',s,e,1 if s=='success' else 0))
  if e: errors.append(f'{u}: {e}')

 events=[]
 currency_mismatch_count=0
 localization_repair_count=0
 event_fields=['event_at','event_type','monitor_id','observed_product_id','observed_variant_id','name_observed','canonical_url','old_value_observed','new_value_observed','old_value_normalized','new_value_normalized','percentage_change','evidence_url','run_id','notes']
 def ev(t,r,oldv='',newv='',oldn='',newn='',pct='',note=''):
  events.append({'event_at':NOW,'event_type':t,'monitor_id':r.get('monitor_id',''),'observed_product_id':r.get('observed_product_id',''),'observed_variant_id':r.get('observed_variant_id',''),'name_observed':r.get('name_observed',''),'canonical_url':r.get('canonical_url',''),'old_value_observed':oldv,'new_value_observed':newv,'old_value_normalized':oldn,'new_value_normalized':newn,'percentage_change':pct,'evidence_url':r.get('canonical_url',''),'run_id':RUN_ID,'notes':note})

 for u in product_urls:
  if u in success:
   nr=success[u]; orow=byurl.get(u)
   nr.update({'first_seen':orow.get('first_seen',NOW) if orow else NOW,'last_seen':NOW,'last_changed':NOW if not orow or nr['content_hash']!=orow.get('content_hash') else orow.get('last_changed',NOW),'missing_streak':'0','catalog_status':'active'})
   if orow:
    for k in fields:
     if k not in nr: nr[k]=orow.get(k,'')
    if not nr.get('breadcrumb_category_observed'): nr['breadcrumb_category_observed']=orow.get('breadcrumb_category_observed','')
    oa,na=orow.get('availability_normalized'),nr.get('availability_normalized')
    if oa=='out_of_stock' and na=='in_stock': ev('restocked',nr,oa,na,oa,na)
    elif oa!='out_of_stock' and na=='out_of_stock': ev('out_of_stock',nr,oa,na,oa,na)
    op=money(orow.get('sale_price_normalized')) or money(orow.get('regular_price_normalized')); np=money(nr.get('sale_price_normalized')) or money(nr.get('regular_price_normalized'))
    old_currency=text(orow.get('currency_normalized')).upper(); new_currency=text(nr.get('currency_normalized')).upper()
    currency_mismatch=bool(op and np is not None and old_currency and new_currency and old_currency!=new_currency)
    reference=history_reference.get((u,new_currency),0)
    repairing_localization=u in suspicious_localized and reference and np is not None and 0.5<=np/reference<=2
    if currency_mismatch and nr.get('price_status_observed')=='listed':
     currency_mismatch_count+=1
     for k in ('regular_price_observed','regular_price_normalized','sale_price_observed','sale_price_normalized','currency_observed','currency_normalized','discount_observed','discount_pct_normalized'): nr[k]=orow.get(k,'')
     nr['content_hash']=hashrow(nr); nr['last_changed']=NOW if nr['content_hash']!=orow.get('content_hash') else orow.get('last_changed',NOW)
    elif repairing_localization:
     localization_repair_count+=1
    elif op and np is not None and op!=np: ev('price_increase' if np>op else 'price_decrease',nr,orow.get('sale_price_observed') or orow.get('regular_price_observed'),nr.get('sale_price_observed') or nr.get('regular_price_observed'),op,np,round((np-op)*100/op,2))
   else: ev('added',nr,newv=nr.get('name_observed'),note='New canonical URL in complete product sitemap')
   byurl[u]=nr
  elif u in byurl:
   byurl[u]['last_seen']=NOW; byurl[u]['missing_streak']='0'; byurl[u]['catalog_status']='active'
  else:
   # Keep the sitemap catalog boundary complete even when a newly listed detail
   # page is temporarily malformed or returns 404. Do not invent price/stock.
   slug=u.rsplit('/',1)[-1]
   nr={k:'' for k in fields}
   nr.update({'monitor_id':hashlib.sha256(u.encode()).hexdigest()[:20],
              'name_observed':text(slug.replace('-',' ').replace('_',' ')).title(),
              'canonical_url':u,'first_seen':NOW,'last_seen':NOW,'last_changed':NOW,
              'source_url':prod_sm,'all_source_urls':prod_sm,'missing_streak':'0',
              'catalog_status':'active','availability_normalized':'unknown'})
   nr['content_hash']=hashrow(nr); byurl[u]=nr
   ev('added',nr,newv=nr['name_observed'],note='New canonical URL in complete product sitemap; detail page unavailable')

 for u in sorted(missing):
  r=byurl[u]; streak=int(r.get('missing_streak') or 0)+1; r['missing_streak']=str(streak)
  if streak==1: ev('missing_after_one_scan',r,note='Absent from successful complete product sitemap scan')
  elif streak==2: r['catalog_status']='removed'; ev('removed_after_two_consecutive_successful_full_scans',r,note='Absent from two consecutive successful complete product sitemap scans')

 rows=sorted(byurl.values(),key=lambda r:(r.get('name_observed','').casefold(),r.get('canonical_url','')))
 with cp.open('w',encoding='utf-8-sig',newline='') as f: w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
 ph=DATA/'price-history.csv'
 with ph.open(encoding='utf-8-sig',newline='') as f: pf=csv.DictReader(f).fieldnames
 with ph.open('a',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=pf)
  for r in rows:
   if r.get('catalog_status')=='active' and r.get('canonical_url') in success:
    d={k:r.get(k,'') for k in pf}; d['observed_at']=NOW; w.writerow(d)
 ce=DATA/'change-events.csv'
 with ce.open('a',encoding='utf-8-sig',newline='') as f: csv.DictWriter(f,fieldnames=event_fields).writerows(events)

 # Merge durable source registry, retaining full history.
 sp=DATA/'sources.json'; sd=json.loads(sp.read_text('utf-8')); smap={norm(x['url']):x for x in sd.get('sources',[]) if x.get('url')}
 for u,t,st,err,n in source_obs:
  k=norm(u); x=smap.get(k)
  if not x:
   x={'url':k,'type':t,'discovered_via':'robots/sitemap/navigation','first_seen':NOW,'history':[]}; smap[k]=x
   dummy={'canonical_url':k,'name_observed':k,'monitor_id':''}; ev('source_added',dummy,newv=k)
  x.update({'last_seen':NOW,'status':st});
  if st=='success': x['last_success']=NOW; x.pop('last_error',None)
  else: x['last_error']=err
  x.setdefault('history',[]).append({'at':NOW,'status':st,'error':err} if err else {'at':NOW,'status':st})
 # Retain disappeared product sources and mark them retired; never delete them.
 current_product_sources=set(product_urls)
 for k,x in smap.items():
  if x.get('type')=='product' and k not in current_product_sources and x.get('status')!='retired':
   x['status']='retired'; x['retired_at']=NOW
   x.setdefault('history',[]).append({'at':NOW,'status':'retired','reason':'absent_from_complete_product_sitemap'})
   dummy={'canonical_url':k,'name_observed':k,'monitor_id':''}; ev('source_retired',dummy,oldv=k,note='Absent from complete product sitemap')
 sd={'schema_version':'1.0','updated_at':NOW,'sources':list(smap.values())}; sp.write_text(json.dumps(sd,ensure_ascii=False,indent=2),'utf-8')
 # Source-added events are created during registry merge, after the first event
 # append above; persist only that tail here.
 source_events=[e for e in events if e['event_type']=='source_added']
 if source_events:
  with ce.open('a',encoding='utf-8-sig',newline='') as f: csv.DictWriter(f,fieldnames=event_fields).writerows(source_events)

 active=[r for r in rows if r.get('catalog_status')=='active']; ins=sum(r.get('availability_normalized')=='in_stock' for r in active); outs=sum(r.get('availability_normalized')=='out_of_stock' for r in active)
 counts={t:sum(e['event_type']==t for e in events) for t in set(e['event_type'] for e in events)}
 partial=len(success)<len(tofetch)
 with (DATA/'run-log.md').open('a',encoding='utf-8') as f:
  f.write(f'\n## {NOW}\n\n- Run ID: {RUN_ID}\n- Result: '+('Partial detail refresh; complete product-sitemap catalog boundary.' if partial else 'Successful complete sitemap comparison with targeted detail refresh.')+f'\n- Product sitemap URLs: {len(product_urls):,}\n- Active products: {len(active):,}\n- In stock: {ins:,}\n- Out of stock: {outs:,}\n- Added: {counts.get("added",0)}; suspected removals: {counts.get("missing_after_one_scan",0)}; confirmed removals: {counts.get("removed_after_two_consecutive_successful_full_scans",0)}; restocks: {counts.get("restocked",0)}; price changes: {counts.get("price_increase",0)+counts.get("price_decrease",0)}.\n- Detail pages attempted/succeeded: {len(tofetch)}/{len(success)}\n- Access errors: {len(errors)}\n- Currency detected: INR\n- Currency-mismatched localized prices ignored: {currency_mismatch_count}\n- Localized price observations repaired from compatible structured data: {localization_repair_count}\n- Evidence: {prod_sm}\n')
 print(json.dumps({'run_id':RUN_ID,'active':len(active),'in_stock':ins,'out_of_stock':outs,'product_sitemap_urls':len(product_urls),'new':counts.get('added',0),'suspected_removed':counts.get('missing_after_one_scan',0),'confirmed_removed':counts.get('removed_after_two_consecutive_successful_full_scans',0),'restocked':counts.get('restocked',0),'price_increase':counts.get('price_increase',0),'price_decrease':counts.get('price_decrease',0),'currency_mismatch_ignored':currency_mismatch_count,'localized_price_repairs':localization_repair_count,'detail_attempted':len(tofetch),'detail_success':len(success),'errors':errors,'events':[e for e in events if e['event_type'] in ('price_increase','price_decrease','restocked','out_of_stock')]}))

if __name__ == "__main__":
 run_scan()
