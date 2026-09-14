# Controls on parts: pressing and turning the machine itself

**Status: provisional plan, 2026-09-14.** Nothing here is ratified. It is
the working document three OpenSpec cycles would be cut from — one in the
framework, one in the viewer, one in the Pascaline module — and where it
and a baseline spec or an accepted ADR disagree, the spec and the ADR are
right and this note is stale. It claims no interface exists.

---

## 1. The ask, and what is already decided

The Pascaline module runs in a browser and is driven from a panel: one
button per declared instruction (`Add one`, `Add ten`, `Add hundred`,
`Back one`), a nudge pair and a jog pair per declared input. The pilot
wants the other door: click the dial, and the dial advances.

Most of the design is already ratified, and this note only has to obey
it:

- The 2026-09-12 ratification (`workflow/open-run-simulation/design.md`,
  "Inputs, instructions and controls"): an **input** exposes a coordinate;
  an **instruction** is a named, reusable movement request; a **control**
  is how a person issues a request — "a button, a held jog, or **dragging
  a part**". "An optional controls declaration adds jog/drag interactions
  or customizes presentation. Authors do not maintain two matching lists
  just to make named actions usable." A button for an instruction
  *references* it and never repeats its definition.
- ADR-048 (viewer, `drive-the-run-on-screen`), Consequences: "Constrained
  dragging of a part is deliberately out: the next viewer cycle binds a
  pick to a declared input through this same command interface, with the
  same blocked-travel reporting."
- No two-way binding, ever: a part is posed only from the committed bank.
  A blocked request accumulates no hidden movement. A manual gesture ends
  on release, lost capture, lost focus and a hidden page.

What exists to build on, verified against the module's own published
`_build/viewer.json` (version 5):

- `handle.run().trigger(name)`, `.move(input, {by, duration})`,
  `.rate(input, rate)` — every on-screen control already goes through
  them, and every outcome reports completed / blocked / refused /
  cancelled with the travel admitted.
- The tree names the joint coordinate a part rides in the operation of
  the node it hangs from: `units.input` carries
  `['r', 'units.input.turn', [1, 0, 0]]`, and `units.input.dial` is a leaf
  under it. The viewer already composes those matrices, so the joint's
  world axis and origin are one `matrixWorld` away.
- `program.sources` is the reaching-inputs table (which inputs move each
  coordinate) and `program.coordinates[*].domain` says `rotational`.

## 2. Why the viewer cannot infer this on its own

Two facts from the module's document rule out "every part whose coordinate
one input reaches is a handle for that input":

- **Reaching is ambiguous where it matters.** `units.input.turn` is
  reached by `units_entry` alone, but `tens.input.turn` is reached by
  `tens_entry` *and* `units_entry` — the carry from the column below
  moves the tens dial too. The document cannot say which of the two a hand
  on the tens dial means. Only the author can.
- **Not every moving part may be touched.** The number drum turns, but a
  hand does not turn it: it sits under the lid, and the ratchet is on the
  input arbor, not on it. A viewer that made every posed part draggable
  would let a maker do to the model what the machine forbids.

So the binding is a declaration, made by the author beside the
instructions, and published in the document. The geometry of the gesture
(axis, origin, direction) is *not* declared: the tree already has it.

## 3. The framework: a `controls` declaration

Two control kinds, in the pilot's own 2026-09-12 spellings, declared on an
assembly exactly as `instructions` are:

```python
class Pascaline(AssemblyNode):
    time = Time.running()
    units_entry = Driver(default=0.0, unit='digit')
    ...
    instructions = {
        'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0),
        ...
    }
    controls = {
        'units dial':    Button(units.input.dial, 'Add one'),
        'tens dial':     Button(tens.input.dial, 'Add ten'),
        'hundreds dial': Button(hundreds.input.dial, 'Add hundred'),
        'turn units':    Turn(units.input.dial, units_entry),
        'turn tens':     Turn(tens.input.dial, tens_entry),
        'turn hundreds': Turn(hundreds.input.dial, hundreds_entry),
    }
```

- **`Button(part, instruction)`** — a press on `part` submits the named
  instruction. It is the panel's instruction button, moved onto the part;
  it carries no movement of its own. The name resolves in the declaring
  node's scope, the way instruction ids are qualified.
- **`Turn(part, input)`** — a drag on `part`, about the rotational
  coordinate the part rides, is a sequence of relative moves on `input`.
  The input is always named; the framework never guesses it from the
  reaching table (§2). `Slide` for a prismatic coordinate is the obvious
  sibling and is not proposed here.

Both take a **node**, referenced at class-body time the way
`units.drum.turn` already is, and qualified to a path through
`instance_path` the way driver ids are. A `part` not linked under the
declaring assembly is refused where it is written.

What the framework checks at compile time, and refuses with the facts:

- the part, or its nearest ancestor with a pose operation over a
  run-owned coordinate, gives the control its **coordinate**; a part that
  no run-owned coordinate poses is refused ("nothing the run owns moves
  this part");
- for `Turn`, that coordinate's domain must be rotational, and `input`
  must be in `program.sources[coordinate]` — refused otherwise, naming the
  inputs that do reach it;
- for `Button`, the instruction must be declared;
- controls are accepted only under a running root in this cycle. An
  untimed document's `trigger` exists too, but posing the pressed part
  from a target ramp is a different chrome and is out of scope; a
  `controls` table on a root without `Time.running()` is refused by name.

**The ratio is derived, not declared.** A `Turn` needs to know how far the
input travels per degree of the part, so that a sweep of one tooth asks
for one digit. The author would only be restating a relation the compiled
program already holds (`units.input.turn = -36 · units_entry`), and a
number stated twice is a number that drifts. The framework evaluates the
compiled program at the rest bank with `input` displaced by ±ε, checks the
two agree, and publishes `per_unit` (coordinate units per input design
unit: `-36.0` for each dial). Zero is refused: "the part does not move
with that input at rest". Caveat, stated in the spec: the ratio is
measured at rest. A law whose partial in that input changes with state
makes the pointer lead or lag the part; the part still moves exactly what
the run commits, so nothing is ever wrong, only less tight. The
alternative — an explicit `per_turn=` argument the framework checks
against the same measurement where it can — is one line away if the pilot
prefers a declared number.

## 4. The document: a `controls` table beside `instructions`

```json
"controls": {
  "units dial": {
    "kind": "button", "part": ["units", "input", "dial"],
    "instruction": "Add one",
    "joint": ["units", "input"], "coordinate": "units.input.turn", "axis": [1, 0, 0]
  },
  "turn units": {
    "kind": "turn", "part": ["units", "input", "dial"],
    "input": "units_entry", "per_unit": -36.0,
    "joint": ["units", "input"], "coordinate": "units.input.turn", "axis": [1, 0, 0]
  }
}
```

`joint` and `axis` are published so the viewer reads the gesture's
geometry off one node's world matrix rather than searching expressions for
the coordinate's name.

**Additive under version 5, no bump.** `document_version`'s own ladder
rule is the argument: `bindings` and `program` force a version because a
consumer that ignored them would pose the machine *wrongly*; `loop` and
`instructions` were additive because a consumer that ignored them still
rendered the truth. `controls` is of the second kind — a viewer that does
not read the table still drives the machine from its panel. The
capability gate a host needs is the viewer **API version**, which rises
(§5) exactly for "gains a capability a host may require". The program
identity is untouched: controls are presentation over the program, not
part of it, so the running corpus and every `identity` digest stay as
they are. Version 6 remains the pilot's option if a refused old viewer is
preferred to a silent one.

Baseline specs touched: `simulation` gains a requirement for the
declaration and its refusals; `export` gains one for the table and the
derived ratio. One ADR, in the simulation series, for "a control is a
declaration on the model, published beside the instructions, and the
gesture's geometry comes from the tree".

## 5. The viewer: a press and a turn on the part

One cycle, `drive-the-run-by-touch`, on the viewer:

- **Affordance.** A part named by a control gets a pointer cursor and a
  light emissive highlight on hover, and its control's name as a title.
  Every other part orbits the camera as it always has.
- **Press.** `pointerdown` casts a ray against control meshes only (each
  mesh gets a back-reference to its tree node at load; a part hidden or
  focused out by the navigator is not pressable). The pointer is captured
  and orbit is suspended for the gesture. `pointerup` inside a small
  movement threshold is a press: `run().trigger(instruction)`. The outcome
  is shown twice through one path — a transient label at the press point,
  and the panel's button for the same instruction, which already reports.
- **Turn.** Movement past the threshold is a drag. The pointer ray is
  intersected with the plane through the joint's world origin normal to
  its world axis; the angle about the origin, relative to the
  `pointerdown` angle, is the sweep. Each time the accumulated sweep
  crosses one **quantum** — the input's nudge amount times `per_unit`,
  one digit = 36° on a dial — one `move(input, {by: ±amount, duration})`
  is issued. A blocked outcome does not advance the sweep origin, so a
  drag against the ratchet reports blocked and leaves no backlog. The
  part never follows the pointer; it follows commits, so the pointer may
  run ahead and the dial catches up at the nudge's duration. The gesture
  ends on the same five sides as a jog. A camera edge-on to the plane
  falls back to the screen-space angle about the projected axis point.
- **Mount surface.** `partControls: 'inline' | 'none'`, separate from
  `driverControls`, because a host that builds its own panel still wants
  the dial pressable. `handle.controls()` lists the document's controls
  with each part's current screen rectangle, for hosts and for tests. API
  version rises by one.
- **Tests.** The planning is pure data in its own module (sweep to
  quanta, the blocked-origin rule, the plane fallback), tested in node
  like `runControls.ts`; the Playwright suite presses a dial on the
  fixture; the module's own acceptance is in §6.

Nothing in the widget writes a coordinate, and the posed chrome of
versions 1 to 4 reaches exactly the code it always did.

## 6. The module: turn the dials

- `controls` as in §3: three `Button`s on the existing instructions, three
  `Turn`s on the entries. Whether a press should take the instruction's
  one second or a faster project instruction is a knob, not a decision.
- `tests/test_browser.py` grows: press the units dial ten times through
  the mouse at the rectangle `handle.controls()` reports, read `010` as
  the buttons do today; drag the units dial one digit forward and read
  one; drag it back and read the blocked report and an unmoved drum.
- Out of scope, and said so: dialing by position (a stylus placed at
  digit *n* and turned to the stop enters *n*), which is the historical
  Pascaline's gesture and not this modular design's; the ratchet
  chirality finding; the end covers.

## 7. Order, homes and open decisions

| Cycle | Repository | Base | Depends on |
| --- | --- | --- | --- |
| `declare-controls-on-parts` | solid-node, worktree `WTs/controls-on-parts` | main `00398f4` | nothing |
| `drive-the-run-by-touch` | solid-node-viewer | the `viewer-navigator` branch head `644b504` (cycle 3 archived, API 11 → 12), or main once the pilot integrates that branch | the framework cycle's document |
| `turn-the-dials` | Pascaline-module | its main | both |

The shop needs no change: the studio mounts the widget and inherits the
behaviour; its e2e fake widget is API 4 and untouched.

For the pilot:

1. the spellings `Button` and `Turn` (the 2026-09-12 sketch's `Button`,
   plus one word for the drag);
2. derived `per_unit` (recommended) or a declared `per_turn=` the
   framework checks;
3. additive under version 5 (recommended) or a version 6 bump;
4. whether the viewer cycle waits for the navigator campaign's cycle 4 or
   branches from its cycle 3 head now.
