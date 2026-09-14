## Context

Four mechanisms touch a node's operations, and they identify an operation
differently: the joint by the objects it remembers, the enumeration by the
tag it stamped, the test runner by the list's content, and `clear_solved`
not at all — it drops the coordinate and leaves the operations to the
others.

**The joint.** `Joint.place` (`solid_node/motion/joints.py:645`) calls
`self.clear(node)` and then `apply_joint_motion(node, …, slot)`
(`solid_node/node/base.py:370`), which stamps every operation of the
placement with `operation._motion = True` and `operation._joint_slot = slot`
— the joint's index in `declared_joints(type(node))`, unique per joint within
one node — and inserts the whole run at that slot's position. `place` then
records the operation OBJECTS in `node.__dict__['_joint_motion'][name]`.
`Joint.clear` (`joints.py:738`) pops that record and removes exactly those
objects, `if not any(operation is dropped …)`. Its own docstring already
admits the weakness: "the test runner's checkpoint restore can replace the
list wholesale, so an operation that is no longer there is simply not there."

**The enumeration.** `_sweep` (`solid_node/node/assembly.py:16`) removes
operations by ANIMATOR identity (`operation._animator is assembly`), and it
says why: a tag-based sweep "drops them anyway … regardless of which
operation OBJECT currently sits in the list". Every operation a simulate
phase applied is tagged, so a wholesale list replacement cannot strand one.

**The runner.** `save_children_checkpoints` / `restore_children_checkpoints`
(`solid_node/manager/test.py:385`, `:395`) snapshot and restore each ROOT
CHILD's list BY CONTENT, deliberately: "an operation INSERTED anywhere in the
list (not just appended) is reverted too."

Under a RUNNING root the third path appears: `set_state`'s
`CoordinateDelivery` (`assembly.py:255`, reached from `_receive_state`,
`assembly.py:516`) binds joint coordinates through `set_coordinate`
(`solid_node/motion/ports.py:494`) during the pre-enumeration delivery walk,
so `place` runs with no lifecycle phase current. `apply_joint_motion` marks
those operations as motion and stamps their slot but does NOT tag them
(`phase is None`), by design: the run owns the coordinate, no later
enumeration re-places it, and a tag would have the next sweep delete the
run's own pose. `Run.bind` (`solid_node/simulation/run.py:348`) does this for
the whole bank on every tick, and `Sim.__init__` does it once at
construction — including the `Sim` a `ScenarioTest` builds over the very node
the runner handed it (`ScenarioTest.scenario_node`,
`solid_node/simulation/scenario.py:62`).

So a running root's leaves carry UNTAGGED motion operations that only
`Joint.clear`'s recorded identities can remove, and the runner replaces the
list those identities point into. `evidence.md` measures each step; the two
faces are:

- **Lost.** The restore reinstates the BUILD's operation, which IS tagged;
  the next `set_keyframe` sweeps it and nothing re-places, so the leaf stands
  at rest while its coordinate reads the run's value (`evidence.md` §7:
  `slide.travel=8.0, placed=0.0`).
- **Doubled.** When the checkpoint was taken while an untagged run placement
  stood, the restore puts that operation back while `_joint_motion` already
  points at the one that replaced it; the next `place` clears nothing and
  inserts beside it (`evidence.md` §1 and §3: two translations, 12.0 and
  0.0, for one coordinate reading 0.0; a `Free` goes from four operations to
  eight). This is the lock's reported symptom.

A sub-assembly's children are untouched because the runner checkpoints only
`node.children`, the root's own (`evidence.md` §2, `arm.slide`). An untimed
root is untouched as long as every binding happens inside a simulate phase —
but `evidence.md` §6 shows it is NOT immune: a test that binds a joint
coordinate BY HAND on an untimed tree places outside any phase too, and the
same restore strands it permanently.

**The fourth mechanism: `clear_solved`.** `clear_solved`
(`couplings.py:1786`, run from `assembly.py:101` at the START of an
assembly's simulate phase, right after `_sweep`) drops the VALUE and the
BINDER of every coordinate that assembly bound in its previous phase — and
nothing else. Its requirement, "An author-bound joint is cleared with its
motion" (`openspec/specs/joints/spec.md:1436`), states that the value and
the motion are halves of one binding and are dropped together; in the code
only the value half is done here, and the motion half is delegated to the
`_sweep` that runs a line earlier. That delegation is sound for a placement
the enumeration made, which is tagged. It is unsound for an UNTAGGED one,
and revision 1's Finding A is exactly that hole: a placement made outside a
phase survives the sweep, and `clear_solved` drops the value that justified
it, so the body stands at a pose no coordinate states. `evidence.md` §6's
last line shows it today; `evidence.md` §A2 shows the restore of decisions 2
and 3 producing one on an UNTIMED tree, which is why decision 5 below is
part of this change and not a follow-up.

## Goals / Non-Goals

**Goals**

- A child the runner restores stands at the coordinates it holds, on every
  instant and every test.
- A joint that is placed again or cleared leaves nothing of its previous
  placement behind, however the list was replaced in between.
- A joint's motion does not outlive its coordinate's value: a body never
  stands at a pose no coordinate states.
- The runner's existing guarantee is kept: a leaked operation, inserted
  anywhere, is still reverted.
- No change to the geometry an untimed project's tests report, to the
  runner's output, or to a node that declares no joint.

**Non-Goals**

- Making the checkpoint restore revert COORDINATE values. The bank belongs to
  the run (`run-owns-the-coordinates`); a `Sim` rebinds it wholesale at
  construction and a scenario's point is to leave the machine where it drove
  it. The runner never owned those values and this change does not give it
  them.
- Changing when a run binds, or tagging the run's placements so the sweep
  reaches them (see Decisions).
- Giving the RUNNER anything to do about sub-assembly children, which it
  does not checkpoint. Decision 5 is not the runner's and does reach them,
  as it reaches every coordinate any assembly binds — but it only removes a
  placement whose value is being dropped in the same moment, so a
  sub-assembly's child ends each enumeration exactly where it ended it
  before.

## Decisions

### 1. `Joint.clear` drops by the joint's own mark, not by remembered objects

`clear(node)` removes every operation of `node.operations` that is motion and
whose `_joint_slot` equals this joint's slot in `declared_joints(type(node))`
— the mark `apply_joint_motion` already stamps. `_joint_motion` is written by
`place` and read by `clear` alone (nothing else in the framework reads it):
the implementation may keep it as the record of what this joint last applied,
but it stops being the handle the removal depends on.

Why the slot is the right mark: it is stamped by the one seam that places a
joint, it is stable across a list replacement because it lives on the
operation, and within one node it identifies exactly one joint —
`declared_joints` is that node's class's own ordered mapping. A many-operation
placement (`Free`'s four, an off-origin `Revolute`'s three, an `Orbit`'s one)
carries one slot across the whole run, so it is dropped as a unit
(`evidence.md` §3 shows all four of a `Free`'s operations carrying slot 0).

*Alternative rejected — a new `operation._joint` attribute pointing at the
joint instance.* It adds a second mark where one already exists, and the
joint instance is a CLASS attribute shared by every instance of that class,
so it identifies the joint no more precisely than the slot does while making
every operation hold a reference to a descriptor.

*Alternative rejected — re-find the operation by INDEX.* The list can be
replaced wholesale and a test may insert anywhere; an index is not identity.
This is the assumption the current bug rests on.

### 2. One seam re-places every declared joint of a node from what it holds

A module-level function in `solid_node/motion/joints.py` takes a node and,
for each joint `declared_joints(type(node))` reports: reads the values its
coordinates hold through `get_coordinate`, clears the joint when any of them
is unbound, and places it otherwise. That is exactly the loop
`CoordinateDelivery.restore` (`assembly.py:317`) writes by hand today; that
call site moves onto the seam so the framework states the rule once.

*Alternative rejected — leaving the loop duplicated in the runner.* The
runner would have to reach for `declared_joints`, `get_coordinate` and the
`Free` arity rule, which is the joint capability's knowledge, not the test
runner's.

### 3. The runner re-places after restoring, and only then

`restore_children_checkpoints` keeps its content restore unchanged and then
calls the seam for each child it restored. Order matters: the content restore
is what reverts a leaked operation, and the re-place is what makes the
result consistent with the coordinates. A child whose class declares no joint
takes no extra work beyond one empty `declared_joints` lookup, so a
driverless, jointless project's run is what it was.

**Only `node.children`, never the node under test itself.** The seam is
called for exactly the children `save_children_checkpoints` snapshotted
(`test.py:385`, `self._children_operations`) and for nothing else. A joint
declared on the ROOT under test is outside the defect — the runner never
replaces the root's own operation list, so no placement of it can be
stranded — and it is outside this fix: re-placing it would be the runner
writing operations onto a node it never checkpointed, which is a new
behaviour with no measured need. The spec text says `children`, not
"the node", for this reason.

*Alternative rejected — restoring `_joint_motion` alongside the list
(the wart's first candidate).* It cures the DOUBLING only: the record would
point back at the restored objects, so the next `place` would clear them. It
does not cure the LOSS, because the restored operation is the build's tagged
one and the next enumeration's sweep removes it while nothing re-places
(`evidence.md` §7). It also puts a private per-node dict into the runner's
snapshot, which is joint bookkeeping the runner has no business holding.

*Alternative rejected — checkpointing THROUGH the joint's `clear`/`place`
at save time (the wart's second candidate).* Saving through `clear` would
have to undo the pose the run had made before the test, which the runner
must not do; and it would still leave `place` unable to remove an operation
a later restore reinstated. Decision 1 is needed either way, and with it the
save side needs no joint knowledge at all.

*Alternative rejected — tagging the run's placements with the root assembly
so `_sweep` reaches them.* The next enumeration's sweep would then DELETE the
run's own pose, because under a running root nothing re-places a run-owned
coordinate: the loss face would become every render's behaviour, not only a
restored one. The run binds outside the enumeration on purpose
(`assembly.py:255`, `run.py:348`).

*Alternative rejected — having the runner snapshot and restore coordinate
values as well.* See Non-Goals: the bank is the run's.

### 4. Three modules change, and no two of them are enough

Measured: with decision 1 alone, a restored child keeps its stale placement
swept away and never gets a new one (the loss face survives). With decision 3
alone, the re-place calls `place`, whose `clear` still removes only the
recorded objects, so it inserts a second placement beside the reinstated one
(the doubling face survives). With 1 and 3 but not 5, an untimed guarded
binding strands the re-placed operation for the instant that leaves it
unbound (`evidence.md` §A2). The joint owns what its placement is and how to
remove it; the runner owns when a checkpoint is restored; the solver owns
when a binding stops being in force.

### 5. `clear_solved` drops a coordinate's PLACEMENT with its value

The requirement "An author-bound joint is cleared with its motion" says the
value and the motion are halves of one binding, dropped together. Make that
literal: for every coordinate whose value `clear_solved` drops, it also
clears — by slot, under decision 1 — the joint that owns that coordinate, so
no operation of that binding survives the value that stated it.

The records `clear_solved` already walks are SLOTS, and a slot carries
`.node` (the node owning the coordinate, which may be a leaf several levels
under the assembly that solved it) and `.name` (the key under which
`joint.coordinates` reports it, `pose.roll` included) — measured in
`evidence.md` §A3. So the clear needs nothing new recorded: `declared_joints
(type(slot.node))`, the joint whose `coordinates` holds `slot.name`,
`joint.clear(slot.node)`. The two exemptions `clear_solved` already makes
are untouched and both matter here: a slot some OTHER assembly already
re-bound in the current enumeration (`_enum_marker`) is skipped, and a slot
the RUN owns (`run_owned`) is skipped — which is what keeps a running root's
placements, the ones this whole change exists to preserve, out of reach of
the new clear (`evidence.md` §A6).

**Why this is in the change and not a follow-up.** Without it, decisions 2
and 3 introduce a regression revision 1 predicted and `evidence.md` §A
measures. Under an UNTIMED root the seam re-places from the value the last
enumeration bound, and that re-placed operation is UNTAGGED — no phase is
current during a restore. If the NEXT enumeration does not re-bind that
joint — an author's `simulate()` binding it under a guard, which ADR-099's
clear semantics explicitly allow ("SHALL find the coordinate unbound on
every run") — then `_sweep` cannot reach the untagged operation, `clear_solved`
drops the value, nothing calls `joint.clear`, and the body stands at the
previous instant's pose instead of at rest. `evidence.md` §A1 shows that
case GREEN today (`travel=None, motion=[]` at the second instant) and §A2
shows it RED under decisions 1-3 alone (`travel=None, motion=[untagged
10.0]`). §A4 shows this decision restoring it to `travel=None, motion=[]`.

This decision also settles open question 2 of the first draft: the
permanently stranded operation an untimed HAND binding leaves behind
(`evidence.md` §6's last line, 7.0 + 0.0 for a coordinate reading 0.0) is
removed at the next enumeration, because the slot it stranded is one the
enumeration had bound and so one `clear_solved` walks (`evidence.md` §A5).
A coordinate NO phase ever bound is still never cleared — the requirement's
"A joint bound outside a phase keeps its value" is unchanged, because such a
slot was never recorded on any phase and `clear_solved` never sees it.

*Alternative rejected — revision 1's direction (i): have the restore
re-place ONLY the bindings the next enumeration will not re-place, and clear
the rest.* Measured, the discriminator it needs does not exist.
`evidence.md` §A3 is the whole table:

| binding path | `slot.binder` | `slot._bound_by` | `run_owned` |
| --- | --- | --- | --- |
| the author's own `simulate()` assignment | `None` | the assembly whose phase ran | `False` |
| a relation (`push.drives(slide.travel)`) | `RelationRecord` | the assembly | `False` |
| a derived formula driving a joint | `RelationRecord` (of the formula's own relation) | the assembly | `False` |
| a wiring into a leaf's joint coordinate | `Wiring` | the assembly | `False` |
| a hand assignment outside any phase | `None` | STALE: whatever a previous phase left | `False` |
| a running simulation (`CoordinateDelivery`) | `RunBinder` | stale leftover | `True` |
| a document publication (`CoordinateDelivery`) | `RunBinder` | stale leftover | `True` |
| a slot nothing ever bound | `None` | stale leftover | `False` |

Two rows kill (i). `binder` is `None` for BOTH the author's own `simulate()`
assignment and a hand assignment, so it cannot tell "the enumeration will
re-place this" from "nothing will" — and the author's guarded `simulate()`
binding is precisely the case Finding A is about, so (i) would have to guess
on it. And `_bound_by` is never cleared by anything (`clear_solved` resets
`_value` and `binder` only; `note_bound` only ever sets it), so it is a
sticky leftover, not the `None` that sketch assumed: measured
`Conditional` even on a slot no phase has ever bound. The one live
discriminator is `_enum_marker`, which `bind` stamps on every binding and
which is `None` exactly when nothing was enumerating — but that is
`clear_solved`'s own freshness bookkeeping, documented for one purpose, and
making the test runner's restore branch on it would couple the runner to the
solver's internals to reach a narrower result. (i) also leaves the ghost
reachable outside the runner entirely: `evidence.md` §6's permanent stranded
operation happens in a plain `set_keyframe`/render sequence with no test
runner in it, and (i) does nothing for it.

*Alternative rejected — clearing the joint in `_sweep` instead.* `_sweep`
runs before the phase and removes by ANIMATOR identity; it has no
coordinate in hand and no way to know which value is about to be dropped.
The value's drop is what licenses the motion's drop, so the two belong in
the same place.

### 6. What an untimed root sees, stated by binding kind

The claim is about GEOMETRY, not about which operation object carries it.

- A joint whose coordinates an ENUMERATION bound (a relation, a wiring, a
  derived formula, the author's own `simulate()`): at the restore the seam
  re-places it from the value it holds — the value that same enumeration
  bound, so the same geometry, in a new UNTAGGED operation at the same slot.
  At the next render, `clear_solved` (decision 5) removes that operation as
  it drops the value, and the enumeration binds and places afresh, tagged.
  Every test therefore measures the placement its own instant's enumeration
  produced, which is what it measured before this change.
- A joint the next enumeration does NOT re-bind (a guarded `simulate()`, a
  joint left at rest for this instant): the restore re-places it, and
  decision 5 clears it at the next render. The body is at rest for that
  instant, which is what it was before this change (`evidence.md` §A1
  against §A4).
- A joint bound BY HAND outside any phase, on a coordinate some phase had
  bound earlier: the restore re-places it from the hand value instead of
  stranding a second copy of it, and the next enumeration clears and rebinds
  it. This is a CHANGE, and it is the defect of `evidence.md` §6 being
  fixed: today that tree carries 14 mm of travel for a coordinate reading
  7.0, then 7.0 + 0.0 for a coordinate reading 0.0, for good.
- A joint on a node NO phase ever bound and the runner never checkpointed
  (a node a test constructed itself, a sub-assembly's child): untouched by
  every part of this change.

Pinned by the task list with an untimed fixture run through several tests, a
guarded-binding fixture across two instants, and by the existing suites —
`tests/test_joints.py`, `tests/test_couplings.py`, `tests/test_manager_test.py`,
`tests/test_running_simulation.py`, `tests/test_motion_package.py`,
`tests/test_kinematics.py`, `tests/test_mechanisms.py`,
`tests/test_running_stops.py`, `tests/test_running_jumps.py`,
`tests/test_running_document.py`, `tests/test_declarative_nodes.py`,
`tests/test_declarative_render.py`, `tests/test_animator_tag.py` and
`tests/test_controls.py` — which were run UNCHANGED against a probe applying
all of decisions 1, 2, 3 and 5 at their seams: 846 passed, 994 subtests
passed, 0 failed (`evidence.md`, Revision 1 §A7).

## Risks / Trade-offs

- **A re-place on every restore costs work proportional to the root's
  children times their declared joints** → it is one `declared_joints` lookup
  per child and one placement per bound joint, for root children only, twice
  per instant; the measured bench runs 8 tests in 0.09 s before the change.
  If a project ever shows this, the seam can skip a joint whose coordinates
  and placement already agree.
- **The restore now WRITES to a child that leaked nothing** → the write is
  the joint's own placement, replaced by an identical one; the risk is that a
  project depended on the exact operation OBJECTS surviving a test boundary.
  Nothing in the framework does — `_sweep` and `clear` both exist precisely
  because object identity is not dependable here.
- **A test that deliberately hand-places a joint's operations and then
  expects the runner to leave them** would now have them replaced from the
  coordinate → this is the defect being fixed, stated from the other side: a
  placement that contradicts its coordinate is what the change forbids.
- **`_joint_slot` is currently stamped only by `apply_joint_motion`** → if a
  future placement path bypasses that seam its operations would not be
  cleared. The implementation adds a test that every joint kind's placement
  carries its slot.
- **Decision 5 runs on EVERY render of every project, not only under the
  test runner** → it is one `declared_joints` lookup per slot `clear_solved`
  already walks, plus a list filter only for the slots that own a joint. It
  is also the one decision here that changes behaviour outside `solid test`,
  so it carries the widest blast radius of the four; the measured control is
  the fourteen existing suites run unchanged against it (design decision 6 below).
  If a project ever shows the cost, the clear can be skipped for a joint
  whose operations are all tagged, which the sweep has already removed.
- **Decision 5 clears the joint of a coordinate a LATER-running assembly is
  about to bind in the same enumeration** → it cannot: `clear_solved` skips
  a slot whose `_enum_marker` is the current enumeration, which is the
  existing guard for exactly that case, and the joint clear sits inside it.

## Migration Plan

None. No project source changes, no stored artifact changes, no CLI surface.
The lock may drop the private lock its tests build (`lock_under_test()` in
`simulation/test_lock.py`) once this is integrated; that is the originating
project's own validation step, outside this change.

## Open Questions

1. *(Settled in revision 1 — see decision 3.)* A joint declared on the ROOT
   under test is not checkpointed and is not re-placed. Stated in the spec
   text as `children`.
2. *(Settled in revision 1 — see decision 5.)* The permanently stranded
   operation an untimed HAND binding leaves behind is removed at the next
   enumeration, because `clear_solved` now drops a coordinate's placement
   with its value.
3. **Is the wart's own reproduction, which reports FIVE operations on the
   lock's `d1`, still reachable?** Re-run verbatim on this worktree it
   reports four (`evidence.md` §8): the lock's own tests now build a private
   lock, so nothing binds the runner's tree outside the enumeration during
   that sequence. The defect is reproduced instead by the sequences in
   `evidence.md` §1, §3 and §7, which include the doubling the wart describes.
