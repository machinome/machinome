# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Every exact node returns the exact engine's currency (OpenSpec change
`exact-engine`, capabilities `exact-geometry` and `occt-engine`).

`shape()` of every exact adapter, and of an exact fusion, is the bare
`OCP.TopoDS.TopoDS_Shape` the OCCT engine trades in -- never a CadQuery or
build123d object -- and a consumer that wants a front end's methods
rewraps it without changing the geometry: CadQuery's volume of the
rewrapped shape is the volume `tests/data/brep_engine_golden.json`
recorded on the unmodified tree.
"""

import json
import os
import tempfile
from pathlib import Path
from unittest import TestCase

import cadquery as cq
from OCP.TopAbs import TopAbs_COMPOUND
from OCP.TopoDS import TopoDS_Shape

from machinome.node import CadQueryNode

from . import brep_engine_golden as golden

GOLDEN = json.loads((Path(__file__).parent / 'data'
                     / 'brep_engine_golden.json').read_text())['fixtures']


class TwoBlocks(CadQueryNode):
    """A workplane holding two disjoint solids."""

    def render(self):
        return (cq.Workplane('XY').box(2, 2, 2)
                .add(cq.Workplane('XY').box(2, 2, 2).translate((5, 0, 0))))


class CurrencyTest(TestCase):

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        previous = os.environ.get('SOLID_BUILD_DIR')
        os.environ['SOLID_BUILD_DIR'] = directory.name
        self.addCleanup(self._restore, previous)

    @staticmethod
    def _restore(previous):
        if previous is None:
            os.environ.pop('SOLID_BUILD_DIR', None)
        else:
            os.environ['SOLID_BUILD_DIR'] = previous

    def assert_currency(self, shape, fixture):
        self.assertIsInstance(shape, TopoDS_Shape)
        self.assertTrue(type(shape).__module__.startswith('OCP.'),
                        type(shape))
        self.assertAlmostEqual(cq.Shape.cast(shape).Volume(),
                               float(GOLDEN[fixture]['volume']), places=9)

    def built_shape(self, node):
        node.assemble()
        return node.shape()

    def test_a_cadquery_node(self):
        self.assert_currency(self.built_shape(golden.CadQueryBoredBlock()),
                             'cadquery_bored_block')

    def test_a_build123d_node(self):
        self.assert_currency(self.built_shape(golden.Build123dBoredBlock()),
                             'build123d_bored_block')

    def test_a_build123d_sheet_node(self):
        self.assert_currency(self.built_shape(golden.Panel()),
                             'build123d_sheet_panel')

    def test_a_step_node(self):
        from tests.step_project import parts
        from tests.test_step_node import (WRAPPED_SINGLE_PART_STEP,
                                          build_wrapped_single_part)
        build_wrapped_single_part(WRAPPED_SINGLE_PART_STEP)
        self.assert_currency(self.built_shape(parts.WrappedSinglePart()),
                             'step_product')

    def test_a_molejo_node_at_a_binding(self):
        from tests.flexible_project import spring
        node = spring.Valvetrain()
        node.set_state(lift=4.0)
        node.assemble()
        self.assert_currency(node.spring.shape(), 'molejo_spring')

    def test_an_exact_fusion(self):
        fusion = golden.ShaftInBore()
        fusion.assemble()
        fusion.generate_stl()
        self.assert_currency(fusion.shape(), 'exact_fusion_shaft_in_bore')

    def test_a_workplane_of_two_solids_is_one_compound(self):
        shape = self.built_shape(TwoBlocks())

        self.assertIsInstance(shape, TopoDS_Shape)
        self.assertEqual(shape.ShapeType(), TopAbs_COMPOUND)
        from machinome.engine.brep import solid_count
        self.assertEqual(solid_count(shape), 2)

    def test_the_engine_measures_a_cadquery_shape(self):
        from machinome.engine.brep import solid_volume
        shape = cq.Workplane('XY').box(2, 3, 4).val()

        self.assertAlmostEqual(solid_volume(shape), 24.0)
