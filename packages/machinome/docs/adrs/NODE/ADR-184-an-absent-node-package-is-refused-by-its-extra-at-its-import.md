# ADR-184: An Absent Node Package Is Refused by Its Extra at Its Import

**Status:** Accepted
**Date:** 2026-10-10
**Change:** [`cut-the-brep-nodes`](../../../openspec/changes/archive/2026-10-10-cut-the-brep-nodes/)
**Amends:**
- [ADR-167: A kernel is an extra, and its module refuses its absence at import](ADR-167-a-kernel-is-an-extra-and-its-module-refuses-its-absence-at-import.md): when a node type's module is absent, the refusal at its import is the node root's, not the module's
- [ADR-181: The node package's root exports nothing](ADR-181-the-node-packages-root-exports-nothing.md): the three doors keep their refusal when the node package is absent
- [BUILD/ADR-183: An extension package is a namespace portion in its own distribution](../BUILD/ADR-183-an-extension-package-is-a-namespace-portion-in-its-own-distribution.md): an extension package is refused by its extra's name at every door, a node package at its import
**Related to:**
- [BUILD/ADR-179: The core reaches a node package's renderer and command through the table of supported node types](../BUILD/ADR-179-the-core-reaches-a-node-packages-renderer-and-command-through-the-table-of-supported-node-types.md): `load`, whose sentence this decision reuses
- [ADR-169: A leaf type is one module under `machinome.node`](ADR-169-a-leaf-type-is-one-module-under-machinome-node.md): the path extension, which finds an installed portion first

## Context and Problem Statement

The third cycle of the Machinome 0.9 campaign cuts the four node types over
the B-rep engine, `cadquery`, `build123d`, `step` and `molejo`, from the core
into the distributions `machinome-node-<name>`, in ADR-183's shape. Before
the cut, an install without a node type's extra had the module and not its
kernel, and every door answered with the module's own refusal naming
`pip install "machinome[<key>]"`: the project's import line, the node root's
submodule read (`from machinome.node import step`), the markings' artwork
seam, `machinome.node.supported.load` and the CLI. Three ratified
requirements and the installation page promise that refusal ("A kernel
module refuses an absent kernel at import", "An absent extra is reported by
its install line", "A stale marking without the extra is refused by its
install line").

After the cut an install without the extra has neither the module nor the
kernel. Probe 2 of the change's design, with `machinome-node-step`
uninstalled: `import machinome.node.step` and `from machinome.node.step
import StepNode` raise `ModuleNotFoundError: No module named
'machinome.node.step'` with no extra; `from machinome.node import step`
raises `ImportError: cannot import name 'step'` and `hasattr` is `False`; a
stale marking without `machinome-node-build123d` raises `No module named
'machinome.node.build123d'`, naming neither the part, the marking, the
artwork nor the extra. Only `load` and the CLI still name the extra.
ADR-183's rule is that an extension package is refused by its extra's name.

## Considered Options

1. **The node root's last finder**: when no finder before it found
   `machinome.node.<key>` for a key of the table of supported node types,
   the root answers with a module whose import raises the table's refusal
   (chosen)
2. No finder: the project's import line, the node root's submodule read and
   the markings' seam raise the import system's error, and only `load` and
   the CLI name the extra; refused, because three requirements and the
   installation page promise the extra's name at the import
3. A conversion in each seam (`markings`, the root's `_submodule`) without a
   finder; refused, because it leaves the project's own import line, the
   door every project uses, without the extra's name
4. A stub module per node type shipped in the core; refused, because a stub
   with its own file shadows the portion (the core's directory is first on
   the package path) and puts the modules back in the core

## Decision Outcome

**The table words the refusal once.** `machinome.node.supported.absent(key)`
returns the `ExtraUnavailable` that names the node type, its classes, its
module and the extra that installs it: `the step node type (StepNode) needs
machinome.node.step, which is not installed; install it with 'pip install
"machinome[step]"'`. `load` raises it for a module that cannot be found.

**The node root's last finder raises it at the module's import.** Importing
`machinome.node` appends `_AbsentNodeType` to `sys.meta_path`, once. Asked for
`machinome.node.<key>`, a key of the table, which every finder before it
failed to find, it returns a spec whose module's execution raises
`supported.absent(key)`; asked for any other name it returns `None`. An
installed module, from the core's directory, a portion's or a wheel, is
found before it is asked. A module whose kernel is absent still raises its
own refusal from `require_extra`, and a broken module its own error.
Importing `machinome.node` imports no node type and not
`machinome.node.supported`: the finder reads the table only when asked.

So every door names the extra when the package is absent: the project's
import line, `from machinome.node import <key>` (the root's `_load` re-raises
an `ExtraUnavailable` unmodified), `hasattr`, the markings' seam (whose
`_build_markings` re-raises it naming the part, the marking and the
artwork), `load` and the CLI.

### Consequences

- Good: every door names `machinome[<key>]` whether the kernel or the
  package is absent; a reader who copies an install line without its extra
  meets the line that installs it.
- Good: a node type added to the table is refused when absent with no other
  edit.
- Neutral: the finder is consulted for every module no other finder found;
  it answers only `machinome.node.<key>` of the table, after one string
  split, and is last, so it shadows nothing.
- Bad: an absent node type's module has a spec, so
  `importlib.util.find_spec('machinome.node.<key>')` is not `None`; presence
  is asked by importing, as `load` and the root do. Nothing in the core or
  its suite reads a spec as presence.
