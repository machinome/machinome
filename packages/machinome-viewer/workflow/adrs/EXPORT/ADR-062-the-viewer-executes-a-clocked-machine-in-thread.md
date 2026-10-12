# ADR-062: The viewer executes a clocked machine in thread, and a declared stop clips the request before any event

**Status:** Accepted

**Date:** 2026-09-17

**Change:** `execute-the-commit`

**Extends:**
- [ADR-045: The run executes in a worker and the main thread only poses](ADR-045-the-run-executes-in-a-worker.md)
- [ADR-047: The corpus is what makes the two runtimes one algorithm](ADR-047-the-corpus-makes-the-two-runtimes-one-algorithm.md)

**Builds on:**
- [ADR-054: A constraint is derived from the published document, never published](ADR-054-a-constraint-is-derived-from-the-published-document.md)
- [ADR-057: A self-read edge is executed from the retained value, piece by piece](ADR-057-a-self-read-edge-is-executed-from-the-retained-value.md)
- [ADR-058: A block is ordered per piece from the published edges](ADR-058-a-block-is-ordered-per-piece-from-the-published-edges.md)
- [ADR-060: Only what moves along a step's path is walked](ADR-060-only-what-moves-along-a-step-s-path-is-walked.md)
- [ADR-061: A kink is a cut in the viewer too](ADR-061-a-kink-is-a-cut-in-the-viewer-too.md)

**Consumes:**
- solid-node ADR-125: a machine may declare a `State` and commit it at an event
- solid-node ADR-126: a bound stops the request
- solid-node ADR-128: the clocked machine is published as document version 8

## Context

solid-node's ADR-125 gave the framework a third state discipline — a
machine with MEMORY and no cadence: a few retained values, closed-form
positions between events, and a COMMIT of the retained values at each
event. ADR-126 gave it interlocks, ADR-127 a clock, and ADR-128 published
the whole of it as **document version 8**: a `states` table beside
`drivers`, and a `clocked` object carrying the compiled machine — its
`identity`, its `clock`, its reserved own-name, its `commits`, its
`bounds` and its two `limits` — with an EXACT conformance corpus,
`tests/clocked-corpus.json`, whose `"tolerance": {"float": 0.0}` is a
field of the file rather than a convention of its reader.

This viewer rendered versions 1–7 and refused version 8 by name, which
was correct and was the only thing between a clocked machine and a
browser. The originating project is the Curta
(`projects/Calculators/Curta-Type-I-3x`), whose RUNNING model costs
**40.52 / 42.31 / 43.70 ms per crank tick** on ADR-060's own bench, a
figure ADR-061 measured again and did not move. The clocked model exists
to beat that and was worth nothing to its pilot until a browser could
crank it.

**The interlocks had to come with the commit, and the corpus is why.**
Measured on the file: 13 of its 30 machines declare a `clocked.bounds`
entry and they carry 36 of the 76 steps, the Curta-shaped `Calculator`
among them. A build that skipped the clip would not merely lose the stop
report — it would locate events on a path the machine never travels. The
producer's own follow-up commit (`1a959d3`, one past the design's
`2d2dc2b`, corpus byte-identical, md5 `852b86b804ebd785f6e6b1f5568fb01a`)
added one more refusal while this cycle was written, and this build
implements it: a non-finite commit refuses the request rather than
banking it.

## Decision

**A clocked machine is a SECOND executor — a pure, synchronous library
beside the run — and every request is CLIPPED by the declared stops
before a single event is located.**

### The document

- `RENDERED_VERSIONS` becomes `[1 … 8]` and `package.json`'s
  `solidNodeDocumentVersions` with it; the declared widget API version
  rises **16 → 17**, because executing a clocked machine is a capability
  a host may require before mounting. `RELEASED_DOCUMENT_VERSIONS` stays
  `[1, 2, 3, 4]`.
- A version 8 document is read and refused FIELD BY FIELD on the surface
  `loadProgram` already refuses a program on: the `states` table as a
  second driver table with ids disjoint from `drivers`, and the `clocked`
  object's six keys. A document declaring version 8 without a `clocked`
  object is refused; a document carrying BOTH `program` and `clocked` is
  two machines and is refused.
- **The bank's id order is DERIVED**, because ADR-128 publishes no
  `coordinates` table: the `drivers` table's key order, then `states`',
  then the clock name when `clock` is not `null`. Both tables are
  published sorted, so the order is deterministic for a document and
  stable across republication; it is what a host reads on the handle and
  what a snapshot serializes in.

### The executor

- `src/clocked/` — `document.ts` (reading and refusing), `machine.ts`
  (bank, request, session), `events.ts` (locating), `commit.ts`
  (writing), `bounds.ts` (the clip, the stops and the end-of-request
  judgement) — is a pure synchronous library with no DOM, no three.js and
  no `postMessage`, called directly from `viewer.ts` on the MAIN THREAD.
  A run is a cadence and belongs in a worker (ADR-045); a clocked request
  is one gesture → one solve → one pose, and a worker would add a
  structured-clone round trip and a task hop to every gesture. The
  decision is falsifiable and is measured in a real page below.
- What it SHARES with the run is the level of the primitives, not the
  level of the executor — the framework drew the same boundary between
  `clocked.py` and `program.py`. Three pieces of `src/run/` were
  extracted for it, each with the running corpus as its gate:
  `farSideOf` lifted out of `Walk.farSide` as a free function with a
  `scale` argument defaulting to 0 (the framework's own extraction, so
  the clocked caller passes the SEGMENT — ADR-128 closure 2 — and no
  running landing moves); `planPartition` split out of `planCuts` with
  `branchesAt` exported; and `PathHost` extracted from `LoadedProgram`,
  which now `extends` it, so the partition helpers take the narrow
  surface a `LoadedMachine` can present.
- **The event solve mirrors `Committing.next_event` step for step**: only
  the `commits` entries whose `shapes` names the moving input are
  examined; an `affine` level is solved by one division and a `kinked`
  one is cut at its own `abs`/`min`/`max` breakpoints through ADR-061's
  `kinkBreaks`, folded under `limits.crossing_tolerance`; the path's own
  opening surface is kept only when the branch at the next representable
  value the path reaches DIFFERS (closure 1's containment rule, read
  through `nextAfter`); the landing is the far-side bit walk; a landing
  beyond the request's endpoint belongs to the next request; only RISING
  steps fire, read AT the landing; the earliest crossing wins and TIES
  ARE IDENTITY of the landing float, never a tolerance; every firing
  relation reads the PRE-EVENT bank with the input at the landing; two
  answers for one id at one landing refuse the request; targets take
  their results together, the input takes the landing, and the solve
  resumes from there. `shapes` is READ and never re-derived — a value
  that is neither `affine` nor `kinked` is refused.
- **The commit is one expression evaluation over the interned DAG the
  pose already uses.** A law's result is coerced once with `Number(…)`,
  because a comparison evaluates to a boolean here and to `bool` in
  Python and both coerce identically under `*` and `+`; a non-numeric
  result refuses. An `int` target is rounded ONCE, half to EVEN —
  `Math.round` is wrong here — and `halfToEven` is Python-exact, checked
  value by value against the framework's `round`. A NON-FINITE commit
  refuses the whole request by name.
- **A REQUEST's `by`/`to` are DESIGN units and the bank is NATIVE.** The
  conversion is `Driver.native`'s: divide by `scale`, round an `int`
  driver once by the same half-to-even, report the admitted travel back
  multiplied by `scale`.

### The clip

- Per `bounds` entry whose `shapes` NAMES the moving input: the published
  chain is evaluated over the bank at the request's START and held under
  the machine's reserved own-name for the whole request; the bound is
  evaluated with it; the LEVEL is the consumer's own subtraction
  (`value − bound` high, `bound − value` low — publishing it would
  publish the bound twice); the threshold is `h = max(0, g(0))`; the path
  is partitioned at the level's own jump surfaces through the published
  `plan` with each piece's branches read at its MIDPOINT; each piece is
  solved by its published classification, which for a bound admits
  `constant` as well as `affine` and `kinked`.
- A crossing at fraction `0.0` admits ZERO travel, said OFF THE CROSSING
  and never left to the walk; otherwise the landing is the SAME far-side
  walk run BACKWARDS, so it lands on the last value that still satisfies.
  An event lands beyond its surface because the path reached it; a stop
  lands short of it because that is where the machine still is.
- The EARLIEST fraction across every constraint truncates `delta` BEFORE
  the first event is located, and every constraint landing on that value
  reports a `Stop` — coordinate, side, bound and value as the chain gives
  them at the landing, the input's value there, and the fraction, whose
  SIGN is part of the contract (`Standing`'s recorded `-0.0`). **A
  request stopped at zero travel is ADMITTED with its stop**: an
  interlock that holds is the machine working.
- After the last event and BEFORE the pose, every constraint is judged
  again over the FINAL bank with the own-name still at the request's
  starting value: a COMMIT that carried a coordinate out of range refuses
  the whole request by name. **The viewer needs no MARK** — the
  framework's `clocked_marking` exists because its pose re-judges bounds
  by enumeration; this viewer's pose is expression evaluation over the
  bank and judges no bound at all, so the clocked executor is the sole
  authority by construction.
- The clip is read ONCE per request. `Gate`'s `move('crank', by=1000)` is
  therefore clipped against the CLOSED gate and admits 300, where 200
  then 800 commits the opening first and admits all 1000 — ADR-126's own
  consequence, kept and pinned rather than smoothed.

### The clock, the timeline and the capture

- The clock STANDS. An elapsed document loads, poses, animates and takes
  every request on its ordinary drivers; only `move('time', …)` is
  refused, by name, at the GESTURE and not at the load, because a clock
  that stands renders TRUTHFULLY — the initial bank is a real instant of
  the machine. Cycle 6 turns that refusal into a request.
- `$t` sweeps while the bank stands: a version 8 document publishes the
  ordinary `animation` object, so the clocked pose scope is `poseScope`'s
  with `time` taking the playback's `$t` rather than the fixed `0` a
  running document poses at.
- That splits a question `capture.py` had been asking with one predicate.
  `carries_program` read `version >= 5` as "carries a program, and
  therefore has no animation instant", which refused `--time` on a
  version 8 document that DOES animate. It is now two predicates —
  `carries_clocked` and `animates_time` — so a clocked staging is
  photographed at its INITIAL BANK and a non-zero `--time` is honoured.

### Refusals, the session and the chrome

- Every clocked error carries an explicit `kind` mapping onto the four
  the corpus records — `TooManyEvents`, `ClockedError` (the conflict, and
  now the non-finite commit), `JointRangeError` (the end-of-request
  judgement) and `ValueError` (a request the machine has no meaning for,
  the clock request included) — and the replay asserts the kind and that
  the message CONTAINS each qualified name, never the prose. Every
  refusal leaves the bank, the tree and the pose standing: the request is
  computed over a working copy and assigned only after the pose is
  accepted.
- `snapshot()` / `restore()` / `reset()` are session-local, and the
  document's `identity` guards a restored bank against another machine.
- `src/clockedControls.ts` is a THIRD chrome, pure data exactly as
  `runControls.ts` is. A DRIVER is a handle — a clocked driver is
  positional again, so the slider `runControls.ts` refuses comes back
  where a `range` is declared — and every gesture is ONE
  `move(id, {to})` whose outcome is reported where it was made: the
  admitted travel, the STOPS that held it, or the refusal's own message.
  A STATE is a follow-only readout and never a handle; so is a clock.
  Declared instructions are LISTED and DISABLED, because ADR-128 §14
  publishes the table and gives it no runtime meaning. There is no
  transport: there is no cadence to run, step or speed.

## Consequences

**All 30 corpus machines load and 68 of the 76 steps replay BIT FOR
BIT**, with `toBe` and `tolerance.float` read from the file — 652 of the
722 recorded numbers: whole banks, admitted travels, commits with their
landings and targets, stops with their bounds and fractions, and three of
the corpus's four recorded refusals by kind and by every qualified name
their messages carry (`Counter` 6 `TooManyEvents`, `Conflict` 0
`ClockedError`, `Shut` 0 `JointRangeError`). **No operation was widened
and no corpus value was edited.** The 8 remaining steps are the CLOCK's:
three clock requests this build refuses where the corpus records them
admitted — asserted as a DEPARTURE, by kind and by name — and five steps
standing downstream of them, asserted SKIPPED-BY-NAME. A CENSUS test
derives that partition from the file (a departure is a `move` whose input
is that machine's own `clocked.clock`) and pins **76 = 68 + 3 + 5** and
30 = 30, so a regenerated corpus cannot narrow the suite by accident; a
31st machine written into the file turns six cases red.

**The running side did not move one bit through the extraction, and that
was measured before a line of clocked code was written.** A scratch
harness replayed all 20 running-corpus scenarios and wrote every number
the engine produced at full round-trip precision — 1 988 lines of banks,
crossings, stops and admitted travels — against `HEAD`'s `jumps.ts` and
then against the extracted one: md5 `f6bb20782b1a27c6c1ab7504811588e6`
both times, `diff` empty. `running-corpus`, `run`, `jumps` and `edges`:
180 tests green.

**A request costs a fraction of a frame, in thread and in a real page.**
Three runs each, node v24.11.1, numbers printed by the tests themselves:

| `Calculator`, in thread | ms |
| --- | --- |
| one stroke (`crank` by 360) | 6.76 / 1.20 / 0.95 |
| one clearing sweep (`ring` by 500) | 1.69 / 1.79 / 1.43 |
| one CLIPPED selector move | 0.97 / 0.29 / 0.26 |
| `Counter`, per EVENT | 0.054 / 0.036 / 0.033 |
| the whole corpus, 76 steps over 30 machines | 13.6 |

| `Calculator`, in Chromium | ms |
| --- | --- |
| one stroke, SOLVE AND POSE | 0.40 / 0.20 / 0.20 |
| one CLIPPED selector move | 0.20 / 0.30 / 0.10 |
| one clearing sweep | 0.70 / 0.30 / 0.30 |
| the POSE alone (a `restore`) | 0.10 / 0.10 / 0.00 |

Each page number is asserted under one 16 ms frame budget, which is what
makes the main-thread decision falsifiable; none comes within two orders
of magnitude of it. Held against ADR-060's own bench for the operating
Curta — **40.52 / 42.31 / 43.70 ms per crank TICK**, idle 9.52 / 9.57 /
9.86, unmoved by ADR-061 — the clocked side's widest gesture costs ≈1 ms
in thread and ≈0.2 ms in the page. **The comparison's two limits are
printed in the test itself and are stated here too**: it is
FIXTURE-to-PROJECT, because the Curta's own clocked model does not exist
yet and the clocked side is `Calculator`'s four wheels rather than the
Curta's seventeen; and a running TICK is not a clocked REQUEST, because a
running crank turn is a sequence of 1/240-second ticks at ≈40 ms each
while a clocked crank turn is ONE request. The claim is the RATIO on one
host.

**A version 8 model with geometry is operated in a real page.**
`tests/fixtures/calculator/` is the framework's own
`tests/clocked_project/calculator.py:Calculator` exported verbatim from a
throwaway copy of solid-node (15 000 bytes, md5
`0884b61fe1ee8c8a79b0d4b78b28767a`, six commits, three bounds), and
`solid export` warned for a version the installed bundle did not read
exactly as ADR-128 §15 says, which is why the fixture can exist at all.
In Chromium it opens at the initial bank; `operand → 4` admits 3; 1100°
of crank fires three strokes and the dials read 2, 1, 0, 0; `setting` by
1 with the crank off rest admits **0.0** with the freeze's stop reported
at the control and the knob visibly still; −30° of crank admits −2.0 on
the ratchet's last seated tooth; `ring` by 500° clears the dials; an
undeclared input leaves every dial where it was. Two screenshots are kept
as evidence.

**Nothing of the run changed.** Versions 1–7 load, pose, animate, drive
and run exactly as they did; `run()` is untouched and stays `null` for a
version 8 document, the worker is untouched, `RELEASED_DOCUMENT_VERSIONS`
does not move, and nothing of the framework, of another checkout or of
the document's shape was altered. The clocked branch is entered only when
a document declares version 8 or carries a `clocked` object.

**Seven findings came out of the mirror; each is recorded and none was
worked around.**

- **F1 — the corpus does not discriminate `farSideOf`'s `scale` on the
  clocked side.** Dropping the segment scale in BOTH clocked callers
  leaves all 104 clocked tests green, because the clip says the
  zero-travel case OFF the crossing (closure 1) and so masks closure 2 on
  every corpus fixture. The behaviour is pinned instead by a direct unit
  test of `farSideOf` in both directions. Presumably true of the
  framework's own suite: recorded as a follow-up for the producer's
  corpus, not mended here.
- **F2 — a machine's identity is not a function of the machine.**
  `Clocked.described` opens with the class's MODULE PATH, so the same
  class exported two ways gets two identities: the corpus's `Calculator`
  is `6eb8e577…` and the `solid export` fixture `979b1a0e…`, with EVERY
  other field of both `clocked` objects byte-identical. A snapshot taken
  against one export is refused against the other, which is not what
  ADR-128 §13 means. Producer-side, for the pilot; the same shape ADR-057
  already recorded for a running program's `identity`, and shared with
  `Program.described`. Nothing here works around it; the fixture's README
  records both strings.
- **F3 — a published `bound` may be a NUMBER**, as ADR-128 §7 says and
  the first loader did not. A numeric bound becomes its own literal text
  so the level is one expression, and the literal is CHECKED to read back
  as the same double; one that cannot is refused rather than clipped
  against a value the document did not state.
- **F4 — a real document's BINDINGS table names the reserved own-name.**
  No corpus document does; the acceptance fixture publishes two such
  entries, and only the page found it. `assertRenderable` now admits
  `machine.own` in a BINDINGS ENTRY, beside a plan's placeholders, and
  still refuses it reached from an OPERATION.
- **F5 — the clocked limits carry no sampling resolution.**
  `subdivisions`, `bisectionRounds` and `agreement` are NaN on a clocked
  host, because inventing a number would publish a resolution the
  document never stated. It is safe because every published clocked shape
  is `constant`, `affine` or `kinked` and anything else is refused at
  load — asserted over all 30 machines.
- **F6 — the framework's `_leveled` is narrower than the run's
  `levelOf`**, refusing a non-finite level only for `floor`, `ceil` and
  `%`. The clocked module mirrors the framework; the running side is
  untouched.
- **F7 — `move('time', …)` on a machine that declares NO clock** meets
  the ordinary undeclared-input refusal: same kind, different prose,
  because the document publishes `clock: null` and never the reserved
  word. The corpus pins neither.

**A harness finding worth carrying: the bundler's JSON import destroys
`-0`.** `Standing`'s recorded stop fraction IS `-0.0`, and
`JSON.stringify` turns it into `0`. Every clocked suite therefore reads
the corpus BYTES with `readFileSync` + `JSON.parse`, which preserves it,
as `Response.json()` does for a real document in a browser.

**Two notation slips in the ratified text were recorded rather than
silently applied**, and neither is a change of rule. Design §14 lists
`-0.5 → -0` for `halfToEven`; Python's `round` returns an INT, which has
no signed zero, so `round(-0.5)` is `0` and the same task names that
cross-check as the authority — the implementation is Python-exact and a
test pins that `Object.is(halfToEven(-0.5), -0)` is false while
`Object.is(Math.round(-0.5), -0)` is true. Task 6.5 says `Calculator`'s
`halved` walks "2, 2, 4, 4, 6"; the corpus's own `move('feed', by=350)`
records THREE commits, `2, 2, 4`, and the corpus is the authority. A
third, in §8's rejected-alternative prose: an unclipped build does not
"admit 1.0" on `Calculator` step 2, it refuses the whole request at the
end-of-request judgement — the design's own conclusion, sharper.

**One transient suite failure is reported unreproduced.** One full
`npx vitest run` of six reported `1 failed | 1138 passed` without the run
being captured; five consecutive runs around it and three of the cost
file alone are clean. The only load-sensitive assertions in this cycle
are the design's own cost floors — 4 ms against a measured 0.26–0.95 ms —
left at the ratified number rather than quietly widened, and recorded so
the pilot knows which assertion can be made to fail by load alone.

**A host at API 16 and a producer at version 8 disagree silently unless
the host checks.** That is what `documentVersions` is for, and `describe`
reports it — which is also how the producer's export warning named this
refusal while it stood.

**What is left to the next cycle**: the CLOCK — a request that advances
elapsed seconds, the events on it, and the playback of an elapsed base —
which turns all eight departed and deferred corpus steps into ordinary
replayed ones; and the PRIMARY checkout's bundle rebuild.

## Alternatives considered

- **Widen `Run` instead of writing a second executor.** `Run` integrates
  a tick — `dt`, commands with durations and rates, spans, stops, a
  trajectory ring — and a clocked root refuses every one of those names.
  Widening it would carry them into a machine that must refuse them and
  would put the running corpus and the clocked corpus through one code
  path where each is meant to pin a different algorithm.
- **Execute the clocked solve in the worker, as the run does.** A run is
  a cadence and a request is a gesture; a worker would make a drag
  asynchronous — a slider at 60 Hz would have to queue and coalesce
  replies to keep its order — for a computation the clocked discipline
  exists to make cheap. A worker remains a decoder away, because the
  solver is a pure library.
- **Read the bounds, validate them, and REFUSE a bounded document by name
  for one cycle.** This repository's established posture for a shape it
  cannot execute, and this proposal's first shape. Rejected because the
  refusal would be lifted by the very next cycle while costing this one
  its acceptance fixture, its speed number and half its corpus — and
  because "version 8 is read, except when it is not" is a half-state in a
  permanent record with no lasting reason behind it.
- **Execute a bounded document UNCLIPPED.** Not a smaller version of the
  clip but a wrong render: events would be located on a path the machine
  never travels. Measured — with the clip disabled, 9 of the 13 bounded
  machines are red.
- **Clip the bounded COORDINATE and let the driver run on.** ADR-108's
  clamp, refused there for the reason that holds here: the group's other
  coordinates would stand where an unstopped request put them.
- **Re-compute the clip after each commit.** ADR-126's own rejected
  alternative: the clocked quantum is the REQUEST, and `Gate` is the
  fixture that shows the difference.
- **Re-derive `shapes` rather than reading them.** ADR-128 publishes the
  classification precisely so a consumer does not; a consumer that
  classified a level differently would cut a kinked path differently and
  land on a different float.
- **Split engine and chrome into two cycles**, as ADR-045 and ADR-048
  split the run. Rejected: `machine()` without a panel is a capability no
  maker can reach, and the API version would have to rise twice for one
  document version.

## Review (2026-09-17)

Accepted at the cycle's adversarial review with no closure. The reviewer
re-ran `npx tsc --noEmit` (clean), the clocked suites and the running
corpus (161 passed), checked the implementation against the producer's
`clocked.py` at the sensitive sites, and accepted the two recorded
notation corrections as recorded rather than folded into the ratified
design. F2 is referred to the pilot as a producer-side question shared
with `Program.described`; F1 is referred to the framework's corpus as a
follow-up; the transient vitest failure stands as unreproduced.
