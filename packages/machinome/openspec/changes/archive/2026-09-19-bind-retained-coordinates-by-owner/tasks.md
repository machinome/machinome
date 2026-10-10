## 1. Red-first owner-delivery proof

- [x] 1.1 Add focused nested-joint tests that first fail with the bank, bound
  coordinate and rendered pose disagreeing after independent parent and child
  movement under the current delivery.
- [x] 1.2 Prove the failure depends on complete-bank insertion order, then pin
  equal normal-order and reverse-order results as the acceptance contract.
- [x] 1.3 Pin compatibility before implementation: bare coordinate/coordinate
  and coordinate/driver collisions remain ambiguous with full rollback, while
  bare drivers, qualified drivers and global `time` keep their existing reach.
- [x] 1.4 Add targeted class-declared, site-declared and multi-coordinate cases
  proving every coordinate form observes the same owner boundary.

## 2. Owner-scoped delivery

- [x] 2.1 Preserve original qualification provenance as state entries descend
  and stop a consumed qualified coordinate at its owner without stopping an
  originally bare ambiguity-discovery entry.
- [x] 2.2 Run the focused tests green and verify repeated complete-bank binding
  is absolute, order-independent and does not advance the run.

## 3. Restore and publication regressions

- [x] 3.1 Test snapshot restore and reset on distinct nested retained values,
  asserting the bank, coordinate slots and rendered transforms together.
- [x] 3.2 Test symbolic document publication with nested same-named coordinates,
  owner-qualified expressions and exact restoration of the live numeric bank
  and pose, without a schema or version change.
- [x] 3.3 Run the relevant kinematics, running-simulation, serializer and export
  suites plus broader simulation/export regression coverage.

## 4. Originating-project acceptance

- [x] 4.1 Run the unchanged Curta minimal probe and
  `simulation.tools.test_retained_pose_probe` at project checkpoint `1aaad6c`.
- [x] 4.2 Run unchanged `simulation/test_running_motion.py` carriage-shift and
  clearing geometry acceptance and record the framework/project commits.
- [x] 4.3 Capture and inspect the carriage-shift and clearing visual evidence,
  recording any environmental limitation without changing Curta geometry,
  laws or tolerances.

## 5. Completion checks

- [x] 5.1 Confirm the implementation restores ADR-105 without a public API,
  architecture, dependency, export-schema or viewer change; create no ADR
  unless implementation evidence contradicts that classification.
- [x] 5.2 Run strict OpenSpec validation and final targeted and regression tests,
  then record commands and results for adversarial review before sync/archive.
