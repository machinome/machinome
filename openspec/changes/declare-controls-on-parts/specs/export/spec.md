## ADDED Requirements

### Requirement: A running document publishes the controls its parts carry

A version 5 document whose root's tree declares at least one control
SHALL carry a top-level `controls` object, beside `instructions`, keyed
by the control's QUALIFIED name and ordered by it, so republishing an
unchanged model produces a byte-identical document.

Each entry SHALL carry, in this order:

- `kind`: `"button"` or `"turn"`.
- `part`: the LIST of node names, from the document's root down, of the
  node a person touches — the names the document's own tree publishes,
  so a consumer walks to it without parsing a dotted string.
- for a button, `instruction`: the QUALIFIED instruction name, which
  SHALL be a key of the same document's `instructions` table.
- for a turn, `input`: the qualified driver id, which SHALL be a key of
  the same document's `drivers` table; and `per_unit`, defined below.
- `joint`: the LIST of node names of the node the control's coordinate
  poses.
- `coordinate`: that coordinate's qualified id, which SHALL be a key of
  `program.coordinates`.
- `axis`: the joint's axis, as three numbers in the joint node's OWN
  frame.
- `origin`: the point the joint moves the part about, as three numbers
  in the joint node's own frame — `[0, 0, 0]` where the line runs
  through that node's placed origin.

The entry SHALL NOT repeat the coordinate's `domain` or `unit`, which
`program.coordinates` publishes under the same id, and SHALL carry no
EXPRESSION, so the `controls` table SHALL NOT participate in the
document's `bindings` table and SHALL NOT change it.

`per_unit` SHALL be the coordinate units the part moves per DESIGN unit
the input travels, MEASURED from the compiled program at the REST BANK
with that input displaced by a small amount in each direction and by
nothing else. The two readings SHALL agree within a stated relative
window; a disagreement SHALL be REFUSED naming both readings, the
coordinate and the input. A measurement of ZERO in both directions SHALL
be REFUSED saying the part does not move with that input at rest. The
published value is a reading AT REST: a law whose response to that input
changes with state makes a pointer built on it lead or lag the part,
which costs the gesture tightness and never correctness, because the
part is posed only by what the run commits.

The table SHALL be ADDITIVE within version 5. It SHALL NOT move the
document's version, because a consumer that ignores it still drives the
machine from the declarations the document already published and still
renders the truth. A document whose tree declares NO control SHALL OMIT
the key entirely and SHALL be byte-identical to the document the
producer publishes without this table, for every version — 1, 2, 3, 4
and 5 alike. The compiled program's `identity`, ordering and published
shape SHALL be unchanged by the presence or absence of a control, so a
snapshot taken against a program is neither refused nor accepted
differently because one was declared.

A control whose part THIS render OMITTED SHALL be left out of the table
rather than refused, because the document does not contain that part;
every other unresolvable part is refused where the control is declared.

The producers that publish the model's own declarations — the build's
`viewer.json` and the export's `manifest.json` — SHALL publish this
table. The headless browser-snapshot capture SHALL NOT: it bakes one
instant and already publishes an empty `instructions` table, and a
button naming an instruction that document does not list would be
inconsistent.

#### Scenario: A running document publishes its controls

- **WHEN** a running root declaring
  `controls = {'units dial': Button(units.dial, 'Add one'),
  'turn units': Turn(units.dial, units_entry)}` is built and exported
- **THEN** each document carries a `controls` object with those two
  keys, the button entry naming `Add one` — a key of its own
  `instructions` table — and the turn entry naming `units_entry`, a key
  of its own `drivers` table

#### Scenario: The gesture's geometry comes from the tree

- **WHEN** the part is a leaf under a node posed by
  `turn = Revolute(axis=(1, 0, 0))`, at ratio `-36` from its input
- **THEN** the entry's `part` is the leaf's node-name path, `joint` is
  the posing node's node-name path, `coordinate` is that node's joint
  coordinate id, `axis` is `[1, 0, 0]`, `origin` is `[0, 0, 0]`, and
  `per_unit` is `-36.0`

#### Scenario: An off-centre joint publishes the point it turns about

- **WHEN** the posing node declares `Revolute(axis=(1, 0, 0), at=(0, 3, 0))`
- **THEN** the entry's `origin` is `[0, 3, 0]` — the point the placement
  turns the part about, in that node's own frame — and `axis` is still
  `[1, 0, 0]`

#### Scenario: A part reached by two inputs publishes the declared one

- **WHEN** a coordinate is reached by two inputs and the author declared
  `Turn` against one of them
- **THEN** the entry's `input` is the declared one and `per_unit` is
  measured against that input alone, the other input's contribution
  being held at zero

#### Scenario: A document with no controls is unchanged in every byte

- **WHEN** a running root declaring no control, a looping root and an
  untimed root are each published
- **THEN** none of the three documents carries a `controls` key, each
  declares the version it declared before this change, and each is
  byte-identical to the document published before this change

#### Scenario: The program and the corpus are untouched

- **WHEN** a running root's controls are added, changed or removed
- **THEN** its `program` object — `identity`, `coordinates`, `edges`,
  `spans`, `sources` and `limits` — is unchanged in every byte, and the
  regenerated conformance corpus is identical to the committed one

#### Scenario: A part does not move with its input at rest

- **WHEN** a `Turn` names an input whose displacement at the rest bank
  moves the control's coordinate by nothing
- **THEN** publication is refused naming the part, the input and the
  coordinate, and saying the part does not move with that input at rest

#### Scenario: A part the render omitted drops its control

- **WHEN** a parameter makes the render omit the part a declared control
  names
- **THEN** the published document's tree does not contain that part, its
  `controls` table has no entry for that control, the other controls are
  published unchanged, and the build is not refused

#### Scenario: Republishing an unchanged model changes nothing

- **WHEN** a running model carrying controls is published twice
- **THEN** the two documents are byte-identical, the `controls` table's
  key order and each entry's field order included

#### Scenario: A baked capture publishes no controls

- **WHEN** a running root carrying controls is captured with the
  headless browser snapshot
- **THEN** that document carries no `controls` key, exactly as it
  carries an empty `instructions` table, and is otherwise the document
  the capture published before this change
