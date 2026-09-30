# declarative-movie Specification

## Purpose
A project declares a movie of its model in Python, lists it in
`pyproject.toml`, and evaluates it once, purely, to the movie document the
renderer reads; mistakes are refused by name before speech is generated.
Created by the archived change `declarative-movie`.
## Requirements
### Requirement: A movie is declared in Python and listed in the project

An author SHALL declare a movie as a Python class tree in the project: a
`Movie` whose chapters are `Chapter` instances, each chapter owning one
`Narration`, the elements its shots place and its `Shot`s, found by type in
declaration order and named by the attribute that holds them. The project
SHALL list the movie in `pyproject.toml` under `[tool.machinome.movies]` as
`name = "module:Class"`, as it lists models, and the tool SHALL list and
evaluate the movies of a project from that table.

#### Scenario: List a project's movies
- **WHEN** the author runs `python -m machinome_movie list <project>`
- **THEN** every name in the project's `[tool.machinome.movies]` table is
  printed with its reference, in table order.

#### Scenario: Evaluate a movie by name
- **WHEN** the author runs `python -m machinome_movie evaluate <project> <movie>`
- **THEN** the movie's module is imported from the project and its document
  is written to `_build/movie.json` beside the module, with `root` `..`.

#### Scenario: Unknown movie name
- **WHEN** the name is not in the table
- **THEN** the command refuses, naming it and the movies the table declares.

### Requirement: A movie evaluates to one deterministic document

Evaluating a movie SHALL produce a `machinome-movie/0.1` document with the
fields of the contract page, written as canonical JSON. Evaluation MUST read
only the export's manifest and source revision (and, from the command line,
the project's `pyproject.toml`), MUST NOT read a clock, draw randomness,
reach the network or build CAD, and two evaluations of the same sources MUST
be byte-identical. Anchors SHALL stay symbolic: a phrase, the end of a
phrase, or a mark, with an optional offset; the tool evaluating the movie
never reads speech.

#### Scenario: Evaluate twice
- **WHEN** a movie is evaluated twice
- **THEN** both documents are identical byte for byte.

#### Scenario: Timing on a phrase
- **WHEN** a shot lasts until `lines.spoken("In the model")`
- **THEN** its `until` in the document is `{"spoken": "In the model"}`, and
  no seconds are written for it.

#### Scenario: The document is valid
- **WHEN** any movie evaluates
- **THEN** its document validates against `schema/machinome-movie-0.1.json`.

### Requirement: Parts are named by the model's declarations

A cue, a highlight or a layer SHALL name a part by the declaration path of
the model class (`Mill.feed.pawl`, `Mill.carriage`), never by a string. The
tool SHALL resolve it to the export's names and MUST refuse, at evaluation, a
path the export does not contain, naming the path as written and the export
path it resolved to.

#### Scenario: A path resolved to export names
- **WHEN** a ring is drawn around `LeonardoHydraulicSawmill.feed.pawl`
- **THEN** the document names the part `["Feed mechanism", "Driving pawl"]`.

#### Scenario: A stale export
- **WHEN** the model declares a part the export lacks
- **THEN** evaluation refuses, naming the declaration path.

### Requirement: Mistakes are refused by name before speech

The tool MUST refuse, naming the chapter or movie, the shot and the thing at
fault, at class creation where every class involved is known and at
evaluation otherwise: a slot the shot's set does not have, a slot filled
twice or left empty, an element the chapter does not declare, a phrase absent
from or repeated in the chapter's narration, an unknown mark, model keys that
do not start at the shot's start and end at its end, a camera not declared on
the view's take, a project-defined set or element (the stage that would draw
it does not exist yet), and an emphasis cue whose anchor is not a spoken
phrase.

#### Scenario: A misspelled phrase
- **WHEN** a shot lasts until `lines.spoken("Buut")` and the narration says "But"
- **THEN** the chapter's class is refused, naming the chapter, the shot,
  `until` and `Buut`.

#### Scenario: A camera of another take
- **WHEN** a view on one loop moves to a camera declared on another
- **THEN** the chapter is refused, naming the shot and the camera.

#### Scenario: A project set
- **WHEN** a project declares its own `Set` subclass
- **THEN** it is refused at class creation, naming the class and saying the
  stage does not exist yet.

### Requirement: The shared fixtures pin the document

Every document registered in `fixtures/manifest.json` SHALL equal the
evaluation of the fixture movie of the same name, and every invalid fixture
that Python can refuse before speech SHALL be refused with a message
containing each of its `must_mention` substrings.

#### Scenario: A fixture document drifts
- **WHEN** a fixture movie's evaluation differs from its registered document
- **THEN** the Python suite fails, naming the fixture.

