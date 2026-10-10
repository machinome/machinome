# ADR-166: The Core Recognises No Node Type by the Spelling of Its Class Name

**Status:** Accepted
**Date:** 2026-10-03
**Change:** [`backend-switch`](../../../openspec/changes/archive/2026-10-03-backend-switch/)
**Amends:** [ADR-046: Conditional OpenSCAD dependency](ADR-046-conditional-openscad-dependency.md) — what needed OpenSCAD is named as the node and its own class, not a backend
**Related to:**
- [ADR-004: Multi-CAD backend adapter pattern](ADR-004-multi-cad-backend-adapter-pattern.md) — the adapters the retired lookup named; not amended, it never specified the refusal
- [ADR-102: Native materialization precedes optional SCAD presentation](ADR-102-native-materialization-precedes-optional-scad-presentation.md) — the path a SCAD-presented leaf takes to OpenSCAD, and the move that left `FusionNode` off it
- [ADR-161: The core holds no kernel code](ADR-161-the-core-holds-no-kernel-code.md) — the parallel one-rule decision for kernel code
- [ADR-163: The leaf bases are declared extension points](ADR-163-the-leaf-bases-are-declared-extension-points.md) — the contract that makes a leaf written outside the core an equal of the core's own

## Context and Problem Statement

`AbstractBaseNode.generate_stl` walked the node's method resolution order
for the literals `'Solid2Node'`, `'OpenScadNode'` and `'FusionNode'`,
falling back to the node's own class name, and used the result only to word
the refusal raised when OpenSCAD is missing: `node housing (Solid2Node
backend) requires the OpenSCAD binary because its backend renders this STL
through OpenSCAD; ...`. The lookup decided no branch: whether OpenSCAD is
checked and launched was already decided by the guards above it (STL
current, rigid, locked). `FusionNode` overrides `generate_stl` in full and
had not reached the path since faceted fusion moved to the mesh engine
(ADR-102); its name was dead.

The lean-core campaign (`workflow/ongoing/lean-core.md`, item 2) forbids a
core path that recognises a node type by its name, and the pilot's rule is
that a node package needs no core change. A leaf written outside the core
against the declared leaf contract (ADR-163), presented as SCAD, reached
the same path and was described by a different rule from the core's own:
`node OutsideScadLeaf (OutsideScadLeaf backend) ...`, its own class
mislabelled a backend (probed on the bench, 3 October 2026). An AST scan of
every module under `machinome/` found this switch and no other comparison
of a class name with a string.

## Decision Drivers

- A node type written outside the core is treated exactly as a core type
  declaring the same members.
- No member is added to the leaf contract for one word in one message.
- When OpenSCAD is checked and launched does not change, nor does any
  artifact, record, identity or document.
- The rule holds for the whole core, so the next instance is stopped at
  review.

## Considered Options

1. **Remove the name; declare nothing** (chosen)
2. A declared class attribute naming the SCAD backend, defaulting to the
   class's qualname
3. Derive the label structurally, from the class that owns `as_scad`
4. Keep the lookup and add the outside leaf's spelling

## Decision Outcome

**The core decides nothing about a node by the spelling of its class name,
or of any class in its method resolution order.** No module under
`machinome/` compares a class's `__name__` or `__qualname__` with a string
literal, or a string literal naming a class defined under `machinome/` with
any value, or matches a class name with `startswith`/`endswith`. What a
path needs to know about a node it learns from members the node declares or
inherits. Displaying a class name — in a refusal, a `repr`, a file name —
is not recognition and stays allowed.
`tests/test_no_class_name_recognition.py` holds the rule over every module
under `machinome/`, with no allowed exception.

**The OpenSCAD refusal names the node and its own class, and the path's
reason:** `require_openscad(f'node {node_name}
({type(self).__qualname__})', 'its STL is rendered from SCAD by
OpenSCAD')`. For a `Solid2Node` subclass `FacetedBox` named `housing`:

```
before: node housing (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
after:  node housing (FacetedBox) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
```

A SCAD-presented leaf written outside the core gets the same sentence with
its own name and class. The `(qualname)` form is the one the exact base's
conversion refusal already uses, so the core's refusals name a node one way.

### Why not a declared attribute (option 2)

It adds a member to the leaf contract whose only effect is one word in one
error; no leaf outside the core uses it, against ADR-163's driver to
declare only what a leaf uses today; and an outside leaf that does not know
to declare it is still worded differently from the core's unless the
default is the class name, in which case the attribute labels two core
classes only.

### Why not a structural label (option 3)

It names whichever class last overrode a presentation hook, so a project
subclass overriding `as_scad` becomes "the backend"; and it keeps "backend"
in the core's vocabulary while the lean core is removing kernels from it.

### Why not extend the list (option 4)

A registry of names is what the rule forbids.

## Consequences

- A user with OpenSCAD absent sees their own node's class where they saw
  `Solid2Node backend` or `OpenScadNode backend`; 16 project directories
  use `Solid2Node` and 4 `OpenScadNode`, none of which names the label or
  the message. splitflap's first refused node read `node front (Solid2Node
  backend)` before and `node front (FrontPanel)` after.
- An unnamed node repeats its class, `node FacetedBox (FacetedBox)`, as the
  exact refusal already does.
- Which nodes reach the OpenSCAD path is still decided by staleness after
  preparation, not by declaration: a self-materializing leaf whose
  `materialize` publishes nothing falls through to it (`JScadNode`'s
  no-output branch is the core's one instance). Recorded in
  `workflow/warts.md`, untriaged.
- A future comparison that truly needs a class name is a design
  conversation; the test's failure names the site and this rule.
- The leaf contract is unchanged; `machinome.node.leaf.CONTRACT` stays 1.

## References

- `machinome/node/base.py` (`AbstractBaseNode.generate_stl`),
  `machinome/openscad.py`
- `tests/test_no_class_name_recognition.py`,
  `tests/test_openscad_dependency.py`,
  `tests/contract_package/scad_stand_in.py`
- `openspec/specs/node-model/spec.md` ("No node type is recognised by its
  class name", "Leaf adapters are distinct types"),
  `openspec/specs/openscad-dependency/spec.md` ("A missing OpenSCAD binary
  is reported actionably")
