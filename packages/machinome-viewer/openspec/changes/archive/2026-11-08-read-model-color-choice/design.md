## Context

This is the viewer half of core `color-model-lamps`, from the actual Enigma lamp finding. That record audits the current static color, marking, source-CAD and host-highlight alternatives and recommends the proposed public helper. Both records share clean base `6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9` in managed `illuminate-model-lamps`; both remain planning-only pending their planning commit; the capture predecessor has integrated. The pilot’s active completion goal grants advance apply and local integration authority; the coordinating agent reviewed both full plans. No human review of the finished text is claimed and no installed environment has changed.

The existing material path is narrow: `ManifestNode.color` is string/null; `WidgetTree` inherits color and constructs one material per mesh; `update` evaluates placements and flexible shapes but not color; static `reconcile` replaces/repaints colors only when a new document arrives. `viewer.ts` loads clocked content when version is 8 or a `clocked` key exists, otherwise infers a program from `version >= 5`. `capture.py` has related classification predicates. A version-14 posed document therefore needs explicit content-aware classification, not merely an appended supported number.

Accepted ADR-076 gives `MaterialPresentation` sole ownership of base/hover/highlight composition. A base copied before a color change would otherwise restore an obsolete dark/lit state when the overlay leaves. The new state choice must join that owner, not add a writer or host callback.

## Goals / Non-Goals

**Goals:** Read exactly the producer's two-color choice; same geometry/body; ordinary controls and standing-state reset/restore/replay; no stale base color under overlays; explicit refusal by older readers; unchanged static documents and public handle types.

**Non-Goals:** No emission/brightness physics, generic material API, new UI, host shader callback, new electrical state, extra bodies or geometry fetch per color change. No new integration/snapshot semantics for the physical running executor.

## Decisions

1. **Validate one new wire form.** At version 14, `color` can retain its legacy string/null or carry exactly `{when: expression, on: hex, off: hex}`. Both colors use the existing six-digit node-color contract; both are checked at load even when one is not currently selected. The predicate is read through existing expression/binding/qualified-scope validation. Unknown keys/shapes, missing fields and undeclared inputs refuse before attaching the incoming document. A choice in a document claiming an older version is malformed and refuses rather than slipping through a static-color reader.

2. **Resolve from the current scope.** Finite zero selects off; finite nonzero selects on, exactly as the native helper. Include the condition in binding closure and changed-input dependencies. An uncolored child inherits the nearest declared color specification; its own static or conditional declaration overrides it, and marking colors remain their own. A shared ancestor choice changes only the descendants that inherit it. The effective `assembly().color` stays string/null and describes the current selected color, preserving the host type. Initial mount resolves the authored default bank before any visible frame; no transient off-colored flash is accepted when the default is on.

3. **Prepare before material publication.** Extend the existing pose preparation boundary so evaluated conditional colors are validated before any live base color or transform is changed. A later invalid condition cannot recolor an earlier sibling. In a clocked request, the existing pose-before-bank hook then preserves bank/events/pose/materials on refusal; restore behaves the same. Posed and running updates retain their existing input/physical-bank ownership: a color condition is not a new mechanical stop or a worker-side integration law. A presentation evaluation failure leaves standing materials intact through the existing refusal surface; this cycle does not invent rollback of already committed running ticks or new interior evaluations.

4. **Rebase the existing owner.** Update the material's declared base color through `MaterialPresentation` and recompute its currently active hover/highlight/dim/ghost overlays from that base. Do not save the currently highlighted material as a new base or replace/refetch geometry to show another color. Preserve existing material types and ownership wherever possible. Clearing all overlays, then restoring a bank, must reveal precisely that bank's selected base color. No three.js object crosses the public handle.

5. **Version by content, execution kind by payload.** Advertise API 30 and document versions 1–14. A version-14 document with `clocked` is clocked; one with `program` is running; one with neither is posed. Both payloads together remain invalid. Retain all existing version-1–13 behavior, including refusal of legacy versions that require a missing compiled machine. Update capture/runtime predicates consistently; no new top-level execution discriminator is introduced. Old API-29/readers supporting only 1–13 must refuse the new document before operation.

## Risks / Trade-offs

- Using a mutable overlay's visible color as the new base can leave a lamp permanently highlighted/dark → overlap color changes with hover/highlight and remove overlays in both orders.
- Adding 14 to the whitelist alone can misclassify a posed lamp as running → producer-owned posed/clocked/running fixture trio and capture classification tests.
- Candidate memo values can outlive a refusal → fresh whole-bank scopes and the existing evaluator pass semantics remain; prove independent-driver recovery and later valid recoloring without reset/remount. No global cache clearing is proposed.
- Asset replacement/reconcile can lose a current selected base → re-evaluate the current scope after normal replacement and preserve the owner/lifecycle rules; test no refetch for color-only changes and current color after same-document reload.
- Invalid presentation on a running bank can be confused with a physical constraint → retain the executor's established bank authority and test valid reset/restore/replay; promise atomic clocked admission, not a new running stop.

## Validation Plan

Use an authored minimal retained standard export, not a hand-edited document, as the fixture. Real official bundle/normal controls must show dark/lit/dark pixels on the same mesh with native expected colors. Check ordinary driver control changes, clocked state commits, running committed frames and native reset/restore/replay parity; no custom client logic may compute the lamp observation. Validate malformed/old-version choice data, initial powered default, inheritance/overrides, fixed markings, binding reuse, independent-input recovery, clocked invalid-condition rollback and overlays across a state change. Count model requests and ownership to prove no geometry replacement. Preserve all existing legacy fixtures byte-for-byte, typecheck, run focused/full widget and Python browser suites, and require actual browser execution for acceptance.

Then the originating project validates the 26 existing glass paths and its electrical oracle through its ordinary declared root in an isolated project worktree, with the canonical root/document untouched. Capture representative dark/lit/released images before expensive reachability queries; use images/native values and bounded visible-region checks, not private scene/material inspection as the only evidence. This is visual state selection only.

## Migration Plan / Ratification

Core and viewer halves are covered together by the pilot’s advance completion authorization and coordinating-agent review, with their ownership retained. Implementation starts only after the framework workflow's authority/validation/planning-commit gates. A source upgrade producing choice data needs the new reader; fallback to a static color is forbidden. No installed environment, Studio server, release version, publication or push changes during proposal preparation. An architectural decision record is extracted only after an approved implementation confirms the actual choices.

Planning validation (2026-11-07): supported `openspec status` reports 4/4 planning artifacts complete and `openspec validate read-model-color-choice --strict` passes from this owning package root. This is artifact validation only; no implementation, new runtime tests, dependency installation, planning commit or integration has occurred.


Base/authority gate (2026-11-08): the coordinating agent verified clean main
`6f07b083d3e9a4194d5f982ce200ae9dc6ffe4b9` after the capture cycle’s complete
local integration and authorized refreshing this existing cycle to that base.
The managed worktree fast-forwarded from its historical base without dropping
planning material. Both planning records are reviewed under the pilot’s
advance completion/local-integration authority and the Studio contract-sync
dependency is expressly included. The two-record planning-only commit is the
remaining gate before apply; the pilot-controlled installed environment is
not a validation target. Push, publication and contact remain unauthorized.
