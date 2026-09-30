import {readFile, realpath} from 'node:fs/promises';
import {resolve, dirname, relative, isAbsolute} from 'node:path';
import {execFileSync} from 'node:child_process';
import {parseDocument, visit, isAlias, isScalar, isMap} from 'yaml';
import {loadSourceCode,validateCode,validateCodeSource} from './code.mjs';
import {cameraAt,endRate,FORMATS,formatAtLeast} from './timeline.mjs';
import {EASINGS,unknownEasing} from './easing.mjs';
import {splitWords,validateSpokenPair,evenCount} from './words.mjs';
import {validatePictureCues,loadPictures} from './pictures.mjs';

export function parseSource(source) {
  const doc = parseDocument(source, {version:'1.2', uniqueKeys:true});
  if (doc.errors.length || doc.warnings.length) throw new Error([...doc.errors,...doc.warnings].map(e=>e.message).join('\n'));
  visit(doc, (_, node) => {
    if (isAlias(node) || node?.anchor || node?.tag) throw new Error('YAML aliases, anchors and tags are not supported');
    if (isMap(node)) for (const pair of node.items) {
      if (!isScalar(pair.key) || typeof pair.key.value !== 'string' || pair.key.value === '<<')
        throw new Error('YAML keys must be unique strings; merge keys are not supported');
    }
  });
  return doc.toJS({maxAliasCount:0});
}
const need = (ok, message) => {if (!ok) throw new Error(message);};
const finite = n => typeof n === 'number' && Number.isFinite(n);
// The format list and its order live in timeline.mjs; code.mjs imports this
// module while timeline.mjs is still loading, so nothing here reads them at load.
export {FORMATS};
const V02='machinome-video-draft/0.2',V03='machinome-video-draft/0.3',V04='machinome-video-draft/0.4';
// Episodes without a format field are the unit-test shape of a 0.2 episode.
const formatOf=e=>e.format??FORMATS[0];
export function assemblyPaths(root) {
  const paths=new Set();
  (function walk(n,path=[]){paths.add(JSON.stringify(path));for(const child of n.children??[])walk(child,[...path,child.name]);})(root);
  return paths;
}
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const dot=(a,b)=>a.reduce((sum,v,i)=>sum+v*b[i],0);
// Before a viewer would refuse it mid-render: every output frame of a shot whose
// up changes keeps up at least about half a degree away from the view direction.
function validateUpAlongShot(e,s){
  const fps=e.output.fps,limit=Math.cos(.5*Math.PI/180);
  for(let i=Math.ceil(s.start*fps-1e-9);i/fps<s.end;i++){
    const local=i/fps-s.start,{view,up}=cameraAt(e,s,local);
    const forward=unit(view.target.map((v,k)=>v-view.camera[k]));
    need(Math.abs(dot(forward,unit(up)))<limit,`Camera up lies along the view direction in shot ${s.id} at ${(i/fps).toFixed(2)} s`);
  }
}
const within=(outer,inner)=>outer.length<=inner.length&&outer.every((name,i)=>name===inner[i]);
const isPath=p=>Array.isArray(p)&&p.length>0&&p.every(n=>typeof n==='string'&&n.length>0);
// A part target is a production layer name or one root-relative assembly path.
function targetPaths(e,s,part,known,where){
  if(typeof part==='string'){need(e.layers?.[part],`Unknown layer: ${part} (${where} in shot ${s.id})`);return e.layers[part];}
  need(isPath(part),`Invalid part: expected a layer name or an assembly path (${where} in shot ${s.id})`);
  need(known(part),`Missing assembly path: ${part.join('/')} (${where} in shot ${s.id})`);
  return [part];
}
function hiddenPaths(e,s){return (s.hiddenLayers??[]).flatMap(name=>e.layers?.[name]??[]);}
const pair=(v,lo,hi)=>Array.isArray(v)&&v.length===2&&v.every(n=>finite(n)&&n>=lo&&n<=hi);
const ANNOTATION_FIELDS=new Set(['from','to','kind','part','point','text','place','offset','padding','enter','leave']);
// Rings, padding, entrances and exits (format 0.4): the fields 0.3 does not know.
const MARK_FIELDS=['padding','enter','leave'];
const ENTRANCE_FIELDS=new Set(['kind','duration','ease']);
// Seconds as an author wrote them, without the binary remainder of a subtraction.
const seconds=x=>+x.toFixed(6);
// An entrance or exit (graphic-overlays D3, D7): `enter` is a fade or a draw-on,
// `leave` a fade; each at least two frames and within the cue.
function validateEntrance(e,s,a,i,field,bad){
  const x=a[field],what=field==='enter'?'entrance':'exit',where=`annotation #${i} in shot ${s.id}`;
  if(x===undefined)return;
  need(x&&typeof x==='object'&&!Array.isArray(x),bad(`${field} must be a mapping {kind, duration, ease}`));
  for(const key of Object.keys(x))need(ENTRANCE_FIELDS.has(key),`Unknown ${what} field: ${key} (${where})`);
  if(field==='enter'){
    need(['fade','draw'].includes(x.kind),bad('the entrance kind must be fade or draw'));
    need(!(x.kind==='draw'&&a.kind==='label'),bad('a label has no stroke to draw; enter with fade'));
  }else need(x.kind==='fade',bad('the exit kind must be fade'));
  if(x.ease!==undefined)need(EASINGS.includes(x.ease),`${unknownEasing(x.ease)} (${what} of ${where})`);
  const fps=e.output.fps,cue=seconds(a.to-a.from);
  need(finite(x.duration)&&x.duration*fps>=2-1e-9,bad(`the ${what} duration must be at least two frames (${(2/fps).toFixed(3)} s at ${fps} fps)`));
  need(x.duration<=cue+1e-9,bad(`the ${x.duration} s ${what} is longer than the cue (${cue} s)`));
}
function validateAnnotations(e,s,known){
  if(s.annotations===undefined)return;
  need(formatAtLeast(e,V03),`Annotations need format machinome-video-draft/0.3: shot ${s.id}`);
  need(Array.isArray(s.annotations),`Annotations must be a list: shot ${s.id}`);
  const inset=e.style?.safeInsetFraction;
  need(finite(inset)&&inset>=0&&inset<.5,`Annotations need a declared style.safeInsetFraction in [0, 0.5): shot ${s.id}`);
  const duration=s.end-s.start,hidden=hiddenPaths(e,s),marks=formatAtLeast(e,V04);
  s.annotations.forEach((a,i)=>{
    const where=`annotation #${i}`,bad=why=>`Invalid ${where} in shot ${s.id}: ${why}`;
    need(a&&typeof a==='object'&&!Array.isArray(a),bad('expected a mapping'));
    // Before 0.4 a ring or an entrance is asked to change its format, never
    // refused as an unknown kind or field (design D7).
    if(!marks){
      const used=[...(a.kind==='ring'?['kind: ring']:[]),...MARK_FIELDS.filter(key=>a[key]!==undefined)];
      need(!used.length,`Rings, entrances and exits need format machinome-video-draft/0.4: shot ${s.id} (${used[0]} in ${where})`);
    }
    for(const key of Object.keys(a))need(ANNOTATION_FIELDS.has(key),`Unknown annotation field: ${key} (${where} in shot ${s.id})`);
    need((marks?['arrow','label','ring']:['arrow','label']).includes(a.kind),bad(marks?'kind must be arrow, label or ring':'kind must be arrow or label'));
    need(finite(a.from)&&finite(a.to)&&a.from>=0&&a.from<a.to&&a.to<=duration,bad('times must satisfy 0 <= from < to <= shot duration'));
    if(a.kind==='ring')need(a.point===undefined,bad('a ring is drawn around a part; give part, not point'));
    need((a.part===undefined)!==(a.point===undefined),bad('give exactly one of part or point'));
    if(a.point!==undefined)need(Array.isArray(a.point)&&a.point.length===3&&a.point.every(finite),bad('point must be three finite numbers'));
    else for(const path of targetPaths(e,s,a.part,known,where))
      need(!hidden.some(h=>within(h,path)),`Annotated part is hidden in shot ${s.id}: ${path.join('/')} (${where})`);
    need(a.text===undefined||(typeof a.text==='string'&&a.text.trim().length>0),bad('text must be non-empty words'));
    if(a.kind==='ring'){
      need(a.text===undefined&&a.place===undefined&&a.offset===undefined,bad('a ring carries no text or place; add a label or an arrow beside it'));
      need(a.padding===undefined||(finite(a.padding)&&a.padding>=0&&a.padding<=.25),bad('padding must be a number in [0, 0.25]'));
    }else if(a.kind==='arrow'){
      need(a.offset===undefined,bad('offset belongs to a label; an arrow takes place'));
      need(pair(a.place,0,1),bad('an arrow needs place: [x, y] within the safe area, each in [0, 1]'));
    }else{
      need(a.place===undefined,bad('place belongs to an arrow; a label takes offset'));
      need(typeof a.text==='string'&&a.text.trim().length>0,bad('a label needs text'));
      need(a.offset===undefined||pair(a.offset,-1,1),bad('offset must be [dx, dy], each in [-1, 1]'));
    }
    if(a.kind!=='ring')need(a.padding===undefined,bad('padding belongs to a ring'));
    validateEntrance(e,s,a,i,'enter',bad);
    validateEntrance(e,s,a,i,'leave',bad);
    if(a.enter&&a.leave)need(a.enter.duration+a.leave.duration<=seconds(a.to-a.from)+1e-9,
      `Entrance and exit overlap in ${where} in shot ${s.id}: ${a.enter.duration} s in and ${a.leave.duration} s out exceed its ${seconds(a.to-a.from)} s`);
  });
}
const HIGHLIGHT_FIELDS=new Set(['from','to','parts','others','color']);
export const COLOR=/^#[0-9a-fA-F]{6}$/;
const OVERLAY_FIELDS=new Set(['from','to','text','position','reveal','subtitle','enter','leave']);
const REVEAL_SPOKEN=new Set(['timing','phrase']),REVEAL_EVEN=new Set(['timing','duration','ease']);
const TEXT_FADE_FIELDS=new Set(['kind','duration','ease']);
function validateOverlays(e,s){
  const modern=formatAtLeast(e,V04),duration=s.end-s.start,uses=[];
  for(const [i,cue] of s.overlays.entries()){
    const where=`overlay #${i} in shot ${s.id}`;
    need(cue&&typeof cue==='object'&&!Array.isArray(cue),`Invalid overlay: ${s.id}`);
    if(!modern&&(['reveal','subtitle','enter','leave'].some(key=>cue[key]!==undefined)||cue.position==='title'))
      throw new Error(`Text animation needs format machinome-video-draft/0.4: shot ${s.id}`);
    if(modern)for(const key of Object.keys(cue))need(OVERLAY_FIELDS.has(key),`Unknown overlay field: ${key} (${where})`);
    need(finite(cue.from)&&finite(cue.to)&&cue.from>=0&&cue.to>cue.from&&cue.to<=duration&&
      typeof cue.text==='string'&&['top','lower-third','center',...(modern?['title']:[])].includes(cue.position),`Invalid overlay: ${s.id}`);
    if(!modern)continue;
    if(cue.position==='title'){
      need(cue.subtitle===undefined||(typeof cue.subtitle==='string'&&cue.subtitle.trim()),`Invalid subtitle on title: ${where}`);
      for(const prior of uses)need(cue.from>=prior.to||cue.to<=prior.from,`Titles overlap in shot ${s.id}`);
      uses.push(cue);
    }else need(cue.subtitle===undefined&&cue.enter===undefined&&cue.leave===undefined,
      `Only a title may have subtitle, enter or leave: ${where}`);
    for(const field of ['enter','leave']){
      const fade=cue[field];if(fade===undefined)continue;
      need(fade&&typeof fade==='object'&&!Array.isArray(fade),`Invalid ${field}: ${where}`);
      for(const key of Object.keys(fade))need(TEXT_FADE_FIELDS.has(key),`Unknown ${field==='enter'?'entrance':'exit'} field: ${key} (${where})`);
      need(fade.kind==='fade',`Only fade is supported for title ${field}: ${where}`);
      need(finite(fade.duration)&&fade.duration>0&&fade.duration<=cue.to-cue.from,`Title ${field} needs a positive duration within its cue: ${where}`);
      if(fade.ease!==undefined)need(EASINGS.includes(fade.ease),`${unknownEasing(fade.ease)} (${field} of ${where})`);
    }
    need((cue.enter?.duration??0)+(cue.leave?.duration??0)<=cue.to-cue.from+1e-9,
      `Title entrance and exit overlap or exceed cue: ${where}`);
    if(cue.reveal!==undefined){
      const reveal=cue.reveal;
      need(reveal&&typeof reveal==='object'&&!Array.isArray(reveal),`Invalid reveal: ${where}`);
      need(['spoken','even'].includes(reveal.timing),`Invalid reveal timing: ${where}`);
      const fields=reveal.timing==='spoken'?REVEAL_SPOKEN:REVEAL_EVEN;
      for(const key of Object.keys(reveal))need(fields.has(key),`Unknown reveal field: ${key} (${where})`);
      const words=splitWords(cue.text).filter(p=>p.word);
      need(words.length>0,`Reveal needs words: ${where}`);
      if(reveal.timing==='spoken')validateSpokenPair({text:cue.text,phrase:reveal.phrase??cue.text,
        narration:s.narration,replacements:e.audio?.replacements??{},shotId:s.id,index:i});
      else{
        need(finite(reveal.duration)&&reveal.duration>0&&cue.from+reveal.duration<=cue.to+1e-9,
          `Even reveal duration exceeds cue: ${where}`);
        if(reveal.ease!==undefined)need(EASINGS.includes(reveal.ease),`${unknownEasing(reveal.ease)} (${where})`);
        // Every word must have one global film frame with that count visible.
        let shown=0;
        for(let frame=Math.ceil((s.start+cue.from)*e.output.fps-1e-9);
          frame/e.output.fps<s.start+cue.to-1e-9;frame++)
          shown=Math.max(shown,evenCount(words.length,frame/e.output.fps-s.start,cue.from,reveal.duration,reveal.ease??'linear'));
        need(shown>=words.length,
          `Even reveal word ${words.at(-1).text} appears on no output frame: ${where}`);
      }
    }
  }
}
function validateHighlight(e,s,known){
  if(s.highlight===undefined)return;
  need(formatAtLeast(e,V03),`Highlights need format machinome-video-draft/0.3: shot ${s.id}`);
  need(Array.isArray(s.highlight),`Highlight must be a list of cues: shot ${s.id}`);
  const duration=s.end-s.start,hidden=hiddenPaths(e,s);
  s.highlight.forEach((c,i)=>{
    const where=`highlight #${i}`,bad=why=>`Invalid ${where} in shot ${s.id}: ${why}`;
    need(c&&typeof c==='object'&&!Array.isArray(c),bad('expected a mapping'));
    for(const key of Object.keys(c))need(HIGHLIGHT_FIELDS.has(key),`Unknown highlight field: ${key} (${where} in shot ${s.id})`);
    need(finite(c.from)&&finite(c.to)&&c.from>=0&&c.from<c.to&&c.to<=duration,bad('times must satisfy 0 <= from < to <= shot duration'));
    // A string is a layer name and a list is one path; a bare path therefore reads as unknown layers.
    need(Array.isArray(c.parts)&&c.parts.length>0,bad('parts must be a non-empty list of layer names or assembly paths'));
    for(const part of c.parts)for(const path of targetPaths(e,s,part,known,where))
      need(!hidden.some(h=>within(h,path)),`Highlighted part is hidden in shot ${s.id}: ${path.join('/')} (${where})`);
    need(c.others===undefined||['keep','dim','ghost'].includes(c.others),bad('others must be keep, dim or ghost'));
    if(c.color===undefined)need(typeof e.style?.accent==='string'&&COLOR.test(e.style.accent),bad('the default colour style.accent must be a quoted #rrggbb'));
    else need(typeof c.color==='string'&&COLOR.test(c.color),bad('color must be a quoted #rrggbb'));
  });
  const cues=[...s.highlight].sort((a,b)=>a.from-b.from);
  for(let i=1;i<cues.length;i++)need(cues[i].from>=cues[i-1].to,`Highlight cues overlap in shot ${s.id}`);
}
// The lowest Viewer API an episode can be produced with, and why.
export function requiredViewerApi(e) {
  const reasons=[],first=e.cameras?.[e.shots?.[0]?.camera?.[0]?.preset];
  const differs=(c,d)=>c&&(c.fov!==d.fov||unit(c.up).some((v,i)=>Math.abs(v-unit(d.up)[i])>1e-12));
  for(const s of e.shots??[]){
    if(s.annotations?.length)reasons.push(`annotations (shot ${s.id})`);
    if(s.highlight?.length)reasons.push(`highlight (shot ${s.id})`);
    // The page mounts with the first camera's up and field of view; any other
    // lens or up, within a shot or across a cut, must be set on every setView.
    if(first&&s.camera?.some(k=>differs(e.cameras?.[k.preset],first)))reasons.push(`camera up/field of view (shot ${s.id})`);
  }
  return {api:reasons.length?28:21,reasons};
}
export function viewerApiRefusal(required,declared) {
  return `This episode needs Viewer API ${required.api} for ${required.reasons.join(', ')}; the selected viewer declares API ${declared}. Select a newer machinome-viewer bundle with --viewer.`;
}
// check has no browser: it reads the "viewer API <n>" banner of the selected bundle.
export function viewerApiFromBanner(text) {
  const match=/\bviewer API (\d+)\b/.exec(String(text).slice(0,4096));
  return match?Number(match[1]):null;
}
export function confirmViewerApi(required,bundleText) {
  if(required.api<=21)return null;
  const declared=bundleText==null?null:viewerApiFromBanner(bundleText);
  need(declared!==null,`Cannot confirm the viewer API: this episode needs Viewer API ${required.api} for ${required.reasons.join(', ')}, and the selected bundle is missing or declares no "viewer API" banner. Select a machinome-viewer bundle with --viewer.`);
  need(declared>=required.api,viewerApiRefusal(required,declared));
  return declared;
}
// Format 0.4 closes the field lists of a shot, its simulation, its model
// keyframes and its camera keys; 0.2 and 0.3 keep ignoring unknown fields.
const SHOT_FIELDS=new Set(['id','start','end','speechOffset','narration','direction','simulation','camera','hiddenLayers','overlays','evidence','code','layout','annotations','highlight','pictures','transition','fadeIn','fadeOut']);
const SIMULATION_FIELDS=new Set(['from','to','keyframes']);
const KEYFRAME_FIELDS=new Set(['at','seconds','ease']);
const CAMERA_KEY_FIELDS=new Set(['at','preset','ease']);
function closedFields(e,value,fields,message){
  if(!formatAtLeast(e,V04)||!value||typeof value!=='object')return;
  for(const key of Object.keys(value))need(fields.has(key),message(key));
}
// ease on a key names the curve of the segment that ends there (format 0.4).
function validateEase(e,s,key,i,what){
  if(key?.ease===undefined)return;
  need(formatAtLeast(e,V04),`Easing needs format machinome-video-draft/0.4: shot ${s.id}`);
  need(i>0,`Nothing to ease before the first ${what}: shot ${s.id}`);
  need(EASINGS.includes(key.ease),`${unknownEasing(key.ease)} (${what} #${i} in shot ${s.id})`);
}
// Joining shots (format 0.4): transition on any shot but the first, fadeIn on
// the first and fadeOut on the last. `index` is the shot's place in the film.
const TRANSITION_FIELDS=new Set(['kind','duration','ease','direction','color']);
const FADE_FIELDS=new Set(['duration','ease','color']);
const KINDS=['fade','dissolve','wipe','slide'];
function validateTransitions(e,s,index){
  const fields=['transition','fadeIn','fadeOut'].filter(field=>s[field]!==undefined);
  if(!fields.length)return;
  need(formatAtLeast(e,V04),`Transitions need format machinome-video-draft/0.4: shot ${s.id}`);
  const fps=e.output.fps,length=shot=>shot.end-shot.start,prior=e.shots[index-1];
  for(const field of fields){
    const x=s[field],bad=why=>`Invalid ${field} in shot ${s.id}: ${why}`;
    need(x&&typeof x==='object'&&!Array.isArray(x),bad('expected a mapping'));
    const known=field==='transition'?TRANSITION_FIELDS:FADE_FIELDS;
    for(const key of Object.keys(x))need(known.has(key),`Unknown ${field} field: ${key} (${field} in shot ${s.id})`);
    if(field==='transition'){
      need(index>0,bad('the first shot comes in from nothing; use fadeIn'));
      need(KINDS.includes(x.kind),bad('kind must be fade, dissolve, wipe or slide; omit transition for a cut'));
      if(['wipe','slide'].includes(x.kind))need(x.direction===undefined||['left','right'].includes(x.direction),bad('direction must be left or right'));
      else need(x.direction===undefined,bad('direction belongs to a wipe or slide'));
      if(x.kind!=='fade')need(x.color===undefined,bad('color belongs to a fade'));
    }
    if(field==='fadeIn')need(index===0,bad('only the first shot fades in; give this shot a transition of kind fade'));
    if(field==='fadeOut')need(index===e.shots.length-1,bad('only the last shot fades out; give the next shot a transition of kind fade'));
    if(field!=='transition'||x.kind==='fade'){
      if(x.color===undefined)need(typeof e.style?.background==='string'&&COLOR.test(e.style.background),bad('the default colour style.background must be a quoted #rrggbb'));
      else need(typeof x.color==='string'&&COLOR.test(x.color),bad('color must be a quoted #rrggbb'));
    }
    if(x.ease!==undefined)need(EASINGS.includes(x.ease),`${unknownEasing(x.ease)} (${field} in shot ${s.id})`);
    need(finite(x.duration)&&x.duration*fps>=2-1e-9,bad(`duration must be at least two frames (${(2/fps).toFixed(3)} s at ${fps} fps)`));
    if(field==='transition')need(x.duration<=length(prior),bad(`${x.duration} s is longer than shot ${prior.id} (${length(prior)} s)`));
    need(x.duration<=length(s),bad(`${x.duration} s is longer than shot ${s.id} (${length(s)} s)`));
  }
  const incoming=s.transition??s.fadeIn;
  if(incoming&&s.fadeOut)need(incoming.duration+s.fadeOut.duration<=length(s),
    `Transitions overlap in shot ${s.id}: ${incoming.duration} s in and ${s.fadeOut.duration} s out exceed its ${length(s)} s`);
  // The outgoing shot is seen for the whole transition, or half a fade, and
  // must not ask the viewer for a model second the export does not have.
  if(s.transition){
    const shown=s.transition.kind==='fade'?s.transition.duration/2:s.transition.duration;
    const reach=prior.simulation.to+endRate(prior)*shown,limit=e.model.expectedDurationSeconds;
    need(reach<=limit,`Shot ${prior.id} cannot continue ${shown} s into the ${s.transition.kind} to shot ${s.id}: its model would reach ${reach.toFixed(2)} s, past the export's ${limit} s; end its simulation earlier or shorten the transition`);
  }
}
export function validateEpisode(e, manifest) {
  need(FORMATS.includes(formatOf(e)),'Unsupported episode format');
  const paths=manifest.root?assemblyPaths(manifest.root):null;
  const known=path=>!paths||paths.has(JSON.stringify(path));
  need(manifest.animation?.loop === e.model.expectedDurationSeconds, 'Model duration differs from production settings; recheck the exported simulation');
  need(e.model.timeMode === 'normalized-loop' && !manifest.program && !manifest.clocked, 'Only posed normalized-loop models are supported');
  need(finite(e.model.expectedDurationSeconds) && e.model.expectedDurationSeconds > 0, 'Invalid model duration');
  for (const k of ['width','height','fps']) need(Number.isInteger(e.output[k]) && e.output[k] > 0, `Invalid output ${k}`);
  need(e.output.width%2===0 && e.output.height%2===0, 'Video dimensions must be even');
  need(finite(e.output.durationSeconds) && e.output.durationSeconds > 0 && Number.isInteger(e.output.durationSeconds*e.output.fps), 'Video duration must be a whole number of frames');
  for (const [name,c] of Object.entries(e.cameras)) {
    for (const k of ['position','target','up']) need(Array.isArray(c[k]) && c[k].length===3 && c[k].every(finite), `Invalid ${name}.${k}`);
    need(c.position.some((v,i)=>v!==c.target[i]), `Camera ${name} coincides with target`);
    need(c.up.some(v=>v!==0) && finite(c.fov) && c.fov>0 && c.fov<180, `Invalid camera ${name}`);
  }
  let end=0;const ids=new Set();
  need(Array.isArray(e.shots) && e.shots.length>0,'No shots');
  for (const [index,s] of e.shots.entries()) {
    need(typeof s.id==='string' && /^[a-z0-9-]+$/.test(s.id) && !ids.has(s.id), 'Shot ids must be unique slugs');ids.add(s.id);
    closedFields(e,s,SHOT_FIELDS,key=>`Unknown shot field: ${key} (shot ${s.id})`);
    need(s.start===end && finite(s.end) && s.end>s.start, `Shots must be contiguous: ${s.id}`);end=s.end;
    need(typeof s.narration==='string' && s.narration.trim() && typeof s.direction==='string', `Missing narration/direction: ${s.id}`);
    need(s.speechOffset===undefined||(finite(s.speechOffset)&&s.speechOffset>=0&&s.speechOffset<s.end-s.start),`Invalid speech offset: ${s.id}`);
    if(s.layout!==undefined){
      need(formatOf(e)===V04,`Source-only layout needs format machinome-video-draft/0.4: shot ${s.id}`);
      need(s.layout==='source-only',`Unknown layout: ${s.layout} (shot ${s.id})`);
      need(s.code,`Source-only layout needs pinned code in shot ${s.id}`);
      for(const field of ['annotations','highlight','pictures'])
        need(!s[field]?.length,`Source-only layout cannot use ${field} in shot ${s.id}`);
    }
    validateCode(e,s);
    closedFields(e,s.simulation,SIMULATION_FIELDS,key=>`Unknown simulation field: ${key} (shot ${s.id})`);
    need(finite(s.simulation.from) && finite(s.simulation.to) && s.simulation.from>=0 && s.simulation.to>=s.simulation.from && s.simulation.to<=e.model.expectedDurationSeconds,`Invalid simulation range: ${s.id}`);
    if(s.simulation.keyframes){
      const keys=s.simulation.keyframes;
      need(keys.length>=2&&keys[0].at===0&&keys[0].seconds===s.simulation.from&&keys.at(-1).at===s.end-s.start&&keys.at(-1).seconds===s.simulation.to,`Invalid model keyframe endpoints: ${s.id}`);
      keys.forEach((k,i)=>{
        closedFields(e,k,KEYFRAME_FIELDS,key=>`Unknown model keyframe field: ${key} (keyframe #${i} in shot ${s.id})`);
        validateEase(e,s,k,i,'model keyframe');
      });
      for(let i=0;i<keys.length;i++)need(finite(keys[i].at)&&finite(keys[i].seconds)&&keys[i].seconds>=s.simulation.from&&keys[i].seconds<=s.simulation.to&&(i===0||(keys[i].at>keys[i-1].at&&keys[i].seconds>=keys[i-1].seconds)),`Invalid model keyframes: ${s.id}`);
    }
    need(Array.isArray(s.camera) && s.camera.length>0 && s.camera[0].at===0,`Missing initial camera: ${s.id}`);
    let at=-1;let prior;
    for (const [i,key] of s.camera.entries()) {
      closedFields(e,key,CAMERA_KEY_FIELDS,field=>`Unknown camera key field: ${field} (key #${i} in shot ${s.id})`);
      validateEase(e,s,key,i,'camera key');
      const c=e.cameras[key.preset];need(c && finite(key.at) && key.at>at && key.at<=s.end-s.start,`Invalid camera key: ${s.id}`);at=key.at;
      if(prior&&formatOf(e)===V02)need(c.fov===prior.fov && JSON.stringify(c.up)===JSON.stringify(prior.up),`Changing FOV/up within a shot is not supported: shot ${s.id}; use format machinome-video-draft/0.3 with Viewer API 28`);
      if(prior)need(dot(unit(c.up),unit(prior.up))>=-.99,`Camera up reverses between keys in shot ${s.id}; add an intermediate preset`);
      prior=c;
    }
    if(formatAtLeast(e,V03)&&s.camera.some(k=>JSON.stringify(e.cameras[k.preset].up)!==JSON.stringify(e.cameras[s.camera[0].preset].up)))
      validateUpAlongShot(e,s);
    for(const name of s.hiddenLayers)need(e.layers[name],`Unknown layer: ${name}`);
    validateOverlays(e,s);
    for(const name of s.evidence)need(e.evidence[name],`Unknown evidence: ${name}`);
    validateAnnotations(e,s,known);
    validateHighlight(e,s,known);
    validatePictureCues(e,s);
  }
  // After every shot is known to be sound: a transition reads the shots on both sides.
  for(const [index,s] of e.shots.entries())validateTransitions(e,s,index);
  need(end===e.output.durationSeconds,'Shots must cover the video duration');
}
export async function loadEpisode(file) {
  const episodePath=await realpath(file), base=dirname(episodePath);
  const script=parseSource(await readFile(episodePath,'utf8'));
  need(FORMATS.includes(script.format),'Unsupported episode format');
  const productionPath=await realpath(resolve(base,script.production));
  const p=parseSource(await readFile(productionPath,'utf8'));
  const e={...p,...script};
  const manifestPath=await realpath(resolve(dirname(productionPath),p.model.manifest));
  const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
  validateEpisode(e,manifest);
  const paths=assemblyPaths(manifest.root);
  for(const layer of Object.values(e.layers)) for(const path of layer) need(paths.has(JSON.stringify(path)),`Missing assembly path: ${path.join('/')}`);
  for(const path of Object.values(e.evidence)) await readFile(resolve(dirname(productionPath),path));
  const repository=execFileSync('git',['rev-parse','--show-toplevel'],{cwd:base,encoding:'utf8'}).trim();
  need(!relative(repository,base).startsWith('..'),'Episode must live inside its project repository');
  const sourceRevision=(await readFile(resolve(dirname(manifestPath),'source-revision.txt'),'utf8')).trim();
  need(e.model.sourceRevision===sourceRevision,'Pin model.sourceRevision to the export source-revision.txt before rendering');
  e.paths={episode:episodePath,production:productionPath,manifest:manifestPath,repository,build:resolve(base,'_build')};
  e.sourceCode=await loadSourceCode(e);
  for(const shot of e.shots)validateCodeSource(e,shot);
  await loadPictures(e);
  return e;
}

export function contained(root,path) {
  const rel=relative(root,path);
  return !isAbsolute(rel) && rel!=='..' && !rel.startsWith('../');
}
