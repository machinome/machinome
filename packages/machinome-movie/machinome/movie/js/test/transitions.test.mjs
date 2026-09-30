import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi} from '../src/episode.mjs';
import {frameAt,cameraAt} from '../src/timeline.mjs';
import {EASINGS,ease,endSlope} from '../src/easing.mjs';

// Five shots joined by every kind (design D1): the first a code shot fading in,
// a linear dissolve, a fade through the paper, a slide right, a wipe (default
// left) and a fade out to black on the last shot.
const manifest={animation:{loop:296},root:{name:'Mill',children:[
  {name:'Feed mechanism',children:[{name:'Driving pawl'}]},{name:'Frame'}]}};
const shot=(id,start,end,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
const joined=()=>({format:'machinome-video-draft/0.4',
  output:{width:1280,height:720,fps:30,durationSeconds:20},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
  cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},b:{position:[4,-10,2],target:[0,0,0],up:[0,0,1],fov:37}},
  layers:{frame:[['Frame']],pawl:[['Feed mechanism','Driving pawl']]},evidence:{},
  sourceCode:{drive:{file:'machine.py',lines:[1,2],text:'wheel = Wheel()\nwheel.drives(saw)'}},
  shots:[
    shot('code',0,4,{simulation:{from:8,to:12},hiddenLayers:['frame'],fadeIn:{duration:1},
      code:{snippet:'drive',typing:[{from:.5,to:3,throughLine:2}]}}),
    shot('whole',4,9,{transition:{kind:'dissolve',duration:1,ease:'linear'},
      simulation:{from:12,to:14,keyframes:[{at:0,seconds:12},{at:3,seconds:12},{at:5,seconds:14,ease:'in'}]},
      camera:[{at:0,preset:'a'},{at:5,preset:'b'}]}),
    shot('pawls',9,13,{transition:{kind:'fade',duration:1.2},simulation:{from:14,to:18},hiddenLayers:['frame'],
      camera:[{at:0,preset:'a'},{at:3,preset:'b'}],
      overlays:[{from:0,to:4,text:'Runs to the cut',position:'top'},{from:0,to:2,text:'Ends early',position:'lower-third'}],
      highlight:[{from:1,to:4,parts:['pawl'],others:'ghost'}],
      annotations:[{from:0,to:4,kind:'arrow',part:'pawl',place:[.2,.2],text:'Pawl'},{from:0,to:1,kind:'label',point:[0,0,0],text:'Early'}]}),
    shot('held',13,16,{transition:{kind:'slide',duration:.8,direction:'right'},simulation:{from:18,to:18},camera:[{at:0,preset:'b'}]}),
    shot('closing',16,20,{transition:{kind:'wipe',duration:.8},fadeOut:{duration:2,color:'#000000'},simulation:{from:18,to:22}}),
  ]});
const valid=e=>validateEpisode(e,manifest);
const D=296,fps=30;
const frames=e=>Array.from({length:e.output.durationSeconds*fps},(_,i)=>i/fps);
const plain=()=>{const e=joined();for(const s of e.shots){delete s.transition;delete s.fadeIn;delete s.fadeOut;}return e;};
const without=({transition,...rest})=>rest;
// Shot-local time is video time minus the shot's start, which is not exact in binary.
const close=(actual,expected,what)=>assert.ok(Math.abs(actual-expected)<=1e-12,`${what??''} ${actual} is not ${expected}`);

test('a 0.4 episode joining shots by every kind is valid, and the incoming timeline is untouched',()=>{
  const e=joined(),cut=plain();
  assert.doesNotThrow(()=>valid(e));valid(cut);
  for(const t of frames(e))assert.deepEqual(without(frameAt(e,t)),without(frameAt(cut,t)),`at ${t}`);
  for(const t of frames(cut))assert.equal(frameAt(cut,t).transition,null,'every 0.4 frame carries transition');
  for(const t of [1,2,5,6.5,10.5,14,17,17.9])assert.equal(frameAt(e,t).transition,null,`no transition at ${t}`);
});

test('progress follows the named easing, linear or by default smooth, and direction defaults to left',()=>{
  const e=joined();valid(e);
  const quarter=frameAt(e,4.25).transition;
  assert.equal(quarter.kind,'dissolve');assert.equal(quarter.field,'transition');
  assert.equal(quarter.progress,.25);assert.equal(quarter.shotId,'whole');assert.equal(quarter.outgoingShotId,'code');
  assert.equal(frameAt(e,4).transition.progress,0,'the first frame shows the outgoing picture alone');
  const slide=frameAt(e,13.2).transition;
  assert.equal(slide.kind,'slide');assert.equal(slide.direction,'right');
  close(slide.progress,ease('smooth',.25));close(slide.progress,.15625);
  const wipe=frameAt(e,16.2).transition;
  assert.equal(wipe.kind,'wipe');assert.equal(wipe.direction,'left');close(wipe.progress,ease('smooth',.25));
  assert.equal(frameAt(e,4.5).transition.direction,undefined,'a dissolve has no direction');
});

test('the outgoing shot continues past its end: model at its end rate, camera held, cues that ran to the end',()=>{
  const e=joined();valid(e);
  // The code shot into the dissolve: rate (12 - 8) / 4 = 1 model second per video second.
  for(const u of [0,.25,.5,.9]){
    const out=frameAt(e,4+u).transition.outgoing;
    assert.equal(out.shotId,'code');
    close(out.time,(12+1*u)/D,`model at u = ${u}`);
    assert.deepEqual(out.view,{camera:[0,-10,0],target:[0,0,0]});
    assert.equal(out.code.text,'wheel = Wheel()\nwheel.drives(saw)');assert.equal(out.code.cursor,false);
    assert.deepEqual(out.hidden,[['Frame']]);
    assert.equal(out.transition,null,'the outgoing frame is a plain frame');
  }
  // The shot eased in to its end runs on at three times its last segment's average rate (ratification).
  const fading=frameAt(e,9.3).transition;
  assert.equal(fading.outgoingShotId,'whole');
  close(fading.outgoing.time,(14+3*1*.3)/D,'in: slope 3');
  assert.deepEqual(fading.outgoing.view,{camera:[4,-10,2],target:[0,0,0]},'the camera holds its last key');
  // The overlay, highlight and arrow that run to the end stay; the earlier ones do not.
  const out=frameAt(e,13.4).transition.outgoing;
  assert.equal(out.shotId,'pawls');close(out.time,(18+.4)/D);
  assert.deepEqual(out.overlays.map(o=>o.text),['Runs to the cut']);
  assert.deepEqual(out.highlight,{paths:[['Feed mechanism','Driving pawl']],others:'ghost',color:'#bf531f'});
  assert.deepEqual(out.annotations.map(a=>a.text),['Pawl']);
  assert.deepEqual(out.hidden,[['Frame']]);
  assert.deepEqual(out.view,cameraAt(e,e.shots[2],4).view);
  assert.equal(out.code,null);
  // A held shot stays held.
  for(const u of [0,.3,.7])assert.equal(frameAt(e,16+u).transition.outgoing.time,18/D);
  // An outgoing shot eased out to rest, or smoothly, holds.
  for(const name of ['out','smooth','in-out']){
    const eased=joined();eased.shots[1].simulation.keyframes[2].ease=name;valid(eased);
    assert.equal(frameAt(eased,9.3).transition.outgoing.time,14/D,name);
  }
});

test('fades: through the colour between shots, in from it at the head and out to it at the tail',()=>{
  const e=joined();valid(e);
  const at=t=>frameAt(e,t).transition;
  // Between shots: the plate rises over the outgoing picture to the plain colour at the midpoint.
  assert.equal(at(9).plate,0);assert.equal(at(9).picture,'outgoing');assert.equal(at(9).color,'#faf7ef','default: style.background');
  close(at(9.3).plate,ease('smooth',.5));assert.equal(at(9.3).picture,'outgoing');
  let prior=-1;
  for(let i=0;i<18;i++){const x=at(9+i/fps);assert.equal(x.picture,'outgoing');assert.ok(x.plate>prior);prior=x.plate;}
  const middle=at(9.6);
  assert.equal(middle.plate,1);assert.equal(middle.picture,'incoming');assert.equal(middle.outgoing,null);
  prior=2;
  for(let i=18;i<36;i++){const x=at(9+i/fps);assert.equal(x.picture,'incoming');assert.ok(x.plate<prior);prior=x.plate;}
  close(at(9.9).plate,1-ease('smooth',.5));
  assert.equal(frameAt(e,10.2).transition,null);
  // Head: exactly the colour on the first frame, gone at its end.
  assert.equal(at(0).plate,1);assert.equal(at(0).field,'fadeIn');assert.equal(at(0).kind,'fade');assert.equal(at(0).color,'#faf7ef');
  close(at(.5).plate,1-ease('smooth',.5));
  assert.ok(at(1-1/fps).plate<.01);
  assert.equal(frameAt(e,1).transition,null);
  // Tail: nothing at its start, exactly the colour on the film's last frame.
  assert.equal(at(18).plate,0);assert.equal(at(18).field,'fadeOut');assert.equal(at(18).color,'#000000');
  assert.equal(at(20-1/fps).plate,1);
  assert.ok(at(19).plate>0&&at(19).plate<1);
  assert.equal(at(18).picture,'incoming');assert.equal(at(18).outgoing,null);
});

const refused=(edit,pattern,format)=>{
  const e=joined();if(format)e.format=format;edit(e);
  assert.throws(()=>valid(e),error=>pattern.test(error.message),String(pattern));
};
const [code,whole,pawls,held,closing]=[0,1,2,3,4];

test('invalid transitions are refused before rendering, naming the shot',()=>{
  // Older formats: without the 0.4 keyframe ease (and, for 0.2, the 0.3 cues) the episode is otherwise valid.
  for(const format of ['machinome-video-draft/0.3','machinome-video-draft/0.2']){
    const older=edit=>e=>{delete e.shots[whole].simulation.keyframes[2].ease;
      if(format.endsWith('0.2'))for(const s of e.shots){delete s.highlight;delete s.annotations;}edit(e);};
    refused(older(()=>{}),/^Transitions need format machinome-video-draft\/0\.4: shot code$/,format);
    refused(older(e=>{delete e.shots[code].fadeIn;}),/^Transitions need format machinome-video-draft\/0\.4: shot whole$/,format);
    refused(older(e=>{for(const s of e.shots){delete s.transition;delete s.fadeIn;}}),/^Transitions need format machinome-video-draft\/0\.4: shot closing$/,format);
    const e=joined();e.format=format;older(e=>{for(const s of e.shots){delete s.transition;delete s.fadeIn;delete s.fadeOut;}})(e);
    assert.doesNotThrow(()=>valid(e),`the same episode without transitions is a valid ${format}`);
  }
  refused(e=>{e.shots[whole].transition={kind:'dissolve',durration:1};},/^Unknown transition field: durration \(transition in shot whole\)$/);
  refused(e=>{e.shots[code].fadeIn.ease='smooth';e.shots[code].fadeIn.kind='fade';},/^Unknown fadeIn field: kind \(fadeIn in shot code\)$/);
  refused(e=>{e.shots[closing].fadeOut.direction='left';},/^Unknown fadeOut field: direction \(fadeOut in shot closing\)$/);
  refused(e=>{e.shots[whole].transition='dissolve';},/^Invalid transition in shot whole: expected a mapping$/);
  refused(e=>{e.shots[whole].transition.kind='cut';},/^Invalid transition in shot whole: kind must be fade, dissolve, wipe or slide; omit transition for a cut$/);
  refused(e=>{e.shots[held].transition.direction='up';},/^Invalid transition in shot held: direction must be left or right$/);
  refused(e=>{e.shots[whole].transition.ease='bounce';},/^Unknown easing: bounce; use linear, smooth, in, out or in-out \(transition in shot whole\)$/);
  refused(e=>{e.shots[closing].fadeOut.ease='ease-out';},/^Unknown easing: ease-out; use linear, smooth, in, out or in-out \(fadeOut in shot closing\)$/);
  refused(e=>{e.shots[whole].transition.direction='left';},/^Invalid transition in shot whole: direction belongs to a wipe or slide$/);
  refused(e=>{e.shots[pawls].transition.direction='left';},/^Invalid transition in shot pawls: direction belongs to a wipe or slide$/);
  refused(e=>{e.shots[closing].transition.color='#000000';},/^Invalid transition in shot closing: color belongs to a fade$/);
  refused(e=>{e.shots[pawls].transition.color='black';},/^Invalid transition in shot pawls: color must be a quoted #rrggbb$/);
  refused(e=>{e.shots[closing].fadeOut.color='#00000';},/^Invalid fadeOut in shot closing: color must be a quoted #rrggbb$/);
  refused(e=>{e.style.background='cream';},/^Invalid fadeIn in shot code: the default colour style\.background must be a quoted #rrggbb$/);
  refused(e=>{e.style.background='cream';delete e.shots[code].fadeIn;},/^Invalid transition in shot pawls: the default colour style\.background must be a quoted #rrggbb$/);
  refused(e=>{e.shots[whole].transition.duration=1/30;},/^Invalid transition in shot whole: duration must be at least two frames \(0\.067 s at 30 fps\)$/);
  refused(e=>{e.shots[whole].transition.duration=Infinity;},/^Invalid transition in shot whole: duration must be at least two frames/);
  refused(e=>{delete e.shots[whole].transition.duration;},/^Invalid transition in shot whole: duration must be at least two frames/);
  refused(e=>{e.shots[code].fadeIn.duration=0;},/^Invalid fadeIn in shot code: duration must be at least two frames/);
  refused(e=>{e.shots[whole].transition.duration=4.5;},/^Invalid transition in shot whole: 4\.5 s is longer than shot code \(4 s\)$/);
  refused(e=>{e.shots[held].transition.duration=3.5;},/^Invalid transition in shot held: 3\.5 s is longer than shot held \(3 s\)$/);
  refused(e=>{e.shots[code].fadeIn.duration=4.5;},/^Invalid fadeIn in shot code: 4\.5 s is longer than shot code \(4 s\)$/);
  refused(e=>{e.shots[closing].fadeOut.duration=5;},/^Invalid fadeOut in shot closing: 5 s is longer than shot closing \(4 s\)$/);
  refused(e=>{e.shots[code].transition={kind:'dissolve',duration:1};},/^Invalid transition in shot code: the first shot comes in from nothing; use fadeIn$/);
  refused(e=>{e.shots[whole].fadeIn={duration:1};},/^Invalid fadeIn in shot whole: only the first shot fades in; give this shot a transition of kind fade$/);
  refused(e=>{e.shots[held].fadeOut={duration:1};},/^Invalid fadeOut in shot held: only the last shot fades out; give the next shot a transition of kind fade$/);
  refused(e=>{e.shots[closing].fadeOut.duration=3.5;},/^Transitions overlap in shot closing: 0\.8 s in and 3\.5 s out exceed its 4 s$/);
  refused(e=>{e.shots.splice(1);e.shots[0].end=20;e.shots[0].simulation={from:8,to:28};e.shots[0].fadeIn.duration=12;e.shots[0].fadeOut={duration:9};},
    /^Transitions overlap in shot code: 12 s in and 9 s out exceed its 20 s$/);
});

test('an outgoing model that would run past the export is refused; a held one at its end is not',()=>{
  refused(e=>{e.shots[code].simulation={from:291.5,to:295.5};},
    /^Shot code cannot continue 1 s into the dissolve to shot whole: its model would reach 296\.50 s, past the export's 296 s; end its simulation earlier or shorten the transition$/);
  // A fade shows the outgoing shot for half its duration; the in-eased end runs at three times the average.
  refused(e=>{e.shots[whole].simulation={from:292,to:296,keyframes:[{at:0,seconds:292},{at:3,seconds:292},{at:5,seconds:296,ease:'in'}]};},
    /^Shot whole cannot continue 0\.6 s into the fade to shot pawls: its model would reach 299\.60 s, past the export's 296 s; end its simulation earlier or shorten the transition$/);
  for(const edit of [
    e=>{e.shots[code].simulation={from:296,to:296};},
    e=>{e.shots[whole].simulation={from:292,to:296,keyframes:[{at:0,seconds:292},{at:3,seconds:292},{at:5,seconds:296,ease:'out'}]};},
    e=>{e.shots[held].simulation={from:296,to:296};},
    e=>{e.shots[closing].simulation={from:292,to:296};},
  ]){const e=joined();edit(e);assert.doesNotThrow(()=>valid(e));}
  const e=joined();e.shots[code].simulation={from:296,to:296};valid(e);
  assert.equal(frameAt(e,4.5).transition.outgoing.time,1,'held at the export end');
});

test('transitions raise no viewer requirement',()=>{
  const e=joined(),cut=plain();
  assert.deepEqual(requiredViewerApi(e),requiredViewerApi(cut));
  const bare=joined();for(const s of bare.shots){delete s.highlight;delete s.annotations;}
  assert.deepEqual(requiredViewerApi(bare),{api:21,reasons:[]});
});

test('the end slope of each curve is its derivative at the key, in average rates',()=>{
  const h=1e-6;
  for(const name of EASINGS)assert.ok(Math.abs((1-ease(name,1-h))/h-endSlope(name))<1e-5,name);
  assert.throws(()=>endSlope('bounce'),/Unknown easing: bounce/);
});
