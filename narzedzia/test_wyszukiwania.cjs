// Run from the repository root: node narzedzia/test_wyszukiwania.cjs czytelnia/assets
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const assets=path.resolve(process.argv[2]||'czytelnia/assets');
const read=name=>JSON.parse(fs.readFileSync(path.join(assets,name),'utf8'));
const catalog=read('katalog.json'), requests=[];
let failNext=false;
const window={};
vm.runInNewContext(fs.readFileSync(path.join(assets,'library-data.js'),'utf8'),{window,fetch:async url=>{
 const file=url.slice('assets/'.length);requests.push(file);
 if(failNext){failNext=false;return {ok:false}}
 return {ok:true,json:async()=>read(file)};
}});
const lib=window.SuttaLibrary;
const docs=new Map(catalog.map(d=>[d.slug,read('teksty/'+d.slug+'.json')]));
const fold=s=>s.normalize('NFD').replace(/\p{M}/gu,'').replace(/ł/g,'l').replace(/Ł/g,'L').toLowerCase();
function reference(scope,query,extra){
 const q=fold(query),expected=[];
 for(const meta of scope){
  const d=docs.get(meta.slug);
  const title=fold([d.code,d.title,d.paliTitle].join(' ')).includes(q);
  d.units.forEach((u,i)=>{if((!i&&title)||fold(u.pl+(extra?' '+u.pi:'')).includes(q))expected.push([d.slug,u.id,u.pl])});
  if(extra)for(const [id,text] of Object.entries(d.notes))if(fold(text).includes(q))expected.push([d.slug,'note-'+id,text]);
 }
 return expected;
}
async function main(){
 const all=await lib.getCatalog();const mn=all.filter(d=>d.collection==='MN');
 for(const q of ['MN 48','mn48','Mnisi z Kosambī','Kosambiyasutta','Kosamb']){
  const hit=await lib.lookup(all,q);assert(hit.titlesOnly);assert(hit.matches.some(m=>m.slug==='mn-48'));
 }
 assert.deepEqual(requests,['katalog.json']);
 failNext=true;await assert.rejects(()=>lib.lookup(mn,'cierpienie'));await lib.lookup(mn,'cierpienie');
 assert.deepEqual(new Set(requests.slice(1)),new Set([mn[0].searchFiles[0]]));
 await lib.lookup(mn,'khamo',true);
 assert.deepEqual(new Set(requests.slice(1)),new Set(mn[0].searchFiles));
 const count=requests.length;await lib.lookup(mn,'wielka',true,true);assert.equal(requests.length,count);
 for(const scope of [all,mn,all.filter(d=>d.collection==='AN'),[]]){
  for(const extra of [false,true])for(const term of ['cierpienie','mnisi','BŁOGOSŁAWIONY','saṅkhā','khamo','MN 48','kosamb','zzzzzzz']){
   const response=await lib.lookup(scope,term,extra,true);assert.equal(response.titlesOnly,false);
   const actual=Array.from(response.matches,m=>[m.slug,m.id,m.text]);
   assert.deepEqual(actual,reference(scope,term,extra));
  }
 }
 assert(!requests.some(f=>f.startsWith('teksty/')));
 console.log('PASS — katalog, duplikaty żądań, ponowienie po błędzie, 64 porównania z pełnymi dokumentami');
}
main().catch(err=>{console.error(err);process.exitCode=1});
