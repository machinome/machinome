// Layer 6 (serial; Chromium, FFmpeg, the real viewer; ADR-008, ADR-012): the
// clocked take on the machinome-viewer bundle VIDEOMAKER_VIEWER_BUNDLE
// selects, over the fixture counter's export, which the framework's `machine
// export` made, filmed by the 0.2 fixture movie `count`, whose take the
// Python side recorded through the framework's simulation. Without a selected
// bundle every test here is skipped, "no viewer bundle selected". The viewer
// is reached only through its declared handle: mount, apiVersion, machine()
// and the methods the stage calls.
import {afterAll} from 'vitest';
import {viewerTest as test,assertViewerApi} from '../support/viewer-bundle.mjs';
import assert from 'node:assert/strict';
import {readFile,rm} from 'node:fs/promises';
import {join,dirname,extname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {browserSession,sharedStage} from '../support/stage.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {stageConfig} from '../../src/render.mjs';
import {frameAt,filmShots} from '../../src/timeline.mjs';
import {replayTake} from '../../src/take.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const WIDTH=640,VIEW='counting.view';

let count=null;
const cleanup=[];
afterAll(async()=>{for(const dir of cleanup)await rm(dir,{recursive:true,force:true});});
async function theCount(){
  return count??=(async()=>{
    const movie=await fixtureMovie({onTestFinished(){}},'count');
    if(!process.env.KEEP_VIDEOMAKER_TEST)cleanup.push(movie.dir);
    return {...movie,film:await loadEpisode(movie.file)};
  })();
}
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
const middle=(film,id)=>{const shot=shotOf(film,id);return (shot.start+shot.end)/2;};

test('the bundle declares the Viewer API a take needs, and its machine is the export\'s, read from a mounted instance',async(t,bundle)=>{
  const {film}=await theCount();
  const required=stageConfig(film).viewer.required.api;
  assert.equal(required,29,'a movie on a clocked take needs API 29');
  const {browser,assets}=await sharedStage();
  // The project's exports: the seesaw's posed loop, which every bundle
  // mounts, tells the API; the counter's clocked machine, its identity.
  const exports=dirname(dirname(film.paths.manifest));
  const release=assets.mount(async(req,res)=>{
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=path==='/viewer.js'?bundle:path.startsWith('/export/')?join(exports,path.slice('/export/'.length)):null;
    if(path==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><div id="a" style="width:640px;height:360px"></div><div id="b" style="width:640px;height:360px"></div><script src="/viewer.js"></script>');return;}
    if(!file||!file.startsWith(exports+'/')&&file!==bundle){res.writeHead(404);res.end();return;}
    try{res.setHeader('Content-Type',extname(file)==='.js'?'text/javascript':'application/octet-stream');res.end(await readFile(file));}
    catch{res.writeHead(404);res.end();}
  });
  const page=await browser.newPage({viewport:{width:640,height:720}});
  const options={renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none',up:[0,0,1],fov:37};
  try{
    await page.goto(`${assets.origin}/`);
    const api=await page.evaluate(async options=>(await window.MachinomeViewer.mount('#a','/export/seesaw/manifest.json',
      {...options,time:0,view:{camera:[400,-600,300],target:[0,0,50]}})).apiVersion,options);
    // A bundle below the take's API is named here, before the clocked mount
    // it would refuse.
    assertViewerApi(bundle,api,required);
    // The stage's options, without a loop time: a clocked document under
    // on-demand rendering is what API 29 admits.
    const identity=await page.evaluate(async options=>{
      const viewer=await window.MachinomeViewer.mount('#b','/export/counter/manifest.json',
        {...options,view:{camera:[160,-260,140],target:[0,0,20]}});
      return viewer.machine?.()?.identity()??null;
    },options);
    assert.equal(identity,film.take.identity,'the viewer\'s machine is the one the take was recorded on');
  }finally{await page.close();release();}
});

test('every step of the recorded take, replayed on the viewer from its bank, returns the framework\'s request exactly',async(t,bundle)=>{
  const {film}=await theCount();
  const {before,after}=replayTake(film.take);
  const seen=await browserSession(film,bundle,WIDTH,[],async({page})=>{
    // Beyond what the session compares: every field of the request, and the
    // bank the machine holds after it, with Object.is.
    const differences=await page.evaluate(([key,take,before,after])=>{
      const machine=window.film.machine(key),out=[];
      const same=(where,a,b)=>{if(!Object.is(a,b))out.push(`${where}: viewer ${JSON.stringify(a)}, take ${JSON.stringify(b)}`);};
      const sameBank=(where,a,b)=>{for(const id of new Set([...Object.keys(a),...Object.keys(b)]))same(`${where}.${id}`,a[id],b[id]);};
      take.steps.forEach((step,i)=>{
        machine.restore({identity:take.identity,bank:before[i]});
        const r=machine.move(step.input,step.to!==undefined?{to:step.to}:{by:step.by});
        for(const field of ['input','origin','end','admitted'])same(`${step.id}.${field}`,r[field],step[field]);
        same(`${step.id}.commits.length`,r.commits.length,step.commits.length);
        r.commits.forEach((c,j)=>{const q=step.commits[j]??{};
          for(const field of ['fraction','value'])same(`${step.id}.commits[${j}].${field}`,c[field],q[field]);
          sameBank(`${step.id}.commits[${j}].targets`,c.targets,q.targets??{});
          same(`${step.id}.commits[${j}].relations`,JSON.stringify(c.relations),JSON.stringify(q.relations));});
        same(`${step.id}.stops.length`,r.stops.length,step.stops.length);
        sameBank(`${step.id} bank after`,machine.state(),after[i]);
      });
      return out;
    },[VIEW,film.take,before,after]);
    return {result:differences};
  });
  assert.deepEqual(seen.takeReplay,{steps:3,matched:true},'the session held the viewer to the take before its first frame');
  assert.deepEqual(seen.result,[],'every field of every request, and the bank after it, is the framework\'s');
});

test('posing one bank, then another, then the first gives identical pixels; the banks at the marks are the recorded ones; no viewer control is shown',async(t,bundle)=>{
  const {film}=await theCount();
  const a=middle(film,'nine'),b=middle(film,'once');
  assert.notDeepEqual(frameAt(film,a).elements[VIEW].bank,frameAt(film,b).elements[VIEW].bank);
  const seen=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    const grab=async t=>{const f=await pose(t,{transition:null});return {png:await page.screenshot(),report:f.observed.elements[VIEW]};};
    const a1=await grab(a),b1=await grab(b),a2=await grab(a);
    // Shots begin at the marks one (nine) and nine (carry).
    const marks={};
    for(const [id,mark] of [['nine','one'],['carry','nine']])marks[mark]=(await pose(shotOf(film,id).start,{transition:null})).observed.elements[VIEW].bank;
    const controls=await page.evaluate(()=>[...document.querySelectorAll('.machinome-fullscreen')]
      .filter(e=>{const s=getComputedStyle(e),r=e.getBoundingClientRect();return s.display!=='none'&&s.visibility!=='hidden'&&r.width>0&&r.height>0;}).length);
    return {result:{a1,b1,a2,marks,controls}};
  });
  const {a1,b1,a2,marks,controls}=seen.result;
  assert.ok(!a1.png.equals(b1.png),'two banks are two pictures');
  assert.ok(a1.png.equals(a2.png),'the first bank is drawn identically after the second');
  assert.deepEqual(a1.report.bank,frameAt(film,a).elements[VIEW].bank,'the viewer holds the bank it was given');
  assert.deepEqual(marks,{one:film.take.banks.one,nine:film.take.banks.nine});
  assert.equal(controls,0,'the film shows no viewer control');
});

test('a copy of the take with one commit\'s target forged is refused before the first frame, naming the step and the field',async(t,bundle)=>{
  const {film}=await theCount();
  const forged=structuredClone(film);
  forged.take.steps[1].commits[0].targets.units=7;
  let posed=0;
  await assert.rejects(browserSession(forged,bundle,WIDTH,[],async()=>{posed++;}),
    /The viewer does not reproduce the take: step step-2 \(take\.steps\[1\]\), commits\[0\]\.targets\.units: the viewer gives 2, the take records 7/);
  assert.equal(posed,0);
});

// The command line in a child process with no key and a fetch that throws.
const NO_FETCH='data:text/javascript,globalThis.fetch=()=>{throw new Error("A test attempted a network request")}';
const cli=(...args)=>{
  try{return {code:0,out:execFileSync(process.execPath,['--import',NO_FETCH,join(here,'..','..','bin','videomaker.mjs'),...args],
    {encoding:'utf8',stdio:['ignore','pipe','pipe'],env:{...process.env,ELEVENLABS_API_KEY:''}})};}
  catch(error){return {code:error.status,out:String(error.stdout)+String(error.stderr)};}
};
function probe(file){
  const data=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-of','json',file],{encoding:'utf8'}));
  const video=data.streams.find(s=>s.codec_type==='video');
  return {frames:Number(video.nb_read_frames),width:video.width,height:video.height,rate:video.r_frame_rate};
}

test('the counter\'s take is checked, previewed and rendered with the real viewer',async(t,bundle)=>{
  const movie=await fixtureMovie(t,'count');
  const checked=cli('check',movie.file,'--viewer',bundle);
  assert.equal(checked.code,0,checked.out);
  assert.match(checked.out,/^Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark$/m);
  const api=/^Viewer API 29 required for clocked take, highlight \(shot carry\); (.+) declares API (\d+)$/m.exec(checked.out);
  assert.ok(api,checked.out);assert.equal(api[1],bundle);assert.ok(Number(api[2])>=29);
  const previewed=cli('preview',movie.file,'--viewer',bundle,'--width',String(WIDTH));
  assert.equal(previewed.code,0,previewed.out);
  const report=JSON.parse(await readFile(join(movie.build,'preview','report.json'),'utf8'));
  assert.deepEqual(report.takeReplay,{steps:3,matched:true});
  assert.equal(report.pixelReplay,true);
  assert.deepEqual(report.highlightChecks.map(c=>c.shotId),['carry']);
  const rendered=cli('render',movie.file,'--viewer',bundle,'--width',String(WIDTH));
  assert.equal(rendered.code,0,rendered.out);
  const manifest=JSON.parse(await readFile(join(movie.build,'rehearsal-manifest.json'),'utf8'));
  const frames=Math.round(11.4*10);
  assert.equal(manifest.count,frames);
  assert.deepEqual(probe(manifest.output),{frames,width:640,height:360,rate:'10/1'},'every frame, counted by ffprobe');
});
