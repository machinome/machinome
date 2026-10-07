## Context

### Reproduction at `f8d19a1`

Bench `/home/asa/devel/machinome/machinome/WTs/fix-warts-3`, branch
`fix-warts-3`, `git rev-parse HEAD` =
`f8d19a11c7d6afe43b4707ea9716c4dc868ccf91`, clean tree.
`python -c 'import machinome; print(machinome.__file__)'` under
`PYTHONPATH=<bench>` prints `<bench>/machinome/__init__.py`.

`<scratch>` is the campaign scratchpad's `cycle13/` directory,
`/tmp/claude-1000/-home-asa-devel-machinome/ba39ba63-e521-4122-987c-3d17c62c72c6/scratchpad/cycle13`.
`<scratch>/repro/` is a scratch project: `pyproject.toml`
(`[tool.machinome]`, `model = "boat.sweep:Sweep"`), and in `boat/` four
one-cube `Solid2Node` modules, each with a companion:

- `sweep.py` / `test_sweep.py`: `SweepTest.test_fails_at_two_instants_differently`,
  `@testing_steps(3)` (instants `0`, `0.5`, `1`), raising
  `AssertionError('first failure, at the first instant')` at the first and
  `ValueError('second failure, at the last instant')` at the last (a leaf
  keeps no time, so a class-level call counter says which instant runs);
  and a passing `test_after_the_sweep`.
- `setup.py` / `test_setup.py`: `ASetUpRaisesTest`, whose `setUp` raises
  `RuntimeError('setUp blew up')`, with `test_a` and `test_b`; then
  `BAfterTest.test_after`, which passes.
- `setupclass.py` / `test_setupclass.py`: `ASetUpClassRaisesTest`, whose
  `setUpClass` raises `RuntimeError('setUpClass blew up')`, with `test_a`;
  then `BAfterTest.test_after`.
- `skipclass.py` / `test_skipclass.py`: `ASetUpClassSkipsTest`, whose
  `setUpClass` raises `unittest.SkipTest('no B-rep engine here')`, with
  `test_a`; then `BAfterTest.test_after`.

Each run alone, `env -C <scratch>/repro -u SOLID_BUILD_DIR
PYTHONPATH=<bench> /home/asa/devel/machinome/.venv/bin/python -c 'from
machinome.cli import manage; manage()' test boat/<name>.py` (build
chatter and traceback source lines omitted):

```text
=== machinome test boat/sweep.py
Running SweepTest.test_after_the_sweep. passed
Running SweepTest.test_fails_at_two_instants_differently...FAIL!
Traceback (most recent call last):
  File "<bench>/machinome/manager/test.py", line 429, in run_test
  File "<scratch>/repro/boat/test_sweep.py", line 22, in test_fails_at_two_instants_differently
ValueError: second failure, at the last instant

Ran 2 tests in 0.13 seconds: 1 passed, 1 failed
exit: 1
=== machinome test boat/setup.py
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "<bench>/machinome/cli.py", line 207, in manage
  File "<bench>/machinome/manager/test.py", line 198, in handle
  File "<bench>/machinome/manager/test.py", line 310, in run_selection
  File "<bench>/machinome/manager/test.py", line 386, in run_class_tests
  File "<bench>/machinome/manager/test.py", line 403, in run_test
  File "<scratch>/repro/boat/test_setup.py", line 11, in setUp
RuntimeError: setUp blew up
exit: 1
=== machinome test boat/setupclass.py
Traceback (most recent call last):
  ...
  File "<bench>/machinome/manager/test.py", line 379, in run_class_tests
  File "<scratch>/repro/boat/test_setupclass.py", line 12, in setUpClass
RuntimeError: setUpClass blew up
exit: 1
=== machinome test boat/skipclass.py
Traceback (most recent call last):
  ...
  File "<bench>/machinome/manager/test.py", line 379, in run_class_tests
  File "<scratch>/repro/boat/test_skipclass.py", line 14, in setUpClass
unittest.case.SkipTest: no B-rep engine here
exit: 1
```

The sweep's first failure is not printed and no instant is named. Each
set-up exception ends the run with no `Running` line for the method, no
summary line, and `BAfterTest` never runs; the exit status, 1, is
Python's for an uncaught exception. The skip raised by `setUpClass` is
not even honoured as a skip, although the requirement "A skipped test is
not a failure" says a test declaring itself inapplicable "by raising the
skip exception any other way" is reported skipped.

Where it comes from, `machinome/manager/test.py`:

- `run_test` (`:391`) rebinds `error` in the instants loop's `except
  Exception` arm on every raising instant and prints `error[2]` once,
  after the loop (`:441`, `:474`). The loop variable `instant` is never
  printed.
- `run_test` calls `self.test_case.setUp()` inside `try: ... except
  unittest.SkipTest` (`:401`); anything else escapes, through the outer
  `finally`, which calls `tearDown` and then lets it propagate.
- `run_class_tests` calls `klass.setUpClass()` (`:379`) and
  `klass.tearDownClass()` (`:389`) unguarded.
- `handle` catches only `StopTestRun` (`:199`); its `finally` flushes the
  verdict store, and `report` is never reached.

### 3DPrintedClocks' mantel clock 34

`<Clocks>` = `/home/asa/devel/machinome/projects/3DPrintedClocks` at
`ec2a05d`; `git -C <Clocks> status --short` shows ` M
screenshots/wall_clock_03.png` and `?? WTs/`, neither ours. Mantel clock 34
is the campaign's measured clock (cycle 6 ran it in 24 to 43 s), and its
suite carries sweeps of 8, 48 and 32 instants that fail, so it exercises
both the instant report and a real sweep's count.

`env -C <Clocks> PYTHONPATH=<bench>:<Clocks>
/home/asa/devel/machinome/.venv/bin/machinome test mantel_clock_34_steampunk
--mesh --volume-epsilon 0.001` (exit 1, wall 46.40 s,
`<scratch>/mantel34-before.txt`):

```text
Running MantelClock34SteampunkTest.test_assembly_integrity........FAIL!
Running MantelClock34SteampunkTest.test_movement_runs_free_through_a_swing................................................FAIL!
Running MantelClock34SteampunkTest.test_solid_integrity.FAIL!
Running MantelClock34SteampunkTest.test_source_body_inventory.FAIL!
Running MantelClock34SteampunkTest.test_the_train_meshes_all_the_way_round................................FAIL!
...
Ran 20 tests in 43.12 seconds: 15 passed, 5 failed (mesh engine, volume epsilon 0.001 mm³)
```

Captured to a file the marks carry no colour (`termcolor` 2.4.0 writes
none when standard output is not a terminal): the log cannot say which of the 8, 48 or 32
instants failed. Each of the three sweeps' tracebacks ends
`AssertionError: movement.pendulum.bob.shell should not interfere with
movement.pendulum.bob.lid_screw_right (intersection volume
1.7215580128600183)`: a collision that does not move with the clock, so
which instant's traceback is printed cannot be told from the message here,
which is why the provoked case below carries an instant-dependent value.

`<scratch>/provoke_mantel34.py`, run as `env -C <Clocks>
PYTHONPATH=<bench>:<Clocks> /home/asa/devel/machinome/.venv/bin/python
<scratch>/provoke_mantel34.py` (exit 1, wall 9.74 s,
`<scratch>/provoke-before.txt`), builds the clock's root with the
runner's own `build_node`, binds a scratch `ProvokedTest(TestCase)` (node
`MantelClock34Steampunk`) whose one method,
`@testing_steps(4, end=2700)`, asserts the minute hand's centroid equals
`()`, and runs it through `Test.run_tests` (the `run_class_tests` /
`run_test` path `machinome test` takes). It records each instant's
reading and prints them after the run:

```text
Running ProvokedTest.test_the_minute_hand_never_moves....FAIL!
...
AssertionError: Tuples differ: (47.837, -83.031, 45.609) != ()
...
Ran 1 tests in 0.04 seconds: 0 passed, 1 failed (mesh engine, volume epsilon 0.001 mm³, verdict store off)
probe: instant 0.0 read the minute hand at (65.434, -65.434, 70.495)
probe: instant 900.0 read the minute hand at (83.031, -47.837, 45.608)
probe: instant 1800.0 read the minute hand at (65.434, -65.434, 20.722)
probe: instant 2700 read the minute hand at (47.837, -83.031, 45.609)
```

The printed failure is the last instant's (`2700`); the first failing
instant was `0.0`. `git -C <Clocks> status --short` afterwards: unchanged.

### Focused tests at `f8d19a1`

`env -C <bench> PYTHONPATH=<bench> .venv/bin/pytest -q -p no:cacheprovider
tests/test_manager_test.py`: 106 passed, 18 subtests passed, 1.93 s (2.37 s
wall). One of them pins the abort this change removes:
`SkipAndExpectedFailureTest.test_a_non_skip_setup_error_still_propagates`
asserts `RuntimeError` escapes `run_class_tests` — written in
`honour-skip-and-xfail` as "a green-both-ways guard, not a RED case", for
exactly the behaviour its reviewer filed as this finding.

### Who reads the runner's output

- **The summary line.** In the workspace's `scripts/` (`scan-projects`,
  `load-projects`, `rewrite-projects`), the studio's `floor/` (its MCP
  `machinome_test` tool returns the exit status and the raw output and
  parses neither) and `profiles/`, and the framework's CI
  (`.github/workflows/python-app.yml` runs `black`, `flake8` and `pytest`,
  never `machinome test`), nothing parses it. The framework's own tests
  match its prefix: `tests/test_meta.py` (`SUMMARY`, `(\d+) passed,
  (\d+) failed`), `tests/test_brep_engine_dependency.py` (`_summary`),
  `tests/mesh_engine_golden.py` (`Ran (\d+) tests in [\d.]+ seconds:
  (.*)$`) and several `assertIn('N passed, M failed', ...)`. Every one
  still matches a line with `, E errors` appended after `F failed`, and a
  run with no error prints the line unchanged. Where the line changes —
  a run with an error — today's run printed no summary line at all.
- **The per-method line.** `tests/test_meta.py` and
  `tests/test_verdict_store_cli.py` classify a `Running ...` line as failed
  when it contains `FAIL!`, `tests/mesh_engine_golden.py` and
  `tests/brep_engine_golden.py` the same; `tests/test_meta.py` pins
  `\.\.FAIL!` (and not `\.\.\.FAIL!`) for the `--failfast` run of
  `assembly_supported_lifted`. Keeping `FAIL!` immediately after the marks
  and adding the instant AFTER it leaves all of them matching. An `ERROR!`
  line would read as passed to those classifiers; no meta fixture raises in
  set-up, and the fixtures this change adds live in
  `tests/test_manager_test.py`, not in `tests/meta_project/`, whose every
  `test_*.py` the two golden recorders walk.
- **The manual.** `docs/reference/cli.rst` states the summary line, the
  exit status and `--failfast`; `docs/reference/assertions.rst`
  ("Instants", "Skipping a test and marking a known gap") the instants and
  skips; the tutorial quotes `Running CounterFitTest.<method>.FAIL!` twice
  (`docs/tutorial/06-fit.rst`) for methods that declare no instant, so its
  quotes stay right.
- **Outside the framework.** The studio's API skill states the summary
  line and the exit rule; it is another repository (proposal, "Deliberately
  out").

## Goals / Non-Goals

**Goals:**

- A failing method's report is the first failing instant's, names that
  instant in a form that can be written back into `@testing_instant`, and
  says how many instants failed.
- An exception in set-up gives the affected methods a verdict, ERROR,
  with the traceback; the run reports every other test and prints its
  summary line.
- A run with no error and no declared-instant failure prints exactly what
  it prints today.

**Non-Goals:**

- Reclassifying an exception raised by a test method itself (proposal,
  "Deliberately out").
- Guarding `tearDown` / `tearDownClass` (Open Questions, 2).
- Any change to skip, expected-failure or unexpected-success reporting
  beyond honouring a skip raised by `setUpClass`.
- Any change to what is built, what is compared, or a verdict.

## Decisions

### 1. The first failing instant's traceback is the one printed

In the instants loop, the `except Exception` arm keeps the traceback text
only when none is kept yet, with the instant and its 1-based position
among the declared instants; every failing instant still increments the
failure count. Nothing else in the loop changes: every instant still runs
(unless `--failfast` stops at a real failure, as today), the children are
still restored after each, and the verdict is decided by the same counts.

Alternatives: print every failing instant's traceback (a 48-instant sweep
failing on one static collision would print the same traceback 48 times —
mantel clock 34's three sweeps up to 88); print the first and the
last (a second choice of what is "representative", with no finding asking
for it). The first is the one a maker reproduces: it is where the machine
first went wrong, and with the instant named it is one
`@testing_instant(...)` away.

### 2. The failure line names the instant, for a method that declares its instants

The `FAIL!` written after the marks keeps its place — immediately after
the last mark — and is continued, for a method carrying
`testing_instants` (set by `@testing_instant` and `@testing_steps`, read
through the bound method as the loop already reads it), by:

- ` at instant T` — always;
- then, when the method declares more than one instant:
  - ` (K of N instants failed)` when the sweep ran to its end, K the
    failing instants and N the declared ones (skipped instants count in
    N, not in K);
  - ` (--failfast stopped the sweep at instant P of N)` when `--failfast`
    broke the loop at the failing instant P and P < N.

So: `FAIL! at instant 0.5`, `FAIL! at instant 0 (2 of 3 instants
failed)`, `FAIL! at instant 0.5 (--failfast stopped the sweep at
instant 2 of 3)`. A method with no `testing_instants` (it runs once at `0`
by default) prints `FAIL!` as today: it declared no instant, and the
tutorial's and every static project's output stays as it is.

T is printed by a private helper, `_instant_text(instant)`: `str(instant)`
for an `int` (not a `bool`), `repr(float(instant))` for anything `float()`
accepts — Python's shortest round-tripping spelling, so `0.25`, `900.0`,
`0.020833333333333332` — and `str(instant)` otherwise. The value is the one
handed to `set_keyframe`, so writing it into `@testing_instant(T)`
reproduces the instant exactly; under a root declaring a time base it is in
seconds, as the decorators say.

Alternatives: always name the instant (`FAIL! at instant 0` on every
undecorated failure, changing the tutorial's quotes and every static
project's log for no information); print `{instant:g}` (six significant
digits: `0.0208333` does not reproduce `1/48` exactly); name the step index
instead of the value (the index does not reproduce under another `steps`).
The words are on the line, not in colour, the discipline the skip
requirement set for a captured log.

### 3. An exception in set-up is an ERROR for the methods it denies a verdict

`setUp` (per method). In `run_test`, the existing `except
unittest.SkipTest` arm is followed by `except bdb.BdbQuit: raise` (a
developer's debugger quit still ends the run, as a quit in the method body
does) and `except Exception`, which records the method as an error: it
writes `Running <Class>.<method>`, then ` ERROR! (setUp raised)` in red,
then the traceback, counts one error, and returns; under `--failfast` it
raises `StopTestRun` after writing. No instant of the method runs.

`setUpClass` (per class). In `run_class_tests`, the call is guarded the
same way, in this order:

- `unittest.SkipTest` → every `test_` method of the class is reported
  skipped with the exception's text as its reason, exactly as the
  class-level skip decoration reports it (the existing loop, moved into a
  private helper both paths call), and the class's methods do not run.
- `bdb.BdbQuit` → re-raised.
- `Exception` → every `test_` method of the class is counted as a test and
  as an error, each written `Running <Class>.<method> ERROR! (setUpClass
  raised)`, the traceback printed once, after the first; no method runs.
  Under `--failfast` the run stops after the first.

Errors are counted per METHOD, not per class. That is the rule the class
skip already follows in this runner and in the ratified "A whole test
class declared skipped" scenario (each method counted once), and it keeps
`Ran N tests` the same whether a class's set-up works or not, so two runs
of one project compare. The alternative, one error per class as `unittest`
reports it, would make N shrink when set-up breaks and would need a
`Running <Class>.setUpClass` line no other outcome has (Open Questions, 1).

An expected-failure marking does not apply to set-up: a method marked
`@unittest.expectedFailure` whose `setUp` raises is an ERROR, not an
expected failure, which is what `unittest` reports (it applies the
expectation to the test method's own body).

A node's own test methods (`TestCaseMixin` on the node) go through the
same `run_class_tests`; `setUp` is called on the bound companion
`self.test_case`, as today.

### 4. What is not undone after a set-up that raised

After `setUp` raised, `tearDown` is not called; after `setUpClass` raised,
`tearDownClass` is not called. `unittest` does the same, because the
set-up those undo did not complete, and a `tearDown` that undoes a
half-made set-up commonly raises itself — which would abort the run this
change exists to keep going. The children's checkpoint restore in
`run_test`'s `finally` still runs. A `setUp` that SKIPS keeps calling
`tearDown`, as the ratified skip behaviour and its test
(`test_a_skip_declared_in_setup_skips_the_method_and_continues`, calls
`['setup', 'teardown', 'setup', 'teardown']`) pin; that is not changed
here.

### 5. The summary line and the exit status

`report` continues the line with `, E errors` (`, 1 error`) immediately
after `F failed`, only when E is not zero, before the skipped,
expected-failure and unexpected-success continuations and the engine note:
`Ran 5 tests in 1.00 seconds: 2 passed, 1 failed, 1 error, 1 skipped`. The
two counts that fail a run sit together, and every parser of the
`P passed, F failed` prefix still matches. `handle` exits 1 when
`num_failed or num_errors or num_unexpected_successes`. `--failfast`
"stops at the first test that fails the run", and an error fails the run.

Alternatives: count a set-up exception as a failure (no new count, but it
is not a statement about the machine that turned out false, and `unittest`,
which every companion `TestCase` and `pytest` run here already reads,
separates the two); a distinct exit status for errors (the exit status is
read as pass/fail by every caller; a set-up exception already exits 1
today).

### 6. Code shape

All in `machinome/manager/test.py`:

- `Test.__init__`: `self.num_errors = 0`.
- `_instant_text(instant)`: module-level, private (Decision 2).
- `Test._skip_class(klass, class_name, reason)`: the existing class-skip
  loop of `run_class_tests`, moved; called by the decoration path and by
  the `SkipTest` arm of the class set-up.
- `Test._record_error(label, phase, text)`: writes `Running {label}`, then
  `colored(f' ERROR! ({phase} raised)\n', 'red')`, then `text` when it is
  not `None`; increments `num_errors`; raises `StopTestRun` under
  `failfast`.
- `run_class_tests`: the guarded `setUpClass` (Decision 3); `tearDownClass`
  only after a set-up that completed.
- `run_test`: the guarded `setUp` and a flag that keeps `tearDown` from
  running after it raised (Decision 4); `enumerate` over the instants;
  the first failure kept as `(instant, position, text)`; a `stopped` flag
  set where `--failfast` breaks; the failure line of Decision 2.
- `report`: the error continuation (Decision 5).
- `handle`: the exit rule (Decision 5).

No public name is added; the `--failfast` help text ("Stop the test run on
the first error.") stays true.

### 7. Proof

Red first, in `tests/test_manager_test.py`, each seen failing on the
unmodified runner for the reason given:

- Unit, on the file's `FakeNode` fixtures (`with_instants` sets
  `testing_instants`):
  - a sweep at `(0, 0.5, 1)` raising `AssertionError('first, at 0')` at
    `0` and `ValueError('last, at 1')` at `1`: the output contains the
    first message and not the second (red: the second is printed), and the
    line `FAIL! at instant 0 (2 of 3 instants failed)` (red: no instant);
  - the same under `--failfast`: `FAIL! at instant 0 (--failfast stopped
    the sweep at instant 1 of 3)`, and the calls are `[0]`;
  - a single declared instant `0.5` failing: `FAIL! at instant 0.5\n`;
    and instants `(0, 1/48)` failing at the second: `at instant
    0.020833333333333332 (1 of 2 instants failed)`;
  - an undeclared failing method (`FirstTestFailsNode`): its line ends
    `FAIL!\n` exactly (green both ways: the guard that static output is
    unchanged);
  - `SetupRaisesCase` (two methods, `setUp` raising): `run_class_tests`
    returns, two errors, `ERROR! (setUp raised)` and the message in the
    output, no `tearDown` call; this replaces
    `test_a_non_skip_setup_error_still_propagates` (red: `RuntimeError`
    escapes);
  - a case whose `setUpClass` raises, two methods: two errors, the
    message printed once, no method body run, `tearDownClass` not called
    (red: it escapes);
  - a case whose `setUpClass` raises `unittest.SkipTest`: two skipped
    with the reason, no body run (red: it escapes);
  - `--failfast` with `SetupRaisesCase`: one error, then `StopTestRun`,
    the second method never set up (red);
  - a method marked `@unittest.expectedFailure` on a case whose `setUp`
    raises: one error, no expected failure (red: it escapes);
  - `bdb.BdbQuit` from `setUp` still propagates (green both ways);
  - `report` with `num_errors` 1 and 2: `..., 1 failed, 1 error, 1
    skipped` and `2 errors` (red: never printed); the existing
    "default run reports today's line unchanged" test stays green.
- End to end, through `Runner().handle` on `MultiTestCaseFixture` scratch
  projects (the shape of `UnusualResultExitCodeTest`):
  - the two-way failing sweep: exit 1, the first message only, the
    instant line, the summary line (red);
  - a `setUp`-raising case followed by a passing case: exit 1, `Ran 3
    tests in ...: 1 passed, 0 failed, 2 errors`, the passing case ran
    (red: `RuntimeError` escapes `handle`);
  - a `setUpClass`-raising case followed by a passing case: exit 1,
    `1 passed, 0 failed, 1 error` (red).

Then green, `tests/test_manager_test.py` whole, `tests/test_meta.py` alone
(its `FAIL!` classification and the `\.\.FAIL!` failfast pin), and the
full suite once.

In 3DPrintedClocks, against the bench, before and after: the documented
mantel clock 34 run, the same 20 tests, 15 passed, 5 failed, the same
`AssertionError` lines, each of the five `FAIL!` lines now naming its
instant (the three sweeps with their counts); and
`<scratch>/provoke_mantel34.py`, whose line becomes `FAIL! at instant 0.0
(4 of 4 instants failed)` with the traceback reading `(65.434, -65.434,
70.495)`, the first instant's centroid. The project is not edited.

### 8. No ADR

The exit status of a run whose set-up raised is 1 before and after; what
changes is that the run finishes and says why. The new outcome follows the
classification `unittest` already applies, which ADR-118 adopted as the
precedent for this runner's verdicts, and the summary-line discipline of
ADR-090 and ADR-118 (a run without the new outcome prints today's line).
No new architectural decision is made; the requirements carry it.

## Risks / Trade-offs

- The failure line of a method that declares its instants is one clause
  longer; a sweep failing at every instant still prints one traceback.
- A project whose `tearDown` assumed `setUp` completed, and which relied
  on `tearDown` running after `setUp` raised, loses that call. Today such
  a run aborted right after it, so nothing observable depended on it.
- The first failing instant may be a less interesting one than the last
  (a sweep that fails mildly first and badly later). The count says there
  is more, and the instant named lets the maker look at any one.

## Open Questions

1. **One error per method or per class for `setUpClass`?** Recommended and
   designed: per method (Decision 3). The ratifier may prefer `unittest`'s
   one-per-class; the change would be `_record_error` called once with the
   class name and `num_tests` incremented once. Answered by the
   orchestrator at ratification (7 October 2026): per method, as
   designed.
2. **Tear-down exceptions.** An exception from `tearDown` or
   `tearDownClass` still escapes and stops the run without a summary
   line, the same defect on the other side of the test. Recommended: out
   of this change, filed by the applier as a new `workflow/warts.md` entry
   under a heading naming this change, since no project has hit it.
   Answered by the orchestrator at ratification (7 October 2026): out of
   this change, filed as a finding; if taken in later, the same
   `_record_error` covers it with phase `tearDown`/`tearDownClass`.
3. **The studio's API skill** states the summary line and the exit rule
   (`shop-skills/machinome-api/SKILL.md`, "It prints `Ran N tests ...`");
   it gains `, E errors` and the error exit there. Another repository;
   for the campaign's outside-the-framework cycle, recorded there at
   ratification (7 October 2026).
