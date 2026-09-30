// Review material is decoded from the published MP4, not browser screenshots.
// This module intentionally imports neither episode nor timeline code.
import {randomUUID} from 'node:crypto';
import {spawn} from 'node:child_process';
import {once} from 'node:events';
import {copyFile,mkdir,readFile,readdir,realpath,stat,unlink,writeFile} from 'node:fs/promises';
import {resolve,dirname,relative,isAbsolute,join} from 'node:path';
import {deflateSync} from 'node:zlib';
import {command,fileHash,hash,json} from './util.mjs';
import {decodePng} from './pixels.mjs';

export const REVIEW_PACK_SCHEMA='review-pack-v1';
const PLAN_SCHEMA='review-samples-v1';
const missing=e=>e?.code==='ENOENT'||e?.code==='ENOTDIR';
const need=(ok,message)=>{if(!ok)throw new Error(message);};
const number=n=>Number.isSafeInteger(n)&&n>=0;
const pngName=index=>`${String(index).padStart(6,'0')}.png`;
const framePath=index=>`frames/${pngName(index)}`;
const LABEL_KINDS=new Set(['join','word-onset','source-emphasis-onset',
  'source-emphasis-clear','picture-entry','shot-end','film-end',
  'transition-midpoint','transition-last-active']);
const inside=(root,path)=>{const rel=relative(root,path);return rel!==''&&rel!=='..'&&
  !rel.startsWith('../')&&!isAbsolute(rel);};

function checkPlan(manifest){
  const p=manifest.reviewSamples;
  need(p?.schema===PLAN_SCHEMA,
    'Manifest has no compatible review plan (review-samples-v1); rerender this film before review');
  need(number(manifest.count)&&manifest.count>0&&number(manifest.width)&&manifest.width>0&&
    number(manifest.height)&&manifest.height>0&&Number.isFinite(manifest.fps)&&manifest.fps>0,
  'Manifest film dimensions/count/rate are invalid');
  need(p.frameCount===manifest.count&&p.fps===manifest.fps&&Array.isArray(p.samples),
    'Review plan frame count/rate differs from manifest; rerender');
  let previousEnd=-1,filmEnd=false;const seen=new Set();
  for(const sample of p.samples){
    const indices=sample?.indices,id=JSON.stringify(indices),end=indices?.at(-1);
    need(sample&&Array.isArray(sample.indices)&&[1,2].includes(sample.indices.length)&&
      sample.indices.every(i=>number(i)&&i<manifest.count)&&
      (sample.indices.length===1||sample.indices[1]===sample.indices[0]+1)&&
      end>=previousEnd&&!seen.has(id)&&Array.isArray(sample.labels)&&sample.labels.length>0,
    'Review plan has an invalid sample index or label; rerender');
    previousEnd=end;seen.add(id);
    for(const l of sample.labels){
      need(l&&LABEL_KINDS.has(l.kind)&&typeof l.shotId==='string'&&l.shotId.length>0&&
        typeof l.description==='string'&&
        l.visibility==='resolved candidate, not reviewed',
      'Review plan has an invalid kind, label or candidate qualifier; rerender');
      if(l.kind==='film-end'){
        need(end===manifest.count-1,'Review plan film-end is not the last frame; rerender');filmEnd=true;
      }
      if(l.kind==='join')need(typeof l.outgoingShotId==='string'&&
        Array.isArray(l.sides)&&l.sides.length>0,'Review plan join is incomplete; rerender');
      if(['word-onset','source-emphasis-onset'].includes(l.kind))
        need(number(l.authoredIndex)&&number(l.wordOrdinal)&&
          ['incoming','outgoing'].includes(l.side),
        'Review plan cue identity is incomplete; rerender');
      if(l.kind==='word-onset')need(number(l.shown)&&l.shown>0,
        'Review plan word count is invalid; rerender');
      if(l.kind==='source-emphasis-clear')need(number(l.authoredIndex)&&
        ['incoming','outgoing'].includes(l.side)&&Array.isArray(l.words)&&l.words.length>0&&
        l.words.every(word=>number(word.wordOrdinal)&&typeof word.word==='string'&&
          number(word.line)&&number(word.start)&&number(word.end)),
      'Review plan source clear identity is incomplete; rerender');
      if(l.kind==='picture-entry')need(number(l.authoredIndex)&&
        ['incoming','outgoing'].includes(l.side)&&
        (number(l.shown)||number(l.wordOrdinal)),
      'Review plan picture entry is incomplete; rerender');
      if(l.kind.startsWith('transition-'))need(['transition','fadeIn','fadeOut'].includes(l.field)&&
        Array.isArray(l.sides)&&l.sides.length>0,
      'Review plan transition interior is incomplete; rerender');
    }
  }
  need(filmEnd,'Review plan has no film-end sample; rerender');
  return p;
}

function ticks(value){
  if(typeof value==='number')need(Number.isSafeInteger(value),'Missing or unsafe decoded PTS timestamp');
  else need(typeof value==='string'&&/^-?(0|[1-9][0-9]*)$/.test(value),
    'Missing or unsafe decoded PTS timestamp');
  return BigInt(value);
}
function timeBase(value){
  need(typeof value==='string'&&/^[1-9][0-9]*\/[1-9][0-9]*$/.test(value),
    'Missing decoder PTS time base');
  return value;
}
export function validateDecodedFrames(frames,film){
  need(Array.isArray(frames)&&frames.length===film.count,
    'Decoded frame count differs from the manifest');
  let previous=null,base=null;
  for(let i=0;i<frames.length;i++){
    const f=frames[i];
    need(f&&f.index===i,`Decoded frame index/order differs at ${i}`);
    need(f.width===film.width&&f.height===film.height,
      `Decoded frame dimensions differ at ${i}`);
    const value=ticks(f.ptsTicks),tb=timeBase(f.timeBase);
    need(previous===null||value>previous,`Decoded PTS is not increasing at frame ${i}`);
    need(base===null||base===tb,'Decoded PTS time base changes within the film');
    previous=value;base=tb;
  }
  return frames;
}

function overviewIndices(count,fps){
  const stride=Math.max(1,Math.round(fps/2),Math.ceil((count-1)/95));
  const indices=[];for(let i=0;i<count;i+=stride)indices.push(i);
  if(indices.at(-1)!==count-1)indices.push(count-1);
  return indices;
}
const CELL_WIDTH=480,CELL_HEIGHT=330,COLS=4,CELLS_PER_PAGE=24;
function shortLabel(index,labels,metadata){
  const p=metadata.get(index),kind=labels?.length>1?'MULTI':labels?.[0]?.kind?.toUpperCase()??'OVERVIEW';
  const shot=labels?.[0]?.shotId?.slice(0,10).toUpperCase()??'';
  const a=`F${index} PTS:${p.ptsTicks} X${p.timeBase}`;
  need(a.length<=39,'Actual PTS label exceeds the review sheet cell');
  const b=`${kind} ${shot}`.slice(0,39);
  return `${a} | ${b}`;
}
function page(kind,groups,metadata){
  const cells=[];
  for(const group of groups)for(const index of group.indices)
    cells.push({index,labels:group.labels??[],printedLabel:shortLabel(index,group.labels,metadata),
      pairStart:group.indices.length===2&&index===group.indices[0],padding:false});
  while(cells.length<CELLS_PER_PAGE)cells.push({padding:true,printedLabel:'PADDING'});
  cells.forEach((cell,i)=>cell.rect={x:(i%COLS)*CELL_WIDTH,y:Math.floor(i/COLS)*CELL_HEIGHT,
    width:CELL_WIDTH,height:CELL_HEIGHT});
  return {kind,width:COLS*CELL_WIDTH,height:6*CELL_HEIGHT,cells};
}
export function planReviewPages(plan,metadata){
  need(plan?.schema===PLAN_SCHEMA&&number(plan.frameCount)&&plan.frameCount>0&&
    Number.isFinite(plan.fps)&&plan.fps>0&&metadata instanceof Map,
  'Cannot page an invalid review plan');
  const overview=overviewIndices(plan.frameCount,plan.fps),pages=[];
  for(let at=0;at<overview.length;at+=CELLS_PER_PAGE)
    pages.push(page('overview',overview.slice(at,at+CELLS_PER_PAGE).map(index=>({indices:[index]})),metadata));
  const pairs=plan.samples.filter(s=>s.indices.length===2),singles=plan.samples.filter(s=>s.indices.length===1);
  // Pairs stay contiguous; reserve no more than twelve pairs per page. A
  // labelled singleton can use a remaining cell but never divide a pair.
  let groups=[];
  const flush=()=>{if(groups.length){pages.push(page('events',groups,metadata));groups=[];}};
  for(const group of [...pairs,...singles]){
    const used=groups.reduce((n,g)=>n+g.indices.length,0);
    if(used+group.indices.length>CELLS_PER_PAGE)flush();
    groups.push(group);
  }
  flush();
  return {pages,overviewIndices:overview};
}

// Plain 8-bit RGB PNGs let the test compare every decoded pixel exactly. The
// scanlines use filter 0; checksums are standard PNG CRC32, not a tolerance.
const CRC_TABLE=Uint32Array.from({length:256},(_,index)=>{
  let value=index;for(let i=0;i<8;i++)value=value&1?0xedb88320^(value>>>1):value>>>1;
  return value>>>0;
});
function crc(bytes){let value=0xffffffff;for(const byte of bytes)value=CRC_TABLE[(value^byte)&255]^(value>>>8);return (value^0xffffffff)>>>0;}
function chunk(kind,body){
  const type=Buffer.from(kind,'ascii'),out=Buffer.alloc(12+body.length);
  out.writeUInt32BE(body.length,0);type.copy(out,4);body.copy(out,8);
  out.writeUInt32BE(crc(out.subarray(4,8+body.length)),8+body.length);return out;
}
function encodeRgbPng(width,height,rgb){
  need(rgb.length===width*height*3,'Decoded RGB frame has wrong byte count');
  const stride=width*3,scan=Buffer.alloc((stride+1)*height);
  for(let y=0;y<height;y++)rgb.copy(scan,y*(stride+1)+1,y*stride,(y+1)*stride);
  const ihdr=Buffer.alloc(13);ihdr.writeUInt32BE(width,0);ihdr.writeUInt32BE(height,4);ihdr[8]=8;ihdr[9]=2;
  return Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10]),chunk('IHDR',ihdr),
    chunk('IDAT',deflateSync(scan)),chunk('IEND',Buffer.alloc(0))]);
}

// Five-row fixed-format cell text: labels contain only numeric PTS/index,
// controlled event kind and a short slug. Full authored cue text stays JSON.
const GLYPHS={
  'A':['010','101','111','101','101'],'B':['110','101','110','101','110'],
  'C':['011','100','100','100','011'],'D':['110','101','101','101','110'],
  'E':['111','100','110','100','111'],'F':['111','100','110','100','100'],
  'G':['011','100','101','101','011'],'H':['101','101','111','101','101'],
  'I':['111','010','010','010','111'],'J':['011','001','001','101','010'],
  'K':['101','101','110','101','101'],'L':['100','100','100','100','111'],
  'M':['101','111','111','101','101'],'N':['101','111','111','111','101'],
  'O':['010','101','101','101','010'],'P':['110','101','110','100','100'],
  'Q':['010','101','101','011','001'],'R':['110','101','110','101','101'],
  'S':['011','100','010','001','110'],'T':['111','010','010','010','010'],
  'U':['101','101','101','101','111'],'V':['101','101','101','101','010'],
  'W':['101','101','111','111','101'],'X':['101','101','010','101','101'],
  'Y':['101','101','010','010','010'],'Z':['111','001','010','100','111'],
  '0':['111','101','101','101','111'],'1':['010','110','010','010','111'],
  '2':['110','001','111','100','111'],'3':['110','001','011','001','110'],
  '4':['101','101','111','001','001'],'5':['111','100','110','001','110'],
  '6':['011','100','110','101','010'],'7':['111','001','010','010','010'],
  '8':['010','101','010','101','010'],'9':['010','101','011','001','110'],
  '-':['000','000','111','000','000'],'/':['001','001','010','100','100'],
  '#':['101','111','101','111','101'],':':['000','010','000','010','000'],
  '.':['000','000','000','000','010'],' ':['000','000','000','000','000']};
function drawText(rgb,width,height,x,y,value){
  const scale=3,step=12;
  for(const [n,char] of [...value.toUpperCase()].entries()){
    const rows=GLYPHS[char]??GLYPHS[' '],left=x+n*step;
    for(let row=0;row<5;row++)for(let col=0;col<3;col++)if(rows[row][col]==='1')
      for(let dy=0;dy<scale;dy++)for(let dx=0;dx<scale;dx++){
        const px=left+col*scale+dx,py=y+row*scale+dy;
        if(px<0||px>=width||py<0||py>=height)continue;
        const at=(py*width+px)*3;rgb[at]=28;rgb[at+1]=30;rgb[at+2]=31;
      }
  }
}
function drawSheet(layout,frames){
  const {width,height}=layout,rgb=Buffer.alloc(width*height*3,244);
  for(const cell of layout.cells){
    const {x,y}=cell.rect;
    if(!cell.padding){
      const source=frames.get(cell.index);
      need(source,`Missing selected decoded image for sheet frame ${cell.index}`);
      const maxW=CELL_WIDTH,maxH=CELL_HEIGHT-54;
      const scale=Math.min(maxW/source.width,maxH/source.height);
      const drawnW=Math.floor(source.width*scale),drawnH=Math.floor(source.height*scale);
      const left=x+Math.floor((CELL_WIDTH-drawnW)/2),top=y+Math.floor((maxH-drawnH)/2);
      for(let row=0;row<drawnH;row++)for(let col=0;col<drawnW;col++){
        const sx=Math.min(source.width-1,Math.floor(col/scale)),sy=Math.min(source.height-1,Math.floor(row/scale));
        const from=(sy*source.width+sx)*3,to=((top+row)*width+left+col)*3;
        rgb[to]=source.rgb[from];rgb[to+1]=source.rgb[from+1];rgb[to+2]=source.rgb[from+2];
      }
    }
    const lines=cell.printedLabel.split(' | ');
    drawText(rgb,width,height,x+5,y+CELL_HEIGHT-48,lines[0].slice(0,39));
    if(lines[1])drawText(rgb,width,height,x+5,y+CELL_HEIGHT-25,lines[1].slice(0,39));
  }
  return encodeRgbPng(width,height,rgb);
}

function artifactPath(generation,file){
  if(typeof file!=='string'||!file||isAbsolute(file)||file.includes('\\'))return null;
  const path=resolve(generation,file);
  return inside(generation,path)?path:null;
}
async function verifiedFile(generation,file,sha,dimensions){
  const path=artifactPath(generation,file);
  if(!path||typeof sha!=='string'||!/^[a-f0-9]{64}$/.test(sha))return false;
  try{
    const actual=await realpath(path);
    if(!inside(generation,actual)||(await stat(actual)).isFile()===false)return false;
    const bytes=await readFile(actual);
    if(hash(bytes)!==sha)return false;
    const image=decodePng(bytes);
    return image.width===dimensions.width&&image.height===dimensions.height;
  }catch(error){
    if(missing(error)||/PNG|inflate|buffer|bounds/i.test(error.message))return false;
    throw error;
  }
}
async function verifiedGeneration(generation,manifestSha,mp4Sha,manifestFile,output,film,plan){
  let index;
  try{index=JSON.parse(await readFile(join(generation,'index.json'),'utf8'));}
  catch(error){if(missing(error)||error instanceof SyntaxError)return null;throw error;}
  if(!index||Array.isArray(index)||index.schema!==REVIEW_PACK_SCHEMA||
    index.status!=='generated, not reviewed'||index.inputs?.manifest?.sha256!==manifestSha||
    index.inputs?.mp4?.sha256!==mp4Sha||index.inputs.manifest.path!==manifestFile||
    index.inputs.mp4.path!==output||!sameFilm(index.film,film)||
    typeof index.decoder?.ffmpegVersion!=='string'||
    typeof index.decoder?.ffprobeVersion!=='string'||
    !Array.isArray(index.selectedFrames)||!Array.isArray(index.pages))return null;
  const wanted=[...new Set([...overviewIndices(film.count,film.fps),
    ...plan.samples.flatMap(sample=>sample.indices)])].toSorted((a,b)=>a-b);
  if(index.selectedFrames.length!==wanted.length)return null;
  const metadata=new Map();let prior=null;
  for(let i=0;i<wanted.length;i++){
    const entry=index.selectedFrames[i];
    if(!entry||entry.index!==wanted[i]||entry.file!==framePath(entry.index)||
      entry.timeBase!==index.decoder.timeBase)return null;
    let value;
    try{value=ticks(entry.ptsTicks);timeBase(entry.timeBase);}catch{return null;}
    if(prior!==null&&value<=prior)return null;
    prior=value;metadata.set(entry.index,entry);
    if(!await verifiedFile(generation,entry.file,entry.sha256,film))return null;
  }
  let expected;
  try{expected=planReviewPages(plan,metadata).pages;}catch{return null;}
  if(index.pages.length!==expected.length)return null;
  for(let i=0;i<expected.length;i++){
    const page=index.pages[i],layout=expected[i];
    if(!page||page.kind!==layout.kind||page.width!==layout.width||
      page.height!==layout.height||page.file!==`${page.kind}-${String(i).padStart(3,'0')}.png`||
      JSON.stringify(page.cells)!==JSON.stringify(layout.cells)||
      !await verifiedFile(generation,page.file,page.sha256,page))return null;
  }
  return index;
}
const sameFilm=(a,b)=>a&&a.count===b.count&&a.width===b.width&&a.height===b.height&&a.fps===b.fps;

async function decoderMetadata(snapshot,film){
  const parsed=JSON.parse(await command('ffprobe',['-v','error','-select_streams','v:0',
    '-show_streams','-show_frames','-show_entries',
    'stream=time_base,width,height,codec_name:frame=pts,width,height','-of','json',snapshot]));
  const stream=parsed.streams?.[0];
  need(stream&&stream.width===film.width&&stream.height===film.height,
    'Decoded video stream dimensions differ from manifest');
  const frames=(parsed.frames??[]).map((f,index)=>({index,ptsTicks:f.pts,timeBase:stream.time_base,
    width:f.width,height:f.height}));
  validateDecodedFrames(frames,film);
  return {frames,stream};
}

async function extractSelected(snapshot,generation,film,selected){
  const bytesPerFrame=film.width*film.height*3;
  need(Number.isSafeInteger(bytesPerFrame)&&bytesPerFrame>0,'Invalid decoded RGB dimensions');
  const child=spawn('ffmpeg',['-v','error','-i',snapshot,'-map','0:v:0',
    '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],
  {stdio:['ignore','pipe','pipe']});
  const completion=once(child,'close');let stderr='',count=0,offset=0;
  child.stderr.on('data',chunk=>stderr=(stderr+chunk).slice(-16000));
  const buffer=Buffer.alloc(bytesPerFrame),records=[];
  try{
    for await(const chunk of child.stdout){
      let at=0;
      while(at<chunk.length){
        const take=Math.min(bytesPerFrame-offset,chunk.length-at);
        chunk.copy(buffer,offset,at,at+take);at+=take;offset+=take;
        if(offset===bytesPerFrame){
          if(selected.has(count)){
            const file=framePath(count),bytes=encodeRgbPng(film.width,film.height,buffer);
            await writeFile(join(generation,file),bytes);
            records.push({index:count,file,sha256:hash(bytes)});
          }
          count++;offset=0;
        }
      }
    }
    const [code]=await completion;
    need(code===0,`MP4 decode failed: ${stderr}`);
    need(offset===0&&count===film.count,`Decoded frame count differs from manifest: ${count} instead of ${film.count}`);
    need(records.length===selected.size,'Decoded selection is incomplete');
    return records;
  }catch(error){child.kill('SIGTERM');await completion.catch(()=>{});throw error;}
}

async function stillLive(manifestPath,output,manifestSha,mp4Sha){
  need(await fileHash(manifestPath)===manifestSha&&await fileHash(output)===mp4Sha,
    'Review input changed during attempt: manifest or MP4 hash mismatch');
}

export async function reviewManifest(manifestPath,{beforeReuse,beforePublish}={}){
  // A project catalogue may be reached through a directory symlink. Bind
  // provenance and artifact containment to the owning real directory, not
  // the caller's spelling of its manifest path.
  const manifestFile=await realpath(resolve(manifestPath)),owner=dirname(manifestFile);
  const manifestBytes=await readFile(manifestFile),manifestSha=hash(manifestBytes);
  let manifest;
  try{manifest=JSON.parse(manifestBytes);}catch{throw new Error('Review manifest is not valid JSON');}
  const plan=checkPlan(manifest);
  need(typeof manifest.output==='string'&&manifest.output.length>0&&
    typeof manifest.outputSha256==='string'&&/^[a-f0-9]{64}$/.test(manifest.outputSha256),
  'Review manifest has no bound MP4 output hash');
  const output=await realpath(resolve(owner,manifest.output)),mp4Sha=await fileHash(output);
  need(mp4Sha===manifest.outputSha256,'Review MP4 hash differs from manifest output SHA-256');
  const packDirectory=join(owner,'review-packs');await mkdir(packDirectory,{recursive:true});
  const root=await realpath(packDirectory);
  need(inside(owner,root),'Review pack directory escapes the manifest owner');
  let names=await readdir(root);
  for(const name of names.toSorted().reverse()){
    const generation=join(root,name),index=await verifiedGeneration(generation,manifestSha,mp4Sha,
      manifestFile,output,{count:manifest.count,width:manifest.width,height:manifest.height,fps:manifest.fps},plan);
    if(!index)continue;
    if(beforeReuse)await beforeReuse();
    await stillLive(manifestFile,output,manifestSha,mp4Sha);
    return {generation,index,reused:true};
  }
  const generation=join(root,`${manifestSha.slice(0,12)}-${mp4Sha.slice(0,12)}-${randomUUID()}`);
  await mkdir(join(generation,'frames'),{recursive:true});
  const snapshotManifest=join(generation,'manifest.snapshot.json');
  const snapshotMp4=join(generation,'film.snapshot.mp4');
  try{
  await copyFile(manifestFile,snapshotManifest);await copyFile(output,snapshotMp4);
  need(await fileHash(snapshotManifest)===manifestSha&&await fileHash(snapshotMp4)===mp4Sha,
    'Review snapshot differs from initially verified manifest/MP4');
  const film={count:manifest.count,width:manifest.width,height:manifest.height,fps:manifest.fps};
  const {frames,stream}=await decoderMetadata(snapshotMp4,film);
  const metadata=new Map(frames.map(f=>[f.index,f])),layout=planReviewPages(plan,metadata);
  const selected=new Set(layout.pages.flatMap(page=>page.cells.filter(cell=>!cell.padding).map(cell=>cell.index)));
  const records=await extractSelected(snapshotMp4,generation,film,selected);
  const selectedFrames=records.map(record=>({...record,ptsTicks:frames[record.index].ptsTicks,
    timeBase:frames[record.index].timeBase}));
  const pages=[];
  for(const [i,page] of layout.pages.entries()){
    const images=new Map();
    for(const cell of page.cells)if(!cell.padding&&!images.has(cell.index)){
      const decoded=decodePng(await readFile(join(generation,framePath(cell.index))));
      images.set(cell.index,decoded);
    }
    const file=`${page.kind}-${String(i).padStart(3,'0')}.png`,bytes=drawSheet(page,images);
    await writeFile(join(generation,file),bytes);
    pages.push({...page,file,sha256:hash(bytes)});
  }
  const index={schema:REVIEW_PACK_SCHEMA,status:'generated, not reviewed',
    inputs:{manifest:{path:manifestFile,sha256:manifestSha},mp4:{path:output,sha256:mp4Sha}},
    film,decoder:{name:'ffmpeg',codec:stream.codec_name,timeBase:stream.time_base,
      ffmpegVersion:(await command('ffmpeg',['-version'])).split('\n')[0],
      ffprobeVersion:(await command('ffprobe',['-version'])).split('\n')[0]},
    selectedFrames,pages};
  if(beforePublish)await beforePublish();
  for(const entry of [...selectedFrames,...pages])
    need(await verifiedFile(generation,entry.file,entry.sha256,
      entry.width?entry:film),
      `Generated review artifact hash differs: ${entry.file}`);
  // Input snapshots are attempt-only, not another permanent copy of a film.
  // Remove them before the complete index, including on failed attempts.
  await unlink(snapshotManifest);await unlink(snapshotMp4);
  // No long artifact-verification interval remains after the final live
  // attestation. This is still a narrow file-state check, not a lock.
  await stillLive(manifestFile,output,manifestSha,mp4Sha);
  await json(join(generation,'index.json'),index);
  return {generation,index,reused:false};
  }finally{
    for(const path of [snapshotManifest,snapshotMp4])
      await unlink(path).catch(error=>{if(!missing(error))throw error;});
  }
}
