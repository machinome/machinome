# Markings: what a part carries but is not made of

Status: design note, **not ratified, not implemented, not a public API
promise**. Date: 2026-09-15. Written at the pilot's request from a finding in
`projects/Calculators`, recorded in `../warts.md` under *Calculators
(2026-09-15)*, so that another agent can take the work up under
`libresolid-studio/skills/framework-change/SKILL.md`. Every name below is a
placeholder for the pilot to rename. Nothing in any repository is changed by
this document, and where it and a baseline spec or an accepted ADR disagree,
the spec and the ADR are right and this note is stale.

## 1. The finding

A Curta Type I is a calculator. Its answer is read off the number rolls: ten
printed cylinders, each showing one of the digits 0-9 through a window in the
digits cover. The register value *is* the angular position of those rolls.

In `projects/Calculators/Curta-Type-I-3x` the rolls are modelled — they are
`ResultsDialType1` / `ResultsDialType2` from the source STEP, fitted as
`FittedDialType1` / `FittedDialType2` in `simulation/dial_fits.py`, each on a
`Revolute` in `simulation/registers.py`, each carrying the register value
through its port. The kinematics are there. The digits are not, because the
standard CAD has none: they are not on the part when it comes off the printer.

Upstream supplies them three separate ways, and the three ways are the whole
design problem:

- **Painted or vinyl.** `Manual/Painting/` holds eleven DXF files —
  `5mm digits.dxf`, `results dial.dxf`, `Input Digits.dxf`,
  `upper outer sleeve-cricut.dxf`, `reversing lever arrows.dxf`, and others.
  `Drawings/` holds the same artwork as SVG, and `Drawings/cricut-images/`
  as high-resolution PNG with a sizing table for Cricut Design Space. The
  maker cuts or masks the artwork and applies it to the finished part.
- **Co-printed.** `Mods/Printed Lettering/` is an optional variant supplying,
  for each lettered part, the body STL *plus one STL per glyph*: `results dial
  - digit 0.stl` through `digit 9.stl`, `upper housing - digit 1.stl` through
  `digit 11-2.stl` (a two-digit number is two glyph bodies), `upper outer
  sleeve - A/C/R/T/U` and two arrow STLs, and the reversing arrows and centre
  dot for the lower housing. Beside each set sits a `.3mf` — `mmu results dial
  type 1.3mf`, `mmu upper housing.3mf` — grouping body and glyphs as one
  object for a multi-material printer.
- **Not at all**, which is what a maker who skips the mod and the painting
  gets, and what the model currently shows.

The same shape appears in `projects/Calculators/Pascaline-module`, whose
`DigitDrum` (`simulation/parts.py`) is one `StlNode` with one colour turning
`DIGIT_STEP` degrees per entered digit.

Read the `Mods/Printed Lettering/dials/` listing and the concept is already
stated by the file names: **one part, several colour bodies, one manufacturing
unit.** 3MF says it natively. solid-node cannot say it at all.

The cost is not cosmetic. A Curta model that computes its register value
**cannot display it**. Drive the crank in the browser and the machine gives no
answer, which for a calculator is the one thing it is for. The same hole eats
every dial face, index mark, scale, warning label and part number in the
catalogue.

## 2. What the framework can say today, and what it costs

`color` is one class attribute per node, defaulting to `None`
(`solid_node/node/base.py:569`), validated to a single `#RRGGBB` and applied
whole-node in `_colorize` (`base.py:1002-1010`). It reaches the document as
one scalar field (`solid_node/core/serializer.py:645`) and the viewer resolves
it to exactly one `MeshStandardMaterial` per mesh
(`solid-node-viewer`, `solid_node_viewer/widget/src/tree.ts:55,106`). There is
no vocabulary for a region of a part anywhere in that chain, and none for a
finishing step.

So a project has two options and both are wrong:

1. **Model each glyph as its own leaf.** The tree gains ten "parts" that no
   maker ever handles separately; each carries volume, and — once 0.8 makes
   mass follow from process and material — mass; and every clearance,
   interference and disconnected-solid contract sees solids that in the
   painted build do not exist. The model lies about the bill of materials to
   buy a picture.
2. **Drop the markings.** What both Curta and Pascaline did. The model is
   honest and mute.

## 3. The concept

Add a declared, first-class, **non-solid** surface feature on a leaf:

    class FittedDialType1(ClearingGearFit, ResultsDialType1):
        digits = Marking(
            artwork=Dxf(PAINTING / 'results dial.dxf'),
            onto=Wrapped(axis=Z, radius=10.5, at=(0, 0, 18.45)),
            color=WHITE,
            process=painted,
        )

Four properties make it worth having.

**It has no volume.** A marking never enters a boolean, a bounds, a volume, a
mass, a clearance or an interference contract, and never appears in the part
inventory. It is an annotation on a leaf, not a fourth geometry kind beside
rigid and flexible. This single rule is what the split-into-leaves workaround
breaks, and it is the invariant the cycle must defend with tests.

**It moves for free.** A marking is on a part; the part stands at its joint
coordinate. Turn the roll and the digit at the window is the digit the register
reads. Nothing is needed from the motion layer — the marking inherits the
part's placement exactly as everything else on the part does.

**It is a manufacturing output.** `painted` or `vinyl` emits the artwork flat,
at model scale, in the part's own frame: literally the file the maker feeds a
cutter, which upstream had to draw by hand — and note that
`upper_housing_numbers.png` is sized by *width*, 224.8 mm, because it is an
unwrapped circumference. `coprinted` emits body and glyphs as a
multi-material 3MF, which is what `Mods/Printed Lettering` hand-assembled.
There is a precedent for a per-part nominal 2D artifact in
`solid_node/node/adapters/build123d_sheet.py`, whose `_export_dxf` writes the
authored profile at model scale with no kerf on the stated ground that
"compensation is a property of a machine and a material, not of the part".
A marking's artwork is nominal for the same reason.

**It is the natural seat for 0.8's finish vocabulary.** `roadmap.md` has
process and material arriving in 0.8 so that mass follows from them. A marking
is a post-process step on a part whose process is by then already declared —
the same slot, and it keeps finishing from being invented separately later.

## 4. The invariants

Whatever the declaration ends up looking like, these are the properties that
make it honest, and each deserves a red test before the code that satisfies it:

1. A marking contributes no solid. `assertNoIntersectingSolids`,
   `assertNoDisconnectedSolids`, the volume of the part, and every pairwise
   sweep behave identically whether the part declares markings or not, faceted
   and exact alike.
2. A marking is not a child. It does not appear in `children`, is not a node,
   is not selectable as a part in the navigator's inventory, and does not
   change the part count of an assembly.
3. A marking does not change artifact identity for the *solid*. Editing the
   artwork must rebuild whatever the marking itself produces without
   invalidating the part's STL/BREP — or, if that proves impossible, the
   decision to invalidate must be deliberate and recorded, not incidental.
4. A marking is in the part's own frame, timeless and placement-free, in the
   same sense `base.py` already requires of a leaf's geometry. An assembly's
   rigid placement carries it.
5. A part with no markings produces a byte-identical document to today's.

## 5. Placement: two cases, not a general projection

Do **not** build surface parameterisation. Two placements cover every marking
in the catalogue:

- **`Wrapped`** — a cylindrical wrap: axis, radius, height along the axis,
  angular origin, and an angular pitch when the artwork repeats. This is every
  number roll, dial, drum, selector top and sleeve in the Curta and the
  Pascaline, and it is exactly what the flat DXF already assumes.
- **`Flat`** — a plane with an origin and orientation. This is a badge, a
  plate label, a part number, the reversing arrows on a housing face.

"Project this artwork onto that arbitrary face" is a later extension and is
not a prerequisite for anything above. Say so in the proposal so nobody builds
it first.

## 6. Artwork sources

Cheapest honest first cut: **imported vector art**, reduced to planar faces —
the same reduction `Build123dSheetNode` already performs on an authored
profile. DXF and SVG both, since upstream ships both.

`Text('0123456789', font=...)` is the obvious second source and is deliberately
*not* in the first cut: a font makes geometry non-reproducible across machines,
and every marking in the catalogue already exists as a file. If the pilot wants
text, it wants its own cycle and an explicit answer on font provenance.

## 7. The document and the viewer

This is two changes in two repositories — the framework's and the viewer's —
and the contract between them is specified on both sides, as with
`solid_node.viewer` and `solid-node-viewer describe|serve|capture`.

**Framework side.** A rigid node's document entry gains a `markings` field:
absent, or a list, each entry naming its artwork reference, its placement, its
colour and its process. That is a non-additive bump in the ladder at
`serializer.py:84-114` if a consumer that ignores it would render the part
wrongly — and it would not, since ignoring a marking yields exactly today's
picture. On that reasoning it is **additive**, and the version rule there is
that the version is a property of the content: a document with no marking stays
byte-identical to version 5. The proposal must settle this explicitly rather
than assume it.

**Viewer side.** Two routes, and the first cut should take the second:

- *Texture.* Rasterise the artwork and UV-map it onto the surface. Correct,
  cheap at frame rate, and needs UV coordinates the pipeline does not produce.
- *Decal mesh.* Emit each marking as its own thin mesh, offset from the surface
  by a small rendering constant, with its own colour, flagged in the document
  so it is drawn but excluded from every contract and from the part inventory.
  This reuses the entire existing rigid-mesh path — `loadMesh`, the material,
  the placement, the reloader — and needs no texture work at all. The offset is
  a rendering constant, not a claim about the part, and the note should say so
  where a reader might mistake it for geometry.

Texture-mapping is the better answer eventually. It is not the first answer.

## 8. Staging

Three cycles, in this order, each in its own repository:

1. **Framework: the declaration and the document.** `Marking`, `Wrapped`,
   `Flat`, DXF/SVG artwork, the five invariants of §4 proved red first, and the
   document field. No export, no text, no projection.
2. **Viewer: draw it.** Decal meshes from the document field, excluded from the
   navigator's inventory and from any measurement the viewer reports. A viewer
   API version bump.
3. **Framework, with or after 0.8: the process and the artifact.** `painted` /
   `vinyl` writing a nominal flat DXF per marking — unwrapped for a `Wrapped`
   placement — and `coprinted` writing a multi-material 3MF grouping body and
   glyph bodies. This is where the finish vocabulary joins the process and
   material declaration, and it is the half that genuinely belongs to 0.8.

Cycles 1 and 2 pay for themselves before 0.8: they are what makes the Curta
and the Pascaline readable in the browser.

## 9. Decisions held for the pilot

These are product and architecture calls, not implementation details, and the
agent taking this up should bring them back rather than settle them:

- **Does a marking ever become geometry?** An `engraved` marking is a cut: it
  changes the solid and belongs in the part's own render, not here. But
  `coprinted` blurs the line — an MMU glyph body *is* geometry that belongs to
  the same part. The position taken above is that `coprinted` still declares no
  solid in the model and affects only the export. That decides whether a
  marking can ever collide with anything, so it is the pilot's call.
- **Non-additive or additive document bump** (§7), if the analysis there is
  wrong.
- **Whether text-from-font is ever a source** (§6), and if so whose font.
- **Whether a marking may be driven independently of its part.** Nothing in the
  catalogue needs it; a flip-dot or split-flap display would.

## 10. What this note does not claim

It does not claim the Curta's or the Pascaline's source meshes carry or lack
engraved digits — only that the standard CAD has none and that each model node
can express exactly one colour. It does not claim any of this is in 0.7 scope.
It proposes no schedule. It has not been checked against the viewer's ratified
specs beyond the two source lines cited, and the version analysis in §7 is
reasoning, not a ratified conclusion.
