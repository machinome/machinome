// Layer 5 harness (serial; Chromium, the viewer double): within one run,
// Chromium is launched once and one asset server serves every browser test,
// while the command line keeps launching its own (ADR-003). Launches are
// counted by test/support/one-browser.mjs.
import assert from 'node:assert/strict';
import {mkdtemp,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {get} from 'node:http';
import * as renderer from '../src/render.mjs';
import {slowTest as test} from './support/memo.mjs';
import {sharedStage,launches,allowLaunches} from './support/stage.mjs';
import {viewerDouble} from './viewer-double.mjs';

async function fixture(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-browser-seam-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  await writeFile(join(dir,'manifest.json'),JSON.stringify({root:{name:'test'},animation:{loop:2}}));
  const viewer=join(dir,'viewer.js');await writeFile(viewer,viewerDouble());
  const e={format:'machinome-video-draft/0.4',title:'Seam',series:'SEAM',output:{width:320,height:180,fps:2,durationSeconds:1},
    model:{expectedDurationSeconds:2},style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
    paths:{repository:dir,episode:join(dir,'episode.yaml'),production:join(dir,'production.yaml'),manifest:join(dir,'manifest.json'),build:join(dir,'_build')},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    shots:[{id:'only',start:0,end:1,narration:'',direction:'Look.',simulation:{from:0,to:1},camera:[{at:0,preset:'a'}],
      hiddenLayers:[],overlays:[],evidence:[]}]};
  return {e,viewer};
}
// A loopback request to the asset server: status and body.
const ask=url=>new Promise((resolve,reject)=>get(url,res=>{let body='';res.on('data',c=>body+=c);res.on('end',()=>resolve({status:res.statusCode,body}));}).on('error',reject));
const look=async({page})=>({origin:new URL(page.url()).origin,owner:page.context().browser()});

test('two sessions on the shared browser launch nothing, share one asset server and leave the browser open',async t=>{
  const {e,viewer}=await fixture(t),{browser,assets}=await sharedStage(),before=launches();
  const first=await renderer.browserSession(e,viewer,320,[],look,{browser,assets});
  const second=await renderer.browserSession(e,viewer,320,[],look,{browser,assets});
  assert.equal(launches()-before,0,'no Chromium launched');
  assert.equal(first.origin,assets.origin);assert.equal(second.origin,assets.origin);
  assert.equal(first.owner,browser);assert.equal(second.owner,browser);
  assert.ok(browser.isConnected(),'the shared browser stays open for the next test');
  assert.equal(browser.contexts().length,0,'each session closed its own page and context');
});

test('a session given no browser launches exactly one Chromium and closes it, as the command line does',async t=>{
  const {e,viewer}=await fixture(t),before=launches();
  allowLaunches(1);
  const seen=await renderer.browserSession(e,viewer,320,[],look);
  assert.equal(launches()-before,1,'exactly one Chromium launched');
  assert.ok(!seen.owner.isConnected(),'and closed after the session');
  assert.notEqual(seen.origin,(await sharedStage()).assets.origin,'with its own asset server');
});

test('the asset server serves one session at a time and refuses a second by name',async()=>{
  const assets=await renderer.assetServer();
  try{
    const release=assets.mount((req,res)=>res.end('first'));
    assert.throws(()=>assets.mount((req,res)=>res.end('second')),/^Error: The asset server at http:\/\/127\.0\.0\.1:\d+ already serves a film session$/);
    assert.equal((await ask(assets.origin+'/')).body,'first');
    release();
    assert.equal((await ask(assets.origin+'/')).status,503,'between sessions it serves nothing');
    const again=assets.mount((req,res)=>res.end('second'));
    assert.equal((await ask(assets.origin+'/')).body,'second');
    again();
  }finally{await assets.close();}
});
