// The player's pure parts (the player-page change, design D3 to D9): what a
// live session's outline and frames mean to the page, with no DOM and no
// clock. Snapping to the film's frames; the request the stage page is posed
// by, which is the renderer's, a composed join shown as a cut at its midpoint
// and a shot's fade without its plate; the surface an address names; the
// ruler's geometry and the time under a pointer; the readout; and what a new
// generation asks of the page.

/** /film.json, as src/live.mjs serves it (the live-server change, D5; marks, the player-page change, D3). */
export interface Outline {
  id:string;
  title:string;
  output:{width:number;height:number;fps:number;duration:number};
  chapters:{id:string;start:number;end:number}[];
  shots:{id:string;chapter:string;start:number;end:number;set:string;join:{kind:string;duration:number}|null;model?:unknown}[];
  cues:{shot:string;id:string;at:number;until:number|null}[];
  marks:{name:string;shot:string;at:number}[];
  takes:Record<string,{kind:'clocked'|'loop';duration:number;marks:{name:string;time:number}[];url?:string}>;
  speech:{mix:boolean;captions:boolean};
  stage:{sha256:string};
  viewer:{api:number};
  generation:{number:number;loadedAt:string};
  refusal:{message:string;at:string}|null;
}
/** A frame as /frame gives it (frameAt of src/timeline.mjs). */
export interface Frame {
  time:number;
  chapterId:string;
  shotId:string;
  set:string;
  slots:Record<string,string>;
  elements:Record<string,unknown>;
  transition:Transition|null;
  [field:string]:unknown;
}
export interface Transition {
  field:'transition'|'fadeIn'|'fadeOut';
  kind:string;
  shotId:string;
  duration:number;
  start?:number;
  progress?:number;
  boxes?:Record<string,number[]>;
  outgoing?:Frame|null;
  [field:string]:unknown;
}
export type Surface={readonly kind:'movie'}|{readonly kind:'take';readonly key:string};
export interface Caption {text:string;start:number;end:number}
/** The generation event of /events. */
export interface GenerationEvent {number:number;loadedAt:string;stageSha256:string;exportChanged:boolean}

const EPSILON=1e-9;
const seconds=(value:number)=>String(Number(value.toFixed(3)));

// ----- snapping -----

/**
 * The frame of `t` on a grid of `fps` over `duration`: index round(t·fps),
 * clamped to the first frame and the last. A film's last frame is before its
 * end (`exclusive`: the server's rule, so the last instant is
 * (count − 1) / fps); a take's last instant is its end (`inclusive`), the end
 * itself when it is off the grid.
 */
export function snap(t:number,{fps,duration,end}:{fps:number;duration:number;end:'exclusive'|'inclusive'})
  :{index:number;time:number;count:number}{
  if(typeof t!=='number'||!Number.isFinite(t))throw new Error(`snap: ${String(t)} is not a time in seconds`);
  const whole=Math.round(duration*fps);
  if(end==='exclusive'){
    const index=Math.min(Math.max(Math.round(t*fps),0),whole-1);
    return {index,time:index/fps,count:whole};
  }
  // The take's end is reachable: one frame more when the end is off the grid.
  const last=Math.abs(whole/fps-duration)<=EPSILON?whole:Math.ceil(duration*fps-EPSILON);
  const index=Math.min(Math.max(Math.round(t*fps),0),last);
  return {index,time:Math.min(index/fps,duration),count:last+1};
}

// ----- the stage request -----

/** What the page shows of a transition the stage does not compose. */
export interface Shown {field:Transition['field'];kind:string;into:string;duration:number;shown:'cut'|'live'|'unfaded'}
const COMPOSED=new Set(['dissolve','wipe','slide','fade']);
const without=(frame:Frame)=>{const {transition:_,...rest}=frame;return rest as Frame;};

/**
 * The request the stage page is posed by for `frame`, as the renderer's
 * `show` makes it: the frame without its transition, and a reframe's
 * progress and boxes, which the stage draws live (ADR-010). Inside a
 * composed join the outgoing frame is posed before the join's midpoint (for
 * a fade, while the frame carries an outgoing picture, the same half) and
 * the frame itself from the midpoint on; a shot's fade in or out is posed
 * without its plate. Returns the request, the shot it poses, and what is
 * shown of the transition.
 */
export function stageRequest(frame:Frame):{request:Frame;posed:string;shown:Shown|null}{
  const x=frame.transition;
  if(!x)return {request:without(frame),posed:frame.shotId,shown:null};
  const shown=(as:Shown['shown']):Shown=>({field:x.field,kind:x.kind,into:x.shotId,duration:x.duration,shown:as});
  if(x.field!=='transition')return {request:without(frame),posed:frame.shotId,shown:shown('unfaded')};
  if(x.kind==='reframe')
    return {request:{...without(frame),transition:{kind:'reframe',progress:x.progress,boxes:x.boxes} as unknown as Transition},
      posed:frame.shotId,shown:shown('live')};
  if(COMPOSED.has(x.kind)){
    const outgoing=x.kind==='fade'?Boolean(x.outgoing):frame.time-(x.start??frame.time)<x.duration/2-EPSILON;
    if(outgoing&&x.outgoing)return {request:without(x.outgoing),posed:x.outgoing.shotId,shown:shown('cut')};
    return {request:without(frame),posed:frame.shotId,shown:shown('cut')};
  }
  return {request:without(frame),posed:frame.shotId,shown:null};
}

/** The readout's words for what is shown of a transition. */
export function joinWords(shown:Shown|null):string|null{
  if(!shown)return null;
  const d=`${seconds(shown.duration)} s`;
  if(shown.shown==='unfaded')return `${shown.field==='fadeIn'?'fade in':'fade out'}, ${d}: shown without its fade`;
  if(shown.shown==='live')return `${shown.kind} into ${shown.into}, ${d}: drawn live`;
  return `${shown.kind} into ${shown.into}, ${d}: shown as a cut at its midpoint`;
}

// ----- the surface an address names -----

const LABELS:Record<string,string>={take:'Take',loop:'Loop'};
/** Every surface of the outline, with its address and its label: the movie, then each take. */
export function surfacesOf(outline:Outline):{hash:string;label:string;surface:Surface}[]{
  return [{hash:'#movie',label:'Movie',surface:{kind:'movie'}},
    ...Object.keys(outline.takes).map(key=>({hash:`#take/${key}`,label:LABELS[key]??key,surface:{kind:'take',key} as Surface}))];
}
/**
 * The surface `hash` names; an empty or unknown hash is the default, the
 * movie when the outline has chapters, else the first take, with the address
 * that names it.
 */
export function routeOf(hash:string,outline:Outline):{surface:Surface;hash:string;known:boolean}{
  const all=surfacesOf(outline),found=all.find(s=>s.hash===hash);
  if(found)return {surface:found.surface,hash:found.hash,known:true};
  const fallback=outline.chapters.length||all.length===1?all[0]:all[1];
  return {surface:fallback.surface,hash:fallback.hash,known:false};
}

// ----- the ruler -----

export interface Ruler {
  duration:number;
  bands:{id:string;from:number;to:number}[];
  segments:{id:string;chapter:string;start:number;from:number;to:number}[];
  joins:{shot:string;kind:string;from:number;to:number}[];
  ticks:{shot:string;id:string;at:number;x:number}[];
  flags:{name:string;at:number;x:number}[];
}
/** The duration a surface moves through: the film's, or the take's in seconds. */
export function durationOf(outline:Outline,surface:Surface):number{
  return surface.kind==='movie'?outline.output.duration:outline.takes[surface.key].duration;
}
/**
 * The ruler of a surface, in fractions of its duration: on the movie surface
 * the chapters as bands, the shots as segments, each shot's incoming join
 * over its span, the cues as ticks and the marks where frames reach them; on
 * the take surface the take's marks only.
 */
export function rulerOf(outline:Outline,surface:Surface):Ruler{
  const duration=durationOf(outline,surface),x=(t:number)=>Math.min(1,Math.max(0,t/duration));
  if(surface.kind==='take')
    return {duration,bands:[],segments:[],joins:[],ticks:[],
      flags:outline.takes[surface.key].marks.map(m=>({name:m.name,at:m.time,x:x(m.time)}))};
  return {duration,
    bands:outline.chapters.map(c=>({id:c.id,from:x(c.start),to:x(c.end)})),
    segments:outline.shots.map(s=>({id:s.id,chapter:s.chapter,start:s.start,from:x(s.start),to:x(s.end)})),
    joins:outline.shots.filter(s=>s.join).map(s=>({shot:s.id,kind:s.join!.kind,from:x(s.start),to:x(s.start+s.join!.duration)})),
    ticks:outline.cues.map(c=>({shot:c.shot,id:c.id,at:c.at,x:x(c.at)})),
    flags:outline.marks.map(m=>({name:m.name,at:m.at,x:x(m.at)}))};
}
/** The time under a pointer at `fraction` of the ruler's width, clamped to the ruler. */
export function timeAt(fraction:number,ruler:Ruler):number{
  return Math.min(1,Math.max(0,Number.isFinite(fraction)?fraction:0))*ruler.duration;
}

// ----- the readout -----

export interface Readout {
  time:string;
  frame:number;
  count:number;
  shot:string|null;
  chapter:string|null;
  mark:string|null;
  join:string|null;
  caption:string|null;
}
/** The grid a surface snaps to. */
export function gridOf(outline:Outline,surface:Surface){
  return {fps:outline.output.fps,duration:durationOf(outline,surface),end:surface.kind==='movie'?'exclusive' as const:'inclusive' as const};
}
/** The marks of a surface, by their time on it. */
export function marksOf(outline:Outline,surface:Surface):{name:string;at:number}[]{
  return surface.kind==='movie'?outline.marks.map(m=>({name:m.name,at:m.at}))
    :outline.takes[surface.key].marks.map(m=>({name:m.name,at:m.time}));
}
/**
 * Where the playhead is, at the time posed: the time, its frame of the
 * count, the shot and chapter holding it (movie surface), the mark within
 * half a frame of it, the join as the page shows it, and the caption that
 * holds it.
 */
export function readoutOf({outline,surface,time,shown,captions}:
  {outline:Outline;surface:Surface;time:number;shown:Shown|null;captions:Caption[]|null}):Readout{
  const fps=outline.output.fps,{index,count}=snap(time,gridOf(outline,surface)),movie=surface.kind==='movie';
  const holds=(start:number,end:number)=>time>=start-EPSILON&&time<end-EPSILON;
  const shot=movie?outline.shots.find(s=>holds(s.start,s.end))?.id??null:null;
  const chapter=movie?outline.chapters.find(c=>holds(c.start,c.end))?.id??null:null;
  const mark=marksOf(outline,surface).find(m=>Math.abs(m.at-time)<0.5/fps-EPSILON)?.name??null;
  const caption=movie&&captions?captions.find(c=>holds(c.start,c.end))?.text??null:null;
  return {time:`${time.toFixed(2)} s`,frame:index,count,shot,chapter,mark,join:movie?joinWords(shown):null,caption};
}

// ----- the reload -----

export type ReloadAction='none'|'pose-again'|'reload-stage'|'reattach'|'remount';
/**
 * What a generation event asks of the page that holds generation `held`:
 * nothing for the generation held; on the movie surface, the next one with
 * the same stage page and export poses again, any other reloads the stage
 * page; on the take surface, the next one whose export did not change
 * attaches the transport again, any other remounts the viewer. A generation
 * that skips one is a change, since exportChanged compares only with the one
 * before it.
 */
export function reloadAction(surface:'movie'|'take',held:{number:number;stageSha256:string},event:GenerationEvent):ReloadAction{
  if(event.number<=held.number)return 'none';
  const next=event.number===held.number+1;
  if(surface==='movie')return next&&event.stageSha256===held.stageSha256&&!event.exportChanged?'pose-again':'reload-stage';
  return next&&!event.exportChanged?'reattach':'remount';
}
