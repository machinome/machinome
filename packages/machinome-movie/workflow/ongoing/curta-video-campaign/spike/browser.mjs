// Spike questions 3 to 8 on the real viewer bundle, over the clocked Curta
// export, with the recorded Python scenario (scenario.py's JSON) as the
// reference and the Leonardo sawmill export as the posed baseline.
//
//   node browser.mjs <bundle> <curta export> <scenario.json> <posed export> <results.json> <stills dir> [sections] [cycles]
//
// `sections` is a comma list of parity, restore, highlight, resize, cost,
// posed (default all); `cycles` the number of poses each cost row times
// (default 30). The mount and the memory reading always run. The machine's
// load average is recorded around each section, since other work on the
// machine changes every duration here.
//
// Everything the viewer is asked goes through its public handle
// (MachinomeViewer.mount, viewer.machine(), setView, highlight, setTime,
// partOnScreen) as the reference pages describe it.
import {mkdir,readFile,writeFile} from 'node:fs/promises';
import {launch,serve,openPage,mount,mountClocked,treeRss,median,sha,join,twoFrames} from './harness.mjs';
import {decodePng} from '../../../../src/pixels.mjs';

const [bundle,curta,scenarioFile,posed,resultsFile,stills,sections='all',cyclesArg='30']=process.argv.slice(2);
const want=s=>sections.split(',').some(x=>x==='all'||x===s);
const CYCLES=Number(cyclesArg);
const load=async()=>(await readFile('/proc/loadavg','utf8')).split(' ').slice(0,3).map(Number);
const scenario=JSON.parse(await readFile(scenarioFile,'utf8'));
const exportIdentity=JSON.parse(await readFile(join(curta,'manifest.json'),'utf8')).clocked.identity;
await mkdir(stills,{recursive:true});

// A camera that shows the crank, the result dials and the setting slides
// (camera.mjs, candidate chosen by eye).
const VIEW={camera:[240,-240,300],target:[0,0,10],up:[0,0,1],fov:40};
const FRACTIONS=[0,0.3,0.5,0.7,1];
// The setting slide of the first digit, read from the export's tree
// (export-facts.json, input_selector_paths).
const SLIDE=['input_selectors','selectors','digit_selector_axle_1','selector_knob_1_419057'];
const HIDE_CHROME='.machinome-fullscreen{display:none !important}';
const results={bundle,curta,posed,exportIdentity,view:VIEW,slide:SLIDE,sections,cycles:CYCLES,load:{}};

// ---- the bank at a fraction of a recorded step (the plan's contract) ----
// The bank before the step, the moving input at origin + f·(end − origin),
// and the targets of every commit whose fraction ≤ f written.
function bankAt(before,request,f){
  const bank={...before};
  bank[request.input]=request.origin+f*(request.end-request.origin);
  for(const commit of request.commits)if(commit.fraction<=f)Object.assign(bank,commit.targets);
  return bank;
}
const requests=scenario.requests;
const crank23=requests.findIndex(r=>r.step[0]==='trigger');
const before23=requests[crank23-1].bank_after;
const banks=Object.fromEntries(FRACTIONS.map(f=>[f,bankAt(before23,requests[crank23],f)]));

const {browser,pid,version,close}=await launch();
const server=await serve(bundle,{model:curta,posed});
results.chromium=version;
try{
  // ---------------- Q8 memory, and the mount ----------------
  const rssBrowser=await treeRss(pid);
  const {page,errors}=await openPage(browser,server.origin,1920,1080);
  await page.addStyleTag({content:HIDE_CHROME});
  const rssBefore=await treeRss(pid);
  const mounted=await mountClocked(page,'model',{time:0,view:{camera:VIEW.camera,target:VIEW.target},up:VIEW.up,fov:VIEW.fov});
  await page.evaluate(async([view,wait])=>{window.viewer.setView(view);await eval(wait);},[VIEW,twoFrames]);
  const rssAfter=await treeRss(pid);
  results.mount=mounted;
  results.memory={browserOnly:rssBrowser,pageNoMount:rssBefore,mounted:rssAfter};
  console.log('mount',mounted);
  console.log('memory MB',[rssBrowser,rssBefore,rssAfter].map(x=>`${(x.kb/1024).toFixed(0)} in ${x.processes}`).join(' | '));

  // ---------------- Q3 parity ----------------
  if(want('parity')){results.load.parity=await load();
  results.parity=await page.evaluate(([scenario,exportIdentity])=>{
    const machine=window.viewer.machine();
    if(!machine)return {error:'viewer.machine() is null'};
    const diffs=[],same=(where,a,b)=>{if(!Object.is(a,b))diffs.push({where,viewer:a,python:b});};
    const sameBank=(where,a,b)=>{
      const keys=new Set([...Object.keys(a),...Object.keys(b)]);
      for(const k of keys)same(`${where}.${k}`,a[k],b[k]);
    };
    const replay=(label,useTrigger)=>{
      machine.reset();
      sameBank(`${label}.bank_before`,machine.state(),scenario.bank_before);
      const seen=[];
      scenario.requests.forEach((p,i)=>{
        const [kind,subject,args]=p.step;
        const t0=performance.now();
        const r=kind==='move'?machine.move(subject,args):useTrigger?machine.trigger(subject):machine.move('crank_rotation',{by:360});
        const ms=performance.now()-t0;
        const w=`${label}[${i}] ${kind} ${subject}`;
        for(const f of ['input','origin','end','admitted'])same(`${w}.${f}`,r[f],p[f]);
        if(kind==='move')for(const f of ['by','to'])same(`${w}.${f}`,r[f],p[f]);
        same(`${w}.commits.length`,r.commits.length,p.commits.length);
        r.commits.forEach((c,j)=>{
          const q=p.commits[j]??{};
          same(`${w}.commits[${j}].fraction`,c.fraction,q.fraction);
          same(`${w}.commits[${j}].value`,c.value,q.value);
          sameBank(`${w}.commits[${j}].targets`,c.targets,q.targets??{});
          same(`${w}.commits[${j}].relations`,JSON.stringify(c.relations),JSON.stringify(q.relations));
        });
        same(`${w}.stops.length`,r.stops.length,p.stops.length);
        sameBank(`${w}.bank_after`,machine.state(),p.bank_after);
        seen.push({ms,request:JSON.parse(JSON.stringify(r))});
      });
      return seen;
    };
    const byMove=replay('move',false);
    const byTrigger=replay('trigger',true);
    machine.reset();
    return {identity:machine.identity(),identityMatchesExport:machine.identity()===exportIdentity,
      order:machine.order().length,diffs,byMove,byTriggerMs:byTrigger.map(x=>x.ms)};
  },[scenario,exportIdentity]);
  console.log('parity: identity',results.parity.identityMatchesExport,'differences',results.parity.diffs?.length,
    'move ms',results.parity.byMove?.map(x=>x.ms.toFixed(2)).join(' '));
  }

  // ---------------- Q4 restored banks pose ----------------
  if(want('restore')){results.load.restore=await load();
  const pose=async(f,{settle=false}={})=>page.evaluate(async([bank,identity,view,settle,wait])=>{
    const machine=window.viewer.machine();
    let refusal=null;
    try{machine.restore({identity,bank});}catch(error){refusal=String(error.message??error);}
    window.viewer.setView(view);
    if(settle)await eval(wait);
    const state=machine.state(),exact=Object.keys(bank).every(k=>Object.is(state[k],bank[k]))&&Object.keys(state).length===Object.keys(bank).length;
    return {refusal,exact,crank:state.crank_rotation,crankOnScreen:window.viewer.partOnScreen(['main_drive','crank'])?.rect??null};
  },[banks[f],exportIdentity,VIEW,settle,twoFrames]);
  const q4={fractions:{},abaIdentical:null};
  for(const f of FRACTIONS){
    const now=await pose(f);const immediate=await page.screenshot();
    await page.evaluate(wait=>eval(wait),twoFrames);const settled=await page.screenshot();
    await page.evaluate(async wait=>{for(let i=0;i<15;i++)await eval(wait);},twoFrames);const idle=await page.screenshot();
    q4.fractions[f]={...now,immediate:await sha(immediate),settled:await sha(settled),idle30:await sha(idle),
      immediateEqualsSettled:immediate.equals(settled),settledEqualsIdle:settled.equals(idle)};
    await writeFile(join(stills,`fraction-${f}.png`),settled);
  }
  const shots=Object.values(q4.fractions).map(x=>x.settled);
  q4.distinctPictures=new Set(shots).size;
  const a1=(await pose(0.3),await page.screenshot());
  const b1=(await pose(0.7),await page.screenshot());
  const a2=(await pose(0.3),await page.screenshot());
  q4.abaIdentical=a1.equals(a2);q4.abDiffer=!a1.equals(b1);
  q4.aMatchesFirstPose=(await sha(a1))===q4.fractions[0.3].immediate;
  results.restore=q4;
  console.log('restore',JSON.stringify(q4));
  }

  // ---------------- Q6 highlight across a restore ----------------
  if(want('highlight')){results.load.highlight=await load();
  const highlight=page=>page.evaluate(([path,view])=>{
    window.release=window.viewer.highlight([path],{color:'#ff5a1f',others:'ghost'});window.viewer.setView(view);},[SLIDE,VIEW]);
  const release=page=>page.evaluate(view=>{window.release();window.release=null;window.viewer.setView(view);},VIEW);
  const restoreBank=(page,bank)=>page.evaluate(([bank,identity,view])=>{
    window.viewer.machine().restore({identity,bank});window.viewer.setView(view);
    return window.viewer.partOnScreen(['input_selectors','selectors','digit_selector_axle_1','selector_knob_1_419057']);
  },[bank,exportIdentity,VIEW]);
  const X=requests[crank23-1].bank_after;                       // digit_1 at 3, digit_2 at 2
  const Y=requests.findLast(r=>r.step[0]==='move'&&r.step[1]==='digit_3').bank_after;  // digit_1 at 5
  const q6={};
  q6.slideX=await restoreBank(page,X);const plainX=await page.screenshot();
  await highlight(page);const litX=await page.screenshot();
  q6.slideY=await restoreBank(page,Y);const litYcarried=await page.screenshot();
  q6.secondHighlightRefusal=await page.evaluate(path=>{try{const r=window.viewer.highlight([path],{});r();return null;}catch(e){return String(e.message);}},SLIDE);
  await release(page);await restoreBank(page,Y);const plainY=await page.screenshot();
  await highlight(page);const litYfresh=await page.screenshot();
  await release(page);
  const changed=(a,b)=>{const A=decodePng(a),B=decodePng(b);let n=0;for(let i=0;i<A.rgb.length;i+=3)if(A.rgb[i]!==B.rgb[i]||A.rgb[i+1]!==B.rgb[i+1]||A.rgb[i+2]!==B.rgb[i+2])n++;return n;};
  // Tinted: a pixel the highlight made strongly orange (red well above blue)
  // that was not so in the plain picture of the same bank.
  const tinted=(lit,plain)=>{const L=decodePng(lit),P=decodePng(plain);let n=0;
    for(let i=0;i<L.rgb.length;i+=3){const o=L.rgb[i]-L.rgb[i+2]>90&&L.rgb[i]>150,p=P.rgb[i]-P.rgb[i+2]>90&&P.rgb[i]>150;if(o&&!p)n++;}return n;};
  Object.assign(q6,{
    carriedEqualsFresh:litYcarried.equals(litYfresh),
    pixelsChangedXtoY_lit:changed(litX,litYcarried),
    pixelsChangedXtoY_plain:changed(plainX,plainY),
    tintedX:tinted(litX,plainX),tintedYcarried:tinted(litYcarried,plainY),tintedYfresh:tinted(litYfresh,plainY),
  });
  for(const [name,png] of Object.entries({plainX,litX,litYcarried,plainY}))await writeFile(join(stills,`highlight-${name}.png`),png);
  results.highlight=q6;
  console.log('highlight',JSON.stringify(q6));
  }

  // ---------------- Q7 the canvas after a resize ----------------
  if(want('resize')){results.load.resize=await load();
  results.resize=await page.evaluate(async()=>{
    const box=document.getElementById('box'),canvas=()=>document.querySelector('#v canvas');
    const rects=()=>({c:canvas().getBoundingClientRect(),b:box.getBoundingClientRect()});
    const fills=()=>{const {c,b}=rects();return c.width>=b.width*.98&&c.height>=b.height*.98;};
    const exact=()=>{const {c,b}=rects();return Math.abs(c.width-b.width)<=1&&Math.abs(c.height-b.height)<=1;};
    const frame=()=>new Promise(r=>requestAnimationFrame(r));
    const full={left:'0px',width:'100%'},half={left:'50%',width:'50%'};
    // Single animation frames until the canvas fills (stage's 98 % rule) and
    // until it is the box's size within a pixel.
    const single=async style=>{
      Object.assign(box.style,style);const t0=performance.now();
      const at0={fills:fills(),exact:exact()};let filled=at0.fills?0:null,sized=at0.exact?0:null,n=0;
      while(n<120&&(filled===null||sized===null)){await frame();n++;if(filled===null&&fills())filled=n;if(sized===null&&exact())sized=n;}
      const {c,b}=rects();
      return {filled,sized,ms:performance.now()-t0,canvas:[c.width,c.height],box:[b.width,b.height]};
    };
    // The stage's loop: two frames, then the check, at most 30 tries.
    const stage=async style=>{
      Object.assign(box.style,style);const t0=performance.now();let tries=0;
      for(;tries<30;){await frame();await frame();tries++;if(fills())break;}
      return {tries,ms:performance.now()-t0,fills:fills()};
    };
    const out={single:[],stage:[],gradual:[]};
    for(let i=0;i<5;i++){out.single.push({to:'half',...await single(half)});out.single.push({to:'full',...await single(full)});}
    for(let i=0;i<5;i++){out.stage.push({to:'half',...await stage(half)});out.stage.push({to:'full',...await stage(full)});}
    // The reframe's shape: the box shrinks from the whole frame to the right
    // half over 15 frames, one size per frame.
    for(let k=1;k<=15;k++){const left=50*k/15;out.gradual.push({left,...await stage({left:`${left}%`,width:`${100-left}%`})});}
    Object.assign(box.style,full);await stage(full);
    return out;
  });
  console.log('resize single',results.resize.single.map(x=>`${x.to}:${x.filled}/${x.sized}`).join(' '),
    'stage',results.resize.stage.map(x=>x.tries).join(' '),'gradual',results.resize.gradual.map(x=>x.tries).join(' '));
  }

  // ---------------- Q5 the cost of a pose ----------------
  // Median of each phase over CYCLES poses, with the minimum and maximum of
  // the whole cycle; the pose cycles through the five fractions so every
  // pose changes the picture.
  const cost=async(page,poseCall,n=CYCLES)=>{
    // The interval between animation frames while idle: what a render loop
    // (or its absence) costs before any pose is asked for.
    const frameMs=await page.evaluate(async()=>{const t=[];let last=null;
      for(let i=0;i<11;i++){await new Promise(r=>requestAnimationFrame(r));const now=performance.now();if(last!==null)t.push(now-last);last=now;}
      t.sort((a,b)=>a-b);return +t[5].toFixed(1);});
    const rows=[];
    for(let i=0;i<n;i++){
      const t0=performance.now();const inPage=await poseCall(i);const t1=performance.now();
      await page.screenshot();const t2=performance.now();
      rows.push({...inPage,evaluate:t1-t0,screenshot:t2-t1,total:t2-t0});
    }
    const keys=Object.keys(rows[0]);
    return {n,frameMs,...Object.fromEntries(keys.map(k=>[k,+median(rows.map(r=>r[k])).toFixed(2)])),
      totalMin:+Math.min(...rows.map(r=>r.total)).toFixed(0),totalMax:+Math.max(...rows.map(r=>r.total)).toFixed(0)};
  };
  const clockedPose=page=>i=>page.evaluate(([bank,identity,view])=>{
    const m=window.viewer.machine(),t0=performance.now();m.restore({identity,bank});const t1=performance.now();
    window.viewer.setView(view);const t2=performance.now();return {restore:t1-t0,setView:t2-t1};
  },[banks[FRACTIONS[i%FRACTIONS.length]],exportIdentity,VIEW]);
  results.cost={};
  if(want('cost')){results.load.cost1080=await load();results.cost.curta1080=await cost(page,clockedPose(page));
    console.log('cost curta1080',JSON.stringify(results.cost.curta1080));}
  results.pageErrors=errors;
  await page.close();
  if(want('cost')){results.load.cost540=await load();
    const {page,errors}=await openPage(browser,server.origin,960,540);
    await page.addStyleTag({content:HIDE_CHROME});
    await mountClocked(page,'model',{time:0,view:{camera:VIEW.camera,target:VIEW.target},up:VIEW.up,fov:VIEW.fov});
    await page.evaluate(async([view,wait])=>{window.viewer.setView(view);await eval(wait);},[VIEW,twoFrames]);
    results.cost.curta540=await cost(page,clockedPose(page));
    console.log('cost curta540',JSON.stringify(results.cost.curta540));
    // Evidence stills at 960×540, JPEG, for the note.
    for(const f of FRACTIONS){
      await page.evaluate(([bank,identity,view])=>{window.viewer.machine().restore({identity,bank});window.viewer.setView(view);},[banks[f],exportIdentity,VIEW]);
      await page.screenshot({path:join(stills,`still-${f}.jpg`),type:'jpeg',quality:80});
    }
    if(errors.length)results.pageErrors540=errors;
    await page.close();
  }
  // The posed baseline: the sawmill on the stage's own options (on-demand),
  // and the same sawmill in the continuous mode the Curta has to mount in, to
  // tell the cost of the model from the cost of the render mode.
  if(want('posed'))for(const mode of ['on-demand','continuous'])for(const [w,h] of [[1920,1080],[960,540]]){
    results.load[`posed-${mode}-${h}`]=await load();
    const {page}=await openPage(browser,server.origin,w,h);
    await page.addStyleTag({content:HIDE_CHROME});
    const m=await mount(page,'posed',{time:0,renderMode:mode});
    const view=await page.evaluate(()=>{const v=window.viewer.view(),a=x=>[x.x,x.y,x.z];return {camera:a(v.camera),target:a(v.target)};});
    if(w===960&&mode==='on-demand')await page.screenshot({path:join(stills,'posed-baseline.png')});
    results.cost[`posed-${mode}-${h}`]={mountMs:+m.ms.toFixed(0),...await cost(page,i=>page.evaluate(([t,view])=>{
      const t0=performance.now();window.viewer.setTime(t);const t1=performance.now();window.viewer.setView(view);const t2=performance.now();
      return {setTime:t1-t0,setView:t2-t1};},[(i%30)/30,view]))};
    console.log(`cost posed-${mode}-${h}`,JSON.stringify(results.cost[`posed-${mode}-${h}`]));
    await page.close();
  }
  results.load.end=await load();
}finally{
  await writeFile(resultsFile,JSON.stringify(results,null,1)+'\n');
  await close();await server.close();
}
