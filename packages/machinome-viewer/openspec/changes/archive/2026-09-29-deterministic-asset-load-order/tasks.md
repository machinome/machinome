## 1. Red-first loading proof

- [x] 1.1 Add deferred-STL unit tests for two coincident sibling models resolving in AB and BA order; show current code reverses their relative mesh/material identity order and record the red result before implementation. Assert that both fetches start before either is resolved.
- [x] 1.2 Add red-first model-plus-multiple-marking completion-order tests, checking document-order placement, independent marking colours and existing marking lift/material properties.
- [x] 1.3 Add red-first local-ownership tests: observe a mesh/material reserved before its STL resolves, then make that fetch or decal preparation fail and assert that load discards its unready mesh and disposes its material and returned geometry without blank early attachment. Retain existing `artifactChanged` and `manifestChanged` failure-containment tests for the prior tree/camera; do not require cleanup of unrelated successful or pending sibling loads.
- [x] 1.4 Add a viewer-owned Python/Playwright regression for controlled ABBA captures: fresh mounts with reversed STL response order, five same-frame captures per mount, and an assertion of exact PNG equality. Run it against the old bundle before runtime edits and record the failing assertion and verified response orders. Preserve the independent diagnostic reports too; their scripts reported inequality but did not themselves exit nonzero for unequal pixels.

## 2. Narrow viewer correction

- [x] 2.1 Reserve rigid model and marking mesh/material identity in document traversal before asynchronous STL completion, leaving fetches concurrent and attaching only ready meshes. Preserve normal depth/geometry and ADR-056 marking lift, polygon offset, sides and own colour.
- [x] 2.2 Make each failed load discard only the unready mesh it newly reserved and dispose its material and any geometry returned to it; retain prepare-before-mutation and prior-live-tree failure containment on targeted replacements. Do not expand `viewer.ts` mount lifecycle or aggregate sibling/reconciliation cleanup without new evidence.
- [x] 2.3 Make the deferred-load tests green; add a differing-depth regression proving real occlusion is unchanged, and run widget tests and typecheck.

## 3. Exact browser and film verification

- [x] 3.1 Build the repaired bundle, pass the viewer-owned browser regression, and rerun the independent controlled ABBA browser capture with the same manifest, viewpoint, pose, viewport and delayed response protocol. Record bundle/browser hashes, actual response orders and all PNG hashes; require exact equality across ABBA mounts and all repeated captures, without specifying which coincident colour wins.
- [x] 3.2 With the repaired bundle pinned, repeat fresh cold captures of Leonardo's 70-frame `demo-incremental-source-grid` in separate browser mounts and compare every frame's PNG hash, explicitly checking frame 10 and pixel (487, 262). Preserve evidence of any residual mismatch rather than calling the root cause proven.
- [x] 3.3 Run the existing real 80-frame `demo-incremental-rendering` and 70-frame `demo-incremental-source-grid` cold-versus-incremental Videomaker checks at exact per-frame PNG equality; record source/film inputs, output configuration, viewer bundle hash and cache reuse/recapture observations. A failure blocks the corresponding cache proof and is not resolved by a tolerance change.
- [x] 3.4 Review the diff for unchanged API/document version, concurrent fetching, existing targeted-update behavior and absence of universal `renderOrder`/depth/geometry workaround; report the bounded conclusion and any unresolved real-film difference to the root reviewer before completion.
