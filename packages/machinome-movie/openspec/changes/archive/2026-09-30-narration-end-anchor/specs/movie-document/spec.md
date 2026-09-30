## MODIFIED Requirements

### Requirement: Cuts, keys and cues can be anchored to spoken words

Wherever a shot takes a time (its `until`, a cue's `at` and `until`, a
`move`'s `until`, a model key's `at`, a picture view key's `at`), the author
SHALL be able to write a number or an anchor: `spoken` (the instant the
narrator begins a phrase: the onset of the first letter or digit of its first
word), `spokenEnd` (the instant its last character ends) or
`{"narrationEnd": true}` (the instant the chapter's narration ends: the end
of the last letter or digit of the chapter's take), each with an optional
`plus` in seconds, positive or negative. A number is shot-local seconds (for
`until`, the shot's duration). An anchor SHALL resolve to the chapter's start
plus its speech offset plus the phrase's time, or the narration's end, in the
cached take plus `plus`, snapped to the nearest frame of the output rate;
shots then run in order from zero, each starting where the one before ended,
and the film lasts until the last shot's end.

The phrase MUST occur exactly once in the chapter's written narration and its
spoken form (after `audio.replacements`) exactly once in the chapter's take;
otherwise the document is refused naming the chapter, the shot, the field by
its path in the shot (`until`, `cues[1].at`, `cues[0].actions[0].until`,
`model.keys[2].at`, `cues[3].actions[0].view[1].at`) and the phrase. A
`narrationEnd` anchor whose value is not `true`, or which carries a field
other than `plus`, MUST be refused naming the chapter, the shot, the field's
path and `narrationEnd`; one whose chapter's take holds no letter or digit
MUST be refused naming the chapter, the shot, the field and `narrationEnd`. A
shot whose `until` resolves at or before its start, a cue or key anchored
before its shot's start or after its end, a spanning action whose `until` is
at or before its `at`, and a `move` whose `until` is at or before its `at`
MUST be refused naming the shot and the anchor.

#### Scenario: A cut on a spoken phrase
- **WHEN** `coupling` has `until: {"spoken": "A crank"}`
- **THEN** the cut to `stroke` falls on the output frame nearest the instant
  the narrator begins "A crank" in the cached take, and moves with it when the
  take is regenerated.

#### Scenario: A highlight from one word to another
- **WHEN** a cue of `coupling` is `at: {"spoken": "waterwheel"}` and
  `until: {"spoken": "crankshaft"}` and highlights the waterwheel on `mill`
- **THEN** the highlight begins on the frame nearest the onset of
  "waterwheel" and is gone from the frame nearest the onset of "crankshaft".

#### Scenario: A cut after the narration ends
- **WHEN** the last shot of `drive` has `until: {"narrationEnd": true,
  "plus": 0.9}` and the chapter's narration ends "…turns the crankshaft."
- **THEN** the chapter ends on the output frame nearest 0.9 s after the end
  of the final "t" of "crankshaft" in the cached take, the same frame
  `{"spokenEnd": "crankshaft", "plus": 0.9}` would give, and moves with it
  when the take is regenerated.

#### Scenario: A narration end that is not true
- **WHEN** a shot's `until` is `{"narrationEnd": false}`
- **THEN** the document is refused by its schema, naming the chapter, the
  shot and `until.narrationEnd`, before any take is read.

#### Scenario: A phrase the narration does not contain
- **WHEN** an anchor names "the saw" in a chapter whose narration never says
  it
- **THEN** the document is refused, naming the chapter, the shot, the field
  and "the saw", before any take is read.

#### Scenario: An ambiguous phrase
- **WHEN** an anchor names a phrase said twice in its chapter
- **THEN** the document is refused as ambiguous, naming the chapter, the
  shot, the field and the phrase.

#### Scenario: A cut before its own start
- **WHEN** a shot's `until` names a phrase spoken before the shot begins
- **THEN** the document is refused naming the shot and its `until`.

## ADDED Requirements

### Requirement: `check` reports each chapter's take and tail

With every cut on a phrase, a film is as long as its takes and their tails.
After its summary line, `check` SHALL print one line per chapter, in order:
the chapter's id, its cached take's measured length, the chapter's resolved
length and its tail (the chapter's length minus its speech offset minus the
take), in seconds; a chapter whose take is not cached SHALL be reported as
having none, with its length. `check` MUST NOT generate or purchase speech to
report a take.

#### Scenario: Reading where a film's length comes from
- **WHEN** `check` passes on a movie whose chapter `drive` has a 5.68 s take,
  a speech offset of 0.2 s and resolves to 7.20 s
- **THEN** it prints `drive: take 5.68 s, chapter 7.20 s, tail 1.32 s`.

#### Scenario: A chapter without a take
- **WHEN** `check` passes on a source with a chapter whose times are all
  numbers and whose speech was never generated
- **THEN** its line says it has no cached take and gives its length, and no
  speech is requested.
