# Design — honour skip and expected failure

Every mechanism claim below cites `file:line` in this worktree at `f409947`;
every behavioural claim it rests on is a probe in `evidence.md`.

## The mechanism as it stands

### One loop, one `except`, three counters

`solid_node/manager/test.py` is the whole runner.

| piece | lines | what it does |
| --- | --- | --- |
| `__init__` | `:48-52` | `num_tests`, `num_passed`, `num_failed`, `failfast` |
| `handle` | `:85-180` | resolves the comparison policy, builds each selection, runs, reports, exits |
| the exit | `:179-180` | `if self.num_failed: sys.exit(1)` |
| `report` | `:285-300` | the summary line and its kernel/quantum notes |
| `run_selection` | `:275-283` | the node's own methods, then each companion case |
| `run_class_tests` | `:311-323` | `setUpClass`, every `test_`-prefixed attribute, `tearDownClass` |
| `run_test` | `:325-383` | `setUp`, the instants loop, the verdict, `tearDown` |

`run_class_tests` counts one test per METHOD (`:319`, `self.num_tests += 1`)
and `run_test` executes the method once per INSTANT (`:341-342`,
`instants = getattr(method, 'testing_instants', [0])`). The instants come from
`@testing_instant` (`solid_node/test.py:2491-2505`) and `@testing_steps`
(`solid_node/test.py:2507-2531`), which set `testing_instants` and return the
same function object.

Inside the loop the only classification is pass/raise:

```
:343      try:
:344          node.set_keyframe(instant)
:345          method()
:346          step_pass += 1
:347          dot_color = 'green'
:348      except bdb.BdbQuit:
...
:351      except Exception as e:
:352-361      error = (exc_type, exc_value, formatted traceback)
:362          step_fail += 1
:363          dot_color = 'red'
```

and at the end of the method:

```
:371      if not step_fail:
:372-373      " passed" (green), num_passed += 1
:374      else:
:375-377      "FAIL!" (red), print(error[2]), num_failed += 1
:378-379      if self.failfast: raise StopTestRun()
```

Three consequences, each measured in `evidence.md`:

1. `unittest.SkipTest` is an `Exception` (measurement 6), so `:351` catches it
   and `:362` counts it as a failing instant. A skipped test is a failed test.
2. `__unittest_expecting_failure__` — the only thing
   `unittest.expectedFailure` does (Python 3.12: it sets that attribute and
   returns the same function) — is read nowhere in the framework
   (`grep` finds it in no `solid_node/` file). A marked method that raises is
   a failure; a marked method that passes is a pass.
3. `error` is REBOUND on every raising instant (`:353`) and only the last one
   is printed (`:376`), so a later skip replaces the traceback of an earlier
   real failure (measurement 2, section F).

`run_class_tests` never looks at `__unittest_skip__` (`:311-323`), so a
class-level `@unittest.skip` runs every body and counts every one as passed
(measurement 5).

### Both kernels are the same path

`handle` resolves a `ComparisonPolicy` (`:86-99`) and prints the faceted
announcement line; `report` appends the faceted note (`:290-293`). Neither
touches `run_class_tests`/`run_test`. `--faceted` and `--exact` therefore
produce identical verdicts and identical counts (measurement 3) — this is one
fix, not two.

### Colour is decoration, the word is the message

Every verdict is written through `termcolor.colored` (`:364`, `:372`, `:375`),
whose `_can_do_colour` returns false when stdout is not a tty and under
`NO_COLOR`/`ANSI_COLORS_DISABLED`/`TERM=dumb` (read in the workspace venv;
measurement 4 pipes a run and finds no escape sequences). So a captured log
distinguishes outcomes only by the words ` passed` and `FAIL!`, and the
per-instant dots are indistinguishable from one another.

### `skipTest` is already on offer

`solid_node/test.py:18` imports `unittest.TestCase as BaseTestCase`, `:1836`
derives the framework's `TestCase` from it, and `TestCaseMixin` (`:2482`)
carries it into a node. So `self.skipTest` exists on every companion case and
every node that mixes the mixin in (measurement 6) — it simply is not
honoured. `manager/test.py:19-20` already imports `solid_node.test` at module
scope, which imports `unittest`, so reading `unittest.SkipTest` in the runner
adds no import cost.

## The change

### 1. Each instant gets one of three outcomes

`run_test`'s loop classifies `skip` before `fail`, because `SkipTest` is an
`Exception` and a bare `except Exception` would swallow it:

```
except bdb.BdbQuit:          # unchanged (:348-350)
except unittest.SkipTest as e:
    step_skip += 1; skip_reason = skip_reason or str(e); mark = ('s', 'yellow')
except Exception:
    ... error = (...)        # unchanged (:352-361)
    step_fail += 1; mark = ('.', 'red')
```

A passing instant keeps `('.', 'green')`. A skipped instant prints a NEW
CHARACTER, `s`, rather than a new colour for the existing dot, so the outcome
survives a pipe (measurement 4) and no byte of an existing run's output
changes. `error` is only ever set by the `except Exception` arm, so a skip can
no longer overwrite a real failure's traceback.

`restore_children_checkpoints` still runs after every instant, skipped
instants included (`:366-368`): a method that raised `SkipTest` halfway may
have left an operation behind.

### 2. The method's verdict follows its instants

With `expecting = getattr(method, '__unittest_expecting_failure__', False)`
and `n = len(instants)`:

| instants | not marked | marked expected-to-fail |
| --- | --- | --- |
| every instant skipped | SKIPPED | SKIPPED (skip wins — `unittest` does the same, measured) |
| some skipped, rest passed | PASSED, saying how many skipped | UNEXPECTED SUCCESS |
| any instant failed | FAILED (last failing traceback, as today) | EXPECTED FAILURE (no traceback) |

Expectation is a property of the METHOD. Under a sweep, one raising instant is
enough to make the method an expected failure. The rejected per-instant
reading is in "Alternatives", with the actuator's own numbers.

The words written, all colour-independent:

| verdict | written | colour |
| --- | --- | --- |
| passed | ` passed` (unchanged) | green |
| passed with skips | ` passed (2 of 8 instants skipped)` | green |
| failed | `FAIL!` + traceback (unchanged) | red |
| skipped | ` skipped: <reason>` | yellow |
| expected failure | ` expected failure` | yellow |
| unexpected success | `UNEXPECTED SUCCESS!` | red |

`UNEXPECTED SUCCESS` is spelled the way `unittest`'s own text runner spells it
(`out-unittest-reference.txt`), so a maker who has seen one recognises it.

### 3. `--failfast` stops on what fails the run

The break at `:369` becomes conditional on the instant being a REAL failure —
`step_fail` grew and the method is not marked expected-to-fail — so a skip
never truncates a sweep (it does today, measurement 2, section D) and neither
does the expected raise of a marked method. At the run level `:378-379`
becomes `if self.failfast and verdict in (FAILED, UNEXPECTED_SUCCESS)`.

### 4. A class declared skipped runs nothing

`run_class_tests` checks `getattr(klass, '__unittest_skip__', False)` BEFORE
`setUpClass` (`:312`), and when set, counts each `test_`-prefixed attribute
once as skipped with `__unittest_skip_why__` as the reason and returns without
calling `setUpClass`/`tearDownClass`. `klass` here is sometimes the node
INSTANCE (`run_selection`, `:279`), and `getattr` on an instance finds the
class attribute, so one check covers both callers. A method-level
`@unittest.skip`/`@skipIf` needs no code at all: it wraps the function and
raises `SkipTest` when called (measurement 5), and `functools.wraps` carries
`testing_instants` through (measurement 2).

### 5. The counters and the summary

Three counters join the three at `:48-52`: `num_skipped`,
`num_expected_failures`, `num_unexpected_successes`. `num_tests` still counts
METHODS, so `N = P + F + S + X + U`.

`report` (`:285-300`) appends `, S skipped`, `, X expected failures`,
`, U unexpected successes` for each non-zero count, BEFORE the existing
parenthesised kernel/quantum notes. A run with none of them prints exactly
today's line — the discipline ADR-090 set for this output, and the
"An exact run reads as it always did" scenario the spec delta keeps.

### 6. The exit code

`:179-180` becomes
`if self.num_failed or self.num_unexpected_successes: sys.exit(1)`.
`run_tests` (`:302-308`) still does not exit — it is the seam
`tests/test_manager_test.py` drives — and is untouched.

`record_model_failure` (`:229-239`) is untouched: a model that cannot be
built is a failure, not a skip.

## Why this is an ADR — ADR-117

The exit-code contract moves in BOTH directions, and it is the contract every
CI job and every shop floor reads:

- a run whose only unusual result is a skipped test exits **0** where it exits
  **1** today;
- a run containing an unexpected success exits **1** where it exits **0**
  today — a green run becomes red because a statement about the machine has
  gone stale.

The second is the consequential one: it is the first time `solid test` fails a
run over something that did not raise. `unittest` has decided this the same
way since 3.4 (`wasSuccessful()` is false with `unexpectedSuccesses`,
measurement 1), and the framework follows it rather than inventing a third
answer. `ADR-117: An unexpected success fails the run` records the decision,
its two directions, and the `unittest` precedent, under
`docs/adrs/TEST-FRAMEWORK/`, with `docs/adrs/README.md` updated.

## Alternatives considered

1. **Delegate to `unittest`: build a real `TestSuite` and run it under a
   `TextTestRunner`/custom `TestResult`.** Rejected. The framework's unit of
   execution is the INSTANT, not the method (`:341-370`): between instants it
   sets a keyframe and restores every child's operation checkpoint
   (`:366-368`, the whole "Test runner lifecycle" contract). `TestCase.run`
   owns that loop and has no seam for it, would run `setUp`/`tearDown` per
   method where the runner runs them per method around the sweep (`:330-331`,
   `:380-383`), and a node mixing in `TestCaseMixin` is not a `TestCase` the
   loader can instantiate with a method name. A rewrite would put every
   ratified lifecycle scenario at risk to gain three classifications.
2. **Read the expectation per INSTANT: every instant of a marked method is
   expected to fail.** Rejected on the originating project's own numbers. The
   actuator's gap is a ~0.18° window at one configuration
   (`workflow/warts.md`, same finding, bullet (a)); a `@testing_steps(48)`
   sweep would report 47 unexpected successes and fail the run, so the marking
   would be unusable exactly where it was asked for. Method-level expectation
   also matches `unittest`, so a companion case reads the same under `pytest`.
3. **Count a skip as a pass.** Rejected: it makes a test that did not run
   indistinguishable from a test that ran and proved something — which is
   precisely the early-`return` workaround the finding was filed about.
4. **Let an unexpected success be a warning with exit 0.** Rejected: the
   silence is the bug. Measurement 1 shows `unittest` fails the run, and a
   stale expected-failure marking is a false statement about the machine that
   nothing else in the framework will catch.
5. **Always print `0 skipped, 0 expected failures, 0 unexpected successes`.**
   Rejected: ADR-090 fixed the discipline that a default run's summary stays
   byte-for-byte, and the ratified scenario "An exact run reads as it always
   did" states it.
6. **Give a skipped instant a new dot COLOUR instead of a new character.**
   Rejected by measurement 4: no colour survives a pipe or a CI log, which is
   where a skip most needs reading.
7. **Report the FIRST failing instant's traceback instead of the last.**
   Arguably better and deliberately out of scope: this change only stops a
   SKIP from becoming the reported traceback (`error` set in one arm only).
   Which real failure is reported when several instants fail is left as it is,
   and recorded as a finding.
8. **Leave the class-level `@unittest.skip` to a later change.** Rejected: it
   is the same finding (the runner has no skip concept), it is three lines in
   `run_class_tests`, and leaving it means a decorated class silently reports
   green on bodies that were never meant to run.

## What this change does not touch

- The comparison kernels, the verdict memo, the placement quantum, the
  broad phase: none of them is reached from the classification.
- `--all` and `record_model_failure` (`:229-239`).
- The build, the lock, the checkpoint/restore contract (`:385-411`).
- `docs`-level claims about assertions; only `solid test`'s own reporting.

## Reviewer's notes (ratification, 2026-09-15)

Ratified as written, with these additions binding on the implementation:

1. **A skip raised from `setUp` is in scope.** `run_test` calls
   `self.test_case.setUp()` inside its outer `try` (`:330-331`) but outside
   the instants loop's `except` arms, and `handle` catches only
   `StopTestRun` (`:176-177`), so today ANY exception `setUp` raises —
   `SkipTest` included — escapes the runner and aborts `solid test` with an
   uncaught traceback, no verdict, no summary. `self.skipTest(...)` in
   `setUp` is the commonest skip idiom (`unittest` skips the method), so the
   change honours it: a `SkipTest` from `setUp` reports the method as
   skipped with its reason, counts it once, runs no instant, and continues
   with the next test; `tearDown` still runs through the existing `finally`
   (`:380-383`), as it does today for every `setUp` outcome — say so in the
   docs. Any OTHER exception from `setUp` keeps today's behaviour exactly
   (the run aborts) and is filed in `workflow/warts.md` as a finding: a
   set-up error aborts the run without a verdict. `setUpClass` raising
   `SkipTest` stays out of scope as proposed; the same finding names it.
   Scenario "A skip declared in set-up" added to the ADDED requirement;
   tests in task 1.1.
2. **Number words in the summary.** `1 skipped`, `1 expected failure`,
   `1 unexpected success`; `N expected failures`, `N unexpected successes`
   for N ≠ 1; `skipped` never inflects. The tests in 1.2 assert these
   spellings.
3. **A skipped instant still restores the children's checkpoints** (design
   §1) — assert it in the sweep tests: a skip at instant 1 after an
   operation was added at instant 0 must not leak into instant 2.
4. **ADR-117** accepted as proposed, under `docs/adrs/TEST-FRAMEWORK/`.
5. **`shop-skills/solid-node-api/SKILL.md:1050`** is the reviewer's
   follow-up at the campaign's end, not this change's.
