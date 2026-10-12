#!/usr/bin/env node
// Re-pins the fixture project after any of its files changed, in one command
// (fixtures/README.md, "The fixture project"): it makes the project's commit by
// the recipe, exports every model of the project from that commit with the
// framework's command, so that each export's manifest records the commit in
// its `source` (the framework's ADR-158), replaces export/<model>/ with what
// the command wrote, evaluates every document fixtures/manifest.json registers
// whose movie the project declares into fixtures/documents/, and prints what
// changed. It never writes fixtures/resolved/: a person runs
// scripts/pin-resolved.mjs for the documents that changed and reviews the pins
// before committing.
// Usage: node scripts/pin-fixture-project.mjs [--python PYTHON] [--machinome MACHINOME]
// PYTHON (default python3) runs the machinome.movie package of this
// package's directory, packages/machinome-movie/, and must have its
// dependencies installed;
// MACHINOME (default machinome) is the framework's command line.
import {cp,mkdtemp,readFile,readdir,rm,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname,relative,sep} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const project=join(root,'..','..','..','tests','fixtures','project'),fixtures=join(root,'fixtures');
// Every export of the project and the options it is made with: the seesaw's
// loop at 30 fps over 600 frames, the clocked counter at the defaults.
const EXPORTS={counter:[],seesaw:['--fps','30','--frames','600']};
// The recipe's identity, date and message, and no global or system Git
// configuration; nothing of the caller's Git environment is inherited.
const FIXED={GIT_AUTHOR_NAME:'Videomaker fixture',GIT_AUTHOR_EMAIL:'fixture@videomaker.invalid',
  GIT_AUTHOR_DATE:'2026-09-30T00:00:00+00:00',GIT_COMMITTER_NAME:'Videomaker fixture',
  GIT_COMMITTER_EMAIL:'fixture@videomaker.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00+00:00',
  GIT_CONFIG_GLOBAL:'/dev/null',GIT_CONFIG_NOSYSTEM:'1'};
const LEFT_OUT=new Set(['export','_build','__pycache__']);
const read=file=>readFile(file,'utf8').catch(error=>{if(error.code==='ENOENT')return null;throw error;});
const withoutGit=()=>Object.fromEntries(Object.entries(process.env).filter(([key])=>!key.startsWith('GIT_')));

// The exports the project holds now: each directory of export/ with a
// manifest.json. They must be the ones this script makes.
async function exportsNow(){
  const exports=join(project,'export'),found=[];
  for(const entry of await readdir(exports,{withFileTypes:true}))
    if(entry.isDirectory()&&await read(join(exports,entry.name,'manifest.json'))!==null)found.push(entry.name);
  return found.sort();
}

// The commit of the project made by the recipe (every file but export/,
// _build/ and __pycache__/, in a fresh repository), and each model exported
// from it into a directory outside it, so that the framework records the
// recipe commit, clean. No bytecode is written: a __pycache__/ in the copy
// would make the record dirty.
async function exportFromTheRecipe(machinome,each){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-fixture-project-'));
  const out=await mkdtemp(join(tmpdir(),'videomaker-fixture-export-'));
  try{
    await cp(project,dir,{recursive:true,filter:source=>!relative(project,source).split(sep).some(part=>LEFT_OUT.has(part))});
    const env={...withoutGit(),...FIXED};
    const git=(...args)=>execFileSync('git',args,{cwd:dir,env,encoding:'utf8'}).trim();
    git('init','-q');git('add','-A');git('commit','-q','-m','Fixture project');
    const revision=git('rev-parse','HEAD');
    // The framework builds each model under the project's _build/, which the
    // copy ignores, as a project ignores its build products, so that the next
    // export's record is not made dirty by the last one's build. The rule
    // lives in the repository's own exclude file, outside the commit.
    await writeFile(join(dir,'.git','info','exclude'),'/_build/\n');
    for(const [name,options] of Object.entries(EXPORTS)){
      const target=join(out,name);
      execFileSync(machinome,['export',name,'-o',target,...options,'--no-widget'],
        {cwd:dir,env:{...env,PYTHONDONTWRITEBYTECODE:'1'},stdio:['ignore','ignore','inherit']});
      const source=JSON.parse(await readFile(join(target,'manifest.json'),'utf8')).source;
      if(source?.revision!==revision||source?.dirty!==false)
        throw new Error(`export/${name}: the framework recorded source ${JSON.stringify(source??null)}, not the recipe commit ${revision} clean; the recipe copy must be a clean Git work tree when the model is exported`);
      await each(name,target,revision);
    }
    return revision;
  }finally{
    await rm(dir,{recursive:true,force:true});
    await rm(out,{recursive:true,force:true});
  }
}

try{
  const args=process.argv.slice(2),options={'--python':'python3','--machinome':'machinome'},seen=new Set();
  for(let i=0;i<args.length;i+=2){
    if(!(args[i] in options)||seen.has(args[i])||!args[i+1])
      throw new Error('Usage: node scripts/pin-fixture-project.mjs [--python PYTHON] [--machinome MACHINOME]');
    seen.add(args[i]);options[args[i]]=args[i+1];
  }
  const python=options['--python'],machinome=options['--machinome'];
  const env={...process.env,PYTHONPATH:[join(root,'..','..','..'),process.env.PYTHONPATH].filter(Boolean).join(':')};
  const movie=(...rest)=>execFileSync(python,['-m','machinome.movie',...rest],{cwd:root,env,encoding:'utf8',stdio:['ignore','pipe','inherit']});

  const held=await exportsNow(),made=Object.keys(EXPORTS).sort();
  if(held.join()!==made.join())
    throw new Error(`The fixture project holds the exports ${held.join(', ')||'none'}; this script makes ${made.join(', ')}; add the model to EXPORTS with its options`);
  const now=await exportFromTheRecipe(machinome,async(name,made,revision)=>{
    const target=join(project,'export',name),before=await read(join(target,'manifest.json'));
    await rm(target,{recursive:true,force:true});
    await cp(made,target,{recursive:true});
    const after=await read(join(target,'manifest.json'));
    console.log(`Export ${name}: made from ${revision}, ${after===before?'manifest unchanged':'manifest changed'}, written to ${relative(root,target)}.`);
  });
  console.log(`Revision: ${now}, recorded by every export's source.`);

  const declared=new Set(movie('list',project).split('\n').filter(Boolean).map(line=>line.split('\t')[0]));
  const {documents}=JSON.parse(await readFile(join(fixtures,'manifest.json'),'utf8')),changed=[];
  for(const name of documents){
    const file=join(fixtures,'documents',`${name}.json`);
    if(!declared.has(name)){
      const pinned=JSON.parse(await read(file)??'{}').model?.sourceRevision;
      console.log(`Document ${name}: written by hand, not evaluated; its model.sourceRevision is ${pinned??'absent'}${pinned===now?'':', not the project\'s revision'}.`);
      continue;
    }
    const old=await read(file);
    movie('evaluate',project,name,'--out',file);
    if(await read(file)===old)console.log(`Document ${name}: unchanged.`);
    else{changed.push(name);console.log(`Document ${name}: changed, written to ${relative(root,file)}.`);}
  }
  if(changed.length)console.log(`Now run node scripts/pin-resolved.mjs ${changed.join(' ')} and review the pins before committing.`);
}catch(error){console.error(error.message);process.exitCode=1;}
