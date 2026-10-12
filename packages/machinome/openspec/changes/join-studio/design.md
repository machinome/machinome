## Context

The fourth cycle of the road to Machinome 0.9.0
(`workflow/ongoing/release-0.9.md` at the repository root, "The cycles, in
order", 4), cut from the line `v0.9-joins` at 675edac4, whose head holds the
viewer's join (the root npm workspace, ADR-188), the skills' join (`machinome
skills`, ADR-190) and the command seam (ADR-189), on the bench
`machinome/WTs/v0.9-joins-join-studio`. Two cycles land on the line before
this change's planning commit, which the orchestrator makes after
fast-forwarding the bench: `join-movie` (its ratified design's Decisions 5, 6,
9, 11 and 13: the command class `machinome movie`, the second npm member with
the root `.npmrc` `install-strategy=shallow`, the member's own tracked lock,
the seam's fakes renamed `fake-film`, the `check-dist` row, the Node suite;
ADR-191) and `release-tooling` (its ratified design's Decision 1, the root
`Makefile` with `PACKAGES`, `TESTED`, the npm members and `MEMBER_LOCKS`, and
Decision 11, CI on the targets; ADR-192). This design is written against both
as landed; each place that assumes them says so with "(as `join-movie`
lands it)" or "(as `release-tooling` lands it)".

The pilot's decisions of 12 October 2026 (`release-0.9.md`, decisions 1, 2,
3, 4, 6, 7 and 9), settled and not reopened here:

- **The studio joins whole** with its record in its directory, as the
  distribution `machinome-studio` at `packages/machinome-studio/`.
- **Its address is `machinome.studio`**: the package `floor` becomes the
  portion `machinome/studio/`; no module of the former name is provided and
  no alias; whoever imports `floor` moves.
- **One version**: the set's, 0.8.1 on this line, pinned `~=` both ways; the
  bump to 0.9.0 is the road's last step.
- **One licence**: its `LICENSE` and `NOTICE` go, its manifest states the
  set's expression, no record this change writes names the licence it
  carried, and the provenance its `NOTICE` records goes to `CREDITS.md`.
- **Its command is `machinome studio`**, the third contributor of the group
  `machinome.commands` (ADR-189), installed by the core's extra
  `machinome[studio]`.
- **Pip only**: its built browser surface is carried by its wheel; nothing is
  published on npm; its frontend is the third member of the root's npm
  workspace.
- **Its manual folds into the framework's**, inside
  `packages/machinome/docs/`.
- **The studio keeps its own skills** (`shop-skills/machinome`,
  `shop-skills/machinome-api`) and links `machinome-simulate` from the skills
  package (`packages/machinome-skills/machinome/skills/agent-skills/machinome-simulate`);
  unifying them further is deferred.
- **Its branches other than `main` are not joined**: they are listed here
  with their deltas against `main` and held for the pilot.

Machinome Studio is the project hub and workspace in which a team of agents
builds a machinome project with its maker: a FastAPI service with a React
browser surface, the runtime profiles and their prompts, the agent backends
(Claude Code, OpenCode, qualified Codex) and an MCP server through which the
agents reach the project. It has been an independent repository since
26 September 2026, experimental, at 0.1.0, never published; the workspace
installs it editable and opens the floor with its console script
`machinome-studio`. It imports none of the framework's modules and runs the
`machinome` command beside its interpreter as a subprocess; it finds the
viewer's bundle through the framework's `machinome viewer` report
(`preparation.py`).

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. `P` is the package directory
`packages/machinome-studio/machinome/studio`. Probes ran in the scratch
directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C8-propose/`
(named `<scratch>` below), never in the bench, the product, the workspace or a
project, with uv 0.11.8, git-filter-repo `ed61b4050b71`, Node 24.11.1, npm
11.6.2, Sphinx 9.1.0, CPython 3.12.3 and the OpenSpec CLI 1.6.0.
`<scratch>/studio-rw` is the rewritten clone; `<scratch>/merge` a clone of the
bench's branch at 675edac4 with the rewritten `main` merged and the prototype
of this design applied in its working tree (uncommitted), with its own venv
`<scratch>/merge/.venv` synced from its edited lock; `<scratch>/merged-only` a
worktree of the bare merge commit; `<scratch>/npm-ws` a copy of the npm
workspace with the three members, its root files taken from the movie's bench
on 12 October 2026 (the movie's implementation in progress there).

### What the join touches

- **The product's 751 tracked files** at 0a09e05 (7 October 2026, `main`):
  `README.md`, `CHANGELOG.md`, `pyproject.toml` (0.1.0, fastapi, tomlkit,
  uvicorn, watchdog; the console script `machinome-studio =
  floor.orchestrator:main`; package data `floor = ["static/**"]`; extras `e2e`
  with Playwright 1.61.0 and `docs`), `NOTICE`, `LICENSE`, `.gitignore`,
  `.readthedocs.yaml`, `AGENTS.md` and the link `CLAUDE.md`, `.codex/config.toml`
  (the repository's Codex development defaults), `.claude-plugin/`
  (`plugin.json` and `marketplace.json`, the studio described as a Claude Code
  plugin of 26 September 2026); `floor/` (83: 17 modules, `backends/` with 11,
  `frontend/` with its `package.json` (`shop-floor-frontend`, private, version
  0.0.0), `package-lock.json`, seven sources, `public/assets/` (the identity's
  `brand/v1/`, the favicon pack, the two interface fonts with their notices),
  the configurations); `profiles/` (11: `openspec-builder` and `fordesmac`,
  their prompts, `profile.toml` and per-profile skill links); `shop-skills/`
  (3: `machinome/SKILL.md`, `machinome-api/SKILL.md` and its
  `agents/openai.yaml`); `tests/` (49: 42 modules, `__init__.py`, six
  fixtures); `docs/` (85: ten manual pages, `conf.py`, `requirements.txt`, the
  architecture overview, 35 ADR files, `design/`, `product/`, `spikes/`);
  `openspec/` (498: 26 specs, 60 archived changes, two active ones,
  `add-project-model-screenshots` and `make-shop-floor-event-driven`);
  `workflow/` (7); `scripts/` (`setup`, `test-e2e`, `build-favicon`). No tags.
- **History.** 349 commits over every ref, 347 on `main`, 1349 paths. Earlier
  layouts: a Go broker (`cmd/`, `internal/`, `go.mod`), a first Python service
  `src/shop_floor/`, a root `frontend/` (moved to `floor/frontend/` on
  20 July 2026) and a root `package.json` with `playwright.config.mjs`, role
  cards under `agents/` (moved into `profiles/fordesmac/`), skills under
  `skills/` (moved to `shop-skills/`), Codex role adapters under
  `.codex/agents/`, a gitlink `solid-node` with its `.gitmodules`, and the
  design reference under `docs/design_handoff_shop_desktop/` (moved to
  `docs/design/`).
- **The licence the product carried** is stated in `LICENSE`, `NOTICE`, both
  manifests and the frontend's lock, `README.md`, 89 SPDX lines in 88 current
  files (`floor/`: 28 Python modules, five TypeScript and two TSX sources, one
  stylesheet, `index.html`; `scripts/`: two; `tests/`: 49 files, 50 lines,
  `test_license_headers.py` holding the pattern twice), and 16 records (three
  spike files of archived changes, ten files of `docs/design/`, three of
  `docs/spikes/`). `docs/architecture-overview.md` names the viewer's former
  licence once, as a record. No manual page names it.
- **What the product carries of others'**: the identity's artwork under
  `public/assets/brand/v1/` and the studio's favicon pack built from it, which
  its `brand/README.md` says "carries no public licence" and are trademarks of
  Poiesis Tecnologia da Informação LTDA (`NOTICE`); the derived logo font
  Machinome Logo Regular (from Anta, SIL OFL 1.1, Copyright 2019 The Anta
  Project Authors, 2026 The Machinome Project Authors) and the interface fonts
  Space Grotesk (SIL OFL 1.1, Copyright 2020 The Space Grotesk Project
  Authors) and IBM Plex Mono (SIL OFL 1.1, Copyright 2017 IBM Corp., Reserved
  Font Name "Plex"), each with its notice beside it; and, minified into the
  built `static/assets/*.js`, the frontend's runtime packages
  (`<scratch>/frontend-own-lock.json`, non-development entries): react and
  react-dom 19.2.7, scheduler 0.27.0, three 0.185.1, monaco-editor 0.56.0,
  @monaco-editor/react 4.7.0, @monaco-editor/loader 1.7.0, state-local 1.0.7,
  marked 14.0.0 (MIT each) and dompurify 3.4.8 (its own expression, MPL-2.0 or
  the other licence its `package.json` names). The built assets carry no
  licence notice of these packages (probe 17).
- **The core.** The extra `studio = ["machinome-studio"]`, unpinned, with the
  comment "still experimental and unpublished"; the root's `exclude-dependencies
  = ["machinome-studio"]`; `tests/test_machinome_identity.py` already expects
  the extra to name `machinome-studio`; `framework-identity`'s requirement
  "Extras select independent Machinome products" and its scenario "A reader
  asks for the studio extra before publication"; `docs/project/status.rst`
  and `docs/project/upgrading.rst` ("experimental and unpublished");
  `docs/reference/cli.rst` and `docs/architecture.md` ("the studio is to add
  its own"); `AI-USE.md`'s sibling repositories; `CREDITS.md`'s section
  "Adapted from Machinome Studio, in the skills package".
- **Consumers.** The workspace runs the console script `machinome-studio`
  (its `AGENTS.md`, `README.md`, `docs/collaborator-setup.md`, `scripts/setup`,
  the skills `debug-workflow`, `sprint`, `simulate-project`,
  `write-the-manual`) and reads `~/.config/machinome-studio/config.toml`. No
  project repository imports `floor` or names the launcher (`grep -rIl` over
  `projects/`, `*.py` for `^(from|import) floor`, `*.md|*.sh|*.toml` for
  `machinome-studio --projects-dir|python -m floor`: 0 files); projects carry
  `[tool.machinome-studio]` tables, which the studio keeps reading.
- **What the studio carries from before 0.8.** `P/mcp_server.py`'s
  `machinome_test` tool takes `kernel` in `("exact", "faceted")` and passes
  `--exact`/`--faceted`; `machinome test` on this line accepts `[--brep |
  --mesh]` and reads `SOLID_TEST_ENGINE`. `shop-skills/machinome/SKILL.md`
  and `shop-skills/machinome-api/SKILL.md` teach `machinome test
  --faceted|--exact`, `kernel="faceted"`, `SOLID_TEST_KERNEL` and seven
  import statements from `machinome.node`'s root (26 names), which 0.8.0
  refuses (`ImportError: ... the root of machinome.node exports nothing`). The
  framework's `workflow/ongoing/release-0.8.0.md`, section (c), lists both as
  the studio's follow-ups of 0.8.

### Probes

1. **The import, rehearsed** on a fresh clone with every branch made local
   (21) and the command of Decision 2 (`<scratch>/filter-repo-command.sh`,
   `<scratch>/filter-repo.out`): 349 commits parsed, every branch rewritten,
   `main` at fd139a5 with 318 commits; 29 are pruned as empty
   (`<scratch>/pruned-commits.txt`): the commits that touched only dropped
   files (the operating contract, its `CLAUDE.md` link, the setup script) and
   two merges left degenerate. The tree holds 738 files
   (`<scratch>/rehearsal-ls-files.txt`): 730 under
   `packages/machinome-studio/`, 8 under `packages/machinome/docs/`; no commit
   of any branch touches a path outside `packages/`. Without `--follow`,
   `git log` on `P/app.py` lists 30 commits back to a3ca3e5, 20 July 2026,
   "feat: apply and archive FastAPI shop-floor rebuild cycle" (the original's
   `--follow` on `floor/app.py` also lists 30); on
   `P/frontend/src/main.tsx` 55 commits back to 9831f04, 20 July 2026 (the
   original's `--follow`, 52; the root `frontend/` is mapped to its
   successor); on `P/profiles/fordesmac/profile.toml` back to 31 July 2026;
   on `packages/machinome-studio/workflow/design/README.md` 20 back to
   1 August 2026. No commit's tree holds both a predecessor path and its
   successor (`frontend/` and `floor/frontend/`, `skills/` and `shop-skills/`,
   `docs/design_handoff_shop_desktop/` and `docs/design/`: checked on all 349
   commits), so the renames of Decision 2 collide nowhere. The five per-profile
   skill links arrive as links (`120000`), their relative targets still
   resolving.
2. **The merge, rehearsed** in `<scratch>/merge`: `git fetch <rewrite> main`,
   `git merge --allow-unrelated-histories FETCH_HEAD`: no conflict, `git
   status` clean (`<scratch>/merge.out`).
3. **The gates at the join**, eight modules on `<scratch>/merged-only` with
   the bench venv (`<scratch>/gates-at-join.txt`): 24 failed, 124 passed. Red
   for the join: `test_every_member_is_a_workspace_source`,
   `test_the_readme_links_every_package_and_states_the_licence`,
   `test_every_sibling_is_in_the_table` ("packages/machinome-studio is in
   neither EXTENSIONS nor PRODUCTS"),
   `test_the_guide_installs_every_member_without_uv`, each naming
   `machinome-studio`; `test_one_lockfile_at_the_root_names_the_widget` (the
   frontend's own `package-lock.json`); the release records'
   `test_every_member_is_numbered_with_the_core` ('0.1.0' != '0.8.1'),
   `test_every_pin_between_members_is_compatible` (the core's unpinned extra)
   and `test_the_version_is_bumped_from_the_root`; the split-word gate (13
   occurrences: `mcp_server.py` 9, `preparation.py` 4); the node-root gate (26
   offences in the two skills). The other reds are the rehearsal's own (the
   bench venv's editable lines name the bench's directories). The
   no-scad and kernel-free gates are green.
4. **The npm workspace with three members** (`<scratch>/npm-ws`): the root
   `package.json` naming the widget, the movie's `js` and `P/frontend`, the
   root `.npmrc` `install-strategy=shallow`, the frontend renamed
   `@machinome/studio`, version 0.8.1, the set's licence, its own lock moved
   out. A plain `npm install` resolves the frontend afresh: 73 of its 133
   resolutions move (react and react-dom 19.2.7 to 19.3.0, rollup 4.62.2 to
   4.63.1, the Babel and esbuild families). Seeded instead
   (`<scratch>/root-lock-seeded.json`: the member's entry, its workspace link,
   and each `node_modules/<name>` of its own lock inserted as
   `<member>/node_modules/<name>`), `npm install` keeps all 133 (0 moved),
   changes none of the root lock's 264 entries and adds the member's (399
   entries); `npm install --package-lock-only` then says "up to date" and
   leaves the lock byte for byte; `npm ci` installs 229 packages, the member's
   own 50 directories in `P/frontend/node_modules/` (its TypeScript 5.9.3, vite
   7.3.6, react 19.2.7, three 0.185.1; the movie's TypeScript 7.0.2 and react
   19.3.0 stay in its own `node_modules`). From the root: `npm test
   --workspace P/frontend` (`tsc -b`) exits 0 in 2.6 s; `npm run build
   --workspace P/frontend` writes `P/static/` in 12.0 s, with the chunk-size
   warning the original build gives; `npm run build --workspaces
   --if-present` builds the widget and the studio's frontend; the widget's
   typecheck and build still pass beside it. The frontend needs no lock of its
   own: nothing installs it outside the workspace, its wheel carrying the
   built surface.
5. **The lock** (`<scratch>/merge`, the member a workspace source and out of
   `exclude-dependencies`, the core's extra `machinome-studio~=0.8.1`, the
   default group gaining `machinome[studio]`): `uv lock` fails, "Because
   machinome depends on fastapi==0.111.* and machinome-studio depends on
   fastapi>=0.115,<1 ... your workspace's requirements are unsatisfiable".
   The workspace venv has run the studio on fastapi 0.111.1 and starlette
   0.37.2 since its install (`/home/asa/devel/machinome/.venv`), and the
   studio's tests pass there (probe 10). With the floor `fastapi>=0.111,<1`,
   the viewer's: "Resolved 195 packages", two more than the base's 193 (the
   member and tomlkit 0.15.1), the lock's diff 48 lines
   (`<scratch>/uv-lock.diff`); `uv sync --python 3.12`: sixteen
   `__editable__` `.pth` files, the studio's among them. On the movie's line
   the count is the movie's plus two (*inferred*: the movie adds no package
   the studio needs).
6. **The resources at the address.** `preparation.shop_resource_root()` is
   `Path(__file__).resolve().parents[1]`, the directory above `floor/`, where
   the checkout held `profiles/` and `shop-skills/`; at `P/` it names
   `packages/machinome-studio/machinome/`, and in an installed wheel
   `site-packages/machinome/`, where neither exists; the 0.1.0 wheel shipped
   only `floor/static/`. With the profiles and skills inside the portion and
   the root its own directory (`Path(__file__).resolve().parent`), both
   profiles load from the checkout and from the wheel (probes 7, 8). The MCP
   server is started as `python -m floor.mcp_server` with the resource root on
   `PYTHONPATH` (`backends/claude.py`, `backends/opencode.py`); at the
   address the module is `machinome.studio.mcp_server` and the path entry the
   directory that holds the portion's `machinome/`. `find_spec('floor')` is
   `None` in the rehearsal's venv.
7. **The archives** (`<scratch>/build-studio.out`, `<scratch>/dist`): with the
   manifest, `MANIFEST.in` and hook of Decision 3 and `static/` removed first,
   `python -m build` writes both archives in 22.8 s, the sdist hook building
   the frontend through the workspace; the sdist holds 1172 entries (60 under
   `static/`, the frontend's sources, the profiles and skills with every link
   a regular file), the wheel 113: the 19 modules (the 17 of `floor/`,
   `cli.py` and `packaging.py`), `backends/` (11),
   `static/` (53), the profiles (17, each profile carrying its skills as
   files) and `shop-skills/` (5, `machinome-simulate/SKILL.md` and its
   reference among them, regular files with the skills package's bytes), the
   licence files, no frontend source, no `node_modules`, no
   `machinome/__init__.py`; `entry_points.txt` holds `[machinome.commands]
   studio = machinome.studio.cli:Studio`. The wheel built from the sdist ran
   no npm: the unpacked `static/` is newer than every source.
8. **Installed beside the core, the viewer and the skills** from the four
   built wheels in a throwaway venv (`<scratch>/wheel-venv`): the group
   `machinome.commands` lists `skills` and `studio`; the requirements read
   `machinome~=0.8.1`, `machinome-viewer[snapshot]~=0.8.1`, `fastapi<1,>=0.111`,
   `tomlkit`, `uvicorn`, `watchdog`; the core's metadata `machinome-studio~=0.8.1;
   extra == "studio"`; `shop_resource_root()` names the installed package
   directory, `static/index.html` a file; both profiles load, the builder
   with `machinome-api`, `machinome` and `machinome-simulate`; no
   `machinome-studio` script. `machinome studio --projects-dir
   <scratch>/catalogue --port 9188` printed "shop-floor open at
   http://127.0.0.1:9188", answered `/` with 200 (764 bytes, "Machinome
   Studio") and `/api/entries` with the catalogue's project, and was stopped
   (`<scratch>/hub-wheel.out`).
9. **The command's cost** (`<scratch>/timing-*.txt`, medians of nine runs on
   the rehearsal's venv, the same minute): with the package root as it is,
   which imports the application, `machinome -h` 841 ms and `machinome studio
   -h` 351 ms, `import machinome.studio.cli` 296 ms and 427 modules
   (fastapi, starlette, uvicorn, watchdog and tomlkit among them); with a lazy
   root, 619 ms, 76 ms, 17 ms and 79 modules (`machinome`,
   `machinome.studio`, `machinome.studio.cli`, the standard library). From the
   wheels, `machinome -h` with and without the studio installed: 533 and 513
   ms, then 505 and 514 ms, within the run-to-run spread.
10. **The studio's tests.** At the original layout (`<scratch>/studio-orig`,
    a fresh clone with its frontend built, the workspace venv: fastapi
    0.111.1, Playwright 1.62.0): 499 passed, 1 skipped (the development
    workspace's own installation), 405 subtests (`<scratch>/orig-tests.out`;
    this run overlapped the movie bench's suite, which started meanwhile; its
    result is the product's own count, not a timing). At the new place
    (`<scratch>/merge`, its venv, Playwright 1.63.0, Chromium 1243), after a
    mechanical rewrite of `floor` to `machinome.studio` and of the resource
    paths: 64 failed, 442 passed, 2 skipped, then on a second run 63 failed,
    443 passed, 2 skipped (`<scratch>/new-place-tests-2.out`). The failures
    are the pins Decision 14 rewrites: the documentation tests (25: the pages
    moved, `conf.py`, `.readthedocs.yaml`, `requirements.txt` gone), the Codex
    fixtures' resource root (19: a role context built from the former root),
    the profile tests that copy the profiles into a temporary directory (9:
    the copied `machinome-simulate` link dangles there), the console script,
    licence headers, identity and plugin pins (6), and four path or
    `PYTHONPATH` expectations. Every behaviour test of the hub, the floor, the
    broker, the backends, the MCP tools, the watcher and the build passes at
    the address. The first run's one browser failure
    (`test_shop_lifecycle_e2e.py:670`, the Apply button still disabled after
    30 s) did not recur alone (22 passed, 1 skipped) nor in the second full
    run. The two skips: the development workspace's installation, and the
    browser test of the real viewer bundle, which no bundle was built for in
    the rehearsal. With a `PATH` of the venv, `/usr/bin` and `/bin` only (no
    OpenSpec CLI, no backend, no Node): 121 failed, 387 passed, 1 skipped
    (`<scratch>/new-place-bare-path.out`); the 58 more are the hub's API and
    entry point, the OpenSpec tools and prerequisite, the orchestrator's
    shutdown and the browser tests, each refusing to start without
    `openspec`. The studio's suite needs the OpenSpec CLI on the `PATH`; it
    needs no backend (the backends are faked).
11. **The seam's tests with the studio installed** (`<scratch>/seam-tests.out`):
    `test_cli_contributed.py`, `test_cli_lazy_imports.py`,
    `test_kernel_extras.py`, `test_machinome_identity.py`,
    `test_vet_universe.py`: 74 passed, 113 subtests. No fake is named
    `studio`; the choices the help expects are computed from the environment's
    contributors (`join-skills`), and the contract walk reads `studio` of
    `machinome-studio` beside `skills`.
12. **The vet's reading** (`<scratch>/vetproj`): a project made by `machinome
    new probe` whose model imports `from machinome.studio.app import
    create_app` is vetted pure, exit 0: `machinome.studio` lies beneath the
    contract member `machinome` and no denial names it.
13. **The manual folded in**, a docs venv from `docs/requirements.txt` alone
    (Sphinx 9.1.0, the theme, the published machinome-viewer 0.8.0): the bare
    merge builds with exit 1 and 43 warnings (`<scratch>/docs-red.out`): 20
    unknown documents, 8 undefined substitutions (`machinome-version`,
    `required-viewer-api`, `claude-models`, `claude-efforts`, `codex-models`,
    `codex-efforts`, `build-volume`), 7 pages in no toctree, 8 toctree entries
    naming documents of the former layout. With Decision 13's links,
    substitutions and toctrees applied in scratch
    (`<scratch>/fold-docs-probe.py`, on a copy with every package beside it):
    exit 0, no warning (`<scratch>/docs-fold.out`).
14. **The originating check, rehearsed.** `machinome studio --projects-dir
    <scratch>/catalogue --port 9187` from the rehearsal's venv, the catalogue
    a fresh clone of `Vibecoded-demos/gear-shift` (f3c79c2, profile
    `fordesmac`): "shop-floor open at http://127.0.0.1:9187", `/health`
    `{"status":"open"}`, `/api/entries` the project, `/api/backends` Claude,
    OpenCode and Codex found; then `python -m machinome.studio` on the same
    catalogue and port, the project opened by `POST /api/sessions` (state
    `open`, no agent started), photographed in Chromium: the hub
    (`<scratch>/hub.png`: the wordmark, the working folder, three backends,
    the project's card with its preview) and the floor page
    (`<scratch>/floor.png`: the gearbox in the viewer, the assembly navigator
    with `GearboxDemo` and its five children, the Foreman's empty
    conversation), no page error; both stopped, the port free, the copy's
    `git status` clean.
15. **The branches** of the original, against `main`: 21 local branches, two
    with worktrees (`WTs/codex-tool-isolation-spike`,
    `WTs/production-api-contract`, both clean). Nineteen are ancestors of
    `main`. `codex-tool-isolation-spike` (a49bda9, 26 September 2026, "Record
    Codex no-environment tool isolation spike") is one commit ahead and 36
    behind; `git cherry` marks it equivalent to `main`'s 696282f, and `main`
    has since extended the spike's files; it holds nothing `main` lacks.
    `production-api-contract` (4f161c8, 4 October 2026, "Document development
    production profile public contract", Luis Fagundes) is one commit ahead
    and one behind (`main`'s 0a09e05): 201 lines added to
    `shop-skills/machinome-api/SKILL.md`. The rehearsal rewrote it to
    9e34081 with the same mapping.
16. **The split-word gate after the tool's correction** (the gate's `scan`
    run on the prototype): 6 occurrences left, all the ordinary adjective:
    `mcp_server.py` 759 "Stage the exact paths given" and 1235 "Exact paths to
    stage", `preparation.py` 648 "an exact project repository" and the
    identifier `_require_exact_repository` (three uses).
17. **The bundled packages' notices**: the eleven built `static/assets/*.js`
    files hold one occurrence of "license" in all; vite's minified output
    keeps no notice of the packages of "What the join touches".

## Goals / Non-Goals

**Goals:**

- machinome-studio joins at `packages/machinome-studio/` with the whole
  history of its `main`, every file at its final path, the merge rehearsed
  and clean.
- The studio is a product of the set at the address `machinome.studio`,
  numbered with it, under its licence, installed by `machinome[studio]` with
  `~=` pins, reached by `machinome studio`, built and smoked by
  `scripts/check-dist`, its wheel serving the hub, the profiles and the
  skills with no checkout.
- Its frontend the third npm member, built from the root; its tests green at
  their new place; its manual in the framework's; its record kept and
  brought current.
- The originating check: `machinome studio` on a scratch catalogue from the
  bench's venv, the hub and a project's floor page photographed.

**Non-Goals:**

- Any change to what the studio does for a maker: the hub, the floor, the
  profiles' roles and prompts beyond their skill lists, the backends, the
  broker, the configuration file and its keys, the port and its precedence.
- The studio's branches other than `main`; unifying its skills with the
  skills package beyond the one link; deriving the API skill from the manual;
  rewriting the skills' prose beyond what Decision 7 names.
- The workspace's consistency cycle (Decision 17), a version for upload, the
  original repository's fate, any push.

## Decisions

### 1. The join merges `main` and nothing else

`main` (0a09e05) is fetched rewritten (fd139a5) and merged; no other ref, no
tag (the product has none). Of the 21 branches (probe 15), nineteen are
ancestors of `main`, `codex-tool-isolation-spike` holds nothing `main` lacks,
and `production-api-contract` holds one unmerged commit, held for the pilot
(Open Questions 9): resumed later, it is a 201-line addition to
`P/shop-skills/machinome-api/SKILL.md`, fetched from a clone rewritten with
Decision 2's command (where it is 9e34081) and merged, or re-applied by hand.
The two active changes under `openspec/changes/` arrive as records of the
product; this change neither archives nor edits them.

### 2. The mapping and the import

Every path of the product, at 0a09e05 and in history, old to new or dropped
(`D` is `packages/machinome-studio`, `P` is `D/machinome/studio`, `M` is
`packages/machinome/docs`):

| at 0a09e05 (and in history) | lands at | reason |
|---|---|---|
| everything not named below | `D/` at the same relative path | the product's record and history in its directory: `README.md`, `CHANGELOG.md`, `pyproject.toml`, `.gitignore`, `tests/`, `openspec/`, `workflow/`, `scripts/build-favicon`, `scripts/test-e2e`; and, in history only, the Go broker, `src/shop_floor/`, `agents/`, the root `package.json` and `playwright.config.mjs` |
| `floor/` | `P/` | the package at its address |
| `frontend/` (history) | `P/frontend/` | the root frontend, moved to `floor/frontend/` on 20 July 2026, so the frontend reads at its path back to its start |
| `profiles/` | `P/profiles/` | the floor reads them from its resource root, which an installed wheel must hold (probe 6) |
| `shop-skills/`, `skills/` (history) | `P/shop-skills/` | the same; `skills/` is the directory `shop-skills/` was renamed from |
| `docs/adrs/` | `D/workflow/adrs/` | the product's own decision log under its own numbers, as the viewer's and the movie's |
| `docs/architecture-overview.md` | `D/workflow/architecture-overview.md` | the product's architecture as of the join; its summary goes to the framework's `docs/architecture.md` (Decision 15) |
| `docs/design/`, `docs/design_handoff_shop_desktop/` (history) | `D/workflow/design/` | the reference design, a record |
| `docs/product/`, `docs/spikes/` | `D/workflow/product/`, `D/workflow/spikes/` | stories, sprints and spikes, records |
| `docs/foreman-listener.md`, `docs/shop-history.md` (history) | `D/workflow/foreman-listener.md`, `D/workflow/archive/shop-history.md` | the paths `main` already gives them |
| `docs/index.rst` | `M/reference/studio/index.rst` | the section's index, rewritten in place (Decision 13) |
| `docs/reference/cli.rst` | `M/reference/studio/command.rst` | lookup: the command |
| `docs/reference/profiles.rst`, `project-configuration.rst` | `M/reference/studio/` | lookup |
| `docs/troubleshooting.rst` | `M/reference/studio/troubleshooting.rst` | lookup: symptoms and remedies |
| `docs/opening-a-project.rst` | `M/howto/open-a-studio-project.rst` | one job: open or create a project from the hub |
| `docs/the-floor.rst` | `M/howto/studio-workspace.rst` | one job: work in a project's workspace |
| `docs/working-with-agents.rst` | `M/howto/studio-agents.rst` | one job: choose and steer the agents |
| `docs/installation.rst`, `docs/project/status.rst` | dropped | the install facts go to the installation page and the opening how-to, the Codex login to the agents how-to, the source build to the contributor guide; the status facts to the section's index and the framework's status page (Decision 13) |
| `docs/conf.py`, `docs/requirements.txt`, `.readthedocs.yaml` | dropped | the manual is the framework's |
| `LICENSE`, `NOTICE` | dropped | one licence at the join; the package links the root's, the provenance goes to `CREDITS.md` |
| `AGENTS.md`, `CLAUDE.md` | dropped | the framework owns no agent prompts; the repository's contributor guide and the workspace's contract say how the studio is changed (Open Questions 5) |
| `.codex/` (with `.codex/agents/` of history) | dropped | the product repository's Codex development defaults and former role adapters: assistant configuration, not the product (Open Questions 5) |
| `.claude-plugin/` | dropped | the studio described as a Claude Code plugin; under pip-only distribution the package is the studio (Open Questions 5) |
| `scripts/setup` | dropped | it built the checkout's venv: the repository's `make sync` and `pip install "machinome[studio]"` replace it (Decision 11) |
| `solid-node`, `.gitmodules` (history) | dropped | a gitlink to the framework's former repository, from the workspace's early layout |

The command, run by the orchestrator in a fresh clone (`git clone
file:///home/asa/devel/machinome/machinome-studio <dir>`), as rehearsed in
probe 1 (`<scratch>/filter-repo-command.sh`). Every path first lands under
`D/`; the renames after the first refine that, in order, `git filter-repo`
applying them in turn:

```
D=packages/machinome-studio
P=$D/machinome/studio
M=packages/machinome/docs
git filter-repo \
  --path AGENTS.md --path CLAUDE.md --path .codex/ --path .claude-plugin/ \
  --path LICENSE --path NOTICE --path .readthedocs.yaml \
  --path docs/conf.py --path docs/requirements.txt \
  --path docs/installation.rst --path docs/project/status.rst \
  --path scripts/setup --path .gitmodules --path solid-node \
  --invert-paths \
  --path-rename :$D/ \
  --path-rename $D/floor/:$P/ \
  --path-rename $D/frontend/:$P/frontend/ \
  --path-rename $D/profiles/:$P/profiles/ \
  --path-rename $D/shop-skills/:$P/shop-skills/ \
  --path-rename $D/skills/:$P/shop-skills/ \
  --path-rename $D/docs/adrs/:$D/workflow/adrs/ \
  --path-rename $D/docs/architecture-overview.md:$D/workflow/architecture-overview.md \
  --path-rename $D/docs/design/:$D/workflow/design/ \
  --path-rename $D/docs/design_handoff_shop_desktop/:$D/workflow/design/ \
  --path-rename $D/docs/product/:$D/workflow/product/ \
  --path-rename $D/docs/spikes/:$D/workflow/spikes/ \
  --path-rename $D/docs/foreman-listener.md:$D/workflow/foreman-listener.md \
  --path-rename $D/docs/shop-history.md:$D/workflow/archive/shop-history.md \
  --path-rename $D/docs/index.rst:$M/reference/studio/index.rst \
  --path-rename $D/docs/reference/cli.rst:$M/reference/studio/command.rst \
  --path-rename $D/docs/reference/profiles.rst:$M/reference/studio/profiles.rst \
  --path-rename $D/docs/reference/project-configuration.rst:$M/reference/studio/project-configuration.rst \
  --path-rename $D/docs/troubleshooting.rst:$M/reference/studio/troubleshooting.rst \
  --path-rename $D/docs/opening-a-project.rst:$M/howto/open-a-studio-project.rst \
  --path-rename $D/docs/the-floor.rst:$M/howto/studio-workspace.rst \
  --path-rename $D/docs/working-with-agents.rst:$M/howto/studio-agents.rst
```

The `--path` filters read the original paths; the renames read the renamed
ones, so each after the first names a prefix under `D/`, and none names a
prefix another one's output begins with. The rewritten commits keep their
messages, authors and dates; the original repository keeps every dropped file
under the original hashes. The orchestrator then checks that `git ls-tree -r
--name-only main` lists the 738 paths of `<scratch>/rehearsal-ls-files.txt`,
that `main` is fd139a5 (*inferred* deterministic: the same input and
options), and that no commit of `main` touches a path outside `packages/`;
fetches `main` into the bench; and merges it with `git merge
--allow-unrelated-histories`, one merge commit, after the planning commit.

### 3. The package's directory

`D` after the cycle holds `pyproject.toml`, `README.md`, `CHANGELOG.md`,
`MANIFEST.in`, `.gitignore`, the links `LICENSE -> ../../LICENSE` and
`LICENSES -> ../../LICENSES`, the package directory `machinome/studio/` (its
own `__init__.py`, none at `machinome/`; `backends/`, `frontend/`,
`profiles/`, `shop-skills/` and the built `static/` inside it), `scripts/`,
`tests/`, `openspec/` and `workflow/`.

`pyproject.toml`, replacing the product's (built, locked, installed and run
in probes 5, 7 and 8):

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-studio"
version = "0.8.1"
description = "Machinome Studio: a project hub and workspace in the browser where a team of agents builds a machinome project with its maker"
readme = { file = "README.md", content-type = "text/markdown" }
requires-python = ">=3.11"
license = "GPL-2.0-or-later OR CERN-OHL-S-2.0+"
license-files = ["LICENSE", "LICENSES/*.txt"]
authors = [
    { name = "Luis Fagundes", email = "lhfagundes@gmail.com" },
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["machinome", "cad", "agents"]
dependencies = [
    # The framework whose `machinome` command the studio runs for every
    # build, test and snapshot, and the browser viewer whose bundle it serves
    # and through whose capture it photographs each project, released with
    # it: the set carries one version, and the pins between its packages are
    # ~= both ways. The studio imports neither's modules.
    "machinome~=0.8.1",
    "machinome-viewer[snapshot]~=0.8.1",
    "fastapi>=0.111,<1",
    "tomlkit>=0.13,<1",
    "uvicorn>=0.30,<1",
    "watchdog>=6,<7",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

# `machinome studio`, the third command a package contributes (ADR-189).
[project.entry-points."machinome.commands"]
studio = "machinome.studio.cli:Studio"

[tool.setuptools.packages.find]
# The package directory machinome/studio/, which has its own __init__.py,
# with none at machinome/, and its one subpackage backends/. The frontend's
# sources, the profiles and the skills beside them are data, not packages.
include = ["machinome.studio", "machinome.studio.backends"]
namespaces = true

[tool.setuptools]
include-package-data = false
zip-safe = false

[tool.setuptools.package-data]
# The built browser surface, and the profiles and skills the studio reads
# from its package directory; a skill linked from the skills package is
# carried as files.
"machinome.studio" = [
    "static/**",
    "profiles/**",
    "shop-skills/**",
]

[tool.setuptools.cmdclass]
sdist = "machinome.studio.packaging.BuildSourceDistribution"
build_py = "machinome.studio.packaging.BuildPythonWithFrontend"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- **`include-package-data = false`** with the three explicit globs, rather
  than the viewer's `exclude-package-data`: what the wheel carries is the
  list, so no file `MANIFEST.in` brings for the sdist (the frontend's sources,
  its configurations) reaches it; probe 7's wheel holds no frontend source.
- **`fastapi>=0.111,<1`**: the studio's former `>=0.115` cannot resolve
  beside the core's `fastapi==0.111.*` (probe 5), and the studio has run on
  0.111.1 in the workspace venv, its tests passing (probe 10); the floor is
  the viewer's (Open Questions 15).
- **`machinome-viewer[snapshot]`**: the hub photographs every project through
  `machinome snapshot --renderer web`, which needs the viewer's capture and
  Playwright; the 0.1.0 setup script installed both. Playwright is then the
  viewer's (1.63.0 in the lock) and the `e2e` extra's 1.61.0 goes with the
  extra (Open Questions 8). Chromium stays a second step, `playwright install
  chromium`.
- The `e2e` and `docs` extras go: the workspace's dev group installs the
  tools, and the manual is the framework's. The console script goes (Open
  Questions 1).

`README.md`, replacing the product's, in the products' shape:

```markdown
# machinome-studio

The studio of [Machinome](https://github.com/machinome/machinome): the
package `machinome.studio` and the command `machinome studio`. It opens a
project hub in the browser over a folder of projects; opening a project
starts a session of its own, with the agents its profile declares, the
conversation with the one who speaks for them, the model in the browser
viewer following every change to its source, the project's files and the
printable pieces of its last build. The agents work inside the project's own
Git repository through Claude Code, OpenCode or Codex.

## Install

    pip install "machinome[studio]"
    playwright install chromium
    machinome studio --projects-dir PATH

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`MANIFEST.in`, new (probe 7):

```
include CHANGELOG.md
recursive-include scripts *
recursive-include workflow *
recursive-include openspec *.md *.yaml

# The frontend travels with its sources so a source distribution can
# rebuild it, and with its built output so installing needs no npm.
recursive-include machinome/studio/frontend *
prune machinome/studio/frontend/node_modules
recursive-include machinome/studio/static *
recursive-include machinome/studio/profiles *
recursive-include machinome/studio/shop-skills *

recursive-include tests *
recursive-exclude * __pycache__
recursive-exclude * *.py[co]
```

`.gitignore`, edited in place to this package's own leavings (the root's
covers `__pycache__/`, `*.py[cod]`, `/packages/*/build/`,
`/packages/*/*.egg-info/`, `/.venv/`, `/.env`, `/node_modules/`):

```
# This package's leavings the root's .gitignore does not name: the
# frontend's dependencies npm installs beside it, the browser surface it
# builds, the package's own test runs and its browser tests' reports.
node_modules/
/machinome/studio/static/
.pytest_cache/
playwright-report/
test-results/
```

**`P/packaging.py`**, new: the hooks of `[tool.setuptools.cmdclass]`,
importing the standard library and setuptools alone (setuptools loads it while
resolving `cmdclass`, before the package's dependencies exist). The sdist hook
always builds the frontend; the `build_py` hook builds it when
`static/index.html` is absent or older than a file of `frontend/` outside
`node_modules`. A build first refuses when any `node_modules` from the
frontend up to the filesystem root is a symbolic link, naming it (the
viewer's guard: inside the workspace `npm ci` writes the root's), then runs
`npm ci --no-audit --no-fund` and `npm run build` in the frontend, which
inside the workspace install at the root from the root lock and write
`static/` (vite's `outDir: "../static"`, unchanged).

**Headers.** Each of the 89 SPDX lines of the 88 current files of "What the
join touches" becomes `GPL-2.0-or-later OR CERN-OHL-S-2.0+` in its file's
comment syntax; the copyright lines stay; `index.html`'s comment is served to
browsers and says the same. The 16 records keep theirs. The frontend's
`package.json` gains `"license": "GPL-2.0-or-later OR CERN-OHL-S-2.0+"`.

### 4. The source at its address

- **The package root is lazy** (probe 9): `__init__.py` keeps its docstring,
  rewritten for `machinome studio`, and `__all__ = ["create_app"]`, the name
  read on first use through a module `__getattr__` (PEP 562), as the movie's
  root and `machinome.node.freecad`'s are. `machinome -h` and `machinome
  studio -h` then import no web framework, and `packaging.py` imports in an
  isolated build.
- **The resources are the package directory's**:
  `preparation.shop_resource_root()` returns `Path(__file__).resolve().parent`,
  its docstring saying the package directory holds `profiles/`, `shop-skills/`
  and `static/` in a checkout and in an installed wheel alike; `app.py`'s
  default profile lookup (its line 186, `parents[1]`) calls it. `STATIC_ROOT`
  (`Path(__file__).parent / "static"`) is unchanged.
- **The MCP server**: `mcp_server.mcp_command` runs `[python, "-m",
  "machinome.studio.mcp_server", ...]`; the two backends that start it put
  on `PYTHONPATH` the directory holding the package's `machinome/`
  (`shop_root.parents[1]`), not the resource root, which at the address would
  expose the package's modules as top-level names (`openspec`, `profiles`).
- **`codex_auth`**: `LOGIN_COMMAND = "python -m machinome.studio.codex_auth
  login"`, and its one absolute import at the address.
- **`orchestrator`**: `main()` parses its options and calls a new
  `run(arguments)`, the body `main()` had after parsing; `machinome studio`
  calls `run` with its own parsed options (Decision 6). `python -m
  machinome.studio.orchestrator` and `python -m machinome.studio` (the hub
  without agents, `__main__.py`) keep their parsers.
- **Docstrings** that spell `python -m floor...` or `machinome-studio` (the
  package's `__init__`, `launcher.py`, `__main__.py`) name `machinome studio`
  and the module forms at the address.
- **What keeps the word floor**: the product's word for a project's
  workspace, the MCP server's name `floor` and its tools `floor_*`, the
  environment variables `FLOOR_URL`, `FLOOR_SESSION`, `FLOOR_PORT` and
  `SHOP_FLOOR_STATIC_ROOT`, and the line the command prints, "shop-floor open
  at http://127.0.0.1:PORT" (Open Questions 11). They are protocol and
  vocabulary, not the module.
- **The studio imports no framework module.** Its modules import each other
  relatively or at `machinome.studio`; `machinome` loads only as the
  namespace's parent, its `__init__`, as every viewer process does since the
  viewer's join. It runs `machinome` beside its interpreter
  (`default_machinome_command()`, unchanged) and reads the viewer's bundle
  from `machinome viewer`'s report (unchanged).

### 5. The skills

- **The studio's own two stay**: `P/shop-skills/machinome` and
  `P/shop-skills/machinome-api`, their substance unchanged but for Decision 7.
- **`machinome-simulate` is linked**: `P/shop-skills/machinome-simulate` is
  the relative link
  `../../../../machinome-skills/machinome/skills/agent-skills/machinome-simulate`,
  and each profile exposes it as it exposes the others,
  `P/profiles/<profile>/skills/machinome-simulate ->
  ../../../shop-skills/machinome-simulate`. The wheel and the sdist carry the
  skill as regular files with the skills package's bytes, under
  `shop-skills/` and under each profile (probe 7).
- **The loader reads a profile's skill link one level.** `_skill_path`
  resolved a link fully and required its target's parent to be
  `shop-skills/`, which refuses a skill reached through `shop-skills/` into
  another package (probe 6's red, "must link directly to
  shop-skills/<skill>"). It now reads the profile's link itself
  (`os.readlink`, normalised against the link's directory) and requires that
  it names `shop-skills/<skill>` of the same shop, then requires that entry
  to be a directory holding `SKILL.md`, following its own link. A profile
  link into another profile, into a repository `skills/` directory or
  anywhere but `shop-skills/<skill>` is still refused. The studio's spec
  `shop-runtime-profile` states the rule (Decision 16; Open Questions 16 on
  the transitive link).
- **The allowlists**: the builder of `openspec-builder` and the designer and
  the machinist of `fordesmac` name `machinome-simulate` in their prompts'
  frontmatter `skills:` list; the foreman and the librarian do not (Open
  Questions 16).

### 6. The command `machinome studio`

`P/cli.py`, the class `Studio`, meeting ADR-189's contract and importing the
standard library alone (probe 9):

- docstring "Open the studio: the project hub and its agents, in the
  browser", `needs_node = False`;
- `add_arguments`: `--projects-dir PATH` (`type=Path`), `--port PORT`
  (`type=int`), and the launcher's two options it hides from its help,
  `--machinome-command` and `--backend-command BACKEND=COMMAND`
  (repeatable), each with the launcher's own defaults and help;
- `handle`: imports `machinome.studio.orchestrator` and calls `run(args)`,
  which resolves the project folder and port by `launcher.resolve_launch`
  (option, then `FLOOR_PORT`, then the configuration file
  `~/.config/machinome-studio/config.toml` or `MACHINOME_STUDIO_CONFIG`,
  then 9000), refuses without the OpenSpec CLI, prints "shop-floor open at
  http://127.0.0.1:PORT" once the hub listens, and runs until interrupted.
  Its refusals are the launcher's: `error: ...` on standard error and exit
  1; an unknown option exits 2. It opens no browser (Open Questions 11).

The framework's `load_dotenv()` reads `./.env` before any command, as for
every command; the launcher reads its environment after it. The module forms
stay: `python -m machinome.studio.orchestrator` (the same command),
`python -m machinome.studio` (the hub without agents), `python -m
machinome.studio.codex_auth login` (the separate Codex login). The console
script `machinome-studio` is not declared (Open Questions 1); the studio's
ADR 0033 is superseded in its command by ADR-193 (Decision 15).

### 7. The corrections the joined tree's gates require

The joined tree fails two permanent gates of the set (probe 3): the
split-word gate (ADR-180) on the studio's test tool, and the node-root gate
(ADR-181) on its skills. Both name behaviour the framework of this line
refuses. This design corrects them in this change, the pilot's word on that
held in Open Questions 12:

- **The test tool.** `mcp_server.machinome_test(path, failfast, engine)`:
  `engine` in `("brep", "mesh")`, passed as `--brep` or `--mesh`, refused
  otherwise naming both values; its schema `"engine": {"enum": ["brep",
  "mesh"]}` with the description "Comparison engine for this run: 'mesh'
  decides every geometric assertion on meshes (fast, not commit evidence);
  'brep' on the boundary-representation solids. Omitted: the project's .env
  decides, else brep."; the docstring the same. The tool's name is
  unchanged. Probe 16 leaves the gate six ordinary occurrences, which its
  tables admit (Decision 10).
- **The skills.** In `shop-skills/machinome/SKILL.md` and
  `shop-skills/machinome-api/SKILL.md`: the seven import statements from
  `machinome.node`'s root become imports from each name's module, as the
  framework's refusal names them (`from machinome.node.assembly import
  AssemblyNode`, `from machinome.node.cadquery import CadQueryNode`, `from
  machinome.node.frames import Frame`, `from machinome.node.fusion import
  FusionNode`, and the others of the gate's table); every line that names a
  test flag, the test variable or the tool's parameter takes the 0.8 spelling
  (`--mesh`, `--brep`, `SOLID_TEST_ENGINE`, `engine="mesh"`, `engine="brep"`),
  and a line quoting what `machinome test` prints quotes what the bench's
  `machinome test --mesh` prints. The prose that uses the 0.7 engine words as
  descriptions (the craft skill's eight lines with "faceted", the API skill's
  sixteen) stays as it is and is listed in `evidence.md`; the node-root gate
  is green afterwards.

### 8. The npm workspace's third member

- **The root `package.json`**'s `workspaces` gains
  `packages/machinome-studio/machinome/studio/frontend` after the movie's
  directory (as `join-movie` lands it); nothing else changes. The root
  `.npmrc`'s `install-strategy=shallow` (`join-movie`'s) installs the
  member's direct dependencies in `P/frontend/node_modules`.
- **The frontend's `package.json`**: name `@machinome/studio` (the widget is
  `@machinome/viewer`, the movie's `@machinome/movie`), version `0.8.1`, the
  set's licence; `private`, the scripts (`build` = `tsc -b && vite build`,
  `dev`, `test` = `tsc -b --pretty false`) and every dependency unchanged.
- **The lock.** The frontend's `package-lock.json` arrives with the join and
  is removed (`git rm`) in the implementation; its resolutions are seeded into
  the root lock as probe 4 did (`<scratch>/root-lock-seeded.json` shows the
  shape: the member's entry with its dependencies and development
  dependencies, `node_modules/@machinome/studio` linked to the member, and
  each `node_modules/<name>` of the member's lock as
  `<member>/node_modules/<name>`), then `npm install --no-audit --no-fund` and
  `npm install --package-lock-only` at the root. Expected: the frontend's 133
  resolutions kept, none of the root's moved, "up to date"; if a resolution
  moves, the applier stops and reports. The member keeps no lock of its own
  (Open Questions 3): nothing installs it outside the workspace, its wheel
  carrying the built surface. `MEMBER_LOCKS` (as `release-tooling` lands it)
  stays the movie's alone.
- **The built surface** is never tracked: `P/static/` is ignored, written by
  the frontend's build, the package's hooks, `make widget` (`npm run build
  --workspaces --if-present` builds it with the widget) and
  `make test PKG=machinome-studio`.

### 9. The pins, the uv workspace and the bench venv

- The studio requires `machinome~=0.8.1` and
  `machinome-viewer[snapshot]~=0.8.1` (Decision 3). The core's extra becomes,
  replacing the unpinned one and its comment:

  ```toml
  # Machinome Studio, the project hub and workspace where a team of agents
  # builds a project with its maker, and the command `machinome studio`
  # (`machinome.studio`), the repository's distribution machinome-studio,
  # numbered with the set.
  studio = [
      "machinome-studio~=0.8.1",
  ]
  ```

  `all` stays the kernels' and `dev` does not name it.
- The root's sources gain `machinome-studio = { workspace = true }` after
  `machinome-skills`; `exclude-dependencies` and its comment go (the lock
  resolves the member from the workspace); the default `dev` group gains
  `"machinome[studio]"`, its comment naming the studio, whose tests run from
  its directory and whose command the suite's conformance walk reads.
- `uv lock`: the movie's count plus two (195 on this base, probe 5); `uv sync
  --python 3.12`: one `__editable__` `.pth` file more, naming `D`. Then from
  `/tmp`: `machinome studio -h` lists `--projects-dir` and `--port`;
  `python -c "import machinome.studio"` names `P/__init__.py`; `import
  floor` raises `ModuleNotFoundError`.
- The bench runs `npm ci` at its root before the studio's tests, which need
  the built surface; never through a link to another checkout's
  `node_modules`, which the hook refuses.

### 10. The core

- **The layout gate**, `tests/test_repository_layout.py`. `PRODUCTS` gains:

  ```python
      'machinome-studio': ('machinome.studio', 'studio',
                           ('.gitignore', 'CHANGELOG.md', 'LICENSE',
                            'LICENSES', 'MANIFEST.in', 'README.md',
                            'machinome', 'openspec', 'pyproject.toml',
                            'scripts', 'tests', 'workflow')),
  ```

  `NODE_MEMBERS` (the mapping `join-movie` makes of it) gains
  `'packages/machinome-studio/machinome/studio/frontend': '@machinome/studio'`
  after the movie's. `TheNodeWorkspaceTest`'s tracked locks stay the root's
  and the movie's (red at the join: the frontend's own lock); the default
  group's test expects `machinome[studio]`; `TheContinuousIntegrationTest`
  gains the OpenSpec CLI's step before `make test` (Decision 11). The
  module's docstring names the studio and the change. `TheMakefileTest` (as
  `release-tooling` lands it) then holds `PACKAGES` and `TESTED` to the
  studio's directory and its rule.
- **The release records**, `tests/test_release_records.py`: the member is
  numbered with the core and its pins are `~=` (already their rules); a new
  `test_the_studio_s_frontend_version_files_agree`: the frontend's
  `package.json` version and the root lock's entry for the member equal the
  set's version, and `.bumpversion.cfg` names the `package.json`.
- **`.bumpversion.cfg`** gains, after the movie's tables:
  `[bumpversion:file(version):packages/machinome-studio/pyproject.toml]`
  (`version = "{current_version}"`),
  `[bumpversion:file(pins):packages/machinome-studio/pyproject.toml]`
  (`~={current_version}"`, which moves both pins) and
  `[bumpversion:file:packages/machinome-studio/machinome/studio/frontend/package.json]`
  (`"version": "{current_version}"`). No table for a lock: `make bump` (as
  `release-tooling` lands it) runs `npm install --package-lock-only` at the
  root. The applier proves the bump on a copy.
- **`tests/test_kernel_extras.py`**: `EXTRAS` gains `'studio':
  {f'machinome-studio~={VERSION}'}`, its comment naming the change. Red at the
  join: the extra lists the unpinned name. `tests/test_machinome_identity.py`
  already expects the extra's name; its comment on floors stays true.
- **The vet universe**, `machinome/vet/universe.toml`: `[contract] deny`
  gains `"machinome.studio"` after `"machinome.movie"`, with a comment naming
  the change (Open Questions 18): the studio serves, spawns agents and writes
  into projects. `tests/test_vet_universe.py`: `test_the_contract`'s tuple,
  and a new `test_the_studio_is_internal_and_its_former_name_outside`, two
  scratch projects as the viewer's test makes them: `from machinome.studio.app
  import create_app` is `framework-internal` naming `machinome.studio`, `from
  floor.app import create_app` is `outside-universe`. Red at the join: the
  first is pure (probe 12).
- **The split-word gate**, `tests/test_core_names_no_split_words.py`:
  `ORDINARY` gains `'machinome/studio/preparation.py': {'_require_ex'
  'act_repository'}`; `ORDINARY_TEXT` gains
  `'machinome/studio/mcp_server.py': ('ex' 'act paths given', 'Ex' 'act paths
  to stage')` and `'machinome/studio/preparation.py': ('ex' 'act project
  repository',)`, with a comment: the exact paths given and the exact root of
  a repository, the ordinary adjective (change `join-studio`). The tool's
  former names are corrected, not admitted (Decision 7).
- **`docs/conf.py`**: the release facts of the studio's pages (Decision 13)
  and nothing else; the path list for autodoc already takes every
  `packages/machinome-*` but the viewer, the studio's source among them,
  which imports nothing at build time.

### 11. The Makefile and CI

As `release-tooling` lands them:

- `PACKAGES` gains `machinome-studio` (in its sorted place, after
  `machinome-skills`); `TESTED` gains `machinome-studio` after
  `machinome-movie`.
- A variable beside `WIDGET` and `MOVIE_JS`:
  `STUDIO_FRONTEND := packages/machinome-studio/machinome/studio/frontend`.
- A rule, its typecheck and build first since the tests serve the built
  surface:

  ```make
  test-machinome-studio:
  	$(NPM) test --workspace $(STUDIO_FRONTEND)
  	$(NPM) run build --workspace $(STUDIO_FRONTEND)
  	cd packages/machinome-studio && $(PYTHON) -m pytest
  ```

  The browser tests skip there unless `MACHINOME_STUDIO_E2E=1` (Decision 14);
  the contributor guide names `MACHINOME_STUDIO_E2E=1 make test
  PKG=machinome-studio` for them.
- `CLEAN` gains `packages/machinome-studio/machinome/studio/static`, which the
  targets write and the package's `.gitignore` ignores.
- `make widget` builds the studio's frontend already (probe 4).
- CI's `test` job (`.github/workflows/python-app.yml`) gains, before "Run the
  tests", a step installing the OpenSpec CLI the studio's tests run (probe
  10): `npm install -g @fission-ai/openspec@1.6.0` (Open Questions 17). Its
  `make test` then runs the studio; its `dist` job's `make check` builds it.
  No other job changes.

### 12. `scripts/check-dist`: one row, installed from its wheel

The script's start refuses, as for the viewer and the movie, when the studio
is a member and `npm` is not on the PATH ("machinome-studio's browser surface
is built by npm; put Node 22 and npm on the PATH"); its docstring's account
of what it writes in the repository gains `P/static/` and the member's
`node_modules/`. The row, after the movie's, installed by path (no index
serves the package):

```python
    'machinome-studio': {
        # Installed from its wheel by path; the smoke reads the extra's
        # requirement from the core's metadata, loads both profiles from the
        # installed package and opens the hub on a scratch catalogue.
        'extras': [],
        'code': '''
import importlib.metadata as metadata
import os
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
import machinome.studio as studio
from machinome.studio.preparation import shop_resource_root
from machinome.studio.profiles import load_profile
distribution = metadata.distribution('machinome-studio')
version = metadata.version('machinome')
assert distribution.version == version, (distribution.version, version)
files = [str(path) for path in distribution.files]
shipped = [path for path in files if path.startswith('machinome/')
           and '__pycache__' not in path]
assert 'machinome/studio/cli.py' in shipped, shipped
assert 'machinome/studio/static/index.html' in shipped, shipped
assert 'machinome/studio/shop-skills/machinome-simulate/SKILL.md' in shipped, shipped
assert not [path for path in shipped if '/frontend/' in path
            or 'node_modules' in path or path == 'machinome/__init__.py'], shipped
root = shop_resource_root()
assert root == Path(studio.__file__).resolve().parent, root
assert root.is_relative_to(Path(VENV).resolve()), root
assert f'machinome~={version}' in distribution.requires, distribution.requires
assert f'machinome-viewer[snapshot]~={version}' in distribution.requires, distribution.requires
core = metadata.requires('machinome')
assert any(line.startswith(f'machinome-studio~={version}')
           and 'studio' in line.partition(';')[2] for line in core), core
(entry,) = [entry for entry in metadata.entry_points(group='machinome.commands')
            if entry.name == 'studio']
assert entry.value == 'machinome.studio.cli:Studio', entry.value
for name in ('openspec-builder', 'fordesmac'):
    profile = load_profile(name, shop_root=root)
    assert profile.agents, name
builder = load_profile('openspec-builder', shop_root=root).agent('builder')
assert [skill.name for skill in builder.skills] == [
    'machinome-api', 'machinome', 'machinome-simulate'], builder.skills
# The hub refuses to start without an OpenSpec CLI, which no wheel carries:
# a stand-in that answers its version stands for it here.
scratch = Path(tempfile.mkdtemp())
stand_in = scratch / 'bin' / 'openspec'
stand_in.parent.mkdir()
stand_in.write_text('#!/bin/sh\\necho 1.6.0\\n')
stand_in.chmod(0o755)
(scratch / 'catalogue').mkdir()
with socket.socket() as probe:
    probe.bind(('127.0.0.1', 0))
    port = probe.getsockname()[1]
hub = subprocess.Popen(
    [str(Path(VENV) / 'bin' / 'machinome'), 'studio', '--projects-dir',
     str(scratch / 'catalogue'), '--port', str(port)],
    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    env={**{key: value for key, value in os.environ.items()
            if key not in ('MACHINOME_STUDIO_CONFIG', 'FLOOR_PORT')},
         'PATH': f"{stand_in.parent}:{os.environ['PATH']}",
         'HOME': str(scratch), 'XDG_CONFIG_HOME': str(scratch)})
try:
    for _ in range(100):
        try:
            page = urllib.request.urlopen(f'http://127.0.0.1:{port}/').read()
            break
        except OSError:
            time.sleep(0.1)
    else:
        raise AssertionError('the hub did not answer')
    assert b'Machinome Studio' in page, page[:200]
finally:
    hub.terminate()
    output = hub.communicate(timeout=10)[0]
assert f'shop-floor open at http://127.0.0.1:{port}' in output, output
'''
        + LICENCES.substitute(name='machinome-studio')
        + '''
print('machinome-studio', distribution.version, 'module', studio.__file__,
      'hub answered')
''',
        'commands': [['machinome', 'studio', '-h']],
    },
```

The shipped-files assertions prove the static, the linked skill as a file,
no frontend source and no `machinome/__init__.py` (probe 7); the profiles'
loading proves the resource root in an installed environment (probe 8); the
hub proves the command serves the built surface. Red first: before the row
the script fails "machinome-studio has no smoke in scripts/check-dist". (In
the code string, `\\n` writes a newline into the stand-in script.)

### 13. The manual

By reader intent, under the workspace's `skills/write-the-manual/SKILL.md`:

| page | section | from |
|---|---|---|
| `howto/open-a-studio-project.rst`, "Open a project in the studio" | How-to guides, after the movie's | `opening-a-project.rst`, opened by the install and start of `installation.rst` |
| `howto/studio-workspace.rst`, "Work in a project's workspace" | after the above | `the-floor.rst` |
| `howto/studio-agents.rst`, "Choose and steer the studio's agents" | after the above | `working-with-agents.rst`, with `installation.rst`'s "Using Codex" |
| `reference/studio/index.rst`, "Studio" | Reference, after `reference/movie/index` | `index.rst`, with `project/status.rst`'s "What it runs against" and "Limits" |
| `reference/studio/{command,project-configuration,profiles,troubleshooting}.rst` | the section, in that order | `reference/cli.rst` (titled "The studio command"), the two reference pages, `troubleshooting.rst` |

- **Three how-tos and one reference section** (Open Questions 4): a maker
  opens a project, works in it, or chooses its agents; a host looks up a
  command option, a configuration key, a profile's roster or a symptom.
- **The links** (probe 13): every `:doc:` link of the eight pages to a
  page of the former layout names its new page, absolutely
  (`/reference/studio/command`, `/howto/studio-agents`, ...); a link to
  `installation` names `/start/install`, to `project/status`
  `/project/status`.
- **The release facts.** The pages' substitutions become the framework's:
  `|machinome-version|` becomes `|release|`; `docs/conf.py`'s release-facts
  block gains, as literals with a comment ("the studio's, held to its source
  by the studio's documentation test"), `studio_viewer_api = '20'`,
  `studio_claude_models`, `studio_claude_efforts`, `studio_codex_version =
  'codex-cli 0.157.1'`, `studio_codex_models`, `studio_codex_efforts` and
  `studio_build_volume = '250 × 210 × 220 mm'` (the values the studio's
  `conf.py` derived from `preparation.py`, `codex_auth.py`,
  `backends/codex_policy.py` and `build_package.py`), with their
  substitutions; the pages use `|studio_viewer_api|` and the others. The
  framework's manual reads no file of another package at build time, as the
  viewer's facts are held (the viewer's Open Questions 4).
- **The section's index**, rewritten in place: the title "Studio"; the
  landing's first two paragraphs; one sentence, "The studio is the package
  ``machinome-studio``, installed by ``machinome[studio]`` and numbered with
  the framework; ``machinome studio`` starts it."; the status page's "What it
  runs against" (the framework of this release with its viewer, API
  |studio_viewer_api| or later, Linux, the three backends, Codex's limits)
  and "Limits", rewritten for the joined package (no "clone of its
  repository", no `scripts/setup`); the toctree; no licence sentence, no
  link to the studio's former repository.
- **The opening how-to** gains, before its own sections, an install part:
  what is needed (Linux, Python 3.11 or later, Git, OpenSCAD, the OpenSpec
  CLI `npm install -g @fission-ai/openspec`, a logged-in backend), `pip
  install "machinome[studio]"`, `playwright install chromium`, and `machinome
  studio --projects-dir PATH`, then the configuration file once. Every
  `machinome-studio`, `python -m floor`, `python -m floor.orchestrator`,
  `python -m floor.codex_auth`, `scripts/setup`, `floor/static` and
  `npm --prefix floor/frontend` on the eight pages becomes `machinome studio`,
  the module forms at `machinome.studio`, or goes (the source build is the
  contributor guide's).
- **The command reference**: its title "The studio command"; the synopsis
  `machinome studio [--projects-dir PATH] [--port PORT]`; the module forms;
  the configuration file and the precedence unchanged.
- **The framework's pages**: `start/install.rst` names ``studio`` among the
  extras (the distribution ``machinome-studio``, the studio and its command,
  needing the OpenSpec CLI and a backend; ``playwright install chromium`` its
  second step) and ``machinome-studio`` among the packages of the set under
  the same licence; `reference/cli.rst`'s "Commands from other packages"
  names the studio's command among the others' and a section `machinome
  studio` (anchor `.. _studio-command:`) gives the synopsis, the options,
  the module forms, the exit statuses and a link to
  :doc:`/reference/studio/command`; `project/status.rst`'s paragraph on the
  studio says it is the package ``machinome-studio`` of the set, experimental
  (its roles, prompts and disciplines exercised and revised on real
  projects), on Linux only, and that no index serves it until the set's next
  release; `index.rst` gains the three how-tos and `reference/studio/index`.
  `project/upgrading.rst`'s 0.8 sentence on the `studio` extra ("remains
  experimental and unpublished and cannot be installed from an index") is
  put in that release's past, "In 0.8 the ``studio`` extra named Machinome
  Studio, which no index served."; the 0.9 section the release cycle writes
  says the studio joined.
- **The pins**: `test_docs_structure.py` gains the toctree entries, the
  install page's distribution and lines, the CLI section, `KernelExtrasTest.STALE`
  gaining `github.com/machinome/machinome-studio`, `machinome-studio
  --projects-dir` and `python -m floor` (`RECORDS` admitting the last in
  `project/changelog.rst`, whose entry names the former command), and no
  page saying the studio is to add its command; the
  studio's `tests/test_documentation.py` reads the folded pages (Decision 14).
- **The build**: `sphinx -b html -n -W --keep-going` with
  `docs/requirements.txt` alone, exit 0 (probe 13); the new pages looked at.

### 14. The tests at their new place

- **Imports and paths**: `floor` becomes `machinome.studio` in the 42 modules
  and the six fixtures (`from machinome.studio...`, `patch("machinome.studio...")`,
  `"-m", "machinome.studio..."`); the resource root a test passes as
  `shop_root` is the package directory (`ROOT / "machinome" / "studio"`);
  `ROOT / "floor" / ...`, `ROOT / "profiles"` and `ROOT / "shop-skills"`
  name their places under it; the fake Claude CLI's probe of the importable
  package names `machinome.studio`; the `PYTHONPATH` expectations name the
  import root (Decision 4). The Codex fixtures build their role context from
  the same root.
- **Copied profiles**: a test that copies the profiles into a temporary shop
  copies `shop-skills/` with its links followed (`shutil.copytree(...,
  symlinks=False)` for that directory), since the copy's relative link to the
  skills package would dangle there (probe 10).
- **Rewritten pins**: `test_packaging.py` holds the entry point in
  `machinome.commands` and no `[project.scripts]`; `test_license_headers.py`
  holds every SPDX line of the package's tracked current files (outside
  `openspec/changes/archive/`, `workflow/design/`, `workflow/spikes/`,
  `workflow/archive/`) to the set's expression, read from the core's manifest,
  and names no other licence; `test_machinome_identity.py` holds the
  manifest's name and description and the scripts' product paths
  (`build-favicon`, `test-e2e`); `test_product_identity.py` loses the plugin
  and setup-script tests with the files they read, and reads the frontend at
  `P/frontend/`; `test_documentation.py` is rewritten for the folded manual,
  as the viewer's was: the repository root four levels above it, the eight
  pages under `packages/machinome/docs/`, the manual's build files absent from
  the package, the framework's `conf.py` literals equal to the source
  constants they state, every launcher option and configuration key in
  `reference/studio/command.rst`, no page naming a catalogue project, a
  checkout path, `python -m floor` or the console script.
- **A new test**, `test_the_studio_imports_no_framework_module`: every
  absolute import of `P/**/*.py` naming `machinome` names `machinome.studio`
  or beneath it.
- **A new test**, `test_a_profile_skill_may_reach_another_package_through_shop_skills`
  (Decision 5): a temporary shop whose `shop-skills/<skill>` links a skill
  directory elsewhere loads; one whose profile link names anything but
  `shop-skills/<skill>` is refused. Red at the join: "must link directly".
- **The browser tests opt in**: `test_shop_lifecycle_e2e.py`'s class skips
  unless `MACHINOME_STUDIO_E2E=1`, naming the variable (Open Questions 7); its
  real-bundle test finds the viewer at `machinome.viewer.web` (it imports the
  viewer's former module name today).
- **`scripts/test-e2e`** builds the frontend from the root (`npm run build
  --workspace ...`) and runs the three modules with `MACHINOME_STUDIO_E2E=1`;
  `scripts/build-favicon` reads and writes under `P/frontend/public/assets/`.
- **`test_scoped_tools.py`**: the test tool's test takes `engine="mesh"` and
  `engine="brep"` (Decision 7), and the refused value names both.

A contributor runs them with `make test PKG=machinome-studio`, or `python -m
pytest` from `packages/machinome-studio` after the root's `npm ci` and the
frontend's build, with the OpenSpec CLI on the PATH. The core's suite does
not collect them.

### 15. The records

- **`HISTORY.rst`**, at the end of `Unreleased`, after the movie's bullet:

  ```
  * **The studio joins the repository.** Machinome Studio, developed in a
    repository of its own, is the package ``machinome-studio`` at
    ``packages/machinome-studio/``, its history kept: its Python package is
    ``machinome.studio`` (formerly ``floor``) and its command is ``machinome
    studio``, contributed through ``machinome.commands``; the console script
    ``machinome-studio`` is gone. Its frontend is the third member of the
    repository's npm workspace and its wheel carries the built surface, the
    profiles and the skills, ``machinome-simulate`` linked from the skills
    package. It is numbered with the set, installed by ``machinome[studio]``,
    licensed as every package of the repository, keeps its changelog,
    specs, decision log and tests in its directory, and its manual is part
    of this one; ``machinome vet`` refuses a model that reaches it. Its test
    tool and its skills take the engines' and the node package's 0.8
    spellings. Change ``join-studio`` (ADR-193).
  ```
- **`docs/project/changelog.rst`**, at the end of `Unreleased`:

  ```
  * **The studio is part of this manual.** Opening a project in the studio,
    working in its workspace and choosing its agents are how-to guides
    (:doc:`/howto/open-a-studio-project`, :doc:`/howto/studio-workspace`,
    :doc:`/howto/studio-agents`), and its command, configuration, profiles
    and troubleshooting are the reference section
    :doc:`/reference/studio/index`. ``pip install "machinome[studio]"``
    installs it, numbered with the framework, and ``machinome studio``
    starts it: a script that ran ``machinome-studio`` or ``python -m floor``
    runs ``machinome studio`` or ``python -m machinome.studio``.
  ```
- **The studio's `CHANGELOG.md`**: its `Unreleased` section's opening
  paragraph says the studio, numbered with Machinome, runs against the
  framework and viewer of its own release; a subsection `### Joined to the
  Machinome repository` above `### What a maker gets`:

  ```
  - Machinome Studio is part of the Machinome repository,
    <https://github.com/machinome/machinome>, at `packages/machinome-studio/`,
    with its history. Its Python package is `machinome.studio` (formerly
    `floor`), a portion of the `machinome` package, and its command is
    `machinome studio`; the `machinome-studio` command is gone, `python -m
    machinome.studio` serves the hub without agents, and the configuration
    file, its keys and the project's `[tool.machinome-studio]` table are
    unchanged. It is numbered with Machinome, installed by
    `pip install "machinome[studio]"`, and licensed as every package of the
    repository, GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the
    recipient's choice. Its manual is part of Machinome's,
    <https://machinome.readthedocs.io>. Its frontend builds from the
    repository's npm workspace and its wheel carries the built surface, the
    profiles and the skills.
  - The profiles' agents may load `machinome-simulate`, the skills package's
    skill for reconstructing an existing design; the builder, the designer
    and the machinist allowlist it.
  - The `machinome_test` tool takes `engine` (`brep` or `mesh`), the
    framework's flags since 0.8, in place of `kernel`; the two skills import
    each node name from its module.
  ```

  The "A manual under `docs/`" bullet of "What a maker gets" says the manual
  is part of Machinome's.
- **`CREDITS.md`** (the framework's): a section "### Carried by the studio"
  after the viewer's, stating the fonts (Machinome Logo Regular derived from
  Anta, Space Grotesk, IBM Plex Mono: SIL OFL 1.1, the copyright lines of
  their notices, the notices kept beside them under
  `P/frontend/public/assets/`), the identity's artwork and its trademark
  statement (Open Questions 13), and the frontend's runtime packages bundled
  into `P/static/` with their versions read from the root lock and their own
  licences (Open Questions 14); the section "Adapted from Machinome Studio,
  in the skills package" names the studio's package
  (`packages/machinome-studio/`) rather than its former repository.
- **`docs/architecture.md`**: a short section "Studio (STUDIO · specs
  `studio-distribution`, `cli`)": the repository's distribution
  `machinome-studio` at `packages/machinome-studio/`, the package
  `machinome.studio`, a product that runs the framework's command and reads
  the viewer's report as processes of its own, its architecture and
  decisions in its own `workflow/architecture-overview.md` and
  `workflow/adrs/` (ADR-193); the Commands paragraph's "the movie's and the
  studio's follow at their joins" names both as contributors; the Map gains a
  row for the studio.
- **The root `README.md`**: a row after the movie's:
  ``| [`machinome-studio`](packages/machinome-studio/) | The studio, `machinome.studio`: the project hub and workspace where a team of agents builds a project with its maker, and the command `machinome studio`; installed by `machinome[studio]`. |``
- **`CONTRIBUTING.rst`**: the pip block gains `-e packages/machinome-studio
  \`; "Development environment" names the OpenSpec CLI (`npm install -g
  @fission-ai/openspec@1.6.0`) as what the studio's tests run; "Running tests"
  gains the studio's sentence (Decision 14), its browser tests' opt-in and
  the frontend's build from the root; the source build of the studio's
  browser surface (`npm run build --workspace
  packages/machinome-studio/machinome/studio/frontend`).
- **`context7.json`**: `excludeFolders` gains `packages/machinome-studio/openspec`,
  `packages/machinome-studio/tests` and `packages/machinome-studio/workflow`;
  a rule: "Machinome Studio is machinome.studio, the repository's distribution
  machinome-studio, installed by pip install \"machinome[studio]\" and
  numbered with the framework; machinome studio --projects-dir PATH opens its
  project hub on 127.0.0.1, the port from --port, FLOOR_PORT or
  ~/.config/machinome-studio/config.toml, else 9000. It needs the OpenSpec CLI
  on the PATH and a logged-in Claude Code, OpenCode or Codex; a project
  selects its profile and agents' runtimes in [tool.machinome-studio] of its
  pyproject.toml."
- **`AI-USE.md`**: machinome-studio leaves the list of sibling repositories;
  the paragraph on what is agent-written names the studio under
  `packages/machinome-studio/`, joined with its history on the join's day.
- **ADR-193** (Open Questions 10),
  `docs/adrs/BUILD/ADR-193-the-studio-is-a-product-of-the-set-reached-by-machinome-studio.md`,
  Status Proposed, Change `join-studio`. Context: the pilot's decisions of
  12 October 2026; probes 5 to 10 and 12. Options: (1) the studio a product of
  the set at `machinome.studio`, its resources in its package directory, its
  command contributed, the console script dropped (chosen); (1') the same
  with the console script kept as an alias (Open Questions 1); (2) the
  studio's resources beside the package, found from the checkout (refused:
  probe 6, an installed wheel holds no checkout); (3) the studio kept outside
  the set, consuming its packages (refused by the pilot). The decision outcome
  states Decisions 3 to 12 and the vet's denial. Consequences: good, one
  licence, one version, one command, one manual, the studio installable by
  pip from the set; bad, the studio's lock floor for fastapi follows the
  core's pin; its tests need the OpenSpec CLI and the built surface; the wheel
  carries third-party minified code whose notices it does not hold today
  (Open Questions 14); neutral, the studio still reaches the framework and
  the viewer only as processes. Amends ADR-182 (a third npm member, keeping
  no lock of its own), ADR-188 (the studio's frontend beside the widget) and
  ADR-189 (its third contributor), each with the dated consequence "Neutral
  (2026-10-12, `join-studio`): ..." and "amended by 193". Its index line under
  BUILD after ADR-192.
- **The studio's decision log**, `D/workflow/adrs/README.md`: a dated note
  under its opening, "(12 October 2026, change `join-studio`) The studio
  joined the machinome repository at `packages/machinome-studio/`; this log
  stays its own, numbered `0001` on, beside the framework's
  `packages/machinome/docs/adrs/`. A number of four digits names this log's
  ADR; the framework's are cited as 'framework ADR-nnn'. ADR 0033's command
  is superseded by framework ADR-193: the studio starts with `machinome
  studio`." ADR 0033's status line gains "command superseded by framework
  ADR-193"; the records are otherwise untouched; the index's reference to
  `docs/architecture-overview.md` names `../architecture-overview.md`.
- **The plan's progress** (`workflow/ongoing/release-0.9.md`): the cycle's
  entry at its close.

### 16. The product's record, brought current in place

The applier edits, in place and with no change of behaviour beyond Decisions
4 to 7:

- `openspec/config.yaml`'s context (if it names the package or the
  repository): the studio is the repository's package `machinome.studio` at
  `packages/machinome-studio/`.
- `openspec/specs/shop-floor-lifecycle/spec.md`, "The shop starts from an
  installed command": `machinome studio` in place of `machinome-studio`, and
  `python -m machinome.studio.orchestrator` and `python -m machinome.studio`
  in place of the `floor` forms; scenario titles kept.
- `openspec/specs/shop-runtime-profile/spec.md`, "Profile prompts and skills
  are contained and allowlisted": the profile's link names
  `shop-skills/<skill>`, read one level, and that entry may be a link into the
  skills package of the same repository (Decision 5); a scenario added for
  `machinome-simulate`; titles kept.
- `openspec/specs/scoped-agent-tools/spec.md`: the test tool's `engine`
  (Decision 7); titles kept.
- `openspec/specs/user-documentation/spec.md`: the manual is the studio's
  pages of the Machinome manual, built with it from its requirements; the
  command reference names `machinome studio`; titles kept.
- `openspec/specs/product-identity/spec.md`: the package `machinome.studio`
  and the command `machinome studio` beside the identifier
  `machinome-studio`, which stays the distribution's, the configuration
  directory's and the project table's; the plugin's identifiers go with the
  plugin; titles kept.
- `workflow/README.md` and `workflow/documentation.md`: the notes in force,
  the latter saying the pages are in the framework's manual (the three
  how-tos and `reference/studio/`), built with it; the other notes are
  records of their day.
- `P/frontend/README.md`: the commands from the repository's root (`npm ci`,
  `npm run dev|build|test --workspace ...`), `static/` beside the package's
  modules, `make test PKG=machinome-studio` for the browser tests with their
  opt-in.

`env -C packages/machinome-studio openspec validate --specs --strict` passes
afterwards. The two active changes and every archived record stay as written.

### 17. Workspace and project follow-ups, outside this repository

Listed for the workspace's consistency cycle (`release-0.9.md`, decision 11);
none is done by this cycle:

- the operating contract's studio paragraphs and section (`AGENTS.md`: an
  independent repository, the launcher `machinome-studio` on the venv's
  PATH, "never imports the framework", its own `AGENTS.md`), its layout block
  and its lane "On the shop floor", which names the command;
- `docs/collaborator-setup.md` and `scripts/setup` (both tiers clone the
  studio at `machinome-studio/`, install it editable and build its frontend);
- the skills that name the launcher or `floor/` (`debug-workflow`, `sprint`,
  `simulate-project`, `write-the-manual`) and the workspace's specs
  `framework-change-protocol` and `sprint-coordination`;
- the pilot's running floor, started with `machinome-studio` on port 9010,
  which `machinome studio --port 9010` replaces once the workspace venv
  installs the set from the repository; the configuration file
  `~/.config/machinome-studio/config.toml` is read unchanged;
- the original repository on GitHub and its two worktrees, the pilot's;
- no project repository moves (Context).

### 18. Validation and the originating check

The suite from `packages/machinome` (expected: the line's count with the
tests this change adds, its skips unchanged); the studio's tests from its
directory (expected: every test passes or skips naming what is absent; the
browser tests once with `MACHINOME_STUDIO_E2E=1`, Chromium for the locked
Playwright, and the viewer's bundle built); the frontend's typecheck and
build from the root, and the widget's and the movie's as `make test` runs
them; the manual with warnings as errors from `docs/requirements.txt` alone,
the eight pages looked at; `scripts/check-dist` on the tree and on a clean
copy (seventeen members, 34 archives); `env -C packages/machinome-studio
openspec validate --specs --strict`. No universe sweep: no project imports
the studio or names its launcher (Context), and no module of the core
changes but `universe.toml`'s denylist, which no project's model reaches; the
evidence states it. The originating check, on the bench's venv: `machinome
studio --projects-dir <scratch catalogue>` holding a fresh clone of
`Vibecoded-demos/gear-shift`, on a port other than the pilot's 9010; the hub
page photographed in Chromium; the project opened to its floor page by
`python -m machinome.studio` on the same catalogue (no agent run: the
backends are the pilot's accounts) and photographed with its model in the
viewer; both stopped (probe 14 rehearsed it).

### 19. The spec deltas

- `framework-identity`: MODIFIED "Extras select independent Machinome
  products", composed from `join-movie`'s text: the `studio` extra pins the
  set's studio `~=`, the sentence that the extra cannot resolve goes, the
  scenario "A reader asks for the studio extra before publication" keeps its
  title and says what the guidance now states, one scenario added ("A user
  installs the studio extra"); ADDED "The studio is a product of the set and
  the third member of the npm workspace", as `join-movie` added its own
  rather than modifying the monorepo requirement `release-tooling` modifies.
- `cli`: ADDED "Studio command".
- `cli-startup-cost`: ADDED "The studio command loads none of the studio's
  application to be listed".
- `vet`: ADDED "A model that reaches the studio is refused".
- `user-documentation`: ADDED "The studio is documented in the manual".
- `framework-contributor-guidance`: ADDED "The contributor guide says how the
  studio's tests run".
- `studio-distribution`: new, four requirements.

## Risks / Trade-offs

- [The studio's skills keep 0.7 engine words in their prose] → Decision 7
  corrects every flag, variable, parameter and import a runtime agent would
  run; the descriptive words are listed in the evidence and left to the
  skills' later derivation from the manual, deferred by the pilot (Open
  Questions 12 offers the full pass).
- [The test tool's parameter changes for runtime agents] → The skills that
  teach it change in the same commit; an agent that sends `kernel` is refused
  by the tool's schema, naming the accepted parameter.
- [A source checkout's profile link reaches the skills package through two
  links] → The loader reads the profile's link one level and still refuses
  every other target; an installed wheel holds files (Decision 5).
- [The studio's tests need the OpenSpec CLI and the built surface] → `make
  test` builds the surface; CI installs the CLI (Decision 11); the guide names
  both.
- [The browser tests are timing-sensitive under load] → Opt-in (probe 10's one
  failure did not recur); the cycle's evidence runs them once.
- [The wheel carries minified third-party code without its notices] → Open
  Questions 14; `CREDITS.md` states the packages in the meantime.
- [The identity's artwork is not under the set's licence] → Open Questions
  13; the carve-out the studio states today is kept in `CREDITS.md` and the
  brand README.
- [The fastapi floor drops to 0.111] → The studio runs on 0.111.1 in the
  workspace today, its tests green (probe 10).
- [The joined archived records and design files keep the licence the product
  carried] → Historical records, as in the earlier joins.
- [Rehearsed before the movie and release-tooling landed] → The import touches
  no path they add; the npm seeding and `uv lock` are rerun on the landed
  line, each expected count stated against the landed one.

## Migration Plan

In the order of tasks.md: the baseline; the join, by the orchestrator, and the
reds it causes; the red gates; the package and its source; the corrections;
the npm workspace; the core, the uv workspace and the sync; the tests at their
new place; the manual; the Makefile, `check-dist` and CI; the records; the
product's record; validation and the originating check; the archive.
Rollback is a revert of the implementation commit and of the merge commit,
`uv lock`, `uv sync`, and `npm ci` at the root.

## Open Questions

Each carries a recommendation; the orchestrator's review and the pilot's word
settle them.

1. **The console script.** Keep `machinome-studio` as an alias of `machinome
   studio`, or drop it. Recommendation: drop it; the pilot wants one command,
   no project names the launcher, and the workspace's consistency cycle
   rewrites the contract's launcher line and the pilot's floor's start
   (Decision 17). If kept, the manifest gains `[project.scripts]
   machinome-studio = "machinome.studio.orchestrator:main"` and the packaging
   test holds it.
2. **The profiles' and skills' place.** Inside the portion as package data, or
   beside it in the package directory. Recommendation: inside; the studio
   reads them from its resource root, and only a path inside the package
   reaches an installed wheel (probes 6 to 8).
3. **The frontend's lock.** A lock of its own beside the root's, as the movie
   keeps, or none. Recommendation: none; the movie's lock serves an installed
   copy's `machinome movie setup`, while the studio's wheel carries the built
   surface and nothing installs the frontend outside the workspace.
4. **The manual's section.** Three how-tos and a reference section, or one
   section "Studio" holding all eight pages. Recommendation: the split, as the
   viewer's and the movie's pages are placed: a maker's job and a host's
   lookup are different intents.
5. **`AGENTS.md`, `CLAUDE.md`, `.codex/` and `.claude-plugin/`.** Dropped at
   the join, or kept in the package directory. Recommendation: dropped; the
   first three are the product repository's assistant contract and
   configuration, which the framework does not keep (the workspace holds the
   development contract, `CONTRIBUTING.rst` the repository's); the plugin
   manifest describes the studio as a Claude Code plugin of 26 September 2026
   (version 0.1.0, roles it no longer has), and under pip-only distribution
   the package is the studio. Packaging the studio for an assistant again is
   a later decision with its own evidence.
6. **The ADRs' place.** The studio's 34 ADRs in its `workflow/adrs/` under
   their own numbers, or renumbered into the framework's log.
   Recommendation: its own log, as the viewer's and the movie's; renumbering
   would break every citation in the studio's code, specs and records.
7. **The browser tests in CI.** Recommendation: not in CI, as the movie's
   browser projects; they opt in with `MACHINOME_STUDIO_E2E=1`, run in the
   cycle's evidence and on a contributor's machine. Probe 10 saw one
   timing failure under a full run that did not recur.
8. **The Playwright version.** The `e2e` extra's 1.61.0 kept, or the viewer's
   `snapshot` extra's, locked at 1.63.0. Recommendation: the viewer's; the
   studio requires `machinome-viewer[snapshot]` for its previews, so one
   Playwright and one Chromium serve the capture, the movie and the studio's
   browser tests; the `e2e` extra goes.
9. **The studio's branches.** Held for the pilot (Decision 1):
   `production-api-contract` holds one commit `main` lacks;
   `codex-tool-isolation-spike` nothing. Recommendation: keep them in the
   original repository; resume the first, if wanted, as a change of the joined
   package.
10. **The ADR.** ADR-193, or amendments only. Recommendation: ADR-193; the
    join makes choices no record holds: the third product numbered with the
    set, the resources in the package directory for an installed wheel, the
    command replacing the console script, the skill reached through
    `shop-skills/` into another package. If declined, the HISTORY bullet's
    "(ADR-193)" becomes "(ADR-182, ADR-188 and ADR-189 amended)".
11. **What `machinome studio` prints and when it opens a browser.**
    Recommendation: unchanged; it prints "shop-floor open at
    http://127.0.0.1:PORT" once the hub listens and opens no browser: the hub
    runs on a machine the maker may reach from another, and the line is what
    the studio's tests, its manual and the pilot's routine read.
12. **The corrections the gates require** (Decision 7). In this change, in a
    studio change of its own before the join (in the original repository), or
    the gates relaxed for the studio. Recommendation: in this change, because
    the joined tree cannot pass ADR-180's and ADR-181's gates otherwise, and
    because both name behaviour the framework of this line refuses (the
    framework's `release-0.8.0.md`, section (c)). This exceeds the plan's
    statement of the join and needs the pilot's word; if declined in favour
    of a relaxed gate, the gates gain the studio's two skills and its
    `mcp_server.py` as exceptions and Decision 7 goes. A full pass over the
    skills' prose is a further option, recommended against here (the pilot
    deferred the skills' derivation).
13. **The identity's artwork.** The studio carries the identity's marks and its
    favicon pack, which its own record says carry no public licence and are
    trademarks of Poiesis Tecnologia da Informação LTDA, while the set's rule
    is one licence for every file. Recommendation: keep the carve-out as the
    studio states it today: `CREDITS.md`'s studio section and
    `P/frontend/public/assets/brand/README.md` say the artwork carries no
    public licence and the marks are trademarks of Poiesis Tecnologia da
    Informação LTDA, which the repository's licence grants no right to use,
    the brand README pointing at `CREDITS.md` instead of the dropped `NOTICE`;
    the `NOTICE`'s sentence that a modified version must carry its own name
    and marks is left to the pilot, since it was written as an additional term
    of the licence the product carried. The pilot may instead license the
    artwork under the set's licence, or move it out of the package.
14. **The bundled packages' notices.** The built surface carries react,
    monaco-editor, three, dompurify and seven more, minified, with no notice
    (probe 17). Recommendation: `CREDITS.md` names them with versions and
    licences in this change; carrying their notices in the wheel (a notices
    file written into `static/` by the build) is a change of its own with the
    pilot's word, since the 0.1.0 surface never did.
15. **The fastapi floor.** `fastapi>=0.111,<1`, the viewer's, or the core's
    pin raised. Recommendation: the floor lowered; raising the core's pin is
    a framework change with no finding behind it, and the studio runs on
    0.111.1 today.
16. **`machinome-simulate`'s allowlist and its transitive link.** Which roles
    name it, and whether the loader's rule may admit one link from
    `shop-skills/` into the skills package. Recommendation: the builder, the
    designer and the machinist (the roles that design and machine a
    reconstruction; the foreman assigns and the librarian researches); the
    rule as Decision 5 states it, which still refuses every target but
    `shop-skills/<skill>` for the profile's own link.
17. **The OpenSpec CLI in CI.** A global install in the test job, or a
    development dependency of the frontend member that `make test` puts on
    the PATH. Recommendation: the global install of the version this machine
    runs, 1.6.0; the CLI is the studio's runtime prerequisite, which a maker
    installs the same way, and a member dependency would put a tool the
    frontend does not use into its lock.
18. **The vet's denial.** `machinome.studio` denied, or left in the contract.
    Recommendation: denied, as the viewer and the movie are; a model has no
    business importing the hub, and at the address it would pass (probe 12).
