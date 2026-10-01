// Layer 5 (serial; Chromium, the viewer double): a clocked take on the stage
// (the pose-a-take change, ADR-012), on the fixture movie `count`, whose view
// films the counter's take. The double's machine answers the take's own
// requests, or a table a test forges, and draws its bank into its canvas.
// Every proof reads what window.film.setFrame reports, the double's calls and
// the pixels.
import {afterAll} from 'vitest';
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {rm,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {browserSession} from '../support/stage.mjs';
import {fixtureMovie,takeMachine} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {frameAt,filmShots} from '../../src/timeline.mjs';
import {viewerDouble} from '../viewer-double.mjs';
import {assertMarkFollowsTheBank} from '../support/mark-on-a-take.mjs';

let count=null;
const cleanup=[];
afterAll(async()=>{for(const dir of cleanup)await rm(dir,{recursive:true,force:true});});
async function theCount(){
  return count??=(async()=>{
    const movie=await fixtureMovie({onTestFinished(){}},'count');
    if(!process.env.KEEP_VIDEOMAKER_TEST)cleanup.push(movie.dir);
    const film=await loadEpisode(movie.file);
    const double=async(name,options)=>{const file=join(movie.dir,name);
      await writeFile(file,`// machinome-viewer double, viewer API ${options?.api??29}\n${viewerDouble({parts:'*',tintHighlight:true,api:29,...options})}`);return file;};
    return {...movie,film,double};
  })();
}
const WIDTH=640,VIEW='counting.view';
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
const middle=(film,id)=>{const shot=shotOf(film,id);return (shot.start+shot.end)/2;};

test('every view on the take is restored to its frame\'s bank, never given a loop time, and reports the bank it holds',async()=>{
  const {film,viewer}=await theCount();
  const instants=[shotOf(film,'once').start,middle(film,'once'),shotOf(film,'nine').start,middle(film,'nine'),middle(film,'carry')];
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    await page.evaluate(()=>{window.viewerCalls.length=0;});
    const out=[];for(const t of instants)out.push(await pose(t,{transition:null}));
    return {result:{out,calls:await page.evaluate(()=>window.viewerCalls)}};
  });
  const {out,calls}=seen.result;
  for(const f of out){
    const state=f.elements[VIEW];
    assert.ok(state.bank&&!Object.hasOwn(state,'time'),'the frame gives the view a bank and no loop time');
    assert.deepEqual(f.observed.elements[VIEW].bank,state.bank,`the bank reported at ${f.time} s is the frame's`);
  }
  assert.deepEqual(out.map(f=>f.elements[VIEW].bank.units),[0,0,1,5,9],'the units drum through the take');
  assert.ok(!calls.some(c=>c[0]==='setTime'),'no loop time is set on a view on a take');
  const restores=calls.map((c,i)=>[c[0],i]).filter(([name])=>name==='restore');
  assert.equal(restores.length,instants.length,'one restore per pose');
  for(const [,i] of restores)assert.equal(calls[i+1][0],'setView','the camera is set after the bank');
  // The replay of the take on the viewer ran before the first frame and matched.
  assert.deepEqual(seen.takeReplay,{steps:3,matched:true});
});

test('posing one bank, then another, then the first gives identical pixels; a mark poses its recorded bank',async()=>{
  const {film,viewer,document:doc}=await theCount();
  const a=middle(film,'nine'),b=shotOf(film,'nine').start;
  assert.notDeepEqual(frameAt(film,a).elements[VIEW].bank,frameAt(film,b).elements[VIEW].bank);
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const grab=async t=>{const f=await pose(t,{transition:null});return {png:await page.screenshot(),bank:f.observed.elements[VIEW].bank};};
    const a1=await grab(a),b1=await grab(b),a2=await grab(a);
    return {result:{a1,b1,a2}};
  });
  const {a1,b1,a2}=seen.result;
  assert.ok(!a1.png.equals(b1.png),'two banks are two pictures');
  assert.ok(a1.png.equals(a2.png),'the first bank is drawn identically after the second');
  // nine begins at the mark one.
  assert.deepEqual(b1.bank,doc.take.banks.one);
});

test('a ring on the units drum follows it from the take\'s start to the mark one, and back (the assertion layer 6 makes)',async()=>{
  const {film,viewer}=await theCount();
  await assertMarkFollowsTheBank(film,viewer);
});

test('a double whose machine follows no input, or one its bank does not hold, is refused at mount, naming it',async()=>{
  const {film,double,document:doc}=await theCount();
  const first=shotOf(film,'once').start,session=file=>browserSession(film,file,WIDTH,[],async({pose})=>{await pose(first);});
  const {follows:_,...still}=takeMachine(doc.take).machine;
  await assert.rejects(session(await double('follows-nothing.js',{machine:still})),
    /the double's machine follows no input; name one of crank, tens, units in machine\.follows/);
  await assert.rejects(session(await double('follows-crank-arm.js',{machine:{...still,follows:{input:'crank_arm',range:[0,360]}}})),
    /the double's machine follows crank_arm, which its bank does not hold \(crank, tens, units\)/);
});

test('a viewer below API 29, without a machine, or with another machine is refused at mount, naming the view',async()=>{
  const {film,double,document:doc}=await theCount();
  const first=shotOf(film,'once').start,session=file=>browserSession(film,file,WIDTH,[],async({pose})=>{await pose(first);});
  await assert.rejects(session(await double('api-28.js',{api:28,...takeMachine(doc.take)})),
    /This movie needs Viewer API 29 for clocked take, highlight \(shot carry\); the selected viewer declares API 28/);
  await assert.rejects(session(await double('no-machine.js',{})),
    /View counting\.view in shot once: the viewer gives no machine for this clocked document/);
  const other={...takeMachine(doc.take).machine,identity:'another-machine'};
  await assert.rejects(session(await double('another-machine.js',{machine:other})),
    new RegExp(`View counting\\.view in shot once: the viewer's machine is another-machine, and the take was recorded on ${doc.take.identity} \\(take\\.identity\\)`));
});

test('a viewer that answers a step otherwise than the take is refused before the first frame, naming the step and the field',async()=>{
  const {film,double,document:doc}=await theCount();
  const forged=structuredClone(doc.take.steps);forged[1].commits[0].targets.units=7;
  const file=await double('forged.js',{machine:{...takeMachine(doc.take).machine,requests:forged}});
  let posed=0;
  await assert.rejects(browserSession(film,file,WIDTH,[],async({pose})=>{posed++;await pose(shotOf(film,'once').start);}),
    /The viewer does not reproduce the take: step step-2 \(take\.steps\[1\]\), commits\[0\]\.targets\.units: the viewer gives 7, the take records 2/);
  assert.equal(posed,0,'refused before the session\'s first frame');
  // Another origin, another number of commits.
  const shifted=structuredClone(doc.take.steps);shifted[2].commits.push({...shifted[2].commits[0],fraction:1});
  await assert.rejects(browserSession(film,await double('extra-commit.js',{machine:{...takeMachine(doc.take).machine,requests:shifted}}),
    WIDTH,[],async()=>{}),/step step-3 \(take\.steps\[2\]\), commits: the viewer gives 2 commits, the take records 1/);
});

test('a view whose bank differs from the frame\'s is refused naming the view, the time and the id; at a mark, naming the mark',async()=>{
  const {film,viewer,document:doc}=await theCount();
  const start=shotOf(film,'nine').start,inside=middle(film,'once');
  // The frame asks for one bank; the stage is handed another: the renderer's
  // check compares what the viewer holds with the frame, and with the take at a mark.
  const seen=await browserSession(film,viewer,WIDTH,[],async({pose})=>{
    const out={};
    const wrong=t=>{const state=frameAt(film,t).elements[VIEW];return {elements:{[VIEW]:{...state,bank:{...state.bank,units:4}}}};};
    for(const [name,t] of [['inside',inside],['mark',start]]){
      try{await pose(t,wrong(t));out[name]=null;}catch(error){out[name]=error.message;}
    }
    return {result:out};
  });
  // The stage restored what it was handed, so the frame it was posed from
  // and the bank it reports agree; the take does not.
  assert.equal(seen.result.inside,null,'inside a step a frame is held to itself');
  assert.match(seen.result.mark,new RegExp(`^Viewer bank differs from the take at mark one: counting\\.view in nine at ${start.toFixed(2)} s, units: the viewer holds 4, the take records 1$`));
  assert.equal(doc.take.banks.one.units,1);
  // A machine that holds another bank than the one restored on it is refused
  // at the session's first pose, the film's first frame.
  const {double}=await theCount();
  const skewed=await double('skewed.js',{machine:{...takeMachine(doc.take).machine,skew:{tens:3}}});
  await assert.rejects(browserSession(film,skewed,WIDTH,[],async({pose})=>{await pose(inside,{transition:null});}),
    /Viewer bank differs from the frame: counting\.view in once at 0\.00 s, tens: the viewer holds 3, the frame asks for 0/);
});
