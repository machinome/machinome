# React stage campaign — plan

Status: working plan, 30 September 2026, opened on branch `react-stage`
(worktree `WTs/react-stage`) from `declarative-python` at 8dd2474, the head
of the previous campaign, which is not integrated into `main`. The pilot
commissioned it in these words, after inspecting the first film declared in
Python: "I gave you autonomy on the scope of the video and you were lazy and
eager to get a quick goal. You left the source code out. That deferred the
stage. New goal: implement the stage. The template needs to own the screen,
I hate that there is this hard-coded bar, I didn't specify it, but the stage
would get rid of it. All hardcoded stuff are annoying me, I want a template
to define the whole video, no hardcoded stuff in the screen. I want source
code shown, that nice way of highlighting the concepts, side by side, two
different containers. Goal: new video after the underlying software has
been implemented." Nothing here is ratified; each cycle ratifies its own
change. Integration of `react-stage` into `main` is the pilot's.

Two rulings of the pilot govern the whole campaign:

- **Steps, not protocols** (30 September 2026): `machinome-movie/0.1` was a
  step; the stage carries the declarations' shape as `machinome-movie/0.2`
  and preserves nothing of 0.1; no format is a protocol before the pilot
  makes a release; a deferral in this plan is the orchestrator's cut, never
  the pilot's choice.
- **The progress rule goes** (`remove-progress-rule`, proposed on branch
  `remove-progress-rule` the same morning): showing position is the
  player's job, not the video's; the bar leaves every film; the masthead
  stays where a set draws one. In the stage nothing is fixed chrome: a set
  draws what its template says and nothing else.

## The cut

The direction note (`workflow/ongoing/declarative-python-api.md`) lists six
steps. The previous campaign took steps 1 and 3 (the document, the Python
declarations). This campaign takes **step 2, the React stage, in full**, and
revises 1 and 3 to carry the stage's shape:

- **In.** The React stage: sets as React templates that own the whole
  screen, slots, elements, a registry, project modules bundled per movie,
  generated prop types, chrome as a set's choice; the movie document 0.2
  carrying sets, slots, elements, cues and actions; YAML episodes loading
  into the same resolved shape through shipped sets; the timeline resolving
  every element's state per frame; the renderer driving the stage with its
  readback checks, pixel proofs, shot cache and provenance intact; one test
  runner and the test memo; the Python declarations for project sets and
  elements, `Title` and `Picture` as elements, marks bound to a view,
  emphasis pairing spoken words with source tokens on any line; the film,
  *Cut and Advance* v2, with the project's own template and source shown
  beside the model in three chapters.
- **Out, the orchestrator's cut, not the pilot's.** Takes recorded from
  running or clocked scenarios (step 6; no running Leonardo episode exists);
  the `Page` element and the page take (step 4; the museum shot is wished
  for and not yet written); the studio's live preview (step 5); several
  formats from one movie; sound design. Each waits for the episode that
  needs it. Not one of them is a protocol decision.

## The empirical validation

`projects/Leonardo/videos/cut_and_advance/spec.md`, revised under "Version
2" before the cycles ran: the same five chapters and narration (the cached
takes are reused; no speech is bought), on the project's own root set
`Leonardo` and its split `LeonardoSplit`, written in the project's
`stage.tsx`; source shown in three chapters (the wheel-to-crankshaft
coupling, the pawl and ratchet laws, the winding shaft), each with spoken
words lighting tokens of the source while the same parts highlight in the
model beside it; one project element (`Jobs`, the two jobs card) lit on cue;
no progress rule; the masthead the project chooses.

## The contract the cycles build against

Written by the orchestrator before the cycles, on the campaign branch:

- `docs/movie-document.md` — the 0.2 document, the resolved document, the
  frame, and the stage's contract with the renderer.
- `schema/machinome-movie-0.2.json` — the schema both runtimes check.

A cycle that finds the contract wrong brings the finding to the
orchestrator with the smallest correction; it does not fork the contract.
The manual page `docs/stage.md` (how a project writes a set or an element)
is the `react-stage` change's to write; `docs/declaring-a-movie.md` is the
`declarative-stage` change's.

### What the stage is, in one paragraph each

**A set is a React template that owns the screen.** It receives the movie
(`title`, `series`, `style`), its own static `props`, and renders its
layout with `<Slot name="…"/>` where an element goes. It draws its chrome,
if any, inside `<Chrome>`, which the stage lifts above the transition layer,
hides in picture-only captures and measures for the proofs' mask. It is
registered under its kind with the slots it declares; the stage refuses a
mismatch by name. Sets inherit by composition: `LeonardoSplit` renders
`Leonardo`'s chrome and its own two containers.

**An element is content with state per frame.** The tool ships `view`,
`source`, `title`, `picture`; a project declares its own kind in Python,
with typed props and actions, and writes its component. A component draws
its state and nothing else: no wall clock, no measurement that changes the
picture, no state between frames. It may report measurements through
`useReport`, and the stage always reports its box.

**A frame is what the timeline resolves**, in Node, purely: the set, the
element in each slot, each element's complete state. A view's camera
follows its moves; a source panel's text follows its typing and its lit
tokens follow the take; a title's opacity and revealed words follow its
show; a picture's rect follows its view keys; a project element gets its
active actions with `progress`. The stage renders that and returns what it
measured.

**The viewer mounts once per view instance**, outside React's
reconciliation, in a host the stage positions over the view element's box
after each commit; two views in one shot are two instances; a view keeps
its instance across the shots of its chapter. Every frame re-specifies the
instance's whole state, so nothing depends on the order frames are posed in.

**One bundle per movie.** `src/stage-build.mjs` bundles the tool's runtime
(`stage/`, TypeScript, React 19) with the document's `stage.modules` into
`<root>/_build/stage/stage.js` and `stage.css` (esbuild, IIFE, production
React), generates `movie.d.ts` from `stage.sets` and `stage.elements`, and
type-checks TypeScript modules against it (`tsc --noEmit`); the bundle's
hash enters the shot cache's common key and the manifest. A YAML episode
bundles the runtime alone.

**YAML episodes keep producing** through the shipped sets `paper`,
`paper-split` and `source-only`, which reproduce the earlier page's layouts
with its masthead and no progress rule; the loader maps overlays to `title`
elements in the set's `title`, `top`, `lower-third` and `center` slots,
pictures to a `picture` element in `plate`, camera keys to `move` actions,
annotations and highlights to view actions, typing and emphasis to source
actions. Pixels change for every film (there is no release to preserve);
semantics do not.

## Cycles

| # | change | side | worktree | cut from | depends on |
|---|---|---|---|---|---|
| A | `one-runner` | Node tests: vitest, projects, Chromium once, the memo, memo honesty tests | `WTs/one-runner` | react-stage 5dae43f | nothing |
| P | `declarative-stage` | Python: project sets and elements, `Title` and `Picture` elements, view-bound marks, emphasis pairs, `Style`, evaluation to 0.2, fixtures documents and invalid set | `WTs/declarative-stage` | the contract commit | the contract |
| S | `react-stage` | Node and TypeScript: 0.2 loading and resolution, YAML into the resolved shape, the per-element timeline, the stage runtime and shipped sets and elements, bundling, the renderer on the stage, resolved fixtures, takes | `WTs/react-stage-runtime` | A merged | A, the contract |
| F | the film | Leonardo project, direct project work: `stage.tsx`, `stage.css`, `movie.py`, evaluate, check, preview, render | none | P and S merged into `react-stage` |

A runs first because S writes its tests under the runner and memo A
provides. P runs beside A; it does not touch `test/` or `src/`. S starts
when A has merged. Each of A, P and S is a complete two-commit OpenSpec
cycle under `AGENTS.md`, red first, and merges into `react-stage` after the
orchestrator's adversarial review. F is project work committed in the
Leonardo repository; its findings go to `workflow/warts.md`.

Fixture ownership while P and S run in parallel: P owns
`fixtures/documents/`, `fixtures/invalid/`, `fixtures/manifest.json` and the
takes of its documents (`fixtures/takes/<name>/`, written by the recipe in
`fixtures/README.md`); S owns `schema/` amendments (through the
orchestrator), `fixtures/resolved/` and any hand-written Node document,
named `node-*.json`. The orchestrator pins `resolved/` for P's documents
after the merge, reviewing each by hand.

## Evidence to keep

`PROGRESS.md` beside this plan records commits, test runs and the render.
The campaign archives to `workflow/archive/react-stage-<date>/` with its
report once F has been inspected by the pilot.
