# Implementation evidence

## Authority and scope

The second change of Videomaker's player campaign, on branch `live-server`
(worktree `WTs/live-server`), cut from `player` at `b86f88b`. The planning
commit is `93e6826`, made after the orchestrator ratified the proposal with
four binding notes (the watched set recomputed from every accepted
generation; the stage hash over the whole stage page; the outline's
geometry and take keys; `checkFilm` renamed `checkSource`). One addition
came after the planning commit, on the orchestrator's message, from a
finding of the parallel `take-transport` cycle: `GET /take.json` (design
D11), recorded in `design.md`, the spec delta and `tasks.md`.

Nothing was pushed or published. No network or paid request was made, and
no speech was generated: every take is a fixture double, and the layer-8
tests replace `fetch` so that any request beyond the loopback interface
fails. Nothing was installed (`node_modules` is the primary checkout's,
linked). No real film was touched, and no proof ran on one (finding 16 of
`workflow/warts.md`). The viewer was reached only through the bundle
selected by path,
`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js`
(`machinome-viewer 0.7.1 - viewer API 29`). It was never written into the
repository. The baseline spec is not synced, the change is not archived
and ADR-021 stays Proposed: the pilot ordered the campaign to stop before
sync.

Environment: Linux, Node v24.11.1, vitest 5.0.3, Playwright's Chromium,
Python from the workspace venv. Another cycle (`take-transport`) ran in
another worktree at the same time, so durations are indicative only.

## Baseline

Run on the base content (the change's directory just created, nothing else
changed), memo allowed, no viewer bundle selected:

    env -C WTs/live-server npm test
     Test Files  40 passed (40)
          Tests  395 passed | 13 skipped (408)
    Test memo: 34 passed from the memo, 361 run
    real	11m1.304s

The 13 skipped tests are layer 6, "no viewer bundle selected".

## 1. The extractions, behaviour unchanged

### 1.1 `checkSource`

The body of `check` was moved from `bin/videomaker.mjs` into
`src/check.mjs` (`checkSource`, `commandOptions`, `summaryLine`). The code
was moved, not rewritten; the only rename is the local `fps` to `rate`,
which avoids shadowing the parameter. Before anything else, the pipeline
tests that pin `check`'s lines were run cold, with no change to their
expectations:

    npm test -- --cold --project slow test/pipeline/movie-pipeline.test.mjs
     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (16 tests) 223606ms
     Test Files  1 passed (1)
          Tests  16 passed (16)
    Test memo: 0 passed from the memo, 16 run
    real	3m46.278s

### 1.2 `src/film-assets.mjs`

`stage()` (renamed `filmFiles`), `clipUses` and the inline handler moved
from `src/render.mjs` into `src/film-assets.mjs`. The handler became
`filmAssets({paths, config, onError})`; `browserSession` uses it. Diffed
against the base, the moved functions differ only in their names and in
the page's path, which is now the constant `FILM_PAGE`. The shot cache's
common key gains `assets` (the hash of `src/film-assets.mjs`).
`test/support/reach.mjs` declares that `src/film-assets.mjs` reads
`src/film.html`.

The first transcription dropped a closing bracket in `clipUses`. The first
run stopped at import analysis and ran no test
(`Failed to parse source for import analysis`). It was fixed and the moved
code diffed against the base before the run below.

The whole slow project, cold. The first run was ended by the tool's
ten-minute command limit after its fourth file:

     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (16 tests) 232920ms
     ✓ |slow| test/pipeline/incremental-rendering.test.mjs (20 tests) 207921ms
     ✓ |slow| test/browser/render.test.mjs (17 tests) 121774ms
     ✓ |slow| test/browser/stage.test.mjs (14 tests) 68981ms
    real	10m53.532s

The ten remaining files were then run cold:

    npm test -- --cold --project slow <the ten remaining files>
     Test Files  10 passed (10)
          Tests  72 passed (72)
    Test memo: 0 passed from the memo, 72 run
    real	1m49.921s

Together, the 14 files and 139 tests of the slow project passed cold on
the extracted code.

## 2. Layer 3, pure

### Red

`test/live.test.mjs` written, with `src/live.mjs` absent:

    npm test -- --cold --project pure test/live.test.mjs
     FAIL  |pure| test/live.test.mjs [ test/live.test.mjs ]
    Error: Cannot find module '../src/live.mjs' imported from …/test/live.test.mjs
     Test Files  1 failed (1)
          Tests  no tests
    real	0m0.834s

### Green

`frameFor`, `outline` and `takeDocument` (design D5, D11):

     ✓ |pure| test/live.test.mjs (7 tests) 78ms
     Test Files  1 passed (1)
          Tests  7 passed (7)
    Test memo: 0 passed from the memo, 7 run
    real	0m1.160s

## 3. Layer 8, serial

### Red

`test/pipeline/live.test.mjs` written, with `src/live.mjs` holding only
the pure functions and the command not yet added (cold):

    npm test -- --cold --project slow test/pipeline/live.test.mjs
       × a session on the counter serves the outline, the frames, the take, the stage page and its files, events, reloads and refusals, then stops 914ms
       × a stage module that starts importing a file has that file watched from the next generation on 117ms
       × a session on the YAML episode reloads when its production settings change, and refuses an excerpt source that left its pin 134ms
       × the live command serves the tour on a fixed port, opens its address, finds a change by polling, and stops on an interrupt 2687ms
       × the live command refuses what check refuses, its malformed options and a port in use, and does not fail when xdg-open does 619ms
    TypeError: live is not a function                         (tests 1 to 3)
    Error: live exited 1 before its address line:
    Unknown option '--port'. To specify a positional argument starting with a '-', …   (test 4)
    AssertionError: … + 'Unknown command: live' - 'The live command takes no --fps'      (test 5)
     Test Files  1 failed (1)
          Tests  5 failed (5)
    real	0m6.938s

### Green

`live` (D3, D4, D6, D7, D9), `assetServer({port})` and the command (D8):

     ✓ |slow| test/pipeline/live.test.mjs (5 tests) 28375ms
       ✓ a session on the counter … then stops 11943ms
       ✓ a stage module that starts importing a file has that file watched from the next generation on 3186ms
       ✓ a session on the YAML episode … left its pin 1316ms
       ✓ the live command serves the tour on a fixed port, … stops on an interrupt 6404ms
       ✓ the live command refuses what check refuses, … when xdg-open does 5522ms
     Test Files  1 passed (1)
          Tests  5 passed (5)
    Test memo: 0 passed from the memo, 5 run
    real	0m30.926s

### Two mutations, to show the watcher tests discriminate

Each mutation was applied to `src/live.mjs`, run cold, and reverted, with
the file compared byte for byte against the kept copy:

- (a) Reload on any event in a watched directory, instead of only events
  that name an input:

       × a session on the counter … then stops 2684ms
      AssertionError: the tool's own products start no reload

- (b) Skip re-arming the watches after an accepted generation:

       × a stage module that starts importing a file has that file watched from the next generation on 123007ms
      AssertionError: no loading event arrived

### Reload time, measured

A scratch script (not part of the suite) ran `live` on fresh copies of the
fixtures `count` and `tour` and rewrote each document three times. It
timed the write, the `loading` event and the `generation` event, in ms:

    count {"firstLoadMs":247,"reloads":[{"edit_to_loading":201,"loading_to_generation":116,"edit_to_generation":317},
                                        {"edit_to_loading":201,"loading_to_generation":105,"edit_to_generation":306},
                                        {"edit_to_loading":201,"loading_to_generation":117,"edit_to_generation":318}]}
    tour  {"firstLoadMs":1525,"reloads":[{"edit_to_loading":201,"loading_to_generation":1291,"edit_to_generation":1492},
                                        {"edit_to_loading":201,"loading_to_generation":1316,"edit_to_generation":1517},
                                        {"edit_to_loading":200,"loading_to_generation":1317,"edit_to_generation":1517}]}

The 200 ms from the write to `loading` is the settle time. `tour` shows a
picture and comes in by a reframe, so each of its loads opens headless
Chromium to measure its layout, as `check` does; `count` opens none.

## 4. Layer 9 and the records

### Red

The two new pins in `test/repository.test.mjs` (every option the command
line declares is in the README; the README, usage line, overview, ADR,
index, changelog and `AGENTS.md` say how a film is served live), before
the records were written:

    npm test -- --cold --project pure test/repository.test.mjs
       × every option the command line declares is documented in the README 7ms
       × the manual and the records say how a film is served live (live-server) 1ms
    AssertionError: README: --port
    AssertionError: README: the command in use
          Tests  2 failed | 12 passed (14)

### Green

After the README, `CHANGELOG.md`, ADR-021 and its index row,
`docs/architecture-overview.md` and `AGENTS.md`:

     Test Files  1 passed (1)
          Tests  14 passed (14)

Then the pure and stage projects:

    npm test -- --cold --project pure --project stage
     Test Files  25 passed (25)
          Tests  265 passed (265)
    Test memo: 0 passed from the memo, 265 run
    real	0m5.000s

## 5. The final runs

The Node suite, cold, with the API 29 bundle selected (layers 2 to 9, layer
6 included):

    env -C WTs/live-server VIDEOMAKER_VIEWER_BUNDLE=…/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js npm test -- --cold
     ✓ |slow| test/pipeline/live.test.mjs (5 tests) 27455ms
     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (16 tests) 220983ms
     …
     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 147015ms
     ✓ |viewer| test/viewer/take.test.mjs (6 tests) 19696ms
     Test Files  42 passed (42)
          Tests  422 passed (422)
    Test memo: 0 passed from the memo, 422 run
    real	14m57.501s

The Python suite (no Python changed):

    env -C WTs/live-server/python PYTHONPATH=… …/.venv/bin/python -m pytest -q
    291 passed in 29.68s

## Findings

1. **`assetServer` did not handle a listen error.** A port in use would
   have left its promise pending, with an unhandled `error` event. With a
   port it can now be given, it rejects, and `live` refuses the port by
   name. The renderer's calls, on port 0, are unchanged.
2. **A film with a picture or a reframe pays for a headless Chromium at
   every reload**: about 1.3 s per reload on `tour`, against about 0.1 s on
   `count`. A cache of the measured layout, keyed by the bundle and the
   sets, would remove it. It is not proposed here; the player episode
   measures whether it matters on a real film.
3. **A file a refused document names for the first time is not yet
   watched** (design D7). After a refused load the session keeps the
   previous generation's watches, so creating the missing file does not
   reload; touching the document does. This is the cost of watching only
   what an accepted load read.
4. **`/narration.wav` is whatever `speech` last mixed**, which may be older
   than the document. The session serves it as it is; the player page will
   show it as it is.
5. **`check --width` is validated and then not used by `check`.** It was
   like this before; `live` relies on it to refuse a bad `--width` in
   `check`'s words.
6. **`--poll 0` watches** (design D8, implementation note). The design had
   first said a poll starts at 1; it now agrees with the module's own
   default.

## Not done

- The baseline spec is not synced, the change is not archived and ADR-021
  is not promoted: the campaign stops before sync.
- The player page, its build, the take transport and `machinome_movie
  watch` are the campaign's other changes.
- No browser was opened on a session: the player page that would drive one
  does not exist yet. Layer 8 reads the routes over HTTP and does not pose
  the stage page in a browser.
- Nothing was listened to or viewed: this change draws nothing new.
