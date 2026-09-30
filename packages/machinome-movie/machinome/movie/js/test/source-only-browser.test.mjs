import {slowTest as test} from './support/memo.mjs';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {browserSession,preview} from './support/stage.mjs';
import {frameAt} from '../src/timeline.mjs';
import {decodePng,largestDifference,at,hexColor,chromeMask} from '../src/pixels.mjs';

async function fixture(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-source-only-'));
  t.onTestFinished(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  const manifest=join(dir,'manifest.json'),viewer=join(dir,'viewer.js'),build=join(dir,'_build');
  await mkdir(build);
  await writeFile(manifest,JSON.stringify({root:{name:'test'},animation:{loop:10}}));
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
  const shot=(id,start,end,extra={})=>({id,start,end,narration:'The waterwheel drives.',direction:'Show.',
    simulation:{from:start,to:end},camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],...extra});
  const e={format:'machinome-video-draft/0.4',title:'Source',series:'TEST FILM',
    output:{width:640,height:360,fps:10,durationSeconds:6},
    model:{expectedDurationSeconds:10,timeMode:'normalized-loop'},
    style:{background:'#faf7ef',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans',safeInsetFraction:.08},
    paths:{repository:dir,episode:join(dir,'episode.yaml'),production:join(dir,'production.yaml'),manifest,build},
    cameras:{a:{position:[0,-10,3],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    sourceCode:{line:{file:'model.py',lines:[415,415],text:'waterwheel.drives(crankshaft)'}},
    shots:[shot('model-before',0,2),
      shot('source',2,4,{code:{snippet:'line',typing:[{from:0,to:.8,throughLine:415}],
        emphasis:[{line:415,phrase:'waterwheel',words:['waterwheel'],hold:.2}]},layout:'source-only'}),
      shot('model-after',4,6,{transition:{kind:'dissolve',duration:.4}})]};
  e.wordTiming={source:{sha256:'fixture',overlays:{},emphasis:[{cues:[{word:'waterwheel',line:415,start:0,end:10,
    from:1,wordEnd:1.2,to:1.5}]}]}};
  return {dir,e,viewer};
}
const bounds=async page=>page.evaluate(()=>{
  const source=document.querySelector('#source'),viewport=document.querySelector('#viewport');
  const r=source.getBoundingClientRect();
  return {rect:{x:r.x,y:r.y,width:r.width,height:r.height},display:getComputedStyle(source).display,
    viewportDisplay:getComputedStyle(viewport).display,viewportVisibility:getComputedStyle(viewport).visibility,
    text:document.querySelector('#source-code').textContent,
    marks:[...document.querySelectorAll('#source-code mark.spoken')].map(x=>x.textContent),
    brand:document.querySelector('#brand').textContent,series:document.querySelector('#series').textContent,
    progress:document.querySelector('#progress').getBoundingClientRect().width};
});
function fullSource(s){
  assert.equal(s.display,'block');
  assert.ok(Math.abs(s.rect.x-32)<=1&&Math.abs(s.rect.y-57.6)<=1&&
    Math.abs(s.rect.width-576)<=1&&Math.abs(s.rect.height-226.8)<=1,
    `source fills the plain-stage rectangle: ${JSON.stringify(s.rect)}`);
  assert.ok(s.viewportDisplay==='none'||s.viewportVisibility==='hidden','model canvas is not a visible pane');
}

test('portable source-only page proves literal typing, measured mark, chrome and exact seek replay',async t=>{
  const {e,viewer}=await fixture(t),result=await browserSession(e,viewer,640,[],async({page,pose})=>{
    await pose(2.3,{layout:'source-only',transition:null});const typed=await bounds(page);
    await pose(3.1,{layout:'source-only',transition:null});const measured=await bounds(page);
    await pose(3.6,{layout:'source-only',transition:null});const full=await bounds(page),first=await page.screenshot();
    await pose(5);await pose(3.6,{layout:'source-only',transition:null});
    return {typed,measured,full,replay:first.equals(await page.screenshot())};
  });
  assert.ok(result.typed.text.length>0&&result.typed.text.length<e.sourceCode.line.text.length);
  assert.equal(result.full.text,e.sourceCode.line.text);
  assert.ok(result.measured.marks.includes('waterwheel'),'measured word is marked visibly');
  assert.equal(result.replay,true);
  assert.ok(result.full.brand.includes('MACHINOME')&&result.full.series==='TEST FILM'&&result.full.progress>0);
  fullSource(result.full);
});

test('portable source-only overflow refuses with shot and exact frame time',async t=>{
  const {e,viewer}=await fixture(t);
  e.sourceCode.line.text=Array.from({length:90},(_,i)=>`waterwheel_${i}.drives(crankshaft_${i})`).join('\n');
  e.sourceCode.line.lines=[415,504];e.shots[1].code.typing=[{from:0,to:.8,throughLine:504}];
  await assert.rejects(browserSession(e,viewer,640,[],async({pose})=>{
    await pose(3.6,{layout:'source-only',transition:null});
  }),/Source excerpt overflows the panel: source at 3\.60 s; select fewer lines/);
});

test('a first-shot source picture mounts at useful size and the next model returns visibly',async t=>{
  const {e,viewer}=await fixture(t);
  e.shots[0].id='first-source';e.shots[0].code=structuredClone(e.shots[1].code);
  e.shots[0].layout='source-only';delete e.shots[1].code;delete e.shots[1].layout;
  e.wordTiming['first-source']=e.wordTiming.source;
  const result=await browserSession(e,viewer,640,[],async({page,pose})=>{
    await pose(.9,{layout:'source-only'});const source=await bounds(page);
    await pose(2.5);const model=await page.evaluate(()=>{
      const viewport=document.querySelector('#viewport'),stage=document.querySelector('#stage').getBoundingClientRect(),
        canvas=document.querySelector('#stage canvas').getBoundingClientRect();
      return {visibility:getComputedStyle(viewport).visibility,display:getComputedStyle(viewport).display,
        stage:{x:stage.x,y:stage.y,width:stage.width,height:stage.height},
        canvas:{width:canvas.width,height:canvas.height}};
    });
    return {source,model};
  });
  fullSource(result.source);
  assert.ok(result.model.display!=='none'&&result.model.visibility!=='hidden');
  assert.ok(Math.abs(result.model.stage.x-32)<=1&&Math.abs(result.model.stage.width-576)<=1);
  assert.ok(result.model.canvas.width>=result.model.stage.width*.98&&result.model.canvas.height>=result.model.stage.height*.98,
    'model canvas restores its measured stage after the hidden first shot');
});

test('source-only browser check refuses an absent or displaced panel, not just overflowing text',async t=>{
  for(const [name,css,pattern] of [
    ['hidden','#source{display:none !important}',/Source panel is not visible: source at 3\.60 s/],
    ['displaced','#source{left:0 !important}',/Source panel is outside the picture area: source at 3\.60 s/]]){
    const {e,viewer}=await fixture(t);
    await assert.rejects(browserSession(e,viewer,640,[],async({page,pose})=>{
      await page.addStyleTag({content:css});await pose(3.6,{layout:'source-only',transition:null});
    }),pattern,`${name} source must be refused by the page proof`);
  }
});

test('matching shifted source and hidden viewport do not launder the wrong picture rectangle',async t=>{
  const {e,viewer}=await fixture(t);
  await assert.rejects(browserSession(e,viewer,640,[],async({page,pose})=>{
    await page.addStyleTag({content:'#viewport{left:0 !important;width:90% !important} #source{left:0 !important;width:90% !important}'});
    await pose(3.6,{layout:'source-only',transition:null});
  }),/Source panel is outside the picture area: source at 3\.60 s/);
});

test('a preview proof override to an outgoing model does not inherit incoming source layout',async t=>{
  const {e,viewer}=await fixture(t);
  e.shots[1].transition={kind:'fade',duration:.4};
  const time=2.1,x=frameAt(e,time).transition;
  assert.equal(x.outgoing.shotId,'model-before');
  assert.equal(Object.hasOwn(x.outgoing,'layout'),false);
  const result=await browserSession(e,viewer,640,[],async({page,pose})=>{
    await pose(time,{...x.outgoing,transition:null},{fresh:true});
    return {picture:await bounds(page)};
  });
  assert.equal(result.picture.display,'none','outgoing model picture has no source panel');
  assert.equal(result.picture.viewportVisibility,'visible','outgoing model is the visible picture');
});

test('portable preview separates hidden source lens pose from visible split projection',async t=>{
  const {e,viewer}=await fixture(t);
  delete e.shots[1].code.emphasis;delete e.wordTiming;
  e.cameras.rolled={...e.cameras.a,up:[1,0,1],fov:24};
  e.shots[1].camera=[{at:0,preset:'a'},{at:1,preset:'rolled'}];
  const hidden=await preview(e,{viewer,width:640});
  const checks=hidden.cameraChecks?.filter(c=>c.shotId==='source')??[];
  assert.ok(checks.length>0);
  assert.ok(checks.every(c=>c.measured===undefined&&c.expected===undefined),
    `hidden canvas cannot be positive visible-lens evidence: ${JSON.stringify(checks)}`);
  delete e.shots[1].layout;
  const split=await preview(e,{viewer,width:640});
  assert.ok(split.cameraChecks?.some(c=>c.shotId==='source'&&Number.isFinite(c.measured)&&Number.isFinite(c.expected)));
});

test('the unchanged visible split still proves changed FOV/up by positive projection',async t=>{
  const {e,viewer}=await fixture(t);
  delete e.shots[1].layout;delete e.shots[1].code.emphasis;delete e.wordTiming;
  e.cameras.rolled={...e.cameras.a,up:[1,0,1],fov:24};
  e.shots[1].camera=[{at:0,preset:'a'},{at:1,preset:'rolled'}];
  const report=await preview(e,{viewer,width:640});
  const checks=report.cameraChecks?.filter(c=>c.shotId==='source')??[];
  assert.equal(checks.length,2);
  assert.ok(checks.every(c=>Number.isFinite(c.measured)&&Number.isFinite(c.expected)&&c.measured>0&&c.upAbove));
});

test('portable source/model joins in both directions obey the old four same-instant pixel rules',async t=>{
  const {e,viewer}=await fixture(t),outcomes=[];
  await browserSession(e,viewer,640,[],async({page,pose})=>{
    for(const kind of ['fade','dissolve','wipe','slide']){
      for(const shot of [e.shots[1],e.shots[2]])shot.transition={kind,duration:.4,
        ...(['wipe','slide'].includes(kind)?{direction:'left'}:{})};
      for(const [side,time] of [['incoming',2+(kind==='fade'?.3:.2)],['outgoing',4+(kind==='fade'?.1:.2)]]){
        const x=frameAt(e,time).transition;
        const opted={layout:side==='incoming'?'source-only':undefined,
          transition:{...x,outgoing:x.outgoing&&{...x.outgoing,layout:side==='outgoing'?'source-only':undefined}}};
        const posed=await pose(time,opted,{fresh:true}),composed=await page.screenshot();
        const plainX={...x,outgoing:x.outgoing&&{...x.outgoing,layout:undefined}};
        await pose(time,{layout:undefined,transition:plainX},{fresh:true});const split=await page.screenshot();
        const incoming={transition:null,layout:side==='incoming'?'source-only':undefined};
        const outgoing={...x.outgoing,transition:null,layout:side==='outgoing'?'source-only':undefined};
        const grab=async(request,options={})=>{await pose(time,request,{fresh:true,...options});return decodePng(await page.screenshot());};
        const A=await grab(outgoing),B=await grab(incoming),image=decodePng(composed),p=x.progress,s=Math.round(p*640),left=x.direction==='left';
        await pose(time,side==='incoming'?incoming:outgoing,{fresh:true});const source=await bounds(page);
        const mask=chromeMask(640,image.height,posed.observed.chrome);
        let difference,limit;
        if(kind==='dissolve'){
          difference=largestDifference(image,(px,y,k)=>(1-p)*at(A,px,y,k)+p*at(B,px,y,k));limit=2;
        }else if(kind==='wipe'){
          difference=largestDifference(image,(px,y,k)=>(left?px>=640-s:px<s)?at(B,px,y,k):at(A,px,y,k));limit=0;
        }else if(kind==='slide'){
          const a=await grab(outgoing,{pictureOnly:true}),b=await grab(incoming,{pictureOnly:true});
          difference=largestDifference(image,(px,y,k)=>left?
            (px<640-s?at(a,px+s,y,k):at(b,px-640+s,y,k)):
            (px>=s?at(a,px-s,y,k):at(b,px-s+640,y,k)),mask);limit=0;
        }else{
          const C=hexColor(x.color),plain=x.picture==='outgoing'?A:B;
          difference=largestDifference(image,(px,y,k)=>x.plate*C[k]+(1-x.plate)*at(plain,px,y,k),mask);limit=2;
        }
        outcomes.push({kind,side,changed:!composed.equals(split),sourceWidth:source.rect.width,difference,limit});
      }
    }
    return {};
  });
  assert.ok(outcomes.every(x=>x.changed&&Math.abs(x.sourceWidth-576)<=1&&x.difference<=x.limit),
    `each source side is distinct and its join uses the same instant: ${JSON.stringify(outcomes)}`);
});
