## Context

A clocked machine's identity is computed once, in `Clocked.__init__`
(`machinome/simulation/clocked.py`): a SHA-256 over `Clocked.described()`.
That listing covers the root class, every driver and state with its `dtype`
and `scale`, the clock where an elapsed base declares one, every committing
relation's ends, primitive, level and laws, and every compiled bound. It is
taken before `state=` is applied, so it describes the machine and not the
bank.

Every producer gets the clocked machine from
`serializer.compiled_clocked(node)`. That function calls
`clocked.clocked_of(root)`, which constructs `Sim(root)` and returns its
`sim._clocked`. `Clocked.published()` then writes
`'identity': self.identity` into the document's `clocked` object. The
export manifest's `clocked.identity` is therefore the `_clocked.identity` of
a `Sim` over the same model. There is no second implementation that could
disagree.

`Sim` already has two private refusal helpers, and they share one shape:

- `_not_clocked(what)` refuses a cadence member (`tick`, `at`, `every`,
  `run`, …) over a clocked root. It raises `TypeError("{what} belongs to a
  simulation with a CLOCK, and {Model} is CLOCKED: …")`.
- `_running(what)` refuses a running member (`rate`, `commands`, `program`,
  `crossings`, and the session members on an untimed root). It raises
  `TypeError("{what} belongs to a RUNNING simulation, and {Model} declares
  no time base or a looping one. …")`.

No `Sim` member is clocked-only today. `commits`, `stops`, `snapshot`,
`restore`, `reset` and `initial` are shared by the clocked and running
roots, and on an untimed root they fall through to `_running`.

The finding and its evidence are in `proposal.md`.

## Goals / Non-Goals

**Goals:**

- A consumer holding a clocked `Sim` can read the machine's identity
  through the public API. The value is the same string the export publishes
  as `clocked.identity` for the same model.
- A consumer holding a `Sim` that is not clocked is told by name that the
  member does not apply. It does not receive a value it could compare by
  mistake.

**Non-Goals:**

- The clocked snapshot's shape. `ClockedSnapshot` keeps `model` and
  `values`, and `restore` keeps comparing `model`. That the viewer's
  snapshot carries the identity and the framework's does not is recorded as
  a finding of this change, not changed by it (the orchestrator's cut).
- The viewer, the document, its version, and every producer's bytes.
- Videomaker's use of the member, and the studio's api skill.
- An identity for untimed or running roots under this name.

## Decisions

### 1. `Sim.identity` returns the clocked machine's own attribute

The property returns `self._clocked.identity`, the same attribute
`Clocked.published()` writes into the document. The equality with the
export's manifest therefore holds by construction.

Rejected:

- *Recompute through `compiled_clocked(self.node)`.* That constructs a
  second `Sim`, pays its pose and walks the tree a caller is holding, to
  produce a value this simulation already has.
- *A module-level function `clocked_identity(node)`.* That is a new public
  name, and the consumer in the evidence already holds the `Sim` it records
  through.

### 2. A read-only property

`identity` is a property with no setter, like `running` and `clocked`. An
identity describes the compiled machine and is never assigned.

### 3. Refused by name off a clocked root, in `_running`'s shape

A new private helper, `_clocked_only(what)`, sits beside `_not_clocked`
and `_running`. It returns the clocked machine, or raises:

> `TypeError: identity belongs to a CLOCKED simulation, and {Model} is not
> clocked: nothing in its tree declares a State, so it compiles no clocked
> machine and its document carries no clocked.identity.`

Under a running root the message adds one sentence: *"Under
Time.running() the compiled program carries its own identity:
sim.program.identity."* That is the public member that already holds the
string a running document publishes as `program.identity`.

This is the shape the two existing helpers use: a `TypeError` that names
the member, names the model's class, and says what the root would have to
declare for the member to apply. It is mirrored, not invented. The test
asserts the member's name and the model's name in the message.

Rejected:

- *Return `None` off a clocked root.* A consumer comparing two takes would
  find `None == None` and accept a take recorded over a different machine.
  That is the silent pass this change exists to remove.
- *Return `program.identity` under a running root.* No project asks for it,
  since the running value is already public through `sim.program`. It would
  also make one name mean two digests of two different document fields
  (`program.identity` and `clocked.identity`), which a consumer would then
  have to tell apart by the root's kind.
- *`AttributeError`.* `hasattr(sim, 'identity')` would then answer
  `False`, unlike every other member that does not apply to a root. Those
  raise `TypeError` by name, and a refusal that mimics a missing attribute
  says less than one that names the root.

### 4. The identity does not depend on the bank

`Clocked.__init__` computes the digest before it applies `state=`, and
neither a request nor `restore` recomputes it. The spec states this, and a
test reads the identity of a `Sim` opened with `state=`, moved, and
restored. This matters to the consumer in the evidence. A take begins from
an `initial` bank that is not the declared rest, and its identity must
still equal the export's, which was taken at rest.

### 5. No ADR

What the identity is, and that a bank is refused against another machine by
it, was decided by ADR-128 (and its document field by the export spec). This
change puts an existing value on the public API with the existing refusal
shape. It makes no architectural decision, so ADR-157, reserved for this
cycle, is not used. `docs/architecture.md` gains one clause in the clocked
mode's synthesis, because that paragraph lists what a clocked `Sim`
exposes.

### 6. The changelog entry

The entry goes under the existing `Unreleased` section of the manual's
changelog, `docs/project/changelog.rst`, where `persistent-verdict-memo`
put its own. `HISTORY.rst` is not touched.

*Corrected during implementation.* The planning commit put the entry in
both records, with a new `Unreleased` section in `HISTORY.rst`, because the
cycle brief named `HISTORY.rst`. The orchestrator then corrected the brief:
the entry belongs in `docs/project/changelog.rst` alone, as in the
precedent and in the sibling cycle. The `HISTORY.rst` section, and the
correction of the two pins it had turned red, were removed before the
implementation commit.

## Risks / Trade-offs

- [A consumer compares the identity across framework versions] → The
  digest covers `described()`, and a framework change to that listing
  changes every identity, as it already does for the document. That is the
  intended meaning: a take and an export made by different compilers are
  not known to describe one machine.
