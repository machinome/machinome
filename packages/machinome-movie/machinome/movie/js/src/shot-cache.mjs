// Complete, attested shot generations. The film clock, not a shot-local clock,
// chooses output frames; a generation is reusable only after its index is last.
import {randomUUID} from 'node:crypto';
import {link,mkdir,readFile,readdir,rename,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {frameAt} from './timeline.mjs';
import {fileHash,hash,json} from './util.mjs';

export const SHOT_CACHE_SCHEMA='shot-v1';
const pngName=index=>`${String(index).padStart(6,'0')}.png`;
const pngSignature=Buffer.from([137,80,78,71,13,10,26,10]);
const missing=error=>error?.code==='ENOENT'||error?.code==='ENOTDIR';

export function outputShotUnits(e,fps,captions=[]){
  const count=e.output.durationSeconds*fps;
  if(!Number.isInteger(count))throw new Error('Frame count is not integral');
  const byId=new Map(e.shots.map(shot=>[shot.id,{shotId:shot.id,start:shot.start,end:shot.end,frames:[]}]));
  for(let index=0;index<count;index++){
    const time=index/fps,request=frameAt(e,time,captions),unit=byId.get(request.shotId);
    if(!unit)throw new Error(`Frame ${index} has no shot unit`);
    unit.frames.push({index,time,progress:time/e.output.durationSeconds,request});
  }
  return {count,units:e.shots.map(shot=>byId.get(shot.id))};
}

function reachedPictures(frame){
  return [frame.picture,frame.transition?.outgoing?.picture].filter(Boolean);
}

export async function fingerprintShotUnits(e,units,commonKey){
  const sourceHashes=new Map(),decodedHashes=new Map();
  for(const unit of units){
    const media=[];
    for(const {request} of unit.frames)for(const picture of reachedPictures(request)){
      const family=picture.kind==='still'?'stills':'clips';
      const item=e.pictureMedia?.[family]?.[picture.name];
      if(!item)throw new Error(`Missing ${picture.kind} ${picture.name} for shot cache`);
      const id=`${family}/${picture.name}`;
      if(!sourceHashes.has(id))sourceHashes.set(id,await fileHash(item.file));
      const record={kind:picture.kind,name:picture.name,sourceSha256:sourceHashes.get(id),
        format:item.format,codec:item.codec,width:item.width,height:item.height,upscale:item.upscale};
      if(picture.kind==='clip'){
        const path=resolve(item.extraction.dir,pngName(picture.frame));
        if(!decodedHashes.has(path))decodedHashes.set(path,await fileHash(path));
        Object.assign(record,{frame:picture.frame,timestamp:item.timestamps[picture.frame],
          decoder:item.extraction.ffmpegVersion,decodedSha256:decodedHashes.get(path)});
      }
      media.push(record);
    }
    const measured=[...new Set(unit.frames.flatMap(({request})=>[request.shotId,request.transition?.outgoing?.shotId].filter(Boolean)))]
      .flatMap(shotId=>{
        const timing=e.wordTiming?.[shotId];
        return timing?.sha256?[{shotId,sha256:timing.sha256,timingSha256:hash(JSON.stringify(timing))}]:[];
      });
    unit.media=media;unit.measured=measured;
    unit.key=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,commonKey,shotId:unit.shotId,
      start:unit.start,end:unit.end,frames:unit.frames,media,measured}));
  }
  return units;
}

export function shotCacheRoot(build){return resolve(build,'shot-cache',SHOT_CACHE_SCHEMA);}
function shotPath(root,unit){return resolve(root,hash(unit.shotId).slice(0,16),unit.key);}
export function generationPath(root,unit){return resolve(shotPath(root,unit),randomUUID());}

function pngDimensions(bytes){
  if(bytes.length<24||!bytes.subarray(0,8).equals(pngSignature)||bytes.toString('ascii',12,16)!=='IHDR')return null;
  return {width:bytes.readUInt32BE(16),height:bytes.readUInt32BE(20)};
}

async function verifiedIndex(path,unit,commonKey,width,height){
  let index;
  try{index=JSON.parse(await readFile(resolve(path,'index.json'),'utf8'));}
  catch(error){if(missing(error)||error instanceof SyntaxError)return null;throw error;}
  const expected=unit.frames;
  if(!index||Array.isArray(index)||typeof index!=='object'||
    index.schema!==SHOT_CACHE_SCHEMA||index.commonKey!==commonKey||index.shotKey!==unit.key||
    index.shotId!==unit.shotId||index.width!==width||index.height!==height||
    !Array.isArray(index.frames)||index.frames.length!==expected.length||
    !index.provenance||typeof index.provenance!=='object'||Array.isArray(index.provenance)||
    typeof index.provenance.workflowHead!=='string'||typeof index.provenance.projectHead!=='string'||
    index.provenance.commonKey!==commonKey||index.provenance.shotKey!==unit.key||
    JSON.stringify(index.media)!==JSON.stringify(unit.media)||
    JSON.stringify(index.measured)!==JSON.stringify(unit.measured))return null;
  for(let i=0;i<expected.length;i++){
    const wanted=expected[i],record=index.frames[i];
    if(!record||typeof record!=='object'||Array.isArray(record)||
      record.index!==wanted.index||record.time!==wanted.time||record.file!==pngName(wanted.index)||
      record.width!==width||record.height!==height||typeof record.sha256!=='string')return null;
    let bytes;
    try{bytes=await readFile(resolve(path,pngName(wanted.index)));}
    catch(error){if(missing(error))return null;throw error;}
    const size=pngDimensions(bytes);
    if(!size||size.width!==width||size.height!==height||hash(bytes)!==record.sha256)return null;
  }
  return index;
}

export async function findShotGeneration(root,unit,commonKey,width,height){
  const path=shotPath(root,unit);
  let names;
  try{names=await readdir(path);}catch(error){if(missing(error))return null;throw error;}
  for(const name of names.toSorted().reverse()){
    const generation=resolve(path,name);
    const index=await verifiedIndex(generation,unit,commonKey,width,height);
    if(index)return {generation,index};
  }
  return null;
}

export async function captureShotGeneration(root,unit,commonKey,width,height,capture,provenance){
  const generation=generationPath(root,unit);await mkdir(generation,{recursive:true});
  const frames=[];
  for(const frame of unit.frames){
    const bytes=await capture(frame),size=pngDimensions(bytes);
    if(!size||size.width!==width||size.height!==height)
      throw new Error(`Captured frame ${frame.index} has wrong PNG dimensions`);
    const file=pngName(frame.index),path=resolve(generation,file);
    await writeFile(path+'.tmp',bytes);await rename(path+'.tmp',path);
    frames.push({index:frame.index,time:frame.time,file,width,height,sha256:hash(bytes)});
  }
  const index={schema:SHOT_CACHE_SCHEMA,commonKey,shotKey:unit.key,shotId:unit.shotId,
    width,height,frames,media:unit.media,measured:unit.measured,provenance};
  await json(resolve(generation,'index.json'),index);
  return {generation,index};
}

export async function assembleShotFrames(root,units,selections,count){
  const dir=resolve(root,'assemblies',randomUUID());await mkdir(dir,{recursive:true});
  const found=new Set();
  for(const unit of units){
    const selected=selections.get(unit.shotId);
    if(!selected)throw new Error(`No verified generation for shot ${unit.shotId}`);
    for(const frame of unit.frames){
      if(found.has(frame.index))throw new Error(`Duplicate output frame ${frame.index}`);
      found.add(frame.index);
      await link(resolve(selected.generation,pngName(frame.index)),resolve(dir,pngName(frame.index)));
    }
  }
  if(found.size!==count||Array.from({length:count},(_,i)=>i).some(i=>!found.has(i)))
    throw new Error('Shot generations leave a hole in output frames');
  return dir;
}
