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

From the viewer's join on, `release-0.9.md` beside this note lists the
cycles and the pilot's decisions of 12 October 2026; this list stays as
written on 11 October for the record.

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

2. `join-mechanics`. **Done** (12 October 2026): branch
   `v0.9-joins-join-mechanics`, planning commit db007dd0 on d5d194ad,
   ratified by the orchestrator's review, with the pilot's decisions of 12
   October 2026 (the import `machinome.mechanics`, the manual folded into
   the framework's, mechanics at its own version); the join, the merge
   commit 076b566d of machinome-mechanics' `v0.8-symbolic-assertions`
   rewritten by `git filter-repo` to its final paths (157 files, 45
   commits, the tag `mechanics-v0.1.0`; `git log --follow` on `belts.py`
   reaches f8c2cefd of 20 September 2026, and `git log` on `gears.py`, without
   `--follow`, the founding commit b3f5a127 of 11 September 2026). ADR-187,
   the mechanics helpers are a portion of the repository at their own
   version, accepted; ADR-132 superseded in its import path and repository,
   ADR-182 and ADR-183 amended. The package is
   `packages/machinome-mechanics/` (the package directory
   `machinome/mechanics/` with its `__init__.py` and nine family modules),
   numbered 0.1.0 outside `.bumpversion.cfg`, requiring `machinome>=0.8.0`,
   under the set's licence, keeping its changelog, tests, specs, sixteen
   archived changes and working record in its directory; no module of the
   former name `machinome_mechanics` is provided. The core's `mechanics`
   extra floors at `machinome-mechanics>=0.1.0`; the boundary test's guard
   refuses the dotted address; the layout gate gains a table of products;
   the release records hold the package to its changelog and the manual's
   `mechanics_version`; the vet universe's contract is `machinome` and
   `molejo`. Its manual folds into the framework's as the reference section
   `reference/mechanics/` and the how-to `howto/mechanism-formulas`, whose
   149 examples the package's tests run. The specs modified are
   `mechanics-distribution`, `framework-identity`, `vet`,
   `user-documentation` (one requirement renamed) and
   `framework-contributor-guidance`. `uv lock` resolves 188 packages; the
   sync installs the package editable and removes the PyPI 0.1.0. The suite
   green on the bench's uv venv (4838 passed, 24 skipped, the base's, 7505
   subtests); the package's tests from its directory, 204 passed, run by a
   step of CI's test job; the manual built with warnings as errors;
   `scripts/check-dist` green on the tree and on a clean copy: thirteen
   members built, 26 archives `twine check --strict` passed, the mechanics
   wheel installed by its path and smoked numeric and symbolic; the clean
   copy's framework sdist holds 1059 entries (13 more: the how-to and the
   mechanics section) and its wheel 114, the mechanics package's 213 and 17;
   nothing uploaded. The projects moved onto `machinome.mechanics` in their
   own repositories: 47 files in 26 repositories, one commit each, the
   verification records under `docs/` and science-jubilee's pinned tool left
   as they were. Thor 29 of 34, dragon-r1 3 of 3 and wall clock 02 14 of 22
   on the bench, the failures those of before the move. The universe sweep
   after the move: 63 repositories, 130 rows, 122 ok, 0 expected, 2
   unexpected, 0 timeout, 6 no-model, identical to `join-freecad`'s row for
   row; no sweep ran before the move. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-12-join-mechanics/evidence.md`.

3. `join-viewer`. **Done** (12 October 2026): branch
   `v0.9-joins-join-viewer`, planning commit 912fb7b4 on 484a528f, ratified
   by the orchestrator's review, with the pilot's decisions of 12 October
   2026 (the viewer whole with its record, the import `machinome.viewer.web`,
   one licence, one version with `~=` both ways, pip-only distribution with
   a root npm workspace, the seam unchanged); the join, the merge commit
   7ed45449 of machinome-viewer's `main` rewritten by `git filter-repo` to
   its final paths (893 files, 285 commits, `main` at 1b41968, the tags
   `viewer-v0.7.0` to `viewer-v0.8.1`; `git log` on `server.py`, without
   `--follow`, reaches 88f844be of 18 July 2023, and on `evaluator.ts` the
   commit of 16 July 2026 that added the widget). ADR-188, the browser
   viewer is a product of the repository numbered with the set, accepted;
   ADR-068 superseded in its repository and licence, ADR-182, ADR-183 and
   ADR-187 amended. The package is `packages/machinome-viewer/` (the package
   directory `machinome/viewer/web/` with its eight modules and the widget,
   no `__init__.py` at `machinome/` nor `machinome/viewer/`), at 0.8.1 with
   the set, requiring `machinome~=0.8.1`, under the set's licence (155
   source headers and the bundle's banner), keeping its changelog, tests,
   specs, archived and active changes, working record and decision log in
   its directory; no module of the former name `machinome_viewer` is
   provided. The core's `viewer` and `web-snapshot` extras pin
   `machinome-viewer~=0.8.1`, its `dev` extra installs `web-snapshot`, the
   framework runs `python -m machinome.viewer.web`, and `machinome vet`
   denies the package as a framework internal. The root holds an npm
   workspace, a private `package.json` and one `package-lock.json` seeded
   from the widget's (174 resolutions, 0 moved); the currency check and the
   packaging guard read `node_modules` where npm puts it. The manual folds
   into the framework's as three how-tos and the reference section
   `reference/viewer/`, the embedding example built beside its guide with
   the installed viewer's bundle and a committed spinner export. The specs
   modified are `framework-identity`, `viewer-distribution`,
   `user-documentation` (one requirement renamed),
   `framework-contributor-guidance`, `kinematics` and `vet`; the viewer's own
   specs brought current in place. `uv lock` resolves 192 packages
   (Playwright 1.63.0, Chromium revision 1243 fetched by the orchestrator).
   The suite green on the bench's uv venv (4865 passed, 9 skipped: fifteen
   of the base's sixteen viewer skips now run, twelve tests added); the
   viewer's tests from its directory, 250 passed and 2 skipped, 252 passed
   with the Curta's builds, run by a step of CI's test job after
   `playwright install`; the widget's from the root, 66 files, 1715 passed,
   2 skipped, typecheck and build green, run by CI's test job after one
   `npm ci`. The manual built with warnings as errors from
   `docs/requirements.txt` alone, its viewer pages reviewed in Chromium by
   the adapted `scripts/check-docs-browser.py` (12 pages, 265 local links,
   the reference's examples run). `scripts/check-dist` green on the tree
   and on a clean copy: fourteen members built, 28 archives `twine check
   --strict` passed, the viewer's wheel installed by its path and smoked
   (API 29, documents 1 to 13, the banner, the licence texts,
   `machinome-viewer describe` and `machinome viewer`); the clean copy's
   framework sdist holds 1072 entries (13 more: the twelve pages and their
   directory) and its wheel 114, the viewer's 1089 and 21; nothing
   uploaded. The originating check, on scratch copies: `machinome snapshot
   --renderer web` of a new starter through `python -m
   machinome.viewer.web capture`, the cube and its bore photographed, and
   `machinome develop` on `Vibecoded-demos/gear-shift` through the viewer's
   `serve`, the gearbox photographed in Chromium with API 29. The universe sweep on the bench: 130 rows, identical to
   `join-mechanics`'s row for row (122 ok, 2 unexpected as before, 6
   no-model); the catalogue's self-referencing link `machinome-projects`
   of 12 October 2026 made the walk recurse, so the rows read are the
   unprefixed ones and the two it cut off were swept with `--only`. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-12-join-viewer/evidence.md`.

4. `join-skills`. **Done** (12 October 2026): branch
   `v0.9-joins-join-skills`, planning commit 624aab77 on 5af14f71, ratified
   by the orchestrator's review, with the pilot's decisions of 12 October
   2026 (`release-0.9.md`, decisions 1, 2, 4 and 6); the join, the merge
   commit 36974f3e of machinome-skills' `main` rewritten by `git
   filter-repo` to its final paths (8 files, one commit, its message kept as
   written; `git log --follow` on the skill `machinome` and on the format
   tests reaches 1b86a970 of 20 September 2026). ADR-190, the machinome
   skills are a package of the set installed into assistants' directories
   by a command, accepted. The package is `packages/machinome-skills/` (the
   package directory `machinome/skills/` with `__init__.py`, `cli.py`,
   `installer.py`, the registry `tools.toml` and the two skills under
   `agent-skills/`), numbered 0.8.1 with the set, requiring
   `machinome~=0.8.1`, under the set's licence, its tests and working
   record in its directory and its specification the framework's new
   `skills-distribution`; its licence, notice and per-skill licence and
   notice files dropped at the join, the frontmatter's `license` the set's,
   the skills otherwise unchanged; its provenance in `CREDITS.md`. Its
   command `machinome skills install|update|list`, a contributor of
   `machinome.commands`, writes each skill whole with a marker in its
   frontmatter's `metadata`, refuses a skill it did not write unless
   `--force` and deletes nothing, over a registry of OpenSpec 1.6.0's 31
   tool ids and `agents`. The core gains the extra `skills`, the root's
   default group `machinome[skills]`; the seam's tests read the
   environment's contributors (the fake `fake-skills` renamed
   `fake-lessons`, the expected choices computed), and the conformance walk
   now walks a real entry. The specs modified are `cli`,
   `framework-identity`, `user-documentation` and
   `framework-contributor-guidance`; `skills-distribution` is created
   (totals + 8, ~ 3). `uv lock` resolves 189 packages. The suite green on
   the bench's uv venv (4857 passed, 24 skipped, the base's, 7562
   subtests); the package's tests from its directory, 47 passed, run by a
   step of CI's test job; the manual, with the how-to
   `howto/assistant-skills` and the command reference's section `machinome
   skills`, built with warnings as errors; `scripts/check-dist` green on the
   tree and on a clean copy: fourteen members built, 28 archives `twine
   check --strict` passed, the skills wheel installed by its path, 8 files
   installed for agents and claude and `machinome skills list` exit 0; the
   clean copy's framework sdist holds 1062 entries (1 more: the how-to) and
   its wheel 114, the skills package's 37 and 16; nothing uploaded. The
   originating check, in a scratch git project: `machinome skills install
   --tools agents,claude` wrote the eight files where Codex and Claude Code
   read them, each `SKILL.md` marked, and `update` rewrote the one copy
   marked older alone; the two assistants were not asked to list the
   skills, since either writes its session record under the user's home.
   No universe sweep: no project repository reaches the package, its
   module or its command (0 files on 12 October 2026), and no module of the
   core changed. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-12-join-skills/evidence.md`.
