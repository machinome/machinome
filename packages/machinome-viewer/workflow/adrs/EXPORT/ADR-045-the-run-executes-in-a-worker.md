# ADR-045: The run executes in a worker and the main thread only poses

**Status:** Accepted

**Date:** 2026-09-13

**Change:** `run-in-the-worker`

**Extends:**
- [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md)

**Depends on:**
- solid-node's ADR-110: the compiled mechanical program is published in
  the document (`openspec/changes/archive/2026-09-13-publish-the-mechanical-program/`)

## Context

solid-node has published the machine. A version 5 document is a version 4
one plus a top-level `program` object — the bank of coordinates with
their rest values, the values the program computes and never stores, the
edges in propagation order with their expressions, their affinity and
their jump plans, the declared bounds, the reaching-inputs table and the
five constants the algorithm is defined by — and, beside it, a tree whose
pose expressions name **joint coordinates** rather than drivers.

Under that document the carry law is no longer part of the tens drum's
pose. The drum's rotation is the single name `tens.drum.turn`, and what
puts a number there is a **run**: an absolute pose can only ever show the
first window, which is why ten `Add one` used to leave the tens drum
where one did. Not one expression in a version 5 document contains `$t`;
there is no timeline, and no bank value would ever change, because the
thing that changes a bank value is the tick.

This viewer had no tick. It also had four refusals in the way, two of
them silent: the version, twelve undeclared names, a qualified id that
resolved to `undefined` past its first dot, and nothing to move anything.

## Decision

**A published program is integrated by a TypeScript engine that mirrors
`solid_node/simulation/program.py` and `run.py` function for function**,
over the published data: admissions, propagation in program order,
`f(end) − f(start)` for a continuous law, the branch-per-segment
partition for a jumping one, wirings, formulas, checks, conflict, stops
located inside the tick with the group of inputs that push them,
segments, `blocked` with the travel actually admitted and no backlog,
snapshot, restore, reset, bounded rings. The rule is *the same arithmetic
in the same order*, not *an equivalent result*.

**`src/run/` is a library and the worker is a transport.** No DOM, no
three.js and no `postMessage` in the engine; `worker.ts` is a thin
decoder around it and `runtime.ts` is the main thread's side. That split
is what lets the conformance corpus (ADR-047) replay the engine
in-thread, where a divergence is a stack trace rather than a message that
never came back.

**The render loop drives the cadence and there is always one advance in
flight.** Per animation frame the main thread computes how many ticks the
elapsed wall time has earned, sends **one** `advance` message, and
renders the bank of the reply — and sends the next only after that reply
arrives. One rule settles three questions:

- a page nobody is watching gets no animation frame, sends no advance and
  accumulates **no backlog**: the machine stands where it stood;
- a tick slower than a frame drops **display** frames and never
  mechanics: no tick is skipped, the next advance asks for the ticks the
  stall earned, and the wall-time debt is capped at four frames' worth so
  a long stall cannot produce an unbounded burst;
- commands reach the worker in issue order and are applied before the
  next tick it integrates, which is the corpus's own rule.

**The step size is the viewer's own choice**, published nowhere, fixed
for the life of a mount at `1/240` s by default — because a run state
carries its step size and a restore across two of them is refused by the
framework's own rule, so a live `setDt` would silently invalidate every
state a host held. **Speed keeps its one meaning** — a multiple of real
time — and changes how many ticks a wall second earns, never the step
size, because a fast watch must not be a coarser simulation.

**A page that cannot create the worker runs the same engine in-thread and
says so** on the handle (`runsInWorker: false`). A
Content-Security-Policy forbidding a blob worker throws at
`new Worker(...)`; that is caught once. Silently degrading would be
wrong; failing to open the machine would be worse.

**The worker is bundled into the one published file.** `build.mjs` gains
a first pass that bundles `src/run/worker.ts` to a string and injects it
as `__WORKER_SOURCE__`; the runtime makes the worker from a blob URL of
it. There is still exactly one published artifact,
`dist/solid-widget.js`.

**A mounted run starts stopped.** It is created at the published rest
bank and begins when a host or a control asks — so a still capture and
every thumbnail get the rest pose for free, without knowing that runs
exist.

## Alternatives weighed

- **The engine written directly as the worker's message loop.** It would
  make the corpus suite spawn thirteen workers and put the algorithm
  behind a transport in every test that touches it.
- **The worker owns a timer and pushes frames.** A browser throttles a
  hidden tab's timer to about 1 Hz, and the worker would then be handed a
  one-second catch-up: an invisible backlog integrated while nobody is
  looking, with a thousand ticks of mechanism between two paints.
- **No worker at all — the tick on the main thread beside the render.** A
  jumping law with a non-affine level quantity searches 64 sample points
  and bisects up to 64 rounds per crossing per tick, which is exactly the
  work that must not compete with the frame.
- **Publish `solid-widget.worker.js` beside the bundle.** It breaks four
  copy sites and the one-file export contract to avoid one blob URL.
- **Scale `dt` with speed.** It would make a fast watch a *coarser*
  simulation, which is the one thing a jump law cannot survive.

## Consequences

- The viewer reads document version 5 and declares API version 8; the
  handle gains `run()`, which answers `null` for a document carrying no
  program.
- A 30 Hz display integrates the same ticks per wall second as a 60 Hz
  one, because elapsed time is what is measured — but a display that
  stops stops the machine. That is this decision, stated rather than
  mitigated.
- The engine reads and never recomputes the six things compile time
  decided: the edge order, each law's affinity, each plan's postorder,
  level quantity and rewrite, the `sources` table and the five `limits`.
  A jump primitive outside the published ten is refused by name, which is
  the engine's forward-compatibility seam.
- Nothing on screen drives a running document yet. The chrome is
  `drive-the-run-on-screen`.
