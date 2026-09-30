import {test} from 'node:test';
import assert from 'node:assert/strict';
import {splitWords,spokenOnsets,evenCount,fadeOpacity,resolveEmphasis,activeEmphasis,resolveWordTiming,validateWordFramesAtFps} from '../src/words.mjs';
import {prepareWordTimingForCommand} from '../src/command-timing.mjs';

const phrase='Propose. Inspect. Correct.';
const spoken='Intro. '+phrase+' Outro.';
const alignment=text=>({characters:Array.from(text),
  character_start_times_seconds:Array.from(text,(_,i)=>i/10),
  character_end_times_seconds:Array.from(text,(_,i)=>(i+1)/10)});
const reveal=(extra={})=>({text:phrase,phrase,narration:spoken,alignment:alignment(spoken),
  replacements:{},offset:.2,from:0,to:7,shotStart:0,fps:30,shotId:'judgment',index:0,...extra});

test('word splitting preserves every separator and source character',()=>{
  for(const source of [phrase,'One line\nAnother line','  A  B\tC  ']){
    const parts=splitWords(source);
    assert.equal(parts.map(p=>p.text).join(''),source);
    assert.deepEqual(parts.filter(p=>p.word).map(p=>p.text),source.match(/\S+/gu)??[]);
  }
  assert.deepEqual(splitWords(phrase).filter(p=>p.word).map(p=>p.text),['Propose.','Inspect.','Correct.']);
});

test('spoken words use cached character onsets, capitalization, punctuation and aliases',()=>{
  const onsets=spokenOnsets(reveal());
  assert.deepEqual(onsets,['Propose.','Inspect.','Correct.'].map(word=>.2+spoken.indexOf(word)/10));
  assert.deepEqual(spokenOnsets(reveal({text:'PROPOSE. INSPECT. CORRECT.'})),onsets);
  const alias='Intro. machine-ohm runs.';
  assert.deepEqual(spokenOnsets(reveal({text:'Machinome',phrase:'Machinome',narration:'Intro. Machinome runs.',
    alignment:alignment(alias),replacements:{Machinome:'machine-ohm'},from:0,to:4})),[.2+alias.indexOf('machine-ohm')/10]);
  const quoted='She said “Propose.”';
  assert.deepEqual(spokenOnsets(reveal({text:'“Propose.”',phrase:'“Propose.”',narration:quoted,
    alignment:alignment(quoted),from:0,to:4})),[.2+quoted.indexOf('Propose')/10]);
});

test('spoken timing refuses ambiguous, mismatched, malformed and unfilmable words',()=>{
  const bad=(extra,pattern)=>assert.throws(()=>spokenOnsets(reveal(extra)),pattern);
  bad({phrase:'Absent'},/phrase.*judgment|judgment.*phrase/i);
  bad({narration:phrase+' '+phrase},/ambiguous|twice/i);
  bad({alignment:alignment('No phrase here')},/spoken phrase|recorded speech/i);
  bad({alignment:alignment(phrase+' '+phrase)},/ambiguous|twice/i);
  bad({text:'Pause. Inspect. Correct.'},/Pause|Propose/);
  bad({text:'Propose. Inspect.'},/word counts differ/i);
  bad({text:'· Propose. Inspect. Correct.'},/·|punctuation/);
  bad({text:'One two',phrase:'One two',narration:'One two',replacements:{'One two':'one-two'},
    alignment:alignment('one-two')},/replacement|two words/i);
  bad({alignment:{...alignment(spoken),character_end_times_seconds:[]}},/alignment/i);
  const negative=alignment(spoken);negative.character_start_times_seconds[3]=-1;
  bad({alignment:negative},/alignment/i);
  const nonfinite=alignment(spoken);nonfinite.character_start_times_seconds[3]=Infinity;
  bad({alignment:nonfinite},/alignment/i);
  const decreasing=alignment(spoken);decreasing.character_start_times_seconds[5]=0;
  bad({alignment:decreasing},/alignment/i);
  const equal=alignment(spoken);equal.character_start_times_seconds.fill(0);
  bad({alignment:equal},/onset|alignment/i);
  bad({from:5},/before|Propose/);
  bad({to:2,shotStart:10.2},/frame|Correct/);
  assert.deepEqual(spokenOnsets(reveal({text:'A',phrase:'A',narration:'A',alignment:alignment('A'),offset:0,
    from:.015,to:.2})),[0]); // less than one 30-fps frame early: starts at cue.from
  bad({text:'A',phrase:'A',narration:'A',alignment:alignment('A'),offset:.07,
    from:.07,to:.08,shotStart:10.2},/global output frame/);
  bad({text:'Propose.',phrase:'Propose.',narration:'Propose.',alignment:alignment('Propose.'),offset:0,
    from:1/30,to:1},/frame or more before|Propose/);
  const ends=alignment(spoken);ends.character_end_times_seconds[5]=0;
  bad({alignment:ends},/alignment/i);
});

test('emphasis follows spoken phrase replacement without replacing identifiers',()=>{
  const source='waterwheel.drives(crankshaft)';
  const written='Machinome: waterwheel drives crankshaft.';
  const spoken='Masheenome: waterwheel drives crankshaft.';
  const cues=resolveEmphasis({source,firstLine:415,line:415,phrase:written,words:['waterwheel','drives','crankshaft'],
    alignment:alignment(spoken),offset:0,hold:0,narration:written,shotId:'source',shotDuration:10,
    replacements:{Machinome:'Masheenome'}});
  assert.equal(cues[0].from,spoken.indexOf('waterwheel')/10);
});

test('an astral source character before a token does not make an already typed word appear untyped',async()=>{
  const source='"😀"; waterwheel';
  const e={audio:{replacements:{}},output:{fps:30},sourceCode:{example:{text:source,lines:[1,1]}},
    shots:[{id:'source',start:0,end:4,narration:'waterwheel',speechOffset:1,
      overlays:[],code:{snippet:'example',typing:[{from:0,to:.1,throughLine:1}],
        emphasis:[{line:1,phrase:'waterwheel',words:['waterwheel'],hold:0}]}}]};
  const timing=await resolveWordTiming(e,async()=>({sha256:'take',alignment:alignment('waterwheel')}));
  assert.equal(timing.source.emphasis[0].cues[0].word,'waterwheel');
});

test('even reveals share eased progress and settle with all words shown',()=>{
  assert.deepEqual([0,.79,.81,1.59,1.61,2.4].map(local=>evenCount(3,local,0,2.4,'linear')),[1,1,2,2,3,3]);
  assert.ok(evenCount(3,.81,0,2.4,'in')<evenCount(3,.81,0,2.4,'linear'));
  assert.equal(evenCount(3,20,0,2.4,'linear'),3);
});

test('a lower render fps refuses words with no delivered frame',()=>{
  const e={output:{fps:30},shots:[{id:'short',start:0,end:1,overlays:[
    {from:.03,to:.15,text:'One Two Three',reveal:{timing:'even',duration:.11}}]}]};
  validateWordFramesAtFps(e,30);
  assert.throws(()=>validateWordFramesAtFps(e,10),/Word.*fps output frame.*short/);
  const together={output:{fps:30},shots:[{id:'together',start:0,end:1,overlays:[
    {from:0,to:.15,text:'One Two Three',reveal:{timing:'even',duration:.12}}]}]};
  validateWordFramesAtFps(together,10); // words two and three may arrive together
});

test('silent build reads measured timing from cache and refuses a missing take without generation',async()=>{
  const make=()=>({audio:{replacements:{}},output:{fps:30},shots:[{id:'hook',start:0,end:1,
    narration:'Hello.',speechOffset:.2,overlays:[{from:0,to:1,text:'Hello.',reveal:{timing:'spoken'}}]}]});
  const cached=make();let reads=0;
  await prepareWordTimingForCommand(cached,{command:'build',silent:true},async()=>{
    reads++;return {sha256:'take',alignment:alignment('Hello.')};});
  assert.equal(reads,1);assert.deepEqual(cached.wordTiming.hook.overlays[0].onsets,[.2]);
  const missing=make();
  await assert.rejects(prepareWordTimingForCommand(missing,{command:'build',silent:true},async()=>{
    throw new Error('Word timing needs cached speech for shot hook; run the speech command first');
  }),/run the speech command first/);
  const narrated=make();
  await prepareWordTimingForCommand(narrated,{command:'build',silent:false},async()=>{throw new Error('narrated build must wait for speech');});
  assert.equal(narrated.wordTiming,undefined);
});

test('a measured onset at a fractional global instant is active, and its clear remains exclusive',()=>{
  const cues=[{word:'wheel',from:2.133,to:5.14}];
  const localOnset=10.133-8,localClear=13.14-8;
  assert.deepEqual(activeEmphasis(cues,localOnset).map(c=>c.word),['wheel']);
  assert.deepEqual(activeEmphasis(cues,localClear),[]);
});

test('a title fade has exact ends and the named easing between them',()=>{
  const cue={from:0,to:4,enter:{kind:'fade',duration:1},leave:{kind:'fade',duration:1}};
  assert.equal(fadeOpacity(cue,0),0);assert.equal(fadeOpacity(cue,.5),.5);
  assert.equal(fadeOpacity(cue,1),1);assert.equal(fadeOpacity(cue,3),1);
  assert.equal(fadeOpacity(cue,3.5),.5);assert.equal(fadeOpacity(cue,4),0);
  assert.equal(fadeOpacity(cue,5),0);
});

test('source emphasis keeps literal token ranges, measured onsets and a common clear',()=>{
  const source='class Mill:\n    water_drive.waterwheel.spin.drives(water_drive.crankshaft.spin)';
  const full='Intro. Here, the waterwheel drives the crankshaft.';
  const cues=resolveEmphasis({source,firstLine:365,line:366,phrase:'Here, the waterwheel drives the crankshaft.',
    words:['waterwheel','drives','crankshaft'],alignment:alignment(full),offset:.8,hold:.9,
    narration:full,shotId:'source',shotDuration:10});
  for(const cue of cues){assert.equal(source.slice(cue.start,cue.end),cue.word);
    assert.equal(cue.from,.8+full.indexOf(cue.word)/10);}
  assert.deepEqual(activeEmphasis(cues,cues[1].from).map(c=>c.word),['waterwheel','drives']);
  assert.deepEqual(activeEmphasis(cues,cues[2].to),[]);
  assert.throws(()=>resolveEmphasis({source,firstLine:365,line:365,phrase:'Here, the waterwheel drives the crankshaft.',
    words:['waterwheel'],alignment:alignment(full),offset:.8,hold:0,narration:full,shotId:'source',shotDuration:10}),/source token|line/i);
});

test('stable emphasis refuses malformed identifiers, source ambiguity, order and late clearing',()=>{
  const source='waterwheel.drives(crankshaft)',narration='waterwheel drives crankshaft';
  const base={source,firstLine:415,line:415,phrase:narration,words:['waterwheel','drives','crankshaft'],
    alignment:alignment(narration),offset:0,hold:0,narration,shotId:'source',shotDuration:10};
  const bad=(change,pattern)=>assert.throws(()=>resolveEmphasis({...base,...change}),pattern);
  bad({line:416},/line/i);bad({words:['waterwhee1']},/source token|spoken token/i);
  bad({phrase:'not spoken'},/phrase/i);bad({phrase:'waterwheel',narration:'waterwheel waterwheel'},/ambiguous/i);
  bad({alignment:{...alignment(narration),character_end_times_seconds:[]}},/alignment/i);
  bad({words:['48.0']},/identifier/i);bad({words:['drives','drives']},/distinct/i);
  bad({words:['crankshaft','drives']},/order/i);
  bad({shotDuration:2},/shot source ends/);
});

test('resolved emphasis refuses a word not typed at onset and overlapping cues',async()=>{
  const text='waterwheel.drives(crankshaft)',phrase='waterwheel drives crankshaft';
  const base=()=>({audio:{replacements:{}},output:{fps:30},sourceCode:{example:{text,lines:[1,1]}},
    shots:[{id:'source',start:0,end:10,narration:phrase,speechOffset:1,overlays:[],
      code:{snippet:'example',typing:[{from:0,to:.1,throughLine:1}],
        emphasis:[{line:1,phrase,words:['waterwheel'],hold:0}]}}]});
  const read=async()=>({sha256:'take',alignment:alignment(phrase)});
  const late=base();late.shots[0].code.typing[0].to=8;
  await assert.rejects(resolveWordTiming(late,read),/not yet typed.*waterwheel|waterwheel.*not yet typed/i);
  const overlap=base();overlap.shots[0].code.emphasis.push({line:1,phrase,words:['drives'],hold:0});
  await assert.rejects(resolveWordTiming(overlap,read),/overlap/i);
});
