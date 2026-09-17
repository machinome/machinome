## MODIFIED Requirements

### Requirement: A clocked simulation solves a request path event by event

The system SHALL provide `Sim(model)` over a clocked root, constructed with
NO `dt`. A `dt` given over a clocked root SHALL be refused by name, saying a
state moves on requests and not on a cadence; a `dt` omitted over any other
root SHALL remain refused as it is today. `state=` SHALL accept declared
drivers AND declared states by qualified id, bound over the declared defaults
before the first render. Construction SHALL pose the tree once and hold a
BANK of every driver and every state by qualified id; joint coordinates and
ports SHALL NOT be in that bank, being what the
ordinary enumeration computes from it on every pose. `time` SHALL NOT be in
that bank under a clocked root that declares NO time base, because such a
root has no clock and a state moves on requests rather than on one; under a
clocked root declaring `Time.elapsed()` `time` SHALL be a banked value, by
the requirement "An elapsed clocked root banks its clock", and everything
this requirement says of the bank SHALL hold of it.

A clocked tree that declares no time base SHALL be posed exactly as the
build path poses a driven model
outside a simulation: every driver and every state bound to its current
value, and `time` left as the untimed symbolic animation variable through the
fallback an unbound time already takes. A `simulate()` that reads `self.time`
under such a root SHALL therefore read what it reads today under an
untimed one.

`sim.move(input_id, by=travel)` or `sim.move(input_id, to=value)` SHALL take
exactly one of `by`/`to` and SHALL name exactly ONE MOVING INPUT — one
declared driver, in design units, or, under an elapsed root, the clock — and
is a REQUEST: a straight path from the value that input
holds to the requested one, with every other bank value standing. A request
naming a state, a joint coordinate, or more than one input SHALL be refused
by name.

Before any event is located the request's path SHALL be CLIPPED by the
requirement "A bound stops a clocked request on its path": the travel
becomes the travel every declared bound admits, and every rule below
applies to the CLIPPED path. A request whose admitted travel is ZERO SHALL
fire no event, commit nothing and still be admitted.

Along that path the system SHALL locate events EXACTLY, by the tools the
running executor already owns and with no additional locator, tolerance or
knob:

1. Each committing relation's `at` level SHALL be bound at the standing
   sources and classified structurally over the one MOVING INPUT — a declared
   driver, or the clock under an elapsed root. An AFFINE
   level's surfaces SHALL be solved by division; a KINKED level SHALL be cut
   at its own breakpoints and each sub-interval solved the same way; a CURVED
   level SHALL be refused at simulation construction, by name, naming the
   relation, the input whose motion curves it and the primitive, and saying
   a clocked event is solved and never searched.
2. A crossing SHALL fire only when the step is RISING — `at`'s branch after
   the crossing greater than its branch before — the branch before read at
   the midpoint of the piece the path came from, the branch after read AT
   THE LANDING, the nearest representable point of the piece the path
   enters, which is the only reading available when the crossing is the
   request's own endpoint. A falling step SHALL fire nothing. A mechanism that
   commits on the other edge states it by negating its own level. Where the
   crossing is the path's own OPENING — the level standing exactly on a
   surface at the value the request starts from — there is no piece behind
   it, and the branch before SHALL be read AT THE START and the far side
   asked for at the next representable value the path reaches.
3. The earliest rising crossing over all committing relations SHALL be the
   next event. Two crossings SHALL be ONE event exactly when their far-side
   landings are the SAME floating-point value, and SHALL otherwise be two
   events taken in path order, the later reading what the earlier committed.
   NO TOLERANCE SHALL decide that question: a tolerance stated as a fraction
   of the request's travel would make one long request merge events that
   several short requests keep apart.
4. The moving input SHALL take the NEAREST REPRESENTABLE VALUE ON THE FAR
   SIDE of the surface, found by walking the solved value in float space, and
   that one value SHALL be used both for the event's reads and for the
   resumption of the remaining path, so no event can fire twice. Membership
   of a value in the far side SHALL be decided by evaluating the jump node's
   BRANCH at that value, never by comparing it to the surface: a solved value
   at which the branch has already changed IS the landing, a strict
   comparison against a representable threshold lands on the next value
   beyond it, and a non-strict comparison lands on the threshold itself. The
   walk SHALL bracket in a first step sized by the SEGMENT it walks on — the
   larger of the landed value's own magnitude and the magnitudes of the
   path's ends — and never by the magnitude of a value that happens to be
   zero, whose own step is a denormal no segment can express.
5. **A crossing belongs to the request whose path CONTAINS its landing.** A
   landing ON the request's endpoint is that request's, so a request that
   ends exactly on a NON-STRICT surface has reached it. A landing one
   representable value BEYOND the endpoint — which a STRICT comparison
   reached exactly produces — is NOT that request's, and SHALL be fired by
   the NEXT request, which begins on that surface and whose path contains
   the landing. Containment SHALL therefore be judged by the LANDING and not
   by the fraction at which the crossing was solved: a crossing solved at
   fraction ZERO whose far side lies ahead inside the path IS an event, and
   a request resuming from its OWN landing still fires nothing, because
   there the landing IS the value the request starts from.
6. Every relation firing at that event SHALL evaluate its `at` and `law`
   callables at that input value and at the PRE-EVENT value of every state —
   including a state the same relation writes and a state another relation
   writes at the same event — and the targets SHALL take the results
   together. Declaration order SHALL NOT be observable. Two relations firing
   at one event and writing DIFFERENT states is that synchronous case; two
   firing at one event and writing the SAME state is a CONFLICT, and the
   whole REQUEST SHALL be refused, naming the state by its qualified id,
   both relations as written and the landing, and committing nothing.
7. The remaining path SHALL be solved again from the landing with the new
   bank, so an event surface that reads a committed state moves with it. The
   process SHALL repeat until the path is exhausted.

A commit value that is not a FINITE number — an infinity or a NaN — SHALL
refuse the WHOLE request, naming the relation as written, the state by its
qualified id and the value, and SHALL commit nothing: a bank holding such a
value poses nothing, satisfies no bound and carries no later event. The
judgement SHALL be made BEFORE an integer state's rounding, so a
`dtype=int` target SHALL refuse by that message rather than by the
rounding's own overflow. A document cannot express a raise, and the export
requirement "A published commit says what it reads, writes and fires on"
therefore has a CONSUMER that computes a non-finite commit value refuse the
request rather than bank it; the two runtimes refuse the same request.

A request SHALL NOT pose the tree between events: `at` and `law` read only
banked values, and the tree SHALL be bound exactly once, at the end of the
request. A request SHALL be ATOMIC — a refused request SHALL commit nothing
and SHALL leave the bank, the tree and the record exactly as they were. That
atomicity SHALL INCLUDE the final pose: the tree SHALL be posed over the
request's working bank BEFORE that bank becomes the simulation's, and a pose
the tree refuses SHALL leave the bank, the recorded events and the posed
tree exactly as they stood, the refusal being raised to the caller.
`restore()` SHALL behave the same way: a snapshot whose pose is refused
SHALL leave the previous bank and the previous pose standing.

A committing relation NO REQUEST can reach — one whose every source is a
state, so that its event level can never move along any request path —
SHALL be refused at simulation construction, by name, saying that its event
level moves with no declared driver and, under an elapsed root, not with
the clock either. Under an elapsed root a relation whose only moving source
is the CLOCK SHALL be admitted: the clock is something a request moves.

A request SHALL be refused when one committing relation's located events
exceed the crossing maximum the framework already states for one graph — one
thousand. The judgement SHALL be made over the events ACTUALLY LOCATED, one
by one as the path is solved, and never over a count estimated from the
travel and the surface spacing, so a level that stops crossing halfway
through a long request is not refused for a crossing it never makes. The
refusal SHALL name the request — the input and its travel — the relation as
written, the count reached and the maximum, and SHALL say that the request
can be split into shorter ones.

`move` SHALL return a value object naming the input, the travel REQUESTED,
the travel ADMITTED, the bounds met and the events it fired, each event entry
carrying the relation as written, the fraction of the path, the moving
input's value at the event, and the targets with their new values. The admitted
travel and the stops are stated by the requirement "A bound stops a clocked
request on its path"; where no bound is met the admitted travel SHALL be the
requested one and the stops SHALL be empty. `record=N` SHALL keep a bounded
ring of the same event entries, and a second bounded ring of the stops;
without it the request's own result SHALL still be complete. `sim.state` SHALL return
the whole bank by qualified id as a fresh mapping. `sim.snapshot()`,
`sim.restore()`, `sim.initial` and `sim.reset()` SHALL act on that bank,
`restore` refusing a snapshot taken over a different model before touching
anything.

A clocked simulation has no CADENCE: `run`, `at`, `every`, `tick`, `rate`,
`trigger`, `commands`, `program` and `crossings`
SHALL each be refused by name, under every time base. `sim.time` SHALL be
refused by name under a clocked root that declares NO time base, naming
`Time.elapsed()` as the way to have one, and SHALL read the banked seconds
under a clocked root that declares it. `sim.stops` SHALL NOT be refused: it
is the
bounded ring of the bounds a clocked machine met, under the requirement "A
bound stops a clocked request on its path".

A violated joint `range` SHALL be a STOP on the request's path, under the
requirement "A bound stops a clocked request on its path", which clips the
travel before any event is located, judges the constraints it compiled ITSELF
at the end of the request, and leaves every pose that is not a request to the
enumeration. A bound violated by the INITIAL pose — construction, `state=` or
`restore` — SHALL remain an impossible pose raising `JointRangeError`. Where
a request's own COMMITS carry a bounded coordinate outside its range, that
end-of-request judgement SHALL raise `JointRangeError` and refuse the whole
request, which commits nothing and never poses.

A request along the CLOCK SHALL NOT be clipped by any bound: a declared
range is a mechanical stop and nothing holds a clock. A coordinate carried
outside its range by a time request SHALL be judged by the same
end-of-request judgement, which refuses the whole request, commits nothing
and never poses.

#### Scenario: One request fires one event

- **WHEN** a register fixture standing at `units = 0` receives
  `sim.move('crank', by=360)` with `at = floor(crank / 360)`
- **THEN** exactly one event is reported, at the fraction the solve gives,
  `sim.state['units']` is `1`, and `sim.state['crank']` is `360`

#### Scenario: Ten events in one request equal ten requests of one

- **WHEN** one `sim.move('crank', by=3600)` is compared with ten successive
  `sim.move('crank', by=360)` from the same initial bank
- **THEN** both give the same bank, entry for entry, and the same ten events
  in the same path order

#### Scenario: A backwards request fires nothing

- **WHEN** a register fixture standing at `units = 9` receives
  `sim.move('crank', by=-3600)`
- **THEN** no event is reported, `units` and `tens` hold, `crank` has moved
  the whole travel, and the pose follows the crank

#### Scenario: An event surface that reads its own state moves with it

- **WHEN** a clearing fixture whose `at` is
  `ring >= START + PITCH * (10 - digit)` sweeps its ring far enough to clear
  a dial, and then sweeps further
- **THEN** exactly one event fires on the first sweep, the digit is zero
  after it, and the second sweep fires nothing

#### Scenario: The landing is on the far side of the surface

- **WHEN** a crossing of `floor(crank / 360)` is solved at `crank = 360`
- **THEN** the law is evaluated at exactly `360.0`, the floor branch there is
  `1`, and resuming the path from that value does not fire the event again

#### Scenario: Simultaneous commits read the same pre-event state

- **WHEN** two committing relations cross at one point and each law reads a
  state the other writes
- **THEN** both read the values that stood before the event and both sets of
  targets take their results together

#### Scenario: Surfaces one ulp apart are two events

- **WHEN** two committing relations have comparison surfaces differing by one
  representable value, and one request crosses both
- **THEN** two events are reported, in path order, the second law reading
  what the first committed, and the same two events are reported whether the
  crossing happens inside one long request or inside the shorter request that
  reaches just past it

#### Scenario: Surfaces that land on one value are one event

- **WHEN** two committing relations' far-side landings are the same
  floating-point value
- **THEN** exactly one event is reported, both relations commit at it, and
  both read the bank as it stood before it

#### Scenario: A clocked pose leaves time symbolic

- **WHEN** a clocked root whose `simulate()` reads `self.time` is posed by
  `Sim(model)` and again after a request
- **THEN** `time` is the untimed symbolic animation variable in both poses,
  unchanged from the same model built outside a simulation, and `time` is
  absent from `sim.state`

#### Scenario: A curved at is refused at construction

- **WHEN** a committing relation's `at` is `floor(sin(crank))`
- **THEN** simulation construction is refused naming the relation, `crank`
  and the primitive

#### Scenario: A refused request commits nothing

- **WHEN** a request's third event evaluates a law that raises
- **THEN** the bank, the tree and the record stand exactly as they did before
  the request

#### Scenario: A request whose commit leaves a joint out of range commits nothing

- **WHEN** a request would advance a state far enough that the joint it
  would pose leaves its declared `range`
- **THEN** `JointRangeError` is raised, the bank holds the values it held
  before the request — the moving driver's included — the tree is still
  posed where it was, and the recorded events are unchanged

#### Scenario: Two relations writing one state at one event refuse the request

- **WHEN** two committing relations of one tree write the same state and
  their far-side landings on one request are the same floating-point value
- **THEN** the request is refused naming that state, both relations and the
  landing, and the bank, the tree and the record stand exactly as they did
  before it

#### Scenario: A non-finite commit refuses the request

- **WHEN** a committing relation's law computes an infinity or a NaN for a
  state it writes, whether that state declares `dtype=int` or not
- **THEN** the request is refused naming the relation, the state and the
  value, and the bank, the tree and the record stand exactly as they did
  before it

#### Scenario: A relation no driver can reach is refused

- **WHEN** a committing relation's sources are all states, so that no
  declared driver can move its event level
- **THEN** simulation construction is refused naming the relation and saying
  its event level moves with no declared driver

#### Scenario: The cadence surface is refused

- **WHEN** a clocked simulation calls `run`, `every`, `tick`, `trigger` or
  `rate`, and a clocked simulation over a root declaring no time base also
  calls `time`
- **THEN** each is refused by name, saying a clocked model has no cadence,
  and the `time` refusal names `Time.elapsed()` as the way to have a clock

#### Scenario: A request ending exactly on a strict surface leaves it for the next request

- **WHEN** a committing relation states `at` as a STRICT comparison against a
  representable threshold and a request ends exactly ON that threshold
- **THEN** the request fires nothing, and the next request, beginning on that
  threshold, fires the event once at the first representable value past it,
  while the non-strict twin of the same relation fires on the FIRST request,
  at the threshold itself, and fires nothing on the one that resumes from it

#### Scenario: A stop from a coordinate standing at zero admits no travel

- **WHEN** a bank stands outside a LOW bound with the moving input at exactly
  `0.0`, and a request pushes it further outside
- **THEN** the request admits ZERO travel, fires nothing, commits nothing and
  reports its stop, exactly as the same machine's HIGH bound does from a
  coordinate whose magnitude is large
