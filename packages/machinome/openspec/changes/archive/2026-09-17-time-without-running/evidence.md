# Evidence: `time-without-running`

Implementation record of cycle 3 of the clocked-machine campaign, worked
in the framework worktree `solid-node/WTs/clocked-machine` on branch
`clocked-machine` over the planning commit `3067e3a` (base `81c5364`).

Every run under `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
PYTHONPATH="$PWD"` with the workspace venv, ONE pytest process at a
time.

## 1. The baseline this cycle must not move (task 1)

- **1.1** The whole suite at `3067e3a`, before a line was written:
  `3183 passed, 4 skipped, 53 warnings, 1754 subtests passed in 324.83s`.
  Slowest call: `test_retained_builder_generation.py::FreshProcessBatchTest
  ::test_cold_twenty_four_artifact_build_uses_one_spawned_builder`,
  34.10 s; the running fixtures' own rows were
  `test_running_simulation.py::RecordingTest::
  test_nothing_is_recorded_by_default` 16.48 s and
  `test_running_jumps.py::CrossingRecordTest::
  test_nothing_is_recorded_by_default` 6.41 s.
- **1.2** `git status --short` was EMPTY at the baseline.
  `md5sum tests/running-corpus.json tests/running_project/*.py`:

      651a3b5750c49eecad4587438dc9a85a  tests/running-corpus.json
      ca007699cc86e3fbf26cd7edb7c83d91  tests/running_project/__init__.py
      5488741d94a58a961b5a5b8bcff7c1b5  tests/running_project/flexible.py
      1ef62a397d766d4c970b0c7d9f2be62a  tests/running_project/machine.py
      5f16e070352c4c505c6b8e53e7c479ba  tests/running_project/parts.py

- **1.3** Every consumer of `declared_time(cls)`, verified against the
  source. Reads `.loop`: `core/serializer.animation_block` (line 437),
  `node/assembly.read_time` (line 692), `manager/snapshot.py` (line 314).
  Compares `.mode` to `'running'`: `core/serializer.running_root` (148),
  `simulation/sim.Sim.__init__` (158, 201, 219),
  `motion/couplings.run_owned` (1072),
  `node/assembly._coordinate_delivery` (336), `manager/snapshot.py` (261,
  315), and `simulation/enumeration._decide_block_membership` (217) --
  **the one site the design did not name**, a pre-pass confined to a
  running root, which an elapsed root skips exactly as an undeclared one
  does. No other site reads either attribute.

## 2. The red log

Each entry is a test written first and SEEN RED, with the failure line as
pytest printed it.

| # | Task | Test | The red |
| --- | --- | --- | --- |
| 1 | 2.1 | `tests/test_time_base.py::ElapsedBase*` (collection) | `AttributeError: type object 'Time' has no attribute 'elapsed'` |
| 2 | 3.1 | `tests/test_clocked_time.py` (collection, through `tests/clocked_project/pendulum.py:163`) | `TypeError: unsupported operand type(s) for &: 'Time' and 'Driver'` |
| 3 | 3.2 | `BankTest::test_the_clock_is_in_the_bank_at_zero` and three more | `TypeError: Regulator declares time = Time.running() and its tree declares the state(s) count. ...` -- the fall-through task 3.2 warned about, an elapsed root handed the RUNNING message |
| 4 | 3.3 | `BankTest::test_a_clocked_root_with_no_base_has_no_clock_in_its_bank` | `AssertionError: 'Time.elapsed()' not found in 'time belongs to a simulation with a CLOCK, and Clockless is CLOCKED: ...'` |
| 5 | 3.4 | `StatelessElapsedTest::test_unbound_time_is_bare_t_...` (a first draft reading `node.bob.time`) | `Exception: Leaf node cannot rely on time, animation should be done on internal nodes.` -- a LEAF may not read the clock at all, so the descendant that proves the delivery is an assembly (`Nested`/`Swinging`) |
| 6 | 5.5 | `EventsOnTheClockTest::test_one_request_fires_the_releases_on_its_path` | `AssertionError: Lists differ: [0.49999999999999994, 1.5] != [0.5, 1.5]` -- see "The landing of a release" below |
| 7 | 5.5 | `EventsOnTheClockTest::test_a_request_crossing_the_maximum_is_refused` | `AssertionError: 'split' not found in "... Split it into shorter requests."` (the assertion's own case) |
| 8 | 6.2 | `ProducerTest::test_the_build_publishes_the_same_snapshot` | `AssertionError: '... "name": "Swing" ...' != '... "name": "Untimed" ...'` -- the root's name is its class's, and nothing else differed |
| 9 | 7.3 | `BoundsAndTheClockTest::test_a_chain_that_carries_the_clock_is_refused_at_construction` | `AssertionError: ClockedError not raised` -- the chain reached compilation carrying `$t` and was admitted |

**Red-first, honestly reported.** Reds 1, 2, 3, 4 and 9 are the design's
own failures, seen before the code that answers them. Reds 5, 6, 7 and 8
are the tests' own assumptions corrected against what the framework
actually does, each recorded above rather than quietly fixed.

Two groups of tests were written AFTER the implementation of their own
task, and this is stated rather than dressed up: the class-definition
refusals of task 5.2 (`ClockAsASourceTest`) and the request refusals of
task 4.2 (`RequestTest`). Their fixture module could not be IMPORTED
until the clock was a legal source (red 2), so the faces of tasks 4.4 and
5.3 had to land in the same pass as the bank of task 3.3. The red that
covers them is red 2, at collection, and the behaviours they asserted
afterwards were not present before it.

## 3. What the implementation is

Files changed:

- `solid_node/motion/ports.py` -- `Time.elapsed()`, built without
  `__init__` as `running()` is; the private `_elapsed` marker (NOT a
  dataclass field, so `loop` stays the one field every producer reads);
  `mode` answering `'elapsed'`; the `TypeError` and the `__set_name__`
  message naming all three spellings; `Time.name = CLOCK_NAME`, so a
  clock answers the question every other declaration answers; the
  `drives`, `commits` and `__and__` faces; `__rand__` on `Coordinate` and
  on `Time`.
- `solid_node/motion/couplings.py` -- `ClockRef`, a source-only
  reference kind refusing either end of `drives` and checked against the
  owner's own declaration; `Time` admitted by `_is_group_member` and by
  `coordinate_ref`; the clock refused as a `commits` TARGET by name; the
  clock refused as a SOURCE under `Time(loop=)` and `Time.running()`,
  naming the base and `Time.elapsed()`; `refuse_left_operand`, the
  reflected mirror of `group_with`'s right-operand refusal, with the
  module sentence; `__rand__` on `CoordinateRef` and `Coordinates`.
- `solid_node/node/qualified.py` -- `__rand__` on `DriverDeclaration`
  (and through it `StateDeclaration`).
- `solid_node/node/declarative.py` -- `__rand__` on `ChildDeclaration`
  and `RepeatDeclaration`.
- `solid_node/simulation/enumeration.py` -- `refuse_states_under_a_clock`
  RETURNS for the elapsed base before the unconditional running refusal,
  which is what keeps the looping and running messages exactly as they
  were.
- `solid_node/simulation/clocked.py` -- `Clocked.clock`; the clock in the
  bank at `0.0` under `CLOCK_NAME`; `_ClockInput`, the seconds-in-
  seconds-out declaration a request reads; the backwards refusal; the
  clock in `compile_clocked`/`_compiled`'s per-input classification loop,
  with the "no request can reach this relation" refusal now naming the
  clock; `Clocked.time`; the clock delivered through `drive_tree`'s
  EXISTING `visit` hook in `Clocked.pose`; `_over_the_bank`, the general
  free-name refusal in `_constrained`.
- `solid_node/simulation/sim.py` -- `sim.time` delegating to the clocked
  executor, which answers under this base and refuses by name under every
  other clocked root.

New tests and fixtures: `tests/clocked_project/pendulum.py`,
`tests/clocked_project/module_clock.py`,
`tests/clocked_project/bare_clock.py`, `tests/test_clocked_time.py`
(46 tests), and ADDED tests only in `tests/test_time_base.py` (10, over
the 34 that stood at `3067e3a`).

**No tool signature was changed.** `drive_tree` gained nothing: the clock
rides its existing `visit` hook, and a root with no clock passes
`visit=None`, asserted by
`PoseDeliveryTest::test_a_model_with_no_clock_enters_the_walk_with_no_visit`.
The one internal signature that grew is `compile_clocked(..., clock=False)`
and `_compiled(..., clock=False)`, both private to `simulation/clocked.py`
and defaulted, so no caller outside it changed.

## 4. Design questions

Recorded rather than silently decided.

### 4.1 `by=40*T` fires EIGHTY events, not forty

`design.md` section 13 and the spec scenario "A request on the clock
fires the events on it" both say a `sim.move('time', by=40 * T)` over the
pendulum fires FORTY events and advances the count by forty. The level
they state -- `floor((time + T/4) / (T/2))` -- rises every `T/2`, twice
per period, which is what puts a release at each of the swing's own
extremes. So `40 * T` seconds hold EIGHTY releases, and the measured
request fires eighty.

The implementation follows the LEVEL, which is the design's normative
part (it is the affine-in-time evidence the whole no-tolerance claim
rests on), and the test asserts both readings: eighty events for
`by=40*T`, and forty for `by=20*T`, each at the hand-computed instants.
**The spec scenario needed its number corrected** -- either to eighty
events for `by=40*T`, or to `by=20*T` for forty. **Decided at the
orchestrator's review: EIGHTY over `by=40*T` is right, the LEVEL being
the design's normative half.** The orchestrator corrected the scenario
"A request on the clock fires the events on it"
(`specs/simulation/spec.md`) and `design.md` section 13 in the working
tree itself, marking the correction in the design text; the
implementation and its tests were already what those now say, and
nothing else in the cycle depended on it.

### 4.2 The landing of a release is one ulp below the ideal instant

The first release's landing is `0.49999999999999994` and not `0.5`, and
this is the landing rule working exactly as ADR-125 states it rather than
a defect: membership of the far side is decided by EVALUATING the level's
own branch, never by comparing a float to the surface. The level adds a
quarter period before it divides, and at the first release
`0.49999999999999994 + 0.5` rounds UP to exactly `1.0`, so the level has
already stepped one representable value below the ideal instant, and that
value IS the nearest representable point of the piece the path enters.

**Decided at the orchestrator's review: recorded, no change.** The
fixture's own tests therefore assert each landing within ONE ulp of
the hand-computed release instant (`assert_releases`), never with a
tolerance in the solver: the SOLVER introduces none, and
`EventsOnTheClockTest::test_no_tolerance_reaches_the_clock` asserts
`_CROSSING_TOLERANCE` appears nowhere in `simulation/clocked.py`. Ten
short requests still equal one long one EXACTLY, instant for instant,
which is the property that would have been lost to a tolerance.

### 4.3 A clock-carrying chain is reachable, and was REACHED (task 7.4)

The route design section 7 established statically was EXECUTED, not only
read. `Sim(Captured())` over a `law=` factory that reads `source.time` at
realization compiles two constraints whose chain is
`(engaged + (12.0 * $t))` and whose free names are `('$t', 'engaged')`;
before the refusal landed, the first request died with a bare
`KeyError: '$t'` exactly where design section 7 predicted
(`Bounded.standing`). The factory's read raised nothing and emitted no
`FutureWarning` in this fixture. Task 7.4's STOP clause was therefore not
reached, and the general free-name rule went in as the design states it,
not as a backstop.

The refusal fires on the LOW side first, because `_constrained` compiles
`low` before `high`; the message names the node, the joint, the
coordinate, that side and the name that survived. **Decided at the
orchestrator's review: the executed captured-clock route stands as
designed.**

### 4.4 Two `Time` declarations of different bases compare EQUAL

`Time` is a frozen dataclass whose generated `__eq__` compares its one
field, so `Time.running() == Time.elapsed()` is `True` while their `mode`
differs. Nothing in the framework compares `Time` instances -- every
consumer reads `.loop` or `.mode` (task 1.3) -- so nothing is wrong
today, and a second field would have reached every producer, which
section 1 of the design rejects.

**Decided at the orchestrator's review: this is a real defect and not a
latent one** -- a test or a consumer comparing declarations would find
two bases that mean different things indistinguishable. CLOSED red-first
in section 7 below, without a second dataclass field.

### 4.5 One `.mode` consumer the design did not name

`simulation/enumeration._decide_block_membership` (line 217) compares
`.mode` to `'running'` beside the sites design section 1 lists. It is a
pre-pass confined to a running root, which an elapsed root skips exactly
as an undeclared one does. **Decided at the orchestrator's review: noted
among the `.mode` consumers in ADR-127**, which names it.

## 5. Measurements (task 9)

On the pendulum fixtures and cycle 1's register fixture only, reported
as their own numbers and compared to nothing outside this change.
Nothing is claimed about the Curta, which has no clock, and nothing
comparative about `Time.running()`, which this cycle does not touch.

Measured with `scratchpad/measure.py`, which puts a checkout root first
on `sys.path` and times each call 40 times (10 for the forty-event
requests), reporting the minimum and the median. The BEFORE column runs
the same script against a clean export of the planning commit
(`git archive 3067e3a`), so the two differ in this cycle's content and
in nothing else. One process at a time, `OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=1`.

**The clock costs a model that has none nothing** (task 9.2):

| measurement | before (`3067e3a`) | after |
| --- | --- | --- |
| register fixture, one request of one stroke `move('crank', by=360)` | min 0.107 ms, median 0.115 ms | min 0.107 ms, median 0.117 ms |
| stateless fixture, one pose (`bind_declared_defaults`) | min 0.044 ms, median 0.045 ms | min 0.044 ms, median 0.046 ms |

**The pendulum** (task 9.1):

| measurement | result |
| --- | --- |
| a time request with NO event (`by=T/8`) | min 0.062 ms, median 0.067 ms |
| a time request with ONE event (`by=T/2`) | min 0.109 ms, median 0.114 ms |
| a time request with FORTY events (`by=20*T`, a fresh `Sim` each time, so the number includes construction) | min 4.388 ms, median 4.529 ms |
| a time request with forty events (the same `Sim`, request after request) | min 2.067 ms, median 2.149 ms |
| one pose of the fixture (`Clocked.pose`) | min 0.035 ms, median 0.036 ms |
| one pose of the stateless elapsed twin `Swing` | min 0.045 ms, median 0.047 ms |

**The ratio design section 6 rests on.** A forty-event request costs
2.07 ms and one pose costs 0.035 ms, so the pose is about 1.7% of that
request and the events are essentially all of it; a request of ONE event
costs 0.109 ms against the same 0.035 ms pose, where the pose is about a
third. Posing TWICE per request -- the `set_state` delivery section 6
rejected -- would therefore have cost about a third again on the short
requests a maker actually makes, which is what the `visit` hook avoids.

## 6. Zero behaviour change (task 8)

- **8.1** The whole suite on the final content, run twice (the second
  run is the one that matches this tree byte for byte):
  `3239 passed, 4 skipped, 53 warnings, 1774 subtests passed in 325.76s`
  -- the baseline's 3183 plus this cycle's 56 new tests (46 in
  `tests/test_clocked_time.py`, 10 added to `tests/test_time_base.py`;
  the per-file split first written here was 44 and 12, which totals the
  same 56 and was corrected by counting the files at completion),
  with NO existing test edited and no expected value changed anywhere.
  `git status --short` against 1.2: seven modified source files, one
  modified test file (added tests only) and four new test files, and
  nothing else.
- **8.2** `tests/running-corpus.json` and every `tests/running_project`
  fixture are untracked by this diff -- `git status --short` reports
  none of them, so their 1.2 hashes stand. The running fixtures' cost is
  inside the envelope recorded in 1.1:
  `test_running_simulation.py::RecordingTest::
  test_nothing_is_recorded_by_default` 15.32 s against 16.48 s, and
  `test_running_jumps.py::CrossingRecordTest::
  test_nothing_is_recorded_by_default` 5.69 s against 6.41 s
  (`139 passed, 371 subtests passed in 25.17s`).
- **8.3** The stateless document is byte-identical: cycle 1's pinned
  literal in `test_clocked_publication.py::ZeroBehaviourChangeTest::
  test_a_stateless_document_is_byte_identical` still passes untouched,
  and this cycle adds the same assertion for the ELAPSED stateless root
  against an undeclared twin, for `document_body`, for `export_node` and
  for the builder's viewer snapshot (`ProducerTest`). The clocked-path
  counter reads ZERO across a stateless elapsed model's construction,
  pose, `Sim(node, dt)` stepping and publication
  (`StatelessElapsedTest::
  test_no_clocked_code_path_is_entered_for_a_stateless_elapsed_root`).
- **8.4** `Time.running()` is untouched, BY DIFF: `git diff --stat`
  names `solid_node/motion/{couplings,ports}.py`,
  `solid_node/node/{declarative,qualified}.py` and
  `solid_node/simulation/{clocked,enumeration,sim}.py` and NOTHING else.
  `solid_node/simulation/run.py` and `solid_node/simulation/program.py`
  -- the tick, the compile and the running document path -- have not one
  changed line. The three lines touched in `sim.py` are the `sim.time`
  readout; `enumeration.py`'s nine are the elapsed return; neither
  reaches a running root.
- **5.6** No tolerance was introduced: `_CROSSING_TOLERANCE` appears
  nowhere in `solid_node/simulation/clocked.py`, before or after -- the
  diff adds no reference to it and
  `EventsOnTheClockTest::test_no_tolerance_reaches_the_clock` asserts it
  of the module's own source.

## 7. Closure 1: two bases that compare EQUAL (review, 2026-09-17)

The orchestrator's adversarial review decided question 4.4 a REAL defect
rather than a latent one: `Time.running() == Time.elapsed()` was `True`
and the two hashed alike, so a test or a consumer comparing declarations
would find two bases that mean different things indistinguishable.
Closed here, red first, and without a second dataclass field -- design
section 1 rejects a field that reaches every producer.

**The red**, written before the fix
(`tests/test_time_base.py::TimeEqualityTest`, seven tests):

    3 failed, 4 passed, 44 deselected in 0.98s
    test_the_two_unwrapping_bases_are_not_equal
        AssertionError: Time(loop=None) == Time(loop=None)
    test_the_two_unwrapping_bases_do_not_share_a_hash
        AssertionError: 9181102132670838864 == 9181102132670838864
    test_a_declaration_stays_usable_in_a_set_and_a_dict
        AssertionError: 2 != 3

The four that passed red are the ones that must not move: a base equals
another declaration of itself, `Time(loop=4) == Time(loop=4)`,
`Time(loop=4) != Time(loop=5)`, and a declaration is not equal to a
foreign object.

**The fix.** `__eq__` and `__hash__` defined explicitly on `Time`, in the
class body, over `(loop, mode)`. `@dataclass` never overwrites either
when it is written in the body (`_set_new_attribute` for `__eq__`, and an
explicit `__hash__` suppressing the generated one), so the frozen
declaration stays hashable and usable as a dict key and set member.
`mode` is the property that tells the two unwrapping bases apart, which
is exactly why it is a property and not a field. Nine lines of code in
`solid_node/motion/ports.py` and no other file.

**Green, with the existing tests untouched:**
`tests/test_time_base.py` `51 passed, 7 subtests passed in 1.47s` --
the 44 that stood before this closure plus the 7 written for it, with no
existing test edited and no expected value changed.

## 8. Completion (2026-09-17)

- ADR-127 (NODE), "A clock is a banked value, and an event on it is an
  event", extracted after the implementation per design section 10;
  `docs/adrs/README.md` gained its row after ADR-126 and
  `docs/architecture.md` was rewritten where the synthesis moved -- the
  two-axis paragraph (one `-` left, `elapsed x none` admitted), the
  time-base paragraph (three spellings, the private marker, the equality
  rule), the clocked-mode block (the clock in the bank, the `visit`
  delivery, the clock as a source, "nothing stops a clock"), the
  stateless paragraph and the limitations list.
- `docs/scenarios.rst` gained three sections ("A machine with a CLOCK",
  "Events on the clock are events", "Nothing stops a clock") and its
  refusal list was corrected; `HISTORY.rst` gained the Unreleased entry.
- `workflow/warts.md` gained "Findings from the framework cycle
  `time-without-running` (2026-09-17)", carrying design section 12's
  Non-goals with their reasons and shapes -- the clip in time and the
  chain that follows the clock as ONE item -- the `NameError` blind spot,
  the three open questions of design sections 12 and 13, and the
  documentation gap that `docs/animation.rst` still names two bases.
  Nothing was marked CLOSED that this cycle did not close, and
  `declare-the-state`'s "A clocked model cannot be PUBLISHED or VIEWED"
  stays open as cycle 4's.
- Baseline specs synced and the change archived; the final suite and
  `openspec validate --all --strict` are recorded in the completion
  report.
