// Layer 5 (serial; Chromium, the viewer double): the take transport on its
// own, outside the stage (the take-transport change; ADR-020), as the
// player's take surface will use it: the transport bundled by esbuild and
// loaded beside the double, whose machine answers the fixture counter's take
// and draws its bank into its canvas, mounted under on-demand rendering as
// the stage mounts it. The take document is fixtures/documents/count.json.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {join} from 'node:path';
import {sharedStage} from '../support/stage.mjs';
import {transportPage} from '../support/transport-bundle.mjs';
import {FIXTURES,takeMachine} from '../support/fixture-movie.mjs';
import {viewerDouble} from '../viewer-double.mjs';
import {bankAt} from '../../src/take.mjs';

const OPTIONS={renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none',
  view:{camera:[160,-260,140],target:[0,0,20]},up:[0,0,1],fov:37};
const theCount=async()=>JSON.parse(await readFile(join(FIXTURES,'documents','count.json'),'utf8'));
// A page with the double and the transport, the take attached as window.take.
async function attached(doc,options={}){
  const {page,close}=await transportPage(await sharedStage(),{viewer:viewerDouble({api:29,parts:'*',...takeMachine(doc.take),...options})});
  await page.evaluate(async([doc,options])=>{
    const viewer=await window.MachinomeViewer.mount('#v','/model/manifest.json',options);
    window.take=window.VideomakerTransport.attachTake(viewer,doc);
  },[doc,OPTIONS]);
  return {page,close};
}

test('a take transport beside the double seeks every mark of the counter\'s take to its recorded bank, by a restore and a redraw',async()=>{
  const doc=await theCount(),{page,close}=await attached(doc);
  try{
    const seen=await page.evaluate(()=>{
      const take=window.take,out={kind:take.kind,duration:take.duration,marks:take.marks,identity:take.machine.identity,
        callsOnAttach:window.viewerCalls?.length??0,seeks:{}};
      for(const {name,time} of take.marks){
        window.viewerCalls.length=0;
        take.seek(time);
        out.seeks[name]={bank:take.machine.bank(),time:take.time(),calls:window.viewerCalls.map(c=>c[0]),restored:window.viewerCalls[0][1]};
      }
      return out;
    });
    assert.deepEqual([seen.kind,seen.duration,seen.identity],['clocked',8,doc.take.identity]);
    assert.deepEqual(seen.marks,[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}]);
    assert.equal(seen.callsOnAttach,0,'attaching poses nothing');
    for(const [name,time] of Object.entries(doc.marks)){
      const s=seen.seeks[name];
      assert.deepEqual(s.bank,doc.take.banks[name],`the bank the machine holds at the mark ${name} is the recorded one`);
      assert.deepEqual(s.restored,doc.take.banks[name]);
      assert.equal(s.time,time);
      assert.deepEqual(s.calls,['restore','setView'],`the mark ${name} is posed by a restore and a redraw, and no loop time is set`);
    }
  }finally{await close();}
});

test('a take transport beside the double poses one time, another and the first again: one bank and identical pixels, the pose rule\'s',async()=>{
  const doc=await theCount(),{page,close}=await attached(doc);
  try{
    const grab=async t=>{
      const bank=await page.evaluate(t=>{window.take.seek(t);return window.take.machine.bank();},t);
      return {bank,png:await page.screenshot()};
    };
    const a1=await grab(3.5),b1=await grab(7),a2=await grab(3.5);
    assert.deepEqual(a1.bank,bankAt(doc,3.5),'inside step-2, the pose rule\'s bank');
    assert.deepEqual(b1.bank,bankAt(doc,7),'inside step-3, the pose rule\'s bank');
    assert.notDeepEqual(a1.bank,b1.bank);
    assert.deepEqual(a2.bank,a1.bank);
    assert.ok(!a1.png.equals(b1.png),'two banks are two pictures');
    assert.ok(a1.png.equals(a2.png),'the first time is drawn identically after the second');
    // Outside the take: its start and its end.
    const clamped=await page.evaluate(()=>{const out=[];for(const t of [-1,9]){window.take.seek(t);out.push([window.take.time(),window.take.machine.bank()]);}return out;});
    assert.deepEqual(clamped,[[0,doc.take.initial],[8,doc.take.banks.ten]]);
  }finally{await close();}
});

test('a take transport refuses a viewer whose machine is not the take\'s, in the stage\'s words, before touching it',async()=>{
  const doc=await theCount(),{page,close}=await transportPage(await sharedStage(),
    {viewer:viewerDouble({api:29,parts:'*',machine:{...takeMachine(doc.take).machine,identity:'another-machine'}})});
  try{
    const refused=await page.evaluate(async([doc,options])=>{
      const viewer=await window.MachinomeViewer.mount('#v','/model/manifest.json',options);
      try{window.VideomakerTransport.attachTake(viewer,doc);return null;}
      catch(error){return {message:error.message,calls:window.viewerCalls.length};}
    },[doc,OPTIONS]);
    assert.deepEqual(refused,{message:`the viewer's machine is another-machine, and the take was recorded on ${doc.take.identity} (take.identity)`,calls:0});
  }finally{await close();}
});
