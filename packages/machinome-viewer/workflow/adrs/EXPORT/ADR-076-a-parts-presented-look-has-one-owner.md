# ADR-076: A part's presented look has one owner

**Status:** Proposed

**Date:** 2026-09-29

**Change:** `highlight-a-part`

**Amends:** [ADR-053: A pick is bound to a declared control, and the part follows commits](ADR-053-a-pick-is-bound-to-a-declared-control.md) (how the hover lift is written and put back)

**Builds on:** [ADR-035: Reusable viewer core and declared API version](ADR-035-reusable-viewer-core-and-declared-api.md) (three.js stays private to the viewer)

## Context

Until now one thing changed a material after it was built: the hover lift
of a declared control's part. It copies each emissive colour, writes
`HOVER_EMISSIVE`, and returns a closure that writes the copies back. That
is exact while it is the only writer.

A film host needs a second writer. Videomaker's roadmap, item 2, asks for a
part tinted while the narration names it and the others dimmed or ghosted
so a housing is seen through; the pilot asked for it for the Leonardo film
*Revolutions*. The viewer's handle gains `highlight(paths, options)`, which
writes `emissive` on the named parts and `color`, `opacity`, `transparent`
and `depthWrite` on the others, and must put all of them back exactly.

Two writers that each save and restore the values they found corrupt each
other when their lifetimes interleave. Hover saves the declared emissive
and writes grey; highlight saves grey and writes its tint; unhover writes
the declared emissive over the tint; the highlight's restore writes grey,
and the part stays lifted after both are gone. An interactive host can
produce exactly that order.

## Decision

**Every departure of a mesh's material from the look it was built with is
computed by one owner from the material's recorded base values and the
overlays standing on it, and the base is written back when no overlay
stands.**

1. `presentation.ts` holds `MaterialPresentation`. It records a material's
   base `emissive`, `color`, `transparent`, `opacity` and `depthWrite` the
   first time an overlay touches it, and drops the record when the last
   overlay leaves, after writing the base back.
2. The overlays are the hovered meshes and the standing highlight. The
   presented values are a function of the base and the overlays, never of
   the current values: a highlighted mesh shows the highlight colour whether
   or not it is hovered, a hovered mesh that is not highlighted shows the
   hover grey, and dim or ghost apply to the others regardless of hover.
3. Hover and highlight are clients of the owner. Neither writes a material
   directly, and neither restores by copying.
4. Before each of the three places meshes or materials are replaced, the
   owner writes every base back and forgets; afterwards the standing
   highlight is re-resolved from its assembly paths. A material the owner
   never touched is never written.
5. The owner is inside the viewer. A host names assembly paths and a
   treatment; no three.js material, mesh or colour object crosses the
   handle.

## Consequences

- Exact restore holds in every order of hover, unhover, highlight and
  restore, and is testable without WebGL, since three.js materials are plain
  objects.
- The point search of `partOnScreen` can ask the owner which meshes are
  ghosted and see through them, without a second record of that state.
- A future overlay (for example a selection look) joins the owner rather
  than adding a third save-and-restore closure.
- A part with no declared colour renders through `MeshNormalMaterial`,
  which has no emissive and no colour: it can be ghosted but not tinted or
  dimmed. That limitation already applied to hover and is stated, not
  worked around.
