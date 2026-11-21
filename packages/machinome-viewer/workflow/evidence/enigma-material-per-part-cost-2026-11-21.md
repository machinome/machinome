# What one material per part costs, Enigma I, 21 November 2026

Opening evidence for `share-one-material-per-appearance`, written by the
reviewing agent before the proposal. Measured facts with their limits;
nothing here is a design.

## Where the finding comes from

The Enigma I reconstruction (`enigma-i` at `081f4e6`), as its page is built
by the project's own tools, in the viewer at framework commit `e72d1ae7`
(after `rebuild-a-flexible-part-for-less`).

The page's scene, counted in the mounted viewer:

- 3,347 meshes, each with a material object of its own: 3,338
  `MeshStandardMaterial` and 9 `MeshNormalMaterial`.
- 79 distinct appearances among them, an appearance being the material's
  type and the values of its colour, emissive colour, metalness, roughness,
  flat shading, side, transparency, opacity, depth write and polygon
  offset. The ten largest hold 702, 506, 182, 165, 152, 115, 108, 105, 104
  and 104 meshes.
- 4,173 nodes; 426 flexible parts; 53 markings.
- 754 nodes take their colour from a choice (`{when, on, off}`), one mesh
  each, with four distinct pairs of colours among them.

## What was measured

Headless Chromium (Playwright), the page's own files, the viewer built
unminified from its unedited source with a scratch entry that exposes the
renderer, the scene and the mounted handle. WebGL draw calls were counted
and not executed, except for the pictures below, so every time is script
time on the measuring machine (a virtual machine with no GPU).

The prototype edits no source. After the page has loaded it points every
mesh whose material has the same appearance at one material object, from
outside the viewer, and puts each mesh's own material back afterwards. The
variants ran alternately in one page load.

### A frame in which nothing moves

Median script per frame over 2.5 seconds, in milliseconds, three rounds
each in three page loads:

| Page load | As shipped | One material per appearance |
|---|---|---|
| 1 | 29.4, 30.1, 28.6 | 21.0, 19.5, 17.9 |
| 2 | 26.9, 22.4, 26.0 | 18.4, 19.4, 19.5 |
| 3 | 24.0, 25.9, 26.5 | 19.7, 18.6, 19.9 |

Of it, the renderer's `render` call: 20.0 to 26.4 as shipped, 15.7 to 17.9
shared. The tree update that changes nothing is 2.7 to 3.8 either way.
3,347 draw calls either way.

Calls into WebGL per still frame, counted in page loads 1 and 2 with the
same result: `uniform*` 5,656 as shipped and 5,003 shared; `useProgram` 442
and 25; every other call 3,484 and 3,372. The calls hardly change, so the
time saved is the renderer's own script per change of material, not work
handed to WebGL.

Read from three.js 0.156.1: `WebGLRenderer`'s `setProgram` refreshes and
uploads a material's uniforms whenever `material.id` differs from the
previous draw's (`_currentMaterialId`), and its uniform setters skip the
WebGL call when the value is the cached one.

### A frame of a key press

A colour choice as shipped writes the part's own material in place, so for
this measurement the 754 colour-choosing parts kept their own materials:
830 material objects in use instead of 79. Median script per changing
frame, in milliseconds, and pictures drawn in the two seconds, three rounds
of Press and Release:

| Viewer bundle | As shipped | Shared, colour-choosing parts left alone |
|---|---|---|
| with molejo's `main` | 57.2 to 65.4 ms, 29 to 34 pictures | 51.2 to 57.6 ms, 34 to 38 pictures |
| with the published molejo, as `main` ships | 80.5 to 89.8 ms, 21 to 26 pictures | 78.6 to 88.5 ms, 21 to 26 pictures |

With the published molejo the difference does not rise above the spread.

### The order of drawing, and the picture

Read from the source: `tree.ts`'s `loadMesh` creates each mesh and its
material before any model can arrive ("Reserve both render identities in
document traversal order"), and three.js sorts the opaque list by
`groupOrder`, `renderOrder`, `material.id`, `z`, `id`
(`painterSortStable`). With one material per mesh the opaque parts are
therefore drawn in the order their materials were made. A shared material
changes that order: meshes are grouped by material, and by depth inside a
group. Which of two surfaces at the same depth shows is decided by that
order.

The same still frame, a third way: materials shared and the opaque list
sorted by each mesh's original material number, so the order is the
shipped one (`renderer.setOpaqueSort`). Along that order the shared
material changes 1,293 times, against 3,346 as shipped and 78 when grouped.
Page load 3, three rounds: 19.1, 21.5 and 21.0 ms, against 19.7, 18.6 and
19.9 grouped and 24.0, 25.9 and 26.5 as shipped.

The picture, really drawn by the software rasteriser at 998 by 868, read
back from the canvas in the task that drew it, five views (the opening
view, two turned, two close) at rest and with a key held, every pixel
compared with the shipped drawing of the same view:

| Drawn | Pictures that differ, of ten | Pixels |
|---|---|---|
| As shipped, a second time | 0 | 0 |
| Shared, grouped by material | 4 | one pixel in each, by 1 of 255 in two and by 17 of 255 in two |
| Shared, in the shipped order | 0 | 0 |

### A highlight

One part lit (one mesh), through the mounted handle's `highlight`, as
shipped, two page loads; times in milliseconds:

| The others | The call, with its draw | A still frame while it stands | Putting back, with its draw |
|---|---|---|---|
| kept | 22.7, 23.9 | 22.0, 30.7 | 22.2, 30.5 |
| dimmed | 30.6, 31.9 | 24.6, 26.3 | 26.6, 27.6 |
| ghosted | 209.5, 221.5 | 28.0, 30.3 | 53.6, 54.7 |

The same looks on shared materials, by pointing each mesh at another
material and back, two ways: one material made per shared material and
look, or one made per mesh.

| The others | Made | Materials made | Re-pointing | First frame | A still frame while it stands |
|---|---|---|---|---|---|
| kept | either | 1 | 0.4 to 1.4 | 19.0 to 22.6 | 17.3 to 23.8 |
| dimmed | per look | 80 | 1.9, 4.3 | 21.8, 25.2 | 21.1, 18.7 |
| dimmed | per mesh | 3,347 | 11.1, 7.4 | 31.0, 37.3 | 29.7, 30.4 |
| ghosted | per look | 80 | 1.8, 2.4 | 26.1, 22.6 | 20.6, 23.7 |
| ghosted | per mesh | 3,347 | 3.7, 4.0 | 27.9, 32.3 | 28.3, 33.7 |

With materials shared and no highlight standing, the still frame in those
two page loads was 17.4 and 18.0 ms.

## Limits

- Script time on one virtual machine. No GPU was involved; what a change
  of material costs a graphics card was not measured, and nothing was
  measured on a maker's hardware.
- The as-shipped still frame varied between 22 and 30 ms across rounds and
  page loads; the shared one between 17 and 21.
- The prototype is a swap of pointers made from outside the viewer after
  load. It exercised nothing of how a shared material would be owned,
  released or disposed, nothing of a part changing colour while shared, of
  a reload, a republish, a failed load or two viewers on one page.
- The key-press figures leave 754 of the 3,347 parts unshared. What a
  press costs with those shared too was not measured.
- The pictures are ten views of one document on a software rasteriser. The
  one differing pixel was not traced to a pair of parts. Ten views cannot
  show that no view differs.
- "The shipped order" above is the order of the materials each mesh had
  when the page finished loading. As shipped, a part that receives a new
  material later (a flexible part or a marking changing colour, a part
  gaining or losing its colour) receives a new, higher material number and
  moves to the end of the order. No such change happened in these runs.
- The highlight was applied to one part with one mesh. The ghosted figures
  include three.js sorting 3,346 transparent meshes by depth on every
  frame, which sharing does not change.
- The Enigma document is a project's and is not in this repository; its
  pictures cannot be committed here.
