# Spike (cycle 0): the clocked Curta before the camera

Status: evidence note, 1 October 2026, branch `curta-spike` from `curta-video`
ad8f444. Not ratified; it informs cycles 1 to 4 of the plan beside it. No
product file of Videomaker was changed; the Curta project received only its
untracked `export/clocked_curta/`.

**In one line.** The framework's and the viewer's clocked requests agree bit
for bit on 23 + 145, a restored bank with the crank mid-stroke is accepted and
poses deterministically, a highlight works on the clocked export and survives
a restore. But **the stage's mount options refuse a clocked document**
(`on-demand rendering requires a posed document without instructions`), and
the one mode the viewer admits, `continuous`, costs about 12 s per 1080p frame,
so a viewer change is needed before cycle 2.

## Machine and versions

| what | value |
|---|---|
| machine | 16 cores, 15 GiB, Linux 6.8; projects on virtiofs (`projects/` is a symlink to `/mnt/data/machinome-projects`) |
| Curta project | `Calculators/Curta-Type-I-3x` `main` c214704, model `clocked_curta` = `simulation.clocked:ClockedCurta` |
| framework | editable checkout `main` 6a575f0 (metadata says 0.7.0), workspace venv, Python 3.12.3 |
| viewer bundle | `machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`, API 28, sha256 5280a86be7cbe532…, viewer checkout 94cfcc0 |
| Node, Chromium | Node v24.11.1; Playwright 1.62.0 headless shell 1234 with the stage's `--use-angle=swiftshader --enable-unsafe-swiftshader` |
| posed baseline | Leonardo `export/hydraulic_sawmill` (document version 4, source revision 28b43bc…), read only |

Durations were taken while other agents ran their suites in other worktrees
(a vitest of another `curta-video` worktree was running at 01:50); the load
average is recorded per section in `spike/browser.json` and `spike/cost.json`
(1-minute load from 0.9 when the first browser run started to 21 during the
cost runs, most of it this spike's own
software-rendering GPU process at up to 1300 % CPU). Compare durations within
one table, not across machines.

## The scripts

All under `spike/`; results committed beside them.

| script | answers | run as |
|---|---|---|
| `export_facts.py` | 1 | `<venv>/bin/python export_facts.py <export> export-facts.json` |
| `scenario.py` | 2 | `env -C <Curta realpath> PYTHONPATH=<Curta realpath> <venv>/bin/python scenario.py scenario.json` |
| `harness.mjs` | (shared) | Chromium as a server (PID for `/proc`), an HTTP server for the bundle and exports, the stage's host layout and mount options |
| `camera.mjs` | camera choice | `node camera.mjs <bundle> <export> <out dir> '<candidates>'` |
| `browser.mjs` | 3 to 8 | `node browser.mjs <bundle> <Curta export> scenario.json <sawmill export> <results.json> <stills dir> [sections] [cycles]` |

Results: `export-facts.json`, `scenario.json`, `browser.json` (sections
parity, restore, highlight, resize), `cost.json` (sections cost, posed, 30
cycles), and five 960×540 stills `stills/still-<f>.jpg` of the 23 stroke at
f = 0, 0.3, 0.5, 0.7, 1.

The camera used everywhere (`VIEW` in `browser.mjs`): camera
`[240, −240, 300]`, target `[0, 0, 10]`, up `[0, 0, 1]`, fov 40. It shows the
crank, the result dials and the setting slides (chosen by eye from
`camera.mjs` candidates).

## 1. The export

`env -C <Curta> PYTHONPATH=<Curta> machinome export clocked_curta -o export/clocked_curta --no-widget`
succeeded: `Exported to export/clocked_curta`.

| fact | value |
|---|---|
| document `version` | **8** |
| `states` | yes, 18: `clearing_check`, `result_0.value` … `result_10.value`, `turns_0.value` … `turns_5.value` |
| `instructions` | yes: `Turn crank` = `{by: {crank_rotation: 360}, duration: 6}` |
| `clocked` | yes, keys `bounds clock commits identity limits own`; identity `18f8b447b410de79b8f161e0a95a02e2bdbca28207cc9b08a8679dddf84d63c7` |
| drivers | 23: `digit_1`…`digit_8` (range 0–9, unit `digit`, no dtype), `crank_rotation`, `crank_elevation`, `carriage_rotation`, `carriage_elevation`, `clearing_rotation`, `marker_1_rotation`…`marker_10_rotation` |
| `animation` | `{fps: 30, frames: 360}` (present, but no `loop`) |
| `source-revision.txt` | **not written** (see below) |
| tree | 627 nodes; 390 mesh references, 149 distinct meshes |
| on disk | 157 files (156 STL + `manifest.json`), 28 833 432 bytes (27.5 MiB); manifest 1 863 678 bytes |
| export time | 66.7 s wall, 221 s user, 113 s system, peak RSS 1.55 GB (`/usr/bin/time -v`), on a warm project `_build/` (7 marking STLs regenerated) |

**`source-revision.txt` is not the framework's.** `machinome export` writes
none; the Leonardo export has one because the Leonardo project's
`scripts/gallery.py` writes `git rev-parse HEAD` beside its exports. Videomaker
reads it in two places: `python/machinome_movie/evaluate.py` (`_read_revision`
returns `None` when the file is missing, no refusal) and `src/movie.mjs` line
582, which reads it with `readFile` and then requires
`Pin model.sourceRevision to the export source-revision.txt before rendering`;
a missing file there fails on the read (read from the source, not run). The
Curta project has to write it the way Leonardo does (cycle 4), or a cycle must
decide otherwise.

Setting slide paths, read from the manifest (`export-facts.json`,
`input_selector_paths`): `input_selectors/selectors/digit_selector_axle_<n>/selector_knob_1_<id>`
for each digit, e.g. `…/digit_selector_axle_1/selector_knob_1_419057`; the
result dials are `carriage/registers/result_register/<p_…>`; the crank is
`main_drive/crank`. The class attribute `ClockedCurta.input_selectors` is the
assembly `input_selectors` in the export.

## 2. The scenario in Python

`scenario.py` over `Sim(ClockedCurta())`, every request through the public
API; `trigger('Turn crank')` **returns the request**, so the instruction is
used directly. `register_reading(sim)` reads **23** after the first stroke and
**168** after the second (turns counter 1, then 2). The whole scenario, replayed
from `sim.reset()`, gives identical records (`repeat_identical: true`).

| # | request | origin → end | admitted | commits | stops | ms |
|---|---|---|---|---|---|---|
| 0 | `move('digit_1', to=3)` | 0 → 3 | 3.0 | 0 | 0 | 22.9 |
| 1 | `move('digit_2', to=2)` | 0 → 2 | 2.0 | 0 | 0 | 22.6 |
| 2 | `trigger('Turn crank')` (by 360) | 0 → 360 | 360.0 | 1, at fraction **1.0**, value 360.0 | 0 | 45.2 |
| 3 | `move('digit_1', to=5)` | 3 → 5 | 2.0 | 0 | 0 | 22.9 |
| 4 | `move('digit_2', to=4)` | 2 → 4 | 2.0 | 0 | 0 | 22.5 |
| 5 | `move('digit_3', to=1)` | 0 → 1 | 1.0 | 0 | 0 | 21.8 |
| 6 | `trigger('Turn crank')` (by 360) | 360 → 720 | 360.0 | 1, at fraction **1.0**, value 720.0 | 0 | 43.0 |

`Sim(ClockedCurta())` construction: 1.91 s. The bank has 41 entries (23
drivers, 18 states), all `0` before the first request.

What the film must know from this:

- **A stroke is one commit, at its very end.** The relation
  `(crank_rotation, …, turns_5.value) commits (result_0.value, …, turns_5.value)`
  fires once per revolution at fraction 1.0 and writes all 17 register states
  at once (first stroke: `result_0.value 3`, `result_1.value 2`,
  `turns_0.value 1`, the rest 0; second: `8, 6, 1` and `turns_0.value 2`).
  So by the plan's pose rule no commit is written for any f < 1: the dials'
  motion mid-stroke is the closed-form pose of the crank and the standing
  bank, which is the model's own design (`register_reading`'s docstring:
  "committed digits, distinct from a mid-stroke dial's moving reading"). The
  stills show it: at f = 0.3 the units dial is rolling between 1 and 2, at
  f = 0.5 the dials already show 2 and 3 although the bank still holds 0. A
  mark placed after the `Trigger` is the first instant the bank reads 23.
- `crank_rotation` does not wrap: the second stroke runs 360 → 720.
- Bank values that were never moved stay Python `int`s; the moving input's
  ends are `int` when the request started from a whole default
  (`origin 0`, `end 360`), commit values are `float` (`360.0`). JSON cannot
  carry that distinction to JavaScript; it did not matter for parity (below).
- Run from the symlinked project path, `Sim(ClockedCurta())` **fails**:
  `PermissionError: [Errno 13] Permission denied: '/mnt/home'`, raised in
  `machinome/node/base.py` `_make_build_dirs`, because the node's source file
  resolves to `/mnt/data/machinome-projects/…` while the project root is taken
  from the symlinked `/home/asa/devel/machinome/projects/…`, and their relative
  path climbs out of the build root. Run from the real path it works.
  `machinome export` from the symlinked path is not affected (it anchors its
  build directory). This is a framework finding; cycle 1's evaluation records
  the take through `Sim` and will meet it whenever the movie is evaluated
  from the symlinked path.

## 3. Parity in the browser

The viewer mounted on the export's manifest; `viewer.machine()` is a
`MachineHandle`. From `machine.reset()` the seven requests were replayed twice:
once with `machine.move(input, {to})` and `machine.move('crank_rotation', {by: 360})`
as the brief says, once with `machine.trigger('Turn crank')` for the strokes.
Each `ClockedRequest` was compared with Python's by `Object.is`: `input`,
`origin`, `end`, `admitted`, `by`/`to` for the moves, every commit's
`fraction`, `value`, every `targets` entry, `relations`, the number of
`stops`; and the whole bank after each request (`machine.state()` against
Python's `snapshot()` values), and the bank after `reset()` against Python's
initial bank.

| check | result |
|---|---|
| differences, `move` replay | **none** |
| differences, `trigger` replay | **none** |
| `machine.identity()` | `18f8b447…d63c7`, **equal** to the export's `clocked.identity` and to the framework simulation's own identity |
| `machine.order()` | 41 ids |
| viewer request time, `move` replay (ms) | 22.1, 26.5, 46.3, 21.2, 20.3, 13.2, 25.1 |
| viewer request time, `trigger` replay (ms) | 11.0, 9.8, 51.7, 30.0, 12.5, 10.4, 46.5 |

The two runs of `browser.json` (an earlier one and the committed one) gave the
same result.

## 4. A restored bank poses

From the recorded 23 stroke: the bank before it (digits 3 and 2 set), with
`crank_rotation` at `origin + f·(end − origin)` and the targets of every
commit with `fraction ≤ f` written; `machine.restore({identity, bank})`, then
`viewer.setView(VIEW)`, at 1920×1080.

| f | crank | restore | `state()` equals the bank given | crank on screen (x, y, w, h) | picture (sha256, 16) |
|---|---|---|---|---|---|
| 0 | 0 | accepted | exact | 817, 82, 462, 480 | da6a909a2a4e3316 |
| 0.3 | 108 | accepted | exact | 682, 100, 400, 450 | ac2abddfdc5963bd |
| 0.5 | 180 | accepted | exact | 671, 47, 432, 455 | a2615f61262c129f |
| 0.7 | 251.99999999999997 | accepted | exact | 737, 23, 481, 470 | 649d6d17cd1c098e |
| 1 | 360 | accepted | exact | 817, 82, 462, 480 | 09bfcdf468aeb0fc |

- **`restore` accepts a bank whose input lies mid-path**: no refusal at any
  fraction, and `machine.state()` returns exactly the bank given.
- **The screenshot differs between fractions**: five distinct pictures. The
  crank turns (its screen rectangle moves; at f = 0 and 1 it is the same
  rectangle, the pictures differ by the dials).
- **A, B, A gives identical bytes**: 0.3, then 0.7, then 0.3 is byte-identical
  to the first 0.3, and equal to 0.3's picture in the fraction sweep. The same
  hashes came out of two separate browser launches.
- **No animation frame is needed**: the screenshot taken right after
  `restore` + `setView` equals the one after two `requestAnimationFrame`s and
  the one after 30 more, at every fraction. Two caveats. These ran in
  `continuous` mode (question 5), where the viewer's own loop also draws; what
  is shown not to need a frame is the **scene**: `partOnScreen` read in the
  same task right after `restore` + `setView`, with no frame in between,
  already reports the crank at its new place, so `restore` poses the tree
  synchronously, and `setView` renders synchronously by its reference. Whether
  `restore` alone renders under `on-demand` cannot be tested today, because
  `on-demand` refuses this document.

## 5. The cost of a pose

Thirty poses each, cycling through the five banks (or 30 timeline instants
for the sawmill); medians in ms; `evaluate` is the round trip of the in-page
call, `screenshot` Playwright's `page.screenshot()`. Idle frame interval: the
median of ten `requestAnimationFrame` intervals before the poses.

| model, mode, size | restore | setTime | setView | evaluate | screenshot | total (min–max) | idle frame |
|---|---|---|---|---|---|---|---|
| Curta, continuous, 1920×1080 | 24.8 | | 3.8 | 33.1 | **12 259** | 12 291 (10 940–17 028) | 16.6 |
| Curta, continuous, 960×540 | 22.5 | | 3.3 | 29.6 | **8 981** | 9 010 (8 021–10 215) | 16.9 |
| sawmill, on-demand, 1920×1080 | | 10.1 | 0.7 | 13.3 | 428 | 446 (421–626) | 16.7 |
| sawmill, on-demand, 960×540 | | 9.3 | 0.7 | 12.1 | 286 | 300 (279–1 041) | 16.7 |
| sawmill, continuous, 1920×1080 | | 13.8 | 0.7 | 17.8 | 4 734 | 4 763 (2 084–6 093) | 16.5 |
| sawmill, continuous, 960×540 | | 12.6 | 0.7 | 16.1 | 3 974 | 3 989 (1 294–4 592) | 16.6 |

The pose itself is cheap: a `restore` of the 41-entry bank costs about 23 ms,
`setView` 3 to 4 ms. The screenshot is the cost, and the render mode decides
it: the same sawmill costs 0.45 s per 1080p frame on-demand and 4.8 s in
continuous mode, about ten times more, because the viewer's frame loop keeps
the software-rendering GPU process busy (it ran at up to 1300 % CPU while the
Curta was mounted) and every capture waits behind it. The Curta, 390 meshes,
costs 12.3 s per 1080p frame in continuous mode. At that rate a 60-second
film at 30 fps (1 800 frames) takes about six hours to capture once.

## 6. A highlight on the clocked export

`viewer.highlight([['input_selectors','selectors','digit_selector_axle_1','selector_knob_1_419057']], {color: '#ff5a1f', others: 'ghost'})`
at bank X (digit 1 at 3), then `restore` of bank Y (digit 1 at 5), at
1920×1080.

| check | result |
|---|---|
| highlight on the clocked export | applied: the slide tinted, every other part ghosted |
| the highlight still stands after `restore` | yes: a second `highlight()` throws `highlight is already applied; call the function the previous highlight returned before highlighting again` |
| picture after `restore` with the highlight carried, against a highlight applied fresh on Y | **byte-identical** |
| the slide moved | `partOnScreen` rectangle y 771 → 795, point (1108, 844) → (1088, 867) |
| pixels changed X → Y | 44 522 with the highlight (the ghosted interior moves too), 8 718 without |
| strongly orange pixels the highlight added | 6 140 at X, 6 137 at Y (carried), 6 137 at Y (fresh) |

So the highlight survives a `restore`, and the tinted pixels move with the
slide (same tinted area, new place). The stage re-applies highlights per
frame anyway; nothing here asks it to change.

## 7. The canvas after a resize

Host box at 1920×1080: full frame → right half (`left: 50%`, `width: 50%`) →
full, five round trips, counted once in single animation frames and once with
the stage's own loop (two frames, then its check: canvas ≥ 98 % of the box).
Then the reframe's shape: the box shrinking from the whole frame to the right
half in 15 steps, one size per stage wait.

| measure | result |
|---|---|
| frames until the canvas is the box's size within 1 px, to half | 2, 1, 1, 1, 1 |
| frames until the canvas is the box's size within 1 px, to full | 1, 1, 1, 1, 1 |
| stage-loop tries until it fills (10 resizes) | 1 each (544 to 2 816 ms per try, under the continuous loop's load) |
| stage-loop tries per step of the 15-step shrink | 1 each (552 to 2 284 ms per step) |

One weakness of the stage's check: when the box **shrinks**, the old, larger
canvas already passes "≥ 98 % of the box" at frame 0 (it overflows the box),
so the check cannot tell a resized canvas from a stale one. Here the canvas
was resized within the stage's two frames every time (worst case 2 single
frames), so no frame was posed into a stale canvas, but the reframe's shrink
resizes on every frame and relies on that timing, not on the check. The
layer-6 test already asserts "fills, and is no larger"; the stage's own wait
would need the same two-sided test to be safe for a shrink.

## 8. Memory

Chromium's process tree, VmRSS summed from `/proc`, page at 1920×1080:

| moment | RSS | processes |
|---|---|---|
| browser only | 326 MB | 5 |
| page loaded with the bundle, before mounting | **462 MB** | 6 |
| Curta mounted and posed once | **898 MB** | 6 |

The mounted Curta adds about 436 MB (the cost run's launch measured 464 →
899 MB). Megabytes here are MiB (kB / 1024).

## Other observations

- In continuous mode the viewer draws its full-screen corner control
  (`.machinome-fullscreen`, seen in `camera.mjs`'s default capture). The spike
  hid it with the documented CSS rule; the stage sets no such rule, because the
  on-demand mount it uses today has not needed one.
- `machine.trigger()` starts a drawing over the instruction's 6 s; the stage
  must not use it to pose (it posts the final bank at once and animates on the
  viewer's own clock). `move` and `restore` land immediately; the take poses
  by `restore` only.
- `export/` is not in the Curta project's `.gitignore`; it shows as `?? export/`
  there, as the brief expects.

## What the cycles must know

**A viewer change is needed.** The stage mounts every view with
`renderMode: 'on-demand'` (`stage/runtime.tsx`, `mountView`), and the viewer
refuses that for this document, verbatim:

> on-demand rendering requires a posed document without instructions

Its reference (`mount.rst`, `renderMode`) documents the refusal of clocked
machines. The only admitted mode, `continuous`, poses correctly and
deterministically in every test here, but costs 12.3 s per 1080p frame (sawmill
baseline: 0.45 s on-demand, 4.8 s continuous), roughly six hours per capture
of a one-minute film. The smallest change, a viewer cycle in the viewer
repository (the plan's `pose-a-bank`, two changes in two repositories):
**admit `renderMode: 'on-demand'` for a clocked (version 8) document** under
the same four conditions, with `machine().restore()`/`reset()`/`move()`
updating the pose without a frame loop and the next explicit render
(`setView`) drawing it, and `machine().trigger()` refused under on-demand
(it needs frames to draw), naming the mode. Everything else the take needs
already exists: `restore` takes a mid-path bank, poses the tree synchronously
and is exact. Videomaker's stage then mounts clocked views exactly as posed
ones; `ViewerInstance` in `stage/runtime.tsx` gains `machine()`.

**Parity: none.** The viewer's requests equal the framework's bit for bit on
23 + 145 (origin, end, admitted, every commit's fraction, value, targets and
relations, every bank after each request, by `move` and by `trigger`), and the
identities agree. Cycle 2's layer-6 parity check can be exactly `Object.is`.

**The cost of a pose.** Restore about 23 ms and setView about 4 ms in the
page; the capture dominates and depends on the render mode: about 0.3 to
0.45 s per frame on-demand (posed baseline; the Curta's own on-demand figure
cannot be measured until the viewer admits it), 9 to 12 s for the Curta in
continuous mode. The shrink resizes on every frame and pays one stage wait per
frame (one try, two animation frames, each time here).

**Against the plan's contract.**

1. "Viewer. Expected: nothing new." Contradicted, as above: the stage's mount
   options refuse a clocked document.
2. The pose rule holds and is honest, but on the Curta it writes nothing
   before f = 1: the stroke's only commit is at fraction 1.0. The film's
   "result reads 23" is a mark after the `Trigger`; mid-stroke the dials move
   by the model's closed-form pose, not by commits.
3. The contract names the export's identity and the document version 8, both
   confirmed, but not `source-revision.txt`, which the framework does not write
   and Videomaker's render reads; the Curta export has none. Cycle 1 or 4 must
   say who writes it (Leonardo's project writes its own).
4. Recording the take through `Sim` fails from the symlinked project path
   (`PermissionError: [Errno 13] Permission denied: '/mnt/home'`), a framework
   finding for the orchestrator's triage; cycle 1's evaluation must run from
   the real path until it is fixed.
5. For `reframe-join` (cycle 3): the stage's canvas check accepts a stale,
   larger canvas when the box shrinks; it worked here because the viewer
   resized within two frames every time.
