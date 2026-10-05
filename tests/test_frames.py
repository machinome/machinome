# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A frame: a named connector on a part.

OpenSpec change ``place-parts-by-mate``, tasks section 2. Thor's elbow is
one joint stated in three files, because nothing a part declares says
WHERE on it another part attaches: the parent's `render()` places the
forearm by arithmetic and the forearm's own class restates the same pin
as a joint. A frame is the part's own statement of a connector -- an
origin and a right-handed triad in the part's OWN rest frame -- and an
assembly mates two of them (`tests/test_mates.py`).

What this file pins is the declaration alone, in the mould of a marking
(ADR-120): it names itself, it is enumerable off the class, it is
inherited through the MRO (a plain mixin included, `None` dropping it),
it collides with nothing the class already declares, it is not
identity, and it resolves per instance -- by the joint's own argument
rule -- the moment its declarer is constructed.
"""

import math

from solid2 import cube

from machinome.motion.joints import Revolute
from machinome.motion.ports import RotationalPort
from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node
from machinome.node.markings import Marking, Svg, Wrapped
from machinome.parameters import Length, ParameterError

from .base import BaseNodeTest
from .import_probe import probe


def _frames():
    """The module under test, imported where a test needs it."""
    from machinome.node import frames

    return frames


def resolved(node, name):
    """The resolved frame `name` of the realized `node`."""
    return node.__dict__['_frame_arguments'][name]


class Plain(Solid2Node):
    """A part with nothing declared on it, for a clash to collide with."""

    def render(self):
        return cube(4)


##############################################
# 2.1 Declaration

class DeclarationTest(BaseNodeTest):

    def test_a_leaf_declares_a_frame_by_name(self):
        Frame = _frames().Frame

        class Forearm(Solid2Node):
            hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))

            def render(self):
                return cube(4)

        found = _frames().declared_frames(Forearm)

        self.assertEqual(list(found), ['hinge'])
        self.assertIs(found['hinge'], Forearm.hinge)
        self.assertEqual(Forearm.hinge.name, 'hinge')

    def test_an_assembly_declares_its_own_frame(self):
        Frame = _frames().Frame

        class UpperArm(AssemblyNode):
            elbow_pin = Frame(at=(0, 160, 68), z=(0, 0, 1))

        self.assertEqual(list(_frames().declared_frames(UpperArm)),
                         ['elbow_pin'])

    def test_frames_are_reported_in_declaration_order(self):
        Frame = _frames().Frame

        class Bracket(Solid2Node):
            top = Frame(at=(0, 0, 10))
            side = Frame(at=(5, 0, 0), z=(1, 0, 0))
            bottom = Frame(z=(0, 0, -1))

            def render(self):
                return cube(4)

        self.assertEqual(list(_frames().declared_frames(Bracket)),
                         ['top', 'side', 'bottom'])

    def test_the_class_reports_its_frames_without_an_instance(self):
        Frame = _frames().Frame

        class Refusing(Solid2Node):
            pin = Frame()

            def check(self):
                raise AssertionError('an instance was constructed')

            def render(self):
                return cube(4)

        self.assertEqual(list(_frames().declared_frames(Refusing)), ['pin'])

    def test_frame_resolves_from_the_node_package_too(self):
        from machinome.node.frames import Frame

        self.assertIs(Frame, _frames().Frame)

    def test_importing_frames_adds_nothing_outside_the_framework(self):
        # `machinome.node` itself is on every invocation's path; what a
        # frame may cost is what it adds to that, and it adds nothing
        # but its own module.
        result = probe(
            'import sys\n'
            'import machinome.node\n'
            'before = set(sys.modules)\n'
            'import machinome.node.frames\n'
            'added = sorted(set(sys.modules) - before)\n'
            'print(",".join(added))\n')

        result.check()
        added = set(filter(None, result.stdout.strip().split(',')))
        self.assertLessEqual(added, {'machinome.node.frames'})
        for heavy in ('trimesh', 'cadquery', 'build123d'):
            with self.subTest(module=heavy):
                self.assertFalse(result.imported(heavy))


##############################################
# 2.2 Inheritance

class InheritanceTest(BaseNodeTest):

    def test_a_subclass_inherits_and_can_drop_a_frame(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0))
            foot = Frame()

            def render(self):
                return cube(4)

        class Footless(Base):
            foot = None

        self.assertEqual(list(_frames().declared_frames(Base)),
                         ['hinge', 'foot'])
        self.assertEqual(list(_frames().declared_frames(Footless)),
                         ['hinge'])

    def test_a_frame_declared_in_a_plain_mixin_belongs_to_the_node(self):
        Frame = _frames().Frame

        class Connectors:
            socket = Frame(at=(0, 0, 3))

        class Part(Connectors, Solid2Node):
            def render(self):
                return cube(4)

        self.assertEqual(list(_frames().declared_frames(Part)), ['socket'])


##############################################
# 2.3 Clashes

class ClashTest(BaseNodeTest):

    def assertRefused(self, build, *expected):
        with self.assertRaises(TypeError) as raised:
            build()
        message = str(raised.exception)
        for fragment in expected:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_frame_cannot_take_a_parameters_name(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            hinge = Length(3)

            def render(self):
                return cube(4)

        def build():
            class Clashing(Base):
                hinge = Frame()

        self.assertRefused(build, 'Clashing', 'hinge', 'parameter')

    def test_a_parameter_and_a_frame_in_one_body_are_refused(self):
        Frame = _frames().Frame

        def build():
            class Clashing(Solid2Node):
                hinge = Length(3)
                hinge = Frame()  # noqa: F811

                def render(self):
                    return cube(4)

        self.assertRefused(build, 'hinge', 'frame')

    def test_a_frame_cannot_take_a_childs_name(self):
        Frame = _frames().Frame

        class Base(AssemblyNode):
            link = Plain()

        def build():
            class Clashing(Base):
                link = Frame()

        self.assertRefused(build, 'Clashing', 'link', 'child')

    def test_a_frame_cannot_take_a_ports_name(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            turn = RotationalPort(unit='deg')

            def render(self):
                return cube(4)

        def build():
            class Clashing(Base):
                turn = Frame()

        self.assertRefused(build, 'Clashing', 'turn', 'port')

    def test_a_frame_cannot_take_a_joint_coordinates_name(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            hinge = Revolute(axis=(0, 1, 0))

            def render(self):
                return cube(4)

        def build():
            class Clashing(Base):
                hinge = Frame()

        self.assertRefused(build, 'Clashing', 'hinge', 'joint')

    def test_a_frame_cannot_take_a_markings_name(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            digits = Marking(
                Svg('markings_project/label.svg'),
                Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45)),
                color='#FFFFFF')

            def render(self):
                return cube(4)

        def build():
            class Clashing(Base):
                digits = Frame()

        self.assertRefused(build, 'Clashing', 'digits', 'marking')

    def test_a_frame_cannot_shadow_the_nodes_colour(self):
        Frame = _frames().Frame

        def build():
            class Clashing(Solid2Node):
                color = Frame()

                def render(self):
                    return cube(4)

        self.assertRefused(build, 'Clashing', 'color', 'shadow')

    def test_a_frame_cannot_shadow_a_reserved_node_attribute(self):
        Frame = _frames().Frame

        def build():
            class Clashing(Solid2Node):
                files = Frame()

                def render(self):
                    return cube(4)

        self.assertRefused(build, 'Clashing', 'files', 'shadow')


##############################################
# 2.4 Identity

class IdentityTest(BaseNodeTest):

    def test_a_frame_is_not_identity(self):
        Frame = _frames().Frame

        def make(with_frame):
            class Plate(Solid2Node):
                width = Length(10)
                if with_frame:
                    pin = Frame(at=(0, 0, 5))

                def render(self):
                    return cube([self.width, 4, 2])

            return Plate

        framed, plain = make(True)(), make(False)()

        self.assertEqual(list(_frames().declared_frames(type(framed))),
                         ['pin'])
        self.assertEqual(framed.uniq_id, plain.uniq_id)


##############################################
# 2.5 Resolution at realization

class ResolutionTest(BaseNodeTest):

    def test_a_frame_reads_its_declarers_parameters(self):
        Frame = _frames().Frame

        class UpperArm(AssemblyNode):
            reach = Length(160)
            elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))

        frame = resolved(UpperArm(reach=150), 'elbow_pin')

        self.assertEqual(frame.at, (0.0, 150.0, 68.0))

    def test_a_frame_reads_a_formula_over_parameters(self):
        Frame = _frames().Frame

        class UpperArm(AssemblyNode):
            reach = Length(160)
            elbow_pin = Frame(at=(0, reach / 2, 68), z=(0, 0, 1))

        frame = resolved(UpperArm(reach=150), 'elbow_pin')

        self.assertEqual(frame.at, (0.0, 75.0, 68.0))

    def test_a_frame_may_be_computed_from_the_realized_node(self):
        Frame = _frames().Frame

        class Built:
            def __init__(self, depth):
                self.bore = (0.0, 0.0, depth)

        class Boss(AssemblyNode):
            depth = Length(12)
            bore = Frame(at=lambda node: node.built.bore)

            @property
            def built(self):
                return Built(self.depth)

        self.assertEqual(resolved(Boss(depth=7), 'bore').at, (0.0, 0.0, 7.0))
        self.assertEqual(resolved(Boss(depth=9), 'bore').at, (0.0, 0.0, 9.0))

    def test_a_component_that_is_not_a_number_is_refused(self):
        Frame = _frames().Frame

        class Wrong(AssemblyNode):
            pin = Frame(at=(0, 'far', 0))

        with self.assertRaises(ParameterError) as raised:
            Wrong()

        message = str(raised.exception)
        for fragment in ('Wrong', 'pin', 'at'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)


##############################################
# 2.6, 2.7 The triad

class TriadTest(BaseNodeTest):

    def frame(self, **arguments):
        Frame = _frames().Frame

        class Holder(AssemblyNode):
            pin = Frame(**arguments)

        return resolved(Holder(), 'pin')

    def test_z_is_normalized_and_x_is_squared_up_against_it(self):
        frame = self.frame(z=(0, 0, 2), x=(1, 0, 1))

        self.assertEqual(frame.z, (0, 0, 1))
        self.assertEqual(frame.x, (1, 0, 0))
        self.assertEqual(frame.y, (0, 1, 0))

    def test_y_is_z_cross_x(self):
        frame = self.frame(z=(0, 1, 0), x=(1, 0, 0))

        self.assertEqual(frame.y, (0, 0, -1))

    def test_the_default_x_is_the_next_principal_axis(self):
        for z, expected in (((0, 0, 1), (1, 0, 0)),
                            ((1, 0, 0), (0, 1, 0)),
                            ((0, 1, 0), (0, 0, 1)),
                            ((0, 0, -1), (-1, 0, 0)),
                            ((-1, 0, 0), (0, -1, 0)),
                            ((0, -1, 0), (0, 0, -1))):
            with self.subTest(z=z):
                self.assertEqual(self.frame(z=z).x, expected)

    def test_the_default_x_is_the_zero_a_wrapped_marking_derives(self):
        for z in ((0, 0, 1), (1, 0, 0), (0, 1, 0),
                  (0, 0, -1), (-1, 0, 0), (0, -1, 0)):
            with self.subTest(z=z):
                wrapped = Wrapped(axis=z, radius=1.0, at=(0, 0, 0))
                self.assertEqual(
                    self.frame(z=z).x,
                    tuple(round(component) for component in wrapped._zero))

    def test_a_diagonal_z_must_state_x(self):
        with self.assertRaises(ParameterError) as raised:
            self.frame(z=(0, 1, 1))

        message = str(raised.exception)
        for fragment in ('Holder', 'pin', 'x'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_diagonal_z_with_x_resolves(self):
        frame = self.frame(z=(0, 1, 1), x=(1, 0, 0))

        root = math.sqrt(0.5)
        for component, expected in zip(frame.z, (0, root, root)):
            self.assertAlmostEqual(component, expected, places=12)
        self.assertEqual(frame.x, (1, 0, 0))

    def test_a_z_of_zero_length_is_refused(self):
        with self.assertRaises(ParameterError) as raised:
            self.frame(z=(0, 0, 0))

        message = str(raised.exception)
        for fragment in ('Holder', 'pin', 'z'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_an_x_parallel_to_z_is_refused(self):
        with self.assertRaises(ParameterError) as raised:
            self.frame(z=(0, 0, 1), x=(0, 0, 5))

        message = str(raised.exception)
        for fragment in ('Holder', 'pin', 'x', 'parallel'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)


##############################################
# 2.8 Refused at construction, whether or not a mate names it

class ConstructionTest(BaseNodeTest):

    def test_a_frame_that_cannot_resolve_refuses_its_declarer(self):
        Frame = _frames().Frame

        class Unmated(Solid2Node):
            pin = Frame(z=(1, 1, 0))

            def render(self):
                return cube(4)

        with self.assertRaises(ParameterError) as raised:
            Unmated()

        self.assertIn('Unmated.pin', str(raised.exception))

    def test_the_refused_declarer_realized_no_child(self):
        Frame = _frames().Frame
        built = []

        class Counted(Solid2Node):
            def __init__(self, *args, **kwargs):
                built.append(self)
                super().__init__(*args, **kwargs)

            def render(self):
                return cube(4)

        class Holder(AssemblyNode):
            pin = Frame(at=(0, 'far', 0))
            part = Counted()

        with self.assertRaises(ParameterError):
            Holder()

        self.assertEqual(built, [])


##############################################
# read-frames-and-mates, tasks 2.1 to 2.7: the resolved frames of a
# realized node, read through the documented `resolved_frames`.

def resolved_frames(node):
    """`machinome.node.frames.resolved_frames`, imported where a test
    needs it, so each test names its own failure."""
    from machinome.node.frames import resolved_frames as read

    return read(node)


def _rest_matrix(serialized_operations):
    """The rotation rows and translation a chain of serialized rest
    operations composes to, applied in list order (Rodrigues' formula,
    so this file needs no geometry library)."""
    rotation = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    translation = [0.0, 0.0, 0.0]
    for operation in serialized_operations:
        if operation[0] == 'r':
            angle = math.radians(float(operation[1]))
            axis = [float(component) for component in operation[2]]
            length = math.sqrt(sum(component * component
                                   for component in axis))
            kx, ky, kz = (component / length for component in axis)
            c, s, v = math.cos(angle), math.sin(angle), 1 - math.cos(angle)
            step = [[c + kx * kx * v, kx * ky * v - kz * s,
                     kx * kz * v + ky * s],
                    [ky * kx * v + kz * s, c + ky * ky * v,
                     ky * kz * v - kx * s],
                    [kz * kx * v - ky * s, kz * ky * v + kx * s,
                     c + kz * kz * v]]
            rotation = [[sum(step[row][k] * rotation[k][column]
                             for k in range(3)) for column in range(3)]
                        for row in range(3)]
            translation = [sum(step[row][k] * translation[k]
                               for k in range(3)) for row in range(3)]
        else:
            translation = [value + float(offset) for value, offset
                           in zip(translation, operation[1])]
    return rotation, translation


def _upper_arm():
    """The upper arm of the spec scenario "The read is what the mate
    composes": `reach` a token of the arm, a child `art3` whose class
    declares the elbow's `hinge`, and one mate between them."""
    from machinome.node.frames import Frame

    class Art3(Solid2Node):
        hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0), x=(1, 0, 0))

        def render(self):
            return cube([20, 20, 160])

    class UpperArm(AssemblyNode):
        reach = Length(160)
        elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))

        art3 = Art3()

        elbow = art3.hinge.on(elbow_pin, Revolute(range=(-135, 135)))

    return UpperArm, Art3


class ResolvedReadTest(BaseNodeTest):
    """What `resolved_frames` reads off a realized node: the frames its
    constructor resolved, as numbers, in declaration order."""

    def test_the_numbers_are_read_off_the_instance(self):
        Frame = _frames().Frame
        tokens = []

        class UpperArm(AssemblyNode):
            reach = Length(160)
            elbow_pin = Frame(at=(0, reach, 68), z=(0, 0, 1))
            tokens.append(reach)

        read = resolved_frames(UpperArm(reach=150))

        self.assertIs(type(read), dict)
        self.assertEqual(list(read), ['elbow_pin'])
        frame = read['elbow_pin']
        self.assertEqual(frame.at, (0.0, 150.0, 68.0))
        for component in frame.at:
            self.assertIs(type(component), float)
        self.assertEqual(frame.x, (1, 0, 0))
        self.assertEqual(frame.y, (0, 1, 0))
        self.assertEqual(frame.z, (0, 0, 1))
        self.assertEqual(frame.rotation(), [[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        declared = _frames().declared_frames(UpperArm)['elbow_pin']
        self.assertIs(declared, UpperArm.elbow_pin)
        self.assertIs(declared.at[1], tokens[0])

    def test_frames_are_read_in_declaration_order(self):
        Frame = _frames().Frame

        class Bracket(Solid2Node):
            top = Frame(at=(0, 0, 10))
            side = Frame(at=(5, 0, 0), z=(1, 0, 0))
            bottom = Frame(z=(0, 0, -1))

            def render(self):
                return cube(4)

        self.assertEqual(list(resolved_frames(Bracket())),
                         ['top', 'side', 'bottom'])

    def test_the_default_x_is_read_on_each_principal_z(self):
        Frame = _frames().Frame

        class Cube(Solid2Node):
            east = Frame(z=(1, 0, 0))
            west = Frame(z=(-1, 0, 0))
            north = Frame(z=(0, 1, 0))
            south = Frame(z=(0, -1, 0))
            top = Frame(z=(0, 0, 1))
            bottom = Frame(z=(0, 0, -1))

            def render(self):
                return cube(4)

        read = resolved_frames(Cube())

        # Written out, never computed: (x, y, z) for each frame.
        expected = {
            'east': ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            'west': ((0, -1, 0), (0, 0, 1), (-1, 0, 0)),
            'north': ((0, 0, 1), (1, 0, 0), (0, 1, 0)),
            'south': ((0, 0, -1), (1, 0, 0), (0, -1, 0)),
            'top': ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
            'bottom': ((-1, 0, 0), (0, 1, 0), (0, 0, -1)),
        }
        self.assertEqual(list(read), list(expected))
        for name, (x, y, z) in expected.items():
            with self.subTest(frame=name):
                frame = read[name]
                self.assertEqual((frame.x, frame.y, frame.z), (x, y, z))
                for component in frame.x + frame.y + frame.z:
                    self.assertIs(type(component), int)

    def test_a_stated_x_is_read_squared_up(self):
        Frame = _frames().Frame

        class Holder(AssemblyNode):
            pin = Frame(z=(0, 0, 2), x=(1, 0, 1))

        frame = resolved_frames(Holder())['pin']

        self.assertEqual(frame.z, (0, 0, 1))
        self.assertEqual(frame.x, (1, 0, 0))
        self.assertEqual(frame.y, (0, 1, 0))
        for component in frame.x + frame.y + frame.z:
            self.assertIsInstance(component, (int, float))

    def test_the_rotations_columns_are_the_read_triad(self):
        Frame = _frames().Frame

        class Holder(AssemblyNode):
            pin = Frame(z=(0, 1, 1), x=(1, 0, 0))

        frame = resolved_frames(Holder())['pin']

        root = math.sqrt(0.5)
        for read, expected in ((frame.x, (1, 0, 0)),
                               (frame.y, (0, root, -root)),
                               (frame.z, (0, root, root))):
            for component, value in zip(read, expected):
                self.assertAlmostEqual(component, value, delta=1e-12)
        rotation = frame.rotation()
        self.assertEqual(len(rotation), 3)
        for column, direction in enumerate((frame.x, frame.y, frame.z)):
            with self.subTest(column=column):
                self.assertEqual(tuple(row[column] for row in rotation),
                                 direction)

    def test_the_read_is_what_the_mate_composes(self):
        UpperArm, Art3 = _upper_arm()
        arm = UpperArm(reach=150)
        arm.render()

        fixed = resolved_frames(arm)['elbow_pin']
        moving = resolved_frames(arm.art3)['hinge']

        self.assertEqual(moving.x, (1, 0, 0))
        self.assertEqual(moving.y, (0, 0, -1))
        self.assertEqual(moving.z, (0, 1, 0))

        # R = F_fixed . F_moving^T, t = at_fixed - R . at_moving.
        f, m = fixed.rotation(), moving.rotation()
        rotation = [[sum(f[row][k] * m[column][k] for k in range(3))
                     for column in range(3)] for row in range(3)]
        translation = [fixed.at[row] - sum(rotation[row][k] * moving.at[k]
                                           for k in range(3))
                       for row in range(3)]

        rest = [operation.serialized for operation in arm.art3.operations]
        self.assertEqual(rest[0], ['r', '90', [1, 0, 0]])
        self.assertEqual([float(value) for value in rest[1][1]],
                         [0.0, 231.5, 68.0])
        placed_rotation, placed_translation = _rest_matrix(rest)
        for row in range(3):
            for column in range(3):
                self.assertAlmostEqual(rotation[row][column],
                                       placed_rotation[row][column],
                                       delta=1e-9)
        for ours, placed, written in zip(translation, placed_translation,
                                         (0, 231.5, 68)):
            self.assertAlmostEqual(ours, placed, delta=1e-9)
            self.assertAlmostEqual(ours, written, delta=1e-9)

    def test_the_read_holds_the_objects_the_mate_composes(self):
        # A test may read the private cache to pin the identity; the
        # public read does not depend on it.
        UpperArm, Art3 = _upper_arm()
        arm = UpperArm(reach=150)
        key = _frames().RESOLVED_KEY

        self.assertIs(resolved_frames(arm)['elbow_pin'],
                      arm.__dict__[key]['elbow_pin'])
        self.assertIs(resolved_frames(arm.art3)['hinge'],
                      arm.art3.__dict__[key]['hinge'])

    def test_a_mated_child_reads_as_its_declared_class(self):
        UpperArm, Art3 = _upper_arm()
        mated = resolved_frames(UpperArm(reach=150).art3)
        alone = resolved_frames(Art3())

        self.assertEqual(list(mated), list(alone))
        for name in alone:
            for attribute in ('at', 'x', 'y', 'z'):
                with self.subTest(frame=name, attribute=attribute):
                    self.assertEqual(getattr(mated[name], attribute),
                                     getattr(alone[name], attribute))

    def test_a_function_is_not_called_by_the_read(self):
        Frame = _frames().Frame
        calls = []

        def counting(node):
            calls.append(node)
            return (0, 0, 7)

        class Boss(Solid2Node):
            bore = Frame(at=counting)

            def render(self):
                return cube(4)

        boss = Boss()
        realized = len(calls)

        first = resolved_frames(boss)['bore']
        second = resolved_frames(boss)['bore']

        self.assertEqual(first.at, (0.0, 0.0, 7.0))
        self.assertEqual(second.at, (0.0, 0.0, 7.0))
        self.assertEqual(len(calls), realized)

    def test_each_read_is_a_fresh_mapping(self):
        UpperArm, Art3 = _upper_arm()
        arm = UpperArm(reach=150)

        first = resolved_frames(arm)
        del first['elbow_pin']
        child = resolved_frames(arm.art3)
        del child['hinge']

        self.assertEqual(list(resolved_frames(arm)), ['elbow_pin'])
        self.assertEqual(list(resolved_frames(arm.art3)), ['hinge'])

        arm.render()
        untouched = UpperArm(reach=150)
        untouched.render()
        self.assertEqual(
            [operation.serialized for operation in arm.art3.operations],
            [operation.serialized for operation in untouched.art3.operations])

    def test_a_node_declaring_no_frame_reads_nothing(self):
        self.assertEqual(resolved_frames(Plain()), {})

    def test_a_dropped_frame_is_not_read(self):
        Frame = _frames().Frame

        class Base(Solid2Node):
            hinge = Frame(at=(0, 0, 81.5), z=(0, 1, 0))
            foot = Frame()

            def render(self):
                return cube(4)

        class Footless(Base):
            foot = None

        self.assertEqual(list(resolved_frames(Footless())), ['hinge'])


class ResolvedReadRefusalTest(BaseNodeTest):
    """What `resolved_frames` refuses, by name: anything that is not a
    realized node, and a node whose frames are not yet resolved."""

    def assertRefused(self, value, *expected):
        with self.assertRaises(TypeError) as raised:
            resolved_frames(value)
        message = str(raised.exception)
        for fragment in expected:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_class_is_refused(self):
        UpperArm, Art3 = _upper_arm()

        self.assertRefused(UpperArm, 'UpperArm', 'declared_frames',
                           'instance')

    def test_a_child_declaration_is_refused(self):
        UpperArm, Art3 = _upper_arm()

        self.assertRefused(UpperArm.art3, 'ChildDeclaration',
                           'realized node')

    def test_a_frame_is_refused(self):
        Frame = _frames().Frame

        self.assertRefused(Frame(), 'Frame', 'realized node')

    def test_a_number_is_refused(self):
        self.assertRefused(3, 'int', 'realized node')

    def test_a_read_from_check_is_refused(self):
        Frame = _frames().Frame

        class Early(Solid2Node):
            width = Length(4)
            pin = Frame(at=(0, 0, 3))

            def check(self):
                resolved_frames(self)

            def render(self):
                return cube(self.width)

        with self.assertRaises(TypeError) as raised:
            Early()

        message = str(raised.exception)
        for fragment in ('Early', 'pin', 'check()', 'joints'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)

    def test_a_read_from_a_frame_argument_is_refused(self):
        # The cache is part-filled while a frame argument's callable
        # runs; the argument rule reports what the callable raised.
        Frame = _frames().Frame

        class Midway(Solid2Node):
            first = Frame(at=(0, 0, 1))
            second = Frame(
                at=lambda node: resolved_frames(node)['first'].at)

            def render(self):
                return cube(4)

        with self.assertRaises(ParameterError) as raised:
            Midway()

        message = str(raised.exception)
        for fragment in ('Midway', 'second', 'TypeError', 'check()'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, message)
