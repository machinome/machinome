# ADR 0021: Serve verified project source as inert editable text

**Status:** Accepted

**Date:** 2026-08-11

**Deciders:** Pilot

**Amends:** [ADR 0004](./0004-static-build-artifact-boundary-for-functional-model-inspection.md)

## Context

The workspace already presents a project's published functional model and its
persistent agent conversation, but the maker cannot inspect or edit the source
that produces that model. ADR 0004 deliberately prohibited Floor from serving
project Python so the Model path could not accidentally import, execute, or
depend on live module state. A source editor needs a narrower boundary that
preserves that safety property while allowing inert text access.

Maker and agent edits also occur concurrently. The editor must not overwrite a
newer agent change, duplicate the existing filesystem-triggered build path, or
claim that an observed filesystem event identifies its author. An agent active
when the maker saves needs to learn about that edit without the notice itself
waking the agent or becoming a user direction.

## Decision

Floor may enumerate, read, and atomically replace verified project source as
inert text for the Code workspace. The source working set is exactly the files
Git reports as tracked or non-ignored untracked files, excluding `.git`, build
output, and build staging. Every operation remains rooted in the verified
project repository, rejects symlinks and non-regular files, and bounds editable
UTF-8 content.

Reads return a content revision. A save compares that revision under a
session-scoped lock and rejects stale content instead of overwriting it. An
accepted save atomically replaces the existing file and relies on the same
filesystem watcher and build policy as any agent or terminal write; the save
route never invokes a build directly.

Source filesystem events are project-scoped invalidations, not content or
attribution. The browser re-lists and re-reads through the safe source API.
Clean buffers accept external revisions, while dirty buffers retain the
maker's text and enter an explicit conflict state.

After an accepted maker save, active broker roles receive a trusted
`user_file_changed` notice containing the path and installed revision. The
notice is neither conversation nor direction, never changes work state, and
must not start a turn. If it cannot be injected into the current delivery, it
is retained and prepended to that role's next ordinary delivery.

ADR 0004's functional-model boundary otherwise remains unchanged. Floor never
imports, interprets, or executes project source, and the Model workspace still
consumes only complete framework-published `_build` artifacts.

## Alternatives considered

- Recursively walk the project and reproduce Git ignore matching in Floor.
  Rejected because ignore precedence and negation would create a second,
  divergent definition of the project working set.
- Invoke `solid build` directly from the save route. Rejected because this
  would create a second build path and could duplicate watcher-triggered builds.
- Deliver the file notice as ordinary user direction. Rejected because ordinary
  delivery may start a turn after a completion race and cannot safely address
  every active role without changing messaging semantics.
- Force-overwrite or merge stale buffers in the first increment. Rejected in
  favor of an explicit reload choice that preserves both versions without
  pretending to perform a correct merge.

## Consequences

### Positive

- Makers can inspect and edit the same Git-visible source agents modify.
- Agent-created, non-ignored untracked files appear without instrumenting agent
  tools.
- Revision checks and conflict state prevent silent concurrent overwrite.
- Maker and agent Python writes share one watcher, debounce, and build path.
- Active agents are guaranteed eventual notice without being woken solely for
  that notice.

### Negative / trade-offs

- Git enumeration runs during structural invalidation and can be noisy in a
  burst, though projects are local and source content stays out of SSE.
- Monaco materially increases the locally bundled frontend assets.
- A notice can remain queued indefinitely if no later ordinary delivery reaches
  its role; session close bounds that retention.
- The first increment offers reload rather than merge or force-save for dirty
  conflicts.

### Neutral

- Binary, oversized, ignored, build, unsafe, and symlinked paths may appear in
  the filesystem but are not editable through Floor.
- Source invalidations deliberately carry no actor identity.
- Source tabs, dirty buffers, and queued notices remain session/page state and
  are not persisted across restart.
