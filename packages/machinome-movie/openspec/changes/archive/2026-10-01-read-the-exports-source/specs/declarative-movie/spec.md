## MODIFIED Requirements

### Requirement: A movie evaluates to one deterministic document

Evaluating a movie SHALL produce a `machinome-movie/0.2` document with the
fields of the contract page, written as canonical JSON: a `stage` block
listing the stage modules, every set kind a shot uses (with the project sets
they derive from) and every project element kind a chapter declares;
chapters declaring their elements; shots naming their set, their placements,
their end, their model time and their cues of actions. Evaluation MUST open
only the export's manifest and the source files of the excerpts an emphasis
lights (and, from the command line, the project's `pyproject.toml`); a
movie that films a clocked take SHALL in addition run the framework's
simulation of the declared model once, which reads only the model's own
project files. The document's `model.sourceRevision` SHALL be the export
manifest's `source.revision`, the revision the framework recorded when it
exported the model; an export whose manifest has no `source` MUST be
refused, naming the manifest, `source.revision` and that the model must be
exported again from the project's Git repository with a commit, and no
other file beside the manifest is read for it. Evaluation MUST NOT read a
clock, draw randomness, reach the network or build CAD, and two evaluations
of the same sources MUST be byte-identical. Anchors SHALL stay symbolic: a
phrase, the end of a phrase, the end of the narration, or a mark, with an
optional offset; the tool evaluating the movie never reads speech.
`lines.end()` SHALL evaluate to `{"narrationEnd": true}`, with its `plus`
when one is given, and never to a phrase the author did not write. Nothing
of `machinome-movie/0.1` is emitted.

#### Scenario: Evaluate twice
- **WHEN** a movie is evaluated twice
- **THEN** both documents are identical byte for byte.

#### Scenario: Evaluate a clocked take twice
- **WHEN** the fixture movie `count`, which films the counter's take
  `Turns`, is evaluated twice
- **THEN** both documents are identical byte for byte, and neither
  evaluation read a clock, drew randomness, reached the network or made a
  CAD workplane.

#### Scenario: Timing on a phrase
- **WHEN** a shot lasts until `lines.spoken("In the model")`
- **THEN** its `until` in the document is `{"spoken": "In the model"}`, and
  no seconds are written for it.

#### Scenario: Timing on the end of the narration
- **WHEN** a shot lasts until `lines.end(plus=0.9)` in a chapter whose
  narration ends "Up. Down. Up."
- **THEN** its `until` in the document is `{"narrationEnd": true, "plus":
  0.9}`, and no phrase of the narration is written for it.

#### Scenario: The document is valid
- **WHEN** any movie evaluates
- **THEN** its document validates against `schema/machinome-movie-0.2.json`.

#### Scenario: The stage block lists what the movie uses
- **WHEN** a movie's shots use the project set `LeonardoSplit`, derived from
  `Leonardo`, and the shipped `Frame`, and a chapter declares a `Jobs`
  element, all drawn by `stage.tsx` beside the movie
- **THEN** `stage.modules` is `["stage.tsx"]`, `stage.sets` holds
  `leonardo-split` with `base` `leonardo`, `leonardo` itself and `frame`
  with its slots only, and `stage.elements` holds `jobs` with its props'
  kinds and its actions' parameter kinds.

#### Scenario: The revision comes from the manifest
- **WHEN** the fixture movie `tour` is evaluated from the seesaw's export,
  whose manifest records `source.revision`
- **THEN** the document's `model.sourceRevision` is that revision, and the
  files evaluation opened are the manifest and the emphasised excerpt.

#### Scenario: An export without a source
- **WHEN** a movie is evaluated from an export whose manifest has no
  `source`
- **THEN** evaluation refuses, naming the movie, the manifest and
  `source.revision`, and saying to export the model again.
