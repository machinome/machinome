## Context

The requirement, the table it comes from and what this cycle is owed by are
in `proposal.md`. Three records bind this design:

- **The ratified clocked discipline.**
  `openspec/changes/archive/2026-09-17-declare-the-state` with **ADR-125**,
  and `openspec/changes/archive/2026-09-17-a-bound-stops-the-request` with
  **ADR-126**, together with the baseline specs they synced. They are
  AUTHORITY: nothing here re-opens a decision they took.
- **The requirement note**, `workflow/docs/clocked-machine.md`, sections
  "Time without running" and "Candidate spelling". It is SUPERSEDED history
  carrying four marked corrections; its two-axis table and its pendulum
  sentence are the requirement this cycle answers, and its candidate
  spelling is a sketch.
- **The rejected protocol.** On 2026-09-13 the pilot rejected `running(r)`,
  `r.state`, `r.event` and `r.equal`
  (`workflow/open-run-simulation/design.md`, "Decision 2026-09-13").
  Nothing here reintroduces it: the clock is a VALUE in the bank, read by
  the same closed-form callables a project already writes.

One constraint stands above the rest and is repeated because an implementer
will be tempted: **`Time.running()` is untouched.** ADR-104 remains the
decision for the running base; ADR-105, ADR-106 and ADR-107 stand exactly as
written. This cycle does not make `Time.elapsed()` a route into the running
mechanics, does not compile a program, and does not integrate anything.

The machinery this design REUSES rather than reproduces is the machinery
ADR-125 and ADR-126 already consume: `JumpPlan._solved` and `_surfaces`
(ADR-107), `_shape_of` and `_KinkCuts` (ADR-123), `far_side_of` (ADR-121),
`checked_expression` and `SYMBOLIC_BUILTINS` (ADR-106), `_MAX_CROSSINGS`.
**This cycle introduces no locator, no knob and no tolerance.**

## Goals / Non-Goals

**Goals:**

1. A project can say "this machine's time is elapsed seconds" without also
   saying "retain every coordinate and integrate every law", and can commit
   a state at an instant the clock reaches.
2. Events on time and events on inputs are THE SAME EVENT: one solver, one
   ordering, one conflict rule, one exactness claim.
3. A model that declares no `State` is unchanged in behaviour, in published
   bytes and in cost, and a model that declares `Time.running()` is
   unchanged in every particular.
4. Every square of the two-axis table is either sayable or refused BY NAME,
   with the refusal stating what it means.

**Non-Goals:**

Listed in `proposal.md`; section 12 gives each its reason and the shape a
later cycle takes.

## Decisions

### 1. `Time.elapsed()`, the third spelling

```python
from solid_node.motion.ports import Time

class Regulator(AssemblyNode):
    time = Time.elapsed()
```

ADR-104's shape exactly: `Time` keeps its ONE field `loop`, a constructor
per base tells the bases apart, and `mode` is a property. `Time.elapsed()`
is a frozen instance whose `loop` is `None` and whose `mode` reads
`'elapsed'`, built the way `Time.running()` is built — without `__init__`,
because `loop` is deliberately absent here and present-and-validated in
`Time(loop=)`. `__set_name__` is untouched, so the third base obeys the
same declaration rules as the other two: the name `time`, on an
`AssemblyNode`, on the root of the tree it is read in.

`Time()` with no base goes on raising a `TypeError`; its message gains the
third spelling. The existing tests assert the SUBSTRINGS `Time(loop=` and
`Time.running()` (`tests/test_time_base.py`), both of which survive, so no
expected value moves anywhere in the suite.

**Every consumer that reads `.loop` keeps getting `None`, and behaves as it
does for the running base.** That is four call sites, each verified against
the source rather than assumed: `serializer.animation_block` publishes no
`loop` key, `assembly.read_time` leaves `$t` unscaled, `manager.snapshot`
keyframes the fraction, and `declared_time` returns the declaration. Every
consumer that reads `.mode` compares it to `'running'`
(`serializer.running_root`, `Sim.__init__`, `couplings.run_owned`,
`assembly._coordinate_delivery`, `manager.snapshot`), so an elapsed root is
treated as NOT running by each of them, which is what it is.

*Alternatives considered.* A second declaration class `Elapsed()` — rejected
for ADR-104's own reason: every consumer of `declared_time(cls)` would learn
a second type where a `mode` string costs them a comparison. `Time(elapsed=
True)` — rejected for ADR-104's own reason: a flag rather than the thing it
declares. Making `Time.running()` sugar for "elapsed plus integrated", as
the note floats — rejected because it would change `Time.running()`, which
is the one thing this cycle may not do.

### 2. Elapsed × none is ADMITTED and EQUIVALENT

`Time.elapsed()` on a root whose tree declares NO `State` is admitted, and
the two axes stay independent: **the STATE DISCIPLINE selects the executor,
the TIME BASE says what `time` means.** Concretely:

| question | answer for an elapsed root with no state |
| --- | --- |
| which simulation runs over it | `Sim(node, dt)`, the ordinary fixed-`dt` stepping loop: `Sim.__init__` selects the clocked executor on the tree's STATES and branches on the base only for `mode == 'running'` (`simulation/sim.py:157-219`) |
| what `sim.time` reads | `self._tick * self.dt` — seconds, computed from the tick count on every access (`simulation/sim.py:442-451`) |
| what the stepping loop BINDS as `time` | exactly that number of seconds: `_binding` returns `dict(self.state, time=self.time)` and `set_state` delivers it (`simulation/sim.py:453-464`). A stepped simulation has bound SECONDS rather than the 0..1 fraction under EVERY base since it existed — an undeclared root included — so an elapsed root is bound with what its neighbour is bound with, and this cycle changes nothing here |
| what `self.time` reads unbound | bare `$t`, exactly as under `Time.running()` (ADR-104) and an undeclared root: `read_time` branches on `base.loop is None` (`node/assembly.py:693-700`) |
| what `self.time` reads bound | the bound number, in seconds, from `Sim`, `set_keyframe(t)` or `set_state(time=t)` — the snapshot entry `read_time` returns first (`node/assembly.py:674-678`) |
| what its document is | the document an undeclared root publishes, byte for byte: no `loop` key, no new version, no new binding |
| what publication does | publishes it, unchanged — the publication refusal is keyed on declared STATES (ADR-125 §10) and not on the time base |

So the declaration without memory changes NOTHING observable, and that is
the point: it lets a machine that is OPERATED say so before it has any
memory to retain, and it makes "elapsed" a property of the clock rather than
a property of the state discipline. The table's `—` in that square was
"nobody had asked", not "this cannot be".

*Alternative considered and rejected: refuse `Time.elapsed()` on a stateless
root, by name.* It would make the base's admissibility depend on a walk of
the whole tree for `State` declarations at the moment the defaults are
bound, would refuse a model the instant its author removed his last `State`,
and would state a rule the two-axis decomposition does not have. The one
thing it would buy — "every elapsed root has a banked clock" — is bought
more cheaply by decision 3's own wording.

*Alternative considered and rejected: make the elapsed base select the
CLOCKED executor by itself*, so `Sim(model)` takes no `dt` over any elapsed
root. It reads well — "elapsed means requests, not cadence" — but it makes
`Time.elapsed()` silently change the simulation surface of a stateless
model, and it makes ADR-125's ratified sentence "no clocked code path is
entered for a tree whose state collection is empty" false. Rejected for
both. A stateless machine with a clock has nothing to retain, so
`set_keyframe` and the stepping loop already put it anywhere it can be.

### 3. `time` in the bank, under an elapsed CLOCKED root

A tree that declares a `State` is a CLOCKED model (ADR-125, unchanged).
When such a root ALSO declares `Time.elapsed()`, its clocked simulation
banks `time`:

- the bank id is the bare `time`, which is `CLOCK_NAME` — the same string
  the run reserves, the same string `set_state` takes as its one global
  entry, and the same string a version 5 document publishes as a running
  program's clock. One name, from one place;
- the value is SECONDS, a float, initial `0.0`;
- `state={'time': 3.0}` at construction sets it, as session setup, exactly
  as it sets a driver or a state;
- `sim.state` returns it beside the drivers and the states;
- `sim.snapshot()` carries it and `sim.restore()` puts it back, because a
  snapshot IS the bank; `sim.reset()` returns it to `0.0` with everything
  else;
- `sim.time` reads it. This is the ONE name of ADR-125 §9's refused list
  that this cycle lifts, and it is lifted only under this base: under an
  untimed clocked root `sim.time` stays refused, with its message improved
  to name `Time.elapsed()` as the way to have one.

**No collision is possible, and nothing new refuses one.** A bank id is
bare only for a ROOT-declared driver or state, and a root-declared `Driver`
or `State` named `time` is ALREADY refused at class definition:
`DriverDeclaration.__set_name__` refuses a declaration that would shadow a
member of a base class, and `AssemblyNode.time` is such a member. A
child-declared one qualifies as `child.time` and cannot collide with the
bare name. The run's explicit `CLOCK_NAME` reservation
(`simulation/run.py`) exists because a running bank also holds JOINT
COORDINATES, which qualify by a different rule; a clocked bank holds none.
This is asserted by a test rather than left as a claim.

### 4. The request that moves time

`sim.move('time', by=seconds)` and `sim.move('time', to=seconds)` — the
SAME verb, the same `Request` value object, the same rules:

- ONE moving input per request still holds. A request moves TIME with every
  driver standing, or ONE DRIVER with time standing. Nothing moves two.
- Seconds are both the design unit and the native unit: the clock has no
  `scale`, no `dtype` and no `range`, so `by=`/`to=` and `Request.admitted`
  are all plain seconds and no conversion happens anywhere.
- **Time never reverses.** A request whose travel is negative, or whose
  `to=` is behind the banked seconds, is REFUSED by name, naming the banked
  instant and the one asked for, and saying elapsed seconds never wrap and
  never run backwards. It is a refusal and not a clip: a clip reports a
  STOP, and there is no stop — the request is meaningless, not obstructed.
- **Zero is admitted.** `by=0`, or `to=` the banked instant, moves nothing,
  fires nothing and poses the bank that already stands, returning a
  `Request` with `admitted == 0.0` and no commits. That is ADR-126's own
  reading of a request stopped at zero travel, and it keeps
  `move('time', to=t)` idempotent.
- A request naming `'time'` under a clocked root that declares NO elapsed
  base is refused by name, saying the root declares no time base and naming
  `Time.elapsed()`.

*Alternative considered and rejected: `sim.advance(seconds)`.* A second verb
would carry its own return type, its own ordering rules, its own recording
and its own documentation, all of them copies of `move`'s; and it could not
express "advance to exactly `t = 10`" without a second argument that is
`to=` under another name. `Sim.tick`, `Sim.run`, `Sim.every` and `Sim.at`
are the RUNNING and stepping cadence surface and stay refused over a clocked
root: a cadence is not what this is.

### 5. Events on time are events

`time` is admitted as a SOURCE of a committing relation, in both factories,
exactly as a driver is:

```python
T = 2.0          # seconds per swing
A = 12.0         # degrees

class Regulator(AssemblyNode):
    time = Time.elapsed()
    engaged = Driver(default=1, dtype=int)
    count = State(default=0, dtype=int)

    (time & engaged & count).commits(count, at=release, law=advance)

    def simulate(self):
        self.bob.rotate([0, 0, A * sin(2 * pi * self.time / T)])

def release(sources, targets):
    return lambda time, engaged, count: floor((time + T / 4) / (T / 2))

def advance(sources, targets):
    return lambda time, engaged, count: count + engaged
```

Everything about the event is ADR-125's, unchanged:

- `at` is ONE jump node whose level is classified STRUCTURALLY per moving
  input — affine SOLVED by division, kinked CUT at its own breakpoints and
  solved piece by piece, **curved REFUSED at simulation construction by
  name**. The clock joins the drivers in that loop and is classified by the
  same `_shape_of` over the same `_standing_except` substitution;
- only RISING steps fire, read from the branch the path came from and the
  branch at the landing;
- the landing is the nearest representable value on the FAR SIDE, by
  `far_side_of`'s ordinal walk, and it is both what the event reads and
  where the path resumes;
- two relations are ONE event exactly when their far-side landings are the
  SAME float — no tolerance, for ADR-125's reason, which is unchanged here
  because a request's travel in seconds is as much the author's to choose as
  a request's travel in degrees;
- commits are ordered by PATH ORDER, reads are SYNCHRONOUS and PRE-EVENT,
  and two relations writing one state at one landing refuse the REQUEST by
  name and commit nothing;
- `_MAX_CROSSINGS` applies unchanged: a time request that would fire more
  than a thousand events of one relation is refused naming the request, the
  relation, the count and the maximum, and saying it can be split.

**A pendulum's release is AFFINE in time.** `floor((t + T/4) / (T/2))` is a
floor over a linear function of the clock, so the fixture needs no curved
level, and this cycle therefore adds NO tolerance and keeps ADR-125's
exactness promise whole. A curved `at` in time — `floor(sin(t))` — is
refused at construction by the existing message with the clock named as the
input whose motion curves it. The alternative, admitting it and locating it
by ADR-123's bisection, was rejected outright: a clocked model's entire
claim is that its events are exact, and the bisection ADR-107 uses under a
run is stated in TICK-FRACTION units, which a request has none of.

**A relation the clock alone can move is legal.** ADR-125 refuses at
construction a committing relation whose every source is a state, because
nothing a request can move enters its level and it would sit silently inert.
Under an elapsed root the clock is something a request can move, so that
refusal becomes "no declared driver AND not the clock" — a relation NO
REQUEST can reach. The refusal's reason is unchanged and its message names
the clock among the inputs that would fix it.

**Where the clock may be named, and what a body without one actually gets.**
A committing relation naming `time` is declared in the class body that
declares the base — the root's — because that is the body in which the name
`time` holds the declaration object itself (`__get__` is not invoked on a
name read out of the body's own namespace). Three cases follow from ordinary
Python, and the third is not what a reader expects:

1. **The body declares `Time.elapsed()`.** `time` is that frozen `Time`
   instance, and this cycle gives `Time` the `&` and `commits` faces every
   other source kind carries (`motion/ports.py`, beside `Coordinate.drives`
   and `Coordinate.__and__` at lines 164-172). Admitted.
2. **The body declares `Time(loop=)` or `Time.running()`.** `time` is a
   `Time` instance of the wrong base, so the SAME faces are reached and
   refuse AT CLASS DEFINITION, by name, saying an event is located on a
   clock that never wraps and naming `Time.elapsed()`. The facts exist
   exactly there, which is ADR-125's own rule about where a refusal is
   raised. Reachable, and kept.
3. **The body declares no base.** A Python class body does **not** see a
   base class's attributes, so `time` is NOT `AssemblyNode.time` and the
   framework is not reached through it at all. The name resolves the way any
   other free name in a class body resolves — module globals, then builtins
   — which in practice means one of two things:
   - the file imported the stdlib `time` module (common in a project that
     already uses `time.perf_counter`), so `time` is a MODULE. A module has
     no `__and__`, so `time & engaged` dispatches to the RIGHT operand's
     reflected `__rand__`, which today does not exist on any declaration
     kind — Python then raises its own
     `TypeError: unsupported operand type(s) for &: 'module' and
     'DriverDeclaration'`;
   - nothing bound `time` at all, so the body raises `NameError` before any
     framework code runs.

**Decision: refuse the reachable half, and say plainly that the other half
is Python's.** `group_with` already refuses a non-coordinate RIGHT operand by
name (`motion/couplings.py:828-848`, "is not a coordinate, so it cannot join
a group with &"); the LEFT operand has no such refusal only because no
declaration kind carries `__rand__`. This cycle adds it — one reflected
helper, assigned on the kinds that already carry `__and__`:
`Coordinate` (`motion/ports.py:169`), `CoordinateRef`
(`motion/couplings.py:320`), `Coordinates` (`motion/couplings.py:789`),
`DriverDeclaration` and through it `StateDeclaration`
(`node/qualified.py:167`), `ChildDeclaration` (`node/declarative.py:451`)
and `RepeatDeclaration` (`node/declarative.py:567`) — so `<anything> &
<declaration>` refuses by name and names the operand instead of printing
Python's operand-type line. Where that operand is a MODULE the message adds
the clock sentence: the machine's clock is named only through the root's own
`time = Time.elapsed()` declaration, and a body that declares no base has no
clock to name. It costs six one-line assignments and one function, it
changes no admitted behaviour — `__rand__` is reached only when the left
operand's own `__and__` is absent, and every kind above raises or builds in
its own `__and__` — and it is the same generalization §7 makes of a chain's
free names: the refusal is stated for ANY foreign operand, and the clock is
only the case that found it.

**The blind spot, recorded rather than papered over.** A body that never
bound `time` raises `NameError`, and no framework refusal can improve on
that: the name fails before an operator is reached. The spec says so, the
scenario asserts Python's own answer, and this change promises no message
there.

### 6. What the pose reads, and the one walk that binds the clock

Under a bound clocked simulation with an elapsed base, the tree is posed
with every driver, every state AND the clock bound — `self.time` a number of
seconds. Unbound — the build path, `solid build`, `solid export`, a
snapshot, any producer, and any render outside a simulation — `self.time`
reads bare `$t` through the fallback an unbound clock already takes, because
`read_time` branches on `base.loop is None` and an elapsed base's `loop` IS
`None`. **That branch needs no edit**, which is why this cycle touches no
document producer: a `simulate()` or a law that is a formula of time
animates in the untimed preview exactly as it does today, and is posed at
`sim.time` under the simulation.

**The clock is delivered in the ONE walk that binds the tree, through the
hook that walk already has.** The walk is
`solid_node/node/qualified.py:drive_tree(root, resolve, visit=None,
collected=None)` — not an assembly-module function — and `Clocked.pose`
calls it with a `resolve` that reads the bank
(`simulation/clocked.py:1394-1408`). Both claims this design rests on are the
walk's own, verified in the source:

- it **writes each node's snapshot directly**, `states[name] = resolve(node,
  path, name, declaration)` (line 389), deliberately bypassing `set_state`
  because the symbolic mode's values are not numbers (docstring, lines
  348-353);
- it **renders once at the end**, `root.render()` after the whole descent
  (lines 421-422), which is what makes one request cost one pose.

`read_time` (`node/assembly.py:652`) reads `node._states['time']` FIRST
(line 676) and falls back to the symbolic path per node, so a clock bound
only on the root would leave every descendant symbolic. The delivery is
therefore per visited assembly — and `drive_tree` already has the hook for
exactly that: `visit(node, path, children)` is called for every assembly
after its drivers and states are bound and BEFORE anything in the tree
renders (lines 415-417), and its docstring states its purpose as "a caller
that also needs something else declared per node pays for one walk rather
than two". `qualified_declarations` already uses it that way
(`simulation/enumeration.py:74-112`).

**So no new parameter.** Under an elapsed clocked root `Clocked.pose` passes
a `visit` that writes the banked seconds into `node._states['time']`; under
every other root it passes none and the walk is the walk every other pass
makes. That keeps §11's "the walk is unchanged for a model with no clock"
literally true — the argument is not merely optional, it is absent.

*Alternative considered and rejected: a new `clock=` parameter on
`drive_tree`.* It would say the same thing in a signature every caller of a
shared walk has to read, where `visit` already says it and is already used
this way by the enumeration.

*Alternative considered and rejected: `node.set_state(time=seconds)` after
`drive_tree`.* It is the existing recursive delivery and would need no hook
at all — but it re-simulates the tree, so every request would pose TWICE.
A request costing two poses would halve the speed result the clocked
discipline exists for, on the one base this cycle adds. Rejected for cost.

### 7. Nothing stops a clock, and no chain follows one

Two questions, one answer.

**A request along TIME is never clipped.** ADR-126 clips a request by
taking, for each constraint THE MOVING DRIVER CAN MOVE, the earliest point
at which its level exceeds its threshold. Constraint plans are compiled per
declared driver, so the clock has none and the clip finds nothing — the
behaviour falls out of ADR-126's own compile. This cycle STATES it as a
promise rather than leaving it an accident, because the reason is a design
decision and not an implementation detail: **a declared range is a
MECHANICAL STOP, and no interlock holds a clock.** A pawl stops a crank
because something is in the way; nothing is in the way of the next second.

What happens instead is already written: ADR-126's step 6 judges every
compiled constraint over the FINAL bank, through the same chains the clip
used, and a violation refuses the REQUEST by name and commits nothing. So a
coordinate that leaves its declared range at some instant is an impossible
POSE and the request that reaches it is refused whole — which is exactly the
untimed reading of a range, and exactly what ADR-125 said a bound was before
ADR-126 gave a driver request its clip. The refusal message names the
coordinate, the side, the bound's value, the coordinate's value and the
instant, and says a clock is not stopped by an interlock.

**A compiled CHAIN may not follow the clock.** ADR-126 composes each
bounded coordinate, and each coordinate a `Bound` reads, down to the bank's
ids, which stay free names. A relation whose law carries the clock (the next
paragraph names the one construction that can) composes a graph carrying the
animation symbol instead, and today that graph reaches
evaluation with a free name the bank has no entry for and dies with a bare
`KeyError`. This cycle refuses it AT SIMULATION CONSTRUCTION, by name,
naming the joint, the node, the side and the name that survived, and saying
that a clocked stop is compiled over the bank and that a clock-driven
coordinate is not something a stop can hold. The rule is stated GENERALLY —
**any free name surviving a composed chain that is not a bank id is
refused** — so it covers the clock and whatever else ever leaks, and it is
ADR-126's own promise ("what the bank cannot reach this way is refused by
name") made true for a case its implementation left open.

**How a chain ever carries the clock, named exactly, because it is not
obvious.** `time` is refused as a `drives` source by this very cycle, and a
`law=` callable receives only its sources' VALUES, so neither is a route.
The one route is the law FACTORY, and it is the ordinary protocol used
ordinarily: a factory is called ONCE at realization with the realized OWNERS
(`motion/couplings.py:1552-1554`,
`self.callable_law(_law_argument(driver_ends), _law_argument(driven_ends))`),
so a factory that reads `owner.time` there captures what an UNBOUND read
gives — the symbolic `$t` (`node/assembly.py:693-700`) — and closes over it:

```python
def wobble(source, driven):            # the realized owners
    base = source.time                 # unbound at realization: `$t`
    return lambda crank: crank + A * base
```

From there the path to the refusal is the existing compile, step by step:
`_Chains._law` applies that callable to SYMBOLIC tokens while composing
(`simulation/clocked.py:776-818`, `record.law.forward(*tokens)` at line 794),
`checked_expression` passes a free NAME through untouched — it refuses raw
text and unknown calls, not names (`simulation/program.py:3772-3796`) —
`free_names` keeps `$t` like any other name
(`expression_graph.py:42-43`), the substitution replaces only the source
tokens (line 816-818), and the surviving name reaches `Bounded.standing`,
whose `{name: bank[name] for name in self.names}`
(`simulation/clocked.py:964-969`) raises the bare `KeyError` this cycle
replaces with a refusal. `_constrained` is where the refusal belongs: it
already computes `moving = free_names(root)` (`simulation/clocked.py:1166`)
and already holds the bank as `chains.bank` (drivers AND states,
line 1113-1122), so the check is "every free name of the chain and of the
level, `$own` aside, is a bank id" and costs one set difference per
compiled bound.

Two facts about that fixture an implementer should have before writing it,
both checked here: reading `owner.time` in a factory cannot RAISE — the
phase note is a recorder, not a guard (`node/phase.py:191-203`) — but it
MAY, if the factory runs inside a render phase, record a "read time" that
makes the legacy-render `FutureWarning` fire for that class, which the test
should expect rather than be surprised by. Task 7.4 keeps its STOP clause
even so: this route is established statically, not yet executed, and an
implementer who finds it blocked reports the evidence instead of inventing
a path.

*What this excludes, stated rather than hidden.* A clock-driven coordinate
carrying a declared `range` — a pendulum whose bob is both ranged and driven
by a relation whose law factory captured the clock. Such a model must drop the range (a
clock-driven part is not stopped by one) or state the relation from a
driver. In practice the shape is already rare: a joint an author poses BY
HAND in `simulate()` from `self.time` is the ordinary way to write a
pendulum, and ADR-126 already refuses a RANGED joint bound by hand, so the
only models this newly refuses are relation-driven ones.

*Alternative considered and rejected: admit the clock as a chain free name
and clip a time request like a driver request.* It is coherent and it is
where a later cycle goes. It was rejected HERE because it is two changes
and not one — the rename of the animation symbol to the bank id is the easy
half, and the hard half is that a level moving with the clock must be
classified, solved and given a direction test whose `h = max(0, g(0))`
reading ADR-126 already records as contested
(`workflow/warts.md`, "The direction test and a request back to exactly
where it started"). Doing half of it would ship a clip that stops a clock
sometimes. The two arrive together or not at all, and they are recorded as
one wart in section 12.

**A `Bound`'s own expression is unchanged.** `reads=` names COORDINATES
(ADR-113) and the clock is not a coordinate, so nothing about a bound's
argument list changes. A read of a declared driver or a declared state stays
what ADR-126 made it; a read reaching a clock-driven coordinate is refused
by the rule above, naming the read.

### 8. The refusal table, and what each one says

| Attempt | Refused | Where |
| --- | --- | --- |
| `Time()` with no base | `TypeError` naming all THREE spellings | the constructor, as today |
| `Time.elapsed()` misnamed, on a leaf, or below the root | by name, exactly as the other two bases are | `__set_name__`, `read_time` — untouched |
| a `State` under `Time(loop=)` | by name: a loop replays from zero and the state climbs across loops | the enumeration that binds defaults — unchanged |
| a `State` under `Time.running()` | by name, with the meaning DEFINED and not implemented | the same place — unchanged |
| a `State` under `Time.elapsed()` | **admitted**: this is the square the cycle opens | — |
| `time` as a source under `Time(loop=)` or `Time.running()` | by name, naming `Time.elapsed()` | class definition, where the base declaration is written |
| `time & <a declaration>` in a body that declares no base, where `time` is the stdlib MODULE the file imported | by name: the reflected `&` names the operand and says the clock is only the root's own `Time.elapsed()` declaration (§5) | class definition, in the `&` |
| `time` in a body that BINDS no `time` at all | **not the framework's**: Python raises `NameError` before an operator is reached, and this cycle promises nothing there (§5) | — |
| `time` as a DRIVEN end of `commits`, or either end of `drives` | by name | class definition |
| `sim.move('time', ...)` under a non-elapsed clocked root | by name, naming `Time.elapsed()` | the request |
| a request moving time BACKWARDS | by name, naming both instants | the request |
| `sim.time` under a clocked root with no elapsed base | by name, naming `Time.elapsed()` | the readout — ADR-125 §9's refusal, message improved |
| `sim.run`, `at`, `every`, `tick`, `rate`, `trigger`, `commands`, `program`, `crossings` | by name, unchanged under every clocked root | the readout |
| a committing relation no request can move | by name, now naming the clock among the inputs that would fix it | simulation construction |
| a curved `at` in the clock | by name, naming the clock and the primitive | simulation construction |
| a chain reaching a name the bank has not got | by name, naming the joint, the side and the name | simulation construction |
| publishing a tree that declares a `State` | by name, unchanged — cycle 4's to lift | `serializer.document_body` |

### 9. What `Time.running()` keeps, said once more

Not its compile, not its tick, not its document, not its meaning. In
particular: a `State` under `Time.running()` stays REFUSED with ADR-125's
own message, and its DEFINED meaning — an ADR-121 self-read law whose value
changes only through a switch — is unchanged and still not implemented. The
running root's document, its version, its program block, its clock name and
`tests/running-corpus.json` are untouched, and the change is validated
against that by assertion rather than by intention (section 13).

`Time.elapsed()` is not a partial `Time.running()` and must not be
described as one. It is the OTHER half of ADR-104: the base, without the
mechanics ADR-105 to ADR-107 attach to it.

### 10. The ADR plan

ONE NODE ADR, candidate **ADR-127** — "A clock is a banked value, and an
event on it is an event" (ADR-126 is the highest accepted). Extracted AFTER
implementation, as the discipline requires, and not written now. It will
record:

- the third spelling and ADR-104's one-field shape it keeps (§1);
- the two axes made independent, and elapsed × none admitted as equivalent
  because the state discipline alone selects the executor (§2);
- the clock in the bank under one name, with no collision possible (§3);
- one verb for every request, and time that never reverses (§4);
- events on time located by ADR-125's solver with no new tolerance, and the
  pendulum's affine release as the evidence that none is needed (§5);
- where the clock may be NAMED, and the honest limit of it: the `&` made
  symmetric so a foreign left operand is refused by name, and a body that
  binds no `time` left to Python's own `NameError` (§5);
- the clock delivered through the hook the walk that already poses the tree
  already has, so a request still costs one pose and the walk gains no
  parameter (§6);
- nothing stops a clock: a time request is never clipped, a chain may not
  follow the clock, and an impossible pose is refused whole (§7).

**Extends** ADR-104 (the base, whose running half it leaves alone) and
ADR-125 (the bank, the solver and the refusal temperament). **Cites**
ADR-126 (the clip it declines to give a time request, and the chain compile
it tightens), ADR-107, ADR-121, ADR-123. It amends NOTHING: ADR-104 stands
as written for the running base, and ADR-105, ADR-106 and ADR-107 stand
whole. The originating project is named as what the cycle is NOT owed by:
the Curta has no clock, and the pendulum fixture is the evidence.

No second ADR. The clock's document is cycle 4's decision and the viewer's
clock is cycle 6's.

### 11. Zero behaviour change, as a requirement with a test

Structural, not hoped for:

- the elapsed base is a third value of an existing property, and every
  consumer branches on `loop is None` or `mode == 'running'`, both of which
  give an elapsed root the answer they give a running one or an undeclared
  one (§1, each site verified at apply);
- the clocked executor is entered exactly where ADR-125 entered it — a
  non-empty state collection — so "no clocked code path is entered for a
  stateless tree" stays literally true and its counter assertion stays
  green;
- `drive_tree` gains NOTHING: the clock rides its existing `visit` hook, and
  only an elapsed clocked pose passes one, so the walk every other pass
  makes is the walk it makes today (§6);
- the reflected `&` refusal (§5) is reached only where Python raises
  `TypeError` today — a left operand whose own `__and__` is absent — so no
  admitted `&` changes and no message an existing test asserts moves;
- no document producer is touched at all.

Proof in section 13.

### 12. What is left, and the shape each takes

Named here and carried to `workflow/warts.md` at completion.

- **A clip in time, and a chain that follows the clock.** One piece of work,
  §7. Its shape: the animation symbol renamed to the bank id where a chain
  is composed, the constraint level classified in the clock as it is in a
  driver, and a direction test for a level that is PERIODIC in time — which
  is the case ADR-126's `h = max(0, g(0))` was never asked about, and the
  contested reading already recorded in `warts.md` is the first thing it
  must settle.
- **A looping root with memory.** Still refused by name. The demo that would
  make it sayable — a snapshot restored at each wrap — has not appeared.
- **`Time.elapsed()` under a running root**, which is a category error, and
  **a `State` under `Time.running()`**, whose meaning is defined and not
  implemented (ADR-125, unchanged).
- **An `Instruction`, a control, or `move(duration=)` over the clock.** A
  declared advance of a named number of seconds is a coherent idea and is
  what a browser panel will want; its shape depends on what cycle 6 needs
  from it.
- **A multi-input request** that moves a driver and the clock together.
  ADR-125's narrowing, unchanged: the exactness classification is stated
  against one moving input.
- **`time` as the source of a `drives` relation.** A part whose pose is a
  formula of time is written in `simulate()`, which is what the pendulum
  fixture does; admitting the clock into the relation graph would reach the
  running compile's own source space, and that is not this cycle's.
- **Publication and the viewer** (cycles 4, 5 and 6).

## Risks / Trade-offs

- **An implementer reads "elapsed" and reaches for the run.** → The one
  constraint is repeated in the context, in §9 and in the ADR plan, and
  section 13 asserts the running corpus and the running fixtures unchanged
  rather than trusting the reading.
- **The clock in the bank makes `sim.state` grow a key under one base.** →
  Stated in the spec and asserted both ways: present under an elapsed
  clocked root, absent under every other clocked root.
- **A model with a clock-driven RANGED joint is newly refused** (§7). → The
  message names the joint and the one-line fix, the shape is rare for the
  reason §7 gives, and the alternative — leaving it to die on a `KeyError`
  at the first request — is worse.
- **A long time request can fire a great many events.** → `_MAX_CROSSINGS`
  applies unchanged and its refusal says the request can be split; the
  fixture asserts it at a request that crosses the maximum.
- **Two poses per request would halve the speed result.** → §6's decision,
  and section 13 measures seconds per request and per pose on the fixture so
  the claim is a number and not a hope.

## Open Questions

Recorded rather than silently decided; none blocks this cycle.

1. **Should a time request report the instants it PASSED without firing?**
   A maker asking "what happened between 0 and 10 seconds" is answered by
   the commits; one asking "which releases were disengaged" is not. The same
   question ADR-126 records for constraints examined but not met.
2. **Does an elapsed clocked root want `set_keyframe` to be refused?** Today
   `set_state(time=)` is a general delivery and the clocked simulation does
   not own the clock the way a run owns its coordinates. Left alone: this
   cycle refuses nothing that already works.
3. **What a version carrying a clocked clock publishes** — the clock's name,
   its initial value, and whether a consumer advances it — is cycle 4's, and
   nothing here presumes it.

## Planned proof

### 13. Fixtures and tests, every one RED FIRST

Geometry-free — no `meshes=True` — with ONE exception: the document-producer
check of §6 runs `solid build` and `solid export` over the `Swing` fixture,
whose geometry is a single box for exactly that reason. **No headless
browser anywhere in this cycle**: byte identity of the published document is
what is being proved, `document_body` is where that fact is, and a Chromium
capture would add an unreliable dependency (this mount, and the snapshot
extra) to a claim it cannot strengthen. Every run under
`OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`, one job at a time
(`/home/asa/devel` is a virtiofs mount that exhausts file descriptors under
parallel load). Cycle 1's and cycle 2's fixtures — the counter, the
clearing dial, the Curta-shaped register, the pawl, the lock, the freeze,
the gate — are NOT edited.

**`tests/clocked_project/pendulum.py`** (new), two roots:

- `Regulator` — the elapsed × memory fixture of §5: `time = Time.elapsed()`,
  an `engaged` Driver, a `count` State, a bob posed in `simulate()` from
  `A * sin(2*pi*self.time/T)`, and one committing relation
  `(time & engaged & count).commits(count, at=release, law=advance)` whose
  `at` is `floor((time + T/4) / (T/2))`.
- `Swing` — the same root with the State and the relation removed: the
  elapsed × none fixture.

**The clock is declared and equivalent** (§1, §2): `Time.elapsed()` reads
`mode == 'elapsed'` and `loop is None` off the class; `declared_time`
returns it; `Time()` still names three spellings; a misnamed, leaf-borne or
below-the-root declaration is refused exactly as the other bases' are;
`Swing` renders with `self.time` bare `$t`, keyframes to a number and
clears back; `Sim(Swing(), dt=0.1)` steps and `sim.time` reads `k*dt`;
`Swing`'s published document is compared BYTE FOR BYTE with the same tree
declaring no base at all.

**The bank** (§3): `sim.state['time']` is `0.0` at construction and absent
from a clocked fixture with no base; `state={'time': 4.0}` opens there;
`snapshot`/`restore` carry the instant with the count; `reset` returns both;
a root-declared `Driver(time=...)`/`State` named `time` is refused at class
definition by the existing shadowing message, asserted so the "no collision"
claim is tested and not assumed.

**The request** (§4): `move('time', by=T/2)` from rest fires exactly one
event at the solved instant; `by=` negative and `to=` behind the bank are
each refused by name with the bank unchanged; `by=0` is admitted, commits
nothing and leaves the pose standing; `move('time', ...)` on a clocked root
with no base is refused naming `Time.elapsed()`.

**Events on time** (§5): one request of `by=40*T` fires EIGHTY events in
path order (the level rises twice per period, at each extreme of the swing;
the first draft of this section said forty and was corrected at the
orchestrator's review of the implementation) with their instants EXACTLY
the hand-computed release times; the same eighty as forty requests of
`by=T` give an identical bank and identical instants; a `move('engaged', to=0)` at a standing clock fires NOTHING and
then a time request over it commits a held count; a curved `at` in the clock
is refused at construction naming the clock and the primitive; a relation
whose only moving source is the clock is ADMITTED where cycle 1 refused it;
a request crossing `_MAX_CROSSINGS` releases is refused naming the request,
the relation and the maximum.

**The pose** (§6): after `move('time', by=3*T/4)` the bob's operation is the
number `A*sin(2*pi*(3T/4)/T)` and `self.time` reads that instant; the SAME
tree rendered outside any simulation carries `$t` in its operation, and its
serialized expression is identical to the `Swing` fixture's; a counter
asserts ONE render per request.

**Bounds** (§7): a `Regulator` variant with a ranged joint driven by a
relation whose LAW FACTORY captured `owner.time` at realization — the
construction §7 names, spelled out there — is REFUSED at simulation
construction naming the joint, the side and the surviving name; a
`Regulator` variant with a ranged DRIVER-driven joint is clipped by a driver
request exactly as ADR-126 says and is NOT clipped by a time request; a time
request that carries that coordinate out of range is refused whole, naming
the instant, with the bank, the pose and the record standing.

**Refusals** (§8), one test each asserting what the message names: a
`State` under `Time(loop=)` and under `Time.running()`, unchanged; a `State`
under `Time.elapsed()` ADMITTED; `time` as a source under each of the other
two bases; a body that declares no base whose file imported the stdlib
`time`, where the reflected `&` refuses naming the operand and the clock
rule; a body that binds no `time` at all, where PYTHON's `NameError` is
asserted and no framework message is claimed; `time` as a driven end and as
either end of `drives`; `sim.time` refused under an untimed clocked root
naming `Time.elapsed()`; every other name of ADR-125 §9's list still refused
under an elapsed clocked root.

**Zero behaviour change** (§11): the whole existing suite green with no
fixture edited and no expected value changed; `tests/running-corpus.json`
and every running fixture untouched, asserted by `git status`; a
byte-identical document assertion for an existing published fixture; the
clocked-path counter asserted ZERO across a stateless model's construction,
pose, `Sim(node, dt)` stepping and publication; the running fixtures' per-
tick cost inside its recorded envelope.

### 14. Measurement plan

On the pendulum fixtures only, reported as their own numbers and compared to
nothing outside this change:

- seconds per time request with no event, with one event, and with forty;
- seconds per pose of the fixture, so the ratio §6 rests on is a number;
- seconds per request of the cycle 1 register fixture before and after, to
  show the clock costs an untimed clocked model nothing;
- seconds per pose of a stateless fixture before and after.

**Not claimed:** anything about the Curta, which has no clock, and any
comparison with `Time.running()`, which this cycle does not touch.
