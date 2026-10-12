// Throwaway checkouts for the speech key's lookup, in the shapes a
// Videomaker checkout can have: a plain directory (no Git), a primary work
// tree, another work tree of the same repository, and a copy inside some
// other repository's work tree. Not a test file: it
// registers no tests. The layouts live under the system's temporary directory,
// outside every repository, so no lookup in them can reach a real `.env`.
//
//   const {checkout,primary}=await keyLayout(t,'worktree');
//   // checkout: <root>/primary/WTs/wt, primary: <root>/primary
import {mkdtemp,mkdir,rm,realpath} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync} from 'node:child_process';

const FIXED={GIT_AUTHOR_NAME:'Videomaker fixture',GIT_AUTHOR_EMAIL:'fixture@videomaker.invalid',
  GIT_AUTHOR_DATE:'2026-09-30T00:00:00+00:00',GIT_COMMITTER_NAME:'Videomaker fixture',
  GIT_COMMITTER_EMAIL:'fixture@videomaker.invalid',GIT_COMMITTER_DATE:'2026-09-30T00:00:00+00:00',
  GIT_CONFIG_GLOBAL:'/dev/null',GIT_CONFIG_NOSYSTEM:'1'};

// A key no provider would accept, so a leak could never spend anything.
export const FAKE_KEY='fake-key-for-tests-never-valid';

export async function keyLayout(t,kind){
  const root=await realpath(await mkdtemp(join(tmpdir(),'videomaker-key-')));
  t?.onTestFinished(()=>rm(root,{recursive:true,force:true}));
  const git=(cwd,...args)=>execFileSync('git',args,{cwd,env:{...process.env,...FIXED},encoding:'utf8',stdio:['ignore','pipe','pipe']});
  if(kind==='plain'){const checkout=join(root,'plain');await mkdir(checkout);return {root,checkout};}
  const primary=join(root,'primary');await mkdir(primary);
  git(primary,'init','-q');git(primary,'commit','-q','--allow-empty','-m','fixture');
  if(kind==='primary')return {root,checkout:primary,primary};
  // A copy of the tool inside another project's repository, not a checkout of its own.
  if(kind==='inside'){const checkout=join(primary,'vendor','videomaker');await mkdir(checkout,{recursive:true});return {root,checkout,primary};}
  if(kind!=='worktree')throw new Error('Unknown key layout: '+kind);
  const checkout=join(primary,'WTs','wt');
  git(primary,'worktree','add','-q','-b','wt',checkout);
  return {root,checkout,primary};
}
