# ADR-148: A Mate's Freedom May State Its Own Line

**Status:** Accepted
**Date:** 2026-09-26
**Amended by:** [ADR-150: A Mate's Freedom May Be a Function of the Assembly That States It](ADR-150-a-mates-freedom-may-be-a-function-of-the-assembly-that-states-it.md) — a stated `axis` may be one function of the assembly that states the mate, called once as the assembly realizes the moving child, its result checked and read as three numbers are; `at` stays three numbers
**Amends:** [ADR-147](ADR-147-a-mate-compiles-to-a-rest-placement-a-joint-and-a-coordinate.md) ("the freedom is a fresh `Revolute` with neither axis nor anchor")
**Extends:** [ADR-097](ADR-097-a-joint-is-stated-in-the-frame-of-whoever-declares-it.md) (a stated line is read in the moving child's own frame, the class form)
**OpenSpec change:** `state-the-mate-line`
**Ratified:** 26 September 2026, by the orchestrator's adversarial review under the review gate the pilot delegated on 7 September 2026, on the pilot's instruction of the same day to work the `place-parts-by-mate` findings with the originating project as the validator: both provisional dispositions reopened, a stated line numbers only, a new ADR amending ADR-147.

## Context

ADR-147 made a mate turn its child about the moving frame's `z`,
through the moving frame's origin, and refused a freedom that stated
either. That assumes a part's connector IS its joint frame. The
originating project, a six-axis robot arm reconstructed from an
assembly CAD design, showed otherwise: its design's connectors are
ATTACHMENT frames, and folded with their offsets their `z` lies on the
joint line for two of its five root-chain links, reversed for one and
across the line for two. To mate the three, its frame emitter turned
both frames of each pair about their shared origin until the moving `z`
was the joint line, choosing the attitude about it by restating the
framework's default-`x` rule -- a choice the design does not make. The
same rule, seen from the anchor, gave the shoulder a centring pair its
hand-written joint did not have: the moving frame sits 68 up the joint
line, and ADR-147 copied that origin as the joint's anchor.

## Decision

**A mate's freedom may state its own line.**
`Revolute(axis=..., at=..., range=..., unit=...)` is accepted as a
mate's freedom. A stated `axis` and a stated `at` are read in the
MOVING CHILD's own rest frame -- the frame the moving frame is declared
in, the frame a joint the child's own class declares is read in
(ADR-097), and the frame the installed class-form joint already
resolves in. `_install` passes them straight through: nothing is
carried or inverted.

**Each defaults independently to the moving frame.** No `axis`: the
moving frame's `z`. No `at`: the moving frame's origin. The installed
joint is `Revolute(axis=<stated or frame z>, at=<stated or frame at>,
range, unit)`, the frame's arguments still copied as DECLARED. A freedom
that states neither installs exactly the joint ADR-147 installed and
publishes the same bytes. `Revolute`'s left-out-anchor sentinel stays,
with one purpose: `at` left out takes the frame's origin; `at` written,
even as `(0, 0, 0)`, is the CHILD's own origin (`anchor_written`, by
identity).

**The frames still fix the rest placement and the zero.** `apply_mates`
and `_placement` are unchanged: the moving frame is laid triad onto
triad on the fixed one, so the frames fix where the child rests and the
zero of the coordinate, and the freedom fixes only the line it turns
about from there. The frame's default-`x` rule and its refusal of a
non-principal `z` without `x` are unchanged; the frame's `z` is the line
by default only. Nothing checks a stated line against the frames: an
anchor is any point on its line, and the line is the freedom's own.

**A stated line is three numbers, checked at class creation.** Each of
a stated `axis` and a written `at` must be a sequence of three `int` or
`float` values, not `bool`; a parameter token, a formula, a callable, a
string or a sequence of another length is refused, naming the class,
the mate and the argument and saying the line is written in the
assembly and read in the moving child's frame. The installed joint
resolves against the CHILD, and a token resolves BY NAME, so an
assembly's token would silently read a child parameter of the same
name, and a callable would be called with the child -- the reason
ADR-147 already restricts the freedom's range. Because the values are
numbers, a stated `axis` of zero length (below the joint's `1e-9`) is
refused at class creation too, naming the mate, before the installed
joint's realization-time refusal could name only the child.

## Rejected alternatives

- **The line in the moving frame's own axes** (`axis=(1, 0, 0)` meaning
  the frame's `x`): a reader would compose the frame's triad in their
  head to find the line, the installed joint would need its axis and
  anchor transformed at installation -- the carry the class-form joint
  avoids -- and a project that already states each link's line in the
  link's frame would re-express it per connector.
- **The line in the assembly's frame** (the site form, ADR-098): it
  would be carried through the child's rest placement; the mate's joint
  is a class-form joint and the freedom speaks for the child.
- **The line on the frame** (`Frame(..., axis=...)`): a frame is where
  another part attaches; the line a part turns about belongs to the
  joint between two parts, and one connector may serve a revolute mate
  now and a rigid mate later, where a line would mean nothing.
- **The whole joint argument rule** (tokens, formulas, callables of the
  child): each would resolve against the node the line is not written
  in. No project needs one; one that does gets a resolver-side
  resolution then, together with the range.

## Consequences

- A design's connectors can be declared verbatim: the frames place the
  part, the freedom states the line. The originating project's emitter
  loses its turn and its restated default-`x` rule, and the shoulder's
  centring residue goes, in its own repository's follow-up.
- `at=(0, 0, 0)` written now differs from `at` left out whenever the
  moving frame's origin is not the child's: deliberate, pinned by a test
  pair.
- A reader may find the line in two places, the frame's `z` or the
  freedom; the freedom wins when it states one.
- Numbers only is narrower than a class-declared joint; the refusal
  says why.
- Unchanged: the document (no field, no version move), the serializer,
  the viewer, the mechanics package, `Revolute`'s axis-less refusal
  outside a mate (reworded: the moving frame supplies the axis), and
  every other mate refusal and deferral (`Prismatic`, `Free`, the rigid
  mate, deeper ends, repeated frames, publishing frames or mates).
