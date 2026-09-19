import {loadEnvFile} from 'node:process';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
import {hash,fileHash,json,command,duration} from './util.mjs';
import {captionsFromAlignment,srt} from './timeline.mjs';

export async function speech(e,{generate=false}={}) {
  const dir=resolve(e.paths.build,'audio');await mkdir(dir,{recursive:true});
  if(e.audio.provider!=='elevenlabs'||!e.audio.voice||!e.audio.model)throw new Error('Select ElevenLabs provider, model and voice in production.yaml');
  let key;
  if(generate){
    try{loadEnvFile(fileURLToPath(new URL('../.env',import.meta.url)));}catch(error){if(error.code!=='ENOENT')throw error;}
    key=process.env.ELEVENLABS_API_KEY;
    if(!key)throw new Error('Set ELEVENLABS_API_KEY in Videomaker .env');
  }
  const files=[],captions=[],records=[];let overflow=[];
  const spoken=e.shots.map(s=>{
    let text=s.narration;
    for(const [term,replacement]of Object.entries(e.audio.replacements??{}))text=text.replaceAll(term,replacement);
    return text;
  });
  for(let i=0;i<e.shots.length;i++){
    const shot=e.shots[i];
    const request={text:spoken[i],model_id:e.audio.model,
      voice_settings:e.audio.voiceSettings??{stability:.65,similarity_boost:.75,style:0,use_speaker_boost:true,speed:1},
      seed:4217,previous_text:spoken[i-1],next_text:spoken[i+1]};
    const cache=hash(JSON.stringify({voice:e.audio.voice,request,format:'mp3_44100_128'}));
    const file=resolve(dir,`${shot.id}-${cache.slice(0,16)}.mp3`),meta=file+'.json';
    let record;
    try{record=JSON.parse(await readFile(meta,'utf8'));if(record.sha256!==await fileHash(file))throw new Error('Audio cache checksum mismatch');}
    catch(error){
      if(error.code!=='ENOENT')throw error;
      if(!generate)throw new Error(`Missing speech for ${shot.id}; run the speech command first`);
      console.log(`Generating narration: ${shot.id} (${request.text.length} characters)`);
      const response=await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${encodeURIComponent(e.audio.voice)}/with-timestamps?output_format=mp3_44100_128`,{
        method:'POST',headers:{'xi-api-key':key,'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(120000)});
      if(!response.ok){const data=await response.json().catch(()=>({}));throw new Error(`ElevenLabs HTTP ${response.status}: ${data.detail?.status??'request failed'} (key omitted)`);}
      const data=await response.json();
      if(!data.audio_base64)throw new Error('ElevenLabs returned no audio');
      const alignment=data.normalized_alignment??data.alignment;
      captionsFromAlignment(alignment); // Refuse unusable alignment before caching.
      await writeFile(file,Buffer.from(data.audio_base64,'base64'));
      record={cache,voice:e.audio.voice,model:e.audio.model,request,alignment,sha256:await fileHash(file),duration:await duration(file)};
      await json(meta,record);
    }
    const offset=shot.start+(shot.speechOffset??0.2);
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
  const filters=files.map((f,i)=>`[${i}:a]adelay=${Math.round(f.offset*1000)}:all=1[a${i}]`);
  filters.push(files.map((_,i)=>`[a${i}]`).join('')+`amix=inputs=${files.length}:normalize=0,apad,atrim=duration=${e.output.durationSeconds},loudnorm=I=-16:TP=-1.5:LRA=11[out]`);
  const mix=resolve(e.paths.build,'narration.wav');
  await command('ffmpeg',['-y','-v','error',...files.flatMap(f=>['-i',f.file]),'-filter_complex',filters.join(';'),'-map','[out]','-ar','48000','-ac','2',mix]);
  await json(resolve(e.paths.build,'audio-manifest.json'),{provider:e.audio.provider,records,mixSha256:await fileHash(mix)});
  return {captions,mix,records};
}
