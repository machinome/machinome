## Context

Every placement in machinome is a coordinate written in a parent's
`render()`, and every joint is a coordinate written again in the child's
class body (ADR-097: in the child's own rest frame) or at its declaration
site (ADR-098: in the parent's frame). For a joint whose line does not
pass through the child's origin, the two statements have to agree
through arithmetic the author does by hand. Thor's root chain is five of
these (`proposal.md`, Why), and the design Thor is built from already
states each link as a connector on each side plus an offset.

The working note `workflow/ongoing/mates-and-sketches.md` §5.1–5.2
proposes the interface: named frames on parts; a mate relating two
frames that compiles to a rest placement, a joint and a coordinate.
The orchestrator placed that interface in the architecture
(`evidence/architecture.html`, four figures) and a spike checked the
arithmetic against Thor (`evidence/spike.md`). This design re-checks
every rule of that placement against the source and the ADRs and records
where the source wins.

Seams the change rides, all existing:

- `machinome/node/markings.py` — the mould for a class-body declaration
  that is neither a `Declaration` nor a descriptor, recognized
  duck-typed in `NodeMeta.__new__` and enumerated off the MRO
  (ADR-120).
- `machinome/node/declarative.py` — `_DeclaringNamespace` and
  `record_relation`, the channel a class-body statement is recorded
  through (ADR-089); `_specialize`, the class a site joint is realized
  as (ADR-098); `ChildDeclaration.wiring`, the parent-to-child
  coordinate hand-down (ADR-088).
- `machinome/motion/joints.py` — `Joint.resolve`/`_vector`, the argument
  rule; `declared_joints`, the slot order (ADR-093); `Joint.clear`, the
  slot mark (ADR-114).
- `machinome/motion/couplings.py` — `read_through`, `PathRef`,
  `OwnRef.check_declared_on`, `Wiring`.
- `machinome/node/assembly.py` — `_rest`, the once-only rest render
  (ADR-066).
- `machinome/node/base.py` — the constructor's
  `resolve_declared_joints(self)` call, the moment frames resolve.

## Goals / Non-Goals

**Goals:**

- Thor states each root-chain link once: a frame on each side and one
  `on()` sentence in the assembly, with no hand placement, no restated
  joint and no shared constants, at maximum pose deviation 0.
- A mate compiles to three things the framework already has and invents
  no fourth: rest operations, a joint of the child's class, a coordinate
  of the assembly.
- Every refusal names the mate or the frame at the line that wrote it,
  at class creation wherever the fact is known there.
- Nothing downstream changes: document, serializer, simulation package,
  viewer, mechanics.

**Non-Goals:**

- Loops, a second mate on one child, a solver (§5.3).
- Publishing frames or mates in the document or drawing them (§5.5).
- Repeated frames, broadcast mates, mates in list-held or repeated
  children.
- A moving frame on a grandchild; a fixed frame reached through more than
  one child; a fixed end on a child that can move.
- `Prismatic`, `Free`, `Orbit` and the rigid mate as freedoms (scope
  questions 1 and 2; `Orbit` never, per the note).
- Any claim about a mate's coordinate under a `Time.running()` root or a
  clocked root beyond what an ordinary wired coordinate already does
  there: no named project exercises it, and the tests do not assert it.
- Controls (ADR-112/117) naming a mate's coordinate: no named project
  does; not asserted.

## Decisions

### 1. The frame is a fifth class-body declaration, in the marking mould

`Frame(at=(0, 0, 0), z=(0, 0, 1), x=None)` in `machinome/node/frames.py`,
re-exported from `machinome.node`. A plain class attribute with
`frame_kind = 'frame'`; `NodeMeta.__new__` asks `_declares_frame(cls)`
duck-typed, exactly as `_declares_marking` does, and validates with a
local import so a class without frames pays one attribute scan.
`declared_frames(cls)` walks `reversed(cls.__mro__)`, `None` removes an
inherited entry, a plain mixin contributes. Clash refusals are the
marking's list plus a marking and a mate of the same class; the reserved
names are `machinome.parameters._RESERVED`, the marking's.

Departure from `Marking`, from the note and kept: a frame is allowed on
an `AssemblyNode`, because Thor's upper arm declares its own elbow frame
(`Art2.elbow_pin`) and every root-chain fixed end is an assembly's frame.

*Alternatives.* A `Declaration` (rejected: would enter identity, and a
connector changes no geometry). A descriptor returning resolved numbers
on an instance (rejected: nothing reads a frame on an instance in this
cycle; a marking is not one either, and the cheaper mould wins).

### 2. A frame resolves per instance, beside the joints, by the joint rule

Components are numbers, parameter tokens, formulas, or a callable of the
realized declarer for the whole argument — `Joint._vector`'s rule,
reused rather than restated. Frames are resolved in the node
constructor immediately after `resolve_declared_joints(self)` and cached
in the instance's `__dict__` (`_frame_arguments`), so a bad frame is
refused on the declarer at realization whether or not a mate uses it —
ADR-088's "earliest point a value could be wrong". A component that does
not resolve to a number is refused, as a joint's is.

**Deviation: no symbolic frame.** The placement said "a symbolic `at`
publishes as a symbolic translation; a symbolic axis is refused naming
the frame". In the source, a joint's arguments must resolve to numbers
at realization (`Joint._vector` refuses anything else), and a frame
follows the same rule, so nothing symbolic can reach the resolver.
Both sentences are struck; "a component that is not a number is
refused" replaces them.

**Deviation: the default `x` for a non-principal `z` is refused, not
derived.** The placement said `x` "follows the rule `Wrapped` uses for
`zero` … refused for a diagonal `z`". `Wrapped._zero_direction` in the
source derives a zero for EVERY axis except one parallel to `(1, 1, 1)`,
by projecting the cyclic shift of the axis. For a mate that derived
direction is the zero of the coordinate (spike correction 1), and for a
non-principal `z` it is a direction nobody can read off the source. So
the frame agrees with `Wrapped` on the six principal directions — where
`Wrapped` lands exactly on the next principal axis in right-hand order —
and refuses every other `z` without an `x`, naming `x` as the remedy.

### 3. `on()` is a statement recorded through the relations channel

`ChildDeclaration.__getattr__` and `read_through` learn one more kind of
place: a frame (`frame_kind`) read off a declared class yields a
`FrameRef(root, segments, frame)` from `machinome/motion/mates.py`, a
sibling of `PathRef` sharing its shape and its list-held/repeat checks.
A `FrameRef` is not a `CoordinateRef`: `drives`, arithmetic and further
attribute reads through it refuse by name. `FrameRef.on(fixed,
freedom=None)` builds a `Mate` and records it with
`record_mate`, a twin of `record_relation`, into a new
`__machinome_mates__` list in `_DeclaringNamespace`. A bare `Frame` of
the executing body is the fixed end written by name; `Frame.on` exists
only to refuse (the assembly's own frame cannot move within it).

`Mate` carries `_names_in_body = True`, so assigning it names it while
the body runs, as a relation is named. A mate with a freedom is a
`Coordinate` owning one `RotationalPort(unit=freedom.unit)` as
`coordinate` and `coordinates`, with `__get__`/`__set__` delegating to
that port's slot exactly as `Joint` does — which is what makes
`declared_ports` report it with no change there and `OwnRef`/`PathRef`
resolve it.

`NodeMeta.__new__` pops the mates list beside relations and, BEFORE the
relations are checked (a relation in the same body may name a mate),
refuses a non-assembly, checks both ends against the class, refuses the
cases listed in the spec, stores `cls._own_mates`/`cls._declared_mates`
(inherited through the MRO like constraints), and installs each mate on
its moving child declaration (decision 5). `OwnRef.check_declared_on`
admits a declared mate beside ports and joints.

**Deviation: ends are restricted to depth one.** The placement admitted
a moving end whose ROOT is a direct child and a fixed end "by path". In
the source, a grandchild's rest placement is decided by the child's own
`render()`, which runs in the child's phase, after the declaring
assembly's `_rest` has returned (`_run_phase` → `_rest`, then
`child.render()`). A deeper moving frame would need its axis and anchor
carried through that later placement into the child's frame — the carry
ADR-098 accepted for site joints — and a deeper fixed frame would need
the same placement early. Thor needs neither. Both are refused naming
the path and the reason.

**Deviation: a fixed end on a child that can move is refused.** The
placement admitted any child's frame as a fixed end and resolved mates
"fixed side first", refusing cycles. In the tree, the moving child and
the fixed child are SIBLINGS: the resolver can only use the fixed
child's REST placement, and when the fixed child later turns about its
own joint, the moving child — not its descendant — does not follow. The
note's own §5.2 example (`lid = cap.bottom.on(link.knee)` with `link`
revolute-mated) is exactly this and would leave the lid hanging at the
link's rest pose while the link swings. So a fixed end on a child whose
class declares any joint (class-declared, site-declared, or installed by
a mate) is refused at class creation, naming the reason. With revolute
freedoms only, this also means no mate's fixed end sits on a child
another mate places, so the dependency order among mates is trivially
the declaration order and a cycle cannot be written; the loop refusal
reduces to "a second mate on one child". Both return, and must be
designed, with the rigid mate (§9).

### 4. The compiled rest placement lands in `_rest`, after `render()`

In `_rest(assembly, render)`, after `render(assembly)` returns and the
phase is popped, `apply_mates(assembly)` (in `mates.py`, imported
locally) runs for each declared mate in declaration order:

    M = P_owner · F_fixed · F_moving⁻¹

with `P_owner` the identity for the assembly's own frame and, for a
child's frame, the child's rest placement — its non-motion operations
composed by premultiplication through each operation's `matrix()`, the
composition `Joint._carry` already does, refused by name if an operation
does not evaluate to a number. `F` is a resolved frame as a 4×4 with
columns `x, y, z, at`. `M` is decomposed into one `Rotation(angle, axis)`
and one `Translation(t)`; the rotation is omitted when it is the
identity and the translation when it is zero. Axis components are
snapped with `joints._snapped` and the angle is snapped to a whole
degree within `1e-9` — needed, not cosmetic: the spike's default-`x`
elbow came back as `120.00000000000001` degrees and the shoulder's
180-degree axis as `(0, 0.7071067811865476, 0.7071067811865475)`. The
translation is not rounded (ADR-097: the framework does not edit the
arithmetic). For Thor's principal-axis frames every entry is an exact
`0`/`±1` and the translation is exact.

The operations are appended to the moving child's `operations`, carry
the mate's slot mark (`_mate_slot`, the mate's index in
`declared_mates`), and are untagged, so `_sweep` leaves them alone and
they compose OUTSIDE the child's joint block — exactly where a
hand-written rest placement sits (ADR-066, ADR-093).

- **Hand placement refused.** Before applying, any operation this
  assembly's render phase applied to the moving child (the phase's own
  `applied` list, which `_rest` already walks to untag) refuses the
  render, naming the assembly, the child and the mate.
- **Legacy render.** A render that read a driver re-runs under every
  binding (`_legacy_render`); `apply_mates` first drops every operation
  carrying a `_mate_slot` of that mate, then applies — ADR-114's
  slot-mark rule, so re-running never stacks.

*Alternative rejected:* applying the placement at `realize_children`
time, before `render()`. The rest placement would then precede the
author's operations on other children (harmless) but the hand-placement
refusal would need to inspect the child after the fact without knowing
which operations the render added; applying after the render and
reading the phase's `applied` list is exact.

### 5. The joint goes on the child by specialization, class form

At the assembly's class creation, for each mate, the moving child
declaration's `node_class` is replaced by `_specialize(node_class,
{mate_name: joint})` — ADR-098's mechanism, unchanged: identity, name,
qualname, module, doc and source file copied, so the child keys the same
artifacts; the joint's `__set_name__` fires against the child's MRO and
`_refuse_shadowing` refuses a clash with anything the child answers to
(the message wrapped to name the mate). Because the name is new on the
child, `declared_joints` places it AFTER every joint the child's class
declares (ADR-093). The specialization is built at class creation, not
at the `on()` call: the mate's name, which the joint and the coordinate
both carry, is known only once the assignment has run.

The joint is `Revolute(axis=moving_frame.z, at=moving_frame.at,
range=freedom.range, unit=freedom.unit)` with the frame's DECLARED
arguments copied literally — a tuple, tokens, formulas or a callable of
the node — so it resolves against the child in `resolve_declared_joints`
exactly as a class-declared joint does, with `_declared_at_site` False:
nothing is carried, nothing inverted (ADR-097). The joint normalizes its
own axis; the frame's `z` and the joint's axis are the same direction.

**Deviation: the freedom's range is restricted.** The placement put the
joint in "class form". A class-form joint resolves `range` against the
CHILD's parameters and resolves a `Bound`'s reads against the child
(`Joint.declarer_of`), but the freedom is written in the ASSEMBLY's body.
Thor's ranges are numbers (on its drivers, today). So a freedom's range
is admitted only as numbers, `None`, or per-bound functions of the
coordinate's own value — all declarer-independent — and a parameter
token, a whole-range callable of the node, or a `Bound` with `reads=` is
refused at class creation naming the mate. A later project that needs
an assembly-scoped range gets a resolver-side resolution then.

### 6. The coordinate reaches the joint through a wiring, with one exemption

The mate is added to the child declaration's `wiring` under the mate's
name, so `_record_wiring` marks the child's joint `wired_from` at
realization, `_wirings`/`Wiring.apply` bind it from the assembly's slot
in the assembly's fixpoint, `clear_solved` drops it with its motion, and
`bind()` refuses any other binder (ADR-088's single-binder rule, message
reworded for a mate). Relations, drivers and derived coordinates see the
assembly's port and nothing new.

**Deviation: an unbound mate coordinate is not refused.** The existing
wiring path refuses an unbound source at the fixpoint's close
(`couplings.py`, `wiring.unbound_source()`; the `ports` spec, "Binding a
wiring whose source coordinate is unbound SHALL fail"). An unbound
joint, by contrast, simply rests. A mate is a joint as far as its author
is concerned, so a mate's wiring carries a flag that skips it when its
source is unbound and leaves the child's joint cleared. The `ports`
requirement is untouched because it governs the wirings an author
writes as keywords; the mate's is framework-built and the `mates` spec
states its behaviour.

*Alternative rejected: alias the assembly's coordinate to the child's
slot* (one slot, two names). It needs no exemption, but it gives one
value two addresses — `arm.elbow` and `arm.art3.elbow` — in every
qualified-id enumeration, the document's bindings table and the
serializer's symbolic pass, which is the hazard the driver-sideways rule
exists to prevent. The wiring keeps one binder and one address.

### 7. `Revolute` without an axis

`Revolute.__init__(self, axis=None, at=(0, 0, 0), range=None,
unit=None)`; `Joint.__init__` keeps `axis` required for every other kind.
An axis-less `Revolute` is refused when it is named in a class body
(`Joint.__set_name__`), at a declaration site (`ChildDeclaration.__init__`,
before specialization), and accepted only by `FrameRef.on`, which checks
it is fresh (`owner is None`, not bound in the executing body) and
axis-less and anchor-less (`at` left at its default object — compared by
identity to the default so an explicit `at=(0, 0, 0)` is refused too).

### 8. Nothing is published that is not already publishable

The compiled rest placement is `Rotation`/`Translation` in `operations`;
the coordinate is a port with a binding. No serializer, export or
document-version change. Frames are not serialized. A machine with no
frame and no mate takes no new path at all (the duck-typed checks find
nothing), and a byte comparison of its exported document before and
after is a test.

### 9. What the rigid mate would add (scope question 2)

If the pilot wants it now: (a) `on()` with no freedom, its placement
compiled as decision 4 and no joint, no coordinate, reading it yields
the declaration; (b) the fixed-end-on-a-moving-child refusal relaxed for
a child placed by a RIGID mate, which brings a dependency order among
sibling mates (fixed side first) and a cycle refusal naming both mates;
(c) a document-level decision on whether a rigidly mated child's
placement differs in any way from a hand-written one (it should not).
None of this is in the tasks.

### 10. ADR

One new ADR, **ADR-147 (NODE): a mate compiles at realization to a rest
placement, a joint and a coordinate** — the frame as a declaration
(extends ADR-120's mould to assemblies), the statement (extends ADR-061,
ADR-089's channel), the compile (extends ADR-066's rest render, ADR-093's
slot, ADR-097's own-frame rule, ADR-098's specialization, ADR-088's
wiring with the unbound exemption, ADR-114's slot mark), the depth-one
and still-fixed-child restrictions, and the rejected alternatives.
Written `Proposed` with the planning commit, `Accepted` at archive.

## Risks / Trade-offs

- **Specialization identity** — `type(child) is Art3` stops holding for
  a mated child, as for a site-jointed one (ADR-098 consequence, pinned
  by `SpecializationOwnTypeGuardTest`). → Nothing in the catalogue
  writes the identity check; covered by the existing guard test plus
  one mate case.
- **Mate name on the child** — the installed joint takes the mate's name
  on the child's class, so a mate cannot reuse a name the child answers
  to. → Refused by name at class creation; Thor's migration deletes the
  child's own `elbow`/`shoulder`/`yaw`/`wrist` joints in the same edit.
- **Wiring exemption** — a second rule where the `ports` spec states one.
  → Scoped by a flag only the mate sets; spec'd in `mates`.
- **Two coordinates in the bindings table** — the assembly's port and
  the child's wired joint both appear, as for any wiring today. → No
  document change; the Thor migration's comparison is by pose, and the
  viewer already consumes wired coordinates.
- **Rotation decomposition residue** — axis–angle extraction near 0 and
  180 degrees is ill-conditioned. → Snapping (decision 4); 180-degree
  extraction by the diagonal, as the spike does; tests pin both Thor
  cases.
- **Running and clocked roots** unexercised. → Stated as a non-goal; a
  project that needs it brings the evidence.
- **Existing tests that assert `Revolute()` raises `TypeError`** (none
  found by grep in `tests/`; the implementer re-checks) would change to
  the class-definition refusal.

## Migration Plan

No framework user migrates: every existing declaration keeps its
meaning. The originating project migrates afterwards, in its own
repository, by a separate agent (tasks, section 9): frames emitted from
the design's LCS beside `emit_layout.py`, the Assembly4
`AttachmentOffset` folded into the moving frame's triad, five mates
replacing five hand placements and five joint declarations and the
shared constants, a pose comparison at maximum deviation 0, and the
stale-solve finding recorded. Rollback is reverting the framework
commits; Thor's migration is on its own branch.

## Open Questions

- The three scope questions in `proposal.md` (freedoms, rigid mate,
  Thor scope). The artifacts are written to the recommendations.
- Whether the mate's coordinate should carry the freedom's range for
  consumers that read a port's range (controls, the viewer's slider).
  Not needed by Thor, whose ranges are on its drivers; left out.
