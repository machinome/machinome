# Evidence — `report-the-instant`

Cycle 13 of the fix-warts-3 campaign (`workflow/ongoing/fix-warts-3.md`).
Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3` (`<bench>`),
branch `fix-warts-3`; planning commit `1551d0d`
(`git -C <bench> rev-parse HEAD` =
`1551d0d81be06201f43f557a32ea0e18e8871ed5`, clean tree). Every framework
command ran as `env -C <bench> PYTHONPATH=<bench>
/home/asa/devel/machinome/.venv/bin/<tool> ...` (Python 3.12.3);
`python -c 'import machinome; print(machinome.__file__)'` printed
`<bench>/machinome/__init__.py`. `<Clocks>` is
`/home/asa/devel/machinome/projects/3DPrintedClocks` at `ec2a05d`, read and
run, never edited. `<scratch>` is the campaign scratchpad's `cycle13/`
directory (sources of its scratch project and probe at the end of this
file). One run of ours at a time, `ps -eo pid,args` checked before each
heavy one.

## 1. Baseline on the unmodified tree (`1551d0d`)

### 1.2 The runner's tests

```
$ pytest -q -p no:cacheprovider tests/test_manager_test.py
106 passed, 18 subtests passed in 1.98s        (wall 2.42 s)
```

### 1.3 The four scratch projects

`env -C <scratch>/repro -u SOLID_BUILD_DIR PYTHONPATH=<bench>
.../python -c 'from machinome.cli import manage; manage()' test
boat/<name>.py`, each alone; build chatter and traceback source lines
omitted; logs `<scratch>/a-<name>-before.txt`:

```
=== machinome test boat/sweep.py                         exit 1
Running SweepTest.test_after_the_sweep. passed
Running SweepTest.test_fails_at_two_instants_differently...FAIL!
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 429, in run_test
  File "<scratch>/repro/boat/test_sweep.py", line 22, in test_fails_at_two_instants_differently
ValueError: second failure, at the last instant

Ran 2 tests in 0.05 seconds: 1 passed, 1 failed
=== machinome test boat/setup.py                         exit 1
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<bench>/machinome/cli.py", line 207, in manage
  File "<bench>/machinome/manager/test.py", line 198, in handle
  File "<bench>/machinome/manager/test.py", line 310, in run_selection
  File "<bench>/machinome/manager/test.py", line 386, in run_class_tests
  File "<bench>/machinome/manager/test.py", line 403, in run_test
  File "<scratch>/repro/boat/test_setup.py", line 11, in setUp
RuntimeError: setUp blew up
=== machinome test boat/setupclass.py                    exit 1
Traceback (most recent call last):
  ... handle, run_selection
  File "<bench>/machinome/manager/test.py", line 379, in run_class_tests
  File "<scratch>/repro/boat/test_setupclass.py", line 12, in setUpClass
RuntimeError: setUpClass blew up
=== machinome test boat/skipclass.py                     exit 1
Traceback (most recent call last):
  ... handle, run_selection
  File "<bench>/machinome/manager/test.py", line 379, in run_class_tests
  File "<scratch>/repro/boat/test_skipclass.py", line 14, in setUpClass
unittest.case.SkipTest: no B-rep engine here
```

The same as Stage P recorded (design.md, Context): the last instant's
`ValueError` printed and no instant named; three bare tracebacks, no
`Running` line for the method, no summary line, `BAfterTest` never run.

### 1.4 3DPrintedClocks, mantel clock 34

`git -C <Clocks> status --short`: ` M screenshots/wall_clock_03.png`, `??
WTs/` (neither ours). Then `env -C <Clocks> PYTHONPATH=<bench>:<Clocks>
.../machinome test mantel_clock_34_steampunk --mesh --volume-epsilon 0.001`
(exit 1, wall 24.53 s, `<scratch>/a-mantel34-before.txt`):

```
Running MantelClock34SteampunkTest.test_assembly_integrity........FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_movement_runs_free_through_a_swing................................................FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Running MantelClock34SteampunkTest.test_solid_integrity.FAIL!
AssertionError: case.plates.edging should be one connected body, but its STL contains 6 connected bodies
Running MantelClock34SteampunkTest.test_source_body_inventory.FAIL!
AssertionError: ['root.case.plates.edging: case.plates.edging should be one connected body, ...'] is not false :
Running MantelClock34SteampunkTest.test_the_train_meshes_all_the_way_round................................FAIL!
AssertionError: movement.pendulum.bob.shell should not interfere with movement.pendulum.bob.lid_screw_right (intersection volume 1.7215580128600183)
Ran 20 tests in 21.29 seconds: 15 passed, 5 failed (mesh engine, volume epsilon 0.001 mm³)
```

(the inventory's message is shortened here; it is the same list of twelve
findings before and after, compared below). Then `env -C <Clocks>
PYTHONPATH=<bench>:<Clocks> .../python <scratch>/provoke_mantel34.py`
(exit 1, wall 10.01 s, `<scratch>/a-provoke-before.txt`):

```
Running ProvokedTest.test_the_minute_hand_never_moves....FAIL!
AssertionError: Tuples differ: (47.837, -83.031, 45.609) != ()
Ran 1 tests in 0.03 seconds: 0 passed, 1 failed (mesh engine, volume epsilon 0.001 mm³, verdict store off)
probe: instant 0.0 read the minute hand at (65.434, -65.434, 70.495)
probe: instant 900.0 read the minute hand at (83.031, -47.837, 45.608)
probe: instant 1800.0 read the minute hand at (65.434, -65.434, 20.722)
probe: instant 2700 read the minute hand at (47.837, -83.031, 45.609)
```

The printed failure is instant `2700`'s; the first failing instant was
`0.0`. `git -C <Clocks> status --short` afterwards: unchanged.

## 2. Red tests

In `tests/test_manager_test.py` (new fixtures beside the existing ones,
none in `tests/meta_project/`):

- `FirstFailingInstantTest` — 2.1
  `test_the_first_failing_instants_traceback_is_printed`
  (`FailsTwiceDifferentlyNode`, instants `0, 0.5, 1`); 2.2
  `test_failfast_names_the_instant_it_stopped_the_sweep_at`; 2.3
  `test_the_instant_is_written_so_that_it_reproduces` (subtests "one
  declared instant", `FailsAtItsOneInstantNode` at `0.5`, and "an instant
  that is not a round number", `FailsAtAFortyEighthNode` at `0, 1 / 48`);
  2.4 GUARD `test_a_method_declaring_no_instant_still_reads_fail`.
- `SetUpErrorTest` — 2.5
  `test_a_non_skip_setup_error_is_an_error_and_the_run_goes_on`
  (`SetupRaisesCase`, now with `test_b` and a recording `tearDown`; it
  replaces `SkipAndExpectedFailureTest.test_a_non_skip_setup_error_still_propagates`,
  deleted); 2.6 `test_a_class_set_up_error_is_an_error_of_each_method`
  (`set_up_class_raising(RuntimeError('class set-up blew up'))`, a fresh
  class per call recording `setUpClass`, `tearDownClass`, `setUp` and the
  two methods); 2.7 `test_a_skip_raised_by_class_set_up_skips_the_class`
  (the same factory with `unittest.SkipTest('no B-rep engine here')`; a
  `SkipTest` escaping is turned into `self.fail`, so it cannot read as a
  skipped test); 2.8 `test_failfast_stops_on_a_set_up_error` (through
  `run_tests()`); 2.9
  `test_an_expected_failure_whose_set_up_raises_is_an_error`
  (`SetupRaisesExpectedFailureCase`); 2.10 GUARD
  `test_a_debugger_quit_in_set_up_still_ends_the_run` (`SetupQuitsCase`).
- `ReportSummaryLineTest.test_errors_are_counted_beside_the_failures` —
  2.11, subtests `errors=1` and `errors=2`.
- `ReportTheInstantEndToEndTest(MultiTestCaseFixture)` — 2.12, through
  `Runner().handle`: (a) `test_a_sweep_reports_its_first_failing_instant`
  (`boat/gauge.py`, `@testing_steps(3)`), (b)
  `test_a_set_up_error_is_reported_and_the_run_goes_on` (`boat/pump.py`),
  (c) `test_a_class_set_up_error_is_reported_and_the_run_goes_on`
  (`boat/crane.py`).

### 2.13 Red on the unmodified runner

`pytest -q -p no:cacheprovider tests/test_manager_test.py -k
'FirstFailingInstantTest or SetUpErrorTest or
test_errors_are_counted_beside_the_failures or
ReportTheInstantEndToEndTest' -rA` (log `<scratch>/a-red.txt`):
`14 failed, 4 passed, 105 deselected in 1.78s`. The 14, each for the
reason its task names:

```
FAILED  FirstFailingInstantTest::test_failfast_names_the_instant_it_stopped_the_sweep_at
        'FAIL! at instant 0 (--failfast stopped the sweep at instant 1 of 3)\n' not found in 'Running FailsTwiceDifferentlyNode.test_sweep.FAIL!\nTraceback ...
FAILED  FirstFailingInstantTest::test_the_first_failing_instants_traceback_is_printed
        'first, at 0' not found in 'Running FailsTwiceDifferentlyNode.test_sweep...FAIL!\nTraceback ... ValueError: last, at 1
SUBFAILED[one declared instant] FirstFailingInstantTest::test_the_instant_is_written_so_that_it_reproduces
        '.FAIL! at instant 0.5\n' not found in 'Running FailsAtItsOneInstantNode.test_once.FAIL!\n...
SUBFAILED[an instant that is not a round number] (the same test)
        'FAIL! at instant 0.020833333333333332 (1 of 2 instants failed)\n' not found in 'Running FailsAtAFortyEighthNode.test_sweep..FAIL!\n...
FAILED  SetUpErrorTest::test_a_class_set_up_error_is_an_error_of_each_method
        RuntimeError: class set-up blew up            (escaped run_class_tests)
FAILED  SetUpErrorTest::test_a_non_skip_setup_error_is_an_error_and_the_run_goes_on
        RuntimeError: setup blew up                   (escaped run_class_tests)
FAILED  SetUpErrorTest::test_a_skip_raised_by_class_set_up_skips_the_class
        unittest.case.SkipTest: no B-rep engine here -> AssertionError: a SkipTest raised from setUpClass escaped run_class_tests instead of skipping the class
FAILED  SetUpErrorTest::test_an_expected_failure_whose_set_up_raises_is_an_error
        RuntimeError: setup blew up                   (escaped run_class_tests)
FAILED  SetUpErrorTest::test_failfast_stops_on_a_set_up_error
        RuntimeError: setup blew up                   (escaped run_tests)
SUBFAILED(errors=1) ReportSummaryLineTest::test_errors_are_counted_beside_the_failures
        'Ran 5 tests in 1.00 seconds: 2 passed, 1 failed, 1 error, 1 skipped\n' not found in '\nRan 5 tests in 1.00 seconds: 2 passed, 1 failed, 1 skipped\n'
SUBFAILED(errors=2) (the same test)
        'Ran 6 tests ...: 2 passed, 1 failed, 2 errors, 1 skipped\n' not found in '\nRan 6 tests ...: 2 passed, 1 failed, 1 skipped\n'
FAILED  ReportTheInstantEndToEndTest::test_a_class_set_up_error_is_reported_and_the_run_goes_on
        RuntimeError: setUpClass blew up              (escaped handle)
FAILED  ReportTheInstantEndToEndTest::test_a_set_up_error_is_reported_and_the_run_goes_on
        RuntimeError: setUp blew up                   (escaped handle)
FAILED  ReportTheInstantEndToEndTest::test_a_sweep_reports_its_first_failing_instant
        'first failure, at the first instant' not found in 'Running GaugeTest.test_fails_at_two_instants_differently...FAIL!\nTraceback ... ValueError: second failure, at the last instant ...
```

The four passing are the two guards, green both ways
(`test_a_method_declaring_no_instant_still_reads_fail`,
`test_a_debugger_quit_in_set_up_still_ends_the_run`), and the two
subtest-carrying parents, which pytest reports passed while their
subtests fail.

**A correction to the end-to-end tests, and the red seen again.** The
first green run (section 4) failed the three end-to-end tests on their
summary-line assertions alone: they expected the line to end right after
the counts (`': 0 passed, 1 failed\n'`), but under the test suite's
environment the line carries ` (verdict store off)`. The three assertions
became `assertRegex(stdout, r': ... ( \(|\n)')`. To see the corrected
file red on the unmodified runner, HEAD's tree was exported read-only
(`git -C <bench> archive HEAD | tar -x -C <scratch>/head`; its
`machinome/manager/test.py` compared identical to `git show
HEAD:machinome/manager/test.py`), the corrected
`tests/test_manager_test.py` copied over it, and the same selection run
there with `PYTHONPATH=<scratch>/head` (`machinome.__file__` under
`<scratch>/head`), log `<scratch>/a-red-final.txt`: `14 failed, 4 passed,
105 deselected in 1.82s`, the same 14 for the same reasons.

Task 2.12(a) named the sweep's line `FAIL! at instant 0 (2 of 3 instants
failed)`; the fixture's `@testing_steps(3)` hands the runner `0.0`, `0.5`,
`1` (`start + 0 * step` is a float), so the line is `FAIL! at instant 0.0
(2 of 3 instants failed)`, the value given to `set_keyframe`, as Decision
2 prescribes. The test asserts `0.0` and tasks.md 2.12(a) says so.

## 3. The change

`machinome/manager/test.py` only, as design.md Decision 6 lays it out:
`Test.__init__` gains `num_errors`; module-level `_instant_text`;
`Test._skip_class` (the class-skip loop moved, unchanged in output);
`Test._record_error`; `run_class_tests` guards `setUpClass` (`SkipTest` to
`_skip_class`, `BdbQuit` re-raised, any other exception one
`_record_error` per `test_` method, the traceback passed to the first
only, then return before the methods and `tearDownClass`); `run_test`
guards `setUp` (`BdbQuit` re-raised, any other exception
`_record_error(..., 'setUp', traceback)` and return, `tearDown` skipped in
the `finally` for both), enumerates the instants, keeps the first failure
as `(instant, position, text)`, sets `stopped` where `--failfast` breaks
before the last instant, and writes `FAIL!` with Decision 2's
continuation; `report` writes `, E error(s)` after `F failed`; `handle`
exits 1 on `num_errors`. The instants loop's `except Exception as e` lost
its unused `e` (the file's one pyflakes finding at HEAD). `StopTestRun`'s
docstring says "fails the run" for "fails".

## 4. Green

### 4.1 The runner's tests

```
$ pytest -q -p no:cacheprovider tests/test_manager_test.py -k '<the selection of 2.13>'
14 passed, 105 deselected, 4 subtests passed in 1.33s
$ pytest -q -p no:cacheprovider tests/test_manager_test.py
119 passed, 22 subtests passed in 2.19s        (wall 2.66 s)
```

(106 at baseline, one replaced, fourteen added; 18 subtests and four.)

### 4.2 The meta suite, alone

```
$ pytest -q -p no:cacheprovider tests/test_meta.py
62 passed in 82.16s (0:01:22)                  (exit 0, wall 82.51 s)
```

Its `FAIL!` classification and the `\.\.FAIL!` failfast pin hold: no meta
fixture declares instants on a failing method, so their lines read as
before.

### 4.3 The four scratch projects

Logs `<scratch>/a-<name>-after.txt`, filtered as in 1.3:

```
=== machinome test boat/sweep.py                         exit 1
Running SweepTest.test_after_the_sweep. passed
Running SweepTest.test_fails_at_two_instants_differently...FAIL! at instant 0.0 (2 of 3 instants failed)
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 506, in run_test
  File "<scratch>/repro/boat/test_sweep.py", line 20, in test_fails_at_two_instants_differently
AssertionError: first failure, at the first instant

Ran 2 tests in 0.05 seconds: 1 passed, 1 failed
=== machinome test boat/setup.py                         exit 1
Running ASetUpRaisesTest.test_a ERROR! (setUp raised)
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 464, in run_test
  File "<scratch>/repro/boat/test_setup.py", line 11, in setUp
RuntimeError: setUp blew up

Running ASetUpRaisesTest.test_b ERROR! (setUp raised)
Traceback (most recent call last):
  (the same)
RuntimeError: setUp blew up

Running BAfterTest.test_after. passed

Ran 3 tests in 0.06 seconds: 1 passed, 0 failed, 2 errors
=== machinome test boat/setupclass.py                    exit 1
Running ASetUpClassRaisesTest.test_a ERROR! (setUpClass raised)
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 389, in run_class_tests
  File "<scratch>/repro/boat/test_setupclass.py", line 12, in setUpClass
RuntimeError: setUpClass blew up

Running BAfterTest.test_after. passed

Ran 2 tests in 0.06 seconds: 1 passed, 0 failed, 1 error
=== machinome test boat/skipclass.py                     exit 0
Running ASetUpClassSkipsTest.test_a skipped: no B-rep engine here
Running BAfterTest.test_after. passed

Ran 2 tests in 0.06 seconds: 1 passed, 0 failed, 1 skipped
```

## 5. Project validation, 3DPrintedClocks

### 5.1 Mantel clock 34

The same command as 1.4 (exit 1, wall 46.25 s,
`<scratch>/a-mantel34-after.txt`):

```
Running MantelClock34SteampunkTest.test_assembly_integrity........FAIL! at instant 0.0 (8 of 8 instants failed)
Running MantelClock34SteampunkTest.test_movement_runs_free_through_a_swing................................................FAIL! at instant 0.0 (48 of 48 instants failed)
Running MantelClock34SteampunkTest.test_solid_integrity.FAIL! at instant 0
Running MantelClock34SteampunkTest.test_source_body_inventory.FAIL! at instant 0
Running MantelClock34SteampunkTest.test_the_train_meshes_all_the_way_round................................FAIL! at instant 0.0 (32 of 32 instants failed)
Ran 20 tests in 42.87 seconds: 15 passed, 5 failed (mesh engine, volume epsilon 0.001 mm³)
```

20 tests, 15 passed, 5 failed, as before. `diff` of the `AssertionError`
lines before and after: identical (exit 0). `diff` of every `Running` line
before and after with everything from `FAIL!` on cut: identical (exit 0),
so every pass and every mark is as before. `test_solid_integrity` and
`test_source_body_inventory` read `at instant 0` because the project's
shared base declares them `@testing_instant(0)`
(`<Clocks>/simulation/shared/testing.py:121`, `:125`); the three sweeps,
whose collision does not move with the clock, failed at every instant,
which the log could not say before (its marks carry no colour in a file).
The wall time (24.53 s before, 46.25 s after; the runner's own line 21.29 s
and 42.87 s) moved with the host: Stage P measured 43.12 s on the
unmodified tree, and the change adds no work per instant beyond keeping
one traceback.

### 5.2 The provoked failure

The same command as 1.4 (exit 1, wall 9.58 s,
`<scratch>/a-provoke-after.txt`):

```
Running ProvokedTest.test_the_minute_hand_never_moves....FAIL! at instant 0.0 (4 of 4 instants failed)
AssertionError: Tuples differ: (65.434, -65.434, 70.495) != ()
+ () : the minute hand stands at (65.434, -65.434, 70.495)
Ran 1 tests in 0.03 seconds: 0 passed, 1 failed (mesh engine, volume epsilon 0.001 mm³, verdict store off)
probe: instant 0.0 read the minute hand at (65.434, -65.434, 70.495)
probe: instant 900.0 read the minute hand at (83.031, -47.837, 45.608)
probe: instant 1800.0 read the minute hand at (65.434, -65.434, 20.722)
probe: instant 2700 read the minute hand at (47.837, -83.031, 45.609)
```

The traceback is now the first instant's, its centroid
`(65.434, -65.434, 70.495)`, and the line names instant `0.0`, which
`@testing_instant(0.0)` reproduces.

### 5.3 The project afterwards

`git -C <Clocks> status --short`: ` M screenshots/wall_clock_03.png`, `??
WTs/`, unchanged.

## 6. Documentation and records

- 6.1 `docs/reference/cli.rst`, "machinome test": the summary-line
  paragraph names `, E errors` first among the continuations, the exit
  rule "failed, errored or succeeded unexpectedly", the failure line
  naming the first failing instant with the count (`FAIL! at instant 0.25
  (3 of 48 instants failed)`) and `FAIL!` alone for a method declaring
  none, and a `setUp`/`setUpClass` exception reported `ERROR!` with the
  run going on; `--failfast`: "an unexpected success and an error do".
- 6.2 `docs/reference/assertions.rst`: "Instants" gains one sentence (a
  failing method reported at its first failing instant, with its
  traceback and the count, written so it can be given back to
  `@testing_instant`); "Skipping a test and marking a known gap" names
  `unittest.SkipTest` raised from `setUpClass`, which skips the class.
- 6.3 `docs/architecture.md`, "Test framework": the verdicts sentence
  gains ERROR for an exception from `setUp` or `setUpClass`, and that a
  failure is reported at its first failing instant, named.
- 6.4 `docs/project/changelog.rst`: one bullet at the end of the existing
  `Unreleased` section, "A failing test names the instant it failed at,
  and a set-up that raises is an error.", naming `report-the-instant`.
  `pytest -q -p no:cacheprovider tests/test_release_records.py`: `9
  passed, 58 subtests passed in 0.12s`.
- 6.5 The whole section "honour-skip-and-xfail (2026-09-15, found while
  fixing)" of `workflow/warts.md`, its introduction and three entries,
  moved verbatim to `workflow/archive/fix-warts-3-2026-10-06/resolved.md`
  under `## \`report-the-instant\``, with a "What shipped" paragraph, and
  deleted from `warts.md`. One new entry filed in `warts.md` under "##
  Findings from the framework cycle `report-the-instant` (2026-10-07)":
  an exception from `tearDown` or `tearDownClass` still aborts the run
  (design.md, Open Question 2). Seen on the changed bench with a scratch
  module `<scratch>/repro/boat/teardown.py` and its companion (sources
  below): `Running ATearDownRaisesTest.test_a.` then a bare traceback
  through `handle`, `run_selection`, `run_class_tests` and `run_test`
  (`self.test_case.tearDown()`), `RuntimeError: tearDown blew up`, exit 1,
  no summary line, `BAfterTest` never run (`<scratch>/a-teardown-after.txt`).
- 6.6 `workflow/ongoing/fix-warts-3.md`, "Progress": one line for this
  cycle, after cycle 12's.

## 7. Sync, archive and checks

- 7.1 / 7.2 `openspec validate report-the-instant`: "Change
  'report-the-instant' is valid". Then `openspec archive report-the-instant
  --yes` (openspec 1.6.0), the CLI's own sync: "Specs to update:
  test-framework: update", "+ 2 added", "~ 2 modified", "Totals: + 2, ~ 2,
  - 0, → 0", "Change 'report-the-instant' archived as
  '2026-10-07-report-the-instant'". Its warnings: the Why section's length,
  and 39 of 42 tasks complete (7.1, 7.2 and 7.4, done after it and ticked in
  the archived copy). Checked by script (`<scratch>/check_sync.py`, against
  a copy of the baseline taken before the archive): each of the four
  requirements appears once in `openspec/specs/test-framework/spec.md`, its
  text equal to the delta's (blank lines aside); no scenario title repeats;
  "Test runner lifecycle" has 15 scenarios (its 14 carried, one added) and
  "A skipped test is not a failure" 8 (its 7 carried, one added); the two
  added requirements have 5 each; 22 requirements before, 24 after, the
  other 20 unchanged. `openspec validate --specs`: `Totals: 45 passed, 0
  failed (45 items)`; `openspec validate test-framework`: valid.
- 7.3 Lint on `machinome/manager/test.py` and `tests/test_manager_test.py`,
  on the working tree and as at HEAD (HEAD's tree exported to
  `<scratch>/head/` with `git archive`, beside its own `setup.cfg`):
  - `flake8 --max-line-length=89` (pyenv shim, 7.3.0): 16 findings at
    HEAD, 15 after; compared with line numbers stripped, the one difference
    is HEAD's `machinome/manager/test.py` F841 (`local variable 'e' is
    assigned to but never used`, the instants loop's `except Exception as
    e`), which this change removed. The rest are pre-existing: in the
    runner E127 (the `machinome.test` import), E501 (90 columns, a
    `self.fail` line in `handle`) and E128 (`report`'s mesh note); in the
    test file E114/E116 on five comment lines and two E127.
  - `black --check` (26.5.1): both files "would reformat" at HEAD and
    after; neither follows black (black's diff at HEAD changes 261 lines of
    the runner and 911 of the test file). The new code is written in the
    files' own style, so black's diff grows to 283 and 1232 lines by that
    style alone. Nothing was reformatted.
- 7.4 The focused tests on the final tree:

  ```
  $ pytest -q -p no:cacheprovider tests/test_manager_test.py tests/test_release_records.py
  128 passed, 80 subtests passed in 2.28s        (wall 2.72 s)
  ```

  The full suite, alone (`ps` showed no run of ours), `pytest -q -p
  no:cacheprovider` at the bench root, log `<scratch>/full-suite.log`:

  ```
  4739 passed, 4 skipped, 55 warnings, 6677 subtests passed in 640.10s (0:10:40)   (exit 0, wall 642.58 s)
  ```

  (Cycle 12 closed at 4726 passed and 6673 subtests; this change adds
  thirteen tests net, fourteen new and one replaced, and four subtests.)

Everything is left uncommitted.

## Sources of the scratch project and the probe

`<scratch>/repro/pyproject.toml`:

```toml
[tool.machinome]
model = "boat.sweep:Sweep"
```

`boat/__init__.py` is empty. `boat/sweep.py`, `boat/setup.py`,
`boat/setupclass.py`, `boat/skipclass.py` and `boat/teardown.py` are one
node each, differing only in the class name (`Sweep`, `Setup`,
`SetupClass`, `SkipClass`, `Teardown`):

```python
from machinome.node.solid2 import Solid2Node
from solid2 import cube


class Sweep(Solid2Node):
    def render(self):
        return cube(1, center=True)
```

`boat/test_sweep.py`:

```python
from machinome.test import TestCase, testing_steps
from .sweep import Sweep


class SweepTest(TestCase):
    """Defects 1 and 2: a sweep failing at two instants, differently.

    `testing_steps(3)` runs the method at instants 0, 0.5 and 1; a leaf
    keeps no time of its own, so the call count says which instant ran.
    """

    node = Sweep
    calls = 0

    @testing_steps(3)
    def test_fails_at_two_instants_differently(self):
        call = SweepTest.calls
        SweepTest.calls += 1
        if call == 0:
            raise AssertionError('first failure, at the first instant')
        if call == 2:
            raise ValueError('second failure, at the last instant')

    def test_after_the_sweep(self):
        pass
```

`boat/test_setup.py`:

```python
from machinome.test import TestCase
from .setup import Setup


class ASetUpRaisesTest(TestCase):
    """Defect 3, setUp: a non-skip exception from setUp."""

    node = Setup

    def setUp(self):
        raise RuntimeError('setUp blew up')

    def test_a(self):
        pass

    def test_b(self):
        pass


class BAfterTest(TestCase):
    """Runs after the failing class (dir() and file order): never reached
    today."""

    node = Setup

    def test_after(self):
        pass
```

`boat/test_setupclass.py`:

```python
from machinome.test import TestCase
from .setupclass import SetupClass


class ASetUpClassRaisesTest(TestCase):
    """Defect 3, setUpClass: any exception from setUpClass."""

    node = SetupClass

    @classmethod
    def setUpClass(cls):
        raise RuntimeError('setUpClass blew up')

    def test_a(self):
        pass


class BAfterTest(TestCase):
    """Runs after the failing class: never reached today."""

    node = SetupClass

    def test_after(self):
        pass
```

`boat/test_skipclass.py`:

```python
import unittest

from machinome.test import TestCase
from .skipclass import SkipClass


class ASetUpClassSkipsTest(TestCase):
    """A skip declared in setUpClass: unittest skips the class."""

    node = SkipClass

    @classmethod
    def setUpClass(cls):
        raise unittest.SkipTest('no B-rep engine here')

    def test_a(self):
        pass


class BAfterTest(TestCase):

    node = SkipClass

    def test_after(self):
        pass
```

`boat/test_teardown.py` (written by the applier for 6.5):

```python
from machinome.test import TestCase
from .teardown import Teardown


class ATearDownRaisesTest(TestCase):
    """Out of report-the-instant: a tearDown that raises."""

    node = Teardown

    def tearDown(self):
        raise RuntimeError('tearDown blew up')

    def test_a(self):
        pass


class BAfterTest(TestCase):

    node = Teardown

    def test_after(self):
        pass
```

`<scratch>/provoke_mantel34.py`, run from `<Clocks>`:

```python
"""Provoked failure on 3DPrintedClocks' mantel clock 34, through the
runner's own instants loop.

A scratch companion case beside nothing: it subclasses the project's own
test case for its binding (`node = MantelClock34Steampunk`) and adds one
method swept over three quarters of an hour, whose assertion is
impossible and whose message carries the minute hand's centroid, so every
instant fails with a different message. The runner (`Test.run_tests`,
the same `run_class_tests`/`run_test` path `machinome test` uses) runs
only this method, on the clock's root built exactly as `machinome test`
builds it.

Run from the project directory with PYTHONPATH=<bench>:<project>. Nothing
is written in the project; the verdict store is off.
"""

import os
import sys

from machinome.manager.test import Test as Runner
from machinome.test import (TestCase, resolve_comparison_policy,
                             set_comparison_policy, testing_steps)
from simulation.mantel_clock_34_steampunk.clock import MantelClock34Steampunk


#: the centroid each instant read, in sweep order, printed after the run
SEEN = []


class ProvokedTest(TestCase):

    node = MantelClock34Steampunk

    @testing_steps(4, end=2700)
    def test_the_minute_hand_never_moves(self):
        hand = self.node.movement.motion_works.hands.minute_hand
        centroid = tuple(round(float(value), 3)
                         for value in hand.mesh.centroid)
        SEEN.append(centroid)
        self.assertEqual(centroid, (), 'the minute hand stands at '
                         f'{centroid}')


policy = resolve_comparison_policy('mesh', 0.001, None, False)
set_comparison_policy(policy)
runner = Runner()
runner.policy = policy
runner.node = runner.build_node('mantel_clock_34_steampunk')
case = ProvokedTest()
case.set_node(runner.node)
runner.test_case = None
runner.test_cases = [case]
# Only the provoked method: the node's own and the inherited contracts
# are the documented run's business, not this probe's.
for name in dir(case):
    if name.startswith('test_') and name != 'test_the_minute_hand_never_moves':
        setattr(case, name, None)
runner.run_class_tests = (lambda klass, node, run=runner.run_class_tests:
                          run(klass, node) if klass is case else None)
runner.run_tests()
instants = ProvokedTest.test_the_minute_hand_never_moves.testing_instants
for instant, centroid in zip(instants, SEEN):
    print(f'probe: instant {instant!r} read the minute hand at {centroid}')
sys.stdout.flush()
os._exit(1 if runner.num_failed else 0)
```
