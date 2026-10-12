## Context

The third cycle of the road to Machinome 0.9.0
(`workflow/ongoing/release-0.9.md` at the repository root, "The cycles, in
order", 3), cut from the line `v0.9-joins` at 40087800, whose head holds the
viewer's join (the root npm workspace, ADR-188) and the skills' join
(ADR-190), on the bench `machinome/WTs/v0.9-joins-release-tooling`. The
movie's join, `join-movie`, is implemented on its own bench meanwhile and lands
on the line before this change's planning commit; its ratified design
(Decisions 6, 10, 11 and 13: the second npm member, its tracked member lock,
its Node test projects, its `check-dist` row) is read here, and where this
design names the movie it means the movie as `join-movie` lands it.

The pilot's decisions of 12 October 2026 bind the cycle and are not reopened.
Decision 2: the bump to 0.9.0 is the road's last step, one bump from the
root's `.bumpversion.cfg`; the number is declared in one place,
`current_version` of that file, and the manifests, the pins and the manual's
release facts are copies the release-records test holds. Decision 10: a
Makefile at the root with the targets `version`, `bump VERSION=`, `sync`,
`test [PKG=]`, `lint`, `docs`, `widget`, `dist`, `upload`, `check`, `clean`;
`scripts/check-dist --out dist/vX.Y.Z` keeps the archives it built, checked
and smoked flat in that folder, so `twine upload dist/vX.Y.Z/*` uploads the
bytes proved; CI calls the same targets, the layout gate reads the Makefile's
package list, the contributor guide names the commands; no sweep target and no
target that chains `dist` and `upload`. This cycle leaves `current_version` at
0.8.1 and proves `make bump` on a copy.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench
at 40087800 unless marked *inferred*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C7-propose/`
(named `<scratch>` below), never in the bench, with uv 0.11.8, CPython 3.12.3
(the bench venv), GNU Make 4.3, Node 24.11.1 and npm 11.6.2, bump2version 1.0.1,
build, twine, and the OpenSpec CLI 1.6.0. `<scratch>/tree/` is a clean copy of
the tracked tree (`git ls-files -z | tar --null -T - -cf - | tar -x`, links
kept); `<scratch>/bump/` the same made a Git repository of one commit;
`<scratch>/rehearsal/` the same with the prototype of this design applied
(the Makefile of Decision 1 without the movie's lines, `scripts/check-dist` of
Decision 10, `.bumpversion.cfg` of Decision 3, `.gitignore`'s
`/.docs-venv/`, `packages/machinome/Makefile` removed), committed once.

### What the release takes today

- **The version** is stated in twenty files: `.bumpversion.cfg`'s
  `current_version` (34 file tables, `commit = True`, `tag = True`, no
  comment, since bump2version's writer drops comments: `cut-the-engines`,
  Decision 5), the fourteen manifests numbered with the set and their `~=`
  pins, the core's `__init__.py`, `docs/conf.py`'s `release` and
  `viewer_version`, `machinome/vet/universe.toml`, the viewer's `__init__.py`
  and its widget's `package.json`; and in two locks no table names: the root
  `package-lock.json`'s entry for the widget (npm rewrites it,
  `join-viewer`'s probe 15) and `uv.lock`'s member entries. The mechanics
  helpers carry their own version, outside the cfg (ADR-187), until the
  0.9.0 bump. `tests/test_release_records.py` reads the version from the
  core's `pyproject.toml` and holds the cfg, the other manifests, the pins,
  the viewer's files and the lock entry to it.
- **The tool** is bump2version 1.0.1, in the core's `dev` extra, which the
  root's default `dev` group installs; `python -m bumpversion` runs it.
  `CONTRIBUTING.rst`'s Deploying section tells a maintainer to run
  `bump2version patch`, which with the cfg's two lines commits and tags.
- **The archives**: `scripts/check-dist` builds every member's sdist and wheel
  into a temporary directory outside the repository, checks them with
  `twine check --strict`, installs the wheels into a throwaway venv, smokes
  each member from its row, and deletes everything when the temporary
  directory closes; it reads no argument. The 0.8.1 archives were built by
  hand before it existed (it came with `monorepo-layout`, 6fb505ed, after
  the release commit 58a1e74f): the framework's into
  `dist/0.8.1-2026-10-10/` of the framework's checkout and the viewer's into
  its own repository's `dist/0.8.1-2026-10-10/` (two archives each), and the
  framework's checkout keeps `dist/0.7.1-2026-09-27/` and
  `dist/0.8.0-2026-10-06/` the same way.
- **The commands a contributor runs** are spelled in three places that
  differ: `CONTRIBUTING.rst` (`uv sync`, `npm ci`, `npm run build
  --workspaces`, `make test` and `make lint` from `packages/machinome/`,
  `python -m pytest` from each product's directory, `npm test --workspaces`,
  `bump2version patch`, `make release`), the framework's own
  `packages/machinome/Makefile` (a cookiecutter file: `test` is `pytest`,
  `lint` lacks the line length CI uses, `docs` runs `sphinx-apidoc` and
  opens a browser, `release` runs `dist` then `twine upload dist/*`), and CI's
  workflow (every job's commands written out). `tests/test_repository_layout.py`
  lists `Makefile` among the framework's entries that must not be at the
  root.
- **CI** (`.github/workflows/python-app.yml`): `lint` (black and flake8 from
  `packages/machinome`, both `continue-on-error`), `test` (`npm ci`, the
  widget's typecheck, tests and build at the root, `coverage run --source
  machinome -m pytest` and `coverage report -m`, then pytest from the
  mechanics', the viewer's (after `playwright install --with-deps chromium`)
  and the skills' directories), `browser-snapshot` (`npm ci`, the bundle,
  Chromium, one end-to-end test), `docs` (setup-python, `pip install -r
  docs/requirements.txt`, `python -m sphinx -b html -W docs docs/_build`),
  `dist` (setup-python, `pip install build twine`, Node, `scripts/check-dist`)
  and, on a tag, `build` (`make dist` from `packages/machinome`, the
  framework's Makefile, then `gh release create` with `./dist/*`). Every job
  but `dist` runs from `packages/machinome` by default; the layout test holds
  that, the test job's widget steps before the suite and its product steps,
  and the dist job's `scripts/check-dist`; `tests/test_docs_exports.py`
  holds the docs job to installing `docs/requirements.txt` alone and building
  with `-W`; `tests/test_kernel_extras.py` holds `lint`, `test` and
  `browser-snapshot` to one `uv sync --locked` step at the root.

### Probes

1. **`scripts/check-dist` at the line's head does not parse.**
   `python3 -c "import ast; ast.parse(...)"` on 40087800's
   `scripts/check-dist`: `SyntaxError: '{' was never closed` at `SMOKES = {`
   (line 240). The same file at 8315e65c (the skills' implementation) and at
   78a584df (the viewer's integration) parses. The merge 40087800 kept the
   viewer's row and the skills' row side by side but lost the line `    },`
   that closed the viewer's row after its `'commands'` line (line 659), so the
   skills' row became a key of the viewer's dict and `SMOKES` never closes.
   Every run of the script on the line, the CI's `dist` job included, fails
   before it reads a member. Restoring the one line makes it parse (the scratch
   copies below).
2. **`--out`, prototyped** in `<scratch>/tree/scripts/check-dist` (the
   diff is `<scratch>/check-dist-out.diff`, 68 lines: the brace,
   `import argparse`, `keep_out`, `keep`, `main(argv=None)` parsing `--out
   DIR`, and the call to `keep` inside the temporary directory after the last
   smoke). A folder holding one file: `check-dist failed: <folder> exists and
   is not empty; ...`, exit 1, before any build. A regular file at the path:
   the same refusal (its wording is corrected in Decision 10). `--help`:
   the usage line `check-dist [-h] [--out DIR]`. On the clean copy, with the
   bench venv's interpreter, `--out <scratch>/dist/v0.8.1`: fifteen members
   built (the core, two engines, nine node packages, mechanics, skills,
   viewer), every smoke passed, "30 archives kept", exit 0, 3 min 12 s wall,
   530 MB peak; the folder holds 30 archives flat (`machinome-0.8.1.tar.gz`
   and its wheel through `machinome_viewer-0.8.1-py3-none-any.whl`, and
   `machinome_mechanics-0.1.0.*`); `twine check --strict <folder>/*`: 30
   PASSED. The brief expected 28 (fourteen members); the line has fifteen
   since `join-freecad`, and sixteen (32 archives) once the movie lands.
3. **The bump on a copy** (`<scratch>/bump/`, a Git repository of the tracked
   files). `python -m bumpversion --no-commit --no-tag --new-version 0.9.0
   patch`: exit 0; 20 files, 55 lines (15 manifest versions, 13
   `machinome~=` pins, 6 `machinome-engine-brep~=` pins, the other
   members' pins, two `__version__`, `release`, `viewer_version`, the
   universe's version, the widget's `"version"`, `current_version`); no
   commit, no tag; the cfg keeps its `commit = True` and `tag = True`. What
   still says 0.8.1 in a tracked `.toml`, `.json`, `.py` or `.cfg`:
   `context7.json` (2), the core's identity test (1) and the viewer's
   documentation test (4), which are the release cycle's records, and
   `package-lock.json` (1). Then `npm install --package-lock-only --no-audit
   --no-fund` at the copy's root: "up to date", 0.3 s, one line of the lock
   (the widget's entry), no `node_modules/` written; then `uv lock`: "Updated
   machinome v0.8.1 -> v0.9.0" for each of the fourteen numbered members, 28
   lines of `uv.lock`. Twenty-two files in all.
   With the cfg's two lines removed and no flag given,
   `bumpversion --new-version 0.9.0 patch`: exit 0, the same 20 files, no
   commit, no tag; the cfg rewritten as `[bumpversion]` and
   `current_version = 0.9.0`. On a copy whose tracked files have changes:
   exit 1, a `WorkingDirectoryIsDirtyException` traceback listing them; with
   only an untracked file: it proceeds.
   The movie's member lock: `packages/machinome-movie/machinome/movie/js/package.json`
   and its `package-lock.json` copied from the movie's bench into
   `<scratch>/movie-lock/`, the manifest's version set to 0.9.0, `npm install
   --package-lock-only --no-audit --no-fund` there: "up to date", 0.35 s, the
   lock's two root entries at 0.9.0 and nothing else changed, no
   `node_modules/` written (`join-movie`'s probe 10 regenerates it the same
   way).
4. **The suites by package**, on the bench venv: `python -m pytest` from
   `packages/machinome-mechanics` 204 passed in 7.0 s, from
   `packages/machinome-skills` 47 passed in 2.5 s, from
   `packages/machinome-viewer` 250 passed, 2 skipped, 185 subtests in 269 s
   (Chromium build 1243 in `~/.cache/ms-playwright`); the widget at the root
   by `--workspace packages/machinome-viewer/machinome/viewer/web/widget`:
   `npm run typecheck` 2.5 s, `npm test` 65 files and 1715 tests passed (one
   file and two tests skipped) in 59 s, `npm run build` 0.5 s; `npm run build
   --workspaces --if-present` builds the widget's bundle alone (the movie's
   `js` has only a `test` script, read on the movie's bench). The core's
   suite was not run by this proposer; the line's last count is the command
   seam's, 4854 passed, 24 skipped, 7508 subtests (its evidence).
5. **The manual from its requirements alone**: `uv venv --python 3.12
   <tree>/.docs-venv` and `uv pip install --python <tree>/.docs-venv/bin/python
   -r packages/machinome/docs/requirements.txt`: 0.9 s from uv's cache
   (Sphinx 9.1.0, the published `machinome-viewer` 0.8.0); then from
   `<tree>/packages/machinome`, `python -m sphinx -b html -W -q docs
   docs/_build/html`: exit 0, 9.3 s, 82 pages. uv's venv has no pip;
   `uv pip install --python` installs into it.
6. **The lint CI runs**, from `packages/machinome` with the glob expanded by a
   shell: `flake8 --max-line-length=89 machinome tests ../machinome-*/machinome`
   1515 lines, exit 1; `black --check` over the same: 549 files would be
   reformatted, 198 left unchanged, one fails to parse
   (`tests/vet_projects/unparseable/sim/broken.py`, a deliberate fixture),
   exit 123. Both steps are `continue-on-error` in CI today. Through `env -C`
   the glob is not expanded and black refuses the literal path.
7. **The rehearsal** (`<scratch>/rehearsal/`, PATH holding uv and npm):
   - `make`: twelve lines, one per target (`help` first).
   - `make version`: `0.8.1`.
   - `make test PKG=machinome-engine-brep`: "make test:
     machinome-engine-brep keeps no tests of its own; the core's suite tests
     it: make test PKG=machinome", make's exit 2. `PKG=nope`: "nope is not a
     package; the packages are ..." (the fifteen), exit 2.
   - `make bump`: "name the version", exit 2; `make bump VERSION=0.8.1`:
     "the set is at 0.8.1 already", exit 2.
   - `make upload` with no `dist/v0.8.1`: "no archives in dist/v0.8.1; make
     dist builds them", exit 2; `make -n upload` prints `<venv>/bin/python -m
     twine upload dist/v0.8.1/*` and runs nothing. (No upload was run, ever.)
   - `make sync`: 6.3 s from warm caches: uv "Resolved 193 packages",
     "Installed 184 packages", fifteen `__editable__` files; `npm ci` "added
     101 packages"; `playwright install chromium` (already cached). `git
     status --porcelain`: empty.
   - `make lint`: 14.1 s, both tools run, black's and flake8's counts of
     probe 6, make's exit 2.
   - `make test PKG=machinome-skills`: 47 passed, 3.3 s;
     `PKG=machinome-mechanics`: 204 passed, 2.7 s.
   - `make docs`: venv made, requirements installed, the build with `-W -E`:
     exit 0, 10.1 s.
   - `make widget`: `npm ci` and the bundle, 2.1 s.
   - `make dist` with an untracked `stray.txt`: "the tree differs from its
     commit; commit or remove: ?? stray.txt", exit 2. Without it (the first
     prototype, on the checkout): 206 s,
     "30 archives kept in .../rehearsal/dist/v0.8.1", exit 0; `twine check
     --strict dist/v0.8.1/*`: 30 PASSED; `git status --porcelain`: empty (the
     folder is ignored by the root's `/dist/`); `make dist` again: check-dist's
     refusal of the non-empty folder, exit 2.
   - `make check`: 414 s, both runs "Every distribution built, checked,
     installed and smoked", exit 0; the copy's temporary directory removed.
     The tree's core sdist: 1081 entries; the copy's: 1075 (probe 9).
   - `make bump VERSION=0.9.0` (after a commit, the tree clean): 1.25 s,
     bump2version, npm ("up to date"), `uv lock` (fourteen members
     "Updated v0.8.1 -> v0.9.0"), `git diff --stat` "22 files changed, 70
     insertions(+), 70 deletions(-)" and the 22 files listed; `git log`
     unchanged, no tag; `make version`: 0.9.0.
   - `make test` (the design's Makefile without the movie's lines, committed
     as the rehearsal's third commit): the widget's bundle, then the core's
     suite, `1 failed, 4884 passed, 9 skipped` in 716 s, 720 s in all, make's
     exit 2, and the mechanics', skills' and viewer's tests not run (the
     stop at the first failure). The failure is the base's layout test,
     `test_the_framework_s_entries_are_not`, "Makefile is at the repository
     root": the gate this change rewrites (Decision 12), red as expected.
     The skips differ from the command seam's 24 on its bench venv; not
     investigated here.
   - `make clean`: `.docs-venv/`, `packages/machinome/docs/_build/` and the
     widget's `dist/` gone; `.venv/`, `node_modules/`, `dist/v0.8.1/` and the
     fifteen `*.egg-info` kept. `git check-ignore -q --no-index` answers each
     cleaned path as ignored when it is asked as a directory (a trailing
     slash), and not otherwise, since the patterns end in `/`.
8. **The gate's parse**, prototyped (`<scratch>/parse_probe.py`) on the
   rehearsal's Makefile: the continued lines joined, `PACKAGES` read from its
   one `:=` assignment equals the sorted directories of `packages/` (15);
   `TESTED` read; the twelve targets with a `## ` help line found, each in
   `.PHONY`; `upload` has no prerequisite; only `upload`'s recipe holds
   `twine upload`; no rule names `dist` or `upload` as a prerequisite; the
   `docs` recipe read. No `make` process is needed.
9. **Ignored build directories enter the core's sdist.** In the rehearsal,
   `make dist` run on the checkout itself (the first prototype, before the
   copy of Decision 7) after `make docs`: the core's sdist held 1081 entries
   where the clean copy's held 1075, the six more being
   `docs/_build/html/_static/` and three PNG files, carried by the
   `MANIFEST.in` line `recursive-include docs ... *.png`; `git status
   --porcelain` was empty, since `_build/` is ignored. The release folders
   show the same: `machinome-0.7.1.tar.gz` kept in `dist/0.7.1-2026-09-27/` of
   the framework's checkout, built by hand from a checkout, holds 1145
   entries, 10 under `docs/_build/` and 246 under `tests/_build*` (244 of the
   suite's meta-project build `tests/_build_meta/` and two lock files, carried
   by `recursive-include tests *`); the 0.7.0, 0.8.0 and 0.8.1 sdists kept
   there hold none. With `make dist` building from `git archive HEAD`
   (Decision 7; the rehearsal's second commit, the manual's build still in
   the checkout): 211 s, "in a copy of the commit cd57d86", 30 archives kept,
   the core's sdist 1075 entries, no entry under any `_build*/` in any of the
   30 (`tar tzf` and `unzip -l`), `twine check --strict`: 30 PASSED, no
   `machinome-dist-*` directory left, `git status --porcelain` empty.

## Goals / Non-Goals

**Goals:**

- One command per step, declared once, at the root: the steps a contributor,
  CI and the pilot run are the Makefile's targets.
- The version declared in one place, moved in one command that commits
  nothing and tags nothing.
- The archives uploaded are the archives built, checked, installed and smoked,
  kept in one folder per release.
- The gates hold the Makefile to the tree: every package listed, every
  product's tests run, no target that uploads what it built, nothing tracked
  cleaned.

**Non-Goals:**

- The bump to 0.9.0, the release sections, the tag, the push and the upload:
  the road's last cycle and the pilot.
- A sweep target, a browser-snapshot target, a coverage target.
- The workspace's `scripts/setup` and `scripts/dev-env`, the workspace
  consistency cycle's.
- The Read the Docs configuration, the manual's pages, any module of any
  package.
- Making the lint pass: 1515 flake8 lines and 549 unformatted files stay as
  CI has tolerated them.

## Decisions

### 1. One Makefile at the root; the framework's goes

`Makefile` at the repository root, verbatim but where the implementation's
evidence corrects a line (each correction recorded):

```make
# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
#
# The repository's steps, one command each (change `release-tooling`,
# ADR-192). Run from the repository root, after `make sync`; `make` alone
# lists the targets. uv and npm are found on the PATH.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
# One step at a time, even under -j: the suites share their build
# directories, and `make test` stops at the first failure.
.NOTPARALLEL:
MAKEFLAGS += --no-builtin-rules --no-builtin-variables

UV := uv
NPM := npm
PYTHON := $(CURDIR)/.venv/bin/python
# The workspace's commands first, as an activated venv puts them: the suites
# run `machinome`, `playwright` and the venv's tools as subprocesses.
export PATH := $(CURDIR)/.venv/bin:$(PATH)
DOCS_VENV := .docs-venv

# Every distribution of the repository, by its directory under packages/;
# the layout test holds this list to the directories there.
PACKAGES := \
	machinome \
	machinome-engine-brep \
	machinome-engine-mesh \
	machinome-mechanics \
	machinome-movie \
	machinome-node-build123d \
	machinome-node-cadquery \
	machinome-node-freecad \
	machinome-node-jscad \
	machinome-node-molejo \
	machinome-node-openscad \
	machinome-node-solid2 \
	machinome-node-step \
	machinome-node-stl \
	machinome-skills \
	machinome-viewer

# The packages with tests of their own, in the order `make test` runs them;
# the core's suite tests the extension packages.
TESTED := machinome machinome-mechanics machinome-skills machinome-viewer \
	machinome-movie
UNTESTED := $(filter-out $(TESTED),$(PACKAGES))

# The npm member that builds the browser viewer's bundle, and the movie's
# Node side, whose tests CI runs by project.
WIDGET := packages/machinome-viewer/machinome/viewer/web/widget
MOVIE_JS := packages/machinome-movie/machinome/movie/js

# The npm members that keep a lock of their own, which npm reads only
# outside the workspace.
MEMBER_LOCKS := $(MOVIE_JS)

# The set's version, declared once: `current_version` of .bumpversion.cfg.
CURRENT := $(shell sed -n 's/^current_version = //p' .bumpversion.cfg)
RELEASE := dist/v$(CURRENT)

# What the targets write and `make clean` removes: never .venv/, an npm
# install, a release folder under dist/ or a tracked file.
CLEAN := $(DOCS_VENV) packages/machinome/docs/_build packages/*/build \
	$(WIDGET)/dist

.PHONY: help version bump sync test lint docs widget dist upload check clean \
	bundle $(addprefix test-,$(PACKAGES))

help: ## List the targets
	@awk -F ':.*## ' '/^[a-z]+:.*## / {printf "  make %-8s %s\n", $$1, $$2}' $(firstword $(MAKEFILE_LIST))

version: ## Print the set's version, current_version of .bumpversion.cfg
	@echo $(CURRENT)

bump: ## Move the set to VERSION=X.Y.Z: every copy and every lock; no commit, no tag
	@test -n "$(VERSION)" || { echo 'make bump: name the version: make bump VERSION=X.Y.Z' >&2; exit 2; }
	@test "$(VERSION)" != "$(CURRENT)" || { echo 'make bump: the set is at $(CURRENT) already' >&2; exit 2; }
	@git diff --quiet HEAD || { echo 'make bump: the tracked files have changes; commit them first:' >&2; git status --short --untracked-files=no >&2; exit 1; }
	$(PYTHON) -m bumpversion --no-commit --no-tag --new-version $(VERSION) patch
	$(NPM) install --package-lock-only --no-audit --no-fund
	@for member in $(MEMBER_LOCKS); do \
	  copy=$$(mktemp -d); \
	  cp $$member/package.json $$member/package-lock.json $$copy/; \
	  (cd $$copy && $(NPM) install --package-lock-only --no-audit --no-fund); \
	  cp $$copy/package-lock.json $$member/package-lock.json; rm -rf $$copy; \
	done
	$(UV) lock
	@git diff --stat
	@git status --short

sync: ## Install the workspace from its locks: every package editable, the npm members, Chromium
	@command -v $(UV) >/dev/null || { echo 'make sync: uv is not on the PATH' >&2; exit 1; }
	@command -v $(NPM) >/dev/null || { echo 'make sync: npm is not on the PATH; install Node.js 22 or newer' >&2; exit 1; }
	$(UV) sync --python 3.12
	$(NPM) ci --no-audit --no-fund
	playwright install chromium

test: $(if $(PKG),test-$(PKG),$(addprefix test-,$(TESTED))) ## Run the tests of PKG=<package>, or of every package with tests, stopping at the first failure

bundle:
	$(NPM) run build --workspace $(WIDGET)

test-machinome: bundle
	cd packages/machinome && $(PYTHON) -m pytest

test-machinome-mechanics test-machinome-skills:
	cd packages/$(@:test-%=%) && $(PYTHON) -m pytest

test-machinome-viewer:
	$(NPM) run typecheck --workspace $(WIDGET)
	$(NPM) test --workspace $(WIDGET)
	$(NPM) run build --workspace $(WIDGET)
	cd packages/machinome-viewer && $(PYTHON) -m pytest

test-machinome-movie:
	cd packages/machinome-movie && $(PYTHON) -m pytest
	$(NPM) test --workspace $(MOVIE_JS) -- --project pure --project stage

$(addprefix test-,$(UNTESTED)):
	@echo 'make test: $(@:test-%=%) keeps no tests of its own; the core'"'"'s suite tests it: make test PKG=machinome' >&2; exit 2

test-%:
	@echo 'make test: $* is not a package; the packages are $(PACKAGES)' >&2; exit 2

lint: ## Check the style of every package's sources with black and flake8, as CI does
	@status=0; cd packages/machinome; \
	$(PYTHON) -m black --check machinome tests ../machinome-*/machinome || status=1; \
	$(PYTHON) -m flake8 --max-line-length=89 machinome tests ../machinome-*/machinome || status=1; \
	exit $$status

docs: ## Build the manual with warnings as errors, from docs/requirements.txt alone, into packages/machinome/docs/_build/html
	test -x $(DOCS_VENV)/bin/python || $(UV) venv --python 3.12 $(DOCS_VENV)
	$(UV) pip install --python $(DOCS_VENV)/bin/python -r packages/machinome/docs/requirements.txt
	cd packages/machinome && $(CURDIR)/$(DOCS_VENV)/bin/python -m sphinx -b html -W -E docs docs/_build/html

widget: ## Install the npm workspace from its lock and build its bundles
	$(NPM) ci --no-audit --no-fund
	$(NPM) run build --workspaces --if-present

dist: ## Build, check and smoke every archive of the commit into dist/vX.Y.Z; upload nothing
	@git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo 'make dist: a release is built from a Git checkout' >&2; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo 'make dist: the tree differs from its commit; commit or remove:' >&2; git status --short >&2; exit 1; }
	@copy=$$(mktemp -d "$${TMPDIR:-/tmp}/machinome-dist-XXXXXX"); \
	trap 'rm -rf "$$copy"' EXIT; \
	git archive HEAD | tar -x -C "$$copy"; \
	echo "$$ scripts/check-dist --out $(RELEASE), in a copy of the commit $$(git rev-parse --short HEAD)"; \
	cd "$$copy" && $(PYTHON) scripts/check-dist --out $(CURDIR)/$(RELEASE)

upload: ## Upload dist/vX.Y.Z to PyPI with twine; run by no other target
	@test -n "$$(ls -A $(RELEASE) 2>/dev/null)" || { echo 'make upload: no archives in $(RELEASE); make dist builds them' >&2; exit 1; }
	$(PYTHON) -m twine upload $(RELEASE)/*

check: ## Build, check and smoke every archive from the tree and from a clean copy of its tracked files; keep nothing
	$(PYTHON) scripts/check-dist
	@copy=$$(mktemp -d "$${TMPDIR:-/tmp}/machinome-check-XXXXXX"); \
	trap 'rm -rf "$$copy"' EXIT; \
	git ls-files -z | tar --null -T - -cf - | tar -x -C "$$copy"; \
	echo "$$ scripts/check-dist in a clean copy of the tracked files, $$copy"; \
	cd "$$copy" && $(PYTHON) scripts/check-dist

clean: ## Remove what the targets wrote: the docs venv, the manual's build, build scratch, the bundle
	rm -rf $(CLEAN)
```

The lines that name `machinome-movie`, `MOVIE_JS`, `MEMBER_LOCKS`'s value and
`test-machinome-movie` are the movie as `join-movie` lands it; were the movie
not on the line when this change is implemented, they are left out and the
movie's join adds them (the gate of Decision 12 fails naming the directory
until it does). The rehearsal ran the file without them (probe 7).

The shell is bash, for `pipefail`; `ubuntu-latest`
and every Linux and macOS development machine have it. `uv` and `npm` are
named, not located: `make sync` refuses with one line when either is absent;
the other targets meet the shell's "command not found". The venv's tools are
reached through `$(PYTHON) -m` and the exported PATH, so no target needs an
activated venv, and CI's `GITHUB_PATH` line stays harmless. Variables a reader
passes are `PKG` and `VERSION` only; `CURRENT`, not `VERSION`, is the version
read from the cfg, so `make dist VERSION=…` cannot build a folder named for
another version.

**`packages/machinome/Makefile` is removed** (`git rm`): its `release` target
chains a build and `twine upload dist/*`, the one shape decision 10 forbids,
and each of its other targets is either a root target now (`test`, `lint`,
`dist`, `docs`, `clean`) or an editor convenience nobody documents
(`servedocs`, `coverage` opening a browser, `install`). `docs/Makefile`, the
Sphinx quickstart's, stays: it runs only Sphinx and is not the release's
(*inferred*: nothing in the repository calls it; `grep -rn "docs/Makefile\|-C
docs"` finds only the removed file). `Makefile` leaves the layout test's
`FRAMEWORK_ENTRIES` (the root's is the repository's), and the test asserts
the framework's directory holds none.

### 2. The version is declared once

`current_version` of `.bumpversion.cfg` is the declaration;
`make version` prints it and every target that needs the number reads it
there (`CURRENT`). `tests/test_release_records.py`'s `released_version()`
reads it from the cfg (`configparser`, section `bumpversion`) instead of the
core's manifest, and `test_every_version_file_agrees_with_pyproject` holds
the core's `pyproject.toml` among the copies (its `statements` gain
`pyproject.toml`'s `version = "<v>"` and lose the cfg, which is now the
source); every other test of the module reads the same function, so the
viewer's files, the lock entry, the members and the pins are held to the
declaration unchanged. The module's docstring says the cfg states the
version once. A new `test_the_bump_neither_commits_nor_tags` reads the cfg's
`[bumpversion]` section: its keys are exactly `current_version` (red at the
base: `commit` and `tag`).

### 3. `make bump VERSION=X.Y.Z`

The recipe of Decision 1, in this order: refuse an empty `VERSION`, a
`VERSION` equal to the current one, and tracked files with changes (the
bump2version check would refuse them too, with a traceback, probe 3; the
recipe's own line says it in one sentence and lists them); `python -m
bumpversion --no-commit --no-tag --new-version $(VERSION) patch` (the part
argument is required by the tool and ignored with `--new-version`); `npm
install --package-lock-only` at the root (the workspace members' entries in
the root lock); the same in a temporary copy of each npm member that keeps a
lock of its own (the movie's `js`, whose lock npm reads only outside the
workspace: `join-movie`, Decision 6, probe 3 here); `uv lock` (the members'
entries in `uv.lock`); then `git diff --stat` and `git status --short`, which
list every file the bump changed. It never runs `git commit` or `git tag`.

`.bumpversion.cfg` loses `commit = True` and `tag = True` (Open Questions 1),
so a maintainer who runs the tool by hand gets the same no-commit, no-tag bump
(probe 3), and the Makefile still passes both flags, which states the intent
where the command is.

The bump moves no mechanics file: ADR-187's own version stays outside the cfg
until the 0.9.0 cycle adds its tables (the pilot's decision 2), and the
release-records test's `OWN_VERSION` keeps saying so until then.

### 4. `make sync` and `make widget`

`make sync` is what a bench needs and nothing more: `uv sync --python 3.12`
(the recipe of the benches, `scripts/dev-env`'s; CI keeps its own `uv sync
--locked` step, which fails on a stale lock), `npm ci --no-audit --no-fund`
at the root (every npm member's dependencies from the root lock), and
`playwright install chromium`, the browser the viewer's tests and the
suite's capture need (CI installs it `--with-deps`, which needs root, as its
own step). OpenSCAD, Node itself and Python 3.12 are the contributor's, named
in the guide.

`make widget` is `npm ci --no-audit --no-fund` then `npm run build
--workspaces --if-present`: every npm member's bundle from the lock, which is
the viewer's alone (the movie's `js` declares no `build` script, probe 4;
`join-movie`, Decision 6). It is the bundle step CI's `test`, `browser-snapshot`
jobs run before their tests.

### 5. `make test [PKG=]`

A per-package rule each; `make test` with no `PKG` runs `TESTED` in its order,
one after another, and make stops at the first that fails; `.NOTPARALLEL`
keeps it so under `-j`.

- `machinome`: the widget's bundle (`npm run build --workspace` the widget,
  0.5 s; the suite photographs through it), then `python -m pytest` from
  `packages/machinome`. Plain pytest: CI's `coverage run` and `coverage
  report -m` are not kept (Open Questions 9).
- `machinome-mechanics`, `machinome-skills`: `python -m pytest` from the
  package's directory.
- `machinome-viewer`: the widget's typecheck, tests and bundle by
  `--workspace` (never `--workspaces`, which would run the movie's whole Node
  suite), then `python -m pytest` from `packages/machinome-viewer`.
- `machinome-movie` (as `join-movie` lands it): `python -m pytest` from its
  directory, then `npm test --workspace <js> -- --project pure --project
  stage`, the projects CI runs (`join-movie`, Decision 10). The `slow` and
  `viewer` projects, which launch Chromium, run FFmpeg and pin pixels
  measured on one machine, stay a command of their own named in the guide
  (`npm test --workspace <js>`), since one target means one thing in CI and on
  a bench (Open Questions 10).
- An extension package: refused, naming the core's suite, which tests it
  (Open Questions 3). Any other name: refused, listing the packages.

### 6. `make lint` and `make docs`

`make lint` runs CI's two lines from `packages/machinome`, where
`setup.cfg`'s `[flake8]` (its per-file ignores name `../machinome-*` paths) is
found: black, then flake8, both always run, the target failing when either
does (probe 7). CI keeps `continue-on-error` on its step (Non-Goals).

`make docs` builds the manual as Read the Docs does, from
`packages/machinome/docs/requirements.txt` alone: the venv `.docs-venv/` at
the root, made by `uv venv --python 3.12` when absent (Open Questions 4), the
requirements installed into it by `uv pip install` at every run (0.9 s when
cached; a changed requirements file is picked up), then `python -m sphinx -b
html -W -E docs docs/_build/html` from `packages/machinome`. `-E` reads every
page at every run, so a warning of an unchanged page is reported again on a
bench's incremental build; CI's checkout is fresh either way. The output is
`packages/machinome/docs/_build/html`, which the framework's `.gitignore`
already ignores; the root's `.gitignore` gains `/.docs-venv/`. 10.1 s in the
rehearsal.

### 7. `make dist`, `make upload`, `make check`; nothing chains them

- `make dist` runs `scripts/check-dist --out dist/v$(CURRENT)` on a copy of
  the checked-out commit (`git archive HEAD` unpacked in a temporary directory
  outside the repository, removed afterwards), and refuses first a checkout
  whose `git status --porcelain` is not empty, naming the files (Open
  Questions 11). The copy is what keeps the archives the commit's: an ignored
  build directory of the checkout (the manual's `docs/_build/`, the suite's
  `tests/_build/`) is carried into the core's sdist by its `MANIFEST.in`'s
  `recursive-include docs ... *.png` and `recursive-include tests *`, which
  `git status` does not report (probe 9); the guard is what keeps the pilot
  from releasing a commit other than the one in front of them. The folder is
  `dist/v0.9.0` for 0.9.0, the tag's name, written in the checkout, where the
  root's `/dist/` ignores it.
- `make upload` runs `python -m twine upload dist/v$(CURRENT)/*` and nothing
  else; it refuses when the folder is absent or empty. It has no
  prerequisite, no other target names it, and no other recipe holds `twine
  upload`; `dist` has no dependent. The pilot runs `make dist`, reads the
  folder, then runs `make upload`.
- `make check` runs `scripts/check-dist` on the tree, then on a clean copy of
  the tracked files in a temporary directory outside the repository, removed
  when the recipe ends: the second run proves that nothing untracked is needed
  to build the set, as each cycle has done by hand (Open Questions 2). It keeps
  no archive.
- No target runs the universe sweep (`scripts/load-projects` of the
  workspace), which needs the workspace's catalogue and stays a cycle's own
  evidence.

### 8. `make clean`

Removes `CLEAN`: `.docs-venv/`, `packages/machinome/docs/_build/`, each
`packages/*/build/` and the widget's `dist/`, which the targets write. It never
removes `.venv/`, `node_modules/` or a member's, `dist/` (the release folders
are the record of what was uploaded, as `dist/0.8.1-2026-10-10/` of the
framework's checkout is today), the suites' own build directories, the
`*.egg-info` directories the editable install of `make sync` uses, or a
tracked file (Open Questions 5). The gate checks each path is ignored by Git.

### 9. The package lists

`PACKAGES` names every directory of `packages/`, written out (Open Questions
6); `TESTED` the core and every product, in the order `make test` runs them;
`UNTESTED` the rest. The layout test reads both lists from the Makefile's text
with a regular expression over its continued lines (one `:=` assignment each,
no `+=`), not by running `make`: the suite runs where make is absent (probe 8).
It holds `PACKAGES` equal to the sorted directories of `packages/`, `TESTED`
equal as a set to the core and `PRODUCTS`, each with its `test-<name>` rule,
and `PRODUCTS` stays the layout test's own table (its entries per directory).

### 10. `scripts/check-dist`: the brace, and `--out`

- The line `    },` after the viewer's row's `'commands'` line (probe 1).
  This is the merge's defect, not this change's; it is fixed here because
  every target of Decision 7 runs the script, and its red is the new test
  `test_the_script_parses` (Decision 12). The orchestrator may prefer to fix
  it on the line first (Open Questions 12).
- `main(argv=None)` parses `--out DIR` with `argparse` (the docstring's first
  line its description). With `DIR` given, `keep_out(DIR)` runs before
  `members()`: a `DIR` that exists and is not an empty folder (a file, or a
  folder with an entry) is refused, `check-dist failed: <DIR> exists and is
  not an empty folder; the archives of a release are kept in a new one`, exit
  1. After the last smoke and its commands, still inside the temporary
  directory, `keep(DIR, scratch, wheels)` checks the folder again, collects
  every `*.tar.gz` and `*.whl` of each member's build folder, refuses two of
  one name, creates `DIR` (`parents=True`), copies each with `shutil.copy2`
  and prints one line per archive and the count. A failure anywhere before
  leaves no `DIR` (the copy is the last step). Without `--out` nothing changes
  but the argument parser (`--help` now prints usage instead of running the
  build).
- The module docstring's last paragraph says that, with `--out DIR`, it also
  writes the archives into `DIR`.

### 11. CI on the targets

`.github/workflows/python-app.yml`: the jobs' `defaults.run.working-directory`
go (every `make` runs at the root); every setup step stays as it is (checkout,
`awalsh128/cache-apt-pkgs-action` for OpenSCAD, `astral-sh/setup-uv`, the
"Sync the workspace" step with `uv sync --locked --python 3.12` and its
`GITHUB_PATH` line, `actions/setup-node`, `playwright install --with-deps
chromium`); each job's commands become targets:

- `lint`: "Lint", `make lint`, `continue-on-error: true` (the two steps become
  one).
- `test`: setup; "Build the bundles", `make widget`; "Install Chromium",
  `playwright install --with-deps chromium`; "Run the tests", `make test`.
- `browser-snapshot`: setup; `make widget`; Chromium; the end-to-end step
  unchanged (`MACHINOME_WEB_SNAPSHOT_E2E=1`, `pytest
  tests/test_browser_renderer.py::BrowserSnapshotEndToEndTest`, with
  `working-directory: packages/machinome` on the step), there being no target
  for it (Non-Goals).
- `docs`: checkout, `astral-sh/setup-uv` (no workspace sync), "Build the
  manual (fail on warnings)", `make docs`; no Node, no apt package.
- `dist`: needs `test` and `docs`; checkout, setup-uv, the sync step, Node;
  "Check the distributions", `make check`.
- `build` (on a tag): needs `test`; checkout, setup-uv, the sync step, Node;
  "The tag names the set's version", `test "$GITHUB_REF_NAME" = "v$(make -s
  version)"`; `make dist`; `gh release create "$GITHUB_REF_NAME"
  "dist/$GITHUB_REF_NAME"/* --title "${GITHUB_REF_NAME#v}"` with the token, as
  the job does today with the core's archives alone. The `packaging` step and
  `MACHINOME_VERSION` go.

`make` is on `ubuntu-latest`. Nothing of the workflow can run here; the
rehearsal runs every target CI calls but `make test` whole (Validation).

### 12. The gates, red first

- **`tests/test_repository_layout.py`**, a new `TheMakefileTest` with the
  helpers of probe 8:
  `test_the_makefile_is_the_repository_s` (the root's exists, the framework's
  directory holds none; red: no root Makefile, the framework's present);
  `test_the_package_list_is_the_package_directories`;
  `test_the_tested_list_is_the_core_and_the_products` (and each has its rule);
  `test_the_targets_are_the_decided_ones` (the targets with a help line are
  exactly the twelve, each phony, `help` the default goal; no target named for
  a sweep);
  `test_upload_is_reached_by_no_other_target` (no prerequisite, the only
  `twine upload`, no rule depends on `dist` or `upload`, `dist`'s recipe runs
  `scripts/check-dist --out $(RELEASE)`, `RELEASE` is `dist/v$(CURRENT)`,
  `CURRENT` read from `current_version` of `.bumpversion.cfg`);
  `test_the_bump_neither_commits_nor_tags` (its recipe passes `--no-commit
  --no-tag` and runs no `git commit` or `git tag`);
  `test_clean_removes_only_what_git_ignores` (each `CLEAN` path, a glob's
  `*` replaced by a sample directory name, is ignored by `git check-ignore -q
  --no-index` asked with a trailing slash, and none is `.venv`,
  `node_modules` or `dist`).
  Each red at the base names the missing file; after the file, each
  mutation of evidence (a package dropped from `PACKAGES`, a product dropped
  from `TESTED`, `upload` given `dist` as prerequisite, `.venv` added to
  `CLEAN`) fails naming it, shown once on a scratch copy of the Makefile.
  `FRAMEWORK_ENTRIES` loses `Makefile`; `test_the_root_ignores_the_benches_and_the_venv`
  adds `/.docs-venv/`.
- **The CI tests**, in place: `test_every_job_runs_from_the_package_directory`
  becomes `test_every_job_calls_the_makefile` (the `make` commands of each job,
  in order, are `lint`: `make lint`; `test`: `make widget`, `make test`;
  `browser-snapshot`: `make widget`; `docs`: `make docs`; `dist`: `make check`;
  `build`: `make dist`; and no `run` spells `flake8`, `black`, `sphinx`,
  `coverage`, `scripts/check-dist`, `twine`, `pip install`, `npm ` or
  `pytest`, the browser-snapshot step excepted);
  `test_the_test_job_runs_each_product_s_tests` reads `TESTED` (every product
  in it); `test_the_dist_job_checks_the_distributions` reads `make check` and
  `needs` `docs` and `test`; the widget test becomes
  `test_the_test_job_builds_the_bundles_and_chromium_before_the_tests` (Node
  before `make widget`, the sync before Chromium, both before `make test`; the
  Makefile's viewer rule runs typecheck, tests and bundle before pytest);
  `test_the_dist_job_sets_up_node_before_checking` reads `make check`. Red at
  the base: each names the command the job spells.
- **`tests/test_docs_exports.py`**: `ActionsDocsJobBuildsNothingTest` reads
  the docs job's steps and the Makefile's `docs` recipe: no forbidden step in
  either, no Node in the job, the job's one command `make docs`, the recipe's
  one install `-r packages/machinome/docs/requirements.txt`, its build with
  `-W`. Red at the base: the job spells `pip install` and Sphinx and no `make
  docs`.
- **`tests/test_kernel_extras.py`**: unchanged; its three jobs keep their one
  `uv sync --locked` at the root (green before and after).
- **`tests/test_release_records.py`**: Decision 2; red:
  `test_the_bump_neither_commits_nor_tags` (the cfg's two lines), and, shown
  once on a scratch copy whose cfg says 0.9.0 and whose manifests say 0.8.1,
  the record test naming the core's manifest as the copy left behind (at the
  base it names the cfg).
- **`tests/test_check_dist.py`**, new, loading `scripts/check-dist` with
  `importlib.machinery.SourceFileLoader` (it reads the checkout, as the layout
  tests do): `test_the_script_parses` (`ast.parse`; red at the base,
  `SyntaxError`); `test_out_refuses_a_folder_that_is_not_empty` and
  `test_out_refuses_a_file` (`main(['--out', …])` raises `Failure` naming the
  path before `members` is called, a patched `members` failing the test if
  reached; red: `TypeError`, `main()` takes no argument);
  `test_keep_copies_every_archive_flat` (two fake members' build folders with
  an sdist, a wheel and a stray file: four archives in the new folder, bytes
  equal, the stray left); `test_keep_refuses_two_archives_of_one_name`;
  `test_nothing_is_kept_when_a_check_fails` (`build` patched to raise
  `Failure`: the folder never created). Runs in under a second; builds nothing.

### 13. The records and ADR-192

- **`CONTRIBUTING.rst`**: "Development environment" keeps its requirements
  and the install without uv (the layout test's pip spelling), and gives the
  install with uv as `make sync` (what it runs, in one sentence) and the
  bundles as `make widget`; "Running tests" gives `make test`, `make test
  PKG=<package>` with the packages that have tests and what each runs, `make
  lint`, `make docs`, and keeps `pytest tests/<file>` from `packages/machinome`
  for one file; the products' paragraphs name `make test PKG=machinome-mechanics`,
  `-viewer`, `-skills` (and `-movie`, as `join-movie` lands its paragraph) and
  say each runs pytest from that directory; "Pull requests" step 4 says `make
  lint` and `make test`; "Deploying" is rewritten: `make bump VERSION=X.Y.Z`
  (every copy and lock, no commit, no tag; `make version` prints the
  current one), the release records, the commit, `make dist` (the folder
  `dist/vX.Y.Z`), the tag and the push, `make upload`; `make check` before a
  pull request touching packaging. The guide names no `requirements.txt` and
  no `tox` (its test).
- **`HISTORY.rst`**, its `Unreleased` section, after the skills' bullet:

  ```rst
  * **One command per step.** A ``Makefile`` at the repository root runs the
    repository's steps: ``make sync``, ``make test [PKG=<package>]``,
    ``make lint``, ``make docs``, ``make widget``, ``make check``, and for a
    release ``make bump VERSION=X.Y.Z``, ``make dist`` and ``make upload``;
    ``make`` alone lists them. The set's version is declared once, as
    ``current_version`` of ``.bumpversion.cfg``, and ``make bump`` moves every
    copy and every lock without committing or tagging.
    ``scripts/check-dist --out dist/vX.Y.Z`` keeps the archives it built,
    checked and smoked, the ones ``make upload`` uploads. CI runs the same
    targets; the framework's own ``Makefile`` is gone. Change
    ``release-tooling`` (ADR-192).
  ```

- **The manual's changelog**: unchanged; nothing a maker uses changes.
- **`docs/architecture.md`**: the "Repository layout" row's code names
  `Makefile` beside `.bumpversion.cfg` and `scripts/check-dist`, its specs
  gain `release-tooling` and its ADRs 192.
- **`docs/adrs/BUILD/ADR-192-the-repository-s-steps-are-the-targets-of-one-makefile.md`**,
  Status Proposed: context (the finding), the decision (Decisions 1 to 3, 7
  and 11 in brief: the targets, the version declared once, the bump that never
  commits, the kept folder and the upload alone, CI on the targets, the
  framework's Makefile gone), the options weighed (a task runner other than
  make, scripts under `scripts/`, the steps left in the guide), consequences;
  amends ADR-182 (the root holds the Makefile) and ADR-183 (the version's
  declaration and its bump), cites 187, 188. Its index entry after ADR-191
  (the movie's) under BUILD; ADR-182's and ADR-183's status and index lines
  "amended by 192".
- **The root `README.md`**: unchanged; it names no command (its rule: a README
  changes only the fact it is asked to change).
- **`context7.json`**: unchanged; it indexes no build file.
- **`docs/project/contributing.rst`** (the manual's page): unchanged; it sends
  the reader to `CONTRIBUTING.rst` for the commands.

### 14. The spec deltas

`framework-identity`'s requirement "The framework is the package directory
`packages/machinome` of a monorepo" is MODIFIED, every scenario title kept:
the set's one version is the one `current_version` of `.bumpversion.cfg`
declares, the root holds the `Makefile`, and CI runs `scripts/check-dist`
through `make check`. `join-movie` modifies another requirement of that spec
("Extras select independent Machinome products") and adds one; it does not
touch this one (its design, Decision 18), so this change's copy is the
baseline's at the bench's head. The applier confirms, before the archive,
that the MODIFIED block equals the baseline at that head plus this change's
edits, and re-derives it if the baseline moved. The same holds for
`framework-contributor-guidance`'s "The contributor guide states the
monorepo's development setup" (MODIFIED; `join-movie` adds a requirement
beside it) and `user-documentation`'s "The documentation build produces
nothing" (MODIFIED; `join-movie` adds one beside it). `release-tooling` is new,
seven requirements. The 0.8.1 release record (`user-documentation`) stays as
it is: its facts are 0.8.1's and hold.

### 15. Validation and the originating check

On the bench, after the movie has landed: the whole core suite through `make
test PKG=machinome` (one process); `make test` whole (every package of
`TESTED`, in order); `make lint` (the counts of probe 6, the movie's modules
added); `make docs`; `make check` (both runs; 32 archives a run with the
movie); `make bump VERSION=0.9.0` on a Git copy of the tracked tree (every
file of probe 3, the movie's three tables, both npm locks and `uv.lock`, no
commit, no tag; nothing in the bench); and the originating check, a dry
release rehearsal: the tracked tree copied to a scratch directory and made a
Git repository of one commit (what a fresh clone of the release commit is),
then `make sync && make test PKG=machinome && make docs && make dist`, the
folder's archives listed and `twine check --strict dist/v0.8.1/*`. `make
upload` is never run, by the applier or the orchestrator: its refusal of an
absent folder and `make -n upload` are its evidence. No universe sweep: no
project reaches the Makefile, `scripts/check-dist` or the CI workflow, and no
module of any package changes.

## Risks / Trade-offs

- [A contributor without make] → Every target is a few commands the guide
  still states (the install without uv, pytest from a directory); the suite
  reads the Makefile as text and needs no make.
- [`make test` whole takes the core's suite, the viewer's and the widget's,
  about twenty minutes] → `PKG=` runs one; CI runs it whole, as its test job
  ran each before.
- [Coverage is no longer reported in CI] → It had no threshold and no upload;
  `coverage` stays in the dev extra for a contributor who wants the report
  (Open Questions 9).
- [`make dist` refuses a tree with an untracked scratch file] → It names the
  file; the release is built from its commit, which is the point.
- [`make check`'s first run builds from the checkout, ignored build
  directories included] → It keeps nothing; its second run, on the tracked
  files, is the one a release's archives match, and `make dist` builds from
  the commit.
- [`make check` takes two builds] → About seven minutes on this machine
  (probe 2, probe 7), in CI's `dist` job, which already takes the longest.
- [An upload that fails part-way leaves part of the set on the index] →
  PyPI refuses a file of an existing name; the folder is unchanged and
  `twine upload --skip-existing dist/vX.Y.Z/*` by hand resumes it. The
  target stays the plain upload the decision names.
- [The mechanics helpers' 0.1.0 archives are kept in `dist/v0.8.1` by a
  rehearsal] → The index already serves a `machinome-mechanics` 0.1.0 of the
  former import; nothing uploads a rehearsal's folder, and at 0.9.0 every
  member carries 0.9.0.
- [Docs built with uv rather than pip] → The same requirements file and
  interpreter version as Read the Docs; the installer differs, the set
  installed does not (probe 5).

## Migration Plan

Within the cycle, in the order of tasks.md: the baseline; the red tests; the
check-dist script; the Makefile and the removal of the framework's; the cfg
and `.gitignore`; CI; the records; validation; the rehearsal. Rollback is a
revert of the implementation commit. Outside the cycle: the workspace's
`scripts/dev-env` and `scripts/setup` may call `make sync` at the workspace
consistency cycle; the 0.9.0 cycle runs `make bump VERSION=0.9.0`, adds the
mechanics' tables, then `make dist`; the pilot runs `make upload`.

## Open Questions

1. **The cfg's `commit = True` and `tag = True`.** Removed, or kept with the
   Makefile passing `--no-commit --no-tag`. Recommendation: removed; the
   pilot tags, and a hand run of the tool then does what the target does
   (probe 3). The Makefile passes the flags either way.
2. **`make check`'s clean copy.** Both runs in one target, or the tree's alone
   with the copy left to the cycles by hand. Recommendation: both; the copy is
   the check every cycle has run by hand and the one a fresh clone meets, and
   the cost is one more build in the slowest CI job.
3. **`make test PKG=` for a package with no tests of its own.** An error
   naming the core's suite, or a message and exit 0. Recommendation: the
   error; an exit 0 says tests passed where none ran.
4. **The docs venv's place.** `.docs-venv/` at the root, ignored, made when
   absent; or under `packages/machinome/docs/`, or a temporary venv each run.
   Recommendation: the root, beside `.venv/`, where `make clean` finds it; a
   temporary venv costs a resolution each run.
5. **`make clean`'s scope.** What the targets write, never `dist/`; or
   `dist/` too, as the brief listed. Recommendation: never `dist/`: the
   release folders are the record of what was uploaded, as the framework's
   checkout keeps `dist/0.7.1-2026-09-27/` to `dist/0.8.1-2026-10-10/` today;
   nor the `*.egg-info` the editable install uses, nor the suites' build
   directories, whose verdict caches are expensive to rebuild.
6. **The package list or a glob of `packages/*`.** Recommendation: the list;
   the decision makes it the declaration the gate reads, and a new directory
   is then declared in the Makefile as it is in the root's uv sources.
7. **The ADR.** ADR-192 (BUILD), amending 182 and 183; or amendments of those
   two only. Recommendation: ADR-192: where a release's steps are declared, and
   that no target uploads what it built, is a decision of its own.
8. **`make dist` and a folder that is not empty.** Refused before any build;
   or emptied and refilled. Recommendation: refused; a folder that exists may
   be the one already uploaded, and an archive rebuilt is not byte-identical
   (its timestamps), so it would no longer be the archive proved and uploaded.
9. **Coverage in CI.** Dropped with the plain `make test`; or `make test
   PKG=machinome` runs under `coverage` and prints its report.
   Recommendation: dropped (no threshold, no upload, read by nobody); the
   pilot may keep it, in which case the core's rule runs `coverage run
   --source machinome -m pytest` and `coverage report -m`.
10. **What `make test PKG=machinome-movie` runs.** The Python tests and the
    Node `pure` and `stage` projects, as CI; or the whole Node suite.
    Recommendation: as CI, for one meaning per target; the whole suite is
    `npm test --workspace <js>`, named in the guide.
11. **`make dist` from a copy of the commit, and its guard.** Built from
    `git archive HEAD` and refused when `git status` lists a file; or built
    from the checkout under the guard alone; or from the checkout as it is.
    Recommendation: the copy and the guard. The guard alone lets the ignored
    build directories into the core's sdist (probe 9: the published 0.7.1
    sdist kept in `dist/0.7.1-2026-09-27/` carries 246 entries of
    `tests/_build*`); the copy alone would build
    a commit other than the tree the pilot sees when files are uncommitted. A
    `prune docs/_build` and `prune tests/_build*` in the core's `MANIFEST.in`
    would close today's two directories but not the next one a test writes.
12. **The brace in `scripts/check-dist`.** Fixed here, red first by
    `test_the_script_parses`; or fixed on the line by the orchestrator before
    this change's implementation. Recommendation: on the line at once, since
    the line's CI `dist` job fails until it is; this change's test then pins
    it.
