import {test} from 'node:test';
import assert from 'node:assert/strict';
import {parseSource, validateEpisode} from '../src/episode.mjs';
import {frameAt, captionsFromAlignment} from '../src/timeline.mjs';
import {base02,order02,lens03,cues03,cuesManifest} from './frame-fixtures.mjs';

const fixture = () => ({output:{width:1280,height:720,fps:30,durationSeconds:4},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37},
    b:{position:[10,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{frame:[['Frame']]}, evidence:{},
  shots:[{id:'first',start:0,end:2,narration:'One.',direction:'Look.',
    simulation:{from:8,to:12},camera:[{at:0,preset:'a'},{at:2,preset:'b'}],
    hiddenLayers:['frame'],overlays:[],evidence:[]},
    {id:'second',start:2,end:4,narration:'Two.',direction:'Look again.',
      simulation:{from:12,to:12},camera:[{at:0,preset:'b'}],hiddenLayers:[],overlays:[],evidence:[]}]});
test('YAML refuses duplicates, tags, aliases and non-string keys',()=>{
  for(const source of ['x: 1\nx: 2', 'x: !custom hi','x: &a [1]\ny: *a','1: value','x: {<<: {a: 1}}'])
    assert.throws(()=>parseSource(source));
  assert.equal(parseSource('narration: >-\n  Hello\n  world').narration,'Hello world');
});
test('stale model duration, gaps and unknown layers fail before rendering',()=>{
  const e=fixture();
  assert.throws(()=>validateEpisode(e,{animation:{loop:108}}),/duration/);
  e.shots[1].start=3;
  assert.throws(()=>validateEpisode(e,{animation:{loop:296}}),/contiguous/);
  e.shots[1].start=2;e.shots[0].hiddenLayers=['missing'];
  assert.throws(()=>validateEpisode(e,{animation:{loop:296}}),/layer/);
});
test('video clock maps to model seconds, camera interpolates and cuts restore visibility',()=>{
  const e=fixture();
  const middle=frameAt(e,1);
  assert.equal(middle.time,10/296);
  assert.deepEqual(middle.view.camera,[5,0,10]);
  assert.deepEqual(middle.hidden,[['Frame']]);
  const boundary=frameAt(e,2);
  assert.equal(boundary.shotId,'second');
  assert.deepEqual(boundary.hidden,[]);
  assert.equal(frameAt(e,3).time,12/296);
  assert.throws(()=>frameAt(e,4),/outside/);
});
test('captions follow supplied speech timestamps, not guessed reading speed',()=>{
  const alignment={characters:[...'Hi all.'],character_start_times_seconds:[0,.1,.2,1,1.1,1.2,1.3],
    character_end_times_seconds:[.1,.2,.3,1.1,1.2,1.3,1.4]};
  const cues=captionsFromAlignment(alignment,10);
  assert.equal(cues[0].start,10);assert.equal(cues[0].end,11.4);
  assert.equal(cues[0].text,'Hi all.');
});
test('model keyframes synchronize stroke boundaries with spoken cues',()=>{
  const e=fixture();e.shots[0].simulation.keyframes=[{at:0,seconds:8},{at:1.5,seconds:10},{at:2,seconds:12}];
  assert.equal(frameAt(e,1.5).time,10/296);
  assert.equal(frameAt(e,1.75).time,11/296);
});
test('0.2 episodes are unchanged',()=>{
  // Pinned literally from the pre-annotation timeline (b32ef53).
  const pinned={
    0:{shotId:'first',time:0.02702702702702703,view:{camera:[0,0,10],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[['Frame']],overlays:[],code:null},
    1:{shotId:'first',time:0.033783783783783786,view:{camera:[5,0,10],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[['Frame']],overlays:[],code:null},
    2:{shotId:'second',time:0.04054054054054054,view:{camera:[10,0,10],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[],overlays:[],code:null},
    3:{shotId:'second',time:0.04054054054054054,view:{camera:[10,0,10],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[],overlays:[],code:null}};
  for(const format of [undefined,'machinome-video-draft/0.2']){
    const e=fixture();if(format)e.format=format;
    validateEpisode(e,{animation:{loop:296}});
    for(const [t,frame] of Object.entries(pinned))assert.deepEqual(frameAt(e,Number(t)),frame);
  }
  const e=fixture();e.format='machinome-video-draft/0.2';
  e.shots[1].annotations=[{from:0,to:1,kind:'label',point:[0,0,0],text:'Here'}];
  assert.throws(()=>validateEpisode(e,{animation:{loop:296}}),/Annotations need format machinome-video-draft\/0\.3: shot second/);
});
test('constant up and field of view are unchanged',()=>{
  // Pinned literally before the move-up-and-field-of-view change (fbc95a4).
  const view=camera=>({camera,target:[0,0,0]});
  const first={shotId:'first',up:[0,1,0],fov:37,hidden:[['Frame']],overlays:[],code:null};
  const second={shotId:'second',up:[0,1,0],fov:37,hidden:[],overlays:[],code:null};
  const pinned={
    0:{...first,time:0.02702702702702703,view:view([0,0,10])},
    0.5:{...first,time:0.030405405405405407,view:view([1.5625,0,10])},
    1:{...first,time:0.033783783783783786,view:view([5,0,10])},
    1.5:{...first,time:0.037162162162162164,view:view([8.4375,0,10])},
    2:{...second,time:0.04054054054054054,view:view([10,0,10])},
    3:{...second,time:0.04054054054054054,view:view([10,0,10])}};
  const e=fixture();
  for(const [t,frame] of Object.entries(pinned))assert.deepEqual(frameAt(e,Number(t)),frame);
});
test('0.2 and 0.3 frames are unchanged',()=>{
  // Whole frameAt objects pinned literally from the timeline before
  // keyframes-and-easing (base 37b2e56, src/ as 835cf35). order02 at 240/30 = 8 s
  // is an instant where multiply-first and divide-first linear orders differ.
  const pinned={
    base02:{
      "0":{"shotId":"first","time":0.02702702702702703,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[["Frame"]],"overlays":[],"code":null},
      "1":{"shotId":"first","time":0.031531531531531536,"view":{"camera":[5,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[["Frame"]],"overlays":[],"code":null},
      "3":{"shotId":"second","time":0.04054054054054054,"view":{"camera":[10,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null},
      "0.5":{"shotId":"first","time":0.02927927927927928,"view":{"camera":[1.5625,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[["Frame"]],"overlays":[],"code":null},
      "1.5":{"shotId":"first","time":0.033783783783783786,"view":{"camera":[8.4375,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[["Frame"]],"overlays":[],"code":null},
      "1.75":{"shotId":"first","time":0.037162162162162164,"view":{"camera":[9.5703125,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[["Frame"]],"overlays":[],"code":null}},
    order02:{
      "238":{"shotId":"stroke","time":0.6028415042949927,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null},
      "239":{"shotId":"stroke","time":0.6031217263775404,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null},
      "240":{"shotId":"stroke","time":0.603401948460088,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null},
      "241":{"shotId":"stroke","time":0.6036821705426356,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null},
      "242":{"shotId":"stroke","time":0.6039623926251833,"view":{"camera":[0,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null}},
    lens03Tight:{
      "1":{"shotId":"narrow","time":0.030405405405405407,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":28.5,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "0.2":{"shotId":"narrow","time":0.0277027027027027,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":36.524,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "0.5":{"shotId":"narrow","time":0.028716216216216218,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":34.34375,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "1.3":{"shotId":"narrow","time":0.031418918918918924,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":24.789749999999998,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "1.9":{"shotId":"narrow","time":0.033445945945945944,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":20.12325,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "2.5":{"shotId":"narrow","time":0.03547297297297297,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0,0,1],"fov":20,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null}},
    lens03Rolled:{
      "1":{"shotId":"narrow","time":0.030405405405405407,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.3826834323650897,0,0.9238795325112867],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "0.2":{"shotId":"narrow","time":0.0277027027027027,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.019958727736856283,0,0.99980080475419],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "0.5":{"shotId":"narrow","time":0.028716216216216218,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.11501586620387408,0,0.9933636547213576],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "1.3":{"shotId":"narrow","time":0.031418918918918924,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.5409539174957836,0,0.8410522333041895],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "1.9":{"shotId":"narrow","time":0.033445945945945944,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.703464783916434,0,0.7107301160000219],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null},
      "2.5":{"shotId":"narrow","time":0.03547297297297297,"view":{"camera":[0,-10,0],"target":[0,0,0]},"up":[0.7071067811865475,0,0.7071067811865475],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[],"highlight":null}},
    cues03:{
      "1":{"shotId":"pawls","time":0.030405405405405407,"view":{"camera":[2,0,10],"target":[0,0,0]},"up":[0,1,0],"fov":37,"hidden":[],"overlays":[],"code":null,"annotations":[{"index":0,"kind":"arrow","text":"Pulls one tooth","target":{"paths":[["Feed mechanism","Driving pawl"]]},"place":[0.18,0.22],"safeInset":0.08}],"highlight":{"paths":[["Feed mechanism","Driving pawl"],["Feed mechanism","Holding pawl"]],"others":"ghost","color":"#bf531f"}}}
  };
  const check=(e,pins,t=Number,m={animation:{loop:296}})=>{
    validateEpisode(e,m);
    for(const [k,frame] of Object.entries(pins))assert.deepEqual(frameAt(e,t(k)),frame,`${e.shots[0].id} at ${k}`);
  };
  for(const format of [undefined,'machinome-video-draft/0.2']){const e=base02();if(format)e.format=format;check(e,pinned.base02);}
  check(order02(),pinned.order02,k=>Number(k)/30);
  check(lens03('tight'),pinned.lens03Tight);
  check(lens03('rolled'),pinned.lens03Rolled);
  check(cues03(),pinned.cues03,Number,cuesManifest);
});
