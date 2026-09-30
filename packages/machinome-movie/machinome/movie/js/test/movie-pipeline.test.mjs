// Pipeline layer (serial; Chromium, FFmpeg, the viewer double, no provider):
// a movie document end to end, and a YAML episode's identity with the base
// commit before chapters existed.
import {slowTest as test} from './support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdir,writeFile,readFile,copyFile,realpath} from 'node:fs/promises';
import {join,basename,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {loadEpisode} from '../src/episode.mjs';
import {speech,speechCacheEntry,spokenChapters} from '../src/speech.mjs';
import {frameAt} from '../src/timeline.mjs';
import {prepareWordTimingForCommand} from '../src/command-timing.mjs';
import {preview,render} from './support/stage.mjs';
import {pendingMovie,generateMovieTakes} from '../src/movie.mjs';
import {hash} from '../src/util.mjs';
import {fixtureProject,yamlEpisode,evenAlignment,installTake,readJson} from './project-fixture.mjs';
import {viewerDouble} from './viewer-double.mjs';

const here=dirname(fileURLToPath(import.meta.url)),fixtures=join(here,'..','fixtures');
// No key in the environment, and any request fails the test that made it.
function noNetwork(t){
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,calls=[];
  delete process.env.ELEVENLABS_API_KEY;
  globalThis.fetch=(...args)=>{calls.push(String(args[0]));throw new Error('A test attempted a network request');};
  t.onTestFinished(()=>{globalThis.fetch=fetch;if(key!==undefined)process.env.ELEVENLABS_API_KEY=key;});
  return calls;
}

// Computed on the base commit 6e86728 (source as declarative-python), before
// any source change of this cycle, by loading the same YAML episode with the
// same takes: file names, speech records, captions, word timing and every
// output frame's request. Literal; never regenerate from the code under test.
const BASE={"names":["hook-11814c00c2ad9784.wav","coupling-7126e3bf3e18a59a.wav","closing-f6d9fbde9278b628.wav"],"records":[{"id":"hook","offset":0.3,"duration":1.4,"sha256":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d"},{"id":"coupling","offset":2.7,"duration":1.95,"sha256":"d434dc64629dd462d731ae5d10b168cd4c0fd445448c18f1ef11b47da2ea4506"},{"id":"closing","offset":5.2,"duration":1.4,"sha256":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d"}],"captions":[{"text":"The wheel turns the shaft.","start":0.3,"end":1.6},{"text":"The waterwheel drives the crankshaft.","start":2.7,"end":4.550000000000001},{"text":"Watch Machinome again.","start":5.2,"end":6.5}],"wordTiming":{"hook":{"sha256":"f7c37e07ac365bedbc371c8bab4b074539e9e284afcb2ca004bb6f02f13fdf6d","overlays":{"0":{"onsets":[0.3,0.5,0.8]}},"emphasis":[]},"coupling":{"sha256":"d434dc64629dd462d731ae5d10b168cd4c0fd445448c18f1ef11b47da2ea4506","overlays":{},"emphasis":[{"index":0,"from":0.4,"to":2.2500000000000004,"cues":[{"word":"waterwheel","line":3,"start":0,"end":10,"from":0.4,"wordEnd":0.8999999999999999,"to":2.2500000000000004},{"word":"drives","line":3,"start":11,"end":17,"from":0.95,"wordEnd":1.25,"to":2.2500000000000004},{"word":"crankshaft","line":3,"start":18,"end":28,"from":1.5,"wordEnd":2,"to":2.2500000000000004}]}]}},"framesSha256":"42fa6bae9d8feab7a7faae5ea4b9d4bd22abd7f48ebe910f631ad438f91767fc","frameCount":70,"sample":{"0":{"shotId":"hook","time":0.1,"view":{"camera":[0,-10,4],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[{"from":0,"to":2.5,"text":"The wheel turns","position":"top","reveal":{"timing":"spoken"},"words":[{"text":"The","word":true,"start":0,"end":3},{"text":" ","word":false,"start":3,"end":4},{"text":"wheel","word":true,"start":4,"end":9},{"text":" ","word":false,"start":9,"end":10},{"text":"turns","word":true,"start":10,"end":15}],"shown":0}],"code":null,"annotations":[],"highlight":null,"transition":{"field":"fadeIn","kind":"fade","shotId":"hook","duration":0.5,"ease":"smooth","color":"#faf7ef","plate":1,"picture":"incoming","outgoing":null},"picture":null},"13":{"shotId":"hook","time":0.16153846153846155,"view":{"camera":[1.657,-6.686,2.343],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[{"from":0,"to":2.5,"text":"The wheel turns","position":"top","reveal":{"timing":"spoken"},"words":[{"text":"The","word":true,"start":0,"end":3},{"text":" ","word":false,"start":3,"end":4},{"text":"wheel","word":true,"start":4,"end":9},{"text":" ","word":false,"start":9,"end":10},{"text":"turns","word":true,"start":10,"end":15}],"shown":3}],"code":null,"annotations":[],"highlight":null,"transition":null,"picture":null},"27":{"shotId":"coupling","time":0.312,"view":{"camera":[2,-6,2],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[],"code":{"file":"models/fixture.py","firstLine":3,"lastLine":3,"text":"waterwheel.drives(c","html":"waterwheel.<span class=\"hljs-title function_\">drives</span>(c","cursor":true,"emphasis":[]},"annotations":[],"highlight":null,"transition":{"field":"transition","kind":"dissolve","shotId":"coupling","duration":0.4,"ease":"smooth","outgoingShotId":"hook","start":2.5,"progress":0.5000000000000007,"outgoing":{"shotId":"hook","time":0.3230769230769231,"view":{"camera":[2,-6,2],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[{"from":0,"to":2.5,"text":"The wheel turns","position":"top","reveal":{"timing":"spoken"},"words":[{"text":"The","word":true,"start":0,"end":3},{"text":" ","word":false,"start":3,"end":4},{"text":"wheel","word":true,"start":4,"end":9},{"text":" ","word":false,"start":9,"end":10},{"text":"turns","word":true,"start":10,"end":15}],"shown":3}],"code":null,"annotations":[],"highlight":null,"transition":null,"picture":null}},"picture":null},"41":{"shotId":"coupling","time":0.396,"view":{"camera":[2,-6,2],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[],"code":{"file":"models/fixture.py","firstLine":3,"lastLine":3,"text":"waterwheel.drives(crankshaft)","html":"waterwheel.<span class=\"hljs-title function_\">drives</span>(crankshaft)","cursor":false,"emphasis":[{"word":"waterwheel","line":3,"start":0,"end":10},{"word":"drives","line":3,"start":11,"end":17},{"word":"crankshaft","line":3,"start":18,"end":28}]},"annotations":[],"highlight":null,"transition":null,"picture":null},"66":{"shotId":"closing","time":0.53,"view":{"camera":[0.40000000000000036,-9.2,3.5999999999999996],"target":[0,0,0]},"up":[0,0,1],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":{"paths":[["Feed","Pawl"]],"others":"ghost","color":"#237c86"},"transition":{"field":"fadeOut","kind":"fade","shotId":"closing","duration":0.5,"ease":"smooth","color":"#faf7ef","plate":0.156249999999999,"picture":"incoming","outgoing":null},"picture":null}}};

test('a YAML episode keeps its take keys, captions, word timing and every frame',async t=>{
  const calls=noNetwork(t);
  const {dir,revision}=await fixtureProject(t);
  const e=await loadEpisode(await yamlEpisode(dir,revision));
  assert.deepEqual(e.chapters,e.shots.map(s=>({id:s.id,narration:s.narration,speechOffset:s.speechOffset??.2,
    start:s.start,end:s.end,shots:[s.id]})));
  const spoken=e.shots.map(s=>s.narration.replaceAll('Machinome','mah-SHEEN-ohm'));
  assert.deepEqual(spokenChapters(e),spoken);
  const names=[];
  for(const i of e.shots.keys()){
    const entry=speechCacheEntry(e,spoken,i);names.push(basename(entry.file));
    await installTake(entry,{alignment:evenAlignment(spoken[i]),duration:+(Array.from(spoken[i]).length*.05+.1).toFixed(6)});
  }
  assert.deepEqual(names,BASE.names);
  await prepareWordTimingForCommand(e,{command:'check'});
  const audio=await speech(e,{generate:false});
  assert.deepEqual(audio.records.map(r=>({id:r.id,offset:r.offset,duration:r.duration,sha256:r.sha256})),BASE.records);
  assert.deepEqual(audio.captions,BASE.captions);
  assert.deepEqual(JSON.parse(JSON.stringify(e.wordTiming)),BASE.wordTiming);
  const frames=[];for(let i=0;i<e.output.durationSeconds*e.output.fps;i++)frames.push(frameAt(e,i/e.output.fps));
  assert.equal(frames.length,BASE.frameCount);
  for(const [i,frame] of Object.entries(BASE.sample))assert.deepEqual(JSON.parse(JSON.stringify(frames[i])),frame,`frame ${i}`);
  assert.equal(hash(JSON.stringify(frames)),BASE.framesSha256);
  assert.deepEqual(calls,[]);
});

// The fixture project with the two-chapter document copied to its build
// directory, a still, a description and the viewer double.
async function documentProject(t){
  const {dir,revision}=await fixtureProject(t);
  const source=join(fixtures,'documents','two-chapters.json'),doc=await readJson(source);
  assert.equal(doc.model.sourceRevision,revision,'the fixture commit is deterministic');
  const movie=join(dir,'videos','two-chapters'),file=join(movie,'_build','movie.json');
  await mkdir(join(movie,'_build'),{recursive:true});await mkdir(join(movie,'media'));
  await copyFile(source,file);
  await writeFile(join(movie,'description.md'),'Fixture description.\n');
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i','testsrc2=s=640x360','-frames:v','1',join(movie,'media','plate.png')]);
  const viewer=join(dir,'viewer.js');
  await writeFile(viewer,'/* fixture double, viewer API 28 */\n'+viewerDouble({timeColor:true}));
  return {dir,movie,file,doc,viewer};
}
async function installFixtureTakes(file){
  const pending=await pendingMovie(file),spoken=spokenChapters(pending),files=[];
  for(const [i,chapter] of pending.chapters.entries()){
    const entry=speechCacheEntry(pending,spoken,i);
    assert.match(basename(entry.file),new RegExp(`^${chapter.id}-[0-9a-f]{16}\\.wav$`));
    files.push(await installTake(entry,await readJson(join(fixtures,'takes','two-chapters',`${chapter.id}.json`))));
  }
  return files;
}
// The command line in a child process with no key and a fetch that throws, so
// a take that is not cached can never become a request.
const NO_FETCH='data:text/javascript,globalThis.fetch=()=>{throw new Error("A test attempted a network request")}';
const cli=(...args)=>{
  try{return {code:0,out:execFileSync(process.execPath,['--import',NO_FETCH,join(here,'..','bin','videomaker.mjs'),...args],{encoding:'utf8',stdio:['ignore','pipe','pipe'],
    env:{...process.env,ELEVENLABS_API_KEY:''}})};}
  catch(error){return {code:error.status,out:String(error.stdout)+String(error.stderr)};}
};

test('a movie document is refused before its takes, then checks, speaks, previews and renders from them',async t=>{
  const calls=noNetwork(t);
  const {movie,file,viewer}=await documentProject(t);
  await assert.rejects(loadEpisode(file),
    /^Error: Chapter drive has spoken anchors and no cached narration take; run the speech command first \(check, preview and render never generate speech\)$/);
  const refused=cli('check',file,'--viewer',viewer);
  assert.equal(refused.code,1);assert.match(refused.out,/Chapter drive has spoken anchors and no cached narration take/);
  await installFixtureTakes(file);
  // The speech command's first step, on the unresolved document: every take is cached, nothing is requested.
  const generated=await generateMovieTakes(file);
  assert.deepEqual(generated.map(g=>[g.id,g.generated]),[['drive',false],['feed',false]]);
  const spoke=cli('speech',file);
  assert.equal(spoke.code,0,spoke.out);
  assert.match(spoke.out,/Narration drive: 4\.54s\nNarration feed: 4\.06s/);assert.doesNotMatch(spoke.out,/Generating/);
  const e=await loadEpisode(file);
  const resolved=await readJson(join(movie,'_build','movie-resolved.json'));
  assert.deepEqual(resolved,await readJson(join(fixtures,'resolved','two-chapters.json')));
  assert.equal(e.movie,'machinome-movie/0.1');assert.equal(e.format,'machinome-video-draft/0.4');
  assert.deepEqual(e.chapters,resolved.chapters);
  assert.equal(e.paths.episode,await realpath(file));assert.equal(e.paths.base,await realpath(movie));
  const checked=cli('check',file,'--viewer',viewer);
  assert.equal(checked.code,0,checked.out);assert.match(checked.out,/Two Chapters: 4 shots/);
  await prepareWordTimingForCommand(e,{command:'check'});
  const audio=await speech(e,{generate:false});
  assert.deepEqual(audio.records.map(r=>[r.id,r.offset]),e.chapters.map(c=>[c.id,c.start+c.speechOffset]));
  assert.equal(audio.captions[0].start,e.chapters[0].start+e.chapters[0].speechOffset);
  assert.ok(audio.captions.some(c=>c.start>=e.chapters[1].start+e.chapters[1].speechOffset-1e-9&&c.text.startsWith('Watch')));
  const p=await preview(e,{viewer,width:320});
  assert.equal(p.pixelReplay,true);
  assert.ok(p.emphasisChecks.length>0&&p.revealChecks.length>0&&p.pictureChecks.length>0);
  const output=await render(e,{viewer,audio});
  assert.equal(output,join(await realpath(movie),'_build','rehearsal.mp4'));
  const manifest=await readJson(join(movie,'_build','rehearsal-manifest.json'));
  assert.equal(manifest.count,Math.round(e.output.durationSeconds*e.output.fps));
  assert.deepEqual(manifest.probe.streams.map(s=>s.codec_type).sort(),['audio','video']);
  assert.equal(manifest.width,320);assert.equal(manifest.height,180);
  assert.equal(manifest.provenance.episodeSha256,hash(await readFile(file)));
  assert.match(await readFile(join(movie,'_build','rehearsal.srt'),'utf8'),/Water turns the wheel\./);
  assert.deepEqual(calls,[]);
});

// Takes layer: a provider double stands in for the service; the key is a
// placeholder the double never sends anywhere.
test('speech generates one take per chapter from the unresolved document, and only once',async t=>{
  const {file,doc}=await documentProject(t);
  const fetch=globalThis.fetch,key=process.env.ELEVENLABS_API_KEY,requests=[];
  process.env.ELEVENLABS_API_KEY='double-key-never-sent';
  t.onTestFinished(()=>{globalThis.fetch=fetch;if(key===undefined)delete process.env.ELEVENLABS_API_KEY;else process.env.ELEVENLABS_API_KEY=key;});
  globalThis.fetch=async(url,init)=>{
    const body=JSON.parse(init.body),chapter=doc.chapters.find(c=>c.narration===body.text);
    requests.push({url:String(url),text:body.text,previous:body.previous_text,next:body.next_text});
    const take=await readJson(join(fixtures,'takes','two-chapters',`${chapter.id}.json`));
    const pcm=Buffer.alloc(Math.round(take.duration*24000)*2);
    return new Response(JSON.stringify({audio_base64:pcm.toString('base64'),alignment:take.alignment}),
      {status:200,headers:{'content-type':'application/json'}});
  };
  const [drive,feed]=doc.chapters.map(c=>c.narration);
  const first=await generateMovieTakes(file);
  assert.deepEqual(first,[{id:'drive',generated:true},{id:'feed',generated:true}]);
  assert.deepEqual(requests.map(r=>[r.text,r.previous,r.next]),[[drive,undefined,feed],[feed,drive,undefined]]);
  assert.ok(requests.every(r=>r.url.endsWith('/text-to-speech/test-voice/with-timestamps?output_format=pcm_24000')));
  const again=await generateMovieTakes(file);
  assert.deepEqual(again,[{id:'drive',generated:false},{id:'feed',generated:false}]);
  assert.equal(requests.length,2);
  const e=await loadEpisode(file);
  assert.deepEqual(e.chapters,(await readJson(join(fixtures,'resolved','two-chapters.json'))).chapters);
});
