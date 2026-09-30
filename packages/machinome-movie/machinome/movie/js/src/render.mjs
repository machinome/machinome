import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,copyFile,rename,link,unlink} from 'node:fs/promises';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID} from 'node:crypto';
import {chromium} from 'playwright';
import {frameAt,srt} from './timeline.mjs';
import {contained,requiredViewerApi,viewerApiRefusal} from './episode.mjs';
import {fileHash,hash,json,command} from './util.mjs';
import {decodePng,hexColor,chromeMask,largestDifference,at,proveMark} from './pixels.mjs';
import {resolveWordTiming,validateWordFramesAtFps} from './words.mjs';
import {readSpeechTake} from './speech.mjs';
import {STAGE_AREAS,extractClips,validatePictureSizing,pictureReports,clipCadenceForCue} from './pictures.mjs';
import {SHOT_CACHE_SCHEMA,outputShotUnits,fingerprintShotUnits,shotCacheRoot,
  findShotGeneration,captureShotGeneration,assembleShotFrames} from './shot-cache.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const sub=(a,b)=>a.map((v,i)=>v-b[i]),add=(a,b,s)=>a.map((v,i)=>v+b[i]*s);
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const cueKey=cue=>JSON.stringify([cue.from,cue.to,cue.position,cue.text]);
const overlayIndex=(shot,index,local)=>shot.overlays.slice(0,index)
  .filter(c=>local>=c.from-1e-9&&local<c.to-1e-9).length;
// All plain/absent states of simultaneously fading marks, preserving every
// non-fading mark's position in the drawing order. The weights sum to one.
export function fadeSubsets(annotations=[]){
  const fades=annotations.filter(a=>a.opacity>0&&a.opacity<1);
  if(!fades.length)return null;
  const variants=[];
  for(let mask=0;mask<2**fades.length;mask++){
    let weight=1;
    const chosen=annotations.flatMap(a=>{
      const j=fades.findIndex(mark=>mark.index===a.index);
      if(j<0)return [a];
      const included=Math.floor(mask/2**j)%2===1;
      weight*=included?a.opacity:1-a.opacity;
      if(!included)return [];
      const {opacity,drawn,...plain}=a;return [plain];
    });
    variants.push({annotations:chosen,weight});
  }
  return variants;
}
// Where a camera key starts or ends a change of field of view or up direction.
function lensChanges(e,shot){
  const sameUp=(a,b)=>unit(a.up).every((v,i)=>Math.abs(v-unit(b.up)[i])<=1e-12);
  const instants=[];
  for(let i=1;i<shot.camera.length;i++){
    const a=e.cameras[shot.camera[i-1].preset],b=e.cameras[shot.camera[i].preset];
    if(a.fov===b.fov&&sameUp(a,b))continue;
    const last=shot.end-shot.start-1/e.output.fps;
    for(const at of [shot.camera[i-1].at,Math.min(shot.camera[i].at,last)])instants.push({time:shot.start+at,up:!sameUp(a,b)});
  }
  return instants;
}
async function stage(e,viewer) {
  const manifest=JSON.parse(await readFile(e.paths.manifest,'utf8'));
  const assets=new Set();
  function walk(value){if(typeof value==='string'&&/\.(stl|png|jpg|jpeg|webp|svg)$/i.test(value))assets.add(value);else if(value&&typeof value==='object')Object.values(value).forEach(walk);}
  walk(manifest);
  const paths=new Map([['/viewer.js',resolve(viewer)],['/model/manifest.json',e.paths.manifest],
    ['/film.js',resolve(here,'film.js')],['/',resolve(here,'film.html')]]);
  for(const asset of assets){
    const file=resolve(dirname(e.paths.manifest),asset);
    if(!contained(dirname(e.paths.manifest),file))throw new Error(`Model asset escapes export: ${asset}`);
    paths.set('/model/'+asset,file);
  }
  for(const [name,media] of Object.entries(e.pictureMedia?.stills??{}))
    paths.set(`/pictures/stills/${name}`,media.file);
  for(const [name,media] of Object.entries(e.pictureMedia?.clips??{}))
    for(const n of media.extraction?.frames??[])
      paths.set(`/pictures/clips/${name}/${String(n).padStart(6,'0')}.png`,
        resolve(media.extraction.dir,`${String(n).padStart(6,'0')}.png`));
  const hashes={};for(const [url,file]of paths){
    if(url.startsWith('/pictures/clips/'))continue;
    hashes[url]=await fileHash(file);
  }
  for(const [name,media] of Object.entries(e.pictureMedia?.clips??{}))
    if(media.extraction)hashes[`/pictures/clips/${name}`]=media.extraction.key;
  return {paths,hashes};
}

export async function browserSession(e,viewer,width,captions,action) {
  validatePictureSizing(e,width);
  await extractClips(e);
  const {paths,hashes}=await stage(e,viewer);
  const height=Math.round(e.output.height*width/e.output.width/2)*2;
  const initial=frameAt(e,0,captions);
  const required=requiredViewerApi(e);
  const cfg={style:e.style,series:e.series??e.title,initial,requiredViewerApi:required,
    pictureStills:Object.keys(e.pictureMedia?.stills??{}),viewerRefusal:viewerApiRefusal(required,'{declared}')};
  const errors=[];
  const server=createServer(async(req,res)=>{
    try{
      const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(cfg));return;}
      if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
      const file=paths.get(path);if(!file){res.writeHead(404);res.end('Not found');return;}
      res.setHeader('Content-Type',({'.js':'text/javascript','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp'}[extname(file)])??'application/octet-stream');
      res.end(await readFile(file));
    }catch(error){errors.push(String(error));res.writeHead(500);res.end('Asset error');}
  });
  await new Promise(r=>server.listen(0,'127.0.0.1',r));
  let browser;
  try{
    browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
    const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
    page.on('pageerror',e=>errors.push(e.message));
    page.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
    page.on('requestfailed',r=>errors.push(r.url()+': '+r.failure()?.errorText));
    page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`);});
    await page.goto(`http://127.0.0.1:${server.address().port}/`);
    await page.waitForFunction(()=>window.film||window.filmError,{},{timeout:60000});
    const error=await page.evaluate(()=>window.filmError);if(error)throw new Error(error);
    let frames=0;
    const viewerApi=await page.evaluate(()=>window.film.apiVersion);
    // Poses one picture and runs every check a posed frame has. The page sets its
    // state by request, so nothing depends on what was posed before. A fresh pose
    // does not depend on the one before it even in the raster of its text; every
    // pose inside a transition is fresh.
    async function show(f,t,{pictureOnly=false,fresh=false}={}){
      if(errors.length)throw new Error(errors.join('\n'));
      const {transition,...request}=f;
      const observed=await page.evaluate(f=>window.film.setFrame(f),{...request,pictureOnly,fresh:fresh||pictureOnly});
      for(const k of ['camera','target'])for(let i=0;i<3;i++)if(Math.abs(observed[k][i]-f.view[k][i])>1e-6)throw new Error('Viewer did not adopt requested camera');
      if(viewerApi>=28){
        if(!(Math.abs(observed.fov-f.fov)<=1e-6))throw new Error(`Viewer did not adopt the requested field of view: ${f.shotId} at ${t.toFixed(2)} s (${observed.fov} instead of ${f.fov})`);
        const seen=unit(observed.up),asked=unit(f.up);
        if(!seen.every((v,i)=>Math.abs(v-asked[i])<=1e-6))throw new Error(`Viewer did not adopt the requested up direction: ${f.shotId} at ${t.toFixed(2)} s`);
      }
      const canvasSize=await page.locator('#stage canvas').boundingBox(),stageSize=await page.locator('#stage').boundingBox();
      if(f.layout==='source-only'){
        const where=`${f.shotId} at ${t.toFixed(2)} s`;
        const visible=await page.locator('#source').evaluate(el=>{
          const style=getComputedStyle(el),rect=el.getBoundingClientRect();
          return {shown:style.display!=='none'&&style.visibility!=='hidden'&&Number(style.opacity)>0,
            rect:{x:rect.x,y:rect.y,width:rect.width,height:rect.height}};
        });
        if(!visible.shown||!stageSize||stageSize.width<=0||stageSize.height<=0)
          throw new Error(`Source panel is not visible: ${where}`);
        const panel=visible.rect,expected=STAGE_AREAS.plain.map((v,i)=>v*(i%2?height:width));
        if(panel.width<=0||panel.height<=0||
          [panel.x-expected[0],panel.y-expected[1],panel.width-expected[2],panel.height-expected[3]]
          .some(delta=>Math.abs(delta)>1))throw new Error(`Source panel is outside the picture area: ${where}`);
        const viewportVisible=await page.locator('#viewport').evaluate(el=>{
          const style=getComputedStyle(el);return style.display!=='none'&&style.visibility!=='hidden'&&Number(style.opacity)>0;
        });
        if(viewportVisible)throw new Error(`Source-only model pane remains visible: ${where}`);
      }else if(!canvasSize||canvasSize.height<stageSize.height*.98||canvasSize.width<stageSize.width*.98)
        throw new Error('Viewer canvas does not fill the film stage');
      if(f.picture){
        const p=f.picture,seen=observed.picture,media=e.pictureMedia[p.kind==='still'?'stills':'clips'][p.name];
        if(!seen)throw new Error(`Picture did not reach the page: ${f.shotId} #${p.index} at ${t.toFixed(2)} s`);
        const viewport=STAGE_AREAS[f.code?'code':'plain'].map((v,i)=>v*(i%2?height:width));
        if([observed.stage.x,observed.stage.y,observed.stage.width,observed.stage.height]
          .some((v,i)=>Math.abs(v-viewport[i])>1))throw new Error(`Film stage layout differs from the picture geometry: shot ${f.shotId}`);
        const area=p.area==='frame'?[0,0,width,height]:STAGE_AREAS[f.code?'code':'plain'].map((v,i)=>v*(i%2?height:width));
        if(p.area==='stage'&&[seen.area.x,seen.area.y,seen.area.width,seen.area.height]
          .some((v,i)=>Math.abs(v-area[i])>1))throw new Error(`Film stage layout differs from the picture geometry: shot ${f.shotId}`);
        const rect=[area[0]+p.rect[0]*area[2],area[1]+p.rect[1]*area[3],p.rect[2]*area[2],p.rect[3]*area[3]];
        if([seen.drawn.x,seen.drawn.y,seen.drawn.width,seen.drawn.height].some((v,i)=>Math.abs(v-rect[i])>.5))
          throw new Error(`Picture geometry differs from timeline: ${f.shotId} #${p.index} at ${t.toFixed(2)} s`);
        if(media.format==='svg'){
          if(Math.abs(seen.natural.width/seen.natural.height-media.width/media.height)>media.width/media.height*.001)
            throw new Error(`SVG picture aspect differs from viewBox: ${f.shotId} #${p.index}`);
        }else if(seen.natural.width!==media.width||seen.natural.height!==media.height)
          throw new Error(`Picture natural size differs from probe: ${f.shotId} #${p.index}`);
        if(p.kind==='clip'&&seen.frame!==p.frame)throw new Error(`Clip frame differs from timeline: ${f.shotId} #${p.index}`);
        const scale=seen.drawn.width/seen.natural.width*(e.output.width/width);
        if(media.format!=='svg'&&scale>media.upscale+1e-9)
          throw new Error(`Picture drawn larger than its upscale allowance: ${f.shotId} #${p.index}`);
      }else if(observed.picture)throw new Error(`Picture remained on screen outside cue: ${f.shotId} at ${t.toFixed(2)} s`);
      if(f.code){
        const fits=await page.locator('#source').evaluate(el=>el.scrollHeight<=el.clientHeight&&el.scrollWidth<=el.clientWidth);
        if(!fits)throw new Error(f.layout==='source-only'
          ?`Source excerpt overflows the panel: ${f.shotId} at ${t.toFixed(2)} s; select fewer lines`
          :`Source excerpt overflows the panel: ${f.shotId}; select fewer lines`);
        if(await page.locator('#source-code').textContent()!==f.code.text)throw new Error('Displayed code differs from source');
        if(f.code.emphasis){
          const expected=f.code.emphasis.map(c=>c.word),actual=observed.emphasis.map(c=>c.text);
          if(JSON.stringify(actual)!==JSON.stringify(expected))throw new Error(`Source emphasis did not reach the picture: ${f.shotId} at ${t.toFixed(2)} s`);
        }
      }
      for(const [index,cue] of f.overlays.entries()){
        const drawn=observed.overlays[index];
        if(!drawn)throw new Error(`Overlay is missing from the picture: ${f.shotId} #${index} at ${t.toFixed(2)} s`);
        if(cue.words&&drawn.shown!==cue.shown)throw new Error(`Overlay word count differs from timeline: ${f.shotId} #${index} at ${t.toFixed(2)} s (${drawn.shown} instead of ${cue.shown})`);
        if(cue.position==='title'){
          const b=drawn.box,frame=observed.frame;
          if(b.x<-.5||b.y<-.5||b.x+b.width>frame.width+.5||b.y+b.height>frame.height+.5)
            throw new Error(`Title leaves the frame: ${f.shotId} at ${t.toFixed(2)} s`);
        }
      }
      for(const drawn of f.annotations?observed.annotations:[]){
        const cue=f.annotations.find(a=>a.index===drawn.index),stage=observed.stage,frame=observed.frame;
        const name=`${f.shotId} #${drawn.index}${cue.text===undefined?` (${cue.kind})`:` '${cue.text}'`} at ${t.toFixed(2)} s`;
        const p=drawn.anchor;
        if(!p||p.x<stage.x||p.x>stage.x+stage.width||p.y<stage.y||p.y>stage.y+stage.height)throw new Error(`Annotation target is not on screen: ${name}`);
        if(cue.kind==='ring'){
          const r=drawn.rect,g=drawn.ring;
          if(r.x<stage.x||r.y<stage.y||r.x+r.width>stage.x+stage.width||r.y+r.height>stage.y+stage.height)
            throw new Error(`Ring target is not wholly on screen: ${name}`);
          if(g.cx-g.rx<0||g.cy-g.ry<0||g.cx+g.rx>frame.width||g.cy+g.ry>frame.height)
            throw new Error(`Ring leaves the frame: ${name}`);
        }
        const box=drawn.text;
        if(box&&(box.x<-.5||box.y<-.5||box.x+box.width>frame.width+.5||box.y+box.height>frame.height+.5))throw new Error(`Annotation text leaves the frame: ${name}`);
      }
      return observed;
    }
    async function showPicture(f,t,options={}){
      if(f.picture&&f.picture.opacity<1){
        const observed=await show(f,t,options),opacity=f.picture.opacity;
        if(opacity<=0){await show({...f,picture:null},t,{...options,fresh:true});return observed;}
        const captures=[];
        for(const [picture,weight] of [[{...f.picture,opacity:1},opacity],[null,1-opacity]]){
          await show({...f,picture},t,{...options,fresh:true});
          captures.push({src:'data:image/png;base64,'+(await page.screenshot()).toString('base64'),weight});
        }
        Object.assign(observed,await page.evaluate(p=>window.film.composeMarkBlend(p),captures));
        return observed;
      }
      const variants=fadeSubsets(f.annotations);
      if(!variants)return show(f,t,options);
      // Each screenshot is the same instant with a subset of the faded marks
      // drawn plainly. The weighted sum is exact even when two marks overlap:
      // opacity compositing is affine in each mark's opacity separately.
      const observed=await show(f,t,options),pictures=[];
      for(const {annotations,weight} of variants){
        await show({...f,annotations},t,{...options,fresh:true});
        pictures.push({src:'data:image/png;base64,'+(await page.screenshot()).toString('base64'),weight});
      }
      Object.assign(observed,await page.evaluate(p=>window.film.composeMarkBlend(p),pictures));
      return observed;
    }
    // A picture of this instant without the film's chrome, posed and checked, as
    // the page will draw it again.
    async function capture(f,t){
      const observed=await showPicture(f,t,{pictureOnly:true});
      return {src:'data:image/png;base64,'+(await page.screenshot()).toString('base64'),observed};
    }
    // One film frame. Inside a transition it is composed from poses of the same
    // instant only (design D6): the page draws captures of the pictures it is made
    // of, then the plate of a fade, under its own masthead and progress rule. A
    // fade poses one picture; a dissolve, wipe or slide poses both. override
    // replaces frame fields for preview-only comparison frames; pictureOnly
    // leaves out the masthead and progress rule.
    async function pose(t,override={},{pictureOnly=false,fresh=false}={}){
      const baseline=frameAt(e,t,captions);
      if(override.overlays)for(const cue of override.overlays.filter(c=>c.words)){
        const prior=baseline.overlays.find(c=>cueKey(c)===cueKey(cue));
        if(prior&&cue.shown!==prior.shown)throw new Error(`Overlay word count differs from timeline: ${baseline.shotId} at ${t.toFixed(2)} s`);
      }
      const f={...baseline,progress:t/e.output.durationSeconds,...override};
      // A preview comparison can replace the incoming request with the
      // preceding shot's complete outgoing request. Absent layout on that
      // older/model shot means absent, not the incoming source-only layout.
      if(override.shotId&&override.shotId!==baseline.shotId&&!Object.hasOwn(override,'layout'))
        delete f.layout;
      const x=f.transition;let observed;
      if(!x)observed=await showPicture(f,t,{pictureOnly,fresh});
      else{
        const outgoing=x.outgoing&&{...x.outgoing,progress:f.progress};
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
    const info={width,height,browser:browser.version(),viewerApi,hashes,requiredViewerApi:required};
    const result=await action({page,pose,info});
    if(errors.length)throw new Error(errors.join('\n'));
    return {...result,...info,framesChecked:frames};
  }finally{await browser?.close();await new Promise(r=>server.close(r));}
}

export async function preview(e,{viewer,width=960,captions=[]}) {
  if(!e.wordTiming)await resolveWordTiming(e,shot=>readSpeechTake(e,shot));
  const dir=resolve(e.paths.build,'preview');await mkdir(dir,{recursive:true});
  const result=await browserSession(e,viewer,width,captions,async({page,pose})=>{
    // Highlights first, while every material is pristine: the same instant
    // without its cue, with it, without it, with it. The cue must change the
    // pixels, restore() must return them exactly, and re-applying must match.
    const highlightChecks=[];
    for(const shot of e.shots)for(const [index,cue] of (shot.highlight??[]).entries()){
      // Posed without any transition, so a cue under an outgoing picture is still proved on its own shot.
      const t=shot.start+(cue.from+cue.to)/2,capture=async override=>{await pose(t,{transition:null,...override});return page.screenshot();};
      const plain=await capture({highlight:null}),lit=await capture(),plainAgain=await capture({highlight:null}),litAgain=await capture();
      const fail=async(check,message,before,after)=>{
        await writeFile(resolve(dir,`highlight-${shot.id}-${index}-${check}-before.png`),before);
        await writeFile(resolve(dir,`highlight-${shot.id}-${index}-${check}-after.png`),after);
        throw new Error(`${message}: ${shot.id} #${index} at ${t.toFixed(2)} s; inspect preview/highlight-${shot.id}-${index}-${check}-{before,after}.png`);
      };
      if(!plain.equals(plainAgain))await fail('restore','Highlight did not restore exactly',plain,plainAgain);
      if(lit.equals(plain))await fail('visible','Highlight did not reach the pixels',plain,lit);
      if(!lit.equals(litAgain))await fail('reapply','Highlight did not re-apply identically',lit,litAgain);
      highlightChecks.push({shotId:shot.id,index,time:t,changed:true,restored:true,reapplied:true});
    }
    const samples=[];
    for(const shot of e.shots){
      const times=[0,.5,.95].map(u=>shot.start+(shot.end-shot.start)*u);
      for(const cue of shot.code?.typing??[])times.push(shot.start+(cue.from+cue.to)/2);
      // Each annotation at its start, quarters, midpoint and last frame before it ends.
      for(const a of shot.annotations??[]){
        for(const u of [0,.25,.5,.75])times.push(shot.start+a.from+(a.to-a.from)*u);
        times.push(shot.start+Math.max(a.from,a.to-1/e.output.fps));
        if(a.enter){
          times.push(shot.start+a.from+a.enter.duration/2);
          if(a.from+a.enter.duration<a.to-1e-9)times.push(shot.start+a.from+a.enter.duration);
        }
        if(a.leave)times.push(shot.start+a.to-a.leave.duration,shot.start+a.to-a.leave.duration/2);
      }
      for(const cue of shot.highlight??[])times.push(shot.start+(cue.from+cue.to)/2);
      for(const t of [...new Set(times)].sort((a,b)=>a-b)){
      const posed=await pose(t);
      const readable=await page.locator('.lower-third').evaluateAll(elements=>elements.every(element=>{
        const background=getComputedStyle(element).backgroundColor;
        return background!=='transparent'&&background!=='rgba(0, 0, 0, 0)';
      }));
      if(!readable)throw new Error('Lower-third credits need an opaque background over the model');
      const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}.png`);
      await page.screenshot({path:file});
      samples.push(posed.annotations?{time:t,file,annotations:posed.observed.annotations}:{time:t,file});
      }
    }
    // Each animated mark is compared against the same instant with the mark
    // drawn plainly and absent. These captures isolate its shot from a join.
    const entranceChecks=[];
    for(const shot of e.shots)for(const [index,cue] of (shot.annotations??[]).entries()){
      if(!cue.enter&&!cue.leave)continue;
      const checks=[];
      if(cue.enter)checks.push(['enter-start',cue.from],['enter',cue.from+cue.enter.duration/2],['enter-end',cue.from+cue.enter.duration]);
      if(cue.leave)checks.push(['leave-start',cue.to-cue.leave.duration],['leave',cue.to-cue.leave.duration/2]);
      for(const [phase,local] of checks){
        if(phase==='enter-end'&&local>=cue.to-1e-9){
          entranceChecks.push({shotId:shot.id,index,phase,kind:cue.enter.kind,time:shot.start+cue.to,
            skipped:'cue ends at this exclusive boundary'});
          continue;
        }
        const time=shot.start+local,frame=frameAt(e,time,captions),asWritten=frame.annotations.find(a=>a.index===index);
        if(!asWritten)throw new Error(`Annotation proof has no active cue: ${shot.id} #${index} ${phase} at ${time.toFixed(2)} s`);
        const full=frame.annotations.map(a=>{
          if(a.index!==index)return a;
          const {opacity,drawn,...plain}=a;return plain;
        });
        const without=frame.annotations.filter(a=>a.index!==index);
        const grab=async annotations=>{
          const posed=await pose(time,{transition:null,...(annotations?{annotations}:{})},{fresh:true});
          const bytes=await page.screenshot();return {posed,bytes,image:decodePng(bytes)};
        };
        const composed=await grab(),whole=await grab(full),absent=await grab(without);
        const observed=composed.posed.observed.annotations.find(a=>a.index===index);
        const kind=phase.startsWith('leave')?cue.leave.kind:cue.enter.kind;
        const name=`entrance-${shot.id}-${index}-${phase}`,where=`${shot.id} #${index} ${phase} at ${time.toFixed(2)} s`;
        let proof;
        try{proof=proveMark(phase,{composed:composed.image,full:whole.image,without:absent.image},
          {where,entrance:kind,opacity:asWritten.opacity,inside:observed.inside,outside:observed.outside,text:observed.text});}
        catch(error){
          for(const [label,picture] of [['composed',composed],['full',whole],['without',absent]])
            await writeFile(resolve(dir,`${name}-${label}.png`),picture.bytes);
          throw new Error(`${error.message}; inspect preview/${name}-{composed,full,without}.png`);
        }
        const check={shotId:shot.id,index,phase,kind,time,opacity:asWritten.opacity,drawn:asWritten.drawn,...proof};
        if(phase==='enter'||(phase==='leave'&&!cue.enter)){
          await pose(time,{transition:null},{fresh:true});const first=await page.screenshot();
          await pose((time+e.output.durationSeconds/2)%e.output.durationSeconds,{transition:null},{fresh:true});
          await pose(time,{transition:null},{fresh:true});const again=await page.screenshot();
          if(!first.equals(again)){
            await writeFile(resolve(dir,`${name}-replay-before.png`),first);await writeFile(resolve(dir,`${name}-replay-after.png`),again);
            throw new Error(`Annotation entrance replay is not deterministic: ${where}; inspect preview/${name}-replay-{before,after}.png`);
          }
          check.replay=true;
        }
        entranceChecks.push(check);
      }
    }
    // Word reveals are checked against the page's actual visible-word count,
    // not merely the timeline's arithmetic; compare first and last pixels.
    const revealChecks=[];
    for(const shot of e.shots)for(const [index,cue] of shot.overlays.entries()){
      if(!cue.reveal)continue;
      const onsets=e.wordTiming?.[shot.id]?.overlays?.[index]?.onsets;
      const first=cue.reveal.timing==='spoken'?Math.max(cue.from,onsets[0]):cue.from;
      const last=cue.reveal.timing==='spoken'?Math.max(cue.from,onsets.at(-1)):cue.from+cue.reveal.duration;
      const locals=[first,(first+last)/2,last],records=[],pictures=[];
      for(const local of locals){
        const time=shot.start+Math.min(local,cue.to-1e-8);
        const posed=await pose(time,{transition:null},{fresh:true});
        const atIndex=overlayIndex(shot,index,time-shot.start),active=posed.overlays[atIndex],shown=posed.observed.overlays[atIndex]?.shown;
        if(shown!==active?.shown)throw new Error(`Reveal count differs from timeline: ${shot.id} #${index} at ${time.toFixed(2)} s`);
        const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}-reveal-${index}-${records.length}.png`);
        const bytes=await page.screenshot({path:file});samples.push({time,file,reveal:index});
        records.push({time,shown,expected:active.shown,file});pictures.push(bytes);
      }
      if(records.some((r,i)=>i&&r.shown<records[i-1].shown)||records.at(-1).shown!==cue.text.match(/\S+/gu)?.length)
        throw new Error(`Reveal does not reach all words in order: ${shot.id} #${index}`);
      if(records.at(-1).shown>1&&pictures[0].equals(pictures.at(-1)))throw new Error(`Reveal did not change the picture: ${shot.id} #${index}`);
      revealChecks.push({shotId:shot.id,index,timing:cue.reveal.timing,samples:records,pixelsDiffer:!pictures[0].equals(pictures.at(-1))});
    }
    // Hold the model and every other cue at this same video instant while
    // comparing the authored title, a fully opaque title, and its absence.
    const fadeChecks=[];
    for(const shot of e.shots)for(const [index,cue] of shot.overlays.entries()){
      if(cue.position!=='title'||(!cue.enter&&!cue.leave))continue;
      const phases=[];
      if(cue.enter)phases.push(['enter-start',cue.from],['enter-mid',cue.from+cue.enter.duration/2],
        ['enter-end',cue.from+cue.enter.duration]);
      if(cue.leave)phases.push(['leave-start',cue.to-cue.leave.duration],['leave-mid',cue.to-cue.leave.duration/2]);
      for(const [phase,local] of phases){
        if(local>=cue.to-1e-9){fadeChecks.push({shotId:shot.id,index,phase,skipped:'cue ends at this exclusive boundary'});continue;}
        const time=shot.start+local,frame=frameAt(e,time,captions),active=frame.overlays[overlayIndex(shot,index,local)];
        if(!active)throw new Error(`Title fade proof has no active cue: ${shot.id} #${index} ${phase}`);
        const full=frame.overlays.map(o=>o===active?{...o,opacity:1}:o);
        const without=frame.overlays.filter(o=>o!==active);
        const capture=async overlays=>{await pose(time,{transition:null,...(overlays?{overlays}:{})},{fresh:true});return page.screenshot();};
        const composed=await capture(),whole=await capture(full),absent=await capture(without);
        const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}-title-${index}-${phase}.png`);
        await writeFile(file,composed);samples.push({time,file,title:index,phase});
        const midpoint=phase.endsWith('mid'),boundary=phase.endsWith('start')&&phase.startsWith('enter')?'absent':'full';
        if(midpoint?(composed.equals(whole)||composed.equals(absent)):
          !composed.equals(boundary==='absent'?absent:whole)){
          const name=`title-${shot.id}-${index}-${phase}`;
          for(const [label,bytes] of [['composed',composed],['full',whole],['without',absent]])
            await writeFile(resolve(dir,`${name}-${label}.png`),bytes);
          throw new Error(`Title fade proof failed: ${shot.id} #${index} ${phase}; inspect preview/${name}-{composed,full,without}.png`);
        }
        fadeChecks.push({shotId:shot.id,index,phase,time,file,opacity:active.opacity,
          equals:midpoint?'neither':boundary});
      }
    }
    const emphasisChecks=[];
    for(const shot of e.shots)for(const cue of e.wordTiming?.[shot.id]?.emphasis??[]){
      const checks=[['before',Math.max(0,cue.from-1/e.output.fps)],
        ...cue.cues.map((word,i)=>[`word-${i}`,word.from]),['clear',cue.to]];
      const records=[];let firstImage;
      for(const [phase,local] of checks){
        if(local>=shot.end-shot.start-1e-9){records.push({phase,skipped:'shot ends at this exclusive boundary'});continue;}
        const time=shot.start+local,posed=await pose(time,{transition:null},{fresh:true});
        const words=posed.observed.emphasis.map(m=>m.word);
        const expected=phase==='before'||phase==='clear'?[]:
          cue.cues.slice(0,Number(phase.split('-')[1])+1).map(c=>c.word);
        const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}-emphasis-${cue.index}-${phase}.png`);
        const bytes=await page.screenshot({path:file});samples.push({time,file,emphasis:cue.index,phase});
        if(JSON.stringify(words)!==JSON.stringify(expected))throw new Error(`Source emphasis count differs: ${shot.id} ${phase}; inspect ${file}`);
        if(phase==='word-0')firstImage=bytes;
        records.push({phase,time,words,file});
      }
      if(firstImage){await pose(shot.start+cue.cues[0].from,{transition:null},{fresh:true});
        if(!firstImage.equals(await page.screenshot()))throw new Error(`Source emphasis replay is not deterministic: ${shot.id}`);}
      emphasisChecks.push({shotId:shot.id,index:cue.index,samples:records,replay:Boolean(firstImage)});
    }
    const pictureChecks=[];
    for(const shot of e.shots)for(const [index,cue] of (shot.pictures??[]).entries()){
      const end=shot.start+cue.to,last=(Math.ceil(end*e.output.fps-1e-9)-1)/e.output.fps;
      const locals=[cue.from,...(cue.view??[]).map(k=>Math.min(k.at,last-shot.start)),
        ...(cue.enter?[cue.from+cue.enter.duration/2,cue.from+cue.enter.duration]:[]),
        ...(cue.leave?[cue.to-cue.leave.duration,cue.to-cue.leave.duration/2]:[]),Math.max(cue.from,last-shot.start)];
      const records=[];
      for(const local of [...new Set(locals)].filter(t=>t>=cue.from-1e-9&&t<cue.to-1e-9).sort((a,b)=>a-b)){
        const time=shot.start+local,posed=await pose(time),shown=posed.observed.picture;
        if(!shown)throw new Error(`Picture proof has no active cue: ${shot.id} #${index} at ${time.toFixed(2)} s`);
        const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}-picture-${index}-${records.length}.png`);
        await page.screenshot({path:file});samples.push({time,file,picture:index});
        records.push({time,file,kind:posed.picture.kind,rect:posed.picture.rect,
          area:shown.area,drawn:shown.drawn,natural:shown.natural,
          ...(posed.picture.kind==='clip'?{frame:shown.frame,clipSeconds:posed.picture.clipSeconds}:{})});
      }
      const replayTime=records.find(r=>frameAt(e,r.time,captions).picture?.opacity>=1-1e-9)?.time??
        records.find(r=>frameAt(e,r.time,captions).picture?.opacity>.01)?.time??records[0].time;
      await pose(replayTime);const before=await page.screenshot();
      await pose((replayTime+e.output.durationSeconds/2)%e.output.durationSeconds);
      await pose(replayTime);const after=await page.screenshot();
      if(!before.equals(after)){
        const name=`picture-${shot.id}-${index}-replay`;
        await writeFile(resolve(dir,`${name}-before.png`),before);await writeFile(resolve(dir,`${name}-after.png`),after);
        throw new Error(`Picture replay is not deterministic: ${shot.id} #${index}; inspect preview/${name}-{before,after}.png`);
      }
      const partialTime=records.find(r=>{
        const a=frameAt(e,r.time,captions).picture?.opacity;return a>.01&&a<1-.01;
      })?.time;
      if(partialTime!==undefined){
        await pose(partialTime);const before=await page.screenshot();
        await pose((partialTime+e.output.durationSeconds/2)%e.output.durationSeconds);
        await pose(partialTime);const after=await page.screenshot();
        if(!before.equals(after)){
          const name=`picture-${shot.id}-${index}-partial-replay`;
          await writeFile(resolve(dir,`${name}-before.png`),before);await writeFile(resolve(dir,`${name}-after.png`),after);
          throw new Error(`Partial picture replay is not deterministic: ${shot.id} #${index} at ${partialTime.toFixed(2)} s; inspect preview/${name}-{before,after}.png`);
        }
      }
      const fades=[];
      for(const field of ['enter','leave'])if(cue[field]){
        const duration=cue[field].duration,checks=field==='enter'?
          [['start',cue.from],['mid',cue.from+duration/2],['end',cue.from+duration]]:
          [['start',cue.to-duration],['mid',cue.to-duration/2]];
        for(const [phase,local] of checks){
          if(local>=cue.to-1e-9){fades.push({field,phase,skipped:'cue ends at this exclusive boundary'});continue;}
          const time=shot.start+local,frame=frameAt(e,time,captions),full={...frame.picture,opacity:1};
          const grab=async picture=>{await pose(time,{transition:null,picture},{fresh:true});return page.screenshot();};
          const composed=await grab(frame.picture),whole=await grab(full),absent=await grab(null);
          const reference=field==='enter'&&phase==='start'?'absent':phase==='mid'?'neither':'full';
          const passed=reference==='neither'?!composed.equals(whole)&&!composed.equals(absent):
            composed.equals(reference==='full'?whole:absent);
          const name=`picture-${shot.id}-${index}-${field}-${phase}`;
          for(const [label,bytes] of [['composed',composed],['full',whole],['without',absent]])
            await writeFile(resolve(dir,`${name}-${label}.png`),bytes);
          if(!passed)throw new Error(`Picture fade proof failed: ${shot.id} #${index} ${field}-${phase}; inspect preview/${name}-{composed,full,without}.png`);
          fades.push({field,phase,time,equals:reference});
        }
      }
      pictureChecks.push({shotId:shot.id,index,kind:cue.still!==undefined?'still':'clip',samples:records,replay:true,replayTime,
        replayOpacity:frameAt(e,replayTime,captions).picture?.opacity,partialReplay:partialTime!==undefined,partialTime,fades});
    }
    // Each transition: stills at its first frame, quarters, midpoint and last frame
    // (a fade in or out: first, middle, last), and proofs from the plain pictures
    // of the same instant (design D8).
    const transitionChecks=[],fps=e.output.fps,W=width;
    for(const shot of e.shots)for(const field of ['fadeIn','transition','fadeOut']){
      const spec=shot[field];if(!spec)continue;
      const d=spec.duration,start=field==='fadeOut'?shot.end-d:shot.start,middle=start+d/2;
      const last=(Math.ceil((start+d)*fps-1e-9)-1)/fps,kind=field==='transition'?spec.kind:'fade';
      const instants=[...new Set(field==='transition'?[start,start+d/4,middle,start+3*d/4,last]:[start,middle,last])];
      const stills=[];
      for(const time of instants){
        await pose(time);
        const file=resolve(dir,`${String(samples.length).padStart(2,'0')}-${shot.id}-${field}.png`);
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
      if(kind!=='fade'){
        const composed=await grab(middle),x=composed.posed.transition,p=x.progress,s=composed.posed.observed.offset;
        const incoming=await grab(middle,{transition:null}),outgoing=await grab(middle,{...x.outgoing,transition:null});
        const A=outgoing.image,B=incoming.image,left=x.direction==='left';
        let largest,limit=0,kept={outgoing,incoming,composed};
        if(kind==='dissolve'){limit=2;largest=largestDifference(composed.image,(px,y,k)=>(1-p)*at(A,px,y,k)+p*at(B,px,y,k));}
        else if(kind==='wipe')largest=largestDifference(composed.image,(px,y,k)=>(left?px>=W-s:px<s)?at(B,px,y,k):at(A,px,y,k));
        else{
          // The two pictures alone, without chrome, at their offsets; the chrome stays put above them.
          const a=await grab(middle,{...x.outgoing,transition:null},{pictureOnly:true}),b=await grab(middle,{transition:null},{pictureOnly:true});
          const mask=chromeMask(W,composed.image.height,composed.posed.observed.chrome);
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
          const mask=chromeMask(W,composed.image.height,composed.posed.observed.chrome);
          const found=largestDifference(composed.image,(px,y,k)=>a*C[k]+(1-a)*at(plain.image,px,y,k),mask);
          await prove(found,2,time,{[x.picture]:plain,composed});
          largest=Math.max(largest,found);
        }
        const full=field==='transition'?middle:field==='fadeIn'?start:last;
        const composed=await grab(full),x=composed.posed.transition,C=hexColor(x.color);
        const mask=chromeMask(W,composed.image.height,composed.posed.observed.chrome);
        await prove(x.plate===1?largestDifference(composed.image,(px,y,k)=>C[k],mask):Infinity,0,full,{composed});
        Object.assign(check,{progress:frameAt(e,middle).transition.plate,largestDifference:largest,exactColor:true,colorAt:full});
      }
      // Replay: the midpoint, another instant, the midpoint again.
      await pose(middle);const before=await page.screenshot();
      await pose((middle+e.output.durationSeconds/2)%e.output.durationSeconds);await pose(middle);const after=await page.screenshot();
      if(!before.equals(after)){
        await writeFile(resolve(dir,`${name}-replay-before.png`),before);await writeFile(resolve(dir,`${name}-replay-after.png`),after);
        throw new Error(`Transition replay is not deterministic: ${shot.id} at ${middle.toFixed(2)} s; inspect preview/${name}-replay-{before,after}.png`);
      }
      check.replay=true;
      transitionChecks.push(check);
    }
    // A changed lens must reach the picture: a world offset of s beside the
    // target, at distance d, projects to (H/2)·s/(d·tan(fov/2)) pixels; a
    // changed up must put a point above the target above it on screen.
    const cameraChecks=[];
    for(const shot of e.shots)for(const instant of lensChanges(e,shot)){
      const f=await pose(instant.time,{transition:null}),C=f.view.camera,T=f.view.target;
      if(f.layout==='source-only'){
        cameraChecks.push({shotId:shot.id,time:instant.time,fov:f.fov,up:f.up,
          resolvedPose:true,sourceVisible:true,visibleProjection:false});
        continue;
      }
      const d=Math.hypot(...sub(T,C)),forward=unit(sub(T,C)),up=unit(f.up),right=unit(cross(forward,up)),s=.01*d;
      const [p0,p1,pu]=await page.evaluate(points=>window.film.project(points),[T,add(T,right,s),add(T,up,s)]);
      const H=(await page.locator('#stage canvas').boundingBox()).height;
      const measured=p0&&p1?Math.hypot(p1.x-p0.x,p1.y-p0.y):NaN,expected=(H/2)*s/(d*Math.tan(f.fov*Math.PI/360));
      const where=`${shot.id} at ${instant.time.toFixed(2)} s`;
      const keep=async()=>{const file=resolve(dir,`lens-${shot.id}-${instant.time.toFixed(2)}.png`);await page.screenshot({path:file});return file;};
      if(!(Math.abs(measured/expected-1)<=.02))throw new Error(`Field of view did not reach the picture: ${where} (measured ${measured} px, expected ${expected} px); inspect ${await keep()}`);
      const upAbove=instant.up?Boolean(pu&&pu.y<p0.y):undefined;
      if(instant.up&&!upAbove)throw new Error(`Camera up did not reach the picture: ${where}; inspect ${await keep()}`);
      cameraChecks.push({shotId:shot.id,time:instant.time,fov:f.fov,up:f.up,measured,expected,...(instant.up?{upAbove}:{})});
    }
    // Real-browser check: revisiting an exact pose must restore the pixels.
    const replay=e.output.durationSeconds*.23;
    await pose(replay);const original=await page.screenshot();
    await pose(e.output.durationSeconds*.87);await pose(replay);const restored=await page.screenshot();
    if(!original.equals(restored)){
      await writeFile(resolve(dir,'replay-before.png'),original);
      await writeFile(resolve(dir,'replay-after.png'),restored);
      throw new Error('Pixel replay is not deterministic; inspect preview/replay-{before,after}.png');
    }
    // Bad camera requests must leave the actual mounted view intact.
    const preserved=await page.evaluate(()=>{const v=window.film.viewer;const before=JSON.stringify(v.view());try{v.setView({camera:[1,NaN,3],target:[0,0,0]});return false;}catch{return before===JSON.stringify(v.view());}});
    if(!preserved)throw new Error('Invalid camera request changed viewer state');
    return {samples,pixelReplay:true,invalidCameraPreserved:true,...(highlightChecks.length?{highlightChecks}:{}),...(cameraChecks.length?{cameraChecks}:{}),
      ...(transitionChecks.length?{transitionChecks}:{}),...(entranceChecks.length?{entranceChecks}:{}),
      ...(revealChecks.length?{revealChecks}:{}),...(fadeChecks.length?{fadeChecks}:{}),
      ...(emphasisChecks.length?{emphasisChecks}:{}),...(pictureChecks.length?{pictureChecks}:{})};
  });
  await json(resolve(dir,'report.json'),result);
  // A contact sheet for quickly inspecting the chosen shots, then individual PNGs.
  await command('ffmpeg',['-y','-v','error','-pattern_type','glob','-i',resolve(dir,'*.png'),'-vf',`scale=480:-1,tile=3x${Math.ceil(result.samples.length/3)}`,'-frames:v','1',resolve(e.paths.build,'storyboard.jpg')]);
  return result;
}

export async function render(e,{viewer,width=e.output.width,fps=e.output.fps,audio=null,label='rehearsal'}) {
  // Re-read measured takes even when the caller resolved them earlier: a
  // cache hit must not launder a removed or changed speech take in a reused e.
  await resolveWordTiming(e,shot=>readSpeechTake(e,shot));
  validateWordFramesAtFps(e,fps);
  const captions=audio?.captions??[];
  const fontFile=async(name,style='Regular')=>{
    const path=await command('fc-match',['-f','%{file}',`${name}:style=${style}`]).catch(()=>null);
    return path?{path,sha256:await fileHash(path)}:null;
  };
  const fontRecord=await fontFile(e.style.fontFamily??'DejaVu Sans');
  const filmBold=await fontFile(e.style.fontFamily??'DejaVu Sans','Bold');
  const codeFontRecord=await fontFile('DejaVu Sans Mono');
  const codeBold=await fontFile('DejaVu Sans Mono','Bold');
  const fontFaces={film:{regular:fontRecord,bold:filmBold},code:{regular:codeFontRecord,bold:codeBold}};
  const report=await browserSession(e,viewer,width,captions,async({page,pose,info})=>{
    const sharedHashes=Object.fromEntries(Object.entries(info.hashes).filter(([url])=>!url.startsWith('/pictures/')));
    const commonKey=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,hashes:sharedHashes,browser:info.browser,
      viewerApi:info.viewerApi,width,height:info.height,fps,
      duration:e.output.durationSeconds,format:e.format,style:e.style,series:e.series??e.title,
      initial:frameAt(e,0,captions),fonts:fontFaces,
      renderer:await fileHash(resolve(here,'render.mjs')),timeline:await fileHash(resolve(here,'timeline.mjs')),
      pictures:await fileHash(resolve(here,'pictures.mjs')),
      easing:await fileHash(resolve(here,'easing.mjs')),
      words:await fileHash(resolve(here,'words.mjs')),
      pixels:await fileHash(resolve(here,'pixels.mjs')),
      sourceRenderer:await fileHash(resolve(here,'code.mjs')),
      shotCache:await fileHash(resolve(here,'shot-cache.mjs')),
      dependencies:await fileHash(resolve(here,'../package-lock.json'))}));
    const {count,units}=outputShotUnits(e,fps,captions);
    await fingerprintShotUnits(e,units,commonKey);
    const root=shotCacheRoot(e.paths.build),selections=new Map(),shotReports=[];
    const captureProvenance={workflowHead:(await command('git',['rev-parse','HEAD'],{cwd:resolve(here,'..')})).trim(),
      projectHead:(await command('git',['rev-parse','HEAD'],{cwd:e.paths.repository})).trim(),
      episodeSha256:await fileHash(e.paths.episode),productionSha256:await fileHash(e.paths.production),
      viewerSha256:sharedHashes['/viewer.js'],modelSha256:sharedHashes['/model/manifest.json'],
      browser:info.browser,commonKey};
    const started=Date.now();
    let capturedFrames=0,reusedFrames=0;
    for(const unit of units){
      let selected=await findShotGeneration(root,unit,commonKey,width,info.height);
      const reused=Boolean(selected);
      if(!selected){
        selected=await captureShotGeneration(root,unit,commonKey,width,info.height,async frame=>{
          await pose(frame.time);
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
    return {identity,dir,count,cache:{schema:SHOT_CACHE_SCHEMA,commonKey,capturedFrames,reusedFrames,shots:shotReports}};
  });
  const output=resolve(e.paths.build,`${label}.mp4`);
  const publicationId=randomUUID(),pendingOutput=resolve(e.paths.build,`${label}.pending-${publicationId}.mp4`);
  const args=['-y','-v','error','-framerate',String(fps),'-start_number','0','-i',resolve(report.dir,'%06d.png')];
  if(audio)args.push('-i',audio.mix,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k');
  args.push('-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-t',String(e.output.durationSeconds),pendingOutput);
  console.log('Encoding '+output);await command('ffmpeg',args);
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',pendingOutput]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  if(Number(video.nb_read_frames)!==report.count||video.width!==report.width||video.height!==report.height)throw new Error('Encoded video does not match requested frames/dimensions');
  if(audio&&!probe.streams.some(s=>s.codec_type==='audio'))throw new Error('Encoded video has no audio');
  if(probe.format)probe.format.filename=output;
  const thumbnail=resolve(e.paths.build,'thumbnail.png'),pendingThumbnail=`${thumbnail}.pending-${publicationId}`;
  await copyFile(resolve(report.dir,`${String(Math.min(report.count-1,Math.floor(Math.min(10,e.output.durationSeconds*.5)*fps))).padStart(6,'0')}.png`),pendingThumbnail);
  const subtitles=audio?resolve(e.paths.build,`${label}.srt`):null;
  const pendingSubtitles=subtitles?`${subtitles}.pending-${publicationId}`:null;
  if(pendingSubtitles)await writeFile(pendingSubtitles,srt(captions));
  const usedStills=new Set(),usedClips=new Set(),pictureCues=[];
  for(const shot of e.shots)for(const [index,cue] of (shot.pictures??[]).entries()){
    const kind=cue.still!==undefined?'still':'clip',name=cue[kind],media=e.pictureMedia[kind==='still'?'stills':'clips'][name];
    (kind==='still'?usedStills:usedClips).add(name);
    const record={...pictureReports(e,width).find(r=>r.shotId===shot.id&&r.index===index)};
    if(kind==='clip'){
      const cadence=clipCadenceForCue(e,shot,cue,media,fps);
      Object.assign(record,{filmRate:fps,dropped:cadence.dropped,repeated:cadence.repeated});
    }
    pictureCues.push(record);
  }
  const publicMedia=media=>{const {file,...record}=media;return record;};
  const pictures={stills:Object.fromEntries(Object.entries(e.pictureMedia?.stills??{}).map(([name,media])=>[name,{...publicMedia(media),
      cues:pictureCues.filter(c=>c.kind==='still'&&c.name===name)}])),
    clips:Object.fromEntries(Object.entries(e.pictureMedia?.clips??{}).map(([name,media])=>[name,{...publicMedia(media),
      cues:pictureCues.filter(c=>c.kind==='clip'&&c.name===name)}])),cues:pictureCues};
  const pictureReleaseIssues=[];
  for(const [kind,names] of [['still',usedStills],['clip',usedClips]])for(const name of names){
    const media=e.pictureMedia[kind==='still'?'stills':'clips'][name];
    for(const field of ['credit','rights'])if(media[field]===null)pictureReleaseIssues.push(`${kind} ${name} has unresolved ${field}`);
    if(!media.committed)pictureReleaseIssues.push(`${kind} ${name} is not committed at project HEAD`);
  }
  const description=await readFile(resolve(dirname(e.paths.production),e.release.descriptionTemplate),'utf8');
  if((usedStills.size||usedClips.size)&&!description.includes('{{pictureCredits}}'))
    pictureReleaseIssues.push('Description template lacks {{pictureCredits}} for shown pictures');
  const pictureCredits=[...Array.from(usedStills,name=>({kind:'stills',name})),
    ...Array.from(usedClips,name=>({kind:'clips',name}))].map(({kind,name})=>{
    const media=e.pictureMedia[kind][name];
    return `${name}: ${media.credit??`[PICTURE CREDIT PENDING: ${name}]`}`;
  }).join('\n');
  const releaseReady=Boolean(e.release.simulationUrl&&e.release.sourceUrl)&&pictureReleaseIssues.length===0;
  const descriptionOutput=resolve(e.paths.build,'description.md'),pendingDescription=`${descriptionOutput}.pending-${publicationId}`;
  await writeFile(pendingDescription,description
    .replaceAll('{{simulationUrl}}',e.release.simulationUrl??'[PUBLIC SIMULATION URL PENDING]')
    .replaceAll('{{sourceUrl}}',e.release.sourceUrl??'[PUBLIC SOURCE URL PENDING]')
    .replaceAll('{{pictureCredits}}',pictureCredits));
  const gitHead=async cwd=>(await command('git',['rev-parse','HEAD'],{cwd})).trim();
  const workflow=await gitHead(resolve(here,'..'));
  const project=await gitHead(e.paths.repository);
  const manifestOutput=resolve(e.paths.build,`${label}-manifest.json`),pendingManifest=`${manifestOutput}.pending-${publicationId}`;
  const outputSha256=await fileHash(pendingOutput);
  const manifest={...report,fps,output,outputSha256,
    audio:audio?.records??[],subtitles:pendingSubtitles?{file:subtitles,sha256:await fileHash(pendingSubtitles),burnedIn:false}:null,
    episode:e,probe,pictures,pictureReleaseIssues,releaseReady,
    provenance:{workflowHead:workflow,projectHead:project,font:fontRecord,codeFont:codeFontRecord,fontFaces,
      episodeSha256:await fileHash(e.paths.episode),productionSha256:await fileHash(e.paths.production),
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
  await rename(pendingDescription,descriptionOutput);
  await rename(pendingManifest,manifestOutput);
  if(backedUp)await unlink(previous).catch(error=>console.warn(`Previous-output backup remains: ${error.message}`));
  return output;
}
