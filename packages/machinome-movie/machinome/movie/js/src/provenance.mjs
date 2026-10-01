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
//
// The third revision a film's records name is the one the model's export was
// made from, which the framework records in the export's manifest as
// `source: {revision, dirty}` (the read-the-exports-source change, ADR-019):
//
//   exportSource(manifest, manifestPath)         -> {revision, dirty}, or a refusal by name
//   pinnedRevision(declared, source, manifestPath)  refuses a model.sourceRevision that differs
//   exportLine(source, command)                  the Export: line after the tree lines
//   exportReleaseIssue(source)                   the manifest's releaseIssues entry, or null
//   exportProvenance(source)                     {exportRevision, exportDirty}
//   withoutSource(manifest)                      the manifest as the shot cache keys it
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

// A full object name as `git rev-parse` prints it: SHA-1 or SHA-256.
const FULL_HASH=/^(?:[0-9a-f]{40}|[0-9a-f]{64})$/;

// The revision the export records it was made from. Nothing beside the
// manifest is read for it, and nothing falls back to a sidecar: an export
// whose manifest has no source was made before the framework recorded it,
// or outside Git, and is exported again.
export function exportSource(manifest,manifestPath){
  const source=manifest?.source,named=`The export ${manifestPath}`;
  if(source===undefined)throw new Error(`${named} records no source, the revision it was made from (manifest field source.revision); export the model again with a machinome that records it, from the project's Git repository with a commit: a project outside Git cannot be filmed with a pinned revision`);
  if(!source||typeof source!=='object'||Array.isArray(source))throw new Error(`${named} records source ${JSON.stringify(source)}, which is not a record of a revision; export the model again`);
  if(typeof source.revision!=='string'||!FULL_HASH.test(source.revision))
    throw new Error(`${named} records source.revision ${JSON.stringify(source.revision)}, which is not a full commit hash; export the model again`);
  if(typeof source.dirty!=='boolean')
    throw new Error(`${named} records source.dirty ${JSON.stringify(source.dirty)}, which is not true or false; export the model again`);
  return {revision:source.revision,dirty:source.dirty};
}

// A film is pinned to the revision its export was made from; both are named
// in full, since a prefix can make two revisions look equal.
export function pinnedRevision(declared,source,manifestPath){
  if(declared===source.revision)return;
  throw new Error(`model.sourceRevision is ${declared??'null'}, and the export ${manifestPath} was made from source.revision ${source.revision}; pin the revision the export records (evaluate a movie again), or export the model again from ${declared??'the revision the film pins'}`);
}

const EXPORT_CONSEQUENCE={
  check:'a render now records an export that is not that revision and is not release-ready',
  preview:'the preview\'s exportRevision is not the content exported',
  render:'the manifest\'s exportRevision is not the content exported, and the film is not release-ready',
};

// "Export: made from <revision>, clean", or dirty and what that means for the
// command's record. The framework records whether Git listed anything, not
// what, so the line names no path.
export function exportLine(source,commandName){
  if(!source.dirty)return `Export: made from ${short(source.revision)}, clean`;
  return `Export: made from ${short(source.revision)}, dirty: Git listed changes in the project when the model was exported; ${EXPORT_CONSEQUENCE[commandName]}`;
}

export function exportReleaseIssue(source){
  if(!source.dirty)return null;
  return `export dirty when made: exportRevision ${short(source.revision)} is not the content exported; export the model again from a clean tree`;
}

export const exportProvenance=source=>({exportRevision:source.revision,exportDirty:source.dirty});

// The manifest as the shot cache's common key reads it: the export's source
// record is provenance, never a picture input (the viewer ignores it), so an
// export made again from another commit, or with other dirt, keeps the key.
export function withoutSource(manifest){
  const {source,...rest}=manifest;
  return rest;
}
