# ADR-147: A Mate Compiles at Realization to a Rest Placement, a Joint and a Coordinate

**Status:** Accepted
**Date:** 2026-09-26
**Amended by:** [ADR-148: A Mate's Freedom May State Its Own Line](ADR-148-a-mates-freedom-may-state-its-own-line.md) — the freedom may state `axis` and `at` in numbers, read in the moving child's own frame, each defaulting to the moving frame's; the frames still fix the rest placement and the zero
**Amended by:** [ADR-150: A Mate's Freedom May Be a Function of the Assembly That States It](ADR-150-a-mates-freedom-may-be-a-function-of-the-assembly-that-states-it.md) — the freedom's range may be one function of the assembly that states the mate, called once as the assembly realizes the moving child and its result resolved against the child as a written range is
**Extends:** [ADR-061](ADR-061-a-call-in-a-class-body-is-a-declaration.md) (a frame read off a child declaration is a place), [ADR-066](ADR-066-render-at-rest-simulate-per-instant.md) (the rest render places mated children after the author's `render()`), [ADR-088](ADR-088-a-joint-owns-one-coordinate.md) (the frame follows the joint argument rule; the mate's coordinate reaches the child through a wiring), [ADR-089](ADR-089-drives-relates-two-coordinates.md) (a mate is a class-body statement recorded through the relations channel), [ADR-093](ADR-093-joints-of-one-class-compose-in-declaration-order.md) (the installed joint's slot), [ADR-097](ADR-097-a-joint-is-stated-in-the-frame-of-whoever-declares-it.md) (the moving frame is already in the child's own frame), [ADR-098](ADR-098-a-joint-may-be-declared-where-a-child-is-placed.md) (installation by specialization), [ADR-114](ADR-114-a-joints-placement-is-identified-by-its-slot-not-by-what-bound-it.md) (the slot mark that keeps a re-run from stacking), [ADR-120](ADR-120-a-marking-is-a-declaration-that-produces-an-artifact-and-no-solid.md) (the declaration mould, extended to assemblies)
**OpenSpec change:** `place-parts-by-mate`
**Ratified:** 26 September 2026, by the orchestrator's adversarial review under the review gate the pilot delegated on 7 September 2026, with the proposal's three scope questions at their recommendations: `Revolute` only, the rigid mate deferred, the originating project's whole root chain as validation.

## Context

A joint whose line does not pass through the moving part's own origin
was stated twice: once as the rest placement the parent's `render()`
computes by hand, and once as the joint the child's class restates in
its own frame (ADR-097) or the parent restates at the declaration site
(ADR-098), the two kept in agreement by constants shared between files.
The originating project, a six-axis robot arm reconstructed from an
assembly CAD design, repeats that shape at each of the five links of its
root chain. The design it is built from states each link once, as a
connector on each part and how the two meet; a spike re-derived 142 of
the project's 145 transcribed placements from those connectors under one
rule and reproduced the elbow's and the shoulder's hand-written
placements and the elbow's hand-written joint from two frames each.

## Decision

**A frame is a fifth class-body declaration, in the marking mould.**
`Frame(at=(0, 0, 0), z=(0, 0, 1), x=None)` in `machinome.node.frames`,
also resolving from `machinome.node`: an origin and a right-handed triad
in the declarer's own rest frame. Recognized duck-typed on `frame_kind`
in `NodeMeta.__new__`, enumerated by `declared_frames(cls)` off the MRO
(a plain mixin contributes, `None` drops one), refused at class creation
on a name that clashes with a parameter, a child, a joint, a port, a
marking or a mate, or that would shadow an attribute every node carries.
Not a `Declaration` and not a descriptor, so it is never identity and
never keys an artifact. Allowed on ANY node kind, an assembly included —
the one departure from ADR-120 — because an assembly's frames are its
connectors to the assembly above it. Each argument follows the joint
argument rule, lifted out of `Joint._vector` into `resolved_vector` and
shared; a frame resolves per instance right after the declarer's joints,
so one that cannot resolve refuses its declarer whether or not a mate
names it. `z` is normalized and `x` squared up against it; an omitted
`x` is the next principal axis for a PRINCIPAL `z` only, and any other
`z` must state `x`, because `x` fixes the zero of a revolute mate and a
derived one would be invisible. No frame is symbolic.

**A mate is a statement in an assembly's class body.**
`elbow = forearm.hinge.on(elbow_pin, Revolute(range=(-135, 135)))`: the
frame that speaks MOVES. Reading a frame off a child declaration yields a
`FrameRef`, a place like a path reference, which refuses `drives`,
arithmetic and further reads by name. `on()` records a `Mate` through the
declaring-namespace channel relations use; every refusal is made when the
class is created, where the mate's name is known. A `Mate` is a
`Coordinate` owning one `RotationalPort` and is deliberately NOT a
`Joint`, so it is never enumerated, resolved or cleared as a joint of the
assembly. Mates are processed in `NodeMeta.__new__` before the class's
constraints and relations are checked, and `OwnRef.check_declared_on`
admits a declared mate.

**The ends are depth one, and the fixed end does not move.** The moving
end is a frame of a child this class body declares; the fixed end is the
assembly's own frame, written by its bare name, or a frame of another
declared child whose class declares no joint — its own, a site's or a
mate's. A grandchild's rest placement is its own parent's, decided after
this assembly's, and a sibling does not carry another sibling, so a
moving child placed against a fixed child's rest placement would not
follow that child's joint. With revolute freedoms only, no mate's fixed
end sits on a child another mate places: the dependency order is the
declaration order and a cycle cannot be written. A second mate on one
child is refused as a loop; list-held and repeated children are refused
at either end; a subclass's own mate on a child an ancestor declares is
refused, because installing it would change a declaration the ancestor
shares.

**The freedom is a fresh `Revolute` with neither axis nor anchor.**
`Revolute`'s `axis` becomes optional for this one use and is refused
anywhere else at class definition, naming the mate as the only place it
may be left out. `at` left out is a sentinel object, so an explicit
`at=(0, 0, 0)` is refused too. The freedom's range is numbers, `None` or
functions of the coordinate's own value; a parameter token, a
whole-range callable or a `Bound` with reads is refused, because the
installed joint resolves its range against the CHILD. `Prismatic`,
`Orbit`, `Free` and no freedom at all (the rigid mate) are refused naming
this version's scope.

**What a mate compiles to, at realization, and nothing else:**

1. **A rest placement.** After the author's `render()` returns and its
   phase is popped, `_rest` calls `apply_mates`, which places each moving
   child at `P_owner · F_fixed · F_moving⁻¹` — `P_owner` the identity for
   the assembly's own frame, else the fixed child's non-motion
   operations composed through each operation's `matrix()`, refused by
   name when one does not evaluate to a number — as one `Rotation`
   (omitted at the identity) then one `Translation` (omitted at zero),
   appended untagged, so they compose outside the child's joint block
   exactly as a hand-written rest placement does. The angle comes from
   `atan2`, the axis from the antisymmetric part up to 90 degrees and
   from the diagonal beyond it; axis components and the angle are
   snapped to a whole number within `1e-9`, the translation is not. Each
   operation carries `_mate_slot`; a legacy render's re-run drops and
   re-applies by that mark and never stacks. An operation the render's
   own phase applied to a mated child refuses the render, naming the
   assembly, the child and the mate.
2. **A joint of the child's class.** At class creation the moving child
   declaration's class is replaced by `_specialize(node_class,
   {mate: Revolute(axis=frame.z, at=frame.at, range=..., unit=...)})`
   with the frame's DECLARED arguments copied literally, so the joint
   resolves against the child like any class-declared joint, nothing
   carried or inverted, and takes the slot after every joint the child
   declares. The child keeps its name, identity and artifacts; a mate
   name the child already answers to is refused naming what it declares.
3. **A coordinate of the assembly** under the mate's name, reported by
   `declared_ports`, an end of relations and derived coordinates and a
   wiring source like any coordinate the assembly owns. It reaches the
   child's joint through the mate added to the child declaration's
   wiring (ADR-088): one binder, one address. The mate's wiring carries
   `rests_unbound`, so an unbound mate coordinate leaves the child's
   joint unbound and resting — as an unbound joint rests — instead of
   being refused as an author's wiring is; `clear_solved` drops a
   previous binding with its motion. Binding the installed joint by
   hand or by a relation is refused naming the mate's coordinate by path
   (`Bind arm.elbow instead`); reading it as a source is allowed.

**Nothing is published that is not already publishable.** The rest
placement is operations and the coordinate a binding; frames and mates
are not serialized, no field is added and no document version moves. A
machine that declares no frame or mate takes no new path and publishes
the bytes it published before.

## Rejected alternatives

- **A frame as a `Declaration`** would enter identity; a connector
  changes no geometry. **As a descriptor returning resolved numbers**:
  nothing reads a frame on an instance in this version.
- **Applying the placement at child realization**, before `render()`:
  the hand-placement refusal would then have to infer after the fact
  which operations the render added; after the render, the phase's own
  `applied` list says exactly.
- **Aliasing the assembly's coordinate to the child's slot** (one slot,
  two names) needs no unbound exemption but gives one value two
  addresses in every qualified-id enumeration, the bindings table and
  the serializer's symbolic pass — the hazard the driver-sideways rule
  exists to prevent.
- **Ends by path and a fixed end on any child** (the working note's
  first reading): refused until a named project needs the carry a deeper
  end requires, and until the rigid mate brings a dependency order that
  can place a fixed child first.
- **Deriving `x` for any `z` by `Wrapped`'s general rule**: that zero is
  unreadable from the declaration.

## Consequences

- The originating project can state each root-chain link once — a frame
  on each side and one `on()` sentence — deleting its hand placements,
  the joints they restated and the constants that kept them in step; its
  migration, in its own repository, is compared pose for pose at maximum
  deviation 0.
- `type(child) is C` stops holding for a mated child, as for a
  site-jointed one (ADR-098); `isinstance` holds.
- A second binding rule sits beside the `ports` capability's refusal of
  an unbound wiring source, scoped by a flag only a mate sets.
- A mated machine's bindings table carries both the assembly's port and
  the child's wired joint, as for any wiring.
- Deferred, each needing its own evidence: the rigid mate (which brings
  the dependency order and a loop refusal among sibling mates back),
  `Prismatic` and `Free` freedoms, repeated frames and broadcast mates,
  ends deeper than one child, publishing frames and mates for the
  viewer, and a mate coordinate's range for consumers that read one.
