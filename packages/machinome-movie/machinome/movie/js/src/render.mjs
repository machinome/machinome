import {createServer} from 'node:http';
import {readFile,writeFile,mkdir,copyFile,stat,rename} from 'node:fs/promises';
import {resolve,dirname,extname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {chromium} from 'playwright';
import {frameAt,srt} from './timeline.mjs';
import {contained,requiredViewerApi,viewerApiRefusal} from './episode.mjs';
import {fileHash,hash,json,command} from './util.mjs';

const here=dirname(fileURLToPath(import.meta.url));
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
  const hashes={};for(const [url,file]of paths)hashes[url]=await fileHash(file);
  return {paths,hashes};
}

export async function browserSession(e,viewer,width,captions,action) {
  const {paths,hashes}=await stage(e,viewer);
  const height=Math.round(e.output.height*width/e.output.width/2)*2;
  const initial=frameAt(e,0,captions);
  const required=requiredViewerApi(e);
  const cfg={style:e.style,series:e.series??e.title,initial,requiredViewerApi:required,viewerRefusal:viewerApiRefusal(required,'{declared}')};
  const errors=[];
  const server=createServer(async(req,res)=>{
    try{
      const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
      if(path==='/config.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(cfg));return;}
      if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
      const file=paths.get(path);if(!file){res.writeHead(404);res.end('Not found');return;}
      res.setHeader('Content-Type',({'.js':'text/javascript','.html':'text/html','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg'}[extname(file)])??'application/octet-stream');
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
    // override replaces frame fields for preview-only comparison frames.
    async function pose(t,override={}){
      if(errors.length)throw new Error(errors.join('\n'));
      const f={...frameAt(e,t,captions),progress:t/e.output.durationSeconds,...override};
      const observed=await page.evaluate(f=>window.film.setFrame(f),f);
      for(const k of ['camera','target'])for(let i=0;i<3;i++)if(Math.abs(observed[k][i]-f.view[k][i])>1e-6)throw new Error('Viewer did not adopt requested camera');
      const canvasSize=await page.locator('#stage canvas').boundingBox(),stageSize=await page.locator('#stage').boundingBox();
      if(!canvasSize||canvasSize.height<stageSize.height*.98||canvasSize.width<stageSize.width*.98)throw new Error('Viewer canvas does not fill the film stage');
      if(f.code){
        const fits=await page.locator('#source').evaluate(el=>el.scrollHeight<=el.clientHeight&&el.scrollWidth<=el.clientWidth);
        if(!fits)throw new Error(`Source excerpt overflows the panel: ${f.shotId}; select fewer lines`);
        if(await page.locator('#source-code').textContent()!==f.code.text)throw new Error('Displayed code differs from source');
      }
      for(const drawn of f.annotations?observed.annotations:[]){
        const cue=f.annotations.find(a=>a.index===drawn.index),stage=observed.stage,frame=observed.frame;
        const name=`${f.shotId} #${drawn.index}${cue.text===undefined?` (${cue.kind})`:` '${cue.text}'`} at ${t.toFixed(2)} s`;
        const p=drawn.anchor;
        if(!p||p.x<stage.x||p.x>stage.x+stage.width||p.y<stage.y||p.y>stage.y+stage.height)throw new Error(`Annotation target is not on screen: ${name}`);
        const box=drawn.text;
        if(box&&(box.x<-.5||box.y<-.5||box.x+box.width>frame.width+.5||box.y+box.height>frame.height+.5))throw new Error(`Annotation text leaves the frame: ${name}`);
      }
      frames++;return Object.assign(f,{observed});
    }
    const info={width,height,browser:browser.version(),viewerApi:await page.evaluate(()=>window.film.apiVersion),hashes,requiredViewerApi:required};
    const result=await action({page,pose,info});
    if(errors.length)throw new Error(errors.join('\n'));
    return {...result,...info,framesChecked:frames};
  }finally{await browser?.close();await new Promise(r=>server.close(r));}
}

export async function preview(e,{viewer,width=960,captions=[]}) {
  const dir=resolve(e.paths.build,'preview');await mkdir(dir,{recursive:true});
  const result=await browserSession(e,viewer,width,captions,async({page,pose})=>{
    // Highlights first, while every material is pristine: the same instant
    // without its cue, with it, without it, with it. The cue must change the
    // pixels, restore() must return them exactly, and re-applying must match.
    const highlightChecks=[];
    for(const shot of e.shots)for(const [index,cue] of (shot.highlight??[]).entries()){
      const t=shot.start+(cue.from+cue.to)/2,capture=async override=>{await pose(t,override);return page.screenshot();};
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
    return {samples,pixelReplay:true,invalidCameraPreserved:true,...(highlightChecks.length?{highlightChecks}:{})};
  });
  await json(resolve(dir,'report.json'),result);
  // A contact sheet for quickly inspecting the chosen shots, then individual PNGs.
  await command('ffmpeg',['-y','-v','error','-pattern_type','glob','-i',resolve(dir,'*.png'),'-vf',`scale=480:-1,tile=3x${Math.ceil(result.samples.length/3)}`,'-frames:v','1',resolve(e.paths.build,'storyboard.jpg')]);
  return result;
}

export async function render(e,{viewer,width=e.output.width,fps=e.output.fps,audio=null,label='rehearsal'}) {
  const captions=audio?.captions??[];
  const report=await browserSession(e,viewer,width,captions,async({page,pose,info})=>{
    const identity=hash(JSON.stringify({episode:e,hashes:info.hashes,browser:info.browser,width,fps,captions,
      renderer:await fileHash(resolve(here,'render.mjs')),timeline:await fileHash(resolve(here,'timeline.mjs')),
      sourceRenderer:await fileHash(resolve(here,'code.mjs')),dependencies:await fileHash(resolve(here,'../package-lock.json'))}));
    const dir=resolve(e.paths.build,'frames',identity.slice(0,16));await mkdir(dir,{recursive:true});
    const count=e.output.durationSeconds*fps;
    if(!Number.isInteger(count))throw new Error('Frame count is not integral');
    const started=Date.now();
    for(let i=0;i<count;i++){
      const file=resolve(dir,`${String(i).padStart(6,'0')}.png`);
      try{if((await stat(file)).size>0)continue;}catch(error){if(error.code!=='ENOENT')throw error;}
      await pose(i/fps);
      await writeFile(file+'.tmp',await page.screenshot());
      await rename(file+'.tmp',file);
      if(i%90===0)console.log(`Frames ${i+1}/${count} · ${((Date.now()-started)/1000).toFixed(0)}s elapsed`);
    }
    return {identity,dir,count};
  });
  const output=resolve(e.paths.build,`${label}.mp4`);
  const args=['-y','-v','error','-framerate',String(fps),'-start_number','0','-i',resolve(report.dir,'%06d.png')];
  if(audio)args.push('-i',audio.mix,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','192k');
  args.push('-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart','-t',String(e.output.durationSeconds),output);
  console.log('Encoding '+output);await command('ffmpeg',args);
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',output]));
  const video=probe.streams.find(s=>s.codec_type==='video');
  if(Number(video.nb_read_frames)!==report.count||video.width!==report.width||video.height!==report.height)throw new Error('Encoded video does not match requested frames/dimensions');
  if(audio&&!probe.streams.some(s=>s.codec_type==='audio'))throw new Error('Encoded video has no audio');
  await copyFile(resolve(report.dir,`${String(Math.min(report.count-1,Math.floor(Math.min(10,e.output.durationSeconds*.5)*fps))).padStart(6,'0')}.png`),resolve(e.paths.build,'thumbnail.png'));
  const subtitles=audio?resolve(e.paths.build,`${label}.srt`):null;
  if(subtitles)await writeFile(subtitles,srt(captions));
  const releaseReady=Boolean(e.release.simulationUrl&&e.release.sourceUrl);
  const description=await readFile(resolve(dirname(e.paths.production),e.release.descriptionTemplate),'utf8');
  await writeFile(resolve(e.paths.build,'description.md'),description
    .replaceAll('{{simulationUrl}}',e.release.simulationUrl??'[PUBLIC SIMULATION URL PENDING]')
    .replaceAll('{{sourceUrl}}',e.release.sourceUrl??'[PUBLIC SOURCE URL PENDING]'));
  const gitHead=async cwd=>(await command('git',['rev-parse','HEAD'],{cwd})).trim();
  const workflow=await gitHead(resolve(here,'..'));
  const project=await gitHead(e.paths.repository);
  const font=await command('fc-match',['-f','%{file}','DejaVu Sans']).catch(()=>null);
  const fontRecord=font?{path:font,sha256:await fileHash(font)}:null;
  const codeFont=await command('fc-match',['-f','%{file}','DejaVu Sans Mono']).catch(()=>null);
  const codeFontRecord=codeFont?{path:codeFont,sha256:await fileHash(codeFont)}:null;
  await json(resolve(e.paths.build,`${label}-manifest.json`),{...report,fps,output,outputSha256:await fileHash(output),
    audio:audio?.records??[],subtitles:subtitles?{file:subtitles,sha256:await fileHash(subtitles),burnedIn:false}:null,episode:e,probe,releaseReady,
    provenance:{workflowHead:workflow,projectHead:project,font:fontRecord,codeFont:codeFontRecord,
      episodeSha256:await fileHash(e.paths.episode),productionSha256:await fileHash(e.paths.production),
      ffmpeg:(await command('ffmpeg',['-version'])).split('\n')[0]}});
  return output;
}
