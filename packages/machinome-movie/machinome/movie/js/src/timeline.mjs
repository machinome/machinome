// Pure time mapping: no wall clock, browser state or mechanical equations.
import {codeAt} from './code.mjs';
import {ease,endSlope,keyedValue} from './easing.mjs';
// Accepted episode formats, oldest first. Each accepts everything the one before
// it does, with the same meaning; an episode without a format is a 0.2 episode.
export const FORMATS=['machinome-video-draft/0.2','machinome-video-draft/0.3','machinome-video-draft/0.4'];
export const formatAtLeast=(e,format)=>FORMATS.indexOf(e.format??FORMATS[0])>=FORMATS.indexOf(format);
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
// Camera keys ease position, target and field of view along the curve named by
// the key the move ends at (smooth unless it says otherwise). In a shot whose
// keys share one up, it is carried exactly as authored; in a shot whose up
// changes, up is always a unit vector: the two keys' unit directions mixed with
// the same weight and normalized again (a hold normalizes the held direction).
export function cameraAt(e,shot,local){
  let a=shot.camera[0],b=a;
  for(const key of shot.camera){if(key.at<=local)a=key;else{b=key;break;}b=a;}
  const ca=e.cameras[a.preset],cb=e.cameras[b.preset];
  const u=b.at===a.at?0:Math.min(1,(local-a.at)/(b.at-a.at));
  const w=ease(b.ease??'smooth',u);
  const mix=k=>ca[k].map((v,i)=>v+(cb[k][i]-v)*w);
  const fov=ca.fov===cb.fov?ca.fov:ca.fov+(cb.fov-ca.fov)*w;
  let up=ca.up;
  const upChanges=shot.camera.some(k=>JSON.stringify(e.cameras[k.preset].up)!==JSON.stringify(ca.up));
  if(upChanges){const ua=unit(ca.up),ub=unit(cb.up);up=unit(ua.map((v,i)=>v+(ub[i]-v)*w));}
  return {view:{camera:mix('position'),target:mix('target')},up,fov};
}
// Active annotations as data. Screen positions exist only in the posed page.
function annotationsAt(e,shot,on){
  return (shot.annotations??[]).flatMap((a,index)=>{
    if(!on(a))return [];
    const target=a.point?{point:a.point}:{paths:typeof a.part==='string'?e.layers[a.part]:[a.part]};
    const cue={index,kind:a.kind,text:a.text,target};
    if(a.text===undefined)delete cue.text;
    if(a.kind==='arrow')cue.place=a.place;else cue.offset=a.offset??[0,0];
    cue.safeInset=e.style.safeInsetFraction;
    return [cue];
  });
}
// The active highlight cue as data, with every choice explicit, or null.
function highlightAt(e,shot,on){
  const cue=(shot.highlight??[]).find(on);
  if(!cue)return null;
  return {paths:cue.parts.flatMap(part=>typeof part==='string'?e.layers[part]:[part]),
    others:cue.others??'keep',color:cue.color??e.style.accent};
}
// Model seconds per video second at a shot's end: the last segment's average
// rate times its curve's end slope, so a segment easing to rest, or a hold, holds.
export function endRate(shot){
  const s=shot.simulation,keys=s.keyframes??[{at:0,seconds:s.from},{at:shot.end-shot.start,seconds:s.to}];
  const a=keys.at(-2),b=keys.at(-1);
  return (b.seconds-a.seconds)/(b.at-a.at)*endSlope(b.ease??'linear');
}
// The frame of one shot at shot-local time. Past the shot's end, while a
// transition still shows it, the shot continues: its model runs on at its end
// rate, its camera holds its last key, the cues that ran to its end stay, and
// its code panel holds the completed excerpt.
function shotFrame(e,shot,local){
  const duration=shot.end-shot.start,past=local>=duration;
  const on=c=>local>=c.from&&(local<c.to||(past&&c.to===duration));
  const camera=cameraAt(e,shot,local);
  // Model keyframes are linear unless the key a segment ends at names a curve.
  const keys=shot.simulation.keyframes??[{at:0,seconds:shot.simulation.from},{at:duration,seconds:shot.simulation.to}];
  const modelSeconds=past?shot.simulation.to+endRate(shot)*(local-duration)
    :keyedValue(keys.map(k=>({at:k.at,value:k.seconds,ease:k.ease})),local,'linear');
  const frame={shotId:shot.id,time:modelSeconds/e.model.expectedDurationSeconds,
    view:camera.view,up:camera.up,fov:camera.fov,
    hidden:shot.hiddenLayers.flatMap(k=>e.layers[k]),
    overlays:shot.overlays.filter(on),
    code:codeAt(e,shot,local)};
  // Format 0.2 frames keep their exact shape; 0.3 and later frames always carry the new cues.
  if(formatAtLeast(e,FORMATS[1])){frame.annotations=annotationsAt(e,shot,on);frame.highlight=highlightAt(e,shot,on);}
  // 0.4 frames always carry transition; a frame posed on its own has none.
  if(formatAtLeast(e,FORMATS[2]))frame.transition=null;
  return frame;
}
// Normalized progress through a transition, allowing for the rounding of video
// time at the instants whose value must be exact (a midpoint, an end).
const settle=(x,k)=>Math.abs(x-k)<1e-9?k:x;
// The transition at video time t, or null (design D2, D4, D6). A transition
// occupies the first seconds of the shot that declares it and fadeOut the last;
// their bounds are compared in video time, as the shots' own are.
function transitionAt(e,index,t){
  const shot=e.shots[index],duration=shot.end-shot.start,local=t-shot.start;
  const base=(field,spec,kind)=>({field,kind,shotId:shot.id,duration:spec.duration,ease:spec.ease??'smooth'});
  const plate=(field,spec,opacity)=>({...base(field,spec,'fade'),color:spec.color??e.style.background,plate:opacity,picture:'incoming',outgoing:null});
  if(shot.fadeIn&&t<shot.start+shot.fadeIn.duration){
    const f=shot.fadeIn;return plate('fadeIn',f,1-ease(f.ease??'smooth',local/f.duration));
  }
  const x=shot.transition;
  if(x&&t<shot.start+x.duration){
    const prior=e.shots[index-1],u=local,d=x.duration,name=x.ease??'smooth';
    const outgoing=()=>shotFrame(e,prior,prior.end-prior.start+u);
    const join={...base('transition',x,x.kind),outgoingShotId:prior.id,start:shot.start};
    if(x.kind==='fade'){
      // Through the colour: the outgoing picture under a rising plate, then the incoming under a falling one.
      const h=settle(2*u/d,1);
      return h<1?{...join,color:x.color??e.style.background,plate:ease(name,h),picture:'outgoing',outgoing:outgoing()}
        :{...join,color:x.color??e.style.background,plate:1-ease(name,h-1),picture:'incoming',outgoing:null};
    }
    const t={...join,progress:ease(name,u/d)};
    if(x.kind!=='dissolve')t.direction=x.direction??'left';
    t.outgoing=outgoing();
    return t;
  }
  const f=shot.fadeOut;
  if(f&&t>=shot.end-f.duration){
    // Complete on the film's last frame, at end - 1/fps.
    const r=settle((local-(duration-f.duration))/(f.duration-1/e.output.fps),1);
    return plate('fadeOut',f,ease(f.ease??'smooth',Math.min(1,r)));
  }
  return null;
}
export function frameAt(e, t, captions=[]) {
  const index=e.shots.findIndex(s=>t>=s.start && t<s.end);
  if(index<0)throw new Error(`Frame time ${t} is outside the episode`);
  const shot=e.shots[index],frame=shotFrame(e,shot,t-shot.start);
  if(formatAtLeast(e,FORMATS[2]))frame.transition=transitionAt(e,index,t);
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
