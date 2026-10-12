## 1. The fixture

- [x] 1.1 Export the framework's marked fixture from the solid-node checkout —
  `PYTHONPATH="$PWD" solid export tests/markings_project/assembly.py:Bench -o
  <dir> --no-widget` — and commit it verbatim as
  `tests/fixtures/marked/`: `manifest.json` plus the five STLs under
  `models/markings_project/` (59 218 bytes; design D11). Nothing here edits it.
- [x] 1.2 Write `tests/fixtures/marked/README.md` in the shape the `lock`,
  `pascaline` and `touched` READMEs take: which framework fixture produced it,
  that the document and the artifacts are verbatim, that the part meshes are
  real (and why, design D11), the four facts the document settles — `version: 2`,
  two markings of different colours on `plate` in declaration order, a `null`
  part colour under a `#FFFFFF` decal, and a `band` decal at radius 12.0 outside
  the plate's ±10.0 box — and that nothing here regenerates it.
- [x] 1.3 Add `export_marked(target)` and `published_marked(target)` to
  `tests/support.py` beside `export_with_widget` / `published_build`, and a
  helper that writes the same document with every `markings` key stripped — the
  unmarked twin every "unchanged" assertion compares against, produced by the
  test and never committed.

## 2. Reading the document: types and refusal

- [x] 2.1 Red: extend `document.test.ts` with the refusals of design D6 — a
  `markings` that is not an array; an entry that is not an object, or whose
  `name` or `model` is not a non-empty string, or whose `color` is not
  `#RRGGBB`; a repeated `name` on one node; a `markings` on a node carrying
  `children` or `flexible` — each asserting the document, the node and the
  marking are named, and that a document with no `markings` key validates
  exactly as it did (assert against the stripped twin of the marked fixture).
- [x] 2.2 Add `ManifestMarking` to `types.ts` and `markings?: ManifestMarking[]`
  to `ManifestNode`, documented as the wire shape the producer publishes
  (solid-node's "Manifest contract"), and implement the validation inside
  `assertRenderable`'s existing per-node `visit` (`viewer.ts`), after the
  controls table and before the tree's expressions are walked. Green.

## 3. Drawing a decal

- [x] 3.1 Red: `tree.test.ts` — constructing a `WidgetTree` over a node
  carrying two markings loads one mesh per entry through the mocked STL loader,
  in document order, each with its own `materialForColor(entry.color)`; the
  meshes are inside the node's own group; a node with no `markings` adds no
  object at all (the scene graph is the one it has today).
- [x] 3.2 Red: the material carries `side: THREE.DoubleSide`,
  `polygonOffset: true`, `polygonOffsetFactor: -1`, `polygonOffsetUnits: -1`
  and writes depth; and each decal vertex is lifted `MARKING_LIFT = 0.15`
  along its own normal (design D3) — assert on a hand-built geometry whose
  normals are known, so the lift's direction and magnitude are both pinned.
  The hand-built geometry must wind outward the way the producer's does
  (design D3, "What the lift assumes of the producer"), and a second small
  assertion loads the committed fixture's wrapped decal and checks that its
  lifted vertices all moved to a LARGER radius, so a producer that ever
  flipped its winding fails here, by name, rather than drawing digits inside
  the roll.
- [x] 3.3 Implement in `tree.ts`: the lazily created marking group (design D2),
  a `markings` record array in document order, and `loadMarking` reusing
  `loadMesh` with the marking material. Green.
- [x] 3.4 Red then green: `applyVisibility` sets the marking group's own
  `visible` to `inFocusedSubtree` beside the direct meshes' — a part that is an
  ancestor of the focused root draws neither its surface nor its decals — and
  `setColor` and `removeMesh` leave a decal's material and geometry untouched
  (the two filters design D2 names).

## 4. A marking is not a part

- [x] 4.1 Red then green: `tree.test.ts` — `assembly()` over the marked fixture
  returns exactly the snapshot the stripped twin returns: same nodes, paths,
  colours and `model` flags, and no node per marking.
- [x] 4.2 Red then green: `navtree.test.ts` — `navigatorRows` over the marked
  fixture's assembly presents exactly the rows the stripped twin presents. Pin
  it even though `navigatorRows` walks `children` and cannot see a marking: "by
  construction" is a property of today's code (design D7).
- [x] 4.3 Red then green: hiding a marked part hides its decals and showing it
  restores them, driven through the same `setVisible` a host calls.

## 5. Reload on its own currency

- [x] 5.1 Red: `tree.test.ts` reconcile cases — a marking whose `mtime` moved is
  refetched and the node's model is not; a node whose model moved is refetched
  and its markings are not; a marking removed from the list is removed and
  disposed while the rest stand; a whole `markings` key removed drops the group;
  a marking added to a node that had none creates the group; a retained
  marking whose `color` moved has its material replaced with no refetch.
- [x] 5.2 Red: `artifactChanged(decalPath)` refetches that marking only, and the
  `reconcile` that follows — naming the new `mtime` for bytes already on screen
  — does not refetch it (the per-marking `freshFromArtifact` of design D5).
- [x] 5.3 Red: a decal fetch that rejects leaves the whole previously rendered
  scene intact and a later update still succeeds (`viewer-package`, "A failed
  update leaves the model standing").
- [x] 5.4 Implement the reconcile and `artifactChanged` routing in `tree.ts`
  (design D5: match by `name`, order by the document, fetch everything before
  the live tree is touched). Green.
- [x] 5.5 Confirm `viewer.ts`'s `artifactChanged` handler needs no change beyond
  what `tree.ts` now does — `partSurface.clear()`, `rebuildPartControls()` and
  `notifyAssemblyChange()` already run — and that `rebuildPartControls`'s
  traverse now includes decal meshes, so a decal on a touchable dial is
  pressable with it (design D2). Add the test that says so.

## 6. Version, and the declaration

- [x] 6.1 Red: `version.test.ts` and `tests/test_version.py` expect 14 from the
  package declaration, the bundle global, the mount handle and `describe`, with
  `documentVersions` still `[1, 2, 3, 4, 5]`.
- [x] 6.2 Set `solidNodeViewerApi` to 14 in
  `solid_node_viewer/widget/package.json` — that one line and nothing else in
  the file, because `slide-and-turn-parts` moves the same line to 13 and the
  conflict at integration should be one line wide (design D9). Green.

## 7. Pixels

- [x] 7.1 Build the bundle in THIS worktree —
  `cd solid_node_viewer/widget && npm run build` — never in the primary
  checkout, which is on another cycle's branch with uncommitted work.
- [x] 7.2 Red then green: a Playwright acceptance in `tests/test_widget_e2e.py`
  over `export_marked` (design D12): near-white pixels are many on the marked
  document and none on the stripped twin; every pixel that is not near-white is
  unchanged between the two; and after `setDriver('angle', 180)` the near-white
  pixels are still present and their centroid has moved — the decal turning with
  its part. Justify the near-white threshold in the test from
  `MeshNormalMaterial`'s own ceiling of 201 (design D12), so the probe is one
  the part provably cannot trip.
- [x] 7.3 Red then green: a capture test in `tests/test_capture.py` over
  `published_marked`, asserting the photograph shows the marking's colour where
  the marking is and the part's where it is not, and that the stripped twin's
  photograph does not. Record whether `capture.py` needed any change at all —
  design D10 predicts none.
- [x] 7.4 Inspect the pixels. If any part punches through its own decal, record
  the measurement and file it as a framework finding (design D3's residual —
  the part declares a `linear_deflection` above 0.15 mm) rather than quietly
  enlarging `MARKING_LIFT`.

## 8. Validation and the record

- [x] 8.1 `cd solid_node_viewer/widget && npm run typecheck && npm test` — the
  whole widget suite, including the running corpus and the parity fixture,
  which this cycle must not move.
- [x] 8.2 `/home/asa/devel/libresolid-studio/.venv/bin/python -m pytest` from the
  worktree root, after 7.1 (`tests/support.py`'s `needs_bundle` skips on a
  bundle that was never built, so an unbuilt bundle silently skips the e2e).
  Report honestly anything the environment skips.
- [x] 8.3 README: a "What a part carries" section under the reading/driving
  sections — what a marking is, that it is drawn in the part's own place in its
  own colour, that it is no part (no row, no readback, no focus or visibility
  target of its own), that it reloads on its own currency, and that the
  anti-z-fighting bias is the viewer's constant and not a claim about the part.
  Move the "Versions" table's 0.2.0 row to API 14, noting that
  `slide-and-turn-parts` moves the same row to 13 and integration reconciles it.
- [x] 8.4 `CHANGELOG.md`: an entry under `0.2.0 — unreleased` in the voice of
  its neighbours — the Curta and the Pascaline become readable, the decal-mesh
  route and why not a texture, the marking that is not a part, the currency
  split, the API rising to 14, and the framework change it consumes
  (solid-node ADR-120, `carry-markings-on-a-part`).
- [x] 8.5 Write the ADR **after** implementation, in `docs/adrs/EXPORT/` (the
  document-consumption decisions live there), at the next free number at that
  moment — ADR-054 is the highest committed here and `slide-and-turn-parts` may
  take 055, so plan on **ADR-056 and re-check before writing**. It records the
  decision "a marking is drawn as a decal mesh inside the part's own group, and
  the anti-z-fighting bias is the viewer's rendering constant", cites
  solid-node ADR-120 as the producer contract it consumes, and extends ADR-035.
  Add its row to `docs/adrs/README.md`, preserving the table's order.
- [ ] 8.6 Sync the delta specs into `openspec/specs/`, archive this change, and
  commit the completed implementation record. Nothing is pushed and nothing is
  published; both are the pilot's explicit decision.
