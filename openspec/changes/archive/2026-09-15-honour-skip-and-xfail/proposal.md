## Why

`solid test` has no concept of a skipped test and no concept of a test that is
expected to fail. Its runner calls every method inside one bare
`except Exception` (`solid_node/manager/test.py:342-370`), so
`unittest.SkipTest` — the exception `self.skipTest(reason)` raises — arrives
as an ordinary failure, and `@unittest.expectedFailure` is an attribute nobody
reads.

`projects/Actuators/Internal-Cycloidal-Actuator` paid for it
(`workflow/warts.md`, "# Internal-Cycloidal-Actuator (2026-09-06, STEP import
cycles)", bullet (c)):

> `solid test`'s runner has no skip and no expected-failure concept: it calls
> each method in a loop under a bare `except Exception`, so `self.skipTest()`
> and `@unittest.expectedFailure` both count as plain failures. The actuator
> guards exact-only volume bands with an early `return` and records the kernel
> gap as a canary asserting the wrong value, which is the honest equivalent it
> has …

The two workarounds that project was forced into are exactly the two costs.
An early `return` makes a test that did not run indistinguishable from a test
that passed — the run stays green over a contract nobody checked. And a canary
asserting the value the kernel *wrongly* produces goes green while the bug is
there and RED when the kernel is fixed, which is the wrong way round and burns
a debugging session the day the fix lands.

Reproduced on this worktree — `evidence.md`, every line from a probe actually
run, on a two-node fixture under `evidence/skip_xfail_project/`:

- **`self.skipTest('the exact kernel is not available here')`** → the runner
  prints `FAIL!` with the `SkipTest` traceback, counts it in `3 failed`, and
  the process exits **1**. A project cannot say "not applicable here" at all.
- **`@unittest.expectedFailure` that raises** → `FAIL!` with the assertion's
  traceback, counted in `3 failed`, exit **1**. A known, recorded, accepted
  gap cannot be expressed; the suite is permanently red or the test is deleted.
- **`@unittest.expectedFailure` that passes** → ` passed`, counted in
  `2 passed`, exit **0**, in complete silence. The marking is now wrong — the
  bug it names is fixed, or the test no longer exercises it — and nothing says
  so.
- Under `@testing_steps(3)` the body runs once per instant (measured: three
  bodies, three dots) but a skip at ONE instant fails the whole method:
  `Ran 4 tests … 1 passed, 3 failed`.
- Worse, a skip **overwrites the traceback of a real failure** in the same
  method: `error` is rebound on each raising instant (`:351-361`) and only the
  last one is printed (`:376`), so a method that genuinely failed at instant 0
  and skipped at instant 2 prints `FAIL!` over the `SkipTest` traceback
  (`evidence.md`, measurement 2, section F).
- A **class-level** `@unittest.skip` is ignored outright: both test bodies ran
  and both were counted as passed (`evidence.md`, measurement 5).
- `--faceted` and `--exact` produce identical verdicts, counts and exit code:
  the kernel is a comparison policy (`:86-99`) and both go through the one
  `run_test` (`:325-383`). **One fix, not two.**

The framework's own pytest suite already depends on these semantics —
`tests/test_coarse_filesystem_freshness.py:249` skips itself when OpenSCAD is
absent. `solid test` is the only runner in the framework that does not honour
them.

## What Changes

- A test that declares itself inapplicable — `skipTest(reason)`, any raise of
  the skip exception, or `unittest`'s skip decoration on the method or on the
  whole class — SHALL be reported as **skipped**: named with its reason,
  counted as neither passed nor failed, and unable on its own to make the run
  exit 1.
- A skip's unit is the **instant**. Under `@testing_instant`/`@testing_steps`
  an instant that skips is skipped alone; the remaining instants still run and
  decide the method's verdict. A method all of whose instants skipped is one
  skipped test; a method some of whose instants skipped and whose rest passed
  is a pass that says how many instants it skipped.
- A skip SHALL NOT replace the report of a real failure in the same method.
- `@unittest.expectedFailure` SHALL be honoured: a marked method that raises
  at any instant is an **expected failure** (neither passed nor failed, no
  traceback printed); a marked method that raises at no instant is an
  **unexpected success**, which **fails the run**. Expectation is a property
  of the method, not of an instant. A skip takes precedence over the
  expectation, as it does in `unittest` (measured).
- The summary line gains `, S skipped`, `, X expected failures` and
  `, U unexpected successes`, each printed only when non-zero, so a run with
  none of them prints today's line unchanged (the ADR-090 discipline for this
  output). The exit code becomes: 1 when any test failed **or** any test
  succeeded unexpectedly, 0 otherwise.
- Every verdict is carried by a WORD, not by a colour: `termcolor` already
  strips escapes when stdout is not a tty, or under `NO_COLOR` (measured), so
  a log says ` skipped`, ` expected failure`, `UNEXPECTED SUCCESS!` in text.
  The per-instant dot gains a new CHARACTER for a skipped instant rather than
  a new colour for the existing one, so no byte of today's output changes.
- `--failfast` stays coherent: a skip and an expected failure never stop a
  sweep or a run; an unexpected success does, because it fails the run.
- **Out of scope**, recorded so it is not read into this change:
  - The runner keeps the LAST failing instant's traceback rather than the
    first (`:351-361`, measured). This change only stops a skip from becoming
    that traceback; which real failure is reported when several instants fail
    is left exactly as it is.
  - No per-instant location is added to a failure report ("failed at instant
    0.5"), useful as it would be.
  - `unittest`'s `subTest`, `skipUnless` on a class hierarchy, and
    `setUpClass`-raised skips beyond the `__unittest_skip__` flag.
  - The shop's `shop-skills/solid-node-api/SKILL.md:1050` documents the
    summary line and the exit rule; it is in another repository and is a
    follow-up for the reviewer, not part of this change.

## Impact

- Affected specs: `test-framework` — MODIFIED "Test runner lifecycle"
  (summary line and exit code); ADDED "A skipped test is not a failure";
  ADDED "An expected failure is honoured and an unexpected success fails the
  run".
- Affected code: `solid_node/manager/test.py` only (`run_class_tests`,
  `run_test`, `report`, `handle`'s exit, the counters in `__init__`).
  `tests/test_manager_test.py` grows a new test class; no fixture project is
  added to `tests/`.
- Affected docs: `docs/cli.rst` (`solid test` — the summary line, the exit
  rule, `--failfast`), `docs/testing.rst` (how to skip and how to mark a known
  gap), `docs/changelog.rst`.
- Affected projects: `Internal-Cycloidal-Actuator` may replace its early
  `return` guards with `skipTest` and its inverted canary with a marked
  expected failure. Nothing forces it to; nothing it does today breaks.
- ADR-118 is proposed: the exit-code contract changes in both directions — a
  run whose only unusual result is a skip exits 0 where it exits 1 today, and
  a run containing an unexpected success exits 1 where it exits 0 today.
