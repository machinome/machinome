# PRD: The model changes as it is made

**Sprint:** SPRINT-003
**Status:** Draft, awaiting pilot ratification
**Date:** 2026-08-02

This document is the source for SPRINT-003. Every story, cycle, OpenSpec
proposal, architecture record, and acceptance test in this sprint derives from
it. Where an implementation disagrees with this document, this document is
wrong or the implementation is — resolve it here first.

---

## 1. Outcome

The maker watches a model take shape. A part that finishes rebuilding appears;
the rest of the model stays where it is, and so does the camera. Nothing
reloads, nothing flashes, nothing goes stale, and the view never wedges.

This holds no matter who caused the change — an agent, the maker's own editor,
a terminal, or several at once.

## 2. Why now

The floor's model refresh is broken today, and the previous attempt to fix it
failed three times in a row while never touching the defect. That is a signal
about the architecture, not about the implementer.

### 2.1 The reported failure

A change to project source does not refresh the browser. Measured cause, in two
independent defects that compound:

**Defect A — one failed fetch kills the viewer permanently.**
`floor/frontend/src/main.tsx` renders either the viewer host or an error, never
both. When a fetch fails, `setError` unmounts the host `<div>`, so
`container.current` becomes `null`; the effect's `if (!target) return;` guard
then fires before `setError(null)` on every subsequent change. Proven: after
three successful rebuilds the page still displayed
`Failed to load /artifacts/viewer.json?generation=0` — still generation 0, so no
remount was ever attempted. Only a manual page reload recovers.

**Defect B — the artifact route manufactures the fetch failure.**
`floor/app.py` resolves the `_build` symlink three separate times in one
request and compares the results. A publication landing between those
resolutions leaves `candidate` in the old publication while `build_root.resolve()`
names the new one, so containment fails and the route returns 404. Measured
during an ordinary single-builder rebuild: `viewer.json` 200, its STL 404 in
the same instant. No agent race required.

A + B: one rebuild, one unlucky instant, and the model never updates again for
the rest of the session.

### 2.2 Why the previous attempt could not converge

All three fix commits on `make-shop-floor-event-driven` edited
`floor/watcher.py`. Neither defect is in `watcher.py`. The event source works
correctly and always did — verified live on the SSE stream:

```
model_build_succeeded  {"trigger": "root/__init__.py", "duration_seconds": 3.36}
model_changed          {"trigger": "root/__init__.py"}
```

Its e2e test is honest but blind: a control run with a no-op edit confirmed the
assertion does not fire without a real change, so it is not a false positive —
it simply never exercises a failed fetch, which is the only thing that breaks.

### 2.3 Why a repair is not enough

Fixing A and B restores the current behaviour, which is a full teardown and
reload of the entire model on every change. Measured on `projects/v8-engine`:

| Quantity | Measured |
|---|---|
| Published artifacts | 113 MB across 55 STLs |
| Largest single mesh | 32 MB |
| `viewer.json` | 13 KB |
| Nodes / distinct mtimes | 46 / 7 |
| Rebuild latency (trivial project) | ~3.4 s |

Every change refetches 113 MB, re-parses 55 meshes and re-uploads all of them,
to show a difference that usually touches one leaf. The cost is not bandwidth —
this is localhost — it is mesh parsing and GPU upload, and it is why the view
visibly stalls.

## 3. Target architecture

One sentence: **a build writes each artifact atomically into a single
directory, the floor forwards each completed artifact as an event, and the
viewer updates only what the event named.**

### 3.1 Building

A single `_build` directory. No symlink, no versioned publications, no staging
copy. Every artifact is written to a temporary name in the same directory and
`os.replace`d into place, so a reader observes an artifact complete or not at
all, and a reader that has already opened one keeps reading it to completion.

Concurrent builders — the floor, `machinome test`, `machinome develop`, several agents —
serialise on a build lock held in the project. A builder that acquires the lock
and finds the current publication already covers its triggering change skips
building and trusts the result.

### 3.2 Ordering

The manifest is the only thing that makes an artifact reachable. Therefore:
write the artifact, then the pointer; remove the pointer, then the artifact.
Concretely — new STLs first and `viewer.json` last; on removal `viewer.json`
first and the sweep after. This is already what the builder does for additions
(`builder.py:173` writes the snapshot after rendering completes); the removal
half is new, because dropping a whole publication used to handle it implicitly.

### 3.3 Watching and forwarding

The floor runs two watchers with distinct jobs:

- **source → build trigger.** A project source change makes the floor build.
- **build output → event.** A completed artifact makes the floor emit SSE.

The floor is a pipe. It forwards content events only, carrying the artifact
path and nothing else. It does not diff, does not inspect artifacts, and does
not forward deletions.

### 3.4 Updating

The viewer holds the manifest, so it maps an artifact path back to the nodes
referencing it and reloads only those meshes. A manifest change refetches 13 KB
and reconciles the tree, fetching geometry for nodes it has not seen. Geometry
is refetched only when its bytes changed; a placement, colour or animation edit
costs no fetch at all.

## 4. Decisions

Each decision records what was rejected and why, so a later reader does not
reopen settled ground.

**D1 — Single build directory with per-artifact atomicity, replacing set
atomicity.**
Rejected: keeping the symlink swap. It exists to make racing publishers settle
and to give readers a complete set; the lock (D2) covers the first, and
per-artifact rename covers torn reads without needing the second. Set atomicity
also actively prevents the outcome this sprint wants — parts appearing as they
finish rather than a stall and a jump.

**D2 — Build mutual exclusion via `flock` on a file in the project.**
Rejected: a broker, daemon, or WebSocket lock. The framework had one and
removed it deliberately as a platform feature. `flock` adds no protocol and no
process, and the kernel releases it on death, so there is no stale-lock reaping.
Dedup rule: if the publication already covers the acquirer's triggering change,
skip. The lock covers the build only — `machinome test` releases before running
tests, so a long sweep never blocks the maker's refresh.

**D3 — The event names the artifact; no diff on the wire.**
Rejected: publication generations with a server-computed diff. Only the browser
knows what it currently holds, so a server diff would require per-client state,
a baseline negotiation, and a resync path. A file-granular event makes all three
disappear. The manifest is 13 KB; there is nothing to save by diffing it.

**D4 — Deletions are not forwarded.**
The manifest is authoritative for existence and, by D3's ordering, always
changes first, so a deletion event carries no information. Forwarding one
invites `artifactChanged` to fetch a path that no longer exists — regenerating
Defect A's failed fetch from a routine node removal. Not forwarding leaves
`artifactChanged` with exactly one meaning: these bytes changed.

**D5 — The viewer owns the targeted update.**
Rejected: the shop computing the update and driving fine-grained widget
mutations. The manifest, `mtime` and `operations` are the framework's data
model, and `machinome develop` needs the identical behaviour — it reloads coarsely
today. One implementation upstream serves both consumers and shrinks the shop.

**D6 — Geometry staleness is keyed on `(model path, mtime)` together.**
A touched-but-unedited source causes a harmless spurious refetch. The reverse
matters more: builds are parameter-keyed, so a parameter change can move the
`model` path without moving the source mtime. Either key alone misses a case.

**D7 — `errors.json` is cleared on every successful build.**
With the staging copy gone, nothing carries or clears it implicitly any more.

**D8 — A partial model is a legitimate observable state.**
It follows from D1. The maker must be able to tell an arriving model from a
settled one, and a failed build now leaves a partially updated model rather
than the previous complete one — a change from the guarantee the framework
documents today.

## 5. Architecture records

Three, in the repositories and subsystems that own the decisions.

**machinome, BUILD — per-file atomic publication and build mutual exclusion.**
Covers D1 and D2 as one decision, because their correctness is joint: a single
directory is safe only given rename-based writes and a lock, and splitting them
would let one land without the other, which is the corrupting case.

It must argue two things head-on rather than by implication:

- It **reverses ADR-030**, which did not merely establish the publication
  boundary but explicitly rejected rendering into the public build directory
  because "readers can observe a mixed artifact set while a build is in
  progress." ADR-030 conflated *complete set* with *no torn reads*.
  Per-artifact rename delivers the second without the first, and the mixed set
  it feared is the progressive update this sprint wants.
- It **does not regress ADR-018**, which superseded the framework's
  WebSocket global lock (ADR-017) as platform bloat. `flock` on a project file
  adds no daemon, no protocol and no platform surface.

It supersedes ADR-032, whose own origin line records that the shop drove it by
measurement — the same path this sprint takes.

**machinome, VIEWER-WEB — targeted artifact update in the viewer widget.**
Covers D5 and D6. A separate record because the framework files ADRs by
subsystem, because `machinome develop` consumes it independently of any shop
concern, and because a shop record cannot decide a framework interface.

**machinome-studio — the floor's model event pipeline.**
Covers D3, D4 and D8. Amends ADR-0010, which settled that the shop watches and
rebuilds rather than asking an agent to: that holds, but the *event source*
moves from the floor's own build completion to observed build output, so a
change published by anyone reaches the browser. Reaffirms ADR-0004's artifact
boundary unchanged — the floor still never imports, executes or serves project
Python.

## 6. Cycles

| ID | Repository | Change | Requires |
|---|---|---|---|
| F1 | `machinome` | `build-mutual-exclusion` | none |
| F2 | `machinome` | `per-file-build-publication` | F1 |
| F3 | `machinome` | `viewer-targeted-update` | none |
| S1 | `machinome-studio` | `floor-artifact-event-pipeline` | F2 |
| S2 | `machinome-studio` | `floor-in-place-model-updates` | F3, S1 |

F1 before F2 is not a preference. Under set-atomic publication a race caused a
lost update; under a single directory two builders write the same files and
interleave, so the race becomes corrupting. F3 is independent of the build work
and may run in parallel.

S2 is where Defects A and B are finally answered: B dissolves when there is no
symlink to re-resolve, and A is fixed by construction when the viewer host stops
being unmounted on error.

## 7. Acceptance

The sprint is done when each of these passes for the right reason. The previous
attempt shipped a test that passed while the product was broken; every criterion
below is written so that it cannot.

1. **One edit, one artifact event.** Editing a single leaf of `v8-engine`
   produces exactly one artifact event, not 55.
2. **The canvas survives.** The viewer's DOM node identity is preserved across
   a model change. This is the only assertion that distinguishes in-place update
   from reload.
3. **A failed fetch is recoverable.** Induce an artifact fetch failure; the
   viewer recovers on the next publication with no page reload.
4. **The newest source wins.** Race two builds with a stale one finishing last;
   the published model matches the newest source.
5. **A concurrent reader is not torn.** `machinome test` reading artifacts while
   another builder republishes them completes against consistent data.
6. **Placement costs nothing.** An operations-only or colour-only edit produces
   no geometry refetch.
7. **A deletion does not fetch.** Removing a node updates the model with no
   request for the removed artifact.
8. **No regression in the boundary.** The floor still imports, executes and
   serves no project Python.

## 8. Out of scope

- Content-addressing artifact filenames. A single directory plus per-node
  staleness keys removes the need; revisit only if D6 proves insufficient.
- Any change to what the viewer can render. This sprint changes when and how
  much it updates, not what a model looks like.
- Remote or multi-client floors. The shop is local and attended; the
  architecture deliberately optimises for one browser.
- Retiring `machinome develop`. It becomes a lock participant, nothing more.
- The shop workspace redesign already on `main`.

## 9. Risks

- **R1 — ADR-030 reversal is contested.** The strongest objection is that a
  failed build now leaves a partially updated model where it previously left the
  last complete one. D8 accepts this; if it proves unacceptable in use, the
  fallback is a build-in-progress signal, not a return to set atomicity.
- **R2 — `errors.json` behaviour is assumed, not verified.** It is written into
  the published build directory, and the staging copy that may have carried it
  forward is being removed. F2 must prove its lifecycle rather than inherit it.
- **R3 — Most of the sprint is upstream.** Four of five cycles' risk sits in
  `machinome`, and framework integration needs explicit pilot authority that
  sprint membership does not grant.
- **R4 — The superseded worktree.** `make-shop-floor-event-driven` describes a
  source-watching, floor-building, full-reload design this PRD rejects. Its
  diagnosis is preserved in section 2; its specs are not carried forward.
