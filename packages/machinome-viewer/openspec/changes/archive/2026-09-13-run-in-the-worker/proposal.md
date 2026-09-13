## Why

solid-node has published the machine. This viewer cannot read it, and could
not run it if it could.

The framework's `publish-the-mechanical-program` cycle (archived
`2026-09-13-publish-the-mechanical-program`, ADR-110 and ADR-111) declares
**document version 5**: a version 4 document plus a top-level `program`
object carrying the compiled mechanical program — the bank of coordinates
with its rest values, the edges in propagation order with their expressions,
their affine flags and their jump plans, the spans, the reaching-inputs
table and the five constants the algorithm is defined by — and, beside it,
a tree whose pose expressions now name **joint coordinates** rather than
drivers. Under that document the carry law is no longer part of the tens
drum's pose; the drum's rotation is the single name `tens.drum.turn`, and
what puts a number there is a *run*.

**The empirical chain.** The Pascaline module needed a carry that
accumulates → an absolute pose can only ever show the first window, so ten
`Add one` left the tens drum where one did → the framework grew a running
time base that integrates a law instead of evaluating it → it now publishes
that program in the document → **this viewer must execute it.** The
acceptance document is on disk: the module's `_build/viewer.json`, version
5, 32,994 bytes, three inputs, nine joint coordinates, six intermediates, nine
edges, three jump plans, three relative instructions, no spans.

**What this viewer does with it today**, checked against that document.
Four refusals stand between it and a frame, and two of them are silent:

1. `assertRenderable` refuses the version: `RENDERED_VERSIONS` is
   `[1, 2, 3, 4]`. This one is correct and deliberate — the framework
   designed the bump so an old viewer refuses rather than animating a
   plausible, incomplete machine.
2. Were the version accepted, the document's `bindings` table names
   `_j0`, `_j1` and `_j2` — the branch placeholders of the three carry
   plans — and its pose expressions name `units.drum.turn` and eight
   more coordinate ids. None of those is a declared driver, so the
   undeclared-driver refusal fires on twelve names at once.
3. Were that accepted, **nothing would pose.** `DriverStore.scope()`
   splits a qualified id at its FIRST dot only, so `units.drum.turn`
   reaches the evaluator as `{units: {'drum.turn': 7}}` and resolves to
   `undefined`. Measured against the shipped modules: `evalExpr('(-1 *
   units.drum.turn)', {time: 0, drivers: store.scope()})` is `NaN`.
   Every three-segment id in every document version is already broken
   this way; a coordinate id is always at least three segments deep.
4. Were all three accepted, **nothing would move.** Not one expression
   in a version 5 document contains `$t`; `animated` is false, there is
   no timeline, and no bank value would ever change, because the thing
   that changes a bank value is the tick — and this package has no tick.

This change is the tick, and everything the tick needs.

## What Changes

- **The viewer reads document version 5.** `RENDERED_VERSIONS` becomes
  `[1, 2, 3, 4, 5]`; a version 6 document is refused by name, exactly as a
  version 5 one is refused by every viewer released so far. Documents 1 to 4
  render, animate and drive exactly as they do today.
- **A compiled program is loaded from the document and validated by name.**
  Every shape the engine cannot execute is refused when the document is
  loaded, naming what is wrong and quoting the source: a missing or
  malformed `program` key, an `edges` entry whose kind the engine does not
  know, a jump primitive outside the published ten, a placeholder two plans
  share, an expression whose free names are not among its edge's `needs`,
  a span over a coordinate the bank does not hold, a bound that reads
  anything but its own coordinate, an `inputs` set that disagrees with the
  `drivers` table, and an id set that cannot be nested (`a.b` beside
  `a.b.c`). Never a machine that runs wrongly.
- **A run engine in TypeScript, module for module against the Python run.**
  The tick — admissions, propagation in program order, `f(end) − f(start)`
  for a continuous law, the branch-per-segment partition for a jumping one,
  wirings, formulas, checks, hold, conflict, stops located inside the tick
  with the group of inputs that push, segments, `blocked` with the travel
  actually admitted and no backlog, snapshot, restore, reset, bounded rings
  — is `solid_node/simulation/program.py` and `run.py` reproduced function
  for function over the published data.
- **The run lives in a Web Worker.** The main thread never integrates: it
  sends commands, asks for an advance once per animation frame, and receives
  committed banks. A worker that cannot be created — a page whose policy
  forbids a blob worker — falls back to the same engine in-thread and says
  so on the handle, rather than failing to open the machine.
- **A committed bank poses the geometry.** Per frame the main thread
  evaluates the document's own expressions with the bank in the evaluation
  scope beside the driver values, which is the evaluator the widget already
  has; flexible parts follow by the same rule. Rendering never advances the
  run: a dropped frame drops display, not mechanics.
- **The handle gains the running API**: `run()` returns a running handle
  with `move`, `rate`, `trigger`, `cancel`, `start`, `pause`, `step`,
  `reset`, `snapshot`, `restore`, `state()`, `tick()`, `elapsed()` and an
  outcome channel reporting `completed`, `blocked`, `refused` and
  `cancelled` with the travel admitted. The on-screen chrome that issues
  those requests is the **next** change (`drive-the-run-on-screen`); this
  one leaves a version 5 document posed at its rest bank with no controls
  of its own, driven by its host.
- **`dt` is the viewer's choice, published nowhere.** The default is
  `1/240` s, settable once at mount and never afterwards, because a
  snapshot is refused across two step sizes.
- **Conformance.** The framework's `tests/running-corpus.json` — thirteen
  scenarios over eleven machines, 260 ticks, every jump primitive, a
  multi-source law, an expression bound, a blocked command, a rate, a
  snapshot and a restore — is committed here as the viewer's parity
  fixture, and a vitest suite replays every scenario through the engine and
  compares tick by tick: exact for discrete state, statuses, names, orders
  and levels; `1e-9` relative for every float. Every scenario passes. A
  divergence is a bug in this viewer, never a tolerance to widen.
- **The viewer API rises to 8** and `describe()` gains
  `documentVersions: [1, 2, 3, 4, 5]`, which is the field the framework
  reads to decide whether to warn on a build and whether to refuse
  `solid snapshot --renderer web`.
- **Two evaluator corrections the run forces into the open**, each with a
  red test: a qualified id is nested at **every** segment, so a
  three-or-more-segment id resolves instead of reading `undefined`; and
  `sign` resolves by the framework's own `(x > 0) − (x < 0)` rather than
  `Math.sign`, which differs from it at negative zero. Neither moves a
  number any correct document produced.

## Capabilities

### New Capabilities

None. The run is the viewer package's own behaviour, specified against
`viewer-package`.

### Modified Capabilities

- `viewer-package`: five new requirements — the viewer executes a published
  program; the tick is the framework's algorithm; a program the engine
  cannot execute is refused by name; a committed bank poses the geometry;
  the two runtimes agree on a conformance corpus — and three modified ones:
  the loader reads version 5, the declared API version rises to 8, and a
  qualified id resolves at every segment.
- `viewer-distribution`: the entry point's report gains `documentVersions`,
  the list of document schema versions this build reads, so a framework can
  ask the question it actually has.

Capabilities needing no delta, and why:

- `development-server`, `snapshot-capture`: both mount the same bundle
  through the same contract, and both inherit version 5 from it — the dev
  page poses a version 5 document at its rest bank and the capture
  photographs one, with no route or option changed. What they must say
  about a RUN — reload keeping a run whose program identity is unchanged,
  a capture stating what it photographs — belongs with the controls, in
  `drive-the-run-on-screen`.
- `viewer-assembly-navigation`: assembly identity is names and structure,
  never an expression and never a coordinate.

## Impact

- `solid_node_viewer/widget/src/run/` — **new**: `program.ts` (load and
  validate), `edges.ts`, `jumps.ts`, `commands.ts`, `run.ts`, `engine.ts`
  (the façade), `scope.ts` (the nesting builder), `protocol.ts` (the
  message types), `worker.ts` (the worker entry), `runtime.ts` (the main
  thread's side: worker or in-thread, one advance in flight).
- `solid_node_viewer/widget/src/viewer.ts` — `RENDERED_VERSIONS` gains 5;
  `assertRenderable` validates the program and widens the declared-name set
  to the clock, the coordinates, the intermediates and the plans'
  placeholders; `mount` starts a runtime for a version 5 document and poses
  from its banks; the handle gains `run()`.
- `solid_node_viewer/widget/src/drivers.ts` — `scope()` nests at every
  segment (through `run/scope.ts`), which is the three-segment fix.
- `solid_node_viewer/widget/src/expressions.ts` — `context.sign` becomes
  the framework's formula. Nothing else: the DAG, the memoization, the
  pass comparison and the bindings map are what the engine evaluates
  through, unchanged.
- `solid_node_viewer/widget/src/types.ts` — `ManifestVersion` gains `5`;
  `ManifestProgram` and its parts; `ManifestInstruction` gains `by`.
- `solid_node_viewer/widget/src/running-corpus.json` — **new**, the
  framework's committed fixture, copied verbatim;
  `src/run/running-corpus.test.ts` replays it.
- `solid_node_viewer/widget/build.mjs` — a two-pass build that bundles the
  worker entry into the one published `dist/solid-widget.js`; no second
  published file.
- `solid_node_viewer/widget/package.json` — `solidNodeViewerApi` 7 → 8, a
  new `solidNodeDocumentVersions` array; `version.test.ts` follows.
- `solid_node_viewer/bundle.py` — `describe()` reports `documentVersions`
  from that one declaration; `tests/test_bundle.py`, `tests/test_cli.py`.
- `README.md` (the version table gains document version 5 at API 8),
  `CHANGELOG.md` (**0.2.0, unreleased** — the founding of running
  documents; 0.1.0 stays exactly as it is), and the ADRs design.md names.
- **The producer half is done, in another repository.** solid-node's
  `publish-the-mechanical-program` is archived on its
  `open-run-simulation` worktree. This change carries no framework edit and
  imports nothing of the framework: the corpus and the acceptance document
  are data.
- **Ordering.** Until this change lands, a version 5 document is refused by
  every viewer in the workspace — which is the framework's designed
  behaviour and what makes the ordering free. The framework's `viewer`
  extra version floor is its own follow-up, once this package is released.
