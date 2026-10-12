# Machinome 0.9.0: the decisions and the road to the release

Campaign plan, provisional. Written 12 October 2026 from the workspace
conversation of that day, in which the pilot settled what 0.9.0 contains
and how it is released; the plan the remaining cycles are cut from.
Working record, not a promise: nothing here is ratified, no ADR is
accepted by it, and a baseline spec or an accepted ADR outranks every
sentence. Written on the line `v0.9-joins` at 484a528f, after the joins
of machinome-freecad and machinome-mechanics and the integration of
`digest-only-what-the-node-names`, with the viewer's join and the command
seam on their benches. `monorepo-0.9.md` and `joins-0.9.md` beside this
note still hold for the layout and the method of a join; from the viewer's
join on, this note's list of cycles supersedes theirs.

## What 0.9.0 is (pilot, 12 October 2026)

One repository of released packages under one licence,
GPL-2.0-or-later OR CERN-OHL-S-2.0+ at the recipient's choice, stated
once at the root; one version for every package of the set; one command,
`machinome`, to which the packages contribute their subcommands; one
manual, inside the framework's package; and one release: every archive
built, checked and smoked into one folder and uploaded in one command.

## Decided (pilot, 12 October 2026)

1. **Addresses.** Every package of the set takes the dotted address, as the
   norm of 2 October 2026 says: `machinome.mechanics` (done),
   `machinome.viewer.web` (the address the `viewer-seam` outline of
   4 October 2026 gives the browser viewer, so the seam's cycle renames
   nothing of it), `machinome.movie`, `machinome.skills`,
   `machinome.studio`. No module of a former name is provided and no
   alias; the project repositories that import a former name move, as the
   26 importers of the mechanics helpers did.
2. **Versions.** mechanics kept its own version at its join (ADR-187).
   The bump to 0.9.0 is the last step of the road: everything is bumped to
   0.9.0 in one bump from the root's `.bumpversion.cfg`, mechanics and the
   skills included, which ends the own-version exception; one tag,
   `v0.9.0`, marks the set, the viewer's prefixed tags being history. The
   number is declared in one place, `current_version` of
   `.bumpversion.cfg`; the manifests, the pins and the manual's release
   facts are copies the release-records test holds.
3. **Distribution.** pip only. Nothing of the set is published on npm: the
   root `package.json` workspace founded at the viewer's join is a build
   arrangement, its members private, the built bundles carried by the
   wheels.
4. **One command.** `machinome` learns its subcommands from the installed
   packages through the entry-point group `machinome.commands` (cycle
   `commands-contributed-by-packages`, ADR-189): the movie is the first
   contributor, the skills the second, the studio the third. The viewer's
   command becomes a subcommand in a cycle of its own before the bump:
   the framework's `viewer` command grows the viewer's verbs and
   dispatches to the installed provider through the seam, since a
   framework name is never taken by a contributor. Unifying anything
   beyond that is deferred.
5. **The videomaker** joins as one member, `machinome-movie` at
   `packages/machinome-movie/`, the Node side inside the portion beside
   the Python one. Its command is `machinome movie` with the verbs
   `list`, `evaluate`, `watch`, `check`, `speech`, `preview`, `render`,
   `build`, `live`, `review` and `setup`. There is no viewer option: the
   verbs take the installed viewer's bundle through the entry point, as
   `machinome develop` does, and the studio the same. A source is an
   episode document, a movie document, or a project and a movie name,
   evaluated first. Node is the user's, 22 or newer, found on the PATH or
   named by `MACHINOME_NODE`; `machinome movie setup` installs the Node
   dependencies into the package's own JavaScript directory in the
   environment that owns it, never into a cache, and `setup --remove`
   deletes them; Playwright's Chromium stays the documented second step.
   The join takes the videomaker's main and its two finished branches,
   `live-audio-mixer` and `record-review`, fetched from the rewritten
   clone as `movie-live-audio-mixer` and `movie-record-review`, two
   commits each, resumed later by merging the line onto them; the stale
   `remove-progress-rule` is discarded. Its documents fold into the
   manual.
6. **The skills.** machinome-skills joins as it is: the two skills
   `machinome` and `machinome-simulate` unchanged in substance, at the
   set's version, under the set's licence, its licence files and notices
   replaced, its check script a test, its evaluation note its working
   record. Its command, `machinome skills`, follows OpenSpec's installer:
   a registry of tools with OpenSpec's ids and dot-directories plus
   `agents` for the `.agents/skills/` convention; `install --tools
   all|none|a,b,c [path]`, with a picker pre-selecting the tools detected
   in the project; `update [--force]`; `list`; `--personal` for a tool's
   user-level directory; a marker in each installed copy; `agents` the
   default when no tool is named; nothing deleted that the command did
   not write. The package is separate from the studio; the studio keeps
   its own skills and links `machinome-simulate` from the package. The
   unification of `machinome-simulate` with the workspace's
   `simulate-project`, and the derivation of the studio's API skill from
   the manual, are deferred.
7. **The studio** joins whole with its record in its directory, at the
   set's version, at the address `machinome.studio`, its command
   `machinome studio`, its manual folded, its frontend the third member of
   the npm workspace.
8. **The viewer seam.** The cycle the 4 October 2026 outline describes,
   the framework's `machinome/viewer/__init__.py` declaring the contract
   of viewers with the providers `machinome.viewer.openscad` and
   `machinome.viewer.web`, is inside 0.9 if nothing blocks it; its
   `__init__.py` must extend its path with portions, as the viewer's
   revision proved.
9. **The manual** stays inside the framework's package,
   `packages/machinome/docs/`, distributed with its source archive; the
   other products' pages fold into it. One small cycle gives every page
   the extra it needs, rendered at the top of the page by the manual's
   own extension, pinned by a test, the installation page's list derived
   from the same declarations.
10. **Release tooling.** A Makefile at the root: `version`, `bump
    VERSION=`, `sync`, `test [PKG=]`, `lint`, `docs`, `widget`, `dist`,
    `upload`, `check`, `clean`; `scripts/check-dist --out dist/vX.Y.Z`
    keeps the archives it built, checked and smoked flat in that folder,
    so `twine upload dist/vX.Y.Z/*` uploads the bytes proved; CI calls
    the same targets, the layout gate reads the Makefile's package list,
    the contributor guide names the commands. No sweep target and no
    target that chains `dist` and `upload`.
11. **The workspace** stays where it is for 0.9. A consistency cycle at
    the close brings it in step with the repository: the contract's
    status paragraphs and sections, the collaborator setup, `scripts/setup`,
    `scripts/dev-env` building the widget on a bench, the load-projects
    tables, the venv reinstalled from main, the README, the skills' paths
    and the `videomaker` skill rewritten for `machinome movie`; on a
    workspace worktree, the merge the pilot's. The move of the workspace
    into the repository is deferred past 0.9.

## Held for the pilot

The release day, which dates the histories' release sections; the tag,
the push and the upload; the Read the Docs dashboard path and the
retirement of the mechanics and viewer projects there; the fate of the
original repositories on GitHub; molejo, out of scope.

## The cycles, in order

Two cycles run beside each other when they touch different files; a
later one takes the line's head before its planning commit.

1. `join-viewer` (on its bench) and `commands-contributed-by-packages`
   (on its bench), beside each other.
2. `join-movie` and `join-skills`, beside each other, both contributors of
   the seam.
3. `release-tooling`: the Makefile, `check-dist --out`, CI on the targets.
4. `join-studio`.
5. `viewer-seam`: the contract of viewers and the OpenSCAD provider.
6. `viewer-command`: the viewer's verbs under `machinome viewer`.
7. `manual-extras`: every page states the extra it needs.
8. `workspace-consistency`, in the workspace repository.
9. The close: the suite, `scripts/check-dist` and the universe sweep at
   the line's head; the merge into local main.
10. `release-0.9.0`: the bump, the release sections dated by the pilot,
    the 0.9 section of the upgrading page, `make dist`; the tag, the push
    and the upload the pilot's.

## Empirical validation, per cycle

As `joins-0.9.md` states: the suite green on the bench's own venv; the
manual built with warnings as errors; `scripts/check-dist` green on the
tree and on a clean copy; the universe sweep identical to its base row
for row or each difference explained; the joined product's own tests
green at their new place; the originating check of each cycle.

## Progress

(entries appended at each cycle's close; the joins' entries stay in
`joins-0.9.md`)

1. `commands-contributed-by-packages`. **Done** (12 October 2026). Beside the joins (12 October 2026): the framework cycle
`commands-contributed-by-packages`, by the pilot's decision of 12 October
2026 ("one single machinome cli with packages contributing subcommands").
Branch `v0.9-joins-command-seam`, planning commit 766e78c1 on 484a528f,
ratified by the orchestrator's review with every recommendation of its
Open Questions accepted. ADR-189, a package contributes a command through
the group `machinome.commands`, accepted; ADR-024 and ADR-168 amended. An
installed distribution declares `name = "package.module:Class"` in the
entry-point group `machinome.commands`, its class meeting the framework
commands' contract with `needs_node` declared; the command is the first
argument that is not an option, and the group is read only when it is not
a framework command, so a framework command's dispatch reads no entry
point; the guard and argparse's choices read the union; `machinome -h`
lists the contributed commands after the framework's, by name; a
framework name is never taken (one warning line), a name two packages
declare runs neither (exit 1 naming both), an absent extra is answered by
it, an unmet contract refused, other failures propagate, and the help
lists each as unavailable and exits 0. `machinome/cli.py` alone changes;
no package declares a command yet: the videomaker (`machinome movie`), the
skills package (`machinome skills`) and the studio (`machinome studio`)
register at their joins. Proved by fake distributions written into
temporary directories (`tests/contributed_commands.py`,
`tests/test_cli_contributed.py`, thirteen tests; three more in
`tests/test_cli_lazy_imports.py`, whose help oracle reads the group
empty). The specs modified are `cli` (one requirement added, two
modified) and `cli-startup-cost` (two modified). The suite green on the
bench's uv venv (4854 passed, 24 skipped, the base's, 7508 subtests; the
orchestrator's run the same); the manual built with warnings as errors.
Timings against the base, alternating runs: a framework command within
noise (`vet -h` 56 and 58 ms, `build -h` 231 and 244 ms); an unknown name
47 and 114 ms; `machinome -h` about 70 ms slower (807 and 874 ms), 25 to
31 ms of it the group's read and the rest unexplained; the fake movie
command 112 ms. Evidence:
`packages/machinome/openspec/changes/archive/2026-10-12-commands-contributed-by-packages/evidence.md`.

2. `release-tooling`. **Done** (12 October 2026). The third cycle of the
road, by the pilot's decisions 2 and 10 of 12 October 2026. Branch
`v0.9-joins-release-tooling`, planning commit afef5c96 on 462f7119 (after
`join-movie` and the correction 675edac4 of `scripts/check-dist`'s brace),
ratified by the orchestrator's review with every recommendation of its Open
Questions accepted. ADR-192, the repository's steps are the targets of one
Makefile at its root, accepted; ADR-182 and ADR-183 amended. A root
`Makefile` with the targets `help` (the default), `version`, `bump
VERSION=`, `sync`, `test [PKG=]`, `lint`, `docs`, `widget`, `dist`, `upload`,
`check` and `clean`, declaring the sixteen packages (`PACKAGES`) and the five
with tests of their own (`TESTED`), which the layout gate holds to the tree;
the framework's own `Makefile` gone. The set's version is declared once, as
`current_version` of `.bumpversion.cfg`, whose `commit` and `tag` lines are
gone; `make bump` moves every copy, both npm locks and `uv.lock`, and never
commits or tags (proved on a copy: 25 files to 0.9.0, no commit, no tag).
`scripts/check-dist --out DIR` keeps the archives it proved; `make dist`
builds them into `dist/vX.Y.Z` from a copy of the commit, refusing a tree
that differs from it; `make upload` alone runs twine. CI's jobs call the
targets. By the orchestrator's decision at the checkpoint,
`packages/machinome/.gitignore` ignores `/_build.lock`, the builder's lock
the core's suite leaves beside the package directory, which on a clone made
`make dist`'s guard refuse after `make test` (which test leaves it was not
identified). Counts: `make test` on the bench, the core 4909 passed and 9
skipped (the line's 4894 and this change's fifteen tests), the mechanics
204, the skills 47, the viewer's widget 1715 tests and its Python 252 passed
(2 skipped), the movie 322 and its Node `pure` and `stage` 329, in 21 min 29
s; `make check`, 32 archives per run, 32 PASSED each, the core's sdist 1146
entries from the tree and 1083 from the clean copy, 7 min 15 s; the dry
release rehearsal on a one-commit copy, `make sync`, `make test
PKG=machinome` (4909 passed, 9 skipped), `make docs` and `make dist`: 32
archives in `dist/v0.8.1`, `twine check --strict` 32 PASSED, no entry under a
`_build` directory, `make dist` again refused, `make clean` keeping `.venv/`,
`node_modules/` and `dist/v0.8.1/`. Nothing uploaded, tagged or pushed.
Evidence:
`packages/machinome/openspec/changes/archive/2026-10-12-release-tooling/evidence.md`.

3. `viewer-seam`. **Done** (12 October 2026). The pilot's eighth decision
of 12 October 2026, on the outline of 4 October 2026. Branch
`v0.9-joins-viewer-seam`, planning commit 1f0c1cb0 on 01981a3f (after
`release-tooling` and `join-studio`), ratified by the orchestrator's review
with every recommendation of its Open Questions accepted, Decision 13 (the
manual's build takes the repository's viewer) as a reversible working
assumption flagged to the pilot. ADR-194, viewers are providers behind one
seam, chosen by name, accepted; it supersedes ADR-068's lookup and process
boundary and ADR-188's "The seam is unchanged", and amends ADR-179 (the
renderer column removed), ADR-183 and ADR-191. The core's
`machinome/viewer/__init__.py` declares `CONTRACT = 1`, the operations
`present`, `capture`, `serve` and `embed` as Protocols, the viewers it knows
with their extras and each operation's default; a viewer is resolved at
`machinome.viewer.<name>` and refused absent by its extra, unknown, of
another contract or lacking an operation, never substituted. The web viewer
`machinome.viewer.web` serves in a thread of the command's process and
captures there, its staging moved from the core's `machinome/viewers/`,
which is gone with the entry point `machinome.viewer` and every run of
`python -m machinome.viewer.web` by the framework; the OpenSCAD viewer is
`machinome.viewer.openscad`, the new distribution
`machinome-viewer-openscad` (eighteen members), installed by
`viewer-openscad`, `openscad` and `solid2`. `machinome snapshot`, `develop`
and `export` take `--viewer`, else the project's `[tool.machinome]
viewer`, else their default; `--renderer` is refused naming `--viewer`;
`machinome vet` denies `machinome.viewer`. Found on the way and kept: the
web package keeps its operation `capture` from being replaced by its
submodule of the same name, the OpenSCAD viewer loads its node package
through the table first, the session binds its port before its thread
starts (a taken port is one line and exit 1), and CI's docs job runs `make
widget` before `make docs`. The specs: `viewer-seam` created; `web-snapshot`,
`cli`, `viewer-distribution` (two requirements removed),
`kernel-extras`, `framework-identity`, `openscad-node`,
`openscad-dependency`, `build-pipeline`,
`backend-neutral-materialization`, `cli-startup-cost`,
`movie-distribution`, `vet`, `user-documentation` and `release-tooling`
modified; 51 specs valid. The lock 201 packages. Counts: the core 4985
passed, 9 skipped (the base's 4916 and 69 more); the viewer 259 passed, 2
skipped; the movie 322; the studio 485 passed, 24 skipped; `make docs` with
the bundle built by npm; `make check`, 36 archives on the tree and 36 on
the clean copy. The originating check: the manual's "Photograph" stills
through each viewer byte-identical to the base's (0 differing pixels of
2073600, four images), the web still in the command's process, a project's
`viewer = "web"` taking the web image; `machinome develop` on a copy of
`Vibecoded-demos/gear-shift` reloading the open page on its socket where the
base closed it. The projects' move: `--renderer` to `--viewer` in the live
instructions of 19 of 63 repositories (28 files, one commit each), recorded
evidence untouched; the universe sweep after it identical to the movie
cycle's row for row (130 rows, 122 ok, 2 unexpected as before). Nothing
pushed. Evidence:
`packages/machinome/openspec/changes/archive/2026-10-12-viewer-seam/evidence.md`.

4. `viewer-command`. **Done** (12 October 2026). The pilot's fourth decision
of 12 October 2026: the framework's `viewer` command grows the viewer's
verbs and dispatches through the seam, a framework name being never taken by
a contributor (ADR-189); no alias. Branch `v0.9-joins-viewer-command`,
planning commit 4c68d02c on cca33986 (after `viewer-seam`), ratified by the
orchestrator's review with every recommendation of its Open Questions
accepted. ADR-196, the viewer's verbs are the framework's `viewer` command,
accepted; it amends ADR-188 (the console script) and ADR-194 (the clause
keeping the viewer's command, and the capture request). `machinome viewer
describe`, `serve --build-dir DIR [--port N]` and `capture STAGING -o PNG`
with the former command's options ask the viewer `--viewer` names, else
`web`, reading no project manifest, each requiring its operation (`embed`,
`serve`, `capture` of a published document) and refusing by name a viewer
that lacks it; `machinome viewer` with no verb prints the same report, byte
for byte. The seam's `CaptureRequest` names its camera by the notation or by
its parts (`eye`, `target`, `up`, `fov`), never both, and the web viewer
takes the parts as given. The console script `machinome-viewer` is removed,
serve's three ignored frontend flags with it, and `python -m
machinome.viewer.web` runs `machinome viewer` with the same parser. Found on
the way and fixed in the cycle: since the seam's session binds its port
itself, uvicorn no longer printed its address; the session now prints
`Serving at http://0.0.0.0:PORT (Ctrl+C to stop)` once it listens, for
`machinome viewer serve` and `machinome develop` alike. The specs: `cli`,
`cli-startup-cost`, `viewer-distribution`, `framework-identity` and
`user-documentation` modified, `viewer-seam` modified with one requirement
added; 51 specs valid; the viewer's own specs, changelog and OpenSpec
configuration brought current in place. Counts: the core 5023 passed, 9
skipped (the seam's 4985 and 38 more); the viewer 252 passed, 2 skipped (8
tests moved to the core's command test, 1 removed, 2 added for the
address); the movie 322; the studio 485 passed, 24 skipped; `make docs`;
`make check`, 36 archives on the tree and 36 on the clean copy, the viewer
row running the three commands and finding no executable of its own. The
originating check: `machinome viewer capture` of the tutorial's carry pose
with five option sets byte-identical to `machinome-viewer capture`'s (0
differing pixels each); `machinome viewer serve` of a copy of
`Vibecoded-demos/gear-shift` serving the same page, document and greeting,
Ctrl-C exit 0, SIGTERM exit -15, a taken port exit 1 with one `Error:` line;
the studio reading the report through the command. The projects' move: the
Curta's eleven browser tools under `simulation/tools/`, which ran
`[sys.executable, '-m', 'machinome_viewer', 'describe']`, run `'-m',
'machinome.viewer.web', 'describe'`, the module form this change keeps for
tools, one commit f4a7005 in that repository on 12 October 2026 ("Ask the
viewer's report through machinome.viewer.web"), nothing of the former
module left under its tools; no other project ran the script or the module.
The site's intake (three files in the site's repository) is held for the
pilot; no universe sweep, since nothing a project imports moved. Nothing
pushed. Evidence:
`packages/machinome/openspec/changes/archive/2026-10-12-viewer-command/evidence.md`.
