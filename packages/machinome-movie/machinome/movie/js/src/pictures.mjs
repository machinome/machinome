// Project-held, time-pure still and clip pictures. The browser only draws the
// resolved frame; paths, codecs, rights and geometry are checked here first.
import {readFile,realpath,mkdir,readdir,writeFile,stat} from 'node:fs/promises';
import {resolve,dirname,relative,extname,isAbsolute} from 'node:path';
import {execFileSync} from 'node:child_process';
import {ease} from './easing.mjs';
import {hash,fileHash,command,json,sourceBase} from './util.mjs';

const need=(ok,message)=>{if(!ok)throw new Error(message);};
const finite=n=>typeof n==='number'&&Number.isFinite(n);
const modern=e=>(e.format??'machinome-video-draft/0.2')==='machinome-video-draft/0.4';
const inside=(root,path)=>{const rel=relative(root,path);return !isAbsolute(rel)&&rel!=='..'&&!rel.startsWith('../');};
const near=(a,b)=>Math.abs(a-b)<=1e-9;
const seconds=x=>+x.toFixed(6);
export const STAGE_AREAS=Object.freeze({plain:Object.freeze([.05,.16,.90,.63]),code:Object.freeze([.56,.20,.42,.65])});
const FIELD_MEDIA=new Set(['file','credit','rights','upscale']);
const FIELD_PICTURE=new Set(['from','to','still','clip','area','fit','enter','leave','view','inPoint']);
const FIELD_VIEW=new Set(['at','center','zoom','ease']);
const FIELD_FADE=new Set(['kind','duration','ease']);
const EASINGS=['linear','smooth','in','out','in-out'];

export function viewAt(keys,local){
  if(!keys?.length)return {center:[.5,.5],zoom:1};
  let a=keys[0],b=a;
  for(const key of keys){if(key.at<=local+1e-9)a=key;else{b=key;break;}b=a;}
  if(a===b||local<=a.at)return {center:[...a.center],zoom:a.zoom};
  const u=(local-a.at)/(b.at-a.at),w=ease(b.ease??'smooth',u);
  if(w<=0)return {center:[...a.center],zoom:a.zoom};
  if(w>=1)return {center:[...b.center],zoom:b.zoom};
  const z=a.zoom===b.zoom?a.zoom:a.zoom*(b.zoom/a.zoom)**w;
  const k=a.zoom===b.zoom?w:(1-a.zoom/z)/(1-a.zoom/b.zoom);
  return {center:a.center.map((v,i)=>v+(b.center[i]-v)*k),zoom:z};
}

export function pictureRect(media,area,fit='contain',view={center:[.5,.5],zoom:1}){
  const [,,wa,ha]=area,scale=(fit==='cover'?Math.max:Math.min)(wa/media.width,ha/media.height)*view.zoom;
  const w=scale*media.width/wa,h=scale*media.height/ha;
  const x=.5-view.center[0]*w,y=.5-view.center[1]*h;
  return [x,y,w,h];
}

export function clipFrameAt(timestamps,instant){
  need(Array.isArray(timestamps)&&timestamps.length>0,'Clip has no usable frame timestamps');
  let lo=0,hi=timestamps.length;
  while(lo<hi){const mid=(lo+hi)>>1;if(timestamps[mid]<=instant+1e-9)lo=mid+1;else hi=mid;}
  return Math.max(0,lo-1);
}
const clipFrameBefore=(timestamps,end)=>{
  let lo=0,hi=timestamps.length;
  while(lo<hi){const mid=(lo+hi)>>1;if(timestamps[mid]<end-1e-9)lo=mid+1;else hi=mid;}
  return Math.max(0,lo-1);
};
export function clipCadence(timestamps,start,end,fps,sampleOffset=0){
  const shown=[];
  for(let i=0;start+sampleOffset+i/fps<end-1e-9;i++)
    shown.push(clipFrameAt(timestamps,start+sampleOffset+i/fps));
  const begin=clipFrameAt(timestamps,start),last=clipFrameBefore(timestamps,end);
  return {shown,dropped:Math.max(0,last-begin+1-new Set(shown).size),
    repeated:shown.length-new Set(shown).size};
}
export function clipCadenceForCue(e,shot,cue,media,fps=e.output.fps){
  const globalStart=shot.start+cue.from,first=Math.ceil(globalStart*fps-1e-9)/fps;
  const phase=Math.max(0,first-globalStart),start=cue.inPoint??0;
  const next=e.shots[e.shots.indexOf(shot)+1]?.transition;
  const continuation=near(cue.to,shot.end-shot.start)&&next?
    next.kind==='fade'?next.duration/2:next.duration:0;
  return clipCadence(media.timestamps,start,start+cue.to-cue.from+continuation,fps,phase);
}

const overlap=(a,b)=>a.from<b.to&&b.from<a.to;
export function validatePictureCues(e,shot){
  if(shot.pictures===undefined)return;
  need(modern(e),`Pictures need format machinome-video-draft/0.4: shot ${shot.id}`);
  need(Array.isArray(shot.pictures),`Pictures must be a list: shot ${shot.id}`);
  const duration=shot.end-shot.start,ordered=[];
  for(const [index,cue] of shot.pictures.entries()){
    const where=`picture #${index} in shot ${shot.id}`;
    need(cue&&typeof cue==='object'&&!Array.isArray(cue),`Invalid ${where}`);
    for(const key of Object.keys(cue))need(FIELD_PICTURE.has(key),`Unknown picture field: ${key} (${where})`);
    need(finite(cue.from)&&finite(cue.to)&&cue.from>=0&&cue.from<cue.to&&cue.to<=duration,
      `Invalid picture times: ${where}`);
    need((cue.still!==undefined)!==(cue.clip!==undefined),`Give exactly one of still or clip: ${where}`);
    const kind=cue.still!==undefined?'still':'clip',name=cue[kind];
    need(typeof name==='string'&&name.length>0&&e[kind==='still'?'stills':'clips']?.[name],
      `Unknown ${kind}: ${name} (${where})`);
    need(cue.area===undefined||['stage','frame'].includes(cue.area),`Invalid picture area: ${where}`);
    need(cue.fit===undefined||['contain','cover'].includes(cue.fit),`Invalid picture fit: ${where}`);
    if(kind==='still')need(cue.inPoint===undefined,`inPoint belongs to a clip: ${where}`);
    else{
      need(cue.view===undefined,`view belongs to a still: ${where}`);
      need(cue.inPoint===undefined||(finite(cue.inPoint)&&cue.inPoint>=0),`Invalid clip inPoint: ${where}`);
    }
    if(cue.view!==undefined){
      need(Array.isArray(cue.view)&&cue.view.length>0,`Invalid view keys: ${where}`);
      let prior=-Infinity;
      for(const [k,key] of cue.view.entries()){
        need(key&&typeof key==='object'&&!Array.isArray(key),`Invalid view key #${k}: ${where}`);
        for(const field of Object.keys(key))need(FIELD_VIEW.has(field),`Unknown view key field: ${field} (${where})`);
        need(finite(key.at)&&key.at>=cue.from&&key.at<=cue.to&&key.at>prior,
          `View keys must increase inside the picture: ${where}`);prior=key.at;
        need(Array.isArray(key.center)&&key.center.length===2&&key.center.every(n=>finite(n)&&n>=0&&n<=1),
          `Invalid view center: ${where}`);
        need(finite(key.zoom)&&key.zoom>=1,`Invalid view zoom: ${where}`);
        if(key.ease!==undefined){
          need(k>0,`Nothing to ease before the first view key: ${where}`);
          need(EASINGS.includes(key.ease),`Unknown easing ${key.ease}: ${where}`);
        }
      }
    }
    for(const field of ['enter','leave'])if(cue[field]!==undefined){
      const fade=cue[field],label=field==='enter'?'entrance':'exit';
      need(fade&&typeof fade==='object'&&!Array.isArray(fade),`Invalid ${label}: ${where}`);
      for(const key of Object.keys(fade))need(FIELD_FADE.has(key),`Unknown ${label} field: ${key} (${where})`);
      need(fade.kind==='fade',`Picture ${label} kind must be fade: ${where}`);
      need(finite(fade.duration)&&fade.duration*e.output.fps>=2-1e-9,
        `Picture ${label} duration must be at least two frames: ${where}`);
      need(fade.duration<=cue.to-cue.from+1e-9,`Picture ${label} exceeds cue: ${where}`);
      if(fade.ease!==undefined)need(EASINGS.includes(fade.ease),`Unknown easing ${fade.ease}: ${where}`);
    }
    need((cue.enter?.duration??0)+(cue.leave?.duration??0)<=seconds(cue.to-cue.from)+1e-9,
      `Picture entrance and exit overlap: ${where}`);
    for(const prior of ordered)need(!overlap(prior,cue),`Pictures overlap in shot ${shot.id}`);
    ordered.push(cue);
    for(const [i,annotation] of (shot.annotations??[]).entries())
      need(!overlap(annotation,cue),`Annotation #${i} overlaps picture #${index} in shot ${shot.id}; a picture covers the model`);
    for(const [i,highlight] of (shot.highlight??[]).entries())
      need(!overlap(highlight,cue),`Highlight #${i} overlaps picture #${index} in shot ${shot.id}; a picture covers the model`);
  }
}

function validateEntry(entry,name,kind){
  need(entry&&typeof entry==='object'&&!Array.isArray(entry),`Invalid ${kind} ${name}`);
  for(const key of Object.keys(entry))need(FIELD_MEDIA.has(key),`Unknown ${kind} field: ${key} (${kind} ${name})`);
  need(typeof entry.file==='string'&&entry.file.length>0,`Missing file: ${kind} ${name}`);
  for(const key of ['credit','rights'])need(Object.hasOwn(entry,key)&&
    (entry[key]===null||typeof entry[key]==='string'&&entry[key].trim().length>0),
    `Missing or invalid ${key}: ${kind} ${name}`);
  if(entry.upscale!==undefined){
    need(kind!=='still'||extname(entry.file).toLowerCase()!=='.svg',`upscale is not allowed on SVG still ${name}`);
    need(finite(entry.upscale)&&entry.upscale>=1,`Invalid upscale allowance: ${kind} ${name}`);
  }
}

const probe=async(file,args=[])=>JSON.parse(await command('ffprobe',['-v','error',...args,'-of','json',file]));
function svgSize(source,name){
  const root=/<svg\b([^>]*)>/i.exec(source);
  need(root,`Still ${name} is not an SVG picture`);
  const attrs=root[1],found=/\bviewBox\s*=\s*(["'])(.*?)\1/i.exec(attrs);
  if(!found){
    const width=/\bwidth\s*=\s*(["'])(.*?)\1/i.exec(attrs)?.[2],height=/\bheight\s*=\s*(["'])(.*?)\1/i.exec(attrs)?.[2];
    const suggestion=width&&height?`; for width ${width} and height ${height} add viewBox="0 0 ${width} ${height}"`:'';
    throw new Error(`SVG still ${name} needs a viewBox${suggestion}`);
  }
  const nums=found[2].trim().split(/[\s,]+/).map(Number);
  need(nums.length===4&&nums.every(finite)&&nums[2]>0&&nums[3]>0,
    `SVG still ${name} has an invalid viewBox`);
  for(const [label,pattern] of [
    ['script',/<script\b|\bon\w+\s*=/i],['foreignObject',/<foreignObject\b/i],
    ['animation',/<animate(?:Motion|Transform)?\b|<set\b|@keyframes|\b(?:animation|transition)(?:-[\w-]+)?\s*:/i]])
    need(!pattern.test(source),`SVG still ${name} contains ${label}`);
  for(const match of source.matchAll(/\b(?:xlink:)?href\s*=\s*(?:(["'])(.*?)\1|([^\s>]+))/gi))
    need((match[2]??match[3]).trim().startsWith('#'),`SVG still ${name} contains external href`);
  for(const match of source.matchAll(/\burl\(([^)]*)\)/gi)){
    const target=match[1].trim().replace(/^(["'])(.*)\1$/,'$2').trim();
    need(target.startsWith('#'),`SVG still ${name} contains external href`);
  }
  need(!/@import\b/i.test(source),`SVG still ${name} contains external href`);
  return {width:nums[2],height:nums[3],viewBox:nums};
}
function committed(root,path){
  const rel=relative(root,path);
  try{
    execFileSync('git',['ls-files','--error-unmatch','--',rel],{cwd:root,stdio:'ignore'});
    execFileSync('git',['diff','--quiet','HEAD','--',rel],{cwd:root,stdio:'ignore'});
    return true;
  }catch{return false;}
}
function clipTimestamps(frames,name,stream){
  const base=/^(\d+)\/(\d+)$/.exec(stream.time_base??'');
  need(base&&Number(base[1])>0&&Number(base[2])>0,
    `Clip ${name} has no usable frame timestamps; re-encode it`);
  const seconds=Number(base[1])/Number(base[2]);
  const raw=frames.map(f=>Number(f.best_effort_timestamp));
  need(raw.every((t,i)=>Number.isFinite(t)&&fSafe(frames[i].best_effort_timestamp)),
    `Clip ${name} has no usable frame timestamps; re-encode it`);
  const times=raw.map(t=>(t-raw[0])*seconds);
  need(times.length>0&&times.every(finite)&&times.every((t,i)=>i===0||t>times[i-1]),
    `Clip ${name} has no usable frame timestamps; re-encode it`);
  return {times:times.map(t=>t-times[0]),seconds};
}
const fSafe=value=>(typeof value==='number'||typeof value==='string')&&Number.isSafeInteger(Number(value));
export function inspectClipProbe(data,name){
  const stream=data.streams?.[0];
  need(['h264','hevc','vp8','vp9','av1'].includes(stream?.codec_name),`Unsupported clip codec: ${name}`);
  need(['progressive','unknown',undefined].includes(stream.field_order)&&
    !(data.frames??[]).some(f=>f.interlaced_frame===1),`Clip ${name} is interlaced; deinterlace it deliberately first`);
  need(['1:1','N/A',undefined].includes(stream.sample_aspect_ratio),`Clip ${name} has non-square pixels`);
  need(!stream.tags?.rotate&&!stream.side_data_list?.some(x=>Number(x.rotation)),`Clip ${name} has a rotation tag`);
  const frames=data.frames??[],{times:timestamps,seconds}=clipTimestamps(frames,name,stream);
  const final=Number(frames.at(-1)?.pkt_duration)*seconds,
    prior=timestamps.length>1?timestamps.at(-1)-timestamps.at(-2):NaN;
  const end=timestamps.at(-1)+(finite(final)&&final>0?final:prior);
  need(finite(end)&&end>timestamps.at(-1),`Clip ${name} has no usable frame timestamps; re-encode it`);
  const rate=stream.avg_frame_rate?.split('/').map(Number),averageRate=rate?.length===2&&rate[1]?rate[0]/rate[1]:timestamps.length/end;
  return {codec:stream.codec_name,width:stream.width,height:stream.height,
    timestamps,end,averageRate,frameCount:timestamps.length,audio:'not played'};
}
// Probe every still and clip the source names: paths inside the project,
// formats, sizes, timestamps, hashes and committed status.
async function probeMedia(e){
  const root=e.paths.repository,base=sourceBase(e),result={stills:{},clips:{}};
  for(const [kind,map] of [['still',e.stills??{}],['clip',e.clips??{}]])for(const [name,entry] of Object.entries(map)){
    validateEntry(entry,name,kind);
    const ext=extname(entry.file).toLowerCase();
    need((kind==='still'?['.png','.jpg','.jpeg','.webp','.svg']:['.mp4','.webm']).includes(ext),
      `Unsupported ${kind} extension: ${name}`);
    const file=await realpath(resolve(base,entry.file));
    need(inside(root,file),`${kind[0].toUpperCase()+kind.slice(1)} ${name} is outside the project repository`);
    const info={file,path:relative(root,file),sha256:await fileHash(file),committed:committed(root,file),
      credit:entry.credit??null,rights:entry.rights??null,upscale:entry.upscale??1};
    if(kind==='still'){
      if(ext==='.svg')Object.assign(info,{format:'svg',...svgSize(await readFile(file,'utf8'),name)});
      else{
        const data=await probe(file,['-count_frames','-select_streams','v:0','-show_streams']);
        const stream=data.streams?.[0],expected=ext==='.png'?'png':ext==='.webp'?'webp':'mjpeg';
        need(stream?.codec_name===expected&&Number(stream.nb_read_frames)===1,
          `Still ${name} is not a single PNG, JPEG or WebP picture`);
        Object.assign(info,{format:ext.slice(1),width:stream.width,height:stream.height});
      }
      result.stills[name]=info;
    }else{
      const data=await probe(file,['-show_streams','-show_frames','-select_streams','v:0']);
      Object.assign(info,{format:ext.slice(1),...inspectClipProbe(data,name)});
      result.clips[name]=info;
    }
  }
  return result;
}
// A YAML episode's pictures (format 0.4 only), checked as they always were;
// a movie's media, whose geometry is checked against the slot's box the stage
// reports (design D8).
export async function loadPictures(e){
  if(e.source==='movie'){e.pictureMedia=await probeMedia(e);return e.pictureMedia;}
  if(!modern(e)){e.pictureMedia={stills:{},clips:{}};return e.pictureMedia;}
  e.pictureMedia=await probeMedia(e);
  validateLoadedPictures(e);
  return e.pictureMedia;
}

const areaPixels=(e,shot,cue,width=e.output.width)=>{
  const scale=width/e.output.width,height=e.output.height*scale;
  if((cue.area??'stage')==='frame')return [0,0,width,height];
  const [x,y,w,h]=STAGE_AREAS[shot.code?'code':'plain'];return [x*width,y*height,w*width,h*height];
};
const peakZoom=cue=>Math.max(1,...(cue.view??[]).map(v=>v.zoom));
function enlargement(e,shot,cue,width=e.output.width){
  const kind=cue.still!==undefined?'still':'clip',name=cue[kind],media=e.pictureMedia[kind==='still'?'stills':'clips'][name];
  if(media.format==='svg')return {peak:null,allowance:null,media};
  const area=areaPixels(e,shot,cue,width),s0=(cue.fit==='cover'?Math.max:Math.min)(area[2]/media.width,area[3]/media.height);
  return {peak:s0*peakZoom(cue),allowance:media.upscale,media,area};
}
export function validatePictureSizing(e,width=e.output.width){
  for(const shot of e.shots)for(const cue of shot.pictures??[]){
    const {peak,allowance,media,area}=enlargement(e,shot,cue,width);
    if(peak!==null)need(peak<=allowance+1e-9,
      `${cue.still!==undefined?'Still':'Clip'} ${cue.still??cue.clip} would be enlarged ${peak.toFixed(2)}× in shot ${shot.id} (${media.width}×${media.height} source pixels in the ${area[2]}×${area[3]} ${cue.area??'stage'} area); its upscale allowance is ${allowance}. Set upscale on the ${cue.still!==undefined?'still':'clip'}, choose area: stage, or use a larger source.`);
  }
}
// How much a picture drawn at `drawn` CSS pixels wide from a source `natural`
// pixels wide is enlarged at output width `outputWidth` for a page `width` wide.
export const drawnEnlargement=(drawnWidth,naturalWidth,pageWidth,outputWidth)=>drawnWidth/naturalWidth*(outputWidth/pageWidth);
export function pictureReports(e,width=e.output.width){
  return e.shots.flatMap(shot=>(shot.pictures??[]).map((cue,index)=>{
    const {peak,allowance,media}=enlargement(e,shot,cue,width);
    return {shotId:shot.id,index,kind:cue.still!==undefined?'still':'clip',name:cue.still??cue.clip,peak,allowance,
      width:media.width,height:media.height,averageRate:media.averageRate,frameCount:media.frameCount};
  }));
}
function validateLoadedPictures(e){
  if(!modern(e))return;
  validatePictureSizing(e);
  const fps=e.output.fps;
  for(const [shotIndex,shot] of e.shots.entries())for(const [index,cue] of (shot.pictures??[]).entries()){
    const kind=cue.still!==undefined?'still':'clip',name=cue[kind],media=e.pictureMedia[kind==='still'?'stills':'clips'][name];
    if(kind==='clip'){
      const next=e.shots[shotIndex+1]?.transition;
      const continuation=near(cue.to,shot.end-shot.start)&&next?
        next.kind==='fade'?next.duration/2:next.duration:0;
      const required=(cue.inPoint??0)+(cue.to-cue.from)+continuation;
      need(required<=media.end+1e-9,
        `Clip ${name} ends at ${media.end.toFixed(2)} s, before ${(cue.inPoint??0)} + ${(cue.to-cue.from+continuation)} s needed by picture #${index} in shot ${shot.id}`);
    }
    // Validate every output frame, not merely the view keys. A mixed zoom and
    // pan can leave the picture between two valid endpoints.
    for(let frame=Math.ceil((shot.start+cue.from)*fps-1e-9);frame/fps<shot.start+cue.to-1e-9;frame++){
      const local=frame/fps-shot.start,view=kind==='still'?viewAt(cue.view,local):{center:[.5,.5],zoom:1};
      const rect=pictureRect(media,areaPixels(e,shot,cue),cue.fit??'contain',view);
      for(const axis of [0,1]){
        const start=rect[axis],size=rect[axis+2];
        const framed=size>=1-1e-9?start<=1e-9&&start+size>=1-1e-9:
          start>=-1e-9&&start+size<=1+1e-9;
        need(framed,`Picture view leaves the picture in shot ${shot.id} at ${(frame/fps).toFixed(2)} s (picture #${index}, ${name}); keep the view inside the picture or zoom in`);
      }
    }
  }
}

function opacity(cue,local){
  const incoming=cue.enter?ease(cue.enter.ease??'smooth',(local-cue.from)/cue.enter.duration):1;
  const outgoing=cue.leave?1-ease(cue.leave.ease??'smooth',(local-(cue.to-cue.leave.duration))/cue.leave.duration):1;
  return Math.min(incoming,outgoing);
}
export function pictureAt(e,shot,local){
  const duration=shot.end-shot.start,past=local>=duration;
  const index=(shot.pictures??[]).findIndex(c=>local>=c.from-1e-9&&
    (local<c.to-1e-9||past&&near(c.to,duration)));
  if(index<0)return null;
  const cue=shot.pictures[index],kind=cue.still!==undefined?'still':'clip',name=cue[kind];
  const media=e.pictureMedia?.[kind==='still'?'stills':'clips']?.[name];
  if(!media)throw new Error(`Picture media is not resolved: ${name} in shot ${shot.id}`);
  const view=kind==='still'?viewAt(cue.view,local):{center:[.5,.5],zoom:1};
  const rect=pictureRect(media,areaPixels(e,shot,cue),cue.fit??'contain',view);
  const result={index,kind,name,area:cue.area??'stage',rect,opacity:past&&cue.leave?0:opacity(cue,local)};
  if(kind==='still')result.view=view;
  else{const clipSeconds=(cue.inPoint??0)+Math.max(0,local-cue.from);
    result.clipSeconds=clipSeconds;result.frame=clipFrameAt(media.timestamps,clipSeconds);}
  return result;
}

const ffmpegVersion=async()=>(await command('ffmpeg',['-version'])).split('\n')[0];
// Decode each clip's frames the film shows, once, into the build directory.
// `uses` are [{name, inPoint, span}] (span includes a transition's continuation).
export async function extractClips(e,uses=episodeClipUses(e)){
  if(!Object.keys(e.pictureMedia?.clips??{}).length)return;
  const version=await ffmpegVersion();
  for(const [name,media] of Object.entries(e.pictureMedia?.clips??{})){
    const ranges=uses.filter(u=>u.name===name).map(u=>[clipFrameAt(media.timestamps,u.inPoint),clipFrameBefore(media.timestamps,u.inPoint+u.span)]);
    if(!ranges.length)continue;
    const start=Math.min(...ranges.map(x=>x[0])),end=Math.max(...ranges.map(x=>x[1]));
    const filter=`select=between(n\\,${start}\\,${end})`,args=['-i',media.file,'-vf',filter,'-vsync','0'];
    const key=hash(JSON.stringify({sha256:media.sha256,start,end,args,version}));
    const dir=resolve(e.paths.build,'clips',key.slice(0,16));await mkdir(dir,{recursive:true});
    const record=resolve(dir,'index.json');let index;
    try{index=JSON.parse(await readFile(record,'utf8'));}catch(error){if(error.code!=='ENOENT')throw error;}
    const listed=Array.from({length:end-start+1},(_,i)=>start+i);
    const complete=index?.key===key&&JSON.stringify(index.frames)===JSON.stringify(listed)&&
      (await Promise.all(listed.map(n=>stat(resolve(dir,`${String(n).padStart(6,'0')}.png`)).then(x=>x.size>0).catch(()=>false)))).every(Boolean);
    if(!complete){
      await command('ffmpeg',['-y','-v','error',...args,'-start_number',String(start),resolve(dir,'%06d.png')]);
      const files=(await readdir(dir)).filter(x=>x.endsWith('.png'));
      need(files.length===listed.length,`Clip ${name} decoded ${files.length} frames where ${listed.length} were listed; re-encode it`);
      index={key,frames:listed,ffmpegVersion:version};await json(record,index);
    }
    media.extraction={key,dir,start,end,ffmpegVersion:version,frames:listed};
  }
}
// The clip spans a YAML episode's picture cues show.
function episodeClipUses(e){
  return (e.shots??[]).flatMap((shot,shotIndex)=>(shot.pictures??[]).filter(c=>c.clip!==undefined).map(c=>{
    const next=e.shots[shotIndex+1]?.transition;
    const continuation=near(c.to,shot.end-shot.start)&&next?(next.kind==='fade'?next.duration/2:next.duration):0;
    return {name:c.clip,inPoint:c.inPoint??0,span:c.to-c.from+continuation};
  }));
}
