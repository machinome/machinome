# Implementation evidence

## Authority and scope

A cycle of Videomaker's fix-warts campaign, on branch `narration-end-anchor`
(worktree `WTs/narration-end-anchor`), cut from `fix-warts` at `e30b05f`,
for warts 2 and 7 of *Cut and Advance* under the orchestrator's ruling on
the contract (30 September 2026). Planning commit `b83edb1`. Nothing was
pushed or published; no network or paid request was made; no `.env` was
read; nothing was installed (`node_modules` as `npm ci` left it). The
Leonardo project and its film were not read or touched: re-evaluating
*Cut and Advance* is the project's (task 6.2). Integration into `fix-warts`
is the orchestrator's.

Environment of every run: Linux, Node v24, vitest 5.0.3, Playwright's
Chromium, FFmpeg 6.1.1, the workspace venv's Python. Other fix-warts cycles
ran their suites in other worktrees at the same time, so durations are not
comparable across runs.

## Base

Before any change, on `e30b05f`:

- Node, `npm test`:

      Test Files  28 passed (28)
            Tests  291 passed (291)
         Duration  8.13s (tests 51%, import 24%, transform 15%, environment 8%, setup 2%, worker 1%)
      Test memo: 109 passed from the memo, 182 run

- Python, `python -m pytest -q` in `python/`: `186 passed in 12.62s`.

## Red first

**Layer 1 (pytest).** The new and changed expectations, before
`anchors.py` changed:

    FAILED tests/test_declarations.py::test_actions_that_finish_on_their_own_need_no_until
    FAILED tests/test_declarations.py::test_the_end_of_the_narration_is_its_own_anchor_and_names_no_phrase
    FAILED tests/test_evaluation.py::test_a_title_in_a_slot_and_the_end_of_the_narration
    FAILED tests/test_evaluation.py::test_a_completed_panel_on_the_shipped_split_and_an_arrow
    FAILED tests/test_evaluation.py::test_a_second_view_on_the_shipped_frame_and_fade_out
    FAILED tests/test_evaluation.py::test_minimal_document_has_no_optional_blocks
    6 failed, 99 passed in 3.25s

The repeated ending, verbatim (wart 2's growing tail):

    E       AssertionError: assert {'spokenEnd':..., 'plus': 0.9} == {'narrationEn..., 'plus': 0.9}
    E         Left contains 1 more item:
    E         {'spokenEnd': 'Down. Up'}
    E         Right contains 1 more item:
    E         {'narrationEnd': True}

After `anchors.py` changed and before the schema had the form, the same
tests failed on the schema check of the evaluated document:

    E           machinome_movie.names.MovieError: The movie document is invalid at chapter tip, shot invitation, field until: {'narrationEnd': True, 'plus': 1.2} is not valid under any of the given schemas

**Layer 2 (both suites, `fixtures/invalid/narration-end-not-true.json`).**
The Node side, with the schema branch added and `src/schema.mjs` unchanged:

    AssertionError: narration-end-not-true.json: refused for another reason: "Invalid movie document: chapter opening, shot question, field until must be one of: seconds, spoken anchor, spokenEnd anchor, narrationEnd anchor" does not name "until.narrationEnd"

The Python side, checked against the base commit's schema (the schema branch
had to precede the fixture, since the layer-1 evaluations validate against
it; tasks.md, implementation note):

    HEAD schema: The movie document is invalid at chapter tip, shot invitation, field until: {'narrationEnd': True, 'plus': 1.2} is not valid under any of the given schemas
    mentions: [('shot question', False), ('until.narrationEnd', False)]

**Layer 3 (vitest, pure, `test/movie-document.test.mjs`).** Before
`src/movie.mjs` changed, the re-evaluated fixtures failed fourteen of the
file's tests with `Error: chapter only, shot whole, until: the phrase
'undefined' is absent from the chapter's narration`, and the three new tests:

    × a narrationEnd anchor resolves to the end of the take's last letter or digit plus its plus, on the grid
    × a narrationEnd anchor needs its chapter's take, and a take with no letter or digit is refused naming it
    × a narrationEnd anchor is named in refusals, and one carrying another field is refused by the schema naming it
    Error: chapter opening, shot question, until: the phrase 'undefined' is absent from the chapter's narration
    AssertionError: refusal "chapter only, shot whole, until: the phrase 'undefined' is absent from the chapter's narration" does not name "Chapter only"
    AssertionError: Expected values to be strictly equal:
          Tests  3 failed | 18 skipped (21)

and the report's pure test before `chapterTakeLines` existed:

    × check's line for each chapter gives its take, its length and its tail, or says it has no take
    TypeError: chapterTakeLines is not a function

**Layer 8 (vitest, slow, `test/pipeline/movie-pipeline.test.mjs`, run with
`VIDEOMAKER_TEST_COLD=1`).** Before `bin/videomaker.mjs` printed the line:

    × the tour is checked, previewed, rendered twice and reviewed from the command line
    × the YAML fixture episode is checked, previewed, rendered twice and reviewed
    AssertionError: The input did not match the regular expression /^Tour: 3 chapters.*\n {2}opening: take 3\.94 s, chapter 4\.77 s, tail 0\.63 s\n {2}balance: take 6\.04 s, chapter 6\.67 s, tail 0\.43 s\n {2}tip: take 6\.22 s, chapter 7\.47 s, tail 1\.05 s$/m.
    AssertionError: The input did not match the regular expression /^ {2}hook: take 1\.35 s, chapter 2\.50 s, tail 0\.85 s\n {2}coupling: take 1\.90 s, chapter 2\.50 s, tail 0\.40 s\n {2}closing: take 1\.35 s, chapter 2\.00 s, tail 0\.45 s$/m.
          Tests  2 failed | 5 skipped (7)
    Test memo: 0 passed from the memo, 2 run

Green, the same file cold:

     ✓ |slow| test/pipeline/movie-pipeline.test.mjs (7 tests) 177843ms
          Tests  7 passed (7)
       Duration  179.64s (tests 100%)
    Test memo: 0 passed from the memo, 7 run

**Layer 9 (pytest, `test_repository.py`),** with the manual page stashed
back to the base:

    E       assert "The narrator sets the film's length." in '# Declaring a movie in Python A movie is declared in Python, …'
    FAILED tests/test_repository.py::test_the_manual_says_the_narrator_sets_the_length_and_what_the_end_is
    1 failed, 11 passed in 3.15s

## The resolved pins did not move (task 2.3)

The fixture documents were re-evaluated with `python -m machinome_movie
evaluate python/tests/fixtures/project <name> --out fixtures/documents/<name>.json`
(`PYTHONPATH` the worktree's `python/`). Their diff is the anchors only:
`minimal`'s `whole` `until` and, in `tour`, the `until`s of `question`,
`push` and `invitation`, the `until`s of `question`'s two cues, of `push`'s
move and arrow cue, and of `invitation`'s cue, each `{"spokenEnd": <tail>}`
become `{"narrationEnd": true}` with the same `plus`.

`fixtures/resolved/*.json` were not rewritten. Resolving the base documents
(`e30b05f`, `spokenEnd` tails) and the re-evaluated ones (`narrationEnd`)
with the final code, serialized as the pins are:

    minimal: old document (spokenEnd tails) resolves byte-identical to the pin: true ; new document (narrationEnd): true
    tour: old document (spokenEnd tails) resolves byte-identical to the pin: true ; new document (narrationEnd): true

The same probe measured the ruling's literal reading, the last character's
end (design D2):

      only/whole: last letter "w" ends 0.48 s, last character "." ends 0.54 s; until 1.2 s (pin 1.2), literal reading 1.2 s (0 frames later at 10 fps)
      opening/question: last letter "t" ends 3.78 s, last character "?" ends 3.84 s; until 4.766666666666667 s (pin 4.766666666666667), literal reading 4.833333333333333 s (2 frames later at 30 fps)
      balance/push: last letter "n" ends 5.88 s, last character "." ends 5.94 s; until 11.433333333333334 s (pin 11.433333333333334), literal reading 11.5 s (2 frames later at 30 fps)
      tip/invitation: last letter "l" ends 6.06 s, last character "." ends 6.12 s; until 18.9 s (pin 18.9), literal reading 18.966666666666665 s (2 frames later at 30 fps)

Under the literal reading every 30 fps pin moves (the film grows by six
frames, and each cue ending on `lines.end()` two frames later); under D2
nothing moves.

## The refusals, verbatim

    Python: The movie document is invalid at chapter opening, shot question, field until.narrationEnd: False is not one of [True]
    Node: Invalid movie document: chapter opening, shot question, field until.narrationEnd must be one of true, not false (read as a narrationEnd anchor)

A `narrationEnd` carrying another field (not a shared fixture; the Node pure
test pins its words):

    Python: The movie document is invalid at chapter opening, shot question, field until: {'narrationEnd': True, 'phrase': 'it'} is not valid under any of the given schemas
    Node: Unknown field: phrase (chapter opening, shot question, field until) (read as a narrationEnd anchor)

A take with no letter or digit (Node resolution):
`chapter only, shot whole, until: narrationEnd: no spoken letter or digit ends the recorded narration of chapter only`.

## Final runs

On the final content (after the archive), one suite at a time:

- Node, `npm test`:

      Test Files  28 passed (28)
            Tests  295 passed (295)
         Duration  605.05s (tests 98%, import 1%, transform 1%)
      Test memo: 0 passed from the memo, 295 run

  No verdict came from the memo: the change reaches every slow file
  (`src/movie.mjs`, `src/schema.mjs`, `src/chapters.mjs`, the fixture
  documents), so every slow test ran fresh on this content. This is not a
  `--cold` run (the artefact memo was read), but no pass was reused.
- Python, `python -m pytest -q` in `python/`: `189 passed in 11.66s`.

## Findings

1. **The ruling's two statements disagree** (design D2). "The end of the
   last character of the take" and "the tail's end and the narration's end
   are the same instant" cannot both hold for a narration ending in
   punctuation, which is every narration in the fixtures and in the film.
   The change implements the last letter or digit, which keeps every frame;
   the literal reading moves every 30 fps pin two frames (above). Smallest
   correction if the orchestrator prefers the literal reading: the
   `findLastIndex` in `resolveMovie` becomes the last index, and the pins
   are re-pinned by a person.
2. **The sharper `oneOf` refusal changes other Node wordings.** A malformed
   `spoken` or `spokenEnd` anchor on a time is now refused by its own field, for example `{"spoken": ""}` as `field until.spoken must not be
   empty (read as a spoken anchor)` and `{"spoken": "How", "extra": 1}` as
   `Unknown field: extra (…, field until) (read as a spoken anchor)`, where
   both used to be `field until must be one of: seconds, spoken anchor,
   spokenEnd anchor`. No invalid fixture pinned the old words. An object
   carrying two forms' fields (`{"narrationEnd": true, "spokenEnd": "it"}`)
   keeps the list. The model's `from`/`to` are refused by the model's own
   untitled `oneOf` first (`{"mark": 5}` as `Missing field: keys (…, field
   model)`), as before; this change leaves that alone.
3. **Python names the extra field less precisely than Node.** For
   `{"narrationEnd": true, "phrase": "it"}` `jsonschema`'s `best_match`
   stays at `until` and names `narrationEnd` and `phrase` only inside the
   value's repr. Both runtimes name the field and `narrationEnd`, which is
   what the ruling asks; a shared fixture for this form would need Python to
   descend the same way, which no film needs now.
4. **`lines.end()` with no `plus` on a chapter's last cut is refused by
   `speech`.** The take's file runs past its last letter (0.16 s in the
   fixture doubles, the provider's trailing silence in a real take), and
   `speech` requires the take to end 0.1 s before the chapter does. The
   narration end is the voice's end, not the file's; `check`'s tail line now
   shows the difference as a negative or small tail before `speech`
   refuses. Unchanged; an author writes `plus=`, as the film does.
5. **"spoken anchors" in two wordings** (`missingTake`, and step 3 of
   "Resolution" in the contract page) cover `narrationEnd` too; the words
   were left as they are, since the refusal still names the chapter and the
   command, and the page says `narrationEnd` resolves from the take.
6. The architecture overview's structure did not move (one pure function in
   `src/chapters.mjs`, one branch in `resolveMovie`); it is unchanged.

## What was not done, and why

- *Cut and Advance* was not re-evaluated or rendered: it is the Leonardo
  project's, and this change touches no project (task 6.2).
- No shared fixture for the extra-field form (finding 3): the brief asks for
  one invalid fixture, and the value form is the one both runtimes name the
  same way.
- The whole Node suite was not run `--cold` (the brief does not ask it); the
  changed slow file ran cold, and every other slow file ran fresh on the
  final content because its key changed (0 passed from the memo).
- No per-shot report, no other anchor form, no change to `spoken`,
  `spokenEnd` or snapping (out of scope).
- 0.2 (the orchestrator's review of the planning commit) and 6.1 (D2's
  ruling) are the orchestrator's.
