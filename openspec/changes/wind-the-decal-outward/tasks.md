Red first throughout: every test in group 1 must be written and seen to FAIL
against the base producer, for the reason the test names, before group 2 makes
it pass. Run them with the workspace venv from inside this worktree:

    cd solid-node/WTs/decal-winding
    PYTHONPATH="$PWD" ../../../.venv/bin/python -m pytest tests/test_markings.py -x

## 1. The failing tests

- [ ] 1.1 In `tests/test_markings.py`, add a `reversed_regions` helper that
      patches `Svg.regions` to return
      `build123d.Face(face.wrapped.Complemented())` for each region the real
      method yields, restoring it in `addCleanup`. Real artwork geometry,
      really reversed, through the real `tessellate` / `place` /
      `mesh_bytes` path — this is the only way to reach the failure, because
      `ocpsvg.ensure_face_normal_up` means no SVG can express a reversed
      region (design D2, and the blind spot recorded in Risks).
- [ ] 1.2 Add a `face_normals(vertices, faces)` helper built on
      `trimesh.Trimesh(..., process=False).face_normals` and
      `.triangles_center`, beside the existing `loaded` and
      `cylinder_departure` helpers.
- [ ] 1.3 `WindingTest.test_a_wrapped_decal_faces_away_from_its_axis`: under
      1.1, build `markings_project.dial.Dial`'s `digits` surface at
      `DIAL_DEFLECTION` and assert every face normal's dot product with the
      outward radial direction at that triangle's centre is **positive**.
      RED: measured `-0.99947` mean, `-0.99625` max, i.e. every triangle
      faces into the drum.
- [ ] 1.4 `WindingTest.test_a_flat_decal_faces_along_its_declared_normal`:
      under 1.1, build `markings_project.plate.Plate`'s `badge` surface and
      assert every face normal dots the declared `(0, 0, 1)` positively.
      RED: measured `-1.0`.
- [ ] 1.5 `WindingTest.test_the_wrapped_decal_on_the_faceted_part_too`: the
      same assertion for `Plate.band` at the framework default 0.1, so the
      `StlNode` half of the fixture is covered as it is everywhere else in
      this file. RED: measured `-0.99907` mean.
- [ ] 1.6 `WindingTest.test_reversed_artwork_builds_the_same_decal`: assert
      the three decals' `mesh_bytes` under 1.1 equal their `mesh_bytes`
      without it — the spec's "byte for byte" clause. RED under 1.1: the
      index order differs.
- [ ] 1.7 `WindingTest.test_correct_artwork_is_untouched`: with NO patch,
      pin the three decals' byte lengths and sha256 prefixes — `Dial.digits`
      22484 / `bd3dacd344bd5050`, `Plate.badge` 184 / `ff24e82d90c28677`,
      `Plate.band` 8084 / `e492ab49a5dbb307` — so the fix is proved a no-op
      on correct input and not merely asserted to be. This one is GREEN
      before the change and must stay green after it; note that in the
      docstring so a later reader does not mistake it for a red-first test.
- [ ] 1.8 `test_the_marking_artifact_records_its_producer_recipe` in
      `MarkingRecipeTest` already pins `marking-svg-v1`; confirm it still
      names `v1` and leave it alone (design D4). No new test.
- [ ] 1.9 In `ArtworkReductionTest`, add
      `test_a_non_positive_scale_is_refused`: `Svg('label.svg', scale=-1.0)`
      and `scale=0` each raise `ValueError` naming the value. RED: both are
      accepted today, and a negative one silently mirrors the artwork.
      (Design D3 — severable with task 2.2 if the pilot cuts it.)
- [ ] 1.10 Run the file and record every failure message verbatim for the
      implementation commit's evidence.

## 2. The producer

- [ ] 2.1 In `Svg.tessellate` (`solid_node/node/markings.py`), orient each
      region before meshing it: `if face.normal_at().Z < 0: face =
      b3d.Face(face.wrapped.Complemented())`, with `import build123d as b3d`
      alongside the existing local `numpy` import. Extend the docstring to
      say the winding is this producer's property and not the drawing tool's,
      and why the placements make `+Z` the outward side.
- [ ] 2.2 In `Svg.__init__`, refuse a non-positive `scale` with `ValueError`
      naming the value, in the shape `Wrapped`'s `radius` refusal uses, and
      say in the message that a negative scale mirrors the artwork. Update
      the class docstring's `scale` paragraph.
- [ ] 2.3 Re-run `tests/test_markings.py`: group 1 green, nothing else moved.

## 3. Proof beyond the new tests

- [ ] 3.1 Run the whole `tests/test_markings.py` file and confirm every
      pre-existing test still passes — in particular `MarkingRecipeTest`,
      `SeparateCurrencyTest`, `ByteIdentityTest` and `ArtworkReductionTest`'s
      `test_the_closed_regions_become_faces_with_their_holes_nested`, which
      reads `regions()` directly and must be unaffected by a change made in
      its caller.
- [ ] 3.2 Run `tests/test_sheet_leaf.py`, `tests/test_export.py` and
      `tests/test_node_lazy_exports.py` — the other users of build123d and
      of the marking's document path — and then the full suite.
- [ ] 3.3 Rebuild the fixture decals from a cold build directory and confirm
      the three artifacts' bytes match the hashes pinned in 1.7, proving the
      no-op holds through `_prepare` and the artifact lifecycle and not only
      through `mesh_bytes`.
- [ ] 3.4 Confirm no decal is re-derived by the change: build the fixture,
      note the artifact mtimes, apply nothing, build again, and confirm the
      recipe check leaves them alone (design D4).

## 4. Records

- [ ] 4.1 `docs/markings.rst`, "What the build writes": one paragraph saying
      the sheet's triangles wind away from the part — outward from the wrap
      axis, along the declared normal for a flat marking — whatever way the
      drawing tool wound the artwork, so a renderer can separate the decal
      from the surface without asking the part which side it is on. Keep the
      existing "no offset" sentence adjacent and unchanged; the two are the
      direction and the magnitude of the same thing.
- [ ] 4.2 `docs/markings.rst`, the `Svg` reference: `scale` is positive.
- [ ] 4.3 `HISTORY.rst`: fold one clause into the Unreleased marking entry —
      the decal's triangles wind away from the part, so a viewer can lift it
      clear without inspecting the part — rather than adding a second bullet
      for a property of a feature that has not shipped.
- [ ] 4.4 No ADR (design D5). No `workflow/` note (design, Open Questions).
      Both recorded as deliberate in the implementation commit message.
- [ ] 4.5 `openspec validate wind-the-decal-outward --type change --strict`,
      then sync the baseline specs and archive the change.
