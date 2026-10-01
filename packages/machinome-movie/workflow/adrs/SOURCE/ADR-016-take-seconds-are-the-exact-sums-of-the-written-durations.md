# ADR-016: Take seconds are the exact sums of the written durations

Status: Accepted (OpenSpec change `exact-take-times`, 1 October 2026)

Numbered 016 by the addition-warts campaign's plan; ADR-013 to ADR-015 and
ADR-017 onward are other cycles' of the same campaign. A merge that
reorders them renumbers.

## Context

A clocked take declares its time (ADR-011): a `Move` is drawn over its
`over=` seconds, a `Trigger` over its instruction's declared duration, and
a `Mark` names the instant after the step before it. Evaluation summed the
durations in binary floats and wrote the running sums into the document as
each step's `at`, the marks and the take's length; the Node side re-added
`at + duration` in floats to find a step's end and met the written marks
through a tolerance of 1e-9 s, in the document check, in the pose rule and
in the renderer's check of a frame posed on a mark (ADR-012).

The Curta film *Addition* met the drift (finding 7 of its warts): moves of
1.2 s after the 9 s mark gave marks `10.2`, `11.399999999999999` and
`12.599999999999998`, which the document carried and `check` printed. The
film chose binary-exact steps of 1.25 s to avoid it. The re-derivation had
a sharper edge: a step of 1.2 s from 2.4 ended, in floats, at
`3.5999999999999996`, so the mark at 3.6 belonged to the next step at
`f = 0`, and a commit of that step at fraction 0 was posed on the mark, one
instant early, where the recorded bank does not have it.

## Decision

**A duration is the decimal its author wrote, and take seconds are its
exact sums.** Python reads each duration through its shortest form
(`repr`) into a `fractions.Fraction`, sums the fractions, and writes each
sum as the number nearest it: the integer when it is whole, otherwise the
correctly rounded double, whose shortest form is the sum's decimal. Three
steps of 1.2 s end at 3.6. The document carries the sums: each step's
`at`, every mark and `model.expectedDurationSeconds`.

**Both runtimes hold the sums exactly.** The document check recomputes the
exact sum of the written durations step by step and compares each `at`,
the length and every mark with it, with no tolerance; a document summed in
floats is refused naming the field. Node sums as Python does: `String()`
gives the same shortest digits as `repr`, the digits become a `BigInt`
scaled by a power of ten, and `Number()` of the exact decimal rounds it as
`float()` of the fraction does.

**Node reads what is written.** A step's end is the next step's `at`, and
the last step's the take's length; the pose rule, the step a mark follows,
`check`'s take line and the renderer's mark check read them, and a frame is
on a mark only when its take time is the mark exactly. Nothing adds two
take times in floats.

## Options considered

- **`decimal.Decimal`.** Exact for these sums too, but its arithmetic runs
  in a context whose precision (28 digits by default) rounds a long sum
  silently; a `Fraction` has no context.
- **`Fraction(float)`, the binary values summed exactly.** Still drifts:
  three of the doubles nearest 1.2, summed exactly, fall on a tie that
  rounds to even, `3.5999999999999996`. The author wrote `1.2`, not its
  double.
- **Durations on the frame grid, or frame counts.** Take time is declared
  in seconds and the frame rate belongs to the output; a duration off the
  grid stays legal, and which frame owns an instant stays the renderer's
  rule.
- **Keep the floats, widen or keep the tolerance.** The document and
  `check` would still carry the wrong marks, and the tolerance only ever
  matched instants the pose rule does not pose on the mark's bank.

## Consequences

- A take's marks are the numbers its author would compute by hand, in the
  document, in `check` and in the review records; a film may draw a step
  over any decimal of seconds.
- A hand-written take document summed in floats is refused; the shared
  invalid fixture `take-mark-summed-in-floats` holds both runtimes to it.
- The 1e-9 tolerance remains only where a reader adds a number of its own
  to a take time: the range check of a shot's model time written as a mark
  with a `plus`, which no Python declaration writes.
- `bankAt` takes the document, not its `take` block, since the last step's
  end is the take's length.
