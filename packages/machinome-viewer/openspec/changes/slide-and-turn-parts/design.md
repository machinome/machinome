## Context

The pilot approved direct physical interaction with the Curta. Its selectors
translate; its crank and carriage each translate and rotate. The viewer's
current API 12 controls support buttons and rotational drags only, and reject
even a button whose posing coordinate is translational. ADR-053's leading
rotation rule must therefore be extended coherently with the framework's
`direct-part-motion` change.

This is an independent AGPL viewer change, based on main
`33ac0ad934ee5011f2085365134a640bd4544ee8`. Producer-generated fixture
documents cross the repository boundary; Python imports do not. The pilot
subsequently requested adversarial review, correction of missing work, and
implementation of the already approved Curta interactions. The browser
prerequisite remains a separate public-package change under that direction.
The reviewed producer is now based on merged main in `harden-direct-part-motion`,
following the pilot's updated branch instruction.

## Goals / Non-Goals

**Goals:** operate sliding parts directly; make sliding and turning separately
reachable on the same part; preserve click-to-instruct, current-frame geometry,
occlusion, camera ownership, cancellations and run-owned outcomes.

**Non-Goals:** enforce an operation sequence, move another control for the user,
write coordinate state from a pointer, change the worker's mechanical solver,
replace the run panel, implement the Curta's mechanical laws, or publish.

## Decisions

### 1. Slide is a translational gesture on a declared part

Read `kind: slide` with the same named input and measured ratio as a turn.
Resolve the joint's present world axis using the document's placement. Measure
signed displacement along that axis in coordinate units, then use the existing
nudge amount/duration, one-request-in-flight and no-backlog planner. Reversing
the pointer reverses the request; a blocked request does not create queued
travel. No pointer position is applied to the part's transform.

For an axis viewed too nearly end-on to measure displacement reliably, show
that the view needs rotating and issue no guessed movement. The ordinary panel
nudge remains available. Test the angular threshold and continuity at its
boundary; use the existing rotational fallback unchanged for turns.

Alternative: use an arbitrary vertical pixels-to-millimetres drag. Rejected
because it loses the connection between the visible rail and the gesture.

### 2. A two-freedom part exposes both physical directions

A part with only one drag control is directly draggable as before. When a
part has both a Slide and a Turn, hovering or selecting it shows two compact
on-part drag handles: an axial arrow and a turning arc, labelled by the
declared names. Grabbing one selects exactly that gesture until release.
The part body remains clickable for its declared Button; touching/selecting
it makes the handles reachable for touch input as well. The handles are
visible interaction cues, not new mechanical parts or an operation menu.

Neither handle invokes the other, chooses an operation order or makes an
interlocked movement succeed. A plain drag of a multi-freedom body without
choosing a handle submits no ambiguous request. The UI exposes the handles
clearly before motion so it does not silently choose a degree of freedom.

Alternative: guess slide versus turn from the initial pointer direction.
Rejected because the projections can overlap. Alternative: modifier keys as
the only way to lift. Rejected because the interaction must be discoverable
and usable with touch. Keep at most one button, slide and turn per part;
multiple controls of the same kind remain a named load-time refusal.

### 3. Gesture geometry follows the selected placement, not the whole body

Consume the producer's optional `operation_span: [start, end]` as a half-open
interval selecting the complete joint placement block. Validate its bounds,
operation structure and coordinate identity before replacing a standing
scene. Derive the interaction frame from the parent's current world matrix
and the joint node's outer operations after that interval. Use the committed
bank and existing expression evaluation, including bindings, for those outer
operations. A slide requires a translational placement; a turn requires a
rotational placement. A button may refer to either.

Legacy controls without the interval retain the existing rotational contract
and frame behavior. No-control documents remain unchanged. Current geometry
is recomputed as the run and camera move, including during a held gesture.
The viewer neither invents nor derives a second mechanical coordinate graph.

### 4. Picking, reporting and the host interface stay coherent

Handles follow the part's visibility, focus and occlusion. They cannot make a
hidden control accessible through another part. Engaged gestures capture the
pointer and suspend camera manipulation; release, cancellation, lost capture,
lost focus, page hiding, model replacement and disposal all clear the gesture
and restore camera behavior. Existing issued-command cancellation behavior
is preserved; gesture cancellation never rewinds an admitted movement.

`controls()` continues to report every declaration, including hidden ones.
Report Slide and the selected placement metadata, and expose the reachable
gesture-handle point for each drag control in viewport CSS coordinates.
Keep the existing part rectangle and button press point meanings. A host or
browser test must be able to grab the reported handle without private scene
or run access. Missing/occluded handles report no reachable point.

Publish API capability version 13 through the widget global and package
description, with the same document version set. Update all duplicated
capability assertions and public types. This is an unreleased capability,
not a package publication or new run-program format.

## Risks / Trade-offs

- Handles could clutter the small Curta → show them only on hover/selection,
  use readable compact targets, and inspect the actual exported model.
- Pointer motion could be counted twice as a part moves → prove the signed
  displacement planner against committed frames and camera changes.
- A composed axis might look correct only at rest → include non-parallel
  joints, an off-centre pivot and moving ancestors in pure-math and browser
  tests, using documents exported by the paired producer.
- A viewer-only fixture could conceal a producer mismatch → regenerate the
  fixtures from the exact framework content commit and record both commits.

## Migration Plan

After ratification, prove the current reader/gesture failures red, implement
the reader and pure planner, then connect actual pointer handling. Preserve
existing press/turn and run-worker tests. Build the public bundle and test its
reported controls using real browser gestures. Test both standalone and the
normal hosted viewer path; do not introduce a Curta-only page to satisfy them.

Consume the paired framework fixtures before the Curta migration relies on
the feature. Complete the Curta acceptance checks in the project and record
them as originating-project evidence, without folding its source into this
repository. Update the ADR index and README/changelog accurately, sync and
archive this repository's change. No push, release or publication is implied.
Rollback is restoring the previous paired package content and model; there
is no persisted-data migration.

## Open Questions

If actual-model pointer tests reveal that the chosen handles cannot expose the required freedoms,
return the evidence and proposed interaction revision before substituting a
different control design.
