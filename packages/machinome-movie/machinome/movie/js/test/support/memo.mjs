// The test memo (AGENTS.md, "Memoization of slow tests"; ADR-003).
//
// Two memos, both keyed on content and both kept in the ignored `.test-memo/`
// at the repository root, never committed:
//
// - The verdict memo keeps a slow test's pass. `slowTest(name, fn)` is a
//   vitest `test` whose key is the SHA-256 of the test's name and file, the
//   content fingerprint of everything a slow test can read (`src/`, `bin/`,
//   `fixtures/`, `schema/`, every non-test module under `test/` — the helpers,
//   the viewer double, these support modules —, the test's own file,
//   `package.json`, `package-lock.json`, `vitest.config.mjs`) and the
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
// - The cold switch (`npm test -- --cold`, carried as VIDEOMAKER_TEST_COLD=1)
//   ignores the memo entirely: nothing is read from it or written to it, and
//   an artefact is produced in a temporary directory outside it.
// - A step that reaches a network or reads a clock for its verdict is not
//   memoizable and is doubled instead. The slow tests' remaining reads outside
//   the key (the repository's Git HEAD recorded as provenance, a clock read
//   only to log elapsed time or to bound a wait, random names of temporary
//   directories, loopback sockets) decide no verdict; see ADR-003.
import {createHash,randomUUID} from 'node:crypto';
import {readFile,readdir,lstat,readlink,mkdir,writeFile,rename,rm,mkdtemp} from 'node:fs/promises';
import {rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,relative,dirname,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {test,inject} from 'vitest';

export const MEMO_LABEL='passed from the memo';
export const REPOSITORY=join(dirname(fileURLToPath(import.meta.url)),'..','..');
export const MEMO_DIR=join(REPOSITORY,'.test-memo');
const VERDICT_SCHEMA='verdict-memo-v1',ARTEFACT_SCHEMA='artefact-memo-v1',INDEX='index.json';

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

async function writeWhole(file,text){
  await mkdir(dirname(file),{recursive:true});
  const pending=`${file}.${randomUUID()}.pending`;
  await writeFile(pending,text);await rename(pending,file);
}

const coldDirs=new Set();
let coldCleanup=false;

// A memo over `dir` with the run's toolchain record. `log` receives the
// "passed from the memo" lines.
export function openMemo({dir=MEMO_DIR,toolchain,cold=false,log=console.log}){
  if(!toolchain||typeof toolchain!=='object')throw new Error('The test memo needs the toolchain record of test/support/toolchain.mjs');

  async function readVerdict(file,key,name){
    let entry;
    try{entry=JSON.parse(await readFile(file,'utf8'));}catch(error){
      if(error.code==='ENOENT')return false;
      await rm(file,{force:true});return false;
    }
    const {check,...rest}=entry??{};
    const good=entry&&typeof entry==='object'&&rest.schema===VERDICT_SCHEMA&&rest.key===key&&rest.test===name
      &&rest.verdict==='pass'&&check===sha256(canonical(rest));
    if(!good)await rm(file,{force:true});
    return good;
  }

  // Runs `body` unless a verified pass is memoized for `test` over `inputs`.
  // Returns 'memo', 'ran' or 'cold'; a failing body rejects and records nothing.
  async function verdict({test:name,inputs},body,task){
    if(cold){await body();return 'cold';}
    const read=await fingerprint(inputs);
    const key=sha256(canonical({schema:VERDICT_SCHEMA,test:name,inputs:read,toolchain}));
    const file=join(dir,'verdicts',`${key}.json`);
    if(await readVerdict(file,key,name)){
      task.meta.memo=MEMO_LABEL;log(`${MEMO_LABEL}: ${name}`);return 'memo';
    }
    await body();
    if(await fingerprint(inputs)!==read){log(`not memoized, its inputs changed while it ran: ${name}`);return 'ran';}
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
      files:inputs.length?await fingerprint(inputs):null,producer:produce.toString(),toolchain}));
    if(cold){
      const out=await mkdtemp(join(tmpdir(),`videomaker-cold-${safe}-`));
      coldDirs.add(out);
      if(!coldCleanup){coldCleanup=true;process.on('exit',()=>{for(const d of coldDirs)rmSync(d,{recursive:true,force:true});});}
      await produce(out);return out;
    }
    const root=join(dir,'artefacts'),entry=join(root,`${safe}-${key.slice(0,16)}`);
    if(await verified(entry,key))return entry;
    await rm(entry,{recursive:true,force:true});
    await mkdir(root,{recursive:true});
    const staging=await mkdtemp(join(root,'.staging-'));
    try{
      await produce(staging);
      const made=await files(staging);
      if(!made)throw new Error(`Artefact ${name} holds something other than files and directories`);
      if(made.includes(INDEX))throw new Error(`Artefact ${name} wrote ${INDEX}, which the memo reserves for its index`);
      const listed=[];
      for(const path of made){const bytes=await readFile(join(staging,path));listed.push({path,size:bytes.length,sha256:sha256(bytes)});}
      await writeFile(join(staging,INDEX),JSON.stringify({schema:ARTEFACT_SCHEMA,key,name,files:listed},null,2)+'\n');
      await rename(staging,entry);
    }catch(error){await rm(staging,{recursive:true,force:true});throw error;}
    return entry;
  }

  return {verdict,artefact};
}

// The run's memo, from the toolchain record the global setup provides.
let run=null;
function runMemo(){
  return run??=openMemo({toolchain:inject('toolchain'),
    cold:inject('cold')??process.env.VIDEOMAKER_TEST_COLD==='1'});
}

// Everything a slow test can read, for its verdict key.
async function helpers(dir,out=[]){
  for(const entry of (await readdir(dir,{withFileTypes:true})).sort((a,b)=>a.name<b.name?-1:1)){
    const path=join(dir,entry.name);
    if(entry.isDirectory())await helpers(path,out);
    else if(!entry.name.endsWith('.test.mjs'))out.push(path);
  }
  return out;
}
export async function slowTestInputs(file){
  return [...['src','bin','fixtures','schema','package.json','package-lock.json','vitest.config.mjs']
    .map(p=>join(REPOSITORY,p)),...await helpers(join(REPOSITORY,'test')),file];
}
function fullName(task){
  const names=[];
  for(let t=task;t&&!t.filepath;t=t.suite)names.unshift(t.name);
  return names.join(' > ');
}

// A vitest test whose pass is memoized (the verdict memo).
export function slowTest(name,fn,options){
  return test(name,async context=>{
    const file=context.task.file.filepath;
    await runMemo().verdict({test:`${posix(relative(REPOSITORY,file))} > ${fullName(context.task)}`,
      inputs:await slowTestInputs(file)},()=>fn(context),context.task);
  },options);
}

// An expensive input product, memoized (the artefact memo).
export function artefact(name,spec,produce){return runMemo().artefact(name,spec,produce);}
