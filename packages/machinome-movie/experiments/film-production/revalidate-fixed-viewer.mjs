// One-shot Leonardo real-film revalidation against the fixed API-28 viewer.
// Creates only new project-owned demo directories and their ignored build output.
// Existing historical evidence and product source are never overwritten.
import {mkdir,copyFile,readFile,writeFile} from 'node:fs/promises';
import {resolve,join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {spawn} from 'node:child_process';
import {decodePng} from '../../src/pixels.mjs';

const [projectArg,viewerArg]=process.argv.slice(2);
if(!projectArg||!viewerArg)throw Error('Usage: node revalidate-fixed-viewer.mjs LEONARDO_ROOT FIXED_VIEWER_BUNDLE');
const project=resolve(projectArg),viewer=resolve(viewerArg),tool=resolve(import.meta.dirname,'../..');
const videos=join(project,'videos');
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const fileSha=async path=>sha(await readFile(path));
const expected={
  render:'c34f3423c7130f37965f34534b9fb7eac797774e58f3d3a8ba46b4bc52c50312',
  shotCache:'9dbab4bdfbff39bb4e0ff66def627e6c0bcdda09f05f7e68ca199bebf1b991ed',
  timeline:'af93900b72ccc9b4429ce3df1bde62824988354e439d38d9e6fabeed9703648b',
  film:'74a4ecb314aca8a5e1bfc6cbbd479632584e27b7b57e775e4f5b8093cf18024f',
  viewer:'5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413',
  model:'92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9',
  speech:'fbb90324145522ded0dde83554039c2063c5ac38141cdfa2c85d66f1c28373d8',
};
const actual={
  render:await fileSha(join(tool,'src/render.mjs')),
  shotCache:await fileSha(join(tool,'src/shot-cache.mjs')),
  timeline:await fileSha(join(tool,'src/timeline.mjs')),
  film:await fileSha(join(tool,'src/film.js')),
  viewer:await fileSha(viewer),
  model:await fileSha(join(project,'export/hydraulic_sawmill/manifest.json')),
  speech:await fileSha(join(videos,'demo-incremental-source-grid/_build/audio/source-72b6eea39321423a.wav')),
};
for(const [name,want] of Object.entries(expected))if(actual[name]!==want)throw Error(`${name} input changed: ${actual[name]} != ${want}`);

const invoke=(command,args,cwd)=>new Promise((done,fail)=>{
  const start=process.hrtime.bigint(),child=spawn(command,args,{cwd,env:process.env});
  const out=[],err=[];child.stdout.on('data',chunk=>out.push(chunk));child.stderr.on('data',chunk=>err.push(chunk));
  child.on('error',fail);child.on('close',code=>done({code,wallSeconds:Number(process.hrtime.bigint()-start)/1e9,
    stdout:Buffer.concat(out).toString(),stderr:Buffer.concat(err).toString()}));
});
const configs=[
  {kind:'80',count:80,source:'demo-incremental-rendering',main:'demo-incremental-rendering-fixed',
    colds:['demo-incremental-rendering-fixed-cold'],
    oldBaseline:'bd3e4433c76107149238c3179ea4e469d8eb6f0eafb37a26fc8a3163603451e2',
    oldVariant:'f75acd21e85958dd31aa08964553d7e0b1ee65695a5fc9656f555a78be38df8b',
    edit:['THE TWO FEED PAWLS','STEP AND HOLD THE FEED'],expectedReuse:40,expectedCapture:40,
    reviewFrames:[0,20,25,39,40,42,43,60,65,79]},
  {kind:'70',count:70,source:'demo-incremental-source-grid',main:'demo-incremental-source-grid-fixed',
    colds:['demo-incremental-source-grid-fixed-cold-1','demo-incremental-source-grid-fixed-cold-2','demo-incremental-source-grid-fixed-cold-3'],
    oldBaseline:'9e1ad0a730c47c4ff17e898ca44f37f006fdf0d5141553d807571d20d6d82d09',
    oldVariant:'a8d61ea3206718d2576762505febfab772e8c1db8f95e3cd0785054e6a7b0f96',
    edit:['camera: [{at: 0, preset: drive}]','camera: [{at: 0, preset: drive-near}]'],
    expectedReuse:25,expectedCapture:45,reviewFrames:[0,10,11,12,20,46,47,48,50,57,65,69]},
];

async function stage(dir,source,episodeBytes,copySpeech){
  const target=join(videos,dir);
  await mkdir(target); // Refuse pre-existing names; never overwrite old/new evidence.
  await copyFile(join(videos,source,'production.yaml'),join(target,'production.yaml'));
  await copyFile(join(videos,source,'description.md'),join(target,'description.md'));
  await writeFile(join(target,'episode.yaml'),episodeBytes,{flag:'wx'});
  if(copySpeech){
    const audio=join(target,'_build/audio');await mkdir(audio,{recursive:true});
    for(const extension of ['','.json'])await copyFile(
      join(videos,source,'_build/audio/source-72b6eea39321423a.wav'+extension),
      join(audio,'source-72b6eea39321423a.wav'+extension));
  }
  return target;
}
async function inspectRun(config,episode,manifestPath,result){
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  if(manifest.count!==config.count)throw Error(`${episode}: ${manifest.count} frames; expected ${config.count}`);
  const film=join(dirname(manifestPath),'silent-preview.mp4');
  if(await fileSha(film)!==manifest.outputSha256)throw Error(`${episode}: MP4 hash mismatch`);
  const frames=[];
  for(let i=0;i<config.count;i++){
    const path=join(manifest.dir,`${String(i).padStart(6,'0')}.png`);
    frames.push({index:i,path,sha256:await fileSha(path)});
  }
  const probe=await invoke('ffprobe',['-v','error','-count_frames','-show_entries',
    'stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',film],tool);
  if(probe.code)throw Error(`${episode}: ffprobe failed: ${probe.stderr}`);
  const observed=JSON.parse(probe.stdout),video=observed.streams.find(s=>s.codec_type==='video');
  if(video?.nb_read_frames!==String(config.count)||video.width!==960||video.height!==540||video.r_frame_rate!=='10/1')
    throw Error(`${episode}: MP4 probe differs from fixture: ${probe.stdout}`);
  return {episode,wallSeconds:result.wallSeconds,exitCode:result.code,
    manifestPath,manifestSha256:await fileSha(manifestPath),film,filmSha256:manifest.outputSha256,
    assemblyDir:manifest.dir,browser:manifest.browser,provenance:manifest.provenance,
    cache:manifest.cache,probe:observed,frames};
}
async function save(report,path){await writeFile(path,JSON.stringify(report,null,2)+'\n');}
async function compare(a,b){
  const differences=[];
  for(let i=0;i<a.frames.length;i++)if(a.frames[i].sha256!==b.frames[i].sha256){
    const A=decodePng(await readFile(a.frames[i].path)),B=decodePng(await readFile(b.frames[i].path));
    let changedPixels=0,changedChannels=0,maxChannelDelta=0,x0=A.width,y0=A.height,x1=-1,y1=-1;
    for(let y=0;y<A.height;y++)for(let x=0;x<A.width;x++){
      let changed=false;const offset=(y*A.width+x)*3;
      for(let c=0;c<3;c++){const d=Math.abs(A.rgb[offset+c]-B.rgb[offset+c]);
        if(d){changed=true;changedChannels++;maxChannelDelta=Math.max(maxChannelDelta,d);}}
      if(changed){changedPixels++;x0=Math.min(x0,x);x1=Math.max(x1,x);y0=Math.min(y0,y);y1=Math.max(y1,y);}
    }
    differences.push({index:i,aSha256:a.frames[i].sha256,bSha256:b.frames[i].sha256,
      changedPixels,changedChannels,maxChannelDelta,bounds:{x0,y0,x1,y1}});
  }
  return {equal:differences.length===0,differences};
}
async function extractReview(config,run,root){
  const reviewDir=join(root,'_build/evidence/fixed-viewer-review');await mkdir(reviewDir,{recursive:true});
  const stills=[];
  for(const index of config.reviewFrames){
    const output=join(reviewDir,`frame-${String(index).padStart(3,'0')}.png`);
    const result=await invoke('ffmpeg',['-v','error','-y','-i',run.film,'-vf',`select=eq(n\\,${index})`,
      '-frames:v','1',output],tool);
    if(result.code)throw Error(`ffmpeg frame ${index}: ${result.stderr}`);
    stills.push({index,path:output,sha256:await fileSha(output)});
  }
  const sheet=join(reviewDir,'contact-sheet.png');
  const result=await invoke('ffmpeg',['-v','error','-y','-i',run.film,'-vf',
    `select='${config.reviewFrames.map(n=>`eq(n\\,${n})`).join('+')}',scale=480:270,tile=4x${Math.ceil(config.reviewFrames.length/4)}`,
    '-frames:v','1',sheet],tool);
  if(result.code)throw Error(`ffmpeg contact sheet: ${result.stderr}`);
  return {stills,contactSheet:{path:sheet,sha256:await fileSha(sheet)}};
}

for(const config of configs){
  const sourceDir=join(videos,config.source),baseline=await readFile(join(sourceDir,'episode-baseline.yaml'));
  if(sha(baseline)!==config.oldBaseline)throw Error(`${config.kind}: baseline source changed`);
  const baselineText=baseline.toString();
  const editStart=config.kind==='70'?baselineText.indexOf('  - id: source\n'):0;
  const editEnd=config.kind==='70'?baselineText.indexOf('  - id: continuation\n'):baselineText.length;
  if(editStart<0||editEnd<=editStart)throw Error(`${config.kind}: cannot isolate edited shot`);
  const section=baselineText.slice(editStart,editEnd),matches=section.split(config.edit[0]).length-1;
  if(matches!==1)throw Error(`${config.kind}: expected exactly one edit target in shot, got ${matches}`);
  const variant=Buffer.from(baselineText.slice(0,editStart)+section.replace(config.edit[0],config.edit[1])+baselineText.slice(editEnd));
  if(sha(variant)!==config.oldVariant)throw Error(`${config.kind}: variant source differs from measured edit`);
  const main=await stage(config.main,config.source,baseline,config.kind==='70');
  const reportPath=join(main,'_build/evidence/fixed-viewer-revalidation.json');
  await mkdir(dirname(reportPath),{recursive:true});
  const report={schema:'leonardo-fixed-viewer-revalidation/1',status:'running',kind:config.kind,
    inputSha256:actual,viewerPath:viewer,toolPath:tool,projectPath:project,
    source:{baseline:sha(baseline),variant:sha(variant),production:await fileSha(join(main,'production.yaml'))},
    expected:{frames:config.count,reusedOnEdit:config.expectedReuse,capturedOnEdit:config.expectedCapture},
    runs:{},comparisons:{},review:null};
  await save(report,reportPath);
  const render=async(name,episode)=>{
    const logDir=join(main,'_build/evidence/fixed-viewer-logs');await mkdir(logDir,{recursive:true});
    const result=await invoke('node',['bin/videomaker.mjs','render',join(episode,'episode.yaml'),
      '--viewer',viewer,'--silent'],tool);
    await writeFile(join(logDir,`${name}.stdout.txt`),result.stdout,{flag:'wx'});
    await writeFile(join(logDir,`${name}.stderr.txt`),result.stderr,{flag:'wx'});
    if(result.code)throw Error(`${config.kind}/${name} render failed with ${result.code}; logs at ${logDir}`);
    const evidence=join(episode,'_build/evidence/fixed-viewer-'+name);
    await mkdir(evidence,{recursive:true});
    await copyFile(join(episode,'_build/silent-preview.mp4'),join(evidence,'silent-preview.mp4'));
    await copyFile(join(episode,'_build/silent-preview-manifest.json'),join(evidence,'silent-preview-manifest.json'));
    // Manifest keeps its immutable assembly-generation path in this episode.
    const run=await inspectRun(config,episode,join(evidence,'silent-preview-manifest.json'),result);
    report.runs[name]=run;await save(report,reportPath);
    console.log(`${config.kind}/${name}: ${result.wallSeconds.toFixed(2)} s, ${run.cache?.capturedFrames} captured, ${run.cache?.reusedFrames} reused, MP4 ${run.filmSha256}`);
    return run;
  };
  try{
    const baselineRun=await render('baseline',main);
    const warm=await render('warm',main);
    report.comparisons.warmVsBaseline=await compare(warm,baselineRun);await save(report,reportPath);
    if(!report.comparisons.warmVsBaseline.equal)throw Error(`${config.kind}: warm differs from baseline`);
    await writeFile(join(main,'episode.yaml'),variant); // New fixture only, preserving baseline copy separately below.
    await writeFile(join(main,'episode-baseline.yaml'),baseline,{flag:'wx'});
    const variantRun=await render('variant',main);
    report.comparisons.variantVsBaseline=await compare(variantRun,baselineRun);await save(report,reportPath);
    if(variantRun.cache?.reusedFrames!==config.expectedReuse||variantRun.cache?.capturedFrames!==config.expectedCapture)
      throw Error(`${config.kind}: unexpected cache counts`);
    for(let i=0;i<config.colds.length;i++){
      const cold=await stage(config.colds[i],config.source,variant,config.kind==='70');
      const coldRun=await render(`cold${i+1}`,cold);
      report.comparisons[`variantVsCold${i+1}`]=await compare(variantRun,coldRun);
      await save(report,reportPath);
      console.log(`${config.kind}/cold${i+1}: exact ${report.comparisons[`variantVsCold${i+1}`].equal}`);
      if(!report.comparisons[`variantVsCold${i+1}`].equal)
        throw Error(`${config.kind}: variant differs from independent cold ${i+1}`);
    }
    report.review=await extractReview(config,variantRun,main);
    report.status='passed';await save(report,reportPath);
    console.log(`${config.kind}: PASS; report ${reportPath}`);
  }catch(error){
    report.status='failed';report.error={name:error.name,message:error.message,stack:error.stack};
    await save(report,reportPath);console.error(`${config.kind}: FAIL ${error.message}; report ${reportPath}`);
    process.exitCode=1;break;
  }
}
