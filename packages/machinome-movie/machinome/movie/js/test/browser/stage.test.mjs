// Layer 5 (serial; Chromium, the viewer double): the React stage in a
// browser, on the 0.2 fixture movie `tour` (the fixture project's own sets
// playbill and playbill-split and element tally, the shipped frame and split).
// Every test reads what window.film.setFrame reports (`observed`) and the
// pixels; none reads the stage's internals beyond its documented classes.
import {afterAll} from 'vitest';
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {rm,writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {browserSession,preview} from '../support/stage.mjs';
import {bootStage} from '../support/stage-page.mjs';
import {fixtureMovie} from '../support/fixture-movie.mjs';
import {loadEpisode} from '../../src/episode.mjs';
import {frameAt,filmShots,shotActions} from '../../src/timeline.mjs';
import {decodePng,hexColor} from '../../src/pixels.mjs';
import {viewerDouble} from '../viewer-double.mjs';

// The tour, copied, committed and loaded once for this file's tests (each
// test that is not memoized asks for it).
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
const WIDTH=640;
// The middle of a shot, by id.
const middle=(film,id)=>{const {shot}=filmShots(film).find(s=>s.shot.id===id);return (shot.start+shot.end)/2;};
const shotOf=(film,id)=>filmShots(film).find(s=>s.shot.id===id).shot;
const close=(a,b,tolerance=1e-6)=>a.length===b.length&&a.every((v,i)=>Math.abs(v-b[i])<=tolerance);
const unit=v=>{const l=Math.hypot(...v);return v.map(x=>x/l);};

test('each view reads back exactly the camera, target, up and field of view it was asked for',async()=>{
  const {film,viewer,double}=await theTour();
  const instants=filmShots(film).map(({shot})=>middle(film,shot.id));
  const seen=await browserSession(film,viewer,WIDTH,[],async({pose})=>{
    const out=[];for(const t of instants)out.push(await pose(t,{transition:null}));return {result:out};
  });
  let views=0;
  for(const f of seen.result)for(const [key,state] of Object.entries(f.elements)){
    if(state.kind!=='view')continue;
    const read=f.observed.elements[key],where=`${key} in ${f.shotId}`;views++;
    assert.ok(close(read.camera,state.view.camera),`camera of ${where}`);
    assert.ok(close(read.target,state.view.target),`target of ${where}`);
    assert.ok(close(unit(read.up),unit(state.up)),`up of ${where}`);
    assert.ok(Math.abs(read.fov-state.fov)<=1e-6,`field of view of ${where}`);
  }
  assert.equal(views,instants.length,'one view in every shot of the tour');
  // A viewer that keeps the lens it mounted with is refused, naming the view,
  // once the view is asked for another (tip.close mounts in rise at 37 degrees).
  await assert.rejects(browserSession(film,await double('ignores-fov.js',{ignoreFov:true}),WIDTH,[],async({pose})=>{
    await pose(middle(film,'rise'),{transition:null});
    await pose(middle(film,'rhythm'),{transition:null});
  }),/Viewer did not adopt the requested field of view: tip\.close in rhythm at /);
});

test('a viewer that sizes its canvas on its own animation frame fills its view on a fresh mount, after a change of set, and when its view returns',async()=>{
  // The real viewer sizes its canvas from its host on an animation frame after
  // it mounts and after each resize, and a host detached while its view is off
  // screen is observed at no size, so the canvas shrinks to nothing; the stage
  // waits for the canvas to fill its box before it measures, on a fresh mount,
  // on a change of set and when the view is placed again. Found by the
  // Leonardo film: preview refused 'Viewer canvas does not fill its view' on
  // the first shot once its samples came back to it.
  const {film,double}=await theTour();
  const seen=await browserSession(film,await double('late-canvas.js',{lateCanvas:true}),WIDTH,[],async({pose})=>{
    const hook=await pose(middle(film,'hook'),{transition:null});
    const source=await pose(middle(film,'source'),{transition:null});
    const back=await pose(middle(film,'hook'),{transition:null});
    return {result:[hook,source,back]};
  });
  for(const f of seen.result)for(const [key,state] of Object.entries(f.elements)){
    if(state.kind!=='view')continue;
    const read=f.observed.elements[key];
    assert.ok(read.canvas.width>=read.box.width*.98&&read.canvas.height>=read.box.height*.98,`canvas of ${key} in ${f.shotId} fills its box`);
  }
});

test('posing A, then B, then A again gives identical pixels',async()=>{
  const {film,viewer,double}=await theTour();
  const a=middle(film,'hook'),b=middle(film,'push');
  const replay=async file=>(await browserSession(film,file,WIDTH,[],async({page,pose})=>{
    await pose(a);const first=await page.screenshot();
    await pose(b);const other=await page.screenshot();
    await pose(a);const again=await page.screenshot();
    return {result:{same:first.equals(again),changed:!first.equals(other)}};
  })).result;
  assert.deepEqual(await replay(viewer),{same:true,changed:true});
  // The proof is not vacuous: a viewer whose picture depends on its history fails it.
  assert.equal((await replay(await double('drifting.js',{drift:true}))).same,false);
});

test('a pose waits for what can change the picture: nothing when only a view changes, a repaint when a title\'s words change',async()=>{
  // Chromium rasters only what a change invalidates, and keeps antialiased
  // glyph edges just outside it; a pose whose page changed repaints the whole
  // page. A pose that changes only a view's canvas has nothing to repaint.
  // Counted as the animation frames a pose requests.
  const {film,viewer}=await theTour();
  const holds=shotOf(film,'holds'),rise=shotOf(film,'rise'),fps=film.output.fps;
  const h1=middle(film,'holds'),h2=h1+.2;
  // An instant of rise with its heading fully shown and no mark half faded
  // (a half-faded mark is composed from captures, which always repaint).
  let a=null;
  for(let n=Math.ceil(rise.start*fps);n/fps<rise.end&&a===null;n++){
    const state=frameAt(film,n/fps).elements;
    if(state['tip.heading'].shown&&state['tip.heading'].opacity===1&&state['tip.close'].marks.every(m=>m.opacity===1))a=n/fps;
  }
  assert.ok(a!==null&&h2<holds.end,'the instants exist');
  const heading=frameAt(film,a).elements['tip.heading'],other={...heading,text:'Down and up again'};
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    await page.evaluate(()=>{
      const request=window.requestAnimationFrame.bind(window);
      window.poseFrames=0;window.requestAnimationFrame=callback=>{window.poseFrames++;return request(callback);};
    });
    const posed=async(t,override)=>{
      await page.evaluate(()=>{window.poseFrames=0;});
      const f=await pose(t,{transition:null,...override});
      return {frames:await page.evaluate(()=>window.poseFrames),view:f.elements['balance.mill'],png:await page.screenshot()};
    };
    const first=await posed(h1),again=await posed(h1),later=await posed(h2);
    const A=await posed(a),B=await posed(a,{elements:{'tip.heading':other}}),A2=await posed(a);
    return {result:{first,again,later,A,B,A2}};
  });
  const {first,again,later,A,B,A2}=seen.result;
  assert.notDeepEqual([later.view.time,later.view.view],[first.view.time,first.view.view],'the view moved between the two instants of holds');
  assert.equal(again.frames,0,'the same frame posed again requests no animation frame');
  assert.ok(again.png.equals(first.png),'and gives the same pixels');
  assert.equal(later.frames,0,'a frame of the view alone at another instant requests no animation frame');
  assert.ok(B.frames>0,'a title whose words changed repaints the page');
  assert.ok(A2.frames>0,'and so does the pose that changes them back');
  assert.ok(!B.png.equals(A.png),'the words reach the pixels');
  assert.ok(A2.png.equals(A.png),'posing A, then B, then A gives identical pixels for A');
});

test('a set with no Chrome draws no masthead: the shipped frame shows its view to the top edge',async()=>{
  const {film,viewer}=await theTour();
  const band=image=>{const out=new Set();
    for(let y=0;y<Math.round(image.height*.1);y++)for(let x=0;x<image.width;x++){
      const i=(y*image.width+x)*3;out.add(`${image.rgb[i]},${image.rgb[i+1]},${image.rgb[i+2]}`);}
    return out;};
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const plain=await pose(middle(film,'holds'),{transition:null});const plainImage=decodePng(await page.screenshot());
    const layer=await page.evaluate(()=>document.getElementById('chrome').children.length);
    const bill=await pose(middle(film,'hook'),{transition:null});const billImage=decodePng(await page.screenshot());
    return {result:{plain:{set:plain.set,chrome:plain.observed.chrome,layer,band:[...band(plainImage)]},
      bill:{set:bill.set,chrome:bill.observed.chrome,band:[...band(billImage)]}}};
  });
  const {plain,bill}=seen.result;
  assert.equal(plain.set,'frame');
  assert.deepEqual(plain.chrome,[]);assert.equal(plain.layer,0,'nothing in the chrome layer');
  assert.deepEqual(plain.band,[hexColor('#6f8fa8').join(',')],'the top band is the view, one flat colour, with nothing over it');
  // The control: the tour's own set draws its masthead in that band.
  assert.equal(bill.set,'playbill');
  assert.equal(bill.chrome.length,2,'the series and the title');
  assert.ok(bill.band.length>2,'a masthead is drawn in the top band');
});

test('a picture-only capture leaves out the chrome, and only the chrome',async()=>{
  const {film,viewer}=await theTour();
  const t=middle(film,'hook');
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const live=await pose(t,{transition:null});const liveImage=decodePng(await page.screenshot());
    const liveHidden=await page.evaluate(()=>getComputedStyle(document.getElementById('chrome')).visibility);
    await pose(t,{transition:null},{pictureOnly:true});const bare=decodePng(await page.screenshot());
    const bareHidden=await page.evaluate(()=>getComputedStyle(document.getElementById('chrome')).visibility);
    return {result:{chrome:live.observed.chrome,liveImage,bare,liveHidden,bareHidden}};
  });
  const {chrome,liveImage,bare,liveHidden,bareHidden}=seen.result;
  assert.equal(liveHidden,'visible');assert.equal(bareHidden,'hidden');
  assert.equal(chrome.length,2);
  const background=hexColor('#faf7ef');
  const inside=(x,y)=>chrome.some(r=>x>=r.x-2&&x<r.x+r.width+2&&y>=r.y-2&&y<r.y+r.height+2);
  let differing=0,outside=0;
  for(let y=0;y<bare.height;y++)for(let x=0;x<bare.width;x++){
    const i=(y*bare.width+x)*3,same=[0,1,2].every(k=>bare.rgb[i+k]===liveImage.rgb[i+k]);
    if(inside(x,y)){
      if(!same)differing++;
      if(chrome.some(r=>x>=r.x&&x<r.x+r.width&&y>=r.y&&y<r.y+r.height))
        assert.deepEqual([0,1,2].map(k=>bare.rgb[i+k]),background,`the background under the chrome at ${x},${y}`);
    }else if(!same)outside++;
  }
  assert.ok(differing>50,'the live chrome was drawn');
  assert.equal(outside,0,'nothing but the chrome differs');
});

test('two views in one shot are two viewer instances, each posed as its own state asks',async()=>{
  const {film,viewer}=await theTour();
  // A frame built by hand on the shipped split: the tip chapter's two views side by side.
  const t=middle(film,'rise'),rise=frameAt(film,t),wide=frameAt(film,middle(film,'invitation')).elements['tip.wide'];
  const request={shotId:'two-views',chapterId:'tip',set:'split',slots:{left:'tip.close',right:'tip.wide'},
    elements:{'tip.close':rise.elements['tip.close'],'tip.wide':wide},transition:null};
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    await page.evaluate(()=>{window.viewerCalls.length=0;});
    const f=await pose(t,request);
    return {result:{observed:f.observed,views:await page.evaluate(()=>window.film.views()),
      instances:await page.evaluate(()=>window.viewerInstances.map(i=>({selector:i.selector,views:i.calls.filter(c=>c[0]==='setView').map(c=>c[1])})))}};
  });
  const {observed,views,instances}=seen.result;
  const close_=observed.elements['tip.close'],wide_=observed.elements['tip.wide'];
  assert.notEqual(close_.instance,wide_.instance,'two instances');
  assert.deepEqual(views.filter(v=>v.visible).map(v=>v.key).sort(),['tip.close','tip.wide']);
  for(const [report,slot] of [[close_,'left'],[wide_,'right']]){
    const box=observed.slots[slot];
    assert.ok(Math.abs(report.box.x-box.x)<=.5&&Math.abs(report.box.width-box.width)<=.5,`the ${slot} view fills its slot`);
    assert.ok(report.canvas.width>=report.box.width*.98&&report.canvas.x>=report.box.x-.5,`the ${slot} canvas is its own`);
  }
  assert.ok(close(close_.camera,request.elements['tip.close'].view.camera)&&close(wide_.camera,wide.view.camera));
  // Each instance was asked for its own camera only.
  const asked=instances.map(i=>i.views.at(-1)?.camera);
  assert.ok(asked.some(c=>c&&close(c,request.elements['tip.close'].view.camera))&&asked.some(c=>c&&close(c,wide.view.camera)));
  assert.ok(instances.every(i=>new Set(i.views.map(v=>JSON.stringify(v.camera))).size<=1),'no instance is posed with the other view\'s camera');
});

test('a view keeps its viewer instance across the cuts inside its chapter',async()=>{
  const {film,viewer}=await theTour();
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const out=[];
    for(const id of ['holds','source','push']){
      const f=await pose(middle(film,id),{transition:null});
      out.push({set:f.set,view:f.observed.elements['balance.mill']});
    }
    return {result:{out,mounts:await page.evaluate(()=>window.viewerInstances.length),views:await page.evaluate(()=>window.film.views())}};
  });
  const {out,mounts,views}=seen.result;
  assert.deepEqual(out.map(x=>x.set),['frame','playbill-split','split']);
  assert.equal(new Set(out.map(x=>x.view.instance)).size,1,'one instance for balance.mill in all three shots');
  assert.equal(new Set(out.map(x=>JSON.stringify(x.view.box))).size,3,'in three different boxes');
  for(const {view} of out)assert.ok(view.canvas.width>=view.box.width*.98&&view.canvas.height>=view.box.height*.98,'its canvas follows its box');
  assert.equal(views.filter(v=>v.key==='balance.mill').length,1);
  assert.equal(mounts,2,'the session\'s first frame (opening.wide) and balance.mill, nothing more');
});

test('a project element\'s state reaches its component: the tally lights the item its action names',async()=>{
  const {film,viewer}=await theTour();
  const hook=shotOf(film,'hook'),question=shotOf(film,'question');
  const light=shot=>shotActions(shot).find(x=>x.action.element==='card'&&x.action.action==='light');
  const on=light(hook),next=light(question);
  const instants=[['before',hook.start+on.cue.at/2],['balance',hook.start+(on.cue.at+on.cue.until)/2],
    ['tip',question.start+(next.cue.at+next.cue.until)/2]];
  const seen=await browserSession(film,viewer,WIDTH,[],async({page,pose})=>{
    const out={};
    for(const [name,t] of instants){
      const f=await pose(t,{transition:null});
      out[name]={state:f.elements['opening.card'],report:f.observed.elements['opening.card'],
        items:await page.$$eval('.vm-element[data-element="opening.card"] .tally-item',els=>els.map(e=>({text:e.textContent,lit:e.classList.contains('tally-lit')})))};
    }
    return {result:out};
  });
  const {before,balance,tip}=seen.result;
  assert.deepEqual(before.state.actions,[]);
  assert.deepEqual(before.items,[{text:'Balance',lit:false},{text:'Tip',lit:false}]);
  assert.deepEqual(balance.state.actions.map(a=>[a.action,a.params]),[['light',{item:'Balance'}]]);
  assert.deepEqual(balance.items,[{text:'Balance',lit:true},{text:'Tip',lit:false}]);
  assert.deepEqual(tip.items,[{text:'Balance',lit:false},{text:'Tip',lit:true}]);
  assert.ok(balance.report.box.width>0&&balance.report.kind==='tally');
});

test('the stage refuses at mount, by name, a set kind, slots, an element kind or a viewer it cannot draw',async()=>{
  const {film,viewer,double}=await theTour();
  assert.deepEqual(await bootStage(film,{viewer}),{error:null,ready:true},'the tour as it is boots');
  const refused=async edit=>(await bootStage(film,{viewer,edit})).error;
  assert.match(await refused(c=>{c.stage.sets.marquee={slots:['stage'],props:{}};return c;}),
    /Set kind marquee is not registered by the stage modules/);
  assert.match(await refused(c=>{c.stage.sets.playbill.slots=[...c.stage.sets.playbill.slots,'footer'];return c;}),
    /Set kind playbill registers slots aside, headline, plate, stage but the document declares aside, footer, headline, plate, stage/);
  assert.match(await refused(c=>{c.stage.elements=[...c.stage.elements,'gauge'];return c;}),
    /Element kind gauge is not registered by the stage modules/);
  // A viewer below the movie's API is refused when its first view mounts.
  await assert.rejects(browserSession(film,await double('api27.js',{api:27}),WIDTH,[],async()=>({})),
    /Viewer API 28 for highlight \(shot source\).*declares API 27/);
});

test('the tour previews: every proof holds and the report lists each kind of check',async()=>{
  const {film,viewer}=await theTour();
  const report=await preview(film,{viewer,width:WIDTH});
  assert.equal(report.pixelReplay,true);
  assert.equal(report.invalidCameraPreserved,true);
  for(const kind of ['highlightChecks','entranceChecks','revealChecks','fadeChecks','emphasisChecks','pictureChecks','transitionChecks','cameraChecks'])
    assert.ok(report[kind]?.length>0,`the report lists ${kind}`);
  assert.deepEqual(report.highlightChecks.map(c=>c.shotId),['source','source','rise','rise','invitation']);
  assert.deepEqual([...new Set(report.transitionChecks.map(c=>`${c.shotId}:${c.field}`))].sort(),
    ['hook:fadeIn','invitation:fadeOut','invitation:transition','push:transition','rhythm:transition','source:transition']);
  assert.ok(report.entranceChecks.every(c=>c.skipped||c.vacuous===false));
  assert.ok(report.pictureChecks.every(c=>c.replay));
});
