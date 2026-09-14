## Why

solid-node's ADR-113 made a joint's range bound able to READ OTHER
COORDINATES: `range=(0, Bound(lambda turn, l1, …: 90 * clear(l1) * …,
reads=(p1.lift, …)))`. Under a running root such a bound is a
CONSTRAINT — evaluated along the tick's path over the coordinates it
reads, stopping every input that carries it outward, the inputs moving
what it reads included. The framework implemented it, regenerated the
conformance corpus with a fourteenth machine that exercises it, and
recorded, in its own design §8, that the viewer's worker refuses such a
document by name until this cycle lands.

It does. The pin tumbler lock (`projects/Locks/Pin_tumbler_lock`) is the
originating project, and its published version 5 document is refused on
load today:

```text
viewer.json declares document version 5 and the bound declared on
"plug.key.insert" names "plug.turn", which it may not read. It may read:
plug.key.insert. … The document is malformed: refusing it rather than
running a machine this viewer cannot execute.
```

That refusal is correct — a consumer that cannot execute what it was
given must say so (ADR-034) — and it is the last thing between the lock
and a browser. A lock whose plug turns only when five pins stand at the
shear line, and which captures the key once turned, is the mechanism;
without this cycle the browser shows a machine that cannot lock.

## What Changes

- The worker READS a span whose expression names other coordinates:
  at load it derives, per such bound, the read ids (the expression's
  free names through the document's bindings table, minus the bound
  coordinate's own id), the SUB-PROGRAM (the published edges that
  determine the bounded coordinate and every read, in program order) and
  the CANDIDATES (the union of `program.sources` over them) — all three
  projections of what the document already publishes, as the framework
  derives rather than publishes them (ADR-110, framework design §7).
- The worker EXECUTES such a bound as a constraint, reproducing
  ADR-113's semantics function for function: the own coordinate frozen
  at the tick's committed value, the reads along the path; examined only
  when something it depends on moves; a NUMBER when no read moves, which
  dispatches into the existing self-only stop path unchanged; sampled at
  `program.limits.subdivisions` fractions inside the stretch when a read
  moves, bracketed and bisected to `crossing_tolerance`, `t*` the inside
  end; no snap; the group every candidate whose admission alone raises
  the level; and an assertion at commit that refuses the tick when the
  invariant is broken.
- A read that is NOT a bank id — a published intermediate, an unknown
  name — is refused BY NAME at load, beside the refusals already listed,
  so a document this viewer cannot execute is never rendered.
- The committed conformance corpus is replaced by the framework's
  regenerated one (14 scenarios, 276 ticks, the `Captured` machine) and
  replayed green; the widget's width guard gains the producer's two new
  required features, so a narrower corpus copied in is loud here.
- The pin tumbler lock's published document is committed as a browser
  fixture and mounted in a real page: the plug is blocked until the key
  is seated, turns when it is, and the key is captured while the plug
  stands turned.
- **Not** a document version change: `documentVersions` stays
  `[1, 2, 3, 4, 5]`, the shape of a span is unchanged, and no public JS
  surface moves, so the declared widget API version stays at 12.

## Capabilities

### New Capabilities

None. This cycle widens a capability the viewer already has.

### Modified Capabilities

- `viewer-package`: ADDED — the worker derives and executes a bound that
  reads other coordinates. MODIFIED — "The step reproduces the
  producer's own integration" (a declared bound is no longer always a
  number evaluated once per step); "A program the viewer cannot execute
  is refused by name" (what a bound may read, and the refusal of a read
  that is not a bank id); "The two runtimes agree on a conformance
  corpus" (the two features the producer's generator now requires).

## Impact

- `solid_node_viewer/widget/src/run/program.ts` — the span free-name
  check, the derived constraint table, the sub-program and candidates.
- `solid_node_viewer/widget/src/run/run.ts` — `boundsNow`,
  `reachedBounds`, `eventOf`, the commit path, and the new constraint
  level, search, group, evaluated bound and invariant assertion.
- `solid_node_viewer/widget/src/running-corpus.json` — replaced by the
  producer's regenerated copy; `src/run/running-corpus.test.ts` — the
  width guard; `src/run/cost.test.ts` — what a constraint tick costs.
- `tests/fixtures/lock/` (new), `tests/support.py`, and a new
  Playwright acceptance beside `tests/test_running_document.py`.
- `CHANGELOG.md` under 0.2.0; `docs/adrs/EXPORT/ADR-054`, extracted after
  implementation.
- Nothing in the framework, and nothing of the document's shape: the two
  packages stay separate processes over an unchanged contract.
