# Machinome 0.9: the monorepo, and the cut of the framework's packages

Campaign plan, provisional. Written 10 October 2026 from the workspace
conversation of that day, in which the pilot set the direction of 0.9 and
accepted the architecture below with every recommendation; the plan the
campaign's OpenSpec changes are cut from. Working record, not a promise:
nothing here is ratified, no ADR is accepted by it, and a baseline spec or
an accepted ADR outranks every sentence. Written from the framework at
Machinome 0.8.1 on `main` (58a1e74f, released state, tagged `v0.8.1`).

## What 0.9 is (pilot, 10 October 2026)

machinome becomes a monorepo of several packages, every one distributed
under the one licence the framework already carries, GPL-2.0-or-later OR
CERN-OHL-S-2.0+ at the recipient's choice. Everything joins the machinome
repository, which becomes that monorepo. The first step, and this
campaign, is the split of the framework's own modules into packages
inside it: the ten extension packages the lean-core campaign locked
(`lean-core.md`, "Every node type is a package" and "Locked at the
session's close", 4 October 2026) and the repository layout that holds
them. The joins of the viewer, the videomaker and the studio, and the 0.9
release itself, are later campaigns cut from this note's layout.

## The rule

Three statements carry the layout. The first two the 0.8 campaign locked;
the third the pilot set for 0.9.

- **The address is the location.** A node type is `machinome.node.<x>`,
  installed by `machinome[<x>]`, published as `machinome-node-<x>`, and
  kept in the repository at `packages/machinome-node-<x>/` with the
  address as the path inside it: `packages/machinome-node-step/machinome/node/step.py`.
  One thing, four spellings, nothing to look up. The engines follow the
  rule under `machinome.engine` (`machinome-engine-brep`,
  `machinome-engine-mesh`); anything else a package brings follows it
  under the root (`machinome.<name>`, `machinome[<name>]`,
  `machinome-<name>`).
- **A record lives with what it records.** The repository's record is at
  the root: the licence, the contributor guide, the AI-use statement, the
  CI, the scripts, the campaigns that span products. A product's record
  is in its directory: its manual, its specs, its ADRs, its working
  record, its tests. An extension package carries only what distinguishes
  it: its manifest, its source and a README. A repository that joins
  moves whole into its directory with its history (`git filter-repo
  --to-subdirectory-filter`), so nothing is renumbered or merged.
- **One licence, stated once.** The texts live at the root. Every package
  directory holds symlinks to them, and its manifest declares the
  expression and the files. Verified on 10 October 2026 with a throwaway
  namespace portion: setuptools carries a symlinked `LICENSE` and
  `LICENSES/` into the sdist and the wheel as real files, and the portion
  ships `machinome/node/<x>.py` with no `__init__.py` at either level.

## The layout

```
machinome/                            the repository machinome/machinome
├── README.md                         the monorepo: what is here, the packages, the licence
├── LICENSE, LICENSES/                the one licence, stated here only
├── CONTRIBUTING.rst, AI-USE.md       the repository's
├── HISTORY.rst                       the set's changelog, one Unreleased section at the top
├── pyproject.toml                    the uv workspace, members = packages/*, no distribution of its own
├── uv.lock
├── package.json                      the npm workspace, when the first JS package joins
├── context7.json                     one index per repository
├── .github/workflows/                lint, test, docs, dist over every package
├── scripts/                          check-dist for the set; the release pass
├── workflow/                         campaigns that span products; this note is its first
└── packages/
    ├── machinome/                    the core distribution and the framework's record
    │   ├── pyproject.toml            name machinome; extras naming the sibling packages
    │   ├── README.rst                the framework as a thing by itself, pinned as today
    │   ├── CREDITS.md                the framework's bundled material
    │   ├── LICENSE -> ../../LICENSE, LICENSES -> ../../LICENSES
    │   ├── HISTORY.rst, CONTRIBUTING.rst, AI-USE.md -> the root's (the sdist carries them)
    │   ├── machinome/                the import package: __init__, core/, node/ base, engine/ seams,
    │   │                             motion/, simulation/, production/, manager/, vet/, viewers/, ...
    │   ├── tests/                    the whole suite, run against the whole set installed
    │   ├── docs/                     the manual, architecture.md, adrs/, .readthedocs.yaml beside it
    │   ├── openspec/                 specs and changes of the framework and its extension packages
    │   ├── workflow/                 warts.md, ongoing/, archive/
    │   ├── tools/, spike/            the framework's evidence tools and spikes
    │   └── setup.cfg, tox.ini, Makefile, MANIFEST.in, requirements*.txt, .gitignore
    ├── machinome-node-step/          one extension package; every other has this shape
    │   ├── pyproject.toml
    │   ├── README.md
    │   ├── LICENSE -> ../../LICENSE, LICENSES -> ../../LICENSES
    │   └── machinome/node/step.py    the portion: no __init__.py at either level
    ├── machinome-node-cadquery/, -build123d/, -molejo/, -openscad/, -solid2/, -jscad/, -stl/
    ├── machinome-engine-brep/machinome/engine/brep.py
    ├── machinome-engine-mesh/machinome/engine/mesh.py
    ├── machinome-viewer/             joins later: its tree as it is today, history included
    ├── machinome-studio/             joins later
    └── machinome-movie/, videomaker/ join later, each a member of its ecosystem's workspace
```

What stays at the root is the repository's; everything else of today's
tree moves under `packages/machinome/` unchanged, the framework's
`.gitignore` included (its patterns are relative to the directory it sits
in, so they keep meaning there) and a new root `.gitignore` for `WTs/`,
`.venv/` and the workspace's own leavings. `.readthedocs.yaml` stays
beside the manual; Read the Docs reads a configuration path per project,
which is the pilot's setting at release. The repository's `.claude/`
prompts stay at the root as they are; the package standard records them
as a conformance gap and this campaign does not touch them.

## Decisions accepted by the pilot (10 October 2026)

1. **The record of an extension package is the framework's.** The eleven
   distributions are one product with one release; their specs already
   cite each other. An extension package carries its manifest, its
   source and a README; its specs, its tests and its manual pages stay in
   `packages/machinome/`. A test moves into an extension package's
   directory only when a finding wants that package tested alone.
2. **One version for the whole set.** Every package in the repository
   carries one version, one changelog section, one tag and one release
   pass. The pins between packages are `~=<version>` both ways, so a
   patch of one does not strand the others, and the contract numbers at
   the seams remain the real guard. The bumpversion table in `setup.cfg`
   and `tests/test_release_records.py` grow to cover every manifest and
   every pin. The studio and mechanics join that sequence when they join
   the repository. During this campaign the extension packages carry the
   line's version (0.8.1 at its start) and are published by nobody; the
   release change of 0.9 renumbers the set.
3. **A uv workspace at the root.** A lock file, one command to sync the
   set with every extra, a venv per bench instead of the `PYTHONPATH`
   trick. The build backend stays setuptools; publishing does not change.
   Every member is installed editable in compat mode (a `.pth` line per
   package root), as the workspace's setup script already does for the
   framework, so each portion's directory lands on `sys.path` where
   `machinome._namespace_portions` finds it; the lenient editable finder
   does not serve a namespace portion, since it answers only for the
   names it maps and never for a submodule under a sibling's `__path__`.
   Where uv takes that setting (`[tool.uv] config-settings` or the sync
   command's `--config-setting`) is proven in the first cycle that
   installs a portion, and recorded in its evidence; a bench that cannot
   be synced falls back to the workspace venv with `PYTHONPATH` listing
   every package directory, which the path extension serves equally.
4. **Today's tree moves in the first cycle.** The extension packages get
   their siblings at once, and each later join is a plain move.

Not decided by this plan and held for the pilot: which products join
beyond the viewer, the videomaker and the studio (the orchestrator's
reading: mechanics belongs, molejo stays its own product with its own
names on two indexes, machinome-freecad and machinome-skills are the
pilot's call); the viewer's and the studio's licences, AGPL-3.0-or-later
today, which change in their own repositories before or with their move;
the push of the line; the Read the Docs configuration path; the 0.9
release and its version bump.

## Facts the campaign stands on (10 October 2026)

- The core imports a node package in exactly one place: the OpenSCAD
  snapshot renderer, `machinome/viewers/openscad.py`, importing
  `machinome.node.openscad`, left in the core provisionally by ADR-179.
  The cut moves it into the openscad package and repoints the renderer
  row of `machinome/node/supported.py`. The two project templates under
  `manager/templates/` name node types as text, not imports.
- The import graph of the subpackages, measured on 58a1e74f: every node
  module imports the core's top-level modules, the node base and the
  engine seams; `step` imports `cadquery`; `solid2` imports `openscad`;
  `brep.py` and `mesh.py` import only the core. No core module but the
  renderer above imports a node module or an engine provider.
- The suite (593 files, 4768 passed, 4 skipped, 6734 subtests, 14 minutes
  on the line head on 10 October 2026) imports
  `machinome.node.solid2` in 94 files and `machinome.node.openscad` in
  43; `tests/base.py` writes SCAD through the openscad package. It never
  ran on a bare core and runs against the whole set installed.
- Tests that read files by a path relative to the repository root
  (`Path(__file__).resolve().parents[1]` and the like):
  `test_docs_structure.py`, `test_docs_exports.py` (which also reads
  `.github/workflows/python-app.yml` and `.readthedocs.yaml`),
  `test_kernel_extras.py`, `test_release_records.py`,
  `test_node_root_exports_nothing.py`, `test_viewer_documentation_links.py`,
  `test_vet_universe.py`, `test_verdict_store_cli.py`,
  `test_machinome_identity.py`, `test_export.py`, `mesh_engine_fixture.py`,
  and ten more with one reference each. After the move, `parents[1]` is
  `packages/machinome/`, which still holds everything they read but the
  CI workflow.
- `machinome._namespace_portions` (and the same call in `machinome.node`
  and `machinome.engine`) admits a sibling directory without an
  `__init__.py` from `sys.path` and refuses one with it; the
  `kernel-extras` spec's scenario "A provider portion resolves from
  another directory" exercises it with a temporary directory. No
  distribution has used it yet.
- The ten distribution names were free on PyPI on 10 October 2026:
  `machinome-engine-brep`, `machinome-engine-mesh`,
  `machinome-node-cadquery`, `machinome-node-build123d`,
  `machinome-node-step`, `machinome-node-molejo`,
  `machinome-node-openscad`, `machinome-node-solid2`,
  `machinome-node-jscad`, `machinome-node-stl`. Nothing is uploaded by
  this campaign.
- The tooling on the pilot's machine: uv 0.11.8, Python 3.12.3, pip 26.2,
  setuptools 84, build 1.6, twine 7, git-filter-repo, OpenSCAD 2021.01,
  the OpenSpec CLI 1.6.0.
- `tests/test_release_records.py` admits one `Unreleased` section above
  the released version's in `HISTORY.rst`; each cycle writes its entry
  there in the same cycle (the pilot's ruling of 29 September 2026).

## The campaign: the cut

**Line.** `v0.9-base`, worktree `machinome/WTs/v0.9-base`, cut from
`main` at 58a1e74f on 10 October 2026. Cycle benches:
`scripts/dev-env v0.9-base-<change> setup --base v0.9-base`.

**Orchestration**, as the lean-core campaign practised it: one opus
proposer and one opus applier per cycle, fresh agents with a written
briefing; agents never commit; the orchestrator's adversarial review is
the ratification gate before the planning commit and before the
implementation commit, which the orchestrator makes; the orchestrator
runs the suite itself at the cycle's head before fast-forwarding the
cycle into the line; one suite at a time on this filesystem; the line
merges into `main` at the campaign's close; pushing and uploading stay
the pilot's.

**The cycles, in order.** Each is a two-commit OpenSpec change in the
framework's `openspec/` (at the root until the first cycle lands, under
`packages/machinome/` after it), with its red tests, its evidence, its
HISTORY entry under `Unreleased`, its spec deltas and its ADR when a
decision is architectural.

1. `monorepo-layout`. Today's tree moves under `packages/machinome/`;
   the root becomes the repository's as drawn above: `README.md` (new,
   the monorepo's), `LICENSE` and `LICENSES/` (unchanged, the package
   directory symlinking them), `CONTRIBUTING.rst`, `AI-USE.md` and
   `HISTORY.rst` (moved, symlinked back for the sdist), `pyproject.toml`
   (the uv workspace with the one member), `uv.lock`, `context7.json`
   (its excluded folders prefixed), `.github/workflows/` (the jobs run
   from the package directory), `.editorconfig`, `.claude/`, a root
   `.gitignore`, `scripts/check-dist` (founded: builds every member,
   checks with twine, installs the archives into a throwaway venv outside
   the repository, imports and smokes, uploads nothing), and `workflow/`
   holding only this note and a README stating the convention, the
   framework's working record having moved with it. The gate, red first:
   a test pinning the layout, the symlinks resolving to the root files,
   the sdist and wheel carrying the licence texts, and the manifest of
   the workspace naming the member. The `framework-identity` spec gains
   the sentence that the framework lives at `packages/machinome` of the
   repository `machinome/machinome`; `framework-contributor-guidance` and
   `user-documentation` follow where they name a path. No version bump,
   no API change, no deprecation.
   **Done** (10 October 2026): branch `v0.9-base-monorepo-layout`, planning
   commit 257293d2 on 19c9f83b, ratified by the orchestrator's review (ADR-182).
   As applied it corrects the design's index of the repository root in the
   tests, `parents[3]` rather than `parents[2]`, recorded in design.md as a
   dated correction. The gate is green, the suite green on the bench's uv
   venv (4774 passed, 20 skipped, 6799 subtests, the 16 skips beyond the
   base's 4 being the viewer's tests the lock excludes), the manual built
   with warnings as errors from its requirements alone, and
   `scripts/check-dist` green: the sdist and the wheel built, `twine check
   --strict` passed, the five linked files in the sdist as regular files
   with the root's bytes, the wheel installed with `[openscad,stl]` into a
   throwaway venv, version 0.8.1, the licence expression and the three
   licence files, `machinome --help` exit 0, nothing uploaded. `uv lock`
   resolves 185 packages and `uv sync --python 3.12` installs 175. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-10-monorepo-layout/evidence.md`.
2. `cut-the-engines`. `machinome-engine-brep` and `machinome-engine-mesh`
   founded as the first portions; the core's `brep` and `mesh` extras
   repointed at them with `~=` pins; the root's sources mapping them to
   their directories; the editable mode proven on an installed set (the
   `kernel-extras` scenario on a real distribution, red first); the
   bumpversion table and the release-records test grown; `check-dist`
   building and smoking the three. Specs: `kernel-extras`,
   `brep-engine-dependency`, `mesh-engine-dependency`. ADR: an extension
   package is a namespace portion in its own distribution, resolved by
   the core's path extension and refused by its extra's name.
   **Done** (10 October 2026): branch `v0.9-base-cut-the-engines`, planning
   commit edf88424 on 6fb505ed, ratified by the orchestrator's review
   (ADR-183). The two engines are portions in `packages/machinome-engine-brep/`
   and `packages/machinome-engine-mesh/`, installed by the core's `brep` and
   `mesh` extras; the version is bumped from the root's `.bumpversion.cfg`;
   CI syncs the locked workspace with uv, and the requirements files, tox and
   the `dev` extra's tox are retired. The bench venv is the sweep's
   environment from this cycle, its default group carrying the mechanics
   package the catalogue imports. The suite green on the bench's uv venv
   (4786 passed, 20 skipped, 6831 subtests), the manual built with warnings
   as errors, and `scripts/check-dist` green: three members built, six
   archives `twine check --strict` passed, the engines installed through
   `machinome[brep]` and `machinome[mesh]` from the built archives and
   smoked through the seams (contracts 2 and 1, a 10 mm box's volume 1000
   and a 2 x 3 x 4 box's 24), nothing uploaded; a clean copy's framework
   sdist holds 1019 entries and its wheel 126, each engine's 18 and 8. `uv
   lock` resolves 179 packages. The universe sweep: 63 repositories, 130
   rows, 121 ok, 0 expected, 3 unexpected, 0 timeout, 6 no-model; the
   unexpected rows are wall_clock_41's own CadQuery error and Dum-E without
   machinome-freecad, as at `root-cleanup`, and fender-bender without
   `fb_library`, a dependency of that project alone which the bench venv does
   not carry. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-10-cut-the-engines/evidence.md`.
3. `cut-the-brep-nodes`. `cadquery`, `build123d`, `step` and `molejo` as
   four packages over the B-rep engine, `step` depending on `cadquery`;
   extras, pins, table, test, `check-dist` grown. Specs: `kernel-extras`,
   `step-import`, `step-assembly`, `markings` where they name an install.
   **Done** (10 October 2026): branch `v0.9-base-cut-the-brep-nodes`,
   planning commit bdadf767 on 84757c38, ratified by the orchestrator's
   review (ADR-184). The four node types are portions in
   `packages/machinome-node-cadquery/`, `-build123d/`, `-step/` and
   `-molejo/`, each stating its kernel and requiring the B-rep engine,
   `machinome-node-step` requiring `machinome-node-cadquery`, the first pin
   between two extension packages; the core's `cadquery`, `build123d`,
   `step` and `molejo` extras install them. A node type whose package is
   absent is refused by its extra at every door by the node root's last
   finder (ADR-184), and the manual's autodoc path names the siblings. The
   suite green on the bench's uv venv (4791 passed, 20 skipped, 6914
   subtests), the manual built with warnings as errors, and
   `scripts/check-dist` green: seven members built, fourteen archives `twine
   check --strict` passed, the node packages installed through their extras
   from the built archives and smoked by a part on each kernel (volumes
   1000, 24, 120 and 477.89 against the closed form 477.8895), nothing
   uploaded; a clean copy's framework sdist holds 1015 entries and its wheel
   122, each sibling's 18 and 8. `uv lock` resolves 183 packages. The
   universe sweep: 63 repositories, 130 rows, 121 ok, 0 expected, 3
   unexpected, 0 timeout, 6 no-model, every row as at `cut-the-engines`; the
   unexpected rows are wall_clock_41's own CadQuery error, Dum-E without
   machinome-freecad and fender-bender without `fb_library`. Evidence:
   `packages/machinome/openspec/changes/archive/2026-10-10-cut-the-brep-nodes/evidence.md`.
4. `cut-the-mesh-nodes`. `openscad` (the package directory, with the
   snapshot renderer moved in from the core's viewers and the supported
   table's row repointed), `solid2`, `jscad` and `stl`; the last core
   import of a node package gone, pinned by the kernel-free scan. Specs:
   `kernel-extras`, `openscad-node`, `openscad-dependency`, `stl-import`,
   `cli` where the snapshot renderer is named.

**Close** (the orchestrator): the suite and `check-dist` at the line's
head; the line merged into the local `main`; then, in the workspace
repository under its own process: `scripts/setup` and
`scripts/dev-env` on the new layout (the bench recipe becomes the uv
sync), `docs/collaborator-setup.md`, the workspace venv reinstalled from
`machinome/packages/*`, the operating contract's layout paragraph, and
the studio's `machinome-api` skill where it states an install line
(unchanged in spelling: `machinome[step]` still installs the step node).

## Empirical validation, per cycle

- The framework's suite from `packages/machinome/`, one process, on the
  bench's synced venv (or the fallback recipe above), count recorded.
- `scripts/check-dist`: every member built, checked, installed from the
  archives into a throwaway venv outside the repository, imported and
  smoked there; from cycle 2 on, the smoke imports each portion through
  the core and runs one tiny model that needs it.
- The manual built with warnings as errors from `docs/requirements.txt`.
- From cycle 2 on, the workspace's `scripts/load-projects` universe sweep
  against the bench, read against the previous cycle's counts (121 ok,
  2 unexpected pre-existing, 6 no-model at 0.8.1's root cleanup).

## What this campaign does not do

It joins no repository, bumps no version, uploads nothing, pushes
nothing, touches no project repository, and changes no public name: every
import a project writes today resolves after the cut to the same module,
and every install line (`machinome[<x>]`) installs what it installed,
now from a sibling distribution. The viewer seam deferred by the 0.8
campaign (`lean-core.md`, "The last cycle of the phase") stays deferred.
