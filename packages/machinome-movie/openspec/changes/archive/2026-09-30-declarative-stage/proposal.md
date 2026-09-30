## Why

The validation film *Cut and Advance* (Leonardo project,
`videos/cut_and_advance/spec.md`, version 2) is to be produced from a Python
source in which the project's own template owns the whole screen: a root set
`Leonardo` and its split `LeonardoSplit` written in the project's
`stage.tsx`, a project element `Jobs` with a typed action, source shown
beside the model in three chapters with spoken concepts lighting the tokens
that name them, titles and a picture placed in the template's slots. The
pilot, inspecting version 1, found the source code left out and the film
page's hard-coded chrome unacceptable, and commissioned the React stage
(`workflow/ongoing/react-stage-campaign/plan.md`). The `machinome_movie`
package today evaluates to `machinome-movie/0.1`, which flattens sets, slots
and elements into the old film page's fields and refuses a project's set or
element by name, so the film's source cannot be written. The pilot ruled 0.1
a step, not a protocol: nothing of it is preserved.

This change is the Python side of the stage: the declarations evaluate to
`machinome-movie/0.2` (contract `docs/movie-document.md`, schema
`schema/machinome-movie-0.2.json`), the document that carries the
declarations' shape. The Node side, loading 0.2 and drawing it, is the
parallel `react-stage` change; the film is produced in the Leonardo
repository once both are merged.

## What Changes

- **BREAKING** Evaluation emits `machinome-movie/0.2`: a `stage` block
  (`modules`, `sets`, `elements`), chapters that declare their `elements`,
  shots with `set`, `places`, `until`, `model` and `cues` of `{at, until?,
  actions}`. Nothing of 0.1 is emitted or read; `check_document` checks 0.2
  against the 0.2 schema, and the 0.1 schema leaves the repository.
- A project declares its own **sets**: a `Set` subclass with `module` (its
  stage module, TypeScript or JavaScript, relative to the declaring file),
  `Slot()` declarations (a slot no longer says what it holds), plain class
  attributes as static props (JSON values only), a kind derived from the
  class name (`LeonardoSplit` is `leonardo-split`) unless `kind` is written.
  A derived set inherits the chrome, not the layout. Empty slots are allowed.
- A project declares its own **elements**: an `Element` subclass with
  `module` and `Action(param=type, …)` declarations; an instance's keyword
  arguments are its props; calling a declared action yields a cue's action,
  its parameters checked by name and type.
- The shipped sets are `Frame` (`stage`) and `Split` (`left`, `right`).
  **BREAKING** `Paper`, `PaperSplit` and `SourceOnly` leave the package (they
  remain in the stage runtime, for YAML episodes), and `Paper.style(...)`
  becomes `Style(...)`.
- The shipped **elements** are elements: `View` gains the marks `ring`,
  `label` and `arrow` beside `move` and `highlight` (**BREAKING** the
  free-standing `Ring`, `Label` and `Arrow` leave); `Source.panel` with
  `type` and `emphasize`, where a word is a token or a `(spoken, token)`
  pair on any line of the excerpt; `Title(text, subtitle=)` with
  `show(enter=, leave=, reveal=)`; `Picture(still, fit=)` with
  `show(enter=, leave=, view=)` (**BREAKING** the `Title` action and
  `still.show` leave).
- An element keeps its state across the shots of its chapter: a source panel
  completed in an earlier shot need not be typed again.
- Refusals by name for everything the contract refuses that Python can see
  before speech, including a token absent from or repeated in its excerpt,
  which makes evaluation read the source files an emphasis lights.
- Fixtures: the fixture project's movies rewritten on `Frame`, `Split`, a
  project set and a project element with a placeholder `stage.tsx`;
  `fixtures/documents/minimal.json` and `tour.json` as 0.2, their takes, and
  an invalid set naming every new refusal; the 0.1 documents `bare` and
  `two-chapters` and their takes deleted.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `declarative-movie`: the declarations gain project sets and elements,
  shipped elements with their actions, emphasis pairs, element state across
  a chapter, and evaluate to `machinome-movie/0.2`.

The `movie-document` capability (the Node side's loading) is changed by the
parallel `react-stage` change, not here.

## Impact

Changed: `python/machinome_movie/` (every module), `python/tests/`, the
fixture project under `python/tests/fixtures/project/`, `fixtures/documents/`,
`fixtures/invalid/`, `fixtures/manifest.json`, `fixtures/takes/`,
`fixtures/README.md` (the documents it describes are 0.2), the package's
schema link, `docs/declaring-a-movie.md`, `docs/architecture-overview.md`
("Movies declared in Python"), `python/README.md`, `AGENTS.md` (the Python
part of the status bullet), `CHANGELOG.md`, a new ADR-005, the index.
Removed: `schema/machinome-movie-0.1.json`. The Node suite reads the 0.1
schema and fixtures until the `react-stage` change replaces its loading; the
two changes land together on the campaign branch. No framework, viewer,
studio or project repository changes; the film's `movie.py` and `stage.tsx`
are written in the Leonardo repository by the campaign's film step.

## Non-goals

No Node, no `src/`, no `test/`, no stage runtime, no `fixtures/resolved/`
(the Node cycle pins those), no scenario takes, no page element. Spellings
the film does not use (a shot's or chapter's `direction`, `speechOffset`, a
clip, an arrow at a point, a ring's padding, a highlight colour, an even
reveal) stay out until an episode asks. No publication.
