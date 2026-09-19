## Why

The Pascaline module (`projects/Calculators/Pascaline-module`) runs in a
browser and is driven from a panel beside the model: one button per
declared instruction, a nudge pair and a jog pair per declared input.
The pilot wants the other door — click the dial, and the dial advances —
and the campaign already promised it. ADR-048's Consequences say so
outright: *"Constrained dragging of a part is deliberately out: the next
viewer cycle binds a pick to a declared input through this same command
interface, with the same blocked-travel reporting."* The 2026-09-12
ratification (`workflow/open-run-simulation/design.md`, "Inputs,
instructions and controls") named the third thing a control can be —
*"clicking a button, holding a jog control or **dragging a part**"* — and
said an optional controls declaration adds it without the author keeping
two matching lists.

**The viewer cannot infer the binding, and the module's own document is
the proof.** Two facts from its published `_build/viewer.json` (version 5)
rule out "every part whose coordinate one input reaches is a handle for
that input":

- **Reaching is ambiguous exactly where it matters.**
  `program.sources['units.input.turn']` is `['units_entry']`, but
  `program.sources['tens.input.turn']` is `['tens_entry', 'units_entry']`
  — the carry from the column below moves the tens dial too. Nothing in
  the document can say which of the two a hand on the tens dial means.
  Only the author can.
- **Not every moving part may be touched.** `units.drum.turn` is in the
  bank and the number drum turns with it, but a hand does not turn the
  drum: it sits under the lid and the ratchet is on the input arbor, not
  on it. A viewer that made every posed part draggable would let a maker
  do to the model what the machine forbids.

So the binding is a declaration the author makes beside the
instructions, and the framework publishes it. The GEOMETRY of the
gesture is not declared: the tree already carries it. `units.input` is
posed by `['r', 'units.input.turn', [1, 0, 0]]` and `units.input.dial`
is a leaf under it, so the joint's world axis and origin are one world
matrix away from a part the consumer already draws.

The authority for the shape below is the pilot's 2026-09-14 decision on
`workflow/docs/controls-on-parts.md` §3, §4 and §7: the spellings
`Button` and `Turn`; a ratio DERIVED from the compiled program rather
than declared; and the table published ADDITIVELY under document
version 5, with the viewer's API version as the capability gate. This is
the first of that note's three cycles, and the only one in this
repository.

## What Changes

- **An assembly may declare `controls`,** a mapping of display name to
  control, beside `instructions`:

  ```python
  controls = {
      'units dial': Button(units.input.dial, 'Add one'),
      'turn units': Turn(units.input.dial, units_entry),
  }
  ```

  `Button(part, instruction)` — a press on `part` submits the named
  instruction. It is the panel's instruction button moved onto the part,
  and it carries no movement of its own. `Turn(part, input)` — a drag on
  `part`, about the rotational coordinate that part rides, is a sequence
  of relative moves on `input`. Both name a NODE, written the way a
  relation's path ends already are (`units.input.dial`), and both
  qualify through the declaring node's instance path exactly as an
  instruction does. `Slide` for a prismatic coordinate is the obvious
  sibling and is deliberately not proposed here.

- **The framework finds the gesture's coordinate, and refuses where it
  cannot.** A control's coordinate is the one owned by the nearest
  ancestor-or-self of the part whose joint poses it and whose coordinate
  the run banks. A part no run-owned coordinate poses, a posing node
  declaring more than one joint, a joint owning more than one
  coordinate, a `Turn` over a coordinate that is not rotational, a
  `Turn` whose input does not reach the coordinate through the compiled
  program, a `Button` naming no declared instruction, a part that is not
  a node the declaring assembly holds, and a `controls` table under a
  root that does not declare `Time.running()` are each REFUSED naming
  the facts a reader can find in the model.

- **The ratio is DERIVED, never declared.** A `Turn` needs to know how
  far the input travels per degree of the part. The author would only be
  restating a relation the compiled program already holds
  (`units.input.turn = −36 · units_entry`), and a number stated twice is
  a number that drifts. The framework evaluates the compiled program at
  the REST BANK with the input displaced by ±ε and publishes `per_unit`,
  the coordinate units per input design unit. Two readings that disagree
  are refused, and so is zero.

- **A version 5 document gains a top-level `controls` table,**
  ADDITIVELY: the version does not move, and a document that declares no
  control omits the key and stays byte-identical to the one the
  framework publishes today. Each entry carries `kind`, the part's node
  path, the reference the kind needs (`instruction`, or `input` with
  `per_unit`), and the gesture's geometry read off the tree — the joint
  node's path, the coordinate's qualified id, the joint's axis and the
  point it turns about. The compiled program, its `identity`, the
  conformance corpus and every existing version 1 to 5 document are
  untouched.

What does NOT change: the run, the tick, the bank, ownership, admission,
outcomes and every rule about stops and jumps; `trigger`, `move` and
`rate`, which are still the one path every movement request takes; the
program's `identity`, ordering and published shape; the `bindings` pass,
which a control entry never enters, because it carries no expression;
the conformance corpus and its coverage guard; the instructions table;
and every untimed, looping and version 1 to 4 document. No control moves
anything itself, no control stores state, and nothing in this change
depends on `cancel()`, whose defect is a filed and untriaged wart
(`workflow/warts.md`, "running-command cancellation").

## Capabilities

### New Capabilities

None. A control is a declaration inside the existing `simulation`
capability and a table inside the existing `export` one.

### Modified Capabilities

- `simulation`: a new requirement states the `controls` declaration, how
  a control is discovered and qualified, how its coordinate is found,
  and every refusal with the facts it carries. No existing requirement's
  behaviour changes.
- `export`: a new requirement states the version 5 `controls` table, the
  derived `per_unit`, the additive rule and the byte-identity it
  preserves, and which producers publish it. No existing requirement's
  behaviour changes; the version ladder in "Manifest contract" is
  untouched, exactly as `pieces` was added beside it.

## Impact

- `solid_node/simulation/control.py` (new): `Button` and `Turn`, the
  part reference they accept, and the class-definition refusals they
  raise.
- `solid_node/node/declarative.py`: `NodeMeta.__new__` validates a
  `controls` declaration where it is written, as it already validates a
  relation, and marks the class so a document walk can recognize one
  without importing the simulation layer. Duck-typed on the control's
  own `control_kind`, so the node layer still imports nothing from
  `solid_node/simulation/`.
- `solid_node/simulation/enumeration.py`: `qualified_declarations(root)`
  returns the tree's instructions AND controls from ONE walk;
  `qualified_instructions` and a new `qualified_controls` are its thin
  faces.
- `solid_node/simulation/program.py`: `compile_program` gains the
  controls and instructions it must check against, compiles each control
  to the coordinate, joint path, axis and origin it names, and hangs the
  result on `Program.controls`; `Program.described()` is NOT touched, so
  the identity a snapshot is checked against is unchanged;
  `Program.response(bank, input_id, epsilon)` is the pure propagation
  the ratio is measured with, and `Program.published_controls(initial)`
  is the table.
- `solid_node/simulation/run.py`: `Run.__init__` hands the controls and
  instructions to `compile_program`; `_values` and `_deltas` move to
  `Program` and are delegated to, so the measurement and the tick share
  one implementation of "the bank, plus the intermediates" and of "one
  input's displacement".
- `solid_node/simulation/sim.py`: one walk for both declarations; a
  control under a non-running root refused at construction.
- `solid_node/simulation/__init__.py`: `Button` and `Turn` exported
  lazily, like every other name here.
- `solid_node/core/serializer.py`: `document_body` gains a `controls`
  argument and publishes the key only when it is non-empty;
  `symbolic_document`'s walk refuses a control under a non-running root.
- `solid_node/core/builder.py`, `solid_node/core/export.py`: each passes
  the table it just compiled. `solid_node/viewers/browser.py` — the
  baked web-snapshot capture — passes none, exactly as it passes no
  instructions today.
- Tests: `tests/running_project/machine.py` and `parts.py` gain the
  Pascaline-shaped fixture (a root driver, a joint at depth, a leaf
  under the joint, a second column two inputs reach) and one fixture per
  refusal; a new `tests/test_controls.py`; `tests/test_running_document.py`
  gains the table and the byte-identity case; `tests/running-corpus.json`
  is regenerated and must come back identical.
- Docs: `docs/driving.rst` (a "Controls" section after "Instructions"),
  `docs/scenarios.rst`, `docs/api-reference.rst`, `docs/changelog.rst`,
  `docs/architecture.md`.
- Projects: none edited here. The Pascaline module's own `controls`
  declaration is its own change in its own repository, which this cycle
  unblocks, and the viewer's `drive-the-run-by-touch` is a second change
  in a third.
