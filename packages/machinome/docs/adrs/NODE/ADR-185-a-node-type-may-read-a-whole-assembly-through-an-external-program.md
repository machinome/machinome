# ADR-185: A Node Type May Read a Whole Assembly Through an External Program

**Status:** Accepted
**Date:** 2026-10-11
**Change:** [`join-freecad`](../../../openspec/changes/archive/2026-10-11-join-freecad/)
**Amends:**
- [BUILD/ADR-183: An extension package is a namespace portion in its own distribution](../BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): a package that joined the repository from a repository of its own is an extension package like the others, its history imported to its final paths and its record folded into the framework's
**Related to:**
- [ADR-004: Multi-CAD backend adapter pattern](ADR-004-multi-cad-backend-adapter-pattern.md): the FreeCAD node type is one more adapter, whose node is an assembly rather than a leaf
- [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md): an external program as a conditional dependency, found at its point of use and installed by no Python package
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md): the package checks `OCP` in its `__init__` and is installed by the `freecad` extra
- [ADR-184: An absent node package is refused by its extra at its import](ADR-184-an-absent-node-package-is-refused-by-its-extra-at-its-import.md): the table's row makes the absent package refused by `machinome[freecad]` with no other edit

## Context and Problem Statement

The plan for the joins of Machinome 0.9 (`workflow/ongoing/joins-0.9.md` at
the repository root, set by the pilot on 11 October 2026) brings
machinome-freecad into the repository as its first join. machinome-freecad
is the native FreeCAD assembly adapter born from the Dum-E project,
developed in a repository of its own from 1 to 3 October 2026 and never
published: the module `machinome_freecad`, whose `FreeCADAssemblyNode`
compiles one native FreeCAD assembly, its fixed and revolute joints and
their enabled limits, into ordinary nodes, joints and leaves, read by
FreeCAD's own Python in a separate process found through
`MACHINOME_FREECAD_ROOT`, and whose `FreeCADJoint` names one native revolute
for a driver. Its contract is its spec `native-freecad-assembly`.

No node type of the framework is like it. Every row of the table of
supported node types is a leaf type whose kernel is a Python package an
extra installs; this one is an assembly whose kernel is a program no Python
package installs, run in another interpreter. And on the line's head the
product does not load: every one of its four test modules fails at
collection on `from machinome.node import AssemblyNode`, refused since
ADR-181, and behind that import its leaf names `machinome.node.exact_leaf`,
leaf contract 1 and `machinome.occt.engine`, all gone in 0.8 (design.md of
the change, probe 1). Four import lines and one test line bring its 82 tests
green on today's core with FreeCAD 1.1.4 (probe 2), and Dum-E's seven tests
pass on it with its posed snapshot byte-identical to the one of 1 October
2026 (probe 7).

## Considered Options

1. **The FreeCAD node type as a package portion of the table**, whose node
   is an `AssemblyNode` compiled when it is constructed from a document
   FreeCAD reads in a separate process found through
   `MACHINOME_FREECAD_ROOT` (chosen)
2. machinome-freecad kept as an independent product importing the
   framework; refused by the pilot's plan of 11 October 2026, which joins
   the products of the set into one repository, one version and one licence
3. A leaf type per occurrence, the joints redeclared by the project;
   refused by the product's ratified contract, under which the source owns
   the mechanics and the project declares no joint, axis, frame, zero or
   limit
4. FreeCAD installed by the extra; refused, because no wheel of the program
   exists, and the separate process is the boundary between FreeCAD's Python
   and OCCT and the host's

## Decision Outcome

**The table names it once.** `machinome.node.supported` gains the row
`'freecad': NodeType(('FreeCADAssemblyNode', 'FreeCADJoint'))`: its address
is `machinome.node.freecad`, its extra `machinome[freecad]`, and the node
root refuses both class names naming that module. No renderer and no
command.

**The package is an extension package in ADR-183's shape.** The
distribution `machinome-node-freecad`, at `packages/machinome-node-freecad/`,
ships the package directory `machinome/node/freecad/` with its own
`__init__.py` and the modules `adapter.py`, `runtime.py` and `worker.py`, as
the OpenSCAD package ships its own. It carries the set's version and
licence, requires `machinome~=<version>`, `machinome-engine-brep~=<version>`,
`numpy` and `scipy`, and its `__init__` calls
`require_extra('freecad', ..., 'OCP')` before anything imports the binding.

**Its occurrences are B-rep leaves.** The adapter's occurrence leaf is a
`BrepLeafNode` at leaf contract 3, whose solid FreeCAD hands over as BREP
and the adapter reads through `OCP`, counting its solids through the B-rep
engine's seam, `require_brep_engine`.

**Its runtime is refused at construction.** Importing the package and
declaring a class need no FreeCAD; constructing an instance does, and
without `MACHINOME_FREECAD_ROOT` it is refused naming the variable.

**Its tests skip without the variable, and its record is the framework's.**
Its four test modules run in the framework's suite where
`MACHINOME_FREECAD_ROOT` is set and are each reported skipped, naming it,
where it is not. Its spec, archived change and working record joined the
framework's, its history imported to their final paths.

### Consequences

- Good: one address, `machinome.node.freecad`, and one install line,
  `pip install "machinome[freecad]"`; an absent package is refused by its
  extra at every door with no edit to ADR-184's finder.
- Good: the adapter's history reads at its new path back to the commit of
  1 October 2026 that wrote it.
- Bad: CI has no FreeCAD, so it runs none of the package's tests; it proves
  the package's install, its refusal without the runtime and the skips.
- Bad: `machinome vet` and the leaf-contract reach gate do not read the
  package (recorded in `workflow/warts.md`, `join-freecad`).
- Neutral: each fresh model still costs two FreeCAD processes, as before
  the join.
