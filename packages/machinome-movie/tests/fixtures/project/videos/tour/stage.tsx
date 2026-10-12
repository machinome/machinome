// The tour movie's template: the sets Playbill and PlaybillSplit and the
// element Tally, declared in movie.py beside this file. The words on screen
// come from the movie (its title) and the set's props (its series); the
// layout and the look are this file's and stage.css's.
import {Chrome, Slot, defineElement, defineSet, useMovie} from 'videomaker/stage';
import type {ElementComponentProps, SetComponentProps} from 'videomaker/stage';
import type {PlaybillProps, PlaybillSplitProps, TallyState} from 'videomaker/movie';
import './stage.css';

// The masthead, drawn in Chrome so it stays above pictures and transitions.
function PlaybillChrome({series}: {series: string}) {
  const movie = useMovie();
  return (
    <Chrome>
      <div className="playbill-series">{series}</div>
      <div className="playbill-title">{movie.title}</div>
    </Chrome>
  );
}

// The root set: the model below the masthead, a plate over it for a picture,
// a headline band at its top and a card column at the right.
function Playbill({props}: SetComponentProps<PlaybillProps>) {
  return (
    <div className="playbill">
      <PlaybillChrome series={props.series}/>
      <Slot name="stage" className="playbill-stage"/>
      <Slot name="plate" className="playbill-plate"/>
      <Slot name="aside" className="playbill-aside"/>
      <Slot name="headline" className="playbill-headline"/>
    </div>
  );
}

// Derived by composition: Playbill's chrome, its own two containers.
function PlaybillSplit({props}: SetComponentProps<PlaybillSplitProps>) {
  return (
    <div className="playbill">
      <PlaybillChrome series={props.series}/>
      <Slot name="left" className="playbill-left"/>
      <Slot name="right" className="playbill-right"/>
      <Slot name="headline" className="playbill-headline"/>
    </div>
  );
}

// A card listing its items; the item a `light` action names is filled with
// the accent colour while the action lasts.
function Tally({state}: ElementComponentProps<TallyState>) {
  const lit = state.actions.find(a => a.action === 'light')?.params.item;
  return (
    <ul className="tally">
      {state.props.items.map(item => (
        <li key={String(item)} className={item === lit ? 'tally-item tally-lit' : 'tally-item'}>{String(item)}</li>
      ))}
    </ul>
  );
}

defineSet({kind: 'playbill', slots: ['stage', 'plate', 'headline', 'aside'], component: Playbill});
defineSet({kind: 'playbill-split', slots: ['left', 'right', 'headline'], component: PlaybillSplit});
defineElement({kind: 'tally', component: Tally});
