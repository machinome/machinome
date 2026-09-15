# Evidence — honour skip and expected failure

Every line below was produced on this worktree (`solid-node`, branch
`fix-warts`, head `f409947`) by a probe under `evidence/`, with

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python
    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/solid

Re-run everything with `sh openspec/changes/honour-skip-and-xfail/evidence/run-probes.sh`
from the worktree root. It rewrites the `out-*.txt` transcripts quoted here.

Python is 3.12.3 — `out-unittest-reference.txt` carries the interpreter's
`sys.version` (`python 3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`;
stdout and stderr interleave in the capture, so it is not the first line). Long absolute paths inside quoted tracebacks are abridged to
`...` here; the transcripts hold them in full.

## What is under `evidence/`

| file | what it measures |
| --- | --- |
| `skip_xfail_project/` | a two-node Solid project (`widget.py`, `sweeper.py`) with companion tests calling `skipTest` and carrying `@unittest.expectedFailure` — the fixture `solid test` is run against |
| `probe_unittest_reference.py` | what `unittest` itself does with the same five methods: the semantics this change adopts |
| `probe_runner_mechanism.py` | `solid_node.manager.test.Test` driven directly, without a build: instants, tracebacks, failfast, the `unittest.skip` forms |
| `run-probes.sh` | runs all of it and captures the transcripts |
| `out-*.txt` | the captured transcripts, quoted below |

`solid test` builds the fixture, so running the probes creates
`evidence/skip_xfail_project/_build/` and `__pycache__/` **under the fixture's
own directory** and nowhere else. Both are removed from the change as
delivered; the script recreates them.

## Measurement 1 — the three outcomes today, through the CLI

`evidence/skip_xfail_project/test_widget.py` declares five methods: a plain
pass, a plain failure, `self.skipTest(...)`, an `@unittest.expectedFailure`
that raises, and an `@unittest.expectedFailure` that passes.

`solid test widget.py` (`out-cli-widget.txt`, build chatter filtered):

```
Running WidgetTest.test_expected_failure_passes. passed
Running WidgetTest.test_expected_failure_raises.FAIL!
Traceback (most recent call last):
  File ".../solid_node/manager/test.py", line 345, in run_test
    method()
  File ".../test_widget.py", line 16, in test_expected_failure_raises
    raise AssertionError('the known kernel gap')
AssertionError: the known kernel gap

Running WidgetTest.test_plain_fail.FAIL!
...
AssertionError: a real regression

Running WidgetTest.test_plain_pass. passed
Running WidgetTest.test_skipped.FAIL!
Traceback (most recent call last):
  File ".../solid_node/manager/test.py", line 345, in run_test
    method()
  File ".../test_widget.py", line 12, in test_skipped
    self.skipTest('the exact kernel is not available here')
  File "/usr/lib/python3.12/unittest/case.py", line 711, in skipTest
    raise SkipTest(reason)
unittest.case.SkipTest: the exact kernel is not available here


Ran 5 tests in 0.05 seconds: 2 passed, 3 failed

[exit code 1]
```

The three measurements the addendum asks for, read off that one run:

1. **`self.skipTest(...)`** → printed `FAIL!` with the `SkipTest` traceback,
   counted in `3 failed`, exit code **1**.
2. **`@unittest.expectedFailure` that raises** → printed `FAIL!` with the
   assertion's traceback, counted in `3 failed`, exit code **1**.
3. **`@unittest.expectedFailure` that passes** → printed ` passed`, counted
   in `2 passed`, contributing **0** to the exit code. The wrong marking is
   completely silent.

For comparison, `unittest` on the same five methods
(`out-unittest-reference.txt`):

```
test_expected_failure_passes ... unexpected success
test_expected_failure_raises ... expected failure
test_plain_fail ... FAIL
test_plain_pass ... ok
test_skipped ... skipped 'the exact kernel is not available here'

FAILED (failures=1, skipped=1, expected failures=1, unexpected successes=1)

testsRun=5 failures=1 errors=0 skipped=1 expectedFailures=1
unexpectedSuccesses=1 wasSuccessful=False
```

`wasSuccessful=False` with `failures=1` **and** `unexpectedSuccesses=1`: in
`unittest` an unexpected success alone fails a run. That is the exit-code
contract this change adopts (ADR-117).

Precedence, from the same probe — a test marked expected-to-fail that skips
instead:

```
=== skip inside an expectedFailure test
skipped=1 expectedFailures=0 unexpectedSuccesses=0 wasSuccessful=True
```

Skip wins over the expectation, and the run is successful.

## Measurement 2 — `@testing_steps` runs the body once per instant, and the skip is not per-instant today

`evidence/skip_xfail_project/test_sweeper.py` decorates methods
`@testing_steps(3)`. `solid test sweeper.py` (`out-cli-sweeper.txt`):

```
Running SweeperTest.test_skip_at_one_instant  [body ran, instant #1]
.  [body ran, instant #2]
.  [body ran, instant #3]
.FAIL!
...
unittest.case.SkipTest: nothing to compare at mid-sweep


Ran 4 tests in 0.06 seconds: 1 passed, 3 failed

[exit code 1]
```

- The body ran **three times**, one per declared instant, and printed a dot
  after each: the method is the unit of counting (`num_tests += 1` per method,
  `manager/test.py:319`) and the instant is the unit of execution
  (`manager/test.py:341-370`).
- The skip was declared at instant 2 of 3. Instant 3 still ran — a skip does
  not currently break the sweep — but the method as a whole was reported
  `FAIL!` and counted in `3 failed`. So today the summary counts a skipped
  instant as a failed **test**.
- The same run shows the decorator pair is harmless:
  `instants on test_expected_failure_over_a_sweep: [0.0, 0.5, 1];
  __unittest_expecting_failure__: True` — `unittest.expectedFailure` sets an
  attribute and returns the same function object (Python 3.12
  `unittest/case.py`), so `testing_instants` survives in either decorator
  order. `@unittest.skip` wraps with `functools.wraps`, and
  `out-runner-mechanism.txt` section H shows `testing_instants=[0.0, 0.5, 1]`
  surviving that too.

Section C of `out-runner-mechanism.txt`, a four-instant method whose only
exception is a skip at instant 1:

```
Running OnlyASkip.test_sweep....FAIL!
...
unittest.case.SkipTest: skipped at instant 1

Ran 1 tests in 0.00 seconds: 0 passed, 1 failed
num_tests=1 num_passed=0 num_failed=1
```

Four dots, then one failed test. Under the fix this method is a **pass with
one instant skipped**.

### A skip overwrites a real failure's traceback

Section A of `out-runner-mechanism.txt` — two failing instants in one method:

```
FIRST failure in output: False
LAST failure in output:  True
```

`error` is rebound on every raising instant (`manager/test.py:351-361`) and
only `error[2]` is printed (`:376`), so the LAST raise wins. Section F makes
that concrete with a real failure at instant 0 and a skip at instant 2:

```
Running FailThenSkip.test_sweep...FAIL!
...
unittest.case.SkipTest: skipped at instant 2

num_failed=1; REAL failure in output: False
```

The maker sees `FAIL!` over a `SkipTest` traceback and never sees the
`AssertionError` that is the actual regression. This is why the skip
requirement says a skip must not replace the report of a real failure.

### Failfast breaks the sweep on a skip

Section D of `out-runner-mechanism.txt`, the same four-instant skipping
method with `failfast=True`:

```
Running OnlyASkip.test_sweep..FAIL!
```

Two dots instead of four: the break at `manager/test.py:369` is driven by
`dot_color == 'red'`, which a `SkipTest` sets. `out-cli-failfast.txt` shows
the run-level half — `solid test --failfast sweeper.py` stops after the first
method and reports `Ran 1 tests ... 0 passed, 1 failed`, exit 1, where that
method is the one marked expected-to-fail.

## Measurement 3 — `--faceted` and `--exact` are one runner path

`solid test --faceted widget.py` (`out-cli-faceted.txt`), same fixture:

```
Comparing on the faceted kernel (volume epsilon 0 mm³): ...
Running WidgetTest.test_expected_failure_passes. passed
Running WidgetTest.test_expected_failure_raises.FAIL!
Running WidgetTest.test_plain_fail.FAIL!
Running WidgetTest.test_plain_pass. passed
Running WidgetTest.test_skipped.FAIL!

Ran 5 tests in 0.06 seconds: 2 passed, 3 failed (faceted kernel, volume
epsilon 0 mm³)

[exit code 1]
```

Identical verdicts, identical counts, identical exit code: the kernel
selection only sets a comparison policy (`manager/test.py:86-99`), and both
kernels go through the same `run_selection`/`run_class_tests`/`run_test`
(`:276-383`). **One fix, not two.**

## Measurement 4 — colour is not the carrier

`termcolor.colored` returns the text unchanged when
`_can_do_colour()` is false, which it is when stdout is not a tty, and when
`NO_COLOR` or `ANSI_COLORS_DISABLED` is set, or `TERM=dumb`
(termcolor's `termcolor.py`, read in the workspace venv). Verified by piping:

```
$ solid test widget.py 2>/dev/null | grep test_plain_pass | cat -v
Running WidgetTest.test_plain_pass. passed
```

No escape sequences. So every verdict the runner writes must be carried by a
WORD (` passed`, `FAIL!`), not a colour, and a new outcome needs a new word —
and, for the per-instant dot, a new character rather than a new dot colour.

## Measurement 5 — `unittest`'s skip decorations

Section G of `out-runner-mechanism.txt`:

```
@unittest.skip wraps the function: True, __unittest_skip__=True
calling it raises SkipTest(SkipTest('method-level @skip')) -- so a
method-level @skip reaches the runner as the same exception skipTest() raises

class carries __unittest_skip__=True
Running SkippedWholeCase.test_a    [body of test_a RAN]
. passed
Running SkippedWholeCase.test_b    [body of test_b RAN]
. passed

Ran 2 tests in 0.00 seconds: 2 passed, 0 failed
num_tests=2 num_passed=2 num_failed=0
```

- A method-level `@unittest.skip` / `@skipIf` needs no special handling: the
  wrapper raises `SkipTest`, which is the exception the skip rule already
  covers.
- A **class-level** `@unittest.skip` is ignored entirely: both bodies RAN and
  both were counted as PASSED. `run_class_tests` (`manager/test.py:311-323`)
  never looks at `__unittest_skip__`. That is a second silent wrong answer
  in the same family, and this change covers it.

## Measurement 6 — the mixin really does offer these

Section E of `out-runner-mechanism.txt`:

```
solid_node.test.TestCase mro includes unittest.TestCase: True
TestCaseMixin has skipTest: True
unittest.SkipTest is an Exception subclass: True
```

`solid_node/test.py:18` imports `unittest.TestCase as BaseTestCase` and
`:1836` derives the framework's `TestCase` from it, so `self.skipTest` is
offered to every companion case and, through `TestCaseMixin`
(`solid_node/test.py:2482`), to every node that mixes it in. The framework's
own pytest suite already relies on it working —
`tests/test_coarse_filesystem_freshness.py:249` calls
`self.skipTest('openscad is not installed')`, under pytest, where it is
honoured. Only `solid test` does not honour it.

## What is NOT measured here

- No measurement of a real project's run time; nothing in this change touches
  geometry or the comparison kernels.
- The originating project (`Internal-Cycloidal-Actuator`) is not in this
  worktree and was not run; the finding is quoted from `workflow/warts.md`.
