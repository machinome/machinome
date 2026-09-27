# Implementation evidence

Framework base: `6ca6061f576a512fb31d6412815c38bd6c1e6485`; planning commit:
`42b42eacb2a6d4e05deacbd6a5d60a0179b41290`. The worktree was clean and
exactly one commit above base before implementation.

## Red-first numerical and public-frame proof

With production unchanged, `/home/asa/devel/machinome/.venv/bin/python -m
pytest -q tests/test_mate_rotation_conversion.py` reported **27 failed,
3 passed, 32 subtests passed in 1.45s**. Pure Z -95.6 returned X/Y
`-5.028708403180495e-09`; signed principal cases reconstructed spurious
off-axis motion, genuine small axes were lost or distorted, and the public
Frame mate emitted the same erroneous axis. These fixtures use independently
constructed Rodrigues matrices and public operation matrices, without CAD.

## Narrow implementation and green proof

Only `_axis_angle` recovery and its explanatory docstring change. Above
90 degrees, the dominant diagonal component alone takes a square root;
other components come from symmetric off-diagonal terms. Equal diagonal
squares retain equal magnitudes for symmetric-axis serialization. Angle
recovery, sign orientation, normalization policy, identity omission and
the `1e-9` whole-number snap remain unchanged. No interface, schema,
translation, operation order, binding or author parameter changes occur.

The first green run identified four fixture assertions incorrectly expecting
an unsnapped dominant `0.99999999999`; reconstruction already passed. Those
assertions now explicitly honor the unchanged whole-number snap, while
genuine small components still require retention and strict reconstruction.

Focused plus complete `tests/test_mates.py`: **139 passed, 462 subtests
passed in 2.70s**.

Selected command, from this worktree:

```sh
/home/asa/devel/machinome/.venv/bin/python -m pytest -q tests/test_mate_rotation_conversion.py tests/test_mates.py tests/test_mate_contracts.py tests/test_mate_contract_review.py tests/test_mate_contract_docs.py tests/test_mate_existing_joint.py tests/test_existing_mate_review.py tests/test_frames.py tests/test_joints.py tests/test_operations.py
```

Result: **421 passed, 853 subtests passed in 6.50s**. One existing
`Symbolic.render()` time-read deprecation warning; no failures. No native
CAD was used.

## Root review and originating caller

Root adversarial review accepted the narrow implementation. Independent
`tests/test_mate_rotation_adversarial.py` passed 3 tests and 27 subtests
in 1.02s, including 1200 seeded rotations, small-axis permutations on both
sides of 180 degrees, and composed nonidentity public frames with an existing
joint. Loading the review module with importlib (registered in sys.modules)
from the primary checkout, with imported mates.__file__ verified, reproduced
26 failing subcases in 3 tests / 0.767s: 24 small-axis and 2 public-pose cases.
The seeded generic and oblique exact-halfturn witnesses already passed base.

Root's unchanged Curta command was `python -m unittest -v
simulation.test_selector_mates simulation.test_register_mates
simulation.test_mate_refactor`, using this worktree on PYTHONPATH:
8 tests passed in 8.980s. The selector-only baseline had 1 failure in 2 tests
/ 1.033s, with discrepancy 1.0524132676437148e-8. Caller HEAD was `4b2ea5a`;
Git blobs: selectors `e016939988de8c14fa912f987901653747cd69cc`,
selector_frames `3425a6d6b5f2aae0429ee12378fd3f34d96b2a0b`,
test_selector_mates `4b9150cf2b02aa011068a5f2a2fc383262758b57`.
Reviewed numerical source blob: `00420601bf6ad15155543ac6399359f3a74007d3`.
No caller tolerance or source was changed by this apply agent. The separate
whole operating-state batch imported the old framework and is not acceptance
evidence for this fix. Numerical pose equivalence is not a measured fit claim.

## Completion checks

Final selected command is the preceding ten-file command with
`tests/test_mate_rotation_adversarial.py` added: **424 passed, 880 subtests
passed in 6.69s**, with the same single existing deprecation warning.
`openspec validate --all --strict`: **37 passed, 0 failed**.
`git diff --check` passed. All eleven tasks are complete after explicit root
review and completion authorization. The sole mates baseline delta was synced
and verified; OpenSpec archived through `openspec archive
stable-mate-rotation-conversion --skip-specs --yes` after manual sync. Workflow
intent is archived under `workflow/archive/stable-mate-rotation-conversion-2026-09-27/`.
Integration, cleanup and any post-integration caller checks remain root-owned.

## Decision disposition

This is a nonarchitectural correction to the already ratified whole-triad
rest-placement contract and numerical conversion. No new ADR or manual/API
change is warranted. Existing ADR-147 remains authoritative; the change
does not introduce a new architectural decision.
