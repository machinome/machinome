## Why

On 12 October 2026 the pilot settled what Machinome 0.9.0 contains
(`workflow/ongoing/release-0.9.md` at the repository root, decisions 1, 2, 3,
4, 6, 7 and 9): Machinome Studio, the project hub and workspace in which a
team of agents builds a machinome project with its maker, kept since
26 September 2026 in a repository of its own, experimental and never
published, joins the repository whole with its record in its directory, as
the distribution `machinome-studio` at `packages/machinome-studio/` and the
portion `machinome.studio` (no module `floor`, no alias), at the set's version
0.8.1 pinned `~=` both ways, under the set's licence, installed by the core's
extra `machinome[studio]`, reached by the command `machinome studio`, the
third contributor of the group `machinome.commands` (ADR-189), its manual
folded into the framework's, its frontend the third member of the npm
workspace, its two skills kept and `machinome-simulate` linked from the skills
package, pip only with the built browser surface in its wheel.

The probes of design.md find the product does not work at its new place as it
is. Its resources are found from its module's parent directory, which at
`machinome/studio/` names `machinome/`; its MCP server is run as `python -m
floor.mcp_server`; its manifest's `fastapi>=0.115` cannot resolve beside the
core's `fastapi==0.111.*` (`uv lock`: unsatisfiable); its profile loader
refuses a skill reached through two links ("must link directly to
shop-skills/<skill>"); its package root imports the whole application, so
`machinome studio -h` would take 351 ms where a lazy root takes 76 ms; and the
joined tree fails two permanent gates of the set: the studio's `machinome_test`
tool still offers the engines' 0.7 names `exact` and `faceted` and passes
`--exact`/`--faceted`, which `machinome test` has refused since 0.8.0, and its
two skills teach seven imports from the node package's root, which 0.8.0
refuses (ADR-180, ADR-181; the framework's
`workflow/ongoing/release-0.8.0.md` listed both as the studio's follow-ups).
The eight of its ten manual pages that land in the framework's manual build
there with 43 warnings.

## What Changes

- **The join, by the orchestrator, after the planning commit**: a fresh clone
  of machinome-studio rewritten by `git filter-repo` with the mapping of
  design.md Decision 2 (738 files land, 730 under `packages/machinome-studio/`
  and 8 in the framework's manual; 13 tracked files are dropped), its `main`
  (0a09e05, rewritten fd139a5, 318 commits) merged with
  `--allow-unrelated-histories`; rehearsed in the scratch directory, where the
  merge is clean and `app.py` reads at its new path, without `--follow`, back
  to 20 July 2026. The product's other branches are not joined; they are
  listed and held for the pilot (Decision 1).
- **`machinome-studio` at `packages/machinome-studio/`**, a product that keeps
  its record in its directory: its manifest at the set's version, requiring
  `machinome~=0.8.1` and `machinome-viewer[snapshot]~=0.8.1`, under the set's
  licence, declaring `studio = "machinome.studio.cli:Studio"` in
  `machinome.commands`, its built browser surface, profiles and skills as
  package data, the frontend built by the wheel's and the sdist's hooks as the
  viewer's bundle is; the package directory `machinome/studio/` with the
  frontend, the profiles and the shop skills inside it; its tests, specs,
  changes, working record, decision log (`workflow/adrs/`, its 34 ADRs under
  their own numbers) and changelog in its directory. **BREAKING** for whoever
  runs `machinome-studio`, `python -m floor` or `python -m floor.orchestrator`:
  the command is `machinome studio`, the modules `machinome.studio` and
  `machinome.studio.orchestrator`; the console script `machinome-studio` is
  not kept (no project imports `floor` or names the launcher, design.md
  Context).
- **The command `machinome studio`** with the options the launcher has
  (`--projects-dir`, `--port`, the configuration file, the environment), its
  output and its refusals unchanged; `python -m machinome.studio` serves the
  same hub without agents.
- **The studio at its address**: a lazy package root; the profiles and skills
  found in the package directory, in a checkout and in an installed wheel
  alike; the MCP server run as `python -m machinome.studio.mcp_server`; the
  word floor kept for the product's workspace, its MCP server name and its
  tools.
- **The skills**: the studio keeps `machinome` and `machinome-api`;
  `shop-skills/machinome-simulate` is a relative link into the skills
  package's `machinome-simulate`, which the wheel carries as files; the
  profile loader reads a profile's skill link one level, so that link is
  admitted; the builder, the designer and the machinist allowlist it.
- **The corrections the gates require** (design.md Decision 7, held for the
  pilot's word in Open Questions 12): the `machinome_test` tool's `kernel`
  (`exact`, `faceted`) becomes `engine` (`brep`, `mesh`) passed as `--brep`
  and `--mesh`; the two skills' node-root imports and their test flags and
  variable take the 0.8 spellings.
- **The npm workspace's third member**: the frontend, `@machinome/studio`,
  private, numbered with the set, its 133 resolutions seeded into the root lock
  (0 moved, none of the root's 264 entries changed), its own lock retired.
- **The core and the workspace**: the extra `studio =
  ["machinome-studio~=0.8.1"]` replacing the unresolvable `machinome-studio`;
  the root's source, `exclude-dependencies` gone, the default `dev` group
  installing `machinome[studio]`; `uv lock` resolves 195 packages on this base
  (two more than the base, the member and tomlkit); `machinome vet` denies
  `machinome.studio`; the layout gate, the release records, the bumpversion
  tables, the split-word gate's ordinary phrases, the Makefile's lists and a
  `test-machinome-studio` rule, CI's OpenSpec CLI step, and
  `scripts/check-dist`'s row, which installs the wheel by path, loads both
  profiles, and opens the hub on a scratch catalogue.
- **One licence at the join**: the product's `LICENSE` and `NOTICE` are
  dropped by the import; its manifests, 89 SPDX lines of 88 current files and
  its reader-facing pages state the set's expression; its fonts' notices, the
  bundled libraries of its browser surface and the identity's trademark
  statement go to `CREDITS.md` (Open Questions 13 and 14); no record this change
  writes names the licence it carried.
- **The manual folds in** by reader intent: three how-to guides (open a
  project in the studio, work in a project's workspace, choose and steer the
  agents) and the reference section `reference/studio/` (the studio, its
  command, the project configuration, the profiles, troubleshooting); the
  install page's row `pip install "machinome[studio]"` then `machinome
  studio`; the CLI reference's section `machinome studio`.
- **The tests at their new place**: the studio's 42 test modules run from
  `packages/machinome-studio/` (443 passed in the rehearsal before the
  pinning rewrites; 499 passed at the original layout); its browser tests
  opt in with `MACHINOME_STUDIO_E2E=1`; the core's suite collects none of them.
- **Records**: `HISTORY.rst`, the manual's changelog and the studio's
  `CHANGELOG.md`; `CREDITS.md`, `docs/architecture.md`, the root
  `README.md`, `CONTRIBUTING.rst`, `context7.json`, `AI-USE.md`; ADR-193
  (Open Questions 10), the studio's ADR 0033 superseded in its command,
  ADR-182, ADR-188 and ADR-189 amended; the studio's own specs and notes
  brought current in place.

Not in this change: the studio's branches other than `main` (held), the
unification of the studio's skills with the skills package beyond the link,
the derivation of the API skill from the manual, a version for upload, the
workspace's consistency cycle (the contract's studio section and launcher
line, `scripts/setup`, the collaborator setup, the pilot's running floor),
the original repository's fate, any push.

## Capabilities

### New Capabilities

- `studio-distribution`: the package `machinome-studio`, what its wheel ships
  (the built browser surface, the profiles, the skills, the link to
  `machinome-simulate` carried as files), where its resources are found, its
  dependence on the framework's command and the viewer's report rather than on
  their modules, the profile loader's one-level skill link, and its tests'
  place and opt-in browser tests.

### Modified Capabilities

- `framework-identity`: the `studio` extra pins the set's studio `~=`, and the
  reader is no longer told the extra cannot resolve (scenario titles kept);
  the studio is a product of the set and the third member of the npm
  workspace (one requirement added).
- `cli`: `machinome studio`, the third contributed command (one requirement
  added).
- `cli-startup-cost`: the studio's command loads none of the application to be
  listed (one requirement added).
- `vet`: a model that reaches `machinome.studio` is refused (one requirement
  added).
- `user-documentation`: the studio is documented in the manual (one
  requirement added).
- `framework-contributor-guidance`: how the studio's tests run (one
  requirement added).

`kernel-extras` is unchanged: it states the kernels' extras and names no
product's.

## Impact

- **Tree.** The join adds 738 files. The cycle adds the package's links,
  `MANIFEST.in`, `machinome/studio/cli.py` and `packaging.py`, the
  `machinome-simulate` links (one in `shop-skills/`, one per profile), ADR-193
  and the edits of design.md Decisions 3 to 16; it deletes the frontend's
  `package-lock.json` and `scripts/setup` is dropped at the join.
- **Code.** In the studio: the package root, `preparation.shop_resource_root`,
  `app.py`'s profile lookup, `mcp_server`'s command and test tool, the two
  backends' `PYTHONPATH` entry, `codex_auth`'s login line, `orchestrator`'s
  `run`, `profiles._skill_path`, docstrings. In the core: the manifest's
  `studio` extra, `machinome/vet/universe.toml`'s denylist.
- **Tests.** Joining: 42 Python test modules and their fixtures run from the
  studio's directory,
  rewritten from `floor` to `machinome.studio` and to the folded manual.
  Changed in the core's suite: `test_repository_layout.py`,
  `test_release_records.py`, `test_kernel_extras.py`, `test_docs_structure.py`,
  `test_vet_universe.py`, `test_core_names_no_split_words.py`,
  `test_machinome_identity.py`'s comment.
- **Build and CI.** Seventeen members build from `packages/` with the movie's;
  the studio's sdist builds its frontend with npm; `make test` runs the studio
  after its frontend's typecheck and build; CI's test job installs the OpenSpec
  CLI the studio's tests run.
- **Environment.** No new browser: the studio's Playwright is the viewer's
  `snapshot` extra's (1.63.0, Chromium 1243, present on this machine).

Originating evidence: the pilot's decisions of 12 October 2026, the product's
own record, the framework's `workflow/ongoing/release-0.8.0.md` (its
follow-ups for the studio), the probes of design.md, and the originating check
of design.md Decision 18: `machinome studio --projects-dir` a scratch
catalogue holding a copy of `Vibecoded-demos/gear-shift` from the bench's
venv, the hub photographed in Chromium, the project opened to its floor page
without an agent and photographed with the gearbox in the viewer, then
stopped.
