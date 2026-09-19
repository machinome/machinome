## Why

The clocked discipline (`declare-the-state`, ADR-125; `a-bound-stops-the-
request`, ADR-126) gave a root MEMORY with no clock. Its bank is drivers and
states, a request moves ONE driver along a straight path, every rising step
of an `at` level on that path is an event located exactly, a declared range
clips the travel, and `time` is not banked at all: a clocked pose leaves
`self.time` the untimed symbolic `$t` exactly as the build path does.

ADR-125's own two-axis table (design section 12, and the ADR's first
Consequence) leaves ONE square to this cycle:

| time base | none | memory | integrated |
| --- | --- | --- | --- |
| untimed | poses today | ADR-125 | — |
| looping (`Time(loop=)`) | the clocks today | refused by name | — |
| elapsed | **this cycle** | **this cycle** | `Time.running()` |

**elapsed × memory** is a machine with a clock and memory and no
integration. The requirement note states it plainly
(`workflow/docs/clocked-machine.md`, "Time without running"): *a pendulum is
a formula of elapsed time; a counter beside it is a state variable committed
when the pendulum's phase, an expression of time, crosses its release.
Events on time and events on inputs are the same kind of event.* The
framework cannot say it, because ADR-104 made "elapsed seconds that never
wrap" declarable only as HALF of `Time.running()`, whose other half
(ADR-105, ADR-106, ADR-107) retains every coordinate and integrates every
law at a fixed cadence — the generality the clocked discipline exists not to
pay for.

**This cycle is not owed by the originating project.** The Curta
(`projects/Calculators/Curta-Type-I-3x`, branch `direct-operation` at
`9fb725f`) is the machine the clocked discipline was cut from and it has NO
clock: it is operated, its events are located on the crank and the clearing
ring, and nothing in it is a function of elapsed seconds. What owes this
cycle is the two-axis table itself — a decomposition is not honest while one
of its squares is unsayable — and the viewer, whose timeline is a clock and
which must be able to execute a clocked document that has one (cycle 6). The
Curta stays named because the machinery this cycle extends is its, and
because nothing here may cost it anything.

`Time.running()` is UNTOUCHED: not its compile, not its tick, not its
document, not its meaning. That is a pilot constraint, not a preference.

## What Changes

- **`Time.elapsed()` is a third spelling of `Time`**, beside `Time(loop=)`
  and `Time.running()`, in ADR-104's own shape: one field, a constructor per
  base, `mode` reading `'elapsed'` and `loop` reading `None`. The
  declaration rules are unchanged — the name `time`, on an `AssemblyNode`,
  on the root of the tree it is read in. `Time()` with no base goes on
  raising the `TypeError` that names the spellings, now three.
- **The time base and the state discipline are INDEPENDENT AXES, and only
  the state discipline selects the executor.** `Time.elapsed()` on a root
  whose tree declares NO `State` is ADMITTED and EQUIVALENT: the simulation
  over it is the ordinary fixed-`dt` stepping loop, `self.time` reads bare
  `$t` unbound and the bound seconds under a snapshot exactly as under
  `Time.running()`, and its document is byte-identical to an undeclared
  root's. What the elapsed base ADDS is a MEANING for `time` — elapsed
  seconds that never wrap, which is what a machine that is operated has and
  a loop has not — and, under a clocked root, a banked clock.
- **Under a clocked root declaring `Time.elapsed()`, `time` is a BANKED
  VALUE of the simulation**: in seconds, initial `0`, `sim.time` reading it
  (the one name ADR-125 §9 refused that this cycle lifts, and only for this
  base), carried by `snapshot`/`restore`, settable by `state=` as session
  setup, returned to `0` by `reset`. `sim.state` carries it beside the
  drivers and the states.
- **A request may move time.** `sim.move('time', by=seconds)` or
  `to=seconds` — the SAME verb, the same value object, the same one-moving-
  input rule: a request moves time with every driver standing, or one driver
  with time standing. Elapsed seconds never wrap and never reverse, so a
  request that would move time BACKWARDS is refused by name; zero is
  admitted, fires nothing and poses what already stands.
- **`time` is a SOURCE of a committing relation, exactly as a driver is.**
  `(time & engaged & count).commits(count, at=release, law=advance)` —
  `at` is an integer-valued expression over drivers, states and the clock,
  every RISING step of it along a time request is one event located exactly
  by ADR-125's solver, commits are ordered by path, reads are synchronous
  and pre-event, and two relations writing one state at one landing refuse
  the request as they do today. ADR-125's classification is unchanged:
  affine solved, kinked cut, curved refused at construction by name. A
  pendulum's release is AFFINE in time — `floor((t + T/4) / (T/2))` — so
  nothing here needs a curved level and NO TOLERANCE is introduced, which
  keeps ADR-125's exactness promise whole.
- **What the pose reads is the banked clock, and nothing else changes.**
  Under a bound clocked simulation `self.time` reads the banked seconds as
  a number; unbound — the build path, an export, a snapshot, any producer —
  it reads bare `$t` exactly as it does under `Time.running()` today
  (ADR-104), so a `simulate()` or a law that is a formula of time animates
  in the untimed preview as it does today and is posed at `sim.time` under
  the simulation. No document producer is touched by this cycle.
- **Nothing stops a clock.** A request along TIME is never clipped by a
  bound: ADR-126's clip examines the constraints the moving DRIVER can move,
  and time is not one. A coordinate that leaves its declared range at some
  instant is an impossible POSE, and the request that reaches it is refused
  whole and commits nothing — ADR-126's own end-of-request judgement,
  unchanged. Correspondingly a compiled CHAIN may not follow the clock: a
  bounded coordinate, or a coordinate a `Bound` reads, whose chain composes
  down to anything that is not a bank id is refused at simulation
  construction, by name. That closes a latent hole — such a chain reaches
  evaluation today with a free animation symbol and dies with a bare
  `KeyError` — with the refusal ADR-126's own temperament asks for.
- **Refusals, each where its facts are.** A `State` under `Time(loop=)`
  stays refused by name; a `State` under `Time.running()` stays refused with
  its meaning defined and not implemented; every name ADR-125 §9 refuses on
  a clocked `Sim` stays refused except `sim.time` under this base; `time`
  named as a source under any base but the elapsed one is refused at class
  definition, where the declaration that says which base it is was written.
  A body that declares NO base is a different case and is stated honestly: a
  class body does not see `AssemblyNode.time`, so there is no declaration to
  refuse there — the `&` group's LEFT-operand refusal is made symmetric with
  the right-operand one it already raises, which names a stdlib `time`
  MODULE and the clock rule, and a body that binds no `time` at all keeps
  Python's own `NameError`, which this cycle does not pretend to improve.
  Publication is unchanged: it refuses a tree that declares a `State`, which
  is cycle 4's to lift, and an elapsed root with no state publishes the
  document an undeclared root publishes, byte for byte.
- **Zero behaviour change** for every untimed, looping and RUNNING root, as
  in both previous cycles: the existing suite green with no fixture edited
  and no expected value changed, documents byte-identical, the running
  fixtures and `tests/running-corpus.json` untouched, and a tree that
  declares no `State` entering no clocked path.

## Capabilities

### New Capabilities

None. The change gives one existing declaration a third spelling and lets
the bank hold a value it already names.

### Modified Capabilities

- `kinematics`: ONE MODIFIED requirement, "Declared time base" — the third
  spelling, what it means bound and unbound, that every producer reading
  `loop` still reads `None`, and that an elapsed root's document is the
  document an undeclared root publishes.
- `ports`: ONE MODIFIED requirement, "The motion package holds what moves" —
  the module's time channel now carries three bases told apart by `mode`.
- `simulation`: ONE ADDED requirement, "An elapsed clocked root banks its
  clock", stating the bank entry, the request that moves it, events located
  on it, the pose, the bound rules and every refusal; and TWO MODIFIED — "A
  clocked simulation solves a request path event by event", whose bank
  today excludes `time` and whose request today names one declared DRIVER
  and whose refused-name list today includes `time`; and "A state is a value
  the machine writes", whose base refusals today name two bases and must
  name the third as ADMITTED.
- `couplings`: ONE MODIFIED requirement, "A grouped source commits states at
  an event", whose source set today is drivers and states, and whose `&`
  today refuses only its RIGHT operand by name.

## Impact

- `solid_node/motion/ports.py`: the `elapsed()` constructor, `mode`, the
  three-spelling `TypeError`, and the `&`/`commits` faces that let a class
  body name the clock as a source.
- `solid_node/motion/couplings.py`: a clock reference kind beside
  `DriverRef` and `StateRef`, with its class-definition refusals (a driven
  end, a `drives` source, a non-elapsed base); and the reflected `__rand__`
  that makes the group's LEFT-operand refusal the mirror of the
  right-operand one it already raises.
- `solid_node/node/qualified.py` and `solid_node/node/declarative.py`: that
  same reflected face on the declaration kinds that already carry `&`.
- `solid_node/node/qualified.py`: the clock delivered through `drive_tree`'s
  EXISTING `visit` hook — the walk gains no parameter — so a clocked pose
  still renders ONCE.
- `solid_node/simulation/enumeration.py`: `refuse_states_under_a_clock`
  admitting the elapsed base.
- `solid_node/simulation/clocked.py`: the clock in the bank, in the event
  classification, in `move`, in `pose`; the backwards refusal; the chain's
  non-bank free-name refusal.
- `solid_node/simulation/sim.py`: `sim.time` under this base.
- `tests/clocked_project/pendulum.py` (new): the pendulum-and-count fixture
  and its stateless twin; `tests/test_clocked_time.py` (new);
  `tests/test_time_base.py` (added tests only); `docs/scenarios.rst`;
  `HISTORY.rst`.
- One ADR, candidate **ADR-127** (NODE), extracted after implementation.

### Non-goals

Each is named in `design.md` with its reason and the shape a later cycle
takes.

- **Any change to `Time.running()`** — not its compile, not its tick, not
  its document, not its meaning. A `State` under it stays refused with its
  meaning defined (ADR-125), and `Time.elapsed()` is not a way to reach the
  running mechanics.
- **The document and the conformance corpus** (cycle 4); **the viewer's
  clock** (cycles 5 and 6, in `solid-node-viewer`'s own repository).
- **A clip in time**, and a compiled chain that follows the clock. The two
  are one piece of work and arrive together or not at all.
- **A looping root with memory**, and the snapshot-at-each-wrap demo that
  would make it sayable.
- **`time` as the source of a `drives` relation**, an `Instruction` or a
  `move(duration=)` over the clock, and a multi-input request that moves a
  driver and the clock together.
- **A clock in the Curta.** The originating project has none, and this cycle
  invents no reason for it to acquire one.
