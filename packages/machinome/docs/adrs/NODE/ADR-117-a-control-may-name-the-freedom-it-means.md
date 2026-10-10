# ADR-117: A Control May Name the Freedom It Means, and the Document Says Which Placement That Freedom Is

**Status:** Accepted
**Date:** 2026-09-15
**Supersedes in part:**
- [ADR-112: A control is a declaration on the model, and the gesture's geometry comes from the tree](./ADR-112-a-control-is-a-declaration-on-the-model-and-the-gesture-comes-from-the-tree.md) — its decision 2, the single-joint narrowing, and the `Slide`/composed-joint extensions it recorded rather than took
**Depends on:**
- [ADR-093: Joints of one class compose in declaration order](./ADR-093-joints-of-one-class-compose-in-declaration-order.md)
- [ADR-114: A joint's placement is identified by its slot, not by what bound it](./ADR-114-a-joints-placement-is-identified-by-its-slot-not-by-what-bound-it.md)
**Cites:**
- [ADR-110: The compiled program is published in the document](../EXPORT/ADR-110-the-compiled-program-is-published-in-the-document.md)
- [ADR-111: A conformance corpus is the contract between the two runtimes](../EXPORT/ADR-111-a-conformance-corpus-is-the-contract-between-the-two-runtimes.md)
- solid-node-viewer `slide-and-turn-parts`, the paired consumer change
**OpenSpec change:** `direct-part-motion`

## Context and Problem Statement

ADR-112 put the request on the part and derived everything else from
the tree. It also narrowed hard: one control names one coordinate, that
coordinate is the one owned by *the nearest ancestor-or-self of the part
whose joint the run banks*, a posing node declaring several joints is
refused, and `Turn` is the only drag there is. Under that narrowing the
coordinate is always bare in its joint's own operation, so a consumer
could take the joint node's whole world matrix as the gesture's frame
and never be wrong.

`projects/Calculators/Curta-Type-I-3x` is the machine that narrowing
cannot describe. Its eight setting selectors only slide. Its crank
lifts along the machine's axis and turns about it. Its register carriage
does the same. There is no nearest joint on a body with two, and there
was no prismatic gesture at all — a selector could not even carry a
`Button`, because the viewer validated a leading rotation on every
control it read.

Two questions had to be answered together. Which coordinate does this
control mean, when the tree cannot say? And once two controls name two
freedoms of one body, what is each gesture's frame — because the body's
world matrix now contains *both* placements, and using it for either one
applies the other joint's motion to a line that does not move with it.

## Decision Drivers

- The declaration says only what the tree cannot: ADR-112's whole
  argument, applied again. An author who must restate an axis, a pivot,
  a direction or a scale is an author with a second number to drift.
- A control on a two-freedom body must not distort the assembly. The
  alternative on the table was wrapping every such body in empty nodes
  so that inference would find a different nearest joint — a
  control-shaped change to a mechanical model.
- Nothing the run computes may move: the program, its `identity` and the
  conformance corpus (ADR-111) are what a snapshot is judged against.
- Every document published before this must be byte-identical after it.
- The frame must be recoverable at *every* committed pose, not only at
  rest, and from what the document already carries.

## Considered Options

1. **Translate a vertical pointer movement into a fake rotational
   input.** Rejected: the declaration would misdescribe the mechanism,
   and the viewer would measure the gesture in the wrong physical frame.
2. **Restructure two-freedom bodies into wrapper nodes** so inference
   finds one joint per node. Rejected: a control-specific distortion of
   the project's mechanical assembly.
3. **Publish the final node world matrix for every joint**, as the
   legacy entry effectively does. Rejected: two non-parallel freedoms on
   one body need different current axis frames, and an inner rotation
   would turn the outer joint's line.
4. **Publish a second set of frame expressions** beside the control.
   Rejected: the document already carries the operations and their
   binding dependencies; a second copy is a second thing to drift.
5. **Name the existing joint, and name its existing placement block.**
   Chosen.

## Decision

**A control may name the joint it means, `Slide` is the prismatic
gesture, and an entry that needs one publishes the half-open interval of
its own placement inside the joint node's operations.**

1. `Slide(part, input, *, coordinate=None)` joins `Button` and `Turn` in
   `solid_node.simulation`: a drag *along* the selected translational
   coordinate, declared exactly as a turn is and deriving its axis, its
   origin and its `per_unit` from the same places. A `Turn` requires a
   rotational coordinate and a `Slide` a translational one; a `Button`
   requires neither, because a press has no direction.
2. The keyword-only `coordinate=` on all three names an existing joint
   DECLARATION — the `Revolute(...)`/`Prismatic(...)` itself, or a path
   of declared children to one (`crank.lift`), never a qualified id
   string, for the reason a `Turn`'s input is never one. The selected
   joint must pose the touched part or one of its ancestors in the same
   tree, must own exactly one coordinate, and must be one the run banks.
   It may be *further* from the part than the nearest joint; it may
   never reach sideways to another mechanism. Without a selection,
   ADR-112's inference and its ambiguity refusal are unchanged, and the
   refusal now names the escape.
3. Selection adds no joint, no edge and no source. `Program.described()`
   still never learns that a control exists, so `identity` and the
   corpus are what they were.
4. `operation_span: [start, end]` is published for a translational
   coordinate and for any coordinate the author selected, and for
   nothing else. It is a half-open interval into the named joint node's
   own `operations`, derived from the slot mark every operation a joint
   places already carries (ADR-093, ADR-114) — the thing that placed
   them — and never from searching a rendered expression for a
   coordinate's name. A block that is not exactly one contiguous run of
   that coordinate's operations is refused rather than published as an
   invented frame.
5. With operations applied first to last, inner to outer, the gesture's
   frame is the joint node's parent's current world matrix composed with
   the operations *after* the block; `axis` and `origin` remain the
   values the placement was built from, expressed in the frame that
   block acts in. So an inner joint's motion is never applied to an
   outer joint's line, a sliding pivot travels with its rail, and the
   consumer evaluates the outer operations against the committed bank
   rather than a pose captured on pointer-down.
6. An entry inferred over a single rotational joint publishes no span
   and keeps its existing field order and bytes: such a joint turns its
   own axis and its own pivot into themselves, so the whole world matrix
   was already right for it. The table stays additive within document
   version 5 — the version does not move, no expression enters it, it
   never touches `bindings`, and a document declaring no control is
   byte-identical to the one published before controls existed.

## Consequences

- The Curta's selectors, crank and carriage become declarable: three
  controls on one body, each naming the coordinate it means, with no
  change to the body, its placement or the run program.
- The run remains the only motion authority. A sliding control is the
  `move` the panel would have issued; a stop belonging to a second
  mechanism stops it exactly as it stops that move; releasing a gesture
  rewinds nothing, and a blocked crank does not seat the carriage.
- A viewer must read spans to operate a sliding part or to pick between
  the two freedoms of one body: that is the paired viewer's API 13. A
  viewer that ignores the table still drives the machine from the panel
  and still renders the truth.
- `per_unit` is still a reading at rest. A slide whose ratio changes
  with state gets a looser drag, not a wrong one.
- What remains recorded rather than taken: a control on a joint owning
  several coordinates (a `Free`), which naming the joint does not
  unpack, and a `Button` on a part nothing poses at all.
