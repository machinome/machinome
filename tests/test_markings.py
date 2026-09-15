# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""A marking: what a part carries on its surface and is not made of.

OpenSpec change ``carry-markings-on-a-part``. A calculator whose answer
is the angular position of a printed number roll computes the answer
correctly and shows nothing, because the digits are not on the part, and
the only way to put them there was to declare each glyph as its own
leaf -- inventing parts no maker handles and putting phantom solids in
front of every clearance and interference contract.

So the four invariants are what most of this file is about, and they are
what a marking has to keep being true: it contributes no solid, it is not
a child, it does not key the part's artifacts, and it lives in the part's
own adjusted frame so the part's placement carries it. The fixture is
`tests/markings_project`, and it is a pair of pairs: an exact dial and a
faceted plate, each with a twin of the same class name and the same
parameters that declares no marking at all.
"""

import math
import os
import shutil
import subprocess
import tempfile
import warnings
from types import SimpleNamespace

import numpy as np

from unittest.mock import patch

from solid_node import currency
from solid_node.core.pieces import PieceInventory
from solid_node.core.export import ExportModelPathError, export_node
from solid_node.core.serializer import (document_body, drivers_table,
                                        instructions_table, serialize_node,
                                        symbolic_document)
from solid_node.simulation.enumeration import bind_declared_defaults
from solid_node.node.declarative import ChildDeclaration, identity_values
from solid_node.test import TestCase as AssertingTestCase
from solid_node.test import resolve_comparison_policy, set_comparison_policy
from solid_node.viewers.openscad import OpenScadRenderer

from .base import BaseNodeTest
from .import_probe import probe
from solid2 import cube

from solid_node.motion.joints import Revolute
from solid_node.motion.ports import TranslationalPort
from solid_node.node import (AssemblyNode, FlexibleNode, FusionNode,
                             Solid2Node)
from solid_node.node.declarative import NodeMeta
from solid_node.node.sources import MissingSourceFile
from solid_node.parameters import Length, declared_parameters
from solid_node.node.markings import (Flat, Marking, Svg, Wrapped,
                                      declared_markings)

from .markings_project.decals import badge as badge_module
from .markings_project.decals.badge import BadgeDecal, MissingBadgeDecal
from .markings_project.dial import (DIAL_ARTWORK_AT, DIAL_DEFLECTION,
                                    DIAL_RADIUS)
from .markings_project.dial import Dial as FixtureDial
from .markings_project.decals.badge import BADGE_PLANE_Z
from .markings_project.plain_dial import Dial as PlainDial
from .markings_project.plain_plate import Plate as PlainPlate
from .markings_project.plate import BAND_RADIUS
from .markings_project.plate import Plate as FixturePlate
from .markings_project.assembly import Bench, PlainBench

#: The fixture artwork, named from THIS module's directory: every
#: class declared here resolves its artwork against `tests/`.
LABEL = 'markings_project/label.svg'

# What `label.svg` measures, read off the file it is committed as. Its
# two closed regions are an 8 x 8 square with a 4 x 4 counter and a
# 6 x 6 square; its open border is 24 x 12 and is NOT part of this.
LABEL_AREA = 84.0
LABEL_MIN_X = 2.0
LABEL_MAX_X = 20.0
LABEL_MIN_Y = -10.0
LABEL_MAX_Y = -2.0


class Cube(Solid2Node):
    """A part with nothing on it, for a clash to collide with."""

    def render(self):
        return cube(4)


def _body(namespace):
    """A class body as `NodeMeta` prepares one.

    The shadow cases below cannot be written as class statements: a
    body assigning `files = Marking(...)` is a syntactically fine but
    unreadable test, and one assigning `model` shadows the name the
    test itself reads back. Building the namespace through the
    metaclass's own `__prepare__` runs exactly the path a class
    statement runs.
    """
    prepared = NodeMeta.__prepare__('Shadow', (Solid2Node,))
    for key, value in namespace.items():
        prepared[key] = value
    return prepared


class Dial(Solid2Node):
    """The declaration the whole capability is for."""

    digits = Marking(
        Svg(LABEL),
        Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45)),
        color='#FFFFFF',
    )

    def render(self):
        from solid2 import cylinder
        return cylinder(r=9.45, h=24)


class DeclarationTest(BaseNodeTest):
    """(2.1) A marking is a declaration on a rigid part."""

    def test_a_part_declares_the_artwork_it_carries(self):
        self.assertEqual(list(declared_markings(Dial)), ['digits'])

    def test_a_marking_takes_its_name_from_its_attribute(self):
        self.assertEqual(Dial.digits.name, 'digits')

    def test_the_marking_is_readable_off_an_instance(self):
        # Not a descriptor: `self.digits` is the declaration itself,
        # useful in a test and inert everywhere else.
        self.assertIs(Dial().digits, Dial.digits)

    def test_marking_kind_is_read_off_the_type_not_the_instance(self):
        # A class that declares a CHILD as well as a marking asks
        # `marking_kind` of the child's `ChildDeclaration` too, once
        # per class in the MRO. `ChildDeclaration.__getattr__` resolves
        # any non-underscore name through `read_through`, so probing
        # the INSTANCE works today only because that path ends in an
        # `AttributeError` subclass; the marker is a class attribute on
        # `Marking`, so the type answers without ever entering it.
        probed = []
        original = ChildDeclaration.__getattr__

        def spy(self, attribute):
            probed.append(attribute)
            return original(self, attribute)

        with patch.object(ChildDeclaration, '__getattr__', spy):
            class ChildAndMarking(FusionNode):
                part = Cube()
                digits = marking()

        self.assertNotIn('marking_kind', probed)
        self.assertEqual(list(declared_markings(ChildAndMarking)),
                         ['digits'])


class Plain(Dial):
    """The variant part: the same solid without its label."""

    digits = None


class Labelled(Dial):
    """A subclass that inherits the base's marking untouched."""


class TwoMarkings(Solid2Node):
    """Declaration order is a reading order."""

    digits = Marking(Svg(LABEL), Wrapped(axis=(0, 0, 1), radius=9.45,
                                         at=(0, 0, 0)), color='#FFFFFF')
    arrows = Marking(Svg(LABEL), Flat(at=(0, 0, 0), normal=(0, 0, 1),
                                      x_axis=(1, 0, 0)), color='#FF0000')

    def render(self):
        from solid2 import cube
        return cube(4)


class Badged(Solid2Node, BadgeDecal):
    """A node wearing a marking declared in a plain mixin in another
    module -- the Curta's own shape."""

    def render(self):
        from solid2 import cube
        return cube(4)


class InheritanceTest(BaseNodeTest):
    """(2.3) A marking is inherited, dropped and ordered like an
    attribute."""

    def test_a_subclass_inherits_the_markings_of_its_base(self):
        self.assertEqual(list(declared_markings(Labelled)), ['digits'])
        self.assertIs(declared_markings(Labelled)['digits'], Dial.digits)

    def test_a_subclass_assigning_none_declares_no_marking(self):
        self.assertEqual(declared_markings(Plain), {})
        self.assertEqual(list(declared_markings(Dial)), ['digits'])

    def test_two_markings_keep_their_declaration_order(self):
        self.assertEqual(list(declared_markings(TwoMarkings)),
                         ['digits', 'arrows'])

    def test_a_marking_declared_in_a_plain_mixin_belongs_to_the_node(self):
        # Python calls `__set_name__` on the mixin's marking whatever
        # its metaclass, and the walk is over `cls.__mro__`, not over
        # node classes, so the node class wearing the mixin reports it.
        self.assertEqual(list(declared_markings(Badged)), ['badge'])
        self.assertEqual(Badged.badge.name, 'badge')

    def test_the_mixins_marking_names_the_mixins_own_module(self):
        self.assertIs(Badged.badge._owner, BadgeDecal)
        self.assertEqual(
            Badged.badge._directory,
            os.path.dirname(os.path.realpath(badge_module.__file__)))


def marking(color='#FFFFFF', artwork=None, placement=None):
    """One valid marking, for a test that is about something else."""
    return Marking(
        Svg(LABEL) if artwork is None else artwork,
        Wrapped(axis=(0, 0, 1), radius=9.45,
                at=(0, 0, 0)) if placement is None else placement,
        color=color,
    )


class RigidityTest(BaseNodeTest):
    """(2.4) Only a rigid node may carry a marking."""

    def test_an_assembly_cannot_carry_a_marking(self):
        with self.assertRaises(TypeError) as raised:
            class MarkedAssembly(AssemblyNode):
                digits = marking()

        message = str(raised.exception)
        self.assertIn('MarkedAssembly', message)
        self.assertIn('digits', message)
        self.assertIn('rigid', message)

    def test_a_flexible_leaf_cannot_carry_a_marking(self):
        with self.assertRaises(TypeError) as raised:
            class MarkedSpring(FlexibleNode):
                digits = marking()

        message = str(raised.exception)
        self.assertIn('MarkedSpring', message)
        self.assertIn('digits', message)

    def test_a_rigid_leaf_and_a_fusion_are_accepted(self):
        class MarkedLeaf(Solid2Node):
            digits = marking()

        class MarkedFusion(FusionNode):
            digits = marking()

        self.assertEqual(list(declared_markings(MarkedLeaf)), ['digits'])
        self.assertEqual(list(declared_markings(MarkedFusion)), ['digits'])

    def test_a_mixins_marking_is_refused_on_the_node_that_wears_it(self):
        # The mixin knows nothing about rigidity, so the refusal belongs
        # to the node class -- where `NodeMeta.__new__` runs.
        with self.assertRaises(TypeError) as raised:
            class BadgedAssembly(AssemblyNode, BadgeDecal):
                pass

        self.assertIn('BadgedAssembly', str(raised.exception))
        self.assertIn('badge', str(raised.exception))


class Knobbed(Solid2Node):
    """A part with a parameter, a child, a port and a joint, each of
    which a marking of the same name would collide with."""

    digits = Length(4.0)
    travel = TranslationalPort(unit='mm')
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def render(self):
        return cube(self.digits)


class Framed(FusionNode):
    """A declared child, for the same reason."""

    part = Cube()


class NameClashTest(BaseNodeTest):
    """(2.5) A marking's name is a name on its node.

    Two shapes. Across a base and a subclass, a marking taking the name
    of a parameter, a child, a port or a joint declared through the
    bases is refused once the class exists, since that is where each of
    those survives to be read. Within ONE body, a second assignment
    would otherwise simply replace the first, leaving nothing to
    collide with by the time the class exists -- but
    `_DeclaringNamespace.__setitem__` is the one place that sees both
    the shadowed value and the new one as the second arrives, so a
    marking taking the name of any other declaration in the SAME body,
    in either order, is refused right there.
    """

    def test_a_marking_cannot_take_a_parameters_name(self):
        with self.assertRaises(TypeError) as raised:
            class ParameterClash(Knobbed):
                digits = marking()

        message = str(raised.exception)
        self.assertIn('ParameterClash', message)
        self.assertIn('digits', message)
        self.assertIn('declared parameter', message)

    def test_a_marking_cannot_take_a_declared_childs_name(self):
        with self.assertRaises(TypeError) as raised:
            class ChildClash(Framed):
                part = marking()

        message = str(raised.exception)
        self.assertIn('ChildClash', message)
        self.assertIn('part', message)
        self.assertIn('declared child', message)

    def test_a_marking_cannot_take_a_ports_name(self):
        with self.assertRaises(TypeError) as raised:
            class PortClash(Knobbed):
                travel = marking()

        message = str(raised.exception)
        self.assertIn('PortClash', message)
        self.assertIn('travel', message)
        self.assertIn('port', message)

    def test_a_marking_cannot_take_a_joint_coordinates_name(self):
        with self.assertRaises(TypeError) as raised:
            class JointClash(Knobbed):
                turn = marking()

        message = str(raised.exception)
        self.assertIn('JointClash', message)
        self.assertIn('turn', message)
        self.assertIn('joint', message)

    def test_a_parameter_then_a_marking_in_one_body_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class Overwritten(Solid2Node):
                digits = Length(4.0)
                digits = marking()

                def render(self):
                    return cube(4)

        message = str(raised.exception)
        self.assertIn('digits', message)
        self.assertIn('declared twice in one class body', message)
        self.assertIn('Length', message)
        self.assertIn('marking', message)

    def test_a_marking_then_a_parameter_in_one_body_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class Overwritten(Solid2Node):
                digits = marking()
                digits = Length(4.0)

                def render(self):
                    return cube(4)

        message = str(raised.exception)
        self.assertIn('digits', message)
        self.assertIn('declared twice in one class body', message)
        self.assertIn('Length', message)
        self.assertIn('marking', message)

    def test_a_marking_then_none_in_one_body_creates_the_class(self):
        class Dropped(Solid2Node):
            digits = marking()
            digits = None

            def render(self):
                return cube(4)

        self.assertEqual(list(declared_markings(Dropped)), [])


class ShadowTest(BaseNodeTest):
    """(2.6) A marking is read as an attribute of its node.

    A parameter of these names is already refused two ways -- the
    `_RESERVED` set of the attributes `__init__` assigns
    (`parameters.py:138-143`) and the MRO walk in
    `Declaration.__set_name__` right after it, which is what catches
    `color`, since `AbstractBaseNode` carries `color = None` as a class
    attribute. A marking is refused the same way.
    """

    def test_a_marking_cannot_shadow_the_nodes_colour(self):
        # First, because `color = Marking(...)` would make `self.color`
        # a Marking and break `_colorize` (`base.py:1002-1010`).
        with self.assertRaises(TypeError) as raised:
            class ColourShadow(Solid2Node):
                color = marking()

        message = str(raised.exception)
        self.assertIn('ColourShadow', message)
        self.assertIn('color', message)

    def test_a_marking_cannot_shadow_an_instance_attribute(self):
        for attribute in ('files', 'model', 'stl_file'):
            with self.subTest(attribute=attribute):
                with self.assertRaises(TypeError) as raised:
                    NodeMeta('Shadow', (Solid2Node,),
                             _body({attribute: marking()}))

                message = str(raised.exception)
                self.assertIn('Shadow', message)
                self.assertIn(attribute, message)


class MalformedTest(BaseNodeTest):
    """(2.7) A marking that is not one is refused where it is written."""

    def test_an_invalid_colour_raises_value_error(self):
        with self.assertRaises(ValueError) as raised:
            class BadColour(Solid2Node):
                digits = marking(color='white')

        message = str(raised.exception)
        self.assertIn('BadColour', message)
        self.assertIn('digits', message)

    def test_a_missing_colour_raises_value_error(self):
        with self.assertRaises(ValueError) as raised:
            class NoColour(Solid2Node):
                digits = Marking(Svg(LABEL),
                                 Flat(at=(0, 0, 0), normal=(0, 0, 1),
                                      x_axis=(1, 0, 0)))

        self.assertIn('NoColour', str(raised.exception))
        self.assertIn('digits', str(raised.exception))

    def test_an_artwork_that_is_not_an_artwork_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class BadArtwork(Solid2Node):
                digits = Marking('markings_project/label.svg',
                                 Flat(at=(0, 0, 0), normal=(0, 0, 1),
                                      x_axis=(1, 0, 0)),
                                 color='#FFFFFF')

        self.assertIn('BadArtwork', str(raised.exception))
        self.assertIn('digits', str(raised.exception))

    def test_a_placement_that_is_not_a_placement_is_refused(self):
        with self.assertRaises(TypeError) as raised:
            class BadPlacement(Solid2Node):
                digits = Marking(Svg(LABEL), (0, 0, 0), color='#FFFFFF')

        self.assertIn('BadPlacement', str(raised.exception))
        self.assertIn('digits', str(raised.exception))


class PublicModuleTest(BaseNodeTest):
    """(2.9) The four names resolve from the package, lazily."""

    def test_the_names_resolve_from_the_node_package(self):
        import solid_node.node as package
        import solid_node.node.markings as module

        for name in ('Marking', 'Wrapped', 'Flat', 'Svg'):
            with self.subTest(name=name):
                self.assertIn(name, package.__all__)
                self.assertIs(getattr(package, name), getattr(module, name))

    def test_naming_a_marking_imports_no_geometry_library(self):
        # build123d costs about 1.6 s and trimesh 0.64 s, and
        # `solid_node.node` is on every `solid` invocation's path: a
        # project that declares a marking pays for the reduction when
        # the decal is BUILT, never when the name is read.
        result = probe(
            'from solid_node.node import Marking, Wrapped, Flat, Svg\n'
            'assert isinstance(Marking, type)\n'
            "print('DONE')\n")
        self.assertEqual(result.stdout.strip(), 'DONE', result.stderr)
        self.assertFalse(result.imported('build123d'),
                         'resolving Marking imported build123d')
        self.assertFalse(result.imported('trimesh'),
                         'resolving Marking imported trimesh')
        self.assertFalse(result.imported('cadquery'),
                         'resolving Marking imported cadquery')

    def test_importing_the_module_imports_no_geometry_library(self):
        result = probe(
            'import solid_node.node.markings\n'
            "print('DONE')\n")
        self.assertEqual(result.stdout.strip(), 'DONE', result.stderr)
        self.assertFalse(result.imported('build123d'),
                         'importing the marking module imported build123d')
        self.assertFalse(result.imported('trimesh'),
                         'importing the marking module imported trimesh')


class ArtworkPathTest(BaseNodeTest):
    """(3.1) An artwork is a file beside the module that declared the
    marking."""

    def test_a_missing_artwork_is_refused_at_the_declaration(self):
        with self.assertRaises(MissingSourceFile) as raised:
            class Absent(Solid2Node):
                digits = marking(artwork=Svg('no-such-label.svg'))

        error = raised.exception
        message = str(error)
        expected = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'no-such-label.svg')
        self.assertIn('Absent', message)
        self.assertIn('digits', message)
        self.assertIn('no-such-label.svg', message)
        self.assertIn(expected, message)
        # The only thing develop-mode reload repair actually reads
        # (`builder.py:505-533` watches `exc.filename`).
        self.assertEqual(error.filename, expected)
        self.assertIsInstance(error, FileNotFoundError)

    def test_an_artwork_that_is_a_directory_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            class Directory(Solid2Node):
                digits = marking(artwork=Svg('markings_project/decals'))

        error = raised.exception
        expected = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'markings_project', 'decals')
        self.assertIn('Directory', str(error))
        self.assertIn('digits', str(error))
        self.assertIn(expected, str(error))
        self.assertEqual(error.filename, expected)
        self.assertNotIsInstance(error, FileNotFoundError)

    def test_a_subclass_reads_the_file_the_declaring_module_meant(self):
        # `Dial` declares `Svg('label.svg')` in the fixture package;
        # this subclass is declared in `tests/`, where there is no
        # `label.svg` at all.
        class InheritedDial(FixtureDial):
            pass

        self.assertEqual(
            InheritedDial.digits.artwork.resolved,
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'markings_project', 'label.svg'))

    def test_a_mixins_artwork_resolves_against_the_mixins_module(self):
        class Badged(Solid2Node, BadgeDecal):
            def render(self):
                return cube(4)

        self.assertEqual(
            Badged.badge.artwork.resolved,
            os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'markings_project', 'decals', 'badge.svg'))

    def test_a_mixins_missing_artwork_names_the_mixins_directory(self):
        with self.assertRaises(MissingSourceFile) as raised:
            class BadlyBadged(Solid2Node, MissingBadgeDecal):
                def render(self):
                    return cube(4)

        expected = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'markings_project', 'decals',
                                'no-such-badge.svg')
        self.assertEqual(raised.exception.filename, expected)
        self.assertIn(expected, str(raised.exception))


class ArtworkReductionTest(BaseNodeTest):
    """(3.2, 3.3) The drawing reduced to its closed regions."""

    def artwork(self, **kwargs):
        art = Svg(LABEL, **kwargs)
        art.resolve(os.path.dirname(os.path.abspath(__file__)),
                    Dial, 'digits')
        return art

    def test_the_closed_regions_become_faces_with_their_holes_nested(self):
        with self.assertLogs('node.markings', level='INFO'):
            regions = self.artwork().regions()

        self.assertEqual(len(regions), 2)
        # The first region is the one drawn with its counter inside it:
        # a face with one hole, not two faces.
        self.assertEqual([len(face.inner_wires()) for face in regions],
                         [1, 0])
        self.assertAlmostEqual(sum(face.area for face in regions),
                               LABEL_AREA, places=6)

    def test_the_open_border_contributes_nothing_and_is_counted(self):
        with self.assertLogs('node.markings', level='INFO') as logged:
            regions = self.artwork().regions()

        self.assertEqual(len(logged.records), 1)
        message = logged.records[0].getMessage()
        self.assertIn('label.svg', message)
        self.assertIn('1', message)
        # The regions sit where the file puts them: the border is a
        # registration mark and is not part of the drawing's extent.
        bounds = [face.bounding_box() for face in regions]
        self.assertAlmostEqual(min(box.min.X for box in bounds),
                               LABEL_MIN_X, places=6)
        self.assertAlmostEqual(max(box.max.X for box in bounds),
                               LABEL_MAX_X, places=6)
        self.assertAlmostEqual(min(box.min.Y for box in bounds),
                               LABEL_MIN_Y, places=6)
        self.assertAlmostEqual(max(box.max.Y for box in bounds),
                               LABEL_MAX_Y, places=6)

    def test_a_drawing_with_nothing_closed_is_refused(self):
        art = Svg('markings_project/open_only.svg')
        art.resolve(os.path.dirname(os.path.abspath(__file__)),
                    Dial, 'digits')

        with self.assertRaises(ValueError) as raised:
            art.regions()

        self.assertIn('open_only.svg', str(raised.exception))
        self.assertIn('closed', str(raised.exception))

    def test_an_artwork_authored_in_other_units_is_scaled(self):
        with self.assertLogs('node.markings', level='INFO'):
            scaled = self.artwork(scale=25.4).tessellate(0.1)[0]

        self.assertAlmostEqual(scaled[:, 0].min(), LABEL_MIN_X * 25.4,
                               places=6)
        self.assertAlmostEqual(scaled[:, 1].max(), LABEL_MAX_Y * 25.4,
                               places=6)


class FlatPlacementTest(BaseNodeTest):
    """(3.4) A plane, an in-plane X axis, and the artwork on it."""

    def test_points_land_on_the_declared_plane(self):
        placement = Flat(at=(0, -40, 12), normal=(0, -1, 0),
                         x_axis=(1, 0, 0))

        placed = placement.place([(0, 0), (5, 3), (-2, -7)])

        for point in placed:
            self.assertAlmostEqual(point[1], -40.0, places=9)

    def test_artwork_x_runs_along_the_orthogonalized_x_axis(self):
        # The x axis is not in the plane and not unit: both are the
        # modeller's business, not a reason to refuse.
        placement = Flat(at=(0, 0, 0), normal=(0, 0, 1), x_axis=(3, 0, 4))

        placed = placement.place([(0, 0), (1, 0), (0, 1)])

        self.assertTrue(np.allclose(placed[0], (0, 0, 0)))
        self.assertTrue(np.allclose(placed[1], (1, 0, 0)))
        # y is normal x x_axis, which is +Y here.
        self.assertTrue(np.allclose(placed[2], (0, 1, 0)))

    def test_the_artwork_origin_lands_on_the_placement_origin(self):
        placement = Flat(at=(10, 0, 0), normal=(0, 0, 1), x_axis=(1, 0, 0),
                         origin=(4, 2))

        placed = placement.place([(4, 2), (5, 2)])

        self.assertTrue(np.allclose(placed[0], (10, 0, 0)))
        self.assertTrue(np.allclose(placed[1], (11, 0, 0)))

    def test_an_x_axis_parallel_to_the_normal_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Flat(at=(0, 0, 0), normal=(0, 0, 1), x_axis=(0, 0, 2))

        message = str(raised.exception)
        self.assertIn('(0, 0, 1)', message)
        self.assertIn('(0, 0, 2)', message)


class WrappedPlacementTest(BaseNodeTest):
    """(3.5) Artwork X is arc length; artwork Y is height."""

    def test_every_point_sits_on_the_declared_cylinder(self):
        placement = Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45))

        placed = placement.place([(0, 0), (6, 2), (-3, 5), (18, -4)])

        radii = np.hypot(placed[:, 0], placed[:, 1])
        self.assertTrue(np.allclose(radii, 9.45, atol=1e-12))

    def test_artwork_y_is_height_along_the_axis_from_at(self):
        placement = Wrapped(axis=(0, 0, 1), radius=9.45, at=(0, 0, 18.45))

        placed = placement.place([(0, 0), (0, 6)])

        self.assertAlmostEqual(placed[0][2], 18.45, places=9)
        self.assertAlmostEqual(placed[1][2], 24.45, places=9)

    def test_arc_length_is_preserved_around_the_wrap(self):
        radius = 9.45
        circumference = 2 * math.pi * radius
        placement = Wrapped(axis=(0, 0, 1), radius=radius, at=(0, 0, 0))

        placed = placement.place([(0, 0), (circumference, 0),
                                  (circumference / 2, 0)])

        self.assertTrue(np.allclose(placed[0], placed[1], atol=1e-9))
        self.assertTrue(np.allclose(placed[2], (-radius, 0, 0), atol=1e-9))

    def test_a_non_positive_radius_is_refused(self):
        for radius in (0, -1.0):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError) as raised:
                    Wrapped(axis=(0, 0, 1), radius=radius, at=(0, 0, 0))

                self.assertIn('radius', str(raised.exception))


class AngularZeroTest(BaseNodeTest):
    """(3.6) The angle's zero is stated, never inferred by a reader."""

    def zero_of(self, axis, **kwargs):
        placement = Wrapped(axis=axis, radius=2.0, at=(0, 0, 0), **kwargs)
        return placement.place([(0, 0)])[0] / 2.0

    def test_the_zero_is_the_next_principal_axis_in_right_hand_order(self):
        for axis, expected in (((0, 0, 1), (1, 0, 0)),
                               ((1, 0, 0), (0, 1, 0)),
                               ((0, 1, 0), (0, 0, 1)),
                               ((0, 0, -1), (-1, 0, 0))):
            with self.subTest(axis=axis):
                self.assertTrue(
                    np.allclose(self.zero_of(axis), expected, atol=1e-12),
                    f'{axis} wrapped from {self.zero_of(axis)}')

    def test_a_positive_angle_turns_right_handed_about_the_axis(self):
        placement = Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0))

        # A quarter of the circumference along artwork X.
        quarter = math.pi * 2.0 / 2
        placed = placement.place([(quarter, 0)])[0]

        self.assertTrue(np.allclose(placed, (0, 2, 0), atol=1e-9))

    def test_a_stated_zero_wins(self):
        self.assertTrue(np.allclose(self.zero_of((0, 0, 1), zero=(0, 1, 0)),
                                    (0, 1, 0), atol=1e-12))

    def test_a_zero_parallel_to_the_axis_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0), zero=(0, 0, 1))

        message = str(raised.exception)
        self.assertIn('(0, 0, 1)', message)
        self.assertIn('zero', message)

    def test_an_axis_with_no_derivable_zero_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Wrapped(axis=(1, 1, 1), radius=2.0, at=(0, 0, 0))

        message = str(raised.exception)
        self.assertIn('(1, 1, 1)', message)
        self.assertIn('zero', message)

    def test_that_axis_is_accepted_once_its_zero_is_stated(self):
        placement = Wrapped(axis=(1, 1, 1), radius=2.0, at=(0, 0, 0),
                            zero=(1, -1, 0))

        placed = placement.place([(0, 0)])[0]

        self.assertTrue(np.allclose(placed / 2.0,
                                    (1 / math.sqrt(2), -1 / math.sqrt(2), 0),
                                    atol=1e-12))


class PitchTest(BaseNodeTest):
    """(3.7) A repeating artwork is stamped around the circle."""

    def test_a_pitch_stamps_the_artwork_around_the_circle(self):
        placement = Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0),
                            pitch=36)

        self.assertEqual(placement.repeats, 10)
        for index in range(10):
            with self.subTest(repeat=index):
                placed = placement.place([(0, 0)], repeat=index)[0]
                angle = math.radians(36 * index)
                self.assertTrue(np.allclose(
                    placed, (2 * math.cos(angle), 2 * math.sin(angle), 0),
                    atol=1e-9))

    def test_a_placement_with_no_pitch_is_stamped_once(self):
        self.assertEqual(
            Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0)).repeats, 1)
        self.assertEqual(
            Flat(at=(0, 0, 0), normal=(0, 0, 1), x_axis=(1, 0, 0)).repeats, 1)

    def test_a_pitch_that_does_not_divide_the_circle_is_refused(self):
        with self.assertRaises(ValueError) as raised:
            Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0), pitch=50)

        message = str(raised.exception)
        self.assertIn('50', message)
        # 360 / 50 is 7.2, so the nearest whole count is 7.
        self.assertIn('7', message)

    def test_a_non_positive_pitch_is_refused(self):
        for pitch in (0, -36):
            with self.subTest(pitch=pitch):
                with self.assertRaises(ValueError) as raised:
                    Wrapped(axis=(0, 0, 1), radius=2.0, at=(0, 0, 0),
                            pitch=pitch)

                self.assertIn('pitch', str(raised.exception))


def built(node_class, **kwargs):
    """One part, assembled: its artifacts are on disk afterwards."""
    node = node_class(**kwargs)
    node.assemble()
    return node


def loaded(path):
    """A marking artifact's mesh, read back as it was written."""
    import trimesh
    return trimesh.load(path, file_type='stl', process=False)


def cylinder_departure(mesh, axis_point, radius):
    """How far the built SURFACE departs from its nominal cylinder.

    Every VERTEX is on the cylinder exactly -- that is what the wrap
    computes -- so the departure of the surface is the sagitta of its
    chords, measured at the midpoint of every edge. It is the whole
    reason the wrap subdivides: two vertices of a flat triangle joined
    across an arc describe a chord, not the surface the decal sits on.
    """
    vertices = mesh.vertices - np.array(axis_point)
    edges = mesh.edges_unique
    midpoints = (vertices[edges[:, 0]] + vertices[edges[:, 1]]) / 2.0
    return float(np.max(np.abs(radius - np.hypot(midpoints[:, 0],
                                                 midpoints[:, 1]))))


class MarkingArtifactTest(BaseNodeTest):
    """(4.1) One artifact per marking, beside the part's own."""

    def test_a_marking_artifact_sits_beside_the_parts_mesh(self):
        node = built(FixtureDial)

        artifact = node.marking_file('digits')
        self.assertTrue(os.path.exists(artifact), artifact)
        self.assertEqual(os.path.dirname(artifact),
                         os.path.dirname(node.stl_file))
        self.assertTrue(
            os.path.basename(artifact).startswith(
                os.path.basename(node.stl_file)[:-len('.stl')]))
        self.assertIn('digits', os.path.basename(artifact))

    def test_two_markings_on_one_part_are_two_artifacts(self):
        node = built(FixturePlate)

        artifacts = {name: node.marking_file(name)
                     for name in ('badge', 'band')}
        self.assertEqual(len(set(artifacts.values())), 2)
        for name, path in artifacts.items():
            with self.subTest(marking=name):
                self.assertTrue(os.path.exists(path), path)
                self.assertIn(name, os.path.basename(path))

    def test_a_part_declaring_no_marking_writes_none(self):
        marked = built(FixtureDial)
        directory = os.path.dirname(marked.stl_file)
        shutil.rmtree(self.build_dir)

        built(PlainDial)

        written = sorted(os.path.basename(name)
                         for name in os.listdir(directory))
        self.assertFalse([name for name in written if 'marking' in name],
                         written)


class WrapPrecisionTest(BaseNodeTest):
    """(4.2, 4.3) The decal follows the surface it is on."""

    def test_the_wrapped_decal_follows_the_exact_parts_own_precision(self):
        node = built(FixtureDial)

        mesh = loaded(node.marking_file('digits'))
        departure = cylinder_departure(mesh, DIAL_ARTWORK_AT, DIAL_RADIUS)

        self.assertLessEqual(departure, DIAL_DEFLECTION)
        # And the part's declared precision is really the rule: the
        # framework's default would leave a chord this artwork can see.
        self.assertLess(DIAL_DEFLECTION, 0.1)

    def test_the_wrapped_decal_follows_the_faceted_parts_default(self):
        node = built(FixturePlate)

        mesh = loaded(node.marking_file('band'))
        departure = cylinder_departure(mesh, (0, 0, 10.0), BAND_RADIUS)

        self.assertFalse(hasattr(node, 'linear_deflection'))
        self.assertLessEqual(departure, 0.1)

    def test_every_vertex_sits_on_the_nominal_cylinder(self):
        node = built(FixtureDial)

        mesh = loaded(node.marking_file('digits'))
        radii = np.hypot(mesh.vertices[:, 0], mesh.vertices[:, 1])

        self.assertTrue(np.allclose(radii, DIAL_RADIUS, atol=1e-6),
                        f'{radii.min()} .. {radii.max()}')

    def test_a_flat_decal_sits_on_the_nominal_plane(self):
        node = built(FixturePlate)

        mesh = loaded(node.marking_file('badge'))

        self.assertTrue(np.allclose(mesh.vertices[:, 2], BADGE_PLANE_Z,
                                    atol=1e-9))


class CurrencyTestCase(BaseNodeTest):
    """Plumbing for the tests about when a decal is rebuilt."""

    def edited(self, path, old, new):
        """Edit a committed fixture file for one test, and put it back.

        The artwork and the module that declares the marking are both
        committed files, and what these tests are about is what happens
        when one of them CHANGES -- so the edit is real and the restore
        is registered before it is made.
        """
        original = open(path, 'rb').read()

        def restore():
            with open(path, 'wb') as handle:
                handle.write(original)

        self.addCleanup(restore)
        text = original.decode()
        self.assertIn(old, text)
        with open(path, 'w') as handle:
            handle.write(text.replace(old, new))

    def state(self, path):
        """What a build has to leave alone: the bytes and the stamp."""
        return (open(path, 'rb').read(), os.stat(path).st_mtime_ns)


class MarkingRecipeTest(CurrencyTestCase):
    """(4.5) The rule that produced a decal is not all in its sources."""

    def test_the_marking_artifact_records_its_producer_recipe(self):
        node = built(FixtureDial)

        self.assertEqual(
            currency.recorded_recipe(node.marking_file('digits')),
            f'marking-svg-v1:{DIAL_DEFLECTION}')

    def test_the_solids_own_artifacts_record_no_recipe(self):
        node = built(FixtureDial)

        for path in (node.stl_file, node.brep_file, node.scad_file):
            with self.subTest(artifact=os.path.basename(path)):
                self.assertIsNone(node._artifact_recipe(path))
                self.assertIsNone(currency.recorded_recipe(path))

    def test_an_unchanged_recipe_reuses_the_decal(self):
        built(FixtureDial)

        second = FixtureDial()
        path = second.marking_file('digits')
        sources = second.marking_sources(second.digits)

        self.assertTrue(second._up_to_date(path, sources))

    def test_a_recipe_from_another_producer_re_derives_the_decal(self):
        node = built(FixtureDial)
        path = node.marking_file('digits')
        before = self.state(path)
        sources = node.marking_sources(node.digits)

        # Every source is unchanged; only the recorded recipe differs,
        # as it would after the meshing rule or the framework default
        # changed underneath an existing build.
        currency.record(path, currency.recorded_digest(path),
                        currency.recorded_fingerprint(path),
                        'marking-svg-v0:9.99')

        second = FixtureDial()
        self.assertFalse(second._up_to_date(path, sources))

        second._prepare()

        self.assertEqual(currency.recorded_recipe(path),
                         f'marking-svg-v1:{DIAL_DEFLECTION}')
        self.assertEqual(open(path, 'rb').read(), before[0])


class SkipDecisionTest(CurrencyTestCase):
    """(4.6) A decal is not the sheet leaf's DXF.

    `SheetLeafNode` widens both leaf skip predicates because its DXF is
    derived FROM the rendered profile, so a lost DXF genuinely needs the
    render back. A marking is derived from the artwork and the
    declaration and never from the render, so the predicates are left
    exactly as they are (`leaf.py:41-65`) and the decal is built outside
    them -- and the evidence for that is the SPY, not the artifact.
    """

    def test_a_current_marking_is_not_rewritten(self):
        built(FixtureDial)

        second = FixtureDial()
        with patch.object(Marking, 'mesh_bytes',
                          side_effect=AssertionError('must not re-mesh')):
            second._prepare()

    def test_a_deleted_decal_comes_back_without_the_parts_render(self):
        node = built(FixtureDial)
        path = node.marking_file('digits')
        solid = self.state(node.stl_file)
        exact = self.state(node.brep_file)
        os.remove(path)

        second = FixtureDial()
        self.assertTrue(second._up_to_date(second.stl_file))
        with patch.object(type(second), 'render',
                          side_effect=AssertionError('must not render')), \
                patch.object(type(second), 'materialize',
                             side_effect=AssertionError('must not write')):
            second._prepare()

        self.assertTrue(os.path.exists(path))
        self.assertEqual(self.state(second.stl_file), solid)
        self.assertEqual(self.state(second.brep_file), exact)

    def test_the_leaf_skip_predicates_are_not_widened(self):
        # The other half of the same statement: a missing decal is not a
        # reason to re-enter the render path at all.
        node = built(FixtureDial)
        os.remove(node.marking_file('digits'))

        second = FixtureDial()

        self.assertTrue(second._prepare_can_be_skipped())
        self.assertTrue(second._render_can_be_skipped())

    def test_the_spy_does_see_the_render_when_the_solid_is_stale(self):
        node = built(FixtureDial)
        os.remove(node.stl_file)

        second = FixtureDial()
        rendered = []
        with patch.object(type(second), 'render',
                          side_effect=lambda: rendered.append(True)):
            with self.assertRaises(Exception):
                second._prepare()

        self.assertEqual(len(rendered), 1)


class SeparateCurrencyTest(CurrencyTestCase):
    """(4.7, 4.8) The artwork rebuilds the decal; the declaration
    rebuilds the part."""

    def test_the_artwork_is_not_in_the_parts_tracked_sources(self):
        node = built(FixtureDial)

        artwork = node.digits.artwork.resolved
        self.assertNotIn(artwork, node.files)
        self.assertIn(artwork, node.marking_sources(node.digits))

    def test_editing_the_artwork_rebuilds_only_the_decal(self):
        node = built(FixtureDial)
        path = node.marking_file('digits')
        solid = self.state(node.stl_file)
        exact = self.state(node.brep_file)
        decal = self.state(path)

        self.edited(node.digits.artwork.resolved,
                    '<!-- A plain closed region. -->',
                    '<!-- A plain closed region, edited. -->')

        second = FixtureDial()
        sources = second.marking_sources(second.digits)
        self.assertFalse(second._up_to_date(path, sources))
        self.assertTrue(second._up_to_date(second.stl_file))
        self.assertTrue(second._up_to_date(second.brep_file))

        second._prepare()

        self.assertNotEqual(self.state(path)[1], decal[1])
        self.assertEqual(self.state(second.stl_file), solid)
        self.assertEqual(self.state(second.brep_file), exact)

    def test_editing_the_declaration_rebuilds_the_part(self):
        # The accepted consequence of the currency split: the class body
        # is in the node's scoped source digest (ADR-071), which is
        # scoped per class and not per statement, so moving a decal
        # rebuilds the part it is on. One part, one rebuild, recorded
        # rather than engineered around.
        node = built(FixtureDial)

        self.edited(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 'markings_project', 'dial.py'),
                    'start=0.0),', 'start=90.0),')

        second = FixtureDial()

        self.assertFalse(second._up_to_date(second.stl_file))
        self.assertFalse(second._up_to_date(second.brep_file))


def piece_of(node):
    """The piece id a published document would carry for `node`."""
    with PieceInventory(publish_facts=False) as inventory:
        return inventory.register(node, os.path.basename(node.stl_file))


class SolidIdentityTest(BaseNodeTest):
    """(5.1) A marking contributes no solid and keys no artifact."""

    def test_the_exact_solid_is_byte_identical_with_and_without_markings(self):
        marked = built(FixtureDial)
        plain = built(PlainDial)

        self.assertEqual(marked.uniq_id, plain.uniq_id)
        self.assertEqual(open(marked.stl_file, 'rb').read(),
                         open(plain.stl_file, 'rb').read())
        self.assertEqual(open(marked.brep_file, 'rb').read(),
                         open(plain.brep_file, 'rb').read())
        self.assertEqual(piece_of(marked), piece_of(plain))

    def test_the_faceted_solid_is_byte_identical_too(self):
        marked = built(FixturePlate)
        plain = built(PlainPlate)

        self.assertEqual(marked.uniq_id, plain.uniq_id)
        self.assertEqual(open(marked.stl_file, 'rb').read(),
                         open(plain.stl_file, 'rb').read())
        self.assertEqual(piece_of(marked), piece_of(plain))
        # An StlNode is faceted: neither part writes exact geometry, so
        # the BREP half of the comparison is the exact pair's alone.
        self.assertFalse(marked.exact)
        self.assertFalse(os.path.exists(marked.brep_file))
        self.assertFalse(os.path.exists(plain.brep_file))

    def test_a_marking_does_not_key_the_artifact(self):
        # Not a `Declaration`, so it never reaches `identity_values` or
        # `_build_uniq_id`: there is no code path by which a marking
        # can change an artifact key.
        self.assertEqual(FixtureDial().uniq_id, PlainDial().uniq_id)
        self.assertEqual(FixturePlate().uniq_id, PlainPlate().uniq_id)
        self.assertNotIn('digits', identity_values(
            FixtureDial, FixtureDial().__dict__.get('_parameters', {})))


class NoSolidTest(BaseNodeTest):
    """(5.2) Every geometric verdict is the verdict without the
    markings."""

    def setUp(self):
        super().setUp()
        self.addCleanup(set_comparison_policy, None)

    def trees(self):
        trees = []
        for factory in (Bench, PlainBench):
            node = factory()
            bind_declared_defaults(node)
            node.assemble()
            trees.append(node)
        return trees

    def verdicts(self, node):
        asserter = AssertingTestCase()
        results = []
        for assertion in (asserter.assertNoSolidInterference,
                          asserter.assertNoDisconnectedSolids):
            try:
                assertion(node)
                results.append('passed')
            except AssertionError as failure:
                results.append(str(failure))
        return results

    def test_every_verdict_is_the_same_under_both_kernels(self):
        marked, plain = self.trees()

        for kernel in ('faceted', 'exact'):
            with self.subTest(kernel=kernel):
                set_comparison_policy(
                    resolve_comparison_policy(kernel=kernel))
                self.assertEqual(self.verdicts(marked),
                                 self.verdicts(plain))
                self.assertEqual(self.verdicts(marked), ['passed', 'passed'])

    def test_the_pairwise_sweep_agrees(self):
        marked, plain = self.trees()
        asserter = AssertingTestCase()

        with warnings.catch_warnings():
            warnings.simplefilter('ignore', DeprecationWarning)
            asserter.assertNoPairwiseIntersections(marked)
            asserter.assertNoPairwiseIntersections(plain)

    def test_volume_and_bounds_are_unchanged(self):
        marked, plain = self.trees()

        for carrying, without in ((marked.dial, plain.dial),
                                  (marked.plate, plain.plate)):
            with self.subTest(part=carrying.name):
                self.assertAlmostEqual(carrying.mesh.volume,
                                       without.mesh.volume, places=9)
                self.assertTrue(np.allclose(carrying.mesh.bounds,
                                            without.mesh.bounds))

    def test_a_marking_is_not_in_the_tree(self):
        marked, plain = self.trees()

        self.assertEqual(marked.dial.children, tuple())
        self.assertEqual(marked.plate.children, tuple())
        self.assertEqual(len(marked.children), len(plain.children))
        self.assertEqual([child.name for child in marked.children],
                         [child.name for child in plain.children])
        for child in marked.children:
            self.assertNotIn('digits', child.name)
            self.assertNotIn('badge', child.name)
            self.assertNotIn('band', child.name)


def entry_of(node, **kwargs):
    """One rigid node's document entry, with the markings resolved the
    way a producer resolves a model: to a reference of its own."""
    return serialize_node(node, lambda rigid: os.path.basename(
        rigid.stl_file), **kwargs)


def marking_reference(rigid, artifact):
    return os.path.basename(artifact)


class DocumentTest(CurrencyTestCase):
    """(5.3, 5.4) What a part publishes about what it carries."""

    def test_a_part_publishes_the_markings_it_carries(self):
        node = built(FixturePlate)

        entry = entry_of(node, marking_path=marking_reference)

        self.assertEqual([published['name']
                          for published in entry['markings']],
                         ['badge', 'band'])
        for published in entry['markings']:
            with self.subTest(marking=published['name']):
                self.assertEqual(sorted(published),
                                 ['color', 'model', 'mtime', 'name'])
                self.assertNotIn('piece', published)
        self.assertEqual(entry['markings'][0]['color'], '#FFFFFF')
        self.assertEqual(entry['markings'][1]['color'], '#C0C0C0')
        self.assertEqual(
            entry['markings'][0]['model'],
            os.path.basename(node.marking_file('badge')))

    def test_a_part_declaring_no_marking_has_no_markings_key(self):
        node = built(PlainPlate)

        entry = entry_of(node, marking_path=marking_reference)

        self.assertNotIn('markings', entry)

    def test_a_producer_that_resolves_no_marking_publishes_none(self):
        # Every existing caller passes only `model_path`, and keeps the
        # document it published.
        node = built(FixturePlate)

        self.assertNotIn('markings', entry_of(node))

    def test_the_piece_inventory_is_unchanged_by_the_markings(self):
        marked = built(FixturePlate)
        plain = built(PlainPlate)

        with PieceInventory(publish_facts=False) as inventory:
            entry = serialize_node(
                marked, lambda rigid: os.path.basename(rigid.stl_file),
                inventory.register, marking_path=marking_reference)
            pieces = inventory.pieces()
        with PieceInventory(publish_facts=False) as inventory:
            serialize_node(plain,
                           lambda rigid: os.path.basename(rigid.stl_file),
                           inventory.register)
            without = inventory.pieces()

        self.assertEqual(len(pieces), 1)
        self.assertEqual([piece['id'] for piece in pieces],
                         [piece['id'] for piece in without])
        for published in entry['markings']:
            self.assertNotIn(
                published['model'],
                [model for piece in pieces for model in piece['models']])

    def test_a_markings_mtime_is_its_own(self):
        node = built(FixtureDial)
        before = entry_of(node, marking_path=marking_reference)

        self.edited(node.digits.artwork.resolved,
                    '<!-- A plain closed region. -->',
                    '<!-- A plain closed region, edited. -->')

        second = FixtureDial()
        second._prepare()
        after = entry_of(second, marking_path=marking_reference)

        self.assertNotEqual(after['markings'][0]['mtime'],
                            before['markings'][0]['mtime'])
        self.assertEqual(after['mtime'], before['mtime'])
        self.assertEqual(after['model'], before['model'])


#: Every key a rigid node's entry carried before markings existed.
PUBLISHED_NODE_FIELDS = {'name', 'type', 'color', 'mtime', 'operations',
                         'model'}


class ByteIdentityTest(BaseNodeTest):
    """(5.6) A document with no marking is the document it always was.

    Nothing under `tests/base_documents/` is recaptured, and nothing is
    added to it: those seven captures are earlier cycles' BASES, and a
    capture regenerated with this cycle's code would assert nothing at
    all. `tests/test_running_document.py`'s `ByteIdentityTest` keeps
    comparing this cycle's output against pre-marking bytes, and the
    marking fixture -- which existed at no base -- is asserted
    structurally here instead.
    """

    def published(self, node):
        bind_declared_defaults(node)
        node.assemble()
        with symbolic_document(node) as (declarations, instructions):
            root = serialize_node(
                node, lambda rigid: os.path.basename(rigid.stl_file),
                graph_values=True,
                marking_path=marking_reference)
            body = document_body(node, root, drivers_table(declarations),
                                 instructions_table(instructions))
        body['root'] = root
        return body

    def walk(self, entry):
        yield entry
        for child in entry.get('children', ()):
            yield from self.walk(child)

    def test_the_marking_free_tree_publishes_no_markings_key(self):
        document = self.published(PlainBench())

        for entry in self.walk(document['root']):
            with self.subTest(node=entry['name']):
                self.assertNotIn('markings', entry)

    def test_the_marking_free_tree_declares_the_version_it_needed(self):
        document = self.published(PlainBench())

        self.assertEqual(document['format'], 'solid-node-export')
        self.assertEqual(document['version'], 2)
        self.assertNotIn('program', document)
        self.assertNotIn('bindings', document)

    def test_every_node_field_is_the_set_published_today(self):
        document = self.published(PlainBench())

        for entry in self.walk(document['root']):
            with self.subTest(node=entry['name']):
                expected = set(PUBLISHED_NODE_FIELDS)
                if 'children' in entry:
                    expected = (expected - {'model'}) | {'children'}
                self.assertEqual(set(entry), expected)

    def test_the_marked_tree_adds_the_key_and_nothing_else(self):
        marked = self.published(Bench())
        plain = self.published(PlainBench())

        self.assertEqual(marked['version'], plain['version'])
        self.assertEqual(marked['format'], plain['format'])
        self.assertEqual(marked['animation'], plain['animation'])
        for entry in self.walk(marked['root']):
            with self.subTest(node=entry['name']):
                self.assertEqual(set(entry) - {'markings'},
                                 set(PUBLISHED_NODE_FIELDS)
                                 if 'children' not in entry
                                 else (set(PUBLISHED_NODE_FIELDS)
                                       - {'model'}) | {'children'})


class ExportMarkingTest(BaseNodeTest):
    """(5.7) An export carries the markings it names."""

    def exported(self, node):
        bind_declared_defaults(node)
        self.out_dir = os.path.join(self.build_dir, 'export_out')
        manifest = export_node(node, self.out_dir, widget=False)
        return manifest

    def test_every_named_marking_is_copied_under_models(self):
        manifest = self.exported(Bench())

        published = [entry for entry in manifest['root']['children']
                     if 'markings' in entry]
        self.assertEqual(len(published), 2)
        for entry in published:
            for marking in entry['markings']:
                with self.subTest(marking=marking['name']):
                    reference = marking['model']
                    self.assertTrue(reference.startswith('models/'))
                    self.assertNotIn('..', reference)
                    copied = os.path.join(self.out_dir, reference)
                    self.assertTrue(os.path.exists(copied), copied)
                    self.assertGreater(os.path.getsize(copied), 0)

    def test_a_marking_outside_the_build_fails_before_output(self):
        node = Bench()
        bind_declared_defaults(node)
        node.assemble()
        outside = os.path.join(tempfile.mkdtemp(), 'stray.marking-digits.stl')
        self.addCleanup(shutil.rmtree, os.path.dirname(outside),
                        ignore_errors=True)
        with open(outside, 'wb') as handle:
            handle.write(b'')
        out_dir = os.path.join(self.build_dir, 'refused_export')

        with patch.object(type(node.dial), 'marking_file',
                          return_value=outside):
            with self.assertRaises(ExportModelPathError):
                export_node(node, out_dir, widget=False)

        self.assertFalse(os.path.exists(out_dir))


class SweepTest(BaseNodeTest):
    """(5.8) A marking is spared by reference, not by kind."""

    def builder_for(self, node):
        from solid_node.core.builder import Builder

        bind_declared_defaults(node)
        node.assemble()
        node.build_stls()
        builder = Builder('model.py', build_dir=self.build_dir, watch=False)
        builder.node = node
        return builder

    def test_a_declared_marking_survives_the_sweep(self):
        node = Bench()
        builder = self.builder_for(node)

        builder._write_viewer_snapshot()

        for part, names in ((node.dial, ('digits',)),
                            (node.plate, ('badge', 'band'))):
            for name in names:
                with self.subTest(marking=name):
                    self.assertTrue(os.path.exists(part.marking_file(name)))

    def test_a_dropped_marking_leaves_nothing_behind(self):
        node = Bench()
        builder = self.builder_for(node)
        builder._write_viewer_snapshot()
        dropped = node.dial.marking_file('digits')
        kept = node.plate.marking_file('badge')
        self.assertTrue(os.path.exists(dropped))
        solid = open(node.dial.stl_file, 'rb').read()

        # The declaration is gone: the next successful publication
        # names the artifact nowhere, and the sweep takes it.
        with patch.object(type(node.dial), 'declared_markings',
                          return_value={}):
            builder._write_viewer_snapshot()

        self.assertFalse(os.path.exists(dropped))
        self.assertTrue(os.path.exists(kept))
        self.assertTrue(os.path.exists(node.dial.stl_file))
        self.assertTrue(os.path.exists(node.dial.brep_file))
        self.assertEqual(open(node.dial.stl_file, 'rb').read(), solid)


class OpenScadPathTest(BaseNodeTest):
    """(5.9) The OpenSCAD path does not draw markings, and does not
    fail."""

    def scad_of(self, factory):
        node = factory()
        bind_declared_defaults(node)
        node.assemble()
        return node, node.scad_code

    def test_the_scad_is_what_it_is_without_the_markings(self):
        marked, with_markings = self.scad_of(Bench)
        plain, without = self.scad_of(PlainBench)

        # The artifact names differ only by the module each twin is
        # declared in; nothing of a marking reaches the SCAD at all.
        self.assertNotIn('marking', with_markings)
        self.assertEqual(
            with_markings.replace('dial-Dial', 'X').replace(
                'plate-Plate', 'Y'),
            without.replace('plain_dial-Dial', 'X').replace(
                'plain_plate-Plate', 'Y'))

    def test_the_openscad_renderer_photographs_the_marked_model(self):
        node = Bench()
        bind_declared_defaults(node)
        node.assemble()
        node.build_stls()

        output = os.path.join(self.build_dir, 'bench.png')
        OpenScadRenderer().render(
            node,
            SimpleNamespace(imgsize='120,90', time=0, camera=None, path=None,
                            autocenter=True, viewall=True, projection=None,
                            colorscheme=None, preview=False, view=None),
            output, subprocess.run)

        self.assertTrue(os.path.exists(output))
        self.assertGreater(os.path.getsize(output), 0)
