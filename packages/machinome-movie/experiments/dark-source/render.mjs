// Disposable visual study commissioned by the pilot: no stable format or spec.
// Reuses source pinning and existing narration; does not change normal rendering.
import {readFile,realpath,mkdir,copyFile,link,rm} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createServer} from 'node:http';
import assert from 'node:assert/strict';
import {chromium} from 'playwright';
import hljs from 'highlight.js/lib/core';
import {loadEpisode,parseSource,contained} from '../../src/episode.mjs';
import {loadSourceCode} from '../../src/code.mjs';
import {hash,fileHash,command,json} from '../../src/util.mjs';

const recipe=await realpath(resolve(process.argv[2]??''));
if(!process.argv[2])throw new Error('Pass the project-owned experimental episode.yaml');
const base=dirname(recipe),r=parseSource(await readFile(recipe,'utf8'));
assert.equal(r.format,'machinome-visual-experiment/dark-source');
const parent=await loadEpisode(resolve(base,r.referenceEpisode));
assert.ok(contained(parent.paths.repository,base),'Experiment must be in the same project');
assert.equal(r.narration,parent.shots[0].narration,'Narration changed: cannot reuse this take');
assert.equal(parent.shots.length,1);
assert.equal(r.output.durationSeconds,parent.output.durationSeconds);
const audio=JSON.parse(await readFile(resolve(parent.paths.build,'audio-manifest.json'),'utf8'));
const mix=resolve(parent.paths.build,'narration.wav');
assert.equal(await fileHash(mix),audio.mixSha256);
const sources=await loadSourceCode({...parent,paths:{...parent.paths,production:recipe},sourceCode:r.sourceCode});
// Restore indentation removed by the reusable excerpt loader. These are literal
// ranges from one file, not a rewritten tutorial; omission markers are editorial.
const original=s=>s.text.split('\n').map(line=>' '.repeat(s.dedent)+line).join('\n');
const fixed=original(sources.imports)+'\n\n# …\n\n'+original(sources.architecture)+'\n    # …\n\n';
const ending=original(sources.ending);
const {from,to}=r.endingMotion;
assert.ok(from>=0&&to>from&&to<r.output.durationSeconds);
const full=fixed+ending;
const sequence=r.sequence??[{kind:'code',start:0,end:r.output.durationSeconds}];
let end=0;
for(const shot of sequence){assert.equal(shot.start,end);assert.ok(shot.end>shot.start);assert.ok(['code','machine'].includes(shot.kind));end=shot.end;}
assert.equal(end,r.output.durationSeconds);
const codeShot=sequence.find(s=>s.kind==='code');assert.ok(codeShot&&from>=codeShot.start&&to<codeShot.end);
const credit=/©|copyright|licen[cs]e|vibecoded|made with|created by|written by/i;
assert.ok(!credit.test(r.narration+full),'Film content contains a credit marker');
const build=resolve(base,'_build');await mkdir(build,{recursive:true});
const html=await readFile(new URL('./stage.html',import.meta.url),'utf8');
const identity=hash(JSON.stringify({r,sources,html,script:await fileHash(fileURLToPath(import.meta.url))}));
const frames=resolve(build,'frames',identity.slice(0,16));await mkdir(frames,{recursive:true});
let server,modelPage;
const modelHashes={};
const browser=await chromium.launch({headless:true,args:['--use-angle=swiftshader','--enable-unsafe-swiftshader']});
let checked=0,captured=0;
try{
  const page=await browser.newPage({viewport:{width:r.output.width,height:r.output.height}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.setContent(html);
  await page.evaluate(({background,foreground})=>{
    document.body.style.background=background;document.body.style.color=foreground;
  },r.palette);
  await page.evaluate(()=>document.fonts.ready);
  if(sequence.some(s=>s.kind==='machine')){
    assert.ok(process.argv[3]&&!process.argv[3].startsWith('--'),'Supply a viewer bundle for the sequence');
    const viewer=await realpath(resolve(process.argv[3]));
    const manifest=JSON.parse(await readFile(parent.paths.manifest,'utf8'));
    const paths=new Map([['/viewer.js',viewer],['/model/manifest.json',parent.paths.manifest]]);
    function collect(value){
      if(typeof value==='string'&&/\.(stl|png|jpg|jpeg|webp|svg)$/i.test(value)){
        const file=resolve(dirname(parent.paths.manifest),value);assert.ok(contained(dirname(parent.paths.manifest),file));paths.set('/model/'+value,file);
      }else if(value&&typeof value==='object')Object.values(value).forEach(collect);
    }
    collect(manifest);for(const [url,path] of paths)modelHashes[url]=await fileHash(path);
    server=createServer(async(req,res)=>{
      try{
        const path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
        if(path==='/'){res.setHeader('Content-Type','text/html');res.end(`<!doctype html><html><style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:${r.palette.background}}#viewport{position:absolute;inset:4%}#stage{width:100%;height:100%}canvas{display:block}</style><div id="viewport"><div id="stage"></div></div><script src="/viewer.js"></script></html>`);return;}
        if(path==='/favicon.ico'){res.writeHead(204);res.end();return;}
        const file=paths.get(path);if(!file){res.writeHead(404);res.end();return;}
        res.setHeader('Content-Type',path.endsWith('.js')?'text/javascript':path.endsWith('.json')?'application/json':'application/octet-stream');res.end(await readFile(file));
      }catch(error){errors.push(error.message);res.writeHead(500);res.end();}
    });
    await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
    modelPage=await browser.newPage({viewport:{width:r.output.width,height:r.output.height}});
    modelPage.on('pageerror',e=>errors.push(e.message));modelPage.on('requestfailed',q=>errors.push(q.url()));
    await modelPage.goto(`http://127.0.0.1:${server.address().port}/`);
    const first=sequence.find(s=>s.kind==='machine');
    await modelPage.evaluate(async({camera,target,fov})=>{
      window.viewer=await MachinomeViewer.mount('#stage','/model/manifest.json',{
        animation:'external',autoplay:false,driverControls:'none',partControls:'none',renderMode:'on-demand',
        up:[0,0,1],fov,view:{camera,target},time:0});
      window.hidden=[];
    },first);
  }
  const state=t=>{
    const count=Math.floor(ending.length*Math.max(0,Math.min(1,(t-from)/(to-from))));
    const text=fixed+ending.slice(0,count);
    return {text,html:hljs.highlight(text,{language:'python',ignoreIllegals:true}).value,
      cursor:t>=from&&t<to};
  };
  async function poseCode(t){
    const frame=state(t);
    await page.evaluate(f=>{
      document.querySelector('code').innerHTML=f.html;
      document.querySelector('#cursor').style.visibility=f.cursor?'visible':'hidden';
    },frame);
    assert.equal(await page.locator('code').textContent(),frame.text);
    assert.ok(await page.locator('pre').evaluate(el=>el.scrollWidth<=el.clientWidth&&el.scrollHeight<=el.clientHeight),'Code overflows');
    assert.equal(await page.locator('canvas,video,#caption').count(),0,'Code-only shot must have no competing animation or captions');
    assert.equal(errors.length,0,errors.join('\n'));checked++;
    return frame;
  }
  async function pose(t){
    const shot=sequence.find(s=>t>=s.start&&t<s.end);assert.ok(shot);
    if(shot.kind==='code'){await poseCode(t);return page;}
    const seconds=shot.simulation.from+(shot.simulation.to-shot.simulation.from)*(t-shot.start)/(shot.end-shot.start);
    await modelPage.evaluate(({shot,time})=>{
      const hidden=shot.hidden??[];
      if(JSON.stringify(window.hidden)!==JSON.stringify(hidden)){
        for(const path of window.hidden)window.viewer.setVisible(path,true);
        window.hidden=hidden;
        for(const path of window.hidden)window.viewer.setVisible(path,false);
      }
      window.viewer.setTime(time);window.viewer.setView({camera:shot.camera,target:shot.target});
    },{shot,time:seconds/parent.model.expectedDurationSeconds});
    assert.equal(await modelPage.locator('pre,code,#caption').count(),0);
    const box=await modelPage.locator('canvas').boundingBox();
    assert.ok(box.width>r.output.width*.85&&box.height>r.output.height*.85,'Model canvas must fill its scene');
    assert.equal(errors.length,0,errors.join('\n'));checked++;return modelPage;
  }
  await poseCode(codeShot.start);const still=await page.screenshot();
  await poseCode(from-1);assert.ok(still.equals(await page.screenshot()),'The reading hold must be completely still');
  await poseCode((from+to)/2);const typing=await page.screenshot();
  await poseCode(to+.5);await poseCode((from+to)/2);assert.ok(typing.equals(await page.screenshot()),'Typing must replay exactly');
  const samples=[['opening',0],['code',codeShot.start+.5],['ending',(from+to)/2],['complete',to+.5],['closing',r.output.durationSeconds-1]];
  for(const [name,time] of samples){
    const active=await pose(time);await active.screenshot({path:resolve(build,name+'.png')});
  }
  for(const shot of sequence.filter(s=>s.kind==='machine')){
    const a=await pose(shot.start+.1),before=await a.screenshot();
    const b=await pose(shot.start+.8),after=await b.screenshot();assert.ok(!before.equals(after),'Machine must visibly move');
    await pose(shot.start+.1);assert.ok(before.equals(await a.screenshot()),'Machine must replay exactly');
  }
  if(process.argv.includes('--preview')){console.log('Preview: '+build);process.exitCode=0;}
  else{
  const cache=new Map(),count=r.output.fps*r.output.durationSeconds;
  assert.ok(Number.isInteger(count));
  for(let i=0;i<count;i++){
    const t=i/r.output.fps,shot=sequence.find(s=>t>=s.start&&t<s.end);
    const key=shot.kind==='code'?JSON.stringify(state(t)):`machine-${i}`;
    const file=resolve(frames,String(i).padStart(6,'0')+'.png');
    // Only this experiment's generated frame is replaced on rerun.
    await rm(file,{force:true});
    if(cache.has(key))await link(cache.get(key),file);
    else {const active=await pose(t);await active.screenshot({path:file});cache.set(key,file);captured++;}
    if(i%120===0)console.log(`Frames ${i+1}/${count}`);
  }
  const output=resolve(build,'dark-source.mp4');
  await command('ffmpeg',['-y','-v','error','-framerate',String(r.output.fps),'-i',resolve(frames,'%06d.png'),'-i',mix,
    '-map','0:v:0','-map','1:a:0','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p',
    '-c:a','aac','-b:a','192k','-t',String(r.output.durationSeconds),'-movflags','+faststart',output]);
  const srt=resolve(build,'dark-source.srt');await copyFile(resolve(parent.paths.build,'captions.srt'),srt);
  const probe=JSON.parse(await command('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',output]));
  assert.deepEqual(probe.streams.map(s=>s.codec_type).sort(),['audio','video']);
  const video=probe.streams.find(s=>s.codec_type==='video');
  assert.equal(Number(video.nb_read_frames),count);assert.equal(video.width,r.output.width);assert.equal(video.height,r.output.height);
  await json(resolve(build,'experiment-manifest.json'),{status:'visual experiment, not a ratified format',recipe:r,identity,sources,sequence,modelHashes,
    omittedRanges:[[8,195],[207,248]],sourceText:full,audio:{reusedFrom:mix,sha256:audio.mixSha256,records:audio.records},
    output,sha256:await fileHash(output),subtitles:{file:srt,sha256:await fileHash(srt),burnedIn:false},probe,
    browser:browser.version(),checks:{staticReadingHold:true,pixelReplay:true,exclusiveCodeAndMachine:true,machineMotionChecked:Boolean(modelPage),noBurnedCaptions:true,poses:checked,uniqueFrames:captured}});
  console.log(output);
  }
}finally{await browser.close();if(server)await new Promise(resolve=>server.close(resolve));}
