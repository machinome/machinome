# Implementation evidence

## Authority and scope

Ratified on 29 September 2026 by the orchestrating agent as the campaign's
review gate, under the pilot's delegation (`design.md`, "Ratification"): cubic
curves, closed 0.4 field lists campaign-wide, task 3.4 as small silent
implementation evidence, task 3.1 as an untracked Leonardo demo episode.
Planning commit `37b2e56` on branch `film-motion`; base for the pins and the
"before" stills is that commit's source, whose `src/` is identical to
`835cf35`. First cycle of the film motion campaign applied. No viewer,
simulation or CAD change; nothing committed to Leonardo, pushed or published.
The design was implemented as ratified; no decision was substituted.

## Red / green

Pin (task 1.2), green by design: `0.2 and 0.3 frames are unchanged` in
`test/workflow.test.mjs`, with whole `frameAt` objects generated from the base
source before any source change and written literally (fixtures in
`test/frame-fixtures.mjs`): the 0.2 keyframe fixture `{0,8}`, `{1.5,10}`,
`{2,12}` at 0, 0.5, 1, 1.5, 1.75 and 3 s in the format-less and 0.2
spellings; a 0.2 fixture with keys `{0, 158.7}`, `{8.6, 180.1}` at frames
238–242 (frame 240 = 8 s, model second 178.60697674418606, where the
divide-first order gives ...603 and a different `time`); the 0.3 lens fixture
(`wide`→`tight`) and the rolling fixture (`wide`→`rolled`) at 0.2, 0.5, 1, 1.3,
1.9 and 2.5 s; a 0.3 fixture with an annotation and a highlight active at 1 s.
Run on the base: `node --test test/workflow.test.mjs`, 8 pass, 0 fail. Green
again after the change.

Mutation check of the pin, after implementation, each reverted at once: making
the linear branch of `keyedValue` divide first fails the pin (`stroke at 240`)
and the order test of `test/easing.test.mjs`; writing `smooth` as
`u*u*3-2*u*u*u` fails the pin and `smooth is the camera smoothstep to the last
bit`.

Red, before implementation:

- `test/easing.test.mjs` (1.1): fails to load, `ERR_MODULE_NOT_FOUND: Cannot
  find module .../src/easing.mjs`.
- `test/keyframes.test.mjs` (1.3): fails to load for the same reason. With
  2.1 in place and before 2.2–2.3, 0 of 6 pass: the 0.4 equality, camera and
  model-time tests and the 0.4 lens test all throw `Unsupported episode format`;
  the refusal test reports `Missing expected exception: /^Easing needs format
  machinome-video-draft\/0\.4: shot machinome$/` (a 0.3 episode with `ease` was
  accepted); the closed-field test got `Unsupported episode format` instead of
  `Unknown camera key field: eas (key #1 in shot genome)`.
- `test/render.test.mjs` (1.4, real Chromium, viewer double): 5 pass, 1 fail.
  `eased camera moves and model time reach the viewer ...` fails: `setView` at
  0.75 s received camera `[2, -10, 1]` (smoothstep at half the move) instead of
  the `out` value `[3.5, -10, 1.75]`. The existing cases pass unchanged; the
  double records `setTime` only behind the new `recordTime` option.

Green after implementation: `node --test`, 49 pass, 0 fail (48 tests plus the
fixture module, which node counts as a file and which registers no tests). The
suite had 33 tests before this change.

During implementation one ordering trap appeared: `code.mjs` imports
`episode.mjs` while `timeline.mjs` is still loading, so `episode.mjs` must not
read the format list from `timeline.mjs` at load time (`Cannot access 'FORMATS'
before initialization`). The list and its order (`FORMATS`, `formatAtLeast`)
live in `timeline.mjs`; `episode.mjs` re-exports `FORMATS` and names its three
format constants literally.

## What changed

- `src/easing.mjs` (new): `EASINGS`, `ease` (D1, clamped input, refuses any
  other name with `Unknown easing: <name>; use linear, smooth, in, out or
  in-out`) and `keyedValue` (D2: holds before the first and from the last key,
  the segment named by its ending key, linear in the model-time order, eased
  values clamped between the segment's keys, vectors component by component).
- `src/timeline.mjs`: `cameraAt` weight `ease(b.ease ?? 'smooth', u)`; model
  time through `keyedValue` with fallback `linear`; `FORMATS` gains 0.4 and one
  ordered comparison `formatAtLeast`; 0.3-or-later frames carry `annotations`
  and `highlight`.
- `src/episode.mjs`: 0.4 accepted; annotations, highlights and the up sweep
  test "0.3 or later", the lens refusal "is 0.2", messages unchanged; `ease`
  validated on camera keys and model keyframes (format, not on the first key,
  one of the five, each message naming the shot); closed field lists in 0.4
  with the D7 messages.
- `src/render.mjs`: the frame identity includes the hash of `easing.mjs` (D8).
- `docs/FORMAT.md`: title, status and "Read the screenplay first" name 0.4;
  timing semantics name `ease`; the lens section says "the same easing"; new
  sections "Format 0.4" and "Easing". `README.md`: set-up and timing name 0.4
  and easing.

## Unchanged episodes, before and after (task 3.3)

Bundle: machinome-viewer worktree `film-annotations`, banner `machinome-viewer
0.7.1 - viewer API 28`, SHA-256
`a3fe03f2db691ff46ed3e3624eee57c57445d526d29530835d0df1f00dda095c`, copied to
the session scratchpad before the first run so it could not change between runs.
Stills at 960 px; the "before" set was taken with the base source before any
source file was touched and kept in the session scratchpad
(`keyframes-before/`).

- The sawmill rehearsal fails `check` in place against the current export
  (`Model duration differs from production settings`), as the
  `annotate-a-part` evidence recorded. It was replaced, as the briefing allows,
  by `demo-annotate-a-part` (0.3), and additionally previewed from a scratch
  copy outside Leonardo (its own scratch Git repository) with the three stale
  settings patched: model duration 1460, `sourceRevision` `28b43bc`, and the
  `structure` layer path renamed `Fixed timber structure`, file paths made
  absolute. That copy keeps the 0.2 format and its model keyframes; "before"
  ran from a scratch extract of `37b2e56`'s `src/`, `bin/` and lock file.
- `demo-annotate-a-part` (0.3): `check` passes; 6 of 6 stills byte-identical
  before and after; `report.json` byte-identical.
- `demo-feed-mechanism` (0.3, lens moves, highlights, annotations): `check`
  passes; 26 of 26 stills byte-identical; `report.json` byte-identical (two lens
  checks and two highlight checks included).
- Sawmill rehearsal, scratch re-pinned copy (0.2, model keyframes): `check`
  passes; 24 of 24 stills byte-identical.

The baseline was repeated once for the two demo episodes (a second "before"
run): 6 of 6 and 26 of 26 identical to the first, so on this machine the
cross-process single-pixel flicker recorded in `move-up-and-field-of-view`
did not appear.

## Consumer episode (tasks 3.1, 3.2, 3.4)

`/home/asa/devel/machinome/projects/Leonardo/videos/demo-keyframes-and-easing/`
(untracked; generated media only in its ignored `_build/`): format 0.4,
1920×1080, 30 fps, 26.5 s, on the `demo-feed-mechanism` production (sawmill
export at revision `28b43bc`, loop 1460 s, so model seconds 453–466.8 exist)
with the *Revolutions* `mechanism` and `linkage` presets added. Shot `machinome`
(0–14 s): keys `{0, 453}`, `{3.733, 453}`, `{14, 461, ease: in}`, camera held on
`mechanism`. Shot `genome` (14–26.5 s): keys `{0, 461}`, `{6.899, 466.8, ease:
out}`, `{12.5, 466.8}`; camera `mechanism` at 0 to `{9.615, linkage, ease:
out}`; structure, foundation and water hidden. Keys and times are exactly D4
and D5's, which makes the episode 26.5 s rather than about 10.

`check` passes with the API 28 bundle, and with the API 27 bundle (primary
checkout 0.7.1 build, banner `viewer API 27`, SHA-256
`3e2cfb3dcb70e48c5edd89d82e267467b5db75508a323c9c618609cc56e8f5ab`) without
reading it: `requiredViewerApi` is `{api: 21, reasons: []}`.

`preview` with the API 28 bundle: 6 stills, pixel replay exact, invalid camera
preserved, viewer API 28. With the API 27 bundle: the same, viewer API 27, and
the 6 stills byte-identical to the API 28 ones (easing needs no newer viewer).

Frame-by-frame, pure `frameAt` at every output frame (795 frames; full CSV kept
in the session scratchpad, not in Git). Model speed and camera speed are the
differences to the previous frame, per video second:

| frame | t (s) | shot | model s | model speed | camera position | camera speed |
|---|---|---|---|---|---|---|
| 111 | 3.700 | machinome | 453.000000 | 0.0000 | 740, 940, 705 | 0 |
| 112 | 3.733 | machinome | 453.000000 | 0.0000 | 740, 940, 705 | 0 |
| 113 | 3.767 | machinome | 453.000000 | 0.0000 | 740, 940, 705 | 0 |
| 114 | 3.800 | machinome | 453.000002 | 0.0001 | 740, 940, 705 | 0 |
| 120 | 4.000 | machinome | 453.000141 | 0.0014 | 740, 940, 705 | 0 |
| 150 | 5.000 | machinome | 453.015035 | 0.0347 | 740, 940, 705 | 0 |
| 210 | 7.000 | machinome | 453.257755 | 0.2343 | 740, 940, 705 | 0 |
| 300 | 10.000 | machinome | 454.819443 | 0.8663 | 740, 940, 705 | 0 |
| 390 | 13.000 | machinome | 458.882701 | 1.8976 | 740, 940, 705 | 0 |
| 419 | 13.967 | machinome | 460.922333 | 2.3149 | 740, 940, 705 | 0 |
| 420 | 14.000 | genome | 461.000000 | 2.3300 | 740, 940, 705 | 0 |
| 421 | 14.033 | genome | 461.083665 | 2.5099 | 736.372, 937.409, 703.083 | 145.58 |
| 422 | 14.067 | genome | 461.166521 | 2.4857 | 732.770, 934.836, 701.178 | 144.57 |
| 450 | 15.000 | genome | 463.174192 | 1.8544 | 641.760, 869.828, 653.073 | 117.74 |
| 480 | 16.000 | genome | 464.723213 | 1.2804 | 563.872, 814.194, 611.904 | 92.04 |
| 540 | 18.000 | genome | 466.369658 | 0.4505 | 459.706, 739.790, 556.845 | 50.12 |
| 600 | 20.000 | genome | 466.787166 | 0.0444 | 408.601, 703.287, 529.832 | 20.84 |
| 624 | 20.800 | genome | 466.799983 | 0.0007 | 398.783, 696.274, 524.643 | 12.67 |
| 626 | 20.867 | genome | 466.799999 | 0.0001 | 398.174, 695.838, 524.320 | 12.08 |
| 627 | 20.900 | genome | 466.800000 | 0.0000 | 397.880, 695.629, 524.165 | 11.79 |
| 690 | 23.000 | genome | 466.800000 | 0.0000 | 390.092, 690.065, 520.048 | 0.63 |
| 700 | 23.333 | genome | 466.800000 | 0.0000 | 390.009, 690.006, 520.005 | 0.14 |
| 709 | 23.633 | genome | 466.800000 | 0.0000 | 390, 690, 520 | 0 |
| 794 | 26.467 | genome | 466.800000 | 0.0000 | 390, 690, 520 | 0 |

- Zero speed at the resume: the machine leaves 453 from rest (2e-6 model
  seconds past 453 at 3.8 s, two frames after the key) and gathers speed to 2.31 model s/s by the
  cut, against the linear segment's constant 0.78 that the original shot jumps
  to in one frame.
- Zero speed at the pause: model time arrives at 466.8 from rest at 20.899 s
  (genome 6.899 s), peaking at 2.51 model s/s just after the cut (the design's
  "about 2.5 times").
- The camera is already travelling in the first frame after the cut (145.6
  units/s, its fastest), where `smooth` would have covered 3 % of the move in
  the whole first second; it settles and holds exactly on `linkage` from
  genome 9.615 s.
- Every key met exactly: `time` equals `seconds / 1460` at 0 and 3.733
  (`machinome`) and at 0 and 6.899 (`genome`); the `linkage` pose is exact at
  its key. No frame's model time is below the previous frame's (0 decreases in
  795 frames).

Silent clip (3.4): `render --width 960 --fps 30 --silent` with the API 28
bundle, 795 frames posed and checked, 960×540, 26.5 s, frame cache
`ba3f86bec3bb4b23`; `_build/silent-preview.mp4` SHA-256
`1dac0fb687c92b2b31b8ca72379727c5a0c3e47b245df925bac3a0b65aa98d0f`. A contact
sheet of frames 112–720 shows the held machine, the move to the linkage and the
pause. How the curves feel in motion is task 4.1, for the pilot.

## Findings out of scope

- All five 0.2 Leonardo episodes (the sawmill rehearsal, *Revolutions*,
  *Revolutions v2*, the source and syntax studies) still fail `check` in place
  against the current export (stale duration or source revision, and the
  renamed `structure` path). Re-pinning them is the Leonardo
  repository's work.
- Node's test runner treats every `.mjs` under `test/` as a test file, so
  `test/frame-fixtures.mjs` appears once in the run as a passing file with no
  tests. Harmless; noted so the count is not misread.
