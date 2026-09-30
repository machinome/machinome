import {test} from 'vitest';
import assert from 'node:assert/strict';
import {base02,cues03,element} from './frame-fixtures.mjs';
import {frameAt} from '../src/timeline.mjs';
import {episodeFilm} from '../src/episode.mjs';
import {outputShotUnits,fingerprintShotUnits} from '../src/shot-cache.mjs';
import {hash} from '../src/util.mjs';
import {buildReviewSamplePlan} from '../src/review-samples.mjs';

// An episode is planned as the resolved document it converts to (react-stage
// D3); `timing` fills what resolveWordTiming would have measured, by shot.
function filmOf(e){
  const film=episodeFilm(e);
  for(const [shotId,{onsets={},emphasis={}}] of Object.entries(e.timing??{})){
    const shot=film.chapters.flatMap(c=>c.shots).find(s=>s.id===shotId);
    for(const cue of shot.cues)for(const action of cue.actions){
      if(action.overlay!==undefined&&onsets[action.overlay])action.reveal.onsets=onsets[action.overlay];
      if(action.emphasis!==undefined&&emphasis[action.emphasis]){
        const {at,until}=emphasis[action.emphasis];
        action.words.forEach((word,k)=>{word.at=at[k];});action.until=until;cue.at=at[0];
      }
    }
    film.wordTiming[shotId]={sha256:`take-${shotId}`};
  }
  return film;
}
function planFor(e,fps=e.output.fps){
  const film=filmOf(e);
  const {count,units}=outputShotUnits(film,fps),before=JSON.stringify(units.map(u=>u.frames));
  const plan=buildReviewSamplePlan(film,units,fps);
  assert.equal(JSON.stringify(units.map(u=>u.frames)),before,
    'render-only cue identities must not mutate frame requests or shot-cache inputs');
  assert.equal(plan.schema,'review-samples-v1');
  assert.equal(plan.frameCount,count);assert.equal(plan.fps,fps);
  assert.ok(Array.isArray(plan.samples));
  return {plan,units};
}
const sample=(plan,indices)=>plan.samples.find(s=>JSON.stringify(s.indices)===JSON.stringify(indices));
const labels=(plan,indices,kind)=>sample(plan,indices)?.labels.filter(l=>l.kind===kind)??[];
const shot=(id,start,end,more={})=>({id,start,end,narration:'Words.',direction:'Look.',
  simulation:{from:start,to:end},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...more});
function episode(){
  const e={format:'machinome-video-draft/0.4',title:'Review',output:{width:320,height:180,fps:4,durationSeconds:4.5},
    model:{expectedDurationSeconds:10},style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f'},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    shots:[shot('A',0,1.45),shot('B',1.45,3.45,{transition:{kind:'dissolve',duration:1.3}}),
      shot('C',3.45,4.5,{transition:{kind:'fade',duration:.5}})]};
  return e;
}
function measuredEpisode(){
  const e=episode(),b=e.shots[1];
  e.sourceCode={drive:{file:'model.py',lines:[415,415],text:'wheel shaft'}};
  b.narration='wheel shaft';
  b.overlays=[{from:.1,to:2,position:'top',text:'wheel shaft',reveal:{timing:'spoken'}}];
  b.code={snippet:'drive',typing:[{from:0,to:.2,throughLine:415}],
    emphasis:[{line:415,phrase:'wheel shaft',words:['wheel','shaft'],hold:.2}]};
  e.timing={B:{onsets:{0:[.3,.55]},emphasis:{0:{at:[.3,.55],until:.9}}}};
  return e;
}

// The review sidecar is render-only: planning reads the frames and never
// changes them or the shot keys computed from them, and both are deterministic.
test('frame requests and shot keys are deterministic and untouched by planning',async()=>{
  const a=base02(),b=cues03(),c=base02(),d=base02();
  c.format=d.format='machinome-video-draft/0.4';
  d.sourceCode={drive:{file:'model.py',lines:[415,415],text:'water_drive.spin()'}};
  d.shots[1].code={snippet:'drive',typing:[{from:0,to:.8,throughLine:415}]};
  for(const [e,time] of [[a,1.5],[b,1],[c,1.5],[d,2.5]]){
    const keys=async(plan)=>{
      const film=episodeFilm(e),{units}=outputShotUnits(film,e.output.fps);
      await fingerprintShotUnits(film,units,'review-common');
      if(plan)buildReviewSamplePlan(film,units,e.output.fps);
      return {request:hash(JSON.stringify(frameAt(film,time))),keys:units.map(u=>u.key),frames:JSON.stringify(units.map(u=>u.frames))};
    };
    const once=await keys(false),twice=await keys(true);
    assert.deepEqual(twice,once);
    assert.equal(once.request,hash(JSON.stringify(frameAt(episodeFilm(e),time))));
  }
});

test('fractional global requests pair a join, measured word, source token and clearing exactly',()=>{
  const e=measuredEpisode(),{plan,units}=planFor(e);
  assert.deepEqual(units.map(u=>u.frames[0]?.index),[0,6,14]);
  const film=filmOf(e);
  assert.equal(frameAt(film,1.5).shotId,'B');
  assert.deepEqual(element(frameAt(film,1.75),'code').emphasis,[{token:'wheel',start:0,end:5}]);
  assert.equal(labels(plan,[5,6],'join').length,1);
  const word=labels(plan,[6,7],'word-onset');
  assert.equal(word.length,1);assert.equal(word[0].shotId,'B');
  assert.equal(word[0].authoredIndex,0);assert.equal(word[0].wordOrdinal,0);
  const source=labels(plan,[6,7],'source-emphasis-onset');
  assert.equal(source.length,1);assert.deepEqual(
    [source[0].shotId,source[0].authoredIndex,source[0].wordOrdinal,source[0].word,source[0].line,source[0].start,source[0].end],
    ['B',0,0,'wheel',415,0,5]);
  // Labels name the cue and the element as well as the authored index.
  assert.deepEqual([word[0].cue,word[0].element],['cues[0].actions[0]','B.overlay-0']);
  assert.deepEqual([source[0].cue,source[0].element],['cues[2].actions[0]','B.code']);
  assert.equal(labels(plan,[7,8],'word-onset')[0].wordOrdinal,1);
  assert.equal(labels(plan,[7,8],'source-emphasis-onset')[0].wordOrdinal,1);
  assert.equal(labels(plan,[9,10],'source-emphasis-clear').length,1);
  assert.equal(labels(plan,[13,14],'word-onset').some(l=>l.shotId==='B'),false,
    'the same B cue moving from active to outgoing is not a new onset');
  const join=labels(plan,[13,14],'join')[0];
  assert.equal(join.shotId,'C');assert.equal(join.outgoingShotId,'B');
  assert.deepEqual(join.sides,['outgoing'],
    'C is a fade on its outgoing-only first frame, although both logical shot identities remain');
  assert.equal(sample(plan,[6,7]).labels.length>=2,true,'co-occurring labels stay on one pair');
});

test('a document\'s cue, which has no YAML authored index, is labelled by its index in its shot',()=>{
  const film=filmOf(measuredEpisode());
  for(const cue of film.chapters[1].shots[0].cues)for(const action of cue.actions){delete action.emphasis;delete action.overlay;}
  const {units}=outputShotUnits(film,4),plan=buildReviewSamplePlan(film,units,4);
  assert.equal(labels(plan,[6,7],'source-emphasis-onset')[0].authoredIndex,2);
  assert.equal(labels(plan,[6,7],'word-onset')[0].authoredIndex,0);
});

test('identical even descriptions retain two authored overlay identities, not text-based identity',()=>{
  const e=episode(),b=e.shots[1];
  b.overlays=[{from:.1,to:2,position:'top',text:'ONE TWO',reveal:{timing:'even',duration:.6}},
    {from:.1,to:2,position:'top',text:'ONE TWO',reveal:{timing:'even',duration:.6}}];
  const {plan}=planFor(e),first=labels(plan,[6,7],'word-onset');
  assert.deepEqual(first.map(l=>[l.shotId,l.authoredIndex,l.wordOrdinal,l.shown,l.element]),
    [['B',0,0,1,'B.overlay-0'],['B',1,0,1,'B.overlay-1']]);
  const second=labels(plan,[7,8],'word-onset');
  assert.deepEqual(second.map(l=>[l.shotId,l.authoredIndex,l.wordOrdinal,l.shown]),
    [['B',0,1,2],['B',1,1,2]]);
});

test('different shots keep cue index zero distinct across a join and unchanged active-to-outgoing state',()=>{
  const e=episode();e.shots[1].transition.kind='dissolve';
  e.shots[0].overlays=[{from:1,to:1.45,position:'top',text:'A B',
    reveal:{timing:'even',duration:.4}}];
  e.shots[1].overlays=[{from:0,to:2,position:'top',text:'C D',
    reveal:{timing:'even',duration:.4}}];
  const {plan}=planFor(e);
  assert.ok(labels(plan,[3,4],'word-onset').some(l=>l.shotId==='A'&&l.authoredIndex===0));
  assert.ok(labels(plan,[5,6],'word-onset').some(l=>l.shotId==='B'&&l.authoredIndex===0));
  assert.equal(labels(plan,[5,6],'word-onset').some(l=>l.shotId==='A'),false,
    'A cue has the same resolved full count before and after role transfer');
  assert.equal(labels(plan,[5,6],'join')[0].outgoingShotId,'A');
});

test('two measured words resolved onto one global frame retain two ordinals on one pair',()=>{
  const e=episode();e.shots[1].overlays=[{from:.1,to:2,position:'top',text:'ONE TWO',
    reveal:{timing:'spoken'}}];
  e.timing={B:{onsets:{0:[.26,.27]}}};
  const {plan}=planFor(e);
  assert.deepEqual(labels(plan,[6,7],'word-onset').map(l=>[l.shotId,l.authoredIndex,l.wordOrdinal,l.shown]),
    [['B',0,0,2],['B',0,1,2]],'both timed words remain, even though the rendered count jumps 0 to 2');
});

test('fade samples its selected side; other joins retain both candidate sides and interior frames',()=>{
  for(const kind of ['fade','dissolve','wipe','slide']){
    const e=episode(),b=e.shots[1];b.transition={kind,duration:1.3};
    b.overlays=[{from:0,to:2,position:'top',text:'ONE TWO THREE',reveal:{timing:'even',duration:.8}}];
    const {plan,units}=planFor(e),run=units[1].frames.filter(f=>f.request.transition?.field==='transition').map(f=>f.index);
    assert.deepEqual(run,[6,7,8,9,10]);
    assert.equal(labels(plan,[5,6],'join').length,1,kind);
    assert.equal(labels(plan,[8],'transition-midpoint').length,1,kind);
    assert.equal(labels(plan,[10],'transition-last-active').length,1,kind);
    if(kind==='fade'){
      assert.equal(labels(plan,[6,7],'word-onset').some(l=>l.shotId==='B'),false,
        'incoming word advance at outgoing-only frame is not a visible onset');
      const entry=labels(plan,[8,9],'picture-entry').find(l=>l.shotId==='B');
      assert.ok(entry,'newly selected incoming picture records its resolved state');
      assert.ok(entry.shown>=2);assert.equal(entry.side,'incoming');
      assert.equal(labels(plan,[8,9],'word-onset').some(l=>l.shotId==='B'),false);
    }else{
      assert.ok(labels(plan,[6,7],'word-onset').some(l=>l.shotId==='B'&&l.side==='incoming'),kind);
      const join=labels(plan,[5,6],'join')[0];
      assert.ok(join.sides.includes('outgoing')&&join.sides.includes('incoming'),kind);
    }
  }
});

test('film and shot ends use filmed indices; one-frame end is single and zero-frame shot invents none',()=>{
  const e=episode(),{plan}=planFor(e);
  assert.equal(labels(plan,[16,17],'film-end').length,1);
  assert.equal(labels(plan,[4,5],'shot-end').some(l=>l.shotId==='A'),true);
  assert.equal(labels(plan,[12,13],'shot-end').some(l=>l.shotId==='B'),true);
  const short={...episode(),output:{width:320,height:180,fps:2,durationSeconds:1},
    shots:[shot('first',0,.1),shot('unfilmed',.1,.2),shot('last',.2,1)]};
  const {plan:tiny,units}=planFor(short);
  assert.deepEqual(units.map(u=>u.frames.map(f=>f.index)),[[0],[],[1]]);
  assert.equal(labels(tiny,[0],'shot-end').some(l=>l.shotId==='first'),true);
  assert.equal(labels(tiny,[1],'shot-end').some(l=>l.shotId==='last'),true);
  assert.equal(tiny.samples.flatMap(s=>s.labels).some(l=>l.shotId==='unfilmed'&&l.kind==='shot-end'),false);
  const one={...short,output:{...short.output,durationSeconds:.5},shots:[shot('only',0,.5)]};
  const {plan:single}=planFor(one);
  assert.equal(labels(single,[0],'shot-end').length,1);
  assert.equal(labels(single,[0],'film-end').length,1);
  assert.equal(single.samples.some(s=>s.indices.some(i=>i<0)),false);
});

test('back-to-back dissolves have distinct per-shot transition interiors',()=>{
  const e=episode();e.output.durationSeconds=3;
  e.shots=[shot('A',0,1),shot('B',1,2,{transition:{kind:'dissolve',duration:1}}),
    shot('C',2,3,{transition:{kind:'dissolve',duration:1}})];
  const {plan}=planFor(e);
  assert.equal(labels(plan,[5],'transition-midpoint')[0]?.shotId,'B');
  assert.equal(labels(plan,[7],'transition-last-active')[0]?.shotId,'B');
  assert.equal(labels(plan,[9],'transition-midpoint')[0]?.shotId,'C');
  assert.equal(labels(plan,[11],'transition-last-active')[0]?.shotId,'C');
});

test('fadeIn and fadeOut each retain midpoint/last-active samples without an outgoing shot',()=>{
  const e=episode();e.output.durationSeconds=2;
  e.shots=[shot('A',0,1,{fadeIn:{duration:1}}),shot('B',1,2,{fadeOut:{duration:1}})];
  const {plan}=planFor(e);
  for(const [index,shotId,field,kind] of [[1,'A','fadeIn','transition-midpoint'],
    [3,'A','fadeIn','transition-last-active'],[5,'B','fadeOut','transition-midpoint'],
    [7,'B','fadeOut','transition-last-active']]){
    const found=labels(plan,[index],kind)[0];
    assert.equal(found?.shotId,shotId);assert.equal(found?.field,field);
    assert.equal(Object.hasOwn(found,'outgoingShotId'),false);
  }
});

test('emphasis clearing on continued outgoing shot labels its selected outgoing side',()=>{
  const e=episode(),a=e.shots[0];e.shots[1].transition.kind='dissolve';
  e.sourceCode={drive:{file:'model.py',lines:[415,415],text:'wheel'}};
  a.code={snippet:'drive',typing:[{from:0,to:.1,throughLine:415}],
    emphasis:[{line:415,phrase:'wheel',words:['wheel'],hold:0}]};
  a.narration='wheel';
  e.timing={A:{emphasis:{0:{at:[1],until:1.4}}}};
  const {plan}=planFor(e);
  const clear=labels(plan,[5,6],'source-emphasis-clear')[0];
  assert.equal(clear?.shotId,'A');assert.equal(clear?.side,'outgoing');
  assert.deepEqual(clear?.words,[{wordOrdinal:0,word:'wheel',line:415,start:0,end:5}]);
});

test('a frame-zero reveal has a single filmed onset sample, never an invented predecessor',()=>{
  const e=episode();e.output.durationSeconds=1;
  e.shots=[shot('A',0,1,{overlays:[{from:0,to:1,position:'top',text:'ONE TWO',
    reveal:{timing:'even',duration:.5}}]})];
  const {plan}=planFor(e);
  assert.deepEqual(labels(plan,[0],'word-onset').map(l=>[l.shotId,l.wordOrdinal,l.shown]),[['A',0,1]]);
  assert.equal(plan.samples.some(s=>s.indices.some(index=>index<0)),false);
});

test('coarse render grid keeps fade-delayed first incoming picture as entry after transition ends',()=>{
  const e=episode();e.output.fps=30;e.output.durationSeconds=3;
  e.shots=[shot('A',0,1.45),shot('B',1.45,3,{transition:{kind:'fade',duration:.4},
    overlays:[{from:0,to:1.55,position:'top',text:'ONE TWO',
      reveal:{timing:'even',duration:.2}}]})];
  const {plan,units}=planFor(e,2);
  assert.equal(units[1].frames[0].request.transition.picture,'outgoing');
  assert.equal(units[1].frames[1].request.transition,null);
  assert.equal(labels(plan,[3,4],'word-onset').some(l=>l.shotId==='B'),false);
  const entry=labels(plan,[3,4],'picture-entry').find(l=>l.shotId==='B');
  assert.equal(entry?.shown,2);assert.equal(entry?.side,'incoming');
});
