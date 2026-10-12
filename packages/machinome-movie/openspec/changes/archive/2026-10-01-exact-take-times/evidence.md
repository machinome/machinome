# Implementation evidence

## Authority and scope

Cycle 3 of Videomaker's addition-warts campaign
(`workflow/ongoing/addition-warts-campaign/plan.md`), finding 7 of
`workflow/warts.md`, "Addition (Curta, 1 October 2026)". Branch
`exact-take-times` (worktree `WTs/exact-take-times`), cut from
`addition-warts` at `c8c6309`. The planning commit is `d2708d4`. Nothing was
pushed or published; no network or paid request was made; nothing was
installed. The schema is unchanged; `docs/movie-document.md` gained one
sentence, in "The take", as the brief allowed. The viewer was reached only
through the bundle selected by path in the environment
(`machinome-viewer/machinome_viewer/widget/dist/machinome-viewer.js` of the
workspace, Viewer API 29), never written into the repository. The Curta
project was read and evaluated into a scratch file; nothing was written in
it. Integration into `addition-warts` is the orchestrator's.

Environment: Linux, Node v24.11.1, vitest, Playwright's Chromium, Python
3.12 from the workspace venv. Other agents ran their cycles' suites in
other worktrees at the same time; durations are not comparable across runs.

## Red

Every red below was run before the code it proves was written.

### Layer 1 and the Python document check (`python/tests/test_take.py`, `test_fixtures.py`)

    FAILED tests/test_take.py::test_take_time_is_the_exact_sum_of_the_written_durations
    FAILED tests/test_take.py::test_an_instructions_duration_is_summed_exactly_with_the_moves
    FAILED tests/test_take.py::test_the_document_carries_the_exact_sums - Asserti...
    FAILED tests/test_take.py::test_a_take_document_is_refused_naming_its_fault[<lambda>-names13]
    FAILED tests/test_take.py::test_a_take_document_is_refused_naming_its_fault[<lambda>-names14]
    FAILED tests/test_take.py::test_a_take_document_is_refused_naming_its_fault[<lambda>-names15]
    FAILED tests/test_fixtures.py::test_invalid_fixture_is_refused_naming_its_subjects[take-mark-summed-in-floats]
    7 failed, 148 passed in 8.24s

The assertions, verbatim:

    >       assert {name: repr(at) for name, at in trial.marks.items()} == {
    E       AssertionError: assert {'first': '1....999999999996'} == {'first': '1....third': '3.6'}
    E         Differing items:
    E         {'third': '3.5999999999999996'} != {'third': '3.6'}

    >       assert {name: repr(at) for name, at in trial.marks.items()} == {'moved': '0.3',
    E         Differing items:
    E         {'moved': '0.30000000000000004'} != {'moved': '0.3'}

    >       assert written['marks'] == {'first': 1.2, 'second': 2.4, 'third': 3.6}
    E         Differing items:
    E         {'third': 3.5999999999999996} != {'third': 3.6}

    >       with refused(*names):
    E       Failed: DID NOT RAISE MovieError        (the three mutations a hair off: step-2 at
                                                     2.0000000000000004, the length 7.999999999999999,
                                                     the mark nine 6.000000000000001)

    >       with pytest.raises(MovieError) as refusal:
    E       Failed: DID NOT RAISE MovieError        (take-mark-summed-in-floats)

### Layer 2 and 3, Node (`test/movie-document.test.mjs`, `test/take.test.mjs`)

    FAIL  |pure| test/movie-document.test.mjs > every invalid fixture is refused by the static checks, naming every word it must
    AssertionError: take-mark-summed-in-floats.json was not refused

    FAIL  |pure| test/take.test.mjs > a mark is found at its step's written end, and a mark summed in floats is refused naming it
    AssertionError: was not refused

    FAIL  |pure| test/take.test.mjs > a frame is on a mark only at the mark's take time exactly
    AssertionError: 3.6000000000000005 is not the mark third
    'third' !== null

    FAIL  |pure| test/take.test.mjs > check's take line gives the marks and the length as the document writes them
    + 'Take: 3 steps, marks first 1.2 s, second 2.4 s, third 3.6 s, 3.5999999999999996 s long; the replay of its steps gives the recorded bank at every mark'
    - 'Take: 3 steps, marks first 1.2 s, second 2.4 s, third 3.6 s, 3.6 s long; the replay of its steps gives the recorded bank at every mark'

    FAIL  |pure| test/take.test.mjs > a take document whose steps, length or marks were summed in floats is refused naming the field
    AssertionError: was not refused

The tests of the pose rule call `bankAt` with the document, the new
signature, so on the old module they failed first on the signature
(`TypeError: take.steps is not iterable`), as did the existing pose tests
moved to it. The behaviour they prove was shown red with the old module's
own signature, on the same take of four 1.2 s steps whose fourth has a
commit at fraction 0 (a scratch script, not committed):

    bankAt(take, 3.6) = {"crank":1080,"flag":1} ; recorded at the mark third: {"crank":1080,"flag":0}

The float end of the third step, `2.4 + 1.2 = 3.5999999999999996`, gave the
mark 3.6 to the fourth step at `f = 0`, which wrote its commit on the mark:
a frame posed there differs from the recorded bank, and the renderer would
have refused it ("Viewer bank differs from the take at mark third").

## Green

Python, the whole suite on the final content (after the archive):

    286 passed in 19.01s

Node, the whole suite with the API 29 bundle selected
(`VIDEOMAKER_VIEWER_BUNDLE`), on the implementation before the archive.
Nothing came from the memo, since `src/take.mjs` is reached by every slow
test's key:

     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 152158ms
     ✓ |viewer| test/viewer/take.test.mjs (5 tests) 22384ms
     Test Files  38 passed (38)
          Tests  378 passed (378)
       Duration  957.61s (tests 98%, import 1%, environment 1%, transform 1%)
    Test memo: 0 passed from the memo, 378 run

and again on the final content, after the archive synced the baseline specs
(no source changed between the two runs):

     ✓ |viewer| test/viewer/real-viewer.test.mjs (7 tests) 1311ms
     ✓ |viewer| test/viewer/take.test.mjs (5 tests) 925ms
     Test Files  38 passed (38)
          Tests  378 passed (378)
       Duration  22.58s (tests 59%, import 18%, environment 11%, transform 9%, setup 3%, worker 1%)
    Test memo: 142 passed from the memo, 236 run

`openspec validate --specs --strict`: 16 passed, 0 failed.

No fixture document or resolved pin changed: the shared fixtures' durations
are whole seconds, so the exact sums are the integers they were, and the
Python suite's equality with `fixtures/documents/*.json` and the Node
suite's resolution to `fixtures/resolved/*.json` pass without re-pinning.
`scripts/pin-fixture-project.mjs` was not run.

## The film, as a no-regression check

The Curta film's movie evaluated from this worktree, by the project's real
path, into a scratch file (nothing written in the project; `git status` of
the project unchanged before and after):

    PYTHONPATH=<worktree>/python python -m machinome_movie evaluate <project> addition --out <scratch>/addition-movie.json

compared with `videos/addition/_build/movie.json`, the document the film
was rendered from:

    marks (rendered):    {'added_145': 18.75, 'added_23': 9, 'rest': 0, 'set_145': 12.75, 'set_23': 3, 'tens_4': 11.5, 'units_3': 1.5, 'units_5': 10.25}
    marks (this change): {'added_145': 18.75, 'added_23': 9, 'rest': 0, 'set_145': 12.75, 'set_23': 3, 'tens_4': 11.5, 'units_3': 1.5, 'units_5': 10.25}
    length: 18.75 18.75
    steps at/duration equal: True
    take block identical: True
    top-level fields that differ: ['root']
    model fields that differ: []

`root` differs only because the scratch document is written elsewhere. The
same take with the three setting moves drawn over 1.2 s instead of 1.25 s
(a class derived in memory from the film's `Addition`, not written
anywhere) has the marks the finding reported drifting, now exact:

    {'rest': 0, 'units_3': 1.5, 'set_23': 3, 'added_23': 9, 'units_5': 10.2, 'tens_4': 11.4, 'set_145': 12.6, 'added_145': 18.6} 18.6

(the float sum gave `11.399999999999999` and `12.599999999999998`).

## Findings

1. **A mark with a `plus` on a shot's model time is still a float sum on
   the reader's side.** `movie.mjs` resolves `{"mark": m, "plus": p}` as
   `marks[m] + p` and both runtimes range-check it with the 1e-9 tolerance
   kept for that purpose. No Python declaration writes a `plus` on model
   time (`Take.run` and `Take.keys` take marks or numbers), so no film has
   one; a hand-written document whose `mark + plus` lands on another mark
   would pose a hair off it. The smallest correction, if a film ever needs
   it, is the same exact sum (`takeTimes`'s arithmetic) in the resolver and
   the range check.
2. **The renderer's mark check used to match a frame within 1e-9 s of a
   mark, then compare its bank with the mark's exactly.** Any frame that
   matched without being exactly on the mark was posed inside a step by the
   pose rule and would have been refused ("Viewer bank differs from the
   take at mark"), unless the moving input had not moved. No film met it
   (a shot starting on a mark poses take time `from` exactly). `markAt` is
   now exact, as the spec already said ("a frame whose take time is a mark
   exactly"); recorded so the orchestrator can judge whether it was a
   latent wart of `pose-a-take`.

## What was not done, and why

- Durations as frame counts or snapped to the frame grid, any change to
  easing, to how a frame's take time is computed from video time, or to
  which frame owns an instant: out of the brief.
- The `plus` sum of finding 1: no film or Python declaration writes it.
- The `--cold` switch was not used: the first whole run took nothing from
  the memo (378 run), which is the cold run's content for this change; a
  `--cold` run before integration remains the orchestrator's to ask for.
- The film was not re-rendered or re-checked with `check`/`preview`: its
  document's take is byte-identical but for `root`; the renderer's
  provenance includes `src/take.mjs`, so the film's shots recapture once at
  its next render. `workflow/warts.md` was not edited (the orchestrator's).
