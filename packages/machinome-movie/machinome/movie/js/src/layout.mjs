// The layout `check` measures (the check-measures-the-stage change, ADR-009):
// a movie document's slot boxes are its sets' layout, drawn only by the stage,
// so when the movie shows a picture, `check` poses each set kind its shots use,
// once, with no element placed, on the page the renderer serves (the bundle,
// src/film.html, the stage config) with a stub viewer whose mount is never
// called, at the output size. It refuses what the measured boxes let it
// refuse: a picture enlarged beyond its allowance, before any take is read,
// and a picture view that leaves the picture, once the takes resolve its
// times, in the words a YAML episode's pictures are refused in
// (src/pictures.mjs). On the same page it also measures the text each shot
// shows, wholly shown: the size of a source panel's code and the lines of a
// title and its subtitle, which `check` reports and never judges (the
// proofs-report-the-look change, ADR-017). Nothing memoizes it: it runs once
// per `check`.
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {assetServer,stageConfig,CHROMIUM_ARGS} from './render.mjs';
import {pictureRect} from './pictures.mjs';
import {wholeSource} from './code.mjs';
import {frameAt,movingViews} from './timeline.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const PAGE=resolve(here,'film.html');
// boot() requires a viewer factory; no view is placed, so mount is never called.
const STUB_VIEWER="window.MachinomeViewer={mount(){throw new Error('The layout probe mounts no viewer');}};\n";
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const number=v=>String(+v.toFixed(1));
const size=box=>`${number(box[2])}×${number(box[3])}`;
// A slot whose box `check` trusts: it does not change with what the set's
// slots hold, and a picture placed in it has a box.
export const trusted=slot=>Boolean(slot?.fixed&&slot.picture[2]>0&&slot.picture[3]>0);

// Every `show` of a picture element a shot's cue fires, with where it is
// placed, from an unresolved or a resolved document alike.
export function picturesShown(doc){
  const out=[];
  for(const chapter of doc.chapters)for(const shot of chapter.shots)for(const cue of shot.cues??[])for(const action of cue.actions){
    const element=chapter.elements[action.element];
    if(element?.kind!=='picture'||action.action!=='show')continue;
    const media=element.still!==undefined?'still':'clip';
    out.push({chapter,shot,cue,action,element,media,name:element[media],set:shot.set,
      slot:Object.keys(shot.places).find(slot=>shot.places[slot]===action.element),key:`${chapter.id}.${action.element}`});
  }
  return out;
}

// Every reframe of a document, unresolved or resolved: the shot, the shot
// before it, and the view elements it moves with the slot holding each in
// either set (the reframe-join change, ADR-010).
export function reframesOf(doc){
  const out=[];let previous=null;
  for(const chapter of doc.chapters)for(const shot of chapter.shots){
    if(shot.transition?.kind==='reframe'&&previous)
      out.push({chapter,shot,outgoing:previous.shot,views:movingViews(previous.chapter,previous.shot,chapter,shot)});
    previous={chapter,shot};
  }
  return out;
}
// The set kinds a document's reframes move views between, in order.
export const reframeSets=doc=>[...new Set(reframesOf(doc).flatMap(r=>r.views.flatMap(v=>[v.from.set,v.to.set])))];

// The boxes a reframe's frames are drawn from, the film's `reframes`: for each
// reframed shot, each moving view's outgoing and incoming slot with its box
// as fractions of the frame, from a layout measured on the stage
// ({width, height, sets}). A slot sized by what it holds has no box before it
// is drawn with its content, so a reframe through one is refused, naming the
// shot, the view, the set and the slot.
export function reframeBoxes(doc,layouts){
  const out={};
  for(const {shot,views} of reframesOf(doc)){
    const boxes={};
    for(const view of views){
      const end=({set,slot},word)=>{
        const slots=layouts.sets[set];
        need(slots,`Shot ${shot.id} comes in by a reframe ${word==='into'?'into':'out of'} set ${set}, whose layout was not measured`);
        const measured=slots.find(s=>s.slot===slot);
        need(measured,`Shot ${shot.id} comes in by a reframe that moves ${view.key} ${word} slot ${slot} of set ${set}, which the set does not draw`);
        need(measured.fixed,`Shot ${shot.id} comes in by a reframe that moves ${view.key} ${word} slot ${slot} of set ${set}, which is sized by what it holds; a reframe moves a view between slots whose boxes stay put`);
        need(measured.box[2]>0&&measured.box[3]>0,`Shot ${shot.id} comes in by a reframe that moves ${view.key} ${word} slot ${slot} of set ${set}, which has no box`);
        const [x,y,w,h]=measured.box;
        return {set,slot,box:[x/layouts.width,y/layouts.height,w/layouts.width,h/layouts.height]};
      };
      boxes[view.key]={from:end(view.from,'out of'),to:end(view.to,'into')};
    }
    out[shot.id]=boxes;
  }
  return out;
}
// What `check` prints: one line per reframe, each view with its two slots'
// measured boxes.
export function reframeLines(doc,layouts){
  const at=(set,slot)=>{const s=layouts.sets[set].find(x=>x.slot===slot);return `${set} ${slot} ${size(s.box)} at ${number(s.box[0])},${number(s.box[1])}`;};
  return reframesOf(doc).map(({shot,views})=>`Reframe into ${shot.id}: `+
    views.map(v=>`${v.key} from ${at(v.from.set,v.from.slot)} to ${at(v.to.set,v.to.slot)}`).join('; '));
}

// In the page: pose the emptied frame of a set, then measure each slot's box,
// the box a picture element placed in it gets, and whether the slot's box
// stays put when every slot holds a block three times the frame's size.
async function measureSet(frame){
  await window.film.setFrame(frame);
  const rect=el=>{const r=el.getBoundingClientRect();return [r.x,r.y,r.width,r.height];};
  const slots=[...document.querySelectorAll('#stage-root .vm-slot')];
  // The element and classes the stage gives a picture's box.
  const boxes=slots.map(slot=>{const box=document.createElement('div');box.className='vm-element vm-element-picture';slot.append(box);return box;});
  const held=slots.map((slot,i)=>({slot:slot.dataset.slot,box:rect(slot),picture:rect(boxes[i])}));
  for(const box of boxes){
    box.className='vm-element';
    const block=document.createElement('div');
    block.style.width=`${3*window.innerWidth}px`;block.style.height=`${3*window.innerHeight}px`;
    box.append(block);
  }
  const filled=slots.map(rect);
  for(const box of boxes)box.remove();
  return held.map((h,i)=>({...h,fixed:h.box.every((v,k)=>Math.abs(v-filled[i][k])<1e-6)}));
}

// The text a shot shows, wholly shown, by shot (ADR-017): every source panel
// it places, its whole excerpt typed (`excerpts`, the pinned excerpts by
// name), and every title one of its cues shows, with all its words; each in
// its slot, in the order the shot places them. Views, pictures and project
// elements are not placed: the probe mounts no viewer and serves no media.
export function textFrames(doc,excerpts){
  const out=[];
  for(const chapter of doc.chapters)for(const shot of chapter.shots){
    const slots={},elements={},kinds={};
    for(const [slot,key] of Object.entries(shot.places)){
      const element=chapter.elements[key],id=`${chapter.id}.${key}`;
      const shown=element?.kind==='title'&&(shot.cues??[]).some(cue=>cue.actions.some(a=>a.element===key&&a.action==='show'));
      if(element?.kind==='source')elements[id]=wholeSource(excerpts,element.source);
      else if(shown)elements[id]={kind:'title',shown:true,opacity:1,text:element.text,...(element.subtitle!==undefined?{subtitle:element.subtitle}:{})};
      else continue;
      slots[slot]=id;kinds[id]={slot,kind:element.kind};
    }
    if(Object.keys(slots).length)out.push({shotId:shot.id,kinds,
      frame:{time:0,chapterId:chapter.id,shotId:shot.id,set:shot.set,slots,elements,transition:null}});
  }
  return out;
}
// Poses each shot's text frame on a page that serves the movie's stage and
// reads what the stage measured: [{shotId, elements: [{key, kind, slot,
// fontSize} or {key, kind, slot, lines, subtitleLines?}]}].
export async function measureTextOn(page,doc,excerpts,{refuse=e=>new Error(`Measuring the stage's text: ${e}`),errors=[]}={}){
  const out=[];
  for(const {shotId,kinds,frame} of textFrames(doc,excerpts)){
    let seen;
    try{seen=await page.evaluate(async f=>(await window.film.setFrame(f)).elements,frame);}
    catch(error){throw refuse(`shot ${shotId}: ${error.message.replace(/^page\.evaluate: (Error: )?/,'')}`);}
    if(errors.length)throw refuse(errors.join('\n'));
    out.push({shotId,elements:Object.entries(kinds).map(([key,{slot,kind}])=>{
      const r=seen[key]??{};
      return kind==='source'?{key,kind,slot,fontSize:r.fontSize??null}
        :{key,kind,slot,lines:r.lines??null,...(r.subtitleLines!==undefined?{subtitleLines:r.subtitleLines}:{})};
    })});
  }
  return out;
}
// What `check` prints: one line per shot whose text was measured, a source
// panel's size in CSS pixels and in vw of the output width, a title's lines.
// No threshold: the numbers are the author's to judge.
export function textLines(layouts){
  const lines=n=>n===null?'unmeasured lines':`${n} line${n===1?'':'s'}`;
  return (layouts.text??[]).map(({shotId,elements})=>`Shot ${shotId}: `+elements.map(e=>e.kind==='source'
    ?`source ${e.key} in ${e.slot} at `+(e.fontSize===null?'an unmeasured size':`${e.fontSize.toFixed(1)} px (${(e.fontSize/layouts.width*100).toFixed(2)} vw)`)
    :`title ${e.key} in ${e.slot} on ${lines(e.lines)}`+(e.subtitleLines!==undefined?`, its subtitle on ${lines(e.subtitleLines)}`:'')).join('; '));
}
// Whether a document's shots place a source panel or show a title: the text
// `check` reports as not measured when it opens no browser.
export const showsText=doc=>doc.chapters.some(chapter=>chapter.shots.some(shot=>Object.values(shot.places).some(key=>{
  const element=chapter.elements[key];
  return element?.kind==='source'||element?.kind==='title'&&(shot.cues??[]).some(cue=>cue.actions.some(a=>a.element===key&&a.action==='show'));
})));
export const TEXT_NOT_MEASURED='Text not measured: check measures a movie\'s stage only when it shows a picture or comes in by a reframe; read the sizes and the lines on preview\'s stills';

// The layout of every set kind the movie's shots use, at the output size:
// {width, height, sets: {kind: [{slot, box, picture, fixed}]}, text}, the
// sets in the order the shots first use them and their slots in the page's
// order, and the text each shot shows (`measureTextOn`; `excerpts` are the
// pinned excerpts its source panels show). A browser and an asset server may
// be given (a test run shares one of each); otherwise it launches Chromium
// and makes a server, and closes both.
export async function measureLayouts(doc,bundle,{browser:givenBrowser,assets:givenAssets,excerpts={}}={}){
  const {width,height}=doc.output,first=new Map();
  for(const chapter of doc.chapters)for(const shot of chapter.shots)
    if(!first.has(shot.set))first.set(shot.set,{chapterId:chapter.id,shotId:shot.id});
  const config=stageConfig({...doc,source:'movie',pictureMedia:null});
  const files=new Map([['/',[PAGE,'text/html']],['/stage.js',[bundle.js,'text/javascript']],['/stage.css',[bundle.css,'text/css']]]);
  const errors=[];
  const serve=async(req,res)=>{
    try{
      const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(config));return;}
      if(path==='/viewer.js'){res.setHeader('Content-Type','text/javascript');res.end(STUB_VIEWER);return;}
      if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
      const found=files.get(path);if(!found){res.writeHead(404);res.end('Not found');return;}
      res.setHeader('Content-Type',found[1]);res.end(await readFile(found[0]));
    }catch(error){errors.push(String(error));res.writeHead(500);res.end('Asset error');}
  };
  const refuse=error=>new Error(`Measuring the stage's layout for check: ${error}`);
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
    const error=await page.evaluate(()=>window.filmError);if(error)throw refuse(error);
    const layouts=await measureSetsOn(page,doc,[...first.keys()],{width,height,refuse,errors});
    return {...layouts,text:await measureTextOn(page,doc,excerpts,{refuse,errors})};
  }finally{
    if(givenBrowser)await page?.close();else await browser?.close();
    release();if(!givenAssets)await assets.close();
  }
}

// The layout of the set kinds `kinds` on a page that already serves the
// movie's stage (the probe's, or a renderer session's), at that page's size:
// {width, height, sets}. Each set is posed empty at the first shot that uses
// it. The renderer's sessions measure the sets their reframes use this way,
// on their own page, before their first frame.
export async function measureSetsOn(page,doc,kinds,{width,height,refuse=e=>new Error(`Measuring the stage's layout: ${e}`),errors=[]}){
  const first=new Map();
  for(const chapter of doc.chapters)for(const shot of chapter.shots)
    if(!first.has(shot.set))first.set(shot.set,{chapterId:chapter.id,shotId:shot.id});
  const sets={};
  for(const kind of kinds){
    try{sets[kind]=await page.evaluate(measureSet,{time:0,...first.get(kind),set:kind,slots:{},elements:{},transition:null});}
    catch(error){throw refuse(`set ${kind}: ${error.message.replace(/^page\.evaluate: (Error: )?/,'')}`);}
    if(errors.length)throw refuse(errors.join('\n'));
  }
  return {width,height,sets};
}

// What `check` prints: one line per measured set.
export function layoutLines(layouts){
  return Object.entries(layouts.sets).map(([kind,slots])=>`Layout ${kind} at ${layouts.width}×${layouts.height}: `+
    slots.map(s=>!s.fixed?`${s.slot} sized by what it holds`:!trusted(s)?`${s.slot} has no box`:
      `${s.slot} ${size(s.box)} at ${number(s.box[0])},${number(s.box[1])}`).join('; '));
}

// Refuses a raster picture whose peak enlargement in its measured box exceeds
// its allowance; needs no take. Returns, by `<shot id>/<element key>`, the
// text `check` prints for each picture shown.
export function checkEnlargements(doc,media,layouts){
  const verdicts=new Map();
  for(const p of picturesShown(doc)){
    const probe=media[p.media==='still'?'stills':'clips'][p.name];
    const slot=layouts.sets[p.set]?.find(s=>s.slot===p.slot);
    let text;
    if(probe.format==='svg')text='vector, no enlargement limit';
    else if(!trusted(slot))text=`allowance ${probe.upscale}×; slot ${p.slot} of set ${p.set} `+
      `${slot?.fixed?'has no box':'is sized by what it holds'}, enlargement checked against its box at preview and render`;
    else{
      const [,,w,h]=slot.picture,zoom=Math.max(1,...(p.action.view??[]).map(v=>v.zoom));
      const peak=((p.element.fit??'contain')==='cover'?Math.max:Math.min)(w/probe.width,h/probe.height)*zoom;
      need(peak<=probe.upscale+1e-9,
        `${p.media==='still'?'Still':'Clip'} ${p.name} would be enlarged ${peak.toFixed(2)}× in shot ${p.shot.id} `+
        `(${probe.width}×${probe.height} source pixels in the ${size(slot.picture)} box of slot ${p.slot} of set ${p.set}); `+
        `its upscale allowance is ${probe.upscale}. Set upscale on the ${p.media}, place it in a smaller slot, or use a larger source.`);
      text=`peak ${peak.toFixed(2)}×; allowance ${probe.upscale}×`;
    }
    verdicts.set(`${p.shot.id}/${p.key}`,text);
  }
  return verdicts;
}

// Refuses, on the resolved film, a still's view that leaves the picture at an
// output frame of its cue, in its measured box: a rectangle that overfills an
// axis covers the box on it, one that underfills it stays inside.
export function checkPictureViews(film,layouts){
  const fps=film.output.fps;
  for(const p of picturesShown(film)){
    if(p.media!=='still'||!p.action.view)continue;
    const slot=layouts.sets[p.set]?.find(s=>s.slot===p.slot);
    if(!trusted(slot))continue;
    const media=film.pictureMedia.stills[p.name],box=[0,0,slot.picture[2],slot.picture[3]],{shot,cue}=p;
    for(let n=Math.ceil((shot.start+cue.at)*fps-1e-9);n/fps<shot.start+cue.until-1e-9;n++){
      const state=frameAt(film,n/fps).elements[p.key];
      if(!state?.shown)continue;
      const rect=pictureRect(media,box,state.fit,state.view);
      const framed=[0,1].every(axis=>{
        const start=rect[axis],extent=rect[axis+2];
        return extent>=1-1e-9?start<=1e-9&&start+extent>=1-1e-9:start>=-1e-9&&start+extent<=1+1e-9;
      });
      need(framed,`Picture view leaves the picture in shot ${shot.id} at ${(n/fps).toFixed(2)} s (${p.key}, ${p.name}); keep the view inside the picture or zoom in`);
    }
  }
}
