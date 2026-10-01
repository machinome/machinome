#!/usr/bin/env node
// Re-pins the fixture project after any of its files changed, in one command
// (fixtures/README.md, "The fixture project"): it makes the project's commit by
// the recipe, writes its hash to the source-revision.txt of every export of the
// project (export/<model>/, each holding a manifest.json), evaluates
// every document fixtures/manifest.json registers whose movie the project
// declares into fixtures/documents/, and prints what changed. It never writes
// fixtures/resolved/: a person runs scripts/pin-resolved.mjs for the documents
// that changed and reviews the pins before committing.
// Usage: node scripts/pin-fixture-project.mjs [--python PYTHON]
// PYTHON (default python3) runs the machinome_movie package of this
// repository's python/ directory and must have its dependencies installed.
import {cp,mkdtemp,readFile,readdir,rm,writeFile} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,dirname,relative,sep} from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const root=join(dirname(fileURLToPath(import.meta.url)),'..');
const project=join(root,'python','tests','fixtures','project'),fixtures=join(root,'fixtures');
// Every export of the project pins the one revision: each directory of
// export/ that holds a manifest.json.
async function pins(){
  const exports=join(project,'export'),found=[];
  for(const entry of (await readdir(exports,{withFileTypes:true})).sort((a,b)=>a.name<b.name?-1:1))
    if(entry.isDirectory()&&await read(join(exports,entry.name,'manifest.json'))!==null)
      found.push(join(exports,entry.name,'source-revision.txt'));
  return found;
}
// The recipe's identity, date and message, and no global or system Git
// configuration; nothing of the caller's Git environment is inherited.
const FIXED={GIT_AUTHOR_NAME:'Videomaker fixture',GIT_AUTHOR_EMAIL:'fixture@videomaker.invalid',
  GIT_AUTHOR_DATE:'2026-09-30T00:00:00+00:00',GIT_COMMITTER_NAME:'Videomaker fixture',
  GIT_COMMITTER_EMAIL:'fixture@videomaker.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00+00:00',
  GIT_CONFIG_GLOBAL:'/dev/null',GIT_CONFIG_NOSYSTEM:'1'};
const LEFT_OUT=new Set(['export','_build','__pycache__']);
const read=file=>readFile(file,'utf8').catch(error=>{if(error.code==='ENOENT')return null;throw error;});

// The commit of the project made by the recipe: every file but export/,
// _build/ and __pycache__/, in a fresh repository.
async function revision(){
  const dir=await mkdtemp(join(tmpdir(),'videomaker-fixture-project-'));
  try{
    await cp(project,dir,{recursive:true,filter:source=>!relative(project,source).split(sep).some(part=>LEFT_OUT.has(part))});
    const env={...Object.fromEntries(Object.entries(process.env).filter(([key])=>!key.startsWith('GIT_'))),...FIXED};
    const git=(...args)=>execFileSync('git',args,{cwd:dir,env,encoding:'utf8'}).trim();
    git('init','-q');git('add','-A');git('commit','-q','-m','Fixture project');
    return git('rev-parse','HEAD');
  }finally{await rm(dir,{recursive:true,force:true});}
}

try{
  const args=process.argv.slice(2),at=args.indexOf('--python');
  const python=at<0?'python3':args[at+1];
  if(!python||args.length!==(at<0?0:2))throw new Error('Usage: node scripts/pin-fixture-project.mjs [--python PYTHON]');
  const env={...process.env,PYTHONPATH:[join(root,'python'),process.env.PYTHONPATH].filter(Boolean).join(':')};
  const movie=(...rest)=>execFileSync(python,['-m','machinome_movie',...rest],{cwd:root,env,encoding:'utf8',stdio:['ignore','pipe','inherit']});

  const now=await revision();
  for(const pin of await pins()){
    const before=(await read(pin))?.trim()??null;
    if(before===now)console.log(`Revision: ${now}, unchanged in ${relative(root,pin)}.`);
    else{await writeFile(pin,now+'\n');console.log(`Revision: ${before??'none'} -> ${now}, written to ${relative(root,pin)}.`);}
  }

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
