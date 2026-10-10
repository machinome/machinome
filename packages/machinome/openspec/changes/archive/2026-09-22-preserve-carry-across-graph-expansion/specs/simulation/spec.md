## ADDED Requirements

### Requirement: Source-timed execution is declared in exports and snapshots

Every newly exported running program SHALL use document version 11, including
ordinary, selected, Play and explicit-time programs. Existing fields and
expression syntax SHALL remain unchanged; posed/looping and clocked version
selection SHALL remain unchanged. A consumer supporting only versions through
10 SHALL refuse the corrected export before operation.

The running program's canonical identity SHALL include its source-timing
semantic generation. A snapshot from endpoint-era semantics SHALL refuse
restore before changing the bank, commands or records. This deliberately
supersedes earlier running identity and document-byte preservation promises
for this semantic correction, even for an affine program whose result is
unchanged. Corrected snapshots SHALL remain deterministic and replayable.

#### Scenario: Re-export protects the originating carry

- **WHEN** the unchanged Curta carry is exported by the corrected framework
- **THEN** the document is v11 and an old viewer refuses it rather than
  silently using the endpoint carry arithmetic

#### Scenario: Old arithmetic state is not restored silently

- **WHEN** an endpoint-era running snapshot is restored into the same machine
  compiled with source-timed semantics
- **THEN** the identity mismatch refuses before mutating any live state

#### Scenario: Other motion modes retain their format

- **WHEN** posed, looping and clocked models are exported by the corrected producer
- **THEN** their version selection remains unchanged

## MODIFIED Requirements

### Requirement: A jump is located inside the tick and subtracted

Under a running root a law whose expression contains a DISCONTINUOUS
primitive SHALL contribute, over one tick, the CONTINUOUS part of its
change: the tick's path SHALL be cut at every crossing of every jump
surface it meets, and the law's change SHALL be summed over the pieces
between those cuts, so that no jump ever moves a part.

The PATH of a tick SHALL follow each source's physical motion at the same
fraction `t` in `[0, 1]`: commanded linear motion for an input, constant motion
for a held coordinate, and law-determined motion for a driven source. Driven
sources SHALL retain dwell, kink, crossing and landing timing through ordinary
chains as well as selected blocks, rather than interpolate their net increments.
For a law naming several sources these paths SHALL be read jointly at that
same fraction. A tick in which no source moves SHALL
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
exactly, every surface between the endpoint values included. Where it is
PIECEWISE AFFINE — the requirement "A kink is a cut, and a
piecewise-affine quantity is solved" — the piece SHALL be SUB-DIVIDED at
that level's own kink breakpoints and the crossings SHALL be solved
exactly on each sub-piece, again every surface between that sub-piece's
endpoint values included. Otherwise
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
coordinates take over the stretch — commanded motion for an input and
law-determined motion for a driven source, retaining its timing — and the
stretch SHALL be CUT at every surface any of them
reaches: solved exactly where that level is affine or PIECEWISE AFFINE —
the requirement "A kink is a cut, and a piecewise-affine quantity is
solved" — otherwise sampled at
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
coordinate it drives — with each active determined source following the
motion its law gives it
at the corresponding point of the request, including its dwell, crossings
and landing. This SHALL also hold for determined sources upstream of the
block. Restricting a source to a piece SHALL retain that motion's timing,
not substitute a straight line between the piece's endpoints. Inputs and
held coordinates SHALL retain their commanded and constant paths,
respectively.

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

Adding later stations whose active motion does not influence an earlier
carry SHALL NOT alter that carry's physical outcome. Additional internal
partition boundaries SHALL NOT re-time a source's motion. Existing
agreement windows and the status/discrete-reading rules above SHALL apply.

The source-timing guarantee SHALL apply to ordinary chains as well as
selected blocks: freezing a selection SHALL NOT change the physical timing
of the same laws. Existing exact affine propagation SHALL retain its result;
ordinary endpoint approximations that lose a dwell or landing SHALL be
corrected rather than preserved for compatibility.

#### Scenario: An ordinary frozen carry retains the same timing

- **WHEN** the existing ShiftedCarry at shift 0 and its FixedZero ordinary
  acyclic twin move crank 0..4, with a carry landing at 1 and gate at .5,
  in one move and again in sixteen portions
- **THEN** both versions finish with carry.travel 1 and higher.turn 3.5,
  commands completed with full travel admitted, rather than the old bulk
  result 2 produced by spreading the lever's stroke over the whole request

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

#### Scenario: Later result stations preserve an earlier carry

- **WHEN** Curta's unchanged result-carry diagnostic sets digit to 0,
  height to 9, crank angle to 90 and then requests crank angle 180 in one
  unsplit move, with six, seven and eleven active result stations
- **THEN** every move completes, ones.turn ends at 724, tens.turn ends at
  704 and the first lever ends at 0 within the existing agreement window,
  with the same earlier carry in all three graphs

#### Scenario: A dwelling predecessor is not replaced by a ramp

- **WHEN** a selected carry chain contains a source which moves and then
  dwells or lands, and the same physical request is made with an additional
  station whose selection changes but cannot influence that carry
- **THEN** the earlier successor receives the same timed physical motion
  and produces the same carry whether or not the later station is present

#### Scenario: An upstream driven source retains its timing

- **WHEN** the carry's driving shaft has nonuniform motion during a
  request and the same request is executed whole or in smaller portions
- **THEN** the full bank and admitted travel agree within the existing
  window, with identical statuses and discrete readings away from the
  threshold neighborhoods defined above

#### Scenario: Observing the full result bank does not lose the carry

- **WHEN** the eleven-station Curta result-carry diagnostic makes that same
  unsplit request with its original ones and tens contact constraints
- **THEN** the crank reaches 180 with completed status and tens.turn 704,
  without disabling a constraint, reducing the bank, changing a law, or
  subdividing the pilot's request
