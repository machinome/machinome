## Why

A Curta is a calculator whose answer is the angular position of ten printed
number rolls. `projects/Calculators/Curta-Type-I-3x` models and drives every
one of them — `FittedDialType1`/`FittedDialType2` in `simulation/dial_fits.py`,
each on a `Revolute` in `simulation/registers.py`, each carrying its register
digit through its port — so the register value is computed correctly and is
**unreadable**, because the digits are not on the part.
`projects/Calculators/Pascaline-module` has the same hole: its `DigitDrum`
(`simulation/parts.py`) is one `StlNode` with one colour turning `DIGIT_STEP`
degrees per entered digit and showing nothing. Drive either crank in the
browser and the machine gives no answer, which for a calculator is the one
thing it is for.

The finding is recorded in `workflow/warts.md`, "# Calculators (2026-09-15,
markings applied after the part is made)", and the design note this change
implements is `workflow/docs/markings.md`. The limit is one line wide: `color`
is a single class attribute per node (`solid_node/node/base.py:569`), validated
to one `#RRGGBB` and applied whole-node (`_colorize`, `base.py:1002-1010`),
published as one scalar (`solid_node/core/serializer.py:645`). Nothing in that
chain names a **region** of a part. A project that wants digits on a roll must
either declare each glyph as its own leaf — which invents parts no maker
handles, gives them volume, and puts phantom solids in front of every
clearance, interference and disconnected-solid contract — or drop the markings.
Both calculators dropped them, and the same gap eats every dial face, index
mark, scale, warning label and part number in the catalogue.

Upstream already states the concept the framework is missing. The Curta ships
its markings as cut artwork (`Manual/Painting/`, eleven DXF; `Drawings/`, the
same as SVG), as a co-printed multi-material variant (`Mods/Printed
Lettering/`, body STL plus one STL per glyph beside a grouping `.3mf`), or not
at all. **One part, several colour bodies, one manufacturing unit** is what
those file names say. solid-node cannot say it.

## What Changes

- A **marking** becomes a declared, first-class, **non-solid** surface feature
  on a rigid node — a new kind of declaration beside parameters, children,
  ports and controls, and not a node:

      from solid_node.node.markings import Marking, Wrapped, Flat, Svg

      class FittedDialType1(ClearingGearFit, ResultsDialType1):
          digits = Marking(
              Svg('../Drawings/results_dial.svg'),
              Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45), start=0),
              color='#FFFFFF',
          )

- A marking SHALL contribute **no solid**. Volume, bounds, the STL and BREP
  bytes, the piece id, `assertNoIntersectingSolids`,
  `assertNoDisconnectedSolids` and every pairwise sweep SHALL be identical
  with and without it, faceted and exact alike. It is not a child: `children`,
  the tree, the part count and the `pieces` inventory are unchanged, and it is
  not selectable as a part.
- A marking SHALL NOT change the **solid's** artifact identity. It is not a
  parameter `Declaration`, so it never enters `identity_values` or
  `_build_uniq_id`, and editing the **artwork file** rebuilds only the
  marking's own artifact while the STL and BREP stay current. Editing the
  declaration **line** does rebuild the part, because the class body is in the
  node's scoped source digest (ADR-071); that consequence is deliberate and
  recorded in `design.md`, not engineered around.
- A marking is in the part's own **adjusted** frame — the frame its artifact is
  in — timeless and placement-free. An assembly's placement carries it, and
  nothing from the motion layer is involved: turn the roll and the digit at the
  window is the digit the register reads.
- Declaration is collected by `NodeMeta` the way `controls` is validated
  today: recognized in the class namespace, named by `__set_name__`, recorded
  in declaration order, inherited through the MRO, dropped by a subclass
  assigning `digits = None`. It is refused at class creation on an
  `AssemblyNode` or a flexible leaf, and refused when its attribute name
  clashes with a parameter, a child, a port or a joint coordinate of the same
  class, or would shadow an attribute every node already carries (`color`,
  `files`, `model`, `stl_file`) — each refusal naming the class and the
  attribute.
- Artwork is **`Svg(path, scale=None)`** in this cycle: a path relative to the
  declaring module, resolved and refused exactly as `stl_source` is
  (`require_source_file`), read through build123d's `import_svg` with the
  file's own origin kept, reduced to its closed **faces** (holes already
  nested). Open wires are ignored and their count logged at INFO naming the
  artwork file — the Curta's `results_dial.svg` carries its sheet border as
  four open lines, and that border is exactly the unwrapped circumference
  (measured: 59.376 mm against 2π·9.45 = 59.376 mm), so it is a registration
  mark, not a glyph.
  Artwork yielding no face is refused naming the file.
- Placement is **`Wrapped`** (a cylindrical wrap: artwork X is arc length,
  artwork Y is height along the axis, with a declared angular zero and an
  optional repeat pitch) or **`Flat`** (a plane through a point with a normal
  and an in-plane X axis). Both put the artwork point `origin` at the placement
  origin. No general surface projection.
- `color` is **required** on a marking and validated exactly as a node's is
  (`#RRGGBB`, else `ValueError`).
- The build SHALL write **one surface mesh artifact per marking** beside the
  part's STL, at the nominal surface with no offset, in the part's adjusted
  frame, through the same artifact lifecycle the sheet leaf's DXF already uses:
  written atomically with its digest and fingerprint, regenerated when stale,
  left alone when current. Its currency is checked **separately** from the
  solid's, on every build whether or not the solid is current, so a lost decal
  always comes back and a stale or missing one never re-derives an STL or a
  BREP. It is reachable through the manifest, so the sweep keeps it, and
  `solid export` copies it under `models/` under the same portability rules as
  `model`.
- A rigid node's document entry gains an optional **`markings`** list, each
  entry carrying `name`, `model`, `color` and its own `mtime`; absent when the
  node declares none. This is **ADDITIVE with no version bump**: a consumer
  that ignores it draws exactly today's picture, which is the `piece`
  precedent (ADR-043) and the ADR-057 rule that a producer emits the lowest
  version its content needs. Placement is **not** published — the decal mesh is
  already in the part's frame and the consumer applies the part's operations to
  it — and a marking has no `piece`.
- A node declaring no marking SHALL produce a **byte-identical** document to
  today's.

### Out of scope, recorded so it is not read into this change

- **`Dxf` artwork.** Upstream ships both, and DXF needs a rule and a tolerance
  the SVG does not. Measured on `Manual/Painting/results dial.dxf`: cadquery's
  `importDXF` fails to close its chains at a 1e-3 mm tolerance, and at 1e-2 mm
  yields ONE face of 512.9 mm² — the sheet border with the digits as holes,
  i.e. the stencil, not the glyphs. A follow-up cycle, with its own
  chain-closing rule.
- **Text from a font.** A font makes geometry non-reproducible across machines
  and every marking in the catalogue already exists as a file; font provenance
  needs its own answer and its own cycle (`markings.md` §6).
- **General surface projection.** "Project this artwork onto that arbitrary
  face" is a later extension and a prerequisite for nothing here
  (`markings.md` §5).
- **`process`** (`painted`, `vinyl`, `coprinted`) and the manufacturing outputs
  they imply — the nominal flat cut file and the multi-material 3MF. Process
  and material arrive in 0.8 so that mass follows from them; accepting a
  `process=` keyword before anything acts on it would be a false claim
  (`markings.md` §8, cycle 3).
- **Drawing the marking.** The viewer is a separate repository and a separate
  change (`solid-node-viewer`, `markings.md` §8 cycle 2). This change specifies
  the framework side of the contract so that cycle can specify its own against
  it, and touches no viewer code. The OpenSCAD fallback — `solid develop`
  without the viewer extra, `solid snapshot` with the OpenSCAD renderer — does
  not draw markings; that is a stated scenario, not a gap.
- **A marking driven independently of its part.** Nothing in the catalogue
  needs it; a split-flap display would (`markings.md` §9).

## Capabilities

### New Capabilities

- `markings`: what a marking is and is not — the declaration and where it may
  be declared, the artwork source and its reduction, the two placements and
  their frames, the marking artifact and its own currency, and the four
  invariants that make it honest (no solid, not a child, not the solid's
  identity, in the part's adjusted frame).

### Modified Capabilities

- `node-model`: MODIFIED "Color declaration" — a node's single `color` is
  unchanged and a marking carries its own, validated the same way; and
  MODIFIED "Rigid vs non-rigid distinction" — a marking may be declared only
  on a rigid node, refused at class creation on an assembly or a flexible
  leaf.
- `build-pipeline`: MODIFIED "Build artifact layout" — the per-marking mesh
  artifact beside the part's `.stl`, under the same basename; and MODIFIED "A
  successful build sweeps unreferenced artifacts" — a marking artifact is
  spared by reference, not by kind, because the manifest names it.
- `export`: MODIFIED "Manifest contract" — the optional additive `markings`
  list on a rigid node's entry, its fields, the absence of placement and of
  `piece`, the version rule, and the byte-identity of a document with no
  marking; and MODIFIED "Export artifact contents" — a marking's mesh is
  copied under `models/` so the export stays self-contained.
- `printed-pieces`: MODIFIED "The inventory is additive to the published
  document" — a marking is not a printed piece and never enters the inventory.

## Impact

- **New code**: `solid_node/node/markings.py` — `Marking`, `Wrapped`, `Flat`,
  `Svg`, the MRO enumeration, the placement maths and the artwork reduction.
  Lazily re-exported from `solid_node/node/__init__.py` like every other
  public node name. Nothing heavier than the standard library is imported at
  module import; build123d and trimesh are reached inside the build, as
  `Build123dSheetNode` already does.
- **Changed code**: `solid_node/node/declarative.py` (`NodeMeta.__new__`
  validates a marking declaration where it is written, duck-typed, as
  `_validate_controls` does); `solid_node/node/base.py` (the marking
  artifact's path, its own currency and producer recipe, and building the
  stale ones in `_prepare`, outside the solid's skip decision — the leaf skip
  predicates in `solid_node/node/leaf.py` are deliberately NOT widened, unlike
  `sheet_leaf.py`'s, because a marking is derived from the artwork and never
  from the render); `solid_node/core/serializer.py` (one optional producer callback,
  as `piece_id` already is); `solid_node/core/builder.py`,
  `solid_node/core/export.py`, `solid_node/viewers/browser.py` (pass it, and
  export copies the artifact); `solid_node/core/builder.py`'s sweep (collect
  the references).
- **Dependencies**: none added. `trimesh` is already a dependency and
  `build123d` is already the sheet adapter's backend; a project whose markings
  are all `Svg` needs build123d at build time, as a sheet part already does.
- **Tests**: a new fixture project `tests/markings_project` with a small
  committed SVG and both leaf kinds — an exact `CadQueryNode` dial, so the
  `.brep` and the declared `linear_deflection` are really compared, and a
  faceted `StlNode` plate — and a new `tests/test_markings.py`;
  `tests/test_node_lazy_exports.py` gains the four names. `tests/base_documents/`
  gains NOTHING: its captures are earlier cycles' bases and stay untouched, so
  the existing `ByteIdentityTest` keeps comparing against pre-marking bytes,
  and the new fixture's marking-free tree is asserted structurally instead.
- **Docs**: a new `docs/markings.rst` linked from `docs/index.rst`, and a
  `HISTORY.rst` entry.
- **Projects**: `Curta-Type-I-3x` and `Pascaline-module` may declare their
  markings once the viewer draws them. Nothing forces them to, and nothing
  either project does today changes.
- **ADR-120 is proposed**: a marking is a declaration on a part that produces
  an artifact and no solid — a fourth answer beside parameter, child and port
  to "what may a class body declare", and the first artifact a node writes
  that is published, coloured and drawn but is not geometry the model claims
  to be made of. (ADR-119 is the highest on main at 710d86f, the base this
  cycle was fast-forwarded onto on 2026-09-15. Re-check at extraction time.)
