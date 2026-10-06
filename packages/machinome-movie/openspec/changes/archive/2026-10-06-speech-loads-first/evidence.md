# Implementation evidence

## Authority and scope

The `speech-loads-first` cycle of Videomaker's catch-up-0-8 campaign: wart
31 of *Addition*. Branch `speech-loads-first` (worktree
`WTs/speech-loads-first`), cut from `catch-up-0-8` at `e9b08f9`; the
planning commit is `9c8ff54`. The orchestrator ratified the design with
one revision before that commit: the proof is the takes layer in process
with the provider double the pipeline tests already had, and the command
line once with its existing `NO_FETCH` import, not a new child-process
double. Nothing was pushed or published. No paid request was made, `speech`
was run on no real film, and no test had a key: the in-process double runs
under a placeholder key it never sends, and the command-line runs have an
empty key and a `fetch` that throws. The Curta project's film document was
read once, to count its chapters (five), and changed nowhere.

Environment: Linux, Node v24, vitest 5.0.3, Playwright's Chromium, FFmpeg,
the workspace venv's Python 3.12 with machinome 0.8.0. The worktree's
`node_modules` is a symbolic link to the primary checkout's (same
`package-lock.json`), as the sibling worktrees have; nothing was
installed.

One sentence of the planning commit was corrected during the red, in
`design.md` D5 and task 1.1: the proof was to call `generateMovieTakes`
and expect it to refuse. Before the change it refuses none of the faults
(the refusal is the load's, after it), so the proof runs the speech
command's two steps in process, `generateMovieTakes` and then
`loadEpisode`, which is what the command does and gives the red its same
refusal after the purchase.

## The order that moves (design D3)

The take-free half of the load now runs before `generateTakes`, whose
first step is `checkAudio`. A document that both fails a take-free check of
the load and lacks a supported provider, model, voice or output format is
therefore refused for the load's fault first; before, for its audio
settings. Both are refused before any request either way, which is what the
contract asks. Nothing else's order moves: `loadMovie` continues at its
step 6 exactly as before, so `check`, `preview`, `render`, `build` and
`live` load in the same order with the same words.

## Red

The tests were written first, on the base code, and run cold:
`npm test -- --cold test/pipeline/movie-pipeline.test.mjs -t speech`.
In process, every fault was refused with the load's words (each per-fault
`assert.equal` of the refusal passed), and the provider double recorded
one request per chapter before it:

    FAIL  |slow| test/pipeline/movie-pipeline.test.mjs > the speech step refuses what the load refuses without a take, and requests none
    AssertionError: no take is requested before a refusal of the load
    + actual - expected
      [
        { fault: 'revision differs',  + requested: 3  - requested: 0 },
        { fault: 'export missing',    + requested: 3  - requested: 0 },
        { fault: 'excerpt differs',   + requested: 3  - requested: 0 },
        { fault: 'running program',   + requested: 3  - requested: 0 },
        { fault: 'identity differs',  + requested: 1  - requested: 0 }
      ]

(`tour` has three chapters, `count` one; the vitest diff is condensed
here to one line per fault, its values unchanged.)

From the command line, with `cli()`'s empty key and throwing `fetch`,
`speech` on the changed-revision copy went for a take before it loaded the
film and printed the missing-key refusal, not the load's:

    FAIL  |slow| test/pipeline/movie-pipeline.test.mjs > speech and build from the command line refuse a film its load refuses, before they try to buy a take
    AssertionError: No ElevenLabs key: set ELEVENLABS_API_KEY in the environment or in a Videomaker checkout's .env; looked in the environment (set but empty)

The key lookup comes before any `fetch` in `ensureTake`, so with an empty
key the purchase stops at the key, and the network-request error is never
reached; the test refuses both texts.

    Tests  2 failed | 2 passed | 14 skipped (18)

(The two passing tests are the existing `check type-checks the stage
modules before any speech…` and `speech generates one take per chapter…`,
selected by the same `-t speech` filter.)

## Green

`src/movie.mjs` as designed (D2): `openMovie` (steps 2 to 5 of `loadMovie`,
moved verbatim; `loadMovie` now starts with it), `checkBeforeTakes`
(`checkProject`, the evidence files, `loadSourceCode`, `loadPictures`, on
the unresolved document), `generateMovieTakes` opening and checking before
`generateTakes`, and `checkProject`'s frame count only `if(film.resolved)`.
`bin/videomaker.mjs` changed only its comment.

    ✓ check type-checks the stage modules before any speech, and refuses one that does not by name 854ms
    ✓ speech generates one take per chapter from the unresolved document, and only once 760ms
    ✓ the speech step refuses what the load refuses without a take, and requests none 482ms
    ✓ speech and build from the command line refuse a film its load refuses, before they try to buy a take 1106ms
    Tests  4 passed | 14 skipped (18)
    Test memo: 0 passed from the memo, 4 run

## Mutation

`generateMovieTakes` put back to `return generateTakes(await
pendingMovie(file));` (the early load removed), the rest of the change
kept, the same cold run:

    × the speech step refuses what the load refuses without a take, and requests none 1605ms
    × speech and build from the command line refuse a film its load refuses, before they try to buy a take 605ms
    AssertionError: no take is requested before a refusal of the load
      revision differs 3, export missing 3, excerpt differs 3, running program 3, identity differs 1 (expected 0 each)
    AssertionError: No ElevenLabs key: set ELEVENLABS_API_KEY in the environment or in a Videomaker checkout's .env; looked in the environment (set but empty)
    Tests  2 failed | 2 passed | 14 skipped (18)

The source was restored byte for byte from a copy taken before the
mutation (`cmp`), and no `MUTATION` marker remains.

## Suites

**Node**, cold, with the API 29 bundle selected
(`VIDEOMAKER_VIEWER_BUNDLE=…/machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js
npm test -- --cold`), on the final code:

    Test Files  52 passed (52)
         Tests  503 passed (503)
      Duration  927.37s
    Test memo: 0 passed from the memo, 503 run
    real 15m27.942s

No skip: the viewer layer ran on the selected bundle.

**Python** (`PYTHONPATH=<worktree>/python <venv>/bin/python -m pytest
tests -q -p no:cacheprovider --continue-on-collection-errors`, in
`python/`), which this change does not touch:

    9 failed, 96 passed, 3 errors in 2417.36s (0:40:17)

Every failure and error is the campaign's known one, the fixture project's
models under machinome 0.8 (`ImportError: module 'machinome.node' has no
attribute 'AssemblyNode': the root of machinome.node exports nothing`),
which the `fixture-under-0-8` cycle re-pins on its own worktree:
collection errors in `test_declarations.py`, `test_evaluation.py` and
`test_take.py`; failures in `test_cli.py` (2), `test_fixtures.py` (3),
`test_repository.py::test_every_emitted_document_validates` (3) and
`test_watch.py` (1). The run took forty minutes because the `test_watch.py`
test hung: its `watch` child, unable to evaluate the fixture movie, printed
no line, and the test's `next_line` blocks in `readline`, so its 120 s
deadline is never checked. The child (one process of this run, by its PID)
was stopped after 38 minutes, and the test then failed as the others did.
That is a finding, below; it is not this change's.

## Records

- `docs/movie-document.md`, "Resolution" item 2: what `speech` checks
  before it generates, stated once.
- `CHANGELOG.md`: one bullet under `Unreleased`.
- `workflow/warts.md`, Addition 31: its triage, fixed by
  `speech-loads-first`.
- `docs/architecture-overview.md`: read and not changed. Its sentence
  ("`speech` generates the takes from the unresolved document, because the
  anchors that place cuts and cues are resolved from those takes") is still
  true, and no module, boundary or flow it describes moved.
- No ADR (design, "No ADR").

## Findings met, not fixed here

1. `python/tests/test_watch.py`'s `next_line` cannot time out: `readline`
   blocks while a live child prints nothing, so a `watch` that never
   evaluates hangs the suite indefinitely instead of failing at its 120 s
   deadline (seen in this run under the fixture-project failure).
2. Under machinome 0.8 the Python suite is red at collection (the known
   campaign item; not touched here).

## Not done

No paid request; `speech` was not run on any real film; the Curta film was
not checked, previewed or rendered from this branch; nothing pushed.
