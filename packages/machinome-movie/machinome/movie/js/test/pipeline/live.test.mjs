// Layer 8 (serial; the viewer double, the speech double, no provider): the
// live session (the live-server change, ADR-021; the player it builds and
// serves at /, the player-page change, ADR-022) end to end on the fixture
// movies `count`, `minimal` and `tour` and on the YAML fixture episode,
// through the module and through the command line. The command line runs in
// a child process with no key and a fetch that throws, and launches its own
// Chromium for the tour's layout, as `check` does; the module's sessions
// here load films that open no browser. Waits are bounded by a clock; no
// verdict reads one.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {readFile,writeFile,mkdir,chmod,mkdtemp,rm} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {createServer} from 'node:net';
import {createHash} from 'node:crypto';
import {execFileSync,spawn,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {live} from '../../src/live.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {speech,speechCacheEntry,spokenChapters} from '../../src/speech.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {fixtureMovie,PROJECT} from '../support/fixture-movie.mjs';
import {fixtureProject,yamlEpisode,evenAlignment,installTake,readJson} from '../project-fixture.mjs';
import {viewerDouble} from '../viewer-double.mjs';

const here=dirname(fileURLToPath(import.meta.url)),CLI=join(here,'..','..','bin','videomaker.mjs');
const FILM_PAGE=join(here,'..','..','src','film.html'),PLAYER_PAGE=join(here,'..','..','player','index.html');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const pause=ms=>new Promise(r=>setTimeout(r,ms));
const NO_FETCH='data:text/javascript,globalThis.fetch=()=>{throw new Error("A test attempted a network request")}';
const childEnv=(extra={})=>({...process.env,ELEVENLABS_API_KEY:'',...extra});
// The command line, run to its end (a refusal, or check).
function cli(...args){
  const run=spawnSync(process.execPath,['--import',NO_FETCH,CLI,...args],{encoding:'utf8',env:childEnv(),timeout:180_000});
  return {code:run.status,out:run.stdout,err:run.stderr};
}
// check's lines, the Stage line's bundled or reused aside: a second load
// reuses the bundle the first one built.
const lines=text=>text.split('\n').filter(Boolean).map(l=>l.replace(/^Stage: (bundled|reused) /,'Stage: '));
// What the module's session prints, from now on.
function capture(t){
  const seen=[],log=console.log;
  console.log=(...args)=>{seen.push(...args.join(' ').split('\n'));};
  t.onTestFinished(()=>{console.log=log;});
  return seen;
}
// No key, and any request beyond the loopback interface fails the test.
function loopbackOnly(t){
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,calls=[];
  delete process.env.ELEVENLABS_API_KEY;
  globalThis.fetch=(url,...rest)=>{
    if(String(url).startsWith('http://127.0.0.1:'))return fetch(url,...rest);
    calls.push(String(url));throw new Error('A test attempted a network request');
  };
  t.onTestFinished(()=>{globalThis.fetch=fetch;if(key!==undefined)process.env.ELEVENLABS_API_KEY=key;});
  return calls;
}
async function get(origin,path){
  const res=await fetch(origin+path),bytes=Buffer.from(await res.arrayBuffer());
  return {status:res.status,type:res.headers.get('content-type'),cache:res.headers.get('cache-control'),bytes,
    text:bytes.toString('utf8'),json:()=>JSON.parse(bytes.toString('utf8'))};
}
// The server-sent events of a session, one at a time.
async function eventStream(origin){
  const controller=new AbortController(),res=await fetch(`${origin}/events`,{signal:controller.signal});
  assert.equal(res.status,200);assert.match(res.headers.get('content-type'),/^text\/event-stream/);
  const reader=res.body.getReader(),decoder=new TextDecoder(),queue=[];
  let buffer='',ended=false,wake=()=>{};
  (async()=>{
    try{
      for(;;){
        const {value,done}=await reader.read();if(done)break;
        buffer+=decoder.decode(value,{stream:true});
        for(let i;(i=buffer.indexOf('\n\n'))>=0;){
          const block=buffer.slice(0,i);buffer=buffer.slice(i+2);
          const kind=/^event: (.*)$/m.exec(block)?.[1],data=/^data: (.*)$/m.exec(block)?.[1];
          if(kind)queue.push({kind,data:JSON.parse(data)});
          wake();
        }
      }
    }catch{}
    ended=true;wake();
  })();
  return {
    // The next event, which must be of `kind`.
    async next(kind,timeout=120_000){
      const until=Date.now()+timeout;
      while(!queue.length&&!ended&&Date.now()<until)await new Promise(r=>{wake=r;setTimeout(r,250);});
      const event=queue.shift();
      assert.ok(event,`no ${kind} event arrived${ended?' (the stream ended)':''}`);
      assert.equal(event.kind,kind,JSON.stringify(event));
      return event.data;
    },
    // Nothing arrives for `ms`.
    async quiet(ms,why){await pause(ms);assert.deepEqual(queue,[],why);},
    // Every event until none has arrived for `ms` and the last is not a
    // reload still loading.
    async drain(ms){
      const seen=[];
      for(;;){
        await pause(ms);
        if(!queue.length&&seen.at(-1)?.kind!=='loading')return seen;
        seen.push(...queue.splice(0));
      }
    },
    ended:()=>ended,
    close:()=>controller.abort(),
  };
}
async function freePort(){
  const server=createServer();await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const {port}=server.address();await new Promise(r=>server.close(r));return port;
}
async function canListen(port){
  const server=createServer();
  const ok=await new Promise(r=>{server.once('error',()=>r(false));server.listen(port,'127.0.0.1',()=>r(true));});
  if(ok)await new Promise(r=>server.close(r));
  return ok;
}
// An xdg-open on the path that records its arguments, or fails.
async function opener(t,{fails=false}={}){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-opener-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  await writeFile(join(dir,'xdg-open'),fails?'#!/bin/sh\nexit 3\n':'#!/bin/sh\nprintf \'%s\\n\' "$@" > "$(dirname "$0")/opened"\n');
  await chmod(join(dir,'xdg-open'),0o755);
  return {dir,PATH:`${dir}:${process.env.PATH}`,opened:()=>readFile(join(dir,'opened'),'utf8').catch(()=>null)};
}
// The command line, left running: resolves once it prints its address line.
function startCli(t,args,env={}){
  const child=spawn(process.execPath,['--import',NO_FETCH,CLI,'live',...args],{env:childEnv(env),stdio:['ignore','pipe','pipe']});
  let out='',err='';
  const exited=new Promise(r=>child.on('exit',(code,signal)=>r({code,signal})));
  t.onTestFinished(()=>{if(child.exitCode===null&&child.signalCode===null)child.kill('SIGKILL');});
  child.stderr.on('data',d=>{err+=d;});
  const ready=new Promise((resolveReady,rejectReady)=>{
    child.stdout.on('data',d=>{out+=d;const m=/^Live: (http:\/\/127\.0\.0\.1:(\d+))\/$/m.exec(out);if(m)resolveReady({origin:m[1],port:Number(m[2])});});
    exited.then(({code})=>rejectReady(new Error(`live exited ${code} before its address line:\n${out}${err}`)));
  });
  return {child,ready,exited,out:()=>out,err:()=>err};
}

test('a session on the counter serves the outline, the frames, the take, the stage page and its files, events, reloads and refusals, then stops',async t=>{
  const calls=loopbackOnly(t);
  const {file,viewer,build}=await fixtureMovie(t,'count');
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.err);
  const printed=capture(t);
  const session=await live(file,{viewer,width:640});
  // The first load is check's: the same lines, in the same order.
  assert.deepEqual(lines(printed.join('\n')),lines(checked.out));
  assert.ok(printed.some(l=>/^Take: 3 steps/.test(l))&&printed.some(l=>/^Continuation: shot nine/.test(l)));
  assert.match(session.origin,/^http:\/\/127\.0\.0\.1:\d+$/);
  const g=session.generation(),film=g.film;
  assert.deepEqual([g.number,typeof g.loadedAt,g.stageSha256.length,g.exportSha256.length],[1,'string',64,64]);

  // The outline.
  const outline=(await get(session.origin,'/film.json'));
  assert.equal(outline.status,200);assert.match(outline.type,/^application\/json/);assert.equal(outline.cache,'no-store');
  const o=outline.json();
  assert.deepEqual([o.id,o.title,o.output],['count','Count',{width:640,height:360,fps:10,duration:11.4}]);
  assert.deepEqual(o.chapters,[{id:'counting',start:0,end:11.4}]);
  assert.deepEqual(o.shots.map(s=>[s.id,s.set,s.join]),[['once','frame',null],['nine','frame',null],['carry','split',{kind:'dissolve',duration:0.5}]]);
  assert.deepEqual(o.shots.map(s=>s.model),film.chapters[0].shots.map(s=>s.model));
  assert.deepEqual(o.cues.map(c=>[c.shot,c.id]),[['carry','cues[0]'],['carry','cues[1]'],['carry','cues[2]']]);
  assert.deepEqual(o.takes,{take:{kind:'clocked',duration:8,marks:[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}],url:'/take.json'}});
  assert.deepEqual([o.speech,o.stage,o.viewer,o.generation,o.refusal],
    [{mix:false,captions:false},{sha256:g.stageSha256},{api:29},{number:1,loadedAt:g.loadedAt},null]);

  // The frame at a time: the renderer's frame at the nearest output instant.
  const frame=async t=>(await get(session.origin,`/frame?t=${t}`)).json();
  assert.deepEqual(await frame('6.04'),JSON.parse(JSON.stringify(frameAt(film,6))));
  assert.deepEqual(await frame('3.24'),JSON.parse(JSON.stringify(frameAt(film,32/10))));
  assert.deepEqual(await frame('-1'),JSON.parse(JSON.stringify(frameAt(film,0))));
  assert.deepEqual(await frame('99'),JSON.parse(JSON.stringify(frameAt(film,113/10))));
  for(const query of ['/frame','/frame?t=','/frame?t=soon','/frame?t=Infinity']){
    const refused=await get(session.origin,query);
    assert.equal(refused.status,400,query);assert.match(refused.text,/\bt\b/,query);
  }

  // The take document, verbatim.
  const take=await get(session.origin,'/take.json');
  assert.equal(take.status,200);
  assert.equal(take.text,JSON.stringify({model:{expectedDurationSeconds:film.model.expectedDurationSeconds},marks:film.marks,take:film.take}));

  // The stage page and its files, as the renderer serves them.
  const page=await get(session.origin,'/film.html');
  assert.equal(page.status,200);assert.match(page.type,/^text\/html/);
  assert.ok(page.bytes.equals(await readFile(FILM_PAGE)));
  assert.deepEqual((await get(session.origin,'/config.json')).json(),JSON.parse(JSON.stringify(g.config)));
  assert.equal(sha((await get(session.origin,'/stage.js')).bytes),g.bundle.sha256);
  assert.equal(sha((await get(session.origin,'/stage.css')).bytes),g.bundle.cssSha256);
  assert.ok((await get(session.origin,'/viewer.js')).bytes.equals(await readFile(viewer)));
  assert.ok((await get(session.origin,'/model/manifest.json')).bytes.equals(await readFile(film.paths.manifest)));
  const line=checked.out.split('\n').find(l=>l.startsWith('Stage: '));
  assert.ok(line.includes(`(sha256 ${g.bundle.sha256.slice(0,12)})`),line);

  // The player, built once for the session before it served (player-page):
  // the page, its script and its stylesheet from _build/player/.
  const page0=await get(session.origin,'/');
  assert.deepEqual([page0.status,page0.status===404?page0.text:''],[200,''],'/ is the built player');
  assert.match(page0.type,/^text\/html/);
  assert.equal(session.player.reused,false,'the first session on a fresh copy builds the player');
  assert.ok(page0.bytes.equals(await readFile(join(build,'player','index.html'))));
  assert.ok(page0.bytes.equals(await readFile(PLAYER_PAGE)),'the page is player/index.html');
  assert.match(page0.text,/<script src="\/player\.js"><\/script>/);assert.match(page0.text,/href="\/player\.css"/);
  const script=await get(session.origin,'/player.js'),style=await get(session.origin,'/player.css');
  assert.match(script.type,/^text\/javascript/);assert.match(style.type,/^text\/css/);
  assert.deepEqual([sha(script.bytes),sha(style.bytes),sha(page0.bytes)],[session.player.sha256,session.player.cssSha256,session.player.htmlSha256]);
  assert.match(script.text,/^ {2}\/\/ videomaker\/player\/index\.ts$/m);
  // No narration yet.
  for(const path of ['/narration.wav','/captions.json'])assert.equal((await get(session.origin,path)).status,404,path);

  // A subscriber hears the current generation at once.
  const events=await eventStream(session.origin);
  assert.deepEqual(await events.next('generation'),{number:1,loadedAt:g.loadedAt,stageSha256:g.stageSha256,exportChanged:false});

  // The tool's own products under _build/ reload nothing: the player's
  // directory, the stage bundle's, the preview, the resolved document.
  await writeFile(join(build,'player','scratch.txt'),'scratch\n');
  await writeFile(join(build,'player','index.html'),await readFile(join(build,'player','index.html')));
  await writeFile(join(build,'stage','scratch.txt'),'scratch\n');
  await mkdir(join(build,'preview'),{recursive:true});await writeFile(join(build,'preview','scratch.png'),'not a png\n');
  await writeFile(join(build,'movie-resolved.json'),await readFile(join(build,'movie-resolved.json')));
  await events.quiet(1500,'the tool\'s own products start no reload');
  assert.ok((await get(session.origin,'/')).bytes.equals(page0.bytes),'the player is still served');

  // The document written again: a reload, check's lines printed again.
  const document=await readFile(file);
  let from=printed.length;
  await writeFile(file,document);
  assert.ok((await events.next('loading')).at);
  const second=await events.next('generation');
  assert.deepEqual([second.number,second.stageSha256,second.exportChanged],[2,g.stageSha256,false]);
  assert.deepEqual(lines(printed.slice(from).join('\n')),lines(checked.out),'check\'s lines again');
  assert.equal(session.generation().number,2);

  // speech mixes the cached take (no request): the mix and the captions are
  // inputs, so the film reloads, once or twice (speech writes them apart),
  // and both are served.
  await speech(await loadEpisode(file),{generate:false});
  const reloads=await events.drain(2000);
  assert.ok(reloads.length>=2,JSON.stringify(reloads));
  assert.deepEqual(reloads.map(e=>e.kind),reloads.map((_,i)=>i%2?'generation':'loading'),JSON.stringify(reloads));
  const last=reloads.at(-1).data;
  const mix=await readFile(join(build,'narration.wav')),narration=await fetch(`${session.origin}/narration.wav`);
  assert.ok(Buffer.from(await narration.arrayBuffer()).equals(mix));
  // An audio element reads the mix's length and seeks it by ranges (player-page).
  assert.deepEqual([narration.headers.get('content-length'),narration.headers.get('accept-ranges')],[String(mix.length),'bytes']);
  const part=await fetch(`${session.origin}/narration.wav`,{headers:{Range:'bytes=100-199'}});
  assert.deepEqual([part.status,part.headers.get('content-range'),part.headers.get('content-length')],[206,`bytes 100-199/${mix.length}`,'100']);
  assert.ok(Buffer.from(await part.arrayBuffer()).equals(mix.subarray(100,200)));
  const tail=await fetch(`${session.origin}/narration.wav`,{headers:{Range:'bytes=-10'}});
  assert.deepEqual([tail.status,tail.headers.get('content-range')],[206,`bytes ${mix.length-10}-${mix.length-1}/${mix.length}`]);
  await tail.arrayBuffer();
  const outside=await fetch(`${session.origin}/narration.wav`,{headers:{Range:`bytes=${mix.length}-`}});
  assert.deepEqual([outside.status,outside.headers.get('content-range')],[416,`bytes */${mix.length}`]);
  await outside.arrayBuffer();
  assert.deepEqual((await get(session.origin,'/captions.json')).json(),await readJson(join(build,'captions.json')));
  assert.deepEqual((await get(session.origin,'/film.json')).json().speech,{mix:true,captions:true});
  const accepted=session.generation().number;
  assert.equal(last.number,accepted);

  // A broken document is refused; the last accepted film stays served.
  await writeFile(file,'{"format": "machinome-movie/0.2",');
  await events.next('loading');
  const refused=await events.next('refused');
  assert.match(refused.message,/^Movie document is not valid JSON/);assert.ok(refused.at);
  const during=(await get(session.origin,'/film.json')).json();
  assert.deepEqual([during.generation.number,during.refusal],[accepted,refused]);
  assert.deepEqual(await frame('1'),JSON.parse(JSON.stringify(frameAt(session.generation().film,1))));
  assert.equal((await get(session.origin,'/stage.js')).status,200);
  // A page opened during the refusal hears the generation, then the refusal.
  const late=await eventStream(session.origin);
  assert.equal((await late.next('generation')).number,accepted);
  assert.deepEqual(await late.next('refused'),refused);
  late.close();
  // Restored: the next generation, and no refusal.
  await writeFile(file,document);
  await events.next('loading');
  assert.equal((await events.next('generation')).number,accepted+1);
  assert.equal((await get(session.origin,'/film.json')).json().refusal,null);

  // close() ends the streams and frees the port.
  const port=Number(new URL(session.origin).port);
  await session.close();
  for(let i=0;i<40&&!events.ended();i++)await pause(50);
  assert.equal(events.ended(),true,'the event stream ended');
  await assert.rejects(fetch(`${session.origin}/film.json`));
  assert.equal(await canListen(port),true,'the port is free');
  // A second session on the same film reuses the player the first built:
  // tool content, built once per session, not per generation.
  const again=await live(file,{viewer,width:640});
  try{
    assert.equal(again.player.reused,true);
    assert.deepEqual([again.player.sha256,again.player.cssSha256],[session.player.sha256,session.player.cssSha256]);
    assert.ok((await get(again.origin,'/')).bytes.equals(page0.bytes));
  }finally{await again.close();}
  assert.deepEqual(calls,[]);
});

test('a stage module that starts importing a file has that file watched from the next generation on',async t=>{
  loopbackOnly(t);
  const {file,viewer,movie}=await fixtureMovie(t,'minimal');
  const doc=await readJson(file);
  doc.stage.modules=['extra.js'];
  await writeFile(file,JSON.stringify(doc,null,2)+'\n');
  await writeFile(join(movie,'extra.js'),'// A stage module of the test; it registers nothing.\n');
  await writeFile(join(movie,'helper.js'),'export const helper=1;\n');
  capture(t);
  const session=await live(file,{viewer,width:320});
  t.onTestFinished(()=>session.close());
  const events=await eventStream(session.origin);
  assert.equal((await events.next('generation')).number,1);
  // Not imported: not an input.
  await writeFile(join(movie,'helper.js'),'export const helper=2;\n');
  await events.quiet(1500,'a file no module imports starts no reload');
  // Imported: the module changed reloads, and the new generation watches it.
  await writeFile(join(movie,'extra.js'),'// A stage module of the test; it registers nothing.\nimport \'./helper.js\';\n');
  await events.next('loading');
  assert.equal((await events.next('generation')).number,2);
  await writeFile(join(movie,'helper.js'),'export const helper=3;\n');
  await events.next('loading');
  assert.equal((await events.next('generation')).number,3);
  await session.close();
});

test('a session on the YAML episode reloads when its production settings change, and refuses an excerpt source that left its pin',async t=>{
  loopbackOnly(t);
  const {dir,revision}=await fixtureProject(t);
  const file=await yamlEpisode(dir,revision),viewer=join(dir,'viewer.js');
  await writeFile(viewer,'// machinome-viewer double, viewer API 28\n'+viewerDouble({}));
  const e=await loadEpisode(file),spoken=spokenChapters(e);
  for(const i of e.chapters.keys())
    await installTake(speechCacheEntry(e,spoken,i),{alignment:evenAlignment(spoken[i]),duration:+(Array.from(spoken[i]).length*.05+.05).toFixed(6)});
  capture(t);
  const session=await live(file,{viewer,width:320});
  t.onTestFinished(()=>session.close());
  const o=(await get(session.origin,'/film.json')).json();
  assert.deepEqual([o.title,o.chapters.length,o.shots.length,o.output],['YAML fixture',3,3,{width:320,height:180,fps:10,duration:7}]);
  assert.deepEqual(o.takes,{loop:{kind:'loop',duration:20,marks:[]}});
  const none=await get(session.origin,'/take.json');
  assert.deepEqual([none.status,none.text],[404,'No take document']);
  const events=await eventStream(session.origin);
  await events.next('generation');
  const production=join(dirname(file),'production.yaml');
  await writeFile(production,(await readFile(production,'utf8'))+'# touched\n');
  await events.next('loading');
  assert.equal((await events.next('generation')).number,2);
  // The excerpt source is an input: changed from its pin, it is refused.
  const source=join(dir,'models','fixture.py'),pinned=await readFile(source);
  await writeFile(source,pinned.toString()+'# changed\n');
  await events.next('loading');
  assert.match((await events.next('refused')).message,/Source differs from pinned model revision: models\/fixture\.py/);
  await writeFile(source,pinned);
  await events.next('loading');
  assert.equal((await events.next('generation')).number,3);
  await session.close();
});

test('the live command serves the tour on a fixed port, opens its address, finds a change by polling, and stops on an interrupt',async t=>{
  loopbackOnly(t);
  const {file,viewer}=await fixtureMovie(t,'tour');
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.err);
  const port=await freePort(),open=await opener(t);
  const run=startCli(t,[file,'--viewer',viewer,'--port',String(port),'--poll','100','--open'],{PATH:open.PATH});
  const {origin}=await run.ready;
  assert.equal(origin,`http://127.0.0.1:${port}`);
  // check's lines, the layout's included, then the address line, and nothing else.
  const out=run.out().split('\n').filter(Boolean);
  assert.equal(out.at(-1),`Live: ${origin}/`);
  assert.deepEqual(lines(out.slice(0,-1).join('\n')),lines(checked.out));
  assert.ok(out.some(l=>/^Layout playbill at 1280×720: /.test(l))&&out.some(l=>/^Reframe into question: /.test(l)));
  for(let i=0;i<100&&await open.opened()===null;i++)await pause(50);
  assert.equal(await open.opened(),`${origin}/\n`,'xdg-open was given the address');

  const o=(await get(origin,'/film.json')).json();
  assert.deepEqual(o.output,{width:960,height:540,fps:30,duration:18.9});
  assert.deepEqual(o.takes,{loop:{kind:'loop',duration:20,marks:[{name:'rise',time:5},{name:'top',time:10},{name:'fall',time:15}]}});
  const question=o.shots.find(s=>s.id==='question'),push=o.shots.find(s=>s.id==='push');
  assert.equal(question.join.kind,'reframe');assert.equal(push.join.kind,'wipe');
  const none=await get(origin,'/take.json');
  assert.deepEqual([none.status,none.text],[404,'No take document']);
  // The frame inside the reframe carries the boxes check measured.
  const inside=(await get(origin,`/frame?t=${question.start+question.join.duration/2}`)).json();
  assert.equal(inside.transition.kind,'reframe');
  assert.ok(Object.keys(inside.transition.boxes).includes('opening.wide'),JSON.stringify(inside.transition));
  const plate=await get(origin,'/pictures/stills/plate');
  assert.equal(plate.status,200);assert.ok(plate.bytes.equals(await readFile(join(PROJECT,'media','plate.png'))));

  // A change found by polling: the next generation, check's lines again.
  const events=await eventStream(origin);
  assert.equal((await events.next('generation')).number,1);
  const doc=await readJson(file);doc.title='Tour, retitled';
  await writeFile(file,JSON.stringify(doc,null,2)+'\n');
  await events.next('loading');
  assert.equal((await events.next('generation')).number,2);
  assert.equal((await get(origin,'/film.json')).json().title,'Tour, retitled');
  assert.match(run.out(),/^Tour, retitled: 3 chapters, 9 shots, 18\.9s; model 20s$/m);

  // An interrupt: exit 0, the stream ended, the port free.
  run.child.kill('SIGINT');
  assert.deepEqual(await run.exited,{code:0,signal:null},run.err());
  for(let i=0;i<40&&!events.ended();i++)await pause(50);
  assert.equal(events.ended(),true);
  assert.equal(await canListen(port),true,'the port is free');
});

test('the live command refuses what check refuses, its malformed options and a port in use, and does not fail when xdg-open does',async t=>{
  const {file,viewer}=await fixtureMovie(t,'count');
  // An option another command takes, or a malformed one, before any load.
  const fps=cli('live',file,'--viewer',viewer,'--fps','10');
  assert.deepEqual([fps.code,fps.err.trim()],[1,'The live command takes no --fps']);
  const port=cli('check',file,'--viewer',viewer,'--port','8080');
  assert.deepEqual([port.code,port.err.trim()],[1,'The check command takes no --port']);
  for(const [option,value] of [['--port','soon'],['--port','70000'],['--poll','fast'],['--poll','0.5']]){
    const refused=cli('live',file,'--viewer',viewer,option,value);
    assert.equal(refused.code,1,`${option} ${value}`);assert.match(refused.err,new RegExp(`^${option} must be `),refused.err);
  }
  // A port in use is refused naming it.
  const busy=createServer();await new Promise(r=>busy.listen(0,'127.0.0.1',r));
  const taken=busy.address().port;
  const inUse=cli('live',file,'--viewer',viewer,'--port',String(taken));
  await new Promise(r=>busy.close(r));
  assert.equal(inUse.code,1);
  assert.match(inUse.err,new RegExp(`^Port ${taken} is in use on 127\\.0\\.0\\.1; choose another with --port, or 0 for any free port$`,'m'));
  // A failing xdg-open fails nothing.
  const open=await opener(t,{fails:true});
  const run=startCli(t,[file,'--viewer',viewer,'--open'],{PATH:open.PATH});
  const {origin}=await run.ready;
  assert.equal((await get(origin,'/film.json')).status,200);
  run.child.kill('SIGINT');
  assert.deepEqual(await run.exited,{code:0,signal:null},run.err());
  // A document check refuses: check's message, exit 1, no address.
  await writeFile(file,'{"format": "machinome-movie/0.2",');
  const checked=cli('check',file,'--viewer',viewer),refused=cli('live',file,'--viewer',viewer);
  assert.equal(checked.code,1);
  assert.deepEqual([refused.code,refused.err,refused.out],[1,checked.err,'']);
  assert.match(refused.err,/^Movie document is not valid JSON/);
});
