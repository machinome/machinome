// Independent, project-owned evidence for the root-authored Leonardo source-only fixture.
// PREPARATION ONLY until root replaces every PENDING_ROOT_REVIEW pin and grants
// the sole browser/render lease. No speech generation, source rewrite or product edit.
import {createHash,randomUUID} from 'node:crypto';
import {spawn} from 'node:child_process';
import {constants as fsConstants} from 'node:fs';
import {copyFile,mkdir,readFile,readdir,writeFile} from 'node:fs/promises';
import {basename,dirname,join,relative,resolve,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {isDeepStrictEqual} from 'node:util';

const tool=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const project='/mnt/data/machinome-projects/Leonardo';
const fixture=join(project,'videos/demo-source-only');
const coldFixture=join(project,'videos/demo-source-only-cold');
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
const take='source-72b6eea39321423a.wav';
const line='water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)';
const reviewIndices=[0,10,11,12,13,14,15,16,20,25,30,40,46,47,48,49,50,51,56,57,65,69];
const groups=[{shotId:'whole-machine',count:12},{shotId:'source',count:35},
  {shotId:'continuation',count:10},{shotId:'whole-return',count:13}];
const expected={
  projectHead:'28b43bce1b88446995f0ff231dd9075d1a839ab3',
  baseline:'d15a03865ffef8685f5427110e64825ae29e3fb376b229f84145c730318497ef',
  edited:'37989962da303a91b72c0ae9590edb2964ea87762b37bdd3235d6181ccf28766',
  production:'fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3',
  description:'a0a5e535d86d7f919d96308afff20f95368d859667b640bd00a756f10ee0f2ea',
  modelSource:'947ef0fc2540531f602beffdf48ea7b2ffb356378c4aefbd7f52a058e85300ea',
  exportManifest:'92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9',
  exportTree:'6ba645c99936216c84994379e7e1f3d39144197c640b7b838e9849e848628682',
  exportFiles:120,
  viewer:'5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413',
  take:'fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8',
  alignment:'ee78ced064e170a82118254c7a94588a0afe68af43f3cd890ed76b52c5ac7ea3',
  prechangeProductions:{
    'format-02-model':'7bd0b1fd474462329c80e3cc8d4e8e1ddc5396abbf9518d85d0b7a7f98451cb3',
    'format-03-annotated':'95bd905cab668baa9d82914ac13df2efb4663516995188c16fff1fa362c97c23',
    'format-04-model':'6ce70fb6d1c05d8e64744df72f15cdf70c7c8b4b3ba570707ac76573a4972280',
    'format-04-split':'fdb663363cdc8595d99619b194a734bf0942fad23320d5675e214909c19732e3',
  },
  // Root fills these only after reviewing the completed implementation and
  // apply's immutable pre-change 13-pose baseline. A pending value is fatal
  // before this script creates any output.
  runtimeSrcTree:'d095c77dc2622b43e964fa67e15b386bd50cd780f41be7d3ab154a965c1d42db',
  runtimeBin:'702c52e46ea13a584c8168dce034cfac7227d546a8d049e6331b0ff74ca07990',
  runtimeLockfile:'c83093ba053bf5e92d480b4e3c947fb83e3a9c54904f88a81a21a7c22da59d15',
  prechange13Report:'4b7d4198b3b4eb73eb95ec8e40a50ce01fc3a76f4335f00fc6962d451a08d305',
};

const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const fileSha=async path=>sha(await readFile(path));
const need=(condition,message)=>{if(!condition)throw new Error(message);};
const equal=(actual,want,label)=>need(actual===want,`${label} changed: ${actual} != ${want}`);
const save=async(report,path)=>writeFile(path,JSON.stringify(report,null,2)+'\n');
async function filesOf(root){
  const files=[];
  async function walk(at){
    for(const entry of await readdir(at,{withFileTypes:true})){
      const path=join(at,entry.name);
      if(entry.isDirectory())await walk(path);
      else if(entry.isFile())files.push(relative(root,path).split(sep).join('/'));
      else throw new Error(`Unexpected export/source tree entry: ${path}`);
    }
  }
  await walk(root);return files.sort();
}
async function treeSha(root){
  const files=await filesOf(root),hash=createHash('sha256');
  for(const name of files){hash.update(name);hash.update('\0');hash.update(await readFile(join(root,name)));hash.update('\0');}
  return {files:files.length,sha256:hash.digest('hex')};
}
async function command(exe,args,cwd){
  return new Promise((done,fail)=>{
    const child=spawn(exe,args,{cwd,env:process.env}),out=[],err=[];
    child.stdout.on('data',bytes=>out.push(bytes));child.stderr.on('data',bytes=>err.push(bytes));
    child.on('error',fail);child.on('close',code=>done({code,stdout:Buffer.concat(out).toString(),stderr:Buffer.concat(err).toString()}));
  });
}
async function checkedCommand(exe,args,cwd){
  const result=await command(exe,args,cwd);
  need(result.code===0,`${exe} failed (${result.code}): ${result.stderr.slice(0,1200)}`);
  return result.stdout;
}
async function verifyFile(path,want,label){equal(await fileSha(path),want,label);}

// Root supplies the exact saved report from source-only-baseline.mjs. It is
// read-only and its captured PNG bytes must still match their records.
const args=process.argv.slice(2);
need(args.length===2&&args[0]==='--prechange-report',
  'Usage: node source-only-evidence.mjs --prechange-report /absolute/report.json');
const prechangePath=resolve(args[1]);
for(const key of ['runtimeSrcTree','runtimeBin','runtimeLockfile','prechange13Report'])
  need(/^[0-9a-f]{64}$/.test(expected[key]),`Root-reviewed ${key} pin is still pending; no output created`);

// All preflight is read-only. Do not create the fresh output root until every
// fixture, export, cache, viewer, runtime and pre-change artifact checks out.
const projectHead=(await checkedCommand('git',['rev-parse','HEAD'],project)).trim();
equal(projectHead,expected.projectHead,'Leonardo HEAD');
const inputFiles=[
  [join(fixture,'episode-baseline.yaml'),expected.baseline,'split baseline'],
  [join(fixture,'episode.yaml'),expected.edited,'source-only edit'],
  [join(fixture,'production.yaml'),expected.production,'production'],
  [join(fixture,'description.md'),expected.description,'description'],
  [join(coldFixture,'episode.yaml'),expected.edited,'cold episode'],
  [join(coldFixture,'production.yaml'),expected.production,'cold production'],
  [join(coldFixture,'description.md'),expected.description,'cold description'],
  [join(project,'models/hydraulic_sawmill/model.py'),expected.modelSource,'pinned Python source'],
  [join(project,'export/hydraulic_sawmill/manifest.json'),expected.exportManifest,'export manifest'],
  [viewer,expected.viewer,'repaired viewer'],
];
for(const [path,want,label] of inputFiles)await verifyFile(path,want,label);
const exportTree=await treeSha(join(project,'export/hydraulic_sawmill'));
equal(exportTree.files,expected.exportFiles,'export file count');
equal(exportTree.sha256,expected.exportTree,'complete export tree');
for(const base of [fixture,coldFixture])for(const [suffix,want] of [[take,expected.take],[take+'.json',expected.alignment]])
  await verifyFile(join(base,'_build/audio',suffix),want,`${basename(base)} cached ${suffix}`);
const baselineText=await readFile(join(fixture,'episode-baseline.yaml'),'utf8');
const editedText=await readFile(join(fixture,'episode.yaml'),'utf8');
need(editedText.split('    layout: source-only\n').length===2&&
  editedText.replace('    layout: source-only\n','')===baselineText,
  'Split control and source-only edit are not exactly one layout line apart');
equal((await readFile(join(project,'models/hydraulic_sawmill/model.py'),'utf8')).split('\n')[414].trimStart(),line,'model.py line 415');
const runtime={srcTree:await treeSha(join(tool,'src')),bin:await fileSha(join(tool,'bin/videomaker.mjs')),
  lockfile:await fileSha(join(tool,'package-lock.json'))};
equal(runtime.srcTree.sha256,expected.runtimeSrcTree,'reviewed runtime source tree');
equal(runtime.bin,expected.runtimeBin,'reviewed CLI');
equal(runtime.lockfile,expected.runtimeLockfile,'reviewed lockfile');
await verifyFile(prechangePath,expected.prechange13Report,'pre-change 13-pose report');
const prechange=JSON.parse(await readFile(prechangePath,'utf8'));
equal(prechange.viewerSha256,expected.viewer,'pre-change viewer');
need(prechange.cases?.length===4&&prechange.cases.reduce((n,c)=>n+c.records.length,0)===13,
  'Pre-change report does not contain the approved 4 cases / 13 poses');
const prechangeProductions=[];
need(isDeepStrictEqual(prechange.cases.map(c=>c.name).sort(),Object.keys(expected.prechangeProductions).sort()),
  'Pre-change report case names differ from the four pinned productions');
for(const sample of prechange.cases){
  await verifyFile(sample.source,sample.episodeSha256,`pre-change ${sample.name} source`);
  const productionPath=join(dirname(sample.source),'production.yaml');
  const productionSha256=expected.prechangeProductions[sample.name];
  await verifyFile(productionPath,productionSha256,`pre-change ${sample.name} production`);
  prechangeProductions.push({name:sample.name,path:productionPath,sha256:productionSha256});
  for(const frame of sample.records)await verifyFile(frame.file,frame.sha256,`pre-change ${sample.name} ${frame.time}`);
}

const evidenceParent=join(fixture,'_build/evidence');
await mkdir(evidenceParent,{recursive:true});
const root=join(evidenceParent,`source-only-${new Date().toISOString().replace(/[:.]/g,'-')}-${randomUUID()}`);
await mkdir(root); // EEXIST is fatal: never reuse an output root or its cache.
const reportPath=join(root,'report.json');
const report={schema:'leonardo-source-only-evidence/1',status:'running',stage:'preflight-complete',
  startedUtc:new Date().toISOString(),root,tool,project,fixture,coldFixture,viewer,
  pins:expected,runtime,exportTree,prechangePath,prechangeSha256:expected.prechange13Report,
  prechangeProductions,
  expected:{globalFrames:70,shotFrames:groups,reusedOnEdit:25,capturedOnEdit:45},
  builds:{},runs:{},comparisons:{},preview:null,positivePictures:null,sourceFirstProof:null,
  compatibility:null,review:null};
await save(report,reportPath);

// Only runtime imports occur after the complete hash gate. The episode source
// stays immutable; overriding paths.build gives fresh, isolated ignored cache
// roots while retaining the original relative source/export resolution.
let loadEpisode,prepareWordTimingForCommand,preview,render,browserSession,frameAt;
try{
  const [episode,timing,runtime,timeline]=await Promise.all([
    import('../../src/episode.mjs'),import('../../src/command-timing.mjs'),
    import('../../src/render.mjs'),import('../../src/timeline.mjs')]);
  ({loadEpisode}=episode);({prepareWordTimingForCommand}=timing);
  ({preview,render,browserSession}=runtime);({frameAt}=timeline);
}catch(error){
  report.status='failed';report.error={stage:'runtime-import',name:error.name,message:error.message,stack:error.stack};
  report.finishedUtc=new Date().toISOString();await save(report,reportPath);throw error;
}
async function build(name){
  const path=join(root,name);await mkdir(path);await mkdir(join(path,'audio'));
  for(const suffix of [take,take+'.json']){
    const from=join(fixture,'_build/audio',suffix),to=join(path,'audio',suffix);
    await copyFile(from,to,fsConstants.COPYFILE_EXCL);
    await verifyFile(to,suffix===take?expected.take:expected.alignment,`fresh ${name} ${suffix}`);
  }
  report.builds[name]=path;await save(report,reportPath);return path;
}
async function load(source,buildPath){
  const e=await loadEpisode(source);e.paths.build=buildPath;
  await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:10});
  return e;
}
async function ffprobe(film){
  const raw=await checkedCommand('ffprobe',['-v','error','-count_frames','-show_entries',
    'stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',film],tool);
  const probe=JSON.parse(raw),video=probe.streams?.find(s=>s.codec_type==='video');
  need(probe.streams?.length===1&&video?.codec_name==='h264'&&video.width===960&&video.height===540&&
    video.r_frame_rate==='10/1'&&video.nb_read_frames==='70'&&Number(probe.format?.duration)===7,
  `Encoded stream differs from 70-frame silent fixture: ${raw}`);
  return probe;
}
async function decodedFrames(film){
  const raw=await checkedCommand('ffmpeg',['-v','error','-i',film,'-map','0:v:0','-f','framemd5','-'],tool);
  const records=raw.split('\n').filter(s=>s&&!s.startsWith('#')).map(s=>s.split(',').at(-1).trim());
  need(records.length===70,`Decoded video has ${records.length} frames instead of 70`);return records;
}
async function inspectRun(name,source,buildPath,output,wallMs){
  const manifestPath=join(buildPath,`${name}-manifest.json`);
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  need(manifest.count===70,`${name} manifest reports ${manifest.count} frames`);
  equal(await fileSha(output),manifest.outputSha256,`${name} MP4 publication`);
  equal(manifest.provenance?.episodeSha256,name.startsWith('split-')?expected.baseline:expected.edited,
    `${name} episode provenance`);
  equal(manifest.provenance?.productionSha256,expected.production,`${name} production provenance`);
  equal(manifest.provenance?.projectHead,expected.projectHead,`${name} project provenance`);
  equal(manifest.hashes?.['/viewer.js'],expected.viewer,`${name} mounted viewer`);
  equal(manifest.hashes?.['/model/manifest.json'],expected.exportManifest,`${name} mounted export`);
  equal(manifest.browser,prechange.cases[0].browser,`${name} Chromium version`);
  const frames=[];
  for(let i=0;i<70;i++){
    const path=join(manifest.dir,`${String(i).padStart(6,'0')}.png`);
    frames.push({index:i,path,sha256:await fileSha(path)});
  }
  need(manifest.cache?.shots?.length===4,`${name} lacks four shot-cache records`);
  for(const [i,g] of groups.entries()){
    const shot=manifest.cache.shots[i];
    need(shot.shotId===g.shotId&&shot.indices?.length===g.count,
      `${name} shot ${i} frame assignment differs from the fractional grid`);
  }
  return {name,build:buildPath,episodePath:source,episodeSha256:await fileSha(source),wallMs,
    output,mp4Sha256:manifest.outputSha256,manifestPath,manifestSha256:await fileSha(manifestPath),
    assemblyDir:manifest.dir,frames,cache:manifest.cache,provenance:manifest.provenance,
    browser:manifest.browser,probe:await ffprobe(output),decodedFrameMd5:await decodedFrames(output)};
}
async function runRender(name,source,buildPath,captured,reused){
  report.stage=name;await save(report,reportPath);
  const e=await load(source,buildPath),started=process.hrtime.bigint();
  const output=await render(e,{viewer,width:960,fps:10,audio:null,label:name});
  const run=await inspectRun(name,source,buildPath,output,Number(process.hrtime.bigint()-started)/1e6);
  report.runs[name]=run;await save(report,reportPath);
  need(run.cache.capturedFrames===captured&&run.cache.reusedFrames===reused,
    `${name} cache count ${run.cache.capturedFrames}/${run.cache.reusedFrames}, expected ${captured}/${reused}`);
  for(const [i,g] of groups.entries())need(run.cache.shots[i].captured+run.cache.shots[i].reused===g.count,
    `${name} shot ${g.shotId} count differs`);
  return run;
}
function compareFrames(a,b){
  const mismatches=[];
  for(let i=0;i<70;i++)if(a.frames[i].sha256!==b.frames[i].sha256)
    mismatches.push({index:i,a:a.frames[i],b:b.frames[i]});
  return {exact:mismatches.length===0,mismatches};
}
function assertShotCounts(run,counts){
  for(const [i,shot] of run.cache.shots.entries()){
    const [captured,reused]=counts[i];
    need(shot.captured===captured&&shot.reused===reused,
      `${run.name} ${shot.shotId} captured/reused ${shot.captured}/${shot.reused}, expected ${captured}/${reused}`);
  }
}
async function positivePictures(e,buildPath){
  const probes=[
    {time:.5,shot:'whole-machine',picture:'model'},
    {time:1.7,shot:'source',picture:'source',marks:['waterwheel']},
    {time:3,shot:'source',picture:'source',marks:['waterwheel','crankshaft']},
    {time:4.1,shot:'source',picture:'source',marks:[]},
    {time:5.2,shot:'continuation',picture:'model'},
    {time:6.2,shot:'whole-return',picture:'model'},
  ];
  const joinTimes=[1.2,1.4,1.5,4.7,4.9,5.0];
  const dir=join(buildPath,'positive-pictures');await mkdir(dir);
  const result=await browserSession(e,viewer,960,[],async({page,pose})=>{
    const pictures=[],joins=[];
    for(const probe of probes){
      const posed=await pose(probe.time,{transition:null});
      const dom=await page.evaluate(()=>{
        const source=document.querySelector('#source'),stage=document.querySelector('#stage'),canvas=stage.querySelector('canvas');
        const visible=el=>{
          if(!el)return false;
          for(let at=el;at;at=at.parentElement){const style=getComputedStyle(at);
            if(style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0)return false;}
          const rect=el.getBoundingClientRect();return rect.width>0&&rect.height>0;
        };
        const rect=el=>{const r=el.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};};
        return {sourceVisible:visible(source),canvasVisible:visible(canvas),sourceRect:rect(source),
          sourceFits:source.scrollHeight<=source.clientHeight&&source.scrollWidth<=source.clientWidth,
          text:document.querySelector('#source-code').textContent,
          marks:[...document.querySelectorAll('#source-code mark.spoken')].map(el=>el.dataset.word),
          brand:document.querySelector('#brand').textContent,
          brandVisible:visible(document.querySelector('#brand')),
          ruleVisible:visible(document.querySelector('#rule'))};
      });
      need(posed.shotId===probe.shot,`Probe ${probe.time} reached ${posed.shotId}`);
      need(dom.brand==='MACHINOME'&&dom.brandVisible&&dom.ruleVisible,`Film chrome absent at ${probe.time}`);
      if(probe.picture==='source'){
        need(dom.sourceVisible&&!dom.canvasVisible&&dom.sourceFits,`Source-only panel/model visibility or fit failed at ${probe.time}`);
        need(dom.text===posed.code?.text,`Displayed source differs from pinned typed state at ${probe.time}`);
        const r=dom.sourceRect;
        need([r.x,r.y,r.width,r.height].every((value,i)=>
          Math.abs(value-[48,86.4,864,340.2][i])<=1),
          `Source panel does not occupy the intended main picture region at ${probe.time}`);
        need(isDeepStrictEqual(dom.marks,probe.marks),`Source emphasis marks differ at ${probe.time}: ${dom.marks}`);
      }else need(!dom.sourceVisible&&dom.canvasVisible,`Model-only control is not visible at ${probe.time}`);
      const path=join(dir,`own-${String(probe.time).replace('.','-')}.png`);
      await page.screenshot({path});pictures.push({...probe,dom,path,sha256:await fileSha(path)});
    }
    for(const time of joinTimes){
      const posed=await pose(time),transition=posed.transition;
      need(transition?.kind==='fade',`Missing authored fade at ${time}`);
      need(Number.isFinite(transition.plate)&&transition.plate>=0&&transition.plate<=1&&
        posed.observed?.chrome?.length===3&&posed.observed.chrome[0].width>0&&
        posed.observed.chrome[2].width>0,
      `Fade plate or film chrome is invalid at ${time}`);
      if(time>=4.65){
        need(posed.shotId==='continuation'&&!posed.layout,
          `Incoming continuation unexpectedly carries source-only layout at ${time}`);
        if(transition.picture==='outgoing')
          need(transition.outgoing?.shotId==='source'&&transition.outgoing.layout==='source-only',
            `Outgoing source lost its own layout at ${time}`);
        else need(transition.picture==='incoming'&&transition.outgoing===null,
          `Incoming half still carries outgoing source at ${time}`);
      }
      const path=join(dir,`join-${String(time).replace('.','-')}.png`);
      await page.screenshot({path});joins.push({time,kind:transition.kind,plate:transition.plate,
        picture:transition.picture,outgoingLayout:transition.outgoing?.layout??null,
        path,sha256:await fileSha(path)});
    }
    return {pictures,joins};
  });
  return result;
}
// A source-only opening must mount a genuinely sized viewer while hidden, then
// restore that same viewer on the next model shot. This is an in-memory
// rearrangement of pinned authored shots, not a new episode file or render.
async function sourceFirstProof(e,buildPath){
  const first={...e.shots[1],start:0,end:3.5};
  delete first.transition;
  const later={...e.shots[3],start:3.5,end:4.8};
  const probe={...e,shots:[first,later],output:{...e.output,durationSeconds:4.8},
    paths:{...e.paths,build:buildPath}};
  need(first.id==='source'&&first.layout==='source-only'&&later.id==='whole-return'&&
    !later.layout,'Source-first probe did not select the intended source/model shots');
  const view=page=>page.evaluate(()=>{
    const source=document.querySelector('#source'),stage=document.querySelector('#stage');
    const canvas=stage.querySelector('canvas'),viewport=document.querySelector('#viewport');
    const visible=el=>{
      if(!el)return false;
      for(let at=el;at;at=at.parentElement){const style=getComputedStyle(at);
        if(style.display==='none'||style.visibility==='hidden'||Number(style.opacity)===0)return false;}
      const rect=el.getBoundingClientRect();return rect.width>0&&rect.height>0;
    };
    const rect=el=>{const r=el.getBoundingClientRect();return {width:r.width,height:r.height};};
    return {viewerMounted:Boolean(window.film?.viewer),canvasCount:stage.querySelectorAll('canvas').length,
      canvasBacking:{width:canvas?.width??0,height:canvas?.height??0},
      canvasRect:canvas?rect(canvas):null,stageRect:rect(stage),
      sourceVisible:visible(source),viewportVisible:visible(viewport),canvasVisible:visible(canvas),
      sourceFits:source.scrollHeight<=source.clientHeight&&source.scrollWidth<=source.clientWidth};
  });
  const result=await browserSession(probe,viewer,960,[],async({page,pose})=>{
    const initial=await view(page);
    need(initial.viewerMounted&&initial.canvasCount===1&&
      initial.canvasBacking.width>0&&initial.canvasBacking.height>0&&
      initial.canvasRect.width>0&&initial.canvasRect.height>0&&
      initial.stageRect.width>0&&initial.stageRect.height>0&&
      initial.sourceVisible&&!initial.viewportVisible&&!initial.canvasVisible,
    'Source-first initial mount lacks a nonzero-sized hidden viewer');
    const sourceFrame=await pose(.8,{transition:null});
    need(sourceFrame.shotId==='source','Source-first probe did not pose its source opening');
    const sourceState=await view(page);
    need(sourceState.viewerMounted&&sourceState.canvasBacking.width>0&&
      sourceState.canvasBacking.height>0&&sourceState.sourceVisible&&
      !sourceState.canvasVisible&&sourceState.sourceFits,
    'Source-first opening lost its hidden mounted viewer or source fit');
    const sourcePath=join(buildPath,'source-first.png');
    const before=await page.screenshot({path:sourcePath});
    const modelFrame=await pose(3.8,{transition:null});
    need(modelFrame.shotId==='whole-return','Source-first probe did not reach its later model shot');
    const modelState=await view(page);
    need(modelState.viewerMounted&&modelState.canvasCount===1&&modelState.canvasVisible&&
      modelState.viewportVisible&&!modelState.sourceVisible&&
      modelState.canvasBacking.width>0&&modelState.canvasBacking.height>0,
    'Later model shot did not restore the originally mounted viewer');
    const modelPath=join(buildPath,'model-restored.png');
    await page.screenshot({path:modelPath});
    await pose(.8,{transition:null});
    const replayPath=join(buildPath,'source-first-replay.png');
    const replay=await page.screenshot({path:replayPath});
    need(before.equals(replay),'Source-first opening did not replay exactly after model restoration');
    return {clone:{sourceEpisode:e.paths.episode,sourceShot:first.id,modelShot:later.id,
      outputDurationSeconds:probe.output.durationSeconds},initial,sourceState,modelState,
      screenshots:[sourcePath,modelPath,replayPath],replayExact:true};
  });
  result.screenshots=await Promise.all(result.screenshots.map(async path=>({path,sha256:await fileSha(path)})));
  return result;
}
async function compareLegacy(){
  const cases=[];
  for(const sample of prechange.cases){
    report.stage=`legacy-${sample.name}`;await save(report,reportPath);
    const e=await loadEpisode(sample.source);
    if(sample.name==='format-04-split')
      await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:e.output.fps});
    const dir=join(root,`legacy-${sample.name}`);await mkdir(dir);e.paths.build=dir;
    const records=[];
    const result=await browserSession(e,viewer,960,[],async({page,pose})=>{
      for(const old of sample.records){
        const request=frameAt(e,old.time,[]),requestExact=isDeepStrictEqual(request,old.request);
        await pose(old.time);
        const path=join(dir,`${String(records.length).padStart(2,'0')}-${old.time.toFixed(2)}.png`);
        await page.screenshot({path});
        records.push({time:old.time,path,sha256:await fileSha(path),
          prechangeSha256:old.sha256,requestExact});
      }
      return {records};
    });
    const evidence={name:sample.name,source:sample.source,browser:result.browser,
      viewerApi:result.viewerApi,records};
    cases.push(evidence);report.compatibility={cases};await save(report,reportPath);
    need(result.browser===sample.browser,`Legacy ${sample.name} browser version changed`);
    need(records.every(r=>r.requestExact&&r.sha256===r.prechangeSha256),
      `Legacy ${sample.name} request/pixel differs; inspect saved PNGs`);
  }
  return {exact:true,count:cases.reduce((n,c)=>n+c.records.length,0),cases};
}
async function reviewFrames(run){
  const dir=join(root,'encoded-review');await mkdir(dir);
  const stills=[];
  for(const index of reviewIndices){
    const output=join(dir,`frame-${String(index).padStart(3,'0')}.png`);
    await checkedCommand('ffmpeg',['-v','error','-n','-i',run.output,'-vf',`select=eq(n\\,${index})`,
      '-frames:v','1',output],tool);
    stills.push({index,path:output,sha256:await fileSha(output)});
  }
  const contactSheet=join(dir,'contact-sheet.png');
  const select=reviewIndices.map(index=>`eq(n\\,${index})`).join('+');
  await checkedCommand('ffmpeg',['-v','error','-n','-i',run.output,'-vf',
    `select=${select},scale=480:270,tile=4x${Math.ceil(reviewIndices.length/4)}`,
    '-frames:v','1',contactSheet],tool);
  return {stills,contactSheet:{path:contactSheet,sha256:await fileSha(contactSheet)}};
}

try{
  const shared=await build('shared-baseline-warm-edit');
  const baseline=await runRender('split-baseline',join(fixture,'episode-baseline.yaml'),shared,70,0);
  assertShotCounts(baseline,groups.map(g=>[g.count,0]));
  const warm=await runRender('split-warm',join(fixture,'episode-baseline.yaml'),shared,0,70);
  assertShotCounts(warm,groups.map(g=>[0,g.count]));
  report.comparisons.warmVsBaseline={...compareFrames(warm,baseline),
    sameMp4Sha256:warm.mp4Sha256===baseline.mp4Sha256,
    sameDecodedFrames:isDeepStrictEqual(warm.decodedFrameMd5,baseline.decodedFrameMd5)};
  await save(report,reportPath);
  need(report.comparisons.warmVsBaseline.exact&&
    report.comparisons.warmVsBaseline.sameMp4Sha256&&
    report.comparisons.warmVsBaseline.sameDecodedFrames,
  'Warm split PNG, MP4 hash or decoded-video output differs from its cold baseline');

  const previewBuild=await build('source-only-preview');
  report.stage='source-only-preview';await save(report,reportPath);
  const editedPreview=await load(join(fixture,'episode.yaml'),previewBuild);
  const previewReport=await preview(editedPreview,{viewer,width:960});
  report.preview={path:join(previewBuild,'preview/report.json'),report:previewReport};await save(report,reportPath);
  need(previewReport.pixelReplay===true,'Source-only preview lacks exact seek replay');
  for(const id of ['source','continuation']){
    const join=previewReport.transitionChecks?.find(c=>c.shotId===id&&c.kind==='fade');
    need(join?.exactColor===true&&join.replay===true,`Preview did not prove ${id} fade and replay`);
  }
  const emphasis=previewReport.emphasisChecks?.find(c=>c.shotId==='source');
  need(emphasis?.replay&&emphasis.samples.some(s=>s.phase==='word-0'&&
    isDeepStrictEqual(s.words,['waterwheel']))&&emphasis.samples.some(s=>s.phase==='word-1'&&
    isDeepStrictEqual(s.words,['waterwheel','crankshaft'])),
  'Preview did not prove measured source emphasis and replay');
  report.positivePictures=await positivePictures(editedPreview,previewBuild);await save(report,reportPath);
  const firstBuild=await build('source-first-probe');
  report.stage='source-first-probe';await save(report,reportPath);
  report.sourceFirstProof=await sourceFirstProof(editedPreview,firstBuild);await save(report,reportPath);

  const edited=await runRender('source-only-incremental',join(fixture,'episode.yaml'),shared,45,25);
  assertShotCounts(edited,[[0,12],[35,0],[10,0],[0,13]]);
  for(const index of [0,3]){
    const before=baseline.cache.shots[index],after=edited.cache.shots[index];
    need(after.generation===before.generation&&isDeepStrictEqual(after.origin,before.origin),
      `Unchanged shot ${after.shotId} did not retain the baseline generation/origin`);
  }
  for(const index of [1,2])need(edited.cache.shots[index].generation!==baseline.cache.shots[index].generation&&
    edited.cache.shots[index].origin.episodeSha256===expected.edited,
  `Changed shot ${edited.cache.shots[index].shotId} did not get a new edited generation`);
  report.comparisons.editVsSplitBaseline=compareFrames(edited,baseline);await save(report,reportPath);
  for(const [start,end,name,wantDifference] of [[0,12,'A',false],[12,47,'B',true],[47,57,'C',true],[57,70,'D',false]]){
    const changed=report.comparisons.editVsSplitBaseline.mismatches.filter(m=>m.index>=start&&m.index<end);
    need(Boolean(changed.length)===wantDifference,`${name} changed-frame expectation failed (${changed.length})`);
  }

  const cold=await build('independent-source-only-cold');
  const coldRun=await runRender('source-only-cold',join(coldFixture,'episode.yaml'),cold,70,0);
  assertShotCounts(coldRun,groups.map(g=>[g.count,0]));
  report.comparisons.incrementalVsCold=compareFrames(edited,coldRun);
  report.comparisons.incrementalVsCold.sameMp4Sha256=edited.mp4Sha256===coldRun.mp4Sha256;
  report.comparisons.incrementalVsCold.sameDecodedFrames=isDeepStrictEqual(edited.decodedFrameMd5,coldRun.decodedFrameMd5);
  await save(report,reportPath);
  need(report.comparisons.incrementalVsCold.exact&&report.comparisons.incrementalVsCold.sameDecodedFrames,
    'Incremental/cold 70-frame PNG or decoded-video equality failed');
  need(report.comparisons.incrementalVsCold.sameMp4Sha256,
    'Encoded MP4 hashes differ; preserve evidence for provenance review, not a pixel-tolerance pass');

  report.compatibility=await compareLegacy();await save(report,reportPath);
  need(report.compatibility.count===13,'Pre-change compatibility did not cover all 13 poses');
  report.review=await reviewFrames(edited);await save(report,reportPath);
  for(const [path,want,label] of inputFiles)await verifyFile(path,want,`post-run ${label}`);
  for(const sample of prechange.cases)
    await verifyFile(sample.source,sample.episodeSha256,`post-run pre-change ${sample.name} source`);
  for(const production of prechangeProductions)
    await verifyFile(production.path,production.sha256,`post-run pre-change ${production.name} production`);
  equal((await treeSha(join(project,'export/hydraulic_sawmill'))).sha256,expected.exportTree,
    'post-run export tree');
  equal((await treeSha(join(tool,'src'))).sha256,expected.runtimeSrcTree,
    'post-run reviewed runtime');
  await verifyFile(join(tool,'bin/videomaker.mjs'),expected.runtimeBin,'post-run reviewed CLI');
  await verifyFile(join(tool,'package-lock.json'),expected.runtimeLockfile,'post-run reviewed lockfile');
  for(const base of [fixture,coldFixture])for(const [suffix,want] of [[take,expected.take],[take+'.json',expected.alignment]])
    await verifyFile(join(base,'_build/audio',suffix),want,`post-run ${basename(base)} cached ${suffix}`);
  report.status='passed';report.stage='complete';report.finishedUtc=new Date().toISOString();
  await save(report,reportPath);console.log(`PASS ${reportPath}`);
}catch(error){
  report.status='failed';report.error={stage:report.stage,name:error.name,message:error.message,stack:error.stack};
  report.finishedUtc=new Date().toISOString();await save(report,reportPath);
  console.error(`FAIL ${reportPath}: ${error.message}`);process.exitCode=1;
}
