## Why

`machinome test` loses information exactly when a maker needs it: when a
sweep fails, and when a test case cannot even be set up. Three entries of
`workflow/warts.md`, section "honour-skip-and-xfail (2026-09-15, found
while fixing)", all on the runner `machinome/manager/test.py`:

> **The runner keeps the LAST failing instant's traceback, not the
> first.** `run_test`'s `error` is rebound on every raising instant
> (`manager/test.py`) and only the last is printed, so a method that
> fails at instant 0 and again, differently, at instant 2 reports
> instant 2's traceback.

> **No failure report names the instant it happened at.** `FAIL!`'s
> traceback shows where in the method's own source the assertion raised,
> never which declared instant (`0`, `0.5`, `1`, ...) it raised at under
> `@testing_steps`/`@testing_instant`. A maker reproducing a sweep
> failure has to re-run the method by hand to find the instant.

> **A non-skip exception from `setUp`, or any exception from
> `setUpClass`, aborts the run without a verdict.** [...] any OTHER
> exception `setUp` raises still escapes `run_test` uncaught, as does
> anything `setUpClass` raises, and `handle` catches only `StopTestRun` —
> so the run stops with a bare traceback, no summary line, and no verdict
> for the tests that would have followed.

Reproduced on the bench `fix-warts-3` at `f8d19a1` (design.md, Context):

- A scratch project whose `@testing_steps(3)` method raises an
  `AssertionError` at its first instant and a `ValueError` at its last
  prints `Running SweepTest.test_fails_at_two_instants_differently...FAIL!`
  followed by the `ValueError`'s traceback alone. Nothing printed says
  which instant failed, how many did, or that the first one failed at all.
- The same project's `setUp` raising `RuntimeError` ends the run with a
  bare traceback through `handle` and `run_selection`, no `Running` line
  for the method, no summary line, and the following test case never
  runs; `setUpClass` raising does the same.
- 3DPrintedClocks' mantel clock 34 (project at `ec2a05d`), its documented
  run `machinome test mantel_clock_34_steampunk --mesh --volume-epsilon
  0.001`: 20 tests, 15 passed, 5 failed, three of the failures sweeps of 8,
  48 and 32 instants. In the captured log the instants' marks are all `.`
  (the colour that separates a red dot from a green one is dropped when
  the output is not a terminal), so the log does not say at which instant,
  or at how many, any sweep failed. A scratch case swept over four
  instants of the minute hand's travel, with an impossible assertion whose
  message carries the hand's centroid, prints the centroid read at the
  LAST instant, `(47.837, -83.031, 45.609)`, while the first instant read
  `(65.434, -65.434, 70.495)`.

## What Changes

- **A failing method reports its first failing instant.** The traceback
  printed under `FAIL!` is the one the first failing instant raised; the
  later ones are counted, not printed.
- **The failure line names the instant.** For a method that declares its
  instants (`@testing_instant`, `@testing_steps`), the line reads
  `FAIL! at instant 0.25`, and for a sweep it adds how many of its
  instants failed, `FAIL! at instant 0.25 (3 of 48 instants failed)`, or,
  when `--failfast` cut the sweep short, where it stopped,
  `FAIL! at instant 0.25 (--failfast stopped the sweep at instant 13 of
  48)`. The instant is printed as the value the runner handed to
  `set_keyframe`, exactly enough to be written back into
  `@testing_instant(...)`. A method declaring no instant prints `FAIL!`
  exactly as today.
- **An exception in set-up is an ERROR, and the run goes on.** An
  exception other than a skip raised by a test case's `setUp` reports that
  method `ERROR! (setUp raised)` with the traceback; raised by its
  `setUpClass`, it reports each of the class's test methods `ERROR!
  (setUpClass raised)`, the traceback printed once, and none of them runs.
  Either way the run continues with the next test, the summary line gains
  `, E errors` (`1 error`) after `F failed` when there are any, and the run
  exits 1. `--failfast` stops on an error, as on a failure. A run with no
  error prints today's summary line byte for byte.
- **A skip raised by `setUpClass` skips the class.** `unittest.SkipTest`
  from `setUpClass` reports each of the class's methods skipped with the
  reason, exactly as `unittest`'s skip decoration on the class does; the
  error arm above must not turn a declared skip into an error, and today
  the skip aborts the run.
- After `setUp` raised, the case's `tearDown` is not called (it is what
  `unittest` does: the set-up it would undo did not complete); after
  `setUpClass` raised, `tearDownClass` is not called.

**Deliberately out**, with the reason:

- an exception raised by the test METHOD that is not an `AssertionError`.
  It stays a failure, as today. `unittest` calls it an error, but the
  framework's own assertions raise `ValueError` and engine exceptions on
  some paths (`assertJoined`'s "Not all meshes are volumes!"), so
  reclassifying would move verdicts in every project's log and in the
  meta goldens; no finding asks for it.
- an exception raised by `tearDown` or `tearDownClass`. It still escapes
  and stops the run. No project has hit it; it is filed as a new entry in
  `workflow/warts.md` by this change (design.md, Open Questions, 2).
- a declared model under `--all` that cannot reach its tests. It is
  counted as a failure today, by a separate requirement; it stays so.
- the expected-failure, unexpected-success and skip lines, which name no
  instant and print no traceback; they are unchanged.
- the studio's API skill (`machinome-studio/shop-skills/machinome-api/SKILL.md`,
  "It prints `Ran N tests in X seconds: P passed, F failed`, exits 1 on any
  failure"), another repository; recorded for the campaign's
  outside-the-framework cycle, not edited here.
- the projects. 3DPrintedClocks is read and run, never edited.
- `pytest`'s view of any test. This is `machinome test`'s own runner.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `test-framework`:
  - ADDED "A failing method reports its first failing instant, by name".
  - ADDED "An exception in set-up is an error, and the run goes on".
  - MODIFIED "Test runner lifecycle": the summary line's `, E errors`
    continuation, the exit status on an error, and `--failfast` on an
    error; its fourteen scenarios carried, "A B-rep run reads as it always
    did" naming errors among the outcomes whose absence keeps the line
    exact, and one scenario added.
  - MODIFIED "A skipped test is not a failure": a skip raised by a test
    case's class set-up is honoured as the class-level decoration is; its
    seven scenarios carried and one added.

## Impact

- Code: `machinome/manager/test.py` only — `Test.__init__` (an error
  count), `run_class_tests` (the class set-up guarded), `run_test` (the
  first failing instant kept, the instant named, the set-up guarded),
  `report` (the error count) and `handle`'s exit rule; two small private
  helpers (design.md, Decision 6).
- Tests: `tests/test_manager_test.py` — unit tests on its `FakeNode`
  fixtures, end-to-end tests through `Runner().handle` on scratch projects
  (its `MultiTestCaseFixture`), and the one existing test that pins the
  abort, `test_a_non_skip_setup_error_still_propagates`, which inverts.
- Manual: `docs/reference/cli.rst` ("machinome test": the summary line,
  the exit status, `--failfast`, the failure and error lines),
  `docs/reference/assertions.rst` ("Instants"); `docs/architecture.md`'s
  test-framework paragraph; `docs/project/changelog.rst`, one bullet under
  `Unreleased`.
- Records: the three `workflow/warts.md` entries move to
  `workflow/archive/fix-warts-3-2026-10-06/resolved.md`; one new entry for
  tear-down exceptions.
- Consumers: no documented consumer parses the lines that change
  (design.md, Context, "Who reads the runner's output"); the exit status
  of a run whose set-up raised is 1 before and after.
- No ADR (design.md, Decision 8).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 13, `report-the-instant`, validated in
3DPrintedClocks.
