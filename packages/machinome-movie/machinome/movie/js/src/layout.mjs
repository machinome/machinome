// The layout `check` measures (the check-measures-the-stage change, ADR-009):
// a movie document's slot boxes are its sets' layout, drawn only by the stage,
// so when the movie shows a picture, `check` poses each set kind its shots use,
// once, with no element placed, on the page the renderer serves (the bundle,
// src/film.html, the stage config) with a stub viewer whose mount is never
// called, at the output size. It refuses what the measured boxes let it
// refuse: a picture enlarged beyond its allowance, before any take is read,
// and a picture view that leaves the picture, once the takes resolve its
// times, in the words a YAML episode's pictures are refused in
// (src/pictures.mjs). Nothing memoizes it: it runs once per `check`.
import {readFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {assetServer,stageConfig,CHROMIUM_ARGS} from './render.mjs';
import {pictureRect} from './pictures.mjs';
import {frameAt} from './timeline.mjs';

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

// The layout of every set kind the movie's shots use, at the output size:
// {width, height, sets: {kind: [{slot, box, picture, fixed}]}}, the sets in
// the order the shots first use them and their slots in the page's order. A
// browser and an asset server may be given (a test run shares one of each);
// otherwise it launches Chromium and makes a server, and closes both.
export async function measureLayouts(doc,bundle,{browser:givenBrowser,assets:givenAssets}={}){
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
    const sets={};
    for(const [kind,at] of first){
      try{sets[kind]=await page.evaluate(measureSet,{time:0,...at,set:kind,slots:{},elements:{},transition:null});}
      catch(error){throw refuse(`set ${kind}: ${error.message.replace(/^page\.evaluate: (Error: )?/,'')}`);}
      if(errors.length)throw refuse(errors.join('\n'));
    }
    return {width,height,sets};
  }finally{
    if(givenBrowser)await page?.close();else await browser?.close();
    release();if(!givenAssets)await assets.close();
  }
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
