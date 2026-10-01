// Summaries of measure.mjs results: per phase mean, median, p10, p90, min,
// max in ms and the median's share of the median frame; the CPU each
// Chromium process spent; per probe of an alternatives run the same, with
// its bytes and decoded pixels against the baseline's of the same frame.
//   node summarize.mjs RESULT.json... > summary.txt
//   node summarize.mjs --json RESULT.json... > summary.json
import {readFile} from 'node:fs/promises';
import {basename} from 'node:path';

const args=process.argv.slice(2),asJson=args[0]==='--json',files=asJson?args.slice(1):args;
const q=(v,p)=>{const s=[...v].sort((x,y)=>x-y);if(!s.length)return NaN;const i=(s.length-1)*p,lo=Math.floor(i),hi=Math.ceil(i);return s[lo]+(s[hi]-s[lo])*(i-lo);};
const stats=v=>({n:v.length,mean:v.reduce((x,y)=>x+y,0)/v.length,median:q(v,.5),p10:q(v,.1),p90:q(v,.9),min:Math.min(...v),max:Math.max(...v)});
const f=x=>Number.isFinite(x)?(Math.abs(x)>=100?x.toFixed(0):x.toFixed(1)):'-';
const line=(name,s,total)=>`${name.padEnd(34)} ${f(s.mean).padStart(8)} ${f(s.median).padStart(8)} ${f(s.p10).padStart(8)} ${f(s.p90).padStart(8)} ${f(s.min).padStart(8)} ${f(s.max).padStart(8)}${total?` ${(100*s.median/total).toFixed(1).padStart(6)} %`:''}`;
const head=`${'phase (ms)'.padEnd(34)} ${'mean'.padStart(8)} ${'median'.padStart(8)} ${'p10'.padStart(8)} ${'p90'.padStart(8)} ${'min'.padStart(8)} ${'max'.padStart(8)}  share`;

function phaseRows(rows,{dropFirst}){
  const r=dropFirst?rows.slice(1):rows;
  const col=k=>r.map(x=>typeof k==='function'?k(x):x[k]??0);
  const total=x=>x.pose+x.screenshot+x.pngCheck+x.write+x.rename+x.hash+x.link;
  const phases={
    'frame (all phases)':col(total),
    'pose: total (Node)':col('pose'),
    '  setFrame round trip':col('setFrame'),
    '    in page: setFrame':col(x=>x.page.setFrame),
    '      restore (bank)':col(x=>x.page.restore),
    '      setView (camera, draw call)':col(x=>x.page.setView),
    '      animation-frame waits':col(x=>x.page.rafWait),
    '      rest (React, marks, measure)':col(x=>x.page.setFrame-x.page.restore-x.page.setView-x.page.setTime-x.page.highlight-x.page.rafWait),
    '    evaluate overhead':col(x=>x.setFrame-x.page.setFrame),
    '  checks (Node)':col('checks'),
    '  inner screenshots (joins, fades)':col('innerScreenshot'),
    '  compose (joins, fades)':col('compose'),
    '  frame resolution, bookkeeping':col(x=>x.pose-(x.setFrame??0)-(x.checks??0)-(x.innerScreenshot??0)-(x.compose??0)),
    'screenshot (page.screenshot)':col('screenshot'),
    'Node: PNG check':col('pngCheck'),
    'Node: write':col('write'),
    'Node: rename':col('rename'),
    'Node: sha256':col('hash'),
    'Node: link':col('link'),
  };
  const s=Object.fromEntries(Object.entries(phases).map(([k,v])=>[k,stats(v)]));
  const cpuKeys=[...new Set(r.flatMap(x=>[...Object.keys(x.cpuScreenshot),...Object.keys(x.cpuPose)]))].filter(k=>!['zygote','other','utility'].includes(k)||r.some(x=>x.cpuScreenshot[k]||x.cpuPose[k]));
  const cpu=Object.fromEntries(cpuKeys.flatMap(k=>[[`cpu during pose: ${k}`,stats(col(x=>x.cpuPose[k]??0))],[`cpu during screenshot: ${k}`,stats(col(x=>x.cpuScreenshot[k]??0))]]));
  return {stats:s,cpu,load1:stats(col('load1')),rafFrames:r.filter(x=>x.page.rafCount>0).length,frames:r.length,
    transitions:r.filter(x=>x.transition).length,bytes:stats(col('bytes')),firstFrame:dropFirst?{pose:rows[0].pose,screenshot:rows[0].screenshot}:null};
}

const out={};const text=[];
for(const file of files){
  const r=JSON.parse(await readFile(file,'utf8'));const name=basename(file);
  text.push(`== ${name}: mode ${r.mode}, shot ${r.shot}, ${r.frameCount} frames (${r.frames?.[0]?.index}..${r.frames?.at(-1)?.index}), ${r.environment?.width??r.runs.find(x=>x.environment)?.environment.width}×${r.environment?.height??r.runs.find(x=>x.environment)?.environment.height}, wall ${(r.wallMs/1000).toFixed(1)} s, load1 ${r.load1Start} → ${r.load1End}`);
  if(r.mode==='phases'||r.mode==='flags'){
    for(const run of r.runs){
      if(!run.rows){text.push(`-- ${run.variant} round ${run.round}: ${run.error}`);continue;}
      const p=phaseRows(run.rows,{dropFirst:true});
      out[`${name}:${run.variant}:${run.round??0}`]=p;
      text.push(`-- variant ${run.variant}${run.round!==undefined?` round ${run.round}`:''}${run.environment?`: ${run.environment.webgl?.view?.renderer}`:''}; first frame excluded (pose ${f(p.firstFrame.pose)}, screenshot ${f(p.firstFrame.screenshot)}); ${p.frames} frames, ${p.rafFrames} with animation-frame waits, ${p.transitions} in a join; load1 median ${f(p.load1.median)} (${f(p.load1.min)}–${f(p.load1.max)}); PNG ${f(p.bytes.median/1024)} KiB`);
      text.push(head);
      const total=p.stats['frame (all phases)'].median;
      for(const [k,s] of Object.entries(p.stats))text.push(line(k,s,k.startsWith('frame')?null:total));
      text.push(`${'CPU ms per frame, by process'.padEnd(34)}`);
      for(const [k,s] of Object.entries(p.cpu))if(s.max>0)text.push(line(k,s));
    }
    if(r.mode==='flags'){
      // Bytes across variants, frame by frame.
      const byVariant={};for(const run of r.runs)if(run.rows)(byVariant[run.variant]??=[]).push(new Map(run.rows.map(x=>[x.index,x.sha256])));
      const ref=byVariant.stage?.[0];
      for(const [v,maps] of Object.entries(byVariant)){
        const same=maps.map(m=>[...m].filter(([i,h])=>ref?.get(i)===h).length);
        text.push(`bytes equal to stage round 0, ${v}: ${same.join(', ')} of ${maps.map(m=>m.size).join(', ')} frames`);
      }
    }
  }else if(r.mode==='parallel'){
    // The CPU columns of a run with two sessions sum both browsers.
    for(const run of r.runs){
      const shot=stats(run.rows.map(x=>x.screenshot));
      text.push(`${run.variant} round ${run.round}: load1 ${f(run.load1)} at its start; slices ${run.sliceMs.map(x=>(x/1000).toFixed(1)).join(', ')} s; ${(1/run.framesPerSecond*1000).toFixed(0)} ms of wall per frame (${run.framesPerSecond.toFixed(3)} frames/s); screenshot median ${f(shot.median)} ms in each session`);
      out[`${name}:${run.variant}:${run.round}`]={msPerFrame:1000/run.framesPerSecond,screenshot:shot,load1:run.load1};
    }
  }else if(r.mode==='alternatives'){
    const rows=r.runs[0].rows.slice(1);
    const names=[...new Set(rows.flatMap(x=>x.probes.map(p=>p.name)))];
    const res={};
    text.push(`first frame excluded; ${rows.length} frames, probes in this order per frame, each after its own pose: ${names.join(', ')}`);
    text.push(`${'probe (ms)'.padEnd(34)} ${'mean'.padStart(8)} ${'median'.padStart(8)} ${'p10'.padStart(8)} ${'p90'.padStart(8)} ${'min'.padStart(8)} ${'max'.padStart(8)}  vs png`);
    const base=stats(rows.map(x=>x.probes.find(p=>p.name==='png').ms));
    for(const n of names){
      const ps=rows.map(x=>x.probes.find(p=>p.name===n)).filter(Boolean);
      const err=ps.filter(p=>p.error);
      const val=k=>stats(ps.filter(p=>!p.error).map(k));
      const entry={};
      if(ps.some(p=>p.ms!==undefined)){entry.ms=val(p=>p.ms);text.push(line(n,entry.ms)+`  ${(entry.ms.median/base.median).toFixed(2)}×`);}
      if(ps.some(p=>p.finish!==undefined)){entry.finish=val(p=>p.finish);text.push(line(`  ${n}: gl.finish before`,entry.finish));}
      if(ps.some(p=>p.firstMs!==undefined)){entry.firstMs=val(p=>p.firstMs);text.push(line(`  ${n}: the first capture before it`,entry.firstMs));}
      if(ps.some(p=>p.raf!==undefined)){entry.raf=val(p=>p.raf);text.push(line(`  ${n}: two animation frames`,entry.raf));}
      if(ps.some(p=>p.redraw)){entry.setView=val(p=>p.redraw.setView);entry.redraw=val(p=>p.redraw.ms);
        text.push(line(`  ${n}: setView again`,entry.setView));text.push(line(`  ${n}: then the read/finish`,entry.redraw));}
      if(ps.some(p=>p.cpu)){
        for(const k of ['gpu-process','browser','renderer','node']){const s=val(p=>p.cpu?.[k]??0);if(s.max>0){entry[`cpu:${k}`]=s;text.push(line(`  ${n}: cpu ${k}`,s));}}
      }
      entry.pose=val(p=>p.pose);
      // Bytes and pixels against the first baseline of the same frame.
      if(ps.some(p=>p.sha256)){
        let sameBytes=0,samePixels=0,count=0;
        for(const x of rows){const b=x.probes.find(p=>p.name==='png'),p=x.probes.find(p=>p.name===n);if(!p?.sha256)continue;count++;
          if(p.sha256===b.sha256)sameBytes++;if(p.pixels&&p.pixels===b.pixels)samePixels++;}
        entry.bytesEqual=`${sameBytes}/${count}`;entry.pixelsEqual=`${samePixels}/${count}`;
        entry.size=val(p=>p.size??0);
        text.push(`  ${n}: bytes equal to baseline ${sameBytes}/${count}, decoded pixels equal ${samePixels}/${count}, size median ${f(entry.size.median/1024)} KiB`);
      }
      if(err.length)text.push(`  ${n}: ${err.length} errors, first: ${err[0].error.slice(0,200)}`);
      res[n]=entry;
    }
    const load=stats(rows.flatMap(x=>x.probes.map(p=>p.load1)));
    text.push(`load1 over the probes: median ${f(load.median)} (${f(load.min)}–${f(load.max)})`);
    out[name]={probes:res,load1:load};
  }
  text.push('');
}
console.log(asJson?JSON.stringify(out,null,1):text.join('\n'));
