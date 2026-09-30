// The sets and elements the tool ships. `frame` and `split` draw no chrome;
// `paper`, `paper-split` and `source-only` reproduce the earlier film page's
// layouts for YAML episodes, with a masthead whose words come only from the
// set's props. The elements draw exactly their state (docs/movie-document.md,
// "The frame"); the view element is a box, whose viewer the runtime owns.
import {useLayoutEffect,useRef,type CSSProperties,type ReactNode} from 'react';
import {Chrome,Slot,useElementKey,useStage} from './components';
import {registerElement,registerSet} from './registry';
import type {ElementComponentProps,PictureState,SetComponentProps,SourceState,TitleState} from './types';

// ----- sets -----

const indexed=(base:string):string[]=>[base,...[2,3,4,5,6,7,8].map(n=>`${base}-${n}`)];
const TEXT=['title','top','lower-third','center'];

export const SHIPPED_SLOTS:Readonly<Record<string,readonly string[]>>=Object.freeze({
  frame:['stage'],
  split:['left','right'],
  paper:['stage',...indexed('plate'),...indexed('full'),...TEXT.flatMap(indexed)],
  'paper-split':['left','right',...indexed('plate'),...indexed('full'),...TEXT.flatMap(indexed)],
  'source-only':['source',...TEXT.flatMap(indexed)],
});

function FrameSet(){
  return <Slot name="stage" className="vm-frame-stage"/>;
}
function SplitSet({movie}:SetComponentProps){
  const style={'--vm-safe-inset':String(movie.style.safeInsetFraction)} as CSSProperties;
  return (
    <div className="vm-split" style={style}>
      <Slot name="left" className="vm-split-left"/>
      <Slot name="right" className="vm-split-right"/>
    </div>
  );
}

function PaperMasthead({props}:{props:Record<string,unknown>}){
  const brand=typeof props.brand==='string'?props.brand:null,series=typeof props.series==='string'?props.series:null;
  if(brand===null&&series===null)return null;
  return (
    <Chrome className="vm-paper-masthead">
      {brand!==null&&<div className="vm-paper-brand">{brand}</div>}
      {series!==null&&<div className="vm-paper-series">{series}</div>}
    </Chrome>
  );
}
const slots=(base:string,className:string):ReactNode[]=>indexed(base).map(name=><Slot key={name} name={name} className={className}/>);
const textSlots=():ReactNode[]=>TEXT.flatMap(base=>slots(base,`vm-paper-text vm-paper-${base}`));

function PaperSet({props}:SetComponentProps){
  return (
    <>
      <Slot name="stage" className="vm-paper-model"/>
      {slots('plate','vm-paper-picture vm-paper-plate')}
      {slots('full','vm-paper-picture vm-paper-full')}
      {textSlots()}
      <PaperMasthead props={props}/>
    </>
  );
}
function PaperSplitSet({props}:SetComponentProps){
  return (
    <>
      <Slot name="left" className="vm-paper-code"/>
      <Slot name="right" className="vm-paper-model"/>
      {slots('plate','vm-paper-picture vm-paper-plate')}
      {slots('full','vm-paper-picture vm-paper-full')}
      {textSlots()}
      <PaperMasthead props={props}/>
    </>
  );
}
function SourceOnlySet({props}:SetComponentProps){
  return (
    <>
      <Slot name="source" className="vm-paper-source-only"/>
      {textSlots()}
      <PaperMasthead props={props}/>
    </>
  );
}

// ----- elements -----

function ViewElement(){
  // The runtime appends the view's viewer host into this element's box.
  return null;
}

/**
 * Wraps each emphasis range of the typed excerpt in <mark class="spoken">,
 * over the text nodes of the highlighted markup. Offsets are UTF-16 offsets
 * into the excerpt's text, the same offsets the timeline records; a range
 * whose text is not its token is refused.
 */
export function markSource(code:HTMLElement,state:Pick<SourceState,'text'|'emphasis'>):void{
  if(!state.emphasis.length)return;
  if(code.textContent!==state.text)throw new Error('the highlighted markup differs from the typed text');
  // Work backwards so wrapping one range cannot disturb an earlier offset.
  for(const range of [...state.emphasis].sort((a,b)=>b.start-a.start)){
    if(state.text.slice(range.start,range.end)!==range.token)
      throw new Error(`emphasis range ${range.start}–${range.end} differs from its token ${range.token}`);
    const walker=document.createTreeWalker(code,NodeFilter.SHOW_TEXT),nodes:{node:Text;start:number;end:number}[]=[];
    let node:Node|null,offset=0;
    while((node=walker.nextNode())){const text=node as Text;nodes.push({node:text,start:offset,end:offset+text.length});offset+=text.length;}
    const first=nodes.find(n=>range.start>=n.start&&range.start<n.end),last=nodes.find(n=>range.end>n.start&&range.end<=n.end);
    if(!first||!last)throw new Error(`emphasis of ${range.token} is outside the typed text`);
    const dom=document.createRange();
    dom.setStart(first.node,range.start-first.start);dom.setEnd(last.node,range.end-last.start);
    if(dom.toString()!==range.token)throw new Error(`emphasis mark differs from its token ${range.token}`);
    const mark=document.createElement('mark');mark.className='spoken';mark.dataset.token=range.token;
    mark.append(dom.extractContents());dom.insertNode(mark);
  }
}

function SourceElement({state}:ElementComponentProps<SourceState>){
  const code=useRef<HTMLElement>(null),stage=useStage(),key=useElementKey();
  // The markup is escaped by the Node highlighter; source is never executed.
  // Set on every commit, then the lit tokens wrapped.
  useLayoutEffect(()=>{
    const element=code.current;if(!element)return;
    element.innerHTML=state.html;
    try{markSource(element,state);}
    catch(error){stage.fail(new Error(`Source element ${key} in shot ${stage.frame.shotId}: ${(error as Error).message}`));}
  });
  return (
    <section className="vm-source">
      <div className="vm-source-file">{`${state.file} · L${state.firstLine}–${state.lastLine}`}</div>
      <pre><code ref={code} className="vm-source-code"/><span className="vm-source-cursor" style={{visibility:state.cursor?'visible':'hidden'}}/></pre>
    </section>
  );
}

function TitleElement({state}:ElementComponentProps<TitleState>){
  if(!state.shown)return null;
  let body:ReactNode=state.text;
  if(state.words){
    const revealed=state.revealed??0;let n=0;
    body=state.words.map((part,i)=>{
      if(!part.word)return part.text;
      const hidden=n++>=revealed;
      return <span key={i} className="vm-reveal-word" style={hidden?{visibility:'hidden'}:undefined}>{part.text}</span>;
    });
  }
  return (
    <div className="vm-title" style={state.opacity<1?{opacity:state.opacity}:undefined}>
      {body}
      {state.subtitle!==undefined&&<span className="vm-title-subtitle">{state.subtitle}</span>}
    </div>
  );
}

export const pictureSource=(state:Pick<PictureState,'media'|'name'|'frame'>):string=>state.media==='still'
  ?`/pictures/stills/${encodeURIComponent(state.name)}`
  :`/pictures/clips/${encodeURIComponent(state.name)}/${String(state.frame).padStart(6,'0')}.png`;

function PictureElement({state}:ElementComponentProps<PictureState>){
  const stage=useStage(),key=useElementKey();
  if(!state.shown)return null;
  const media=stage.config.media?.[state.media==='still'?'stills':'clips']?.[state.name];
  if(!media||!(media.width>0)||!(media.height>0))
    throw new Error(`Picture element ${key} in shot ${stage.frame.shotId} shows ${state.media} ${state.name}, whose size the stage config does not give`);
  if(state.media==='clip'&&!Number.isInteger(state.frame))
    throw new Error(`Picture element ${key} in shot ${stage.frame.shotId} shows clip ${state.name} without a frame number`);
  // The drawn rectangle is CSS arithmetic over the element's box (a size
  // container): the fit's scale times the zoom, centred on the view's centre.
  const geometry={
    '--vm-picture-aspect':String(media.width/media.height),
    '--vm-picture-zoom':String(state.view.zoom),
    '--vm-picture-cx':String(state.view.center[0]),
    '--vm-picture-cy':String(state.view.center[1]),
  } as CSSProperties;
  return (
    <div className="vm-picture" style={state.opacity<1?{opacity:state.opacity}:undefined}>
      <div className="vm-picture-plate"/>
      <img className="vm-picture-img" data-fit={state.fit} src={pictureSource(state)} alt="" style={geometry}/>
    </div>
  );
}

let registered=false;
/** Registers the shipped sets and elements, once. */
export function registerShipped():void{
  if(registered)return;
  registered=true;
  registerSet('frame',SHIPPED_SLOTS.frame,FrameSet,true);
  registerSet('split',SHIPPED_SLOTS.split,SplitSet,true);
  registerSet('paper',SHIPPED_SLOTS.paper,PaperSet,true);
  registerSet('paper-split',SHIPPED_SLOTS['paper-split'],PaperSplitSet,true);
  registerSet('source-only',SHIPPED_SLOTS['source-only'],SourceOnlySet,true);
  registerElement('view',ViewElement,true);
  registerElement('source',SourceElement,true);
  registerElement('title',TitleElement,true);
  registerElement('picture',PictureElement,true);
}
/** Tests only: allow registerShipped again after the registry is reset. */
export function forgetShipped():void{registered=false;}
