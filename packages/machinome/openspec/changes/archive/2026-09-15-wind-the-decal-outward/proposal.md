## Why

The viewer cycle `draw-what-a-part-carries` (`solid-node-viewer`, branch
`draw-markings`) lifts every decal vertex along its own vertex normal by
`MARKING_LIFT = 0.15 mm` so the decal clears the surface it lies on instead of
z-fighting with it. Its own design says, in "What the lift assumes of the
producer", that the direction of that lift "relies on a property the
framework's export spec does not yet promise: that a decal's triangles wind so
their normal points AWAY from the part", and records the property as
**observed, not promised**. A producer that ever wound a decal the other way
would make the viewer lift it **into** the part — the exact artefact the lift
exists to remove, at 1.5× the framework's own tessellation tolerance, and with
no error anywhere.

The property does hold today, and measurement says so. Every face of the
Curta's `results_dial.svg`, `upper_housing_numbers.svg` and
`reversing_lever_arrows.svg`, and of the fixture's `label.svg` and
`decals/badge.svg`, comes back with normal `+Z` and `+Z` winding; the
fixture's wrapped decals measure mean `dot(face normal, radial)` = 0.99947
(`Dial.digits`) and 0.99907 (`Plate.band`), and the flat `Plate.badge`
measures exactly `+1.0` against its declared normal.

What the finding got slightly wrong is *why* it holds, and the correction is
the argument for this change rather than against it. It is not an accident of
OCCT: `ocpsvg`'s `ensure_face_normal_up` (`ocpsvg/ocp.py:197-203`, ocpsvg
0.5.0) explicitly reverses any imported SVG face whose surface normal has
`Z < 0`, and `build123d.import_svg` yields exactly those faces. So the
framework's promise rests on an implementation detail of an **undeclared
transitive dependency** — build123d 0.10.0 pulls ocpsvg, solid-node pins
neither, nothing in solid-node names the behaviour, and no test would notice
if it went away. Meanwhile the framework's own placement maths already does
the other half of the job correctly and deliberately: `Flat` builds
`ŷ = n̂ × x̂` so `x̂ × ŷ = n̂`, and `Wrapped` maps artwork `(û, v̂)` to
`(θ̂, â)` whose cross product is the outward radial direction. Artwork `+Z`
is mapped outward **by design**; only the artwork's own `+Z` is borrowed.

So the fix is small and the promise is cheap: orient the artwork to `+Z` in
the producer, and write down what the artifact guarantees. Measured on all
three fixture decals, the orientation step is **byte-for-byte a no-op** on
correctly oriented input and produces byte-identical output from deliberately
reversed input.

## What Changes

- The `export` spec's "Manifest contract" and the `markings` spec's "A marking
  is built as its own artifact beside the part" each gain a **winding
  promise**: a marking artifact's triangles SHALL wind so their normal points
  **away from the part** — radially outward from the wrap axis for `Wrapped`,
  along the declared `normal` for `Flat` — whatever orientation the drawing
  tool gave the faces the artwork was read from. A consumer may therefore
  offset, lift or light a decal along its own normals without inspecting the
  part.
- `Svg.tessellate()` orients every artwork face to `+Z` before meshing it
  (`face.normal_at().Z < 0` → the complemented face), so the winding becomes a
  property of **this producer** and not of the drawing tool or of a transitive
  dependency's fix-up pass.
- A non-positive `Svg(scale=…)` is refused at the declaration. A negative
  scale mirrors the artwork, which reverses the winding of every triangle
  after the faces were oriented, and produces a decal whose glyphs are
  backwards; it is the one remaining way to defeat the promise from a
  project's own class body, and it is a mistake, not a unit conversion.
  (Beyond the finding; see `design.md` D3. Severable from the rest of this
  cycle.)
- No change to placement maths, to artifact naming or location, to the marking
  artifact's currency, sources or **producer recipe**, or to the published
  document. `marking-svg-v1:<tolerance>` stays `v1`: see `design.md` D4.
- Documentation: one paragraph under "What the build writes" in
  `docs/markings.rst`, and a `HISTORY.rst` note folded into the Unreleased
  marking entry.

### Out of scope, recorded so it is not read into this change

- **Publishing the decal's tessellation tolerance in the manifest.** The
  viewer's own residual — a part declaring `linear_deflection` above
  `MARKING_LIFT` may still punch through — is a magnitude question and this
  change is a direction question. The viewer's design already names publishing
  the tolerance, or lifting in the producer, as the two candidate remedies;
  neither is decided here and neither is blocked by this change.
- **Lifting the decal in the producer.** D5 of ADR-120 is unchanged: the
  artifact sits on the nominal surface with no offset, and any separation is
  the renderer's constant. This change makes the *direction* of that
  renderer's constant well defined; it does not move the surface.
- **Any change to the viewer.** The viewer cycle is a separate repository and
  a separate change. It already tests the direction by name and does not wait
  on this; after this change its test is checking a promise instead of an
  observation.
- **A general winding rule for the framework's other meshes.** STL, BREP and
  the faceted fusion mesh are closed solids whose orientation is the mesh
  engine's business. A marking artifact is the framework's only **open sheet**,
  which is the whole reason it needs a stated side.

## Capabilities

### New Capabilities

<!-- None: this change promises a property of an existing artifact. -->

### Modified Capabilities

- `export`: MODIFIED "Manifest contract" — the winding of a published marking
  artifact is promised, so a consumer may use a decal's own normals as an
  outward direction. Every existing paragraph and scenario is kept.
- `markings`: MODIFIED "A marking is built as its own artifact beside the
  part" — the artifact's triangles wind outward whatever the orientation of
  the faces read from the artwork; and MODIFIED "A marking's artwork is a
  declared drawing file" — a non-positive `scale` is refused.

## Impact

- **Changed code**: `solid_node/node/markings.py` — `Svg.tessellate()` orients
  each face before meshing; `Svg.__init__` refuses a non-positive `scale`.
  Nothing else. No new import: `build123d` is already imported inside
  `Svg.regions()`, and the orientation step needs only `Face` and
  `normal_at()`.
- **Dependencies**: none added, and one implicit dependency **removed** — the
  framework stops relying on `ocpsvg.ensure_face_normal_up` for a property it
  publishes.
- **Artifacts on disk**: none invalidated. No SVG reaching `import_svg` can
  produce a reversed face today, so no decal already built is wrong, and the
  producer recipe stays `marking-svg-v1`. Measured: all three fixture decals
  are byte-identical before and after the change (`Dial.digits` 22 484 B,
  `Plate.badge` 184 B, `Plate.band` 8 084 B).
- **Tests**: `tests/test_markings.py` gains a `WindingTest` — a wrapped decal's
  face normals dot its radial direction positively, a flat decal's dot its
  declared normal positively, both from artwork whose faces arrive reversed;
  and a byte-identity check pinning the no-op on correct input.
  `ArtworkReductionTest` gains the non-positive-scale refusal. No fixture SVG
  is added: a reversed face cannot be authored in SVG, which is itself the
  reason the red path is a seam (`design.md` D2).
- **Docs**: `docs/markings.rst`, `HISTORY.rst`.
- **Viewer**: none. The contract moves in the framework's favour; the viewer's
  `draw-what-a-part-carries` cycle needs no edit and may cite this once
  integrated.
- **No ADR.** ADR-120 already decided what a marking artifact is and that it
  sits on the nominal surface. This change states a conformance property of
  that artifact and changes no boundary, no interface and no architectural
  option; there is nothing to record that ADR-120 plus the baseline specs do
  not already say. (ADR-120 is the highest accepted ADR at this cycle's base,
  main `3045600`.)
