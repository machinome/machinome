## Context

`floor/watcher.py` today is one object doing two jobs. It fingerprints the
project's `*.py` sources, runs `solid build root` when they settle, and then —
inside the same method, from the same subprocess's exit — hashes
`_build/viewer.json` and publishes `model_changed` if the hash moved. That
coupling is why only a build the floor itself ran can ever reach the browser,
and why the only thing the browser can be told is "everything is different".

Framework `sprint-003` @ `582da89` (F2) changed the ground underneath it:

- `_build` is a real directory, not a symlink to a versioned sibling. The
  `_build.*` and `.solid-node-build-*` families the watcher excludes no longer
  exist.
- Each artifact is `os.replace`d into place from a temporary sibling created by
  `mkstemp` in the artifact's own directory. A reader observing the final name
  observes a complete file, and a reader holding one open reads it to
  completion. **Publication is a rename**, and both ends of that rename are
  inside the build directory.
- `viewer.json` is written last and republished whenever it no longer matches
  the model, so the manifest is reliably the final publication of a build.
- `errors.json` is written into the same directory on failure, by the same
  atomic path, and removed immediately before the manifest is republished.

`floor/app.py`'s artifact route resolves `build_root` twice per request and
compares against a separately resolved candidate. That was written to survive
a symlink being repointed mid-request; with no symlink it can only produce
false negatives.

## Goals / Non-Goals

**Goals:**

- One event per completed artifact, naming the artifact and nothing else.
- Events for publications the shop did not run.
- No spurious 404 from the artifact route under concurrent republication.
- The floor still never imports, executes, or serves project Python (ADR 0004).

**Non-Goals:**

- Any change to how the model is rendered or updated in the browser. S2 owns
  that; S1 retargets the existing reload and banner onto the new events without
  changing what either does.
- Any remaining sampling loop in the shop outside the model pipeline.
- Diffing, generations, per-client state, or any resync protocol (PRD D3).
- Deciding what a published file means. The floor forwards; the browser
  interprets.

## Decisions

**Two watcher objects, both owned by the app lifespan.** `ModelWatcher` keeps
the source→build job and loses everything after the subprocess exits;
a new `ArtifactWatcher` owns build output→event. They share no state and
neither calls the other: the source watcher does not tell the artifact watcher
that a build finished, because a build the shop did not run must produce
identical behaviour. Both live in the lifespan for ADR 0010's reason — what
they refresh is this app's own artifact route, and this app publishes the
events. An app built without a solid command still runs no source watcher; it
may still run the artifact watcher, since observing a directory spawns no
subprocess.

*Alternative rejected:* one watcher with two loops. It preserves exactly the
coupling that produced the defect, and makes "whoever published it" a special
case rather than the only case.

**Nothing is polled. Both watchers are filesystem event handlers.** The floor
runs one `watchdog` `Observer` with two handlers scheduled on it — the project
root for source, `_build` for output. No fingerprint dictionaries, no
`(mtime_ns, size)` diffing, no hashing, no seeding from disk, no interval. This
amends ADR 0010, which chose a 0.5 s poll on the grounds that `watchdog` "adds a
runtime dependency to a harness that has two". That ground is gone: the floor
runs only where solid-node is installed, solid-node depends on `watchdog`, and
its own builder is a `FileSystemEventHandler`. This machine allows 524 288
inotify watches against a project of tens of files.

**A publication is a rename, so the floor listens for renames and nothing
else.** F2 publishes every artifact by `os.replace` from a temporary sibling in
the same directory. inotify pairs that into one `FileMovedEvent` whose
`dest_path` names the artifact that just became reachable — exactly once, after
it is complete. The floor forwards that path.

This deletes the in-flight exclusion problem rather than solving it. A temporary
being written produces create and modify events, never a move, so it is not
forwarded — not because the floor recognises `.tmp`, but because it was never
published. No filename taxonomy survives in the design: no `.tmp`, no `.scad`,
no `.stl.lock`, no `errors.json` case. The floor's rule and F2's publication
protocol are now the same sentence.

Deletions need no code either. A removal is a delete event, which is not a move,
so D4 holds by construction rather than by a rule someone has to remember.

*Alternative rejected:* a fingerprint diff over `_build`. It reconstructs by
`(mtime_ns, size)` heuristic what the kernel reports directly, cannot tell a
publication from a touch, needs seeding at startup so an already-validated build
does not announce all 55 artifacts at once, and needs a filename taxonomy to
suppress in-flight temporaries. Each of those is a symptom of asking the
filesystem the wrong question.

**Source changes are events with a settle timer, not stable samples.** The
source handler reacts to any event on a `*.py` path under the project root
outside `_build` and (re)schedules a single settle timer; the build runs when
that timer fires with no further event. One mechanism covers both things the
poll's two-consecutive-samples rule covered: an editor writing in place keeps
producing events and keeps pushing the timer out, and a multi-file save
coalesces into one build. The timer is scheduled once per burst and cancelled by
the next event — it samples nothing.

**Build output needs no settle timer.** The move is itself the completion
signal. Waiting after it would add latency to every event and could only ever
report the same path again.

**A failed build is reported by forwarding `errors.json`, not by a second
channel.** F2 writes `errors.json` into the build output on failure and removes
it before republishing the manifest on success. That file is published build
output, so the floor forwards it exactly like a mesh, and a failure therefore
reaches the browser whoever caused it — the shop's build, `solid develop`, an
agent, a terminal. `model_build_failed` and `model_build_succeeded`, which
derive a model verdict from the floor's own subprocess exit, are removed: they
are a privileged report of a fact the floor can observe, available only for
builds the floor happened to run, which is the same exception `model_changed`
was.

What survives from the subprocess is narrower and genuinely the shop's own:
the build command could not be run at all. That produces no build output for
anyone to observe, so it is reported as `model_build_unavailable` and says
nothing about the model.

**The failure clears by the manifest event, not by a deletion.** `clear_errors`
removes the file, and D4 does not forward removals. It does not need to: F2
clears `errors.json` immediately before republishing `viewer.json`, so a
manifest event always follows the withdrawal of a failure. The browser drops a
displayed error when it takes a new manifest — which is the honest rule anyway,
since a new manifest *is* the evidence that a build succeeded. This keeps D4
without an exception for the one file the manifest does not name.

*Known edge, in F2 rather than here:* a build that fixes a transient failure but
produces a byte-identical manifest returns before `clear_errors`, leaving a
stale `errors.json`. It is recorded here rather than fixed from a shop cycle.

**The event is `model_artifact_changed` with payload `{"artifact": <path>}`,**
the move's `dest_path` made relative to the build root, exactly as the browser
would request it from `/artifacts/`. No generation, no mtime, no size, no kind.
The floor does not distinguish `viewer.json` from geometry; the browser knows
which one it asked for and what to do with it (PRD 3.4). The existing
`model_changed` kind is removed rather than kept as a fallback — keeping it
would require the hash the rest of this change deletes.

**Deletions produce no event** (PRD D4), and no code implements that. A removal
is a delete event and the handler only acts on moves. The manifest is
authoritative for existence and, by F2's ordering, is republished before the
sweep removes anything, so the browser has already been told. Forwarding a
deletion would invite a fetch of a path that no longer exists — Defect A's
failed fetch, regenerated from a routine node removal.

**Nothing is announced at startup.** Preparation has already validated a
complete publication before the floor opens, and an event handler is silent
until something happens, so the floor cannot announce all 55 artifacts of
`v8-engine` to a browser that has not connected. The poll design needed a
seeding step to achieve this; this one has nothing to seed.

**The artifact route resolves the build root once.** `create_app` resolves it at
construction; the route resolves the candidate once and checks containment
against that fixed root. Traversal protection is unchanged — a candidate
resolving outside the root is still refused — but a publication landing between
two resolutions can no longer make a valid artifact look foreign, because there
is only one resolution. Torn reads are handled by F2's rename, not by the route.

**The source handler's build-tree exclusion is one condition.** The
`EXCLUDED_DIRECTORIES` and `EXCLUDED_PREFIXES` sets named a versioned-sibling
layout F2 deleted, and retaining them would silently exclude project source
directories that happen to share the prefix. What replaces them is a single
guard: ignore a path under `_build`. Without it a build would trigger the build
that produced it, which is a correctness requirement rather than an
optimisation — the one thing ADR 0010 got right about the build tree that
survives unchanged.

**The browser bridge keeps today's behaviour on the new events.** `main.tsx`
increments its generation on `model_artifact_changed` for `viewer.json` instead
of on `model_changed`, and shows the build failure by fetching `errors.json`
when an event names it, clearing that banner when the manifest event arrives.
The result is behaviourally today's floor — a full reload, Defects A and B still
present — but driven by observed output, so the sprint branch never shows a dead
model between cycles. S2 replaces the reload with the in-place update.

## Risks / Trade-offs

- **`watchdog`'s `Observer` runs on its own thread while the floor is asyncio.**
  → Events cross into the loop with `call_soon_threadsafe`, and the handlers do
  nothing but publish. The framework's own builder already observes this way.

- **A publisher writing directly into `_build` without F2's rename publishes
  nothing the floor will forward.** → Correct by the design's own rule: the
  floor reports what was published, and publication means rename. F2 makes that
  the framework's only publication path.

- **Two watches overlap on the project root, which also contains `_build`.** →
  The source handler ignores paths under `_build`. Without that guard a build
  triggers the build that produced it.

- **`FileMovedEvent` requires both ends of the rename inside a watched tree.**
  → F2's temporaries are created by `mkstemp(dir=...)` in the artifact's own
  directory, so both ends are always under the `_build` watch. If a future
  publication path moved a file in from outside, inotify would report a create
  and the floor would stay silent — a visible failure rather than a wrong event,
  and one the end-to-end tests would catch.

- **inotify watch exhaustion.** → 524 288 watches available against a project of
  tens of files and a build directory of tens of artifacts.

- **The bridge leaves Defects A and B live on the sprint branch until S2.** →
  Accepted and recorded: S1 is explicitly not the cycle that fixes them (PRD
  section 6), and hiding them behind a partial fix would make S2's acceptance
  criteria unfalsifiable.

## Migration Plan

No data or on-disk migration. The floor requires framework `sprint-003` @
`582da89` or later; an older framework that publishes by symlink swap installs a
whole directory rather than renaming artifacts into place, so the floor would
report nothing at all. The floor already refuses to open against a viewer older
than it requires, and that check is where the dependency belongs if it needs
stating.

`watchdog` becomes a declared shop dependency. It is already installed wherever
the floor runs, since solid-node depends on it, but the shop should not rely on
a transitive dependency of a package it shells out to.

## Open Questions

None. The remaining polling in the shop — `main.tsx`'s 1 s `setInterval`
refetching run and conversation state beside an open SSE stream — is browser
workspace rather than the model pipeline, and is left to its own cycle.
