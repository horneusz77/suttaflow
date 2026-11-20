/* Shared catalogue and text search; requests stay on the reader's own host. */
window.SuttaLibrary=(()=>{
 const cache=new Map();let catalogPromise;
 const normalize=s=>String(s).normalize('NFD').replace(/\p{M}/gu,'').replace(/ł/g,'l').replace(/Ł/g,'L').toLowerCase();
 async function json(url,cache='no-cache'){const r=await fetch(url,{cache});if(!r.ok)throw Error('Nie udało się odczytać biblioteki');return r.json()}
 const getCatalog=()=>catalogPromise||(catalogPromise=json('assets/katalog.json').catch(error=>{catalogPromise=null;throw error}));
 async function loadDocument(slug){if(!cache.has(slug))cache.set(slug,json('assets/teksty/'+encodeURIComponent(slug)+'.json').catch(error=>{cache.delete(slug);throw error}));return cache.get(slug)}
 const indexCache=new Map();
 function loadIndex(file){
  if(!indexCache.has(file)){
   const promise=json('assets/'+encodeURIComponent(file),'default').then(index=>{
    // Fold accents once per downloaded index, keeping original text for snippets.
    for(const doc of Object.values(index)){
     if(Array.isArray(doc)){
      for(const row of doc)row.push(normalize(row[1]));
     }else{
      doc.pali=doc.pali.map(normalize);
      doc.notes=Object.entries(doc.notes).map(([id,text])=>[id,text,normalize(text)]);
     }
    }
    return index;
   }).catch(error=>{indexCache.delete(file);throw error});
   indexCache.set(file,promise);
  }
  return indexCache.get(file);
 }
 function titleHits(catalog,q){
  const codeKey=value=>normalize(value).replace(/[\s-]/g,'');
  const ref=codeKey(q);
  const exact=catalog.filter(d=>codeKey(d.code)===ref);
  if(exact.length)return exact;
  return catalog.filter(d=>normalize(d.code+' '+d.title+' '+d.paliTitle).includes(q));
 }
 async function lookup(catalog,query,extra=false,forceText=false){
  const q=normalize(query.trim());
  if(!q)return {titlesOnly:false,matches:[]};
  const titles=titleHits(catalog,q);
  if(titles.length && !forceText && !extra){
   return {titlesOnly:true,matches:titles.map(d=>({slug:d.slug,code:d.code,title:d.title,collection:d.collection,id:'',label:'tytuł',text:d.description||''}))};
  }
  const files=new Set(catalog.flatMap(d=>extra?d.searchFiles:[d.searchFiles[0]]));
  const parts=new Map(await Promise.all([...files].map(async file=>[file,await loadIndex(file)])));
  const matches=[];
  const titleSlugs=new Set(titles.map(d=>d.slug));
  for(const {slug,code,title,collection,searchFiles} of catalog){
   const rows=parts.get(searchFiles[0])[slug];
   const supplement=extra?parts.get(searchFiles[1])[slug]:null;
   const add=(id,label,text)=>matches.push({slug,code,title,collection,id,label,text});
   for(const [i,[id,pl,folded]] of rows.entries()){
    if((i===0 && titleSlugs.has(slug)) || (extra?folded+' '+supplement.pali[i]:folded).includes(q)){
     add(id,'fragment '+(i+1),pl);
    }
   }
   if(extra)supplement.notes.forEach(([key,text,folded],i)=>{
    if(folded.includes(q))add('note-'+key,'przypis '+(i+1),text);
   });
  }
  return {titlesOnly:false,matches};
 }
 // Earlier reader scripts expect a flat array of full-text matches.
 async function find(catalog,query,extra=false){
  return (await lookup(catalog,query,extra,true)).matches;
 }
 function resolveUnitId(doc,id){
  return doc.previousUnitIds && Object.hasOwn(doc.previousUnitIds,id) ? doc.previousUnitIds[id] : id;
 }
 return {getCatalog,loadDocument,lookup,find,normalize,resolveUnitId};
})();
