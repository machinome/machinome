## Context

solid-node's `carry-markings-on-a-part` (ADR-120, merged at `8d29cf5`) closed
the producer's half of `solid-node/workflow/docs/markings.md`. A rigid part may
now declare what it **carries** on its surface — artwork, a placement, a colour
— without declaring a solid; the build writes one surface-mesh artifact per
marking; and the document publishes it. This is the consumer's half: cycle 2 of
that note's §8 staging, "Viewer: draw it".

### The contract, as the producer specifies it

From solid-node's `export` capability, requirement **"Manifest contract"**:

> A rigid node that declares markings under the `markings` capability SHALL
> additionally carry a `markings` list, one entry per declared marking in
> declaration order, each entry carrying the marking's `name`, a `model`
> reference to its artifact under the same rules and the same portability
> guarantee as the node's own `model`, its `color` in `#RRGGBB` form, and its
> own `mtime` — the marking artifact's, not the node's […] The key SHALL be
> ABSENT on a node that declares no marking.
>
> A marking entry SHALL NOT publish its placement: the artifact already holds
> the artwork's surface in the part's own frame, so a consumer applies the
> part's operations to it exactly as it applies them to the part's model, and
> no consumer reproduces the placement arithmetic. A marking SHALL NOT carry a
> `piece`, and SHALL NOT appear in the piece inventory.
>
> The `markings` list SHALL be treated as ADDITIVE and SHALL NOT bump
> `version`.

and from **"Export artifact contents"**: `models/` holds a copy of every
marking artifact the manifest names, with the same containment guarantee a
model has, so a marked export is self-contained on a static host.

solid-node's design **D5** settles the one thing that is ours:

> Per marking, one **surface mesh** — an open sheet of triangles lying on the
> nominal cylinder or plane, with no thickness and **no offset**. Any
> anti-z-fighting offset is a rendering constant belonging to the viewer, not a
> claim about where the part's surface is.

and adds that the mesh is deliberately **not watertight** and is never fused,
imported or measured.

### The document this cycle was designed against

The framework's own marked fixture, `tests/markings_project/assembly.py:Bench`,
exported here as design evidence (`solid export … --no-widget`, under the
scratchpad; the artifacts are reproduced as this cycle's committed fixture):

| file | bytes |
| --- | --- |
| `manifest.json` | 2 698 |
| `models/…/dial-Dial-….stl` (the part) | 25 084 |
| `models/…/dial-Dial-….marking-digits.stl` | 22 484 |
| `models/…/plate-Plate-….stl` (the part) | 684 |
| `models/…/plate-Plate-….marking-band.stl` | 8 084 |
| `models/…/plate-Plate-….marking-badge.stl` | 184 |

Its shape, verbatim:

```json
{"name": "dial", "type": "LeafNode", "color": null,
 "mtime": 1789474293.821272,
 "operations": [["r", "angle", [0, 0, 1]], ["t", ["0", "0", "20.0"]]],
 "model": "models/markings_project/dial-Dial-9f2c3557d753.stl",
 "piece": "62f6c453fd92",
 "markings": [{"name": "digits",
               "model": "models/markings_project/dial-Dial-….marking-digits.stl",
               "color": "#FFFFFF", "mtime": 1789474294.235284}]}
```

Four facts this document settles that no prose had:

1. It declares **`version: 2`**. The list really is additive, and the capability
   is not gated on a document version: a marked document may be any version this
   viewer reads.
2. The `plate` node carries **two** markings, `badge` then `band`, in
   declaration order, with **different colours** (`#FFFFFF`, `#C0C0C0`).
3. The `dial` node's own `color` is **`null`** — the part renders through
   `MeshNormalMaterial` while its decal is `#FFFFFF`. Colour inheritance and a
   marking's own colour are visibly independent.
4. The `band` decal lies at radius 12.0 on a plate whose bounding box is
   ±10.0. A decal is **not guaranteed to be within its part's silhouette**;
   the producer places it where the declaration says.

## Goals / Non-Goals

**Goals:**

- Draw every marking a document's parts carry, in its own colour, in the
  part's own place, at any document version this viewer reads.
- Carry a decal with its part through every motion the viewer already has:
  pose, animation, a run's committed bank, focus, hide/show, and a targeted
  update.
- Keep a marking out of everything a marking is not: the assembly readback, the
  navigator, the piece inventory, and every measurement the viewer reports.
- Reload a decal on its own currency, without refetching the part it is on.
- Refuse a `markings` list this viewer cannot read, by name, before anything is
  rendered.
- Leave a document with no marking rendering exactly as it renders today — not
  approximately, but with the same scene graph, the same materials and the same
  code path.

**Non-Goals:**

- Texture or UV mapping (`markings.md` §7: the better answer eventually, and
  not this answer — the pipeline produces no UV coordinates).
- Any placement arithmetic. D4's wrap maths stays in the producer. The
  anti-z-fighting bias below is a *rendering* constant, which D5 explicitly
  assigns to us; it is not a placement.
- Drawing markings for the OpenSCAD path (the framework's renderer, whose own
  spec already says it draws none).
- A version floor on the framework's `viewer` extra (framework side, later,
  and it needs a viewer release first).
- DXF, process or 3MF output (`markings.md` §8 cycle 3, framework, 0.8).
- Driving a marking independently of its part (`markings.md` §9, undecided,
  and nothing in the catalogue needs it).

## Decisions

### D1. A decal is a mesh loaded through the path a model already takes

Each `markings[]` entry is fetched by the same `loadMesh(url, color)` that
`tree.ts:437` already uses for a node's own `model`: `STLLoader.loadAsync`,
`computeVertexNormals()`, `new THREE.Mesh(geometry, materialForColor(color))`.
The artifact is a binary STL like any other; nothing about it needs a second
loader, a second cache or a second failure mode.

**Why not a texture** (`markings.md` §7's first route): rasterising the artwork
and UV-mapping it is correct and cheap at frame rate, and needs UV coordinates
that neither the producer nor this viewer has. The decal mesh reuses the whole
existing rigid path for nothing, which is why the note says the first cut takes
the second route.

This makes the framework's "not watertight" a non-event here: nothing in this
package ever asked a loaded mesh to be closed.

### D2. The decal lives in a group of its own, inside the part's group

`WidgetTree` gains, only for a node that carries markings, one child
`THREE.Group` holding that node's decals, and a `markings` array of
`{name, model, mtime, color, mesh}` records in document order. A node with no
marking builds no group and adds no object: its scene graph is byte-for-byte the
one it has today.

Membership in the part's group is what buys everything:

- the part's local matrix is the decal's parent matrix, so **pose, `$t`
  animation and a run's committed bank all carry the decal with no new code**
  — this is the whole reason the producer publishes no placement;
- `applyVisibility` (`tree.ts:363-377`) already sets `node.group.visible` for
  focus and hiding, so a hidden part's decals are hidden with it;
- `dispose()` (`tree.ts:398-408`) traverses and already disposes them;
- `rebuildPartControls` (`viewer.ts:673-696`) traverses the part's group, so a
  decal on a touchable dial is **pressable and highlights with the dial** —
  which is what a maker means when they press the digit they can see;
- `assembly()` (`tree.ts:329-338`) walks `this.children`, which are
  `WidgetTree`s, so a marking is excluded from the readback **by
  construction**, not by a filter anyone must remember.

**Why a sub-group rather than tagged meshes in the part's own group.** Three
existing sites filter the *direct* `THREE.Mesh` children of a node's group, and
two of them would be wrong for a decal:

- `removeMesh` (`tree.ts:265-274`) removes and disposes every direct mesh — it
  would destroy the decals whenever the part's own model was replaced;
- `setColor` (`tree.ts:280-295`) replaces the material of every direct mesh —
  it would repaint a decal in the part's inherited colour;
- `applyVisibility` (`tree.ts:370-373`) sets `mesh.visible = inFocusedSubtree`
  on every direct mesh, which a decal *does* want.

A `userData` tag plus a predicate at each site is the alternative, and this
codebase already argues against it at `viewer.ts:367-371`: a tag "survives into
`artifactChanged`'s freshly loaded replacement only if every construction site
remembers to set it". A group is correct by construction at all three sites and
at every site written later. The one line it costs is in `applyVisibility`,
which must set the marking group's own `visible` to `inFocusedSubtree` beside
the meshes' — the case that matters is a part that is an *ancestor* of the
focused node, whose group stays visible to preserve the transform while its own
surface must not be drawn. Its decals are its own surface.

### D3. The anti-z-fighting bias, and the numbers

The artifact carries no offset, so the decal is exactly on the nominal surface
and the viewer supplies the bias. **Measured on the framework's own fixture**
(the dial, R = 9.45 mm, meshed at the part's declared `linear_deflection` of
0.05 mm), casting a ray outward from the axis through each of the decal's 448
facet centroids and comparing the decal's radius there with the part's
tessellated surface:

| | mm |
| --- | --- |
| decal vertex radius | 9.450000 (to 5 × 10⁻⁷) |
| decal facet centroid radius | 9.429 … 9.449 |
| gap (decal − part surface), median | **−0.0045** |
| gap, worst | **−0.0203** |
| decal facets lying *behind* the part's surface | **77.2 %** |

Both meshes are chordal approximations of the same cylinder, and their facet
boundaries do not line up, so three quarters of the decal's facets sit up to
20 µm *inside* the part. This is not a coplanar z-fight; it is a real
interpenetration in world units, and **`polygonOffset` alone does not clear
it**: `polygonOffsetUnits` is denominated in the depth buffer's smallest
resolvable difference, which at this framing is on the order of 3 × 10⁻⁴ mm per
unit and varies with the camera, so no fixed unit count is a fixed world bias.

So the rendering constant is two things, and both belong to the viewer:

1. **A world-space lift.** At load, each decal vertex is displaced along its own
   vertex normal by `MARKING_LIFT = 0.15` document units (millimetres). The
   direction is verified against the fixture: a wrapped decal's averaged vertex
   normals are radially outward (scaling the fixture's measured per-unit effect
   to this lift, 0.15 raises every vertex radius by 0.14982 and moves z by
   0.00000), and a `Flat` decal's are its declared plane normal (z by +0.15000,
   radius by 0.00000). A rigid transform preserves it, so the lift stays
   perpendicular to the surface under every operation the part carries.
2. **`polygonOffset: true, polygonOffsetFactor: -1, polygonOffsetUnits: -1`**,
   on top, for the case the lift cannot reach: a viewer zoomed far enough out
   that 0.15 mm falls below one depth-buffer step. −1/−1 is the minimum bias
   that separates two surfaces the depth buffer cannot tell apart, and staying
   at the minimum is deliberate — a large offset starts letting a decal show
   through a part standing genuinely in front of it.

Beside those, the material is `materialForColor(entry.color)` with
`side: THREE.DoubleSide` — an open sheet has a back, and a decal inside a
transparent-less part must not vanish when the camera crosses its plane — and
**normal depth write**, because a decal that does not write depth would show
through everything drawn after it.

The lift is a **rendering** constant and not a placement: it says nothing about
where the part's surface is, which is precisely D5's sentence.

**The magnitude is a derived bound, not a guess.** The producer subdivides a
wrapped decal so it follows its cylinder to within the part's own tessellation
precision `t` — the part's declared `linear_deflection`, or the framework
default 0.1 mm when it declares none (solid-node ADR-120; archived design D5)
— and the part's own faceted surface lies within its tolerance of the same
nominal surface. Chords sag INWARD, so a decal facet lies inside the part only
where the decal's chord sags more than the part's does at that point; the
depth of that interpenetration is bounded by the decal's own chordal sag,
which is at most `t`. So the lift must be at least the tolerance the decal was
meshed at. Setting `MARKING_LIFT = 0.15` mm — 1.5 × the framework default —
covers every part that declares no `linear_deflection` and every part
declaring up to 0.15 mm, with margin: the fixture (meshed at 0.05 mm) measures
a worst-case interpenetration of 0.0203 mm, consistent with the bound.
**Decided**: the constant ships alone, no mount option (resolves what was
Open Question 1). The residual is recorded rather than hidden: a part
declaring a `linear_deflection` above 0.15 mm may still show punch-through,
and the remedy then is a framework finding — publishing the tolerance in the
marking entry, or lifting the decal in the producer — not a viewer knob.

**What the lift assumes of the producer.** The direction argument above — that
a decal's averaged vertex normals point away from the part, so lifting along
them always moves the decal clear rather than deeper in — relies on a
property the framework's export spec does not yet promise: that a decal's
triangles wind so their normal points AWAY from the part. Observed, not
promised: the producer tessellates artwork faces oriented +Z in artwork space,
and `Wrapped`/`Flat` map artwork +Z to the outward radial direction or the
declared plane normal respectively. This was measured, not assumed — on every
Curta drawing (`results_dial.svg`, `upper_housing_numbers.svg`,
`reversing_lever_arrows.svg`: every face normal +Z, first-triangle winding +Z)
and on the fixture's own decals (mean `dot(normal, radial)` = 0.999 for both
wrapped decals; the flat decal's normal equals its declared normal). A
framework follow-up will promise this in the export spec ("a decal's
triangles wind with their normal away from the part") — filed by the reviewer
as a finding; this cycle does not wait for it, and the test this cycle adds
(task 3.x) fails by name if a producer ever winds the other way.

**Welded before it is lifted — a defect the pixels caught, and the amendment
that ratifies the fix.** An STL arrives non-indexed: every facet owns private
copies of its corners, so `computeVertexNormals` gives each corner its facet's
own normal and lifting each corner along it pulls neighbouring facets apart by
`2 · L · sin(θ/2)` — on the fixture's wrapped decal (448 facets, 11.8° between
neighbours) a 0.031 mm tear, a visible grid of part-coloured cracks over the
digits at 30 mm, widening with the lift. The lift is therefore applied only
after the geometry is welded: co-located corners merged (`mergeVertices`, the
file's own normals dropped first so equality is positional), per-vertex normals
recomputed as the average of the facets meeting there — the "averaged vertex
normals" this section already assumed — and then every vertex moved along that
averaged normal. `liftAlongNormals` stays the pure per-vertex step the
hand-built test pins; `liftDecal` is weld, average, lift, and is what the
shipping path and the fixture tests use. Residual after welding, recorded and
not mended by enlarging the constant: 206 part-coloured pixels inside 46 400
decal pixels (0.44 %) along a few long thin triangles at 30 mm, none at a
normal viewing distance.

### D4. A marking's colour is its own, and inheritance never reaches it

`materialForColor(null)` returns `MeshNormalMaterial`, the fallback for a part
whose tree declares no colour anywhere. A marking never reaches it: the producer
**requires** `color` on a marking (solid-node D6: "a decal with no colour is
invisible, which means the declaration did nothing"), and this viewer refuses a
marking entry without a well-formed `#RRGGBB` (D6 below). The fixture proves the
two are independent: the `dial` renders through the normal material while its
`digits` decal is `#FFFFFF`.

`setColor` therefore must not touch a decal — free, by D2 — and a decal whose
**own** colour moved between republishes has its material replaced in place,
with the old one disposed, and no refetch: colour is not geometry identity.

### D5. Reload: a decal has its own currency

Extends `viewer-package`'s "Geometry is refetched only when its identity
changes". A marking's identity is its `model` path and its own `mtime`, exactly
as a node's is, and the two are **independent**: the producer's whole currency
split exists so that editing artwork moves the marking's stamp and leaves the
part's STL current (solid-node D5, invariant 3).

- **`prepareReconcile`** (`tree.ts:167`) fetches, before the live tree is
  touched, every decal whose entry is new or whose `model`/`mtime` moved, and
  builds the apply closure that swaps, adds and removes. A decal is matched
  across a republish **by `name`** (a marking's name is its declaring attribute,
  so it is unique on its node); order in the group follows document order. An
  entry that disappeared has its mesh removed and disposed; a `markings` key
  that disappeared entirely removes the group. This inherits the existing
  "fetch everything first" guarantee, so a decal that will not fetch leaves the
  whole previous scene standing (`viewer-package`, "A failed update leaves the
  model standing").
- **`artifactChanged(path)`** (`tree.ts:141`) collects, beside the nodes whose
  `model === path`, the markings whose `model === path`, refetches those and
  swaps them in. Routing is exact string match, so there is no ambiguity —
  and in practice no collision is even possible, the producer naming a decal
  `<basepath>.marking-<name>.stl`.
- **`freshFromArtifact`** (`tree.ts:73`) is per-marking as well as per-node, for
  the reason the node's flag exists: the manifest publishes after the artifact,
  so the reconcile that follows an `artifactChanged` would otherwise see a moved
  `mtime` for bytes already on screen and refetch them. A decal's flag is
  independent of its node's, because their stamps are.

**A correction to the briefing, recorded here.** The development page never
calls `artifactChanged`: `develop.ts:112-116` routes every reload through
`inspector.viewer.manifestChanged()`, deliberately ("never `reload()`, which
would refetch every artifact"). `artifactChanged(path)` is a **handle** method
(`viewer.ts:1242`) that a host — the studio's targeted update — calls. Both
paths must route a decal; only the second is the one named `artifactChanged`.

### D6. A `markings` list this viewer cannot read is refused by name

Validated inside `assertRenderable`'s existing per-node `visit`
(`viewer.ts:1937+`), on the surface an unreadable `bindings` table, an
inexecutable `program` and an unresolvable `controls` table already stand on:
before anything is rendered, naming the document, the node and the marking.
Refused: a `markings` that is not an array; an entry that is not an object, or
whose `name` or `model` is not a non-empty string, or whose `color` is not a
`#RRGGBB`; two markings on one node sharing a `name`; and a `markings` on a node
that is not rigid — one carrying `children` or `flexible`, which the producer
cannot emit.

**Why refuse rather than ignore.** The framework blesses a consumer that ignores
`markings` entirely — it renders today's picture, which is a truthful picture.
This viewer does not ignore them, and a viewer that reads nine digits and
silently drops the tenth shows a *false* register. Half-reading is the failure
mode; refusing names the producer bug where it can be fixed. `mtime` is the one
optional field, accepted absent exactly as a node's own optional `mtime` is.

### D7. A marking is not a part, stated four ways

- **Not a navigator row.** `navigatorRows` (`navtree.ts:73`) walks
  `AssemblyNode.children`, and `assembly()` builds those from `WidgetTree`
  children only, so a marking cannot become a row. Excluded by construction —
  and pinned with a test, because "by construction" is a property of today's
  code.
- **Not in a host's readback.** The same walk: a host reading `assembly()` on a
  marked document sees exactly the nodes, paths, colours and `model` flags it
  sees on the unmarked twin.
- **Not a focus or visibility target of its own.** There is no path that names
  one. A decal is hidden when its part is hidden and focused out when its part
  is focused out, and never separately.
- **In no measurement.** This viewer reports no volume, mass or piece count; the
  one number it derives from geometry is the camera fit box, and D8 settles
  that.

### D8. The camera fit box includes decals

`visibleBounds` (`viewer.ts:1789-1808`) unions the bounding box of every visible
mesh, so a decal enters the fit by construction, and this cycle **keeps it
there**.

The reasoning is not "the difference is negligible". The fixture proves it is
not always: the `band` decal sits at radius 12.0 on a plate whose own box is
±10.0, because the producer places a decal where the declaration says and does
not clip it to the part's silhouette. Excluding decals would frame that model
with its marking cut off — the opposite of the point. A decal on the nominal
surface changes the box by at most `MARKING_LIFT`, which is invisible; a decal
off it is the model's own statement, and framing it is right.

### D9. API 14, and the expected conflict

`solidNodeViewerApi` rises from 12 to **14** in
`solid_node_viewer/widget/package.json` — the single declaration `describe`,
the mount handle and the browser global all report — because drawing a
document's markings is a capability a host may require: a studio that means to
show a readable Curta wants to know, before it mounts, whether this bundle
draws the digits or silently shows a blank drum.
`solidNodeDocumentVersions` stays `[1, 2, 3, 4, 5]`: `markings` is additive and
moves no document version, which is the same posture the `controls` table's
requirement already states.

**13 is skipped deliberately.** The in-flight cycle `slide-and-turn-parts`
claims 13 (its design §D, and the primary checkout's uncommitted
`package.json`). This cycle takes 14 so the two numbers cannot collide whatever
order they integrate in. Expect a **one-line conflict on `package.json`** and a
conflict on the "The viewer declares its API version" requirement text at
integration; keep both diffs minimal and let integration reconcile the prose.
This is not a dependency: neither cycle needs the other's code.

The README "Versions" table's 0.2.0 row goes to 14 for the same reason.

### D10. The capture needs no code, and the cycle proves it

`Capture.serve` (`capture.py:180-195`) serves the **whole staging directory**,
and the framework's browser-snapshot producer already stages marking artifacts
beside the models it copies. So `solid snapshot --renderer web` photographs
markings the moment the widget draws them, with no change to `capture.py` and
no change to `mount_options`. That is a claim, and this cycle tests it with a
marked staging rather than asserting it.

### D11. The fixture: the framework's own marked export, verbatim

`tests/fixtures/marked/` holds the export above **exactly as `solid export`
wrote it** — `manifest.json` and all five STLs, 59 218 bytes total, in line with
`lock` (84 K), `pascaline` (116 K) and `touched` (112 K) — with a `README.md`
saying what it is, that nothing here edited or regenerates it, and which
framework fixture produced it.

**Why real part meshes and not the stand-in cubes** the `pascaline`, `lock` and
`touched` fixtures use: those fixtures test a run and a gesture, where a cube
shows what a digit drum shows. This one tests **pixels on a surface** — the
decal's colour where the decal is and the part's where it is not — and that
question is meaningless unless the decal genuinely lies on the part it marks.
The part meshes are 25 768 of the 59 218 bytes, and they are the cheapest
honest answer.

**Why the `Bench` document and not a smaller one**: it is a single 2.7 kB
document carrying every case this cycle has to draw — a `Wrapped` decal on an
exact part whose own colour is `null`, two decals of different colours on one
faceted part in declaration order, a decal off its part's silhouette, and
`version: 2`, which proves the capability is not gated on a document version.
The smallest marking in it, the 184-byte `badge`, is a two-triangle `Flat`
decal, which is also the cheapest possible reconcile subject.

**The unmarked twin is produced by the test, not committed.** Every "renders
exactly as before" and "reads exactly as before" assertion compares against the
same document with its `markings` keys stripped, written into the test's own
temporary staging — the framework's byte-identity argument mirrored in pixels
and in readback, at no fixture cost. `tests/support.py` gains
`export_marked(target)` and `published_marked(target)`, mirroring the existing
`export_with_widget` / `published_build` pair.

### D12. What proves it on screen

Pixels are the evidence (`AGENTS.md`), and the fixture is built for it: the
`dial` and the `plate` declare no colour, so both render through
`MeshNormalMaterial`, whose output is `normal * 0.5 + 0.5`. Two probes follow
from that, and the part provably trips neither — the second was added at
implementation, by measurement, and is ratified here:

- **Near-white.** A unit normal cannot exceed 0.577 in all three components at
  once, so the **brightest grey the part can possibly show is 201**, and an
  antialiased edge cannot beat it (an averaged pair of unit normals is no
  longer than a unit normal). The probe sits at 205. A `#FFFFFF` decal passes
  it — but only just, and not everywhere: measured over a 12 × 3 sweep of
  camera azimuth and elevation, a `#FFFFFF` surface in this scene never renders
  brighter than 213–217 in its darkest channel, and the dial's decal, whose
  normals are horizontal while the one directional light shines from
  (1, −1, 2), never passes 180 at any angle. Near-white alone cannot see the
  turning decal, and cannot see the fixture's `band` at all, which is `#C0C0C0`
  by declaration.
- **Neutral grey.** `normal * 0.5 + 0.5` is neutral only where
  |nx| = |ny| = |nz|, which a cylinder about z (normals (cos, sin, 0) and
  (0, 0, ±1)) and an axis-aligned box never reach; both declared marking
  colours are neutral under the scene's near-white lights at any brightness.
  Spread 20, floor 40 (below it is background or shadow). Measured: 4 369
  marking pixels on the marked fixture against 6 on the stripped twin.

The Playwright acceptance, at a FIXED camera (the fit box includes decals,
D8, so a marked document and its twin do not frame alike):

1. mounts the marked fixture, screenshots the canvas, and counts marking
   pixels under both probes — many (244 near-white, 4 369 neutral);
2. does the same against the stripped twin — none (0 and 6);
3. asserts every pixel that is not a marking pixel is unchanged between the
   two, which is "adding a decal changes only the decal";
4. `setDriver('angle', 180)` on the dial alone and screenshots again: the
   neutral-grey pixels are still there (2 171 → 1 925) and their centroid has
   **moved** by 169 px, which is the decal turning with its part and is the
   whole claim of "the producer publishes no placement".

## Risks / Trade-offs

- **The lift is a derived bound, not a guarantee for every declarable
  tolerance.** A part declaring a `linear_deflection` above 0.15 mm (the
  framework default is 0.1 mm; `MARKING_LIFT = 0.15` is 1.5× it) can still
  punch through its own decal. → Decided (D3): ship the constant alone, no
  mount knob; the acceptance test is the arbiter, and a part found punching
  through is a framework finding (publish the tolerance, or lift in the
  producer), not a viewer escape hatch. Not silently enlarged: a lift big
  enough for any tolerance would be a visible float.
- **`polygonOffset` costs a pipeline state change per decal material.** → One
  material per marking, of which a document has a handful; the parts already
  cost one each.
- **`DoubleSide` doubles the decal's rasterised fragments.** → An open sheet of
  a few hundred triangles; the dial's whole decal is 448.
- **A decal inherits the part's touchability** (D2), including the emissive
  lift on hover. → Intended, and stated: the digits are the dial's surface.
  Should a maker ever need a part touchable but its decal not, that is a
  declaration the document does not carry and would be a separate change.
- **Refusing a malformed `markings` fails a document that would otherwise
  render.** → It is a producer bug, the document is the producer's, and the
  house posture on every other unreadable table is to refuse by name. Recorded
  as D6's weighed alternative.
- **Two cycles move the same `package.json` line and the same requirement.** →
  Expected and named (D9); the numbers are chosen so they cannot collide.
- **The fixture adds 58 kB of committed binary.** → Smaller than three of the
  four fixtures already committed, and the pixels are the evidence.

## Migration Plan

None. `markings` is additive, absent from every document published before it,
and a document without it takes exactly the code path it takes today: no
marking group is built, no material is made, no validation branch is entered.
A host on API 12 or 13 mounting a marked document on this build draws the
markings without asking; a host that needs to *know* reads the declared 14.

Rollback is the commit: nothing is persisted, nothing is migrated, and no
published artifact changes shape.

## Open Questions

1. **Does a marking ever become a measurement?** Not here — this viewer reports
   none. If a later cycle publishes a bounding box or a size on the handle, the
   decision D7 records ("a marking is in no measurement the viewer reports")
   has to be honoured there too, and D8 shows the fit box is the one place the
   answer is already "yes, it counts" for a reason.
