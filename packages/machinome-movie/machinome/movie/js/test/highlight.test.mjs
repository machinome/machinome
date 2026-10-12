import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi} from '../src/episode.mjs';
import {viewAt} from './frame-fixtures.mjs';

const manifest={animation:{loop:296},root:{name:'Mill',children:[
  {name:'Feed mechanism',children:[{name:'Driving pawl'},{name:'Holding pawl'},{name:'Ratchet'}]},{name:'Frame'}]}};
const shot=(id,start,end,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
const highlighted=()=>({format:'machinome-video-draft/0.3',
  output:{width:1280,height:720,fps:30,durationSeconds:6},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{feed:[['Feed mechanism']],frame:[['Frame']],pawls:[['Feed mechanism','Driving pawl'],['Feed mechanism','Holding pawl']]},evidence:{},
  shots:[shot('pawls',0,4,{highlight:[
      {from:0,to:2,parts:['pawls',['Feed mechanism','Ratchet']],others:'ghost'},
      {from:2,to:3,parts:[['Feed mechanism','Holding pawl']],color:'#237c86'}]}),
    shot('after',4,6)]});
const valid=e=>validateEpisode(e,manifest);

test('the active highlight is emitted with explicit others and colour, and ends at its cue or cut',()=>{
  const e=highlighted();valid(e);
  assert.deepEqual(viewAt(e,1).highlight,{paths:[['Feed mechanism','Driving pawl'],['Feed mechanism','Holding pawl'],['Feed mechanism','Ratchet']],others:'ghost',color:'#bf531f'});
  assert.deepEqual(viewAt(e,2).highlight,{paths:[['Feed mechanism','Holding pawl']],others:'keep',color:'#237c86'});
  assert.equal(viewAt(e,3.5).highlight,null);
  assert.equal(viewAt(e,4).highlight,null,'a cut restores');
});

test('invalid highlights are refused before rendering, naming the shot',()=>{
  const cases=[
    [c=>{c.parts=[];},/parts/],
    [c=>{c.parts=['ropes'];},/Unknown layer: ropes/],
    [c=>{c.parts=[['Feed mechanism','Drving pawl']];},/Missing assembly path: Feed mechanism\/Drving pawl/],
    [c=>{c.parts=['Feed mechanism','Driving pawl'];},/Unknown layer: Feed mechanism/],
    [c=>{c.others='fade';},/others/],
    [c=>{c.color='red';},/#rrggbb/],
    [c=>{c.to=4.5;},/time/],
    [c=>{c.colour='#ffffff';},/Unknown highlight field: colour/],
  ];
  for(const [edit,pattern] of cases){
    const e=highlighted();edit(e.shots[0].highlight[0]);
    assert.throws(()=>valid(e),error=>pattern.test(error.message)&&/pawls/.test(error.message),String(pattern));
  }
  let e=highlighted();e.shots[0].highlight[1].from=1.5;
  assert.throws(()=>valid(e),/Highlight cues overlap in shot pawls/);
  e=highlighted();e.shots[0].hiddenLayers=['feed'];
  assert.throws(()=>valid(e),/Highlighted part is hidden in shot pawls/);
  e=highlighted();e.style.accent='teal';
  assert.throws(()=>valid(e),/pawls.*style\.accent.*#rrggbb/);
  e=highlighted();e.format='machinome-video-draft/0.2';
  assert.throws(()=>valid(e),/Highlights need format machinome-video-draft\/0\.3: shot pawls/);
  e=highlighted();e.shots[0].hiddenLayers=['frame'];
  assert.doesNotThrow(()=>valid(e),'hiding one layer while ghosting the rest is allowed');
});

test('highlights require Viewer API 28',()=>{
  assert.deepEqual(requiredViewerApi(highlighted()),{api:28,reasons:['highlight (shot pawls)']});
});
