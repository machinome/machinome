## Context

The third cycle of the joins campaign of Machinome 0.9
(`workflow/ongoing/joins-0.9.md` at the repository root, cycle 3, set by the
pilot on 11 October 2026), cut from the line `v0.9-joins` at 484a528f, the
head of `join-mechanics`, on the bench
`machinome/WTs/v0.9-joins-join-viewer`. The decisions of `monorepo-0.9.md`
still hold, and the joins plan's method: a product is imported by rewriting
its history directly to its final paths and merged with
`--allow-unrelated-histories` by the orchestrator after the planning commit;
one licence at the join; a product that is not an extension package keeps
its record in its directory; the original repository stays as it is.

The pilot's decisions for this cycle (12 October 2026), settled and not
reopened here:

- **The viewer joins whole** into `packages/machinome-viewer/`, with its
  record in its directory: its tests (the Python modules and the widget's
  vitest tests), its OpenSpec specs and archived changes, its working record
  `workflow/` with its own decision log `workflow/adrs/` (the viewer-owned
  ADRs under their original numbers, a log of its own beside the framework's
  `docs/adrs/`), its `CHANGELOG.md`. Its history is kept whole, the 79
  commits from before the split included; its tags `v0.7.0`, `v0.7.1`,
  `v0.8.0`, `v0.8.1` take the prefix `viewer-`.
- **Its manual folds into the one manual**, by reader intent under the
  workspace's `skills/write-the-manual/SKILL.md`; the separate Read the Docs
  project is retired by the pilot later; the framework's pages that link it
  link inside the manual.
- **One licence at the join**: the licence file and every header and notice
  stating the licence it carried go; its manifest declares the set's
  expression and files; no record this change writes names that licence; its
  third-party provenance goes to `CREDITS.md`.
- **One version**: it takes the set's version (0.8.1), pins `~=` both ways
  (the core's `viewer` and `web-snapshot` extras, floors at the base, become `~=`),
  enters `.bumpversion.cfg` and the release-records test; its `CHANGELOG.md`
  stays its record.
- **pip-only distribution**: nothing is published on npm; the widget's
  `package.json` stays private and becomes the first member of a root
  `package.json` npm workspace founded by this cycle (one `npm ci` at the
  root, one lockfile, the widget built from the monorepo); the built bundle
  is never tracked and the wheel carries it as it does at the base.
- **The seam is unchanged**: the framework finds the installed viewer through
  the entry point `machinome.viewer` and runs it as a separate process
  (`machinome develop`, `snapshot --renderer web`, `machinome viewer`); the
  studio takes the bundle from that report.
- **The root manifest's `exclude-dependencies`** loses `machinome-viewer`;
  the lock resolves the member from the workspace.

The import name, settled by the pilot on 12 October 2026 after this design
was first written: the viewer's Python package takes the address
**`machinome.viewer.web`**, the dot like the rest of the set, and the address
the pilot's `viewer-seam` outline of 4 October 2026 (probe 18) gives this
package, so no later cycle renames it. Not `machinome.viewer`, which the
first draft took and which is the seam's own address, and not
`machinome_viewer` kept, which the first draft recommended. The core's seam
of viewers, `machinome/viewer/__init__.py` with the OpenSCAD provider
`machinome.viewer.openscad`, is a later cycle, inside 0.9 if nothing blocks
it; this change does not write it. The design below is revised in place for
that address; the variant that kept `machinome_viewer` is gone from it.

machinome-viewer is the browser viewer: the embeddable three.js widget (a
TypeScript project of 128 sources under `machinome_viewer/widget/`, built by
esbuild into the one artifact `dist/machinome-viewer.js`), the export and
development pages beside it, the FastAPI development server and the
Playwright capture, packaged for pip. Published 0.7.0, 0.7.1 and 0.8.0;
0.8.1 is at released state, tagged locally. Its `main` is bd2bf75, equal to
its GitHub main: 291 commits, every one of its 61 branches an ancestor of
`main` (`git rev-list --count --all` in a fresh clone is 291). Its four tags
are annotated.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C3-propose/join-viewer/`
(named `<scratch>` below), never in the bench, the product or a project, with
uv 0.11.8, git-filter-repo `ed61b4050b71`, Node 24.11.1 and npm 11.6.2,
Sphinx 9.1.0 and the OpenSpec CLI. `<scratch>/merge-rehearsal` is a clone of
the bench's branch at 484a528f with the rehearsed import merged; its scratch
venv `<scratch>/venv` was synced from its own edited lock (probe 7). The
revision for the address `machinome.viewer.web` reran the probes the address
touches, but the manual's build (probe 13, where the address appears only
in the command reference's text) and its source path (probe 14), in
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C3-revise/`
(named `<revise>` below): `<revise>/merge-web` is a fresh clone of the bench's
branch at 484a528f with the import rewritten at the new address merged and
the first draft's scratch edits carried one level deeper, its venv
`<revise>/merge-web/.venv` synced from that lock; `<revise>/merged-only` is a
worktree of its bare merge commit. A probe below states the address it ran
at.

### What the join touches

- **The product's 904 tracked files** at bd2bf75: `README.md`,
  `CHANGELOG.md`, `pyproject.toml` (version 0.8.1, no dependency on the
  framework, extras `docs`, `snapshot`, `dev`, the console script, the entry
  point, the build hooks), `MANIFEST.in`, `LICENSE`, `context7.json`,
  `.readthedocs.yaml`, `.github/workflows/ci.yml`, `.gitignore`,
  `scripts/check-dist`, `scripts/check-docs-browser.py`, `web/__init__.py`
  (a vestige importing a module the repository has not carried since its
  layout of 5 September 2026); `machinome_viewer/` (144: eight modules and
  `widget/` with `package.json`, `package-lock.json`, `build.mjs`, `src/`,
  `tools/`, `tsconfig.json`, `vitest.config.ts`, `index.html`,
  `develop.html`); `tests/` (118: 24 test modules, `support.py`,
  `__init__.py`, 92 fixture files); `docs/` (21: twelve pages, two examples,
  two statics, `conf.py`, `Makefile`, `requirements.txt`, `index.rst`,
  `installation.rst`); `openspec/` (530: `config.yaml`, 16 specs, 60 archived
  changes and three active ones, `execute-running-time-drives`,
  `scripted-camera` and `slide-and-turn-parts`); `workflow/` (79, its decision
  log `workflow/adrs/` among them).
- **History.** 1481 paths in all. The 79 commits before the split hold the
  framework's `solid_node/viewers/` at the root: `__init__.py`, `bundle.py`,
  `browser.py` (later `capture.py`), `web/viewer.py` (later `server.py`),
  `web/app/` (the React development shell, later deleted), `widget/`,
  `openscad.py` (the framework's OpenSCAD viewer, dropped from the viewer on
  10 October 2026); the layout commit eb1595f moved them under
  `solid_node_viewer/`, renamed `machinome_viewer/` on 19 September 2026. The
  decision log lived under `docs/adrs/` and the release record of 0.2 at
  `docs/release-0.2.md` before both moved to `workflow/`.
- **The licence the product carried** is stated in `LICENSE`, both manifests
  and the lock, 156 SPDX lines in 155 files (33 Python, 119 TypeScript, two
  HTML pages and `build.mjs`, whose banner template carries a second),
  `README.md`, `CHANGELOG.md` (the 0.7.0 section's identity bullet),
  `context7.json`, the manual's `index.rst`, `installation.rst` and
  `sharing.rst`, `openspec/config.yaml`, its specs `viewer-distribution` and
  `user-documentation`, `tests/test_licence.py`, the release records
  `workflow/release-0.7.md` and `release-0.8.md`, two active changes, and 40
  lines of twelve archived records (archived changes, evidence, two ADRs).
- **The core.** `pyproject.toml`'s `viewer` and `web-snapshot` extras (floors
  `>=0.8.1`) and the comment above them; the root's
  `exclude-dependencies`; `machinome/viewers/bundle.py` (`viewer_command()`
  is `[sys.executable, '-m', 'machinome_viewer']`, its docstring and remedy
  say "separate", "separately licensed"); `docs/conf.py` (`viewer_version`,
  `viewer_api`, `document_versions`, the source path of every
  `packages/machinome-*`); `docs/requirements.txt` (the published viewer);
  the pages that link `machinome-viewer.readthedocs.io` or the viewer's
  repository or state its licence (`README.rst`, `why.rst`,
  `start/install.rst`, `concepts/publishing.rst`, `tutorial/10-share.rst`,
  `reference/cli.rst`, `reference/manuals.rst`, `project/status.rst`,
  `project/upgrading.rst`, `project/contributing.rst`,
  `project/changelog.rst`); `tools/generate_parity_fixture.py` (writes the
  fixture into a sibling `machinome-viewer` checkout by default);
  `docs/architecture.md` ("Viewers", the Map); ADR-068.
- **Consumers.** The studio runs `machinome viewer` and reads the bundle path
  from its JSON (`machinome-studio/floor/preparation.py`); the videomaker
  takes a bundle path (`--viewer BUNDLE.js`); the site runs the workspace
  venv's `machinome-viewer describe` and reads the banner's
  `machinome-viewer <version> - viewer API <n>` in the bundle's first
  kilobyte (`machinome.org/src/machinome_site/intake_viewer.py`). Sixteen
  project files spell `machinome_viewer`: eleven tools of the Curta
  (`simulation/tools/*`, each running `python -m machinome_viewer
  describe`), the pin tumbler lock's `tools/export-demo.py`,
  science-jubilee's audit tool pinned to a framework revision, and three
  evidence files of Voron-2.

### Probes

1. **The import, rehearsed** on a fresh clone with the command of Decision 2,
   first at the first draft's address (`<scratch>/viewer-rw2`,
   `<scratch>/filter-repo-command.final.sh`), then at `machinome.viewer.web`
   (`<revise>/viewer-rw-web`, `<revise>/filter-repo-command.web.sh`, the same
   command with `PKG=machinome/viewer/web`): 291 commits parsed, every branch
   rewritten, `main` at 1b41968, 285 commits on it. Six are pruned as empty: four framework commits that touched only
   `openscad.py` ("rename instance to node in two classes", "Fix pid-file
   handling crashing on corrupt file or PermissionError", "feat(openscad):
   make dependency conditional", "feat(node): declare a machine in the class
   body"), "Build the manual in CI and describe the package for Context7"
   and the merge "Merge branch 'main' into curta-traced-bound-path". Its tree
   holds 893 files (`<revise>/rehearsal-ls-files.web.txt`, equal to the first
   draft's `<scratch>/rehearsal-ls-files.txt` with `machinome/viewer/` read
   `machinome/viewer/web/`): 877 under `packages/machinome-viewer/` (144 of
   them under `machinome/viewer/web/`: the eight modules and 136 of the
   widget), 16 under `packages/machinome/docs/`; no commit of any branch
   touches a path outside `packages/`. Without `--follow`, `git log` on
   `packages/machinome-viewer/machinome/viewer/web/server.py` lists 42
   commits back to 88f844b, 18 July 2023, "Web viewer - base web server,
   untested" (the original's `--follow` lists 43, the extra one the layout
   commit, which no longer changes the path); `widget/src/evaluator.ts` lists
   10 back to 95bdcf0, 16 July 2026, the commit that added the widget. The
   tags are `viewer-v0.7.0` (3662172), `viewer-v0.7.1` (b3b6b56),
   `viewer-v0.8.0` (4becb18) and `viewer-v0.8.1` (1b41968), annotated, with
   their messages. (At the first draft's address: the same counts, `main` at
   957e33b.)
2. **The merge, rehearsed** in `<scratch>/merge-rehearsal` (a first rewrite,
   identical but for the two statics' names and the address) and again in
   `<revise>/merge-web` at the address `machinome.viewer.web`: `git fetch
   <rewrite> main 'refs/tags/viewer-*:refs/tags/viewer-*'` and `git merge
   --allow-unrelated-histories FETCH_HEAD`: no conflict, 893 files created,
   283596 insertions, `git status` clean, the four tags present; `git log
   --follow` on `server.py` reaches 88f844be (8e5f47a6 at the first draft's
   address) and
   `git blame` attributes its three header lines to their commits of 19
   September 2026, 10 January 2026 and 25 September 2026. 77 commit subjects
   appear twice in the global log, the framework's originals and their
   rewritten copies, told apart by their paths.
3. **The gates at the join**, fifteen suite modules on the merged tree with
   the bench venv (19 failed, 199 passed). Red for the join:
   `test_every_member_is_a_workspace_source`,
   `test_the_readme_links_every_package_and_states_the_licence`,
   `test_every_sibling_is_in_the_table` and
   `test_the_guide_installs_every_member_without_uv`, each naming
   `machinome-viewer`; `test_every_pin_between_members_is_compatible` (the
   core's two floors `machinome-viewer>=0.8.1` and
   `machinome-viewer[snapshot]>=0.8.1`) and
   `test_the_version_is_bumped_from_the_root` (the viewer's manifest). The
   other reds are the rehearsal's own (the bench venv's editable lines name
   the bench's directories) and are not counted, as in the earlier joins.
   The core-names, split-words, kernel-free and root-exports gates scan
   `packages/machinome-*/machinome/**` and pass with the viewer's modules at
   the first draft's `machinome/viewer/`: none holds a word they refuse.
   Rerun at
   `machinome.viewer.web` on `<revise>/merged-only` (the bare merge) with the
   bench venv, the six modules of task 2.3: 19 failed, 98 passed; the six
   join reds above, twelve subtests of
   `test_each_portion_resolves_from_its_package` and one of
   `test_each_product_resolves_from_its_directory` that are the rehearsal's
   own (the bench venv resolves the portions from the bench), and the four
   name gates green with the modules at `machinome/viewer/web/`
   (`<revise>/gates-at-join-web.txt`).
4. **The widget at its new place.** Baseline, the original layout
   (`<scratch>/viewer-orig`, its own `npm ci`): 66 files, 1715 passed, 2
   skipped. At `packages/machinome-viewer/machinome/viewer/web/widget/` on
   the bare merge (`<revise>/merged-only`, the widget's own `npm ci`): 8 files
   fail, 121 failed, 1341 passed, 2 skipped of 1464 collected: the tests read
   the repository's fixtures by `../../../tests/fixtures` from `src/`, which
   at this depth names `machinome/viewer/tests/fixtures` (ENOENT), and the
   manual by `../../../docs`. With the 26 path lines of 14 test files
   deepened by two `../` (probe only, `<revise>/merge-web`, from the root's
   workspace): one file fails, `documentation.test.ts`, 111 tests, 1604
   passed; with that file reading
   `packages/machinome/docs/reference/viewer` from seven levels above `src/`
   (Decision 11): 66 files, 1715 passed, 2 skipped, the baseline's count.
   (At the first draft's address, one level less deep: 12 files, 123 failed
   before the paths moved, the same one file after.) `tsc --noEmit` exits 0
   and the build writes 895.9 kB at every depth.
5. **The npm workspace.** A root `package.json` (`private`, `workspaces`
   naming the widget's directory) and `npm install` at the root: one
   `package-lock.json` at the root, `node_modules/` at the root (79 entries,
   the member linked as `node_modules/@machinome/viewer`), none in the
   widget. A fresh resolution moves 43 transitive packages to newer patch
   releases; seeding the root lock from the widget's (copied to the root,
   then `npm install`) keeps all 174 resolutions, 0 differences (101
   packages installed). `npm ci` at the root, `npm run build|typecheck|test
   --workspace <widget>` and `npm run build` inside the widget all work from
   the root's `node_modules`. `npm ci` run inside the widget detects the
   workspace and installs at the root from the root lock, whether or not the
   widget keeps a lockfile of its own, which it then ignores. After removing
   the lock's top-level `"version"` (carried from the seed), `npm install
   --package-lock-only` leaves it out ("up to date"): the lock then states
   the version once, in the member's entry. `npm ci` does not refuse a
   member whose version differs from the lock's; `npm install
   --package-lock-only` rewrites the member's version (0.8.1 to 0.9.0) and
   nothing else. `git status` shows `node_modules/` untracked. At
   `machinome.viewer.web` (`<revise>/merge-web`, the root `package.json`
   naming `packages/machinome-viewer/machinome/viewer/web/widget`): `npm ci`
   at the root "added 101 packages", the member linked as
   `node_modules/@machinome/viewer -> ../../packages/machinome-viewer/machinome/viewer/web/widget`,
   and the lock equal to the first draft's but for the member's path.
6. **The currency check under the workspace.** With the dependencies at the
   root and none in the widget, a source newer than the bundle: `python -m
   machinome.viewer.web describe` exits 1, "Viewer bundle ... is older than
   .../src/version.ts and was not rebuilt: the widget's dependencies are not
   installed, and a rebuild never installs them" (`<revise>/currency-web.txt`).
   After `npm run build` at the root: exit 0. The check reads whether
   `widget/node_modules` is a directory, nothing more: an empty
   `widget/node_modules` that a step of the revision's probes left behind
   (which step was not identified) let the stale bundle rebuild from the
   root's dependencies; Decision 4's lookup asks for `node_modules/esbuild`
   instead.
7. **The lock.** The member in the root's sources and out of
   `exclude-dependencies`, the core's extras at `~=0.8.1`, the core's `dev`
   extra installing `web-snapshot`: `uv lock` "Resolved 192 packages" (the
   bench's 188, adding `machinome-viewer` from the workspace, `playwright`
   1.63.0, `greenlet` 3.5.6 and `pyee` 13.0.1); the lock's diff is 161 lines
   (`<scratch>/uv-lock.diff`). `uv sync --python 3.12` into `<scratch>/venv`:
   fourteen `__editable__` `.pth` files, the viewer's naming
   `packages/machinome-viewer`; the viewer's editable build ran its
   `build_py` hook with `cmdclass` resolved at the first draft's address. At
   `machinome.viewer.web` (`<revise>/merge-web`): `uv lock` "Resolved 192
   packages" and leaves the lock byte for byte as it was (the lock names the
   member's directory, not its import), `uv sync --python 3.12` builds the
   viewer editable with `cmdclass` at `machinome.viewer.web.packaging` and
   writes fourteen `__editable__` `.pth` files.
8. **Chromium.** Playwright 1.63.0 needs Chromium revision 1243;
   `~/.cache/ms-playwright` holds 1217, 1228 and 1234. The viewer's Python
   tests at the new place on that venv: 128 failed, 118 passed, 3 skipped,
   107 of the failures "Executable doesn't exist ... chromium_headless_shell-1243".
   With Playwright 1.62.0 (revision 1234) installed into the scratch venv
   for the probe only: 16 failed, 231 passed, 2 skipped (the Curta's builds
   not found), the 16 being the pinning modules `test_documentation.py` (9)
   and `test_licence.py` (7). The original on the same venv: 244 passed, 2
   skipped. At `machinome.viewer.web` (`<revise>/merge-web`, Playwright
   1.62.0 for the probe only, `<revise>/viewer-pytest-web.txt` and
   `viewer-pytest-web-pinning.txt`): 15 failed, 232 passed, 2 skipped (the
   Curta's), the 15 in the pinning modules Decision 11 rewrites,
   `test_documentation.py` (10: the manual's pages and build files moved)
   and `test_licence.py` (two tests and three subtests: the expression and
   the pages); every behaviour test passes at the new address.
9. **The core's viewer tests.** `test_browser_renderer.py`,
   `test_cli_lazy_imports.py`, `test_scad_presentation.py`,
   `test_manager_develop.py`, `test_viewer_bundle.py`,
   `test_manager_viewer.py`, `test_sphinx_ext.py` and `test_export.py` on the
   merged tree with the viewer installed and `viewer_command()` at
   `-m machinome.viewer.web` (`<revise>/core-viewer-tests-web.txt`; the first
   draft's address gave the same): 143 passed, 1 skipped (the end-to-end
   capture, opt-in by `MACHINOME_WEB_SNAPSHOT_E2E`). The sixteen tests the
   base skips without the viewer run.
10. **The import's cost.** `python -X importtime -m machinome.viewer.web
    describe` (`<revise>/importtime-web.txt`): 170 modules, three more than
    the original's 167 (`python -m machinome_viewer describe` on
    `<scratch>/viewer-orig`): the core's `machinome` (9.0 to 9.9 ms
    cumulative over three runs, most of it `pkgutil`, which its path
    extension imports), the namespace level `machinome.viewer` (0.5 ms of its
    own) and the package `machinome.viewer.web`; the first draft's address
    gave 169, the namespace level being the one more. Median wall time over
    15 runs each, the same machine and minute (`<revise>/walltime.txt`):
    77.5 ms at `machinome.viewer.web`, 78.3 ms at the first draft's address,
    75.9 ms for the original; the first draft's two medians, 80.6 ms and
    72.3 ms, were taken minutes apart. The extra level costs nothing a
    process start can measure; the core's `__init__` costs about 9 to 10 ms
    of import, within the run-to-run spread of the wall time. The viewer's
    wheel installed alone (`--no-deps`, `<revise>/alone-venv-web`):
    `machinome` and `machinome.viewer` are then implicit namespace packages
    and `python -m machinome.viewer.web describe` answers; the viewer needs
    nothing of the core to run, and requires it only by the pins.
11. **The archives.** With the former `MANIFEST.in` (paths under
    `machinome_viewer/`) the wheel build fails ("No such file or directory:
    .../machinome/viewer/widget"). With Decision 3's: the sdist builds the
    bundle through its hook (an `npm ci` inside the widget, which installs at
    the root) and holds 1089 entries; the wheel 22 (the eight modules,
    `develop.html`, `index.html`, `package.json`, `dist/machinome-viewer.js`,
    `dist/.build.lock`, `tools/expression-pressure.ts`, the three licence
    files, the metadata; no `machinome/__init__.py`, no source). The
    published-to-be 0.8.1 archives of the original: 20 and 452. At
    `machinome.viewer.web` (`<revise>/viewer-dist-web`): the sdist 1089
    entries, the wheel 21, the same files under `machinome/viewer/web/`
    (`dist/.build.lock` absent, the bundle having been built by `npm run
    build` rather than by a currency rebuild), no `machinome/__init__.py`
    and no `machinome/viewer/__init__.py`, `top_level.txt` naming
    `machinome`, the entry point
    `bundle = machinome.viewer.web.bundle:describe` in the group
    `machinome.viewer`. With the excluded data still keyed
    `"machinome.viewer"` (`<revise>/viewer-dist-web-wrongkey`): the wheel
    holds 152 entries, the widget's 128 sources, `build.mjs`,
    `tsconfig.json` and `vitest.config.ts` among them; Decision 9's smoke
    refuses it.
12. **Installed beside the core**, from the two built wheels in a throwaway
    venv (`uv pip install --find-links`): `machinome` 0.8.1 and
    `machinome-viewer` 0.8.1; Decision 9's smoke (`<scratch>/viewer-smoke-draft.py`)
    passes; `machinome-viewer describe` and `machinome viewer` exit 0. At
    `machinome.viewer.web` (`<revise>/both-venv`, the core's wheel built from
    `<revise>/merge-web` with `viewer_command()` at the new address): the
    smoke at that address (`<revise>/viewer-smoke-web.py`) prints
    "machinome-viewer 0.8.1 module .../site-packages/machinome/viewer/web/__init__.py
    API 29 documents 1 to 13"; `python -m machinome.viewer.web describe`,
    `machinome-viewer describe` and `machinome viewer` exit 0.
13. **The manual folded in**, the merged tree built with a scratch docs venv
    from `docs/requirements.txt` alone (Sphinx 9.1.0, the theme, the
    published machinome-viewer 0.8.0): `sphinx -b html -n -W --keep-going`
    exit 1 with 32 warnings: six pages in no toctree, 19 references to
    documents of the former layout, the two example includes not found, five
    undefined substitutions (`package-version`, `viewer-api`,
    `document-versions`). With Decision 10's edits applied in scratch
    (`<scratch>/fold-docs-probe.py`): exit 0, no warning. The embedding
    example lands at `howto/embed-the-viewer/` with the installed viewer's
    bundle and the spinner export; served and loaded in Chromium, its status
    reads "Drag to orbit · scroll to zoom · open Assembly to inspect" with no
    page error, and the guide's button loads it in place: the red hub and the
    three blue blades (`<scratch>/embed-page-demo.png`, looked at).
    `test_docs_structure.py`, `test_docs_exports.py`,
    `test_viewer_documentation_links.py`, `test_node_root_exports_nothing.py`,
    the two core-names gates and `test_profile_documentation.py` on that
    tree: 81 passed.
14. **The manual's source path.** `docs/conf.py` puts every
    `packages/machinome-*` on `sys.path` ahead of site-packages. A source
    copy of the viewer on that path, without a built bundle (as on Read the
    Docs), shadows the published viewer the build installed: the framework's
    lookup then answers "Viewer bundle not found at <source copy>" and the
    tutorial's exports cannot be completed; without it, the lookup answers
    the installed bundle. Probed with `machinome_viewer`, the name the
    published viewer still carries. A source copy at `machinome.viewer.web`
    shadows the same way once a viewer at that address is the one published:
    the core's path extension lists the portions in `sys.path` order, the
    manual's source paths first (*inferred*: the same resolution order; not
    probed, no such viewer being published).
15. **The bump on a copy.** `.bumpversion.cfg` with Decision 7's tables and
    the files they name copied to a scratch repository, `bump2version
    --no-commit --no-tag --new-version 0.9.0 patch`: the viewer's manifest
    version and pin, `__init__.py`, the widget's `package.json` and
    `viewer_version` in `docs/conf.py` move with the rest; rerun at
    `machinome.viewer.web` (`<revise>/bump-web`, the eighteen files the
    tables name, then `npm install --package-lock-only`): the same, the lock's
    member entry 0.8.1 to 0.9.0 and nothing else of it. A table for the
    root lock with a two-line search (the member's name, then its version)
    rewrites the lock wrongly and the configuration with it; the lock is left
    to npm (probe 5).
16. **The seam, rehearsed.** `machinome new starter`, then `machinome
    snapshot --renderer web` with the scratch venv: "Snapshot saved", a
    1920 x 1080 PNG of the starter's cube with its bore through the top
    (`<scratch>/starter-web.png`, looked at), through
    `python -m machinome.viewer capture`. At `machinome.viewer.web`
    (`<revise>/merge-web`'s venv, Playwright 1.62.0, under `strace -f -e
    trace=execve`): "Snapshot saved", the framework executing
    `<venv>/bin/python -m machinome.viewer.web capture ... --imgsize
    1920x1080 --time 0.0`; the PNG (`<revise>/starter-web.png`, looked at)
    shows the same cube and bore.
17. **The licence statements.** `git grep` on the rewritten `main`: the SPDX
    lines of probe "What the join touches"; outside them, sixteen current
    files and twelve archived records (40 lines). The list is
    `<scratch>/licence-mentions.txt`.
18. **The record of the name.** `packages/machinome/workflow/ongoing/lean-core.md`,
    beside the naming norm of 2 October 2026: "The viewer keeps
    `machinome_viewer`: it is reached as a separate process, nothing imports
    it, and its entry-point group is already called `machinome.viewer`."
    The same note's `viewer-seam` outline, ratified in outline by the pilot
    on 4 October 2026 and deferred past 0.8 on 5 October: "A seam
    `machinome/viewer/__init__.py` declares the contract as Protocols ...
    Providers `machinome.viewer.openscad` and `machinome.viewer.web`", and
    "when the viewer comes into the monorepo under the one licence, its own
    portion `machinome.viewer.web` replaces that wrapper". The `cli` spec and
    `machinome/node/supported.py` state the same intended seam. On 12 October
    2026 the pilot gave the viewer that address, `machinome.viewer.web`.
19. **The package at `machinome.viewer.web`.** In `<revise>/merge-web` the
    package directory is `packages/machinome-viewer/machinome/viewer/web/`,
    with no `__init__.py` at `machinome/` nor at `machinome/viewer/`, and the
    manifest of Decision 3 (`include = ["machinome.viewer.web"]`,
    `namespaces = true`). On its editable venv, from `/tmp`
    (`<revise>/probe-resolve-editable.txt`): `machinome` resolves to the
    core's `__init__.py`; `machinome.viewer` is a namespace package
    (`NamespaceLoader`, no file) whose one path entry is
    `packages/machinome-viewer/machinome/viewer`, admitted by the core's path
    extension; `machinome.viewer.web` resolves to the package's
    `__init__.py`, `__version__` 0.8.1; `importlib.metadata.entry_points(
    group='machinome.viewer')` lists one entry, `bundle =
    machinome.viewer.web.bundle:describe` of `machinome-viewer`, and loading
    it gives `machinome.viewer.web.bundle.describe`; the console script
    `machinome-viewer` is `machinome.viewer.web.cli:main`; the core's
    `viewer_command()` ends `-m machinome.viewer.web`; `find_spec(
    'machinome_viewer')` is `None`; `machinome.viewers` resolves to the
    core's `machinome/viewers/__init__.py`. The group's name and the
    namespace's spelling never meet: the group is read from
    `entry_points.txt`, and the namespace is never the entry's value.
    `python -m machinome.viewer.web describe`, `machinome-viewer describe`
    and `machinome viewer` exit 0 with the same report; `python -m
    machinome.viewer describe` exits 1 ("'machinome.viewer' is a package and
    cannot be directly executed") and `python -m machinome_viewer describe`
    exits 1 (`<revise>/probe-commands-editable.txt`). From the built wheels
    (probes 11 and 12) installed in `<revise>/both-venv`: the same answers
    from `site-packages/machinome/viewer/web/` (`<revise>/probe-resolve-wheels.txt`,
    `probe-wheels-commands.txt`); the viewer's wheel alone in
    `<revise>/alone-venv-web`: `machinome` and `machinome.viewer` implicit
    namespaces, `python -m machinome.viewer.web describe` answers
    (`<revise>/probe-alone.txt`).
20. **The seam's future file.** The `viewer-seam` cycle will write
    `machinome/viewer/__init__.py` in the core. Rehearsed by adding that file
    to the core's directory in `<revise>/merge-web` (removed afterwards,
    `<revise>/probe-seam-editable.txt`, `probe-wheels-commands.txt`):
    - **empty, in the editable workspace**: `machinome.viewer` becomes the
      core's regular package with one path entry, the core's
      `machinome/viewer/`; `import machinome.viewer.web` raises
      `ModuleNotFoundError: No module named 'machinome.viewer.web'`, and
      `python -m machinome.viewer.web describe` exits 1. A regular package's
      path is its own directory alone; the viewer's portion, in
      `packages/machinome-viewer/machinome/viewer/`, is not on it.
    - **with the line `machinome/node/__init__.py` carries**, `from
      machinome import _namespace_portions` and `__path__ =
      _namespace_portions(__path__, __name__)`: `machinome.viewer`'s path is
      the core's directory, then the viewer's; `machinome.viewer.web`
      resolves from the viewer's package, and `python -m
      machinome.viewer.web describe` and `machinome viewer` exit 0. The
      portion is admitted because the viewer ships no
      `machinome/viewer/__init__.py`; Decision 7's layout gate keeps it so.
    - **empty, from the built wheels** (the file written into
      `<revise>/both-venv`'s `site-packages/machinome/viewer/`, as the core's
      wheel would install it): `machinome.viewer.web` resolves, both
      distributions installing into one directory, and `python -m
      machinome.viewer.web describe` and `machinome viewer` exit 0.

    So `machinome.viewer.web` keeps resolving under the seam on one
    condition, which the outline already states ("extends its path with
    portions, as `machinome/node/` does"): the seam's `__init__.py` must
    extend its `__path__` with `_namespace_portions`. An empty one breaks
    every editable workspace, the repository's own included, while every
    wheel installation still works, so only a test on the workspace finds
    it; `TheProductsTest.test_each_product_resolves_from_its_directory`
    (Decision 7) is that test. Nothing of the seam is written by this
    change.
21. **The vet's reading of the address** (`<revise>/probe-vet.py`,
    `probe-vet.txt`, on `<revise>/merge-web`'s venv with the bench's
    universe declaration). `Universe.member` is true for
    `machinome.viewer.web.server`, `machinome.viewer.web` and
    `machinome.viewer`, none denied; false for `machinome_viewer.server`.
    Vetting three one-model scratch projects: `from
    machinome.viewer.web.server import WebViewer` gives no finding; `from
    machinome_viewer.server import WebViewer` gives `outside-universe`,
    `machinome_viewer.server`; `from machinome.viewers.browser import
    BrowserRenderer` gives `framework-internal`, `machinome.viewers`. The
    address moves the viewer from outside the universe into the contract
    unless the contract's denylist names it (Decision 7).

## Goals / Non-Goals

**Goals:**

- machinome-viewer joins at `packages/machinome-viewer/` with its whole
  history and its four tags, every file at its final path, the merge
  rehearsed and clean.
- The viewer is a product of the repository numbered with the set, under the
  set's licence, installed by `machinome[viewer]` and `machinome[web-snapshot]`
  with `~=` pins, built and smoked by `scripts/check-dist`, reached by the
  framework exactly as before.
- The root npm workspace, one install and one lock, from which the widget
  builds, and from which CI builds and tests it.
- Its tests green at their new place, run by CI and a contributor; its record
  kept there and brought current; its manual inside the framework's, the
  embedding example working.
- The originating check: `machinome develop` and `machinome snapshot
  --renderer web` on the bench through the joined viewer.

**Non-Goals:**

- Any change to the widget's behaviour, the viewer API (29), the document
  versions (1 to 13), the server, the capture or the seam.
- The `viewer-seam` cycle: no seam of viewers (no
  `machinome/viewer/__init__.py`, no `machinome.viewer.openscad`), no
  `--viewer` flag; the entry-point group `machinome.viewer`, the subprocess
  and `machinome/viewers/` stay. The viewer takes the address that cycle's
  outline gives it, so that cycle moves nothing of the viewer's package.
- A version for upload, an npm publication, the videomaker's `--viewer`, the
  Read the Docs project's retirement, the original repository's fate, any
  push; the joins of the videomaker and the studio.

## Decisions

### 1. The join merges `main`, bd2bf75, and the four tags

`main` holds every branch: in a fresh clone `git rev-list --count --all` and
`git rev-list --count main` are both 291. Fetching `main` and the four tags
brings the product's whole history. The three active changes under
`openspec/changes/` (`execute-running-time-drives`, `scripted-camera`,
`slide-and-turn-parts`) arrive as they stand in `main`, records of the
product; this change neither archives nor edits them.

### 2. The mapping and the import

Every tracked file of the product at bd2bf75, and every earlier path, old to
new, or dropped (`P` is the package directory,
`packages/machinome-viewer/machinome/viewer/web`, the address
`machinome.viewer.web`):

| at bd2bf75 (and in history) | lands at | reason |
|---|---|---|
| `README.md`, `CHANGELOG.md`, `pyproject.toml`, `MANIFEST.in`, `.gitignore` | `packages/machinome-viewer/` | the package's files; README, manifest, `MANIFEST.in` and `.gitignore` rewritten or edited in place (Decision 3), the changelog kept whole and given its entry |
| `scripts/check-docs-browser.py` | `packages/machinome-viewer/scripts/check-docs-browser.py` | the manual's browser review, the viewer's tool, adapted in place to the folded manual (Decision 10) |
| `machinome_viewer/`, `solid_node_viewer/` | `P/` | the package at its address; both spellings to one path |
| `__init__.py`, `bundle.py` (history) | `P/__init__.py`, `P/bundle.py` | the framework's `solid_node/viewers/` before the split, so these modules read at their path back to 2023 without `--follow` |
| `browser.py`, `web/viewer.py` (history) | `P/capture.py`, `P/server.py` | the names the layout commit gave them |
| `widget/`, `web/app/` (history) | `P/widget/`, `P/app/` | the widget, and the React shell deleted on 14 September 2026 |
| `tests/` | `packages/machinome-viewer/tests/` | its record stays in its directory |
| `openspec/` | `packages/machinome-viewer/openspec/` | its specs, archived and active changes |
| `workflow/`, and `docs/adrs/`, `docs/release-0.2.md` in history | `packages/machinome-viewer/workflow/`, `.../workflow/adrs/`, `.../workflow/release-0.2.md` | its working record and decision log at one path |
| `docs/using-the-viewer.rst` | `packages/machinome/docs/howto/browser-viewer.rst` | one job: operate a machine in the viewer |
| `docs/sharing.rst` | `packages/machinome/docs/howto/share-an-export.rst` | one job: share an export and take a still |
| `docs/embedding.rst` | `packages/machinome/docs/howto/embed-the-viewer.rst` | one job: put the viewer in a page |
| `docs/examples/` (`embed.html`, `embed.js`) | `packages/machinome/docs/howto/embed-the-viewer/` | the guide's working host page, beside it, as the mechanics how-to's examples sit beside theirs |
| `docs/reference/index.rst` | `packages/machinome/docs/reference/viewer/index.rst` | the section's index; rewritten in place (Decision 10) |
| `docs/reference/` (`cli`, `clocked`, `layouts`, `mount`, `running`, `viewer-handle`) | `packages/machinome/docs/reference/viewer/` | lookup |
| `docs/compatibility.rst`, `docs/troubleshooting.rst` | `packages/machinome/docs/reference/viewer/` | lookup: versions, and symptoms with remedies |
| `docs/_static/demo.js`, `docs/_static/viewer-docs.css` | `packages/machinome/docs/_static/viewer-demo.js`, `viewer-demo.css` | the guide's click-to-load demo; named for what they serve in a manual of many subjects |
| `docs/index.rst`, `docs/installation.rst` | dropped | the landing's introduction goes to the section's index and its spinner to the operating guide; the install facts to the installation page, the source build to the contributor guide, the serve-a-build facts are already the command reference's (Decision 10) |
| `docs/conf.py`, `docs/Makefile`, `docs/requirements.txt` | dropped | the manual's own |
| `LICENSE` | dropped | one licence at the join; the package links the root's |
| `context7.json` | dropped | one index per repository; its rules fold into the root's |
| `.readthedocs.yaml` | dropped | the manual is the framework's; the project is retired by the pilot |
| `.github/workflows/ci.yml` | dropped | the repository's CI runs the widget's and the viewer's tests (Decision 8) |
| `scripts/check-dist` | dropped | the root's builds and smokes every member (Decision 9) |
| `web/__init__.py` | dropped | a vestige: it imports `.viewer`, which no commit since the layout of 5 September 2026 carries beside it, and no package ships it |
| `openscad.py` (history) | dropped | the framework's OpenSCAD viewer, never the viewer's; its four commits are pruned as empty (probe 1) |

The import lands files only where they live after the cycle; the files the
applier edits are edited in place, and a move and an edit never share a
commit. The rewritten commits keep their messages, authors and dates; the
original repository keeps every dropped file under the original hashes.

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/machinome-viewer <dir>`), as rehearsed in
probe 1 (`<scratch>/filter-repo-command.final.sh`):

```
PKG=machinome/viewer/web
D=packages/machinome-viewer
M=packages/machinome/docs
git filter-repo \
  --path LICENSE --path context7.json --path .readthedocs.yaml \
  --path .github/ --path scripts/check-dist \
  --path docs/conf.py --path docs/Makefile --path docs/requirements.txt \
  --path docs/index.rst --path docs/installation.rst \
  --path openscad.py --path web/__init__.py \
  --invert-paths \
  --path-rename README.md:$D/README.md \
  --path-rename CHANGELOG.md:$D/CHANGELOG.md \
  --path-rename pyproject.toml:$D/pyproject.toml \
  --path-rename MANIFEST.in:$D/MANIFEST.in \
  --path-rename .gitignore:$D/.gitignore \
  --path-rename scripts/check-docs-browser.py:$D/scripts/check-docs-browser.py \
  --path-rename __init__.py:$D/$PKG/__init__.py \
  --path-rename bundle.py:$D/$PKG/bundle.py \
  --path-rename browser.py:$D/$PKG/capture.py \
  --path-rename web/viewer.py:$D/$PKG/server.py \
  --path-rename web/app/:$D/$PKG/app/ \
  --path-rename widget/:$D/$PKG/widget/ \
  --path-rename solid_node_viewer/:$D/$PKG/ \
  --path-rename machinome_viewer/:$D/$PKG/ \
  --path-rename tests/:$D/tests/ \
  --path-rename openspec/:$D/openspec/ \
  --path-rename workflow/:$D/workflow/ \
  --path-rename docs/adrs/:$D/workflow/adrs/ \
  --path-rename docs/release-0.2.md:$D/workflow/release-0.2.md \
  --path-rename docs/reference/index.rst:$M/reference/viewer/index.rst \
  --path-rename docs/reference/:$M/reference/viewer/ \
  --path-rename docs/compatibility.rst:$M/reference/viewer/compatibility.rst \
  --path-rename docs/troubleshooting.rst:$M/reference/viewer/troubleshooting.rst \
  --path-rename docs/using-the-viewer.rst:$M/howto/browser-viewer.rst \
  --path-rename docs/sharing.rst:$M/howto/share-an-export.rst \
  --path-rename docs/embedding.rst:$M/howto/embed-the-viewer.rst \
  --path-rename docs/examples/:$M/howto/embed-the-viewer/ \
  --path-rename docs/_static/demo.js:$M/_static/viewer-demo.js \
  --path-rename docs/_static/viewer-docs.css:$M/_static/viewer-demo.css \
  --tag-rename ':viewer-'
```

Each rename names an explicit prefix of an original path. The root
`__init__.py`, `bundle.py` and `browser.py` match only themselves (no other
path begins with those names), and `web/viewer.py`, `web/app/` and `widget/`
only the pre-split tree. No catch-all `--to-subdirectory-filter`: part of the
product goes to the framework's manual.

**The tags** become `viewer-v0.7.0` to `viewer-v0.8.1`, the plan's method;
the framework's own `v0.7.0` to `v0.8.1` stand beside them. The annotations
keep their texts and point at the rewritten release commits, whose trees lack
the dropped files.

The orchestrator then checks that `git ls-tree -r --name-only main` lists the
893 paths of `<revise>/rehearsal-ls-files.web.txt` and that `main` is
1b41968, fetches `main` and
`refs/tags/viewer-*:refs/tags/viewer-*` into the bench, and merges `main`
with `git merge --allow-unrelated-histories` into the cycle's branch, one
merge commit, after the planning commit.

### 3. The package's directory

`packages/machinome-viewer/` after the cycle holds `pyproject.toml`,
`README.md`, `CHANGELOG.md`, `MANIFEST.in`, `.gitignore`, the links
`LICENSE -> ../../LICENSE` and `LICENSES -> ../../LICENSES`, the package
directory `machinome/viewer/web/` (its own `__init__.py`, none at
`machinome/` nor at `machinome/viewer/`: the core's package path admits the
portion at `machinome/`, and `machinome.viewer` is a namespace level with no
module of its own until the seam cycle writes one, probes 19 and 20),
`scripts/`, `tests/`, `openspec/` and `workflow/`.

`pyproject.toml`, replacing the product's (built, locked and smoked in probes
7, 11 and 12, at `machinome.viewer.web` in probe 19):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-viewer"
version = "0.8.1"
description = "The browser viewer for machinome models: the embeddable widget, the development server and the headless snapshot capture"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"
license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
license-files = ["LICENSE", "LICENSES/*.txt"]
authors = [
    { name = "Luis Fagundes", email = "lhfagundes@gmail.com" },
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Intended Audience :: Manufacturing",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Multimedia :: Graphics :: 3D Modeling",
]
keywords = ["machinome", "cad", "viewer", "three.js"]
dependencies = [
    # The framework this viewer is released with: the set carries one
    # version, and the pins between its packages are ~= both ways. The
    # viewer imports nothing of it; the framework reaches the viewer through
    # the entry point below and its command line.
    "machinome~=0.8.1",
    "fastapi>=0.111,<1",
    "uvicorn>=0.30,<1",
    # uvicorn serves WebSockets only through an optional library, and the
    # development page's live reload is one (/ws/reload).
    "websockets>=10.4",
]

[project.optional-dependencies]
# The headless capture behind `machinome snapshot --renderer web`. Chromium is a
# second, separate step: `playwright install chromium`.
snapshot = [
    "playwright",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[project.scripts]
machinome-viewer = "machinome.viewer.web.cli:main"

# How machinome finds the installed viewer: one entry point that resolves to
# a function returning the bundle path, the export page and the API version.
# Nothing else of this package is an interface to it. The group's name is
# the framework's lookup key, not a module.
[project.entry-points."machinome.viewer"]
bundle = "machinome.viewer.web.bundle:describe"

[tool.setuptools.packages.find]
# The package directory machinome/viewer/web/, which has its own
# __init__.py, with none at machinome/ nor at machinome/viewer/. The widget
# beside the modules is package data, not a package.
include = ["machinome.viewer.web"]
namespaces = true

[tool.setuptools]
include-package-data = true
zip-safe = false

[tool.setuptools.exclude-package-data]
"machinome.viewer.web" = [
    "widget/src/*",
    "widget/build.mjs",
    "widget/tsconfig.json",
    "widget/vitest.config.ts",
]

[tool.setuptools.cmdclass]
sdist = "machinome.viewer.web.packaging.BuildSourceDistribution"
build_py = "machinome.viewer.web.packaging.BuildPythonWithFrontend"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

The `docs` and `dev` extras go: the manual is the framework's, and the
workspace's dev group installs the tools (pytest, pillow, build, twine and
httpx through the core's `dev` extra, Playwright through `web-snapshot`,
setuptools through the lock, which `solidpython2` requires). The
`widget/package-lock.json` entry of the excluded data goes with the file. The
excluded data is keyed by the package, `machinome.viewer.web`: keyed by any
other name it excludes nothing, and the wheel ships the widget's 128 sources,
`build.mjs` and the two configurations (152 entries, probe 11).

`README.md`, replacing the product's, in the shape of the products before it:

```markdown
# machinome-viewer

The browser viewer of [Machinome](https://github.com/machinome/machinome):
the package `machinome.viewer.web`, an embeddable three.js widget with its export
page, the development server `machinome develop` runs and the headless
capture behind `machinome snapshot --renderer web`. It opens a published
model in a WebGL-capable browser, with camera, assembly navigation and the
controls of a posed, running or clocked machine.

## Install

    pip install "machinome[viewer]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`MANIFEST.in`, edited in place (probe 11):

```
include CHANGELOG.md
include scripts/check-docs-browser.py
recursive-include workflow *.md *.png
recursive-include openspec *.md *.yaml

# The frontend travels with its sources so a source distribution can
# rebuild it, and with its built output so installing needs no npm.
# develop.html is a package file here too, not a build output.
recursive-include machinome/viewer/web/widget *
prune machinome/viewer/web/widget/node_modules

recursive-include tests *
prune tests/_shots
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

`LICENSE`, `README.md`,
`.readthedocs.yaml` and the `docs` lines go: the licence files reach the
archives through `license-files`, the README through `readme`, and the
manual is the framework's.

`.gitignore`, edited in place to this package's own leavings (the root's
covers `__pycache__/`, `*.py[cod]`, `/packages/*/build/`,
`/packages/*/*.egg-info/`, `/.venv/` and `/.env`):

```
# This package's leavings the root's .gitignore does not name: its own test
# runs, a local build, the built bundle, the manual's browser review, and the
# screenshots tests/test_running_document.py writes for inspection (pixels
# are evidence, regenerated by running the test, not committed as bytes).
.pytest_cache/
dist/
_build/
/machinome/viewer/web/widget/node_modules
/tests/_shots
```

(`dist/` covers `widget/dist/`.)

**Headers.** Each of the 156 `SPDX-License-Identifier` lines of the 155
files of probe 17 (33 Python, 119 TypeScript, `develop.html`, `index.html`,
`build.mjs`'s file header) becomes `GPL-2.0-or-later OR CERN-OHL-S-2.0+` in
the comment syntax of its file; the other header lines stay, and a file with
no header gains none.

**The widget's `package.json`**: `"license": "GPL-2.0-or-later OR CERN-OHL-S-2.0+"`;
nothing else changes (`private`, the name `@machinome/viewer`, the version,
`machinomeViewerApi`, `machinomeDocumentVersions`, the scripts and
dependencies).

**The banner** (`build.mjs`): its SPDX line the set's expression, its
`Source:` line `https://github.com/machinome/machinome`, its three
`Bundles ...` notices unchanged; the comment above it says the banner names
the bundle's licence and its source and retains the bundled dependencies'
notices, without naming the licence it carried. Its first lines keep
`machinome-viewer <version> - viewer API <n>`, which the site's intake
reads.

### 4. The source at its address

- **Internal imports**: `machinome_viewer` becomes `machinome.viewer.web` in
  the eight modules' imports (`from machinome.viewer.web.bundle import ...`,
  `from machinome.viewer.web import __version__`), in `packaging.py`'s
  `_currency_name` and its error message, in its comment citing
  `MANIFEST.in` (`machinome/viewer/web/widget`), and in `__main__.py`'s and
  `cli.py`'s docstrings (`python -m machinome.viewer.web`). The docstrings
  that name the `machinome.viewer` entry point keep the group's name.
- **Docstrings that state the separation**: `__init__.py` ("machinome
  reaches all of it through one entry point and three commands; it never
  imports this package's code") stays true and stays. `bundle.py`'s,
  `cli.py`'s and `capture.py`'s name the framework and the commands, and
  stay. `capture.py`'s `PLAYWRIGHT_REMEDY` names `pip install
  'machinome-viewer[snapshot]'`, which still installs it, and stays.
  `cli.py`'s comment citing `machinome/manager/develop.py:49-51` becomes
  `packages/machinome/machinome/manager/develop.py`.
- **`currency.py`, the dependencies where npm installs them** (probe 6).
  `_require_dependencies` accepts the build program installed in the widget
  directory or in any ancestor, `node_modules/esbuild` found by walking up
  from the widget as Node resolves `build.mjs`'s `import 'esbuild'`; absent
  everywhere, the refusal and its remedy are unchanged (`cd <widget> && npm
  ci && npm run build`, which installs at the workspace root, probe 5).
  The module still imports only the standard library, and the walk visits
  directories, never `node_modules`' contents.
- **`packaging.py`, the guard where npm writes** (probe 5). `build_frontend`
  refuses before `npm ci` when any `node_modules` from the widget directory
  up to the filesystem root is a symbolic link, naming it: inside the
  workspace `npm ci` writes the root's `node_modules`, and a bench whose root
  `node_modules` links another checkout's would empty it, the failure the
  guard was written for. `build_stale_frontends` and the sdist hook are
  otherwise unchanged.
- **The widget's tests** (probe 4): the 26 lines of 14 test files under
  `src/` that read `tests/fixtures/` by a relative path gain two `../`, the
  widget sitting two levels deeper than at bd2bf75
  (`../../../../../tests/fixtures` from `src/`,
  `../../../../../../tests/fixtures` from its subdirectories).

### 5. The npm workspace

- **The root `package.json`**:

  ```json
  {
    "name": "machinome-repository",
    "private": true,
    "workspaces": [
      "packages/machinome-viewer/machinome/viewer/web/widget"
    ]
  }
  ```

  No version, no scripts, no dependencies: the root is no package of its own,
  as its `pyproject.toml` is no distribution. A later member is added to
  `workspaces` by its own join.
- **The lockfile moves to the root** (Open Questions 3): the widget's
  `package-lock.json` is copied to the root by `git mv` in the implementation
  commit's first step, its top-level `"version"` removed, and `npm install
  --no-audit --no-fund` run at the root, which turns it into the workspace's
  lock with the same 174 resolutions (probe 5); the widget keeps none. `npm
  ci` at the root installs the set; run inside the widget it does the same.
- **The root `.gitignore`** gains `/node_modules/` beside `/.venv/`.
- **The version in the lock** is the member's entry alone. The release pass
  runs `npm install --package-lock-only` after the bump, which rewrites it
  (probe 5); `tests/test_release_records.py` holds it to the set's version
  (Decision 7), since `npm ci` does not.
- **The bundle** is built by `npm run build` from the widget's directory, or
  `npm run build --workspaces --if-present` from the root, by the package's
  hooks when a wheel or an sdist is built, and by the currency check when a
  source checkout's bundle is stale; it is ignored and never tracked.

### 6. The pins, the uv workspace and the bench venv

- The viewer requires `machinome~=0.8.1` (Decision 3), the core's
  `viewer = ["machinome-viewer~=0.8.1"]` and
  `web-snapshot = ["machinome-viewer[snapshot]~=0.8.1"]`, with the comment
  above them: "The browser viewer, `machinome.viewer.web`, the repository's
  distribution machinome-viewer, released with the framework and reached
  only as a separate process; the framework is complete for non-interactive
  use without it. The web snapshot renderer needs the viewer and its
  browser; Chromium itself is a second step: `playwright install chromium`."
- The core's `dev` extra gains `"machinome[web-snapshot]"` after
  `"machinome[all]"`, with a comment: the suite and the viewer's tests
  photograph through the viewer. The root's dev group is unchanged
  (`["machinome[dev]", "machinome[mechanics]"]`).
- The root's sources gain `machinome-viewer = { workspace = true }` after
  `machinome-node-stl`; `exclude-dependencies = ["machinome-studio"]`, its
  comment naming the studio alone.
- `uv lock`: "Resolved 192 packages", the diff of probe 7. `uv sync --python
  3.12`: fourteen `__editable__` `.pth` files. Then, from `/tmp`, the bench
  venv's Python imports `machinome.viewer.web` from
  `packages/machinome-viewer/machinome/viewer/web/__init__.py`, `machinome.viewer`
  is a namespace level whose one path entry is
  `packages/machinome-viewer/machinome/viewer`, and `python -m
  machinome.viewer.web describe` answers once the bundle is built (probe
  19).
- **Chromium for the locked Playwright** (probe 8): the lock resolves
  Playwright 1.63.0, whose Chromium revision 1243 this machine lacks. The
  viewer's browser tests need `playwright install chromium` run once with the
  bench venv's Playwright (it writes `~/.cache/ms-playwright`, outside every
  repository); the brief forbids the proposer and the applier that command,
  so it is the orchestrator's (Open Questions 6). Without it, 107 browser
  tests fail on "Executable doesn't exist"; they do not skip.

### 7. The core

- **`machinome/viewers/bundle.py`**: `viewer_command()` returns
  `[sys.executable, '-m', 'machinome.viewer.web']`; the
  module docstring says the viewer is `machinome-viewer`, the repository's
  package installed through the `viewer` extra, and drops "separately
  licensed"; `INSTALL_REMEDY` says "It is the package machinome-viewer;
  install it with: pip install "machinome[viewer]"". Nothing else.
- **The core's tests that spell the viewer's module**:
  `tests/test_viewer_bundle.py` (the expected command), `test_browser_renderer.py`
  and `test_manager_develop.py` (`VIEWER`), `test_cli_lazy_imports.py`
  (`machinome.viewer.web.server`, `machinome.viewer.web.capture`).
  `test_viewer_bundle.py`'s fake report paths
  (`/site/machinome_viewer/widget/...`) are data of a mocked entry point and
  stay.
- **`machinome.viewers` beside `machinome.viewer`.** The core's module
  directory `machinome/viewers/` (the seam's reader, `bundle.py`, and the
  web snapshot's staging, `browser.py`) and the namespace level
  `machinome.viewer` that the viewer's package sits under are two names one
  letter apart until the `viewer-seam` cycle moves `viewers/` under the
  seam; nothing resolves one for the other (probe 19), and the entry-point
  group `machinome.viewer` is a string in the viewer's metadata, read by
  `importlib.metadata`, never imported.
- **The vet universe** (probe 21). `machinome vet` admits the contract
  member `machinome` whole but its denylist, so at this address an import of
  `machinome.viewer.web.server` passes where `machinome_viewer.server` was
  `outside-universe`. The viewer serves (`server`), drives Chromium
  (`capture`) and runs npm (`currency`, `packaging`): the class of module the
  contract's denylist exists for. `machinome/vet/universe.toml`'s
  `[contract] deny` gains `"machinome.viewer.web"` after
  `"machinome.viewers"`, with a comment naming the change; a vetted file that
  reaches it is `framework-internal`, named `machinome.viewer.web`.
  `machinome.viewer` itself is not denied: it holds no module of its own
  until the seam, and the seam the `viewer-seam` cycle writes there is that
  cycle's to judge.
  `tests/test_vet_universe.py`: `test_the_contract`'s tuple gains the entry,
  and a new `test_the_browser_viewer_is_internal_and_its_former_name_outside`
  vets two scratch projects as the mechanics test does (red at the join: the
  first import passes).
- **The layout gate**, `tests/test_repository_layout.py`. `PRODUCTS` gains:

  ```python
      'machinome-viewer': ('machinome.viewer.web', 'viewer',
                           ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                            'LICENSES', 'MANIFEST.in', 'README.md',
                            'machinome', 'openspec', 'pyproject.toml',
                            'scripts', 'tests', 'workflow')),
  ```

  `TheProductsTest.test_each_product_directory_holds_its_package_and_its_record`
  refuses an `__init__.py` at every level above the package directory, not
  at `machinome/` alone: for `machinome.viewer.web`, at `machinome/` and at
  `machinome/viewer/` (an `__init__.py` there would make the product ship the
  seam's level, which is the core's to write, probe 20); for `machinome.mechanics` the
  check is the one the layout gate makes at 484a528f.
  `TheProductsTest.test_each_product_keeps_its_tests_and_specs` requires a
  `tests/` directory holding a `test_*.py` module and an `openspec/specs/`,
  not a `tests/pyproject.toml`, which the mechanics tests carry to be a
  project and the viewer's do not need. A new class,
  `TheNodeWorkspaceTest`: the root `package.json` is private, has no
  `version`, and its `workspaces` are exactly the widget's directory; one
  `package-lock.json` in the tracked tree, at the root, whose member entry
  names `@machinome/viewer`; the root `.gitignore` names `/node_modules/`;
  no tracked path holds `node_modules/` or `widget/dist/`.
  `TheRootIsTheRepositorysTest.test_the_repository_s_files_are_there` gains
  `package.json` and `package-lock.json`.
  `TheContinuousIntegrationTest` gains
  `test_the_test_job_builds_and_tests_the_widget_before_the_suite` (a
  `setup-node` step, then `npm ci`, `npm run typecheck`, `npm test` and `npm
  run build` at the root, all before "Run tests", and `playwright install
  --with-deps chromium` before the viewer's pytest step) and
  `test_the_dist_job_sets_up_node_before_checking` (a `setup-node` step
  before `scripts/check-dist`). The module's docstring names the viewer and
  the change.
- **The release records**, `tests/test_release_records.py`:
  `test_the_viewer_extras_floor_at_the_matching_viewer` becomes
  `test_the_viewer_extras_pin_the_set_s_viewer`: each of the two extras is
  `machinome-viewer` (with `[snapshot]` for `web-snapshot`) `~=` the
  version; `test_every_pin_between_members_is_compatible` already holds the
  viewer's `machinome~=` and is green once the extras move. A new
  `test_the_viewer_s_version_files_agree`: `machinome/viewer/web/__init__.py`'s
  `__version__`, the widget's `package.json` `version` and the root
  `package-lock.json` member entry's `version` equal the set's, and
  `.bumpversion.cfg` names the first two. The docstring's "Every package of
  the repository carries the framework's version, but the mechanics helpers"
  gains "; the viewer's Python package, its widget and the root's npm lock
  carry it too (change `join-viewer`)".
- **`.bumpversion.cfg`** gains, after the FreeCAD package's tables:
  `[bumpversion:file(version):packages/machinome-viewer/pyproject.toml]`
  (`version = "{current_version}"`),
  `[bumpversion:file(pin):packages/machinome-viewer/pyproject.toml]`
  (`"machinome~={current_version}"`),
  `[bumpversion:file:packages/machinome-viewer/machinome/viewer/web/__init__.py]`
  (`__version__ = "{current_version}"`),
  `[bumpversion:file:packages/machinome-viewer/machinome/viewer/web/widget/package.json]`
  (`"version": "{current_version}"`) and
  `[bumpversion:file(viewer):packages/machinome/docs/conf.py]`
  (`viewer_version = '{current_version}'`). The core's two extras end in
  `~=0.8.1"` and are moved by its existing `(pins)` table. No table for the
  lock (probe 15). The applier proves the bump on a copy (task 8.1).
- **`docs/conf.py`**: `viewer_version = '0.8.1'` stays, its comment "the
  viewer, numbered with the set (`packages/machinome-viewer/pyproject.toml`)";
  `viewer_api` and `document_versions` stay literals, held to the widget's
  `package.json` by a test (Decision 10, Open Questions 4). The path list
  for autodoc leaves out `packages/machinome-viewer` (probe 14):
  `*(path for path in sorted(glob.glob(os.path.abspath('../../machinome-*')))
  if os.path.basename(path) != 'machinome-viewer')`, with a comment: the
  manual takes the viewer it completes exports with from what
  `docs/requirements.txt` installs.
- **`tools/generate_parity_fixture.py`**: with no argument it writes the
  viewer package's committed fixture in the same repository,
  `ROOT/../machinome-viewer/machinome/viewer/web/widget/src/parity-fixture.json`
  (`ROOT` the framework's directory), refusing before it builds when that
  directory is absent, naming it and the output argument; no Git command is
  run. `VIEWER_FIXTURE` and the module docstring follow. Its test,
  `tests/test_generate_parity_fixture.py`, `DefaultFixturePathTest`:
  the default resolves under a temporary repository's
  `packages/machinome-viewer/...` from its `packages/machinome/`, the
  refusal names the directory and the argument, the refusal comes before a
  build, an explicit path is written; the worktree and Git-common-directory
  cases go with the behaviour they tested.

### 8. CI

`.github/workflows/python-app.yml`:

- **`test`**: after the workspace's sync, at the root (`working-directory:
  .`):

  ```yaml
      # The browser viewer's widget is the npm workspace's member (change
      # `join-viewer`): one install at the root, its typecheck and tests,
      # and the bundle the suite and the viewer's tests photograph through.
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
          cache-dependency-path: package-lock.json

      - name: Build and test the widget
        working-directory: .
        run: |
          npm ci --no-audit --no-fund
          npm run typecheck --workspaces --if-present
          npm test --workspaces --if-present
          npm run build --workspaces --if-present
  ```

  then "Run tests" unchanged, then the mechanics step, then:

  ```yaml
      # The viewer keeps its tests in its own directory; its browser tests
      # need Chromium for the Playwright the lock installs.
      - name: Run the viewer package's tests
        working-directory: packages/machinome-viewer
        run: |
          playwright install --with-deps chromium
          python -m pytest
  ```
- **`browser-snapshot`**: the step installing `machinome-viewer[snapshot] @
  git+https://github.com/machinome/machinome-viewer.git` becomes the root's
  `npm ci` and build of the widget and `playwright install --with-deps
  chromium`; the synced workspace already installs the viewer with
  Playwright.
- **`dist`**: `actions/setup-node@v4` with Node 22 before "Check the
  distributions": the viewer's sdist builds its bundle.
- **`lint`** reads `../machinome-*/machinome`, which holds the viewer's
  modules at `machinome/viewer/web/` (3 flake8 lines; `black --check` would
  reformat 6 of the 8 modules, counted at the first draft's address, the
  same files); it is `continue-on-error`, unchanged.
- **`docs`** is unchanged: it installs `docs/requirements.txt`, the published
  viewer among them, and needs no Node.

### 9. `scripts/check-dist`: one row, installed from its wheel

The product's own script is dropped; the root's builds every member and needs
a row for `machinome-viewer`, or it fails "machinome-viewer has no smoke in
scripts/check-dist". The viewer's sdist runs its hook, which needs Node and
npm: `main` refuses at its start, before building, when `npm` is not on the
PATH while the viewer is a member ("machinome-viewer's bundle is built by
npm; put Node 22 and npm on the PATH"). The docstring's requirements gain
Node and npm, and its account of what the script writes inside the
repository gains the root's `node_modules/` and the widget's `dist/`.

The row has no `through`, as the mechanics row: once the original
repository's 0.8.1 is uploaded, the index serves a `machinome-viewer` 0.8.1
whose import is the former one, and pip may take it over the built wheel of
the same version (join-mechanics' probe 11); installed by path, the built
wheel is the one smoked, and the core's extras are proved from the core's
metadata. The row, after the mechanics package's, the API read once at the
top beside `MECHANICS_VERSION` (the script gains `import json`):

```python
#: What the viewer's widget declares (change `join-viewer`): the report and
#: the bundle's banner must state it.
VIEWER_WIDGET = json.loads(
    (ROOT / 'packages/machinome-viewer/machinome/viewer/web/widget/package.json')
    .read_text())
VIEWER_API = VIEWER_WIDGET['machinomeViewerApi']
VIEWER_DOCUMENTS = VIEWER_WIDGET['machinomeDocumentVersions']
```

```python
    'machinome-viewer': {
        # Installed from its wheel by path, not through `machinome[viewer]`:
        # the index may serve another wheel of the same version, whose
        # import is the former one, and pip may take it.
        'extras': [],
        'code': f'''
import importlib.metadata as metadata
from pathlib import Path
import machinome.viewer.web as viewer
from machinome.viewers.bundle import describe, viewer_command
distribution = metadata.distribution('machinome-viewer')
version = metadata.version('machinome')
assert distribution.version == version, (distribution.version, version)
files = [str(path) for path in distribution.files]
shipped = sorted(path for path in files
                 if path.startswith('machinome/') and path.endswith('.py'))
assert shipped == [f'machinome/viewer/web/{{module}}.py' for module in (
    '__init__', '__main__', 'bundle', 'capture', 'cli', 'currency',
    'packaging', 'server')], shipped
assert not [path for path in files
            if '/widget/src/' in path or 'node_modules' in path], files
owned = Path(distribution.locate_file(shipped[0])).resolve()
assert owned == Path(viewer.__file__).resolve(), (owned, viewer.__file__)
assert owned.is_relative_to(Path(VENV).resolve()), owned
assert f'machinome~={{version}}' in distribution.requires, distribution.requires
core = metadata.requires('machinome')
for extra in ('viewer', 'web-snapshot'):
    assert any(line.startswith('machinome-viewer')
               and f'~={{version}}' in line
               and extra in line.partition(';')[2] for line in core), (extra, core)
(entry,) = [entry for entry in metadata.entry_points(group='machinome.viewer')
            if entry.name == 'bundle']
assert entry.value == 'machinome.viewer.web.bundle:describe', entry.value
assert viewer_command()[1:] == ['-m', 'machinome.viewer.web'], viewer_command()
report = describe()
for key in ('path', 'index'):
    found = Path(report[key]).resolve()
    assert found.is_file() and found.is_relative_to(Path(VENV).resolve()), report
assert report['version'] == version, report
assert report['apiVersion'] == {VIEWER_API!r}, report
assert report['documentVersions'] == {VIEWER_DOCUMENTS!r}, report
head = Path(report['path']).read_text()[:600]
for line in (f'machinome-viewer {{version}} - viewer API {VIEWER_API}',
             'SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+',
             'Source: https://github.com/machinome/machinome'):
    assert line in head, (line, head)
'''
        + LICENCES.substitute(name='machinome-viewer')
        + '''
print('machinome-viewer', distribution.version, 'module', viewer.__file__,
      'API', report['apiVersion'], 'documents', report['documentVersions'][0],
      'to', report['documentVersions'][-1])
''',
        'commands': [['machinome-viewer', 'describe'], ['machinome', 'viewer']],
    },
```

The shipped-files assertion also proves the wheel carries no
`machinome/__init__.py` and no `machinome/viewer/__init__.py`, and the
source assertion refuses a wheel whose excluded data is keyed by another name
than the package (probe 11). Probe 12 ran this smoke at
`machinome.viewer.web` but the banner's two licence lines, which the
applier's edits make true. Red first: before the row the script fails naming
the package.

### 10. The manual

By reader intent, under `skills/write-the-manual/SKILL.md`:

| page | section | from |
|---|---|---|
| `howto/browser-viewer.rst`, "Inspect and operate a machine in the viewer" | How-to guides, after `howto/mechanism-formulas` | `using-the-viewer.rst`, with the landing page's "Try the viewer" |
| `howto/share-an-export.rst`, "Share an export and take a still" | How-to guides, after the above | `sharing.rst` |
| `howto/embed-the-viewer.rst`, "Embed the viewer in a page" | How-to guides, after the above | `embedding.rst` and its `examples/` |
| `reference/viewer/index.rst`, "Browser viewer" | Reference, after `reference/mechanics/index` | the reference index, with the landing page's introduction |
| `reference/viewer/{mount,viewer-handle,layouts,running,clocked,cli,compatibility,troubleshooting}.rst` | the section, in that order | the six reference pages, `compatibility.rst`, `troubleshooting.rst` |

- **Three how-to guides and one reference section.** A maker operates a
  machine, publishes one, or puts one in a page: one job a page. A host looks
  up a mount option, a handle member, a running or clocked call, a command
  option, a version rule or a symptom: lookup, beside the API and the
  mechanics helpers. The six reference pages keep their titles but `cli`'s,
  which becomes "The machinome-viewer command" (two pages titled
  "Command-line reference" would share the manual's search and index).
- **The section's index**, rewritten in place: the title "Browser viewer";
  the landing page's first two paragraphs (what the viewer does, its three
  homes), with "the viewer is the package ``machinome-viewer``, installed by
  ``machinome[viewer]`` and numbered with the framework; it declares viewer
  API |viewer_api| and reads document versions |document_versions|"; the
  reference index's paragraph on `MachinomeViewer` and its handles; the
  toctree (`mount`, `viewer-handle`, `layouts`, `running`, `clocked`, `cli`,
  `compatibility`, `troubleshooting`); its link to the embedding guide
  `:doc:`/howto/embed-the-viewer``. No licence sentence, no version note.
- **The operating guide**, `howto/browser-viewer.rst`, converted in place: an
  opening that installs (`pip install "machinome[viewer]"`) and opens a
  project (`machinome develop`, from the dropped `installation.rst`), the
  landing page's "Try the viewer" with its button (`data-viewer-demo=
  "embed-the-viewer/embed.html"`), then its own sections unchanged in
  substance; `:doc:` links absolute (`/reference/viewer/troubleshooting`).
- **The sharing guide**: its two links to the framework's pages become
  `:doc:` links (`/tutorial/10-share`, `/reference/cli`); its licence
  paragraph becomes "The bundle carries its licence and the notices of the
  libraries it bundles. Preserve them when you redistribute it; it is
  licensed |framework_licence|, at the recipient's choice, as every package
  of Machinome."; `:doc:`snapshot extra and Chromium <installation>``
  becomes `:doc:`web-snapshot extra and Chromium </start/install>``.
- **The embedding guide**: the includes and the demo name
  `embed-the-viewer/embed.html` and `embed.js`; its `:doc:` links absolute.
- **The reference pages**: `|package-version|`, `|viewer-api|` and
  `|document-versions|` become `|viewer_version|`, `|viewer_api|` and
  `|document_versions|` (the framework's value reads "1 to 13"; the
  sentences that use it read so); relative `:doc:` links to the dropped or
  moved pages become section-relative or absolute (19 of probe 13);
  `compatibility.rst`'s "The 0.8.1 release declares:" becomes "This release
  declares:", its sentence "It does not import Machinome or load project
  Python code" becomes "It loads no project Python code", and its link to the
  framework's upgrading page a `:doc:` link; `cli.rst`'s opening sentence
  "``python -m machinome_viewer`` is equivalent" names ``python -m
  machinome.viewer.web``, its describe example shows
  `/installation/machinome/viewer/web/widget/...` paths, and its
  `:doc:`../installation`` becomes `:doc:`/start/install``;
  `troubleshooting.rst`'s source-build commands become `npm ci` and `npm run
  build --workspaces` from the repository's root.
- **The installation page**, `start/install.rst`: "Packages and licences"
  names ``machinome-viewer`` among the packages of the set, all licensed
  |framework_licence|, the viewer reached as a separate process; the
  `web-snapshot` sentence gains the second step, `playwright install
  chromium`; one sentence from the dropped page: a host that only serves or
  captures published documents installs ``machinome-viewer`` alone, which
  brings the framework it is numbered with.
- **The framework's pages that link the separate manual or state the
  viewer's separate licence**, each rewrapped at its width, the rest of each
  page unchanged: `concepts/publishing.rst` (its section "The viewer": the
  viewer is the package ``machinome-viewer`` of this repository, installed
  through the ``viewer`` extra and reached only as a separate process; the
  three links to the separate manual become `:doc:` links to
  `/howto/browser-viewer`, `/reference/viewer/index` and
  `/howto/embed-the-viewer`); `tutorial/10-share.rst` (its link,
  `:doc:`/howto/embed-the-viewer``); `reference/cli.rst` (the `develop`
  paragraph names the package without the repository link; "See the viewer
  manual for source development" becomes "See :doc:`/project/contributing`
  for source development"); `reference/manuals.rst` (the opening: "The
  browser viewer and the mechanics helpers are documented in this manual,
  under :doc:`/reference/viewer/index` and :doc:`/reference/mechanics/index`;
  the libraries below have manuals of their own." and the Machinome Viewer
  entry goes); `project/status.rst` ("Packages": the viewer is the package
  ``machinome-viewer``, numbered and licensed with the framework, installed
  through the ``viewer`` extra; "the independent browser viewer" at line 22
  becomes "the browser viewer"); `why.rst` (its licence sentence drops the
  viewer's: "The framework and its packages are licensed |framework_licence|,
  at the recipient's choice, and example designs retain their own
  licences."); `project/upgrading.rst` ("Install a matching viewer": the
  viewer is installed through the ``viewer`` extra, whose pin follows the
  framework's release; the 0.7 part's sentence on the independent viewer
  loses the identifier); `project/contributing.rst` (browser-viewer changes are
  changes of this repository, `packages/machinome-viewer/`);
  `project/changelog.rst`'s two released lines naming the viewer's licence
  lose the identifier in place (Open Questions 7).
- **`docs/conf.py`**: `html_js_files = ['viewer-demo.js']`,
  `html_css_files = ['viewer-demo.css']`, and a `setup(app)` connecting a
  `build-finished` handler that, for the HTML builder, copies
  `howto/embed-the-viewer/` beside the built guide, the committed spinner
  export into it as `spinner/`, and the installed viewer's bundle, read
  through `machinome.viewers.bundle.bundle_path()`, as
  `machinome-viewer.js` (probe 13). The source path of Decision 7.
- **The committed export**: `docs/_exports/spinner/` (`manifest.json` and
  its two models), a copy of the viewer's test fixture `tests/fixtures/spinner`,
  the widget-less export of the framework's spinner project that the
  example loads; `docs/_exports/` holds every export a page shows.
- **`_static/viewer-demo.css`**: the rules for the demo's frame and button and
  for the JavaScript domain's entries on narrow screens; the rule that
  wrapped every table cell of the manual goes (Open Questions 8).
- **The proof of the pages**: the widget's `documentation.test.ts` reads
  `packages/machinome/docs/reference/viewer/` for every public member and
  mount; the viewer's `tests/test_documentation.py` reads the folded pages
  (Decision 11); the framework's `test_docs_structure.py` pins the toctrees
  and the facts; `scripts/check-docs-browser.py`, adapted, runs the
  reference's scripted examples and the embedding page in Chromium against
  the built manual.

### 11. The tests at their new place

- **Imports**: `machinome_viewer` becomes `machinome.viewer.web` in the 24
  test modules and `support.py` (`from machinome.viewer.web... import`,
  `import machinome.viewer.web`, `[sys.executable, '-m',
  'machinome.viewer.web', ...]`), and a path written `ROOT /
  'machinome_viewer' / ...` becomes `ROOT / 'machinome' / 'viewer' / 'web' /
  ...`; no other line of the behaviour modules changes (probe 8: every
  behaviour test passes at the address).
- **`tests/test_licence.py`**, rewritten: the grant is the set's expression,
  read from the core's manifest; both manifests (`license`,
  `license-files`) and the widget's `package.json` state it; every SPDX line
  of every tracked file of the package (`git ls-files packages/machinome-viewer`)
  outside its archived records (`openspec/changes/archive/`,
  `workflow/archive/`, `workflow/adrs/`, `workflow/evidence/`) states it; the
  banner template and a built bundle open with it and with
  `Source: https://github.com/machinome/machinome`; the README states the
  manual's `framework_licence` words. It names no other licence: a header
  carrying any other expression fails the equality.
- **`tests/test_machinome_identity.py`**, rewritten: the manifest's name,
  `scripts`, entry point and package search (Decision 3); its dependencies
  hold `machinome~=` the version; `machinome/viewer/web/__init__.py` a file
  and `machinome/__init__.py`, `machinome/viewer/__init__.py`,
  `machinome_viewer/` and `solid_node_viewer/` absent; Homepage `https://github.com/machinome/machinome`; the build and
  global names and the loader's legacy formats as at bd2bf75.
- **`tests/test_documentation.py`**, rewritten for the folded manual:
  `REPOSITORY = Path(__file__).resolve().parents[3]`, the pages under
  `packages/machinome/docs/` (the three how-tos and the section); the pages
  exist and the manual's own build files do not exist in the package
  (`docs/`, `.readthedocs.yaml`); the decision log and release records stay
  in `workflow/`; the changelog's first release section is `0.8.1 — 10
  October 2026` with one `Unreleased` section admitted above it, which names
  the viewer API; every CLI option is in `reference/viewer/cli.rst`; its
  `describe` example's version, API and document versions are the
  manifest's and the widget's; `conf.py`'s `viewer_api` is the widget's
  `machinomeViewerApi` and its `document_versions` reads "<first> to <last>"
  of `machinomeDocumentVersions`; the full-screen, profile-contact, film
  annotation and on-demand facts read the same pages at their new paths;
  no page or the README links `machinome-viewer.readthedocs.io`; the
  manifest names no documentation URL but the Homepage.
- **`tests/test_version.py`**: the three declarations and the changelog, at
  their paths.
- **`tests/test_packaging.py`**: a new
  `test_packaging_refuses_a_shared_workspace_root` (a temporary widget whose
  parent's `node_modules` is a symbolic link: `RuntimeError` naming it,
  before any `npm` runs). Red at the join: the guard reads the widget's
  `node_modules` only.
- **`tests/test_currency.py`**: a new
  `test_a_stale_bundle_with_hoisted_dependencies_is_rebuilt` (a temporary
  widget with `node_modules/esbuild` in its parent and none in itself, a
  source newer than the bundle, the build command replaced by a recorder: the
  rebuild runs). Red at the join: "the widget's dependencies are not
  installed".
- **`tests/test_bundle.py`**: the standard-library-only set of `bundle.py`'s
  imports names `machinome.viewer.web` and `machinome.viewer.web.currency`
  (the package's `from machinome.viewer.web import __version__` and its
  currency module).
- **`tests/test_curta_drawing.py`**: unchanged; its default reads the
  Curta's builds two levels above the package directory, the workspace from
  the primary checkout, and on a bench `MACHINOME_CURTA_BUILDS` names them.
- **The widget**: `documentation.test.ts` reads
  `<repository>/packages/machinome/docs/reference/viewer`, its root seven
  levels above `src/` (`new URL('../../../../../../../', import.meta.url)`,
  probe 4); the fixture paths of Decision 4.
- **`scripts/check-docs-browser.py`**: `REPOSITORY` and the manual's built
  HTML (`packages/machinome/docs/_build/html` or its first argument), the
  section's pages and the three how-tos as its pages, the reference's
  scripts read from `packages/machinome/docs/reference/viewer/`, the
  fixtures from `packages/machinome-viewer/tests/fixtures`, the example at
  `howto/embed-the-viewer/embed.html`, its artifacts under the package's
  `_build/docs-review`.

A contributor runs the widget's tests with `npm test --workspaces` from the
root and the viewer's with `python -m pytest` from
`packages/machinome-viewer`; the core's suite does not collect them.

### 12. The records

- **`HISTORY.rst`**, at the end of `Unreleased`, after the mechanics bullet:

  ```
  * **The browser viewer joins the repository.** machinome-viewer,
    published from a repository of its own, is the package
    ``machinome-viewer`` at ``packages/machinome-viewer/``, its history
    kept: its Python package is ``machinome.viewer.web`` (formerly
    ``machinome_viewer``), run by the framework as ``python -m
    machinome.viewer.web``, and its widget is the first member of the
    repository's npm workspace, installed by one ``npm ci`` at the root. It
    is numbered with the set, pinned ``~=`` both ways by the ``viewer`` and
    ``web-snapshot`` extras, and licensed as every package of the
    repository; it keeps its changelog, specs, decision log and tests in its
    directory, and its manual is part of this one. The framework still finds
    it through the ``machinome.viewer`` entry point and runs it as a
    separate process, and ``machinome vet`` refuses a model that reaches it.
    Change ``join-viewer`` (ADR-188).
  ```
- **`docs/project/changelog.rst`**, at the end of `Unreleased`:

  ```
  * **The browser viewer is part of this manual.** Operating a machine in the
    viewer, sharing an export and embedding the viewer are how-to guides
    (:doc:`/howto/browser-viewer`, :doc:`/howto/share-an-export`,
    :doc:`/howto/embed-the-viewer`), and its browser API, its command and
    its compatibility are the reference section
    :doc:`/reference/viewer/index`. ``pip install "machinome[viewer]"``
    installs it, numbered with the framework. Its Python package is
    ``machinome.viewer.web`` (formerly ``machinome_viewer``): a script that
    ran ``python -m machinome_viewer`` runs ``python -m
    machinome.viewer.web`` or the ``machinome-viewer`` command, which is
    unchanged.
  ```
- **The viewer's `CHANGELOG.md`**, a `## Unreleased` section above `0.8.1`:

  ```
  ## Unreleased

  - Machinome Viewer is part of the Machinome repository,
    <https://github.com/machinome/machinome>, at
    `packages/machinome-viewer/`, with its history. Its Python package is
    `machinome.viewer.web` (formerly `machinome_viewer`), a portion of the
    `machinome` package, and `python -m machinome.viewer.web` runs its command;
    the `machinome-viewer` command, the `machinome.viewer` entry point, the
    bundle, viewer API 29 and document versions 1 through 13 are unchanged.
    It is numbered with Machinome and requires the matching release, and it
    is licensed as every package of the repository, GPL-2.0-or-later or
    CERN-OHL-S-2.0-or-later, at the recipient's choice; the bundle's banner
    says so. Its manual is part of Machinome's,
    <https://machinome.readthedocs.io>. The widget builds from the
    repository's npm workspace, one `npm ci` at the root; its own lockfile is
    retired.
  - A source checkout rebuilds a stale bundle when npm installed the
    widget's dependencies at the workspace root, and packaging refuses a
    symbolic `node_modules` at the workspace root as it refuses one in the
    widget.
  ```

  The 0.7.0 section's identity bullet loses the licence word in place (Open
  Questions 7): "Package `machinome-viewer`, import `machinome_viewer`, entry
  point `machinome.viewer`. The framework reaches it only through that entry
  point and separate processes; ..." rewrapped.
- **`CREDITS.md`** (the framework's, `packages/machinome/CREDITS.md`): a
  section "### Bundled in the browser viewer" before the historical one:
  "`machinome-viewer.js`, the bundle the `machinome-viewer` distribution
  carries and every export copies, contains these packages; their notices
  open the bundle." with three entries: three.js 0.156.1 (MIT License,
  Copyright 2010-2023 three.js authors), jokenizer 1.0.1 (MIT License,
  Copyright (c) 2018 Umut Özel), molejo 0.2.0 (the licence its
  `LICENSE` file and the banner name, Copyright (C) 2026 Luis Henrique Cassis
  Fagundes, its `NOTICE` retained); the
  historical section's last sentence becomes "The viewer, its successor, is
  the repository's `machinome-viewer`; the framework's own distribution
  contains no JavaScript." These licences are the bundled libraries' own,
  stated as their provenance.
- **`docs/architecture.md`**: "Viewers (VIEWER-WEB · specs
  `viewer-distribution`, `cli`)" begins "The browser viewer is the
  repository's distribution `machinome-viewer` at
  `packages/machinome-viewer/`, the package `machinome.viewer.web`, numbered
  with the framework and installed through the `viewer` extra (ADR-068,
  ADR-103, ADR-188); the framework is complete for non-interactive use
  without it.";
  "`sys.executable -m machinome_viewer`" becomes "`sys.executable -m
  machinome.viewer.web`"; "relocated to the viewer repository under their
  original numbers" becomes "kept in the viewer's own decision log,
  `packages/machinome-viewer/workflow/adrs/`, under their original numbers";
  the diagram's label for the viewer (its separate package and own process)
  reads "machinome-viewer (own process)"; the Map's "Viewer lookup & snapshot
  staging" row's last cell "015, 018, 041, 068, 103, 188 (the viewer itself:
  `packages/machinome-viewer/`)".
- **The root `README.md`**: a row after the mechanics package's:
  ``| [`machinome-viewer`](packages/machinome-viewer/) | The browser viewer, `machinome.viewer.web`: the embeddable widget, the development server and the headless capture; installed by `machinome[viewer]`. |``
- **`packages/machinome/README.rst`**: the "Install" sentences "The browser
  viewer is a separate package, `Machinome Viewer <...>`_, licensed ...,
  which the framework reaches only as a separate process; the ``viewer``
  extra installs it." become "The browser viewer is the package
  ``machinome-viewer``, which the framework reaches only as a separate
  process; the ``viewer`` extra installs it."; the "Licence" sentence
  "Machinome Viewer is a separate ... package." goes. Nothing else
  (`ReadmeTest`).
- **`CONTRIBUTING.rst`**: the opening's sentence on browser-viewer changes
  goes ("browser-viewer changes belong to the separate ... repository");
  "Development environment" says Node.js 22 or newer and npm build and test
  the browser viewer's widget, installed by `npm ci` at the root, and that
  the viewer's browser tests need Chromium (`playwright install chromium`);
  the pip block gains `-e packages/machinome-viewer \` before the
  mechanics line; "Running tests" gains, after the mechanics sentence, "The
  browser viewer keeps its tests in its own directory: run ``python -m
  pytest`` from ``packages/machinome-viewer``, and its widget's with ``npm
  test --workspaces`` from the root."; the note "The browser viewer's own
  tests live in the ``machinome-viewer`` repository. ..." becomes
  "``tools/generate_parity_fixture.py`` produces, from this framework's
  render results, the parity fixture the viewer's widget commits beside its
  expression evaluator."
- **`context7.json`**: `excludeFolders` gains
  `packages/machinome-viewer/openspec`, `packages/machinome-viewer/tests`
  and `packages/machinome-viewer/workflow`; the rule "The optional
  machinome-viewer package owns browser rendering. ..." becomes "The
  browser viewer is machinome.viewer.web, the repository's distribution
  machinome-viewer, installed by pip install \"machinome[viewer]\" and
  numbered with the framework; it is not published on npm. machinome develop
  requires it; --no-web builds and watches without it. Check machinome viewer
  for the installed API and supported documentVersions. Embed an exported
  page in an iframe, or load machinome-viewer.js and call
  MachinomeViewer.mount(target, documentUrl, options); mountInspector() adds
  a collapsible assembly sidebar. The process interface is machinome-viewer
  describe|serve|capture; the machinome.viewer entry point provides only the
  bundle lookup." (the viewer's own rules folded; the API 28 and 29 rule of
  the viewer's index stays in the "matching viewer" rule, which names the
  version through `viewer_version` and its test).
- **`AI-USE.md`**: machinome-viewer leaves the list of sibling repositories,
  its sentence "machinome-viewer's history before the line is this
  repository's, from which it was split" moves to the paragraph on what is
  agent-written: "... and the browser viewer under `packages/machinome-viewer/`,
  split from this repository on 5 September 2026 and joined back with its
  history, ...".
- **ADR-188** (recommended, Open Questions 2),
  `docs/adrs/BUILD/ADR-188-the-browser-viewer-is-a-product-of-the-repository-numbered-with-the-set.md`,
  Status Proposed, Change `join-viewer`. Supersedes ADR-068 in the viewer's
  repository and licence (its lookup, its process boundary and the
  framework's completeness without it stand). Amends ADR-182 (the root holds
  the npm workspace, `package.json` and its lock, beside the uv workspace),
  ADR-183 (a product numbered with the set: its manifest, pin, `__init__.py`
  and `package.json` in `.bumpversion.cfg`, `~=` both ways) and ADR-187 (a
  second product keeping its record in its directory, this one numbered with
  the set). Related to ADR-103 (the browser is the only interactive viewer)
  and ADR-179 (the provisional renderer column, which the `viewer-seam`
  cycle removes). Context: the pilot's decisions of 12 October 2026, the
  address `machinome.viewer.web` among them; probes 4 to 8, 13 and 18 to 21.
  Options: (1) a product of the repository at `machinome.viewer.web`, the
  address the `viewer-seam` outline gives the web provider, numbered with
  the set, its process seam kept (chosen by the pilot); (1') the same at
  `machinome.viewer` (refused by the pilot: the seam's own address, which
  that cycle would take back with a second rename); (1'') the same with
  `machinome_viewer` kept (declined by the pilot: outside the set's dotted
  names); (2) the viewer as an extension package whose record folds into
  the framework's (refused by the plan); (3) the seam of viewers in this
  cycle, the viewer a provider (refused by the pilot: the seam is unchanged
  and `viewer-seam` a later cycle); (4) the widget's own lockfile kept
  beside the workspace's (refused by probe 5: npm ignores it inside the
  workspace). The decision outcome states Decisions 3 to 9 and the vet's
  denial of Decision 7. Consequences: good, one licence, one version, one
  manual, one CI; the viewer sits where the seam of viewers will find its
  web provider, so that cycle renames nothing of it; Node enters the test
  and dist jobs; bad, the 79 pre-split commits read twice in a global log;
  the core suite and the viewer's tests need a built bundle and Chromium;
  every viewer process imports the core's `__init__` (probe 10); until the
  seam, `machinome.viewer` is a namespace level with no module of its own,
  beside the core's `machinome.viewers`, and the seam's
  `machinome/viewer/__init__.py` must extend its path with portions or hide
  the viewer in every editable workspace (probe 20); neutral, the framework
  reaches the viewer as before. Index line under BUILD after
  ADR-187. ADR-068's status and index line note "repository and licence
  superseded by 188"; ADR-182's, ADR-183's and ADR-187's gain the dated
  consequence "Neutral (2026-10-12, `join-viewer`): the browser viewer joined
  as a product numbered with the set; the root holds an npm workspace
  (ADR-188)" and "amended by 188". The framework index's VIEWER-WEB and
  EXPORT entries marked *Relocated* to solid-node-viewer (ADR-068) read
  "*Kept* in the viewer's log, `packages/machinome-viewer/workflow/adrs/`
  (ADR-068, ADR-188)".
- **The viewer's decision log**, `packages/machinome-viewer/workflow/adrs/README.md`:
  a dated note under "Provenance", "(12 October 2026, change `join-viewer`)
  The viewer joined the machinome repository at `packages/machinome-viewer/`;
  this log stays its own, beside the framework's
  `packages/machinome/docs/adrs/`. A number cited in the viewer's code,
  specs and records names this log's ADR; the framework's are cited as
  'framework ADR-nnn'." The records are untouched.
- **The plan's progress** (`workflow/ongoing/joins-0.9.md`): the cycle's
  entry at its close.

### 13. The product's record, brought current in place

The applier edits, in place and with no change of behaviour:

- `openspec/config.yaml`: its context says the viewer is the repository's
  package `machinome.viewer.web` at
  `packages/machinome-viewer/`, its widget a member of the root npm
  workspace, reached by the framework through the entry point and the
  console script as a separate process, under the repository's licence; the
  sentence on the licensing boundary goes.
- `openspec/specs/viewer-distribution/spec.md`: its `Code:` line and the
  requirements naming `machinome_viewer`, the licence and the repository
  (the licence the distribution and the banner state, the `Source:`
  line, "This package SHALL NOT import `machinome`" restated as "SHALL NOT
  import the framework's modules"), with their scenarios' words; titles kept.
- `openspec/specs/user-documentation/spec.md`: "Makers have a viewer
  manual", "The manual is reproducible and reviewable" and "The manual
  states the 0.8.0 release" say the manual is the browser viewer's pages of
  the Machinome manual, built with it, and that every reader-facing licence
  sentence states the set's licence; titles kept.
- `openspec/specs/development-server/spec.md`, `snapshot-capture/spec.md`,
  `viewer-assembly-navigation/spec.md`, `viewer-package/spec.md`: the `Code:`
  lines and import spellings (`machinome.viewer.web`).
- `workflow/README.md` and `workflow/documentation.md`: the maintainer notes
  in force; `documentation.md` says the pages are in the framework's manual
  (the how-tos and `reference/viewer/`), built with it, and checked in the
  browser by `scripts/check-docs-browser.py`; the Read the Docs section goes.
  The other notes are records of their day and stay as written.

`env -C packages/machinome-viewer openspec validate --specs --strict` passes
afterwards. The three active changes and every archived record stay as
written.

### 14. The spec deltas

- `framework-identity`: MODIFIED "Extras select independent Machinome
  products" (the viewer extras pin `~=` the set's viewer, a distribution of
  the repository; scenario titles kept) and "The framework is the package
  directory `packages/machinome` of a monorepo" (the viewer among the
  products, numbered with the set; the root npm workspace; `check-dist`
  smokes it from its wheel; three new scenarios).
- `viewer-distribution`: MODIFIED "The framework resolves the Machinome
  viewer" (the package `machinome.viewer.web`, run as `python -m
  machinome.viewer.web`; one new scenario).
- `user-documentation`: MODIFIED "Viewer and embedding claims are accurate",
  "The documentation build produces nothing", "The viewer's provenance and
  installation are stated", "The 0.8.0 release is recorded", "The README
  describes the package", "The 0.8.1 release is recorded"; RENAMED "Viewer
  users can reach the independent viewer manual" to "The browser viewer is
  documented in the manual", MODIFIED under the new title.
- `framework-contributor-guidance`: MODIFIED "The contributor guide states
  the monorepo's development setup" (Node, the root `npm ci`, the viewer's
  and the widget's tests, the pip command; two new scenarios).
- `kinematics`: MODIFIED "The parity fixture is regenerated from any checkout
  of the framework" (the repository's own viewer package; titles kept).
- `vet`: MODIFIED "A framework internal is a finding" (`machinome.viewer.web`
  among the denied modules; the former name outside the universe; one new
  scenario, "The browser viewer is an internal").

Each MODIFIED requirement is copied whole from its baseline and edited;
every existing scenario keeps its title. Archived in a scratch copy of the
bench's `openspec/` with a one-line tasks file (`<revise>/os-probe`,
`<revise>/os-archive.txt`, after the revision), the deltas apply "~ 13
modified, → 1 renamed" and `openspec validate --specs --strict` passes 46 of
46; every scenario of the six specs survives, three added to
`framework-identity` (29 to 32), one to `viewer-distribution` (13 to 14),
three to `user-documentation` (86 to 89), two to
`framework-contributor-guidance` (9 to 11) and one to `vet` (66 to 67),
`kinematics` keeping its 98. (The first draft's five deltas, in
`<scratch>/os-probe`: "~ 12 modified, → 1 renamed", 46 of 46.)

### 15. Workspace and project follow-ups, outside this repository

Listed for the orchestrator; none is done by this cycle:

- the operating contract's viewer paragraphs (`AGENTS.md`: an independent
  repository, published 0.7.0 to 0.8.0, 0.8.1 tagged locally) and its layout
  block; `docs/collaborator-setup.md`; `scripts/setup`, which clones the
  viewer's repository and builds `machinome_viewer/widget` and
  `machinome_viewer/app`; `scripts/dev-env`, whose bench then needs `npm ci`
  at its root (never a symbolic `node_modules`) before the widget builds; at
  the campaign's close, as the plan says;
- the studio's `shop-skills/machinome-api/SKILL.md` and the workspace's
  `skills/write-the-manual/SKILL.md`, which describe the viewer's separate
  manual and its tests;
- the projects that spell `machinome_viewer` (probe "Consumers"): the eleven
  Curta tools and the lock's `tools/export-demo.py` run `python -m
  machinome_viewer describe`; they move to `machinome viewer`, the
  framework's report, or to `python -m machinome.viewer.web`, in their own
  repositories; science-jubilee's tool and Voron-2's evidence stay
  as recorded;
- the site's intake reads the banner line this design keeps;
- for the `viewer-seam` cycle, recorded in the framework's
  `workflow/ongoing/` note when the orchestrator closes this one: the seam's
  `machinome/viewer/__init__.py` must extend its `__path__` with
  `_namespace_portions`, or the viewer's package stops resolving in every
  editable workspace (probe 20).

### 16. Validation and the originating check

The suite from `packages/machinome` (expected: the base's 4838 passed and the
tests this change adds, the base's 24 skips but the sixteen viewer ones, the
end-to-end capture still skipped without its opt-in); the viewer's tests
from its directory with Chromium for the locked Playwright (expected: every
test passes or skips naming what is absent, the Curta's two with
`MACHINOME_CURTA_BUILDS` set to the project's `_build`); the widget's
typecheck, tests (1715 or more) and build from the root; the manual with
warnings as errors from `docs/requirements.txt` alone, the embedding page
loaded in Chromium and looked at, and `scripts/check-docs-browser.py` on it;
`scripts/check-dist` on the tree and on a clean copy (fourteen members, 28
archives); the universe sweep, identical to its base row for row; and the
originating check on the bench: `machinome develop` on a project of the
catalogue with the bench's viewer, its page opened and photographed, and
`machinome snapshot --renderer web` of one model, looked at.

## Risks / Trade-offs

- [The lock's Playwright needs a Chromium this machine lacks] → CI installs
  it in the test job; locally the orchestrator runs `playwright install
  chromium` with the bench venv's Playwright once (Open Questions 6).
- [The core suite runs its viewer tests from this change on] → They need the built bundle; a
  bench builds it by `npm ci` and `npm run build` at its root before the
  suite, and a stale bundle is rebuilt by the currency check once its
  dependencies are installed (Decision 4).
- [The index may serve a former-import `machinome-viewer` 0.8.1] → The
  smoke installs the built wheel by path; the core's `~=0.8.1` extras admit
  0.8.x until the 0.9 release renumbers the set (Decision 9).
- [The manual completes its exports with the published viewer] → As at the base:
  the docs build installs `docs/requirements.txt`; the embedding example
  shows the published bundle, which a release moves with the set.
- [npm writes the root's `node_modules` from the widget's directory] → The
  guard reads every ancestor (Decision 4); the workspace's bench recipe runs
  `npm ci` per bench.
- [A global log shows 77 pre-split subjects twice] → Accepted by the pilot;
  the paths tell them apart.
- [The joined archives, notes and two viewer ADRs keep the licence the
  product carried] → Historical records, as in the earlier joins; every
  current file and every record this change writes states the set's.
- [The viewer's lint adds 184 flake8 lines (3 in its modules)] → CI's lint
  is `continue-on-error`; reformatting would put an edit between the join
  and `git blame`. Not done.
- [The sdist grows to 1089 entries with the specs and archives] → The
  product's record travels with its source, as the framework's and the
  mechanics package's do.
- [The seam's future `machinome/viewer/__init__.py`, written empty, hides
  `machinome.viewer.web` in an editable workspace while every wheel
  installation still works] → Probe 20; the outline already says the seam
  extends its path as `machinome/node/` does, the layout gate's
  `test_each_product_resolves_from_its_directory` fails on the workspace if
  it does not, and Decision 15 lists the condition for that cycle.
- [`machinome.viewers` and `machinome.viewer` side by side] → Two names one
  letter apart until the `viewer-seam` cycle moves `viewers/` under the
  seam; nothing resolves one for the other (probe 19).
- [The excluded package data keyed by a name other than the package] → The
  wheel then ships the widget's sources (probe 11); the smoke of Decision 9
  refuses it.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and
the reds it causes; the red gates; the package and its source; the npm
workspace; the core, the uv workspace and the sync; the tests at their new
place; the manual; `check-dist` and CI; the records; validation and the
originating check; the archive. Rollback is a revert of the implementation
commit and of the merge commit, `uv lock`, `uv sync`, and the root's
`node_modules` removed.

## Open Questions

The pilot settled Open Questions 1 on 12 October 2026, and the orchestrator
accepted on the same day the recommendations of Open Questions 2 to 9 as
they stand below; each keeps its reasoning for the record. Open Questions 10
is the revision's.

1. **The import name: settled, `machinome.viewer.web`.** The pilot's
   decision of 12 October 2026, over the first draft's two candidates,
   `machinome.viewer` (the seam's own address, which the `viewer-seam` cycle
   would take back with a second rename) and `machinome_viewer` kept (the
   first draft's recommendation, declined). The seam is unchanged at this
   address: the framework loads only the entry point and runs a process
   (probes 9, 12, 16 and 19), and the package runs without the core (probe
   10). What it costs, measured at the address:
   - the 86 lines of 32 files of the package, its manifest and its tests
     (Decisions 3, 4 and 11), the 26 fixture paths of 14 widget tests moved
     by two levels and `documentation.test.ts` by four, the core's command
     and four tests (Decision 7);
   - every viewer process imports the core's `__init__`: 170 modules against
     the original's 167, the core's `machinome` 9 to 10 ms of import, the
     extra namespace level 0.5 ms, wall-clock medians within run-to-run
     spread (77.5 ms, against 78.3 ms at `machinome.viewer` and 75.9 ms for
     the original, probe 10);
   - twelve project tools that run `python -m machinome_viewer` break until
     moved (Decision 15);
   - `machinome vet` admits the address unless denied, so the contract's
     denylist gains it (probe 21, Decision 7, Open Questions 10);
   - `machinome.viewer` is a namespace level with no module of its own,
     beside the core's `machinome.viewers`, until the `viewer-seam` cycle;
     that cycle's `machinome/viewer/__init__.py` must extend its path with
     portions (probe 20).
   What it buys: the viewer sits where the seam of viewers will look for its
   web provider, so the `viewer-seam` cycle moves nothing of the viewer's
   package.
2. **The ADR.** ADR-188, or amendments only (ADR-068 superseded in part,
   ADR-182, ADR-183 and ADR-187 a dated consequence each). Recommendation:
   ADR-188; the join makes choices no record holds: the first product
   numbered with the set, the npm workspace at the root, and the process
   boundary kept with its licence reason gone. If declined, the HISTORY
   bullet's "(ADR-188)" becomes "(ADR-068 superseded in part, ADR-182,
   ADR-183 and ADR-187 amended)".
3. **The lockfile's place.** One lock at the root, seeded from the widget's
   (Decision 5), or the widget's kept and the root's beside it.
   Recommendation: the root's alone; npm reads only the root's inside a
   workspace (probe 5), so a second lock would be stale by construction, and
   seeding keeps every resolution.
4. **`viewer_version` and the viewer facts in the release block.**
   `viewer_version` kept (a literal in `docs/conf.py`, from this change in
   `.bumpversion.cfg`), or dropped for `|release|` on every page.
   Recommendation: kept; pages read "this manual matches viewer
   |viewer_version|" correctly either way, the test that holds it to the
   release stands, and dropping it edits eight pages for no reader. The same
   reasoning keeps `viewer_api` and `document_versions` literals, held to the
   widget's `package.json` by the viewer's documentation test rather than
   read by `conf.py`, which would make the manual's build read a file of
   another package.
5. **The pages' placement.** Three how-tos and one reference section
   (Decision 10), or one section "Browser viewer" holding all eleven pages.
   Recommendation: the split; the manual's sections are by reader intent and
   a maker's job and a host's lookup are different intents, as the mechanics
   section and how-to are.
6. **Chromium for the locked Playwright, in CI and here.** CI runs
   `playwright install --with-deps chromium` in the test job before the
   viewer's tests; locally the orchestrator runs `playwright install
   chromium` once with the bench venv (outside every repository). The
   alternative, constraining Playwright in the lock to the version whose
   Chromium a machine has cached, would tie the lock to one machine.
   Recommendation: the command, the orchestrator's, before task 6.2.
   Accepted: the lock keeps Playwright 1.63.0, and the orchestrator runs
   `playwright install chromium` with the bench venv at the implementation
   step (task 6.2).
7. **The released changelog sections that name the viewer's licence**: the
   viewer's 0.7.0 identity bullet and the framework changelog's 0.8.0 and 0.7
   lines. Keep them as written, as records of their releases (the docs test
   then admits `project/changelog.rst` as a record), or drop the identifier
   in place. Recommendation: drop it in place, as the orchestrator accepted
   for the mechanics changelog's 0.1.0 bullet; `HISTORY.rst`'s released
   entries, the release notes under `docs/releases/` and the archived records
   stay as written.
8. **The demo and its stylesheet.** Kept, renamed `viewer-demo.js` and
   `viewer-demo.css`, the stylesheet's rule for every table cell dropped and
   its rules for the demo and the JavaScript domain's entries kept; or the
   click-to-load demo replaced by the `.. machinome::` directive on the
   committed spinner. Recommendation: kept as described; the directive shows
   an export page, while the guide's point is a host page using the public
   mount, and the remaining rules style only the demo and the viewer's own
   reference entries.
9. **The parity fixture's default.** The generator writes the repository's
   own viewer package by default (Decision 7), or keeps writing a sibling
   checkout. Recommendation: the repository's; after the join the sibling is
   the original repository, which no one develops in.
10. **The vet's denial of the viewer.** `machinome.viewer.web` denied by the
    contract's denylist, a vetted file that reaches it `framework-internal`
    (Decision 7), or left in the contract as a module beneath `machinome`.
    Recommendation: denied. Before the join a model that imported the viewer
    was refused as `outside-universe` (probe 21); at the address it would
    pass, and the viewer serves, drives Chromium and runs npm, which is what
    the denylist is for. Only `machinome.viewer.web` is denied, not
    `machinome.viewer`, whose seam the `viewer-seam` cycle writes and judges.
    If declined, the `vet` delta, the `universe.toml` line and the vet test
    of tasks 3.7 and 6.1 are dropped, and the HISTORY bullet loses its vet
    clause.
