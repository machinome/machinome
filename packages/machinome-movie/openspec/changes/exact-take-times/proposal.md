## Why

The episode is *Addition*, the Curta film of the curta-video campaign (the
Curta Type I 3x project, `videos/addition/`, `23 + 145`), the first film on
a clocked take. Finding 7 of `workflow/warts.md` ("Addition (Curta,
1 October 2026)"): **mark times drift when `over` durations are summed in
floats.** The take's moves were first written `over=1.2`; evaluation summed
the durations in binary floats (`at = at + planned.duration` in
`python/machinome_movie/take.py`) and the document carried marks like
`12.599999999999998`, which `check` printed as the film's mark times. The
film worked around it by choosing binary-exact steps of 1.25 s. The Node
side then re-derived every step's end as `at + duration`, in floats again,
and met the written marks only through a tolerance of 1e-9 s (`TOLERANCE`,
`markSteps`, `markAt`, `bankAt` in `src/take.mjs`).

Three moves of 1.2 s end at 3.6. Summed as floats they end at
3.5999999999999996, and so does the sum of the binary values nearest 1.2,
summed exactly and rounded once (a tie that rounds to even). The duration an
author wrote is a decimal; the sum of decimals is a decimal; the document
should carry it.

## What the film does with the result

The Curta film, and the next take on a clocked machine, can draw a step over
the seconds its screenplay wants (1.2 s, 0.4 s, an instruction's 6 s) rather
than over a binary-exact number chosen to keep the marks clean: its marks,
its steps' `at` and its length are the decimals the durations add up to,
`check` prints them so, and a frame posed on a mark is posed on that mark's
recorded bank without a tolerance in between. The film's own 1.25 s steps
are already exact; evaluated from this change its marks are unchanged, which
is this change's no-regression check on the real film.

## What Changes

- **Python sums take time exactly.** A `Take`'s steps' `at`, its marks and
  its length are summed from the durations as written (a move's `over=`, an
  instruction's declared `duration`), each read through its shortest decimal
  form, in exact rational arithmetic, and written as the number nearest the
  exact sum: an integer when it is whole, otherwise the double whose
  shortest form is the sum's decimal (`3.6`, not `3.5999999999999996`).
- **Both runtimes hold the document's sums exactly.** The document check,
  Python's and Node's, compares each step's `at`, the take's length
  (`model.expectedDurationSeconds`) and every mark with the exact sum of the
  written durations before it, with no tolerance; a document whose sums
  were made in floats is refused naming the field (`take.steps[i]` and
  `at`, `model.expectedDurationSeconds`, or `marks.<name>` and `end of a
  step`). A new shared invalid fixture, `take-mark-summed-in-floats`, is
  refused by both.
- **Node reads what is written.** A step's end is the next step's `at`,
  and the last step's the take's length, as the document writes them; the
  pose rule (`bankAt`), the marks a step ends at (`markSteps`), the mark a
  frame is posed on (`markAt`, now exact) and `check`'s take line (the
  length) read them and never add two take times in floats.
- **Contract and manual.** One sentence in "The take" of
  `docs/movie-document.md` says the sums are exact; `docs/declaring-a-movie.md`
  says so where it says take time is the sum of the durations.
- **Records**: ADR-016 (SOURCE), `CHANGELOG.md`, `fixtures/README.md`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `declarative-movie`: a `Take`'s take time is the exact sum of the
  durations as written.
- `movie-document`: a take document carries exact sums and both runtimes
  hold them exactly; the pose at a take time reads a step's end as written;
  `check`'s take line gives the length as written.

## Impact

Code: `python/machinome_movie/names.py` (the exact sum), `take.py`
(`Take._time`), `document.py` (`check_take`); `src/take.mjs` (the exact sum,
the written ends, `bankAt`, `markSteps`, `markAt`, `takeLine`),
`src/movie.mjs` (`checkTake`), `src/timeline.mjs` (`bankAt` takes the
document). Tests at layers 1, 2 and 3; one invalid fixture. No schema
change, no stage or viewer change, no change to how a frame's take time is
computed from video time. The fixture documents' durations are whole
seconds, so no pinned document is expected to change; `src/take.mjs`
changes, so the renderer's provenance and the slow tests that reach it
recompute once.

## Non-goals

Durations as frame counts, or snapped to the frame grid: a duration off the
grid (0.35 s at 30 fps) stays legal, and which frame owns an instant is the
renderer's rule, unchanged. No change to easing, to the frame-ownership
rule, or to a shot's model time between keys. A mark with a `plus` offset on
a shot's model time, which no Python declaration writes, keeps the reader's
float sum and its range check's tolerance. No publication, push or paid
request.
