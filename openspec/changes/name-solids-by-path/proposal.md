## Why

An assertion that fails on two instances of one class cannot say which
instance it means. Two projects recorded it, from opposite sides, in
`workflow/warts.md`:

- "3DPrintedClocks (2026-09-07, shared simulation package)":

  > No public way to give a declared child an instance-specific tree name.
  > Mantel clock 34's `TrainArbor` (one class, six instances) set
  > `part.name` and the private `_explicit_name` on its `wheel` and `rod`
  > children so the viewer tree and interference failures said which wheel
  > was which. The refactor dropped the private and relies on the hierarchy
  > (`train.centre.wheel`); an interference failure still names the leaf
  > only (`wheel should not interfere with wheel`). A public per-instance
  > name, or failure messages that print the qualified path, would close
  > it.

- "Robots/Thor (2026-09-07, full simulation with fasteners)", the second
  entry's last paragraph:

  > Related: neither the assertion nor the pair helpers can name a solid
  > by its path. `seats.qualified_names()` walks the tree to build
  > `{id(node): 'shoulder.art2.art3.art4.art56.gt2x40_pulley_1'}`, because
  > `solid.name` is `gt2x40_pulley_1` and this machine has two. Same gap
  > as the 3DPrintedClocks entry above, from the other side.

Reproduced on the bench `fix-warts-3` at `d1ec98f` (design.md, Context,
measurements 1 to 4):

- A fixture of one class, `TrainArbor`, held twice under one parent as
  `centre` and `third`, each holding a `wheel` and a `rod`, the two wheels
  overlapping. `machinome test` reads
  `AssertionError: wheel should not interfere with wheel (intersection
  volume 32.0)` from `assertNoSolidInterference(self.node)`, and
  `wheel should not intersect wheel (intersection volume 32.0)` from
  `assertNotIntersecting(self.node.centre.wheel, self.node.third.wheel)`.
- 3DPrintedClocks' mantel clock 34 (project at `ec2a05d`), its documented
  run `machinome test mantel_clock_34_steampunk --mesh --volume-epsilon
  0.001`: 20 tests, 15 passed, 5 failed, and three of the failures read
  `shell should not interfere with lid_screw_right (intersection volume
  1.7215580128600183)`; nothing in the message says that `shell` is the
  pendulum bob's. The project's own `test_source_body_inventory` prefixes
  each message with a path it builds by hand (`root.movement.pendulum.bob.shell
  / root.movement.pendulum.bob.lid_screw_right: shell should not intersect
  lid_screw_right ...`). A scratch script pulling the fourth arbor onto the
  third gets `wheel should not intersect wheel (intersection volume
  809.3194719841327)` and `wheel should not interfere with wheel
  (intersection volume 0.8092617098037365)`.
- Robots/Thor (project at `47ba67f`): 438 printed solids at rest, 67 leaf
  names repeated among them; the path `seats.qualified_names()` builds by
  hand equals the framework's own `instance_path` below the root for every
  one of the 438.

The path both projects want exists and is published already: the
framework derives it for every qualified driver id
(`machinome/node/qualified.py`, `instance_path` and `driver_id`, ADR-056),
the serialized document nests each node's `name` under its parent's, and
the viewer's tree walks the same names. On the fixture the document's
tree, `instance_path` and the expected message name the same four strings
(`centre.wheel`, `centre.rod`, `third.wheel`, `third.rod`). Only the test
assertions print the bare leaf name.

## What Changes

- **A failing assertion names a node by its path below the node under
  test.** `wheel should not interfere with wheel` becomes
  `centre.wheel should not interfere with third.wheel`; mantel clock 34's
  interference failure becomes `movement.pendulum.bob.shell should not
  interfere with movement.pendulum.bob.lid_screw_right (...)`. The
  segments are the linked child names the framework already derives and
  publishes, joined by `.`, so the framework gains no second spelling of a
  node's place in a tree.
- **One helper names a node for a message.** `path_name(node, root=None)`
  in `machinome/node/qualified.py`, beside `instance_path`: the dotted
  path below `root`, or below the topmost node `node` is linked under when
  `root` is not one of its ancestors, or the bare name when there is no
  path. It never raises. `machinome.test.TestCase` gains one private
  method, `_named(node)`, that calls it with the node under test, and every
  assertion message in `machinome/test.py` that prints a node's name uses
  it: the seven mesh assertions, the perturbation pair, the two connectivity
  assertions, `assertNoSolidInterference`, both phases of
  `assertAssemblySupported`, the three messages of `assertJoined` and the
  deprecated `assertNoPairwiseIntersections` (design.md, Decision 4, lists
  every site).
- **A node with no path keeps its bare name.** The node under test itself,
  a node linked under no tree, and the support assertion's unmodelled floor
  (`the floor`) are named exactly as today.
- **A message whose named nodes are direct children of the node under test
  is unchanged, byte for byte.** Measured on the framework's own fixtures,
  five existing expectations in `tests/test_meta.py` move and two more are
  tightened (design.md, Decision 6); the tutorial's quoted messages name
  direct children and stay.

**Deliberately out**, with the reason:

- a public per-instance name. The path already tells every instance apart,
  from structure the project has written; a settable instance name would be
  a second spelling of the same identity, which is the defect removed here.
- the labels a kernel or engine error carries (`intersect_shapes`,
  `fuse_shapes`, the mesh engine's refusal of a flexible part's mesh): those
  are raised from module-level helpers holding no node under test, and are
  not assertion messages. The residue is recorded as a new entry in
  `workflow/warts.md` rather than widened into this change.
- the motion layer's refusal helpers (`machinome/motion/couplings.py`
  `where`, `machinome/motion/joints.py` `_where`). They already name a node
  by the same path below the root of its tree and are refusals, not
  assertions; they are left as they are.
- Thor's other finding in the same entry, a public interference inventory;
  it stays in `workflow/warts.md`.
- the projects. Neither is edited: 3DPrintedClocks' hand-built prefix and
  Thor's `qualified_names()` keep working and may be dropped by their
  projects later.
- any verdict, any pair an assertion evaluates, the document, the viewer.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `test-framework`: ADDED "A failing assertion names a node by its path".
  MODIFIED "Mesh assertions" — the offending nodes are named by their path
  under the added requirement; its three scenarios carried, the first
  reworded from "the node names" to "each node's path".

## Impact

- Code: `machinome/node/qualified.py` (one function, `path_name`),
  `machinome/test.py` (`TestCase._named` and the message sites of
  design.md, Decision 4).
- Tests: `tests/test_driver_ids.py` and `tests/test_assertions.py` (the
  helper and the naming rule), `tests/meta_project/two_arbors.py` with
  `tests/meta_project/test_two_arbors.py` and a meta-test in
  `tests/test_meta.py` (the reproduction end to end), and the seven
  expectation lines of `tests/test_meta.py` listed in design.md,
  Decision 6.
- Manual: `docs/reference/assertions.rst` states the naming rule in its
  opening paragraph; `docs/project/changelog.rst` takes one bullet under
  `Unreleased`.
- Documents, the viewer, driver ids, published artifacts: unchanged.
- No ADR (design.md, Decision 7).

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 6, `name-solids-by-path`, validated in
3DPrintedClocks' mantel clock 34 and in Robots/Thor. It takes up the
direction of the change of the same name proposed on the branch
`fix-warts` (`c8c0b6f`, 15 September 2026), ratified and left
unimplemented by the pilot then; its artifacts predate the rename and the
lean-core split and are rewritten here for this tree.
