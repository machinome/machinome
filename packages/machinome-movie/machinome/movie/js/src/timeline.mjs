// The frame: a pure function of the resolved document and video time (design
// D4 of the react-stage change; docs/movie-document.md, "The frame"). No wall
// clock, browser state or mechanical equations. `film` is the resolved
// document with what its load attached: the excerpts' pinned text
// (`excerpts`) and the pictures' probes (`pictureMedia`).
import {sourceState} from './code.mjs';
import {ease,endSlope,keyedValue} from './easing.mjs';
import {splitWords,evenCount} from './words.mjs';
import {viewAt,clipFrameAt} from './pictures.mjs';
import {effectiveStyle} from './style.mjs';
import {boundedMatches} from './text.mjs';
import {typedCount} from './words.mjs';
import {bankAt} from './take.mjs';

// Accepted YAML episode formats, oldest first (docs/FORMAT.md). Each accepts
// everything the one before it does, with the same meaning; an episode without
// a format is a 0.2 episode.
export const FORMATS=['machinome-video-draft/0.2','machinome-video-draft/0.3','machinome-video-draft/0.4'];
export const formatAtLeast=(e,format)=>FORMATS.indexOf(e.format??FORMATS[0])>=FORMATS.indexOf(format);
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const near=(a,b)=>Math.abs(a-b)<1e-9;
// Normalized progress through an entrance or exit or a transition, settled at
// its ends so the rounding of video time cannot leave it a hair short.
const settled=x=>Math.abs(x)<1e-9?0:Math.abs(x-1)<1e-9?1:x;
const settle=(x,k)=>Math.abs(x-k)<1e-9?k:x;

// A YAML camera key list as the old timeline read it, kept for the episode's
// own checks (validateEpisode): camera at shot-local time.
export function cameraAt(e,shot,local){
  let a=shot.camera[0],b=a;
  for(const key of shot.camera){if(key.at<=local)a=key;else{b=key;break;}b=a;}
  const ca=e.cameras[a.preset],cb=e.cameras[b.preset];
  const u=b.at===a.at?0:Math.min(1,(local-a.at)/(b.at-a.at));
  return between(ca,cb,ease(b.ease??'smooth',u),shot.camera.some(k=>JSON.stringify(e.cameras[k.preset].up)!==JSON.stringify(ca.up)));
}
// Position, target and field of view mixed by the eased weight w; up carried
// exactly when the two cameras share it, otherwise their unit directions mixed
// and normalized again.
function between(ca,cb,w,upChanges=JSON.stringify(ca.up)!==JSON.stringify(cb.up)){
  const mix=k=>ca[k].map((v,i)=>v+(cb[k][i]-v)*w);
  const fov=ca.fov===cb.fov?ca.fov:ca.fov+(cb.fov-ca.fov)*w;
  let up=ca.up;
  if(upChanges){const ua=unit(ca.up),ub=unit(cb.up);up=unit(ua.map((v,i)=>v+(ub[i]-v)*w));}
  return {view:{camera:mix('position'),target:mix('target')},up,fov};
}
// Model seconds per video second at a shot's end: the last segment's average
// rate times its curve's end slope, so a segment easing to rest, or a hold, holds.
export function endRate(shot){
  const duration=shot.end-shot.start,m=shot.model;
  const keys=m.keys??[{at:0,seconds:m.from},{at:duration,seconds:m.to}];
  const a=keys.at(-2),b=keys.at(-1);
  return (b.seconds-a.seconds)/(b.at-a.at)*endSlope(b.ease??'linear');
}
export function modelSecondsAt(shot,local){
  const duration=shot.end-shot.start,m=shot.model;
  const keys=m.keys??[{at:0,seconds:m.from},{at:duration,seconds:m.to}];
  if(local>=duration)return keys.at(-1).seconds+endRate(shot)*(local-duration);
  // Model keyframes are linear unless the key a segment ends at names a curve.
  return keyedValue(keys.map(k=>({at:k.at,value:k.seconds,ease:k.ease})),local,'linear');
}

// Derived, per film, once: every shot with its chapter and index, and where
// each view's camera stands when each shot starts (its last move's camera in
// an earlier shot of the chapter). Pure; cached by the film object.
const derived=new WeakMap();
function index(film){
  let d=derived.get(film);if(d)return d;
  const shots=[],cameraAtStart=new Map();
  for(const chapter of film.chapters){
    const standing=new Map();
    for(const [key,element] of Object.entries(chapter.elements))if(element.kind==='view')standing.set(key,element.camera);
    for(const shot of chapter.shots){
      shots.push({chapter,shot,index:shots.length});
      for(const [key,camera] of standing)cameraAtStart.set(`${shot.id}/${key}`,camera);
      for(const {action,cue} of actionsOf(shot).filter(x=>x.action.action==='move').sort((a,b)=>a.cue.at-b.cue.at))
        standing.set(action.element,action.camera);
    }
  }
  d={shots,cameraAtStart};derived.set(film,d);return d;
}
// Every action of a shot with its cue and its place (cues[i].actions[j]).
function actionsOf(shot){
  return shot.cues.flatMap((cue,i)=>cue.actions.map((action,j)=>({cue,action,id:`cues[${i}].actions[${j}]`})));
}
// A spanning action is on from its at, inclusive, to its until, exclusive;
// past the shot's end (a transition's continuation) one that ran to the end stays.
const on=(from,to,local,duration,past)=>local>=from-1e-9&&(local<to-1e-9||(past&&near(to,duration)));
function fade(action,from,to,local){
  const x=action.enter,y=action.leave;
  const first=x?ease(x.ease??'smooth',settled((local-from)/x.duration)):1;
  const last=y?1-ease(y.ease??'smooth',settled((local-(to-y.duration))/y.duration)):1;
  return {first,last};
}
const pathsOf=(film,part)=>typeof part==='string'?film.layers[part]:[part];

function viewState(film,chapter,shot,key,element,local,past){
  const duration=shot.end-shot.start,own=actionsOf(shot).filter(x=>x.action.element===key);
  // The camera: where the view stood when the shot began, then its moves.
  let current=index(film).cameraAtStart.get(`${shot.id}/${key}`)??element.camera,camera=null;
  const moves=own.filter(x=>x.action.action==='move').sort((a,b)=>a.cue.at-b.cue.at);
  // In a shot whose moves change the view's up, up is always a unit vector,
  // held or moving (docs/FORMAT.md, "camera"); otherwise it is carried exactly.
  const upOf=name=>JSON.stringify(film.cameras[name].up);
  const upChanges=moves.some(({action})=>upOf(action.camera)!==upOf(current));
  for(const {cue,action} of moves){
    if(local<cue.at)break;
    if(local<action.until){
      const u=Math.min(1,(local-cue.at)/(action.until-cue.at));
      camera=between(film.cameras[current],film.cameras[action.camera],ease(action.ease??'smooth',u),upChanges);break;
    }
    current=action.camera;
  }
  if(!camera){const c=film.cameras[current];camera={view:{camera:[...c.position],target:[...c.target]},up:upChanges?unit(c.up):c.up,fov:c.fov};}
  const highlight=own.find(x=>x.action.action==='highlight'&&on(x.cue.at,x.cue.until,local,duration,past));
  const style=effectiveStyle(film.style);
  const marks=own.flatMap(({cue,action,id})=>{
    if(!['ring','label','arrow'].includes(action.action))return [];
    if(!on(cue.at,cue.until,local,duration,past)||(past&&action.leave))return [];
    const mark={id,kind:action.action,target:action.point?{point:action.point}:{paths:pathsOf(film,action.part)}};
    if(action.text!==undefined)mark.text=action.text;
    if(action.action==='arrow')mark.place=action.place;
    else if(action.action==='ring')mark.padding=action.padding??.01;
    else mark.offset=action.offset??[0,0];
    const {first,last}=fade(action,cue.at,cue.until,local);
    mark.opacity=Math.min(action.enter?.kind==='fade'?first:1,last);
    mark.drawn=action.enter?.kind==='draw'?first:1;
    return [mark];
  });
  // A view on a clocked take carries the machine's whole bank at its take
  // time (src/take.mjs, ADR-012); a view on a posed loop, the loop's time.
  const seconds=modelSecondsAt(shot,local);
  const pose=film.model.timeMode==='take'?{bank:bankAt(film.take,seconds)}:{time:seconds/film.model.expectedDurationSeconds};
  return {kind:'view',...pose,
    view:camera.view,up:camera.up,fov:camera.fov,
    hidden:(element.hide??[]).flatMap(name=>film.layers[name]),
    highlight:highlight?{paths:highlight.action.parts.flatMap(p=>pathsOf(film,p)),
      others:highlight.action.others??'keep',color:highlight.action.color??style.accent}:null,
    marks};
}
function titleState(shot,key,element,local,past){
  const duration=shot.end-shot.start;
  const shown=actionsOf(shot).find(x=>x.action.element===key&&x.action.action==='show'&&on(x.cue.at,x.cue.until,local,duration,past));
  const base={kind:'title',shown:Boolean(shown),text:element.text,...(element.subtitle!==undefined?{subtitle:element.subtitle}:{})};
  if(!shown)return {...base,opacity:0};
  const {cue,action}=shown,{first,last}=fade(action,cue.at,cue.until,local),state={...base,opacity:Math.min(first,last)};
  const reveal=action.reveal;
  if(reveal){
    state.words=splitWords(element.text);
    if(reveal.timing==='spoken'){
      if(!reveal.onsets)throw new Error(`Word timing is not resolved: shot ${shot.id}`);
      state.revealed=reveal.onsets.filter(t=>local>=Math.max(cue.at,t)-1e-9).length;
    }else state.revealed=evenCount(state.words.filter(p=>p.word).length,local,cue.at,reveal.duration,reveal.ease??'linear');
  }
  return state;
}
function pictureState(film,shot,key,element,local,past){
  const duration=shot.end-shot.start,media=element.still!==undefined?'still':'clip',name=element[media];
  const shown=actionsOf(shot).find(x=>x.action.element===key&&x.action.action==='show'&&on(x.cue.at,x.cue.until,local,duration,past));
  const base={kind:'picture',shown:Boolean(shown),media,name,fit:element.fit??'contain'};
  if(!shown)return {...base,opacity:0};
  const {cue,action}=shown,{first,last}=fade(action,cue.at,cue.until,local);
  const state={...base,opacity:past&&action.leave?0:Math.min(first,last)};
  if(media==='still')state.view=viewAt(action.view,local);
  else{
    const probe=film.pictureMedia?.clips?.[name];
    if(!probe)throw new Error(`Picture media is not resolved: ${name} in shot ${shot.id}`);
    state.view={center:[.5,.5],zoom:1};
    state.clipSeconds=(element.inPoint??0)+Math.max(0,local-cue.at);
    state.frame=clipFrameAt(probe.timestamps,state.clipSeconds);
  }
  return state;
}
function projectState(shot,key,element,local,past){
  const duration=shot.end-shot.start;
  const actions=actionsOf(shot).filter(x=>x.action.element===key&&on(x.cue.at,x.cue.until,local,duration,past))
    .map(({cue,action})=>({action:action.action,params:action.params,since:cue.at,until:cue.until,
      progress:Math.min(1,Math.max(0,settled((local-cue.at)/(cue.until-cue.at))))}));
  return {kind:element.kind,props:element.props,actions};
}

// The frame of one shot at shot-local time. Past the shot's end, while a
// transition still shows it, the shot continues (design D4).
function shotFrame(film,chapter,shot,local,time){
  const past=local>=shot.end-shot.start,slots={},elements={};
  for(const [slot,key] of Object.entries(shot.places)){
    const element=chapter.elements[key],id=`${chapter.id}.${key}`;
    slots[slot]=id;
    elements[id]=element.kind==='view'?viewState(film,chapter,shot,key,element,local,past)
      :element.kind==='source'?sourceState(film,chapter,shot,key,element,local)
      :element.kind==='title'?titleState(shot,key,element,local,past)
      :element.kind==='picture'?pictureState(film,shot,key,element,local,past)
      :projectState(shot,key,element,local,past);
  }
  return {time,chapterId:chapter.id,shotId:shot.id,set:shot.set,slots,elements,transition:null};
}
// The seconds a join shows its outgoing shot past that shot's end: half of a
// fade, the whole of a dissolve, wipe or slide, none of a reframe, whose
// outgoing shot is not drawn.
export const joinShows=join=>!join?0:join.kind==='fade'?join.duration/2:join.kind==='reframe'?0:join.duration;
// The view elements a reframe moves: those its shot and the shot before it
// both place (a view element belongs to its chapter, so two chapters' shots
// share none), each with its frame key and the slot holding it in either set.
export function movingViews(outgoingChapter,outgoing,chapter,shot){
  if(outgoingChapter.id!==chapter.id)return [];
  const slotOf=(places,key)=>Object.keys(places).find(slot=>places[slot]===key);
  return Object.entries(shot.places).filter(([,key])=>chapter.elements[key]?.kind==='view'&&slotOf(outgoing.places,key)!==undefined)
    .map(([slot,key])=>({key:`${chapter.id}.${key}`,element:key,from:{set:outgoing.set,slot:slotOf(outgoing.places,key)},to:{set:shot.set,slot}}));
}
// The words a reframe without a view element in both shots is refused in, by
// both runtimes (python/machinome_movie/names.py says the same).
export const noViewInBoth=(outgoing,incoming)=>`a reframe from shot ${outgoing} into shot ${incoming} moves a view element both shots place, and there is no view element in both`;

// The reframe into a shot, `local` seconds after it starts (clamped to the
// join): the incoming shot is drawn live; each view element both shots place
// is drawn in a box (fractions of the frame) between its slot's box in the
// outgoing set and its slot's box in the incoming set, by the eased progress,
// and every other element at the progress as opacity. The boxes are the
// film's measured `reframes` (src/layout.mjs); none is ever guessed.
export function reframeAt(film,shotId,local){
  const {shots}=index(film),at=shots.find(s=>s.shot.id===shotId);
  if(!at||at.shot.transition?.kind!=='reframe')throw new Error(`Shot ${shotId} does not come in by a reframe`);
  const {shot,index:i}=at,x=shot.transition,measured=film.reframes?.[shot.id];
  if(!measured)throw new Error(`Shot ${shot.id} comes in by a reframe whose slot boxes are not measured; check and every browser session measure them on the stage`);
  const p=settled(ease(x.ease??'smooth',Math.min(local,x.duration)/x.duration));
  const boxes=Object.fromEntries(Object.entries(measured).map(([key,{from,to}])=>[key,from.box.map((v,k)=>(1-p)*v+p*to.box[k])]));
  return {field:'transition',kind:'reframe',shotId:shot.id,duration:x.duration,ease:x.ease??'smooth',
    outgoingShotId:shots[i-1].shot.id,start:shot.start,progress:p,outgoing:null,boxes};
}

// The transition at video time t, or null. A transition occupies the first
// seconds of the shot that declares it and fadeOut the last.
function transitionAt(film,at,t){
  const {chapter,shot,index:i}=at,duration=shot.end-shot.start,local=t-shot.start,style=effectiveStyle(film.style);
  const base=(field,spec,kind)=>({field,kind,shotId:shot.id,duration:spec.duration,ease:spec.ease??'smooth'});
  const plate=(field,spec,opacity)=>({...base(field,spec,'fade'),color:spec.color??style.background,plate:opacity,picture:'incoming',outgoing:null});
  if(shot.fadeIn&&t<shot.start+shot.fadeIn.duration){
    const f=shot.fadeIn;return plate('fadeIn',f,1-ease(f.ease??'smooth',local/f.duration));
  }
  const x=shot.transition;
  if(x&&t<shot.start+x.duration){
    if(x.kind==='reframe')return reframeAt(film,shot.id,local);
    const prior=index(film).shots[i-1],u=local,d=x.duration,name=x.ease??'smooth';
    const outgoing=()=>shotFrame(film,prior.chapter,prior.shot,prior.shot.end-prior.shot.start+u,t);
    const join={...base('transition',x,x.kind),outgoingShotId:prior.shot.id,start:shot.start};
    if(x.kind==='fade'){
      // Through the colour: the outgoing picture under a rising plate, then the incoming under a falling one.
      const h=settle(2*u/d,1);
      return h<1?{...join,color:x.color??style.background,plate:ease(name,h),picture:'outgoing',outgoing:outgoing()}
        :{...join,color:x.color??style.background,plate:1-ease(name,h-1),picture:'incoming',outgoing:null};
    }
    const result={...join,progress:ease(name,u/d)};
    if(x.kind!=='dissolve')result.direction=x.direction??'left';
    result.outgoing=outgoing();
    return result;
  }
  const f=shot.fadeOut;
  if(f&&t>=shot.end-f.duration){
    // Complete on the film's last frame, at end - 1/fps.
    const r=settle((local-(duration-f.duration))/(f.duration-1/film.output.fps),1);
    return plate('fadeOut',f,ease(f.ease??'smooth',Math.min(1,r)));
  }
  return null;
}
export function frameAt(film,t){
  const at=index(film).shots.find(({shot})=>t>=shot.start&&t<shot.end);
  if(!at)throw new Error(`Frame time ${t} is outside the film`);
  const frame=shotFrame(film,at.chapter,at.shot,t-at.shot.start,t);
  frame.transition=transitionAt(film,at,t);
  return frame;
}
// Every shot of the film in order with its chapter and index.
export const filmShots=film=>index(film).shots;
export const shotActions=actionsOf;

// Where each emphasised token is in its excerpt's text (UTF-16 offsets, as
// the stage's ranges count), on its line when the action names one.
export function tokenRange(snippet,token,line){
  const text=snippet.text;
  if(line===undefined){const [start]=boundedMatches(text,token);return {start,end:start+token.length};}
  const lines=text.split('\n'),index=line-snippet.lines[0];
  const lineStart=lines.slice(0,index).reduce((n,s)=>n+s.length+1,0);
  const [within]=boundedMatches(lines[index],token);
  return {start:lineStart+within,end:lineStart+within+token.length};
}

// The checks of a loaded movie that need its excerpts, its media or its
// frames (design D2.4). A YAML film is checked by validateEpisode instead.
export function checkFilm(film){
  const {shots}=index(film),fps=film.output.fps;
  for(const {chapter,shot,index:i} of shots){
    const where=`chapter ${chapter.id}, shot ${shot.id}`,duration=shot.end-shot.start;
    for(const {cue,action,id} of actionsOf(shot)){
      const element=chapter.elements[action.element];
      if(action.action==='emphasize'){
        const snippet=film.excerpts[element.source],cps=text=>Array.from(text).length;
        action.words.forEach((word,k)=>{
          const range=tokenRange(snippet,word.token,action.line);
          const typed=typedAt(film,chapter,shot,action.element,word.at);
          if(cps(snippet.text.slice(0,range.end))>typed)
            throw new Error(`${where}, ${id}, words[${k}].token: the token '${word.token}' is not yet typed when '${word.spoken}' is spoken (${(shot.start+word.at).toFixed(2)} s)`);
        });
      }
      if(element.kind==='picture'&&element.clip!==undefined){
        const media=film.pictureMedia.clips[element.clip],next=shots[i+1]?.shot.transition;
        const continuation=near(cue.until,duration)?joinShows(next):0;
        const required=(element.inPoint??0)+(cue.until-cue.at)+continuation;
        if(required>media.end+1e-9)throw new Error(`${where}, ${id}: clip ${element.clip} ends at ${media.end.toFixed(2)} s, before the ${required.toFixed(2)} s the cue and its continuation need`);
      }
    }
    // Every output frame keeps a view's up at least about half a degree away
    // from its view direction, before a viewer would refuse it mid-render.
    for(const [slot,key] of Object.entries(shot.places)){
      if(chapter.elements[key].kind!=='view')continue;
      for(let n=Math.ceil(shot.start*fps-1e-9);n/fps<shot.end-1e-9;n++){
        const state=viewState(film,chapter,shot,key,chapter.elements[key],n/fps-shot.start,false);
        const forward=unit(state.view.target.map((v,k)=>v-state.view.camera[k]));
        const cos=Math.abs(forward.reduce((s,v,k)=>s+v*unit(state.up)[k],0));
        if(!(cos<Math.cos(.5*Math.PI/180)))throw new Error(`Camera up lies along the view direction in shot ${shot.id} (places.${slot}) at ${(n/fps).toFixed(2)} s`);
      }
    }
  }
}
// Characters a source panel has typed at shot-local `local`, across its chapter.
export function typedAt(film,chapter,shot,key,local){
  const element=chapter.elements[key],snippet=film.excerpts[element.source];
  const lines=snippet.text.split('\n'),upTo=through=>Array.from(lines.slice(0,through-snippet.lines[0]+1).join('\n')).length;
  let prior=0;
  for(const s of chapter.shots){
    if(s===shot)break;
    for(const {action} of actionsOf(s))if(action.element===key&&action.action==='type')prior=Math.max(prior,upTo(action.throughLine));
  }
  const typings=actionsOf(shot).filter(x=>x.action.element===key&&x.action.action==='type')
    .map(({cue,action})=>({at:cue.at,over:action.over,throughLine:action.throughLine}));
  if(!typings.length)return prior;
  // Continue from where the chapter's typing stopped.
  let count=prior,from=prior;
  for(const cue of typings){
    const end=upTo(cue.throughLine);
    if(local<cue.at)break;
    count=from+Math.floor((end-from)*Math.min(1,(local-cue.at)/cue.over));
    if(local<cue.at+cue.over)break;
    from=end;
  }
  return count;
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
