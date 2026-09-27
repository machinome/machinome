# ADR-152: A Mate May Leave Its Freedom Out

**Status:** Accepted
**Date:** 2026-09-27
**Amends:** [ADR-147](ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md) ("A mate compiles at realization to a rest placement, a joint and a coordinate"; "A `Mate` is a `Coordinate` owning one `RotationalPort`"; "no freedom at all (the rigid mate) [is] refused naming this version's scope"; the deferral of the rigid mate in its Consequences), [ADR-151](ADR-151-a-mates-freedom-may-be-a-prismatic.md) ("`Orbit`, `Free` and the rigid mate stay refused")
**Cites:** [ADR-098](ADR-098-a-joint-may-be-declared-where-a-child-is-placed.md) (the specialization a rigid mate does not make), [ADR-088](ADR-088-a-joint-owns-one-coordinate.md) (the wiring a rigid mate does not add)
**OpenSpec change:** `hold-by-mate`
**Ratified:** 27 September 2026, by the orchestrator's review under the review gate the pilot delegated on 7 September 2026, with the proposal's four scope questions at their recommendations: the freedom left out and no `Rigid` class; every mate named; a rigid mate read on an instance as its declaration, and assigning to it, naming it as a relation's end or as a wiring source refused naming the mate; a new ADR amending ADR-147 and ADR-151.

## Context

The originating project is a quadruped reconstructed from its MuJoCo
file and its print plate. Its printed chain migrates onto revolute mates
as another robot's had; its 48 bought parts -- servos bolted by their
ears, horns seated in horn holes, the servos' screws and nuts -- do not
move of their own. Each sits connector onto connector on the part that
holds it, at a seat the project measured off the print. ADR-147 refused
a mate with no freedom, because the project that asked for mates needed
only revolutes, and ADR-151 kept it refused, so the bought parts lived
in a parallel tree of hand placements, tied to the printed tree by eight
relations and one wrapper class that existed only to order a quarter
turn before a joint angle.

A mate's rest placement never read its freedom: `apply_mates` composes
`P_owner · F_fixed · F_moving⁻¹` from the two resolved frames and, for a
fixed child, its rest operations. A probe reproduced the project's hand
placement of a knee servo within `3e-16` from two frames under a
revolute mate. Everything else a mate compiles to -- the joint, the
specialization, the wiring and the coordinate -- is keyed on the
freedom, and a part that is held needs none of it.

## Decision

**A mate may leave its freedom out: the rigid mate.**
`bolted = servo.ears.on(servo_seat)` -- the default `on()` already had
-- places the moving child at rest exactly as any mate does, from the
same two frames, by the same composition, as one rotation then one
translation after the author's `render()`, with the same `1e-9` snap, the
same slot mark and the same refusal of a `render()` that also places the
child. It compiles to nothing else: `_install` returns before building a
joint, so the child's declaration is not specialized (`type(child)` is
the declared class, stronger than ADR-098's `isinstance`), it gets no
wiring, `ChildDeclaration.realize` takes none of the mate paths, and
`mate.joint` stays `None`. `on(fixed, None)` is the same statement.

**A rigid mate is not a coordinate.** `Mate.__init__` builds none for
it -- `coordinate` is `None` and `coordinates` empty -- so
`declared_ports` reports nothing and every consumer that enumerates
ports, qualified ids, bindings and the serializer included, sees nothing
new. Reading it on an instance yields the mate itself, as reading a
frame yields the frame; assigning to it raises `AttributeError` naming
the class and the mate. Named where a coordinate is named -- a
relation's end or a term of a derived coordinate in the body that states
it (`coordinate_ref`), a path from above (`read_through` passes it as a
place and `coordinate_ref` refuses it), or a wiring handed to a child
(`ChildDeclaration.__init__`) -- it is refused by one message worded
once in `mates.py`, naming the mate and saying it owns no coordinate.

**Every mate is named.** A bare rigid mate is refused at class creation,
for its own reason: `declared_mates` reports a mate under its name and
every refusal names it by that name. A bare mate with a freedom keeps
its message.

**The fixed end stays still.** A fixed end is the assembly's own frame
or a frame of a child that no mate places and whose class declares no
joint; a rigid mate enters the placed set like any other. A fixed end on
a child a rigid mate places is refused naming that mate and saying this
version orders no mate before another, since `apply_mates` places a
class's mates in declaration order and nothing orders the fixed child's
first. A held part rides with the part that holds it because it is
declared in that part's class, and a held child may itself declare
joints, children and mates, all composed inside the rest placement. A
rigid mate on a child a base class declares stays refused, its reason
reworded (the mate is stated in the class that declares the child it
moves); the check that a mate's name is free on the moving child's class
is skipped for a rigid mate, which gives the child nothing under that
name. A second mate on a held child is refused as a loop, whichever are
rigid.

**Messages.** The refusal of a freedom that is neither a `Revolute` nor
a `Prismatic` names the three accepted forms, the third being none at
all for a part that is held. Every refusal of a mate with a freedom is
unchanged.

**Unchanged:** every mate with a freedom, in objects, messages and
bytes; the document, which carries a rigid mate's placement as the held
child's ordinary operations and no binding, at the version the same
machine without mates declares; the viewer.

## Rejected alternatives

- **A `Rigid()` freedom class.** A joint-like object that installs no
  joint, owns no coordinate and takes no argument the originating
  project would write: a class for symmetry with `Revolute` and
  `Prismatic`, which is not evidence. The working note's spelling --
  rigid is the default, the freedom the addition -- needed none.
- **Refusing an explicit `None`.** Telling it from the default needs a
  sentinel and a refusal for a spelling nobody writes.
- **A bare rigid mate.** `declared_mates` would need a second kind of
  key, every refusal a second way to name the mate, and the documented
  `name` read would be `None`, to save a word per statement.
- **A coordinate that is never wired**, a rigid mate keeping a port
  bound to nothing: reported by `declared_ports`, carried in the
  bindings table, offered as a relation end that moves nothing, and a
  driver aimed at it would silently do nothing.
- **Letting the missing coordinate fail where it is read:** a
  `'NoneType' object has no attribute` names nothing, and a plain "has
  no attribute" would be false.

## Consequences

- A bought part is held at its seat by one statement in the class of
  the part that holds it; the originating project deletes its parallel
  tree, its eight relations and its ordering wrapper in its own
  repository's follow-up, compared pose for pose at maximum deviation 0.
- A held part's operations may take another form than a hand
  placement's with the same placement: one rotation where a hand writes
  two, no rotation where a hand writes an identity one, `'180'` where a
  hand writes `'180.0'`. A comparison against a hand-placed twin
  compares composed placements, not documents.
- A fastener on a moving part is declared in that part's class; a fixed
  end on a moving sibling is not needed for it, and stays refused.
- Still deferred, each needing its own evidence: a fixed end on a
  sibling another mate places, and the dependency order and cycle
  refusal it would bring; a rigid mate on an inherited child; `Orbit`
  and `Free` freedoms; loops; ends deeper than one child; world-placement
  reads.
