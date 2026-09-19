# ADR-114: A Joint's Placement Is Identified By Its Slot, Not By What Bound It

**Status:** Accepted
**Date:** 2026-09-14
**Depends on:**
- [ADR-093: The joints of one class compose in declaration order](./ADR-093-joints-of-one-class-compose-in-declaration-order.md)
**Cites:**
- [ADR-099: The enumeration's simulate phases are one tree pass](./ADR-099-the-enumerations-simulate-phases-are-one-tree-pass.md)
**OpenSpec change:** `checkpoint-the-joint`

## Context and Problem Statement

Four mechanisms touch a node's operations, and until this decision they
identified an operation four different ways: the joint by the OBJECTS it
remembered placing (`node.__dict__['_joint_motion']`), the enumeration's
sweep by the ANIMATOR each operation was tagged with, the test runner's
checkpoint restore by the list's CONTENT, and `clear_solved` (ADR-099) not
at all — it dropped the coordinate's value and left the operations to the
other two.

Three of those four survive a tool replacing a node's `operations` list
wholesale. The fourth — the joint's own `Joint.clear`, reached from every
`Joint.place` before applying a new run — does not: it removed exactly
the object identities `place` had recorded, and a list replaced out from
under it (the test runner's checkpoint restore, deliberately by content
so a leaked operation is reverted wherever it was inserted) leaves those
identities pointing at objects no longer in the list. The next `place`
then finds nothing to remove and inserts beside whatever the restore put
back.

Measured on this worktree, minimised onto a framework fixture: a running
root's own placement, saved and restored around a later placement, left
a leaf carrying its joint's displacement TWICE — a `Free` joint's whole
four-operation run doubled to eight — or, when the restore's own moment
raced a sweep, not at all, so a geometry assertion measured a machine
that was not the machine. The originating project was the pin tumbler
lock (`projects/Locks/Pin_tumbler_lock`), whose migration to
`Time.running()` recorded a displacement applied twice on five driver
pins; `evidence.md` reproduces both faces on the framework's own
fixtures, step by step.

A second, narrower gap surfaced while designing the fix. Re-placing a
node's joints from the coordinates it holds — the natural repair for the
runner's restore — makes a placement OUTSIDE any lifecycle phase, so it
is motion but UNTAGGED, exactly as any out-of-phase binding is
(`apply_joint_motion`'s existing rule). ADR-099's `clear_solved` drops a
coordinate's value at the start of the assembly's next phase but, by
design, delegates the operations' removal to the sweep that runs one line
earlier — sound for a placement the enumeration itself made, which is
tagged, unsound for one that is not. Applying the restore's re-place
without also closing this gap traded the doubling defect for a narrower
loss: a coordinate an author's guarded `simulate()` leaves unbound on the
next run would still show the PREVIOUS run's placement, because nothing
untagged is swept and nothing else was watching. `evidence.md`'s revision
1 measures this exactly: green on the unchanged framework, red the
moment the restore's re-place lands, green again once this decision's
second half closes it.

## Decision

**A joint's placement is identified by the mark its operations carry —
`_joint_slot`, the joint's own index in `declared_joints(type(node))`,
stamped by `apply_joint_motion` (ADR-093) and nothing else — never by a
remembered object.** `Joint.clear(node)` removes every operation of
`node.operations` that is motion and whose `_joint_slot` equals this
joint's own slot, however many the placement produced and whatever has
happened to the node's operation list since. `_joint_motion` is kept as
the record of what a binding last applied — nothing else reads it — but
it is no longer what removal depends on. The slot is stable across a
wholesale list replacement because it lives on the operation itself, and
within one node it identifies exactly one joint, so a many-operation
placement (a `Free`'s four, an off-origin `Revolute`'s three) is removed
as the one unit it is.

**A joint's motion SHALL NOT outlive its coordinate's value.** Wherever
`clear_solved` drops the value and binder of a coordinate an assembly
bound in its previous simulate phase — the literal reading of ADR-099's
"a coordinate is cleared with the motion it caused" — it now also clears,
by slot, the joint that owns that coordinate: `declared_joints(type(
slot.node))`, the joint whose `coordinates` holds `slot.name`,
`joint.clear(slot.node)`. Both of `clear_solved`'s existing exemptions
stay in force and the new clear sits inside them: a slot some OTHER
assembly has already re-bound in the current enumeration is untouched,
and a coordinate a RUNNING SIMULATION owns is untouched, because the run
binds outside every enumeration and rebinds on every tick — the one
placement this decision must never reach.

**The test runner re-places what the enumeration will not.** A single
module-level seam, `re_place_declared_joints(node)`
(`solid_node/motion/joints.py`), reads every joint a node declares
through the coordinates it holds: clears a joint whose coordinates are
not all bound, places it otherwise. `CoordinateDelivery.restore`
(`solid_node/node/assembly.py`) — the rollback a refused `set_state`
already performed this way, by hand — moves onto it so the rule is
stated once, and the test runner's `restore_children_checkpoints`
(`solid_node/manager/test.py`) calls it for every CHILD it restored, only
after the content restore and never before it, and only for the children
`save_children_checkpoints` snapshotted — never for the node under test
itself, whose own operations the runner never replaces and therefore
never has to repair.

## Consequences

- A checkpoint saved and restored around a joint's placement leaves the
  child standing exactly at the coordinates it holds, on every instant
  and every test — the doubling and the loss `evidence.md` measures are
  both gone, confirmed by the same framework fixtures and by `solid
  test` over them (`evidence.md`, Task 5.1).
- An untagged placement — the shape any out-of-phase binding makes,
  the restore's own re-place included — no longer outlives an
  enumeration that leaves its coordinate unbound: a body an author's
  guarded `simulate()` does not rebind on a given run stands at rest on
  that run, matching what it did before a checkpoint was ever taken.
- A coordinate bound BY HAND outside any phase, on a joint some earlier
  phase had bound, no longer strands a permanent extra operation once
  the next enumeration re-solves it — the open question `evidence.md`'s
  first draft left unresolved. Measured separately: for a
  RELATION-bound coordinate this decision's first half (the mark-based
  `clear`) already closes it on its own, because the coordinate is
  re-placed regardless of the hand interference; the motion-with-its-
  value half is load-bearing specifically for a coordinate the next
  enumeration does NOT rebind.
- Fourteen existing suites — the joints, couplings, runner, running-mode,
  declarative and control suites — pass unchanged: 861 tests, 994
  subtests (`evidence.md`, Revision 1 §A7 and the implementation
  report). No public API is removed and no CLI surface changes.
- **Cost.** The re-place seam runs one `declared_joints` lookup per
  child the runner restores and one placement per bound joint, for root
  children only, twice per instant; `clear_solved`'s new clear is one
  `declared_joints` lookup per solved slot it already walks, plus a list
  filter only for the slots that own a joint. This is the one decision
  here that changes behaviour outside `solid test` — every render of
  every project pays it — and its control is the fourteen suites run
  unchanged against it.
- The originating project may now test the node the runner hands it
  rather than a private lock it builds for its own tests
  (`projects/Locks/Pin_tumbler_lock/simulation/test_lock.py`), a project
  change outside this decision's own commits.
