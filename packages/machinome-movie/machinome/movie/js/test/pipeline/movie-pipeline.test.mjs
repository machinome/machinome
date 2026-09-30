// Layer 8 (serial; Chromium, FFmpeg, the viewer double, the speech double, no
// provider): check, speech, preview, render and review end to end on the 0.2
// fixture movie `tour` and on the YAML fixture episode, from the command line
// and through the functions it calls.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {writeFile,readFile,readdir,appendFile,realpath} from 'node:fs/promises';
import {join,basename,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {loadEpisode} from '../../src/episode.mjs';
import {speech,speechCacheEntry,spokenChapters} from '../../src/speech.mjs';
import {frameAt,filmShots,shotActions} from '../../src/timeline.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {preview,render} from '../support/stage.mjs';
import {pendingMovie,generateMovieTakes} from '../../src/movie.mjs';
import {reviewManifest} from '../../src/review-pack.mjs';
import {fileHash} from '../../src/util.mjs';
import {fixtureProject,yamlEpisode,evenAlignment,installTake,readJson} from '../project-fixture.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {viewerDouble} from '../viewer-double.mjs';

const here=dirname(fileURLToPath(import.meta.url)),fixtures=join(here,'..','..','fixtures');
// No key in the environment, and any request fails the test that made it.
function noNetwork(t){
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,calls=[];
  delete process.env.ELEVENLABS_API_KEY;
  globalThis.fetch=(...args)=>{calls.push(String(args[0]));throw new Error('A test attempted a network request');};
  t.onTestFinished(()=>{globalThis.fetch=fetch;if(key!==undefined)process.env.ELEVENLABS_API_KEY=key;});
  return calls;
}
// The command line in a child process with no key and a fetch that throws, so
// a take that is not cached can never become a request. It launches its own
// Chromium, as the command line must.
const NO_FETCH='data:text/javascript,globalThis.fetch=()=>{throw new Error("A test attempted a network request")}';
const cli=(...args)=>{
  try{return {code:0,out:execFileSync(process.execPath,['--import',NO_FETCH,join(here,'..','..','bin','videomaker.mjs'),...args],
    {encoding:'utf8',stdio:['ignore','pipe','pipe'],env:{...process.env,ELEVENLABS_API_KEY:''}})};}
  catch(error){return {code:error.status,out:String(error.stdout)+String(error.stderr)};}
};
// What ffprobe reads of an encoded film: its video frames, size and rate, and
// the kinds of stream it carries.
function probe(file){
  const data=JSON.parse(execFileSync('ffprobe',['-v','error','-count_frames','-show_streams','-of','json',file],{encoding:'utf8'}));
  const video=data.streams.find(s=>s.codec_type==='video');
  return {frames:Number(video.nb_read_frames),width:video.width,height:video.height,rate:video.r_frame_rate,
    kinds:data.streams.map(s=>s.codec_type).sort()};
}
const ffprobeRate=fps=>`${fps}/1`;

// The YAML fixture episode's shots and what each says (after the replacement).
const YAML_SHOTS=[['hook','The wheel turns the shaft.'],['coupling','The waterwheel drives the crankshaft.'],['closing','Watch mah-SHEEN-ohm again.']];
async function yamlFixture(t){
  const {dir,revision}=await fixtureProject(t);
  const file=await yamlEpisode(dir,revision);
  const viewer=join(dir,'viewer.js');
  await writeFile(viewer,'// machinome-viewer double, viewer API 28\n'+viewerDouble({}));
  return {dir,file,viewer};
}
async function installYamlTakes(film,step=.05,extra=.05){
  const spoken=spokenChapters(film),names=[];
  for(const [i,[,text]] of YAML_SHOTS.entries()){
    assert.equal(spoken[i],text);
    const entry=speechCacheEntry(film,spoken,i);names.push(basename(entry.file));
    await installTake(entry,{alignment:evenAlignment(text,step),duration:+(Array.from(text).length*step+extra).toFixed(6)});
  }
  return names;
}

// Computed on the base commit 6e86728 (source as declarative-python), before
// the chapters or the stage existed, by loading the same YAML episode with the
// same takes: file names, speech records, captions, the takes' checksums and
// the words' measured instants. Literal; never regenerate from the code under test.
const BASE={"names":["hook-11814c00c2ad9784.wav","coupling-7126e3bf3e18a59a.wav","closing-f6d9fbde9278b628.wav"],"records":[{"id":"hook","offset":0.3,"duration":1.4,"sha256":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d"},{"id":"coupling","offset":2.7,"duration":1.95,"sha256":"d434dc64629dd462d731ae5d10b168cd4c0fd445448c18f1ef11b47da2ea4506"},{"id":"closing","offset":5.2,"duration":1.4,"sha256":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d"}],"captions":[{"text":"The wheel turns the shaft.","start":0.3,"end":1.6},{"text":"The waterwheel drives the crankshaft.","start":2.7,"end":4.550000000000001},{"text":"Watch Machinome again.","start":5.2,"end":6.5}],
  "takes":{"hook":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d","coupling":"d434dc64629dd462d731ae5d10b168cd4c0fd445448c18f1ef11b47da2ea4506"},
  "onsets":[0.3,0.5,0.8],"emphasis":{"from":0.4,"to":2.2500000000000004,"words":[["waterwheel",0.4],["drives",0.95],["crankshaft",1.5]]},
  "frameCount":70};

test('a YAML episode keeps its take keys, captions, measured words and frames',async t=>{
  const calls=noNetwork(t);
  const {dir,revision}=await fixtureProject(t);
  const e=await loadEpisode(await yamlEpisode(dir,revision));
  assert.deepEqual(e.chapters.map(c=>[c.id,c.narration,c.start,c.end,c.shots.map(s=>s.id)]),
    [['hook','The wheel turns the shaft.',0,2.5,['hook']],['coupling','The waterwheel drives the crankshaft.',2.5,5,['coupling']],
      ['closing','Watch Machinome again.',5,7,['closing']]]);
  const spoken=spokenChapters(e);
  assert.deepEqual(spoken,YAML_SHOTS.map(([,text])=>text));
  const names=[];
  for(const i of e.chapters.keys()){
    const entry=speechCacheEntry(e,spoken,i);names.push(basename(entry.file));
    await installTake(entry,{alignment:evenAlignment(spoken[i]),duration:+(Array.from(spoken[i]).length*.05+.1).toFixed(6)});
  }
  assert.deepEqual(names,BASE.names);
  await prepareWordTimingForCommand(e,{command:'check'});
  const audio=await speech(e,{generate:false});
  assert.deepEqual(audio.records.map(r=>({id:r.id,offset:r.offset,duration:r.duration,sha256:r.sha256})),BASE.records);
  assert.deepEqual(audio.captions,BASE.captions);
  assert.deepEqual(Object.fromEntries(Object.entries(e.wordTiming).map(([k,v])=>[k,v.sha256])),BASE.takes);
  const actions=id=>shotActions(filmShots(e).find(s=>s.shot.id===id).shot);
  assert.deepEqual(actions('hook').find(x=>x.action.reveal).action.reveal.onsets,BASE.onsets);
  const emphasis=actions('coupling').find(x=>x.action.action==='emphasize');
  assert.equal(emphasis.cue.at,BASE.emphasis.from);assert.equal(emphasis.action.until,BASE.emphasis.to);
  assert.deepEqual(emphasis.action.words.map(w=>[w.token,w.at]),BASE.emphasis.words);
  // The frames (the frame is new in this change; its content is the base's).
  const frames=[];for(let i=0;i<e.output.durationSeconds*e.output.fps;i++)frames.push(frameAt(e,i/e.output.fps));
  assert.equal(frames.length,BASE.frameCount);
  const f0=frames[0],f13=frames[13],f27=frames[27],f41=frames[41],f66=frames[66];
  assert.deepEqual([f0.shotId,f0.set,f0.elements['hook.view'].view.camera,f0.elements['hook.overlay-0'].revealed,f0.transition.field,f0.transition.plate],
    ['hook','paper',[0,-10,4],0,'fadeIn',1]);
  assert.deepEqual([f13.elements['hook.view'].time,f13.elements['hook.view'].view.camera,f13.elements['hook.overlay-0'].revealed,f13.transition],
    [0.16153846153846155,[1.657,-6.686,2.343],3,null]);
  assert.deepEqual([f27.shotId,f27.set,f27.elements['coupling.code'].text,f27.elements['coupling.code'].cursor,f27.elements['coupling.code'].emphasis,
    f27.transition.kind,f27.transition.progress,f27.transition.outgoing.elements['hook.view'].time,f27.transition.outgoing.elements['hook.overlay-0'].revealed],
  ['coupling','paper-split','waterwheel.drives(c',true,[],'dissolve',0.5000000000000007,0.3230769230769231,3]);
  assert.deepEqual([f41.elements['coupling.code'].text,f41.elements['coupling.code'].cursor,f41.elements['coupling.code'].emphasis.map(x=>x.token)],
    ['waterwheel.drives(crankshaft)',false,['waterwheel','drives','crankshaft']]);
  assert.deepEqual([f66.shotId,f66.elements['closing.view'].view.camera,f66.elements['closing.view'].highlight,f66.transition.field,f66.transition.plate],
    ['closing',[0.40000000000000036,-9.2,3.5999999999999996],{paths:[['Feed','Pawl']],others:'ghost',color:'#237c86'},'fadeOut',0.156249999999999]);
  assert.deepEqual(calls,[]);
});

test('the tour is checked, previewed, rendered twice and reviewed from the command line',async t=>{
  const calls=noNetwork(t);
  const {file,viewer,build}=await fixtureMovie(t,'tour');
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.out);
  assert.match(checked.out,/^Tour: 3 chapters, 9 shots, 18\.9s; model 20s$/m);
  // Where the film's length comes from (wart 7 of Cut and Advance): each
  // chapter's take, its resolved length and its tail, after the summary line.
  assert.match(checked.out,/^Tour: 3 chapters.*\n {2}opening: take 3\.94 s, chapter 4\.77 s, tail 0\.63 s\n {2}balance: take 6\.04 s, chapter 6\.67 s, tail 0\.43 s\n {2}tip: take 6\.22 s, chapter 7\.47 s, tail 1\.05 s$/m);
  const line=/^Stage: bundled (\S+stage\.js) \(sha256 ([0-9a-f]{12})\) from stage\.tsx; types checked$/m.exec(checked.out);
  assert.ok(line,checked.out);
  const bundle=await fileHash(line[1]);
  assert.equal(bundle.slice(0,12),line[2]);assert.equal(line[1],join(await realpath(build),'stage','stage.js'));
  assert.doesNotMatch(checked.out,/Narration|Generating/,'check buys and mixes no speech');
  const previewed=cli('preview',file,'--viewer',viewer,'--width','640');
  assert.equal(previewed.code,0,previewed.out);
  const report=await readJson(join(build,'preview','report.json'));
  assert.equal(report.pixelReplay,true);assert.equal(report.stage.sha256,bundle);
  assert.ok((await readFile(join(build,'storyboard.jpg'))).length>0);
  const rendered=cli('render',file,'--viewer',viewer,'--width','640');
  assert.equal(rendered.code,0,rendered.out);
  assert.match(rendered.out,/^Video: .*rehearsal\.mp4$/m);assert.match(rendered.out,/^Review pack: /m);
  const manifestPath=join(build,'rehearsal-manifest.json'),manifest=await readJson(manifestPath);
  const frames=Math.round(18.9*30);
  assert.equal(manifest.count,frames);assert.equal(manifest.fps,30);
  assert.equal(manifest.stageSha256,bundle,'the manifest records the stage bundle');
  assert.equal(manifest.provenance.stageSha256,bundle);
  assert.equal(manifest.cache.capturedFrames,frames);
  assert.deepEqual(probe(manifest.output),{frames,width:640,height:360,rate:ffprobeRate(30),kinds:['audio','video']},
    'every frame, the size and the rate, one audio stream and no subtitle stream');
  assert.equal(manifest.subtitles.burnedIn,false);
  // The plate covers the stage as a film's drawing does: the still is the
  // stage's height at 1280 by 720, drawn at its own size, so the shot's zoom of
  // 1.4 is its peak enlargement there, inside the allowance preview checked.
  // Render measures it on its own frames, 640 wide: half of it.
  assert.deepEqual(manifest.pictures.cues.map(c=>[c.shotId,c.element,c.name,c.width,c.height,c.allowance]),
    [['still','tip.plate','plate',864,576,1.5]]);
  assert.ok(Math.abs(manifest.pictures.cues[0].peak-1.4*640/1280)<.005,`peak enlargement ${manifest.pictures.cues[0].peak}`);
  const again=cli('render',file,'--viewer',viewer,'--width','640');
  assert.equal(again.code,0,again.out);
  const second=await readJson(manifestPath);
  assert.equal(second.cache.capturedFrames,0,'a second render captures nothing');
  assert.equal(second.cache.reusedFrames,frames);
  const reviewed=cli('review',manifestPath);
  assert.equal(reviewed.code,0,reviewed.out);assert.match(reviewed.out,/^Review pack: .*\(verified reuse\)$/m);
  assert.deepEqual(calls,[]);
});

test('the YAML fixture episode is checked, previewed, rendered twice and reviewed',async t=>{
  const calls=noNetwork(t);
  const {file,viewer}=await yamlFixture(t);
  const film=await loadEpisode(file);
  await installYamlTakes(film);
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.out);
  assert.match(checked.out,/^YAML fixture: 3 chapters, 3 shots, 7s; model 20s$/m);
  // A YAML episode's chapters are its shots.
  assert.match(checked.out,/^ {2}hook: take 1\.35 s, chapter 2\.50 s, tail 0\.85 s\n {2}coupling: take 1\.90 s, chapter 2\.50 s, tail 0\.40 s\n {2}closing: take 1\.35 s, chapter 2\.00 s, tail 0\.45 s$/m);
  const line=/^Stage: bundled (\S+stage\.js) \(sha256 ([0-9a-f]{12})\) from the runtime alone; no module to type-check$/m.exec(checked.out);
  assert.ok(line,checked.out);
  const e=await loadEpisode(file);
  await prepareWordTimingForCommand(e,{command:'preview'});
  const report=await preview(e,{viewer,width:320});
  assert.equal(report.pixelReplay,true);
  for(const kind of ['revealChecks','emphasisChecks','highlightChecks','transitionChecks'])assert.ok(report[kind]?.length>0,kind);
  assert.equal(report.stage.sha256,await fileHash(line[1]));
  const audio=await speech(e,{generate:false});
  const output=await render(e,{viewer,audio});
  const manifestPath=join(e.paths.build,'rehearsal-manifest.json'),manifest=await readJson(manifestPath);
  assert.equal(output,manifest.output);
  assert.equal(manifest.stageSha256,await fileHash(line[1]),'the manifest records the stage bundle');
  assert.deepEqual(probe(output),{frames:70,width:320,height:180,rate:ffprobeRate(10),kinds:['audio','video']});
  assert.match(await readFile(join(e.paths.build,'rehearsal.srt'),'utf8'),/Watch Machinome again\./);
  await render(e,{viewer,audio});
  const second=await readJson(manifestPath);
  assert.equal(second.cache.capturedFrames,0,'a second render captures nothing');assert.equal(second.cache.reusedFrames,70);
  const pack=await reviewManifest(manifestPath);
  assert.equal(pack.reused,true,'render built the review pack; review verifies and reuses it');
  assert.deepEqual(calls,[]);
});

test('check type-checks the stage modules before any speech, and refuses one that does not by name',async t=>{
  const {file,viewer,movie,build}=await fixtureMovie(t,'tour');
  await appendFile(join(movie,'..','tour','stage.tsx'),"\nexport const broken: number = 'not a number';\n");
  const before=(await readdir(join(build,'audio'))).sort();
  const refused=cli('check',file,'--viewer',viewer);
  assert.equal(refused.code,1,refused.out);
  assert.match(refused.out,/Stage module stage\.tsx does not type-check against the movie's stage block/);
  assert.match(refused.out,/stage\.tsx.*TS2322/);
  assert.doesNotMatch(refused.out,/Narration|Generating|network request/);
  assert.deepEqual((await readdir(join(build,'audio'))).sort(),before,'no take was requested or written');
});

test('check refuses a stage module that does not type-check before it asks for the takes',async t=>{
  const {file,viewer,movie}=await fixtureMovie(t,'tour',{takes:false});
  await appendFile(join(movie,'stage.tsx'),"\nexport const broken: number = 'not a number';\n");
  const refused=cli('check',file,'--viewer',viewer);
  assert.equal(refused.code,1,refused.out);
  assert.match(refused.out,/Stage module stage\.tsx does not type-check against the movie's stage block/);
  assert.doesNotMatch(refused.out,/no cached narration take/);
});

test('a movie document is refused before its takes, then speaks from cached takes and resolves to its pin',async t=>{
  const calls=noNetwork(t);
  const {file,viewer,build}=await fixtureMovie(t,'tour',{takes:false});
  await assert.rejects(loadEpisode(file),
    /^Error: Chapter opening has spoken anchors and no cached narration take; run the speech command first \(check, preview and render never generate speech\)$/);
  const refused=cli('check',file,'--viewer',viewer);
  assert.equal(refused.code,1);assert.match(refused.out,/Chapter opening has spoken anchors and no cached narration take/);
  const pending=await pendingMovie(file),spoken=spokenChapters(pending),durations=[];
  for(const [i,chapter] of pending.chapters.entries()){
    const entry=speechCacheEntry(pending,spoken,i),take=await readJson(join(fixtures,'takes','tour',`${chapter.id}.json`));
    assert.match(basename(entry.file),new RegExp(`^${chapter.id}-[0-9a-f]{16}\\.wav$`));
    await installTake(entry,take);durations.push(`Narration ${chapter.id}: ${take.duration.toFixed(2)}s`);
  }
  // The speech command's first step, on the unresolved document: every take is cached, nothing is requested.
  assert.deepEqual((await generateMovieTakes(file)).map(g=>[g.id,g.generated]),[['opening',false],['balance',false],['tip',false]]);
  const spoke=cli('speech',file);
  assert.equal(spoke.code,0,spoke.out);
  assert.ok(spoke.out.includes(durations.join('\n')),spoke.out);assert.doesNotMatch(spoke.out,/Generating/);
  const e=await loadEpisode(file);
  const resolved=await readJson(join(build,'movie-resolved.json'));
  // The pin, but for the root: the copy's document sits beside its movie (root "..").
  const {root,...pinned}=await readJson(join(fixtures,'resolved','tour.json'));
  assert.equal(resolved.root,'..');assert.ok(root.endsWith('/videos/tour'));
  assert.deepEqual({...resolved,root:undefined},{...pinned,root:undefined});
  assert.equal(e.format,'machinome-movie/0.2');assert.equal(e.source,'movie');
  assert.deepEqual(e.chapters,resolved.chapters);
  assert.equal(e.paths.episode,await realpath(file));assert.equal(e.paths.base,await realpath(join(build,'..')));
  assert.deepEqual(calls,[]);
});

// Takes layer: a provider double stands in for the service; the key is a
// placeholder the double never sends anywhere.
test('speech generates one take per chapter from the unresolved document, and only once',async t=>{
  const {file,document:doc}=await fixtureMovie(t,'tour',{takes:false});
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,requests=[];
  process.env.ELEVENLABS_API_KEY='double-key-never-sent';
  t.onTestFinished(()=>{globalThis.fetch=fetch;if(key===undefined)delete process.env.ELEVENLABS_API_KEY;else process.env.ELEVENLABS_API_KEY=key;});
  globalThis.fetch=async(url,init)=>{
    const body=JSON.parse(init.body),chapter=doc.chapters.find(c=>c.narration===body.text);
    requests.push({url:String(url),text:body.text,previous:body.previous_text,next:body.next_text});
    const take=await readJson(join(fixtures,'takes','tour',`${chapter.id}.json`));
    const pcm=Buffer.alloc(Math.round(take.duration*24000)*2);
    return new Response(JSON.stringify({audio_base64:pcm.toString('base64'),alignment:take.alignment}),
      {status:200,headers:{'content-type':'application/json'}});
  };
  const first=await generateMovieTakes(file);
  assert.deepEqual(first,doc.chapters.map(c=>({id:c.id,generated:true})));
  assert.deepEqual(requests.map(r=>[r.text,r.previous,r.next]),doc.chapters.map(c=>[c.narration,undefined,undefined]),
    'an eleven_v3 request carries no neighbouring text');
  assert.ok(requests.every(r=>r.url.endsWith('/text-to-speech/fixture-voice/with-timestamps?output_format=pcm_24000')));
  const again=await generateMovieTakes(file);
  assert.deepEqual(again,doc.chapters.map(c=>({id:c.id,generated:false})));
  assert.equal(requests.length,doc.chapters.length);
  const e=await loadEpisode(file);
  assert.deepEqual(e.chapters,(await readJson(join(fixtures,'resolved','tour.json'))).chapters);
});
