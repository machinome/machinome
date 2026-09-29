## Context

Every mesh the viewer draws owns its material instance: `materialForColor`,
`materialForFlexible` and `markingMaterial` build a new material per mesh
(`loadMesh`, `FlexibleShape`, `loadDecal`). A declared colour gives a
`MeshStandardMaterial`, which has `color` and `emissive`; no colour gives a
`MeshNormalMaterial`, which has neither. Changing one material therefore
changes one mesh, and nothing else shares it.

Hover (`liftParts` in `viewer.ts`) copies each emissive of the hovered
control's meshes, sets `HOVER_EMISSIVE` (0x777777), and returns a closure
that copies the saved values back. The part surface calls it on hover and
the closure on unhover, and `partSurface.clear()` runs before each of the
three places meshes or materials are replaced: `replaceTree` (via
`rebuildPartControls`), `manifestChanged` (before `tree.reconcile`, since
`setColor` replaces materials) and `artifactChanged`. A mesh's visibility is
owned by `AssemblyNavigation.apply` -> `WidgetTree.applyVisibility`, which
writes `group.visible` and `mesh.visible` only.

A film mounts with `renderMode: 'on-demand'` and `partControls: 'none'`, so
it never hovers; an interactive host may hover and highlight at once.

## Goals / Non-Goals

**Goals:**

- A host tints named parts and keeps, dims or ghosts all others, and puts
  every material back exactly.
- Hover and highlight cannot corrupt each other's restore.
- A ghosted housing does not stop a host locating the part inside it.

**Non-Goals:**

- No outline or glow pass: no post-processing, no second render target.
  The tint is the material's own emissive.
- No per-part opacity or colour API, and no animated fade: a film that
  wants a fade calls `highlight` per frame with the state it wants.
- No change to what a press or hover picks: a ghost still receives a press.
- No change to visibility, focus or the navigation state.

## Decisions

### D1. The member

```ts
export type OthersMode = 'keep' | 'dim' | 'ghost';
export interface HighlightOptions { color?: string; others?: OthersMode; }

interface ViewerHandle {
  highlight(paths: readonly AssemblyPath[], options?: HighlightOptions): () => void;
}
```

It validates everything first (D6), applies, renders with
`renderer.render(scene, camera)` exactly as `setView` does, and returns the
restore function.

### D2. What each part looks like

The highlighted meshes are every mesh under each named path's group (own
model, descendants, flexible mesh, decals). The others are every other mesh
in the tree. For each material:

- **Highlighted:** `emissive` set to `color`. A `MeshNormalMaterial` (a part
  with no declared colour) has no emissive and is left as it is, the rule
  hover already states (`drive-the-run-by-touch` D7); the reference says so.
- **Others, `'keep'`:** unchanged.
- **Others, `'dim'`:** `color` multiplied by `DIM_FACTOR` (0.35). A
  `MeshNormalMaterial` has no colour and is left as it is.
- **Others, `'ghost'`:** `transparent = true`, `opacity =
  min(opacity, GHOST_OPACITY)` (0.15), `depthWrite = false`, for every
  material type including `MeshNormalMaterial`. three.js draws transparent
  objects after opaque ones, so the highlighted part is drawn first and the
  ghost blends over it; with no depth written, ghosts do not hide one
  another's far faces.

`material.needsUpdate` is set whenever `transparent` changes, on applying
and on restoring. `#ffb000`, 0.35 and 0.15 are initial constants; the apply
step may retune them once against the pixel checks and records the values
in evidence.

### D3. One owner of a material's departures

A new `presentation.ts` holds `MaterialPresentation`, the only writer of a
material's `emissive`, `color`, `transparent`, `opacity` and `depthWrite`
outside material construction:

- The first time any overlay touches a material, it records the material's
  base values. The presented values are always computed from the base and
  the standing overlays, never from the current values.
- Overlays: the hovered meshes (set by hover) and the standing highlight
  (highlighted meshes, others, mode, colour). Precedence on `emissive`: a
  highlighted mesh shows the highlight colour whether or not it is hovered;
  a hovered mesh that is not highlighted shows `HOVER_EMISSIVE`. Dim and
  ghost apply to others whether or not they are hovered.
- When no overlay touches a material any more, its base is written back and
  the record dropped: that is what "exactly" means, and it holds in any
  order of hover, unhover, highlight and restore.
- `forget()` writes every base back and drops all records; it runs before
  each mesh-replacement point.
- `isGhosted(mesh)` answers the point predicate (D5).

`liftParts` becomes `presentation.setHover(meshes)` returning
`() => presentation.setHover([])`, so the part surface's `highlight`
collaborator keeps its signature. This is the decision recorded in the
draft ADR-076.

### D4. One standing highlight; a stale restore is a no-op

A second `highlight` while one stands throws
`highlight is already applied; call the function the previous highlight
returned before highlighting again`. Composition was considered and
rejected: two `others` modes have no single meaning, and the film already
diffs its per-frame state before calling (as it does for `hidden` in
`src/film.js`). The restore function carries a token; it clears the
highlight only if that token still stands, then renders. Calling it twice,
or after `dispose()`, does nothing.

### D5. A ghost does not hide a tracked part

`track-a-part-on-screen` finds `partOnScreen`'s point with
`nearestVisibleMesh`. With this change, that search skips meshes
`presentation.isGhosted` reports, so the point of a gear inside a ghosted
housing is found on the gear. `controls()` points, hover and presses keep
the unfiltered nearest hit: what a press reaches does not change.

### D6. Refusals, before any mutation

- `paths` not an array, or empty: throws
  `highlight needs at least one assembly path`.
- Any path unknown or ambiguous: `requirePath`'s error naming the path.
- `color` not `#rgb` or `#rrggbb`: throws naming the value. (three.js's
  colour parser warns and keeps the old colour on an unknown string, which
  would pass silently.)
- `others` not one of `keep`, `dim`, `ghost`: throws naming the value.
- A second highlight (D4), or a disposed viewer: throws.

### D7. Visibility, focus and replacement

Materials are the only thing touched: a hidden or unfocused part stays
hidden, and if the host shows it later it appears highlighted, dimmed or
ghosted per the standing state. At `replaceTree`, `manifestChanged` and
`artifactChanged`, `presentation.forget()` runs before meshes or materials
are replaced (beside `partSurface.clear()`), and after the new tree is in
place the standing highlight is re-resolved from its paths and re-applied.
A path the new tree no longer has is dropped, the rule
`AssemblyNavigation.reconcile` applies to hidden paths; if none remain the
highlight lapses and its restore does nothing. `dispose()` drops the owner
without restoring, since the materials are disposed with the tree.

## Risks / Trade-offs

- [Transparent sorting] -> three.js sorts transparent objects by object
  centre, so interpenetrating ghosts may blend in a varying order between
  poses. With depth writes off the artefact is a small shade difference,
  not a missing surface. Inspected by eye at apply; the film sees it only
  where two ghosts overlap.
- [Colourless parts get no tint and no dim] -> the same honest limitation
  hover has. Leonardo's sawmill declares a colour on all 108 of its parts.
  Substituting a lit material was rejected: it would change what the part
  looks like beyond the tint and complicate exact restore.
- [Moving hover onto the owner touches a working feature] -> the existing
  hover tests (`partSurface.test.ts`, "hover is a cursor, a title and a
  highlight") pin it; the new interleaving test proves the defect the old
  closure had.

## Migration Plan

Additive. Hover looks exactly as before. A host at API 27 lacks the member.

## Open Questions

None beyond the constants in D2, which the pixel checks settle.
