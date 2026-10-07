// Layer 5 (serial; Chromium, the viewer double, the speech double, no
// provider): the player page (the player-page change, ADR-022) in a browser,
// over live sessions run in this process on the fixture movies `count` (a
// clocked take, 10 fps) and `tour` (a posed loop with a reframe, a dissolve,
// a wipe and a fade in). The movie surface poses the frames /frame gives on
// the render's stage page, as the renderer does; the take surface poses the
// take on the viewer alone. Every proof reads what the page reports
// (window.player, provisional), the stage page's own window.film, the
// double's records, the DOM of the ruler and the readout, and the pixels of
// the stage's frame. The page's clock is driven by seeks and keys only; no
// verdict reads a wall clock.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {sharedStage,browserSession,allowLaunches} from '../support/stage.mjs';
import {fixtureMovie,takeMachine} from '../support/fixture-movie.mjs';
import {readJson} from '../project-fixture.mjs';
import {viewerDouble} from '../viewer-double.mjs';
import {live} from '../../src/live.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {speech} from '../../src/speech.mjs';
import {frameAt} from '../../src/timeline.mjs';

const VIEW='counting.view',WIDTH=640;
const OPTIONS={renderMode:'continuous',animation:'external',autoplay:false,driverControls:'none',partControls:'none'};

// No key, and any request beyond the loopback interface fails the test; the
// session's check lines are not printed.
function quiet(t){
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,log=console.log,calls=[];
  delete process.env.ELEVENLABS_API_KEY;
  globalThis.fetch=(url,...rest)=>{
    if(String(url).startsWith('http://127.0.0.1:'))return fetch(url,...rest);
    calls.push(String(url));throw new Error('A test attempted a network request');
  };
  console.log=()=>{};
  t.onTestFinished(()=>{globalThis.fetch=fetch;console.log=log;if(key!==undefined)process.env.ELEVENLABS_API_KEY=key;assert.deepEqual(calls,[]);});
}
// A live session on a fixture movie, closed after the test.
async function session(t,name,{prepare}={}){
  quiet(t);
  const movie=await fixtureMovie(t,name);
  await prepare?.(movie);
  const s=await live(movie.file,{viewer:movie.viewer,width:WIDTH});
  t.onTestFinished(()=>s.close());
  return {...movie,session:s};
}
// The player in a page of the run's Chromium, large enough that the stage's
// frame is drawn at its own size; settled once it has posed.
async function player(t,origin,hash=''){
  const {browser}=await sharedStage();
  const page=await browser.newPage({viewport:{width:1000,height:760},deviceScaleFactor:1});
  const errors=[],requests=[];
  page.on('pageerror',e=>errors.push(e.message));
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  page.on('request',r=>requests.push(new URL(r.url()).pathname));
  t.onTestFinished(()=>page.close());
  await page.goto(`${origin}/${hash}`);
  await page.waitForFunction(()=>window.player&&window.player.generation()>0,{},{timeout:30000});
  await settle(page);
  return {page,errors,requests};
}
const settle=page=>page.evaluate(()=>window.player.idle());
const state=page=>page.evaluate(()=>({surface:window.player.surface(),time:window.player.time(),frame:window.player.frame(),
  playing:window.player.playing(),generation:window.player.generation(),poses:window.player.poses().length}));
async function seek(page,t){await page.evaluate(t=>window.player.seek(t),t);await settle(page);}
const readout=page=>page.evaluate(()=>Object.fromEntries([...document.querySelectorAll('#readout [data-field]')]
  .map(el=>[el.dataset.field,{text:el.textContent,value:el.dataset.value??null}])));
const messages=page=>page.evaluate(()=>Object.fromEntries(['refusal','fault','note'].map(id=>{const el=document.getElementById(id);return [id,el.hidden?null:el.textContent];})));
async function generation(page,number){
  await page.waitForFunction(n=>window.player.generation()>=n,number,{timeout:60000});
  await settle(page);
}
// The session's generation once no reload has started for a second (a bounded wait).
async function settled(s){
  let number=s.generation().number,since=Date.now();
  for(const until=Date.now()+60_000;Date.now()<until&&Date.now()-since<1000;){
    await new Promise(r=>setTimeout(r,100));
    if(s.generation().number!==number){number=s.generation().number;since=Date.now();}
  }
  return number;
}
// What the stage page's own window.film says of the view it holds.
const stageView=page=>page.evaluate(k=>{
  const win=document.querySelector('iframe').contentWindow,film=win.film,transport=film.transport(k);
  return {views:film.views(),bank:transport&&transport.bank(),identity:transport?.identity,sentinel:win.playerSentinel??null,
    loads:Number(document.querySelector('iframe').dataset.loads)};
},VIEW);
const iframePixels=page=>page.locator('iframe').screenshot();
const plain=value=>JSON.parse(JSON.stringify(value));

test('the movie surface poses the frame /frame gives on the render\'s stage page, its report the renderer\'s for the same frame',async t=>{
  const {session:s,file,viewer}=await session(t,'count');
  const {page,errors,requests}=await player(t,s.origin);
  assert.equal(new URL(page.url()).hash,'#movie','the default surface, named in the address');
  const geometry=await page.evaluate(()=>{const f=document.querySelector('iframe');
    return {width:f.width,height:f.height,transform:f.style.transform,src:new URL(f.src).pathname,inner:[f.contentWindow.innerWidth,f.contentWindow.innerHeight]};});
  assert.deepEqual(geometry,{width:'640',height:'360',transform:'scale(1)',src:'/film.html',inner:[640,360]});
  assert.deepEqual((await state(page)).frame,0,'the first frame is posed at once');
  await seek(page,6);
  const at=await state(page);
  assert.deepEqual([at.surface,at.time,at.frame],['movie',6,60]);
  const observed=await page.evaluate(()=>window.player.observed());
  const film=await loadEpisode(file);
  // The frame the renderer would capture there, posed by the renderer's own session.
  const rendered=await browserSession(film,viewer,WIDTH,[],async({pose})=>({result:(await pose(6)).observed}));
  for(const field of ['frame','slots','chrome','elements'])
    assert.deepEqual(plain(observed[field]),plain(rendered.result[field]),`the stage reports the same ${field} in the player and in the renderer`);
  assert.deepEqual(observed.elements[VIEW].bank,frameAt(film,6).elements[VIEW].bank,'the bank the frame gives');
  const seen=await stageView(page);
  assert.deepEqual([seen.bank,seen.identity],[frameAt(film,6).elements[VIEW].bank,film.take.identity],'readback through the stage page\'s film');
  assert.ok(requests.includes('/frame'),'frames come from the session');
  assert.deepEqual(errors,[]);
  assert.deepEqual(await messages(page),{refusal:null,fault:null,note:null});
});

test('the movie surface poses one time, another and the first again: identical pixels of the stage\'s frame',async t=>{
  const {session:s}=await session(t,'count');
  const {page}=await player(t,s.origin,'#movie');
  await seek(page,2.5);const a1=await iframePixels(page);
  await seek(page,8);const b1=await iframePixels(page);
  await seek(page,2.5);const a2=await iframePixels(page);
  assert.ok(!a1.equals(b1),'two frames are two pictures');
  assert.ok(a1.equals(a2),'the first time is drawn identically after the second');
});

test('the ruler of the counter, the keys and the clicks move the playhead, and the readout says where it is',async t=>{
  const {session:s}=await session(t,'count');
  const {page,errors}=await player(t,s.origin);
  const ruler=await page.evaluate(()=>({
    bands:[...document.querySelectorAll('.vm-band')].map(b=>b.dataset.chapter),
    shots:[...document.querySelectorAll('.vm-shot')].map(b=>b.dataset.shot),
    joins:[...document.querySelectorAll('.vm-join')].map(j=>[j.dataset.join,parseFloat(j.style.left),parseFloat(j.style.width)]),
    ticks:document.querySelectorAll('.vm-tick').length,
    flags:[...document.querySelectorAll('.vm-flag')].map(f=>f.dataset.mark)}));
  assert.deepEqual(ruler,{bands:['counting'],shots:['once','nine','carry'],
    joins:[['carry',+(5.3/11.4*100).toFixed(4),+(0.5/11.4*100).toFixed(4)]],ticks:3,flags:['one','nine']});
  const frames=[];
  for(const key of ['Home','ArrowRight','Shift+ArrowRight','ArrowLeft','End']){
    await page.keyboard.press(key);await settle(page);
    frames.push([(await state(page)).frame,Number((await readout(page)).frame.value)]);
  }
  assert.deepEqual(frames,[[0,0],[1,1],[11,11],[0,0],[113,113]]);
  await seek(page,5);
  for(const expected of [3,1,0]){
    await page.keyboard.press('ArrowLeft');await settle(page);
    assert.equal((await state(page)).time,expected,'left goes back two seconds, stopping at zero');
  }
  await page.click('.vm-shot[data-shot="nine"] .vm-shot-name');await settle(page);
  assert.equal((await state(page)).time,3.2);
  const r=await readout(page);
  assert.deepEqual([r.time.text,r.frame.value,r.shot.value,r.chapter.value,r.mark.value,r.join.text],['3.20 s','32','nine','counting','one','']);
  await page.click('.vm-flag[data-mark="nine"]');await settle(page);
  assert.equal((await state(page)).time,5.3);
  const n=await readout(page);
  assert.deepEqual([n.shot.value,n.mark.value,n.join.text],['carry','nine','dissolve into carry, 0.5 s: shown as a cut at its midpoint']);
  // Space plays and pauses.
  await page.keyboard.press(' ');
  assert.equal((await state(page)).playing,true);
  await page.keyboard.press(' ');
  assert.equal((await state(page)).playing,false);
  assert.deepEqual(errors,[]);
});

test('a drag on the ruler across the boundary of two shots poses frames of both and ends on the released time',async t=>{
  const {session:s}=await session(t,'count');
  const {page}=await player(t,s.origin);
  const box=await page.evaluate(()=>{const r=document.getElementById('ruler').getBoundingClientRect();return {x:r.left,y:r.top,width:r.width,height:r.height};});
  const xAt=t=>box.x+box.width*t/11.4,y=box.y+box.height/2;
  const before=(await page.evaluate(()=>window.player.poses())).length;
  await page.mouse.move(xAt(2.0),y);
  await page.mouse.down();
  await settle(page);
  assert.equal((await state(page)).frame,20,'the pointer down seeks to the time under it');
  await page.mouse.move(xAt(4.5),y,{steps:12});
  await settle(page);
  await page.mouse.up();
  await settle(page);
  const poses=(await page.evaluate(()=>window.player.poses())).slice(before);
  assert.ok(poses.some(i=>i<32)&&poses.some(i=>i>=32),`frames of once and of nine were posed: ${poses}`);
  const end=await state(page);
  assert.deepEqual([end.frame,end.time,end.playing],[45,4.5,false],'the playhead stays where the pointer was released');
  assert.equal((await readout(page)).shot.value,'nine');
  // Released, the pointer moves nothing.
  await page.mouse.move(xAt(8),y);await settle(page);
  assert.equal((await state(page)).frame,45);
});

test('a generation with the same stage page keeps the frame and its viewer and poses again; a changed stage module reloads it',async t=>{
  const {session:s,file,movie}=await session(t,'count',{prepare:async({file,movie})=>{
    const doc=await readJson(file);doc.stage.modules=['extra.js'];
    await writeFile(file,JSON.stringify(doc,null,2)+'\n');
    await writeFile(join(movie,'extra.js'),'globalThis.playerExtra=1;\n');
  }});
  const {page,errors}=await player(t,s.origin);
  await seek(page,4);
  await page.evaluate(()=>{document.querySelector('iframe').contentWindow.playerSentinel='kept';});
  const first=await stageView(page),poses=(await state(page)).poses;
  // The document written again, unchanged: the same stage page.
  await writeFile(file,await readFile(file));
  await generation(page,2);
  const kept=await stageView(page),again=await state(page);
  assert.equal(kept.sentinel,'kept','the stage page was not reloaded');
  assert.deepEqual([kept.loads,kept.views],[first.loads,first.views],'one load, the same viewer instance');
  assert.ok(again.poses>poses,'the current time was posed again');
  assert.deepEqual([again.frame,again.generation],[40,2]);
  // A stage module that draws otherwise: another stage page, reloaded.
  await writeFile(join(movie,'extra.js'),'globalThis.playerExtra=2;\n');
  await generation(page,3);
  const reloaded=await stageView(page),after=await state(page);
  assert.equal(reloaded.sentinel,null,'the stage page was reloaded');
  assert.equal(reloaded.loads,first.loads+1);
  assert.deepEqual([after.frame,after.generation],[40,3],'the current time posed on it');
  assert.deepEqual(reloaded.bank,first.bank);
  assert.deepEqual(errors,[]);
});

test('a refusal is shown, the film kept, and cleared when a change is accepted; a caption is read out under the frame',async t=>{
  const {session:s,file,build}=await session(t,'count');
  const {page}=await player(t,s.origin);
  await seek(page,2);
  const saved=await readFile(file);
  await writeFile(file,'{"format": "machinome-movie/0.2",');
  await page.waitForFunction(()=>!document.getElementById('refusal').hidden,{},{timeout:60000});
  const refused=await messages(page);
  assert.match(refused.refusal,/^The last change was refused; the film shown is the last one accepted\.\nMovie document is not valid JSON/);
  assert.deepEqual([(await state(page)).frame,(await state(page)).generation],[20,1],'the film shown stays');
  await writeFile(file,saved);
  await generation(page,2);
  assert.equal((await messages(page)).refusal,null,'cleared by the next generation');
  // Captions written as speech writes them: an input, so the film reloads.
  await writeFile(join(build,'captions.json'),JSON.stringify([{text:'One turn of the crank.',start:1,end:2.5},{text:'Nine.',start:5,end:6}])+'\n');
  await generation(page,3);
  await seek(page,2);
  assert.equal(await page.evaluate(()=>document.getElementById('caption').textContent),'One turn of the crank.');
  assert.equal(await page.evaluate(()=>document.querySelector('iframe').contentDocument.body.textContent.includes('One turn of the crank.')),false,
    'the caption is under the frame, never in it');
  await seek(page,3);
  assert.equal(await page.evaluate(()=>document.getElementById('caption').hidden),true);
});

test('captions and transition readouts keep the movie frame and ruler stationary',async t=>{
  const {session:s}=await session(t,'count',{prepare:async({build})=>{
    await writeFile(join(build,'captions.json'),JSON.stringify([
      {text:'One turn.',start:1,end:2.5},
      {text:'A longer caption that wraps across several lines. '.repeat(12),start:5,end:6},
    ]));
  }});
  const {page}=await player(t,s.origin);
  for(const viewport of [{width:1000,height:520},{width:480,height:640}]){
    await page.setViewportSize(viewport);
    let baseline;
    for(const time of [0,2,3,5.4,6,8,0]){
      await seek(page,time);
      // Allow the ResizeObserver's fit to settle before measuring the actual frame.
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      const boxes=await page.evaluate(()=>['surface','ruler'].map(id=>document.getElementById(id))
        .concat(document.querySelector('iframe')).map(el=>{
          const {x,y,width,height}=el.getBoundingClientRect();return {x,y,width,height};
        }));
      baseline??=boxes;
      assert.deepEqual(boxes,baseline,`layout stays fixed at ${time}s in ${viewport.width}px viewport`);
    }
  }
});

test('with the narration mixed, the movie surface\'s clock is the mix: seeking the player seeks it',async t=>{
  const {session:s,file}=await session(t,'count');
  const {page}=await player(t,s.origin);
  assert.equal(await page.evaluate(()=>document.getElementById('narration')),null,'no mix, a timer');
  await speech(await loadEpisode(file),{generate:false});
  // speech writes the mix and the captions apart, and the session reloads on
  // each: wait for the last generation, on the session and on the page.
  await generation(page,await settled(s));
  await page.waitForFunction(()=>document.getElementById('narration'),{},{timeout:60000});
  await page.waitForFunction(()=>document.getElementById('narration').readyState>=1,{},{timeout:30000});
  await seek(page,4);
  const audio=await page.evaluate(()=>{const a=document.getElementById('narration');return {path:new URL(a.src).pathname,time:a.currentTime,paused:a.paused};});
  assert.deepEqual(audio,{path:'/narration.wav',time:4,paused:true});
  assert.equal((await messages(page)).note,null,'the mix is the film\'s length');
});

test('the take surface poses the counter\'s take on the viewer alone: each mark clicked holds its recorded bank; a new generation attaches again, a new export remounts',async t=>{
  const {session:s,file,dir,document:doc}=await session(t,'count');
  const {page,errors,requests}=await player(t,s.origin,'#take/take');
  const mounted=await page.evaluate(()=>({mounts:window.viewerMounts,iframes:document.querySelectorAll('iframe').length,
    flags:[...document.querySelectorAll('.vm-flag')].map(f=>f.dataset.mark),shots:document.querySelectorAll('.vm-shot').length}));
  assert.deepEqual(mounted.mounts.map(m=>[m.url,m.options]),[['/model/manifest.json',OPTIONS]],'mounted on the export, its camera its own');
  assert.deepEqual([mounted.iframes,mounted.shots,mounted.flags],[0,0,['one','nine','ten']]);
  assert.ok(!requests.some(path=>['/film.html','/stage.js','/config.json'].includes(path)),'nothing of the stage is loaded');
  assert.ok(requests.includes('/take.json'));
  for(const [name,time] of Object.entries(doc.marks)){
    await page.click(`.vm-flag[data-mark="${name}"]`);await settle(page);
    const held=await page.evaluate(()=>({bank:window.player.take().machine.bank(),time:window.player.take().time()}));
    assert.deepEqual(held,{bank:doc.take.banks[name],time},`the viewer's machine holds the recorded bank at the mark ${name}`);
    assert.equal((await readout(page)).mark.value,name);
  }
  // A new generation: the viewer stays, the transport is attached again and the time sought again.
  await page.evaluate(()=>{window.player.take().sentinel='old';});
  const poses=(await state(page)).poses;
  await writeFile(file,await readFile(file));
  await generation(page,2);
  const reattached=await page.evaluate(()=>({mounts:window.viewerMounts.length,sentinel:window.player.take().sentinel??null,
    bank:window.player.take().machine.bank()}));
  assert.deepEqual(reattached,{mounts:1,sentinel:null,bank:doc.take.banks.ten});
  assert.ok((await state(page)).poses>poses);
  // Another viewer bundle, read at the next load: the export changed, the viewer remounts.
  await writeFile(join(dir,'viewer-double.js'),`// machinome-viewer double, viewer API 29, again\n${viewerDouble({parts:'*',tintHighlight:true,api:29,...takeMachine(doc.take)})}`);
  await writeFile(file,await readFile(file));
  await generation(page,3);
  const remounted=await page.evaluate(()=>({mounts:window.viewerMounts.length,hosts:document.querySelectorAll('.vm-take-viewer').length,
    bank:window.player.take().machine.bank(),time:window.player.time()}));
  assert.deepEqual(remounted,{mounts:2,hosts:1,bank:doc.take.banks.ten,time:8});
  assert.deepEqual(errors,[]);
});

test('on the tour: a dissolve and a wipe shown as cuts at their midpoints, a reframe drawn live, a fade in without its plate, and the loop on the take surface',async t=>{
  allowLaunches(1);      // checkSource measures the tour's layout in a Chromium of its own, as check does
  const {session:s}=await session(t,'tour');
  const film=s.generation().film,fps=film.output.fps;
  const {page,errors}=await player(t,s.origin);
  const posedKeys=async index=>{await seek(page,index/fps);return Object.keys(await page.evaluate(()=>window.player.observed().elements)).sort();};
  const keys=frame=>Object.keys(frame.elements).sort();
  const shot=id=>film.chapters.flatMap(c=>c.shots).find(x=>x.id===id);
  // The dissolve into source: holds's frame before its midpoint, source's from it on.
  const source=shot('source'),middle=Math.round((source.start+0.3)*fps);
  const before=frameAt(film,(middle-1)/fps),from=frameAt(film,middle/fps);
  assert.equal(before.transition.kind,'dissolve');
  assert.deepEqual(await posedKeys(middle-1),keys(before.transition.outgoing));
  assert.equal(before.transition.outgoing.shotId,'holds');
  assert.equal((await readout(page)).join.text,'dissolve into source, 0.6 s: shown as a cut at its midpoint');
  assert.deepEqual(await posedKeys(middle),keys(from));
  assert.equal((await readout(page)).shot.value,'source');
  // The wipe into push, the same rule.
  const push=shot('push'),wipe=Math.round((push.start+0.3)*fps);
  assert.deepEqual(await posedKeys(wipe-1),keys(frameAt(film,(wipe-1)/fps).transition.outgoing));
  assert.deepEqual(await posedKeys(wipe+1),keys(frameAt(film,(wipe+1)/fps)));
  assert.equal((await readout(page)).join.text,'wipe into push, 0.6 s: shown as a cut at its midpoint');
  // The reframe into question: posed live, each element at the join's progress.
  const question=shot('question'),inside=Math.round((question.start+0.4)*fps);
  await seek(page,inside/fps);
  const live=await page.evaluate(()=>window.player.observed().elements);
  assert.ok(Object.values(live).every(e=>typeof e.opacity==='number'),'a reframe frame reports each element\'s opacity');
  assert.equal((await readout(page)).join.text,'reframe into question, 0.8 s: drawn live');
  // The fade in of hook: its frame, without the plate.
  assert.deepEqual(await posedKeys(0),keys(frameAt(film,0)));
  assert.equal((await readout(page)).join.text,'fade in, 1 s: shown without its fade');
  // The loop on the take surface: the time over the period, the mark rise at 5 s.
  await page.evaluate(()=>{location.hash='#take/loop';});
  await page.waitForFunction(()=>window.player.surface()==='take/loop'&&window.player.take());
  await seek(page,5);
  const loop=await page.evaluate(()=>({kind:window.player.take().kind,time:window.player.take().time(),
    flags:[...document.querySelectorAll('.vm-flag')].map(f=>f.dataset.mark),iframes:document.querySelectorAll('iframe').length}));
  assert.deepEqual(loop,{kind:'loop',time:0.25,flags:['rise','top','fall'],iframes:0});
  assert.equal((await readout(page)).mark.value,'rise');
  assert.deepEqual(errors,[]);
});
