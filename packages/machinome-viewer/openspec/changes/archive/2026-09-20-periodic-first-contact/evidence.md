# Periodic first-contact evidence — 2026-09-20

Origin: Curta Type I, project `21c7502e88ca8dfe021b851c7410b2fd38c7c221`,
after framework `e63700e4fdb90e066d47f358e9de0ea935ac1be9` repaired the
producer. Viewer base `4355da1a7f64dacd7d86eb27dbdfdf7ced94598f`; planning
commit `8847234`. The pilot approved the matching consumer correction and
continuation through routine local integration, without another approval gate.

## Red, then green

- Exact producer corpus failed its PeriodicStop replay in the old viewer with
  StopInvariantError; stale fixture counts also failed separately.
- Focused tests initially reported 14 failures and 3 passes. One new time-drive
  fixture was itself incomplete: its source table omitted the implicit time
  admissions. That fixture was corrected, not counted as proof of the defect.
- The new coverage mutation failed before its guard was implemented.
- Final focused contact/corpus suite: 48 passes. It includes a mutation restoring
  endpoint-only attribution, which reproduces refusal before the corrected
  executor succeeds on the same producer document.
- Full widget suite: 49 files, 1,402 tests passed (40.18 s).
- TypeScript typecheck and production build passed.
- Full Python suite, including real Chromium server/capture/control tests:
  192 passed, 20 subtests passed (296.85 s). 51 dependency/deprecation warnings;
  no failures or skips.

Only first-contact attribution changes. Numeric bounds, frozen own arguments,
simultaneous stops, independent/relieving/disengaged admissions, time-drive
admissions, replay, no-snap assertions and atomic refusal remain covered.

## Paired corpus and actual project browser

The copied corpus is byte-for-byte producer output: 23 scenarios, 20 machines,
381 ticks; SHA-256
`4d937550b5fb5d5d6bc6b9e5f51428cb4cc106edab2286bb54975470c0005cc1`.
No expected values or tolerance were relaxed.

The freshly built isolated browser bundle SHA-256 is
`8acaf5989e5fa99bb5f3314c2080016603893ca8e665569a4d707ff24f8de751`.
API 23 and document versions 1–10 are unchanged. The project-owned command
`python -m simulation.tools.periodic_lockout_browser` runs Chromium in an
isolated page, not the pilot's Studio session. Its `--measured` mode exercises
the real exported ResultLocking assembly, not a handwritten substitute.

Original periodic export document SHA-256:
`7b6f259e4bf5e51e8439a1d52ef0681899a76f5d2d95072bf6d2fff891a3bd48`.
Both 120→150 and 120→840 requests stop at 125.22 degrees with the source shaft
held at 189.6 degrees, no error and the worker present. The screenshot was
inspected: source-backed drum, bell and shafts are visible and the control
reads 125.2200 degrees.

Measured ResultLocking export document SHA-256:
`1fc33714744a0de08cf9dc40431cf921418c080e3870852df888cd9f517cfa20`.
Seven previously geometry-certified first-contact poses agree with Python:

| Withdrawal | First stop (degrees) |
| --- | --- |
| 120 | 125.22323837227304 |
| 480 | 485.2280105590762 |
| 840 | 845.2050994865567 |
| 1200 | 1205.2280067446554 |
| 1560 | 1565.2280067446554 |
| 115 | 120.38810729947272 |
| 123 | 129.82507171577254 |

All seven pass exact snapshot replay, 0.05-degree backward relief, idle hold
and blocked retry. Four legal 1,080-degree controls (digits 0, 3 and 9, plus
lifted subtraction) complete. No browser errors. Reports and screenshots are
generated under the project's ignored `_build_periodic_lockout/` and
`_build_result_locking/`; the durable reproducer is project-owned.

Complete native-solid and published-mesh geometry certification of those seven
poses is in the producer's archived `periodic-lockout-first-contact` evidence:
14 zero-volume contacts and 14 positive 0.2-degree overtravel controls. This
consumer cycle does not claim to have repeated those geometry operations.

## Boundaries and continuation

ADR-069 amends ADR-054; both modified baseline requirements are synced. No
interface, schema, package version, licensing or published release changes.
Finite sampling can still miss narrow unsampled obstacles; a compound-only
push with no individual pusher still refuses transactionally. The separate
restore-ring cursor finding in the producer's corpus harness is deferred;
the unchanged producer fixture uses a separate quiet restore step.

This proves the viewer correction, not completion of OperatingCurta. Project
work next adopts the measured ones restraint on the actual crank; other
channels, wrong-order controls, clearing loop and whole-machine acceptance
remain project tasks. No upstream print geometry was changed in this cycle.
