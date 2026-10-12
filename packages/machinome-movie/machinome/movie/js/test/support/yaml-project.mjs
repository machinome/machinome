// A YAML episode written into a throwaway project and loaded the way the
// command line loads it: loadEpisode validates it, reads its excerpts and
// pictures and converts it to the resolved movie document (the "film") the
// renderer draws. Not a test file: it registers no tests.
//
//   const project=await yamlProject(t,{manifest,files});
//   const film=await project.film(e);          // <dir>/episode.yaml
//   const other=await project.film(e,{at:'cold'});   // <dir>/cold/episode.yaml
//
// `e` is the merged episode (script and production fields together, as the
// old in-memory tests wrote it), with file references (sourceCode, stills,
// clips, evidence, release.descriptionTemplate) relative to the project root.
// The helper writes the episode as JSON (YAML 1.2 reads it), points its model
// at the project's export and pins the export's revision: the export's
// manifest records the project's commit as its `source`, clean, as the
// framework's export made at that commit records it. `project.commit()`
// commits every file but the export and the build directories, and re-pins.
// `project.setManifest(value)` writes the export's manifest with that source,
// unless `value` names its own `source` (undefined leaves it out).
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,relative,dirname} from 'node:path';
import {execFileSync} from 'node:child_process';
import {loadEpisode} from '../../src/episode.mjs';

const FIXED={GIT_AUTHOR_NAME:'Videomaker fixture',GIT_AUTHOR_EMAIL:'fixture@videomaker.invalid',
  GIT_AUTHOR_DATE:'2026-09-30T00:00:00+00:00',GIT_COMMITTER_NAME:'Videomaker fixture',
  GIT_COMMITTER_EMAIL:'fixture@videomaker.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00+00:00',
  GIT_CONFIG_GLOBAL:'/dev/null',GIT_CONFIG_NOSYSTEM:'1'};
export const PAWL_MANIFEST={root:{name:'test',children:[{name:'Feed',children:[{name:'Pawl'}]}]},animation:{loop:2}};
const SCRIPT=['format','id','title','status','learningGoal','shots'];

export async function yamlProject(t,{manifest=PAWL_MANIFEST,files={}}={}){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-yaml-'));
  t?.onTestFinished(()=>process.env.KEEP_VIDEOMAKER_TEST?console.log('Review fixture: '+dir):rm(dir,{recursive:true,force:true}));
  const git=(...args)=>execFileSync('git',args,{cwd:dir,env:{...process.env,...FIXED},encoding:'utf8'}).trim();
  git('init','-q');
  // The export and every build directory stay out of the commit.
  for(const [name,content] of Object.entries({'.gitignore':'/export/\n_build/\n','description.md':'Test description.\n',...files})){
    await mkdir(dirname(join(dir,name)),{recursive:true});await writeFile(join(dir,name),content);
  }
  const exportDir=join(dir,'export','model'),manifestFile=join(exportDir,'manifest.json');
  let written=manifest;
  const project={dir,git,revision:null,manifest:manifestFile,
    // Commits every file but the export and build directories; the export records the new revision.
    async commit(message='fixture'){
      git('add','-A');
      git('commit','-q','--allow-empty','-m',message);
      project.revision=git('rev-parse','HEAD');
      await project.setManifest(written);
      return project.revision;
    },
    async setManifest(value){
      written=value;
      const source='source' in value||!project.revision?{}:{source:{revision:project.revision,dirty:false}};
      await writeFile(manifestFile,JSON.stringify({...value,...source}));
    },
    // Writes the episode at <dir>/<at>/episode.yaml and loads it.
    async write(e,{at='.'}={}){
      const base=join(dir,at),up=p=>relative(base,join(dir,p));
      await mkdir(base,{recursive:true});
      const {paths,wordTiming,pictureMedia,...rest}=structuredClone(e);
      const script={format:'machinome-video-draft/0.2',...Object.fromEntries(SCRIPT.filter(k=>k in rest).map(k=>[k,rest[k]])),
        production:'production.yaml'};
      const production=Object.fromEntries(Object.entries(rest).filter(([k])=>!SCRIPT.includes(k)));
      production.model={timeMode:'normalized-loop',...production.model,manifest:relative(base,manifestFile),
        sourceRevision:project.revision};
      production.evidence=Object.fromEntries(Object.entries(production.evidence??{}).map(([k,v])=>[k,up(v)]));
      production.layers??={};
      for(const kind of ['stills','clips'])if(production[kind])
        production[kind]=Object.fromEntries(Object.entries(production[kind]).map(([k,v])=>[k,{...v,file:up(v.file)}]));
      if(production.sourceCode)production.sourceCode=Object.fromEntries(Object.entries(production.sourceCode)
        .map(([k,{text,...v}])=>[k,{...v,file:up(v.file)}]));
      if(production.release?.descriptionTemplate)production.release.descriptionTemplate=up(production.release.descriptionTemplate);
      await writeFile(join(base,'production.yaml'),JSON.stringify(production,null,1)+'\n');
      await writeFile(join(base,'episode.yaml'),JSON.stringify(script,null,1)+'\n');
      return join(base,'episode.yaml');
    },
    async film(e,options){return loadEpisode(await project.write(e,options));},
  };
  await mkdir(exportDir,{recursive:true});
  await project.setManifest(manifest);
  await project.commit();
  return project;
}
