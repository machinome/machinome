# ADR-167: A Kernel Is an Extra, and Its Module Refuses Its Absence at Import

**Status:** Accepted; manifold3d's exception amended 2026-10-04 by [ADR-176](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md)
**Date:** 2026-10-03
**Change:** [`lean-install`](../../../openspec/changes/archive/2026-10-03-lean-install/)
**Amends:** [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — an engine whose `occt` extra is not installed is an absent engine, not a broken one
**Related to:**
- [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md) — the conditional-dependency shape, one actionable refusal at the point of use
- [BUILD/ADR-059: Import at the point of use](../BUILD/ADR-059-import-at-the-point-of-use.md) — a deferred import that fails reports itself; an absent extra is now not such a failure
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the pattern the markings' artwork seam follows
- [BUILD/ADR-168: The command table names the module a command needs](../BUILD/ADR-168-the-command-table-names-the-module-a-command-needs.md) — the CLI's door
- [ADR-169: A leaf type is one module under `machinome.node`](ADR-169-a-leaf-type-is-one-module-under-machinome-node.md) — the addresses the extras are named by

## Context and Problem Statement

`pyproject.toml` required `cadquery==2.7.*`, `build123d==0.10.*`,
`ocp-gordon` and `molejo[brep]==0.2.*` (cadquery-ocp arriving through them),
although only five modules reach them: the CadQuery, build123d, STEP and
molejo leaves and the exact engine, plus the markings' SVG reducer. A project
on OpenSCAD alone installed two CAD front ends it never used, about 5.5 s of
import cost (`import cadquery` 3.1 s, `import build123d` 2.4 s, measured
3 October 2026), and the two front ends' coupled OCCT pins block both
upgrades for every project. The lean-core campaign
(`workflow/ongoing/lean-core.md`, "Layers", item 4) makes a bare install the
core alone, inside one distribution, before any package is cut.

The question is not only which dependencies become optional, but what a
user meets when one is missing, and through which door: a project imports
a leaf module directly, names a class through the node root's lazy export,
or runs a command.

## Decision Drivers

- A bare `pip install machinome` installs no CAD kernel; a project installs
  the kernels its parts use, and a project with its extras sees no change.
- The install line is derivable from the address (the one-path rule's rule
  2: the extra is the last component of the address).
- The refusal comes at the import line that needs the kernel, naming what
  needs it and the install line, the same at every door.
- An absent extra is not a broken install; a kernel that is present and
  fails to load still reports itself.
- No core table learns a node type; checking costs nothing.

## Considered Options

1. **The module checks its kernel at import with one helper and refuses by
   its extra** (chosen)
2. A table in the core mapping modules to extras
3. Refuse later, at render or materialization
4. An import hook rewriting `ModuleNotFoundError`

## Decision Outcome

**The kernels are extras named by the address.** The required dependencies
lose `cadquery`, `build123d`, `ocp-gordon` and `molejo[brep]`;
`manifold3d` and `watchdog` stay required. The extras are `occt`
(`cadquery-ocp>=7.8.1,<7.9`), `cadquery`, `build123d` (with the
`ocp-gordon` bound), `step` (CadQuery, which `machinome.node.step` uses
itself), `molejo` (`molejo[brep]`) and `all`. Every kernel extra includes
`machinome[occt]`, so the OCCT range is stated once and several extras
resolve one binding; CadQuery carries one range wherever it is named. The
development extra, CI (`requirements.txt`) and tox install every kernel, so
the framework's suite runs them all.

**One helper, no table.** `machinome.extras.require_extra(extra, needed_by,
*kernels)` asks `importlib.util.find_spec` for each kernel and imports none;
the first that cannot be found raises `ExtraUnavailable(ModuleNotFoundError)`
whose `name` is the missing kernel and which carries `extra`:

```
machinome.node.cadquery (CadQueryNode) needs cadquery, which is not installed; install it with 'pip install "machinome[cadquery]"'
```

Each kernel module — `machinome.node.cadquery`, `.build123d`, `.step`,
`.molejo` and `machinome.occt.engine` — calls it at its top, before any
kernel import and before importing another kernel module, stating its own
extra and kernels. A kernel found and failing to import is not checked
away: it raises its own error where the module imports it.

**Three doors, one refusal.** A leaf module import raises the module's own
refusal. The node root's lazy export (`from machinome.node import StepNode`)
re-raises it unmodified, without the broken-install splice `_load` gives
every other `ImportError`, still an `ImportError` so `from ... import`
carries it and `hasattr` raises it. The CLI answers a command that needs the
module by the extra the refusal names (ADR-168).

**The engine seam reads the engine's refusal as absence.**
`machinome.exact_engine._absent` accepts an `ExtraUnavailable` whose extra is
`occt`, so `exact_engine()` answers `None` and `require_exact_engine` names
`pip install "machinome[occt]"` once cadquery-ocp is optional; an OCP found
and failing still propagates. The engine imports, from the framework, the
contract module and `machinome.extras`, a leaf of the core with no framework
import of its own.

**The markings' artwork seam.** Reducing `Svg` artwork is
`machinome.node.build123d`'s (`svg_regions`, `svg_triangles`,
`SVG_REDUCER_CONTRACT = 1`); `machinome.node.markings` resolves it on first
use and refuses another contract version (ADR-162's pattern). Declaring a
marking and reusing a current one need no kernel; building a stale one
without the extra is refused naming the part's class, the marking and its
artwork. Marking bytes are unchanged.

### Why not a table (option 2)

A row per node type in the core is what the open/closed rule forbids, and a
second copy of what each module can state for itself.

### Why not later (option 3)

An error far from the import line that needs the extra, after the project
has paid for its other imports; and the checks would spread through every
path that renders.

### Why not an import hook (option 4)

The plan rejects import hooks (Flask's `flask.ext`), and Python's own
`ModuleNotFoundError` for the project's own `import cadquery` is already
answered by rule 2.

## Consequences

- A bare install carries no kernel; the tutorial's route is
  `machinome[viewer,cadquery]` (`docs/start/install.rst`).
- `machinome.node.cadquery` and `.build123d` still import no CAD front end;
  the check costs about a millisecond (`find_spec` of the four kernels
  measured 1.2 ms).
- Code that catches `ModuleNotFoundError` behaves the same in this layer
  (module present, kernel absent) and in layer 2 (satellite absent).
- The traceback of an uncaught refusal ends `machinome.extras.ExtraUnavailable:
  ...`, the class as Python prints it.
- `machinome vet` is unchanged: its universe still admits `cadquery`,
  `build123d` and `OCP`, and a verdict does not depend on what is installed.
- At the cut each node package and machinome-occt require their kernel, and
  the checks may go with the move.
- Three kernel modules import their kernels after the call; `setup.cfg`
  ignores E402 for them.

## References

- `machinome/extras.py`, the five kernel modules, `machinome/node/__init__.py`
  (`_load`), `machinome/exact_engine.py` (`_absent`),
  `machinome/node/markings.py`, `machinome/node/base.py` (`_build_markings`)
- `pyproject.toml`, `requirements.txt`, `tox.ini`, `setup.cfg`
- `tests/test_kernel_extras.py`, `tests/test_core_kernel_free.py`,
  `tests/test_node_lazy_exports.py`, `tests/test_exact_engine_seam.py`,
  `tests/test_markings.py`, `tests/exact_engine_absent.py`
- `openspec/specs/kernel-extras/spec.md`, and the `cli-startup-cost`,
  `exact-engine-dependency`, `occt-engine` and `markings` capabilities

## Amendment (2026-10-04)

[ADR-176](../TEST-FRAMEWORK/ADR-176-the-mesh-engine-is-a-provider-behind-the-seam-installed-by-an-extra.md) ends the exception this record kept by
the pilot's ruling of 2 October: `manifold3d` is no longer required. It is
the `manifold` extra, installed by `all` and by no node extra, and its
module `machinome.manifold.engine` refuses its absence at import with
`require_extra('manifold', 'the mesh engine (machinome.manifold.engine)',
'manifold3d')`, which the mesh engine seam reads as an absent engine.
`watchdog` stays required.
