/* Fetch history only when requested or near view; render one bounded page. */
(function () {
  'use strict';
  const pageSize=12;
  let records=null, matches=[], page=0, pending=false, started=false;
  const $=id=>document.getElementById(id);
  const labels={added:'Added',removed_after_two_consecutive_successful_full_scans:'Removed',back_in_catalog:'Back in catalog',out_of_stock:'Out of stock',restocked:'Restocked',price_increase:'Price increased',price_decrease:'Price decreased',sale_started:'Sale started',sale_ended:'Sale ended'};
  const label=t=>labels[t]||String(t||'Unknown').replaceAll('_',' ');
  const safeUrl=u=>/^https?:\/\//i.test(u||'')?u:'';
  const day=value=>{const d=new Date(value);if(Number.isNaN(d.valueOf()))return '';const parts=Object.fromEntries(new Intl.DateTimeFormat('en-CA',{timeZone:'Asia/Kolkata',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(d).map(p=>[p.type,p.value]));return parts.year+'-'+parts.month+'-'+parts.day;};
  const time=value=>{const d=new Date(value);return Number.isNaN(d.valueOf())?'Date not recorded':d.toLocaleString('en-IN',{dateStyle:'medium',timeStyle:'short',timeZone:'Asia/Kolkata'})+' IST';};
  function render(){
    const q=$('eventSearch').value.trim().toLowerCase(),type=$('eventType').value,from=$('eventFrom').value,to=$('eventTo').value;
    if(from&&to&&from>to){$('historyStatus').textContent='Start date must be on or before end date.';$('eventFrom').setAttribute('aria-invalid','true');$('eventExport').disabled=true;$('events').innerHTML='';$('historyPager').hidden=true;return;}
    $('eventFrom').removeAttribute('aria-invalid');$('historyPager').hidden=false;
    matches=records.filter(e=>(!q||[e.name,e.type,e.old,e.new,e.notes].join(' ').toLowerCase().includes(q))&&(!type||e.type===type)&&(!from||day(e.at)>=from)&&(!to||(day(e.at)&&day(e.at)<=to)));
    if($('eventOrder').value==='oldest')matches.reverse();
    const pages=Math.max(1,Math.ceil(matches.length/pageSize));page=Math.min(page,pages-1);
    $('events').innerHTML=matches.slice(page*pageSize,(page+1)*pageSize).map(e=>{
      const url=safeUrl(e.url),evidence=safeUrl(e.evidenceUrl);
      const title=url?'<a href="'+esc(url)+'" target="_blank" rel="noopener">'+esc(e.name||'Product')+'</a>':'<strong>'+esc(e.name||'Product')+'</strong>';
      return '<article class="event"><div class="label">'+esc(label(e.type))+'</div>'+title+'<div class="delta">'+esc([e.old,e.new].filter(Boolean).join(' → '))+(e.percent?' · '+esc(e.percent)+'%':'')+'</div><div class="event-meta">'+esc(time(e.at))+'</div>'+(e.warning?'<p class="event-warning">'+esc(e.warning)+'</p>':'')+'<details class="event-evidence"><summary>Event evidence</summary><p>'+esc(e.notes||'No additional notes recorded.')+'</p><small>Record '+esc(e.id)+' · Run '+esc(e.runId||'not recorded')+'</small>'+(evidence?'<br><a href="'+esc(evidence)+'" target="_blank" rel="noopener">Source listing ↗</a>':'')+'</details></article>';
    }).join('')||'<div class="empty">No events match these filters. Try a wider date range or clear the filters.</div>';
    $('historyStatus').textContent=matches.length?'Showing '+(page*pageSize+1)+'–'+Math.min((page+1)*pageSize,matches.length)+' of '+matches.length+' matching events · '+records.length+' total recorded':'0 matching events · '+records.length+' total recorded';
    $('eventPage').textContent='Page '+(page+1)+' of '+pages;
    $('eventPrev').disabled=page===0;$('eventNext').disabled=page===pages-1;$('eventExport').disabled=!matches.length;
    $('eventCount').textContent=records.length.toLocaleString('en-IN')+' recorded events';
  }
  async function load(){
    if(records||pending)return;pending=true;$('historyStatus').textContent='Loading complete event history…';$('eventLoad').disabled=true;
    try{
      const response=await fetch('events-history.json',{cache:'no-cache'});if(!response.ok)throw Error('HTTP '+response.status);
      const data=await response.json();if(!Array.isArray(data.events)||data.total!==data.events.length)throw Error('Incomplete history');
      records=data.events;$('eventType').insertAdjacentHTML('beforeend',[...new Set(records.map(e=>e.type))].sort().map(t=>'<option value="'+esc(t)+'">'+esc(label(t))+'</option>').join(''));
      $('historyFilters').disabled=false;$('eventLoad').hidden=true;$('historyPager').hidden=false;render();
    }catch(error){$('historyStatus').textContent='Event history could not be loaded. Retry to see the complete record.';$('eventLoad').textContent='Retry loading history';$('eventLoad').disabled=false;}
    finally{pending=false;}
  }
  function init(){
    if(started)return;started=true;
    $('events').innerHTML='<p class="method">History loads when you reach this section.</p>';
    $('events').insertAdjacentHTML('beforebegin','<p class="panel-intro">Every recorded event, newest first. Dates use Indian Standard Time. Observations are not live offers; flagged changes need verification.</p><fieldset id="historyFilters" class="history-filters" disabled><legend class="sr-only">Filter event history</legend><label>Search products or changes<input id="eventSearch" class="control" type="search" placeholder="Product, price or note…"></label><label>Event type<select id="eventType" class="control"><option value="">All event types</option></select></label><label>From (IST)<input id="eventFrom" class="control" type="date"></label><label>To (IST)<input id="eventTo" class="control" type="date"></label><label>Order<select id="eventOrder" class="control"><option value="newest">Newest first</option><option value="oldest">Oldest first</option></select></label><div class="history-actions"><button id="eventClear" class="chip" type="button">Clear filters</button><button id="eventExport" class="chip" type="button">Download matching JSON</button></div></fieldset><div class="history-status"><span id="historyStatus" role="status" aria-live="polite">Full history available on demand</span><button class="load-more" id="eventLoad" type="button">Load event history</button></div>');
    $('events').insertAdjacentHTML('afterend','<div id="historyPager" class="history-pager" hidden><button class="chip" id="eventPrev" type="button">← Previous</button><span id="eventPage"></span><button class="chip" id="eventNext" type="button">Next →</button></div>');
    $('eventLoad').addEventListener('click',load);
    ['eventSearch','eventType','eventFrom','eventTo','eventOrder'].forEach(id=>$(id).addEventListener(id==='eventSearch'?'input':'change',()=>{page=0;render();}));
    $('eventClear').addEventListener('click',()=>{['eventSearch','eventType','eventFrom','eventTo'].forEach(id=>$(id).value='');$('eventOrder').value='newest';page=0;render();});
    ['eventPrev','eventNext'].forEach((id,i)=>$(id).addEventListener('click',()=>{page+=i?1:-1;render();$('historyStatus').scrollIntoView({block:'start'});}));
    $('eventExport').addEventListener('click',()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(matches,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='catalog-event-history.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);});
    if('IntersectionObserver' in window){const observer=new IntersectionObserver(entries=>{if(entries.some(e=>e.isIntersecting)){observer.disconnect();load();}},{rootMargin:'200px'});observer.observe($('changes'));}
  }
  window.eventHistory={init};
})();
