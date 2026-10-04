// Layer 6 (serial; Chromium, the real viewer; ADR-008, ADR-020): the take
// transport on the machinome-viewer bundle VIDEOMAKER_VIEWER_BUNDLE selects,
// outside the stage, as the player's take surface will use it: the viewer
// mounted directly on the fixture project's committed exports under
// on-demand rendering, as the stage mounts it, and the transport bundled by
// esbuild beside it. The counter's take is fixtures/documents/count.json,
// recorded by the Python side through the framework's simulation; the
// seesaw is a posed loop. Without a selected bundle every test here is
// skipped, "no viewer bundle selected".
import {viewerTest as test,assertViewerApi} from '../support/viewer-bundle.mjs';
import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {join} from 'node:path';
import {sharedStage} from '../support/stage.mjs';
import {transportPage} from '../support/transport-bundle.mjs';
import {FIXTURES,PROJECT} from '../support/fixture-movie.mjs';
import {bankAt} from '../../src/take.mjs';

const OPTIONS={renderMode:'on-demand',animation:'external',autoplay:false,driverControls:'none',partControls:'none',up:[0,0,1],fov:37};
const EXPORTS=join(PROJECT,'export');
// Every file of an export directory, the manifest and what it names, served
// under /export/<name>/.
async function exportFiles(name){
  const files={};
  async function walk(dir,prefix){
    for(const entry of await readdir(dir,{withFileTypes:true})){
      if(entry.isDirectory())await walk(join(dir,entry.name),`${prefix}${entry.name}/`);
      else files[`/export/${name}/${prefix}${entry.name}`]={file:join(dir,entry.name)};
    }
  }
  await walk(join(EXPORTS,name),'');
  return files;
}
// A page of the bundle on an export, mounted at #v, the canvas sized to it.
async function mounted(bundle,name,options){
  const files=await exportFiles(name);
  const {page,close}=await transportPage(await sharedStage(),{viewer:await readFile(bundle,'utf8'),files});
  try{
    const api=await page.evaluate(async([url,options])=>{
      window.viewer=await window.MachinomeViewer.mount('#v',url,options);
      return window.viewer.apiVersion;
    },[`/export/${name}/manifest.json`,options]);
    await page.waitForFunction(()=>{const c=document.querySelector('#v canvas'),b=document.querySelector('#v').getBoundingClientRect();
      if(!c)return false;const r=c.getBoundingClientRect();return Math.abs(r.width-b.width)<=1&&Math.abs(r.height-b.height)<=1;},{},{timeout:30000});
    return {page,close,api};
  }catch(error){await close();throw error;}
}

test('the take transport seeks the counter\'s take on the real viewer: the bank at every mark is the recorded one; one time, another and the first again hold one bank and draw identical pixels',async(t,bundle)=>{
  const doc=JSON.parse(await readFile(join(FIXTURES,'documents','count.json'),'utf8'));
  const {page,close,api}=await mounted(bundle,'counter',{...OPTIONS,view:{camera:[160,-260,140],target:[0,0,20]}});
  try{
    assertViewerApi(bundle,api,29);
    const marks=await page.evaluate(doc=>{
      const take=window.take=window.VideomakerTransport.attachTake(window.viewer,doc),out={};
      for(const {name,time} of take.marks){take.seek(time);out[name]={bank:take.machine.bank(),time:take.time()};}
      return {list:take.marks,duration:take.duration,seeks:out};
    },doc);
    assert.deepEqual(marks.list,[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}]);
    assert.equal(marks.duration,8);
    for(const [name,time] of Object.entries(doc.marks))
      assert.deepEqual(marks.seeks[name],{bank:doc.take.banks[name],time},`the viewer holds the bank the take records at the mark ${name}`);
    const grab=async at=>{
      const bank=await page.evaluate(at=>{window.take.seek(at);return window.take.machine.bank();},at);
      return {bank,png:await page.screenshot()};
    };
    const a1=await grab(3.5),b1=await grab(7),a2=await grab(3.5);
    assert.deepEqual(a1.bank,bankAt(doc,3.5),'the viewer holds the pose rule\'s bank inside step-2');
    assert.deepEqual(b1.bank,bankAt(doc,7),'and inside step-3');
    assert.deepEqual(a2.bank,a1.bank);
    assert.ok(!a1.png.equals(b1.png),'two banks are two pictures');
    assert.ok(a1.png.equals(a2.png),'the first time is drawn identically after the second');
  }finally{await close();}
});

test('the loop transport seeks the seesaw\'s loop on the real viewer: one time, another and the first again draw identical pixels, and a time past the loop is its end',async(t,bundle)=>{
  const {page,close}=await mounted(bundle,'seesaw',{...OPTIONS,time:0,view:{camera:[400,-600,300],target:[0,0,50]}});
  try{
    await page.evaluate(()=>{window.loop=window.VideomakerTransport.attachLoop(window.viewer);});
    const grab=async at=>{await page.evaluate(at=>{window.loop.seek(at);},at);return page.screenshot();};
    const a1=await grab(.2),b1=await grab(.6),a2=await grab(.2);
    assert.ok(!a1.equals(b1),'two loop times are two pictures: setTime drew before it returned');
    assert.ok(a1.equals(a2),'the first time is drawn identically after the second');
    assert.deepEqual(await page.evaluate(()=>{window.loop.seek(3);return [window.loop.time(),window.loop.kind,window.loop.duration,window.loop.machine];}),[1,'loop',1,null]);
  }finally{await close();}
});
