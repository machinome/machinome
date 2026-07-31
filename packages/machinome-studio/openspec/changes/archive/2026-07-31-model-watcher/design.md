## Context

Floor serves the project's completed `_build` directory to the browser and
publishes a `model_changed` event that tells the browser to re-fetch it. Today
that event has exactly one source: a POST from a `solid develop root --callback
<url>` process that the machinist is told to start and keep alive. The
orchestrator mints the token, injects the command into the machinist's runtime
context only, and the broker accepts the callback at
`POST /api/runs/{run_id}/model/ready/{token}`.

Constraints that shape this design:

- **ADR 0004 stands.** Floor must not import, execute, reload, or serve project
  Python. The completed `_build` directory stays the only functional-model
  input. This change replaces the *trigger*, not the boundary.
- **`solid build root` is already shop-run.** `floor/preparation.py` runs it
  before the floor opens, from the project directory, with `PYTHONPATH` extended
  when the framework is a checkout inside the workspace. The watcher needs the
  same invocation, not a new one.
- **Repeat builds are incremental — as of framework ADR-033, and not before
  it.** An earlier draft of this design claimed the copy `BuildSession.reset()`
  makes before building was what carried unchanged work forward. It was not:
  measured on `v8-engine`, a warm no-op build cost 19.79 s against 19.83 s to
  build the same project from nothing, because `assemble()` ran `render()`
  before anything consulted the freshness check. Framework ADR-033 fixed both
  that and the source set behind it; the same no-op build now costs 3.22 s, of
  which about 2.45 s is the bare interpreter and framework imports. A one-shot
  build per change is affordable because of that change, so this design's
  latency budget assumes a framework at or after it. Correctness does not: on an
  older framework the watcher still refreshes the right view, just slowly.
- **The shop does not pin a framework version.** Anything that makes floor
  import `solid_node` turns framework drift into a harness crash.
- **macOS must not get harder.** The shop and framework are expected to run
  there; nothing here may be Linux-specific.

## Goals / Non-Goals

**Goals:**

- A change to the project's model refreshes the maker's view regardless of who
  made it — machinist, designer, or the pilot editing by hand.
- A rebuild failure is visible to the maker instead of being silent, and the
  last complete model stays inspectable.
- The trigger is deterministic shop machinery, not agent behaviour, and it lives
  for the whole life of the floor.
- Remove the callback seam entirely rather than leaving two paths to the same
  event.

**Non-Goals:**

- Precise knowledge of which files back the model. The shop cannot ask for that
  yet; see the risk below and the follow-up framework change.
- Replacing `solid develop` for framework or standalone users. This is about how
  the shop drives a build, not about the CLI's own watch loop.
- Serving or interpreting anything beyond the published artifacts. The browser
  keeps fetching `viewer.json` and its referenced files, unchanged.
- Restart recovery, which remains intentionally absent (ADR 0005).

## Decisions

### D1 — The watcher is a floor task tied to the app lifespan, not an orchestrator task

The watcher starts from the FastAPI application's lifespan and stops with it.
`create_app` gains the project root and the solid command; when both are
present it runs the watcher.

*Why:* the refreshed thing is the broker's own static artifact route, and the
broker is what publishes `model_changed`. Tying the watcher to the app gives
both entry points — `python -m floor.orchestrator` and broker-only
`python -m floor` — the same behaviour with no duplicated wiring, which matters
because broker-only mode is what browser and lifecycle work runs against.

*Alternative considered:* start it from `floor/orchestrator.py` beside the
backend. Rejected: the orchestrator owns *agent* processes, and a live model has
nothing to do with agents. It would also leave broker-only mode with a dead
view, and that is the mode the E2E test uses.

*Consequence:* tests that build an app without a solid command get no watcher
and no subprocesses, which keeps the existing API tests unchanged in cost.

### D2 — Detect changes by polling a fingerprint, with no new dependency

The watcher walks the project directory for `*.py` files and compares a set of
`(path, mtime_ns, size)` tuples every 0.5 s. It skips `.git`, `__pycache__`,
`.venv`, and — critically — `_build` and its sibling versioned directories and
staging directories.

*Why not `watchdog`:* it is what the framework uses and it is cross-platform, so
it was the obvious candidate. But it adds a runtime dependency to a harness that
has two, and it brings failure modes of its own (inotify watch exhaustion; the
framework already carries a `_watch_broadly` fallback for a related problem). A
CAD project is tens of Python files, so a walk costs microseconds, and the poll
interval doubles as the debounce we would have had to write anyway. Polling is
identical on macOS and Linux with no platform code.

*The exclusion is a correctness requirement, not an optimisation.* A build
writes into the build tree; if the watcher saw those writes it would trigger
itself forever. Wart #3 made `_build` a symlink to a versioned sibling
(`_build.<random>`) with transient `.solid-node-build-*` staging directories, so
the exclusion must cover the whole family, not the literal name `_build`.

*Trade-off accepted:* up to 0.5 s of detection latency versus the callback's
near-immediacy. The build itself dominates that.

### D3 — Require a stable fingerprint across two consecutive polls before building

*Why:* an editor writing a file in place can be observed mid-write, producing a
build failure that a rebuild 0.5 s later silently fixes — a failure banner that
flashes for no reason. One extra quiet poll costs at most 0.5 s and removes most
of that class. It also coalesces a multi-file save into one build.

### D4 — Publish `model_changed` only when the published snapshot actually changed

The watcher hashes `_build/viewer.json` after each successful build and
publishes only when the hash differs from the last published one, seeded from
the snapshot preparation already validated.

*Why the hash and not the build's exit status:* every publication installs a new
versioned directory, so inode and mtime change on every build whether or not
anything is different — those are useless as signals. Content is the honest one.

*Why `viewer.json` alone is sufficient:* the framework embeds each node's source
`mtime` in the viewer state, so any rebuild that re-rendered anything changes
this file. A referenced STL cannot change content while `viewer.json` stays
byte-identical, because the framework only re-renders a node whose `mtime` moved
— and that `mtime` is in the file. ADR-033 strengthened this: a node's `mtime`
now covers the project modules its source imports, so an edit to a module that
holds shared geometry but defines no node moves the dependent nodes' mtimes and
therefore this file. Before that change such an edit moved nothing at all, and
this gate would have withheld a refresh the maker needed.

*What it correctly withholds:* a rebuild triggered by a `.py` edit the model
does not depend on — a test file, an unused helper — now re-renders nothing, so
`viewer.json` is byte-identical and no event is published. The over-triggering
in D2 costs a few seconds of background work and never reaches the browser.

*Direction of error:* a false positive costs the browser one re-fetch of static
files. A false negative shows the maker a stale model. This errs toward
refreshing.

### D5 — One build at a time, with a pending flag

A change observed while a build is running sets a flag; the watcher rebuilds
once when the current build finishes, rather than queuing or racing. The build
runs through `asyncio.create_subprocess_exec` so the event loop keeps serving.

*Why:* concurrent `solid build` invocations are exactly the publication race
wart #3 addressed. That race is now settled safely rather than corruptingly, but
provoking it deliberately would still waste a full build. Serialising also gives
predictable failure attribution.

### D6 — Build outcome events distinguish failure, recovery, and model change

The event carries the build's captured stderr, bounded to a few kilobytes. The
browser shows it and keeps rendering the last complete model. Every subsequent
successful rebuild publishes `model_build_succeeded`, which clears the failure
without implying that the artifacts changed. `model_changed` remains the only
event that causes the browser to fetch a new snapshot.

*Why a shop event and not the framework's `errors.json`:* the framework does
write `_build/errors.json` on failure, and floor could serve it. But that
couples the browser to a framework file convention, and it gives the maker no
push signal — they would have to poll. The exit status of a process the shop
itself ran is the more direct fact, and it is the shop's own event stream.

*Why this is new behaviour worth having:* under the callback design a failed
rebuild sent nothing at all. Silence was indistinguishable from "no edit". This
is the change's second maker-visible improvement, not incidental cleanup.

### D7 — Delete the callback seam rather than keep it as a fallback

The token, the route, `--callback-token`, `RoleContext.model_callback_url`, the
three backend prompt blocks, and the machinist's process paragraph all go.

*Why:* two triggers for one event is worse than either alone — a stale machinist
process would keep firing refreshes the shop did not ask for, and the failure
mode this change exists to remove (a maker-visible guarantee resting on agent
behaviour) would still exist behind a flag. Nothing else uses the route.

## Risks / Trade-offs

- **The watcher rebuilds on Python edits that cannot affect the model** — a test
  file, a helper the model does not import. → Accepted, and now cheap: measured
  on `v8-engine`, a rebuild after editing a test file costs 3.16 s and, by D4,
  publishes nothing. The framework's own `Builder` watches the exact
  `node.files` set, which ADR-033 made correct; the shop still has no way to ask
  for it. A follow-up framework change (`solid sources root`) would let the
  watcher watch that set directly, but at these times it is an optimisation
  rather than the fix this cycle was going to depend on. The watcher logs each
  rebuild so the wasted-rebuild rate stays collectible if that judgement turns
  out to be wrong.
- **Build latency on a complex real project.** On `v8-engine`, against a
  framework carrying ADR-033: no-op 3.22 s, one leaf edited 3.73 s, a shared
  kinematics module edited 3.00 s. About 2.45 s of each is interpreter and
  framework import, so a fresh process per build is now the dominant cost rather
  than the rendering. → Accepted. If that floor becomes the thing worth
  removing, a persistent build process is the answer, and it is a separate
  design; it was not the answer while a build cost twenty seconds, which is why
  the one-shot shape stands.
- **The shop does not pin a framework version, and this cycle's latency numbers
  assume ADR-033.** → Correctness is unaffected: on an older framework every
  refresh the maker needs still arrives, and D4 still withholds the ones they do
  not, because both rest on `viewer.json` content rather than on timing. What
  degrades is speed, visibly and diagnosably, not the model on screen.
- **A `.py` edit that breaks the model now produces a visible failure where the
  maker previously saw nothing.** → That is the intent, but it means a
  half-finished edit by any agent can surface a banner. D3 removes the
  mid-write case; the rest is honest reporting of a genuinely broken model.
- **The watcher runs builds the machinist did not ask for**, concurrently with
  the machinist's own `solid build` verification runs. → Wart #3 made concurrent
  publication safe: the loser of a race reports through the build's own error
  channel instead of raising, and readers never observe a missing or mixed tree.
  This design depends on that fix being in place.
- **Broker-only mode now spawns build subprocesses**, which the E2E test did not
  previously do. → The watcher only runs when a solid command is supplied, so
  tests that do not want it do not get it.

## Migration Plan

Not applicable in the deployment sense — the shop is local and experimental,
with no deployed instances and no persisted state that survives a run. The
change is complete within one cycle: the callback path is removed in the same
commit that adds the watcher, so no configuration exists in which both are
live.

## Open Questions

None blocking. Apply will retain reproducible watcher-level latency and rebuild
count evidence. The framework work this design was originally waiting on has
landed as ADR-033; what remains separate is the interpreter start-up floor and
`solid sources root`, and neither gates this cycle.
