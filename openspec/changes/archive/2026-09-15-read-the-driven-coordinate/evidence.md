# Evidence — proposal stage

Everything below was measured on this worktree at base
`30456007d65aae5d1b31bba2d711e72c2eb416a6`, with the workspace venv and
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`. No framework file was edited:
where a refusal had to be got out of the way it was monkeypatched at
runtime from a scratch script, which is stated at each point. The scripts
are reproduced in §5 so a reviewer can re-run them.

## 1. The three routes through the model as it stands

`spikes/routes.py`.

**A1 — a plain declared range on the wheel stops the RING.** A running
root with `ring = Driver(default=0)`, a wheel whose `turn` declares
`range=(None, 360)`, `ring.drives(wheel.turn, ratio=1.0)`, and
`move('ring', by=500, duration=1)` at `dt = 0.1`:

```json
{"wheel": 360.0, "ring": 360.0, "handle": "blocked", "admitted": 360.0,
 "stops": [["wheel.turn", "high", 360.0, 0.2, ["ring"]]]}
```

The ring is retired `blocked` with `360.0` of `500` admitted. That is
ADR-108 doing exactly what it says and exactly the opposite of the
mechanism: the missing tooth frees the ring.

**A2 — a `Bound` with reads gives the same answer.** The same root with
`range=(None, Bound(lambda turn, r: 360.0 * (r >= 0), reads=(ring,)))`:

```json
{"wheel": 359.9999999999909, "ring": 359.9999999999909,
 "handle": "blocked", "admitted": 359.9999999999909,
 "stops": [["wheel.turn", "high", 360.0, 0.1999999999998181, ["ring"]]]}
```

**B — a gate over the ring's own travel loses the wheel's history.**
`ring.drives(wheel.turn, law=…)` over `90 * clamp01((ring - 100) / 90)`,
swept forward, returned, and swept again:

```json
{"after_first_sweep": 90.0, "after_return": 0.0, "after_second_sweep": 90.0}
```

The wheel un-clears itself when the ring is returned and repeats its
former contribution on the second sweep — requirement items 2 and 3
failing together — and every wheel the same rack reaches would receive
the same contribution whatever digit it stood at, which is item 5.

**C — a duplicated coordinate does not solve.**
`wheel.turn.drives(shadow.turn, ratio=1.0)` plus
`(ring & shadow.turn).drives(wheel.turn, law=…)`:

```text
UnreachedCoordinate: wheel.turn drives shadow.turn: nothing bound either
end. wheel.turn and shadow.turn are both unbound when nothing changes any
more, so the relation has no side to be read from. Bind one of them in
simulate(), or state a relation that reaches one.
```

**D — the project's own diagnostic, verbatim from
`simulation/tools/direct_operation_probe.py`:**

```text
TypeError: wheel.rotation is named as both a source and a driven end of
one relation: a coordinate is a source or a driven end of one relation,
not both.
```

**E — `a.drives(a)`, one to one, is not refused at class definition** and
deadlocks exactly as ADR-100 predicted when it declined to widen the
check:

```text
UnreachedCoordinate: wheel.turn drives wheel.turn: nothing bound either
end. …
```

## 2. Deleting the refusal is not an implementation

`spikes/deleted.py`, `spikes/rest.py`, `spikes/rest2.py`. Each step
monkeypatches out exactly one thing and reports the NEXT failure.

**Step 1 — `_refuse_shared_coordinate` made a no-op.** The project's own
fixture, with the guarded rest default:

```text
DoublyBound: wheel.rotation would be bound by the relation
(rack, wheel.rotation) drives wheel.rotation and by the author's
simulate(). A coordinate has exactly one binder in one enumeration of the
tree, and the framework does not compare two values to decide whether two
statements agree …
```

With no rest default:

```text
UnreachedCoordinate: (rack, wheel.rotation) drives wheel.rotation:
waiting for wheel.rotation. It is unbound when nothing changes any more …
```

Untimed, the guarded shape gives the same `DoublyBound`. This is the
measurement behind design.md §5: the rest render must be told to leave
such a relation alone, and the rest value must be the author's own.

**Step 2 — `_step_relation` also made to record the relation solved
forward without applying it.** The untimed rest pose then comes out
correctly at `{"rotation": 108.0}` with nothing refused, and the COMPILE
is what fails:

```text
UnsupportedLaw: the relations (rack, wheel.rotation) drives wheel.rotation
form a cycle the run cannot order: each waits on a coordinate another
determines. A running program is acyclic, because the rest render solved
every relation in one direction.
```

That is `_ordered`, and it is the measurement behind design.md §6.

**Step 3 — the Kahn ordering also patched to ignore a need an edge gives.**
The program now compiles, and its shape is exactly what design.md §2
predicts:

```text
root __main__.Clearing
input rack dtype=None scale=None
coordinate wheel.rotation
law ['rack', 'wheel.rotation'] -> ['wheel.rotation']
  (rack * ((wheel.rotation - (360.0 * floor((wheel.rotation / 360.0)))) >= 36.0))
  [(rack, wheel.rotation) drives wheel.rotation]
```

- the described listing NAMES the read, so the identity changes for free;
- the skeleton is `(rack * $j1)` and does NOT name `wheel.rotation`, which
  is the switch test of design.md §2 passing structurally;
- both jump levels are affine: `floor` over `wheel.rotation / 360.0`, and
  `>=` over `(wheel.rotation - 360.0 * $j0) - 36.0`.

**And the tick is silently wrong.** From a wheel at `108`, a `500`-degree
rack sweep:

```json
{"initial": {"rack": 0.0, "wheel.rotation": 108.0},
 "after_500": {"rack": 500.0, "wheel.rotation": 608.0},
 "status": "completed", "crossings": [],
 "after_second_500": {"rack": 1000.0, "wheel.rotation": 1108.0}}
```

No crossing was located at all. The self-read source's increment is zero,
so the level never moves, the gate is frozen open for the whole tick, and
`f(end) − f(start)` hands the wheel the rack's entire travel — on every
sweep, forever.

## 3. What a crossing's arithmetic lands on

`spikes/landing.py`, 200 000 randomized crossings.

**Solving `t*` and evaluating the segment does not land on the surface.**
Over 200 000 affine crossings, `start + rate * t*` missed the surface
619 times (0.3 %); recomputed the way a SEGMENT recomputes it — every
admission scaled by `t*` and the law re-evaluated — it missed 6 482 times
(3.2 %). Every single miss left a `wheel % period > 0` gate reading
ENGAGED. Something must place the coordinate; the arithmetic alone does
not.

**`spikes/snap.py`'s comparison is WITHDRAWN.** It measured two candidate
rules — "the segment's own arithmetic" and "the level solved for the
coordinate" — and concluded that nothing should be snapped. The second
rule as that script writes it takes the slope of the level from two
evaluations one unit apart and then divides by it, which loses about a
thousand ulps to cancellation: the table measured that formulation, not
snapping, and decides nothing. The script is kept for the record with
this note; §7 measures the rule the design actually adopts, through the
framework's own classes rather than through hand-written arithmetic, and
the first rule — committing what the segment's arithmetic gives — is the
one that fails there.

**A gate with no width, for the record.** With `modulo(own, period) > 0`,
whose disengaged state is one value, 321 of 190 683 crossings left the
gate engaged in the same sweep. Under §7's far-side landing the FORWARD
case of that gate does hold — the far-side float nearest `own / period =
1` is exactly the multiple, where `> 0` reads false — but a wheel
arriving from ABOVE has the ENGAGED region as its far side and runs on.
A single point is not a gap; the design's band is (`design.md` §4).

## 4. The jump plan of the proposed law shape

`spikes/planned.py`, applying the framework's own `_graph_of` and
`_plan_of` to the law with the driven coordinate entering as an ordinary
source token.

`rack * (wheel % 360 > 0)` compiles to skeleton `(rack * $j1)` with two
jump nodes:

| node | placeholder | level | affine |
| --- | --- | --- | --- |
| `%` | `$q0` | `wheel / 360.0` | yes |
| `>` | `$j1` | `(wheel - $q0 * 360) - 0` | yes |

Both levels are affine, so both crossings are SOLVED. Cutting a path from
`wheel = 108` with a rack delta of `500` gives cuts `[0.0, 0.504, 1.0]`
and one crossing, the `%` node's surface `1.0` at `t = 0.504` — the
fraction at which the wheel reaches `360`. The comparison contributes no
crossing of its own, which is the measured form of the knife-edge
problem: `wheel % 360 > 0` reads TRUE on both sides of the surface.

`rack * clamp01(((-wheel) % 360) / 36)` has a NON-affine skeleton
(`clamp01` is `min`/`max`), so its crossings fall to the search — correct
but slower, and a reason the fixture's gate is written as a comparison.

## 5. The scripts

`spikes/routes.py`, `spikes/deleted.py`, `spikes/rest.py`,
`spikes/rest2.py`, `spikes/planned.py`, `spikes/landing.py`,
`spikes/snap.py` (withdrawn, §3), `spikes/broadcast.py` (§6),
`spikes/landing2.py` (§7) and `spikes/layers.py` (§8). Each is self-contained, imports only the
framework's public surface plus the monkeypatches it declares at the top,
and is run from a directory holding a solid-node manifest with
`PYTHONPATH=<worktree>` and `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`.

## 6. A broadcast source member, paired per copy

`spikes/broadcast.py`. A running root declaring `wheels = Dial().repeat(4)`
and `(ring & wheels.turn).drives(wheels.turn, law=...)`, with
`BroadcastRef.check('driver')` and `_refuse_shared_coordinate`
monkeypatched out.

- The repeated SOURCE member and the DRIVEN end have the SAME ref key:
  `('broadcast', <the repeat declaration>, ('turn',))`. Recognition needs
  no new machinery.
- `Relation.resolve` as it stands cannot do it — the source group goes
  through `_resolve_ends`, which refuses:
  *"'wheels' of Register is 4 children, so the path wheels.turn names no
  single coordinate"*.
- The candidate implementation is ELEVEN LINES over
  `BroadcastRef.resolve_all` — the same call the driven side already
  makes — resolving a source member per copy where its key is one the
  relation drives and once for every copy where it is not. With it, four
  records are solved, and in each one the source member and the driven
  end are THE SAME SLOT of THE SAME COPY (`wheels-0 … wheels-3`), no two
  copies sharing one, the plain `ring` member resolving to the parent's
  driver in all four.

So the broadcast stays in this cycle (`design.md` §1), and the couplings
delta's "a broadcast is never a source" carries the one exception.

## 7. The far-side landing, measured through `Sim`

`spikes/landing2.py`. The walk of `design.md` §3 and the landing of §4
are prototyped as monkeypatches over `Edge.increments`, and
`Run.integrate` is wrapped so the reported landing is what the bank
commits; everything else — the class body, realization, the rest render,
the compile, the segment loop, the plan, the branch reading, the crossing
search, `Sim`, `move`, `run`, `snapshot` — is the framework's own. The
fixture is a ring driving one wheel through the BAND gate

```python
shifted = wheel + GAP
ring * (shifted - PERIOD * floor(shifted / PERIOD) >= 2 * GAP)
```

randomized over the starting angle, the ring's travel and direction, the
period (`360`, `36`, `11.25`, `100`, `1` and uniform draws in
`[0.1, 1000]`) and the gap width (`1e-9`, `1e-6`, `1e-3`, `0.01` and
`0.1` of the period). Each trial sweeps once, then sweeps three more
times with the ring running on, and checks the gate's branch, the bank's
float and the landing's neighbour.

| rule | trials | gate still ENGAGED after the cut | refused | wheel moved on a later tick |
| --- | --- | --- | --- | --- |
| the segment's own arithmetic | 20 000 | **1 253 (6.3 %)** | **2 541 `TooManyCrossings` (12.7 %)** | 0 |
| the far-side landing | 200 000 | **0** | **0** | **0** |

The refusals are the first rule's own remedy failing: committing a ulp
short re-engages the gate, the walk cuts at the same surface again, and
the piece count runs to `_MAX_CROSSINGS`. Its worst landing sat
1.6e9 ulps from the band's edge.

With the landing, every one of the 200 000 crossings put the wheel at
most **2 ulps** from the band's edge, on the DISENGAGED side, with the
float one step back toward the surface reading ENGAGED — the nearest
representable far-side value, by direct test — and the wheel stood
bit-identically still through three further sweeps. The walk cost **4.3
evaluations per cut** on average, and in 58 % of cuts the segment's
arithmetic had already landed PAST the surface, so the walk has to work
inwards as often as outwards — which is why it brackets and bisects
rather than stepping one way.

Worked, in both directions, at `PERIOD = 360`, `GAP = 3.6`:

```json
{"from 108 forward 500": 356.4, "again": "unchanged",
 "from 108 backward 500": 3.5999999999999996, "again": "unchanged",
 "from 0 forward 500": 0.0, "from 359 forward 500": 359.0}
```

The dial stops at the band's LOWER edge sweeping forward and at its UPPER
edge sweeping backward; a dial already standing inside the band does not
move in either direction.

## 8. The two layers compose

`spikes/layers.py`, over the same prototype. One law carries BOTH kinds of
jump: a rack station window over the ring alone —
`floor((ring - 100) / 300) == 0` — and the band gate over the wheel's own
angle. The plan comes out as

```text
skeleton ((ring * $j1) * $j3)
  floor $j0  ((ring - 100.0) / 300.0)                     affine
  ==    $j1  ($j0 - 0.0)                                  affine
  floor $j2  ((wheel.rotation + 3.6) / 360.0)             affine
  >=    $j3  (((wheel.rotation + 3.6) - (360.0 * $j2)) - 7.2)  affine
```

and the dependence test sorts it exactly as `design.md` §3 requires:
`$j0`, `$j1` INDEPENDENT (layer one, ADR-107 unchanged), `$j2`, `$j3`
DEPENDENT (layer two, walked), `$j1` independent although its argument is
a placeholder, because the node it stands for is independent too.

| sweep | wheel | crossing | second sweep |
| --- | --- | --- | --- |
| `+900` through the whole window | `356.4` | `floor` at `t = 0.387` | unchanged, bit for bit |
| `+90`, short of the window | `108.0` (untouched) | none | moves — the ring now enters the window, which is the mechanism |
| `-900` back through the window | `3.5999999999999996` | `>=` at `t = 0.672` | unchanged, bit for bit |

The same `+900` sweep taken in 1, 12 and 240 ticks leaves the wheel at
`356.4` in all three — identical floats, not merely inside the agreement
window — so the accuracy contract holds with both layers in one law.

# Evidence — implementation stage

Everything below was measured on this worktree with the workspace venv
and `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one process at a time,
against the framework's OWN classes — no monkeypatch except where a RED
table needs one switch, which is stated at that point. The "before"
figures come from a pristine copy of the planning commit `cd3e6ca`
extracted with `git archive HEAD | tar -x` into a scratch directory, so
they are measured rather than remembered.

## 9. The refusals, RED then GREEN

`tests/test_couplings.py::SelfReadTest`, RED at `cd3e6ca`:

```text
E TypeError: wheel.turn is named as both a source and a driven end of one
  relation: a coordinate is a source or a driven end of one relation, not both.
E AssertionError: 'ONE coordinate' not found in 'child.spin is named as both a
  source and a driven end of one relation: ...'
E TypeError: 'wheels.travel' passes through the repeated declaration 'wheels' of
  Bead (count=4), so it cannot be the SOURCE of a relation: ...
5 failed, 2 passed, 177 deselected
```

GREEN: `182 passed, 178 subtests passed` over the whole file.

`tests/test_running_simulation.py::SelfReadRestTest`, RED (the compile
refusal `evidence.md` §2 predicted, reached now that the rest rule lets
the render through):

```text
E solid_node.simulation.program.UnsupportedLaw: the relations
  (setter, ring, wheel.turn) drives wheel.turn form a cycle the run cannot
  order: each waits on a coordinate another determines.
8 failed, 2 passed, 75 deselected
```

GREEN: `8 passed, 2 subtests passed`.

One EXISTING test changed, and only because the spec changes its message:
`GroupRefusalTest::test_a_coordinate_on_both_sides_of_a_group_relation_is_refused`
asserted `'not both'`; the driven end there is a GROUP, so the shape is
still refused and now says `ONE coordinate` (tasks 2.3). Nothing else in
the suite was edited to pass.

## 10. The tick, RED then GREEN

With recognition and the compile in place but no walk, one tick of the
reduced fixture reproduced §2's silently wrong answer — the rack's whole
travel handed to the dial, no crossing located. With the two-layer walk
and the far-side landing (`tests/test_running_reads.py`):

```text
forward:  digit 0 -> 0.0 (unmoved); 36 … 324 -> 359.5, and the SAME float
          after a second and a third sweep
backward: digit 36 … 324 -> 0.4999999999999999, unchanged on a further sweep
cadence:  the same 600-degree sweep in 1, 12 and 240 ticks -> 359.5 in all
          three, identical floats, ring 600.0
```

`tests/test_running_reads.py`: `32 passed, 60 subtests passed`.

## 11. The far-side landing, measured through the IMPLEMENTATION

`spikes/landing2.py` measured the rule over monkeypatches. The same sweep
was re-run against the framework's own `_Walk`, with the ONLY switch
being `_Walk._land` replaced by "commit what the segment's arithmetic
gives" for the RED table. Randomized over the starting angle, the ring's
travel and direction, the period (`360`, `36`, `11.25`, `100`, `1` and
uniform draws in `[0.1, 1000]`) and the gap width (`1e-9` … `0.1` of the
period); each trial sweeps once and then three more times with the ring
running on.

| rule | trials | gate still ENGAGED after the cut | refused | moved on a later tick | worst distance from the band edge |
| --- | --- | --- | --- | --- | --- |
| the segment's own arithmetic | 20 000 | **1 247 (6.2 %)** | **2 541 `TooManyCrossings` (12.7 %)** | 0 | 1.6e9 ulps |
| the far-side landing | 50 000 | **0** | **0** | **0** | **2 ulps** |

The spike's own table was 6.3 % and 2 541 refusals over 20 000, so the
implementation reproduces it. In every one of the 50 000 landings the
float one step back toward the surface reads ENGAGED, which is the direct
test that the landing is the NEAREST representable far-side value.

## 12. Rule (c), measured

A dial placed exactly at `360 + GAP` — where the gate's `>=` sits exactly
on its surface and the operator reads ENGAGED — swept BACKWARD holds at
`360.5`, and swept FORWARD turns to `719.5`. Without the flip at the
piece's left end the backward sweep finds no crossing (the level LEAVES
the surface rather than reaching it) and the piece is integrated engaged,
carrying the dial straight through its gap. Both directions are pinned by
`OnSurfaceTest::test_a_wheel_on_a_band_edge_is_not_driven_through_it`.

A gate whose two branches each carry the level back across one surface at
a piece's left end refuses the tick as a sliding mode
(`SlidingRead`), committing nothing.

## 13. The searched crossing, and one thing the prototype never met

The prototype reported `searched cuts: 0` — every gate it ran was affine.
The Curta shape of task 1.3 is the first searched case, and it found a
defect the prototype could not have: with the skeleton non-affine, a
dependent node whose branch HOLDS the driven coordinate sits exactly on
the surface it was landed at for the whole piece, and the search's
`_surfaces(..., inclusive=True)` reports that surface as reached over and
over, running the walk to `_MAX_CROSSINGS`:

```text
TooManyCrossings: (clearing, result0.turn) drives result0.turn: over one tick
result0.turn would cross 1001 surfaces of floor …
```

The fix is one line in `_Walk._searched`, and it is a statement of fact
rather than a tolerance: **a level that does not MOVE crosses nothing**,
so a sub-interval over which the level is unchanged is skipped. With it
the whole six-dial register clears:

```text
rest   result0..2 = 36, 72, 108;  counter0..2 = 144, 180, 216
after  every one of the six at 359.5, clearing = 1.0
back   every one of the six at 359.5 — the ring returned, the register not
```

`CurtaShapeTest` pins it, restating the rack's arithmetic (nine teeth of
36 degrees is 324, and every dial rests within 324 + GAP of its gap)
rather than calling the law.

## 14. Performance

`Train`, the pin for "a law with no self-read changes in nothing",
measured with the same probe on the base tree and on this one:

| | graph evaluations over 10 ticks | 200 ticks, best of 7 | median |
| --- | --- | --- | --- |
| base `cd3e6ca` | 80 | 92.8 ms | 96.1 ms |
| this worktree | 80 | 93.6 ms | 94.5 ms |

The evaluation count is IDENTICAL and the wall time is inside the spread
of the repeats. `test_the_train_pays_what_it_always_paid` asserts the 80
directly and still passes.

The price of a self-read law, at `GraphValue.evaluate` granularity:

| fixture | shape | ticks/s | graph evaluations per tick |
| --- | --- | --- | --- |
| `Clearing` | affine skeleton, crossings SOLVED | 1 349 | 99 |
| `CurtaInterface` | `clamp01` station window, skeleton NOT affine, crossings SEARCHED | 24.4 | 2 861 |

So the migration's own shape costs about 29 times the solved one per
tick, which is design.md §11's prediction with a number on it: six dials,
64 samples per piece plus the bisection behind each. A cheap exact path
for a kinked-but-piecewise-affine skeleton would remove it, and is
recorded as a follow-up.

## 15. The suites

| suite | before (`cd3e6ca`) | after |
| --- | --- | --- |
| the five named regression files plus the corpus | 452 passed, 663 subtests | 465 passed, 673 subtests |
| whole suite, sequential | 2 866 passed, 4 skipped, 1 580 subtests, 3 failed, 291.8 s | **2 925 passed, 4 skipped, 1 662 subtests, 0 failed, 324.8 s** |

The three failures in the "before" column are the extracted scratch
tree's own, not the framework's: `test_build_lock` and
`test_builder_lifecycle` inspect the project's sources and fail there
with `'Mock' object is not iterable` because the copy is not a checkout.
All three pass in this worktree, where the whole suite is green. So the
suite went from 2 869 tests to 2 925 (+56) and from 1 580 subtests to
1 662 (+82), with nothing removed and one existing assertion changed
(§9).

Those are the implementation stage's counts. The closure stage's three
further tests and their re-run of the whole suite are §21.

Commands:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python -m pytest tests/test_couplings.py tests/test_running_simulation.py \
    tests/test_running_jumps.py tests/test_running_stops.py \
    tests/test_running_document.py tests/test_running_corpus.py -q
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python -m pytest tests -q
```

## 16. The corpus

`tools/generate_running_corpus.py` gained three scenarios over two new
machines and three required features. Regenerated:

```text
tests/running-corpus.json: 17 scenarios over 14 machines (Captured, CarryLead,
Clearing, Clutch, Ratchet, Remainder, StopAndJump, StoppedClearing, Swept,
Throwing, Train, TwoStops, Window, Wrapped), 328 ticks, 229068 bytes
```

Every EXISTING scenario is byte-identical to the committed fixture —
checked entry by entry against the previous file, `14` old scenarios, `3`
added, `0` removed, `0` changed — and the tolerance is unchanged.
`tests/test_running_corpus.py` replays it (`10 passed, 51 subtests`) and
the generator refuses a corpus that states no self-read law, that holds
no dial at its gate while the input reaching it moves on, or that carries
no tick with both a self-read crossing and a stop.

## 17. What the design did not anticipate

1. **A `.repeat()` broadcast self-read cannot be a RUNNING machine.**
   design.md §10 asks the corpus for "a self-read under `.repeat()`". A
   repeated child's JOINT coordinate has no qualified id the run can bank
   it under, and a running root already refuses it — measured on the base
   tree, with no self-read anywhere in sight:

   ```text
   DriverIdError: cannot qualify driver 'turn' through node segment
   'wheels-0': a qualified driver id must be a legal identifier …
   ```

   The couplings spec's requirement is about RESOLUTION, and that is
   implemented and tested: four records, each copy reading its own slot,
   no two copies sharing one
   (`SelfReadTest::test_each_copy_of_a_broadcast_reads_itself`). The
   export spec's generator list does not name `.repeat()`, so the ratified
   contract is met; only design.md §10's prose is not.

2. **A knife-edge gate held in every case probed.** design.md §4 says a
   gate whose disengaged set is a single value "runs on" when the
   coordinate arrives from above. It does not, and the reason is the
   landing's own shape rather than luck with the arithmetic: `_land`
   walks the crossed nodes in the graph's postorder and judges each with
   the OTHER nodes at the piece's NEAR-SIDE branches, so where a `floor`
   surface and a comparison surface are coincident in the coordinate —
   which is what a knife edge is — the floor's far-side walk lands the
   coordinate exactly ON the surface, and there the comparison's operator
   reads disengaged. Probed over ratios `1`, `7/3`, `0.7` and `π`, digits
   `108`, `107.3` and `12.345`, both directions and two step sizes, it
   landed exactly on the surface every time. So `KnifeEdgeTest` pins what
   is true — the disengaged set is ONE float, and the dial holds where
   the far side of the surface is disengaged — and `docs/scenarios.rst`
   promises neither the failure nor the hold. The open question stands:
   the framework still cannot tell a knife edge from a band, a single
   float is not a gap, and nothing guarantees another model's numbers
   land on the surface rather than past it. design.md's "Implementation
   notes (2026-09-15)" records it.

# Evidence — closure stage

The adversarial review of the implementation returned four findings. They
were closed on this worktree, measured the same way as everything above:
the workspace venv, `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one
process at a time, against the framework's own classes with no
monkeypatch anywhere. design.md's "Implementation notes (2026-09-15)"
carries the account; this section carries the numbers.

## 18. C1: a phantom crossing, and a flip to a branch the piece never enters

The gate that shows it is `crowded_gate` — a dial whose read changes its
RATE rather than stopping it: two units of wheel per unit of ring over
the first half of every tooth and one over the second, through a
`clamp01` window whose skeleton is NOT affine, so every crossing falls to
the sampled search. Sixty of ring is eighty of wheel, and eighty of wheel
crosses 160 surfaces.

RED, at the implementation under review, with the framework's own classes:

```text
sweep by=+60 in one tick
E   solid_node.simulation.program.TooManyCrossings: (ring, wheel.turn) drives
    wheel.turn: over one tick wheel.turn would cross 1001 surfaces of floor,
    more than the 1000 a single law is admitted in one tick.

sweep by=-60 in one tick
E   solid_node.simulation.program.UnsupportedLaw: (ring, wheel.turn) drives
    wheel.turn: wheel.turn stands exactly on a surface of its floor and each
    branch carries the level back across it -- a sliding mode, not a mechanism.
```

1001 surfaces where 160 are crossed, and the sliding-mode refusal on the
very FIRST piece of the backward tick, before a single cut is taken
(traced: `_decide(t=0.0, right=1.0, own_left=0.0, taken=0)`). Two defects,
both in the walk and neither in the ratified design:

- **the phantom.** After a cut the far-side landing very often puts the
  `floor` node's level EXACTLY on the integer it landed at. The next
  sub-interval therefore STARTS on a surface, `_surfaces(…,
  inclusive=True)` returns it, and `_bisect` opens with a `below` of zero,
  which is never negative, so every round takes the `else` arm and the
  bracket collapses onto the sub-interval's RIGHT end. That was reported
  as a crossing inside the piece, and `_land` — walking outward from a
  value already on the near side — carried the coordinate to the NEXT
  surface. A whole unit per phantom, a thousand of them, then the refusal.
  It was invisible on a gate that HOLDS the part (there `level ==
  previous` for the whole piece and the sub-interval is skipped), which
  is why the Curta fixture passed over it.
- **the flip.** `_decide` took the branch to flip to from
  `_branch_of(probe)`, the level at the first differing sample. For a
  `floor` that sample can be a whole tooth away and names a branch the
  piece never enters; on this gate the wrong branch changed the rate, the
  next probe wanted a third, and the tick refused as a sliding mode. The
  branch is now the region IMMEDIATELY on the side the level departs to,
  `_branch_of(nextafter(surface, probe))` — unchanged for a comparison or
  `sign`, whose two regions are the only ones there are.

GREEN. One tick against sixty, both directions, three travels, the run's
own agreement window `1e-9 · max(1, |a|, |b|)`:

| sweep | one tick | cuts | sixty ticks | cuts | disagreement |
| --- | --- | --- | --- | --- | --- |
| `by=+60` | `79.99999999943458` | 159 | `80.00000000000091` | 160 | 0.007 of the window |
| `by=-60` | `-79.9999999992309` | 159 | `-79.99999999999834` | 159 | 0.010 |
| `by=+17.5` | `23.499999999968296` | 46 | `23.500000000001023` | 47 | 0.001 |
| `by=-17.5` | `-23.249999999958664` | 46 | `-23.250000000000746` | 46 | 0.002 |
| `by=+123.25` | `164.49999999651166` | 328 | `164.50000000000637` | 329 | 0.021 |
| `by=-123.25` | `-164.24999999851127` | 328 | `-164.24999999999437` | 328 | 0.009 |

No refusal anywhere, and the cut counts are twice the wheel's own travel
— the floor's integer and the comparison's half — rather than 1001.
`CrowdedTest::test_the_same_sweep_at_two_cadences_agrees` pins the first
row and its mirror.

**The refusal is now GENUINE.** `CrowdedTest::
test_a_tick_cut_too_many_times_is_refused` sweeps `by=600` — eight
hundred of wheel, sixteen hundred surfaces — and gets:

```text
(ring, wheel.turn) drives wheel.turn: over one tick wheel.turn would cross
1001 surfaces of >=, more than the 1000 a single law is admitted in one tick.
… The tick committed nothing: the bank, the tick count and the tree stand as
they were.
```

with the bank, the tick and the command's `refused` status all asserted.
The primitive named is the comparison and not `floor` because the two
surfaces alternate from a dial standing at zero, so the thousand and
first is the comparison's; the test says so where it asserts it.

**The landing rule is untouched by the fix, and re-measured to say so.**
400 randomized full sweeps of `Clearing` (digit uniform on `[0, 720)`,
both directions, `dt ∈ {1, 0.1, 1/24}`): 399 cut, and in every one of
them the landing reads DISENGAGED and the float one step back toward the
surface reads ENGAGED. The 400th rested in a band and was not cut, which
the check asserts rather than skips.

## 19. C2: a crossing a hair inside the left end

`_Walk._searched` returned a crossing only `if where >
t + _CROSSING_TOLERANCE`, on the reasoning that rule (c) had already
answered anything nearer by flipping. Rule (c) flips a level EXACTLY on a
surface — `_on_surface` is float equality — so a dial a hair SHORT of one
is not flipped, and its crossing at `t*` of the order of `1e-16` was
thrown away.

RED, on the Curta fixture (the SEARCHED shape), a dial resting at
`360 − GAP − 1e-11`, engaged by a hundred-billionth of a degree:

```text
E   AssertionError: 683.4999999999883 != 359.5
```

It did not stop at its gap: the piece integrated ENGAGED and the rack
carried the dial through the gap and on for the whole of its nine teeth.
The same dial on the affine `Clearing` fixture passed at the same moment
— the solved path has no such filter, and `_crossing` returns every
crossing strictly inside the piece — which is the control the test keeps.

GREEN: `NearSurfaceTest::test_a_dial_engaged_by_a_hair_stops_at_its_gap`
lands the dial at `359.5` exactly, and
`test_the_solved_shape_is_the_control` stays green beside it. The filter
is gone: with C1's exclusion of a surface at the sub-interval's left
sample, every crossing with `where > t` is returned.

## 20. C3: an unlanded landing is loud

`_Walk._far_side` returned `own_star` unchanged when no bracket was found
within `_WALK_STRIDES` doublings, committing in silence the one value §4
says is never committed. It now raises `LandingInvariantError` naming the
relation, the coordinate and the primitive, and `Run.integrate` refuses
the tick with it exactly as it refuses a broken stop invariant
(`StopInvariantError`, the kind it is modelled on).

No test reaches it, and none can: a cut exists because the level crossed
the surface, so the branch differs somewhere on either side of it, and
200 doublings of a ulp cover every distance a double expresses. The raise
says so in a comment where it stands, and this is the record of it. The
whole suite ran green with the raise in place, which is the only evidence
available that it is not reached.

## 21. The suites, at closure

| suite | at the implementation under review | after the closure |
| --- | --- | --- |
| `test_running_reads.py` | 32 passed, 60 subtests; the closure's new tests 4 RED | **35 passed, 62 subtests** |
| `test_running_jumps.py`, `test_running_stops.py`, `test_running_corpus.py`, `test_couplings.py` | not re-measured before the fix | **292 passed, 571 subtests** |
| whole suite, sequential | 2 925 passed, 4 skipped, 1 662 subtests (§15) | **2 928 passed, 4 skipped, 1 664 subtests, 0 failed, 316.3 s** |

`tests/running-corpus.json` was NOT regenerated: `test_running_corpus.py`
replays the committed fixture unchanged, so no committed scenario's
expected values moved — as expected, since no corpus scenario carries a
gate whose read changes the rate, and the searched path the closure
touched is reached by no committed scenario.

The `CurtaInterface` price of §14 was re-measured with the closure in
place: **27.2 ticks/s** against 24.4 before it, on the same one-job
machine — the same order, and if anything cheaper, because the phantom
cuts it no longer takes were work.

Commands:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python -m pytest tests/test_running_reads.py tests/test_running_jumps.py \
    tests/test_running_stops.py tests/test_running_corpus.py \
    tests/test_couplings.py -q
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONPATH="$PWD" \
    python -m pytest tests -q
```
