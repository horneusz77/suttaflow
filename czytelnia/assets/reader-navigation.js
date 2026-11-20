/* Navigation metadata is separate from the translation and pinned to its source. */
window.SuttaNavigation=(()=>{
 let ready=false;
 async function init(doc){
  const panel=document.getElementById('contents-drawer'),container=document.getElementById('contents-links'),hint=document.getElementById('contents-hint'),bar=document.getElementById('reading-progress-fill'),percentage=document.getElementById('reading-percentage');
  const indexes=new Map(doc.units.map((unit,index)=>[unit.id,index]));let source=[],support=[],pending=false;
  function update(){
   pending=false;const progress=SuttaPosition.progress;bar.style.transform=`scaleX(${progress})`;percentage.textContent=Math.round(progress*100)+'%';
   const position=SuttaPosition.current,index=position?indexes.get(position.id):-1;let current=source[0]?.id;
   for(const entry of source)if(indexes.get(entry.id)<=index)current=entry.id;
   if(progress===1)for(const entry of support)if(document.getElementById(entry.id).getBoundingClientRect().top<=120)current=entry.id;
   for(const link of container.querySelectorAll('a')){if(link.dataset.contentsTarget===current)link.setAttribute('aria-current','location');else link.removeAttribute('aria-current')}
  }
  const schedule=()=>{if(!pending){pending=true;requestAnimationFrame(update)}};
  function build(entries,message=''){
   source=entries.length?entries:[{id:doc.units[0].id,label:'Początek przekładu'}];
   if(source[0].id!==doc.units[0].id)source=[{id:doc.units[0].id,label:'Początek przekładu'},...source];
   support=[...document.querySelectorAll('.apparatus>details')].map(el=>{const summary=el.querySelector('summary').cloneNode(true);summary.querySelectorAll('span').forEach(node=>node.remove());return{id:el.id||el.parentElement.id,label:summary.textContent.trim()}});
   container.replaceChildren();
   for(const [entries,title]of [[source,'Części przekładu'],[support,'Objaśnienia i opracowanie']]){
    if(!entries.length)continue;const nav=document.createElement('nav');nav.className='contents-list';nav.setAttribute('aria-label',title);
    if(entries===support){const heading=document.createElement('h3');heading.textContent=title;nav.append(heading)}
    for(const entry of entries){const link=document.createElement('a');link.href='#'+encodeURIComponent(entry.id);link.textContent=entry.label;link.dataset.contentsTarget=entry.id;if(entries===source)link.dataset.contentsSource='';nav.append(link)}container.append(nav);
   }
   hint.textContent=message;hint.hidden=!message;update();
  }
  panel.addEventListener('click',event=>{
   const link=event.target.closest('a[data-contents-target]');if(!link||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;
   const target=document.getElementById(link.dataset.contentsTarget);if(!target)return;
   const details=target.matches('details')?target:target.closest('details')||target.querySelector('details');if(details)details.open=true;
   closeDrawer(panel);target.tabIndex=-1;requestAnimationFrame(()=>{target.focus({preventScroll:true});SuttaPosition.remember()});
  });
  addEventListener('sutta-position',schedule);build([],'Ładowanie części spisu…');
  const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),8000);
  try{
   const response=await fetch('assets/spis-tresci.json?v=0.5.0',{cache:'no-cache',signal:controller.signal});if(!response.ok)throw Error('Contents unavailable');
   const metadata=(await response.json()).documents?.[doc.slug];
   if(!metadata){build([]);return}
   if(metadata.sourceSha256!==doc.sourceSha256){build([],'Spis części wymaga aktualizacji.');return}
   const seen=new Set();let previous=-1;
   const entries=Array.isArray(metadata.sections)?metadata.sections.filter(entry=>{
    if(typeof entry?.id!=='string'||typeof entry.label!=='string'||!entry.label.trim()||entry.label.length>160||!indexes.has(entry.id)||seen.has(entry.id)||indexes.get(entry.id)<previous)return false;
    seen.add(entry.id);previous=indexes.get(entry.id);return true;
   }):[];build(entries);
  }catch{build([],'Nie udało się pobrać części spisu. Skróty do przekładu i objaśnień pozostają dostępne.')}
  finally{clearTimeout(timeout);ready=true}
 }
 return{init,get ready(){return ready}};
})();
