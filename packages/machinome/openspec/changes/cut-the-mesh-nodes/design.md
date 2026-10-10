## Context

The fourth and last cycle of the cut in the 0.9 monorepo campaign
(`workflow/ongoing/monorepo-0.9.md` at the repository root, "The campaign: the
cut", cycle 4), cut from the line `v0.9-base` at 10e07f8c, whose head holds the
third cycle, `cut-the-brep-nodes` (ADR-184), integrated, on the bench
`machinome/WTs/v0.9-base-cut-the-mesh-nodes`. The plan's decisions accepted by
the pilot on 10 October 2026 bind it: the record of an extension package is the
framework's (1); one version for the set, `~=` pins both ways (2); a uv
workspace at the root, every member editable in compat mode (3). ADR-183 fixed
the shape of an extension package and said the node packages take it "with no
new mechanism"; ADR-184 said a node type added to the table "is refused when
absent with no other edit". The pilot's ruling of 4 October 2026 is that every
node type is a package, which is why `root-cleanup` gave `jscad` and `stl` an
extra that installs nothing. This cycle cuts the last four and tests those
three sentences on a package directory, a module over another node package and
two modules that need no kernel.

Paths below are the repository's when they start with `packages/` or name a
root file, the framework directory's otherwise. Facts were read on the bench at
10e07f8c unless marked *inferred*. Probes ran in the scratch directory
`/tmp/claude-1000/-home-asa-devel-machinome/1525b0f6-e3a2-4274-9baa-f5f016594707/scratchpad/C4-propose/`
(named `<scratch>` below), never in the bench, with uv 0.11.8, CPython 3.12.3,
pip 26, build 1.6, twine 7, flake8 7.4.1, bump2version, OpenSCAD 2021.01 at
`/usr/bin/openscad`, `xvfb-run`, no `jscad` command, and the OpenSpec CLI 1.6.0.
`<scratch>/repo/` is a git repository holding `git ls-files` of the bench with
its links, on which the cut was made as Decisions 1 to 7 state (not 8 to 11
unless a probe says so); `<scratch>/basewt/` is a worktree of it at the base.

### What the cut touches

- The OpenSCAD package `machinome/node/openscad/`: `__init__.py` calls
  `require_extra('openscad', 'machinome.node.openscad (OpenScadNode and the
  OpenSCAD writer)', 'solid2')`, then imports SolidPython, its `leaf` and
  `writer`, `machinome.node.sources` and `machinome.source_generation`, and
  defines `OpenScadNode`; `leaf.py` (`ScadLeafNode`) imports the node base,
  `machinome.node.leaf` and `from machinome.node.openscad import binary,
  writer`; `writer.py` imports SolidPython, `machinome.currency`, the node base
  and `machinome.node.presentation`; `binary.py` imports only the standard
  library. All imports are absolute.
- `machinome/viewers/openscad.py`, the OpenSCAD snapshot renderer
  (`OpenScadRenderer`, `OpenScadImportError`), imports `machinome.currency` and
  `from machinome.node.openscad import binary, writer`, and logs to the logger
  `viewers.openscad`. It is the one core module importing a node package
  (the plan's "Facts"; ADR-179's provisional column). `machinome/viewers/`
  also holds `__init__.py` (the licence header only), `bundle.py` and
  `browser.py`, which import nothing of the family.
- `machinome/node/solid2.py` calls `require_extra('solid2', ...)`, then imports
  SolidPython, `machinome.core.expressions`, `machinome.expression_graph`, and
  the OpenSCAD package's `binary` and `leaf`. `jscad.py` and `stl.py` call no
  `require_extra`; `jscad.py` imports the core alone and runs the `jscad`
  command; `stl.py` imports `trimesh` and the core.
- `machinome/node/supported.py`: the row `'openscad': NodeType(('OpenScadNode',),
  renderers=(('openscad', 'machinome.viewers.openscad.OpenScadRenderer'),))`;
  `renderer(name)` loads the contributing node type under `load`'s refusals
  and then imports the row's module by string. `machinome/manager/snapshot.py`
  offers `web` and the table's renderer names, defaults to `DEFAULT_RENDERER`,
  calls `supported.renderer` before loading the node and answers an
  `ExtraUnavailable` with `Error: machinome snapshot --renderer <name> needs
  the <extra> extra: <refusal>; or use --renderer web`, exit 1.
- `machinome/node/__init__.py`'s last finder (ADR-184) answers
  `machinome.node.<key>` for every key of the table, so the four keys of this
  cycle are refused when absent with no edit. A submodule of an absent package
  (`machinome.node.openscad.writer`) is refused when its parent is imported.
- The templates `machinome/manager/templates/project/root/solid2.py` and
  `cadquery.py` name their node types as text a project owns; `machinome new`
  loads `solid2`, then `cadquery`, through the table. `tests/base.py` imports
  `machinome.node.openscad.writer` inside `scad_code`. The suite imports
  `machinome.node.solid2` in 94 files and `machinome.node.openscad` in 43; it
  runs against the whole set installed and nothing about that changes.
- The core's `pyproject.toml`: `openscad = ["solidpython2==2.1.*"]`, `solid2 =
  ["machinome[openscad]"]`, `jscad = []`, `stl = []`, each with its comment,
  and the `dependencies` comment naming "SolidPython" among the extras.
  `setup.cfg`'s per-file ignores name `machinome/node/openscad/__init__.py:E402`
  and `machinome/node/solid2.py:E402`.
- The manual: `docs/conf.py` already puts every `../../machinome-*` directory
  on `sys.path` (the third cycle); `docs/reference/api.rst` autodocs
  `Solid2Node`, `OpenScadNode`, `JScadNode` and `StlNode`.
  `docs/start/install.rst` says the `openscad` and `solid2` extras install
  SolidPython, that `jscad` and `stl` "install nothing today", and offers
  `machinome[mesh]` alone for a project of OpenSCAD, JSCAD or STL parts;
  `docs/howto/backends.rst` says the `jscad` and `stl` extras install nothing;
  `docs/reference/cli.rst` says the OpenSCAD renderer needs
  `machinome[openscad]`, still true. `docs/architecture.md` places the
  renderer at `machinome/viewers/openscad.py` and says `jscad` and `stl`
  install nothing.
- The specs. `kernel-extras`, `openscad-node`, `cli` (the snapshot command's
  table row), `node-model`, `framework-identity` and
  `framework-contributor-guidance` name an install, a module's place, the
  renderer's address or the members. `openscad-dependency` names the paths
  that need the binary by behaviour and the leaf base and the binary contract
  by addresses the cut keeps; `stl-import` names no install line and no path
  (`grep` for `machinome\[`, `extra`, `machinome/node/` and `viewers` in each);
  neither is modified.

### Probes

1. **The four portions on a real sync** (`<scratch>/repo/`, the cut of
   Decisions 1 to 7). `uv lock`: "Resolved 187 packages", "Added
   machinome-node-jscad v0.8.1", "-openscad", "-solid2", "-stl". `uv sync
   --python 3.12` on a fresh venv: "Installed 178 packages", eleven
   `__editable__` `.pth` files, each holding its package directory. From
   `/tmp` with the venv's Python: `machinome.node.__path__` is the core's
   `machinome/node`, then eight portion directories; `machinome.node.openscad`
   resolves to `packages/machinome-node-openscad/machinome/node/openscad/__init__.py`,
   its `writer`, `binary`, `leaf` and `renderer` beside it, and
   `machinome.node.solid2`, `.jscad`, `.stl` each to its own directory: a
   portion may be a package directory whose own `__init__.py` sits one level
   below the levels the core defines, and the path extension admits its
   parent. `supported.load(key)` returns each, the classes' `__module__` the
   address; `supported.renderer('openscad')` is an `OpenScadRenderer` from
   `machinome.node.openscad.renderer`; `Solid2Node` subclasses `ScadLeafNode`;
   the core's `machinome/viewers/` holds `__init__.py`, `browser.py`,
   `bundle.py`, and its `machinome/node/` holds none of the eight node types;
   `from machinome.node import OpenScadNode` (and `Solid2Node`, `JScadNode`,
   `StlNode`) raises the root's refusal naming the module, unchanged. In
   `<scratch>/p1/`: `machinome new demo` exits 0 and writes the `Solid2Node`
   starter; `machinome snapshot -o demo-snapshot.png` in it exits 0, logs
   `viewers.openscad - Rendering ...demo-Demo-8a2cc0673b1c.scad`, and writes a
   1920 x 1080 PNG of 21440 bytes: the template's 50 mm cube with its 10 mm
   bore through the top, in Cornfield colours (inspected). The suite's
   `tests/base.py` writes SCAD through the moved writer (probe 6).
2. **A node package absent.** On probe 1's venv, each package's directory
   dropped from `sys.path` before `machinome` is imported (ADR-184's stand-in,
   `<scratch>/absent_probe.py`):
   - with `machinome-node-openscad` absent, `import machinome.node.openscad`,
     `from machinome.node.openscad import OpenScadNode`, `import
     machinome.node.openscad.writer`, `from machinome.node import openscad`,
     `hasattr(machinome.node, 'openscad')`, `supported.load('openscad')`,
     `supported.renderer('openscad')`, `from machinome.node.solid2 import
     Solid2Node` and `supported.load('solid2')` each raise `ExtraUnavailable`
     with `name` `machinome.node.openscad`, `extra` `openscad` and the message
     `the openscad node type (OpenScadNode) needs machinome.node.openscad,
     which is not installed; install it with 'pip install
     "machinome[openscad]"'`; `machinome.node.stl` still imports;
   - with `machinome-node-solid2`, `-jscad` or `-stl` absent, its import raises
     the same refusal for its own key;
   - `machinome snapshot -o refused.png` in `<scratch>/p1/demo` with the
     OpenSCAD package absent (`<scratch>/cli_absent.py`) prints `Error:
     machinome snapshot --renderer openscad needs the openscad extra: the
     openscad node type (OpenScadNode) needs machinome.node.openscad, which is
     not installed; install it with 'pip install "machinome[openscad]"'; or use
     --renderer web`, exits 1 and writes no image;
   - `machinome new demo2` with the OpenSCAD package absent writes the
     `CadQueryNode` starter (`solid2` is refused through the table and
     `cadquery` loads); with it and `machinome-node-cadquery` absent, it writes
     nothing and refuses naming both extras, exit 1.

   On a real uninstall in probe 5's venv (`pip uninstall
   machinome-node-openscad`, then `machinome-node-stl`): `from
   machinome.node.solid2 import Solid2Node`, `import
   machinome.node.openscad.renderer` and `from machinome.node.stl import StlNode`
   raise the same refusals, and `machinome snapshot` prints the same line and
   exits 1 with no image. ADR-184's finder needed no edit.
3. **The archives.** From a clean copy of `<scratch>/repo/`'s tracked files
   (`<scratch>/clean/`), `python -m build` of the four new members and the core:
   exit 0 each. `machinome-node-openscad`'s sdist holds 23 entries and its wheel
   12: `machinome/node/openscad/__init__.py`, `binary.py`, `leaf.py`,
   `renderer.py` and `writer.py`, the three licence files under
   `dist-info/licenses/`, `METADATA`, `WHEEL`, `top_level.txt`, `RECORD`; no
   `machinome/__init__.py` and no `machinome/node/__init__.py`. Each of the
   other three holds 18 and 8, its one module. The sdists hold `LICENSE` (793
   bytes) and the two texts (13419, 17984) as regular files. The core's sdist
   holds 1006 entries and its wheel 114, the third cycle's clean 1015 and 122
   less the eight files and the `openscad/` directory entry, and neither holds
   a moved file but the template `solid2.py`. `twine check --strict` on the ten
   archives: 10 PASSED. The `packages.find` spelling matters: built with
   `include = ["machinome.node"]`, the OpenSCAD wheel holds no module at all;
   with `include = ["machinome.node.openscad"]` (or `"machinome.node*"`), the
   five (`<scratch>/variant/`).
4. **The wheels installed.** A fresh `python3.12 -m venv`, then `pip install`
   with a `--find-links` per built member and the core's wheel,
   `"machinome[openscad]"`, `"machinome[solid2]"`, `"machinome[jscad]"` and
   `"machinome[stl]"`: exit 0; `solidpython2` 2.1.3, `trimesh` 4.4.9. One
   `site-packages/machinome/node/` holds the core's modules, `openscad/`,
   `solid2.py`, `jscad.py` and `stl.py`; `machinome/viewers/` holds
   `__init__.py`, `browser.py`, `bundle.py`. In a project directory, with
   `python -I` (`<scratch>/smoke/smoke.py`): an `OpenScadNode` over a
   `part.scad` holding `module part() { cube([2, 3, 4]); }` and a
   `Solid2Node` returning `cube([2, 3, 4])`, assembled and rendered through
   OpenSCAD, each have an STL of volume 24.0; an `StlNode` over a 2 x 3 x 4 box
   trimesh wrote, 24.0; `supported.renderer('openscad')`'s module file is the
   distribution's. With no `openscad` on the PATH the two SCAD parts write
   their `.scad`, whose last lines are `part();` and `cube(size = [2, 3,
   4]);`. A `JScadNode` raises `FileNotFoundError: ... 'jscad'` at
   `assemble()`, whose materialization launches the command, so without it
   the part can be constructed and not built. Each distribution's
   `requires` is its manifest's (Decision 2).
5. **The SolidPython requirement of `machinome-node-solid2`.** Its module
   imports `solid2` directly, so under `kernel-extras` ("A distribution of the
   set SHALL declare every third-party package its module imports directly")
   it names `solidpython2==2.1.*` beside `machinome-node-openscad~=0.8.1`, as
   `machinome-node-step` names CadQuery beside `machinome-node-cadquery`. The
   install is the same either way (the OpenSCAD package brings it); the
   choice is what the manifest states (Decision 2; Open Questions 3).
6. **The whole suite on the cut tree** (probe 1's venv, `pytest -q -rs -p
   no:cacheprovider` from `packages/machinome/` with the venv's `bin/` first
   on `PATH`, no test edited). It stops at collection: four modules import the
   renderer's former address (`test_markings.py`, `test_snapshot.py`,
   `test_openscad_dependency.py`, and `test_no_class_name_recognition.py`,
   which imports two classes from the third). With
   `--continue-on-collection-errors`: `26 failed, 4554 passed, 20 skipped, 4
   errors, 6842 subtests passed in 489.83s`. The 20 skips are the third
   cycle's (16 the viewer, networkx, the `jscad` command, 2 vendor STEP). The
   26 failures, each the renderer's address, a path or a table this change
   moves:
   - the renderer's address (6): `test_build_publication.py`
     `SweepByDeclarationTest.test_the_renderer_marks_only_a_root_it_does_not_keep_transient`,
     `test_browser_renderer.py` `CaptureDelegationTest.test_browser_failure_never_falls_back_to_openscad`
     (a `patch` string), `test_openscad_node.py`
     `ThePackageTest.test_the_viewer_imports_neither_former_address`
     (`FileNotFoundError` on `machinome/viewers/openscad.py`),
     `TheThreeDoorsTest.test_the_viewer_refuses_with_the_package`
     (`ModuleNotFoundError` for the old address),
     `CountingWriterTest.test_the_binary_for_a_stale_solid2nodes_stl_and_the_renderer`,
     and `test_supported_node_types.py`
     `TheTableTest.test_one_renderer_is_contributed_and_it_is_the_default`
     (the module is `machinome.node.openscad.renderer`);
   - a path (1): `test_openscad_node.py`
     `BinaryTest.test_the_binary_module_imports_no_solidpython`
     (`FileNotFoundError` on `machinome/node/openscad/binary.py`);
   - the scans that expect the core's viewer to reach the family (2):
     `test_expression_type.py`
     `NoExpressionImportTest.test_only_the_viewer_reaches_the_family_package`
     and `test_scad_presentation.py`
     `ImportersTest.test_only_the_viewer_reaches_the_familys_package` (the set
     is now empty);
   - `test_kernel_extras.py` (5): `test_each_extra_lists_what_its_module_needs`
     subtests `openscad`, `solid2`, `jscad`, `stl`, and
     `test_the_solid2_extra_installs_the_openscad_extra`;
   - `test_repository_layout.py` (12): `test_every_sibling_is_in_the_table`,
     the README test and the guide test, four subtests each.

   Green on the cut tree, and so blind to it: `test_core_kernel_free.py`
   (its `KERNELS` lacks `solid2` and its `KERNEL_MODULES` the family, so the
   moved modules leave its core census and enter no other);
   `test_core_names_no_scad.py` (it scans the core's `machinome/` alone, and
   the allowed zones it names no longer exist there);
   `test_docs_structure.py`'s page test (it names six distributions);
   `test_supported_node_types.py`'s `AbsentPackageTest` (it drops `step`
   alone); `test_release_records.py` and the sources test (Decisions 5 and 6
   are applied with the move). `test_core_names_no_split_words.py` and
   `test_node_root_exports_nothing.py` already read every `packages/machinome-*`.
7. **The gate prototyped, red on the base and green on the cut.** The edits of
   Decision 9 to `test_core_kernel_free.py`, `test_core_names_no_scad.py` and
   `test_repository_layout.py`, applied to `<scratch>/basewt/` and to
   `<scratch>/repo/`, run on probe 1's venv. On the base: red, for the stated
   reasons: the core census finds `machinome/node/openscad/__init__.py`,
   `writer.py` and `solid2.py` importing SolidPython; the new census finds the
   family's modules and the viewer importing node modules; the portion census
   finds no family module; `test_each_kernel_module_checks_its_kernel_first`
   raises `KeyError` on the two portion keys; the seams test finds the core's
   family modules naming `machinome.node.openscad`; the SCAD scan reports 6
   modules and 245 occurrences (`machinome/viewers/openscad.py` 65, the
   package's `__init__.py` 57, `leaf.py` 44, `writer.py` 33, `solid2.py` 31,
   `binary.py` 15); the layout gate finds no directory for the four, the core
   holding `openscad/`, `solid2.py`, `jscad.py` and `stl.py`, and
   `machinome/viewers/openscad.py`. On the cut: every one of those green; red
   only the README and guide tests (eight subtests), which the records turn
   green (task group 9).
8. **The manual on the cut tree.** A fresh venv with
   `packages/machinome/docs/requirements.txt` alone, then `sphinx -b html -W
   --keep-going docs <html>` from the cut tree's framework directory: "build
   succeeded", and `reference/api.html` names the four classes. `docs/conf.py`
   needs no edit.
9. **The version bumped from the root** (`<scratch>/bump/`: the root's
   `.bumpversion.cfg` of Decision 6 and the fifteen files it names, a git
   repository). `bump2version --no-commit --no-tag --new-version 0.9.0 patch`:
   exit 0, 41 lines changed in 15 files: the third cycle's 28, the four new
   manifests' `version`, the core's four new pins, and five sibling pins (four
   `machinome~=` and the solid2 package's `machinome-node-openscad~=`); 26
   pins in all. The viewer floors (`machinome-viewer>=0.8.1`) do not move.
10. **The lint.** From the cut tree's framework directory, `flake8
    --max-line-length=89 machinome tests` and the ten `../machinome-*/machinome`
    paths named: 759 lines, the base's 759; 2 E402, both in
    `tests/test_couplings.py`, as at the base.
11. **`scripts/check-dist` prototyped** (Decision 10, in `<scratch>/repo/`).
    The base's script on the cut tree fails "machinome-node-jscad has no smoke
    in scripts/check-dist". The prototype: exit 0, eleven members built, 22
    archives `twine check --strict` PASSED, each member's linked files in its
    sdist as regular files equal to the root's; installed through the core's
    extras from the built archives; the four new lines:
    `machinome-node-jscad 0.8.1 module .../machinome/node/jscad.py part over
    part.js; its STL is rendered by the jscad command, which no package of the
    set installs`; `machinome-node-openscad 0.8.1 module
    .../machinome/node/openscad/__init__.py volume 24.0 through OpenSCAD,
    renderer .../machinome/node/openscad/renderer.py`; `machinome-node-solid2
    0.8.1 module .../machinome/node/solid2.py volume 24.0 through OpenSCAD`;
    `machinome-node-stl 0.8.1 module .../machinome/node/stl.py volume 24.0`;
    the seven earlier rows as at the third cycle; "nothing uploaded".
    `flake8 --max-line-length=89 scripts/check-dist`: 0.

## Goals / Non-Goals

**Goals:**

- `machinome-node-openscad`, `machinome-node-solid2`, `machinome-node-jscad`
  and `machinome-node-stl` founded in ADR-183's shape, each installed by the
  core's extra of the same last name; with the third cycle's four, every node
  type of the table is a package.
- The OpenSCAD snapshot renderer in the OpenSCAD node package, reached through
  the table as before; the core imports no node type and no engine provider.
- Every door that refused a node type by its extra refuses it when its
  distribution is absent, the renderer's and the snapshot command's included.
- Gates that fail if a node module or the renderer drifts back into the core,
  a pin or range drifts, a sibling escapes a scan or a table, or an absent
  package loses its refusal.

**Non-Goals:**

- The viewer seam `machinome.viewer` and the removal of ADR-179's renderer
  column (deferred past 0.8 by the pilot); `machinome/viewers/bundle.py` and
  `browser.py`.
- Any change to a node type's class, a refusal message, the table's keys, the
  writer's output, the renderer's output or its logger's name, a public name
  but the renderer's module, an extra's name or a contract number.
- A leaf contract on the four classes, a version bump, an upload, a push, the
  release job, the workspace's `scripts/setup` and `scripts/dev-env`.

## Decisions

### 1. The shape of the four packages

ADR-183's, with the node package's path:

```
packages/machinome-node-openscad/
├── pyproject.toml
├── README.md
├── LICENSE  -> ../../LICENSE
├── LICENSES -> ../../LICENSES
└── machinome/
    └── node/
        └── openscad/            moved whole by git mv
            ├── __init__.py      the node package's own: OpenScadNode
            ├── binary.py
            ├── leaf.py
            ├── renderer.py      moved by git mv from machinome/viewers/openscad.py
            └── writer.py
```

and `machinome-node-solid2` (`machinome/node/solid2.py`),
`machinome-node-jscad` (`jscad.py`) and `machinome-node-stl` (`stl.py`) as the
third cycle's packages. No `__init__.py` under `machinome/` or
`machinome/node/`: those levels are the core's. The OpenSCAD package's own
`__init__.py` is one level below them, at its address, and ships (probes 1, 3).
No `CREDITS.md` (the four bundle nothing), no `MANIFEST.in` (probe 3), no
`.gitignore` (the root's ignores `/packages/*/build/` and
`/packages/*/*.egg-info/`).

Every moved file is unchanged but one docstring: the OpenSCAD package's
`__init__.py` lists its submodules, and gains, after the `binary` bullet:

```
- `machinome.node.openscad.renderer`: the OpenSCAD snapshot renderer of
  `machinome snapshot`, which the table of supported node types names
  (`machinome.node.supported`, a provisional column).
```

### 2. The four manifests and the four READMEs, verbatim

The third cycle's header and footer, with each package's `name`, `description`,
dependencies and `packages.find`.

`packages/machinome-node-openscad/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-openscad"
version = "0.8.1"
description = "The OpenSCAD node family of Machinome, its SCAD writer and its snapshot renderer"
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
    # SolidPython, the family's kernel: the writer writes SCAD through it and
    # OpenScadNode reads a SCAD module with it. One range for the family:
    # machinome-node-solid2 names SolidPython alike. The OpenSCAD executable
    # itself is no package's to install.
    "solidpython2==2.1.*",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The node package machinome/node/openscad/, which has its own __init__.py,
# with none at machinome/ or machinome/node/, so the core's package path
# admits it.
include = ["machinome.node.openscad"]
namespaces = true
```

`packages/machinome-node-solid2/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-solid2"
version = "0.8.1"
description = "The Solid2Node type of Machinome, a leaf of the OpenSCAD node family rendered with SolidPython"
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
    # The OpenSCAD node family, whose leaf base and binary contract the
    # module imports.
    "machinome-node-openscad~=0.8.1",
    # SolidPython, imported here directly, so named here directly, in the
    # one range machinome-node-openscad states.
    "solidpython2==2.1.*",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The portion, machinome/node/solid2.py, with no __init__.py at either
# level, so the core's package path admits it.
include = ["machinome.node"]
namespaces = true
```

`packages/machinome-node-jscad/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-jscad"
version = "0.8.1"
description = "The JSCAD node type of Machinome"
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
    # Nothing else: the module renders with the jscad command, a Node
    # program no pip package installs.
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The portion, machinome/node/jscad.py, with no __init__.py at either
# level, so the core's package path admits it.
include = ["machinome.node"]
namespaces = true
```

`packages/machinome-node-stl/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "machinome-node-stl"
version = "0.8.1"
description = "The STL node type of Machinome, a committed mesh as a part"
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
    # Meshes; the core pins the range.
    "trimesh",
]

[project.urls]
Homepage = "https://github.com/machinome/machinome"

[tool.setuptools.packages.find]
# The portion, machinome/node/stl.py, with no __init__.py at either
# level, so the core's package path admits it.
include = ["machinome.node"]
namespaces = true
```

`include = ["machinome.node.openscad"]` names the node package, whose own
`__init__.py` makes it a regular package inside the namespace portions
`machinome` and `machinome.node`; `include = ["machinome.node"]` would ship
nothing for it (probe 3). The three module packages keep the third cycle's
`include = ["machinome.node"]`. No package names the B-rep or the mesh
engine: their modules import neither. SolidPython's range is written in two
manifests and held equal by a test (Decision 9), as CadQuery's is.

The READMEs:

```markdown
# machinome-node-openscad

The OpenSCAD node family of [Machinome](https://github.com/machinome/machinome):
the package `machinome.node.openscad`, whose `OpenScadNode` is a part
written as an [OpenSCAD](https://openscad.org) module, with the family's
leaf base, the writer of a presentation's SCAD through
[SolidPython](https://github.com/jeff-dh/SolidPython), the contract of the
`openscad` executable, and the OpenSCAD renderer of `machinome snapshot`.
The executable itself is installed apart, from OpenSCAD.

## Install

    pip install "machinome[openscad]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

```markdown
# machinome-node-solid2

The SolidPython node type of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.solid2`, whose `Solid2Node` is a part modelled
with [SolidPython](https://github.com/jeff-dh/SolidPython), a leaf of the
OpenSCAD node family whose STL OpenSCAD renders from its SCAD.

## Install

    pip install "machinome[solid2]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

```markdown
# machinome-node-jscad

The JSCAD node type of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.jscad`, whose `JScadNode` is a part written in
[JSCAD](https://openjscad.xyz), its STL rendered by the `jscad` command,
which is installed apart, with Node.

## Install

    pip install "machinome[jscad]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

```markdown
# machinome-node-stl

The STL node type of [Machinome](https://github.com/machinome/machinome):
the module `machinome.node.stl`, whose `StlNode` is a part read from a
committed STL file, one body of it selected by index, corrected by the
node's own code and admitted only when it is a closed solid.

## Install

    pip install "machinome[stl]"

## Manual

<https://machinome.readthedocs.io>

## Licence

GPL-2.0-or-later or CERN-OHL-S-2.0-or-later, at the recipient's choice; the
texts are in `LICENSE` and `LICENSES/`.
```

Each shows the package and adds nothing, as the earlier siblings' do. The eight
files as probed are `<scratch>/drafts/machinome-node-<x>/`.

### 3. The renderer's move

`git mv packages/machinome/machinome/viewers/openscad.py
packages/machinome-node-openscad/machinome/node/openscad/renderer.py`, the
file unchanged, after the package directory's own move. Its new address is
`machinome.node.openscad.renderer`: a module of the package whose writer and
binary it draws with, named for what the table's column calls it and for its
class, `OpenScadRenderer`. Its logger keeps the name `viewers.openscad`: the
name is part of the renderer's output (every log line carries it, and
`test_snapshot.py` reads it with `assertLogs`), which this change keeps.

In `machinome/node/supported.py` the row's string becomes
`'machinome.node.openscad.renderer.OpenScadRenderer'`; nothing else in the
module changes, its docstring's paragraph on the provisional column included.
`renderer(name)` still loads the `openscad` node type first, so an absent
package is refused before the renderer's module is asked for (probe 2).

The core's `machinome/viewers/` keeps `__init__.py`, `bundle.py` and
`browser.py`, unchanged. ADR-179's renderer column stays provisional as it is:
the viewer seam is deferred past 0.8 by the pilot and is not this campaign's;
the move changes which distribution holds the renderer, not how the core
reaches it.

The alternative, the renderer shipped by `machinome-node-openscad` at its old
address `machinome.viewers.openscad` as a second portion, would make the
core's `machinome.viewers` a package that extends its path, a seam of its own
that the deferred viewer cycle owns, and give one distribution two portions in
two packages. Rejected.

### 4. The core's manifest

In `packages/machinome/pyproject.toml`, the `dependencies` comment becomes:

```toml
    # No CAD kernel and no node type is required: the node types (the
    # extras `cadquery`, `build123d`, `step`, `molejo`, `openscad`,
    # `solid2`, `jscad` and `stl`), the B-rep engine (the extra `brep`) and
    # the mesh engine (the extra `mesh`) are the extras below, each named by
    # the last component of the address of the module that needs it
    # (OpenSpec changes `lean-install`, `mesh-engine`, `openscad-out` and
    # `brep-mesh`).
```

and the block from "# The OpenSCAD node family" to the line before `all =`
becomes:

```toml
# The node types that need no B-rep engine, each named by the last
# component of its address and each the distribution
# machinome-node-<name>.
#
# The OpenSCAD node family (`machinome.node.openscad`: OpenScadNode, the
# OpenSCAD writer and the OpenSCAD snapshot renderer), which writes SCAD
# through SolidPython; the OpenSCAD executable itself is no extra's to
# install.
openscad = [
    "machinome-node-openscad~=0.8.1",
]
# `machinome.node.solid2` (Solid2Node), which renders with SolidPython over
# the OpenSCAD node family and requires it.
solid2 = [
    "machinome-node-solid2~=0.8.1",
]
# `machinome.node.jscad` (JScadNode), which runs the `jscad` command, a Node
# program no pip extra installs.
jscad = [
    "machinome-node-jscad~=0.8.1",
]
# `machinome.node.stl` (StlNode), which reads meshes with trimesh, which the
# core requires.
stl = [
    "machinome-node-stl~=0.8.1",
]
```

`solid2` no longer names `machinome[openscad]`: its distribution requires the
OpenSCAD package itself, so `pip install "machinome[solid2]"` still installs
it (probe 4). `all`, `dev` and every other extra are unchanged; `git diff`
shows the two hunks.

A bare `pip install machinome` now carries no node type: before the cut it
carried `machinome.node.jscad` and `machinome.node.stl`, whose extras
installed nothing. A project of `StlNode` or `JScadNode` parts installed
without its extra meets, at its import line, `the stl node type (StlNode)
needs machinome.node.stl, which is not installed; install it with 'pip install
"machinome[stl]"'` (probe 2). This is the pilot's ruling of 4 October 2026
taking effect, and the reason `root-cleanup` declared the two extras; it is
recorded as a **BREAKING** line in the proposal and the changelog, and is Open
Questions 1.

Reviewed before the planning commit (10 October 2026): the bare install's
loss of the two node types is accepted by the orchestrator as the pilot's
ruling of 4 October 2026 taking effect, with its refusal naming the extra at
the import line; reported to the pilot. Every recommendation of the Open
Questions is taken: no new ADR, SolidPython named directly by the solid2
package, the SCAD rows writing SCAD where OpenSCAD is absent, the module
name `renderer`.

### 5. The workspace: sources and lock

The root `pyproject.toml`'s `[tool.uv.sources]` gains, in alphabetical order
among the node packages:

```toml
machinome-node-jscad = { workspace = true }
machinome-node-openscad = { workspace = true }
machinome-node-solid2 = { workspace = true }
machinome-node-stl = { workspace = true }
```

so the table reads build123d, cadquery, jscad, molejo, openscad, solid2, step,
stl. `uv lock` regenerates `uv.lock` (probe 1: 187 packages); `uv sync
--python 3.12` installs the four editable in compat mode (eleven `.pth`
lines). Nothing else in the root manifest or the root `.gitignore` changes.

### 6. One version for the set: eight tables

The root `.bumpversion.cfg` gains, after the molejo package's tables, for each
of `openscad`, `solid2`, `jscad` and `stl` in that order:

```ini
[bumpversion:file(version):packages/machinome-node-<x>/pyproject.toml]
search = version = "{current_version}"
replace = version = "{new_version}"

[bumpversion:file(pins):packages/machinome-node-<x>/pyproject.toml]
search = ~={current_version}"
replace = ~={new_version}"
```

The pin search is the node packages' (`~={current_version}"`), which matches
`"machinome~=0.8.1"` and `"machinome-node-openscad~=0.8.1"` and not
`"solidpython2==2.1.*"`. Probe 9 moved the 41 statements and nothing else. No
comment.

### 7. The lint ignores

`packages/machinome/setup.cfg`'s two entries become, in place,
`../machinome-node-openscad/machinome/node/openscad/__init__.py:E402` and
`../machinome-node-solid2/machinome/node/solid2.py:E402`. CI's and the
Makefile's `../machinome-*/machinome` glob already reads the four packages.
Probe 10: 759 lines, the base's.

### 8. The manual's path

No edit: `docs/conf.py` puts every `../../machinome-*` directory after the
core's on `sys.path` (the third cycle's Decision 6), so autodoc imports the
four node types as portions (probe 8).

### 9. The gate, red first

Each test is written or corrected before the move and run, its expected red
stated. "The move" below is task group 3.

- **`tests/test_repository_layout.py`.** `EXTENSIONS` gains
  `'machinome-node-openscad': ('machinome.node.openscad', 'openscad')`,
  `'machinome-node-solid2': ('machinome.node.solid2', 'solid2')`,
  `'machinome-node-jscad': ('machinome.node.jscad', 'jscad')` and
  `'machinome-node-stl': ('machinome.node.stl', 'stl')`. A second table and a
  helper name the package-directory portion:

  ```python
  #: The extension packages whose portion is a package directory at its
  #: address, with its own `__init__.py` below the levels the core defines,
  #: and the modules it holds (`cut-the-mesh-nodes`).
  PACKAGE_PORTIONS = {
      'machinome-node-openscad': ('__init__', 'binary', 'leaf', 'renderer',
                                  'writer'),
  }


  def portion_files(name, address):
      """The files an extension package ships under `machinome/`: its module
      at its address, or its package directory's modules."""
      base = address.replace('.', '/')
      if name in PACKAGE_PORTIONS:
          return [f'{base}/{module}.py' for module in PACKAGE_PORTIONS[name]]
      return [f'{base}.py']
  ```

  `test_each_extension_directory_holds_only_what_distinguishes_it` lists
  `portion_files(name, address)` in place of the one module, and admits as the
  only `__init__.py` under `machinome/` the package portion's own,
  `<address path>/__init__.py`; `test_each_extension_manifest_is_a_portion_of_the_set`
  expects `include` to be the address itself for a package portion and its
  package otherwise; `test_each_portion_resolves_from_its_package` compares the
  imported module's file with `portion_files(name, address)[0]` (the
  package's `__init__.py`); `test_the_core_node_package_holds_no_extension_module`
  also refuses a directory named for the address. Two new tests:
  `test_the_core_node_package_holds_no_node_type` (no
  `machinome/node/<key>.py` and no `machinome/node/<key>/` for any key of
  `machinome.node.supported.NODE_TYPES`) and
  `test_the_core_viewers_hold_no_node_type_s_renderer` (the core's
  `machinome/viewers/` holds exactly `__init__.py`, `browser.py` and
  `bundle.py`, `__pycache__` aside). The module docstring names the four.
  Reds at the base (probe 7): the four rows of the four per-package tests (no
  directory, no manifest, no README, the module resolving under
  `packages/machinome/`), the core-node tests (`openscad/`, `solid2.py`,
  `jscad.py`, `stl.py`), the viewers test (`openscad.py`). Already generic
  and red at the move: the README and guide tests (probe 6).
- **`tests/test_kernel_extras.py`**: `EXTRAS['openscad']`, `['solid2']`,
  `['jscad']` and `['stl']` become `{f'machinome-node-<x>~={VERSION}'}`, the
  `root-cleanup` comment above `jscad` and `stl` replaced by one naming this
  change; `PACKAGE_REQUIREMENTS` gains
  `'machinome-node-openscad': {f'machinome~={VERSION}', 'solidpython2==2.1.*'}`,
  `'machinome-node-solid2': {f'machinome~={VERSION}',
  f'machinome-node-openscad~={VERSION}', 'solidpython2==2.1.*'}`,
  `'machinome-node-jscad': {f'machinome~={VERSION}'}` and
  `'machinome-node-stl': {f'machinome~={VERSION}', 'trimesh'}`;
  `NODE_PACKAGES` keeps every `machinome-node-*` name, and a new
  `BREP_NODE_PACKAGES` names the four over the B-rep engine, which
  `test_every_node_package_requires_the_brep_engine` reads (its name kept);
  `test_no_node_extra_includes_the_mesh_engine` reads all eight node extras;
  `test_the_solid2_extra_installs_the_openscad_extra` becomes
  `test_the_solid2_package_requires_the_openscad_package` (the solid2
  manifest names `machinome-node-openscad~=<version>`, and the core's `solid2`
  extra names its own distribution alone); a new
  `test_solidpython_carries_one_range_wherever_it_is_named` reads the core and
  every sibling manifest and requires `{'==2.1.*'}`, as CadQuery's test does.
  The docstring names the four. Reds at the base: the four `EXTRAS` subtests
  (the core lists SolidPython, `machinome[openscad]` and nothing), the
  requirements test (`FileNotFoundError` on the four manifests), the solid2
  test (no manifest), the SolidPython test (named only in the core, once), the
  lock test (no node package of the four locked).
- **`tests/test_core_kernel_free.py`**: `KERNELS` gains `solid2` and
  `KERNEL_MODULES` `machinome.node.openscad` and `machinome.node.solid2`; a new
  tuple `EXTENSION_MODULES` names the eight node modules and the two engine
  providers, and a new test `test_the_core_imports_no_node_type_and_no_engine_provider`
  finds, among the core's import statements, any of them or a name beneath
  one only in the two templates (`machinome.node.cadquery` and
  `.CadQueryNode`, `machinome.node.solid2` and `.Solid2Node`). The core census
  of `test_kernels_are_imported_only_by_their_modules` expects the two
  templates (`cadquery`, `solid2`);
  `test_the_extension_packages_import_only_their_kernels` also expects
  `machinome-node-openscad/machinome/node/openscad/__init__.py` and `writer.py`
  and `machinome-node-solid2/machinome/node/solid2.py`, each `['solid2']`;
  `EXTRA_OF` gains the OpenSCAD package's `__init__.py` (`openscad`) and the
  solid2 module (`solid2`). `kernel_modules_named` counts a name beneath a
  kernel module as that module, reads every string constant, and does not
  count a module of a node package naming its own package (the OpenSCAD
  package's modules name one another); `SEAMS` gains the template `solid2.py`
  (`machinome.node.solid2`), the solid2 module
  (`machinome.node.openscad`, with the comment that `machinome-node-solid2`
  requires `machinome-node-openscad`) and `machinome/node/supported.py`
  (`machinome.node.openscad`, the renderer row); the seams test asserts the
  solid2 module's and the table's entries exactly, and `TABLE_READERS` gains
  `machinome/manager/snapshot.py` and `machinome/manager/new.py`. The
  docstring names the four and the census. Reds at the base (probe 7): the
  core census (it finds the package's `__init__.py`, `writer.py` and
  `solid2.py`), the new census (the family's modules and the viewer), the
  portion census (no family module), the `require_extra` test (`KeyError` on
  the two portion keys), the seams test (the core's family modules name the
  package; the solid2 portion key is absent).
- **`tests/test_core_names_no_scad.py`**: the allowed zones become the
  family's two distributions, `ALLOWED_PACKAGES = {'machinome-node-openscad',
  'machinome-node-solid2'}` (the first spelled in pieces, as the file spells
  the word), and the core's `ALLOWED_MODULES = {'machinome/node/supported.py'}`;
  `scan(root, prefix='')` prefixes each path, and the gate merges `scan()` of
  the core with `scan(package, prefix=f'{package.name}/')` of every
  `packages/machinome-*`; `test_the_allowed_zones` asserts the two packages'
  paths allowed and the core's former zones (`machinome/node/openscad/...`,
  `machinome/node/solid2.py`, `machinome/viewers/openscad.py`) and
  `machinome-node-stl/machinome/node/stl.py` not. The docstring states the
  zones. Red at the base (probe 7): 6 modules, 245 occurrences. Its blind spot
  on the moved tree is shown once after the move (task 4.6): the word planted
  in a comment of the moved `stl.py` fails the gate naming
  `machinome-node-stl/machinome/node/stl.py`; the plant is removed.
- **The scans that expected the viewer to reach the family**:
  `test_expression_type.py`'s `BINARY_REACHES` and `test_scad_presentation.py`'s
  `ENGINE_REACHES` become empty sets, their comments saying no core module
  reaches the family's package since the renderer moved into it, and the two
  tests are renamed `test_no_core_module_reaches_the_family_package` and
  `test_no_core_module_reaches_the_familys_package`. Red at the base: each
  finds `machinome/viewers/openscad.py`.
- **The renderer's address in the suite.** Every spelling of
  `machinome.viewers.openscad` becomes `machinome.node.openscad.renderer`:
  the imports of `test_snapshot.py` (three) and its two `patch` strings,
  `test_openscad_dependency.py`'s two imports (`from machinome.node.openscad
  import renderer as openscad_viewer`) and its `patch` string,
  `test_markings.py`'s import, `test_build_publication.py`'s,
  `test_browser_renderer.py`'s `patch` string, and `test_openscad_node.py`'s
  import at `CountingWriterTest` and its refusal door
  (`import machinome.node.openscad.renderer`, still refused with `R1`, the
  test renamed `test_the_renderer_refuses_with_the_package`).
  `test_openscad_node.py`'s two file reads take the module's file from
  `importlib.util.find_spec('machinome.node.openscad.renderer').origin` and
  `find_spec('machinome.node.openscad.binary').origin`, as the third cycle
  repointed `test_leaf_contract_reach.py`; the first test is renamed
  `test_the_renderer_imports_neither_former_address`. The `assertLogs`
  channel `viewers.openscad` is unchanged (Decision 3). Red at the base: each
  module importing the new address fails to collect or to import
  (`ModuleNotFoundError: No module named 'machinome.node.openscad.renderer'`).
- **`tests/test_supported_node_types.py`**:
  `test_one_renderer_is_contributed_and_it_is_the_default` expects the module
  `machinome.node.openscad.renderer` (red at the base: it is
  `machinome.viewers.openscad`). `AbsentPackageTest` is generalised over a
  table of the absent package and its doors, its refusal built from the key
  (`the <key> node type (<classes>) needs machinome.node.<key>, ...`): the
  step rows as they are; for each of `openscad`, `solid2`, `jscad` and `stl`
  the four doors (`import`, `from-module` with the row's class, `from-root`,
  `hasattr`); with `machinome-node-openscad` dropped, `import
  machinome.node.openscad.renderer`, `supported.renderer('openscad')` and
  `from machinome.node.solid2 import Solid2Node`, each refused naming
  `openscad`; and `test_the_other_node_packages_still_import` also importing
  `machinome.node.stl` with the OpenSCAD package dropped. A new
  `test_the_snapshot_refuses_an_absent_openscad_package` runs `machinome
  snapshot -o <tmp>/x.png` in a temporary project directory through a
  subprocess that drops the OpenSCAD package's directory and calls
  `machinome.cli.manage()`, and expects exit 1, standard error the line of
  probe 2, and no image. Reds at the base: every door passes (the modules are
  in the core); the snapshot command renders. Green after the move with no
  edit to the finder (probe 2).
- **`tests/test_docs_structure.py`**: the installation page's distributions
  test names the ten distributions. Red: the page names six.
- **`tests/test_release_records.py`**: unchanged; its member, pin and
  bumped-from-root tests read every `packages/*/pyproject.toml`. After the
  founding the bumped-from-root test is red (four manifests without a table);
  the pin test's red is shown once by planting `machinome-node-openscad>=0.8.1`
  in the solid2 manifest.
- **`tests/test_core_names_no_split_words.py`** and
  **`tests/test_node_root_exports_nothing.py`**: unchanged; both already read
  every `packages/machinome-*`. That they read the moved modules is shown
  once after the move (task 4.6): the mesh-quality word planted in a comment
  of the moved `jscad.py` fails the split-words gate naming
  `machinome/node/jscad.py`; the plant is removed.
- **`scripts/check-dist`** is not in the suite. Red first: with the four
  directories founded and no rows, it fails "machinome-node-jscad has no
  smoke in scripts/check-dist" (probe 11).

What stays a blind spot, recorded: the gate reads a checkout; an installed set
is proved by `check-dist` and by the bench venv. The absence of a package is
stood in for by its directory dropped from `sys.path`, which the editable
install allows; a wheel uninstall is probe 2's. The core-only scans that
state a rule of the core (`test_no_class_name_recognition.py`,
`test_leaf_capability_set.py`, `test_machinome_identity.py`) stop reading the
four moved modules, which are no longer the core.

### 10. `scripts/check-dist`: a template and four rows

The script gains, after the `NODE` template's `node_smoke`, a template for a
node package over no B-rep engine, verbatim:

```python
#: The smoke of a node package over no B-rep engine: its module imported at
#: its address, the files it ships under `machinome/` owned by its own
#: distribution inside the venv, its version and pins the core's, then one
#: part of its node type in a new project directory under the temporary
#: directory, rendered to its STL where the part's external program is on
#: the PATH, whose volume trimesh reads, and otherwise built as far as the
#: program allows; its licence.
MESH_NODE = string.Template('''
import importlib
import importlib.metadata as metadata
import os
import shutil
import sys
import tempfile
from pathlib import Path
import trimesh
from machinome.node.base import StlRenderStart
module = importlib.import_module('machinome.node.$node')
distribution = metadata.distribution('$name')
version = metadata.version('machinome')
assert distribution.version == version, (distribution.version, version)
files = [str(path) for path in distribution.files]
shipped = sorted(path for path in files
                 if path.startswith('machinome/') and path.endswith('.py'))
assert shipped == $shipped, shipped
owned = Path(distribution.locate_file(shipped[0])).resolve()
assert owned == Path(module.__file__).resolve(), (owned, module.__file__)
assert owned.is_relative_to(Path(VENV).resolve()), owned
for pin in $pins:
    assert pin.format(version=version) in distribution.requires, (
        pin, distribution.requires)
project = tempfile.mkdtemp(prefix='$name-', dir=os.getcwd())
with open(os.path.join(project, 'pyproject.toml'), 'w') as stream:
    stream.write('[tool.machinome]\\n')
with open(os.path.join(project, 'parts.py'), 'w') as stream:
    stream.write($parts)
sys.path.insert(0, project)
os.chdir(project)


def stl_volume(node):
    """Render `node`'s STL, waiting on its renderer, and read its volume."""
    while True:
        try:
            node.trigger_stl()
            break
        except StlRenderStart as job:
            job.wait()
    return trimesh.load(node.stl_file).volume


$operation
''')

#: The one line such a smoke prints last.
MESH_NODE_LINE = '''
print('$name', distribution.version, 'module', module.__file__, result)
'''


def mesh_node_smoke(name, node, shipped, pins, parts, operation):
    """The code of a node package's smoke over no B-rep engine: `shipped`
    the files it ships under `machinome/`, `pins` its requirements on the
    set (`{version}` standing for the version), `parts` the source of the
    project's `parts.py`, one class `Part`; `operation` sets `result`."""
    values = dict(name=name, node=node, shipped=repr(sorted(shipped)),
                  pins=repr(pins), parts=repr(parts.lstrip()),
                  operation=operation.strip())
    return (MESH_NODE.substitute(values) + LICENCES.substitute(values)
            + string.Template(MESH_NODE_LINE).substitute(values))
```

and, after the molejo row, four rows, verbatim:

```python
    'machinome-node-openscad': {
        'through': 'openscad',
        'extras': [],
        'code': mesh_node_smoke(
            'machinome-node-openscad', 'openscad',
            [f'machinome/node/openscad/{module}.py' for module in
             ('__init__', 'binary', 'leaf', 'renderer', 'writer')],
            ['machinome~={version}'],
            '''
from machinome.node.openscad import OpenScadNode


class Part(OpenScadNode):
    scad_source = 'part.scad'
''',
            '''
with open('part.scad', 'w') as stream:
    stream.write('module part() { cube([2, 3, 4]); }\\n')
import parts
node = parts.Part()
node.assemble()
if shutil.which('openscad'):
    volume = stl_volume(node)
    assert abs(volume - 24) < 1e-6, volume
    result = f'volume {volume} through OpenSCAD'
else:
    node.generate_scad()
    last = Path(node.scad_file).read_text().strip().splitlines()[-1]
    assert last == 'part();', last
    result = f'SCAD {last!r} written, no openscad on the PATH'
from machinome.node import supported
renderer = supported.renderer('openscad')
assert type(renderer).__module__ == 'machinome.node.openscad.renderer'
drawn = Path(sys.modules[type(renderer).__module__].__file__).resolve()
assert drawn == Path(distribution.locate_file(
    'machinome/node/openscad/renderer.py')).resolve(), drawn
result += f', renderer {drawn}'
'''),
        'commands': [],
    },
    'machinome-node-solid2': {
        'through': 'solid2',
        'extras': [],
        'code': mesh_node_smoke(
            'machinome-node-solid2', 'solid2',
            ['machinome/node/solid2.py'],
            ['machinome~={version}', 'machinome-node-openscad~={version}'],
            '''
from solid2 import cube
from machinome.node.solid2 import Solid2Node


class Part(Solid2Node):
    def render(self):
        return cube([2, 3, 4])
''',
            '''
import parts
node = parts.Part()
node.assemble()
if shutil.which('openscad'):
    volume = stl_volume(node)
    assert abs(volume - 24) < 1e-6, volume
    result = f'volume {volume} through OpenSCAD'
else:
    node.generate_scad()
    last = Path(node.scad_file).read_text().strip().splitlines()[-1]
    assert last == 'cube(size = [2, 3, 4]);', last
    result = f'SCAD {last!r} written, no openscad on the PATH'
'''),
        'commands': [],
    },
    'machinome-node-jscad': {
        'through': 'jscad',
        'extras': [],
        'code': mesh_node_smoke(
            'machinome-node-jscad', 'jscad',
            ['machinome/node/jscad.py'],
            ['machinome~={version}'],
            '''
from machinome.node.jscad import JScadNode


class Part(JScadNode):
    jscad_source = 'part.js'
''',
            '''
with open('part.js', 'w') as stream:
    stream.write('module.exports = { main: () => null }\\n')
import parts
node = parts.Part()
source = Path(node.get_source_file()).resolve()
assert source == Path(project, 'part.js').resolve(), source
assert node.stl_file.endswith('.stl'), node.stl_file
result = (f'part over {source.name}; its STL is rendered by the jscad '
          'command, which no package of the set installs')
'''),
        'commands': [],
    },
    'machinome-node-stl': {
        'through': 'stl',
        'extras': [],
        'code': mesh_node_smoke(
            'machinome-node-stl', 'stl',
            ['machinome/node/stl.py'],
            ['machinome~={version}'],
            '''
from machinome.node.stl import StlNode


class Part(StlNode):
    stl_source = 'box.stl'
''',
            '''
trimesh.creation.box([2, 3, 4]).export('box.stl')
import parts
node = parts.Part()
node.assemble()
volume = stl_volume(node)
assert abs(volume - 24) < 1e-6, volume
result = f'volume {volume}'
'''),
        'commands': [],
    },
```

The core's and the earlier rows are unchanged (`git diff` shows no line of
them changed): the core's row keeps `[openscad,stl]` and its two imports, which
now install and import the sibling distributions. How each part is rendered,
and why:

- `openscad` and `solid2`: through OpenSCAD where `openscad` is on the PATH
  (the pilot's machine, the bench; volume 24.0), else the part's SCAD written
  and its last line checked (`part();`, `cube(size = [2, 3, 4]);`). CI's
  `dist` job installs no OpenSCAD and the script must pass there; making it
  install OpenSCAD is Open Questions 4. The script's line says which ran.
- `stl`: always rendered: the node writes its own artifact with trimesh, a
  dependency of the core.
- `jscad`: constructed only. Its materialization launches the `jscad`
  command, a Node program no environment of the set installs (the suite
  skips its integration test for the same reason), so `assemble()` raises
  `FileNotFoundError` (probe 4). The smoke asserts the part resolves its
  `.js` source and names its STL, and its line says the STL is the command's.

### 11. The records and the manual; the ADR question

- **`HISTORY.rst`**, under `Unreleased`, after the third cycle's entry:

  ```
  * **The OpenSCAD, SolidPython, JSCAD and STL node types are PACKAGES of
    their own.** ``machinome-node-openscad`` ships the package
    ``machinome.node.openscad`` and the OpenSCAD snapshot renderer, moved from
    ``machinome.viewers.openscad`` to ``machinome.node.openscad.renderer``;
    ``machinome-node-solid2``, ``machinome-node-jscad`` and
    ``machinome-node-stl`` ship ``machinome.node.<name>``, each a namespace
    portion in its own directory under ``packages/``;
    ``machinome-node-solid2`` requires ``machinome-node-openscad``. The
    framework's ``openscad``, ``solid2``, ``jscad`` and ``stl`` extras install
    them, and the framework imports no node type and no engine. A bare
    install carries no node type: a project of ``StlNode`` or ``JScadNode``
    parts names ``machinome[stl]`` or ``machinome[jscad]``, as the refusal at
    its import says. Every other address, every extra and every message is
    unchanged. Change ``cut-the-mesh-nodes`` (ADR-179 and ADR-183 amended).
  ```

- **`docs/project/changelog.rst`**, under `Unreleased`, after the B-rep node
  types' bullet:

  ```
  * **Every node type is a package of its own.** ``machinome[openscad]``,
    ``machinome[solid2]``, ``machinome[jscad]`` and ``machinome[stl]``
    install the distributions ``machinome-node-openscad``, ``-solid2``,
    ``-jscad`` and ``-stl``. A project of ``StlNode`` or ``JScadNode`` parts,
    whose modules came with the framework before, now names the extra:
    ``pip install "machinome[stl]"``; without it, the import names that line.
  ```

- **`docs/start/install.rst`**: the third cell of the `openscad` row becomes
  "the package ``machinome-node-openscad``, with SolidPython, for
  ``OpenScadNode``, the OpenSCAD writer and the OpenSCAD snapshot renderer of
  ``machinome snapshot``"; of `solid2`, "the package
  ``machinome-node-solid2``, with SolidPython, for ``Solid2Node``; it installs
  ``machinome-node-openscad`` too"; of `jscad`, "the package
  ``machinome-node-jscad``, for ``JScadNode``, which runs the ``jscad``
  command from npm, which no Python package installs"; of `stl`, "the package
  ``machinome-node-stl``, for ``StlNode``, which reads with trimesh, which
  comes with the package". The paragraph's first sentence "``machinome[jscad]``
  and ``machinome[stl]`` install nothing today; they exist so that ... their
  own." becomes "``machinome[jscad]`` and ``machinome[stl]`` install their
  node types' packages and no kernel; a bare install carries no node type."
  "The CAD kernels, SolidPython and the mesh engine are extras" becomes "Its
  node types, the CAD kernels, SolidPython and the engines are extras". The
  install section's "or ``mesh`` for a project whose parts are all OpenSCAD,
  JSCAD or STL" becomes "or, for a project of STL parts, ``stl`` with
  ``mesh``", its example `"machinome[stl,mesh]"`. "Packages and licences"'
  first sentence becomes "The framework is the package ``machinome``, with
  its engines and its node types in packages of their own that its extras
  install (``machinome-engine-brep``, ``machinome-engine-mesh``,
  ``machinome-node-cadquery``, ``machinome-node-build123d``,
  ``machinome-node-step``, ``machinome-node-molejo``,
  ``machinome-node-openscad``, ``machinome-node-solid2``,
  ``machinome-node-jscad`` and ``machinome-node-stl``), all licensed
  |framework_licence|, at the recipient's choice." Each rewrapped at the page's
  width; nothing else changes.
- **`docs/howto/backends.rst`**: the `JScadNode` row's last cell becomes "the
  ``jscad`` command and ``machinome[jscad]``", the `StlNode` row's
  "``machinome[stl]`` (:doc:`imported-parts`)". Nothing else changes;
  `docs/reference/cli.rst` and `docs/reference/api.rst` need no edit.
- **`docs/architecture.md`**: the extras sentence's "`[openscad]` and
  `[solid2]` (SolidPython, ...), `[jscad]` and `[stl]`, which install nothing
  (...)" becomes "`[openscad]`, `[solid2]`, `[jscad]` and `[stl]` for the node
  types that need no B-rep engine (the distributions
  `machinome-node-openscad`, with SolidPython, `machinome-node-solid2`, which
  requires it, and `machinome-node-jscad` and `machinome-node-stl`, which
  install no kernel)"; the family paragraph's "The OpenSCAD snapshot renderer
  stays at `machinome/viewers/openscad.py` until the viewer cycle and imports
  the package's writer and binary directly. Nothing outside the family, that
  module and the table of supported node types names the technology: a token
  scan of `machinome/` in the suite (`tests/test_core_names_no_scad.py`) is
  the gate." becomes "The OpenSCAD snapshot renderer is the package's module
  `machinome.node.openscad.renderer`, which the table of supported node types
  names in its provisional renderer column, and imports the package's writer
  and binary directly. The package is the distribution
  `machinome-node-openscad`, and `Solid2Node` the distribution
  `machinome-node-solid2`. Nothing outside those two distributions and the
  table names the technology: a token scan of the framework's `machinome/` and
  every extension package's in the suite (`tests/test_core_names_no_scad.py`)
  is the gate." In the Map, the OpenSCAD row becomes "OpenSCAD node family,
  the distributions `machinome-node-openscad` and `machinome-node-solid2`" |
  "the repository's `packages/machinome-node-openscad/`
  (`machinome/node/openscad/`: `__init__.py` `OpenScadNode`, `leaf.py`
  `ScadLeafNode`, `writer.py`, `binary.py`, `renderer.py` the OpenSCAD
  snapshot renderer) and `packages/machinome-node-solid2/`
  (`machinome/node/solid2.py`: `Solid2Node`, `adopt`)" | `openscad-node`,
  `openscad-dependency`, `kernel-extras` | "046, 102, 172, 173, 177, 178, 179,
  183"; a row after it, "JSCAD and STL node types, the distributions
  `machinome-node-jscad` and `machinome-node-stl`" | "the repository's
  `packages/machinome-node-<x>/` (`machinome/node/<x>.py`)" | `node-model`,
  `kernel-extras`, `stl-import` | "169, 181, 183"; the Node model row's "the
  four node types over the B-rep engine in their own distributions, row
  below" becomes "every node type in its own distribution, rows below"; the
  viewer row's code drops `viewers/openscad.py`.
- **The root `README.md`**: four rows after the molejo package's:

  ```markdown
  | [`machinome-node-openscad`](packages/machinome-node-openscad/) | The OpenSCAD node family, `machinome.node.openscad`, with its SCAD writer and the OpenSCAD snapshot renderer; installed by `machinome[openscad]`. |
  | [`machinome-node-solid2`](packages/machinome-node-solid2/) | The SolidPython node type, `machinome.node.solid2`; installed by `machinome[solid2]`. |
  | [`machinome-node-jscad`](packages/machinome-node-jscad/) | The JSCAD node type, `machinome.node.jscad`; installed by `machinome[jscad]`. |
  | [`machinome-node-stl`](packages/machinome-node-stl/) | The STL node type, `machinome.node.stl`; installed by `machinome[stl]`. |
  ```

- **`CONTRIBUTING.rst`**: the pip block becomes

  ```
      $ pip install --config-settings editable_mode=compat \
          -e packages/machinome-engine-brep -e packages/machinome-engine-mesh \
          -e packages/machinome-node-cadquery -e packages/machinome-node-build123d \
          -e packages/machinome-node-step -e packages/machinome-node-molejo \
          -e packages/machinome-node-openscad -e packages/machinome-node-solid2 \
          -e packages/machinome-node-jscad -e packages/machinome-node-stl \
          -e "packages/machinome[dev]"
  ```

  Nothing else changes. The framework's `README.rst` names the extras and no
  distribution, and is unchanged.
- **The ADR question: no new ADR; ADR-179 and ADR-183 amended.** The shape of
  the four packages is ADR-183's, which foresaw "the eight node packages of
  the later cycles"; a package-directory portion holds no `__init__.py` at a
  level the core defines, which is ADR-183's wording; their refusal is
  ADR-184's, which said a node type of the table "is refused when absent with
  no other edit" (probe 2). What no ADR yet says is the renderer's home:
  ADR-179's consequence says the viewer cycle moves
  `machinome/viewers/openscad.py`, and ADR-177 says the renderer stays there.
  So, written by the applier and reviewed with the implementation:
  - ADR-179 gains a section "Amendment (2026-10-10)", as its 2026-10-05 one:
    the OpenSCAD renderer's module is `machinome.node.openscad.renderer`,
    shipped by `machinome-node-openscad` (change `cut-the-mesh-nodes`); the
    row names it; the column stays provisional and the viewer cycle replaces
    it with the seam `machinome.viewer`, now moving the renderer from the
    OpenSCAD node package; the core imports no node package. Its status line
    adds "the renderer's module moved 2026-10-10 (amendment below)", and its
    index line "renderer's module amended 2026-10-10".
  - ADR-183 gains a dated consequence: "Neutral (2026-10-10,
    `cut-the-mesh-nodes`): a portion may be a package directory at its
    address, its own `__init__.py` below the levels the core defines, and its
    manifest's `include` names that package; with the four node packages over
    no B-rep engine every node type of the table is a package, and the core
    imports none." Its index line gains "the node packages over no B-rep
    engine third (`cut-the-mesh-nodes`)".
  - ADR-177's status line notes "the snapshot renderer's module moved by
    ADR-179's amendment of 2026-10-10", and ADR-181's index line "the `jscad`
    and `stl` extras install their packages since `cut-the-mesh-nodes`".
  A new ADR is Open Questions 2.

### 12. The spec deltas

- `kernel-extras`: MODIFIED "The CAD kernels are extras, not required
  dependencies" (the four extras install the node distributions; what each
  states; SolidPython's range wherever named; every extra installs a
  distribution; the installation page names ten; a new scenario for the four
  manifests), "The core imports no kernel outside its kernel modules" (no core
  module but the templates; the family's modules in their distributions; a
  new scenario for the census of node types and providers), "An absent node
  package is refused by its extra at its import" (two new scenarios: a module
  beneath an absent package, a node type over one).
- `openscad-node`: MODIFIED "The OpenSCAD node family is the package
  machinome.node.openscad" (its distributions, the renderer's module),
  "SolidPython is the family's kernel, refused at three doors" (the
  distributions install it; the importers read over the packages), "The core
  names no SCAD outside the family and the table of node types" (the scan's
  zones).
- `cli`: MODIFIED "Snapshot command" (the row's module; a new scenario for an
  absent OpenSCAD package).
- `node-model`: MODIFIED "Each leaf type is one module under the node
  package" (every node type in its own distribution; two new scenarios).
- `framework-identity`: MODIFIED "The framework is the package directory
  `packages/machinome` of a monorepo" (ten extension packages; a package
  portion; a new scenario for the four rows of `check-dist`).
- `framework-contributor-guidance`: MODIFIED "The contributor guide states the
  monorepo's development setup" (the scenario's pip command names the four).

Each MODIFIED requirement is copied whole and edited; every existing
scenario keeps its title, and what is new comes under a new title, so the
change archives with the plain command (the third cycle's finding: the CLI
reads a renamed scenario of a MODIFIED requirement as a dropped one).

### 13. The universe sweep

The third cycle's command, with this bench:

```
/home/asa/devel/machinome/.venv/bin/python /home/asa/devel/machinome/scripts/load-projects \
  --bench /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-mesh-nodes/packages/machinome \
  --python /home/asa/devel/machinome/machinome/WTs/v0.9-base-cut-the-mesh-nodes/.venv/bin/python \
  --moved /home/asa/devel/machinome/scripts/load-projects.d/*.toml \
  --timeout 300 \
  --json <scratch>/load-projects.json
```

No new table: no name a project imports moves (the renderer is the CLI's).
Read against the third cycle's counts: 63 repositories, 130 rows, 121 ok, 0
expected, 3 unexpected (wall_clock_41's own CadQuery error, Dum-E without
machinome-freecad, fender-bender without `fb_library`), 0 timeout, 6 no-model.
The bench venv's `.pth` lines put the four packages' directories on the path
(*inferred*; the sweep is the evidence). A row that differs is a finding.

## Risks / Trade-offs

- [A bare install, or `machinome[mesh]` alone, no longer carries `StlNode`
  and `JScadNode`] → The refusal at the import line names the extra; the
  installation page and the changelog say so; nothing is published by this
  campaign, so the first install that meets it is 0.9's (Open Questions 1).
- [The renderer's module address changes] → No project imports it; the core
  reaches it only through the table; the suite's references move with it;
  the logger keeps its name, so log readers see nothing new.
- [CI's `dist` job has no OpenSCAD, so two rows write SCAD rather than
  render] → The bench and the pilot's machine render; the line says which
  ran; the suite's `test` job, which installs OpenSCAD, renders family leaves
  throughout (Open Questions 4).
- [The `jscad` row cannot render] → No environment of the set has the
  command; the suite already skips its integration test; the smoke proves the
  install, the address and the part's construction.
- [The workspace venv holds the primary checkout's framework editable, whose
  `machinome/node/` still holds the four] → As before: the campaign's close
  reinstalls it from `packages/*`.
- [A suite run leaves `packages/machinome/_build.lock` untracked] → Seen once
  on probe 6's tree, which ran with four modules failing to collect; task 10.6
  checks `git status` after the real run and reports a leaving.

## Migration Plan

Within the cycle, in the order of tasks.md: the baseline; the red tests at the
base's paths; the four directories founded and the moves; the manifests, the
READMEs and the core's extras; the workspace's sources, lock and sync; the
version tables and the lint; `check-dist`; the records; validation. Rollback
is a revert of the implementation commit and a `uv sync`. Outside the cycle,
at the campaign's close: the workspace's `scripts/setup` and
`scripts/dev-env`, the workspace venv reinstalled from `packages/*`, the
collaborator guide, the studio's `machinome-api` skill, whose install lines
keep their spelling.

## Open Questions

1. **A bare install carries no node type.** Before the cut `pip install
   machinome` carried `JScadNode` and `StlNode`; after it, a project of those
   parts names `machinome[jscad]` or `machinome[stl]`. The alternatives: keep
   `jscad.py` and `stl.py` in the core, contrary to the pilot's ruling that
   every node type is a package; or have the core require the two packages,
   which makes the extras meaningless and a bare core impossible.
   Recommendation: accept it, as the ruling and `root-cleanup`'s two extras
   intended; the refusal names the line, and the changelog says so.
2. **A new ADR for the cut's close.** The alternative to amending ADR-179 and
   ADR-183 is an ADR-185, "Every node type is a package, and the core imports
   none". Recommendation: amend; the decisions are ADR-183's and ADR-184's,
   and the only new fact, the renderer's home, is a consequence ADR-179
   already wrote down as provisional.
3. **`machinome-node-solid2` names SolidPython directly.** The alternative is
   to reach it through `machinome-node-openscad` (the same install, probe 5).
   Recommendation: direct, by the `kernel-extras` rule that a distribution
   declares what its module imports, as `machinome-node-step` names CadQuery;
   the one-range test holds the two lines equal.
4. **OpenSCAD in CI's `dist` job.** The two SCAD rows render through OpenSCAD
   where it is on the PATH and write SCAD where it is not, which is CI.
   Adding `openscad` to the job's apt packages would render there too.
   Recommendation: not in this cycle; the CI workflow is the repository's,
   and the `test` job already renders family leaves through OpenSCAD.
5. **The renderer's module name.** `renderer` names it for the table's
   column and its class; `viewer` would keep the word of its former address
   and of its logger. Recommendation: `renderer`; the viewer cycle names the
   seam.
