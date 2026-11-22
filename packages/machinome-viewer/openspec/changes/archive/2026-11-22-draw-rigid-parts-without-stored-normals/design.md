## Context

A part read from a model file reaches its geometry through `loadMesh` (`src/tree.ts` 929-961) and the reading of its URL (`STL_READING`, 48-56): `STLLoader.loadAsync`, then `computeVertexNormals()` on the parse, then the geometry is held by every part and marking of one viewer that joined the reading, and copied for a further viewer (ADR-082). Read in three.js 0.156.1 in the bench's `node_modules`:

- `STLLoader` (`examples/jsm/loaders/STLLoader.js` 197-264 binary, 285-361 ASCII) makes a geometry with no index, three vertices a triangle, a `position` and a `normal` attribute of 32-bit floats, the normal being the facet normal the file carries, and a `color` attribute only for a binary file whose header carries `COLOR=`.
- `computeVertexNormals` (`core/BufferGeometry.js` 637-724) on a geometry with no index reuses the existing `normal` attribute and writes on each triangle's three vertices `normalize(cross(C - B, A - B))`, from the positions; `Vector3.normalize` leaves a zero vector zero. So the file's normals are never what is drawn: what is drawn is the normal of the winding.
- The rigid material (`materialForColor`, `tree.ts` 72-81) is a `MeshStandardMaterial` (metalness 0.1, roughness 0.6) or, with no colour, a `MeshNormalMaterial`, both `FrontSide` with three.js's default `flatShading: false`. A marking's (`markingMaterial`, 153-160) is the same with `DoubleSide` and a polygon offset. A flexible part's (`materialForFlexible`, `flexible.ts` 427-436) is the rigid pair with `flatShading: true`, and its geometry has no `normal` attribute.
- With `flatShading`, `WebGLProgram.js` 566 and 756 define `FLAT_SHADED`; `normal_vertex.glsl.js` then writes no `vNormal`, and `normal_fragment_begin.glsl.js` takes `normal = normalize(cross(dFdx(vViewPosition), dFdy(vViewPosition)))`, where `vViewPosition = -mvPosition.xyz` (`meshphysical.glsl.js` 45, `meshnormal.glsl.js` 40). `faceDirection` (`gl_FrontFacing`) is applied only without `FLAT_SHADED` and only with `DOUBLE_SIDED`. Without the flag, `normal = normalize(vNormal)`, `vNormal = normalize(normalMatrix * normal)`.
- `WebGLRenderer.js` 776: an object whose world matrix has a negative determinant is drawn with the front face clockwise. `WebGLGeometries.update` (`renderers/webgl/WebGLGeometries.js` 78-104) uploads every attribute a geometry has, whether the program reads it or not: an attribute left on a geometry is uploaded.
- `WebGLExtensions.init` (`renderers/webgl/WebGLExtensions.js` 52-74) asks a WebGL 1 context for `OES_standard_derivatives`, and `WebGLProgram.js` 113 enables it in a WebGL 1 shader when `flatShading` is set. The renderer tries `webgl2` first (`WebGLRenderer.js` 258).
- `Mesh.raycast` (`objects/Mesh.js` 207-420) reads `position` and the index; with a `normal` attribute it adds an interpolated `intersection.normal`, and it always sets `face.normal` from the positions.

The evidence (`workflow/evidence/enigma-rigid-part-normals-2026-11-22.md`) measured the page with the attribute deleted and the materials made flat by patches in the page. What follows was measured for this proposal on this machine, in the suite's Chromium (Playwright 1.63, headless, `--use-angle=swiftshader`, "ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)))", WebGL 2, `highp`), in two ways; all scratch code is outside the worktree and nothing of it is kept.

**The viewer, base against a prototype.** Two bundles built by `build.mjs`'s own esbuild calls to scratch files, one from the base source and one from a prototype of Decisions 1 and 3 (reverted; `dist/` untouched): the reading deleting the attribute in place of `computeVertexNormals`, and `RIGID` making `materialForColor`'s material with `flatShading` set. Hand-written binary STL files and the suite's marked fixture, mounted `on-demand` in a 321 by 241 host, posed by `setView`, pictures taken of the host and decoded:

| Document | Pictures | Pixels differing | By more than one step | Largest |
|---|---|---|---|---|
| A 40 mm cube, eight views, a highlight in each mode | 11 | 28 | 0 | 1 |
| The same cube, no colour (`MeshNormalMaterial`) | 8 | 7,094 | 0 | 1 |
| The cube with every triangle wound inside out | 8 | 66 | 0 | 1 |
| A sphere of 64 by 32 segments, eight views and highlights | 11 | 51 | 0 | 1 |
| The sphere with no colour | 8 | 252 | 0 | 1 |
| The sphere from 3,000 mm (triangles far below a pixel) | 4 | 0 | 0 | 0 |
| A cylinder of 512 sides, 4 by 80 mm (side triangles 0.05 by 80 mm) | 8 | 107 | 0 | 1 |
| Four parts on three files, one colourless, every highlight mode on two of them | 7 | 908 | 0 | 1 |
| The marked fixture (colourless parts, three markings), six views and highlights | 12 | 7,574 | 0 | 1 |
| A 40 by 40 by 0.5 mm plate seen 5, 2, 1, 0.5, 0.3, 0.2 and 0.1 degrees above its plane | 7 | 81 | 80 (at 0.2 degrees) | 14 |
| The plate with no colour, 0.5, 0.3 and 0.2 degrees | 3 | 80 | 80 (at 0.2 degrees) | 64 |
| The cube with a zero-area triangle on the first edge of each facet | 8 | 60 | 32 | 40 |
| The same with no colour | 8 | 7,124 | 32 | 63 |

The four-part document's WebGL buffers at mount with no view given, counted by `test_share_one_geometry.py`'s init script: 4 of 433,152 bytes on the base, 2 of 216,576 with the prototype (the sphere's and the cylinder's geometries; see Found while proposing); `test_share_one_geometry.py` B1's document: 4 buffers at mount, 2 created and 2 deleted by the artifact update on the base, 2 then 1 and 1 with the prototype; the marked fixture, with no view given, 4,452 bytes on the base and 4,020 with the prototype, 432 bytes less (12 bytes for each of 36 vertices; which geometries were drawn there was not established, and R2 measures the decals' bytes on their own).

**three.js alone.** A page loading `three.module.js` 0.156.1, with the viewer's lights (`viewer.ts` 414-417), renderer options (419) and materials, drawing one geometry with no index twice, once with `computeVertexNormals` and `flatShading: false` (today) and once with no `normal` attribute and `flatShading: true`, reading the pixels with `readPixels` (premultiplied alpha kept, so a partly covered pixel shows its coverage): the cube, the cube wound inside out and the cube under a mirroring scale, from six to twelve views each, coloured, colourless, ghosted, tinted and dimmed: at most one step. A comb of 1,000 and of 10,000 slivers (aspect 1,000 and 10,000), a 512-sided cylinder, a sphere of 256 by 128 segments from 3,000 mm, a cube 5,800 mm from the origin, a 321 by 241 canvas filled edge to edge by a plane (1 of its 2,240 border pixels differing, by one step): at most one step. The cube, coloured and colourless, the sphere and the square below in a WebGL 1 context: the same counts as in WebGL 2. A 100 mm square seen from 150 mm, 0.3 and 0.2 degrees above its plane: 153 and 152 pixels by 14 in one row, all partly covered (alpha 64), none at 0.45 degrees or above, none at 0.1; with no colour the same pixels change from the normal (0, 1, 0) to (0, -1, 0) in view space, that is reversed. The sphere of 64 by 32 segments: one pixel at its silhouette (alpha 128) by 13 in one of eight views, 55 with no colour, not a reversal. Controls, against the flat drawing: the cube drawn unlit, up to 74 steps; the cube with its stored normals negated (lit from behind), up to 58; the sphere drawn with smooth normals, 2,213 pixels by more than one step, up to 6; the sphere with the attribute deleted and its material left smooth, drawn black (up to 172 steps, 255 colourless); the sphere with the attribute kept and `flatShading` on, the flat picture exactly (0 pixels differ). Quantised normals (`Int8Array`, normalised) against today's: at most one step, on 1,765 pixels of a sphere view where flat shading differs on 7.

## Goals / Non-Goals

**Goals:** a part read from a model file holds no `normal` attribute, in the tab or in WebGL, and each facet is drawn lit by its own plane's normal, as today. Markings, flexible parts, highlights, picking, part controls, bounds, the order of drawing, capture, the `on-demand` mode, a mount, a reload, an update in place and a second viewer are as they are. Where the picture is not equal to today's, the design says where, how large and why, and the reviewer's comparison with the base holds it to that.

**Non-goals:** dropping the tab's copy of a geometry after its upload; the flexible parts' geometry; the markings' normals; storing normals more compactly (Alternatives); anything that lowers the resolution or the sampling of a part; instancing; a mount option or handle method; a shader of the viewer's own; molejo; any project's source. Correcting the two cases where the picture differs by more than a step: they are the flexible parts' look today, and whether to correct them, here or for both kinds, is the pilot's (For the pilot).

## Decisions

### 1. Where the attribute goes (attack point 5)

**The rule.** The reading removes the `normal` attribute from its parse, in the guarded step where it now calls `computeVertexNormals`: `loaded.deleteAttribute('normal')` inside the same `try`, which on a throw disposes the parse and fails the reading, as today. It is the reading's only preparation. It runs once a reading, on the geometry `STLLoader` returned, before `admitGeometry` hands it to any part and before `copy` clones it for a further viewer, so no geometry a part is given carries the attribute and no copy needs the removal again. Nothing removes it later: ADR-082 point 8 ("nothing writes a part's geometry after it is handed out") stands.

**Never uploaded.** `WebGLGeometries.update` uploads the attributes a geometry has; the attribute is gone before any geometry reaches a mesh, so no buffer is created for it. The prototype's counts above: one buffer a file geometry where there were two, half the bytes.

**What is left in the tab.** `STLLoader.parse` still allocates and fills the normals array (36 bytes a triangle) while it parses; the array is unreachable once the attribute is deleted and is collected like any garbage. The evidence's experiment deleted it at the same moment (in place of `computeVertexNormals`), so its peak figures include that transient allocation.

**What `computeVertexNormals` in the reading did, every part of it:**

| What it did | After |
|---|---|
| Wrote one normal a triangle on its three vertices, from the positions, overwriting the file's normals | No normal is held; the fragment shader takes the same vector from the positions (Decision 2) |
| Ran a pass over every vertex of every file read, once a reading (993 files, 7.8 million triangles on the Enigma) | No pass |
| Set the attribute's version to 1 (asserted by S1) | No attribute |
| Could throw, making the reading fail, its parse disposed and every subscriber rejected (the test at `tree.test.ts` 215) | The guarded step remains, with the removal in it: a throw there still disposes the parse and fails the reading. `deleteAttribute` on a real geometry does not throw (`BufferGeometry.js`: `delete this.attributes[name]`), so the test reaches the path by making the instance's `deleteAttribute` throw (Decision 9) |
| On an indexed geometry would have averaged normals across shared vertices | Never reached: `STLLoader` makes no index. The widget tests' mocked loaders return `BoxGeometry` (indexed, with `uv`); the reading removes only `normal` from it |

ADR-082's "computes the normals once" (point 1) becomes "computes no normals"; its sharing, holders, copies, release and point 8 are untouched. S1's count of normal computations and its `normal` version, and S12's reference reading (a fresh parse with its normals computed), are restated in Decision 9.

### 2. What three.js draws, case by case (attack point 1)

**The rule, from the shader.** Today a fragment's normal is `normalize(normalMatrix * n)`, `n = normalize(cross(C - B, A - B))` of its triangle, the same at its three vertices. With `flatShading` it is `normalize(cross(dFdx(p), dFdy(p)))` for `p = vViewPosition = -mvPosition`; the two negations cancel, so it is `cross(dP/dx, dP/dy)` of the view position across the screen. For a planar triangle both are perpendicular to its plane. Which side: a screen step right and a screen step up move a visible point along the plane in directions whose cross product points back toward the eye, so the derivative normal faces the viewer whichever way the triangle is wound. A triangle drawn under `FrontSide` is one whose screen winding is counter-clockwise, which for a perspective view is exactly the triangle whose winding normal faces the eye, so its stored normal faces the viewer too. For every triangle the viewer draws of a rigid part, the two are the same unit vector up to rounding, and the lighting, the emissive and the colour that follow are computed identically from it.

| Case | Today | With `flatShading` | Measured |
|---|---|---|---|
| A triangle seen from its front | Its winding normal, facing the viewer | Its plane's normal, facing the viewer | Equal up to one step |
| A triangle seen from its back | Not drawn: every rigid material and every variant is `FrontSide` (`materialForColor` sets no side; `presentation.ts` 547 clones it) | Not drawn | No pixel of it either way |
| The same under `DoubleSide` | Only markings are double-sided, and they keep their stored normals and material (Decision 4). For the record, three.js multiplies a stored normal by `faceDirection` there, and a derivative normal faces the viewer already | — | Not used for rigid parts |
| A mirroring transform | Impossible from a document: `operationsMatrixScoped` (`tree.ts` 1045-1081) and `admitPresentation` compose only rotations about normalised axes and translations; nothing in `src/` scales an object (searched for `scale`, `makeScale`, `.scale.`). Were one applied, three.js draws it with the front face clockwise (`WebGLRenderer.js` 776) and transforms the stored normal by the normal matrix, so it still faces the viewer | Faces the viewer | three.js alone, a scale of -1: equal up to one step |
| Triangles wound inside out | The near faces are culled; the far faces' inner sides are drawn, their winding normals facing the viewer | The same faces, the same normals | Equal up to one step (viewer and three.js alone) |
| A triangle of zero area | Not rasterised | Not rasterised | — |
| A triangle of nearly zero area that the rasteriser still covers a few samples of | `computeVertexNormals` of three nearly collinear points: an arbitrary direction, not the surface's | The derivatives of its own nearly degenerate plane: another arbitrary direction | Up to 40 steps (63 colourless) at a few pixels along the edge the triangle lies on. Against the same cube without such triangles, today's picture differs there by 23 and the change's by 3 to 8, and one pixel gains coverage in both (three.js alone, one view): neither is the faces' colour |
| A facet seen nearly edge-on | Exact | Exact while the facet's image stays more than about a pixel from the vanishing line of its plane | Equal up to one step down to 0.5 degrees on the plate, 0.45 on the square |
| A facet seen within about a pixel of edge-on | Exact | At pixels the facet partly covers, at its edge, the normal can be wrong: reversed on a plane, mis-directed on a sphere's silhouette | The viewer's plate at 0.2 degrees: one row of 80 pixels, up to 14 steps (64 colourless); three.js alone, the 100 mm square at 0.3 and 0.2 degrees: 153 pixels by 14, reversed; the sphere: 1 pixel by 13 (55 colourless) in one of eight views. Every such pixel was partly covered |
| Very small triangles far from the camera | Exact | Exact | The viewer's sphere of 3,968 triangles from 3,000 mm: no pixel differs; three.js alone, a sphere of 65,024 triangles from 3,000 mm: one pixel by one step |
| Long thin triangles | Exact | Exact | 512-sided cylinder, combs of aspect 1,000 and 10,000: up to one step |
| The first and last row and column of the canvas | — | A 2 by 2 quad there is evaluated as anywhere else | 1 of 2,240 border pixels, by one step, on an odd 321 by 241 canvas |
| WebGL 1 | Stored normals need nothing | `OES_standard_derivatives`, which three.js asks for at initialisation | The same counts in a WebGL 1 context; without the extension the flat program would not compile, as the flexible parts' already would not |

**The single pixel by 11.** Not established on the page itself, which this proposal did not open. It is what the two exceptional cases produce: a few partly covered pixels, by about ten steps when coloured. The evidence says no part of the page is seen edge-on as far as its pictures show, but a silhouette of a curved part always has facets at every angle up to edge-on (the sphere's 13), and STL exports commonly carry nearly degenerate triangles. Which of the two it was is for the reviewer's comparison of the states that showed it.

**Why the edge-on pixels differ, as far as measured.** A fragment's derivatives are differences across the 2 by 2 block of pixels it is shaded in, each pixel's view position extrapolated from the facet's plane. When the facet's image lies within about a pixel of its plane's vanishing line, a neighbour of the block falls at or beyond it, where the extrapolated position has no meaning, and the difference can point anywhere: on the plate, exactly backwards (the colourless normal reversed), so the edge is lit as from behind. This is the probable mechanism, consistent with every measurement here (on the square at 0.3 degrees, its image spans 0.23 to 0.45 degrees below the horizontal through the eye, about one pixel of 0.21 degrees, with its vanishing line about a pixel above it; at 0.45 degrees and above nothing differs); it is not established from the rasteriser's source. A stored normal does not depend on neighbouring pixels and has no such case. Flexible parts are drawn this way today, so they show the same pixels when seen edge-on.

**What the measurements do not cover.** A graphics card, where the derivatives are computed by the card's own arithmetic and the count of differing pixels is unmeasured; another browser; a fragment shader without `highp` (WebGL 2 requires it, and three.js reports `highp` here); the Enigma page, which the reviewer measures.

### 3. Materials (attack point 3)

**After the change.** `RIGID` keeps its name and identity and makes, from a colour, `materialForColor`'s material with `flatShading: true` (a `MeshStandardMaterial` with the colour, metalness 0.1 and roughness 0.6; a `MeshNormalMaterial` with no colour). Its values are then exactly `FLEXIBLE`'s. `MARKING` is unchanged and must stay unchanged: `markingMaterial` is built on `materialForColor`, which keeps `flatShading: false`, so the flag is set in `RIGID`'s constructor and not in `materialForColor`.

**Two kinds stay two.** The holder keys appearances by kind (`presentation.ts` 401-428), so a rigid and a flexible part of one colour keep two appearances and two plain materials, equal in every value. Merging the kinds would save one material per colour that both kinds use and would change the counts the shared-material tests and ADR-076 state; it buys nothing measurable and is not done.

**What does not move.** The count of materials, which meshes share one, the variants a look makes and keeps (a variant is `plain.clone()`, and `MeshStandardMaterial.copy` and `MeshNormalMaterial.copy` copy `flatShading`, `materials/MeshStandardMaterial.js` 114, `MeshNormalMaterial.js` 53), and the order of drawing: places are given in `MaterialPresentation.mesh` and `recolor` (`presentation.ts` 265-285), in the order `loadMesh` reserves them in document order (`tree.ts` 939-942), and `drawOrderSort` reads places, never a flag. The prototype ran `src/shared-materials.test.ts` with only the flag changed in O1's recorded looks and in the oracle's rigid constructor (Decision 9): all 25 tests pass, O1's order lines unchanged in every step.

**Compiled programs.** `flatShading` is one of a program's parameters (`WebGLPrograms.js` 302) and nothing in them reads whether the geometry has a `normal` attribute. A rigid part's programs become the ones a flexible part of the same material type, transparency and lights already uses: a document with both compiles one program where it compiled two for each such set; a document with only rigid parts compiles as many as before, other ones. A marking's program (double-sided, stored normals) is unchanged. An expectation from the source; not counted.

### 4. Markings (attack point 4)

A marking keeps its normals, for the reason ADR-056 gives them: its decal is welded (`mergeVertices`) so that co-located corners become one vertex, given averaged normals by `computeVertexNormals` on the welded, indexed sheet, and every vertex lifted 0.15 mm along its own normal (`liftDecal`, `tree.ts` 979-987; `liftAlongNormals`, 120-139). Flat shading would draw a curved decal faceted where it is smooth, and the lift needs a normal per vertex in the tab anyway. Its material (`MARKING`, `DoubleSide`, polygon offset -1/-1) does not change.

**From a file with no normals.** `liftDecal` clones the file's geometry, deletes the clone's `normal` attribute and welds the clone on what is left. Today what is left is `position`; after the change the file's geometry has no `normal` to delete, and what is left is still `position`, so `mergeVertices` receives the same input and the welded sheet, its averaged normals and its lift are the same arrays. A part and its marking naming one file share one reading (ADR-082), so the reading's removal must not reach the decal: it does not, because the decal is made from a clone and has its own normals computed after the weld. `liftDecal` does not change; its `deleteAttribute('normal')` stays (it keeps the weld correct for a geometry handed in with normals, as the tests' are, and `share-one-geometry*.test.ts` identify the lift's temporary clone by that call). The marked fixture above: every picture within one step (its decals' bytes on their own are R2's to pin).

### 5. Every reader of a part's normals (attack point 2)

| Reader | Today | After |
|---|---|---|
| Lighting in `MeshStandardMaterial` (both lights, the emissive, the specular) | `vNormal` | The derivative normal (Decision 2) |
| `MeshNormalMaterial` (no colour) | Packs `vNormal` into the colour | Packs the derivative normal: the facet's direction, as the manual says ("a colour derived from its surface direction"). Up to one step, on more pixels than the lit material (7,094 of 618,888 on the colourless cube) |
| Hover, highlight, dim, ghost (`presentation.ts` 516-567) | Clones of the plain material | Clones carry the flag (Decision 3). Emissive, colour, opacity and depth write do not read a normal |
| `liftAlongNormals` | Reads only the welded decal's own computed normals | Unchanged (Decision 4) |
| `liftDecal` | Deletes the clone's normals before welding | Deletes nothing there; unchanged code (Decision 4) |
| Picking (`Raycaster.intersectObject` → `Mesh.raycast`) | `position`; an `intersection.normal` from the attribute; `face.normal` from the positions | `position`; no `intersection.normal`. The viewer reads only `hit.object` (`viewer.ts` 850-857), and nothing in `src/` reads `intersection.normal` (searched) |
| The per-viewer copy (`STL_READING.copy`, `geometry.clone()`) | Copies every attribute, normals included | Copies the positions (and a coloured file's `color`): half the bytes |
| Bounds (`computeBoundingBox`/`Sphere`), `worldBounds`, `visibleBounds`, the render list's depth | `position` | Unchanged |
| Capture (`capture.py`) and the snapshot path | Draw through the same bundle and renderer | The same picture as on screen |
| three.js beyond lighting | Tangents, morph normals, shadow-map normal bias, `EdgesGeometry`, wireframe helpers would read normals; the viewer uses none of them (searched `src/`), and the scene casts no shadow | — |
| A coloured binary STL's `color` attribute | Uploaded, never drawn (no material sets `vertexColors`) | Unchanged: only `normal` is removed |

### 6. The requirement's words (attack point 6)

Read in the baseline `viewer-package` spec and the ADRs:

- "Colour is inherited and falls back to a normal material": "the framework's normal-based material when no colour is available". Still the normal-based material, from the facet's direction. Untouched.
- "The viewer draws the markings a part carries": "A node that carries no markings SHALL be drawn exactly as it is drawn by a viewer that has never read a marking: the same geometry, the same material and the same scene contents", and the scenario "An unmarked document is untouched", "it renders exactly the picture it rendered before this viewer could draw a marking". Both compare with an earlier build of the viewer; after this change a node without markings has another geometry and material than that build gave it, and its picture equals that build's only within a step. What they are for is that markings add nothing to a node or a document without them, within one viewer. Restated so: "exactly as it is drawn when its document carries no marking" and "exactly the picture this viewer renders of the same document published before markings existed". The delta restates the requirement whole with its six scenarios; its other sentence, "rendered, read back and photographed identically to the same document published before markings existed", already compares two documents in one viewer and stands.
- "Fresh mounts draw loaded rigid assets independently of fetch completion order": two loads by one build, exactly equal pixels. Holds: the derivative normal depends on the geometry and the view, not on the order of arrival (B2-style comparison within one build).
- "A host highlights parts and sets the others back": "the two captures are identical", "looks exactly as it did before either happened": both within one build. Holds.
- "Parts that name one model file share one geometry": "the fully loaded picture equals the picture of the same document in which every part names its own copy of the same bytes": within one build. Holds; `test_share_one_geometry.py` B2 keeps comparing so. "A reading SHALL be one request for the file and one parse of its response": holds.
- "A continuous viewer draws a frame only when its picture has changed": nothing about shading. Holds.
- "The viewer evaluates flexible geometry per frame" and the flexible refusals: nothing about shading. Untouched.
- Scenarios "exactly as it did before" elsewhere ("Older documents are untouched", "A document with no controls is untouched" and the like): they say loads, poses, runs and drives, never the picture. Untouched.
- ADR-082 point 1, "computes the normals once": amended (Decision record). ADR-056, "Each entry is fetched by the same `loadMesh(url, color)` a node's own model is: `STLLoader.loadAsync`, `computeVertexNormals()`, a `THREE.Mesh`": amended; its lift "along the sheet's own normals" and "The sheet is WELDED before it is lifted", with the averaged normals, stand. ADR-078's "existing normal/marking preparation" was already amended by ADR-082. The framework's ADR-057 (`packages/machinome/docs/adrs/NODE/`, "Flat shading, chosen rather than defaulted") and `packages/machinome/docs/architecture.md` 2876-2880 say a flexible part is shaded flat to match an STL, which "arrives non-indexed and therefore already looks flat": still true, and now true by construction; not edited.

The new requirement states the observable behaviour: no normal held for a file part, in the page or the graphics context; each facet drawn flat and lit from its own plane on the side facing the viewer, in every look; where a facet seen within about a pixel of edge-on or a triangle of nearly zero area reaches a pixel, that share of the pixel may be lit as from another direction; markings and flexible parts as before; and what holding no normals does not change. How the picture compares with the viewer that stored normals (within one step of 255, measured) is a fact of this change and is recorded in the decision record and the evidence, not in the requirement: once this change is the base there is no such viewer to compare with, which is the fault the two restated sentences of the markings requirement had.

### 7. What must not change (attack point 9)

Each verified against the source:

- Viewer API 30 and document versions 1 to 14: `package.json` 4-5, not touched.
- The mount handle: `viewer.ts` is not touched.
- Flexible parts: `flexible.ts` changes in its comments only (141-147 and 424-426 say the flat shading matches the rigid parts' look, which is now the same shading); `FLEXIBLE` and its geometry are untouched.
- Markings as drawn: Decision 4.
- Highlights: Decision 3; the picture tests include every mode.
- Picking and part controls: Decision 5; `partControls.ts` reads no normal.
- The order of drawing: Decision 3.
- The requests a page makes: the reading's request is unchanged; nothing new is fetched.
- ADR-082's sharing and its counts of holders: the reading's group, holdings, shares and release are untouched; S2 to S11 and S13 and both generated proofs ran green on the prototype unmodified.
- `on-demand` mode and capture: no write this change adds is read by a draw after the mount (the removal happens before a geometry reaches a mesh, the flag before a material does), and the picture revision is raised by the same calls.
- WebGL 1: Decision 2's last row. The viewer runs on WebGL 1 where three.js 0.156.1 falls back to it (deprecated there); the flexible parts already need `OES_standard_derivatives`, and the rigid parts now do too.

### 8. Cost (attack point 10)

Expectations, for the reviewer to measure; none is a promise.

- Memory: the evidence's experiment is this change's effect on the page (the same attribute removed at the same moment, the same flag): one open copy about 2,489 MiB where it is 3,034, typed arrays and WebGL buffers each about 268.4 MiB less, the flexible parts' 489.9 MiB and the markings' 3.2 MiB unchanged; the peak while the page loads about 2,615 where it is 3,265, while `reload()` holds both models about 3,560 where it is 4,581. One run each in the evidence; the reviewer measures again.
- The load: no normal pass over the file parts' 7.8 million triangles, and half the vertex bytes handed to WebGL and copied for a second viewer. Faster, by an amount not predicted.
- A frame: the vertex shader no longer fetches a normal nor multiplies it by the normal matrix, and one varying fewer is interpolated; the fragment shader computes two derivatives, a cross product and a normalisation where it normalised an interpolated vector. In software drawing these two may not balance; no direction is predicted.
- Programs: Decision 3.

### 9. Tests (attack points 7 and 8, and the planned proof)

**`src/rigid-part-normals.test.ts`, the real tree (node environment).** `STLLoader.loadAsync` is mocked to return three.js's real `STLLoader.parse` of hand-written binary STL bytes, so each reading is handed a real parse with its `normal` attribute, as in the browser; URLs are distinct per test, since the admission module is shared. `computeVertexNormals` and `deleteAttribute` are spied on the prototype, recording `this`; `STLLoader.prototype.parse` is wrapped to record the geometries it returns. Red on the base for the reason given, each to be run on the base far enough to fail there (a probe of N1 to N3's central assertions, written for this proposal and deleted, did: on the base each file geometry had `normal` and `position`, one normal computation a geometry, `flatShading` false in every look, in a second viewer's copy and after a reconcile; with the prototype `position` alone, no computation, true; the decal indexed, with `normal`, not flat and double-sided on both).

- **N1** A mount of four parts over two files, one part colourless, one naming the other's file: every geometry a file part's mesh shows has exactly the attributes `['position']`; no `computeVertexNormals` call has a file part's geometry as `this`; `deleteAttribute('normal')` was called once per reading, on the geometry `parse` returned, before the first mesh held it (recorded by checking, in the spy, that no mesh yet shows that geometry); each part's material is `flatShading: true` and `FrontSide`, a `MeshStandardMaterial` or, colourless, a `MeshNormalMaterial`. Base: `['normal', 'position']`, one computation, `false`.
- **N2** The same assertions after: a new tree for the document with the same holder, the old disposed (the path `reload()` takes); a reconcile moving one part's `mtime`, adding a part naming a file on screen, and giving the colourless part a colour and another part none (the `setColor` replacement path, `tree.ts` 636-653); an `artifactChanged()` of one file; and a second tree of a second holder in the same batch, whose geometry is the reading's copy (not the first viewer's object). Base: as N1.
- **N3** Every look: for a coloured and a colourless rigid mesh, hovered, lit with the others kept, dimmed and ghosted, as the lit part and among the others, every material the mesh points at is `flatShading: true` and `FrontSide`, and after the put-back it points at its plain material again. Base: `false`.
- **N4** Markings: a part and its marking naming one file, and a marking on a file of its own: each decal's geometry is indexed and has `normal` and `position`; its arrays equal, exactly, `liftDecal` applied to a fresh `parse` of the same bytes with its normals computed (the base's path); its material is `flatShading: false`, `DoubleSide`, polygon offset factor and units -1; the part's geometry has `position` alone. A guard: passes on the base except the last clause.
- **N5** Kinds: a rigid part and a flexible part of one colour are two appearances of the kinds `rigid` and `flexible` and two plain materials (the holder's `counts()`), both `flatShading: true`. Red on the base at the rigid material's flag only; its counts pass on the base and guard the separation of the kinds.
- **N6** Picking: a `Raycaster` through the mounted tree's group, at nine rays across each part, returns the same `object`, `distance`, `point`, `faceIndex` and `face.normal` as through a twin mesh of the same positions given today's normals (`computeVertexNormals`). A guard: passes on the base.

**Existing widget tests that change**, each because it asserts the normals or the base's flag, and nothing else in them:

- `src/tree.test.ts`, "reserves sibling mesh and material identities in document order before either STL completes": its `expect(first.geometry.getAttribute('normal')).toBeDefined()` asserts the normals were prepared; it becomes `toBeUndefined()`. Every other assertion stands.
- `src/tree.test.ts`, "disposes returned geometry and its reserved material when normal preparation rejects": it makes `computeVertexNormals` of the returned instance throw, which is no longer called (on the prototype the load resolved). It makes the returned instance's `deleteAttribute` throw instead, and is renamed for the reading's preparation; its four assertions (the load rejects with the error, no mesh attached, the geometry disposed once, the material disposed once) stand. The spy is on the instance the mocked `loadAsync` returns, which is the object the reading calls `deleteAttribute` on.
- `src/share-one-geometry.test.ts`, S1: "whose normals are written once" asserts `seen.normals.get(geometry)` is 1 and the `normal` attribute's version is 1. They become: no normal computation on the geometry, and no `normal` attribute. Its title follows. The requests, parses, sharing and holders it asserts stand.
- `src/share-one-geometry.test.ts`, S12: its reference reading is a fresh parse with `computeVertexNormals()`; it becomes a fresh parse with `deleteAttribute('normal')`. Its assertion that nothing writes a shared geometry over its battery stands. (The spied `deleteAttribute` then records the fresh parse among `liftTemps`, which only exclude clones from the count of copies; harmless.)
- `src/shared-materials.test.ts`, O1: `O1_EXPECTED` was recorded on the base and is never regenerated; its 148 occurrences of `side=0 polygonOffset=false flatShading=false` are exactly the rigid parts' looks (the markings' carry `side=2`, the spring's `flatShading=true`), and each becomes `flatShading=true`, with a comment saying so and naming this change. No order line and no other value changes; on the prototype this edit alone turned O1 green.
- `src/shared-materials.test.ts`, P1 and the twelve P2 tests: the oracle's `shipped('rigid')` is the test's copy of the shipped `materialForColor` (non-flat); it becomes the test's copy of `materialForFlexible`, which is what the rigid constructor now makes. `markingMaterial`'s copy keeps building on the non-flat `materialForColor`. On the prototype this edit and O1's turned all 25 tests green.
- No other widget test changes. Run singly on the prototype: `tree`, `shared-materials`, `share-one-geometry`, `share-one-geometry-viewer` (5 of 5 green), `color`, `assembly`, `clockedControls`, `document`, `expression-reuse`, `draw-on-change`, `expression-lifetime`, `flexible`, `flat-pass`, `flat-pass-parity`, `inspector`, `navigator`, `presentation`, `geometry-admission`, `follow-the-slider`, `navtree`, `picture-revision`, `parent-adversarial-geometry`, `flexible-rebuild`, `partSurface`: only the two of `tree`, S1 and S12 of `share-one-geometry`, and fourteen of `shared-materials` (O1, P1 and the twelve of P2) failed.

**`tests/test_rigid_part_normals.py`, a real browser** (Chromium with SwiftShader, the suite's arguments, served by `QuietHandler`; the buffer counter of `test_share_one_geometry.py`). The model files are written by the test from Python, as `test_share_one_geometry.py` writes its tetrahedron: a 40 mm cube wound outward; the same cube wound inside out; a sphere of 64 by 32 segments; a cylinder of 512 sides, 4 by 80 mm; a 40 by 40 by 0.5 mm plate; the cube with a zero-area triangle on the first edge of each facet. The host is 321 by 241 pixels, odd in both directions.

- **R1** Buffers: a document of the cube, the sphere and the cylinder, one colourless, mounted with a view that frames all three: one buffer a file geometry, of 12 bytes a vertex, created at mount (the expected bytes computed from the facet counts); the base creates two buffers a geometry and twice the bytes. Red on the base.
- **R2** The marked fixture and the same fixture stripped of its markings (`support.strip_markings`): the bytes the markings add at mount equal the figure recorded on the base build and written into the test. A guard of Decision 4: passes on the base.
- **R3** The picture, by what must hold within one run, as the suite's other picture tests are (none stores a picture). The cube, coloured, from a view that shows three of its faces, plain and in each look a page can put it in (lit with the others kept, dimmed and ghosted, as the lit part and among the others): over the interior of each face the sampled pixels stay within the spread recorded on the base build and one step more (a facet is flat: one normal over its face); the three faces' brightnesses stand in the order, and at least half the gaps, recorded on the base build and written into the test; none is black. The cube wound inside out: its three visible inner faces likewise. The colourless cube: three flat faces of three colours, each face's strongest channel the one recorded on the base. The marked fixture: a marking's pixels show its declared colour over its part. A guard: it passes on the base, where the same facets are lit the same way; its proof is the mutations it must turn red, each of which draws a part or a decal black or unlit (MU2, MU5, MU8: tens of steps in the measurements above). It does not see a difference of a few steps from the base's picture: that is the reviewer's comparison, below.
- **The comparison with the base** is made once, by the reviewer, and recorded in `evidence.md`: the strict cases and the two exceptions of Context's table, and the Enigma page, drawn by a bundle built from the base and by one built from the implementation in the same browser and compared pixel by pixel, every pixel that differs by more than one step located. It is not a test of the suite. A picture recorded from the base would be compared only while the suite's browser is the one that recorded it, and would then be skipped for ever; and after this change there is no base to record another from. The proposal planned about sixty such pictures and a test pinning the exceptional pixels; both were struck in review ("Corrected in review").
- **Why one step, in that comparison.** Two float computations of the same unit vector (an interpolated stored normal, a cross product of derivatives) differ by rounding, which the lighting carries into an 8-bit channel as at most one step in every measured case outside the two exceptions; 77 pictures above, none by more. One step rejects every fault that matters: an unlit part (17 to 74 steps on the cube), a part lit from behind (8 to 58), a part drawn smooth where it is faceted (up to 6 on the sphere, on 2,213 pixels of one view), the attribute deleted with a smooth material (black, up to 172). It does not see the attribute kept with the flag on (the picture is the same exactly): R1, N1 and N2 do.

**Existing Python tests that change.** `tests/test_share_one_geometry.py` B1: 4 buffers at mount becomes 2, the update's 2 created and 2 deleted become 1 and 1 (measured with the prototype's bundle), and its comment on the base's counts names both bases. B2 and B3 compare within one build and do not change. No other Python test compares a picture with a stored value: `test_asset_load_order.py` compares digests of one build's loads in different orders; `test_draw_on_change.py`, `test_clocked_pose_admission.py`, `test_state_color.py`, `test_running_document.py`, `test_lock_document.py`, `test_clearing_document.py`, `test_calculator_document.py`, `test_regulator_document.py`, `test_curta_drawing.py` and `test_time_drive_document.py` compare two pictures of one run; `test_widget_e2e.py`, `test_server.py` and `test_capture.py` count pixels against colour thresholds or check transparency (a red channel above 100 and 1.4 times the others, differences above 30, patch means 60 or 150 apart), whose margins are tens of steps. Each still means what it meant; the final gate runs them all.

**Mutations.** Each applied alone to the implementation, then reverted; each must turn the named tests red:

| | Mutation | Red |
|---|---|---|
| MU1 | The attribute kept (the removal dropped), the flag on | N1, N2, R1, B1 (not R3: the picture is the same) |
| MU2 | The attribute removed, `RIGID` left without the flag | N1, N3, R3 (parts drawn black) |
| MU3 | `computeVertexNormals` still called, then the attribute removed | N1 (the computation counted) |
| MU4 | The flag set in `materialForColor`, so markings are flat too | N4, shared-materials P1 (the marking oracle) |
| MU5 | `liftDecal` relying on the file's normals (its `computeVertexNormals` dropped) | N4, R2, R3 (the marked fixture) |
| MU6 | The removal made in `copy` only | N1 (the first viewer's geometry) |
| MU7 | The removal made on the share in `loadMesh`, after the geometry is handed out | N1 (removal before the first mesh holds it) |
| MU8 | A highlight's variant made without the flag (`variant.flatShading = false` in `presentation.ts`) | N3, R3 (highlight states) |
| MU9 | `RIGID` and `FLEXIBLE` merged into one kind | N5 |
| MU10 | The reading's guard dropped (the removal outside the `try`) | `tree.test.ts`, the rewritten preparation test |
| MU11 | The removal made on a clone handed to the first viewer, the reading keeping its parse with the attribute to copy from | N2 (the second viewer's copy) |

Where two guards cover one case: MU1 is seen by the attributes (N1, N2) and by the buffers (R1, B1), never by a picture. MU2 and MU8 are seen by the flag in the widget suite and by the picture in the browser, each alone.

What these tests would not see: a difference of a few steps from the base's picture (the reviewer's comparison is the check, once); a graphics card's arithmetic; another browser; the Enigma's own geometry; a transient allocation in the tab (the parse's normals array before the removal, which the reviewer's memory measurement includes); time.

The final gate: the whole widget suite, the typecheck, the bundle built, then the viewer's Python suite.

### 10. What this replaces, and everything the replaced thing did

- **`computeVertexNormals` in the reading** (`tree.ts` 51): Decision 1's table.
- **`RIGID`'s constructor, `materialForColor`**: made the rigid material without the flag, and is still the base of `markingMaterial` and of the tests' sentinels (`tree.test.ts` 110, 182); it stays as it is and `RIGID` makes its material from it with the flag (Decision 3).
- **The comments that describe the base**: `STL_READING`'s ("the normals computed once"), `setColor`'s (`tree.ts` 645-648, "shaded flat to match the rigid parts an STL already renders that way") and `flexible.ts` 141-147 and 424-426. Corrected to the new state; `liftDecal`'s comment (963-978) explains why the sheet is welded and stays true.

## What the Enigma should show (predictions)

Resting on the evidence's experiment, which removed the same attribute at the same moment and set the same flag: what changes from it is that the implementation removes the attribute in the reading rather than by a patched `computeVertexNormals`, which is the same memory. Predictions in this campaign that scaled one figure were wrong three times; these rest on one measured run.

- One open copy near 2,489 MiB where it is 3,034; the tab's typed arrays and the WebGL buffers each about 268.4 MiB less; 2,004 WebGL buffers alive where there are 2,997; the same 3,347 meshes on the same 1,472 geometries.
- Pictures: in the evidence's nine states, about the evidence's counts (up to 508 pixels by one step, single pixels by about ten). Under each highlight mode and with parts hidden, not measured before: expected the same kind.
- The same requests. The load shorter by the normal pass and half the upload; a frame's time not predicted.

## For the pilot

1. **The picture is no longer equal pixel for pixel.** Within one step of 255 in a channel everywhere measured but for the two cases below; measured in software (SwiftShader) only, never on a graphics card, where the count of differing pixels may be other.
2. **A facet seen within about a pixel of edge-on** is lit wrongly at the few pixels of its edge it partly covers, on the measured plate exactly as from behind: a row of 80 pixels darker by up to 14 of 255 coloured, changed by up to 64 colourless. Flexible parts are drawn this way today. A correction exists for the reversed case (turning a derivative normal that faces away from the viewer back toward it, one line of shader code): measured in three.js alone, it removes the square's 153 pixels, coloured and colourless, and leaves the sphere's one, which is mis-directed rather than reversed; it is a shader of the viewer's own, which this design does not add (Alternatives).
3. **Triangles of nearly zero area**, common in STL exports, are drawn today with an arbitrary normal and now with another: up to 40 steps coloured, 63 colourless, at a few pixels along an edge. Neither is the surface's colour.
4. **Two ratified decisions are revised**: ADR-082's "computes the normals once" and ADR-056's "`computeVertexNormals()`" in a marking's path; and two sentences of the ratified markings requirement are restated (Decision 6).

## Alternatives rejected

- **Normals stored more compactly** (normalised `Int8Array` or `Int16Array` normals). With 8-bit normals in three bytes a vertex, a geometry's normals are a quarter of their bytes: about 201 MiB of the 268.4 saved instead of all of it (padded to four bytes, 179 MiB; a three-byte attribute may be converted to four by some graphics backends, believed and not checked). The picture: within one step, on more pixels (1,765 of a sphere view where flat shading differs on 7); a stored normal does not depend on neighbouring pixels, so the edge-on case does not arise (not measured on the plate). It keeps the normal pass at load, adds a quantising pass, and keeps the rigid and flexible parts shaded two ways. It is the alternative that keeps the edge-on pixels exact; it saves three quarters of the memory, and it is not what the pilot was offered. Not chosen; recorded for the pilot with item 2 above.
- **A shader of the viewer's own** (the facing correction of For the pilot, item 2, or a stored normal per facet read by `gl_PrimitiveID`, which WebGL 2 has not): changes a program three.js owns, through `onBeforeCompile`, for the rigid parts and, to keep one look, the flexible parts; and the measured correction removes only the reversed case. Out of the scope the pilot gave.
- **Merging `RIGID` and `FLEXIBLE`**: Decision 3.
- **Removing the attribute in `loadMesh` or in `copy`**: after the geometry is handed out, against ADR-082 point 8, or only for some viewers (MU6, MU7, MU11).
- **Dropping the reading's guard**: the step cannot throw today, but the guard costs nothing and keeps ADR-082's "a reading's failure fails every load that joined it" for its preparation; its test is kept (Decision 9).
- **A mount option for the old shading**: not needed by a correct design, and not the change's to add.

## Risks / Trade-offs

- [A graphics card draws the edge-on and degenerate cases otherwise, or other pixels by more than one step] → unmeasured; the reviewer's measurement is in software too; stated to the pilot.
- [A later change gives rigid parts back a `normal` attribute or a smooth material] → N1 to N3, R1, R3.
- [Time] → none claimed; the reviewer measures.

## Decision record

A new ADR-083 under `workflow/adrs/EXPORT/`, written after the reviewer's measurement and only if it confirms the design, in the register of the ADRs beside it, amending ADR-082 and ADR-056 with a dated pointer amendment in each and its line in `workflow/adrs/README.md`, building on ADR-076 (the kinds of material) and on the framework's ADR-057 (the flexible parts' flat shading). It must record:

- A part read from a model file holds positions only: the reading removes the `normal` attribute `STLLoader` makes, once, before the geometry is handed out or copied; no normals are computed for it. This replaces ADR-082 point 1's "computes the normals once" and the normals in ADR-056's "`STLLoader.loadAsync`, `computeVertexNormals()`, a `THREE.Mesh`"; ADR-082 point 8 and ADR-056's welded sheet, its averaged normals and the lift along them stand.
- Its facets are shaded from the derivatives of the position (`flatShading` on the rigid kind of material, in every look), the same vector as the stored normal for every facet drawn, and the flexible parts' shading.
- The picture: within one step of 255 of the stored-normal picture, measured, with the two exceptions and their measured sizes, and that the pilot accepted them (or what they ordered instead).
- What stands: the kinds `RIGID`, `MARKING`, `FLEXIBLE`; markings' normals and material; the counts of materials and holders; the order of drawing; viewer API 30 and documents 1 to 14.
- The measured memory and buffers on the Enigma, from the reviewer's measurement.

## Found while proposing, out of scope

- A coloured binary STL (`COLOR=` in its header) gives a `color` attribute that is uploaded and never drawn (no material sets `vertexColors`). None of the Enigma's 993 files has one (the evidence's census: positions and normals only).
- three.js uploads a geometry when it first draws it. Mounted with no view, the four-part document of Context uploaded, by its byte count, the sphere's and the cylinder's geometries and not the cubes' (on both builds), and the marked fixture fewer buffers than its parts and markings have; not investigated. The counts of a mount depend on what its view draws, which is why R1 frames its document explicitly.

## Open Questions

None for the implementation. What is the pilot's is under "For the pilot".

## Corrected in review, before the planning commit

The reviewing agent changed two things in these artifacts, and what follows from them; the proposer's text is otherwise as written.

- **No stored pictures.** The proposal compared the implementation's pictures with about sixty recorded from the base build and committed as fixtures (R3), pinned the exceptional pixels in a second test (R4), and skipped both whenever the suite's browser was not the one that recorded them. No test of this suite stores a picture; a test that skips after the next browser update holds nothing; and no later base could record the pictures again. The comparison with the base is made once by the reviewer, on the proposal's own cases and on the Enigma page, and recorded as evidence. R3 is now a test of what must hold within one run (a facet flat, lit on the side facing the viewer, never black, in every look), which MU2, MU5 and MU8 turn red; R4 and the recordings are gone.
- **The requirement does not compare with a viewer that is gone.** The delta's new requirement bounded the picture against "the picture the viewer drew ... when it stored a normal for every facet". That is the measurement of this change, not a behaviour a later reader can observe, and it is the fault the proposal itself found in two sentences of the markings requirement. The requirement states how a facet is drawn and where a pixel may be lit as from another direction; the bound of one step is in the decision record and the evidence.

## Corrected in review, after the implementation

The reviewing agent read the implementation, planted faults in it and compared it with the base (evidence.md, "The reviewer's record"). No source line changed in review. Where a sentence above disagrees, this section holds.

- **One existing test changes that Decision 9 did not name.** `tests/test_widget_e2e.py`, the on-demand restore, counted every pixel that differs between two frames of one pose under re-fitted near and far planes. Decision 9 listed that file among the tests whose margins are tens of steps; this one counted a difference of one. A normal taken from the derivatives carries a rounding that moves with the frame, so several hundred pixels differ there by one step where a few dozen did. The test now leaves out a one-step difference; its subject, a stale frame, differs by tens.
- **"Within one step" has a third exception on the Enigma page.** In a dimmed, a ghosted and a hidden state one to five pixels differ by two steps. Decision 2 and the hand-written shapes show none.
- **A one-step rounding moves from frame to frame.** The design compares the change with the base, picture by picture; it does not say that two frames of the change itself, of one pose under slightly different planes, differ by a step at several hundred pixels. Two draws of the same state are equal.
