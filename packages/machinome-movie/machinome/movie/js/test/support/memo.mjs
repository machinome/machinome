// The test memo (AGENTS.md, "Memoization of slow tests"; ADR-003).
//
// Two memos, both keyed on content and both kept in one store every worktree
// of the repository shares, never committed: `videomaker-test-memo/` beside
// the common Git directory (`memoDirectory`), or `.test-memo/` at the root
// outside a Git work tree. Fingerprints are relative to the checkout's root,
// so equal content in two worktrees gives equal keys.
//
// - The verdict memo keeps a slow test's pass. `slowTest(name, fn)` is a
//   vitest `test` whose key is the SHA-256 of the test's name and file, the
//   content fingerprint of everything the test can reach (test/support/reach.mjs:
//   its import graph, what the reached modules serve or read, the command line
//   when a test runs it, test/support/, the viewer double, the test's own
//   file, `package.json`, `package-lock.json`, `vitest.config.mjs`), the bytes
//   of a file the maintainer selects outside the repository for it (the
//   viewer bundle of the viewer layer, under its variable's name) and the
//   toolchain record: the versions of Node, Chromium, FFmpeg, ffprobe and Git
//   and the fonts the stage uses, obtained once per run by the global setup
//   (`test/support/toolchain.mjs`). A verified entry for the key is a hit: the
//   body does not run, the task's `meta.memo` is "passed from the memo" and
//   those words are logged with the test's name; the memo reporter lists them.
//   A miss runs the body; only a pass whose inputs were unchanged by the time
//   it finished is recorded. A failure is never recorded.
// - The artefact memo keeps an expensive product a slow test builds as its
//   input. `artefact(name, {params, files}, produce)` returns a directory; the
//   key covers the name, the parameters, the fingerprint of the input files,
//   the producer's own source and the toolchain. Callers copy from the
//   directory and never write into it. The test's assertions still run.
//
// Rules both obey:
// - The key is content, never an mtime: a fingerprint hashes every file's
//   relative path and bytes (a symbolic link as its target text); `stat` only
//   tells a directory from a file.
// - Reuse is verified. A verdict entry (`verdicts/<key>.json`, written to a
//   temporary name and renamed) holds its key, test, verdict and a check hash
//   of the rest; anything else is removed and treated as a miss. An artefact
//   entry (`artefacts/<name>-<key>/`) is produced in a staging directory whose
//   `index.json` (every file's path, size and SHA-256) is written after every
//   part and before the rename into place; on every reuse the directory must
//   hold exactly the indexed files with those hashes, or it is removed and
//   produced again whole.
// - Two suites (two worktrees) may write the store at once. Temporary names
//   carry the writer's PID; a writer that finds an entry published first by
//   another uses it when it verifies; a damaged entry is renamed aside before
//   it is removed. `sweep` removes what a process that is gone left.
// - The cold switch (`npm test -- --cold`, carried as VIDEOMAKER_TEST_COLD=1)
//   ignores the memo entirely: nothing is read from it or written to it, and
//   an artefact is produced inside the run's cold directory (`openColdRun`),
//   which the global teardown removes.
// - A step that reaches a network or reads a clock for its verdict is not
//   memoizable and is doubled instead. The slow tests' remaining reads outside
//   the key (the repository's Git HEAD recorded as provenance, a clock read
//   only to log elapsed time or to bound a wait, random names of temporary
//   directories, loopback sockets) decide no verdict; see ADR-003.
import {createHash,randomUUID} from 'node:crypto';
import {readFile,readdir,lstat,readlink,mkdir,writeFile,rename,rm,mkdtemp} from 'node:fs/promises';
import {execFileSync} from 'node:child_process';
import {tmpdir} from 'node:os';
import {join,relative,dirname,sep,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {test,inject} from 'vitest';
import {slowTestInputs,selectedInputs} from './reach.mjs';

export const MEMO_LABEL='passed from the memo';
export const REPOSITORY=join(dirname(fileURLToPath(import.meta.url)),'..','..');
const VERDICT_SCHEMA='verdict-memo-v2',ARTEFACT_SCHEMA='artefact-memo-v1',INDEX='index.json';
const STORE='videomaker-test-memo',FALLBACK='.test-memo';

// The one store every worktree of the repository shares: beside the common
// Git directory of `root` (the `.git` of the primary checkout, which every
// linked worktree names), or `.test-memo/` at `root` outside a Git work tree.
export function memoDirectory(root=REPOSITORY){
  let common;
  try{
    common=execFileSync('git',['rev-parse','--path-format=absolute','--git-common-dir'],
      {cwd:root,encoding:'utf8',stdio:['ignore','pipe','ignore']}).trim();
  }catch{return join(root,FALLBACK);}
  return join(resolve(root,common),STORE);
}

const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const sorted=value=>Array.isArray(value)?value.map(sorted)
  :value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,sorted(value[k])])):value;
const canonical=value=>JSON.stringify(sorted(value));
const posix=path=>path.split(sep).join('/');

// Every regular file under the paths, by path relative to `base`, with the
// SHA-256 of its bytes. A missing input is refused by name.
async function walk(path,base,out){
  let info;
  try{info=await lstat(path);}catch(error){
    if(error.code==='ENOENT')throw new Error(`Memo input ${path} does not exist`);throw error;
  }
  const name=posix(relative(base,path));
  if(info.isDirectory()){
    for(const entry of (await readdir(path)).sort())await walk(join(path,entry),base,out);
  }else if(info.isSymbolicLink())out.push(`link\0${name}\0${await readlink(path)}`);
  else if(info.isFile())out.push(`file\0${name}\0${sha256(await readFile(path))}`);
  else throw new Error(`Memo input ${path} is neither a file nor a directory`);
}
export async function fingerprint(paths,{base=REPOSITORY}={}){
  const out=[];
  for(const path of [...paths].sort())await walk(path,base,out);
  return sha256(out.join('\n'));
}
// The files a maintainer selects outside the repository ([variable, path]),
// by the variable's name and the file's bytes, never its path; '' for none.
async function selectedFingerprint(selected){
  if(!selected.length)return '';
  const out=[];
  for(const [name,path] of [...selected].sort(([a],[b])=>a<b?-1:a>b?1:0)){
    let bytes;
    try{bytes=await readFile(path);}catch(error){
      if(error.code==='ENOENT'||error.code==='EISDIR')throw new Error(`Memo input ${path} does not exist`);throw error;
    }
    out.push(`selected\0${name}\0${sha256(bytes)}`);
  }
  return ':'+sha256(out.join('\n'));
}

// The regular files of an artefact directory, relative, sorted; null when it
// holds anything else.
async function files(dir,prefix='',out=[]){
  for(const entry of (await readdir(dir,{withFileTypes:true})).sort((a,b)=>a.name<b.name?-1:1)){
    const rel=prefix+entry.name;
    if(entry.isDirectory()){if(!await files(join(dir,entry.name),rel+'/',out))return null;}
    else if(entry.isFile())out.push(rel);
    else return null;
  }
  return out;
}

// Written to a name of its own and renamed: a reader never sees a partial
// entry, and two writers of one key write equal bytes. The PID in the name
// lets a later run remove what a killed one left (sweep).
async function writeWhole(file,text){
  await mkdir(dirname(file),{recursive:true});
  const pending=`${file}.${process.pid}.${randomUUID()}.pending`;
  try{await writeFile(pending,text);await rename(pending,file);}
  catch(error){await rm(pending,{force:true});throw error;}
}
// A damaged entry is renamed aside before it is removed, so a writer never
// removes an entry another has just published under the same name.
async function discard(entry){
  const aside=join(dirname(entry),`.trash-${process.pid}-${randomUUID()}`);
  try{await rename(entry,aside);}catch(error){if(error.code==='ENOENT')return;throw error;}
  await rm(aside,{recursive:true,force:true});
}
const exists=path=>lstat(path).then(()=>true,()=>false);

// The cold run's own directory under the system's temporary directory: the
// slow project's global setup opens it, every cold product of the run is made
// inside it, and the global teardown closes it. The PID in its name lets the
// next run remove it when the run was killed (sweep).
const COLD_RUN='videomaker-cold-run-';
export function openColdRun(tmp=tmpdir()){return mkdtemp(join(tmp,`${COLD_RUN}${process.pid}-`));}
export function closeColdRun(dir){return rm(dir,{recursive:true,force:true});}

// What a killed run left: cold run directories under `tmp`, and staging
// directories, entries put aside and pending verdict writes in the store,
// each carrying the PID of the process that made it. Removes those whose
// process is gone and returns their paths; a live process's (a suite running
// in another worktree) are left alone, and so is anything without a PID
// (the old code's `videomaker-cold-<name>-*`, which may belong to a suite
// still running it).
const alive=pid=>{
  try{process.kill(pid,0);return true;}catch(error){return error.code==='EPERM';}
};
// With `dir` null (a cold run, which writes nothing to the store) only `tmp`
// is swept.
export async function sweep({dir=memoDirectory(),tmp=tmpdir()}={}){
  const places=[[tmp,new RegExp(`^${COLD_RUN}(\\d+)-`)],
    ...(dir?[[join(dir,'artefacts'),/^\.(?:staging|trash)-(\d+)-/],
      [join(dir,'verdicts'),/^(?:\.trash-(\d+)-|.*\.json\.(\d+)\.[^.]+\.pending$)/]]:[])];
  const removed=[];
  for(const [place,pattern] of places){
    let names;
    try{names=await readdir(place);}catch(error){if(error.code==='ENOENT')continue;throw error;}
    for(const name of names.sort()){
      const match=pattern.exec(name);
      if(!match)continue;
      const pid=Number(match[1]??match[2]);
      if(alive(pid))continue;
      await rm(join(place,name),{recursive:true,force:true});removed.push(join(place,name));
    }
  }
  return removed;
}

// A memo over `dir` with the run's toolchain record. `log` receives the
// "passed from the memo" lines.
// Fingerprints are relative to `root`, so two checkouts with equal content
// compute equal keys and share `dir`.
export function openMemo({dir=memoDirectory(),root=REPOSITORY,toolchain,cold=false,coldDir=null,log=console.log}){
  if(!toolchain||typeof toolchain!=='object')throw new Error('The test memo needs the toolchain record of test/support/toolchain.mjs');

  async function readVerdict(file,key,name){
    let entry;
    try{entry=JSON.parse(await readFile(file,'utf8'));}catch(error){
      if(error.code==='ENOENT')return false;
      await discard(file);return false;
    }
    const {check,...rest}=entry??{};
    const good=entry&&typeof entry==='object'&&rest.schema===VERDICT_SCHEMA&&rest.key===key&&rest.test===name
      &&rest.verdict==='pass'&&check===sha256(canonical(rest));
    if(!good)await discard(file);
    return good;
  }

  // Runs `body` unless a verified pass is memoized for `test` over `inputs`.
  // Returns 'memo', 'ran' or 'cold'; a failing body rejects and records nothing.
  // `selected`: [variable, path] of the files outside the repository the
  // maintainer selected for the test (reach.mjs, SELECTED), keyed by bytes.
  async function verdict({test:name,inputs,selected=[]},body,task){
    if(cold){await body();return 'cold';}
    const read=await fingerprint(inputs,{base:root})+await selectedFingerprint(selected);
    const key=sha256(canonical({schema:VERDICT_SCHEMA,test:name,inputs:read,toolchain}));
    const file=join(dir,'verdicts',`${key}.json`);
    if(await readVerdict(file,key,name)){
      task.meta.memo=MEMO_LABEL;log(`${MEMO_LABEL}: ${name}`);return 'memo';
    }
    await body();
    if(await fingerprint(inputs,{base:root})+await selectedFingerprint(selected)!==read){log(`not memoized, its inputs changed while it ran: ${name}`);return 'ran';}
    const entry={schema:VERDICT_SCHEMA,key,test:name,verdict:'pass'};
    await writeWhole(file,JSON.stringify({...entry,check:sha256(canonical(entry))},null,2)+'\n');
    return 'ran';
  }

  async function verified(entry,key){
    let index;
    try{index=JSON.parse(await readFile(join(entry,INDEX),'utf8'));}catch{return false;}
    if(index?.schema!==ARTEFACT_SCHEMA||index.key!==key||!Array.isArray(index.files))return false;
    const present=await files(entry).catch(()=>null);
    if(!present)return false;
    const listed=index.files.map(f=>f?.path);
    if(canonical(present.filter(p=>p!==INDEX))!==canonical([...listed].sort()))return false;
    for(const f of index.files){
      const bytes=await readFile(join(entry,f.path)).catch(()=>null);
      if(!bytes||bytes.length!==f.size||sha256(bytes)!==f.sha256)return false;
    }
    return true;
  }

  // The directory of the product `produce(dir)` writes, memoized by content.
  async function artefact(name,{params={},files:inputs=[]}={},produce){
    const safe=name.replace(/[^A-Za-z0-9._-]/g,'-');
    const key=sha256(canonical({schema:ARTEFACT_SCHEMA,name,params,
      files:inputs.length?await fingerprint(inputs,{base:root}):null,producer:produce.toString(),toolchain}));
    if(cold){
      if(!coldDir)throw new Error(`The cold artefact ${name} needs the run's cold directory (openColdRun), which the global setup provides`);
      const out=await mkdtemp(join(coldDir,`${safe}-`));
      await produce(out);return out;
    }
    const store=join(dir,'artefacts'),entry=join(store,`${safe}-${key.slice(0,16)}`);
    if(await verified(entry,key))return entry;
    if(await exists(entry))await discard(entry);
    await mkdir(store,{recursive:true});
    const staging=await mkdtemp(join(store,`.staging-${process.pid}-`));
    try{
      await produce(staging);
      const made=await files(staging);
      if(!made)throw new Error(`Artefact ${name} holds something other than files and directories`);
      if(made.includes(INDEX))throw new Error(`Artefact ${name} wrote ${INDEX}, which the memo reserves for its index`);
      const listed=[];
      for(const path of made){const bytes=await readFile(join(staging,path));listed.push({path,size:bytes.length,sha256:sha256(bytes)});}
      await writeFile(join(staging,INDEX),JSON.stringify({schema:ARTEFACT_SCHEMA,key,name,files:listed},null,2)+'\n');
      // Another writer (a suite in another worktree) may publish the same
      // entry first: its verified entry is used and this one dropped; a
      // damaged one is put aside and this one published in its place, once.
      for(let attempt=0;;attempt++){
        try{await rename(staging,entry);break;}catch(error){
          if(error.code!=='ENOTEMPTY'&&error.code!=='EEXIST')throw error;
          if(await verified(entry,key)){await rm(staging,{recursive:true,force:true});break;}
          if(attempt)throw new Error(`Artefact ${name} could not be published: another writer keeps a damaged entry at ${entry}`);
          await discard(entry);
        }
      }
    }catch(error){await rm(staging,{recursive:true,force:true});throw error;}
    return entry;
  }

  return {verdict,artefact};
}

// The run's memo, from the toolchain record the global setup provides.
let run=null;
function runMemo(){
  return run??=openMemo({dir:inject('memoDir')??memoDirectory(),toolchain:inject('toolchain'),
    cold:inject('cold')??process.env.VIDEOMAKER_TEST_COLD==='1',coldDir:inject('coldDir')});
}

// Everything a slow test can reach, for its verdict key (test/support/reach.mjs).
export {slowTestInputs} from './reach.mjs';
function fullName(task){
  const names=[];
  for(let t=task;t&&!t.filepath;t=t.suite)names.unshift(t.name);
  return names.join(' > ');
}

// A vitest test whose pass is memoized (the verdict memo).
export function slowTest(name,fn,options){return memoizedTest(name,fn,options);}
// A memoized test behind a gate: `gate(context)` runs before the memo is
// consulted, may skip the test (context.skip) or fail it, and what it returns
// is passed to `fn` after the context. A skip is never recorded.
export function gatedSlowTest(gate){return (name,fn,options)=>memoizedTest(name,fn,options,gate);}
function memoizedTest(name,fn,options,gate=null){
  return test(name,async context=>{
    const passed=gate?await gate(context):undefined;
    const file=context.task.file.filepath;
    await runMemo().verdict({test:`${posix(relative(REPOSITORY,file))} > ${fullName(context.task)}`,
      inputs:await slowTestInputs(file),selected:selectedInputs(file)},()=>fn(context,passed),context.task);
  },options);
}

// An expensive input product, memoized (the artefact memo).
export function artefact(name,spec,produce){return runMemo().artefact(name,spec,produce);}
