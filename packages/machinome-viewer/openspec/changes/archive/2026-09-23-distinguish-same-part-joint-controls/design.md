## Context

The pinned Curta operating-loop trial export is a v13 document with 26
controls. Both `clear registers` and `deploy loop (simulation-only mounting)`
name the visible leaf `carriage/registers/clearing_ring/clearing_ring` and
have kind `turn`; the former selects ancestor joint
`carriage/registers/clearing_ring` and its `.turn` coordinate, the latter
selects the leaf joint and its `.swivel` coordinate. Their validated
operation spans, axes and origins are different. The API-26 viewer refuses
the second declaration because `readControls` claims the pair `(kind,part)`.
The failed hosted report contains no pointer attempts because mount throws.

The gesture surface already has the behavior needed after a valid load:
`viewer.ts` maps every mesh to all controls at the deepest named part,
`partSurfaceWith` creates one named handle per motion freedom, and a body
drag with more than one freedom selects none. However real Chromium showed
that moving the pointer onto a clearing handle sets a pending hover cast;
the next `pollHover` raycasts the crank behind the overlay and replaces the
two clearing handles with crank handles before pointerdown. The failure
was captured after mount with zero outcomes and unchanged bank, not inferred
from a test stub. `lineOf` evaluates each
control's selected joint and operation span. The public `controls()` view
returns each declaration and a `gesturePoint` for its selected handle.

## Goals / Non-Goals

**Goals:**

- Load the actual two-Turn, one-part Curta declaration while preserving
  strict path, ancestry, coordinate, domain and operation-span validation.
- Let a maker select one of two clearly named joint handles and submit only
  that control's driver request through the existing run path. An undecided
  body drag submits no movement.
- Keep duplicate same-kind/same-part/same-joint declarations refused by
  name, regardless of differing labels or inputs. Keep same-kind Slide or
  Button duplicates refused as before.
- Give hosts an API-27 capability check for the new acceptance/interaction
  behavior while retaining document versions 1–13 and the v13 wire.

**Non-Goals:**

- No inferred control, proxy mesh, synthetic project part, new selection
  heuristic, arbitrary preference for one input, new mount or run operation,
  producer schema change, or generic acceptance of every duplicate kind.
- No change to gesture quantization, timing, outcome reporting, coordinate
  or solver semantics. No project source edit in this viewer cycle.

## Decisions

1. **Claim a turn by its selected joint, not merely by its part.** In
   `readControls`, a `Turn` claim is keyed by kind, exact part-name path
   and exact selected joint-name path. Other kinds retain kind+part. Use
   an unambiguous tuple encoding (e.g. JSON of those arrays), not a
   separator that a node name could contain. Preserve the existing
   per-entry validation order, then claim before adding the control. A
   duplicate error names both display names, the part and shared joint.
   Alternative: key by input or coordinate. Rejected because two different
   drivers may still target the same physical joint, leaving one bare
   gesture with two meanings; a distinct selected joint is the evidence
   that two handles can represent two freedoms.

2. **Reuse named multi-freedom handles; do not choose on the body.** The
   existing surface's `selected` list, button `data-control`, hover title,
   `gesturePoint`, and `lineOf` are the intended presentation path. A
   synthetic two-Turn test proved the handle gesture path itself works,
   but real hover found the overlay retarget bug. On `pointermove` over a
   current, owned, visible selected handle, suppress only the pending
   scene hover recast so the handle remains available for `pointerdown`.
   A pointer move back to the canvas or another element resumes ordinary
   nearest-visible-hit picking. A hidden, stale or foreign handle does not
   receive this exemption; pointerdown still verifies ownership and
   reachability.
   Alternative: infer a handle from pointer direction or choose the first
   entry. Rejected because it silently moves a different input depending
   on presentation or declaration order.

3. **Raise API, not document version.** The producer emits the ordinary
   v13 controls table with no new field. API 27 advertises that this viewer
   can mount and operate distinct selected Turn joints on one part. API 26
   rejects that table rather than making an incorrect movement. The
   producer has no minimum-viewer-API field, so this cycle does not invent
   one. The originating project pins/tests the API-27 bundle with its
   export before calling the gesture available.

4. **Keep release facts separate from current source.** `package.json`
   remains the single API declaration and changes to 27. The manual's
   recorded 0.7.0/API-26 home/README/release changelog stays historical;
   the compatibility page and CLI example distinguish source API 27 from
   that release. An Unreleased changelog section records the capability.
   Update the documentation test so it checks both facts, instead of
   assuming current source always equals the last release. No publication
   action or claim follows from building this branch.
   The existing user-documentation baseline spec still called the
   recorded 0.7.0 release API 25/document 1–12, despite the unchanged
   0.7.0 changelog and manual recording API 26/document 1–13. This cycle
   explicitly modifies that older documentation requirement to reconcile
   only those recorded facts while adding the post-release API-27
   requirement; it does not revise release artifacts or runtime semantics.

## Risks / Trade-offs

- **A stale viewer may be paired with a valid new export.** It refuses the
  table by name at load; the project/browser gate must pin the bundle/API
  actually used. The v13 number alone is insufficient as a capability
  check.
- **Two handles could render but target one input.** Synthetic pointer
  tests assert each named handle calls exactly its declared driver; actual
  hosted pointer tests assert both real controls and their separate bank
  effects. The body-drag negative proves no arbitrary fallback.
- **An overlay can cover another moving part.** The owned-handle hover
  guard prevents a ray through the overlay from changing the current
  selection, while canvas hover still checks the nearest visible hit.
- **Joint geometry could be mixed between ancestor and leaf.** Existing
  `operation_span` and `lineOf` validate and read each joint separately;
  the actual Curta pointer gate observes the resulting signs and outcomes.
- **Documentation substitutions could rewrite history.** A released-API
  constant for the historical note and source-derived API for current
  `describe`/compatibility keep them separate, with focused tests.

## Migration Plan

An old document or one-control part is unchanged. A producer-valid pair
previously refused by API 26 loads in API 27. Hosts that need this
capability check `apiVersion >= 27` and keep using `controls()` and
`gesturePoint` as before. No snapshot or document migration is required.
The branch is validated in isolation, archived, then reconciled with the
current viewer main; no push, upload or release is implied.

## Open Questions

None for the viewer plan. Actual source-model mechanical validity and any
project production adoption remain project-owned, separate from this
consumer acceptance test.
