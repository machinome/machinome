## Context

`compile_program` (`solid_node/simulation/program.py:1251`) builds the
program in four steps:

1. it makes a `_Node` for every input and every banked joint coordinate,
   and remembers their keys as `bank_keys`;
2. it walks the units of the tree and turns every relation, wiring and
   derived coordinate into a CANDIDATE `Edge` — and each of
   `_relation_edge`, `_wiring_edge` and `_formula_edge` calls `_register`
   (`:1760`) for every end, which makes a `_Node` for any end that is not
   already in the table;
3. `_reaching_the_bank` (`:2131`) keeps only the candidates that
   determine a bank coordinate, determine something such an edge reads,
   or check what those produce — the rule the simulation spec states as
   "left to the ordinary enumeration";
4. it hands `nodes` and the KEPT edges to `Program`.

Step 2 registers ends that step 3 then drops, and nothing removes them.
`Program.nodes` is therefore not "the program's coordinates" but "the
coordinates of every relation in the tree", and three readers of it are
wrong in consequence:

- `_refuse_unqualified` (`:1108`) walks every node and raises for any
  whose id is the `<ClassName>.<name>` fallback `_qualified` (`:1773`)
  takes when `driver_id(instance_path(...))` raises `DriverIdError`;
- the published `intermediates` (`:1075`) lists every node of kind
  `intermediate`, computed or not;
- `sources` (`:804`, `:1083`) publishes an entry for each of them, always
  empty, since `_reaching_inputs` walks the kept edges only.

`_qualified` falls back for two DIFFERENT reasons, and the refusal's text
names only the first:

- `instance_path` raises when the node is not linked under the root —
  which is what `omit()` produces, since an omitted child is "not linked,
  built, exported, fused or serialized";
- `driver_id` raises when a path SEGMENT is not a legal identifier —
  which is what `.repeat()` produces, because `RepeatDeclaration.realize`
  (`solid_node/node/declarative.py:600`) returns a LIST of copies, the
  parent holds that list under the declaration's attribute, and
  `_child_name_index` (`solid_node/node/base.py:1159`) names a
  list-held child `<attribute>-<index>`. `evidence.md` measures both:
  `instance_path(copy, root)` is `('springs-0',)` and succeeds;
  `driver_id(('springs-0',), 'height')` raises.

So the lock's springs ARE linked, under `springs-0`…`springs-4`, and the
message they provoke ("the node it belongs to is not linked under the
root ... Hold the node on its own attribute of its parent") is wrong
about them twice over. This change removes the refusal for that shape
rather than correcting the sentence; see decision 5 and the open
questions.

## Goals / Non-Goals

**Goals:**

- A running root whose `.repeat()` children own a port a relation drives
  publishes its document.
- A running root that omits an optional part whose joint a driver drives
  publishes its document.
- What the document says about the program is what the program computes:
  `intermediates` and `sources` name only that.
- Nothing about the run, the identity, the version, the poses or the
  bindings table moves.

**Non-Goals:**

- Changing the qualified-id grammar (`_LEGAL_SEGMENT`,
  `solid_node/node/qualified.py:157`) so a repeat copy can carry a
  qualified id. That is a published-document contract the viewer reads,
  the module docstring records bijective sanitization as a deliberate,
  compatible EXTENSION for when a project needs it, and it is what would
  be needed for the other half of the repeat problem (decision 6).
- Changing what `omit()` does to a relation. The wart's candidate
  correction — `compile_program` drops a relation whose end resolves to
  an omitted node, the way `declare-controls-on-parts` drops a control
  whose part this render omitted — is a decision about whether structure
  may vary with parameters, and is unnecessary for the shape measured:
  the relation onto an omitted part's own joint reaches no bank
  coordinate and is already dropped by `_reaching_the_bank`.
- Correcting the refusal's wording for the grammar case (decision 5).
- The lock's other three findings (the runner's operation checkpoint,
  the false `DoublyBound`, the sampled search's cost), each its own
  cycle.

## Decisions

**1. Reduce `nodes` to the bank plus the kept edges' ends, in
`compile_program`, immediately after `_reaching_the_bank`.**

One line of intent: the program's coordinate table is the bank plus
every key the kept edges read or give. Everything downstream is derived
from `nodes` and needs no change — `Program.keys` and `bank_keys` (bank
nodes are never dropped), `sources` via `_reaching_inputs`,
`_constraint_table`'s `by_name`, `published_names`, `intermediates`,
`_refuse_unqualified`, `deltas_of`'s zero table, and `__repr__`.

Placed BEFORE `_refuse_opaque` and `_ordered` so there is one table from
that point on rather than two. Neither is disturbed: `_refuse_opaque`
(`:2160`) reads `nodes[key]` only for the needs of KEPT edges, all of
which survive; `_ordered` (`:2180`) seeds `resolved` with every node no
kept edge determines, and dropping keys no kept edge NEEDS cannot change
which edges become ready.

Alternatives considered:

- *Prune at publication, inside `published()`.* Rejected: `Program.nodes`,
  `sources` and `__repr__` would go on claiming coordinates the program
  does not have, and "what the program computes" would have two
  implementations to keep in step — the thing the campaign moved
  `values_of`/`deltas_of` onto `Program` to avoid.
- *Do not register an end until its edge is kept.* Rejected: an `Edge` is
  built FROM `_Node` keys, and `_reaching_the_bank` runs over already
  built candidates. Registering lazily means building edges without
  keys, which is a larger change to `_relation_edge`, `_wiring_edge` and
  `_formula_edge` for the same result.
- *Keep the dropped edges and compile them.* Rejected: it contradicts the
  ratified rule that such a relation is left to the ordinary
  enumeration, it would move `program.identity` for every affected
  machine, and it would pay a graph evaluation per dropped relation per
  tick for values nothing in the run reads.

**2. The identity does not move, and this is the reason the change is
safe for existing snapshots and for the conformance corpus.**

`described()` (`:862`) lists the root class, the inputs, the
coordinates, the spans and the edges. It never reads `nodes` except
through `edge.needs`/`edge.gives`, which are kept edges' keys. Measured
in `evidence.md`: for all three probe machines, `identity` before and
after the reduction is the same string. A snapshot taken against a
program compiled by the old code restores into one compiled by the new.

**3. The published document loses exactly the names nothing computes,
and nothing reads them.**

Measured over every running fixture in `tests/running_project/machine.py`
(`evidence.md`, "Blast radius"): three publish such a name today —
`Train` (`wheel.turn`, the wiring into the wheel's plain port),
`Gauged` (`gauge.angle`) and `PortDrivenJoint` (`register`) — and in
none of the three documents does any operation or `params` expression
read it, before or after the bindings table is resolved, and none of the
three is a `bindings` entry. This is not luck: a tree expression reads a
plain port by SUBSTITUTING what the relation gives it, which resolves to
bank ids (the export spec's own scenario "A plain port follows the bank",
and `test_a_plain_port_follows_the_bank`), so the port's own id never
enters the document. The invariant "Every name the document reads is
declared" therefore holds over the smaller declared set, and its test
already covers `Gauged`.

The only other reader of `published_names()` is `bind_document`
(`solid_node/core/serializer.py:562`), which uses it solely so a MINTED
name (`_b0`, `_j0`, …) cannot collide with a published id. Shrinking the
set can only shrink the collision surface, and a removed name is a
qualified id or a `<ClassName>.<name>` fallback, neither of which can
match `<prefix><digits>` unless a driver or port is literally named `_b0`
— and drivers and bank coordinates are never removed.

**4. The refusal stays, over the reduced table, and a kept edge with an
unqualified end still refuses.**

Measured (`evidence.md`, `Reader(fitted=False)`): with
`crank.drives(spare.turn)` and `spare.turn.drives(first.turn)` both kept
— because the chain reaches the bank — the omitted `spare`'s coordinate
is an intermediate the program genuinely computes, the reduction removes
nothing, and publication refuses exactly as before. That is the right
answer for this cycle: the document would have to publish an expression
naming that value, and a class-name fallback is not unique across two
instances of the class, which is the whole reason the refusal exists.
Whether such a machine should be buildable at all is the `omit()`
question this change leaves open (non-goals), and answering it by
publishing an ambiguous name would be wrong in every case.

The third shape — the omitted coordinate as a SOURCE nothing computes —
is unreachable through `omit()`: the coupling layer refuses
`spare.turn.drives(second.turn)` with `UnreachedCoordinate` whether the
part is fitted or not, because nothing binds either end. So
`_refuse_opaque` is not a path `omit()` can reach, and it needs no
change.

**5. The refusal's wording is left alone.**

After this change, a repeat copy's name can still reach
`_refuse_unqualified` in principle — through a kept edge, which needs a
wiring or relation whose driven end is one copy and which reaches the
bank. No such shape is measured here and none is known in a project; a
broadcast is refused as a relation SOURCE
(`RepeatDeclaration.__getattr__`), which is what would be needed to
carry a copy's port back to the bank in a class body. Correcting the
message to distinguish "not linked" from "not a legal id segment" is a
user-visible refusal change with its own spec text, and belongs with
whatever cycle takes the grammar on.

**6. The joint half of the repeat problem is measured and left where it
is.**

`evidence.md` records it: a running root whose `.repeat()` child owns a
`Prismatic` fails in `qualified_coordinates` (`program.py:227` →
`qualified.py:169`) with `DriverIdError`, while the BANK is being
enumerated — before any program exists, and inside `Sim.__init__` and
`release_tree` alike, so the machine cannot be simulated at all, let
alone published. It is the id grammar, not publication, and this change
cannot and does not touch it.

## Risks / Trade-offs

- **A consumer that enumerates `program.intermediates` for display loses
  an entry it used to see.** → The entry has no edge computing it and an
  empty `sources` list, so there is nothing a consumer could do with it
  but print a name. The document version is unchanged because version 5
  already DEFINES `intermediates` as what a compiled edge determines;
  this makes the producer obey its own definition.
- **The committed conformance corpus changes.** → Its two `Train`
  entries carry `wheel.turn` (measured in `evidence.md`), so
  `tests/running-corpus.json` must be regenerated with
  `tools/generate_running_corpus.py` and the diff inspected to be those
  two entries and nothing else. `CORPUS` gains no machine, so no tick
  and no script moves. The browser viewer replays this fixture; the
  removed name is one no expression in it reads.
- **`tests/base_documents/running_train.json` stops being
  byte-identical.** → It is recaptured as part of the change, and the
  recapture is exactly two lines: the `intermediates` list and the
  `wheel.turn` entry of `sources`. The other six base documents carry no
  program and are untouched, which is the point of keeping the capture.
- **A machine could exist whose tree expression DOES read a dropped
  intermediate's id.** → None does among the fixtures, and the
  substitution argument in decision 3 says none can arise from a
  relation; the invariant test "Every name the document reads is
  declared" is the guard, and the new fixtures are added to its list.

## Open Questions

- Should a relation whose end resolves to an OMITTED node be dropped at
  relation resolution, so that the `Reader` shape of decision 4 builds
  instead of refusing? The wart records it as a candidate correction and
  this change deliberately does not answer it.
- Should `_LEGAL_SEGMENT` gain the bijective sanitization its own
  docstring records, so a `.repeat()` child can own a joint under a
  running root? That is the only fix for decision 6, and it changes a
  document contract the viewer reads.
- Should `_qualified`'s refusal say WHICH of the two reasons applied?
  Left for whichever cycle takes the grammar on (decision 5).
