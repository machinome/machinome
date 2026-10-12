## Why

The Curta-Type-I-3x operating-loop trial exports two `Turn` controls on one
visible clearing-ring leaf. One selects the ancestor clearing joint and the
other selects the leaf's independent deployment joint. The current viewer
rejects the document before mount because it treats every same-kind,
same-part pair as one ambiguous gesture, even though the selected joints
and the existing named-handle UI distinguish these freedoms. The actual
26-control trial therefore cannot be operated in its exported page.

## What Changes

- Accept multiple `Turn` declarations on one part only when each selects a
  different validated joint path. Keep the load-time refusal for duplicate
  turns selecting the same joint, including declarations with different
  names, inputs or coordinates, and keep the existing malformed-control
  refusals.
- Present both freedoms through the viewer's existing separately named
  selected handles. A body drag with two freedoms remains inert; choosing a
  handle requests only its declared input about its declared joint. No
  inferred freedom, proxy part, new mount operation or document field is
  introduced. Keep selected handles stable as the pointer moves onto one:
  the actual trial showed that the next hover raycast can otherwise replace
  them with handles for a different part visible behind the overlay before
  pointerdown. Normal scene hover resumes off the handle.
- Prove the change first with a failing synthetic load/gesture test and
  then against the pinned Curta trial export, including real pointer
  gestures on both named handles and unchanged unrelated controls.
- Declare viewer API 27, because a host can require the new same-part
  multi-Turn capability even though the schema remains document version 13
  and no host operation or wire field changes. Record this post-release
  source capability in the owning compatibility/reference/changelog
  surfaces without rewriting the recorded 0.7.0/API-26 release or claiming
  a push or upload. An older API-26 bundle safely refuses the pair by name
  rather than operating it incorrectly. No new producer minimum-API field
  is inferred; the originating project must check for the tested API-27
  viewer bundle.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `viewer-package`: a valid same-part, same-kind pair can name distinct
  selected turn joints and must remain unambiguous through named handles;
  a duplicate selecting one joint still refuses.

- `user-documentation`: separate recorded 0.7.0/API-26 release facts from
  current-source API 27 for this capability, while keeping the existing
  document versions 1–13.

## Impact

The validation key in `partControls.ts`, its tests, and the existing
multi-freedom interaction tests are affected. `viewer.ts` needs only a
selected-handle hover guard: it already lists each control, builds a
separate handle for each selected freedom, and refuses to guess on an
ambiguous body drag. The actual producer's 26 controls, tree, and v13
wire are unchanged. The widget's single API declaration, reader-facing
compatibility/reference/changelog surfaces, and documentation version
tests are affected. The originating browser failure is the Curta trial's
`operating-loop-trial-pointers-01` report against export identity
`2b6b59dbb135bd0c0ced9ba87fcc8df9dc36588138d1b0294ce7b8543588df1b`.
