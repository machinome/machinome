## Context

A clocked take (`declare-a-take`, ADR-011) declares its time: each `Move`
is drawn over its `over=` seconds, each `Trigger` over its instruction's
declared `duration`, and a `Mark` names the instant after the step before
it. `Take._time` (`python/machinome_movie/take.py`) sums the durations in
floats (`at = at + planned.duration`) and writes the running sums as the
steps' `at`, the marks and the length (`model.expectedDurationSeconds`).
The document check (`document.py`, `check_take`; `src/movie.mjs`,
`checkTake`; `src/take.mjs`, `markSteps`) re-adds `at + duration` in floats
and compares with 1e-9 s of tolerance. The pose rule (`bankAt`) decides
which step owns a take time by `seconds <= step.at + step.duration`, again a
float sum, and the renderer's mark check (`markAt`) matches a frame's take
time to a mark within the same tolerance.

The Curta film met the drift (finding 7): with `over=1.2` after a take time
of 9 s the marks were `10.2`, `11.399999999999999` and
`12.599999999999998`. The film chose 1.25 s steps, which are binary-exact.

The contract (`docs/movie-document.md`, "The take") already says a step's
`at` is the sum of the durations before it, the length is the last step's
`at` plus its `duration`, a mark is the instant after the step before it,
and a step owns `at < t ≤ at + duration`.

## Goals / Non-Goals

Goals: the document carries the exact decimal sums of the durations an
author wrote; both runtimes hold them exactly; Node reads the written ends
and never re-derives a take time by adding floats. Non-goals: those of the
proposal; in particular no frame-grid arithmetic and no change to which
frame owns an instant.

## Decisions

### D1. A duration is the decimal its shortest form writes, summed as a fraction

Python reads each duration through its shortest decimal form, `repr`, into
a `fractions.Fraction` (`Fraction(repr(1.2))` is `6/5`), sums the
fractions, and writes each sum as the number nearest it: the integer when
the sum is whole, otherwise `float(sum)`, which Python rounds correctly, so
the double written is the one whose shortest form is the sum's decimal
whenever the sum has at most fifteen significant digits (every take a
person writes). Two helpers in `names.py`, beside the other number rules:
`exact(seconds)` and `written(total)`.

Why `Fraction` rather than `decimal.Decimal`: both are exact for the sum of
a few decimals, but `Decimal` arithmetic runs in a context whose precision
(28 digits by default) silently rounds a long sum; a `Fraction` has no
context and is exact by construction, and its conversion to a double is
correctly rounded. Why through `repr` rather than the float itself:
`Fraction(1.2)` is the binary value nearest 1.2, and three of them, summed
exactly and rounded once, land on a tie that rounds to even:
`3.5999999999999996`, the same drift. The author wrote `1.2`; `repr` gives
back exactly what was written for every literal of up to fifteen
significant digits.

Rejected:

- **Sum on the frame grid.** Take time is declared in seconds and the
  output's frame rate belongs to the output; a duration off the grid stays
  legal, and which frame owns an instant is the renderer's rule. The
  campaign's cut rules frame counts out.
- **Round each sum to a fixed number of decimals.** A knob with no
  meaning, which would still leave the Node side comparing with a
  tolerance.
- **Keep the floats and widen the tolerance.** The marks `check` prints
  and the document carries would stay wrong.

### D2. The document's sums are held exactly, by both runtimes

The check of a take document recomputes the exact sum of the written
durations, step by step, the same way on both sides, and compares with
what is written, with no tolerance: each step's `at` must be the sum of
the durations before it, `model.expectedDurationSeconds` the sum of all of
them, and every mark 0 or the written end of a step. The refusals keep
their words: `take.steps[i] (step-n): at is … s, and the steps before it
end at … s`, `model.expectedDurationSeconds is … s, and the take's steps
end at … s`, `marks.<name>: … s is neither 0 nor the end of a step`. A
document whose sums were made in floats is now refused; the shared invalid
fixture `take-mark-summed-in-floats` (the counter's take with three steps
of 1.2 s, its last mark written `3.5999999999999996`) proves both sides
refuse it naming `marks.ten` and `end of a step`.

Node sums the same way Python does: `String(number)` gives the shortest
digits that round-trip, as Python's `repr` does (both choose the closest
shortest decimal; the formats differ only in where they switch to an
exponent, which the parser accepts either way); the digits become a
`BigInt` scaled by a power of ten, the sums are integer sums, and
`Number('<digits>e<exponent>')` rounds the exact sum to the nearest double,
as `float(Fraction)` does. The two runtimes therefore produce the same
double for the same written durations, and compare with `===` and `==`.

The 1e-9 tolerance leaves `src/take.mjs`. It stays where a reader adds a
number of its own to a take time, the range check of a shot's model time
written as a mark with a `plus` (`movie.mjs`, `document.py`), which no
Python declaration writes and this change does not touch.

### D3. Node reads the written ends

The end of step `i` is the next step's `at`, and the end of the last step
the take's length, `model.expectedDurationSeconds`, as the document writes
them (D2 has held them to the exact sums). `src/take.mjs` reads them:

- `bankAt(doc, t)` takes the document instead of its `take` block, since
  the last step's end is the take's length. The owning step is the first
  whose written end is at or after `t`; at its written end exactly the
  bank is the one the step ended with. Under the float sum a step of 1.2 s
  starting at 2.4 ended at `3.5999999999999996`, so the mark at 3.6 was
  owned by the next step at `f = 0`, and a commit of that step at fraction
  0 was written one instant early, on the mark.
- `markSteps(doc)` finds a mark's step by `===` against the written ends.
- `markAt(doc, t)` returns a mark only when the take time is that mark
  exactly. A take time a hair off a mark is posed inside a step, on a bank
  that is not the mark's recorded one, so the tolerance only ever matched
  an instant the renderer would then refuse ("Viewer bank differs from the
  take at mark"); the spec already says "a frame whose take time is a mark
  exactly". A shot that starts on a mark poses take time `from` exactly
  (the linear key at its own instant is its value).
- `takeLine(doc)` prints the length as written.

`src/timeline.mjs` passes the film to `bankAt`. How a frame's take time is
computed from video time is unchanged.

## Risks / Trade-offs

- A document hand-written with float sums, which no film has, is refused
  where it was accepted; the refusal names the field and the expected
  number.
- `Number()` of a decimal string is required to round correctly up to 20
  significant digits by the language and does so beyond in V8; a sum of
  durations as a person writes them has far fewer.
- The renderer's provenance hashes `src/take.mjs`, so every film's shots
  recapture once.

## The words

Unchanged refusals, one new fixture: `take-mark-summed-in-floats`, must
mention `marks.ten` and `end of a step`.
