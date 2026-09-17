# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""The fixed-dt stepping loop.

One assembly, one step size, one integer tick counter. Everything a
scenario says in seconds is converted to a whole number of ticks the
moment it is said, and rejected there if it is not one: an instant
carried as an accumulating float would drift off the tick it names,
and no assertion scheduled on it would be reproducible. That is
ADR-050's integer-arithmetic reasoning applied to simulation time, and
it is what lets two runs of one scenario be compared with `==`.

Scheduled actions are deferred callables. The ADR sketched
`sim.at(2.5).assertEqual(sim.state['x'], 0)`, which cannot work --
Python evaluates the arguments when the line is registered, so the
assertion would read the state at t=0 and pass or fail for the wrong
instant (spike/FINDINGS.md seam 3). `at(t).run(fn)` hands `fn` the
simulation instead, at the tick it was scheduled for.

Cadence exists because of the cost asymmetry the spike measured: a
bare tick is microseconds while one mesh assertion is milliseconds, so
continuous checking is dominated entirely by the assertions. Ticks are
free; cadence budgets assertion cost. Each slot accounts its own calls
and seconds so a scenario report can say that separately from the cost
of stepping.
"""

import time
from collections import namedtuple

from solid_node.motion.ports import declared_time

from .driver import DriverState
from .enumeration import (qualified_declarations, qualified_drivers,
                          tree_declares_states)
from .timebase import finite_seconds


#: "No dt was given", which `None` cannot say: a clocked root takes no
#: dt at all, and every other root must still be refused for omitting
#: one (OpenSpec change ``declare-the-state``).
_NO_DT = object()


CadenceCost = namedtuple('CadenceCost', 'period_ticks calls seconds')


class _Cadence:
    """One `every()` slot and the cost it has run up so far."""

    __slots__ = ('period_ticks', 'fn', 'args', 'calls', 'seconds')

    def __init__(self, period_ticks, fn, args):
        self.period_ticks = period_ticks
        self.fn = fn
        self.args = args
        self.calls = 0
        self.seconds = 0.0

    def run(self):
        started = time.perf_counter()
        try:
            self.fn(*self.args)
        finally:
            # Accounted even when the action raises: the run stops
            # there, and a scenario report of a failed run should still
            # be able to say what its assertions cost.
            self.seconds += time.perf_counter() - started
            self.calls += 1


class _At:
    """The registrar `at(t)` returns: what to do at one tick.

    A separate object rather than `at(t, action)` so the scenario reads
    as the instant first and the intent second, and so the intent is
    always something to CALL later.
    """

    def __init__(self, sim, tick):
        self._sim = sim
        self._tick = tick

    def trigger(self, name):
        """Trigger the named instruction at this instant."""
        self._add(lambda sim: sim.trigger(name))

    def run(self, fn):
        """Call `fn(sim)` at this instant, after the tick has bound its
        snapshot."""
        self._add(fn)

    def _add(self, action):
        self._sim._at.setdefault(self._tick, []).append(action)


class Sim:
    """A stepped simulation over one assembly at a fixed `dt`.

    Construction enumerates every driver in the node's LINKED TREE and
    binds each one's default through `set_state` by qualified id, so an
    assembly whose render() reads a driver -- including one whose
    drivers live only on its children -- is rendered under a complete
    snapshot from the very first render rather than failing on an
    unbound entry. That is the resolution stage 1 deferred to this
    layer: the framework invents no defaults, the declarations state
    them.

    The bank, the trajectory, the programs and instruction targets all
    key by that same qualified id, so two instances of one mechanism
    step independently and the id a scenario writes is the id the
    serialized document publishes.

    `meshes=True` additionally assembles the node and builds its STLs,
    which is what a scenario asserting on geometry needs and what a
    scenario asserting on state should not pay for. Per-tick re-renders
    never touch the artifact path, so this happens once, here.
    """

    def __init__(self, node, dt=_NO_DT, meshes=False, state=None,
                 record=None):
        # A CLOCKED root -- one whose tree declares a `State` -- takes no
        # `dt`: there is no cadence, and a state moves on requests. The
        # question is answered STRUCTURALLY, before anything is bound,
        # exactly as `tree_declares_drivers` answers its own without
        # rendering, so a `dt` over a clocked root is refused before the
        # tree receives any simulation state binding.
        clocked = tree_declares_states(node)
        if clocked:
            if dt is not _NO_DT:
                raise TypeError(
                    f'Sim({type(node).__name__}, dt={dt!r}) gives a dt '
                    f'over a CLOCKED root: its tree declares a State, so '
                    f'it has no clock and no cadence -- a state moves on '
                    f'requests, and every event on a request path is '
                    f'solved exactly rather than met at a tick. '
                    f'Construct it as Sim(model) and move it with '
                    f'sim.move(input, by=...).')
            dt = None
        else:
            if dt is _NO_DT:
                raise TypeError(
                    f'Sim({type(node).__name__}) gives no dt. A stepped '
                    f'simulation is constructed over one assembly and a '
                    f'fixed dt in seconds; only a CLOCKED root -- one '
                    f'whose tree declares a State -- takes none.')
            dt = finite_seconds(dt, 'dt')
            if dt <= 0:
                raise ValueError(f'dt must be greater than zero, not {dt!r}')
        self.node = node
        self.dt = dt
        self._tick = 0
        self._run = None
        self._clocked = None
        base = declared_time(type(node))
        if base is not None and base.mode == 'running':
            # ONE simulation owns a tree at a time, and the NEWEST takes
            # it. A previous run's claim is released BEFORE the FIRST
            # enumeration of this construction, so every walk below finds
            # a tree no run owns and poses it exactly as it would a tree
            # no run ever touched -- which is what makes
            # `ScenarioTest.simulation()`'s "fresh per call" true over a
            # node built once per class. The released run then refuses to
            # advance rather than binding over this one.
            #
            # The BLOCK PRE-PASS follows it, and must: the driver walk
            # below is itself an enumeration, and a dependency cycle
            # every selection breaks is refused THERE -- `DoublyBound`
            # where its driven ends carry rest guards and
            # `UnreachedCoordinate` where they do not -- long before any
            # compile is reached (OpenSpec change ``select-the-source``,
            # design.md section 5).
            from .program import _block_members, release_tree

            release_tree(node)
            _block_members(node)
        # Enumerated across the WHOLE linked tree, not off the root
        # class: a machine's drivers live on its mechanisms, and a
        # machine whose root declares none would otherwise get an empty
        # bank and fail on its own first render. The bank is keyed by
        # the same qualified ids the serialized document publishes,
        # because both come from this one authority.
        self.drivers = {identifier: DriverState(identifier, declaration)
                        for identifier, declaration
                        in qualified_drivers(node).items()}
        # After the declaration walk, not before: `qualified_declarations`
        # is another `drive_tree`, and it rebinds every declared default
        # as it descends. The rest render below has to be the LAST thing
        # that poses the tree before the run reads its coordinates off it.
        # ONE walk returns both tables, because this is the caller that
        # needs both and `drive_tree`'s `visit` exists to save the second
        # descent.
        self.instructions, self.controls, self.states = \
            qualified_declarations(node)
        self._trajectory = []
        self._at = {}
        self._every = []
        if self.controls and not (base is not None
                                  and base.mode == 'running'):
            _refuse_control_without_a_run(node, self.controls)
        if clocked:
            # The clocked executor is imported HERE, and nowhere else: a
            # model that declares no State never loads it, exactly as a
            # model that declares no running time never loads the run.
            from .clocked import Clocked

            self._clocked = Clocked(
                self, node,
                {identifier: driver.declaration
                 for identifier, driver in self.drivers.items()},
                self.states, self.instructions, state=state, record=record)
            if meshes:
                node.assemble()
                node.build_stls()
            return
        self._bind_initial(state)
        if base is not None and base.mode == 'running':
            # The running engine and the compile step are imported HERE,
            # and nowhere else: a model that declares no running time
            # never loads either (capability `cli-startup-cost`). The
            # construction that follows is design.md section 4 -- the
            # untimed rest render above, the bank read off the tree, the
            # program compiled from what that render solved, the initial
            # snapshot, and then the run's own binding of the whole bank.
            from .run import Run

            self._run = Run(self, record)
        if meshes:
            node.assemble()
            node.build_stls()

    def _bind_initial(self, state):
        """Bind the declared defaults, overridden by `state=`, and render
        once: the untimed rest pose every simulation starts from.

        A name in `state` that is not a declared driver id is refused
        here rather than delivered: a joint coordinate id among them is
        refused too, because under a running root the initial
        coordinates come from the rest pose and nowhere else.
        """
        for identifier, value in (state or {}).items():
            try:
                self.drivers[identifier].value = value
            except KeyError:
                known = ', '.join(sorted(self.drivers)) or 'none'
                raise ValueError(
                    f"state={{'{identifier}': ...}} names no declared "
                    f'driver of {type(self.node).__name__}. An initial '
                    f'state names a driver by its qualified id -- a joint '
                    f"coordinate's initial value comes from the rest pose "
                    f'the declared drivers produce, never from here; '
                    f'declared: {known}.') from None
        self.node.set_state(**self._binding())

    @property
    def running(self):
        """Whether this simulation's root declares `Time.running()`, and
        the run therefore owns its coordinates."""
        return self._run is not None

    @property
    def clocked(self):
        """Whether this simulation's tree declares a `State`, and a
        request therefore solves its own events."""
        return self._clocked is not None

    @property
    def tick(self):
        """The integer tick this simulation stands at.

        Refused over a CLOCKED root: there is no cadence to count, and a
        state moves on requests.
        """
        self._not_clocked('tick')
        return self._tick

    @tick.setter
    def tick(self, value):
        self._tick = value

    def _not_clocked(self, what):
        """Refuse `what` over a clocked root, by name."""
        if self._clocked is None:
            return
        raise TypeError(
            f'{what} belongs to a simulation with a CLOCK, and '
            f'{type(self.node).__name__} is CLOCKED: its tree declares a '
            f'State, it declares no time base, and it has no cadence. A '
            f'clocked model moves on requests -- sim.move(input, by=...) '
            f'-- and every event on a request path is solved exactly. '
            f'Read sim.state, sim.commits and the request move() returns.')

    def _running(self, what):
        self._not_clocked(what)
        if self._run is None:
            raise TypeError(
                f'{what} belongs to a RUNNING simulation, and '
                f'{type(self.node).__name__} declares no time base or a '
                f'looping one. Declare time = Time.running() on the root '
                f'to have the simulation own its coordinates, retain their '
                f'history and take commands.')
        return self._run

    ##############################################
    # The running surface

    def move(self, input_id, by=None, to=None, duration=None):
        """Move a declared input BY a travel or TO a value.

        Under a RUNNING root the move takes `duration` seconds and
        returns the handle reporting what the run admits. Under a
        CLOCKED root it is a REQUEST: a straight path from where the
        input stands to where it is asked for, with every rising event
        on it solved and committed in path order, and no duration at all
        -- a state moves on requests, not on a clock.
        """
        if self._clocked is not None:
            if duration is not None:
                raise TypeError(
                    f"move('{input_id}', duration={duration!r}) gives a "
                    f'duration over a CLOCKED root, which has no clock '
                    f'to spend it on. A request is a straight path from '
                    f'where the input stands to where it is asked for; '
                    f'drop the duration.')
            return self._clocked.move(input_id, by=by, to=to)
        return self._running('move()').move(input_id, by=by, to=to,
                                            duration=duration)

    @property
    def commits(self):
        """The bounded ring of committed events `record=` asked for, and
        `()` when it asked for none. A request's own result is complete
        either way."""
        if self._clocked is not None:
            return self._clocked.commits
        return self._running('commits').commits

    def rate(self, input_id, rate):
        """Run a declared input at `rate` design units per simulated
        second until released with `rate(input, 0)`."""
        return self._running('rate()').rate(input_id, rate)

    @property
    def commands(self):
        """The handles of the commands currently owning an input."""
        return self._running('commands').commands

    @property
    def program(self):
        """The compiled program the run integrates."""
        return self._running('program').program

    @property
    def initial(self):
        """The snapshot taken at construction: the rest pose."""
        if self._clocked is not None:
            return self._clocked.initial
        return self._running('initial').initial

    def snapshot(self):
        """This simulation's whole state as a value object."""
        if self._clocked is not None:
            return self._clocked.snapshot()
        return self._running('snapshot()').snapshot()

    def restore(self, snapshot):
        """Put this simulation back to `snapshot`, refusing one taken
        over a different model before touching anything."""
        if self._clocked is not None:
            return self._clocked.restore(snapshot)
        return self._running('restore()').restore(snapshot)

    def reset(self):
        """Restore the initial snapshot."""
        if self._clocked is not None:
            return self._clocked.reset()
        return self._running('reset()').reset()

    @property
    def state(self):
        """The current snapshot by qualified id: a fresh dict, so a
        caller holding one holds a value and not a view of the running
        simulation.

        Under a RUNNING root that is the run's whole bank -- every driver
        AND every joint coordinate of the linked tree -- because under
        that base the coordinates are the state. Under a CLOCKED root it
        is every driver AND every state, and `time` is deliberately not
        in it: a clocked root declares no time base. Under any other
        root it is the driver bank, exactly as it always was."""
        if self._clocked is not None:
            return self._clocked.state
        if self._run is not None:
            return self._run.state
        return {name: driver.value
                for name, driver in sorted(self.drivers.items())}

    @property
    def trajectory(self):
        """What was recorded, oldest first.

        Under a running root that is the bounded ring `record=` asked
        for, and `[]` when it asked for none; under any other root the
        list every tick is appended to, as before."""
        if self._run is not None:
            return self._run.trajectory
        return self._trajectory

    @property
    def crossings(self):
        """Every jump surface met inside a tick, oldest first.

        The bounded ring `record=` asked for, and `[]` when it asked for
        none: each entry names the tick, the relation as written, the
        driven coordinate, the primitive that jumped, the surface it
        reached and the fraction of the tick at which it did.
        """
        return self._running('crossings').crossings

    @property
    def stops(self):
        """Every declared bound reached, oldest first.

        The bounded ring `record=` asked for, and `[]` when it asked for
        none. Under a RUNNING root each entry names the tick, the
        coordinate that stopped, which bound it reached and that bound's
        evaluated value, the fraction of the tick at which it was
        reached, and the inputs the stop blocked.

        Under a CLOCKED root it is the bounds requests stopped at, beside
        `sim.commits`: a clocked model has no clock, but it does have
        STOPS, and a reader counting strokes must not have to filter out
        interlocks (OpenSpec change ``a-bound-stops-the-request``, design
        section 11).
        """
        if self._clocked is not None:
            return self._clocked.stops
        return self._running('stops').stops

    @property
    def time(self):
        """The exact instant this simulation stands at, in seconds.

        Computed from the integer tick count on every access, never
        accumulated: `k*dt` is a fixed point, and a float advanced by
        `+= dt` drifts off the instant a scenario names (ADR-050's
        reasoning applied to simulation time).
        """
        self._not_clocked('time')
        return self._tick * self.dt

    def _binding(self):
        """The full snapshot as `set_state` takes it: every driver by
        qualified id, plus the one global entry.

        `time` is a driver like the rest, and under a simulation it is
        this clock in SECONDS -- a machine executing instructions has no
        period to normalize against, so the 0..1 `$t` timeline ADR-008
        provides is the wrong thing to bind here. Outside a simulation
        that path is untouched.
        """
        return dict(self.state, time=self.time)

    @property
    def cadence_costs(self):
        """What each cadence slot has cost so far, in declaration
        order: a scenario report states assertion cost per slot."""
        return tuple(CadenceCost(slot.period_ticks, slot.calls, slot.seconds)
                     for slot in self._every)

    @property
    def assertion_stats(self):
        """(calls, mean seconds per call) across every cadence slot."""
        calls = sum(slot.calls for slot in self._every)
        seconds = sum(slot.seconds for slot in self._every)
        return calls, (seconds / calls if calls else 0.0)

    def at(self, t):
        """The registrar for instant `t`, in seconds."""
        self._not_clocked('at()')
        tick = self._ticks(t, 'instant')
        if tick < self._tick:
            raise ValueError(
                f'instant {t} is before current simulation time '
                f'{self.time} (tick {self._tick})')
        return _At(self, tick)

    def every(self, period, fn, *args):
        """Call `fn(*args)` every `period` seconds of simulated time.

        The arguments are bound now and the call deferred, which is
        exactly right for an assertion whose subject is a node: the
        node is the same object at every tick, and what changes is the
        snapshot bound into it.
        """
        self._not_clocked('every()')
        ticks = self._ticks(period, 'period')
        if ticks < 1:
            # A cadence of no ticks is the one thing this cannot mean:
            # "every tick" is period == dt, and the loop would divide
            # by zero rather than say so.
            raise ValueError(
                f'period {period} is shorter than one dt={self.dt} tick')
        self._every.append(_Cadence(ticks, fn, args))

    def trigger(self, name):
        """Start the named instruction's ramps at the current tick.

        `name` is qualified the same way a driver id is: an instruction
        declared on a child is `x_axis.Home`, one declared on the root
        keeps its bare name. Its targets are class-local, so they
        resolve against the declaring node's own path -- which is what
        makes "home the X axis" home only the X axis.
        """
        self._not_clocked('trigger()')
        path, instruction = self._instruction(name)
        if self._run is not None:
            # Under a running root an instruction is the run's own
            # command: `targets=` a move TO each target, `by=` a move BY
            # each travel, every input claimed before any of them starts.
            return self._run.trigger(path, instruction, name)
        ticks = self._ticks(instruction.duration,
                            f"duration of instruction '{name}'")
        for driver_name, amount in (instruction.targets
                                    or instruction.by).items():
            driver = self._driver('.'.join(path + (driver_name,)), name)
            native = driver.declaration.native(amount)
            if instruction.relative:
                # A relative instruction ramps from where the driver
                # stands, which is well defined over a driver bank under
                # every time base.
                native = driver.value + native
            driver.ramp_to(native, ticks, self._tick)
        if ticks == 0:
            # A zero-tick ramp is complete at the trigger instant. Rebind
            # once after every target has settled so the node sees one
            # complete, internally consistent snapshot.
            self.node.set_state(**self._binding())

    def run(self, duration):
        """Step for `duration` seconds of simulated time.

        Actions already due at the current tick run first, so a
        scenario opening with `at(0.0).trigger(...)` takes effect on
        the first tick rather than one tick late. Then each tick
        advances every program, binds the whole snapshot, records it,
        and only then runs what was scheduled -- an action must see the
        state its tick produced, never the one before it.
        """
        self._not_clocked('run()')
        duration = finite_seconds(duration, 'duration')
        if duration < 0:
            raise ValueError(
                f'duration must be non-negative, not {duration!r}')
        end = self._tick + self._ticks(duration, 'duration')
        self._fire(self._tick)
        while self._tick < end:
            if self._run is not None:
                # One tick of design.md section 7: the increments the
                # active commands admit, propagated over the compiled
                # program, committed only once nothing refused them, and
                # bound as the run.
                self._run.advance()
            else:
                self._tick += 1
                states = {name: driver.advance(self._tick)
                          for name, driver in sorted(self.drivers.items())}
                self.node.set_state(**dict(states, time=self.time))
                self._trajectory.append((self._tick, states))
            self._fire(self._tick)
            for slot in self._every:
                if self._tick % slot.period_ticks == 0:
                    slot.run()

    def _fire(self, tick):
        for action in self._at.pop(tick, []):
            action(self)

    def _ticks(self, value, what):
        value = finite_seconds(value, what)
        count = round(value / self.dt)
        if abs(count * self.dt - value) > 1e-9:
            raise ValueError(
                f'{what} {value} is not a whole number of dt={self.dt} ticks')
        return count

    def _instruction(self, name):
        try:
            _, path, instruction = self.instructions[name]
        except KeyError:
            known = ', '.join(sorted(self.instructions)) or 'none'
            raise KeyError(f"no instruction '{name}' declared anywhere in "
                           f'{type(self.node).__name__}; declared: '
                           f'{known}') from None
        return path, instruction

    def _driver(self, name, instruction_name):
        try:
            return self.drivers[name]
        except KeyError:
            known = ', '.join(sorted(self.drivers)) or 'none'
            raise KeyError(f"instruction '{instruction_name}' targets driver "
                           f"'{name}', which nothing in "
                           f'{type(self.node).__name__} declares; declared: '
                           f'{known}') from None


def _refuse_control_without_a_run(node, controls):
    """A control belongs to a RUNNING root, refused by name.

    A control issues a movement request, and `trigger`, `move` and
    `rate` -- the three the run accepts -- exist only under
    `Time.running()`. An untimed root's `trigger` exists too, but posing
    the pressed part from a target ramp is a different chrome and is out
    of scope in this release, so the declaration is refused rather than
    published as something a consumer cannot act on. The other place
    this is refused is `serializer.symbolic_document`'s own walk, which
    every publication passes through.
    """
    name = sorted(controls)[0]
    declaring, _path, _control = controls[name]
    raise TypeError(
        f"{type(declaring).__name__} declares the control '{name}', and "
        f"{type(node).__name__} declares no running time base. A control "
        f"is how a person issues a movement request, and only a running "
        f"simulation takes one: declare time = Time.running() on the root, "
        f"or drop the control.")
