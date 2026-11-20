/* Shared catalogue and text search; requests stay on the reader's own host. */
window.SuttaLibrary=(()=>{
 const cache=new Map();let catalogPromise;
 const normalize=s=>String(s).normalize('NFD').replace(/\p{M}/gu,'').replace(/ł/g,'l').replace(/Ł/g,'L').toLowerCase();
 async function json(url){const r=await fetch(url,{cache:'no-cache'});if(!r.ok)throw Error('Nie udało się odczytać biblioteki');return r.json()}
 const getCatalog=()=>catalogPromise||(catalogPromise=json('assets/katalog.json').catch(error=>{catalogPromise=null;throw error}));
 async function loadDocument(slug){if(!cache.has(slug))cache.set(slug,json('assets/teksty/'+encodeURIComponent(slug)+'.json').catch(error=>{cache.delete(slug);throw error}));return cache.get(slug)}
 async function find(catalog,query,extra=false){const q=normalize(query.trim());if(!q)return[];const docs=await Promise.all(catalog.map(d=>loadDocument(d.slug)));const matches=[];
  for(const doc of docs){const titleMatch=normalize(doc.code+' '+doc.title+' '+doc.paliTitle).includes(q);
   for(const [i,u]of doc.units.entries())if(normalize(u.pl+(extra?' '+u.pi:'')).includes(q)||(titleMatch&&i===0))matches.push({slug:doc.slug,code:doc.code,title:doc.title,collection:doc.collection,id:u.id,text:u.pl,label:'fragment '+(i+1)});
   if(extra)for(const [i,key]of Object.keys(doc.notes).entries())if(normalize(doc.notes[key]).includes(q))matches.push({slug:doc.slug,code:doc.code,title:doc.title,collection:doc.collection,id:'note-'+key,text:doc.notes[key],label:'przypis '+(i+1)});
  }return matches;
 }
 function resolveUnitId(doc,id){
  return doc.previousUnitIds && Object.hasOwn(doc.previousUnitIds,id) ? doc.previousUnitIds[id] : id;
 }
 return {getCatalog,loadDocument,find,normalize,resolveUnitId};
})();
