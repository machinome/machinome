# ADR-083: A part read from a file holds its positions alone, and its facets are lit from their own planes

**Status:** Accepted

**Date:** 2026-11-22

**Change:** [draw-rigid-parts-without-stored-normals](../../../openspec/changes/archive/2026-11-22-draw-rigid-parts-without-stored-normals/)

**Amends:** [ADR-082: One reading of a model file is one geometry, held by count](ADR-082-one-reading-of-a-model-file-is-one-geometry-held-by-count.md)
(its point 1, "computes the normals once"),
[ADR-056: A marking is a decal mesh in the part's own group, and the bias over the surface is the viewer's](ADR-056-a-marking-is-a-decal-in-the-parts-own-group.md)
(the `computeVertexNormals()` in the path a marking's file takes)

**Builds on:** [ADR-076: A part's presented look has one owner](ADR-076-a-parts-presented-look-has-one-owner.md)
(the kinds of material and their looks), and on the framework's ADR-057,
which chose flat shading for the flexible parts

## Context

After ADR-082 the 2,868 parts the Enigma I page reads from model files
stood on 993 geometries of 536.7 MiB in the tab and the same again as
WebGL buffers. Half of each was a `normal` attribute: three.js's
`STLLoader` makes one from the file, and the viewer overwrote it with
normals of its own, computed from the positions, one normal a triangle
written on its three vertices. The file's normals were never drawn.

A flexible part has no such attribute. Its material has `flatShading`,
under which three.js takes a fragment's normal from the derivatives of its
position on screen. For a flat facet that is the same vector the viewer
was storing.

The pilot was offered this as the second of three ways to shed part of
one open copy's memory, with the warning that shading could differ by a
hair at edges, and ordered it after trying the first.

## Decision

**A part read from a model file holds no normals, in the page or in
WebGL, and each of its facets is lit by the normal of its own plane,
taken while drawing.**

1. **The reading removes the attribute.** Where a reading computed its
   normals it now deletes the `normal` attribute `STLLoader` made: once a
   reading, before any part is handed the geometry and before a copy is
   made for a further viewer, in the guarded step whose failure fails the
   reading. Nothing removes it later, and no normals are computed for a
   file part at all. ADR-082's point 8 stands: nothing writes a part's
   geometry after it is handed out.
2. **The rigid kind of material is flat.** `RIGID` makes the material it
   made, with `flatShading` set: a `MeshStandardMaterial`, or a
   `MeshNormalMaterial` for a part with no colour. Every look (hovered,
   lit, dimmed, ghosted) is a clone and keeps the flag. Its numbers are
   then the flexible kind's; the two kinds stay two, so the count of
   materials, which meshes share one and the order of drawing do not move.
3. **A marking keeps its normals.** Its decal is welded, given averaged
   normals and lifted along them, from a copy of the file's geometry, as
   ADR-056 decided; its material is not flat. The flag is set in the rigid
   kind and not in the constructor a marking's material is built on.
4. **Which way a facet is lit.** The derivative normal faces the viewer
   whichever way a triangle is wound, and a triangle the viewer draws of a
   rigid part is one whose stored normal faced the viewer too (every rigid
   material is front-sided). A part wound inside out, and a part under a
   mirroring transform were a document able to make one, are lit as
   before.

## What the picture does

The picture is not equal to the one stored normals drew. Measured in
software, never on a graphics card:

- **Within one step of 255 in a channel** in every case but those below.
  On hand-written shapes (cubes wound outward and inside out, spheres near
  and far, a 512-sided cylinder, four parts under every highlight mode, a
  marked fixture; coloured and colourless): 77 pictures, none by more. On
  the Enigma I page: at most 534 of a picture's 605,864 pixels, in sixteen
  states.
- **A rounding step now moves with the frame.** A stored normal was the
  same number at every pixel of a facet; a derivative normal is computed
  at each pixel, and its last bit differs from one frame to another. Two
  frames of one pose under slightly different near and far planes differ
  by one step at several hundred pixels where they differed at a few
  dozen. Two draws of the same state are still equal.
- **A facet seen within about a pixel of edge-on** can be lit as from
  another direction at the pixels of its edge: on a plate seen 0.2 degrees
  above its plane, a row of 80 pixels by up to 14 steps, 64 with no
  colour; nothing at half a degree or more. On the Enigma page: one pixel,
  on the silhouette of a small pin, by 11, in three of sixteen states; and
  one to five pixels by 2 in three others.
- **A triangle of nearly zero area** that the browser still draws is lit
  from an arbitrary direction, as it was before from another: up to 40
  steps, 63 with no colour, at a few pixels along an edge.

The flexible parts were drawn this way already and show the same cases.
The pilot was told of each before integration.

## Consequences

- A file part's geometry is its positions: twelve bytes a vertex, one
  WebGL buffer, half of what it was. A second viewer's copy is half too.
- No pass over a file's vertices when it is read.
- A test that counted every differing pixel between two frames of one
  pose (`test_widget_e2e.py`, the on-demand restore) now leaves out a
  pixel that differs by one step.
- The viewer needs the derivatives extension where it runs on WebGL 1, as
  the flexible parts already did.
- The viewer API stays 30 and the document versions 1 to 14.

## Alternatives

- **Normals stored in a byte a component:** exact at an edge-on facet,
  within one step elsewhere on more pixels; about 201 of the 268 MiB a
  process saved, with the normal pass kept and a second one added, and
  rigid and flexible parts shaded two ways. The one alternative that
  removes the edge-on case; recorded for the pilot.
- **A shader of the viewer's own** that turns a derivative normal facing
  away back toward the viewer: it removed the plate's row and not a
  curved part's pixel, and it changes a program three.js owns.
- **Merging the rigid and flexible kinds:** changes the counts of
  materials for no measured gain.
- **Removing the attribute later**, in a mesh's load or in the copy:
  after the geometry is handed out, or only for some viewers.
- **Pictures recorded from the previous viewer as a permanent test:**
  valid only in the browser that recorded them, and no later base can
  record them again. The comparison was made once, in review.

## Proof

A widget test file on the real tree with three.js's own STL parser: the
attributes of every file part's geometry, the calls that compute or remove
normals and when, and the flag on every material a part points at, after a
mount, a reload, updates in place and in a second viewer's copy, and in
every look; five red before the change, one a guard of picking. In
Chromium: one buffer a file geometry, of twelve bytes a vertex, where
there were two; the bytes the markings add, unchanged; and the picture by
what holds within one run: each face of a cube flat, the faces'
brightnesses in the order and at least half the gaps recorded before the
change, none black, in every look, wound outward and inside out, coloured
and not. Eleven designed mutations and eight faults planted in review
turn named tests red; none stood.

The comparison with the viewer that stored normals was made once, in
review, by a bundle built from each: 103 pictures of hand-written shapes
(77 within one step; 224 pixels by more, all in the plate seen edge-on and
the cube with triangles of no area), and thirty-four pictures of the
Enigma I page in sixteen states.

**Measured** on the Enigma I page (`enigma-i` at `081f4e6`) in Chromium,
draw calls counted and not executed, one run of each build: one open copy
2,489 MiB where it was 3,034; the tab 1,311 MiB where it was 1,578, its
typed arrays 770.7 where they were 1,039.1; the graphics process 1,057
where it was 1,334; 2,004 WebGL buffers of 761.5 MiB where there were
2,997 of 1,029.9, on the same 1,472 geometries. The typed arrays and the
buffers are each 268.4 MiB less. The peak while the page loads 2,612 MiB
where it was 3,265; while a reload holds two models, 3,579 where it was
4,581. The same draw calls. Four loads took 10.1 to 10.7 s where the base
took 10.5 to 12.4, which is not claimed as a gain. Not measured: any
graphics card, where the derivatives are the card's own arithmetic and the
count of differing pixels may be other; the time of a frame; another
browser.

[Design](../../../openspec/changes/archive/2026-11-22-draw-rigid-parts-without-stored-normals/design.md) and
[evidence](../../../openspec/changes/archive/2026-11-22-draw-rigid-parts-without-stored-normals/evidence.md)
record the cases, the tests and the measurements.
