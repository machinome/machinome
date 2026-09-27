# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Existing-joint attachments retain the original dial endpoint."""

from solid2 import cube
from machinome.node import AssemblyNode, Solid2Node, Frame
from machinome.motion.joints import Bound, Free, Orbit, Prismatic, Revolute, declared_joints
from machinome.motion.ports import RotationalPort, Time, declared_ports
from machinome.motion.couplings import DoublyBound, declared_relations, coordinate_ref
from machinome.simulation import Driver, Sim, Turn, Slide, Button, Instruction
from .base import BaseNodeTest
from .test_mates import matrix_of


def pose(node):
    return matrix_of([op.serialized for op in node.operations])


class Dial(Solid2Node):
    axle = Frame()
    turn = Revolute(axis=(0, 0, 1))

    def render(self):
        return cube(1)


def register(*, site=False):
    class Register(AssemblyNode):
        ones_seat = Frame(at=(10, 0, 0))
        tens_seat = Frame(at=(20, 0, 0))
        ones = Dial(turn=Revolute(axis=(0, 0, 1), at=(10, 0, 0))) if site else Dial()
        tens = Dial(turn=Revolute(axis=(0, 0, 1), at=(20, 0, 0))) if site else Dial()
        ones_mount = ones.axle.on(ones_seat, ones.turn)
        tens_mount = tens.axle.on(tens_seat, tens.turn)
        def simulate(self):
            if self.ones.turn.value is None:
                self.ones.turn = 36
            if self.tens.turn.value is None:
                self.tens_mount = 72
    return Register


class ExistingJointTest(BaseNodeTest):
    def test_prismatic_class_and_site_handles_keep_scope_and_controls(self):
        for site in (False, True):
            calls = []
            class Carriage(Solid2Node):
                axle = Frame()
                travel = Prismatic(axis=lambda node: calls.append(node) or (1, 0, 0), range=(0, 8))
                def render(self):
                    return cube(1)
            class Mount(AssemblyNode):
                time = Time.running()
                request = Driver(default=0, unit='mm')
                seat = Frame(at=(10, 0, 0))
                body = Carriage(travel=Prismatic(axis=lambda node: calls.append(node) or (1, 0, 0),
                                                at=lambda node: (0, 0, 0), range=(0, 8))) if site else Carriage()
                mount = body.axle.on(seat, body.travel)
                request.drives(mount)
                mount.constrain(range=(None, 6))
                controls = {'drag': Slide(body, request, coordinate=mount)}
            sim = Sim(Mount(), dt=.1)
            self.assertEqual(calls, [sim.node if site else sim.node.body])
            sim.move('request', to=10)
            self.assertEqual(sim.state['body.travel'], 6)
            self.assertIs(sim.node.mount, sim.node.body.travel)
            self.assertEqual(set(sim.state), {'request', 'body.travel'})

    def test_clocked_state_drives_original_joint_through_handle(self):
        from machinome.simulation import State
        from machinome.math import floor
        class Register(AssemblyNode):
            crank = Driver(default=0)
            count = State(default=0, dtype=int)
            seat = Frame(at=(10, 0, 0))
            body = Dial()
            mount = body.axle.on(seat, body.turn)
            (crank & count).commits(count,
                at=lambda sources, targets: lambda crank, count: floor(crank / 360),
                law=lambda sources, targets: lambda crank, count: count + 1)
            count.drives(mount, ratio=36)
        sim = Sim(Register())
        sim.move('crank', by=720)
        self.assertEqual(sim.state['count'], 2)
        self.assertEqual(sim.node.mount.value, 72)
        self.assertEqual(set(sim.state), {'crank', 'count'})
        saved = sim.snapshot()
        sim.move('crank', by=360)
        later = dict(sim.state)
        sim.restore(saved)
        sim.move('crank', by=360)
        self.assertEqual(sim.state, later)
        self.assertEqual(sim.node.body.turn.value, 108)

    def test_manual_existing_joint_example_executes(self):
        from pathlib import Path
        from .test_mates import _code_block_named
        text = (Path(__file__).resolve().parent.parent / 'docs/concepts/joints.rst').read_text()
        example = _code_block_named(text, 'class Register(AssemblyNode):')
        namespace = dict(__name__=__name__)
        exec(example, namespace)
        node = namespace['Register']()
        node.render()
        self.assertIs(node.ones_mount, node.ones.turn)
        self.assertEqual(node.ones.turn.value, 36)
        self.assertEqual(list(declared_ports(type(node.ones))), ['turn'])
        self.assertEqual(list(declared_ports(type(node))), [])

    def test_seventeen_retained_dials_match_independent_ordinary_witness(self):
        from .running_project.machine import missing_tooth_pair
        def fixture(attached):
            lines = ['class Register(AssemblyNode):', '    time = Time.running()',
                     '    ring = Driver(default=0)']
            for index in range(17):
                lines += [f'    dial{index} = Dial()']
                if attached:
                    lines += [f'    seat{index} = Frame(at=({10 * index}, 0, 0))',
                              f'    mount{index} = dial{index}.axle.on(seat{index}, dial{index}.turn)']
                target = f'mount{index}' if attached else f'dial{index}.turn'
                lines += [f'    (ring & dial{index}.turn).drives({target}, law=missing_tooth_pair)']
            lines += ['    def simulate(self):']
            for index in range(17):
                lines += [f'        if self.dial{index}.turn.value is None:',
                          f'            self.dial{index}.turn = {36 * (index % 10)}']
            if not attached:
                lines += ['    def render(self):']
                for index in range(17):
                    lines += [f'        self.dial{index}.translate([{10 * index}, 0, 0])']
            namespace = dict(__name__=__name__, AssemblyNode=AssemblyNode, Time=Time, Driver=Driver,
                             Dial=Dial, Frame=Frame, missing_tooth_pair=missing_tooth_pair)
            exec('\n'.join(lines), namespace)
            return namespace['Register']
        actual, expected = [Sim(fixture(attached)(), dt=.1) for attached in (True, False)]
        ids = {'ring'} | {f'dial{index}.turn' for index in range(17)}
        def compare():
            self.assertEqual(set(actual.state), ids)
            self.assertEqual(actual.state, expected.state)
            self.assertEqual(actual.snapshot().bank, expected.snapshot().bank)
            for index in range(17):
                for row, wanted in zip(pose(getattr(actual.node, f'dial{index}')),
                                       pose(getattr(expected.node, f'dial{index}'))):
                    for value, target in zip(row, wanted):
                        self.assertAlmostEqual(value, target)
        compare()
        for delta in (-40, -120):
            actual.move('ring', by=delta)
            expected.move('ring', by=delta)
            compare()
        paused = actual.snapshot(), expected.snapshot()
        for delta in (-500,):
            actual.move('ring', by=delta)
            expected.move('ring', by=delta)
            compare()
        cleared = actual.snapshot(), expected.snapshot()
        cleared_dials = {key: value for key, value in actual.state.items() if key != 'ring'}
        actual.move('ring', by=-500)
        expected.move('ring', by=-500)
        compare()
        self.assertEqual({key: value for key, value in actual.state.items() if key != 'ring'}, cleared_dials)
        for sim, saved in zip((actual, expected), paused):
            sim.restore(saved)
            sim.move('ring', by=-500)
        compare()
        self.assertEqual((actual.snapshot(), expected.snapshot()), cleared)

    def test_foreign_formula_provenance_survives_algebra(self):
        class Foreign(AssemblyNode):
            seat = Frame()
            body = Dial()
            mount = body.axle.on(seat, body.turn)
        forms = (
            lambda body: body.turn + Foreign.mount,
            lambda body: 2 * Foreign.mount + body.turn,
            lambda body: (Foreign.mount - Foreign.mount) + body.turn,
            lambda body: 0 * Foreign.mount + body.turn,
            lambda body: (body.turn + Foreign.mount) * 2 - body.turn,
        )
        for form in forms:
            for inline in (False, True):
                with self.subTest(form=form, inline=inline):
                    with self.assertRaisesRegex(TypeError, 'not declared|not a child|foreign'):
                        class Wrong(AssemblyNode):
                            body = Foreign.body
                            target = Dial()
                            if inline:
                                form(body).drives(target.turn)
                            else:
                                relative = form(body)
                            def simulate(self):
                                self.body.turn = 10
                                if not inline:
                                    self.target.turn = 0
                        Wrong().render()

    def test_foreign_nested_handle_formula_is_not_rewalked(self):
        class Foreign(AssemblyNode):
            unit = register()()
        with self.assertRaisesRegex(TypeError, 'not declared|not a child|foreign'):
            class Wrong(AssemblyNode):
                unit = register()()
                relative = 0 * Foreign.unit.ones_mount + unit.ones.turn
            Wrong().render()

    def test_ordinary_expression_merge_never_traverses_alias_keys(self):
        from unittest.mock import patch
        from machinome.motion import couplings
        ports = [RotationalPort() for _ in range(100)]
        with patch.object(couplings, '_alias_comparison_key', wraps=couplings._alias_comparison_key) as canonical:
            value = ports[0]
            for port in ports[1:]:
                value = value + port
        self.assertEqual(len(value.terms_map), 100)
        self.assertEqual(canonical.call_count, 0)

    def test_original_bound_scopes_and_factory_receivers(self):
        calls = []
        class ScopedDial(Solid2Node):
            axle = Frame()
            relief = Revolute(axis=(1, 0, 0))
            turn = Revolute(axis=lambda node: calls.append(node) or (0, 0, 1),
                            range=(0, Bound(lambda own, read: 90 + read, reads=(relief,))))
            def render(self):
                return cube(1)
        class Mount(AssemblyNode):
            time = Time.running()
            request = Driver(default=0)
            release = Driver(default=0)
            relief = RotationalPort(unit='deg')  # deliberate parent same-name trap
            seat = Frame(at=(10, 0, 0))
            body = ScopedDial()
            mount = body.axle.on(seat, body.turn)
            request.drives(mount)
            release.drives(body.relief)
            def simulate(self):
                if self.relief.value is None:
                    self.relief = 100
        left, right = Sim(Mount(), dt=.1), Sim(Mount(), dt=.1)
        self.assertEqual(calls, [left.node.body, right.node.body])
        left.move('release', to=5)
        left.move('request', to=120)
        right.move('request', to=120)
        self.assertEqual(left.state['body.turn'], 95)
        self.assertEqual(right.state['body.turn'], 90)
        self.assertEqual(calls, [left.node.body, right.node.body])
        joint = ScopedDial.turn
        self.assertIs(joint.declarer_of(left.node.body), left.node.body)
        self.assertIs(joint.bound_reads(left.node.body, 'upper')[0].node, left.node.body)

    def test_site_factory_and_bound_keep_parent_scope(self):
        calls, paths = [], {}
        def span(parent):
            calls.append(parent)
            return (0, Bound(lambda own, read: 80 + read, reads=(paths['release'],)))
        class Mount(AssemblyNode):
            time = Time.running()
            request = Driver(default=0)
            release = Driver(default=10)
            seat = Frame(at=(10, 0, 0))
            body = Dial(turn=Revolute(axis=lambda parent: (0, 0, 1),
                                     at=lambda parent: (10, 0, 0), range=span))
            paths['release'] = release
            mount = body.axle.on(seat, body.turn)
            request.drives(mount)
        sim = Sim(Mount(), dt=.1)
        joint = declared_joints(type(sim.node.body))['turn']
        self.assertTrue(joint._declared_at_site)
        self.assertIs(joint.declarer_of(sim.node.body), sim.node)
        self.assertEqual(calls, [sim.node])
        sim.move('request', to=120)
        self.assertEqual(sim.state['body.turn'], 90)
        self.assertEqual(calls, [sim.node])

    def test_original_order_and_nontrivial_placement_match_independent_witness(self):
        class OrderedDial(Dial):
            axle = Frame(at=(1, 2, 3))
            turn = Revolute(axis=(1, 0, 0), at=(0, 1, 0))
            lean = Revolute(axis=(0, 1, 0), at=(2, 0, 0))
        for site in (False, True):
            with self.subTest(site=site):
                class Attached(AssemblyNode):
                    seat = Frame(at=(10, 0, 7), z=(0, -1, 0), x=(1, 0, 0))
                    body = OrderedDial(turn=Revolute(axis=(1, 0, 0), at=(10, 0, 7))) if site else OrderedDial()
                    mount = body.axle.on(seat, body.turn)
                class Ordinary(AssemblyNode):
                    body = OrderedDial(turn=Revolute(axis=(1, 0, 0), at=(10, 0, 7))) if site else OrderedDial()
                    def render(self):
                        return [self.body.rotate(90, (1, 0, 0)).translate((9, 3, 5))]
                attached, ordinary = Attached(), Ordinary()
                attached.render(); ordinary.render()
                self.assertEqual(list(declared_joints(type(attached.body))), ['turn', 'lean'])
                for turn, lean in ((0, 0), (35, 20), (10, -15), (50, 70)):
                    attached.mount = turn; attached.body.lean = lean
                    ordinary.body.turn = turn; ordinary.body.lean = lean
                    self.assertTrue(abs(pose(attached.body) - pose(ordinary.body)).max() < 1e-9)
                plain = OrderedDial()
                self.assertIsNone(getattr(OrderedDial.turn, 'installed_by', None))
                self.assertIs(type(plain), OrderedDial)
                self.assertIs(Attached.body.node_class, type(attached.body))

    def test_supported_inheritance_and_nested_handle(self):
        base = register()
        class Inherited(base):
            pass
        class Root(AssemblyNode):
            angle = Driver(default=0)
            unit = Inherited()
            angle.drives(unit.ones_mount)
        node = Root()
        node.set_state(angle=15)
        self.assertEqual(node.unit.ones.turn.value, 15)
        self.assertIs(node.unit.ones_mount, node.unit.ones.turn)
        with self.assertRaisesRegex(TypeError, 'declares.*anew|no longer declares'):
            class Replaced(base):
                ones = Dial()

    def test_invalid_reference_shapes_are_named(self):
        class Rich(Dial):
            port = RotationalPort()
            orbit = Orbit(axis=(0, 0, 1))
            free = Free()
            deeper = Dial()
        for select in (lambda body, other: other.turn,
                       lambda body, other: body,
                       lambda body, other: body.deeper.turn,
                       lambda body, other: body.port,
                       lambda body, other: body.orbit,
                       lambda body, other: body.free,
                       lambda body, other: body.free.roll,
                       lambda body, other: 'turn',
                       lambda body, other: Dial.turn):
            with self.subTest(select=select), self.assertRaisesRegex(TypeError, 'mate|freedom|existing'):
                class Wrong(AssemblyNode):
                    seat = Frame()
                    body = Rich()
                    other = Rich()
                    mount = body.axle.on(seat, select(body, other))

    def test_foreign_handle_not_redirected_by_matching_names(self):
        foreign = register()
        with self.assertRaisesRegex(TypeError, 'not declared|not a child'):
            class Wrong(AssemblyNode):
                request = Driver(default=0)
                ones_seat = Frame()
                ones = Dial()
                ones_mount = ones.axle.on(ones_seat, ones.turn)
                request.drives(foreign.ones_mount)

    def test_run_owner_cannot_be_bypassed_by_handle(self):
        class Wrong(AssemblyNode):
            time = Time.running()
            seat = Frame()
            body = Dial()
            mount = body.axle.on(seat, body.turn)
            def simulate(self):
                self.mount = 10
        with self.assertRaisesRegex(ValueError, 'running simulation|run owns'):
            Sim(Wrong(), dt=.1)

    def test_mixed_handle_retained_laws_in_both_directions_and_inferred_node(self):
        from .running_project.machine import missing_tooth_pair
        for source_alias, target_alias, inferred in ((False, True, False),
                                                     (True, False, False),
                                                     (False, True, True)):
            with self.subTest(source_alias=source_alias, target_alias=target_alias, inferred=inferred):
                class Running(AssemblyNode):
                    time = Time.running()
                    ring = Driver(default=0)
                    seat = Frame(at=(10, 0, 0))
                    body = Dial()
                    mount = body.axle.on(seat, body.turn)
                    (ring & (mount if source_alias else (body if inferred else body.turn))).drives(
                        mount if target_alias else body.turn, law=missing_tooth_pair)
                    def simulate(self):
                        if self.body.turn.value is None:
                            self.body.turn = 108
                sim = Sim(Running(), dt=.1)
                relation = declared_relations(Running)[0]
                self.assertEqual(relation.self_read, 1)
                self.assertEqual(set(sim.state), {'ring', 'body.turn'})
                edge = sim.program.edges[0]
                self.assertEqual(edge.gives[0], edge.needs[1])
                sim.move('ring', by=-40)
                paused = sim.snapshot()
                sim.move('ring', by=-500)
                cleared = sim.snapshot()
                sim.move('ring', by=-500)
                self.assertEqual(sim.state['body.turn'], dict(cleared.bank)['body.turn'])
                sim.restore(paused)
                sim.move('ring', by=-500)
                self.assertEqual(sim.snapshot(), cleared)
    def test_complete_example_keeps_class_and_slots(self):
        for site in (False, True):
            with self.subTest(site=site):
                cls = register(site=site)
                original = cls.ones.turn.terminal
                specialized = cls.ones.node_class
                mate = cls.ones_mount
                self.assertIs(mate.freedom.root, cls.ones)
                self.assertIs(mate.freedom.terminal, original)
                self.assertIs(cls.ones.node_class, specialized)
                self.assertNotIn('ones_mount', declared_ports(cls))
                self.assertEqual(list(declared_joints(specialized)), ['turn'])
                node = cls()
                node.render()
                self.assertIs(node.ones_mount, node.ones.turn)
                self.assertEqual(node.ones_mount.value, 36)
                self.assertEqual(node.tens_mount.value, 72)
                self.assertNotIn('ones_mount', node.__dict__.get('_port_values', {}))
                self.assertIsNone(getattr(original, 'installed_by', None))
                self.assertEqual(cls.ones.wiring, {})
                self.assertEqual(matrix_of([op.serialized for op in node.ones.operations])[:3, 3].tolist(), [10, 0, 0])

    def test_same_name_handle_does_not_replace_joint(self):
        class Mount(AssemblyNode):
            seat = Frame()
            body = Dial()
            turn = body.axle.on(seat, body.turn)
        self.assertIs(Mount.turn.freedom.terminal, Dial.turn)
        self.assertEqual(declared_ports(Mount), {})
        node = Mount()
        node.render()
        node.turn = 12
        self.assertEqual(node.body.turn.value, 12)

    def test_running_controls_and_constraint_keep_original_id(self):
        class Running(AssemblyNode):
            time = Time.running()
            request = Driver(default=0)
            seat = Frame(at=(10, 0, 0))
            body = Dial()
            mount = body.axle.on(seat, body.turn)
            mount.constrain(range=(None, 90))
            request.drives(mount)
            instructions = {'advance': Instruction(by={'request': 5}, duration=.1)}
            controls = {'turn': Turn(body, request, coordinate=mount),
                        'press': Button(body, 'advance', coordinate=mount)}
        sim = Sim(Running(), dt=.1)
        self.assertEqual(set(sim.state), {'request', 'body.turn'})
        self.assertEqual(sim.move('request', to=120).status, 'blocked')
        self.assertEqual(sim.state['body.turn'], 90)
        self.assertTrue(all(c.coordinate == 'body.turn' for c in sim.program.controls))
        before = sim.snapshot()
        sim.move('request', to=0)
        sim.restore(before)
        self.assertEqual(sim.snapshot(), before)
        self.assertEqual(len(sim.program.edges), 1)
        from .test_running_document import document
        published = document(sim.node)
        self.assertEqual(published['version'], 11)
        self.assertEqual(set(published['program']['coordinates']), {'request', 'body.turn'})
        self.assertEqual(len(published['program']['edges']), 1)
        self.assertNotIn('mount', published['program']['coordinates'])

    def test_derived_and_wiring_source_read_original(self):
        class Mount(AssemblyNode):
            seat = Frame()
            body = Dial()
            mount = body.axle.on(seat, body.turn)
            combined = mount + 2 * body.turn
            follower = Dial(turn=mount)
            def simulate(self):
                self.mount = 10
        node = Mount()
        node.render()
        self.assertEqual(node.combined.value, 30)
        self.assertEqual(node.follower.turn.value, 10)
        self.assertEqual(len(Mount.combined.terms_map), 1)

    def test_existing_author_wiring_keeps_sole_binder(self):
        class Mount(AssemblyNode):
            angle = RotationalPort(unit='deg')
            seat = Frame()
            body = Dial(turn=angle)
            mount = body.axle.on(seat, body.turn)
            def simulate(self):
                self.angle = 25
        node = Mount()
        node.render()
        self.assertEqual(node.mount.value, 25)
        self.assertIs(Mount.body.wiring['turn'], Mount.angle)
        with self.assertRaises(ValueError):
            node.mount = 30

    def test_grouped_aliases_refused(self):
        for inferred in (False, True):
            with self.subTest(inferred=inferred), self.assertRaisesRegex(TypeError, 'twice'):
                class Wrong(AssemblyNode):
                    request = RotationalPort(unit='deg')
                    seat = Frame()
                    body = Dial()
                    mount = body.axle.on(seat, body.turn)
                    (mount & (body if inferred else body.turn)).drives(request)

    def test_two_writers_cannot_hide_behind_handle(self):
        class Wrong(AssemblyNode):
            first = Driver(default=0)
            second = Driver(default=0)
            seat = Frame()
            body = Dial()
            mount = body.axle.on(seat, body.turn)
            first.drives(body.turn)
            second.drives(mount)
        with self.assertRaises(DoublyBound):
            node = Wrong()
            node.set_state(first=0, second=0)
            node.render()

    def test_foreign_site_reference_is_not_same_child(self):
        class Other(AssemblyNode):
            body = Dial()
        with self.assertRaisesRegex(TypeError, 'moving child|same|existing'):
            class Wrong(AssemblyNode):
                seat = Frame()
                body = Dial()
                mount = body.axle.on(seat, Other.body.turn)

    def test_bound_aliases_refused(self):
        with self.assertRaisesRegex(TypeError, 'OWN|itself'):
            class Wrong(AssemblyNode):
                seat = Frame()
                body = Dial()
                mount = body.axle.on(seat, body.turn)
                mount.constrain(range=(None, Bound(lambda own, read: read, reads=(body.turn,))))
