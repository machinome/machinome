// Layer 3 (pure): the reframe, a join that moves a view's box and fades the
// rest (the reframe-join change, ADR-010). Its frame is the incoming shot's,
// live, with the moving view's box between its two slots' measured boxes by
// the eased progress; the boxes come from a measured layout. Inline resolved
// fixtures only: no file, no DOM, no browser.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {frameAt,joinShows,movingViews,reframeAt} from '../src/timeline.mjs';
import {reframeBoxes,reframesOf} from '../src/layout.mjs';
import {ease} from '../src/easing.mjs';

const close=(actual,expected,what='')=>{
  if(Array.isArray(expected))return expected.forEach((v,i)=>close(actual[i],v,`${what}[${i}]`));
  assert.ok(Math.abs(actual-expected)<1e-12,`${what} ${actual} is not ${expected}`);
};
const CAMERAS={a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},
  b:{position:[10,-10,0],target:[0,0,2],up:[0,0,1],fov:20}};
const TEXT='wheel.drives(saw)\nsaw.cuts(wheel)';
const shot=(id,until,more)=>({id,until,cues:[],...more});
const FROM=[0,0,1,1],TO=[.5,.1,.4,.8];
// One chapter at 10 fps: `whole` [0, 2) draws the view in the frame's
// `stage` and a title; `halves` [2, 5) comes in by a one-second reframe and
// places the view in `right`, the source in `left` and the card in `aside`,
// its view moving to camera b from 0 to 2 s and its source typing.
function film({reframes=true,join={kind:'reframe',duration:1},layout=null}={}){
  const doc={format:'machinome-movie/0.2',resolved:true,id:'inline',title:'Inline',output:{width:320,height:180,fps:10},
    model:{expectedDurationSeconds:20},style:{},cameras:structuredClone(CAMERAS),layers:{},
    sourceCode:{drive:{file:'m.py',lines:[10,11]}},stills:{},clips:{},stage:{modules:[],elements:{},sets:{}},
    chapters:[{id:'drive',narration:'x',speechOffset:.2,elements:{
      view:{kind:'view',camera:'a'},code:{kind:'source',source:'drive'},
      card:{kind:'tally',props:{items:['A','B']}},head:{kind:'title',text:'Whole'}},shots:[
      shot('whole',2,{set:'frame',places:{stage:'view',top:'head'},model:{from:0,to:2},
        cues:[{at:0,until:2,actions:[{element:'head',action:'show'}]}]}),
      shot('halves',3,{set:'split',places:{left:'code',right:'view',aside:'card'},model:{from:2,to:5},
        ...(join?{transition:join}:{}),cues:[
        {at:0,actions:[{element:'view',action:'move',camera:'b',until:2}]},
        {at:0,actions:[{element:'code',action:'type',throughLine:11,over:1}]},
        {at:0,until:3,actions:[{element:'card',action:'light',params:{item:'A'}}]}]})]}]};
  let clock=0;
  for(const chapter of doc.chapters){
    chapter.start=clock;
    for(const s of chapter.shots){s.start=clock;s.end=clock+s.until;clock=s.end;}
    chapter.end=clock;
  }
  doc.output.durationSeconds=clock;
  doc.excerpts={drive:{file:'m.py',lines:[10,11],text:TEXT}};
  doc.pictureMedia={stills:{},clips:{}};
  if(reframes)doc.reframes=layout?reframeBoxes(doc,layout):
    {halves:{'drive.view':{from:{set:'frame',slot:'stage',box:FROM},to:{set:'split',slot:'right',box:TO}}}};
  return doc;
}
// The same film cut without a join: what the incoming shot's timeline gives.
const plain=()=>film({join:null});

test('a reframe draws the incoming shot live: its set, slots and elements, and nothing of the outgoing shot',()=>{
  const movie=film();
  for(const t of [2,2.3,2.5,2.9]){
    const f=frameAt(movie,t),g=frameAt(plain(),t);
    assert.equal(f.shotId,'halves');assert.equal(f.set,'split');
    assert.deepEqual(f.slots,{left:'drive.code',right:'drive.view',aside:'drive.card'});
    assert.deepEqual(Object.keys(f.elements).sort(),['drive.card','drive.code','drive.view'],'the outgoing title is not drawn');
    // Every element's state is exactly the incoming timeline's: the view's
    // camera, lens and model time, a move running under the join included.
    assert.deepEqual(f.elements,g.elements,`the elements at ${t} s`);
    const x=f.transition;
    assert.equal(x.kind,'reframe');assert.equal(x.field,'transition');assert.equal(x.shotId,'halves');
    assert.equal(x.outgoingShotId,'whole');assert.equal(x.start,2);assert.equal(x.duration,1);assert.equal(x.ease,'smooth');
    assert.equal(x.outgoing,null,'nothing of the outgoing shot is posed');
    assert.deepEqual(Object.keys(x.boxes),['drive.view']);
  }
  const moving=frameAt(movie,2.5).elements['drive.view'].view.camera;
  assert.ok(moving.some((v,i)=>v!==CAMERAS.a.position[i])&&moving.some((v,i)=>v!==CAMERAS.b.position[i]),'the move runs under the join');
  assert.equal(frameAt(movie,3).transition,null,'the join ends after its duration');
  assert.equal(frameAt(movie,1.9).transition,null,'and the outgoing shot is cut, not continued');
});

test('the moving view\'s box runs from its outgoing slot\'s box to its incoming slot\'s by the eased progress',()=>{
  const movie=film();
  const first=frameAt(movie,2).transition;
  assert.equal(first.progress,0);
  assert.deepEqual(first.boxes['drive.view'],FROM,'exactly the outgoing slot at progress 0');
  for(const u of [.1,.25,.5,.75,.9]){
    const x=frameAt(movie,2+u).transition,p=ease('smooth',u);
    close(x.progress,p,`progress at ${u}`);
    close(x.boxes['drive.view'],FROM.map((v,i)=>(1-p)*v+p*TO[i]),`box at ${u}`);
  }
  // The join at its end, as the proofs pose it: exactly the incoming slot.
  const end=reframeAt(movie,'halves',1);
  assert.equal(end.progress,1);assert.deepEqual(end.boxes['drive.view'],TO);
  assert.deepEqual(reframeAt(movie,'halves',5).boxes['drive.view'],TO,'clamped to the join');
  // An easing of the vocabulary, linear here.
  const linear=film({join:{kind:'reframe',duration:1,ease:'linear'}});
  close(frameAt(linear,2.3).transition.progress,.3);
  assert.equal(frameAt(linear,2.3).transition.ease,'linear');
});

test('a reframe frame is a pure function of video time',()=>{
  const movie=film(),a=frameAt(movie,2.4);
  frameAt(movie,4.2);frameAt(movie,.5);
  assert.deepEqual(frameAt(movie,2.4),a);
  assert.deepEqual(frameAt(film(),2.4),a,'and of the document: a fresh copy gives the same frame');
});

test('a reframe whose boxes were not measured is refused naming the shot; no box is guessed',()=>{
  const movie=film({reframes:false});
  assert.throws(()=>frameAt(movie,2.5),/^Error: Shot halves comes in by a reframe whose slot boxes are not measured/);
  assert.equal(frameAt(movie,3.5).transition,null,'frames after the join need no boxes');
  assert.throws(()=>reframeAt(movie,'whole',0),/Shot whole does not come in by a reframe/);
});

test('a join shows its outgoing shot for half a fade, a whole dissolve, wipe or slide, and none of a reframe',()=>{
  assert.equal(joinShows({kind:'fade',duration:1}),.5);
  for(const kind of ['dissolve','wipe','slide'])assert.equal(joinShows({kind,duration:.8}),.8);
  assert.equal(joinShows({kind:'reframe',duration:.8}),0);
  assert.equal(joinShows(undefined),0);
});

test('the views a reframe moves are those both shots place, in one chapter',()=>{
  const movie=film(),[chapter]=movie.chapters,[whole,halves]=chapter.shots;
  assert.deepEqual(movingViews(chapter,whole,chapter,halves),
    [{key:'drive.view',element:'view',from:{set:'frame',slot:'stage'},to:{set:'split',slot:'right'}}]);
  assert.deepEqual(movingViews({id:'other'},whole,chapter,halves),[],'a view belongs to its chapter');
  assert.deepEqual(movingViews(chapter,{...whole,places:{top:'head'}},chapter,halves),[]);
});

// A measured layout as check and the sessions measure it: pixels at the
// page's size, each slot's box, a picture's box and whether it stays put.
const LAYOUT={width:1280,height:720,sets:{
  frame:[{slot:'stage',box:[0,0,1280,720],picture:[0,0,1280,720],fixed:true},
    {slot:'top',box:[0,0,1280,40],picture:[0,0,1280,40],fixed:false}],
  split:[{slot:'left',box:[64,72,512,576],picture:[64,72,512,576],fixed:true},
    {slot:'right',box:[640,72,512,576],picture:[640,72,512,576],fixed:true},
    {slot:'aside',box:[0,0,10,10],picture:[0,0,10,10],fixed:true}]}};

test('the boxes come from the measured layout, as fractions of the frame',()=>{
  const movie=film({layout:LAYOUT});
  assert.deepEqual(movie.reframes,{halves:{'drive.view':{
    from:{set:'frame',slot:'stage',box:[0,0,1,1]},to:{set:'split',slot:'right',box:[.5,.1,.4,.8]}}}});
  assert.deepEqual(reframesOf(movie).map(r=>[r.shot.id,r.outgoing.id,r.views.map(v=>v.key)]),[['halves','whole',['drive.view']]]);
  assert.deepEqual([...new Set(reframesOf(movie).flatMap(r=>r.views.flatMap(v=>[v.from.set,v.to.set])))],['frame','split']);
  assert.deepEqual(reframeBoxes(plain(),LAYOUT),{},'a film without a reframe has none');
});

test('a reframe slot sized by what it holds is refused naming the shot, the view, the set and the slot',()=>{
  const layout=structuredClone(LAYOUT);layout.sets.split[1].fixed=false;
  assert.throws(()=>film({layout}),
    /^Error: Shot halves comes in by a reframe that moves drive\.view into slot right of set split, which is sized by what it holds/);
  const outgoing=structuredClone(LAYOUT);outgoing.sets.frame[0].fixed=false;
  assert.throws(()=>film({layout:outgoing}),/moves drive\.view out of slot stage of set frame, which is sized by what it holds/);
  const missing=structuredClone(LAYOUT);delete missing.sets.split;
  assert.throws(()=>film({layout:missing}),/Shot halves comes in by a reframe into set split, whose layout was not measured/);
});
