// Layer 5 (serial; Chromium, the viewer double): the reframe in a browser
// (the reframe-join change, ADR-010), on the fixture tour, whose `question`
// comes in from `hook` by Reframe(0.8): `opening.wide` moves from Playbill's
// `stage` to PlaybillSplit's `right`, the tally and the title fade in. The
// session measures the two slots' boxes on its own page before its first
// frame; every proof reads what window.film.setFrame reports and the pixels.
import {afterAll} from 'vitest';
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {rm,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {performance} from 'node:perf_hooks';
import {browserSession} from '../support/stage.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {filmShots,reframeAt} from '../../src/timeline.mjs';
import {ease} from '../../src/easing.mjs';
import {viewerDouble} from '../viewer-double.mjs';

let tour=null;
const cleanup=[];
afterAll(async()=>{for(const dir of cleanup)await rm(dir,{recursive:true,force:true});});
async function theTour(){
  return tour??=(async()=>{
    const movie=await fixtureMovie({onTestFinished(){}},'tour');
    if(!process.env.KEEP_VIDEOMAKER_TEST)cleanup.push(movie.dir);
    const film=await loadEpisode(movie.file);
    const double=async(name,options)=>{const file=join(movie.dir,name);
      await writeFile(file,`// machinome-viewer double, viewer API ${options?.api??28}\n${viewerDouble({parts:'*',tintHighlight:true,...options})}`);return file;};
    return {...movie,film,double};
  })();
}
const WIDTH=640,HEIGHT=360;
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
const px=box=>[box[0]*WIDTH,box[1]*HEIGHT,box[2]*WIDTH,box[3]*HEIGHT];
const rect=r=>[r.x,r.y,r.width,r.height];
const within=(a,b,tolerance)=>a.every((v,i)=>Math.abs(v-b[i])<=tolerance);

test('a reframe moves the view from its outgoing slot\'s box to its incoming slot\'s, fades the rest in, and ends on the incoming frame',async()=>{
  const {film,viewer}=await theTour();
  const q=shotOf(film,'question'),d=q.transition.duration,mid=q.start+d/2,end=q.start+d;
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const first=await pose(q.start);
    const middle=await pose(mid);const midPng=await page.screenshot();
    // The headline the set draws above the right slot stays above the view
    // while it moves: hit-test inside both the title and the moving box.
    const above=await page.evaluate(()=>{
      const title=document.querySelector('[data-element="opening.title"] .vm-title')?.getBoundingClientRect();
      const host=document.querySelector('[data-element="opening.wide"] .vm-view-host')?.getBoundingClientRect();
      if(!title||!host)return null;
      const x0=Math.max(title.left,host.left),x1=Math.min(title.right,host.right);
      const y0=Math.max(title.top,host.top),y1=Math.min(title.bottom,host.bottom);
      if(!(x1>x0&&y1>y0))return {overlap:false};
      const hit=document.elementFromPoint((x0+x1)/2,(y0+y1)/2);
      return {overlap:true,hit:hit?.closest('[data-element]')?.getAttribute('data-element')??null};
    });
    await pose(shotOf(film,'push').start+.3);
    await pose(mid);const againPng=await page.screenshot();
    // The join at its end, by the timeline's own arithmetic, against the same
    // instant without a join.
    const last=await pose(end,{transition:reframeAt(film,'question',d)});const endPng=await page.screenshot();
    const plain=await pose(end,{transition:null});const plainPng=await page.screenshot();
    return {result:{first,middle,above,same:midPng.equals(againPng),last,plain,ends:endPng.equals(plainPng)}};
  });
  const {first,middle,above,same,last,plain,ends}=seen.result;
  const {from,to}=film.reframes.question['opening.wide'];
  assert.deepEqual([from.set,from.slot,to.set,to.slot],['playbill','stage','playbill-split','right']);
  // At the first frame: the outgoing slot's box, nothing else seen.
  assert.equal(first.transition.progress,0);
  assert.equal(first.set,'playbill-split','the live page shows the incoming set');
  const box=f=>rect(f.observed.elements['opening.wide'].box);
  assert.ok(within(box(first),px(from.box),1),`the view starts in playbill's stage: ${box(first)} against ${px(from.box)}`);
  assert.equal(first.observed.elements['opening.card'].opacity,0);
  assert.equal(first.observed.elements['opening.title'].opacity,0);
  // At the midpoint: the eased box, the faded elements at the eased progress.
  const p=middle.transition.progress;
  assert.ok(Math.abs(p-ease('smooth',.5))<1e-9,`the eased progress at the midpoint, ${p}`);
  assert.ok(within(box(middle),px(from.box.map((v,i)=>(1-p)*v+p*to.box[i])),1),'the view is between its two slots');
  for(const key of ['opening.card','opening.title'])
    assert.ok(Math.abs(middle.observed.elements[key].opacity-p)<=1e-3,`${key} at ${middle.observed.elements[key].opacity}`);
  assert.equal(middle.observed.elements['opening.wide'].opacity,1,'the moving view is not faded');
  const canvas=middle.observed.elements['opening.wide'].canvas,mbox=middle.observed.elements['opening.wide'].box;
  assert.ok(canvas.width>=mbox.width*.98&&canvas.height>=mbox.height*.98,'the canvas fills the moving box');
  assert.ok(within(rect(middle.observed.slots.right),px(to.box),1),'the slot keeps the box the set draws');
  assert.deepEqual(above,{overlap:true,hit:'opening.title'},'the headline is drawn above the moving view');
  assert.ok(same,'the midpoint, another instant, and the midpoint again give identical pixels');
  // At the end: the incoming slot's box, and exactly the incoming frame's pixels.
  assert.ok(within(box(last),px(to.box),1)&&within(box(last),box(plain),1e-9),'the view ends in playbill-split\'s right');
  assert.ok(ends,'the reframe at progress 1 is the incoming frame without a join, pixel for pixel');
});

test('a canvas that follows a shrinking box several frames late is waited for; one that never shrinks is refused',async()=>{
  // The reframe shrinks the view's box on every frame of the join (the
  // spike's finding, ADR-012): a canvas still at the larger size passes "fills
  // its box" and must not be posed into. The stage waits until the canvas is
  // the box's size within a pixel; the renderer refuses one that exceeds it.
  const {film,double}=await theTour();
  const q=shotOf(film,'question'),fps=film.output.fps,d=q.transition.duration;
  const frames=[];for(let n=Math.ceil(q.start*fps-1e-9);n/fps<q.start+d-1e-9;n++)frames.push(n/fps);
  const seen=await browserSession(film,await double('later-canvas.js',{lateCanvas:4}),WIDTH,[],async({pose})=>{
    await pose(shotOf(film,'hook').start+.1);
    const out=[];for(const t of frames){const r=(await pose(t)).observed.elements['opening.wide'];out.push({t,canvas:r.canvas,box:r.box});}
    return {result:out};
  });
  const off=seen.result.filter(({canvas,box})=>Math.abs(canvas.width-box.width)>1||Math.abs(canvas.height-box.height)>1);
  assert.deepEqual(off.map(({t,canvas,box})=>`${t.toFixed(2)} s: canvas ${canvas.width}×${canvas.height} in ${box.width}×${box.height}`),[],
    'every frame of the shrinking join is posed into a canvas of its box\'s size');
  await assert.rejects(browserSession(film,await double('stuck-canvas.js',{stuckCanvas:true}),WIDTH,[],async({pose})=>{
    await pose(shotOf(film,'hook').start+.1);
    for(const t of frames)await pose(t);
  }),/Viewer canvas exceeds its view: opening\.wide in question at \d+\.\d\d s \(canvas \d+\.\d×\d+\.\d, box \d+\.\d×\d+\.\d\)/);
});

test('with a viewer that sizes its canvas late, every frame of a reframe waits for its canvas; the cost per frame',async()=>{
  // A moving host is a resize every frame: the stage waits for the canvas to
  // fill the new box before it poses (the late-canvas double sizes it on its
  // own animation frame, as the real viewer does).
  const {film,double}=await theTour();
  const q=shotOf(film,'question'),fps=film.output.fps,d=q.transition.duration;
  const frames=[];for(let n=Math.ceil(q.start*fps-1e-9);n/fps<q.start+d-1e-9;n++)frames.push(n/fps);
  const after=frames.map(t=>t+d).filter(t=>t<q.end-1e-9);
  const seen=await browserSession(film,await double('late-canvas.js',{lateCanvas:true}),WIDTH,[],async({pose})=>{
    const out={join:[],after:[]};
    for(const [name,times] of [['join',frames],['after',after]]){
      for(const t of times){
        const start=performance.now(),f=await pose(t),ms=performance.now()-start;
        const r=f.observed.elements['opening.wide'];
        out[name].push({t,ms,fills:r.canvas.width>=r.box.width*.98&&r.canvas.height>=r.box.height*.98,progress:f.transition?.progress??null});
      }
    }
    return {result:out};
  });
  const {join:inside,after:plain}=seen.result;
  assert.equal(inside.length,Math.round(d*fps));
  assert.ok(inside.every(f=>f.fills),'every frame of the join fills its moving box');
  assert.ok(plain.every(f=>f.fills&&f.progress===null));
  const median=list=>{const s=list.map(f=>f.ms).sort((a,b)=>a-b);return s[Math.floor(s.length/2)];};
  // Logged for the evidence; the clock decides nothing here.
  console.log(`Reframe cost with the late-canvas double at ${WIDTH} px: median ${median(inside).toFixed(1)} ms per frame of the join (${inside.length} frames), ${median(plain).toFixed(1)} ms per frame after it (${plain.length} frames)`);
});
