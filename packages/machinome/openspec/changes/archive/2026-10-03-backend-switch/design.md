## Context

This is item 2 of the lean-core campaign plan (`workflow/ongoing/lean-core.md`,
"What it takes"), the third cycle cut, after `exact-engine` and
`leaf-contract` (`openspec/changes/archive/2026-10-03-*`). The plan's "Facts
established on 1 October 2026" names the switch (`node/base.py:1262` then);
"Empirical validation, per cycle" names splitflap as its deep validator.
Facts below were read in the bench at e98b74a on 3 October 2026 unless marked
*inferred*.

### What the switch decides

`AbstractBaseNode.generate_stl` (`machinome/node/base.py:1323-1356`):

```python
if self._up_to_date(self.stl_file): return ...
if not self.rigid: return ...
if self._stl_generation_locked: return ...
backend = next(
    (cls.__name__ for cls in type(self).__mro__
     if cls.__name__ in ('Solid2Node', 'OpenScadNode', 'FusionNode')),
    type(self).__name__)
node_name = getattr(self, 'name', type(self).__name__)
openscad = require_openscad(
    f'node {node_name} ({backend} backend)',
    'its backend renders this STL through OpenSCAD')
# lock file, temporary STL, Popen(openscad <scad_file> -o ...), StlRenderStart
```

- **`backend` is read once, as text in the `needed_by` argument of
  `require_openscad`.** Nothing else in the method, or anywhere in
  `machinome/`, reads it. It decides no branch: whether OpenSCAD is checked
  and launched is decided by the three guards above it (STL current, rigid,
  locked), and what is launched by `stl_builder_command_for` and `scad_file`.
  `require_openscad` (`machinome/openscad.py`) formats `f'{needed_by}
  requires the OpenSCAD binary because {reason}; {remedy}'`.
- **`FusionNode` is a dead entry.** `FusionNode.generate_stl`
  (`node/fusion.py:103`) overrides the method in full, the exact branch
  through the engine and the faceted branch through the mesh engine
  (`_generate_faceted_stl`), and never calls the base's. The literal was
  added with the switch in e21fa13 (13 August 2026, ADR-046), when a faceted
  fusion still rendered through OpenSCAD; 748d6d9 (11 September 2026,
  ADR-102) moved faceted fusion to manifold3d and left the name unreachable.
  `AssemblyNode` is non-rigid and returns before the switch.
- **Who reaches the path.** Every rigid node not overriding `generate_stl`
  whose STL is not current after `_prepare`: a `Solid2Node` or
  `OpenScadNode` leaf, whose `materialize` writes SCAD; a leaf on the declared
  SCAD-presented path (`leaf-contract`, "A faceted leaf presented as SCAD"),
  routed by `_uses_legacy_scad_materialization`; and, *as a fault*, a
  self-materializing leaf whose `materialize` returned without publishing
  (see "Findings"). Exact, sheet and imported-mesh leaves publish their STL
  in `materialize` or raise, so the first guard returns; flexible leaves are
  non-rigid.

Probe, the bench's own code with `shutil.which` patched to `None`, in a
throwaway project under the session scratchpad:

```
node housing (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
node FacetedBox (Solid2Node backend) requires ...           # unnamed Solid2Node subclass
node OutsideScadLeaf (OutsideScadLeaf backend) requires ... # LeafNode + render + as_scad, outside the core
node SilentProducer (SilentProducer backend) requires ...   # LeafNode + materialize that publishes nothing
```

The third line is the requirement's evidence: a leaf on the declared contract
is described by a different rule from the core's own, its own class called a
backend. The fourth is a finding of its own (below).

### The leaf-contract scenario

`node-model`, "Leaf adapters are distinct types", scenario "The backend
lookup is not confused by a shared ancestor": *an exact adapter resolves to
no mesh-rendering backend ... and never launches OpenSCAD*. It is pinned by
three tests that assert an adapter's MRO names none of the three literals
(`test_build123d_adapter.py:327`, `test_stl_node.py:595`,
`test_sheet_leaf.py:459`). The first half describes the lookup; the second is
the behaviour, and it never depended on the lookup: an exact leaf's
`materialize` writes the `.stl` or raises, so `generate_stl` returns at its
first guard. That half is already pinned behaviourally, with
`require_openscad` and `Popen` patched to fail, for every kind:
`test_build123d_adapter.py:273`, `test_sheet_leaf.py:463` and `:476`,
`test_stl_node.py:320`, `test_jscad_integration.py:25`,
`test_flexible_node.py:196`, `test_openscad_dependency.py` (exact fusion,
mixed exact fusion, build123d leaf), `test_backend_neutral_materialization.py:84`.

### Every other class-name string in `machinome/`

Two AST scans of every module under `machinome/` (scratchpad scripts, run on
the bench): comparisons with a `__name__`/`__qualname__` attribute on one
side and a string literal or collection of them on the other; and
comparisons containing a string literal that spells any of the 251 classes
defined under `machinome/`. Each finds exactly one site, the switch. A grep
for `isinstance`/`issubclass` against an adapter class outside
`node/adapters/` finds none. What remains is not the same smell, and is
recorded here for `workflow/ongoing/magic-strings.md`, not changed:

| site | what it is | why it stays |
|---|---|---|
| `_type = 'LeafNode'`, `'FusionNode'`, `'AssemblyNode'` (`leaf.py:45`, `fusion.py:24`, `assembly.py:412`) | the published document's node `type`, written by `core/serializer.py:1006` | declared, carried and displayed; no core code compares it (grep); a wire vocabulary, out of the inventory's scope |
| `klass.__name__ == name` (`core/loader.py:149`) | a module attribute is a class bound under its own name, not an alias | compares two runtime values, recognises no type |
| `type(rendered).__module__.startswith(self.namespace)` (`leaf.py:188`) | the declared `namespace` guard | the leaf's own declaration (`leaf-contract`) |
| `type(n).__module__.startswith('solid2')` (`adapters/solid2.py:37`), `'build123d'` (`adapters/build123d.py:31`, `build123d_sheet.py:86`) | an adapter recognising its own kernel's objects by module | inside the adapter that owns that kernel; leaves with it at the cut |
| `str(status).split('.')[-1] != 'NoError'` (`fusion.py:136`, `:146`) | manifold3d's status enum by spelling | a third-party enum; a candidate for `magic-strings.md` section 5's kind, not this cycle |
| test-case alias from `self.__class__.__name__` (`test.py:1937`) | snake-case attribute named after the test class | already listed, "Adjacent: magic attribute names" |
| `f'{node.__class__.__name__.lower()}.png'` (`manager/snapshot.py:194`) | default snapshot file name | displayed, not compared |

## Goals / Non-Goals

**Goals:**

- No core path recognises a node type by the spelling of a class name, held
  by a test over all of `machinome/`.
- A leaf written outside the core that reaches the OpenSCAD path gets the
  same behaviour and the same message as a core leaf.
- The `node-model` scenario's behaviour, an exact adapter never launching
  OpenSCAD, stays pinned once the lookup it described is gone.
- No change to when OpenSCAD is checked or launched, to any artifact, record,
  identity or document, or to the leaf contract.

**Non-Goals:**

- No change to which nodes reach the OpenSCAD path, including the
  silent-producer fall-through (Findings).
- No change to `_type`, the module-prefix guards or any site in the
  inventory's table.
- No change to `JScadNode`'s missing-`jscad` behaviour (`openscad-dependency`
  defers it).

## Decisions

### 1. Remove the name; declare nothing

The refusal names the node and its own class and states the path's reason:

```python
node_name = getattr(self, 'name', type(self).__name__)
openscad = require_openscad(
    f'node {node_name} ({type(self).__qualname__})',
    'its STL is rendered from SCAD by OpenSCAD')
```

Before and after, `Solid2Node` subclass `FacetedBox` named `housing`:

```
node housing (Solid2Node backend) requires the OpenSCAD binary because its backend renders this STL through OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
node housing (FacetedBox) requires the OpenSCAD binary because its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and ensure 'openscad' is on PATH
```

and the outside leaf `OutsideScadLeaf`, unnamed:
`node OutsideScadLeaf (OutsideScadLeaf backend) requires ...` becomes
`node OutsideScadLeaf (OutsideScadLeaf) requires the OpenSCAD binary because
its STL is rendered from SCAD by OpenSCAD; ...`.

Why:

- **The core needs to know nothing here.** What the path needs is already
  declared by the leaf contract: a leaf presented as SCAD implements
  `as_scad` (or, for the core's two, `materialize` writing SCAD). The reason
  is a property of the path, not of a backend: whatever presents a node as
  SCAD, OpenSCAD renders it. A backend label adds no information the node's
  class does not lead to in one step.
- **The user loses nothing actionable.** What a user does with the refusal is
  find the node and install OpenSCAD. The node's name and its own class,
  which the user wrote, locate it better than the adapter it derives from;
  the reason names SCAD, which says why. The `(qualname)` form is the one
  `ExactLeafNode._converted` already uses in its refusal (`'{self.name}
  ({type(self).__qualname__}) rendered a ...'`), so the core's refusals
  name a node one way.
- **Smallest.** One call's two arguments change; no member, no contract
  number, no spec of `leaf-contract`, no test of the members' agreement
  moves.

Alternatives rejected:

- **(B) A declared class attribute,** say `scad_backend = None` on
  `LeafNode` (or `AbstractBaseNode`), `'Solid2Node'` on `Solid2Node` and
  `'OpenScadNode'` on `OpenScadNode`, read by `generate_stl` with the
  class's qualname as the default. The message for the core's leaves would
  stay byte-identical. Rejected: it adds a member to the leaf contract (the
  first requirement of `leaf-contract`, the `LeafNode` "Declared members:"
  line and `test_leaf_contract_members.py` would follow; `CONTRACT` would stay
  1, since adding a member changes no existing member's meaning, ADR-165)
  whose only effect is one word in one error; no leaf outside the core uses
  it, against ADR-163's driver "declare only what a leaf uses today"; and an
  outside leaf that does not know to declare it is still worded differently
  from the core's, the inequity this cycle removes, unless the default is
  made the class name, in which case the attribute declares a label for two
  core classes only.
- **(C) Derive the label structurally,** the first class in the MRO whose own
  `__dict__` holds `as_scad`, as `_uses_legacy_scad_materialization` already
  walks. No literal, no member, and the core's two leaves keep "Solid2Node".
  Rejected: it names whichever class last overrode a presentation hook, so a
  project subclass that overrides `as_scad` becomes "the backend"; it keeps
  "backend" in the core's vocabulary when the lean core is removing kernels
  from it; and it is cleverness spent on a word.
- **(D) Keep the lookup and add the outside leaf's spelling.** A registry of
  names is the thing the requirement forbids.

The rejection of (B) rests on the message for 20 project directories (the
plan's counts: 16 `Solid2Node`, 4 `OpenScadNode`) changing from "Solid2Node
backend" to their own class name, seen only when OpenSCAD is absent. If the
pilot wants "Solid2Node" kept in that message, (B) with the qualname default
is the fallback, and this proposal returns for its leaf-contract delta.

### 2. `FusionNode` neither belongs in a declaration nor reaches the path

It overrides `generate_stl` without calling the base (Context). Nothing is
declared for it; the change removes its dead name with the others. A
regression test is not added for it beyond the existing ones that patch
`require_openscad` around faceted and exact fusions
(`test_openscad_dependency.py`: exact pair, mixed exact pair, faceted pair;
`test_exact_geometry.py`: `test_mixed_fusion_uses_direct_mesh_composition`).

### 3. The `node-model` scenario becomes its behaviour

The scenario "The backend lookup is not confused by a shared ancestor" is
replaced by "A shared base does not route an exact adapter through
OpenSCAD", and the requirement gains one sentence saying so. The three
name-walk tests are retired, since the property they test (an MRO free of
three spellings) no longer bears on anything; one parametrised test over
`CadQueryNode`, `Build123dNode` and `Build123dSheetNode` pins the scenario in
the form of the existing behavioural tests (patched `require_openscad` and
`Popen`). It is a characterization and green before the change; the cycle
says so rather than claiming a red.

### 4. One rule for the whole core, held by an AST test

A new `node-model` requirement, "No node type is recognised by its class
name", and `tests/test_no_class_name_recognition.py` scanning every module
under `machinome/`, with no allowed exceptions after the change, by the two
checks of Context. The scope is the whole package rather than "the OpenSCAD
path" because both scans already come back with the switch alone, so the
wider rule costs no exception and stops the next one at review. Display of
a class name (f-strings, `repr`, file names) is not a comparison and is not
caught; the test names that boundary in its docstring.

### 5. No leaf-contract change

No member is added, removed or redefined: `as_scad`, `materialize` and
`generate_scad` already declare what the path needs. `CONTRACT` stays 1,
`leaf.py`'s "Declared members:" line and `test_leaf_contract_members.py` are
untouched. The scenario that an outside SCAD-presented leaf is reported like
a core one is placed in `openscad-dependency`, where the message is
specified.

## Findings, recorded and not fixed

- **A self-materializing leaf that publishes nothing falls through to
  OpenSCAD.** The OpenSCAD path's gate is "STL not current after
  preparation", not "this node is presented as SCAD". A `LeafNode` subclass
  whose `materialize` returns without publishing (probe: `SilentProducer`
  above) reaches `require_openscad`; with OpenSCAD present it would launch
  OpenSCAD on a `.scad` that preparation never wrote *(inferred from the
  code; not run with the binary)*. `JScadNode.materialize` has exactly that
  branch (`if not os.path.exists(temporary): return`, `adapters/jscad.py`),
  so a `jscad` run that exits 0 and writes nothing would end in OpenSCAD,
  which `openscad-dependency` says a `JScadNode` never launches. No project
  uses `JScadNode` (plan's count: 0) and no outside self-materializing leaf
  exists, so by the evidence rule this is a finding, not a change: recorded
  in `workflow/warts.md` (task 6.3) for triage. The remedy shape, should a
  project meet it, is a refusal naming the node that produced no STL, made
  where `materialize` returns.

## SOLID review

**Single responsibility.** `generate_stl` launches OpenSCAD for a node whose
STL comes from SCAD and words its refusal from the node itself; it no longer
also keeps a list of which classes are backends. `require_openscad` keeps the
one sentence shape for every requiring path. No bend.

**Open/closed.** A new SCAD-presented leaf, in the core or a package, reaches
the OpenSCAD path and its refusal with no core edit: before, a fourth core
SCAD adapter would have needed its name added to the tuple to be described
like the first two, and an outside one could not be. The AST test closes the
door for later code. No bend on the OpenSCAD path. (Which nodes reach the
path is still decided by staleness rather than by declaration; that is the
recorded finding, a correctness gap for a faulty producer, not a place a new
type needs a core change.)

**Liskov substitution.** Any leaf honouring the contract's SCAD-presented
kind is substitutable for a `Solid2Node` on this path: same check, same
launch, same sentence with its own name. An exact, sheet, imported-mesh or
flexible leaf never reaches it, whatever bases it shares (the modified
scenario). Bend: a self-materializing leaf that publishes nothing is not
substitutable for one that does (Findings).

**Interface segregation.** Nothing is added to any interface; Decision 1's
rejected (B) was the member a leaf would have had to carry for a message.

**Dependency inversion.** The core's path depends on the node's declared
presentation (`as_scad`/`materialize` writing `scad_file`) and on its own
type for display, never on a concrete adapter's identity. No bend.

## ADRs

Written after implementation, from what the pilot ratifies; fresh number:

- **ADR-166, the core recognises no node type by the spelling of its class
  name.** The rule of the new `node-model` requirement and its AST test;
  the OpenSCAD refusal names the node and its class; cites ADR-004 (adapters),
  ADR-046 (the refusal's contract, which it amends), ADR-102 (the path a
  SCAD-presented leaf takes), ADR-161 (the parallel one-rule decision for
  kernel code), ADR-163 (the contract that makes an outside leaf an equal).
  An ADR rather than only a spec sentence because it constrains every future
  core path, as ADR-161 does for kernel code.
- **ADR-046 amended:** its Decision's "naming what needed OpenSCAD" is the
  node and its class, not a backend; status line "amended by ADR-166" and an
  *Amendment (2026-10-03)* section. Its Evidence sentence ("naming the
  `Solid2Node` backend") is history and stays.

ADR-004 is not amended: it never specified the refusal.

## Empirical validation (run by the orchestrator)

- **Deep, splitflap** (`projects/splitflap`, master 600f7bb, clean; a
  `Solid2Node` project: `simulation/scad.py`'s `ScadPart(Solid2Node)`, used by
  `SensorPcb` in `hardware.py` and by `panels.py` and `wheel.py`). On a
  never-merged branch `lean-core-validation` of its own repository, in a
  worktree: its suite as its README states it (`machinome build`, the three
  `machinome test --faceted` commands, `pytest -q simulation/test_layout.py`)
  run against the bench with `PYTHONPATH=<bench>` and the workspace venv,
  in two legs: before the applier starts (the bench at its planning commit)
  and after the applier stops with the change uncommitted (tasks 6.1); expected migration: none, since no
  project names a backend or the message. And the refusal observed on one of
  its `Solid2Node` nodes, `SensorPcb`, with `openscad` removed from the PATH
  and that node's STL made stale in a scratch build directory, before and
  after: expected `(Solid2Node backend) ... its backend renders this STL
  through OpenSCAD` before and `(SensorPcb) ... its STL is rendered from SCAD
  by OpenSCAD` after, with the node's derived name in both.
- **Shallow, the universe.** `scripts/load-projects` against the bench with
  `scripts/load-projects.d/exact-engine.toml`, `leaf-contract.toml` and this
  cycle's `moved-names.toml` (no `[[moved]]` entry: this cycle moves no
  name), `--timeout 300`. Expected non-ok rows, all carried: Voron-2
  (expected, the first cycle's `shape()` move), wall_clock_41 and Dum-E
  (unexpected, pre-existing), six no-model. Any other row returns to the
  orchestrator.

## Risks / Trade-offs

- [A user, or a doc, relied on "Solid2Node backend" in the message] → grep of
  `projects/` and `docs/` finds no occurrence of the label or the old reason;
  the changelog states the new wording.
- [`(FacetedBox)` repeats the name when a node is unnamed: `node FacetedBox
  (FacetedBox)`] → accepted; the exact refusal reads the same way, and a
  branch to suppress it is display logic for no information.
- [The AST rule bans a legitimate future comparison] → a future need that
  truly compares a class name is a design conversation, which is the point;
  the test's failure message names the site and this requirement.
- [Retiring the name-walk tests loses coverage] → they tested spellings; the
  behaviour is covered by the existing patched tests and the new
  parametrised one.

## Migration Plan

One planning commit, one implementation commit, on `v0.8-backend-switch`;
integration into `v0.8` is the orchestrator's. No artifact rebuilds: nothing
recorded changes. Rollback is reverting the implementation commit.

## Deferred, recorded here so it is not lost

- The silent-producer fall-through (Findings), until a project meets it.
- `magic-strings.md` entries for the inventory's table, if the pilot wants
  internal sites in a document that inventories the public API; the manifold
  status spelling is the only candidate.
- `JScadNode`'s missing-`jscad` refusal (already deferred by
  `openscad-dependency`).

## Open Questions

None at ratification (3 October 2026). The message was settled by the
orchestrator as Decision 1 states: the refusal names the node and its own
class, the form the exact refusal already uses, and no contract member is
added for one word. Recorded so the pilot may overrule before the
implementation commit; alternative (B) is the fallback.
