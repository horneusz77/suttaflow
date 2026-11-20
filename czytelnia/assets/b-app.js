/* Two reading prototypes. Storage belongs only to this browser, never to an account. */
const icons = {
 book:'<path d="M3 4.5h5a4 4 0 0 1 4 2 4 4 0 0 1 4-2h5V20h-5a4 4 0 0 0-4 2 4 4 0 0 0-4-2H3z"/><path d="M12 6.5V22"/>',
 search:'<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/>',
 bookmark:'<path d="M6 3h12v18l-6-4-6 4z"/>',
 arrow:'<path d="m14 6-6 6 6 6M8 12h13"/>',
 close:'<path d="m6 6 12 12M18 6 6 18"/>',
 menu:'<path d="M4 6h16M4 12h16M4 18h16"/>',
 chevron:'<path d="m9 5 7 7-7 7"/>',
 lock:'<rect x="5" y="10" width="14" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
 check:'<path d="m5 12 4 4L19 6"/>',
 settings:'<path d="M4 7h16M4 17h16"/><circle cx="9" cy="7" r="3" fill="currentColor"/><circle cx="15" cy="17" r="3" fill="currentColor"/>',
 list:'<path d="M9 6h11M9 12h11M9 18h11M4 6h.01M4 12h.01M4 18h.01"/>',
 note:'<path d="M5 3h14v18H5zM8 8h8M8 12h8M8 16h5"/>',
 plus:'<path d="M12 5v14M5 12h14"/>',
 minus:'<path d="M5 12h14"/>',
 // Selected Lucide icons (ISC); full notices: vendor/lucide-LICENSE.txt.
 typeNormal:"<path d=\"M12 4v16\" />\n  <path d=\"M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2\" />\n  <path d=\"M9 20h6\" />",
 typeStrong:"<g stroke-width=\"2.7\"><path d=\"M12 4v16\" />\n  <path d=\"M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2\" />\n  <path d=\"M9 20h6\" /></g>",
 bookText:"<path d=\"M12 5v16\" />\n  <path d=\"M16 13h2\" />\n  <path d=\"M16 9h2\" />\n  <path d=\"M20.001 19A2 2 0 0022 17V5a2 2 0 00-1.999-2L16 3.002A5 5 0 0012 5a5 5 0 00-4-2H4a2 2 0 00-2 2v12a2 2 0 001.999 2H8a5 5 0 014 2 5 5 0 014-2z\" />\n  <path d=\"M6 13h2\" />\n  <path d=\"M6 9h2\" />",
 plainText:"<path d=\"M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z\" />\n  <path d=\"M14 2v5a1 1 0 0 0 1 1h5\" />\n  <path d=\"M10 9H8\" />\n  <path d=\"M16 13H8\" />\n  <path d=\"M16 17H8\" />",
 alignJustify:"<path d=\"M3 5h18\" />\n  <path d=\"M3 12h18\" />\n  <path d=\"M3 19h18\" />",
 alignStart:"<path d=\"M21 5H3\" />\n  <path d=\"M15 12H3\" />\n  <path d=\"M17 19H3\" />",
 resetAppearance:"<path d=\"M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8\" />\n  <path d=\"M3 3v5h5\" />",
 leadingCompact:"<path d=\"M5 8h14M5 12h14M5 16h14\"/>",
 leadingStandard:"<path d=\"M5 5h14M5 12h14M5 19h14\"/>",
 leadingLoose:"<path d=\"M5 3h14M5 12h14M5 21h14\"/>",
 marginsNarrow:"<rect x=\"2.5\" y=\"3\" width=\"19\" height=\"18\" rx=\"1\" stroke-width=\"1.2\"/><path d=\"M5 7h14M5 12h14M5 17h14\"/>",
 marginsStandard:"<rect x=\"2.5\" y=\"3\" width=\"19\" height=\"18\" rx=\"1\" stroke-width=\"1.2\"/><path d=\"M7.5 7h9.0M7.5 12h9.0M7.5 17h9.0\"/>",
 marginsWide:"<rect x=\"2.5\" y=\"3\" width=\"19\" height=\"18\" rx=\"1\" stroke-width=\"1.2\"/><path d=\"M10 7h4M10 12h4M10 17h4\"/>"
};
const icon = name => `<svg class="icon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">${icons[name] || icons.book}</svg>`;
const escapeHtml = s => String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const plain = s => s.replace(/\[\^([^\]]+)\]/g,'').replace(/\*\*?|_/g,'');
let data, noteKeys, saved = [], activeNote = null, catalog = [], currentCollection;
let searchVersion=0;
const readStorage = (key, fallback) => {try {return JSON.parse(localStorage.getItem(key)) ?? fallback;} catch {return fallback;}};
const saveStorage = (key, value) => {try {localStorage.setItem(key,JSON.stringify(value));} catch {announce('Przeglądarka nie pozwala zapisać ustawienia. Zadziała do zamknięcia karty.');}};
const variant = document.body.classList.contains('variant-a') ? 'a' : 'b';
const inline = (s, refs=true) => escapeHtml(s).replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>').replace(/\*([^*]+)\*/g,'<em>$1</em>').replace(/\[\^([^\]]+)\]/g, (_, key) => refs ? `<button class="note-ref" data-note="${escapeHtml(key)}" aria-label="Przypis ${noteKeys.indexOf(key)+1}">${noteKeys.indexOf(key)+1}</button>` : '');
const paragraphs = s => s.split(/\n\s*\n/).map(p => `<p>${inline(p)}</p>`).join('');
const announce = text => {
 const status=document.getElementById('status');document.getElementById('status-live').textContent=text;
 status.style.animation='none';status.textContent=text;
 if(typeof status.showPopover==='function'){if(status.matches(':popover-open'))status.hidePopover();status.showPopover()}else status.removeAttribute('popover');
 void status.offsetWidth;status.style.animation='';
};
const button = (name, label, attr='') => `<button class="tool" ${attr}>${icon(name)}<span>${label}</span></button>`;
const pdfLink = (className='') => {const url=catalog.find(d=>d.slug===data.slug)?.pdfUrl;return typeof url==='string'&&/^https:\/\/drive\.google\.com\/file\/d\/[A-Za-z0-9_-]+\/view(?:\?usp=drivesdk)?$/.test(url)?`<a class="${className}" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" data-pdf-link>PDF · ${escapeHtml(data.revision)} <span class="pdf-location">na Dysku Google</span></a>`:'';};
const sizeControls = () => `<div class="size-controls" role="group" aria-label="Wielkość tekstu"><button type="button" class="tool" id="smaller" data-size-step="-2" aria-label="Zmniejsz tekst">${icon('minus')}</button><output id="size-output" data-size-output aria-label="Wielkość tekstu">22 px</output><button type="button" class="tool" id="larger" data-size-step="2" aria-label="Powiększ tekst">${icon('plus')}</button></div>`;

const appearanceFields = [
 ['reading-leading','readingLeading','Interlinia','standard',[['compact','Zwarta','leadingCompact'],['standard','Standardowa','leadingStandard'],['loose','Luźna','leadingLoose']]],
 ['reading-margins','readingMargins','Marginesy','standard',[['narrow','Wąskie','marginsNarrow'],['standard','Standardowe','marginsStandard'],['wide','Szerokie','marginsWide']]],
 ['reading-weight','readingWeight','Pismo','normal',[['normal','Zwykłe','typeNormal'],['strong','Wzmocnione','typeStrong']]],
 ['book-mode','bookMode','Sposób składu','classic',[['classic','Klasyczny — justowanie','alignJustify'],['free','Swobodny — do lewej','alignStart']]]
];
const appearanceRow = (id,title,options) => `<section class="appearance-row"><h3 id="${id}-title">${title}</h3><div id="${id}" class="appearance-options" role="radiogroup" aria-labelledby="${id}-title" ${id==='book-layout-choice'?'aria-describedby="book-layout-hint"':''} style="--count:${options.length}">${options.map(([value,label,image])=>`<label class="appearance-option" title="${label}"><input type="radio" name="${id}" id="${id==='book-layout-choice'?(value==='on'?'book-layout':'book-layout-off'):id+'-'+value}" value="${value}" aria-label="${label}" ${value==='off'?'checked':''}>${icon(image)}<span class="appearance-selected">${icon('check')}</span></label>`).join('')}</div></section>`;
const appearanceRows = () => appearanceFields.map(([id,,title,,options],index)=>(index===3?appearanceRow('book-layout-choice','Skład książkowy',[['off','Wyłączony — zwykły tekst','plainText'],['on','Włączony — skład książkowy','bookText']]):'')+appearanceRow(id,title,options)).join('');

function library() {
 return `<div class="library-inner"><div class="library-drawer-heading"><a class="brand" href="index.html"><img class="brand-mark" src="assets/tipitaka-pl-gold.svg" alt="" title="Tipitaka PL" width="44" height="44"><span>SuttaFlow<span class="brand-sub">Twoja czytelnia</span></span></a><button type="button" class="icon-button" data-close-drawer aria-label="Zamknij bibliotekę">${icon('close')}</button></div>
 <button class="side-search" data-open-search>${icon('search')}<span>Szukaj w tekstach</span><kbd>/</kbd></button>
 <nav class="library-nav" aria-label="Biblioteka"><a class="side-link library-home-link" href="index.html">${icon('arrow')}Spis wszystkich tekstów</a><button class="side-link selected" data-library-view="all">${icon('book')}Biblioteka<span class="nav-count">${catalog.length}</span></button><button class="side-link" data-library-view="saved">${icon('bookmark')}Zakładki<span class="nav-count saved-count">0</span></button></nav>
 <div class="collection-heading">Zbiory</div><nav class="collections" aria-label="Zbiory tekstów">${[['DN','Dīgha Nikāya'],['MN','Majjhima Nikāya'],['SN','Saṃyutta Nikāya'],['AN','Aṅguttara Nikāya'],['KN','Khuddaka Nikāya'],['Vinaya','Vinaya']].map(([code,name])=>`<button class="collection ${code===currentCollection?'current':''}" data-collection="${code}"><span class="collection-code">${code==='Vinaya'?'Vin':code}</span><span>${name}</span><span class="collection-count">${catalog.filter(d=>d.collection===code).length}</span></button>`).join('')}</nav>
 <div class="library-list"><div class="collection-heading">Teksty do czytania</div>${catalog.map(d=>`<a class="current-sutta catalog-entry ${d.slug===data.slug?'is-current':''}" href="b.html?tekst=${encodeURIComponent(d.slug)}" data-catalog-group="${escapeHtml(d.collection)}" ${d.collection!==currentCollection?'hidden':''}><span>${escapeHtml(d.code)}</span><strong>${escapeHtml(d.title)}</strong><span class="sutta-pali">${escapeHtml(d.paliTitle)}</span></a>`).join('')}<p class="empty-collection" ${catalog.some(d=>d.collection===currentCollection)?'hidden':''}>Brak zaimportowanych tekstów w tym zbiorze.</p></div>
 <div class="side-bottom"><img class="brand-mark" src="assets/tipitaka-pl-gold.svg" alt="" title="Tipitaka PL" width="44" height="44"><span>Czytelnia SuttaFlow<br><span>Sutty i Vinaya</span></span></div></div>`;
}

function renderApparatusSections() {
 const template=document.createElement('template');template.innerHTML=data.apparatusHtml;
 const headings=[...template.content.querySelectorAll('h2,h3')].filter(h=>h.tagName==='H2'||['Decyzje tłumaczeniowe','Metryka przekładu'].includes(h.textContent.trim()));
 const ids={'Jak powstało to tłumaczenie':'o-przekladzie','Decyzje tłumaczeniowe':'decyzje-tlumaczeniowe','Paralele kanoniczne':'paralele-kanoniczne','Źródła':'zrodla','Metryka przekładu':'metryka','Komentarze':'komentarze'};
 return headings.map((heading,index)=>{
  const range=document.createRange();range.setStartAfter(heading);
  if(headings[index+1])range.setEndBefore(headings[index+1]);else range.setEnd(template.content,template.content.childNodes.length);
  const content=document.createElement('div');content.append(range.cloneContents());
  const title=heading.textContent.trim(),id=ids[title]||'aparat-'+index;
  return `<details id="${id}" data-apparatus-section><summary>${escapeHtml(title)}</summary><div class="apparatus-content">${content.innerHTML}${id==='o-przekladzie'?pdfLink('apparatus-pdf'):''}</div></details>`;
 }).join('');
}

function renderPolishReading() {
 const article=document.createElement('div');let paragraph=null,previous=null,quotes=0;
 const group=id=>id.match(/^(mn\d+:\d+)\./)?.[1]||id.match(/^(MvI\.6\.\d+)\./)?.[1];
 for(const [index,u]of data.units.entries()){
  if(u.beforeHtml.trim()){paragraph=null;previous=null;quotes=0;article.insertAdjacentHTML('beforeend',u.beforeHtml)}
  const content=document.createElement('template');content.innerHTML=u.plHtml;content.content.querySelectorAll('[lang="pi"],.pali-source').forEach(el=>el.remove());
  const anchor=document.createElement('span');anchor.id=u.id;anchor.dataset.unitIndex=index;
  if(!content.content.textContent.trim()){anchor.className='source-anchor';(paragraph||article).append(anchor);continue}
  const first=content.content.firstElementChild,simple=content.content.children.length===1&&first.tagName==='P'&&!first.querySelector('br');
  if(!simple){paragraph=null;previous=null;quotes=0;const block=document.createElement('section');block.className='unit prose-block';block.id=u.id;block.dataset.unitIndex=index;block.innerHTML='<div class="polish" lang="pl">'+content.innerHTML+'</div>';article.append(block);continue}
  const clean=first.cloneNode(true);clean.querySelectorAll('.note-ref').forEach(el=>el.remove());const text=clean.textContent.trim();
  const continuation=previous&&(!/[.!?…][”»’"')\]]*$/.test(previous.text)||/^\p{Ll}/u.test(text));
  const sameGroup=previous&&group(u.id)&&group(u.id)===group(previous.id);
  const speech=/^[—–]\s/.test(text)||(/^[„“«]/.test(text)&&quotes===0&&!previous?.text.endsWith(':'));
  const boundary=previous&&quotes===0&&(/[”»][.!?…]?$/.test(previous.text)||previous.text.endsWith('?')||/^(To także|Także to),/.test(text));
  if(!paragraph||speech||(!continuation&&(!sameGroup||boundary))){paragraph=document.createElement('p');paragraph.className='reading-paragraph';paragraph.lang='pl';article.append(paragraph)}
  else paragraph.append(document.createTextNode(' '));
  anchor.className='unit reading-unit';const polish=document.createElement('span');polish.className='polish';polish.lang='pl';polish.innerHTML=first.innerHTML;anchor.append(polish);paragraph.append(anchor);
  for(const char of text){if('„“«'.includes(char))quotes++;else if('”»'.includes(char))quotes=Math.max(0,quotes-1)}
  previous={id:u.id,text};
 }
 article.insertAdjacentHTML('beforeend',data.afterHtml);return article.innerHTML;
}

function renderReading(parallel) {
 if(!parallel)return renderPolishReading();
 return data.units.map((u,i)=>`${u.beforeHtml}<section class="unit" id="${escapeHtml(u.id)}" data-unit-index="${i}"><a class="unit-number" href="#${escapeHtml(u.id)}" aria-label="Link do fragmentu ${i+1}">${i+1}</a><div class="polish" lang="pl">${u.plHtml}</div><p class="pali" lang="pi">${escapeHtml(u.pi)}</p><button class="unit-bookmark" data-save="${escapeHtml(u.id)}" aria-label="Dodaj zakładkę przy fragmencie ${i+1}" aria-pressed="false">${icon('bookmark')}</button></section>`).join('')+data.afterHtml;
}

function finishPreparing(){
 const app=document.getElementById('app');document.documentElement.classList.remove('reader-preparing');app.removeAttribute('data-reader-preparing');app.removeAttribute('aria-busy');app.inert=false;document.getElementById('reader-loading')?.remove();
}
function renderLoadError(){finishPreparing();document.getElementById('app').innerHTML='<div class="loading-message"><p>Nie udało się otworzyć tekstu. Odśwież stronę lub wróć do biblioteki.</p><a href="index.html">Otwórz bibliotekę</a></div>'}
function render() {
 const app=document.getElementById('app');document.documentElement.classList.add('reader-preparing');app.setAttribute('data-reader-preparing','');app.setAttribute('aria-busy','true');app.inert=true;
 const loading=document.createElement('p');loading.id='reader-loading';loading.className='loading-message';loading.setAttribute('role','status');loading.textContent='Przygotowywanie tekstu…';document.body.append(loading);
 const a = variant === 'a';
 document.getElementById('app').innerHTML = `
 ${a ? `<aside class="sidebar">${library()}</aside>`:''}
 <div class="workspace">
 <header class="topbar">
 ${a ? `<div class="top-location"><button class="icon-button mobile-nav" data-drawer="library-drawer" aria-label="Otwórz bibliotekę">${icon('menu')}</button><span class="desktop-crumb">Biblioteka <span class="crumb-slash">/</span> Saṃyutta Nikāya <span class="crumb-slash">/</span></span><strong>SN 47.13</strong></div>` : `<a class="brand brand-inline" href="index.html"><img class="brand-mark" data-theme-logo src="assets/tipitaka-pl-brown.svg" alt="" title="Tipitaka PL" width="44" height="44"><span>SuttaFlow</span></a><a class="back-library" href="index.html">${icon('arrow')}<span>Biblioteka</span></a>`}
 <div class="top-actions">${a?'<span class="private-label">'+icon('lock')+'Prywatna czytelnia</span>':`<button class="icon-button" data-open-search aria-label="Szukaj w tekstach">${icon('search')}</button><button type="button" class="icon-button theme-toggle" aria-label="Włącz ciemny motyw"><svg class="icon theme-moon" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 13A8.5 8.5 0 0 1 11 3.5 8.5 8.5 0 1 0 20.5 13Z"/></svg><svg class="icon theme-sun" aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg></button><button class="icon-button" data-drawer="bookmarks-drawer" aria-label="Otwórz zakładki">${icon('bookmark')}</button>`}<a class="compare-link" href="index.html">Porównaj A / B</a></div>
 </header>
 <main id="reading" tabindex="-1">
 <div class="reading-layout"><div class="reading-column">
 <div class="document-meta"><span>${escapeHtml(data.code)} · ${escapeHtml(data.collection==='Vinaya'?'Vinaya — Mahāvagga':({DN:'Dīgha Nikāya',MN:'Majjhima Nikāya',SN:'Saṃyutta Nikāya',AN:'Aṅguttara Nikāya',KN:'Khuddaka Nikāya'}[data.collection]))}</span><span class="edition">${escapeHtml(data.revision)}</span></div>
 <h1>${escapeHtml(data.title)}</h1><p class="pali-title" lang="pi">${escapeHtml(data.paliTitle)}</p>${pdfLink('document-pdf')}
 <div class="reading-toolbar" aria-label="Narzędzia czytania"><button class="pali-toggle" id="pali-toggle" data-pali-toggle aria-pressed="false" ${data.hasPali?'':'disabled title="Ten eksport nie zawiera przyporządkowanych fragmentów pāḷi"'}><span class="toggle-track"><span></span></span>Pokaż pāḷi</button><span class="toolbar-divider"></span><button class="tool" data-drawer="settings-drawer">${icon('settings')}<span>Wygląd tekstu</span></button><button class="bookmark-document icon-button" id="bookmark-document" aria-label="Dodaj zakładkę przy aktualnym fragmencie" aria-pressed="false">${icon('bookmark')}</button></div>
 <section class="search-panel" id="search-panel" hidden aria-label="Wyszukiwanie"><div class="panel-heading"><h2>Szukaj w bibliotece</h2><button class="icon-button" id="close-search" aria-label="Zamknij wyszukiwanie">${icon('close')}</button></div><form id="search-form" role="search"><label for="search-input">Numer, fraza lub słowo</label><div class="search-row"><input id="search-input" type="search" placeholder="np. Ānanda, schronienie, Vin Mv I.6" autocomplete="off"><button class="primary" type="submit">Szukaj</button></div><label class="check-label"><input id="search-extra" type="checkbox"> Uwzględnij pāḷi i przypisy</label></form><p class="demo-hint">Szukaj po numerze, tytule lub w polskim tekście przekładu.</p><div id="search-results" aria-live="polite"></div></section>
 <section class="introduction" aria-label="Wprowadzenie">${data.descriptionHtml}</section>
 <div class="text-start"><h2>Przekład</h2><span>Polski${icon('check')}</span></div>
 <article class="sutta-text" aria-label="Polski przekład i opcjonalny oryginał pāḷi">${renderReading(false)}</article>
 <section class="apparatus" id="interpretacja"><details><summary>Interpretacja<span>Objaśnienie treści tekstu</span></summary><div class="apparatus-content">${data.interpretationHtml}</div></details><details id="przypisy"><summary>Przypisy<span>${noteKeys.length} objaśnień do przekładu</span></summary><ol class="all-notes">${noteKeys.map((key,i)=>`<li id="note-${escapeHtml(key)}"><span class="note-id">${i+1}</span>${data.notesHtml[key]}</li>`).join('')}</ol></details>${renderApparatusSections()}</section>
 <footer class="reader-footer"><span>${escapeHtml(data.code)} · Koniec tekstu</span><a href="#reading">Wróć na początek</a></footer>
 </div>
 ${a?`<aside class="document-rail"><nav aria-label="W tej sutcie"><h2>W tej sutcie</h2><a class="rail-active" href="#reading">Przekład</a><a href="#interpretacja" data-reveal="interpretacja">Interpretacja</a><a href="#przypisy" data-reveal="przypisy">Przypisy <span>14</span></a><a href="#metryka" data-reveal="metryka">O przekładzie</a></nav><div class="rail-topics"><h2>Tematy</h2><button data-topic="nietrwałość">Nietrwałość</button><button data-topic="pomność">Pomność</button><button data-topic="schronienie">Schronienie</button></div><div class="rail-note"><span class="small-line"></span><p>„…mając Dhammę za wyspę, Dhammę za schronienie…”</p><a href="#SN4713-G20">Przejdź do fragmentu ${icon('chevron')}</a></div></aside>`:''}
 </div></main>
 ${!a?`<nav class="reading-dock" aria-label="Skróty czytania"><button data-drawer="library-drawer">${icon('menu')}<span>Biblioteka</span></button><span></span><button data-drawer="contents-drawer">${icon('list')}<span>Spis</span></button><span></span><button data-drawer="notes-drawer">${icon('note')}<span>Objaśnienia</span><span class="dock-count">${noteKeys.length}</span></button><a href="#reading" class="dock-code">${escapeHtml(data.code)}</a></nav>`:''}
 </div>
 ${!a?`<nav id="reading-topbar" class="reading-topbar is-hidden" aria-label="Narzędzia podczas czytania" aria-hidden="true" inert><div class="reading-topbar-inner"><span class="reading-sutta-name" title="${escapeHtml(data.code+' · '+data.title)}">${escapeHtml(data.code)} · ${escapeHtml(data.title)}</span><div class="reading-top-actions"><button type="button" class="reading-pali" id="reading-pali-toggle" data-pali-toggle aria-pressed="false" aria-label="Pokaż pāḷi" ${data.hasPali?'':'disabled title="Ten eksport nie zawiera przyporządkowanych fragmentów pāḷi"'}>pāḷi</button><button type="button" class="reading-appearance icon-button" data-drawer="settings-drawer" aria-label="Wygląd tekstu">${icon('settings')}</button></div></div></nav>`:''}
 <section id="library-drawer" class="drawer library-drawer" popover="auto" aria-label="Biblioteka">${library()}</section>
 <div class="reading-progress" aria-hidden="true"><span id="reading-progress-fill"></span></div>
 <section id="contents-drawer" class="drawer contents-drawer" popover="auto" aria-label="Spis treści"><div class="notes-tools"><div class="panel-heading"><h2>Spis treści</h2><button class="icon-button" data-close-drawer aria-label="Zamknij spis">${icon('close')}</button></div><p class="contents-progress">Przekład · <span id="reading-percentage">0%</span></p></div><p id="contents-hint" class="contents-hint">Ładowanie części spisu…</p><div id="contents-links"></div></section>
 <section id="settings-drawer" class="drawer settings-drawer" popover="auto" aria-label="Wygląd tekstu"><div class="panel-heading"><h2>Wygląd tekstu</h2><button class="icon-button" data-close-drawer aria-label="Zamknij ustawienia">${icon('close')}</button></div><section class="appearance-size"><h3>Wielkość tekstu</h3>${sizeControls()}</section>${appearanceRows()}<p id="book-layout-hint" class="settings-hint">Polskie dzielenie wyrazów i wcięcia akapitów w przekładzie, wprowadzeniu i objaśnieniach. Wariant klasyczny dodatkowo justuje tekst.</p><button type="button" id="reset-appearance" class="appearance-reset">${icon('resetAppearance')}<span>Przywróć domyślne</span></button><button type="button" class="text-button theme-system" data-theme-system hidden>Używaj motywu urządzenia</button><p class="demo-hint">Ustawienia zapisują się w tej przeglądarce.</p></section>
 <section id="notes-drawer" class="drawer notes-drawer" popover="auto" aria-label="Objaśnienia"><div class="notes-tools"><div class="panel-heading"><h2 id="note-title">Objaśnienia</h2><button class="icon-button" data-close-drawer aria-label="Zamknij objaśnienia">${icon('close')}</button></div></div><div id="note-body"><p>Wybierz numer przypisu przy tekście lub otwórz interpretację.</p><button class="text-button" data-show-interpretation>Interpretacja sutty ${icon('chevron')}</button><div class="note-index">${noteKeys.map((key,i)=>`<button data-note="${escapeHtml(key)}"><span>${i+1}</span>${escapeHtml(plain(data.notes[key]).slice(0,95))}…</button>`).join('')}</div></div></section>
 <section id="bookmarks-drawer" class="drawer bookmarks-drawer" popover="auto" aria-label="Twoje zakładki"><div class="panel-heading"><h2>Twoje zakładki</h2><button class="icon-button" data-close-drawer aria-label="Zamknij zakładki">${icon('close')}</button></div><div id="bookmarks-list"></div><p class="demo-hint">Zakładki zapisują się w tej przeglądarce.</p></section>
 <div id="status" class="status-message" popover="manual" aria-hidden="true"></div><div id="status-live" class="status-live" role="status" aria-live="polite" aria-atomic="true"></div>`;
 window.SuttaTheme?.sync();bind().catch(renderLoadError);
}

function openDrawer(id) {
 document.querySelectorAll('.drawer').forEach(d=>{if(d.id!==id)closeDrawer(d)});
 const d=document.getElementById(id);d.dispatchEvent(new Event('drawer-reset'));
 if (typeof d.showPopover==='function') {if(!d.matches(':popover-open'))d.showPopover();} else {d.classList.add('fallback-open');}
 if(id==='bookmarks-drawer')renderBookmarks();
 if(id==='notes-drawer'&&!activeNote)document.getElementById('note-title').textContent='Objaśnienia';
 SuttaBook.refresh(d);
 d.querySelector('button')?.focus({preventScroll:true});
}
function closeDrawer(d) {d.dispatchEvent(new Event('drawer-reset'));if(typeof d.hidePopover==='function'){if(d.matches(':popover-open'))d.hidePopover();}d.classList.remove('fallback-open');}
function bindDrawerGestures(){
 const mobile=matchMedia('(max-width:800px)'),reduced=matchMedia('(prefers-reduced-motion:reduce)'),selected=()=>getSelection()?.isCollapsed===false;
 document.querySelectorAll('.drawer').forEach(drawer=>{
  const direction=drawer.classList.contains('library-drawer')?-1:1;let gesture=null,timer,frame=0,offset=0;
  const paint=()=>{frame=0;drawer.style.transform=`translate3d(${offset}px,0,0)`};
  const reset=()=>{clearTimeout(timer);cancelAnimationFrame(frame);frame=0;gesture=null;drawer.classList.remove('drawer-gesture','is-dragging');drawer.style.removeProperty('transform')};
  function settle(close){
   clearTimeout(timer);if(!drawer.classList.contains('drawer-gesture'))return;
   if(frame){cancelAnimationFrame(frame);paint()}
   drawer.classList.remove('is-dragging');void drawer.offsetWidth;
   offset=close?direction*drawer.offsetWidth:0;paint();
   if(close)timer=setTimeout(()=>closeDrawer(drawer),reduced.matches?0:200);
  }
  drawer.addEventListener('drawer-reset',reset);
  drawer.addEventListener('toggle',event=>{if(event.newState==='closed')reset()});
  drawer.addEventListener('pointerdown',event=>{
   gesture=null;
   if(!mobile.matches||event.pointerType!=='touch')return;
   if(!event.isPrimary||selected()||event.target.closest('button,a,input,select,textarea,label,summary,[contenteditable],[role="button"],[role="slider"]')){settle(false);return}
   clearTimeout(timer);const transform=getComputedStyle(drawer).transform,base=drawer.classList.contains('drawer-gesture')&&transform!=='none'?new DOMMatrixReadOnly(transform).m41:0;
   const width=drawer.offsetWidth;
   if(drawer.classList.contains('drawer-gesture')){cancelAnimationFrame(frame);drawer.classList.add('is-dragging');offset=base;paint()}
   gesture={id:event.pointerId,x:event.clientX,y:event.clientY,base,width};
  },{passive:true});
  drawer.addEventListener('pointermove',event=>{
   if(!gesture||gesture.id!==event.pointerId)return;
   const dx=event.clientX-gesture.x,dy=Math.abs(event.clientY-gesture.y);
   if(selected()||(dy>12&&dy>Math.abs(dx))){gesture=null;settle(false);return}
   if(Math.abs(dx)>8&&Math.abs(dx)>dy*1.6){drawer.classList.add('drawer-gesture','is-dragging');offset=Math.max(0,Math.min(gesture.width,(gesture.base+dx)*direction))*direction;if(!frame)frame=requestAnimationFrame(paint)}
  },{passive:true});
  drawer.addEventListener('pointercancel',()=>{gesture=null;settle(false)},{passive:true});
  drawer.addEventListener('pointerup',event=>{
   const start=gesture;gesture=null;if(!start||start.id!==event.pointerId)return;
   const dx=event.clientX-start.x,dy=event.clientY-start.y,close=mobile.matches&&!selected()&&(start.base+dx)*direction>=64&&Math.abs(dx)>Math.abs(dy)*1.6;
   if(close&&!drawer.classList.contains('drawer-gesture')){drawer.classList.add('drawer-gesture');offset=0;paint()}
   settle(close);
  },{passive:true});
 });
}
function openSearch() {document.querySelectorAll('.drawer').forEach(closeDrawer);document.getElementById('search-panel').hidden=false;document.getElementById('search-panel').scrollIntoView({block:'start'});document.getElementById('search-input').focus({preventScroll:true});}
function updateSaved() {
 document.querySelectorAll('[data-save]').forEach(b=>{const yes=saved.some(s=>s.slug===data.slug&&s.id===b.dataset.save);b.setAttribute('aria-pressed',String(yes));b.setAttribute('aria-label',`${yes?'Usuń':'Dodaj'} zakładkę przy fragmencie ${Number(b.closest('.unit').dataset.unitIndex)+1}`)});
 document.querySelectorAll('.saved-count').forEach(el=>el.textContent=saved.length);
 const current=closestUnit(); document.getElementById('bookmark-document').setAttribute('aria-pressed',String(saved.some(s=>s.slug===data.slug&&s.id===current)));
}
function closestUnit() {return [...document.querySelectorAll('.unit')].find(u=>u.getBoundingClientRect().bottom>80)?.id || data.units.at(-1).id;}
function toggleSaved(id) {const found=saved.some(s=>s.slug===data.slug&&s.id===id),u=data.units.find(u=>u.id===id);if(!u)return;saved=found?saved.filter(s=>!(s.slug===data.slug&&s.id===id)):[...saved,{slug:data.slug,id,quote:u.pl.slice(0,170)}];saveStorage('sf-reader-library-bookmarks',saved);updateSaved();announce(found?'Usunięto zakładkę.':'Dodano zakładkę.');renderBookmarks();}
function renderBookmarks(){document.getElementById('bookmarks-list').innerHTML=saved.length?saved.map(s=>{const doc=catalog.find(d=>d.slug===s.slug);return `<a class="saved-result" data-close-drawer href="b.html?tekst=${encodeURIComponent(s.slug)}#${encodeURIComponent(s.id)}"><span>${escapeHtml(doc.code)} · ${escapeHtml(doc.title)}</span><p>${escapeHtml(s.quote)}…</p></a>`}).join(''):'<p class="empty-state">Nie masz jeszcze zakładek. Użyj symbolu zakładki przy wybranym fragmencie, aby do niego wrócić.</p>';}
const loadDocument=slug=>SuttaLibrary.loadDocument(slug);
async function search(query, extra=false, forceText=false) {
 const version=++searchVersion;
 const norm=s=>plain(s).normalize('NFD').replace(/\p{M}/gu,'').replace(/ł/g,'l').replace(/Ł/g,'L').toLowerCase();
 const q=norm(query.trim()); const results=document.getElementById('search-results');
 if(!q){results.innerHTML='<p>Wpisz numer sutty, słowo lub frazę.</p>';return;}
 results.innerHTML='<p>Przeszukiwanie biblioteki…</p>';
 let found;
 try{found=await SuttaLibrary.lookup(catalog,query,extra,forceText)}
 catch{if(version===searchVersion)results.textContent='Nie udało się przeszukać biblioteki. Spróbuj ponownie.';return}
 if(version!==searchVersion)return;
 const {matches,titlesOnly}=found;
 results.innerHTML=`<p class="result-count">Znaleziono: ${matches.length}${matches.length>30?' · pierwszych 30 wyników':''}</p>`+(matches.length?'<ul class="catalog-list">'+matches.slice(0,30).map(SuttaCatalog.searchRows(catalog,'search-result')).join('')+'</ul>':'')+(!matches.length?'<p class="empty-state">Brak pasujących fragmentów. Spróbuj krótszej frazy albo uwzględnij pāḷi i przypisy.</p>':'');
 if(titlesOnly){
  const button=document.createElement('button');button.type='button';button.className='text-button';
  button.textContent='Szukaj też w treści';button.onclick=()=>search(query,extra,true);results.append(button);
 }
}
function notesOverview(){activeNote=null;document.getElementById('note-title').textContent='Objaśnienia';document.getElementById('note-body').innerHTML='<p>Wybierz przypis lub otwórz interpretację tekstu.</p><button class="text-button" data-show-interpretation>Interpretacja '+icon('chevron')+'</button><div class="note-index">'+noteKeys.map((key,i)=>`<button data-note="${escapeHtml(key)}"><span>${i+1}</span>${escapeHtml(data.notes[key].slice(0,95))}…</button>`).join('')+'</div>';}
function bindReadingBars(){
 const bar=document.getElementById('reading-topbar'),dock=document.querySelector('.reading-dock');if(!bar||!dock)return change=>SuttaPosition.preserve(change);
 let lastScroll=scrollY,anchor=scrollY,direction=0,show=false,pastTools=false,reflow=0;
 const sync=()=>{
  const visible=bar.contains(document.activeElement)||(pastTools&&show);
  bar.classList.toggle('is-hidden',!visible);bar.inert=!visible;bar.setAttribute('aria-hidden',String(!visible));
  dock.classList.toggle('is-hidden',!show&&scrollY>100&&!dock.contains(document.activeElement));
 };
 new IntersectionObserver(([entry])=>{pastTools=entry.boundingClientRect.bottom<0;sync()}).observe(document.querySelector('.reading-toolbar'));
 addEventListener('scroll',()=>{
  const y=Math.max(0,scrollY),delta=y-lastScroll;lastScroll=y;
  if(reflow||!SuttaPosition.ready||SuttaPosition.busy){anchor=y;direction=0;return}
  const next=Math.sign(delta);if(!next)return;
  if(next!==direction){direction=next;anchor=y-delta}
  if(y<=100||Math.abs(y-anchor)>=12){show=next<0;anchor=y;sync()}
 },{passive:true});
 bar.addEventListener('focusout',()=>requestAnimationFrame(sync));dock.addEventListener('focusout',()=>requestAnimationFrame(sync));sync();
 // Layout restoration is not a reading gesture, including its deferred scroll event.
 return async change=>{
  reflow++;try{return await SuttaPosition.preserve(change)}finally{
   await new Promise(resolve=>requestAnimationFrame(resolve));lastScroll=anchor=Math.max(0,scrollY);direction=0;reflow--;
  }
 };
}
async function bind(){
 // A missing font uses the existing serif fallback.
 const fontReady=document.fonts.load("22px 'Source Serif'").catch(()=>[]);
 bindDrawerGestures();const preserveReading=bindReadingBars();
 document.getElementById('status').addEventListener('animationend',event=>{const status=event.currentTarget;if(typeof status.hidePopover==='function'&&status.matches(':popover-open'))status.hidePopover()});
 const rawSaved=readStorage('sf-reader-library-bookmarks',[]);saved=Array.isArray(rawSaved)?rawSaved.filter(s=>s&&catalog.some(d=>d.slug===s.slug)&&typeof s.id==='string'&&typeof s.quote==='string'):[];
 if(data.previousUnitIds){
  const seen=new Set();
  saved=saved.flatMap(bookmark=>{
   if(bookmark.slug!==data.slug)return [bookmark];
   const id=SuttaLibrary.resolveUnitId(data,bookmark.id);
   if(seen.has(id))return [];
   seen.add(id);
   if(id===bookmark.id)return [bookmark];
   const unit=data.units.find(unit=>unit.id===id);
   return [{...bookmark,id,quote:unit.pl.slice(0,170)}];
  });
 }
 if(data.slug==='sn-47-13'&&!saved.length){const legacy=readStorage('sf-reader-bookmarks',[]);if(Array.isArray(legacy))for(const id of legacy){const u=data.units.find(u=>u.id===id);if(u)saved.push({slug:data.slug,id,quote:u.pl.slice(0,170)})}if(saved.length)saveStorage('sf-reader-library-bookmarks',saved)}
 let size=Math.min(30,Math.max(18,Number(readStorage('sf-reader-size',22))||22));
 const setSize=()=>{document.documentElement.style.setProperty('--reading-size',size+'px');document.querySelectorAll('[data-size-output]').forEach(o=>o.textContent=size+' px');document.querySelectorAll('[data-size-step]').forEach(b=>b.disabled=Number(b.dataset.sizeStep)<0?size<=18:size>=30);};setSize();
 document.querySelectorAll('[data-size-step]').forEach(b=>b.onclick=()=>preserveReading(()=>{size=Math.min(30,Math.max(18,size+Number(b.dataset.sizeStep)));setSize();saveStorage('sf-reader-size',size)}));
 const applyAppearance=()=>{for(const [id,attribute]of appearanceFields)document.body.dataset[attribute]=document.querySelector(`input[name="${id}"]:checked`).value;document.body.classList.toggle('wide-lines',document.body.dataset.readingMargins==='narrow')};
 for(const [id,,title,defaultValue,options]of appearanceFields){
  const fallback=id==='reading-margins'&&readStorage('sf-reader-wide-lines',false)?'narrow':defaultValue,stored=readStorage('sf-reader-'+id,fallback),value=options.some(o=>o[0]===stored)?stored:fallback;
  document.getElementById(id+'-'+value).checked=true;
  document.getElementById(id).onchange=()=>preserveReading(()=>{applyAppearance();saveStorage('sf-reader-'+id,document.querySelector(`input[name="${id}"]:checked`).value)});
 }
 applyAppearance();
 let layoutReady=Promise.resolve();
 const book=document.getElementById('book-layout'),bookOff=document.getElementById('book-layout-off'),mode=document.getElementById('book-mode');book.checked=Boolean(readStorage('sf-reader-book-layout',false));
 const syncBookMode=()=>{mode.setAttribute('aria-disabled',String(!book.checked));mode.closest('.appearance-row').classList.toggle('is-disabled',!book.checked);mode.querySelectorAll('input').forEach(input=>input.disabled=!book.checked)};
 book.onchange=bookOff.onchange=()=>layoutReady=preserveReading(async()=>{const enabled=book.checked;syncBookMode();try{await SuttaBook.setEnabled(enabled);if(book.checked===enabled)saveStorage('sf-reader-book-layout',enabled)}catch{if(book.checked!==enabled)return;bookOff.checked=true;syncBookMode();saveStorage('sf-reader-book-layout',false);announce('Nie udało się pobrać polskich wzorców dzielenia. Sprawdź połączenie i spróbuj ponownie.')}});
 if(book.checked)book.onchange();
 syncBookMode();
 document.getElementById('reset-appearance').onclick=()=>preserveReading(async()=>{
  size=22;setSize();saveStorage('sf-reader-size',size);
  for(const [id,,,value]of appearanceFields){document.getElementById(id+'-'+value).checked=true;saveStorage('sf-reader-'+id,value)}
  applyAppearance();bookOff.checked=true;await book.onchange();document.getElementById('status-live').textContent='Przywrócono domyślny wygląd tekstu.';
 });
 document.querySelectorAll('[data-pali-toggle]').forEach(toggle=>toggle.onclick=e=>preserveReading(async()=>{const on=e.currentTarget.getAttribute('aria-pressed')!=='true';document.querySelectorAll('[data-pali-toggle]').forEach(button=>{button.setAttribute('aria-pressed',String(on));button.setAttribute('aria-label',on?'Ukryj pāḷi':'Pokaż pāḷi')});SuttaBook.reset();document.querySelector('.sutta-text').innerHTML=renderReading(on);if(book.checked)await book.onchange();updateSaved();saveStorage('sf-reader-pali',on);if(SuttaPosition.ready)announce(on?'Włączono pāḷi, numerację i zakładki przy fragmentach.':'Włączono sam polski tekst.')}));
 if(data.hasPali&&readStorage('sf-reader-pali',false))document.getElementById('pali-toggle').click();
 document.getElementById('bookmark-document').onclick=()=>toggleSaved(closestUnit());
 document.getElementById('search-form').onsubmit=e=>{e.preventDefault();search(document.getElementById('search-input').value,document.getElementById('search-extra').checked).catch(()=>{document.getElementById('search-results').textContent='Nie udało się odczytać części biblioteki. Spróbuj ponownie.'})};
 document.getElementById('close-search').onclick=()=>{document.getElementById('search-panel').hidden=true;document.querySelector('[data-open-search]')?.focus()};
 document.addEventListener('click',e=>{
  const b=e.target.closest('[data-drawer],[data-close-drawer],[data-open-search],[data-save],[data-note],[data-reveal],[data-library-view],[data-collection],[data-topic],[data-show-interpretation]');if(!b)return;
  if(b.dataset.drawer){if(b.dataset.drawer==='notes-drawer')notesOverview();openDrawer(b.dataset.drawer)}
  if(b.hasAttribute('data-close-drawer'))document.querySelectorAll('.drawer').forEach(closeDrawer);
  if(b.hasAttribute('data-open-search'))openSearch();
  if(b.dataset.save)toggleSaved(b.dataset.save);
  if(b.dataset.note){activeNote=b.dataset.note;if(!data.notesHtml[activeNote])return;document.getElementById('note-title').textContent='Przypis '+(noteKeys.indexOf(activeNote)+1);document.getElementById('note-body').innerHTML='<button class="notes-return" data-note-overview>'+icon('arrow')+'Wszystkie objaśnienia</button>'+data.notesHtml[activeNote]+'<p class="note-source">'+escapeHtml(data.code)+' · '+escapeHtml(data.revision)+'</p>';openDrawer('notes-drawer');}
  if(b.dataset.reveal){const section=document.getElementById(b.dataset.reveal);(section.matches('details')?section:section.querySelector('details'))?.setAttribute('open','');}
  if(b.dataset.libraryView==='saved')openDrawer('bookmarks-drawer');
  if(b.dataset.libraryView==='all'){document.querySelectorAll('.catalog-entry').forEach(el=>el.hidden=false);document.querySelectorAll('.empty-collection').forEach(el=>el.hidden=true);openDrawer('library-drawer')}
  if(b.dataset.collection){currentCollection=b.dataset.collection;document.querySelectorAll('[data-collection]').forEach(el=>el.classList.toggle('current',el.dataset.collection===currentCollection));document.querySelectorAll('.catalog-entry').forEach(el=>el.hidden=el.dataset.catalogGroup!==currentCollection);document.querySelectorAll('.empty-collection').forEach(el=>el.hidden=catalog.some(d=>d.collection===currentCollection));}
  if(b.dataset.topic){openSearch();const topicMap={'nietrwałość':'rozpad','pomność':'pomności','schronienie':'schronienie'};document.getElementById('search-input').value=topicMap[b.dataset.topic];search(topicMap[b.dataset.topic],false,true);}
  if(b.hasAttribute('data-show-interpretation')){document.getElementById('note-title').textContent='Interpretacja';document.getElementById('note-body').innerHTML='<button class="notes-return" data-note-overview>'+icon('arrow')+'Wszystkie objaśnienia</button>'+data.interpretationHtml;SuttaBook.refresh(document.getElementById('note-body'));}
 });
 document.addEventListener('click',e=>{if(e.target.closest('[data-note-overview]'))notesOverview()});
 document.addEventListener('keydown',e=>{if(e.key==='/'&&!/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName)){e.preventDefault();openSearch()}if(e.key==='Escape'){document.querySelectorAll('.fallback-open').forEach(closeDrawer)}});
 let savedTimer;addEventListener('scroll',()=>{clearTimeout(savedTimer);savedTimer=setTimeout(updateSaved,200)},{passive:true});
 await Promise.all([layoutReady,fontReady]);await document.fonts.ready;document.documentElement.classList.remove('reader-preparing');await SuttaPosition.init(data);finishPreparing();await SuttaNavigation.init(data);
 updateSaved();
}
document.getElementById('app').innerHTML='<p class="loading-message" role="status">Otwieranie tekstu…</p>';
SuttaLibrary.getCatalog().then(async list=>{catalog=list;const selected=new URLSearchParams(location.search).get('tekst')||'sn-47-13';if(!catalog.some(d=>d.slug===selected))throw Error('Nieznany tekst');data=await loadDocument(selected);currentCollection=data.collection;document.title=data.title+' — Czytelnia SuttaFlow';noteKeys=Object.keys(data.notes);render()}).catch(renderLoadError);
