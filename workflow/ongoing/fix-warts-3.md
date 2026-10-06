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
| 2 | `name-what-is-refused` | axis-less refusal names a Revolute for a Prismatic; `JointRangeError` names the installed joint, not the mate's coordinate; `a.drives(a)` deadlocks instead of naming itself | OpenMANIPULATOR-X |
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
| 19 | outside the framework | studio API skill's `cancel()` warning; viewer's stray `openscad.py` | studio, viewer repositories |

## Progress

- 6 October 2026: bench opened; this note written.

## Deferred to the pilot

(Entries met during the campaign that turned out to need a decision.
Each names the entry, what was found, and the choice.)
