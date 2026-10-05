## Why

The lean-core campaign (`workflow/ongoing/lean-core.md`, "What it takes",
item 2) removes the one place the core recognises a node type by the spelling
of its class name. `AbstractBaseNode.generate_stl` (`machinome/node/base.py`,
near line 1331) walks the node's method resolution order for the literals
`'Solid2Node'`, `'OpenScadNode'` and `'FusionNode'`, falling back to the
node's own class name, and uses the result only to word the refusal raised
when OpenSCAD is missing: `node housing (Solid2Node backend) requires the
OpenSCAD binary ...`. The plan's rule, and the pilot's that a node package
needs no core change, forbid it: a leaf written outside the core against the
declared leaf contract (ADR-163) that presents itself as SCAD reaches the same
path and is described differently, as `(OutsideScadLeaf backend)`, its own
class mislabelled a backend (probed on the bench, 3 October 2026). The
leaf-contract cycle's `node-model` scenario "The backend lookup is not
confused by a shared ancestor" pins the lookup itself; this cycle replaces it
with the behaviour it stood for.

## What Changes

- **The switch goes, and no declaration replaces it.** The refusal names the
  node and its class (`node housing (FacetedBox)`), as the exact base's
  conversion refusal already does, and states the path's own reason, that the
  node's STL is rendered from SCAD by OpenSCAD. No backend is named, so the
  core needs to know none. The message a user sees with OpenSCAD absent:
  - before: `node housing (Solid2Node backend) requires the OpenSCAD binary
    because its backend renders this STL through OpenSCAD; install OpenSCAD
    and ensure 'openscad' is on PATH`
  - after: `node housing (FacetedBox) requires the OpenSCAD binary because
    its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure
    'openscad' is on PATH`
  A leaf outside the core reaching the path gets the same sentence with its
  own name and class.
- **No core module compares a class name to a string.** An AST test over all
  of `machinome/` holds it; today it finds exactly the switch.
- **When OpenSCAD runs is unchanged.** The path is reached, as before, by a
  rigid node whose STL is not current after preparation and is not locked;
  the lookup never decided that. `FusionNode`, the third literal, overrides
  `generate_stl` in full and has never reached the path since faceted fusion
  moved to the mesh engine (ADR-102); its name was dead.
- The three tests that assert an adapter's MRO contains none of the three
  literals (`test_build123d_adapter.py`, `test_stl_node.py`,
  `test_sheet_leaf.py`) are retired; the behavioural tests that patch
  `require_openscad` and `Popen` for each kind remain the pin.

No leaf-contract member changes, so `machinome.node.leaf.CONTRACT` stays 1.
No artifact, record, identity or document byte changes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `node-model`: "Leaf adapters are distinct types" loses the scenario that
  pinned the class-name lookup and gains its behavioural form, an exact
  adapter never reaching the OpenSCAD path; a new requirement states that the
  core recognises no node type by the spelling of its class name.
- `openscad-dependency`: "A missing OpenSCAD binary is reported actionably"
  names the node and its class instead of a backend, and a SCAD-presented leaf
  written outside the core is reported in the same words.

## Impact

- **Code.** `machinome/node/base.py`, `generate_stl` only: the lookup removed,
  the `require_openscad` call's `needed_by` and `reason` reworded.
  `require_openscad` stays imported into `machinome.node.base`, which the
  existing tests patch.
- **Tests.** `tests/test_openscad_dependency.py` (the message), a new
  `tests/test_no_class_name_recognition.py` (the AST scan and the outside
  leaf), three name-walk tests retired.
- **Projects.** None names the backend label or depends on the message (grep
  of `projects/`, 3 October 2026); 16 directories use `Solid2Node` and 4
  `OpenScadNode`, per the plan's count, and see the new wording only when
  OpenSCAD is absent.
- **Docs.** The changelog's Unreleased section; `docs/architecture.md`
  already says the refusal names "the operation and remedy" and needs no
  change.
- **Validation.** splitflap (deep, a `Solid2Node` project) and the universe
  scan (shallow), both run by the orchestrator. This cycle moves no name.
