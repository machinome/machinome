// Layer 9: the test memo is honest (AGENTS.md, "Memoization of slow tests").
// Fast tests over a tiny memoized step in a temporary directory, with an
// explicit toolchain record: no Chromium, no FFmpeg, no real render.
import {test,describe} from 'vitest';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,readdir,rm,utimes,unlink,appendFile,realpath} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';
import * as memoModule from './support/memo.mjs';
import {openMemo,fingerprint,MEMO_LABEL} from './support/memo.mjs';

const TOOLCHAIN={node:'v0-test',chromium:'0.0-test',ffmpeg:'ffmpeg version test',git:'git version test',fonts:[]};

// A project tree the step reads, a memo directory, and a memo with a log.
async function bench(t,{cold=false,toolchain=TOOLCHAIN}={}){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-memo-test-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  const tree=join(dir,'tree'),memoDir=join(dir,'memo'),coldDir=join(dir,'cold');
  await mkdir(join(tree,'src'),{recursive:true});await mkdir(coldDir);
  await writeFile(join(tree,'src','step.mjs'),'export const value=1;\n');
  await writeFile(join(tree,'fixture.json'),'{"frames":4}\n');
  const logs=[];
  const open=(options={})=>openMemo({dir:memoDir,toolchain,cold,coldDir,log:m=>logs.push(m),...options});
  return {dir,tree,memoDir,coldDir,logs,open,memo:open()};
}
// A step whose runs are counted; it passes unless told to fail.
function step(){
  const s={runs:0,fail:false,body:async()=>{s.runs++;if(s.fail)throw new Error('the step failed');}};
  return s;
}
const task=()=>({meta:{}});
async function listing(dir){
  const out={};
  async function walk(d,prefix){
    let names;try{names=await readdir(d,{withFileTypes:true});}catch(error){if(error.code==='ENOENT')return;throw error;}
    for(const entry of names){
      const path=join(d,entry.name),rel=prefix+entry.name;
      if(entry.isDirectory())await walk(path,rel+'/');else out[rel]=(await readFile(path)).toString('base64');
    }
  }
  await walk(dir,'');return out;
}
const verdicts=async memoDir=>(await readdir(join(memoDir,'verdicts')).catch(()=>[])).filter(n=>n.endsWith('.json'));

describe('the verdict memo',()=>{
  test('a pass is recorded once, then passed from the memo without running, with the same verdict twice',async t=>{
    const {tree,memo,logs,memoDir}=await bench(t),s=step(),id={test:'test/tiny.test.mjs > step',inputs:[tree]};
    assert.equal(await memo.verdict(id,s.body,task()),'ran');
    assert.equal(s.runs,1);
    assert.equal((await verdicts(memoDir)).length,1,'the pass is recorded');
    for(let i=0;i<2;i++){
      const seen=task();
      assert.equal(await memo.verdict(id,s.body,seen),'memo');
      assert.equal(seen.meta.memo,MEMO_LABEL);
    }
    assert.equal(MEMO_LABEL,'passed from the memo');
    assert.equal(s.runs,1,'a memoized pass does not run the step');
    assert.deepEqual(logs.filter(m=>m.includes(MEMO_LABEL)),
      ['passed from the memo: test/tiny.test.mjs > step','passed from the memo: test/tiny.test.mjs > step']);
    const fresh=task();s.runs=0;
    await openMemo({dir:join(memoDir,'..','other-memo'),toolchain:TOOLCHAIN,log:()=>{}}).verdict(id,s.body,fresh);
    assert.equal(fresh.meta.memo,undefined,'a fresh run is never labelled as a memoized one');
  });

  test('a changed input, a new or removed file, another toolchain or another test misses',async t=>{
    const {tree,memo,open}=await bench(t),s=step(),id={test:'tiny > step',inputs:[tree]};
    await memo.verdict(id,s.body,task());
    const miss=async(label,edit,memoUsed=memo,idUsed=id)=>{
      await edit();const before=s.runs;
      assert.equal(await memoUsed.verdict(idUsed,s.body,task()),'ran',label);
      assert.equal(s.runs,before+1,label);
      assert.equal(await memoUsed.verdict(idUsed,s.body,task()),'memo',`${label}: recorded again`);
    };
    await miss('changed bytes',()=>writeFile(join(tree,'src','step.mjs'),'export const value=2;\n'));
    await miss('a new file',()=>writeFile(join(tree,'src','more.mjs'),'\n'));
    await miss('a removed file',()=>unlink(join(tree,'src','step.mjs')));
    await miss('a renamed file with the same bytes',async()=>{
      await writeFile(join(tree,'renamed.json'),await readFile(join(tree,'fixture.json')));await unlink(join(tree,'fixture.json'));});
    await miss('another toolchain',async()=>{},open({toolchain:{...TOOLCHAIN,chromium:'0.1-test'}}));
    await miss('another test name',async()=>{},memo,{...id,test:'tiny > other step'});
  });

  test('a modification time is not an input',async t=>{
    const {tree,memo}=await bench(t),s=step(),id={test:'tiny > step',inputs:[tree]};
    await memo.verdict(id,s.body,task());
    const later=new Date(Date.UTC(2031,0,1));
    await utimes(join(tree,'src','step.mjs'),later,later);await utimes(join(tree,'fixture.json'),later,later);
    assert.equal(await memo.verdict(id,s.body,task()),'memo');
    assert.equal(s.runs,1);
  });

  test('a failure is never recorded, and fails again on the next run',async t=>{
    const {tree,memo,memoDir}=await bench(t),s=step(),id={test:'tiny > step',inputs:[tree]};
    s.fail=true;
    await assert.rejects(memo.verdict(id,s.body,task()),/the step failed/);
    await assert.rejects(memo.verdict(id,s.body,task()),/the step failed/);
    assert.equal(s.runs,2);
    assert.deepEqual(await verdicts(memoDir),[]);
  });

  test('an input changed while the step runs records nothing',async t=>{
    const {tree,memo,memoDir}=await bench(t),id={test:'tiny > step',inputs:[tree]};
    assert.equal(await memo.verdict(id,()=>writeFile(join(tree,'fixture.json'),'{"frames":5}\n'),task()),'ran');
    assert.deepEqual(await verdicts(memoDir),[]);
  });

  test('a corrupted, truncated or forged entry is regenerated',async t=>{
    const {tree,memo,memoDir}=await bench(t),s=step(),id={test:'tiny > step',inputs:[tree]};
    await memo.verdict(id,s.body,task());
    const [name]=await verdicts(memoDir),file=join(memoDir,'verdicts',name),good=await readFile(file,'utf8');
    const forge=edit=>{const entry=JSON.parse(good);edit(entry);return JSON.stringify(entry);};
    const damages={
      garbage:'not json',
      truncated:good.slice(0,good.length>>1),
      empty:'',
      failed:forge(e=>{e.verdict='fail';}),
      'another test':forge(e=>{e.test='tiny > other';}),
      'another key':forge(e=>{e.key='0'.repeat(64);}),
      'a stale check':forge(e=>{e.check='0'.repeat(64);}),
    };
    for(const [label,bytes] of Object.entries(damages)){
      await writeFile(file,bytes);const before=s.runs;
      assert.equal(await memo.verdict(id,s.body,task()),'ran',label);
      assert.equal(s.runs,before+1,label);
      assert.equal(await readFile(file,'utf8'),good,`${label}: the entry is written whole again`);
      assert.equal(await memo.verdict(id,s.body,task()),'memo',label);
    }
  });

  test('the cold switch runs the step and leaves the memo untouched',async t=>{
    const {tree,memo,memoDir,open}=await bench(t),s=step(),id={test:'tiny > step',inputs:[tree]};
    await memo.verdict(id,s.body,task());
    await memo.artefact('film',{params:{frames:4}},async dir=>writeFile(join(dir,'film.bin'),'frames'));
    const before=await listing(memoDir),cold=open({cold:true}),seen=task();
    assert.equal(await cold.verdict(id,s.body,seen),'cold');
    assert.equal(s.runs,2,'a cold run runs a test that has a memoized pass');
    assert.equal(seen.meta.memo,undefined);
    s.fail=true;await assert.rejects(cold.verdict(id,s.body,task()),/the step failed/);
    let produced=0;
    const dir=await cold.artefact('film',{params:{frames:4}},async d=>{produced++;await writeFile(join(d,'film.bin'),'frames');});
    assert.equal(produced,1,'a cold run produces a memoized artefact');
    assert.ok(!dir.startsWith(memoDir),'a cold artefact is made outside the memo');
    assert.equal(await readFile(join(dir,'film.bin'),'utf8'),'frames');
    await cold.artefact('new',{params:{}},async d=>writeFile(join(d,'x'),'x'));
    assert.deepEqual(await listing(memoDir),before,'nothing in the memo was read into or written');
  });
});

describe('the artefact memo',()=>{
  const produceFilm=counter=>async dir=>{
    counter.n++;
    await mkdir(join(dir,'frames'));
    await writeFile(join(dir,'film.bin'),`film ${counter.n}`);
    await writeFile(join(dir,'frames','000000.png'),`frame ${counter.n}`);
  };

  test('a product is made once and reused byte-identical, verified on reuse',async t=>{
    const {memo}=await bench(t),counter={n:0},make=produceFilm(counter);
    const first=await memo.artefact('film',{params:{frames:4}},make);
    const second=await memo.artefact('film',{params:{frames:4}},make);
    assert.equal(counter.n,1);
    assert.equal(second,first);
    assert.equal(await readFile(join(second,'film.bin'),'utf8'),'film 1');
    const index=JSON.parse(await readFile(join(first,'index.json'),'utf8'));
    assert.deepEqual(index.files.map(f=>f.path),['film.bin','frames/000000.png']);
  });

  test('another parameter, another input file or another producer is another product',async t=>{
    const {tree,memo}=await bench(t),counter={n:0},make=produceFilm(counter);
    await memo.artefact('film',{params:{frames:4},files:[tree]},make);
    await memo.artefact('film',{params:{frames:5},files:[tree]},make);
    assert.equal(counter.n,2);
    await writeFile(join(tree,'fixture.json'),'{"frames":6}\n');
    await memo.artefact('film',{params:{frames:5},files:[tree]},make);
    assert.equal(counter.n,3);
    await memo.artefact('film',{params:{frames:5},files:[tree]},async dir=>{counter.n++;await writeFile(join(dir,'film.bin'),'other');});
    assert.equal(counter.n,4,'the producer source is part of the key');
  });

  test('a damaged, partial or extended entry is regenerated whole',async t=>{
    const {memo}=await bench(t),counter={n:0},make=produceFilm(counter);
    const dir=await memo.artefact('film',{params:{frames:4}},make);
    const damages={
      'changed bytes':()=>appendFile(join(dir,'film.bin'),'x'),
      'a removed part':()=>unlink(join(dir,'frames','000000.png')),
      'no index (partial)':()=>unlink(join(dir,'index.json')),
      'a corrupt index':()=>writeFile(join(dir,'index.json'),'{'),
      'an extra part':()=>writeFile(join(dir,'stray.bin'),'stray'),
    };
    for(const [label,damage] of Object.entries(damages)){
      await damage();const before=counter.n;
      const again=await memo.artefact('film',{params:{frames:4}},make);
      assert.equal(counter.n,before+1,label);
      assert.equal(await readFile(join(again,'film.bin'),'utf8'),`film ${counter.n}`,`${label}: the whole product is new`);
      assert.equal(await readFile(join(again,'frames','000000.png'),'utf8'),`frame ${counter.n}`,label);
      assert.deepEqual(Object.keys(await listing(again)).sort(),['film.bin','frames/000000.png','index.json'],label);
    }
  });

  test('a producer that fails leaves no entry behind',async t=>{
    const {memo,memoDir}=await bench(t);
    await assert.rejects(memo.artefact('film',{params:{}},async dir=>{await writeFile(join(dir,'half.bin'),'half');throw new Error('encode failed');}),/encode failed/);
    assert.deepEqual(Object.keys(await listing(join(memoDir,'artefacts'))),[]);
    let produced=0;
    await memo.artefact('film',{params:{}},async dir=>{produced++;await writeFile(join(dir,'whole.bin'),'whole');});
    assert.equal(produced,1);
  });
});

test('a fingerprint is the content and names of files, never their times',async t=>{
  const {tree}=await bench(t);
  const a=await fingerprint([tree]);
  assert.match(a,/^[0-9a-f]{64}$/);
  assert.equal(await fingerprint([tree]),a,'twice the same');
  const later=new Date(Date.UTC(2031,0,1));await utimes(join(tree,'fixture.json'),later,later);
  assert.equal(await fingerprint([tree]),a);
  await writeFile(join(tree,'fixture.json'),'{"frames":5}\n');
  assert.notEqual(await fingerprint([tree]),a);
  await assert.rejects(fingerprint([join(tree,'absent')]),/Memo input .*absent.* does not exist/);
});

// Two roots of one repository (the primary checkout and a linked worktree),
// with equal content, and a plain directory outside any Git work tree.
async function worktrees(t){
  const dir=await realpath(await mkdtemp(join(tmpdir(),'videomaker-memo-share-')));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  const primary=join(dir,'primary'),linked=join(dir,'linked'),plain=join(dir,'plain');
  const env={...process.env,GIT_AUTHOR_NAME:'Test',GIT_AUTHOR_EMAIL:'test@example.invalid',
    GIT_COMMITTER_NAME:'Test',GIT_COMMITTER_EMAIL:'test@example.invalid'};
  const git=(cwd,...args)=>execFileSync('git',args,{cwd,env,stdio:['ignore','pipe','pipe']});
  await mkdir(join(primary,'src'),{recursive:true});await mkdir(plain);
  await writeFile(join(primary,'src','step.mjs'),'export const value=1;\n');
  git(primary,'init','-q');git(primary,'add','.');git(primary,'commit','-qm','content');
  git(primary,'worktree','add','-q','--detach',linked);
  return {dir,primary,linked,plain,common:join(primary,'.git')};
}

describe('one memo for every worktree of the repository',()=>{
  test('two worktrees find one store beside the common Git directory; a plain directory keeps its own',async t=>{
    const {primary,linked,plain,common}=await worktrees(t);
    assert.equal(memoModule.memoDirectory(primary),join(common,'videomaker-test-memo'));
    assert.equal(memoModule.memoDirectory(linked),join(common,'videomaker-test-memo'));
    assert.equal(memoModule.memoDirectory(plain),join(plain,'.test-memo'));
  });

  test('equal content in two roots is passed from one store; a different content misses',async t=>{
    const {primary,linked,dir}=await worktrees(t),store=join(dir,'store'),s=step();
    const at=root=>({memo:openMemo({dir:store,root,toolchain:TOOLCHAIN,log:()=>{}}),id:{test:'test/step.test.mjs > step',inputs:[join(root,'src')]}});
    const a=at(primary),b=at(linked);
    assert.equal(await a.memo.verdict(a.id,s.body,task()),'ran');
    assert.equal(await b.memo.verdict(b.id,s.body,task()),'memo','the other worktree reuses the pass');
    assert.equal(s.runs,1);
    await writeFile(join(linked,'src','step.mjs'),'export const value=2;\n');
    assert.equal(await b.memo.verdict(b.id,s.body,task()),'ran','a different content misses');
    assert.equal(await a.memo.verdict(a.id,s.body,task()),'memo','the first content keeps its pass');
    assert.equal(s.runs,2);
    let produced=0;
    const make=async out=>{produced++;await writeFile(join(out,'film.bin'),'film');};
    const first=await a.memo.artefact('film',{files:[join(primary,'src')]},make);
    await writeFile(join(linked,'src','step.mjs'),'export const value=1;\n');
    const second=await b.memo.artefact('film',{files:[join(linked,'src')]},make);
    assert.equal(produced,1,'the other worktree reuses the product');
    assert.equal(second,first);
  });

  test('two writers producing one product at once both use one verified entry',async t=>{
    const {memoDir,open}=await bench(t);
    let arrived=0,release;const both=new Promise(r=>{release=r;});
    const make=async out=>{
      await writeFile(join(out,'film.bin'),'film');await mkdir(join(out,'frames'));await writeFile(join(out,'frames','0.png'),'frame');
      if(++arrived===2)release();await both;
    };
    const [one,two]=await Promise.all([open().artefact('film',{params:{frames:4}},make),open().artefact('film',{params:{frames:4}},make)]);
    assert.equal(arrived,2,'both produced before either published');
    assert.equal(one,two);
    assert.equal(await readFile(join(one,'film.bin'),'utf8'),'film');
    assert.equal(await open().artefact('film',{params:{frames:4}},make),one);
    assert.equal(arrived,2,'the published entry verifies and is reused');
    assert.deepEqual((await readdir(join(memoDir,'artefacts'))).filter(n=>n.startsWith('.')),[],'no staging directory is left');
    const writes=[1,2].map(()=>open().verdict({test:'tiny > step',inputs:[]},async()=>{},task()));
    assert.deepEqual(await Promise.all(writes),['ran','ran']);
    assert.deepEqual((await readdir(join(memoDir,'verdicts'))).filter(n=>!n.endsWith('.json')),[],'no pending write is left');
  });
});

// The verdict key covers what a slow test can reach (test/support/reach.mjs).
const reachModule=()=>import('./support/reach.mjs');
// A tiny repository: two slow tests, the modules they import, a directory a
// reached module serves without importing it, a command one test spawns, and
// files nothing reaches.
async function reachable(t){
  const root=await mkdtemp(join(tmpdir(),'videomaker-memo-reach-'));
  t.onTestFinished(()=>rm(root,{recursive:true,force:true}));
  const files={
    'package.json':'{}\n',
    'test/support/helper.mjs':'export const helper=1;\n',
    'test/browser/view.test.mjs':"import {a} from '../../src/a.mjs';\nimport {page} from '../../src/page.mjs';\n",
    'test/pipeline/cli.test.mjs':"import {a} from '../../src/a.mjs';\n",
    'src/a.mjs':"import {b} from './b.mjs';\nexport const a=b;\nexport const later=()=>import('./lazy.mjs');\n",
    'src/b.mjs':'export const b=1;\n',
    'src/lazy.mjs':'export const lazy=1;\n',
    'src/page.mjs':"export const page=new URL('../served/page.css',import.meta.url);\n",
    'src/unreached.mjs':'export const unreached=1;\n',
    'served/page.css':'body{}\n',
    'served/page.test.tsx':'// a test beside the served sources: nothing serves it\n',
    'bin/cli.mjs':"import {d} from '../src/d.mjs';\n",
    'src/d.mjs':'export const d=1;\n',
  };
  for(const [name,content] of Object.entries(files)){await mkdir(join(root,name,'..'),{recursive:true});await writeFile(join(root,name),content);}
  const reads={'src/page.mjs':['served'],'test/pipeline/cli.test.mjs':['bin/cli.mjs']};
  const always=['test/support','package.json'];
  const {slowTestInputs}=await reachModule();
  const memoDir=join(root,'.memo-store'),s=step();
  const memo=openMemo({dir:memoDir,root,toolchain:TOOLCHAIN,log:()=>{}});
  // Runs a slow test through the memo and says whether it ran.
  const run=async file=>memo.verdict({test:file,inputs:await slowTestInputs(join(root,file),{root,reads,always})},s.body,task());
  return {root,reads,always,run,edit:(name,content='// edited\n')=>appendFile(join(root,name),content)};
}
const VIEW='test/browser/view.test.mjs',CLI='test/pipeline/cli.test.mjs';

describe('the verdict key covers what a slow test can reach',()=>{
  test('a file reached only through an import misses when changed; an unreached file hits',async t=>{
    const {run,edit}=await reachable(t);
    assert.equal(await run(VIEW),'ran');assert.equal(await run(CLI),'ran');
    for(const reached of ['src/b.mjs','src/lazy.mjs']){
      await edit(reached);
      assert.equal(await run(VIEW),'ran',`${reached} is reached by an import`);
      assert.equal(await run(CLI),'ran',`${reached} is reached by an import`);
    }
    await edit('src/unreached.mjs');
    assert.equal(await run(VIEW),'memo','an unreached file is not an input');
    assert.equal(await run(CLI),'memo','an unreached file is not an input');
    await edit('test/support/helper.mjs');
    assert.equal(await run(VIEW),'ran','the support modules are always inputs');
  });

  test('what a reached module serves is keyed; a spawned command is followed through its imports',async t=>{
    const {run,edit}=await reachable(t);
    await run(VIEW);await run(CLI);
    await edit('served/page.css','p{}\n');
    assert.equal(await run(VIEW),'ran','the served directory of a reached module is an input');
    assert.equal(await run(CLI),'memo','a test that does not reach the page keeps its pass');
    await edit('served/page.test.tsx');
    assert.equal(await run(VIEW),'memo','a test file beside the served sources is not served');
    await edit('src/d.mjs');
    assert.equal(await run(CLI),'ran','a module the spawned command imports is an input');
    assert.equal(await run(VIEW),'memo');
  });

  test('a reached module that locates a file by path without declaring it is refused by name',async t=>{
    const {root,reads}=await reachable(t),{undeclared}=await reachModule();
    const entries=[VIEW,CLI].map(f=>join(root,f));
    assert.deepEqual(await undeclared(entries,{root,reads}),[]);
    const {'src/page.mjs':_,...without}=reads;
    assert.deepEqual(await undeclared(entries,{root,reads:without}),['src/page.mjs']);
    await writeFile(join(root,'src','b.mjs'),"import {resolve} from 'node:path';\nexport const b=resolve('bin/cli.mjs');\n");
    assert.deepEqual(await undeclared(entries,{root,reads}),['src/b.mjs']);
  });

  test('in this repository, every read of every slow test is declared and the stage is keyed for the browser tests',async()=>{
    const {slowTestInputs,undeclared}=await reachModule(),root=memoModule.REPOSITORY;
    const slow=[];
    for(const dir of ['test/browser','test/pipeline'])
      for(const name of (await readdir(join(root,dir))).sort())if(name.endsWith('.test.mjs'))slow.push(join(root,dir,name));
    assert.ok(slow.length>=10);
    assert.deepEqual(await undeclared(slow,{root}),[],'a module reads a repository file the key does not declare');
    for(const file of slow.filter(f=>f.includes('/test/browser/'))){
      const inputs=await slowTestInputs(file,{root});
      for(const served of ['stage/shipped.tsx','stage/runtime.tsx','src/film.html','test/viewer-double.mjs'])
        assert.ok(inputs.includes(join(root,served)),`${served} is an input of ${file}`);
    }
    const speech=await slowTestInputs(join(root,'test/pipeline/speech.test.mjs'),{root});
    assert.ok(speech.includes(join(root,'src/speech.mjs')));
    assert.ok(!speech.includes(join(root,'stage/shipped.tsx')),'the speech tests do not reach the stage');
  });
});

// Wart 10 of the React stage: cold artefacts leaked under the temporary
// directory, removed only on a process exit vitest's workers never reach.
describe('a cold run leaves nothing behind',()=>{
  test('a cold artefact is made inside the run\'s cold directory, and refused without one',async t=>{
    const {open,coldDir,memoDir}=await bench(t),made=[];
    const dir=await open({cold:true}).artefact('film',{params:{}},async out=>{made.push(out);await writeFile(join(out,'film.bin'),'film');});
    assert.ok(dir.startsWith(coldDir+'/'),`${dir} is inside ${coldDir}`);
    assert.equal(await readFile(join(dir,'film.bin'),'utf8'),'film');
    await assert.rejects(open({cold:true,coldDir:null}).artefact('film',{params:{}},async()=>{}),/cold directory/);
    assert.deepEqual(await listing(memoDir),{});
  });

  test('a run\'s cold directory is removed when the run closes it',async t=>{
    const {dir}=await bench(t);
    const run=await memoModule.openColdRun(dir);
    assert.match(run,new RegExp(`/videomaker-cold-run-${process.pid}-[^/]+$`));
    const product=await openMemo({dir:join(dir,'memo'),toolchain:TOOLCHAIN,cold:true,coldDir:run,log:()=>{}})
      .artefact('film',{params:{}},async out=>writeFile(join(out,'film.bin'),'film'));
    assert.ok(product.startsWith(run));
    await memoModule.closeColdRun(run);
    assert.deepEqual((await readdir(dir)).filter(n=>n.startsWith('videomaker-cold')),[]);
  });

  test('the next run removes what a killed run left, and leaves a live run\'s and the old code\'s alone',async t=>{
    const {dir,memoDir}=await bench(t);
    const dead=999999999,live=process.pid,tmp=join(dir,'tmp');
    const dirs=[`tmp/videomaker-cold-run-${dead}-a1`,`tmp/videomaker-cold-run-${live}-b2`,'tmp/videomaker-cold-film-c3',
      `memo/artefacts/.staging-${dead}-d4`,`memo/artefacts/.staging-${live}-e5`,`memo/artefacts/.trash-${dead}-f6`,'memo/artefacts/film-0123456789abcdef'];
    for(const d of dirs){await mkdir(join(dir,d),{recursive:true});await writeFile(join(dir,d,'part'),'x');}
    await mkdir(join(memoDir,'verdicts'),{recursive:true});
    for(const f of [`k.json.${dead}.u1.pending`,`k.json.${live}.u2.pending`,'k.json',`.trash-${dead}-u3`])await writeFile(join(memoDir,'verdicts',f),'x');
    const removed=await memoModule.sweep({dir:memoDir,tmp});
    assert.deepEqual(removed.map(p=>p.slice(dir.length+1)).sort(),[`memo/artefacts/.staging-${dead}-d4`,`memo/artefacts/.trash-${dead}-f6`,
      `memo/verdicts/.trash-${dead}-u3`,`memo/verdicts/k.json.${dead}.u1.pending`,`tmp/videomaker-cold-run-${dead}-a1`]);
    assert.deepEqual((await readdir(tmp)).sort(),['videomaker-cold-film-c3',`videomaker-cold-run-${live}-b2`]);
    assert.deepEqual((await readdir(join(memoDir,'artefacts'))).sort(),[`.staging-${live}-e5`,'film-0123456789abcdef']);
    assert.deepEqual((await readdir(join(memoDir,'verdicts'))).sort(),['k.json',`k.json.${live}.u2.pending`]);
    assert.deepEqual(await memoModule.sweep({dir:join(dir,'absent'),tmp:join(dir,'absent-tmp')}),[],'nothing to sweep is not an error');
  });
});
