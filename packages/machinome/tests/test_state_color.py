# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""One retained body's two colors, native and ordinary publication."""
import json
import math
from unittest import TestCase

from machinome.color import color_when
from machinome.expression_graph import GraphValue, symbol
from machinome.core.serializer import (
    compiled_clocked, compiled_controls, compiled_program, document_body,
    drivers_table, instructions_table, serialize_node, symbolic_document,
)
from machinome.simulation import Sim
from machinome.simulation.enumeration import bind_declared_defaults

from .color_project.model import Clocked, Posed, Running, FailingPublication, OFF, ON


def document(node):
    program, initial = compiled_program(node)
    clocked, clocked_initial = compiled_clocked(node)
    if clocked is not None:
        initial = clocked_initial
    with symbolic_document(node) as (declarations, instructions):
        root = serialize_node(node, lambda leaf: leaf.local_stl, graph_values=True)
        drivers = drivers_table(declarations)
        events = instructions_table(instructions, version_five_or_above=program is not None or clocked is not None)
    result = document_body(node, root, drivers, events, program, initial,
                           controls=compiled_controls(program, initial), clocked=clocked)
    result['root'] = root
    return result


class ColorValueTest(TestCase):
    def test_numeric_truth_returns_the_original_fixed_hex(self):
        for value, expected in [(False, OFF), (0, OFF), (-0., OFF), (True, ON), (-2., ON), (0.01, ON), (10 ** 400, ON)]:
            with self.subTest(value=value):
                self.assertEqual(color_when(value, on=ON, off=OFF), expected)

    def test_both_palettes_are_validated_even_when_not_selected(self):
        for key in ('on', 'off'):
            for bad in ('red', '#123', '123456', '#12345z', None, 123):
                palette = dict(on=ON, off=OFF); palette[key] = bad
                with self.subTest(key=key, bad=bad), self.assertRaisesRegex(ValueError, key):
                    color_when(False, **palette)

    def test_invalid_conditions_are_named(self):
        for bad in (math.nan, math.inf, -math.inf):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, 'condition'):
                color_when(bad, on=ON, off=OFF)
        for bad in ('x', None, [], object(), complex(1)):
            with self.subTest(bad=type(bad)), self.assertRaisesRegex(TypeError, 'condition'):
                color_when(bad, on=ON, off=OFF)

    def test_symbolic_truth_is_never_requested(self):
        condition = symbol('powered') > .5
        choice = color_when(condition, on=ON, off=OFF)
        self.assertEqual(str(GraphValue(choice.condition)), '(powered > 0.5)')
        self.assertEqual((choice.on, choice.off), (ON, OFF))
        with self.assertRaises((AttributeError, TypeError)):
            choice.on = OFF


class PublishedColorTest(TestCase):
    def test_three_modes_publish_the_same_choice_and_restore_numeric_color(self):
        for cls, key in ((Posed, None), (Clocked, 'clocked'), (Running, 'program')):
            with self.subTest(mode=cls.__name__):
                node = cls(); bind_declared_defaults(node); node.set_state(powered=1)
                before = dict(node._states)
                result = document(node)
                self.assertEqual(result['version'], 14)
                choice = result['root']['children'][0]['color']
                self.assertEqual(set(choice), {'when', 'on', 'off'})
                self.assertEqual((choice['on'], choice['off']), (ON, OFF))
                self.assertEqual(node.glass.color, ON)
                self.assertEqual(node._states, before)
                self.assertEqual('clocked' in result, key == 'clocked')
                self.assertEqual('program' in result, key == 'program')
                json.dumps(result)

    def test_failure_during_symbolic_traversal_restores_color_state_and_pose(self):
        node = FailingPublication(); bind_declared_defaults(node); node.set_state(powered=1, independent=3)
        before = dict(node._states)
        before_ops = [op.serialized for op in node.glass.operations]
        with self.assertRaisesRegex(RuntimeError, 'after color assignment'):
            document(node)
        self.assertEqual(node._states, before)
        self.assertEqual(node.glass.color, ON)
        self.assertEqual([op.serialized for op in node.glass.operations], before_ops)

    def test_reset_restore_and_replay_recompute_the_same_body_color(self):
        for cls in (Clocked, Running):
            with self.subTest(mode=cls.__name__):
                node = cls(); sim = Sim(node, **({'dt': .02} if cls is Running else {}))
                body = node.glass
                states = []
                for value in (0, 1, 0):
                    sim.move('powered', to=value)
                    states.append(node.glass.color)
                self.assertEqual(states, [OFF, ON, OFF])
                sim.move('powered', to=1); lit = sim.snapshot()
                sim.reset(); self.assertEqual(node.glass.color, OFF)
                sim.restore(lit); self.assertEqual(node.glass.color, ON)
                sim.reset()
                for value in (0, 1, 0): sim.move('powered', to=value)
                self.assertEqual(node.glass.color, OFF)
                self.assertIs(node.glass, body)

class RelationObservationTest(TestCase):
    def test_list_held_real_glass_reads_settled_signal_at_presentation(self):
        from .color_project.model import PropertyPosed
        node = PropertyPosed(); bind_declared_defaults(node)
        glass = node.lamps.bulbs[0]
        for value, expected in ((0, OFF), (1, ON), (0, OFF)):
            node.set_state(powered=value)
            self.assertEqual(glass.color, expected)
            node.assemble()
            result = document(node)
            self.assertEqual(result['version'], 14)
            choice = result['root']['children'][1]['children'][0]['color']
            self.assertEqual((choice['on'], choice['off']), (ON, OFF))
            self.assertEqual(glass.color, expected)
            self.assertIs(node.lamps.bulbs[0], glass)

class SharingAndGeometryTest(TestCase):
    def test_shared_predicate_is_bound_once_with_placement(self):
        from .color_project.model import Shared
        node = Shared(); bind_declared_defaults(node)
        result = document(node)
        conditions = [child['color']['when'] for child in result['root']['children']]
        self.assertEqual(conditions[0], conditions[1])
        self.assertEqual([entry['expression'] for entry in result['bindings']].count('(powered > 0.5)'), 1)

    def test_nested_choice_uses_the_same_qualified_driver_scope(self):
        from .color_project.model import Nested
        node = Nested(); bind_declared_defaults(node)
        result = document(node)
        self.assertEqual(result['root']['children'][0]['children'][0]['color']['when'], '(unit.powered > 0.5)')
        self.assertIn('unit.powered', result['drivers'])

    def test_a_numeric_choice_keeps_the_legacy_version_and_color_string(self):
        from .color_project.model import NumericChoice
        node = NumericChoice(); bind_declared_defaults(node)
        result = document(node)
        self.assertEqual(result['version'], 2)
        self.assertEqual(result['root']['children'][0]['color'], ON)

    def test_symbolic_presentation_channels_select_the_exact_palette(self):
        from .color_project.model import Glass
        glass = Glass()
        glass.color = color_when(symbol('powered'), on=ON, off=OFF)
        presentation = glass._colorize(object())
        for value, expected in ((0, OFF), (-1, ON), (1, ON)):
            channels = [channel.evaluate({'powered': value}) for channel in presentation.rgb]
            native = [int(expected[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            for actual, wanted in zip(channels, native): self.assertAlmostEqual(actual, wanted)

class ArtifactIdentityTest(TestCase):
    def test_same_glass_mesh_piece_and_volume_survive_color_only_updates(self):
        import hashlib
        import os
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from machinome.core.export import export_node
        from machinome.core.pieces import PieceInventory
        from machinome.core import builder
        from .color_project.model import Posed
        with tempfile.TemporaryDirectory(prefix='machinome-color-geometry-') as directory:
            with patch.dict(os.environ, SOLID_BUILD_DIR=directory), patch.object(builder, '_anchor', None):
                node = Posed(); bind_declared_defaults(node)
                node.build_stls()
                glass = node.glass
                identity = None
                for value in (0, 1, 0):
                    node.set_state(powered=value)
                    path = Path(glass.stl_file)
                    with PieceInventory() as inventory:
                        piece = inventory.register(glass, glass.local_stl)
                    current = (glass.local_stl, hashlib.sha256(path.read_bytes()).hexdigest(), piece,
                               glass.mesh.volume, tuple(glass.mesh.extents))
                    if identity is None: identity = current
                    self.assertEqual(current, identity)
                    self.assertAlmostEqual(current[3], 864.)
                    self.assertEqual(current[4], (12., 12., 6.))
                exported = export_node(node, str(Path(directory) / 'export'), widget=False)
                self.assertEqual(exported['version'], 14)
                self.assertEqual(exported['root']['children'][0]['piece'], identity[2])

class NativeAppearanceAdmissionTest(TestCase):
    def test_invalid_later_color_preserves_clocked_bank_events_and_earlier_glass(self):
        from .color_project.model import InvalidClocked
        node = InvalidClocked(); sim = Sim(node, record=20)
        before = dict(sim.state)
        before_events = list(sim.commits)
        before_colors = (node.glass.color, node.later.color)
        with self.assertRaises(ValueError):
            sim.move('powered', to=3)
        self.assertEqual(sim.state, before)
        self.assertEqual(list(sim.commits), before_events)
        self.assertEqual((node.glass.color, node.later.color), before_colors)
        sim.move('independent', to=2)
        self.assertEqual(node.glass.color, OFF)
        sim.move('powered', to=1)
        self.assertEqual(node.glass.color, ON)

class PublicationIdentityTest(TestCase):
    def test_two_presentations_share_one_clocked_identity(self):
        from .color_project.model import PublicationChoice
        documents = []
        for unsafe in (False, True):
            node = PublicationChoice(unsafe=unsafe); bind_declared_defaults(node)
            documents.append(document(node))
        self.assertEqual(documents[0]['clocked']['identity'], documents[1]['clocked']['identity'])
        self.assertNotEqual(documents[0]['root']['children'][0]['color']['when'], documents[1]['root']['children'][0]['color']['when'])

    def test_retained_state_selects_color_without_becoming_an_input(self):
        from .color_project.model import ClockedStateColor
        node = ClockedStateColor(); sim = Sim(node)
        self.assertEqual(node.glass.color, OFF)
        sim.move('powered', to=1)
        self.assertEqual(node.glass.color, ON)
        powered = sim.snapshot()
        sim.reset(); self.assertEqual(node.glass.color, OFF)
        sim.restore(powered); self.assertEqual(node.glass.color, ON)
        result = document(node)
        self.assertIn('count', result['states'])
        self.assertNotIn('count', result['drivers'])
        self.assertEqual(result['root']['children'][0]['color']['when'], '(count > 0)')
