## Why

The pilot's plan for Machinome 0.9 (`workflow/ongoing/monorepo-0.9.md` at the
repository root, accepted on 10 October 2026) cuts the framework's modules
into the ten extension packages the lean-core campaign locked, and names this
change its second cycle: the first two extension packages, and the first real
namespace portions. The core's engine seams were written for this cut
(`machinome.engine` resolves each provider by name and admits a portion
through `machinome._namespace_portions`), and the `kernel-extras` scenario
"A provider portion resolves from another directory" exercises the path
extension with a temporary directory, but no distribution has ever shipped a
portion. Until one does, the plan's decision 3 (every member editable in
compat mode, so a portion's directory is on `sys.path`) and decision 2 (one
version for the set, `~=` pins both ways) are untested on a real install,
and the eight node packages of the two later cycles would be the first to
meet whatever this one would have found.

## What Changes

- **Two distributions founded under `packages/`**:
  `packages/machinome-engine-brep/` ships `machinome/engine/brep.py` and
  `packages/machinome-engine-mesh/` ships `machinome/engine/mesh.py`, each
  moved from `packages/machinome/machinome/engine/` by `git mv`, unchanged.
  Each directory holds `pyproject.toml`, `README.md`, the relative links
  `LICENSE -> ../../LICENSE` and `LICENSES -> ../../LICENSES`, and the
  portion, with no `__init__.py` under its `machinome/` or
  `machinome/engine/` (design.md, Decisions 1 and 2).
- **The core's `brep` and `mesh` extras install the sibling distributions**,
  `machinome-engine-brep~=0.8.1` and `machinome-engine-mesh~=0.8.1`; each
  engine requires `machinome~=0.8.1` and its kernel, the OCCT range and its
  reason stated once, in the B-rep engine's manifest. Every other extra, the
  `all` extra and every install line keep their names and their meaning:
  `pip install "machinome[brep]"` still installs the B-rep engine and
  `from machinome.engine import brep` still resolves it (Decision 3).
- **The seams do not change.** `BREP_PROVIDER`, `brep_engine`,
  `require_brep_engine` and the mesh trio resolve the portion as they
  resolved the module; the probes in design.md show it resolved from the
  workspace's editable install and from the installed wheels, and refused
  naming `machinome[brep]` or `machinome[mesh]` when the distribution is
  absent. No public name, address, extra name, contract number or document
  changes.
- **The workspace**: the root manifest names both distributions as sources;
  `uv.lock` is regenerated (187 packages, two more than the first cycle's);
  the root `.gitignore` ignores the build's scratch in package directories
  that keep no `.gitignore` of their own (Decision 4).
- **One version for the set, bumped from the root**: a root
  `.bumpversion.cfg` lists every manifest's version and every `~=` pin
  between the set's packages, replacing the `[bumpversion]` tables of the
  core's `setup.cfg`, which keeps its lint configuration only (Decision 5).
- **CI on uv**: the `lint`, `test` and `browser-snapshot` jobs install the
  set with `astral-sh/setup-uv` and `uv sync --locked` at the root, so a
  stale lock fails CI; the lint covers the engine packages' modules. Since
  the suite can no longer be installed from the requirements files once
  the engines are siblings, this is the change the first cycle's open
  question 3 deferred their retirement to: `requirements.txt`,
  `requirements_dev.txt` and `tox.ini` are removed with the Makefile's
  `test-all` target (Decision 6). **BREAKING** for a contributor who ran
  `tox` or installed from the requirements files; nothing a project uses.
- **`scripts/check-dist`** builds and checks the three members, installs
  the engines into the throwaway environment through the core's extras
  from the built archives, and smokes each through the core: the provider
  resolved by the seam, its file owned by its distribution, one operation
  on its kernel, its version equal to the core's, its licence texts. The
  core's row is unchanged (Decision 7).
- **The lint configuration stays in the core's `setup.cfg`**, its
  per-file ignores for the moved modules naming them by their new paths
  relative to that file (Decision 8).
- **The gate, red first** (Decision 9): the layout test's new group pins
  each engine directory, its contents, its links, its manifest's name,
  version and pin, the module resolving from it, the core's
  `machinome/engine/` holding only `__init__.py`, and the workspace's
  sources and lock; `test_kernel_extras.py` reads the sibling
  distributions and the lock in place of the requirements files and tox;
  the kernel-free census and the split-words gate read the engine
  packages beside the core; `test_release_records.py` holds every
  member's version and every pin to the core's; the installation page
  names the two distributions.
- **Records**: `HISTORY.rst` and the manual's changelog gain their
  `Unreleased` entries; `docs/start/install.rst` names the distribution
  each engine extra installs; `docs/architecture.md`'s Map and the ADR
  index's OCCT heading point at the new directories; `CONTRIBUTING.rst`
  states the install without uv for the set and drops `make test-all`;
  ADR-183 (BUILD) records the shape of an extension package
  (Decision 10).

Not in this change: the node packages (cycles `cut-the-brep-nodes` and
`cut-the-mesh-nodes`), any version bump, any upload or push, the release
job's building of the engine distributions (Open Questions 2), and the
workspace's `scripts/setup` and `scripts/dev-env` (the campaign's close).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `kernel-extras`: the `brep` and `mesh` extras install the distributions
  `machinome-engine-brep` and `machinome-engine-mesh`, which state the
  kernel ranges; the CI installs every kernel through the workspace's lock,
  not requirements files and tox; the core's scan finds no kernel in the
  engines' modules, which live in their own distributions and import only
  their kernels; each engine provider is a namespace portion shipped by its
  own distribution and resolved from it.
- `brep-engine-dependency`: the `brep` extra installs the engine's
  distribution, and an absent distribution is an absent engine, refused as
  before; the core's scan for OCP reads the core alone.
- `mesh-engine-dependency`: the same for the `mesh` extra and
  `machinome-engine-mesh`; the core's scan for `manifold3d` reads the core
  alone.
- `framework-identity`: the framework's extension packages live beside it
  under `packages/`, each carrying only its manifest, a README, the licence
  links and its portion, numbered with the set and pinned `~=` both ways;
  the version is bumped from the root; CI syncs the locked workspace;
  `scripts/check-dist` smokes each extension package through the core.
- `framework-contributor-guidance`: the install without uv names every
  member under `packages/`, editable in compat mode.

## Impact

- **Tree.** Two files move (`machinome/engine/brep.py` and `mesh.py` of
  `packages/machinome/` into their distributions); new: two package
  directories (manifest, README, two links each) and the root
  `.bumpversion.cfg`; removed: `packages/machinome/requirements.txt`,
  `requirements_dev.txt` and `tox.ini`.
- **Code.** None beyond the move: the seams and the two modules are
  unchanged, and `machinome/__init__.py`'s docstring sentence saying no
  such distribution exists is corrected (Decision 3).
- **Tests.** Changed: `test_repository_layout.py`, `test_kernel_extras.py`,
  `test_core_kernel_free.py`, `test_core_names_no_split_words.py`,
  `test_release_records.py`, `test_brep_engine.py`, `test_mesh_engine.py`,
  `test_docs_structure.py`; a probe of the whole suite on the moved tree
  names every test the move alone turns red (design.md, Context, probe 5).
- **Build and CI.** Three distributions build from `packages/`; CI installs
  with uv from the lock; `check-dist` gains two rows. The tag-triggered
  `build` job still builds the core alone.
- **Developers.** The bench venv (`uv sync --python 3.12` at the root) is
  the recipe for the suite. The fallback recipe (the workspace venv with
  `PYTHONPATH`) no longer runs the whole suite: fourteen test modules start
  subprocesses with `PYTHONPATH` set to the core's directory alone, which
  drops the engines (design.md, Risks).
- **Records.** ADR-183 (BUILD); five delta specs; `HISTORY.rst`; the
  manual's changelog and installation page.

Originating evidence: the campaign plan (`workflow/ongoing/monorepo-0.9.md`,
"The rule", "Decisions accepted by the pilot" 1 to 3, "The campaign: the
cut", cycle 2), the first cycle's open questions 2 and 3
(`openspec/changes/archive/2026-10-10-monorepo-layout/design.md`), the
workspace's package standard (`docs/software-package-standard.md` of the
workspace, sections 1.1, 1.2 and 1.5), and the probes recorded in
design.md.
