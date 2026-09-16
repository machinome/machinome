# Calculators/Curta-Type-I-3x (2026-09-16, the operating Curta in the studio)

Found while answering "why is the operating Curta so slow in the browser",
against the project's own published document rather than a fixture.
**Status: recorded; triage open.** The dominant cost of that document is the
SEARCHED self-read crossing, which is the framework's, is already recorded in
`solid-node/workflow/warts.md` under `read-the-driven-coordinate` and under
"Originating Curta follow-up: seconds per Python tick", and is not restated
here. What follows is the part that is the VIEWER's, and it is the smaller
part: no correctness failure, and no claim that removing it makes the
document interactive.

## The run rebuilds its evaluation scope on every expression it evaluates

- **Symptom.** A tick of a large running document spends more time
  materializing scope objects and comparing them than evaluating the
  expressions the document actually states. It is paid on every tick,
  including a tick in which nothing moves.

- **Cause.** `run/program.ts`'s `evaluateExpression` is deliberately the one
  evaluation site of `src/run/`, and by design D11 every call builds a FRESH
  scope: `drivers: nest(values)`. `run/scope.ts`'s `nest` splits each dotted
  id and allocates the owner chain, so the cost of one call is the whole id
  set, not the expression. The freshness rule itself is right — the comment
  at that call site explains what a reused, mutated object would silently do
  to the memo, and that reasoning is not disputed here.

  The second cost follows from the first. `expressions.ts`'s `ensurePass`
  takes an identity fast path — `scope === lastScope` — whose own comment says
  it is "true for every evalExpr call of one `tree.update` walk". Under a run
  there is no such walk: each call arrives with a new object, so the fast path
  cannot hit, `scopesEqual` deep-compares the nested driver map through
  `mapsEqual`, and on the (frequent) miss the pass counter advances and every
  memoized node value in the shared DAG is abandoned. The hash-consing
  ADR-043 bought for the POSE path is therefore largely unavailable to the RUN
  path, by construction rather than by accident.

- **Evidence.** Viewer `main` at `94ecbd3` (API 16), engine loaded in-thread
  under Node v24.11.1. Document: `Calculators/Curta-Type-I-3x`,
  `simulation.running:OperatingCurta` as exported to
  `_build_running/viewer.json` — version 7, 208 coordinates, 268 law edges,
  547 jump nodes, 32 self-read edges, 8 594 shared bindings, 148 pieces.
  Step `1/240` s, the viewer's own `DEFAULT_DT`.

  Counted per tick, by instrumenting a bundled copy of the engine:

  |                              | idle tick | crank turning |
  |------------------------------|-----------|---------------|
  | `evaluateExpression` calls   |     4 206 |         8 458 |
  | ids nested by `nest`         |    67 261 |       190 371 |
  | DAG nodes computed           |    20 513 |     1 392 215 |
  | `mapsEqual` calls            |    13 049 |        54 862 |
  | evaluation passes started    |     3 508 |         6 003 |

  An idle tick therefore splits and allocates 67 261 id segments to evaluate
  20 513 arithmetic nodes, and a crank tick abandons the whole memo 6 003
  times. `node --cpu-prof` over 200 idle ticks attributes **40.1%** of
  self time to `nest` (9.1% `foldedNames`, 3.5% `mapsEqual`); over 100 crank
  ticks, **20.0%** to `nest` and 3.0% to `mapsEqual`, with `compute`,
  `valueOf` and `resolveName` — the search itself — taking 59.3%.

  Wall time on that bench: 17-21 ms an idle tick, 152-170 ms a crank tick.
  The measured shares put at most roughly a quarter to two fifths of a tick
  inside this finding; the rest is the framework's searched crossing.

- **Workaround.** None needed for correctness. A host that can raise the step
  pays this fixed cost fewer times per simulated second, which is what the
  studio did (`libresolid-studio`, floor mount option `run.dt`); that changes
  how often the cost is paid, not the cost.

- **Proposed interface.** None. This is an internal cost, not a behaviour: the
  ratified contract — one evaluation site, a scope a caller cannot mutate
  underneath the memo — should survive whatever fixes it. Two directions were
  considered and neither is ratified:

  1. Resolve a dotted id against the FLAT bank in `resolveName`, so no nested
     object is materialized at all. `assertNestable` already refuses the one
     id shape that makes flat and nested resolution disagree.
  2. Keep the nested scope but build it ONCE per tick and hand the DAG an
     explicit generation stamp, so a pass is invalidated by the producer
     saying so rather than by `mapsEqual` inferring it.

  Either would have to keep the guarantee the D11 comment names: an engine
  must not be able to read a previous evaluation's memoized numbers.

- **Skill text this would delete:** none. It is a performance finding, not a
  capability the shop currently works around in prose.
