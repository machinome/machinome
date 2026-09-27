<!-- Copied 2026-09-27 from the workspace repository's docs/magic-strings.md, where it was written; the framework's working record is its home. -->

# Magic strings in the machinome public API

Due diligence of 27 September 2026, against framework main `49a8fc5`
(Machinome 0.7.0 plus ADR-152) and the public contract in
`machinome-studio/shop-skills/machinome-api/SKILL.md`.

## What counts

A **magic string** is a `str` the API interprets to decide behaviour: a
name it looks up, a value from a closed vocabulary it branches on, or a
label it compares. A string that is only carried and displayed, never
looked up or compared, is not one. Neither is a string that names
something outside Python (a file, a product inside a STEP document); those
are listed last because they are unavoidable, not because they are free.

**Severity** is how much of the machine's functionality is expressed
through the string, and then how late a mistake in it is caught. Each
entry records the evidence: the probe run on 27 September 2026 in a
throwaway project under the scratchpad, or the source line.

The framework has already taken the other road three times, and each is
the remedy pattern for what follows:

- a `drives` law given as raw text is refused naming the relation;
- a control's drag `input` is "the `Driver` DECLARATION, not a qualified
  id string";
- a control's `coordinate=` "names a JOINT declaration, not a
  coordinate-id string".

Relations, mates, bounds' `reads=`, wirings and controls all address the
tree by declaration reference in the class body. The strings below are
where the API did not.

## Ranking

| # | surface | what the string decides | caught |
| --- | --- | --- | --- |
| 1 | `Instruction` targets | which driver a declared move moves | at trigger only |
| 2 | instruction names as references | which declared move a button, a trigger or a schedule fires | at simulation construction or trigger |
| 3 | qualified ids in commands | which input a test or session moves or seeds | at the call |
| 4 | qualified ids in readbacks | which value a test reads and asserts | at the call, as a bare `KeyError` for `sim.state` |
| 5 | closed vocabularies | what an assertion checks, which kernel decides, how a result is classified | at the call |
| 6 | unit strings | label, plus an equality gate between coordinates | never validated |
| 7 | colour strings | presentation | at render, not at class definition |
| 8 | external names and references | which file, product, module or root is loaded | at load |

## 1. Instruction targets — the declared moves

```python
instructions = {
    'Home': Instruction({'x_axis.position': 0.0, 'y_axis.position': 0.0},
                        duration=2.0),
    'Advance': Instruction(by={'x_axis.position': 5.0}, duration=0.2),
}
```

`Instruction(targets=None, duration=None, *, by=None)` keys both mappings
by the class-local driver name as a string, dotted for a child's driver
(`machinome/machinome/simulation/instruction.py:48`). This is the most
severe case: an instruction is the machine's whole command vocabulary,
what the viewer publishes as buttons, what a clocked machine turns into a
request, what a scenario triggers. It is the one piece of declared
behaviour in a class body that names its subject by string, sitting next
to relations and controls that name theirs by reference.

**Evidence.** A target misspelt `'fede'` for the driver `feed` is accepted
at class definition and by `Sim(...)` construction under an undeclared
root. It fails only when the instruction is triggered:

```
KeyError "instruction 'Advance' targets driver 'fede', which nothing in Feed declares; declared: feed"
```

A build publishes the instruction first, so the viewer can carry a button
that cannot work. Under a clocked root the one-driver check at
construction catches some of it earlier.

**Remedy shape.** Key by the declaration, as controls already do:
`Instruction(by={feed: 5})`, `Instruction({x_axis.position: 0.0})` with a
path of declared children, resolved and refused at class definition by the
rules relation ends already follow.

## 2. Instruction names used as references

The key of the `instructions` dict is at once the button's label and the
instruction's identity, and three places look it up by string:

- `Button(part, 'Add one')` in `controls`
  (`machinome/machinome/simulation/control.py:206`);
- `sim.trigger('Home')` (`machinome/machinome/simulation/sim.py:86`);
- `sim.at(t).trigger('Home')` in a scenario.

**Evidence.** `Button(carriage, 'Advnce')` beside a declared `'Advance'`
is accepted at class definition and refused only at `Sim` construction
(`ControlError ... the instruction 'Advnce', which nothing in this tree
declares`). `sim.trigger('Advnce')` is refused at the call. By the
contract, a model that is only built meets the same refusal when its
program is compiled.

The instruction's name is also its qualified identity: a child's
instruction is reached as `'<path>.<name>'`, so a label containing a dot
or a space is a label and an identifier at once.

**Remedy shape.** Make the instruction a named declaration that a button
references (`advance = Instruction(...)`, `Button(part, advance)`), with
the label a separate, display-only argument.

## 3. Qualified ids in commands

Every imperative surface that moves or seeds the machine takes the
flattened, dotted qualified id:

- `set_state(**{'x_axis.position': 40.0})` and `clear_state('time')`
  (`machinome/machinome/node/assembly.py:454`);
- `Sim(model, state={'units': 8, 'tens': 3})`;
- `sim.move('crank', by=3600.0)` and `sim.rate('feed', 2.0)`
  (`machinome/machinome/simulation/run.py:449`, `:483`;
  `machinome/machinome/simulation/clocked.py:2089`);
- `set_coordinate(node, 'pose.roll', value)`
  (`machinome/machinome/motion/ports.py:563`).

This is where every scenario and clocked test drives the machine, so it
carries a great deal of functionality. It is ranked below the first two
only because every one of these calls is validated at once with the
declared list. Probed: `sim.move('fed', ...)`, `Sim(state={'fed': 1})`
and `set_state(fed=3)` each refuse naming what is declared, and
`set_coordinate` shares the name check the contract gives
`get_coordinate`.

The string namespace also costs the modeller naming freedom, and the
contract records the cost as rules:

- a bare name resolves while exactly one driver in the tree bears it and
  fails when two do;
- under a running root `set_state` records joint coordinates under bare
  names, so a root driver named like any joint anywhere in the tree
  (`turn` beside `plug.turn`) is refused as ambiguous;
- a list-held or `.repeat()` child cannot be addressed (`units-3` and
  `drivers-0` are not legal segments), so a driver or joint there cannot
  be qualified at all;
- a `Free` joint's six coordinates are dotted names that are not Python
  identifiers.

**Remedy shape.** Accept the declaration reference (`sim.move(Feed.feed,
by=5)`, a path through declared children for a child's driver), with the
string form kept, if at all, as a published-document concern.

## 4. Qualified ids in readbacks

The same ids come back as dictionary keys and fields, and tests compare
against string literals:

- `sim.state['carriage.travel']` (`run.py:390`, `clocked.py:1780`);
- `request.stops[0].coordinate == 'plate.lift'`, `Request.input`,
  `Commit.targets` keyed by id (`clocked.py:1131`, `:1574`, `:1611`);
- `get_coordinate(node, 'pose.roll')` (`ports.py:580`);
- `declared_mates(cls)[name].moving.written`, the string
  `'<child>.<frame>'`, and `fixed.written`.

**Evidence.** A misspelt read `sim.state['carriage.travl']` raises a bare
`KeyError 'carriage.travl'` with no list of what exists, since
`sim.state` is a plain mapping. `get_coordinate` refuses with the
declared list. Reading is less functionality than commanding, so it
ranks below 3.

## 5. Closed vocabularies

A fixed set of words the API branches on or reports. These are magic
strings in the classic sense and the cheapest to replace with an enum or a
keyword.

| surface | words | where |
| --- | --- | --- |
| `assertBlockedBeyond`, `assertFreeWithin` `directions=` | `'both'`, `'forward'` | `machinome/machinome/test.py:2046` |
| test kernel, via `SOLID_TEST_KERNEL` | `'exact'`, `'faceted'` | `test.py:126`, `:175` |
| `Time` declaration `.mode` | `'loop'`, `'running'`, `'elapsed'` | `ports.py:657`, `:675` |
| move and rate handle `.status` | `'active'`, `'completed'`, `'blocked'`, `'refused'`, `'cancelled'` | `run.py:144` |
| move and rate handle `.kind` | `'move'`, `'rate'` | `run.py:470`, `:494` |
| `Stop.side` | `'low'`, `'high'` | `program.py:242`, `clocked.py:1131` |

`directions=` is the only one a caller passes to change behaviour. It
selects what an assertion proves, and `'Both'` is refused at the call.
The kernel choice has proper flags on the command line (`--faceted`,
`--exact`); only its environment spelling is a string. The rest are
results: a test asserts `command.status == 'blocked'` and a typo there is
simply a false comparison, never an error, which is the silent failure
mode of an output vocabulary.

The environment variables themselves are a second, smaller finding: the
test and build settings still carry the pre-rename `SOLID_` prefix
(`SOLID_TEST_KERNEL`, `SOLID_TEST_VOLUME_EPSILON`,
`SOLID_TEST_PLACEMENT_QUANTUM`, `SOLID_BUILD_DIR`).

## 6. Unit strings

`unit='deg'`, `unit='mm'` on `Driver`, `State`, the three port kinds,
`Revolute`, `Prismatic`, `Orbit` and mate freedoms, and
`angle_unit`/`length_unit` on `Free`
(`machinome/machinome/motion/joints.py:302`, `:1187`). This is the case
the pilot named.

The string is free text and is never validated or converted:

- `Revolute(unit='radians')` and `Driver(unit='bananas')` are accepted
  (probed). A `Revolute` turns in degrees whatever its unit says, so
  `unit='rad'` is silently a false statement, not a conversion.
- `scale=` on a driver is the only conversion, and it is a number, not a
  unit.

Yet the string is not a pure label, because the framework compares it:

- a derived coordinate refuses two terms whose unit strings differ
  (`motion/couplings.py:1548`). Probed: `a` in `'deg'` plus `b` in
  `'degrees'` is refused as two units, although both are the same
  quantity;
- a range constraint compares its joint's unit string with its target's
  (`motion/constraints.py:67`);
- a mate freedom with no unit defaults to the string `'deg'`
  (`motion/mates.py:345`);
- the viewer prints it on every readout, nudge and jog label.

Ranked sixth because what it decides is small: a label and an equality
gate. It is pervasive, though, being on every driver and joint, and it is
the one magic string that can make a declaration lie.

**Remedy shape.** The parameter algebra already carries dimensions
(`Length`, `Angle`). A joint's or driver's unit could be the same kind of
object, `Angle` and `Length`, or unit constants from one module, with
equality by dimension and scale rather than by spelling.

## 7. Colour strings

`color = '#RRGGBB'` on a node and the required `color=` of a `Marking`.
Presentation only. A node's colour is checked late: `color = 'red'` is
accepted at class definition, and the check at render time strips a
leading `#` before counting six characters
(`machinome/machinome/node/base.py:1035`). A marking's colour is refused
at its declaration.

## 8. External names and references

These name things that live outside Python, so a string is the honest
type. They are listed for completeness, and only the first item is a
choice.

- `OpenScadNode.module_name` names an OpenSCAD module to call.
- `StepNode.part` names a product as the STEP file carries it. A wrong
  name fails at load with the document's inventory.
- `stl_source`, `step_source`, `scad_source`, `jscad_source` and
  `Svg(path)` are file paths relative to the declaring module.
- `[tool.machinome] model = "package.module:Class"` in `pyproject.toml`
  and node references on the command line are `package.module:Class` or
  `path/to/file.py:Class` strings.

## Adjacent: magic attribute names

Not strings, but the same pattern one level up, and worth knowing when a
proposal adds another. The framework gives meaning to class attributes
and methods by name:

- class attributes `time`, `instructions`, `controls`, `color`, `fn`,
  `optimize`, `linear_deflection`, `angular_deflection`, `thickness`,
  `body`, `part`, `require_watertight`, `node` on a test case;
- methods `render`, `simulate`, `check`, `adjust`, `profile`;
- `time` named as a commit source, which resolves through the class body
  and so is refused when the module imported the standard `time`;
- test discovery by file name (`test_foo.py`, `test.py`), `test_`
  methods, and the snake-case attribute a test class gets
  (`SpurGearTest` gives `self.spur_gear`).

`controls` is validated at class creation
(`machinome/machinome/node/declarative.py:1051`), so a mistyped table is
refused rather than silently inert. `instructions` is not: its targets
wait for a trigger, as section 1 shows.

## Out of scope

- **The published document** (`viewer.json`) is a JSON wire format
  between the framework and the viewer. Its `kind: "button"`,
  `['r', angle, axis]` operations and id-keyed tables are strings because
  JSON has nothing else. The Python API is the subject here.
- **The command line** takes strings by nature (`--set NAME=VALUE`,
  `--drive`, `--renderer web|openscad`). Its flags are validated with
  listed alternatives.
- **Third-party APIs** used inside `render()`, such as cadquery's
  `Workplane("XY")`, are not machinome's.
