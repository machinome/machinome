import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi} from '../src/episode.mjs';
import {frameAt} from '../src/timeline.mjs';

const manifest={animation:{loop:296}};
const shot=(id,start,end,camera)=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera,hiddenLayers:[],overlays:[],evidence:[]});
const moving=()=>({format:'machinome-video-draft/0.3',
  output:{width:1280,height:720,fps:30,durationSeconds:5},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  cameras:{wide:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37},
    tight:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:20},
    rolled:{position:[0,-10,0],target:[0,0,0],up:[1,0,1],fov:37},
    flipped:{position:[0,-10,0],target:[0,0,0],up:[0,0,-1],fov:37},
    along:{position:[0,-10,0],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{},evidence:{},
  shots:[shot('narrow',0,3,[{at:0,preset:'wide'},{at:2,preset:'tight'}]),shot('hold',3,5,[{at:0,preset:'tight'}])]});
const close=(a,b)=>a.every((v,i)=>Math.abs(v-b[i])<1e-12);
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};

test('field of view eases between presets and holds after the last key',()=>{
  const e=moving();validateEpisode(e,manifest);
  assert.equal(frameAt(e,1).fov,28.5);
  assert.equal(frameAt(e,.5).fov,37-17*.15625);
  assert.equal(frameAt(e,2.5).fov,20);
  assert.deepEqual(frameAt(e,1).view,{camera:[0,-10,0],target:[0,0,0]});
});

test('up interpolates by direction and is always a unit vector',()=>{
  const e=moving();e.shots[0].camera[1].preset='rolled';validateEpisode(e,manifest);
  assert.ok(close(frameAt(e,0).up,[0,0,1]));
  assert.ok(close(frameAt(e,2).up,unit([1,0,1])));
  const ease=.5,mid=unit([0+(Math.SQRT1_2-0)*ease,0,1+(Math.SQRT1_2-1)*ease]);
  assert.ok(close(frameAt(e,1).up,mid));
  for(const t of [.2,.7,1.3,1.9])assert.ok(Math.abs(Math.hypot(...frameAt(e,t).up)-1)<1e-12);
});

test('impossible or unsupported camera moves are refused, naming the shot',()=>{
  let e=moving();e.format='machinome-video-draft/0.2';
  assert.throws(()=>validateEpisode(e,manifest),/Changing FOV\/up within a shot is not supported: shot narrow; use format machinome-video-draft\/0\.3 with Viewer API 28/);
  e=moving();e.shots[0].camera[1].preset='flipped';
  assert.throws(()=>validateEpisode(e,manifest),/Camera up reverses between keys in shot narrow; add an intermediate preset/);
  e=moving();e.shots[0].camera[1].preset='along';
  assert.throws(()=>validateEpisode(e,manifest),/Camera up lies along the view direction in shot narrow at 1\.90 s/);
});

test('any change of up or field of view requires Viewer API 28, within a shot or across a cut',()=>{
  assert.deepEqual(requiredViewerApi(moving()),{api:28,reasons:['camera up/field of view (shot narrow)','camera up/field of view (shot hold)']});
  const cut=moving();cut.format='machinome-video-draft/0.2';cut.shots[0].camera=[{at:0,preset:'wide'}];
  assert.deepEqual(requiredViewerApi(cut),{api:28,reasons:['camera up/field of view (shot hold)']});
  const same=moving();same.shots[0].camera=[{at:0,preset:'wide'}];same.shots[1].camera=[{at:0,preset:'wide'}];
  assert.deepEqual(requiredViewerApi(same),{api:21,reasons:[]});
});
