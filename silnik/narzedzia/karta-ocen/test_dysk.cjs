// Real UI -> loopback -> isolated disk JSON; never writes owner choices.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const {spawn}=require('node:child_process');
const {chromium}=require('playwright');
const repo=path.resolve(__dirname,'../..');
const model=JSON.parse(fs.readFileSync(path.join(__dirname,'karta.html'),'utf8').match(/id="sf-card-model">([\s\S]*?)<\/script>/)[1]);
fs.mkdirSync(path.join(repo,'build/tmp'),{recursive:true});
const task=fs.mkdtempSync(path.join(repo,'build/tmp/karta-test-'));
const fixture=fs.mkdtempSync(path.join(task,'.test-disk-ui-'));
const actual=path.join(__dirname,'test-fixture.json'), target=path.join(fixture,model.decision_path);
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const protectedFiles=[actual,path.join(repo,model.source_path),path.join(repo,model.source_path.replace(/\.md$/,'.pdf')),
  path.join(repo,'docs/standards/2.1.0/RULE_REGISTRY.json'),path.join(repo,'prace/20261024-mn53-terminologia/rejestr/RULE_REGISTRY.json')].filter(p=>fs.existsSync(p));
const before=protectedFiles.map(hash);
fs.mkdirSync(path.dirname(target),{recursive:true});
fs.mkdirSync(path.dirname(path.join(fixture,model.source_path)),{recursive:true});
fs.copyFileSync(actual,target);
fs.copyFileSync(path.join(repo,model.source_path),path.join(fixture,model.source_path));
const python='python';
let child,browser;
async function start() {
  child=spawn(python,['-u','-c',
    'import sys; from pathlib import Path; sys.path.insert(0,sys.argv[1]); import autozapis; s=autozapis.make_server(Path(sys.argv[1])/"karta.html",Path(sys.argv[2])); print(s.card_url,flush=True); s.serve_forever()',
    __dirname,fixture],{env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  return await new Promise((resolve,reject)=>{
    let out='',errors='';
    const timeout=setTimeout(()=>reject(Error('Server startup timeout: '+errors)),10000);
    child.stderr.on('data',x=>{errors+=x;});
    child.once('exit',code=>{clearTimeout(timeout);reject(Error('Server exit '+code+': '+errors));});
    child.stdout.on('data',x=>{out+=x;if(out.includes('\n')){clearTimeout(timeout);resolve(out.trim());}});
  });
}
async function stop() {
  if (child && child.exitCode===null) await new Promise(resolve=>{child.once('exit',resolve);child.kill();});
}
const read=()=>JSON.parse(fs.readFileSync(target));
async function until(check) {
  const end=Date.now()+10000;
  while(Date.now()<end){if(check())return;await new Promise(resolve=>setTimeout(resolve,40));}
  throw Error('Disk condition timed out');
}
(async()=>{
  let url=await start();
  browser=await chromium.launch({channel:'chrome',headless:true});
  const page=await browser.newPage();
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  const q=s=>page.locator('#sf-'+s);
  assert.equal(await q('progress').textContent(),'Wybory: 10 z 10');
  assert.equal(hash(actual),hash(target)); // Opening is read-only, all original bytes retained.
  await q('issue').selectOption('3');
  assert.equal(await q('comment').inputValue(),read().issues[3].comment);
  await q('issue').selectOption('6');
  assert.equal(await page.locator('input[value="B"]').isChecked(),true);
  await q('issue').selectOption('0');
  await page.locator('input[value="CUSTOM"]').check();
  await until(()=>read().issues[0].option==='CUSTOM'); // Incomplete custom is still saved.
  await q('custom-text').fill('  szkic <script>bez wykonania</script>  ');
  await q('custom-scope').selectOption('paragraph');
  await q('comment').fill('pierwszy');
  await q('comment').fill('ostatni komentarz');
  await until(()=>read().draft?.choices['MN53-S01'].comment==='ostatni komentarz');
  assert.equal(read().draft.choices['MN53-S01'].text,'  szkic <script>bez wykonania</script>  ');
  assert.equal(read().draft.choices['MN53-S01'].preview_scope,'paragraph');
  assert.equal(read().issues[6].option,'B');
  assert.equal(read().issues[3].comment,JSON.parse(fs.readFileSync(actual)).issues[3].comment);
  assert.equal(hash(target.replace(/\.json$/,'.przed-autozapisem.json')),hash(actual));
  await page.waitForFunction(()=>document.getElementById('sf-storage').textContent.startsWith('Zapisano automatycznie JSON'));
  await stop();url=await start();await page.goto(url);
  assert.equal(await q('custom-text').inputValue(),'  szkic <script>bez wykonania</script>  ');
  assert.equal(await q('custom-scope').inputValue(),'paragraph');
  assert.equal(await q('comment').inputValue(),'ostatni komentarz');
  const endpoint=url+'save';
  const origin=new URL(url).origin;
  assert.equal((await fetch(endpoint,{method:'POST',headers:{'Origin':'https://foreign.invalid','Content-Type':'application/json'},body:'{}'})).status,403);
  assert.equal((await fetch(origin+'/arbitrary-file')).status,404);
  await page.route('**/save',route=>route.abort());
  await q('comment').fill('po awarii');
  await page.waitForFunction(()=>!document.getElementById('sf-disk-retry').hidden);
  assert.notEqual(read().issues[0].comment,'po awarii');
  page.once('dialog',dialog=>dialog.accept());
  await page.reload();
  await q('recovery').waitFor({state:'visible',timeout:3000});
  assert.equal(await q('comment').inputValue(),'ostatni komentarz');
  assert.notEqual(read().issues[0].comment,'po awarii'); // Recovery is never implicit.
  await q('recovery-export').click();
  assert.equal(JSON.parse(await q('output').inputValue()).draft.choices['MN53-S01'].comment,'po awarii');
  assert.equal(await q('comment').inputValue(),'ostatni komentarz');
  await page.unroute('**/save');
  await q('recovery-restore').focus();await page.keyboard.press('Enter');
  await until(()=>read().issues[0].comment==='po awarii');
  await page.waitForFunction(()=>document.getElementById('sf-storage').textContent.startsWith('Zapisano automatycznie JSON'));
  await page.reload();
  assert.equal(await q('recovery').isHidden(),true);
  assert.equal(await q('comment').inputValue(),'po awarii');
  const external=fs.readFileSync(target,'utf8')+' ';
  fs.writeFileSync(target,external);
  await q('comment').fill('konflikt');
  await page.waitForFunction(()=>document.getElementById('sf-storage').textContent.includes('zmienił się'));
  assert.equal(fs.readFileSync(target,'utf8'),external);
  await q('export').click();
  assert.equal(JSON.parse(await q('output').inputValue()).issues[0].comment,'konflikt');
  assert.deepEqual(errors,[]);
  assert.deepEqual(protectedFiles.map(hash),before);
  const stopped=new Promise(resolve=>child.once('exit',resolve));
  assert.equal((await fetch(url+'stop',{method:'POST',headers:{'Origin':new URL(url).origin,'Content-Type':'application/json'},body:'{}'})).status,200);
  await stopped;
  fs.writeFileSync(path.join(task,'TEST_DYSK.json'),JSON.stringify({result:'PASS',checked_at:new Date().toISOString(),
    checks:['synthetic 10 choices and S04 comment','read-only open','UI to real JSON','incomplete custom','raw draft and preview scope','rapid edits','server restart readback','original backup','foreign origin and path denied','save failure and retry','stale file conflict blocks overwrite','manual rescue export','graceful stop'],
    protected_files:protectedFiles.map((p,i)=>({path:path.relative(repo,p).replaceAll('\\','/'),sha256:before[i]})),
    graphify:'Existing map covers PDF Python modules only; query had no card matches. Card/server dependencies checked in current sources.'},null,2)+'\n');
  console.log('PASS: disk autosave, restart, recovery, conflict and protected files');
})().catch(e=>{console.error(e);process.exitCode=1;}).finally(async()=>{
  if(browser)await browser.close();await stop();
  if(path.dirname(fixture)!==task || !path.basename(fixture).startsWith('.test-disk-ui-'))throw Error('Unsafe cleanup');
  fs.rmSync(fixture,{recursive:true,force:true});
  assert.ok(path.resolve(task).startsWith(path.resolve(repo,'build/tmp')+path.sep));
  fs.rmSync(task,{recursive:true,force:true});
});
