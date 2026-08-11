## Context

The project workspace has one session-scoped filesystem observer, one
snapshot-first SSE connection, a mounted functional-model viewer, and a
persistent agent conversation. The observer already treats qualifying Python
filesystem changes identically regardless of whether an agent, terminal, or
other author produced them. The browser has no source API and the accepted
artifact-boundary decision currently forbids serving project Python.

The Code area crosses the browser, filesystem, build, broker, orchestrator, and
backend seams. It must tolerate concurrent maker and agent edits without
instrumenting agent tools, and it must not turn an informational save notice
into an agent wake-up.

## Goals / Non-Goals

**Goals:**

- Make Code the second workspace area, with one Git-visible project navigator
  and a Monaco multi-model editor.
- Give maker saves and agent writes one filesystem event and build path.
- Refresh clean buffers automatically while preserving dirty work and rejecting
  stale saves.
- Inform agents that owned active broker work at save time before their next
  ordinary action, without changing work state or waking them solely for the
  notice.
- Preserve the mounted chat, editor models, and model view state across area
  changes.
- Keep project source inert in Floor and keep published artifacts as the only
  functional-model input.

**Non-Goals:**

- Maker create, rename, delete, Git, terminal, debugging, language-server, or
  collaborative cursor controls.
- Attribution of an observed external write to a particular agent.
- Building non-Python files that the current source watcher does not consider
  model source.
- Persisting open tabs, dirty buffers, or notice queues across a service or page
  restart.
- Executing, importing, parsing, or interpreting project Python in Floor.

## Decisions

### Discover source through Git and validate every operation at the project boundary

The server runs Git in the verified project root to enumerate tracked files plus
untracked files surviving standard ignore rules. It synthesizes directory rows
from those file paths. `.git`, `_build`, and build-staging families are excluded
even if a malformed repository exposes them. An agent-created untracked file
therefore appears as soon as Git considers it visible, while ignored files and
ignored-only directories never appear.

List results carry relative POSIX paths and a file/directory kind. Read and save
resolve the requested path beneath the verified project root, reject symlinks
and non-regular files, confirm the file remains in the Git-visible set, and
never follow a path outside the repository. Reads accept bounded UTF-8 text;
non-text or oversized files remain visible but report that they are not
editable. This uses Git's own ignore semantics rather than duplicating
`.gitignore` parsing.

Alternative: recursively walk and apply pattern matching in Python. Rejected
because Git ignore precedence and negation are easy to reproduce incorrectly.

### Use content revisions and atomic compare-and-save

A readable file response includes a SHA-256 revision of its bytes. Save accepts
the maker's content and expected revision under a per-session async lock,
re-reads the current revision, and returns a conflict without writing when they
differ. An accepted save writes a same-directory temporary file, preserves the
existing mode, flushes it, and atomically replaces the original. The response
returns the installed revision.

The save endpoint does not invoke `solid build`. Its atomic replace is observed
by the same source watcher as an agent write, so qualifying Python saves settle
and coalesce under the existing build policy.

Alternative: save and call the build command directly. Rejected because it
creates a second build path and can duplicate the watcher build.

### Publish source invalidations, not source content

The session's existing recursive observer gains a source-event publisher for
created, modified, moved, and deleted files outside excluded trees. Events name
the affected relative path, operation, and previous path for a move; they do
not claim an author and do not carry file content. The browser re-lists the
Git-visible tree and re-reads affected open files through the safe API. On SSE
connect or reconnect it performs the same reconciliation for the tree and open
files, so source events need not become durable broker snapshot content.

An event received while the browser's own save is in flight is deferred until
the save response supplies the installed revision. A clean buffer accepts a
new external revision and updates its Monaco model. A dirty buffer retains its
text and records the external revision/content as a conflict. Saving a stale
buffer remains prohibited until the maker reloads the external value; the first
increment offers reload rather than merge or force-overwrite.

### Use Monaco path models and preserve the owning React components

The frontend uses locally bundled `@monaco-editor/react` and `monaco-editor`.
Each relative project path is the wrapper's `path`, producing one Monaco model
with its own undo history and view state. External clean-buffer replacement uses
the model edit API under a change guard instead of recreating the model. The
Code and Model center panes change visibility inside one workspace component;
the conversation remains outside that switch and the model viewer remains
mounted. Open file state lives at workspace scope.

The first increment opens one or more file tabs, saves with Ctrl/Cmd+S, marks
dirty/conflicted tabs, and lets the maker reload a conflict. It does not label
external lines with an agent identity because filesystem evidence cannot prove
one.

### Queue trusted notices for the broker-active recipient set

After an accepted maker save, the session snapshots the broker roles whose
work state is `active`. It queues one trusted `user_file_changed` notice per
recipient and path, coalescing a later unsent revision of the same path. The
notice contains path and installed revision, is not a conversation entry or
user direction, and never changes assignment or direct-work state.

The portable backend seam gains a steer-only notice operation. It may inject a
notice into the currently active delivery and report acceptance, but it MUST
NOT start a delivery. Codex and OpenCode translate a missing/completed turn to
not accepted; Claude consults its outstanding delivery record and writes only
when that exact delivery remains outstanding. A completion race leaves the
notice queued.

Before the orchestrator sends that role's next ordinary broker envelope, it
prepends all retained notices in recorded order and removes them only after the
ordinary delivery is accepted. Thus an agent active at save time is guaranteed
the notice in its continuing turn or next ordinary turn, while the notice alone
never wakes a role. Closing the ephemeral session discards undelivered notices.

Alternative: reuse ordinary direction delivery. Rejected because its portable
contract deliberately starts a new turn after a completion race and user
direction cannot address every profile role.

### Amend, rather than weaken, the artifact boundary

A new ADR amends ADR 0004 only where it forbids serving source. Floor may list,
read, and atomically replace verified project text as an editor service. It
still does not import, interpret, or execute source, and the browser Model area
still reads only the framework's published `_build` artifacts. The architecture
overview is rewritten to describe both explicit boundaries.

## Risks / Trade-offs

- **Git enumeration on a burst of filesystem events can be noisy.** → Coalesce
  browser tree reconciliation and keep source contents out of SSE; local project
  repositories are the intended scale.
- **Atomic replacement may emit several platform events.** → Treat events as
  invalidations and deduplicate browser refresh work by path; retain the model
  watcher's existing build settle/coalescing behavior.
- **An ignored status can change when `.gitignore` changes.** → Re-list the
  complete Git-visible tree for every structural invalidation and reconnect.
- **A clean-buffer external update enters Monaco undo history.** → Apply it as a
  guarded model edit so view state survives; the explicit reload action is the
  only operation that discards a dirty local buffer.
- **A notice can be retained indefinitely when no further work reaches a role.**
  → This is intentional: guaranteeing immediate delivery would wake the role;
  session close bounds retention.
- **Monaco increases the frontend bundle.** → Bundle it locally so the IDE has
  no CDN/network dependency and validate the production asset build.

## Migration Plan

1. Add red backend tests for source discovery, unsafe paths, revision conflicts,
   source invalidations, and retained notice delivery.
2. Implement the source service, watcher publication, and portable steer-only
   notice seam while the existing Model-only browser remains functional.
3. Add Monaco and the interactive Code area, then add browser acceptance for
   editing, external refresh, conflicts, tree changes, and persistent chat/model
   state.
4. Add the ADR, update the architecture and design references, sync baseline
   specs, rebuild checked-in frontend assets, and archive the change.

Rollback removes the Code controls and source routes first; the additive source
event and notice state can then be removed without altering the established
model artifact/build path.

## Open Questions

None. The pilot ratified the browse/open/edit/save first increment, Git-visible
tree policy, conflict behavior, active-recipient retention, and lack of
maker-side create/rename/delete controls.
