Every task below is RED FIRST: the test is written, run, and seen to fail
for the stated reason before the change that turns it green. Neither commit
is made until its whole group is green. Both fixtures are geometry-free — no
CAD build, no `meshes = True` — and every run uses
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, ONE JOB AT A TIME:
`/home/asa/devel` is a virtiofs mount whose host daemon exhausts file
descriptors under parallel load, and the symptom is an intermittent "Too many
open files" from git, `ls` or a Python import, never a broken venv.

Run everything from inside this worktree with
`PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python`, so
the worktree's package is imported and not the installed one.

## 1. Fixtures

- [ ] 1.1 Add `tests/clocked_project/` with the REGISTER fixture: a `Counter`
  root declaring `crank = Driver(default=0, unit='deg')`, `units` and `tens`
  as `State(default=0, range=(0, 9), dtype=int)`, two dial children each with
  a `Revolute`, one committing relation
  `(crank & units & tens).commits((units, tens), at=strokes, law=advance)`
  with `strokes` returning `floor(crank / 360)` and `advance` returning
  `((units + 1) % 10, (tens + (units == 9)) % 10)`, and two ordinary
  `drives` relations posing each dial from its state. No geometry beyond a
  cylinder per dial. Expected values are computed BY HAND in every test,
  never by calling the law.
- [ ] 1.2 Add the CLEARING fixture beside it, Curta-shaped and tiny: a root
  with a `ring` driver and a `dial` CHILD that declares `digit = State(...)`,
  with the committing relation stated on the ROOT and naming its target
  through the path `dial.digit` — so the fixture proves a state declared on a
  child and reached by a path, which is the Curta's own shape. `at` and `law`
  read that digit:
  `at = ring >= START + PITCH * (10 - dial.digit)` and
  `law = dial.digit * (ring < START + PITCH * (10 - dial.digit))` — the
  source group naming its own target, which is the spike's finding 2 in
  fixture form.
- [ ] 1.3 Add the refusal fixtures: a non-`State` target; one relation
  naming one target twice, by the PATH; `crank.drives(state)`; a state no
  relation targets; a relation no driver can reach; two relations writing
  one state at ONE landing; a port source; a joint-coordinate source; a
  curved `at`
  (`floor(sin(crank))`); a compound `at` (`floor(a) + floor(b)`); an `at`
  that is `crank % 360`; a `commits` with no `at`; a `commits` with
  `ratio=`; a broadcast `commits`; a law returning the wrong number of
  values; an `at`/`law` returning raw text or calling outside
  `SYMBOLIC_BUILTINS`; a `State` under `Time(loop=4)`; a `State` under
  `Time.running()`; a `Driver` and a `State` qualifying to one id.

## 2. The declaration (`State`)

- [ ] 2.1 RED: a test asserting `State(default=0, range=(0, 9), dtype=int)`
  is declarable, readable as `self.units`, and carries the declaration's five
  fields off the class. Fails: no `State`.
- [ ] 2.2 GREEN: `solid_node/simulation/state.py` beside `driver.py` — the
  frozen declaration, its marker in `solid_node/node/qualified.py` beside
  `DriverDeclaration` so the node layer can recognize and qualify it, and the
  lazy export from `solid_node.simulation`.
- [ ] 2.3 RED: enumeration tests — two children of one class declaring a
  state enumerate as `bank_a.digit` and `bank_b.digit`; a driver and a state
  claiming one id are refused naming both.
- [ ] 2.4 GREEN: `qualified_states` / `declared_states` in
  `simulation/enumeration.py`, collected in the `visit` of the walk
  `qualified_declarations` already makes. NO additional tree pass.
- [ ] 2.5 RED: the writer refusals, one test each, asserting the message
  names the state and the offender — `set_state`, an `Instruction` target, a
  `Button`/`Turn`/`Slide` input, `drives` as a driven end, a state nothing
  writes, `Time(loop=)`, `Time.running()`. SEVERAL committing relations
  writing one state are ADMITTED (closure 1, C2).
- [ ] 2.6 GREEN: each refusal at the site that owns its facts, per
  design §2.

## 3. The verb (`commits`)

- [ ] 3.1 RED: the declaration tests — a bare `commits` recorded on the
  class, a named one resolving per instance with both factories called once
  with the realized owners, a source group naming its own target admitted.
  Fails: no `commits`.
- [ ] 3.2 GREEN: `commits` on `CoordinateRef` and `Coordinates` in
  `motion/couplings.py`; a `Commitment` declaration and a `CommitmentRecord`
  built the way `Relation`/`RelationRecord` are; `_law_argument` reused for
  both factories' arguments; `_checked_return` reused for the law's shape.
- [ ] 3.3 RED: the class-definition refusals of 1.3 that belong to the verb
  (non-`State` target, a target named twice by its PATH, port source,
  `ratio=`, broadcast, missing `at`/`law`), and the ADMISSION of two
  relations targeting one state and of two children of one class as two
  targets (closure 1, C1/C2).
- [ ] 3.4 GREEN: those refusals, each naming the relation as written and the
  class that stated it.

## 4. Compiling `at` and `law`

- [ ] 4.1 RED: `at` accepted as one `floor`, one `ceil`, one `sign` and one
  comparison; refused as a compound, as `%`, as bare arithmetic, and as raw
  text or a call outside the vocabulary.
- [ ] 4.2 GREEN: the `at` inspection — `_graph_of`'s walk reused for text and
  vocabulary, plus the one-jump-node structural check, yielding the node's
  level graph and its surfaces through the existing `_Jump`/`_surfaces`.
- [ ] 4.3 RED: a commit law made ENTIRELY of jumps (`floor(crank / 360) % 10`)
  is ADMITTED and commits the value that expression evaluates to — the
  asymmetry with a running law, which refuses that shape as arithmetic.
- [ ] 4.4 GREEN: the law inspection — `_graph_of`'s text and vocabulary
  walk, with NO jump plan, NO skeleton and NO `_only_jumps` refusal, because
  a commit is evaluated at a point.
- [ ] 4.5 RED: a curved `at` is refused AT SIMULATION CONSTRUCTION naming the
  relation, the driver whose motion curves the level, and the primitive.
- [ ] 4.6 GREEN: the classification — the level graph bound with every
  standing source substituted as a number, classified by the existing
  `_shape_of`, one driver at a time over the drivers a request could move.

## 5. The event solver

- [ ] 5.1 RED: a solver unit test over the register fixture's own level —
  one rising crossing located at the hand-computed fraction, a falling
  crossing located and NOT fired, three crossings in one path in order.
- [ ] 5.2 GREEN: `solid_node/simulation/clocked.py` — a CONSUMER of
  `JumpPlan._solved`, `_surfaces`, `_branch_of`, `_KinkCuts` and
  `_MAX_CROSSINGS`. No new locator, no new constant, and NO USE of
  `_CROSSING_TOLERANCE` beyond what `_solved` and `_KinkCuts` already make of
  it internally: the clocked solver adds no tolerance of its own (design §5).
- [ ] 5.3 RED: the landing — a crossing of `floor(crank / 360)` at
  `crank = 360` evaluates the law at exactly `360.0`, and resuming from that
  value does not re-fire the event. The boundary rule asserted directly on a
  representable threshold `T`: `ring > T` lands on `math.nextafter(T, inf)`
  and `ring >= T` lands on `T` itself, each asserted as an exact float.
- [ ] 5.4 GREEN: the landing through the existing `_far_side`/`_ordinal`
  float walk, whose membership test is `_branch_of` at the candidate value
  and never a comparison against the surface (design §5).
- [ ] 5.5 RED: a KINKED level (`floor(max(crank, 0) / 360)`) is SOLVED at its
  breakpoint against a hand-computed fraction, and the breakpoint is not
  reported as an event.
- [ ] 5.6 GREEN: the kink sub-division, `_KinkCuts` reused.
- [ ] 5.7 RED: simultaneity by IDENTITY — two relations whose far-side
  landings are the SAME float are ONE event, both reading the values that
  stood before it, and swapping their two declaration lines changes nothing
  observable; two relations whose surfaces differ by ONE ULP are TWO events
  in path order, the second reading the first's commit. The ulp pair asserted
  identical under `by=3600` and under ten `by=360` requests, which is the
  assertion a travel-scaled tolerance would fail.
- [ ] 5.8 GREEN: the tie merge — equality of the landing float, no tolerance
  — and the synchronous read.
- [ ] 5.9 RED: an event surface that reads its own state MOVES after the
  commit (the clearing fixture: one event on the first sweep, none on the
  second).
- [ ] 5.10 GREEN: re-solving the remaining path from the landing with the new
  bank.
- [ ] 5.11 RED: more events than the crossing maximum is refused committing
  nothing, with the message asserted to name the input and its travel, the
  relation as written, the count reached and the maximum, and to suggest
  splitting the request. A companion test proves the judgement is over the
  events ACTUALLY LOCATED and not an estimate: a level that would cross more
  than the maximum if it kept crossing, but stops partway through the path,
  is ADMITTED.
- [ ] 5.12 GREEN: the bound and its refusal, `_MAX_CROSSINGS` (1000 per
  graph) reused, counted as events are located.

## 6. The clocked `Sim`

- [ ] 6.1 RED: `Sim(node)` over the register fixture constructs, poses once,
  and `sim.state` holds `crank`, `units` and `tens`. `Sim(node, 0.02)` over
  it is refused naming `dt`. `Sim(node)` over a stateless root is refused as
  today.
- [ ] 6.2 GREEN: the constructor split in `sim.py`, entered only when the
  state table is non-empty.
- [ ] 6.3 RED: `sim.move('crank', by=360)` → one event, `units == 1`;
  `by=3600` → ten events, the same bank as ten calls of `by=360`;
  `by=-3600` → no event, the states hold, the crank moves the whole travel,
  the pose follows the crank. `to=` likewise. A request naming a state, a
  joint coordinate, or two inputs is refused by name.
- [ ] 6.4 GREEN: the request path, the `Request`/`Commit` value objects, and
  the ONE binding of the tree at the end of the request.
- [ ] 6.5 RED: atomicity — a law raising on the third event leaves the bank,
  the tree and the record exactly as they were.
- [ ] 6.6 GREEN: staged commit, applied only when the whole request succeeds.
- [ ] 6.7 RED: `state=` accepting a state id; `snapshot`/`restore`/`initial`/
  `reset` carrying the states; `restore` refusing a snapshot from a different
  model before touching anything; `record=N` keeping a bounded ring.
- [ ] 6.8 GREEN: those, on the bank.
- [ ] 6.9 RED: each of `run`, `at`, `every`, `time`, `tick`, `rate`,
  `trigger`, `commands`, `program`, `crossings`, `stops` refused by name on a
  clocked `Sim`.
- [ ] 6.10 GREEN: the refusals, each naming the clocked base.
- [ ] 6.11 RED: a request whose final pose violates a joint `range` raises
  `JointRangeError` on that pose, and a `Bound` with reads is judged at the
  close of the enumeration, both unchanged from today. Amended by closure 1
  (C3): the request is REFUSED WHOLE — the bank, the tree and the record
  stand as they were — and the recorded cycle-2 gap is therefore that the
  request is refused rather than CLIPPED at the stop, not that it commits
  half a path.
- [ ] 6.12 GREEN: pose the working bank BEFORE assigning it, re-pose the
  previous bank and re-raise on failure, in `move` and in `restore`; assert
  the existing `JointRangeError` behaviour and reference design §9 and §11.
- [ ] 6.13 RED: UNITS — a state declaring `scale=10` commits the value its
  law returned, unrescaled, and poses at ten times it; an `int` state whose
  law returns `9 - 1e-12` reads exactly `9`, and a float state's reads
  `9 - 1e-12`. The scaled case is RED against any implementation that passes
  a commit through `Driver.native()`, which divides by `scale` a second time
  (design §9).
- [ ] 6.14 GREEN: the commit writes the law's NATIVE return, with a single
  `round()` for a `dtype=int` target and no scale conversion anywhere.
- [ ] 6.15 RED: TIME — a clocked fixture whose `simulate()` reads `self.time`
  poses with the symbolic animation variable, before and after a request;
  `time` is absent from `sim.state`; and the posed expression is identical to
  the same fixture built outside a simulation.
- [ ] 6.16 GREEN: nothing to implement — the clocked pose takes the build
  path's binding, drivers and states only, `time` falling back as it does
  today (design §12). Assert it, and assert that each of `rate`, `commands`
  and `program` is refused on a clocked `Sim` while `move`, `snapshot`,
  `restore`, `reset`, `initial` and `state` are admitted.

## 7. Publication refused

- [ ] 7.1 RED: serializing the register fixture is refused naming `units`,
  `tens` and the missing document version. VERIFY EACH ENTRY POINT at apply,
  one assertion per row, rather than trusting the walk to be universal:
  - refused, and leaving no document and no partial staging behind — `solid
    build` (`core/builder.py:653`), `solid export`
    (`core/export.py:143`), `solid develop` (it serves what the builder
    publishes), and `solid snapshot --renderer web`
    (`viewers/browser.py:_stage`, which reaches `document_body` WITHOUT
    entering `symbolic_document` — this is the row that decides where the
    gate goes);
  - untouched — `render()`, `assemble()`, `build_stls()`, `solid test`, and
    `solid snapshot` with the OpenSCAD renderer, which builds no document
    (`manager/snapshot.py:215`). If the OpenSCAD path turns out to need a
    document after all, it is refused too and this task records that instead.
  - The shop hub reaches publication by spawning `solid build`, so it needs
    no framework-side case; confirm that at apply and record it.
  - A stateless fixture's document stays byte-identical to its recorded
    bytes.
- [ ] 7.2 GREEN: the refusal in `core/serializer.py`, placed in
  `document_body` — the one function all four producers pass through — with a
  second, earlier raise in `symbolic_document` only if apply finds a producer
  that would otherwise bind symbolically before reaching it (design §10).

## 8. Zero behaviour change

- [ ] 8.1 RED: a counter on the clocked collector asserted ZERO for a driven,
  stateless model constructed, posed, stepped with `Sim(node, dt)` and
  published.
- [ ] 8.2 GREEN: the guard — clocked paths entered only on a non-empty state
  table, states collected in the existing walk, exports left lazy.
- [ ] 8.3 The whole existing suite green, including the running fixtures and
  `tests/running-corpus.json`, with no fixture edited and no expected value
  changed.

## 9. Measurement

- [ ] 9.1 Measure on the two fixtures ONLY and record in `evidence.md`:
  seconds per request with no event, seconds per event, seconds per pose, and
  a stateless fixture's pose cost before and after. Claim nothing about the
  Curta; the spike's factor of 35 is the project's measurement and is cited,
  not reproduced.

## 9b. Closure 1 (2026-09-17): the orchestrator's four review findings

The review probed the implementation with a Curta-shaped register — three
wheels of one class, carry, per-digit clearing — and found four things. C2
amends the RATIFIED DESIGN, so its planning artifacts were revised FIRST and
re-validated, and only then the implementation, red first. Every red below
is recorded in `evidence.md` under "Closure 1".

- [ ] 9b.1 RED (C1): two children of ONE class each declaring `digit`, one
  relation writing both, one request advancing both — refused today naming
  the SAME relation twice, because the refusal keys on the LOCAL NAME. A
  second test where two children's states are written by two DIFFERENT
  relations. Both must be ADMITTED.
- [ ] 9b.2 RED (C2): one state written by TWO relations at two DIFFERENT
  events — the Curta's stroke and its clearing reach — admitted, each
  firing at its own event; and the CONFLICT: two relations on one input
  whose levels land on the SAME float and both write one state, whose
  request is refused naming the state, both relations and the landing, with
  `sim.state` unchanged.
- [ ] 9b.3 GREEN (C1/C2): drop `declarative._refuse_two_writers` and the
  tree-wide two-writers refusal in `compile_clocked` (keeping "a state
  nothing writes"); refuse the one-event conflict in the request, on the
  target's QUALIFIED ID; keep the "named twice among ONE relation's targets"
  refusal, which already keys on the reference's path.
- [ ] 9b.4 The Curta-shaped `Register` fixture in `tests/clocked_project/`:
  a `crank`, a `ring`, an `operand`, three `Wheel` children of ONE class
  each declaring `digit`, one stroke relation writing all three (carry
  computed BY HAND in the tests) and one clearing relation per wheel
  reading its own digit. Tests: strokes add with carry; a partial sweep
  clears only the wheels it reaches; a reversed sweep un-clears nothing; a
  second sweep fires nothing on a cleared wheel; strokes after clearing
  continue from zero.
- [ ] 9b.5 RED (C3): a request whose FINAL POSE raises `JointRangeError`
  leaves the bank advanced today. It must leave the bank, the tree and the
  record exactly as they were; the same for `restore()`.
- [ ] 9b.6 GREEN (C3): pose the working bank first in `Clocked.move` and
  `Clocked.restore`, assign only on success, re-pose the previous bank and
  re-raise on failure.
- [ ] 9b.7 RED (C4): a committing relation whose sources are ALL states
  compiles today with an empty level table and can never fire. It must be
  refused at simulation construction, by name, saying its event level moves
  with no declared driver.
- [ ] 9b.8 GREEN (C4): the refusal in `_compiled`, beside the curved-level
  one.
- [ ] 9b.9 The five clocked modules green, then the FULL suite once.

## 10. Records

- [ ] 10.1 `docs/scenarios.rst` and `HISTORY.rst`.
- [ ] 10.2 Extract ONE ADR, candidate **ADR-125** (NODE), AFTER implementation
  and tests confirm the final design, per design §15 — including its two
  Consequences that are defined and NOT implemented: the meaning of a `State`
  under `Time.running()`, and that `Time.running()` is untouched. Update
  `docs/adrs/README.md` and `docs/architecture.md` where the synthesis
  changed.
- [ ] 10.3 Amend `workflow/docs/clocked-machine.md` — the requirement note —
  in its own convention: a note is SUPERSEDED by the change cut from it, not
  rewritten as if it had been right. Add to its status line that it was
  "taken up as OpenSpec change `declare-the-state` (ADR-125) on 2026-09-17",
  and add the three corrections the spike and this cycle measured, each
  marked as a correction:
  - its point 5 ("Interlocks are expression bounds") — the spike measured
    that the selector lock is NOT needed for the REGISTER, whose commit law
    reads the settings as they stand at the stroke end; it is needed for the
    POSE, and every mid-stroke action that would break the closed form is one
    the manufacturer's booklet forbids;
  - its candidate spelling's constant `RACK_END[p]` — the measured per-digit
    clearing threshold reads the COMMITTED DIGIT,
    `start_p + pitch_p * (10 - digit_p)`, which is why `at` may read the
    state it commits (design §8);
  - the note's assumption that both edges fire and the law neutralises the
    falling one — measured false (9 → 18); only RISING steps fire, and the
    other edge is written by negating the level (design §6).
- [ ] 10.4 Record in `workflow/warts.md` the follow-ups this cycle names: a
  port as a source of a committing relation, a broadcast `commits`, a
  multi-input request, a direction keyword, an instruction under a clocked
  root, and the fold-commit shape the spike recorded.
- [ ] 10.5 Sync the baseline specs, archive the change, and commit the
  completed implementation record.
