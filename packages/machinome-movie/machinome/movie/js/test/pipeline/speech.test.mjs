// Layer 7 and 8: the speech command over cached takes, on a one-shot YAML
// episode loaded as the command line loads it (a YAML shot is one chapter).
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdir, writeFile, readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {speech,readSpeechTake,speechCacheEntry,spokenChapters} from '../../src/speech.mjs';
import {hash} from '../../src/util.mjs';
import {yamlProject} from '../support/yaml-project.mjs';

async function fixture(t, {cached=true, checksum=true, overlays=[]}={}) {
  const project=await yamlProject(t,{manifest:{root:{name:'test'},animation:{loop:1}}});
  const voice='test-voice', model='test-model';
  const episode=await project.film({format:'machinome-video-draft/0.4',title:'Speech',
    output:{width:320,height:180,fps:30,durationSeconds:1},model:{expectedDurationSeconds:1},
    audio:{provider:'elevenlabs',voice,model},cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},
    shots:[{id:'hook',start:0,end:1,narration:'Hello.',direction:'Say it.',simulation:{from:0,to:1},
      camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays,evidence:[]}]});
  const build=episode.paths.build;
  // The cache key, literally: a legacy-model request for the chapter's text.
  const request={text:'Hello.',model_id:model,
    voice_settings:{stability:.65,similarity_boost:.75,style:0,use_speaker_boost:true,speed:1},
    seed:4217,previous_text:undefined,next_text:undefined};
  const cache=hash(JSON.stringify({voice,request,format:'mp3_44100_128'}));
  const dir=join(build,'audio');await mkdir(dir,{recursive:true});
  const file=join(dir,`hook-${cache.slice(0,16)}.mp3`);
  assert.equal(speechCacheEntry(episode,spokenChapters(episode),0).file,file,'the key of the chapter\'s take');
  // Deliberately not playable audio: refusal must happen before mixing/decoding.
  const bytes=Buffer.from('cached speech fixture');
  if(cached){
    await writeFile(file,bytes);
    await writeFile(file+'.json',JSON.stringify({cache,request,sha256:checksum?hash(bytes):'wrong',duration:2,
      alignment:{characters:[...'Hello.'],character_start_times_seconds:[0,.1,.2,.3,.4,.5],
        character_end_times_seconds:[.1,.2,.3,.4,.5,.6]}}));
  }
  return {file,bytes,episode};
}
const shot=episode=>episode.chapters[0].shots[0];

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
    const take=await readSpeechTake(episode,shot(episode));
    assert.equal(take.sha256,hash(bytes));
    assert.deepEqual(take.alignment.characters,[...'Hello.']);
    assert.equal(take.file,file);
    const missing=await fixture(t,{cached:false});
    await assert.rejects(readSpeechTake(missing.episode,shot(missing.episode)),
      /Word timing needs cached speech for shot hook; run the speech command first/);
    const corrupt=await fixture(t,{checksum:false});
    await assert.rejects(readSpeechTake(corrupt.episode,shot(corrupt.episode)),/Audio cache checksum mismatch/);
  }finally{globalThis.fetch=fetch;if(before===undefined)delete process.env.ELEVENLABS_API_KEY;else process.env.ELEVENLABS_API_KEY=before;}
});

test('speech leaves its cached take and written captions when measured text differs from the take',async t=>{
  const {episode,file,bytes}=await fixture(t,{overlays:[{from:0,to:1,position:'top',text:'Hello.',reveal:{timing:'spoken'}}]});
  const meta=JSON.parse(await readFile(file+'.json','utf8'));
  meta.duration=.4;meta.alignment.characters=[...'Hallo.'];
  await writeFile(file+'.json',JSON.stringify(meta));
  await assert.rejects(speech(episode),/Missing spoken phrase in recorded speech.*hook/);
  assert.deepEqual(await readFile(file),bytes);
  assert.match(await readFile(join(episode.paths.build,'captions.srt'),'utf8'),/Hallo\./);
});
