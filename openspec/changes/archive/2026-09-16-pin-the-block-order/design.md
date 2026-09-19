## Context

`tests/running-corpus.json` is the contract between the framework's run
and any other runtime executing a published program (ADR-111). ADR-122
added the BLOCK — a selected cycle whose members are ordered once per
PIECE of a tick — and published a block's members as an ORDERED LISTING
that is explicitly not an execution order: "A consumer SHALL NOT execute
the members in the published order" (`select-the-source` design.md §9).
The corpus is what was supposed to make that sayable to a consumer that
disagrees.

It does not. `_Block._order` is the one function that decides the order
inside a piece, and monkeypatching it to return the members in the order
they are listed leaves the committed corpus almost entirely green
(`spikes/order.py`, `spikes/patched_corpus.py`, this worktree at
`0b0f02a`):

```text
Train            dt=0.05  PASSES under listing order
...
ShiftedCarry     dt=0.05  PASSES under listing order
RangedBlock      dt=0.05  DIVERGES (1)
Captured         dt=0.05  PASSES under listing order
```

and `RangedBlock`'s single disagreement is
`tick 1: 3 crossing(s) in the corpus, 2 under listing order` — no bank
value anywhere in 19 scenarios and 356 ticks differs by so much as an
ulp. `ShiftedCarry`, the scenario ADR-122 added FOR the block, also
passes with its two block members REVERSED (§3 says why that second
order is the weaker evidence of the two).

The constraint on the fix is that the run is correct: nothing under
`solid_node/` may change, and no other corpus entry may move. The only
thing wrong is the script.

## Goals / Non-Goals

**Goals:**

- A corpus that DISAGREES, on a bank value, with a consumer that runs a
  block's members in the order the document lists them.
- A generator that refuses to write a corpus without the feature that
  makes that possible, derived from the published document and the tick
  log the way every other `REQUIRED` entry is.
- A framework test that pins the discrimination itself, so the promise
  does not rest on the feature list being a good proxy for it.

**Non-Goals:**

- Changing the run, the document, the version ladder, or any other
  corpus entry.
- Making `RangedBlock` discriminate more than its one crossing count.
- Refreshing `solid-node-viewer`'s committed copy of the corpus or its
  own `REQUIRED` mirror (`proposal.md`, Non-goals).
- An ADR. ADR-122 already decided that the published order is a listing;
  this cycle makes the corpus able to say so.

## Decisions

### 1. The script: crank by `2.0` over `0.3 s`, everything else kept

`ShiftedCarry`'s one in-block dependency is the higher wheel's
`carry.travel >= 0.5` gate — `SET` in `tests/carriage_project/machine.py`
— on the lever the lower wheel pushes. The order matters exactly when
that gate crosses inside a tick, because only then does the lever's
value at the left end of a piece differ from its value after the lower
wheel has run.

The committed script cranks `2.0` over `0.2 s` at `dt = 0.05`: four
ticks of `0.5`, so `carry.travel` steps `0.5, 1.0` and reaches `SET`
EXACTLY at a tick boundary. Measured, the whole 20-tick run records
**no crossing at all**.

`0.3 s` gives six ticks of `1/3`: `carry.travel` steps
`1/3, 2/3, 1.0` and reaches `0.5` half way through tick 2. Measured
(`spikes/alternatives.py`, all at `dt = 0.05`, 20 steps, the shift at
tick 8 and the second crank at tick 14 unchanged):

| `duration` | crossings | in-block gate crossings inside a tick | disagreements under listing order | final `higher.turn` |
| --- | --- | --- | --- | --- |
| `0.2` (committed) | none | 0 | **0** | `3.5` / `3.5` |
| `0.4` | none | 0 | **0** | `3.25` / `3.25` |
| `0.15` | 4, the first two in tick **1** | 0 | 22 | `3.5000000000000004` / `3.3333333333333335` |
| **`0.3` (chosen)** | 2, both in tick **2** | **1** | **21** | `3.5` / `3.3333333333333335` |

`0.4` is rejected because it lands on the grid again — `0.25` a tick,
`0.5` at the end of tick 2 — which is the same defect one notch slower.
`0.15` diverges but puts its crossing in the FIRST tick, where the
feature derivation of §2 has no preceding bank to read and reports
nothing; a scenario whose divergence the guard cannot see is the defect
this cycle is fixing. `0.3` is the smallest change to the committed
script that crosses the gate strictly inside a tick that has a
predecessor.

What the chosen script buys, tick by tick: the producer runs `carry`
before `higher` on the piece after the crossing and gives
`higher.turn = 0.16666666666666669` at tick 2; the listing order runs
`higher` first, reads the lever at `1/3` — below `SET` — and gives
`0.0`. One sixth of a turn, and it never heals: `3.5` against
`3.3333333333333335` at tick 20, with the crossing itself moved from
tick 2 to tick 4. Twenty-one disagreements.

The document is untouched, so the scenario keeps everything it supplies
today — `'a switched source'` is structural, and the self-read features
it shares with `Clearing` and `StoppedClearing` come from banks that do
not change in kind. Regeneration is contained: `removed: []`,
`added: []`, `changed: [('ShiftedCarry', 0.05, 20)]`, order preserved,
356 ticks as before (`spikes/regenerate.py`).

Rejected alternatives: a smaller `dt` (it renumbers every tick of the
entry, so the shift and the second crank would have to be re-placed, and
every value in the entry moves for a reason unrelated to the finding);
and a NEW fixture machine whose gate operator is unique (§2) — a new
machine costs a document, a version 7 publication and 20 more ticks in
the corpus, to test a block the corpus already carries a block for.

### 2. Deriving `'an in-block gate crossing inside a tick'`

The generator's `REQUIRED` entries are derived from the published
document and the tick log, never declared beside the machine, so that
the corpus's width is a property of the tool. This one must be too.

A crossing in the fixture carries `relation`, `coordinate`, `primitive`,
`level` and `t`. `level` is the SURFACE VALUE, which for every
comparison is `0.0` (`program.py:182`), so a crossing does NOT identify
the jump it came from. `_selection` already copes with that for
`'a selection crossing inside a tick'` by reporting only the primitives
a member's selectors have and no OTHER jump of it has — conservative,
and enough there.

It is not enough here. Measured on the published `ShiftedCarry` document
(`spikes/gates_debug.py`), the block is `{higher.turn, carry.travel}`
and the higher wheel's four jumps are:

```text
edge 1 ['higher.turn'] _j2 >= | _b2                  (shift - 0.5)
edge 1 ['higher.turn'] _j3 <  | _b2                  (shift - 0.5)
edge 1 ['higher.turn'] _j4 >= | (carry.travel - 0.5)
edge 1 ['higher.turn'] _j5 >  | (higher.turn - 0.5)
```

`_j4` is the in-block gate and `_j2` is a SELECTOR, and both are `>=`.
So the symmetric rule — the primitives a non-selector jump has and no
selector of the same member has — is EMPTY for this member under every
script, and would never detect the feature. The ambiguity is structural
to the fixture, not to the script.

**The derivation therefore reads the tick's own bank, as the self-read
feature already does.** For a crossing `C` under block member `M` with
`0 < C.t < 1`, resolve each of `M`'s jumps' levels transitively through
the document's `bindings` (the generator's own `free_names`) and split
the jumps carrying `C.primitive` into

- **gates** — those naming a coordinate the block gives OTHER than `M`'s
  own driven end, ADR-121's self-read excluded because a self-read
  imposes no order; and
- **selectors** — those naming no coordinate the block gives at all.

`C` counts when some gate's in-block name MOVED across the tick (its
value differs between the previous tick's bank and this one's) and NO
selector carrying that primitive reads anything that moved, or anything
the bank does not carry. Then no selector of that member can account for
`C`, and a gate can. The first tick of a scenario has no predecessor and
is skipped.

Measured: the rule reports exactly one entry on the chosen script —
`tick 2: higher.turn >= t=0.49999999999999994` — and nothing on the
committed one; and NO machine in the corpus as committed supplies it
(`spikes/gate_survey.py`), so the generator refuses the committed corpus
until the script changes. That refusal is the red state task 2 records.

What the rule deliberately does not do:

- It judges "moved" from the tick's ENDPOINTS, so a coordinate that
  leaves a value and returns inside one tick reads as held. A crossing
  could then be credited to a gate when a selector produced it.
- Two gates of the same member with the same primitive on different
  in-block coordinates are not told apart.

Both make the guard admit a crossing it should have; neither invents one
where the member has no gate at all. The guard is a statement about the
corpus's WIDTH — the ordering test of §3 is what pins the behaviour, and
it does not depend on this derivation.

Rejected alternatives: evaluating each level expression over the two
banks to find which surface changed sign (it needs a full expression
evaluator in the generator and in every consumer's mirror of it, to
recover something the fixture could simply have published); publishing
the crossed jump's `name` on a crossing (a document change, which this
cycle is not, and against ADR-110's line that the document carries what
compile time DECIDED); and renaming the fixture's gate operator so the
primitives are unique (changing the fixture to suit the guard, and the
Curta's real associations share operators for the same reason this one
does).

### 3. Pinning the discrimination directly

The feature list is a proxy. What the requirement says is that a
consumer running the members in the published order DISAGREES, so the
test says that:

```text
tests/test_running_corpus.py::BlockOrderTest
  - replay the ShiftedCarry entry with _Block._order patched to
    tuple(range(len(self.members))) and assert some tick's bank differs
    from the corpus by more than tolerance * max(1, |a|, |b|);
  - assert the UNPATCHED replay of the same entry reproduces it, so the
    first assertion cannot pass by breaking the fixture.
```

The patch goes on `solid_node.simulation.program._Block._order` for the
duration of the test and is restored after — the same shape the
`select-the-source` spikes used on `_ordered`, and the only function
whose result the listing order changes. Patching at the `Sim` level
instead (constructing a machine whose members are declared in another
order) would test a different machine; patching the ORDER is what a
wrong consumer actually does.

RED FIRST, and it is already measured: on the committed script the
patched replay PASSES (`spikes/order.py`, section 1), so the test's
first assertion fails before the script changes and passes after. The
generator's new `REQUIRED` entry is red in the same way — `uncovered_features`
on the committed corpus returns the new feature (`spikes/gate_survey.py`).

The reversed order is NOT a second assertion, and it is not even a
second wrong answer. The block has TWO members, `higher.turn` and
`carry.travel` — `lower.turn` is an ordinary edge ordered ahead of the
block — so reversing them is `carry` before `higher`, which is the
order the producer itself chooses while `shift < 0.5`; and once
`shift` is `1.0` the lever has already reached `FULL` and stands still,
so the order stops mattering. That it reproduces the corpus is recorded
in `proposal.md` because a green run under an order chosen at random is
what the finding is about, not because reversing two members is a
consumer's likely mistake. A document publishes ONE listing, and it is
that listing a consumer executes.

### 4. What does not change

`solid_node/` is untouched — no source file is in the Impact list.
`ShiftedCarry` still publishes version 7, its document is byte-identical
(the script is not part of the document), and every other entry of the
corpus is byte-identical (§1). `tests/running-corpus.json` is regenerated
by the tool, never hand-edited, exactly as ADR-111 requires.

`openspec/specs/simulation/spec.md` is not touched: no requirement about
the run changes. The export requirement gains the feature in its refusal
list and a statement that the corpus SHALL discriminate the order, which
is a promise about the corpus and belongs there.

### 5. Cost

One entry of one scenario changes; the corpus keeps its 356 ticks and
its 19 scenarios. The new derivation runs once per crossing of a block
member per scenario in `uncovered_features`, which the suite calls a
handful of times. The new ordering test replays one 20-tick scenario
twice; `ShiftedCarry` benches at 1.3 ms a quiet tick and 2.7 ms on the
tick that crosses a detent (ADR-122's own table), so it is tens of
milliseconds.

## Risks / Trade-offs

- **The guard can be satisfied by a crossing it mis-attributes** (§2) →
  the ordering test of §3 does not use the guard at all, and it is the
  one that fails if the corpus stops discriminating.
- **The viewer's committed copy of the corpus goes stale the moment this
  lands, and its own `uncoveredFeatures` will not know the new feature**
  → it is a separate repository with its own cycle (`proposal.md`,
  Non-goals); until it updates, its old copy still replays there, so the
  staleness is visible as a diff rather than as a failure. Recorded in
  the cycle's report for the viewer's cycle to pick up.
- **A future change to `_Block._order`'s signature breaks the test's
  patch** → it is a framework-internal function patched by a framework
  test in the same repository, and the test fails loudly rather than
  silently passing.
- **`0.3 s` is chosen for one fixture's arithmetic** — six ticks of
  `1/3` against a `0.5` detent — **and a later change to `SET` or to the
  lever's law would put the gate back on the grid** → the ordering test
  fails if that happens, which is the point of having it.

## Open Questions

None. The script, the derivation and the test are all measured on this
worktree before the proposal was written.
