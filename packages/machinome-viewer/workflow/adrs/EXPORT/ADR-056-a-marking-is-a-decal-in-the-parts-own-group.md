# ADR-056: A marking is a decal mesh in the part's own group, and the bias over the surface is the viewer's

**Status:** Accepted

**Date:** 2026-09-15

**Change:** `draw-what-a-part-carries`

**Extends:**
- [ADR-035: Reusable viewer core and declared API](ADR-035-reusable-viewer-core-and-declared-api.md)

**Consumes:**
- solid-node ADR-120: A part carries markings it is not made of

## Context

A Curta's answer is the angular position of ten printed number rolls, and
a Pascaline's is the digit each drum shows through its window. Both
machines were modelled, driven and run in this viewer, and both were
**unreadable**: the digits were not on the parts, so a maker turned the
crank and the machine gave no answer — which for a calculator is the one
thing it is for.

solid-node's ADR-120 closed the producer's half. A rigid part declares
what it **carries** on its surface — artwork, a placement, a colour —
without declaring a solid; the build writes one **surface mesh** per
marking, an open sheet of triangles lying on the nominal cylinder or
plane with no thickness and **no offset**; and the document publishes a
`markings` list beside the node's own `model`, one entry per declared
marking in declaration order, each carrying a `name`, a `model`
reference, a `color` in `#RRGGBB` and **its own `mtime`** — the marking
artifact's, not the node's. No placement is published: the artifact
already holds the artwork's surface in the part's own frame. The list is
additive and moves no document version; the framework's own marked
fixture declares version 2.

Nothing drew it. This is the consumer's half.

One sentence of the producer's design is addressed to us. Its D5 states
that any anti-z-fighting offset is **a rendering constant belonging to
the viewer, not a claim about where the part's surface is** — so the
producer will not lift the decal, and the viewer must.

## Decision

**A marking is drawn as a mesh, through the path a model already takes.**
Each entry is fetched by the same `loadMesh(url, color)` a node's own
model is: `STLLoader.loadAsync`, `computeVertexNormals()`, a `THREE.Mesh`.
The artifact is a binary STL like any other and needs no second loader,
no second cache and no second failure mode. Rasterising the artwork and
UV-mapping it is the better answer eventually and is not this answer: the
pipeline produces no UV coordinates, and the decal mesh reuses the whole
existing rigid path for nothing.

**The decals live in a group of their own, inside the part's group.** A
node that carries markings gains one child `THREE.Group` and a `markings`
record array in document order; a node that carries none builds no group
and adds no object, so its scene graph is the one it had. Membership in
the part's group is what buys everything, and it is the reason the
producer publishes no placement: the part's local matrix is the decal's
**parent** matrix, so pose, `$t` animation and a run's committed bank
carry the decal with no new code; `applyVisibility` already hides the
part's group; `dispose()` already traverses it; `rebuildPartControls`
already traverses it, so a decal on a touchable dial is pressable and
highlights **with** the dial; and `assembly()` walks `WidgetTree`
children, so a marking is excluded from a host's readback by
construction.

A **sub-group** rather than tagged meshes, because three existing sites
filter the DIRECT mesh children of a node's group and two of them would
be wrong for a decal: `removeMesh` would destroy the decals whenever the
part's own model was replaced, and `setColor` would repaint a decal in
the part's inherited colour. A `userData` tag with a predicate at each
site is the alternative, and this codebase already argues against it: a
tag survives into a freshly loaded replacement only if every construction
site remembers to set it. A group is correct at all three sites and at
every site written later. It costs one line, in `applyVisibility`, where
the group's own `visible` follows the direct meshes' — the case that
matters being a part that is an **ancestor** of the focused node, whose
group stays visible to preserve the transform while its own surface must
not be drawn. Its decals are its own surface.

**The anti-z-fighting bias is the viewer's rendering constant, and it is
two things.** Measured on the framework's own fixture — the dial,
R = 9.45 mm, meshed at its declared `linear_deflection` of 0.05 mm —
77.2 % of the decal's 448 facets lie *behind* the part's tessellated
surface, by a median 0.0045 mm and a worst 0.0203 mm. Both meshes are
chordal approximations of the same cylinder and their facet boundaries do
not line up, so this is a real interpenetration in world units and not a
coplanar z-fight. So:

1. **A world-space lift** of `MARKING_LIFT = 0.15` document units along
   the sheet's own normals, at load. The magnitude is a derived bound,
   not a guess: the producer meshes a decal to the part's own tolerance
   `t` (its declared `linear_deflection`, or the framework default
   0.1 mm), chords sag INWARD, so the depth of any interpenetration is
   bounded by the decal's own chordal sag, at most `t`. 0.15 is 1.5× the
   default, covering every part declaring no tolerance and every part
   declaring up to 0.15 mm.
2. **`polygonOffset: true, polygonOffsetFactor: -1,
   polygonOffsetUnits: -1`** under it, for the case the lift cannot
   reach: a viewer zoomed far enough out that 0.15 mm falls below one
   depth-buffer step. −1/−1 is the minimum bias that separates two
   surfaces the depth buffer cannot tell apart, and staying at the
   minimum is deliberate — a large offset starts letting a decal show
   through a part standing genuinely in front of it.

Beside them the material is `side: THREE.DoubleSide` — an open sheet has
a back, and a decal must not vanish when the camera crosses its plane —
and normal depth write, because a decal that did not write depth would
show through everything drawn after it.

**The sheet is WELDED before it is lifted.** This is the one thing
implementation added to the decision, and it is load-bearing. An STL
arrives non-indexed, one private copy of each corner per facet, so
`computeVertexNormals` gives every copy its own FACE normal and lifting
each along that normal pulls adjacent facets **apart**. Measured on the
fixture's wrapped decal — 448 facets, an 11.8° turn between neighbours —
the tear is 2 × 0.15 × sin(5.9°) = 0.031 mm, which draws a visible grid
of part-coloured cracks over the digits from 30 mm away and widens with
the lift. Welding the co-located corners into one vertex carrying the
**mean** of the facet normals around it — which is what the producer's
own design argument already assumed by saying *averaged* vertex normals —
moves the sheet off the surface as one piece.

The lift's DIRECTION relies on a property the producer has and its export
spec does not yet promise: a decal's triangles wind with their normal
AWAY from the part. That was measured, not assumed — on every Curta
drawing and on the fixture's own decals — and it is pinned here by a test
that loads the committed fixture and asserts every lifted vertex moved to
a LARGER radius, so a producer that ever wound the other way fails by
name rather than drawing digits inside the roll.

**A marking's colour is its own, and inheritance never reaches it.** The
producer requires `color` on a marking, and this viewer refuses one
without a well-formed `#RRGGBB`, so `materialForColor`'s null fallback is
unreachable for a decal. The fixture proves the two are independent: its
`dial` renders through `MeshNormalMaterial` while its `digits` decal is
`#FFFFFF`. A decal whose own colour moved has its material replaced in
place, with no refetch — colour is not geometry identity.

**A decal reloads on its own currency.** A marking's identity is its
`model` path and its own `mtime`, exactly as a node's is, and the two are
independent: the producer's whole currency split exists so that editing
artwork moves the marking's stamp and leaves the part's STL current.
`prepareReconcile` fetches every new or moved decal before the live tree
is touched, matching across a republish **by name** and ordering by the
document; `artifactChanged(path)` collects the markings whose `model` is
that path beside the nodes whose model is, by exact string match; and
`freshFromArtifact` is **per marking**, independent of its node's,
because their stamps are.

**A `markings` list this viewer cannot read is refused by name**, inside
`assertRenderable`'s per-node visit, before anything is rendered, naming
the document, the node and the marking — a value that is not a list, an
entry that is not an object or whose name or artifact reference is not a
non-empty string, a colour that is not six hexadecimal digits, one node
declaring a name twice, or a list on a node that is not rigid. The
framework blesses a consumer that ignores `markings` entirely: it renders
today's picture, which is a truthful picture. This viewer does not ignore
them, and one that read nine digits and silently dropped the tenth would
show a **false** register. Half-reading is the failure mode; refusing
names the producer bug where it can be fixed.

## Consequences

- **A marked machine is readable in a browser.** The framework's marked
  bench mounts, draws three decals in two declared colours on two parts,
  and turns its dial with the digits on it — proved in pixels, at a
  pinned camera, against the same document with its `markings` keys
  stripped.

- **A marking is not a part, four ways.** No navigator row, no node in a
  host's readback, no focus or visibility target of its own, and in no
  inventory. The camera fit box is the one place a decal counts, and
  deliberately: the fixture's `band` decal lies at radius 12.0 on a plate
  whose own box is ±10.0, because the producer places a decal where the
  declaration says and does not clip it to the silhouette. Framing that
  model with its marking cut off would be the opposite of the point.

- **An unmarked document is untouched.** No marking group is built, no
  material is made, no validation branch is entered, and the scene graph
  is what it was.

- **The residual is recorded, not hidden.** A part declaring a
  `linear_deflection` above 0.15 mm may still punch through its own
  decal, and the remedy then is a framework finding — publishing the
  tolerance in the marking entry, or lifting in the producer — not a
  viewer knob. On the fixture, whose dial declares 0.05 mm, the welded
  sheet shows 206 part-coloured pixels inside 46,400 decal pixels
  (0.44 %) along a few long thin triangles at a 30 mm viewing distance,
  and none at a normal one.

- **The capture needed no code.** `Capture.serve` serves the whole
  staging directory and the framework already stages marking artifacts
  beside the models it copies, so `solid snapshot --renderer web`
  photographs markings the moment the widget draws them. That was a
  claim; it is now a test over a marked staging.

- **The declared API version rises to 14**, because drawing a document's
  markings is a capability a host may require. `documentVersions` stays
  `[1, 2, 3, 4, 5]`: `markings` is additive and gated on no document
  version. 13 is skipped deliberately, the in-flight
  `slide-and-turn-parts` cycle claiming it, so the two numbers cannot
  collide whatever order they integrate in.

- **Not in this:** no texture or UV mapping, no placement arithmetic in
  the viewer, no markings in the OpenSCAD path, no version floor on the
  framework's `viewer` extra, and no driving a marking independently of
  its part.
