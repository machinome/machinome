# Machinome 0.8 — four layers, typed declarations, one import path

Provisional, 2026-09-27. Working record, not a promise: nothing here is
ratified, and an OpenSpec spec or an accepted ADR outranks it. It
supersedes the "0.8 — production" section of `roadmap.md` in scope:
production stays the fourth layer and mass still arrives from it, but 0.8
is no longer production alone. Every cycle below is re-checked against
its originating finding before it is proposed, cycle by cycle, and a cycle
whose finding has dissolved is struck rather than executed.

## What 0.8 is

Two commitments, stated by the pilot on 2026-09-27.

**A project is four layers.** Model, Simulation, View, Production.

- *Model* — what the pieces are and how they are put together.
- *Simulation* — how the state of the parts and the machine changes
  according to inputs, and the checks that it is functional.
- *View* — how a person interacts with a simulation.
- *Production* — how the machine is manufactured: which parts are printed
  and which are sourced, the bill of materials, and the maker's own
  instructions.

Each layer is its own type with its own class body, and a layer refers to
another by declaration reference, never by name.

**No magic words.** A thing that gives behaviour has a type; its name is
the author's. The framework stops recognising a class attribute by its
spelling, and stops branching on a string it interprets. The model is
Django's: a field is what its type says, under whatever name the author
chose. The inventory of what this rule has to clear is
`magic-strings.md` beside this note. Overriding a base method such as
`render()` is type-driven and stays.

## The empirical conductor

The Curta pair. Marcus Wu's Type I at three times scale
(`projects/Calculators/Curta-Type-I-3x`, 217 commits, some two hundred
modules) is the operating simulation of record. A second Curta from
another author arrived on 2026-09-27 as a BambuStudio 3MF
(`curta-2x-files/`): 93 distinct object names carrying assembly station
codes such as `【H3-2】`, 506 objects over 19 plates, PETG and PETG-CF
presets, modelled from the drawings with credit to Marcus Wu. It is a
different design, not a rescale: no part name matches. Its embedded
description says three times scale and about 300 × 150 × 150 mm while
only the file names say 2x, so the scale is to be measured on a known part
before any law is fitted to it.

The goal for the pair: two models, one simulation and one test suite,
selected by name; one view that is a project page of rich widgets rather
than a panel the framework generates from instructions; two productions
that share a catalogue of sourced parts.

What the 3x project shows today, and why the layers are needed:

- the layers are one inheritance tower — each simulation class subclasses
  the model class of the same level (`MainDrive(SourceDrive)`,
  `Frame(SourceFrame)`), the running root subclasses the layered source,
  and laws read STEP entity names such as
  `p_10220_410003_1_419227.travel`;
- laws carry measured millimetres of the 3x design — the 9 mm crank lift,
  the reverser heights — so the same laws cannot pose the other design;
- one physical fact, "the operator turns the crank", is declared three
  times: `crank_rotation = Driver()`, `crank_rotation.drives(main_drive.turn)`
  and `Turn(handle, crank_rotation, coordinate=main_drive.turn)`, the last
  in a reserved `controls` dict;
- the project already wrote its own view by hand (`simulation/viewer/`, a
  page over the widget with `driverControls: 'none'`), and its README
  says the legacy `operand` driver is "a convenient presentation" — a view
  fact living in a driver;
- three roots share the parts (`fast_curta`, `operating_curta`,
  `clocked_curta`), which is the "two simulations, one model" shape
  turned round.

## The four layers as types

Candidate spellings. None is ratified; each is cut into a cycle only with
the Curta finding that needs it.

**Model.** A `Part` declares its geometry as a typed value under any name
(`shape = Step(STEP, 'M4 Nut')`), replacing `step_source`, `part`,
`stl_source`, `body`, `thickness` and the deflection knobs recognised by
spelling today. A `Body` is a rigid group of parts carrying `Frame()`
declarations. A base body that declares `spindle = Frame()` without a
position, `handle = Part()` without geometry, or `lift_stroke = Length()`
without a value is abstract by construction: a subclass must supply them
and is refused by name at class creation when it does not. No keyword
marks abstractness; the empty typed slot does. Mates with their freedoms
belong here, because a bearing fit that permits rotation is how two parts
are put together. A concrete model subclasses the abstract one and fills
the slots; the framework checks each replacement is a subtype of the slot.

```python
class Crank(Body):
    spindle = Frame()
    handle = Part()

class CurtaModel(Model):
    housing = Housing()
    crank = Crank()
    dials = Dial().repeat(17)
    turn = crank.spindle.on(housing.crank_seat, Revolute(axis=(0, 0, 1)))

class Curta3x(CurtaModel):
    housing = MarcusHousing()
    crank = MarcusCrank()
    dials = MarcusDial().repeat(17)
```

**Simulation.** Generic over the abstract model type, constructed with a
concrete one, checked by type at construction. Its declarations are
inputs, states, laws, bounds, outputs and the clock, and its tests.

```python
class OperatingCurta(Simulation[CurtaModel]):
    clock = Running()
    crank = Input(CurtaModel.turn)
    lift = Input(CurtaModel.lift)
    result = Output(decode(CurtaModel.dials))
    ...

curta_3x = OperatingCurta(Curta3x())
curta_2x = OperatingCurta(Curta2x())
```

An `Input` is an operator's contribution to a model freedom, not the
freedom's value: the Pascaline's tens dial turns by the hand and by the
carry from the units, so the input composes with the law that also writes
that coordinate, as `drives` composes today. Range, unit and rest value
come from the mate. The clock is chosen by type, not by a reserved
`time` attribute, and units are `Angle` and `Length`, not strings.

**View.** A React app in the project, built from a template the viewer
package ships, bound to the ids the framework publishes from the
attribute names. Gestures and scripted actions live here:

```tsx
<Machine of={curta}>
  <Drag part={m.crank.handle} about={m.turn} input="crank" />
  <Press label="Turn crank" move={{ input: "crank", by: 360 }} draw={2} />
  <Digits of="result" places={11} />
</Machine>
```

The framework then owns no gesture and no instruction. It publishes what
the view cannot compute: the tree, each joint's axis and origin, the
program, and the request API `move(input, by)`. The ratio a drag needs is
measurable in the viewer from the program it already executes. The floor
mounts a project's built view when one exists and keeps its generated
panel as the fallback; `machinome export` uses the view as the index page.

**Production.** Typed declarations over a concrete model, referencing
pieces by declaration path the way mates reference frames, with materials
and standards as objects rather than strings.

```python
PETG_CF = Material(density=1.29)

class Marcus3xProduction(Production[Curta3x]):
    handle = Printed(Curta3x.crank.handle, material=PETG_CF)
    screws = Sourced(Curta3x.housing.m4x10, standard=ISO7045(M4, 10))
    seat_the_drum = Step(Curta3x.drum, Curta3x.housing)
```

The bill of materials is the existing content-derived piece inventory
times these declarations. Mass is density times the volume the inventory
already publishes, which is `roadmap.md`'s argument and what lets
`assertAssemblySupported` drop unit density. The catalogue of `Material`
and `Standard` objects is what the two Curta productions share. The 2x's
3MF is itself a production artifact, so a 3MF import yields pieces plus
per-object process facts, and the multi-material 3MF export the markings
finding asked for lands here.

## What `Turn` is

Recorded because it is the clearest specimen of the disease. `Turn`
(`machinome/simulation/control.py:323`, ADR-112, 2026-09-14, for the
Pascaline dials) is an input of the simulation declared as a screen
gesture. It bundles three facts from three layers: the part and the
freedom it rides (model — the tree already holds the mate, its axis and
its pivot; `coordinate=` only selects between two freedoms of one body),
"the operator's hand moves this freedom" (simulation — the actual content,
which the Curta declares three times), and the drag (view). The
`per_unit` it publishes is a derived fact of the compiled program,
computed at `program.py:3599`, and exists only because a driver could be
wired to a joint with `ratio=-360`; typed units remove the need.

So `Turn` and `Slide` become `Input` over a freedom, their difference
being the freedom's kind; `Button` is view, since "one revolution" is a
macro on a picture, not something the Curta has; `Instruction` is view
too, and tests do not need it because they call `move` on inputs, as the
running and clocked scenarios already do; `Driver` survives only as
`Input`, the operating Curta having no driver that is not a freedom.

## The simulation package today

`machinome.simulation` is 17 modules, 12,731 lines, 21 public names, and
holds five kinds of thing. Declarations: `driver.py` (`Driver`,
`DriverState`, `RampProgram`), `state.py`, `instruction.py`, `control.py`
(`Button`, `Turn`, `Slide`), `play.py`, `follow.py`. Enumeration:
`enumeration.py`, the authority that mints the dotted-id namespace.
Three executors and their compiler: `sim.py` (the fixed-dt loop and
dispatch on the clock's mode), `run.py` (the running bank), `program.py`
(the compiled expression program, 5,376 lines, 42 % of the package),
`clocked.py` (the clocked executor), `trajectory.py`. Contact
mathematics: `profile.py`, `contact_proof.py`. Test tooling:
`scenario.py`, `timebase.py`.

Read against the layers: `Instruction`, `Button`, `Turn`, `Slide`,
`RampProgram`, `Sim.trigger`, `qualified_instructions`,
`qualified_controls`, `_refuse_control_without_a_run` and
`_control_displacement` are view; the clock (`motion.ports.Time`) and
the other laws (`Affine`, `drives`, `Bound`, `commit` in `machinome.motion`)
are simulation living outside the package while `Play` and `Follow` live
inside it; and `Sim` stitches three executors together by a mode string.

## Task 1 — one import path

Ordered by the pilot on 2026-09-27 as the first cycle of 0.8: the package
roots stop re-exporting their submodules, and every project imports each
name from the one module that defines it.

**Finding.** The rule "exactly one import path for each name" was set at
the start and applied once. `machinome.motion` keeps it and it is
ratified — `openspec/specs/ports/spec.md`: "The package `__init__` SHALL
export no name of its own and SHALL NOT resolve a submodule's names as
attributes of the package, so there is exactly one import path for each
name" — with the node root refusing the old `machinome.node.Port`
spelling through its `_MOVED` table and a message naming
`machinome.motion.ports`. The two older roots never had it:
`machinome/node/__init__.py` has re-exported since the framework's first
commit, `8f6cbf3` (2023-07-09, `from .internal import AssemblyNode,
FusionNode`), and `machinome/simulation/__init__.py` since its own first
commit, `a10794a` (2026-08-25); `86b075a` (2026-08-30) only made the list
lazy so `.scenario` stopped dragging cadquery into every publication. The
studio's `shop-skills/machinome-api/SKILL.md` "Imports" section teaches
the root spelling for both, so every project learned it. The
`convex-profile-contact` spec already pins `machinome.simulation.profile`
as the only path for its names.

**Where the root spelling is used** (counted 2026-09-27, primary
checkouts, worktrees and build directories excluded):

| where | files | note |
| --- | --- | --- |
| the framework itself (`machinome/`, `tests/`, `docs/`, `README.md`) | 311 | source, tests and the manual's examples |
| project repositories under `projects/` | 990 in 74 repositories | 215 in the Curta alone |
| `machinome-mechanics` | 4 | two tests, two manual examples |
| `machinome-studio` | 2 | the two shop skills |
| scaffolds | 3 lines | `manager/import_step.py:171,361`, `manager/templates/project/root/__init__.py:1` |

**The names and their one path.** `machinome.node` (20):

| name | module |
| --- | --- |
| `AssemblyNode` | `machinome.node.assembly` |
| `FusionNode` | `machinome.node.fusion` |
| `FlexibleNode` | `machinome.node.flexible` |
| `SheetLeafNode` | `machinome.node.sheet_leaf` |
| `Frame` | `machinome.node.frames` |
| `Marking`, `Wrapped`, `Flat`, `Svg` | `machinome.node.markings` |
| `declared_children` | `machinome.node.declarative` |
| `property_as_number` | `machinome.node.decorators` |
| `CadQueryNode` | `machinome.node.adapters.cadquery` |
| `Build123dNode` | `machinome.node.adapters.build123d` |
| `Build123dSheetNode` | `machinome.node.adapters.build123d_sheet` |
| `MolejoNode` | `machinome.node.adapters.molejo` |
| `Solid2Node` | `machinome.node.adapters.solid2` |
| `OpenScadNode` | `machinome.node.adapters.openscad` |
| `JScadNode` | `machinome.node.adapters.jscad` |
| `StlNode` | `machinome.node.adapters.stl` |
| `StepNode` | `machinome.node.adapters.step` |

`StlRenderStart` is imported eagerly into the root from
`machinome.node.base` and listed in `__all__`; its one consumer,
`core/builder.py:30`, already imports it from `base`, so the root simply
stops carrying it.

`machinome.simulation` (21):

| name | module |
| --- | --- |
| `Driver`, `RampProgram` | `machinome.simulation.driver` |
| `State`, `declared_states` | `machinome.simulation.state` |
| `Instruction` | `machinome.simulation.instruction` |
| `Button`, `Turn`, `Slide` | `machinome.simulation.control` |
| `Play` | `machinome.simulation.play` |
| `Follow` | `machinome.simulation.follow` |
| `Sim` | `machinome.simulation.sim` |
| `ScenarioTest` | `machinome.simulation.scenario` |
| `qualified_drivers`, `qualified_states`, `qualified_instructions` | `machinome.simulation.enumeration` |
| `RunConflict` | `machinome.simulation.run` |
| `UnsupportedLaw`, `TooManyCrossings`, `Crossing`, `Stop` | `machinome.simulation.program` |

Later cycles move several of these across layers; each move changes the
path again, which is why this cycle comes first and takes the paths as
they stand.

**Shape of the change.**

- Both roots keep an empty `__all__`, define nothing, and resolve no
  submodule name as an attribute. `from machinome.node import assembly`
  and `import machinome.node.assembly` keep working, being Python's
  submodule import, not a re-export.
- Each former root name is refused the way the node root already refuses
  the moved port names: the `_MOVED` table extended with every row above,
  raising `ImportError` — not `AttributeError`, for the reason
  `node/__init__.py:137` records — whose message names the one module.
  The simulation root gains the same `__getattr__` and table.
- The `node-model` and `simulation` baseline specs gain the ports spec's
  sentence, with a scenario per root that the old spelling is refused
  naming the new path.
- The scaffolds write submodule paths. The manual's examples and the
  framework's own tests move to submodule paths; the manual pages a
  reader is sent to are touched under `skills/write-the-manual/SKILL.md`.
- A rewrite script for the mechanical migration ships in the change's
  evidence, since 74 repositories will run it: one regex per row of the
  tables, idempotent, leaving anything it does not recognise alone.
- No deprecation period: the pilot's word is "force". This is the first
  entry of 0.8's history and a breaking change against 0.7.1, so it does
  not land on a 0.7.x line.

**Outside the framework repository, each in its own repository:**
`machinome-mechanics` (4 files), the studio's two shop skills with the
"Imports" section rewritten to the submodule spelling, and the 74
project repositories, migrated by the script and committed per project
in whichever lane the pilot chooses. `machinome vet` may later refuse a
root import in a project; that is its own cycle if wanted.

## Cycles after task 1 — provisional order

Each is proposed only with the Curta finding that needs it, and struck if
the finding dissolves by then.

2. **Typed declarations in the simulation and the model.** `Input` over a
   model freedom replacing `Driver` + `drives` + `Turn`/`Slide`; the clock
   by type; units as `Angle`/`Length`; geometry as a typed value on a
   `Part`. Retires the reserved `time`, `controls`, `color` and the leaf
   source attributes. Evidence: `magic-strings.md` §6, §7 and "Adjacent";
   the Curta's triple declaration of the crank.
3. **Bodies, abstract slots and the bound simulation.** `Body`, empty
   typed slots, `Simulation[Model]` constructed with a concrete model,
   subtype-checked replacement. Curta: the skeleton cut out of
   `running.py` and `mechanism.py`, marcus3x bound, the operating suite
   green.
4. **Model facts replacing the 3x millimetres in laws.** Curta: the 2x
   bound, both suites green, geometry tests on the 2x faceted only since
   its pieces are meshes.
5. **View.** `Output` and readouts published; the viewer's React bindings
   and template; the floor mounting a project view; export using it.
   Then `Instruction`, `Button`, `Turn`, `Slide`, the `instructions` and
   `controls` tables and their document keys retire at a version bump,
   and the viewer's control-picking API becomes a plain pick-a-part API.
   Curta: the view replaces `simulation/viewer/`; the operating
   demonstrations split into simulation tests and view examples.
6. **Production.** `Printed`, `Sourced`, `Cut`, `Step`, `Material`,
   `Standard`; the BOM from the piece inventory; mass from density and
   volume; then 3MF import as the 2x needs it. Curta: both productions
   over one catalogue.
7. **The simulation package itself.** After the moves above, what remains
   is three executors sharing one compiler and stitched by a mode
   string; whether they become three typed clocks over one program is
   decided on what the Curta pair still needs.

## Open decisions, held for the pilot

- The names of the layer types — `Part`, `Body`, `Model`, `Simulation`,
  `Production` — and whether `AssemblyNode` survives beside `Body`.
- "Model" already means a buildable root in `[tool.machinome.models]`;
  either the manifest key changes or the layer takes another name.
- Whether a mate's range is the model's physical stop or the simulation's
  interlock; `Bound` does both jobs today.
- Whether the generic spelling `Simulation[CurtaModel]` or the constructor
  alone carries the binding.
- Process declared on the part class, which is simpler, or in a
  production table, which lets one model be produced two ways.
- The view bindings come from the AGPL viewer package, so a project's
  view carries that licence; the Foundry licensing policy needs a line.
- The 2x's scale, measured, before any law is fitted to it.
