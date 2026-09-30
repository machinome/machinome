## Context

`machinome-movie/0.2` has two anchor forms of a chapter's narration:
`{"spoken": phrase}`, the onset of the first letter or digit of the phrase's
first word, and `{"spokenEnd": phrase}`, the end of the phrase's last
character; either takes `plus`. The Python declarations offer three:
`lines.spoken(phrase)`, `lines.spoken_end(phrase)` and `lines.end()`. The
third has no form of its own: `Narration.end()` evaluates to
`{"spokenEnd": tail}`, where `Narration.tail()` finds the shortest run of the
narration's last words that occurs once, edge punctuation stripped. The
Node side resolves anchors in `resolveMovie` (`src/movie.mjs`) against the
chapter's cached take, whose alignment spells the spoken narration (after
`audio.replacements`) one code point per character with a start and an end
time each.

*Cut and Advance* ends four of its five chapters on `lines.end(plus=…)`
(wart 2) and resolved to 59 s from a 100-second shot list (wart 7). The
orchestrator ruled the contract on 30 September 2026: a third anchor form
`{"narrationEnd": true}` with an optional `plus`, accepted wherever
`spokenEnd` is, resolving to the chapter start plus `speechOffset` plus the
end of the take plus `plus`, snapped to the frame grid, needing a cached take
like the others, refused by the schema when its value is not `true` or when
it carries another field, naming `narrationEnd`; and `check` reporting each
chapter's take, length and tail.

## Goals / Non-Goals

Goals: the document says "the end of the narration" when the author wrote
it; the film's frames do not move (the fixture pins stay byte-identical);
the author sees, per chapter, where the length of the film comes from.
Non-goals: those of the proposal.

## Decisions

### D1. The form is `{"narrationEnd": true}`, with an optional `plus`

As ruled. A distinct key, beside `spoken` and `spokenEnd`, so the three forms
are told apart by their one required field, and a reader of the document
sees what the author meant. Its value is the constant `true`: the form names
no phrase, and a key with no value is not JSON.

Alternatives rejected: `{"spokenEnd": null}` (overloads a form whose value is
a phrase, and every consumer would have to special-case `null`); keeping the
tail and documenting it (the finding is that the document says a phrase the
author never wrote, and that it grows on a repeated ending); resolving the
tail on the Node side (the same phrase search, moved, with the same
fragility).

### D2. The instant is the end of the take's last spoken letter or digit

The ruling says "the end of the last character of the chapter's cached take"
and, in the same breath, that the resolved pins must not move "since the
tail's end and the narration's end are the same instant". Both cannot hold:
every fixture narration ends in punctuation ("A seesaw.", "…tip it?",
"…one end down.", "…the model."), a take's alignment gives that punctuation
its own character time (0.06 s in the fixture doubles), and the tail, edge
punctuation stripped, ends on the last letter. Resolving to the last
character's end moves every `lines.end()` cut 0.06 s later; at 30 fps the
snapped instant moves one or two frames and both pins change (measured in
`evidence.md`).

The instant is therefore **the end of the last letter or digit of the
chapter's take**: the mirror of `spoken`, which begins at the onset of the
first letter or digit of its phrase, so a narration's first and last spoken
sounds are measured the same way. For every narration whose last word ends
in a letter or a digit it is exactly the instant the tail resolved to (the
tail ends on its last word character, and a phrase's end is its last
character's end), so every existing film, *Cut and Advance* included, keeps
its frames. Punctuation carries no sound of its own; its time
in an alignment is the provider's bookkeeping, not the voice.

This is a refinement of the ruling's wording made to keep its stated
invariant, recorded here and in the report for the orchestrator to overturn:
the literal reading is a one-line change in `resolveMovie` and a re-pin.

A take whose alignment holds no letter or digit is refused at resolution,
naming the chapter, the shot, the field and `narrationEnd`.

### D3. Where it is accepted, and what it needs

- The schema's `time` gains a fourth branch, `narrationEnd`, titled
  `narrationEnd anchor`: `narrationEnd` with `enum: [true]`, `plus` a number,
  no other field. Every place that takes a `time` accepts it; model seconds do
  not (they take marks).
- The static checks (both runtimes) look for a phrase in the written
  narration only for `spoken` and `spokenEnd`; `narrationEnd` has none to
  check. An `emphasize` cue still needs `spoken` without `plus`, so a
  `narrationEnd` there is refused as any other non-`spoken` anchor is.
- A chapter with a `narrationEnd` anchor needs its take, as a chapter with any
  anchor does, and is refused without one by the existing refusal naming the
  chapter and the `speech` command.
- A model key list whose last key is at the shot's `until` compares the two as
  written, so `{"narrationEnd": true, "plus": 0.8}` on both is equal, as for
  the other forms.
- `describeAnchor` prints it as `narrationEnd`, with `plus N` when it has one,
  so a refusal reads `until narrationEnd plus 0.8 resolves at …`.

### D4. The schema refusal names the field at fault

`{"narrationEnd": false}` fails every branch of `time`. The Node validator
today reports a failed titled `oneOf` as "must be one of: seconds, spoken
anchor, spokenEnd anchor, narrationEnd anchor", which names `narrationEnd`
only because it lists every form. Python's `jsonschema` `best_match` already
descends into the branch that got furthest and says
`field until.narrationEnd: False is not one of [True]`.

The Node validator does the same, by one rule: when every branch of a `oneOf`
fails, the value is an object, and exactly one **titled** branch has all its
required fields present in it, the refusal is that branch's own error, with
`(read as a <title>)` after it. `{"narrationEnd": false}` is then refused at
`field until.narrationEnd` naming `narrationEnd anchor`, and
`{"narrationEnd": true, "phrase": "it"}` as an unknown `phrase` at `until`,
read as a `narrationEnd anchor`. Untitled branches (the shipped actions,
the model's two shapes, a part) are untouched, so no other refusal of those
changes; a malformed `spoken`, `spokenEnd` or `mark` anchor is now refused by
its own field too, which only sharpens a refusal's words (recorded as a
consequence in `evidence.md`).

The shared invalid fixture is `{"narrationEnd": false}` on the tour's
`question` `until`, and must mention `shot question` and
`until.narrationEnd`, which both runtimes print.

Alternative rejected: a semantic refusal after the schema. The schema is the
one place both runtimes read the closed field lists, and a second check would
be a second statement of the form.

### D5. Python: `Narration.end(plus=0)` emits the form; the tail goes

`Anchor('end', None, plus, narration).document()` returns
`{"narrationEnd": True}` and `plus` when non-zero, like the others.
`Anchor.check` refuses only an anchor of another chapter's narration for this
kind; a narration always has an end. `Narration.tail()` has no other caller
and is removed. `lines.end()` keeps its name, its `plus=` and its written
form `lines.end(plus=…)` in refusals.

### D6. `check` reports each chapter's take and tail

After the summary line `<title>: N chapters, M shots, Ss; model …s`, `check`
prints, for every chapter in order, a line indented by two spaces:

    <id>: take <take> s, chapter <length> s, tail <tail> s

where `take` is the cached take's measured duration (the `duration` of its
speech record, the length of the audio file), `length` the chapter's resolved
end minus its start, and `tail` the length minus the chapter's speech offset
minus the take, each with two decimals. A chapter with no cached take (a
chapter no anchor needs a take for, whose speech was never generated) prints
`<id>: no cached take, chapter <length> s`. The line is computed by a pure
function, `chapterTakeLines(film, takes)` in `src/chapters.mjs`, from the
loaded film and the cached records `check` reads with `cachedTake`, which
never generates speech. It is printed for a YAML episode too: its chapters are
its shots, and the same code reads them. The pipeline test that runs `check`
on the tour pins the three lines' words and the fixture's numbers.

A negative tail is printed as it is: the take overruns its chapter, which
`speech` refuses; `check` only reports.

### D7. The manual says the narrator sets the length

`docs/declaring-a-movie.md`, where it explains anchors, gains one paragraph:
with every cut on a phrase, a film is as long as its takes and their tails,
so an author estimates by speaking the narration, not by counting shots, and
reads `check`'s per-chapter line. Its description of `lines.end()` says the
document writes `{"narrationEnd": true}`. `README.md`'s description of
`check` names the per-chapter line. A repository pin (pytest, layer 9)
asserts both sentences are on the page.

## Risks / Trade-offs

- [D2 departs from the ruling's wording] → recorded above and in the report;
  reversing it is one line and a re-pin, and the measurement is in
  `evidence.md`.
- [A take whose last letter's end is followed by a long silence] → the anchor
  names the voice's end, not the file's; the file's length is what `check`
  reports as the take, so the tail line shows the difference.
- [The sharper `oneOf` refusal changes the words of malformed `spoken`,
  `spokenEnd` and `mark` anchors] → no invalid fixture pins those words
  (the suite proves it), and each new message names the field at fault.

## Migration Plan

A document evaluated before this change keeps its `spokenEnd` tails and
resolves as before; re-evaluating it writes `narrationEnd` and resolves to
the same frames. *Cut and Advance* needs only a re-evaluation. No format
version changes: 0.2 is a step, not a protocol.

## Open Questions

- Whether the orchestrator keeps D2 or rules the literal last character.
