import {test} from 'node:test';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi} from '../src/episode.mjs';
import {frameAt} from '../src/timeline.mjs';
import {EASINGS,ease,keyedValue} from '../src/easing.mjs';
import {lens03,cues03,cuesManifest} from './frame-fixtures.mjs';

const V04='machinome-video-draft/0.4';
const manifest={animation:{loop:1460}};
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};
const as04=e=>({...e,format:V04});
// The restaged Revolutions machinome and genome shots (design D4, D5).
const shot=(id,start,end,simulation,camera,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation,camera,hiddenLayers:[],overlays:[],evidence:[],...extra});
const restaged=(format=V04)=>({format,output:{width:1280,height:720,fps:30,durationSeconds:26.5},
  model:{expectedDurationSeconds:1460,timeMode:'normalized-loop'},
  cameras:{mechanism:{position:[0,-10,4],target:[0,0,0],up:[0,0,1],fov:37},
    linkage:{position:[6,-8,2],target:[1,0,1],up:[0,0,1],fov:37},
    rolled:{position:[0,-10,4],target:[0,0,0],up:[1,0,1],fov:37}},
  layers:{},evidence:{},
  shots:[shot('machinome',0,14,{from:453,to:461,keyframes:[{at:0,seconds:453},{at:3.733,seconds:453},{at:14,seconds:461,ease:'in'}]},
      [{at:0,preset:'mechanism'}]),
    shot('genome',14,26.5,{from:461,to:466.8,keyframes:[{at:0,seconds:461},{at:6.899,seconds:466.8,ease:'out'},{at:12.5,seconds:466.8}]},
      [{at:0,preset:'mechanism'},{at:9.615,preset:'linkage',ease:'out'}])]});
const valid=e=>validateEpisode(e,manifest);
const frames=e=>Array.from({length:e.output.durationSeconds*e.output.fps},(_,i)=>i/e.output.fps);

// Amended by shot-transitions (ratified): every 0.4 frame also carries transition, null outside one.
test('a 0.4 episode without ease gives the frames of the same episode in 0.3',()=>{
  for(const [make,m] of [[()=>lens03('tight'),{animation:{loop:296}}],[()=>lens03('rolled'),{animation:{loop:296}}],[cues03,cuesManifest]]){
    const old=make(),next=as04(make());
    validateEpisode(old,m);validateEpisode(next,m);
    for(const t of frames(old))assert.deepEqual(frameAt(next,t),{...frameAt(old,t),transition:null},`at ${t}`);
  }
});

test('a camera move follows the ease of the key it ends at, position, target, field of view and up alike',()=>{
  const e=restaged();valid(e);
  // Local time as frameAt computes it: video time minus the shot's start.
  const a=e.cameras.mechanism,b=e.cameras.linkage,start=e.shots[1].start;
  for(const local of [0,.5,1,3,6,9,9.5]){
    const w=ease('out',(start+local-start)/9.615),f=frameAt(e,start+local);
    assert.deepEqual(f.view.camera,a.position.map((v,i)=>v+(b.position[i]-v)*w),`camera at ${local}`);
    assert.deepEqual(f.view.target,a.target.map((v,i)=>v+(b.target[i]-v)*w),`target at ${local}`);
    assert.equal(f.fov,a.fov+(b.fov-a.fov)*w,`fov at ${local}`);
  }
  // Already travelling at the cut: out covers far more of the move in its first second than smooth.
  assert.ok(ease('out',1/9.615)>0.25&&ease('smooth',1/9.615)<0.035);
  for(const local of [9.615,10,12.4])assert.deepEqual(frameAt(e,start+local).view,{camera:b.position,target:b.target},'the hold after the last key is exact');

  const linear=restaged();linear.shots[1].camera[1].ease='linear';valid(linear);
  const x=local=>frameAt(linear,start+local).view.camera[0];
  const steps=[1,2,3,4,5,6,7,8,9].map(s=>x(s)-x(s-1));
  for(const step of steps)assert.ok(Math.abs(step-6/9.615)<1e-12,`constant speed: ${step}`);

  const rolling=restaged();rolling.shots[1].camera[1]={at:9.615,preset:'rolled',ease:'in'};valid(rolling);
  for(const local of [0,1,4.8,8,9.615,11]){
    const w=ease('in',Math.min(1,(start+local-start)/9.615)),ua=unit([0,0,1]),ub=unit([1,0,1]);
    assert.deepEqual(frameAt(rolling,start+local).up,unit(ua.map((v,i)=>v+(ub[i]-v)*w)),`up at ${local}`);
  }
  const narrowing=restaged();narrowing.cameras.tight={...narrowing.cameras.mechanism,fov:20};
  narrowing.shots[1].camera[1]={at:9.615,preset:'tight',ease:'in'};valid(narrowing);
  for(const local of [2,5,9])assert.equal(frameAt(narrowing,start+local).fov,37+(20-37)*ease('in',(start+local-start)/9.615));
});

test('model time follows the ease of the keyframe it runs to, meets every key and never runs back',()=>{
  const e=restaged();valid(e);
  const D=e.model.expectedDurationSeconds;
  for(const s of e.shots){
    const keys=s.simulation.keyframes.map(k=>({at:k.at,value:k.seconds,ease:k.ease}));
    for(const t of frames(e).filter(t=>t>=s.start&&t<s.end))
      assert.equal(frameAt(e,t).time,keyedValue(keys,t-s.start,'linear')/D,`${s.id} at ${t}`);
    for(const k of s.simulation.keyframes)if(k.at<s.end-s.start)assert.equal(frameAt(e,s.start+k.at).time,k.seconds/D,`${s.id} key at ${k.at}`);
  }
  // Resume motion gently; settle into the pause.
  const seconds=t=>frameAt(e,t).time*D;
  assert.ok(seconds(3.733+1/30)-453<1e-3,'in leaves the hold from rest');
  assert.ok(466.8-seconds(14+6.899-1/30)<1e-3,'out arrives at rest');
  for(const name of EASINGS){
    const eased=restaged();
    for(const s of eased.shots){s.simulation.keyframes.slice(1).forEach(k=>{k.ease=name;});s.camera.slice(1).forEach(k=>{k.ease=name;});}
    valid(eased);
    let prior=-Infinity;
    for(const t of frames(eased)){
      const f=frameAt(eased,t),s=eased.shots.find(s=>s.id===f.shotId),local=t-s.start,keys=s.simulation.keyframes;
      const i=keys.findLastIndex(k=>k.at<=local),lo=keys[i].seconds/D,hi=(keys[i+1]??keys[i]).seconds/D;
      assert.ok(f.time>=prior,`${name}: model time decreases at ${t}`);
      assert.ok(f.time>=lo&&f.time<=hi,`${name}: ${f.time} leaves [${lo}, ${hi}] at ${t}`);
      for(const k of keys)if(Math.abs(local-k.at)<1e-12)assert.equal(f.time,k.seconds/D);
      prior=f.time;
    }
  }
});

const refused=(edit,pattern,format=V04)=>{
  const e=restaged(format);edit(e);
  assert.throws(()=>valid(e),error=>pattern.test(error.message),String(pattern));
};

test('ease is refused outside format 0.4, when unknown and on a first key, naming the shot',()=>{
  for(const format of ['machinome-video-draft/0.3','machinome-video-draft/0.2']){
    refused(e=>{delete e.shots[1].simulation.keyframes[1].ease;delete e.shots[1].camera[1].ease;},/^Easing needs format machinome-video-draft\/0\.4: shot machinome$/,format);
    refused(e=>{delete e.shots[0].simulation.keyframes[2].ease;delete e.shots[1].simulation.keyframes[1].ease;},/^Easing needs format machinome-video-draft\/0\.4: shot genome$/,format);
    refused(e=>{delete e.shots[0].simulation.keyframes[2].ease;delete e.shots[1].camera[1].ease;},/^Easing needs format machinome-video-draft\/0\.4: shot genome$/,format);
  }
  const plain=e=>{delete e.shots[0].simulation.keyframes[2].ease;delete e.shots[1].simulation.keyframes[1].ease;delete e.shots[1].camera[1].ease;};
  for(const format of ['machinome-video-draft/0.3','machinome-video-draft/0.2']){
    const e=restaged(format);plain(e);
    assert.doesNotThrow(()=>valid(e),`the same episode without ease is a valid ${format}`);
  }
  refused(e=>{e.shots[1].camera[1].ease='bounce';},/^Unknown easing: bounce; use linear, smooth, in, out or in-out \(camera key #1 in shot genome\)$/);
  refused(e=>{e.shots[1].simulation.keyframes[1].ease='ease-out';},/^Unknown easing: ease-out; use linear, smooth, in, out or in-out \(model keyframe #1 in shot genome\)$/);
  refused(e=>{e.shots[1].camera[1].ease='Smooth';},/Unknown easing: Smooth.*shot genome/);
  refused(e=>{e.shots[1].camera[1].ease=null;},/Unknown easing: null.*shot genome/);
  refused(e=>{e.shots[1].camera[0].ease='out';},/^Nothing to ease before the first camera key: shot genome$/);
  refused(e=>{e.shots[1].simulation.keyframes[0].ease='in';},/^Nothing to ease before the first model keyframe: shot genome$/);
});

test('in format 0.4 a shot, its simulation, its keyframes and its camera keys refuse unknown fields',()=>{
  refused(e=>{e.shots[1].camera[1].eas='out';},/^Unknown camera key field: eas \(key #1 in shot genome\)$/);
  refused(e=>{e.shots[1].simulation.keyframes[1].speed=2;},/^Unknown model keyframe field: speed \(keyframe #1 in shot genome\)$/);
  refused(e=>{e.shots[1].simulation.ease='in';},/^Unknown simulation field: ease \(shot genome\)$/);
  refused(e=>{e.shots[1].transiton={kind:'fade'};},/^Unknown shot field: transiton \(shot genome\)$/);
  const e=restaged();for(const s of e.shots)s.speechOffset=.2;
  assert.doesNotThrow(()=>valid(e),'every defined field is accepted');
  // 0.3 keeps ignoring what it does not know.
  const old=restaged('machinome-video-draft/0.3');
  for(const s of old.shots){delete s.simulation.keyframes.at(-1).ease;delete s.simulation.keyframes[1].ease;delete s.camera.at(-1).ease;}
  old.shots[1].camera[1].eas='out';old.shots[1].simulation.keyframes[1].speed=2;old.shots[1].simulation.extra=1;old.shots[1].transiton={kind:'fade'};
  assert.doesNotThrow(()=>valid(old));
});

test('0.4 means everything 0.3 means, and needs no newer viewer for easing',()=>{
  const lens=as04(lens03('tight'));
  assert.doesNotThrow(()=>validateEpisode(lens,{animation:{loop:296}}),'0.4 may change lens, never refused with the 0.2 message');
  assert.doesNotThrow(()=>validateEpisode(as04(lens03('rolled')),{animation:{loop:296}}));
  const cues=as04(cues03());validateEpisode(cues,cuesManifest);
  assert.ok(frameAt(cues,1).annotations.length===1&&frameAt(cues,1).highlight.others==='ghost');
  const next=as04(lens03('tight'));next.format='machinome-video-draft/0.5';
  assert.throws(()=>validateEpisode(next,{animation:{loop:296}}),/Unsupported episode format/);
  const eased=restaged();valid(eased);
  assert.deepEqual(requiredViewerApi(eased),{api:21,reasons:[]});
});
