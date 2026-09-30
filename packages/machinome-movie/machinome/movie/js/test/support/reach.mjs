// What a slow test can reach, for its verdict key (AGENTS.md, "Memoization of
// slow tests"; ADR-003, amended 30 September 2026 by `test-memo-sharing`).
//
// The inputs of a slow test file's key are:
// 1. the import graph: the file and every module it reaches through relative
//    static imports, re-exports and import() of a literal relative path, in
//    .mjs, .js, .ts and .tsx files, followed transitively (a bare specifier,
//    `node:` or a package, is a dependency the lock covers);
// 2. what a reached module reads without importing it, declared in READS: a
//    directory is every file under it except test files and what a build or
//    Python leaves; a module path is a spawned command, followed through its
//    own imports;
// 3. always (ALWAYS): test/support/ (the global setup, setup file and
//    reporter run around every slow test without being imported by it), the
//    viewer double, package.json, package-lock.json, vitest.config.mjs; and
//    the test's own file. The memo adds the toolchain record.
//
// The table can fall behind the code, so `undeclared` names every reached
// module that locates a repository file by path (import.meta.url, or a
// working-directory path such as 'bin/...') and has no entry in READS; a pure
// test in test/memo.test.mjs requires it to name none. No vitest import here,
// so a script can measure with it.
import {readFile,readdir,lstat} from 'node:fs/promises';
import {join,dirname,resolve,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';

export const REPOSITORY=join(dirname(fileURLToPath(import.meta.url)),'..','..');

const posix=path=>path.split(sep).join('/');
const MODULE=/\.(?:mjs|js|ts|tsx)$/;
const TEST_FILE=/\.test\.[cm]?[jt]sx?$/;
// Static relative imports and re-exports, and import() of a literal relative path.
const IMPORTS=/\b(?:import|export)\s*(?:[\w*{}\s,$]*?\s*from\s*)?['"](\.{1,2}\/[^'"]+)['"]|\bimport\(\s*['"](\.{1,2}\/[^'"]+)['"]\s*\)/g;
// A module that locates a repository file by path rather than importing it.
export const LOCATES=/\bimport\.meta\.url\b|\b(?:resolve|join)\(\s*['"](?:\.\.?\/)?(?:bin|src|stage|fixtures|schema|python|test)\//;

const FIXTURE_PROJECT='python/tests/fixtures/project';
// What a module reads without importing it, by path relative to the root. A
// module path (.mjs) is followed through its own imports (a spawned command);
// a directory is every file under it, less test files and what a build or
// Python leaves behind. An empty list says the module locates files but none
// that decides a verdict, and why is written beside it.
export const READS={
  'src/render.mjs':['stage','src/film.html'],        // the page and the stage bundle it serves
  'src/stage-build.mjs':['stage'],                    // bundles the runtime from stage/
  'src/schema.mjs':['schema'],                        // the movie document schema
  'src/speech.mjs':[],                                // ./.env, absent under test: the key is never read by a test
  'test/support/memo.mjs':[],                         // the memo itself: reads the key's inputs
  'test/support/reach.mjs':[],                        // this module: reads the key's inputs
  'test/support/fixture-movie.mjs':['fixtures',FIXTURE_PROJECT],
  'test/support/stage-page.mjs':['src/film.html'],
  'test/pipeline/movie-pipeline.test.mjs':['fixtures','bin/videomaker.mjs'],  // spawns the command line
  'test/pipeline/review-pack.test.mjs':['bin/videomaker.mjs'],                // spawns the command line
  'test/pipeline/source-scenes.test.mjs':['src/film.html'],
};
// Always in a slow test's key, besides its own file and the toolchain record:
// what the runner loads around a test (setup files, reporter, config) and the
// dependency lock.
export const ALWAYS=['test/support','test/viewer-double.mjs','package.json','package-lock.json','vitest.config.mjs'];
const LEFT_BEHIND=new Set(['__pycache__','_build','node_modules']);

async function exists(path){try{await lstat(path);return true;}catch{return false;}}
async function resolveSpecifier(from,spec){
  const base=resolve(dirname(from),spec);
  for(const candidate of [base,base+'.mjs',base+'.ts',base+'.tsx',join(base,'index.ts')])
    if(await exists(candidate)&&(await lstat(candidate)).isFile())return candidate;
  throw new Error(`${from} imports ${spec}, which does not resolve`);
}
async function filesUnder(path,out){
  const info=await lstat(path);
  if(info.isDirectory()){
    for(const entry of (await readdir(path)).sort()){
      if(LEFT_BEHIND.has(entry))continue;
      await filesUnder(join(path,entry),out);
    }
  }else if(!TEST_FILE.test(path))out.add(path);
}

// The modules `entries` import, transitively, and the files those modules
// declare they read. Returns {modules, files}: absolute paths, sorted.
export async function reach(entries,{root=REPOSITORY,reads=READS}={}){
  const modules=new Set(),files=new Set(),todo=[...entries];
  while(todo.length){
    const file=todo.pop();
    if(modules.has(file))continue;
    modules.add(file);
    const text=await readFile(file,'utf8');
    for(const m of text.matchAll(IMPORTS)){
      const target=await resolveSpecifier(file,m[1]??m[2]);
      if(MODULE.test(target))todo.push(target);else files.add(target);
    }
    for(const read of reads[posix(relative(root,file))]??[]){
      const path=join(root,read);
      if(MODULE.test(read)&&!TEST_FILE.test(read))todo.push(path);
      else await filesUnder(path,files);
    }
  }
  return {modules:[...modules].sort(),files:[...files].sort()};
}

// Every input of a slow test file's verdict key, absolute, sorted.
export async function slowTestInputs(file,{root=REPOSITORY,reads=READS,always=ALWAYS}={}){
  const {modules,files}=await reach([file],{root,reads});
  const all=new Set([...modules,...files]);
  for(const p of always)await filesUnder(join(root,p),all);
  all.add(file);
  return [...all].sort();
}

// The modules a slow test reaches that locate repository files by path and
// declare nothing they read: each is a key that could miss an input.
export async function undeclared(entries,{root=REPOSITORY,reads=READS}={}){
  const {modules}=await reach(entries,{root,reads});
  const out=[];
  for(const m of modules){
    const rel=posix(relative(root,m));
    if(!(rel in reads)&&LOCATES.test(await readFile(m,'utf8')))out.push(rel);
  }
  return out;
}
