// Layer 6 (serial; Chromium, FFmpeg, the real viewer; ADR-008): the stage and
// the commands with the machinome-viewer bundle the maintainer selects in
// VIDEOMAKER_VIEWER_BUNDLE, over the fixture project's export, which the
// framework's `machinome export` made, on the 0.2 fixture movie `tour`.
// Without a selected bundle every test here is skipped, "no viewer bundle
// selected" (test/support/viewer-bundle.mjs). The viewer is reached only
// through its declared handle: mount, apiVersion and the methods the stage
// calls.
import {afterAll,inject} from 'vitest';
import {viewerTest as test,assertViewerApi} from '../support/viewer-bundle.mjs';
import assert from 'node:assert/strict';
import {readFile,readdir,rm} from 'node:fs/promises';
import {join,dirname,extname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {browserSession,sharedStage} from '../support/stage.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {stageConfig} from '../../src/render.mjs';
import {frameAt,filmShots} from '../../src/timeline.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const WIDTH=640;

// The tour, copied, committed and loaded once for this file's tests.
let tour=null;
const cleanup=[];
afterAll(async()=>{for(const dir of cleanup)await rm(dir,{recursive:true,force:true});});
async function theTour(){
  return tour??=(async()=>{
    const movie=await fixtureMovie({onTestFinished(){}},'tour');
    if(!process.env.KEEP_VIDEOMAKER_TEST)cleanup.push(movie.dir);
    return {...movie,film:await loadEpisode(movie.file)};
  })();
}
const middle=(film,id)=>{const {shot}=filmShots(film).find(s=>s.shot.id===id);return (shot.start+shot.end)/2;};
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
// The first output frame of a shot whose state satisfies `wanted`.
function firstInstant(film,id,wanted){
  const shot=shotOf(film,id),fps=film.output.fps;
  for(let n=Math.ceil(shot.start*fps);n/fps<shot.end;n++)if(wanted(frameAt(film,n/fps)))return n/fps;
  return null;
}
const fits=report=>report.canvas&&Math.abs(report.canvas.width-report.box.width)<=1&&Math.abs(report.canvas.height-report.box.height)<=1;
const inside=(p,r)=>p.x>=r.x-.5&&p.y>=r.y-.5&&p.x<=r.x+r.width+.5&&p.y<=r.y+r.height+.5;
const within=(a,r)=>a.x>=r.x-.5&&a.y>=r.y-.5&&a.x+a.width<=r.x+r.width+.5&&a.y+a.height<=r.y+r.height+.5;

test('the bundle declares the Viewer API the tour needs, read from a mounted instance',async(t,bundle)=>{
  const {film}=await theTour();
  const required=stageConfig(film).viewer.required.api;
  assert.equal(required,28,'the tour needs API 28: its views carry marks and highlights');
  // Mounted on its own, outside the stage, so a bundle below the movie's API
  // is named here rather than refused by the stage at its first view.
  const {browser,assets}=await sharedStage();
  const exported=dirname(film.paths.manifest);
  const release=assets.mount(async(req,res)=>{
    const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=path==='/viewer.js'?bundle:path.startsWith('/model/')?join(exported,path.slice('/model/'.length)):null;
    if(path==='/'){res.setHeader('Content-Type','text/html');res.end('<!doctype html><div id="v" style="width:640px;height:360px"></div><script src="/viewer.js"></script>');return;}
    if(!file||!file.startsWith(exported+'/')&&file!==bundle){res.writeHead(404);res.end();return;}
    try{res.setHeader('Content-Type',extname(file)==='.js'?'text/javascript':'application/octet-stream');res.end(await readFile(file));}
    catch{res.writeHead(404);res.end();}
  });
  const page=await browser.newPage({viewport:{width:640,height:360}});
  try{
    await page.goto(`${assets.origin}/`);
    const declared=await page.evaluate(async()=>{
      const viewer=await window.MachinomeViewer.mount('#v','/model/manifest.json',
        {renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none',
          time:0,view:{camera:[400,-600,300],target:[0,0,50]},up:[0,0,1],fov:37});
      return viewer.apiVersion;
    });
    assertViewerApi(bundle,declared,required);
  }finally{await page.close();release();}
});

test('a view\'s canvas fills its box on a fresh mount, after a change of set, and when the view returns',async(t,bundle)=>{
  // The real viewer sizes its canvas from its host on its own animation frame
  // and shrinks a detached host's canvas to nothing (wart 1 of "Cut and
  // Advance, version 2"). hook mounts opening.wide on playbill; source places
  // balance.mill on playbill-split, on the instance opening.wide freed
  // (ADR-007); hook places opening.wide back on it.
  const {film}=await theTour();
  const seen=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    // Each frame's outcome is kept, so every frame whose canvas does not fit
    // is named, not only the first the renderer refuses.
    const out=[];
    for(const [id,key] of [['hook','opening.wide'],['source','balance.mill'],['hook','opening.wide']]){
      try{const f=await pose(middle(film,id),{transition:null});out.push({id,set:f.set,key,report:f.observed.elements[key]});}
      catch(error){out.push({id,key,error:error.message.split('\n')[0]});}
    }
    return {result:{out,views:await page.evaluate(()=>window.film.views())}};
  });
  const {out,views}=seen.result;
  // Fills, and is no larger: a canvas left at another box's size overflows
  // the box it is in, which the renderer's check (at least 98 % of the box)
  // does not refuse.
  const size=r=>`${r.width.toFixed(1)}×${r.height.toFixed(1)}`;
  assert.deepEqual(out.flatMap(({id,key,error,report})=>error?[`${key} in ${id}: ${error}`]
    :fits(report)?[]:[`${key} in ${id}: canvas ${report.canvas?size(report.canvas):'absent'} in a box ${size(report.box)}`]),[],
  'every frame is posed, its canvas its box\'s size');
  assert.deepEqual(out.map(x=>x.set),['playbill','playbill-split','playbill']);
  assert.equal(new Set(out.map(x=>x.report.instance)).size,1,'one instance served the three frames');
  assert.equal(views.length,1);
});

test('posing A, then B, then A gives identical pixels across a camera move, a ghosted highlight, a hidden layer and a leased instance',async(t,bundle)=>{
  const {film}=await theTour();
  // A: balance.mill in source, its highlight standing (others ghost) and the
  // ground hidden. B: opening.wide in hook, halfway through its move to near,
  // on the instance A freed.
  const a=firstInstant(film,'source',f=>f.elements['balance.mill'].highlight?.others==='ghost');
  const b=middle(film,'hook');
  assert.ok(a!==null,'source has an instant with a ghosted highlight');
  const A=frameAt(film,a).elements['balance.mill'],B=frameAt(film,b).elements['opening.wide'];
  const start=frameAt(film,shotOf(film,'hook').start).elements['opening.wide'];
  assert.ok(A.hidden.length>0&&B.hidden.length===0&&!B.highlight,'A hides a layer and highlights; B neither');
  assert.notDeepEqual(B.view.camera,start.view.camera,'B is posed during a camera move');
  const seen=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    const shot=async(t,key)=>{const f=await pose(t,{transition:null});return {png:await page.screenshot(),report:f.observed.elements[key]};};
    const a1=await shot(a,'balance.mill'),b1=await shot(b,'opening.wide'),a2=await shot(a,'balance.mill');
    return {result:{a1,b1,a2,mounts:(await page.evaluate(()=>window.film.views())).length}};
  });
  const {a1,b1,a2,mounts}=seen.result;
  assert.equal(mounts,1,'one instance, leased from balance.mill to opening.wide and back');
  assert.equal(new Set([a1,b1,a2].map(x=>x.report.instance)).size,1);
  assert.ok(!a1.png.equals(b1.png),'B differs from A');
  assert.ok(a2.png.equals(a1.png),'A is drawn identically before and after B');
  const fresh=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    await pose(b,{transition:null});return {result:await page.screenshot()};
  });
  assert.ok(b1.png.equals(fresh.result),'B on the instance A freed gives the pixels of B on a fresh instance');
});

test('a label\'s target is on screen through the real partOnScreen and project, and its text inside the frame',async(t,bundle)=>{
  const {film}=await theTour();
  // rise, with the ring and the Plank label fully shown.
  const at=firstInstant(film,'rise',f=>{const m=f.elements['tip.close'].marks;
    return m.some(x=>x.kind==='label'&&x.text==='Plank')&&m.every(x=>x.opacity===1);});
  assert.ok(at!==null,'rise shows its Plank label fully');
  const state=frameAt(film,at).elements['tip.close'];
  const seen=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    const f=await pose(at,{transition:null});
    const projected=await page.evaluate(([target,camera])=>window.film.project('tip.close',[target,camera]),[state.view.target,state.view.camera]);
    return {result:{observed:f.observed,projected}};
  });
  const {observed,projected}=seen.result,view=observed.elements['tip.close'];
  const frame={x:0,y:0,width:observed.frame.width,height:observed.frame.height};
  assert.equal(view.marks.length,state.marks.length,'every mark reached the picture');
  const label=view.marks.find(m=>m.kind==='label');
  assert.ok(label,'the label was drawn');
  for(const mark of view.marks){
    assert.ok(mark.anchor&&inside(mark.anchor,view.box),`the ${mark.kind}'s target is on screen in the view (${JSON.stringify(mark.anchor)})`);
    if(mark.rect)assert.ok(mark.rect.width>0&&mark.rect.height>0,`the viewer gives the ${mark.kind}'s part a rectangle`);
  }
  assert.ok(label.text&&within(label.text,frame),`the label's text lies inside the frame (${JSON.stringify(label.text)})`);
  // The camera's target projects to the centre of the view; the camera itself
  // is not in front of itself.
  const [target,eye]=projected;
  assert.ok(target&&Math.abs(target.x-(view.box.x+view.box.width/2))<=1&&Math.abs(target.y-(view.box.y+view.box.height/2))<=1,
    `the target projects to the view's centre (${JSON.stringify(target)}, box ${JSON.stringify(view.box)})`);
  assert.equal(eye,null,'a point at the camera does not project');
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

test('the tour is checked, previewed and rendered with the real viewer',async(t,bundle)=>{
  const movie=await fixtureMovie(t,'tour');
  const checked=cli('check',movie.file,'--viewer',bundle);
  assert.equal(checked.code,0,checked.out);
  const api=/^Viewer API 28 required for .*; (.+) declares API (\d+)$/m.exec(checked.out);
  assert.ok(api,checked.out);assert.equal(api[1],bundle);assert.ok(Number(api[2])>=28);
  const previewed=cli('preview',movie.file,'--viewer',bundle,'--width',String(WIDTH));
  assert.equal(previewed.code,0,previewed.out);
  const report=JSON.parse(await readFile(join(movie.build,'preview','report.json'),'utf8'));
  assert.equal(report.pixelReplay,true);
  assert.deepEqual(report.highlightChecks.map(c=>c.shotId),['source','source','rise','rise','invitation']);
  for(const kind of ['entranceChecks','fadeChecks','emphasisChecks','pictureChecks','transitionChecks','cameraChecks'])
    assert.ok(report[kind]?.length>0,`the report lists ${kind}`);
  const rendered=cli('render',movie.file,'--viewer',bundle,'--width',String(WIDTH));
  assert.equal(rendered.code,0,rendered.out);
  const manifest=JSON.parse(await readFile(join(movie.build,'rehearsal-manifest.json'),'utf8'));
  const frames=Math.round(18.9*30);
  assert.equal(manifest.count,frames);
  assert.deepEqual(probe(manifest.output),{frames,width:640,height:360,rate:'30/1'},'every frame, counted by ffprobe');
});

// The resident memory of a process and its descendants, in kB, from /proc.
async function treeRss(root){
  const parents=new Map();
  for(const name of await readdir('/proc')){
    if(!/^\d+$/.test(name))continue;
    const stat=await readFile(`/proc/${name}/stat`,'utf8').catch(()=>null);
    if(!stat)continue;
    const ppid=Number(stat.slice(stat.lastIndexOf(')')+2).split(' ')[1]);
    parents.set(Number(name),ppid);
  }
  const tree=new Set([root]);
  for(let grew=true;grew;){grew=false;for(const [pid,ppid] of parents)if(!tree.has(pid)&&tree.has(ppid)){tree.add(pid);grew=true;}}
  let kb=0;
  for(const pid of tree){
    const status=await readFile(`/proc/${pid}/status`,'utf8').catch(()=>'');
    const m=/^VmRSS:\s+(\d+) kB$/m.exec(status);if(m)kb+=Number(m[1]);
  }
  return {processes:tree.size,kb};
}

test('the memory of one and of two viewer instances is read and recorded',async(t,bundle)=>{
  // Recorded, not asserted (ADR-008): the numbers depend on the machine and on
  // what else runs. The page's JavaScript heap from CDP, and the resident
  // memory of Chromium's whole process tree from /proc.
  const {film}=await theTour();
  const pid=inject('browserPid');
  assert.ok(Number.isInteger(pid),'the global setup provides the browser\'s PID');
  const tA=middle(film,'rise'),tB=middle(film,'invitation');
  const two={shotId:'two-views',chapterId:'tip',set:'split',slots:{left:'tip.close',right:'tip.wide'},
    elements:{'tip.close':frameAt(film,tA).elements['tip.close'],'tip.wide':frameAt(film,tB).elements['tip.wide']},transition:null};
  const seen=await browserSession(film,bundle,WIDTH,[],async({page,pose})=>{
    const cdp=await page.context().newCDPSession(page);await cdp.send('Performance.enable');
    const read=async()=>{
      await cdp.send('HeapProfiler.collectGarbage').catch(()=>{});
      const {metrics}=await cdp.send('Performance.getMetrics'),m=Object.fromEntries(metrics.map(x=>[x.name,x.value]));
      return {instances:(await page.evaluate(()=>window.film.views())).length,
        jsHeapUsedMB:+(m.JSHeapUsedSize/2**20).toFixed(1),jsHeapTotalMB:+(m.JSHeapTotalSize/2**20).toFixed(1),
        chromium:await treeRss(pid)};
    };
    const before=await treeRss(pid);
    await pose(tA,{transition:null});const one=await read();
    await pose(tA,two);const both=await read();
    return {result:{before,one,both}};
  });
  const {before,one,both}=seen.result;
  const mb=kb=>+(kb/1024).toFixed(0);
  console.log(`Viewer memory: before the session, Chromium ${mb(before.kb)} MB resident in ${before.processes} processes; `+
    `one instance: page heap ${one.jsHeapUsedMB} MB used of ${one.jsHeapTotalMB} MB, Chromium ${mb(one.chromium.kb)} MB in ${one.chromium.processes}; `+
    `two instances: page heap ${both.jsHeapUsedMB} MB used of ${both.jsHeapTotalMB} MB, Chromium ${mb(both.chromium.kb)} MB in ${both.chromium.processes}`);
  assert.equal(one.instances,1);assert.equal(both.instances,2);
  for(const x of [one,both])assert.ok(x.jsHeapUsedMB>0&&x.chromium.kb>0,'both were read');
});
