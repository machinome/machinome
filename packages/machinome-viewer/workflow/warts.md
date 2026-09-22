# Calculators/Curta-Type-I-3x (2026-09-16, the operating Curta in the studio)

Found while answering "why is the operating Curta so slow in the browser",
against the project's own published document rather than a fixture.
**Status: recorded; triage open.** The dominant cost of that document is the
SEARCHED self-read crossing, which is the framework's, is already recorded in
`machinome/workflow/warts.md` under `read-the-driven-coordinate` and under
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

- **After-measurement (2026-09-16, `walk-only-what-moves`, ADR-060).** A
  quantity followed along a step's path now reads a followed point's
  qualified ids from the run's FLAT bank directly (Proposed interface
  direction 1, above) — but only for the five call sites that FOLLOW a
  quantity along many points of one piece; `evaluateExpression` itself is
  unchanged for every call that is not one of them, so `nest` does not
  disappear, it falls out of the HOT path. Measured on this cycle's own
  bench (node v24.11.1, in-thread, the same document and bundle): `nest`'s
  self time fell from 40.1% to **12.0%** of an idle tick and from 20.0% to
  **4.65%** of a crank tick. `foldedNames` (the selection fold, untouched
  by this cycle) is now the largest single self-time contributor on an
  idle tick, at 16.6%.

  **Triage: largely retired by ADR-060; the remainder is not worth a cycle
  on this document.** This cycle's own measurement (its proposal's Non-
  goals, "Retiring the rest of the scope-rebuild wart") found that after
  the change 100% of this document's cost is inside the two evaluation
  sites `walk-only-what-moves` already addresses, and that direction 2
  above (a per-tick generation stamp) buys nothing further on it. The
  entry is kept rather than deleted: the memo's SECOND cost — that it
  shares no node between two DIFFERENT followed quantities under one run,
  because each gets its own fresh scope by the D11 rule this finding does
  not dispute — is unaddressed, and a document whose followed quantities
  overlap more than the Curta's own could still pay for it.

- **OperatingCurta v11 follow-up (2026-09-22).** The earlier conclusion was
  for the v7 export and no longer describes this project's v11 running source
  timing. On its pinned 213-coordinate export, with WebGL absent, 48/480 crank
  ticks took 32.605 s. ADR-074's unchanged-node cache fell that to 27.838 s
  (14.6%), and its selector setup from 11.553 s to 7.004 s. The post-cache
  profile still assigns substantial CPU to `nest`, `compute`, `resolveName`
  and full-bank copies at `ExpressionPath.bind` (alongside necessary
  `PathValue.at` work); see `workflow/evidence/operating-curta-path-cache-2026-09-22.md`.
  **Triage: reopened for this v11 document.** A next cycle must measure and
  address the remaining viewer-owned evaluation/scope cost without weakening
  the admitted path or changing dt; this cache alone does not make the
  declared two-second turn interactive.

- **Minimal retained inputs (2026-09-22).** The next viewer cycle removed
  `ExpressionPath.bind`'s full-bank generation-reset copy: the same pinned
  48-tick window fell from 24.420 s to 22.075 s (9.6%) in a paired CPU run,
  with the exact 213-entry digest unchanged. See
  `workflow/evidence/operating-curta-minimal-path-inputs-2026-09-22.md`.
  Remaining `nest` and whole-expression evaluation are not covered by this
  cycle. **Triage: still open; no full-turn browser acceptance.**

# The clocked machine (2026-09-17, `execute-the-commit`, ADR-062)

Four findings met while mirroring machinome's clocked executor (ADR-125,
ADR-126, ADR-128) into the viewer. They are recorded HERE rather than only
in the change's own `evidence.md` — which is where a finding met while
applying a cycle normally lives, and which holds each one's full text —
because none of them belongs to a viewer cycle to fix: two are the
PRODUCER's, one is the producer's CORPUS's, and one is a property of this
repository's suite rather than of any change in it. **Status: recorded;
triage the pilot's.**

## A machine's identity is not a function of the machine

- **Symptom.** The same class exported two ways publishes two
  `clocked.identity` hashes, so a bank snapshotted against one export is
  refused when restored against the other. That is not what machinome
  ADR-128 §13 means by "a bank taken against one machine is refused
  against another".

- **Cause.** `Clocked.described` opens its digest with
  `root {klass.__module__}.{klass.__qualname__}`. The module path is a
  property of how the class was IMPORTED, not of the machine.

- **Evidence.** The corpus's `Calculator` (imported as
  `tests.clocked_project.calculator`) publishes
  `6eb8e57724cde8a15bc10a2966d02e039ba6fa4aee8c3392bb02c951064eb4a7`; the
  same class exported by `machinome export
  tests/clocked_project/calculator.py:Calculator` publishes
  `979b1a0ef4fe214106f329844ef1c5af789dd18608b5d883eaf22bfdc73ba684`.
  **Every other field of the two `clocked` objects is byte-identical** —
  `clock`, `own`, all six `commits`, all three `bounds`, `limits` — as are
  the `drivers`, `states`, `instructions` and `bindings` tables. Importing
  the class the corpus's way in a throwaway copy reproduces the corpus's
  hash exactly.

- **Not the viewer's.** It is PRODUCER-side, and it is shared with the
  running half: `Program.described` opens the same way, which ADR-057
  already recorded for a program's `identity`. Nothing in the viewer works
  around it; the acceptance fixture's README records both strings.

## The clocked corpus does not discriminate the landing walk's segment scale

- **Symptom.** machinome ADR-128's closure 2 — the far-side walk's first
  step is sized by the SEGMENT rather than by the ulp of a value that
  happens to be `0.0` — is unpinned by the corpus. Dropping the scale in
  BOTH clocked callers (the event landing and the stop landing) leaves all
  104 of this cycle's clocked tests green.

- **Cause.** Structural, and the framework's own: the ulp-of-zero hazard is
  reached only where the walk starts from zero, and the clip says the
  zero-travel case OFF the crossing (closure 1) rather than leaving it to
  the walk — which masks closure 2 on every corpus fixture.

- **Evidence.** One of ten mutations in the cycle's battery, each applied
  and reverted; this one and its stop-side twin were the only two that bit
  NOTHING. The behaviour is pinned here instead by a direct unit test of
  `farSideOf` in both directions (`src/run/jumps.test.ts`), where it is
  unambiguous.

- **Not the viewer's to fix.** The gap is in the producer's corpus, and the
  same is presumably true of the framework's own suite: a corpus fixture
  whose landing walk starts from zero at a crossing the clip does not
  short-circuit would close it on both sides at once.

## What an instruction MEANS under a clocked root

- **Symptom.** machinome ADR-128 §14 publishes a clocked root's declared
  instructions in the version 5 shape and gives the table NO runtime
  meaning. A consumer can neither honour one nor honestly hide it.

- **What this build does.** Lists them, DISABLED, with the reason available
  to a reader and to assistive tools, and refuses `machine().trigger()` by
  name. Hiding them would make the panel disagree with a document the maker
  can read; showing them live would offer a gesture nothing can honour.

- **Open, in both repositories.** The framework records it as its own wart
  and the cycle's design as its one open question. If the answer is "an
  instruction is a request on its targets", it is a later cycle here and
  there.

## One vitest run in six failed and was never reproduced

- **Symptom.** During `execute-the-commit`, one full `npx vitest run` —
  started while the Python suite's Chromium was still settling — reported
  `1 failed | 1138 passed` without the run being captured. Five consecutive
  runs before and after it, and three consecutive runs of
  `src/clocked/cost.test.ts` alone, are clean at 1139/1139.

- **The one candidate.** The only load-sensitive assertions in the suite are
  the cost floors, and this cycle's are the ratified design's own: 4 ms
  against a measured 0.26–0.95 ms, which is four to fifteen times' headroom
  on an idle box and less on a loaded one.

- **Left at the ratified number rather than quietly widened.** Recorded so
  that the next unexplained red in this suite is met with a known suspect
  rather than a fresh investigation, and so the pilot knows which assertion
  in this repository can be made to fail by load alone.

# The clock (2026-09-17, `run-the-clock`, ADR-063)

Two findings met while mirroring machinome's CLOCK (ADR-127, ADR-128 §10)
into the viewer, recorded HERE rather than only in the change's own
`evidence.md` — which is where a finding met while applying a cycle normally
lives, and which holds each one's full text — for the same exception the
entry above names: neither belongs to a viewer cycle to fix. One is the
PRODUCER's, and one is a limit of a decision this cycle ratified rather than
a defect anywhere. A third of ADR-125's own narrowings — a MULTI-INPUT
request moving a driver and the clock together — is recorded in the change's
`evidence.md` and is not opened here, because nothing has asked for it: the
corpus does not script one and no fixture wants one. **Status: recorded;
triage the pilot's.**

Three of the four findings recorded for `execute-the-commit` above are
carried forward unchanged and are not restated: a machine's identity is not a
function of the machine (reproduced exactly by this cycle's `Regulator`
fixture — `281dfdc2…` from `machinome export`, `2e172caa…` from the corpus
generator, every other field of both `clocked` objects identical), what an
instruction MEANS under a clocked root, and the load-sensitive cost floors —
of which this cycle moved exactly one, to the design's own ratified 16 ms
frame budget, and said so.

## A CLIP in time, and a chain that follows the clock

- **Symptom.** A clocked machine cannot express a stop over elapsed seconds.
  No published constraint may name the clock — in its chain, its bound, its
  level or its `shapes` — and no declared stop ever clips a request that
  moves the clock.

- **Not a defect: a ratified decision with a recorded narrowing.** ADR-127
  decides it, for the reason that a declared range is a MECHANICAL stop
  (ADR-108) and nothing is in the way of the next second, and it records the
  later cycle that would take the clipped time request. This cycle MIRRORS
  the producer's refusal rather than anticipating that cycle: the viewer's
  loader now refuses exactly what `clocked.py`'s `_over_the_bank` refuses,
  where before it was silently wider and would have clipped a hand-written
  document against a clock-driven coordinate.

- **Producer-side if it is ever to change**, and its first task is the
  producer's too: settling ADR-126's contested direction test for a level
  that is PERIODIC in time. Nothing here works around it.

## `max_crossings` bounds a played frame, and the refusal cannot name the speed to drop to

- **Symptom.** Playing an elapsed machine at a high speed on a machine with a
  fast release can ask one frame to cross more surfaces of one relation than
  the machine's own published `limits.max_crossings` admits. The request is
  refused whole, the transport pauses and reports — and the message can say
  what it refused but not what speed WOULD work.

- **Cause.** A frame is one request (ADR-063), by the decision that keeps
  every event inside it located exactly and in order, so the machine's own
  per-request limit applies to it. Computing the largest admissible speed
  would need the EVENT RATE, which the published document does not carry:
  `Regulator`'s one release a second is a property of its law, not a field.

- **Evidence.** At the corpus's `max_crossings` of 1000 and `Regulator`'s one
  event a second, a frame at ×3600 carries ~58 events and a one-second stall
  at that speed would carry 3600. The per-frame cap (four frames' worth of
  machine time, wall time beyond it lost) keeps the ordinary case well inside
  the limit; the acceptance drives the refusal deliberately at ×100000 and
  asserts that it pauses and reports ONCE.

- **Left as a limit rather than worked around.** A maker's remedy is a lower
  speed. Producer-side if it is ever to change: the machine would have to
  publish something it does not — an event rate, or a `max_crossings` a
  consumer could reason about per second rather than per request.

# The drawn instruction (2026-09-17, `play-the-instruction`, ADR-064)

Three findings met while giving a clocked root's declared instructions a
runtime meaning (machinome ADR-129), recorded HERE rather than only in the
change's own `evidence.md` — which holds each one's full text — for the same
exception the entries above name: none belongs to a viewer cycle to fix. One
is this package's own but is NOT this cycle's surface, one is the PRODUCER's,
and one is a property of the host the measurement ran on rather than of any
change in it. **Status: recorded; triage the pilot's.**

**One wart above is CLOSED by this cycle and is not carried forward.** "What
an instruction MEANS under a clocked root", open under both `execute-the-commit`
and `run-the-clock`, is answered: machinome ADR-129 decided that an
instruction under a clocked root is ONE REQUEST over the ONE driver it names,
with the declared duration saying how long a consumer draws the transition,
and this cycle implements it — the buttons are pressable, a press is drawn,
and an instruction this build could not play is refused at load. The two
identity findings and the load-sensitive cost floors are carried forward
unchanged and are not restated (this cycle moved no floor).

## `dispose()` does not remove the clocked panel

- **Symptom.** Mounting a widget twice on one host element leaves TWO clocked
  panels stacked, the older one reading a bank nothing updates. It bit this
  cycle's screenshots, which now clear the host before mounting.

- **Cause.** Pre-existing and ADR-062's: `dispose()` removes `driverChrome`
  and `runChrome` and never `clockedChrome`. The clocked panel was added as a
  third chrome and the teardown was not extended with it.

- **Not this cycle's surface.** `play-the-instruction` changes what the panel's
  instruction rows DO; it does not own the mount lifecycle, and fixing teardown
  inside it would have been a second change riding on a cycle's evidence.
  Nothing here works around it: the acceptance clears the host, which is what
  any host remounting a widget would do anyway.

- **Cheap to fix when the pilot wants it**: one removal beside the two that
  already run, red-first against a double mount.

## A machine's identity does not cover its instruction table

- **Symptom.** A clocked root that GAINS declared instructions publishes the
  same `clocked.identity` as before. A snapshot taken against the old export
  restores into the new one, although pressing a button on the new one makes a
  request the old machine had no name for.

- **Evidence.** The acceptance fixture re-exported from the producer's own
  `tests/clocked_project/calculator.py:Calculator` at `2ab9505`, which now
  declares `'Stroke'` and `'Set four'`, publishes the UNCHANGED identity
  `979b1a0e…`; the two exports differ in the `instructions` key and in the
  `mtime` fields alone, and both meshes are byte for byte identical.
  `Clocked.described` does not hash the instruction table.

- **Producer-side, and smaller than it looks.** An instruction is one request
  over a declared driver, so a bank restored across the difference is still a
  bank of the same drivers and states — the identity guards what a bank MEANS,
  and that has not changed. It is recorded because ADR-128 §13's promise is
  about what the identity covers, and this is a published field it does not.
  It sits beside the identity finding this file already records (a machine's
  identity is not a function of the machine).

## The Curta's clocked page renders at 3 fps IDLE on this host

- **Symptom.** The measurement of a drawn stroke on
  `Calculators/Curta-Type-I-3x`'s own clocked build reports **3.0 fps before
  anything is drawn**, and 2.0 fps while drawing.

- **Cause: the rasteriser, not the pose.** Headless Chromium on `swiftshader`
  software rendering, with 54 MB of meshes in the page. The measurement takes
  an IDLE phase on the same page first precisely so the two can be told apart:
  a frame of the DRAWING costs **9.20 ms** more than a frame of that idle page,
  against **9.50 ms** for the posed `fast_curta`'s ramp in the same session —
  so the clocked pose is not more expensive than the posed one, and both are
  inside a 60 Hz budget. For a document this host can render at 60 Hz, the
  committed calculator acceptance draws 120 frames over 2.02 s (59.4 fps) with
  a per-frame pose median of 0.40 ms.

- **Recorded rather than explained away.** The number on a machine with a GPU
  is not known from here, and no claim in ADR-064 rests on the page's own
  frame rate. What it means in practice: a per-frame FPS figure measured in
  this repository's headless harness is a figure about the harness, and a
  claim about how a document FEELS needs hardware the pilot has.

- **2026-09-17, `draw-at-the-declared-tempo`: this is now the BINDING limit on
  the Curta measurement.** With a gesture drawn at the document's declared
  tempo, the pilot's nudge of a whole turn went from 1 frame (`[0, 360]`, the
  teleport) to 3 frames over 2.21 s on this host — but the thing the pilot is
  watching, a one-tooth digit advance, is 11.25 of 360 degrees, which at 2.2
  fps is **0.09 of a frame**. No rule can draw a 3% band of a stroke on a page
  that renders three times in it. The same rule on the calculator fixture,
  which this host DOES render at 60 fps, gives the stroke 121 frames and the
  passage 3.8. Where the Curta harness needs the RULE measured without the
  rasteriser in the way, it hands the animation loop timestamps at a stated
  spacing (`FREEZE`'s `stride`): at a simulated 20 fps, 100 ms into the same
  nudge, the crank stood at 180 degrees before the change and 18 after.

## The clocked nudge AMOUNT reaches a row's buttons only at the next rebuild

**CLOSED 2026-09-17 at the orchestrator's review of `draw-every-request`:** the
amount box is now built before the `±` buttons and a press reads the amount
the box holds at that instant (falling back to the remembered one), so the
first press after typing 360 moves 360. The finding below is kept as its
record.

- **Symptom.** A maker types `360` into a clocked row's amount box and presses
  `+`. The machine moves **1 degree**. The next press moves 360. It is the
  pilot's own sequence on the Curta — the one that project's record prescribes
  (`simulation/docs/clocked-curta-2026-09-17.md:42`) — and it was measured
  while writing `draw-every-request`'s acceptance:
  `the first press after setting the amount moved to 1 (moved 1 deg)`.

- **Cause.** `setNudge` writes `clockedNudge[id]` and rebuilds nothing, while
  the `±` buttons of a built row carry `control.nudge` — the amount the panel
  was BUILT with (`viewer.ts:3446-3455`). The setting therefore reaches the
  button only at the next rebuild, which any request performs, so the second
  press is correct and the first is not. The RUNNING chrome does not have this:
  its amount lives in a live closure its nudge button reads
  (`viewer.ts:4038-4048`).

- **Pre-existing**, ADR-062's, and untouched by ADR-064 and ADR-065 — it is a
  SETTING that does not reach a control, not a request that does the wrong
  thing. It is more visible now that the gesture is drawn: a maker watches a
  one-degree transition and reads `moved 1 deg`.

- **Not worked around silently.** Both new harnesses ARM the amount with a
  reset — the rebuild the setting needs — and the acceptance records the
  stale press rather than skipping it.

- **Cheap to fix when the pilot wants it**: `setNudge` rebuilding the panel, or
  the row reading the setting at click time, red-first against "type an amount
  and press once".

## A value committed with the field still focused loses the field

- **Symptom.** A maker types a value into a clocked handle's number field and
  presses Enter. The request is made, and the element they typed into is gone:
  `document.activeElement` is the body a moment later, and the new field
  follows the drawing rather than keeping what was typed (measured at `30.06`
  one frame after a commit of 360).

- **Cause.** Every clocked request rebuilds the whole panel
  (`rebuildClockedChrome`), which removes the focused `<input>` and builds a
  new one. The focus guard that protects a control a maker is editing
  (`viewer.ts:3502`) can only protect an element that still exists.

- **What is still true.** The requirement's clause is met and reachable: a
  maker whose cursor is in a field WHILE a drawing runs keeps what they typed,
  pinned by `test_calculator_document.py`'s section 5, where `42` survives
  twelve frames of a whole turn. What the guard does NOT protect is the field
  a value was committed FROM. `draw-every-request`'s design said otherwise in
  its open item 3 and was wrong.

- **It is the rebuild, not the drawing.** The same rebuild also destroys
  selection and scroll position on every request, and ADR-064 already chose a
  narrow per-frame writer over a per-frame rebuild for exactly that reason.
  The per-REQUEST rebuild is what remains, and shrinking it is its own cycle.
