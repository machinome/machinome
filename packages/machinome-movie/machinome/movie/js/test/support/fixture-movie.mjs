// The shared fixture project (python/tests/fixtures/project) as a movie the
// browser and pipeline tests produce: copied to a temporary directory,
// committed by the recipe of fixtures/README.md (so its revision is the one
// the documents pin), with a fixture document written beside its movie and
// its take doubles installed as the speech command caches them. Not a test
// file: it registers no tests.
import {cp,mkdtemp,mkdir,readFile,rm,writeFile,access} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {speechCacheEntry,spokenChapters} from '../../src/speech.mjs';
import {installTake} from '../project-fixture.mjs';
import {viewerDouble} from '../viewer-double.mjs';

export const REPOSITORY=join(dirname(fileURLToPath(import.meta.url)),'..','..');
export const PROJECT=join(REPOSITORY,'python','tests','fixtures','project');
export const FIXTURES=join(REPOSITORY,'fixtures');
const FIXED={GIT_AUTHOR_NAME:'Videomaker fixture',GIT_AUTHOR_EMAIL:'fixture@videomaker.invalid',
  GIT_AUTHOR_DATE:'2026-09-30T00:00:00+00:00',GIT_COMMITTER_NAME:'Videomaker fixture',
  GIT_COMMITTER_EMAIL:'fixture@videomaker.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00+00:00',
  GIT_CONFIG_GLOBAL:'/dev/null',GIT_CONFIG_NOSYSTEM:'1'};
const readJson=async file=>JSON.parse(await readFile(file,'utf8'));
const exists=file=>access(file).then(()=>true,()=>false);
// The viewer double's machine for a take: its identity, its initial bank and
// its steps as the requests the double answers. Its part rects follow the
// counter's units, 0 to 9, the input whose drum the take turns.
export const FOLLOWS={input:'units',range:[0,9]};
export const takeMachine=take=>({machine:{identity:take.identity,initial:take.initial,requests:take.steps,follows:FOLLOWS}});

// A copy of the fixture project, committed as the recipe says. `t` (a vitest
// context) removes it after the test unless KEEP_VIDEOMAKER_TEST is set.
export async function fixtureProjectCopy(t){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-movie-'));
  t?.onTestFinished(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  const skip=/(^|\/)(_build|__pycache__)(\/|$)/;
  await cp(PROJECT,dir,{recursive:true,filter:source=>!skip.test(source.slice(PROJECT.length))});
  const git=(...args)=>execFileSync('git',args,{cwd:dir,env:{...process.env,...FIXED},encoding:'utf8'}).trim();
  git('init','-q');
  // Everything but the export, as the recipe commits it.
  git('add','-A','--',':!export');
  git('commit','-q','-m','Fixture project');
  const revision=git('rev-parse','HEAD');
  // The framework recorded the commit each export was made from in its
  // manifest's source (scripts/pin-fixture-project.mjs exports from it).
  const pinned=(await readJson(join(dir,'export','seesaw','manifest.json'))).source?.revision;
  if(revision!==pinned)throw new Error(`The fixture project's commit is ${revision}, and export/seesaw/manifest.json records source.revision ${pinned}; re-pin it by the recipe in fixtures/README.md`);
  return {dir,git};
}

// A fixture document (fixtures/documents/<name>.json) written where the
// Python side writes it, <movie dir>/_build/movie.json with root "..", and
// its takes cached; returns the document's path and the project copy.
export async function fixtureMovie(t,name='tour',{takes=true,viewer:given}={}){
  const {dir,git}=await fixtureProjectCopy(t);
  const doc=await readJson(join(FIXTURES,'documents',`${name}.json`));
  // A movie on a clocked take is drawn by a Viewer API 29 double whose machine
  // answers the take's own requests.
  const viewer=given??(doc.take?{parts:'*',tintHighlight:true,api:29,...takeMachine(doc.take)}:{parts:'*',tintHighlight:true});
  const movie=join(dir,'videos',name),build=join(movie,'_build'),file=join(build,'movie.json');
  await mkdir(build,{recursive:true});
  await writeFile(file,JSON.stringify({...doc,root:'..'},null,2)+'\n');
  const pending={audio:doc.audio,paths:{build},chapters:doc.chapters.map(c=>({id:c.id,narration:c.narration}))};
  const installed=[];
  if(takes)for(const [i,chapter] of doc.chapters.entries()){
    const take=join(FIXTURES,'takes',name,`${chapter.id}.json`);
    if(!await exists(take))continue;
    const record=await readJson(take);
    installed.push(await installTake(speechCacheEntry(pending,spokenChapters(pending),i),record));
  }
  const viewerFile=join(dir,'viewer-double.js');
  await writeFile(viewerFile,`// machinome-viewer double, viewer API ${viewer.api??28}\n${viewerDouble(viewer)}`);
  return {dir,git,movie,build,file,viewer:viewerFile,takes:installed,document:doc};
}
