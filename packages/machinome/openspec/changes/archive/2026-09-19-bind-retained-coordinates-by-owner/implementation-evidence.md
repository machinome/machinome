# Implementation evidence

## Identity and scope

- Framework base: `c62319e1974b88d8cfd2dd13fd205c7bf2533991`
- Planning commit: `0ccdc6bdc11637a06ebb233b3075e1602a661f57`
- Project checkpoint: `1aaad6c37c1117b3582977a199ebf4c5722c4c97`
- Implementation is confined to private state-delivery provenance and focused
  tests. It changes no public API, architecture, dependency, export schema or
  viewer contract; no ADR is warranted.

## Red-first evidence

Before the product edit:

```text
python -m unittest tests.test_retained_coordinate_delivery
Ran 2 tests: FAILED (failures=3)
ring bound 40 instead of retained -20; complete-bank result [35, 35, -30]
instead of [35, -65, -30].
```

Adversarial review then exposed a first-candidate regression where mixed bare
and qualified `turn` entries were accepted. Both insertion orders were pinned
red before the carrier was revised to retain ordered provenance variants. The
final tests also preserve established last-write precedence for accepted bare
and qualified aliases of a single driver or coordinate owner.

The separate root reviewer subsequently exercised all 720 permutations of the
complete nested bank plus `time`, and all six combinations of bare `turn` with
one of the three qualified owner paths in both mapping orders. Every complete
bank preserved `(20, -90, -146)` and every mixed ambiguous request named all
claimants with exact rollback. The review also matched the base behavior for
both orders of the accepted single-owner `slide.travel`/`travel` aliases.

## Framework proof

All commands used `PYTHONPATH="$PWD"` and the workspace Python.

```text
python -m unittest tests.test_retained_coordinate_delivery
Ran 11 tests: OK

python -m unittest tests.test_retained_coordinate_delivery \
  tests.test_kinematics tests.test_running_simulation \
  tests.test_running_document tests.test_export tests.test_simulate_split \
  tests.test_clocked_sim
Ran 312 tests in 28.250s: OK

python -m unittest tests.test_retained_coordinate_delivery \
  tests.test_running_simulation.SetStateCoordinateTest
Ran 16 tests in 0.968s: OK
```

Coverage asserts owner slots and local/world placements for parent, child and
grandchild; normal/reverse/repeated bank delivery; bare coordinate and mixed
coordinate/driver ambiguity with rollback; class/site/multi-coordinate joints;
bare/qualified driver and `time` reach; snapshot/reset; and each serialized
node's own owner-qualified expression with exact numeric live-pose restore.

## Originating-project acceptance

Commands ran unchanged from the Curta project with the framework worktree
first on `PYTHONPATH`.

```text
python -m simulation.tools.retained_pose_probe --minimal
# carrier/ring/wheel bank and bound pose agree at rest, parent=20, ring=-90

python -m unittest simulation.tools.test_retained_pose_probe
Ran 2 tests in 0.757s: OK

machinome test --faceted simulation/test_running_motion.py
Ran 3 tests in 23.35s: 3 passed, 0 failed
```

The root reviewer completed task 4.3 with actual world-mesh captures and
before/after inspection. See [adversarial and visual review](evidence/review.md)
for the independently checked results, capture command and content identities.

## Completion

Adversarial review passed before synchronization. Both added requirements were
merged into their kinematics and simulation baseline specs, and an exact-text
comparison verified that every previous baseline byte was preserved. All 14
tasks and all planning artifacts were complete when this `spec-driven` change
was archived to
`openspec/changes/archive/2026-09-19-bind-retained-coordinates-by-owner/`.

Before archival, `openspec validate --all --strict --no-interactive` passed all
35 items (the change and 34 baseline specs). After archival, the same command
passed all 34 baseline specs. The final post-archive run of
`tests.test_state_binding`, `tests.test_running_corpus` and
`tests.test_retained_coordinate_delivery` passed 55 tests in 1.779 seconds.

The completed cycle remains on its isolated branch. Framework `main` is still
at the recorded base; integration, push and publication were not performed.
