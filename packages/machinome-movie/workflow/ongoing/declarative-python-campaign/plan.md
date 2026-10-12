# Declarative Python campaign — plan

Status: working plan, 30 September 2026, opened on branch
`declarative-python` (worktree `WTs/declarative-python`) from `main` afbdfe7.
The pilot commissioned it in these words: implement the declarative Python
API through orchestrated OpenSpec cycles, after writing a validation video
spec around the Leonardo sawmill, and end with that video rendered from
Python source to inspect. Nothing here is ratified; each cycle ratifies its
own change. Integration of `declarative-python` into `main` is the pilot's.

## The cut

The direction note describes six steps. This campaign takes the two that
produce a film from Python on today's renderer and leaves the rest:

- **In:** the movie document as the input contract (`docs/movie-document.md`);
  chapters with one continuous narration take each; anchors on phrases and
  marks resolved after speech; the Python declarations that evaluate to the
  document; the validation film.
- **Out:** the React stage (sets are the three layouts the film page has),
  takes recorded from running or clocked scenarios (the posed loop with
  author-declared marks is the only take), the browser page element, the
  studio preview, several formats, sound design.

## Steps, not protocols

The pilot's ruling of 30 September 2026: the movie document of this campaign
(`machinome-movie/0.1`) is a step, not a protocol. The Python declarations
carry sets, slots and elements; evaluation flattens them into the renderer's
present fields because the React stage does not exist yet. When the stage
arrives, the document will carry the declarations' shape and this one will
not be preserved; no compatibility with it is owed or maintained. The full
scope ships in one release, and no format becomes a protocol before the
pilot makes that release. A deferral in this plan is the orchestrator's cut
of the work, never a choice of the pilot's.

## The empirical validation

`projects/Leonardo/videos/cut-and-advance/spec.md`: a film of about 100
seconds in five chapters, whose Python source is the acceptance target of the
`declarative-movie` change. Its shot list names which capability each shot
validates.

## Cycles

| # | change | repository side | worktree | depends on |
|---|---|---|---|---|
| A | `movie-document` | Node: load `machinome-movie/0.1`, chapters, anchors, schema, resolved output, fixtures | `WTs/movie-document` | the contract page |
| B | `declarative-movie` | Python: `machinome_movie` package under `python/`, declarations, evaluation, `pyproject.toml` movies table, CLI, fixtures | `WTs/declarative-movie` | the contract page |
| C | the film | Leonardo project, direct project work: `movie.py`, speech, preview, render | none (project repository) | A and B merged into `declarative-python` |

A and B run in parallel from the same base. Each is a complete two-commit
OpenSpec cycle under `AGENTS.md`, red first, and merges back into
`declarative-python` after the orchestrator's adversarial review. C is not
a cycle: it is project work committed in the Leonardo repository, and its
findings go to `workflow/warts.md`.

## Evidence to keep

`PROGRESS.md` beside this plan records commits, test runs and the render.
The campaign archives to `workflow/archive/declarative-python-<date>/` with
its report once C has been inspected by the pilot.
