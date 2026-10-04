// The live session (the live-server change, ADR-021; README, "live"): one
// process per film, on the loopback interface, that loads the film as `check`
// does, serves the renderer's stage page and the frame function to a browser,
// and reloads when the film's inputs change. A movie frame is `frameAt` of
// the film in this process, on the renderer's grid; the browser computes
// none. What it answers of a generation is pure, below.
import {spawn} from 'node:child_process';
import {watch} from 'node:fs';
import {readFile,readdir,stat} from 'node:fs/promises';
import {basename,dirname,extname,join,relative,resolve,sep} from 'node:path';
import {checkSource,commandOptions} from './check.mjs';
import {assetServer,stageConfig} from './render.mjs';
import {extractClips} from './pictures.mjs';
import {filmFiles,clipUses,filmAssets,FILM_PAGE} from './film-assets.mjs';
import {hash} from './util.mjs';
import {frameAt,filmShots} from './timeline.mjs';

// The frame the route gives for `t`: the output frame nearest `t` on the
// renderer's grid (round(t·fps)/fps, as outputShotUnits counts frames),
// clamped to the film's first and last frames. A `t` that is not a finite
// number is refused, naming it.
export function frameFor(film,t){
  if(typeof t!=='number'||!Number.isFinite(t))
    throw new RangeError(`The frame needs t, a finite number of seconds; got ${t===undefined?'nothing':typeof t==='string'?JSON.stringify(t):String(t)}`);
  const fps=film.output.fps,count=Math.round(film.output.durationSeconds*fps);
  const index=Math.min(Math.max(Math.round(t*fps),0),count-1);
  return frameAt(film,index/fps);
}

// The document's marks sorted by time, as check's take line lists them.
const marksOf=film=>Object.entries(film.marks??{}).sort((a,b)=>a[1]-b[1]).map(([name,time])=>({name,time}));
// The take a film carries, keyed by the block it comes from (a document
// records no take name): a clocked take, its length in take seconds and
// where its document is served; or the posed loop, its period and marks in
// model seconds (the take seconds of a loop).
function takesOf(film){
  const duration=film.model.expectedDurationSeconds,marks=marksOf(film);
  return film.model.timeMode==='take'?{take:{kind:'clocked',duration,marks,url:'/take.json'}}
    :{loop:{kind:'loop',duration,marks}};
}

// The outline of a film as a session serves it at `width` (/film.json):
// times in video seconds except under `takes`. The output is the session's
// geometry: `width` and the renderer's height for it.
export function outline(film,{width,number,loadedAt,stageSha256,speech,refusal=null}){
  const {output}=film,shots=filmShots(film);
  return {id:film.id,title:film.title,
    output:{width,height:Math.round(output.height*width/output.width/2)*2,fps:output.fps,duration:output.durationSeconds},
    chapters:film.chapters.map(c=>({id:c.id,start:c.start,end:c.end})),
    shots:shots.map(({chapter,shot})=>({id:shot.id,chapter:chapter.id,start:shot.start,end:shot.end,set:shot.set,
      join:shot.transition?{kind:shot.transition.kind,duration:shot.transition.duration}:null,model:shot.model})),
    cues:shots.flatMap(({shot})=>(shot.cues??[]).map((cue,i)=>({shot:shot.id,id:`cues[${i}]`,
      at:shot.start+cue.at,until:cue.until===undefined?null:shot.start+cue.until}))),
    takes:takesOf(film),speech,stage:{sha256:stageSha256},viewer:{api:(film.viewerApi??{api:21}).api},
    generation:{number,loadedAt},refusal};
}

// The take document of a film on a clocked take (/take.json; design D11):
// its length, its marks and its take block, verbatim, which is what the
// pose rule (`bankAt` of src/take.mjs) reads; null for a posed loop.
export function takeDocument(film){
  if(film.model?.timeMode!=='take')return null;
  return {model:{expectedDurationSeconds:film.model.expectedDurationSeconds},marks:film.marks,take:film.take};
}

// ----- the session -----

// Changes within this long of the first are one reload (design D7).
export const SETTLE_MS=200;
const KEEP_ALIVE_MS=15_000;
const PLAYER={'/':'index.html','/player.js':'player.js','/player.css':'player.css'};
const TYPES={'.html':'text/html','.js':'text/javascript','.css':'text/css','.json':'application/json','.wav':'audio/wav'};
const exists=path=>stat(path).then(()=>true,()=>false);

// The film's inputs (design D7): the files a change to which can change what
// the session serves, and the directory of the cached takes. Never anything
// the tool writes: the resolved document, the stage bundle, the player, the
// preview, the shot cache and the extracted frames are not inputs.
async function inputsOf(film){
  const {paths}=film,files=new Set([paths.episode,paths.production,paths.manifest,
    resolve(paths.build,'narration.wav'),resolve(paths.build,'captions.json')]);
  // Every project file the stage bundle read, by the names it records
  // (ADR-013): the modules, what they import, their stylesheets.
  const record=await readFile(resolve(paths.build,'stage','inputs.json'),'utf8').then(JSON.parse,()=>null);
  for(const {path} of record?.inputs??[])
    if(typeof path==='string'&&path.startsWith('project/'))files.add(resolve(paths.repository,path.slice('project/'.length)));
  for(const excerpt of Object.values(film.excerpts??{}))files.add(resolve(paths.repository,excerpt.file));
  for(const kind of ['stills','clips'])for(const media of Object.values(film.pictureMedia?.[kind]??{}))if(media.file)files.add(media.file);
  return {files:[...files].sort(),dirs:[resolve(paths.build,'audio')]};
}

// One accepted load (design D3), or the error that refuses it.
async function loadGeneration(source,{viewer,width},previous){
  const {film,bundle}=await checkSource(source,{viewer,width});
  const bundlePath=commandOptions(film,{viewer}).viewer;
  await extractClips(film,clipUses(film));
  const files=await filmFiles(film,bundlePath,bundle);
  // `/` is the player's; the stage page is /film.html, its files at the root.
  const paths=new Map(files.paths);paths.delete('/');paths.set('/film.html',FILM_PAGE);
  const config=stageConfig(film);
  // What the stage page boots from, and what a viewer mounted on the export loads.
  const stageSha256=hash(JSON.stringify({page:files.hashes['/'],script:bundle.sha256,stylesheet:bundle.cssSha256,
    config:hash(JSON.stringify(config))}));
  const exportSha256=hash(JSON.stringify(Object.entries(files.hashes)
    .filter(([url])=>url==='/viewer.js'||url.startsWith('/model/')).sort(([a],[b])=>a<b?-1:a>b?1:0)));
  return {number:(previous?.number??0)+1,loadedAt:new Date().toISOString(),film,bundle,config,paths,stageSha256,exportSha256,
    exportChanged:previous?previous.exportSha256!==exportSha256:false,inputs:await inputsOf(film),
    serve:filmAssets({paths,config,onError:error=>console.error(String(error))})};
}

// The nearest existing directory at or above `path`, or null.
async function nearest(path){
  for(let dir=path;;dir=dirname(dir)){
    if(await exists(dir))return dir;
    if(dirname(dir)===dir)return null;
  }
}
// What to watch for `inputs`: each directory an input lies in, with the names
// in it that are inputs (or any entry, for the cached takes), and, for an
// input whose directory does not exist yet, its nearest existing ancestor
// with the name on the way to it. Never recursive.
async function watchPlan(inputs){
  const plan=new Map(),add=(dir,name)=>{
    const entry=plan.get(dir)??{any:false,names:new Set()};
    if(name===null)entry.any=true;else entry.names.add(name);
    plan.set(dir,entry);
  };
  const toward=async path=>{const at=await nearest(dirname(path));if(at)add(at,relative(at,path).split(sep)[0]);};
  for(const file of inputs.files)if(await exists(dirname(file)))add(dirname(file),basename(file));else await toward(file);
  for(const dir of inputs.dirs)if(await exists(dir))add(dir,null);else await toward(dir);
  return plan;
}
// What a stat poll compares: each input file's size, time and inode, and the
// entries of each input directory.
const statLine=path=>stat(path).then(s=>`${s.size}:${s.mtimeMs}:${s.ino}`,()=>'absent');
async function signature(inputs){
  const parts=[];
  for(const file of inputs.files)parts.push(`${file}\0${await statLine(file)}`);
  for(const dir of inputs.dirs){
    const names=await readdir(dir).catch(()=>null);
    if(names===null){parts.push(`${dir}\0absent`);continue;}
    for(const name of names.sort())parts.push(`${join(dir,name)}\0${await statLine(join(dir,name))}`);
  }
  return parts.join('\n');
}

// The session (design D3 to D9). The first load must succeed, or this throws
// what `check` would; a later failed load is a refusal and the previous
// generation stays served.
export async function live(source,{viewer,width=960,port=0,poll=0,open=false}={}){
  if(!Number.isInteger(port)||port<0||port>65535)throw new Error('--port must be an integer from 0 to 65535');
  if(!Number.isInteger(poll)||poll<0)throw new Error('--poll must be a whole number of milliseconds (0 watches instead of polling)');
  let current=await loadGeneration(source,{viewer,width},null),refusal=null;
  const subscribers=new Set();
  const send=(res,kind,data)=>res.write(`event: ${kind}\ndata: ${JSON.stringify(data)}\n\n`);
  const broadcast=(kind,data)=>{for(const res of subscribers)send(res,kind,data);};
  const announced=g=>({number:g.number,loadedAt:g.loadedAt,stageSha256:g.stageSha256,exportChanged:g.exportChanged});

  // ----- routes (design D4) -----
  const text=(res,status,body)=>{res.writeHead(status,{'Content-Type':'text/plain; charset=utf-8'});res.end(body);};
  const json=(res,value)=>{res.writeHead(200,{'Content-Type':'application/json'});res.end(JSON.stringify(value));};
  async function file(res,path,missing){
    let bytes;
    try{bytes=await readFile(path);}catch(error){if(error.code==='ENOENT')return text(res,404,missing);throw error;}
    res.writeHead(200,{'Content-Type':TYPES[extname(path)]??'application/octet-stream'});res.end(bytes);
  }
  async function handle(req,res){
    res.setHeader('Cache-Control','no-store');
    if(req.method!=='GET'&&req.method!=='HEAD')return text(res,405,'Method not allowed');
    const g=current,url=new URL(req.url,'http://localhost'),path=url.pathname,build=g.film.paths.build;
    try{
      if(path==='/film.json'){
        const speech={mix:await exists(resolve(build,'narration.wav')),captions:await exists(resolve(build,'captions.json'))};
        return json(res,outline(g.film,{width,number:g.number,loadedAt:g.loadedAt,stageSha256:g.stageSha256,speech,refusal}));
      }
      if(path==='/frame'){
        const raw=url.searchParams.get('t'),t=raw===null||raw.trim()===''?undefined:Number(raw);
        if(t===undefined||!Number.isFinite(t))
          return text(res,400,`The frame needs t, a finite number of seconds (/frame?t=12.4); got ${raw===null?'no t':JSON.stringify(raw)}`);
        return json(res,frameFor(g.film,t));
      }
      if(path==='/take.json'){const doc=takeDocument(g.film);return doc?json(res,doc):text(res,404,'No take document');}
      if(path==='/narration.wav'||path==='/captions.json')return file(res,resolve(build,path.slice(1)),'Not found');
      if(Object.hasOwn(PLAYER,path))return file(res,resolve(build,'player',PLAYER[path]),'The player is not built');
      if(path==='/events'){
        res.writeHead(200,{'Content-Type':'text/event-stream','Connection':'keep-alive'});
        send(res,'generation',announced(g));
        if(refusal)send(res,'refused',refusal);
        subscribers.add(res);req.on('close',()=>subscribers.delete(res));
        return;
      }
      return g.serve(req,res);
    }catch(error){
      console.error(String(error));
      if(!res.headersSent)text(res,500,'Live session error');else res.end();
    }
  }

  // ----- the watcher (design D7) -----
  let watchers=[],pollTimer=null,armed=null,closed=false,settle=null,reloading=null,again=false;
  function disarm(){for(const w of watchers)w.close();watchers=[];clearTimeout(pollTimer);pollTimer=null;armed=null;}
  // Watches (or polls) the inputs of the generation just accepted, in place
  // of the previous generation's.
  async function arm(inputs){
    disarm();
    if(closed)return;
    const token=armed={};
    if(poll){
      let last=await signature(inputs);
      const tick=async()=>{
        const now=await signature(inputs);
        if(closed||armed!==token)return;
        if(now!==last){last=now;changed();}
        pollTimer=setTimeout(tick,poll);
      };
      if(armed===token)pollTimer=setTimeout(tick,poll);
      return;
    }
    for(const [dir,entry] of await watchPlan(inputs)){
      try{
        const w=watch(dir,(_,name)=>{if(name==null||entry.any||entry.names.has(String(name)))changed();});
        w.on('error',error=>console.error(`Watching ${dir} failed: ${error.message}; run live with --poll`));
        watchers.push(w);
      }catch(error){console.error(`Watching ${dir} failed: ${error.message}; run live with --poll`);}
    }
  }
  function changed(){
    if(closed)return;
    if(reloading){again=true;return;}
    if(settle)return;
    settle=setTimeout(()=>{
      settle=null;
      reloading=reload().finally(()=>{reloading=null;if(again){again=false;changed();}});
    },SETTLE_MS);
  }
  async function reload(){
    broadcast('loading',{at:new Date().toISOString()});
    let next;
    try{next=await loadGeneration(source,{viewer,width},current);}
    catch(error){
      refusal={message:error.message,at:new Date().toISOString()};
      console.error(error.message);
      broadcast('refused',refusal);
      return;
    }
    if(closed)return;
    // Replaced whole, then watched by its own inputs, then announced.
    current=next;refusal=null;
    await arm(next.inputs);
    broadcast('generation',announced(next));
  }

  // ----- the server (design D4) -----
  let assets;
  try{assets=await assetServer({port});}
  catch(error){
    if(error.code==='EADDRINUSE')throw new Error(`Port ${port} is in use on 127.0.0.1; choose another with --port, or 0 for any free port`);
    throw error;
  }
  const release=assets.mount(handle);
  await arm(current.inputs);
  const keepAlive=setInterval(()=>{for(const res of subscribers)res.write(': keep-alive\n\n');},KEEP_ALIVE_MS);
  const address=`${assets.origin}/`;
  // Best effort: a missing or failing xdg-open changes nothing.
  if(open){
    try{const child=spawn('xdg-open',[address],{stdio:'ignore',detached:true});child.on('error',()=>{});child.unref();}catch{}
  }
  let closing=null;
  // Stops watching, waits for a reload in flight, ends every event stream
  // and closes the server; the port is free when it resolves (design D9).
  function close(){
    closing??=(async()=>{
      closed=true;
      clearTimeout(settle);settle=null;disarm();clearInterval(keepAlive);
      await reloading;
      for(const res of subscribers)res.end();
      subscribers.clear();
      release();await assets.close();
    })();
    return closing;
  }
  return {origin:assets.origin,generation:()=>current,close};
}
