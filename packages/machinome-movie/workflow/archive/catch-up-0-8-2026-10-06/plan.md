# Catch-up campaign: Videomaker under machinome 0.8 and four recorded warts

Status: working note, written 6 October 2026 at the pilot's request ("go
with 1, 2, 3, 4 and 8, keep the discipline"). Nothing here is ratified; a
cycle below becomes work through its own OpenSpec change or a narrow
adjustment under `AGENTS.md`, and the pilot's rulings stand over this note.
Where this note and a baseline spec disagree, the spec is right.

## What it does not claim

- That any of the fixes below is designed. Each cycle's proposal designs
  it; this note names the finding, the evidence and the smallest shape.
- That the Curta film is rendered again. The pilot deferred the render
  (63 min, `warts.md` Addition 14); this campaign stops at `preview`.
- That anything is pushed, published or merged beyond this repository's
  local `main`.

## Where it comes from

Five items of the warts list the orchestrator sorted for the pilot on
6 October 2026, each with evidence in hand:

1. **Videomaker's fixture project does not load under machinome 0.8.**
   Reproduced the same day on `main` fb54df7 against the workspace venv
   (`machinome vet`: universe machinome 0.8.0): `python -m pytest python/tests`
   stops at collection of `test_declarations.py` with
   `ImportError: module 'machinome.node' has no attribute 'AssemblyNode':
   the root of machinome.node exports nothing`. Both fixture models
   (`models/seesaw.py`, `models/counter.py`) import `AssemblyNode` and
   `CadQueryNode` from that root; the other roots the fixture and
   `test_take.py` use (`machinome.simulation`, `machinome.math`,
   `machinome.parameters`) still export. The Leonardo and Curta projects
   were moved to the 0.8 spelling; the fixture project was not.
2. **The Curta film is stale against its project** (`warts.md`, Addition
   28 and 38, plus the project's three machinome 0.8 commits up to
   1f3dc22). `check` on `videos/addition/_build/movie.json` refuses:
   `Source differs from pinned model revision: simulation/event_driven.py`.
3. **`speech` generates paid takes before it loads the film** (Addition
   31): `bin/videomaker.mjs` calls `generateMovieTakes` before the
   document is loaded, so a mismatched or unrecorded export is refused only
   after paying. The record names the smallest fix: load and refuse first.
4. **`python/tests/test_cli.py` tests the primary checkout's package from
   a worktree** (The player 11): its `run()` builds the child's
   environment from `PATH` alone, so the venv's editable install resolves
   `machinome_movie` to the primary checkout. The record names the smallest
   fix: the worktree's `python/` on the child's `PYTHONPATH`.
8. **Two findings marked "worth the viewer's log" are not in it** (The
   player 13 and 14): the viewer styles the element it is mounted in
   (`position: relative`) and collapses an absolutely placed host; the
   handle declares no way to release an instance. Neither is in
   `machinome-viewer/workflow/warts.md` (checked by grep, 6 October).

## The cycles

| cycle | kind | where | what |
|---|---|---|---|
| `fixture-under-0-8` | narrow adjustment (maintenance preserving ratified behaviour) | `WTs/fixture-under-0-8` | the two fixture models on the 0.8 spelling; the project re-pinned by `scripts/pin-fixture-project.mjs` with the venv's Python and `machinome`; resolved pins reviewed; both suites cold |
| `test-cli-in-the-worktree` | narrow adjustment (test hygiene) | same worktree, its own commit | `test_cli.py`'s child runs the checkout's `python/`; proved by a run from a worktree that fails red against the primary's package |
| `speech-loads-first` | OpenSpec change (changed user-visible order: refusal before purchase) | `WTs/speech-loads-first` | `speech` loads and checks the film before any take is generated; red first at layer 8 with the provider double counting requests on a refused document |
| the Curta film | project work in the Curta repository, not a Videomaker change | `projects/Calculators/Curta-Type-I-3x` | export `event_driven_curta` again at the project's head, evaluate, `check` and `preview` the film on `main` of this repository once wave 1 lands; README and `spec.md` kept true; no render |
| the viewer's log | record, in the viewer repository | `machinome-viewer/workflow/warts.md` | the two player findings filed as the log's entries, by the orchestrator |

Waves: wave 1 is the three Videomaker cycles in parallel, each on its own
worktree from this branch; wave 2 is the Curta film, after the fixture
cycle's exports have run (one CAD run of ours at a time). The viewer log
is filed at once.

## Discipline

The workspace's delegated discipline: one agent per cycle, briefed in
writing from this note; two pauses, after the proposal and before the
implementation commit; the orchestrator's adversarial review is the gate,
never a rubber stamp; no agent spawns another; no amend on a cycle branch;
a changelog bullet in the cycle that lands; findings to `warts.md` at the
merge; at the close the campaign branch is integrated into this
repository's `main` locally, and nothing is pushed.
