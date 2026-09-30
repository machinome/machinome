// Render-only identities for the already resolved global output requests.
// Nothing from this sidecar is inserted into frameAt or a shot-cache key.
import {activeOverlayEntries} from './timeline.mjs';
import {activeEmphasis} from './words.mjs';

export const REVIEW_SAMPLES_SCHEMA='review-samples-v1';
const candidate='resolved candidate, not reviewed';
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
const pair=index=>index>0?[index-1,index]:[index];
const key=indices=>indices.join(',');
const wordKey=(shotId,index)=>`${shotId}/overlay/${index}`;
const emphasisKey=(shotId,index,ordinal)=>`${shotId}/emphasis/${index}/${ordinal}`;

function selectedPictures(request){
  const transition=request.transition;
  if(!transition?.outgoing)return [{side:'incoming',frame:request}];
  if(transition.kind==='fade')return transition.picture==='outgoing'
    ?[{side:'outgoing',frame:transition.outgoing}]:[{side:'incoming',frame:request}];
  return [{side:'outgoing',frame:transition.outgoing},{side:'incoming',frame:request}];
}

function stateFor(e,record){
  const {index,time,request}=record,states=new Map();
  for(const {side,frame} of selectedPictures(request)){
    const shot=e.shots.find(s=>s.id===frame.shotId);
    if(!shot)throw new Error(`Review sample frame ${index} names unknown shot ${frame.shotId}`);
    const local=time-shot.start,entries=activeOverlayEntries(e,shot,local);
    if(entries.length!==frame.overlays.length)
      throw new Error(`Review overlay sidecar differs from frame ${index} in shot ${shot.id}`);
    entries.forEach(({index:authoredIndex,cue},position)=>{
      const drawn=frame.overlays[position];
      if(!same([drawn.text,drawn.from,drawn.to,drawn.position],
        [cue.text,cue.from,cue.to,cue.position]))
        throw new Error(`Review overlay sidecar differs from frame ${index} in shot ${shot.id}`);
      if(cue.reveal){
        const shown=drawn.shown;
        if(!Number.isInteger(shown)||shown<0)
          throw new Error(`Review word count differs from frame ${index} in shot ${shot.id}`);
        states.set(wordKey(shot.id,authoredIndex),{kind:'overlay',shotId:shot.id,
          authoredIndex,side,shown,description:cue.text});
      }
    });
    if(shot.code?.emphasis!==undefined){
      const measured=e.wordTiming?.[shot.id]?.emphasis;
      if(!Array.isArray(measured))throw new Error(`Review source emphasis is unresolved: shot ${shot.id}`);
      const active=measured.flatMap(entry=>entry.cues.flatMap((cue,ordinal)=>
        activeEmphasis([cue],local).map(()=>({authoredIndex:entry.index,ordinal,cue}))));
      const seen=frame.code?.emphasis??[];
      if(!same(active.map(({cue})=>({word:cue.word,line:cue.line,start:cue.start,end:cue.end})),seen))
        throw new Error(`Review source emphasis sidecar differs from frame ${index} in shot ${shot.id}`);
      for(const {authoredIndex,ordinal,cue} of active){
        states.set(emphasisKey(shot.id,authoredIndex,ordinal),{kind:'emphasis',shotId:shot.id,
          authoredIndex,wordOrdinal:ordinal,side,word:cue.word,line:cue.line,
          start:cue.start,end:cue.end,description:shot.code.emphasis[authoredIndex]?.phrase??cue.word});
      }
    }
  }
  return states;
}

export function buildReviewSamplePlan(e,units,fps){
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
    const {index,request}=record,states=stateFor(e,record),selected=selectedPictures(request);
    const priorPictures=previous?selectedPictures(previous.request):[];
    if(previous&&request.shotId!==previous.request.shotId)
      add(pair(index),{kind:'join',shotId:request.shotId,
        outgoingShotId:request.transition?.outgoingShotId??previous.request.shotId,
        sides:selected.map(x=>x.side),description:`${previous.request.shotId} to ${request.shotId}`});
    for(const [id,current] of states){
      const old=previousStates.get(id),base={shotId:current.shotId,
        authoredIndex:current.authoredIndex,side:current.side,description:current.description};
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
        const cueKey=`${old.shotId}/${old.authoredIndex}`;
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
