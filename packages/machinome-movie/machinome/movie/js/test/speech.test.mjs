import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp, mkdir, writeFile, readFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {speech,readSpeechTake} from '../src/speech.mjs';
import {hash} from '../src/util.mjs';

async function fixture(t, {cached=true, checksum=true}={}) {
  const build=await mkdtemp(join(tmpdir(),'videomaker-speech-test-'));
  t.after(()=>rm(build,{recursive:true,force:true}));
  const voice='test-voice', model='test-model';
  const request={text:'Hello.',model_id:model,
    voice_settings:{stability:.65,similarity_boost:.75,style:0,use_speaker_boost:true,speed:1},
    seed:4217,previous_text:undefined,next_text:undefined};
  const cache=hash(JSON.stringify({voice,request,format:'mp3_44100_128'}));
  const dir=join(build,'audio');await mkdir(dir);
  const file=join(dir,`hook-${cache.slice(0,16)}.mp3`);
  // Deliberately not playable audio: refusal must happen before mixing/decoding.
  const bytes=Buffer.from('cached speech fixture');
  if(cached){
    await writeFile(file,bytes);
    await writeFile(file+'.json',JSON.stringify({cache,request,sha256:checksum?hash(bytes):'wrong',duration:2,
      alignment:{characters:[...'Hello.'],character_start_times_seconds:[0,.1,.2,.3,.4,.5],
        character_end_times_seconds:[.1,.2,.3,.4,.5,.6]}}));
  }
  return {file,bytes,episode:{paths:{build},audio:{provider:'elevenlabs',voice,model},
    output:{durationSeconds:1},shots:[{id:'hook',start:0,end:1,narration:'Hello.'}]}};
}

test('cached speech overflow is refused without deleting the generated segment',async t=>{
  const {episode,file,bytes}=await fixture(t);
  await assert.rejects(speech(episode),/Narration exceeds shot timing.*\n.*hook: audio 2.00s, slot 0.70s/);
  assert.deepEqual(await readFile(file),bytes);
});

test('cache-only rendering refuses missing speech instead of generating it',async t=>{
  const {episode}=await fixture(t,{cached:false});
  await assert.rejects(speech(episode),/Missing speech for hook/);
});

test('corrupt cached speech is refused instead of silently regenerated',async t=>{
  const {episode}=await fixture(t,{checksum:false});
  await assert.rejects(speech(episode),/Audio cache checksum mismatch/);
});

test('word timing reads only the exact cached take and verifies its checksum without a key or network',async t=>{
  const {episode,file,bytes}=await fixture(t);
  const before=process.env.ELEVENLABS_API_KEY,fetch=globalThis.fetch;
  delete process.env.ELEVENLABS_API_KEY;
  globalThis.fetch=()=>{throw new Error('Network was called for cache-only word timing');};
  try{
    const take=await readSpeechTake(episode,episode.shots[0]);
    assert.equal(take.sha256,hash(bytes));
    assert.deepEqual(take.alignment.characters,[...'Hello.']);
    assert.equal(take.file,file);
    const missing=await fixture(t,{cached:false});
    await assert.rejects(readSpeechTake(missing.episode,missing.episode.shots[0]),
      /Word timing needs cached speech for shot hook; run the speech command first/);
    const corrupt=await fixture(t,{checksum:false});
    await assert.rejects(readSpeechTake(corrupt.episode,corrupt.episode.shots[0]),/Audio cache checksum mismatch/);
  }finally{globalThis.fetch=fetch;if(before===undefined)delete process.env.ELEVENLABS_API_KEY;else process.env.ELEVENLABS_API_KEY=before;}
});

test('speech leaves its cached take and written captions when measured text differs from the take',async t=>{
  const {episode,file,bytes}=await fixture(t);
  const meta=JSON.parse(await readFile(file+'.json','utf8'));
  meta.duration=.4;meta.alignment.characters=[...'Hallo.'];
  await writeFile(file+'.json',JSON.stringify(meta));
  episode.output.fps=30;
  episode.shots[0].overlays=[{from:0,to:1,position:'top',text:'Hello.',reveal:{timing:'spoken'}}];
  await assert.rejects(speech(episode),/Missing spoken phrase in recorded speech.*hook/);
  assert.deepEqual(await readFile(file),bytes);
  assert.match(await readFile(join(episode.paths.build,'captions.srt'),'utf8'),/Hallo\./);
});
