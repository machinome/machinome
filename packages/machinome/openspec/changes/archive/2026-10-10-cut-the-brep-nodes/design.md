## Context

The third cycle of the 0.9 monorepo campaign (`workflow/ongoing/monorepo-0.9.md`
at the repository root, "The campaign: the cut", cycle 3), cut from the line
`v0.9-base` at 84757c38, whose head holds the second cycle, `cut-the-engines`
(ADR-183), integrated, on the bench `machinome/WTs/v0.9-base-cut-the-brep-nodes`.
The plan's decisions accepted by the pilot on 10 October 2026 bind it: the
record of an extension package is the framework's (1); one version for the set,
`~=` pins both ways (2); a uv workspace at the root, every member editable in
compat mode (3). ADR-183 fixed the shape of an extension package on the two
engines and said the eight node packages take it "with no new mechanism"; this
cycle cuts the four over the B-rep engine and tests that sentence.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench at
84757c38 unless marked *inferred*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C3-propose/`
(named `<scratch>` below), never in the bench, with uv 0.11.8, CPython 3.12.3,
pip 26, build 1.6, twine 7, flake8 7.4.1, bump2version and the OpenSpec CLI
1.6.0. `<scratch>/repo/` is a git repository holding `git ls-files` of the bench
with its links, on which the cut was made as Decisions 1 to 4 and 7 to 9 state
(not 5, 6 or 10 to 12 unless a probe says so).

### What the cut touches

- The four modules. `machinome/node/cadquery.py` imports `machinome.engine`,
  `machinome.extras`, `machinome.node.declarative` and
  `machinome.node.brep_leaf`, and no kernel (a project's `render()` imports
  CadQuery). `build123d.py` imports `logging`, `machinome.engine`,
  `machinome.extras`, `machinome.node.brep_leaf` and
  `machinome.node.sheet_leaf`, and imports `build123d` and `numpy` inside its
  functions; it is also the artwork reducer of the markings
  (`SVG_REDUCER_CONTRACT = 1`). `step.py` calls `require_extra('step', ...,
  'cadquery', 'OCP')`, then imports `cadquery`, `numpy`, fourteen `OCP`
  modules, `machinome.engine`, `machinome.node.cadquery` (`workplane_shape`),
  `machinome.node.brep_leaf`, `machinome.node.sources` and
  `machinome.source_generation`. `molejo.py` calls `require_extra('molejo',
  ..., 'molejo', 'OCP')`, then imports `trimesh`, `molejo.brep` and
  `machinome.node.flexible`. None of the four declares a `leaf_contract`.
- `machinome/node/__init__.py` extends `__path__` with
  `_namespace_portions`, refuses each class name of the table naming its
  module, and resolves a submodule on attribute read (`_submodule`, `_load`).
  `machinome/node/supported.py` holds `NODE_TYPES` (the four keys among
  eight), `load(key)`, which turns a `ModuleNotFoundError` naming the module
  into `ExtraUnavailable(key, 'the <key> node type (<classes>)', address)`,
  `renderer` and `needed_by`. `machinome/manager/import_step.py` and
  `machinome/manager/new.py` reach node types through `supported.load`; the
  CLI through `needed_by` and `load`. `machinome/node/markings.py` resolves the
  artwork reducer with `importlib.import_module('machinome.node.build123d')`
  in `_artwork_reducer()`, and `machinome/node/base.py`'s `_build_markings`
  re-raises an `ExtraUnavailable` from it naming the part, the marking and the
  artwork; any other import error passes unchanged. The markings' reducer stays
  where the second cycle's tree has it: in `machinome.node.build123d`, so it
  moves with that module. The template `manager/templates/project/root/cadquery.py`
  imports `from machinome.node.cadquery import CadQueryNode` as text a project
  owns.
- The core's `pyproject.toml`: `cadquery = ["cadquery==2.7.*",
  "machinome[brep]"]`, `build123d` with `ocp-gordon>=0.2.2,<0.3`, `step` with
  `cadquery==2.7.*`, `molejo = ["molejo[brep]==0.2.*", "machinome[brep]"]`,
  each with its comment, and `all` naming every extra.
- `setup.cfg`'s `[flake8]` per-file ignores name `machinome/node/step.py:E402`
  and `machinome/node/molejo.py:E402`.
- The manual: `docs/conf.py` puts `..` (the framework's directory) first on
  `sys.path` and mocks the kernels; `docs/reference/api.rst` autodocs
  `machinome.node.cadquery.CadQueryNode`, `machinome.node.build123d.Build123dNode`
  and `.Build123dSheetNode`, `machinome.node.step.StepNode` and
  `machinome.node.molejo.MolejoNode`. `docs/start/install.rst` names the
  extras, the engines' distributions and, as an example, the refusal
  `machinome.node.cadquery (CadQueryNode) needs cadquery, which is not
  installed; ...`. `howto/backends.rst` names each node type's extra and not
  what it installs; `howto/imported-parts.rst` names no install line; neither
  needs an edit.
- The specs. `kernel-extras`, `node-model`, `markings`, `cli` (the
  `import-step` command), `framework-identity` and
  `framework-contributor-guidance` name a node type's install, its module's
  place or the members by name. `step-import`, `step-assembly` and
  `flexible-parts` name neither an install line nor a module path the cut
  moves (`grep` for `machinome\[`, `extra` and `machinome/node/` in each), so
  they are not modified. `vet` reads import names, not distributions.

### Probes

1. **The four portions on a real sync** (`<scratch>/repo/`: the four
   directories founded as Decision 1 states, the four `git mv`, the manifests
   and READMEs of Decision 2, the core's extras of Decision 4, the root sources
   of Decision 7, the version tables of Decision 8, the lint ignores of
   Decision 9). `env -C <scratch>/repo uv lock`: "Resolved 183 packages",
   "Added machinome-node-build123d v0.8.1", "-cadquery", "-molejo", "-step";
   the lock records `source = { editable = "packages/machinome-node-<x>" }` for
   each, the step package's dependencies naming `machinome-node-cadquery` and
   `machinome-engine-brep` editable. `uv sync --python 3.12` on a fresh venv:
   "Installed 174 packages", seven `__editable__` `.pth` files, each holding its
   package directory. With the venv's Python, from `/tmp`:
   `machinome.node.__path__` is the core's `machinome/node`, then the
   build123d, cadquery, molejo and step directories' `machinome/node`; each of
   `machinome.node.cadquery`, `.build123d`, `.step` and `.molejo` has its
   `__file__` in its own directory; `machinome.node.step.workplane_shape is
   machinome.node.cadquery.workplane_shape` (one import across two portions);
   `supported.load(key)` returns each, the classes' `__module__` the address;
   `from machinome.node import StepNode` (and `CadQueryNode`,
   `Build123dSheetNode`, `MolejoNode`) raises the root's refusal naming the
   module, unchanged; the core's `machinome/node/` holds none of the four;
   `markings._artwork_reducer()` returns the build123d package's module,
   contract 1. In `<scratch>/p1/`: `machinome new demo` exits 0 (a `Solid2Node`
   starter, SolidPython being installed); a two-product STEP document written
   by CadQuery, then `machinome import-step ../pair.step` writes `parts.py`
   (`from machinome.node.step import StepNode`) and `assembly.py` and exits 0.
   The seams needed no change.
2. **A node package absent** (same venv). `uv pip uninstall
   machinome-node-step`: `__path__` has four entries, and:
   - `import machinome.node.step` and `from machinome.node.step import
     StepNode` raise `ModuleNotFoundError: No module named
     'machinome.node.step'`, `name` the module, no extra;
   - `from machinome.node import step` raises `ImportError: cannot import name
     'step' from 'machinome.node'`, and `hasattr(machinome.node, 'step')` is
     `False`;
   - `from machinome.node import StepNode` raises the root's refusal naming
     `machinome.node.step`, as before;
   - `supported.load('step')` raises `ExtraUnavailable: the step node type
     (StepNode) needs machinome.node.step, which is not installed; install it
     with 'pip install "machinome[step]"'`, and `machinome import-step
     ../pair.step` prints `Error: machinome import-step needs the step extra:`
     followed by that sentence, writes nothing and exits 1.

   Then `uv pip uninstall machinome-node-build123d` and the build of
   `tests/test_markings.py`'s `BUILD_PLATE` (the faceted plate whose markings
   are stale) from the framework's directory: the error is
   `ModuleNotFoundError: No module named 'machinome.node.build123d'`, naming
   neither the part, the marking, the artwork nor the extra, and no marking
   artifact is written. Before the cut, an install without the extra had the
   module and not its kernel, and both doors answered with the module's own
   refusal naming `machinome[<key>]` (the `kernel-extras` requirement "A kernel
   module refuses an absent kernel at import", the `cli-startup-cost` scenario
   "An absent extra is reported by its install line", the `markings` scenario
   "A stale marking without the extra is refused by its install line"). After
   the cut an install without the extra has neither, so the project's import
   line, the node root's submodule read and the markings' seam lose the
   extra's name; only `load` and the CLI keep it. This is what Decision 5
   answers.
3. **Decision 5 prototyped** (`<scratch>/finder-variant2.diff`, 73 lines, the
   code of Decision 5 applied to `<scratch>/repo/`, both packages uninstalled):
   `import machinome.node.step`, `from machinome.node.step import StepNode`,
   `from machinome.node import step` and `hasattr(machinome.node, 'step')` each
   raise `ExtraUnavailable` with `name` `machinome.node.step`, `extra` `step`
   and `load`'s sentence; `load('step')` and `import-step` as in probe 2; the
   stale marking build raises `ExtraUnavailable: marking badge of Plate
   (artwork badge.svg) needs machinome.node.build123d, which is not installed;
   install it with 'pip install "machinome[build123d]"'` and writes no
   artifact; importing `machinome.node` does not import
   `machinome.node.supported`; the finder is the last of `sys.meta_path`.
   Dropping a portion's directory from `sys.path` before the first import of
   `machinome` stands in for its absence on the editable install (the same
   refusal for `machinome.node.step`, the other portions still resolving), which
   is how the gate tests it (Decision 10). Re-synced, the modules
   `test_node_root.py`, `test_node_root_exports_nothing.py`,
   `test_supported_node_types.py`, `test_cli_lazy_imports.py`, `test_markings.py`,
   `test_import_step.py`, `test_leaf_addresses.py`, `test_manager_new.py`,
   `test_step_node.py`, `test_cli.py`, `test_leaf_contract_members.py` and
   `test_lazy_test_framework.py` pass but one test:
   `test_supported_node_types.py::TheTableTest::test_the_module_defines_only_the_table_and_its_readers`,
   whose set of the module's names lacks `absent`.
4. **The archives.** From a clean copy of `<scratch>/repo/`'s tracked files
   (`<scratch>/clean/`), `python -m build packages/<member> --outdir
   <scratch>/dist/<member>` for the seven, with the workspace venv: exit 0
   each. Each node sdist holds 18 entries, among them `LICENSE` (793 bytes) and
   `LICENSES/CERN-OHL-S-2.0.txt` (13419) and `GPL-2.0-or-later.txt` (17984) as
   regular files and `machinome/node/<x>.py`, and no `__init__.py`; each node
   wheel holds 8 entries: `machinome/node/<x>.py`, the three licence files under
   `dist-info/licenses/`, `METADATA`, `WHEEL`, `top_level.txt`, `RECORD`. The
   core's sdist holds 1015 entries and its wheel 122, the second cycle's clean
   1019 and 126 less the four modules, and neither holds one of them. `twine
   check --strict` on the fourteen archives: 14 PASSED.
5. **The wheels installed.** A fresh `python3.12 -m venv`, then `pip install`
   with a `--find-links` per member's `dist/` and
   `"<dist>/machinome/machinome-0.8.1-py3-none-any.whl[openscad,stl]"
   "machinome[brep]" "machinome[mesh]" "machinome[cadquery]"
   "machinome[build123d]" "machinome[step]" "machinome[molejo]"`: exit 0. One
   `site-packages/machinome/node/` holds `__init__.py` and the four modules,
   `__path__` one entry. In a directory holding a `pyproject.toml` with
   `[tool.machinome]` and a `parts.py` of one class per node type, with `python
   -I`: a `CadQueryNode` box 10 x 10 x 10, assembled, has a B-rep volume of
   999.9999999999998 through `brep_engine().solid_volume(node.shape())`; a
   `Build123dNode` box 2 x 3 x 4, 24.0; a `StepNode` over a 4 x 5 x 6 box
   CadQuery wrote to `box.step`, 120.0; a `MolejoNode` tube of radius 1 swept
   along a helix of radius 8, 3 turns and height 20, through
   `snapshot_shape(render(), {'height': 20.0})`, one solid of volume 477.89,
   the closed form being 477.8895. Each distribution's `locate_file` of its
   module resolves to the imported module's file, lists three licence files,
   and `requires` is its manifest's (Decision 2).
6. **Where `step` gets CadQuery and the engine.** `pip install --dry-run
   --ignore-installed --report` of `machinome-node-step` into a fresh venv from
   the built archives, once with the manifest of Decision 2 and once with a
   variant naming only `machinome~=0.8.1`, `machinome-node-cadquery~=0.8.1` and
   `numpy`: 85 packages each way, the same names and versions (`cadquery`
   2.7.0, `cadquery-ocp` 7.8.1.1.post1, `machinome-engine-brep` 0.8.1, `numpy`
   2.2.6). The choice changes no install; Decision 3 makes it on what the
   module imports.
7. **The whole suite on the cut tree** (probe 1's venv, `pytest -q -rs -p
   no:cacheprovider` from `packages/machinome/` with the venv's `bin/` first on
   `PATH`; the tree of probe 1, no test edited): `31 failed, 4780 passed, 20
   skipped, 6836 subtests passed in 498.66s`. The 20 skips are the second
   cycle's (16 the viewer, networkx, the `jscad` command, 2 vendor STEP). The
   31 failures, in four modules, each a path or a table this change moves:
   - `test_core_kernel_free.py` (8): `test_no_core_module_imports_the_kernel_or_cadquery`
     and `test_kernels_are_imported_only_by_their_modules` (the core censuses
     still list the four), `test_the_engine_packages_import_only_their_kernels`
     (the portion census finds the node packages too),
     `test_each_kernel_module_checks_its_kernel_first` four subtests
     (`KeyError: 'machinome/node/<x>.py'`), and
     `test_kernel_modules_are_named_only_at_the_seams` subtest
     `seam='machinome/node/step.py'` (`None != {'machinome.node.cadquery'}`);
   - `test_kernel_extras.py` (9): `test_each_extra_lists_what_its_module_needs`
     and `test_every_kernel_extra_includes_the_brep_extra`, four subtests each
     (the core's extras now name the distributions),
     `test_cadquery_carries_one_range_wherever_it_is_named` (it reads only the
     core, which names CadQuery nowhere now);
   - `test_leaf_contract_reach.py` (6): `FileNotFoundError` on
     `packages/machinome/machinome/node/<x>.py` (`LEAVING`);
   - `test_repository_layout.py` (8): the root README links no node package,
     and `CONTRIBUTING.rst` names no `-e packages/machinome-node-<x>`.

   Green on the cut tree, and so blind to it: `test_node_root_exports_nothing.py`'s
   text gate (its `scan()` reads the core's `machinome/` alone, so the four
   modules leave it); `test_docs_structure.py` (the page test names the
   engines' distributions only); `test_supported_node_types.py` and
   `test_markings.py`'s artwork seam (each simulates an absent kernel, never an
   absent package); the layout gate's extension group (its table holds the two
   engines). The core-only scans (`test_core_names_no_scad.py`,
   `test_no_class_name_recognition.py`, `test_expression_type.py`,
   `test_leaf_capability_set.py`, `test_machinome_identity.py`) stop reading the
   four modules; each states a rule of the core, which the four no longer are.
   `test_core_names_no_split_words.py` already reads every `packages/machinome-*`
   (the second cycle), with zone paths relative to each package, so the four
   modules stay in its scan under their `ZONES` spelling.
8. **The manual on the cut tree.** A fresh venv with
   `packages/machinome/docs/requirements.txt` alone (Sphinx, the theme,
   `machinome-viewer`), then `sphinx -b html -W --keep-going docs <html>` from
   the clean copy's framework directory: "build finished with problems, 5
   warnings (with warnings treated as errors)", exit 1, each `autodoc: failed
   to import` one of `CadQueryNode`, `Build123dNode`, `Build123dSheetNode`,
   `StepNode` and `MolejoNode` (`No module named 'machinome.node.<x>'`). With
   `docs/conf.py` as Decision 6 states: exit 0, and `reference/api.html` holds
   the five classes. Read the Docs clones the repository, so the siblings are
   there (`.readthedocs.yaml` reads every path from the root).
9. **The version bumped from the root** (`<scratch>/bump/`: the root's
   `.bumpversion.cfg` of Decision 8 and the eleven files it names, a git
   repository). `bump2version --no-commit --no-tag --new-version 0.9.0 patch`:
   exit 0, 28 lines changed in 11 files: `current_version`, the seven
   manifests' and the universe's `version`, `__version__`, `release`, and 17
   pins (the core's six, each engine's one, two each in the CadQuery,
   build123d and molejo packages, three in the STEP package). The viewer floors (`machinome-viewer>=0.8.1`) do not move.
10. **The lint.** From `<scratch>/repo/packages/machinome/`, `flake8
    --max-line-length=89 machinome tests` and the six `../machinome-*/machinome`
    paths named explicitly: 759 lines, equal line for line to the bench's 759
    once the `../machinome-node-<x>/` prefix is stripped; 2 E402, both in
    `tests/test_couplings.py`, as at the base. With the base's `setup.cfg`: 25
    E402, the moved `step.py` and `molejo.py` having lost their ignores.

## Goals / Non-Goals

**Goals:**

- `machinome-node-cadquery`, `machinome-node-build123d`, `machinome-node-step`
  and `machinome-node-molejo` founded in ADR-183's shape, each installed by the
  core's extra of the same last name.
- Every door that refused a node type by its extra before the cut refuses it by
  its extra after it, when its distribution is absent.
- The manual builds with warnings as errors from its requirements alone.
- Gates that fail if a node module drifts back into the core, a pin drifts, a
  sibling escapes a scan or a table, or an absent package loses its refusal.

**Non-Goals:**

- The OpenSCAD family, `solid2`, `jscad` and `stl` (`cut-the-mesh-nodes`).
- Any change to the four modules, a seam's resolution, a message's words, a
  class, the table's keys, `import-step`'s behaviour, a public name, an
  address, an extra's name or a contract number.
- A `leaf_contract` declared on the four classes (Open Questions 3), a version
  bump, an upload, a push, the release job, the workspace's `scripts/setup`
  and `scripts/dev-env`.

## Decisions

### 1. The shape of a node package

ADR-183's, with the node package's path:

```
packages/machinome-node-step/
├── pyproject.toml
├── README.md
├── LICENSE  -> ../../LICENSE
├── LICENSES -> ../../LICENSES
└── machinome/
    └── node/
        └── step.py          moved by git mv, unchanged
```

and `machinome-node-cadquery` (`cadquery.py`), `machinome-node-build123d`
(`build123d.py`) and `machinome-node-molejo` (`molejo.py`) the same. No
`__init__.py` under `machinome/` or `machinome/node/` (probes 1, 4, 5). The
package standard's items are read as the second cycle's design, Decision 1,
reads them: no `CREDITS.md` (the four bundle nothing), no `MANIFEST.in` (probe
4), no `.gitignore` (the root's ignores `/packages/*/build/` and
`/packages/*/*.egg-info/`; `git status` after probe 1's sync shows nothing
untracked).

### 2. The four manifests and the four READMEs, verbatim

Every manifest has the engines' header and footer with its own `name`,
`description` and portion comment:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-<x>"
version = "0.8.1"
description = "<the description below>"
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
    # The core this node type is a portion of, released with it: the set
    # carries one version, and the pins between its packages are ~= both
    # ways.
    "machinome~=0.8.1",
    <the node package's lines below>
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The portion, machinome/node/<x>.py, with no __init__.py at either
# level, so the core's package path admits it.
include = ["machinome.node"]
namespaces = true
```

The engines' first comment names the contract number at the seam as "the real
guard"; the node packages' does not, because none of the four classes declares
a `leaf_contract` (Context; Open Questions 3).

`machinome-node-cadquery`, description "The CadQuery node type of Machinome":

```toml
    # cadquery and build123d both bind the single OCP module through the
    # cadquery-ocp distribution, so their ranges must intersect. This pair is
    # the newest that resolves to one OCP (7.8): cadquery 2.8 moved to
    # cadquery-ocp >=7.9 while build123d 0.11 moved to cadquery-ocp-novtk, a
    # second distribution installing the same OCP package. One range per
    # kernel: machinome-node-step names CadQuery alike.
    "cadquery==2.7.*",
    # The B-rep engine, which turns a render result into B-rep geometry and
    # states the OCCT range, once.
    "machinome-engine-brep~=0.8.1",
```

`machinome-node-build123d`, description "The build123d node types of
Machinome, and the reducer of its SVG artwork":

```toml
    # The newest build123d whose OCP is the one cadquery 2.7 binds
    # (machinome-node-cadquery's manifest says why the pair).
    "build123d==0.10.*",
    # build123d 0.10 leaves this transitive dependency unbounded; 0.3
    # imports OCP 8 collections absent from our shared OCP 7.8 runtime.
    "ocp-gordon>=0.2.2,<0.3",
    # The B-rep engine, which turns a render result into B-rep geometry and
    # states the OCCT range, once.
    "machinome-engine-brep~=0.8.1",
    # Arrays, imported by the artwork reducer; the core pins the range.
    "numpy",
```

`machinome-node-step`, description "The STEP node types of Machinome, on
CadQuery's reader":

```toml
    # The module converts a CadQuery shape with machinome.node.cadquery's
    # workplane_shape.
    "machinome-node-cadquery~=0.8.1",
    # The reader and adjust are CadQuery's, imported here directly, so
    # named here directly, in the one range machinome-node-cadquery states.
    "cadquery==2.7.*",
    # The document is read through the OCCT binding, whose range the B-rep
    # engine states once; the part is a B-rep leaf on that engine.
    "machinome-engine-brep~=0.8.1",
    # Arrays; the core pins the range.
    "numpy",
```

`machinome-node-molejo`, description "The molejo node type of Machinome, for
flexible parts":

```toml
    # The flexible leaf evaluates molejo shapes and reaches for molejo's
    # OCCT evaluator, so molejo[brep]. Pinned to the minor: a molejo minor
    # carries the shape-spec version it implements, and the documents this
    # framework writes name that version.
    "molejo[brep]==0.2.*",
    # The B-rep engine, whose currency molejo's solid already is, and which
    # states the OCCT range once.
    "machinome-engine-brep~=0.8.1",
    # Meshes; the core pins the range.
    "trimesh",
```

The comments are the core's of today, moved with their pins: the CadQuery
and build123d pair's reason in the CadQuery package, pointed at from the
build123d one, so it is stated once; `ocp-gordon`'s and molejo's verbatim. Each
package names the B-rep engine directly, since each module imports
`machinome.engine` and turns its geometry into the engine's currency; none
names `cadquery-ocp`, so the OCCT range stays stated once, in
`machinome-engine-brep` (`test_the_occt_range_is_stated_once`). A third-party
module a node module imports directly is a declared dependency, unranged, the
core pinning the range: `numpy` (build123d, step) and `trimesh` (molejo), as
the engines declare `numpy` (the second cycle's Open Questions 3, accepted).

`include = ["machinome.node"]` with `namespaces = true` ships the portion and
nothing else (probe 4).

`packages/machinome-node-cadquery/README.md`:

```markdown
# machinome-node-cadquery

The CadQuery node type of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.cadquery`, whose `CadQueryNode` is a part modelled
with [CadQuery](https://cadquery.readthedocs.io), its render result B-rep
geometry on the framework's B-rep engine.

## Install

    pip install "machinome[cadquery]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

The other three have the same `## Install` (with their extra), `## Manual` and
`## Licence` sections and these headings and first paragraphs:

```markdown
# machinome-node-build123d

The build123d node types of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.build123d`, whose `Build123dNode` is a part
modelled with [build123d](https://build123d.readthedocs.io) and whose
`Build123dSheetNode` is a sheet part cut from an authored profile, both
B-rep geometry on the framework's B-rep engine. It also reduces the SVG
artwork of a part's markings.
```

```markdown
# machinome-node-step

The STEP node types of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.step`, whose `StepNode` is one part read from a
STEP document, B-rep geometry on the framework's B-rep engine, and whose
`StepAssembly` reads the document's products and their placements, both
through CadQuery's reader. `machinome import-step` uses it to write a
project's source from a document.
```

```markdown
# machinome-node-molejo

The molejo node type of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.molejo`, whose `MolejoNode` is a flexible part
authored as a [molejo](https://molejo.readthedocs.io) shape, evaluated by
molejo to a mesh and to a B-rep solid at each instant of the machine.
```

Each shows the package and adds nothing, as the engines' do. The eight files
as probed are `<scratch>/drafts/machinome-node-<x>/pyproject.toml` and
`README.md`.

### 3. `machinome-node-step` requires the CadQuery node, and names CadQuery and the engine itself

`step.py` imports `machinome.node.cadquery` (`workplane_shape`), so
`machinome-node-step` requires `machinome-node-cadquery~=0.8.1`: the first pin
between two extension packages, `~=` like every pin of the set, held by
`test_every_pin_between_members_is_compatible` as it is written and moved by
`.bumpversion.cfg`'s pin table (Decision 8). It also imports `cadquery` and
`OCP` itself, so it names `cadquery==2.7.*` and `machinome-engine-brep~=0.8.1`
directly, rather than reaching them through the CadQuery package. Probe 6 shows
both spellings install the same 85 packages; the difference is what a reader of
the manifest learns and what a later edit of the CadQuery package's manifest
can silently take away. The CadQuery range is then written in two manifests,
and `test_cadquery_carries_one_range_wherever_it_is_named` holds them equal
(Decision 10). The alternative, the CadQuery package alone, is Open Questions 2.

### 4. The core's manifest

In `packages/machinome/pyproject.toml`, the block from "# The kernel extras,
each named by the last component" to the line before "# The OpenSCAD node
family" becomes:

```toml
# The node types over OCCT, each named by the last component of its address
# and each the distribution machinome-node-<name>, which states its kernel
# and requires the B-rep engine, so the OCCT range, stated once in
# machinome-engine-brep, resolves one OCCT binding for several extras.
#
# `machinome.node.cadquery` (CadQueryNode).
cadquery = [
    "machinome-node-cadquery~=0.8.1",
]
# `machinome.node.build123d` (Build123dNode, Build123dSheetNode and the
# reducer of Svg artwork).
build123d = [
    "machinome-node-build123d~=0.8.1",
]
# `machinome.node.step` (StepNode, StepAssembly, `machinome import-step`),
# which reads with CadQuery and the OCCT binding itself and requires the
# CadQuery node type.
step = [
    "machinome-node-step~=0.8.1",
]
# `machinome.node.molejo` (MolejoNode), with molejo and its OCCT evaluator.
molejo = [
    "machinome-node-molejo~=0.8.1",
]
```

and the comment in `dependencies` naming "cadquery, build123d, ocp-gordon,
molejo, the B-rep engine ..." becomes "the node types over cadquery, build123d
and molejo (the extras `cadquery`, `build123d`, `step` and `molejo`), the B-rep
engine (the extra `brep`), the mesh engine (the extra `mesh`) and SolidPython
are the extras below, ...", the rest of that comment unchanged. The four extras
no longer name `machinome[brep]`: each node distribution requires the engine
itself, so `pip install "machinome[cadquery]"` still installs it (probe 5).
`brep`, `mesh`, `all`, `dev` and every other extra are unchanged.

### 5. An absent node package is refused by its extra at its import

Probe 2 shows that the cut alone moves the refusal of an absent node type from
the module's import, where three requirements and the installation page put
it, to `load` and the CLI alone. The plan's rule for an extension package
(ADR-183) is that it is "refused by its extra's name". The smallest change that
keeps every door's refusal is a last finder: when no finder before it has found
`machinome.node.<key>` for a key of the table, the node root answers with a
module whose import raises the table's refusal. The message is the one `load`
already gives, stated once.

In `machinome/node/supported.py`, `load`'s branch for an absent module becomes
`raise absent(key) from None`, and the module gains:

```python
def absent(key):
    """The refusal of node type `key` when no installed distribution ships
    its module: it names the node type, its classes, its module and the
    extra that installs it. `load` raises it, and so does the node root's
    last finder at the module's own import."""
    classes = ', '.join(NODE_TYPES[key].classes)
    return ExtraUnavailable(key, f'the {key} node type ({classes})',
                            f'machinome.node.{key}')
```

In `machinome/node/__init__.py`, after `__path__ = _namespace_portions(...)`,
with `import sys as _sys` and `from importlib.machinery import ModuleSpec as
_ModuleSpec` among its imports:

```python
class _AbsentNodeType:
    """The last finder on `sys.meta_path`: a node type of the table whose
    module no finder before it found -- its distribution is not installed --
    is a module whose import raises the table's refusal,
    `supported.absent(key)`, naming the extra that installs it."""

    def find_spec(self, fullname, path=None, target=None):
        package, _, key = fullname.rpartition('.')
        if package != __name__:
            return None
        from .supported import NODE_TYPES
        if key not in NODE_TYPES:
            return None
        return _ModuleSpec(fullname, self)

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        from .supported import absent
        raise absent(module.__name__.rpartition('.')[2])


if not any(isinstance(finder, _AbsentNodeType) for finder in _sys.meta_path):
    _sys.meta_path.append(_AbsentNodeType())
```

and the module docstring's paragraph "The refusals." gains one sentence: "A
node type of the table whose distribution is not installed is refused at its
own import by the root's last finder, with the table's refusal naming its
extra." Probe 3 shows the effect at every door. What does not change: an
installed module, from the core's directory, a portion's or a wheel, is found
before the finder is asked; a module whose kernel is absent still raises its
own refusal from `require_extra`; a broken module still raises its own error;
`from machinome.node import StepNode` still raises the root's refusal naming
the module; importing `machinome.node` imports no node type and not
`machinome.node.supported` (the finder reads the table only when asked for a
node type no other finder found). `importlib.util.find_spec` now returns a spec
for an absent node type's module, which nothing in the core or the suite reads
as presence (`grep -rn find_spec`): the root's `_submodule` then loads it and
raises the refusal, which is what the `cli-startup-cost` requirement "Deferred
imports do not hide a broken installation" asks of an absent extra.

The markings seam needs no edit: `_artwork_reducer()` receives the
`ExtraUnavailable` and `_build_markings` re-raises it naming the part, the
marking and the artwork (probe 3). The alternatives are Open Questions 1.

Reviewed before the planning commit (10 October 2026): Decision 5 is
accepted by the orchestrator under the pilot's advance authorization, as the
smallest change that keeps the refusal three ratified requirements and the
installation page promise, last on `sys.meta_path` so it shadows nothing,
recorded in ADR-184 and reported to the pilot as reversible; declining it
would be the larger decision, a user-visible loss of the promise.

### 6. The manual's autodoc path

`docs/conf.py`'s first lines become:

```python
import glob
import os
import sys

# Make machinome importable for autodoc without installing it, with the
# extension packages beside it under packages/, whose modules the core's
# package path admits as portions (machinome._namespace_portions).
sys.path[:0] = [os.path.abspath('..'),
                *sorted(glob.glob(os.path.abspath('../../machinome-*')))]
```

Probe 8: the five classes resolve and the build passes with `-W`. The engines'
directories join the path too; nothing in the manual autodocs them (its engine
functions are written as `py:function` directives). The alternative, a
`docs/requirements.txt` line per node package, would install from an index that
serves none of them before 0.9; installing the core would make the manual
document an install rather than the tree.

### 7. The workspace: sources and lock

The root `pyproject.toml`'s `[tool.uv.sources]` gains, after the two engines:

```toml
machinome-node-build123d = { workspace = true }
machinome-node-cadquery = { workspace = true }
machinome-node-molejo = { workspace = true }
machinome-node-step = { workspace = true }
```

`uv lock` regenerates `uv.lock` (probe 1: 183 packages); `uv sync --python 3.12`
installs the four editable in compat mode (a fresh venv: 174 packages, seven
`.pth` lines). Nothing else in the root manifest or the root `.gitignore`
changes.

### 8. One version for the set: eight tables

The root `.bumpversion.cfg` gains, after the mesh engine's tables, for each of
`cadquery`, `build123d`, `step` and `molejo` in that order:

```ini
[bumpversion:file(version):packages/machinome-node-<x>/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pins):packages/machinome-node-<x>/pyproject.toml]
search = ~={current_version}"
replace = ~={new_version}"
```

The pin table's search is the core's (`~={current_version}"`), not the engines'
(`"machinome~={current_version}"`), because a node manifest holds two or three
pins. Probe 9 moved the 28 statements and nothing else. The file keeps no
comment (the second cycle's correction 3).

### 9. The lint ignores

`packages/machinome/setup.cfg`'s two entries become
`../machinome-node-step/machinome/node/step.py:E402` and
`../machinome-node-molejo/machinome/node/molejo.py:E402`, in place. CI's and
the Makefile's `../machinome-*/machinome` glob already reads the four packages.
Probe 10: 759 lines, the base's.

### 10. The gate, red first

Each test is written or corrected before the move and run, its expected red
stated. "The move" below is task group 3.

- **`tests/test_repository_layout.py`, the extension group generalised.**
  `ENGINES` becomes one table of every sibling:

  ```python
  #: The framework's extension packages, by directory: the module each
  #: ships, by its address, and the core's extra that installs it.
  EXTENSIONS = {
      'machinome-engine-brep': ('machinome.engine.brep', 'brep'),
      'machinome-engine-mesh': ('machinome.engine.mesh', 'mesh'),
      'machinome-node-cadquery': ('machinome.node.cadquery', 'cadquery'),
      'machinome-node-build123d': ('machinome.node.build123d', 'build123d'),
      'machinome-node-step': ('machinome.node.step', 'step'),
      'machinome-node-molejo': ('machinome.node.molejo', 'molejo'),
  }
  ```

  and the group's tests read it: `test_each_extension_directory_holds_only_what_distinguishes_it`
  (the module's path is the address's), `test_each_extension_manifest_is_a_portion_of_the_set`
  (`include` is the address's package, `machinome.engine` or `machinome.node`),
  `test_each_extension_readme_names_its_install_and_the_licence`,
  `test_each_portion_resolves_from_its_package` (the imported module's file is
  the directory's; for an engine, its seam returns that module), the unchanged
  `test_the_core_engine_package_holds_only_the_seams`, and two new:
  `test_the_core_node_package_holds_no_extension_module` (no
  `machinome/node/<x>.py` of the table in the core's directory) and
  `test_every_sibling_is_in_the_table` (every `packages/machinome-*` directory
  is a key). Reds: the four node rows of the first four tests (no directory;
  the module resolves under `packages/machinome/`), the core-node test (the
  four are there). `test_every_sibling_is_in_the_table` is green before the
  move and after (its red is shown once at task 3.3 by a stray directory).
  Already generic and red at the move: the README test and
  `test_the_guide_installs_every_member_without_uv` (probe 7); the sources test
  is green on probe 7's tree because Decision 7 is applied with the move, and
  red at task 3.3, between the move and the sources.
- **`tests/test_kernel_extras.py`**: `EXTRAS['cadquery']` and the three others
  become `{f'machinome-node-<x>~={VERSION}'}`; `ENGINE_REQUIREMENTS` becomes
  `PACKAGE_REQUIREMENTS`, gaining the four manifests' requirement sets of
  Decision 2 (its readers, the requirements, OCCT-range and lock tests, read it
  under the new name); `test_every_kernel_extra_includes_the_brep_extra`
  becomes `test_every_node_package_requires_the_brep_engine` (each node
  manifest names `machinome-engine-brep~=<version>`);
  `test_no_node_extra_includes_the_mesh_engine` also reads the node manifests
  (none names `machinome-engine-mesh` or `machinome[mesh]`);
  `test_cadquery_carries_one_range_wherever_it_is_named` reads the core and
  every sibling manifest, and requires CadQuery named somewhere. The module
  docstring names the node manifests. Reds: the four `EXTRAS` subtests, the
  requirements test (`FileNotFoundError` on the node manifests), the
  brep-engine test (no manifest), the lock test (no node package locked).
- **`tests/test_core_kernel_free.py`**: the core census of
  `test_kernels_are_imported_only_by_their_modules` and the one of
  `test_no_core_module_imports_the_kernel_or_cadquery` keep the template alone;
  `test_the_engine_packages_import_only_their_kernels` becomes
  `test_the_extension_packages_import_only_their_kernels`, expecting also
  `machinome-node-build123d/machinome/node/build123d.py: ['build123d']`,
  `machinome-node-molejo/machinome/node/molejo.py: ['molejo']` and
  `machinome-node-step/machinome/node/step.py: ['OCP', 'cadquery']`; `EXTRA_OF`'s
  four node keys and `SEAMS`' step key take the `machinome-node-<x>/...`
  spelling; `test_kernel_modules_are_named_only_at_the_seams` reads
  `every_module()` and `portion_modules()`. Reds: the two core censuses (they
  find the four), the portion census (it finds the engines alone), the
  `require_extra` test (`KeyError` on the portion keys), the seams test (the
  step key is absent).
- **`tests/test_leaf_contract_reach.py`**: `LEAVING` through
  `importlib.util.find_spec(f'machinome.node.{name}').origin`, as the second
  cycle repointed the engine tests; the `ALLOWED` reasons for
  `step.py -> machinome.node.cadquery` and for `require_extra` say what the cut
  decided ("machinome-node-step requires machinome-node-cadquery
  (`cut-the-brep-nodes`)"; "the check stays in the module that moved"). Green
  before the move and after; its red without the repointing is probe 7's.
- **`tests/test_node_root_exports_nothing.py`**: the gate test merges `scan()`
  of every `packages/machinome-*` directory, its paths prefixed by the
  directory's name. Its blind spot is shown red first after the move (task
  4.6): a comment spelling the root import of `StepNode` (in pieces in the
  task's command) planted in the moved `step.py`; the base's gate passes, the
  repointed one fails naming it; the plant is removed.
- **`tests/test_core_names_no_split_words.py`**: unchanged. That it reads the
  moved modules is shown once after the move (task 4.7): the mesh-quality
  word planted in a comment of the moved `molejo.py` fails the gate naming
  `machinome/node/molejo.py`; the plant is removed.
- **`tests/test_supported_node_types.py`**: `absent` joins the names
  `test_the_module_defines_only_the_table_and_its_readers` expects, and a new
  `AbsentPackageTest` runs, for `step`, a subprocess that removes
  `<repository>/packages/machinome-node-step` from `sys.path` before importing
  `machinome`, and expects `ExtraUnavailable` with `name`
  `machinome.node.step`, `extra` `step` and `load`'s sentence at
  `import machinome.node.step`, at `from machinome.node.step import StepNode`,
  at `from machinome.node import step` and at `hasattr(machinome.node,
  'step')`, while `machinome.node.cadquery` still imports. Reds: before the
  move the module is in the core and imports (no refusal); after the move and
  before Decision 5, a plain `ModuleNotFoundError` with no `extra`, and the
  root's `ImportError` and `False`.
- **`tests/test_markings.py`**: `ArtworkSeamTest.test_a_stale_marking_without_the_reducer_package_is_refused`,
  `BUILD_PLATE` run with `packages/machinome-node-build123d` removed from
  `sys.path` first, expecting the refusal of probe 3 and no marking artifact.
  Reds: before the move the build succeeds; after it, `ModuleNotFoundError`
  naming the module.
- **`tests/test_docs_structure.py`**: `test_the_installation_page_names_the_engine_distributions`
  becomes `test_the_installation_page_names_the_extension_distributions`, the
  six names of `EXTENSIONS` written out. Red: the page names no node
  distribution.
- **`tests/test_release_records.py`**: unchanged; its member, pin and
  bumped-from-root tests read every `packages/*/pyproject.toml`. After the
  founding the bumped-from-root test is red (four manifests without a table);
  the pin test's red is shown once by planting `machinome-node-cadquery>=0.8.1`
  in the step manifest.
- **`scripts/check-dist`** is not in the suite. Red first: with the four
  directories founded and no rows, it fails "machinome-node-build123d has no
  smoke in scripts/check-dist" (the first missing by sort order).

What stays a blind spot, recorded: the gate reads a checkout; an installed set
is proved by `check-dist` and by the bench venv the suite runs on. The absence
of a package is stood in for by its directory missing from `sys.path`, which
an editable install allows and a wheel install is proved by probe 2's
uninstall.

### 11. `scripts/check-dist`: four rows

The script gains a `NODE` template beside `ENGINE`, and four rows keyed by the
node distributions, each with `'through'` its key, `'extras': []` and
`'commands': []`. The smoke, run with the throwaway venv's `python -I`:

1. imports `machinome.node.<x>`; reads `metadata.distribution(<name>)` and
   asserts its version equals `metadata.version('machinome')`, its files hold
   `machinome/node/<x>.py` and no `__init__.py`, the file it locates resolves
   to the module's `__file__`, inside the venv, and its requirements hold
   `machinome~=<version>` and `machinome-engine-brep~=<version>`;
2. writes, in a new temporary directory under the scratch directory, a
   `pyproject.toml` holding `[tool.machinome]` and a `parts.py` with one class,
   puts that directory first on `sys.path` and makes it the working directory;
3. renders one part on its kernel and reads its volume with
   `machinome.engine.brep_engine().solid_volume`: a `CadQueryNode` box
   10 x 10 x 10 assembled, within 1e-6 of 1000; a `Build123dNode` box
   2 x 3 x 4, within 1e-6 of 24; a `StepNode` over a 4 x 5 x 6 box CadQuery
   exports to `box.step` in that directory, within 1e-6 of 120; a `MolejoNode`
   tube of radius 1 swept along a helix of radius 8, 3 turns and height 20,
   `snapshot_shape(render(), {'height': 20.0})`, one solid within 0.1 % of the
   closed form `pi * 3 * sqrt((16 * pi) ** 2 + (20 / 3) ** 2)`;
4. the licence lines of `LICENCES`, formatted with the name;
5. prints one line: the name, version, module file and the volume.

Probe 5 ran these four renders on the installed wheels. Every member has a
row, so the script still refuses one without.

### 12. The records and the manual; ADR-184

- **`HISTORY.rst`**, under `Unreleased`, after the second cycle's entry:

  ```
  * **The CadQuery, build123d, STEP and molejo node types are PACKAGES of
    their own.** ``machinome-node-cadquery``, ``machinome-node-build123d``,
    ``machinome-node-step`` and ``machinome-node-molejo`` each ship
    ``machinome.node.<name>`` as a namespace portion in its own directory
    under ``packages/``, state its kernel and require the B-rep engine;
    ``machinome-node-step`` requires ``machinome-node-cadquery``. The
    framework's ``cadquery``, ``build123d``, ``step`` and ``molejo`` extras
    install them; every address, extra and install line is unchanged. A node
    type whose package is not installed is refused at its import naming the
    extra that installs it, as an absent kernel was. Change
    ``cut-the-brep-nodes`` (ADR-184).
  ```

- **`docs/project/changelog.rst`**, under `Unreleased`, after the engines'
  bullet:

  ```
  * **The B-rep node types are packages of their own.**
    ``machinome[cadquery]``, ``machinome[build123d]``, ``machinome[step]``
    and ``machinome[molejo]`` install the distributions
    ``machinome-node-cadquery``, ``-build123d``, ``-step`` and ``-molejo``;
    ``from machinome.node.step import StepNode`` and every install line are
    unchanged, and without the extra the import names the line that installs
    it.
  ```

- **`docs/start/install.rst`**: the third cell of the `cadquery`, `build123d`,
  `step` and `molejo` rows begins "the package ``machinome-node-<x>``, with"
  before what it installs today (CadQuery, build123d, CadQuery's STEP reader,
  molejo with its B-rep evaluator), the rest of each cell unchanged; the
  `brep` row's "every extra above installs it too" stays true. The example
  refusal becomes the one an install without the extra gives:

  ```
      ModuleNotFoundError: the cadquery node type (CadQueryNode) needs
      machinome.node.cadquery, which is not installed; install it with
      'pip install "machinome[cadquery]"'
  ```

  "Packages and licences"' first sentence becomes "The framework is the
  package ``machinome``, with its engines and its node types over the B-rep
  engine in packages of their own that its extras install
  (``machinome-engine-brep``, ``machinome-engine-mesh``,
  ``machinome-node-cadquery``, ``machinome-node-build123d``,
  ``machinome-node-step`` and ``machinome-node-molejo``), all licensed
  |framework_licence|, at the recipient's choice." Nothing else on the page
  changes; `howto/backends.rst` and `howto/imported-parts.rst` need no edit
  (Context).
- **`docs/architecture.md`**, the Map: a row after the mesh engine's, "Node
  types over the B-rep engine, the distributions `machinome-node-cadquery`,
  `-build123d`, `-step` and `-molejo`" with code "the repository's
  `packages/machinome-node-<x>/` (`machinome/node/<x>.py`)", capabilities
  `node-model`, `kernel-extras`, `step-import`, `step-assembly`,
  `flexible-parts`, `markings`, ADRs "057, 078, 079, 115, 162, 167, 169, 183,
  184"; the Node model row's code says "the four node types over the B-rep
  engine in their own distributions (row below)" and its ADRs gain 184. Any
  sentence that says a node module "leaves the core" for one of the four
  (`grep -n "leaves the core\|at the cut"`) says it has left, in the
  distribution named.
- **The root `README.md`**: four rows after the engines':

  ```markdown
  | [`machinome-node-cadquery`](packages/machinome-node-cadquery/) | The CadQuery node type, `machinome.node.cadquery`; installed by `machinome[cadquery]`. |
  | [`machinome-node-build123d`](packages/machinome-node-build123d/) | The build123d node types and the reducer of SVG artwork, `machinome.node.build123d`; installed by `machinome[build123d]`. |
  | [`machinome-node-step`](packages/machinome-node-step/) | The STEP node types, `machinome.node.step`; installed by `machinome[step]`. |
  | [`machinome-node-molejo`](packages/machinome-node-molejo/) | The molejo node type, `machinome.node.molejo`; installed by `machinome[molejo]`. |
  ```

- **`CONTRIBUTING.rst`**: the pip block's middle line names the six siblings:

  ```
      $ pip install --config-settings editable_mode=compat \
          -e packages/machinome-engine-brep -e packages/machinome-engine-mesh \
          -e packages/machinome-node-cadquery -e packages/machinome-node-build123d \
          -e packages/machinome-node-step -e packages/machinome-node-molejo \
          -e "packages/machinome[dev]"
  ```

  Nothing else changes.
- **ADR-184, NODE**: `docs/adrs/NODE/ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md`,
  written by the applier with Status **Proposed** and promoted to **Accepted**
  after review, Date 2026-10-10, Change `cut-the-brep-nodes`; amends ADR-167
  (the refusal at the module's import, when the module is absent, is the
  node root's), ADR-181 (the three doors keep their refusal when the package is
  absent) and ADR-183 (an extension package is refused by its extra's name at
  every door, a node package at its import); related to ADR-179 (`load`, whose
  sentence it reuses) and ADR-169 (the path extension, found first). Context:
  probe 2. Considered options: (1) the node root's last finder answering an
  absent node type of the table with a module whose import raises the table's
  refusal, chosen; (2) no finder: the project's import line, the node root's
  submodule read and the markings seam raise the import system's error and only
  `load` and the CLI name the extra, refused because three requirements and
  the installation page promise the extra's name at the import; (3) a
  conversion in each seam (`markings`, the root's `_submodule`) without a
  finder, refused because it leaves the project's own import line, the door
  every project uses, without the extra's name; (4) shipping a stub module per
  node type in the core, refused because a stub with its own file shadows the
  portion (the core's directory is first on the package path) and puts the
  modules back in the core. Decision: as Decision 5. Consequences: every door
  names `machinome[<key>]` whether the kernel or the package is absent; an
  absent node type's module has a spec (`importlib.util.find_spec` is not
  `None`), so presence is asked by importing it, as `load` does; a node type
  added to the table is refused when absent with no other edit.

  The shape of the four packages takes no ADR of its own: ADR-183 decides it
  and foresaw them ("the eight node packages of the later cycles take the same
  shape with no new mechanism"), and the pin between two extension packages is
  the set's rule already (`framework-identity`, "every requirement between two
  of them SHALL be the compatible-release pin"). ADR-183's index line gains
  "the B-rep node packages second (`cut-the-brep-nodes`)" and "amended by 184".
  If the pilot declines Decision 5 (Open Questions 1), no ADR is written and
  ADR-183 gains instead a dated consequence: "Bad: a project's import of a node
  type whose package is absent raises the import system's error; `load` and
  the CLI name the extra."

### 13. The spec deltas

- `kernel-extras`: MODIFIED "The CAD kernels are extras, not required
  dependencies" (the four extras install the node distributions; each states
  its kernel and requires the engine; `machinome-node-step` requires the
  CadQuery package; the ranges where they are now stated; the installation
  page names every extension distribution), "The core imports no kernel
  outside its kernel modules" (the four modules are not the core's; their own
  scan; the seams without `step.py`); ADDED "An absent node package is refused
  by its extra at its import" (Decision 5).
- `node-model`: MODIFIED "Each leaf type is one module under the node package"
  (the four modules each shipped by its own distribution as a portion, the
  address unchanged, the framework's distribution shipping none).
- `markings`: MODIFIED "Artwork is reduced through a seam that names its extra"
  (the reducer shipped by `machinome-node-build123d`; its absence refused like
  its kernel's).
- `cli`: MODIFIED "Import-step command" (the reader shipped by
  `machinome-node-step`; the command refuses its absence as it refuses its
  absent kernel).
- `framework-identity`: MODIFIED "The framework is the package directory
  `packages/machinome` of a monorepo" (the extension packages today; a pin
  between two of them; `check-dist` renders a part through each node package).
- `framework-contributor-guidance`: MODIFIED "The contributor guide states the
  monorepo's development setup" (the scenario's pip command names the four).

Each MODIFIED requirement is copied whole and edited.

### 14. The universe sweep

The second cycle's command (its design, Decision 12), with this bench:

```
/home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
  --bench /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-brep-nodes/packages/machinome \
  --python /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-brep-nodes/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 \
  --json <scratch>/load-projects.json
```

No new table: no name moves. Read against the second cycle's counts: 63
repositories, 130 rows, 121 ok, 0 expected, 3 unexpected (wall_clock_41's own
CadQuery error, Dum-E without machinome-freecad, fender-bender without
`fb_library`), 0 timeout, 6 no-model. `load-projects` puts `--bench` first on
`PYTHONPATH`, and the bench venv's `.pth` lines put the four packages'
directories on the path, so the catalogue's imports of the four modules
resolve as portions (*inferred*; the sweep is the evidence). A row that
differs is a finding.

## Risks / Trade-offs

- [The finder is consulted for every module the import system finds nowhere
  else] → It answers only `machinome.node.<key>` of the table and returns
  `None` for every other name after one string split; it is last, so no
  installed module is ever shadowed.
- [`importlib.util.find_spec('machinome.node.<key>')` is no longer `None` when
  the package is absent] → Nothing reads it as presence; presence is asked by
  importing, as `load` and the root do. A project probing presence that way
  would see a spec and a refusal on import; recorded in ADR-184.
- [The fallback recipe, the workspace venv with `PYTHONPATH`, loses the four
  node types as it lost the engines] → The bench venv is the recipe (the second
  cycle's Risks); with the finder, such a run is refused naming the extra
  rather than failing obscurely.
- [The workspace venv holds the primary checkout's framework editable, whose
  `machinome/node/` still holds the four modules] → As for the engines: the
  campaign's close reinstalls it from `packages/*`.
- [`pip install "machinome[step]"` from an index fails until the node packages
  are uploaded] → Nothing is published by this campaign; 0.9 publishes the set
  together.
- [Read the Docs builds the manual from the repository's tree] → It clones the
  whole repository, so `../../machinome-*` exists there as on a bench (probe 8
  on a clean copy); a build from an sdist was never supported.

## Migration Plan

Within the cycle, in the order of tasks.md: the baseline; the red tests at the
base's paths; the founding of the four directories and the four `git mv`; the
manifests, the READMEs and the core's extras; the workspace's sources, lock and
sync; the absent package's refusal; the manual's path; the version tables and
the lint; `check-dist`; the records; validation. Rollback is a revert of the
implementation commit and a `uv sync`. Outside the cycle, at the campaign's
close: the workspace's `scripts/setup` and `scripts/dev-env`, the workspace
venv, the collaborator guide, the studio's `machinome-api` skill (no install
line changes).

## Open Questions

1. **The absent package's refusal (Decision 5).** The plan says an extension
   package is "refused by its extra's name"; probe 2 shows the cut alone keeps
   that at `load` and the CLI but not at the project's import line, the node
   root's submodule read or the markings seam. The options are ADR-184's.
   Recommendation: the finder, the one mechanism that keeps every door's
   message without a second copy of it and without a module in the core; it is
   the cycle's one code change beyond the move, so it is the pilot's to accept.
   Declined, Decision 5 and its tests and ADR-184 leave the change, the
   `kernel-extras` ADDED requirement goes, the `markings` and `cli` deltas say
   the refusal of an absent package is the import system's, and install.rst's
   example keeps the kernel's message with a sentence that an install without
   the extra's package raises `No module named 'machinome.node.<x>'`.
2. **`machinome-node-step` names CadQuery and the engine directly.** The
   alternative is to reach both through `machinome-node-cadquery` (probe 6:
   the same install). Recommendation: direct (Decision 3); a direct import is a
   declared dependency, and the one-range test holds the two CadQuery lines
   equal.
3. **A leaf contract on the four classes.** None of `CadQueryNode`,
   `Build123dNode`, `Build123dSheetNode`, `StepNode` and `MolejoNode` declares
   `leaf_contract`, so the only guard between a node package and a core of
   another release is the `~=` pin. Declaring `leaf_contract = 3` on each
   would edit the moved modules, which this cycle keeps unchanged.
   Recommendation: not here; a finding from a mixed install would start that
   change, as ADR-165 started the stand-ins'.
4. **The installation page's example refusal.** It shows the kernel's message
   today; Decision 12 shows the one a reader without the extra now sees, the
   node root's. Recommendation: change it, since a reader who copies the page's
   install line without an extra meets that message first; the kernel's message
   stays in the `kernel-extras` spec for an install with the package and
   without its kernel.
5. **The `numpy` and `trimesh` lines.** Declared unranged because the modules
   import them, as the engines declare `numpy`. Recommendation: keep them, for
   the reason the second cycle's Open Questions 3 gave.
