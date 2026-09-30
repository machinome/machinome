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
