import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi,viewerApiFromBanner,confirmViewerApi,viewerApiRefusal,PAPER_STAGE} from '../src/episode.mjs';
import {viewAt,placeInBox,offsetInBox} from './frame-fixtures.mjs';

const manifest={animation:{loop:296},root:{name:'Mill',children:[
  {name:'Feed mechanism',children:[{name:'Driving pawl'},{name:'Holding pawl'},{name:'Ratchet to reduction shaft'}]},
  {name:'Frame'}]}};
const shot=(id,start,end,extra={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:8,to:8+end-start},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
export const annotated=()=>({format:'machinome-video-draft/0.3',
  output:{width:1280,height:720,fps:30,durationSeconds:4},
  model:{expectedDurationSeconds:296,timeMode:'normalized-loop'},
  style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
  cameras:{a:{position:[0,0,10],target:[0,0,0],up:[0,1,0],fov:37}},
  layers:{feed:[['Feed mechanism']],'rope-1':[['Feed mechanism','Ratchet to reduction shaft']],frame:[['Frame']]},evidence:{},
  shots:[shot('pawls',0,2,{annotations:[
      {from:.5,to:1.5,kind:'arrow',part:['Feed mechanism','Driving pawl'],place:[.18,.22],text:'Pulls one tooth'},
      {from:0,to:2,kind:'label',part:'rope-1',offset:[.04,-.05],text:'Rope 1'}]}),
    shot('plain',2,4)]});
const valid=e=>validateEpisode(e,manifest);

// An annotation is a mark of the shot's view (design D3): its safe-area place
// and offset converted to fractions of the view's box in the paper set.
const box=PAPER_STAGE.paper,marks=(e,t)=>viewAt(e,t).marks;
test('a 0.3 arrow on a path and a label on a layer are emitted only while active',()=>{
  const e=annotated();valid(e);
  assert.deepEqual(marks(e,.25).map(a=>a.text),['Rope 1']);
  const both=marks(e,1);
  assert.deepEqual(both.map(a=>a.kind),['arrow','label']);
  assert.deepEqual(both[0],{id:'cues[0].actions[0]',kind:'arrow',text:'Pulls one tooth',target:{paths:[['Feed mechanism','Driving pawl']]},
    place:placeInBox([.18,.22],.08,box),opacity:1,drawn:1});
  assert.deepEqual(both[1],{id:'cues[1].actions[0]',kind:'label',text:'Rope 1',target:{paths:[['Feed mechanism','Ratchet to reduction shaft']]},
    offset:offsetInBox([.04,-.05],.08,box),opacity:1,drawn:1});
  assert.deepEqual(marks(e,1.5).map(a=>a.id),['cues[1].actions[0]']);
  assert.deepEqual(marks(e,2),[],'the cut removes every annotation');
  e.shots[0].annotations[1]={from:0,to:1,kind:'label',point:[1,2,3],text:'Here'};valid(e);
  assert.deepEqual(marks(e,0)[0],{id:'cues[1].actions[0]',kind:'label',text:'Here',target:{point:[1,2,3]},offset:[0,0],opacity:1,drawn:1});
});

test('invalid annotations are refused before rendering, naming the shot',()=>{
  const cases=[
    [a=>{a.kind='ring';},/kind/],
    [a=>{a.point=[0,0,0];},/exactly one of part or point/],
    [a=>{delete a.part;},/exactly one of part or point/],
    [a=>{a.part='ropes';},/Unknown layer: ropes/],
    [a=>{a.part=['Feed mechanism','Drving pawl'];},/Missing assembly path: Feed mechanism\/Drving pawl/],
    [a=>{delete a.part;a.point=[0,Infinity,0];},/point/],
    [a=>{a.to=2.5;},/time/],
    [a=>{a.from=1.5;},/time/],
    [a=>{delete a.place;},/place/],
    [a=>{a.place=[1.2,.5];},/place/],
    [a=>{a.offset=[0,0];},/offset/],
    [a=>{a.palce=[.1,.1];},/Unknown annotation field: palce/],
  ];
  for(const [edit,pattern] of cases){
    const e=annotated();edit(e.shots[0].annotations[0]);
    assert.throws(()=>valid(e),error=>pattern.test(error.message)&&/pawls/.test(error.message),String(pattern));
  }
  const labels=[
    [a=>{delete a.text;},/text/],
    [a=>{a.offset=[0,1.5];},/offset/],
    [a=>{a.place=[.5,.5];},/place/],
  ];
  for(const [edit,pattern] of labels){
    const e=annotated();edit(e.shots[0].annotations[1]);
    assert.throws(()=>valid(e),error=>pattern.test(error.message)&&/pawls/.test(error.message),String(pattern));
  }
  let e=annotated();e.shots[0].hiddenLayers=['feed'];
  assert.throws(()=>valid(e),/Annotated part is hidden in shot pawls/);
  e=annotated();delete e.style.safeInsetFraction;
  assert.throws(()=>valid(e),/safeInsetFraction/);
  e=annotated();e.format='machinome-video-draft/0.2';
  assert.throws(()=>valid(e),/format machinome-video-draft\/0\.3.*pawls|pawls.*format machinome-video-draft\/0\.3/);
});

test('annotations require Viewer API 28, confirmed from the bundle banner by check',()=>{
  const required=requiredViewerApi(annotated());
  assert.deepEqual(required,{api:28,reasons:['annotations (shot pawls)']});
  const plain=annotated();delete plain.shots[0].annotations;
  assert.deepEqual(requiredViewerApi(plain),{api:21,reasons:[]});
  const banner='/*!\n * machinome-viewer.js - the browser viewer for machinome models\n * machinome-viewer 0.7.1 - viewer API 27\n */\nwindow.x=1;';
  assert.equal(viewerApiFromBanner(banner),27);
  assert.equal(viewerApiFromBanner('window.MachinomeViewer={}'),null);
  assert.throws(()=>confirmViewerApi(required,banner),/needs Viewer API 28 for annotations \(shot pawls\); the selected viewer declares API 27/);
  assert.throws(()=>confirmViewerApi(required,'window.MachinomeViewer={}'),/cannot confirm the viewer API/i);
  assert.throws(()=>confirmViewerApi(required,null),/cannot confirm the viewer API/i);
  assert.doesNotThrow(()=>confirmViewerApi(required,banner.replace('API 27','API 28')));
  assert.doesNotThrow(()=>confirmViewerApi({api:21,reasons:[]},null),'a 21 episode never needs the bundle');
});

test('the viewer refusal calls an episode an episode and a movie a movie',()=>{
  const required=requiredViewerApi(annotated());
  const banner='/*! machinome-viewer 0.7.1 - viewer API 27 */';
  assert.equal(viewerApiRefusal(required,27,'episode'),
    'This episode needs Viewer API 28 for annotations (shot pawls); the selected viewer declares API 27. Install a machinome-viewer that declares it: pip install -U "machinome[viewer]".');
  assert.equal(viewerApiRefusal(required,27),viewerApiRefusal(required,27,'episode'),'an episode by default');
  assert.throws(()=>confirmViewerApi(required,banner),/^Error: This episode needs Viewer API 28/);
  const marks={api:28,reasons:['marks (shot push)']};
  assert.equal(viewerApiRefusal(marks,27,'movie'),
    'This movie needs Viewer API 28 for marks (shot push); the selected viewer declares API 27. Install a machinome-viewer that declares it: pip install -U "machinome[viewer]".');
  assert.throws(()=>confirmViewerApi(marks,banner,'movie'),/^Error: This movie needs Viewer API 28 for marks \(shot push\)/);
  assert.throws(()=>confirmViewerApi(marks,null,'movie'),/this movie needs Viewer API 28/);
  assert.throws(()=>confirmViewerApi(marks,null,'movie'),e=>!/episode/.test(e.message));
});
