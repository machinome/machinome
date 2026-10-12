// The shapes the stage receives and the types a project's module is written
// against. The frame is what the Node timeline resolves for one instant
// (docs/movie-document.md, "The frame"); the registry interfaces MovieSets and
// MovieElements are empty here and augmented per movie by the generated
// movie.d.ts, so a module's sets and elements are checked against its document.
import type {ComponentType} from 'react';
// A vector, a rectangle and a machine's bank are the viewer's handle's, which
// the take transport declares (ADR-020); the stage gives authors the same names.
import type {Bank,Rect,Vec3} from '../transport/viewer-handle';
export type {Bank,Rect,Vec3};

export type Vec2=[number,number];

export interface MovieStyle {
  background:string;
  foreground:string;
  accent:string;
  fontFamily:string;
  safeInsetFraction:number;
}
/** What `useMovie()` returns and a set receives as `movie`. */
export interface MovieInfo {id:string;title:string;series:string;style:MovieStyle}

// Shipped element states.
export interface MarkState {
  id:string;
  kind:'ring'|'label'|'arrow';
  target:{paths:string[][]}|{point:Vec3};
  text?:string;
  /** Arrow: where its text sits, as fractions of the view element's box. */
  place?:Vec2;
  /** Label: the text's offset from the part, as fractions of the view element's box. */
  offset?:Vec2;
  /** Ring: padding around the part, as a fraction of the view element's box width. */
  padding?:number;
  opacity:number;
  drawn:number;
}
export interface HighlightState {paths:string[][];others?:string;color?:string}
/**
 * A view's state: on a posed loop its normalized loop `time`; on a clocked
 * take, instead, the machine's whole `bank` at the view's take time, which
 * the stage restores on the viewer's machine (ADR-012).
 */
export interface ViewState {
  kind:'view';
  time?:number;
  bank?:Bank;
  view:{camera:Vec3;target:Vec3};
  up?:Vec3;
  fov?:number;
  hidden:string[][];
  highlight:HighlightState|null;
  marks:MarkState[];
}
export interface EmphasisRange {token:string;start:number;end:number}
export interface SourceState {
  kind:'source';
  file:string;
  firstLine:number;
  lastLine:number;
  text:string;
  html:string;
  cursor:boolean;
  emphasis:EmphasisRange[];
}
export interface TitleWord {text:string;word:boolean;start:number;end:number}
export interface TitleState {
  kind:'title';
  shown:boolean;
  text:string;
  subtitle?:string;
  opacity:number;
  words?:TitleWord[];
  revealed?:number;
}
export interface PictureState {
  kind:'picture';
  shown:boolean;
  media:'still'|'clip';
  name:string;
  fit:'contain'|'cover';
  opacity:number;
  view:{center:Vec2;zoom:number};
  frame?:number;
  clipSeconds?:number;
}
export interface ProjectActionShape {action:string;params:Record<string,unknown>}
/** One active action of a project element, with where it is in its span. */
export type ActiveAction<A extends ProjectActionShape=ProjectActionShape>=A&{since:number;until:number;progress:number};
/** A project element's state: its declared props and its active actions. */
export interface ProjectElementState<P=Record<string,unknown>,A extends ProjectActionShape=ProjectActionShape> {
  kind:string;
  props:P;
  actions:ActiveAction<A>[];
}
export type ShippedElementState=ViewState|SourceState|TitleState|PictureState;
export type ElementState=ShippedElementState|ProjectElementState;

/**
 * The join a frame carries when its shot comes in by a reframe (ADR-010): the
 * eased progress, which every element but the moving views is drawn at as
 * opacity, and the box each moving view is drawn in, `[x, y, width, height]`
 * as fractions of the frame. The other joins are composed by the renderer
 * and reach the stage as compositions, not on the frame.
 */
export interface ReframeTransition {
  kind:'reframe';
  progress:number;
  boxes:Record<string,readonly number[]>;
}
export interface StageFrame {
  time:number;
  chapterId:string;
  shotId:string;
  set:string;
  slots:Record<string,string>;
  elements:Record<string,ElementState>;
  transition?:ReframeTransition|null|unknown;
  pictureOnly?:boolean;
  fresh?:boolean;
}

/** The renderer's config.json. */
export interface StageConfig {
  movie:{id:string;title:string;series:string;style?:Partial<MovieStyle>};
  stage:{sets:Record<string,{slots:string[];props?:Record<string,unknown>}>;elements?:string[]};
  media?:{stills?:Record<string,{width:number;height:number}>;clips?:Record<string,{width:number;height:number}>};
  viewer?:{required?:{api:number;reasons?:string[]};refusal?:string};
  /** A take document's machine identity, which a view on the take restores with. */
  take?:{identity:string};
}

// The per-movie registry, augmented by the generated movie.d.ts:
//   declare module 'videomaker/stage' {
//     interface MovieSets {'playbill': {slot: 'stage'|'plate'; props: {series: string}}}
//     interface MovieElements {'tally': {props: {items: unknown[]}; actions: {action: 'light'; params: {item: string}}}}
//   }
// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface MovieSets {}
// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface MovieElements {}

type Field<T,F extends string>=T extends {[K in F]:infer V}?V:never;

export interface SetComponentProps<P=Record<string,unknown>> {movie:MovieInfo;props:P}
export interface ElementComponentProps<S=ElementState> {state:S}

export interface ShippedElements {view:ViewState;source:SourceState;title:TitleState;picture:PictureState}

/** The slot names the document declares for a set kind, or any string for a kind it does not. */
export type SlotOf<K extends string>=K extends keyof MovieSets?Field<MovieSets[K],'slot'>&string:string;
/** The static props the document gives a set kind. */
export type SetPropsOf<K extends string>=K extends keyof MovieSets?Field<MovieSets[K],'props'>:Record<string,unknown>;
/** The state an element kind's component receives. */
export type ElementStateOf<K extends string>=K extends keyof MovieElements
  ?ProjectElementState<Field<MovieElements[K],'props'>,Field<MovieElements[K],'actions'>&ProjectActionShape>
  :K extends keyof ShippedElements?ShippedElements[K]:ProjectElementState;

type Missing<K extends string,L extends readonly string[]>=Exclude<SlotOf<K>,L[number]>;
/** A set's slots: exactly the document's, in any order. */
export type SlotsOf<K extends string,L extends readonly string[]>=K extends keyof MovieSets
  ?(L[number] extends SlotOf<K>?([Missing<K,L>] extends [never]?L:{slotsDifferFromTheDocument:true;missing:Missing<K,L>}):readonly SlotOf<K>[])
  :L;

export interface SetDefinition<K extends string=string,L extends readonly string[]=readonly string[]> {
  kind:K;
  slots:L;
  component:ComponentType<SetComponentProps<SetPropsOf<K>>>;
}
export interface ElementDefinition<K extends string=string> {
  kind:K;
  component:ComponentType<ElementComponentProps<ElementStateOf<K>>>;
}
