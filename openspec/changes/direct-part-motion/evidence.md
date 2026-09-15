# Pre-implementation evidence — 2026-09-15

Origin: the pilot approved direct mechanical operation of
`projects/Calculators/Curta-Type-I-3x`, including individual selectors,
crank lift/rotation and carriage lift/rotation, without automatic sequencing.

At framework base `3519c61bf6d79e2be5df7a5972411358c9ae2371`, run from
this cycle worktree with the workspace environment:

```sh
PYTHONPATH="$PWD" /home/asa/devel/libresolid-studio/.venv/bin/python -m pytest tests/test_controls.py::RefusalTest::test_a_turn_on_a_coordinate_that_does_not_turn_is_refused tests/test_controls.py::RefusalTest::test_a_node_declaring_two_joints_is_refused -q
```

Result: **2 passed in 1.14 s**. These tests prove the current intentional
refusals, not the proposed features. The fixtures `Sliding` and `TwoJoints`
exercise the public Sim path and assert the named translational-domain and
multiple-joint errors. The new positive feature tests must still run red
after ratification and before implementation.

At viewer base `33ac0ad934ee5011f2085365134a640bd4544ee8`, the source
`solid_node_viewer/widget/src/partControls.ts` lists only button/turn and
unconditionally validates a leading rotation. This also rejects a prismatic
button, even though a press does not need angular gesture math. No viewer
behavioral test for the new feature has yet been run.

The project currently declares one operand Driver and derives all eight
selector settings from it. Its crank and register carriage each already own
both turn and lift joints. Its custom calculator page keeps register history
outside the run and performs operation preparation. The approved migration
removes those interaction abstractions; existing source-fit findings remain
separate work, not evidence for this prerequisite.

No production source has been changed and no prerequisite implementation is
claimed complete. Ratification, new feature red tests and paired browser
verification are outstanding.
