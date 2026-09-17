# Evidence: `publish-the-clocked-machine`

Implementation of the ratified plan, worked RED FIRST through `tasks.md`.
The originating project is `projects/Calculators/Curta-Type-I-3x` (branch
`direct-operation`, HEAD `9fb725f`; the clocked spike is its worktree
`WTs/clocked-spike`), whose clocked model reproduces the operating model's
registers at every stroke end and is worth nothing to its pilot until a
browser can crank it.

Every command below was run from this worktree with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD"` and the
workspace venv, ONE pytest process at a time.

## 1. The baseline this cycle must not move

- **1.1** Green baseline at `627114b`, worktree clean:
  **3246 passed, 4 skipped, 1774 subtests, 318.11 s**. The running
  fixtures' timings are in the run's `--durations=25` list; the slowest
  three are `test_retained_builder_generation` (33.08 s),
  `test_running_simulation::RecordingTest` (15.17 s) and
  `test_node_lazy_exports` (14.51 s), none of them a clocked path.
- **1.2** `git status --short` was EMPTY. Hashes taken of
  `tests/running-corpus.json`, every `tests/running_project/*.py`, and
  `simulation/run.py`, `simulation/program.py`, `core/expressions.py`,
  `viewers/bundle.py`.
- **1.3** Four FULL document bodies published and kept: `plain`
  (`clocked_project.counter:Stateless`, version 2, 0 bindings, 489
  bytes), `bindings` (`expression_project.sharing:SharedValueTree`,
  version 4, 4 bindings, 1467 bytes), `flexible`
  (`flexible_project.spring:Valvetrain`, version 4, 1 binding, 941
  bytes) and `running` (`running_project.machine:Train`, version 5, 0
  bindings, 3073 bytes).
- **1.4** Verified against the source. Producers reaching `document_body`:
  `core/builder.py:672`, `core/export.py:161`, `viewers/browser.py:100`
  and `tools/generate_running_corpus.py:308` (`document_of`). Callers of
  `viewer_bundle.unreadable_document`: `viewers/browser.py:148`,
  `core/builder.py:46`, `core/export.py:203`. Non-test callers of
  `instructions_table` with `running=`: `core/builder.py:664`,
  `core/export.py:158`, `tools/generate_running_corpus.py:307`. **No site
  the design did not name.**

## 2. The red log

Each entry is the test, and the failure line seen BEFORE the change that
turned it green.

| task | test | red |
| --- | --- | --- |
| 2.1 | `RetainedLawTest` (both) | `AttributeError: 'Committing' object has no attribute 'law_graphs'` |
| 2.3, 2.7, 2.8 | `PublishedObjectTest` (6) | `AttributeError: 'Clocked' object has no attribute 'published'` |
| 2.4 | `PublishedCommitTest` (6) | `commits` published as `[]`: `IndexError: list index out of range`, and `[] != [['w0.digit', ...], ...]` |
| 2.4a | `test_a_law_over_a_negative_operand_publishes_what_is_banked` | `AssertionError: -1.0 != 9 : ((((w0.digit + (10 * w1.digit)) + (100 * w2.digit)) + operand) % 10)` |
| 2.4b | `test_the_desugaring_reproduces_pythons_own_remainder` | `ImportError: cannot import name '_floored_remainder'` |
| 2.5, 2.6 | `PublishedBoundTest` (6) | `bounds` published as `[]`: `0 != 4`, `0 != 2` |
| 2.9 | `CompiledForPublicationTest` (3) | `ImportError: cannot import name 'clocked_of'` / `cannot import name 'compiled_clocked'` |
| 3.1 | `test_dollar_own_is_not_a_name_of_the_expression_language` | `ExpressionError: expected a scalar expression (offset 0 of '$own + 1')` — the refusal the test now pins |
| 3.2 | `test_a_driver_named_own_lengthens_the_minted_name` | with the mint's `while` loop removed: `AssertionError: '_own' != '__own'` |
| 4.1, 4.2 | `VersionLadderTest` (4) | `TypeError: document_version() got an unexpected keyword argument 'clocked'` |
| 4.3, 4.5, 4.6 | `StatesTableTest`, `ClockedObjectInTheDocumentTest` (9) | `TypeError: instructions_table() got an unexpected keyword argument 'version_five_or_above'` |
| 4.7 | `ReaimedGateTest` (2) | `AssertionError: 'without its compiled machine' not found in 'Counter is a CLOCKED model ... the document version that carries declared states is not defined yet.'` |
| 4.8 | `test_a_stateless_tree_costs_one_structural_walk` | `AssertionError: 4 != 1` — the walk RECURSES, so the counter had to count walks and not nodes |
| 5.1 | `test_an_elapsed_clocked_document_carries_the_clock_by_name` | `AssertionError: 'time' not found in '[["r", "(12.0 * sin(((360.0 * $t) / 2.0)))", [0, 0, 1]]]'` |
| 6.3 | `test_a_version_eight_document_publishes_every_instruction` | with `version_five_or_above` forced False: `AssertionError: Lists differ: ['Park'] != ['Advance', 'Park']` |
| 7.1, 7.2, 7.3 | `ProducerPublicationTest`, `BrowserRefusalTest` (4) | `ClockedDocumentError: Counter is a CLOCKED model ... this document body was assembled without its compiled machine` — each producer refused because it did not compile |
| 7.6 | `ReaimedGateTest::test_each_producer_reaches_it` | `AttributeError: module 'solid_node.core.export' does not have the attribute 'compiled_clocked'` |
| 9.6 | `test_one_representable_value_of_drift_fails_the_replay` | the replay REJECTS a landing moved by one representable value, which a `1e-9` window accepts — asserted directly |
| 10.1 | `GoldenDocumentTest` | the fixture files did not exist |

Two behaviours were written and turned green inside a wider change and
their reds were reproduced afterwards by reverting the one line that
makes them true (rows 3.2 and 6.3 above). Both reverts are recorded with
their failure text; nothing else in this cycle was asserted without a red.

## 3. Measurements

**The Curta-shaped fixture** (`tests/clocked_project/calculator.py`,
task 8.3), on this worktree:

- compile (`Sim(Calculator())` construction, which is what `clocked_of`
  performs): **8.3 ms**
- `Clocked.published(initial)`: **0.39 ms**
- longest published CHAIN, the selector's through the port and the ratio:
  **3 nodes** (`(setting * 6.0)` composed through `shaft`). The ratchet's
  chain is 1 node and its bound 6; the freeze's bounds are 13 and 14
  nodes and their levels 17 and 18. ADR-126 measured 1 to 3 nodes and
  levels 3 to 18 on its own fixtures, so nothing here is larger than what
  that cycle already sized.
- published `clocked` object: **4919 bytes**, 6 commits, 3 bounds
- whole version 8 document: **8071 bytes**, 39 bindings

**The corpus** (task 9.5): `tests/clocked-corpus.json`, **136 922 bytes**,
**30 scenarios over 30 machines**, **70 steps**. The machines are
`Calculator, Ceiling, Clearer, ClockAlone, Conflict, Counter, Decorative,
Freeze, Gate, JumpsOnly, Kinked, KinkedCounter, Lift, Lock, NonStrict,
Pawl, Register, Regulator, Rounded, SamePair, Scaled, ScaledStroke, Shut,
Signed, Standing, Strict, Stroke, SwappedPair, UlpPair, Untouchable`.

**Golden documents** (task 10.1), under `tests/clocked_documents/`:
`counter.json` 2689 B, `pendulum.json` 1653 B, `pawl.json` 3778 B,
`register.json` 6648 B, `calculator.json` 13 627 B.

**The desugaring's property test** (task 2.4b), run two ways against
CPython's own `a % b`:

- **500 000 random double pairs** as a one-off on this worktree —
  uniform small, wide-magnitude with a sub-ulp divisor, integral values,
  and random finite BIT PATTERNS of both signs: **0 value mismatches**,
  with 5577 pairs differing only in the SIGN OF A ZERO. That reproduces
  the number `design.md` §16 recorded, against this implementation.
- **6000 pairs per suite run**, in the committed test, plus the six hand
  cases `-1 % 10 = 9`, `1 % -10 = -9`, `-7 % -3 = -1`, `5.5 % -2 = -0.5`,
  `-5.5 % 2 = 0.5` and `1e308 % -3 = -1`: zero mismatches. Six thousand
  rather than half a million because the suite runs it on every commit;
  the wide sweep is evidence, and the committed one is the regression.

The ONE stated exception is the SIGN of a zero result under a negative
divisor: Python's `copysign(0.0, b)` gives `-0.0` where the desugaring
gives `+0.0`, which compares equal as a number in both runtimes
(`-0.0 == 0.0`, `-0 === 0`) and which nothing in the published vocabulary
distinguishes. The test counts those and asserts equality everywhere
else.

**Final suite** (task 11.5): **3352 passed, 4 skipped, 1874 subtests,
323.13 s** — against the baseline's 3246 / 4 / 1774 / 318.11 s. 106 tests
and 100 subtests added, no timing regression, no fixture edited and no
expected value moved.

## 4. What must not have moved, checked rather than claimed

- **11.1** The four FULL documents of §1.3 published again and compared
  LITERALLY against the files kept then: **identical, byte for byte**
  (`diff -q` clean).
- **11.2** `sha256sum -c` over `tests/running-corpus.json`, every
  `tests/running_project/*.py`, `simulation/run.py`,
  `simulation/program.py`, `core/expressions.py` and `viewers/bundle.py`:
  **every line OK**.
- **11.3** `git diff` of `simulation/run.py` is EMPTY, and so is
  `simulation/program.py`'s — **better than the design planned**. The
  design expected `program.py` to be reused; it is reused
  (`_placeholder_prefix`, `_published_plan`, `_renamed`, `_snapshots`,
  `_restore`, `_plan_of`, `_shape_of`, `JumpPlan`, `_Jump`,
  `_CROSSING_TOLERANCE`, `_MAX_CROSSINGS`, `far_side_of`) and NOT
  modified: no running behaviour changes, asserted by diff.
  `core/expressions.py` and `viewers/bundle.py` are likewise unchanged
  (tasks 3.3 and 7.5), each with a test that says so.
- **11.4** `simulation.clocked.entered()` reads ZERO across a stateless
  model's construction, `set_state`, render, `Sim(node, dt)` stepping,
  `symbolic_document`, `compiled_clocked` AND `document_body`
  (`ZeroBehaviourChangeTest::test_a_stateless_tree_enters_no_clocked_path`).
  Three subprocess import probes assert that importing the serializer
  imports neither `simulation.clocked` nor `simulation.program`, that
  publishing a stateless model imports no clocked module, and that
  publishing a clocked one does.
- **4.8** `document_body` asks ONE structural walk for a stateless tree
  and renders nothing, counted by patching `tree_declares_states` and
  counting only TOP-level calls.

## 5. The basis of the exactness claim (task 9.9)

The corpus declares `"tolerance": {"float": 0.0}` and the replay compares
with `assertEqual` and nothing else. Operation by operation:

- **IEEE `+`, `-`, `*`, `/` and `sqrt`** — the standard requires each
  correctly rounded, so one double in gives one double out in either
  runtime. `sqrt` is admitted by the generator's exactness guard for
  exactly that reason.
- **The truncated remainder `%`** — exact by construction (`math.fmod` in
  the framework's two evaluators, JavaScript's native `%` in the
  viewer's), and the FLOORED remainder composed from it adds ONE IEEE
  addition and therefore one rounding. Verified against CPython's
  `float_rem` over 6000 random pairs plus the hand cases (§3).
- **`floor`, `ceil`, `abs`, `sign`, `min`, `max` and the six
  comparisons** — each SELECTS rather than rounds.
- **The landing walk**, `far_side_of` (`program.py:1578-1634`), is a
  bisection in the ORDINAL space of a double's own bits, through
  `_ordinal`/`_from_ordinal` (`program.py:1029-1041`): a
  reinterpretation of a double's 64 bits as a signed integer, which a
  second runtime reproduces with one `ArrayBuffer` viewed as a
  `Float64Array` and a `BigInt64Array`, **and never with arithmetic**.
  A consumer that walked by a small epsilon instead would land on a
  different float at exactly the surfaces this corpus is built on, and
  **cycle 5 owes that bit walk.**
- **What it does NOT rest on:** a TRANSCENDENTAL (`sin`, `cos`, `tan`,
  `asin`, `acos`, `atan`, `atan2`) or a POWER, neither correctly rounded.
  `inexact_operations` REFUSES a machine carrying one in a published
  commit law, event level, constraint level or chain, and
  `ExactnessGuardTest` tests that refusal four ways on doctored
  documents. `pendulum`'s `sin` is in the POSE, which the corpus does not
  record at all.

The claim is PROVED and not merely declared: moving one recorded landing
of `UlpPair` by ONE representable value — a drift far inside `1e-9`
relative — makes the replay fail
(`test_one_representable_value_of_drift_fails_the_replay`).

## 6. What the parity fixture pins (task 9.8), and it is not what the design assumed

The design says ADR-022's parity fixture "pins the DOCUMENT's `%`, which
is what a chain and a bound carry". **It does not.** Checked here:
`solid_node.math.SYMBOLIC_BUILTINS` is a list of NAMES and `%` is an
OPERATOR, not one of them, and no case of
`tools/generate_parity_fixture.py`'s vocabulary carries a remainder at
all (`build()['cases']` yields no expression containing `%`).

What actually pins the document's own `%` is the RUNNING corpus, whose
feature inventory REQUIRES `'%'` and whose `Remainder` machine states it,
within that corpus's own `1e-9` window. This cycle's corpus pins the
DESUGARED form a commit law carries, exactly, and its machines' own
`bindings` tables carry the truncated remainder in 18 entries — so both
spellings are pinned, in two places, and neither by the parity fixture.
Recorded as a test
(`test_what_pins_the_documents_own_remainder_is_not_the_parity_fixture`)
rather than as a sentence.

## 7. Design questions and deviations

Each is a place where what I found differs from `design.md`. None changed
a ratified behaviour; each is reported rather than silently substituted.

### 7.1 `Committing.jumps` is a SUPERSET of the inputs that can move the level

Design §6 says an input absent from a commit's published `shapes` "cannot
move this level at all, which is exactly `moves_with`". It is not exactly
`moves_with`. `_compiled` (`clocked.py`) classifies EVERY driver among a
relation's sources, and a driver the level does not read at all
classifies **`'constant'`** — so `register`'s stroke relation holds
`{'crank': 'affine', 'operand': 'constant'}` and `moves_with('operand')`
answers True.

The export capability admits exactly two values for a `shapes` entry,
`"affine"` and `"kinked"`, and defines the table as "one entry per input
that can MOVE this relation's event level". **Decision: publish the
affine and kinked entries and omit the constant ones**, which is what the
ratified requirement says and what a consumer needs — examining a
relation whose level cannot move finds no crossing and costs a wasted
solve. `moves_with` and the request path are UNTOUCHED. Recorded in the
publisher's own docstring and asserted by
`test_a_relation_an_input_cannot_move_is_not_listed_for_it`.

### 7.2 `CompiledClocked` is `Clocked`

Tasks 2.3 and 2.9 name `CompiledClocked.published(initial)`. There is no
such class: the compiled machine and the executor are ONE object,
`simulation.clocked.Clocked`, and `Sim` holds it as `sim._clocked`
(where a run holds `sim.program` beside `Run`). `published`, `described`,
`published_names`, `own` and `identity` are therefore on `Clocked`, and
`clocked_of(root)` returns `(sim._clocked, dict(sim.initial.values))`.

### 7.3 `published(initial)` does not read `initial`

Design §4 settles that a clocked document carries no `coordinates` table
because a clocked bank holds no joint coordinate and every number in it
is already published by the two tables and `clocked.clock`. The
consequence is that `published`'s `initial` parameter has nothing to do:
it is accepted for `Program.published`'s symmetry — both are reached
through `document_body(..., initial=...)` — and deliberately not
published. Stated in the docstring rather than dropped, because dropping
it would make `clocked_block` and `program_block` two different shapes at
the one call site that dispatches between them.

### 7.4 Two landings the shared locator has no answer for

Two requests reachable from the corpus's own machines raise
`LandingInvariantError` from `far_side_of` — the solver's own "broken
invariant" — where the design's behaviour is a stop that admits ZERO
travel or an event that fires:

1. **A request that ends EXACTLY on a STRICT comparison's surface.**
   `ties.Strict` states `at = crank > 100`; `move('crank', to=100.0)`
   raises. At `crank == 100` the level reads the unsatisfied branch, and
   the satisfied side begins at the next representable value, which is
   beyond the request's own endpoint. The NON-strict twin
   (`ties.NonStrict`, `crank >= 100`) lands on `100.0` and fires, which
   is ADR-125's stated rule ("a request that ends exactly ON a surface
   has reached it").
2. **A bank standing on a LOW bound's threshold and pushed FURTHER out
   from a coordinate value of exactly `0.0`.** `calculator.Standing`
   rests with `slide.travel` at `0.0` and its low bound at `3.0`;
   `move('feed', by=-1.0)` raises, while the same machine moved to
   `feed = 1.0` first admits one representable value of travel and
   reports its stop, and the MIRROR case on a HIGH bound
   (`outside.Outside` opened at `feed = 12.0`, pushed further out by
   `+1.0`) admits ZERO travel and reports its stop, exactly as designed.

Neither is this cycle's to fix — both are in the shared locator ADR-126
compiled against, and this cycle may not change what a clip computes —
and neither is recorded as corpus contract: `Strict` is driven THROUGH
its surface and `Standing` is only driven back INSIDE. **Both are open
items for the pilot** and belong in `workflow/warts.md` (task 12.3, which
follows the orchestrator's review).

### 7.5 `affine` travels in a published bound's jump plan

Design §7 says the published `plan` is "EXACTLY the running document's
jump plan, through the same `_published_plan`", and the export
requirement says "in exactly the shape a published program's jump plan
has". `_published_plan` emits `affine` per jump beside `name`,
`primitive` and `level`, so a clocked bound's plan carries it too. That
is one classification stated twice — `affine` from the level's own
global shape, and `shapes[input]['jumps'][i]` from the per-input shape —
and the per-input one is authoritative. Kept as the design states,
because the alternative is a second plan publisher.

To publish it, `Bounded` gained one slot, `plan`: the base `JumpPlan`
`_plan_of` built, `None` where the level carries no jump. `plans` (per
moving input) is what a REQUEST still solves over, unchanged.

### 7.6 A bound's jump shape may read `constant`

The export requirement admits `"affine"` and `"kinked"` for a commit's
`shapes`; a BOUND's `shapes` entry carries "the SKELETON's structural
shape and one shape per published jump" with no such restriction, and a
ratchet's `floor(_own / 6.0)` is CONSTANT in the crank. Published as
`constant`, which is the true classification and what the solver used.

### 7.7 Where the producer tests live

`proposal.md`'s Impact lists "added tests in `tests/test_viewer_bundle.py`,
`tests/test_browser_renderer.py`, `tests/test_build_publication.py`,
`tests/test_export.py`". The build, export and browser assertions are in
`tests/test_clocked_publication.py` instead — the file whose refusals
this cycle INVERTS (task 4.7), where the build/export/browser refusal
tests already stood, so each refusal and the publication that replaces it
sit side by side. `tests/test_viewer_bundle.py` gained its own tests as
planned; `tests/test_snapshot.py` gained the OpenSCAD-renderer tests of
task 7.4, which the proposal did not name.

### 7.8 The `crossing_tolerance` claim ADR-127 pinned as a source check

`tests/test_clocked_time.py::test_no_tolerance_reaches_the_clock`
asserted that `_CROSSING_TOLERANCE` appears NOWHERE in `clocked.py`.
Design §9 corrects the claim it stood for: a clocked path introduces no
NEW use of that constant but does REACH it, when a kinked event level's
crossings are merged by `_deduplicated` and when a jumped constraint
level's cuts are folded by `JumpPlan.cuts`, both inside the shared
locator. The test is rewritten to assert what is now true and checkable:
the module names the constant in exactly TWO lines — the import, and the
published `limits` — and nowhere on the request path.

## 8. What this cycle did NOT do

Per the assignment: no ADR (candidate ADR-128), no spec sync, no archive,
and no edit to `docs/scenarios.rst`, `docs/animation.rst`, `HISTORY.rst`
or `workflow/warts.md`. Tasks 12.1, 12.2, 12.3 and 12.5 follow the
orchestrator's review. Nothing is committed: the implementation is
uncommitted in this worktree for review.

`workflow/warts.md` (task 12.3) must record, beside this cycle's own
findings: the CROSS-MODE `%` divergence (the same law text means the
floored remainder under a clocked root, where the callable is called, and
`fmod` under a running root, where the graph is evaluated); the
POSE-versus-GRAPH `%` divergence, framework-wide and pre-existing, where
a `drives(law=)` taking `%` of a negative poses through the callable and
publishes through the graph in every document version from 2 upward; the
brief's wrong assumption about instructions under a clocked root (§14 of
the design, pinned as a test); the two landing invariants of §7.4 above;
and `Committing.jumps`' constant entries of §7.1.

## 9. Closure 1: the two landing invariants, closed here

Section 7.4 reported two requests the SHARED locator had no answer for and
left them for the pilot. The review's decision was that neither is deferred:
both LOSE or REFUSE a legitimate request, and this cycle's corpus is what
found them, so they close here. Design section 22 states the rule; this
section is the evidence. Both were seen RED first.

### 9.1 The reds

**(a)** `tests/test_clocked_solver.py::LandingContainmentTest` — two of its
four tests failed before the change, both from the same raise:

```
E   solid_node.simulation.program.LandingInvariantError: (crank, a) commits
    a: a was cut at a surface of > and no value within 200 doublings of a ulp
    of the segment's own arithmetic reads the other branch, so the cut placed
    the coordinate nowhere. ...
FAILED ...::test_a_request_ending_on_a_strict_surface_fires_nothing
FAILED ...::test_the_next_request_fires_the_strict_surface_it_stands_on
2 failed, 2 passed, 18 deselected
```

The raise is NOT the one the message describes. Traced (`far_side_of`
instrumented over `Sim(ties.Strict()).move('crank', to=100.0)`), the walk is
entered TWICE: once at `own_star = 100.0` with `direction = +1.0`, where it
lands correctly on `100.00000000000001`; and once more at the same
`own_star` with `direction = -1.0`, where no value below 100.0 reads the
other branch. The second call is the request RESUMING: the landing lies one
representable value BEYOND the endpoint, `Sim.move`'s loop sets
`current = landing`, and `delta = target - current` is then `-1.42e-14` — the
request turns round and re-solves the surface it has just passed. So the
symptom is a broken invariant, and the defect is the containment rule.

**(b)** `tests/test_clocked_bounds.py::ClipTest::`
`test_a_stop_from_a_coordinate_standing_at_zero_admits_nothing`:

```
E   solid_node.simulation.program.LandingInvariantError: the low bound of
    'slide.travel': the level was crossed on this request and no value of
    'feed' within reach of the crossing's own arithmetic reads the satisfied
    side, so the stop placed the input nowhere. ...
1 failed, 42 deselected
```

With the step scaled by the segment but the stop still left to the walk, the
same test failed a SECOND way, which is the measurement design section 22
quotes:

```
E   AssertionError: -2.220446049250313e-16 != 0.0
```

— half an ulp of the LEVEL (`ulp(3.0) / 2`), the travel the input's finer
grid near zero buys and the level cannot express. The high-bound mirror
admits exactly `0.0` (`test_the_threshold_frees_a_bank_standing_outside_a_bound`,
unchanged and green).

### 9.2 The change

| file | what changed |
| --- | --- |
| `simulation/program.py` | `far_side_of` takes `scale=0.0`; `step = math.ulp(own_star) if own_star else 5e-324` becomes `math.ulp(max(abs(own_star), abs(scale)))`. TWO code lines and a docstring paragraph; nothing else in the module. |
| `simulation/clocked.py` | `Committing._located` adds the path's OPENING surface through the shared `_on_surface`; `Committing.next_event` reads the opening branch at the start and at the next representable value, skips a landing beyond the endpoint, and passes `scale`; `Bounded.clip` returns `(0.0, start)` for a crossing solved at fraction 0 and passes `scale`. |
| `tools/generate_clocked_corpus.py` | `Strict`, `NonStrict` and `Standing` scripts extended; two features added to `REQUIRED` with their detection. |
| `tests/test_clocked_solver.py` | `LandingContainmentTest`, 4 tests. |
| `tests/test_clocked_bounds.py` | the low-side mirror test, in `ClipTest`. |
| `tests/test_clocked_corpus.py` | two coverage-guard tests added; the ulp-apart guard now drops `Signed` too. |
| `tests/clocked-corpus.json` | regenerated. |

`math.ulp(0.0)` IS `5e-324`, so `far_side_of` with no `scale` computes the
same step it computed before for every value, zero included: the running
walk is unchanged BY CONSTRUCTION and not merely by measurement.
`_Walk._far_side` passes no `scale`.

### 9.3 The corpus diff

`tests/clocked-corpus.json`: **136 922 → 139 262 bytes, 70 → 76 steps**, 30
machines and 30 scenarios unchanged. Step by step, the ONLY differences:

- `Strict` gains four steps after a reset: `to=100.0` admits 100.0 and fires
  NOTHING; `by=1.0` fires once at `100.00000000000001` (fraction
  `1.4210854715202004e-14`); a second `by=1.0` fires nothing. Its first two
  steps are unchanged.
- `NonStrict` gains one step: `by=1.0` after the surface fires nothing, so
  the twin fires exactly once, on the request that ends ON the threshold.
- `Standing` gains one step AT THE FRONT: `by=-1.0` admits `0.0` with one
  stop (`slide.travel`, `low`, bound `3.0`, value `0.0`). Its two existing
  steps are byte-identical.
- `Signed` changes: `move('shuttle', by=10.0)` from `-5.0` now fires TWO
  events, at `0.0` and at `5e-324`, and `count` ends at 2 rather than 1 —
  the `0 → +1` step of `sign` that the fraction reading lost. This is the
  ONE existing recorded value the closure moves, and it moves because it
  was wrong.

No other machine's bank, admitted travel, commit or stop differs in any
byte.

### 9.4 What did not move

- `tests/running-corpus.json`, `simulation/run.py`: `git diff` EMPTY.
- `solid_node/simulation/program.py`: the diff is the `far_side_of`
  signature, the one `step =` line and the docstring — no other line.
- `tests/test_running_simulation.py`, `tests/test_running_corpus.py`,
  `tests/test_running_document.py`: green, unchanged.
- Every clocked test of cycles 1 to 3 green and unedited except the two
  coverage guards named above; `test_resuming_from_the_landing_does_not_refire`,
  `test_a_strict_comparison_lands_on_the_next_float`,
  `test_a_non_strict_comparison_lands_on_the_threshold` and
  `test_the_threshold_frees_a_bank_standing_outside_a_bound` all stand
  untouched and green.

### 9.5 Where it is recorded

`design.md` section 22; the export delta's corpus inventory and two new
scenarios; a MODIFIED `A clocked simulation solves a request path event by
event` in `specs/simulation/spec.md` carrying every existing scenario plus
the two new ones, with the containment rule as its new item 5 and the walk's
segment-sized step in item 4; ADR-128, which states both as clarifications
of ADR-125 and ADR-126; and `workflow/warts.md`, where both are marked
CLOSED with their origin and where the running walk's untouched ulp-of-zero
step is filed.

## 10. Follow-up (2026-09-17): a non-finite commit is banked

Found by the shop-skill writer running this branch to check every example
the public API skill states, and fixed as a NARROW ADJUSTMENT on the same
branch (commit message `fix(simulation): a non-finite commit refuses the
request; correct two scenario sentences`).

**The defect.** The export requirement "A published commit says what it
reads, writes and fires on" states that a document cannot express a raise,
so a CONSUMER that computes a non-finite commit value refuses the request
rather than banking it (design section 16; this cycle's own commit message
claimed the framework did the same). It did not. `Committing.commit` passed
whatever the law returned to `State.committed`, which touches nothing but an
integer's rounding, so a law returning `float('inf')` or `math.nan` to a
FLOAT state was BANKED — silently, with the pose, every bound and every
later event then reading a value no arithmetic recovers from. A `dtype=int`
state was no better: `round(float('inf'))` raised `OverflowError` from
`state.py`, naming neither the relation, nor the state, nor the value. The
two runtimes of one exact corpus refused different requests.

**The red.** `tests/test_clocked_sim.py::NonFiniteCommitTest`, over three
new fixtures in `tests/clocked_project/unsupported.py` (`Infinite`,
`NotANumber`, `InfiniteCount`): before the change, `ClockedError not
raised` for the two float states — `sim.state['value']` held `inf` and
`nan` — and `OverflowError: cannot convert float infinity to integer` for
the integer one.

**The change.** `Committing.commit` judges each returned value BEFORE
`State.committed` rounds it: a numeric value that is not finite raises
`_not_a_value`, a `ClockedError` naming the relation as written, the state
by its qualified id and the value. The request is refused WHOLE — the
executor's working bank is a copy and the pose is taken after it, so
ADR-125's atomicity carries the refusal with nothing added. A non-numeric
return is untouched, a value slot still accepting whatever is put into it.
Mutation: with the finiteness test forced to `False`, all three reds return.

**The corpus.** `tools/generate_clocked_corpus.py` gained the guard
`non_finite_records`, refusing to WRITE a fixture in which any recorded
bank, commit, admitted travel or stop is non-finite — such a file is not
even JSON a strict reader in a second runtime can parse, `json.dump`
writing the non-standard `Infinity`/`NaN` tokens. No committed machine
records one, so `tests/clocked-corpus.json` regenerates BYTE-IDENTICAL
(`build()` compared against the committed file); the guard is covered by
`tests/test_clocked_corpus.py::NonFiniteGuardTest`, whose doctored case
fails when the check is removed.

**The record.** One sentence and one scenario ("A non-finite commit refuses
the request") were added to the requirement "A clocked simulation solves a
request path event by event", in the baseline `openspec/specs/simulation/
spec.md` and in this change's own `specs/simulation/spec.md` delta, which
remain identical block for block. ADR-128 carries an implementation-note
line. `docs/scenarios.rst` gained the refusal in "What a clocked model
refuses today" and `HISTORY.rst` one sentence.

Two further defects the same reading found were documentation-only and are
corrected in the same commit, both in `docs/scenarios.rst`:

1. "What a clocked model refuses today" ended with "an instruction or a
   control under a clocked root", which is the brief this cycle's design
   section 14 and ADR-128 explicitly OVERTURNED: a control is refused, an
   instruction naming a STATE is refused at simulation construction, and an
   instruction over a DRIVER is admitted and published in the version 5
   shape with no execution meaning, `trigger` staying refused by name.
2. "Running a machine that keeps a FEW values" said a state "is written by
   exactly one thing" and then, eleven paragraphs later, "SEVERAL relations
   may write one state" — the ratified rule (ADR-125 closure 1). The first
   sentence was pre-amendment text and now states the ratified rule: a
   committing relation is the only writer, several may write one state, and
   two writing it at ONE landing refuse the request.
