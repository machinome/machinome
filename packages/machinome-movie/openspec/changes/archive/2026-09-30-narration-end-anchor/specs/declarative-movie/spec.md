## MODIFIED Requirements

### Requirement: A movie evaluates to one deterministic document

Evaluating a movie SHALL produce a `machinome-movie/0.2` document with the
fields of the contract page, written as canonical JSON: a `stage` block
listing the stage modules, every set kind a shot uses (with the project sets
they derive from) and every project element kind a chapter declares;
chapters declaring their elements; shots naming their set, their placements,
their end, their model time and their cues of actions. Evaluation MUST open
only the export's manifest and source revision and the source files of the
excerpts an emphasis lights (and, from the command line, the project's
`pyproject.toml`), MUST NOT read a clock, draw randomness, reach the network
or build CAD, and two evaluations of the same sources MUST be byte-identical.
Anchors SHALL stay symbolic: a phrase, the end of a phrase, the end of the
narration, or a mark, with an optional offset; the tool evaluating the movie
never reads speech. `lines.end()` SHALL evaluate to `{"narrationEnd": true}`,
with its `plus` when one is given, and never to a phrase the author did not
write. Nothing of `machinome-movie/0.1` is emitted.

#### Scenario: Evaluate twice
- **WHEN** a movie is evaluated twice
- **THEN** both documents are identical byte for byte.

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
