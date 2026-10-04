// Layer 6 (serial; Chromium, the real viewer; ADR-008, ADR-022): the player's
// take surface (the player-page change) on the machinome-viewer bundle
// VIDEOMAKER_VIEWER_BUNDLE selects, over a live session on the fixture movie
// `count` in this process: the viewer mounted on the fixture counter's
// committed export by the page itself, with no camera, its own navigator's,
// the take transport attached to the session's /take.json, and each mark of
// the ruler clicked. Without a selected bundle every test here is skipped,
// "no viewer bundle selected".
import {viewerTest as test,assertViewerApi} from '../support/viewer-bundle.mjs';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {sharedStage} from '../support/stage.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {live} from '../../src/live.mjs';

test('the take surface poses the counter\'s take on the real viewer: after each mark is clicked the bank its machine holds is the recorded one',async(t,bundle)=>{
  const log=console.log;console.log=()=>{};t.onTestFinished(()=>{console.log=log;});
  // The bundle declares the API a clocked take needs (its banner, which check reads too).
  const banner=/viewer API (\d+)/.exec((await readFile(bundle,'utf8')).slice(0,2000));
  assertViewerApi(bundle,banner?Number(banner[1]):null,29);
  const {file,document:doc}=await fixtureMovie(t,'count');
  const session=await live(file,{viewer:bundle,width:640});
  t.onTestFinished(()=>session.close());
  const {browser}=await sharedStage();
  const page=await browser.newPage({viewport:{width:1000,height:760},deviceScaleFactor:1});
  t.onTestFinished(()=>page.close());
  const errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(`${session.origin}/#take/take`);
  await page.waitForFunction(()=>window.player?.take(),{},{timeout:60000});
  await page.evaluate(()=>window.player.idle());
  const attached=await page.evaluate(()=>({canvas:document.querySelector('.vm-take-viewer canvas')!==null,
    identity:window.player.take().machine.identity,marks:window.player.take().marks,fault:document.getElementById('fault').hidden?null:document.getElementById('fault').textContent}));
  assert.deepEqual(attached,{canvas:true,identity:doc.take.identity,marks:[{name:'one',time:2},{name:'nine',time:6},{name:'ten',time:8}],fault:null});
  // The viewer fills the surface it is shown on: it styles the element it is
  // mounted in, and the page mounts it in a target that fills its region.
  const sizes=await page.evaluate(()=>{const r=el=>{const b=el.getBoundingClientRect();return [b.width,b.height];};
    return {region:r(document.getElementById('surface')),canvas:r(document.querySelector('.vm-take-viewer canvas'))};});
  assert.ok(sizes.region[1]>300,JSON.stringify(sizes));
  assert.ok(sizes.canvas.every((v,i)=>Math.abs(v-sizes.region[i])<=1),`the canvas fills the take surface: ${JSON.stringify(sizes)}`);
  for(const [name,time] of Object.entries(doc.marks)){
    await page.click(`.vm-flag[data-mark="${name}"]`);
    await page.evaluate(()=>window.player.idle());
    const held=await page.evaluate(()=>({bank:window.player.take().machine.bank(),time:window.player.take().time()}));
    assert.deepEqual(held,{bank:doc.take.banks[name],time},`the viewer holds the bank the take records at the mark ${name}`);
  }
  assert.deepEqual(errors,[]);
});
