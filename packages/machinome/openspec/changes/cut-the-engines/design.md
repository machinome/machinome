## Context

The second cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`
at the repository root, "The campaign: the cut", cycle 2), cut from the line
`v0.9-base` at 6fb505ed, whose head holds the first cycle, `monorepo-layout`
(ADR-182), integrated, on the bench `machinome/WTs/v0.9-base-cut-the-engines`.
The plan's decisions accepted by the pilot on 10 October 2026 bind it: the
record of an extension package is the framework's, so an extension package
carries its manifest, its source and a README (1); one version for the whole
set, `~=` pins both ways, the contract numbers at the seams the real guard
(2); a uv workspace at the root, every member editable in compat mode (3).
The workspace's package standard (`docs/software-package-standard.md` of the
workspace) is read per product, as the first cycle read it: its sections 1.1
and 1.2 are written for a repository that is a product, and Decision 1 says
which of their items an extension package carries.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench
at 6fb505ed unless marked *inferred*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C2-propose/`
(named `<scratch>` below), never in the bench, with uv 0.11.8, CPython
3.12.3, setuptools from the build isolation, pip 26, build 1.6, twine 7,
flake8 7.4.1, bump2version and the OpenSpec CLI 1.6.0.

### What the cut touches

- `machinome/engine/__init__.py` names the providers by string
  (`BREP_PROVIDER = 'machinome.engine.brep'`, `MESH_PROVIDER`), imports
  neither, reads an `ExtraUnavailable` naming its extra or a
  `ModuleNotFoundError` naming the provider as absence, and ends with
  `__path__ = _namespace_portions(__path__, __name__)`.
  `machinome._namespace_portions` appends every directory `pkgutil.extend_path`
  finds on `sys.path` that holds no `__init__.py`. Its docstring says
  "Nothing uses the extension yet; no such distribution exists", which this
  change makes false.
- `brep.py` and `mesh.py` import from the framework only `machinome.extras`
  (both) and `machinome.engine` (brep, for two error types), call
  `require_extra('brep', ...)` and `require_extra('mesh', ...)` before their
  kernels, and declare `CONTRACT = 2` and `CONTRACT = 1`. No core module
  imports either (the `brep-engine-dependency` and `mesh-engine-dependency`
  scans, `tests/test_core_kernel_free.py`).
- `pyproject.toml` (the core's): `brep = ["cadquery-ocp>=7.8.1,<7.9"]` with
  a comment saying the cut repoints it, `mesh = ["manifold3d"]`, the four
  B-rep node extras each naming `machinome[brep]`, `all` naming every extra.
- `setup.cfg`: four `[bumpversion:file:...]` tables (the manifest's
  `version`, `machinome/__init__.py`, `docs/conf.py`'s `release`,
  `machinome/vet/universe.toml`) and `[flake8]` with per-file E402 ignores
  naming `machinome/engine/brep.py` and `mesh.py`.
- `requirements.txt` mirrors the kernel requirements, `requirements_dev.txt`
  the tools, `tox.ini` installs `extras = all` into an isolated environment;
  the CI's `lint`, `test`, `browser-snapshot` and `build` jobs run
  `pip install -r requirements.txt -r requirements_dev.txt` and never install
  the framework itself: pytest's rootdir puts `packages/machinome/` on
  `sys.path`. `test_kernel_extras.py` pins `requirements.txt` against its own
  `EXTRAS` table and `tox.ini`'s `extras = all`.
- Tests that read the providers by path: `test_brep_engine.py` and
  `test_mesh_engine.py` (`ENGINE_SOURCE`), `test_core_kernel_free.py`
  (`PROVIDERS`, `EXTRA_OF`, the census, `MESH_PROVIDER`),
  `test_core_names_no_split_words.py` (`ZONES`, and `scan()` over
  `machinome/` of the core).
- Eighteen test modules name `PYTHONPATH` (`grep -rln PYTHONPATH tests`);
  fourteen of them start subprocesses with `PYTHONPATH` replaced by one
  directory, the core's or a project's (`import_probe.py`,
  `test_brep_engine.py`, `test_mesh_engine.py`, `test_meta.py`,
  `test_build_lock.py`, `test_export.py` among them).
- The manual names `machinome[brep]` and `machinome[mesh]` on
  `start/install.rst` (the extras table, and "The framework is one package,
  ``machinome``" under "Two packages, two licences"), `reference/api.rst`
  (installed by the extra: stays true), `howto/fast-tests.rst` and
  `project/upgrading.rst` (the extras by name: stay true);
  `howto/backends.rst` names neither engine extra (`grep` for
  `machinome\[brep\]`, `machinome\[mesh\]`, `cadquery-ocp`, `manifold3d`
  under `docs/*.rst`).

### Probes

1. **The portion on a real sync** (`<scratch>/repo/`: `git ls-files` of the
   bench copied with its links, made a git repository; the two directories
   founded as Decision 1 states, the two `git mv`, the manifests of
   Decision 2 with placeholder READMEs, the core's extras of Decision 3, the
   root sources of Decision 4). `env -C <scratch>/repo uv lock`: "Resolved
   187 packages", "Added machinome-engine-brep v0.8.1", "Added
   machinome-engine-mesh v0.8.1"; the lock records
   `source = { editable = "packages/machinome-engine-brep" }` and `-mesh`.
   `uv sync --python 3.12`: "Installed 177 packages". Three `.pth` files,
   each one line: `__editable__.machinome-0.8.1.pth` holds
   `<scratch>/repo/packages/machinome`,
   `__editable__.machinome_engine_brep-0.8.1.pth` holds
   `<scratch>/repo/packages/machinome-engine-brep`, and the mesh one its
   directory. With the venv's Python, from `/tmp`:
   `machinome.engine.__path__` is the core's `machinome/engine`, then
   `packages/machinome-engine-brep/machinome/engine`, then the mesh one;
   `brep_engine()` returns the module whose `__file__` is
   `packages/machinome-engine-brep/machinome/engine/brep.py`, `CONTRACT` 2
   equal to `BREP_CONTRACT`; `mesh_engine()` likewise, 1 and 1;
   `from machinome.engine import brep` is the same module; `solid_volume`
   of a 10 mm OCCT box is 999.9999999999998 and `volume(centred_box([2, 3,
   4]))` is 24.0. The core's `packages/machinome/machinome/engine/` holds
   `__init__.py` alone (and `__pycache__`). The seams needed no change.
2. **The distribution absent** (same venv). `uv pip uninstall
   machinome-engine-brep`: its `.pth` goes, `__path__` has two entries,
   `brep_engine()` is `None`, `require_brep_engine('B-rep fusion Bracket',
   'fusing its B-rep children')` raises `BrepEngineUnavailable: B-rep fusion
   Bracket requires the B-rep engine because fusing its B-rep children;
   install it with 'pip install "machinome[brep]"'. A model with no B-rep
   node never needs it`, and `import machinome.engine.brep` raises
   `ModuleNotFoundError` with `name` `machinome.engine.brep`; the mesh engine
   still resolves. The same for `machinome-engine-mesh`: `mesh_engine()` is
   `None` and `require_mesh_engine` raises `MeshEngineUnavailable` naming
   `pip install "machinome[mesh]"`. `uv sync` reinstalls both ("Installed 2
   packages"). `git status` then shows `packages/machinome-*/
   machinome_engine_*.egg-info/` untracked and not ignored: the editable
   build writes it in the member's directory, and the root `.gitignore`
   ignores no `*.egg-info` (Decision 4).
3. **The archives.** `python -m build packages/<member> --outdir
   <scratch>/dist/<member>` for the three, with the workspace venv: exit 0
   each. `machinome_engine_brep-0.8.1.tar.gz` holds 18 entries: `LICENSE`
   (793 bytes) and `LICENSES/CERN-OHL-S-2.0.txt` (13419) and
   `GPL-2.0-or-later.txt` (17984) as regular files, `PKG-INFO`,
   `README.md`, `pyproject.toml`, `setup.cfg` (setuptools' `egg_info`
   stamp), the egg-info and `machinome/engine/brep.py` (34749 bytes), with
   no `__init__.py`. `machinome_engine_brep-0.8.1-py3-none-any.whl` holds 8
   entries: `machinome/engine/brep.py`, the three licence files under
   `dist-info/licenses/`, `METADATA`, `WHEEL`, `top_level.txt`, `RECORD`.
   The mesh archives are the same shape (18 and 8, `mesh.py` 4140 bytes).
   The core's sdist holds 1019 entries and its wheel 126, the first cycle's
   1021 and 128 less the two modules; neither holds `machinome/engine/brep.py`
   or `mesh.py`, and both hold `machinome/engine/__init__.py`. `twine check
   --strict` on the six archives: 6 PASSED. The sdists are named with an
   underscore (`machinome_engine_brep-0.8.1.tar.gz`); `check-dist` reads
   the top directory from the archive, so it needs no change for that.
4. **The wheels installed.** A fresh `python3.12 -m venv`, then
   `pip install --find-links <dist>/machinome --find-links
   <dist>/machinome-engine-brep --find-links <dist>/machinome-engine-mesh
   "<dist>/machinome/machinome-0.8.1-py3-none-any.whl[openscad,stl]"
   "machinome[brep]" "machinome[mesh]"`: exit 0; installed `machinome`,
   `machinome-engine-brep` and `-mesh` 0.8.1, `cadquery-ocp`
   7.8.1.1.post1, `manifold3d` 3.5.4, `solidpython2` 2.1.3. The extras
   reached the engines in the built archives, which no index serves. With
   `python -I` from the venv's directory: one `site-packages/machinome/engine/`
   holds `__init__.py`, `brep.py` and `mesh.py`; `__path__` has that one
   entry; both seams resolve with their contracts; the B-rep and mesh
   operations of probe 1 give the same numbers;
   `importlib.metadata.distribution('machinome-engine-brep').files` lists
   `machinome/engine/brep.py` and the three licence files and no
   `__init__.py`; `License-Expression` is `GPL-2.0-or-later OR
   CERN-OHL-S-2.0+` for both engines; `requires('machinome-engine-brep')` is
   `['machinome~=0.8.1', 'cadquery-ocp<7.9,>=7.8.1', 'numpy']` and the core's
   extras require `machinome-engine-brep~=0.8.1; extra == "brep"` and the
   mesh one.
5. **The whole suite on the cut tree** (probe 1's venv, `pytest -q -rs -p
   no:cacheprovider` from `packages/machinome/` with the venv's `bin/` first
   on `PATH`; 4794 collected, the first cycle's 4774 passed and 20 skipped):
   `9 failed, 4771 passed, 20 skipped, 6797 subtests passed in 503.29s`.
   The 20 skips are the first cycle's 20 (16 the viewer, which the lock
   excludes; networkx; the `jscad` command; 2 vendor STEP). The nine
   failures, six test methods, every one a path or a table this change
   moves:
   - `test_brep_engine.py::ContractDeclarationTest::test_the_contract_is_an_integer_literal_of_two`
     and `test_mesh_engine.py::ContractDeclarationTest::test_the_contract_is_an_integer_literal_of_one`:
     `FileNotFoundError` on `packages/machinome/machinome/engine/brep.py`
     and `mesh.py` (`ENGINE_SOURCE`);
   - `test_core_kernel_free.py::KernelsOnlyInTheirModulesTest::test_each_kernel_module_checks_its_kernel_first`,
     two subtests: `KeyError: 'machinome/engine/brep.py'` and `mesh.py`;
   - `test_core_kernel_free.py::KernelsOnlyInTheirModulesTest::test_kernels_are_imported_only_by_their_modules`:
     the expected census lists the two engine modules, which the core no
     longer holds;
   - `test_kernel_extras.py::KernelMetadataTest::test_each_extra_lists_what_its_module_needs`,
     subtests `brep` and `mesh`: the table expects `cadquery-ocp>=7.8.1,<7.9`
     and `manifold3d`;
   - `test_repository_layout.py::TheRootIsTheRepositorysTest::test_the_readme_links_every_package_and_states_the_licence`,
     subtests `machinome-engine-brep` and `-mesh`: the root README links no
     new directory.

   Green on the cut tree, and so blind to it: `test_core_names_no_split_words.py`
   (its `scan()` reads the core's `machinome/` alone, so the engines' modules
   leave the gate), `test_kernel_extras.py::test_ci_installs_every_concrete_requirement_of_all`
   (it compares `requirements.txt` with its own table, not with the
   manifests), `test_release_records.py` (it reads no member but the core),
   and the layout gate's G4 (it pins `machinome`'s source and lock entry
   and says nothing of a second member).
6. **Where the lint configuration lives** (`<scratch>/lint/`, a copy of the
   three packages' modules and the core's `setup.cfg` and `tox.ini`).
   `flake8 --max-line-length=89 ../machinome-engine-brep/machinome
   ../machinome-engine-mesh/machinome` from the core's directory, the base's
   `setup.cfg`: 24 E402 in `brep.py` and 2 in `mesh.py` (its per-file
   ignores name the old paths). A root `.flake8` with the whole section and
   the core's `setup.cfg` without it: from the root, 0 E402; from
   `packages/machinome/`, 65 E402, every ignore lost (flake8 7.4.1 reads no
   configuration above the working directory). The core's `setup.cfg`
   keeping its section with the two entries spelled
   `../machinome-engine-brep/machinome/engine/brep.py:E402` and the mesh one:
   from `packages/machinome/`, 0 E402 over the three packages (flake8 reads
   a per-file-ignores path relative to the file that states it). On the cut
   tree, `flake8 --max-line-length=89 machinome tests` from the core's
   directory: 759 lines, the first cycle's 759; with
   `../machinome-*/machinome` added under the corrected `setup.cfg`:
   759. `black --check` over the same: 521 files would be reformatted, as
   the CI's `continue-on-error` step already reports for the core.
7. **The version bumped from the root** (`<scratch>/bump/`, the five
   version-carrying files of the three packages and a root `.bumpversion.cfg`
   as Decision 5 states, a git repository). `bump2version --new-version
   0.9.0 patch` with `commit` and `tag` off: `current_version`, the three
   manifests' `version`, both engines' `"machinome~=0.8.1"`, the core's two
   `~=0.8.1"` pins, `__version__`, `release` and the universe's `version`
   all read 0.9.0, and nothing else changed (`git diff -U0`). Two tables on
   one file are spelled `[bumpversion:file(label):path]`, which the
   installed bump2version accepts. The core's viewer floors
   (`machinome-viewer>=0.8.1`) are not touched, because the pin table's
   search is `~={current_version}"`.
8. **The install without uv** (`<scratch>/pipcopy/`: the three packages'
   build inputs, a fresh `python3.12 -m venv`). From the copy's root,
   `pip install -e packages/machinome-engine-brep -e
   packages/machinome-engine-mesh -e "packages/machinome[dev]"
   --config-settings editable_mode=compat`: exit 0, three `__editable__`
   `.pth` files each holding its package directory, both seams resolving to
   the packages' files. One `--config-settings` serves the three builds.
9. **The CI action** (its documentation, through Context7, 10 October
   2026): `astral-sh/setup-uv` is at v10.1.0, takes `version`,
   `enable-cache` and `cache-dependency-glob`, and installs uv only; the
   environment is made by a later `uv sync` step.

## Goals / Non-Goals

**Goals:**

- `machinome-engine-brep` and `machinome-engine-mesh` founded as the first
  extension packages, each a namespace portion in its own distribution,
  installed by the core's extra of the same last name.
- The plan's decisions 2 and 3 proved on a real install: the workspace sync,
  the archives, and the installed wheels, each resolving the engines through
  the unchanged seams.
- One version for the set, bumped from one place, pinned `~=` both ways, and
  held together by a test.
- CI that installs the set as the developers do, from the lock.
- Gates that fail if an engine drifts back into the core, a pin or a version
  drifts, or a member escapes a scan.

**Non-Goals:**

- The node packages (`cut-the-brep-nodes`, `cut-the-mesh-nodes`), and any
  table, helper or rule shaped for them beyond what the two engines use.
- Any change to the seams' code, a public name, an address, an extra's name,
  a contract number, the document format or the viewer API.
- A version bump, an upload, a push, a Read the Docs setting.
- The release job building the engine distributions (Open Questions 2), the
  workflow's rename (the first cycle's open question 4), the viewer's
  exclusion from the lock (its open question 5), and the workspace's
  `scripts/setup`, `scripts/dev-env` and collaborator guide (the campaign's
  close).

## Decisions

### 1. The shape of an extension package

```
packages/machinome-engine-brep/
├── pyproject.toml
├── README.md
├── LICENSE  -> ../../LICENSE
├── LICENSES -> ../../LICENSES
└── machinome/
    └── engine/
        └── brep.py          moved by git mv, unchanged
```

and `packages/machinome-engine-mesh/` the same with `mesh.py`. No
`__init__.py` under `machinome/` or `machinome/engine/`: the core's
`__init__.py` files are the package, and a portion's own would make it
"another copy of the core", which `_namespace_portions` refuses (probe 1
shows the portion admitted without them).

Which items of the package standard an extension package carries, read per
product under the plan's decision 1:

| Standard item | Extension package | Why |
|---|---|---|
| 1.1 `README.md` | carried, short (below) | the distribution's long description on an index, and the directory's landing page |
| 1.1 `LICENSE`, the notice | the root's, by the two links | "One licence, stated once"; probe 3 shows the archives carry them as files |
| 1.1 `CREDITS.md` | not carried | the engines bundle no third-party material; their kernels are declared dependencies |
| 1.1 `AI-USE.md`, `CHANGELOG.md` | not carried | the repository's `AI-USE.md` and `HISTORY.rst` cover the set; one changelog section per release (decision 2) |
| 1.2 `pyproject.toml` | carried (Decision 2) | name, the set's version, licence, `requires-python`, dependencies with their comments, URLs |
| 1.2 compatibility declaration | the module's `CONTRACT`, unchanged | the seam checks it at resolve time and refuses a mismatch naming both versions (`BrepEngineIncompatible`, `MeshEngineIncompatible`) |
| 1.2 `MANIFEST.in` | not carried | the portion ships no non-Python file; setuptools carries the README, the manifest and the `license-files` without one (probe 3) |
| 1.2 `.gitignore`, `.editorconfig` | not carried | the root's serve (Decision 4) |
| 1.3, 1.4, 1.5 | the framework's | specs, ADRs, architecture, manual, tests, CI and `check-dist` stay in `packages/machinome/` and at the root (decision 1) |

### 2. The two manifests and the two READMEs, verbatim

`packages/machinome-engine-brep/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-engine-brep"
version = "0.8.1"
description = "The B-rep engine of Machinome, on the OCCT kernel"
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
    "Natural Language :: English",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
keywords = ["machinome"]
dependencies = [
    # The core this engine is a portion of, released with it: the set
    # carries one version, and the pins between its packages are ~= both
    # ways. The contract number at the seam (machinome.engine.BREP_CONTRACT
    # against this module's CONTRACT) is the real guard.
    "machinome~=0.8.1",
    # The OCCT binding, in the range the pinned cadquery 2.7 requires. Every
    # node type over OCCT installs this engine through the core's brep
    # extra, so the range is stated here once and several extras resolve
    # one OCCT binding.
    "cadquery-ocp>=7.8.1,<7.9",
    # Arrays; the core pins the range.
    "numpy",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The portion, machinome/engine/brep.py, with no __init__.py at either
# level, so the core's package path admits it.
include = ["machinome.engine"]
namespaces = true
```

`packages/machinome-engine-mesh/pyproject.toml`: the same but `name =
"machinome-engine-mesh"`, `description = "The mesh engine of Machinome, on
manifold3d"`, the first comment naming `machinome.engine.MESH_CONTRACT`, the
kernel line and its comment

```toml
    # Unranged, as it was when the core required it.
    "manifold3d",
```

in place of the OCCT pair, and the last comment naming
`machinome/engine/mesh.py`. `numpy` is declared because each module imports
it directly; unranged, since the core's `numpy==2.2.*` is the one range.
`include = ["machinome.engine"]` with `namespaces = true` is the spelling
probe 3 shows ships the portion and nothing else; `machinome` itself is not
included, so no `machinome/__init__.py` can be shipped by accident.

`packages/machinome-engine-brep/README.md`:

```markdown
# machinome-engine-brep

The B-rep engine of [Machinome](https://github.com/machinome/machinome): the
module `machinome.engine.brep`, which reads, places, fuses, intersects,
measures and writes boundary-representation shapes on the OCCT kernel,
through its Python binding OCP. The framework resolves it when a part has
B-rep geometry.

## Install

    pip install "machinome[brep]"

The extras of the node types built on OCCT (`cadquery`, `build123d`, `step`
and `molejo`) install it too.

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

`packages/machinome-engine-mesh/README.md`:

```markdown
# machinome-engine-mesh

The mesh engine of [Machinome](https://github.com/machinome/machinome): the
module `machinome.engine.mesh`, which builds solids from triangle meshes and
places, intersects, unites and measures them on manifold3d. The framework
resolves it when it compares or fuses parts on their meshes.

## Install

    pip install "machinome[mesh]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

Each shows the package and adds nothing: no version, no history, no account
of the cut. The licence sentence is `docs/conf.py`'s `framework_licence`
with its two choices; the gate checks it (Decision 9). The licence files are
named, not linked, because a relative link does not resolve on an index's
page.

### 3. The core's manifest; the seams unchanged

In `packages/machinome/pyproject.toml` the two extras and their comments
become:

```toml
# The B-rep engine (`machinome.engine.brep`, resolved by its seam in
# `machinome.engine`) is the distribution machinome-engine-brep, which
# states the OCCT range.
brep = [
    "machinome-engine-brep~=0.8.1",
]
# The mesh engine (`machinome.engine.mesh`, resolved by its seam in
# `machinome.engine`) is the distribution machinome-engine-mesh, over
# manifold3d, for every comparison on meshes: a part without B-rep
# geometry, `machinome test --mesh`, `assertAssemblySupported` and a fusion
# of such parts. No node extra includes it: a B-rep project needs it only
# for a mesh question, which it may never ask.
mesh = [
    "machinome-engine-mesh~=0.8.1",
]
```

The comment above the kernel extras changes "so the OCCT range is stated
once" to "so the OCCT range, stated once in machinome-engine-brep, resolves
one OCCT binding for several extras". The comment in `dependencies` naming
"the OCCT binding (the extra `brep`), manifold3d (the extra `mesh`)" becomes
"the B-rep engine (the extra `brep`), the mesh engine (the extra `mesh`)".
`cadquery`, `build123d`, `step` and `molejo` keep `machinome[brep]`; `all`
and `dev` are unchanged and now reach the two distributions through `brep`
and `mesh`.

The seams in `machinome/engine/__init__.py` do not change (probes 1, 2 and
4). The one edit to a module is the docstring of
`machinome._namespace_portions`: "Nothing uses the extension yet; no such
distribution exists (OpenSpec change `lean-install`)." becomes "The engines'
distributions, `machinome-engine-brep` and `machinome-engine-mesh`, are the
first such portions (OpenSpec change `cut-the-engines`)." Its code is
unchanged.

### 4. The workspace: sources, lock, ignores

The root `pyproject.toml`'s sources become:

```toml
[tool.uv.sources]
machinome = { workspace = true }
machinome-engine-brep = { workspace = true }
machinome-engine-mesh = { workspace = true }
```

and nothing else in it changes. `uv lock` regenerates `uv.lock` (probe 1:
187 packages); `uv sync --python 3.12` installs 177 with three `.pth` lines.

The root `.gitignore` (probe 2) becomes:

```
# The repository's leavings. The framework keeps its own .gitignore beside
# its sources; these are the root's, and the build's scratch of the
# packages that keep none.
/WTs/
/.venv/
/.env
/dist/
/packages/*/build/
/packages/*/*.egg-info/
__pycache__/
*.py[cod]
```

Anchored to `packages/*/` so they say exactly where the scratch lands.

### 5. One version for the set: a root `.bumpversion.cfg`

The core's `setup.cfg` loses its `[bumpversion]` tables and keeps `[flake8]`
only. A root `.bumpversion.cfg`, exactly:

```ini
# One version for every package of the repository (the 0.9 plan's decision
# 2): each manifest's version, the files that restate the framework's, and
# every ~= pin between the packages. Run bump2version from this directory.
[bumpversion]
current_version = 0.8.1
commit = True
tag = True

[bumpversion:file(version):packages/machinome/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pins):packages/machinome/pyproject.toml]
search = ~={current_version}"
replace = ~={new_version}"

[bumpversion:file:packages/machinome/machinome/__init__.py]
search = __version__ = "{current_version}"
replace = __version__ = "{new_version}"

[bumpversion:file:packages/machinome/docs/conf.py]
search = release = '{current_version}'
replace = release = '{new_version}'

[bumpversion:file:packages/machinome/machinome/vet/universe.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(version):packages/machinome-engine-brep/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pin):packages/machinome-engine-brep/pyproject.toml]
search = "machinome~={current_version}"
replace = "machinome~={new_version}"

[bumpversion:file(version):packages/machinome-engine-mesh/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pin):packages/machinome-engine-mesh/pyproject.toml]
search = "machinome~={current_version}"
replace = "machinome~={new_version}"
```

Probe 7 ran it (with `commit` and `tag` off) and moved exactly these
statements. The alternative, keeping the table in the core's `setup.cfg`
with `../` paths, works for bump2version too but puts the set's version in
one member's file; the root holds what spans the packages (ADR-182). The
comment in `machinome/vet/universe.toml` naming "setup.cfg's bumpversion"
becomes "the root's `.bumpversion.cfg`".

`tests/test_release_records.py` (Decision 9) reads the version from the
core's manifest, as it does at the base, and holds to it: `.bumpversion.cfg`'s
`current_version`, every member's `version`, and every requirement between
members, which must be `~=<version>`; and it requires a `.bumpversion.cfg`
table for every member's manifest and none in the core's `setup.cfg`.

### 6. CI on uv; the requirements files and tox retired

The first cycle deferred this (its open question 3) to "the change that moves
CI onto `uv sync --locked`". This is that change, because after the cut the
CI's `pip install -r requirements.txt -r requirements_dev.txt` cannot put the
engines on the path: the jobs never install the framework, pytest's rootdir
supplies the core alone, and a requirements file can name the siblings only
as editable installs, which in setuptools' default mode shadow the core
(the first cycle's probe 2) and in compat mode need every member listed and
built: the uv sync, by hand. The weighed alternative, editable pip installs
of each member in compat mode (probe 8's line), works and is what
`CONTRIBUTING.rst` gives a contributor without uv; for CI it duplicates the
lock and checks nothing, where `uv sync --locked` installs exactly what the
developers' benches install and fails when `uv.lock` is stale.

The `lint`, `test` and `browser-snapshot` jobs each replace their
`actions/setup-python` step and their "Install requirements" step with:

```yaml
      - name: Setup uv
        uses: astral-sh/setup-uv@v10
        with:
          version: "0.11.8"
          enable-cache: true
          cache-dependency-glob: uv.lock

      # The workspace from its lock: every package under packages/ editable
      # in compat mode, with the framework's dev extra (every kernel, the
      # tools). --locked fails when uv.lock is stale. Run at the root, where
      # the default group is declared; the venv's bin/ joins the PATH of the
      # later steps.
      - name: Sync the workspace
        working-directory: .
        run: |
          uv sync --locked --python 3.12
          echo "$GITHUB_WORKSPACE/.venv/bin" >> "$GITHUB_PATH"
```

so their later `run` lines (`black`, `flake8`, `coverage run ... pytest`,
`pytest tests/...`) keep their spelling and run from the job's default
directory, `packages/machinome`. uv is pinned to the version the lock was
made with. The `browser-snapshot` job's install step becomes:

```yaml
      - name: Install the browser snapshot dependencies
        run: |
          uv pip install --python "$GITHUB_WORKSPACE/.venv/bin/python" \
            "machinome-viewer[snapshot] @ git+https://github.com/machinome/machinome-viewer.git"
          playwright install --with-deps chromium
```

(a uv venv carries no pip). Its `actions/setup-node` step stays. The lint
steps cover the engines' modules:

```yaml
      - name: Black
        continue-on-error: true
        run: black --check machinome tests ../machinome-*/machinome

      - name: Flake8
        continue-on-error: true
        run: flake8 --max-line-length=89 machinome tests ../machinome-*/machinome
```

The glob names the engine packages' import trees; each later cycle's
packages match it by their directory's name. The `docs` job is unchanged
(it installs `docs/requirements.txt` alone, pinned by
`test_docs_exports.py`). The `dist` job is unchanged. The tag-triggered
`build` job's "Install requirements" step becomes `pip install build`, the
only tool its `make dist` runs; it still builds and attaches the core alone
(Open Questions 2).

Retired with the requirements files: `tox.ini`, whose `[testenv]` installs
`extras = all` into an isolated environment and so needs the engine
distributions from an index, which serves none before the 0.9 release; its
`flake8` environment is the CI's lint. The Makefile's `test-all` target
(`tox`) and its `clean-test` line removing `.tox/` go with it, and the
Makefile's lint targets take the same paths as CI:
`flake8 machinome tests ../machinome-*/machinome` and the black
line likewise. `CONTRIBUTING.rst` drops `make test-all`.

`test_kernel_extras.py` loses `test_ci_installs_every_concrete_requirement_of_all`
and `test_tox_installs_every_extra` and gains, in their place (Decision 9),
that the lock holds every kernel distribution and both engines, and that the
`lint`, `test` and `browser-snapshot` jobs each run `uv sync --locked` at
the root. The `kernel-extras` requirement's sentence "the continuous
integration and the tox environments SHALL install every kernel extra"
becomes the CI syncing the lock whose default group installs the
development extra.

### 7. `scripts/check-dist`: two rows

The script is unchanged but for its table and the install line it builds.
`SMOKES` gains two rows, and a row may carry `through`: the core's extra
that installs it. The install command then names the core's wheel with its
row's extras (unchanged: `[openscad,stl]`), and, for each row with
`through`, `machinome[<through>]` instead of that member's wheel path; the
`--find-links` of every member's `dist/` directory makes pip take the
engines from the built archives, which no index serves (probe 4). So the
smoke proves that the core's extra reaches the sibling distribution.

The two rows, keyed `machinome-engine-brep` and `machinome-engine-mesh`,
each with `'through'` (`'brep'`, `'mesh'`), `'extras': []`, `'commands': []`,
and code that, in the throwaway venv's `python -I`:

1. imports `machinome.engine` and resolves the provider through the seam
   (`brep_engine()` / `mesh_engine()`), asserting it is not `None`, its
   `CONTRACT` equals `BREP_CONTRACT` / `MESH_CONTRACT`, and it is
   `machinome.engine.brep` / `.mesh`;
2. reads `importlib.metadata.distribution('<name>')` and asserts its
   `version` equals `metadata.version('machinome')`, its `files` hold
   `machinome/engine/<x>.py` and no `__init__.py`, and
   `Path(distribution.locate_file('machinome/engine/<x>.py')).resolve()`
   equals `Path(<provider>.__file__).resolve()`, which lies inside the venv;
3. asserts its requirements hold `machinome~=<version>`;
4. runs one operation on its kernel: B-rep, `solid_volume` of
   `OCP.BRepPrimAPI.BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 10, 10, 10).Shape()`
   within 1e-6 of 1000; mesh, `volume(centred_box([2.0, 3.0, 4.0]))` equal
   to 24.0 and `identity()[0] == 'manifold3d'`;
5. asserts `License-Expression` and lists and asserts the three licence
   files under the distribution's `licenses/`, as the core's row does; the
   lines are one shared template formatted with the name, so the core's row
   keeps its own code unchanged;
6. prints one line: the name, version, provider file, contract and the
   operation's result.

Because every member must have a row, the script refuses a member without
one, as it does at the base; the node packages' cycles add theirs.


Reviewed before the planning commit (10 October 2026): the lint glob and
the scans' glob are `machinome-*`, every sibling package's import tree,
not `machinome-engine-*`, so the node packages of the next two cycles match
them without an edit; `machinome-*` never matches the core's own directory.

### 8. The lint configuration stays in the core's `setup.cfg`

The `[flake8]` section stays in `packages/machinome/setup.cfg`, its two
engine entries becoming

```
    ../machinome-engine-brep/machinome/engine/brep.py:E402
    ../machinome-engine-mesh/machinome/engine/mesh.py:E402
```

Probe 6: flake8 reads a per-file-ignores path relative to the file stating
it, and reads no configuration above its working directory, so a root
`.flake8` is lost when the lint runs from `packages/machinome/`, where CI,
the Makefile and `CONTRIBUTING.rst` run it. A configuration in each engine
package would be a file the plan's decision 1 does not give it (`flake8`
reads no `pyproject.toml`), and inline `# noqa: E402` on 26 import lines
edits the moved modules. One place, the framework's, which owns the
extension packages' record.

### 9. The gate, red first

Each test is written or corrected before the move and run; the expected red
is stated. "The move" below is task group 3.

- **`tests/test_repository_layout.py`, new group G9, the extension
  packages** (`ENGINES = {'machinome-engine-brep': 'brep',
  'machinome-engine-mesh': 'mesh'}`):
  - `test_each_engine_directory_holds_only_what_distinguishes_it`: `git
    ls-files --cached --others --exclude-standard` under the directory is
    exactly `pyproject.toml`, `README.md`, `LICENSE`, `LICENSES` and
    `machinome/engine/<x>.py`; `LICENSE` and `LICENSES` are links reading
    `../../LICENSE` and `../../LICENSES`; no `__init__.py` under
    `machinome/`. Red: the directory does not exist.
  - `test_each_engine_manifest_is_a_portion_of_the_set`: `[project] name` is
    the directory's; `license` and `license-files` equal the core's;
    `[tool.setuptools.packages.find]` is `include = ["machinome.engine"]`,
    `namespaces = true`. Red: no manifest.
  - `test_each_engine_readme_names_its_install_and_the_licence`: `README.md`
    holds `pip install "machinome[<x>]"` and `framework_licence`
    (whitespace normalised). Red: no README.
  - `test_each_provider_resolves_from_its_package`:
    `Path(importlib.import_module('machinome.engine.<x>').__file__).resolve()
    == REPOSITORY / 'packages' / <name> / 'machinome/engine/<x>.py'`, and
    the seam returns that module. A checkout test, as the gate is. Red: the
    module resolves to `packages/machinome/machinome/engine/<x>.py`.
  - `test_the_core_engine_package_holds_only_the_seams`: the entries of
    `PACKAGE / 'machinome/engine'` but `__pycache__` are `{'__init__.py'}`.
    Red: `brep.py` and `mesh.py` are there.
  - G4 generalised, `test_every_member_is_a_workspace_source`:
    `tool.uv.sources` equals `{name: {'workspace': True}}` for the
    distribution name of every directory under `packages/`, and `uv.lock`
    records `source = { editable = "packages/<dir>" }` for each. The base's
    `test_the_framework_is_a_workspace_source` and
    `test_the_lock_records_the_member_editable` are folded into it. Red
    once the directories exist (the sources name `machinome` alone); before
    the move it is green, the directories being absent, so its red is shown
    after task 3.1, before the sources are edited.
  - `test_the_guide_installs_every_member_without_uv`: the root
    `CONTRIBUTING.rst` names `editable_mode=compat` and, for every directory
    under `packages/`, `-e packages/<dir>` (the framework's with `[dev]`),
    and names neither `tox` nor `requirements.txt`. Red: the guide's pip
    line names the framework alone and it says `make test-all`, tox's.
  - Already generic and red at the move: G7's
    `test_the_readme_links_every_package_and_states_the_licence` (probe 5),
    turned green by the root README's two rows (Decision 10).
- **`tests/test_kernel_extras.py`**: `REPOSITORY = parents[3]`; the
  version read from the core's manifest; `EXTRAS['brep'] =
  {f'machinome-engine-brep~={VERSION}'}` and `mesh` likewise; a new table
  `ENGINE_REQUIREMENTS = {'machinome-engine-brep': {f'machinome~={VERSION}',
  'cadquery-ocp>=7.8.1,<7.9', 'numpy'}, 'machinome-engine-mesh':
  {f'machinome~={VERSION}', 'manifold3d', 'numpy'}}` and
  `test_each_engine_requires_the_core_and_its_kernel` reading
  `packages/<name>/pyproject.toml`; `test_the_occt_range_is_stated_once`:
  across the core's dependencies and extras and both engines' dependencies,
  `cadquery-ocp` is named once, in `machinome-engine-brep`;
  `test_the_lock_installs_every_kernel`: the `[[package]]` names of
  `uv.lock` include every `KERNEL_DISTRIBUTIONS` entry and both engines;
  `test_ci_syncs_the_locked_workspace`: the `lint`, `test` and
  `browser-snapshot` jobs each have a step running `uv sync --locked` with
  `working-directory: .`. The two retired tests are removed and the module
  docstring names the manifests and the lock. Reds: `brep` and `mesh`
  (the core lists the kernels), the engines' manifests absent, the lock
  holding no engine, no `uv sync` in CI; `test_the_occt_range_is_stated_once`
  red (`cadquery-ocp` named in the core's `brep` extra, not in an engine).
- **`tests/test_core_kernel_free.py`**: `REPOSITORY = parents[3]`; a
  `portion_modules()` yielding every module under
  `packages/machinome-*/machinome/`, keyed
  `machinome-engine-brep/machinome/engine/brep.py` (relative to
  `packages/`); `PROVIDERS` and the provider exclusions of the core's scans
  dropped (the core holds no provider to exclude); the core census of
  `test_kernels_are_imported_only_by_their_modules` without the two engine
  rows; a new `test_the_engine_packages_import_only_their_kernels`
  expecting `{'machinome-engine-brep/machinome/engine/brep.py': ['OCP'],
  'machinome-engine-mesh/machinome/engine/mesh.py': ['manifold3d']}`;
  `EXTRA_OF`'s engine keys in that spelling, and
  `test_each_kernel_module_checks_its_kernel_first` reading
  `dict(every_module()) | dict(portion_modules())`. Reds: the core census
  (it still finds the engines), the portion census (empty), and the
  `require_extra` check (`KeyError` on the portion keys).
- **`tests/test_core_names_no_split_words.py`**: `REPOSITORY = parents[3]`
  and the gate test scanning `ROOT` and every `packages/machinome-*`
  directory (`scan(root)` already reads `root / 'machinome'` relative to
  `root`, so `ZONES` keep their spelling). Not red by itself before the
  move (the engines are in the core's scan); its blind spot after the move
  is shown red first (task 4.4): a comment holding the mesh-quality word
  (W1, which offends in every zone) is planted in the moved `mesh.py`;
  the base's gate passes, the repointed one fails naming
  `machinome/engine/mesh.py`; then the plant is removed.
- **`tests/test_release_records.py`**: `VersionFilesTest` reads
  `REPOSITORY / '.bumpversion.cfg'` for `current_version` in place of
  `setup.cfg`; new `test_every_member_is_numbered_with_the_core`
  (`packages/*/pyproject.toml` versions), `test_every_pin_between_members_is_compatible`
  (every requirement of a member, extras included, naming another member is
  `~=<version>`; a member's own name, as in `machinome[brep]`, is skipped),
  and `test_the_version_is_bumped_from_the_root` (a `bumpversion:file` or
  `bumpversion:file(<label>)` table for every member's `pyproject.toml`, and
  no `[bumpversion]` in the core's `setup.cfg`). Reds: no
  `.bumpversion.cfg`; after the founding, the tables missing for the two
  engines.
- **`tests/test_brep_engine.py`, `tests/test_mesh_engine.py`**:
  `ENGINE_SOURCE = Path(importlib.util.find_spec('machinome.engine.brep').origin)`
  (and `.mesh`), which finds the provider wherever it is installed without
  importing it. Green before the move; red at the move without this
  repointing (probe 5), so the repointing lands before the move and the
  move leaves them green.
- **`tests/test_docs_structure.py`**: `KernelExtrasTest` gains
  `test_the_installation_page_names_the_engine_distributions`
  (`machinome-engine-brep` and `machinome-engine-mesh` on
  `start/install.rst`). Red: the page names neither.
- **`scripts/check-dist`** is not in the suite; it is run by the applier
  and CI's `dist` job (Decision 7). Red first: with the two directories
  founded and no rows yet, it fails "machinome-engine-brep has no smoke in
  scripts/check-dist".

What stays a blind spot, recorded: the gate reads a checkout. An installed
set is proved by `check-dist` and by the bench venv the suite runs on, not
by the suite.

### 10. The records and the manual

- **`HISTORY.rst`**, under `Unreleased`, after the first cycle's entry:

  ```
  * **The B-rep and mesh engines are PACKAGES of their own.**
    ``machinome-engine-brep`` ships ``machinome.engine.brep`` and
    ``machinome-engine-mesh`` ships ``machinome.engine.mesh``, each a
    namespace portion in its own directory under ``packages/``, numbered
    with the framework and pinned to it with ``~=`` both ways; the
    framework's ``brep`` and ``mesh`` extras install them, and the OCCT
    range is stated in the B-rep engine's manifest. Every address, extra
    and install line is unchanged. The version is bumped from the
    repository's ``.bumpversion.cfg``; CI installs the workspace from its
    lock with uv, and ``requirements.txt``, ``requirements_dev.txt`` and
    ``tox.ini`` are retired. Change ``cut-the-engines`` (ADR-183).
  ```

- **`docs/project/changelog.rst`**: an `Unreleased` section above
  `Machinome 0.8.1` with one bullet, since what a reader's `pip install`
  brings changes:

  ```
  Unreleased
  ----------

  * **The engines are packages of their own.** ``machinome[brep]`` installs
    the distribution ``machinome-engine-brep`` and ``machinome[mesh]``
    installs ``machinome-engine-mesh``; ``from machinome.engine import
    brep`` and every install line are unchanged.
  ```

  The release-records pin and the profile pin already admit one
  `Unreleased` section above the released one in the changelog.
- **`docs/start/install.rst`**: in the extras table, the `brep` row's third
  cell becomes "the B-rep engine, the package ``machinome-engine-brep``,
  with the OCCT kernel; every extra above installs it too", and the `mesh`
  row's "the mesh engine, the package ``machinome-engine-mesh``, with
  manifold3d, for every comparison on meshes: a part without B-rep
  geometry, ``machinome test --mesh``, ``assertAssemblySupported``, a
  fusion of such parts". The section "Two packages, two licences" becomes
  "Packages and licences", its first sentence "The framework is the package
  ``machinome``, with its engines in the packages ``machinome-engine-brep``
  and ``machinome-engine-mesh`` that its ``brep`` and ``mesh`` extras
  install, all licensed |framework_licence|, at the recipient's choice." The
  rest of the page is unchanged; no release fact moves, the licence stays a
  substitution, no page changes shape. `howto/backends.rst` needs no edit
  (Context).
- **`docs/architecture.md`**, the Map: the two engine rows become "B-rep
  engine, on OCCT, the distribution `machinome-engine-brep`" with code "the
  repository's `packages/machinome-engine-brep/` (`machinome/engine/brep.py`)",
  ADRs "160 (`docs/adrs/OCCT/`), 180, 183", and "Mesh engine, on manifold3d,
  the distribution `machinome-engine-mesh`" likewise with "176, 180, 183";
  the "Repository layout" row's code gains `.bumpversion.cfg` and its ADRs
  183. Wherever its prose says an engine "leaves the core at the cut" or
  "in layer 2" (`grep -n "leaves the core"`), the sentence states that it
  has left, in the distribution named.
- **`docs/adrs/README.md`**: ADR-183 under BUILD after ADR-182; the OCCT
  category heading "(leaves the core with `machinome/engine/brep.py` at the
  cut)" becomes "(the distribution `machinome-engine-brep`, ADR-183)".
- **The root `README.md`**: two rows after the framework's:

  ```markdown
  | [`machinome-engine-brep`](packages/machinome-engine-brep/) | The B-rep engine, `machinome.engine.brep`, on OCCT; installed by `machinome[brep]`. |
  | [`machinome-engine-mesh`](packages/machinome-engine-mesh/) | The mesh engine, `machinome.engine.mesh`, on manifold3d; installed by `machinome[mesh]`. |
  ```

- **`CONTRIBUTING.rst`**: the uv sentence "which installs the framework
  editable with its dev dependencies" becomes "which installs every package
  under ``packages/`` editable, the framework with its dev dependencies";
  the sentence before the pip block becomes "or, without uv, create a
  virtualenv and install every package under ``packages/`` editable in
  compat mode, the framework with its dev dependencies::" and the block's
  last line becomes

  ```
      $ pip install --config-settings editable_mode=compat \
          -e packages/machinome-engine-brep -e packages/machinome-engine-mesh \
          -e "packages/machinome[dev]"
  ```

  (probe 8); the line `$ make test-all      # tox across supported Python
  versions` is removed. Nothing else changes.
- **`context7.json`**: unchanged (it excludes no new folder; the engines'
  READMEs are documentation). Its rules name `machinome[brep]` where they
  do, which stays true.
- **ADR-183, BUILD**: `docs/adrs/BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md`,
  written by the applier with Status **Proposed** and promoted to
  **Accepted** after review, Date 2026-10-10, Change `cut-the-engines`,
  Related to ADR-182 (the layout it fills), ADR-180 (the engine package
  that admits portions) and ADR-167 (the extras, amended: `brep` and `mesh`
  name distributions). BUILD rather than NODE: it decides how a module is
  distributed, installed, versioned and checked, beside ADR-130 and ADR-182;
  the resolution it relies on is ADR-169's and ADR-180's and does not
  change. Context: the plan's decisions 1 to 3, the seams written for
  portions and never exercised. Considered options: (1) each extension
  package a namespace portion in its own distribution under `packages/`,
  with no `__init__.py` at the levels the core defines, chosen; (2) the
  engines as regular packages under another import name with the core
  re-exporting them: refused, the address is the location and the plan's
  rule forbids a second spelling; (3) the core shipping every module and
  the extras only pulling kernels, as in 0.8: refused by the plan, the
  cut's purpose. Decision: an extension package is a directory
  `packages/<distribution>/` holding its manifest, a README, the root's
  licence by relative links, and its portion at its address; the core's
  path extension resolves it; the seam refuses its absence by the extra's
  name; it carries the set's version, and the pins between it and the core
  are `~=<version>` both ways, bumped from the root's `.bumpversion.cfg`;
  the workspace names it as a source and installs it editable in compat
  mode; `check-dist` installs it through the core's extra and smokes it
  through the seam; its kernel ranges are stated in its manifest; its
  record is the framework's. Consequences: installed from wheels the
  portion's file lands in the core's `machinome/engine/` directory and is
  owned by its own distribution's `RECORD`; the editable install puts its
  directory on the path, and an install whose `PYTHONPATH` names the core
  alone loses it; the core's `pip install` without the extra carries no
  engine; CI installs the set with uv.

### 11. The spec deltas

- `kernel-extras`: MODIFIED "The CAD kernels are extras, not required
  dependencies" (the `brep` and `mesh` extras install the two
  distributions, which state the kernels and their ranges; CI through the
  lock; the installation page names the distributions), "The core imports
  no kernel outside its kernel modules" (the core's scan without the
  engines; the engine packages' modules import only their kernels), "The
  engine providers are modules of one engine package that admits portions"
  (each provider a portion shipped by its own distribution; resolving
  from it; the core's distribution holding neither).
- `brep-engine-dependency`: MODIFIED "The core holds no kernel code" (the
  scan reads the core, where no provider is) and "An unavailable B-rep
  engine fails actionably at the point of use" (the extra installs the
  distribution; an absent distribution is an absent engine).
- `mesh-engine-dependency`: MODIFIED "An unavailable mesh engine fails
  actionably at the point of use" and "The core holds no mesh engine code",
  likewise.
- `framework-identity`: MODIFIED "The framework is the package directory
  `packages/machinome` of a monorepo" (the extension packages beside it,
  their shape, one version bumped from the root, CI from the lock,
  `check-dist` through the core).
- `framework-contributor-guidance`: MODIFIED "The contributor guide states
  the monorepo's development setup" (the install without uv names every
  member in compat mode).

Each MODIFIED requirement is copied whole and edited.

### 12. The universe sweep

From this cycle the campaign reads the project catalogue against the bench
with the workspace's `scripts/load-projects`, which loads each model in a
fresh interpreter with `PYTHONPATH` set to `--bench` first, refuses a bench
without `machinome/__init__.py`, and runs the interpreter `--python` names.
The bench is therefore the framework's directory and the interpreter the
bench venv, whose `.pth` lines put both engine directories on the path:

```
/home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
  --bench /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-engines/packages/machinome \
  --python /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-engines/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 \
  --json <scratch>/load-projects.json
```

All ten tables of `scripts/load-projects.d/` apply, as at `root-cleanup`; no
new table, since no name moves. Read against `root-cleanup`'s counts: 62
repositories, 129 rows, 121 ok, 0 expected, 2 unexpected (wall_clock_41's
own CadQuery error, Dum-E without machinome-freecad), 0 timeout, 6
no-model. A row that differs is a finding.

## Risks / Trade-offs

- [The fallback recipe (the workspace venv with `PYTHONPATH`) no longer runs
  the whole suite: fourteen test modules start subprocesses with
  `PYTHONPATH` set to the core's directory alone, which drops a portion
  reached only through `PYTHONPATH`] → The bench venv is the validation
  recipe; the fallback serves a partial run with `PYTHONPATH` listing the
  three package directories. The fourteen modules are not changed: on the
  bench venv the `.pth` lines put the engines on the path whatever
  `PYTHONPATH` says, and the campaign's close moves the workspace's benches
  onto the sync.
- [The workspace venv (`/home/asa/devel/machinome/.venv`) has the primary
  checkout's framework editable, whose `machinome/engine/` still holds the
  engines] → It holds its own `__init__.py`, so `_namespace_portions`
  refuses it from a bench's path; a bench run on that venv finds no engine
  rather than the primary's. Its reinstall is the campaign's close.
- [`pip install "machinome[brep]"` from an index fails until
  `machinome-engine-brep` is uploaded with the release] → Nothing is
  published by this campaign; the release of 0.9 publishes the set
  together (the package standard, section 2).
- [A contributor who used `tox` or the requirements files loses them] →
  `CONTRIBUTING.rst` gives both installs; the CI's matrix of one Python is
  unchanged.
- [`setup-uv@v10` or uv 0.11.8 changes behaviour] → The uv version is
  pinned in the step and is the one the lock was made with.
- [Uninstalling the core from a wheel install leaves the engines' files in
  `site-packages/machinome/engine/`] → Each is owned by its distribution's
  `RECORD` and leaves with it; recorded, not addressed.
- [The `numpy` line in each engine's manifest is unranged] → The core,
  pinned `~=` by the engine, pins `numpy==2.2.*`; one range, stated once.

## Migration Plan

Within the cycle, in the order of tasks.md: the baseline; the red tests at
the base's paths; the founding of the two directories and the two `git mv`;
the manifests and the core's extras; the workspace's sources, lock and sync;
the version table; CI, the Makefile and the retirements; `check-dist`; the
records; validation. Rollback is a revert of the implementation commit and a
`uv sync`. Outside the cycle, at the campaign's close: the workspace's
`scripts/setup` and `scripts/dev-env` (the sync recipe), the workspace venv,
the collaborator guide, the studio's `machinome-api` skill (no install line
changes).

## Open Questions

1. **Whether this cycle retires tox.** Its `[testenv]` cannot install the
   set before the engines are on an index, and CI never ran it. The
   alternative is `tox-uv` with `runner = uv-venv-lock-runner`, which
   installs from the lock. Recommendation: retire it here (Decision 6);
   multi-Python runs return, if wanted, as a CI matrix over `uv sync
   --python 3.11` and `3.12`, which tests what the lock installs.
2. **The tag-triggered `build` job.** It builds and attaches the core's
   archives alone. Recommendation: leave it so in this campaign, which
   publishes nothing; the 0.9 release change makes it build every member,
   with the release pass that uploads the set together.
3. **The engines' `numpy` line.** Declared unranged because each module
   imports numpy. The alternative is to omit it and rely on the core's
   requirement. Recommendation: keep it; a direct import is a declared
   dependency, and the range stays the core's.
4. **An `Unreleased` section in the manual's changelog.** The first cycle
   wrote none, its change being invisible to a project. This one changes
   what `pip install "machinome[brep]"` brings, so the pilot's ruling of 29
   September 2026 asks for the bullet now. Recommendation: write it
   (Decision 10); the 0.9 release rewrites the section as a story.
5. **The README links on an index page.** The engines' READMEs name
   `LICENSE` and `LICENSES/` as text, since relative links do not resolve
   on PyPI. Recommendation: keep it so; the framework's README.rst links
   relatively and the release may revisit both together.
