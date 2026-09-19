// Pure time mapping: no wall clock, browser state or mechanical equations.
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
  return {shotId:shot.id,time:modelSeconds/e.model.expectedDurationSeconds,
    view:{camera:mix('position'),target:mix('target')},up:ca.up,fov:ca.fov,
    hidden:shot.hiddenLayers.flatMap(k=>e.layers[k]),
    overlays:shot.overlays.filter(o=>local>=o.from&&local<o.to),
    caption:captions.find(c=>t>=c.start&&t<c.end)?.text??''};
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
