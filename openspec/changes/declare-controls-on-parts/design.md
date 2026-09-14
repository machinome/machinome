# Design — declare controls on parts

## Context

### What already exists

- **The declaration surface.** An assembly declares `instructions` as a
  plain class-body dict; `enumeration.qualified_instructions(root)`
  walks the linked tree with `drive_tree` and returns
  `{qualified name: (node, path, instruction)}`, a root-declared
  instruction keeping its bare name. `Sim.__init__` calls it once and
  holds the result as `sim.instructions`;
  `serializer.instructions_table` publishes it, qualifying each local
  target name through the declaring node's path with the same
  `driver_id` that keyed the drivers table.
- **Class-body paths.** `units.input.dial`, written in a class body, is
  not a value: `ChildDeclaration.__getattr__` calls
  `couplings.read_through`, which admits a port, a joint, a derived
  coordinate or another child declaration and refuses a parameter or a
  driver, and returns a `PathRef(root_declaration, segments, terminal)`.
  Every segment is checked against the class the previous segment names,
  AT CLASS DEFINITION, so a misspelt segment is a class-definition error.
  `PathRef._walk(instance)` resolves the path against the realized tree;
  `PathRef.check_declared_on(owner, relation)` refuses a first segment
  the owner does not declare as a child. A probe on this worktree
  confirms `Columns.units.dial` is a `PathRef` with segments `('dial',)`
  and terminal `<declared Block dial>`, that `_walk` returns the realized
  leaf, and that `qualified.instance_path(leaf, root)` is
  `('units', 'dial')` — the same names the document's tree publishes.
- **`NodeMeta.__new__`** already validates class-body declarations where
  they are written: it pops the recorded relations out of the namespace,
  refuses them on a non-assembly, and calls `relation.check_declared_on(cls)`
  on each, "because the class exists now, so its own ports, joints,
  drivers and children can be enumerated". It reaches `AssemblyNode`
  through a local import taken only by a class that carries relations, so
  no import edge is added for anything else. It imports nothing from
  `solid_node/simulation/`, and that one-way rule is why
  `DriverDeclaration` is a node-layer marker the simulation layer's
  `Driver` subclasses.
- **The compiled program** (`simulation/program.py`).
  `compile_program(root, inputs, coordinates)` is called once from
  `Run.__init__`, after the untimed rest render. `Program` holds
  `inputs`, `coordinates`, `nodes` (`{key: _Node(name, kind)}` over
  inputs, bank coordinates and intermediates), ordered `edges`, `spans`,
  `sources` — the inputs that reach each node key — and an `identity`
  digest over `described()`. `Program.published(initial)` is the version
  5 `program` object.
- **The tick's arithmetic.** `Run._values(bank)` is the bank plus every
  intermediate a compiled edge determines, recomputed rather than
  stored; `Run._deltas(admissions)` seeds one displacement per input;
  `Run._pass(values, deltas, found, tick)` propagates once over the
  ordered edges through `edge.increments(values, deltas)`, which is
  `f(end) − f(start)` for a continuous law and the jump plan's
  subtracted sum for one that jumps. `_pass` is the whole of the tick's
  propagation; the segment loop around it is stops and staging.
- **Joint placement.** `Joint.place(node, value)` places ONE contiguous
  run of operations at the joint's own slot on the node the joint is
  declared on — for a SITE-declared joint, the child the site handed it
  to, which is the node `qualified_coordinates` reports as that
  coordinate's owner. A `Revolute` places `translate(-anchor)`,
  `rotate(value, axis)`, `translate(anchor)`, omitting the two
  translations when the line runs through the node's placed origin. A
  site joint's axis and anchor are carried into the node's own frame by
  `_carry` before the placement is built, so `joint.axes(node)` and
  `joint.carried_points(node, anchor)` are exactly what `place` used.
- **The published document.** Three producers share `document_body`:
  `core/builder.py` (the build's `viewer.json`), `core/export.py`
  (an export's `manifest.json`), and `viewers/browser.py` (the headless
  web-snapshot capture). `document_body` builds `format`, `version`,
  `animation`, `drivers`, `instructions`, then `bindings` when the
  binding pass found something to share, then `program` under a running
  root; the producer adds `root` and `pieces`. `document_version` reads
  the version off the finished content and is overruled by `program`.
- **The acceptance project**, read-only: the Pascaline module. Its
  published `_build/viewer.json` is version 5;
  `program.sources['tens.input.turn']` is `['tens_entry', 'units_entry']`;
  `units.input` carries `['r', 'units.input.turn', [1, 0, 0]]` and holds
  the leaves `shaft`, `gear`, `ratchet` and `dial`.

### The authority

`workflow/docs/controls-on-parts.md` §3 (the declaration and its
refusals), §4 (the document shape) and §7 (the cycle order), with the
pilot's 2026-09-14 answers to its four open decisions: the spellings
`Button` and `Turn`; `per_unit` derived, not declared; additive under
version 5, the viewer API version being the capability gate; sequencing
settled elsewhere. Behind it, the 2026-09-12 ratification in
`workflow/open-run-simulation/design.md` ("Inputs, instructions and
controls") and ADR-048's Consequences in the viewer.

That note is not ratified and this document is where it and the
framework's own records are reconciled. §9 lists every place this design
departs from it, and why.

## Goals / Non-Goals

**Goals:**

- An author states, beside the instructions, which parts a person may
  press and which parts a person may turn, and against which instruction
  or which input — in the tree's own vocabulary, with no second list to
  keep in step.
- The framework derives everything a consumer needs to draw and drive
  the gesture: the coordinate, the joint node, the axis, the point it
  turns about, and how far the input travels per unit of coordinate.
- Every mistake is refused with the facts, as early as the facts exist —
  at class definition where the classes are known, at compile where the
  program is known.
- The compiled program, the corpus, and every document published today
  are untouched, byte for byte.

**Non-Goals:**

- Any movement of its own. A control names a request the run already
  accepts; ownership, admission, stops and outcomes are the rules
  `trigger`, `move` and `rate` already state, unchanged.
- `Slide` (a prismatic drag), a control on an untimed or looping root,
  a control the author may present or label beyond its name, a Python
  API for issuing a control's gesture, and any viewer behaviour. The
  viewer's pick, drag, quantum and affordance are
  `drive-the-run-by-touch` in `solid-node-viewer`.
- Anything depending on `handle.cancel()`, which is a filed and
  untriaged wart.
- A control on a part posed by a joint owning several coordinates, or by
  a node declaring several joints. Both are refused by name, and both
  are compatible extensions.

## Decisions

### 1. `Button` and `Turn` are declared in a `controls` mapping, and qualify like instructions

```python
class Pascaline(AssemblyNode):
    time = Time.running()
    units_entry = Driver(default=0.0, unit='digit')
    units = DecimalModule(...)

    instructions = {'Add one': Instruction(by={'units_entry': 1.0}, duration=1.0)}
    controls = {
        'units dial': Button(units.input.dial, 'Add one'),
        'turn units': Turn(units.input.dial, units_entry),
    }
```

`controls` is a plain class-body dict, exactly as `instructions` is, and
it inherits exactly as `instructions` does: a subclass that assigns
`controls` replaces its base's table whole, which is the rule
`getattr(node, 'instructions', {})` already gives. No new inheritance
rule is introduced.

The enumeration is the instruction enumeration's twin, and shares its
walk. `drive_tree`'s `visit` already exists so "a caller that also needs
something else declared per node pays for one walk rather than two", and
`Sim.__init__` needs both tables. So `qualified_instructions` and a new
`qualified_controls` become thin faces over one
`qualified_declarations(root)` returning `(instructions, controls)`,
each keyed by the declaring node's instance path joined with the
declared name — `'units dial'` on the root, `'column.units dial'` one
level down — and carrying `(node, path, control)`.

A control's INSTRUCTION reference qualifies through the SAME path, so
`Button(dial, 'Add one')` declared on a child at `('column',)` names
`'column.Add one'`, which is a key of the instructions table by
construction rather than by two schemes agreeing. This is
`instructions_table`'s own rule for target names, applied to a name
instead of a target.

*Alternative rejected:* registering each control at construction the way
`record_relation` registers a relation. A relation is a STATEMENT and has
no name; a control is an entry in a named table, and the name is the
label. Registering at construction would double-record a control built
outside the dict and would put the dict's key out of reach.

### 2. A part is a node reference, checked where it is written

`Button`/`Turn` accept a `ChildDeclaration` (`Button(units, ...)`) or a
`PathRef` through child declarations (`Button(units.input.dial, ...)`),
normalized to a `PathRef` exactly as `couplings.coordinate_ref` does
for a bare child. Anything else is refused in the constructor, naming
what was written: a coordinate ("a control names a PART — a node whose
geometry a hand touches — not a coordinate"), a `Driver`, a
`RepeatDeclaration` or a `BroadcastRef` ("a repeated child names one
part per copy"), a list-held child, or a plain value.

`read_through` has already done the hard half before `Button` is even
called: every segment of `units.input.dial` was checked against the
class the previous segment names, so a misspelling raises at the line
where it is written. What remains — that the FIRST segment is a child
the DECLARING class holds — needs the class, which does not exist while
its body runs.

So `NodeMeta.__new__` validates the table, immediately after
`super().__new__` creates the class and `__set_name__` has run over
every declaration, in the same place and for the same reason it
validates relations. It reads `namespace.get('controls')`, duck-typing a
control on its own `control_kind` attribute — the file's own documented
style, which recognizes a coordinate by "it IS a port declaration" and a
joint by "it OWNS one" rather than importing either — and calls
`control.check_declared_on(cls, name)`. That keeps
`solid_node/node/` importing nothing from `solid_node/simulation/`,
which is the invariant `DriverDeclaration` exists to preserve.

The control implements `check_declared_on` itself rather than delegating
to `PathRef.check_declared_on`, whose message says "in the relation" and
"A path is walked from the instance stating the relation". It performs
the same `declared_children(owner)[first] is ref.root` test and says
"in the control 'units dial'" instead.

`controls` therefore becomes a RESERVED class-body name on node classes,
like `instructions`: a `controls` attribute that is not a mapping of
names to controls is refused naming the entry. A grep over this
worktree and over every project in the workspace finds exactly one
occurrence of `controls =`, a local variable inside a clock test, and no
node-class attribute. The cost of the reservation is a rename in a
project that had used the name; the benefit is that a mistyped control
table is never silently inert.

`NodeMeta` also records `cls._declares_controls`, `True` exactly when
the class's own `controls` table is non-empty — so a subclass that
assigns `controls = {}` reads `False`, and a subclass that assigns
nothing inherits its base's flag along with its base's table. It is the
only thing §5 needs to refuse a control under a non-running root without
importing the simulation layer into a document walk.

### 3. `Turn`'s input is a `Driver` declared on the declaring class

`Turn(units.input.dial, units_entry)` receives the `Driver` DECLARATION
object. At `NodeMeta.__new__` time `__set_name__` has run, so
`declared_drivers_of(cls)` finds it by identity and gives its qualified
id through the declaring node's path. A `Driver` the declaring class does
not declare is refused naming the class's declared drivers; a string is
refused saying an input is named by its declaration.

That has a consequence worth stating: a root CANNOT name a driver
declared on a child, because reading one off a child declaration is
already refused by `read_through` ("a driver is addressed by the
qualified id its position in the tree gives it, and a second address for
one value is what that qualification prevents"). The author declares the
control on the assembly that declares the input, and it qualifies down
from there — which is exactly what an instruction over a child's driver
already does.

*Alternative rejected:* accepting a qualified id string, which would
give a driver a second address and reopen the hole
`solid_node/node/qualified.py` exists to close.

### 4. The part's coordinate is the nearest posing joint, and v1 names one

From the realized part node, walk `_parent` up to the root. The first
node — the part itself included — that declares a joint whose coordinate
the run banks OWNS this control's coordinate. In the Pascaline the dial
declares none, its parent `units.input` declares `turn`, and
`units.input.turn` is in the bank.

Three narrowings, each refused by name:

- **Nothing posing.** No ancestor-or-self declares a banked joint
  coordinate: "nothing the run owns moves this part". A part moved only
  by an author's own `render()` arithmetic over a plain port is in this
  case deliberately — a control's gesture is a JOINT's motion, and a
  hand-written rotation is not one.
- **Several joints on the posing node.** Two joints compose one motion
  and neither is "the" coordinate. Refused naming both.
- **A joint owning several coordinates** (a `Free`). Refused naming
  them.

Under those narrowings the coordinate is ALWAYS BARE in its joint's own
operation, which answers the brief's question about a coordinate that
appears inside an expression. `Joint.place` builds the placement from
`value`, and under a running root `value` is the symbolic token of that
coordinate's own qualified id, so a `Revolute` publishes
`['r', '<id>', axis]` and a `Prismatic` publishes a translation whose
non-zero components are that id. A coordinate reaching an operation
INSIDE an expression happens when a joint owns several — a `Free`'s six
— and that is the case refused above. There is therefore no expression
to search and no ambiguity to resolve, and the framework never has to
parse a published operation to find the gesture.

Both narrowings are compatible extensions: a later cycle can publish a
control's coordinate CHOSEN among a composed joint's, or a `Free`'s
named part, without changing an entry that exists today.

### 5. `Turn` additionally requires rotational, reaching, and a run

- The coordinate's port domain must be `rotational` — the same value
  `program.coordinates[id].domain` publishes. A `Prismatic` is refused
  saying `Slide` is not in this release.
- The input must be in `program.sources[coordinate]`. Refused otherwise
  naming the coordinate and the inputs that DO reach it. This is the
  refusal the Pascaline earns: `Turn(hundreds.input.dial, units_entry)`
  names an input that genuinely reaches `hundreds.input.turn` and is
  admitted; an input that reaches nothing of the part is not.
- Reaching is necessary and not sufficient, exactly as it is for a
  stop's blocked group: an input coupled only through a disengaged law
  reaches a coordinate and moves it not at all. §6's ratio is what
  catches that, at rest.

A control under a root that does not declare `Time.running()` is refused
by name in two places, both of which every real project passes through:
`Sim.__init__`, before any run is built, and `symbolic_document`'s walk,
which visits every ASSEMBLY of the tree it publishes and can read
`type(target)._declares_controls` without importing anything. A control
on a leaf is not a case: a leaf declares no children, so
`check_declared_on` refuses its part at class definition. A tree that
declares a control, declares NO driver and is not running is never
walked at all and publishes the document it always did; that tree is
vacuous — a `Turn` names a driver on its own class and a `Button` names
an instruction, which targets one — and the gap is recorded here rather
than paid for with a structural walk on every publication.

### 6. `per_unit` is measured off the compiled program, at rest, both ways

The measurement must not build a `Sim`. `program_of(root)` deliberately
asks a LIVE run for its program rather than constructing one, because
"publication SHALL succeed over a tree a live running simulation owns
and SHALL leave that simulation's ownership, bank and ability to advance
intact", and constructing a `Sim` RELEASES whatever run owns the tree.
So the ratio is pure arithmetic over the compiled program, off the tree
entirely:

```python
Program.response(bank, input_id, epsilon)
```

is `Program.values_of(bank)` (the bank plus every intermediate a
compiled edge determines) seeded with one displacement on one input, then
one ordered pass over `edge.increments(values, deltas)` — the tick's own
propagation with no command, no stop, no staging and no record. A probe
on this worktree measured it against the run itself: on a
Pascaline-shaped fixture, `response(rest_bank, 'units_entry', 1e-3)`
gives `units.turn` exactly `-0.036000000000000004`, and a real
`sim.move('units_entry', by=1e-3, duration=0)` on a fresh simulation
moves it by exactly the same double.

`Run._values` and `Run._deltas` MOVE to `Program` as `values_of` and
`deltas_of`, with `Run` delegating, so "the bank plus the intermediates"
and "one input's displacement" have one implementation rather than two
to keep in step. `Run._pass` stays where it is: it owns conflict
detection and the messages a failed TICK needs, which a measurement does
not have and must not borrow. The corpus replay is the guard that the
move changed nothing.

- **ε is stated in the input's DESIGN units** — `per_unit` is coordinate
  units per input design unit — and is `2**-20`, a power of two so the
  division is exact and an affine chain publishes `-36.0` rather than
  `-36.000000000000004`. A probe confirms both signs read exactly
  `-36.0` at that ε on a chain of one wiring edge.
- **For an integer-typed input ε is raised to one native unit** —
  `scale` design units, or `1.0` with no scale — because `Driver.native`
  rounds a design-unit displacement to whole native units ONCE, and a
  displacement below half a native unit is no displacement at all.
- **Both directions are read.** `forward = response(+ε)[coordinate] / ε`
  and `backward = response(-ε)[coordinate] / -ε`. Both zero is REFUSED:
  "the part does not move with that input at rest". A disagreement
  beyond a stated relative window is REFUSED naming both readings, the
  coordinate and the input: a law whose response at rest is not one
  number gives the gesture no single scale, and a drag scaled by the
  other direction's number would be wrong in one direction.
- **The window is `1e-3` relative**, a module constant of its own, NOT
  the program's `agreement` (`1e-9`). `agreement` is the window inside
  which two increments of ONE movement are called equal; this is a
  two-sided finite difference over a law that is allowed to curve, and
  `1e-9` would refuse every smooth non-affine law — which the authority
  explicitly permits ("A law whose partial in that input changes with
  state makes the pointer lead or lag the part; the part still moves
  exactly what the run commits, so nothing is ever wrong, only less
  tight"). `1e-3` catches a kink, a jump and a one-way law at rest and
  admits curvature.
- **The published number is the FORWARD reading**, and the spec says it
  is measured at rest. A mean would be a number neither direction
  produced.

*Alternative rejected:* a declared `per_turn=` the framework checks. It
is one line away if the pilot changes his mind, and the pilot has
already answered.

### 7. The document: a top-level `controls` table, additive, absent when empty

```json
"controls": {
  "turn units": {
    "kind": "turn",
    "part": ["units", "input", "dial"],
    "input": "units_entry",
    "per_unit": -36.0,
    "joint": ["units", "input"],
    "coordinate": "units.input.turn",
    "axis": [1.0, 0.0, 0.0],
    "origin": [0.0, 0.0, 0.0]
  },
  "units dial": {
    "kind": "button",
    "part": ["units", "input", "dial"],
    "instruction": "Add one",
    "joint": ["units", "input"],
    "coordinate": "units.input.turn",
    "axis": [1.0, 0.0, 0.0],
    "origin": [0.0, 0.0, 0.0]
  }
}
```

- **Top level, beside `instructions`, not inside `program`.** A control
  is presentation over the program, not part of it: the run computes the
  same numbers whether or not a control exists. Keeping it out of
  `program` is also what keeps the conformance corpus untouched — the
  fixture copies "the published document's program-bearing keys —
  `format`, `version`, `drivers`, `instructions`, `bindings` and
  `program`", and `controls` is not one of them.
- **`part` and `joint` are LISTS of node names**, not dotted strings,
  because a node name is not always a legal identifier
  (`<attribute>-<index>` for a list-held child) and a consumer walks the
  document's tree by `name` anyway. `coordinate` and `input` are dotted
  qualified ids, because they are expression names and must be.
- **The key is absent when the table is empty**, exactly as `bindings`
  is. That is what makes "every existing version 1 to 5 document stays
  byte-identical" true by construction rather than by inspection.
- **The version does not move.** `document_version`'s own ladder rule is
  the argument: `bindings` and `program` force a version because a
  consumer that ignored them would pose the machine WRONGLY; `loop` and
  `instructions` were additive because a consumer that ignored them
  still rendered the truth. `controls` is of the second kind — a viewer
  that does not read the table still drives the machine from its panel —
  and the capability gate a host needs is the viewer's own API version,
  which rises in the next cycle. Version 6 remains the pilot's option
  (§10).
- **No `domain` field**, because `program.coordinates[coordinate].domain`
  already carries it under the same id, and the export spec's own rule
  for the program is that no declaration field is repeated.
- **No expression anywhere**, so the table does not enter
  `bind_document` and the `bindings` pass is untouched.
- **Ordered by qualified control name**, and each entry's keys in the
  fixed order above, so republishing an unchanged model is byte-identical.

### 8. `origin` beside `axis` — a deviation, with its reason

The authority's §4 publishes `joint`, `coordinate` and `axis`, reasoning
that "the viewer reads the gesture's geometry off one node's world
matrix". That is true for a joint whose line runs through the node's
placed origin — the case of a wheel on its own bearing, which is the
Pascaline's — and only that case. `Revolute.placement` composes
`translate(-anchor)`, `rotate(value, axis)`, `translate(anchor)` when
`at=` puts the line elsewhere, so the node's world origin is NOT on the
axis and a viewer holding only `axis` would rotate the drag about the
wrong line. A probe on this worktree with `Revolute(axis=(1,0,0), at=(0,3,0))`
publishes operations `[['t', [-0,-3,-0]], ['r', ..., [1,0,0]], ['t', [0,3,0]]]`
— the anchor is present in the document, but only as two translations a
consumer would have to recognize and subtract.

So the entry carries `origin`: the point the joint turns about, in the
JOINT NODE's own frame, being exactly the anchor `Joint.place` used —
`joint.carried_points(node, joint.arguments(node)[1])` with the
site-declared carry applied, the same values that built the placement.
`axis` is `joint.axes(node)` under the same carry. A consumer then
computes the world line as `matrixWorld · origin` and
`matrixWorld · axis` with no case analysis, and the Pascaline's entries
read `[0, 0, 0]` — the authority's own picture, plus one triple that
makes the general case work.

This is the only departure from §4's document shape, and it is an
ADDITION: an entry with `origin` is a superset of the entry the viewer
cycle was written against.

### 9. Which producers publish it

`document_body` gains a `controls` argument beside `instructions`.
`core/builder.py` and `core/export.py` pass the table they just
compiled from the program. `viewers/browser.py` — the headless
`solid snapshot --renderer web` capture — passes none.

That is a deviation from the authority's brief, which expected all three
producers to publish it, and the reason is the capture itself: it BAKES
one instant, its tree holds numbers rather than expressions, it never
calls `symbolic_document`, and it already publishes an EMPTY
instructions table for that reason. A `Button` naming an instruction
that the same document does not list would be an inconsistent document,
and a still capture offers no `handle.run()` for a press to reach. The
capture's document is otherwise unchanged, which is also the cheapest
thing to be true.

### 10. An omitted part drops its control rather than refusing the build

`omit()` leaves a node "not linked, built, exported, fused or
serialized", and structure "may vary with parameters, never with time".
A part a build omits therefore has no instance path and is absent from
the document's tree. Refusing the build would mean `--set covers=false`
on a machine with a control on the lid could not build at all.

So a control whose part THIS render omitted is left out of the published
table, deterministically and without an error, because the document
genuinely does not contain that part. Every other way a part could fail
to resolve was already refused at class definition (§2), so this rule
cannot hide a misdeclaration.

### 11. The identity, the corpus and the docs

`Program.described()` — the canonical listing the `identity` digest is
taken of — is NOT touched. A control changes nothing the run computes,
so a snapshot taken against a program must not be refused because a
control was added or removed. The conformance corpus, its machines, its
format and its coverage guard are likewise untouched: `tools/generate_running_corpus.py`
passes no controls, `tests/running-corpus.json` must regenerate
byte-identical, and no corpus machine gains a control.

The framework's own documentation gains a "Controls: pressing and
turning the part itself" section in `docs/driving.rst`, immediately
after "Instructions", where the button-per-instruction convention is
already explained; a cross-reference from `docs/scenarios.rst`'s running
section; `Button` and `Turn` in `docs/api-reference.rst` beside
`Instruction`; a changelog entry; and a sentence each in
`docs/architecture.md`'s Simulation and Export sections.

## Risks / Trade-offs

- **`controls` becomes a reserved class-body name.** → A grep over this
  worktree and every project in the workspace finds no node class using
  it. The refusal names the offending entry and the reservation, so a
  project that had one learns it at class definition rather than at
  render.
- **Moving `_values`/`_deltas` off `Run` touches the tick's hot path.**
  → They are pure functions of program-derived state and the move is
  mechanical; the corpus replay reproduces every tick of every fixture
  machine exactly, and the cost probe from the run-owns-the-coordinates
  cycle is re-run to show the per-tick cost did not move.
- **`per_unit` is a reading at rest and a curved law makes the pointer
  lead or lag.** → Stated in the spec and accepted by the authority. The
  part still moves exactly what the run commits; the two-sided check
  catches the cases where the number is meaningless rather than merely
  approximate.
- **The narrowings of §4 refuse machines a maker might reasonably
  build** — a part on a composed joint, a part on a `Free`. → Each is
  refused by name with what the joint declares, and each relaxation is
  additive to an entry that already exists. None of the campaign's
  projects has a control on such a part.
- **A `Button` requires the part to be posed by the run**, so a fixed
  plate cannot be a press target. → The authority states the rule for
  both kinds. §12 puts it to the reviewer; relaxing it later is additive
  (`joint`, `coordinate`, `axis` and `origin` would read `null`).
- **The declaration is validated in two places** — class definition and
  compile. → That is where the facts are: the classes are known at
  definition and the program is not. It is the same split `relation`
  already has between `check_declared_on` and the fixpoint's own
  refusals.

## Open Questions

1. **Should a `Button` be allowed on a part nothing moves?** A press
   carries no gesture geometry, so the requirement that a run-owned
   coordinate pose it is a real restriction on, say, a fixed start
   plate. This design keeps the authority's rule (both kinds require
   it). Relaxing it is additive.
2. **Version 6 instead of additive?** The authority recommends additive
   and the pilot answered additive. Recorded so the reviewer sees it was
   a choice: an old viewer that ignores `controls` drives the machine
   from its panel and renders the truth, which is why the version does
   not move.
3. **`origin` (§8).** The one departure from the authority's published
   shape. The viewer cycle has not been written yet, so adopting it now
   costs nothing there.
4. **Should `Sim` expose `sim.controls`?** This design does not add it:
   nothing in the cycle needs it, and a Python-side control API is the
   viewer's business. A test reads `program.controls` and the published
   table.
5. **Should a control be able to state a duration or a label distinct
   from its name?** Out of scope here; the authority calls presentation
   customization a later freedom.

### Reviewer decisions, 2026-09-14

Ruled at the ratification gate the pilot delegated (adversarial review
in place of presenting the artifacts), so implementation does not wait
on them:

1. **Kept.** A `Button` requires a part the run poses. The Pascaline,
   the Curta and every campaign project press a part that moves;
   relaxing this later is additive, and the entry's geometry fields
   would then read `null`.
2. **Additive under version 5**, as the pilot answered.
3. **`origin` adopted.** The viewer cycle has not been written; its
   brief will name the field.
4. **No `sim.controls`.** Tests read `program.controls` and the
   published table.
5. **Deferred**, as proposed.

Two corrections were folded in during review: `_declares_controls`
reflects the class's OWN table (§2, task 3.2), and the base running
document of task 0.4 is captured but never committed before commit 2.
Verified against the originating project: `carried_column` is
`DIGIT_STEP * entry + handed_on(below)`, affine in the column's own
entry, so both dials publish `per_unit` `-36.0` under §6 and
`Turn(tens.input.dial, units_entry)` is the zero-at-rest refusal.

## The ADR to extract

One, in the simulation series, after implementation:

**ADR-112 — A control is a declaration on the model, published beside
the instructions, and the gesture's geometry comes from the tree.** An
author says which part is pressed and which part is turned, and against
what; the framework refuses what it cannot resolve, derives the ratio
from the compiled program at rest rather than letting a second number
drift, and publishes the table additively because a consumer that
ignores it still renders the truth. Depends on 105 and 110, cites 048
(viewer) and 111.

Do not write it now.
