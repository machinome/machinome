import {loadEnvFile} from 'node:process';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {hash,fileHash,json,command,duration} from './util.mjs';
import {captionsFromAlignment,srt} from './timeline.mjs';
import {validateAlignment,resolveWordTiming} from './words.mjs';

export function speechRequest(e,spoken,i){
  const v3=e.audio.model==='eleven_v3';
  const request={text:spoken[i],model_id:e.audio.model,
    voice_settings:e.audio.voiceSettings??(v3?{stability:.5,similarity_boost:.75}:{stability:.65,similarity_boost:.75,style:0,use_speaker_boost:true,speed:1}),seed:4217};
  if(!v3){request.previous_text=spoken[i-1];request.next_text=spoken[i+1];}
  return request;
}
const spokenShots=e=>e.shots.map(s=>{
  let text=s.narration;
  for(const [term,replacement]of Object.entries(e.audio.replacements??{}))text=text.replaceAll(term,replacement);
  return text;
});
// One key calculation for generation and for cache-only measured timing.
export function speechCacheEntry(e,spoken,i){
  const format=e.audio.outputFormat??'mp3_44100_128',request=speechRequest(e,spoken,i);
  const cache=hash(JSON.stringify({voice:e.audio.voice,request,format}));
  const file=resolve(e.paths.build,'audio',`${e.shots[i].id}-${cache.slice(0,16)}.${format.startsWith('pcm_')?'wav':'mp3'}`);
  return {format,request,cache,file,meta:file+'.json'};
}
export async function readSpeechTake(e,shot){
  const i=e.shots.indexOf(shot);
  if(i<0)throw new Error(`Unknown shot for word timing: ${shot?.id}`);
  const {file,meta}=speechCacheEntry(e,spokenShots(e),i);
  let record;
  try{record=JSON.parse(await readFile(meta,'utf8'));}
  catch(error){if(error.code==='ENOENT')throw new Error(`Word timing needs cached speech for shot ${shot.id}; run the speech command first (check, preview and render never generate speech)`);throw error;}
  let digest;
  try{digest=await fileHash(file);}
  catch(error){if(error.code==='ENOENT')throw new Error(`Word timing needs cached speech for shot ${shot.id}; run the speech command first (check, preview and render never generate speech)`);throw error;}
  if(record.sha256!==digest)throw new Error('Audio cache checksum mismatch');
  validateAlignment(record.alignment,`shot ${shot.id}`);
  return {file,sha256:digest,alignment:record.alignment,record};
}

// ElevenLabs PCM is mono signed 16-bit little-endian, without a container.
export function pcmWav(pcm,sampleRate){
  if(!pcm.length||pcm.length%2)throw new Error('Invalid PCM sample buffer');
  const header=Buffer.alloc(44);header.write('RIFF');header.writeUInt32LE(36+pcm.length,4);
  header.write('WAVEfmt ',8);header.writeUInt32LE(16,16);header.writeUInt16LE(1,20);
  header.writeUInt16LE(1,22);header.writeUInt32LE(sampleRate,24);header.writeUInt32LE(sampleRate*2,28);
  header.writeUInt16LE(2,32);header.writeUInt16LE(16,34);header.write('data',36);header.writeUInt32LE(pcm.length,40);
  return Buffer.concat([header,pcm]);
}

export async function mixSpeech(files,seconds,mix){
  // Resample before sample-accurate delay. Never trim/gate/fade an individual clip.
  const filters=files.map((f,i)=>`[${i}:a]aresample=48000,adelay=${Math.round(f.offset*48000)}S:all=1[a${i}]`);
  filters.push(files.map((_,i)=>`[a${i}]`).join('')+`amix=inputs=${files.length}:normalize=0,apad,atrim=duration=${seconds},loudnorm=I=-16:TP=-1.5:LRA=11[out]`);
  await command('ffmpeg',['-y','-v','error',...files.flatMap(f=>['-i',f.file]),'-filter_complex',filters.join(';'),'-map','[out]','-ar','48000','-ac','2',mix]);
}

export async function speech(e,{generate=false}={}) {
  const dir=resolve(e.paths.build,'audio');await mkdir(dir,{recursive:true});
  if(e.audio.provider!=='elevenlabs'||!e.audio.voice||!e.audio.model)throw new Error('Select ElevenLabs provider, model and voice in production.yaml');
  const format=e.audio.outputFormat??'mp3_44100_128';
  if(!['mp3_44100_128','pcm_24000'].includes(format))throw new Error('Supported speech output formats: mp3_44100_128, pcm_24000');
  let key;
  if(generate){
    try{loadEnvFile(fileURLToPath(new URL('../.env',import.meta.url)));}catch(error){if(error.code!=='ENOENT')throw error;}
    key=process.env.ELEVENLABS_API_KEY;
    if(!key)throw new Error('Set ELEVENLABS_API_KEY in Videomaker .env');
  }
  const files=[],captions=[],records=[];let overflow=[];
  const spoken=spokenShots(e);
  for(let i=0;i<e.shots.length;i++){
    const shot=e.shots[i];
    const {request,cache,file,meta}=speechCacheEntry(e,spoken,i);
    let record;
    try{record=JSON.parse(await readFile(meta,'utf8'));if(record.sha256!==await fileHash(file))throw new Error('Audio cache checksum mismatch');}
    catch(error){
      if(error.code!=='ENOENT')throw error;
      if(!generate)throw new Error(`Missing speech for ${shot.id}; run the speech command first`);
      console.log(`Generating narration: ${shot.id} (${request.text.length} characters)`);
      const response=await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(e.audio.voice)}/with-timestamps?output_format=${format}`,{
        method:'POST',headers:{'xi-api-key':key,'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(120000)});
      if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(`ElevenLabs HTTP ${response.status}: ${data.detail?.status??'request failed'} (key omitted)`);}
      const data=await response.json();
      if(!data.audio_base64)throw new Error('ElevenLabs returned no audio');
      const alignment=data.normalized_alignment??data.alignment;
      captionsFromAlignment(alignment); // Refuse unusable alignment before caching.
      const bytes=Buffer.from(data.audio_base64,'base64');
      await writeFile(file,format==='pcm_24000'?pcmWav(bytes,24000):bytes);
      record={cache,voice:e.audio.voice,model:e.audio.model,format,request,alignment,sha256:await fileHash(file),duration:await duration(file)};
      await json(meta,record);
    }
    const offset=shot.start+(shot.speechOffset??0.2);
    if(!Number.isFinite(offset)||offset<shot.start)throw new Error(`Invalid speech offset: ${shot.id}`);
    if(offset+record.duration>shot.end-0.1)overflow.push(`${shot.id}: audio ${record.duration.toFixed(2)}s, slot ${(shot.end-offset-.1).toFixed(2)}s`);
    const cues=captionsFromAlignment(record.alignment,offset);
    // Display the project's spelling while speaking the pronunciation alias.
    for(const cue of cues)for(const [term,replacement]of Object.entries(e.audio.replacements??{}))cue.text=cue.text.replaceAll(replacement,term);
    captions.push(...cues);files.push({file,offset});records.push({id:shot.id,file,sha256:record.sha256,duration:record.duration,offset});
    console.log(`Narration ${shot.id}: ${record.duration.toFixed(2)}s`);
  }
  if(overflow.length)throw new Error('Narration exceeds shot timing; revise YAML (audio is cached):\n'+overflow.join('\n'));
  await json(resolve(e.paths.build,'captions.json'),captions);
  await writeFile(resolve(e.paths.build,'captions.srt'),srt(captions));
  // Captions and the generated take stay cached if measured words reveal a
  // mismatch; the mix/manifest are not claimed as complete on that refusal.
  await resolveWordTiming(e,shot=>readSpeechTake(e,shot));
  const mix=resolve(e.paths.build,'narration.wav');
  await mixSpeech(files,e.output.durationSeconds,mix);
  await json(resolve(e.paths.build,'audio-manifest.json'),{provider:e.audio.provider,records,mixSha256:await fileHash(mix)});
  return {captions,mix,records};
}
