# Empirical helper expansion

Pilot authority: 2026-09-20 conversation. Implement the audited shortlist,
one public helper per OpenSpec cycle; after implementation use gpt-5.6-sol
subagents to refactor consumers and report issues. Validate in at least two
distinct project repositories, sync baseline specs, archive and merge locally
before starting the next helper. No per-cycle ratification is required. Skip a
blocked helper with evidence; do not archive unfinished work. No push or release.

Resource discipline added at pilot request during cycle 8: do not run unbounded
nested symbolic-expression expansion or parallel heavy CAD checks. Evaluate
only the changed expression boundary when full expansion duplicates shared
graphs, retaining full-model numeric and CAD evidence. Run lightweight probes
with explicit memory/CPU/wall limits and measure peak RSS; sequence heavy checks
with thread counts limited and a bounded memory budget. Report a necessary
check that cannot fit instead of silently raising its limit.

For CAD, address-space caps rejected shared-library mappings even around
560 MiB RSS. The available systemd user manager/cgroup v2 supports a stronger
actual-memory limit: run one isolated transient unit with `MemoryMax=768M`,
`MemorySwapMax=0` and bounded `RuntimeMaxSec`, explicit working directory and
source/environment overlays. This caps the whole process tree, including CAD
children, without mistaking virtual mappings for resident consumption. Do not
raise the physical cap when a check fails; record the limitation or skip the
helper. A no-op transient-unit smoke succeeded before adopting this mechanism.
Treat CAD-backed project imports and model set_state probes as heavy too:
their short duration does not imply a small working set. They require the
same sole-process slot and cgroup bounds as CAD tests, builds and captures.

Each cycle records its exact consumer commits, validation commands, results,
limits and any issues in its own `validation.md`. Existing project evidence and
user changes are preserved. Refactors preserve mechanics and public controls;
new design choices exposed by validation are reported, not silently substituted.

| Order | Public helper | Empirical consumers to verify | State |
| --- | --- | --- | --- |
| 1 | `rolling_travel` | Dragon R1; Thor; six additional repositories | integrated |
| 2 | `rolling_angle` | Prusa3-vanilla; Kossel; four additional repositories | integrated |
| 3 | `pulley_pitch_radius` | Thor; Open Robot Actuator; five additional repositories | integrated |
| 4 | `belt_tangent_points` | Thor; Prusa3-vanilla; three additional repositories | integrated |
| 5 | `belt_path_metrics` | Prusa3-vanilla; Kossel; Metamaquina2; Hangprinter; Thor | integrated |
| 6 | `belt_pulley_angle` | Metamaquina2; Prusa3-vanilla; Kossel | integrated |
| 7 | `two_link_angles` | ZeroBug; Spiderbot; AlbertPro (BiPed singular-origin exclusion) | integrated |
| 8 | `four_bar_pose` | Dragon R1; Strandbeest | integrated |
| 9 | `cycloidal_ratio` | CycloidalDrive; OpenCycloid | active |
| 10 | `harmonic_cam_lift` | Leonardo cam hammer; Deepseek sawmill | queued |
| 11 | `internal_mesh_angle` | Thor; OpenTorque | queued |
| 12 | `differential_angles` | Thor; Dragon R1 | queued |
| 13 | `indexed_advance` | Pascaline-module; Deepseek sawmill | queued |

Names and consumer selection remain working assumptions until each cycle's
source inspection confirms its contract. Do not manufacture a second consumer
or change a project's behavior merely to meet the threshold.

## Integration evidence

`rolling_travel`: mechanics `264d4839db143dc0f4c863c5e75700de8e5c8902`
is on main. All eight exact consumer commits named in its archived validation
are verified at the tips of their original branches (main, master, version_4
or declarative-api as recorded). Each project imports the merged primary
mechanics package. Post-integration package checks: 38 tests and 24 subtests;
all three baseline specs validate strictly. The clean helper worktree was
removed, retaining the branch. Existing screenshots and the unrelated
user-documentation worktree were preserved. Nothing pushed or published.

Environment note: the framework's primary branch advanced independently from
`9fb5127` to `0ce71cd` during cycle 1. Its validation header identifies the
initial observed dependency, not a frozen framework checkout for every later
consumer run. The mechanics content and all consumer commits are exact; future
cycles record dependency heads around their checks to expose such drift.

Cycle 2 integration: mechanics `3ac3767e73efd810ffbc25b5f48cefd6cc745d93`
is on main. All six exact consumer commits in its archived validation were
fast-forwarded to their unchanged original master/main/declarative-api branches.
Every project imports the merged primary package. Post-merge checks passed:
46 package tests, 24 subtests and three strict baseline specs. The clean helper
worktree was removed, branch retained; nothing pushed or published.

Cycle 3 integration: mechanics `59f63bbbf225fa142c79cc72a73c6d1269a5918e`
is on main. All seven consumer commits in the archived validation were
fast-forwarded to their original branches and their imports resolve to the
merged package. Post-merge 57 tests, 24 subtests and three strict baseline
specs passed. Clean helper worktree removed, branch retained; user screenshots
preserved in mechanics and Dutch Windmill 2. No push or publication.

Cycle 4 integration: mechanics `45bcabffc3325a4de9f2034e54b1e60d7df18502`
is on main. All five exact consumer commits in its archived validation are on
their original branches; their ordinary imports resolve to the merged package.
Post-merge 78 tests, 24 subtests and three strict baseline specs passed. Clean
helper worktree removed, branch retained. No push or publication.

Cycle 5 integration: mechanics `ec4f0c334bfbb62fe17b47ddaa2fef3c84159c8c`
is on main. All five consumer commits recorded in archived validation are on
their original branches and import the merged package. Post-merge 97 tests,
24 subtests and three strict baseline specs passed. Clean helper worktree
removed, branch retained; user screenshots preserved. Independent review caught
and fixed a floating wrap seam red-first; Thor's legacy degenerate policies
were preserved in its adapter. Framework advanced independently from 0ce71cd
to 8d2bd71 during validation; records distinguish those observations. No push
or publication.

Cycle 6 integration: mechanics `7af7eefc0f1666c6109f0062970986df0e785373`
is on main. All three exact consumer commits recorded in archived validation
are on their original branches and import the merged package. Post-merge
109 tests, 24 subtests and three strict baseline specs passed. Clean helper
worktree removed, branch retained. Dependency heads remained clean/stable at
framework 8d2bd71 and viewer 4355da1. No push or publication.

Cycle 7 integration: mechanics `8bbad8af6042d0aeb55de28202e3eeb9e73213cf`
is on main. All three exact consumer commits in archived validation are on
their original main branches and import the merged package. Post-merge
128 tests, 24 subtests and three strict baseline specs passed. Clean helper
worktree removed, branch retained. BiPed stays unchanged because its finite
deferred origin convention is not the helper's singular geometry. Parent
review strengthened Spiderbot's probe to exercise the real solver. Dependency
heads stayed clean/stable at 8d2bd71/4355da1. No push or publication.

Cycle 7 packaging follow-up: integration review found missing dependency
declarations in ZeroBug and AlbertPro, whose first mechanics imports were added
by that cycle. Metadata-only consumer commits
`07cf32fecd1d28d59338533248fd916e3deb544a` (ZeroBug) and
`d0e35ee0312a5b011c959c786862a0959a3324a7` (AlbertPro) are now on main.
Both declare machinome-mechanics>=0.1.0; Albert's Python minimum now matches
>=3.11. Parent verified TOML and merged-package imports. ZeroBug wheel metadata
was checked; Albert's pre-existing flat-layout discovery gap prevents wheel
building and remains documented, not repaired. No formula or CAD changed.
Consumer records state the dependency is founded but unpublished and requires
source installation. Future migrations check metadata alongside imports.

Earlier-cycle metadata follow-up: Thor commit
`c229b25322e3b899aa70349355dccd262fb8748b` aligns its Python minimum to
>=3.11; Fender Bender commit `5f23cd14c307bee2e58d4d3423a334442562fc5d`
adds machinome-mechanics>=0.1.0 to its existing requirements.txt. Parent
reviewed the focused diffs and fast-forwarded both unchanged original main
branches. Static metadata checks and merged-package imports passed under a
768 MiB address-space cap; Fender's consumer import also passed. Thor's
additional CAD-backed import could not map OCP under that cap and is not
claimed as a pass. No formula or CAD changed, and no heavy gate was rerun.
Both consumer records explain the founded-but-unpublished source dependency.

Cycle 8 integration: mechanics `25180b0efadc35cd22def3e2f073c7834538c43e`
is on main. Dragon R1 `107102444b2614f65e6beb9229657c5a160e3d9f` and
Strandbeest `4ccaa591de164322a6e62318d1ddd0d6b6111987` are on their original
main branches and import the merged package. Post-merge 143 tests, 24 subtests
and three strict baseline specs passed. Clean helper worktree removed, branch
retained; user screenshots preserved. Final Strand affected exact/faceted CAD,
full build and fresh capture passed under the new 768 MiB physical-memory
process-tree cap. Parent also verified the cap on a live capture unit and
terminated the obsolete broad-sweep orphan. Dependency heads remained clean
at 8d2bd71/4355da1. No push or publication.

## Project findings outside helper scope

- Kossel: inverse-rolling review found the vertical belt anchor using the
  copied X-axis span projection. Existing wheel/mesh checks miss the resulting
  excessive travel because geometry is periodic. The rolling-angle cycle's
  validation and Kossel `docs/mechanics-rolling-angle.md` contain measurements;
  behavior is deliberately preserved here, pending a separate red-first
  project correction.
