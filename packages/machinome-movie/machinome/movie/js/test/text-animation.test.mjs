import {test} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,requiredViewerApi,episodeFilm} from '../src/episode.mjs';
import {frameAt} from '../src/timeline.mjs';
import {resolveWordTiming} from '../src/words.mjs';
import {base02,yamlFrame,element} from './frame-fixtures.mjs';

const align=text=>({characters:Array.from(text),character_start_times_seconds:Array.from(text,(_,i)=>i/20),character_end_times_seconds:Array.from(text,(_,i)=>(i+1)/20)});
const episode=()=>{const e=base02();e.format='machinome-video-draft/0.4';e.audio={replacements:{}};
  e.shots[0].narration='Propose. Inspect. Correct.';
  e.shots[0].overlays=[
    {from:0,to:1.9,text:'Propose. Inspect. Correct.',position:'top',reveal:{timing:'spoken'}},
    {from:0,to:1.9,text:'Pause. Inspect. Test.',position:'lower-third',reveal:{timing:'even',duration:1.5}},
    {from:0,to:1.9,text:'REVOLUTIONS',subtitle:'A working wheel',position:'title',enter:{kind:'fade',duration:.4},leave:{kind:'fade',duration:.4}}];
  return e;};
const manifest={animation:{loop:296}};

// Overlay #i of a shot is its title element overlay-<i> (react-stage D3).
test('0.4 measured, even and title frames are deterministic, while plain frames stay authored',async()=>{
  const e=episode();validateEpisode(e,manifest);
  assert.deepEqual(requiredViewerApi(e),{api:21,reasons:[]});
  const film=episodeFilm(e);
  assert.throws(()=>frameAt(film,.1),/Word timing is not resolved: shot first/);
  await resolveWordTiming(film,async()=>({sha256:'take',alignment:align(e.shots[0].narration)}));
  const overlay=(t,i)=>element(frameAt(film,t),`overlay-${i}`);
  assert.equal(overlay(.8,0).revealed,2);
  assert.equal(overlay(.8,1).revealed,2);
  assert.equal(overlay(.8,2).opacity,1);
  assert.equal(overlay(.8,0).words.filter(p=>p.word).length,3);
  assert.equal(overlay(0,2).opacity,0);
  assert.ok(Math.abs(overlay(1.7,2).opacity-.5)<1e-12);
  assert.deepEqual(overlay(.8,2),{kind:'title',shown:true,text:'REVOLUTIONS',subtitle:'A working wheel',opacity:1});
  assert.deepEqual(frameAt(film,.8),frameAt(film,.8));
  const plain=base02();plain.format='machinome-video-draft/0.4';plain.shots[0].overlays=[{from:0,to:1,text:'Plain',position:'top'}];
  assert.deepEqual(element(yamlFrame(plain,.5),'overlay-0'),{kind:'title',shown:true,text:'Plain',opacity:1});
  assert.equal(yamlFrame(plain,.5).slots.top,'first.overlay-0');
});

test('new text fields require 0.4, while older unknown fields remain ignored',()=>{
  for(const format of ['machinome-video-draft/0.2','machinome-video-draft/0.3']){
    for(const field of ['reveal','subtitle','enter','leave']){
      const e=episode();e.format=format;e.shots[0].overlays=[{from:0,to:1,text:'One',position:'top',[field]:field==='reveal'?{timing:'even',duration:.5}:field==='subtitle'?'Sub':{kind:'fade',duration:.2}}];
      assert.throws(()=>validateEpisode(e,manifest),/Text animation needs format machinome-video-draft\/0.4: shot first/);
    }
    const title=episode();title.format=format;title.shots[0].overlays=[{from:0,to:1,text:'One',position:'title'}];
    assert.throws(()=>validateEpisode(title,manifest),/Text animation needs format machinome-video-draft\/0.4: shot first/);
    const old=base02();old.format=format;old.shots[0].overlays=[{from:0,to:1,text:'One',position:'top',unknown:7}];
    validateEpisode(old,manifest);
  }
});

test('0.4 closed fields, position rules, durations and title overlap refuse invalid text',()=>{
  const bad=(edit,pattern)=>{const e=episode();edit(e);assert.throws(()=>validateEpisode(e,manifest),pattern);};
  bad(e=>{e.shots[0].overlays[0].revael=1;},/Unknown overlay field: revael/);
  bad(e=>{e.shots[0].overlays[0].reveal.duration=1;},/Unknown reveal field: duration/);
  bad(e=>{e.shots[0].overlays[1].reveal.ease='sideways';},/Unknown easing/);
  bad(e=>{e.shots[0].overlays[1].reveal.duration=2;},/reveal.*cue|cue.*reveal/i);
  bad(e=>{e.shots[0].overlays[0].subtitle='No';},/title.*subtitle/i);
  bad(e=>{e.shots[0].overlays[0].enter={kind:'fade',duration:.1};},/title.*enter/i);
  bad(e=>{e.shots[0].overlays[0].leave={kind:'fade',duration:.1};},/title.*leave/i);
  bad(e=>{e.shots[0].overlays[2].enter.kind='draw';},/fade/);
  bad(e=>{e.shots[0].overlays[2].enter.duration=0;},/positive|duration/i);
  bad(e=>{e.shots[0].overlays[2].leave.duration=0;},/positive|duration/i);
  bad(e=>{e.shots[0].overlays[2].enter.duration=1.2;e.shots[0].overlays[2].leave.duration=1.2;},/overlap|exceed/i);
  bad(e=>{e.shots[0].overlays.push({from:.5,to:1.5,text:'Second',position:'title'});},/titles overlap/i);
});

test('0.4 closes entrance, exit, code, typing and emphasis fields without closing old code',()=>{
  const bad=(edit,pattern)=>{const e=episode();e.sourceCode={sample:{lines:[1,1],text:'x = 1'}};
    e.shots[1].narration='x';e.shots[1].code={snippet:'sample',typing:[{from:0,to:.2,throughLine:1}],
      emphasis:[{line:1,phrase:'x',words:['x'],hold:0}]};edit(e);
    assert.throws(()=>validateEpisode(e,manifest),pattern);};
  bad(e=>{e.shots[0].overlays[2].enter.curve='in';},/Unknown entrance field: curve/);
  bad(e=>{e.shots[0].overlays[2].leave.curve='in';},/Unknown exit field: curve/);
  bad(e=>{e.shots[1].code.snipet='sample';},/Unknown code field: snipet/);
  bad(e=>{e.shots[1].code.typing[0].easing='in';},/Unknown typing cue field: easing/);
  bad(e=>{e.shots[1].code.emphasis[0].wordsToo=['x'];},/Unknown emphasis field: wordsToo/);
  const old=base02();old.format='machinome-video-draft/0.3';old.sourceCode={sample:{lines:[1,1],text:'x = 1'}};
  old.shots[1].code={snippet:'sample',typing:[{from:0,to:.2,throughLine:1,ignored:1}],ignored:1};
  validateEpisode(old,manifest);
  old.shots[1].code.emphasis=[];
  assert.throws(()=>validateEpisode(old,manifest),/Text animation needs format machinome-video-draft\/0.4: shot second/);
  old.format='machinome-video-draft/0.2';
  assert.throws(()=>validateEpisode(old,manifest),/Text animation needs format machinome-video-draft\/0.4: shot second/);
});

// Pinned whole, as the stage reads it: the paper-split set with its source
// panel, its view and the three text positions (the same content the 0.3 page
// drew, on the new frame).
test('the literal 0.3 frame with three overlay positions and typed Python remains pinned',()=>{
  const e=base02();e.format='machinome-video-draft/0.3';
  e.sourceCode={sample:{file:'model.py',lines:[1,1],text:'x = 1'}};
  e.shots[1].overlays=['top','lower-third','center'].map(position=>({from:0,to:2,position,text:position}));
  e.shots[1].code={snippet:'sample',typing:[{from:0,to:.2,throughLine:1}]};
  const title=text=>({kind:'title',shown:true,text,opacity:1});
  assert.deepEqual(yamlFrame(e,2.5),{time:2.5,chapterId:'second',shotId:'second',set:'paper-split',
    slots:{right:'second.view',left:'second.code',top:'second.overlay-0','lower-third':'second.overlay-1',center:'second.overlay-2'},
    elements:{
      'second.view':{kind:'view',time:12/296,view:{camera:[10,0,10],target:[0,0,0]},up:[0,1,0],fov:37,hidden:[],highlight:null,marks:[]},
      'second.code':{kind:'source',file:'model.py',firstLine:1,lastLine:1,text:'x = 1',
        html:'x = <span class="hljs-number">1</span>',cursor:false,emphasis:[]},
      'second.overlay-0':title('top'),'second.overlay-1':title('lower-third'),'second.overlay-2':title('center')},
    transition:null});
});
