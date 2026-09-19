## ADDED Requirements

### Requirement: A selection decides which sources a law reads

A mechanism's dependencies may be SELECTED by where one of its own parts
stands, so that the union of what it reads over every selection is
cyclic although each selection's own dependencies are not — the same
fixed carry lever of a Curta is tripped by the dial the carriage has
brought under it and advances the dial beyond that one.

Under a running root the system SHALL admit such a union and SHALL order
it once per PIECE of a tick rather than once per program.

**A BLOCK is a nontrivial strongly connected component** of the
dependency graph the requirement "A relation's law is compiled to an
expression over coordinate ids" defines. Every coordinate a block's edges
read SHALL therefore be one the block itself determines, or one
determined UPSTREAM of it, or an input, or a coordinate that holds.

**A SELECTOR is a jump node of a block member's law whose LEVEL QUANTITY
reads no coordinate the block determines** — a placeholder standing in
that level being resolved into the jump node it replaced, transitively.
A jump node whose level reads a coordinate the block determines,
including the member's own driven end, SHALL NOT be a selector.

**FOLDING a law means setting jump placeholders to ZERO in the member's
SKELETON and simplifying**: a product or a quotient with a zero numerator
being zero, a sum or a difference with a zero operand being the other
operand (negated where it is subtracted). What the member READS under a
fold SHALL be the folded skeleton's free names, with every surviving
placeholder followed into its own folded level quantity, transitively.

**A placeholder SHALL be foldable to zero only where its primitive holds
the ZERO branch over an INTERVAL of its level quantity** — `floor` over
`[0, 1)`, `ceil` over `(-1, 0]`, a remainder's quotient over `(-1, 1)`,
a comparison over the whole of its false side. `sign` reads zero at a
single POINT of its level and SHALL NOT be foldable: a source it gates
is active on every piece of positive width, so treating it as removable
would admit at construction a machine every tick refuses.

**A member's UNCONDITIONAL dependencies SHALL be the coordinates the
block determines that it still reads with EVERY foldable selector of that
member at zero AT ONCE**, and a source it reads with nothing folded but
not under that one fold SHALL be SWITCHED. One fold SHALL decide both:
folding a further placeholder can only remove names and never add one, so
the reads under that single fold are the fewest any selection can leave.

Folding at compile time and reading a branch at run time are DIFFERENT
operations and SHALL NOT be conflated: over a piece the system substitutes
the branch values actually read, whatever they are, and keeps whatever
survives.

The system SHALL REFUSE, at construction and by relation identity —
naming the relations as written and the classes that stated them:

- a block containing a WIRING or a DERIVED COORDINATE, saying that
  neither carries a jump node and neither can therefore be switched;
- a block whose members' UNCONDITIONAL dependencies still form a cycle,
  under the refusal the compile requirement states — a cycle present on
  every piece is a cycle the run cannot order;
- a block one of whose driven ends the run does not BANK — a plain port
  or a derived coordinate — saying that a block advances its coordinates
  piece by piece and only a coordinate the run owns keeps that history,
  and to state the relation into the joint coordinate so the port follows
  it;
- a block member whose driven end is a GROUP, saying that a member of a
  block drives ONE coordinate.

**Over a stretch of a tick the block's SELECTORS SHALL be located
first.** Every selector's level SHALL be followed along the path its
coordinates take over the stretch — the same linear path every other
source takes — and the stretch SHALL be CUT at every surface any of them
reaches: solved exactly where that level is affine, otherwise sampled at
the same fixed number of sub-intervals and bisected to the same tolerance
a jump crossing already uses. Two cuts within that tolerance SHALL be
ONE, a tick cut more times than the stated maximum SHALL be refused
exactly as any other over-crossed tick is, and no further tolerance SHALL
be introduced.

**On each piece the block SHALL be ORDERED and then RUN.** Every
selector's branch SHALL be read at the piece's MIDPOINT; what each member
reads with THOSE branch values substituted — not the compile's zero ones
— SHALL give the piece's ACTIVE dependencies; and the members SHALL be
ordered topologically over them.
A piece whose active dependencies are STILL CYCLIC SHALL REFUSE the tick,
naming the piece, the selector branches it was read under and the
relations on the cycle, and SHALL COMMIT NOTHING: the bank, the tick
count, the tree and the records SHALL stand as they were and the commands
that moved an input SHALL be retired refused, exactly as for a conflict.

**On a piece a selector SHALL be a CONSTANT for every member of the
block**: the branch read at the midpoint SHALL be substituted into the
member's own integration rather than re-located by it, so the order the
block chose and the branch the member reads cannot disagree. Each member
SHALL otherwise be integrated over the piece by the rules that already
govern it — the jump partition, and the walk of a law that reads the
coordinate it drives — with a coordinate the block determines taken at
the value the block has advanced it to and moving by the increment
computed for it on THAT piece, and every other coordinate taken along the
stretch's own path restricted to the piece.

The block's contribution to each of its coordinates SHALL be the sum over
the pieces. Where ANY piece's integration LANDED a coordinate at an
absolute value, the block SHALL report for that coordinate the ABSOLUTE
value it has itself advanced it to by the END of the stretch — that
landing, and every increment the later pieces gave it — and the run SHALL
commit that value exactly where it commits a landing of a law that reads
the coordinate it drives. A coordinate no piece landed SHALL be reported
as an increment only, and committed as its value plus that increment. A
landing followed by further motion SHALL therefore commit the motion:
reporting the landing alone would discard it. Every crossing a piece
reports SHALL be recorded at its fraction of the whole tick, and a
selector's own crossings SHALL be recorded as the crossings of the member
whose law states them.

A source a piece's fold switched OUT, and which the piece's order has not
yet determined, SHALL be given to the member that reads it at the value
the block has advanced it to at the piece's START, moving by nothing.

**A selector crossing is NOT a stop.** It SHALL stop no input, retire no
command, and appear in the crossing record rather than the stop record. A
DECLARED RANGE on a coordinate a block determines SHALL stop it exactly
as it stops any other, located through the block, and SHALL be committed
at its bound even where a piece of the same segment landed it elsewhere.
An input that reaches a stopped coordinate only through a selection that
is INACTIVE over the stretch SHALL NOT be stopped by it.

**At rest a block relation SHALL bind nothing.** It SHALL be recorded
solved FORWARD, its law unapplied, so the rest render poses the tree from
the author's own rest default and the run refuses by name when there is
none. Binding the whole bank again, rendering, or inspecting the tree
SHALL advance a block's coordinates by nothing.

**Membership SHALL be decided BEFORE the rest render**, over the
relations, wirings and derived coordinates of the linked tree, each read
in the direction it is DECLARED. Every relation on a dependency cycle
that determines at least one coordinate the run BANKS SHALL be so
decided, whether it names one coordinate at each end or several, so that
every such cycle reaches the compile and is answered there by name rather
than by the rest render's own refusals. A cycle that determines NO banked
coordinate SHALL be left alone and SHALL behave exactly as it does
without this requirement.

Deciding membership again over the same tree SHALL give the same answer,
and a simulation constructed over a tree a previous simulation owned
SHALL decide it afresh, so a tree posed by one run and handed to another
carries nothing of the first.

Under a root that does NOT declare `Time.running()` nothing SHALL change:
the same relations SHALL be solved, deferred and refused by the ordinary
enumeration exactly as they are without this requirement.

**A SELECTION CHANGE ALONE SHALL MOVE NOTHING.** A selector is a jump
node, and a jump never moves a part: with its sources otherwise still, a
tick in which a selection changes SHALL commit every coordinate of the
block unchanged.

A command taken in one tick, and the same command taken in many, SHALL
agree within the run's own agreement window for every coordinate and for
the travel each command admits, and EXACTLY for every command's STATUS
and for every discrete reading of a coordinate — a gate set or not, a
digit — taken where no committed value stands within that window of a
surface, a bound or a gate threshold. The travel a command admits is
accumulated once per tick and SHALL NOT be required to agree bit for bit
across two partitions of one command.

The program's IDENTITY SHALL distinguish a program carrying a block from
one that does not, and SHALL distinguish two programs whose blocks hold
different members. A block's members SHALL be listed in an order
deterministic for a given tree, and the program's listing SHALL name the
block at its position in the program's order and then carry each of its
members' own entries, so the identity covers every member's ends,
direction and expression as it does any other edge's.

#### Scenario: A carriage selects which wheel a lever reads

- **WHEN** a running root states a lever driven by `lower.turn` gated by
  `shift < .5` and by `higher.turn` gated by `shift >= .5`, and a
  `higher.turn` driven by the crank gated by `shift >= .5` and by the
  lever gated by `shift < .5` — a union the compiler cannot order — with
  a rest default on every driven coordinate
- **THEN** construction succeeds, the program carries ONE block holding
  those two relations, and its listing names the block

#### Scenario: The carry happens at one position and not the other

- **WHEN** that root is cranked with `shift` at `0`, and again with
  `shift` at `1`
- **THEN** at `0` the lower wheel drives the lever and the lever advances
  the higher wheel, at `1` the higher wheel drives the lever and the
  higher wheel is driven by the crank directly, and each result equals
  the one the SAME laws give with `shift` frozen at that value and
  compiled as an ordinary acyclic program

#### Scenario: A selection change inside a tick moves nothing

- **WHEN** `shift` is moved from `0` to `1` in one tick, crossing both
  selectors, with every other input standing still
- **THEN** every coordinate of the block commits the float it held, the
  selector crossings are recorded in `sim.crossings`, and no stop is
  recorded

#### Scenario: A shift away and back preserves every part's state

- **WHEN** the crank is turned until the lever is set, the carriage is
  shifted to another position, the crank is turned again, and the
  carriage is shifted back
- **THEN** the lever still stands where the mechanism left it, each wheel
  holds the angle its own motion gave it, and nothing was reset by the
  shifts

#### Scenario: A finer partition agrees with a coarser one

- **WHEN** the same crank travel is requested as one tick, as twelve, and
  as two hundred and forty, each from the same restored snapshot, with
  every gate threshold and declared bound chosen away from where a tick
  ends
- **THEN** every coordinate agrees within the run's agreement window,
  every command's admitted travel agrees within that same window, and
  every command reports the same status

#### Scenario: A landing in one piece and motion in a later one commit both

- **WHEN** one tick carries a selector crossing, a coordinate the block
  drives is landed at a gate in the piece BEFORE that crossing, and the
  selection the crossing brings in drives that same coordinate further in
  the piece after it
- **THEN** the bank commits the absolute value the block advanced it to
  over the whole stretch — the landing plus the later piece's increment —
  and not the landing alone

#### Scenario: A switched-out source is handed no motion

- **WHEN** a piece's selection switches an in-block source out of a
  member's law, and the same tick is run again with that source given a
  different increment
- **THEN** the member's contribution on that piece is the same float in
  both runs

#### Scenario: A cycle with no self-read and no selection is refused by the compile

- **WHEN** a running root states an UNCONDITIONAL cycle of multi-source
  relations, none of which gates a source behind a jump node and none of
  which reads the coordinate it drives, each driven coordinate carrying
  its own guarded rest default
- **THEN** construction is refused naming the relations on the cycle and
  the coordinates they wait on — the compile's own refusal, rather than
  the rest render's refusal of a doubly bound coordinate

#### Scenario: A selected cycle with no self-read is admitted

- **WHEN** the same cycle gates each in-block source behind a comparison
  on a coordinate it does not determine, still with no relation reading
  the coordinate it drives
- **THEN** construction succeeds, the program carries one block holding
  those relations, and each driven coordinate's rest value is its own
  guarded default

#### Scenario: A cycle no selection breaks is refused at construction

- **WHEN** a running root states the same two relations with their
  selections removed, so each reads the other's coordinate
  unconditionally
- **THEN** construction is refused naming both relations and the
  coordinates they wait on

#### Scenario: A plain port among a block's driven ends is refused

- **WHEN** one of the two relations drives a plain port that a wiring
  carries into a joint coordinate, rather than the joint coordinate
  itself
- **THEN** construction is refused naming the relation and the port, and
  saying that only a coordinate the run owns keeps a block's history

#### Scenario: A piece that cannot be ordered refuses the tick

- **WHEN** a running root's two selections are written so that some
  reachable value of the selecting input leaves both dependencies active
  at once, and the input is moved to that value
- **THEN** the tick is refused naming the selector branches and the
  relations on the cycle, `sim.state` is the bank the previous tick
  committed, the tick count did not advance, and the commands that moved
  an input report `refused`

#### Scenario: An inactive association does not block an input

- **WHEN** a wheel the block drives declares a range, stands at its
  bound, and an input that reaches it ONLY through a currently inactive
  selection is moved
- **THEN** that input's command is not retired `blocked`, it admits its
  whole travel, and the stopped wheel does not move

#### Scenario: A range on a block coordinate stops it and wins over a landing

- **WHEN** a coordinate the block drives declares a range and one tick
  both lands it at a gate and carries it past that range
- **THEN** it is committed AT its bound, the stop is recorded naming the
  inputs that pushed it, and the landing does not overwrite the bound

#### Scenario: A block member that reads its own coordinate walks inside each piece

- **WHEN** one of the block's relations also reads the coordinate it
  drives through a switch — a latch set by a pin and reset by a cam — and
  one tick carries both a selector crossing and a crossing of that
  latch's own gate
- **THEN** both crossings are recorded at their own fractions of the
  tick, the latch is committed at the value its walk left it at, and the
  tick's result equals the one the same tick gives with the selection
  frozen at each of its two branches over the corresponding parts of the
  travel

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
may read the coordinate it drives", and a relation the system has
recognized as a member of a BLOCK, which binds NOTHING at rest under the
requirement "A selection decides which sources a law reads" — and read
every joint coordinate off the tree. A joint coordinate that rest render leaves unbound SHALL be
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

#### Scenario: A rest default under a block relation is the bank's value

- **WHEN** a running root states two relations whose union is cyclic and
  whose selections are mutually exclusive comparisons on a live input,
  and each driven coordinate's own `simulate()` binds a value under
  `if ... is None`
- **THEN** construction succeeds, the initial bank reads each of those
  rest values, neither relation bound anything at rest, and nothing is
  refused as doubly bound

#### Scenario: A block relation with no rest default is refused

- **WHEN** the same root's driven coordinates declare no rest default, so
  the rest render leaves them unbound
- **THEN** construction is refused naming a qualified id and saying the
  run needs a rest value for every joint coordinate

### Requirement: A relation's law is compiled to an expression over coordinate ids

At construction under a running root the system SHALL COMPILE the
relations the rest render solved into a program over the bank: each
relation's law SHALL be applied ONCE to a symbolic token per source
coordinate, in the direction the rest render solved it, and the
expression graph that application builds — over the qualified ids of
the sources — SHALL be what the run evaluates on every tick and what
the refusals below inspect. A graph containing a DISCONTINUOUS
primitive — a call to `floor`, `ceil` or `sign`, the `%` operator, or a
comparison — SHALL additionally be compiled into a JUMP PLAN: its jump
nodes in the graph's postorder, each with the level quantity whose
surfaces it crosses, the graph of that level quantity with the jump
nodes inside it replaced by branch placeholders, whether that level
quantity is AFFINE in the sources, and the SKELETON of the whole
expression with every jump node so replaced. A wiring into a bank
coordinate SHALL be an
identity edge and a derived coordinate a linear edge.

The compiled edges SHALL be ORDERED so that every edge's sources are
determined before it runs: over the DEPENDENCY GRAPH in which edge A
precedes edge B when B reads a coordinate A determines — a coordinate an
edge itself determines EXCLUDED, because that is a read of what the
coordinate holds — the edges SHALL be ordered topologically, with each
nontrivial STRONGLY CONNECTED COMPONENT of that graph contracted to ONE
entry, a BLOCK, under the requirement "A selection decides which sources
a law reads". A coordinate no edge determines SHALL be resolved from the
start: it is an input, or it HOLDS. A relation or
wiring none of whose driven ends is, or reaches through such
intermediates, a bank coordinate SHALL be left to the ordinary
enumeration, and SHALL leave nothing of itself in the program: the
program's COORDINATES SHALL be the bank's, plus exactly the ends its
compiled edges read and give. An end of a relation left to the ordinary
enumeration SHALL NOT be a coordinate of the program, SHALL NOT be
published as one, and SHALL NOT be a reason to refuse the program — the
run never computes it, and the ordinary enumeration recomputes it from
the bank on every tick exactly as it does under no time base at all.
The program SHALL have an IDENTITY derived from the root
class, the bank's ids, the inputs' declarations and every edge's ends,
direction and expression.

The system SHALL refuse, at construction and by relation identity —
naming the relation as written and the class that stated it:

- a law that cannot be applied to symbols — one that raises when handed
  a symbolic token, returns something that is neither a number nor an
  expression, or whose expression holds text the framework cannot
  evaluate or a call outside the symbolic vocabulary — saying that a
  running law is an expression over its sources;
- a relation or wiring INTO a bank coordinate whose source is a
  coordinate the run does not own and no compiled edge computes — a
  plain port the author's `simulate()` binds — saying to state that
  value as a relation or a joint;
- a relation naming several driven ends of which some are bank
  coordinates and some are not;
- a set of relations whose dependencies form a CYCLE that no selection
  breaks — naming every relation on the cycle and the coordinates they
  wait on, saying that a running program is ordered before it runs, and
  saying what a switch would be, in the terms the requirement "A
  selection decides which sources a law reads" defines: a source that
  folding a jump node to zero removes from the law, where that node's
  level reads no coordinate the cycle determines and its zero branch is
  one the node holds over an interval of that level — so a `sign` is not
  one;
- a law whose expression contains a DISCONTINUOUS primitive and none of
  whose driven ends is a coordinate the run owns — a plain port or a
  derived coordinate the ordinary enumeration recomputes from the bank
  on every tick — saying that a subtracted jump implies a history,
  that only a coordinate the run owns keeps one, and that the relation
  should be stated into the joint coordinate so the port follows it.

A law whose expression has no free coordinate — a constant — SHALL
compile and contribute a zero increment; a law that can move its
coordinate only by jumping SHALL be refused under the requirement "A
law that can only jump is refused as arithmetic".

#### Scenario: A running root with a floor in a law compiles

- **WHEN** a running root states `crank.drives(first.turn, law=window)`
  where the law's expression contains `floor(angle / 360)`
- **THEN** construction succeeds, the compiled graph names the source's
  qualified id, its jump plan holds one `floor` node whose level
  quantity is that qualified id divided by 360 and is AFFINE in the
  sources, and the same root without `Time.running()` poses exactly as
  before

#### Scenario: A jumping law into a plain port is refused

- **WHEN** a running root states `crank.drives(register, law=window)`
  where `register` is a plain port wired to a joint coordinate and the
  law's expression contains `floor`
- **THEN** construction is refused naming the relation and the port, and
  saying to state the relation into the joint coordinate the run owns;
  and the same relation stated into that joint coordinate compiles

#### Scenario: A law over stdlib math is refused as non-symbolic

- **WHEN** a running root's law computes `math.sin(angle)` from Python's
  standard library
- **THEN** construction is refused naming the relation and saying the law
  cannot be applied to symbols

#### Scenario: A relation sourced from an author-bound port is refused

- **WHEN** a running root's `simulate()` binds a plain port from its
  crank and a relation drives a joint from that port
- **THEN** construction is refused naming the relation and the port, and
  advising a relation or a joint

#### Scenario: A law with a kink compiles

- **WHEN** a running root's law is `4 + 72 * clamp01((angle − 113.5) / 11.25)`
- **THEN** construction succeeds and the compiled expression names the
  source's qualified id and only `min` and `max` among calls

#### Scenario: A relation the enumeration keeps leaves no coordinate in the program

- **WHEN** a running root drives the `height` port of its `.repeat()`
  children, and no relation carries those ports back to a joint
  coordinate
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates only, no copy's port is among them, the program's
  edges are unchanged, and the run poses every copy exactly as the same
  root without `Time.running()` does

#### Scenario: A part this render omits leaves no coordinate in the program

- **WHEN** a running root holds an optional part whose joint one of its
  drivers drives, and this render `omit()`s that part
- **THEN** the compiled program's coordinates are the driver and the
  joint coordinates of the parts that ARE in the machine, the omitted
  part's coordinate is not among them, and construction succeeds

#### Scenario: Two relations waiting on each other are refused

- **WHEN** a running root states `(a & b.turn).drives(c.turn, law=...)`
  and `(a & c.turn).drives(b.turn, law=...)`, neither law gating the
  other's coordinate behind a jump node
- **THEN** construction is refused naming BOTH relations and saying they
  form a cycle the run cannot order

#### Scenario: A wiring on a cycle is refused by name

- **WHEN** a running root states a cycle one of whose steps is a wiring
  or a derived coordinate rather than a law
- **THEN** construction is refused naming that wiring or derived
  coordinate and saying it carries no jump node and therefore no
  selection
