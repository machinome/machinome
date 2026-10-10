## Context

The originating project is `projects/Calculators/Curta-Type-I-3x`. Its approved
interaction design has eight separately handled setting selectors, a crank
that lifts and turns, a carriage that lifts and turns, a reversing lever,
a clearing ring and independently movable decimal markers. The user chooses
the order; the machine's declared limits decide what movement is possible.

ADR-112 and the current simulation specification deliberately support only
`Button` and `Turn`, infer a single nearest posing joint, and refuse a body
declaring multiple joints. The viewer independently assumes a rotational
placement even for a button. These are actual public-contract limits, not
missing Curta event handlers. This change revises ADR-112's single-joint
restriction; it does not revise the run's integration or constraint semantics.

This standalone cycle is based on framework main
`3519c61bf6d79e2be5df7a5972411358c9ae2371`, on branch `direct-part-motion`
at `solid-node/WTs/direct-part-motion`. The paired consumer change is
`solid-node-viewer/openspec/changes/slide-and-turn-parts`. Planning is proposed,
not ratified. Local integration into framework main needs pilot authority.

## Goals / Non-Goals

**Goals:** let a model declare sliding interaction and independently address
the existing sliding and turning freedoms of one body; derive interaction
geometry from that body's actual placement; preserve command admission,
stops, history, program identity and existing control declarations.

**Non-Goals:** a collision/force solver, automatic operation ordering, arbitrary
six-axis manipulation, new mechanical laws, a Curta-specific framework API,
UI implementation in this repository, or publishing either package.

## Decisions

### 1. A slide names an input, just as a turn does

Add `Slide(part, input, *, coordinate=None)` to `solid_node.simulation`.
The input belongs to the declaring class and must reach the selected joint
coordinate through the compiled program. Its domain must be translational.
Measure `per_unit` through the existing rest-bank measurement, including its
existing refusal of a zero or locally inconsistent response. Authors do not
repeat an axis, pivot, direction, scale or law in the control declaration.

`Button` remains an instruction request, with no directional gesture. It can
name either a translational or a rotational single-coordinate joint.

Alternative: translate a vertical pointer movement into a fake rotational
input. Rejected because the declaration would misdescribe the mechanism and
the viewer would measure movement in the wrong physical frame.

### 2. Coordinate selection is explicit only when inference is insufficient

Add the keyword-only `coordinate` argument to `Button` and `Turn` as well.
It accepts the existing joint declaration/path reference, not a string id.
For a root with child `crank`, the intended spelling is:

```python
controls = {
    'Turn crank': Button(crank, 'One revolution', coordinate=crank.turn),
    'Rotate crank': Turn(crank, crank_hand, coordinate=crank.turn),
    'Lift crank': Slide(crank, crank_lift_hand, coordinate=crank.lift),
}
```

The selected joint must actually pose the touched part or one of its
ancestors, belong to the same linked tree and own exactly one run-banked
coordinate. No selection may reach sideways to another mechanism. A joint
with several coordinates, including `Free`, remains refused. Without an
explicit selection the existing nearest-single-joint inference and its
ambiguity refusal remain unchanged. Selection adds no joint or source edge.

Alternative: restructure every two-freedom body into empty wrapper nodes so
the control can find a different nearest joint. Rejected as a control-specific
distortion of the project's mechanical assembly.

### 3. A selected joint publishes its place in composed motion

Retain the existing control entry and add optional `operation_span: [start,
end]`, a half-open interval into the named joint node's `operations`, when
needed for a translational or explicitly selected coordinate. It identifies the
complete placement block of the selected joint, including pivot translations.
Indices are derived from the placement's existing ownership slots, never from
searching the rendered expression text or a second author declaration.

With operations applied from first to last (inner to outer), the joint's
interaction frame is its parent's current world matrix composed with the
operations **after** that block. Its `axis` and `origin` are expressed in the
block's input/output frame, before those outer operations. This frame carries
the joint's line without allowing an inner joint to rotate the line belonging
to an outer joint. The selected motion itself preserves its own axis line.
The viewer evaluates the outer operations using the current committed bank,
not a pose captured on pointer-down.

Existing inferred rotational controls keep their byte-identical table and
legacy frame interpretation, with no new field. New entries remain additive
within document version 5: ignoring controls still renders the same run;
an older control-aware viewer rejects unsupported entries instead of moving
parts incorrectly. The new viewer capability is API 13. No expression enters
the control table, no control participates in `bindings`, and no control changes
the program or its identity. The framework's bundle reporting remains the
existing cross-process contract, with no consumer import.

Alternative: use the final node world matrix for every joint. Rejected because
two non-parallel freedoms on one body need different current axis frames.
Alternative: publish a second set of frame expressions. Rejected because the
document already carries the operations and their binding dependencies.

### 4. The run remains the only motion authority

Sliding and turning controls merely identify existing `move` requests; a
button identifies an existing instruction. Bounds, ownership conflicts,
interruptions and partial movement are neither predicted nor repaired by a
control. A blocked crank does not cause the carriage to seat. Releasing a
gesture does not rewind state. Driver ranges remain presentation metadata.

The Curta will declare its actual restraints in its project. Those restraints
must be observable through the Python run as well as through a browser; they
are not UI-disabled states or an arithmetic calculator kept beside the run.

## Risks / Trade-offs

- Incorrect operation ownership or order could produce plausible but wrong
  gestures → export offset-pivot, fixed-placement and non-parallel composed
  fixtures, and test their frames at several committed poses.
- A rest-measured gesture ratio can lead or lag a state-dependent mechanism
  → retain the existing documented limitation; movement always follows the
  admitted run, never pointer placement.
- An older viewer cannot operate new controls → preserve old declarations,
  report the required new viewer capability in documentation, and validate the
  paired packages before attempting the Curta browser acceptance run.
- The Curta has pre-existing geometry validation gaps → report them separately;
  this prerequisite is not evidence that its whole mechanism is proven.

## Migration Plan

After ratification, validate and commit planning only. Add red-first tests for
Slide, coordinate selection, publication and frame ownership, then implement
the producer and publish deterministic small fixture documents for the paired
viewer. Preserve the running conformance corpus byte-for-byte. Confirm the
consumer's browser evidence before reporting the originating need satisfied.

Only after implementation evidence confirms the design, update ADR-112 through
a new accepted decision and update the architecture synthesis. Sync and archive
through OpenSpec, then create the second cycle commit. Integrate locally only
on pilot authority and only if main is clean and still at the recorded base.
Rollback is to keep using the old paired packages and old model; no data or
snapshot format migration is required. Do not push, tag or publish.

## Open Questions

No implementation choice is delegated to the pilot beyond ratification of
this prerequisite design and authority for its eventual local integration.
Any evidence requiring another change to the run's semantics returns to the
pilot as a separate finding rather than silently expanding this cycle.
