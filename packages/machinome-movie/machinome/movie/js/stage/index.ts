// `videomaker/stage`: the authoring API a project's stage module imports.
// A module registers its sets with defineSet and its elements with
// defineElement; a set lays out <Slot>s and draws its chrome inside <Chrome>;
// an element draws its state and may report measurements with useReport.
// The generated `videomaker/movie` types augment MovieSets and MovieElements,
// so a module is checked against its movie's document.
export {defineSet,defineElement} from './registry';
export {Slot,Chrome,useMovie,useReport,type SlotProps,type Report,type ReportSource} from './components';
export type {
  ActiveAction,ElementComponentProps,ElementDefinition,ElementState,ElementStateOf,EmphasisRange,HighlightState,
  MarkState,MovieElements,MovieInfo,MovieSets,MovieStyle,PictureState,ProjectActionShape,ProjectElementState,Rect,
  SetComponentProps,SetDefinition,SetPropsOf,ShippedElementState,SlotOf,SourceState,StageFrame,TitleState,TitleWord,
  Vec2,Vec3,ViewState,
} from './types';
