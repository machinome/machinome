// Layer 8 (serial; Chromium, FFmpeg, a viewer double): the shot cache over a
// four-shot YAML episode, loaded as the command line loads it after every
// edit. A YAML shot is one chapter; the shots are a, b, c and d.
import {describe} from 'vitest';
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdir,readFile,readdir,rename,unlink,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import {render} from '../support/stage.mjs';
import {yamlProject} from '../support/yaml-project.mjs';
import {fileHash,hash} from '../../src/util.mjs';
import {outputShotUnits,assembleShotFrames,shotCacheRoot} from '../../src/shot-cache.mjs';
import {pcmWav,speechCacheEntry,spokenChapters} from '../../src/speech.mjs';

async function fixture(t,{files={}}={}){
  const project=await yamlProject(t,{manifest:{root:{name:'test'},animation:{loop:8}},files});
  const {dir}=project,viewer=join(dir,'viewer.js');
  await writeFile(viewer,`window.MachinomeViewer={async mount(selector,url,options){
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';
    document.querySelector(selector).append(canvas);let view={...options.view,up:options.up,fov:options.fov};
    return {apiVersion:28,setVisible(){},navigation(){return {}},
      setTime(t){canvas.style.background='rgb('+Math.round(t*200)+',90,160)'},
      setView(v){view={...view,...v}},
      view(){return {camera:{toArray:()=>view.camera},target:{toArray:()=>view.target},
        up:{toArray:()=>view.up},fov:view.fov}}};
  }};`);
  const common={narration:'Look.',direction:'Test.',camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]};
  const shot=(id,start,end,more={})=>({...common,id,start,end,simulation:{from:start,to:end},...more});
  const episode={format:'machinome-video-draft/0.4',title:'Cache test',series:'CACHE TEST',
    output:{width:640,height:360,fps:2,durationSeconds:8},model:{expectedDurationSeconds:8},
    style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    release:{descriptionTemplate:'description.md'},stills:{},clips:{},shots:[
      shot('a',0,2),shot('b',2,4,{overlays:[{from:0,to:2,position:'title',text:'BEFORE'}]}),
      shot('c',4,6,{transition:{kind:'wipe',duration:1}}),shot('d',6,8)]};
  // The episode as it stands now, loaded afresh; `at` puts it in another directory.
  const load=options=>project.film(episode,options);
  const run=async(options={},{at}={})=>render(await load({at}),{viewer,label:'incremental',audio:null,...options});
  return {project,dir,viewer,episode,load,run};
}

async function report(dir){return JSON.parse(await readFile(join(dir,'_build','incremental-manifest.json'),'utf8'));}

test('a local title edit recaptures its shot and incoming join, but reuses distant shots',async t=>{
  const {dir,episode,run}=await fixture(t);
  await run();
  const first=await report(dir);
  await run();
  const warm=await report(dir);
  episode.shots[1].overlays[0].text='AFTER';
  await run();
  const edited=await report(dir);
  if(!edited.cache){
    const files=await readdir(edited.dir);
    console.log(`old whole-episode renderer: first=${first.dir}, unchanged=${warm.dir}, edited=${edited.dir}; edited directory has ${files.filter(f=>f.endsWith('.png')).length} newly captured PNGs for 16 output frames`);
  }
  assert.equal(edited.framesChecked,8,'only B and its dependent incoming-transition C are posed');
  assert.equal(warm.cache?.reusedFrames,16,'an unchanged rerender reuses every verified shot frame');
  assert.deepEqual(edited.cache?.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',4,0],['c',4,0],['d',0,4]]);
  assert.equal(edited.cache?.capturedFrames,8);
  assert.equal(edited.cache?.reusedFrames,8);
});

test('a B-only lens edit does not turn a viewer refusal reason into a global pixel dependency',async t=>{
  const {dir,episode,run}=await fixture(t);
  await run();
  episode.cameras.b={...episode.cameras.a,fov:24};
  episode.shots[1].camera=[{at:0,preset:'b'}];
  await run();
  const edited=await report(dir);
  assert.equal(edited.framesChecked,8,'B and its following join change, not A and D');
  assert.deepEqual(edited.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',4,0],['c',4,0],['d',0,4]]);
});

test('every incremental PNG equals a separately cold film across the first reused-shot gap',async t=>{
  const {dir,episode,run}=await fixture(t,{files:{'machine.py':'water = 1\nturn(water)\ndrive = 1\nreturn drive\n'}});
  episode.sourceCode={sampleA:{file:'machine.py',lines:[1,2]},sampleB:{file:'machine.py',lines:[3,4]}};
  episode.shots[0].code={snippet:'sampleA',typing:[{from:0,to:1.5,throughLine:2}]};
  episode.shots[1].code={snippet:'sampleB',typing:[{from:0,to:1.5,throughLine:4}]};
  episode.shots[1].overlays=[
    {from:0,to:2,position:'title',text:'BEFORE',enter:{kind:'fade',duration:1}},
    {from:0,to:2,position:'lower-third',text:'ONE TWO',reveal:{timing:'even',duration:1}}];
  await run();
  episode.shots[1].overlays[0].text='AFTER';
  await run();
  const incremental=await report(dir);
  assert.equal(incremental.cache.reusedFrames,8);
  assert.equal(incremental.cache.capturedFrames,8);
  await run({},{at:'cold'});
  const fresh=JSON.parse(await readFile(join(dir,'cold','_build','incremental-manifest.json'),'utf8'));
  assert.equal(fresh.cache.capturedFrames,16);
  for(let i=0;i<16;i++){
    const name=`${String(i).padStart(6,'0')}.png`;
    assert.equal(await fileHash(join(incremental.dir,name)),await fileHash(join(fresh.dir,name)),`global frame ${i}`);
  }
  assert.equal(incremental.outputSha256,fresh.outputSha256,'the identical frame sequence encodes identically');
});

describe('each join depends on its outgoing shot, while an ordinary cut does not',()=>{
  for(const kind of ['cut','fade','dissolve','wipe','slide'])test(kind,async sub=>{
    const {dir,episode,run}=await fixture(sub);
    if(kind==='cut')delete episode.shots[2].transition;
    else episode.shots[2].transition={kind,duration:1};
    await run();
    episode.shots[1].overlays[0].text='CHANGED';
    await run();
    const edited=await report(dir),changed=kind==='cut'?4:8;
    assert.equal(edited.framesChecked,changed);
    assert.deepEqual(edited.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
      [['a',0,4],['b',4,0],['c',kind==='cut'?0:4,kind==='cut'?4:0],['d',0,4]]);
  });
});

// A still of one colour, declared in the episode (not committed).
function addStill(episode,dir,name,color){
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i',`color=c=${color}:s=16x16`,'-frames:v','1',join(dir,`${name}.png`)]);
  episode.stills[name]={file:`${name}.png`,credit:'Test',rights:'Own',upscale:100};
}
function addClip(episode,dir,name,color){
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i',`color=c=${color}:s=16x16:r=1`,'-t','1',
    '-c:v','libx264','-pix_fmt','yuv420p',join(dir,`${name}.mp4`)]);
  episode.clips[name]={file:`${name}.mp4`,credit:'Test',rights:'Own',upscale:100};
}

test('release-only and unused media changes keep PNGs; only a reached still recaptures',async t=>{
  const {dir,episode,run}=await fixture(t);
  addStill(episode,dir,'focus','red');
  episode.shots[2].pictures=[{from:0,to:2,still:'focus',area:'frame',fit:'cover'}];
  await run();
  episode.release.sourceUrl='https://example.invalid/source';
  addStill(episode,dir,'unused','green');
  await run();
  let next=await report(dir);
  assert.equal(next.framesChecked,0,'release prose and an unused preload name are nonvisual');
  addStill(episode,dir,'unused','blue');
  await run();
  next=await report(dir);
  assert.equal(next.framesChecked,0,'changing bytes of unused media is nonvisual');
  addClip(episode,dir,'unused','green');
  await run();
  next=await report(dir);assert.equal(next.framesChecked,0,'declaring an unused clip is nonvisual');
  addClip(episode,dir,'unused','blue');
  await run();
  next=await report(dir);assert.equal(next.framesChecked,0,'changing unused clip bytes is nonvisual');
  addStill(episode,dir,'focus','yellow');
  await run();
  next=await report(dir);
  assert.deepEqual(next.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',0,4],['c',4,0],['d',0,4]]);
});

test('a shared clip extraction range can broaden without invalidating unchanged selected frames',async t=>{
  const {dir,episode,load,viewer}=await fixture(t);
  const file=join(dir,'shared.mp4');
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','testsrc2=size=160x120:rate=3:duration=4',
    '-c:v','libx264','-pix_fmt','yuv420p',file]);
  episode.clips.shared={file:'shared.mp4',credit:'Own',rights:'Own',upscale:10};
  episode.shots[1].pictures=[{from:0,to:1,clip:'shared',inPoint:1,area:'stage'}];
  episode.shots[3].pictures=[{from:0,to:1,clip:'shared',inPoint:2,area:'stage'}];
  const run=async()=>{const film=await load();await render(film,{viewer,label:'incremental',audio:null});return film;};
  const before=await run();
  const prior=await report(dir),oldRange=before.pictureMedia.clips.shared.extraction.key;
  episode.shots[3].pictures[0].to=2;
  const after=await run();
  const next=await report(dir);
  assert.notEqual(after.pictureMedia.clips.shared.extraction.key,oldRange);
  assert.equal(next.cache.shots[1].key,prior.cache.shots[1].key,'B selected the same decoded source bytes');
  assert.deepEqual(next.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',0,4],['c',0,4],['d',4,0]]);
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','smptebars=size=160x120:rate=3:duration=4',
    '-c:v','libx264','-pix_fmt','yuv420p',file]);
  await run();
  const replaced=await report(dir);
  assert.deepEqual(replaced.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',4,0],['c',0,4],['d',4,0]],
    'new source bytes invalidate only shots that reach this clip');
});

test('fractional shot boundaries use the global output grid and invalidate shifted requests',async t=>{
  const {dir,episode,load,run}=await fixture(t);
  episode.output.fps=4;
  episode.shots[0].end=1.3;episode.shots[0].simulation.to=1.3;
  episode.shots[1].start=1.3;episode.shots[1].simulation.from=1.3;
  const plan=outputShotUnits(await load(),4);
  assert.deepEqual(plan.units[0].frames.map(f=>f.index),[0,1,2,3,4,5]);
  assert.equal(plan.units[1].frames[0].index,6);
  assert.equal(plan.units[1].frames[0].time,1.5);
  assert.ok(Math.abs(plan.units[1].frames[0].request.elements['b.view'].time-1.5/8)<1e-12);
  await run();
  const prior=await report(dir);
  episode.shots[0].end=1.45;episode.shots[0].simulation.to=1.45;
  episode.shots[1].start=1.45;episode.shots[1].simulation.from=1.45;
  await run();
  const shifted=await report(dir);
  assert.notEqual(shifted.cache.shots[1].key,prior.cache.shots[1].key);
  assert.equal(shifted.cache.shots[2].key,prior.cache.shots[2].key);
  assert.deepEqual(outputShotUnits(await load(),4).units[2].frames.map(f=>f.request.transition?.outgoing),
    plan.units[2].frames.map(f=>f.request.transition?.outgoing),
    'C sees the same B end state and continuation despite the earlier boundary moving');
  assert.deepEqual(shifted.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',6,0],['b',10,0],['c',0,8],['d',0,8]]);
  await run({},{at:'cold'});
  const fresh=JSON.parse(await readFile(join(dir,'cold','_build','incremental-manifest.json'),'utf8'));
  for(let i=0;i<32;i++){
    const name=`${String(i).padStart(6,'0')}.png`;
    assert.equal(await fileHash(join(shifted.dir,name)),await fileHash(join(fresh.dir,name)),`fractional global frame ${i}`);
  }
});

test('common style, chrome, viewer, model, geometry, FPS and duration invalidate all units',async t=>{
  const {project,dir,viewer,episode,run:render}=await fixture(t);
  const run=async options=>{await render(options);return report(dir);};
  let current=await run();
  const faces=current.provenance.fontFaces;
  for(const entry of [faces.film.regular,faces.film.bold,faces.code.regular,faces.code.bold]){
    assert.ok(entry?.path&&entry.sha256===await fileHash(entry.path),'every used regular/bold face is bound');
  }
  episode.style.accent='#237c86';current=await run();assert.equal(current.cache.capturedFrames,16);
  episode.series='OTHER SERIES';current=await run();assert.equal(current.cache.capturedFrames,16);
  await writeFile(viewer,(await readFile(viewer,'utf8'))+'\n// new viewer bytes\n');
  current=await run();assert.equal(current.cache.capturedFrames,16);
  await project.setManifest({root:{name:'test',note:'changed asset manifest'},animation:{loop:8}});
  current=await run();assert.equal(current.cache.capturedFrames,16);
  current=await run({width:320});assert.equal(current.cache.capturedFrames,16);
  current=await run({fps:4});assert.equal(current.cache.capturedFrames,32);
  episode.output.durationSeconds=10;episode.shots[3].end=10;episode.shots[3].simulation.to=8;
  current=await run({fps:4});assert.equal(current.cache.capturedFrames,40);
});

// Shot b says ONE TWO, revealed as it is spoken.
function spokenReveal(episode){
  episode.audio={provider:'elevenlabs',model:'eleven_v3',voice:'test',replacements:{},outputFormat:'pcm_24000'};
  episode.shots[1].narration='ONE TWO';
  episode.shots[1].overlays=[{from:0,to:2,position:'top',text:'ONE TWO',reveal:{timing:'spoken'}}];
}

test('a pre-resolved measured cue cannot hide its now-missing cached speech take',async t=>{
  const {episode,load,viewer}=await fixture(t);
  spokenReveal(episode);
  const film=await load();
  film.wordTiming={b:{sha256:'stale'}};
  for(const cue of film.chapters[1].shots[0].cues)for(const action of cue.actions)if(action.reveal)action.reveal.onsets=[0,.5];
  await assert.rejects(render(film,{viewer,label:'incremental',audio:null}),
    /Word timing needs cached speech for shot b; run the speech command first/);
});

// Installs shot b's measured take: 'ONE' at 0 s and 'TWO' at `secondOnset`.
async function measuredTake(film,level=0,secondOnset=.5){
  const entry=speechCacheEntry(film,spokenChapters(film),1);
  await mkdir(join(film.paths.build,'audio'),{recursive:true});
  const pcm=Buffer.alloc(24000*2);pcm.fill(level);
  await writeFile(entry.file,pcmWav(pcm,24000));
  const starts=[0,.1,.2,.3,secondOnset,secondOnset+.1,secondOnset+.2];
  const alignment={characters:Array.from('ONE TWO'),character_start_times_seconds:starts,
    character_end_times_seconds:starts.map(x=>x+.09)};
  await writeFile(entry.meta,JSON.stringify({sha256:await fileHash(entry.file),alignment}));
  return entry;
}

test('a verified measured take and alignment bind only the shots whose words can show',async t=>{
  const {dir,episode,load,run}=await fixture(t);
  spokenReveal(episode);
  await measuredTake(await load());
  await run();
  const first=await report(dir);
  await measuredTake(await load(),1);
  await run();
  let next=await report(dir);
  assert.notEqual(next.cache.shots[1].key,first.cache.shots[1].key,'the verified take checksum is bound');
  assert.deepEqual(next.cache.shots.map(s=>[s.shotId,s.captured,s.reused]),
    [['a',0,4],['b',4,0],['c',4,0],['d',0,4]]);
  const priorKey=next.cache.shots[1].key;
  await measuredTake(await load(),1,.55);
  await run();
  next=await report(dir);
  assert.notEqual(next.cache.shots[1].key,priorKey,'sub-frame measured onset changes remain bound');
  assert.equal(next.cache.shots[1].captured,4);
  await measuredTake(await load(),1,.9);
  await run();
  next=await report(dir);
  assert.equal(next.cache.shots[1].captured,4,'changed measured word onsets recapture B');
  assert.equal(next.cache.shots[0].reused,4);
  assert.equal(next.cache.shots[3].reused,4);
});

test('audio and external captions change the output but never buy speech or recapture plain PNGs',async t=>{
  const {dir,episode,run}=await fixture(t);
  episode.shots[1].overlays.push({from:0,to:2,position:'lower-third',text:'ONE TWO',
    reveal:{timing:'even',duration:1}});
  const mix=join(dir,'mix.wav');
  const firstAudio=pcmWav(Buffer.alloc(24000*2*8),24000);
  await writeFile(mix,firstAudio);
  const firstCaptions=[{text:'First narration.',start:.2,end:1}];
  await run({audio:{mix,records:[{id:'first'}],captions:firstCaptions}});
  const prior=await report(dir);
  episode.shots[1].narration='Different words without a measured visual cue.';
  await writeFile(mix,pcmWav(Buffer.alloc(24000*2*8,8),24000));
  const nextCaptions=[{text:'Second narration.',start:.2,end:1}];
  await run({audio:{mix,records:[{id:'second'}],captions:nextCaptions}});
  const next=await report(dir);
  assert.equal(next.cache.reusedFrames,16);
  assert.equal(next.framesChecked,0,'an even reveal does not depend on the narration take');
  assert.deepEqual(next.audio,[{id:'second'}]);
  assert.notEqual(next.outputSha256,prior.outputSha256);
  assert.match(await readFile(join(dir,'_build','incremental.srt'),'utf8'),/Second narration\./);
});

test('an index contradicting its bound media or measured inputs is not reused',async t=>{
  const {dir,run}=await fixture(t);
  await run();
  const first=await report(dir),shot=first.cache.shots[1];
  const path=join(shot.generation,'index.json');
  const index=JSON.parse(await readFile(path,'utf8'));
  index.measured=[{shotId:'b',sha256:'invented'}];
  await writeFile(path,JSON.stringify(index));
  await run();
  const next=await report(dir);
  assert.equal(next.cache.shots[1].captured,4,'contradictory index requires a new complete B generation');
  assert.equal(next.cache.shots[0].reused,4);
  assert.notEqual(next.cache.shots[1].generation,shot.generation);
});

test('only complete, dimensioned and byte-attested shot generations survive interruption or damage',async t=>{
  const {dir,run}=await fixture(t);
  const legacy=join(dir,'_build','frames','legacy');await mkdir(legacy,{recursive:true});
  await writeFile(join(legacy,'000000.png'),'an old nonempty frame is not an attested shot');
  const rerun=async()=>{await run();return report(dir);};
  let current=await rerun();
  assert.equal(current.cache.capturedFrames,16,'legacy whole-episode frames are not imported');
  assert.equal(current.cache.shots.length,4);
  assert.equal(current.cache.shots.reduce((n,s)=>n+s.captured+s.reused,0),16);
  for(const shot of current.cache.shots){
    const index=JSON.parse(await readFile(join(shot.generation,'index.json'),'utf8'));
    assert.equal(index.frames.length,4);
    assert.equal(index.provenance.workflowHead,shot.origin.workflowHead);
    assert.equal(index.provenance.projectHead,shot.origin.projectHead);
    for(const frame of index.frames)
      assert.equal(await fileHash(join(current.dir,frame.file)),frame.sha256);
  }
  const damage=async modify=>{
    const prior=current.cache.shots[1];
    await modify(prior);
    current=await rerun();
    assert.equal(current.cache.shots[1].captured,4);
    assert.notEqual(current.cache.shots[1].generation,prior.generation);
    assert.equal(current.cache.shots[0].reused,4);
    assert.equal(current.cache.shots[2].reused,4);
    assert.equal(current.cache.shots[3].reused,4);
    assert.equal(current.outputSha256,await fileHash(current.output));
  };
  await damage(async shot=>{await writeFile(join(shot.generation,'000004.png'),'truncated');});
  await damage(async shot=>{await unlink(join(shot.generation,'000004.png'));});
  await damage(async shot=>{await writeFile(join(shot.generation,'index.json'),'null');});
  await damage(async shot=>{
    const path=join(shot.generation,'index.json'),index=JSON.parse(await readFile(path,'utf8'));
    index.frames[0]=null;await writeFile(path,JSON.stringify(index));
  });
  await damage(async shot=>{
    const path=join(shot.generation,'index.json'),index=JSON.parse(await readFile(path,'utf8'));
    delete index.provenance;await writeFile(path,JSON.stringify(index));
  });
  await damage(async shot=>{
    const tiny=join(dir,'tiny.png');
    execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','color=c=blue:s=16x16','-frames:v','1',tiny]);
    const bytes=await readFile(tiny),path=join(shot.generation,'index.json');
    await writeFile(join(shot.generation,'000004.png'),bytes);
    const index=JSON.parse(await readFile(path,'utf8'));
    index.frames[0].sha256=hash(bytes);await writeFile(path,JSON.stringify(index));
  });
  await damage(async shot=>{
    await unlink(join(shot.generation,'index.json'));
    await unlink(join(shot.generation,'000005.png'));
    await writeFile(join(shot.generation,'000005.png.tmp'),'interrupted screenshot');
  });
  const healthy=current.cache.shots[1];
  await writeFile(join(healthy.generation,'..','zzzz-not-a-generation'),'stray sibling');
  current=await rerun();
  assert.equal(current.cache.reusedFrames,16,'a stray file is skipped and a healthy generation is found');
});

test('assembly refuses duplicate or missing global output frames before encoding',async t=>{
  const {dir,load,run}=await fixture(t);
  await run();
  const film=await load(),current=await report(dir),units=outputShotUnits(film,film.output.fps).units;
  const selections=new Map(current.cache.shots.map(shot=>[shot.shotId,{generation:shot.generation}]));
  const root=shotCacheRoot(film.paths.build);
  units[1].frames[0].index=units[0].frames[0].index;
  await assert.rejects(assembleShotFrames(root,units,selections,16),/Duplicate output frame 0/);
  units[1].frames[0].index=4;
  units[1].frames.shift();
  await assert.rejects(assembleShotFrames(root,units,selections,16),/hole in output frames/);
});

test('a failed encode preserves the previous MP4 and manifest while completed shots remain reusable',async t=>{
  const {dir,episode,run}=await fixture(t);
  const output=await run();
  const oldOutputHash=await fileHash(output);
  const manifestPath=join(dir,'_build','incremental-manifest.json');
  const oldManifestHash=await fileHash(manifestPath);
  episode.shots[1].overlays[0].text='AFTER FAILURE';
  await assert.rejects(run({audio:{mix:join(dir,'missing-mix.wav'),records:[],captions:[]}}),/ffmpeg exited/);
  assert.equal(await fileHash(output),oldOutputHash,'the old complete film is not overwritten');
  assert.equal(await fileHash(manifestPath),oldManifestHash,'no new manifest claims the failed film');
  await run();
  const recovered=await report(dir);
  assert.equal(recovered.cache.reusedFrames,16,'the interrupted encode did not discard attested shot captures');
  assert.equal(recovered.outputSha256,await fileHash(output));
  assert.notEqual(recovered.outputSha256,oldOutputHash);
  assert.equal(recovered.probe.format.filename,output,'published probe names the published film');
  assert.equal((await readdir(join(dir,'_build'))).filter(name=>name.startsWith('incremental.mp4.previous-')).length,0,
    'a successful publication does not accumulate recovery copies');
});

test('an interrupted publication leaves a stale-hash manifest and a recoverable prior film',async t=>{
  const {dir,episode,run}=await fixture(t);
  const output=await run();
  const prior=await report(dir),oldHash=await fileHash(output);
  const thumbnail=join(dir,'_build','thumbnail.png');
  await rename(thumbnail,`${thumbnail}.prior`);await mkdir(thumbnail);
  episode.shots[1].overlays[0].text='NEW FILM';
  await assert.rejects(run(),/EISDIR|ENOTEMPTY|directory/i);
  const stillOldManifest=await report(dir);
  assert.equal(stillOldManifest.outputSha256,prior.outputSha256);
  assert.notEqual(stillOldManifest.outputSha256,await fileHash(output),
    'the old manifest visibly fails its output-hash check after the publication interruption');
  const backups=(await readdir(join(dir,'_build'))).filter(name=>name.startsWith('incremental.mp4.previous-'));
  assert.equal(backups.length,1);
  assert.equal(await fileHash(join(dir,'_build',backups[0])),oldHash,'the prior good MP4 is recoverable');
});
