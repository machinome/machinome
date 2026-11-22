# ADR-076: A part's presented look has one owner

**Status:** Accepted

**Date:** 2026-09-29

**Change:** `highlight-a-part`

**Amended by:** [ADR-079](ADR-079-model-colors-follow-the-admitted-presentation-scope.md)
(a state-selected declared base color joins the same owner), and by the
shared-materials amendment of 21 November 2026 below (the owner holds the
materials and writes none after it is handed to a mesh)

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

## Shared-materials amendment — 21 November 2026

`share-one-material-per-appearance` makes the owner the holder of the
viewer's materials. What the decision is for stands: every departure from a
part's declared look is computed in one place, from the declared values and
the overlays standing, never from the values a material shows now. How it
is done changes.

**Holds.** `MaterialPresentation` makes every mesh a part, a flexible part
or a marking draws with. A mesh points at the one material of its
appearance, a kind of material (`RIGID`, `MARKING`, `FLEXIBLE`, each a
`{ name, make }` beside its constructor) and a colour value compared
exactly, and of the look its overlays call for. A look's values are point
2's, by the same formulas, from the appearance's plain material. A look's
material is a clone of the plain one with those values, set before any mesh
points at it; a look whose values are the plain ones stays on the plain
material.

**Written never.** No material is written after it is handed to a mesh. A
hover, a highlight, a put-back and a colour the model chooses point meshes
at other materials and back. This replaces point 1 (bases recorded from a
material and written back) and the last sentence of point 4. Point 4
otherwise stands: before a replacement the owner points every overlaid mesh
back at its plain material and forgets the overlays, and the standing
highlight is re-resolved afterwards. Code that later writes a property of
a part's material would change every part of that appearance: a new look
belongs in the owner.

**The order of drawing.** With a material per mesh, three.js's opaque sort
drew the parts in the order their materials were made, which the tree
reserves in document order before any model arrives; the requirement that
fresh mounts draw the same picture whatever order their models arrive in
rests on it. Each mesh now carries a place: a number from the owner's
counter, given where the mesh is made and where its material used to be
replaced (a part gaining or losing its colour, a flexible part or a
retained marking recoloured). A colour chosen between two colours keeps
it. The viewer's renderer sorts its opaque list by the place where three.js
reads the material's number (`drawOrderSort`, installed with
`setOpaqueSort`); the transparent list keeps three.js's sort by depth. The
order is the one the viewer drew in before, in every state, two behaviours
recorded as findings included and not changed: a mesh whose material is
replaced moves to the end, and an in-place update's new meshes can follow
which fetch finished first.

**Release.** By counts. A variant no mesh points at is disposed, except a
ghosted one, kept while its appearance has meshes: three.js keeps a
material's compiled programs only while the material lives, so a second
ghost would otherwise compile again. An appearance's materials are disposed
when its last mesh is released. Disposing a mesh releases its material
where it was made. One owner per viewer, emptied when the viewer is
disposed.

**ADR-079.** Its point 4 says a colour change "preserves the existing mesh,
geometry and colored material". It preserves the mesh, its geometry and its
place, and points the mesh at the material of its new colour. The
transition between no colour and a colour remains a replacement and takes a
new place.

**Proof.** Tests red before the change by count: material objects among
meshes of one appearance, changes of material along the drawn order, a
write to a material after it was handed out, materials made by a reload.
The order of drawing and every mesh's look through a scripted sequence,
recorded on the base and reproduced. Generated sequences compared property
by property with the previous owner, kept inside the test. Lifetime tests.
A browser test of three coincident plates, red without the sort. Ten
designed mutations and twenty faults planted in review turn named tests
red.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`): 3,347 meshes
drawn with 79 materials; forty pictures drawn in software in fixed views
and states, highlights and a colour chosen by the model among them, with no
pixel different from the base's, and one pixel different in 24 of them
when the sort is left out. Script only, with draw calls skipped: a frame in
which nothing moves 24 to 29 ms before and 17.5 to 23 after; a ghosting
highlight 211 to 224 ms before and 92 to 101 after, 55 to 60 and 22 to 27
when repeated. Not measured: any GPU's frame time, another browser. That
page declares no part controls, so no hover was drawn on it. The viewer API
and the document versions are unchanged.

[Design](../../../openspec/changes/archive/2026-11-21-share-one-material-per-appearance/design.md)
and [evidence](../../../openspec/changes/archive/2026-11-21-share-one-material-per-appearance/evidence.md)
record the cases, the tests and the measurements.

## Picture-revision amendment — 22 November 2026

`draw-only-when-the-picture-changes` gives the holder one more thing to
carry: the mount's picture revision, a counter it raises whenever it
points a mesh at another material, and at no other moment. The viewer's
loop reads it to know whether to draw
([ADR-080](ADR-080-a-continuous-viewer-draws-a-frame-only-when-its-picture-has-changed.md)).
The rule of the shared-materials amendment is what makes it sufficient:
the holder is the only writer of a mesh's material, at one place.

