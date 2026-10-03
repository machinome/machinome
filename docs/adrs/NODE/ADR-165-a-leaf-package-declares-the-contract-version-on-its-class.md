# ADR-165: A Leaf Package Declares the Contract Version on Its Class

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`leaf-contract`](../../../openspec/changes/archive/2026-10-03-leaf-contract/)
**Extends:**
- [ADR-162: A resolved provider declares the contract version it implements](ADR-162-a-resolved-provider-declares-the-contract-version-it-implements.md) — the same check, moved to the moment an imported package's class meets the core
**Related to:**
- [EXPORT/ADR-068: Optional viewer package behind a process boundary](../EXPORT/ADR-068-optional-viewer-package-behind-a-process-boundary.md) — the declared-API pattern ADR-162 follows
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md) — the contract being versioned

## Context and Problem Statement

ADR-162 checks a provider's declared contract when a seam resolves it. A node
package has no seam: a project imports it (the plan's D2), and the first
moment the core sees it is when its class is created. machinome-freecad shows
what happens without a check: it refuses any machinome release but 0.7.1 at
construction. That number says nothing about the contract: the campaign line
still declares 0.7.1 while a module the adapter imported is gone, and in the
workspace venv the check read stale editable metadata (0.7.0) and refused the
bench for a reason unrelated to either. A release check reads whatever
metadata is installed, not the code that runs, and cannot see a contract
change.

## Decision Drivers

- A leaf written against another contract must fail before any instance
  exists, naming both versions.
- No project leaf, core adapter or existing class may need a declaration.
- Editable and source-tree installs, which bypass dependency pins, are how
  the workspace runs and must be covered.

## Considered Options

1. **An integer on the class, checked at class creation, when declared**
   (chosen)
2. The number in package metadata only
3. A module-level `CONTRACT` in the package, checked through
   `sys.modules[cls.__module__]`
4. No check

## Decision Outcome

`machinome/node/leaf.py` declares `CONTRACT = 1`, an integer literal.
`LeafNode` carries `leaf_contract = None`, and `LeafNode.__init_subclass__`
reads `leaf_contract` from the new class's own `__dict__` only: absent or
`None`, nothing is checked; otherwise, unless it is an `int` (`bool`
excluded) equal to `CONTRACT`, it raises `TypeError` naming the class, the
declared value, the version the core speaks and `machinome.node.leaf`, and
the class does not exist. A subclass of a declaring class inherits the
declaration without being checked again.

Equality, not a range, as for the engine: the packages are numbered with the
framework (the plan's D7). A change to the meaning of a declared member, or
the removal of one, changes `CONTRACT` in the same change. The dependency
pin (`machinome~=0.8.0`) remains the install-time guard; the package
standard's metadata declaration is added when the packages are cut, as for
the engine. The core's own adapters declare nothing: they ship with the core
and cannot differ.

Option 2 checks nothing at runtime, the 0.7.1 failure again; option 3 would
have to tell a project's modules from a package's, which the core cannot do
reliably; option 4 leaves the adapter pinning a release. Requiring a
declaration of every subclass would break every project's leaves.

## Consequences

- The FreeCAD adapter replaces its release pin with `leaf_contract = 1` on
  its leaf.
- A contract change is a deliberate act: the core's `CONTRACT` and each
  package's literal.

## References

- `machinome/node/leaf.py` — `CONTRACT`, `LeafNode.leaf_contract`,
  `LeafNode.__init_subclass__`
- `tests/test_leaf_contract_version.py`
