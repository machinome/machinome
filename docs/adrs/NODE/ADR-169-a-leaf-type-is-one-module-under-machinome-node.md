# ADR-169: A Leaf Type Is One Module Under `machinome.node`; the Adapters Package Is Dissolved

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`lean-install`](../../../openspec/changes/archive/2026-10-03-lean-install/)
**Amends:** [ADR-004: Multi-CAD backend adapter pattern](ADR-004-multi-cad-backend-adapter-pattern.md) — the adapters' module layout
**Related to:**
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md)
- [ADR-165: A leaf package declares the contract version on its class](ADR-165-a-leaf-package-declares-the-contract-version-on-its-class.md)
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the extras named by these addresses

## Context and Problem Statement

The one-path rule locked on 2 October 2026 puts a node type at
`machinome.node.<nodetype>`, the address its package keeps when the node
packages are cut; the leaves lived at `machinome.node.adapters.<x>`. The
root-cleanup cycle that strikes the root re-exports needs the final paths so
that the project repositories migrate once. Fifteen project files in seven
projects imported `machinome.node.adapters.step` directly (measured
3 October 2026). The cut also needs the core packages to find a satellite's
modules under `machinome` and `machinome.node`.

## Decision Drivers

- Each leaf at its final address; the root spellings unchanged.
- A project that has not migrated fails at its import line, told where the
  module went; no alias, no re-export.
- One technology, one module, one extra, one distribution at the cut.
- A satellite's modules resolve at the same address, and a second copy of
  the core on `sys.path` is never merged into the package.

## Considered Options

1. **Leaf modules directly under `machinome.node`; the adapters package
   kept only to refuse; a filtered path extension** (chosen)
2. `Build123dSheetNode` in its own module `machinome.node.build123d_sheet`
3. Python's own `ModuleNotFoundError` for the old addresses
4. Nine one-line modules under `adapters/`, each naming its new home
5. The plain `pkgutil.extend_path` line

## Decision Outcome

**The addresses.** `machinome.node.cadquery` (`CadQueryNode`),
`machinome.node.build123d` (`Build123dNode`, `Build123dSheetNode` and the
`Svg` artwork reducer), `machinome.node.step` (`StepNode`, `StepAssembly`,
`solids_from_faces`, `cached_document`), `machinome.node.molejo`,
`machinome.node.solid2`, `machinome.node.openscad`, `machinome.node.jscad`
and `machinome.node.stl`. The node root's export table keeps every key; only
its targets move. "Node type" in the rule names the technology, not the
class: the sheet node has the kernel, pin and licence of `Build123dNode`,
and `StepNode` and `StepAssembly` already share a module. Two classes in one
module stay two types.

**The dissolved package refuses.** `machinome/node/adapters/__init__.py`
holds only a docstring and

```
ImportError: module 'machinome.node.adapters' was dissolved: each leaf type is now one module under 'machinome.node', so 'machinome.node.adapters.<x>' is 'machinome.node.<x>' ('build123d_sheet' is part of 'machinome.node.build123d'). Write, for example, `from machinome.node.step import StepAssembly`.
```

A dotted path never consults the parent's module `__getattr__` (probed), so
the root's `_MOVED` table cannot answer it; the parent package is imported
first, so its refusal answers every spelling beneath it. It stays as long
as `_MOVED` does; the root cleanup decides both.

**The filtered path extension.** `machinome/__init__.py` and
`machinome/node/__init__.py` extend their `__path__` with
`pkgutil.extend_path`, admitting only portions that ship no `__init__.py`
of their own. A satellite never ships either package's `__init__.py`, so
every install combination of the plan still finds it. Nothing uses the
extension yet.

### Why not a sheet module (option 2)

It needs an extra installing exactly what `build123d` installs, or breaks
"the extra is the last component of the address", and makes a second
package at the cut for the same kernel.

### Why not Python's error, or nine modules (options 3, 4)

Python's error names the old package and not where the names went, against
the root's rule for moved names; nine files kept only to refuse, where one
suffices.

### Why not the plain line (option 5)

Probed on 3 October 2026: the workspace venv installs the primary checkout
in compat editable mode, so the plain line appended the primary's
`machinome/` to a bench's package path, and `import machinome.exact`
(deleted by `exact-engine`) resolved to the primary's file. A regular
package wins for which `__init__.py` runs, not for which submodules resolve.

## Consequences

- Projects importing a former address migrate textually:
  `machinome.node.adapters.<x>` → `machinome.node.<x>`, `from
  machinome.node.adapters import <x>` → `from machinome.node import <x>`,
  `build123d_sheet` → `build123d`; rows of the root cleanup's rewrite
  script.
- A node whose class is a moved leaf class itself, rather than a project's
  subclass, changes recipe identity and rebuilds once (`type(self).__module__`
  enters it).
- `import machinome` costs about 6 ms more (`pkgutil` and the scan).
- ADRs written before this one keep their historical paths.

## References

- `machinome/node/*.py`, `machinome/node/adapters/__init__.py`,
  `machinome/__init__.py` (`_namespace_portions`), `machinome/node/__init__.py`
- `tests/test_leaf_addresses.py`, `tests/test_node_lazy_exports.py`
- `openspec/specs/node-model/spec.md` ("Each leaf type is one module under
  the node package")
