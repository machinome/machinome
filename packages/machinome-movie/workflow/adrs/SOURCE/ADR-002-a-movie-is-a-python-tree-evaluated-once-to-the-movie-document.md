# ADR-002: A movie is a Python tree evaluated once to the movie document

Status: Proposed (OpenSpec change `declarative-movie`, 30 September 2026)

Numbered 002 to leave 001 to the parallel `movie-document` change, whose
decision is the document itself; a merge that reorders them renumbers.

## Context

Every Leonardo episode was a YAML screenplay whose timing was hand
arithmetic and whose speech measurements were hand-copied into cues; every
real film grew a script beside its YAML (`workflow/ongoing/declarative-python-api.md`,
"Where it comes from"). On 30 September 2026 the pilot settled that a movie
is a declarative Python tree in the project, declared in `pyproject.toml`
like a model, and that it evaluates to a data document, the movie document
(`docs/movie-document.md`), which is the only thing the renderer reads. The
validation film *Cut and Advance* specifies its source in that shape.

## Decision

A project declares a movie with the classes of the `machinome_movie`
package, in the framework's declarative manner: a class body declares; a
chapter finds its narration, elements and shots by type in declaration
order; a movie finds its chapters the same way; the attribute holding a
declaration is its name. Parts are the model class's own declaration paths,
resolved against the export. Mistakes are refused by name when the class is
created, or at evaluation for what needs the export.

Evaluation is a pure function of the declarations, the export's manifest and
its source revision, run once, to canonical JSON. Anchors stay symbolic
(phrases, phrase ends, marks); resolving them against speech is the
renderer's. The document is the boundary: nothing the renderer does reaches
back into Python, and Python emits no markup.

## Options considered

- **YAML with derived timing and anchors.** Fixes the timing findings, not
  the scripts beside the YAML or the fixed layouts.
- **A hermetic configuration language (Starlark, Jsonnet).** Pure by
  construction but a third language between the Python scenario and the
  stage, unable to import a model's declarations, so parts would be strings
  again.
- **Python evaluated at every frame by the renderer.** Loses validation
  before a browser opens, the shot cache's content key and the provenance
  hash, all of which rest on a data document.

## Consequences

- A movie can name parts, cameras and marks by reference, so a misspelling
  fails at the line that makes it rather than in a render.
- Reproducibility comes from hashing the document, as it does from hashing
  an export, not from forbidding code in the source.
- The document carries one model; takes from running or clocked scenarios,
  project-defined sets and elements, and the React stage are later
  decisions. A project's set or element is refused until the stage exists.
- The Python package and the Node renderer share one schema and one set of
  fixtures, so each side's suite fails when they drift.
