// Disposable visual study commissioned by the pilot: no stable format or spec.
// Reuses source pinning and existing narration; does not change normal rendering.
import {readFile,realpath,mkdir,copyFile,link,rm} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
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
const credit=/©|copyright|licen[cs]e|vibecoded|made with|created by|written by/i;
assert.ok(!credit.test(r.narration+full),'Film content contains a credit marker');
const build=resolve(base,'_build');await mkdir(build,{recursive:true});
const html=await readFile(new URL('./stage.html',import.meta.url),'utf8');
const identity=hash(JSON.stringify({r,sources,html,script:await fileHash(fileURLToPath(import.meta.url))}));
const frames=resolve(build,'frames',identity.slice(0,16));await mkdir(frames,{recursive:true});
const browser=await chromium.launch({headless:true});
let checked=0,captured=0;
try{
  const page=await browser.newPage({viewport:{width:r.output.width,height:r.output.height}});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.setContent(html);
  await page.evaluate(({background,foreground})=>{
    document.body.style.background=background;document.body.style.color=foreground;
  },r.palette);
  await page.evaluate(()=>document.fonts.ready);
  const state=t=>{
    const count=Math.floor(ending.length*Math.max(0,Math.min(1,(t-from)/(to-from))));
    const text=fixed+ending.slice(0,count);
    return {text,html:hljs.highlight(text,{language:'python',ignoreIllegals:true}).value,
      cursor:t>=from&&t<to};
  };
  async function pose(t){
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
  await pose(0);const still=await page.screenshot();
  await pose(from-1);assert.ok(still.equals(await page.screenshot()),'The reading hold must be completely still');
  await pose((from+to)/2);const typing=await page.screenshot();
  await pose(to+.5);await pose((from+to)/2);assert.ok(typing.equals(await page.screenshot()),'Typing must replay exactly');
  for(const [name,time] of [['opening',0],['ending',(from+to)/2],['complete',to+.5]]){
    await pose(time);await page.screenshot({path:resolve(build,name+'.png')});
  }
  const cache=new Map(),count=r.output.fps*r.output.durationSeconds;
  assert.ok(Number.isInteger(count));
  for(let i=0;i<count;i++){
    const t=i/r.output.fps,key=JSON.stringify(state(t));
    const file=resolve(frames,String(i).padStart(6,'0')+'.png');
    // Only this experiment's generated frame is replaced on rerun.
    await rm(file,{force:true});
    if(cache.has(key))await link(cache.get(key),file);
    else {await pose(t);await page.screenshot({path:file});cache.set(key,file);captured++;}
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
  await json(resolve(build,'experiment-manifest.json'),{status:'visual experiment, not a ratified format',recipe:r,identity,sources,
    omittedRanges:[[8,195],[207,248]],sourceText:full,audio:{reusedFrom:mix,sha256:audio.mixSha256,records:audio.records},
    output,sha256:await fileHash(output),subtitles:{file:srt,sha256:await fileHash(srt),burnedIn:false},probe,
    browser:browser.version(),checks:{staticReadingHold:true,pixelReplay:true,noModelOrCaptions:true,poses:checked,uniqueFrames:captured}});
  console.log(output);
}finally{await browser.close();}
