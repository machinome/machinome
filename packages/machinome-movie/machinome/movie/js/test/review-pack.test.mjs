import {test} from 'node:test';
import assert from 'node:assert/strict';
import {spawn,execFileSync,spawnSync} from 'node:child_process';
import {once} from 'node:events';
import {mkdtemp,mkdir,readFile,readdir,writeFile,appendFile,chmod,stat,rm,symlink,unlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {dirname,join,resolve,delimiter} from 'node:path';
import {fileHash} from '../src/util.mjs';
import {decodePng} from '../src/pixels.mjs';
import {render} from '../src/render.mjs';

const cli=resolve('bin/videomaker.mjs');
const packModule=await import('../src/review-pack.mjs').catch(error=>{
  if(error.code==='ERR_MODULE_NOT_FOUND')return null;
  throw error;
});
function reviewManifest(path,options){
  assert.equal(typeof packModule?.reviewManifest,'function',
    'encoded-film review generator is absent before implementation');
  return packModule.reviewManifest(path,options);
}
function needHelper(name){
  assert.equal(typeof packModule?.[name],'function',`${name} is absent before implementation`);
  return packModule[name];
}
async function root(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-review-pack-'));
  t.after(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Preserved review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  return dir;
}
const label=(kind,description='resolved candidate')=>({kind,shotId:'B',side:'incoming',
  authoredIndex:0,wordOrdinal:0,description,visibility:'resolved candidate, not reviewed'});
function samplePlan(count=8,fps=4){
  return {schema:'review-samples-v1',frameCount:count,fps,samples:[
    {indices:[2,3],labels:[{kind:'join',shotId:'B',outgoingShotId:'A',sides:['outgoing','incoming'],
      description:'A to B',visibility:'resolved candidate, not reviewed'}]},
    {indices:[3],labels:[{kind:'transition-midpoint',shotId:'B',field:'transition',sides:['outgoing','incoming'],
      description:'B transition midpoint',visibility:'resolved candidate, not reviewed'}]},
    {indices:[Math.max(0,count-2),count-1],labels:[{kind:'film-end',shotId:'B',
      description:'film end',visibility:'resolved candidate, not reviewed'}]}]};
}
async function filmFixture(t,{count=8,fps=4,width=160,height=90,plan=samplePlan(count,fps)}={}){
  const dir=await root(t),output=join(dir,'review.mp4'),manifestPath=join(dir,'review-manifest.json');
  execFileSync('ffmpeg',['-y','-v','error','-f','lavfi','-i',`testsrc2=size=${width}x${height}:rate=${fps}`,
    '-frames:v',String(count),'-c:v','libx264','-pix_fmt','yuv420p',
    '-output_ts_offset','2','-movflags','+faststart',output]);
  const manifest={count,width,height,fps,output,outputSha256:await fileHash(output),reviewSamples:plan,
    // Review must not load this author's YAML, source, speech, model or build path.
    episode:{paths:{episode:join(dir,'missing-episode.yaml'),build:join(dir,'wrong-build-root')}}};
  const save=async()=>writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n');
  await save();return {dir,output,manifestPath,manifest,save};
}
async function indexOf(result){
  assert.equal(typeof result?.generation,'string');
  const index=JSON.parse(await readFile(join(result.generation,'index.json'),'utf8'));
  assert.equal(index.schema,'review-pack-v1');
  assert.equal(index.status,'generated, not reviewed');
  return index;
}
async function completeIndexes(dir){
  const folder=join(dir,'review-packs');let generations=[];
  try{generations=await readdir(folder);}catch(error){if(error.code==='ENOENT')return [];throw error;}
  const found=[];
  for(const name of generations){
    try{await stat(join(folder,name,'index.json'));found.push(join(folder,name));}
    catch(error){if(error.code!=='ENOENT')throw error;}
  }
  return found;
}
const runCli=(manifestPath,env=process.env)=>spawnSync(process.execPath,[cli,'review',manifestPath],
  {encoding:'utf8',env,timeout:30000});
const delay=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const closedWithin=(completion,ms)=>Promise.race([completion.then(()=>true),delay(ms).then(()=>false)]);
async function reapOwnedGroup(child,completion,gate){
  // Release a waiting wrapper on every assertion path. The spawned command is
  // its own process group; never signal an unrelated process or broad pattern.
  await writeFile(gate,'continue').catch(()=>{});
  if(await closedWithin(completion,1500))return;
  if(Number.isSafeInteger(child.pid)&&child.pid>0){
    try{process.kill(-child.pid,'SIGTERM');}catch(error){if(error.code!=='ESRCH')throw error;}
    if(await closedWithin(completion,1000))return;
    try{process.kill(-child.pid,'SIGKILL');}catch(error){if(error.code!=='ESRCH')throw error;}
  }
  assert.ok(await closedWithin(completion,2000),'owned review/FFmpeg process group did not reap');
}

test('standalone review is a manifest route, before episode/source/viewer resolution',async t=>{
  const {manifestPath,dir}=await filmFixture(t);
  const result=runCli(manifestPath);
  assert.equal(result.status,0,`review MANIFEST.json must succeed without author sources: ${result.stderr}`);
  assert.ok((await completeIndexes(dir)).length===1);
});

test('symlinked catalogue manifest owns and reuses a canonical pack without following escaping artifacts',async t=>{
  const {dir,manifestPath}=await filmFixture(t);
  const aliasRoot=await root(t),alias=join(aliasRoot,'project');
  await symlink(dir,alias,'dir');
  const throughAlias=join(alias,'review-manifest.json');
  const generated=await reviewManifest(throughAlias);
  assert.equal(generated.reused,false);
  assert.equal(dirname(dirname(generated.generation)),dir,
    'the generation belongs to the real manifest directory, not a lexical alias');
  const direct=await reviewManifest(manifestPath);
  assert.equal(direct.reused,true,'real and alias routes identify the same verified generation');
  assert.equal(direct.generation,generated.generation);
  const aliasAgain=await reviewManifest(throughAlias);
  assert.equal(aliasAgain.reused,true);
  assert.equal(aliasAgain.generation,generated.generation);
  const cliResult=runCli(throughAlias);
  assert.equal(cliResult.status,0,`standalone CLI accepts the catalogue alias: ${cliResult.stderr}`);
  assert.equal((await completeIndexes(dir)).length,1,'CLI reuse publishes no duplicate generation');

  const index=await indexOf(generated),frame=index.selectedFrames[0];
  assert.equal(index.inputs.manifest.path,manifestPath,'recorded provenance uses the canonical manifest');
  const artifact=join(generated.generation,frame.file),outside=join(aliasRoot,'outside.png');
  await writeFile(outside,await readFile(artifact));
  assert.equal(await fileHash(outside),frame.sha256,
    'the outside bait has the exact hash expected by the complete index');
  await unlink(artifact);
  await symlink(outside,artifact,'file');
  const regenerated=await reviewManifest(throughAlias);
  assert.equal(regenerated.reused,false,'a hash-matching artifact symlink outside the generation is refused');
  assert.notEqual(regenerated.generation,generated.generation);
});

test('standalone legacy manifest refusal asks for rerender, not an episode or unknown command',async t=>{
  const {dir,manifestPath,manifest,save}=await filmFixture(t);
  delete manifest.reviewSamples;await save();
  const result=runCli(manifestPath);
  assert.notEqual(result.status,0);
  assert.match(result.stderr,/review.*plan|rerender|review-samples-v1/i);
  assert.doesNotMatch(result.stderr,/Unknown command|ENOENT.*episode/i);
  assert.deepEqual(await completeIndexes(dir),[]);
});

test('matching film yields exact decoded selected PNGs and actual display-order PTS',async t=>{
  const {dir,output,manifestPath,manifest}=await filmFixture(t);
  const result=await reviewManifest(manifestPath),index=await indexOf(result);
  assert.equal(dirname(dirname(result.generation)),dir,'pack belongs to the selected manifest directory');
  assert.equal(index.inputs.manifest.sha256,await fileHash(manifestPath));
  assert.equal(index.inputs.mp4.sha256,manifest.outputSha256);
  assert.equal(index.film.count,8);assert.deepEqual([index.film.width,index.film.height,index.film.fps],[160,90,4]);
  const raw=execFileSync('ffmpeg',['-v','error','-i',output,'-f','rawvideo','-pix_fmt','rgb24','pipe:1']);
  const bytesPerFrame=160*90*3;
  assert.equal(raw.length,bytesPerFrame*8,'independent decoder produced exactly all eight display-order frames');
  const probe=JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_streams',
    '-show_frames','-show_entries','stream=time_base:frame=pts','-of','json',output],{encoding:'utf8'}));
  const pts=probe.frames.filter(f=>f.pts!==undefined);
  assert.equal(pts.length,8);
  assert.ok(Number(pts[0].pts)>0,
    'the fixture starts at a nonzero encoded PTS, so n/fps cannot impersonate actual PTS');
  assert.ok(index.selectedFrames.length>0);
  for(const selected of index.selectedFrames){
    assert.ok(Number.isInteger(selected.index)&&selected.index>=0&&selected.index<8);
    assert.equal(String(selected.ptsTicks),String(pts[selected.index].pts));
    assert.ok(Number.isSafeInteger(Number(selected.ptsTicks)));
    assert.equal(selected.timeBase,probe.streams[0].time_base);
    assert.equal(selected.sha256,await fileHash(join(result.generation,selected.file)));
    const decoded=decodePng(await readFile(join(result.generation,selected.file)));
    assert.deepEqual([decoded.width,decoded.height],[160,90]);
    assert.ok(decoded.rgb.equals(raw.subarray(selected.index*bytesPerFrame,(selected.index+1)*bytesPerFrame)),
      `selected frame ${selected.index} is exact decoded MP4 pixels, not shot-cache pixels`);
  }
  assert.ok(index.selectedFrames.some(f=>f.index===0));
  assert.ok(index.selectedFrames.some(f=>f.index===7));
});

test('tampered MP4, legacy plan and malformed plan refuse without loading frameAt',async t=>{
  const {dir,output,manifestPath,manifest,save}=await filmFixture(t);
  await appendFile(output,Buffer.from([0]));
  await assert.rejects(reviewManifest(manifestPath),/hash|SHA|mismatch/i);
  assert.deepEqual(await completeIndexes(dir),[]);
  manifest.outputSha256=await fileHash(output);
  delete manifest.reviewSamples;await save();
  await assert.rejects(reviewManifest(manifestPath),/review.*plan|rerender|review-samples-v1/i);
  assert.deepEqual(await completeIndexes(dir),[]);
  manifest.reviewSamples={schema:'review-samples-v0',frameCount:8,fps:4,samples:[]};await save();
  await assert.rejects(reviewManifest(manifestPath),/review.*plan|rerender|review-samples-v1/i);
  manifest.reviewSamples={schema:'review-samples-v1',frameCount:8,fps:4,
    samples:[{indices:[8,9],labels:[label('word-onset')]}]};await save();
  await assert.rejects(reviewManifest(manifestPath),/plan|index|frame|range/i);
  manifest.reviewSamples=samplePlan();manifest.reviewSamples.samples.pop();await save();
  await assert.rejects(reviewManifest(manifestPath),/plan|film.end|rerender/i,
    'a v1 plan with no film-end evidence is not a complete plan');
  manifest.reviewSamples=samplePlan();manifest.reviewSamples.samples[0].labels[0].kind='unknown-kind';await save();
  await assert.rejects(reviewManifest(manifestPath),/plan|kind|rerender/i);
  manifest.reviewSamples=samplePlan();delete manifest.reviewSamples.samples[0].labels[0].visibility;await save();
  await assert.rejects(reviewManifest(manifestPath),/plan|candidate|rerender/i);
  assert.deepEqual(await completeIndexes(dir),[]);
});

test('internally incomplete or contradictory complete indexes regenerate instead of verifying reuse',async t=>{
  const {manifestPath}=await filmFixture(t);
  let current=await reviewManifest(manifestPath);
  const cases=[
    index=>{index.selectedFrames=[];},
    index=>{index.selectedFrames.pop();},
    index=>{index.selectedFrames[1]={...index.selectedFrames[0]};},
    index=>{index.pages=index.pages.filter(page=>page.kind!=='events');},
    index=>{index.film.width++;},
    index=>{index.pages[0].cells[0].labels=[label('word-onset','forged label')];},
    index=>{index.selectedFrames[0].ptsTicks=null;},
  ];
  for(const mutate of cases){
    const file=join(current.generation,'index.json'),damaged=JSON.parse(await readFile(file,'utf8'));
    mutate(damaged);await writeFile(file,JSON.stringify(damaged));
    const next=await reviewManifest(manifestPath);
    assert.equal(next.reused,false,'a corrupted complete index cannot be a verified hit');
    assert.notEqual(next.generation,current.generation);
    current=next;
  }
});

test('a real decode refuses manifest frame-count and dimension disagreement',async t=>{
  const {dir,manifestPath,manifest,save}=await filmFixture(t);
  manifest.count=9;manifest.reviewSamples=samplePlan(9);await save();
  await assert.rejects(reviewManifest(manifestPath),/Decoded frame count differs from the manifest/i);
  assert.deepEqual(await completeIndexes(dir),[]);
  manifest.count=8;manifest.reviewSamples=samplePlan(8);manifest.width=162;await save();
  await assert.rejects(reviewManifest(manifestPath),/Decoded video stream dimensions differ from manifest/i);
  assert.deepEqual(await completeIndexes(dir),[]);
});

test('decoded metadata rejects missing/nonincreasing PTS, frame count or dimensions',()=>{
  const validate=needHelper('validateDecodedFrames');
  const film={count:3,width:160,height:90};
  const good=[0,1,2].map(i=>({index:i,ptsTicks:32768+i*4096,timeBase:'1/16384',width:160,height:90}));
  assert.doesNotThrow(()=>validate(good,film));
  assert.doesNotThrow(()=>validate([{index:0,ptsTicks:32768,timeBase:'1/16384',width:160,height:90}],
    {count:1,width:160,height:90}));
  assert.throws(()=>validate([{index:0,ptsTicks:null,timeBase:'1/16384',width:160,height:90}],
    {count:1,width:160,height:90}),/PTS|timestamp/i,
    'null on a one-frame film is missing, not integer zero');
  assert.throws(()=>validate(good.slice(0,2),film),/count|frame/i);
  assert.throws(()=>validate(good.map((f,i)=>i===1?{...f,width:159}:f),film),/dimension|width/i);
  assert.throws(()=>validate(good.map((f,i)=>i===1?{...f,ptsTicks:null}:f),film),/PTS|timestamp/i);
  assert.throws(()=>validate(good.map((f,i)=>i===1?{...f,ptsTicks:32768}:f),film),/PTS|timestamp|increasing/i);
  assert.throws(()=>validate(good.map((f,i)=>i===1?{...f,index:2}:f),film),/index|order|frame/i);
});

test('overview and event pages keep 93/96 bound, 24 cells, adjacent pairs, padding and long full labels',()=>{
  const pagesFor=needHelper('planReviewPages');
  const count=1380,fps=30,long=`UNSAFE_USER_CUE_SENTINEL : ' " \\ [filter] ${'very long cue description '.repeat(40)}`;
  const samples=[];
  for(let i=0;i<15;i++)samples.push({indices:[200+i*2,201+i*2],labels:[label('word-onset',long),
    label('source-emphasis-onset',long)]});
  samples.push({indices:[402],labels:[label('transition-midpoint',long)]});
  samples.push({indices:[408],labels:[label('transition-last-active',long)]});
  const plan={schema:'review-samples-v1',frameCount:count,fps,samples};
  const metadata=new Map(Array.from({length:count},(_,i)=>[i,{index:i,ptsTicks:i*512,timeBase:'1/15360'}]));
  const layout=pagesFor(plan,metadata),overview=layout.pages.filter(p=>p.kind==='overview');
  const actualOverview=overview.flatMap(p=>p.cells.filter(c=>!c.padding).map(c=>c.index));
  assert.equal(actualOverview.length,93);assert.equal(new Set(actualOverview).size,93);
  assert.deepEqual(actualOverview.slice(0,4),[0,15,30,45]);
  assert.deepEqual(actualOverview.slice(-2),[1365,1379]);
  assert.ok(overview.every(p=>p.cells.length<=24));assert.equal(overview.length,4);
  assert.ok(overview.at(-1).cells.some(c=>c.padding===true),'padding is marked, not a black decoded frame');
  const events=layout.pages.filter(p=>p.kind==='events');
  assert.ok(events.length>=2);assert.ok(events.every(p=>p.cells.length<=24));
  const all=events.flatMap(p=>p.cells.filter(c=>!c.padding));
  for(const item of samples){
    const cells=all.filter(c=>item.indices.includes(c.index));
    assert.equal(cells.length,item.indices.length,`every sample ${item.indices} retained`);
    if(item.indices.length===2){
      const page=events.find(p=>p.cells.some(c=>c.index===item.indices[0]));
      const at=page.cells.findIndex(c=>c.index===item.indices[0]);
      assert.equal(page.cells[at+1].index,item.indices[1],'pair never splits across pages');
    }
  }
  assert.ok(events.every(p=>p.cells.filter(c=>c.pairStart).length<=12));
  assert.ok(all.some(c=>c.labels?.length===2),'shared pair retains both full labels');
  assert.ok(all.some(c=>c.labels?.some(l=>l.description===long)),'full description remains in index metadata');
  assert.ok(all.every(c=>c.printedLabel?.length<=80),'sheet text is fixed-format and bounded');
  assert.ok(all.every(c=>!c.printedLabel?.includes('UNSAFE_USER_CUE_SENTINEL')),
    'even a distinctive authored prefix never enters FFmpeg-visible label text');
  for(const page of layout.pages)for(const cell of page.cells){
    const box=cell.rect;
    assert.ok(box&&box.x>=0&&box.y>=0&&box.width>0&&box.height>0,
      'every cell has a real, nonnegative image/label rectangle');
    assert.ok(box.x+box.width<=page.width&&box.y+box.height<=page.height,
      'long or shared labels cannot overflow the sheet bounds');
  }
});

test('a live MP4 or manifest replaced during decode refuses despite a stable snapshot',async t=>{
  for(const target of ['mp4','manifest'])await t.test(target,async sub=>{
    const {dir,output,manifestPath,manifest}=await filmFixture(sub);
    const bin=join(dir,'bin');await mkdir(bin);
    const real=execFileSync('which',['ffmpeg'],{encoding:'utf8'}).trim();
    const wrapper=join(bin,'ffmpeg'),ready=join(dir,'decode-ready'),go=join(dir,'decode-go');
    await writeFile(wrapper,`#!/bin/sh\ncase " $* " in *".mp4"*) : > "$REVIEW_GATE_READY"; n=0; while [ ! -f "$REVIEW_GATE_GO" ]; do n=$((n+1)); [ "$n" -lt 200 ] || exit 124; sleep 0.05; done;; esac\nexec "$REVIEW_REAL_FFMPEG" "$@"\n`);
    await chmod(wrapper,0o755);
    const env={...process.env,PATH:bin+delimiter+process.env.PATH,REVIEW_GATE_READY:ready,
      REVIEW_GATE_GO:go,REVIEW_REAL_FFMPEG:real};
    const child=spawn(process.execPath,[cli,'review',manifestPath],{env,detached:true,stdio:['ignore','pipe','pipe']});
    const completion=once(child,'close'); // register before any gate/assertion can fail
    let stderr='';child.stderr.on('data',chunk=>stderr+=chunk);
    try{
      let gated=false;
      for(let n=0;n<200;n++){
        try{await stat(ready);gated=true;break;}catch(error){if(error.code!=='ENOENT')throw error;}
        if(child.exitCode!==null)break;
        await delay(50);
      }
      assert.ok(gated,`review did not reach decode after initial verification: ${stderr}`);
      if(target==='mp4')await appendFile(output,Buffer.from([0]));
      else await writeFile(manifestPath,JSON.stringify({...manifest,reviewNote:'changed during decode'})+'\n');
      await writeFile(go,'continue');
      assert.ok(await closedWithin(completion,10000),'review did not finish after decode gate release');
      const [code]=await completion;
      assert.notEqual(code,0,'changed live input must not publish a verified pack');
      assert.match(stderr,/changed|hash|mismatch|refus/i);
      assert.deepEqual(await completeIndexes(dir),[]);
    }finally{
      await reapOwnedGroup(child,completion,go);
    }
  });
});

test('verified reuse rechecks live inputs and every artifact path/hash; prior generations stay immutable',async t=>{
  const {dir,manifestPath,manifest,save}=await filmFixture(t);
  const first=await reviewManifest(manifestPath),index=await indexOf(first);
  const firstIndexBytes=await readFile(join(first.generation,'index.json'));
  const firstPage=join(first.generation,index.pages[0].file),firstPageBytes=await readFile(firstPage);
  const originalFilmBytes=await readFile(manifest.output);
  const reused=await reviewManifest(manifestPath);
  assert.equal(reused.reused,true);assert.equal(reused.generation,first.generation);
  await assert.rejects(reviewManifest(manifestPath,{beforeReuse:async()=>{
    await writeFile(manifestPath,JSON.stringify({...manifest,reviewNote:'replaced after verification'})+'\n');
  }}),/changed|hash|mismatch/i);
  assert.ok(firstIndexBytes.equals(await readFile(join(first.generation,'index.json'))));
  assert.ok(firstPageBytes.equals(await readFile(firstPage)));
  await save();
  await assert.rejects(reviewManifest(manifestPath,{beforeReuse:async()=>{
    await appendFile(manifest.output,Buffer.from([0]));
  }}),/changed|hash|mismatch/i);
  assert.ok(firstIndexBytes.equals(await readFile(join(first.generation,'index.json'))));
  await writeFile(manifest.output,originalFilmBytes);
  assert.equal(await fileHash(manifest.output),manifest.outputSha256);
  await appendFile(firstPage,Buffer.from([0]));
  const afterDamage=await reviewManifest(manifestPath);
  assert.equal(afterDamage.reused,false,'a corrupt artifact is not a verified pack hit');
  assert.notEqual(afterDamage.generation,first.generation);
  // An index-controlled relative path must never escape its own generation.
  const damaged=JSON.parse(await readFile(join(afterDamage.generation,'index.json'),'utf8'));
  const originalPageBytes=await readFile(join(afterDamage.generation,damaged.pages[0].file));
  await writeFile(join(dir,'outside.png'),originalPageBytes);
  assert.equal(await fileHash(join(dir,'outside.png')),damaged.pages[0].sha256,
    'a real, hash-matching bait file makes unchecked traversal appear reusable');
  damaged.pages[0].file='../../outside.png';
  await writeFile(join(afterDamage.generation,'index.json'),JSON.stringify(damaged));
  const afterUnsafe=await reviewManifest(manifestPath);
  assert.equal(afterUnsafe.reused,false,'unsafe artifact path is not followed or reused');
  assert.notEqual(afterUnsafe.generation,afterDamage.generation);
  manifest.reviewSamples.samples[0].labels[0].description='a changed full label';await save();
  const newInput=await reviewManifest(manifestPath);
  assert.notEqual(newInput.generation,afterUnsafe.generation);
  assert.ok((await completeIndexes(dir)).length>=4);
  assert.ok(firstIndexBytes.equals(await readFile(join(first.generation,'index.json'))));
});

test('a new manifest hash publishes a new generation without overwriting an old complete pack',async t=>{
  const {manifestPath,manifest,save}=await filmFixture(t);
  const first=await reviewManifest(manifestPath),index=await indexOf(first);
  const indexBytes=await readFile(join(first.generation,'index.json'));
  const pageBytes=await readFile(join(first.generation,index.pages[0].file));
  manifest.reviewSamples.samples[0].labels[0].description='reworded full label';await save();
  const second=await reviewManifest(manifestPath);
  assert.notEqual(second.generation,first.generation);
  assert.ok(indexBytes.equals(await readFile(join(first.generation,'index.json'))));
  assert.ok(pageBytes.equals(await readFile(join(first.generation,index.pages[0].file))));
});

test('interruption and mid-attempt input drift never publish a complete new index; retry succeeds',async t=>{
  const {dir,manifestPath,manifest}=await filmFixture(t);
  await assert.rejects(reviewManifest(manifestPath,{beforePublish:async()=>{throw new Error('injected pack interruption');}}),
    /injected pack interruption/);
  assert.deepEqual(await completeIndexes(dir),[]);
  await assert.rejects(reviewManifest(manifestPath,{beforePublish:async()=>{
    await writeFile(manifestPath,JSON.stringify({...manifest,reviewNote:'changed before publish'})+'\n');
  }}),/changed|hash|mismatch/i);
  assert.deepEqual(await completeIndexes(dir),[]);
  await writeFile(manifestPath,JSON.stringify(manifest,null,2)+'\n');
  const cliResult=runCli(manifestPath);
  assert.equal(cliResult.status,0,`standalone retry should complete: ${cliResult.stderr}`);
  assert.equal((await completeIndexes(dir)).length,1);
});

async function renderFixture(t){
  const dir=await root(t),build=join(dir,'_build');await mkdir(build);
  execFileSync('git',['init','-q'],{cwd:dir});
  await writeFile(join(dir,'episode.yaml'),'review render fixture');
  await writeFile(join(dir,'production.yaml'),'review render fixture');
  await writeFile(join(dir,'description.md'),'Review fixture.');
  await writeFile(join(dir,'model.json'),JSON.stringify({root:{name:'test'},animation:{loop:2}}));
  const viewer=join(dir,'viewer.js');
  await writeFile(viewer,`window.MachinomeViewer={async mount(selector,url,options){
    const canvas=document.createElement('canvas');canvas.style.width='100%';canvas.style.height='100%';
    document.querySelector(selector).append(canvas);let view={...options.view,up:options.up,fov:options.fov};
    return {apiVersion:28,setVisible(){},navigation(){return {}},
      setTime(t){canvas.style.background='rgb('+Math.round(t*180)+',90,160)'},
      setView(v){view={...view,...v}},
      view(){return {camera:{toArray:()=>view.camera},target:{toArray:()=>view.target},
        up:{toArray:()=>view.up},fov:view.fov}}};
  }};`);
  execFileSync('git',['add','.'],{cwd:dir});
  execFileSync('git',['-c','user.name=Test','-c','user.email=test@example.invalid','commit','-qm','fixture'],{cwd:dir});
  const episode={format:'machinome-video-draft/0.4',title:'Review',series:'Review',
    output:{width:320,height:180,fps:2,durationSeconds:2},model:{expectedDurationSeconds:2},
    style:{background:'#f5f1e8',foreground:'#222222',accent:'#bf531f',fontFamily:'DejaVu Sans'},
    paths:{repository:dir,episode:join(dir,'episode.yaml'),production:join(dir,'production.yaml'),
      manifest:join(dir,'model.json'),build},
    cameras:{a:{position:[0,-10,0],target:[0,0,0],up:[0,0,1],fov:37}},layers:{},
    release:{descriptionTemplate:'description.md'},shots:[
      {id:'A',start:0,end:1,narration:'',direction:'Look.',simulation:{from:0,to:1},
        camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[]},
      {id:'B',start:1,end:2,narration:'',direction:'Look.',simulation:{from:1,to:2},
        camera:[{at:0,preset:'a'}],hiddenLayers:[],overlays:[],evidence:[],
        transition:{kind:'dissolve',duration:.5}}]};
  return {dir,build,viewer,episode};
}
async function cliRenderFixture(t){
  const fixture=await renderFixture(t),{dir,episode}=fixture;
  const model={manifest:'model.json',timeMode:'normalized-loop',
    expectedDurationSeconds:2,sourceRevision:'fixture-revision'};
  const script={format:episode.format,production:'production.yaml',title:episode.title,
    series:episode.series,output:episode.output,style:episode.style,cameras:episode.cameras,
    layers:{},evidence:{},release:episode.release,
    shots:episode.shots.map(shot=>({...shot,id:shot.id.toLowerCase(),narration:'Look.',
      ...(shot.transition?{transition:{...shot.transition,duration:1}}:{})}))};
  await writeFile(join(dir,'source-revision.txt'),'fixture-revision\n');
  await writeFile(join(dir,'production.yaml'),JSON.stringify({model})+'\n');
  await writeFile(join(dir,'episode.yaml'),JSON.stringify(script)+'\n');
  execFileSync('git',['add','.'],{cwd:dir});
  execFileSync('git',['-c','user.name=Test','-c','user.email=test@example.invalid',
    'commit','-qm','valid CLI episode'],{cwd:dir});
  return {...fixture,episodePath:join(dir,'episode.yaml')};
}

test('render writes a review-samples-v1 plan on a cold capture and on a full shot-cache hit',async t=>{
  const {build,viewer,episode}=await renderFixture(t);
  await render(episode,{viewer,audio:null,label:'review'});
  const manifestPath=join(build,'review-manifest.json');
  const cold=JSON.parse(await readFile(manifestPath,'utf8'));
  assert.equal(cold.reviewSamples?.schema,'review-samples-v1',
    'the published manifest lacks a resolved review plan');
  assert.equal(cold.reviewSamples.frameCount,4);
  assert.ok(cold.reviewSamples.samples.some(s=>s.labels.some(l=>l.kind==='join')));
  await render(episode,{viewer,audio:null,label:'review'});
  const warm=JSON.parse(await readFile(manifestPath,'utf8'));
  assert.equal(warm.cache.reusedFrames,4);
  assert.equal(warm.reviewSamples?.schema,'review-samples-v1',
    'a full cache hit must still record the current resolved plan');
  assert.deepEqual(warm.reviewSamples,cold.reviewSamples);
});

test('a warm full shot-cache hit still records the resolved review plan',async t=>{
  const {build,viewer,episode}=await renderFixture(t);
  await render(episode,{viewer,audio:null,label:'review'});
  await render(episode,{viewer,audio:null,label:'review'});
  const warm=JSON.parse(await readFile(join(build,'review-manifest.json'),'utf8'));
  assert.equal(warm.cache.reusedFrames,4,'this is actually a full hit, not a new capture');
  assert.equal(warm.framesChecked,0);
  assert.equal(warm.reviewSamples?.schema,'review-samples-v1',
    'cache reuse must not skip plan derivation from the global requests');
  assert.ok(warm.reviewSamples.samples.some(s=>s.labels.some(l=>l.kind==='join')));
});

test('automatic pack failure warns after a good film and standalone retry succeeds',async t=>{
  const {build,viewer,episode}=await renderFixture(t),packs=join(build,'review-packs');
  await mkdir(packs);await chmod(packs,0o500);
  const messages=[],warn=console.warn,error=console.error;
  console.warn=(...args)=>messages.push(args.join(' '));
  console.error=(...args)=>messages.push(args.join(' '));
  try{
    const output=await render(episode,{viewer,audio:null,label:'review'});
    const manifestPath=join(build,'review-manifest.json');
    const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
    assert.equal(await fileHash(output),manifest.outputSha256,'film publication succeeded independently');
    assert.match(messages.join('\n'),/review pack failed; film published/i);
    assert.match(messages.join('\n'),/review .*review-manifest\.json/i,'warning supplies standalone retry');
    assert.deepEqual(await completeIndexes(build),[]);
    await chmod(packs,0o700);
    const retried=runCli(manifestPath);
    assert.equal(retried.status,0,`standalone review retry: ${retried.stderr}`);
    assert.equal((await completeIndexes(build)).length,1);
  }finally{console.warn=warn;console.error=error;await chmod(packs,0o700);}
});

test('render CLI exits zero with a published film even when its automatic pack fails',async t=>{
  const {build,viewer,episodePath}=await cliRenderFixture(t),packs=join(build,'review-packs');
  await mkdir(packs);await chmod(packs,0o500);
  try{
    const result=spawnSync(process.execPath,[cli,'render',episodePath,'--viewer',viewer,'--silent'],
      {encoding:'utf8',timeout:60000});
    assert.equal(result.status,0,`a pack failure must not fail film production: ${result.stderr}`);
    const manifestPath=join(build,'silent-preview-manifest.json');
    const manifest=JSON.parse(await readFile(manifestPath,'utf8'));
    assert.equal(await fileHash(manifest.output),manifest.outputSha256);
    assert.match(result.stdout,/Video: .*silent-preview\.mp4/);
    assert.match(result.stderr,/review pack failed; film published/i);
    assert.match(result.stderr,/review .*silent-preview-manifest\.json/i);
    assert.deepEqual(await completeIndexes(build),[]);
    await chmod(packs,0o700);
    const retry=runCli(manifestPath);
    assert.equal(retry.status,0,`standalone retry must succeed: ${retry.stderr}`);
    assert.equal((await completeIndexes(build)).length,1);
  }finally{await chmod(packs,0o700);}
});
