// Prepared only: do not run without root's exclusive browser/render lease.
// Two full, cold 450-frame arms; product sources are read, never edited.
// Usage: node experiments/film-production/profile-compositing.mjs [NEW_OUTPUT_DIR]
// Default output is a newly named ignored directory in Leonardo's _build.
import {readFile,writeFile,copyFile,mkdir,readdir,symlink} from 'node:fs/promises';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {performance} from 'node:perf_hooks';
import {Script} from 'node:vm';
import {loadEpisode} from '../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {render as productRender} from '../../src/render.mjs';
import {outputShotUnits} from '../../src/shot-cache.mjs';
import {fileHash,command} from '../../src/util.mjs';

const here=dirname(fileURLToPath(import.meta.url)),tool=resolve(here,'../..'),source=join(tool,'src');
const fixture='/home/asa/devel/machinome/projects/Leonardo/videos/demo-graphic-overlays/episode.yaml';
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
const pins={
  render:'c34f3423c7130f37965f34534b9fb7eac797774e58f3d3a8ba46b4bc52c50312',
  film:'74a4ecb314aca8a5e1bfc6cbbd479632584e27b7b57e775e4f5b8093cf18024f',
  cache:'9dbab4bdfbff39bb4e0ff66def627e6c0bcdda09f05f7e68ca199bebf1b991ed',
  timeline:'af93900b72ccc9b4429ce3df1bde62824988354e439d38d9e6fabeed9703648b',
  code:'8ee22334b646543c92e5e483803c6e21a852e86600e50875aa640656cd94364b',
  commandTiming:'4253aae83c46cfbf1aa46aff6c9ad506258e0648352e1934a4e99d2befb92a99',
  easing:'b83a96d8c2364077e5fa0328e7233dfa147df45fa2c97764f84a4d0ee5a53804',
  episodeModule:'51bc4c3dbfa654205a92cce9e3f14e9da1d65682c74e057546b6b6f88c526864',
  pictures:'075313592d885b596273acb00853152b1c4c73f3245ac375b958551cf1882092',
  pixels:'9090c6fcafdd4b13c5b5c01de7038b0ba473038fbde6610874528f0cff2896d9',
  speechModule:'41fcd65628ee14f1a8e37ff6406d62b47349c835d28c8cb4ff2e2de579483dd5',
  util:'4d76b3e162bed50d6aa8fdd9a15ca8cdd1d86687d88ef15b5ff761daab8ccec0',
  words:'686a56570cd5334956764e55b98f45e34d752c51a6380225f70d50fafdb8d05a',
  filmHtml:'21cdfe37ce977deb11fd897838cac4eed25991789f45dbd8a5a3f9b715437f9a',
  lockfile:'c83093ba053bf5e92d480b4e3c947fb83e3a9c54904f88a81a21a7c22da59d15',
  viewer:'5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413',
  episode:'1507bcad8a95598a1ef52b70f61773df816febb22d092f9b61deaa56b96780c4',
  production:'437ffaa5bde70ff9dddfcfbfceea53217252bdc74ff44624314865b054059f08',
  model:'92c3f1cb757dfa6d67c225bab89bbd4b096ea2b5469e5387e7aba7e60c3365b9',
};
const paths={render:join(source,'render.mjs'),film:join(source,'film.js'),cache:join(source,'shot-cache.mjs'),
  timeline:join(source,'timeline.mjs'),code:join(source,'code.mjs'),
  commandTiming:join(source,'command-timing.mjs'),easing:join(source,'easing.mjs'),
  episodeModule:join(source,'episode.mjs'),pictures:join(source,'pictures.mjs'),
  pixels:join(source,'pixels.mjs'),speechModule:join(source,'speech.mjs'),
  util:join(source,'util.mjs'),words:join(source,'words.mjs'),
  filmHtml:join(source,'film.html'),lockfile:join(tool,'package-lock.json'),
  viewer,episode:fixture,
  production:resolve(dirname(fixture),'production.yaml'),
  model:'/home/asa/devel/machinome/projects/Leonardo/export/hydraulic_sawmill/manifest.json'};
const now=()=>performance.now();
const fail=(message)=>{throw new Error(message);};
async function checkPins(){
  const actual={};for(const [name,path] of Object.entries(paths)){
    actual[name]=await fileHash(path);
    if(actual[name]!==pins[name])fail(`Pinned ${name} drifted (${actual[name]}). Review anchors/plan before profiling; no output created.`);
  }
  return actual;
}
function exact(sourceText,oldText,newText,number=1){
  const count=sourceText.split(oldText).length-1;
  if(count!==number)fail(`Private instrumentation anchor count ${count}, expected ${number}: ${oldText.slice(0,90)}`);
  return sourceText.replaceAll(oldText,newText);
}

function instrumentRender(input){
  let s="import {profile} from './profile-hook.mjs';\n"+input;
  s=exact(s,'  validatePictureSizing(e,width);\n  await extractClips(e);',
    "  const __preflightStart=performance.now();validatePictureSizing(e,width);\n  await profile.measure('clipPreparation',()=>extractClips(e));profile.add('browserSessionPreflight',performance.now()-__preflightStart);");
  s=exact(s,'const {paths,hashes}=await stage(e,viewer);',
    "const {paths,hashes}=await profile.measure('assetStage',()=>stage(e,viewer));");
  s=exact(s,"await new Promise(r=>server.listen(0,'127.0.0.1',r));",
    "await profile.measure('loopbackServerStart',()=>new Promise(r=>server.listen(0,'127.0.0.1',r)));");
  s=exact(s,"browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});",
    "browser=await profile.measure('browserLaunch',()=>chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']}));");
  s=exact(s,'const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});',
    "const page=await profile.measure('pageCreate',()=>browser.newPage({viewport:{width,height},deviceScaleFactor:1}));");
  s=exact(s,'await page.goto(`http://127.0.0.1:${server.address().port}/`);',
    "await profile.measure('pageNavigate',()=>page.goto(`http://127.0.0.1:${server.address().port}/`));");
  s=exact(s,'await page.waitForFunction(()=>window.film||window.filmError,{},{timeout:60000});',
    "await profile.measure('pageMountReady',()=>page.waitForFunction(()=>window.film||window.filmError,{},{timeout:60000}));");
  s=exact(s,'const observed=await page.evaluate(f=>window.film.setFrame(f),{...request,pictureOnly,fresh:fresh||pictureOnly});',
    "const observed=await profile.measure('setFrameAwaited',()=>page.evaluate(f=>window.film.setFrame(f),{...request,pictureOnly,fresh:fresh||pictureOnly}));\n      profile.pageTimes(observed);const __checksStart=performance.now();profile.count('setFrame');");
  s=exact(s,'      return observed;\n    }\n    async function showPicture',
    "      profile.add('showLayoutChecks',performance.now()-__checksStart);return observed;\n    }\n    async function showPicture");
  s=exact(s,"captures.push({src:'data:image/png;base64,'+(await page.screenshot()).toString('base64'),weight});",
    "captures.push({src:'data:image/png;base64,'+(await profile.screenshot(page,'pictureSubset')).toString('base64'),weight});");
  s=exact(s,"pictures.push({src:'data:image/png;base64,'+(await page.screenshot()).toString('base64'),weight});",
    "pictures.push({src:'data:image/png;base64,'+(await profile.screenshot(page,'annotationSubset')).toString('base64'),weight});");
  s=exact(s,'Object.assign(observed,await page.evaluate(p=>window.film.composeMarkBlend(p),captures));',
    "Object.assign(observed,await profile.measure('composeMarkBlendAwaited',async()=>{const result=await page.evaluate(p=>window.film.composeMarkBlend(p),captures);profile.pageResult(result);profile.count('pictureBlend');return result;}));");
  s=exact(s,'Object.assign(observed,await page.evaluate(p=>window.film.composeMarkBlend(p),pictures));',
    "Object.assign(observed,await profile.measure('composeMarkBlendAwaited',async()=>{const result=await page.evaluate(p=>window.film.composeMarkBlend(p),pictures);profile.pageResult(result);profile.count('annotationBlend');return result;}));");
  s=exact(s,"(await page.screenshot()).toString('base64'),observed};",
    "(await profile.screenshot(page,'transitionPicture')).toString('base64'),observed};");
  s=exact(s,'const baseline=frameAt(e,t,captions);',
    "const __timelineStart=performance.now(),baseline=frameAt(e,t,captions);profile.add('frameAt',performance.now()-__timelineStart);");
  s=exact(s,'Object.assign(observed,await page.evaluate(r=>window.film.compose(r),{...request,pictureOnly}));',
    "Object.assign(observed,await profile.measure('composeTransitionAwaited',()=>page.evaluate(r=>window.film.compose(r),{...request,pictureOnly})));profile.count('transitionCompose');");
  s=exact(s,'await fingerprintShotUnits(e,units,commonKey);',
    "await profile.measure('fingerprintShotUnits',()=>fingerprintShotUnits(e,units,commonKey));");
  s=exact(s,"await resolveWordTiming(e,shot=>readSpeechTake(e,shot));\n  validateWordFramesAtFps(e,fps);",
    "await profile.measure('renderWordTiming',()=>resolveWordTiming(e,shot=>readSpeechTake(e,shot)));\n  validateWordFramesAtFps(e,fps);");
  s=exact(s,"  const fontRecord=await fontFile(e.style.fontFamily??'DejaVu Sans');",
    "  const __fontStart=performance.now();const fontRecord=await fontFile(e.style.fontFamily??'DejaVu Sans');");
  s=exact(s,"  const codeBold=await fontFile('DejaVu Sans Mono','Bold');",
    "  const codeBold=await fontFile('DejaVu Sans Mono','Bold');profile.add('fontPreflight',performance.now()-__fontStart);");
  s=exact(s,'let selected=await findShotGeneration(root,unit,commonKey,width,info.height);',
    "let selected=await profile.measure('cacheLookup',()=>findShotGeneration(root,unit,commonKey,width,info.height));");
  s=exact(s,'selected=await captureShotGeneration(root,unit,commonKey,width,info.height,async frame=>{\n          await pose(frame.time);\n          const bytes=await page.screenshot();capturedFrames++;',
    "selected=await captureShotGeneration(root,unit,commonKey,width,info.height,async frame=>{\n          profile.startFrame(frame);\n          await profile.measure('poseOrchestration',()=>pose(frame.time));\n          const bytes=await profile.screenshot(page,'final');capturedFrames++;");
  s=exact(s,'const dir=await assembleShotFrames(root,units,selections,count);',
    "const dir=await profile.measure('assembleShotFrames',()=>assembleShotFrames(root,units,selections,count));");
  s=exact(s,'  const report=await browserSession(e,viewer,width,captions,async({page,pose,info})=>{',
    "  const __browserSessionStart=performance.now();const report=await browserSession(e,viewer,width,captions,async({page,pose,info})=>{");
  s=exact(s,'  const output=resolve(e.paths.build,`${label}.mp4`);',
    "  profile.add('browserSessionTotal',performance.now()-__browserSessionStart);\n  const output=resolve(e.paths.build,`${label}.mp4`);");
  s=exact(s,"console.log('Encoding '+output);await command('ffmpeg',args);",
    "console.log('Encoding '+output);await profile.measure('ffmpegEncode',()=>command('ffmpeg',args));");
  s=exact(s,"const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',pendingOutput]));",
    "const probe=JSON.parse(await profile.measure('ffprobe',()=>command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',pendingOutput])));");
  s=exact(s,"await writeFile(pendingManifest,JSON.stringify(manifest,null,2)+'\\n');",
    "await profile.measure('manifestWrite',()=>writeFile(pendingManifest,JSON.stringify(manifest,null,2)+'\\n'));");
  s=exact(s,'await rename(pendingManifest,manifestOutput);',
    "await profile.measure('manifestPublish',()=>rename(pendingManifest,manifestOutput));");
  // The private copy lives under Leonardo's ignored build directory. Preserve
  // the original tool-worktree provenance rather than using that copy's Git cwd.
  s=exact(s,"cwd:resolve(here,'..')","cwd:'"+tool+"'",1);
  s=exact(s,"await gitHead(resolve(here,'..'))","await gitHead('"+tool+"')",1);
  return s;
}
function instrumentCache(input){
  let s="import {profile} from './profile-hook.mjs';\n"+input;
  s=exact(s,"await writeFile(path+'.tmp',bytes);await rename(path+'.tmp',path);",
    "await profile.measure('framePngWritePublish',async()=>{await writeFile(path+'.tmp',bytes);await rename(path+'.tmp',path);});");
  s=exact(s,'frames.push({index:frame.index,time:frame.time,file,width,height,sha256:hash(bytes)});',
    "const __hashStart=performance.now(),digest=hash(bytes);profile.add('framePngHash',performance.now()-__hashStart);\n    frames.push({index:frame.index,time:frame.time,file,width,height,sha256:digest});profile.endFrame();");
  s=exact(s,"await json(resolve(generation,'index.json'),index);",
    "await profile.measure('shotIndexPublish',()=>json(resolve(generation,'index.json'),index));");
  return s;
}
function instrumentFilm(input){
  let s=input;
  s=exact(s,'    clearComposition();document.body.classList.add(\'in-mark-blend\');',
    "    const __profile={decode:0,drawReadback:0,weightedBlend:0,roundOutput:0,putAttach:0};const __allStart=performance.now();\n    clearComposition();document.body.classList.add('in-mark-blend');");
  s=exact(s,'      const img=new Image();img.src=src;await img.decode();ctx.clearRect(0,0,W,H);ctx.drawImage(img,0,0);\n      const rgba=ctx.getImageData(0,0,W,H).data;\n      for(let i=0;i<rgba.length;i++)sum[i]+=rgba[i]*weight;',
    "      let __part=performance.now();const img=new Image();img.src=src;await img.decode();__profile.decode+=performance.now()-__part;\n      __part=performance.now();ctx.clearRect(0,0,W,H);ctx.drawImage(img,0,0);\n      const rgba=ctx.getImageData(0,0,W,H).data;__profile.drawReadback+=performance.now()-__part;\n      __part=performance.now();for(let i=0;i<rgba.length;i++)sum[i]+=rgba[i]*weight;__profile.weightedBlend+=performance.now()-__part;");
  s=exact(s,'    const output=ctx.createImageData(W,H);\n    for(let i=0;i<sum.length;i++)output.data[i]=Math.round(sum[i]);\n    ctx.putImageData(output,0,0);transition.append(canvas);\n    return {chrome:chrome()};',
    "    let __part=performance.now();const output=ctx.createImageData(W,H);\n    for(let i=0;i<sum.length;i++)output.data[i]=Math.round(sum[i]);__profile.roundOutput=performance.now()-__part;\n    __part=performance.now();ctx.putImageData(output,0,0);transition.append(canvas);__profile.putAttach=performance.now()-__part;\n    __profile.markBlendTotal=performance.now()-__allStart;return {chrome:chrome(),__profile};");
  s=exact(s,'    // Every frame starts from an empty transition layer and a visible stage.\n    clearComposition();',
    '    const __profileStart=performance.now(),__profile={};\n    // Every frame starts from an empty transition layer and a visible stage.\n    clearComposition();');
  s=exact(s,'    viewer.setTime(frame.time);',
    "    __profile.preViewerState=performance.now()-__profileStart;const __viewerStart=performance.now();\n    viewer.setTime(frame.time);");
  s=exact(s,'    else viewer.setView(frame.view);\n    const overlays=',
    "    else viewer.setView(frame.view);\n    __profile.viewerPose=performance.now()-__viewerStart;const __layoutStart=performance.now();\n    const overlays=");
  s=exact(s,'    const picture=await drawPicture(frame.picture);\n    if(frame.fresh||frame.picture)await repaint();',
    "    const picture=await drawPicture(frame.picture);__profile.layoutAndPicture=performance.now()-__layoutStart;\n    if(frame.fresh||frame.picture){const __repaintStart=performance.now();await repaint();__profile.repaintWait=performance.now()-__repaintStart;}");
  s=exact(s,'    const view=viewer.view();\n    return {camera:',
    "    const view=viewer.view();__profile.setFrameTotal=performance.now()-__profileStart;\n    return {__profile,camera:");
  return s;
}

async function privateCopy(root){
  const privateRoot=join(root,'private'),privateSrc=join(privateRoot,'src');
  await mkdir(privateSrc,{recursive:true});
  const files=await readdir(source);
  for(const name of files)await copyFile(join(source,name),join(privateSrc,name));
  await copyFile(join(tool,'package-lock.json'),join(privateRoot,'package-lock.json'));
  await symlink(join(tool,'node_modules'),join(privateRoot,'node_modules'),'dir');
  await copyFile(join(here,'profile-hook.mjs'),join(privateSrc,'profile-hook.mjs'));
  for(const [name,transform] of [['render.mjs',instrumentRender],['shot-cache.mjs',instrumentCache],['film.js',instrumentFilm]]){
    const path=join(privateSrc,name),original=await readFile(path,'utf8');
    await writeFile(path,transform(original));
  }
  const hashes={};for(const name of ['render.mjs','shot-cache.mjs','film.js','profile-hook.mjs'])
    hashes[name]=await fileHash(join(privateSrc,name));
  return {privateSrc,hashes};
}

async function load(build){
  const e=await loadEpisode(fixture);e.paths.build=build;
  await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:30});
  if(e.output.fps!==30||e.output.durationSeconds!==15||e.shots.map(s=>s.id).join('|')!=='pawls|callouts|ropes')
    fail('Graphic-overlays fixture timing/shot identity changed');
  const {count,units}=outputShotUnits(e,30,[]),categories=[0,0,0];
  for(const unit of units)for(const frame of unit.frames){
    if(frame.request.picture||frame.request.transition)fail('Picture/transition branch is no longer absent; classify separately before profiling');
    const n=(frame.request.annotations??[]).filter(a=>a.opacity>0&&a.opacity<1).length;
    if(n>2)fail(`More than two simultaneous annotation fades at frame ${frame.index}`);
    categories[n]++;
  }
  if(count!==450||categories.join('/')!=='320/105/25')fail(`Actual grid/fade groups changed: ${count} / ${categories.join('/')}`);
  return {e,categories};
}
async function armReport(e,renderWallMs){
  const manifestPath=join(e.paths.build,'silent-preview-manifest.json');
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  const mp4=join(e.paths.build,'silent-preview.mp4');
  if(manifest.count!==450||manifest.cache?.capturedFrames!==450||manifest.cache?.reusedFrames!==0)
    fail(`Arm is not a cold 450-frame capture: ${manifestPath}`);
  if(manifest.viewerApi!==28||manifest.hashes?.['/viewer.js']!==pins.viewer||
    manifest.hashes?.['/model/manifest.json']!==pins.model)fail('Arm viewer/model provenance differs from pins');
  const mp4Sha=await fileHash(mp4);if(mp4Sha!==manifest.outputSha256)fail('MP4 hash/provenance mismatch');
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_entries',
    'stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames:format=duration','-of','json',mp4]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  if(video?.nb_read_frames!=='450'||video.width!==960||video.height!==540||video.r_frame_rate!=='30/1'||
    probe.streams.some(s=>s.codec_type==='audio')||Number(probe.format.duration)!==15)
    fail('MP4 stream/frame properties differ');
  const signature=Buffer.from([137,80,78,71,13,10,26,10]);
  const frames=[];for(let index=0;index<450;index++){
    const path=join(manifest.dir,`${String(index).padStart(6,'0')}.png`);
    const bytes=await readFile(path);
    if(!bytes.subarray(0,8).equals(signature)||bytes.readUInt32BE(16)!==960||bytes.readUInt32BE(20)!==540)
      fail(`PNG dimensions/signature differ at frame ${index}`);
    frames.push({index,path,sha256:await fileHash(path)});
  }
  const decoded=await command('ffmpeg',['-v','error','-i',mp4,'-f','framemd5','-']);
  const decodedFrameMd5=decoded.split('\n').filter(line=>/^\d+,\s*\d+,/.test(line))
    .map(line=>line.trim().split(',').at(-1).trim());
  if(decodedFrameMd5.length!==450)fail(`Decoded MP4 has ${decodedFrameMd5.length} frame hashes, expected 450`);
  return {renderWallMs,manifestPath,manifestSha256:await fileHash(manifestPath),mp4,mp4Sha256:mp4Sha,
    assemblyDir:manifest.dir,cache:manifest.cache,browser:manifest.browser,probe,decodedFrameMd5,frames};
}
function distribution(values){
  if(!values.length)return null;
  const sorted=values.toSorted((a,b)=>a-b),pick=p=>sorted[Math.ceil(p*sorted.length)-1];
  return {count:values.length,totalMs:values.reduce((a,b)=>a+b,0),p50Ms:pick(.5),p90Ms:pick(.9),p95Ms:pick(.95),maxMs:sorted.at(-1)};
}
function summarize(frames){
  const groups={};for(const n of [0,1,2]){
    const list=frames.filter(f=>f.partialFades===n),names=new Set(list.flatMap(f=>Object.keys(f.nodeMs)));
    const node={};for(const name of names)node[name]=distribution(list.map(f=>f.nodeMs[name]??0));
    const pages=new Set(list.flatMap(f=>Object.keys(f.pageMs))),page={};
    for(const name of pages)page[name]=distribution(list.map(f=>f.pageMs[name]??0));
    groups[n]={count:list.length,total:distribution(list.map(f=>f.totalMs)),node,page,
      slowest:list.toSorted((a,b)=>b.totalMs-a.totalMs).slice(0,8).map(f=>({index:f.index,shotId:f.shotId,totalMs:f.totalMs}))};
  }
  const first=frames[0],last=frames.at(-1);
  return {groups,firstToLastFinalScreenshotMs:last.finalScreenshotMonotonicMs-first.finalScreenshotMonotonicMs,
    captureOnlySpanMs:last.endedMonotonicMs-first.startedMonotonicMs};
}
function procStat(text){
  const end=text.lastIndexOf(')');if(end<0)return null;
  const fields=text.slice(end+1).trim().split(/\s+/);
  return fields.length>=20?{state:fields[0],ppid:Number(fields[1]),starttime:fields[19]}:null;
}
async function procSnapshot(){
  // PID/PPID traversal sees children of every browser thread; /proc task
  // leader children alone can omit Chromium descendants. No cmdline or env.
  const rows=[];
  for(const item of await readdir('/proc',{withFileTypes:true})){
    if(!item.isDirectory()||!/^\d+$/.test(item.name))continue;
    const pid=Number(item.name);
    try{const stat=procStat(await readFile(`/proc/${pid}/stat`,'utf8'));
      if(stat&&Number.isInteger(stat.ppid))rows.push({pid,...stat});
    }catch(error){if(!['ENOENT','ESRCH','EACCES','EPERM'].includes(error.code))throw error;}
  }
  return rows;
}
function ownedTree(processes,owned){
  const byPid=new Map(processes.map(p=>[p.pid,p])),tree=new Set(),root=byPid.get(process.pid);
  if(root&&(!owned.has(root.pid)||owned.get(root.pid).starttime===root.starttime))tree.add(root.pid);
  for(const [pid,identity] of owned)if(byPid.get(pid)?.starttime===identity.starttime)tree.add(pid);
  for(let changed=true;changed;){
    changed=false;for(const p of processes)if(tree.has(p.ppid)&&!tree.has(p.pid)){tree.add(p.pid);changed=true;}
  }
  for(const p of processes)if(tree.has(p.pid))owned.set(p.pid,{pid:p.pid,ppid:p.ppid,starttime:p.starttime});
  return processes.filter(p=>tree.has(p.pid)&&owned.get(p.pid)?.starttime===p.starttime);
}
async function ownedMetrics(p){
  const {pid,ppid,starttime,state}=p;
  if(state==='Z')return {knownZombie:{pid,ppid,starttime}};
  try{
    const [status,fds]=await Promise.all([readFile(`/proc/${pid}/status`,'utf8'),readdir(`/proc/${pid}/fd`)]);
    return {row:{pid,ppid,starttime,rssKiB:Number(/^VmRSS:\s+(\d+) kB/m.exec(status)?.[1]??0),fds:fds.length}};
  }catch(error){
    if(!['ENOENT','ESRCH','EACCES','EPERM'].includes(error.code))throw error;
    let current;
    try{current=procStat(await readFile(`/proc/${pid}/stat`,'utf8'));}
    catch(statError){
      if(['ENOENT','ESRCH'].includes(statError.code))return {teardownRace:{pid,ppid,starttime,metricError:error.code,attested:'gone'}};
      throw error;
    }
    if(!current)throw error;
    if(current.starttime!==starttime)return {teardownRace:{pid,ppid,starttime,metricError:error.code,
      attested:'identity-changed',observedStarttime:current.starttime}};
    if(current.state==='Z')return {teardownRace:{pid,ppid,starttime,metricError:error.code,attested:'zombie'}};
    throw error; // A still-live denied identity is not a valid measurement.
  }
}
async function treeResourceSnapshot(owned){
  const current=ownedTree(await procSnapshot(),owned),rows=[],teardownRaces=[],knownZombies=[];
  for(const p of current){const m=await ownedMetrics(p);
    if(m.row)rows.push(m.row);
    if(m.teardownRace)teardownRaces.push(m.teardownRace);
    if(m.knownZombie)knownZombies.push(m.knownZombie);
  }
  const root=rows.find(r=>r.pid===process.pid),rssKiB=rows.reduce((n,r)=>n+r.rssKiB,0),
    fdCount=rows.reduce((n,r)=>n+r.fds,0),rootRssKiB=root?.rssKiB??0,rootFdCount=root?.fds??0;
  return {processCount:rows.length,rssKiB,fdCount,rootRssKiB,rootFdCount,
    descendantRssKiB:rssKiB-rootRssKiB,descendantFdCount:fdCount-rootFdCount,
    teardownRaces,knownZombies};
}
function resourceSampler(){
  const metrics=['processCount','rssKiB','fdCount','rootRssKiB','rootFdCount','descendantRssKiB','descendantFdCount'];
  const peak=Object.fromEntries(metrics.map(key=>[key,0])),errors=[],teardownRaces=[],knownZombies=[],owned=new Map();
  let pending=Promise.resolve(),samples=0;
  const timer=setInterval(()=>{pending=pending.then(async()=>{
    const sample=await treeResourceSnapshot(owned);samples++;
    for(const key of metrics)peak[key]=Math.max(peak[key],sample[key]);
    teardownRaces.push(...sample.teardownRaces);knownZombies.push(...sample.knownZombies);
  }).catch(async error=>{
    const path=error.path??null,pid=Number(/\/proc\/(\d+)\//.exec(path??'')?.[1]??0)||null;
    errors.push({atUtc:new Date().toISOString(),code:error.code??null,path,pid,
      starttime:pid?owned.get(pid)?.starttime??null:null,message:error.message});
  });},500);
  return async()=>{
    clearInterval(timer);await pending;
    const counts={};for(const error of errors){const key=`${error.pid??'unknown'}:${error.starttime??'unknown'}`;counts[key]=(counts[key]??0)+1;}
    return {complete:errors.length===0,peaksAreLowerBounds:errors.length>0,samples,peak,
      sampleErrors:errors,unreadableIdentityCounts:counts,teardownRaces,knownZombies};
  };
}
async function checkHookCounts(profile){
  // Unit-only simulation of the 0/1/2-fade call topology; fake screenshot
  // bytes, no page, browser, render or project output. Reset before real use.
  const fakePage={screenshot:async()=>Buffer.from('hook-count-only')};
  for(const n of [0,1,2]){
    profile.startFrame({index:n,time:n,request:{shotId:'hook-count-only',
      annotations:Array.from({length:n},(_,index)=>({index,opacity:.5}))}});
    const subsets=n?2**n:0;
    for(let k=0;k<1+subsets;k++)profile.count('setFrame');
    for(let k=0;k<subsets;k++){
      profile.count('repaint');await profile.screenshot(fakePage,'annotationSubset');
    }
    if(n)profile.count('annotationBlend');
    await profile.screenshot(fakePage,'final');profile.endFrame();
    const calls=profile.frames.at(-1).calls;
    for(const [key,want] of [['setFrame',1+subsets],['repaint',subsets],
      ['annotationSubsetScreenshot',subsets],['annotationBlend',n?1:0],['finalScreenshot',1]])
      if((calls[key]??0)!==want)fail(`Hook count check ${n} fades: ${key}=${calls[key]??0}, expected ${want}`);
  }
  profile.reset();
}

// --prepare checks pins, exact source anchors, private-module imports/syntax,
// and the 450-frame classification. It opens no browser and performs no render.
const prepareOnly=process.argv[2]==='--prepare';
if(!prepareOnly&&process.argv[2]?.startsWith('--'))fail('Unknown profile mode');
const actualPins=await checkPins();
const output=resolve((prepareOnly?process.argv[3]:process.argv[2])??join(dirname(fixture),'_build',
  `compositing-profile-${prepareOnly?'prepare-':''}${new Date().toISOString().replaceAll(/[:.]/g,'-')}`));
await mkdir(output); // Refuse an existing root; preserve every previous run.
const reportPath=join(output,'report.json'),report={schema:'compositing-profile/1',status:'running',
  pins:actualPins,fixture,viewer,width:960,height:540,fps:30,expectedFadeGroups:[320,105,25],arms:{},comparisons:null};
const persist=()=>writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
await persist();
try{
  // Private instrumentation is prepared and syntax/import checked *before*
  // even the plain 450-frame arm, so a stale anchor cannot waste that arm.
  const {privateSrc,hashes}=await privateCopy(output);report.instrumentation={privateSrc,hashes};
  new Script(await readFile(join(privateSrc,'film.js'),'utf8'),{filename:join(privateSrc,'film.js')});
  const {render:instrumentedRender}=await import(pathToFileURL(join(privateSrc,'render.mjs')).href);
  const {profile}=await import(pathToFileURL(join(privateSrc,'profile-hook.mjs')).href);
  if(typeof instrumentedRender!=='function'||!profile?.frames)fail('Private instrumentation imports are incomplete');
  await checkHookCounts(profile);
  const plainArmStart=now();let prepStart=now();const first=await load(join(output,'plain-build'));
  report.preflightPlainMs=now()-prepStart;
  report.actualFadeGroups=first.categories;
  report.prepare={anchorsChecked:true,privateImportsChecked:true,filmSyntaxChecked:true,hookCountsChecked:true,
    fullRenderRequired:!prepareOnly};
  if(prepareOnly){report.status='prepared-no-browser';await persist();console.log(`Prepared without browser: ${reportPath}`);}
  else{
  await persist();
  const t0=now(),stopPlain=resourceSampler();let plainRenderEnd;
  try{await productRender(first.e,{viewer,width:960,fps:30,audio:null,label:'silent-preview'});plainRenderEnd=now();}
  finally{report.arms.plainResources=await stopPlain();}
  report.arms.plain=await armReport(first.e,plainRenderEnd-t0);
  report.arms.plain.loadPrepareThroughRenderMs=plainRenderEnd-plainArmStart;
  report.arms.plain.endToEndIncludingEvidenceMs=now()-plainArmStart;
  await persist();
  if(!report.arms.plainResources.complete)fail('Plain-arm resource peaks are incomplete lower bounds; stop before instrumented arm');
  const instrumentedArmStart=now();prepStart=now();const second=await load(join(output,'instrumented-build'));
  report.preflightInstrumentedMs=now()-prepStart;
  const t1=now(),stopInstrumented=resourceSampler();let instrumentedRenderEnd;
  try{await instrumentedRender(second.e,{viewer,width:960,fps:30,audio:null,label:'silent-preview'});instrumentedRenderEnd=now();}
  finally{report.arms.instrumentedResources=await stopInstrumented();}
  report.arms.instrumented=await armReport(second.e,instrumentedRenderEnd-t1);
  report.arms.instrumented.loadPrepareThroughRenderMs=instrumentedRenderEnd-instrumentedArmStart;
  report.arms.instrumented.endToEndIncludingEvidenceMs=now()-instrumentedArmStart;
  if(!report.arms.instrumentedResources.complete)fail('Instrumented-arm resource peaks are incomplete lower bounds');
  if(profile.frames.length!==450)fail(`Instrumented per-frame records: ${profile.frames.length}, expected 450`);
  const groups=[0,1,2].map(n=>profile.frames.filter(f=>f.partialFades===n).length);
  if(groups.join('/')!=='320/105/25')fail(`Instrumented category drift: ${groups.join('/')}`);
  report.instrumentation.stages=profile.stages;
  report.instrumentation.counts=profile.counts;
  report.instrumentation.frames=profile.frames;
  for(const [name,want] of [['setFrame',760],['repaint',310],['annotationSubsetScreenshot',310],
    ['finalScreenshot',450],['annotationBlend',130]])
    if(profile.counts[name]!==want)fail(`Instrumentation call count ${name}=${profile.counts[name]}, expected ${want}`);
  report.instrumentation.summary=summarize(profile.frames);
  report.instrumentation.overheadMs=report.arms.instrumented.renderWallMs-report.arms.plain.renderWallMs;
  report.instrumentation.overheadFraction=report.instrumentation.overheadMs/report.arms.plain.renderWallMs;
  report.instrumentation.overheadCaution=Math.abs(report.instrumentation.overheadFraction)>.2;
  report.instrumentation.timingSemantics='Browser page subphases nest within Node awaited calls; screenshot wall includes browser capture, PNG encoding and transfer, not isolated transfer.';
  report.comparisons={sameMp4Sha256:report.arms.plain.mp4Sha256===report.arms.instrumented.mp4Sha256,
    sameDecodedVideoFrames:report.arms.plain.decodedFrameMd5.every((md5,i)=>md5===report.arms.instrumented.decodedFrameMd5[i]),
    differingFrames:report.arms.plain.frames.filter((f,i)=>f.sha256!==report.arms.instrumented.frames[i].sha256)
      .map((f)=>f.index)};
  report.status=report.comparisons.differingFrames.length?'invalid-pixel-drift':'exact-png-pass';
  await persist();
  if(report.status!=='exact-png-pass')fail(`Instrumentation changed PNG pixels at ${report.comparisons.differingFrames.join(',')}`);
  console.log(`Exact 450/450 PNG equality; report ${reportPath}`);
  }
}catch(error){report.status='failed';report.error={name:error.name,message:error.message,stack:error.stack};await persist();throw error;}
