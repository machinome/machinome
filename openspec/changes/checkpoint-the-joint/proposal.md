## Why

The `solid test` runner checkpoints each ROOT CHILD's operation list around
every test and restores it by CONTENT, while a joint removes its previous
placement by the OBJECT IDENTITIES it recorded in `node._joint_motion`. After
a restore those two disagree, and a leaf that owns a joint then stands where
its own coordinate does not say: measured on this worktree as a displacement
applied TWICE (the pin tumbler lock's five driver pins, 0.1 mm deep) and, in
the shape a plain scenario run produces, as a displacement applied NOT AT ALL.

The originating project is the pin tumbler lock
(`projects/Locks/Pin_tumbler_lock`), whose migration to `Time.running()` under
the `bounds-read-other-coordinates` cycle recorded the finding
(`workflow/warts.md`, "Pin tumbler lock (2026-09-14 …)", first bullet). Its
cost there was a false `assertNoSolidInterference` failure
(`core should not interfere with d2, intersection volume 0.103`) from the
second geometry test on, and a project that now builds a lock of its own
rather than testing the one the runner hands it. The reproduction, minimised
onto a framework fixture and measured step by step, is in `evidence.md`.

## What Changes

- A joint SHALL remove its whole previous placement when it is placed again
  or cleared, even when the operation objects in the node's list were
  replaced since the placement was made — a joint's operations are already
  marked with the joint's own declaration slot, and that mark, not a
  remembered object, is what identifies them.
- A joint's motion SHALL NOT outlive its coordinate's value. The framework
  already drops the value of every coordinate an assembly bound in its
  previous simulate phase; it SHALL now drop that coordinate's PLACEMENT in
  the same moment, so a body cannot stand at a pose no coordinate states —
  the missing half of "An author-bound joint is cleared with its motion",
  which today relies on the sweep and so reaches only a placement the
  enumeration itself made.
- The test runner's checkpoint restore SHALL leave every restored CHILD of
  the node under test posed at the coordinates it holds: after restoring the
  list by content it re-places each joint the child declares from that
  child's own coordinate values (and clears one whose coordinates are
  unbound), so a child's placement and its coordinates never disagree across
  a test boundary. A joint declared on the node under test ITSELF is not
  checkpointed and not re-placed.
- The runner's existing guarantee is kept unchanged: an operation a test
  leaked — appended or INSERTED anywhere — is still reverted, and a child
  that declares no joint is untouched.
- No change to the geometry an untimed, jointless or sub-assembly-held node
  reports at any test, and no change to the runner's output.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `joints`: a new requirement that re-placing or clearing a joint removes
  every operation its previous placement applied, however the node's
  operation list was replaced in between.
- `joints`: the "An author-bound joint is cleared with its motion"
  requirement is made literal — the placement is dropped with the value
  rather than left to the sweep, so an untagged placement cannot outlive
  the value it stated.
- `test-framework`: the "Test runner lifecycle" requirement gains the
  restore's obligation to re-place a restored child's joints from the
  coordinates it holds.

## Impact

- `solid_node/motion/joints.py` — `Joint.clear` drops by the joint's own
  mark rather than by recorded identity; one new module-level seam that
  re-places every declared joint of a node from the coordinates it holds.
- `solid_node/node/assembly.py` — `CoordinateDelivery.restore` already
  hand-writes that loop and moves onto the new seam, so the framework states
  it once.
- `solid_node/motion/couplings.py` — `clear_solved` clears, by slot, the
  joint of every coordinate whose value it drops. The records it already
  walks are slots, and a slot carries `.node` and `.name`, so nothing new
  has to be recorded to reach the joint.
- `solid_node/manager/test.py` — `restore_children_checkpoints` calls the
  seam for each restored child.
- Projects: the lock can go back to testing the node the runner hands it;
  every running project whose tests step a `Sim` (Pascaline, Curta bench)
  is measuring a tree that may be mis-posed today.
- No public API is removed and no CLI surface changes.
