import {test} from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {loadEpisode} from '../../src/episode.mjs';
import {prepareWordTimingForCommand} from '../../src/command-timing.mjs';
import {browserSession,preview} from '../../src/render.mjs';
import {frameAt} from '../../src/timeline.mjs';
import {decodePng,largestDifference,at,hexColor,chromeMask} from '../../src/pixels.mjs';

const project='/home/asa/devel/machinome/projects/Leonardo/videos/demo-source-only';
const viewer='/home/asa/devel/machinome/machinome-viewer/WTs/film-production-order/machinome_viewer/widget/dist/machinome-viewer.js';
// Never overwrite earlier diagnostic captures: each explicit run gets its own
// ignored output root, even when a test stops before writing a report.
const evidence=await mkdtemp(resolve('_build/source-only-real-'));
console.log(`Source-only real-browser evidence: ${evidence}`);
async function fixture(name){
  // The authored opt-in cannot pass the old parser. Load its otherwise identical
  // baseline, then inject the explicit presentation only at the browser seam.
  const e=await loadEpisode(resolve(project,'episode-baseline.yaml'));
  await prepareWordTimingForCommand(e,{command:'render',silent:true,fps:e.output.fps});
  e.shots[1].layout='source-only';e.paths.build=resolve(evidence,name);
  await mkdir(e.paths.build,{recursive:true});
  return e;
}
const close=(a,b)=>Math.abs(a-b)<=1;
async function appearance(page){return page.evaluate(()=>{
  const s=document.querySelector('#source'),v=document.querySelector('#viewport'),r=s.getBoundingClientRect();
  const p=document.querySelector('#progress').getBoundingClientRect();
  return {source:{display:getComputedStyle(s).display,visible:getComputedStyle(s).visibility,
      x:r.x,y:r.y,width:r.width,height:r.height,text:document.querySelector('#source-code').textContent},
    viewer:{display:getComputedStyle(v).display,visible:getComputedStyle(v).visibility},
    brand:document.querySelector('#brand').textContent,series:document.querySelector('#series').textContent,
    progress:p.width,marks:[...document.querySelectorAll('#source-code mark.spoken')].map(m=>m.textContent)};
});}
function sourceBounds(seen){
  assert.equal(seen.source.display,'block','the literal source panel is visible');
  assert.ok(close(seen.source.x,48)&&close(seen.source.y,86.4)&&close(seen.source.width,864)&&close(seen.source.height,340.2),
    `source-only must fill the plain content rectangle: ${JSON.stringify(seen.source)}`);
  assert.ok(seen.viewer.display==='none'||seen.viewer.visible==='hidden','the source shot has no visible model pane');
}

test('injected source-only browser request has literal source, fitted plain-stage bounds, chrome, typing, measured marks and exact replay',async()=>{
  const e=await fixture('appearance');
  const result=await browserSession(e,viewer,960,[],async({page,pose})=>{
    const source='source-only';
    await pose(1.4,{layout:source,transition:null});
    const partial=await appearance(page),partialPng=await page.screenshot();
    await writeFile(resolve(e.paths.build,'typed.png'),partialPng);
    await pose(2.5,{layout:source,transition:null});
    const full=await appearance(page),first=await page.screenshot();
    await writeFile(resolve(e.paths.build,'full.png'),first);
    const timing=e.wordTiming.source.emphasis[0].cues[0],onset=1.15+timing.from;
    await pose(onset,{layout:source,transition:null});
    const measured=await appearance(page),onsetPng=await page.screenshot();
    await writeFile(resolve(e.paths.build,'measured-onset.png'),onsetPng);
    await pose(5.4);await pose(2.5,{layout:source,transition:null});
    const again=await page.screenshot();
    await writeFile(resolve(e.paths.build,'replayed.png'),again);
    return {partial,full,measured,replay:first.equals(again),expected:e.sourceCode['wheel-coupling'].text,
      measuredWord:timing.word,onset,frame:frameAt(e,onset)};
  });
  assert.ok(result.partial.source.text.length>0&&result.partial.source.text.length<result.expected.length,'typing is partial');
  assert.equal(result.full.source.text,result.expected,'pinned literal statement reaches the picture');
  assert.equal(result.measured.source.text,result.frame.code.text,'the onset displays exactly the text typed at that instant');
  assert.ok(result.measured.marks.includes(result.measuredWord),`measured ${result.measuredWord} must be visibly marked`);
  assert.ok(result.full.brand?.includes('MACHINOME')&&result.full.series?.length>0&&result.full.progress>0,'film chrome remains');
  assert.equal(result.replay,true,'seek away/back restores exact bytes');
  sourceBounds(result.full);
});

test('an excerpt too tall for the source-only panel retains the named overflow refusal',async()=>{
  const e=await fixture('overflow');
  const extra=Array.from({length:90},(_,i)=>`wheel_${i} = crankshaft_${i}`).join('\n');
  const snippet=e.sourceCode['wheel-coupling'];snippet.text+='\n'+extra;snippet.lines=[415,505];
  e.shots[1].code.typing=[{from:0,to:.8,throughLine:505}];
  await assert.rejects(browserSession(e,viewer,960,[],async({pose})=>{
    await pose(2.5,{layout:'source-only',transition:null});
  }),/Source excerpt overflows the panel: source at 2\.50 s; select fewer lines/);
});

test('a hidden source-only lens change is not reported as visible projection; visible model control still is',async()=>{
  const e=await fixture('lens');
  const original=e.cameras['drive-near'];
  e.cameras['source-roll']={...original,up:[1,0,1],fov:24};
  e.shots[1].camera=[{at:0,preset:'drive-near'},{at:2,preset:'source-roll'}];
  const report=await preview(e,{viewer,width:960,captions:[]});
  const source=report.cameraChecks?.filter(c=>c.shotId==='source')??[];
  assert.ok(source.length>0,'source-only changed up/FOV remains a resolved pose check');
  assert.ok(source.every(c=>c.measured===undefined&&c.expected===undefined&&c.visibleProjection!==true),
    `hidden source viewer cannot be claimed as visible lens evidence: ${JSON.stringify(source)}`);
  const visible=await fixture('visible-lens');delete visible.shots[1].layout;
  visible.cameras['split-roll']={...visible.cameras['drive-near'],up:[1,0,1],fov:24};
  visible.shots[1].camera=[{at:0,preset:'drive-near'},{at:2,preset:'split-roll'}];
  const control=await preview(visible,{viewer,width:960,captions:[]});
  assert.ok(control.cameraChecks?.some(c=>c.shotId==='source'&&Number.isFinite(c.measured)&&Number.isFinite(c.expected)));
});

test('all four joins use each side source-only or model independently and prove same-instant pixels',async()=>{
  const e=await fixture('joins');
  const outcomes=[];
  await browserSession(e,viewer,960,[],async({page,pose})=>{
    for(const kind of ['fade','dissolve','wipe','slide']){
      for(const shot of [e.shots[1],e.shots[2]])shot.transition={kind,duration:.4,
        ...(['wipe','slide'].includes(kind)?{direction:'left'}:{})};
      for(const [side,time] of [['incoming',1.15+(kind==='fade'?.3:.2)],
        ['outgoing',4.65+(kind==='fade'?.1:.2)]]){
        const baseline=frameAt(e,time),x=baseline.transition;
        const opted={layout:side==='incoming'?'source-only':undefined,
          transition:{...x,outgoing:x.outgoing&&{...x.outgoing,
            ...(side==='outgoing'?{layout:'source-only'}:{})}}};
        const posed=await pose(time,opted,{fresh:true});const composed=await page.screenshot();
        await writeFile(resolve(e.paths.build,`${kind}-${side}-composed.png`),composed);
        const plainTransition={...x,outgoing:x.outgoing&&{...x.outgoing,layout:undefined}};
        await pose(time,{layout:undefined,transition:plainTransition},{fresh:true});const oldSplit=await page.screenshot();
        await writeFile(resolve(e.paths.build,`${kind}-${side}-split-control.png`),oldSplit);
        const incoming={transition:null,layout:side==='incoming'?'source-only':undefined};
        const outgoing={...x.outgoing,transition:null,layout:side==='outgoing'?'source-only':undefined};
        const grab=async(request,options={})=>{
          await pose(time,request,{fresh:true,...options});return decodePng(await page.screenshot());
        };
        const A=await grab(outgoing),B=await grab(incoming);
        await pose(time,side==='incoming'?incoming:outgoing,{fresh:true});
        const sourceWidth=(await appearance(page)).source.width;
        await writeFile(resolve(e.paths.build,`${kind}-${side}-source.png`),await page.screenshot());
        const image=decodePng(composed),p=x.progress,s=Math.round(p*960),left=x.direction==='left';
        const mask=chromeMask(960,image.height,posed.observed.chrome);
        let largest,limit;
        if(kind==='dissolve'){
          largest=largestDifference(image,(px,y,k)=>(1-p)*at(A,px,y,k)+p*at(B,px,y,k));limit=2;
        }else if(kind==='wipe'){
          largest=largestDifference(image,(px,y,k)=>(left?px>=960-s:px<s)?at(B,px,y,k):at(A,px,y,k));limit=0;
        }else if(kind==='slide'){
          const a=await grab(outgoing,{pictureOnly:true}),b=await grab(incoming,{pictureOnly:true});
          largest=largestDifference(image,(px,y,k)=>left?
            (px<960-s?at(a,px+s,y,k):at(b,px-960+s,y,k)):
            (px>=s?at(a,px-s,y,k):at(b,px-s+960,y,k)),mask);limit=0;
        }else{
          const color=hexColor(x.color),plain=x.picture==='outgoing'?A:B;
          largest=largestDifference(image,(px,y,k)=>x.plate*color[k]+(1-x.plate)*at(plain,px,y,k),mask);limit=2;
        }
        outcomes.push({kind,side,changed:!composed.equals(oldSplit),sourceWidth,largest,limit});
      }
    }
    return {};
  });
  assert.ok(outcomes.every(x=>x.changed&&close(x.sourceWidth,864)&&x.largest<=x.limit),
    `opted source picture must affect both sides of every join: ${JSON.stringify(outcomes)}`);
});
