// Render-only identities for the already resolved global output requests,
// read from their element states (design D8): a title's revealed words and a
// source panel's lit tokens, by shot, element and cue. Nothing from this
// sidecar is inserted into frameAt or a shot-cache key.
import {filmShots,shotActions,tokenRange} from './timeline.mjs';

export const REVIEW_SAMPLES_SCHEMA='review-samples-v1';
const candidate='resolved candidate, not reviewed';
const pair=index=>index>0?[index-1,index]:[index];
const key=indices=>indices.join(',');
const live=(from,to,local,duration)=>local>=from-1e-9&&(local<to-1e-9||(local>=duration&&Math.abs(to-duration)<1e-9));

function selectedPictures(request){
  const transition=request.transition;
  if(!transition?.outgoing)return [{side:'incoming',frame:request}];
  if(transition.kind==='fade')return transition.picture==='outgoing'
    ?[{side:'outgoing',frame:transition.outgoing}]:[{side:'incoming',frame:request}];
  return [{side:'outgoing',frame:transition.outgoing},{side:'incoming',frame:request}];
}

function stateFor(film,record){
  const {index,time,request}=record,states=new Map(),shots=filmShots(film);
  for(const {side,frame} of selectedPictures(request)){
    const at=shots.find(x=>x.shot.id===frame.shotId);
    if(!at)throw new Error(`Review sample frame ${index} names unknown shot ${frame.shotId}`);
    const {chapter,shot}=at,local=time-shot.start,duration=shot.end-shot.start,actions=shotActions(shot);
    for(const [elementKey,state] of Object.entries(frame.elements)){
      const own=actions.filter(x=>`${chapter.id}.${x.action.element}`===elementKey);
      if(state.kind==='title'&&state.shown&&state.words){
        const x=own.find(x=>x.action.action==='show'&&live(x.cue.at,x.cue.until,local,duration));
        if(!x||!Number.isInteger(state.revealed)||state.revealed<0)
          throw new Error(`Review word count differs from frame ${index} in shot ${shot.id}`);
        states.set(`${shot.id}/overlay/${x.id}`,{kind:'overlay',shotId:shot.id,element:elementKey,
          authoredIndex:x.action.overlay??shot.cues.indexOf(x.cue),cue:x.id,side,shown:state.revealed,description:chapter.elements[x.action.element].text});
      }
      if(state.kind==='source'){
        const snippet=film.excerpts[chapter.elements[own[0]?.action.element??'']?.source]??null;
        const active=own.filter(x=>x.action.action==='emphasize').flatMap(x=>x.action.words.flatMap((word,ordinal)=>
          local>=word.at-1e-9&&local<x.action.until-1e-9?[{x,word,ordinal,...tokenRange(snippet,word.token,x.action.line)}]:[]));
        const seen=state.emphasis.map(e=>`${e.token}@${e.start}`).sort(),mine=active.map(a=>`${a.word.token}@${a.start}`).sort();
        if(JSON.stringify(seen)!==JSON.stringify(mine))
          throw new Error(`Review source emphasis sidecar differs from frame ${index} in shot ${shot.id}`);
        for(const {x,word,ordinal,start,end} of active)
          states.set(`${shot.id}/emphasis/${x.id}/${ordinal}`,{kind:'emphasis',shotId:shot.id,element:elementKey,
            authoredIndex:x.action.emphasis??shot.cues.indexOf(x.cue),cue:x.id,wordOrdinal:ordinal,side,word:word.token,line:x.action.line??snippet.lines[0]+(snippet.text.slice(0,start).match(/\n/g)?.length??0),start,end,
            description:x.action.phrase??x.action.words.map(w=>w.spoken).join(' ')});
      }
    }
  }
  return states;
}

export function buildReviewSamplePlan(film,units,fps){
  const frames=units.flatMap(unit=>unit.frames).toSorted((a,b)=>a.index-b.index),count=frames.length;
  if(!Number.isInteger(fps)||fps<1||frames.some((frame,i)=>frame.index!==i))
    throw new Error('Review sample plan needs a contiguous global output grid');
  const samples=new Map();
  const add=(indices,label)=>{
    const id=key(indices),entry=samples.get(id)??{indices,labels:[]};
    entry.labels.push({...label,visibility:candidate});samples.set(id,entry);
  };
  let previous=null,previousStates=new Map(),run=[],runIdentity=null;
  const finishRun=()=>{
    if(!run.length)return;
    const middle=run[Math.floor((run.length-1)/2)],last=run.at(-1);
    const t=frames[middle].request.transition;
    for(const [kind,at] of [['transition-midpoint',middle],['transition-last-active',last]])
      add([at],{kind,field:t.field,shotId:t.shotId,
        ...(t.outgoingShotId?{outgoingShotId:t.outgoingShotId}:{}),
        sides:selectedPictures(frames[at].request).map(x=>x.side),
        description:t.outgoingShotId?`${t.outgoingShotId} to ${t.shotId}`:`${t.field} ${t.shotId}`});
    run=[];runIdentity=null;
  };
  for(const record of frames){
    const {index,request}=record,states=stateFor(film,record),selected=selectedPictures(request);
    const priorPictures=previous?selectedPictures(previous.request):[];
    if(previous&&request.shotId!==previous.request.shotId)
      add(pair(index),{kind:'join',shotId:request.shotId,
        outgoingShotId:request.transition?.outgoingShotId??previous.request.shotId,
        sides:selected.map(x=>x.side),description:`${previous.request.shotId} to ${request.shotId}`});
    for(const [id,current] of states){
      const old=previousStates.get(id),base={shotId:current.shotId,
        authoredIndex:current.authoredIndex,...(current.cue?{cue:current.cue}:{}),...(current.element?{element:current.element}:{}),side:current.side,description:current.description};
      const wasSelected=priorPictures.some(x=>x.frame.shotId===current.shotId);
      const fadeEntry=!wasSelected&&current.side==='incoming'&&
        (request.transition?.kind==='fade'||
          previous?.request.shotId===current.shotId&&
          previous.request.transition?.kind==='fade'&&
          previous.request.transition.picture==='outgoing');
      if(current.kind==='overlay'){
        if(old){
          if(current.shown<old.shown)throw new Error(`Review word count went backwards: ${id}`);
          for(let ordinal=old.shown;ordinal<current.shown;ordinal++)
            add(pair(index),{...base,kind:'word-onset',wordOrdinal:ordinal,shown:current.shown});
        }else if(current.shown>0){
          if(!fadeEntry)for(let ordinal=0;ordinal<current.shown;ordinal++)
            add(pair(index),{...base,kind:'word-onset',wordOrdinal:ordinal,shown:current.shown});
          else add(pair(index),{...base,kind:'picture-entry',shown:current.shown});
        }
      }else if(!old){
        if(previous&&fadeEntry)
          add(pair(index),{...base,kind:'picture-entry',wordOrdinal:current.wordOrdinal,
            word:current.word,line:current.line,start:current.start,end:current.end});
        else add(pair(index),{...base,kind:'source-emphasis-onset',wordOrdinal:current.wordOrdinal,
          word:current.word,line:current.line,start:current.start,end:current.end});
      }
    }
    const clears=new Map();
    for(const [id,old] of previousStates)if(old.kind==='emphasis'&&!states.has(id)){
      // A fade can remove a side from the picture. That is a picture switch,
      // not a timed emphasis clear. A continuing selected side can clear.
      const selectedSide=selected.find(x=>x.frame.shotId===old.shotId)?.side;
      if(selectedSide){
        const cueKey=`${old.shotId}/${old.element}/${old.authoredIndex}`;
        const clear=clears.get(cueKey)??{kind:'source-emphasis-clear',shotId:old.shotId,
          authoredIndex:old.authoredIndex,side:selectedSide,description:old.description,words:[]};
        clear.words.push({wordOrdinal:old.wordOrdinal,word:old.word,line:old.line,
          start:old.start,end:old.end});clears.set(cueKey,clear);
      }
    }
    for(const clear of clears.values())add(pair(index),clear);
    const transition=request.transition;
    const identity=transition?`${transition.field}/${transition.shotId}`:null;
    if(run.length&&identity!==runIdentity)finishRun();
    if(identity){runIdentity=identity;run.push(index);}
    previous=record;previousStates=states;
  }
  finishRun();
  for(const unit of units){
    const last=unit.frames.at(-1)?.index;
    if(last!==undefined)add(unit.frames.length>1?[unit.frames.at(-2).index,last]:[last],
      {kind:'shot-end',shotId:unit.shotId,description:`shot ${unit.shotId} end`});
  }
  if(count)add(count>1?[count-2,count-1]:[0],
    {kind:'film-end',shotId:frames.at(-1).request.shotId,description:'film end'});
  return {schema:REVIEW_SAMPLES_SCHEMA,frameCount:count,fps,
    samples:[...samples.values()].toSorted((a,b)=>a.indices.at(-1)-b.indices.at(-1)||a.indices.length-b.indices.length)};
}
