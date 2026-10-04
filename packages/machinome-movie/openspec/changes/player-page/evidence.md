# Evidence — `player-page`

Worktree `WTs/player-page`, branch `player-page`, cut from the `player`
head e7703df, which carries `take-transport` and `live-server` merged. The
merge defect found on the base was fixed first, in its own commit 2c46e84;
the planning commit is 03a77b9, made after the orchestrator ratified the
proposal by message on 4 October 2026 with two instructions (the merge
defect fixed in this branch first; the ruler made a scrubber). The viewer
bundle for layer 6 is selected by path in the environment
(`VIDEOMAKER_VIEWER_BUNDLE`, `machinome-viewer 0.7.1 - viewer API 29`,
sha256 `b5fcdb8613aceb3936c09d755af41f1ceb9ad1125e4f5bc4e671a568a0920107`),
never written into the repository.

Nothing was pushed or published. No network or paid request was made and
no speech was generated: every take is a fixture's, the layer 5 and 8
tests replace `fetch` so a request beyond the loopback interface fails,
and the test environment carries no key. Nothing was installed
(`node_modules` is the primary's, linked). No real film was touched and no
proof ran on one (finding 16 of `workflow/warts.md`). No `pkill` or `kill`
with a pattern was run. Environment: Linux, Node v24.11.1, vitest 5.0.3,
Playwright's Chromium, the workspace venv's Python.

## The base, and the merge defect

The Node suite cold with the API 29 bundle on e7703df, this change's
directory untracked:

    env -C WTs/player-page VIDEOMAKER_VIEWER_BUNDLE=… npm test -- --cold
     FAIL  |pure| test/repository.test.mjs [ test/repository.test.mjs ]
    Error: Failed to parse source for import analysis because the content contains invalid JS syntax.
     Test Files  1 failed | 46 passed (47)
          Tests  445 passed (445)
    Test memo: 0 passed from the memo, 445 run
    exit 1 elapsed 947 s

Every viewer file ran (`transport`, `real-viewer`, `take`), none skipped.
The failing file did not parse: the merge of `live-server` into `player`
(e94ca59) dropped the `});` that closes the take-transport pin of
`test/repository.test.mjs` (`node --check` passes the file at both parents,
1cfdf2b and 537fed3, and fails it at e94ca59), so none of its fifteen
repository pins had run on the merged head. The Python suite on the base:

    env -C WTs/player-page/python PYTHONPATH=… …/.venv/bin/python -m pytest -q
    291 passed in 28.08s

2c46e84 (`test: close the take-transport pin the live-server merge left
open`) restored the brace. On it, the merged head's fifteen repository pins
ran for the first time, and passed:

    npm test -- --cold --project pure test/repository.test.mjs
     ✓ |pure| test/repository.test.mjs (15 tests) 116ms
     Test Files  1 passed (1)
          Tests  15 passed (15)
    Test memo: 0 passed from the memo, 15 run

## Red first, innermost first

### Layer 1 and 9 (pytest): `watch`

`python/tests/test_watch.py` and the manual pin of `test_repository.py`
written, `watch.py` absent:

    python -m pytest -q tests/test_watch.py tests/test_repository.py
    E   ModuleNotFoundError: No module named 'machinome_movie.watch'
    ERROR tests/test_watch.py
    1 error in 0.33s

    python -m pytest -q tests/test_repository.py
    FAILED tests/test_repository.py::test_the_manual_and_the_package_readme_document_the_watch
    1 failed, 16 passed in 3.34s

    python -m machinome_movie watch /tmp minimal
    python -m machinome_movie: error: argument command: invalid choice: 'watch' (choose from 'list', 'evaluate')
    status 2

Green after `watch.py`, the subcommand and the manual:

    python -m pytest -q tests/test_repository.py tests/test_watch.py
    23 passed in 11.83s

### Layer 3: the marks in video time

    npm test -- --cold --project pure test/live.test.mjs
       × the marks in video time: the first frame of a shot that reaches each mark, and none for a mark no frame reaches 7ms
       × a mark is flagged once where a shot holds at it, and where a shot crosses it backwards 1ms
    TypeError: markInstants is not a function
          Tests  2 failed | 7 passed (9)

Green after `markInstants` and the outline's `marks` (9 passed).

### Layer 4: the player's pure parts, and its type check

`player/model.test.ts`, `player/poser.test.ts`, the `stage` project given
`player/**/*.test.ts`, the `tsc -p player/tsconfig.json` test beside the
others, `player/` holding only the tests:

    npm test -- --cold --project stage player/
     FAIL  |stage| player/model.test.ts [ player/model.test.ts ]
    Error: Failed to resolve import "./model" from "player/model.test.ts". Does the file exist?
     FAIL  |stage| player/poser.test.ts [ player/poser.test.ts ]
    Error: Failed to resolve import "./poser" from "player/poser.test.ts". Does the file exist?
     Test Files  2 failed (2)
          Tests  no tests

    npm test -- --cold --project pure test/stage-types.test.mjs -t "player compiles"
         × the player compiles strictly, its tests included: tsc --noEmit -p player/tsconfig.json 132ms
    + error TS5058: The specified path does not exist: '…/WTs/player-page/player/tsconfig.json'.
          Tests  1 failed | 12 skipped (13)

Green after `model.ts`, `poser.ts`, `tsconfig.json`:

     ✓ |stage| player/model.test.ts (21 tests) 14ms
     ✓ |stage| player/poser.test.ts (3 tests) 12ms
          Tests  24 passed (24)
    tsc --noEmit --pretty false -p player/tsconfig.json: no output, exit 0

### Layer 9: the build and the boundary

`test/player-build.test.mjs`, the player's import pin and the transport's
refusal of `../player/…` in `test/transport-boundary.test.mjs`, the reads
table entry for `src/player-build.mjs`, the build module absent:

    npm test -- --cold --project pure test/player-build.test.mjs test/transport-boundary.test.mjs test/memo.test.mjs
       × every file of the player imports only its own files and the take transport, and its tests also the runner 17ms
     FAIL  |pure| test/player-build.test.mjs [ test/player-build.test.mjs ]
    Error: Cannot find module '../src/player-build.mjs' imported from …/test/player-build.test.mjs
    AssertionError: player/index.html
          Tests  1 failed | 30 passed (31)

After `src/player-build.mjs` and the page, the pin refused a comment of
`player/css.d.ts` ("a module computed at run time": the words
"import (`import './player.css'`)" read as `import(`); the comment was
reworded, and the second-checkout helper made once per file (a second
`symlink` refused `EEXIST`). Then:

     Test Files  4 passed (4)
          Tests  46 passed (46)

### Layer 8: `live` serves the built player

`test/pipeline/live.test.mjs` given the built player at `/` (and the reuse
by a second session), `live` not yet building it:

    npm test -- --cold --project slow test/pipeline/live.test.mjs -t "a session on the counter"
       × a session on the counter serves the outline, … then stops 1234ms
    AssertionError: / is the built player
    +   404,
    +   'The player is not built'
    -   200,
    -   ''

Green after `live` builds the player once before it serves (5 passed).

### Layer 5: the page in a browser

`test/browser/player.test.mjs` written (nine tests). Red with `live`'s call
of `buildPlayer` replaced by `{}` (a mutation, restored and compared with
`cmp`), so `/` answers 404 and the page never defines `window.player`:

    npm test -- --cold --project slow test/browser/player.test.mjs
       × the movie surface poses the frame /frame gives … 30553ms
       … (all nine)
    TimeoutError: page.waitForFunction: Timeout 30000ms exceeded.
          Tests  9 failed (9)

With the player built, before the double accepted a mount without a camera
and before the session answered the mix by ranges:

       × the ruler of the counter, the keys and the clicks … 662ms
       × with the narration mixed, the movie surface's clock is the mix … 1481ms
       × the take surface poses the counter's take on the viewer alone … 531ms
       × on the tour: … and the loop on the take surface 32870ms
          Tests  4 failed | 5 passed (9)

- the ruler: the browser writes `4.3860%` back as `4.386%`; the test now
  compares the numbers;
- the narration: `The mix is Infinity s and the film 11.40 s`: the session
  answered `/narration.wav` without its length or ranges (finding 3);
- the take surface and the tour's loop: the double read `options.view.camera`
  of a mount without a camera (`window.viewerMounts` undefined, the loop's
  mount refused); the double now takes a camera of its own and records each
  mount's options.

The ranges, red at layer 8 first (`npm test -- --cold --project slow
test/pipeline/live.test.mjs -t "a session on the counter"`):

    AssertionError: Expected values to be strictly deep-equal:
    +   null,
    +   null
    -   '2188878',
    -   'bytes'

then green (5 passed). Layer 5 green:

     ✓ |slow| test/browser/player.test.mjs (9 tests) 17667ms
          Tests  9 passed (9)

Three mutations of the page, each restored and compared with `cmp`:

- a composed join posed as its incoming frame throughout:
  `× on the tour: …` `AssertionError: Expected values to be strictly deep-equal`;
- every generation reloading the stage page:
  `× a generation with the same stage page …` `AssertionError: the stage page was not reloaded`;
- the scrubber not following a held pointer:
  `× a drag on the ruler …` `AssertionError: frames of once and of nine were posed: 20`.

### Layer 6: the take surface on the real viewer

`test/viewer/player.test.mjs` passed on its first run (the page was written
before it). Its red is a mutation, the take posed half a second early:

    VIDEOMAKER_VIEWER_BUNDLE=… npm test -- --cold --project viewer test/viewer/player.test.mjs
       × the take surface poses the counter's take on the real viewer: … 1231ms
    AssertionError: the viewer holds the bank the take records at the mark nine

Then a screenshot of the take surface on the real viewer (a scratch script,
not part of the suite) showed the model small in the top left: the real
viewer sets `position: relative` on the element it is mounted in, which
undid the host's `position: absolute; inset: 0`, and the host shrank to
150 px (finding 4). The bank proof had passed regardless. The page now
mounts the viewer in a target that fills a host, and the test asserts the
canvas fills the take surface; red by the mutation that mounts in the host
again:

    AssertionError: the canvas fills the take surface: {"region":[1000,633.8125],"canvas":[1000,150]}

then green (1 passed).

### The records (layer 9)

The pin `the manual and the records say how the player shows a film and a
take, and what it does not draw (player-page)` before the records:

       × … (player-page) 12ms
    AssertionError: README: `#movie`
          Tests  1 failed | 15 passed (16)

Green after the README, ADR-022 and its index row, the changelog bullet,
the overview, `AGENTS.md` and the manual (16 passed). The pure and stage
projects then: `Test Files 31 passed (31)`, `Tests 328 passed (328)`.

## The final runs

A first cold run on the content then (1 failed | 500 passed (501), 1029 s)
failed one test: `with the narration mixed, …`: `The mix is 5.46 s and the
film 11.40 s: run speech again`. The session had accepted a generation
while `speech` was still writing the mix, and that generation's audio
element, already replaced, reported its partial length after the next one
had cleared the note (finding 5). The page now stops a replaced element
loading and ignores what it reports, and the test waits for the session's
last generation after `speech`; run three times alone, it passed three
times. Then, on the final content (the evidence file excepted):

    env -C WTs/player-page VIDEOMAKER_VIEWER_BUNDLE=… npm test -- --cold
     ✓ |pure| test/player-build.test.mjs (2 tests)
     ✓ |pure| test/repository.test.mjs (16 tests)
     ✓ |pure| test/transport-boundary.test.mjs (5 tests)
     ✓ |pure| test/live.test.mjs (9 tests)
     ✓ |pure| test/memo.test.mjs (26 tests)
     ✓ |stage| player/model.test.ts (21 tests)
     ✓ |stage| player/poser.test.ts (3 tests)
     ✓ |pure| test/stage-types.test.mjs (13 tests)
     ✓ |slow| test/pipeline/live.test.mjs (5 tests)
     ✓ |slow| test/browser/player.test.mjs (9 tests)
     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests)
     ✓ |viewer| test/viewer/take.test.mjs (6 tests)
     ✓ |viewer| test/viewer/player.test.mjs (1 test)
     ✓ |viewer| test/viewer/transport.test.mjs (2 tests)
     …
     Test Files  52 passed (52)
          Tests  501 passed (501)
       Duration  1060.46s
    Test memo: 0 passed from the memo, 501 run
    exit 0 elapsed 1062 s

Layer 6 ran on the bundle, none skipped. 445 on the base, whose fifteen
repository pins did not run; 460 on 2c46e84; this change adds five files
(36 tests: `player/model.test.ts` 21, `player/poser.test.ts` 3,
`test/player-build.test.mjs` 2, `test/browser/player.test.mjs` 9,
`test/viewer/player.test.mjs` 1) and five tests to existing files
(`test/live.test.mjs` 2, `test/repository.test.mjs`,
`test/transport-boundary.test.mjs` and `test/stage-types.test.mjs` 1 each),
and extends the existing `test/pipeline/live.test.mjs` (the built player at
`/`, its reuse by a second session, the mix by ranges).

The Python suite on the final content:

    env -C WTs/player-page/python PYTHONPATH=… …/.venv/bin/python -m pytest -q
    298 passed in 51.59s

(291 on the base; `tests/test_watch.py` adds 6 and `test_repository.py` 1.)

## Edits to the planning artifacts after the planning commit

- `design.md` D5 (the mix by ranges), D7 (the viewer mounted in a target
  that fills a host; the take ruler's ground row); `specs/live-preview`:
  the requirement "The mix is served with its length and by byte ranges";
  `tasks.md`: ticked, task 5.3 added.

## Findings

1. **The live-server merge left `test/repository.test.mjs` unparsed**
   (e94ca59): fifteen repository pins did not run on `player` until
   2c46e84. A merge with unions in a test file passed nothing that would
   notice: the suite reported "1 failed" for the file, not for its tests,
   and the counts (445 passed) looked whole.
2. **`python/tests/test_cli.py` runs the primary checkout's package in a
   worktree.** Its `run()` gives the child only `PATH` and
   `PYTHONDONTWRITEBYTECODE`, and the workspace venv's editable install
   points at the primary checkout, so in `WTs/<name>/` the command-line
   tests prove the primary's `machinome_movie`, not the worktree's.
   `test_watch.py` passes `PYTHONPATH` for its own runs; `test_cli.py` is
   not changed here.
3. **The session answered `/narration.wav` without its length or ranges**
   (live-server): an audio element took the mix for a stream of unknown
   length and could seek only what it had read. Fixed in this change
   (design D5), pinned at layer 8.
4. **The real viewer styles the element it is mounted in**
   (`position: relative`): a page that mounts it in an absolutely placed
   element loses that placement. The layer 6 bank proof could not see it;
   a screenshot did. Pinned now (the canvas fills the surface).
5. **A generation can be accepted while `speech` is still writing the
   mix**: the session settles 200 ms after the first event and loads while
   FFmpeg writes; the next event brings the whole mix. The page shows the
   last one; the note on a length mismatch can flash in between.
6. **The viewer's handle declares no release.** A take surface mounted
   again (a new export, or switching surfaces) leaves the previous
   instance, rendering continuously, to the page's garbage collection.
7. **The counter's mark `ten` is never reached by the film**: `carry`'s
   last frame poses 7.97 s of the take, so the movie ruler flags `one` and
   `nine` only, and the take surface all three. A film fact, said by the
   outline, not a defect.
8. **A flag at the ruler's end overflowed the page**, and a click there
   scrolled the page sideways though the body hid its overflow; the page
   now clips its overflow and labels a flag near the end on its left.

## What was not done

- The baseline specs are not synced, the change is not archived and
  ADR-022 stays Proposed: the campaign stops before sync.
- No composed join or fade is drawn live; the readout says so.
- No timing of playback was measured: no verdict reads a clock, the
  clocks are proved at layer 4 (take-transport), and the page's play is
  proved only to start and stop. The cost of a pose on a GPU, the Curta
  keeping the narration's pace, and the time from an edit to the frame on
  screen are the episode's, the pilot's, in a browser.
- Nothing was listened to. The player was looked at in headless Chromium
  only, by screenshots of the fixture `count` and `tour` with the real
  viewer (the movie surface inside the reframe into `question` and at 6 s;
  the take surface at the mark `ten`; the loop at `fall`).
