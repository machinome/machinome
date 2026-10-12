# Deterministic asset load order — implementation evidence

## Existing finding and pre-implementation red

The originating Leonardo `demo-incremental-source-grid` had two fresh cold
70-frame renders with identical inputs but one different model-geometry pixel:
frame 10 at (487, 262). Repeated poses within each mount were stable. This is
an integration symptom; the cause of that particular pixel is not yet proved.
Root's independent old-bundle two-STL diagnostic forced opposite network
completion orders and found two exact full-frame PNG hashes, blue overlap
`069361614c03ad12e160cdf1e77fbd4ff1547d2ae7db1b3407b6403d8442a2eb`
versus red overlap
`529fc85e7466dc46b25f5bc293303c8614b03a0fe3597f7348bc43a9908f31cb`.
Its scripts exited zero when merely reporting inequality, so they are not
represented as failed assertions. The root review records its preserved
reports and fixed old-bundle hash.

Before editing `tree.ts`, new deferred-loader tests in `tree.test.ts` failed
against the old source: `npm test --prefix machinome_viewer/widget --
src/tree.test.ts --maxWorkers=1` exited 1 with **five new failures and 56
existing passes**. Blue-first completion yielded sibling mesh IDs red 9,
blue 8; reverse completion of one model and two markings yielded IDs
`[15, 14, 13]` instead of document order `[13, 14, 15]`. A failed fetch
disposed zero reserved materials/placeholders; failed normal and decal
preparation disposed neither their returned geometry nor material. Assertions
that both sibling fetches began before either settled passed. The first unit
red run had four new failures; root requested tighter owned-resource checks
and a normal-preparation case, so the five-failure run is the final unit red
record. No runtime edit occurred between them.

The viewer-owned `tests/test_asset_load_order.py` was then run against the
old bundle **before runtime edits**. `python -m pytest
tests/test_asset_load_order.py -q` exited 1 at the actual exact-PNG assertion
`2 != 1`, with completion orders ABBA: red→blue, blue→red, blue→red,
red→blue. Five captures within each mount were byte-identical. The full PNG
SHA-256 sequence was blue hash, red hash, red hash, blue hash as above; center
pixels were `(30, 30, 204)` versus `(201, 30, 30)`. A no-store HTTP server
delayed one fixed STL URL by 200 ms, and the test asserted the completed
response order, so a failed reversal could not silently pass. The fixture
uses two identical coincident STL solids, fixed document, public Viewer API
28, viewpoint, pose, viewport and production SwiftShader flags. It imports
no Videomaker code.

## Scoped correction and green checks

`loadMesh` now reserves a placeholder geometry, policy-correct material and
mesh synchronously in document traversal, before awaiting STL bytes. It
prepares normals and swaps in the returned geometry before the established
ready-mesh attachment; requests remain concurrent and no blank mesh is
attached. A rejected fetch or normal preparation disposes that load's
placeholder, material and any returned geometry. `loadDecal` retains ADR-056
lift, polygon offset, double-sided material, own colour and ordinary depth,
and disposes its own mesh/material/geometry if decal preparation rejects.
`artifactChanged` and `prepareReconcile` were not changed; the pre-existing
aggregate cleanup of other successful/pending siblings remains out of scope.

Focused `tree.test.ts`: **61/61 passed** after the fix, including all five
new reds and existing targeted-update/marking containment tests. The rebuilt
worktree bundle SHA-256 is
`5280a86be7cbe532dabac8cfc99d4b78822275686c8f6fe1356c796148bcc413`.
The viewer-owned Python ABBA test passed exact PNG equality across four fresh
contexts and five repeated captures each. A separate differing-depth browser
test passed: a physically nearer green plate occluded the farther red plate
under both response orders, with exact PNG equality. The automated browser
tests were **2/2 passed** after the rebuilt bundle.

`npm run typecheck --prefix machinome_viewer/widget` passed. The bounded full
widget run, `npm test --prefix machinome_viewer/widget -- --maxWorkers=2`,
passed **1,670 tests, 2 skipped** across 62 passing files and one skipped
file. Relevant Python browser/capture/currency tests:
`python -m pytest tests/test_asset_load_order.py tests/test_widget_e2e.py
tests/test_capture.py tests/test_currency.py -q` passed **107 tests and four
subtests** in 81.25 seconds; 41 warnings were existing Pillow `getdata`
deprecations. No dependency install or distribution check ran through the
shared `node_modules` symlink.

## Held independent gates

Root reserved the independent repaired-bundle ABBA replay and Leonardo real
film checks for its own review and separate empirical worker. Thus tasks
3.1–3.4 are not marked complete here. The viewer-owned passing ABBA assertion
establishes the controlled defect is corrected, but it alone does not prove
that Leonardo's one pixel or either Videomaker cache comparison is repaired.
No visual tolerance was widened and no API, document or package version was
changed. No mechanical source/export, Videomaker runtime or main checkout was
edited, and this worktree has not been committed, synced or archived.

That was the implementation handoff state. Root subsequently passed the
independent ABBA replay and both real-film gates, including three 70-frame
cold mounts. The complete acceptance record and exact evidence paths are in
`root-review.md`; tasks 3.1–3.4 are now complete. This later closure does not
replace or reinterpret the pre-fix failures.
