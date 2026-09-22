/* Progressive enhancements: no third-party runtime or API credentials. */
(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const aliases = {tamba:'copper',tamra:'copper','तांबा':'copper',chandi:'silver','चांदी':'silver',sona:'gold',pital:'brass',peetal:'brass',kansa:'bronze',ranga:'tin',parad:'mercury',aluminum:'aluminium'};
  const normalize = value => String(value || '').normalize('NFKC').toLowerCase().replace(/[\u2010-\u2015_-]/g,' ').replace(/\s+/g,' ').trim().split(' ').map(t => aliases[t] || t).join(' ');
  const originalSearch = searchable;
  searchable = p => normalize(originalSearch(p));
  const safeImage = p => /^https?:\/\//.test(p.image || '') && !/\/img\/x\.gif(?:\?|$)/.test(p.image);
  document.body.insertAdjacentHTML('afterbegin','<a class="skip" href="#products">Skip to products</a>');
  ['search','category','stock','sort'].forEach(id => $('#'+id).setAttribute('aria-label',({search:'Search catalog',category:'Category',stock:'Availability',sort:'Sort products'})[id]));
  $('#resultCount').setAttribute('aria-live','polite');
  $('.tools').insertAdjacentHTML('afterend',`<div class="advanced">
    <label>Metal<select id="metalFilter" class="control"><option value="">All materials</option></select></label>
    <label>Minimum price ₹<input id="minPrice" class="control" type="number" min="0" inputmode="decimal" placeholder="Any"></label>
    <label>Maximum price ₹<input id="maxPrice" class="control" type="number" min="0" inputmode="decimal" placeholder="Any"></label>
    <label>Data availability<select id="qualityFilter" class="control"><option value="">All products</option><option value="valued">Metal value available</option><option value="missing-image">Missing image</option><option value="missing-weight">Weight / size missing</option><option value="uncertain">Metal value unavailable</option></select></label>
  </div><div class="scope" id="filteredSummary" aria-live="polite">Loading product evidence…</div>`);
  $('#coverage').insertAdjacentHTML('beforebegin','<section class="panel"><div class="panel-head"><h2>Catalog composition</h2><span class="meta">Entire loaded catalog</span></div><div class="insight-grid"><div><h3>Largest categories</h3><div id="categoryDistribution"></div></div><div><h3>Available product information</h3><div id="dataDistribution"></div></div></div></section>');
  $('#products').insertAdjacentHTML('afterend','<section class="panel"><div class="panel-head"><h2>Data and methodology</h2></div><div class="data-links"><a href="products-manifest.json">JSON manifest</a><a href="data-guide.md">Field definitions and bot guide</a><button class="chip" id="exportResults">Download filtered JSON</button></div><p class="method">One record per canonical product URL; complete variant coverage is not available. Catalog sightings are not fresh price checks. Prices, availability and material claims must be confirmed with the merchant. Image presence does not guarantee a working image.</p></section>');
  const originalRow = row;
  row = function(p) {
    let html = originalRow(p).replace(/<span class="thumb-fallback"[^>]*>[^<]*<\/span>/,'<span class="thumb-fallback">No image<br>available</span>');
    if(p.availability==='unknown') html=html.replace('class="pill "','class="pill unknown"');
    const m=p.metalEstimate;
    const info='<details class="row-detail"><summary>Product evidence</summary><dl><dt>Merchant material</dt><dd>'+esc(p.material||'Not provided')+'</dd><dt>Merchant weight / size</dt><dd>'+esc(p.weightSize||'Not provided')+'</dd><dt>Metal assessment</dt><dd>'+esc(m?m.status.replaceAll('_',' '):'No recognized metal claim')+'</dd><dt>First catalog sighting</dt><dd>'+esc(p.firstSeen||'Unknown')+'</dd><dt>Last catalog sighting (not price freshness)</dt><dd>'+esc(p.lastSeen||'Unknown')+'</dd><dt>Record ID</dt><dd>'+esc(p.id)+'</dd></dl></details>';
    return html.replace('</td>',info+'</td>');
  };
  const originalRender=render;
  const originalData=()=>DATA;
  let fullData=null;
  render=function(){
    if(!fullData) fullData=originalData();
    const metal=$('#metalFilter').value,quality=$('#qualityFilter').value;
    const min=$('#minPrice').value===''?null:Number($('#minPrice').value),max=$('#maxPrice').value===''?null:Number($('#maxPrice').value);
    const query=$('#search').value;
    DATA=fullData.filter(p=>{
      const m=p.metalEstimate,pr=price(p);
      return (!metal||(m?.detectedMetals||[]).includes(metal)) && (min===null||(pr!==null&&pr>=min)) && (max===null||(pr!==null&&pr<=max)) && (!quality || (quality==='valued'&&m?.status==='estimated') || (quality==='missing-image'&&!safeImage(p)) || (quality==='missing-weight'&&!p.weightSize) || (quality==='uncertain'&&m&&m.status!=='estimated'));
    });
    $('#search').value=normalize(query);
    originalRender();
    $('#search').value=query;
    DATA=fullData;
    const prices=filtered.map(price).filter(Number.isFinite).sort((a,b)=>a-b),n=prices.length;
    const median=n?(n%2?prices[(n-1)/2]:(prices[n/2-1]+prices[n/2])/2):null;
    $('#filteredSummary').textContent=`${filtered.length.toLocaleString('en-IN')} matches · ${filtered.filter(p=>p.availability==='in_stock').length} in stock · ${filtered.filter(p=>p.availability==='unknown').length} stock unknown · Median ${median===null?'unavailable':fmt.format(median)} (${n} priced records)`;
    const u=new URL(location.href);[['q',query],['metal',metal],['min',min],['max',max],['quality',quality]].forEach(([k,v])=>v===null||v===''?u.searchParams.delete(k):u.searchParams.set(k,v));history.replaceState(null,'',u);
  };
  const originalEnhance=enhance;
  enhance=function(d){
    fullData=d.products;
    const metals=[...new Set(fullData.flatMap(p=>p.metalEstimate?.detectedMetals||[]))].sort();
    $('#metalFilter').insertAdjacentHTML('beforeend',metals.map(m=>'<option>'+esc(m)+'</option>').join(''));
    const u=new URL(location.href);[['metalFilter','metal'],['minPrice','min'],['maxPrice','max'],['qualityFilter','quality']].forEach(([id,key])=>$('#'+id).value=u.searchParams.get(key)||'');
    const counts={};fullData.forEach(p=>{const c=p.category||'Uncategorized';counts[c]=(counts[c]||0)+1});
    const bars=rows=>rows.map(([name,n])=>'<div class="distribution"><span>'+esc(name)+'</span><meter min="0" max="'+fullData.length+'" value="'+n+'">'+n+'</meter><span>'+n+'</span></div>').join('');
    $('#categoryDistribution').innerHTML=bars(Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,6));
    $('#dataDistribution').innerHTML=bars([['Image URL',fullData.filter(safeImage).length],['Material claim',fullData.filter(p=>p.material).length],['Weight / size',fullData.filter(p=>p.weightSize).length],['Metal valuation',fullData.filter(p=>p.metalEstimate?.status==='estimated').length],['Rating',fullData.filter(p=>p.rating!==null).length],['Unknown stock',fullData.filter(p=>p.availability==='unknown').length]]);
    originalEnhance(d);
  };
  ['metalFilter','minPrice','maxPrice','qualityFilter'].forEach(id=>$('#'+id).addEventListener('change',render));
  $('#clearFilters').addEventListener('click',()=>{['metalFilter','minPrice','maxPrice','qualityFilter'].forEach(id=>$('#'+id).value='');render()});
  $('#exportResults').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({schemaVersion:1,exportedAt:new Date().toISOString(),view:location.href,recordCount:filtered.length,limitations:'Seller claims; catalog sightings do not establish price freshness; incomplete variant coverage.',products:filtered},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='catalog-filtered.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});
})();
