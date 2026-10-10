## MODIFIED Requirements

### Requirement: A relation may name several coordinates at each end

A mechanism may read several coordinates and move several. The system
SHALL let ONE relation name several coordinates as its source, several
as its driven end, or both, and SHALL hand the whole of it to the
project's own law, which reads all the sources and returns all the
driven values in one call.

The system SHALL apply such a relation in ONE DIRECTION only: it SHALL
be applied when every source end is bound, binding every driven end
together, and SHALL NEVER be read backwards, whatever inverse its law
offers — for the reason a broadcast is never read backwards, that
recovering the sources from the driven values would mean comparing or
solving values, which the framework does not do. Asked to, the system
SHALL refuse by name.

A relation naming several coordinates at either end SHALL resolve to ONE
RECORD holding all its ends, in the order written — and, where its
driven end is a broadcast, to one such record PER REALIZED COPY, each
holding that copy's driven ends. The driven ends of one record SHALL be
bound by ONE application of one law, and SHALL NOT be bound, refused or
deferred one without the others; the system SHALL claim every one of
them before it binds any.

Such a relation SHALL take part in the solve exactly as any other does:
attempted at the end of its own instance's simulate phase, DEFERRED
while any source is unbound, applied as soon as the whole tree's
propagation binds the last of them, and refused only when nothing
changes any more. Its motion SHALL be the motion of the assembly that
stated it, tagged, swept and cleared with the rest of that assembly's
motion.

Values SHALL pass through it unresolved, exactly as through any other
relation: a law over several symbolic sources publishes several
expressions, one per driven end, and the operations they lower to are
those the same bindings written by hand would produce.

A coordinate named BOTH as a source and as a driven end of ONE such
relation SHALL be a READ of that driven end: the law SHALL be handed its
owner exactly as it is handed any source's owner, in the position the
source group writes it, and what the law reads there SHALL be the value
the coordinate HOLDS and never a value that same application is about to
give it. Such a relation SHALL be recognized only where an end names
SEVERAL coordinates, SHALL be applied FORWARD only like any other
relation of several ends, and SHALL be integrated under the simulation
requirement "A law may read the coordinate it drives", which is the only
reading that gives it a meaning.

Such a relation SHALL drive exactly ONE coordinate. A relation whose
driven end is a GROUP and whose source group names any member of that
group SHALL be REFUSED at class definition, naming the relation and the
coordinate, and saying that a relation reading its own driven end drives
one coordinate — whether that member reads ITSELF or a SIBLING driven end
of the same group. Where the driven end is a BROADCAST the relation still
drives one coordinate per copy, and the source group's repeated member —
the same broadcast — SHALL resolve per copy exactly as the driven end
does, so each copy reads ITSELF and each copy is its own record. A
coordinate named twice within ONE group SHALL stay refused, and a read of
a coordinate some OTHER relation drives SHALL stay the ordinary source it
has always been.

Under a root that does NOT declare `Time.running()` such a relation SHALL
be REFUSED by name at the close of the enumeration, naming the relation
and the class that stated it and saying that a relation reading its own
driven end states increments, which only a run integrates — rather than
standing silently inert over a coordinate nothing moves.

A relation naming ONE coordinate at each end whose source IS its driven
end — `wheel.turn.drives(wheel.turn)`, or the same coordinate spelled
two ways: a node standing for its one joint and that joint's path, or a
reused-joint mate's handle and the joint it reuses — is NOT a read of
its driven end, and SHALL be REFUSED at class definition, after the
checks either end already has, naming the relation as written and saying
that its one source is its own driven end, so that it has no other value
to compute the driven one from, and how a law that reads the coordinate
it drives is written instead: with another source beside it, under a
root declaring `Time.running()`.

#### Scenario: A pawl deflects from two drums

- **WHEN** a position states
  `(count & next_count).drives(sautoir.pawl.swing, law=pawl_deflection)`
  and both ports are bound
- **THEN** the law was handed the tuple of the two sources' owners and
  the pawl's node, its `forward` was called with the two values in the
  order written, and the pawl's swing holds the one value it returned

#### Scenario: Three sources and four driven ends on every copy

- **WHEN** a delta printer declaring `rods = Rod().repeat(6)` states
  `(x & y & z).drives((rods.spin, rods.lean, rods.swing, rods.rise), law=delta_rod)`
  and binds its three drivers
- **THEN** each of the six rods holds its own four values, each copy's
  law was called once at realization with that copy, and each rod's body
  is placed by the four bindings exactly as if they had been written by
  hand

#### Scenario: Several sources and one driven end

- **WHEN** the same printer states
  `(x & y & z).drives(towers.height, law=delta_carriage)` over three
  repeated towers
- **THEN** each tower's height holds the value its own law returned, and
  the law returned that value rather than a sequence

#### Scenario: A relation of several ends is not applied while a source is unbound

- **WHEN** a relation of three sources has only two of them bound when
  its own instance's relations are attempted, and nothing else in the
  tree binds the third
- **THEN** nothing was bound by it, and the enumeration refuses naming
  the relation and the unbound source

#### Scenario: The driven ends of one law are bound together

- **WHEN** a relation of four driven ends is applied and one of those
  coordinates was already bound by the author's `simulate()`
- **THEN** the doubly-bound refusal names that coordinate and its two
  binders, and none of the other three was bound

#### Scenario: A coordinate named on both sides is read, not refused

- **WHEN** a class states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` on a root
  declaring `Time.running()`
- **THEN** class definition succeeds, the law is called with the rack's
  owner and the wheel's owner in that order, and the relation's one
  record names `wheel.turn` as both a source and its driven end

#### Scenario: A driven group with a self-read is refused

- **WHEN** a class states
  `(crank & lever.swing & pawl.turn).drives((lever.swing, pawl.turn), law=hysteresis)`
- **THEN** class definition raises naming the relation and the coordinate
  read, and saying that a relation reading its own driven end drives one
  coordinate

#### Scenario: Each copy of a broadcast reads itself

- **WHEN** a class declaring `wheels = Wheel().repeat(6)` states
  `(ring & wheels.turn).drives(wheels.turn, law=missing_tooth)`
- **THEN** class definition succeeds although the source group names a
  broadcast, six records are solved, one per copy, and each copy's law
  read that copy's OWN turn rather than the first copy's

#### Scenario: A coordinate named twice in one group is still refused

- **WHEN** a class states
  `(rack & wheel.turn & wheel.turn).drives(wheel.turn, law=...)`
- **THEN** class definition raises naming the relation and the
  coordinate, because one value would take two positions of the law

#### Scenario: A self-read relation under no running root is refused

- **WHEN** a root declaring no time base, or `Time(loop=4)`, states
  `(rack & wheel.turn).drives(wheel.turn, law=missing_tooth)` and the
  tree is rendered
- **THEN** the enumeration refuses at its close naming the relation and
  the class that stated it, and says that a relation reading its own
  driven end states increments, which only a run integrates, and to
  declare `time = Time.running()`

#### Scenario: A relation whose one source is its own driven end is refused

- **WHEN** a class states `wheel.turn.drives(wheel.turn)`, with or without
  a `law=`; or `turn.drives(turn)` over a port it declares; or
  `wheel.drives(wheel.turn)`, `wheel` declaring that one joint; or
  `mount = body.axle.on(seat, body.turn)` and `mount.drives(body.turn)`
- **THEN** class definition raises, naming the relation as written and
  saying that its one source is its own driven end, and pointing to a
  law that names another source beside it; while `crank.drives(crank)`
  over a `Driver` and `wheels.turn.drives(wheels.turn)` over a repeat
  are still refused by their own end checks, with their own messages
