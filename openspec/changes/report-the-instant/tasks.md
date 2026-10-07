Bench: `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`. Every framework command runs as
`env -C <bench> PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/<tool> ...`;
every project command as
`env -C <Clocks> PYTHONPATH=<bench>:<Clocks> /home/asa/devel/machinome/.venv/bin/<tool> ...`
with `<Clocks>` = `/home/asa/devel/machinome/projects/3DPrintedClocks`,
read and run, never edited; nothing is created under it. `<scratch>` is
the campaign scratchpad's `cycle13/` directory: `repro/` (the scratch
project of design.md, Context), `provoke_mantel34.py` (run from
`<Clocks>`), and Stage P's captured outputs (`repro-before.txt`,
`repro-skipclass-before.txt`, `mantel34-before.txt`,
`provoke-before.txt`). The scratch runs use `env -C <scratch>/repro -u
SOLID_BUILD_DIR PYTHONPATH=<bench> .../python -c 'from machinome.cli
import manage; manage()' test boat/<name>.py`. One test run of ours at a
time (`ps -eo pid,args | grep '[p]ytest\|[m]achinome test\|[m]achinome
snapshot\|[m]achinome build'` first; the meta suite and the full suite
share `tests/_build`). Every test marked RED in section 2 is run and seen
red, for the reason it names, before the code that turns it green. Record
every command and its result in `evidence.md` as you go, in the shape of
`openspec/changes/archive/2026-10-04-scad-presentation/evidence.md`, and
copy the scratch sources (`repro/` and `provoke_mantel34.py`) into it: the
scratchpad is not durable.

## 1. Baseline on the unmodified tree

- [ ] 1.1 Create `evidence.md` with the bench commit (`git -C <bench>
  rev-parse HEAD`) and the interpreter check (`python -c 'import
  machinome; print(machinome.__file__)'` prints a path under the bench).
- [ ] 1.2 Run `pytest -q -p no:cacheprovider tests/test_manager_test.py`;
  record counts and wall time (Stage P: 106 passed, 18 subtests passed,
  1.93 s, 2.37 s wall).
- [ ] 1.3 Run the four scratch projects (`boat/sweep.py`,
  `boat/setup.py`, `boat/setupclass.py`, `boat/skipclass.py`) and record
  each output and exit status (Stage P, design.md, Context: the
  `ValueError` of the last instant printed and no instant named; three
  bare tracebacks, no summary line, exit 1).
- [ ] 1.4 In `<Clocks>`: `git -C <Clocks> status --short` (expect only
  ` M screenshots/wall_clock_03.png` and `?? WTs/`, neither ours); then
  `machinome test mantel_clock_34_steampunk --mesh --volume-epsilon
  0.001`, recording the summary line, the wall time, every `Running ...
  FAIL!` line and every `AssertionError` line (Stage P: 20 tests, 15
  passed, 5 failed, 43.12 s, 46.40 s wall); then `python
  <scratch>/provoke_mantel34.py` (Stage P: `....FAIL!`, the traceback
  reading `(47.837, -83.031, 45.609)`, the instant `2700`'s centroid,
  while `0.0` read `(65.434, -65.434, 70.495)`).

## 2. Red tests

All in `tests/test_manager_test.py` (design.md, Decision 7). New fixtures
go in this file, never in `tests/meta_project/`, whose every `test_*.py`
the golden recorders walk.

- [ ] 2.1 RED A `FakeNode` fixture swept `with_instants(0, 0.5, 1)`,
  raising `AssertionError('first, at 0')` at `0` and `ValueError('last, at
  1')` at `1`: the output of `run_class_tests` contains `first, at 0` and
  not `last, at 1`, and contains `FAIL! at instant 0 (2 of 3 instants
  failed)`.
- [ ] 2.2 RED The same fixture with `runner.failfast = True`: calls are
  `[0]` and the output contains `FAIL! at instant 0 (--failfast stopped
  the sweep at instant 1 of 3)`.
- [ ] 2.3 RED `with_instants(0.5)` failing: the output contains `FAIL! at
  instant 0.5\n`; `with_instants(0, 1 / 48)` failing at the second: `FAIL!
  at instant 0.020833333333333332 (1 of 2 instants failed)` (subtests).
- [ ] 2.4 GUARD `FirstTestFailsNode` (no instants declared): the line of
  `test_a_fails` ends `FAIL!\n` exactly. Green both ways.
- [ ] 2.5 RED Replace `test_a_non_skip_setup_error_still_propagates` with
  a test that `SetupRaisesCase` (given a second method and a `tearDown`
  that records its call) yields from `run_class_tests`: no exception, two
  errors (`runner.num_errors == 2`), `ERROR! (setUp raised)` and `setup
  blew up` in the output, no `tearDown` call. Red today: `RuntimeError`
  escapes.
- [ ] 2.6 RED A case whose `setUpClass` raises `RuntimeError('class set-up
  blew up')`, with two methods recording their calls and a `tearDownClass`
  recording its call: no exception, two errors, the message printed once,
  no method called, `tearDownClass` not called.
- [ ] 2.7 RED A case whose `setUpClass` raises `unittest.SkipTest('no
  B-rep engine here')`, with two methods: two skipped, the reason in the
  output, no method called, no error.
- [ ] 2.8 RED `--failfast` with `SetupRaisesCase` through `run_tests()`:
  one error, the second method never set up, the summary line printed.
- [ ] 2.9 RED A method marked `@unittest.expectedFailure` on a case whose
  `setUp` raises: one error, no expected failure.
- [ ] 2.10 GUARD `bdb.BdbQuit` raised from `setUp` propagates out of
  `run_class_tests`. Green both ways.
- [ ] 2.11 RED `ReportSummaryLineTest`: with `num_errors` 1 (and one
  failed, one skipped) the line contains `1 failed, 1 error, 1 skipped`;
  with 2, `2 errors`. The existing default-line test stays as it is.
- [ ] 2.12 RED End to end through `Runner().handle`, on
  `MultiTestCaseFixture` scratch projects (beside
  `UnusualResultExitCodeTest`): (a) the two-way failing sweep: exit 1, the
  first message only, `FAIL! at instant 0 (2 of 3 instants failed)`, a
  summary line; (b) a `setUp`-raising case of two methods, then a passing
  case: exit 1, `: 1 passed, 0 failed, 2 errors` and the passing method's
  `passed`; (c) a `setUpClass`-raising case, then a passing case: exit 1,
  `: 1 passed, 0 failed, 1 error`. Red today: (a) prints the last message
  and no instant; (b) and (c) raise out of `handle`.
- [ ] 2.13 Run section 2's tests on the unmodified runner and record each
  red with its reason in `evidence.md`.

## 3. The change

`machinome/manager/test.py` only (design.md, Decision 6).

- [ ] 3.1 `Test.__init__`: `self.num_errors = 0`.
- [ ] 3.2 Module-level `_instant_text(instant)` (design.md, Decision 2).
- [ ] 3.3 `Test._skip_class(klass, class_name, reason)`: the class-skip
  loop moved out of `run_class_tests`, unchanged in output.
- [ ] 3.4 `Test._record_error(label, phase, text)` (Decision 6).
- [ ] 3.5 `run_class_tests`: guard `setUpClass` — `unittest.SkipTest` to
  `_skip_class`, `bdb.BdbQuit` re-raised, `Exception` to one
  `_record_error` per `test_` method, the traceback passed to the first
  only, each counted in `num_tests`; return before the methods and before
  `tearDownClass`.
- [ ] 3.6 `run_test`: after the `SkipTest` arm of `setUp`, `bdb.BdbQuit`
  re-raised and `Exception` to `_record_error(f'{class_name}.{name}',
  'setUp', traceback text)` then return; the outer `finally` calls
  `tearDown` only when `setUp` did not raise.
- [ ] 3.7 `run_test`: enumerate the instants; keep the first failure as
  `(instant, position, text)`; set `stopped` where `--failfast` breaks;
  write `FAIL!` and the continuation of Decision 2; print the kept text.
- [ ] 3.8 `report`: `, E errors` / `, 1 error` after `F failed`.
- [ ] 3.9 `handle`: exit 1 when `num_failed or num_errors or
  num_unexpected_successes`.

## 4. Green

- [ ] 4.1 Section 2's tests pass; `pytest -q -p no:cacheprovider
  tests/test_manager_test.py` whole; record counts and time.
- [ ] 4.2 Alone, `pytest -q -p no:cacheprovider tests/test_meta.py`
  (its `FAIL!` classification and the `\.\.FAIL!` failfast pin); record.
- [ ] 4.3 Rerun the four scratch projects (1.3) and record: the sweep's
  first message and its instant line; `ERROR!` lines, summary lines and
  `BAfterTest` passing in the three set-up projects; the skip project's
  `skipped: no B-rep engine here` and exit 0.

## 5. Project validation

- [ ] 5.1 In `<Clocks>`, the same mantel clock 34 run as 1.4: the same
  20 tests, 15 passed, 5 failed, the same `AssertionError` lines; record
  the five `FAIL!` lines, each now naming its instant (the three sweeps
  with their counts), and the wall time. If any count or message moved,
  stop and report: this change moves no verdict.
- [ ] 5.2 `python <scratch>/provoke_mantel34.py`: expect `FAIL! at
  instant 0.0 (4 of 4 instants failed)` and the traceback reading
  `(65.434, -65.434, 70.495)`; record.
- [ ] 5.3 `git -C <Clocks> status --short`: unchanged from 1.4.

## 6. Documentation and records

- [ ] 6.1 `docs/reference/cli.rst`, "machinome test": the summary line
  with `, E errors` and its order, the exit status on an error, an error
  in set-up reported and the run continuing, a failing method's line
  naming its first failing instant with the count, and `--failfast`
  stopping on an error — each fact changed in place in the existing
  paragraphs, nothing else added.
- [ ] 6.2 `docs/reference/assertions.rst`, "Instants": one sentence that a
  failing sweep is reported at its first failing instant, named so it can
  be written into `@testing_instant`, with how many instants failed.
  "Skipping a test and marking a known gap": `setUpClass` among the places
  a skip may be declared.
- [ ] 6.3 `docs/architecture.md`, "Test framework": the sentence listing a
  method's verdicts gains ERROR for an exception in set-up.
- [ ] 6.4 `docs/project/changelog.rst`, under `Unreleased`: one bullet
  naming the change (`report-the-instant`) in the shape of the bullets
  above it.
- [ ] 6.5 `workflow/warts.md`: move the three entries of
  "honour-skip-and-xfail (2026-09-15, found while fixing)" verbatim to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md` under a heading
  `report-the-instant`, with a "What shipped" paragraph; delete the
  section (heading and preamble) from `warts.md`. File one new entry in
  `warts.md` under a heading naming this change (2026-10-07): an exception
  from `tearDown` or `tearDownClass` still escapes the runner and stops the
  run with no summary line (design.md, Open Questions, 2).
- [ ] 6.6 `workflow/ongoing/fix-warts-3.md`, "Progress": one line for cycle
  13.

## 7. Sync, archive and checks

- [ ] 7.1 Sync the delta spec into `openspec/specs/test-framework/spec.md`
  (two ADDED requirements, two MODIFIED requirements replaced whole).
- [ ] 7.2 Archive the change to
  `openspec/changes/archive/<date>-report-the-instant/`; `openspec
  validate --all` (or the archived change and `test-framework`) passes.
- [ ] 7.3 `black --check` and `flake8 --max-line-length=89` on
  `machinome/manager/test.py` and `tests/test_manager_test.py`.
- [ ] 7.4 `tests/test_manager_test.py` once more, then the full suite
  once, alone; record counts and time. Leave everything uncommitted.
