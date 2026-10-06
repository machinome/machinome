# Fix-warts 3: the autonomously workable findings

Status: working record, opened 6 October 2026. Not ratified; each cycle's
archived OpenSpec change is the authority for what it did. This note says
which entries of `../warts.md` the campaign takes, in what order, what
validates each, and where it stands. It claims nothing about entries it
does not name.

## Mandate

The pilot, 6 October 2026, after an assessment of `warts.md` that sorted
its entries into plain defects with a stated remedy, investigations, and
items held for the pilot: "work on the items you can autonomously,
orchestrating opus subagents and using empirical evidence from projects
to validate, other than your adversarial review. if something needs my
input, record and defer, you'll go unsupervised."

So: every cycle is proposed and applied by an Opus subagent, reviewed
adversarially by the orchestrator before each of its two commits, and
validated in the project whose finding it closes, not only by its own
tests. Anything that turns out to need a product, architecture or policy
choice is recorded under "Deferred to the pilot" below and left alone.
Nothing is pushed, published or integrated into a release line; the
campaign branch merges into the local `main` at close, as the standing
rule for a validated campaign says.

## Bench

Branch `fix-warts-3`, worktree `machinome/WTs/fix-warts-3` (slot 8), cut
from `main` at `d7b6f9b` (6 October 2026, "readme-for-readers"). One bench
for the whole campaign: cycles run one at a time, each as its two commits
on this branch, in the order below. A cycle that must be set aside leaves
no uncommitted state behind.

A resolved entry leaves `warts.md` in the cycle that closes it, for
`../archive/fix-warts-3-2026-10-06/resolved.md`, which keeps the text and
says what closed it; the changelog's `Unreleased` section takes a bullet
in the same cycle.

## Cycles, in order

| # | Change | Closes | Validated in |
|---|---|---|---|
| 1 | `snap-keeps-the-triad-unit` | SO-ARM100 triad snap (frames with `x` omitted; the joint's own snap) | SO-ARM100 |
| 2 | `build-settles-on-a-grown-source-set` | `machinome build` restarts every second when a data source is newer than its module (the lean-install hang; the mesh-engine addendum); promoted here on 6 October because it blocks the full suite on this bench (seven `test_scad_presentation` tests) | the fixture project; a fresh worktree of a small STL-backed project |
| 2a | `name-what-is-refused` | axis-less refusal names a Revolute for a Prismatic; `JointRangeError` names the installed joint, not the mate's coordinate; `a.drives(a)` deadlocks instead of naming itself | OpenMANIPULATOR-X |
| 3 | `children-refuse-early-reads` | `self.children` reads empty during `simulate()` | AlbertPro |
| 4 | `resolve-repeated-joints-per-copy` | a `.repeat()` copy's joint callable reads `index` before it exists | Prusa3-vanilla |
| 5 | `tooling-paths-and-flags` | parity fixture generator from a worktree; bare `--preview`; negative-leading camera `--up` | 3DPrintedClocks, Voron-2 snapshot commands |
| 6 | `name-solids-by-path` | interference failures name the leaf only | 3DPrintedClocks mantel 34, Thor |
| 7 | `keep-the-corpus-cursor-honest` | corpus generator's record cursor across a scripted restore | Curta-Type-I-3x |
| 8 | `snapshot-the-follow-prefix` | the Follow prefix cache hands back a mapping proxy | Curta-Type-I-3x |
| 9 | `clocked-snapshot-identity` | `ClockedSnapshot` carries no identity | Curta-Type-I-3x |
| 10 | `production-reads-once` | production binding after a build doubles placements; a missing input file escapes as a changed-file error | Curta-Type-I-3x production slice |
| 11 | `production-reports-in-scope` | Markdown gate refuses non-dependencies; an overlap elsewhere blocks a child's reports; declaration paths change shape with the count | Curta-Type-I-3x production slice |
| 12 | `refuse-the-undeclared-file-by-name` | four adapters refuse an undeclared file inconsistently; the builder's wrapper names the model | fixture projects |
| 13 | `report-the-instant` | runner keeps the last failing instant; names no instant; `setUp`/`setUpClass` errors lose the verdict | 3DPrintedClocks |
| 14 | `key-the-shape-on-its-observation` | `cached_shape` keyed on a float mtime | Thor or a clock |
| 15 | `strict-manual-build` | `sphinx -W` red; stale "not yet viewed" line; the joints page on conditional placement | docs |
| 16 | `release-metadata-and-vestiges` | `viewer` extra floor; vestigial `mesh_stl_file`; a leaf's `.scad` becoming a self-import (if still so) | fixture projects |
| 17 | investigations | build restart loop; artifact freshness; OpenAstroMount's refused scenario; `networkx` on the mesh path; the exact-geometry flake; Thor's seat inventory; wall clock 02 | each its project |
| 18 | exact suite timings | fold commit `a659cc7` against main, two or three projects | catalogue |
| 19 | outside the framework | studio API skill's `cancel()` warning, and its Frame paragraph's per-component snap sentences (companion of cycle 1, lines ~814 and ~995); viewer's stray `openscad.py`; the viewer's committed parity fixture is behind the framework's (cycle 5 found 249 expressions now rewritten over a 145-entry bindings table against the committed 4; same keys and values) | studio, viewer repositories |

## Progress

- 6 October 2026: bench opened; this note written.
- 6 October 2026: cycle 1, `snap-keeps-the-triad-unit`, applied: a joint's
  axis and a frame's snapped-path directions snap to an axis only as a
  whole; SO-ARM100's frames, axes and pose operations unchanged; entry
  moved to `../archive/fix-warts-3-2026-10-06/resolved.md`, the two snaps
  it left recorded in `../warts.md`.
- 6 October 2026: cycle 2, `build-settles-on-a-grown-source-set`, applied
  (promoted ahead of the rest: it blocked the full suite): a part source
  newer than its module no longer restarts a build without end; the
  fixture, a scratch project and a fresh worktree of
  Robots/hexapod_spiderbot_model build in one generation, and the full
  suite runs with nothing deselected; the `mesh-engine` addendum moved to
  `../archive/fix-warts-3-2026-10-06/resolved.md`, the three-hour hang
  left in `../warts.md` with a Remaining note.
- 6 October 2026: cycle 2a, `name-what-is-refused`, applied: an axis-less
  `Prismatic` or `Orbit` is refused naming its kind, a range refusal on a
  mate's joint names the mate on its assembly, and `a.drives(a)` is refused
  by name at class definition; OpenMANIPULATOR-X's refusal now heads
  `arm.link2.link3.link4.link5: mate 'left_travel'`, its suites and
  OpenArm's unchanged; three entries moved to
  `../archive/fix-warts-3-2026-10-06/resolved.md`, the two questions it
  left recorded in `../warts.md`.
- 6 October 2026: cycle 3, `children-refuse-early-reads`, applied: a read
  of an internal node's `children` inside `render()` or `simulate()`
  before the framework has linked them is refused naming the declared
  attributes; AlbertPro's runs unchanged (35 and 12); the eight clocks
  refuse at load as expected. On the project branch `children-reads`
  clocks 12, 25 and 28 are rewritten and load with their colours; the
  edits of 32, 36, 37, 39 and 40 were refused by the harness and are not
  made. The entry moved to
  `../archive/fix-warts-3-2026-10-06/resolved.md`; the clocks and reads
  outside any phase are recorded in `../warts.md`.
- 6 October 2026: cycle 4, `resolve-repeated-joints-per-copy`, applied: a
  `.repeat()` copy carries its `index` from the start of its own
  construction, so its `check()` and the functions given as its
  class-declared joint and frame arguments read it and each copy resolves
  its own; resolution did not move, and ADR-096 is amended. Prusa3-vanilla's
  documented run unchanged (17 passed, the same 2 failed); the entry moved
  to `../archive/fix-warts-3-2026-10-06/resolved.md`.

## Deferred to the pilot

(Entries met during the campaign that turned out to need a decision.
Each names the entry, what was found, and the choice.)

- **Cycle 3, `children-refuse-early-reads`: eight clock models.** The
  refusal of a `self.children` read inside `render()` (always empty
  there, since `render()` is what decides the children) makes
  3DPrintedClocks' wall clocks 12, 25, 28, 32, 36, 37, 39 and 40 refuse
  to load until their eighteen such reads loop over the declared
  attributes instead; seven of them publish sixty dial islands and forty
  other parts with no colour today because of exactly that read. The
  orchestrator chose to refuse (the finding's point is that a silent
  wrong model becomes an error) and started the companion rewrite as
  direct project work on the project branch `children-reads` (worktree
  `projects/3DPrintedClocks/WTs/children-reads`, commit `58ff90e`:
  clocks 12, 25 and 28 rewritten, validated against this bench, their
  77 uncoloured parts now coloured). The rewrite of clocks 32, 36, 37,
  39 and 40 stopped there: in this session every Edit of a project file
  prompts for permission (worktree and checkout alike, through the
  `./projects` spelling), the pilot declined the prompts, and the
  orchestrator may not add the allow rule itself. Your decisions: the
  one-line allow rule for `Edit`/`Write` under the projects tree in
  `.claude/settings.local.json`; the remaining five clocks (each loop
  over its declared attributes, as the three done show); merging
  `children-reads` into `solid-node-simulation` and the order in which
  it and this change land. Until then those eight clocks refuse to
  load against this framework, and the project's checkout carries the
  untracked `WTs/` directory of that worktree.
