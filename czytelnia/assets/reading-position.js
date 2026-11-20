/* Locations refer to source text characters, not viewport pixels or soft hyphens. */
window.SuttaPosition=(()=>{
 let doc=null,last=null,busy=false,ready=false,timer,resizeTimer,viewportWidth=innerWidth,total=0,anchorY=null;
 const textPositions=new Map(),notify=()=>dispatchEvent(new Event('sutta-position'));
 const line=90,clean=text=>text.replace(/\u00ad/g,'');
 const read=key=>{try{return JSON.parse(localStorage.getItem(key))}catch{return null}};
 const write=(key,value)=>{try{localStorage.setItem(key,JSON.stringify(value))}catch{}};
 const frame=()=>new Promise(resolve=>requestAnimationFrame(resolve));
 function nodes(root){const excluded=root.matches('.pali')?'.note-ref,button':'.note-ref,button,.pali,[lang=pi]',out=[],walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while(node=walker.nextNode())if(node.data.trim()&&!node.parentElement.closest(excluded))out.push(node);return out}
 function rect(node,offset){const range=document.createRange();range.setStart(node,Math.min(offset,node.length));range.setEnd(node,Math.min(offset+1,node.length));return range.getClientRects()[0]}
 function captureText(root,id,part){
   if(!root)return null;
   let offset=0;
   for(const node of nodes(root)){
    const range=document.createRange();range.selectNodeContents(node);const bounds=range.getBoundingClientRect();
    if(bounds.bottom>line&&bounds.top<innerHeight){let lo=0,hi=node.length-1;while(lo<hi){const mid=(lo+hi)>>1,r=rect(node,mid);if(r&&r.bottom>line)hi=mid;else lo=mid+1}const r=rect(node,lo);if(r&&r.top<innerHeight)return{id,offset:offset+clean(node.data.slice(0,lo)).length,top:r.top-line,source:doc.sourceSha256,...(part?{part}:{})}}
    offset+=clean(node.data).length;
   }
   return null;
 }
 function capture(){
  if(!doc)return null;
  for(const unit of document.querySelectorAll('.sutta-text .unit')){
   if(unit.getBoundingClientRect().bottom<=line)continue;
   const location=captureText(unit.querySelector('.polish'),unit.id)||captureText(unit.querySelector('.pali'),unit.id,'pali');if(location)return location;
  }return null;
 }
 function valid(value){return value&&typeof value.id==='string'&&doc.units.some(u=>u.id===value.id)&&(value.part===undefined||value.part==='pali')&&Number.isInteger(value.offset)&&value.offset>=0&&Number.isFinite(value.top)&&Math.abs(value.top)<innerHeight}
 // Hiding Pali shows its Polish unit, while retaining the cursor for a round trip.
 function inLayout(value){return value?.part==='pali'&&!document.getElementById(value.id)?.querySelector('.pali')?.getClientRects().length?{id:value.id,offset:0,top:0,source:value.source}:value}
 function restore(value){
  value=inLayout(value);
  if(!value||!doc.units.some(u=>u.id===value.id))return false;
  const unit=document.getElementById(value.id);if(!unit)return false;
  if(!valid(value)||value.source!==doc.sourceSha256){unit.scrollIntoView({block:'start',behavior:'instant'});return true}
  let remaining=value.offset;
  for(const node of nodes(unit.querySelector(value.part==='pali'?'.pali':'.polish')||unit)){
   const length=clean(node.data).length;if(remaining>=length){remaining-=length;continue}
   let actual=0,count=0;while(actual<node.length&&count<remaining){if(node.data[actual]!=='\u00ad')count++;actual++}const r=rect(node,actual);if(r){scrollBy({top:r.top-(line+value.top),behavior:'instant'});return true}
  }unit.scrollIntoView({block:'start',behavior:'instant'});return true;
 }
 // Reflow scroll events must not replace the source character with a new line start.
 function remember(){if(busy||!doc)return;if(anchorY===null||Math.abs(scrollY-anchorY)>.5){last=capture();anchorY=scrollY}notify();if(!last)return;write('sf-reader-location:'+doc.slug,last);write('sf-reader-position:'+doc.slug,last.id);write('sf-reader-last-document',{slug:doc.slug,id:last.id})}
 async function preserve(change){if(!doc||busy)return change();const location=anchorY!==null&&Math.abs(scrollY-anchorY)<=.5?last:capture();busy=true;try{await change();await document.fonts.ready;await frame();last=location;if(last)restore(last);anchorY=scrollY}finally{busy=false;remember()}}
 async function init(data){
  doc=data;busy=true;history.scrollRestoration='manual';
  total=0;textPositions.clear();for(const unit of doc.units){const root=document.getElementById(unit.id)?.querySelector('.polish'),length=root?nodes(root).reduce((sum,node)=>sum+clean(node.data).length,0):0;textPositions.set(unit.id,{start:total,length});total+=length}
  await document.fonts.ready;await frame();
  let target=null;
  if(location.hash){let id=location.hash.slice(1);try{id=decodeURIComponent(id)}catch{}id=SuttaLibrary.resolveUnitId(doc,id);target={id};const el=document.getElementById(id);const details=el?.closest('details');if(details)details.open=true;el?.scrollIntoView({block:'start',behavior:'instant'})}
  else{const stored=read('sf-reader-location:'+doc.slug),legacy=read('sf-reader-position:'+doc.slug);if(stored && typeof stored==='object')stored.id=SuttaLibrary.resolveUnitId(doc,stored.id);
   target=valid(stored)?stored:typeof legacy==='string'?{id:SuttaLibrary.resolveUnitId(doc,legacy)}:null;if(target&&doc.units.some(u=>u.id===target.id)){const back=document.createElement('button');back.className='resume-reading';back.textContent='Początek tekstu';back.onclick=()=>{last=null;write('sf-reader-location:'+doc.slug,null);write('sf-reader-position:'+doc.slug,null);write('sf-reader-last-document',{slug:doc.slug,id:doc.units[0].id});scrollTo({top:0,behavior:'instant'});anchorY=scrollY;notify()};document.querySelector('.reading-toolbar').after(back);restore(target)}}
  busy=false;ready=true;last=valid(target)&&target.source===doc.sourceSha256?target:capture();anchorY=scrollY;remember();
  addEventListener('scroll',()=>{if(busy||innerWidth!==viewportWidth||Math.abs(scrollY-anchorY)<=.5)return;last=capture();anchorY=scrollY;notify();clearTimeout(timer);timer=setTimeout(remember,200)},{passive:true});
  addEventListener('pagehide',remember);
  addEventListener('resize',()=>{if(innerWidth===viewportWidth)return;viewportWidth=innerWidth;if(busy)return;clearTimeout(resizeTimer);const saved=last;if(!saved){anchorY=null;remember();return}busy=true;resizeTimer=setTimeout(async()=>{await document.fonts.ready;await frame();last=saved;restore(last);anchorY=scrollY;busy=false;remember()},120)});
 }
 function progress(){const location=inLayout(last),item=location&&textPositions.get(location.id);if(!total)return 0;return item?Math.min(1,(item.start+(location.part==='pali'?item.length:Math.min(location.offset,item.length)))/total):document.querySelector('.sutta-text').getBoundingClientRect().bottom<=line?1:0}
 return{init,capture,preserve,remember,get current(){return inLayout(last)},get progress(){return progress()},get ready(){return ready},get busy(){return busy}};
})();
