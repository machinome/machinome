# ADR-001: The movie document and chapter narration

Status: Accepted (OpenSpec change `movie-document`, proposed and archived 30 September 2026;
ratified by the campaign orchestrator's review; integration is the pilot's)

## Context

A Videomaker source was a YAML episode: shots with numeric times, each
carrying its own narration, synthesized as one take per shot. The
declarative-python campaign produces the validation film *Cut and Advance*
(Leonardo project, `videos/cut_and_advance/spec.md`) from Python
declarations, which evaluate to a JSON document, `machinome-movie/0.1`
(`docs/movie-document.md`). The film needs a paragraph of narration to span
several shots without a restart at each cut, cuts and cues placed on spoken
phrases rather than on numbers copied from a take, and model instants named
by marks.

## Decision

1. The tool accepts a movie document (`.json`) wherever it accepts an episode
   (`.yaml`). Both load into one internal episode: the format 0.4 shape with a
   `chapters` field. Nothing after loading (`frameAt`, preview, render, the
   shot cache, review packs) distinguishes them.
2. Narration belongs to a chapter, an ordered run of shots. One take is
   generated per chapter, placed at the chapter's start plus its speech
   offset, and must fit the chapter. A YAML episode is a movie whose every
   shot is a chapter, so its take keys, captions and frames are unchanged.
3. Times in a document may be anchored to the chapter's narration (`spoken`,
   `spokenEnd`, with `plus`) and model seconds to named marks. Anchors are
   resolved after `speech` from the cached take, snapped to the output frame
   grid, and the resolution is written to `<root>/_build/movie-resolved.json`.
   `check`, `preview` and `render` never generate speech.
4. The unresolved document has one JSON Schema,
   `schema/machinome-movie-0.1.json`, which both runtimes validate against
   before any semantic rule, and one set of shared fixtures.
5. Everything that can be refused without a take is refused before `speech`
   is needed: phrases in the written narration, marks, sets, fades, camera
   presets, the last model keyframe at the shot's `until`, and the parts
   named against the export.

## Options considered

- **Extend the YAML format with chapters and anchors** (a 0.5 draft). Rejected:
  the campaign's settled direction (`workflow/ongoing/declarative-python-api.md`)
  is declarations in the project that evaluate to data; a second authored
  format with the same features would double the contract.
- **Resolve anchors in the Python evaluation.** Rejected: the take is produced
  by `speech`, after evaluation; evaluation would have to call the provider or
  read Videomaker's cache, and a regenerated take would require re-evaluating.
  Resolution belongs where the take is read.
- **Keep one take per shot, cut takes at shot boundaries.** Rejected: a
  restart at every cut is what the film asks to remove.
- **Chapters embed their shots in the internal episode.** Rejected: the render
  manifest records the episode whole; chapters name their shots by id so each
  shot is held once and `frameAt` keeps its flat `shots` list.

## Consequences

- A document's film length follows its takes: regenerating speech moves cuts
  and cues with the words, and `check` refuses until the takes are cached.
- A resolved end lies on the output frame grid, so its duration is a whole
  number of frames at the document's rate, but not necessarily at another
  rate; a quick render at a lower rate may be refused (design Open Questions).
- YAML episodes keep their exact frames, take keys and captions; the Leonardo
  project's cached takes remain valid.
- The schema is validated in Node by a small validator of the keywords it uses
  (`src/schema.mjs`), not a dependency; a test keeps the two in step.

## Amendment (30 September 2026)

The pilot ruled, the day this ADR was accepted, that `machinome-movie/0.1`
is a step of the declarative-python campaign and not a protocol. The
document flattens the declarations' sets, slots and elements into the
renderer's present fields because the React stage does not exist yet. When
the stage arrives the document will carry the declarations' shape, this
shape will not be preserved, and no compatibility with it is owed or
maintained. No format becomes a protocol before the pilot makes a release.
The decision above stands for this step; its consequences do not extend
past it.

## Amendment (30 September 2026, `react-stage`)

Decision 1 is replaced by [ADR-006](ADR-006-yaml-episodes-and-movie-documents-load-into-one-resolved-document.md):
both sources load into the resolved movie document, not into the YAML format
0.4 shape. Chapters, anchors, one take per chapter, the schema and the shared
fixtures stand, for `machinome-movie/0.2`.

## Amended 30 September 2026: the narration's end is an anchor

(OpenSpec change `narration-end-anchor`, fix-warts campaign; warts 2 and 7
of *Cut and Advance*.) Decision 3 gains a third form of a narration anchor,
`{"narrationEnd": true}` with an optional `plus`, accepted wherever
`spokenEnd` is. It resolves to the chapter's start plus its speech offset
plus the end of the last letter or digit of the chapter's cached take plus
`plus`, snapped to the frame grid, and needs the take as the other forms do.
The declarations' `lines.end()` evaluates to it, where it used to evaluate to
`spokenEnd` of the shortest unique run of the narration's last words, a
phrase the author never wrote, which grew when the last words repeated
earlier ones.

The instant is the last *letter or digit*, not the last character, the
mirror of `spoken`'s first letter or digit: closing punctuation has its own
time in an alignment and no sound, and waiting for it would have moved every
existing end-of-narration cut one or two frames later (measured in the
change's evidence). The orchestrator's ruling named the last character; the
change keeps the ruling's stated invariant, that the tail's end and the
narration's end are one instant, and records the departure for review.
The orchestrator accepted it at the merge into `fix-warts` (30 September
2026): the last letter or digit is the instant.

A consequence stated in the original Consequences is now shown to the
author: a document's length follows its takes, and `check` prints each
chapter's take, resolved length and tail.
