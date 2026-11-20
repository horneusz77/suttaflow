/* Polish hyphenation is loaded from this host only when book layout is enabled. */
window.SuttaBook=(()=>{
 const originals=new Map();let ready=null,version=0,hyphenate=null;
 const scopes='.polish,.introduction,.apparatus-content,.all-notes,#note-body';
 function loadScript(file,globalName){
  if(window[globalName])return Promise.resolve();
  return new Promise((resolve,reject)=>{const script=document.createElement('script');script.src='assets/vendor/'+file;script.onload=resolve;script.onerror=()=>{script.remove();reject(Error('Nie udało się pobrać polskich wzorców'))};document.head.append(script)});
 }
 function dictionary(){
  return ready||(ready=Promise.all([loadScript('hyphen-1.14.1.js','createHyphenator'),loadScript('patterns-pl-1.14.1.js','hyphenationPatternsPl')]).then(()=>window.createHyphenator(window.hyphenationPatternsPl,{minWordLength:6,html:false})).catch(error=>{ready=null;throw error}));
 }
 async function setEnabled(enabled){
  const current=++version;
  if(!enabled){return SuttaPosition.preserve(()=>{document.body.classList.remove('book-layout');for(const [node,text]of originals)node.data=text})}
  const dictionaryResult=await dictionary();if(current!==version)return;
  return SuttaPosition.preserve(()=>{hyphenate=dictionaryResult;formatWithin(document);document.body.classList.add('book-layout')});
 }
 function formatWithin(root){
  for(const node of originals.keys())if(!node.isConnected)originals.delete(node);
  const sections=[...root.querySelectorAll(scopes)];if(root.matches?.(scopes))sections.push(root);
  for(const section of sections){
   const walker=document.createTreeWalker(section,NodeFilter.SHOW_TEXT);let node;
   while(node=walker.nextNode()){
    if(originals.has(node)||node.parentElement.closest('a,button,code,pre,em,[lang="pi"],.pali-source,.gatha,h1,h2,h3,h4,h5,h6,summary,#zrodla,#metryka,table,dl')||node.parentElement.closest('p')?.querySelector('br'))continue;
    originals.set(node,node.data);
   }
  }
  for(const [node,text]of originals){const bound=text.replace(/(\p{L}+)([ \t]+)/gu,(all,word)=>word.length===1&&/[aiouwz]/i.test(word)?word+'\u00a0':all);node.data=bound.replace(/\p{L}+/gu,word=>/^[a-ząćęłńóśźż]+$/i.test(word)?hyphenate(word):word)}
 }
 document.addEventListener('copy',event=>{
  if(!document.body.classList.contains('book-layout')||!event.clipboardData)return;
  const selection=getSelection();if(!selection.rangeCount)return;const range=selection.getRangeAt(0),parent=range.commonAncestorContainer.nodeType===1?range.commonAncestorContainer:range.commonAncestorContainer.parentElement;
  if(!parent.closest('.sutta-text,'+scopes))return;
  const clean=text=>text.replace(/\u00ad/g,'').replace(/\u00a0/g,' '),container=document.createElement('div');container.append(range.cloneContents());
  event.clipboardData.setData('text/plain',clean(selection.toString()));event.clipboardData.setData('text/html',clean(container.innerHTML).replace(/&nbsp;|&shy;/g,match=>match==='&nbsp;'?' ':''));event.preventDefault();
 });
 function refresh(root=document){if(document.body.classList.contains('book-layout')&&hyphenate)formatWithin(root)}
 function reset(){version++;for(const [node,text]of originals)node.data=text;originals.clear();document.body.classList.remove('book-layout')}
 return {setEnabled,reset,refresh};
})();
