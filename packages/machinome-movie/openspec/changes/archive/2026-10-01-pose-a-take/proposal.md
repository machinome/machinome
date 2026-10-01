## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `23 + 145`; `workflow/ongoing/curta-video-campaign/plan.md`).
Its Curta is clocked. `declare-a-take` declared and recorded its take in
the movie document; the spike proved that the viewer restores a recorded
bank synchronously and exactly and reproduces the framework's requests bit
for bit. Nothing draws it: the commands refuse every document but a posed
normalized loop, the Node checks know no take, and the stage only sets a
loop's time.

## What the film does with the result

`videos/addition/` of the Curta project films its `Addition` take: the
setting slides move, the crank turns, the result reads 23 and then 168,
and the reframe of chapter 4 runs the take on under the moving box. Every
frame poses the bank the take gives that instant on the real viewer, which
is held to the framework's record before the first frame and at every mark.

## What Changes

- **A take document loads.** `model.timeMode: "take"` with a `take` block
  loads, checks and resolves; `"take"` without a block, a block under
  `"normalized-loop"` and a clocked export filmed as a loop are refused
  naming the field; a running program stays refused; the refusal that named
  only normalized loops goes. The Node checks refuse the five take fixtures
  with the words Python names, the replay of the steps included. YAML
  episodes are unchanged.
- **The frame carries the bank.** A view on a take carries `bank`, the
  machine's whole bank at its take time by the contract's rule, computed in
  a pure module (`src/take.mjs`), instead of a loop `time`.
- **The stage poses a bank.** It restores the bank on the viewer's machine
  with the take's identity, then sets the camera; it refuses at mount a
  viewer with no machine or another identity, naming the view; it reports
  the bank it posed. A movie on a take needs Viewer API 29.
- **The renderer holds the viewer to the take.** Before the first frame,
  each step is replayed on the viewer from its recorded bank and compared
  exactly with the record; at every frame the reported bank is the frame's,
  and at a mark the take's. A canvas more than a pixel larger than its view
  is refused (`Viewer canvas exceeds its view`), and the stage's canvas wait
  waits for a canvas to shrink as it waits for one to grow.
- **`check` prints the take**: its steps, marks, length and that the replay
  matched.
- **Proofs**: the fixture `count` pinned resolved; the viewer double gains
  a machine; layer 6 proves the take on the API 29 bundle over the fixture
  counter's real export; layer 8 runs `count` through the pipeline.
- **Records**: ADR-012 (STAGE); `docs/stage.md`, `docs/movie-document.md`
  (the API sentence only), `README.md`, `AGENTS.md`,
  `docs/architecture-overview.md`, `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `movie-document`: a take document loads; its Node checks and replay; the
  frame of a view on a take; `check`'s take line; the viewer held to the
  take.
- `react-stage`: a view on a take is posed by its bank; the mount refusals;
  Viewer API 29; the canvas larger than its view.
- `test-suite`: the viewer layer proves the fixture take.

## Impact

Code: `src/take.mjs` (new), `src/movie.mjs`, `src/timeline.mjs`,
`src/render.mjs`, `bin/videomaker.mjs`; `stage/runtime.tsx`,
`stage/types.ts`; `test/viewer-double.mjs`, `test/support/fixture-movie.mjs`;
tests at layers 2 to 6 and 8; `fixtures/resolved/count.json`. The runtime
changes, so every film's stage bundle changes and recaptures once. No
Python change, no schema change, no viewer change.

## Non-goals

Running machines stay refused. No scenario take recorded by a framework
command. No change to the Python side or to the viewer. No publication,
push or paid request.
