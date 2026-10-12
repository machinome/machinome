# Machinome 0.9: the joins, the products entering the monorepo

Campaign plan, provisional. Written 11 October 2026 from the workspace
conversation of that day, in which the pilot set the order of the joins
and their method; the plan the campaign's OpenSpec changes are cut from.
Working record, not a promise: nothing here is ratified, no ADR is
accepted by it, and a baseline spec or an accepted ADR outranks every
sentence. Written from the framework's main at c6a3ad4f (the cut of the
ten extension packages, 10 October 2026, unreleased), on the line
`v0.9-joins`. The layout and the decisions of `monorepo-0.9.md` beside
this note still hold; this note adds the joins to them.

## What this campaign is (pilot, 11 October 2026)

The products of the ecosystem that join the repository, each one cycle,
in this order: machinome-freecad, machinome-mechanics, machinome-viewer,
the videomaker, machinome-studio. The whole set is distributed under the
one licence the framework carries, GPL-2.0-or-later OR CERN-OHL-S-2.0+ at
the recipient's choice, stated once at the root; no package in the
repository carries another.

Out of scope, by the pilot: molejo stays its own product in its own
repository, with its own names on PyPI and npm; the pilot relicenses it
there when he chooses, and nothing in this campaign touches it or waits
on it. machinome-skills was not placed by the pilot and is not in this
campaign. machinome.org, visual-identity and the browser-delivery
prototypes are not packages of the set and do not join.

## The method (pilot, 11 October 2026)

- **Directly to its final place.** A product is imported by rewriting its
  history: on a fresh clone of its repository, `git filter-repo` with
  `--to-subdirectory-filter packages/<distribution>` for what moves
  whole and a `--path-rename` for each piece that goes elsewhere, and
  `--tag-rename ':<name>-'` prefixing its tags (the viewer's `v0.7.0` to
  `v0.8.1` carry the framework's own tag names). The rewritten branch is
  fetched into the cycle bench and merged with
  `--allow-unrelated-histories`: one merge commit, made by the
  orchestrator after the cycle's planning commit, is the join. There is
  no staging directory and no later move, so every file's history reads
  at its final path, `git log` on the package directory shows its whole
  life, and `git blame` reaches the commit that wrote each line. The
  mapping is settled in the change's design and rehearsed on a throwaway
  clone before the import. A move and an edit of the same file never
  share a commit, so rename detection keeps the thread.
- **The viewer's history is duplicated, accepted.** The viewer repository
  was founded on 5 September 2026 by rewriting the framework's history:
  79 of its commits, back to 16 July 2023, are the framework's commits
  that touched `solid_node/viewers/`, filtered to it and moved to its
  root, byte-identical blobs under new hashes. The join brings those 79
  again, at the new paths, beside the framework's originals at the old
  ones. The viewer's own line then reads whole from any of its files; a
  global log shows each pre-split message twice, told apart by the paths
  they touch. The alternative, importing only the 212 commits since the
  split, would stop the viewer's history at the split; the pilot chose
  the whole line.
- **One licence at the join.** The licence file a product carries, and
  any notice stating that licence, is removed at its join; its directory
  links the root's `LICENSE` and `LICENSES/`; its manifest declares the
  set's expression and files; the records the join writes do not name
  the licence it carried before. Third-party provenance a product
  recorded (what it calls, what it adapted, whose copyright it retains)
  is kept, in the framework's `CREDITS.md`.
- **One version.** A member takes the set's version at its join (0.8.1 on
  this line), pins a sibling with `~=` both ways, and enters the
  bumpversion tables and the release-records test; the 0.9 release
  renumbers the set.
- **Where a record lives.** An extension package carries its manifest,
  its source and a README (`monorepo-0.9.md`, decision 1): its tests
  join the core suite, its specs the framework's specs, its archived
  changes and working record the framework's archives, its documentation
  the manual. A product that is not an extension package (mechanics, the
  viewer, the videomaker, the studio) keeps its record in its directory:
  manual, specs, ADRs, working record, tests (`monorepo-0.9.md`, "A
  record lives with what it records").
- **The original repository stays as it is**, the record of the original
  hashes. Pushing the join, and archiving or retiring the original on
  GitHub, are the pilot's.

## Cycles

Each cycle is one OpenSpec change on a bench cut from this line
(`scripts/dev-env v0.9-joins-<change> setup --base v0.9-joins`), the
two-commit cycle with the join merge between its commits.

1. `join-freecad`. machinome-freecad, the native FreeCAD assembly adapter
   born from the Dum-E project: branch `lean-core-validation` at 5ed665f,
   four commits containing its main, unreleased, the module
   `machinome_freecad` with `FreeCADAssemblyNode` and `FreeCADJoint`, its
   runtime an independently installed FreeCAD 1.1.4 found through
   `MACHINOME_FREECAD_ROOT`. It becomes `machinome-node-freecad` at
   `packages/machinome-node-freecad/`, the module `machinome.node.freecad`
   (a package portion, as `machinome.node.openscad` is), installed by
   `machinome[freecad]`, a row of the supported node types table so an
   absent package is refused by its extra at its import (ADR-184), and a
   row of the layout gate. Its four test modules and their FCStd fixtures
   join the core suite, skipping without `MACHINOME_FREECAD_ROOT`; its
   spec `native-freecad-assembly` joins the framework's specs; its
   archived change and its workflow archive join the framework's
   archives; `docs/api.md` and `docs/runtime.md` become a how-to page of
   the manual and an install row; the provenance of `NOTICE.md` joins
   `CREDITS.md`. Its licence file, notice, manifest files, smoke script,
   `.gitignore`, OpenSpec configuration and workflow README go, replaced
   by the repository's. `scripts/check-dist` grows a row. The extra
   installs no FreeCAD. The Dum-E project, the originating project, moves
   onto the module in its own repository, by the orchestrator, as the
   cycle's empirical validation with the runtime set.
Between cycles 1 and 2 (12 October 2026): the framework cycle
`digest-only-what-the-node-names`, done on its bench on 10 October 2026
against 0.8.1 and not integrated while the cut moved the framework under
`packages/machinome/`, is merged into the line at 55befe33. Its ADR is
renumbered from 182 to 186 (the cut took 182 to 185 meanwhile), its
archived change and its two new files are placed under
`packages/machinome/`, the three append conflicts in the records (the
ADR index, the manual's changelog, `workflow/warts.md`) are resolved by
keeping both sides, and `HISTORY.rst` gains its bullet. The suite on the
bench's uv venv: 4827 passed, 24 skipped; `scripts/check-dist` green;
wall clock 02 on a scratch copy of the project's `string-cache` worktree
at b980d59 with the bench: a cold build of 54 parts in 55.0 s, a warm
build with all 54 untouched in 14.4 s, the cord edit at line 144 with
all 54 restamped and none regenerated in 15.9 s. Not a cycle of this
plan; recorded so the line's head reads whole.

2. `join-mechanics`. machinome-mechanics, published 0.1.0, pure Python,
   with its own tests and manual, into `packages/machinome-mechanics/`
   whole, record included. Decisions owed before it is proposed: its
   import name, `machinome.mechanics` under the norm settled on 2 October
   2026 or `machinome_mechanics` kept (fifteen project repositories
   import it today); its manual, folded into the one manual or kept as
   its own Read the Docs project built from its directory.
3. `join-viewer`. machinome-viewer, whole into `packages/machinome-viewer/`
   with its record, tags prefixed `viewer-`. The widget's `package.json`
   is the first npm member, so the root `package.json` workspace of
   `monorepo-0.9.md` is founded here. The entry-point seam is unchanged.
   Its name leaves the root manifest's excluded dependencies and the lock
   resolves it from the workspace. Its manual's question is mechanics'.
4. `join-videomaker`. Two members from one repository: the npm package
   `machinome-videomaker` and the Python distribution `machinome-movie`
   from its `python/` directory. It declares a licence for the first time
   rather than changing one. The take transport the player campaign left
   in it lifts into the viewer, as that campaign recorded for the
   monorepo. Playwright and Chromium enter the suite's CI.
5. `join-studio`. machinome-studio, whole into `packages/machinome-studio/`,
   its profiles, shop skills and records with it; its frontend the third
   npm member. The end-user product, last because it consumes the viewer
   and the framework's command.

Close: the suite, `scripts/check-dist` and the universe sweep at the
line head; the merge into local main; the workspace follow-ups (the
contract's status paragraphs, `docs/collaborator-setup.md`,
`scripts/setup` installing the joined packages, the launcher's path).

## Not decided by this plan and held for the pilot

mechanics' import name; the manuals of mechanics and the viewer, folded or
kept; machinome-skills; the push of the line; the 0.9 release and its
renumbering; the fate of each original repository on GitHub.

## Empirical validation, per cycle

The suite green on the bench's own venv from `packages/machinome`; the
manual built with warnings as errors; `scripts/check-dist` green on the
tree and on a clean copy; the universe sweep
(`scripts/load-projects --bench <bench>/packages/machinome --python
<bench>/.venv/bin/python --moved scripts/load-projects.d/*.toml`)
identical to its base row for row or each difference explained; and the
joined product's own tests green at their new place. For `join-freecad`,
the FreeCAD tests run with `MACHINOME_FREECAD_ROOT` set to the 1.1.4
extraction, and Dum-E loads on the bench with the root set.

## Progress

(entries appended by each cycle's applier at its close)

1. `join-freecad`. **Done** (11 October 2026): branch
   `v0.9-joins-join-freecad`, planning commit dea7d7f4 on cf631645, ratified
   by the orchestrator's review; the join, the merge commit dba7dae5 of
   machinome-freecad's `lean-core-validation` rewritten by `git filter-repo`
   to its final paths (51 files; `git log --follow` on the adapter reaches
   fc69a67a of 1 October 2026). ADR-185, a node type may read a whole
   assembly through an external program, accepted; ADR-183 amended. The
   package is `packages/machinome-node-freecad/` (the package directory
   `machinome/node/freecad/` with `__init__.py`, `adapter.py`, `runtime.py`
   and `worker.py`), numbered 0.8.1, requiring `machinome~=0.8.1`,
   `machinome-engine-brep~=0.8.1`, numpy and scipy, under the set's licence;
   the table of supported node types gains the row `freecad`, the core the
   extra `freecad` and `all` with it, and an absent package is refused by
   `machinome[freecad]` at every door with no edit to ADR-184's finder. Its
   occurrences are `BrepLeafNode` leaves at leaf contract 3 through the B-rep
   engine's seam. Its four test modules, three helpers and 27 FCStd fixtures,
   regenerated with the set's licence in their metadata, join the suite and
   skip without `MACHINOME_FREECAD_ROOT`; its spec `native-freecad-assembly`,
   its archived change and its workflow record join the framework's, its
   guide the manual as `howto/freecad-assemblies`, its provenance
   `CREDITS.md`. The specs modified are `native-freecad-assembly` (one
   requirement renamed), `kernel-extras`, `node-model`, `framework-identity`
   and `framework-contributor-guidance`; `user-documentation` gains one
   requirement. `uv lock` resolves 188 packages. The suite green on the
   bench's uv venv without the runtime (4798 passed, 24 skipped, the base's
   20 and the four FreeCAD modules, 7136 subtests); the four FreeCAD modules
   with FreeCAD 1.1.4 and Dum-E's untouched source, 82 passed; the manual
   built with warnings as errors; `scripts/check-dist` green: twelve members
   built, 24 archives `twine check --strict` passed, the FreeCAD package
   installed through its extra and its construction refused naming
   `MACHINOME_FREECAD_ROOT` without the runtime, blocked at its enabled
   limit, 120 degrees, through FreeCAD with it; a clean copy's framework
   sdist holds 1045 entries (39 more: the guide, the tests, the fixtures)
   and its wheel 114, the FreeCAD package's 22 and 11; nothing uploaded.
   Dum-E moved onto `machinome.node.freecad` in its own repository (its
   commit 26ae7aa): its 7 tests passed with the runtime set, its posed
   snapshot byte-identical to that of 1 October 2026 (SHA-256
   `40f8d568...b804`) and looked at, `machinome vet` exit 0, pure. The
   universe sweep after the move: 63 repositories, 130 rows, 122 ok, 0
   expected, 2 unexpected, 0 timeout, 6 no-model; Dum-E's row ok, the two
   unexpected the base's (fender-bender without `fb_library`, wall_clock_41's
   own error). Two findings recorded in `packages/machinome/workflow/warts.md`:
   vet does not read `freecad_source`, and the leaf-contract reach gate does
   not read the adapter. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-11-join-freecad/evidence.md`.
