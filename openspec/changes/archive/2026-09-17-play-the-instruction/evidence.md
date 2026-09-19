# Evidence: `play-the-instruction`

Every number here was measured on the cycle bench
`solid-node/WTs/play-the-instruction` (branch `play-the-instruction`, base
`1a959d3`), one process at a time, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD"` and the workspace
venv at `/home/asa/devel/libresolid-studio/.venv`. The originating project is
`projects/Calculators/Curta-Type-I-3x` (branch `direct-operation`, HEAD
`9fb725f`), whose `simulation/clocked.py:ClockedCurta` declares an instruction
a consumer cannot play.

## 1. Baseline, before anything moved

### 1.1 The files the zero-change claim is checked against

Recorded at `0186ed3`, the ratified planning commit, over a clean worktree:

| file | bytes | sha256 (first 16) |
| --- | ---: | --- |
| `tests/clocked-corpus.json` | 139262 | `e58c1feaa8f109ea` |
| `tests/running-corpus.json` | 267185 | `08855baf37384397` |
| `tests/clocked_documents/calculator.json` | 13627 | `70e7c2bfe9bc72ed` |
| `tests/clocked_documents/counter.json` | 2689 | `0e0ebfd9a017d7de` |
| `tests/clocked_documents/pawl.json` | 3778 | `ef5b11e221a1df4b` |
| `tests/clocked_documents/pendulum.json` | 1653 | `a9c06f2f31a46b7a` |
| `tests/clocked_documents/register.json` | 6648 | `df22485b72af47f2` |

The clocked, running-corpus and export modules at the base:

```
$ pytest tests/test_clocked_{bounds,corpus,declaration,document,publication,
         refusals,register,sim,solver,time}.py tests/test_running_corpus.py
         tests/test_export.py -q
352 passed, 1 warning, 212 subtests passed in 16.33s
```

### 1.2 RED, for design section 5: a request says nothing about where it began

Probed over the `Calculator` fixture at the base:

```
$ python -c "sim.move('crank', by=740.0)"
slots   : ('input', 'by', 'to', 'commits', 'admitted', 'stops')
input   : crank
by      : 740.0
to      : None
admitted: 740.0
stops   : ()
  commit (crank, operand, w0.digit, ...) value 360.0 fraction 0.4864864864864865
  commit (crank, operand, w0.digit, ...) value 720.0 fraction 0.9729729729729730
repr    : <request move('crank', by=740.0) -> 2 commits, admitted 740.0>
has origin? False   has end? False
bank['crank'] after: 740.0
```

Nothing in the value object is `0.0`, the value the crank stood at when the
request began, and nothing in it is `740.0` *as a bank entry* — `by` and
`admitted` are both the DESIGN-unit ask, which coincides here only because the
crank declares no scale. Every commit's `value` (360.0, 720.0) is in NATIVE
units, so a consumer holding only this request cannot say what segment those
values lie on. This is the failure design section 5 closes.

## 2. The refusal: exactly one driver (design section 2)

### 2.2 RED

`tests/clocked_project/unsupported.py` gained `TwoInputs` (an instruction
whose `by` names `crank` and `ring`) and `NoInput` (whose `by` is empty), and
`tests/test_clocked_refusals.py` a new `InstructionArityRefusalTest`:

```
FAILED ...::test_an_instruction_naming_no_driver_is_refused
  AssertionError: ClockedError not raised
FAILED ...::test_an_instruction_naming_two_drivers_is_refused
  AssertionError: ClockedError not raised
2 failed, 1 passed
```

Both models CONSTRUCT at the base — which is the design's own reading of the
`publish-the-clocked-machine` correction: `compile_clocked` refused an
instruction only where its TARGET is a State.

### 2.3 GREEN

The arity refusal went into `compile_clocked`'s instruction loop, BEFORE the
State refusal and in the same pass, raising `ClockedError` naming the
instruction, the count, the sorted qualified inputs and the rule. `23 passed`.

### 2.4 REGRESSION

`test_the_state_target_refusal_is_not_absorbed_by_the_arity_one` asserts that
`Instructed` — one target, and that target a State — is still refused by the
STATE message (`which is a State`) and not by the new count (`exactly one` is
asserted ABSENT from it). Green. The pre-existing
`test_an_instruction_targeting_a_state_is_refused` in `test_clocked_sim.py` is
untouched and still green.

## 3. `trigger` is a request (design sections 1, 3, 4, 6)

### 3.1-3.4 RED

`tests/test_clocked_sim.py` gained `TriggerTest`. Every case failed with the
same refusal, which is exactly the failure the cycle exists to remove:

```
TypeError: trigger() belongs to a simulation with a CLOCK, and Calculator is
CLOCKED: its tree declares a State, it declares no time base, and it has no
cadence. ...
```

five failures: the relative form, the absolute form, the duration's silence,
the unknown name (which raised that `TypeError` about a cadence instead of the
`KeyError` listing the declared names), and a child-declared instruction.

### 3.5-3.6 GREEN

`Sim.trigger` drops `_not_clocked('trigger()')` and, when `self._clocked is
not None`, resolves through the EXISTING `_instruction` and `_driver` and
returns `self._clocked.move(input_id, by=…)` or `(input_id, to=…)`. No new
resolver, no method on `Clocked`, no change to the running or untimed branches
— `git diff --stat -- solid_node/simulation/run.py` is empty. `_not_clocked`'s
message now names `sim.trigger(name)` beside `sim.move(input, by=…)` as the
request verbs a clocked caller has.

### 3.7 REGRESSION

`trigger` left the cadence-refusal lists in BOTH
`tests/test_clocked_sim.py:CadenceRefusalTest` (untimed clocked root) and
`tests/test_clocked_time.py:RefusedNamesTest` (elapsed clocked root); `run`,
`at`, `every`, `tick`, `rate`, `commands`, `program` and `crossings` stay
refused by name in both, and `time` stays refused without an elapsed base.
`test_trigger_is_not_refused_as_a_cadence` pins the positive half: over
`Counter`, which declares no instruction, `trigger('Home')` raises the
instruction resolver's `KeyError` and the message does not say `CLOCKED`.

## 4. Both ends of the path (design section 5)

### 4.2-4.3 RED

`tests/test_clocked_sim.py:PathEndsTest`, five cases, every one:

```
AttributeError: 'Request' object has no attribute 'origin'
```

### 4.4-4.5 GREEN

`Request.__slots__` and `__init__` gained `origin` and `end`, placed after
`to` so the value object reads input, ask, ends, events; `Clocked.move` passes
`origin` — the bank entry it already held — and the CLIPPED `target`, neither
recomputed. `__repr__` is unchanged: it gains nothing a reader does not
already have. The docstrings of `Request` and `Clocked.move` say what the two
ends are, that they are NATIVE where `admitted` is DESIGN, and why they are
not left for a caller to recompute.

What the five cases prove, each value computed by hand from the fixtures'
own constants:

| case | fixture | origin | end |
| --- | --- | ---: | ---: |
| `by=` from a non-zero start | `Calculator` crank, after 100 | `100.0` | `840.0` |
| clipped at a numeric bound | `Stroke` lift, asked 12 mm | `0.0` | `9.0` |
| admitted at ZERO travel | `Standing` feed, pushed further out | `0.0` | `0.0` |
| `to=` over an `int` driver | `Calculator` operand | `1` | `4` |
| a SCALED driver | `ScaledStroke` lift, `by=3.0` | `0.0` | `6.0` |

The last is the documented asymmetry, proved rather than asserted: the same
request reports `admitted == 3.0` in DESIGN units and `end == 6.0` in native
ones, which is why a consumer must not rebuild an end through the scale.

## 5. The corpus records a trigger (design section 8)

### 5.1-5.2 RED

`tests/test_clocked_corpus.py` gained `TriggeredStepTest` and
`TriggerInventoryTest`: `66 failed, 2 passed`. The failures were of three
kinds —

- `test_the_corpus_plays_an_instruction_in_each_form`: no script step carries
  a `trigger` at all;
- `test_every_recorded_request_carries_both_ends_of_its_path`: 63 recorded
  steps, `AssertionError: 'origin' not found in {...}`;
- `TriggerInventoryTest`: `uncovered_features` lists neither new feature, so a
  corpus playing no instruction is written rather than refused.

(`test_a_recorded_trigger_carries_the_request_it_made` passed vacuously at the
base, there being no trigger step to examine; its companion above is the one
that fails.)

### 5.3 GREEN

`tools/generate_clocked_corpus.py`: `apply_step` records `origin` and `end` on
every request step and takes a `{'trigger': '<name>'}` verb through the SAME
recording shape; `REQUIRED` gained "an instruction played as a request BY a
travel" and "an instruction played as a request TO a target";
`uncovered_features` reads which FORM a trigger played off the published
`instructions` table, the way a consumer reads it, and then treats the step
exactly as a request step. The declared `duration` is recorded nowhere.

`tests/clocked_project/calculator.py` gained the two instructions, and the
`Calculator` script gained, after its closing `reset`:

```python
{'trigger': 'Set four'},      # targets=, over an int driver
{'snapshot': 'd'},
{'trigger': 'Stroke'},        # by=, crossing the stroke event at 360
{'restore': 'd'},
{'move': {'input': 'crank', 'by': 360.0}},   # the same request by hand
```

### 5.4 The corpus, before and after

| file | before | after |
| --- | ---: | ---: |
| `tests/clocked-corpus.json` | 139262 bytes, 76 steps | 145673 bytes, 81 steps |
| `tests/clocked_documents/calculator.json` | 13627 bytes | 13816 bytes |

30 machines and 30 scenarios, unchanged. The 6411 bytes are: five new
`Calculator` steps (two triggers, a snapshot, a restore, a hand-made request),
`origin` and `end` on all 63 recorded requests across all 30 machines, and the
two instructions in the `Calculator` document copy.

Every other file under `tests/clocked_documents/` is byte-identical to task
1.1's record — `counter.json` `0e0ebfd9a017d7de`, `pawl.json`
`ef5b11e221a1df4b`, `pendulum.json` `a9c06f2f31a46b7a`, `register.json`
`df22485b72af47f2` — and none appears in `git diff --stat`.

### 5.5-5.6

The replay reproduces the file exactly, `tolerance.float` still `0.0`, and
`CorpusReplayTest.apply` now replays a trigger step through the same
comparison a request step goes through, `origin` and `end` included.
`test_a_triggered_step_equals_the_same_request_made_by_hand` asserts the
recorded `Stroke` step and the hand-made `move('crank', by=360.0)` two steps
later — after the restore that puts the bank back — are EQUAL as recorded
dictionaries, field for field.

`calculator.json` differs from task 1.1's copy in exactly one hunk:

```
469c469,482
<   "instructions": {},
---
>   "instructions": {
>     "Set four": { "duration": 0.5, "targets": { "operand": 4 } },
>     "Stroke":   { "by": { "crank": 360.0 }, "duration": 2.0 }
>   },
```

`CorpusDocumentAgreesWithTheGoldenTest` pins that in the suite: the corpus's
own `Calculator` document copy equals the committed golden key for key, and
the `instructions` table is exactly the two declared.

## 6. The document does not change (design section 7)

### 6.1

`test_the_meaning_reaches_no_key_of_the_document` publishes ONE class twice —
`_instructed(declare=True)` and `_instructed(declare=False)`, the same class
name either way, because a published commit names the assembly that stated it
— and asserts that every key of the two documents is identical except
`instructions`. It is a regression and not red-first, and it passes.

The stronger form of the same claim is the golden diff above: the document
`Calculator` publishes after this cycle is byte for byte the one it published
before it, apart from the table whose CONTENT it declared.

### 6.2 RED

`test_an_instruction_naming_two_drivers_reaches_no_document` was written after
the refusal of task 2.3 was already in, so its RED was demonstrated OUT OF
ORDER and is recorded as such: the arity guard in `compile_clocked` was
disabled (`if False:`) and the test run —

```
SUBFAILED(model='TwoInputs') ... AssertionError: ClockedError not raised
SUBFAILED(model='NoInput')  ... AssertionError: ClockedError not raised
2 failed, 2 passed
```

— then the guard restored and the test re-run: `2 passed, 2 subtests passed`.
A root whose instruction names two drivers, or none, publishes a document when
the compile does not refuse it; it writes none when it does.

### 6.3

Nothing in `solid_node/core/serializer.py` changed. `git diff --stat --
solid_node/core/` is EMPTY. The design was not wrong here.

## 7. Zero behaviour change elsewhere (design section 13)

### 7.1

`tests/running-corpus.json` is byte-identical to task 1.1's record — 267185
bytes, sha `08855baf37384397` — and does not appear in `git diff --stat`.
`tests/test_running_corpus.py` replays it green.

### 7.2

`tests/test_running_simulation.py` and `tests/test_running_stops.py` still
unpack a running `trigger`'s TUPLE of command handles
(`crank_handle, lever_handle = sim.trigger('Wind')`, `blocked, free =
sim.trigger('Sweep')`), and the ownership refusal that starts nothing is
unchanged. `tests/test_simulation_sim.py` gained one assertion the suite did
not have — `test_an_untimed_trigger_still_returns_nothing` — so the
asymmetry design section 3's open question 3 records is pinned rather than
assumed: only a CLOCKED root's `trigger` gained a return value.

### 7.3

`ZeroBehaviourChangeTest` (`tests/test_clocked_publication.py`) is unchanged
and green: a stateless tree's construction, render, run, symbolic walk,
compile and `document_body` leave `clocked_module.entered()` exactly where it
was.

### 7.4

```
$ git diff --stat -- solid_node/simulation/run.py \
      solid_node/simulation/program.py solid_node/core/
(empty)
```

The whole change:

```
 solid_node/simulation/clocked.py        |  71 ++++-
 solid_node/simulation/sim.py            |  31 ++-
 tests/clocked-corpus.json               | 270 ++++++++++-
 tests/clocked_documents/calculator.json |  15 +-
 tests/clocked_project/calculator.py     |  15 +-
 tests/clocked_project/unsupported.py    |  36 ++
 tests/test_clocked_corpus.py            | 182 +++++++-
 tests/test_clocked_document.py          | 112 +++--
 tests/test_clocked_refusals.py          |  56 +++
 tests/test_clocked_sim.py               | 239 +++++++++-
 tests/test_clocked_time.py              |  11 +-
 tests/test_simulation_sim.py            |  11 +
 tools/generate_clocked_corpus.py        |  59 ++-
```

plus `docs/scenarios.rst`, `docs/api-reference.rst` and `HISTORY.rst` from
task 8.

## 8. Measurement

### 8.3 `trigger` against the same `move`

Over the `Calculator` fixture, median of 20, one process, each request made
from the same restored bank (the restore is outside the timed region):

| | median |
| --- | ---: |
| `sim.trigger('Stroke')` | 0.7833 ms |
| `sim.move('crank', by=360.0)` | 0.7817 ms |
| difference | **1.7 us (+0.22%)** |

Twenty lookups of `sim.instructions['Stroke']` cost 1.9 us in the same
process. The difference between pressing the button and making the request is
therefore the table lookup, the driver lookup and the `'.'.join` that
qualifies the name, and nothing else: the claim "an instruction is a request
and nothing else" holds.

### 8.4 Suites

| | at the base | after |
| --- | --- | --- |
| clocked + running-corpus + export modules | 352 passed, 212 subtests, 16.3 s | 375 passed, 281 subtests, 15.5 s |
| the FULL `tests` suite | not run at the base | **3389 passed, 4 skipped, 1943 subtests, 350.5 s** |

Run once, one process, `-p no:cacheprovider`, with
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`. No failure, no error, no new
warning: the 53 warnings are the pre-existing `render()`-reads-a-driver
`FutureWarning`s.

## 9. What implementation found that the plan did not say

Recorded rather than silently resolved, per the assignment.

1. **`docs/api-reference.rst` documents NO clocked API at all.** Task 8.2 asks
   for "`Request`'s two new fields" there, and the file's reference stops at
   the RUNNING simulation: `Request`, `Commit`, `Clocked` and `ClockedError`
   were never added by ADR-125..128, and `Request` is not exported from
   `solid_node.simulation` either. Adding two fields to an entry that does not
   exist is impossible, so a short **Clocked simulation** section was added
   beside the Running one — `Clocked` with its request surface, `Request`,
   `Commit`, `ClockedSnapshot` and `ClockedError` — which is where the two new
   fields are now documented. This is more surface than task 8.2 named; it is
   flagged for the reviewer rather than assumed.

2. **`HISTORY.rst` carried a now-stale corpus size.** The version 8 entry in
   the same UNRELEASED section says the clocked corpus is "thirty machines,
   seventy-six steps"; it is eighty-one after this cycle, and the two entries
   ship together. The number was corrected in place. ADR-128's own
   "**Measured**: 30 machines, 30 scenarios, 76 steps, 139 262 bytes" was left
   alone: it is that cycle's record of what it measured.

3. **Two test modules carried the cadence list, not one.** Design section 6
   and task 3.7 name the clocked cadence refusal; `trigger` was in the refused
   list of `tests/test_clocked_sim.py:CadenceRefusalTest` AND of
   `tests/test_clocked_time.py:RefusedNamesTest`, the elapsed root's own copy.
   Both were corrected, and the second is the one that proves the meaning
   holds under EVERY time base, which the simulation delta spec states.

4. **`_instructed()` had to become parameterizable to prove task 6.1.** The
   first attempt compared two differently named classes and failed on
   `clocked`: a published commit carries `stated_by`, the name of the assembly
   that stated it. The fixture now takes `declare=False` and yields the SAME
   class without the two declarations, which is the only way to vary one
   declaration and nothing else.

5. **Nothing contradicted the design's substance.** `compile_clocked` had the
   facts the arity refusal needs; `Clocked.move` already held both floats at
   the return; `Sim.trigger`'s existing `_instruction`/`_driver` resolvers gave
   the unknown-name and unknown-driver messages by construction; and task
   6.3's prediction held exactly — `solid_node/core/serializer.py` did not
   change.
