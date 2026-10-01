// The render-cost investigation's driver (addition-warts campaign, wart 14).
// Loads a movie document as the CLI does, opens the instrumented copy of the
// renderer's browserSession on it, and times frames three ways:
//
//   phases        render's own capture loop on the selected frames, in order:
//                 pose (the stage's setFrame and the renderer's checks), the
//                 screenshot, then the Node side (PNG size check, hash,
//                 write, rename, link), each timed, with the CPU each
//                 Chromium process spent and the stage's in-page breakdown
//                 (restore, setView, animation-frame waits, the rest).
//   alternatives  every selected frame posed afresh before each probe, the
//                 probes interleaved per frame (baseline first and last):
//                 the WebGL finish alone, an animation-frame round trip, the
//                 canvas read, the page without its views, JPEG, clip, CDP
//                 captures with optimizeForSpeed and fromSurface off on one
//                 persistent CDP session; bytes and decoded pixels hashed.
//   flags         phases on a short run per launch, the launches alternated
//                 between Chromium flag sets, frames hashed.
//
// node measure.mjs --mode phases|alternatives|flags --viewer BUNDLE.js
//   (--movie MOVIE.json | --fixture count) --shot ID [--skip N] [--frames N]
//   [--step K] [--width W] [--rounds R] --out RESULT.json
// TMPDIR must name a directory under this evidence directory's _build/ (the
// fixture project is copied there, never under /tmp).
import {parseArgs} from 'node:util';
import {readFile,writeFile,mkdir,rename,link,rm} from 'node:fs/promises';
import {readdirSync,readFileSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadavg,cpus} from 'node:os';
import {createHash} from 'node:crypto';
import {loadEpisode} from '../../../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../../../src/command-timing.mjs';
import {outputShotUnits} from '../../../../src/shot-cache.mjs';
import {decodePng} from '../../../../src/pixels.mjs';
import {browserSession,CHROMIUM_ARGS} from './render.instrumented.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
const now=()=>performance.now();
const load1=()=>loadavg()[0];
const {values:a}=parseArgs({options:{mode:{type:'string'},viewer:{type:'string'},movie:{type:'string'},fixture:{type:'string'},
  shot:{type:'string'},skip:{type:'string',default:'0'},frames:{type:'string',default:'60'},step:{type:'string',default:'1'},
  width:{type:'string'},rounds:{type:'string',default:'2'},variants:{type:'string'},out:{type:'string'},label:{type:'string'},probes:{type:'string'}}});
if(!a.mode||!a.viewer||!a.out||!(a.movie||a.fixture))throw new Error('usage: see the header of measure.mjs');
if(!process.env.TMPDIR||!resolve(process.env.TMPDIR).startsWith(resolve(here,'_build')))throw new Error('Set TMPDIR under this directory\'s _build/');

// ----- the film, loaded as the CLI loads it -----
async function loadFilm(){
  let file=a.movie,source;
  if(a.fixture){
    const {fixtureMovie}=await import('../../../../test/support/fixture-movie.mjs');
    const movie=await fixtureMovie(null,a.fixture);file=movie.file;source=`fixture ${a.fixture} copied to ${movie.dir}`;
  }else source=file;
  const resolvedBefore=await readFile(resolve(dirname(file),'movie-resolved.json')).then(sha,()=>null);
  const film=await loadEpisode(file);
  const resolvedAfter=await readFile(resolve(dirname(file),'movie-resolved.json')).then(sha,()=>null);
  await prepareWordTimingForCommand(film,{command:'render',silent:true,fps:film.output.fps});
  // The stage bundle and every frame go to this directory's _build, never
  // into the project's.
  const build=resolve(here,'_build',a.label??a.fixture??'movie');await mkdir(build,{recursive:true});
  if(!a.fixture)film.paths.build=build;
  return {film,source,build,movieResolved:{before:resolvedBefore,after:resolvedAfter}};
}

// ----- the frames: render's own output frames of one shot -----
function selectFrames(film){
  const fps=film.output.fps,{units}=outputShotUnits(film,fps);
  const unit=units.find(u=>u.shotId===a.shot);if(!unit)throw new Error(`No shot ${a.shot}`);
  const skip=Number(a.skip),n=Number(a.frames),step=Number(a.step);
  const frames=unit.frames.slice(skip).filter((_,i)=>i%step===0).slice(0,n);
  return {fps,frames:frames.map(f=>({index:f.index,time:f.time,transition:f.request.transition?.kind??null})),shotFrames:unit.frames.length};
}

// ----- CPU of Chromium's processes, from /proc (clock ticks of 10 ms) -----
const TICK=10;
function procs(){
  const all=new Map();
  for(const d of readdirSync('/proc'))if(/^\d+$/.test(d)){
    try{
      const stat=readFileSync(`/proc/${d}/stat`,'utf8'),rest=stat.slice(stat.lastIndexOf(')')+2).split(' ');
      all.set(Number(d),{ppid:Number(rest[1]),ticks:Number(rest[11])+Number(rest[12])});
    }catch{}
  }
  const mine=new Set([process.pid]);let grew=true;
  while(grew){grew=false;for(const [pid,p] of all)if(!mine.has(pid)&&mine.has(p.ppid)){mine.add(pid);grew=true;}}
  mine.delete(process.pid);
  return [...mine].map(pid=>{
    let cmd='';try{cmd=readFileSync(`/proc/${pid}/cmdline`,'utf8').split('\0').join(' ');}catch{}
    const type=/--type=([\w-]+)/.exec(cmd)?.[1]??(/chrom|headless/.test(cmd)?'browser':'other');
    return {pid,type,ticks:all.get(pid).ticks,cmd};
  });
}
function cpu(){
  const by={};for(const p of procs())by[p.type]=(by[p.type]??0)+p.ticks*TICK;
  const u=process.cpuUsage();by.node=(u.user+u.system)/1000;return by;
}
const cpuDelta=(x,y)=>Object.fromEntries([...new Set([...Object.keys(x),...Object.keys(y)])].map(k=>[k,(y[k]??0)-(x[k]??0)]));

// ----- in the page: timers around the stage and the viewer -----
const INIT=`(()=>{
  const rc=window.__rc={cur:null,last:null,intervals:[],inFrame:false};
  const fresh=()=>({setFrame:0,restore:0,setView:0,setTime:0,highlight:0,rafCount:0,rafWait:0});
  rc.cur=fresh();
  const raf=window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame=cb=>{const t=performance.now(),inFrame=rc.inFrame;
    return raf(ts=>{if(inFrame){rc.cur.rafCount++;rc.intervals.push([t,performance.now()]);}return cb(ts);});};
  const union=v=>{v.sort((p,q)=>p[0]-q[0]);let s=0,end=-Infinity;for(const [x,y] of v){if(y<=end)continue;s+=y-Math.max(x,end);end=y;}return s;};
  const timed=(o,name,bucket)=>{const f=o[name];if(typeof f!=='function'||f.__rc)return;
    const g=function(...args){const t=performance.now();try{return f.apply(this,args);}finally{rc.cur[bucket]+=performance.now()-t;rc.cur[bucket+'Calls']=(rc.cur[bucket+'Calls']??0)+1;}};
    g.__rc=true;o[name]=g;if(o[name]!==g)rc.unwrapped=(rc.unwrapped??[]).concat(name);};
  const wrapViewer=v=>{
    timed(v,'setView','setView');timed(v,'setTime','setTime');timed(v,'highlight','highlight');
    if(typeof v.machine==='function'){const m=v.machine;v.machine=function(...args){const h=m.apply(this,args);if(h)timed(h,'restore','restore');return h;};}
    return v;};
  let factory;
  Object.defineProperty(window,'MachinomeViewer',{configurable:true,get(){return factory;},set(f){
    // The bundle's exports are getters: the factory is proxied, not edited.
    if(f&&typeof f.mount==='function'){const mount=f.mount;const wrapped=async(...args)=>wrapViewer(await mount.apply(f,args));
      factory=new Proxy(f,{get:(t,k)=>k==='mount'?wrapped:Reflect.get(t,k)});}
    else factory=f;}});
  let film;
  Object.defineProperty(window,'film',{configurable:true,get(){return film;},set(v){
    if(v&&typeof v.setFrame==='function'){const sf=v.setFrame;v.setFrame=async function(f){
      rc.cur=fresh();rc.intervals=[];rc.inFrame=true;const t=performance.now();
      try{return await sf.call(this,f);}finally{rc.inFrame=false;rc.cur.setFrame=performance.now()-t;rc.cur.rafWait=union(rc.intervals);rc.last=rc.cur;}};}
    film=v;}});
  const canvases=()=>[...document.querySelectorAll('.vm-view-host canvas')];
  const gl=c=>c.getContext('webgl2')||c.getContext('webgl');
  rc.finish=()=>{const t=performance.now();for(const c of canvases()){const g=gl(c);if(g)g.finish();}return performance.now()-t;};
  rc.raf=()=>new Promise(r=>{const t=performance.now();raf(()=>raf(()=>r(performance.now()-t)));});
  // A redraw of the first view alone: the same camera set again (on-demand,
  // setView renders synchronously), then the work finished or read back.
  const again=()=>{const v=window.film.viewer,r=v.view();v.setView({camera:r.camera.toArray(),target:r.target.toArray(),up:r.up?.toArray(),fov:r.fov});};
  rc.redraw=how=>{
    let t=performance.now();again();const setView=performance.now()-t;
    const c=canvases()[0],g=gl(c);t=performance.now();let bytes=0;
    if(how==='finish')g.finish();
    else if(how==='readPixels'){const w=g.drawingBufferWidth,h=g.drawingBufferHeight,px=new Uint8Array(w*h*4);g.readPixels(0,0,w,h,g.RGBA,g.UNSIGNED_BYTE,px);bytes=px.length;}
    else if(how==='toDataURL'){bytes=c.toDataURL('image/png').length;}
    return {setView,ms:performance.now()-t,bytes,width:c.width,height:c.height};
  };
  // Hidden and put back attribute for attribute, so the page's content (the
  // stage's repaint test) is what it was.
  let saved=[];
  rc.hideViews=hidden=>{
    if(hidden){saved=[...document.querySelectorAll('.vm-view-host')].map(h=>[h,h.getAttribute('style')]);for(const [h] of saved)h.style.visibility='hidden';}
    else{for(const [h,s] of saved)s===null?h.removeAttribute('style'):h.setAttribute('style',s);saved=[];}
  };
  rc.renderer=()=>{
    const out={};const c=canvases()[0];
    for(const [name,ctx] of [['view',c&&gl(c)],['fresh',document.createElement('canvas').getContext('webgl2')]]){
      if(!ctx){out[name]=null;continue;}
      const ext=ctx.getExtension('WEBGL_debug_renderer_info');
      out[name]={version:ctx.getParameter(ctx.VERSION),vendor:ext&&ctx.getParameter(ext.UNMASKED_VENDOR_WEBGL),renderer:ext&&ctx.getParameter(ext.UNMASKED_RENDERER_WEBGL),
        attributes:ctx.getContextAttributes()};
    }
    out.canvases=canvases().map(c=>({width:c.width,height:c.height}));
    return out;
  };
})();`;

const trace={cur:null,add(name,ms){if(this.cur)this.cur[name]=(this.cur[name]??0)+ms;}};

async function environment(page,info){
  const ps=procs();
  return {chromium:info.browser,viewerApi:info.viewerApi,width:info.width,height:info.height,
    webgl:await page.evaluate(()=>window.__rc.renderer()),
    processes:ps.map(p=>({type:p.type,cmd:p.cmd})),node:process.version,cpus:cpus().length,
    viewerSha256:info.hashes['/viewer.js'],stageSha256:info.stage.sha256,takeReplay:info.takeReplay??null};
}

// Render's capture loop on the selected frames (src/render.mjs, the
// captureShotGeneration callback, and shot-cache's write and link).
async function phases(page,pose,frames,dir){
  await rm(dir,{recursive:true,force:true});await mkdir(resolve(dir,'generation'),{recursive:true});await mkdir(resolve(dir,'assembly'));
  const rows=[];
  for(const frame of frames){
    const row={index:frame.index,time:frame.time,transition:frame.transition,load1:load1()};trace.cur=row;
    const c0=cpu();let t=now();
    const posed=await pose(frame.time);row.pose=now()-t;
    const c1=cpu();t=now();
    const bytes=await page.screenshot();row.screenshot=now()-t;
    const c2=cpu();
    t=now();const ok=bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&bytes.readUInt32BE(16)>0;row.pngCheck=now()-t;
    const file=resolve(dir,'generation',`${String(frame.index).padStart(6,'0')}.png`);
    t=now();await writeFile(file+'.tmp',bytes);row.write=now()-t;
    t=now();await rename(file+'.tmp',file);row.rename=now()-t;
    t=now();row.sha256=sha(bytes);row.hash=now()-t;
    t=now();await link(file,resolve(dir,'assembly',`${String(frame.index).padStart(6,'0')}.png`));row.link=now()-t;
    row.bytes=bytes.length;row.ok=ok;
    trace.cur=null;
    row.page=await page.evaluate(()=>window.__rc.last);
    row.cpuPose=cpuDelta(c0,c1);row.cpuScreenshot=cpuDelta(c1,c2);
    row.bank=posed.observed&&Object.values(posed.observed.elements).find(e=>e.bank)?sha(JSON.stringify(Object.values(posed.observed.elements).find(e=>e.bank).bank)).slice(0,12):null;
    rows.push(row);
  }
  return rows;
}

// Every probe starts from a fresh pose of the same frame, so each is the
// first capture after a pose, as render's is.
async function alternatives(page,pose,frames,{width,height}){
  const cdp=await page.context().newCDPSession(page);
  const shot=async(fn)=>{const c0=cpu(),t=now();const bytes=await fn();const ms=now()-t;return {ms,cpu:cpuDelta(c0,cpu()),bytes};};
  const viaCdp=params=>async()=>Buffer.from((await cdp.send('Page.captureScreenshot',{format:'png',...params})).data,'base64');
  const probes={
    png:()=>shot(()=>page.screenshot()),
    finishThenPng:async()=>{const finish=await page.evaluate(()=>window.__rc.finish());const s=await shot(()=>page.screenshot());return {...s,finish};},
    rafThenPng:async()=>{const raf=await page.evaluate(()=>window.__rc.raf());const finish=await page.evaluate(()=>window.__rc.finish());const s=await shot(()=>page.screenshot());return {...s,raf,finish};},
    redrawFinish:async()=>({redraw:await page.evaluate(()=>window.__rc.redraw('finish'))}),
    redrawReadPixels:async()=>({redraw:await page.evaluate(()=>window.__rc.redraw('readPixels'))}),
    redrawToDataURL:async()=>({redraw:await page.evaluate(()=>window.__rc.redraw('toDataURL'))}),
    hiddenPng:async()=>{await page.evaluate(()=>window.__rc.hideViews(true));const s=await shot(()=>page.screenshot());await page.evaluate(()=>window.__rc.hideViews(false));return s;},
    jpeg:()=>shot(()=>page.screenshot({type:'jpeg'})),
    clip:()=>shot(()=>page.screenshot({clip:{x:0,y:0,width,height}})),
    cdp:()=>shot(viaCdp({})),
    cdpFast:()=>shot(viaCdp({optimizeForSpeed:true})),
    cdpNoSurface:()=>shot(viaCdp({fromSurface:false})),
    cdpFastNoSurface:()=>shot(viaCdp({optimizeForSpeed:true,fromSurface:false})),
    // A second capture of the posed page: the draw already rastered, so what
    // remains is compositing, readback, encoding and the transfer.
    pngAgain:async()=>{const first=await shot(()=>page.screenshot());const s=await shot(()=>page.screenshot());return {...s,firstMs:first.ms};},
  };
  const chosen=a.probes?a.probes.split(','):Object.keys(probes).filter(k=>k!=='png');
  const order=['png',...chosen,'png'];
  const rows=[];
  for(const frame of frames){
    const row={index:frame.index,time:frame.time,transition:frame.transition,probes:[]};
    for(const [i,name] of order.entries()){
      const load=load1();let t=now();await pose(frame.time);const poseMs=now()-t;
      const page_=await page.evaluate(()=>window.__rc.last);
      let r;try{r=await probes[name]();}catch(error){r={error:String(error.message??error)};}
      const out={name:i===order.length-1?'png2':name,load1:load,pose:poseMs,rafCount:page_.rafCount,...r};
      if(r.bytes){out.size=r.bytes.length;out.sha256=sha(r.bytes);
        if(name!=='jpeg'){try{out.pixels=sha(decodePng(r.bytes).rgb??decodePng(r.bytes).data??Buffer.alloc(0));}catch(error){out.pixels=`undecodable: ${error.message}`;}}
        delete out.bytes;}
      row.probes.push(out);
    }
    rows.push(row);
  }
  await cdp.detach();
  return rows;
}

const VARIANTS={
  stage:CHROMIUM_ARGS,
  playwright:[],
  disableGpu:['--disable-gpu',...CHROMIUM_ARGS],
  angleSwiftshader:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'],
  // A measurement of the multisampling's share only: the viewer's context is
  // asked for without antialiasing, which changes pixels by construction.
  noAntialias:CHROMIUM_ARGS,
};
const INIT_EXTRA={
  noAntialias:`(()=>{const g=HTMLCanvasElement.prototype.getContext;HTMLCanvasElement.prototype.getContext=function(type,attrs){
    return g.call(this,type,/webgl/.test(type)?{...(attrs??{}),antialias:false}:attrs);};})();`,
};

const {film,source,build,movieResolved}=await loadFilm();
const width=a.width?Number(a.width):film.output.width;
const result={mode:a.mode,source,shot:a.shot,width,movieResolved,
  started:new Date().toISOString(),load1Start:load1(),runs:[]};
// Frames are chosen inside a session, as render chooses them: a reframe's
// boxes are measured on the session's page first.
let frames=null;
const pick=()=>{if(!frames){const s=selectFrames(film);frames=s.frames;Object.assign(result,{fps:s.fps,shotFrames:s.shotFrames,frameCount:s.frames.length,frames:s.frames});}return frames;};
const session=async(launchArgs,action,extra='')=>browserSession(film,a.viewer,width,[],action,{trace,initScript:extra+INIT,launchArgs,outputWidth:width});
const started=now();
if(a.mode==='phases'){
  await session(CHROMIUM_ARGS,async({page,pose,info})=>{
    result.environment=await environment(page,info);
    result.runs.push({variant:'stage',rows:await phases(page,pose,pick(),resolve(build,'frames','phases'))});
    return {};
  });
}else if(a.mode==='alternatives'){
  await session(CHROMIUM_ARGS,async({page,pose,info})=>{
    result.environment=await environment(page,info);
    result.runs.push({variant:'stage',rows:await alternatives(page,pose,pick(),{width:info.width,height:info.height})});
    return {};
  });
}else if(a.mode==='flags'){
  const names=(a.variants??Object.keys(VARIANTS).join(',')).split(',');
  for(let round=0;round<Number(a.rounds);round++)for(const name of names){
    const t=now();let env=null,rows=null,error=null;
    try{
      await session(VARIANTS[name],async({page,pose,info})=>{
        env=await environment(page,info);
        rows=await phases(page,pose,pick(),resolve(build,'frames',`${name}-${round}`));return {};
      },INIT_EXTRA[name]??'');
    }catch(e){error=String(e.message??e).slice(0,2000);}
    result.runs.push({variant:name,round,args:VARIANTS[name],sessionMs:now()-t,environment:env,rows,error});
    console.log(`${name} round ${round}: ${error?'failed: '+error.split('\n')[0]:rows.length+' frames'} in ${((now()-t)/1000).toFixed(1)} s`);
  }
}else if(a.mode==='parallel'){
  // Throughput only: the same frames by one session, then split between
  // concurrent sessions (each its own Chromium), alternated per round.
  const counts=(a.variants??'1,2').split(',').map(Number);
  for(let round=0;round<Number(a.rounds);round++)for(const n of counts){
    const t=now(),load=load1();let all=null;
    const slices=await Promise.all(Array.from({length:n},(_,k)=>new Promise((done,fail)=>{
      session(CHROMIUM_ARGS,async({page,pose})=>{
        const mine=pick().filter((_,i)=>i%n===k);
        // The mount and the first frame are paid before the clock starts.
        await pose(mine[0].time);await page.screenshot();
        const t0=now();const rows=await phases(page,pose,mine,resolve(build,'frames',`parallel-${n}-${round}-${k}`));
        done({rows,ms:now()-t0});return {};
      }).catch(fail);
    })));
    all=slices.flatMap(s=>s.rows);
    result.runs.push({variant:`sessions-${n}`,round,sessions:n,load1:load,sliceMs:slices.map(s=>s.ms),wallMs:now()-t,
      framesPerSecond:all.length/(Math.max(...slices.map(s=>s.ms))/1000),rows:all});
    console.log(`${n} sessions round ${round}: ${all.length} frames, slowest slice ${(Math.max(...slices.map(s=>s.ms))/1000).toFixed(1)} s`);
  }
}else throw new Error(`Unknown mode ${a.mode}`);
result.wallMs=now()-started;result.load1End=load1();result.finished=new Date().toISOString();
await writeFile(a.out,JSON.stringify(result,null,1)+'\n');
console.log(`${a.mode}: ${frames?.length} frames, ${(result.wallMs/1000).toFixed(1)} s, wrote ${a.out}`);
