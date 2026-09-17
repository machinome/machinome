Every task below is RED FIRST: the test is written, run, and SEEN to fail for
the stated reason before the change that turns it green. Neither commit is
made until its whole group is green. Every fixture is geometry-free — no CAD
build, no `meshes = True` — and every run uses
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, ONE JOB AT A TIME:
`/home/asa/devel` is a virtiofs mount whose host daemon exhausts file
descriptors under parallel load, and the symptom is an intermittent "Too many
open files" from git, `ls` or a Python import, never a broken venv.

Run everything from inside this worktree with
`PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python`, so the
worktree's package is imported and not the installed one.

`design.md` section numbers are cited where a task implements a decision.

## 1. Baseline, recorded before anything moves

- [ ] 1.1 Record the byte size and sha256 of `tests/clocked-corpus.json`,
  `tests/running-corpus.json` and every file under `tests/clocked_documents/`,
  and the full clocked + running + export suite green at the cycle's base.
  These are the numbers §13's zero-change claim is checked against.
- [ ] 1.2 Record the probe of `Request`'s fields over the `Calculator`
  fixture — `move('crank', by=740.0)` reporting no start value — as the red
  evidence for §5, in `evidence.md`.

## 2. The refusal: exactly one driver (design §2)

- [ ] 2.1 `tests/clocked_project/unsupported.py`: two declarations beside the
  existing `Instructed` — `TwoInputs`, whose instruction's `by` names two
  declared drivers, and `NoInput`, whose `by` is empty — each geometry-free
  and written so a refusal test can quote it.
- [ ] 2.2 RED: `tests/test_clocked_refusals.py` asserts that `Sim(TwoInputs())`
  and `Sim(NoInput())` are refused naming the instruction, the inputs it names
  and the one-input rule. Fails: both construct today.
- [ ] 2.3 GREEN: the arity refusal in `compile_clocked`'s instruction loop
  (`solid_node/simulation/clocked.py:421-430`), beside the State refusal and
  before it, raising `ClockedError` with the instruction name, the sorted
  qualified inputs, the count and the rule — that a request names exactly one
  moving input, so an instruction under a clocked root names exactly one
  driver.
- [ ] 2.4 REGRESSION: the existing State-target refusal still fires with its
  own message over `Instructed`, unabsorbed by the new one.

## 3. `trigger` is a request (design §1, §3, §4, §6)

- [ ] 3.1 RED: `tests/test_clocked_sim.py` asserts that over the `Calculator`
  fixture with the instructions of task 4.1, `sim.trigger('Stroke')` returns a
  request equal field for field to `sim.move('crank', by=360.0)` from the same
  bank, and leaves an equal bank. Fails: `TypeError` from `_not_clocked`.
- [ ] 3.2 RED: the same for `sim.trigger('Set four')` against
  `sim.move('operand', to=4)` — the `targets=` branch, over an `int` driver.
- [ ] 3.3 RED: two roots differing ONLY in the declared `duration` (2.0 and
  0.0) make equal requests and equal banks: the machine reads no duration
  (§4).
- [ ] 3.4 RED: `sim.trigger('nothing')` under a clocked root raises `KeyError`
  listing the declared qualified names, and the bank and the posed tree stand.
  Fails: today it raises `TypeError` about a cadence.
- [ ] 3.5 GREEN: `Sim.trigger` (`solid_node/simulation/sim.py:514`) drops
  `_not_clocked('trigger()')` and, when `self._clocked is not None`, resolves
  through the EXISTING `_instruction` and `_driver` and returns
  `self._clocked.move(input_id, by=…)` or `(input_id, to=…)`. No new resolver,
  no method on `Clocked`, no change to the running or untimed branches.
- [ ] 3.6 GREEN: `_not_clocked`'s message stops implying `trigger` is refused
  and names the request verbs a clocked caller has.
- [ ] 3.7 REGRESSION: the cadence refusal test loses `trigger` and keeps
  `run`, `at`, `every`, `tick`, `rate`, `commands`, `program` and `crossings`
  refused by name, and `sim.time` still refused without an elapsed base.

## 4. Both ends of the path (design §5)

- [ ] 4.1 `tests/clocked_project/calculator.py`: `instructions = {'Stroke':
  Instruction(by={'crank': 360.0}, duration=2.0), 'Set four':
  Instruction({'operand': 4}, duration=0.5)}` on the existing `Calculator`,
  and nothing else in that fixture changed.
- [ ] 4.2 RED: `tests/test_clocked_sim.py` asserts that a `by=` request from a
  NON-ZERO start reports `origin` equal to the bank entry before it and
  `end` equal to the bank entry after it, and that every commit's `value`
  lies on the segment between them. Fails: `Request` has no such attributes.
- [ ] 4.3 RED: a CLIPPED request reports `end` at the stop's landing and
  not at the value asked for; a request admitted at ZERO travel reports
  `origin == end`; a `to=` request over an `int` driver reports `end`
  as the converted native value.
- [ ] 4.4 GREEN: `Request.__slots__` and `__init__` gain `origin` and
  `end`; `Clocked.move` passes `origin` (`clocked.py:2063`) and the
  CLIPPED `target` (`clocked.py:2090`) at the return (`clocked.py:2145`);
  `__repr__` stays one line and gains nothing a reader does not need.
- [ ] 4.5 The docstrings of `Request` and `Clocked.move` say what the two ends
  are, in which units, and why they are not left for a caller to recompute.

## 5. The corpus records a trigger (design §8)

- [ ] 5.1 RED: `tests/test_clocked_corpus.py` asserts that the committed
  corpus carries at least one `trigger` step in each instruction form and that
  a recorded trigger step carries `origin` and `end`. Fails: no such step
  and no such fields.
- [ ] 5.2 RED: the generator's inventory test asserts that a corpus playing no
  instruction, and one playing only the relative form, are refused naming the
  uncovered feature. Fails: the inventory does not list them.
- [ ] 5.3 GREEN: `tools/generate_clocked_corpus.py` — a `{'trigger': '<name>'}`
  script verb applied through the same `apply_step` recording shape as a
  request; `origin` and `end` recorded on every request and trigger step;
  `REQUIRED` gains "an instruction played as a request BY a travel" and "an
  instruction played as a request TO a target"; the `Calculator` script gains
  a `trigger` of each form, one of them crossing a stroke event, and a
  hand-made request beside it for task 5.5.
- [ ] 5.4 Regenerate `tests/clocked-corpus.json` and
  `tests/clocked_documents/calculator.json`, ONE process, and record the size
  before and after. Every other file under `tests/clocked_documents/` must be
  byte-identical to task 1.1's record.
- [ ] 5.5 The replay reproduces the file exactly, `tolerance.float` still
  `0.0`, and a `trigger` step's recorded fields equal those of the same
  request made by hand in the same script.
- [ ] 5.6 The corpus's own document copy for `Calculator` differs from task
  1.1's only in its `instructions` table — asserted, not inspected.

## 6. The document does not change (design §7)

- [ ] 6.1 REGRESSION, not red-first: `tests/test_clocked_document.py` asserts
  that a clocked root declaring one relative and one absolute instruction
  publishes a document byte-identical to the golden one recorded at task 1.1.
  It passes at the base and must pass after every group below; a failure means
  the meaning leaked into the document, which the design forbids.
- [ ] 6.2 RED: publishing a root whose instruction names two drivers writes no
  document and is refused by the machine's compile, through a build and
  through an export. Fails: it publishes today.
- [ ] 6.3 GREEN: nothing in `solid_node/core/serializer.py` changes. If this
  task needs a code change, the design is wrong and the pilot decides.

## 7. Zero behaviour change elsewhere (design §13)

- [ ] 7.1 `tests/running-corpus.json` replays unchanged and is byte-identical
  to task 1.1's record.
- [ ] 7.2 A running root's `trigger` still returns its tuple of commands,
  still claims every input before starting any, and still refuses an
  already-owned input; an untimed root's `trigger` still ramps and still
  returns `None`.
- [ ] 7.3 A stateless model's document is byte-identical, and the clocked
  counter still reads ZERO across its construction, render, symbolic walk,
  compile and `document_body`.
- [ ] 7.4 `git diff --stat` shows no change under `solid_node/simulation/run.py`,
  `solid_node/simulation/program.py` or `solid_node/core/`.

## 8. Documentation and measurement

- [ ] 8.1 `docs/scenarios.rst`: `trigger` leaves the "What a clocked model
  refuses today" cadence bullet and the instruction bullet; a short passage
  says an instruction under a clocked root is one request, that it returns
  one, and that the duration is for whoever draws it.
- [ ] 8.2 `docs/api-reference.rst`: `Request`'s two new fields;
  `HISTORY.rst`: one entry naming the originating project.
- [ ] 8.3 Measure `trigger` against the same `move` over the `Calculator`,
  median of 20, and record both in `evidence.md`: the difference must be a
  dictionary lookup.
- [ ] 8.4 Record in `evidence.md` every number this cycle measured, the red log
  for every task above, and anything found that contradicts `design.md`
  rather than silently resolving it.

## 9. Close the record

- [ ] 9.1 `workflow/warts.md`: mark "the instruction's meaning under a clocked
  root" CLOSED by this change, with the decision in one line and the
  multi-input refusal recorded as the deliberate narrowing it is.
- [ ] 9.2 ADR-129 (NODE) extracted after implementation per design §12, the
  house `Amended` line added to ADR-128 §"Instructions are published in the
  version 5 shape, with no meaning", and `docs/adrs/README.md` updated.
- [ ] 9.3 Sync the baseline specs, archive the change, and run
  `openspec validate --strict`.
- [ ] 9.4 Report what the viewer's cycle inherits: a returned `Request` with
  `origin`, `end`, `commits` and `stops`, a `trigger` that makes one
  request, and a regenerated corpus carrying trigger steps.
