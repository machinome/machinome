## MODIFIED Requirements

### Requirement: A running root's simulation owns every driver and joint coordinate

Under a root assembly declaring `time = Time.running()` the simulation
SHALL own a BANK holding every driver AND every joint coordinate of the
linked tree — on assemblies and leaves alike, class-declared and
site-declared joints alike — keyed by the qualified id the driver
enumeration and the port enumeration produce: the instance path joined
with the driver's name, the joint's name, or `<joint>.<coordinate>` for a
joint owning several. `sim.state` SHALL return the whole bank by id, as a
fresh mapping. Plain ports and derived coordinates SHALL NOT be in the
bank: they are computed by the ordinary enumeration from the bank on
every tick. There SHALL be no separate memory bank, and the author SHALL
declare no state. An id two declarations of one node would both claim
SHALL be refused at construction naming both.

The initial bank SHALL be the untimed rest pose at the requested driver
values: construction SHALL bind the driver values (the declared defaults,
overridden by `state=`) with `time` at zero, enumerate the tree once
exactly as an untimed root is enumerated — the author's `simulate()` and
every relation solving as they do today, except a relation that reads its
own driven end, which binds NOTHING at rest under the requirement "A law
may read the coordinate it drives" — and read every joint coordinate
off the tree. A joint coordinate that rest render leaves unbound SHALL be
refused at construction naming the node path and the coordinate and
saying that the run owns every joint coordinate and needs a rest value for
each.

From the moment construction completes, every bank coordinate SHALL be
bound by the run — through `set_state` with the whole bank and `time`,
the run recorded as the binder — so that `render()` and `simulate()` stay
pure functions of the bound snapshot: rendering, inspecting, or binding
the same snapshot again SHALL advance nothing and change no value. An
author's `simulate()` that binds a run-owned coordinate SHALL be refused
as doubly bound naming the class and the coordinate, at construction; a
binding written under a guard that finds the coordinate already bound is
not a binding and SHALL keep working.

`sim.time` SHALL remain `tick * dt`, and every instant, duration and
period SHALL keep the whole-tick rule.

ONE simulation SHALL own a tree at a time, and the newest SHALL take it.
Constructing a simulation over a tree a previous run owns SHALL RELEASE that
ownership before the rest render: the run's claim on the tree and on every
joint coordinate it bound is dropped, so the rest render finds a tree no run
owns and poses it exactly as it would a tree no run ever touched. A released
run SHALL REFUSE to advance, naming both simulations and saying its bank no
longer describes the tree, rather than binding over the simulation that now
owns it. This is what makes a fresh simulation per call possible over a node
built once and shared — the contract the scenario base states — and it does
not weaken the doubly-bound refusal: an author's `simulate()` binding of a
run-owned coordinate is still refused, because a release happens only before
the rest render of a NEW simulation and never during one.

A declared driver or joint coordinate whose qualified id is `time` SHALL be
REFUSED at construction, naming the id and the reservation: `time` is the one
snapshot entry that is global by contract, the run binds it beside the whole
bank on every tick, and a bank entry under that id would be silently
overwritten.

#### Scenario: The bank lists joint coordinates by qualified id

- **WHEN** a simulation is constructed over a running root declaring
  drivers `crank` and `lever`, its own joint `spindle` wired into a
  child's plain port `wheel.turn`, children `first` and `second` each
  owning a `turn` joint on a leaf, and a child `slide` owning a `travel`
  joint
- **THEN** `sim.state` has exactly the keys `crank`, `lever`, `spindle`,
  `first.turn`, `second.turn` and `slide.travel` — the plain port
  `wheel.turn` among them nowhere

#### Scenario: The initial bank is the rest pose

- **WHEN** the same root states `crank.drives(first.turn, ratio=2.0)`,
  `first.turn.drives(second.turn, ratio=-1.5)` and
  `lever.drives(slide.travel, law=tooth_window)`, and the simulation is
  constructed with `state={'crank': 10.0}`
- **THEN** the initial bank reads `first.turn == 20.0`,
  `second.turn == -30.0` and `slide.travel` equal to the law at the
  lever's default — the values the untimed root poses at

#### Scenario: Rendering and rebinding advance nothing

- **WHEN** a running simulation has moved its crank for ten ticks and the
  caller then renders the node, reads every coordinate, and calls
  `set_state` with `sim.state` and `time=sim.time` once more
- **THEN** `sim.state`, `sim.tick` and every joint coordinate on the tree
  are unchanged, and the next tick continues from the same bank

#### Scenario: An author binding of a run-owned coordinate is refused

- **WHEN** a running root's `simulate()` binds `self.first.turn` from its
  crank unconditionally
- **THEN** construction is refused naming that class and `first.turn` as
  doubly bound, saying the running simulation owns it and a law belongs
  in a relation

#### Scenario: A guarded rest default keeps working

- **WHEN** a running root's `simulate()` reads `self.slide.travel.value`,
  finds it `None` and binds `4.0`
- **THEN** construction succeeds, the bank reads `slide.travel == 4.0`, and
  the guard never binds again while the run owns the coordinate

#### Scenario: An unbound joint coordinate is refused at construction

- **WHEN** a running root's rest render leaves a joint coordinate unbound —
  nothing drives it and no `simulate()` binds it
- **THEN** construction is refused naming its qualified id and saying the
  run needs a rest value for every joint coordinate

#### Scenario: A joint on a leaf is owned like any other

- **WHEN** the joint `turn` is declared on a leaf class held as `first`
- **THEN** `first.turn` is in the bank, the run binds it on every tick, and
  the leaf's body is placed by the bound value

#### Scenario: A second simulation over one tree starts fresh

- **WHEN** a simulation over a running root has moved its crank for twenty
  ticks and a second simulation is constructed over the SAME node
- **THEN** construction succeeds, the second simulation's bank is the rest
  pose — identical to the first's initial snapshot — and nothing is refused
  as doubly bound

#### Scenario: A released simulation refuses to advance

- **WHEN** a simulation whose tree a later simulation has taken over is
  stepped
- **THEN** it refuses naming both simulations and saying its bank no longer
  describes the tree, and the tree is left as the owning simulation posed it

#### Scenario: An author binding is still refused

- **WHEN** a running root's `simulate()` binds a run-owned coordinate
  unconditionally
- **THEN** construction is refused as doubly bound, naming the class and the
  coordinate, exactly as before

#### Scenario: A driver named for the clock is refused

- **WHEN** a running root declares a driver whose qualified id is `time`
- **THEN** construction is refused naming the id and saying `time` is
  reserved for the simulation clock

#### Scenario: A rest default under a self-read relation is the bank's value

- **WHEN** a running root states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` and the
  wheel's own `simulate()` binds `108.0` under `if ... is None`
- **THEN** construction succeeds, the initial bank reads
  `wheel.turn == 108.0`, the relation bound nothing at rest, and nothing
  is refused as doubly bound

#### Scenario: A self-read relation with no rest default is refused

- **WHEN** the same root's wheel declares no rest default, so the rest
  render leaves `wheel.turn` unbound
- **THEN** construction is refused naming that qualified id and saying
  the run needs a rest value for every joint coordinate



### Requirement: A jump is located inside the tick and subtracted

Under a running root a law whose expression contains a DISCONTINUOUS
primitive SHALL contribute, over one tick, the CONTINUOUS part of its
change: the tick's path SHALL be cut at every crossing of every jump
surface it meets, and the law's change SHALL be summed over the pieces
between those cuts, so that no jump ever moves a part.

The PATH of a tick SHALL be the straight line from the values the law's
sources hold to those values plus the increments they were given,
parametrised by a fraction `t` in `[0, 1]` — in the JOINT space of the
sources for a law naming several. A tick in which no source moves SHALL
contribute zero without evaluating the law.

Each jump node SHALL have a LEVEL QUANTITY and a family of SURFACES:
`floor(x)` and `ceil(x)` over `x` at every integer; `sign(x)` over `x`
at zero; `a % b` over `a / b` at every NONZERO integer, the operator
being the remainder that takes the sign of the DIVIDEND and is
therefore continuous where `a / b` crosses zero; a comparison over
`a − b` at zero. `wrap()` SHALL be integrated as the `ceil` it is built
on, and `piecewise()` SHALL need nothing, being built on `clamp01`.

On each open piece between two cuts every jump node SHALL hold one
BRANCH — the integer for `floor` and `ceil`, `-1`, `0` or `+1` for
`sign`, the integer quotient for `%` so that the node reads `a − q·b`,
and `1` or `0` for a comparison — determined by evaluating its level
quantity at the MIDPOINT of that piece, in the graph's postorder so
that a jump nested inside another's argument is determined first — with
the one amendment the requirement "A law may read the coordinate it
drives" states for a node that DEPENDS on the law's own driven
coordinate, whose value at a midpoint is a consequence of the branch
being asked for. The
law with those branches substituted SHALL be continuous on the closed
piece, and the increment SHALL be the sum, over the pieces, of that
substituted law's value at the piece's end minus its value at the
piece's start. A piece's endpoints SHALL therefore carry the one-sided
values of the law, at the tick's own start and end as well as at each
cut.

Crossings SHALL be found for every jump node of the law, in the graph's
postorder, over each piece the nodes before it have already produced,
and ALL crossings of one node inside one piece SHALL be found — not
only the difference of the piece's endpoints. Where the level quantity
is AFFINE in the sources along the path the crossings SHALL be solved
exactly, every surface between the endpoint values included; otherwise
the piece SHALL be sampled at a fixed number of sub-intervals and each
bracketed crossing located by bisection to a stated tolerance, with the
limit of that search documented. Two crossings closer than the
tolerance SHALL be one cut, and several jump nodes crossing at one
fraction SHALL be one cut whose midpoint sample fixes every branch at
once. For a law that reads its own driven coordinate THIS partition SHALL be
built over the jump nodes that do NOT depend on that coordinate, and the
nodes that DO SHALL be walked piece by piece INSIDE each of its pieces,
under the requirement "A law may read the coordinate it drives", because
the path of that coordinate on one piece is a consequence of the
branches of the piece before it. Merging two crossings closer than the
tolerance into one cut belongs to THIS partition and SHALL NOT be
applied in that walk.

A tick that would cut one law's path more than a stated maximum number
of times SHALL be refused naming the relation, the driven coordinate,
the primitive and the count, and SHALL commit nothing — the bank, the
tick count and the bound tree standing as before and the commands that
moved an input in it retired reporting `refused` — exactly as a
conflict does. A `%` whose divisor is zero anywhere the tick evaluates
SHALL be refused the same way.

#### Scenario: A periodic window advances once per revolution

- **WHEN** a running root states
  `crank.drives(pinion.turn, law=periodic_window)` carrying
  `4 + 72 * clamp01((angle − 360 * floor(angle / 360) − 113.5) / 11.25)`,
  the crank rests at `100`, `dt` is `1/240`, and the simulation moves
  `crank` by `360` over one second, twice
- **THEN** `pinion.turn` reads `4` before the first move, `76` after it
  and `148` after the second, and the tick in which the crank passes
  `360` contributes exactly zero

#### Scenario: A tick that passes three windows adds three throws

- **WHEN** the same root is given `move('crank', by=1080, duration=0)`
  from a crank of `100`
- **THEN** `pinion.turn` reads `220`, three crossings are located inside
  that one tick, and the crank stands at `1180`

#### Scenario: A gate holds open and re-engages without a jump

- **WHEN** a running root states
  `(shaft.turn & sleeve.travel).drives(wheel.turn, law=clutch)` carrying
  `-2 * shaft * (sleeve > 0.5)`, and the shaft turns by `4` over a tick
  in which the sleeve stands at `0`, then over a tick in which it
  stands at `1`, then over a tick in which it travels from `0` to `1`
- **THEN** `wheel.turn` moves by `0`, then by `-8`, then by `-4` — the
  travel after engagement only — and never by the value the gate factor
  would have jumped to

#### Scenario: A wrapped law integrates to the unwrapped travel

- **WHEN** a running root's law is `2 * wrap(angle, 360)` and the crank
  travels `500` degrees from `100`
- **THEN** the driven coordinate gains exactly `1000`, and the two
  `ceil` crossings inside that travel contribute nothing of their own

#### Scenario: A remainder window and a floor window agree

- **WHEN** two running roots carry the same tooth window, one written
  with `angle − 360 * floor(angle / 360)` and one with `angle % 360`,
  and both cranks are moved through one revolution from `100`
- **THEN** both driven coordinates read the same value at every tick

#### Scenario: A sign that does not jump integrates as its continuous twin

- **WHEN** a running root's law is `5 * (x − 50) * sign(x − 50)` and a
  second root's is `5 * abs(x − 50)`, and both are driven across `50`
- **THEN** both driven coordinates read the same value at every tick,
  the crossing of `sign` having been located and contributed nothing

#### Scenario: A jump nested in another jump's argument

- **WHEN** a running root's law engages only on alternate revolutions,
  `72 * clamp01((angle − 360 * w − 113.5) / 11.25) * (1 − (w − 2 * floor(w / 2)))`
  with `w = floor(angle / 360)`, and the crank is moved through four
  revolutions from `100`
- **THEN** the driven coordinate reads `72` after the first revolution,
  `72` after the second, `144` after the third and `144` after the
  fourth

#### Scenario: The same movement split differently gives the same answer

- **WHEN** one running simulation takes a revolution of the crank in a
  single tick, another in twelve, and another in two hundred and forty
- **THEN** all three leave the driven coordinate at the same value

#### Scenario: A tick that would cross too many surfaces is refused

- **WHEN** a periodic law is driven far enough in one tick to cross more
  surfaces than the stated maximum
- **THEN** the tick is refused naming the relation, the coordinate, the
  primitive and the count; the bank, the tick count and the tree are
  unchanged; and the move's handle reports `refused`



## ADDED Requirements

### Requirement: A law may read the coordinate it drives

Under a running root a relation whose source group names its own DRIVEN
end SHALL be integrated so that the law reads, on each piece of the tick,
the value that coordinate HELD at the piece's start — its RETAINED value
— and never a value the same piece is computing.

Such a relation SHALL drive exactly ONE coordinate. A relation whose
driven end is a GROUP and whose source group names any member of that
group SHALL be REFUSED at class definition, naming the relation and the
coordinate, and saying that a relation reading its own driven end drives
one coordinate — whether the member reads ITSELF or a SIBLING driven end.

**The read SHALL be a SWITCH.** The system SHALL REFUSE, at construction
and by relation identity — naming the relation as written and the class
that stated it — a law whose SKELETON, the expression with every jump
node replaced by its branch, still names the driven coordinate it reads.
A read that survives the skeleton enters the law continuously, which
makes the relation a differential equation that the difference of two
evaluations does not define. The message SHALL say that a read must pass
through a node that is piecewise constant in it — `floor`, `ceil`,
`sign` or a comparison — and that a remainder alone is not one, because
a fixed quotient leaves `a − q·b`, which still carries the coordinate's
slope.

The system SHALL likewise REFUSE, at construction and by relation
identity, a relation reading a driven end the run does not BANK — a
plain port or a derived coordinate — saying that a retained value is a
history and only a coordinate the run owns keeps one.

**Over one tick such a law SHALL be integrated PIECE BY PIECE.** A jump
node DEPENDS on the driven coordinate when that coordinate is among the
free names of the node's argument subtree. The tick's path SHALL first
be partitioned by the jump nodes that do NOT depend on it, exactly as any
other law's path is, their branches read at that partition's midpoints;
INSIDE each of its pieces the dependent nodes SHALL then be walked:

- At the walk's left end the driven coordinate holds a known value: the
  tick's committed value at the start, and the value the cuts already
  taken placed it at afterwards.
- Every dependent node's branch SHALL be determined in the graph's
  postorder, with the driven coordinate at that retained value and every
  OTHER source at the piece's LEFT END — not at its midpoint, because a
  level quantity naming both the driven coordinate and a source may cross
  inside the piece by the source's motion alone, and the branch read past
  that crossing is not the branch the piece begins under.
- A dependent node whose level sits EXACTLY on a surface at that left end
  SHALL take the branch its operator gives; if the level then LEAVES the
  surface into the other branch's region, that node SHALL be flipped to
  the other branch at the left end and every branch decided again. If the
  flipped branch carries the level back across as well, the tick SHALL be
  REFUSED naming the relation, the coordinate and the primitive, and
  SHALL commit nothing.
- With those branches fixed the substituted law SHALL be continuous on
  the piece and SHALL NOT name the driven coordinate, so that
  coordinate's own value along the piece is one ordinary evaluation.
- Each dependent node's level quantity SHALL be followed along the piece
  — through the driven coordinate's own path and through the sources —
  and the piece SHALL be CUT at the FIRST surface any of them reaches
  strictly inside it: SOLVED exactly where that level is affine along the
  path, otherwise sampled at the same fixed number of sub-intervals and
  bisected to the same tolerance a jump search already uses. No further
  tolerance SHALL be introduced, and a crossing found within that
  tolerance of the piece's left end SHALL NOT be merged into it.
- The piece's contribution SHALL be the substituted law's change over it,
  and the next piece SHALL be decided the same way.

A tick whose path is cut more times than the stated maximum SHALL be
refused exactly as any other over-crossed tick is.

**After a cut the driven coordinate SHALL be committed AT THE FAR SIDE OF
THE SURFACE, at the nearest representable value.** Where the piece moved
it, the coordinate SHALL be placed at the representable value NEAREST the
surface among those at which the crossing node's level — evaluated with
the driven coordinate at that value and every other source at the
crossing's own fraction — reads the branch on the side the level was
moving TOWARD. That value SHALL be what the next piece starts from, and a
tick in which at least one cut placed the coordinate SHALL COMMIT the
value the walk left it at — the last landing and whatever the pieces
after it contributed — rather than its starting value plus the
increment, exactly as a stopped coordinate is committed at its bound. Where the piece did NOT move the coordinate, it SHALL stand where
it stood. A coordinate held at a gate SHALL therefore read the same
branch on every later tick, whatever its sources do, and SHALL survive a
snapshot and a restore bit for bit.

A model SHALL state a gate whose DISENGAGED state has WIDTH — the
mechanism's own clearance — because a gate whose disengaged state is a
single value of the coordinate reads engaged on one side of it and cannot
hold when the coordinate arrives from that side. The width is the
model's to state and the system SHALL NOT require any particular one: a
band of any positive width holds from both directions.

**A self-read crossing is NOT a stop.** It SHALL stop no input, retire
no command and appear in the crossing record rather than the stop
record. A declared range on the driven coordinate SHALL stop it exactly
as it stops any other, located over this same partition, and SHALL be
committed at its bound even where a cut of the same segment placed it
elsewhere.

**At rest such a relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance it by nothing: the relation moves its coordinate only
through a tick.

#### Scenario: A wheel clears to its gap and the ring runs on

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=missing_tooth)`, whose gate
  is disengaged over a band of half-width `g` about every multiple of
  `360`, the wheel rests at `108`, and `move('ring', by=500, duration=1)`
  is run at `dt = 0.1`
- **THEN** the tick sequence commits with `ring` at `500` and its handle
  `completed`, `wheel.turn` at the band's lower edge — within `g` of
  `360`, at the nearest representable value on the disengaged side — and
  the crossing at which the wheel reached its gap recorded in
  `sim.crossings` and not in `sim.stops`

#### Scenario: Sweeping an already-cleared wheel moves it by nothing

- **WHEN** the same root is swept a second time by another
  `move('ring', by=500, duration=1)`, and a third
- **THEN** `ring` reads `1500`, `wheel.turn` holds the SAME float it
  landed on, bit for bit, after each of them, and every handle reports
  `completed`

#### Scenario: Swept backward, a digit clears to zero the short way

- **WHEN** the wheel rests at `108` and the ring is swept BACKWARD far
  enough to carry it past zero
- **THEN** the wheel ends at the band's UPPER edge — within `g` above
  `0`, at the nearest representable value on the disengaged side — having
  turned three teeth and no more, and it does not move on a further
  backward sweep

#### Scenario: Every digit clears and no digit overruns

- **WHEN** the same root is constructed ten times, its wheel resting at
  each of `0, 36, 72, … 324`, and each is given a sweep long enough to
  reach the gap
- **THEN** each wheel ends within `g` of the next multiple of `360` in
  the sweep's direction — the one it already stood on for the wheel that
  rested at `0`, which does not move at all

#### Scenario: A wheel standing exactly on a band edge is not driven through it

- **WHEN** a wheel is placed exactly at the value its own gate's surface
  sits on — the float a previous sweep landed it at — and the ring is
  swept, first in the direction that carries the level INTO the gate's
  engaged region and then in the direction that carries it away
- **THEN** it holds in the direction that would take it deeper into the
  band, turns in the direction that leaves it, and in neither case is it
  carried through the band by a piece integrated under the wrong branch

#### Scenario: A partial sweep is retained and resumes

- **WHEN** the wheel rests at `108`, `move('ring', by=120, duration=1)`
  completes, the caller then reads `sim.state`, renders the tree, takes a
  snapshot and restores it, and only then requests another
  `move('ring', by=380, duration=1)`
- **THEN** the wheel stands at `228` after the first move and unchanged
  through every inspection, and at the band's edge after the second — no
  starting register having been supplied by the caller

#### Scenario: The same sweep at three cadences agrees

- **WHEN** one running simulation takes the whole sweep in a single
  tick, another in twelve and another in two hundred and forty, and a
  fourth takes it as four partial commands with the ring released
  between them
- **THEN** all four leave the wheel and the ring at the same values
  within the run's agreement window, no tick records a stop, no command
  is retired `blocked`, and the total travel admitted is the same

#### Scenario: A continuous read is refused

- **WHEN** a running root states
  `(ring & wheel.turn).drives(wheel.turn, law=...)` whose law is
  `ring * wheel`, or `ring * (wheel % 360)`
- **THEN** construction is refused naming the relation and the class that
  stated it, and saying the read must pass through a node that is
  piecewise constant in it and that a remainder alone is not one

#### Scenario: A self-read of a coordinate the run does not bank is refused

- **WHEN** a running root states a self-read relation whose driven end is
  a plain port rather than a joint coordinate
- **THEN** construction is refused naming the relation and the port, and
  saying that a retained value is a history and only a coordinate the run
  owns keeps one

#### Scenario: A driven group with a self-read is refused

- **WHEN** a class states
  `(crank & lever.swing & pawl.turn).drives((lever.swing, pawl.turn), law=...)`
- **THEN** class definition is refused naming the relation and the
  coordinate read, and saying that a relation reading its own driven end
  drives one coordinate

#### Scenario: Several wheels clear independently from one ring

- **WHEN** a running root drives four wheels resting at `0`, `108`, `252`
  and `324` from one `ring` input, each by its own self-read relation
  whose rack term opens over that wheel's own station, and the ring is
  swept through the first three stations only
- **THEN** the first wheel does not move, the second and third each end
  at their band's edge, the fourth is untouched, and the ring's handle
  reports `completed` with its whole travel admitted

#### Scenario: A declared range on the ring still blocks

- **WHEN** the ring's own coordinate declares `range=(None, 400)` and a
  sweep of `500` is requested
- **THEN** the ring stops at exactly `400`, its command retires
  `blocked`, `sim.stops` names the ring's coordinate, and the wheels
  cleared only as far as the admitted sweep carried their racks

#### Scenario: Reversal inside the gap moves nothing

- **WHEN** a wheel standing INSIDE its band is swept backwards and then
  forwards again
- **THEN** it does not move in either direction, both handles report
  `completed`, and no stop is recorded

#### Scenario: Reversal while engaged backs the wheel up

- **WHEN** a sweep carries a wheel from `108` part way toward its gap and
  the ring is then swept back the same distance
- **THEN** the wheel returns to `108` within the run's agreement window,
  the two increments having been the same law read in both directions

#### Scenario: A stop and a self-read crossing in one tick

- **WHEN** one tick would carry a wheel through its gap at one fraction
  and take an unrelated ranged coordinate past its bound at another
- **THEN** the ranged coordinate stops at its bound exactly, the wheel
  holds at its gap, the crossing is recorded at its fraction OF THE TICK
  rather than of the segment, and `sim.stops` names only the ranged
  coordinate

#### Scenario: A self-read law's identity names what it reads

- **WHEN** two running roots differ only in whether their law reads the
  driven coordinate
- **THEN** the program's described listing differs, their identities
  differ, and a snapshot of one is refused by the other

#### Scenario: A tick that fails after a self-read cut commits nothing

- **WHEN** a segment after a self-read cut meets a conflict
- **THEN** the bank, the tick count and the tree stand as before the
  whole tick, no crossing is recorded, the coordinate is NOT left at the
  value the cut placed it at, and the commands that moved retire
  `refused`
