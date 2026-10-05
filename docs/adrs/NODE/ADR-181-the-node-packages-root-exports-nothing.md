# ADR-181: The Node Package's Root Exports Nothing

**Status:** Accepted
**Date:** 2026-10-05
**Change:** [`root-cleanup`](../../../openspec/changes/archive/2026-10-05-root-cleanup/)
**Amends:**
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md) — the three doors: the node root's lazy export is no longer one
- [ADR-169: A leaf type is one module under `machinome.node`](ADR-169-a-leaf-type-is-one-module-under-machinome-node.md) — the root's re-exports struck; "the root spellings unchanged" no longer holds; `_MOVED` and the adapters package, left to this cycle, both stay
- [BUILD/ADR-179: The core reaches a node package's renderer and command through the table of supported node types](../BUILD/ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md) — the `classes` column's readers are the root's refusal and `load`'s message; there is no export table
**Related to:**
- [ADR-087: One module, one question](ADR-087-one-module-one-question.md) — why `_MOVED` exists
- [ADR-166: The core recognises no node type by the spelling of its class name](ADR-166-the-core-recognises-no-node-type-by-the-spelling-of-its-class-name.md) — read here: a lookup of the requested name that words a refusal is not recognition
- [BUILD/ADR-168: The command table names the module a command needs](../BUILD/ADR-168-the-command-table-names-the-module-a-command-needs.md) — the CLI's door, unchanged
- [ADR-177: The OpenSCAD family is a node package, and the core names no technology](ADR-177-the-openscad-family-is-a-node-package-and-the-core-names-no-technology.md) — the token gate that forbids the root to spell `OpenScadNode`
- [ADR-180: The engines are named for the representation each consumes](ADR-180-the-engines-are-named-for-the-representation-each-consumes.md) — the moved-names format and the scenario-title table this cycle follows

## Context and Problem Statement

One address per name is the readiness condition of the package split: a name
a project imports must have exactly one import path, the module that defines
it, so that cutting a node package moves a module and never a second
spelling. The node package's root, `machinome/node/__init__.py`, still
resolved twenty-one names a second time: lazily through `_EXPORTS` (the
core's eleven and the nine class names of the table of supported node types)
and `StlRenderStart` eagerly; it also bound `NODE_TYPES`, `import_module`,
`find_spec` and `ExtraUnavailable` as public names. On 4 October 2026 the
project catalogue held 1007 files on the root spelling and 35 on the
module's. The pilot decided on 5 October 2026 that the root exports nothing,
each former root name refusing with its module's address as the moved port
names do, the manual changing with the code and every project repository
rewritten in one pass before the change lands; and, by the ruling "Every
node type is a package" of 4 October, `jscad` and `stl` become node packages
with their extras.

## Considered Options

1. **The root resolves no name of its own: each of the twenty-one refused
   with `ImportError` naming its module, the node types' names read from the
   table, the core's twelve from a closed table in the root; `__all__` empty
   and the namespace binding only submodules** (chosen)
2. Keep `_EXPORTS` with a `DeprecationWarning`
3. Delete the root's logic and let Python answer `cannot import name`
4. One table in `machinome.node.supported` for both the node types and the
   core's twelve
5. Refuse only the twenty-one, leaving `NODE_TYPES` and the importlib
   helpers resolvable

## Decision Outcome

**What the root is.** A package path extended with portions
(`_namespace_portions`, ADR-169), its refusals, and its submodules, imported
on first read by `__getattr__` (`machinome.node.step`,
`from machinome.node import supported`), a submodule whose kernel is absent
raising its own refusal unmodified and a broken install raising its own
error with the requested name spliced in (`_load`). `__all__ = []`, so a
star import binds nothing, and no public name of its namespace is anything
but a submodule: `import_module`, `find_spec` and `ExtraUnavailable` are
bound privately, and `NODE_TYPES` is not bound. Importing it imports neither
`base` nor any node type's module.

**The refusals.** `__getattr__` refuses, in order, `_MOVED` (unchanged),
then the former root names, then resolves a submodule, else raises
`AttributeError`. A former name raises `ImportError` (for the reason
`_MOVED` gives: `from X import Y` discards an `AttributeError`'s message)
whose text is, for name *n* and module *m*:

```
module 'machinome.node' has no attribute 'n': the root of machinome.node exports nothing, and 'n' is imported from its module, 'm'. Write `from m import n`.
```

Its opening sentence is Python's own, which `scripts/load-projects` reads as
the dotted name, so a project failing on the root is explained by the row of
the change's `moved-names.toml`. The module comes from two sources: the
node types' class names from `machinome.node.supported.NODE_TYPES`, read
when a name is asked for, each refused naming `machinome.node.<key>` (so the
root spells none of them, which the `openscad-out` token gate requires, and
a row added later is refused with no edit to the root); and `_DEFINED_IN`,
the core's twelve (`AssemblyNode`, `declared_children`, `FusionNode`,
`SheetLeafNode`, `FlexibleNode`, `Marking`, `Wrapped`, `Flat`, `Svg`,
`Frame`, `property_as_number`, `StlRenderStart`), a closed record that no
new name ever joins. The lookup is a mapping read with the requested name,
and it decides nothing but the words of the error: that is not class-name
recognition in ADR-166's sense. Nothing aliases, re-exports or forwards a
refused name, and no refusal is cached.

**`_MOVED` and the adapters package stay.** Both refuse and neither resolves
a name; each turns a released spelling into a message naming where the name
went, for a user outside the catalogue whom the workspace's rewrite never
reaches.

**The doors after the root.** A kernel module is reached, and its absent
kernel refused, at its own import however spelled (`from
machinome.node.step import StepNode`, `from machinome.node import step`), at
the table's `load(key)`, and at the CLI command that needs it (ADR-168). The
root's refusal of a class name imports no node type, so where CadQuery is
absent `StepNode` meets the root's refusal naming `machinome.node.step`, and
the line it suggests meets the module's refusal naming `machinome[step]`.

**`jscad` and `stl` are extras that install nothing.** `JScadNode` runs the
`jscad` command, a Node program no pip extra installs; `StlNode` reads with
trimesh, which the core requires. `jscad = []` and `stl = []` make the
install line every node type's name promises, `machinome[<key>]`, one pip
resolves today and one a manifest can name before the node packages are
cut; `all` includes both. Neither module checks a kernel, so neither is
refused at any door.

**Generated source.** The templates `machinome new` copies import their
node type from its module, and `machinome import-step` composes each import
line it writes from the class it names (`f'from {cls.__module__} import
{cls.__name__}'`), so the command spells no node type's module.

**The gate.** `tests/test_node_root_exports_nothing.py`, permanent: at run
time the twenty-one refused with this text by `from ... import`, `getattr`
and `hasattr`, each imported from its module, `__all__` empty, the star
import binding nothing, every public name a submodule, every class of every
table row refused naming its row; as text, no file under `machinome/` or
`tests/`, no page under `docs/` but the decision records, and not
`README.rst`, spelling a former name in an import from the root or as a
dotted address on it. It was red on 6 + 291 + 20 files and is at zero.

## Rejected Options

- **2:** no alias, no deprecation path (ADR-169): a second working spelling
  is the thing the split cannot carry.
- **3:** Python's message names no module, against the rule for moved names
  and against the sweep's explanation by row.
- **4:** the token gate admits `scad` in `supported.py` and not in the root,
  so the node types' names must be derived from the table whichever file
  holds the core's twelve; and the table's responsibility is the node types
  the core supports, keyed by a technology with an extra, which
  `AssemblyNode` or `Frame` is not.
- **5:** `from machinome.node import NODE_TYPES` is a second path to the
  table's name as much as `AssemblyNode` is; the rule would be left to the
  next helper someone imports in the root.

## Consequences

- Every project file on the root spelling fails at its import line until
  rewritten; the workspace's `scripts/rewrite-projects` rewrote every project
  repository before integration (56 of 62 repositories, 910 files), and the
  universe sweep against the change found no `expected` row.
- A rewritten part's import line is part of its source digest, so it
  rebuilds once, to the same bytes; the leaf-contract golden reads the moved
  digests as expected (`ROOT_CLEANUP_EXPECTED`), and the lock's `.scad`
  hashes and 2573 verdicts were found identical.
- `hasattr(machinome.node, 'AssemblyNode')` raises instead of answering
  `False`, as `_MOVED` already did for ports.
- The API reference documents each class under its module; the install page
  and the backends guide list every node type with its module and extra.
- machinome-studio's two skills and machinome-mechanics' two tests and two
  examples still spell the root and change at their release passes.

## References

- [`root-cleanup` change](../../../openspec/changes/archive/2026-10-05-root-cleanup/): design Decisions 1 to 14, `moved-names.toml`, `evidence.md`, `load-projects.json`
- `workflow/ongoing/lean-core.md`: "Root cleanup decided; the viewer deferred; 0.8 after the root is clean (pilot, 5 October 2026)", "The next phase: the architecture ready for the split", "Every node type is a package"
- `machinome/node/__init__.py`, `machinome/node/supported.py`, `machinome/manager/import_step.py`, `pyproject.toml`
- `tests/test_node_root_exports_nothing.py`, `tests/test_node_root.py`
- `openspec/specs/node-model/spec.md`, and the `cli-startup-cost`, `kernel-extras`, `openscad-node`, `markings`, `mates`, `ports`, `vet`, `cli` and `user-documentation` capabilities
