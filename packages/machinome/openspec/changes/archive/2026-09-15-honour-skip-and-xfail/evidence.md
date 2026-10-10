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
contract this change adopts (ADR-118).

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

## Red — tests/test_manager_test.py before implementation

Task 1.1/1.2: `SkipAndExpectedFailureTest`, `ReportSummaryLineTest` and
`UnusualResultExitCodeTest` added to `tests/test_manager_test.py`, run against
the UNCHANGED `solid_node/manager/test.py` (still `f409947`):

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_manager_test.py -q

```
.....FF.F.FFFFFFFFFF.F..................FF.............................. [ 90%]
........                                                                 [100%]
=================================== FAILURES ===================================
_ SkipAndExpectedFailureTest.test_a_class_level_skip_runs_no_body_and_no_setup _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_class_level_skip_runs_no_body_and_no_setup>

    def test_a_class_level_skip_runs_no_body_and_no_setup(self):
        node = SkippedWholeClassNode()
        runner = Runner()
        runner.test_case = None
    
        run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(node.calls, [])
E       AssertionError: Lists differ: ['a', 'b'] != []
E       
E       First list contains 2 additional elements.
E       First extra element 0:
E       'a'
E       
E       - ['a', 'b']
E       + []

tests/test_manager_test.py:472: AssertionError
__ SkipAndExpectedFailureTest.test_a_marked_methods_sweep_runs_every_instant ___

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_marked_methods_sweep_runs_every_instant>

    def test_a_marked_methods_sweep_runs_every_instant(self):
        node = ExpectedFailureSweepNode()
        runner = Runner()
        runner.test_case = None
    
        run_class_tests_capturing_output(runner, node, node)
    
        self.assertEqual(node.calls, [0, 1, 2])
>       self.assertEqual(getattr(runner, 'num_expected_failures', 0), 1)
E       AssertionError: 0 != 1

tests/test_manager_test.py:451: AssertionError
_ SkipAndExpectedFailureTest.test_a_skip_at_one_instant_does_not_fail_the_sweep _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_at_one_instant_does_not_fail_the_sweep>

    def test_a_skip_at_one_instant_does_not_fail_the_sweep(self):
        node = SkipMiddleInstantNode()
        runner = Runner()
        runner.test_case = None
    
        text = run_class_tests_capturing_output(runner, node, node)
    
        self.assertEqual(node.calls, [0, 1, 2])
>       self.assertEqual(runner.num_passed, 1)
E       AssertionError: 0 != 1

tests/test_manager_test.py:417: AssertionError
_ SkipAndExpectedFailureTest.test_a_skip_declared_in_setup_skips_the_method_and_continues _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_declared_in_setup_skips_the_method_and_continues>

    def test_a_skip_declared_in_setup_skips_the_method_and_continues(self):
        case = SetupSkipsCase()
        node = FakeNode()
        runner = Runner()
        runner.test_case = case
        runner.node = node
    
        try:
>           text = run_class_tests_capturing_output(runner, case, node)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

tests/test_manager_test.py:484: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
tests/test_manager_test.py:94: in run_class_tests_capturing_output
    runner.run_class_tests(klass, node)
solid_node/manager/test.py:320: in run_class_tests
    self.run_test(klass, method_name, method, node)
solid_node/manager/test.py:331: in run_test
    self.test_case.setUp()
tests/test_manager_test.py:193: in setUp
    self.skipTest('the exact kernel is not available here')
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = <tests.test_manager_test.SetupSkipsCase object at 0x7a2bcb65cbf0>
reason = 'the exact kernel is not available here'

    def skipTest(self, reason=None):
>       raise unittest.SkipTest(reason)
E       unittest.case.SkipTest: the exact kernel is not available here

tests/test_manager_test.py:106: SkipTest

During handling of the above exception, another exception occurred:

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_declared_in_setup_skips_the_method_and_continues>

    def test_a_skip_declared_in_setup_skips_the_method_and_continues(self):
        case = SetupSkipsCase()
        node = FakeNode()
        runner = Runner()
        runner.test_case = case
        runner.node = node
    
        try:
            text = run_class_tests_capturing_output(runner, case, node)
        except unittest.SkipTest:
>           self.fail(
                'a SkipTest raised from setUp escaped run_class_tests '
                "instead of being reported as a skipped test "
                "(reviewer's note 1)")
E           AssertionError: a SkipTest raised from setUp escaped run_class_tests instead of being reported as a skipped test (reviewer's note 1)

tests/test_manager_test.py:486: AssertionError
_ SkipAndExpectedFailureTest.test_a_skip_does_not_overwrite_a_real_failures_traceback _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_does_not_overwrite_a_real_failures_traceback>

    def test_a_skip_does_not_overwrite_a_real_failures_traceback(self):
        node = FailThenSkipNode()
        runner = Runner()
        runner.test_case = None
    
        text = run_class_tests_capturing_output(runner, node, node)
    
        self.assertEqual(runner.num_failed, 1)
>       self.assertIn('a real regression', text)
E       AssertionError: 'a real regression' not found in 'Running FailThenSkipNode.test_sweep...FAIL!\nTraceback (most recent call last):\n  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/solid_node/manager/test.py", line 345, in run_test\n    method()\n  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/tests/test_manager_test.py", line 148, in test_sweep\n    self.skipTest(\'skipped at instant 2\')\n  File "/home/asa/devel/libresolid-studio/solid-node/WTs/fix-warts/tests/test_manager_test.py", line 106, in skipTest\n    raise unittest.SkipTest(reason)\nunittest.case.SkipTest: skipped at instant 2\n\n'

tests/test_manager_test.py:440: AssertionError
____ SkipAndExpectedFailureTest.test_a_skip_is_reported_skipped_not_failed _____

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_is_reported_skipped_not_failed>

    def test_a_skip_is_reported_skipped_not_failed(self):
        node = SkipsOnlyInstantNode()
        runner = Runner()
        runner.test_case = None
    
        text = run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(runner.num_failed, 0)
E       AssertionError: 1 != 0

tests/test_manager_test.py:381: AssertionError
_______ SkipAndExpectedFailureTest.test_a_skip_wins_over_the_expectation _______

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_skip_wins_over_the_expectation>

    def test_a_skip_wins_over_the_expectation(self):
        node = ExpectedFailureAllSkipNode()
        runner = Runner()
        runner.test_case = None
    
        run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(getattr(runner, 'num_skipped', 0), 1)
E       AssertionError: 0 != 1

tests/test_manager_test.py:461: AssertionError
_ SkipAndExpectedFailureTest.test_a_sweep_that_skips_at_every_instant_is_one_skipped_test _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_a_sweep_that_skips_at_every_instant_is_one_skipped_test>

    def test_a_sweep_that_skips_at_every_instant_is_one_skipped_test(self):
        node = SkipEveryInstantNode()
        runner = Runner()
        runner.test_case = None
    
        run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(getattr(runner, 'num_skipped', 0), 1)
E       AssertionError: 0 != 1

tests/test_manager_test.py:428: AssertionError
_ SkipAndExpectedFailureTest.test_an_expected_failure_that_passes_is_an_unexpected_success _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_an_expected_failure_that_passes_is_an_unexpected_success>

    def test_an_expected_failure_that_passes_is_an_unexpected_success(self):
        node = ExpectedFailurePassesNode()
        runner = Runner()
        runner.test_case = None
    
        text = run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(runner.num_passed, 0)
E       AssertionError: 1 != 0

tests/test_manager_test.py:405: AssertionError
_ SkipAndExpectedFailureTest.test_an_expected_failure_that_raises_is_not_a_failure _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_an_expected_failure_that_raises_is_not_a_failure>

    def test_an_expected_failure_that_raises_is_not_a_failure(self):
        node = ExpectedFailureRaisesNode()
        runner = Runner()
        runner.test_case = None
    
        text = run_class_tests_capturing_output(runner, node, node)
    
>       self.assertEqual(runner.num_failed, 0)
E       AssertionError: 1 != 0

tests/test_manager_test.py:393: AssertionError
_ SkipAndExpectedFailureTest.test_failfast_does_not_break_on_a_marked_methods_raise _

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_failfast_does_not_break_on_a_marked_methods_raise>

    def test_failfast_does_not_break_on_a_marked_methods_raise(self):
        node = FailfastExpectedFailureSweepThenPassNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True
    
        with redirect_stdout(io.StringIO()):
            runner.run_tests()
    
>       self.assertEqual(
            node.calls, [('a', 0), ('a', 1), ('a', 2), 'b'])
E       AssertionError: Lists differ: [('a', 0), ('a', 1)] != [('a', 0), ('a', 1), ('a', 2), 'b']
E       
E       Second list contains 2 additional elements.
E       First extra element 2:
E       ('a', 2)
E       
E       - [('a', 0), ('a', 1)]
E       + [('a', 0), ('a', 1), ('a', 2), 'b']

tests/test_manager_test.py:543: AssertionError
_ SkipAndExpectedFailureTest.test_failfast_does_not_break_the_sweep_on_a_skip __

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_failfast_does_not_break_the_sweep_on_a_skip>

    def test_failfast_does_not_break_the_sweep_on_a_skip(self):
        node = FailfastSkipSweepNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True
    
        with redirect_stdout(io.StringIO()):
            runner.run_tests()
    
>       self.assertEqual(node.calls, [0, 1, 2])
E       AssertionError: Lists differ: [0, 1] != [0, 1, 2]
E       
E       Second list contains 1 additional elements.
E       First extra element 2:
E       2
E       
E       - [0, 1]
E       + [0, 1, 2]
E       ?      +++

tests/test_manager_test.py:529: AssertionError
___ SkipAndExpectedFailureTest.test_failfast_stops_on_an_unexpected_success ____

self = <tests.test_manager_test.SkipAndExpectedFailureTest testMethod=test_failfast_stops_on_an_unexpected_success>

    def test_failfast_stops_on_an_unexpected_success(self):
        node = FailfastUnexpectedSuccessNode()
        runner = Runner()
        runner.test_case = None
        runner.node = node
        runner.failfast = True
    
        with redirect_stdout(io.StringIO()):
            runner.run_tests()
    
>       self.assertEqual(node.calls, ['a'])
E       AssertionError: Lists differ: ['a', 'b'] != ['a']
E       
E       First list contains 1 additional elements.
E       First extra element 1:
E       'b'
E       
E       - ['a', 'b']
E       + ['a']

tests/test_manager_test.py:558: AssertionError
_ ReportSummaryLineTest.test_nonzero_counts_are_appended_before_the_kernel_note _

self = <tests.test_manager_test.ReportSummaryLineTest testMethod=test_nonzero_counts_are_appended_before_the_kernel_note>

    def test_nonzero_counts_are_appended_before_the_kernel_note(self):
        runner = Runner()
        runner.num_tests = 8
        runner.num_passed = 4
        runner.num_failed = 0
        runner.num_skipped = 1
        runner.num_expected_failures = 2
        runner.num_unexpected_successes = 1
        runner.policy = framework.ComparisonPolicy('faceted', 0.0)
    
        out = io.StringIO()
        with redirect_stdout(out):
            runner.report(1.0)
    
>       self.assertIn(
            'Ran 8 tests in 1.00 seconds: 4 passed, 0 failed, '
            '1 skipped, 2 expected failures, 1 unexpected success '
            '(faceted kernel, volume epsilon 0 mm³)',
            out.getvalue())
E       AssertionError: 'Ran 8 tests in 1.00 seconds: 4 passed, 0 failed, 1 skipped, 2 expected failures, 1 unexpected success (faceted kernel, volume epsilon 0 mm³)' not found in '\nRan 8 tests in 1.00 seconds: 4 passed, 0 failed (faceted kernel, volume epsilon 0 mm³)\n'

tests/test_manager_test.py:596: AssertionError
__ UnusualResultExitCodeTest.test_a_run_with_an_unexpected_success_exits_one ___

self = <tests.test_manager_test.UnusualResultExitCodeTest testMethod=test_a_run_with_an_unexpected_success_exits_one>

    def test_a_run_with_an_unexpected_success_exits_one(self):
        node_path = self.write('boat/gadget.py', UNEXPECTED_SUCCESS_SOURCE)
        self.write('boat/test_gadget.py', UNEXPECTED_SUCCESS_TEST_SOURCE)
    
        code, stdout, stderr = self.run_solid_test(node_path)
    
>       self.assertEqual(code, 1, stderr)
E       AssertionError: 0 != 1 :

tests/test_manager_test.py:1115: AssertionError
----------------------------- Captured stderr call -----------------------------
Geometries in cache: 1
Geometry cache size in bytes: 728
CGAL Polyhedrons in cache: 0
CGAL cache size in bytes: 0
Total rendering time: 0:00:00.000
   Top level object is a 3D object:
   Facets:          6
_______ UnusualResultExitCodeTest.test_a_run_with_only_a_skip_exits_zero _______

self = <tests.test_manager_test.UnusualResultExitCodeTest testMethod=test_a_run_with_only_a_skip_exits_zero>

    def test_a_run_with_only_a_skip_exits_zero(self):
        node_path = self.write('boat/widget.py', SKIP_ONLY_SOURCE)
        self.write('boat/test_widget.py', SKIP_ONLY_TEST_SOURCE)
    
        code, stdout, stderr = self.run_solid_test(node_path)
    
>       self.assertEqual(code, 0, stderr)
E       AssertionError: 1 != 0 :

tests/test_manager_test.py:1106: AssertionError
----------------------------- Captured stderr call -----------------------------
Geometries in cache: 1
Geometry cache size in bytes: 728
CGAL Polyhedrons in cache: 0
CGAL cache size in bytes: 0
Total rendering time: 0:00:00.000
   Top level object is a 3D object:
   Facets:          6
=========================== short test summary info ============================
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_class_level_skip_runs_no_body_and_no_setup
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_marked_methods_sweep_runs_every_instant
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_skip_at_one_instant_does_not_fail_the_sweep
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_skip_declared_in_setup_skips_the_method_and_continues
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_skip_does_not_overwrite_a_real_failures_traceback
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_skip_is_reported_skipped_not_failed
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_skip_wins_over_the_expectation
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_a_sweep_that_skips_at_every_instant_is_one_skipped_test
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_an_expected_failure_that_passes_is_an_unexpected_success
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_an_expected_failure_that_raises_is_not_a_failure
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_failfast_does_not_break_on_a_marked_methods_raise
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_failfast_does_not_break_the_sweep_on_a_skip
FAILED tests/test_manager_test.py::SkipAndExpectedFailureTest::test_failfast_stops_on_an_unexpected_success
FAILED tests/test_manager_test.py::ReportSummaryLineTest::test_nonzero_counts_are_appended_before_the_kernel_note
FAILED tests/test_manager_test.py::UnusualResultExitCodeTest::test_a_run_with_an_unexpected_success_exits_one
FAILED tests/test_manager_test.py::UnusualResultExitCodeTest::test_a_run_with_only_a_skip_exits_zero
16 failed, 64 passed in 2.20s
```

All 16 new-test failures are for the reason `tasks.md` 1.1/1.2 records: the
bare `except Exception` counts a skip as a failure (`num_failed == 1` instead
of `0`), the `expectedFailure` attribute is read nowhere (a raising marked
method is `num_failed == 1`; a passing one is `num_passed == 1`), a
class-level `@unittest.skip` runs both bodies, a `setUp` skip escapes
`run_class_tests` uncaught rather than being reported, a later skip
overwrites a real failure's traceback, `--failfast` breaks the sweep/run on a
skip or a marked raise and does NOT break it on an unexpected success, and
`report()`/the exit code know nothing of the three new counts. The two guards
in the same class (`test_a_skip_between_instants_still_restores_the_children`,
`test_a_non_skip_setup_error_still_propagates`) and
`ReportSummaryLineTest.test_default_run_reports_todays_line_unchanged` are
GREEN already, as intended — they assert what today's code already does
correctly and must keep doing.

16 failed, 64 passed in 2.20s.

## The whole suite once, before the implementation commit (task 3.2)

    PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest -q

Baseline (before this change's tests were added, i.e. the planning commit
`6fb52ab`): `2707 passed, 4 skipped`.

After this change's tests and implementation:

```
2726 passed, 4 skipped, 53 warnings, 1501 subtests passed in 330.45s (0:05:30)
```

Exit code 0 (pytest reports no failures or errors; the run ended in the
summary line above with no `FAILURES`/`ERRORS` section, which is pytest's own
exit-0 shape). `2726 - 2707 = 19`, exactly the number of test methods this
change adds (`SkipAndExpectedFailureTest` 15, `ReportSummaryLineTest` 2,
`UnusualResultExitCodeTest` 2) -- nothing else in the suite moved.

## After (task 3.3) — the same probes, re-run against the implementation

`sh openspec/changes/honour-skip-and-xfail/evidence/run-probes.sh`, re-run
after task 2, rewrote every `out-*.txt` transcript quoted above. The
unittest-reference transcript is byte-for-byte unchanged (that probe drives
`unittest` itself, never this runner). The other four follow.

### Measurement 1, after — the same five methods through the CLI

`solid test widget.py` (`out-cli-widget.txt`):

```
Running WidgetTest.test_expected_failure_passes.UNEXPECTED SUCCESS!
Running WidgetTest.test_expected_failure_raises. expected failure
Running WidgetTest.test_plain_fail.FAIL!
Traceback (most recent call last):
  File ".../solid_node/manager/test.py", line 401, in run_test
    method()
  File ".../test_widget.py", line 23, in test_plain_fail
    raise AssertionError('a real regression')
AssertionError: a real regression

Running WidgetTest.test_plain_pass. passed
Running WidgetTest.test_skippeds skipped: the exact kernel is not available here

Ran 5 tests in 0.13 seconds: 1 passed, 1 failed, 1 skipped, 1 expected failure, 1 unexpected success

[exit code 1]
```

Read off that one run:

1. **`self.skipTest(...)`** → no longer `FAIL!`: ` skipped: the exact kernel
   is not available here`, counted in `1 skipped`, not in `1 failed`. (The
   `s` glued to `test_skippeds` is the new per-instant mark character for
   this one-instant method, printed exactly where the old `.` was — the same
   place `test_plain_pass` and `test_plain_fail` still print theirs; no
   space was ever there.)
2. **`@unittest.expectedFailure` that raises** → ` expected failure`, no
   traceback, counted in `1 expected failure`, not in `1 failed`.
3. **`@unittest.expectedFailure` that passes** → `UNEXPECTED SUCCESS!`,
   counted in `1 unexpected success`, no longer silent.

The overall run still exits **1** because `test_plain_fail` — a genuine,
unmarked regression — is in the same fixture; that is correct and unchanged
(`Requirement: Failing contract fails the run`). Whether each of the three
outcomes above would exit 0 or 1 **on its own** is what
`tests/test_manager_test.py`'s `UnusualResultExitCodeTest` isolates directly,
one outcome per run, free of the other four methods sharing this fixture:
`test_a_run_with_only_a_skip_exits_zero` (exit 0) and
`test_a_run_with_an_unexpected_success_exits_one` (exit 1) — both GREEN
against the implementation (task 3.1). The expected-failure-alone case is the
same `UnusualResultExitCodeTest` shape as the skip case (neither pass nor
fail, no unexpected success), covered unit-level by
`SkipAndExpectedFailureTest.test_an_expected_failure_that_raises_is_not_a_failure`.

### Measurement 2, after — the sweep, the skip is per-instant, failfast does not break on it

`solid test sweeper.py` (`out-cli-sweeper.txt`):

```
Running SweeperTest.test_expected_failure_over_a_sweep... expected failure
Running SweeperTest.test_fail_at_one_instant...FAIL!
...
AssertionError: mid-sweep regression

Running SweeperTest.test_instants_attribute_survives_the_decorator_pair  instants on test_expected_failure_over_a_sweep: [0.0, 0.5, 1]; __unittest_expecting_failure__: True
. passed
Running SweeperTest.test_skip_at_one_instant  [body ran, instant #1]
.  [body ran, instant #2]
s  [body ran, instant #3]
. passed (1 of 3 instants skipped)

Ran 4 tests in 0.12 seconds: 2 passed, 1 failed, 1 expected failure

[exit code 1]
```

The body still runs three times (three marks after
`test_skip_at_one_instant`), but the method is now `passed (1 of 3 instants
skipped)` and counted in `2 passed`, not in `3 failed` — measurement 2's
original finding is gone. `test_expected_failure_over_a_sweep` runs every
instant and is one `expected failure`, matching the design's "the run over
the remaining instants is not abandoned by the first raise".

`probe_runner_mechanism.py`'s sections, re-run (`out-runner-mechanism.txt`):

- **Section A** (two failing instants) is unchanged: the LAST failure's
  traceback still survives (`error` is only ever set by the `except
  Exception` arm — the out-of-scope choice this change deliberately leaves
  alone).
- **Section F** (a real failure at instant 0, a skip at instant 2) now reads
  `real failure reported: True` — the skip no longer overwrites the real
  failure's traceback, which was the finding's sharpest complaint:

  ```
  Running FailThenSkip.test_sweep..sFAIL!
  Traceback (most recent call last):
  ...
  AssertionError: REAL failure, at instant 0

  Ran 1 tests in 0.00 seconds: 0 passed, 1 failed

  num_failed=1; REAL failure in output: True
  ```

- **Section C** (a method whose only exception is a skip, over four
  instants) is now `passed (1 of 4 instants skipped)`, `num_passed=1
  num_failed=0` — previously `FAIL!`, `num_failed=1`.
- **Section D** (the same, `--failfast`) now prints all four marks
  (`.s..`) and reports the same `passed (1 of 4 instants skipped)` —
  previously failfast broke the sweep after two dots (measurement 2, section
  D, before). A skip no longer stops a failfast sweep.
- **Section G** (`unittest.skip` forms) now shows the CLASS-level case fixed
  too:

  ```
  Running SkippedWholeCase.test_a skipped: class-level @skip
  Running SkippedWholeCase.test_b skipped: class-level @skip

  Ran 2 tests in 0.00 seconds: 0 passed, 0 failed, 2 skipped

  num_tests=2 num_passed=0 num_failed=0
  ```

  Previously both bodies ran and both were counted passed; now neither body
  runs (`setUpClass` does not run either) and each is counted once as
  skipped.
- **Section H** is unchanged (`testing_instants` still survives
  `@unittest.skip` wrapping `@testing_steps`, as it did before this change
  touched anything).

### Measurement 3, after — `--faceted` and `--exact` remain one path

`solid test --faceted widget.py` (`out-cli-faceted.txt`) reproduces
Measurement 1's after-transcript exactly, with the kernel line and the
`(faceted kernel, volume epsilon 0 mm³)` suffix added — identical verdicts,
identical counts, identical exit code to the exact run. Still one fix, not
two.

### `--failfast` at the run level (`out-cli-failfast.txt`)

`solid test --failfast sweeper.py`:

```
Running SweeperTest.test_expected_failure_over_a_sweep... expected failure
Running SweeperTest.test_fail_at_one_instant..FAIL!
...
AssertionError: mid-sweep regression

Ran 2 tests in 0.07 seconds: 0 passed, 1 failed, 1 expected failure

[exit code 1]
```

The expected-failure method runs to completion and does not stop the run
(matching "Failfast and an unexpected success" being the ONLY thing that
should stop it); `test_fail_at_one_instant`'s real failure still stops the
run at the next test, as before.

## Reviewer's independent full run (ratification of the implementation, 2026-09-15)

    PYTHONPATH="$PWD" timeout 590 .venv/bin/python -m pytest tests -q -p no:cacheprovider

    2726 passed, 4 skipped, 53 warnings, 1501 subtests passed in 349.79s (0:05:49)
    exit 0

Reviewer's note: a method whose `testing_instants` list is EMPTY would now
read as skipped (`step_skip == n` with both zero) where it read as passed
before; unreachable through the public decorators (`testing_steps` refuses
fewer than two steps, `testing_instant` sets exactly one), so accepted as
is and recorded here.
