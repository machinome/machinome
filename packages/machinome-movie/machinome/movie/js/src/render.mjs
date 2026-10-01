// The renderer on the stage (design D8 of the react-stage change): serves the
// stage bundle, the viewer, the model and the pictures to headless Chromium,
// poses frames through window.film.setFrame, checks what the stage reports
// against what the frame asked for, proves the pixels in preview, and
// captures, caches and encodes the film in render.
import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,copyFile,rename,link,unlink} from 'node:fs/promises';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID} from 'node:crypto';
import {chromium} from 'playwright';
import {frameAt,srt,filmShots,shotActions,joinShows,reframeAt,modelSecondsAt} from './timeline.mjs';
import {replayTake,markAt} from './take.mjs';
import {viewerApiRefusal,filmSubject,PAPER_STAGE} from './episode.mjs';
import {fileHash,hash,json,command,sourceBase} from './util.mjs';
import {decodePng,hexColor,chromeMask,largestDifference,at,proveMark} from './pixels.mjs';
import {resolveWordTiming,validateWordFramesAtFps} from './words.mjs';
import {readSpeechTake} from './speech.mjs';
import {extractClips,pictureRect,clipCadence,drawnEnlargement} from './pictures.mjs';
import {SHOT_CACHE_SCHEMA,outputShotUnits,fingerprintShotUnits,shotCacheRoot,
  findShotGeneration,captureShotGeneration,assembleShotFrames} from './shot-cache.mjs';
import {buildReviewSamplePlan} from './review-samples.mjs';
import {reviewManifest} from './review-pack.mjs';
import {effectiveStyle} from './style.mjs';
import {buildFilmStage} from './stage-build.mjs';
import {measureSetsOn,reframeBoxes,reframeSets} from './layout.mjs';
import {treeState,treeLine,treeReleaseIssue,exportLine,exportReleaseIssue,exportProvenance,withoutSource} from './provenance.mjs';
import {exportFiles} from './export.mjs';

const here=dirname(fileURLToPath(import.meta.url));
// The two trees a film's records name a head of, the project's and
// Videomaker's own checkout, read and printed in the command's words
// (ADR-015): by preview and render once before the first frame, by check
// after its other lines. After them, the revision the model's export was
// made from and whether the project was dirty then, as the export's manifest
// records it and the film's load read it (ADR-019).
export async function readTrees(film,commandName){
  const trees={project:await treeState(film.paths.repository),workflow:await treeState(resolve(here,'..')),
    export:film.exportSource};
  for(const tree of ['project','workflow'])console.log(treeLine(tree,trees[tree],commandName));
  console.log(exportLine(trees.export,commandName));
  return trees;
}
const treeProvenance=trees=>({workflowHead:trees.workflow.head,workflowDirty:trees.workflow.dirty,
  projectHead:trees.project.head,projectDirty:trees.project.dirty,...exportProvenance(trees.export)});
// Headless Chromium with software WebGL: the browser every session renders in.
export const CHROMIUM_ARGS=['--use-angle=swiftshader','--enable-unsafe-swiftshader'];
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const sub=(a,b)=>a.map((v,i)=>v-b[i]),add=(a,b,s)=>a.map((v,i)=>v+b[i]*s);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const near=(a,b)=>Math.abs(a-b)<1e-9;
const inside=(r,box,slack=.5)=>r.x>=box.x-slack&&r.y>=box.y-slack&&r.x+r.width<=box.x+box.width+slack&&r.y+r.height<=box.y+box.height+slack;

// Every fading thing of a frame drawn as the plain/absent states whose
// weighted sum is the frame: pictures and marks between nothing and opaque.
// The weights sum to one; opacity compositing is affine in each separately.
export function fadeSubsets(frame){
  const fades=[];
  for(const [key,state] of Object.entries(frame.elements??{})){
    if(state.kind==='picture'&&state.shown&&state.opacity>0&&state.opacity<1)fades.push({key,opacity:state.opacity});
    if(state.kind==='view')for(const mark of state.marks)if(mark.opacity>0&&mark.opacity<1)fades.push({key,id:mark.id,opacity:mark.opacity});
  }
  if(!fades.length)return null;
  const variants=[];
  for(let mask=0;mask<2**fades.length;mask++){
    let weight=1;const elements={...frame.elements};
    fades.forEach((fade,j)=>{
      const included=Math.floor(mask/2**j)%2===1;
      weight*=included?fade.opacity:1-fade.opacity;
      const state=elements[fade.key];
      if(fade.id===undefined)elements[fade.key]=included?{...state,opacity:1}:{...state,shown:false,opacity:0};
      else elements[fade.key]={...state,marks:state.marks.flatMap(m=>m.id!==fade.id?[m]:included?[{...m,opacity:1}]:[])};
    });
    variants.push({elements,weight});
  }
  return variants;
}
// A picture shown at opacity zero is drawn as not shown: nothing of it reaches
// the pixels, and the blend of one picture needs no capture of it.
function withoutInvisible(frame){
  const elements={};
  for(const [key,state] of Object.entries(frame.elements))
    elements[key]=state.kind==='picture'&&state.shown&&state.opacity<=0?{...state,shown:false}:state;
  return {...frame,elements};
}
// The camera a view stands at, by name, when each move starts.
function lensChanges(film){
  const instants=[],fps=film.output.fps;
  for(const {chapter,shot} of filmShots(film)){
    const last=shot.end-shot.start-1/fps;
    for(const {cue,action} of shotActions(shot)){
      if(action.action!=='move')continue;
      const before=frameAt(film,shot.start+Math.min(cue.at,last)).elements[`${chapter.id}.${action.element}`];
      const a={fov:before.fov,up:before.up},b=film.cameras[action.camera];
      const sameUp=unit(a.up).every((v,i)=>Math.abs(v-unit(b.up)[i])<=1e-12);
      if(Math.abs(a.fov-b.fov)<1e-12&&sameUp)continue;
      for(const local of [cue.at,Math.min(action.until,last)])instants.push({time:shot.start+local,key:`${chapter.id}.${action.element}`,up:!sameUp,shotId:shot.id});
    }
  }
  return instants;
}
// The boxes the shipped paper sets draw their model stage, pictures and
// source-only panel in, as fractions of the frame (the old page's geometry);
// a posed frame checks the set's layout against them, as the old page did.
function knownSlotBox(set,slot){
  if(set==='source-only')return slot==='source'?PAPER_STAGE.paper:null;
  if(!PAPER_STAGE[set])return null;
  if(slot==='stage'||slot==='right'||/^plate(-\d+)?$/.test(slot))return PAPER_STAGE[set];
  if(/^full(-\d+)?$/.test(slot))return [0,0,1,1];
  return null;
}

async function stage(film,viewer,bundle) {
  const paths=new Map([['/viewer.js',resolve(viewer)],['/model/manifest.json',film.paths.manifest],
    ['/stage.js',bundle.js],['/stage.css',bundle.css],['/',resolve(here,'film.html')],
    ...await exportFiles(film.paths.manifest)]);
  for(const [name,media] of Object.entries(film.pictureMedia?.stills??{}))
    paths.set(`/pictures/stills/${name}`,media.file);
  for(const [name,media] of Object.entries(film.pictureMedia?.clips??{}))
    for(const n of media.extraction?.frames??[])
      paths.set(`/pictures/clips/${name}/${String(n).padStart(6,'0')}.png`,
        resolve(media.extraction.dir,`${String(n).padStart(6,'0')}.png`));
  const hashes={};for(const [url,file]of paths){
    if(url.startsWith('/pictures/clips/'))continue;
    hashes[url]=await fileHash(file);
  }
  for(const [name,media] of Object.entries(film.pictureMedia?.clips??{}))
    if(media.extraction)hashes[`/pictures/clips/${name}`]=media.extraction.key;
  return {paths,hashes};
}
// What the stage reads before its first frame (design D5).
export function stageConfig(film){
  const kinds=new Set();
  for(const chapter of film.chapters)for(const element of Object.values(chapter.elements))kinds.add(element.kind);
  const size=media=>({width:media.width,height:media.height});
  const required=film.viewerApi??{api:21,reasons:[]};
  return {movie:{id:film.id,title:film.title,series:film.series??film.title,style:effectiveStyle(film.style)},
    stage:{sets:Object.fromEntries(Object.entries(film.stage.sets).map(([kind,entry])=>[kind,{slots:entry.slots,props:entry.props??{}}])),
      elements:[...kinds].sort()},
    media:{stills:Object.fromEntries(Object.entries(film.pictureMedia?.stills??{}).map(([n,m])=>[n,size(m)])),
      clips:Object.fromEntries(Object.entries(film.pictureMedia?.clips??{}).map(([n,m])=>[n,size(m)]))},
    viewer:{required,refusal:viewerApiRefusal(required,'{declared}',filmSubject(film))},
    // A view on a clocked take restores its bank with the take's identity (ADR-012).
    ...(film.model?.timeMode==='take'?{take:{identity:film.take.identity}}:{})};
}

// The first id (sorted) at which two banks differ, or null.
function bankDifference(held,wanted){
  for(const id of [...new Set([...Object.keys(held??{}),...Object.keys(wanted)])].sort())
    if(!Object.is(held?.[id],wanted[id]))return id;
  return null;
}
const valueOf=v=>v===undefined?'nothing':JSON.stringify(v);
// The take time a frame's views are posed at: its shot's model time at the
// frame's instant (an outgoing shot's past its end, through a join).
function takeTimeOf(film,f){
  const shot=filmShots(film).find(s=>s.shot.id===f.shotId).shot;
  return modelSecondsAt(shot,f.time-shot.start);
}

// Replays every step of the take on the viewer's machine of the view element
// `key` (design D6 of the pose-a-take change, ADR-012): the bank before the
// step restored, the same move asked, and the request the viewer returns
// compared exactly with the record. Refuses on the first difference, naming
// the step and the field. The next frame restores its own whole bank.
async function replayTakeOnViewer(page,film,key){
  const {before}=replayTake(film.take);
  const answers=await page.evaluate(([key,identity,steps,before])=>{
    const machine=window.film.machine(key);
    if(!machine||typeof machine.move!=='function')return {error:`the viewer of ${key} gives no machine that moves`};
    return {requests:steps.map((step,i)=>{
      machine.restore({identity,bank:before[i]});
      const r=machine.move(step.input,step.to!==undefined?{to:step.to}:{by:step.by});
      return {origin:r.origin,end:r.end,commits:r.commits.map(c=>({fraction:c.fraction,value:c.value,targets:c.targets}))};
    })};
  },[key,film.take.identity,film.take.steps.map(({input,to,by})=>({input,to,by})),before]);
  const refuse=(step,i,field,given,recorded)=>{throw new Error(`The viewer does not reproduce the take: step ${step.id} (take.steps[${i}]), ${field}: the viewer gives ${given}, the take records ${recorded}`);};
  if(answers.error)throw new Error(`The viewer does not reproduce the take: ${answers.error}`);
  film.take.steps.forEach((step,i)=>{
    const r=answers.requests[i];
    for(const field of ['origin','end'])if(!Object.is(r[field],step[field]))refuse(step,i,field,valueOf(r[field]),valueOf(step[field]));
    if(r.commits.length!==step.commits.length)refuse(step,i,'commits',`${r.commits.length} commits`,`${step.commits.length}`);
    step.commits.forEach((commit,j)=>{
      const given=r.commits[j];
      for(const field of ['fraction','value'])if(!Object.is(given[field],commit[field]))refuse(step,i,`commits[${j}].${field}`,valueOf(given[field]),valueOf(commit[field]));
      const id=bankDifference(given.targets,commit.targets);
      if(id!==null)refuse(step,i,`commits[${j}].targets.${id}`,valueOf(given.targets[id]),valueOf(commit.targets[id]));
    });
  });
  return {steps:film.take.steps.length,matched:true};
}
// The clip spans a film shows: each picture's cue, and the continuation a
// transition shows past its shot's end.
function clipUses(film){
  const shots=filmShots(film);
  return shots.flatMap(({chapter,shot},i)=>shotActions(shot).flatMap(({cue,action})=>{
    const element=chapter.elements[action.element];
    if(element?.kind!=='picture'||element.clip===undefined)return [];
    const continuation=near(cue.until,shot.end-shot.start)?joinShows(shots[i+1]?.shot.transition):0;
    return [{name:element.clip,inPoint:element.inPoint??0,span:cue.until-cue.at+continuation}];
  }));
}

// One HTTP server for the stage's assets, serving one session at a time:
// a session mounts its handler and releases it when it ends. The command line
// makes one per session; a test run shares one across its sessions.
export async function assetServer(){
  let handler=null;
  const server=createServer((req,res)=>{
    if(handler)return handler(req,res);
    res.writeHead(503);res.end('No film session');
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  const origin=`http://127.0.0.1:${server.address().port}`;
  return {origin,
    mount(next){
      if(handler)throw new Error(`The asset server at ${origin} already serves a film session`);
      handler=next;return ()=>{if(handler===next)handler=null;};
    },
    close:()=>new Promise(r=>server.close(r))};
}

// A browser and an asset server may be given (a test run shares one of each);
// otherwise the session launches Chromium and makes a server, and closes both.
// A picture's enlargement is measured for a film `outputWidth` wide: the
// output's width in preview, the width it is rendered at in render.
export async function browserSession(film,viewer,width,captions,action,{browser:givenBrowser,assets:givenAssets,outputWidth=film.output.width}={}) {
  await extractClips(film,clipUses(film));
  const bundle=await buildFilmStage(film);
  const {paths,hashes}=await stage(film,viewer,bundle);
  const height=Math.round(film.output.height*width/film.output.width/2)*2;
  const cfg=stageConfig(film);
  const errors=[];
  const serve=async(req,res)=>{
    try{
      const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(cfg));return;}
      if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
      const file=paths.get(path);if(!file){res.writeHead(404);res.end('Not found');return;}
      res.setHeader('Content-Type',({'.js':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}[extname(file)])??'application/octet-stream');
      res.end(await readFile(file));
    }catch(error){errors.push(String(error));res.writeHead(500);res.end('Asset error');}
  };
  const assets=givenAssets??await assetServer(),release=assets.mount(serve);
  let browser=givenBrowser,page;
  try{
    browser??=await chromium.launch({headless:true,args:CHROMIUM_ARGS});
    page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    await page.goto(`${assets.origin}/`);
    await page.waitForFunction(()=>window.film||window.filmError,{},{timeout:60000});
    const error=await page.evaluate(()=>window.filmError);if(error)throw new Error(error);
    // The boxes a reframe moves its views between are the sets' layout,
    // measured on this page at its own size before the first frame and
    // attached to the film (ADR-010); a slot sized by what it holds is refused.
    const reframed=reframeSets(film);
    if(reframed.length)film.reframes=reframeBoxes(film,await measureSetsOn(page,film,reframed,
      {width,height,errors,refuse:e=>new Error(`Measuring the slots a reframe moves views between: ${e}`)}));
    let frames=0,viewerApi=null;
    const where=(f,t)=>`${f.shotId} at ${t.toFixed(2)} s`;
    // A mark is named as its author wrote it: a YAML annotation by its index
    // in the shot (#0), a movie's by its element and cue (cues[i].actions[j]).
    const markSubject=(shotId,key,id)=>{
      const shot=filmShots(film).find(s=>s.shot.id===shotId)?.shot,action=shot&&shotActions(shot).find(x=>x.id===id)?.action;
      return action?.annotation!==undefined?`#${action.annotation}`:`${key} ${id}`;
    };
    // Poses one picture and runs every check a posed frame has. The stage
    // sets its whole state by request, so nothing depends on what was posed
    // before; a pose repaints the whole page when anything outside the views'
    // canvases changed since the stage's last repaint.
    async function show(f,t,{pictureOnly=false,fresh=false}={}){
      if(errors.length)throw new Error(errors.join('\n'));
      const {transition,...request}=f;
      // A reframe is drawn live from the frame (ADR-010); the other joins
      // reach the stage as compositions, never on the frame.
      const reframe=transition?.kind==='reframe'?transition:null;
      const live=reframe?{transition:{kind:'reframe',progress:reframe.progress,boxes:reframe.boxes}}:{};
      const observed=await page.evaluate(f=>window.film.setFrame(f),{...request,...live,pictureOnly,fresh});
      viewerApi??=await page.evaluate(()=>window.film.apiVersion);
      const frameBox={x:0,y:0,width:observed.frame.width,height:observed.frame.height};
      for(const [key,state] of Object.entries(f.elements)){
        const seen=observed.elements[key],name=`${key} in ${where(f,t)}`;
        if(!seen)throw new Error(`Element did not reach the stage: ${name}`);
        const drawn=!['title','picture'].includes(state.kind)||state.shown;
        if(drawn&&!(seen.box?.width>0&&seen.box?.height>0))throw new Error(`Element has no box on the stage: ${name}`);
        const known=knownSlotBox(f.set,Object.keys(f.slots).find(slot=>f.slots[slot]===key));
        if(known&&known.map((v,i)=>v*(i%2?observed.frame.height:observed.frame.width))
          .some((v,i)=>Math.abs(v-[seen.box.x,seen.box.y,seen.box.width,seen.box.height][i])>1))
          throw new Error(`Film stage layout differs from the picture geometry: ${name}`);
        if(state.kind==='view'){
          for(const k of ['camera','target'])for(let i=0;i<3;i++)if(Math.abs(seen[k][i]-state.view[k][i])>1e-6)throw new Error(`Viewer did not adopt requested camera: ${name}`);
          if(viewerApi>=28){
            if(!(Math.abs(seen.fov-state.fov)<=1e-6))throw new Error(`Viewer did not adopt the requested field of view: ${name} (${seen.fov} instead of ${state.fov})`);
            const a=unit(seen.up),b=unit(state.up);
            if(!a.every((v,i)=>Math.abs(v-b[i])<=1e-6))throw new Error(`Viewer did not adopt the requested up direction: ${name}`);
          }
          const canvas=seen.canvas,sizes=()=>`canvas ${canvas?`${canvas.width.toFixed(1)}×${canvas.height.toFixed(1)}`:'absent'}, box ${seen.box.width.toFixed(1)}×${seen.box.height.toFixed(1)}`;
          if(!canvas||canvas.height<seen.box.height*.98||canvas.width<seen.box.width*.98)throw new Error(`Viewer canvas does not fill its view: ${name} (${sizes()})`);
          // A canvas left larger by a shrinking box is a stale picture (ADR-012).
          if(canvas.width>seen.box.width+1||canvas.height>seen.box.height+1)throw new Error(`Viewer canvas exceeds its view: ${name} (${sizes()})`);
          // A view on a take holds the bank its frame asked for, and at a
          // mark the bank the take recorded there (ADR-012).
          if(state.bank){
            const id=bankDifference(seen.bank,state.bank);
            if(id!==null)throw new Error(`Viewer bank differs from the frame: ${name}, ${id}: the viewer holds ${valueOf(seen.bank?.[id])}, the frame asks for ${valueOf(state.bank[id])}`);
            const mark=markAt(film,takeTimeOf(film,f));
            const other=mark===null?null:bankDifference(seen.bank,film.take.banks[mark]);
            if(other!==null)throw new Error(`Viewer bank differs from the take at mark ${mark}: ${name}, ${other}: the viewer holds ${valueOf(seen.bank?.[other])}, the take records ${valueOf(film.take.banks[mark][other])}`);
          }
          for(const mark of seen.marks){
            const cue=state.marks.find(m=>m.id===mark.id),label=`${f.shotId} ${markSubject(f.shotId,key,mark.id)}${cue?.text===undefined?` (${mark.kind})`:` '${cue.text}'`} at ${t.toFixed(2)} s`;
            const p=mark.anchor;
            if(!p||!inside({x:p.x,y:p.y,width:0,height:0},seen.box,0))throw new Error(`Annotation target is not on screen: ${label}`);
            if(mark.kind==='ring'){
              if(!inside(mark.rect,seen.box,0))throw new Error(`Ring target is not wholly on screen: ${label}`);
              const g=mark.ring;
              if(g.cx-g.rx<0||g.cy-g.ry<0||g.cx+g.rx>observed.frame.width||g.cy+g.ry>observed.frame.height)throw new Error(`Ring leaves the frame: ${label}`);
            }
            if(mark.text&&!inside(mark.text,frameBox))throw new Error(`Annotation text leaves the frame: ${label}`);
          }
          if(seen.marks.length!==state.marks.length)throw new Error(`Marks did not reach the picture: ${name}`);
        }else if(state.kind==='source'){
          if(!seen.fits)throw new Error(`Source excerpt overflows the panel: ${where(f,t)}; select fewer lines`);
          if(seen.text!==state.text)throw new Error(`Displayed code differs from source: ${name}`);
          const expected=state.emphasis.map(c=>c.token),actual=seen.emphasis.map(c=>c.text);
          if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error(`Source emphasis did not reach the picture: ${name}`);
        }else if(state.kind==='title'){
          if(state.shown&&state.words&&seen.revealed!==state.revealed)throw new Error(`Overlay word count differs from timeline: ${name} (${seen.revealed} instead of ${state.revealed})`);
          if(state.shown&&seen.text&&!inside(seen.text,frameBox))throw new Error(`Title leaves the frame: ${where(f,t)}`);
        }else if(state.kind==='picture'){
          if(!state.shown){if(seen.drawn)throw new Error(`Picture remained on screen outside cue: ${name}`);continue;}
          const media=film.pictureMedia[state.media==='still'?'stills':'clips'][state.name];
          if(!seen.drawn||!seen.natural)throw new Error(`Picture did not reach the page: ${name}`);
          const box=seen.box,r=pictureRect({width:media.width,height:media.height},[0,0,box.width,box.height],state.fit,state.view);
          const rect=[box.x+r[0]*box.width,box.y+r[1]*box.height,r[2]*box.width,r[3]*box.height];
          if([seen.drawn.x,seen.drawn.y,seen.drawn.width,seen.drawn.height].some((v,i)=>Math.abs(v-rect[i])>.5))
            throw new Error(`Picture geometry differs from timeline: ${name}`);
          for(const [start,size,from,extent] of [[seen.drawn.x,seen.drawn.width,box.x,box.width],[seen.drawn.y,seen.drawn.height,box.y,box.height]]){
            const framed=size>=extent-.5?start<=from+.5&&start+size>=from+extent-.5:start>=from-.5&&start+size<=from+extent+.5;
            if(!framed)throw new Error(`Picture view leaves the picture: ${name} (${state.name}); keep the view inside the picture or zoom in`);
          }
          if(media.format==='svg'){
            if(Math.abs(seen.natural.width/seen.natural.height-media.width/media.height)>media.width/media.height*.001)
              throw new Error(`SVG picture aspect differs from viewBox: ${name}`);
          }else if(seen.natural.width!==media.width||seen.natural.height!==media.height)
            throw new Error(`Picture natural size differs from probe: ${name}`);
          if(state.media==='clip'&&seen.frame!==state.frame)throw new Error(`Clip frame differs from timeline: ${name}`);
          const scale=drawnEnlargement(seen.drawn.width,seen.natural.width,width,outputWidth);
          if(media.format!=='svg'&&scale>media.upscale+1e-9)
            throw new Error(`${state.media==='still'?'Still':'Clip'} ${state.name} would be enlarged ${scale.toFixed(2)}× in ${name}; its upscale allowance is ${media.upscale}. Set upscale on the ${state.media}, place it in a smaller slot, or use a larger source.`);
          seen.enlargement=scale;
        }
      }
      // A reframe frame: each moving view is drawn in the frame's box, within
      // a pixel, and every other element at the join's progress as opacity.
      if(reframe)for(const [key,seen] of Object.entries(observed.elements)){
        const name=`${key} in ${where(f,t)}`,box=reframe.boxes[key];
        if(box){
          const wanted=box.map((v,i)=>v*(i%2?observed.frame.height:observed.frame.width)),drawn=[seen.box.x,seen.box.y,seen.box.width,seen.box.height];
          if(drawn.some((v,i)=>Math.abs(v-wanted[i])>1))
            throw new Error(`Reframe box differs from the timeline: ${name} (drawn ${drawn.map(v=>v.toFixed(1)).join(', ')}, the frame's ${wanted.map(v=>v.toFixed(1)).join(', ')})`);
        }else if(!(Math.abs(seen.opacity-reframe.progress)<=1e-3))
          throw new Error(`Reframe fade differs from the timeline: ${name} (opacity ${seen.opacity} instead of ${reframe.progress})`);
      }
      return observed;
    }
    const png=bytes=>'data:image/png;base64,'+bytes.toString('base64');
    // A frame with fading pictures or marks: the same instant with each drawn
    // plainly or not at all, composed as the weighted sum of picture-only
    // captures under the live chrome (design D10).
    async function showPicture(f,t,options={}){
      const g=withoutInvisible(f),variants=fadeSubsets(g);
      if(!variants)return show(g,t,options);
      const observed=await show(g,t,options),pictures=[];
      for(const {elements,weight} of variants){
        await show({...g,elements},t,{pictureOnly:true,fresh:true});
        pictures.push({src:png(await page.screenshot()),weight});
      }
      // The blended frame is picture-only only when this pose is: the stage
      // sets the page's state before its repaint, so the chrome is drawn
      // over the blend as over any other frame.
      Object.assign(observed,await page.evaluate(r=>window.film.composeMarkBlend(r),{pictures,pictureOnly:Boolean(options.pictureOnly)}));
      return observed;
    }
    // A picture of this instant without the film's chrome, posed and checked.
    async function capture(f,t){
      const observed=await showPicture(f,t,{pictureOnly:true});
      return {src:png(await page.screenshot()),observed};
    }
    // One film frame. Inside a transition it is composed from poses of the same
    // instant only: the stage draws captures of the pictures it is made of,
    // then the plate of a fade, under its live chrome. A fade poses one
    // picture; a dissolve, wipe or slide poses both. `override` replaces
    // frame fields for preview-only comparison frames; `elements` in it
    // replaces the named element states.
    async function pose(t,override={},{pictureOnly=false,fresh=false}={}){
      const baseline=frameAt(film,t);
      const f={...baseline,...override,elements:{...(override.shotId&&override.shotId!==baseline.shotId?{}:baseline.elements),...(override.elements??{})}};
      const x=f.transition;let observed;
      // A reframe frame is a live frame: no capture, no composition.
      if(!x||x.kind==='reframe')observed=await showPicture(f,t,{pictureOnly,fresh});
      else{
        const outgoing=x.outgoing;
        let request;
        if(x.kind==='fade'){
          const picture=await capture(x.picture==='outgoing'?outgoing:f,t);
          observed=picture.observed;
          request={images:[{src:picture.src,x:0}],plate:{color:x.color,opacity:x.plate}};
        }else{
          // Whole pixels, so the proofs can be exact: the edge or offset is round(p·W).
          const s=Math.round(x.progress*width),left=x.direction==='left';
          const a=(await capture(outgoing,t)).src,b=await capture(f,t);
          observed={...b.observed,offset:s};
          request={images:x.kind==='dissolve'?[{src:b.src,x:0},{src:a,x:0,opacity:1-x.progress}]
            :x.kind==='wipe'?[{src:b.src,x:0},{src:a,x:0,columns:left?[0,width-s]:[s,width]}]
            :[{src:a,x:left?-s:s},{src:b.src,x:left?width-s:s-width}]};
        }
        Object.assign(observed,await page.evaluate(r=>window.film.compose(r),{...request,pictureOnly}));
      }
      frames++;return Object.assign(f,{observed});
    }
    // Resolve the viewer's API before the action reads it, at the first frame
    // that places a view, so a viewer below the movie's API is refused before
    // anything is captured. This probe is not one of the frames the action
    // checks, and is not counted as one.
    const firstView=filmShots(film).find(({chapter,shot})=>Object.values(shot.places).some(k=>chapter.elements[k].kind==='view'));
    await pose(firstView?firstView.shot.start:0);frames=0;
    // A film of a clocked take holds the viewer to the record before its
    // first frame, on the instance that probe mounted (ADR-012).
    const takeReplay=film.model.timeMode==='take'&&firstView?await replayTakeOnViewer(page,film,
      `${firstView.chapter.id}.${Object.values(firstView.shot.places).find(k=>firstView.chapter.elements[k].kind==='view')}`):null;
    const info={width,height,browser:browser.version(),viewerApi,hashes,requiredViewerApi:film.viewerApi,
      ...(takeReplay?{takeReplay}:{}),
      stage:{sha256:bundle.sha256,cssSha256:bundle.cssSha256,modules:bundle.modules??film.stage.modules}};
    const result=await action({page,pose,info});
    if(errors.length)throw new Error(errors.join('\n'));
    return {...result,...info,framesChecked:frames};
  }finally{
    // A given browser keeps running; closing the page closes its own context.
    if(givenBrowser)await page?.close();else await browser?.close();
    release();if(!givenAssets)await assets.close();
  }
}

// The actions of the film that preview proves, with where they are.
function actionsWith(film,test){
  return filmShots(film).flatMap(({chapter,shot})=>shotActions(shot).filter(x=>test(x.action,chapter.elements[x.action.element]))
    .map(x=>({...x,chapter,shot,key:`${chapter.id}.${x.action.element}`,element:chapter.elements[x.action.element]})));
}
const label=x=>x.action.overlay!==undefined?`#${x.action.overlay}`:x.action.annotation!==undefined?`#${x.action.annotation}`:
  x.action.highlight!==undefined?`#${x.action.highlight}`:x.action.picture!==undefined?`#${x.action.picture}`:
  x.action.emphasis!==undefined?`#${x.action.emphasis}`:x.id;

// An entrance whose end falls inside the exit, or an exit that starts inside
// the entrance, has no instant at which the element is drawn as it is
// without them; those two checks are recorded as skipped, not passed.
function overlapped(action,cue,phase){
  if(!action.enter||!action.leave)return null;
  const enterEnd=cue.at+action.enter.duration,leaveStart=cue.until-action.leave.duration;
  if(enterEnd<=leaveStart+1e-9)return null;
  if(/^enter-end$|^end$/.test(phase))return 'the entrance ends inside the exit';
  if(/^leave-start$/.test(phase)||phase==='leave/start')return 'the exit starts inside the entrance';
  return null;
}

export async function preview(film,{viewer,width=960,captions=[],browser,assets}) {
  if(film.source!=='movie'&&!Object.keys(film.wordTiming??{}).length)await resolveWordTiming(film,shot=>readSpeechTake(film,shot));
  const dir=resolve(film.paths.build,'preview');await mkdir(dir,{recursive:true});
  const fps=film.output.fps,duration=film.output.durationSeconds;
  const trees=await readTrees(film,'preview');
  const result=await browserSession(film,viewer,width,captions,async({page,pose})=>{
    const shots=filmShots(film);
    const grabBytes=async()=>page.screenshot();
    // Highlights first, while every material is pristine: the same instant
    // without its cue, with it, without it, with it. The cue must change the
    // pixels, restore() must return them exactly, and re-applying must match.
    const highlightChecks=[];
    for(const x of actionsWith(film,a=>a.action==='highlight')){
      const t=x.shot.start+(x.cue.at+x.cue.until)/2,state=frameAt(film,t).elements[x.key];
      const capture=async lit=>{await pose(t,{transition:null,elements:{[x.key]:lit?state:{...state,highlight:null}}});return grabBytes();};
      const plain=await capture(false),lit=await capture(true),plainAgain=await capture(false),litAgain=await capture(true);
      const name=`highlight-${x.shot.id}-${label(x).replace('#','')}`;
      const fail=async(check,message,before,after)=>{
        await writeFile(resolve(dir,`${name}-${check}-before.png`),before);
        await writeFile(resolve(dir,`${name}-${check}-after.png`),after);
        throw new Error(`${message}: ${x.shot.id} ${label(x)} at ${t.toFixed(2)} s; inspect preview/${name}-${check}-{before,after}.png`);
      };
      if(!plain.equals(plainAgain))await fail('restore','Highlight did not restore exactly',plain,plainAgain);
      if(lit.equals(plain))await fail('visible','Highlight did not reach the pixels',plain,lit);
      if(!lit.equals(litAgain))await fail('reapply','Highlight did not re-apply identically',lit,litAgain);
      highlightChecks.push({shotId:x.shot.id,element:x.key,cue:x.id,index:x.action.highlight,time:t,changed:true,restored:true,reapplied:true});
    }
    const samples=[];
    for(const {shot} of shots){
      const times=[0,.5,.95].map(u=>shot.start+(shot.end-shot.start)*u);
      for(const {cue,action} of shotActions(shot)){
        if(action.action==='type')times.push(shot.start+cue.at+action.over/2);
        if(action.action==='highlight')times.push(shot.start+(cue.at+cue.until)/2);
        if(['ring','label','arrow'].includes(action.action)){
          for(const u of [0,.25,.5,.75])times.push(shot.start+cue.at+(cue.until-cue.at)*u);
          times.push(shot.start+Math.max(cue.at,cue.until-1/fps));
          if(action.enter){
            times.push(shot.start+cue.at+action.enter.duration/2);
            if(cue.at+action.enter.duration<cue.until-1e-9)times.push(shot.start+cue.at+action.enter.duration);
          }
          if(action.leave)times.push(shot.start+cue.until-action.leave.duration,shot.start+cue.until-action.leave.duration/2);
        }
      }
      for(const t of [...new Set(times)].filter(t=>t<shot.end-1e-9).sort((a,b)=>a-b)){
        const posed=await pose(t);
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}.png`);
        await page.screenshot({path:file});
        const marks=Object.entries(posed.observed.elements).filter(([,r])=>r.kind==='view'&&r.marks?.length);
        samples.push(marks.length?{time:t,file,marks:Object.fromEntries(marks.map(([k,r])=>[k,r.marks]))}:{time:t,file});
      }
    }
    // Each animated mark is compared against the same instant with the mark
    // drawn plainly and absent. These captures isolate its shot from a join.
    const entranceChecks=[];
    for(const x of actionsWith(film,a=>['ring','label','arrow'].includes(a.action)&&(a.enter||a.leave))){
      const {cue,action,shot}=x,checks=[];
      if(action.enter)checks.push(['enter-start',cue.at],['enter',cue.at+action.enter.duration/2],['enter-end',cue.at+action.enter.duration]);
      if(action.leave)checks.push(['leave-start',cue.until-action.leave.duration],['leave',cue.until-action.leave.duration/2]);
      for(const [phase,local] of checks){
        const skip=overlapped(action,cue,phase);
        if(skip){entranceChecks.push({shotId:shot.id,element:x.key,mark:x.id,index:action.annotation,phase,skipped:skip});continue;}
        if(phase==='enter-end'&&local>=cue.until-1e-9){
          entranceChecks.push({shotId:shot.id,element:x.key,mark:x.id,index:action.annotation,phase,kind:action.enter.kind,time:shot.start+cue.until,
            skipped:'cue ends at this exclusive boundary'});
          continue;
        }
        const time=shot.start+local,frame=frameAt(film,time),state=frame.elements[x.key],asWritten=state.marks.find(m=>m.id===x.id);
        if(!asWritten)throw new Error(`Annotation proof has no active cue: ${shot.id} ${label(x)} ${phase} at ${time.toFixed(2)} s`);
        const full={...state,marks:state.marks.map(m=>m.id===x.id?{...m,opacity:1,drawn:1}:m)};
        const without={...state,marks:state.marks.filter(m=>m.id!==x.id)};
        const grab=async s=>{
          const posed=await pose(time,{transition:null,...(s?{elements:{[x.key]:s}}:{})},{fresh:true});
          const bytes=await page.screenshot();return {posed,bytes,image:decodePng(bytes)};
        };
        const composed=await grab(),whole=await grab(full),absent=await grab(without);
        const observed=composed.posed.observed.elements[x.key].marks.find(m=>m.id===x.id);
        const kind=phase.startsWith('leave')?action.leave.kind:action.enter.kind;
        const name=`entrance-${shot.id}-${label(x).replace(/[#\[\]\.]/g,'')}-${phase}`,at=`${shot.id} ${label(x)} ${phase} at ${time.toFixed(2)} s`;
        let proof;
        try{proof=proveMark(phase,{composed:composed.image,full:whole.image,without:absent.image},
          {where:at,entrance:kind,opacity:asWritten.opacity,inside:observed.inside,outside:observed.outside,text:observed.text,
            chrome:composed.posed.observed.chrome});}
        catch(error){
          for(const [tag,picture] of [['composed',composed],['full',whole],['without',absent]])
            await writeFile(resolve(dir,`${name}-${tag}.png`),picture.bytes);
          throw new Error(`${error.message}; inspect preview/${name}-{composed,full,without}.png`);
        }
        const check={shotId:shot.id,element:x.key,mark:x.id,index:action.annotation,phase,kind,time,opacity:asWritten.opacity,drawn:asWritten.drawn,...proof};
        if(phase==='enter'||(phase==='leave'&&!action.enter)){
          await pose(time,{transition:null},{fresh:true});const first=await page.screenshot();
          await pose((time+duration/2)%duration,{transition:null},{fresh:true});
          await pose(time,{transition:null},{fresh:true});const again=await page.screenshot();
          if(!first.equals(again)){
            await writeFile(resolve(dir,`${name}-replay-before.png`),first);await writeFile(resolve(dir,`${name}-replay-after.png`),again);
            throw new Error(`Annotation entrance replay is not deterministic: ${at}; inspect preview/${name}-replay-{before,after}.png`);
          }
          check.replay=true;
        }
        entranceChecks.push(check);
      }
    }
    // Word reveals are checked against the stage's actual visible-word count,
    // not merely the timeline's arithmetic; compare first and last pixels.
    const revealChecks=[];
    for(const x of actionsWith(film,a=>a.action==='show'&&a.reveal)){
      const {cue,action,shot}=x,reveal=action.reveal;
      const first=reveal.timing==='spoken'?Math.max(cue.at,reveal.onsets[0]):cue.at;
      const last=reveal.timing==='spoken'?Math.max(cue.at,reveal.onsets.at(-1)):cue.at+reveal.duration;
      const records=[],pictures=[];
      for(const local of [first,(first+last)/2,last]){
        const time=shot.start+Math.min(local,cue.until-1e-8);
        const posed=await pose(time,{transition:null},{fresh:true}),state=posed.elements[x.key],shown=posed.observed.elements[x.key].revealed;
        if(shown!==state.revealed)throw new Error(`Reveal count differs from timeline: ${shot.id} ${label(x)} at ${time.toFixed(2)} s`);
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}-reveal-${label(x).replace(/[#\[\]\.]/g,'')}-${records.length}.png`);
        const bytes=await page.screenshot({path:file});samples.push({time,file,reveal:x.key});
        records.push({time,shown,expected:state.revealed,file});pictures.push(bytes);
      }
      const words=x.element.text.match(/\S+/gu)?.length;
      if(records.some((r,i)=>i&&r.shown<records[i-1].shown)||records.at(-1).shown!==words)
        throw new Error(`Reveal does not reach all words in order: ${shot.id} ${label(x)}`);
      if(records.at(-1).shown>1&&pictures[0].equals(pictures.at(-1)))throw new Error(`Reveal did not change the picture: ${shot.id} ${label(x)}`);
      revealChecks.push({shotId:shot.id,element:x.key,index:action.overlay,timing:reveal.timing,samples:records,pixelsDiffer:!pictures[0].equals(pictures.at(-1))});
    }
    // Hold the model and every other element at this same video instant while
    // comparing the authored title, a fully opaque title, and its absence.
    const fadeChecks=[];
    for(const x of actionsWith(film,(a,e)=>e?.kind==='title'&&a.action==='show'&&(a.enter||a.leave))){
      const {cue,action,shot}=x,phases=[];
      if(action.enter)phases.push(['enter-start',cue.at],['enter-mid',cue.at+action.enter.duration/2],['enter-end',cue.at+action.enter.duration]);
      if(action.leave)phases.push(['leave-start',cue.until-action.leave.duration],['leave-mid',cue.until-action.leave.duration/2]);
      for(const [phase,local] of phases){
        if(local>=cue.until-1e-9){fadeChecks.push({shotId:shot.id,element:x.key,index:action.overlay,phase,skipped:'cue ends at this exclusive boundary'});continue;}
        const skip=overlapped(action,cue,phase);
        if(skip){fadeChecks.push({shotId:shot.id,element:x.key,index:action.overlay,phase,skipped:skip});continue;}
        const time=shot.start+local,state=frameAt(film,time).elements[x.key];
        if(!state.shown)throw new Error(`Title fade proof has no active cue: ${shot.id} ${label(x)} ${phase}`);
        const capture=async s=>{await pose(time,{transition:null,...(s?{elements:{[x.key]:s}}:{})},{fresh:true});return page.screenshot();};
        const composed=await capture(),whole=await capture({...state,opacity:1}),absent=await capture({...state,shown:false,opacity:0});
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}-title-${label(x).replace(/[#\[\]\.]/g,'')}-${phase}.png`);
        await writeFile(file,composed);samples.push({time,file,title:x.key,phase});
        const midpoint=phase.endsWith('mid'),boundary=phase==='enter-start'?'absent':'full';
        if(midpoint?(composed.equals(whole)||composed.equals(absent)):!composed.equals(boundary==='absent'?absent:whole)){
          const name=`title-${shot.id}-${label(x).replace(/[#\[\]\.]/g,'')}-${phase}`;
          for(const [tag,bytes] of [['composed',composed],['full',whole],['without',absent]])await writeFile(resolve(dir,`${name}-${tag}.png`),bytes);
          throw new Error(`Title fade proof failed: ${shot.id} ${label(x)} ${phase}; inspect preview/${name}-{composed,full,without}.png`);
        }
        fadeChecks.push({shotId:shot.id,element:x.key,index:action.overlay,phase,time,file,opacity:state.opacity,equals:midpoint?'neither':boundary});
      }
    }
    // Source words lit as they are spoken: none before the first onset, one
    // more at each onset, none after the clear; the first lit instant replays.
    const emphasisChecks=[];
    for(const x of actionsWith(film,a=>a.action==='emphasize')){
      const {action,shot}=x,d=shot.end-shot.start,onsets=action.words.map(w=>w.at);
      const checks=[['before',Math.max(0,Math.min(...onsets)-1/fps)],...action.words.map((w,i)=>[`word-${i}`,w.at]),['clear',action.until]];
      const records=[];let firstImage,firstTime;
      for(const [phase,local] of checks){
        if(local>=d-1e-9){records.push({phase,skipped:'shot ends at this exclusive boundary'});continue;}
        const time=shot.start+local,posed=await pose(time,{transition:null},{fresh:true});
        const words=posed.observed.elements[x.key].emphasis.map(m=>m.token);
        const lit=phase==='before'||phase==='clear'?[]:action.words.filter(w=>w.at<=local+1e-9).map(w=>w.token);
        const expected=posed.elements[x.key].emphasis.map(e=>e.token);
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}-emphasis-${label(x).replace(/[#\[\]\.]/g,'')}-${phase}.png`);
        const bytes=await page.screenshot({path:file});samples.push({time,file,emphasis:x.key,phase});
        if(JSON.stringify([...words].sort())!==JSON.stringify([...expected].sort())||!lit.every(tk=>words.includes(tk)))
          throw new Error(`Source emphasis count differs: ${shot.id} ${phase}; inspect ${file}`);
        if(phase==='word-0'){firstImage=bytes;firstTime=time;}
        records.push({phase,time,words,file});
      }
      if(firstImage){await pose(firstTime,{transition:null},{fresh:true});
        if(!firstImage.equals(await page.screenshot()))throw new Error(`Source emphasis replay is not deterministic: ${shot.id}`);}
      emphasisChecks.push({shotId:shot.id,element:x.key,cue:x.id,index:action.emphasis,samples:records,replay:Boolean(firstImage)});
    }
    const pictureChecks=[];
    for(const x of actionsWith(film,(a,e)=>e?.kind==='picture'&&a.action==='show')){
      const {cue,action,shot}=x,end=shot.start+cue.until,last=(Math.ceil(end*fps-1e-9)-1)/fps;
      const locals=[cue.at,...(action.view??[]).map(k=>Math.min(k.at,last-shot.start)),
        ...(action.enter?[cue.at+action.enter.duration/2,cue.at+action.enter.duration]:[]),
        ...(action.leave?[cue.until-action.leave.duration,cue.until-action.leave.duration/2]:[]),Math.max(cue.at,last-shot.start)];
      const records=[];
      for(const local of [...new Set(locals)].filter(t=>t>=cue.at-1e-9&&t<cue.until-1e-9).sort((a,b)=>a-b)){
        const time=shot.start+local,posed=await pose(time),seen=posed.observed.elements[x.key],state=posed.elements[x.key];
        if(!state?.shown)throw new Error(`Picture proof has no active cue: ${shot.id} ${label(x)} at ${time.toFixed(2)} s`);
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}-picture-${label(x).replace(/[#\[\]\.]/g,'')}-${records.length}.png`);
        await page.screenshot({path:file});samples.push({time,file,picture:x.key});
        records.push({time,file,media:state.media,view:state.view,box:seen.box,drawn:seen.drawn,natural:seen.natural,
          // The clip frame the timeline shows; show() has refused any drawn
          // frame that differs, and at opacity zero nothing is drawn.
          ...(state.media==='clip'?{frame:state.frame,clipSeconds:state.clipSeconds}:{})});
      }
      const opacityAt=time=>frameAt(film,time).elements[x.key]?.opacity??0;
      const replayTime=records.find(r=>opacityAt(r.time)>=1-1e-9)?.time??records.find(r=>opacityAt(r.time)>.01)?.time??records[0].time;
      const replay=async(time,tag,message)=>{
        await pose(time);const before=await page.screenshot();
        await pose((time+duration/2)%duration);
        await pose(time);const after=await page.screenshot();
        if(!before.equals(after)){
          const name=`picture-${shot.id}-${label(x).replace(/[#\[\]\.]/g,'')}-${tag}`;
          await writeFile(resolve(dir,`${name}-before.png`),before);await writeFile(resolve(dir,`${name}-after.png`),after);
          throw new Error(`${message}: ${shot.id} ${label(x)} at ${time.toFixed(2)} s; inspect preview/${name}-{before,after}.png`);
        }
      };
      await replay(replayTime,'replay','Picture replay is not deterministic');
      const partialTime=records.find(r=>{const a=opacityAt(r.time);return a>.01&&a<1-.01;})?.time;
      if(partialTime!==undefined)await replay(partialTime,'partial-replay','Partial picture replay is not deterministic');
      const fades=[];
      for(const field of ['enter','leave'])if(action[field]){
        const d=action[field].duration,checks=field==='enter'?[['start',cue.at],['mid',cue.at+d/2],['end',cue.at+d]]:[['start',cue.until-d],['mid',cue.until-d/2]];
        for(const [phase,local] of checks){
          if(local>=cue.until-1e-9){fades.push({field,phase,skipped:'cue ends at this exclusive boundary'});continue;}
          const skip=overlapped(action,cue,field==='enter'?(phase==='end'?'end':phase):`leave/${phase}`);
          if(skip){fades.push({field,phase,skipped:skip});continue;}
          const time=shot.start+local,state=frameAt(film,time).elements[x.key];
          const grab=async s=>{await pose(time,{transition:null,elements:{[x.key]:s}},{fresh:true});return page.screenshot();};
          const composed=await grab(state),whole=await grab({...state,opacity:1}),absent=await grab({...state,shown:false,opacity:0});
          const reference=field==='enter'&&phase==='start'?'absent':phase==='mid'?'neither':'full';
          const passed=reference==='neither'?!composed.equals(whole)&&!composed.equals(absent):composed.equals(reference==='full'?whole:absent);
          const name=`picture-${shot.id}-${label(x).replace(/[#\[\]\.]/g,'')}-${field}-${phase}`;
          for(const [tag,bytes] of [['composed',composed],['full',whole],['without',absent]])await writeFile(resolve(dir,`${name}-${tag}.png`),bytes);
          if(!passed)throw new Error(`Picture fade proof failed: ${shot.id} ${label(x)} ${field}-${phase}; inspect preview/${name}-{composed,full,without}.png`);
          fades.push({field,phase,time,equals:reference});
        }
      }
      pictureChecks.push({shotId:shot.id,element:x.key,index:action.picture,media:x.element.still!==undefined?'still':'clip',samples:records,replay:true,replayTime,
        replayOpacity:opacityAt(replayTime),partialReplay:partialTime!==undefined,partialTime,fades});
    }
    // Each transition: stills at its first frame, quarters, midpoint and last
    // frame (a fade in or out: first, middle, last), and proofs from the plain
    // pictures of the same instant, every one leaving out the chrome.
    const transitionChecks=[],W=width;
    for(const {shot} of shots)for(const field of ['fadeIn','transition','fadeOut']){
      const spec=shot[field];if(!spec)continue;
      const d=spec.duration,start=field==='fadeOut'?shot.end-d:shot.start,middle=start+d/2;
      const last=(Math.ceil((start+d)*fps-1e-9)-1)/fps,kind=field==='transition'?spec.kind:'fade';
      const instants=[...new Set(field==='transition'?[start,start+d/4,middle,start+3*d/4,last]:[start,middle,last])];
      const stills=[];
      for(const time of instants){
        await pose(time);
        const file=resolve(dir,`${String(samples.length).padStart(3,'0')}-${shot.id}-${field}.png`);
        await page.screenshot({path:file});samples.push({time,file,transition:field});stills.push(file);
      }
      const name=field==='transition'?`transition-${shot.id}`:`${field}-${shot.id}`;
      const grab=async(time,override,options)=>{const posed=await pose(time,override,{fresh:true,...options});const bytes=await page.screenshot();return {posed,bytes,image:decodePng(bytes)};};
      const prove=async(largest,limit,time,kept)=>{
        if(largest<=limit)return;
        for(const [k,v] of Object.entries(kept))await writeFile(resolve(dir,`${name}-${k}.png`),v.bytes);
        throw new Error(`Transition proof failed: ${kind} ${field==='transition'?'into':field==='fadeIn'?'fading in':'fading out'} shot ${shot.id} at ${time.toFixed(2)} s (largest difference ${largest}, allowed ${limit}); inspect preview/${name}-{${Object.keys(kept).join(',')}}.png`);
      };
      const check={shotId:shot.id,field,kind,instants,stills};
      if(kind==='reframe'){
        // A live join (ADR-010): every posed frame of it has had its moving
        // boxes and its fade checked against the timeline (show); here, the
        // ends. At its first frame each moving view is in its outgoing slot's
        // measured box; at its end, the reframe at progress 1 is the incoming
        // frame without a join, pixel for pixel, each view in its incoming
        // slot's box. The midpoint's opacities are recorded.
        const measured=film.reframes[shot.id],views={},opacities={};
        const drawnBox=(posed,key)=>{const b=posed.observed.elements[key].box;return [b.x,b.y,b.width,b.height];};
        const inPixels=(posed,box)=>box.map((v,i)=>v*(i%2?posed.observed.frame.height:posed.observed.frame.width));
        const differs=(a,b)=>a.some((v,i)=>Math.abs(v-b[i])>1);
        const fail=async(message,kept)=>{
          for(const [k,v] of Object.entries(kept))await writeFile(resolve(dir,`${name}-${k}.png`),v.bytes);
          throw new Error(`Reframe proof failed: ${message}; inspect preview/${name}-{${Object.keys(kept).join(',')}}.png`);
        };
        const first=await grab(start);
        for(const [key,{from,to}] of Object.entries(measured)){
          const drawn=drawnBox(first.posed,key),wanted=inPixels(first.posed,from.box);
          if(differs(drawn,wanted))await fail(`at its first frame (${start.toFixed(2)} s) the view ${key} of shot ${shot.id} is drawn at ${drawn.map(v=>v.toFixed(1)).join(', ')}, not in the box of slot ${from.slot} of set ${from.set}, ${wanted.map(v=>v.toFixed(1)).join(', ')}`,{first});
          views[key]={from:{set:from.set,slot:from.slot,box:wanted},to:{set:to.set,slot:to.slot},first:drawn};
        }
        const mid=await grab(middle);
        for(const [key,seen] of Object.entries(mid.posed.observed.elements))if(!measured[key])opacities[key]=seen.opacity;
        const end=Math.min(start+d,(Math.ceil(shot.end*fps-1e-9)-1)/fps),ending=await grab(end,{transition:reframeAt(film,shot.id,d)}),incoming=await grab(end,{transition:null});
        for(const [key,{to}] of Object.entries(measured)){
          const drawn=drawnBox(ending.posed,key),wanted=inPixels(ending.posed,to.box);
          if(differs(drawn,wanted))await fail(`at its end (${end.toFixed(2)} s) the view ${key} of shot ${shot.id} is drawn at ${drawn.map(v=>v.toFixed(1)).join(', ')}, not in the box of slot ${to.slot} of set ${to.set}, ${wanted.map(v=>v.toFixed(1)).join(', ')}`,{end:ending});
          Object.assign(views[key].to,{box:wanted});views[key].end=drawn;
        }
        if(!ending.bytes.equals(incoming.bytes))await fail(`at its end (${end.toFixed(2)} s) the reframe into shot ${shot.id} is not the incoming frame without a join`,{end:ending,incoming});
        Object.assign(check,{progress:mid.posed.transition.progress,views,opacities,endEqualsIncoming:true});
      }else if(kind!=='fade'){
        const composed=await grab(middle),x=composed.posed.transition,p=x.progress,s=composed.posed.observed.offset;
        const incoming=await grab(middle,{transition:null}),outgoing=await grab(middle,{...x.outgoing,transition:null});
        // The live chrome is the incoming set's; the plain frames compared
        // show each set's own. All of it is left out.
        const mask=chromeMask(W,composed.image.height,[composed,incoming,outgoing].flatMap(g=>g.posed.observed.chrome));
        const A=outgoing.image,B=incoming.image,left=x.direction==='left';
        let largest,limit=0,kept={outgoing,incoming,composed};
        if(kind==='dissolve'){limit=2;largest=largestDifference(composed.image,(px,y,k)=>(1-p)*at(A,px,y,k)+p*at(B,px,y,k),mask);}
        else if(kind==='wipe')largest=largestDifference(composed.image,(px,y,k)=>(left?px>=W-s:px<s)?at(B,px,y,k):at(A,px,y,k),mask);
        else{
          // The two pictures alone, without chrome, at their offsets; the chrome stays put above them.
          const a=await grab(middle,{...x.outgoing,transition:null},{pictureOnly:true}),b=await grab(middle,{transition:null},{pictureOnly:true});
          largest=largestDifference(composed.image,(px,y,k)=>left?(px<W-s?at(a.image,px+s,y,k):at(b.image,px-W+s,y,k)):(px>=s?at(a.image,px-s,y,k):at(b.image,px-s+W,y,k)),mask);
          kept={outgoing:a,incoming:b,composed};
        }
        await prove(largest,limit,middle,kept);
        Object.assign(check,{progress:p,offset:kind==='dissolve'?undefined:s,largestDifference:largest,picturesDiffer:!A.rgb.equals(B.rgb)});
        if(!check.picturesDiffer)check.note='the two pictures are identical at the midpoint, so this proof shows nothing';
      }else{
        // A fade: the plate blends its colour with the plain picture as its easing says,
        // and is exactly the colour, outside the chrome, at its full point.
        const quarters=field==='transition'?[start+d/4,start+3*d/4]:[start+d/4];
        let largest=0;
        for(const time of quarters){
          const composed=await grab(time),x=composed.posed.transition,C=hexColor(x.color),a=x.plate;
          const plain=await grab(time,x.picture==='outgoing'?{...x.outgoing,transition:null}:{transition:null});
          const mask=chromeMask(W,composed.image.height,[composed,plain].flatMap(g=>g.posed.observed.chrome));
          const found=largestDifference(composed.image,(px,y,k)=>a*C[k]+(1-a)*at(plain.image,px,y,k),mask);
          await prove(found,2,time,{[x.picture]:plain,composed});
          largest=Math.max(largest,found);
        }
        const full=field==='transition'?middle:field==='fadeIn'?start:last;
        const composed=await grab(full),x=composed.posed.transition,C=hexColor(x.color);
        const mask=chromeMask(W,composed.image.height,composed.posed.observed.chrome);
        await prove(x.plate===1?largestDifference(composed.image,(px,y,k)=>C[k],mask):Infinity,0,full,{composed});
        Object.assign(check,{progress:frameAt(film,middle).transition.plate,largestDifference:largest,exactColor:true,colorAt:full});
      }
      // Replay: the midpoint, another instant, the midpoint again.
      await pose(middle);const before=await page.screenshot();
      await pose((middle+duration/2)%duration);await pose(middle);const after=await page.screenshot();
      if(!before.equals(after)){
        await writeFile(resolve(dir,`${name}-replay-before.png`),before);await writeFile(resolve(dir,`${name}-replay-after.png`),after);
        throw new Error(`Transition replay is not deterministic: ${shot.id} at ${middle.toFixed(2)} s; inspect preview/${name}-replay-{before,after}.png`);
      }
      check.replay=true;
      transitionChecks.push(check);
    }
    // A changed lens must reach the picture: a world offset of s beside the
    // target, at distance d, projects to (H/2)·s/(d·tan(fov/2)) pixels on the
    // view's canvas; a changed up must put a point above the target above it.
    const cameraChecks=[];
    for(const instant of lensChanges(film)){
      const f=await pose(instant.time,{transition:null}),state=f.elements[instant.key],C=state.view.camera,T=state.view.target;
      const d=Math.hypot(...sub(T,C)),forward=unit(sub(T,C)),up=unit(state.up),right=unit(cross(forward,up)),s=.01*d;
      const [p0,p1,pu]=await page.evaluate(([key,points])=>window.film.project(key,points),[instant.key,[T,add(T,right,s),add(T,up,s)]]);
      const H=f.observed.elements[instant.key].canvas.height;
      const measured=p0&&p1?Math.hypot(p1.x-p0.x,p1.y-p0.y):NaN,expected=(H/2)*s/(d*Math.tan(state.fov*Math.PI/360));
      const at=`${instant.shotId} at ${instant.time.toFixed(2)} s`;
      const keep=async()=>{const file=resolve(dir,`lens-${instant.shotId}-${instant.time.toFixed(2)}.png`);await page.screenshot({path:file});return file;};
      if(!(Math.abs(measured/expected-1)<=.02))throw new Error(`Field of view did not reach the picture: ${at} (measured ${measured} px, expected ${expected} px); inspect ${await keep()}`);
      const upAbove=instant.up?Boolean(pu&&pu.y<p0.y):undefined;
      if(instant.up&&!upAbove)throw new Error(`Camera up did not reach the picture: ${at}; inspect ${await keep()}`);
      cameraChecks.push({shotId:instant.shotId,element:instant.key,time:instant.time,fov:state.fov,up:state.up,measured,expected,...(instant.up?{upAbove}:{})});
    }
    // Real-browser check: revisiting an exact pose must restore the pixels.
    const replay=duration*.23;
    await pose(replay);const original=await page.screenshot();
    await pose(duration*.87);await pose(replay);const restored=await page.screenshot();
    if(!original.equals(restored)){
      await writeFile(resolve(dir,'replay-before.png'),original);
      await writeFile(resolve(dir,'replay-after.png'),restored);
      throw new Error('Pixel replay is not deterministic; inspect preview/replay-{before,after}.png');
    }
    // Bad camera requests must leave the actual mounted view intact.
    const preserved=await page.evaluate(()=>{const v=window.film.viewer;if(!v)return null;const before=JSON.stringify(v.view());try{v.setView({camera:[1,NaN,3],target:[0,0,0]});return false;}catch{return before===JSON.stringify(v.view());}});
    if(preserved===false)throw new Error('Invalid camera request changed viewer state');
    return {samples,pixelReplay:true,invalidCameraPreserved:preserved??'no view in this film',...(highlightChecks.length?{highlightChecks}:{}),...(cameraChecks.length?{cameraChecks}:{}),
      ...(transitionChecks.length?{transitionChecks}:{}),...(entranceChecks.length?{entranceChecks}:{}),
      ...(revealChecks.length?{revealChecks}:{}),...(fadeChecks.length?{fadeChecks}:{}),
      ...(emphasisChecks.length?{emphasisChecks}:{}),...(pictureChecks.length?{pictureChecks}:{})};
  },{browser,assets});
  result.provenance=treeProvenance(trees);
  await json(resolve(dir,'report.json'),result);
  // A contact sheet for quickly inspecting the chosen shots, then individual PNGs.
  await command('ffmpeg',['-y','-v','error','-pattern_type','glob','-i',resolve(dir,'*.png'),'-vf',`scale=480:-1,tile=3x${Math.ceil(result.samples.length/3)}`,'-frames:v','1',resolve(film.paths.build,'storyboard.jpg')]);
  return result;
}

// Before capturing a frame, a measured cue re-reads the exact cached take:
// a cache hit must not launder a removed or changed speech take. A movie's
// takes are compared with the ones it was resolved from.
async function refreshWordTiming(film){
  const before=film.wordTiming??{};
  const now=await resolveWordTiming(film,shot=>readSpeechTake(film,shot));
  if(film.source==='movie')for(const [shotId,entry] of Object.entries(before))
    if(now[shotId]?.sha256!==entry.sha256)throw new Error(`The cached take of shot ${shotId} changed since the movie was resolved; run check again`);
  film.wordTiming=film.source==='movie'?before:now;
}

// The picture cues of a film for the manifest: each shown picture with its
// source size, allowance and (when measured in this render) peak enlargement.
function pictureRecords(film,fps,peaks){
  const shots=filmShots(film);
  return shots.flatMap(({chapter,shot},i)=>shotActions(shot).flatMap(({cue,action,id})=>{
    const element=chapter.elements[action.element];
    if(element?.kind!=='picture'||action.action!=='show')return [];
    const media=element.still!==undefined?'still':'clip',name=element[media],probe=film.pictureMedia[`${media}s`][name];
    const key=`${chapter.id}.${action.element}`,record={shotId:shot.id,element:key,cue:id,...(action.picture!==undefined?{index:action.picture}:{}),
      kind:media,name,peak:probe.format==='svg'?null:peaks.get(`${shot.id}/${key}`)??null,allowance:probe.format==='svg'?null:probe.upscale,
      width:probe.width,height:probe.height,averageRate:probe.averageRate,frameCount:probe.frameCount};
    if(media==='clip'){
      const globalStart=shot.start+cue.at,first=Math.ceil(globalStart*fps-1e-9)/fps,phase=Math.max(0,first-globalStart),start=element.inPoint??0;
      const continuation=near(cue.until,shot.end-shot.start)?joinShows(shots[i+1]?.shot.transition):0;
      const cadence=clipCadence(probe.timestamps,start,start+cue.until-cue.at+continuation,fps,phase);
      Object.assign(record,{filmRate:fps,dropped:cadence.dropped,repeated:cadence.repeated});
    }
    return [record];
  }));
}

export async function render(film,{viewer,width=film.output.width,fps=film.output.fps,audio=null,label='rehearsal',browser,assets}) {
  await refreshWordTiming(film);
  validateWordFramesAtFps(film,fps);
  const captions=audio?.captions??[];
  const style=effectiveStyle(film.style);
  const fontFile=async(name,weight='Regular')=>{
    const path=await command('fc-match',['-f','%{file}',`${name}:style=${weight}`]).catch(()=>null);
    return path?{path,sha256:await fileHash(path)}:null;
  };
  const family=style.fontFamily.split(',')[0].trim();
  const fontRecord=await fontFile(family);
  const filmBold=await fontFile(family,'Bold');
  const codeFontRecord=await fontFile('DejaVu Sans Mono');
  const codeBold=await fontFile('DejaVu Sans Mono','Bold');
  const fontFaces={film:{regular:fontRecord,bold:filmBold},code:{regular:codeFontRecord,bold:codeBold}};
  const peaks=new Map();
  const trees=await readTrees(film,'render');
  const report=await browserSession(film,viewer,width,captions,async({page,pose,info})=>{
    // Every page file (the stage bundle, its CSS, the page, the viewer, the
    // model) is a common input: a changed one recaptures every shot.
    const sharedHashes=Object.fromEntries(Object.entries(info.hashes).filter(([url])=>!url.startsWith('/pictures/')));
    // The model's manifest is keyed without its source record, which is
    // provenance and no picture input (ADR-019); it is served as it is.
    const keyedHashes={...sharedHashes,'/model/manifest.json':
      hash(JSON.stringify(withoutSource(JSON.parse(await readFile(film.paths.manifest,'utf8')))))};
    const commonKey=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,hashes:keyedHashes,browser:info.browser,
      viewerApi:info.viewerApi,width,height:info.height,fps,
      // Film duration stays a common input, deliberately conservative
      // (remove-progress-rule D4): no drawn element reads it any more.
      duration:film.output.durationSeconds,format:film.format,style,stage:{sets:film.stage.sets,elements:film.stage.elements},
      fonts:fontFaces,
      renderer:await fileHash(resolve(here,'render.mjs')),timeline:await fileHash(resolve(here,'timeline.mjs')),
      take:await fileHash(resolve(here,'take.mjs')),
      pictures:await fileHash(resolve(here,'pictures.mjs')),
      easing:await fileHash(resolve(here,'easing.mjs')),
      words:await fileHash(resolve(here,'words.mjs')),
      pixels:await fileHash(resolve(here,'pixels.mjs')),
      sourceRenderer:await fileHash(resolve(here,'code.mjs')),
      shotCache:await fileHash(resolve(here,'shot-cache.mjs')),
      dependencies:await fileHash(resolve(here,'../package-lock.json'))}));
    const {count,units}=outputShotUnits(film,fps);
    const reviewSamples=buildReviewSamplePlan(film,units,fps);
    await fingerprintShotUnits(film,units,commonKey);
    const root=shotCacheRoot(film.paths.build),selections=new Map(),shotReports=[];
    // The trees' heads and dirt, and the export's revision and dirt, are
    // provenance, never a key (ADR-015, ADR-019).
    const captureProvenance={...treeProvenance(trees),
      episodeSha256:await fileHash(film.paths.episode),productionSha256:await fileHash(film.paths.production),
      viewerSha256:sharedHashes['/viewer.js'],modelSha256:sharedHashes['/model/manifest.json'],
      stageSha256:sharedHashes['/stage.js'],browser:info.browser,commonKey};
    const started=Date.now();
    let capturedFrames=0,reusedFrames=0;
    for(const unit of units){
      let selected=await findShotGeneration(root,unit,commonKey,width,info.height);
      const reused=Boolean(selected);
      if(!selected){
        selected=await captureShotGeneration(root,unit,commonKey,width,info.height,async frame=>{
          const posed=await pose(frame.time);
          for(const [key,seen] of Object.entries(posed.observed.elements))if(seen.enlargement!==undefined){
            const id=`${posed.shotId}/${key}`;peaks.set(id,Math.max(peaks.get(id)??0,seen.enlargement));
          }
          const bytes=await page.screenshot();capturedFrames++;
          if(frame.index%90===0)console.log(`Frames ${frame.index+1}/${count} · ${((Date.now()-started)/1000).toFixed(0)}s elapsed`);
          return bytes;
        },{...captureProvenance,shotKey:unit.key});
      }else reusedFrames+=unit.frames.length;
      selections.set(unit.shotId,selected);
      shotReports.push({shotId:unit.shotId,start:unit.start,end:unit.end,
        indices:unit.frames.map(frame=>frame.index),key:unit.key,
        captured:reused?0:unit.frames.length,reused:reused?unit.frames.length:0,
        generation:selected.generation,indexSha256:await fileHash(resolve(selected.generation,'index.json')),
        origin:selected.index.provenance});
    }
    const dir=await assembleShotFrames(root,units,selections,count);
    const identity=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,commonKey,shots:shotReports.map(s=>s.key)}));
    return {identity,dir,count,reviewSamples,
      cache:{schema:SHOT_CACHE_SCHEMA,commonKey,capturedFrames,reusedFrames,shots:shotReports}};
  },{browser,assets,outputWidth:width});
  const output=resolve(film.paths.build,`${label}.mp4`);
  const duration=film.output.durationSeconds;
  const publicationId=randomUUID(),pendingOutput=resolve(film.paths.build,`${label}.pending-${publicationId}.mp4`);
  const args=['-y','-v','error','-framerate',String(fps),'-start_number','0','-i',resolve(report.dir,'%06d.png')];
  if(audio)args.push('-i',audio.mix,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k');
  args.push('-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-t',String(duration),pendingOutput);
  console.log('Encoding '+output);await command('ffmpeg',args);
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',pendingOutput]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  if(Number(video.nb_read_frames)!==report.count||video.width!==report.width||video.height!==report.height)throw new Error('Encoded video does not match requested frames/dimensions');
  if(audio&&!probe.streams.some(s=>s.codec_type==='audio'))throw new Error('Encoded video has no audio');
  if(probe.format)probe.format.filename=output;
  const thumbnail=resolve(film.paths.build,'thumbnail.png'),pendingThumbnail=`${thumbnail}.pending-${publicationId}`;
  await copyFile(resolve(report.dir,`${String(Math.min(report.count-1,Math.floor(Math.min(10,duration*.5)*fps))).padStart(6,'0')}.png`),pendingThumbnail);
  const subtitles=audio?resolve(film.paths.build,`${label}.srt`):null;
  const pendingSubtitles=subtitles?`${subtitles}.pending-${publicationId}`:null;
  if(pendingSubtitles)await writeFile(pendingSubtitles,srt(captions));
  const pictureCues=pictureRecords(film,fps,peaks);
  const usedStills=new Set(pictureCues.filter(c=>c.kind==='still').map(c=>c.name)),usedClips=new Set(pictureCues.filter(c=>c.kind==='clip').map(c=>c.name));
  const publicMedia=media=>{const {file,...record}=media;return record;};
  const pictures={stills:Object.fromEntries(Object.entries(film.pictureMedia?.stills??{}).map(([name,media])=>[name,{...publicMedia(media),
      cues:pictureCues.filter(c=>c.kind==='still'&&c.name===name)}])),
    clips:Object.fromEntries(Object.entries(film.pictureMedia?.clips??{}).map(([name,media])=>[name,{...publicMedia(media),
      cues:pictureCues.filter(c=>c.kind==='clip'&&c.name===name)}])),cues:pictureCues};
  const pictureReleaseIssues=[];
  for(const [kind,names] of [['still',usedStills],['clip',usedClips]])for(const name of names){
    const media=film.pictureMedia[kind==='still'?'stills':'clips'][name];
    for(const field of ['credit','rights'])if(media[field]===null)pictureReleaseIssues.push(`${kind} ${name} has unresolved ${field}`);
    if(!media.committed)pictureReleaseIssues.push(`${kind} ${name} is not committed at project HEAD`);
  }
  // A movie document may leave out release: then no description is written
  // and the film is not release-ready.
  const template=film.release?.descriptionTemplate;
  if(template===undefined)console.warn('No release.descriptionTemplate: description.md is not written');
  const description=template===undefined?null:await readFile(resolve(sourceBase(film),template),'utf8');
  if(description!==null&&(usedStills.size||usedClips.size)&&!description.includes('{{pictureCredits}}'))
    pictureReleaseIssues.push('Description template lacks {{pictureCredits}} for shown pictures');
  const pictureCredits=[...Array.from(usedStills,name=>({kind:'stills',name})),
    ...Array.from(usedClips,name=>({kind:'clips',name}))].map(({kind,name})=>{
    const media=film.pictureMedia[kind][name];
    return `${name}: ${media.credit??`[PICTURE CREDIT PENDING: ${name}]`}`;
  }).join('\n');
  // Every reason the film is not release-ready, in words (ADR-015).
  const releaseIssues=[...(description===null?['no release.descriptionTemplate: description.md is not written']:[]),
    ...['simulationUrl','sourceUrl'].filter(field=>!film.release?.[field]).map(field=>`release.${field} is unresolved`),
    ...pictureReleaseIssues,
    ...['project','workflow'].map(tree=>treeReleaseIssue(tree,trees[tree])).filter(Boolean),
    ...[exportReleaseIssue(trees.export)].filter(Boolean)];
  const releaseReady=releaseIssues.length===0;
  const descriptionOutput=resolve(film.paths.build,'description.md'),pendingDescription=`${descriptionOutput}.pending-${publicationId}`;
  if(description!==null)await writeFile(pendingDescription,description
    .replaceAll('{{simulationUrl}}',film.release.simulationUrl??'[PUBLIC SIMULATION URL PENDING]')
    .replaceAll('{{sourceUrl}}',film.release.sourceUrl??'[PUBLIC SOURCE URL PENDING]')
    .replaceAll('{{pictureCredits}}',pictureCredits));
  const manifestOutput=resolve(film.paths.build,`${label}-manifest.json`),pendingManifest=`${manifestOutput}.pending-${publicationId}`;
  const outputSha256=await fileHash(pendingOutput);
  const manifest={...report,fps,output,outputSha256,stageSha256:report.stage.sha256,
    audio:audio?.records??[],subtitles:pendingSubtitles?{file:subtitles,sha256:await fileHash(pendingSubtitles),burnedIn:false}:null,
    episode:film,probe,pictures,pictureReleaseIssues,releaseIssues,releaseReady,
    provenance:{...treeProvenance(trees),font:fontRecord,codeFont:codeFontRecord,fontFaces,
      episodeSha256:await fileHash(film.paths.episode),productionSha256:await fileHash(film.paths.production),
      stageSha256:report.stage.sha256,stageCssSha256:report.stage.cssSha256,
      ffmpeg:(await command('ffmpeg',['-version'])).split('\n')[0]}};
  await writeFile(pendingManifest,JSON.stringify(manifest,null,2)+'\n');
  // A failed encode has not touched the prior output. Through the publication
  // window its old bytes remain reachable; a crash after the MP4 replacement
  // leaves the old manifest visibly stale by its output SHA-256.
  const previous=`${output}.previous-${publicationId}`;let backedUp=false;
  try{await link(output,previous);backedUp=true;}catch(error){if(error.code!=='ENOENT')throw error;}
  await rename(pendingOutput,output);
  await rename(pendingThumbnail,thumbnail);
  if(pendingSubtitles)await rename(pendingSubtitles,subtitles);
  if(description!==null)await rename(pendingDescription,descriptionOutput);
  await rename(pendingManifest,manifestOutput);
  if(backedUp)await unlink(previous).catch(error=>console.warn(`Previous-output backup remains: ${error.message}`));
  // The film transaction is complete. Review is an optional post-publication
  // artifact from its encoded bytes; failure never rewrites or fails the film.
  try{
    const pack=await reviewManifest(manifestOutput);
    console.log(`Review pack: ${pack.generation}${pack.reused?' (verified reuse)':''}`);
  }catch(error){
    console.warn(`review pack failed; film published: ${error.message}; retry: node bin/videomaker.mjs review ${manifestOutput}`);
  }
  return output;
}
