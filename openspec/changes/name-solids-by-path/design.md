## Context

A node's `name` is unique among one parent's children and nowhere else.
`AbstractBaseNode.__init__` defaults it to the class name and records
whether `name=` was passed (`machinome/node/base.py:583-588`); a parent
replaces the default with the attribute it holds the child under when it
links the child (`_link_child`, `machinome/node/base.py:1221`, through the
index `_link_children` builds, `:1237-1266`, where a list-held child is
named `<attribute>-<index>`); a declarative class does the same when it
realizes its declared children (`_name_child`,
`machinome/node/declarative.py:1455-1462`). Two instances of one class in
one tree therefore carry the same leaf names, and an assertion message that
prints `node.name` says the same word twice.

The framework already spells a node's place in a tree, and uses that
spelling everywhere a flat namespace has to address one of several
instances:

- `instance_path(node, root)` (`machinome/node/qualified.py:242-263`) walks
  `_parent` upward and returns the linked names below `root`; it raises
  `DriverIdError` when the walk never reaches `root`, because a driver id
  that fell back to a bare name "would silently give two instances one id"
  (the module docstring, lines 26-30).
- `driver_id(path, name)` (`:223-239`) joins those segments with `.`, and
  refuses a segment that is not an identifier (`_LEGAL_SEGMENT`, `:220`),
  since an id lands in an expression.
- The serialized document publishes each node's `name`
  (`machinome/core/serializer.py:1002`) and nests its children under it
  after linking them (`:1032-1033`), so the document's tree spells the same
  segments.
- The viewer's tree builds each node's path by the same accumulation,
  `[...path, child.name]` from an empty root path
  (`machinome-viewer/machinome_viewer/widget/src/tree.ts:627`, `:672`).
- The motion layer's refusals name a node by the same path below the root
  of its tree, falling back to `name (Class)` when nothing linked it
  (`machinome/motion/couplings.py` `where`, `machinome/motion/joints.py`
  `_where`).

The test assertions alone print `node.name`.

### Measurements on the bench at `d1ec98f`

Interpreter check: `python -c 'import machinome; print(machinome.__file__)'`
prints `.../WTs/fix-warts-3/machinome/__init__.py`.

**1. The reproduction.** A scratch project (`two_arbors.py`): `TwoArbors`
holds `centre` and `third`, two `TrainArbor`s, each holding `wheel` (a
4 mm cube) and `rod` (a 1 mm cube 10 mm above it), `third` placed 2 mm
along x so the wheels overlap; no `name=` anywhere. Its test file asserts
`assertNoSolidInterference(self.node)` and
`assertNotIntersecting(self.node.centre.wheel, self.node.third.wheel)`.
`machinome test two_arbors.py`:

```text
AssertionError: wheel should not interfere with wheel (intersection volume 32.0)
AssertionError: wheel should not intersect wheel (intersection volume 32.0)
Ran 2 tests in 0.16 seconds: 0 passed, 2 failed
```

**2. One spelling already.** On the same fixture, `serialize_node` with a
stub model path publishes leaf paths `centre.wheel`, `centre.rod`,
`third.wheel`, `third.rod` below the root; `'.'.join(instance_path(leaf,
root))` gives the same four strings; `leaf.name` gives `wheel`, `rod`,
`wheel`, `rod`. A list-held child is `beads-0`, `beads-1`. The root's own
path is `()`; `instance_path` raises `DriverIdError` for an unlinked node
and for a node of another tree.

**3. Mantel clock 34** (`projects/3DPrintedClocks`, `ec2a05d`, checkout
carrying its pre-existing ` M screenshots/wall_clock_03.png` and untracked
`WTs/`). `machinome test mantel_clock_34_steampunk --mesh --volume-epsilon
0.001` against the bench: `Ran 20 tests in 194.29 seconds: 15 passed, 5
failed`, wall time 199 s. Three of the five read
`shell should not interfere with lid_screw_right (intersection volume
1.7215580128600183)`; one reads `edging should be one connected body, but
its STL contains 6 connected bodies`; the fifth is the project's own
`test_source_body_inventory`, which prefixes each framework message with a
path it walks by hand (`shared/testing.py`, `solid_inventory(node,
path="root")`): `root.movement.pendulum.bob.shell /
root.movement.pendulum.bob.lid_screw_right: shell should not intersect
lid_screw_right (...)`. `instance_path` below the root gives
`movement.pendulum.bob.shell`, `movement.pendulum.bob.lid_screw_right`,
`movement.train.third.wheel` and `movement.train.fourth.wheel`. A scratch
script (load the model, set instant 0, build, bind the root to a
`TestCase` as the runner does, pull the fourth arbor's wheel onto the
third's, mesh engine, verdict store off) prints:

```text
assertNotIntersecting(third.wheel, fourth.wheel):
    AssertionError: wheel should not intersect wheel (intersection volume 809.3194719841327)
assertNoSolidInterference(root.movement.train):
    AssertionError: wheel should not interfere with wheel (intersection volume 0.8092617098037365)
```

**4. Thor** (`projects/Robotic-Arms/Thor`, `47ba67f`, clean). A scratch
script loads the model, sets instant 0 and prepares it (64.8 s; nothing
built or compared) and compares `seats.qualified_names(root)` with
`'.'.join(instance_path(solid, root))` for every printed solid: 438 solids,
438 named by hand, 0 differ; 67 leaf names repeat among them;
`shoulder.art2.art3.art4.art56.gt2x40_pulley_1` is the same string both
ways. Thor's contracts run only on the B-rep engine and take hours
(`README.md`, "Running it"); no focused model test under a minute exists,
so none was run.

**5. Cost.** The walk `path_name` makes, timed on a scratch copy: 0.38 µs
per call at depth 2 (the fixture), 1.23 µs at depth 12.

**6. Baselines.** `pytest -q -p no:cacheprovider tests/test_assertions.py
tests/test_connectivity.py tests/test_assembly_integrity.py
tests/test_assembly_supported.py tests/test_broad_phase_culling.py
tests/test_mesh_cache.py tests/test_driver_ids.py
tests/test_brep_geometry.py`: 269 passed, 53 subtests passed, 5.75 s.
`pytest -q -p no:cacheprovider tests/test_meta.py`: 61 passed, 94.23 s.

## Goals / Non-Goals

**Goals**

- Every assertion failure in `machinome/test.py` that names a node names
  it by its path below the node under test.
- One spelling: the segments and separator driver ids, the document and
  the viewer's tree already use.
- A node with no path is named by its bare name, never by an exception.
- A message whose named nodes are direct children of the node under test
  is unchanged, byte for byte.

**Non-Goals**

- A public per-instance name.
- A public interference inventory (Thor's other finding).
- Any change to a verdict, to which pairs an assertion evaluates, or to
  the labels a kernel or engine error carries.
- Any change to the document, the viewer, driver ids or the motion layer's
  refusals.

## Decisions

### 1. The path is taken below the node under test

The runner builds one node and binds it to every test case
(`case.set_node(self.node)`, `machinome/manager/test.py:196`;
`TestCase.set_node`, `machinome/test.py:2023-2035`), and a scenario under
pytest binds the node it builds the same way
(`machinome/simulation/scenario.py:80`). That node is the root every
message path is taken below, whatever node an assertion was called with.

The alternative, each whole-assembly assertion's own `node` argument as
the root, gives one solid two names in one test file:
`assertAssemblySupported(self.node.chain)` would name `floater` where
`assertNoSolidInterference(self.node)` names `chain.floater`. Under the
node-under-test rule both say `chain.floater`, which is also the path the
document and the viewer give it. The pairwise assertions take no root
argument at all.

Under `machinome test` the node under test is the root the loader built,
the top of its tree, so this rule and the motion layer's "below the root
of its tree" give the same string there.

### 2. `path_name(node, root=None)` in `machinome/node/qualified.py`

One function, beside `instance_path`, because that module owns the
`_parent` walk and what a segment is. It walks `_parent` upward from
`node`, collecting `current.name`, until it reaches `root` or a node with
no parent, and returns the segments joined by `.`, or `node.name` when
there are none.

| | `instance_path` | `path_name` |
| --- | --- | --- |
| `root` not an ancestor | raises `DriverIdError` | names the node below its topmost linked node |
| `root=None` | not accepted | the same: below the topmost linked node |
| returns | a tuple of segments | one string, or the bare name |
| segment rule | none (`driver_id` applies `_LEGAL_SEGMENT`) | none |

`instance_path` stays as it is: a driver id must fail loudly where a
failure message must not fail at all, since an assertion whose message
could not be built would replace a real geometric failure with a naming
error. The segments are read by the same expression, `current.name`
through `_parent`, so the two cannot disagree about spelling. The name is
plain, not `qualified_name`, because "qualified name" already means a
driver id in this codebase (`{qualified_name: ...}` in
`machinome/core/serializer.py` and `machinome/simulation/enumeration.py`).

The function is internal (`machinome.node.qualified` is not in the
reference manual and exports nothing to projects); it declares nothing and
stores nothing.

`TestCase` gains one private method:

```python
def _named(self, node):
    return path_name(node, getattr(self, 'node', None))
```

so no message site restates the root rule.

### 3. The bare name, reached three ways

1. **The node is the root** (`assertNoDisconnectedSolids(self.node)` on a
   rigid root): no segments.
2. **The node is linked under nothing**: the suite's doubles
   (`tests/test_assertions.py` `FakeNode`, `tests/stand_in.py`) have no
   `_parent`, and the support assertion's `_VirtualFloor`
   (`machinome/test.py:1316-1325`) is not a node and is named
   `'the floor'`.
3. **The node is linked under another tree, or `self.node` is not one of
   its ancestors**: the walk reaches that tree's topmost node and names the
   node below it. This covers the cases where `self.node` is unset (the
   pytest suites' `asserter = AssertingTestCase()`, never bound), is still
   a class (a scenario's `node = SomeClass` under pytest before
   `scenario_node()` runs), or is never set (`TestCaseMixin.set_node` is a
   no-op, `machinome/test.py:2673-2675`, and a mixin node tested by the
   runner is the root anyway). None needs a special case.

### 4. Every message site, and the decision for each

From `grep -n '\.name\b' machinome/test.py` at `d1ec98f`, classified.

**In scope: assertion failure messages.** Each `X.name` becomes
`self._named(X)`.

| line | assertion | names |
| --- | --- | --- |
| 2046 | `assertNotIntersecting` | `node1`, `node2` |
| 2055 | `assertIntersecting` | `node1`, `node2` |
| 2062 | `assertInside` | `node2`, `node1` |
| 2071-2072 | `assertClose` | `node2`, `node1` |
| 2081-2082 | `assertFar` | `node2`, `node1` |
| 2091 | `assertIntersectVolumeAbove` | `node1`, `node2` |
| 2101 | `assertIntersectVolumeBelow` | `node1`, `node2` |
| 2265-2266 | `_assert_perturbation`, blocked, no intersection | `node`, `against` |
| 2268-2269 | `_assert_perturbation`, blocked, below epsilon | `node`, `against` |
| 2273-2274 | `_assert_perturbation`, free | `node`, `against` |
| 2305 | `assertNoDisconnectedSolids` | `solid` |
| 2356 | `assertNoSolidInterference` | `solid1`, `solid2` |
| 2487 | `assertAssemblySupported`, reachability | every unsupported solid |
| 2516, 2519 | `_statics_body` labels, printed at 2543 | every selected solid; the floor |
| 2573-2575 | `assertJoined`, different solids | `node1`, `node2`, `solid1`, `solid2` |
| 2599 | `assertJoined`, not one body | `node1`, `node2` |
| 2605 | `assertJoined`, weld below minimum | `node1`, `node2` |
| 2651 | `assertNoPairwiseIntersections` | `leaf1`, `leaf2` |

**Out of scope: labels an engine or kernel error carries.**

| line | what | why it stays |
| --- | --- | --- |
| 420, 442 | `f"{node.name} at this binding"`, handed to `_admitted`, the mesh engine's refusal of a flexible part's mesh | a `ValueError` from a module-level helper with no test case in scope, not an assertion |
| 1105 | `engine.intersect_shapes(..., first[0].name, second[0].name)` in the candidate intersection | the B-rep engine's labels for its own error, computed per candidate pair in a module-level helper |
| 1967 | `_brep_verdict(..., node1.name, node2.name)` in `_intersection_stats` | the same |
| 2587 | `engine.fuse_shapes(shape1, shape2, node1.name, node2.name)` in `assertJoined` | the engine's label; `assertJoined`'s own three messages are in scope |

A reader can therefore see `wheel` in an engine error beside
`centre.wheel` in an assertion. Qualifying those labels means threading a
root through module-level helpers on the per-pair path, for text no
project has asked about; the residue is filed as its own entry in
`workflow/warts.md` (tasks 7.3).

### 5. Computed at the failure site; the statics labels per call

Every in-scope site but two is inside the `raise`, so a passing assertion
pays nothing. The two are `machinome/test.py:2516` and `:2519`, which label
every selected solid and the floor on every `assertAssemblySupported` call
that reaches the equilibrium phase, pass or fail: one walk per selected
solid, about a microsecond each (measurement 5), beside a linear program
over the same solids. No cache: a render re-links children each pass, and
a cache would have to follow that for no measured gain. Naming at the
raise instead, from `targets[index][0]`, would leave `_Body.name` read by
nothing; the label stays where the body is built.

### 6. Segments are printed as derived; the expectations that move

A list-held or `.repeat()`-ed child's segment is `<attribute>-<index>`,
which `driver_id` refuses because an id lands in an expression. A message
is prose, so `path_name` applies no segment rule and prints `beads-0.foot`
as derived; sanitizing it would be a third spelling. A node given an
explicit `name=` containing a dot makes any path ambiguous, in the document
and the viewer as much as here, and is not validated in the test layer.

Measured on the framework's own fixtures (every `tests/meta_project/test_*`
case's bound node rendered at instant 0, every node below it with a path of
more than one segment listed): the nodes named in existing message
expectations that are not direct children are `group.c`
(`separated_overlap`), `chain.floater`, `chain.rider`, `leaning.left`,
`leaning.right` (`assembly_supported_floating`), `cantilever.bar`,
`tippy.tippy`, `tippy.neighbour` (`assembly_supported_unbalanced`) and
`carriage.moving` (`assembly_integrity_animated`). In `tests/test_meta.py`
at `d1ec98f`:

| line | today | after | why |
| --- | --- | --- | --- |
| 415 | `a should not intersect c` | `a should not intersect group.c` | red otherwise |
| 472 | `floater, rider should be supported against gravity` | `chain.floater, chain.rider should be supported against gravity` | red otherwise |
| 475 | `left, right should be supported against gravity` | `leaning.left, leaning.right should be supported against gravity` | red otherwise |
| 536 | `bar cannot rest in frictionless static equilibrium` | `cantilever.bar cannot rest in frictionless static equilibrium` | still a substring after; tightened so it pins the path |
| 539 | `tippy cannot rest in frictionless static equilibrium` | `tippy.tippy cannot rest in frictionless static equilibrium` | the same |
| 597 | `fixed should not interfere with moving` | `fixed should not interfere with carriage.moving` | red otherwise |
| 617 | `fixed should not interfere with moving` | `fixed should not interfere with carriage.moving` | red otherwise |

Line 542, `assertNotIn('neighbour cannot rest', ...)`, already refuses
`tippy.neighbour cannot rest` and is left as it is. Every other expectation
on message text in `tests/` names a direct child or a double, or pins a
fragment the path keeps (`'Fixed.*Moving'`, `'left.*right'`,
`'should not interfere with'`); the full suite after the change is the
check. The tutorial's quoted messages (`docs/tutorial/06-fit.rst:38`,
`:72`; `07-scenario.rst:57`) name `base`, `units_drum` and `handle`,
direct children of the tutorial's `Counter`, and stay.

### 7. No ADR

That a node's place in a tree is spelled as the dotted path of linked
names was decided by ADR-056 ("Qualified id syntax: dotted instance
path") and is what the document and the viewer already publish. This
change applies that spelling to assertion messages, a wording rule
specified in `test-framework`; it settles no new boundary. The September
proposal planned an ADR for the same rule; on this tree the rule is
ADR-056's, and the requirement added here records its use.

### Published contracts

The message change touches none. Assertion messages are printed by the
runner in a traceback and read by people; nothing in the framework, the
document, the viewer (`machinome-viewer`), the studio
(`machinome-studio/floor`, `shop-skills/machinome-api/SKILL.md`) parses
them (searched for `should not interfere`, `should not intersect`). The
path grammar printed is the one the document and the viewer already
publish, unchanged.

## Proof plan

- Red first, in the order of tasks.md: `path_name` agrees with
  `instance_path` and falls back without raising
  (`tests/test_driver_ids.py`, red on the import); the naming rule on
  linked doubles (`tests/test_assertions.py`, red on the message text);
  the reproduction fixture end to end (`tests/meta_project/two_arbors.py`,
  a meta-test in `tests/test_meta.py`, red reading `wheel should not
  interfere with wheel`).
- Green, then the moved expectations of Decision 6, then the focused
  suites and the full suite.
- Projects, against the bench, before and after: mantel clock 34's
  documented run stays at 20 tests, 15 passed, 5 failed, its interference
  failures now naming `movement.pendulum.bob.shell` and
  `movement.pendulum.bob.lid_screw_right`; the provoked failure names
  `movement.train.third.wheel` and `movement.train.fourth.wheel`. Thor's
  path comparison is re-run and its result set beside the framework's new
  wording on a Thor solid (`path_name` of
  `...gt2x40_pulley_1` equals `qualified_names()`'s string).

## Risks / Trade-offs

- **A project's own checks may read an assertion message.** The change is
  user-visible, which is why it is a specified requirement. It only moves
  a message whose named node is not a direct child of the node under test.
  3DPrintedClocks' `test_source_body_inventory` keeps working; its hand-built
  prefix then repeats the path the framework prints, which is the project's
  to drop.
- **The engine-label residue** of Decision 4 stays visible and recorded.

## Open Questions

None for the pilot. The published-contract check above found no consumer
of the message text and no change to any path grammar.
