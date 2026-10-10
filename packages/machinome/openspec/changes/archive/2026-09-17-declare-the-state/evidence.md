# Apply evidence: `declare-the-state`

Worktree `solid-node/WTs/clocked-machine`, branch `clocked-machine`, base
`81c5364`, planning commit `1118c1d`. Every run below was taken from
inside the worktree with

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
      .venv/bin/python -m pytest <target> -q -p no:cacheprovider

ONE process at a time. The originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`), whose
spike worktree `WTs/clocked-spike` is the requirement's evidence; nothing
in this cycle exercises it, and nothing here claims anything about it.

## The red log

Each entry is what was run, the failure line it was SEEN to raise, and
the change that turned it green.

| # | Test run | Red | Green |
| --- | --- | --- | --- |
| 1 | `tests/test_clocked_declaration.py` | `ImportError: cannot import name 'State' from 'solid_node.simulation'` | `simulation/state.py`, `StateDeclaration` + `declared_states_of` in `node/qualified.py`, the lazy export (tasks 2.2, 2.4) |
| 2 | `tests/clocked_project/counter.py` (collection) | `AttributeError: 'Coordinates' object has no attribute 'commits'` | `commits` on `CoordinateRef`/`Coordinates`/`DriverDeclaration`, `commit()`, `Commitment`, `CommitmentRecord`, `BankedEnd`, `declared_commitments`, `resolve_declared_commitments` (tasks 3.2, 3.4) |
| 3 | `tests/test_clocked_solver.py` | `ModuleNotFoundError: No module named 'solid_node.simulation.clocked'` | `simulation/clocked.py`: the compiler, the locator and the executor (tasks 4.2, 4.4, 4.6, 5.2–5.12) |
| 4 | `tests/test_clocked_sim.py` | `ModuleNotFoundError: No module named 'solid_node.simulation.clocked'` | the clocked branch of `Sim` (tasks 6.2–6.16) |
| 5 | `tests/test_clocked_publication.py` | `ImportError: cannot import name 'ClockedDocumentError' from 'solid_node.core.serializer'` | `_refuse_a_clocked_model` in `document_body` (task 7.2) |

Four further reds were seen INSIDE the green runs above, each fixed
before the group closed, and each recorded because it changed a decision
rather than a typo:

| # | Test | Red | What it changed |
| --- | --- | --- | --- |
| 6 | `test_surfaces_landing_on_one_float_are_one_event` | `AssertionError: 2 != 1` | `Commit` is one entry per EVENT, not per relation: relations landing on one float ARE one event, so the entry carries `relations` (a tuple) and a merged `targets`, with `relation` a property that reads the single one. |
| 7 | `test_a_law_returning_the_wrong_number_of_values_is_refused` | `ClockedError not raised` | a law returning a SEQUENCE for ONE target was silently accepted (the wrapper made it a one-tuple). `_checked_law` now refuses a sequence where one value is owed, naming the target. |
| 8 | `test_two_relations_of_the_tree_writing_one_state_are_refused` | `ClockedError not raised` | `_records_of` walked `node.children`, which is EMPTY on a root the enumeration has just bound. It walks `_rest_children` instead — the same linked rest structure every qualified pass descends. |
| 9 | `test_a_strict_comparison_lands_on_the_next_float` | `ClockedError: the state 'b' is declared and nothing writes it` | the fixture, not the framework: the "nothing writes it" refusal is real and fired on an unwritten spare state in `tests/clocked_project/ties.py`. The fixture dropped it. |

### The discipline slip, stated honestly

Tasks **2.5/2.6** and **3.3/3.4** — the writer refusals and the
class-definition refusals — were IMPLEMENTED in the same pass as the
declaration and the verb (reds 1 and 2), and their tests
(`tests/test_clocked_refusals.py`) were therefore written GREEN rather
than red-first. That is a departure from the rule and it is recorded
rather than hidden.

The evidence red-first would have given was recovered by MUTATION: each
refusal was neutralised at its own site, one at a time, and the test that
asserts it was run. All ten were KILLED; no mutant survived.

| Refusal site | Mutation | Test |
| --- | --- | --- |
| `couplings.StateRef.check` | `if role == 'driven' and False` | `test_a_state_is_not_a_driven_end` |
| `assembly.set_state`'s state branch | `if refused and False` | `test_set_state_refuses_a_state_by_name` |
| `control.Drag.__init__` | `isinstance(input, StateDeclaration) and False` | `test_a_turn_refuses_a_state_as_its_input` |
| `declarative._refuse_two_writers` call | commented out | `test_two_relations_of_one_body_writing_one_state_are_refused` |
| `enumeration.refuse_states_under_a_clock` | early return | `test_a_state_under_a_looping_base_is_refused` |
| `couplings._check_commitment_ends` target | `is None and False` | `test_a_target_that_is_not_a_state_is_refused` |
| `couplings._check_commitment_ends` source | `if True: continue` | `test_a_port_source_is_refused` |
| `couplings.commit` missing factories | `if False:` | `test_a_commits_with_no_at_is_refused` |
| `couplings.commit` rejected kwargs | `if False:` | `test_a_ratio_with_commits_is_refused` |
| `couplings._check_commitment_ends` broadcast | `and False` | `test_a_broadcast_commits_is_refused` |

The mutation harness restored every file it touched; `git diff --stat`
after it matched the run before it.

*Two rows above are HISTORY as of closure 1 (below): red 8 and the
`declarative._refuse_two_writers` mutation both pinned the one-writer
rule, which the design amendment of 2026-09-17 removes. They are left as
written, because they are the record of what was run.*

## Tool signatures changed, and why

Every change below is the minimal one that made reuse possible, and the
whole existing suite is green with it.

1. **`program._Walk._far_side` → the free function `program.far_side_of`.**
   The landing walk was a `_Walk` method closed over `self._level`,
   `self.described` and `self.coordinate`. It is now
   `far_side_of(branch_at, near, own_star, direction, unlanded)`, and
   `_Walk._far_side` is three lines calling it. The clocked solver lands a
   request path by the SAME walk rather than a second one; the body is
   unchanged, line for line.
2. **`program._graph_of`'s text-and-vocabulary walk → `program.checked_expression`.**
   `_graph_of` refuses raw text and a call outside `SYMBOLIC_BUILTINS`,
   then applies `_only_jumps`. The first half is now
   `checked_expression(value, refuse, kind)`, which `_graph_of` calls and
   which the commit-law check reuses WITHOUT the jump plan, the skeleton
   or the `_only_jumps` refusal — which is exactly the asymmetry design
   section 7 states. One refusal message's wording moved from "the run
   can evaluate" to "the framework can evaluate", since both callers now
   share it.
3. **`program._too_many` attaches `count` to the error it builds.** The
   clocked request refusal states the same judgement in its own words and
   reports the number that raise reached rather than guessing one. The
   message is unchanged.
4. **`node.qualified.drive_tree` takes `collected=None`.** A dict passed
   there receives every declared STATE of the tree by qualified id, from
   THIS pass and never a second one. States are BOUND either way, because
   a tree that declares one cannot be rendered without them.
5. **`enumeration.qualified_declarations` returns THREE tables**
   (`instructions, controls, states`) instead of two. This is the
   requirement "the same walk SHALL return every declared `State` ... from
   the same pass rather than an additional one", and it is the only way
   to meet it without a second descent. Its two faces
   (`qualified_instructions`, `qualified_controls`) are unchanged.
6. **`node.base._receive_state` / `assembly._receive_state` take
   `states=None`.** A dict passed there collects the tree's state ids in
   the walk `set_state` already makes, so `set_state` refuses a state BY
   NAME instead of reporting it as an undeclared driver. `None` — every
   existing caller — changes nothing.
7. **`Sim.__init__`'s `dt` became optional**, with a `_NO_DT` sentinel: a
   clocked root takes none, and every other root is still refused for
   omitting one, by a message naming `dt`.
8. **`Sim.tick` became a property** over `_tick`, so it can be refused by
   name over a clocked root. It keeps a setter, because `run.py` assigns
   it.

## Existing tests changed, and why

Exactly two, both pinning a surface this change deliberately extends:

- `tests/test_lazy_test_framework.py::EXPECTED_EXPORTS` — `State`,
  `declared_states` and `qualified_states` added. That table IS the
  package's public surface, and the proposal states the lazy export.
- `tests/test_controls.py::test_one_walk_returns_both_tables` — unpacks
  three tables and asserts the state table is `{}` for a model that
  declares none. The arity change is item 5 above.

No fixture was edited, no expected VALUE was changed, and
`tests/running-corpus.json` was not touched.

## Design questions

None. Nothing in the ratified design was contradicted by what the
implementation found. Two places where the design underdetermined a
detail were resolved inside its own reasoning rather than against it, and
both are recorded here:

1. **Reading the AFTER branch of a crossing.** Design section 6 says a
   step is rising when `at`'s branch after the crossing is greater than
   before, "read from `_branch_of` at the midpoints of the two adjoining
   pieces". A crossing at the request's own ENDPOINT has no right-hand
   piece and therefore no right midpoint — and the endpoint crossing is
   precisely the one `move('crank', by=360)` with `at = floor(crank/360)`
   must fire, by the design's own worked scenario. The after-branch is
   therefore read at the LANDING, which is by construction the nearest
   representable point of the piece the path is going into. The
   before-branch is still the midpoint reading the design names. For a
   non-endpoint crossing the two readings cannot differ: `floor`'s
   surfaces are the integers and a comparison has one surface.
2. **The crossing maximum counts LOCATED crossings, rising or not.** The
   spec says "the events ACTUALLY LOCATED ... never a count estimated
   from the travel and the surface spacing". `JumpPlan._solved` locates
   every surface of an affine piece in one call, so the count IS the
   located number and not an estimate; a path that is monotone in one
   direction has all its steps the same sign, so counting the located
   rather than the rising ones can only refuse a long BACKWARD request
   that would have committed nothing. Recorded rather than special-cased:
   splitting such a request is the same advice the message already gives.

## Measurements (task 9.1)

On the two clocked fixtures ONLY, and compared to nothing. Reported as
microseconds per call, median of the runs below, on this machine, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one process at a time.

| Measurement | Register fixture | Clearing fixture |
| --- | --- | --- |
| one pose of the tree | **60.0 us** | 78.8 us |
| one commit (the law over the bank) | **0.9 us** | 0.7 us |
| a request with NO event | 81.9 us | 96.5 us |
| a request with ONE event | 107.1 us | — |
| a request with TEN events | 428.2 us | — |
| `Sim(...)` construction + a one-event sweep | — | 2 872 us |

What they say, and nothing more:

- **The commit is not the cost; the pose is.** A commit is 1.5 % of a
  pose on the register fixture. That is the design's own claim
  (section 9, "a request costs no pose") measured on the thing this cycle
  built. The project spike's 26 microseconds per commit through the
  Curta's own `calculate` is an ORDER-OF-MAGNITUDE sanity reading for
  this number and not a comparison: that law is the whole of a Curta
  stroke and this one is two digits.
- **A request pays for exactly one pose.** The no-event request is one
  pose plus about 22 us of solving; ten events add about 320 us, which is
  32 us per event of locating and committing, and NO further pose.
- **Nothing here is claimed about the Curta.** The spike's factor of 35
  is that project's measurement, cited as the requirement's evidence and
  deliberately not reproduced.

### The stateless cost, before and after

Seconds per pose of a STATELESS model, the same three calls run under a
checkout of the base commit `81c5364` and under this worktree (script and
extracted base tree in the session scratchpad):

| | run 1 | run 2 | run 3 |
| --- | --- | --- | --- |
| base `81c5364` | 43.9 us | 43.7 us | 48.9 us |
| this worktree | 44.8 us | 42.5 us | 42.0 us |

Indistinguishable: the ranges overlap and neither side is consistently
faster. The one thing a stateless pose gained is a cached
`declared_states_of(type(node))` dict lookup per node, inside the walk it
already made.

### Byte-identical publication

The same stateless model's document body, produced by the same three
calls under the base checkout and under this worktree:

    {"drivers": {"crank": {"default": 0, "dtype": null, "range": null,
     "scale": null, "unit": "deg"}}, "format": "solid-node-export",
     "instructions": {}, "version": 2}

`diff` of the two: IDENTICAL. That literal is pinned in
`tests/test_clocked_publication.py::ZeroBehaviourChangeTest.RECORDED`, so
a later change to this capability cannot move it silently.

### One walk added, named

`Sim.__init__` now asks `tree_declares_states(node)` before it validates
`dt`, because a clocked root takes NO `dt` and the question has to be
answered before anything is bound. `document_body` asks the same
question. Both are structural walks that render nothing — the shape
`tree_declares_drivers` already has — and neither enters a clocked code
path: the counter on `simulation.clocked` is asserted ZERO across a
stateless model's construction, pose, `Sim(node, dt)` stepping and
publication (`test_a_stateless_tree_enters_no_clocked_path`).

## Suite result

    3122 passed, 4 skipped, 1736 subtests passed  (first full run, 310 s)

That run had the two pinned-surface failures above. After updating those
two tests the full suite is green; the final counts are in the report.

## What is NOT done here, by assignment

No commit, no ADR (candidate ADR-125), no baseline-spec sync, no archive:
those follow the orchestrator's review of this uncommitted
implementation. Tasks 10.2 and 10.5 are therefore open; 10.1, 10.3 and
10.4 are done.

## Closure 1 (2026-09-17)

The orchestrator reviewed the uncommitted implementation with a
Curta-shaped probe — a three-wheel register of one class, with carry and
per-digit clearing — and returned four findings. C2 amends the RATIFIED
DESIGN, so the planning artifacts were revised and re-validated FIRST
(`openspec validate declare-the-state --strict` passes), and only then
the implementation, red first. Nothing is committed; the orchestrator
amends planning commit 1 and makes commit 2.

### C1 — the two-writers refusal keyed on the LOCAL NAME

**RED.** Importing the new fixture `tests/clocked_project/register.py` —
three `Wheel` children of ONE class, one relation writing all three
digits:

    TypeError: Register: the state 'digit' is written by two committing
    relations -- (crank, operand, w0.digit, w1.digit, w2.digit) commits
    (w0.digit, w1.digit, w2.digit) and (crank, operand, w0.digit,
    w1.digit, w2.digit) commits (w0.digit, w1.digit, w2.digit).

The SAME relation named twice, because `declarative._refuse_two_writers`
keyed on `id(state_declaration)` and three children of one class share
one `State` declaration. The orchestrator's `probe2.py` reproduced the
same refusal across two children.

**What was found, against the finding's own instruction.** The finding
asked that BOTH refusals be keyed on the path. Only ONE of them was
keyed on the name: the "named twice among the targets" refusal is the
`&`-group's own duplicate check in `couplings._group_refs`, which keys on
`ref.key()` — `('path', id(root), segments)` for a path and
`('state', id(declared))` for a bare one — and therefore already tells
`a.digit` from `b.digit` and still refuses `(a.digit, a.digit)`. It is
unchanged, and a test now pins both halves of that
(`test_one_relation_naming_one_target_twice_is_refused_by_path`,
`test_two_children_of_one_class_are_two_targets`). The refusal that was
wrong is the one C2 removes outright, so the fix is the removal.

**GREEN.** `declarative._refuse_two_writers` and its call are gone,
replaced by a comment saying what a class body decides and what it
cannot; `tests/test_clocked_register.py::PathsNotNamesTest` is the
evidence, and the probe now prints `two same-named states OK {'a.digit':
1, 'b.digit': 2, 'crank': 360}`.

### C2 — several writers, never at one event

**RED, at class definition.** Collecting `tests/test_clocked_register.py`
with the new `unsupported.Conflicting` fixture:

    TypeError: Conflicting: the state 'value' is written by two
    committing relations -- (crank, value) commits value and (crank,
    value) commits value.

**RED, at construction.** The same rule again in
`clocked.compile_clocked`, pinned by
`test_clocked_sim.py::test_two_relations_of_the_tree_writing_one_state_are_refused`.

**GREEN.** Both refusals removed. The tree-wide `written` table is now a
SET, used only for "a state nothing writes", which stays. The conflict is
refused by the REQUEST: `Clocked.move` collects, per event, which
relation wrote which qualified id, and `_two_answers` raises a
`ClockedError` naming the state, both relations as written and the
landing. The bank is untouched until the request completes, so the
refusal commits nothing.

**The fixture.** `tests/clocked_project/register.py` — a `crank`, a
`ring`, an `operand`, three `Wheel` children of one class each declaring
`digit`, one stroke relation writing all three (carry inside the law, and
by hand in every test) and one clearing relation per wheel reading its
own digit. One departure from the finding's suggested threshold,
recorded because it changes what the fixture proves: the thresholds are
`START + 100*p + PITCH*digit`, the MIRROR of the clearing fixture's
measured `START + PITCH*(10 - digit)`. Under the measured form, zeroing a
wheel pushes its threshold AHEAD of the ring, so a sweep long enough to
reach the third wheel reaches the first a SECOND time (measured: four
events where two were expected) — the real machine's ring carries the
zeroed rack along with it, which this fixture does not model.
`clearing.py` keeps the measured form for the self-read proof; the
register fixture states the one-way sweep directly. The docstring says
so.

**Tests** (`tests/test_clocked_register.py`, 12): strokes add with carry
(twelve strokes of one → 2/1/0); a bigger operand carries (nine, eight
times → 2/7/0); a partial sweep to 200 clears only w0 (reached at 18) and
w1 (at 130), not w2 (at 214); a reversed sweep un-clears nothing; a
second sweep fires once, on w2 alone; strokes after clearing continue
from zero; the pose follows the committed digits; two writers on two
inputs are admitted; two writers at ONE landing refuse the request by
name with `sim.state` unchanged.

Two existing tests were replaced by their amended form, both of which
pinned the removed rule:
`test_clocked_refusals.py::test_two_relations_of_one_body_writing_one_state_are_refused`
→ `..._may_write_one_state`, and
`test_clocked_sim.py::test_two_relations_of_the_tree_writing_one_state_are_refused`
→ `..._may_write_one_state`, which now exercises `unsupported.TwoWriters`
as the Curta's stroke-and-clearing shape.

### C3 — atomicity must include the final pose

**RED.** `test_clocked_sim.py::BoundTest::test_a_request_whose_final_pose_is_refused_commits_nothing`:

    AssertionError: {'crank': 1440.0, 'value': 4} != {'crank': 720.0, 'value': 2}

and `..._test_a_restore_whose_pose_is_refused_changes_nothing`:

    AssertionError: {'crank': 0.0, 'value': 3} != {'crank': 360.0, 'value': 1}

**GREEN.** `Clocked.pose(bank=None)` takes the bank to bind, and a new
`Clocked._posed(bank)` poses it FIRST and assigns `self.bank` only if the
tree accepted it; on failure it re-poses the previous bank and re-raises.
`move` and `restore` both go through it. The orchestrator's `probe1.py`
now prints `bounded after failure {'crank': 720, 'n': 2}` where it
printed `{'crank': 1440, 'n': 4}`.

### C4 — an event no driver can reach

**RED.** `test_clocked_sim.py::test_a_relation_no_driver_can_reach_is_refused`
over the new `unsupported.Unreachable`: `ClockedError not raised`. The
relation compiled with an empty `jumps` table, so `moves_with` was False
for every input and it could never fire.

**GREEN.** `_compiled` refuses an empty `jumps` table by name, beside the
curved-level refusal, naming the relation and its sources and saying an
event is located on the motion of a DRIVER.

### Records amended for coherence

`docs/scenarios.rst` (several writers, the one-event conflict, the
all-states refusal, and the bound bullet), `HISTORY.rst` (the same),
`workflow/docs/clocked-machine.md` (CORRECTION 4: the note's "a state has
exactly one committing relation", which its own next paragraph
contradicts), `workflow/warts.md` (the `Bound` follow-up restated, and a
new one: two writers at one event are found by RUNNING, not by reading).

### Suite

Six clocked modules: **111 passed, 18 subtests**, 2.0 s.

Full suite, one process,
`pytest tests -q -p no:cacheprovider`:

    3141 passed, 4 skipped, 1745 subtests passed in 311.00 s

(3124/4/1745 before closure; the 17 added tests are the register module's
12, three refusal tests for C1/C2, and two for C3, against two replaced.)

No measurement was re-taken: nothing in this closure touches a pose, a
commit or the locator. The conflict check is one dict insertion per
target per event.

### Planning files touched (for the amendment of commit 1)

    openspec/changes/declare-the-state/proposal.md
    openspec/changes/declare-the-state/design.md
    openspec/changes/declare-the-state/specs/simulation/spec.md
    openspec/changes/declare-the-state/specs/couplings/spec.md
    openspec/changes/declare-the-state/tasks.md

`evidence.md` is untracked and belongs to commit 2 with the
implementation.
