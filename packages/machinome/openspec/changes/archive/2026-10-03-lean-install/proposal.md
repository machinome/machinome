## Why

The lean-core campaign is built in layers (`workflow/ongoing/lean-core.md`,
"Layers (pilot, 3 October 2026)"): layer 1 is the internal architecture for
the whole split inside one repository and one distribution, and its fourth
cycle is the lean install. Three archived cycles gave the core an exact engine
seam (`exact-engine`, ADR-161), a declared leaf contract (`leaf-contract`,
ADR-163) and no class-name recognition (`backend-switch`, ADR-166). What still
stops a bare `pip install machinome` from being the core alone:

- **Every kernel is a required dependency.** `pyproject.toml` requires
  `cadquery==2.7.*`, `build123d==0.10.*`, `ocp-gordon` and `molejo[brep]==0.2.*`
  (cadquery-ocp arrives through them), although only five modules reach them:
  the CadQuery, build123d, build123d-sheet, STEP and molejo leaves, the exact
  engine, and the markings' SVG reducer. Their pins are coupled: cadquery 2.8
  moved to cadquery-ocp 7.9 and build123d 0.11 to cadquery-ocp-novtk, so
  requiring both blocks both upgrades (the comment in `pyproject.toml`). A
  project on OpenSCAD alone installs about 5.5 s of import cost and two CAD
  front ends it never uses (`import cadquery` 3.1 s, `import build123d` 2.4 s,
  measured in the bench on 3 October 2026).
- **The leaves are not at their final addresses.** The one-path rule locked on
  2 October puts a node type at `machinome.node.<nodetype>`; the leaves live at
  `machinome.node.adapters.<x>`. The root-cleanup cycle that strikes the root
  re-exports needs the final paths so that the 74 repositories migrate once.
  15 project files in 7 projects import `machinome.node.adapters.step`
  directly (measured on 3 October 2026; listed in design.md).
- **Two core paths name a kernel without a seam.** `machinome/node/markings.py`
  imports build123d inside `Svg.regions()` and `Svg.tessellate()`, and
  `machinome import-step` reaches the STEP reader through a lazy import whose
  refusal names `pip install cadquery`, an install line that will no longer
  provide the command's reader.

## What Changes

- **Final addresses.** Every leaf module moves from
  `machinome.node.adapters.<x>` to `machinome.node.<x>`: `cadquery`,
  `build123d` (holding `Build123dNode`, `Build123dSheetNode` and the SVG
  reducer), `step` (`StepNode`, `StepAssembly`, `solids_from_faces`,
  `cached_document`), `molejo`, `solid2`, `openscad`, `jscad`, `stl`. The root's
  export table keeps answering every root spelling it answers today; only its
  module targets move.
- **BREAKING: `machinome.node.adapters` is dissolved.** Its modules are gone;
  its `__init__.py` stays only to refuse, so `from machinome.node.adapters.step
  import StepAssembly` (and every other spelling under it) fails at the import
  line with an `ImportError` naming the rule: `machinome.node.adapters.<x>` is
  now `machinome.node.<x>`. No re-export, no alias.
- **BREAKING (install): kernels become extras, their modules stay in the
  core.** cadquery, build123d, ocp-gordon and molejo leave the required list;
  the extras are named by the address's last component: `cadquery`,
  `build123d`, `step`, `molejo`, `occt` (already declared), and `all`. Each
  kernel module checks its kernel at import, without importing it, and refuses
  an absent one with one `ModuleNotFoundError` naming the node types, the
  missing module and `pip install "machinome[<extra>]"`. A project with the
  extra installed sees no change. manifold3d and watchdog stay required.
- **An absent extra is not a broken install.** The node root's lazy exports
  raise the refusal unmodified (`from machinome.node import StepNode` names
  `machinome[step]`); the exact engine seam treats the engine's absent kernel
  as an absent engine, so `require_exact_engine` keeps naming
  `pip install "machinome[occt]"` once cadquery-ocp is optional. A kernel that
  is present and fails to import still reports its own error.
- **The CLI's command table names the module a command needs.**
  `import-step` keeps its implementation in `machinome.manager.import_step`;
  its table entry also names `machinome.node.step`, which the CLI imports
  before running the command. Without the `step` extra the CLI answers
  `import-step` with the extra to install and exits 1, writing nothing, never
  with an unknown-command error or a traceback. No entry-point group.
- **The SVG reducer behind a seam.** The build123d code of `Svg.regions()` and
  `Svg.tessellate()` moves into `machinome.node.build123d`, which declares the
  reducer contract version it implements. `markings.py` resolves it by a
  try-import on first use; `Marking`, `Wrapped`, `Flat` and `Svg` stay in the
  core and declaring a marking needs no kernel. Without the `build123d` extra,
  building a stale `Svg` marking is refused naming the marking, the artwork and
  the extra. Marking bytes are unchanged.
- **The two path-extension lines**, in `machinome/__init__.py` and
  `machinome/node/__init__.py`, admitting only portions that ship no
  `__init__.py` of their own, so a second checkout on `sys.path` (the
  workspace's editable primary) is never merged into a bench's package.
  Nothing uses them yet.
- **The dev extra, CI and tox install every kernel extra**, so the suite runs
  as today.

## Capabilities

### New Capabilities

- `kernel-extras`: which kernels are extras and which dependencies stay
  required; the extras named by the address's last component and what each
  installs; a kernel module checking its kernel at import without importing
  it and refusing an absent one naming the node types and the install line;
  the refusal's type; a present but broken kernel reporting itself; the core
  importing no kernel outside its kernel modules and the engine; the extras
  the development install pulls.

### Modified Capabilities

- `node-model`: each leaf type is one module under `machinome.node`, and the
  dissolved `machinome.node.adapters` refuses naming the new addresses (ADDED).
- `exact-engine-dependency`: "An unavailable exact engine fails actionably at
  the point of use" counts a provider whose kernel extra is absent as an
  absent engine, not a broken one.
- `occt-engine`: "The engine imports the kernel and nothing above it" lets
  the engine import the core's extras module and refuse an absent OCP by the
  `occt` extra before it imports OCP.
- `cli-startup-cost`: "Node backend exports resolve on first use" names the
  final addresses and corrects its stale CadQuery scenario (the CadQuery
  module has imported no CadQuery since `exact-engine`); "Deferred imports do
  not hide a broken installation" passes an absent extra's refusal through
  unmodified.
- `cli`: "Import-step command" names the `step` extra and answers its absence
  before the command runs; a command whose table entry names a needed module
  is answered by its extra when that module's kernel is absent (ADDED).
- `markings`: reducing `Svg` artwork resolves its reducer through a seam,
  refusing by the `build123d` extra; a declaration and a current marking need
  no kernel (ADDED).
- `vet`: "A framework internal is a finding" names the leaf modules among the
  passing contract and says the dissolved package is not a vet finding.

## Impact

- **Code.** Moved: `machinome/node/adapters/{cadquery,build123d,step,molejo,
  solid2,openscad,jscad,stl}.py` to `machinome/node/`, and
  `adapters/build123d_sheet.py` folded into `machinome/node/build123d.py`.
  New: `machinome/extras.py` (`ExtraUnavailable`, `require_extra`). Changed:
  `machinome/node/adapters/__init__.py` (refusal only), `machinome/__init__.py`
  and `machinome/node/__init__.py` (path extension; `_EXPORTS` targets; `_load`
  passing the refusal through), `machinome/exact_engine.py` (`_absent`),
  `machinome/occt/engine.py` (its kernel check), `machinome/node/markings.py`
  (the seam), `machinome/cli.py` (the table's third column and the refusal),
  `machinome/manager/import_step.py` (the new address; its own kernel refusal
  removed), `pyproject.toml`, `requirements.txt`, `tox.ini`.
- **Public interface.** Root spellings unchanged. Module paths move; 15
  project files (7 projects) import `machinome.node.adapters.step`, rows of the
  root-cleanup rewrite script and of this cycle's moved-names file. A bare
  `pip install machinome` installs no CAD kernel; the tutorial's CadQuery
  machine needs `machinome[cadquery]`.
- **Artifacts.** No artifact byte changes. A class's module enters the native
  recipe identity and the flexible state identity (`type(self).__module__`),
  so a node whose class is a moved adapter itself rather than a project
  subclass rebuilds once. The verdict store starts afresh once (its stamp
  digests the package source; an absent kernel already stamps `absent`).
- **Docs.** `docs/start/install.rst` (the extras), `docs/howto/imported-parts.rst`
  (`solids_from_faces`'s address), the changelog's Unreleased section,
  `docs/architecture.md`; the campaign plan.
- **Outside the framework, deferred and noted:** the studio's
  `shop-skills/machinome-api/SKILL.md` (one address line, the import-step
  extra, the install note); the workspace's `scripts/setup` tier-2 framework
  install line (`[all]`); the workspace's `scripts/load-projects.d/lean-install.toml`.
- **Validation.** Deep: Internal-Cycloidal-Actuator on a never-merged branch
  `lean-core-validation`. Shallow: the universe sweep with this cycle's
  moved-names file. Both run by the orchestrator.
