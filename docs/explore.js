/* Progressive enhancements: no third-party runtime or API credentials. */
(function () {
  'use strict';
  const $ = s => document.querySelector(s);
  const aliases = {tamba:'copper',tamra:'copper','तांबा':'copper',chandi:'silver','चांदी':'silver',sona:'gold',pital:'brass',peetal:'brass',kansa:'bronze',ranga:'tin',parad:'mercury',aluminum:'aluminium'};
  const normalize = value => String(value || '').normalize('NFKC').toLowerCase().replace(/[\u2010-\u2015_-]/g,' ').replace(/\s+/g,' ').trim().split(' ').map(t => aliases[t] || t).join(' ');
  const groupOf = p => {
    const category=normalize(p.category+' '+p.categories), title=normalize(p.name+' '+p.material);
    if (/rudraksha|रुद्राक्ष/.test(category+' '+title)) return 'rudraksha';
    if (/gemstone|diamond|sapphire|emerald|ruby|amethyst|ametrine|opal|citrine|quartz|turquoise|garnet|lapis|moon ?stone|zircon|peridot|iolite|fluorite|coral|tourmaline|topaz|pyrite|chrysoberyl|heliodor|tiger eye|sunstone/.test(category+' '+title)) return 'gemstones';
    if (/gold|silver|platinum|copper|brass|bronze|kansa|tin|ranga|zinc|iron|steel|parad|mercury|aluminium|lead|nickel/.test(category+' '+title)) return 'metals';
    return '';
  };
  // These are browse hints based on explicit merchant wording, not verified variants.
  const typeRules = {
    ring: /\brings?\b/i, payal: /\b(?:payal|anklets?)\b/i,
    bangle: /\b(?:bangles?|kada|bracelets?)\b/i,
    chain: /\b(?:chains?|necklaces?)\b/i,
    utensils: /\b(?:utensils?|vessels?|thali|plates?|bowls?|glass|spoons?|lota|kalash|kadahi)\b/i,
    pendant: /\b(?:pendants?|pandents?|lockets?)\b/i,
    mala: /\b(?:malas?|rosary)\b/i,
    articles: /\b(?:articles?|articels?)\b/i
  };
  const typesOf = p => {
    const evidence = normalize(p.name + ' ' + p.category);
    const specific = Object.entries(typeRules).filter(([key, rule]) => key !== 'articles' && rule.test(evidence)).map(([key]) => key);
    return specific.length ? specific : (typeRules.articles.test(evidence) ? ['articles'] : []);
  };
  const originalSearch = searchable;
  searchable = p => normalize(originalSearch(p));
  const safeImage = p => /^https?:\/\//.test(p.image || '') && !/\/img\/x\.gif(?:\?|$)/.test(p.image);
  document.body.insertAdjacentHTML('afterbegin','<a class="skip" href="#products">Skip to products</a>');
  ['search','category','stock','sort'].forEach(id => $('#'+id).setAttribute('aria-label',({search:'Search catalog',category:'Category',stock:'Availability',sort:'Sort products'})[id]));
  $('#resultCount').setAttribute('aria-live','polite');
  $('.tools').insertAdjacentHTML('afterend',`<div class="advanced">
    <label>Collection<select id="collectionFilter" class="control"><option value="">All collections</option><option value="metals">Metals</option><option value="gemstones">Gemstones</option><option value="rudraksha">Rudraksha</option></select></label>\n    <label>Product form<select id="typeFilter" class="control"><option value="">All product forms</option><option value="ring">Rings</option><option value="payal">Payal & anklets</option><option value="bangle">Bangles & bracelets</option><option value="chain">Chains & necklaces</option><option value="utensils">Utensils & vessels</option><option value="pendant">Pendants</option><option value="mala">Malas</option><option value="articles">Other articles</option></select></label>\n    <label>Metal<select id="metalFilter" class="control"><option value="">All materials</option></select></label>
    <label>Gender claim<select id="genderFilter" class="control"><option value="">All gender claims</option><option value="Male">Male</option><option value="Female">Female</option><option value="Unisex">Unisex</option><option value="-">Not stated</option></select></label>
    <label>Minimum price ₹<input id="minPrice" class="control" type="number" min="0" inputmode="decimal" placeholder="Any"></label>
    <label>Maximum price ₹<input id="maxPrice" class="control" type="number" min="0" inputmode="decimal" placeholder="Any"></label>
    <label>Data availability<select id="qualityFilter" class="control"><option value="">All products</option><option value="valued">Metal value available</option><option value="missing-image">Missing image</option><option value="missing-weight">Weight / size missing</option><option value="uncertain">Metal value unavailable</option></select></label>
  </div><div class="scope scope--metrics" id="filteredSummary" role="status" aria-live="polite">Loading product evidence…</div>`);
  $('#coverage').insertAdjacentHTML('beforebegin','<section class="panel composition-panel" id="catalogComposition" aria-labelledby="compositionHeading"><div class="panel-head"><div><p class="section-kicker">Catalog health</p><h2 id="compositionHeading">Catalog composition</h2></div><span class="meta">Entire loaded catalog</span></div><p class="panel-intro">A quick view of where listings are concentrated and which merchant-provided fields are available. It describes the monitored catalog, not product quality.</p><div class="insight-grid"><div><h3>Largest categories</h3><div id="categoryDistribution"></div></div><div><h3>Available product information</h3><div id="dataDistribution"></div></div></div></section>');
  $('#products').insertAdjacentHTML('afterend','<section class="panel"><div class="panel-head"><h2>Data and methodology</h2></div><div class="data-links"><a href="products-manifest.json">JSON manifest</a><a href="data-guide.md">Field definitions and bot guide</a><button class="chip" id="exportResults">Download filtered JSON</button></div><p class="method">One record per canonical product URL; complete variant coverage is not available. Catalog sightings are not fresh price checks. Prices, availability and material claims must be confirmed with the merchant. Image presence does not guarantee a working image.</p></section>');
  const originalRow = row;
  row = function(p) {
    let html = originalRow(p).replace(/<span class="thumb-fallback"[^>]*>[^<]*<\/span>/,'<span class="thumb-fallback">No image<br>available</span>');
    const images=[...new Set([...(Array.isArray(p.imageCandidates)?p.imageCandidates:[]),p.image].filter(u=>typeof u==='string'&&/^https:\/\//.test(u)&&!/\/img\/x\.gif(?:\?|$)/.test(u)))];
    const imageHtml=images.length?'<img class="thumb lazy-thumb" data-src="'+esc(images[0])+'" data-candidates="'+esc(JSON.stringify(images.slice(1)))+'" alt="" loading="lazy" decoding="async" referrerpolicy="strict-origin-when-cross-origin">':'';
    html=html.replace(/<img class="thumb lazy-thumb"[^>]*>/,imageHtml);
    if(images.length&&!html.includes('class="thumb lazy-thumb"'))html=html.replace('</span></div><div><a href=', '</span>'+imageHtml+'</div><div><a href=');
    if(p.availability==='unknown') html=html.replace('class="pill "','class="pill unknown"');
    const gender=p.gender==='-'?'Not stated':p.gender;
    const material='<td><div>'+esc(p.material||'—')+'</div>';
    html=html.replace(material,'<td><div>'+esc(p.material||'—')+'</div><div class="desc">Gender: '+esc(gender)+'</div>');
    let shownPrice='Price unavailable';
    if(p.priceStatus==='contact_for_price')shownPrice='<a href="'+esc(p.url)+'" target="_blank" rel="noopener">Contact seller for price</a>';
    else if(price(p)!=null) shownPrice=(p.sale!=null?'<span class="old">'+fmt.format(p.regular)+'</span><br><span class="sale">'+fmt.format(p.sale)+'</span>':fmt.format(p.regular))+(p.priceStatus==='listed_unverified'?'<div class="desc">Previously observed · verify with seller</div>':'');
    html=html.replace(/<td class="price">[\s\S]*?<\/td>/,'<td class="price">'+shownPrice+(p.priceStatus==='contact_for_price'?'':metalLine(p))+(p.unitPrice?'<div class="metal">Product ask / stated ct '+fmt.format(p.unitPrice.amount)+' / carat<br><small>May include setting · no gem benchmark</small></div>':'')+'</td>');
    const m=p.metalEstimate;
    const info='<details class="row-detail"><summary>Product evidence</summary><dl><dt>Gender claim</dt><dd>'+esc(gender)+'</dd><dt>Merchant material</dt><dd>'+esc(p.material||'Not provided')+'</dd><dt>Merchant weight / size</dt><dd>'+esc(p.weightSize||'Not provided')+'</dd><dt>Price state</dt><dd>'+esc((p.priceStatus||'unknown').replaceAll('_',' '))+'</dd><dt>Detail last checked</dt><dd>'+esc(p.detailChecked||'Not recorded')+'</dd><dt>Metal assessment</dt><dd>'+esc(m?m.status.replaceAll('_',' '):'No recognized metal claim')+'</dd><dt>First catalog sighting</dt><dd>'+esc(p.firstSeen||'Unknown')+'</dd><dt>Last catalog sighting (not price freshness)</dt><dd>'+esc(p.lastSeen||'Unknown')+'</dd><dt>Record ID</dt><dd>'+esc(p.id)+'</dd></dl></details>';
    return html.replace('</td>',info+'</td>');
  };
  const originalRender=render;
  const originalData=()=>DATA;
  let fullData=null;
  render=function(){
    if(!fullData) fullData=originalData();
    const collection=$('#collectionFilter').value,type=$('#typeFilter').value,metal=$('#metalFilter').value,gender=$('#genderFilter').value,quality=$('#qualityFilter').value;
    const min=$('#minPrice').value===''?null:Number($('#minPrice').value),max=$('#maxPrice').value===''?null:Number($('#maxPrice').value);
    const query=$('#search').value;
    DATA=fullData.filter(p=>{
      const m=p.metalEstimate,pr=price(p);
      return (!collection||groupOf(p)===collection) && (!type||typesOf(p).includes(type)) && (!metal||(m?.detectedMetals||[]).includes(metal)) && (!gender||(p.gender||'-')===gender) && (min===null||(pr!==null&&pr>=min)) && (max===null||(pr!==null&&pr<=max)) && (!quality || (quality==='valued'&&m?.status==='estimated') || (quality==='missing-image'&&!safeImage(p)) || (quality==='missing-weight'&&!p.weightSize) || (quality==='uncertain'&&m&&m.status!=='estimated'));
    });
    $('#search').value=normalize(query);
    originalRender();
    $('#search').value=query;
    DATA=fullData;
    const prices=filtered.map(price).filter(Number.isFinite).sort((a,b)=>a-b),n=prices.length;
    const median=n?(n%2?prices[(n-1)/2]:(prices[n/2-1]+prices[n/2])/2):null;
    const metric=(label,value,kind='')=>'<span class="scope__metric '+kind+'"><strong>'+value+'</strong><span class="scope__label">'+label+'</span></span>';
    $('#filteredSummary').innerHTML=[
      metric('Matching products',filtered.length.toLocaleString('en-IN'),'scope__metric--primary'),
      metric('In stock',filtered.filter(p=>p.availability==='in_stock').length.toLocaleString('en-IN')),
      metric('Stock unknown',filtered.filter(p=>p.availability==='unknown').length.toLocaleString('en-IN'),'scope__metric--caution'),
      metric('Contact for price',filtered.filter(p=>p.priceStatus==='contact_for_price').length.toLocaleString('en-IN')),
      metric('Median asking price',median===null?'Unavailable':fmt.format(median))
    ].join('')+'<span class="scope__note">Based on '+n.toLocaleString('en-IN')+' priced records</span>';
    const u=new URL(location.href);[['q',query],['collection',collection],['type',type],['metal',metal],['gender',gender],['min',min],['max',max],['quality',quality]].forEach(([k,v])=>v===null||v===''?u.searchParams.delete(k):u.searchParams.set(k,v));history.replaceState(null,'',u);
  };
    const originalEnhance=enhance;
  enhance=function(d){
    fullData=d.products;
    const metals=[...new Set(fullData.flatMap(p=>p.metalEstimate?.detectedMetals||[]))].sort();
    $('#metalFilter').insertAdjacentHTML('beforeend',metals.map(m=>'<option>'+esc(m)+'</option>').join(''));
    const u=new URL(location.href);[['collectionFilter','collection'],['typeFilter','type'],['metalFilter','metal'],['genderFilter','gender'],['minPrice','min'],['maxPrice','max'],['qualityFilter','quality']].forEach(([id,key])=>$('#'+id).value=u.searchParams.get(key)||'');
    const typeCounts=Object.fromEntries(Object.keys(typeRules).map(type=>[type,fullData.filter(p=>typesOf(p).includes(type)).length]));
    document.querySelectorAll('[data-type-count]').forEach(node=>{node.textContent=typeCounts[node.dataset.typeCount].toLocaleString('en-IN')+' listings'});
    const counts={};fullData.forEach(p=>{const c=p.category||'Uncategorized';counts[c]=(counts[c]||0)+1});
    const bars=rows=>rows.map(([name,n])=>'<div class="distribution"><span>'+esc(name)+'</span><meter min="0" max="'+fullData.length+'" value="'+n+'">'+n+'</meter><span>'+n+'</span></div>').join('');
    $('#categoryDistribution').innerHTML=bars(Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,6));
    $('#dataDistribution').innerHTML=bars([['Image URL',fullData.filter(safeImage).length],['Material claim',fullData.filter(p=>p.material).length],['Weight / size',fullData.filter(p=>p.weightSize).length],['Metal valuation',fullData.filter(p=>p.metalEstimate?.status==='estimated').length],['Rating',fullData.filter(p=>p.rating!==null).length],['Unknown stock',fullData.filter(p=>p.availability==='unknown').length]]);
    originalEnhance(d);
    const ps=fullData.map(price).filter(Number.isFinite);
    const compact=n=>n>=100000?('₹'+new Intl.NumberFormat('en-IN',{notation:'compact',maximumFractionDigits:1}).format(n)):fmt.format(n).replace('.00','');
    if(ps.length){const range=$('#priceRange');range.textContent=compact(Math.min(...ps))+'–'+compact(Math.max(...ps));range.title=fmt.format(Math.min(...ps))+' to '+fmt.format(Math.max(...ps))}
    const note=$('#priceRange').nextElementSibling;if(note)note.textContent=(d.summary.contactForPrice||0)+' contact for price · '+d.summary.pricedCount+' priced';
  };
  ['collectionFilter','typeFilter','metalFilter','genderFilter','minPrice','maxPrice','qualityFilter'].forEach(id=>$('#'+id).addEventListener('change',render));
  $('#clearFilters').addEventListener('click',()=>{['typeFilter','metalFilter','genderFilter','minPrice','maxPrice','qualityFilter'].forEach(id=>$('#'+id).value='');render()});
  document.querySelectorAll('[data-collection]').forEach(link=>link.addEventListener('click',()=>{
    $('#collectionFilter').value=link.dataset.collection;
    $('#typeFilter').value='';
    render();
    $('#search').focus({preventScroll:true});
  }));
  document.querySelectorAll('[data-type]').forEach(link=>link.addEventListener('click',()=>{
    $('#typeFilter').value=link.dataset.type;
    $('#collectionFilter').value='';
    render();
    $('#search').focus({preventScroll:true});
  }));
  $('#exportResults').addEventListener('click',()=>{const blob=new Blob([JSON.stringify({schemaVersion:1,exportedAt:new Date().toISOString(),view:location.href,recordCount:filtered.length,limitations:'Seller claims; catalog sightings do not establish price freshness; incomplete variant coverage.',products:filtered},null,2)],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='catalog-filtered.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000)});
})();
