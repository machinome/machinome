// Layer 5 (serial; Chromium, a viewer double): a YAML shot with the
// source-only layout is the shipped `source-only` set, which places the
// source panel and no view; its neighbours are the `paper` set.
import {slowTest as test} from '../support/memo.mjs';
import assert from 'node:assert/strict';
import {writeFile} from 'node:fs/promises';
import {join} from 'node:path';
import {browserSession,preview} from '../support/stage.mjs';
import {yamlProject} from '../support/yaml-project.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {resolveWordTiming} from '../../src/words.mjs';
import {decodePng,largestDifference,at,hexColor,chromeMask} from '../../src/pixels.mjs';

// models/model.py: line 415 is the excerpt; 416 to 504 make an overflowing one.
const MODEL=[...Array.from({length:414},(_,i)=>`# line ${i+1}`),'waterwheel.drives(crankshaft)',
  ...Array.from({length:89},(_,i)=>`waterwheel_${i+1}.drives(crankshaft_${i+1})`)].join('\n')+'\n';
const NARRATION='The waterwheel drives.';
// "waterwheel" spoken from 0.8 s into the take (1.0 s into its shot).
const ALIGNMENT=(()=>{const characters=Array.from(NARRATION),start=characters.map((_,i)=>i<4?i*.05:i<14?.8+(i-4)*.02:1.0+(i-14)*.05);
  return {characters,character_start_times_seconds:start,character_end_times_seconds:start.map((s,i)=>i<4?s+.05:i<14?s+.02:s+.05)};})();

async function fixture(t){
  const project=await yamlProject(t,{manifest:{root:{name:'test'},animation:{loop:10}},files:{'models/model.py':MODEL}});
  const viewer=join(project.dir,'viewer.js');
  await writeFile(viewer,`window.MachinomeViewer={async mount(selector,url,options){
    const canvas=document.createElement('canvas');canvas.style.cssText='width:100%;height:100%;background:#617a92';
    document.querySelector(selector).append(canvas);let view={...options.view,up:options.up,fov:options.fov};
    return {apiVersion:28,setVisible(){},navigation(){return {}},
      setTime(t){canvas.style.background='rgb('+Math.round(90+100*t)+',122,146)'},
      setView(v){if(!v.camera.every(Number.isFinite))throw new Error('invalid camera');view={...view,...v}},
      view(){return {camera:{toArray:()=>view.camera},target:{toArray:()=>view.target},
        up:{toArray:()=>view.up},fov:view.fov}},
      project(p){const minus=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((n,v,i)=>n+v*b[i],0);
        const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
        const unit=a=>{const d=Math.hypot(...a);return a.map(v=>v/d)};
        const forward=unit(minus(view.target,view.camera)),right=unit(cross(forward,view.up)),up=cross(right,forward);
        const d=minus(p,view.camera),depth=dot(d,forward);if(depth<=0)return null;
        const b=canvas.getBoundingClientRect(),k=(b.height/2)/Math.tan(view.fov*Math.PI/360);
        return {x:b.left+b.width/2+dot(d,right)/depth*k,y:b.top+b.height/2-dot(d,up)/depth*k}}};
  }};`);
  const shot=(id,start,end,extra={})=>({id,start,end,narration:NARRATION,direction:'Show.',
    simulation:{from:start,to:end},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
  const e={format:'machinome-video-draft/0.4',title:'Source',series:'TEST FILM',
    output:{width:640,height:360,fps:10,durationSeconds:6},
    model:{expectedDurationSeconds:10},audio:{replacements:{}},
    style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
    cameras:{a:{position:[0,-10,3],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    sourceCode:{line:{file:'models/model.py',lines:[415,415]}},
    shots:[shot('model-before',0,2),
      shot('source',2,4,{code:{snippet:'line',typing:[{from:0,to:.8,throughLine:415}],
        emphasis:[{line:415,phrase:'waterwheel',words:['waterwheel'],hold:.2}]},layout:'source-only'}),
      shot('model-after',4,6,{transition:{kind:'dissolve',duration:.4}})]};
  // Loads the episode with the fixture take's word timing.
  const load=async(episode=e,options)=>{
    const film=await project.film(episode,options);
    await resolveWordTiming(film,async()=>({sha256:'fixture',alignment:ALIGNMENT}));
    return film;
  };
  return {project,e,viewer,load};
}
// What the page shows besides the frame's report: the masthead's words, any
// progress rule, and the viewer hosts in the document.
const page=async p=>p.evaluate(()=>({brand:document.querySelector('.vm-paper-brand')?.textContent??null,
  series:document.querySelector('.vm-paper-series')?.textContent??null,
  progress:document.querySelector('#progress,.vm-progress,[class*=progress]')!==null,
  chromeChildren:document.querySelectorAll('#chrome .vm-chrome > *').length,
  views:window.film.views(),connectedCanvases:[...document.querySelectorAll('canvas')].filter(c=>c.isConnected).length}));
// The source panel fills the plain-stage rectangle, and no view is on the page.
function fullSource(posed,shown){
  const panel=posed.observed.elements[`${posed.shotId}.code`];
  assert.equal(posed.set,'source-only');
  const r=panel.box;
  assert.ok(Math.abs(r.x-32)<=1&&Math.abs(r.y-57.6)<=1&&Math.abs(r.width-576)<=1&&Math.abs(r.height-226.8)<=1,
    `source fills the plain-stage rectangle: ${JSON.stringify(r)}`);
  assert.ok(!Object.values(posed.observed.elements).some(x=>x.kind==='view'),'the set places no view');
  assert.ok(shown.views.every(v=>!v.visible)&&shown.connectedCanvases===0,'no model canvas is on the page');
}

test('portable source-only page proves literal typing, measured mark, chrome and exact seek replay',async t=>{
  const {load,viewer}=await fixture(t),e=await load();
  const result=await browserSession(e,viewer,640,[],async({page:p,pose})=>{
    const typed=await pose(2.3);
    const measured=await pose(3.1);
    const full=await pose(3.6),shown=await page(p),first=await p.screenshot();
    await pose(5);await pose(3.6);
    return {typed,measured,full,shown,replay:first.equals(await p.screenshot())};
  });
  const code=posed=>posed.observed.elements['source.code'];
  assert.ok(code(result.typed).text.length>0&&code(result.typed).text.length<'waterwheel.drives(crankshaft)'.length);
  assert.equal(code(result.full).text,'waterwheel.drives(crankshaft)');
  assert.deepEqual(code(result.measured).emphasis.map(m=>m.text),['waterwheel'],'the measured word is marked visibly');
  assert.deepEqual(code(result.full).emphasis,[],'and cleared after its hold');
  assert.equal(result.replay,true);
  assert.equal(result.shown.brand,'MACHINOME');assert.equal(result.shown.series,'TEST FILM');
  // The film has no progress rule: the masthead is the brand and the series only.
  assert.equal(result.shown.progress,false);assert.equal(result.shown.chromeChildren,2);
  assert.equal(result.full.observed.chrome.length,2);
  fullSource(result.full,result.shown);
});

test('portable source-only overflow refuses with shot and exact frame time',async t=>{
  const {e,viewer,load}=await fixture(t);
  e.sourceCode.line.lines=[415,504];e.shots[1].code.typing=[{from:0,to:.8,throughLine:504}];
  const film=await load(e);
  await assert.rejects(browserSession(film,viewer,640,[],async({pose})=>{
    await pose(3.6);
  }),/Source excerpt overflows the panel: source at 3\.60 s; select fewer lines/);
});

test('a first-shot source picture mounts at useful size and the next model returns visibly',async t=>{
  const {e,viewer,load}=await fixture(t);
  e.shots[0].id='first-source';e.shots[0].code=structuredClone(e.shots[1].code);
  e.shots[0].layout='source-only';delete e.shots[1].code;delete e.shots[1].layout;
  const film=await load(e);
  const result=await browserSession(film,viewer,640,[],async({page:p,pose})=>{
    const source=await pose(.9),sourceShown=await page(p);
    const model=await pose(2.5),modelShown=await page(p);
    return {source,sourceShown,model,modelShown};
  });
  fullSource(result.source,result.sourceShown);
  const view=result.model.observed.elements['source.view'];
  assert.equal(result.model.set,'paper');
  assert.ok(result.modelShown.views.some(v=>v.key==='source.view'&&v.visible),'the model view is on the page');
  assert.ok(Math.abs(view.box.x-32)<=1&&Math.abs(view.box.width-576)<=1);
  assert.ok(view.canvas.width>=view.box.width*.98&&view.canvas.height>=view.box.height*.98,
    'the model canvas fills its box after a first shot without a view');
});

test('source-only browser check refuses an absent or displaced panel, not just overflowing text',async t=>{
  for(const [name,css,pattern] of [
    ['hidden','.vm-slot[data-slot="source"]{display:none !important}',/Element has no box on the stage: source\.code in source at 3\.60 s/],
    ['displaced','.vm-slot[data-slot="source"]{left:0 !important}',/Film stage layout differs from the picture geometry: source\.code in source at 3\.60 s/],
    // Every slot shifted together does not launder the wrong rectangle.
    ['shifted','.vm-slot{left:0 !important;width:90% !important}',/Film stage layout differs from the picture geometry: source\.code in source at 3\.60 s/]]){
    const {viewer,load}=await fixture(t),film=await load();
    await assert.rejects(browserSession(film,viewer,640,[],async({page:p,pose})=>{
      await p.addStyleTag({content:css});await pose(3.6);
    }),pattern,`${name} source must be refused by the page proof`);
  }
});

test('a preview proof override to an outgoing model does not inherit incoming source layout',async t=>{
  const {e,viewer,load}=await fixture(t);
  e.shots[1].transition={kind:'fade',duration:.4};
  const film=await load(e);
  const time=2.1,x=frameAt(film,time).transition;
  assert.equal(x.outgoing.shotId,'model-before');
  assert.equal(x.outgoing.set,'paper');
  const result=await browserSession(film,viewer,640,[],async({page:p,pose})=>{
    const picture=await pose(time,{...x.outgoing,transition:null},{fresh:true});
    return {picture,shown:await page(p)};
  });
  assert.equal(result.picture.set,'paper','the outgoing model picture is its own set');
  assert.deepEqual(Object.keys(result.picture.observed.elements),['model-before.view'],'and has no source panel');
  assert.ok(result.shown.views.some(v=>v.key==='model-before.view'&&v.visible),'the outgoing model is the visible picture');
});

test('a source-only shot has no view to pose, and the split proves its changed lens by projection',async t=>{
  const {e,viewer,load}=await fixture(t);
  delete e.shots[1].code.emphasis;
  e.cameras.rolled={...e.cameras.a,up:[1,0,1],fov:24};
  e.shots[1].camera=[{at:0,preset:'a'},{at:1,preset:'rolled'}];
  const alone=await preview(await load(e),{viewer,width:640});
  assert.deepEqual(alone.cameraChecks?.filter(c=>c.shotId==='source')??[],[],
    'the source-only set places no view, so there is no lens to prove');
  delete e.shots[1].layout;
  const split=await preview(await load(e,{at:'split'}),{viewer,width:640});
  assert.ok(split.cameraChecks?.some(c=>c.shotId==='source'&&Number.isFinite(c.measured)&&Number.isFinite(c.expected)));
});

test('the unchanged visible split still proves changed FOV/up by positive projection',async t=>{
  const {e,viewer,load}=await fixture(t);
  delete e.shots[1].layout;delete e.shots[1].code.emphasis;
  e.cameras.rolled={...e.cameras.a,up:[1,0,1],fov:24};
  e.shots[1].camera=[{at:0,preset:'a'},{at:1,preset:'rolled'}];
  const report=await preview(await load(e),{viewer,width:640});
  const checks=report.cameraChecks?.filter(c=>c.shotId==='source')??[];
  assert.equal(checks.length,2);
  assert.ok(checks.every(c=>Number.isFinite(c.measured)&&Number.isFinite(c.expected)&&c.measured>0&&c.upAbove));
});

test('portable source/model joins in both directions obey the old four same-instant pixel rules',async t=>{
  const {e,viewer,load}=await fixture(t),outcomes=[];
  for(const kind of ['fade','dissolve','wipe','slide']){
    for(const shot of [e.shots[1],e.shots[2]])shot.transition={kind,duration:.4,
      ...(['wipe','slide'].includes(kind)?{direction:'left'}:{})};
    const film=await load(e,{at:kind});
    await browserSession(film,viewer,640,[],async({page:p,pose})=>{
      for(const [side,time] of [['incoming',2+(kind==='fade'?.3:.2)],['outgoing',4+(kind==='fade'?.1:.2)]]){
        const x=frameAt(film,time).transition;
        const posed=await pose(time,{},{fresh:true}),composed=await p.screenshot();
        const incoming={transition:null},outgoing={...x.outgoing,transition:null};
        const grab=async(request,options={})=>{const f=await pose(time,request,{fresh:true,...options});
          return {f,image:decodePng(await p.screenshot())};};
        const a=await grab(outgoing),b=await grab(incoming),A=a.image,B=b.image;
        const image=decodePng(composed),q=x.progress,s=Math.round(q*640),left=x.direction==='left';
        const source=side==='incoming'?b.f:a.f;
        const mask=chromeMask(640,image.height,posed.observed.chrome);
        let difference,limit;
        if(kind==='dissolve'){
          difference=largestDifference(image,(px,y,k)=>(1-q)*at(A,px,y,k)+q*at(B,px,y,k));limit=2;
        }else if(kind==='wipe'){
          difference=largestDifference(image,(px,y,k)=>(left?px>=640-s:px<s)?at(B,px,y,k):at(A,px,y,k));limit=0;
        }else if(kind==='slide'){
          const pa=(await grab(outgoing,{pictureOnly:true})).image,pb=(await grab(incoming,{pictureOnly:true})).image;
          difference=largestDifference(image,(px,y,k)=>left?
            (px<640-s?at(pa,px+s,y,k):at(pb,px-640+s,y,k)):
            (px>=s?at(pa,px-s,y,k):at(pb,px-s+640,y,k)),mask);limit=0;
        }else{
          const C=hexColor(x.color),plain=x.picture==='outgoing'?A:B;
          difference=largestDifference(image,(px,y,k)=>x.plate*C[k]+(1-x.plate)*at(plain,px,y,k),mask);limit=2;
        }
        const own=side==='incoming'?B:A;
        outcomes.push({kind,side,changed:!image.rgb.equals(own.rgb),set:source.set,
          sourceWidth:source.observed.elements['source.code']?.box.width,difference,limit});
      }
    });
  }
  assert.ok(outcomes.every(x=>x.changed&&x.set==='source-only'&&Math.abs(x.sourceWidth-576)<=1&&x.difference<=x.limit),
    `each source side is distinct and its join uses the same instant: ${JSON.stringify(outcomes)}`);
});
