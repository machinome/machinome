# Investigation `render-cost`: where a frame's second goes (wart 14)

Status: evidence note, 1 October 2026, branch `render-cost` from
`addition-warts` c8c6309. Not ratified; an investigation of the
addition-warts campaign with no product change: nothing under `src/`,
`stage/`, `bin/` or `test/` was changed. It answers the pilot's question on
wart 14 ("Addition", `workflow/warts.md`) and informs whether cycle 9 of
the plan exists. It does not measure a GPU (there is none in this virtual
machine) and does not claim what one would cost.

**In one sentence.** The second goes to Chromium's software rasterization
of the viewer's WebGL draw (SwiftShader in the GPU process, about 10.5
CPU-seconds spread over ten cores per 1080p Curta frame, about 88 % of the
frame's wall time), which only a GPU would remove; capture, PNG encoding,
the pose and the Node side together are about 12 % (some 130 ms of ~1.1 s),
and no capture alternative moved the frame, so the recommendation is to
**defer** the wart.

## Machine and versions

| what | value |
|---|---|
| machine | virtual machine, 16 cores, 15 GiB, Linux 6.8, no GPU; worktree and projects on virtiofs |
| Chromium | Playwright 1.62.0, `chrome-headless-shell` 151.0.7922.34 (headless shell 1234), the same as the film's render manifest |
| WebGL in the page | `UNMASKED_RENDERER_WEBGL` = `ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero) (0x0000C0DE)), SwiftShader driver)`, WebGL 2.0; the viewer's context: `antialias: true`, `preserveDrawingBuffer: false` |
| launch flags | Playwright's own headless set with the stage's `CHROMIUM_ARGS` (`--use-angle=swiftshader --enable-unsafe-swiftshader`); the full command lines of every Chromium process are in each raw JSON (`environment.processes`) |
| viewer bundle | machinome-viewer 0.7.1, API 29, sha256 `b5fcdb86…0920107`, the bundle the film was rendered with (equal to its manifest's `/viewer.js` hash) |
| Node | v24.11.1 |
| Curta film | `videos/addition/_build/movie.json` of `Calculators/Curta-Type-I-3x`, read only; shot `add-23` (581 frames), frames 647 to 706, after its dissolve, the crank stroke and its dials moving; 1920×1080 |
| fixture | the fixture movie `count` (fixture project copy, real viewer, clocked counter take), shot `carry` (61 frames, a dissolve included), at 640×360 and at 1920×1080 |

**Load.** Five other agents ran their suites meanwhile; this investigation's
own GPU process holds ten cores while it rasterizes. The one-minute load
average is recorded with every sample and quoted with each table: it ran from
6 to 38 over the session, median about 15 to 30 per run. Wall times are
comparable within one table only; CPU-time per process (from `/proc`, 10 ms
ticks) is far less load-dependent and is the attribution this note leans on.

## Method

Everything is under `render-cost/` beside this note; measurements took
about 30 minutes of wall time.

| file | what |
|---|---|
| `instrument.mjs` | writes `render.instrumented.mjs` from `src/render.mjs` (sha256 `2a84351f…b5aa11`): imports pointed back at `src/`, timers around the stage's `setFrame` round trip, the renderer's checks, the screenshots and compositions inside a join; `browserSession` given a trace, launch flags and an init script. Every edit must match once, so a changed renderer refuses instead of being measured stale. One edit is not a timer: a manifest string naming a file the export does not hold is not served (wart 1's ground; the Curta export's workaround link had been moved aside as `STLs.aside` during this investigation, by another cycle, and was left alone). |
| `measure.mjs` | the driver: loads the movie document as the CLI does (`loadEpisode`, `prepareWordTimingForCommand` for `render`), opens the instrumented `browserSession` with an init script that times, in the page, the viewer's `restore` and `setView`, the stage's animation-frame waits and its whole `setFrame`; chooses render's own output frames of one shot (`outputShotUnits`) inside the session; modes `phases`, `alternatives`, `flags`, `parallel` (its header says each). The stage bundle and frames go to `render-cost/_build/` (ignored); the project's `_build` is only read, except that loading rewrites its `movie-resolved.json` with identical bytes (hashed before and after, equal, in each raw JSON). |
| `summarize.mjs` | the tables below from the raw JSON (`raw/*.summary.txt`) |
| `compare-flags.mjs` | decoded pixels of each flag variant against the stage's flags (`raw/curta-flags-pixels.txt`) |
| `raw/*.json` | every sample: per frame and phase in ms, CPU per Chromium process type, load average, PNG size and sha256, the stage's in-page breakdown |

Run as, from the worktree, with `B` the viewer bundle and `M` the film's
`movie.json`:
`TMPDIR=<render-cost>/_build/tmp node <render-cost>/measure.mjs --mode phases --viewer $B --movie $M --label curta --shot add-23 --skip 20 --frames 60 --out raw/curta-phases-1080.json`
(the other runs' arguments are in their raw JSON header: `mode`, `shot`,
`frames`, `width`).

The frame loop of `phases` is render's capture callback and shot-cache's
write, taken apart: `pose(t)` (frame resolution, the stage's `setFrame`, the
renderer's checks), `page.screenshot()`, the PNG size check, `writeFile` of
the `.tmp`, `rename`, `sha256`, and the `link` assembly makes. The first
frame of every session is excluded from the statistics and quoted apart: it
carries the scene's warm-up (10 to 15 s, shader compilation and mesh upload),
paid once per session.

## The phases of a frame

**Curta, `add-23`, 1920×1080**, 59 frames (647 to 706, first excluded),
load1 median 28.3 (23 to 33), `raw/curta-phases-1080.summary.txt`. No frame
of this excerpt waited for an animation frame or was in a join.

| phase | mean | median | p10 | p90 | share of the median frame |
|---|---:|---:|---:|---:|---:|
| **frame** | 1 899 | 1 924 | 1 544 | 2 204 | 100 % |
| pose, total (Node) | 37.4 | 35.0 | 29.4 | 48.1 | 1.8 % |
| · in the page: `restore` of the bank | 24.0 | 22.5 | 18.2 | 32.3 | 1.2 % |
| · in the page: `setView` (validates, issues the draw) | 5.6 | 5.2 | 3.7 | 8.2 | 0.3 % |
| · in the page: animation-frame waits | 0 | 0 | 0 | 0 | 0 % |
| · in the page: the rest (React, marks, measure) | 0.9 | 0.7 | 0.5 | 1.1 | 0.0 % |
| · `page.evaluate` overhead | 6.6 | 5.8 | 4.2 | 10.2 | 0.3 % |
| · checks, frame resolution (Node) | 0.3 | 0.3 | 0.2 | 0.4 | 0.0 % |
| **`page.screenshot()`** | 1 858 | 1 890 | 1 511 | 2 167 | **98.2 %** |
| Node: write, rename, sha256, link, PNG check | 2.8 | 2.0 | | | 0.1 % |

CPU per frame by process (ms of CPU, medians): during the screenshot, the
**GPU process 10 130**, the browser process 50, the renderer 0, Node 14;
during the pose, the GPU process 60, the renderer 30, Node 16. PNG 163 KiB.

**`count`, `carry`**, 60 frames (first excluded), `raw/count-phases-*.summary.txt`:

| | 640×360 (load1 14) | | 1920×1080 (load1 10) | |
|---|---:|---:|---:|---:|
| phase | median | share | median | share |
| **frame** | 33.5 | 100 % | 99.0 | 100 % |
| pose, total | 5.2 | 15.6 % | 7.5 | 7.6 % |
| · `restore`, `setView` | 0.6 | 1.8 % | 0.6 | 0.6 % |
| · animation-frame waits (12 of 60 frames: the stage's repaint, mean) | (11.9 mean) | | (10.3 mean) | |
| **`page.screenshot()`** | 25.5 | 76.1 % | 89.3 | 90.2 % |
| Node: write, rename, sha256, link | 1.2 | 3.6 % | 1.5 | 1.5 % |
| GPU-process CPU in the screenshot | 85 | | 305 | |

The count at 1080p has the Curta's pixels and a trivial scene: its whole
frame is 99 ms. The Curta's frame is ten to twenty times that, and the
difference is all GPU-process CPU.

## Rasterization against capture

Per frame, every probe after its own fresh pose of the same frame, the
baseline first and last (`raw/curta-alternatives-1080.summary.txt`, 29
frames, load1 median 32.6; `raw/curta-capture-again-1080.summary.txt`, 19
frames, load1 median 14.2):

| probe, Curta 1080p | median ms | GPU-process CPU ms | what it shows |
|---|---:|---:|---|
| `page.screenshot()` right after the pose (baseline) | 1 098 (load 14) / 1 488 (load 33) | 10 840 / 10 330 | what render pays |
| **a second `page.screenshot()` of the same pose** | **92** | **110** | capture proper: compositing, readback, PNG encode, transfer |
| `gl.finish()` after the pose, then the screenshot | 0.1, then 1 581 | 10 490 | `finish` does not wait in this Chromium; the work stays queued |
| two animation frames after the pose, then the screenshot | 16, then 1 618 | 10 200 | an animation frame does not rasterize the draw either; the capture does |
| the views hidden after the pose, then the screenshot | 1 518 | 10 410 | hiding the canvas does not cancel the queued draw: the GPU process executes it in order before the capture |
| a redraw (`setView` again) then `readPixels` of the canvas | 6, then 4 700 | | forcing the raster through a read is slower than the screenshot (8 MB read back synchronously) |
| a redraw then `canvas.toDataURL()` | 7, then 2 355 | | the same, with the browser's PNG encoder |

On `count` at 1080p the same second capture is 75 ms against 87 ms for the
first, and the GPU process spends 110 against 290 ms: there the draw is
almost free and capture is everything.

So, of the Curta's ~1.1 s frame at moderate load, about **1.0 s is the
SwiftShader rasterization of the viewer's draw** (~10.7 CPU-seconds over
about ten cores), about **90 ms is capture** (of which the PNG encoder is
the browser process's 50 ms of CPU, ~20 to 30 ms of wall), **about 35 ms is
the pose** (restore 22 ms, setView 5 ms) and **about 2 ms is Node**.

What dominates the raster: the viewer asks for a multisampled context. With
the context asked for without antialiasing (`noAntialias`, a measurement
only, through an init script), the same frames cost **350 ms** instead of
1 185 and 3.2 CPU-seconds instead of 11, so multisampling is about 70 % of
the raster (350 and 368 ms against 1 183 and 1 187, in alternated
launches); and it changes every frame's picture (60 796 pixels per frame
differ, up to 223 levels: the edges lose their antialiasing).

## The alternatives, ranked

Against the baseline on the same frames, interleaved per frame (Curta) or
per launch (flags), medians:

| alternative | Curta 1080p | gain | count 1080p | bytes | decoded pixels |
|---|---:|---:|---:|---|---|
| context without multisampling (viewer change, measurement only) | 350 / 368 vs 1 183 / 1 187 | **−70 %** | | changed | **changed** (60 796 px/frame, up to 223 levels) |
| two concurrent sessions (each its own Chromium) on the same 24 frames | 939 / 983 vs 1 355 ms of wall per frame | **−28 to −31 %** throughput, per frame slower (1.8 s) | | equal 24/24 | equal |
| CDP `Page.captureScreenshot` with `optimizeForSpeed` | 1 570 vs 1 488 (noise) | 0 % here; −21 % on count (69 vs 87) | 0.79× | changed (215 vs 163 KiB, faster zlib) | equal 29/29 |
| JPEG (encoder share only) | 1 668 vs 1 488 (noise) | browser CPU 50 → 20 ms | 0.87× | changed | changed (lossy) |
| CDP, one persistent session reused | 1 526 | 0 % | 0.98× | equal | equal |
| `clip` to the viewport | 1 520 | 0 % | 1.01× | equal | equal |
| CDP `fromSurface: false` | 1 506 | 0 % | 1.09× | equal | equal |
| `--use-gl=angle --use-angle=swiftshader` explicit | 1 244 / 990 vs 1 183 / 1 187 | none beyond the spread | | equal | equal 32/32 |
| Playwright's default headless flags (no stage flags) | 1 056 / 996 vs 1 183 / 1 187 | −11 to −16 %, inside the spread (10.7 vs 11.0 to 11.3 GPU CPU-s) | | changed | changed (1 958 px/frame, ≤ 2 levels) |
| `--disable-gpu` before the stage flags | 1 208 / 1 003 vs 1 183 / 1 187 | none beyond the spread | | changed | changed (1 958 px/frame, ≤ 2 levels) |

Flags runs (`raw/curta-flags-1080.summary.txt`, 15 frames per launch, two
rounds alternated stage, playwright, disableGpu, angleSwiftshader,
noAntialias; load1 15 to 22) quote round 0 / round 1. Every variant still
rasterizes WebGL on SwiftShader (its renderer string and its 10.7 to 11.3
CPU-seconds per frame say so); `--disable-gpu` and Playwright's defaults
change only the compositing path, hence the ≤ 2-level differences.

Parallel sessions (`raw/curta-parallel-1080.summary.txt`): one session
1 355 ms per frame in both rounds (load1 6 and 32 at their start), two
sessions on alternate frames 939 and 983 ms per frame (load1 15 and 23); the
frames are byte-identical to the phases run's, as a pure function of time
promises. Each session's frame takes 1.8 s instead of 1.25 s: two
SwiftShaders contend for sixteen cores, and the other agents' suites for the
same cores.

None of the capture alternatives moves the Curta's frame: the capture they
change is under a tenth of it.

## The answer and the recommendation

The dominant cost is SwiftShader's rasterization of the viewer's WebGL draw
in Chromium's GPU process; capture, encoding, the pose, the waits and the
Node side together are about 12 % of a Curta frame (some 130 ms of ~1.1 s,
of which capture proper is 90 ms and the PNG encoder 20 to 30), so no fix of
theirs can give more than that, and the measured capture alternatives give
nothing within the noise. **Recommendation: defer wart 14**, as the pilot's
ruling foresees: a GPU in the virtual machine, or rendering on the host, is
the lever, and that is the pilot's separate decision.

No cycle 9 is proposed. Two levers were measured that are not capture fixes
and are recorded for that decision, not proposed:

- the viewer's multisampling is 70 % of the raster, but turning it off changes
  every picture (a viewer and picture-quality decision, not Videomaker's);
- concurrent sessions buy about 1.4× throughput on this machine with
  identical bytes, by using cores one SwiftShader leaves idle; on a shared
  machine they take those cores from the other agents, and a GPU makes the
  question moot.

For scale: the film's 3 787 frames at ~1.0 s are its 63 minutes; of those,
about 55 minutes are rasterization, about 6 minutes capture proper, about
2 minutes posing, and about 10 seconds Node.

## Findings

1. **`gl.finish()` does not wait in this Chromium**, and neither do two
   animation frames: with ~10 CPU-seconds of draw pending, `finish` returns
   in 0.1 ms and the next screenshot pays the whole raster. Any future proof
   or timing that assumes `finish` (or an animation frame) has rasterized
   a view is wrong here; reading pixels is the only forcing call, and it is
   slower than the screenshot.
2. **Hiding a view after its pose does not save its raster.** The draw
   `setView` issued is executed before the capture whatever the canvas's
   visibility, so a picture-only capture of a frame that hides a view (an
   opaque picture over it) still pays it. Only not posing a view avoids it.
3. **The viewer's multisampled context is ~70 % of the raster** under
   SwiftShader (350 ms against 1 185 per Curta frame without it). A viewer
   finding, recorded for the viewer's log, not filed here.
4. **Playwright's default flags and `--disable-gpu` give different bytes**
   from the stage's flags (1 958 pixels per frame by up to 2 levels, the
   compositing path), with no speed difference beyond the spread;
   `--use-gl=angle --use-angle=swiftshader` is byte-identical to the stage's
   flags. The flags are a picture input; they live in `src/render.mjs`,
   whose hash is in the shot cache's common key, so a change of them does
   recapture.
5. **Every session pays a 10 to 15 s warm-up** on its first Curta frame
   (shader compilation and mesh upload); render opens one session per film,
   so it is about 0.3 % of the film.
6. **The stage's repaint costs ~45 to 60 ms** on the frames whose page
   content changed (12 of 60 `count` frames, typing in the source panel);
   none of the Curta excerpt's frames repainted. Against a 1 s Curta frame
   that is at most 6 % of the frames that type; not measured on the Curta's
   split shots.
7. **The pose is 35 ms on the Curta** at load 28, two thirds of it `restore`
   of the 41-entry bank (22 ms), against the wart's 14 ms; either way under
   4 % of a frame.
8. The Curta export's workaround link for wart 1 was found moved to
   `STLs.aside` by another cycle during this investigation; the instrumented
   copy serves only files the export holds (see Method), which is the shape
   cycle 1 is about.

## What was not done, and why

- **No GPU was measured**: the virtual machine has none. The note does not
  estimate what one would give.
- **No product change**: the instrumented renderer is a generated copy under
  this directory; `src/render.mjs` is untouched.
- **The test suites were not run**: no file the suites read was changed.
- **Not measured on the Curta**: frames inside a dissolve (two captures and
  a composition each, about 144 of the film's frames, roughly double cost by
  construction), the reframe's canvas wait (24 frames, wart 12), and the
  repaint on the split shots' typing frames. Each is bounded above and does
  not change the answer.
- **Not tried**: `channel: 'chromium'` (new headless) instead of the
  headless shell, a lower `deviceScaleFactor` or width (changes the film),
  and any change to the viewer's context (its repository's decision; the
  `noAntialias` variant only measured its share).
- `render-cost/_build/` (the stage bundle and every captured frame) is
  ignored and was removed after the measurements; `compare-flags.mjs` needs a
  flags run before it.
