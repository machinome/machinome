# ADR 0010: The shop watches the project and rebuilds it, rather than asking an agent to

**Status:** Accepted (amended by [ADR 0013](./0013-observe-atomic-build-publications.md))

**Date:** 2026-07-31

**Origin:** Shop change `model-watcher`

**Supersedes:** the callback mechanism of ADR 0004, whose artifact boundary this
decision reaffirms unchanged

## Context

ADR 0004 settled that Floor never imports, executes, reloads, or serves project
Python: the completed `_build` directory is the only functional-model input. That
boundary is right and is not in question here.

What ADR 0004 also settled, and what this decision replaces, is how Floor learns
that the model has changed. It learned from a POST: the orchestrator minted a
token, injected `solid develop root --callback <url>` into the machinist's
runtime context, told the machinist's role card to start that process and keep it
alive, and the broker accepted the callback at
`POST /api/runs/{run_id}/model/ready/{token}`.

That makes a guarantee the maker depends on rest on agent behaviour. A machinist
that never started the process, or whose process died, leaves the maker looking
at a stale model with no indication anything is wrong. Worse, the machinist is
not the only author: a designer's change, or the pilot's own edit, refreshed
nothing at all, because only the machinist was given the command. The failure is
silent in every case.

A failed rebuild was equally silent. `solid develop` sent a callback on success
and nothing on failure, so "the model is broken" and "nobody edited anything"
looked identical to the maker.

## Decision

The shop watches the project and rebuilds it. The trigger is shop machinery that
lives for the whole life of the floor, and the callback seam is removed rather
than kept as a fallback.

**The watcher belongs to the FastAPI application's lifespan, not to the
orchestrator.** What it refreshes is this application's own artifact route, and
this application is what publishes `model_changed`. Tying it to the app gives
both entry points — the orchestrated floor and broker-only mode — the same
behaviour with no duplicated wiring, and broker-only mode is what the E2E test
runs against. The orchestrator owns *agent* processes; a live model has nothing
to do with agents. An app built without a solid command runs no watcher and
spawns no subprocesses, so existing API tests are unchanged in cost.

**Change detection is a poll over a source fingerprint, adding no dependency.**
The watcher compares `(path, mtime_ns, size)` for `*.py` under the project root
every 0.5 s, and requires the fingerprint to be stable across two consecutive
polls before building. `watchdog` was the obvious candidate — the framework uses
it and it is cross-platform — but it adds a runtime dependency to a harness that
has two, and brings inotify watch exhaustion with it. A CAD project is tens of
files, so the walk costs microseconds, the poll interval doubles as the debounce,
and the behaviour is identical on macOS and Linux with no platform code. The
stability requirement matters for a reason beyond coalescing a multi-file save:
an editor writing in place can be observed mid-write, and building that produces
a failure banner that a rebuild moments later silently retracts.

**Excluding the build tree is a correctness requirement, not an optimisation.** A
build writes into that tree; a watcher that saw those writes would trigger itself
forever. Since the build directory became a symlink to a versioned sibling with
transient staging directories beside it, the exclusion covers the whole family
(`_build`, `_build.*`, `.solid-node-build-*`) and not the literal name.

**`model_changed` is published only when the published snapshot's content
changed.** Every publication installs a new versioned directory, so inode and
mtime move on every build whether or not anything differs; content is the only
honest signal. The watcher hashes `_build/viewer.json`, seeded from the snapshot
preparation already validated. Errors resolve toward refreshing: a false positive
costs the browser one re-fetch of static files, a false negative shows the maker
a stale model.

**A failed rebuild is reported, and recovery is a separate fact from change.**
`model_build_failed` carries the build's captured stderr, bounded to a few
kilobytes; the browser shows it beside the model and keeps rendering the last
complete one. A later success publishes `model_build_succeeded`, which clears the
failure without implying the artifacts changed. Only `model_changed` causes the
browser to fetch a new snapshot. The framework does write `_build/errors.json`,
and Floor could serve it — but that couples the browser to a framework file
convention and gives the maker no push signal. The exit status of a process the
shop itself ran is the more direct fact.

**One build at a time.** A change observed during a build sets a pending flag and
produces one follow-up rebuild rather than a queue or a race.

## Relationship to framework ADR-033

This design's affordability rests on a framework change made in the same period.
An earlier draft claimed `BuildSession`'s copy of the prior build tree was what
carried unchanged work forward; measurement disproved it — on `v8-engine` a warm
no-op build cost 19.79 s against 19.83 s cold, because `assemble()` rendered
before consulting the freshness check. Framework ADR-033 fixed that and the
source set behind it.

That change also carries this design's `viewer.json` gate. A node's `mtime` now
covers the project modules its source imports, so an edit to a module holding
shared geometry moves the dependent nodes' mtimes and therefore the snapshot.
Before it, such an edit moved nothing and this gate would have withheld a refresh
the maker needed.

Measured on `v8-engine` through the watcher itself, poll interval 0.2 s:

| Edit | Rebuild | Published |
|---|---|---|
| A leaf's source | 3.60 s | `model_build_succeeded`, `model_changed` |
| A shared `kinematics.py` | 3.01 s | `model_build_succeeded`, `model_changed` |
| A test file | 3.03 s | `model_build_succeeded` only |

The last row is what makes watching `*.py` broadly acceptable: the rebuild
happens, re-renders nothing, and never reaches the browser.

The shop pins no framework version. On an older framework the watcher still
refreshes the right view and still withholds the wrong ones — both rest on
snapshot content, not on timing. What degrades is speed, visibly.

## Consequences

- The maker's view is current regardless of who changed the model, including the
  pilot editing by hand with no agent running at all.
- A broken model is visible rather than silent, and the last complete model stays
  inspectable while it is fixed. This is new behaviour, not incidental cleanup.
- The machinist's role card no longer manages a process, and no backend injects a
  develop command. `RoleContext.model_callback_url`, the token, the route, and
  `--callback-token` are gone; nothing else used them.
- Broker-only mode now spawns build subprocesses when given a solid command,
  which it did not before.
- A half-finished edit by any agent can surface a failure banner. The two-poll
  stability requirement removes the mid-write case; the rest is honest reporting
  of a genuinely broken model.
- Up to one poll interval of detection latency replaces the callback's
  near-immediacy. The build dominates it.
