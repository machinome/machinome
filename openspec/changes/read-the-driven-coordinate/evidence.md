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
