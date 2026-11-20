/* Explicit choices stay pinned; no stored choice follows the device. */
window.SuttaTheme=(()=>{
 const key='sf-reader-theme',media=matchMedia('(prefers-color-scheme: dark)');
 const valid=value=>value==='light'||value==='dark'?value:null;
 const read=()=>{try{return valid(localStorage.getItem(key))}catch{return null}};
 let preference=read();
 function sync(){
  const current=preference||(media.matches?'dark':'light'),root=document.documentElement;
  if(preference)root.dataset.theme=preference;else delete root.dataset.theme;
  document.querySelector('meta[name=color-scheme]').content=preference||'light dark';
  const chrome=document.querySelector('meta[name=theme-color]');if(chrome)chrome.content=current==='dark'?'#211c17':'#f6efdf';
  const logo=`assets/tipitaka-pl-${current==='dark'?'gold':'brown'}.svg`;
  document.querySelectorAll('[data-theme-logo]').forEach(image=>image.setAttribute('src',logo));
  const favicon=document.querySelector('link[rel=icon]');if(favicon)favicon.setAttribute('href',logo);
  document.querySelectorAll('.theme-toggle').forEach(button=>{const label=current==='dark'?'Włącz jasny motyw':'Włącz ciemny motyw';button.dataset.themeCurrent=current;button.setAttribute('aria-label',label);button.title=label});
  document.querySelectorAll('[data-theme-system]').forEach(button=>button.hidden=!preference);
 }
 function set(value){preference=value;try{if(value)localStorage.setItem(key,value);else localStorage.removeItem(key)}catch{}sync()}
 document.addEventListener('click',event=>{if(event.target.closest('.theme-toggle'))set((preference||(media.matches?'dark':'light'))==='dark'?'light':'dark');if(event.target.closest('[data-theme-system]'))set(null)});
 window.addEventListener('storage',event=>{if(event.key===key||event.key===null){preference=read();sync()}});
 if(media.addEventListener)media.addEventListener('change',sync);else media.addListener(sync);
 sync();return{sync};
})();
