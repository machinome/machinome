# ADR-151: A Mate's Freedom May Be a Prismatic

**Status:** Accepted
**Date:** 2026-09-26
**Amends:** [ADR-147](ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md) ("The freedom is a fresh `Revolute`"; "A `Mate` is a `Coordinate` owning one `RotationalPort`"; "`Prismatic`, `Orbit`, `Free` and no freedom at all (the rigid mate) are refused naming this version's scope"; the deferral of `Prismatic` freedoms in its Consequences)
**Extends:** [ADR-148](ADR-148-a-mates-freedom-may-state-its-own-line.md) (a freedom's stated line, read in the moving child's own frame, now also for a slide, save that a `Prismatic` freedom always states its axis), [ADR-150](ADR-150-a-mates-freedom-may-be-a-function-of-the-assembly-that-states-it.md) (a freedom's `axis` and `range` as functions of the assembly, unchanged for the new kind)
**Cites:** [ADR-112](ADR-112-a-control-is-a-declaration-on-the-model-and-the-gesture-comes-from-the-tree.md) (a control publishes the joint's anchor as its gesture's origin, which is what a slide's `at` still means)
**OpenSpec change:** `slide-by-mate`
**Ratified:** 26 September 2026, by the orchestrator's review under the review gate the pilot delegated on 7 September 2026, with the proposal's scope questions answered: `at` taken as a `Revolute` freedom's, functions of the assembly admitted by ADR-150's rules, a new ADR amending ADR-147, and the axis-less `Prismatic` struck.

## Context

The originating project is a four-joint arm with a two-finger gripper,
reconstructed from its URDF. The URDF states its two finger joints
exactly as it states its four revolutes -- parent, child, origin, axis in
the child's frame, limits -- except that they are `prismatic`, the right
finger a mimic of the left. Moving onto frames and mates, the four links
could be mated as another URDF arm's had been, and the fingers could
not: ADR-147 accepted a `Revolute` freedom only, because the project
that asked for mates exercised only revolutes, and deferred `Prismatic`
until a project needed one. The fingers would have stayed a `translate`
in the palm's `render()` and a class-body `Prismatic` on each finger,
beside four mates, the migration split down the middle.

Everything the mate compiles to past the kind check was already
kind-blind: the joint resolves, places, clears and range-checks through
`Joint`; ADR-150's realization path copies the installed joint and runs
its own `resolve`; the rest placement is composed from the frames
alone; the wiring, the unbound rule and the single-binder refusal key on
the mate; a `Prismatic` publishes its slide as a `Translation`. Three
places named the one kind: the freedom check, the installed joint and
the coordinate's port kind.

## Decision

**A mate's freedom may be a `Revolute` or a `Prismatic`, under one
rule save the axis.** `finger.origin.on(seat, Prismatic(axis=(0, 1, 0),
range=(-11, 20), unit='mm'))` slides the moving child along the line it
states, in its own rest frame. Every rule of a `Revolute` freedom applies
to a `Prismatic` one, checked in the same order: the freedom is fresh; a
stated `at` is three numbers, a written `(0, 0, 0)` the child's own
origin and a left-out one the moving frame's; a stated `axis` is three
numbers of non-zero length or one function of the assembly (ADR-150); a
range is a pair of numbers, `None` or functions of the coordinate's own
value, or one function of the assembly; tokens, formulas, a `Bound` with
reads and a function `at` are refused for the reasons ADR-148 and
ADR-150 give. The frames alone fix the rest placement and so the zero of
the coordinate. The one asymmetry: **a `Prismatic` freedom states its
`axis`**, as a `Prismatic` must anywhere. Its constructor keeps `axis`
first and required, so one written without it is refused by Python
before the mate exists, and the mate adds no refusal of its own; a
`Revolute` stays the one joint that may leave its axis to the moving
frame's `z`, as a mate's freedom only.

**The moving child gets a joint of the freedom's kind.** `_install`
builds a `Prismatic` for a `Prismatic` freedom from the expressions it
uses for a `Revolute` one -- the stated `axis` passed straight through
(never the moving frame's `z`), the written `at` else the moving frame's
declared `at`, the range and the unit -- and installs it by
specialization under the mate's name, as before. A `Revolute` freedom
installs the same `Revolute`, holding the same objects.

**The mate's coordinate is of the freedom's port kind, in its unit.**
A `Prismatic` freedom gives the assembly a `TranslationalPort`, in
`'mm'` unless the freedom states a unit; a `Revolute` one a
`RotationalPort` in `'deg'` as before. The kind is not cosmetic: a
relation's derived coordinate refuses terms of two domains, a running
program publishes each coordinate's domain and unit, and a `Slide`
control requires a translational coordinate. A freedom `_check_freedom`
will refuse still gets a `RotationalPort`, since the mate exists,
unchecked, while the class body runs.

**`Prismatic` gains `Revolute`'s anchor default, and nothing else.** The
two share one private base, `_MateFreedom`, whose `at` defaults to the
one `_DEFAULT_ANCHOR` object and whose `anchor_written` tells a
left-out anchor from a written `(0, 0, 0)` by identity. `Orbit` and
`Free` do not gain it. A `Prismatic`'s anchor places nothing -- a
translation along a line is the same wherever the line is taken to pass
-- and is carried as the joint's, which a control publishes as its
gesture's origin (ADR-112). A class-body or site `Prismatic` behaves and
publishes exactly as before.

**Messages.** The refusal of any other freedom says it is neither a
`Revolute` nor a `Prismatic`, and the rigid mate's hint names both. A
`Prismatic` freedom's own refusals speak of a line to slide along; a
`Revolute` freedom's are unchanged byte for byte.

**Unchanged:** the rest placement; relations (a URDF mimic is a relation
between the two mates' coordinates, `left_grip.drives(right_grip)`,
which already worked); the document, serializer, viewer and mechanics
package; the `joints` spec, `Joint.__set_name__`'s and the declaration
site's axis-less refusals, which stay `Revolute`'s; every existing mate,
which installs the same joint and publishes the same bytes.

## Rejected alternatives

- **The narrowest `Prismatic` freedom** -- `at` ignored, installed as
  `Prismatic(axis, at=(0, 0, 0), ...)` as a class-body slide is written.
  The mate's documented reads (`anchor_written`, "`at` is the mate's
  anchor only when written") would mean one thing for one kind and
  nothing for the other, and a left-out `at` would be the child's origin
  for one kind and the frame's for the other. The difference in cost was
  the anchor default and `anchor_written`.
- **Refusing a written `at` on a slide**, because the placement ignores
  it: the freedom would be narrower than the joint it installs, a
  kind-specific refusal would be added, and `anchor_written` would still
  be needed. The anchor is read: a control publishes it.
- **A rotational coordinate for every mate.** It passes a document that
  publishes no program and misdescribes the machine everywhere a domain
  is read: a relation mixing it with a translational end, a running
  program's coordinate table, a `Slide` control.
- **The axis-less `Prismatic`** -- `Prismatic(range=...)` accepted as a
  freedom, the moving frame's `z` supplying the line, with the axis-less
  refusals widened elsewhere. The originating project states both finger
  axes, the URDF's `(0, 1, 0)` and `(0, -1, 0)`, not the moving frame's
  `z`; no project needs a slide along the moving frame's `z`; the
  argument for it was uniformity across kinds, which is not evidence.
  Struck at ratification.

## Consequences

- A gripper's fingers are mated like its links: the originating project
  states all six URDF joints as mates, read verbatim from the URDF, in
  its own repository's follow-up.
- ADR-147's consequence holds for both kinds: a child a `Prismatic` mate
  places moves, and is refused as a fixed end by the existing branch, so
  the dependency order is the declaration order and no cycle can be
  written.
- A `Prismatic` written without an axis is refused by Python's own
  "missing 1 required positional argument: 'axis'", naming the private
  base's `__init__`, at the line that writes it, before any mate exists.
  An explicit `Prismatic(axis=None)` as a freedom is installed as
  written and refused, as a class-body one is, by `Joint.__set_name__`'s
  axis-less refusal, whose wording still names a `Revolute`.
- A freedom's `unit` is not checked against its kind
  (`Prismatic(unit='deg')` is accepted), as for a class-declared joint.
- Still deferred, each needing its own evidence: `Orbit` and `Free`
  freedoms, the rigid mate, loops, ends deeper than one child, repeated
  frames, controls on a mated part.
