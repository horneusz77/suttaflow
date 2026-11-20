(()=>{
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const arrow='<svg class="row-arrow" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m9 5 7 7-7 7"/></svg>';
 const names={DN:'Dīgha Nikāya',MN:'Majjhima Nikāya',SN:'Saṃyutta Nikāya',AN:'Aṅguttara Nikāya',KN:'Khuddaka Nikāya',Vinaya:'Vinaya'};
 const results=document.getElementById('library-results'),input=document.getElementById('library-query');
 let catalog=[],collection='all',view='library',query='',matches=null,version=0,searchState='idle';
 const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
 const href=(slug,id='')=>'b.html?tekst='+encodeURIComponent(slug)+(id?'#'+encodeURIComponent(id):'');
 const bookmarks=()=>{const saved=read('sf-reader-library-bookmarks',[]);return Array.isArray(saved)?saved.filter(s=>s&&catalog.some(d=>d.slug===s.slug)&&typeof s.id==='string'&&typeof s.quote==='string'):[]};
 function render(){
  const saved=bookmarks();document.getElementById('bookmark-count').textContent=saved.length||'';
  document.getElementById('show-library').setAttribute('aria-current',view==='library'?'page':'false');document.getElementById('show-bookmarks').setAttribute('aria-current',view==='bookmarks'?'page':'false');
  document.querySelector('.library-search').hidden=view==='bookmarks';document.getElementById('collection-filters').hidden=view==='bookmarks';document.querySelector('.collection-help').hidden=view==='bookmarks';
  results.removeAttribute('aria-busy');
  if(view==='bookmarks'){
   document.getElementById('results-title').textContent='Twoje zakładki';document.getElementById('results-count').textContent=String(saved.length);
   results.innerHTML=saved.length?'<ul class="bookmark-list">'+saved.map(s=>{const d=catalog.find(d=>d.slug===s.slug);return '<li><a class="bookmark-link" href="'+href(d.slug,s.id)+'"><span>'+escape(d.code)+'</span><strong>'+escape(d.title)+'</strong><p>'+escape(s.quote)+'</p></a></li>'}).join('')+'</ul>':'<p class="library-state">Nie masz jeszcze zakładek. Podczas czytania wybierz ikonę zakładki przy fragmencie, do którego chcesz wrócić.</p>';return;
  }
  document.querySelectorAll('[data-filter]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===collection)));
  document.getElementById('clear-search').hidden=!query;
  document.getElementById('results-title').textContent=query?'Wyniki wyszukiwania':collection==='all'?'Biblioteka':names[collection];
  if(query&&searchState==='loading'){results.setAttribute('aria-busy','true');document.getElementById('results-count').textContent='';results.innerHTML='<p class="library-state" role="status">Szukanie w tekstach…</p>';return}
  if(query&&searchState==='error'){document.getElementById('results-count').textContent='';results.innerHTML='<p class="library-state" role="alert">Nie udało się przeszukać tekstów. Sprawdź połączenie i wybierz ponownie „Szukaj”.</p>';return}
  if(query&&matches){
   const filtered=matches.filter(m=>collection==='all'||m.collection===collection);document.getElementById('results-count').textContent='Fragmenty: '+filtered.length;
   results.innerHTML=filtered.length?'<ul class="catalog-list">'+filtered.map(m=>'<li><a class="search-hit" href="'+href(m.slug,m.id)+'"><span>'+escape(m.code)+' · '+escape(m.label)+'</span><strong>'+escape(m.title)+'</strong><p>'+escape(m.text.slice(0,260))+(m.text.length>260?'…':'')+'</p></a></li>').join('')+'</ul>':'<p class="library-state">Brak wyników. Spróbuj krótszej frazy, wybierz inny zbiór lub uwzględnij pāḷi i przypisy.</p>';return;
  }
  const docs=catalog.filter(d=>collection==='all'||d.collection===collection);document.getElementById('results-count').textContent='Teksty: '+docs.length;
  results.innerHTML=docs.length?Object.keys(names).map(group=>{
   const list=docs.filter(d=>d.collection===group);
   if(!list.length)return '';
   const rows=list.map(d=>{
    const id=encodeURIComponent(d.slug),description=d.description?.trim();
    return `<li><a class="catalog-link" href="${href(d.slug)}" aria-labelledby="code-${id} title-${id}"${description?` aria-describedby="description-${id}"`:''}>
     <span class="catalog-code" id="code-${id}">${escape(d.code)}</span>
     <span><strong class="catalog-title" id="title-${id}">${escape(d.title)}</strong>${d.paliTitle?`<span class="catalog-pali" lang="pi">${escape(d.paliTitle)}</span>`:''}</span>
     <span class="catalog-language">${d.hasPali?'Polski + pāḷi':'Polski'}</span>${arrow}
     ${description?`<span class="catalog-description" id="description-${id}">${escape(description)}</span>`:''}
    </a></li>`;
   }).join('');
   return `<section class="catalog-group" aria-label="${names[group]}"><h3>${names[group]}</h3><ul class="catalog-list">${rows}</ul></section>`;
  }).join(''):'<p class="library-state">Nie ma jeszcze przekładów w tym zbiorze. Wybierz „Wszystkie”, aby wrócić do biblioteki.</p>';
 }
 async function showContinue(){
  const last=read('sf-reader-last-document',null),doc=last&&catalog.find(d=>d.slug===last.slug);if(!doc||typeof last.id!=='string')return;
  try{const data=await SuttaLibrary.loadDocument(doc.slug),id=SuttaLibrary.resolveUnitId(data,last.id),index=data.units.findIndex(u=>u.id===id);if(index<0)return;
   document.getElementById('continue-title').textContent=doc.code+' · '+doc.title;document.getElementById('continue-position').textContent='Fragment '+(index+1)+' z '+data.units.length;
   document.getElementById('continue-link').href=href(doc.slug);document.getElementById('continue-reading').hidden=false;
  }catch{}
 }
 document.getElementById('collection-filters').addEventListener('click',e=>{const b=e.target.closest('[data-filter]');if(b){collection=b.dataset.filter;render()}});
 document.getElementById('show-bookmarks').onclick=()=>{view='bookmarks';render()};document.getElementById('show-library').onclick=()=>{view='library';render()};
 document.getElementById('clear-search').onclick=()=>{version++;query='';input.value='';matches=null;searchState='idle';render();input.focus()};
 document.getElementById('library-search').onsubmit=async e=>{
  e.preventDefault();query=input.value.trim();const current=++version;matches=null;if(!query){searchState='idle';render();return}
  searchState='loading';render();
  try{const found=await SuttaLibrary.find(catalog,query,document.getElementById('library-extra').checked);if(current!==version)return;matches=found;searchState='success';render()}
  catch{if(current!==version)return;searchState='error';render()}
 };
 SuttaLibrary.getCatalog().then(list=>{
  catalog=list;document.getElementById('library-total').textContent=(list.length-list.filter(d=>d.collection==='Vinaya').length)+' sutt · '+list.filter(d=>d.collection==='Vinaya').length+' tekst Vinayi';
  document.getElementById('collection-filters').innerHTML=[['all','Wszystkie'],...Object.keys(names).map(key=>[key,key])].map(([key,label])=>'<button type="button" data-filter="'+key+'" aria-pressed="'+(key==='all')+'">'+label+' <span>'+(key==='all'?catalog.length:catalog.filter(d=>d.collection===key).length)+'</span></button>').join('');
  render();showContinue();
 }).catch(()=>{results.removeAttribute('aria-busy');results.innerHTML='<div class="library-state" role="alert">Nie udało się otworzyć biblioteki. Sprawdź połączenie i odśwież stronę.<button type="button" id="retry-library">Spróbuj ponownie</button></div>';document.getElementById('retry-library').onclick=()=>location.reload()});
})();
