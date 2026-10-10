# ADR-118: An Unexpected Success Fails the Run

**Status:** Accepted
**Date:** 2026-09-15

**Related to:**
- [ADR-090: The Placement Quantum Is a Property of the Test Run](./ADR-090-the-placement-quantum-is-a-property-of-the-test-run.md)

## Context and Problem Statement

`solid test`'s runner had no concept of a skipped test and no concept of a
test that is expected to fail: every method ran under one bare `except
Exception`, so `unittest.SkipTest` counted as an ordinary failure and
`@unittest.expectedFailure` was an attribute nobody read
(`solid_node/manager/test.py`, before this change).
`projects/Actuators/Internal-Cycloidal-Actuator` paid for it
(`workflow/warts.md`, "Internal-Cycloidal-Actuator (2026-09-06, STEP import
cycles)", bullet (c)): it guarded an exact-only volume band with an early
`return` — indistinguishable from a test that ran and passed — and recorded
the kernel gap as a canary asserting the wrong value, green while the bug is
present and red the day it is fixed.

Honouring both concepts moves `solid test`'s exit-code contract in BOTH
directions:

- a run whose only unusual result is a skipped test now exits **0** where it
  exited **1** before;
- a run containing an unexpected success — a method marked
  `@unittest.expectedFailure` that did not raise — now exits **1** where it
  exited **0** before, in complete silence.

The second direction is the consequential one: it is the first time `solid
test` fails a run over something that did not raise. That is worth a
decision record on its own, distinct from the mechanism that reads the skip
and the marking (`openspec/changes/honour-skip-and-xfail/design.md`).

## Decision Drivers

- A skip must not be indistinguishable from a pass; the workaround it
  replaces already is (an early `return`), and that is the harm being fixed.
- A stale `@unittest.expectedFailure` marking is a false statement about the
  machine — the gap it named is gone, or was never verified — and nothing
  else in the framework catches that on its own.
- `unittest` has decided this exact question, the same way, since Python 3.4:
  `TestResult.wasSuccessful()` is `False` when `unexpectedSuccesses` is
  non-empty, even with zero `failures`
  (`openspec/changes/honour-skip-and-xfail/evidence.md`, measurement 1,
  `out-unittest-reference.txt`: `failures=1 ... unexpectedSuccesses=1
  wasSuccessful=False`, and a run with an unexpected success alone is
  `wasSuccessful=False` too). `solid test` follows the precedent every
  companion `TestCase` and every `pytest` run in this repository already
  reads the same decision by, rather than inventing a third answer for its
  own runner.
- ADR-090's discipline for this output: a run with none of the new outcomes
  must print exactly today's summary line, byte for byte.

## Considered Options

1. **Fail the run on an unexpected success, exit 0 on a skip alone**
   (chosen) — matches `unittest`.
2. Let an unexpected success be a warning with exit 0.
3. Always print `0 skipped, 0 expected failures, 0 unexpected successes` even
   when all three are zero.
4. Count a skip as a pass.

## Decision Outcome

Chosen: **an unexpected success fails the run; a skip, on its own, does
not.**

`solid_node/manager/test.py`'s exit rule (`handle`) becomes:

```python
if self.num_failed or self.num_unexpected_successes:
    sys.exit(1)
```

Each method's verdict follows its instants
(`design.md`, "The method's verdict follows its instants"): every instant
skipped is SKIPPED regardless of any `@unittest.expectedFailure` marking (a
skip wins over the expectation, matching `unittest`'s own precedence,
measured); any instant failed, on a marked method, is an EXPECTED FAILURE, no
traceback printed; no instant failed, on a marked method, with at least one
instant not skipped, is an UNEXPECTED SUCCESS. `--failfast` stops the run on
a FAILED or an UNEXPECTED SUCCESS, and never on a skip or an expected
failure — a method genuinely expected to fail, or genuinely inapplicable,
must not truncate a sweep the way an unmarked, unrelated bug does.

The summary line gains `, S skipped`, `, X expected failures` and
`, U unexpected successes`, each printed only when its count is non-zero, so
a run with none of them prints today's line unchanged.

### Why not option 2 — a warning, exit 0

The silence is the bug this change exists to fix. A warning a maker can
scroll past leaves the run green over a false statement about the machine,
which is exactly what an early-`return` guard or an inverted canary already
does today; nothing else in the framework would catch it.

### Why not option 3 — always print the three counts

Rejected by ADR-090's own discipline: the default run's summary line must
stay byte-for-byte what it is today, confirmed by the ratified "An exact run
reads as it always did" scenario. Printing `0 skipped, 0 expected failures,
0 unexpected successes` on every green run would break that.

### Why not option 4 — count a skip as a pass

A test that did not run must not read as a test that ran and proved
something — that conflation is the early-`return` workaround the
originating finding was filed about, reintroduced under a different name.

## Consequences

- Measured on this worktree (`openspec/changes/honour-skip-and-xfail/evidence.md`,
  "Measurement 1, after"): the same five-method fixture that reported `2
  passed, 3 failed`, exit 1, before this change, now reports `1 passed, 1
  failed, 1 skipped, 1 expected failure, 1 unexpected success`, exit 1 — the
  overall exit stays 1 because a genuine, unmarked regression
  (`test_plain_fail`) is in the same fixture, and `tests/test_manager_test.py`'s
  `UnusualResultExitCodeTest` isolates the two directions on their own: a run
  whose only unusual result is a skip exits 0, and a run whose only unusual
  result is an unexpected success exits 1.
- `Internal-Cycloidal-Actuator` may replace its early `return` guards with
  `skipTest` and its inverted canary with a marked expected failure. Nothing
  forces it to; nothing it does today breaks — it currently has no skip and
  no `expectedFailure` marking, so its own run's exit code is unaffected by
  this decision until it adopts either.
- Every CI job and every shop floor reading `solid test`'s exit code must be
  prepared for a previously-green run — one whose only unusual result is a
  stale `@unittest.expectedFailure` marking — to start failing. That is the
  intended effect: the marking is a statement about the machine, and this
  decision is what makes the statement checked.
- `shop-skills/solid-node-api/SKILL.md:1050` documents the summary line and
  the exit rule; it lives in another repository and needs the same
  correction as a follow-up, not part of this change
  (`design.md`, reviewer's note 5).

## References

- `solid_node/manager/test.py` — `run_test`, `run_class_tests`, `report`,
  `handle`'s exit
- `tests/test_manager_test.py` — `SkipAndExpectedFailureTest`,
  `ReportSummaryLineTest`, `UnusualResultExitCodeTest`
- `workflow/warts.md` — "Internal-Cycloidal-Actuator (2026-09-06, STEP import
  cycles)", bullet (c)
- OpenSpec change `honour-skip-and-xfail`, capability `test-framework`
