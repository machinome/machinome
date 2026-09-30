import {test,describe} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode} from '../src/episode.mjs';
import {frameAt} from '../src/timeline.mjs';
import {outputShotUnits,fingerprintShotUnits} from '../src/shot-cache.mjs';
import {base02} from './frame-fixtures.mjs';

const v04='machinome-video-draft/0.4';
const manifest={animation:{loop:296},root:{name:'Mill'}};
function episode(){
  const e=base02();e.format=v04;
  e.style={background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08};
  e.sourceCode={drive:{file:'model.py',lines:[415,415],text:'water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)'}};
  e.shots[0].hiddenLayers=[];
  e.shots[1].code={snippet:'drive',typing:[{from:0,to:.8,throughLine:415}]};
  return e;
}
function joined(){
  const e=episode();e.output.durationSeconds=6;e.shots[0].end=1.15;
  e.shots[0].simulation={from:8,to:9.15};e.shots[0].camera=[{at:0,preset:'a'}];
  e.shots[1].start=1.15;e.shots[1].end=4.65;e.shots[1].simulation={from:9.15,to:12.65};
  e.shots[1].camera=[{at:0,preset:'b'}];
  e.shots.push({...structuredClone(e.shots[0]),id:'return',start:4.65,end:6,
    simulation:{from:12.65,to:14},camera:[{at:0,preset:'a'}],transition:{kind:'dissolve',duration:.4}});
  return e;
}
const valid=e=>validateEpisode(e,manifest);

test('source-only is a 0.4 code-shot opt-in; omitted layout retains the old request shape',()=>{
  const old=episode();assert.doesNotThrow(()=>valid(old));
  assert.equal(Object.hasOwn(frameAt(old,2.5),'layout'),false);
  const opted=episode();opted.shots[1].layout='source-only';
  assert.doesNotThrow(()=>valid(opted));
  assert.equal(frameAt(opted,2.5).layout,'source-only');
  assert.equal(Object.hasOwn(frameAt(opted,.5),'layout'),false);
});

describe('source-only refuses missing code, unknown layout, older formats and nonempty model/picture cues by name',()=>{
  const bad=(edit,pattern)=>{const e=episode();edit(e);assert.throws(()=>valid(e),pattern);};
  test('code required',()=>bad(e=>{e.shots[0].layout='source-only';},/source-only.*code.*first|first.*source-only.*code/i));
  test('unknown value',()=>bad(e=>{e.shots[1].layout='split';},/layout.*split.*second|second.*layout.*split/i));
  for(const format of ['machinome-video-draft/0.2','machinome-video-draft/0.3'])
    test(format,()=>bad(e=>{e.format=format;e.shots[1].layout='source-only';},/source-only.*0\.4.*second|second.*source-only.*0\.4/i));
  test('annotations',()=>bad(e=>{e.shots[1].layout='source-only';e.shots[1].annotations=[{from:0,to:1,kind:'label',point:[0,0,0],text:'No'}];},/source-only.*annotations.*second|second.*annotations.*source-only/i));
  test('highlight',()=>bad(e=>{e.shots[1].layout='source-only';e.shots[1].highlight=[{from:0,to:1,parts:['frame'],others:'ghost'}];},/source-only.*highlight.*second|second.*highlight.*source-only/i));
  test('pictures',()=>bad(e=>{e.shots[1].layout='source-only';e.shots[1].pictures=[{from:0,to:1,still:'cover'}];},/source-only.*pictures.*second|second.*pictures.*source-only/i));
  test('empty cue lists',()=>{
    const empty=episode();empty.shots[1].layout='source-only';
    empty.shots[1].annotations=[];empty.shots[1].highlight=[];empty.shots[1].pictures=[];
    assert.doesNotThrow(()=>valid(empty));
  });
});

test('fractional global-grid requests carry only the opted shot layout, including outgoing continuation',()=>{
  const e=joined();valid(e);
  const before=frameAt(e,4.7),plain=structuredClone(before);
  assert.equal(before.transition.outgoing.code.text,e.sourceCode.drive.text);
  assert.equal(before.transition.outgoing.code.cursor,false);
  assert.equal(Object.hasOwn(before.transition.outgoing,'layout'),false);
  e.shots[1].layout='source-only';
  // Timeline directly exercises the request seam even while old validation rejects the new author field.
  for(const t of [1.15,1.2,4.633333333333334])assert.equal(frameAt(e,t).layout,'source-only',`incoming at ${t}`);
  for(const t of [4.666666666666667,4.7,4.8]){
    const f=frameAt(e,t);
    assert.equal(f.shotId,'return');assert.equal(Object.hasOwn(f,'layout'),false);
    assert.equal(f.transition.outgoing.layout,'source-only',`outgoing at ${t}`);
    assert.equal(f.transition.outgoing.code.text,e.sourceCode.drive.text);
    assert.equal(f.transition.outgoing.code.cursor,false);
  }
  const {layout:presentedLayout,...otherwiseUnchanged}=frameAt(e,4.7).transition.outgoing;
  assert.equal(presentedLayout,'source-only');
  assert.deepEqual(otherwiseUnchanged,plain.transition.outgoing,
    'outgoing continuation changes only its presentation field');
});

test('a changed source layout keys its whole shot and dependent incoming join, not the distant model',async()=>{
  const defaultEpisode=joined(),opted=joined();opted.shots[1].layout='source-only';
  const plainUnits=outputShotUnits(defaultEpisode,30).units;
  const optedUnits=outputShotUnits(opted,30).units;
  await fingerprintShotUnits(defaultEpisode,plainUnits,'same-common');
  await fingerprintShotUnits(opted,optedUnits,'same-common');
  assert.equal(optedUnits[0].key,plainUnits[0].key,'unaffected first shot remains reusable');
  assert.notEqual(optedUnits[1].key,plainUnits[1].key,'opted source shot changes');
  assert.notEqual(optedUnits[2].key,plainUnits[2].key,'following join depends on outgoing source');
});

test('the dependent join key changes even though its own model request stays unchanged',async()=>{
  const old=joined(),opted=joined();opted.shots[1].layout='source-only';
  const oldUnits=outputShotUnits(old,30).units,newUnits=outputShotUnits(opted,30).units;
  await fingerprintShotUnits(old,oldUnits,'same-common');
  await fingerprintShotUnits(opted,newUnits,'same-common');
  assert.deepEqual(newUnits[2].frames.map(f=>f.request.code),oldUnits[2].frames.map(f=>f.request.code));
  assert.notEqual(newUnits[2].key,oldUnits[2].key,'C has a different outgoing picture dependency');
});
