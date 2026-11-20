// Local browser self-check; no translation edits and no network dependencies.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const repo = path.resolve(__dirname,'../..');
fs.mkdirSync(path.join(repo,'build/tmp'),{recursive:true});
const task=fs.mkdtempSync(path.join(repo,'build/tmp/karta-test-'));
const file = path.join(__dirname,'karta.html');
const source = fs.readFileSync(file,'utf8');
const model = JSON.parse(source.match(/<script type="application\/json" id="sf-card-model">([\s\S]*?)<\/script>/)[1]);
const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const full = p => path.join(repo,p);
const findings = JSON.parse(fs.readFileSync(full(model.audit_path),'utf8'));
const readerLines = fs.readFileSync(full(model.source_path),'utf8').split(/\r?\n/);
assert.equal(hash(full(model.source_path)), model.source_sha256);
assert.equal(hash(full(model.audit_path)), model.audit_sha256);
assert.equal(hash(full('docs/standards/2.1.0/RULE_REGISTRY.json')), model.standard_sha256);
assert.deepEqual(model.issues.map(i=>i.id),findings.findings.map(i=>i.id));
assert.equal(new Set(model.issues.map(i=>i.id)).size,10);
for (const issue of model.issues) {
  assert.equal(issue.quote, findings.findings.find(i=>i.id===issue.id).reader_quote);
  assert.ok(Array.isArray(issue.context) && issue.context.length > 0, `${issue.id}: full source context is required`);
  assert.ok(issue.situation.length > 0);
  assert.ok(issue.comparison,`${issue.id}: complete-paragraph preview is required`);
  for (const paragraph of issue.context) {
    const expected=readerLines[paragraph.source_line-1].replace(/^\[\^[^\]]+\]:\s*/,'').replace(/\[\^[^\]]+\]/g,'').replace(/<\/?em>/g,'').replace(/\*/g,'').trim();
    assert.equal(paragraph.text,expected,`${issue.id}: context must quote a complete source paragraph`);
  }
  assert.ok(issue.context.some(p=>p.text.includes(issue.quote)),`${issue.id}: assessed phrase must occur in its context`);
  assert.ok(issue.options.length > 0);
  assert.equal(new Set(issue.options.map(o=>o.id)).size,issue.options.length);
  assert.ok(issue.options.every(o=>!['KEEP','CUSTOM','DEFER'].includes(o.id)));
}
const auditDir = full('audyty/20261024-mn53-znaczenie-r9');
const protectedFiles = [full(model.source_path),full(model.source_path.replace(/\.md$/,'.pdf')),
  full('docs/standards/2.1.0/RULE_REGISTRY.json'),
  full('prace/20261024-mn53-terminologia/rejestr/RULE_REGISTRY.json'),
  ...fs.readdirSync(auditDir).map(p=>path.join(auditDir,p))].filter(p=>fs.existsSync(p));
const before = protectedFiles.map(p=>hash(p));
let browser, persistent, profile;
(async()=>{
  fs.mkdirSync(task,{recursive:true});
  const standalone=path.join(task,'MN53-karta-ocen.html');
  const wrapper='<!doctype html><html lang="pl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MN53 · karta ocen</title><style>html{color-scheme:light dark;background:light-dark(#e8eef0,#10161a)}body{margin:0;padding:24px 0}@media(max-width:600px){body{padding:0}}</style></head><body>';
  fs.writeFileSync(standalone,wrapper+source+'</body></html>','utf8');
  browser = await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage({viewport:{width:1040,height:1000},colorScheme:'light',acceptDownloads:true});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(standalone).href);
  const q=s=>page.locator('#sf-'+s);
  assert.equal(await q('decision-path').textContent(),'prace/20261024-mn53-terminologia/karta-ocen/MN53-R9-wybory.json');
  assert.equal(await q('issue').locator('option').count(),10);
  assert.equal(await page.locator('input:checked').count(),0);
  assert.equal(await q('progress').textContent(),'Wybory: 0 z 10');
  for (let i=0;i<10;i++) {
    await q('issue').selectOption(String(i));
    assert.equal(await q('quote').textContent(),model.issues[i].quote);
    assert.equal(await q('pali').textContent(),model.issues[i].pali);
    assert.equal(await q('reading').isVisible(),true);
    assert.deepEqual(await q('reading').locator('.sf-passage-text').allTextContents(),model.issues[i].context.map(p=>p.text));
    assert.ok(await q('reading').locator('mark').count()>0);
    assert.ok((await q('reading').locator('mark').allTextContents()).every(t=>t===model.issues[i].quote));
    assert.equal(await page.locator('input:checked').count(),0);
  }
  await q('issue').selectOption('0');
  await page.locator('input[value=A]').check();
  assert.equal(await q('comparison').isVisible(),true);
  assert.ok((await q('chosen-passage').textContent()).endsWith('Rozpoznaje, jak istoty pojawiają się ponownie zgodnie ze swoimi czynami:'));
  assert.ok(!(await q('chosen-passage').textContent()).includes('czynami.:'));
  await q('next').click();
  await page.locator('input[value=B]').check();
  assert.ok((await q('preview-note').textContent()).includes('moralną obawę'));
  assert.equal(await q('chosen-passage').textContent(),'Obawia się złego postępowania. Obawia się złego postępowania ciałem, złego postępowania mową i złego postępowania umysłem. Obawia się popadania w złe, niekorzystne stany.');
  await q('prev').click(); assert.equal(await page.locator('input[value=A]').isChecked(),true);
  await q('next').click(); assert.equal(await page.locator('input[value=B]').isChecked(),true);
  await q('issue').selectOption('2'); await page.locator('input[value=CUSTOM]').check();
  await q('export').click(); assert.ok((await q('error').textContent()).includes('MN53-S03'));
  const malicious='<img src=x onerror="window.bad=true"> Zażółć gęślą jaźń — ṭhāna';
  await q('custom-text').fill(malicious); await q('custom-note').fill(malicious);
  await q('comment').fill('Własne objaśnienie wymaga sprawdzenia.');
  assert.equal(await q('preview-note').textContent(),malicious);
  assert.equal(await q('preview').locator('img').count(),0);
  assert.ok((await q('chosen-passage').textContent()).includes(malicious));
  assert.equal(await q('chosen-passage').locator('img').count(),0);
  await q('custom-scope').selectOption('paragraph');
  assert.equal(await q('chosen-passage').textContent(),malicious);
  await q('custom-scope').selectOption('fragment');
  await q('issue').selectOption('3'); await page.locator('input[value=DEFER]').check();
  assert.equal(await q('comparison').isHidden(),true);
  await q('issue').selectOption('4'); await page.locator('input[value=KEEP]').check();
  assert.equal(await q('chosen-passage').textContent(),await q('current-passage').textContent());
  await q('export').click();
  let exported=JSON.parse(await q('output').inputValue());
  assert.equal(exported.issues.length,10);
  assert.equal(exported.source_sha256,model.source_sha256);
  assert.equal(exported.audit_sha256,model.audit_sha256);
  assert.equal(exported.status,'DRAFT_FOR_OWNER_REVIEW');
  assert.equal(exported.approval_evidence,null);
  assert.equal(exported.issues[0].wording,model.issues[0].options[0].text);
  assert.equal(exported.issues[1].note,model.issues[1].options[1].note);
  assert.equal(exported.issues[2].wording,malicious);
  assert.equal(exported.issues[3].status,'NEEDS_CLARIFICATION');
  assert.equal(exported.issues[4].wording,model.issues[4].quote);
  assert.equal(exported.issues[5].status,'UNSELECTED');
  assert.ok(exported.issues.every(i=>i.implemented===false));
  const waiting=page.waitForEvent('download'); await q('download').click(); const download=await waiting;
  assert.equal(download.suggestedFilename(),'MN53-R9-wybory.json');
  let chunks=[]; for await (const chunk of await download.createReadStream()) chunks.push(chunk);
  assert.deepEqual(JSON.parse(Buffer.concat(chunks).toString('utf8')),exported);
  await download.delete();
  await page.locator('input[value=A]').check(); assert.equal(await q('export-panel').isHidden(),true);
  await q('issue').selectOption('9'); await page.locator('input[value=B]').check(); await q('export').click();
  exported=JSON.parse(await q('output').inputValue());
  assert.equal(exported.issues[9].note,model.issues[9].options[1].note);
  for(let i=0;i<10;i++) {
    await q('issue').selectOption(String(i));
    for(const option of model.issues[i].options) {
      await page.locator(`input[value=${option.id}]`).check();
      assert.equal(await q('comparison').isVisible(),true);
      assert.ok((await q('current-passage').textContent()).length>model.issues[i].quote.length);
      assert.ok((await q('chosen-passage').textContent()).length>model.issues[i].quote.length);
    }
  }
  await q('issue').selectOption('4'); await page.locator('input[value=A]').check();
  const firstJhana=await q('chosen-passage').textContent();
  assert.ok(firstJhana.startsWith('Szlachetny uczeń, odosobniony od zmysłowości, odosobniony od stanów niekorzystnych, osiąga pierwszą jhānę'));
  assert.equal(firstJhana.split('odosobniony od stanów niekorzystnych').length-1,1);
  assert.ok(!firstJhana.includes('…'));
  await q('issue').selectOption('5'); await page.locator('input[value=A]').check();
  assert.ok((await q('chosen-passage').textContent()).startsWith('Wraz z zanikiem tej radości przebywa w równowadze, zachowuje pomność'));
  await page.locator('input[value=B]').check();
  assert.equal(await q('chosen-passage').textContent(),await q('current-passage').textContent());
  assert.ok((await q('comparison-status').textContent()).includes('przypis'));
  await q('issue').selectOption('8'); await page.locator('input[value=A]').check();
  assert.equal(await q('chosen-passage').textContent(),model.issues[8].options[0].text);
  await q('issue').selectOption('9'); await page.locator('input[value=A]').check();
  const method=await q('chosen-passage').textContent();
  assert.ok(method.includes('Formułę boskiego oka sprawdzono także w DN 2 i MN 4.'));
  assert.ok(method.endsWith('a trudniejsze pojęcia sprawdzano w słownikach palijskich.'));
  const narrow=[];
  for (const width of [320,390,736,1040]) {
    await page.setViewportSize({width,height:1000});
    for(let i=0;i<10;i++) {
      await q('issue').selectOption(String(i));
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow at ${width}, issue ${i}`);
    }
    narrow.push(width);
  }
  // A closed page and a restarted browser must restore every kind of draft.
  profile=fs.mkdtempSync(path.join(task,'.test-autosave-'));
  persistent=await chromium.launchPersistentContext(profile,{channel:'chrome',headless:true});
  let returning=await persistent.newPage();
  await returning.goto(pathToFileURL(standalone).href);
  await returning.locator('input[value=B]').check();
  await returning.locator('#sf-comment').fill('Zachowaj sens i objaśnij.');
  await returning.locator('#sf-issue').selectOption('1');
  await returning.locator('input[value=CUSTOM]').check();
  await returning.locator('#sf-custom-text').fill('Moje brzmienie — ṭhāna');
  await returning.locator('#sf-custom-note').fill('Mój przypis.');
  await returning.locator('#sf-comment').fill('Moje pytanie.');
  await returning.locator('#sf-custom-scope').selectOption('paragraph');
  await returning.locator('#sf-issue').selectOption('2'); await returning.locator('input[value=DEFER]').check();
  await returning.locator('#sf-issue').selectOption('3'); await returning.locator('input[value=KEEP]').check();
  await returning.locator('#sf-issue').selectOption('4'); await returning.locator('#sf-comment').fill('Pytanie bez wybranego wariantu.');
  await returning.close(); returning=await persistent.newPage();
  await returning.goto(pathToFileURL(standalone).href);
  assert.equal(await returning.locator('input[value=B]').isChecked(),true,'autosave: chosen variant must survive reopening');
  assert.equal(await returning.locator('#sf-comment').inputValue(),'Zachowaj sens i objaśnij.');
  await persistent.close(); persistent=await chromium.launchPersistentContext(profile,{channel:'chrome',headless:true});
  returning=await persistent.newPage(); await returning.goto(pathToFileURL(standalone).href);
  assert.equal(await returning.locator('input[value=B]').isChecked(),true,'autosave: chosen variant must survive browser restart');
  await returning.locator('#sf-issue').selectOption('1');
  assert.equal(await returning.locator('input[value=CUSTOM]').isChecked(),true);
  assert.equal(await returning.locator('#sf-custom-text').inputValue(),'Moje brzmienie — ṭhāna');
  assert.equal(await returning.locator('#sf-custom-note').inputValue(),'Mój przypis.');
  assert.equal(await returning.locator('#sf-comment').inputValue(),'Moje pytanie.');
  assert.equal(await returning.locator('#sf-custom-scope').inputValue(),'paragraph');
  assert.equal(await returning.locator('#sf-chosen-passage').textContent(),'Moje brzmienie — ṭhāna');
  await returning.locator('#sf-issue').selectOption('2'); assert.equal(await returning.locator('input[value=DEFER]').isChecked(),true);
  await returning.locator('#sf-issue').selectOption('3'); assert.equal(await returning.locator('input[value=KEEP]').isChecked(),true);
  await returning.locator('#sf-issue').selectOption('4'); assert.equal(await returning.locator('input:checked').count(),0);
  assert.equal(await returning.locator('#sf-comment').inputValue(),'Pytanie bez wybranego wariantu.');
  await persistent.close(); persistent=undefined;
  // Host state: valid drafts restore; a different revision and unknown choices cannot.
  const host=await browser.newPage();
  const saved={card_id:model.card_id,source_sha256:model.source_sha256,choices:{[model.issues[0].id]:{option:'B',text:'',note:'',comment:'Zachowaj'} }};
  await host.addInitScript(state=>{
    Object.defineProperty(window,'localStorage',{get(){throw new DOMException('sandbox','SecurityError');}});
    window.openai={widgetState:{modelContent:state},setWidgetState:async x=>{window.lastSaved=x;}};
  },saved);
  await host.goto(pathToFileURL(standalone).href);
  assert.equal(await host.locator('input[value=B]').isChecked(),true);
  await host.evaluate(()=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:{card_id:'stara-karta',source_sha256:'stare',choices:{}}}}}})));
  assert.equal(await host.locator('input[value=B]').isChecked(),true);
  await host.evaluate(state=>{state.saved_at=new Date(Date.now()+1000).toISOString();state.choices['MN53-S01'].option='UNKNOWN'; window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:state}}}}));},saved);
  assert.equal(await host.locator('input[value=B]').isChecked(),true,'invalid restore cannot erase a valid choice');
  await host.locator('input[value=A]').check(); await host.locator('#sf-comment').fill('Świeższa decyzja.');
  await host.waitForFunction(()=>document.getElementById('sf-storage').textContent.includes('Zapisano automatycznie w tym czacie'));
  const hostDraft=await host.evaluate(()=>window.lastSaved.modelContent);
  await host.evaluate(state=>window.dispatchEvent(new CustomEvent('openai:set_globals',{detail:{globals:{widgetState:{modelContent:state}}}})),saved);
  assert.equal(await host.locator('input[value=A]').isChecked(),true,'old host state cannot overwrite a fresh edit');
  assert.equal(await host.locator('#sf-comment').inputValue(),'Świeższa decyzja.');
  const reopenedHost=await browser.newPage();
  await reopenedHost.addInitScript(state=>{
    Object.defineProperty(window,'localStorage',{get(){throw new DOMException('sandbox','SecurityError');}});
    window.openai={widgetState:{modelContent:state},setWidgetState:async()=>{}};
  },hostDraft);
  await reopenedHost.goto(pathToFileURL(standalone).href);
  assert.equal(await reopenedHost.locator('input[value=A]').isChecked(),true);
  assert.equal(await reopenedHost.locator('#sf-comment').inputValue(),'Świeższa decyzja.');
  await reopenedHost.close();
  for(let i=0;i<10;i++) {
    await host.locator('#sf-issue').selectOption(String(i)); await host.locator('input[value=CUSTOM]').check();
    await host.locator('#sf-custom-text').fill('ą'.repeat(1800));
  }
  assert.ok((await host.locator('#sf-storage').textContent()).includes('przekraczają'));
  assert.ok(await host.evaluate(()=>new TextEncoder().encode(JSON.stringify(window.lastSaved)).length<16000));
  await host.locator('#sf-export').click();
  assert.equal(JSON.parse(await host.locator('#sf-output').inputValue()).issues[9].wording.length,1800);
  await host.close();
  const denied=await browser.newPage();
  await denied.addInitScript(()=>Object.defineProperty(window,'localStorage',{get(){throw new DOMException('denied','SecurityError');}}));
  await denied.goto(pathToFileURL(standalone).href); await denied.locator('input[value=A]').check();
  assert.ok((await denied.locator('#sf-storage').textContent()).includes('Nie udało'));
  await denied.locator('#sf-export').click();
  assert.equal(JSON.parse(await denied.locator('#sf-output').inputValue()).issues[0].option,'A');
  await denied.close();
  const quota=await browser.newPage();
  await quota.addInitScript(()=>{Storage.prototype.setItem=function(){throw new DOMException('full','QuotaExceededError');};});
  await quota.goto(pathToFileURL(standalone).href); await quota.locator('input[value=B]').check();
  assert.ok((await quota.locator('#sf-storage').textContent()).includes('Nie udało'));
  assert.equal(await quota.locator('input[value=B]').isChecked(),true);
  await quota.close();
  const badHost=await browser.newPage();
  await badHost.addInitScript(()=>{
    Object.defineProperty(window,'localStorage',{get(){throw new DOMException('sandbox','SecurityError');}});
    window.openai={setWidgetState:async()=>{throw new Error('host save failed');}};
  });
  await badHost.goto(pathToFileURL(standalone).href); await badHost.locator('input[value=A]').check();
  await badHost.waitForFunction(()=>document.getElementById('sf-storage').textContent.includes('Nie udało'));
  assert.equal(await badHost.locator('input[value=A]').isChecked(),true);
  await badHost.close();
  const large=await browser.newPage();
  await large.goto(pathToFileURL(standalone).href);
  for(let i=0;i<10;i++) {
    await large.locator('#sf-issue').selectOption(String(i)); await large.locator('input[value=CUSTOM]').check();
    await large.locator('#sf-custom-text').fill('ą'.repeat(1800));
    await large.locator('#sf-custom-note').fill('ṭ'.repeat(1800));
    await large.locator('#sf-comment').fill('ź'.repeat(1200));
  }
  await large.reload();
  for(let i=0;i<10;i++) {
    await large.locator('#sf-issue').selectOption(String(i));
    assert.equal(await large.locator('#sf-custom-text').inputValue(),'ą'.repeat(1800));
    assert.equal(await large.locator('#sf-custom-note').inputValue(),'ṭ'.repeat(1800));
    assert.equal(await large.locator('#sf-comment').inputValue(),'ź'.repeat(1200));
  }
  const key=await large.evaluate(()=>Object.keys(localStorage).find(k=>k.startsWith('suttaflow:karta:')));
  await large.evaluate(key=>{const saved=JSON.parse(localStorage.getItem(key));saved.source_sha256='other-text';localStorage.setItem(key,JSON.stringify(saved));},key);
  await large.reload(); assert.equal(await large.locator('input:checked').count(),0,'different source must not inherit decisions');
  await large.evaluate(key=>localStorage.setItem(key,'invalid JSON'),key);
  await large.reload(); assert.equal(await large.locator('input:checked').count(),0);
  assert.ok((await large.locator('#sf-storage').textContent()).includes('Nie udało'));
  await large.close();
  await q('issue').focus(); await q('issue').press('Home'); await q('issue').press('ArrowDown');
  assert.equal(await q('issue').inputValue(),'1');
  await page.locator('input[value=A]').focus(); await page.locator('input[value=A]').press('Space');
  assert.equal(await page.locator('input[value=A]').isChecked(),true);
  await page.locator('input[value=A]').press('ArrowDown');
  assert.equal(await page.locator('input[value=B]').isChecked(),true);
  await page.evaluate(()=>{for(const key of Object.keys(localStorage))if(key.startsWith('suttaflow:karta:'))localStorage.removeItem(key);});
  await page.reload();
  await page.setViewportSize({width:1040,height:1000});
  await page.locator('input[value=A]').check();
  await page.screenshot({path:path.join(task,'podglad.png'),fullPage:true});
  await page.emulateMedia({colorScheme:'dark'});
  const darkColors=await q('title').evaluate(e=>({text:getComputedStyle(e).color,surface:getComputedStyle(e.closest('section')).backgroundColor}));
  assert.notEqual(darkColors.text,darkColors.surface);
  assert.deepEqual(errors,[]);
  assert.deepEqual(protectedFiles.map(p=>hash(p)),before);
  const result={status:'PASS',checks:['all_10_audit_ids_and_exact_quotes','source_audit_and_standard_pins','initially_no_owner_choices','all_issues_render','complete_R9_context_and_highlights','all_predefined_variants_in_complete_paragraphs','preview_punctuation_and_jhana_formula_preserved','preview_repeated_clauses_and_method_sources_preserved','note_only_keep_and_defer_preview','custom_fragment_or_paragraph_and_saved_scope','choices_survive_navigation','custom_variant_required','custom_text_escaped','selected_footnotes_and_dependency_scope','full_JSON_and_actual_download','no_approval_or_implementation_claim','export_invalidated_after_change','autosave_page_close_and_browser_restart','all_choice_types_and_comment_only_restored','full_size_drafts_restored_without_truncation','host_state_and_stale_revision','host_16KiB_limit_without_export_loss','storage_denied_and_quota_feedback','failed_host_save_feedback','different_source_and_corrupt_storage_ignored','responsive_320_390_736_1040','native_keyboard_selection','light_and_dark_render','no_browser_errors','protected_inputs_unchanged'],protected_file_count:protectedFiles.length,screen_widths:narrow,card_sha256:hash(file),standalone_sha256:hash(standalone),translation_review:false,graphify_scope:'Existing map covers PDF Python modules; card is outside that map. Checked current card source and browser behavior directly.',created_at:new Date().toISOString()};
  fs.writeFileSync(path.join(task,'TEST.json'),JSON.stringify(result,null,2)+'\n','utf8');
  console.log(JSON.stringify(result,null,2));
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{
  if(persistent)await persistent.close();
  if(browser)await browser.close();
  if(profile){assert.ok(path.resolve(profile).startsWith(path.resolve(task)+path.sep));fs.rmSync(profile,{recursive:true,force:true});}
  assert.ok(path.resolve(task).startsWith(path.resolve(repo,'build/tmp')+path.sep));
  fs.rmSync(task,{recursive:true,force:true});
});
