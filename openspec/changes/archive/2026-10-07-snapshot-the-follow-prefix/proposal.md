## Why

A reused Follow prefix is not the kind of object a replayed one is.
`workflow/warts.md`, "Review of the cycles landed after the 0.7.0 fold
(2026-09-23)", second entry, recorded while reviewing the cycles that sped
up the Curta (`projects/Calculators/Curta-Type-I-3x`):

> **The Follow prefix cache stores mapping proxies where a propagation
> used to flow.** `Run._constraint_level` in `machinome/simulation/run.py`
> memoises a successful law-to-Follow prefix as
> `(MappingProxyType(dict(deltas)), MappingProxyType(dict(landings)))`.
> On a hit the rest of the method receives a plain read-only mapping, not
> the `Propagation` object the first walk produced, so `motions`,
> `untraced`, `follow_cuts` and `follow_closures` are absent. Today only
> item access follows the prefix, so it is correct; the first later change
> that reads a path attribute after the prefix will work on a miss and fail
> on a hit, and the focused tests would not necessarily catch it.
> **Deferred:** when that method is next touched, either snapshot the
> propagation itself (frozen) or assert the shape at the hit.

`Run._constraint_level` (`machinome/simulation/run.py:1062-1114`) walks a
Bound's sub-program at one fraction of the stretch. When the sub-program is
deterministic laws ending in a `Follow` edge, and the run is inside
`_reached` (which owns a stretch-local `prefix_cache`, `:851`), the walk's
result is stored under the edge sequence and the fraction's IEEE-754 bits
(`:1075-1096`). The paired Bound of the same Follow target then reads the
stored result instead of walking again (`:1097-1098`). The walk itself
produces a `Propagation` (`machinome/simulation/trajectory.py:61-76`), a
`dict` of displacements that also carries the paths the walk determined:
`motions`, `demanded`, `untraced`, `follow_cuts`, `follow_closures` and
`terminal_keys`. The store keeps only `MappingProxyType(dict(deltas))`.
After the branch (`:1099-1114`) the method reads the displacements and
landings by key alone, so every value is correct today. The defect is the
two shapes: one reading of a path attribute added after the branch passes
on a miss and raises `AttributeError` on a hit.

**Reproduced on the bench `fix-warts-3` at `1591276`**, with a scratch
script on the framework's own fixture `TwoSurfaces`
(`tests/test_running_follow.py`), whose `ball.slide` Bounds share one
`Follow` prefix. One call with a cache walks the prefix, and a second call
reads it back:

```
edges ['follow']
walks 1 cache entries 1
levels miss/hit 0x0.0p+0 0x0.0p+0
miss deltas type: Propagation follow_cuts {('slot', ...): (0.0, 1.0)} follow_closures keys [('slot', ...)] untraced {('slot', ...)} motions []
hit deltas type: mappingproxy isinstance Propagation: False
motions AttributeError: 'mappingproxy' object has no attribute 'motions'
untraced AttributeError: 'mappingproxy' object has no attribute 'untraced'
follow_cuts AttributeError: 'mappingproxy' object has no attribute 'follow_cuts'
follow_closures AttributeError: 'mappingproxy' object has no attribute 'follow_closures'
demanded AttributeError: 'mappingproxy' object has no attribute 'demanded'
terminal_keys AttributeError: 'mappingproxy' object has no attribute 'terminal_keys'
```

The walk the miss made carries a Follow cut and its closures. The object
the hit hands on carries none of the six attributes.

**The cache matters on the Curta, and the fix costs it nothing
measurable.** Forty 0.1-second crank ticks of `MechanisticCurta`
(`test_mechanistic.py`'s subtraction and addition, every carry moving),
one process per variant, pinned to one CPU, at `1591276`:

| Variant | Wall (s) | Prefix walks / stores / hits | Time in snapshots (s) |
|---|---|---|---|
| Bench as it is | 178.68 | — | — |
| Bench, exact copy with counters | 186.82 | 2856 / 2856 / 2856 | 0.0099 |
| Candidate: frozen propagation | 187.16 | 2856 / 2856 / 2856 | 0.0179 |
| No prefix cache | 239.43 | — | — |

Every variant commits the same 40 banks bit for bit (SHA-256
`167ea1cd…8b18b1fcf` over every key and every float's bits). The cache
saves about a quarter of the Curta's tick. The candidate snapshot costs
8 ms more over 2,856 stores against a run-to-run spread of 8 s between the
bench and its own exact copy. Timed alone on a Curta prefix of 301 keys, the
form this change specifies takes 2.46 µs per store against 1.25 µs today. The smallest project module
that exercises the Follow law, `simulation/test_radial_positioning_ball.py`
(four tests on `RadialBallTrial`: the ball pushed outward, pressed inward,
blocking the crank and the lift, and stopping at the same contact from a
long and a short request), passes 4 of 4 in 260.98 s on the bench and in
262.65 s with the candidate applied by monkeypatch; no test moves by more
than 1.4 s.

## What Changes

- **A reused prefix is a frozen propagation.** A new class beside
  `Propagation` in `machinome/simulation/trajectory.py`,
  `FrozenPropagation(Propagation)`, is built from a finished walk. It holds
  the same displacements and every attribute of the walk, a `dict` as a
  read-only mapping (`motions`, `follow_cuts`, `follow_closures`) and a set
  as a frozen set (`demanded`, `untraced`, `terminal_keys`). The attributes
  are copied from the walk itself, so one added to `Propagation` later is
  carried too. Every mutating `dict` method, item assignment and attribute
  assignment raises `TypeError`.
- **Both sides of the branch read the same object.**
  `Run._constraint_level` stores `(FrozenPropagation(deltas),
  MappingProxyType(dict(landings)))`, as it stored two read-only mappings
  before, and the walk that stores it continues with that same pair. A hit
  and the miss that published it therefore hand the rest of the method one
  shape, a read-only `Propagation` with its paths. A walk that is not
  eligible for the cache keeps its own mutable `Propagation`, as today.
- **One red test** in `tests/test_follow_prefix_cache.py`: after a walk
  that publishes a prefix, the stored propagation is a `Propagation`, has
  the walk's displacements and all six attributes, refuses item and
  attribute changes, and the paired Bound's level read from it is the
  uncached level bit for bit, without a second walk. Red today:
  `mappingproxy(...) is not an instance of <class
  'machinome.simulation.trajectory.Propagation'>`.
- **Records:** a changelog bullet under `Unreleased`; the warts entry moves
  to the campaign's `resolved.md`.

**Deliberately out**, with the reason:

- **Asserting the shape at the hit instead.** An assertion that nothing
  after the branch reads an attribute cannot be checked at run time; it
  would be a comment. The frozen snapshot costs nothing measurable and
  removes the second shape (design.md, Decision 1, Alternatives).
- **Storing the walked `Propagation` itself.** It would be the identical
  type at no copying cost, but one mutable object would then be shared by
  two Bounds. The cycle that introduced the cache required its snapshots
  to be immutable (`openspec/changes/archive/2026-09-23-cache-follow-prefix-probes/design.md`,
  Decision 2), and this change keeps that.
- **The tick's own propagation.** `_reached`, `_constraint_reached` and
  `_searched_constraint` read `follow_cuts`, `follow_closures` and
  `motions` through `getattr(deltas, ..., {})` (`run.py:858-860`,
  `:919-921`, `:945`, `:1010`). Those read the tick's propagation, which
  may be `None` for an internal caller. They are not the prefix and are
  unchanged.
- **The cache's scope, key and eligibility.** Unchanged: stretch-local in
  `_reached`, keyed on edge identity and fraction bits, laws ending in one
  `Follow`, successes only.
- **Projects.** Nothing in the Curta is edited. Its tests are run against
  the bench before and after.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `simulation`: the requirement "Equivalent Follow Bound prefix probes may
  reuse a successful propagation" is modified. One sentence is added: a
  reused prefix is the propagation a replay produces, its displacements
  and the paths it determined, read-only, and the walk that publishes it
  continues with the same snapshot. One scenario is added, "A reused prefix
  carries what a replay carries". The three existing scenarios are carried
  unchanged.

## Impact

- **Code:** `machinome/simulation/trajectory.py`, one class after
  `Propagation` (`:61-76`). `machinome/simulation/run.py`,
  `_constraint_level` (`:1093-1096`): the stored pair and one line that
  continues the walk with it; one import.
- **Tests:** `tests/test_follow_prefix_cache.py`, one test added. Every
  existing test passes unchanged.
- **Values:** no level, landing, stop, bank, verdict, refusal or snapshot
  changes. `tests/running-corpus.json`, `tests/clocked-corpus.json` and
  `tests/time-drive-corpus.json` replay byte-identical and are not written.
- **Documents, declarations, the viewer, projects:** unchanged.
- **Cost:** about 1.2 µs more per stored prefix; some 3.5 ms over the
  2,856 stores of forty Curta ticks of about 180 s.
- **Manual:** `docs/architecture.md` and `docs/concepts/running.rst` do not
  describe the prefix cache's storage and stay correct. The changelog gets
  one bullet.

## Authorization

The pilot's mandate of 6 October 2026 for the fix-warts-3 campaign
(`workflow/ongoing/fix-warts-3.md`, "Mandate"): "work on the items you can
autonomously, orchestrating opus subagents and using empirical evidence
from projects to validate, other than your adversarial review. if
something needs my input, record and defer, you'll go unsupervised." This
change is the campaign table's cycle 8, `snapshot-the-follow-prefix`,
validated in Curta-Type-I-3x. It changes no value and costs the Curta's
tick nothing measurable, so it needs no decision of the pilot's; design.md
records the alternatives.
