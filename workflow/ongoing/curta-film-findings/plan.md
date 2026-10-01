# Curta film findings — plan

Status: working plan, 1 October 2026, on bench `curta-findings` (worktree
`machinome/WTs/curta-findings`), cut from `main` at 8a8a267. Nothing here
is ratified: each cycle ratifies its own change under
`skills/framework-change/SKILL.md`, the orchestrator's adversarial review
being the gate the pilot delegated. The bench fast-forwards into `main`
when its three cycles are merged and the suite is green on its head, by
the pilot's ruling of 1 October 2026 that a finished campaign is
integrated, not forked from. This plan claims no version number and no
release; it changes neither the viewer nor the document version.

## The findings

Filed in `workflow/warts.md` as "Three findings from filming the clocked
Curta (1 October 2026)", from Videomaker's curta-video campaign, which
filmed `ClockedCurta` (document version 8) by recording a take through
the public `Sim` and posing the viewer from the recorded banks:

1. **`Sim` fails over a project reached through a symlink.** With the
   workspace's `projects/` a symlink to `/mnt/data/machinome-projects`,
   `Sim(ClockedCurta())` run from the symlinked path raises
   `PermissionError: [Errno 13] Permission denied: '/mnt/home'` in
   `machinome/node/base.py` `_make_build_dirs`; from the real path it
   works. The build directory is anchored on a root that the symlink
   resolves to the wrong place.
2. **`Sim` publishes no machine identity.** The export's manifest carries
   `clocked.identity` and the viewer validates snapshots against it, but a
   consumer recording a take can read it only from the private
   `sim._clocked.identity`, so it cannot refuse a take recorded over a
   model whose machine differs from the export's.
3. **`machinome export` writes no record of the source revision.**
   Videomaker pins a film to the model it filmed through
   `<export>/source-revision.txt`, which Leonardo's own gallery script
   writes and the Curta film had to write by hand.

## Rulings and cuts

- **Pilot, 1 October 2026, finding 3:** the record goes inside
  `manifest.json`, as a `source` object with the revision and a dirty
  marker. It is additive under the export spec's own rule, as `loop` and
  `markings` were: a consumer that ignores it draws the same picture, so
  the document version does not move and the viewer declares nothing new.
- **Orchestrator's cut, finding 2:** a read-only `Sim.identity`, the same
  string as the manifest's `clocked.identity` for the same model. A `Sim`
  that is not clocked refuses it by name, as the other clocked-only
  members are refused. The snapshot's shape is unchanged; that the
  viewer's snapshot carries the identity and the framework's does not is
  recorded as a finding, not changed here.
- **Orchestrator's cut, finding 1:** the build directory is anchored
  consistently, every side of the path either resolved or not, and the
  fix is proved with a project reached through a symlink.
- **The dirty marker:** `source.dirty` is true when the project's tree has
  tracked modifications or untracked files that are not ignored; the
  export never refuses a dirty tree, since exporting mid-work is normal.
  The root asked is the project root the framework already anchors the
  build directory on; when it is not inside a Git work tree, `source` is
  absent and the document is byte for byte what it was.

## Cycles

| # | change | worktree | depends on | ADR |
|---|---|---|---|---|
| 1 | `sim-through-a-symlink` | `machinome/WTs/sim-through-a-symlink` | nothing | none expected; ADR-159 reserved |
| 2 | `sim-identity` | `machinome/WTs/sim-identity` | nothing | ADR-157 |
| 3 | `export-records-its-revision` | `machinome/WTs/export-records-its-revision` | nothing | ADR-158 |

Waves: 1 and 2 together, 3 after, so that at most two framework suites
run at once. Each is a complete two-commit OpenSpec cycle on an opus
agent in its own worktree, cut from the bench with
`scripts/dev-env <change> setup --base curta-findings`, reviewed by the
orchestrator before its merge into the bench.

## After the bench lands, elsewhere

- The studio's `shop-skills/machinome-api/SKILL.md` gains `Sim.identity`
  and the manifest's `source` (the orchestrator, in the studio
  repository).
- Videomaker reads `source` from the manifest instead of
  `source-revision.txt`: a Videomaker cycle after this bench is in
  `main`, since Videomaker's tests run on the workspace venv's framework.
- Leonardo's `scripts/gallery.py` stops writing the sidecar; the Curta's
  hand-written file is deleted and its clocked export is made again
  (project work, direct).

## Evidence to keep

`PROGRESS.md` beside this plan records worktrees, commits, test runs and
merges. When the bench is in `main`, this directory moves to
`workflow/archive/curta-film-findings-<date>/`.
