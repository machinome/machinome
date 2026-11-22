# Where the Enigma I page's memory goes, 22 November 2026

Measured by the repository agent on the pilot's "yes" of 22 November 2026
to "Shall I measure where the 4.3 GB goes?". The 4.3 GB is the cost of one
open copy of the page, measured on 21 November after the pilot's computer
froze with two copies held (a page left in a tab is kept whole by the
browser). This file says what those bytes are.

## Method

`projects/enigma-i` at `081f4e6`, its built page (`_build-page/`) served on
this machine only. One open copy in the suite's Chromium (Playwright 1.63,
headless, 1440 by 900), with a probe build of the viewer in place of the
page's bundle: the source of framework `main` at `4b456edf` with molejo's
`main` (`363847a`), unminified, with handles on the renderer and the scene,
no source file edited. The WebGL draw calls were counted and not executed;
vertex and index buffers were still uploaded.

- **By process:** the proportional set size of every browser process, from
  `/proc/<pid>/smaps_rollup`, with a blank page, with the page before its
  model is asked for, and with the model loaded, each after two forced
  collections.
- **In the tab:** the JavaScript heap and the memory of typed arrays, from
  `Runtime.getHeapUsage`; and Chromium's own dump by allocator
  (`memory-infra`, detailed).
- **What the viewer holds:** every object of the scene visited, every
  geometry's attributes and index with their bytes and the buffers they
  stand on, grouped by kind.
- **What WebGL was handed:** every `bufferData` recorded with the buffer it
  filled; the buffers alive.
- **What the files hold:** the page's document read from disk: the parts
  that name a model file, the files they name, the triangles in each
  (binary STL: 84 bytes and 50 a triangle; every named file is one).
- **An experiment:** the typed arrays of every geometry replaced by empty
  ones after the upload, and the tab's memory read again.

One run, and a run of 21 November with another build of the viewer whose
totals agree with it within 1 % (4,251 MiB; tab 2,200; graphics 1,889;
typed arrays 1,611).

## One open copy: 4,214 MiB

| | MiB |
|---|---|
| The browser with a blank page | 214 |
| The page before its model is asked for | 285 |
| **The page with the model loaded** | **4,214** |
| of which the tab's process | 2,167 |
| of which the graphics process | 1,927 |
| of which the browser's own process and the network service | 120 |

In the tab: typed arrays 1,613 MiB, JavaScript heap 206 MiB in use, the
rest 348 MiB. In the graphics process: the WebGL buffers alive are 6,747
and hold 1,603.4 MiB (1,276.2 vertex data, 327.2 index), every byte handed
over once and none deleted; the rest is 324 MiB. Chromium's own dump agrees:
it gives the tab's array-buffer partition 1,649 MiB, and 1,636 MiB to the
buffers of the WebGL context, whose bytes the graphics process holds.

## The 1,603 MiB the viewer holds, and holds twice

The scene has 3,347 meshes and 3,347 geometries: **no geometry is used by
more than one mesh.** Their attributes stand on 6,747 array buffers of
1,603.4 MiB, which is the tab's typed-array memory, and each was uploaded
once, which is the graphics process's.

| Kind | Meshes | Triangles | MiB |
|---|---|---|---|
| A part read from a model file: not indexed, `position` and `normal`, 32-bit floats | 2,868 | 16,168,898 | 1,110.2 (555.1 and 555.1) |
| A flexible part (molejo): indexed, `position` only, 32-bit index | 426 | 28,539,352 | 489.9 (163.3 and 326.6) |
| A marking: indexed, `position` and `normal`, 16-bit index | 53 | 110,950 | 3.2 |
| | 3,347 | 44,819,200 | 1,603.4 |

## The files

The 2,868 parts that name a model file name **993 files** of 372.8 MiB,
7,816,568 triangles. Summed over the parts that name them the same files
are 16,168,898 triangles: each part parses the file it names into a
geometry of its own. 809 files are named by one part; 184 by more, up to
208. The largest repeats, in triangles held beyond one copy:

| File | Parts | Triangles each | Beyond one copy |
|---|---|---|---|
| `lamp_attachment-LampMetalCap` | 26 | 118,850 | 2,971,250 |
| `historical_contact_pin-HistoricalContactPin` | 104 | 7,384 | 760,552 |
| `BatteryFloorScrew` | 11 | 39,530 | 395,300 |
| `RearSleeveScrew` | 9 | 47,326 | 378,608 |
| `circuit_route_annotations-ReturnTerminalMarker` | 208 | 1,760 | 364,320 |
| `circuit_route_annotations-ForwardTerminalMarker` | 208 | 1,760 | 364,320 |
| `RearKeyScrew`, `KeyScrew` | 9 each | 38,014 | 304,112 each |

Held once a file instead of once a part, at the 72 bytes a triangle these
geometries take, the parts read from files would be 536.7 MiB where they
are 1,110.2: **573.5 MiB less in the tab, and the same less in the
graphics process.**

The browser's requests for a model file named by several parts: the server
answered the lamp cap's file once a page load, not 26 times. The file is
fetched once and parsed once a part.

## The experiment

With every geometry's typed arrays replaced by empty ones after the upload
(1,603.4 MiB of them), and two collections: the tab's process went from
2,167 MiB to 1,041, its typed-array memory from 1,613 MiB to 499, and the
graphics process stayed at 1,928. What stayed in the tab is the flexible
parts' arrays, which their shapes hold as well as their geometries. The
viewer picks a part under the pointer by casting a ray at these arrays, so
this is a measure of what the tab's copy weighs and not a way to shed it.

## What the figures say

Of 4,214 MiB, 3,207 are the model's triangles held twice, once in the tab
and once in the graphics process. Three things would shed part of it
without changing how many triangles any part has:

| | Less, per open copy |
|---|---|
| One geometry per model file | 1,147 MiB (573.5 in each process) |
| No `normal` attribute on parts read from files (a facet's normal taken while drawing, as the flexible parts are drawn) | 1,110 MiB alone; 537 MiB after the first |
| No copy in the tab after the upload | 1,110 MiB alone, and it needs another way to pick a part |

## Limits

- Headless Chromium on a virtual machine with no graphics card: the
  graphics process's buffers are ordinary memory here. On a machine with a
  graphics card that share lives in its memory or in memory shared with
  it, and how the pilot's machine counts it is not visible from here.
- One run of this method; the totals of 21 November agree.
- The draw calls were not executed. No time is claimed.
- Chromium only.
- The JavaScript heap's 206 MiB was not broken down.
- Nothing here measures what loading costs: how long the parses take, or
  the peak while the page loads.
