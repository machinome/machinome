import {test,describe} from 'vitest';
import assert from 'node:assert/strict';
import {validateEpisode,episodeFilm} from '../src/episode.mjs';
import {outputShotUnits,fingerprintShotUnits} from '../src/shot-cache.mjs';
import {base02,yamlFrame,element} from './frame-fixtures.mjs';

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

// A source-only shot is the shipped set source-only, its panel in the slot
// source and no view placed (react-stage D3); a code shot without it is the
// paper-split set, the panel at left and the view at right.
test('source-only is a 0.4 code-shot opt-in; omitted layout keeps the split set',()=>{
  const old=episode();assert.doesNotThrow(()=>valid(old));
  const split=yamlFrame(old,2.5);
  assert.equal(split.set,'paper-split');assert.deepEqual(split.slots,{left:'second.code',right:'second.view'});
  const opted=episode();opted.shots[1].layout='source-only';
  assert.doesNotThrow(()=>valid(opted));
  const only=yamlFrame(opted,2.5);
  assert.equal(only.set,'source-only');assert.deepEqual(only.slots,{source:'second.code'});
  assert.equal(element(only,'view'),undefined,'no view is placed');
  assert.deepEqual(element(only,'code'),element(split,'code'),'the panel is the same');
  assert.equal(yamlFrame(opted,.5).set,'paper');
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

test('fractional global-grid requests carry only the opted shot\'s set, including outgoing continuation',()=>{
  const e=joined();valid(e);
  const before=yamlFrame(e,4.7),plain=structuredClone(before);
  assert.equal(element(before.transition.outgoing,'code').text,e.sourceCode.drive.text);
  assert.equal(element(before.transition.outgoing,'code').cursor,false);
  assert.equal(before.transition.outgoing.set,'paper-split');
  e.shots[1].layout='source-only';
  for(const t of [1.15,1.2,4.633333333333334])assert.equal(yamlFrame(e,t).set,'source-only',`incoming at ${t}`);
  for(const t of [4.666666666666667,4.7,4.8]){
    const f=yamlFrame(e,t),out=f.transition.outgoing;
    assert.equal(f.shotId,'return');assert.equal(f.set,'paper');
    assert.equal(out.set,'source-only',`outgoing at ${t}`);
    assert.equal(element(out,'code').text,e.sourceCode.drive.text);
    assert.equal(element(out,'code').cursor,false);
  }
  // The outgoing continuation changes only its set and placement: the same
  // panel, and no view.
  const {set,slots,elements,...otherwiseUnchanged}=yamlFrame(e,4.7).transition.outgoing;
  const {set:_,slots:__,elements:plainElements,...plainRest}=plain.transition.outgoing;
  assert.equal(set,'source-only');assert.deepEqual(slots,{source:'second.code'});
  assert.deepEqual(elements,{'second.code':plainElements['second.code']});
  assert.deepEqual(otherwiseUnchanged,plainRest,'outgoing continuation changes only its presentation');
});

test('a changed source layout keys its whole shot and dependent incoming join, not the distant model',async()=>{
  const defaultEpisode=episodeFilm(joined()),optedEpisode=joined();optedEpisode.shots[1].layout='source-only';
  const opted=episodeFilm(optedEpisode);
  const plainUnits=outputShotUnits(defaultEpisode,30).units;
  const optedUnits=outputShotUnits(opted,30).units;
  await fingerprintShotUnits(defaultEpisode,plainUnits,'same-common');
  await fingerprintShotUnits(opted,optedUnits,'same-common');
  assert.equal(optedUnits[0].key,plainUnits[0].key,'unaffected first shot remains reusable');
  assert.notEqual(optedUnits[1].key,plainUnits[1].key,'opted source shot changes');
  assert.notEqual(optedUnits[2].key,plainUnits[2].key,'following join depends on outgoing source');
});

test('the dependent join key changes even though its own model request stays unchanged',async()=>{
  const optedEpisode=joined();optedEpisode.shots[1].layout='source-only';
  const old=episodeFilm(joined()),opted=episodeFilm(optedEpisode);
  const oldUnits=outputShotUnits(old,30).units,newUnits=outputShotUnits(opted,30).units;
  await fingerprintShotUnits(old,oldUnits,'same-common');
  await fingerprintShotUnits(opted,newUnits,'same-common');
  const own=unit=>unit.frames.map(f=>({set:f.request.set,slots:f.request.slots,elements:f.request.elements}));
  assert.deepEqual(own(newUnits[2]),own(oldUnits[2]),'the join\'s own shot is unchanged');
  assert.notEqual(newUnits[2].key,oldUnits[2].key,'C has a different outgoing picture dependency');
});
