# Apply finding: ordinary chains have the same timing defect

2026-09-22. Status: implementation paused for a scope decision; no solver code
changed. This is evidence, not a revision to the ratified design or permission
to change its preservation guarantees.

Planning commit `a072b15` follows pilot ratification and successful strict
validation. Its clean tree and exactly one-commit ancestry above `e6a42c8`
were verified before adding the tests. All production source remains at the
base; uncommitted changes are test and evidence work only.

## Red-first proof

New public-declaration fixture `tests/carriage_project/timed_carry.py` has a
lever that stops at 1 and a successor driven while the lever is at least .5.
The crank moves 0..4 in one request. A later station participates in the union
dependency graph, has its own selector at crank 1, and cannot actively affect
the earlier carry at the selected position. No internal monkeypatching is used.

`pytest -q tests/test_running_carry_timing.py` on unchanged production source:

- Without later station: higher.turn 2; with it: 3.5. Graph-extension invariant
  fails by 1.5.
- The landed-lever physical oracle is 3.5: the .5 gate is reached at crank .5,
  leaving 3.5 of driven travel. Bulk result 2 fails.
- For an upstream `clamp01(2*crank)`, the .5 gate is reached at crank .25;
  expected 3.75, bulk result 2 fails.
- Whole-versus-16-portions comparison fails for three of four fixture variants.
- Pytest reports `6 failed, 1 passed, 1 subtests passed in 1.28s` (three direct
  failures and three failing subtests; the parent subtest method counts as a
  pass). These are arithmetic failures, not setup errors.

An initial fixture attempt incorrectly supplied a rest binding for an ordinary
law-driven lower shaft. It failed `DoublyBound` before exercising the bug; that
fixture error was removed and is not counted as the red proof above.

## Conflicting preservation guarantees

`evidence/frozen_timing.py` uses the repository's EXISTING `ShiftedCarry` and
`FixedZero` models, not the new fixture. Complete banks, commands and block
counts are retained in `evidence/frozen-timing.json`.

| Existing model | Blocks | One 0..4 move: higher.turn | Sixteen portions |
| --- | ---: | ---: | ---: |
| ShiftedCarry, shift 0 | 1 | 2 | 3.5 |
| FixedZero, same laws frozen at shift 0 | 0 | 2 | 3.5 |

All commands complete and admit their full travel. Both models land the carry
at 1. This proves the timing loss also occurs in an ordinary acyclic chain.
The normal frozen-equivalence test covers only twelve small ticks, and the
existing partition test travels only .7, before the lever lands at 1. Those
tests never exercise this conflict.

The ratified design's decision 1 leaves ordinary no-block execution unchanged.
ADR-122's decision drivers preserve no-block meaning, path and cost. The
ratified delta also retains the scenario “The carry happens at one position
and not the other”, which requires the selected machine to equal its ordinary
acyclic twin with the SAME laws frozen at that selection.

For the measured request those guarantees cannot both survive the proposed
correction: fixing ShiftedCarry's timing gives 3.5, preserving FixedZero's
current no-block behavior keeps 2, and the required equivalence is lost.
This conflict was missed during proposal review. It is not a reason to retain
the wrong answer, silently broaden implementation, or rewrite a golden.

## Decision requested

Recommended: revise the change to preserve demanded source timing for affected
ordinary chains as well as selected blocks, keeping the physical law/frozen-
selection equivalence and the unchanged Curta oracle. Replace the blanket
no-block behavior/cost preservation with a narrower guarantee for paths whose
existing affine handoff is exact, and explicitly review affected conformance
and consumer semantics. This is empirical scope from Curta's existing frozen
carry model, not speculative support for another machine.

Alternative: retain ordinary endpoint behavior and explicitly withdraw the
frozen-equivalence promise for these trajectories. This gives the same laws
different physics depending on graph shape and is not recommended.

Neither option is implemented or ratified here. Under the framework-change
skill, wait for the pilot, then invoke the update workflow if revision is
chosen; validate and amend only planning commit 1 after re-ratification,
preserving these uncommitted test/evidence changes. No intermediate
implementation commit, ADR, archive, or integration has been made.

## Pending diagnostic worker at pause

The unchanged four-test Curta replay was launched from this bench using its
production source first on PYTHONPATH and the canonical project root second.
Its log is `evidence/red-curta.log`; session 25315. The seven-station case is
red; the constrained full-bank case is still running at this checkpoint.
Task 1.4 is deliberately not checked off until its complete results, source
hashes and bank/status evidence have been recorded. The worker is diagnostic,
not a solver change, and has not been cancelled.
