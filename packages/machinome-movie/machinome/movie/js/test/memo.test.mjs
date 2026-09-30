// Layer 9: the test memo is honest (AGENTS.md, "Memoization of slow tests").
// Fast tests over a tiny memoized step in a temporary directory, with an
// explicit toolchain record: no Chromium, no FFmpeg, no real render.
import {test,describe} from 'vitest';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,readdir,rm,utimes,unlink,appendFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {openMemo,fingerprint,MEMO_LABEL} from './support/memo.mjs';

const TOOLCHAIN={node:'v0-test',chromium:'0.0-test',ffmpeg:'ffmpeg version test',git:'git version test',fonts:[]};

// A project tree the step reads, a memo directory, and a memo with a log.
async function bench(t,{cold=false,toolchain=TOOLCHAIN}={}){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-memo-test-'));
  t.onTestFinished(()=>rm(dir,{recursive:true,force:true}));
  const tree=join(dir,'tree'),memoDir=join(dir,'memo');
  await mkdir(join(tree,'src'),{recursive:true});
  await writeFile(join(tree,'src','step.mjs'),'export const value=1;\n');
  await writeFile(join(tree,'fixture.json'),'{"frames":4}\n');
  const logs=[];
  const open=(options={})=>openMemo({dir:memoDir,toolchain,cold,log:m=>logs.push(m),...options});
  return {dir,tree,memoDir,logs,open,memo:open()};
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
