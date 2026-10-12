// One-off, bounded film-production experiment. This is not a Videomaker option.
// Run only under an exclusive browser/resource lease after reviewing the source
// pins and the mirrored render() steps below. All outputs use new ignored roots.
//
// Usage: node experiments/film-production/parallel-benchmark.mjs [OUTPUT_PARENT]
// The default parent is Leonardo's demo-incremental-rendering/_build.
// Never launch this concurrently with another browser render or test.
import {spawn} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import {readFile,writeFile,mkdir,mkdtemp,readdir,copyFile,rename,link,unlink} from 'node:fs/promises';
import {resolve,dirname,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
import {performance} from 'node:perf_hooks';
import {loadEpisode} from '../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {resolveWordTiming,validateWordFramesAtFps} from '../../src/words.mjs';
import {readSpeechTake} from '../../src/speech.mjs';
import {browserSession,render} from '../../src/render.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {pictureReports,clipCadenceForCue} from '../../src/pictures.mjs';
import {SHOT_CACHE_SCHEMA,outputShotUnits,fingerprintShotUnits,shotCacheRoot,
  findShotGeneration,captureShotGeneration,assembleShotFrames} from '../../src/shot-cache.mjs';
import {fileHash,hash,json,command} from '../../src/util.mjs';

const script=fileURLToPath(import.meta.url),sourceDir=resolve(dirname(script),'../../src');
const fixture='/home/asa/devel/machinome/projects/Leonardo/videos/demo-incremental-rendering';
const baseline=resolve(fixture,'episode-baseline.yaml'),variant=resolve(fixture,'episode.yaml');
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
const pins={viewer:'5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413',
  render:'c34f3423c7130f37965f34534b9fb7eac797774e58f3d3a8ba46b4bc52c50312',
  shotCache:'9dbab4bdfbff39bb4e0ff66def627e6c0bcdda09f05f7e68ca199bebf1b991ed',
  baseline:'bd3e4433c76107149238c3179ea4e469d8eb6f0eafb37a26fc8a3163603451e2',
  variant:'f75acd21e85958dd31aa08964553d7e0b1ee65695a5fc9656f555a78be38df8b'};
const order=['whole-machine','feed-pawls','water-drive','return-to-whole'];
const expectedFrames=80,width=960,fps=10,height=540;
const limits={treeRssKiB:4*1024*1024,minAvailableKiB:4*1024*1024,
  processFds:1024,treeFds:4096};
const now=()=>performance.now();
const ms=(start)=>Math.round((now()-start)*1000)/1000;
const pngName=index=>`${String(index).padStart(6,'0')}.png`;
const assert=(condition,message)=>{if(!condition)throw new Error(message);};
const readJson=async path=>JSON.parse(await readFile(path,'utf8'));
const gitHead=async cwd=>(await command('git',['rev-parse','HEAD'],{cwd})).trim();
async function availableMemoryKiB(){
  const info=await readFile('/proc/meminfo','utf8');
  const available=Number(info.match(/^MemAvailable:\s+(\d+) kB/m)?.[1]);
  assert(Number.isFinite(available),'Cannot read MemAvailable before browser launch');
  return available;
}

async function assertPins(){
  for(const [name,path] of [['viewer',viewer],['render',resolve(sourceDir,'render.mjs')],
    ['shotCache',resolve(sourceDir,'shot-cache.mjs')],['baseline',baseline],['variant',variant]]){
    const actual=await fileHash(path);
    assert(actual===pins[name],`Pinned ${name} changed: ${actual}; review the benchmark mirror before running`);
  }
}

async function load(source,build){
  const e=await loadEpisode(source);
  e.paths.build=build;
  await prepareWordTimingForCommand(e,{command:'render',silent:true,fps});
  assert(e.output.width===width&&e.output.height===height&&e.output.fps===fps&&
    e.output.durationSeconds===8&&e.shots.map(s=>s.id).join('|')===order.join('|'),
    'The 80-frame, four-shot benchmark fixture changed');
  assert(e.shots.every(s=>!(s.pictures?.length)), 'This benchmark has no clip extraction or picture media');
  return e;
}

// Deliberate mirror of the private render() common-key expression. The pins
// prevent silent drift; every arm also compares this key to its product seed.
async function fontFaces(e){
  const fontFile=async(name,style='Regular')=>{
    const path=await command('fc-match',['-f','%{file}',`${name}:style=${style}`]).catch(()=>null);
    return path?{path,sha256:await fileHash(path)}:null;
  };
  const family=e.style.fontFamily??'DejaVu Sans';
  return {film:{regular:await fontFile(family),bold:await fontFile(family,'Bold')},
    code:{regular:await fontFile('DejaVu Sans Mono'),bold:await fontFile('DejaVu Sans Mono','Bold')}};
}
async function commonKey(e,info,fonts){
  const sharedHashes=Object.fromEntries(Object.entries(info.hashes).filter(([url])=>!url.startsWith('/pictures/')));
  const key=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,hashes:sharedHashes,browser:info.browser,
    viewerApi:info.viewerApi,width,height:info.height,fps,
    duration:e.output.durationSeconds,format:e.format,style:e.style,series:e.series??e.title,
    initial:frameAt(e,0,[]),fonts,
    renderer:await fileHash(resolve(sourceDir,'render.mjs')),
    timeline:await fileHash(resolve(sourceDir,'timeline.mjs')),
    pictures:await fileHash(resolve(sourceDir,'pictures.mjs')),
    easing:await fileHash(resolve(sourceDir,'easing.mjs')),
    words:await fileHash(resolve(sourceDir,'words.mjs')),
    pixels:await fileHash(resolve(sourceDir,'pixels.mjs')),
    sourceRenderer:await fileHash(resolve(sourceDir,'code.mjs')),
    shotCache:await fileHash(resolve(sourceDir,'shot-cache.mjs')),
    dependencies:await fileHash(resolve(sourceDir,'../package-lock.json'))}));
  return {key,sharedHashes};
}
async function captureProvenance(e,info,sharedHashes,key){
  return {workflowHead:await gitHead(resolve(sourceDir,'..')),projectHead:await gitHead(e.paths.repository),
    episodeSha256:await fileHash(e.paths.episode),productionSha256:await fileHash(e.paths.production),
    viewerSha256:sharedHashes['/viewer.js'],modelSha256:sharedHashes['/model/manifest.json'],
    browser:info.browser,commonKey:key};
}
async function plan(e,info,fonts,seedKey){
  const {key,sharedHashes}=await commonKey(e,info,fonts);
  assert(key===seedKey,'Variant common key differs from product baseline seed');
  assert(info.viewerApi===28&&sharedHashes['/viewer.js']===pins.viewer,
    'The mounted viewer is not the repaired API 28 bundle');
  const {count,units}=outputShotUnits(e,fps,[]);
  assert(count===expectedFrames&&units.every((u,i)=>u.shotId===order[i]&&u.frames.length===20),
    'Frame-unit grid differs from the planned 20/20/20/20 split');
  await fingerprintShotUnits(e,units,key);
  const incoming=units[2].frames.filter(f=>f.request.transition?.outgoing?.shotId==='feed-pawls');
  assert(incoming.length>0,'C does not carry the B outgoing transition request');
  return {key,units,count,provenance:await captureProvenance(e,info,sharedHashes,key)};
}
function shotReport(unit,selected,reused){
  return {shotId:unit.shotId,start:unit.start,end:unit.end,
    indices:unit.frames.map(frame=>frame.index),key:unit.key,
    captured:reused?0:unit.frames.length,reused:reused?unit.frames.length:0,
    generation:selected.generation,origin:selected.index.provenance};
}
async function completeReport(e,info,planned,selections,reused,captured,cacheMs){
  const root=shotCacheRoot(e.paths.build),shotReports=[];
  for(const unit of planned.units){
    const selected=selections.get(unit.shotId);
    assert(selected,`Missing selection for ${unit.shotId}`);
    shotReports.push({...shotReport(unit,selected,reused.has(unit.shotId)),
      indexSha256:await fileHash(resolve(selected.generation,'index.json'))});
  }
  const dir=await assembleShotFrames(root,planned.units,selections,planned.count);
  const identity=hash(JSON.stringify({schema:SHOT_CACHE_SCHEMA,commonKey:planned.key,
    shots:shotReports.map(s=>s.key)}));
  return {identity,dir,count:planned.count,width,height:info.height,browser:info.browser,
    viewerApi:info.viewerApi,hashes:info.hashes,requiredViewerApi:info.requiredViewerApi,
    cache:{schema:SHOT_CACHE_SCHEMA,commonKey:planned.key,capturedFrames:captured,
      reusedFrames:[...reused].length*20,shots:shotReports},cacheMs};
}

async function captureUnit(root,unit,planned,info,page,pose){
  return captureShotGeneration(root,unit,planned.key,width,info.height,async frame=>{
    // Exactly the product policy: no gratuitous fresh flag; frameAt's C
    // request contains the outgoing B state and browserSession composes it.
    await pose(frame.time);
    return page.screenshot();
  },{...planned.provenance,shotKey:unit.key});
}
async function serialCapture(e,fonts,seedKey){
  const launched=now();let cacheDiagnosticMs=0,capturePhaseMs=0;
  const report=await browserSession(e,viewer,width,[],async({page,pose,info})=>{
    const planned=await plan(e,info,fonts,seedKey),root=shotCacheRoot(e.paths.build);
    const selections=new Map(),reused=new Set();let captured=0;
    const started=now();let firstCapture,lastSeal;
    for(const unit of planned.units){
      let selected=await findShotGeneration(root,unit,planned.key,width,info.height);
      if(selected)reused.add(unit.shotId);
      else{
        if(firstCapture===undefined)firstCapture=now();
        selected=await captureUnit(root,unit,planned,info,page,pose);
        lastSeal=now();
        captured+=unit.frames.length;
      }
      selections.set(unit.shotId,selected);
    }
    const result=await completeReport(e,info,planned,selections,reused,captured,0);
    capturePhaseMs=Math.round((lastSeal-firstCapture)*1000)/1000;
    cacheDiagnosticMs=ms(started);result.cacheDiagnosticMs=cacheDiagnosticMs;
    return result;
  });
  return {report,browserMs:ms(launched),cacheDiagnosticMs,capturePhaseMs};
}

async function parallelCapture(e,fonts,seedKey){
  const launched=now(),root=shotCacheRoot(e.paths.build);
  let plannedPromise,firstInfo,cacheStart,firstCapture,lastSeal;
  const captured=new Map();
  const actions=['feed-pawls','water-drive'].map(shotId=>
    browserSession(e,viewer,width,[],async({page,pose,info})=>{
      if(!plannedPromise){firstInfo=info;plannedPromise=plan(e,info,fonts,seedKey);}
      assert(info.browser===firstInfo.browser&&info.viewerApi===firstInfo.viewerApi&&
        JSON.stringify(info.hashes)===JSON.stringify(firstInfo.hashes),
        'The two browser sessions differ in pinned inputs');
      const planned=await plannedPromise;
      const unit=planned.units.find(u=>u.shotId===shotId);
      assert(unit,`Missing ${shotId} unit`);
      if(cacheStart===undefined)cacheStart=now();
      const existing=await findShotGeneration(root,unit,planned.key,width,info.height);
      assert(!existing,`${shotId} unexpectedly reused; not a 40-miss trial`);
      if(firstCapture===undefined)firstCapture=now();
      const selected=await captureUnit(root,unit,planned,info,page,pose);
      lastSeal=now();
      captured.set(shotId,selected);
      return {shotId,frames:unit.frames.length};
    }));
  const sessionReports=await Promise.all(actions);
  assert(sessionReports.length===2&&sessionReports.every(r=>r.framesChecked===20),
    'Parallel sessions did not each pose exactly their assigned 20 frames');
  const planned=await plannedPromise,selections=new Map(captured),reused=new Set();
  for(const shotId of ['whole-machine','return-to-whole']){
    const unit=planned.units.find(u=>u.shotId===shotId);
    const selected=await findShotGeneration(root,unit,planned.key,width,height);
    assert(selected,`${shotId} has no verified baseline generation`);
    selections.set(shotId,selected);reused.add(shotId);
  }
  const report=await completeReport(e,firstInfo,planned,selections,reused,40,0);
  const capturePhaseMs=Math.round((lastSeal-firstCapture)*1000)/1000;
  const cacheDiagnosticMs=ms(cacheStart);report.cacheDiagnosticMs=cacheDiagnosticMs;
  report.framesChecked=sessionReports.reduce((n,r)=>n+r.framesChecked,0);
  return {report,browserMs:ms(launched),cacheDiagnosticMs,capturePhaseMs,
    sessionReports:sessionReports.map(r=>({
    shotId:r.shotId,framesChecked:r.framesChecked,browser:r.browser}))};
}

// Silent 0.4 fixture: mirror render()'s encode/probe/thumbnail/description/
// manifest/publication sequence. The source pin above requires review if its
// private orchestration changes; no product module or author interface changes.
async function encodeAndPublish(e,report,fonts,label='variant'){
  const started=now(),output=resolve(e.paths.build,`${label}.mp4`);
  const publicationId=randomUUID(),pendingOutput=resolve(e.paths.build,`${label}.pending-${publicationId}.mp4`);
  const args=['-y','-v','error','-framerate',String(fps),'-start_number','0','-i',resolve(report.dir,'%06d.png'),
    '-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',
    '-t',String(e.output.durationSeconds),pendingOutput];
  await command('ffmpeg',args);
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',pendingOutput]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  assert(Number(video?.nb_read_frames)===report.count&&video.width===report.width&&
    video.height===report.height,'Encoded video does not match requested frames/dimensions');
  assert(!probe.streams.some(s=>s.codec_type==='audio'),'Silent benchmark unexpectedly has audio');
  if(probe.format)probe.format.filename=output;
  const thumbnail=resolve(e.paths.build,'thumbnail.png'),pendingThumbnail=`${thumbnail}.pending-${publicationId}`;
  await copyFile(resolve(report.dir,pngName(Math.min(report.count-1,
    Math.floor(Math.min(10,e.output.durationSeconds*.5)*fps)))),pendingThumbnail);
  const usedStills=new Set(),usedClips=new Set(),pictureCues=[];
  for(const shot of e.shots)for(const [index,cue] of (shot.pictures??[]).entries()){
    const kind=cue.still!==undefined?'still':'clip',name=cue[kind];
    (kind==='still'?usedStills:usedClips).add(name);
    const record={...pictureReports(e,width).find(r=>r.shotId===shot.id&&r.index===index)};
    if(kind==='clip'){
      const media=e.pictureMedia.clips[name],cadence=clipCadenceForCue(e,shot,cue,media,fps);
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
    const media=e.pictureMedia[kind][name];return `${name}: ${media.credit??`[PICTURE CREDIT PENDING: ${name}]`}`;
  }).join('\n');
  const releaseReady=Boolean(e.release.simulationUrl&&e.release.sourceUrl)&&pictureReleaseIssues.length===0;
  const descriptionOutput=resolve(e.paths.build,'description.md'),pendingDescription=`${descriptionOutput}.pending-${publicationId}`;
  await writeFile(pendingDescription,description
    .replaceAll('{{simulationUrl}}',e.release.simulationUrl??'[PUBLIC SIMULATION URL PENDING]')
    .replaceAll('{{sourceUrl}}',e.release.sourceUrl??'[PUBLIC SOURCE URL PENDING]')
    .replaceAll('{{pictureCredits}}',pictureCredits));
  const workflow=await gitHead(resolve(sourceDir,'..')),project=await gitHead(e.paths.repository);
  const manifestOutput=resolve(e.paths.build,`${label}-manifest.json`),pendingManifest=`${manifestOutput}.pending-${publicationId}`;
  const outputSha256=await fileHash(pendingOutput);
  const manifest={...report,fps,output,outputSha256,audio:[],subtitles:null,episode:e,probe,pictures,
    pictureReleaseIssues,releaseReady,provenance:{workflowHead:workflow,projectHead:project,
      font:fonts.film.regular,codeFont:fonts.code.regular,fontFaces:fonts,
      episodeSha256:await fileHash(e.paths.episode),productionSha256:await fileHash(e.paths.production),
      ffmpeg:(await command('ffmpeg',['-version'])).split('\n')[0]}};
  await writeFile(pendingManifest,JSON.stringify(manifest,null,2)+'\n');
  const previous=`${output}.previous-${publicationId}`;let backedUp=false;
  try{await link(output,previous);backedUp=true;}catch(error){if(error.code!=='ENOENT')throw error;}
  await rename(pendingOutput,output);
  await rename(pendingThumbnail,thumbnail);
  await rename(pendingDescription,descriptionOutput);
  await rename(pendingManifest,manifestOutput);
  if(backedUp)await unlink(previous).catch(error=>console.warn(`Previous-output backup remains: ${error.message}`));
  return {output,outputSha256,probe,encodePublishMs:ms(started)};
}

async function verifyStartingState(e,seedKey){
  const {count,units}=outputShotUnits(e,fps,[]);
  await fingerprintShotUnits(e,units,seedKey);
  const root=shotCacheRoot(e.paths.build),state=[];
  for(const unit of units){
    const selected=await findShotGeneration(root,unit,seedKey,width,height);
    state.push({shotId:unit.shotId,frames:unit.frames.length,hit:Boolean(selected)});
  }
  assert(count===80&&state.map(s=>s.hit).join(',')==='true,false,false,true',
    `Starting state is not 40 hit/40 miss: ${JSON.stringify(state)}`);
  return state;
}

async function worker(mode,build,resultFile){
  if(mode==='smoke'){
    const started=now();
    await pause(400); // enough for several real 100 ms parent /proc samples
    await writeFile(resultFile,JSON.stringify({mode,smoke:true,pid:process.pid,wallMs:ms(started)},null,2)+'\n');
    return;
  }
  await assertPins();
  const started=now(),e=await load(mode==='seed'?baseline:variant,build);
  const preflightMs=ms(started);
  if(mode==='seed'||mode==='cold'){
    const output=await render(e,{viewer,width,fps,audio:null,label:mode==='seed'?'baseline':'variant'});
    const manifest=await readJson(resolve(build,`${mode==='seed'?'baseline':'variant'}-manifest.json`));
    assert(manifest.cache.capturedFrames===80&&manifest.cache.reusedFrames===0,
      `${mode} is not an 80-frame cold production render`);
    await writeFile(resultFile,JSON.stringify({mode,build,output,wallMs:ms(started),preflightMs,
      manifest:resolve(build,`${mode==='seed'?'baseline':'variant'}-manifest.json`)},null,2)+'\n');
    return;
  }
  const seed=await readJson(resolve(build,'baseline-manifest.json'));
  const seedKey=seed.cache.commonKey;
  const startingState=await verifyStartingState(e,seedKey);
  const beforeRenderMs=ms(started);
  if(mode==='product'){
    const productStarted=now();
    const output=await render(e,{viewer,width,fps,audio:null,label:'variant'});
    await writeFile(resultFile,JSON.stringify({mode,build,output,wallMs:ms(started),preflightMs,
      beforeRenderMs,productionRenderMs:ms(productStarted),startingState,
      manifest:resolve(build,'variant-manifest.json')},null,2)+'\n');
    return;
  }
  // Product render() re-reads the measured takes and validates frame fit even
  // when the CLI already prepared the episode. The fixture has no clip media.
  await resolveWordTiming(e,shot=>readSpeechTake(e,shot));
  validateWordFramesAtFps(e,fps);
  const fonts=await fontFaces(e);
  const capture=mode==='serial'?await serialCapture(e,fonts,seedKey)
    :mode==='parallel'?await parallelCapture(e,fonts,seedKey):null;
  assert(capture,`Unknown worker mode ${mode}`);
  const published=await encodeAndPublish(e,capture.report,fonts);
  await writeFile(resultFile,JSON.stringify({mode,build,wallMs:ms(started),preflightMs,beforeRenderMs,
    browserMs:capture.browserMs,capturePhaseMs:capture.capturePhaseMs,
    cacheDiagnosticMs:capture.cacheDiagnosticMs,sessionReports:capture.sessionReports??null,
    startingState,...published,manifest:resolve(build,'variant-manifest.json')},null,2)+'\n');
}

function parseProcStat(stat){
  const end=stat.lastIndexOf(')');
  if(end<0)return null;
  const fields=stat.slice(end+1).trim().split(/\s+/);
  // /proc stat fields after comm begin at field 3: state, PPID, ...,
  // starttime (field 22). Starttime protects against PID reuse during stop.
  if(fields.length<20)return null;
  return {state:fields[0],ppid:Number(fields[1]),pgrp:Number(fields[2]),starttime:fields[19]};
}
const vanished=error=>['ENOENT','ESRCH','EACCES','EPERM'].includes(error?.code);
async function procSnapshot(){
  const entries=await readdir('/proc',{withFileTypes:true});
  const processes=[];
  for(const item of entries){
    if(!item.isDirectory()||!/^\d+$/.test(item.name))continue;
    const pid=Number(item.name);
    try{
      const fields=parseProcStat(await readFile(`/proc/${pid}/stat`,'utf8'));
      if(fields&&Number.isInteger(fields.ppid))processes.push({pid,...fields});
    }catch(error){if(!vanished(error))throw error;}
  }
  return processes;
}
function rememberOwned(processes,rootPid,owned){
  const byPid=new Map(processes.map(p=>[p.pid,p]));
  const root=byPid.get(rootPid),rootKnown=owned.get(rootPid),tree=new Set();
  if(root&&(!rootKnown||root.starttime===rootKnown.starttime))tree.add(rootPid);
  for(const [pid,known] of owned){
    const current=byPid.get(pid);
    if(current?.starttime===known.starttime)tree.add(pid);
  }
  for(let changed=true;changed;){
    changed=false;
    for(const p of processes)if(tree.has(p.ppid)&&!tree.has(p.pid)){tree.add(p.pid);changed=true;}
  }
  for(const p of processes)if(tree.has(p.pid))owned.set(p.pid,{pid:p.pid,ppid:p.ppid,starttime:p.starttime});
  return processes.filter(p=>tree.has(p.pid)&&owned.get(p.pid)?.starttime===p.starttime);
}
const realProcIo={
  stat:pid=>readFile(`/proc/${pid}/stat`,'utf8'),
  status:pid=>readFile(`/proc/${pid}/status`,'utf8'),
  fds:pid=>readdir(`/proc/${pid}/fd`),
  limits:pid=>readFile(`/proc/${pid}/limits`,'utf8')};
async function readOwnedMetrics(processRecord,io=realProcIo){
  const {pid,ppid,starttime,state}=processRecord;
  // A zombie retains its PID/stat identity but no longer has a meaningful FD
  // table or resident browser workload. Do not ask /proc/<pid>/fd for it.
  if(state==='Z')return {knownZombie:{pid,ppid,starttime}};
  try{
    const [status,fds,soft]=await Promise.all([
      io.status(pid),io.fds(pid),io.limits(pid)]);
    const rssKiB=Number(status.match(/^VmRSS:\s+(\d+) kB/m)?.[1]??0);
    const softFd=soft.match(/^Max open files\s+(\S+)/m)?.[1]??null;
    return {row:{pid,ppid,starttime,rssKiB,fds:fds.length,softFd}};
  }catch(error){
    if(!['ENOENT','ESRCH','EACCES','EPERM'].includes(error.code))throw error;
    // Denial alone is never a waiver. The exact PID and starttime must now
    // attest a teardown race; a still-live denied identity remains fatal.
    let current;
    try{current=parseProcStat(await io.stat(pid));}
    catch(statError){
      if(statError.code==='ENOENT'||statError.code==='ESRCH')
        return {teardownRace:{pid,ppid,starttime,metricError:error.code,attested:'gone'}};
      throw error;
    }
    if(!current)throw error;
    if(current.starttime!==starttime)
      return {teardownRace:{pid,ppid,starttime,metricError:error.code,attested:'identity-changed',
        observedStarttime:current.starttime}};
    if(current.state==='Z')
      return {teardownRace:{pid,ppid,starttime,metricError:error.code,attested:'zombie'}};
    throw error;
  }
}
async function procSample(rootPid,owned){
  const processes=await procSnapshot();
  const current=rememberOwned(processes,rootPid,owned);
  const rows=[],teardownRaces=[],knownZombies=[];
  for(const processRecord of current){
    const result=await readOwnedMetrics(processRecord);
    if(result.row)rows.push(result.row);
    if(result.teardownRace)teardownRaces.push(result.teardownRace);
    if(result.knownZombie)knownZombies.push(result.knownZombie);
  }
  const meminfo=await readFile('/proc/meminfo','utf8');
  const availableKiB=Number(meminfo.match(/^MemAvailable:\s+(\d+) kB/m)?.[1]);
  assert(Number.isFinite(availableKiB),'Cannot read MemAvailable');
  return {at:Date.now(),rootPid,processes:rows,teardownRaces,knownZombies,
    treeRssKiB:rows.reduce((n,r)=>n+r.rssKiB,0),
    treeFds:rows.reduce((n,r)=>n+r.fds,0),processFds:Math.max(0,...rows.map(r=>r.fds)),availableKiB};
}
const pause=milliseconds=>new Promise(r=>setTimeout(r,milliseconds));
async function signalOwned(owned,signal){
  const current=await procSnapshot(),byPid=new Map(current.map(p=>[p.pid,p]));
  const ordered=[...owned.values()].filter(p=>p.pid!==process.pid)
    .sort((a,b)=>Number(a.pid===b.ppid)-Number(b.pid===a.ppid));
  const sent=[],errors=[];
  for(const known of ordered){
    // Re-read immediately before signaling; never signal a reused PID.
    let live;
    try{live=parseProcStat(await readFile(`/proc/${known.pid}/stat`,'utf8'));}
    catch(error){if(error.code==='ENOENT'||error.code==='ESRCH')continue;throw error;}
    if(!live||live.state==='Z'||live.starttime!==known.starttime||
      byPid.get(known.pid)?.starttime!==known.starttime)continue;
    try{process.kill(known.pid,signal);sent.push(known.pid);}
    catch(error){if(error.code!=='ESRCH')errors.push({pid:known.pid,error:error.message});}
  }
  return {sent,errors};
}
async function liveOwned(rootPid,owned){
  const current=await procSnapshot();
  rememberOwned(current,rootPid,owned);
  const live=[];
  for(const known of owned.values()){
    let state;
    try{state=parseProcStat(await readFile(`/proc/${known.pid}/stat`,'utf8'));}
    catch(error){if(error.code==='ENOENT'||error.code==='ESRCH')continue;throw error;}
    if(state&&state.starttime===known.starttime&&state.state!=='Z')live.push(known);
  }
  return live;
}
async function terminateOwned(rootPid,owned){
  // No process-group assumption: Chromium may launch its own group. Track
  // only descendants of this worker, with starttime-bound PID identities.
  const result={termSent:[],killSent:[],signalErrors:[],survivors:[],
    termGraceMs:3000,killGraceMs:2000};
  await liveOwned(rootPid,owned);
  const term=await signalOwned(owned,'SIGTERM');
  result.termSent.push(...term.sent);result.signalErrors.push(...term.errors);
  const termUntil=now()+3000;
  while(now()<termUntil){
    await pause(100);
    const live=await liveOwned(rootPid,owned);
    if(!live.length)return result;
    // A child forked during shutdown is still an owned descendant.
    const newly=live.filter(p=>!result.termSent.includes(p.pid));
    if(newly.length){
      const more=await signalOwned(new Map(newly.map(p=>[p.pid,p])),'SIGTERM');
      result.termSent.push(...more.sent);result.signalErrors.push(...more.errors);
    }
  }
  const killed=await signalOwned(owned,'SIGKILL');
  result.killSent.push(...killed.sent);result.signalErrors.push(...killed.errors);
  const killUntil=now()+2000;
  while(now()<killUntil){
    await pause(100);
    const live=await liveOwned(rootPid,owned);
    if(!live.length)return result;
  }
  result.survivors=(await liveOwned(rootPid,owned)).map(({pid,ppid,starttime})=>({pid,ppid,starttime}));
  return result;
}
function resourceBreach(sample){
  if(sample.treeRssKiB>limits.treeRssKiB)return 'aggregate RSS exceeded 4 GiB';
  if(sample.availableKiB<limits.minAvailableKiB)return 'host available memory fell below 4 GiB';
  if(sample.processFds>limits.processFds)return 'one process exceeded 1024 FDs';
  if(sample.treeFds>limits.treeFds)return 'process tree exceeded 4096 FDs';
  return null;
}
async function runWorker(mode,build){
  const availableBeforeKiB=await availableMemoryKiB();
  assert(availableBeforeKiB>=limits.minAvailableKiB,
    `${mode} refused before launch: host available memory below 4 GiB`);
  const resultFile=resolve(build,`worker-${mode}-${randomUUID()}.json`);
  const outerStarted=now();
  const child=spawn(process.execPath,[script,'worker',mode,build,resultFile],
    {detached:true,stdio:['ignore','pipe','pipe']});
  const exitPromise=new Promise((resolveExit,reject)=>{
    child.once('error',reject);
    child.once('exit',(code,signal)=>resolveExit({code,signal}));
  }).then(value=>value,error=>({error}));
  // 'close' is distinct from 'exit': a detached Chromium descendant can hold
  // an inherited pipe open after the worker dies. Never gate orphan cleanup
  // on pipe closure.
  const closePromise=new Promise(resolveClose=>child.once('close',(code,signal)=>
    resolveClose({code,signal})));
  let stdout='',stderr='',sampling=false,stopReason=null,stopDetails=null;
  let terminationPromise,safetyTimer,safetyResolve,lastSampleStart;
  const safetyDeadline=new Promise(resolveDeadline=>{safetyResolve=resolveDeadline;});
  const owned=new Map(),sampleTimes=[],teardownRaces=[],knownZombies=[];
  const peaks={treeRssKiB:0,treeFds:0,processFds:0,minAvailableKiB:Infinity,
    byProcess:{},softFdLimits:{}};
  child.stdout.on('data',chunk=>{stdout+=chunk;});
  child.stderr.on('data',chunk=>{stderr+=chunk;});
  const stop=reason=>{
    if(stopReason)return;
    stopReason=reason;
    safetyTimer=setTimeout(()=>safetyResolve({code:null,signal:'safety-timeout'}),8000);
    terminationPromise=terminateOwned(child.pid,owned).then(details=>{stopDetails=details;},error=>{
      stopDetails={termSent:[],killSent:[],signalErrors:[{error:error.message}],survivors:[]};
      stopReason+=`; owned-process termination failed: ${error.message}`;
    });
  };
  const sampled=async()=>{
    if(sampling||stopReason||child.exitCode!==null||!Number.isInteger(child.pid))return;
    sampling=true;
    try{
      const startAt=Date.now(),started=now();
      const s=await procSample(child.pid,owned);
      teardownRaces.push(...s.teardownRaces.map(r=>({at:startAt,...r})));
      knownZombies.push(...s.knownZombies.map(r=>({at:startAt,...r})));
      sampleTimes.push({at:startAt,gapMs:lastSampleStart===undefined?null:startAt-lastSampleStart,
        durationMs:ms(started)});
      lastSampleStart=startAt;
      peaks.treeRssKiB=Math.max(peaks.treeRssKiB,s.treeRssKiB);
      peaks.treeFds=Math.max(peaks.treeFds,s.treeFds);
      peaks.processFds=Math.max(peaks.processFds,s.processFds);
      peaks.minAvailableKiB=Math.min(peaks.minAvailableKiB,s.availableKiB);
      for(const row of s.processes){
        const prior=peaks.byProcess[row.pid]??{ppid:row.ppid,rssKiB:0,fds:0};
        prior.rssKiB=Math.max(prior.rssKiB,row.rssKiB);
        prior.fds=Math.max(prior.fds,row.fds);
        peaks.byProcess[row.pid]=prior;
        peaks.softFdLimits[row.pid]=row.softFd;
      }
      const breach=resourceBreach(s);
      if(breach)stop(breach);
    }catch(error){
      stop(`Resource sampling failed: ${error.message}`);
    }finally{sampling=false;}
  };
  await sampled();
  const timer=setInterval(sampled,100);
  let exit;
  try{exit=await Promise.race([exitPromise,safetyDeadline]);}
  finally{clearInterval(timer);if(safetyTimer)clearTimeout(safetyTimer);}
  if(terminationPromise)await terminationPromise;
  while(sampling)await new Promise(r=>setTimeout(r,10));
  if(!stopReason&&!exit.error){
    const survivors=await liveOwned(child.pid,owned);
    if(survivors.length){
      stopReason='Worker exited with owned descendants still live';
      stopDetails=await terminateOwned(child.pid,owned);
    }
  }
  let pipeClose=null;
  if(exit.signal==='safety-timeout'){
    child.stdout.destroy();child.stderr.destroy();
    stopReason+='; worker pipe did not close within 8 seconds of safety stop';
  }else{
    let pipeTimer;
    const pipeDeadline=new Promise(resolveDeadline=>{
      pipeTimer=setTimeout(()=>resolveDeadline({timeout:true}),3000);
    });
    try{pipeClose=await Promise.race([closePromise,pipeDeadline]);}
    finally{clearTimeout(pipeTimer);}
    if(pipeClose.timeout){
      child.stdout.destroy();child.stderr.destroy();
      stopReason=stopReason?`${stopReason}; worker pipes stayed open after exit`
        :'Worker pipes stayed open after exit despite owned-descendant cleanup';
    }
  }
  const outerWallMs=ms(outerStarted);
  const gaps=sampleTimes.map(s=>s.gapMs).filter(v=>v!==null);
  const resource={samples:sampleTimes.length,requestedSampleIntervalMs:100,
    actualMaxGapMs:Math.max(0,...gaps),actualMinGapMs:gaps.length?Math.min(...gaps):null,
    maxSampleDurationMs:Math.max(0,...sampleTimes.map(s=>s.durationMs)),sampleTimes,
    teardownRaces,knownZombies,
    availableBeforeKiB,peaks,stopReason,stopDetails,pipeClose,limits,outerWallMs,
    caveat:'100 ms is the requested timer interval; actual gaps and durations above are measured, not guaranteed.'};
  await writeFile(resolve(build,`resource-${mode}.json`),JSON.stringify(resource,null,2)+'\n');
  await writeFile(resolve(build,`worker-${mode}.log`),stdout+stderr);
  assert(!stopDetails?.survivors?.length,
    `${mode} left owned descendant survivors: ${JSON.stringify(stopDetails?.survivors??[])}`);
  assert(!stopReason,`${mode} stopped for resource safety: ${stopReason}`);
  if(exit.error)throw exit.error;
  assert(exit.code===0,`${mode} worker exited ${exit.code??exit.signal}: ${stderr.slice(-2000)}`);
  return {...await readJson(resultFile),resource};
}

async function frameHashes(manifest){
  assert(manifest.count===expectedFrames&&manifest.width===width&&manifest.height===height,
    'Rendered manifest has wrong output grid');
  const hashes=[];
  for(let i=0;i<expectedFrames;i++)hashes.push(await fileHash(resolve(manifest.dir,pngName(i))));
  const video=manifest.probe.streams.find(s=>s.codec_type==='video');
  assert(Number(video?.nb_read_frames)===80&&video.width===960&&video.height===540,
    'Output probe has wrong frame count or dimensions');
  assert(await fileHash(manifest.output)===manifest.outputSha256,'Published MP4 SHA differs from manifest');
  return hashes;
}
async function verifyAgainstCold(result,coldHashes){
  const manifest=await readJson(result.manifest);
  const hashes=await frameHashes(manifest);
  assert(hashes.every((value,i)=>value===coldHashes[i]),
    `PNG mismatch at global frame ${hashes.findIndex((value,i)=>value!==coldHashes[i])}`);
  assert(manifest.cache.capturedFrames===40&&manifest.cache.reusedFrames===40,
    'Variant did not capture B+C and reuse A+D');
  assert(manifest.cache.shots.map(s=>`${s.shotId}:${s.captured}/${s.reused}`).join('|')===
    'whole-machine:0/20|feed-pawls:20/0|water-drive:20/0|return-to-whole:0/20',
    'Cache shot ownership does not match planned workload');
  return {all80PngsEqual:true,frameHashes:hashes,outputSha256:manifest.outputSha256,
    probe:manifest.probe,cache:manifest.cache,manifest:result.manifest};
}

async function coordinator(parent){
  await assertPins();
  assert(await availableMemoryKiB()>=limits.minAvailableKiB,
    'Benchmark refused before launch: host available memory below 4 GiB');
  const ignoredBuild=resolve(fixture,'_build'),rel=relative(ignoredBuild,parent);
  assert(!isAbsolute(rel)&&rel!=='..'&&!rel.startsWith('../'),
    'Benchmark output parent must stay under Leonardo demo-incremental-rendering/_build');
  await mkdir(parent,{recursive:true});
  const root=await mkdtemp(resolve(parent,'parallel-benchmark-'));
  const meminfo=await readFile('/proc/meminfo','utf8');
  const softLimits=await readFile('/proc/self/limits','utf8');
  const report={status:'running',root,pins,limits,startedUtc:new Date().toISOString(),
    workflowHead:await gitHead(resolve(sourceDir,'..')),projectHead:await gitHead(fixture),
    host:{memTotalKiB:Number(meminfo.match(/^MemTotal:\s+(\d+) kB/m)?.[1]),
      availableBeforeKiB:Number(meminfo.match(/^MemAvailable:\s+(\d+) kB/m)?.[1]),
      softFdLimit:softLimits.match(/^Max open files\s+(\S+)/m)?.[1]??null},
    sourceHashes:{render:pins.render,shotCache:pins.shotCache,viewer:pins.viewer,
      baseline:pins.baseline,variant:pins.variant},pairs:[],runs:[]};
  const save=()=>json(resolve(root,'report.json'),report);
  await save();
  try{
    const referenceBuild=resolve(root,'cold-reference');await mkdir(referenceBuild);
    const cold=await runWorker('cold',referenceBuild);
    report.runs.push({kind:'cold-reference',...cold});await save();
    const coldManifest=await readJson(cold.manifest),coldHashes=await frameHashes(coldManifest);
    report.reference={manifest:cold.manifest,frameHashes:coldHashes,
      outputSha256:coldManifest.outputSha256,probe:coldManifest.probe};await save();
    for(let pair=1;pair<=2;pair++){
      const sequence=pair===1?['serial','parallel']:['parallel','serial'];
      const builds={};
      for(const mode of ['serial','parallel']){
        const build=resolve(root,`pair-${pair}-${mode}`);await mkdir(build);builds[mode]=build;
        const seed=await runWorker('seed',build);
        report.runs.push({kind:'seed',pair,mode,...seed});await save();
      }
      const measured={};
      for(const mode of sequence){
        const result=await runWorker(mode,builds[mode]);
        const verified=await verifyAgainstCold(result,coldHashes);
        measured[mode]={...result,verified};
        report.runs.push({kind:'primary',pair,mode,...measured[mode]});await save();
      }
      report.pairs.push({pair,sequence,serialWorkerMs:measured.serial.wallMs,
        parallelWorkerMs:measured.parallel.wallMs,
        serialProcessMs:measured.serial.resource.outerWallMs,
        parallelProcessMs:measured.parallel.resource.outerWallMs,
        endToEndSavingMs:measured.serial.resource.outerWallMs-measured.parallel.resource.outerWallMs,
        serialCapturePhaseMs:measured.serial.capturePhaseMs,
        parallelCapturePhaseMs:measured.parallel.capturePhaseMs,
        note:'Capture phase is first captureShotGeneration start to last index seal; cacheDiagnosticMs has mode-specific verification/browser-close boundaries and is not compared.'});
      await save();
    }
    // Authoritative product-path comparator on the identical 40-miss state.
    // Its productionRenderMs excludes the explicit benchmark precheck, while
    // wallMs includes load/preflight/check, matching the custom-arm accounting.
    const comparatorBuild=resolve(root,'production-serial-comparator');await mkdir(comparatorBuild);
    const seed=await runWorker('seed',comparatorBuild);
    report.runs.push({kind:'seed',mode:'product',...seed});await save();
    const comparator=await runWorker('product',comparatorBuild);
    const verified=await verifyAgainstCold(comparator,coldHashes);
    report.comparator={...comparator,verified,
      customSerialWallMs:report.runs.find(r=>r.kind==='primary'&&r.pair===2&&r.mode==='serial').wallMs,
      limitation:'Compare product render() wall and custom serial before attributing any end-to-end gain; this harness mirrors private output steps.'};
    report.comparator.customMinusProductMs=report.comparator.customSerialWallMs-comparator.wallMs;
    report.comparator.customMinusProductProcessMs=
      report.runs.find(r=>r.kind==='primary'&&r.pair===2&&r.mode==='serial').resource.outerWallMs-
      comparator.resource.outerWallMs;
    report.pairedSavingSpreadMs=Math.abs(report.pairs[0].endToEndSavingMs-report.pairs[1].endToEndSavingMs);
    report.status='complete';report.finishedUtc=new Date().toISOString();await save();
    console.log(`Benchmark complete: ${resolve(root,'report.json')}`);
  }catch(error){
    report.status='failed';report.error=String(error.stack??error);
    report.finishedUtc=new Date().toISOString();await save();
    throw error;
  }
}

// Narrow process-safety rehearsal. The grandchild is deliberately detached
// and ignores TERM; an unrelated sentinel must remain untouched. No browser,
// model, renderer, or ffmpeg is started by this mode.
async function safetySelfTest(){
  const parent=resolve(fixture,'_build');await mkdir(parent,{recursive:true});
  const dir=await mkdtemp(resolve(parent,'parallel-benchmark-safety-'));
  const readyFile=resolve(dir,'detached-child-ready');
  const owned=new Map();let root,unrelated,unrelatedIdentity,record={status:'running',dir};
  const save=()=>json(resolve(dir,'report.json'),record);
  await save();
  try{
    root=spawn(process.execPath,[script,'dummy-root',readyFile],{detached:true,stdio:'ignore'});
    unrelated=spawn(process.execPath,[script,'dummy-sentinel'],{detached:true,stdio:'ignore'});
    assert(Number.isInteger(root.pid)&&Number.isInteger(unrelated.pid),'Dummy processes did not start');
    let child;
    const until=now()+5000;
    while(now()<until){
      await procSample(root.pid,owned);
      child=[...owned.values()].find(p=>p.ppid===root.pid&&p.pid!==root.pid);
      let ready=null;
      try{ready=(await readFile(readyFile,'utf8')).trim();}
      catch(error){if(error.code!=='ENOENT')throw error;}
      if(child&&ready===String(child.pid))break;
      await pause(100);
    }
    assert(child&&(await readFile(readyFile,'utf8')).trim()===String(child.pid),
      'Detached dummy descendant was not observed ready by PID/PPID');
    const rootState=parseProcStat(await readFile(`/proc/${root.pid}/stat`,'utf8'));
    const childState=parseProcStat(await readFile(`/proc/${child.pid}/stat`,'utf8'));
    const unrelatedState=parseProcStat(await readFile(`/proc/${unrelated.pid}/stat`,'utf8'));
    unrelatedIdentity=unrelatedState.starttime;
    assert(rootState.pgrp!==childState.pgrp,'Dummy child did not detach its process group');
    const termination=await terminateOwned(root.pid,owned);
    const survivors=await liveOwned(root.pid,owned);
    const unrelatedAfter=parseProcStat(await readFile(`/proc/${unrelated.pid}/stat`,'utf8'));
    record={status:'complete',dir,rootPid:root.pid,detachedChildPid:child.pid,
      rootPgrp:rootState.pgrp,detachedChildPgrp:childState.pgrp,
      unrelatedPid:unrelated.pid,termination,survivors,
      unrelatedUntouched:unrelatedAfter.starttime===unrelatedState.starttime&&unrelatedAfter.state!=='Z',
      killedDetachedChild:termination.killSent.includes(child.pid)};
    await save();
    assert(!survivors.length&&!termination.survivors.length,
      'Safety rehearsal left an owned dummy descendant alive');
    assert(record.killedDetachedChild,'KILL did not reach the TERM-ignoring detached child');
    assert(record.unrelatedUntouched,'Safety stop affected the unrelated sentinel');
    console.log(`Safety rehearsal: ${resolve(dir,'report.json')}`);
  }catch(error){
    record.status='failed';record.error=String(error.stack??error);await save();throw error;
  }finally{
    // Cleanup remains identity-scoped even when a test assertion fails.
    await signalOwned(owned,'SIGKILL').catch(()=>{});
    if(unrelated?.pid&&unrelatedIdentity){
      let current;
      try{current=parseProcStat(await readFile(`/proc/${unrelated.pid}/stat`,'utf8'));}
      catch(error){if(error.code!=='ENOENT'&&error.code!=='ESRCH')throw error;}
      if(current?.starttime===unrelatedIdentity){
        try{process.kill(unrelated.pid,'SIGTERM');}catch(error){if(error.code!=='ESRCH')throw error;}
      }
    }
  }
}

async function monitorRaceSelfTest(){
  const parent=resolve(fixture,'_build');await mkdir(parent,{recursive:true});
  const dir=await mkdtemp(resolve(parent,'parallel-benchmark-monitor-'));
  const record={status:'running',dir,cases:[]};
  const save=()=>json(resolve(dir,'report.json'),record);
  await save();
  const processRecord={pid:12345,ppid:123,starttime:'111',state:'S'};
  const denied=code=>Object.assign(new Error(`mock ${code}`),{code});
  const stat=(state,starttime)=>
    `12345 (dummy) ${state} 123 123 ${Array(16).fill('0').join(' ')} ${starttime}\n`;
  const io=(metricError,statRead)=>({
    status:async()=>{if(metricError.at==='status')throw denied(metricError.code);return 'VmRSS: 10 kB\n';},
    fds:async()=>{if(metricError.at==='fds')throw denied(metricError.code);return ['0','1'];},
    limits:async()=> 'Max open files            65535                65535                files\n',
    stat:statRead});
  try{
    const knownZombie=await readOwnedMetrics({...processRecord,state:'Z'},new Proxy({},
      {get:()=>{throw new Error('Known zombie touched /proc metrics');}}));
    assert(knownZombie.knownZombie?.pid===12345,'Known zombie was not skipped before metric reads');
    record.cases.push({name:'known-zombie',result:'skipped without metric reads'});
    const gone=await readOwnedMetrics(processRecord,io({at:'fds',code:'EACCES'},
      async()=>{throw denied('ENOENT');}));
    assert(gone.teardownRace?.attested==='gone','Gone identity did not attest teardown race');
    record.cases.push({name:'fd-EACCES-then-gone',result:gone.teardownRace});
    const zombie=await readOwnedMetrics(processRecord,io({at:'fds',code:'EPERM'},
      async()=>stat('Z','111')));
    assert(zombie.teardownRace?.attested==='zombie','Zombie identity did not attest teardown race');
    record.cases.push({name:'fd-EPERM-then-zombie',result:zombie.teardownRace});
    const changed=await readOwnedMetrics(processRecord,io({at:'status',code:'EACCES'},
      async()=>stat('S','222')));
    assert(changed.teardownRace?.attested==='identity-changed',
      'Reused PID did not attest identity change');
    record.cases.push({name:'status-EACCES-then-reused-PID',result:changed.teardownRace});
    for(const [name,statRead] of [['same-live-identity',async()=>stat('S','111')],
      ['unreadable-attestation',async()=>{throw denied('EACCES');}]]){
      let failedCode=null;
      try{await readOwnedMetrics(processRecord,io({at:'fds',code:'EACCES'},statRead));}
      catch(error){failedCode=error.code;}
      assert(failedCode==='EACCES',`${name} incorrectly waived live FD denial`);
      record.cases.push({name,result:'refused EACCES'});
    }
    record.status='complete';await save();
    console.log(`Monitor race rehearsal: ${resolve(dir,'report.json')}`);
  }catch(error){record.status='failed';record.error=String(error.stack??error);await save();throw error;}
}

async function workerSmokeTest(){
  const parent=resolve(fixture,'_build');await mkdir(parent,{recursive:true});
  const dir=await mkdtemp(resolve(parent,'parallel-benchmark-smoke-'));
  const report={status:'running',dir};
  const save=()=>json(resolve(dir,'report.json'),report);
  await save();
  try{
    const result=await runWorker('smoke',dir);
    assert(result.smoke===true&&Number.isInteger(result.pid),'Smoke worker result was not returned');
    assert(result.resource.samples>=2,'Successful worker did not receive repeated resource samples');
    assert(result.resource.stopReason===null&&result.resource.stopDetails===null,
      'Successful worker took the resource-stop path');
    assert(result.resource.pipeClose?.code===0&&result.resource.pipeClose?.signal===null,
      'Successful worker did not exit and close its pipes cleanly');
    assert(result.resource.peaks.byProcess[result.pid],
      'Real worker PID was not tracked in the sampled process tree');
    report.status='complete';report.result=result;await save();
    console.log(`Worker smoke rehearsal: ${resolve(dir,'report.json')}`);
  }catch(error){report.status='failed';report.error=String(error.stack??error);await save();throw error;}
}

try{
  if(process.argv[2]==='dummy-child'){
    process.on('SIGTERM',()=>{});
    await writeFile(process.argv[3],String(process.pid)+'\n');
    setInterval(()=>{},1000);
  }else if(process.argv[2]==='dummy-root'){
    spawn(process.execPath,[script,'dummy-child',process.argv[3]],{detached:true,stdio:'ignore'}).unref();
    setInterval(()=>{},1000);
  }else if(process.argv[2]==='dummy-sentinel'){
    setInterval(()=>{},1000);
  }else if(process.argv[2]==='safety-self-test'){
    await safetySelfTest();
  }else if(process.argv[2]==='monitor-race-self-test'){
    await monitorRaceSelfTest();
  }else if(process.argv[2]==='worker-smoke-self-test'){
    await workerSmokeTest();
  }else if(process.argv[2]==='worker'){
    const [mode,build,resultFile]=process.argv.slice(3);
    assert(['seed','cold','serial','parallel','product','smoke'].includes(mode)&&build&&resultFile,
      'Invalid internal benchmark worker invocation');
    await worker(mode,build,resultFile);
  }else{
    assert(process.argv.length<=3,'Usage: node parallel-benchmark.mjs [OUTPUT_PARENT]');
    const parent=resolve(process.argv[2]??resolve(fixture,'_build'));
    await coordinator(parent);
  }
}catch(error){console.error(error.stack??error);process.exitCode=1;}
