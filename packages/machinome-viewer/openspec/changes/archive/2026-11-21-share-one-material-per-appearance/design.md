## Context

Every mesh the viewer draws is a rigid part's model, a marking or a flexible part, and each is made with a material of its own by one of three constructors: `materialForColor` (`tree.ts` 55-64: `MeshStandardMaterial` with the colour, metalness 0.1 and roughness 0.6, or `MeshNormalMaterial` for no colour), `markingMaterial` (`tree.ts` 132-139: the rigid one, then `DoubleSide`, `polygonOffset` with factor and units -1) and `materialForFlexible` (`flexible.ts` 431-441: the rigid pair with `flatShading`). After construction one class writes a material: `MaterialPresentation` (`presentation.ts`, ADR-076, ADR-079), which records a material's base `emissive`, `color`, `transparent`, `opacity` and `depthWrite` when an overlay first touches it, writes the presented values computed from the base and the overlays (hover, highlight with the others kept, dimmed or ghosted), rebases the colour a model chooses (`setBaseColor`), and writes the base back when the last overlay leaves. Three places replace a mesh's material outright: `WidgetTree.setColor` when a node's colour goes from none to one or back (`tree.ts` 587-608), `FlexibleShape.setColor` (`flexible.ts` 198-203) on the same call, and `applyMarkings` for a retained marking whose colour moved (`tree.ts` 527-532). `disposeMesh` (`tree.ts` 162-170) and `FlexibleShape.dispose` dispose a mesh's material with its geometry.

The opening evidence (`workflow/evidence/enigma-material-per-part-cost-2026-11-21.md`) counted 3,347 meshes and material objects with 79 distinct appearances on the Enigma I page, read from three.js 0.156.1 that `setProgram` refreshes a material's uniforms whenever `material.id` differs from the previous draw's, and measured a still frame at 22 to 30 ms of script as shipped, 17 to 21 with one material per appearance grouped by three.js's sort, and 19 to 22 with the shipped order kept by a custom sort. Grouped, one pixel differed in four of ten pictures; with the shipped order, none. Its limits: a swap of pointers from outside, after load, with nothing of ownership, colour changes, reloads, failures or two viewers exercised.

## Goals / Non-Goals

**Goals:**

- Every picture the viewer draws is the picture it draws today, pixel for pixel, in every state it can reach: after load, under a hover, under a highlight with the others kept, dimmed or ghosted, after a colour the model chooses changes, after any interleaving of those, after an in-place update, a reload and a republish. First requirement.
- Meshes of one appearance and one look are drawn with one material, so a frame costs less script. Second requirement.
- Nothing the viewer made is retained after it is disposed, and nothing is disposed while a mesh still draws with it.
- Shown by tests that count work on the base, a parity proof against the shipped owner, the order of drawing read as the renderer would read it, and a browser picture of coincident surfaces; no wall clock and no project export.

**Non-Goals:**

- Sharing, instancing or merging geometry; drawing an idle page less often or skipping a tree update that changes nothing; lights, tone mapping and the renderer's settings other than its opaque sort; molejo; any project's source.
- Anything that lowers a part's resolution or a flexible part's sampling (deferred by the pilot).
- Viewer API (stays 30) and document versions (stay 1 to 14): verified in `widget/package.json` (`machinomeViewerApi: 30`, `machinomeDocumentVersions: [1, …, 14]`). The mount handle's methods and what they do are unchanged; no three.js object crosses it.

## Decisions

### 1. What an appearance is (attack point 3)

An appearance is a **kind** and a **colour value**. The three kinds are the three constructors: `RIGID` (`materialForColor`), `MARKING` (`markingMaterial`) and `FLEXIBLE` (`materialForFlexible`), each a constant descriptor `{ name, make }` exported beside its constructor; the holder keys by the descriptor. The colour value is a `THREE.Color` or none, and the key writes its three components so that values equal under `Object.is` share a key and values that differ do not (`String` of each, with `-0` written apart), or `none`. The constructors accept a `THREE.Color` as well as a string (`new THREE.Color(value)` copies a `Color` exactly), so a kind's material is made from the value itself.

**The premise, checked.** No other property of a part's material varies today. The constructors' other values are constants; the only writers after construction are `MaterialPresentation` and the three replacing sites, all of which go through the holder after this change (a search of `src/` for writes of `side`, `polygonOffset*`, `transparent`, `opacity`, `depthWrite`, `wireframe`, `clipping*`, `needsUpdate` and `.material` finds no other). The evidence's 79 appearances were counted over type, colour, emissive, metalness, roughness, flat shading, side, transparency, opacity, depth write and polygon offset, which is this key at rest. Colours admitted today: a marking's is a six-digit hex in either case (`viewer.ts` 2993, 3048), a choice's `on` and `off` likewise (`color.ts` 7, 18-20), a node's plain string is not checked; the committed fixtures use six-digit hex only, in both cases.

**Where the value comes from.** Exactly where the shipped code gets it, so the value is the one the shipped material carries:

- a mesh made, or a material replaced (`mesh`, `recolor` below): `new THREE.Color(color)`, as the constructors do;
- a colour the model rebases (`setBaseColor`): the mesh's present colour value, cloned, then `.set(color)`, as `base.color.set(color)` does in `setBaseColor` today.

The two differ only for a string three.js cannot read: `set` warns and keeps the colour it had, while a new `Color` stays white (checked during this proposal: `#ff0000` then `set('garbage')` stays 1, 0, 0; `new THREE.Color('garbage')` is 1, 1, 1). That is reachable through a republish of a plain-string colour onto a retained mesh, and the rule reproduces it.

**Two spellings.** `#f00`, `#ff0000`, `#FF0000` and `red` read to the same three numbers (checked: 1, 0, 0 each), so they are one appearance and one material. What it costs: nothing. What it risks: nothing observable, since nothing reads a colour string from a material; the assembly's colours come from the tree's own `color` field (`tree.ts` 656-664). Keying by the string instead would make two materials for one look, and could not express a rebase onto an unreadable string, whose value depends on the colour the mesh had.

### 2. A mesh's material is a function of what stands on it (attack point 2)

The holder (`MaterialPresentation`, kept as the class name ADR-076 gives the one owner) records for each mesh it made: its kind, its colour value, its place in the order of drawing (Decision 3) and the material it points at. A mesh's material is

  `material(appearance, look)`, where `look` = (lit, and in which colour; hovered; dimmed; ghosted)

with lit, dimmed and ghosted decided exactly as `present` decides them today (`presentation.ts` 199-205): lit when the mesh is in the highlight's lit set; dimmed or ghosted when it is in the others, not lit, and the mode is `dim` or `ghost`; hovered when it is in the hover set.

**The values, unchanged.** For the plain material `P` of the appearance (made by the kind's constructor from the colour value, never written after), a look's material carries the values `present` writes today from the base `P` (`presentation.ts` 216-227, 245-263):

- `emissive`, where the material has one: the highlight colour (`new THREE.Color(state.color)`) when lit; else `HOVER_EMISSIVE` (`new THREE.Color(0x777777)`) when hovered; else `P`'s.
- `color`, where it has one: `P.color.clone().multiplyScalar(DIM_FACTOR)` when dimmed; else `P`'s.
- `transparent`: `true` when ghosted; else `P`'s (`false` for every kind).
- `opacity`: `Math.min(P.opacity, GHOST_OPACITY)` when ghosted (`P.opacity` is 1 for every kind, so 0.15); else `P`'s.
- `depthWrite`: `false` when ghosted; else `P`'s (`true`).

**Variants.** The material for a look other than the plain one is `P.clone()` with those values set, before any mesh points at it; `Material.copy` and the subclasses' `copy` carry every other property (side, polygon offset, flat shading, metalness, roughness, `defines`). Where a look's values equal `P`'s (a `MeshNormalMaterial` hovered, lit or dimmed: no colour and no emissive), the mesh points at `P`; where two looks' values are equal (a normal material ghosted, hovered or not), they share one variant. A variant is found through its appearance by its look and, for a lit look, by the highlight colour's value, computed once per appearance and look rather than per mesh. Only one highlight stands at a time (`viewer.ts` 1101-1104), so lit variants of one colour are in use at once.

**The cases the shipped code treats specially:**

- **`MeshNormalMaterial`** (rigid or flexible, no colour): today hover, lit and dim write nothing that changes (no emissive, no colour; `opacity` and `depthWrite` rewritten with their base values), and ghost writes `transparent`, 0.15 and `depthWrite` false with `needsUpdate`. After: hover, lit and dim leave the mesh on `P`; ghost points it at the ghosted variant.
- **Lit and hovered at once:** the highlight colour, as today. **Lit and among the others:** lit, as today (`other = !lit && …`).
- **Dimmed and hovered:** the dimmed colour with the hover grey. **Ghosted and hovered:** the ghost values with the hover grey.
- **`needsUpdate` when `transparent` changes:** today it raises the material's version so three.js chooses another program on the next draw. A variant is made with its `transparent` before its first draw, so three.js chooses its program then; `P` never changes, so nothing needs choosing again.
- **A standing highlight re-resolved onto new meshes** (`presentHighlight`, `viewer.ts` 1061-1085): unchanged; `setHighlight` with the new meshes points them at their looks.
- **"Unhighlight reveals the lamp's new state":** `setBaseColor` under a highlight moves the mesh to the appearance of its new colour value and recomputes its look there; when the overlay leaves it points at that appearance's `P`. No overlay value can be taken for a base, because no base is read from a material.
- **A marking under a highlight:** lit, dimmed or ghosted as any standard material, keeping its two sides and its polygon offset (the variant is a clone).

**What is not reproduced, and why no picture can differ.** Two departures from the shipped owner's sequence, neither reachable through the mount:

- Today a mesh whose colour goes from none to one, or back, while an overlay stands on it shows its new material plain until the next overlay change, and its old material's record stays in `bases`. After, its look is recomputed at once. Unreachable: that transition happens only in a republish's `apply`, which `manifestChanged` runs after `presentation.forget()` (`viewer.ts` 2216-2219), and an update cannot change whether a node has a colour (a colour declaration is a string, `null` or a choice of two hex colours; `color.ts`).
- Today a mesh disposed while an overlay stands on it stays in the overlay's sets until the next overlay change. After, `release` removes it at once. A disposed mesh is not in the scene.

### 3. The order of drawing (attack point 1)

**Today.** three.js sorts the opaque list by `groupOrder`, `renderOrder`, `material.id`, `z`, `id` (`painterSortStable`, `WebGLRenderLists.js` 1-25) and the transparent list by `groupOrder`, `renderOrder`, `z` descending, `id` (27-47). No group or mesh of the viewer sets a `renderOrder`, so both are 0 for every item. Every mesh has a material of its own, so no two opaque items have the same `material.id`, and `z` and `id` are never reached: the opaque parts are drawn in the order of their materials' numbers, which three.js takes from one counter for the page at each material's construction. A material is made for a mesh at these points, so the order in each state is:

- **After a fresh mount or a reload's new tree:** document preorder: a node's model, then its markings in declaration order, then its flexible part, then its children in order. Reserved synchronously in the constructors, before any fetch completes (`loadMesh`, `tree.ts` 873-886, "Reserve both render identities in document traversal order"; `loadMarkings` calls `loadDecal` for every entry before its first `await`; `FlexibleShape` in the constructor). Checked on the base during this proposal: a document with a part carrying two markings and a child, a flexible part and another part gave A, its two markings, A's child, the flexible part, the last part.
- **Flexible parts and markings:** as above; they are meshes like any other in that order.
- **When a mesh receives a new material** (`WidgetTree.setColor` from none to a colour or back, which replaces the node's direct meshes' materials, or the flexible part's alone when the node has one; `FlexibleShape.setColor` on that call; `applyMarkings` for a retained marking whose colour moved): it gets a new, higher number and moves after every mesh already numbered. A colour change between two colours, a colour choice included, writes in place (`setBaseColor`) and keeps the number.
- **After an in-place update** (`manifestChanged`, `reconcile`): retained meshes keep their numbers; every mesh made for the update is numbered when it is made, during preparation, after every retained one. Inside one update a node prepares, in order, its replacement model, its new flexible part, its stale markings and its children, awaiting its model's fetch before the flexible part and the markings' fetches before the children (`prepareReconcile`, `tree.ts` 396-447), while its siblings prepare meanwhile. So the relative order of meshes made for different nodes in one update can follow fetch completion: checked on the base during this proposal, two siblings whose models and markings were replaced gave their markings in the order their models' fetches completed. A new subtree is numbered in its own preorder at once.
- **After `artifactChanged`:** every replacement is reserved before any fetch, the nodes naming the path in preorder, then the markings naming it in preorder (`tree.ts` 339-346), after every retained mesh.
- **A mesh in the scene that is not a part's:** none. The scene holds two lights and the tree's group (`viewer.ts` 412-416, 1775); the placeholder `loadMesh` reserves is never attached.

The baseline requirement "Fresh mounts draw loaded rigid assets independently of fetch completion order" rests on the first point. The two accidents (a recoloured mesh moving to the end; an update's new meshes following fetch completion) are not covered by it.

**After.** Each mesh gets a **place**, a number from a counter of the holder, at exactly the points listed: when the holder makes the mesh (`mesh`, where `loadMesh` and `FlexibleShape` construct it today) and when it replaces the mesh's material today (`recolor`, at the three replacing sites). `setBaseColor` keeps the place. The place is held on the mesh itself, under a property keyed by a module-private symbol, because the comparator reads it at every comparison; `placeOf(mesh)` is exported so that a test can read it, and is no part of the bundle's surface (`widget.ts` exports nothing of `presentation.ts`). The viewer installs one comparator on its renderer (`renderer.setOpaqueSort(drawOrderSort)`, right after the renderer is made), which is `painterSortStable` with the place where three.js reads `material.id`:

```ts
export function drawOrderSort(a: RenderItem, b: RenderItem): number {
  if (a.groupOrder !== b.groupOrder) return a.groupOrder - b.groupOrder;
  if (a.renderOrder !== b.renderOrder) return a.renderOrder - b.renderOrder;
  const p = placeOf(a.object), q = placeOf(b.object);
  if (p !== q) {
    if (p === undefined) return 1;
    if (q === undefined) return -1;
    return p - q;
  }
  if (p === undefined && a.material.id !== b.material.id) return a.material.id - b.material.id;
  if (a.z !== b.z) return a.z - b.z;
  return a.id - b.id;
}
```

An object with no place (none exists today) is drawn after every placed one, by three.js's own keys among themselves, so the order is total.

**Why it reproduces today's order in every state.** Places and the shipped material numbers are assigned by counters that only rise, at the same points of the same sequence of events, one per mesh each time; the shipped counter is also consumed by materials outside this viewer (another viewer, a test's sentinel), which leaves gaps and changes no comparison between two of this viewer's meshes. So for any two meshes of one scene, the place of one is smaller exactly when its shipped material number would be smaller, in each state above, the two accidents included; with places distinct, `z` and `id` are not reached, as today. Two viewers have two counters; each orders only its own scene. Reproducing the accidents is deliberate: changing which of two coincident surfaces shows after a recolour or an update is a choice about pictures, not part of this change.

**The transparent list** keeps three.js's own sort (no `setTransparentSort`): it never reads `material.id`, so which material a ghosted mesh points at cannot change its place, and it stays sorted by depth. A ghosted variant is transparent, so three.js puts the mesh in that list exactly when the shipped code's written `transparent` would (`WebGLRenderList.push`, `WebGLRenderLists.js` 107-125).

**Grouping by material, for the record.** Without the comparator, opaque meshes of one material are drawn together, by depth inside the group. Any two coincident surfaces between which a mesh of another appearance falls in document order can change which shows: three coincident plates red, blue, red show red today (the last drawn wins at equal depth under `LessEqualDepth`) and blue grouped. Under a highlight with the others kept, the lit variant is made after the plain materials, so the lit part would be drawn after its coincident neighbours. The evidence saw it in four of ten pictures. That is why the order is carried by the place.

### 4. Who owns a material and when it is released (attack point 4)

**The sites, today and after:**

| Today | After |
|---|---|
| `loadMesh` constructs the mesh with `material(color)` at reservation: `materialForColor`, or `markingMaterial` through `loadDecal`'s arrow | `presentation.mesh(placeholder, kind, color)`: the mesh, its place, its appearance, its material; `loadMesh` takes the kind and the tree's holder |
| `FlexibleShape`'s constructor: `new THREE.Mesh(geometry, materialForFlexible(color))` | `presentation.mesh(geometry, FLEXIBLE, color)`; the constructor takes the holder, defaulting to a new one, as `WidgetTree`'s does |
| `WidgetTree.setColor`, none to a colour or back: a new `materialForColor`, the old disposed | `presentation.recolor(mesh, color)` |
| `FlexibleShape.setColor`: a new `materialForFlexible`, the old disposed | `presentation.recolor(this.mesh, color)` |
| `applyMarkings`, a retained marking's colour moved: a new `markingMaterial`, the old disposed | `presentation.recolor(record.mesh, entry.color)` |
| `MaterialPresentation.setBaseColor`, `setHover`, `setHighlight`, `forget`: write the materials in place | point meshes at materials; write none |
| `disposeMesh`: `dispose()` on each of the mesh's materials | `releaseMaterial(mesh)` |
| `FlexibleShape.dispose`: `dispose()` on the mesh's material | `releaseMaterial(this.mesh)` |
| the viewer's `dispose()`: the materials go with the trees | the trees disposed as today, then `presentation.dispose()` |

`releaseMaterial` (exported by `presentation.ts`) finds the mesh's holder through a module `WeakMap` that `mesh()` fills, and releases it there; a mesh no holder made has its own material disposed, as today (no such mesh reaches it in the viewer). Every way a mesh is disposed today passes through `disposeMesh` or `FlexibleShape.dispose`: `WidgetTree.dispose`'s traversal, `removeMesh`, a replaced decal, `loadMesh`'s and `loadDecal`'s failure paths, a cancelled owner's cleanup (`owner.own(() => disposeMesh(mesh))`), a batch's cleanup of a prepared `FlexibleShape` or subtree, and `removeFlexible`.

**Counting.** Each appearance counts its **users**, the meshes whose appearance it is in any look; each material counts the meshes **pointing** at it. Every operation moves a mesh's counts from the old material and appearance to the new in one step. Release:

- a variant no mesh points at is disposed and dropped, **except a variant whose `transparent` differs from `P`'s** (ghosted, hovered or not), which is kept while its appearance has users;
- when an appearance's users reach zero, its `P` and every variant it kept are disposed and dropped; none can have a pointer, since every pointer is a user.

Why the ghosted variants are kept: three.js keeps every program a material has been drawn with until the material is disposed (`getProgram`, `WebGLRenderer.js` 1492-1538; `releaseMaterialProgramReferences`, 748-768), and the ghosted look is the only one drawn with another program (`opaque` is a program parameter, `WebGLPrograms.js` 245; emissive, colour and opacity are uniforms). Today, after the first ghost, every part's material holds the transparent program, and a second ghost compiles nothing. With the ghosted variants released at put-back, the last holder of that program would go and a second ghost would compile it again. Kept, a second ghost reuses them as today's materials do.

**No material is disposed while a mesh points at it:** a variant is disposed only at zero pointers, `P` and kept variants only at zero users, and every pointer is a user; counts move in the same step as the pointer; `release` deletes the mesh's record first and does nothing for a mesh it no longer holds, so a second disposal of one mesh cannot count twice.

**None outlives the viewer:** every mesh the viewer makes is released on one of the paths above; the viewer's `dispose()` disposes the pending trees and the tree, whose disposal cancels its preparations, so reserved and prepared meshes are released too; the users of every appearance reach zero and every material is disposed then. `presentation.dispose()` afterwards disposes anything left and empties the holder; L2 checks that nothing is left before it runs, so it cannot hide a leak.

**Failures and cancellations:** a failed load releases its reserved mesh through its failure path or its owner's cancellation; when its appearance has other users, only the counts fall, and no other mesh's pointer or any material's value changes. A failed replacement (`artifactChanged`, `reconcile`) cancels its batch: the reserved meshes, the prepared flexible parts and the created subtrees are released, and the live tree, which no `recolor` or `setBaseColor` reached before `apply`, is untouched. A tree disposed during loading cancels its owner, which releases what it reserved. A reload's new tree takes users of the appearances the standing tree has before the standing tree is disposed, so a reload keeps the same materials (R4).

**Bound:** at any moment the holder holds, for the A appearances that have users, at most A plain materials, at most 2A kept ghosted variants, and the variants meshes point at now, which are at most as many as the meshes under an overlay and at most 4A beyond the kept ones (hovered, lit in the one standing colour, dimmed, dimmed and hovered). What releases the rest: a hover moving across many parts releases each hovered variant when the hover leaves it; a host highlighting again and again in different colours releases each colour's lit variants at put-back; a republish that changes colours releases an appearance with its kept variants when its last mesh is released in `apply`; a long session holds what its loaded document's appearances and its standing overlays hold, and no more.

**Two viewers on one page: one holder each.** three.js would draw one material in two renderers (each keeps its own record of it and listens for its disposal), but one holder for the page would make one viewer's reload or disposal move counts the other depends on, and would number two scenes' places from one counter. One holder per mount (`viewer.ts` 602 already makes one per mount) keeps the viewers independent, at one material per appearance per viewer.

**`forget()` and `drop()`.** `forget()` points every mesh an overlay stands on back at its `P` and drops the overlays, releasing variants by the rule; it keeps its three call sites (`viewer.ts` 1770, 2169, 2218). `drop()` drops the overlays without pointing anything back: the meshes are disposed next, in the viewer's `dispose()`, and release whatever they point at. Their comments ("Every base goes back …", "The materials go with the tree, so nothing is written back") are rewritten to say that.

### 5. Who reads or writes a mesh's material (attack point 6)

- **Widget source.** `mesh.material` is assigned in `tree.ts` (`loadMesh`, `setColor`, `applyMarkings`) and `flexible.ts` (constructor, `setColor`) today, and read by `presentation.ts` (`materialsOf`), `disposeMesh` and `FlexibleShape.dispose`. After, only `presentation.ts` assigns it. Nothing else in `src/` reads a material: `viewer.ts` keys parts by mesh (`partMeshes`, `partOf`), `isGhosted` asks by mesh, `inspector.ts`, `screen.ts`, `camera.ts` and capture read none. The one map keyed by a material's identity is `MaterialPresentation.bases`, which goes.
- **three.js.** The renderer reads `material.visible` and `transparent` to list an item and every property when it draws. `Mesh.raycast`, behind picking, hover and `partOnScreen`, reads `material.side` to decide which faces a ray hits (`objects/Mesh.js`); a variant keeps its kind's side, so picking does not change. Per-object uniforms (the model-view and normal matrices) are set on every draw whether or not the material changed, so a material drawn for several meshes carries nothing of one of them.
- **Widget tests.** `presentation.test.ts` builds meshes with materials of their own and writes their properties; `color.test.ts` asserts a material keeps its identity through colour changes (lines 98, 129-147, 212-218); `tree.test.ts` compares material numbers for order (115-117, 140-141) and spies on `Material.prototype.dispose` (156-222, 1182-1194); `flexible.test.ts` reads a material's class and colour (163-165). What becomes of each is in Decision 7, "Existing tests".
- **The Python tests.** None reads a material: the word appears only in docstrings about `MeshNormalMaterial`'s colours (`test_widget_e2e.py` 1554, 1590, 1721; `test_capture.py` 447).
- **Nothing writes a material once it is handed to a mesh:** only the holder assigns `mesh.material`, and it sets a material's values only between making it and handing it out; no other module writes a material's properties. **What catches a new writer:** R3 snapshots every material when it is first seen on a mesh and compares it, after every step of a sequence through the tree and the holder, property by property under `Object.is`, its `version` included. A writer on a path R3 does not take is not seen by it; the ADR amendment states the rule for the writer who comes later.

### 6. The moment of a change (attack point 7)

Today a hover, a highlight and a put-back write materials in place; the ghost and its put-back also change `transparent` on every ghosted material, so on the next draw three.js computes each one's program parameters again (`getProgram`), and the first ghost compiles the transparent programs. The evidence measured, with one part lit: the call with its draw 22.7 to 23.9 ms kept, 30.6 to 31.9 dimmed, 209.5 to 221.5 ghosted; putting back 22.2 to 30.5, 26.6 to 27.6 and 53.6 to 54.7.

After, every one of them points meshes at materials and makes at most one material per appearance and look it has not met. A new material costs, at its first draw, three.js's first-use work for it (parameters, cache key, uniforms) and, when no live material has its program, a compile. Where the time lands:

- **A hover:** `setHover` points the hovered meshes and makes a hovered variant per hovered appearance it has not met (a clone); their first-use work lands in the next drawn frame. Their program is `P`'s, which is live, so nothing compiles. Prediction, not measured: well under a millisecond per new variant, in a frame that is several milliseconds cheaper than today's.
- **The first highlight after load:** `highlight` draws before it returns (`viewer.ts` 1108), so everything lands inside the call. Kept: the lit variants of the lit appearances (one for one part). Dimmed: also a dimmed variant per appearance among the others (79 on the Enigma page). Ghosted: a ghosted variant per appearance, and the compile of the transparent programs, which the shipped first ghost pays too. Prediction, resting on the evidence's per-look figures (re-pointing 0.4 to 4.3 ms, first frame 19.0 to 26.1): each call below today's figure, the ghosted one by the 3,346 programs not recomputed.
- **A second ghost:** reuses the kept ghosted variants; nothing is made or compiled. **A put-back:** points meshes back at `P`, already drawn; nothing is made; the lit and dimmed variants are disposed.
- **A standing highlight keeps the saving:** each mesh under a dim points at its appearance's dimmed variant, so the opaque list changes material along the order about as often as at rest; the evidence's still frame with one material made per look was 21.1 and 18.7 ms dimmed and 20.6 and 23.7 ghosted, against 24.6 and 26.3 dimmed and 28.0 and 30.3 ghosted as shipped, and 28.3 to 33.7 with one made per mesh.
- **A colour the model chooses:** `setBaseColor` points the mesh at its new colour's material. Where another part has that colour the material exists and nothing is made; where none has, one plain material is made, and disposed when the colour's last part leaves it. The Enigma page's 754 choosing parts have four pairs of colours among them; whether each of those colours always has a part was not counted.
- **A reload:** the new tree's meshes point at the materials the standing tree uses, so its first frame initialises no material where today it initialises one per mesh.

### 7. Tests (attack points 8 and 9)

A new `src/shared-materials.test.ts`, with the STL loader mocked as `tree.test.ts` does and hand-written documents only. The order of drawing is read as the renderer reads it: a helper visits the tree's visible meshes in scene order, computes each one's `z` as `projectObject` does (`WebGLRenderer.js` 1228-1252, a fixed camera), pushes them into three.js's own `WebGLRenderList` (imported from `three/src/renderers/webgl/WebGLRenderLists.js`) and sorts with `drawOrderSort` read through the module's namespace, which on the base is absent so three.js's default is used. Every new export is read through the namespace (`import * as presentation from './presentation'`), so the tests load on the base.

**Red on the base, by count:**

- **R1. One material object per appearance.** A document of twelve meshes: rigid parts in `#ff0000`, `#FF0000`, `#f00`, `red`, `#0000ff` twice and two without colour, one of them carrying two markings in `#ffffff`, and two flexible parts in `#336699`. Distinct material objects among the meshes after load: 5 (rigid red, rigid blue, rigid normal, marking white, flexible). Base: 12, one per mesh (checked during this proposal with six rigid parts: 6 of 6).
- **R2. Changes of material along the drawn order.** Six rigid parts, three red then three blue in document order: along the sorted opaque list, 1 change. Base: 5 (checked during this proposal).
- **R3. No write after a material is handed out.** A tree with rigid, normal, flexible and marked parts and a colour choice; every material is snapshotted when first seen on a mesh (every own property, colours by component, `version` included, `uuid` and `_listeners` left out); then hover, highlight kept, dimmed and ghosted with put-backs, the choice flipped, a republish recolouring a marking and giving a colourless part a colour, `artifactChanged` on one model: after every step, every material seen equals its snapshot. Base: red at the first hover, which writes `emissive` in place (checked during this proposal: same material, emissive 0 to 0x777777).
- **R4. A reload keeps the materials.** A tree, then a new tree of the same document with the same holder, the standing tree disposed after, as `replaceTree` does: every mesh of the new tree points at a material a mesh of the old one pointed at, and none of those is disposed. Base: no material shared between the two trees.

What they prove: meshes of one appearance share a material, the material changes less often along the order the renderer draws in, no material is written after it is handed out, and a reload makes no material. What they cannot: that any value is right (P, O), that the order is right (O), that the renderer is given the comparator (B1), any time.

**The order and the looks through the tree (attack points 1, 2):**

- **O1. A scripted sequence, recorded on the base.** A document with nested parts at distinct translations, colourless parts, a part with two markings, a flexible part and a part whose colour is a choice, the choice's part and the colourless part the republish colours placed before others in document order, so that a move to the end shows. Steps, each followed by what the viewer does after it (`forget` before and the standing highlight re-resolved after a replacement, as `viewer.ts` does): load; hover one part; highlight one part kept; put back; highlight dimmed; highlight ghosted; hover a ghosted part; put back both; flip the choice; a republish giving a colourless part a colour, recolouring a marking, replacing one model by its mtime and adding a node; `artifactChanged` on one model's path; a reload into a new tree with the same holder. After each step: the names along the sorted opaque list and along the sorted transparent list, and each mesh's look (class; colour and emissive by component; `transparent`, `opacity`, `depthWrite`, `side`, `polygonOffset`, `flatShading`). The applier runs it on the base first, prints the three lists per step, and writes them into the test as its expected constants; on the implementation it must give the same.
- **O2. The comparator against three.js's.** Generated items, each with a material of its own whose numbers are in the order of the items' places, with equal and unequal `groupOrder`, `renderOrder` and `z`: sorted by `drawOrderSort`, the same order as `WebGLRenderList`'s default sort. Items without a place come after the placed ones. This compares behaviour with the installed three.js on every run; a three.js whose opaque sort changes its keys turns it red.

What O1 and O2 cannot see: the renderer's frustum culling and layers (not used by the viewer), whether the viewer installs the comparator, a sequence O1 does not script, and pixels.

**The look against the shipped owner (attack point 2):**

- **P1. Generated sequences.** The shipped `MaterialPresentation` and the shipped three constructors, copied verbatim into the test as the oracle, drive one set of meshes with materials of their own; the holder drives a second set made through `mesh()`. 200 seeded sequences of 40 steps over ten meshes: every kind, with and without colour, at least two of each appearance at the start, and two meshes of kinds the test declares (a kind is any `{ name, make }`): one whose material has an emissive of its own, one transparent at opacity 0.5, so that every formula is exercised on a base that is not the constructors' default: hover a subset, highlight (lit subset, others subset or the complement, colour from `#ffb000`, `#00ff00`, `#fff`, `#FFFFFF`, `#abc`, mode), put back, `setBaseColor` on a coloured rigid or flexible mesh (from `#ff0000`, `#f00`, `red`, `#336699`, an unreadable string, console warnings captured), `forget` then `recolor` (the shipped replacement emulated in the oracle), `forget` then replace a mesh by a new one with the highlight re-resolved, `forget`, release a mesh under an overlay. After every step, for every live mesh, the two materials are compared property by property: class, every own property under `Object.is`, colours and vectors by component, `defines` and `userData` deeply; `uuid`, `id`, `version` and `_listeners` are left out (identity and counts of writes, which this change alters by design); and `isGhosted` agrees.
- **P2. The special cases, by name:** each item of Decision 2's list, the marking ghosted, the unreadable rebase, the four spellings, a highlight standing through `setBaseColor` in both orders of put-back (the lamp).

What P cannot see: the order (O), whether the renderer draws a shared material as it draws an own one (B1 and the reviewer's pixels), a write after handing out (R3), lifetime (L), and the differences left out on purpose (identity, `version`).

**Lifetime (attack point 4):**

- **L1. Nothing disposed under a mesh.** `Material.prototype.dispose` spied (passing through), recording disposed materials. Steps: a failed load of a part sharing its appearance with a live part; a republish that removes one of two parts of one colour; a republish that replaces the model of one of two parts of one colour; a failed `reconcile` and a failed `artifactChanged` with a highlight standing; a tree disposed during loading; a mesh released under a hover. After each, no live mesh points at a disposed material, and every mesh that was live before the step and still is has the look of its snapshot before it. The second, third and fourth steps are the added scenario's three conditions.
- **L2. Nothing outlives.** After every tree is disposed, pending ones included, and before `presentation.dispose()`: the holder holds no mesh, appearance or material; every material it made was disposed exactly once.
- **L3. The bound.** Hover across fifty parts one at a time; ten highlights in ten colours, in each mode, each put back; a republish changing every colour. After each put-back: no lit, hovered or dimmed variant held, at most one plain and two ghosted per appearance with users, and every material of an appearance without users disposed.
- **L4. The ghosted variants are kept.** A ghost, a put-back, a second ghost: the second hands out the same material objects as the first, and makes none. It reads the meshes' materials only, so it passes on the base, where a part's own material is ghosted again; the release of the lit variants is L3's.
- **L5. Two holders.** Two trees of one document with two holders share no material; disposing one disposes none of the other's.

**The picture (attack point 9):**

- **B1. Coincident surfaces in the shipped order** (in `tests/test_asset_load_order.py`). A version-14 posed document of three coincident plates (`plate_stl()`): p0 coloured by a choice on a driver `powered`, off `#ff0000` and on `#00ff00`; p1 `#0000ff`; p2 `#ff0000`. Mounted on demand at a fixed view, drawn after each change as that file's tests draw (`setTime`), the centre pixel is red (p2, drawn last, wins at equal depth). Then: highlighting p1 with the others kept gives a frame equal to the loaded one, since p1 is covered; put back, equal; `setDriver('powered', 1)` turns p0 green under p2, equal; back to 0, equal; highlighting p1 with the others dimmed gives a centre still red-dominant and darker; put back, equal. The applier runs it on a bundle built from the base source first, where it must pass, since it pins today's picture; grouping by material would show p1 blue at load (Decision 3).

**The picture tests that exist:**

- `test_asset_load_order.py`, "coincident parts have identical PNGs when response order reverses": holds as written. It compares mounts of one build with each other, and its two plates are two appearances made in document order, so grouping would not change it.
- `test_asset_load_order.py`, "queued models and markings keep pixels and duplicate viewer ownership": holds; eight coincident plates alternating red and blue end on blue either way, so it cannot see grouping. Its second viewer, disposed beside the first, now exercises two holders.
- `test_asset_load_order.py`, "a physically nearer surface occludes in either response order": holds; depth decides there.
- `test_widget_e2e.py`, the highlight tests (lifted, ghosted translucent, dimmed darker, refusals and hidden parts, survives an in-place update): hold; they compare patch means against thresholds, and two compare a frame after put-back with the frame before exactly, within one page.
- `test_state_color.py`: holds; its exact frame comparisons are across states within one page, over a single glass.

None compares a picture with the base's, and none has a repeated appearance after a different one at equal depth, so none could see a changed order. B1 is the test that can.

**Existing tests:**

- **E1, `presentation.test.ts`.** Meshes are made through the holder instead of with materials of their own. The cases whose base the viewer's three kinds cannot produce keep that base through a kind the test declares (a kind is any `{ name, make }`), because the formulas are relative to `P` and these are the cases that show it: "tints … and restores it exactly" and the six orders of hover and highlight keep their emissive of `0x010203` and `0x050505`, and "ghosts the others, including a normal material …" keeps its `glass`, transparent at opacity 0.5, with every assertion on a look as written. Its three `version` assertions ("Recompiled where `transparent` changed, and only there") become: `blade` and `plain` point at transparent variants while their plain materials' `version` is unchanged, `glass`'s variant has the `transparent` its plain material has, and after the put-back each points at its plain material again. "never writes a material no overlay touched" keeps its assertions; R3 states the stronger rule. Every other test keeps its assertions.
- **E2, `color.test.ts`.** "resolves finite zero/nonzero …" line 98, `expect(original.material).toBe(material)`: becomes the mesh and geometry the same objects, the place unchanged and the material the holder's for the new colour. "rebases every overlay from the current declared color, preserving material identity": meshes made through the holder; `toBe(material)` becomes the place unchanged; its colour assertions stand; disposal by release; retitled "… keeping each mesh's place". "keeps an inherited flexible color …" lines 215 and 218: the place and colour instead of the material's identity; geometry identity stands. "judges a chosen color without showing it …" holds as written (a judgement shows nothing, so the material stays the same object).
- **E3, `tree.test.ts`.** The two fresh-load order tests (92-154) hold as written, since their meshes are different appearances whose materials are made in document order, but no longer prove the order: each gains the places' order, read through the comparator. The three disposal tests (156-222) hold as written: each failing mesh is its appearance's only user, so its plain material is disposed, once. "leaves a decal's material alone …" (992-1001) and "replaces the material of a retained marking …" (1182-1194, white and `#C0C0C0`, so the white one has one user) hold.
- `flexible.test.ts` 163-165 holds. Any other test that does not hold as written is reported, not rewritten.

**Mutations,** each applied to the implementation, its test run and its output kept, the implementation restored: M1 no comparator (three.js's default sort in O1's helper): O1 red. M2 `setBaseColor` takes a new place: O1 red at the flip. M3 `recolor` keeps the place: O1 red at the republish. M4 a hover writes `emissive` into the shared material in place: R3 and P1 red. M5 `release` disposes the mesh's material whatever its counts: L1 red. M6 the appearance keyed by the colour string: R1 and P2 red. M7 ghosted variants released at zero pointers: L4 red. M8 lit variants kept: L3 red. M9 a dimmed colour computed from the material the mesh points at when the variant is made, instead of from `P`: P1 and P2 red (a `setBaseColor` under a dim). M-W `renderer.setOpaqueSort` removed and the bundle rebuilt: B1 red at load.

## What the Enigma should show (predictions)

Predictions, resting on the evidence's figures, which the reviewer's measurement decides:

- No pixel differs from the base's in the evidence's ten views, under a hover, under the three highlights or after a colour change: the order is the shipped one and the values are the shipped ones.
- 79 materials at rest, as the evidence's appearances; 80 more under a dimming highlight (79 dimmed, one lit); the ghosted ones kept after the first ghost.
- A still frame near the evidence's 19 to 22 ms with the shipped order kept (shipped 22 to 30), not near the 17 to 21 grouped: the opaque list changes material along the shipped order about 1,293 times where grouping changes it 78.
- A key press lower than shipped by up to the still frame's saving, the 754 colour-choosing parts now shared too; the evidence measured it only with them unshared (51.2 to 57.6 ms with molejo's `main`, against 57.2 to 65.4).
- The three highlight calls below the shipped figures (Decision 6), the ghosted one still paying its first compile; a second ghost with no compile.
- The earlier predictions of this campaign that scaled one figure were wrong three times; these rest on figures measured on this page for this mechanism, from outside the viewer.

## Departures from the basis the pilot was given

- **The ghosted variants are kept** while a mesh of their appearance remains, where the basis has every variant made on first use and released when its overlay ends. Released, a second ghost would recompile what today's per-part materials keep compiled, and would cost more at that moment than today. At most two materials per appearance; no picture changes.
- Not departures, but more than the basis says: a colour's spellings are one appearance (Decision 1); a colourless part under a hover, a lit highlight or a dim stays on its plain material, because today's values there are its plain values; and the order of drawing, which the basis does not mention, is carried by the place (Decision 3).

None of these changes what a maker or a host page sees or may rely on.

## Alternatives rejected

- **Let three.js group by material:** it changes which of two coincident surfaces shows (Decision 3; the evidence saw it in four of ten pictures), for at most 3 ms more of the saving there.
- **A `renderOrder` per mesh:** three.js sorts the transparent list by `renderOrder` before depth, so ghosted parts would be drawn in document order instead of back to front.
- **Places from three.js's own counter** (a bare `THREE.Material` made per mesh only to take its number) or a material kept per mesh as an order token: an object made per mesh for a number the holder's counter gives, and, for the token, 3,347 objects kept for it.
- **The place in a `Map` read by the comparator:** a hash lookup at every comparison of every frame's sort where a property read does. Not measured; the property read is the cheaper by construction.
- **Release every variant at zero** (the basis as given): Decision 4, the second ghost.
- **Keep every variant while its appearance has users:** the lit variants of every colour a host ever used would accumulate.
- **One holder for the page:** couples two viewers' lifetimes and numbers two scenes from one counter.
- **Key appearances by the colour string:** two materials for one look, and no correct key for a rebase onto an unreadable string.
- **Copy on write** (share until an overlay, then give the mesh its own material to write): it keeps the recorded bases and the writes in place this change removes, and a dimming or ghosting highlight makes one material per part, which the evidence measured at 28.3 to 33.7 ms a still frame.

## Risks / Trade-offs

- [The opaque list is sorted by the viewer's comparator] → three.js's algorithm (`Array.prototype.sort` over its list) with its keys and one property read in place of `material.id`; O2 compares it with the installed three.js's sort on every run.
- [A shared material written by later code would change every part of its appearance] → R3 on the paths it takes, and the ADR amendment's rule for those it does not.
- [three.js keeps per-material state that belongs to one object] → Read in 0.156.1: per-object uniforms are set on every draw; the evidence's ten pictures with the shipped order showed no difference; the reviewer's comparison on the page decides.
- [Ghosted variants retained] → At most two per appearance with users, released with it.
- [The order's two accidents are kept] → Deliberately (Decision 3); B1 and O1 hold them.
- [jsdom cannot run the renderer] → The comparator's installation is held by B1 in Chromium, and M-W shows B1 bites.
- [Admitted time] → None claimed beyond the reviewer's measurement.

## Decision record

An amendment to ADR-076 (`workflow/adrs/EXPORT/ADR-076-a-parts-presented-look-has-one-owner.md`), written after the reviewer's measurement and only if it confirms the design, in the register of ADR-079. It must record:

- The owner holds the materials: a mesh's material is the one of its appearance (kind and colour value) and of the look its overlays call for; no material is written after it is handed to a mesh. This replaces point 1 (bases recorded from a material and written back) and the sentence "A material the owner never touched is never written", and changes point 4: before a replacement the owner points every overlaid mesh back at its plain material and forgets the overlays.
- The order of drawing is carried by a place given where a mesh is made and where its material is replaced, and the viewer's opaque sort reads it where three.js reads `material.id`; the transparent sort is three.js's.
- Release: by counts, the ghosted variants kept while their appearance has users, for the reason in Decision 4; one holder per viewer; disposing a mesh releases its material.
- It supersedes one sentence of ADR-079's point 4, "A color change preserves the existing mesh, geometry and colored material": a colour change preserves the mesh, its geometry and its place, and points it at the material of its new colour; the none-to-colour transition remains a replacement and takes a new place.

## Open Questions

None.
