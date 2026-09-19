# Evidence — wind the decal outward

Worktree `solid-node/WTs/decal-winding`, branch `decal-winding`, base main
`3045600`; planning commit `c31d393`. Proposed by an Opus agent, implemented
by a Sonnet agent, reviewed by the repository agent under the pilot's
delegation; run in parallel with the viewer cycle `draw-what-a-part-carries`
on the pilot's explicit instruction.

## The finding

The viewer lifts a decal along its own triangle normals. The direction relies
on the decal's triangles winding with their normal away from the part, which
the framework's export spec did not promise. Measured before proposing, on
`results_dial.svg`, `upper_housing_numbers.svg`, `reversing_lever_arrows.svg`
(Curta) and the fixture's `label.svg`: every face normal +Z, first-triangle
winding +Z; fixture decals mean dot(face normal, radial) 0.99947 (`digits`),
0.99907 (`band`); `badge` normal · (0, 0, 1) = 1.0. The proposer found why:
`ocpsvg 0.5.0` (`ocp.py:197-203`, `ensure_face_normal_up`) reverses any
imported SVG face whose normal is −Z — an undeclared, unpinned transitive
dependency two packages below solid-node. No SVG could be authored to defeat
it (clockwise paths, a mirror transform, arc circles all came back +Z), so the
only red path is substituting reversed faces at the `Svg.regions()` seam,
which is why the orientation lives in `Svg.tessellate()` (design D2).

## Red, then green

Before the producer change, `tests/test_markings.py`: `6 failed, 98 passed` —
`ValueError not raised` for `scale=-1.0` and `scale=0`; `np.False_ is not
true` for the wrapped decal, the flat decal and the wrapped decal on the
faceted part under reversed regions; a byte inequality for
"reversed artwork builds the same decal". `test_correct_artwork_is_untouched`
was green before the change, as the design requires (the fix is a no-op on
correct input).

After: `102 passed, 56 subtests passed` (implementer), and the reviewer's own
run of the same file `102 passed, 4 warnings, 56 subtests passed in 6.04s`.
`tests/test_sheet_leaf.py tests/test_export.py tests/test_node_lazy_exports.py`:
94 passed, 107 subtests. Implementer's full suite: `2875 passed, 4 skipped,
1585 subtests passed`.

## The no-op, measured

A cold rebuild of the three fixture decals matched the pinned hashes exactly:
`Dial.digits` 22484 B `bd3dacd344bd5050…`, `Plate.badge` 184 B
`ff24e82d90c28677…`, `Plate.band` 8084 B `e492ab49a5dbb307…`; a second build
left all three artifact mtimes unchanged, so nothing on disk is re-derived by
this change and the recipe stays `marking-svg-v1`.

## What changed

`Svg.tessellate()` orients each region to +Z (`face.normal_at().Z < 0` →
`Face(face.wrapped.Complemented())`) before meshing; `Svg.__init__` refuses a
non-positive `scale` with `ValueError`. `docs/markings.rst` states the
promise and the positive scale; `HISTORY.rst` folds one clause into the
marking entry. No ADR: a conformance promise on ADR-120, not a new decision.

- Reviewer's full suite on the archived content: `2875 passed, 4 skipped, 53 warnings, 1585 subtests passed in 337.29s`, exit 0.
