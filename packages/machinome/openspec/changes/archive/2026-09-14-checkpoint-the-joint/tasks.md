## 1. Red first: pin the defect on the framework's own fixtures

No new fixture PROJECT is needed. `tests/running_project/machine.py`'s
`Train` is a running root whose `slide` is a ROOT-LEVEL LEAF owning a
`Prismatic`, and `TrainBody` is the untimed twin of the same tree.
`Sixfree`'s `chassis` does carry a `Free` at root level, but a run refuses
it (`the rest render leaves chassis.pose.pitch, chassis.pose.roll unbound`),
so the `Free` case needs one more machine in that module with all six
coordinates driven — `evidence/bench/machine.py`'s `floater` is the shape.
`tests/test_manager_test.py` already owns the runner's checkpoint tests
(`RestoreChildrenCheckpointsTest`), and `tests/test_joints.py` the joint's.

- [x] 1.1 In `tests/test_manager_test.py`, add a failing test that drives the
      runner's real `save_children_checkpoints` / `restore_children_checkpoints`
      over a built `Train` through the sequence of `evidence.md` §1 — a `Sim`
      poses the tree, the checkpoint is taken, a second `Sim` poses it, the
      checkpoint is restored, a third `Sim` poses it — and asserts that
      `slide` carries exactly ONE motion operation, stating the value
      `get_coordinate(slide, 'travel')` holds. It must fail with two
      operations before any implementation.
- [x] 1.2 Add a failing test for the LOST face (`evidence.md` §7): after a
      `Sim` has posed the tree, the checkpoint is restored and
      `set_keyframe(0)` is called, `slide`'s motion operations must still
      state the coordinate it holds. It must fail with no motion operation.
- [x] 1.3 Add a running fixture to `tests/running_project/machine.py` whose
      root-level leaf carries a `Free` with all six coordinates driven, and a
      failing test (`evidence.md` §3) that the same sequence leaves it
      carrying ONE run of the `Free`'s operations — four — and not two runs
      of four.
- [x] 1.4 In `tests/test_joints.py`, add a failing test that binds a joint,
      replaces the node's `operations` list wholesale with a copy of an
      earlier list still holding that placement, binds again, and asserts one
      placement remains — the joints-capability half, with no runner in it.
      Add the sibling-joint case (a node declaring two joints: re-placing one
      leaves the other's operations alone, in declaration order) and the
      clear case (clearing a joint whose list was replaced leaves nothing of
      its placement).
- [x] 1.5 Add a test that every joint kind's placement carries its
      `_joint_slot` (`Revolute` centred and off-origin, `Prismatic`, `Orbit`,
      `Free`), so a future placement path that bypasses `apply_joint_motion`
      is caught by this suite rather than by a project.
- [x] 1.6 RED FIRST for revision 1's Finding A. Add an UNTIMED fixture
      whose root's `simulate()` binds a ROOT-LEVEL LEAF's joint only
      under a guard (`evidence/bench/conditional.py`'s `Conditional` is the
      shape: no time base, `if self.time < 0.5: self.gate.travel = 10.0`), and
      in `tests/test_manager_test.py` a test that drives the runner's
      `save_children_checkpoints`/`restore_children_checkpoints` over it
      across instants 0 and 1 — the first binds, the second does not — and
      asserts the leaf carries NO motion operation at instant 1 and its
      coordinate is unbound. This test is GREEN on the unchanged framework
      (`evidence.md` §A1) and turns RED as soon as task 3.1's re-place lands
      (`evidence.md` §A2), so it must be written in step 1 and re-run after
      3.1 to see it fail; task 4.0 is what turns it green again. Add the
      joints-capability twin in `tests/test_joints.py`: an untagged placement
      standing on a leaf whose coordinate the next enumeration does not
      rebind must be gone after that enumeration.
- [x] 1.7 Add the green-before-and-after controls: an untimed `TrainBody` run
      through the same checkpoint cycles reports the same placement
      throughout (`evidence.md` §4), a leaked operation inserted anywhere in
      a child's list is still reverted by the restore (the existing
      `test_restore_reverts_inserted_operations_too` covers the insertion; add
      one that leaks an operation on a child that ALSO owns a joint), and a
      child whose class declares no joint is restored unchanged.

## 2. The joint half

- [x] 2.1 Change `Joint.clear` (`solid_node/motion/joints.py:738`) to drop
      every operation of `node.operations` that is motion and whose
      `_joint_slot` is this joint's slot in `declared_joints(type(node))`,
      instead of dropping the recorded objects. Keep `_joint_motion` as the
      record `place` writes, and rewrite the docstring: the mark is the
      handle, and a list replaced under the joint is cleaned anyway.
- [x] 2.2 Add the module-level seam that re-places every joint a node
      declares from the coordinates that node holds — clear the joint when
      any of its coordinates is unbound, place it otherwise — reading the
      values through `get_coordinate` and taking the `Free`/multi-coordinate
      arity from `joint.coordinates`, exactly as
      `CoordinateDelivery.restore` does today.
- [x] 2.3 Move `CoordinateDelivery.restore`
      (`solid_node/node/assembly.py:317`) onto that seam so the rule is
      stated once, and confirm `tests/test_running_simulation.py`,
      `tests/test_running_stops.py`, `tests/test_running_jumps.py` and
      `tests/test_running_document.py` are unchanged by it.
- [x] 2.4 Run `tests/test_joints.py`, `tests/test_motion_package.py`,
      `tests/test_couplings.py`, `tests/test_kinematics.py` and
      `tests/test_mechanisms.py`; 1.4 and 1.5 turn green here, 1.1-1.3 do not
      yet.

## 3. The runner half

- [x] 3.1 Have `restore_children_checkpoints`
      (`solid_node/manager/test.py:395`) call the seam for each child it
      restored, after the content restore and never before it, and for the
      children it checkpointed ONLY — never for the node under test. A child
      whose class declares no joint must cost nothing beyond the lookup.
- [x] 3.2 Run `tests/test_manager_test.py`; 1.1-1.3 turn green, 1.7 stays
      green, and 1.6 turns RED — the regression revision 1's Finding A
      predicted, now measured in the suite rather than in a probe. Record
      the failure before going on.

## 4. The motion goes with the value (revision 1, direction (ii))

- [x] 4.0 Change `clear_solved` (`solid_node/motion/couplings.py:1786`) so
      that for every slot whose value and binder it drops it also clears, by
      slot, the joint that owns that coordinate: `declared_joints(type(
      slot.node))`, the joint whose `coordinates` holds `slot.name`,
      `joint.clear(slot.node)`. Both existing exemptions stay and are what
      keep the running root's placements untouched — a slot whose
      `_enum_marker` is the current enumeration, and a `run_owned` slot — so
      the joint clear must sit INSIDE them, after the two `continue`s.
      Task 1.6 turns green here.
- [x] 4.1 Run `tests/test_couplings.py`, `tests/test_joints.py`,
      `tests/test_manager_test.py`, `tests/test_running_simulation.py`,
      `tests/test_motion_package.py`, `tests/test_kinematics.py`,
      `tests/test_mechanisms.py`, `tests/test_running_stops.py`,
      `tests/test_running_jumps.py`, `tests/test_running_document.py`,
      `tests/test_declarative_nodes.py`, `tests/test_declarative_render.py`,
      `tests/test_animator_tag.py` and `tests/test_controls.py`: all of them
      passed against the probe that applied this design
      (`evidence.md`, Revision 1 §A7), so any failure here is the
      implementation diverging from what was measured.
- [x] 4.2 Add the untimed HAND-binding test of `evidence.md` §6/§A5: the
      operation a hand binding stranded is gone after the next
      `set_keyframe`, and the leaf stands at the value the enumeration bound
      — the permanent ghost that was open question 2.

## 5. Specs, decision record and the evidence of the fix

- [x] 5.1 Re-run both probes and the fixture's `solid test`
      (`evidence.md`'s commands) and append their post-fix output to
      `evidence.md` under a section of its own, alongside the red output
      already recorded — the same numbers, now agreeing with the
      coordinates.
- [x] 5.2 Re-run the wart's own reproduction on the lock
      (`evidence/probe_lock.py`) and record it.
- [x] 5.3 Write the ADR, numbered next in `docs/adrs/`, and add it to the
      index. State it as the INVARIANT it introduces, not as a bug fix:
      *a joint's placement is identified by the mark its operations carry,
      never by a remembered object; a joint's motion never outlives its
      coordinate's value; and the test runner re-places what the enumeration
      will not.* Link `docs/adrs/NODE/ADR-093-joints-of-one-class-compose-in-
      declaration-order.md` (the declaration slot the mark reuses) and
      `docs/adrs/NODE/ADR-099-the-enumerations-simulate-phases-are-one-tree-
      pass.md` (the clear-with-its-motion semantics this makes literal).
      Keep it short.
- [ ] 5.4 Sync the three delta requirements into
      `openspec/specs/joints/spec.md` and
      `openspec/specs/test-framework/spec.md`, and archive the change.
- [x] 5.5 Update `workflow/warts.md`: mark the pin tumbler lock's first bullet
      fixed by this change, and correct its two factual errors — the untimed
      model is NOT immune (it is only rarer; `evidence.md` §6), and the
      reproduction as recorded no longer reaches the defect on its own
      (`evidence.md` §8).
- [x] 5.6 Run the full suite once
      (`PYTHONPATH="$PWD" .venv/bin/python -m pytest tests -q`) and record
      the result in the implementation report.

## 6. The originating project (outside this change's commits)

- [x] 6.1 Report to the pilot that
      `projects/Locks/Pin_tumbler_lock/simulation/test_lock.py` can drop
      `lock_under_test()`'s private lock and test the node the runner hands
      it — a project change, made in the project's own repository, under the
      pilot's direction.
