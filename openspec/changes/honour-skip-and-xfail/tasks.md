# Tasks — honour skip and expected failure

Red first: every test in section 1 must fail against the current code, for the
stated reason, before anything in section 2 is written. One commit for the
planning artifacts, one for the implementation; no intermediate commits.

All work is in `solid_node/manager/test.py`; no other module changes.

## 1. Prove the failure

- [ ] 1.1 Add `SkipAndExpectedFailureTest` to `tests/test_manager_test.py`,
  beside the existing `FailfastInstantsLoopTest`/`FailfastAbortsRunTest`
  classes, reusing this file's `FakeNode` and `with_instants` helpers
  (`tests/test_manager_test.py:24-72`) and the
  `run_class_tests_capturing_stdout` / `run_tests` seams, so nothing is built.
  Against the current code each of the following is RED for the recorded
  reason:
  - a method calling `self.skipTest('reason')` at its only instant counts as
    `num_skipped == 1`, `num_failed == 0`, and the output says ` skipped` with
    the reason — RED: `unittest.SkipTest` is caught by the bare
    `except Exception` at `manager/test.py:351` and counted at `:362`, so it
    reports `FAIL!` and `num_failed == 1` (`evidence.md`, measurement 1);
  - a method decorated `@unittest.expectedFailure` that raises counts as
    `num_expected_failures == 1`, `num_failed == 0`, and NO traceback is
    printed — RED: it is an ordinary failure today;
  - a method decorated `@unittest.expectedFailure` that does not raise counts
    as `num_unexpected_successes == 1`, `num_passed == 0`, and the output says
    `UNEXPECTED SUCCESS!` — RED: it prints ` passed` and is counted in
    `num_passed`;
  - a method over three instants that skips at the middle one only: all three
    bodies run, verdict PASSED, output names the skipped instant count,
    `num_passed == 1` — RED: reported `FAIL!` today (measurement 2);
  - a method over three instants that skips at every instant: `num_skipped ==
    1` (one test, not three) — RED;
  - a method over three instants that FAILS at instant 0 and SKIPS at instant
    2: verdict FAILED and the printed traceback is the `AssertionError`, not
    the `SkipTest` — RED: `error` is rebound at `:353` on every raising
    instant and only the last is printed at `:376`
    (measurement 2, section F);
  - a marked method over three instants raising at one instant: one expected
    failure, every instant run — RED;
  - a marked method whose every instant skips: SKIPPED, not expected failure
    and not unexpected success — RED (the precedence `unittest` itself uses,
    measurement 1);
  - a class carrying `@unittest.skip('why')`: no body runs, `setUpClass` is
    not called, each `test_` method counts once as skipped — RED: both bodies
    run and both are counted passed today (measurement 5);
  - a case whose `setUp` calls `self.skipTest('why')`: the method is
    reported skipped with the reason, `num_skipped == 1`, no instant body
    runs, `tearDown` still runs, and the NEXT test still runs — RED today:
    the `SkipTest` escapes `run_test` (`:330-331` has no `except`) and
    aborts the run (reviewer's note 1). Beside it, a guard that a `setUp`
    raising `RuntimeError` still propagates exactly as today;
  - a sweep whose instant 0 adds an operation to a child and whose instant 1
    skips: instant 2 starts from restored children (reviewer's note 3);
  - with `failfast=True`: a skipping instant does NOT break the sweep — RED,
    it breaks at `:369` today (measurement 2, section D); a marked method's
    raising instant does not break the sweep or the run — RED; an unexpected
    success DOES stop the run — RED.
- [ ] 1.2 Add to the same file the summary-and-exit assertions:
  - `report()` prints exactly `Ran N tests in X seconds: P passed, F failed`
    when nothing was skipped, expected, or unexpectedly successful — GREEN
    today and the guard that this change does not move it (`manager/test.py:286-287`,
    ADR-090, and the ratified "An exact run reads as it always did");
  - `report()` continues with `, 1 skipped`, `, 2 expected failures`,
    `, 1 unexpected success` for each non-zero count, BEFORE the
    parenthesised faceted/quantum note (`:288-299`) — RED;
  - the exit rule: a run whose only unusual result is a skip exits 0, and a
    run containing an unexpected success exits 1 (`:179-180`) — RED both ways.
    Drive `handle` or assert on the counters the exit reads, whichever keeps
    the test free of a build.
- [ ] 1.3 Run it and record which assertions are red and why:
  `PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_manager_test.py -x -q`.

## 2. Make it green

- [ ] 2.1 `manager/test.py`: add `num_skipped`, `num_expected_failures`,
  `num_unexpected_successes` to `__init__` (`:48-52`).
- [ ] 2.1a `run_test`: wrap the `setUp` call so that `unittest.SkipTest`
  raised there reports the method as skipped (reason printed, `num_skipped`
  += 1, no instant run) and returns; every other exception propagates as
  today. `tearDown` keeps running through the existing `finally`.
- [ ] 2.2 `run_test` (`:325-383`): add an `except unittest.SkipTest` arm
  BEFORE the `except Exception` arm (`SkipTest` IS an `Exception`; order is
  the whole mechanism), counting `step_skip`, keeping the first reason, and
  printing the new per-instant character `s` in yellow. Leave `error`
  assigned only in the `except Exception` arm, so a skip can never overwrite
  a real failure's traceback. Keep `restore_children_checkpoints` after every
  instant, skipped ones included (`:366-368`).
- [ ] 2.3 `run_test`: compute the verdict from `step_pass`/`step_fail`/
  `step_skip` and `getattr(method, '__unittest_expecting_failure__', False)`,
  per the table in `design.md` §"The method's verdict follows its instants",
  and write the verdict word. ` passed` and `FAIL!` keep their exact present
  spelling for a method with no skips and no marking.
- [ ] 2.4 `run_test`: the failfast break at `:369` fires only on a REAL
  failure (an instant that raised, in a method not marked expected-to-fail);
  the run-level `raise StopTestRun()` at `:378-379` fires on FAILED or
  UNEXPECTED SUCCESS.
- [ ] 2.5 `run_class_tests` (`:311-323`): before `setUpClass`, honour
  `getattr(klass, '__unittest_skip__', False)` — count each `test_`-prefixed
  attribute once as skipped with `__unittest_skip_why__`, print one line each,
  and return without running `setUpClass`/`tearDownClass`.
- [ ] 2.6 `report` (`:285-300`): append `, S skipped`, `, X expected
  failures`, `, U unexpected successes` for each non-zero count, before the
  parenthesised notes. Singular/plural: match the counts' own wording in the
  tests written in 1.2 and keep it consistent.
- [ ] 2.7 `handle` (`:179-180`): exit 1 when `num_failed` or
  `num_unexpected_successes`. `run_tests` (`:302-308`) still does not exit.
- [ ] 2.8 Re-run `tests/test_manager_test.py` green.

## 3. Prove nothing else moved

- [ ] 3.1 `tests/test_manager_test.py`, `tests/test_named_models.py`,
  `tests/test_cli.py`, `tests/test_cli_lazy_imports.py`,
  `tests/test_meta.py`, `tests/test_mesh_engine_dependency.py` — green. The
  three after `test_cli.py` read the summary line or the command registry.
- [ ] 3.2 The whole suite once before the implementation commit, with its
  summary line and exit code recorded in `evidence.md`.
- [ ] 3.3 Re-run `evidence/run-probes.sh` and record the new transcripts
  beside the old ones in `evidence.md` under an "After" heading, so the
  before/after is one document. The three measurements of the proposal must
  read: skipped → exit 0; expected failure → exit 0; unexpected success →
  exit 1.
- [ ] 3.4 Remove `evidence/skip_xfail_project/_build/` and every
  `__pycache__/` the probes created under the fixture before committing.

## 4. Documentation and record

- [ ] 4.1 `docs/cli.rst` (`solid test`, `:111-156`): the summary line's new
  counts, the exit rule, and one sentence each for skipping and for marking a
  known gap; correct `--failfast`'s "stop on the first failure" to say a skip
  and an expected failure are not failures.
- [ ] 4.2 `docs/testing.rst`: a short section — how to skip a test that does
  not apply (`self.skipTest(reason)`, `@unittest.skip`, a skipped class), how
  to record a known gap (`@unittest.expectedFailure`), that the unit of a skip
  is the instant, and that an expected failure which starts passing fails the
  run.
- [ ] 4.3 `docs/changelog.rst`: one line.
- [ ] 4.4 `docs/adrs/TEST-FRAMEWORK/ADR-117-an-unexpected-success-fails-the-run.md`:
  accept ADR-117 per `design.md` §"Why this is an ADR", and add its row to
  `docs/adrs/README.md` in chronological order.
- [ ] 4.5 `docs/architecture.md`, "Test framework (TEST-FRAMEWORK · spec
  `test-framework`)" (`:1324-1342`): that section describes the runner's
  per-instant execution and says nothing about verdicts or the exit code
  (grep finds no `exit 1` in the file). Add one sentence naming the three
  new verdicts and ADR-117 — the overview is the reference, so it must
  reflect the accepted ADR.
- [ ] 4.6 `workflow/warts.md`: mark the
  "# Internal-Cycloidal-Actuator (2026-09-06, STEP import cycles)" bullet (c)
  fixed, naming this change; add the out-of-scope findings as new entries so
  they are not lost — the last-failing-instant traceback (`:353`/`:376`),
  the absence of any per-instant location in a failure report, and that a
  non-skip exception from `setUp` or any exception from `setUpClass` aborts
  the run without a verdict (reviewer's note 1).
- [ ] 4.7 Sync the `test-framework` delta into `openspec/specs/` and archive
  the change.

## 5. Not in this change

- Reporting the FIRST failing instant rather than the last.
- Naming the instant a failure happened at.
- `unittest`'s `subTest`, and skips raised from `setUpClass`.
- `--all`/`record_model_failure` (`:229-239`): a model that cannot be built is
  a failure, not a skip.
- `shop-skills/solid-node-api/SKILL.md:1050` (another repository) documents the
  summary line and the exit rule and will need the same correction; a
  follow-up for the reviewer.
