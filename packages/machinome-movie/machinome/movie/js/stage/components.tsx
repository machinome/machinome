// The React half of the authoring API: the stage's contexts, <Stage> (which
// mounts the set a frame names), <Slot>, <Chrome>, useMovie and useReport.
// Every component here is a pure function of the frame it is given: no clock,
// no state carried between frames.
import {createContext,useContext,useLayoutEffect,type CSSProperties,type ReactNode} from 'react';
import {createPortal} from 'react-dom';
import {elementOf,setOf} from './registry';
import type {MovieInfo,ReframeTransition,StageConfig,StageFrame} from './types';

/** The reframe a frame carries, or null (ADR-010). */
export function reframeOf(frame:StageFrame):ReframeTransition|null{
  const x=frame.transition as {kind?:unknown}|null|undefined;
  return x&&typeof x==='object'&&x.kind==='reframe'?x as ReframeTransition:null;
}

export type Report=Record<string,unknown>;
export type ReportSource=Report|(()=>Report);

/** What one commit of the stage shares with its components. */
export interface StageContextValue {
  frame:StageFrame;
  config:Pick<StageConfig,'stage'|'media'>;
  /** Where Chrome portals its children; `#chrome` when not given. */
  chromeLayer:HTMLElement|null;
  /** Reports of this commit, by element key (useReport). */
  reports:Map<string,ReportSource>;
  /** Errors met by components' layout effects; the runtime rethrows them after the commit. */
  fail:(error:Error)=>void;
}

export const MovieContext=createContext<MovieInfo|null>(null);
export const StageContext=createContext<StageContextValue|null>(null);
export const ElementKeyContext=createContext<string|null>(null);

export function useStage():StageContextValue{
  const stage=useContext(StageContext);
  if(!stage)throw new Error('A stage component is rendered outside the stage');
  return stage;
}
/** The element key (`<chapter>.<element>`) of the element being drawn. */
export function useElementKey():string{
  const key=useContext(ElementKeyContext);
  if(key===null)throw new Error('An element hook is used outside an element');
  return key;
}
/** The movie: id, title, series and style (with the style's defaults applied). */
export function useMovie():MovieInfo{
  const movie=useContext(MovieContext);
  if(!movie)throw new Error('useMovie is used outside the stage');
  return movie;
}
/**
 * Reports JSON measurements of the element being drawn; the stage merges them
 * into its `observed.elements[key]` beside the `box` it always adds. Give a
 * function to measure after the commit (read refs there); it must not change
 * what is drawn.
 */
export function useReport(report:ReportSource):void{
  const stage=useStage(),key=useElementKey();
  useLayoutEffect(()=>{stage.reports.set(key,report);});
}

export interface SlotProps {name:string;className?:string;style?:CSSProperties}
/** Where a set puts the element a shot places in the slot `name`; an empty box otherwise. */
export function Slot({name,className,style}:SlotProps){
  const stage=useStage(),{frame}=stage;
  const key=Object.hasOwn(frame.slots,name)?frame.slots[name]:undefined;
  let content:ReactNode=null;
  if(key!==undefined){
    const state=frame.elements[key];
    if(!state)throw new Error(`Slot ${name} of set ${frame.set} places element ${key}, which frame ${frame.shotId} does not carry`);
    const registered=elementOf(state.kind);
    if(!registered)throw new Error(`Element kind ${state.kind} of element ${key} is not registered by the stage modules`);
    const Component=registered.component;
    // During a reframe every element but the moving views fades in by the
    // join's progress; at its end nothing is written, as without a join.
    const reframe=reframeOf(frame);
    const fade=reframe&&!Object.hasOwn(reframe.boxes,key)&&reframe.progress<1?{opacity:reframe.progress}:undefined;
    content=(
      <ElementKeyContext.Provider key={key} value={key}>
        <div className={`vm-element vm-element-${state.kind}`} data-element={key} style={fade}>
          <Component state={state}/>
        </div>
      </ElementKeyContext.Provider>
    );
  }
  return <div className={['vm-slot',`vm-slot-${name}`,className].filter(Boolean).join(' ')} data-slot={name} style={style}>{content}</div>;
}

/**
 * What a set draws above pictures and transitions (a masthead, a label). The
 * stage lifts it into the `#chrome` layer, hides it in picture-only captures
 * and reports the rectangles of its top-level elements for the proofs' mask.
 */
export function Chrome({children,className}:{children?:ReactNode;className?:string}){
  const stage=useStage();
  const layer=stage.chromeLayer??(typeof document==='undefined'?null:document.getElementById('chrome'));
  if(!layer)return null;
  return createPortal(<div className={['vm-chrome',className].filter(Boolean).join(' ')}>{children}</div>,layer);
}

/** Mounts the registered component of `frame.set` with the movie and the set's static props. */
export function Stage({movie,stage}:{movie:MovieInfo;stage:StageContextValue}){
  const {frame,config}=stage,set=setOf(frame.set);
  if(!set)throw new Error(`Set kind ${frame.set} of shot ${frame.shotId} is not registered by the stage modules`);
  const Component=set.component,props=config.stage.sets[frame.set]?.props??{};
  return (
    <MovieContext.Provider value={movie}>
      <StageContext.Provider value={stage}>
        <div key={frame.set} className={`vm-set vm-set-${frame.set}`} data-set={frame.set}>
          <Component movie={movie} props={props}/>
        </div>
      </StageContext.Provider>
    </MovieContext.Provider>
  );
}
