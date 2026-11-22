# The stored normals of the parts read from files, 22 November 2026

Measured by the repository agent on the pilot's "ok, merge and next" of 22
November 2026, the next being the second of three ways to shed part of one
open copy's memory that the page's measurement gave
(`enigma-page-memory-2026-11-22.md`): no `normal` attribute on the parts
read from model files, a facet's normal being taken while drawing, as the
flexible parts are drawn. This file says what that would save and what it
would do to the picture, before anything is built.

## What the viewer does today

A part read from a model file arrives from three.js's `STLLoader` not
indexed, with a `position` and a `normal` attribute of 32-bit floats, three
vertices a triangle. The reading then calls `computeVertexNormals`
(`tree.ts`, `STL_READING.read`), which for a geometry with no index writes
each triangle's own normal on its three vertices: the file's normals are
not what is drawn. The part's material is a `MeshStandardMaterial` (a
`MeshNormalMaterial` where the part has no colour) with three.js's default
shading, which reads that attribute (`tree.ts`, `materialForColor`).

A flexible part has no `normal` attribute at all. Its material is the same
`MeshStandardMaterial` with `flatShading: true` (`flexible.ts`,
`materialForFlexible`), under which three.js takes the normal in the
fragment shader from the derivatives of the position. The comment there
says why: "that is the look every other part already has".

Nothing else in the widget's sources reads a part's normals: `liftDecal`
deletes them from its copy before welding a marking, and
`liftAlongNormals` reads the normals it has just computed on that welded
copy.

## Method

`projects/enigma-i` at `081f4e6`, its built page served on this machine
only, in the suite's Chromium (Playwright 1.63, headless, 1440 by 900,
software drawing), with a probe build of the viewer in place of the page's
bundle: the source of framework `main` at `6aee67ef` with molejo's `main`
(`363847a`), unminified, with handles, no source file edited. The
experiment is two patches made in the page, not a change to the source:

- before any model is asked for, `BufferGeometry.prototype.computeVertexNormals`
  is replaced by a function that, for a geometry with no index, deletes the
  `normal` attribute instead of writing it, and otherwise does what it did
  (a marking's welded copy keeps its normals);
- before a picture is taken, the material of every mesh whose geometry has
  no index and no normals is given `flatShading: true`.

The pictures are of nine states reached through the mount's handle (the
mount; the case at 0.4; the flap at 60 degrees; a wheel three teeth on; a
key pressed; after `reload()`; the case at 0.4 again; a key pressed again;
the model seen from behind), really drawn in software, and compared with
the pictures of the same states from the same build without the patches.
Only pictures drawn after the materials were changed are compared: a
picture taken on screen in a state where the patch had just changed a
material shows the frame drawn before it, and the forced draw of that
state is compared instead. The memory is by the method of
`enigma-page-memory-2026-11-22.md`, one run, draw calls counted and not
executed.

## The picture

Outside the panel's rail a picture has 605,864 pixels, nearly all of them
the model.

| State | Pixels that differ | By more than 1 of 255 | Largest difference |
|---|---|---|---|
| The mount | 508 | 0 | 1 |
| The case at 0.4 | 258 | 0 | 1 |
| The flap at 60 degrees | 283 | 1 | 11 |
| A wheel three teeth on | 283 | 1 | 11 |
| A key pressed | 285 | 1 | 11 |
| After `reload()` | 508 | 0 | 1 |
| The case at 0.4 again | 258 | 0 | 1 |
| A key pressed again | 259 | 0 | 1 |
| Seen from behind | 203 | 0 | 1 |

At most 0.08 % of a picture's pixels differ, each by one step of 255 in a
channel, and in three states one pixel differs by 11.

## The memory

| One open copy | With stored normals | Without |
|---|---|---|
| All browser processes, settled | 3,034 MiB | 2,489 MiB |
| The tab | 1,578 | 1,310 |
| Its typed arrays | 1,039.1 | 770.7 |
| The graphics process | 1,334 | 1,058 |
| The 993 geometries of the 2,868 parts read from files | 536.7 MiB (268.4 positions, 268.4 normals) | 268.4 MiB |
| WebGL buffers alive | 2,997 of 1,029.9 MiB | 2,004 of 761.5 MiB |
| Peak while the page loads | 3,265 MiB | 2,615 MiB |
| Peak while `reload()` holds both models | 4,581 MiB | 3,560 MiB |

The typed arrays and the WebGL buffers are each 268.4 MiB less: the
`normal` attribute of the 993 geometries. The flexible parts' 489.9 MiB and
the markings' 3.2 MiB do not move.

## Limits

- A software rasteriser on a virtual machine with no graphics card. A
  graphics card computes the same derivatives with its own arithmetic; how
  many pixels differ there, and by how much, was not measured.
- Nine states of one page. No part of this page is seen from inside, is
  mirrored, or has triangles wound the other way round as far as the
  pictures show; what derivative normals do to such a part was not tried.
- No highlight, no hidden part, no second viewer and no marking's own
  shading were compared here: a marking keeps its normals in the
  experiment.
- One run of the memory. No time is claimed.
- The experiment patches three.js in the page; it is not the
  implementation, which would not make the attribute at all.
