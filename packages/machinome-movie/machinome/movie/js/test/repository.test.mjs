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

test('the manual, the contract and the records say how a clocked take is filmed (pose-a-take)',async()=>{
  const read=async path=>(await readFile(join(root,path),'utf8')).split(/\s+/).join(' ');
  const readme=await read('README.md');
  assert.ok(readme.includes('and clocked machines through a take'),'README: what is filmable');
  assert.ok(readme.includes('running machines are refused'),'README: running machines');
  assert.ok(readme.includes('A movie on a clocked take needs Viewer API 29'),'README: the viewer it needs');
  assert.ok(readme.includes('`Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark`'),'README: check\'s take line');
  const stage=await read('docs/stage.md');
  assert.ok(stage.includes('a view on a clocked take by restoring the machine\'s bank the frame gives it on the viewer\'s machine, with the take\'s identity, before its camera is set'),'stage.md: the view row');
  assert.ok(stage.includes('`Viewer canvas exceeds its view`'),'stage.md: the canvas larger than its view');
  assert.ok((await read('docs/movie-document.md')).includes('A document needs Viewer API 29 when it films a clocked take'),'movie-document.md: the API');
  assert.ok((await read('CHANGELOG.md')).includes('(`pose-a-take`, ADR-012)'),'the changelog bullet');
  assert.ok((await read('docs/adrs/README.md')).includes('[ADR-012](STAGE/ADR-012-a-view-on-a-take-is-posed-by-restoring-the-machines-bank.md)'),'the ADR index');
  assert.doesNotMatch(await read('AGENTS.md'),/Only posed models with a normalized loop are filmable/);
});

test('the manual and the records say what provenance records of a dirty tree, and the Stage line\'s two hashes (honest-provenance)',async()=>{
  const read=async path=>(await readFile(join(root,path),'utf8')).split(/\s+/).join(' ');
  const line='`Stage: bundled <path>/stage.js (sha256 <prefix>) and stage.css (sha256 <prefix>) from stage.tsx; types checked`';
  const readme=await read('README.md');
  assert.ok(readme.includes(line),'README: check\'s Stage line');
  assert.ok(readme.includes('`Project tree: clean at <head>`'),'README: the tree line');
  for(const field of ['`projectDirty`','`workflowDirty`','`releaseIssues`'])assert.ok(readme.includes(field),`README: ${field}`);
  assert.ok((await read('docs/stage.md')).includes('Stage: bundled <root>/_build/stage/stage.js (sha256 <12 hex digits>) and stage.css (sha256 <12 hex digits>) from stage.tsx; types checked'),'stage.md: the Stage line');
  assert.ok((await read('CHANGELOG.md')).includes('(`honest-provenance`, ADR-015)'),'the changelog bullet');
  assert.ok((await read('docs/adrs/README.md')).includes('[ADR-015](PIPELINE/ADR-015-provenance-records-whether-each-tree-was-dirty.md)'),'the ADR index');
  assert.ok((await readFile(join(root,'.gitignore'),'utf8')).split('\n').includes('/WTs/'),'.gitignore: the worktrees, as AGENTS.md says');
});

test('the manual and the records say a continuation that crosses a mark is reported, in the words check prints (check-the-continuation)',async()=>{
  const read=async path=>(await readFile(join(root,path),'utf8')).split(/\s+/).join(' ');
  // The README quotes the line check prints for the fixture count: the
  // report its pinned resolution records on nine.
  const pinned=JSON.parse(await readFile(join(root,'fixtures','resolved','count.json'),'utf8'));
  const report=pinned.chapters[0].shots.find(s=>s.id==='nine').model.crossing.report;
  const readme=await read('README.md');
  assert.ok(readme.includes(`\`${report}\``),'README: check\'s continuation line');
  assert.ok(readme.includes('It is a report, not a refusal'),'README: not a refusal');
  assert.ok((await read('docs/movie-document.md')).includes('a shot whose continuation through its outgoing join (rule 8) crosses a mark gains `crossing` on its `model`'),'movie-document.md: the resolved field');
  assert.ok((await read('docs/declaring-a-movie.md')).includes('`check` reports each shot whose continuation crosses a mark, without refusing it'),'declaring-a-movie.md: the join');
  assert.ok((await read('CHANGELOG.md')).includes('(`check-the-continuation`, ADR-014)'),'the changelog bullet');
  assert.ok((await read('docs/adrs/README.md')).includes('[ADR-014](TIMELINE/ADR-014-a-continuation-that-crosses-a-mark-is-reported-from-the-frames-the-join-poses.md)'),'the ADR index');
});

test('the manual and the records say the stage bundle is the same bytes from any checkout (stable-stage-bundle)',async()=>{
  const read=async path=>(await readFile(join(root,path),'utf8')).split(/\s+/).join(' ');
  const stage=await read('docs/stage.md');
  assert.ok(stage.includes('**The same bytes from any checkout.**'),'stage.md: the bullet');
  for(const name of ['`videomaker/stage/<file>`','`videomaker/node_modules/<file>`','`project/<path in the repository>`'])
    assert.ok(stage.includes(name),`stage.md: ${name}`);
  assert.ok((await read('README.md')).includes('the same template bundled from another checkout of the tool does not'),'README: the cache key');
  assert.ok((await read('CHANGELOG.md')).includes('(`stable-stage-bundle`, ADR-013)'),'the changelog bullet');
  assert.ok((await read('docs/adrs/README.md')).includes('[ADR-013](PIPELINE/ADR-013-the-stage-bundle-names-its-files-by-the-tool-and-the-project.md)'),'the ADR index');
});
