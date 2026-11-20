/* The library and both search panels share one catalog entry. */
window.SuttaCatalog=(()=>{
 const escape=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
 const arrow='<svg class="row-arrow" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m9 5 7 7-7 7"/></svg>';
 function row(doc,hit,kind=''){
  const slug=encodeURIComponent(doc.slug),anchor=hit?.id?encodeURIComponent(hit.id):'';
  const id=anchor?slug+'/'+anchor:slug;
  const href='b.html?tekst='+slug+(anchor?'#'+anchor:'');
  const pali=doc.paliTitle?`<span class="catalog-pali" lang="pi">${escape(doc.paliTitle)}</span>`:'';
  const text=anchor?hit.text.trim():(doc.description||'').trim();
  const summary=anchor && text.length>260?text.slice(0,260).trimEnd()+'…':text;
  const location=anchor?`<span class="catalog-location" id="location-${id}">${escape(hit.label)} · </span>`:'';
  return `<li><a class="catalog-link${kind?' '+kind:''}" href="${href}" aria-labelledby="code-${id} title-${id}${anchor?' location-'+id:''}"${summary?` aria-describedby="description-${id}"`:''}>
   <span class="catalog-heading"><span class="catalog-code" id="code-${id}">${escape(doc.code)}</span><strong class="catalog-title" id="title-${id}">${escape(doc.title)}</strong>${pali}<span class="catalog-language">${doc.hasPali?'Polski + pāḷi':'Polski'}</span>${arrow}</span>
   ${summary||location?`<span class="catalog-description">${location}<span id="description-${id}">${escape(summary)}</span></span>`:''}
  </a></li>`;
 }
 function searchRows(catalog,kind){
  const bySlug=new Map(catalog.map(doc=>[doc.slug,doc]));
  return hit=>row(bySlug.get(hit.slug),hit,kind);
 }
 return {row,searchRows};
})();
