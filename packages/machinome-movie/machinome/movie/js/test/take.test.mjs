// Layer 3 (pure): a clocked take on the timeline (the pose-a-take change,
// ADR-012). The bank at a take time is the contract's rule
// (docs/movie-document.md, "The take"): the bank before the step, its input
// interpolated along the recorded path, every commit up to the fraction
// written. The replay holds a document's banks to its steps; a view on a take
// carries the bank of its take time and no loop time. Inline takes and the
// shared fixture `count`; no DOM, no browser.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join,dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {bankAt,replayTake,checkTakeBanks,takeLine,markAt,markSteps} from '../src/take.mjs';
import {checkMovie,checkProject,resolveMovie,movieViewerApi,excerptSources} from '../src/movie.mjs';
import {frameAt,filmShots,modelSecondsAt} from '../src/timeline.mjs';

const fixtures=join(dirname(fileURLToPath(import.meta.url)),'..','fixtures');
const json=async file=>JSON.parse(await readFile(file,'utf8'));
const refusal=fn=>{try{fn();}catch(error){return error.message;}assert.fail('was not refused');};
const refusedNaming=(fn,words)=>{
  const message=refusal(fn);
  for(const word of words)assert.ok(message.includes(word),`refusal "${message}" does not name "${word}"`);
};

// A take of three steps on a machine with two inputs and two states: a move
// with two commits, a move with none whose path ends where the arithmetic
// misses its end by a bit, and a move whose only commit is at fraction 0.
const TAKE={kind:'clocked',identity:'machine',
  initial:{crank:0,slide:0.7,low:0,high:0},
  steps:[
    {id:'step-1',at:0,duration:2,input:'crank',by:360,origin:0,end:360,admitted:360,stops:[],
      commits:[{fraction:.25,value:90,targets:{low:1,high:0},relations:['r']},{fraction:.75,value:270,targets:{low:2,high:0},relations:['r']}]},
    {id:'step-2',at:2,duration:1,input:'slide',to:.1,origin:.7,end:.1,admitted:-.6,stops:[],commits:[]},
    {id:'step-3',at:3,duration:2,input:'crank',by:360,origin:360,end:720,admitted:360,stops:[],
      commits:[{fraction:0,value:360,targets:{low:2,high:1},relations:['r']}]},
  ],
  banks:{}};
// The document the take belongs to: the pose rule reads the last step's end
// as the take's length.
const DOC={model:{expectedDurationSeconds:5,timeMode:'take'},take:TAKE};
const bank=(over={})=>({crank:0,slide:.7,low:0,high:0,...over});

// Steps of 1.2 s as Python writes them (exact-take-times, ADR-016): each `at`
// the exact decimal sum of the durations before it, the marks and the length
// likewise. Summed in floats the third step ends at 3.5999999999999996, and
// (4.8 − 3.6) / 1.2 is 0.9999999999999998 (finding 7 of the Curta film).
const decimalStep=(i,commits=[])=>({id:`step-${i+1}`,at:[0,1.2,2.4,3.6][i],duration:1.2,input:'crank',by:360,
  origin:360*i,end:360*(i+1),admitted:360,stops:[],commits});
const decimal=(count,length,marks)=>({model:{expectedDurationSeconds:length,timeMode:'take'},marks,
  take:{kind:'clocked',identity:'machine',initial:{crank:0,flag:0},
    steps:[decimalStep(0),decimalStep(1),decimalStep(2),
      decimalStep(3,[{fraction:0,value:1080,targets:{flag:1},relations:['r']}])].slice(0,count),
    banks:Object.fromEntries(Object.keys(marks).map((name,i)=>[name,{crank:360*(i+1),flag:i===3?1:0}]))}});
const FOUR=decimal(4,4.8,{first:1.2,second:2.4,third:3.6,fourth:4.8});
const THREE=decimal(3,3.6,{first:1.2,second:2.4,third:3.6});

test('inside a step the input runs along its path and the commits up to the fraction are written',()=>{
  // step-1 at f = 0.5: crank half-way, the commit at 0.25 written, the one at 0.75 not.
  assert.deepEqual(bankAt(DOC,1),bank({crank:180,low:1}));
  // A commit exactly at the fraction is written.
  assert.deepEqual(bankAt(DOC,.5),bank({crank:90,low:1}));
  assert.deepEqual(bankAt(DOC,.49),bank({crank:.49/2*360}));
  // Two commits of one step, both behind the fraction.
  assert.deepEqual(bankAt(DOC,1.5),bank({crank:270,low:2}));
});

test('a step with no commit moves only its input',()=>{
  // step-2 at f = 0.5: the slide half-way from 0.7 to 0.1; the states stay.
  const half=bankAt(DOC,2.5);
  assert.deepEqual(Object.keys(half),['crank','slide','low','high']);
  assert.deepEqual({...half,slide:undefined},{...bank({crank:360,low:2}),slide:undefined});
  assert.equal(half.slide,.7+.5*(.1-.7));
});

test('a step owns its end: its input is exactly the end there, and the next step\'s commit at fraction 0 waits',()=>{
  // 0.7 + 1·(0.1 − 0.7) is 0.09999999999999998; the rule says the end.
  assert.notEqual(.7+1*(.1-.7),.1);
  assert.ok(Object.is(bankAt(DOC,3).slide,.1));
  // At 3 s step-2 has ended and step-3 has not begun: its commit at fraction
  // 0 is not written until the instant after.
  assert.deepEqual(bankAt(DOC,3),bank({crank:360,slide:.1,low:2}));
  assert.deepEqual(bankAt(DOC,3.000001).high,1);
});

test('at 0 and before, the initial bank; at the take\'s end and after, the bank the last step ended with',()=>{
  assert.deepEqual(bankAt(DOC,0),TAKE.initial);
  assert.deepEqual(bankAt(DOC,-1),TAKE.initial);
  const last=bank({crank:720,slide:.1,low:2,high:1});
  assert.deepEqual(bankAt(DOC,5),last);
  assert.deepEqual(bankAt(DOC,9),last);
  assert.notEqual(bankAt(DOC,0),TAKE.initial,'a fresh bank, never the document\'s own object');
});

test('the same take time twice gives the same bank, in the initial bank\'s order',()=>{
  for(const t of [0,.5,1.25,2.7,3,4.2,5]){
    assert.equal(JSON.stringify(bankAt(DOC,t)),JSON.stringify(bankAt(structuredClone(DOC),t)));
    assert.deepEqual(Object.keys(bankAt(DOC,t)),Object.keys(TAKE.initial));
  }
});

test('the replay gives the bank before and after every step',()=>{
  const {before,after}=replayTake(TAKE);
  assert.deepEqual(before,[TAKE.initial,bank({crank:360,low:2}),bank({crank:360,slide:.1,low:2})]);
  assert.deepEqual(after,[bank({crank:360,low:2}),bank({crank:360,slide:.1,low:2}),bank({crank:720,slide:.1,low:2,high:1})]);
});

test('a step of decimal seconds owns its written end: at the mark 3.6 the third step\'s bank, the fourth step\'s commit at fraction 0 still waiting',()=>{
  assert.notEqual(2.4+1.2,3.6);
  assert.deepEqual(bankAt(FOUR,3.6),{crank:1080,flag:0});
  assert.deepEqual(bankAt(FOUR,3.6),FOUR.take.banks.third);
  assert.equal(bankAt(FOUR,3.7).flag,1);
});

test('at the take\'s written length the last step has ended: its input is exactly its end',()=>{
  assert.notEqual((4.8-3.6)/1.2,1);
  assert.deepEqual(bankAt(FOUR,4.8),FOUR.take.banks.fourth);
  assert.deepEqual(bankAt(THREE,3.6),THREE.take.banks.third);
});

test('a mark is found at its step\'s written end, and a mark summed in floats is refused naming it',()=>{
  assert.deepEqual(markSteps(FOUR),{first:0,second:1,third:2,fourth:3});
  checkTakeBanks(FOUR);
  const floats=structuredClone(THREE);floats.marks.third=2.4+1.2;
  refusedNaming(()=>markSteps(floats),['marks.third','end of a step']);
});

test('a frame is on a mark only at the mark\'s take time exactly',()=>{
  assert.equal(markAt(FOUR,3.6),'third');
  assert.equal(markAt(FOUR,0),null);
  // A hair off the mark is posed inside a step by the pose rule, not on the
  // mark's recorded bank: just after it, the fourth step's commit at
  // fraction 0 is written.
  for(const t of [3.6+4.440892098500626e-16,2.4+1.2])assert.equal(markAt(FOUR,t),null,`${t} is not the mark third`);
  assert.notDeepEqual(bankAt(FOUR,3.6+4.440892098500626e-16),FOUR.take.banks.third);
});

test('check\'s take line gives the marks and the length as the document writes them',()=>{
  assert.equal(takeLine(THREE),'Take: 3 steps, marks first 1.2 s, second 2.4 s, third 3.6 s, 3.6 s long; the replay of its steps gives the recorded bank at every mark');
});

test('a take document whose steps, length or marks were summed in floats is refused naming the field',async()=>{
  const {doc}=await count();
  const decimals=d=>{
    d.take.steps.forEach((step,i)=>{step.at=[0,1.2,2.4][i];step.duration=1.2;});
    d.model.expectedDurationSeconds=3.6;d.marks={one:1.2,nine:2.4,ten:3.6};
    return d;
  };
  checkMovie(decimals(structuredClone(doc)));
  const at=decimals(structuredClone(doc));at.take.steps[2].at=1.2+1.2+1e-15;
  refusedNaming(()=>checkMovie(at),['take.steps[2]','step-3','at']);
  const length=decimals(structuredClone(doc));length.model.expectedDurationSeconds=2.4+1.2;
  refusedNaming(()=>checkMovie(length),['model.expectedDurationSeconds','take']);
  const mark=decimals(structuredClone(doc));mark.marks.ten=2.4+1.2;
  refusedNaming(()=>checkMovie(mark),['marks.ten','end of a step']);
});

const count=async()=>{
  const doc=await json(join(fixtures,'documents','count.json'));
  const takes={counting:await json(join(fixtures,'takes','count','counting.json'))};
  return {doc,takes};
};

test('the recorded banks of the counter are its replay at every mark; a forged one is refused naming the mark and the id',async()=>{
  const {doc}=await count();
  checkTakeBanks(doc);
  const {after}=replayTake(doc.take);
  assert.deepEqual([after[0],after[1],after[2]],[doc.take.banks.one,doc.take.banks.nine,doc.take.banks.ten]);
  doc.take.banks.nine.units=8;
  refusedNaming(()=>checkTakeBanks(doc),['take.banks.nine','nine','units']);
  refusedNaming(()=>checkMovie(doc),['take.banks.nine','nine','units']);
});

test('a view on the counter carries the bank of its take time and no loop time',async()=>{
  const {doc,takes}=await count(),film=resolveMovie(doc,takes);
  // The source panel beside the view in carry reads its excerpt, as a load attaches it.
  const text=(await excerptSources(doc,resolve(fixtures,'documents',doc.root))).relations;
  film.excerpts={relations:{file:'models/counter.py',lines:doc.sourceCode.relations.lines,text}};
  const shot=id=>filmShots(film).find(s=>s.shot.id===id).shot;
  // nine starts at the mark one; carry at the mark nine.
  for(const [id,mark] of [['nine','one'],['carry','nine']]){
    const view=frameAt(film,shot(id).start).elements['counting.view'];
    assert.deepEqual(view.bank,doc.take.banks[mark],`${id} starts on the bank of ${mark}`);
    assert.ok(!Object.hasOwn(view,'time'),'a view on a take has no loop time');
  }
  // Half-way through once (take time 0 to 2 over the shot): step-1 at f = 0.5.
  const once=shot('once'),middle=(once.start+once.end)/2;
  const seconds=2*(middle-once.start)/(once.end-once.start);
  assert.deepEqual(frameAt(film,middle).elements['counting.view'].bank,bankAt(doc,seconds));
  assert.deepEqual(frameAt(film,middle),frameAt(film,middle),'the same instant twice');
});

test('check\'s take line gives the steps, the marks, the length and the replay',async()=>{
  const {doc}=await count();
  assert.equal(takeLine(doc),'Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark');
});

test('the load films a take on a clocked export, and refuses a clocked export filmed as a loop and a running program',async()=>{
  const {doc,takes}=await count(),film=resolveMovie(doc,takes);
  const manifest=await json(resolve(fixtures,'documents',doc.root,doc.model.manifest));
  assert.ok(manifest.clocked&&!manifest.animation.loop);
  checkProject(structuredClone(film),manifest);
  // The counter's export filmed as a loop of 8 s.
  const loop=structuredClone(film);loop.model.timeMode='normalized-loop';delete loop.take;
  refusedNaming(()=>checkProject(loop,{...manifest,animation:{...manifest.animation,loop:8}}),['model.timeMode','clocked']);
  // A running machine, either way.
  for(const f of [structuredClone(film),loop])
    refusedNaming(()=>checkProject(f,{...manifest,program:{}}),['program','running machine is not filmable']);
  // The seesaw's loop is filmed as before.
  const tour=await json(join(fixtures,'resolved','tour.json'));
  checkProject(tour,{animation:{loop:20}});
});

test('a movie on a take needs Viewer API 29, its first reason the clocked take',async()=>{
  const {doc,takes}=await count();
  assert.deepEqual(movieViewerApi(resolveMovie(doc,takes)),{api:29,reasons:['clocked take','highlight (shot carry)']});
});

// A continuation that crosses a mark (the check-the-continuation change,
// ADR-014; finding 3 of the Curta film): while a join still shows the
// outgoing shot, its take time runs on at the rate it ended with; a mark it
// runs past, into the step after it, is recorded on the shot's model and
// reported. The counter's nine ends on the mark nine at 6 s still moving
// (4 take seconds over 2.1 s) and dissolves for 0.5 s into carry at 10 fps.
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
const variant=async change=>{const {doc,takes}=await count();change(doc,Object.fromEntries(doc.chapters[0].shots.map(s=>[s.id,s])));return resolveMovie(doc,takes);};
const crossings=film=>filmShots(film).filter(({shot})=>shot.model.crossing).map(({shot})=>shot.id);
// The take time the join's last frame poses of the outgoing shot: the frames
// n / fps from the incoming shot's start while the join shows it, as
// transitionAt decides: a dissolve while t < start + duration, a fade while
// 2u / duration < 1.
const lastPosed=(film,outgoing,incoming,shows)=>{
  const fps=film.output.fps,d=outgoing.end-outgoing.start;let seconds=null;
  for(let n=Math.ceil(incoming.start*fps-1e-9);n/fps<incoming.end;n++){
    const t=n/fps,u=t-incoming.start;if(!shows(t,u))break;seconds=modelSecondsAt(outgoing,d+u);
  }
  return seconds;
};

test('the counter\'s nine runs past the mark nine into step-3 during its dissolve, and its resolved model records it',async()=>{
  const {doc,takes}=await count(),film=resolveMovie(doc,takes);
  const nine=shotOf(film,'nine'),carry=shotOf(film,'carry');
  const reaches=lastPosed(film,nine,carry,t=>t<carry.start+.5);
  assert.equal(reaches.toFixed(2),'6.76');
  assert.deepEqual(nine.model.crossing,{join:'dissolve',duration:.5,into:'carry',mark:'nine',step:'step-3',reaches,past:reaches-6,
    report:'Continuation: shot nine runs on through the 0.5 s dissolve into shot carry and crosses the mark nine: its last frame there poses take time 6.76 s, 0.76 s past the mark, inside step-3, which moves crank by 360; hold the shot at the mark before it ends, or ease its model to rest there'});
  // Only the shot whose continuation crosses: once is cut, carry is the last.
  assert.deepEqual(crossings(film),['nine']);
  assert.deepEqual(resolveMovie(doc,takes),film,'resolved twice, identically');
});

test('the take time a crossing records is the one the join\'s last frame poses for the outgoing view',async()=>{
  const {doc,takes}=await count(),film=resolveMovie(doc,takes);
  const text=(await excerptSources(doc,resolve(fixtures,'documents',doc.root))).relations;
  film.excerpts={relations:{file:'models/counter.py',lines:doc.sourceCode.relations.lines,text}};
  const nine=shotOf(film,'nine'),carry=shotOf(film,'carry'),fps=film.output.fps;
  // Every frame from carry's start: the outgoing view's bank while the join
  // shows nine, then none; the last such bank is the bank at what is recorded.
  let last=null,shown=0;
  for(let n=Math.round(carry.start*fps);n<Math.round(carry.end*fps);n++){
    const t=n/fps,outgoing=frameAt(film,t).transition?.outgoing;
    if(!outgoing)break;
    last=outgoing.elements['counting.view'].bank;shown++;
    assert.deepEqual(last,bankAt(doc,modelSecondsAt(nine,nine.end-nine.start+(t-carry.start))),`the rule's take time at ${t} s`);
  }
  assert.equal(shown,5,'the dissolve shows nine on five frames at 10 fps');
  assert.deepEqual(last,bankAt(doc,nine.model.crossing.reaches));
  assert.notDeepEqual(last,doc.take.banks.nine,'past the mark, the take is inside step-3');
});

test('a shot held at the mark, or eased to rest on it, crosses nothing',async()=>{
  const held=await variant((doc,shots)=>{
    shots.nine.model={keys:[{at:0,seconds:{mark:'one'}},{at:1,seconds:{mark:'nine'}},{at:shots.nine.until,seconds:{mark:'nine'}}]};
  });
  assert.deepEqual(crossings(held),[]);
  assert.ok(!Object.hasOwn(shotOf(held,'nine').model,'crossing'));
  const eased=await variant((doc,shots)=>{
    shots.nine.model={keys:[{at:0,seconds:{mark:'one'}},{at:shots.nine.until,seconds:{mark:'nine'},ease:'out'}]};
  });
  assert.deepEqual(crossings(eased),[]);
});

test('a step boundary that is not a mark is not reported',async()=>{
  const film=await variant((doc,shots)=>{
    delete doc.marks.nine;delete doc.take.banks.nine;
    shots.nine.model.to=6;shots.carry.model.from=6;
  });
  assert.deepEqual(crossings(film),[]);
});

test('a shot that ends before a mark and runs past it crosses it; a fade follows only its first half',async()=>{
  const before=await variant((doc,shots)=>{shots.nine.model.to=5.5;});
  const nine=shotOf(before,'nine'),carry=shotOf(before,'carry');
  const reaches=lastPosed(before,nine,carry,t=>t<carry.start+.5);
  assert.ok(reaches>6);
  assert.deepEqual({...nine.model.crossing,report:undefined},{join:'dissolve',duration:.5,into:'carry',mark:'nine',step:'step-3',reaches,past:reaches-6,report:undefined});
  // Through a fade the outgoing shot is shown for its first half only
  // (u < 0.25): 5.5 s plus a fifth of a second at 5/3 take seconds per
  // second stays short of the mark.
  const fade=await variant((doc,shots)=>{shots.nine.model.to=5.5;shots.carry.transition={kind:'fade',duration:.5};});
  assert.deepEqual(crossings(fade),[]);
  const onMark=await variant((doc,shots)=>{shots.carry.transition={kind:'fade',duration:.5};});
  const crossing=shotOf(onMark,'nine').model.crossing;
  assert.equal(crossing.reaches,lastPosed(onMark,shotOf(onMark,'nine'),shotOf(onMark,'carry'),(t,u)=>2*u/.5<1));
  assert.match(crossing.report,/^Continuation: shot nine runs on through the 0\.5 s fade into shot carry and crosses the mark nine: its last frame there poses take time 6\.38 s, 0\.38 s past the mark, inside step-3/);
});

test('a step is named by its input and where it moves it; crossings are reported in film order',async()=>{
  const film=await variant((doc,shots)=>{shots.nine.transition={kind:'dissolve',duration:.5};});
  assert.deepEqual(crossings(film),['once','nine']);
  const once=shotOf(film,'once').model.crossing;
  assert.equal(once.mark,'one');assert.equal(once.step,'step-2');
  assert.match(once.report,/^Continuation: shot once runs on through the 0\.5 s dissolve into shot nine and crosses the mark one: .* inside step-2, which moves crank to 3240; hold the shot at the mark before it ends, or ease its model to rest there$/);
});

test('a continuation that would leave the take is still refused with its words, and reports nothing',async()=>{
  const {doc,takes}=await count(),nine=doc.chapters[0].shots[1];
  nine.model.to={mark:'ten'};
  refusedNaming(()=>resolveMovie(doc,takes),['Shot nine cannot continue 0.5 s into the dissolve to shot carry','past the export\'s 8 s','end its model earlier or shorten the transition']);
});
