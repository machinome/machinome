# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A clock without a run: `Time.elapsed()`, the banked clock, the
request that moves it and the events located on it.

The OpenSpec change ``time-without-running``, whose square of ADR-125's
two-axis table is `elapsed x memory`: a machine with a clock and memory
and no integration. `Time.running()` is untouched by every line of it.

The fixtures are `tests/clocked_project/pendulum.py`; every expected
value here is computed BY HAND from the constants that module declares.
The originating project of the clocked discipline,
`projects/Calculators/Curta-Type-I-3x`, has NO clock and is not
exercised by this cycle.
"""

import json
import math

from solid_node.motion.joints import JointRangeError
from solid_node.motion.ports import Time
from solid_node.scad_expression import GraphValue
from solid_node.simulation import Sim
from solid_node.simulation import clocked as clocked_module
from solid_node.simulation.clocked import ClockedError

from .base import BaseNodeTest
from .clocked_project.pendulum import (A, DIGIT, FIRST, QUARTER, STROKE, T,
                                       Clockless, Regulator, Swing, Untimed)


def releases(count, first=FIRST, period=T / 2):
    """The first `count` release instants, BY HAND: a quarter period in,
    and every half period after that."""
    return [first + index * period for index in range(count)]


def assert_releases(case, commits, count):
    """The landings of `commits` ARE the first `count` release instants,
    each to within ONE representable value.

    The landing is ADR-125's, unchanged: the nearest representable value
    on the FAR side of the surface, with membership decided by
    EVALUATING the level's own branch and never by comparing a float to
    the surface. The level `floor((t + T/4) / (T/2))` adds a quarter
    period before it divides, and at the first release that addition
    ROUNDS UP to the surface one representable value early -- so the
    landing is the float just below 0.5 rather than 0.5 itself. That is
    the exactness rule working as stated and not a tolerance: the
    instants are the hand-computed ones, and the assertion names the one
    ulp the level's own arithmetic puts them at (evidence.md, "The
    landing of a release").
    """
    case.assertEqual(len(commits), count)
    for commit, ideal in zip(commits, releases(count)):
        case.assertLessEqual(abs(commit.value - ideal), math.ulp(ideal),
                             f'{commit.value!r} is not the landing of the '
                             f'release at {ideal!r}')


class StatelessElapsedTest(BaseNodeTest):
    """Tasks 2.3 and 2.4: an elapsed root that declares NO state is
    admitted and EQUIVALENT -- the same stepping simulation, the same
    reads, the same published bytes, and no clocked code path."""

    def test_the_stepping_simulation_runs_over_it(self):
        sim = Sim(Swing(), 0.1)
        self.assertFalse(sim.clocked)
        self.assertFalse(sim.running)
        self.assertEqual(sim.time, 0.0)
        sim.run(0.5)
        self.assertEqual(sim.tick, 5)
        self.assertAlmostEqual(sim.time, 0.5)

    def test_each_step_binds_the_seconds_the_tree_reads(self):
        sim = Sim(Swing(), 0.5)
        sim.run(0.5)
        # One tick of half a second: the bob stands where the formula
        # puts it at t = 0.5, which is a quarter period of T = 2.
        self.assertAlmostEqual(sim.node.bob.swing.value, A)

    def test_unbound_time_is_bare_t_and_a_keyframe_binds_a_number(self):
        node = Swing()
        node.assemble()
        self.assertEqual(str(node.time), '$t')
        node.set_keyframe(T / 4)
        self.assertEqual(node.time, T / 4)
        self.assertAlmostEqual(node.bob.swing.value, A)
        node.clear_keyframe()
        self.assertEqual(str(node.time), '$t')

    def _body(self, node):
        from solid_node.core.serializer import (document_body, drivers_table,
                                                serialize_node,
                                                symbolic_document)

        with symbolic_document(node) as (declarations, instructions):
            root = serialize_node(node, lambda rigid: 'parts/bob.stl')
            drivers = drivers_table(declarations)
        return document_body(node, root, drivers, {})

    def test_the_published_document_is_byte_identical_to_an_undeclared_root(
            self):
        declared = self._body(Swing())
        undeclared = self._body(Untimed())
        self.assertEqual(json.dumps(declared, sort_keys=True),
                         json.dumps(undeclared, sort_keys=True))
        self.assertNotIn('loop', declared['animation'])

    def test_no_clocked_code_path_is_entered_for_a_stateless_elapsed_root(
            self):
        before = clocked_module.entered()
        node = Swing()
        node.set_state(engaged=1, time=0.0)
        node.render()
        sim = Sim(node, 0.02)
        sim.run(0.1)
        self._body(Swing())
        self.assertEqual(clocked_module.entered(), before)


class BankTest(BaseNodeTest):
    """Task 3: the clock is a banked value of an elapsed CLOCKED
    simulation (design section 3)."""

    def test_the_clock_is_in_the_bank_at_zero(self):
        sim = Sim(Regulator())
        self.assertEqual(sim.state, {'count': 0, 'engaged': 1,
                                     'time': 0.0})
        self.assertEqual(sim.time, 0.0)

    def test_state_opens_the_session_at_an_instant(self):
        sim = Sim(Regulator(), state={'time': 4.0, 'count': 3})
        self.assertEqual(sim.time, 4.0)
        self.assertEqual(sim.state['count'], 3)

    def test_snapshot_and_restore_carry_the_instant(self):
        sim = Sim(Regulator())
        sim.move('time', by=T)
        saved = sim.snapshot()
        held = sim.state
        sim.move('time', by=T)
        self.assertNotEqual(sim.state, held)
        sim.restore(saved)
        self.assertEqual(sim.state, held)
        self.assertEqual(sim.time, T)

    def test_reset_returns_the_clock_to_zero(self):
        sim = Sim(Regulator())
        sim.move('time', by=3 * T)
        sim.reset()
        self.assertEqual(sim.state, {'count': 0, 'engaged': 1, 'time': 0.0})

    def test_a_clocked_root_with_no_base_has_no_clock_in_its_bank(self):
        sim = Sim(Clockless())
        self.assertNotIn('time', sim.state)
        with self.assertRaises(TypeError) as caught:
            sim.time
        message = str(caught.exception)
        self.assertIn('time', message)
        self.assertIn('CLOCKED', message)
        self.assertIn('Time.elapsed()', message)

    def test_a_root_declared_driver_named_time_is_refused(self):
        """The no-collision claim, ASSERTED: a bare bank id belongs only
        to a root-declared driver or state, and one named `time` never
        reaches the bank at all."""
        from solid_node.node import AssemblyNode
        from solid_node.simulation import Driver

        with self.assertRaises(TypeError) as caught:
            class Colliding(AssemblyNode):
                time = Driver(default=0.0)
        self.assertIn('time', str(caught.exception))


class PoseDeliveryTest(BaseNodeTest):
    """Task 3.4: the clock is delivered in the ONE walk that poses the
    tree, through the hook that walk already has."""

    def _walks(self, call):
        """Every `drive_tree` the clocked executor enters while `call`
        runs, as the `visit` each was given.

        `drive_tree` renders the tree ONCE at the end, so one walk is
        one pose: counting the walks is counting the renders.
        """
        from unittest.mock import patch

        real = clocked_module.drive_tree
        seen = []

        def counted(root, resolve, visit=None, collected=None):
            seen.append(visit)
            return real(root, resolve, visit=visit, collected=collected)

        with patch.object(clocked_module, 'drive_tree', counted):
            call()
        return seen

    def test_one_request_poses_the_tree_once(self):
        sim = Sim(Regulator())
        walks = self._walks(lambda: sim.move('time', by=10 * T))
        self.assertEqual(len(walks), 1)
        self.assertIsNotNone(walks[0])

    def test_a_model_with_no_clock_enters_the_walk_with_no_visit(self):
        sim = Sim(Clockless())
        walks = self._walks(lambda: sim.move('crank', by=360.0))
        self.assertEqual(walks, [None])

    def test_a_descendant_reads_the_banked_seconds(self):
        from .clocked_project.pendulum import Nested

        sim = Sim(Nested())
        sim.move('time', by=T / 4)
        self.assertEqual(sim.node.arm.time, T / 4)
        self.assertAlmostEqual(sim.node.arm.tip.swing.value, A)

    def test_the_pose_follows_the_clock_and_the_build_path_reads_t(self):
        node = Regulator()
        sim = Sim(node)
        sim.move('time', by=3 * T / 4)
        self.assertEqual(sim.time, 3 * T / 4)
        # BY HAND: 3T/4 is three quarters of a period, where the swing
        # stands at -A.
        self.assertAlmostEqual(node.bob.swing.value, -A)
        # The same tree rendered outside any simulation reads `$t`.
        outside = Regulator()
        outside.assemble()
        self.assertEqual(str(outside.time), '$t')
        self.assertIsInstance(outside.bob.swing.value, GraphValue)
        # And it is the expression the STATELESS twin carries, so a
        # geometry that is a formula of time animates in the untimed
        # preview exactly as it does today.
        twin = Swing()
        twin.assemble()
        self.assertEqual(str(outside.bob.swing.value),
                         str(twin.bob.swing.value))


class RequestTest(BaseNodeTest):
    """Task 4: the request that moves the clock -- the SAME verb, the
    same value object, seconds in and seconds out (design section 4)."""

    def test_by_and_to_move_the_clock_in_seconds(self):
        sim = Sim(Regulator())
        made = sim.move('time', by=T)
        self.assertEqual(made.input, 'time')
        self.assertEqual(made.by, T)
        self.assertEqual(made.admitted, T)
        self.assertEqual(made.stops, ())
        self.assertEqual(sim.time, T)
        made = sim.move('time', to=3 * T)
        self.assertEqual(made.admitted, 2 * T)
        self.assertEqual(sim.time, 3 * T)

    def test_a_negative_request_is_refused_naming_both_instants(self):
        sim = Sim(Regulator())
        sim.move('time', by=T)
        before = sim.state
        posed = sim.node.bob.swing.value
        with self.assertRaises(ValueError) as caught:
            sim.move('time', by=-1.0)
        message = str(caught.exception)
        self.assertIn(repr(T), message)
        self.assertIn('BACKWARDS', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.bob.swing.value, posed)

    def test_a_to_behind_the_bank_is_refused(self):
        sim = Sim(Regulator())
        sim.move('time', by=3 * T)
        before = sim.state
        with self.assertRaises(ValueError) as caught:
            sim.move('time', to=T)
        message = str(caught.exception)
        self.assertIn(repr(3 * T), message)
        self.assertIn(repr(T), message)
        self.assertEqual(sim.state, before)

    def test_zero_is_admitted_and_commits_nothing(self):
        sim = Sim(Regulator())
        sim.move('time', by=T)
        held = sim.state
        made = sim.move('time', by=0)
        self.assertEqual(made.admitted, 0.0)
        self.assertEqual(made.commits, ())
        self.assertEqual(sim.state, held)
        # `to=` the banked instant is the same request.
        made = sim.move('time', to=T)
        self.assertEqual(made.admitted, 0.0)
        self.assertEqual(made.commits, ())

    def test_a_request_on_a_clocked_root_with_no_base_is_refused(self):
        sim = Sim(Clockless())
        with self.assertRaises(ValueError) as caught:
            sim.move('time', by=1.0)
        self.assertIn('Time.elapsed()', str(caught.exception))

    def test_a_request_naming_a_state_or_a_coordinate_is_refused(self):
        sim = Sim(Regulator())
        with self.assertRaises(ValueError) as caught:
            sim.move('count', by=1)
        self.assertIn('State', str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            sim.move('bob.swing', by=1.0)
        self.assertIn('bob.swing', str(caught.exception))

    def test_both_by_and_to_are_refused_on_the_clock(self):
        sim = Sim(Regulator())
        with self.assertRaises(ValueError) as caught:
            sim.move('time', by=1.0, to=2.0)
        self.assertIn('exactly one', str(caught.exception))


class EventsOnTheClockTest(BaseNodeTest):
    """Task 5: events on time are EVENTS -- ADR-125's solver, its
    ordering, its conflict rule and its exactness, unchanged."""

    def test_one_request_fires_the_releases_on_its_path(self):
        sim = Sim(Regulator(), record=8)
        made = sim.move('time', by=T)
        # BY HAND: the level rises at t = T/4 and every T/2 after it, so
        # one period holds exactly two releases, at 0.5 and 1.5 seconds.
        assert_releases(self, made.commits, 2)
        self.assertEqual(sim.state['count'], 2)
        self.assertEqual(sim.time, T)
        self.assertEqual([commit.targets for commit in made.commits],
                         [{'count': 1}, {'count': 2}])

    def test_a_long_request_fires_every_release_in_path_order(self):
        """Design section 5 says `by=40*T` fires forty events; the level
        it states rises TWICE per period, so the same request fires
        EIGHTY. The instants are the hand-computed ones either way, and
        the discrepancy is recorded in `evidence.md` under "Design
        questions" rather than papered over."""
        sim = Sim(Regulator())
        made = sim.move('time', by=40 * T)
        assert_releases(self, made.commits, 80)
        self.assertEqual(sim.state['count'], 80)
        self.assertEqual(sim.time, 40 * T)
        # And the forty the scenario names is the request that covers
        # forty half swings.
        again = Sim(Regulator())
        forty = again.move('time', by=20 * T)
        assert_releases(self, forty.commits, 40)
        self.assertEqual(again.state['count'], 40)

    def test_ten_short_requests_equal_one_long_one(self):
        long_one = Sim(Regulator())
        made = long_one.move('time', by=10 * T)
        short = Sim(Regulator())
        instants = []
        for _index in range(10):
            instants.extend(commit.value
                            for commit in short.move('time', by=T).commits)
        self.assertEqual(short.state, long_one.state)
        self.assertEqual(instants, [commit.value for commit in made.commits])

    def test_a_driver_request_at_a_standing_clock_fires_nothing(self):
        sim = Sim(Regulator())
        made = sim.move('engaged', to=0)
        self.assertEqual(made.commits, ())
        self.assertEqual(sim.time, 0.0)
        self.assertEqual(sim.state['count'], 0)
        # And a time request over the disengaged escapement commits the
        # count the law gives: count + 0, held.
        after = sim.move('time', by=T)
        self.assertEqual(len(after.commits), 2)
        self.assertEqual(sim.state['count'], 0)

    def test_a_relation_the_clock_alone_moves_is_admitted(self):
        from .clocked_project.pendulum import ClockAlone

        sim = Sim(ClockAlone())
        made = sim.move('time', by=T)
        assert_releases(self, made.commits, 2)
        self.assertEqual(sim.state['count'], 2)

    def test_a_curved_level_in_the_clock_is_refused_at_construction(self):
        from .clocked_project.pendulum import Curved

        with self.assertRaises(ClockedError) as caught:
            Sim(Curved())
        message = str(caught.exception)
        self.assertIn('time', message)
        self.assertIn('sin', message)
        self.assertIn('SOLVED', message)

    def test_a_request_crossing_the_maximum_is_refused(self):
        sim = Sim(Regulator())
        with self.assertRaises(ClockedError) as caught:
            # BY HAND: one release every second, so 1001 seconds crosses
            # one more surface than the framework admits on one request.
            sim.move('time', by=1001.0)
        message = str(caught.exception)
        self.assertIn('1000', message)
        self.assertIn('1001.0', message)
        self.assertIn('Split it', message)
        self.assertEqual(sim.state, {'count': 0, 'engaged': 1, 'time': 0.0})

    def test_no_tolerance_is_introduced_on_the_clock(self):
        """Design section 5: a pendulum's release is AFFINE in time, so
        nothing here needs a searched crossing, and this cycle did not
        give the clocked path a tolerance.

        `publish-the-clocked-machine` (design section 9) CORRECTED what
        this test used to assert. "Introduces no NEW use" and "reaches
        none" are different claims and only the first is true: a KINKED
        event level's crossings are merged by `_deduplicated` and a
        jumped constraint level's cuts are folded by `JumpPlan.cuts`,
        both inside the SHARED locator, both by that constant. So the
        module now NAMES it -- to PUBLISH it as `clocked.limits`, so a
        consumer cannot silently differ from the producer -- and names
        it in no other place: the import and the published object, and
        nothing on the request path.
        """
        import inspect

        source = inspect.getsource(clocked_module)
        lines = [line.strip() for line in source.splitlines()
                 if '_CROSSING_TOLERANCE' in line
                 and not line.strip().startswith('#')]
        self.assertEqual(
            lines,
            ["from .program import (JumpPlan, TooManyCrossings, "
             "_CROSSING_TOLERANCE,",
             "'limits': {'crossing_tolerance': _CROSSING_TOLERANCE,"])


class ClockAsASourceTest(BaseNodeTest):
    """Tasks 5.1 and 5.2: where the clock may be NAMED, and what each
    refusal says (design section 5)."""

    def test_the_clock_is_a_source_beside_a_driver_and_a_state(self):
        from solid_node.motion.couplings import declared_commitments

        commitments = declared_commitments(Regulator)
        self.assertEqual(len(commitments), 1)
        sources = [ref.described()
                   for ref in commitments[0].source_refs()]
        self.assertEqual(sources, ['time', 'engaged', 'count'])

    def test_both_factories_are_called_once_with_the_realized_owners(self):
        seen = []

        def watching(sources, targets):
            seen.append((sources, targets))
            return lambda time, engaged, count: count + 1

        from solid_node.math import floor
        from solid_node.node import AssemblyNode
        from solid_node.simulation import Driver, State

        class Watched(AssemblyNode):
            time = Time.elapsed()
            engaged = Driver(default=1, dtype=int)
            count = State(default=0, dtype=int)

            (time & engaged & count).commits(
                count,
                at=lambda sources, targets:
                    (lambda time, engaged, count: floor(time)),
                law=watching)

        node = Watched()
        Sim(node)
        self.assertEqual(len(seen), 1)
        sources, targets = seen[0]
        # Three owners in written order: the clock's owner is the root
        # that declares it, as a root-declared driver's and state's are.
        self.assertEqual([id(owner) for owner in sources],
                         [id(node), id(node), id(node)])
        self.assertIs(targets, node)

    def test_the_law_receives_the_seconds_positionally(self):
        sim = Sim(Regulator())
        sim.move('time', by=T)
        # The law is `count + engaged`, and `engaged` stands at one, so
        # a count of two is the two releases read in written order.
        self.assertEqual(sim.state['count'], 2)

    def test_the_clock_under_another_base_is_refused_at_class_definition(
            self):
        from solid_node.math import floor
        from solid_node.node import AssemblyNode
        from solid_node.simulation import Driver, State

        def level(sources, targets):
            return lambda time, count: floor(time)

        def law(sources, targets):
            return lambda time, count: count + 1

        for spelling, base in (('Time(loop=', Time(loop=4)),
                               ('Time.running()', Time.running())):
            with self.subTest(base=spelling):
                with self.assertRaises(TypeError) as caught:
                    class Mistimed(AssemblyNode):
                        time = base
                        count = State(default=0, dtype=int)

                        (time & count).commits(count, at=level, law=law)
                message = str(caught.exception)
                self.assertIn(spelling, message)
                self.assertIn('Time.elapsed()', message)
                self.assertIn('NEVER WRAPS', message)

    def test_the_clock_is_refused_as_a_target_and_as_either_end_of_drives(
            self):
        from solid_node.math import floor
        from solid_node.motion.joints import Revolute
        from solid_node.node import AssemblyNode, Solid2Node
        from solid_node.simulation import Driver, State
        from solid2 import cube

        class Face(Solid2Node):
            turn = Revolute(axis=(0, 0, 1), unit='deg')

            def render(self):
                return cube(1)

        def level(sources, targets):
            return lambda time, count: floor(time)

        def law(sources, targets):
            return lambda time, count: count + 1

        with self.assertRaises(TypeError) as caught:
            class Written(AssemblyNode):
                time = Time.elapsed()
                count = State(default=0, dtype=int)

                (time & count).commits(time, at=level, law=law)
        self.assertIn('CLOCK', str(caught.exception))

        with self.assertRaises(TypeError) as caught:
            class Driving(AssemblyNode):
                time = Time.elapsed()
                count = State(default=0, dtype=int)
                face = Face()

                time.drives(face.turn)
        self.assertIn('clock', str(caught.exception))

        with self.assertRaises(TypeError) as caught:
            class Driven(AssemblyNode):
                time = Time.elapsed()
                engaged = Driver(default=1, dtype=int)

                engaged.drives(time)
        self.assertIn('clock', str(caught.exception))

    def test_a_body_that_declares_no_base_names_the_module(self):
        """Design section 5, case 2: a class body does not see
        `AssemblyNode.time`, so `time` is the MODULE the file imported
        and the reflected `&` is what can refuse it."""
        from .clocked_project import module_clock

        with self.assertRaises(TypeError) as caught:
            module_clock.stated()
        message = str(caught.exception)
        self.assertIn('module', message)
        self.assertIn('group is a group of coordinates', message)
        self.assertIn('Time.elapsed()', message)

    def test_a_body_that_binds_no_time_gets_pythons_own_answer(self):
        """Design section 5, case 3: the blind spot, RECORDED. The name
        fails before an operator is reached, and this change promises no
        message of its own there."""
        from .clocked_project import bare_clock

        with self.assertRaises(NameError) as caught:
            bare_clock.stated()
        self.assertIn('time', str(caught.exception))

    def test_a_group_of_coordinates_is_admitted_unchanged(self):
        """The reflected `&` is reached only where the left operand
        carries no `&` of its own, so no admitted group changes."""
        from solid_node.motion.couplings import Coordinates
        from solid_node.node.qualified import declared_drivers_of
        from .clocked_project.counter import Counter

        crank = declared_drivers_of(Counter)['crank']
        units = declared_drivers_of(Counter)
        group = crank & Counter.__dict__['units']
        self.assertIsInstance(group, Coordinates)
        self.assertEqual(len(group.operands), 2)
        # And a foreign left operand IS refused, by name.
        with self.assertRaises(TypeError) as caught:
            4 & crank
        self.assertIn('not a coordinate', str(caught.exception))


class ProducerTest(BaseNodeTest):
    """Task 6.2: no document producer is touched by the elapsed base.

    NO headless browser anywhere: byte identity of the published
    document is what is being proved, `document_body` is where that fact
    is, and a Chromium capture would add the snapshot extra and this
    mount to a claim it cannot strengthen (design section 13).
    """

    def _built(self, node):
        from solid_node.node import StlRenderStart
        from solid_node.simulation.enumeration import bind_declared_defaults

        bind_declared_defaults(node)
        node.assemble()
        for _attempt in range(5):
            try:
                node.build_stls()
                break
            except StlRenderStart:
                continue
        return node

    @staticmethod
    def _anonymous(document):
        """`document` with the ROOT's own name dropped.

        Two fixtures differ in their class name and in nothing else, and
        a root's name is the class's. Everything the time base could
        touch -- the animation block, the drivers, the tree shape, the
        operations, the version -- is compared.
        """
        document = dict(document)
        document.pop('pieces', None)
        document.pop('models', None)
        root = document.get('root')
        if isinstance(root, dict):
            root = dict(root)
            root.pop('name', None)
            document['root'] = root
        return document

    def _manifest(self, node, name):
        import os

        from solid_node.core.export import export_node

        out_dir = os.path.join(self.build_dir, name)
        export_node(self._built(node), out_dir, widget=False)
        with open(os.path.join(out_dir, 'manifest.json')) as handle:
            return json.load(handle)

    def test_export_produces_what_an_undeclared_root_produces(self):
        declared = self._anonymous(self._manifest(Swing(),
                                                  'elapsed_export'))
        undeclared = self._anonymous(self._manifest(Untimed(),
                                                    'untimed_export'))
        self.assertNotIn('loop', declared['animation'])
        self.assertEqual(json.dumps(declared, sort_keys=True),
                         json.dumps(undeclared, sort_keys=True))

    def test_the_build_publishes_the_same_snapshot(self):
        import os

        from solid_node.core.builder import Builder
        from solid_node.core.pieces import PieceInventory

        def viewer(node, name):
            builder = Builder.__new__(Builder)
            builder.node = self._built(node)
            builder.build_dir = os.path.join(self.build_dir, name)
            os.makedirs(builder.build_dir, exist_ok=True)
            with PieceInventory() as inventory:
                builder._write_viewer_snapshot_with_inventory(inventory)
            with open(os.path.join(builder.build_dir,
                                   'viewer.json')) as handle:
                return json.load(handle)

        declared = self._anonymous(viewer(Swing(), 'elapsed_build'))
        undeclared = self._anonymous(viewer(Untimed(), 'untimed_build'))
        self.assertEqual(json.dumps(declared, sort_keys=True),
                         json.dumps(undeclared, sort_keys=True))

    def test_publication_still_refuses_the_clocked_root(self):
        from solid_node.core.serializer import (ClockedDocumentError,
                                                document_body)

        node = self._built(Regulator())
        with self.assertRaises(ClockedDocumentError) as caught:
            document_body(node, {}, {}, {})
        self.assertIn('count', str(caught.exception))


class BoundsAndTheClockTest(BaseNodeTest):
    """Task 7: nothing stops a clock, and no chain follows one (design
    section 7)."""

    def test_a_driver_request_is_clipped_and_a_time_request_is_not(self):
        from .clocked_project.pendulum import Lift

        sim = Sim(Lift(), record=8)
        # ADR-126 unchanged: the driver stops at the declared bound and
        # reports it.
        made = sim.move('lift', by=20.0)
        self.assertEqual(made.admitted, STROKE)
        self.assertEqual(len(made.stops), 1)
        self.assertEqual(made.stops[0].coordinate, 'plate.lift')
        self.assertEqual(sim.state['lift'], STROKE)
        # A request along the CLOCK is clipped by nothing: a declared
        # range is a mechanical stop, and no interlock holds a clock.
        travelled = sim.move('time', by=10 * T)
        self.assertEqual(travelled.stops, ())
        self.assertEqual(travelled.admitted, 10 * T)
        self.assertEqual(sim.time, 10 * T)
        self.assertEqual(sim.state['count'], 20)

    def test_a_time_request_that_leaves_a_range_is_refused_whole(self):
        from .clocked_project.pendulum import Ranged

        sim = Sim(Ranged(), record=8)
        # BY HAND: two releases stand inside the quarter (2 * 36 = 72 of
        # 90 degrees) and a third does not (108).
        sim.move('time', by=T)
        before = sim.state
        posed = sim.node.face.turn.value
        with self.assertRaises(JointRangeError) as caught:
            sim.move('time', by=2 * T)
        message = str(caught.exception)
        self.assertIn('face.turn', message)
        self.assertIn('high', message)
        self.assertEqual(sim.state, before)
        self.assertEqual(sim.node.face.turn.value, posed)
        self.assertEqual(len(sim.commits), 2)

    def test_a_chain_that_carries_the_clock_is_refused_at_construction(self):
        from .clocked_project.pendulum import Captured

        with self.assertRaises(ClockedError) as caught:
            Sim(Captured())
        message = str(caught.exception)
        # The node, the joint, the coordinate, the SIDE compiled first
        # and the name that survived the chain.
        self.assertIn('arm', message)
        self.assertIn("joint 'turn'", message)
        self.assertIn('arm.turn', message)
        self.assertIn('low bound', message)
        self.assertIn('$t', message)
        self.assertIn('clock-driven coordinate', message)


class RefusedNamesTest(BaseNodeTest):
    """Task 5.2 and design section 8: `sim.time` is the ONE name of
    ADR-125's refused list this cycle lifts, and only under this base.
    Every other name stays refused under an elapsed clocked root."""

    # `trigger` left this list with `play-the-instruction`: an
    # instruction under a clocked root is ONE REQUEST under EVERY time
    # base, so it is refused here no more than `move` is.
    REFUSED = ('run', 'at', 'every', 'tick', 'rate', 'commands',
               'program', 'crossings')

    CALLS = {'run': (0.0,), 'at': (0.0,), 'every': (1.0, print),
             'rate': ('engaged', 1.0)}

    def test_every_cadence_name_is_still_refused(self):
        sim = Sim(Regulator())
        for name in self.REFUSED:
            with self.subTest(name=name):
                with self.assertRaises(TypeError) as caught:
                    found = getattr(sim, name)
                    if name in self.CALLS:
                        found(*self.CALLS[name])
                message = str(caught.exception)
                self.assertIn(name, message)
                self.assertIn('CLOCKED', message)

    def test_the_clocked_surface_and_the_clock_are_admitted(self):
        sim = Sim(Regulator())
        for name in ('move', 'trigger', 'snapshot', 'restore', 'reset',
                     'initial', 'state', 'commits', 'stops', 'time'):
            with self.subTest(name=name):
                self.assertTrue(hasattr(sim, name))
