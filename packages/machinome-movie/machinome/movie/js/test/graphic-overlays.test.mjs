import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi,PAPER_STAGE} from '../src/episode.mjs';
import {yamlFrame,element,viewAt,placeInBox,offsetInBox,paddingInBox} from './frame-fixtures.mjs';
import {EASINGS,ease} from '../src/easing.mjs';
import {fadeSubsets} from '../src/render.mjs';

// Rings, entrances and exits (graphic-overlays). Node only: validation and the
// numbers the timeline emits; the page and preview are proved in render.test.mjs.
const V02='machinome-video-draft/0.2',V03='machinome-video-draft/0.3',V04='machinome-video-draft/0.4';
const manifest={animation:{loop:296},root:{name:'Mill',children:[
  {name:'Feed mechanism',children:[{name:'Driving pawl'},{name:'Holding pawl'},{name:'Ratchet to reduction shaft'}]},
  {name:'Frame'}]}};
const shot=(id,start,end,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
const DRIVING=['Feed mechanism','Driving pawl'],HOLDING=['Feed mechanism','Holding pawl'];
// The annotated() shape of annotations.test.mjs, declared 0.4, with a ring on a
// path (#0), a ring on a two-path layer (#1), an arrow drawn on (#2) and a label
// fading in and out (#3).
const overlays=()=>({format:V04,
  output:{width:1280,height:720,fps:30,durationSeconds:4},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{feed:[['Feed mechanism']],pawls:[DRIVING,HOLDING],'rope-1':[['Feed mechanism','Ratchet to reduction shaft']],frame:[['Frame']]},evidence:{},
  shots:[shot('pawls',0,2,{annotations:[
      {from:0,to:1,kind:'ring',part:DRIVING},
      {from:1,to:2,kind:'ring',part:'pawls',padding:.02},
      {from:.5,to:2,kind:'arrow',part:DRIVING,place:[.1,.3],text:'Driving pawl',enter:{kind:'draw',duration:.8,ease:'out'}},
      {from:0,to:2,kind:'label',part:HOLDING,offset:[.12,-.03],text:'Holding pawl',enter:{kind:'fade',duration:.5},leave:{kind:'fade',duration:.4}}]}),
    shot('plain',2,4)]});
const valid=e=>validateEpisode(e,manifest);
// Annotation #i of the shot is the view's mark cues[i].actions[0] (the shot has
// one camera key, so no move comes before its annotations' cues), with its
// safe-area place, offset and padding in the view's box.
const box=PAPER_STAGE.paper,id=index=>`cues[${index}].actions[0]`;
const cue=(e,t,index)=>viewAt(e,t).marks.find(a=>a.id===id(index));

test('simultaneous fades preserve an opaque intervening label and compose overlapping marks at their authored opacities',()=>{
  const mark=(id,opacity)=>({id,kind:'label',target:{point:[0,0,0]},text:id,offset:[0,0],opacity,drawn:1});
  const frame={time:0,chapterId:'c',shotId:'s',set:'paper',slots:{stage:'c.view'},transition:null,
    elements:{'c.view':{kind:'view',time:0,view:{camera:[0,0,1],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[],highlight:null,
      marks:[mark('m0',.25),mark('m1',1),mark('m2',.6)]}}};
  const variants=fadeSubsets(frame);
  const drawn=v=>v.elements['c.view'].marks;
  assert.deepEqual(variants.map(v=>drawn(v).map(a=>a.id)),[['m1'],['m0','m1'],['m1','m2'],['m0','m1','m2']]);
  assert.deepEqual(variants.map(v=>v.weight),[.75*.4,.25*.4,.75*.6,.25*.6]);
  assert.equal(variants.reduce((sum,v)=>sum+v.weight,0),1);
  // Each subset draws its marks whole: the blend, not the mark, carries the opacity.
  for(const v of variants)for(const a of drawn(v)){assert.equal(a.opacity,1);assert.equal(a.drawn,1);}
  assert.deepEqual(frame.elements['c.view'].marks.map(m=>m.opacity),[.25,1,.6],'the frame itself is not changed');
  // One overlapping pixel: the middle, opaque label hides mark 0. Mark 2
  // remains above it. The subset blend must equal that draw order exactly.
  const pixel=chosen=>chosen.reduce((under,a)=>a.id==='m0'?100:a.id==='m1'?180:30,20);
  const mixed=variants.reduce((sum,v)=>sum+v.weight*pixel(drawn(v)),0);
  assert.ok(Math.abs(mixed-(.6*30+.4*180))<1e-12);
  // A frame with nothing fading has no subsets.
  const plain=structuredClone(frame);for(const m of plain.elements['c.view'].marks)m.opacity=1;
  assert.equal(fadeSubsets(plain),null);
});

test('a 0.4 episode with rings, a drawn arrow and a fading label validates, and rings are emitted with explicit padding',()=>{
  const e=overlays();
  assert.doesNotThrow(()=>valid(e));
  assert.deepEqual(cue(e,.5,0),{id:id(0),kind:'ring',target:{paths:[DRIVING]},padding:paddingInBox(.01,.08,box),opacity:1,drawn:1});
  assert.deepEqual(cue(e,1.5,1),{id:id(1),kind:'ring',target:{paths:[DRIVING,HOLDING]},padding:paddingInBox(.02,.08,box),opacity:1,drawn:1});
  assert.equal(cue(e,1,0),undefined,'a ring ends at its to');
});

test('opacity and drawn fraction follow the entrance and exit through their easing',()=>{
  const e=overlays();valid(e);
  const label=t=>cue(e,t,3),arrow=t=>cue(e,t,2);
  assert.equal(label(0).opacity,0,'a fade starts from nothing');
  assert.equal(label(.25).opacity,ease('smooth',.5),'default smooth at the entrance midpoint');
  assert.equal(label(.5).opacity,1,'exactly the mark at the entrance end');
  assert.equal(label(1.6).opacity,1,'exactly the mark at the exit start');
  // The exit midpoint as D4 computes it in binary, (l - (to - d)) / d at 1.8 s.
  assert.equal(label(1.8).opacity,1-ease('smooth',(1.8-(2-.4))/.4));
  assert.ok(Math.abs(label(1.8).opacity-(1-ease('smooth',.5)))<1e-12);
  assert.ok(label(2-1/30).opacity>0&&label(2-1/30).opacity<.02,'nearly gone on the last frame of the cue');
  for(const t of [0,.25,.5,1,1.6,1.8])assert.equal(label(t).drawn,1,`a fade draws the whole mark at ${t}`);
  assert.equal(arrow(.5).drawn,0,'a draw-on starts with none of its stroke');
  assert.equal(arrow(.9).drawn,ease('out',.5));assert.equal(arrow(.9).drawn,.875);
  for(const t of [1.3,1.5,1.9])assert.equal(arrow(t).drawn,1,`drawn exactly from from + 0.8 on, at ${t}`);
  for(const t of [.5,.9,1.3,1.9])assert.equal(arrow(t).opacity,1,`a draw-on never fades, at ${t}`);
  for(const name of EASINGS){
    const eased=overlays();eased.shots[0].annotations[3].enter.ease=name;valid(eased);
    assert.equal(cue(eased,.125,3).opacity,ease(name,.25),name);
  }
  // The whole cue as emitted: the mark's own fields, then opacity and drawn.
  assert.deepEqual(arrow(.9),{id:id(2),kind:'arrow',text:'Driving pawl',target:{paths:[DRIVING]},place:placeInBox([.1,.3],.08,box),opacity:1,drawn:.875});
  assert.deepEqual(label(.5),{id:id(3),kind:'label',text:'Holding pawl',target:{paths:[HOLDING]},offset:offsetInBox([.12,-.03],.08,box),opacity:1,drawn:1});
});

test('a 0.4 cue without enter, leave or padding is emitted exactly as the same cue in 0.3, whole and at full strength',()=>{
  const plain=format=>{const e=overlays();e.format=format;const a=e.shots[0].annotations;
    a.splice(0,2);delete a[0].enter;delete a[1].enter;delete a[1].leave;return e;};
  const old=plain(V03),next=plain(V04);valid(old);valid(next);
  for(const t of [0,.5,1,1.5,1.9]){
    assert.deepEqual(yamlFrame(next,t),yamlFrame(old,t),`at ${t}`);
    for(const a of viewAt(next,t).marks){assert.equal(a.opacity,1);assert.equal(a.drawn,1);}
  }
});

test('into a transition, a cue that leaves is gone, and one that does not continues at full strength',()=>{
  const e=overlays();e.shots[1].transition={kind:'dissolve',duration:1};valid(e);
  const outgoing=(e,t)=>element(yamlFrame(e,t).transition.outgoing,'view').marks;
  for(const t of [2,2.5,2.9]){
    const out=outgoing(e,t);
    assert.deepEqual(out.map(a=>a.id),[id(1),id(2)],`only the cues without leave at ${t}`);
    assert.deepEqual(out[0],{id:id(1),kind:'ring',target:{paths:[DRIVING,HOLDING]},padding:paddingInBox(.02,.08,box),opacity:1,drawn:1});
    assert.equal(out[1].opacity,1);assert.equal(out[1].drawn,1);
  }
  const kept=overlays();delete kept.shots[0].annotations[3].leave;kept.shots[1].transition={kind:'dissolve',duration:1};valid(kept);
  const label=outgoing(kept,2.5).find(a=>a.id===id(3));
  assert.equal(label.opacity,1);assert.equal(label.drawn,1);
});

const refused=(edit,pattern,format)=>{
  const e=overlays();if(format)e.format=format;edit(e.shots[0].annotations,e);
  assert.throws(()=>valid(e),error=>pattern.test(error.message)&&/pawls/.test(error.message),String(pattern));
};

test('invalid rings, entrances and exits are refused before rendering, naming the shot and annotation',()=>{
  refused(a=>{a[0].kind='callout';},/^Invalid annotation #0 in shot pawls: kind must be arrow, label or ring$/);
  refused(a=>{delete a[0].part;a[0].point=[0,0,0];},/^Invalid annotation #0 in shot pawls: a ring is drawn around a part; give part, not point$/);
  for(const [field,value] of [['text','Pawl'],['place',[.1,.1]],['offset',[0,0]]])
    refused(a=>{a[0][field]=value;},/^Invalid annotation #0 in shot pawls: a ring carries no text or place; add a label or an arrow beside it$/);
  for(const padding of [-.1,.3,'0.02',Infinity])
    refused(a=>{a[1].padding=padding;},/^Invalid annotation #1 in shot pawls: padding must be a number in \[0, 0\.25\]$/);
  refused(a=>{a[2].padding=.02;},/^Invalid annotation #2 in shot pawls: padding belongs to a ring$/);
  refused(a=>{a[3].padding=.02;},/^Invalid annotation #3 in shot pawls: padding belongs to a ring$/);
  refused(a=>{a[3].enter='fade';},/^Invalid annotation #3 in shot pawls: enter must be a mapping \{kind, duration, ease\}$/);
  refused(a=>{a[3].leave=[];},/^Invalid annotation #3 in shot pawls: leave must be a mapping \{kind, duration, ease\}$/);
  refused(a=>{a[3].enter={kind:'fade',durration:1};},/^Unknown entrance field: durration \(annotation #3 in shot pawls\)$/);
  refused(a=>{a[3].leave={kind:'fade',duration:.4,eas:'in'};},/^Unknown exit field: eas \(annotation #3 in shot pawls\)$/);
  refused(a=>{a[3].enter.kind='scale';},/^Invalid annotation #3 in shot pawls: the entrance kind must be fade or draw$/);
  refused(a=>{a[3].leave.kind='draw';},/^Invalid annotation #3 in shot pawls: the exit kind must be fade$/);
  refused(a=>{a[3].enter={kind:'draw'};},/^Invalid annotation #3 in shot pawls: a label has no stroke to draw; enter with fade$/);
  refused(a=>{a[3].enter.ease='bounce';},/^Unknown easing: bounce; use linear, smooth, in, out or in-out \(entrance of annotation #3 in shot pawls\)$/);
  refused(a=>{a[3].leave.ease='ease-out';},/^Unknown easing: ease-out; use linear, smooth, in, out or in-out \(exit of annotation #3 in shot pawls\)$/);
  refused(a=>{a[3].enter.duration=1/60;},/^Invalid annotation #3 in shot pawls: the entrance duration must be at least two frames \(0\.067 s at 30 fps\)$/);
  refused(a=>{delete a[3].leave.duration;},/^Invalid annotation #3 in shot pawls: the exit duration must be at least two frames/);
  refused(a=>{a[0].enter={kind:'draw',duration:1.2};},/^Invalid annotation #0 in shot pawls: the 1\.2 s entrance is longer than the cue \(1 s\)$/);
  refused(a=>{a[0].leave={kind:'fade',duration:1.5};},/^Invalid annotation #0 in shot pawls: the 1\.5 s exit is longer than the cue \(1 s\)$/);
  refused(a=>{Object.assign(a[0],{to:1.2,enter:{kind:'draw',duration:.8},leave:{kind:'fade',duration:.6}});},
    /^Entrance and exit overlap in annotation #0 in shot pawls: 0\.8 s in and 0\.6 s out exceed its 1\.2 s$/);
  refused((a,e)=>{e.shots[0].hiddenLayers=['feed'];},/^Annotated part is hidden in shot pawls: Feed mechanism\/Driving pawl \(annotation #0\)$/);
  refused((a,e)=>{e.shots[0].hiddenLayers=['frame'];a[1].part='frame';},/^Annotated part is hidden in shot pawls: Frame \(annotation #1\)$/);
  // An entrance and an exit that together fill the cue are accepted.
  const e=overlays();Object.assign(e.shots[0].annotations[0],{to:1.2,enter:{kind:'draw',duration:.8},leave:{kind:'fade',duration:.4}});
  assert.doesNotThrow(()=>valid(e));
});

test('rings, padding, entrances and exits need format 0.4; 0.2 keeps its annotations message',()=>{
  // The 0.3 base: the arrow and the label without the new fields.
  const older=(format,edit)=>a=>{a.splice(0,2);delete a[0].enter;delete a[1].enter;delete a[1].leave;edit(a);};
  const e=overlays();e.format=V03;older(V03,()=>{})(e.shots[0].annotations);
  assert.doesNotThrow(()=>valid(e),'the same episode without the new fields is a valid 0.3');
  const format=/^Rings, entrances and exits need format machinome-video-draft\/0\.4: shot pawls/;
  refused(older(V03,a=>{a[0].kind='ring';delete a[0].place;delete a[0].text;}),format,V03);
  refused(older(V03,a=>{a[0].kind='ring';}),format,V03);
  refused(older(V03,a=>{a[1].padding=.02;}),format,V03);
  refused(older(V03,a=>{a[0].enter={kind:'draw',duration:.8};}),format,V03);
  refused(older(V03,a=>{a[1].leave={kind:'fade',duration:.4};}),format,V03);
  refused(older(V03,a=>{a[0].kind='callout';}),/^Invalid annotation #0 in shot pawls: kind must be arrow or label$/,V03);
  refused(()=>{},/^Annotations need format machinome-video-draft\/0\.3: shot pawls$/,V02);
});

test('rings and entrances need no newer viewer than annotations do',()=>{
  assert.deepEqual(requiredViewerApi(overlays()),{api:28,reasons:['annotations (shot pawls)']});
});

// Pins, green by design before and after (tasks 1.2): the annotated fixture of
// annotations.test.mjs, its view's model time pinned literally from the base
// 6417f97, its marks as converted; 0.3 and 0.4 give the same frames.
const annotated=()=>({format:V03,
  output:{width:1280,height:720,fps:30,durationSeconds:4},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{feed:[['Feed mechanism']],'rope-1':[['Feed mechanism','Ratchet to reduction shaft']],frame:[['Frame']]},evidence:{},
  shots:[shot('pawls',0,2,{annotations:[
      {from:.5,to:1.5,kind:'arrow',part:DRIVING,place:[.18,.22],text:'Pulls one tooth'},
      {from:0,to:2,kind:'label',part:'rope-1',offset:[.04,-.05],text:'Rope 1'}]}),
    shot('plain',2,4)]});
test('the annotated 0.3 frames, and the same fixture in 0.4, are unchanged',()=>{
  const arrow={"id":"cues[0].actions[0]","kind":"arrow","text":"Pulls one tooth","target":{"paths":[["Feed mechanism","Driving pawl"]]},"place":placeInBox([0.18,0.22],.08,box),"opacity":1,"drawn":1};
  const label={"id":"cues[1].actions[0]","kind":"label","text":"Rope 1","target":{"paths":[["Feed mechanism","Ratchet to reduction shaft"]]},"offset":offsetInBox([0.04,-0.05],.08,box),"opacity":1,"drawn":1};
  const view=(time,marks)=>({"kind":"view","time":time,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"highlight":null,"marks":marks});
  const pinned={"0.25":view(0.02787162162162162,[label]),"1":view(0.030405405405405407,[arrow,label]),"1.5":view(0.03209459459459459,[label])};
  const old=annotated(),next={...annotated(),format:V04};valid(old);valid(next);
  for(const [t,v] of Object.entries(pinned)){
    const f=yamlFrame(old,Number(t));
    assert.equal(f.shotId,'pawls');assert.deepEqual(Object.keys(f.elements),['pawls.view']);
    assert.deepEqual(element(f,'view'),v,`0.3 at ${t}`);
    assert.deepEqual(yamlFrame(next,Number(t)),f,`0.4 at ${t}`);
  }
});

// The proofs of preview (design D8) are functions of decoded images, proved here
// on small synthetic ones. Imported when run, so a missing proof fails its test only.
const image=(width,height,paint)=>{const rgb=Buffer.alloc(width*height*3);
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){const c=paint(x,y);for(let k=0;k<3;k++)rgb[(y*width+x)*3+k]=c[k];}
  return {width,height,rgb};};
const PAPER=[100,110,120],ACCENT=[191,83,31];
const blend=(a,b,w)=>a.map((v,k)=>Math.round((1-w)*v+w*b[k]));

test('the fade proof accepts the predicted blend, refuses one 9 levels off, and records identical pictures as vacuous',async()=>{
  const {proveMark}=await import('../src/pixels.mjs');
  const stroke=(x,y)=>y===4&&x>=2&&x<10;
  const without=image(12,8,()=>PAPER),full=image(12,8,(x,y)=>stroke(x,y)?ACCENT:PAPER);
  const a=ease('smooth',.5),composed=image(12,8,(x,y)=>stroke(x,y)?blend(PAPER,ACCENT,a):PAPER);
  const where='pawls #0 enter at 0.40 s';
  const passed=proveMark('enter',{composed,full,without},{where,entrance:'fade',opacity:a});
  assert.ok(passed.largestDifference<=.5);assert.equal(passed.vacuous,false);
  const off=image(12,8,(x,y)=>stroke(x,y)?blend(PAPER,ACCENT,a).map((v,k)=>k===0&&x===5?v+9:v):PAPER);
  assert.throws(()=>proveMark('leave',{composed:off,full,without},{where:'pawls #0 leave at 45.07 s',opacity:a}),
    error=>/^Annotation fade does not blend as its easing predicts: pawls #0 leave at 45\.07 s \(largest difference 9(\.\d+)? levels\)$/.test(error.message));
  const vacuous=proveMark('leave',{composed:without,full:without,without},{where,opacity:a});
  assert.deepEqual(vacuous,{largestDifference:0,vacuous:true});
});

test('the draw-on proof needs part of the stroke at the inside point and none at the outside point',async()=>{
  const {proveMark}=await import('../src/pixels.mjs');
  const where='pawls #0 enter at 0.50 s',inside={x:3,y:4},outside={x:9,y:4};
  const without=image(12,8,()=>PAPER),full=image(12,8,(x,y)=>y===4?ACCENT:PAPER);
  const half=image(12,8,(x,y)=>y===4&&x<6?ACCENT:PAPER);
  const info={where,entrance:'draw',inside,outside};
  assert.equal(proveMark('enter',{composed:half,full,without},info).vacuous,false);
  assert.throws(()=>proveMark('enter',{composed:full,full,without},info),/^Error: Annotation draw-on shows the rest of its stroke: pawls #0 enter at 0\.50 s/);
  assert.throws(()=>proveMark('enter',{composed:without,full,without},info),/^Error: Annotation draw-on shows none of its stroke: pawls #0 enter at 0\.50 s/);
  const short=image(12,8,(x,y)=>y===4&&x<8?ACCENT:PAPER);
  assert.throws(()=>proveMark('enter',{composed:half,full:short,without},info),/^Error: Annotation draw-on proof shows nothing: the complete stroke does not reach the outside point: pawls #0 enter at 0\.50 s/);
});

test('an entrance starts from nothing (or from its words alone), and ends, as an exit starts, on the mark as drawn',async()=>{
  const {proveMark}=await import('../src/pixels.mjs');
  const where='pawls #2 enter-start at 0.50 s';
  const without=image(12,8,()=>PAPER),full=image(12,8,(x,y)=>y===4||(x<3&&y<2)?ACCENT:PAPER);
  const words=image(12,8,(x,y)=>x<3&&y<2?ACCENT:PAPER),text={x:0,y:0,width:3,height:2};
  assert.equal(proveMark('enter-start',{composed:without,full,without},{where,entrance:'fade'}).largestDifference,0);
  assert.throws(()=>proveMark('enter-start',{composed:words,full,without},{where,entrance:'fade'}),/^Error: Annotation entrance does not start from nothing: pawls #2 enter-start at 0\.50 s \(largest difference \d+ levels\)$/);
  assert.equal(proveMark('enter-start',{composed:words,full,without},{where,entrance:'draw',text}).largestDifference,0);
  assert.throws(()=>proveMark('enter-start',{composed:full,full,without},{where,entrance:'draw',text}),/^Error: Annotation draw-on does not start from its words alone: pawls #2 enter-start/);
  assert.equal(proveMark('enter-end',{composed:full,full,without},{where}).largestDifference,0);
  assert.throws(()=>proveMark('enter-end',{composed:words,full,without},{where:'pawls #2 enter-end at 1.30 s'}),/^Error: Annotation entrance changes the mark it ends on: pawls #2 enter-end at 1\.30 s/);
  assert.throws(()=>proveMark('leave-start',{composed:words,full,without},{where:'pawls #3 leave-start at 1.60 s'}),/^Error: Annotation exit does not start from the mark as drawn: pawls #3 leave-start at 1\.60 s/);
});
