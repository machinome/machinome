# movie-document Specification

## Purpose

Let a project's declarations drive a film through a data document,
`machinome-movie/0.1`: narration in chapters of one take each, times anchored
to spoken phrases and marks and resolved from the cached takes, the sets the
film page draws, one schema and one set of fixtures shared with the Python
side. Created by the `movie-document` change (30 September 2026).

## Requirements
### Requirement: A movie document is a source the tool produces from

`check`, `speech`, `preview`, `render` and `build` SHALL accept a
`machinome-movie/0.1` JSON document wherever they accept a YAML episode, and
SHALL produce from it exactly as from an episode: the same validation of every
format 0.4 field, the same proofs, the same outputs. The document SHALL be
data: its relative paths resolve against its `root`, and the tool's outputs go
to `<root>/_build/`. A document in any other format MUST be refused, naming the
format, before anything else is read.

#### Scenario: The validation film from its document
- **WHEN** the author runs `check` on `videos/cut_and_advance/_build/movie.json`
  after `speech`
- **THEN** the document is checked against the export, the pinned revision, the
  source excerpts and the pictures as an episode is, and preview and render
  produce the film from it.

#### Scenario: A document of a later format
- **WHEN** a document says `"format": "machinome-movie/0.2"`
- **THEN** it is refused naming `machinome-movie/0.2` and the format this build
  reads, and nothing else is checked.

### Requirement: The document is checked against its schema first

The tool SHALL validate an unresolved document against
`schema/machinome-movie-0.1.json` before any other rule: field names, types,
required fields and closed field lists. A field the schema does not know, on
the document, a chapter, a shot, a key or a cue, MUST be refused naming the
field and where it is, so a misspelling or a field of a later build is never
silently dropped. Both runtimes validate against this one file.

#### Scenario: Narration written on a shot
- **WHEN** a shot of a document carries `narration`
- **THEN** it is refused naming `narration` and the shot's place in the
  document, because narration belongs to the chapter.

### Requirement: A chapter's narration is one take

A document SHALL group shots into chapters, each with its own narration,
optional speech offset (default 0.2 s) and optional direction. `speech` SHALL
generate one take per chapter from the narration alone, before anything in
the document is resolved, and place it at the chapter's start plus its speech
offset. The take MUST fit its chapter, ending at least 0.1 s before the
chapter's last shot does; a take that does not is refused after caching,
naming the chapter and its measurement. Captions SHALL follow the chapter's
recorded alignment. A spoken reveal or source emphasis in a shot SHALL read
its chapter's narration and take, at the instant the take starts relative to
that shot.

#### Scenario: A paragraph across a cut
- **WHEN** the `drive` chapter's narration spans the shots `wheel`, `coupling`
  and `stroke`
- **THEN** it is synthesized once, heard without a restart at either cut, and
  its captions follow the one take.

#### Scenario: Emphasis in a later shot of the chapter
- **WHEN** `coupling`, the second shot of `drive`, lights `waterwheel`,
  `drives` and `crankshaft` as they are spoken
- **THEN** each word lights at its measured onset in the chapter's take,
  counted from the shot's own start.

### Requirement: Cuts, keys and cues can be anchored to spoken words

Wherever a shot takes shot-local seconds (its `until`, a camera key's `at`, a
model keyframe's `at`, a cue's `from` and `to`, a typing cue's `from` and `to`,
a picture view key's `at`), the author SHALL be able to write a number or an
anchor: `spoken` (the instant the narrator begins a phrase: the onset of the
first letter or digit of its first word) or `spokenEnd` (the instant its last
character ends), each with an optional `plus` in seconds, positive or
negative. A number keeps its meaning (for `until`, the shot's duration). An
anchor SHALL resolve to the chapter's start plus its speech offset plus the
phrase's time in the cached take plus `plus`, snapped to the nearest frame of
the output rate; shots then run in order from zero, each starting where the
one before ended, and the film lasts until the last shot's end.

The phrase MUST occur exactly once in the chapter's written narration and its
spoken form (after `audio.replacements`) exactly once in the chapter's take;
otherwise the document is refused naming the chapter, the shot, the field and
the phrase. A shot whose `until` resolves at or before its start, and a cue or
key anchored before its shot's start or after its end, MUST be refused naming
the shot and the anchor.

#### Scenario: A cut on a spoken phrase
- **WHEN** `coupling` has `until: {"spoken": "A crank"}`
- **THEN** the cut to `stroke` falls on the output frame nearest the instant the
  narrator begins "A crank" in the cached take, and moves with it when the take
  is regenerated.

#### Scenario: A phrase the narration does not contain
- **WHEN** an anchor names "the saw" in a chapter whose narration never says it
- **THEN** the document is refused, naming the chapter, the shot, the field and
  "the saw", before any take is read.

#### Scenario: An ambiguous phrase
- **WHEN** an anchor names a phrase said twice in its chapter
- **THEN** the document is refused as ambiguous, naming the chapter, the shot,
  the field and the phrase.

#### Scenario: A cut before its own start
- **WHEN** a shot's `until` names a phrase spoken before the shot begins
- **THEN** the document is refused naming the shot and its `until`.

### Requirement: Model seconds can name a mark

A document SHALL be able to name instants of the machine in `marks`, and
wherever it takes model seconds (`simulation.from`, `simulation.to`, a model
keyframe's `seconds`) the author SHALL be able to write a number or a mark
with an optional `plus`, resolved to the mark's model seconds plus `plus`. An
unknown mark MUST be refused naming the shot and the mark.

#### Scenario: The pull settles on the return
- **WHEN** `pawls` keys `pull_start` at the cut, `return_start` with `out`
  easing at the spoken "On the return", and `cycle_end` at the shot's end
- **THEN** the model runs from 436 to 438 and eases into the hold on the words,
  and from 438 to 440 to the end.

#### Scenario: A misspelled mark
- **WHEN** a shot names mark `pull_stat`
- **THEN** it is refused naming the shot and `pull_stat`.

### Requirement: A shot is drawn in one of three sets

A shot SHALL name its `set`: `paper` (the model stage alone), `paper-split`
(source beside the model) or `source-only`, the three layouts the film page
draws. `paper-split` and `source-only` MUST have `code`, and `paper` MUST NOT;
a shot without `set` is `paper` without `code` and `paper-split` with it. Any
other set MUST be refused by name. `fadeIn` SHALL be accepted only on the
film's first shot and `fadeOut` only on its last, across chapters.

#### Scenario: The coupling beside its source
- **WHEN** `coupling` is `paper-split` with the pinned lines 413–415 typed
- **THEN** it is drawn as today's split: source left, model right.

#### Scenario: A set the page cannot draw
- **WHEN** a shot names the set `stage`
- **THEN** it is refused naming `stage`, the shot and its chapter.

### Requirement: What a document names is checked before any take

Before reading any take, the tool SHALL refuse, naming the shot, its chapter
and the name: a camera key whose preset the document does not declare; a
layer, highlighted part or annotated part that the export does not contain
or the document does not declare; and a model keyframe list whose last key is
not at the shot's `until`, written as the same number or the same anchor, so
that the keys end at the shot's end whatever the take.

#### Scenario: A misspelled preset
- **WHEN** a camera key names preset `faraway` and the document declares none
- **THEN** it is refused naming `faraway` and the shot, before `speech` is
  needed.

#### Scenario: A part the export does not have
- **WHEN** a highlight names the assembly path `Beam/Plonk`
- **THEN** it is refused naming `Beam/Plonk` and the shot.

### Requirement: Anchors are resolved only from cached takes

`check`, `preview` and `render` SHALL resolve spoken anchors from the takes
`speech` cached and MUST NOT generate or purchase speech. A document with
spoken anchors in a chapter whose take is not cached MUST be refused, naming
the chapter and asking for `speech` to be run first. Each of them SHALL write
the resolved document, every anchor a number, to
`<root>/_build/movie-resolved.json` before rendering anything.

#### Scenario: Checked before speech
- **WHEN** `check` runs on a new document with spoken anchors
- **THEN** it refuses naming the first chapter without a take and asking for
  the `speech` command, and nothing is requested from the provider.

#### Scenario: Inspecting the resolution
- **WHEN** `check` passes
- **THEN** `_build/movie-resolved.json` holds the chapters with their resolved
  starts, ends and offsets and every shot with numeric times, and resolving the
  same document against the same takes again writes the same file.

### Requirement: Both runtimes share the fixtures

The repository SHALL keep valid documents, their take doubles and their pinned
resolutions, and invalid documents with the words their refusal must contain,
under `fixtures/`, indexed so that a fixture is registered once. The Node
suite MUST load, validate and resolve every registered document against its
takes to exactly its pinned resolution, and refuse every invalid document with
every listed word, so a fixture the other runtime adds is tested here too.

#### Scenario: A fixture added by the Python side
- **WHEN** the Python side adds an invalid document to `fixtures/invalid/`
- **THEN** the Node suite refuses it and asserts its listed words, with no
  change to the Node tests.

