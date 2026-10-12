// PREPARATION ONLY: do not run until root pins the frozen runtime and grants
// the sole browser/render lease. Real Leonardo MP4 review-pack evidence.
// This never edits an authored episode, mechanical source/export, or old film.
// Run under a root-owned outer process deadline: render() itself invokes the
// product's browser/encoder children. This script bounds every child it spawns.
import {createHash,randomUUID} from 'node:crypto';
import {spawn} from 'node:child_process';
import {constants as fsConstants} from 'node:fs';
import {copyFile,mkdir,readFile,readdir,realpath,writeFile} from 'node:fs/promises';
import {basename,dirname,join,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual} from 'node:util';

const tool=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const project='/mnt/data/machinome-projects/Leonardo';
const catalogueAlias='/home/asa/devel/machinome/projects/Leonardo';
const fixture=join(project,'videos/demo-source-only');
const episode=join(fixture,'episode.yaml');
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
const priorReport=join(fixture,'_build/evidence/source-only-2026-09-29T18-49-57-465Z-38eb6fbe-072f-443f-bf3e-27a4fe8411f0/report.json');
const priorFilm=join(project,'videos/demo-all-features/_build/rehearsal.mp4');
const take='source-72b6eea39321423a.wav';
const expected={
  projectHead:'28b43bce1b88446995f0ff231dd9075d1a839ab3',
  episode:'37989962da303a91b72c0ae9590edb2964ea87762b37bdd3235d6181ccf28766',
  production:'fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3',
  description:'a0a5e535d86d7f919d96308afff20f95368d859667b640bd00a756f10ee0f2ea',
  modelSource:'947ef0fc2540531f602beffdf48ea7b2ffb356378c4aefbd7f52a058e85300ea',
  exportManifest:'92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9',
  exportTree:'6ba645c99936216c84994379e7e1f3d39144197c640b7b838e9849e848628682',
  exportFiles:120,
  viewer:'5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413',
  take:'fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8',
  alignment:'ee78ced064e170a82118254c7a94588a0afe68af43f3cd890ed76b52c5ac7ea3',
  priorReport:'d7ec36ca2c25bc8b9e79b35c5cd1d3eba6d92ccf77d068c8f9068bb04372cf8a',
  priorFilm:'c9b73b4a06893b3040be0c219109a4a44237d98bbd7fd9633f35e391699ae34e',
  acceptedSourceOnlyFilm:'7e2585c3a4d5dcda9014f7bb1fdfee8fe787c64b244319c885fe795cf7dddd7d',
  // All runtime pins are supplied only after root freezes and reviews the
  // implementation. A pending value refuses before output or browser work.
  runtimeHead:'9dbdded50d701d6e73e8ed636beddabcf1d49846',
  runtimeSrcTree:'217b6099c2d9ae3091d577db6809c74caaffdd07d2b80f93cee10accc0e7a527',
  runtimeBin:'18513454760f8ce4f5b42a399b7cae5a1d133f12cd1f16676d224f60fa69aaa1',
  runtimeLockfile:'c83093ba053bf5e92d480b4e3c947fb83e3a9c54904f88a81a21a7c22da59d15',
};
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const fileSha=async path=>sha(await readFile(path));
const need=(condition,message)=>{if(!condition)throw new Error(message);};
const equal=(actual,want,label)=>need(actual===want,`${label}: ${actual} != ${want}`);
const save=async(path,record)=>writeFile(path,JSON.stringify(record,null,2)+'\n');
const same=(a,b)=>isDeepStrictEqual(a,b);
async function treeSha(root){
  const files=[];
  async function walk(at){for(const entry of await readdir(at,{withFileTypes:true})){
    const path=join(at,entry.name);
    if(entry.isDirectory())await walk(path);
    else if(entry.isFile())files.push(relative(root,path).split(sep).join('/'));
    else throw new Error(`Unexpected pinned tree entry: ${path}`);
  }}
  await walk(root);files.sort();
  const hash=createHash('sha256');
  for(const name of files){hash.update(name);hash.update('\0');hash.update(await readFile(join(root,name)));hash.update('\0');}
  return {files:files.length,sha256:hash.digest('hex')};
}
async function command(exe,args,cwd=tool){
  return new Promise((done,fail)=>{
    const child=spawn(exe,args,{cwd,env:process.env}),out=[],err=[];
    let hardStop,timedOut=false;
    const deadline=setTimeout(()=>{
      timedOut=true;
      child.kill('SIGTERM');
      hardStop=setTimeout(()=>child.kill('SIGKILL'),5000);
    },120000);
    child.stdout.on('data',bytes=>out.push(bytes));child.stderr.on('data',bytes=>err.push(bytes));
    child.on('error',error=>{clearTimeout(deadline);clearTimeout(hardStop);fail(error);});
    child.on('close',code=>{clearTimeout(deadline);clearTimeout(hardStop);
      done({code,timedOut,stdout:Buffer.concat(out),stderr:Buffer.concat(err).toString()});});
  });
}
async function checked(exe,args,cwd){
  const result=await command(exe,args,cwd);
  need(result.code===0&&!result.timedOut,
    `${exe} ${result.timedOut?'timed out':'failed'} (${result.code}): ${result.stderr.slice(0,1200)}`);
  return result.stdout;
}
async function verifyFile(path,want,label){equal(await fileSha(path),want,label);}
const inputFiles=[
  [episode,expected.episode,'source-only episode'],
  [join(fixture,'production.yaml'),expected.production,'production'],
  [join(fixture,'description.md'),expected.description,'description'],
  [join(project,'models/hydraulic_sawmill/model.py'),expected.modelSource,'mechanical source'],
  [join(project,'export/hydraulic_sawmill/manifest.json'),expected.exportManifest,'export manifest'],
  [join(fixture,'_build/audio',take),expected.take,'cached source take'],
  [join(fixture,'_build/audio',take+'.json'),expected.alignment,'cached alignment'],
  [viewer,expected.viewer,'viewer bundle'],
  [priorReport,expected.priorReport,'prior source-only proof'],
  [priorFilm,expected.priorFilm,'original 46-second film'],
];
const runtimeFiles=[
  [join(tool,'bin/videomaker.mjs'),expected.runtimeBin,'CLI'],
  [join(tool,'package-lock.json'),expected.runtimeLockfile,'lockfile'],
];
async function verifyInputs(){
  equal((await checked('git',['rev-parse','HEAD'],project)).toString().trim(),expected.projectHead,'Leonardo HEAD');
  equal((await checked('git',['rev-parse','HEAD'],tool)).toString().trim(),expected.runtimeHead,'Videomaker HEAD');
  for(const [path,want,label] of [...inputFiles,...runtimeFiles])await verifyFile(path,want,label);
  const previous=JSON.parse(await readFile(priorReport,'utf8')),
    priorFilms=Object.values(previous.runs??{}).map(run=>({path:run.output,sha256:run.mp4Sha256}));
  need(priorFilms.length===4&&priorFilms.every(film=>
    film.path.startsWith(dirname(priorReport)+sep)&&/^[a-f0-9]{64}$/.test(film.sha256)),
  'Prior source-only proof does not name four bounded old films');
  for(const film of priorFilms)await verifyFile(film.path,film.sha256,`prior source-only film ${basename(film.path)}`);
  const tree=await treeSha(join(project,'export/hydraulic_sawmill'));
  equal(tree.files,expected.exportFiles,'export file count');equal(tree.sha256,expected.exportTree,'export tree');
  const source=await treeSha(join(tool,'src'));
  equal(source.sha256,expected.runtimeSrcTree,'reviewed runtime source tree');
  return {exportTree:tree,runtimeSourceTree:source,priorFilms};
}

for(const key of ['runtimeHead','runtimeSrcTree','runtimeBin','runtimeLockfile'])
  need(new RegExp(key==='runtimeHead'?'^[0-9a-f]{40}$':'^[0-9a-f]{64}$').test(expected[key]),
    `Root-reviewed ${key} pin is pending; no output created`);
const preflight=await verifyInputs();
const parent=join(fixture,'_build/evidence');await mkdir(parent,{recursive:true});
const root=join(parent,`review-pack-${new Date().toISOString().replace(/[:.]/g,'-')}-${randomUUID()}`);
await mkdir(root); // EEXIST is fatal; no old build, film or pack is reused.
const reportPath=join(root,'report.json');
const report={schema:'leonardo-review-pack-evidence/1',status:'running',stage:'preflight',
  startedUtc:new Date().toISOString(),root,tool,project,fixture,viewer,pins:expected,preflight,
  builds:{},runs:{},comparisons:{},standalone:null,alias:null,preservation:{},review:null};
await save(reportPath,report);

let loadEpisode,prepareWordTimingForCommand,render;
try{
  const [episodeModule,timingModule,renderModule]=await Promise.all([
    import('../../src/episode.mjs'),import('../../src/command-timing.mjs'),import('../../src/render.mjs')]);
  ({loadEpisode}=episodeModule);({prepareWordTimingForCommand}=timingModule);({render}=renderModule);
}catch(error){report.status='failed';report.stage='runtime-import';report.error={message:error.message,stack:error.stack};
  report.finishedUtc=new Date().toISOString();await save(reportPath,report);throw error;}

async function build(name){
  const path=join(root,name);await mkdir(path);await mkdir(join(path,'audio'));
  for(const suffix of [take,take+'.json']){
    const from=join(fixture,'_build/audio',suffix),to=join(path,'audio',suffix);
    await copyFile(from,to,fsConstants.COPYFILE_EXCL);
    await verifyFile(to,suffix===take?expected.take:expected.alignment,`copied ${suffix}`);
  }
  report.builds[name]=path;await save(reportPath,report);return path;
}
async function readJson(path){return JSON.parse(await readFile(path,'utf8'));}
async function findPack(buildPath,manifestPath,mp4Sha){
  const manifestSha=await fileSha(manifestPath),packs=[];
  for(const name of await readdir(join(buildPath,'review-packs'))){
    const generation=join(buildPath,'review-packs',name),path=join(generation,'index.json');
    let index;
    try{index=await readJson(path);}catch(error){if(error.code==='ENOENT')continue;throw error;}
    if(index.inputs?.manifest?.sha256===manifestSha&&index.inputs?.mp4?.sha256===mp4Sha)
      packs.push({generation,indexPath:path,index});
  }
  need(packs.length===1,`Expected exactly one complete automatic pack for ${manifestPath}; found ${packs.length}`);
  return packs[0];
}
async function runRender(name,buildPath,wantCaptured,wantReused){
  report.stage=name;await save(reportPath,report);
  const e=await loadEpisode(episode);e.paths.build=buildPath;
  await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:10});
  const started=process.hrtime.bigint();
  const output=await render(e,{viewer,width:960,fps:10,audio:null,label:name});
  const wallMs=Number(process.hrtime.bigint()-started)/1e6;
  const manifestPath=join(buildPath,`${name}-manifest.json`),manifest=await readJson(manifestPath);
  equal(manifest.output,output,`${name} manifest output`);
  equal(await fileSha(output),manifest.outputSha256,`${name} manifest/MP4 binding`);
  need(manifest.cache?.capturedFrames===wantCaptured&&manifest.cache?.reusedFrames===wantReused,
    `${name} cache count differs: ${manifest.cache?.capturedFrames}/${manifest.cache?.reusedFrames}`);
  need(manifest.reviewSamples?.schema==='review-samples-v1'&&manifest.reviewSamples.frameCount===70&&
    manifest.reviewSamples.fps===10,`${name} has no correct recorded review plan`);
  equal(manifest.provenance?.episodeSha256,expected.episode,`${name} episode provenance`);
  equal(manifest.provenance?.productionSha256,expected.production,`${name} production provenance`);
  equal(manifest.hashes?.['/viewer.js'],expected.viewer,`${name} viewer provenance`);
  const pack=await findPack(buildPath,manifestPath,manifest.outputSha256);
  const run={name,wallMs,output,mp4Sha256:manifest.outputSha256,manifestPath,
    manifestSha256:await fileSha(manifestPath),reviewSamples:manifest.reviewSamples,
    cache:manifest.cache,pack:{generation:pack.generation,indexPath:pack.indexPath,
      indexSha256:await fileSha(pack.indexPath)}};
  report.runs[name]=run;await save(reportPath,report);return {...run,index:pack.index};
}

// The independent decoder is ffprobe/ffmpeg against the published MP4. It
// does not use Videomaker's PNG decoder, page planner, sheet renderer or cache.
async function independentMetadata(mp4){
  const raw=await checked('ffprobe',['-v','error','-select_streams','v:0','-show_streams',
    '-show_frames','-show_entries','stream=time_base,width,height,codec_name:frame=pts,width,height',
    '-of','json',mp4]);
  const parsed=JSON.parse(raw.toString()),stream=parsed.streams?.[0];
  need(stream?.codec_name==='h264'&&stream.width===960&&stream.height===540,
    'Independent MP4 stream codec/dimensions differ');
  const frames=(parsed.frames??[]).map((frame,index)=>({index,ptsTicks:String(frame.pts),
    timeBase:stream.time_base,width:frame.width,height:frame.height}));
  need(frames.length===70,'Independent decoded metadata is not 70 frames');
  let prior=null;
  for(const frame of frames){
    need(frame.width===960&&frame.height===540&&/^-?[0-9]+$/.test(frame.ptsTicks),
      `Independent decoded metadata invalid at ${frame.index}`);
    const pts=BigInt(frame.ptsTicks);need(prior===null||pts>prior,`PTS did not increase at ${frame.index}`);prior=pts;
  }
  return {stream,frames};
}
async function rawRgb(path,width,height){
  const raw=await checked('ffmpeg',['-v','error','-i',path,'-frames:v','1','-f','rawvideo',
    '-pix_fmt','rgb24','pipe:1']);
  need(raw.length===width*height*3,`Independent PNG RGB size differs: ${path}`);return raw;
}
async function decodeFullMp4(mp4,selected){
  const bytesPerFrame=960*540*3,child=spawn('ffmpeg',['-v','error','-i',mp4,'-map','0:v:0',
    '-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','pipe:1'],
  {cwd:tool,stdio:['ignore','pipe','pipe']});
  let stderr='',count=0,offset=0;const buffer=Buffer.alloc(bytesPerFrame),images=new Map();
  child.stderr.on('data',chunk=>stderr=(stderr+chunk).slice(-12000));
  let hardStop,timedOut=false;
  const deadline=setTimeout(()=>{timedOut=true;child.kill('SIGTERM');
    hardStop=setTimeout(()=>child.kill('SIGKILL'),5000);},120000);
  const completion=new Promise((done,fail)=>{child.on('error',error=>{
    clearTimeout(deadline);clearTimeout(hardStop);fail(error);
  });child.on('close',code=>{
    clearTimeout(deadline);clearTimeout(hardStop);done(code);});});
  try{
    for await(const chunk of child.stdout){
      let at=0;while(at<chunk.length){
        const take=Math.min(bytesPerFrame-offset,chunk.length-at);
        chunk.copy(buffer,offset,at,at+take);offset+=take;at+=take;
        if(offset===bytesPerFrame){if(selected.has(count))images.set(count,Buffer.from(buffer));count++;offset=0;}
      }
    }
    const code=await completion;
    need(code===0&&!timedOut,`Independent MP4 decode ${timedOut?'timed out':'failed'}: ${stderr}`);
    need(offset===0&&count===70&&images.size===selected.size,
      `Independent MP4 decode count/selection differs: ${count}/${images.size}`);
    return images;
  }catch(error){child.kill('SIGTERM');await completion.catch(()=>{});throw error;}
}
function expectedPrintedLabel(cell,frame){
  const labels=cell.labels,kind=labels.length>1?'MULTI':labels[0]?.kind?.toUpperCase()??'OVERVIEW';
  const shot=labels[0]?.shotId?.slice(0,10).toUpperCase()??'';
  return `${`F${cell.index} PTS:${frame.ptsTicks} X${frame.timeBase}`} | `+
    `${`${kind} ${shot}`.slice(0,39)}`;
}
function compareCellThumbnail(sheet,source,rect){
  const pageWidth=1920,maxW=480,maxH=276,sourceW=960,sourceH=540;
  const scale=Math.min(maxW/sourceW,maxH/sourceH),drawW=Math.floor(sourceW*scale),
    drawH=Math.floor(sourceH*scale),left=rect.x+Math.floor((480-drawW)/2),
    top=rect.y+Math.floor((maxH-drawH)/2);
  let mismatches=0,first=null;
  for(let y=0;y<drawH;y++)for(let x=0;x<drawW;x++){
    const sx=Math.min(sourceW-1,Math.floor(x/scale)),sy=Math.min(sourceH-1,Math.floor(y/scale));
    const from=(sy*sourceW+sx)*3,to=((top+y)*pageWidth+left+x)*3;
    if(sheet[to]!==source[from]||sheet[to+1]!==source[from+1]||sheet[to+2]!==source[from+2]){
      mismatches++;if(!first)first={x,y,actual:[...sheet.subarray(to,to+3)],expected:[...source.subarray(from,from+3)]};
    }
  }
  return {pixels:drawW*drawH,mismatches,first};
}
function comparePadding(sheet,rect){
  let mismatches=0;
  for(let y=0;y<276;y++)for(let x=0;x<480;x++){
    const at=((rect.y+y)*1920+rect.x+x)*3;
    if(sheet[at]!==244||sheet[at+1]!==244||sheet[at+2]!==244)mismatches++;
  }
  return mismatches;
}
// These expected indices and cue values come from the preserved measured
// Leonardo take and authored 7 s/10 fps grid, not from the generated plan.
function assertLeonardoEvents(plan,name){
  const at=indices=>plan.samples.find(sample=>sample.indices.join(',')===indices.join(','))?.labels??[];
  const requireLabel=(indices,kind,shotId,check=()=>true)=>
    need(at(indices).some(label=>label.kind===kind&&label.shotId===shotId&&check(label)),
      `${name} lacks independent ${kind} ${shotId} at ${indices.join('/')}`);
  for(const [pair,shot] of [[[11,12],'source'],[[46,47],'continuation'],[[56,57],'whole-return']])
    requireLabel(pair,'join',shot);
  requireLabel([13,14],'picture-entry','source',l=>l.authoredIndex===0&&l.shown===1&&l.side==='incoming');
  for(const [pair,ordinal] of [[[14,15],1],[[20,21],2],[[25,26],3],[[26,27],4]])
    requireLabel(pair,'word-onset','source',l=>l.authoredIndex===0&&l.wordOrdinal===ordinal);
  requireLabel([14,15],'source-emphasis-onset','source',l=>l.authoredIndex===0&&
    l.wordOrdinal===0&&l.word==='waterwheel'&&l.line===415&&l.start===12&&l.end===22);
  requireLabel([26,27],'source-emphasis-onset','source',l=>l.authoredIndex===0&&
    l.wordOrdinal===1&&l.word==='crankshaft'&&l.line===415&&l.start===47&&l.end===57);
  requireLabel([40,41],'source-emphasis-clear','source',l=>l.authoredIndex===0&&
    same(l.words?.map(w=>[w.wordOrdinal,w.word,w.line,w.start,w.end]),
      [[0,'waterwheel',415,12,22],[1,'crankshaft',415,47,57]]));
  requireLabel([48,49],'picture-entry','continuation',l=>l.authoredIndex===0&&
    l.shown===1&&l.side==='incoming');
  requireLabel([49,50],'word-onset','continuation',l=>l.authoredIndex===0&&l.wordOrdinal===1);
  requireLabel([51,52],'word-onset','continuation',l=>l.authoredIndex===0&&l.wordOrdinal===2);
  for(const [pair,shot] of [[[10,11],'whole-machine'],[[45,46],'source'],
    [[55,56],'continuation'],[[68,69],'whole-return']])requireLabel(pair,'shot-end',shot);
  requireLabel([68,69],'film-end','whole-return');
  for(const [index,shot] of [[13,'source'],[48,'continuation']])
    requireLabel([index],'transition-midpoint',shot);
  for(const [index,shot] of [[15,'source'],[50,'continuation']])
    requireLabel([index],'transition-last-active',shot);
  need(!plan.samples.some(sample=>sample.labels.some(label=>
    label.kind==='word-onset'&&label.shotId==='source'&&label.authoredIndex===0&&label.wordOrdinal===0)),
  `${name} invents the source's off-picture first word onset`);
  need(!at([46,47]).some(label=>label.shotId==='source'&&
    ['word-onset','source-emphasis-onset','source-emphasis-clear'].includes(label.kind)),
  `${name} invents an onset/clear when source moves from active to outgoing`);
  need(!at([11,12]).some(label=>label.shotId==='whole-machine'&&
    ['word-onset','source-emphasis-onset','source-emphasis-clear'].includes(label.kind)),
  `${name} invents a cue event when the lead model moves to outgoing`);
  need(!at([48,49]).some(label=>label.shotId==='source'&&
    ['word-onset','source-emphasis-onset','source-emphasis-clear'].includes(label.kind)),
  `${name} calls the outgoing-to-incoming fade switch a source cue event`);
  need(!plan.samples.some(sample=>sample.labels.some(label=>
    label.kind==='word-onset'&&label.shotId==='continuation'&&label.authoredIndex===0&&
    label.wordOrdinal===0)),`${name} invents the continuation's off-picture first word onset`);
}
async function verifyPack(run){
  const {index,generation}=run.index?{index:run.index,generation:run.pack.generation}:
    {index:await readJson(run.pack.indexPath),generation:run.pack.generation};
  need(index.schema==='review-pack-v1'&&index.status==='generated, not reviewed',
    `${run.name} index makes an incompatible or approval claim`);
  equal(index.inputs?.manifest?.sha256,run.manifestSha256,`${run.name} manifest pack binding`);
  equal(index.inputs?.mp4?.sha256,run.mp4Sha256,`${run.name} MP4 pack binding`);
  equal(index.inputs?.manifest?.path,run.manifestPath,`${run.name} manifest path`);
  equal(index.inputs?.mp4?.path,run.output,`${run.name} MP4 path`);
  need(same(index.film,{count:70,width:960,height:540,fps:10}),`${run.name} indexed film geometry differs`);
  const independent=await independentMetadata(run.output);
  equal(index.decoder?.name,'ffmpeg',`${run.name} decoder name`);
  equal(index.decoder?.codec,independent.stream.codec_name,`${run.name} decoder codec`);
  equal(index.decoder?.timeBase,independent.stream.time_base,`${run.name} decoder time base`);
  equal(index.decoder?.ffmpegVersion,
    (await checked('ffmpeg',['-version'])).toString().split('\n')[0],`${run.name} FFmpeg version`);
  equal(index.decoder?.ffprobeVersion,
    (await checked('ffprobe',['-version'])).toString().split('\n')[0],`${run.name} ffprobe version`);
  const plan=run.reviewSamples,selectedFromPages=new Set(),overview=[],events=[];
  need(plan?.schema==='review-samples-v1'&&plan.frameCount===70&&plan.fps===10,
    `${run.name} resolved review plan differs`);
  assertLeonardoEvents(plan,run.name);
  const sampleKeys=new Set();
  for(const sample of plan.samples){
    const key=sample.indices.join(',');need(!sampleKeys.has(key),`Duplicate resolved sample pair: ${key}`);
    sampleKeys.add(key);
    need(sample.labels.length>0&&sample.labels.every(label=>label.visibility==='resolved candidate, not reviewed'),
      `Unqualified event label at ${key}`);
  }
  const wantedOverview=[];for(let n=0;n<70;n+=5)wantedOverview.push(n);
  if(wantedOverview.at(-1)!==69)wantedOverview.push(69);
  for(const [pageIndex,page] of index.pages.entries()){
    need(['overview','events'].includes(page.kind)&&page.width===1920&&page.height===1980&&
      page.cells?.length===24,`${run.name} page ${pageIndex} shape/bound differs`);
    const pagePath=join(generation,page.file);
    equal(await fileSha(pagePath),page.sha256,`${run.name} page ${pageIndex} artifact hash`);
    for(const [cellIndex,cell] of page.cells.entries()){
      need(same(cell.rect,{x:(cellIndex%4)*480,y:Math.floor(cellIndex/4)*330,width:480,height:330}),
        `${run.name} page ${pageIndex} cell ${cellIndex} rectangle differs`);
      if(cell.padding){
        need(cell.printedLabel==='PADDING'&&!Object.hasOwn(cell,'index'),
          `${run.name} padding masquerades as a decoded frame`);
      }else{
        need(Number.isInteger(cell.index)&&cell.index>=0&&cell.index<70&&
          typeof cell.printedLabel==='string'&&cell.printedLabel.length<=82,
        `${run.name} page ${pageIndex} cell ${cellIndex} label/index invalid`);
        equal(cell.printedLabel,expectedPrintedLabel(cell,independent.frames[cell.index]),
          `${run.name} page ${pageIndex} cell ${cellIndex} printed label`);
        selectedFromPages.add(cell.index);
        (page.kind==='overview'?overview:events).push({pageIndex,cellIndex,...cell});
      }
    }
  }
  need(same(overview.map(cell=>cell.index),wantedOverview)&&wantedOverview.length<=96,
    `${run.name} overview indices/page bound differ`);
  const expectedEvents=[...plan.samples.filter(s=>s.indices.length===2),
    ...plan.samples.filter(s=>s.indices.length===1)].flatMap(sample=>sample.indices.map((frame,i)=>
      ({index:frame,labels:sample.labels,pairStart:sample.indices.length===2&&i===0})));
  need(events.length===expectedEvents.length,`${run.name} event cell count truncated`);
  for(const [i,cell] of events.entries()){
    const want=expectedEvents[i];
    need(cell.index===want.index&&same(cell.labels,want.labels)&&cell.pairStart===want.pairStart,
      `${run.name} event cell ${i} differs from resolved sample plan`);
    if(cell.pairStart)need(events[i+1]?.pageIndex===cell.pageIndex&&
      events[i+1]?.cellIndex===cell.cellIndex+1&&events[i+1].index===cell.index+1,
    `${run.name} event pair split at ${i}`);
  }
  const kinds=new Set(plan.samples.flatMap(s=>s.labels.map(l=>l.kind)));
  for(const kind of ['join','word-onset','source-emphasis-onset','source-emphasis-clear',
    'shot-end','film-end','transition-midpoint','transition-last-active'])
    need(kinds.has(kind),`${run.name} real fixture lacks ${kind} evidence`);
  for(const pair of ['11,12','46,47','56,57'])need(plan.samples.some(s=>s.indices.join(',')===pair&&
    s.labels.some(l=>l.kind==='join')),`${run.name} join pair ${pair} absent`);
  need(plan.samples.some(s=>s.indices.join(',')==='68,69'&&s.labels.some(l=>l.kind==='film-end')),
    `${run.name} film-end pair missing`);
  const selectedList=index.selectedFrames.map(f=>f.index);
  need(same(selectedList,[...selectedFromPages].sort((a,b)=>a-b)),
    `${run.name} selected-frame index set differs from pages`);
  const pixels=await decodeFullMp4(run.output,selectedFromPages),rgbRecords=[];
  for(const frame of index.selectedFrames){
    const metadata=independent.frames[frame.index],path=join(generation,frame.file);
    equal(String(frame.ptsTicks),metadata.ptsTicks,`${run.name} frame ${frame.index} actual PTS`);
    equal(frame.timeBase,metadata.timeBase,`${run.name} frame ${frame.index} time base`);
    equal(await fileSha(path),frame.sha256,`${run.name} frame ${frame.index} artifact hash`);
    const extracted=await rawRgb(path,960,540),reference=pixels.get(frame.index);
    need(extracted.equals(reference),`${run.name} selected PNG RGB differs from independent MP4 frame ${frame.index}`);
    rgbRecords.push({index:frame.index,ptsTicks:frame.ptsTicks,timeBase:frame.timeBase,rgbSha256:sha(reference)});
  }
  const pageRecords=[];
  for(const [i,page] of index.pages.entries()){
    const sheet=await rawRgb(join(generation,page.file),1920,1980);
    let cells=0,padding=0,pixelsChecked=0;
    for(const cell of page.cells){
      if(cell.padding){need(comparePadding(sheet,cell.rect)===0,`${run.name} page ${i} padding has film pixels`);padding++;}
      else{
        const compare=compareCellThumbnail(sheet,pixels.get(cell.index),cell.rect);
        need(compare.mismatches===0,`${run.name} page ${i} frame ${cell.index} thumbnail RGB differs: ${JSON.stringify(compare.first)}`);
        cells++;pixelsChecked+=compare.pixels;
      }
    }
    pageRecords.push({page:i,kind:page.kind,cells,padding,pixelsChecked,
      path:join(generation,page.file),sha256:page.sha256});
  }
  return {exact:true,decodedCount:independent.frames.length,stream:independent.stream,
    decodedPts:independent.frames.map(({index,ptsTicks,timeBase})=>({index,ptsTicks,timeBase})),
    selected:rgbRecords,pages:pageRecords,overviewIndices:wantedOverview,
    sampleCount:plan.samples.length,eventKinds:[...kinds].sort()};
}
async function artifactMap(pack){
  const index=await readJson(pack.indexPath),files=[pack.indexPath,
    ...index.selectedFrames.map(x=>join(pack.generation,x.file)),
    ...index.pages.map(x=>join(pack.generation,x.file))];
  return Object.fromEntries(await Promise.all(files.map(async file=>[file,await fileSha(file)])));
}

try{
  const shared=await build('fresh-cold-and-warm');
  const cold=await runRender('review-cold',shared,70,0);
  equal(cold.mp4Sha256,expected.acceptedSourceOnlyFilm,
    'new review-pack render differs from the accepted source-only film bytes');
  report.comparisons.coldPack=await verifyPack(cold);await save(reportPath,report);
  const coldArtifacts=await artifactMap(cold.pack),coldGeneration=await treeSha(cold.pack.generation);
  const warm=await runRender('review-warm',shared,0,70);
  report.comparisons.warmPack=await verifyPack(warm);await save(reportPath,report);
  equal(warm.mp4Sha256,cold.mp4Sha256,'warm MP4 exact hash');
  need(same(warm.reviewSamples,cold.reviewSamples),'Full-cache warm render changed resolved review plan');
  need(same(report.comparisons.warmPack.selected,report.comparisons.coldPack.selected),
    'Full-cache warm pack changed decoded selected RGB or PTS');
  for(const [file,want] of Object.entries(coldArtifacts))await verifyFile(file,want,'preserved cold pack artifact');
  need(same(await treeSha(cold.pack.generation),coldGeneration),'Warm render changed complete cold-pack generation');
  report.preservation.coldPackArtifacts=coldArtifacts;
  report.preservation.coldPackGeneration=coldGeneration;await save(reportPath,report);

  // A fresh owned manifest/movie copy deliberately points all embedded
  // episode/source/build paths at nonexistent locations. The standalone CLI
  // must consume its stored plan and encoded movie, not those author paths.
  const owned=join(root,'standalone-owned-copy');await mkdir(owned);
  const ownedFilm=join(owned,'film.mp4'),ownedManifest=join(owned,'film-manifest.json');
  await copyFile(warm.output,ownedFilm,fsConstants.COPYFILE_EXCL);
  const sourceManifest=await readJson(warm.manifestPath),missing=join(owned,'absent-author-inputs');
  sourceManifest.output=ownedFilm;
  sourceManifest.episode.paths={episode:join(missing,'episode.yaml'),
    production:join(missing,'production.yaml'),manifest:join(missing,'model.json'),
    repository:join(missing,'repository'),build:join(missing,'build')};
  sourceManifest.episode.model.manifest=join(missing,'export.json');
  for(const entry of Object.values(sourceManifest.episode.sourceCode??{}))
    entry.file=join(missing,'source.py');
  await save(ownedManifest,sourceManifest);
  report.stage='standalone-no-author-inputs';await save(reportPath,report);
  const output=(await checked('node',['bin/videomaker.mjs','review',ownedManifest],tool)).toString();
  need(output.includes('Review pack: '),'Standalone review did not report its pack');
  const ownedPack=await findPack(owned,ownedManifest,await fileSha(ownedFilm));
  const standalone={name:'standalone-owned-copy',output:ownedFilm,mp4Sha256:await fileSha(ownedFilm),
    manifestPath:ownedManifest,manifestSha256:await fileSha(ownedManifest),
    reviewSamples:sourceManifest.reviewSamples,pack:{generation:ownedPack.generation,
      indexPath:ownedPack.indexPath,indexSha256:await fileSha(ownedPack.indexPath)},
    index:ownedPack.index,cliOutput:output.trim()};
  report.standalone={...standalone,index:undefined,verification:await verifyPack(standalone)};
  need(same(report.standalone.verification.selected,report.comparisons.warmPack.selected),
    'Standalone plan/decoded selected RGB or PTS differs from warm render');
  await save(reportPath,report);
  // Revisit the SAME owned manifest through the workspace catalogue symlink.
  // It must verify/reuse the complete generation, never make another pack.
  const aliasRelative=relative(project,ownedManifest);
  need(aliasRelative&&!aliasRelative.startsWith('..')&&!aliasRelative.startsWith(sep),
    'Owned manifest is outside the real Leonardo project');
  const aliasManifest=join(catalogueAlias,aliasRelative);
  equal(await realpath(aliasManifest),await realpath(ownedManifest),
    'Catalogue alias does not resolve to the exact owned manifest');
  const ownedPackTree=await treeSha(ownedPack.generation);
  const ownedPackNames=(await readdir(join(owned,'review-packs'))).sort();
  report.stage='standalone-catalogue-alias-reuse';await save(reportPath,report);
  const aliasOutput=(await checked('node',['bin/videomaker.mjs','review',aliasManifest],tool)).toString().trim();
  need(aliasOutput===`Review pack: ${ownedPack.generation} (verified reuse)`,
    `Catalogue alias did not verify/reuse the same complete pack: ${aliasOutput}`);
  need(same((await readdir(join(owned,'review-packs'))).sort(),ownedPackNames),
    'Catalogue alias created or removed a pack generation');
  need(same(await treeSha(ownedPack.generation),ownedPackTree),
    'Catalogue alias changed the complete owned pack generation');
  equal(await fileSha(ownedManifest),standalone.manifestSha256,
    'Catalogue alias changed the owned manifest');
  report.alias={manifest:aliasManifest,resolvedManifest:await realpath(aliasManifest),
    cliOutput:aliasOutput,reusedGeneration:ownedPack.generation,
    indexSha256:await fileSha(ownedPack.indexPath),generationTree:ownedPackTree};
  await save(reportPath,report);
  for(const [file,want] of Object.entries(coldArtifacts))await verifyFile(file,want,'post-standalone cold pack artifact');
  need(same(await treeSha(cold.pack.generation),coldGeneration),'Standalone review changed complete cold-pack generation');
  report.preservation.priorInputs=await verifyInputs();
  report.review={coldPages:cold.pack.generation,warmPages:warm.pack.generation,
    standalonePages:ownedPack.generation,note:'Generated images are for root/pilot human review, not approval; film is silent.'};
  report.status='passed';report.stage='complete';report.finishedUtc=new Date().toISOString();
  await save(reportPath,report);console.log(`PASS ${reportPath}`);
}catch(error){
  report.status='failed';report.error={stage:report.stage,name:error.name,message:error.message,stack:error.stack};
  report.finishedUtc=new Date().toISOString();await save(reportPath,report);
  console.error(`FAIL ${reportPath}: ${error.message}`);process.exitCode=1;
}
