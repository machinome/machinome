// Layer 9: repository pins of the react-stage change. Pure: they read files.
import {test} from 'vitest';
import assert from 'node:assert/strict';
import {readFile,readdir,access,realpath,lstat} from 'node:fs/promises';
import {join,dirname,relative} from 'node:path';
import {fileURLToPath} from 'node:url';
import {SCHEMA_FILE,MOVIE_SCHEMA} from '../src/schema.mjs';
import {slowTestInputs,REPOSITORY} from './support/memo.mjs';
import config,{SLOW,VIEWER} from '../vitest.config.mjs';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const exists=path=>access(join(root,path)).then(()=>true,()=>false);
async function files(dir,keep=()=>true,out=[]){
  for(const entry of await readdir(join(root,dir),{withFileTypes:true})){
    const path=join(dir,entry.name);
    if(entry.isDirectory())await files(path,keep,out);else if(keep(path))out.push(path);
  }
  return out.sort();
}

test('the manual has the stage authoring contract and the movie document',async()=>{
  assert.ok(await exists('docs/movie-document.md'),'docs/movie-document.md');
  assert.ok(await exists('docs/stage.md'),'docs/stage.md, the authoring contract of the stage');
});

test('schema/machinome-movie-0.2.json is the one schema both runtimes read',async()=>{
  assert.equal(SCHEMA_FILE,join(root,'schema','machinome-movie-0.2.json'),'src/schema.mjs reads it');
  assert.deepEqual((await readdir(join(root,'schema'))).filter(n=>n.startsWith('machinome-movie')),['machinome-movie-0.2.json']);
  const bytes=await readFile(SCHEMA_FILE);
  assert.deepEqual(MOVIE_SCHEMA,JSON.parse(bytes));
  const python=join(root,'python','machinome_movie','machinome-movie-0.2.json');
  assert.equal(await realpath(python),await realpath(SCHEMA_FILE),'the Python package resolves to the same file');
  assert.ok((await readFile(python)).equals(bytes));
  const others=(await readdir(join(root,'python','machinome_movie'))).filter(n=>/^machinome-movie-.*\.json$/.test(n));
  assert.deepEqual(others,['machinome-movie-0.2.json']);
});

test('the earlier film page is gone: src/film.js does not exist',async()=>{
  assert.equal(await exists('src/film.js'),false);
  const page=await readFile(join(root,'src','film.html'),'utf8');
  assert.match(page,/<div id="stage-root"><\/div><div id="transition"><\/div><div id="chrome"><\/div>/);
  assert.doesNotMatch(page,/film\.js/);
});

test('no page source carries a brand or a series label',async()=>{
  const sources=['src/film.html',...await files('stage',path=>!/\.test\.[cm]?[jt]sx?$/.test(path))];
  assert.ok(sources.some(s=>s.endsWith('runtime.tsx'))&&sources.some(s=>s.endsWith('stage.css')));
  for(const path of sources){
    const text=await readFile(join(root,path),'utf8');
    assert.doesNotMatch(text,/\bMACHINOME\b/,`${path} carries the brand`);
    assert.doesNotMatch(text,/LEONARDO|HOW IT WORKS/i,`${path} carries a series`);
    assert.doesNotMatch(text,/\b[A-Z]{2,}(?: [A-Z]{2,})* · [A-Z]{2,}/,`${path} carries a series label`);
  }
});

test('the slow project is the browser and pipeline directories, the viewer project the viewer directory, and every test there is memoized',async()=>{
  assert.deepEqual(SLOW,['test/browser/**/*.test.mjs','test/pipeline/**/*.test.mjs']);
  const projects=Object.fromEntries(config.test.projects.map(p=>[p.test.name,p.test]));
  assert.deepEqual(projects.slow.include,SLOW);assert.deepEqual(projects.pure.exclude,[...SLOW,...VIEWER]);
  // Layer 6 is its own project, after the slow one, on the same global setup (ADR-008).
  assert.deepEqual(VIEWER,['test/viewer/**/*.test.mjs']);assert.deepEqual(projects.viewer.include,VIEWER);
  assert.ok(projects.viewer.sequence.groupOrder>projects.slow.sequence.groupOrder);
  assert.deepEqual(projects.viewer.globalSetup,projects.slow.globalSetup);assert.equal(projects.viewer.fileParallelism,false);
  const viewer=(await files('test/viewer')).filter(p=>p.endsWith('.test.mjs'));
  assert.ok(viewer.length>=1);
  for(const path of viewer){
    const text=await readFile(join(root,path),'utf8');
    assert.match(text,/import \{viewerTest as test(,[^}]*)?\} from '\.\.\/support\/viewer-bundle\.mjs';/,`${path} registers viewerTests`);
    assert.doesNotMatch(text,/import \{[^}]*\b(test|it)\b[^}]*\} from 'vitest'/,`${path} registers no plain vitest test`);
  }
  const slow=[...await files('test/browser'),...await files('test/pipeline')].filter(p=>p.endsWith('.test.mjs'));
  assert.ok(slow.length>=9);
  for(const path of (await files('test',p=>/^test\/[^/]+\.test\.mjs$/.test(p))))
    assert.doesNotMatch(await readFile(join(root,path),'utf8'),/^import .* from '(\.\/support\/stage\.mjs|playwright)';$/m,`${path} opens no page: it is not slow`);
  for(const path of slow){
    const text=await readFile(join(root,path),'utf8');
    assert.match(text,/import \{slowTest as test(,[^}]*)?\} from '\.\.\/support\/memo\.mjs';/,`${path} registers slowTests`);
    assert.doesNotMatch(text,/import \{[^}]*\b(test|it)\b[^}]*\} from 'vitest'/,`${path} registers no plain vitest test`);
  }
});

test('a slow test\'s verdict key reads the stage runtime and the fixture project, not what Python or a build leaves there',async()=>{
  const inputs=(await slowTestInputs(join(root,'test','browser','stage.test.mjs'))).map(p=>relative(REPOSITORY,p));
  for(const served of ['stage/runtime.tsx','stage/shipped.tsx','stage/stage.css','src/film.html'])assert.ok(inputs.includes(served),served);
  assert.ok(!inputs.includes('stage/stage.test.tsx'),'a stage component test is not served');
  const project=inputs.filter(p=>p.startsWith('python/tests/fixtures/project/'));
  for(const needed of ['models/seesaw.py','export/seesaw/manifest.json','videos/tour/stage.tsx','videos/tour/stage.css','media/plate.png'])
    assert.ok(project.includes(`python/tests/fixtures/project/${needed}`),needed);
  assert.ok(project.some(p=>/^python\/tests\/fixtures\/project\/export\/seesaw\/.+\.stl$/.test(p)),'the export\'s mesh');
  assert.deepEqual(project.filter(p=>/(^|\/)(__pycache__|_build)(\/|$)/.test(p)),[]);
  for(const path of project)assert.ok((await lstat(join(REPOSITORY,path))).isFile()||(await lstat(join(REPOSITORY,path))).isSymbolicLink());
});
