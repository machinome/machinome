## Why

The validation film of the declarative-python campaign, *Cut and Advance*
(Leonardo project, `videos/cut_and_advance/spec.md`), is specified to be
produced from a Python source and nothing else: no YAML, no hand-copied
decimals. Its "The Python source" section is written against an API that
does not exist. Every real Leonardo episode so far found the same four
problems the direction note records (`workflow/ongoing/declarative-python-api.md`,
"Where it comes from"): timing is hand arithmetic, speech measurements are
hand-copied into cues, every film grew code beside its YAML, and every new
look is a format change. The pilot settled on 30 September 2026 that a movie
is a Python tree in the project, declared in `pyproject.toml` like a model,
evaluated once to a data document; the document is the contract with the
renderer (`docs/movie-document.md`).

This change is the Python half of that contract: the declarations the film's
source is written in, and their evaluation to a `machinome-movie/0.1`
document. The Node half, loading and resolving the document, is the parallel
`movie-document` change. The film itself is produced in the Leonardo
repository once both halves are merged.

## What Changes

- A new Python package, `machinome-movie` (import `machinome_movie`), under
  `python/`, version 0.0.0, licence unselected like the rest of the
  repository, depending on `machinome`.
- Declarations with the spellings of the film's draft source: `Movie`,
  `Chapter`, `Shot`, `Narration`, `Cue`, the take `Loop` with `Camera`,
  `Layer`, `Source` and `Still`, the elements `View` and `Source.panel`, the
  actions `move`, `highlight`, `type`, `emphasize`, `show`, `Title`, `Label`,
  `Arrow`, `Ring`, `Reveal`, the sets `Paper`, `PaperSplit`, `SourceOnly`,
  the joins `Dissolve`, `Fade`, `Wipe`, `Slide`, `FadeIn`, `FadeOut`, and
  `Format`, `Narrator`, `Credits`, `Release`, `Evidence`, `Paper.style`.
- A declarative tree in machinome's manner: a class body declares; a chapter
  finds its narration, elements and shots by type in declaration order; a
  movie finds its chapters the same way; an attribute's name is the
  declaration's name. Parts are named by declaration paths of the model class
  (`Mill.feed.pawl`) and resolved to the export's names.
- Refusals by name at class creation, and at evaluation for what needs the
  export: unknown slot, slot filled twice, an element the chapter does not
  declare, an absent or repeated phrase, an unknown mark, model keys without
  the shot's start and end, a camera not declared on the take, a part path
  the export lacks, a project-defined set or element.
- Pure evaluation to canonical JSON: the export manifest, its
  `source-revision.txt` and the project's `pyproject.toml` are the only files
  read; no clock, randomness or network; two evaluations are byte-identical.
  Anchors stay symbolic.
- `[tool.machinome.movies]` in the project's `pyproject.toml`, and a command
  line: `python -m machinome_movie evaluate <project> <movie> [--out FILE]`
  and `python -m machinome_movie list <project>`.
- The document's JSON Schema `schema/machinome-movie-0.1.json`, written here
  because the Node side has not yet written it in this worktree, and a Python
  check of a document (schema and the refusals Python can make before
  speech) that evaluation applies to its own output and the shared invalid
  fixtures exercise.
- A fixture project and two fixture movies registered in `fixtures/`.
- The first pytest suite: layers 1, 2 and 9 of the testing policy.

## Capabilities

### New Capabilities

- `declarative-movie`: a project declares a movie in Python and evaluates it
  to the movie document.

### Modified Capabilities

None. The YAML formats and every existing command are unchanged; nothing in
`src/` changes.

## Impact

New: `python/` (package, tests, fixture project), `schema/`, the fixture
documents under `fixtures/`, `docs/declaring-a-movie.md`, ADR-002,
`CHANGELOG.md`. Changed: `README.md` (a pointer), `docs/architecture-overview.md`
(the Python side), `docs/adrs/README.md` (the index), `fixtures/README.md`
(where the Python fixture movies live). The workspace venv gains an editable
install of `python/`. No framework, viewer, studio or project repository
changes; the film's `movie.py` is written in the Leonardo repository by the
campaign's cycle C.

## Non-goals

The React stage and any project-defined set or element (refused, by name);
takes from running or clocked scenarios; resolving anchors to seconds, which
is the renderer's; speech; pronunciation replacements, clips, custom
highlight colours, even word reveals and shot or chapter directions, which
the film does not use. No publication.
