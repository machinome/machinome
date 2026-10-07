// The player page (the player-page change; ADR-022): a live session's film
// shown by two transports over what the renderer uses. The movie surface
// poses the renderer's frames (/frame) on the render's own stage page
// (/film.html) through window.film.setFrame, its clock the narration or a
// timer; the take surface poses a take on the viewer alone through the take
// transport. Shared: the ruler and its scrubber, the keys, the readout under
// the frame, the refusals, and the reload the session's events ask for. The
// page draws nothing in the film's frame and says what it cannot show.
import './player.css';
import {attachLoop,attachTake,type TakeTransport,type TakeDocument} from '../transport/take';
import {audioClock,timerClock,type Clock} from '../transport/clock';
import type {ViewerFactory,ViewerInstance} from '../transport/viewer-handle';
import {durationOf,gridOf,marksOf,readoutOf,reloadAction,routeOf,rulerOf,snap,stageRequest,surfacesOf,timeAt,
  type Caption,type Frame,type GenerationEvent,type Outline,type Ruler,type Shown,type Surface} from './model';
import {poser,type Poser} from './poser';

/** What the page calls of the stage page's window.film (stage/runtime.tsx), structurally. */
interface StageFilm {
  setFrame(frame:unknown):Promise<unknown>;
  transport(key:string):unknown;
  views():{key:string|null;instance:number;visible:boolean}[];
}
type StageWindow=Window&{film?:StageFilm;filmError?:string};
/** The page's state, for the proofs and for a page that frames it. Provisional: not a protocol. */
export interface PlayerState {
  surface():string;
  time():number;
  frame():number;
  playing():boolean;
  generation():number;
  poses():number[];
  observed():unknown;
  take():TakeTransport|null;
  seek(t:number):void;
  play():void;
  pause():void;
  idle():Promise<void>;
}
declare global {
  interface Window {MachinomeViewer?:ViewerFactory;player?:PlayerState}
}

const $=<T extends HTMLElement>(id:string)=>{const el=document.getElementById(id);if(!el)throw new Error(`The player page has no #${id}`);return el as T;};
const nextFrame=()=>new Promise<void>(resolve=>requestAnimationFrame(()=>resolve()));
const message=(error:unknown)=>error instanceof Error?error.message:String(error);
async function fetched(url:string):Promise<Response>{
  const res=await fetch(url,{cache:'no-store'});
  if(!res.ok)throw new Error(`${url}: ${res.status} ${(await res.text()).trim()}`);
  return res;
}
const getJson=async<T>(url:string)=>(await (await fetched(url)).json()) as T;

// ----- what the page shows of itself -----

let outline:Outline;
let held={number:0,stageSha256:''};
let captions:Caption[]|null=null;
let active:Instance|null=null;
let loadRefusal:string|null=null,fault:string|null=null,note:string|null=null,reloading=false;

function showMessages(){
  const set=(id:string,text:string|null)=>{const el=$(id);el.hidden=!text;el.textContent=text??'';};
  set('refusal',loadRefusal?`The last change was refused; the film shown is the last one accepted.\n${loadRefusal}`:null);
  set('fault',fault);set('note',note);
  $('status').textContent=`generation ${held.number}${reloading?', reloading':''}`;
}
function showSurfaces(){
  const nav=$('surfaces');nav.replaceChildren();
  for(const {hash,label} of surfacesOf(outline)){
    const a=document.createElement('a');a.href=hash;a.textContent=label;
    if(location.hash===hash)a.setAttribute('aria-current','page');
    nav.append(a);
  }
  $('title').textContent=outline.title;document.title=`${outline.title}: Videomaker player`;
}

// ----- the ruler and the readout -----

const pct=(x:number)=>`${(x*100).toFixed(4)}%`;
function drawRuler(ruler:Ruler,surface:Surface){
  const root=$('ruler');root.replaceChildren();
  const row=(name:string)=>{const el=document.createElement('div');el.className=`vm-ruler-row vm-ruler-${name}`;root.append(el);return el;};
  const box=(parent:HTMLElement,cls:string,from:number,to:number|null)=>{
    const el=document.createElement('div');el.className=cls;el.style.left=pct(from);
    if(to!==null)el.style.width=pct(Math.max(0,to-from));
    parent.append(el);return el;
  };
  if(surface.kind==='movie'){
    const bands=row('bands');
    for(const b of ruler.bands){const el=box(bands,'vm-band',b.from,b.to);el.dataset.chapter=b.id;el.textContent=b.id;}
    const shots=row('shots');
    for(const s of ruler.segments){
      const el=box(shots,'vm-shot',s.from,s.to);el.dataset.shot=s.id;
      const name=document.createElement('span');name.className='vm-shot-name';name.textContent=s.id;name.dataset.seek=String(s.start);
      el.append(name);
    }
    for(const j of ruler.joins){const el=box(shots,'vm-join',j.from,j.to);el.dataset.join=j.shot;el.title=`${j.kind} into ${j.shot}`;}
    for(const t of ruler.ticks){const el=box(shots,'vm-tick',t.x,null);el.dataset.cue=`${t.shot} ${t.id}`;el.style.bottom='0';}
  }
  // The take surface's ground, which the scrubber is pressed on: the take, start to end.
  if(surface.kind==='take')box(row('take'),'vm-take-span',0,1).dataset.take=surface.key;
  const marks=row('marks');
  for(const f of ruler.flags){
    const el=box(marks,'vm-flag',f.x,null);el.dataset.mark=f.name;el.dataset.seek=String(f.at);el.textContent=f.name;
    // A flag near the end is labelled on the left of its line, inside the ruler.
    if(f.x>0.85)el.classList.add('vm-flag-end');
  }
  const playhead=document.createElement('div');playhead.className='vm-playhead';
  const wanted=document.createElement('div');wanted.className='vm-wanted';wanted.hidden=true;
  root.append(playhead,wanted);
}
function placeHead(cls:string,t:number|null){
  const el=$('ruler').querySelector<HTMLElement>(`.${cls}`);if(!el||!active)return;
  if(t===null){el.hidden=true;return;}
  el.hidden=false;el.style.left=pct(Math.min(1,Math.max(0,t/active.ruler.duration)));
}
function drawReadout(){
  if(!active)return;
  const r=readoutOf({outline,surface:active.surface,time:active.posedTime,shown:active.shown,captions});
  const root=$('readout');root.replaceChildren();
  const field=(name:string,text:string|null,value?:string)=>{
    const el=document.createElement('span');el.dataset.field=name;el.textContent=text??'';
    if(value!==undefined)el.dataset.value=value;root.append(el);
  };
  field('time',r.time);field('frame',`frame ${r.frame} of ${r.count}`,String(r.frame));
  field('shot',r.shot&&`shot ${r.shot}`,r.shot??'');field('chapter',r.chapter&&`chapter ${r.chapter}`,r.chapter??'');
  field('mark',r.mark&&`mark ${r.mark}`,r.mark??'');field('join',r.join);
  const caption=$('caption');caption.hidden=!r.caption;caption.textContent=r.caption??'';
  placeHead('vm-playhead',active.posedTime);
}

// ----- a surface -----

interface Instance {
  readonly surface:Surface;
  ruler:Ruler;
  clock:Clock;
  posedTime:number;
  posedIndex:number;
  shown:Shown|null;
  readonly posed:number[];
  observed:unknown;
  take:TakeTransport|null;
  poser:Poser;
  ready:Promise<void>;
  /** The time a clock's frame or a seek asks to pose, snapped or a stop. */
  timeFor(t:number):number;
  /** What a generation event asks of this surface. */
  reload(action:ReturnType<typeof reloadAction>):Promise<void>;
  destroy():void;
}

// The clock of a surface, made again at each generation, keeping its time
// and whether it played.
function clockFor(instance:Instance|null,surface:Surface,previous:Clock|null):Clock{
  const duration=durationOf(outline,surface),time=previous?.time()??0,playing=previous?.playing()??false;
  previous?.pause();
  // The previous generation's mix, if any, stops loading and says nothing more.
  const stale=document.getElementById('narration') as HTMLAudioElement|null;
  if(stale){stale.remove();stale.removeAttribute('src');stale.load();}
  note=null;
  let clock:Clock;
  if(surface.kind==='movie'&&outline.speech.mix){
    const audio=document.createElement('audio');audio.id='narration';audio.preload='auto';
    audio.src=`/narration.wav?generation=${outline.generation.number}`;
    audio.addEventListener('loadedmetadata',()=>{
      if(!audio.isConnected)return;
      const gap=Math.abs(audio.duration-duration);
      note=gap>1/outline.output.fps?`The mix is ${audio.duration.toFixed(2)} s and the film ${duration.toFixed(2)} s: run speech again`:null;
      showMessages();
    });
    document.body.append(audio);
    clock=audioClock(audio,duration);
  }else clock=timerClock(duration);
  clock.onFrame(t=>{if(instance)instance.poser.request(instance.timeFor(t));});
  clock.seek(Math.min(time,duration));
  if(playing)clock.play();
  return clock;
}

function base(surface:Surface,pose:(t:number)=>Promise<void>):Instance{
  const instance:Instance={surface,ruler:rulerOf(outline,surface),clock:null as unknown as Clock,posedTime:0,posedIndex:0,shown:null,
    posed:[],observed:null,take:null,ready:Promise.resolve(),
    poser:poser(async t=>{placeHead('vm-wanted',t);await instance.ready;await pose(t);placeHead('vm-wanted',null);},
      error=>{fault=message(error);showMessages();}),
    timeFor:t=>snap(t,gridOf(outline,surface)).time,
    reload:async()=>{},destroy:()=>{}};
  return instance;
}
function posedAt(instance:Instance,t:number){
  instance.posedTime=t;instance.posedIndex=snap(t,gridOf(outline,instance.surface)).index;instance.posed.push(instance.posedIndex);
  drawReadout();
}

// The movie surface: the render's stage page at the session's geometry.
function movieSurface():Instance{
  const region=$('surface'),boxEl=document.createElement('div'),iframe=document.createElement('iframe');
  boxEl.className='vm-stage-box';iframe.title='The film\'s stage';iframe.tabIndex=-1;iframe.setAttribute('scrolling','no');
  boxEl.append(iframe);region.append(boxEl);
  let film:StageFilm|null=null,stage:StageWindow|null=null,loads=0;
  const fit=()=>{
    const {width,height}=outline.output,scale=Math.min(1,region.clientWidth/width,region.clientHeight/height);
    iframe.width=String(width);iframe.height=String(height);
    Object.assign(iframe.style,{width:`${width}px`,height:`${height}px`,transform:`scale(${scale})`});
    Object.assign(boxEl.style,{width:`${width*scale}px`,height:`${height*scale}px`,
      left:`${Math.max(0,(region.clientWidth-width*scale)/2)}px`,top:`${Math.max(0,(region.clientHeight-height*scale)/2)}px`});
  };
  const resize=new ResizeObserver(fit);resize.observe(region);
  // The stage page, loaded, and window.film or window.filmError there, as the
  // renderer waits for them.
  function load(){
    film=null;stage=null;
    return new Promise<void>((resolve,reject)=>{
      iframe.onload=async()=>{
        const win=iframe.contentWindow as StageWindow|null;
        // The blank document an iframe starts with is not the stage page.
        if(win?.location.pathname!=='/film.html')return;
        loads++;iframe.dataset.loads=String(loads);
        for(let tries=0;tries<3600;tries++){
          if(win?.film||win?.filmError!==undefined)break;
          await nextFrame();
        }
        if(win?.filmError!==undefined){reject(new Error(`The stage page refused: ${win.filmError}`));return;}
        if(!win?.film){reject(new Error('The stage page did not start'));return;}
        film=win.film;stage=win;resolve();
      };
      iframe.src=`/film.html?generation=${outline.generation.number}`;
    });
  }
  const instance=base({kind:'movie'},async t=>{
    if(!film)throw new Error('The stage page is not ready');
    const frame=await getJson<Frame>(`/frame?t=${t}`);
    const {request,shown}=stageRequest(frame);
    // Posed as the renderer poses it: a copy made in the stage page's own
    // realm, as page.evaluate gives the stage its frame.
    instance.observed=await film.setFrame(stage?(stage as unknown as {JSON:JSON}).JSON.parse(JSON.stringify(request)):request);
    instance.shown=shown;posedAt(instance,t);
  });
  fit();
  const started=()=>{instance.ready=load();instance.ready.catch(error=>{fault=message(error);showMessages();});};
  started();
  instance.reload=async action=>{
    fit();
    instance.ruler=rulerOf(outline,instance.surface);drawRuler(instance.ruler,instance.surface);
    if(action==='reload-stage')started();
    instance.clock=clockFor(instance,instance.surface,instance.clock);
    instance.poser.request(instance.timeFor(instance.clock.time()),{force:true});
  };
  instance.destroy=()=>{resize.disconnect();iframe.onload=null;boxEl.remove();document.getElementById('narration')?.remove();};
  return instance;
}

// The viewer's script, loaded once per export.
let viewerScript:{generation:number;loaded:Promise<ViewerFactory>}|null=null;
function viewerFactory(fresh:boolean):Promise<ViewerFactory>{
  if(viewerScript&&!fresh)return viewerScript.loaded;
  document.getElementById('viewer-script')?.remove();
  const script=document.createElement('script');script.id='viewer-script';
  script.src=`/viewer.js?generation=${outline.generation.number}`;
  const loaded=new Promise<ViewerFactory>((resolve,reject)=>{
    script.onload=()=>window.MachinomeViewer?resolve(window.MachinomeViewer):reject(new Error('The viewer script did not define MachinomeViewer'));
    script.onerror=()=>reject(new Error('The viewer script did not load from /viewer.js'));
  });
  viewerScript={generation:outline.generation.number,loaded};
  document.head.append(script);
  return loaded;
}

// The take surface: the viewer alone on the export, the take transport.
function takeSurface(key:string):Instance{
  const surface:Surface={kind:'take',key},region=$('surface');
  let host:HTMLDivElement|null=null,viewer:ViewerInstance|null=null,mounts=0;
  const entry=()=>outline.takes[key];
  const instance=base(surface,async t=>{
    const take=instance.take;
    if(!take)throw new Error(`Take ${key}: the transport is not attached`);
    take.seek(take.kind==='loop'?t/entry().duration:t);
    posedAt(instance,t);
  });
  // A mark is a stop: its own time is posed, not the nearest frame.
  instance.timeFor=t=>{
    const stop=marksOf(outline,surface).find(m=>Math.abs(m.at-t)<=1e-9);
    return stop?stop.at:snap(t,gridOf(outline,surface)).time;
  };
  async function attach(){
    if(!viewer)throw new Error(`Take ${key}: no viewer is mounted`);
    try{
      instance.take=entry().kind==='clocked'?attachTake(viewer,await getJson<TakeDocument>(entry().url??'/take.json')):attachLoop(viewer);
    }catch(error){instance.take=null;throw new Error(`Take ${key}: ${message(error)}`);}
  }
  async function mount(fresh:boolean){
    host?.remove();viewer=null;instance.take=null;
    // The viewer styles the element it mounts in; it fills a box that fills the region.
    host=document.createElement('div');host.className='vm-take-viewer';
    const target=document.createElement('div');target.className='vm-take-target';target.id=`vm-take-viewer-${++mounts}`;
    host.append(target);region.append(host);
    const factory=await viewerFactory(fresh);
    viewer=await factory.mount(`#${target.id}`,'/model/manifest.json',
      {renderMode:'continuous',animation:'external',autoplay:false,driverControls:'none',partControls:'none'});
    host.dataset.mount=String(mounts);
    await attach();
  }
  const started=(fresh:boolean)=>{instance.ready=mount(fresh);instance.ready.catch(error=>{fault=message(error);showMessages();});};
  started(false);
  instance.reload=async action=>{
    instance.ruler=rulerOf(outline,surface);drawRuler(instance.ruler,surface);
    if(action==='remount')started(true);
    else instance.ready=instance.ready.then(attach).catch(error=>{fault=message(error);showMessages();});
    instance.clock=clockFor(instance,surface,instance.clock);
    instance.poser.request(instance.timeFor(instance.clock.time()),{force:true});
  };
  instance.destroy=()=>{host?.remove();viewer=null;};
  return instance;
}

// ----- switching surfaces -----

function show(surface:Surface){
  const previous=active;
  previous?.clock.pause();previous?.destroy();
  fault=null;note=null;
  const instance=surface.kind==='movie'?movieSurface():takeSurface(surface.key);
  active=instance;
  instance.clock=clockFor(instance,surface,null);
  drawRuler(instance.ruler,surface);drawReadout();showSurfaces();showMessages();
}
function route(){
  const {surface,hash,known}=routeOf(location.hash,outline);
  if(!known)history.replaceState(null,'',hash);
  if(active&&JSON.stringify(active.surface)===JSON.stringify(surface))return;
  show(surface);
}

// ----- seeking: the keys, the clicks and the scrubber -----

function seek(t:number){
  if(!active)return;
  const at=active.timeFor(Math.min(Math.max(t,0),active.ruler.duration));
  placeHead('vm-wanted',at);
  active.clock.seek(at);
}
function step(frames:number){
  if(!active)return;
  const grid=gridOf(outline,active.surface),{index,count}=snap(active.clock.time(),grid);
  const last=count-1,next=Math.min(last,Math.max(0,index+frames));
  seek(grid.end==='inclusive'&&next===last?grid.duration:next/grid.fps);
}
function lastFrame(){
  if(!active)return;
  const grid=gridOf(outline,active.surface),{count}=snap(0,grid);
  seek(grid.end==='inclusive'?grid.duration:(count-1)/grid.fps);
}
function toggle(){
  if(!active)return;
  if(active.clock.playing())active.clock.pause();else active.clock.play();
}
document.addEventListener('keydown',event=>{
  if(event.ctrlKey||event.metaKey||event.altKey||!active)return;
  const target=event.target as HTMLElement|null;
  if(target&&/^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName))return;
  const fps=outline.output.fps;
  switch(event.key){
    case ' ':toggle();break;
    case 'ArrowRight':step(event.shiftKey?fps:2*fps);break;
    case 'ArrowLeft':step(event.shiftKey?-fps:-2*fps);break;
    case 'Home':seek(0);break;
    case 'End':lastFrame();break;
    default:return;
  }
  event.preventDefault();
});
{
  const ruler=$('ruler');
  let scrubbing:number|null=null;
  const under=(event:PointerEvent)=>{
    const box=ruler.getBoundingClientRect();
    return active?timeAt((event.clientX-box.left)/box.width,active.ruler):0;
  };
  ruler.addEventListener('pointerdown',event=>{
    if(!active||event.button!==0)return;
    const control=(event.target as HTMLElement).closest<HTMLElement>('[data-seek]');
    if(control)return;
    event.preventDefault();
    active.clock.pause();
    scrubbing=event.pointerId;ruler.setPointerCapture(event.pointerId);
    seek(under(event));
  });
  ruler.addEventListener('pointermove',event=>{if(scrubbing===event.pointerId)seek(under(event));});
  const end=(event:PointerEvent)=>{
    if(scrubbing!==event.pointerId)return;
    scrubbing=null;
    if(ruler.hasPointerCapture(event.pointerId))ruler.releasePointerCapture(event.pointerId);
  };
  ruler.addEventListener('pointerup',end);ruler.addEventListener('pointercancel',end);ruler.addEventListener('lostpointercapture',end);
  ruler.addEventListener('click',event=>{
    const control=(event.target as HTMLElement).closest<HTMLElement>('[data-seek]');
    if(control)seek(Number(control.dataset.seek));
  });
}

// ----- the session's generations -----

async function fetchCaptions(){
  captions=outline.speech.captions?await getJson<Caption[]>(`/captions.json?generation=${outline.generation.number}`).catch(()=>null):null;
}
let handling:Promise<void>=Promise.resolve();
function onGeneration(event:GenerationEvent){
  handling=handling.then(async()=>{
    const action=active?reloadAction(active.surface.kind,held,event):'none';
    if(action==='none'&&held.number)return;
    outline=await getJson<Outline>('/film.json');
    held={number:outline.generation.number,stageSha256:outline.stage.sha256};
    loadRefusal=outline.refusal?.message??null;reloading=false;
    await fetchCaptions();
    showSurfaces();
    const {surface}=routeOf(location.hash,outline);
    if(!active||JSON.stringify(surface)!==JSON.stringify(active.surface)){route();return;}
    fault=null;
    await active.reload(action);
    showMessages();drawReadout();
  }).catch(error=>{fault=message(error);showMessages();});
}

async function boot(){
  outline=await getJson<Outline>('/film.json');
  held={number:outline.generation.number,stageSha256:outline.stage.sha256};
  loadRefusal=outline.refusal?.message??null;
  await fetchCaptions();
  route();
  window.addEventListener('hashchange',()=>{route();showSurfaces();});
  const events=new EventSource('/events');
  events.addEventListener('loading',()=>{reloading=true;showMessages();});
  events.addEventListener('generation',event=>onGeneration(JSON.parse((event as MessageEvent).data) as GenerationEvent));
  events.addEventListener('refused',event=>{
    const data=JSON.parse((event as MessageEvent).data) as {message:string};
    loadRefusal=data.message;reloading=false;showMessages();
  });
}

window.player={
  surface:()=>active?(active.surface.kind==='movie'?'movie':`take/${active.surface.key}`):'',
  time:()=>active?.posedTime??0,
  frame:()=>active?.posedIndex??0,
  playing:()=>active?.clock.playing()??false,
  generation:()=>held.number,
  poses:()=>[...(active?.posed??[])],
  observed:()=>active?.observed??null,
  take:()=>active?.take??null,
  seek,
  play:()=>active?.clock.play(),
  pause:()=>active?.clock.pause(),
  idle:async()=>{
    for(;;){
      await handling;
      const instance=active;if(!instance)return;
      await instance.ready.catch(()=>{});
      await nextFrame();await nextFrame();
      await instance.poser.idle();
      if(instance===active&&!instance.poser.busy())return;
    }
  },
};
boot().catch(error=>{fault=`The player did not start: ${message(error)}`;showMessages();});
