// Pure time mapping: no wall clock, browser state or mechanical equations.
import {codeAt} from './code.mjs';
const V03='machinome-video-draft/0.3';
// Active annotations as data. Screen positions exist only in the posed page.
function annotationsAt(e,shot,local){
  return (shot.annotations??[]).flatMap((a,index)=>{
    if(!(local>=a.from&&local<a.to))return [];
    const target=a.point?{point:a.point}:{paths:typeof a.part==='string'?e.layers[a.part]:[a.part]};
    const cue={index,kind:a.kind,text:a.text,target};
    if(a.text===undefined)delete cue.text;
    if(a.kind==='arrow')cue.place=a.place;else cue.offset=a.offset??[0,0];
    cue.safeInset=e.style.safeInsetFraction;
    return [cue];
  });
}
// The active highlight cue as data, with every choice explicit, or null.
function highlightAt(e,shot,local){
  const cue=(shot.highlight??[]).find(c=>local>=c.from&&local<c.to);
  if(!cue)return null;
  return {paths:cue.parts.flatMap(part=>typeof part==='string'?e.layers[part]:[part]),
    others:cue.others??'keep',color:cue.color??e.style.accent};
}
export function frameAt(e, t, captions=[]) {
  const shot=e.shots.find(s=>t>=s.start && t<s.end);
  if(!shot)throw new Error(`Frame time ${t} is outside the episode`);
  const local=t-shot.start,duration=shot.end-shot.start;
  let a=shot.camera[0],b=a;
  for(const key of shot.camera){if(key.at<=local)a=key;else{b=key;break;}b=a;}
  const ca=e.cameras[a.preset],cb=e.cameras[b.preset];
  const u=b.at===a.at?0:Math.min(1,(local-a.at)/(b.at-a.at));
  const ease=u*u*(3-2*u);
  const mix=k=>ca[k].map((v,i)=>v+(cb[k][i]-v)*ease);
  const keys=shot.simulation.keyframes??[{at:0,seconds:shot.simulation.from},{at:duration,seconds:shot.simulation.to}];
  const index=keys.findIndex((k,i)=>i+1<keys.length&&local>=k.at&&local<keys[i+1].at);
  const left=keys[Math.max(0,index)],right=keys[Math.max(0,index)+1];
  const modelSeconds=left.seconds+(right.seconds-left.seconds)*(local-left.at)/(right.at-left.at);
  const frame={shotId:shot.id,time:modelSeconds/e.model.expectedDurationSeconds,
    view:{camera:mix('position'),target:mix('target')},up:ca.up,fov:ca.fov,
    hidden:shot.hiddenLayers.flatMap(k=>e.layers[k]),
    overlays:shot.overlays.filter(o=>local>=o.from&&local<o.to),
    code:codeAt(e,shot,local)};
  // Format 0.2 frames keep their exact shape; 0.3 frames always carry the new cues.
  if(e.format===V03){frame.annotations=annotationsAt(e,shot,local);frame.highlight=highlightAt(e,shot,local);}
  return frame;
}

export function captionsFromAlignment(a, offset=0) {
  if(!a?.characters?.length)throw new Error('Speech response has no character alignment');
  if(a.characters.length!==a.character_start_times_seconds?.length||a.characters.length!==a.character_end_times_seconds?.length)throw new Error('Malformed speech alignment');
  const words=[];let start=-1;
  for(let i=0;i<=a.characters.length;i++){
    if(i<a.characters.length&&!/\s/.test(a.characters[i])) {if(start<0)start=i;}
    else if(start>=0){words.push({text:a.characters.slice(start,i).join(''),start:offset+a.character_start_times_seconds[start],end:offset+a.character_end_times_seconds[i-1]});start=-1;}
  }
  const cues=[];let group=[];
  function flush(){if(group.length)cues.push({text:group.map(w=>w.text).join(' '),start:group[0].start,end:group.at(-1).end});group=[];}
  for(const word of words){
    if(group.length && (group.map(w=>w.text).join(' ').length+word.text.length>56 || word.end-group[0].start>3.8))flush();
    group.push(word);if(/[.!?]$/.test(word.text))flush();
  }
  flush();return cues;
}

export function srt(cues) {
  const stamp=t=>{let ms=Math.round(t*1000);const h=Math.floor(ms/3600000);ms%=3600000;const m=Math.floor(ms/60000);ms%=60000;const s=Math.floor(ms/1000);ms%=1000;return `${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')},${String(ms).padStart(3,'0')}`;};
  return cues.map((c,i)=>`${i+1}\n${stamp(c.start)} --> ${stamp(c.end)}\n${c.text}\n`).join('\n');
}
