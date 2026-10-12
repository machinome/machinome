// Layer 9: repository pins of the react-stage change. Pure: they read files.
// The manual is the machinome framework's, which the tool's pages joined, and
// the package's changelog, decision log and records are in its directory
// (change join-movie of the machinome repository).
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
// The package's directory (packages/machinome-movie) and the framework's manual.
const PACKAGE='../../..',MANUAL='../../../../machinome/docs';
const FILM=[`${MANUAL}/howto/film-a-movie.rst`,`${MANUAL}/reference/movie/command.rst`];
const STAGE=`${MANUAL}/howto/draw-a-movie-stage.rst`,DOCUMENT=`${MANUAL}/reference/movie/document.rst`;
const DECLARE=`${MANUAL}/howto/declare-a-movie.rst`,EPISODE=`${MANUAL}/reference/movie/episode.rst`;
const CHANGELOG=`${PACKAGE}/CHANGELOG.md`,ADRS=`${PACKAGE}/workflow/adrs`,OVERVIEW=`${PACKAGE}/workflow/architecture-overview.md`;
const read=async(...paths)=>(await Promise.all(paths.map(path=>readFile(join(root,path),'utf8')))).join('\n').split(/\s+/).join(' ');
async function files(dir,keep=()=>true,out=[]){
  for(const entry of await readdir(join(root,dir),{withFileTypes:true})){
    const path=join(dir,entry.name);
    if(entry.isDirectory())await files(path,keep,out);else if(keep(path))out.push(path);
  }
  return out.sort();
}


test('the manual has the stage authoring contract and the movie document',async()=>{
  assert.ok(await exists(DOCUMENT),DOCUMENT);
  assert.ok(await exists(STAGE),`${STAGE}, the authoring contract of the stage`);
});
test('schema/machinome-movie-0.2.json is the one schema both runtimes read',async()=>{
  assert.equal(SCHEMA_FILE,join(root,'schema','machinome-movie-0.2.json'),'src/schema.mjs reads it');
  assert.deepEqual((await readdir(join(root,'schema'))).filter(n=>n.startsWith('machinome-movie')),['machinome-movie-0.2.json']);
  const bytes=await readFile(SCHEMA_FILE);
  assert.deepEqual(MOVIE_SCHEMA,JSON.parse(bytes));
  const python=join(root,'..','machinome-movie-0.2.json');
  assert.equal(await realpath(python),await realpath(SCHEMA_FILE),'the Python package resolves to the same file');
  assert.ok((await readFile(python)).equals(bytes));
  const others=(await readdir(join(root,'..'))).filter(n=>/^machinome-movie-.*\.json$/.test(n));
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
  const project=inputs.filter(p=>p.startsWith('../../../tests/fixtures/project/'));
  for(const needed of ['models/seesaw.py','export/seesaw/manifest.json','videos/tour/stage.tsx','videos/tour/stage.css','media/plate.png'])
    assert.ok(project.includes(`../../../tests/fixtures/project/${needed}`),needed);
  assert.ok(project.some(p=>/^\.\.\/\.\.\/\.\.\/tests\/fixtures\/project\/export\/seesaw\/.+\.stl$/.test(p)),'the export\'s mesh');
  assert.deepEqual(project.filter(p=>/(^|\/)(__pycache__|_build)(\/|$)/.test(p)),[]);
  for(const path of project)assert.ok((await lstat(join(REPOSITORY,path))).isFile()||(await lstat(join(REPOSITORY,path))).isSymbolicLink());
});

test('the manual, the contract and the records say how a clocked take is filmed (pose-a-take)',async()=>{
  const film=await read(...FILM);
  assert.ok(film.includes('and clocked machines through a take'),'the guide: what is filmable');
  assert.ok(film.includes('running machines are refused'),'the guide: running machines');
  assert.ok(film.includes('A movie on a clocked take needs Viewer API 29'),'the guide: the viewer it needs');
  assert.ok(film.includes('``Take: 3 steps, marks one 2 s, nine 6 s, ten 8 s, 8 s long; the replay of its steps gives the recorded bank at every mark``'),'the command: check\'s take line');
  const stage=await read(STAGE);
  assert.ok(stage.includes('a view on a clocked take by restoring the machine\'s bank the frame gives it on the viewer\'s machine, with the take\'s identity, before its camera is set'),'the stage page: the view row');
  assert.ok(stage.includes('``Viewer canvas exceeds its view``'),'the stage page: the canvas larger than its view');
  assert.ok((await read(DOCUMENT)).includes('A document needs Viewer API 29 when it films a clocked take'),'the document page: the API');
  assert.ok((await read(CHANGELOG)).includes('(`pose-a-take`, ADR-012)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-012](STAGE/ADR-012-a-view-on-a-take-is-posed-by-restoring-the-machines-bank.md)'),'the ADR index');
});

test('the manual and the records say what provenance records of a dirty tree, and the Stage line\'s two hashes (honest-provenance)',async()=>{
  const line='``Stage: bundled <path>/stage.js (sha256 <prefix>) and stage.css (sha256 <prefix>) from stage.tsx; types checked``';
  const film=await read(...FILM);
  assert.ok(film.includes(line),'the command: check\'s Stage line');
  assert.ok(film.includes('``Project tree: clean at <head>``'),'the command: the tree line');
  for(const field of ['``projectDirty``','``workflowDirty``','``releaseIssues``'])assert.ok(film.includes(field),`the command: ${field}`);
  assert.ok((await read(STAGE)).includes('Stage: bundled <root>/_build/stage/stage.js (sha256 <12 hex digits>) and stage.css (sha256 <12 hex digits>) from stage.tsx; types checked'),'the stage page: the Stage line');
  assert.ok((await read(CHANGELOG)).includes('(`honest-provenance`, ADR-015)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-015](PIPELINE/ADR-015-provenance-records-whether-each-tree-was-dirty.md)'),'the ADR index');
});

test('the manual and the records say a continuation that crosses a mark is reported, in the words check prints (check-the-continuation)',async()=>{
  // The command's page quotes the line check prints for the fixture count:
  // the report its pinned resolution records on nine.
  const pinned=JSON.parse(await readFile(join(root,'fixtures','resolved','count.json'),'utf8'));
  const report=pinned.chapters[0].shots.find(s=>s.id==='nine').model.crossing.report;
  const film=await read(...FILM);
  assert.ok(film.includes(`\`\`${report}\`\``),'the command: check\'s continuation line');
  assert.ok(film.includes('It is a report, not a refusal'),'the command: not a refusal');
  assert.ok((await read(DOCUMENT)).includes('a shot whose continuation through its outgoing join (rule 8) crosses a mark gains ``crossing`` on its ``model``'),'the document page: the resolved field');
  assert.ok((await read(DECLARE)).includes('``check`` reports each shot whose continuation crosses a mark, without refusing it'),'the declarations page: the join');
  assert.ok((await read(CHANGELOG)).includes('(`check-the-continuation`, ADR-014)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-014](TIMELINE/ADR-014-a-continuation-that-crosses-a-mark-is-reported-from-the-frames-the-join-poses.md)'),'the ADR index');
});

test('the manual and the records say the stage bundle is the same bytes from any checkout (stable-stage-bundle)',async()=>{
  const stage=await read(STAGE);
  assert.ok(stage.includes('**The same bytes from any checkout.**'),'the stage page: the bullet');
  for(const name of ['``videomaker/stage/<file>``','``videomaker/node_modules/<file>``','``project/<path in the repository>``'])
    assert.ok(stage.includes(name),`the stage page: ${name}`);
  assert.ok((await read(...FILM)).includes('the same template bundled from another checkout of the tool does not'),'the command: the cache key');
  assert.ok((await read(CHANGELOG)).includes('(`stable-stage-bundle`, ADR-013)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-013](PIPELINE/ADR-013-the-stage-bundle-names-its-files-by-the-tool-and-the-project.md)'),'the ADR index');
});

test('the manual reads the revision from the export\'s source and names no sidecar (read-the-exports-source)',async()=>{
  const pages=[...FILM,EPISODE,DECLARE,DOCUMENT,STAGE,OVERVIEW,'fixtures/README.md'];
  for(const page of pages)assert.ok(!(await read(page)).includes('source-revision.txt'),`${page} names no sidecar`);
  const film=await read(...FILM);
  assert.ok(film.includes('``Export: made from <revision>, clean``'),'the command: the Export line');
  for(const field of ['``source.revision``','``exportRevision``','``exportDirty``'])assert.ok(film.includes(field),`the command: ${field}`);
  assert.ok((await read(DECLARE)).includes('``source.revision``'),'the declarations page: where the revision comes from');
  assert.ok((await read(EPISODE)).includes('``source.revision``'),'the episode page: the production model block');
  assert.ok((await read(CHANGELOG)).includes('(`read-the-exports-source`, ADR-019)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-019](SOURCE/ADR-019-the-models-revision-is-the-one-its-export-records.md)'),'the ADR index');
  for(const name of ['seesaw','counter'])assert.ok(!await exists(`../../../tests/fixtures/project/export/${name}/source-revision.txt`),`export/${name} has no sidecar`);
});

test('the manual and the records say where a highlight landed and what check measured of the text (proofs-report-the-look)',async()=>{
  const film=await read(...FILM),stage=await read(STAGE);
  assert.ok(film.includes('``preview/highlights/<shot>-<cue>-<parts>-{lit,unlit,difference}.png``'),'the command: the highlight images');
  assert.ok(film.includes('``Shot source: source balance.code in left at 13.1 px (1.02 vw)``'),'the command: check\'s text line');
  assert.ok(film.includes('``Text not measured: …``'),'the command: the text check did not measure');
  assert.ok(stage.includes('Shot question: title opening.title in headline on 1 line, its subtitle on 1 line'),'the stage page: check\'s text line');
  assert.ok(stage.includes('``fontSize``')&&stage.includes('``subtitleLines``'),'the stage page: what the shipped elements report');
  assert.ok((await read(EPISODE)).includes('``preview/highlights/<shot>-highlight-<i>-<parts>-{unlit,lit,difference}.png``'),'the episode page: the highlight images');
  assert.ok((await read(CHANGELOG)).includes('(`proofs-report-the-look`, ADR-017)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('[ADR-017](PIPELINE/ADR-017-what-a-proof-cannot-judge-it-measures-and-lays-out.md)'),'the ADR index');
});

test('the manual and the records say a view on a take is posed through the take transport (take-transport)',async()=>{
  const stage=await read(STAGE);
  assert.ok(stage.includes('``videomaker/transport/<file>``'),'the stage page: the bundle names the transport by the tool');
  assert.ok(stage.includes('through the take transport'),'the stage page: the view row');
  const contract=await read(DOCUMENT);
  assert.ok(contract.includes('``transport(key)``'),'the document page: window.film.transport');
  assert.ok(contract.includes('``attachMachine(viewer, take.identity)``'),'the document page: the pose of a view on a take');
  assert.ok((await read(OVERVIEW)).includes('`transport/`'),'the architecture overview');
  // Layer 4, the take transport's own tests, under the stage project.
  const projects=Object.fromEntries(config.test.projects.map(p=>[p.test.name,p.test]));
  assert.ok(projects.stage.include.includes('transport/**/*.test.ts'),'vitest.config.mjs: layer 4');
  assert.ok((await read(CHANGELOG)).includes('(`take-transport`, ADR-020)'),'the changelog bullet');
  assert.ok((await read(`${ADRS}/README.md`)).includes('| [ADR-020](STAGE/ADR-020-a-take-transport-is-the-browsers-pose-of-a-take-written-to-lift.md) | STAGE | A take transport is the browser\'s pose of a take, written to lift | Accepted |'),'the ADR index');
  assert.ok(await exists(`${ADRS}/STAGE/ADR-020-a-take-transport-is-the-browsers-pose-of-a-take-written-to-lift.md`),'ADR-020');
});

test('every option the Node side declares but the viewer\'s is documented in the command reference',async()=>{
  const script=await readFile(join(root,'bin','videomaker.mjs'),'utf8');
  const declared=/parseArgs\(\{allowPositionals:true,options:\{([\s\S]*?)\}\}\)/.exec(script);
  assert.ok(declared,'bin/videomaker.mjs declares its options in one parseArgs call');
  const names=[...declared[1].matchAll(/(\w+):\{type:/g)].map(m=>m[1]).filter(name=>name!=='help');
  assert.ok(['viewer','width','fps','silent'].every(name=>names.includes(name)),names.join(', '));
  // machinome movie gives the Node side the installed viewer's bundle itself.
  const pages=[`${MANUAL}/reference/movie/command.rst`,`${MANUAL}/reference/cli.rst`];
  for(const page of pages){
    const text=await read(page);
    for(const name of names.filter(name=>name!=='viewer'))assert.ok(text.includes(`--${name}`),`${page}: --${name}`);
  }
  assert.ok(!(await read(...FILM)).includes('--viewer'),'no film page names --viewer');
});

test('the manual and the records say how a film is served live (live-server)',async()=>{
  const film=await read(...FILM);
  assert.ok(film.includes('machinome movie live '),'the guide: the command in use');
  assert.ok(film.includes('``Live: http://127.0.0.1:<port>/``'),'the command: the address line');
  for(const route of ['``/film.json``','``/frame?t=<seconds>``','``/take.json``','``/film.html``','``/narration.wav``','``/captions.json``','``/events``',
    '``The player is not built``','``No take document``'])
    assert.ok(film.includes(route),`the command: ${route}`);
  const script=await readFile(join(root,'bin','videomaker.mjs'),'utf8');
  assert.ok(script.includes('videomaker live EPISODE.yaml|MOVIE.json [--viewer BUNDLE.js] [--width 960] [--port 0] [--poll MS] [--open]'),'the usage line');
  const overview=await read(OVERVIEW);
  for(const module of ['src/check.mjs','src/film-assets.mjs','src/live.mjs'])assert.ok(overview.includes(module),`overview: ${module}`);
  const adr='PIPELINE/ADR-021-a-live-session-serves-the-renders-stage-and-the-frame-function-to-a-browser.md';
  assert.ok(await exists(`${ADRS}/${adr}`),adr);
  assert.ok((await read(`${ADRS}/README.md`)).includes(`[ADR-021](${adr})`),'the ADR index');
  assert.ok((await read(CHANGELOG)).includes('(`live-server`, ADR-021)'),'the changelog bullet');
});

test('the manual and the records say how the player shows a film and a take, and what it does not draw (player-page)',async()=>{
  const film=await read(...FILM);
  for(const words of ['``#movie``','``#take/take``','``#take/loop``','Space plays and pauses','shown as a cut at its midpoint',
    'shown without its fade','drawn live','``window.player``','provisional','machinome movie watch'])
    assert.ok(film.includes(words),`the command: ${words}`);
  assert.doesNotMatch(film,/The player page is not built yet/,'the command: the player is built');
  const adr='PIPELINE/ADR-022-the-player-is-two-transports-over-the-renders-stage-and-a-video-is-its-recording.md';
  assert.ok(await exists(`${ADRS}/${adr}`),adr);
  assert.ok((await read(`${ADRS}/README.md`)).includes(`| [ADR-022](${adr}) | PIPELINE | The player is two transports over the render's stage, and a video is its recording | Accepted |`),'the ADR index');
  assert.ok((await read(CHANGELOG)).includes('(`player-page`, ADR-022)'),'the changelog bullet');
  const overview=await read(OVERVIEW);
  for(const module of ['`player/`','src/player-build.mjs','`markInstants`'])assert.ok(overview.includes(module),`overview: ${module}`);
  assert.doesNotMatch(overview,/player page that drives it is not built/,'overview: what is changing');
  // Layer 4, the player's pure parts, under the stage project.
  const projects=Object.fromEntries(config.test.projects.map(p=>[p.test.name,p.test]));
  assert.ok(projects.stage.include.includes('player/**/*.test.ts'),'vitest.config.mjs: layer 4');
  assert.ok((await read(DECLARE)).includes('``watch`` evaluates the movie as ``evaluate`` does'),'the declarations page: watch');
});

test('the manual names the installed viewer and the API each film needs (status-claims)',async()=>{
  for(const path of [...FILM,EPISODE])
    assert.doesNotMatch(await read(path),/no published release|not yet declared by a published release|not yet a published release|source checkout provides/,`${path}: the viewer's release`);
  const film=await read(...FILM);
  assert.ok(film.includes('with this release it is |viewer_version|, which declares viewer API |viewer_api|'),'the guide: the installed viewer');
  assert.ok(film.includes('need Viewer API 28')&&film.includes('A movie on a clocked take needs Viewer API 29'),'the guide: the API each film needs');
});
