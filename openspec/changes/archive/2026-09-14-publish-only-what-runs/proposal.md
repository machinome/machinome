## Why

A running root's document cannot be published when the model states a
relation into a coordinate the program does not compute. Two shapes of
machine hit it, both filed in `workflow/warts.md` and both reproduced
against this worktree in `evidence.md`:

- **A `.repeat()` child's port.** The pin tumbler lock
  (`projects/Locks/Pin_tumbler_lock`, "Pin tumbler lock (2026-09-14,
  migration to `Time.running()`)") drives its five pen springs' `height`
  port from the pin that compresses them. Publication refuses:

      UnsupportedLaw: the program names 'PenSpring.height', which is a
      FALLBACK derived from a class name rather than an instance path ...
      Hold the node on its own attribute of its parent.

- **A relation onto a part this render omits.** The
  `declare-controls-on-parts` cycle met it building a fixture
  ("A relation onto a coordinate the render OMITS makes a running root's
  document unpublishable"). A machine with an optional subassembly whose
  joint a driver reaches cannot build at all with that option off, under
  a running root, even though the part is simply absent. The same
  refusal, naming `Arbor.turn`.

Both are one defect. `compile_program` creates a program node for EVERY
end of EVERY candidate relation before `_reaching_the_bank` drops the
candidates that reach no bank coordinate, and `Program.nodes` keeps the
dropped edges' ends. So the compiled program carries coordinates nothing
in it computes, and the three things that read `nodes` — the published
`intermediates`, the published `sources`, and the refusal
`_refuse_unqualified` — all see them.

The advice in the refusal is inapplicable in both cases: the omitted
node IS held on its own attribute of its parent, and a repeat copy IS
linked, under the list-held name `springs-0` that the qualified-id
grammar refuses. Neither node is anything the run computes — the run is
untouched, because the edge was never compiled. Only publication
refuses.

The framework already says what this change makes true. The export
capability defines `intermediates` as "the sorted qualified ids of every
value A COMPILED EDGE DETERMINES that the bank does not hold", and the
simulation capability says a relation that reaches no bank coordinate
"SHALL be left to the ordinary enumeration". Today the fixture
`Gauged` — whose own scenario is in the export spec — publishes
`gauge.angle` as an intermediate with no edge computing it and an empty
`sources` entry, and `Train` publishes `wheel.turn` the same way. The
implementation publishes more than the ratified definition allows.

## What Changes

- **The compiled program holds only the coordinates it computes over.**
  After the candidates that reach no bank coordinate are dropped, the
  program's coordinate table is the bank plus the ends of the edges that
  survived. An end of a relation left to the ordinary enumeration is not
  a coordinate of the program.
- **A `.repeat()` child may own a port a relation drives, under a
  running root.** The relation still runs through the ordinary
  enumeration exactly as it does today, on every copy; the document
  publishes, and names none of the copies.
- **A part this render omits no longer makes the document
  unpublishable**, where the relation onto it reaches no bank
  coordinate — which is every relation whose only driven end is that
  part's own joint, since an omitted node's coordinates are not in the
  bank.
- **The published `intermediates` and `sources` lose the names nothing
  computes.** Three existing fixtures publish one today: `Train`
  (`wheel.turn`), `Gauged` (`gauge.angle`) and `PortDrivenJoint`
  (`register`). Measured: no expression in any of those documents reads
  the name it loses, and none of them is a `bindings` entry.
- **A coordinate the program DOES compute and cannot qualify is still
  refused, unchanged.** Where a kept edge reads or gives an unqualified
  end — an omitted node's coordinate that a bank-reaching chain passes
  through — `_refuse_unqualified` refuses with the message it has today.
  That refusal is right: the document would have to name that value,
  and a class-name fallback is not unique across two instances.
- **`program.identity` does not move**, so no snapshot taken against an
  existing program is invalidated. The identity is a digest of
  `described()`, which reads the inputs, the coordinates, the spans and
  the edges and never the coordinate table.
- **Nothing about the run changes.** The tick, the admissions, the
  stops, the jumps and the control measurement address the program
  through its bank ids and its edges' own keys, none of which move.
- **BREAKING for a consumer that reads the published names.** A version
  5 document of one of those three shapes loses an `intermediates` entry
  and its `sources` entry. Both are names nothing in the document reads,
  so a consumer that resolves expressions is unaffected; a consumer that
  enumerates `intermediates` for display sees one fewer. The document
  version does not move: version 5 already defines `intermediates` this
  way.
- **Out of scope, and still refused: a `.repeat()` child that owns a
  JOINT.** Measured in `evidence.md`: that is refused earlier and
  elsewhere — `qualified_coordinates` raises `DriverIdError` from the id
  grammar while the bank is being enumerated, so the running root cannot
  be constructed at all, published or not. Changing what an id segment
  may contain is a published-document contract that reaches the viewer,
  and is not this change's.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `simulation`: "A relation's law is compiled to an expression over
  coordinate ids" states what the compiled program's coordinates ARE —
  the bank plus the ends of the compiled edges — so that a relation left
  to the ordinary enumeration leaves nothing of itself in the program.
- `export`: "A running root's document publishes the compiled program"
  states that the refusal of an unqualifiable id is over the
  coordinates the program computes, and its scenario "A plain port is an
  intermediate, not a bank entry" is corrected to the port the program
  actually computes — one between two bank coordinates — with the port
  no compiled edge determines named as the case that is published no
  longer.

## Impact

- `solid_node/simulation/program.py`: `compile_program` reduces `nodes`
  to the bank plus the kept edges' ends, between `_reaching_the_bank`
  and `_refuse_opaque`. `Program`, `published`, `published_names`,
  `_refuse_unqualified`, `_reaching_inputs` and `_ordered` are unchanged
  and read the reduced table.
- `tests/running_project/machine.py`: three fixtures — a running root
  whose `.repeat()` children own a driven port, one whose optional part
  is omitted, and one whose omitted part's coordinate a bank-reaching
  chain still passes through (the case that stays refused).
- `tests/test_running_document.py`: the publication tests for those,
  and `tests/base_documents/running_train.json` recaptured (`Train` is
  the only base document with a program, and it loses `wheel.turn`).
- `tests/running-corpus.json`: regenerated with
  `tools/generate_running_corpus.py`. Its two `Train` entries carry the
  document, `wheel.turn` included. No machine is added to `CORPUS`, so
  nothing else in the fixture moves.
- `docs/architecture.md` (the running-program synthesis), and
  `docs/changelog.rst`.
- No change to the document version, `program.identity`, the drivers
  table, the poses, the bindings table, the tick, or any public name.
- Outside this repository, and therefore outside this change: the
  browser viewer replays `tests/running-corpus.json`, whose `Train`
  document changes; and the shop's `shop-skills/solid-node-api/SKILL.md`
  says a `.repeat()` child under a running root "may own neither a joint
  nor a port a relation drives", of which the port half becomes false.
