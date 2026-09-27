# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Curta-shaped contracts use a mate's actual posing joint."""

from solid2 import cube

from machinome.motion.joints import Bound, JointRangeError, Prismatic, Revolute, declared_joints
from machinome.motion.ports import Time
from machinome.node import AssemblyNode, Solid2Node
from machinome.node.frames import Frame
from machinome.simulation import Button, Driver, Instruction, Sim, Slide, State, Turn, UnsupportedLaw
from machinome.parameters import ParameterError
from machinome.simulation.clocked import ClockedError
from .base import BaseNodeTest
from .test_mates import matrix_of


class Handle(Solid2Node):
    origin = Frame()
    lift = Prismatic(axis=(0, 0, 1))

    def render(self):
        return cube(1)


class Pawl(Solid2Node):
    origin = Frame()
    turn = Revolute(axis=(0, 0, 1))

    def render(self):
        return cube(1)


def crank_mount(*, factory=False, constrain=False, controls=False, sliding=False):
    declarations, calls = {}, []
    with_controls = controls

    def span(node):
        calls.append(node)
        return (0, Bound(lambda own, pawl: 90 + pawl,
                         reads=(declarations['pawl'].turn,)))

    freedom = Prismatic(axis=(1, 0, 0)) if sliding else Revolute()
    class Mount(AssemblyNode):
        request = Driver(default=0)
        relief = Driver(default=0)
        lift_input = Driver(default=0)
        pin = Frame(at=(0, 0, 7))
        handle = Handle()
        pawl = Pawl()  # realized AFTER handle, read only at evaluation
        declarations['pawl'] = pawl
        freedom.range = (span if factory else
                         (0, Bound(lambda own, pawl: 90 + pawl, reads=(pawl.turn,))))
        travel = handle.origin.on(pin, freedom)
        request.drives(travel)
        relief.drives(pawl.turn)
        lift_input.drives(handle.lift)
        if constrain:
            travel.constrain(range=(None, 100))
        if with_controls:
            instructions = {'advance': Instruction(by={'request': 5}, duration=.1)}
            controls = {'move': (Slide if sliding else Turn)(handle, request, coordinate=travel),
                        'press': Button(handle, 'advance', coordinate=travel),
                        'lift': Slide(handle, lift_input, coordinate=handle.lift)}
    return Mount, calls


class MateContractTest(BaseNodeTest):
    def running(self, mount):
        class Running(mount):
            time = Time.running()
        return Sim(Running(), dt=.1)

    def test_static_bound_uses_assembly_and_late_sibling(self):
        mount, calls = crank_mount()
        sim = self.running(mount)
        self.assertEqual(sim.move('request', to=120).status, 'blocked')
        self.assertEqual(sim.state['handle.travel'], 90)
        self.assertEqual(set(sim.state), {'request', 'relief', 'lift_input',
                                         'handle.travel', 'handle.lift', 'pawl.turn'})
        self.assertEqual(calls, [])
        joint = declared_joints(type(sim.node.handle))['travel']
        self.assertIs(joint.bound_reads(sim.node.handle, 'upper')[0].node, sim.node.pawl)
        self.assertFalse(joint._declared_at_site)
        self.assertEqual(joint.arguments(sim.node.handle)[0], (0, 0, 1))

    def test_factory_bounds_once_and_independent_inherited_instances(self):
        mount, calls = crank_mount(factory=True)
        class Inherited(mount):
            time = Time.running()
        left, right = Sim(Inherited(), dt=.1), Sim(Inherited(), dt=.1)
        self.assertEqual(calls, [left.node, right.node])
        left.move('relief', to=10)
        left.move('request', to=120)
        right.move('request', to=120)
        self.assertEqual(left.state['handle.travel'], 100)
        self.assertEqual(right.state['handle.travel'], 90)
        self.assertEqual(len(calls), 2)

    def test_own_constraint_and_selected_controls_share_generated_joint(self):
        mount, _ = crank_mount(constrain=True, controls=True)
        sim = self.running(mount)
        sim.move('relief', to=20)
        sim.move('request', to=120)
        self.assertEqual(sim.state['handle.travel'], 100)
        controls = {control.name: control for control in sim.program.controls}
        self.assertEqual(controls['move'].coordinate, 'handle.travel')
        self.assertEqual(controls['press'].coordinate, 'handle.travel')
        self.assertEqual(controls['lift'].coordinate, 'handle.lift')

    def test_prismatic_mate_selects_slide(self):
        mount, _ = crank_mount(sliding=True, controls=True)
        sim = self.running(mount)
        controls = {control.name: control for control in sim.program.controls}
        self.assertEqual(controls['move'].coordinate, 'handle.travel')
        self.assertEqual(sim.move('request', to=120).status, 'blocked')
        self.assertEqual(sim.state['handle.travel'], 90)

    def test_ancestor_constraint_reads_and_targets_nested_mates(self):
        mount, _ = crank_mount()
        class Machine(AssemblyNode):
            time = Time.running()
            left = mount()
            right = mount()
            left.travel.constrain(range=(None, Bound(
                lambda own, other: 50 + other, reads=(right.travel,))))
        sim = Sim(Machine(), dt=.1)
        sim.move('right.request', to=10)
        sim.move('left.request', to=100)
        self.assertEqual(sim.state['left.handle.travel'], 60)
        self.assertEqual(sim.state['right.handle.travel'], 10)

    def test_ordinary_joint_bound_reads_a_mate(self):
        class Machine(AssemblyNode):
            time = Time.running()
            a = Driver(default=0)
            b = Driver(default=0)
            seat = Frame()
            handle = Handle()
            travel = handle.origin.on(seat, Revolute())
            pawl = Pawl(turn=Revolute(axis=(0, 0, 1), range=(0, Bound(
                lambda own, other: 10 + other, reads=(travel,)))))
            a.drives(travel)
            a.drives(handle.lift)
            b.drives(pawl.turn)
        sim = Sim(Machine(), dt=.1)
        self.assertEqual(sim.move('b', to=20).status, 'blocked')
        self.assertEqual(sim.state['pawl.turn'], 10)

    def test_alias_self_read_is_refused_for_constraint(self):
        mount, _ = crank_mount()
        with self.assertRaisesRegex(TypeError, 'OWN'):
            class Bad(AssemblyNode):
                unit = mount()
                unit.travel.constrain(range=(None, Bound(
                    lambda own, alias: alias + 10, reads=(unit.handle.travel,))))

    def test_duplicate_physical_reads_are_refused_in_both_orders(self):
        mount, _ = crank_mount()
        for reverse in (False, True):
            with self.subTest(reverse=reverse), self.assertRaisesRegex(TypeError, 'twice'):
                class Bad(AssemblyNode):
                    unit = mount()
                    reads = (unit.travel, unit.handle.travel)
                    if reverse:
                        reads = reads[::-1]
                    unit.pawl.turn.constrain(range=(None, Bound(
                        lambda own, a, b: a + b, reads=reads)))

    def test_untimed_bound_judges_at_enumeration_close(self):
        mount, _ = crank_mount(factory=True)
        node = mount()
        node.set_state(request=80, relief=0, lift_input=0)
        with self.assertRaises(JointRangeError):
            node.set_state(request=100, relief=0, lift_input=0)

    def test_clocked_bound_and_constraint_use_existing_solver(self):
        mount, _ = crank_mount(factory=True, constrain=True)
        class Clocked(mount):
            retained = State(default=0)
            mount.request.commits(retained,
                at=lambda source, target: lambda value: value >= 40,
                law=lambda source, target: lambda value: 1)
        sim = Sim(Clocked())
        sim.move('request', to=120)
        self.assertEqual(sim.state['request'], 90)

    def test_curta_shaped_twin_stop_relief_ancestor_limit_pose_and_replay(self):
        mount, _ = crank_mount(controls=True)
        class Ordinary(AssemblyNode):
            request = Driver(default=0)
            relief = Driver(default=0)
            lift_input = Driver(default=0)
            pawl = Pawl()
            handle = Handle(travel=Revolute(axis=(0, 0, 1), at=(0, 0, 7),
                range=(0, Bound(lambda own, pawl: 90 + pawl, reads=(pawl.turn,)))))
            request.drives(handle.travel)
            relief.drives(pawl.turn)
            lift_input.drives(handle.lift)
            instructions = {'advance': Instruction(by={'request': 5}, duration=.1)}
            controls = {'move': Turn(handle, request, coordinate=handle.travel),
                        'press': Button(handle, 'advance', coordinate=handle.travel),
                        'lift': Slide(handle, lift_input, coordinate=handle.lift)}

            def render(self):
                self.handle.translate((0, 0, 7))

        class MatedRoot(AssemblyNode):
            time = Time.running()
            unit = mount()
            unit.travel.constrain(range=(None, 105))
        class OrdinaryRoot(AssemblyNode):
            time = Time.running()
            unit = Ordinary()
            unit.handle.travel.constrain(range=(None, 105))
        mated, ordinary = Sim(MatedRoot(), dt=.1), Sim(OrdinaryRoot(), dt=.1)
        self.assertEqual(set(mated.state), set(ordinary.state))
        self.assertEqual(tuple((c.name, c.coordinate, c.joint, c.span)
                               for c in mated.program.controls),
                         tuple((c.name, c.coordinate, c.joint, c.span)
                               for c in ordinary.program.controls))
        for sim in (mated, ordinary):
            self.assertEqual(sim.move('unit.request', to=120).status, 'blocked')
            self.assertEqual(sim.state['unit.handle.travel'], 90)
        saved = [sim.snapshot() for sim in (mated, ordinary)]
        def resume(sim):
            sim.move('unit.relief', to=30)
            self.assertEqual(sim.state['unit.handle.travel'], 90)  # no backlog
            sim.move('unit.lift_input', to=4)
            self.assertEqual(sim.move('unit.request', to=120).status, 'blocked')
            self.assertEqual(sim.state['unit.handle.travel'], 105)
            # A moving read cannot invalidate the standing crank.
            self.assertEqual(sim.move('unit.relief', to=0).status, 'blocked')
            self.assertAlmostEqual(sim.state['unit.relief'], 15)
        for sim in (mated, ordinary):
            resume(sim)
        self.assertEqual(dict(mated.state), dict(ordinary.state))
        for a, b in zip(matrix_of([op.serialized for op in mated.node.unit.handle.operations]),
                        matrix_of([op.serialized for op in ordinary.node.unit.handle.operations])):
            for x, y in zip(a, b):
                self.assertAlmostEqual(x, y)
        for sim, snapshot in zip((mated, ordinary), saved):
            expected = sim.snapshot()
            sim.restore(snapshot)
            resume(sim)
            self.assertEqual(sim.snapshot(), expected)

    def test_static_inherited_reads_follow_compatible_replacement(self):
        mount, _ = crank_mount()
        class Replacement(mount):
            time = Time.running()
            pawl = Pawl()
        left, right = Sim(Replacement(), dt=.1), Sim(Replacement(), dt=.1)
        left.move('relief', to=10)
        for sim in (left, right):
            sim.move('request', to=120)
        self.assertEqual(left.state['handle.travel'], 100)
        self.assertEqual(right.state['handle.travel'], 90)
        class Missing(AssemblyNode):
            pass
        with self.assertRaisesRegex((TypeError, AttributeError), 'pawl.turn|turn'):
            class Invalid(mount):
                pawl = Missing()

    def test_nested_mate_control_uses_generated_placement(self):
        class Mount(AssemblyNode):
            pin = Frame()
            handle = Handle()
            travel = handle.origin.on(pin, Prismatic(axis=(1, 0, 0)))
        class Holder(AssemblyNode):
            mount = Mount()
        class Machine(AssemblyNode):
            time = Time.running()
            entry = Driver(default=0)
            lifting = Driver(default=0)
            unit = Holder()
            entry.drives(unit.mount.travel)
            lifting.drives(unit.mount.handle.lift)
            controls = {'slide': Slide(unit.mount.handle, entry, coordinate=unit.mount.travel)}
        sim = Sim(Machine(), dt=.1)
        control = sim.program.controls[0]
        self.assertEqual(control.coordinate, 'unit.mount.handle.travel')
        self.assertEqual(control.joint, ('unit', 'mount', 'handle'))
        self.assertIsNotNone(control.span)

    def test_returned_self_alias_and_duplicate_reads_are_refused(self):
        for spelling in ('mate', 'joint', 'duplicates'):
            held = {}
            def span(node):
                refs = held['refs']
                return (None, Bound(lambda own, *args: sum(args) + 1, reads=refs))
            class Mount(AssemblyNode):
                pin = Frame()
                handle = Handle()
                pawl = Pawl()
                travel = handle.origin.on(pin, Revolute(range=span))
            if spelling == 'mate':
                held['refs'] = (Mount.travel,)
            elif spelling == 'joint':
                held['refs'] = (Mount.handle.travel,)
            else:
                held['refs'] = (Mount.pawl.turn, Mount.pawl.turn)
            with self.subTest(spelling=spelling), self.assertRaisesRegex(
                    ParameterError, 'travel.*(OWN|twice)'):
                Mount()

    def test_rigid_mates_refuse_all_mechanical_contexts_by_name(self):
        class Held(AssemblyNode):
            pin = Frame()
            pawl = Pawl()
            bolted = pawl.origin.on(pin)
        for context in ('reads', 'constraint', 'control'):
            with self.subTest(context=context), self.assertRaisesRegex(TypeError, 'bolted.*no coordinate'):
                class Bad(AssemblyNode):
                    input = Driver(default=0)
                    unit = Held()
                    if context == 'reads':
                        Bound(lambda own, held: held, reads=(unit.bolted,))
                    elif context == 'constraint':
                        unit.bolted.constrain(range=(0, 1))
                    else:
                        controls = {'bad': Turn(unit.pawl, input, coordinate=unit.bolted)}

    def test_wrong_domain_and_sideways_controls_stay_refused(self):
        for sideways, slide in ((False, True), (True, False)):
            with self.subTest(sideways=sideways), self.assertRaisesRegex(Exception, 'translational|neither'):
                class Bad(AssemblyNode):
                    time = Time.running()
                    request = Driver(default=0)
                    seat = Frame()
                    handle = Handle()
                    pawl = Pawl()
                    travel = handle.origin.on(seat, Revolute())
                    request.drives(travel)
                    request.drives(handle.lift)
                    request.drives(pawl.turn)
                    controls = {'bad': (Slide if slide else Turn)(
                        pawl if sideways else handle, request, coordinate=travel)}
                Sim(Bad(), dt=.1)

    def test_clocked_curved_bound_retains_existing_refusal(self):
        held = {}
        def span(node):
            return (None, Bound(lambda own, read: 90 + read*read,
                                reads=(held['pawl'].turn,)))
        class Clocked(AssemblyNode):
            request = Driver(default=0)
            relief = Driver(default=0)
            retained = State(default=0)
            pin = Frame()
            handle = Handle()
            pawl = Pawl()
            held['pawl'] = pawl
            travel = handle.origin.on(pin, Revolute(range=span))
            request.drives(travel)
            request.drives(handle.lift)
            relief.drives(pawl.turn)
            request.commits(retained,
                at=lambda source, target: lambda value: value >= 40,
                law=lambda source, target: lambda value: 1)
        with self.assertRaisesRegex(ClockedError, 'CURVES'):
            Sim(Clocked())
