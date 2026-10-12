# Evidence — draw what a part carries

Worktree `solid-node-viewer/WTs/draw-markings`, branch `draw-markings`, base
main `4cfa251`; planning commit `4ab3b87` (amended once after implementation
to ratify the weld and the second pixel probe, both recorded in design D3 and
D12). Proposed by an Opus agent, revised by a Sonnet agent after review,
implemented by an Opus agent, reviewed by the repository agent under the
pilot's delegation. Consumes solid-node ADR-120 (`carry-markings-on-a-part`,
main 8d29cf5) and the follow-up `wind-the-decal-outward` (branch
`decal-winding`, 5647948) that promises the decal winding the lift relies on.

## Design evidence, before proposing

- Ray-cast through all 448 facets of the fixture dial's decal against the
  part's own tessellation: 77.2 % of decal facets lie behind the part's
  surface, median 0.0045 mm, worst 0.0203 mm — a world-space interpenetration
  of two chordal approximations, not a coplanar z-fight; `polygonOffset` units
  are depth-buffer steps (~3e-4 mm per unit at that framing, camera-dependent).
- Bound derived at review: the decal is subdivided to the part's tolerance `t`
  and chords sag inward, so interpenetration ≤ `t` (0.1 mm at the framework
  default); `MARKING_LIFT = 0.15` mm covers every part declaring none and up
  to 0.15. A part declaring more is a framework finding, not a viewer knob.
- Winding: every face of the Curta's three drawings and the fixture's artwork
  is +Z with +Z winding; fixture decals mean dot(normal, radial) 0.999. The
  framework follow-up promises it.

## Red, per task group (implementer)

- **1 Fixture.** `tests/markings_project/assembly.py:Bench` exported from
  solid-node main 3045600 and copied verbatim: `manifest.json` 2 700 B plus
  five STLs 56 520 B = 59 220 B (design D11 said 59 218; the export timestamp).
- **2 Refusal.** 9 red in `document.test.ts` ("expected [Function] to throw",
  two threw the undeclared-driver message instead); green with
  `ManifestMarking` and `assertMarkings` first in `assertRenderable`'s visit.
  The three "unchanged" pins passed from the start, as intended.
- **3 Drawing.** 8 red (no decal URLs fetched, no marking group,
  `MARKING_LIFT`/`liftAlongNormals` undefined), then one more: `applyVisibility`
  left an ancestor's decals drawn — the one line D2 predicted. `setColor` and
  `removeMesh` pins passed by construction.
- **4 Not a part.** Both pins passed by construction; proven able to fail by
  temporarily emitting a child per marking from `assembly()`
  (`['Bench','dial','digits',…]` vs `['Bench','dial','plate']`), then reverted.
- **5 Currency.** 10 red of 11; green with per-marking staleness in
  `prepareReconcile`, `applyMarkings`, `orderMarkings`, routing in
  `artifactChanged`, per-marking `freshFromArtifact`. `viewer.ts` needed no
  change: `rebuildPartControls`'s traverse reaches decal meshes (pinned).
- **6 Version.** `version.test.ts` red at 12 → 14; `package.json` one line.
  Python pins at 12 in `test_bundle.py`, `test_lock_document.py:245`,
  `test_running_document.py:195` moved to 14 (task 6.1 named the wrong file).
- **7 Pixels.** Bundle built in the worktree; e2e and capture proven red with
  a bundle whose marking load was disabled (`0 not greater than 100: the white
  markings were not drawn`; `4 not greater than 500: the photograph shows no
  marking`). `capture.py` needed no change (D10 confirmed; its diff is empty).
- **8 Record.** README, CHANGELOG, ADR-056 after green.

## Two deviations, ratified by amendment

1. **D12's near-white probe alone cannot see two of its four steps.** Measured
   over a 12 × 3 camera sweep: a `#FFFFFF` surface never exceeds 213–217 in
   its darkest channel; the dial's decal (horizontal normals, light from
   (1, −1, 2)) never passes 180; the `band` is `#C0C0C0`. A second probe of
   the same kind — neutral grey, which `MeshNormalMaterial` reaches only where
   |nx| = |ny| = |nz| — sees both: 4 369 marking pixels vs 6 on the twin;
   dial-only 2 171 px at angle 0 → 1 925 at 180, centroid moved 169 px.
2. **The lift tears an unwelded sheet.** Non-indexed STL corners lifted along
   their own facet normals separate by `2·0.15·sin(5.9°)` = 0.031 mm on the
   fixture's 11.8° facets — a visible grid at 30 mm, confirmed widening at
   0.60. Fixed by welding co-located corners and averaging normals before the
   lift (`liftDecal`); `MARKING_LIFT` stays 0.15. Residual 206 of 46 400 decal
   pixels (0.44 %) at 30 mm along long thin triangles, none at normal distance.

## Green

- Implementer: `npm run typecheck` clean; `npm test` 36 files, 806 tests
  passed; `pytest -q` 114 passed, 0 skipped (bundle, Chromium, Playwright,
  Pillow all present). One unreproducible flake noted in
  `RepublishedRunTest` during a run that also had the two API-version pins
  failing; passed alone and in every run since.
- Reviewer's own run: `npm run typecheck` clean; `npm test` 36 files, 806 tests
  passed; `pytest -q` `114 passed, 53 warnings in 105.95s`, exit 0.
