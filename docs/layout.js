/* Compact navigation: hover/focus expansion, optional pin, accessible mobile drawer. */
(function () {
  'use strict';
  const side=document.querySelector('.side'), main=document.querySelector('.main');
  const mobile=window.matchMedia('(max-width:760px)');
  const icon=path=>'<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+path+'</svg>';
  const paths=['<path d="m3 10 9-7 9 7v10H3zM9 20v-7h6v7"/>','<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>','<path d="m3 17 6-6 4 3 8-10M15 4h6v6"/>','<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>','<path d="M3 11a9 9 0 1 1 3 7M3 4v7h7M12 7v5l3 2"/>','<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6zM8 12l3 3 5-6"/>'];
  const links=[...side.querySelectorAll('.nav a')];
  links.forEach((link,i)=>{const label=link.textContent;link.setAttribute('aria-label',label);link.title=label;link.innerHTML=icon(paths[i])+'<span class="nav-label">'+label+'</span>';});
  const brand=side.querySelector('.brand');brand.innerHTML='<span class="brand-mark" aria-hidden="true">C</span><span class="nav-label">'+brand.innerHTML+'</span>';
  side.insertAdjacentHTML('beforeend','<button class="nav-pin" type="button" aria-pressed="false" aria-label="Pin sidebar open" title="Pin sidebar open">'+icon('<path d="m8 3 8 0-1 6 4 4H5l4-4zM12 13v8"/>')+'<span class="nav-label">Pin sidebar open</span></button>');
  document.body.insertAdjacentHTML('afterbegin','<div class="mobile-bar"><button id="navToggle" type="button" aria-controls="sidebar" aria-expanded="false" aria-label="Open navigation">'+icon('<path d="M4 6h16M4 12h16M4 18h16"/>')+'</button><a href="#products">Chakradhari Watch</a></div><button class="nav-backdrop" tabindex="-1" aria-label="Close navigation" hidden></button>');
  const toggle=document.querySelector('#navToggle'),backdrop=document.querySelector('.nav-backdrop'),pin=side.querySelector('.nav-pin');
  let pinned=false;
  try { pinned=localStorage.getItem('catalog-sidebar-pinned')==='true'; } catch (_) {}
  function setPinned(value){pinned=value;document.body.classList.toggle('nav-pinned',value);pin.setAttribute('aria-pressed',String(value));pin.title=pin.ariaLabel=value?'Unpin sidebar (auto-hide)':'Pin sidebar open';pin.querySelector('.nav-label').textContent=value?'Unpin · auto-hide':'Pin sidebar open';try{localStorage.setItem('catalog-sidebar-pinned',String(value));}catch(_){}}
  function setOpen(value,restoreFocus=true){document.body.classList.toggle('nav-open',value);toggle.setAttribute('aria-expanded',String(value));toggle.setAttribute('aria-label',value?'Close navigation':'Open navigation');backdrop.hidden=!value;side.inert=mobile.matches&&!value;main.inert=mobile.matches&&value;if(value)links[0].focus();else if(restoreFocus)toggle.focus();}
  pin.addEventListener('click',()=>setPinned(!pinned));
  toggle.addEventListener('click',()=>setOpen(toggle.getAttribute('aria-expanded')!=='true'));
  backdrop.addEventListener('click',()=>setOpen(false));
  document.addEventListener('keydown',event=>{
    if(!mobile.matches||toggle.getAttribute('aria-expanded')!=='true')return;
    if(event.key==='Escape'){event.preventDefault();setOpen(false);}
    if(event.key==='Tab'){const controls=[toggle,...side.querySelectorAll('a,button')].filter(el=>el.getClientRects().length);const i=controls.indexOf(document.activeElement);if(event.shiftKey&&i<=0){event.preventDefault();controls.at(-1).focus();}else if(!event.shiftKey&&i===controls.length-1){event.preventDefault();toggle.focus();}}
  });
  links.forEach(link=>link.addEventListener('click',()=>{if(mobile.matches)setOpen(false,false);}));
  mobile.addEventListener('change',()=>setOpen(false,false));
  setPinned(pinned);setOpen(false,false);
  // Track the section being read instead of permanently highlighting Overview.
  let scheduled=false;
  function highlight(){scheduled=false;let active=links[0];for(const link of links){const section=document.querySelector(link.getAttribute('href'));if(section&&section.getBoundingClientRect().top<=150)active=link;}links.forEach(link=>{const selected=link===active;link.classList.toggle('active',selected);if(selected)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current');});}
  window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(highlight);}},{passive:true});highlight();
})();
