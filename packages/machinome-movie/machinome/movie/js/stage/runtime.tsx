// The stage runtime: boots the page the renderer serves, mounts the set each
// frame names, poses each placed view element on a viewer instance leased to
// it for the frame (ADR-007), draws marks, and returns what it measured
// (docs/movie-document.md, "The stage"). A view on a clocked take is posed
// through the take transport (transport/, ADR-020), attached once per mounted
// instance. Imported first by the bundle's entry, so the shipped kinds are
// registered before a project's modules register theirs; the entry calls
// boot() last.
//
// Raster discipline (the earlier film page's, kept): a pose repaints the whole
// page when what it draws outside the views' canvases changed since the last
// repaint, and every composition repaints; live views are hidden while a
// transition or a blend is composed from same-instant captures; nothing
// depends on the order frames are posed in, because every frame re-specifies
// each instance's whole state and the page's pixels are always a whole-page
// raster of its present content (ADR-004, amendment of 30 September 2026).
import {flushSync} from 'react-dom';
import {createRoot,type Root} from 'react-dom/client';
import './stage.css';
import {Stage,reframeOf,type ReportSource,type StageContextValue} from './components';
import {drawMarks,plain,type MarkReport} from './marks';
import {checkRegistry} from './registry';
import {registerShipped} from './shipped';
import type {MovieInfo,MovieStyle,PictureState,Rect,SourceState,StageConfig,StageFrame,Vec3,ViewState} from './types';
import {attachMachine,type MachineTransport} from '../transport/take';
import type {MachineHandle,ViewerFactory,ViewerInstance} from '../transport/viewer-handle';

export interface Film {
  readonly apiVersion:number|null;
  readonly viewer:ViewerInstance|null;
  project(key:string,points:Vec3[]):({x:number;y:number}|null)[];
  /** The machine handle of the viewer instance the view element `key` holds, or null. */
  machine(key:string):MachineHandle|null;
  /** The take transport's machine transport the view element `key` is posed through, or null for a view on a loop. */
  transport(key:string):MachineTransport|null;
  views():{key:string|null;instance:number;visible:boolean}[];
  setFrame(frame:StageFrame):Promise<Observed>;
  compose(request:ComposeRequest):Promise<{chrome:Rect[]}>;
  composeMarkBlend(request:MarkBlendRequest):Promise<{chrome:Rect[]}>;
}
// The picture-only captures a fading frame is blended from, each with its
// weight, and whether the blended frame itself is a picture-only capture.
export interface MarkBlendRequest {
  pictures:{src:string;weight:number}[];
  pictureOnly?:boolean;
}
export interface ComposeRequest {
  images:{src:string;x:number;columns?:[number,number];opacity?:number}[];
  plate?:{color:string;opacity:number};
  pictureOnly?:boolean;
}
export interface Observed {
  frame:{width:number;height:number};
  chrome:Rect[];
  slots:Record<string,Rect>;
  elements:Record<string,Record<string,unknown>>;
}
declare global {
  interface Window {film?:Film;filmError?:string;MachinomeViewer?:ViewerFactory}
}

export const DEFAULT_STYLE:MovieStyle=Object.freeze({
  background:'#faf7ef',foreground:'#222222',accent:'#237c86',
  fontFamily:"'DejaVu Sans', sans-serif",safeInsetFraction:0.08,
});

registerShipped();
// A project module that throws while the bundle loads (a kind registered
// twice) stops the entry before boot(); the page still refuses by name.
if(typeof window!=='undefined')window.addEventListener('error',event=>{
  if(window.filmError===undefined)window.filmError=String(event.error??event.message);
});

// A mounted viewer instance as the lease sees it: the view element it serves,
// or null when it is free, and the lens it keeps (its up and field of view)
// when its viewer cannot be given another (below API 28), else null.
export interface Tenancy {key:string|null;lens:string|null}
// A mounted instance. What it holds (the layers it hides, the highlight
// standing on it and its restore, its last box size, the machine transport a
// view on a take is posed through) belongs to the instance and travels with
// it from one view element to the next.
interface PooledView extends Tenancy {
  instance:number;host:HTMLDivElement;marks:HTMLDivElement;viewer:ViewerInstance;
  hidden:string[][];applied:string|null;restore:(()=>void)|null;size:{width:number;height:number}|null;
  transport:MachineTransport|null;
}

/**
 * The lease (ADR-007): for each view element a frame places (in the frame's
 * order, each once, with its lens), the index of the instance it is drawn on,
 * or -1 when an instance must mount for it. A view whose key an instance
 * serves keeps it; every other instance is free for this frame, and a view
 * without one takes the lowest-numbered free instance that can take its lens.
 * So the instances never outnumber the most views one frame has placed (per
 * lens, for a viewer that keeps its lens).
 */
export function leaseViews(instances:readonly Tenancy[],placed:readonly {key:string;lens:string}[]):number[]{
  const taken=new Set<number>();
  const kept=placed.map(({key})=>{const i=instances.findIndex(t=>t.key===key);if(i>=0)taken.add(i);return i;});
  return placed.map(({lens},n)=>{
    if(kept[n]>=0)return kept[n];
    const i=instances.findIndex((t,j)=>!taken.has(j)&&(t.lens===null||t.lens===lens));
    if(i>=0)taken.add(i);
    return i;
  });
}
const lensOf=(state:ViewState)=>JSON.stringify([state.up??null,state.fov??null]);

/**
 * The inline box of a view's host during a reframe (ADR-010): the frame's box
 * for the view, `[x, y, width, height]` in fractions of the page, in pixels
 * of the page rounded to the layout's unit of 1/64 pixel, relative to the
 * view's element (the host's containing block), whose rectangle is
 * `element`. Without a box, the empty strings that clear it, so the
 * stylesheet's `inset: 0` fills the element again.
 */
export function reframeHost(element:Rect,page:{width:number;height:number},box:readonly number[]|null|undefined)
  :{left:string;top:string;width:string;height:string;right:string;bottom:string}{
  if(!box)return {left:'',top:'',width:'',height:'',right:'',bottom:''};
  const snap=(v:number)=>Math.round(v*64)/64;
  return {left:`${snap(box[0]*page.width)-element.x}px`,top:`${snap(box[1]*page.height)-element.y}px`,
    width:`${snap(box[2]*page.width)}px`,height:`${snap(box[3]*page.height)}px`,right:'auto',bottom:'auto'};
}

/**
 * Poses one view. A view on a clocked take is posed through the machine
 * transport its instance was attached when it mounted (ADR-012, ADR-020):
 * its whole bank restored with the take's identity, then the camera. A view
 * on a loop sets its time, then the camera. The camera call validates,
 * updates and renders synchronously (under on-demand rendering it is also
 * what draws a restored bank); from API 28 it sets up and field of view on
 * every frame, below it camera and target alone.
 */
export function poseView(viewer:ViewerInstance,state:ViewState,transport:MachineTransport|null):void{
  const camera={camera:state.view.camera,target:state.view.target,up:state.up,fov:state.fov};
  if(state.bank){
    if(!transport)throw new Error('a view on a take is posed through the take\'s machine transport, and its viewer has none');
    transport.pose(state.bank,camera);
    return;
  }
  viewer.setTime(state.time as number);
  if(viewer.apiVersion>=28)viewer.setView(camera);
  else viewer.setView({camera:camera.camera,target:camera.target});
}

const frames=()=>new Promise<void>(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>resolve())));
const message=(error:unknown)=>error instanceof Error?error.message:String(error);
const rectOf=(el:Element):Rect=>plain(el.getBoundingClientRect());
const escape=(s:string)=>typeof CSS!=='undefined'&&CSS.escape?CSS.escape(s):s.replace(/["\\]/g,'\\$&');

export async function boot():Promise<void>{
  try{
    if(window.filmError!==undefined)return;
    const config=await (await fetch('/config.json')).json() as StageConfig;
    const style:MovieStyle={...DEFAULT_STYLE,...(config.movie.style??{})};
    const movie:MovieInfo={id:config.movie.id,title:config.movie.title,series:config.movie.series,style};
    const body=document.body,html=document.documentElement;
    body.style.background=style.background;body.style.color=style.foreground;body.style.fontFamily=style.fontFamily;
    for(const [name,value] of [['--vm-background',style.background],['--vm-foreground',style.foreground],
      ['--vm-accent',style.accent],['--vm-font',style.fontFamily],['--vm-safe-inset',String(style.safeInsetFraction)]])
      html.style.setProperty(name,value);
    checkRegistry(config);
    const factory=window.MachinomeViewer;
    if(!factory||typeof factory.mount!=='function')throw new Error('The viewer script did not define MachinomeViewer');
    await Promise.all(Object.keys(config.media?.stills??{}).map(async name=>{
      const image=new Image();image.src=`/pictures/stills/${encodeURIComponent(name)}`;
      try{await image.decode();}catch(error){throw new Error(`Still ${name} does not decode: ${message(error)}`);}
    }));
    await document.fonts.ready;
    window.film=createFilm(config,movie,factory);
  }catch(error){
    window.filmError=String(error);
  }
}

function createFilm(config:StageConfig,movie:MovieInfo,factory:ViewerFactory):Film{
  const need=(id:string)=>{const el=document.getElementById(id);if(!el)throw new Error(`The page has no #${id} layer`);return el;};
  const stageRoot=need('stage-root'),transition=need('transition'),chromeLayer=need('chrome');
  const caught:unknown[]=[];
  const root:Root=createRoot(stageRoot,{
    onUncaughtError:error=>{caught.push(error);},
    onRecoverableError:error=>{caught.push(error);},
  });
  // The mounted instances, in the order they mounted.
  const instances:PooledView[]=[];
  let first:PooledView|null=null,counter=0;
  const accent=movie.style.accent;
  const refusal=(declared:number)=>{
    const required=config.viewer?.required?.api;
    return (config.viewer?.refusal??`The movie needs viewer API ${required}; the viewer declares {declared}`)
      .replace('{declared}',String(declared));
  };

  // ----- composition -----
  function clearComposition(){
    transition.replaceChildren();
    document.body.classList.remove('in-transition','in-mark-blend');
    for(const view of instances)if(view.host.isConnected)view.host.style.visibility='';
  }
  const hideViews=()=>{for(const view of instances)view.host.style.visibility='hidden';};
  // A whole-page repaint: Chromium rasters only what a change invalidates and
  // otherwise keeps antialiased glyph edges just outside a changed area.
  // After it, the pixels are a fresh raster of the page's content, which is
  // recorded: a later pose whose content is the same (only a view's canvas,
  // its own rectangle, changed) has nothing an earlier pose could have left.
  // The content is every element, attribute and word of the document; a
  // canvas's pixels are not part of it.
  const content=()=>document.documentElement.outerHTML;
  let painted:string|null=null;
  async function repaint(){
    const background=document.body.style.background;
    document.body.style.background='#010203';await frames();
    document.body.style.background=background;await frames();
    painted=content();
  }
  const chrome=():Rect[]=>[...chromeLayer.querySelectorAll(':scope > .vm-chrome')]
    .flatMap(wrapper=>[...wrapper.children].map(rectOf));

  // The transition layer: above the set's content, below its chrome. A
  // transition frame is drawn in it entirely from captures of this page at the
  // same instant, each an image at its own pixel size and a whole-pixel
  // offset, optionally translucent and cut to the columns [from, to), with a
  // colour plate over them. The live views are hidden meanwhile: a visible
  // WebGL canvas beneath the layer would make Chromium composite the chrome
  // separately and draw its text without subpixel antialiasing.
  async function compose(request:ComposeRequest){
    clearComposition();
    document.body.classList.add('in-transition');
    document.body.classList.toggle('picture-only',Boolean(request.pictureOnly));
    hideViews();
    for(const image of request.images){
      const img=new Image();img.src=image.src;await img.decode();
      const [from,to]=image.columns??[0,window.innerWidth];
      const box=document.createElement('div');
      Object.assign(box.style,{left:`${from}px`,width:`${to-from}px`,height:'100%',overflow:'hidden'});
      Object.assign(img.style,{position:'absolute',left:`${image.x-from}px`,top:'0'});
      if(image.opacity!==undefined)box.style.opacity=String(image.opacity);
      box.append(img);transition.append(box);
    }
    if(request.plate){
      const plate=document.createElement('div');
      Object.assign(plate.style,{left:'0',width:'100%',height:'100%',background:request.plate.color,opacity:String(request.plate.opacity)});
      transition.append(plate);
    }
    await repaint();
    return {chrome:chrome()};
  }
  // Same-instant raster blend for faded marks and pictures. Chromium switches
  // HTML glyphs from subpixel to grayscale antialiasing under CSS opacity;
  // blending captures of the plain drawing keeps its pixels and the authored
  // opacity.
  async function composeMarkBlend(request:MarkBlendRequest){
    const {pictures}=request;
    clearComposition();document.body.classList.add('in-mark-blend');
    // The captures were posed picture-only; the blended frame is picture-only
    // only when the request says so, as a transition's is, so the live chrome
    // is drawn over a fading picture or mark as over any other frame.
    document.body.classList.toggle('picture-only',Boolean(request.pictureOnly));
    hideViews();
    const W=window.innerWidth,H=window.innerHeight,canvas=document.createElement('canvas');
    canvas.width=W;canvas.height=H;canvas.style.width=`${W}px`;canvas.style.height=`${H}px`;
    const ctx=canvas.getContext('2d',{willReadFrequently:true});
    if(!ctx)throw new Error('The blend canvas has no 2D context');
    const sum=new Float64Array(W*H*4);
    for(const {src,weight} of pictures){
      const img=new Image();img.src=src;await img.decode();ctx.clearRect(0,0,W,H);ctx.drawImage(img,0,0);
      const rgba=ctx.getImageData(0,0,W,H).data;
      for(let i=0;i<rgba.length;i++)sum[i]+=rgba[i]*weight;
    }
    const output=ctx.createImageData(W,H);
    for(let i=0;i<sum.length;i++)output.data[i]=Math.round(sum[i]);
    ctx.putImageData(output,0,0);transition.append(canvas);
    await repaint();
    return {chrome:chrome()};
  }

  // ----- views -----
  const boxOf=(key:string)=>stageRoot.querySelector<HTMLElement>(`.vm-element[data-element="${escape(key)}"]`);

  async function mountView(key:string,state:ViewState,box:HTMLElement,shotId:string):Promise<PooledView>{
    const instance=++counter,host=document.createElement('div'),target=document.createElement('div'),marks=document.createElement('div');
    host.className='vm-view-host';target.className='vm-viewer';target.id=`vm-viewer-${instance}`;marks.className='vm-marks';
    host.append(target,marks);box.append(host);
    let viewer:ViewerInstance;
    try{
      // A view on a take has no loop time: its bank is restored on every pose.
      viewer=await factory.mount(`#${target.id}`,'/model/manifest.json',{
        renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none',
        ...(state.bank?{}:{time:state.time}),view:state.view,up:state.up,fov:state.fov,
      });
    }catch(error){host.remove();throw new Error(`View ${key} in shot ${shotId}: the viewer did not mount: ${message(error)}`);}
    const refuse=(text:string)=>{host.remove();window.filmError=text;throw new Error(text);};
    if(!(viewer.apiVersion>=21)||typeof viewer.setView!=='function')refuse('Viewer API 21 with setView is required');
    const required=config.viewer?.required?.api;
    if(typeof required==='number'&&viewer.apiVersion<required)refuse(refusal(viewer.apiVersion));
    // A view on a take is posed through the take transport's machine
    // transport, attached once, whose machine must be the one the take was
    // recorded on (ADR-012, ADR-020).
    let transport:MachineTransport|null=null;
    if(state.bank){
      try{transport=attachMachine(viewer,config.take?.identity as string);}
      catch(error){refuse(`View ${key} in shot ${shotId}: ${message(error)}`);}
    }
    // Below API 28 setView cannot change up or field of view: the instance
    // keeps the lens it mounted with, and is leased only to that lens.
    const view:PooledView={key,lens:viewer.apiVersion>=28?null:lensOf(state),instance,host,marks,viewer,
      hidden:[],applied:null,restore:null,size:null,transport};
    instances.push(view);first??=view;
    return view;
  }

  // Highlight state follows the request, never the order frames are posed in:
  // restore a standing highlight that differs, apply visibility, then the new
  // one. Each is diffed against what the instance holds, whichever view
  // element it served before, so a leased instance ends in the frame's state.
  function pose(view:PooledView,state:ViewState,shotId:string){
    const {viewer}=view,wanted=state.highlight?JSON.stringify(state.highlight):null;
    try{
      if(wanted!==view.applied&&view.restore){const put=view.restore;view.restore=null;view.applied=null;put();}
      if(JSON.stringify(view.hidden)!==JSON.stringify(state.hidden)){
        for(const path of view.hidden)viewer.setVisible(path,true);
        for(const path of state.hidden)viewer.setVisible(path,false);
        view.hidden=state.hidden;
      }
      if(wanted!==view.applied&&state.highlight){
        const {paths,others,color}=state.highlight;
        view.restore=viewer.highlight(paths,{color,others});view.applied=wanted;
      }
      // The loop's time, or the take's bank through the transport, then the camera.
      poseView(viewer,state,view.transport);
    }catch(error){throw new Error(`View ${key(view)} in shot ${shotId}: ${message(error)}`);}
  }
  const key=(view:PooledView)=>view.key;

  // The host is the view's drawn box: its element's box, or the frame's box
  // during a reframe. A canvas is ready when it fills the box and exceeds it
  // by no more than a pixel: a canvas left larger by a shrinking box is
  // waited for as one left smaller by a growing box is (ADR-012).
  const fills=(view:PooledView)=>{
    const canvas=view.host.querySelector('canvas'),b=view.host.getBoundingClientRect();
    if(!canvas)return false;const c=canvas.getBoundingClientRect();
    return c.width>=b.width*.98&&c.height>=b.height*.98&&c.width<=b.width+1&&c.height<=b.height+1;
  };
  const contains=(outer:Rect,inner:Rect)=>outer.x<=inner.x+.5&&outer.y<=inner.y+.5&&
    outer.x+outer.width>=inner.x+inner.width-.5&&outer.y+outer.height>=inner.y+inner.height-.5;

  // Leases the frame's views their instances, poses them and draws their
  // marks; `resized` says a view was mounted, placed again (on its own
  // instance or one another view freed) or its box changed size, so the
  // canvas wait ran.
  async function poseViews(frame:StageFrame):Promise<{views:Record<string,Record<string,unknown>>;resized:boolean}>{
    const placed=[...new Set(Object.values(frame.slots))].filter(k=>frame.elements[k]?.kind==='view');
    const reframe=reframeOf(frame),page={width:window.innerWidth,height:window.innerHeight};
    const leased=leaseViews(instances,placed.map(k=>({key:k,lens:lensOf(frame.elements[k] as ViewState)})));
    // An instance no view of this frame is drawn on is free: its host leaves
    // the page, as a view that left always did.
    instances.forEach((view,i)=>{if(!leased.includes(i)){view.key=null;view.host.remove();view.host.style.visibility='hidden';}});
    const posed:[PooledView,ViewState,HTMLElement,string][]=[];
    let resized=false;
    for(const [n,k] of placed.entries()){
      const state=frame.elements[k] as ViewState,box=boxOf(k);
      if(!box)throw new Error(`View ${k} in shot ${frame.shotId} has no box: set ${frame.set} draws no slot that holds it`);
      let view:PooledView;
      if(leased[n]<0)view=await mountView(k,state,box,frame.shotId);
      else{
        view=instances[leased[n]];view.key=k;
        // A host detached while it served no view was observed at no size by
        // the viewer, which shrank its canvas; a host moved into another
        // view's box is resized: either is a resize.
        if(view.host.parentElement!==box){box.append(view.host);resized=true;}
      }
      view.host.style.visibility='';
      // A view a reframe moves is drawn over the frame's box, inside its
      // element so the set's stacking order holds; every other is drawn
      // over its element's box. A moving host changes size every frame.
      Object.assign(view.host.style,reframeHost(rectOf(box),page,reframe?.boxes[k]));
      const r=view.host.getBoundingClientRect();
      if(!view.size||view.size.width!==r.width||view.size.height!==r.height)resized=true;
      posed.push([view,state,box,k]);
    }
    // A viewer sizes its canvas from its host on its own animation frame,
    // after it mounts and after each resize, and a resize clears the canvas:
    // wait for every canvas to fill its box, a bounded number of frames, and
    // only then pose, so the viewer renders into the sized canvas before
    // anything is measured or a mark drawn. The renderer refuses a canvas that
    // still does not fill.
    if(resized)for(let tries=0;tries<30;tries++){
      await frames();
      if(posed.every(([view])=>fills(view)))break;
    }
    for(const [view,state] of posed)pose(view,state,frame.shotId);
    // A view under an opaque picture is posed but hidden, so its canvas does
    // not change how Chromium composites the text above it.
    const opaque=Object.values(frame.slots).filter(k=>{const s=frame.elements[k];
      return s?.kind==='picture'&&(s as PictureState).shown&&(s as PictureState).opacity>=1;})
      .map(k=>boxOf(k)).filter((b):b is HTMLElement=>Boolean(b)).map(rectOf);
    const reports:Record<string,Record<string,unknown>>={};
    for(const [view,state,,k] of posed){
      const r=rectOf(view.host);view.size={width:r.width,height:r.height};
      if(opaque.some(o=>contains(o,r)))view.host.style.visibility='hidden';
      const marks:MarkReport[]=drawMarks(view.marks,r,state.marks??[],view.viewer,
        {accent,uid:String(view.instance),where:`view ${k} in shot ${frame.shotId}`});
      const read=view.viewer.view(),canvas=view.host.querySelector('canvas');
      reports[k]={kind:'view',box:r,instance:view.instance,canvas:canvas?rectOf(canvas):null,
        camera:read.camera.toArray(),target:read.target.toArray(),
        ...(view.viewer.apiVersion>=28?{up:read.up?.toArray(),fov:Number(read.fov)}:{}),
        // The bank the machine holds after the pose, for a view on a take.
        ...(state.bank?{bank:view.transport?.bank()??null}:{}),
        navigation:view.viewer.navigation(),marks};
    }
    return {views:reports,resized};
  }

  // ----- measurement -----
  function measure(frame:StageFrame,reports:Map<string,ReportSource>,views:Record<string,Record<string,unknown>>):Observed{
    const slots:Record<string,Rect>={};
    for(const slot of stageRoot.querySelectorAll<HTMLElement>('.vm-slot'))slots[slot.dataset.slot as string]=rectOf(slot);
    const elements:Record<string,Record<string,unknown>>={},reframe=reframeOf(frame);
    for(const k of new Set(Object.values(frame.slots))){
      const state=frame.elements[k],box=boxOf(k);
      if(!state||!box)continue;
      const source=reports.get(k),reported=typeof source==='function'?source():source??{};
      elements[k]={...reported,kind:state.kind,box:rectOf(box),...(views[k]??measureElement(box,state)),
        // During a reframe, the opacity each element is drawn at.
        ...(reframe?{opacity:Number(getComputedStyle(box).opacity)}:{})};
    }
    return {frame:{width:window.innerWidth,height:window.innerHeight},chrome:chrome(),slots,elements};
  }

  async function decodePictures(frame:StageFrame){
    await Promise.all([...stageRoot.querySelectorAll<HTMLImageElement>('.vm-element-picture img')].map(async img=>{
      try{await img.decode();}
      catch(error){const k=img.closest<HTMLElement>('.vm-element')?.dataset.element;
        throw new Error(`Picture element ${k} in shot ${frame.shotId} does not decode ${img.getAttribute('src')}: ${message(error)}`);}
    }));
  }

  async function setFrame(frame:StageFrame):Promise<Observed>{
    // Every frame starts from an empty transition layer and visible views.
    clearComposition();
    // Picture-only captures leave out the set's chrome.
    document.body.classList.toggle('picture-only',Boolean(frame.pictureOnly));
    const reports=new Map<string,ReportSource>(),errors:Error[]=[];
    const stage:StageContextValue={frame,config,chromeLayer,reports,fail:error=>{errors.push(error);}};
    caught.length=0;
    flushSync(()=>root.render(<Stage movie={movie} stage={stage}/>));
    if(caught.length)throw new Error(`Shot ${frame.shotId} at ${frame.time} s: ${message(caught[0])}`);
    if(errors.length)throw errors[0];
    // A reframe's fade, once over, leaves React's emptied style attribute on
    // an element's box; removed, so the page's content is the frame's alone.
    for(const box of stageRoot.querySelectorAll('.vm-element[style=""]'))box.removeAttribute('style');
    for(const [slot,k] of Object.entries(frame.slots))
      if(!stageRoot.querySelector(`.vm-slot[data-slot="${escape(slot)}"]`))
        throw new Error(`Set ${frame.set} draws no slot ${slot}, where shot ${frame.shotId} places ${k}`);
    const {views,resized}=await poseViews(frame);
    await decodePictures(frame);
    // A pose waits for what can change the picture and for nothing else: a
    // proof pose of preview, a view mounted, placed again or resized, or a
    // page whose content differs from the last repaint's. A pose after a
    // composition always differs: it emptied the transition layer.
    if(frame.fresh||resized||content()!==painted)await repaint();
    return measure(frame,reports,views);
  }

  // The instance the view element `k` holds: the last frame placed it.
  const viewNamed=(k:string)=>{const view=instances.find(v=>v.key===k);if(!view)throw new Error(`No viewer instance for view ${k}`);return view;};
  return {
    get apiVersion(){return first?.viewer.apiVersion??null;},
    get viewer(){return first?.viewer??null;},
    project:(k,points)=>{const {viewer}=viewNamed(k);return points.map(p=>viewer.project(p));},
    machine:k=>{const {viewer}=viewNamed(k);return typeof viewer.machine==='function'?viewer.machine():null;},
    transport:k=>viewNamed(k).transport,
    views:()=>instances.map(v=>({key:v.key,instance:v.instance,visible:v.host.isConnected&&v.host.style.visibility!=='hidden'})),
    setFrame,compose,composeMarkBlend,
  };
}

/**
 * The lines the text of `nodes`, the children of `element`, occupies: from
 * the client rectangles of its inline boxes, the distance from the first
 * box's centre to the last's in line heights, plus one, so an empty line of
 * a `pre-line` title counts; with a line height of `normal`, the distinct
 * centres. Null where the page has no layout (ADR-017).
 */
export function linesOf(element:Element,nodes:readonly Node[]):number|null{
  if(!nodes.length)return 0;
  const range=document.createRange();
  if(typeof range.getClientRects!=='function')return null;
  range.setStartBefore(nodes[0]);range.setEndAfter(nodes[nodes.length-1]);
  const centres=[...range.getClientRects()].filter(r=>r.height>0).map(r=>r.top+r.height/2).sort((a,b)=>a-b);
  if(!centres.length)return null;
  const height=parseFloat(getComputedStyle(element).lineHeight);
  if(Number.isFinite(height)&&height>0)return Math.round((centres[centres.length-1]-centres[0])/height)+1;
  let lines=1;
  for(let i=1;i<centres.length;i++)if(centres[i]-centres[i-1]>1)lines++;
  return lines;
}

/** What the stage reports for a shipped element other than a view (the view is the runtime's). */
export function measureElement(box:HTMLElement,state:{kind:string}):Record<string,unknown>{
  switch(state.kind){
    case 'source':{
      const s=state as SourceState,panel=box.querySelector<HTMLElement>('.vm-source'),code=box.querySelector('code'),
        cursor=box.querySelector('.vm-source-cursor'),pre=box.querySelector('.vm-source pre');
      // The size the code is drawn at, in CSS pixels (ADR-017).
      const size=pre?parseFloat(getComputedStyle(pre).fontSize):NaN;
      return {kind:'source',text:code?.textContent??'',
        fits:panel?panel.scrollHeight<=panel.clientHeight&&panel.scrollWidth<=panel.clientWidth:false,
        emphasis:[...box.querySelectorAll<HTMLElement>('mark.spoken')].map(m=>({token:m.dataset.token,text:m.textContent})),
        cursor:cursor?getComputedStyle(cursor).visibility!=='hidden':s.cursor,
        fontSize:Number.isFinite(size)&&size>0?size:null};
    }
    case 'title':{
      const text=box.querySelector('.vm-title'),words=text?[...text.querySelectorAll('.vm-reveal-word')]:[];
      // The lines its text and its subtitle wrap to (ADR-017).
      const subtitle=text?.querySelector('.vm-title-subtitle')??null;
      const own=text?[...text.childNodes].filter(n=>n!==subtitle):[];
      return {kind:'title',text:text?rectOf(text):null,
        revealed:words.length?words.filter(w=>getComputedStyle(w).visibility!=='hidden').length:null,
        ...(text?{lines:linesOf(text,own)}:{}),
        ...(subtitle?{subtitleLines:linesOf(subtitle,[...subtitle.childNodes])}:{})};
    }
    case 'picture':{
      const s=state as PictureState,img=box.querySelector<HTMLImageElement>('img.vm-picture-img');
      const frame=img&&s.media==='clip'?Number(/\/(\d{6})\.png$/.exec(new URL(img.src,location.href).pathname)?.[1]):undefined;
      return {kind:'picture',shown:Boolean(img),drawn:img?rectOf(img):null,
        natural:img?{width:img.naturalWidth,height:img.naturalHeight}:null,...(frame!==undefined?{frame}:{})};
    }
    default:return {};
  }
}
