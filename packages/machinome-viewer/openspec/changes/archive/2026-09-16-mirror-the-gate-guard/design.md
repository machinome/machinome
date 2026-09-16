## Context

`solid_node_viewer/widget/src/running-corpus.json` is solid-node's
`tests/running-corpus.json`, copied byte for byte, and
`src/run/running-corpus.test.ts` is the two things that copy is for: a
REPLAY of every scenario through the shipped engine, and a WIDTH GUARD
that mirrors the producer's generator so a narrowed corpus copied in is
refused here without anyone running the generator (ADR-047, ADR-111).

The producer's `pin-the-block-order` (`d3c2242`) changed one script and
one `REQUIRED` entry, for a finding this repository reported: the
`ShiftedCarry` scenario written FOR the block did not discriminate the
block's order, so an engine that executed the published listing passed
it. Both halves of the copy are therefore stale — the fixture, and the
guard that says how wide the fixture must be.

The constraint is the mirror image of the producer's: the ENGINE is
correct. `execute-the-selection` (ADR-058) already orders a block per
piece, and the producer's new corpus replays green through it on this
base, all 19 scenarios, with the whole widget suite green beside it.
Nothing of `src/run/`'s engine source may change; what is missing here is
the fixture and the guard, plus the one test that proves the engine's
ordering is what makes the replay green.

## Goals / Non-Goals

**Goals:**

- The committed corpus is the producer's at `d3c2242`, byte for byte.
- The width guard knows the producer's new required feature and derives
  it the way the generator derives it — from the corpus's own documents
  and tick logs, never from the engine.
- One test pins, against THIS engine, what the producer's `BlockOrderTest`
  pins against its own: a consumer running a block's members in the
  published listing order disagrees with the corpus.

**Non-Goals:**

- Changing the engine, the document version ladder, the declared API
  version, or the bundle.
- Adding an ordering seam to the engine for the test's benefit (D5).
- Making `RangedBlock` discriminate more than its one crossing count.
- An ADR. ADR-058 already decided that the published order is a listing;
  this cycle makes the corpus committed here able to say so.

## Decisions

### D1. The corpus is REPLACED, byte for byte, and never edited

`cp` the framework's `tests/running-corpus.json` at `d3c2242` over
`src/running-corpus.json`. The census assertion — 19 scenarios, 16 unique
machines, 356 ticks — does NOT move, because the producer's regeneration
changed exactly one entry and added none:

```text
generated_by / corpus / tolerance : equal
scenario keys (name, dt, steps)   : equal, same order
added [] · removed [] · changed [('ShiftedCarry', 0.05, 20)]
ShiftedCarry: script duration 0.2 -> 0.3 (h0 and h2); 10 of 20 ticks moved;
              document BYTE-IDENTICAL (key order included), version 7
```

Six other widget test files import the corpus
(`jumps.test.ts`, `program.test.ts`, `run.test.ts`, `cost.test.ts`,
`runtime.test.ts`, `republish.test.ts`), and every one of them reads a
scenario's `document` and writes its own script; only
`running-corpus.test.ts` reads `entry.script` and `entry.ticks`. Since
the changed entry's document is byte-identical, none of them can move —
and the measurement confirms it: the WHOLE suite (36 files, 922 tests) is
green with the new file in place and the engine untouched.

That is also why this cycle's RED is not the census and not the replay.
The corpus swap alone is green. The red is the guard (D2–D4) and the new
ordering test (D5), and the tasks record them in that order.

### D2. `REQUIRED` gains the producer's entry, in the producer's position

Append `'an in-block gate crossing inside a tick'` after
`'a tick carrying both a selection crossing and a stop'`, which is where
`tools/generate_running_corpus.py:104` puts it. The spelling is the
producer's, character for character: the two lists are compared by eye
across two repositories, and a synonym here would read as a different
feature.

Red first, over the NEW corpus and with no detection written: the guard
then reports exactly `['an in-block gate crossing inside a tick']`
(measured). That is the failure the rest of the cycle turns green.

### D3. The detection mirrors `_in_block_names` and the previous-bank rule

Two pieces, both from the generator.

**`inBlockNames(edge, primitive, bindings, gives)`** — the mirror of
`_in_block_names` (`tools/generate_running_corpus.py:542-574`). For each
non-null plan of the edge, and each jump of that plan whose `primitive`
is the crossing's, resolve the jump's `level` transitively: a free name
that is another jump's `name` in the same plan is followed into THAT
jump's level; every other name is closed over the document's `bindings`
table through the guard's own `freeNamesOf`, which
`running-corpus.test.ts` already has. Then, with `own = edge.gives`:

- `reaches = names ∩ gives − own` non-empty → the jump is a **GATE**, and
  `reaches` is what is returned for it;
- else `names ∩ gives` empty → the jump is a **SELECTOR**, and the WHOLE
  `names` set is what is returned for it;
- otherwise (a jump naming only the member's own driven end) it is
  neither and is returned in neither list.

The asymmetry between the two returned sets — the intersection for a
gate, the full name set for a selector — is the producer's, and it is
load-bearing: the gate test asks whether an IN-BLOCK name moved, and the
selector test asks whether ANYTHING the selector reads moved.

**The tick rule** — the new block of `uncovered_features`
(`tools/generate_running_corpus.py:445-465`). With `previous` the
preceding tick's bank (so the first tick of a scenario is SKIPPED, having
no predecessor) and `changed` the ids whose value differs between the two
banks, a crossing counts when all of:

1. `0 < crossing.t < 1` — strictly inside the tick;
2. `memberOf(edges, crossing.coordinate)` is a member of a block, by the
   guard's existing `selectionOf` map;
3. some GATE's returned set meets `changed`;
4. no SELECTOR's name set meets `changed`, and no SELECTOR's name set
   reaches outside the tick's bank.

Then no selector of that member can account for the crossing and a gate
can. The producer's design §2 records what the rule deliberately refuses
to do — it judges "moved" from the tick's endpoints, and it does not tell
two gates of the same member on different in-block coordinates apart —
and both admissions make the guard admit a crossing it should have rather
than invent one where the member has no gate. That reasoning is the
producer's and is not re-litigated here; the guard is a statement about
the corpus's WIDTH, and D5 is what pins the behaviour.

**It is a SECOND deliberate copy, beside `loadProgram`'s.** The loader
already derives blocks, selectors and folds from the same documents, and
the guard must not call it — the file says why, and this cycle keeps the
reason intact: the guard has to be red on a narrowed corpus even when the
engine is broken. Borrowing the engine's derivation would make a broken
engine agree with itself.

One mirrored quirk, kept deliberately: `memberOf` indexes the published
edges INCLUDING `check` edges while `selectionOf` builds its member map
over the edges with checks filtered out, so the two indexings agree only
where no check edge precedes a law edge. That is exactly what the
producer does (`_member_of` over `program['edges']`, `_selection` over
the filtered list, and the new block indexing `program['edges'][index]`),
and it is latent rather than live: NO document in the corpus publishes a
`check` edge at all (measured over all 19 scenarios), so the two indexings
agree everywhere the guard actually runs. A mirror that silently fixed it
would stop being a mirror. Recorded here so the divergence is a
decision rather than an oversight; if the producer ever fixes it, this
guard follows in that cycle.

### D4. The narrowed-corpus test names the new feature

`'is refused when the corpus is narrowed'` already trims the corpus to
`Train` and asserts several features by name. `Train` states no block at
all, so it supplies no gate crossing either; add the one assertion.
Measured on the trimmed producer corpus: the new feature is in the
uncovered list. Nothing else in that test moves.

### D5. The order-discrimination test, WITHOUT adding a seam

The producer's `BlockOrderTest` monkeypatches `_Block._order` to return
`tuple(range(len(self.members)))` and replays `ShiftedCarry`. The
question this cycle had to answer is whether this engine can be driven
the same way without an engine change.

**It can, and no seam is added.** `blockOrder` (`run/jumps.ts:1142`) is
module-local and NOT exported — but it is not the seam. It reads the
block only through `block.activeReads(index, forced[index])`, and

- `ProgramBlock` (`run/program.ts:221-232`) is a plain interface whose
  `activeReads` is an ordinary method member, which the suite ALREADY
  substitutes: `jumps.test.ts:1079-1091`'s `watched()` builds a
  stand-in block with its own `activeReads` and passes it to
  `blockIncrements`;
- `ProgramEdge.block` (`run/program.ts:192`) is a mutable field of the
  loaded program, so a test can replace one block edge's block before the
  run starts;
- `Engine`'s constructor (`run/engine.ts:37`) takes a `LoadedProgram`, so
  the test loads the document, substitutes, and constructs the engine —
  `Engine.load` is not the only way in.
- `activeReads` has exactly one non-test caller in the whole widget
  (`jumps.ts:1145`), so substituting it changes the ORDER and nothing
  else.

The substitute answers the EMPTY SET. Every member is then ready in the
first Kahn round and `blockOrder` pushes them in `remaining`'s order,
which is `0..n−1` over `block.members` — and `block.members` is the
published listing order, because `componentsOf` sorts each component's
indices ascending (`stronglyConnected`, `program.ts:593-601`) and `_blocked` never re-sorts
(`program.ts:1380-1399`). Measured on `ShiftedCarry` at `d3c2242`: the
members are `['higher.turn', 'carry.travel']` against published edge
gives `[['lower.turn'], ['higher.turn'], ['carry.travel']]`, so the
forced order IS the listing order, which is what the producer patches to.

The test then mirrors `BlockOrderTest` shape for shape:

- replay `ShiftedCarry`'s own corpus entry — its script, its `dt`, its 20
  steps — UNSUBSTITUTED, and assert zero disagreements against every
  committed tick's bank under the corpus's own tolerance rule
  `|a−b| ≤ tol·max(1,|a|,|b|)`; then
- replay it SUBSTITUTED and assert at least one disagreement.

The first assertion is what stops the second from passing by breaking the
fixture. Measured on this base: **21 disagreements substituted, 0
unsubstituted**, the first being `tick 2 higher.turn: corpus
0.16666666666666669, run 0` — the same 21 and the same floats the
producer measured on its side. Against the STALE copy the substituted
replay gives 0, which is the finding, reproduced in this engine.

Rejected alternatives:

- **Exporting `blockOrder`, or adding an option to `Engine.load`.** A
  production interface invented for a fixture, and it would have to be
  specified as behaviour the viewer offers. The substitution above needs
  nothing.
- **Reversing the two members instead.** The producer's design §3 records
  why that is the weaker evidence: a document publishes ONE listing, and
  reversing two members is an order the producer itself chooses on half
  the run. `execute-the-selection` already measured the exchange on the
  stale fixture and it is in this cycle's proposal as history, not as an
  assertion.
- **Asserting the feature list instead.** The guard is a proxy; D3's own
  rule admits crossings it should have. The direct replay does not depend
  on the derivation at all, which is exactly why the producer wrote both.

### D6. What does NOT change, checked rather than assumed

- **The API version and the document ladder.** Nothing about what the
  viewer reads or executes changes, so `solidNodeViewerApi` stays 16 and
  `solidNodeDocumentVersions` stays `[1..7]`; `version.test.ts` and
  `viewer.ts`'s `RENDERED_VERSIONS` are untouched. A host that already
  requires 16 gets the same capability it got before.
- **No ADR.** A fixture refresh and a coverage guard decide nothing about
  the architecture. `docs/adrs/` and its index are untouched.
- **The Python suite.** The corpus is imported by TypeScript test files
  only; no module under `src/` imports it, so it is not in
  `dist/solid-widget.js`, and no Python module or packaged data file
  references it (`grep -rn running-corpus` outside the widget's tests is
  empty). `bundle.py`, `server.py` and `capture.py` cannot observe this
  change. The applier need not run pytest or `scripts/check-dist`; the
  bundle is rebuilt only to show the build still passes.
- **`CHANGELOG.md`** gains one bullet under `0.2.0 — unreleased`.
  `README.md`'s version claims do not move.

### D7. Cost

The guard's new derivation runs once per crossing of a block member per
scenario, over a corpus with 356 ticks; the guard is called four times by
the suite. The ordering test replays one 20-tick scenario twice
(`ShiftedCarry` benches at single-digit milliseconds a tick here). The
measured whole-suite time with the new corpus in place is 51.02 s against
51.42 s on the base — inside this host's noise.

## Risks / Trade-offs

- **The guard can be satisfied by a crossing it mis-attributes** (D3, the
  producer's §2) → the test of D5 does not use the guard at all, and it
  is the one that fails if the corpus stops discriminating.
- **The substitution of D5 is not literally the producer's patch**: it
  forces the order by emptying the dependency set rather than by
  returning an index tuple → the test asserts the forced order IS the
  published listing order before it asserts the divergence, so the
  equivalence is checked rather than argued, and `activeReads`'s single
  non-test caller is named in the test's comment.
- **A future engine change could stop honouring `activeReads`** (a
  cached order, say) and the substituted replay would silently agree
  again → the unsubstituted half of the assertion would still pass, so
  the test would go green for the wrong reason. Mitigated by asserting
  the forced order explicitly; called out here so a later cycle touching
  `blockOrder` knows this test depends on it.
- **The two `REQUIRED` lists live in two repositories and can drift** →
  unchanged by this cycle; it is the standing cost of a mirrored guard,
  and the producer's cycle records the same risk from its side.

## Open Questions

None. The corpus diff, the replay, the guard in all four configurations
and the order discrimination were all measured on this worktree, on the
base, before this design was written.
