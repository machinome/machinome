// The Git work trees a film's records name a head of (the honest-provenance
// change, ADR-015): the project repository and Videomaker's own checkout.
// A tree is dirty when Git lists anything for it: a tracked file changed,
// staged or not, or an untracked path it does not ignore. The callers pass
// the directories; this module locates nothing.
//
//   treeState(cwd)          -> {head, dirty, changes: [path as Git prints it]}
//   treeLine(tree, state, command)    the report line check, preview and render print
//   treeReleaseIssue(tree, state)     the manifest's releaseIssues entry, or null
//
// `tree` is 'project' or 'workflow' (the field names' prefix); `command` is
// 'check', 'preview' or 'render'.
import {command} from './util.mjs';

const SUBJECT={project:'Project tree',workflow:'Videomaker tree'};
const short=head=>head.slice(0,12);

export async function treeState(cwd){
  const head=(await command('git',['rev-parse','HEAD'],{cwd})).trim();
  // No optional locks: reading the state never writes the index of a tree
  // another process may be using.
  const status=await command('git',['--no-optional-locks','status','--porcelain=v1','--untracked-files=normal'],{cwd});
  const changes=status.split('\n').filter(Boolean).map(line=>line.slice(3));
  return {head,dirty:changes.length>0,changes};
}

// "3 paths differ from <what> <head> (a, b, c and 2 more)"
function differ(state,what){
  const n=state.changes.length,named=state.changes.slice(0,3).join(', ');
  return `${n} ${n===1?'path differs':'paths differ'} from ${what} ${short(state.head)} (${named}${n>3?` and ${n-3} more`:''})`;
}

const CONSEQUENCE={
  check:{project:'a render now records a head that is not the content rendered and is not release-ready',
    workflow:'a render now records a head that is not the tool that rendered and is not release-ready'},
  preview:{project:'the preview\'s projectHead is not the content previewed',
    workflow:'the preview\'s workflowHead is not the tool that previewed'},
  render:{project:'the manifest\'s projectHead is not the content rendered, and the film is not release-ready',
    workflow:'the manifest\'s workflowHead is not the tool that rendered, and the film is not release-ready'},
};

export function treeLine(tree,state,commandName){
  if(!state.dirty)return `${SUBJECT[tree]}: clean at ${short(state.head)}`;
  return `${SUBJECT[tree]}: dirty at ${commandName}, ${differ(state,'its head')}; ${CONSEQUENCE[commandName][tree]}`;
}

export function treeReleaseIssue(tree,state){
  if(!state.dirty)return null;
  return `${tree==='project'?'project tree':SUBJECT[tree]} dirty at render: ${differ(state,`${tree}Head`)}`;
}
