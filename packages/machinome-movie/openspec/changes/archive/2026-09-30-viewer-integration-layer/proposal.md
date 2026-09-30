## Why

Two findings of 30 September 2026 in `workflow/warts.md`:

- "Cut and Advance, version 2", wart 1: **the real viewer sizes its canvas on
  its own animation frame, and shrinks it to nothing while its host is
  detached.** The film's first frame was refused (`Viewer canvas does not
  fill its view`), and once that was fixed the preview's samples were refused
  when a view came back after shots without it. The stage now waits, bounded,
  and the viewer double gained `lateCanvas` to pin it; but "Layer 6, the real
  viewer, still has no test; this is what it would have caught."
- "The React stage", wart 5: **memory with the real viewer is unmeasured**
  (layer 6 has no test).

The episode is *Cut and Advance* (the Leonardo project, version 2,
30 September 2026): its first render met, with the real viewer, two failures
no test of the repository could see, because every browser test runs on the
viewer double and the fixture export has no geometry. `AGENTS.md` names the
missing layer: "6. **Viewer integration** (Playwright, the real bundle). The
`View` element over a real posed fixture export; ... Gated on a selected
bundle, and it asserts the API it needs rather than assuming it. The only
layer that touches the real viewer." It also says "Layer 6 still has no
tests".

What the film does with the result: the next change to the stage (a canvas
wait, a lease, a repaint rule) is proved against the viewer the film is
rendered with before the film is rendered again, and the memory a film's
instances cost is a recorded number instead of a guess. The orchestrator's
cut, not the pilot's: only the layer's first sentence applies today (no
running or clocked fixture exists, and no scenario take).

## What Changes

- **A real posed fixture export.** The fixture project's seesaw gains rest
  placement, a declared 20-second loop (`Time(loop=20)`) through which its
  beam tips on its pivot (level and rising at 5 s, top at 10 s, level and
  falling at 15 s, the fixture take's marks), and a colour of its own on its
  blocks. `export/seesaw/` is replaced by what the framework's
  `machinome export` writes for it (a manifest and one 684-byte mesh), and
  the fixture project, its documents and their resolved pins are re-pinned
  with `scripts/pin-fixture-project.mjs`. The fixture movies keep their
  meaning: the same parts, marks, cameras and layers; only
  `model.readiness` and `model.sourceRevision` change in the documents.
- **A `viewer` project** in `vitest.config.mjs`: tests under `test/viewer/`,
  after the slow project, one file at a time, on the run's one Chromium,
  memoized like the other slow tests with the selected bundle's content in
  the key. Gate: `VIDEOMAKER_VIEWER_BUNDLE`. Unset, every test of the project
  is reported skipped, "no viewer bundle selected", by vitest and by the
  memo reporter, and never as passed; set to a file that does not exist or
  does not define `MachinomeViewer`, every test fails naming the path.
- **The tests** (layer 6), over the real export and the tour:
  the bundle declares the API the movie needs, asserted; a view's canvas
  fills its box on a fresh mount, after a change of set and when the view
  returns; A, B, A gives identical pixels across a camera move, a highlight
  with `others: ghost`, a hidden layer and a re-leased instance; a label's
  target is on screen through the real `partOnScreen` and `project` and its
  text inside the frame; the tour through `check`, `preview` and `render`
  with `--viewer <path>`, frames counted by `ffprobe`; and the memory of one
  and two instances read and recorded, not asserted.
- **Records**: ADR-008 (RECORDS); the `test-suite` spec; `AGENTS.md`'s two
  sentences about layer 6; `README.md`, one line on running the suite with
  a viewer; `CHANGELOG.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `test-suite`: a requirement for the viewer integration layer (gated,
  skipped by name, asserts the API); the slow directories include
  `test/viewer/`; the memo keys a selected bundle by its content; how the
  run's one browser serves the viewer project.

## Impact

Tests and fixtures only: `vitest.config.mjs`, `test/support/toolchain.mjs`
(the run's one Chromium shared by the projects that set up), a gate module
under `test/support/`, `test/support/reach.mjs` and `memo.mjs` (the selected
bundle in the key), `test/support/memo-reporter.mjs` (skips by name),
`test/viewer/*.test.mjs`, `test/memo.test.mjs`, the fixture project
(`models/seesaw.py`, `videos/takes.py`, `export/seesaw/`), `fixtures/documents/`
and `fixtures/resolved/` for `minimal` and `tour`, `python/tests/test_evaluation.py`
and the quoted take in `docs/declaring-a-movie.md` (its `readiness`). No
format, schema, refusal of the tool, command option, stage or renderer code
changes. The fixture export is keyed by the browser and pipeline tests, so
they run once cold after the change.

## Non-goals

No scenario takes, no running or clocked fixture, no change to the viewer,
no path to a bundle in the repository (the path is an argument in the
environment), no threshold on memory. No publication, push or paid request.
