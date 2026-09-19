# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""`machinome import-step`: the generator and the command.

Two projects wrote the walk this scaffold now generates by hand
(`Internal-Cycloidal-Actuator`, `openvmp`) -- this module proves the
generator's naming rules, the content of the two files it writes, that
a generated model composes the placements `StepAssembly` reads
faithfully, and the command's argument handling, refusal-to-overwrite,
propriety gate and missing-kernel report.

No binary STEP is committed: every fixture is authored with
`cadquery.Assembly` and exported into a temporary build directory, as
`test_step_assembly.py` and `test_step_node.py` do.
"""

import importlib
import itertools
import os
import re
import shutil
import sys
import tempfile
from argparse import Namespace
from unittest import TestCase
from unittest.mock import patch

import cadquery as cq
import numpy as np

from machinome.manager import import_step
from machinome.manager.import_step import (
    ImportStep, _attribute_name_base, _class_name_base, generate_assembly,
    generate_parts,
)
from machinome.node.adapters import step as step_module
from machinome.node.adapters.step import StepAssembly
from machinome.node.base import _compose_world_matrix

from .step_project import parts as _parts_module


PROJECT = os.path.dirname(os.path.realpath(_parts_module.__file__))

SIMPLE_STEP = os.path.join(PROJECT, 'import_simple.step')
NESTED_STEP = os.path.join(PROJECT, 'import_nested.step')
REPEATED_STEP = os.path.join(PROJECT, 'import_repeated.step')
DUPLICATE_NAMES_STEP = os.path.join(PROJECT, 'import_duplicate_names.step')
DUP_SUBASSEMBLY_STEP = os.path.join(PROJECT, 'import_dup_subassembly.step')

PACKAGE_NAMES = itertools.count()


def _class_body(source, class_name):
    """The exact text of one generated class's body -- up to the next
    unindented `class` line or the end of the source -- for asserting
    which children a specific generated class declares (task 1.5)."""
    match = re.search(
        rf'class {re.escape(class_name)}\(AssemblyNode\):\n(.*?)(?=\nclass |\Z)',
        source, re.S)
    assert match, f'{class_name!r} not found in generated source'
    return match.group(1)


def build_simple(path):
    """One part, turned and carried away from the origin, so the
    generated `render()` has something to state."""
    root = cq.Assembly(name='Actuator')
    root.add(cq.Workplane('XY').box(2, 2, 2), name='Fixed_Ring',
            loc=cq.Location(cq.Vector(1.5, -2.5, 3.0), cq.Vector(0, 1, 0),
                            -79.0959))
    root.export(path, exportType='STEP')


def build_nested(path):
    """A sub-assembly placed non-identically in the root, holding one
    part placed non-identically in its own frame."""
    root = cq.Assembly(name='Machine')
    gearbox = cq.Assembly(name='Gearbox')
    gearbox.add(cq.Workplane('XY').box(1, 1, 1), name='Gear',
               loc=cq.Location(cq.Vector(3, 0, 0)))
    root.add(gearbox, name='Gearbox',
             loc=cq.Location(cq.Vector(10, 20, 0), cq.Vector(1, 0, 0), 90))
    root.export(path, exportType='STEP')


def build_repeated(path):
    """One product placed three times at three different stations, for
    the repeated-declaration rule (design D8).

    `cadquery.Assembly` refuses two siblings sharing one `name=`
    (confirmed in `test_step_node.py`'s own fixtures), so each `add()`
    below is given a distinct sibling name -- but it is the same
    underlying shape OBJECT each time, and cadquery/OCCT deduplicate a
    repeated shape reference into one product regardless of the name
    argument on the second and later calls (confirmed empirically
    against `test_step_node.py`'s `build_repeated_product`, whose
    second addition is likewise named differently from its first,
    'Repeated'/'RepeatedFar', and still reads back as one product
    named 'Repeated' with two occurrences)."""
    root = cq.Assembly(name='Bracket')
    bolt = cq.Workplane('XY').box(1, 1, 1)
    for index, x in enumerate((5, 10, 20)):
        root.add(bolt, name=f'Bolt{index}', loc=cq.Location(cq.Vector(x, 0, 0)))
    root.export(path, exportType='STEP')


def build_duplicate_names(path):
    """Two distinct products sharing one name, in two sub-assemblies --
    the same shape `test_step_node.py`'s own `build_duplicate_names`
    builds, authored again here so this module's tests do not depend on
    that module having run first (task 1.6, evidence.md §2)."""
    root = cq.Assembly(name='Root')
    sub1 = cq.Assembly(name='Sub1')
    sub1.add(cq.Workplane('XY').box(1, 1, 1), name='Pin')
    sub2 = cq.Assembly(name='Sub2')
    sub2.add(cq.Workplane('XY').box(2, 2, 2), name='Pin')
    root.add(sub1, name='Sub1')
    root.add(sub2, name='Sub2')
    root.export(path, exportType='STEP')


def build_dup_subassembly(path):
    """Two distinct sub-assemblies sharing one name ('Stage'), each
    holding a different part -- `evidence/probe_dup_subassembly.py`,
    verbatim (task 1.5, evidence.md §3)."""
    root = cq.Assembly(name='Root')
    for side, child_name, size in (('Left', 'Alpha', 1), ('Right', 'Beta', 2)):
        holder = cq.Assembly(name=side)
        stage = cq.Assembly(name='Stage')
        stage.add(cq.Workplane('XY').box(size, size, size), name=child_name,
                 loc=cq.Location(cq.Vector(size, 0, 0)))
        holder.add(stage, name='Stage',
                  loc=cq.Location(cq.Vector(0, size * 10, 0)))
        root.add(holder, name=side)
    root.export(path, exportType='STEP')


def setUpModule():
    build_simple(SIMPLE_STEP)
    build_nested(NESTED_STEP)
    build_repeated(REPEATED_STEP)
    build_duplicate_names(DUPLICATE_NAMES_STEP)
    build_dup_subassembly(DUP_SUBASSEMBLY_STEP)


class ColdCacheTestCase(TestCase):

    def setUp(self):
        step_module._document_cache.clear()
        self.build_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.build_dir.cleanup)
        environment = patch.dict(os.environ, {
            'SOLID_BUILD_DIR': self.build_dir.name})
        environment.start()
        self.addCleanup(environment.stop)


##############################################
# Section 1: the naming rules (task 5.1)


class ClassNameRuleTest(TestCase):

    def test_the_fact_10_names(self):
        cases = {
            '10010 Stator': 'Part10010Stator',
            '40x50x6mm_Bearing': 'Part40x50x6mmBearing',
            'M4_12mm_Screw': 'M4_12mmScrew',
            'ODrive_S1': 'ODriveS1',
        }
        for name, expected in cases.items():
            with self.subTest(name=name):
                self.assertEqual(_class_name_base(name), expected)

    def test_attribute_names_are_lower_snake_case(self):
        self.assertEqual(_attribute_name_base('M4_12mm_Screw'),
                         'm4_12mm_screw')
        self.assertEqual(_attribute_name_base('10010 Stator'),
                         'p_10010_stator')


##############################################
# Section 2: parts.py content (task 5.2)


class GeneratedPartsTest(ColdCacheTestCase):

    def test_a_part_becomes_a_leaf_class(self):
        assembly = StepAssembly(SIMPLE_STEP)

        source, class_names = generate_parts(assembly, SIMPLE_STEP, PROJECT)

        fixed_ring = next(product for product in assembly.products
                          if product.name == 'Fixed_Ring')
        self.assertEqual(class_names[fixed_ring.identity], 'FixedRing')
        self.assertIn('class FixedRing(StepNode):', source)
        self.assertIn("step_source = 'import_simple.step'", source)
        self.assertIn("part = 'Fixed_Ring'", source)
        self.assertIn('angular_deflection = 0.5', source)
        self.assertNotIn('color', source)

    def test_a_root_and_a_sub_assembly_get_no_leaf_class(self):
        assembly = StepAssembly(NESTED_STEP)

        source, class_names = generate_parts(assembly, NESTED_STEP, PROJECT)

        # `generate_parts` returns `{product.identity: class_name}` (design
        # D3), so membership is checked by the product's identity, not by
        # its name.
        by_name = {product.name: product for product in assembly.products}
        self.assertNotIn(by_name['Machine'].identity, class_names)
        self.assertNotIn(by_name['Gearbox'].identity, class_names)
        self.assertIn(by_name['Gear'].identity, class_names)

    def test_two_products_colliding_on_one_class_name_get_a_suffix(self):
        path = os.path.join(PROJECT, 'import_collision.step')
        root = cq.Assembly(name='Root')
        root.add(cq.Workplane('XY').box(1, 1, 1), name='Widget!')
        root.add(cq.Workplane('XY').box(2, 2, 2), name='Widget#')
        root.export(path, exportType='STEP')

        assembly = StepAssembly(path)
        _, class_names = generate_parts(assembly, path, PROJECT)

        by_name = {product.name: product for product in assembly.products}
        self.assertEqual(class_names[by_name['Widget!'].identity], 'Widget')
        self.assertEqual(class_names[by_name['Widget#'].identity], 'Widget_2')

    def test_duplicate_names_get_two_distinct_classes_each_with_its_own_index(self):
        """Task 1.6: `generate_parts` must not let the second `Pin`
        product's class overwrite the first's (evidence.md §2). It fails
        today with both products naming class `Pin_2`."""
        assembly = StepAssembly(DUPLICATE_NAMES_STEP)

        source, class_names = generate_parts(
            assembly, DUPLICATE_NAMES_STEP, PROJECT)

        pins = [product for product in assembly.products
               if product.name == 'Pin']
        self.assertEqual(len(pins), 2)
        pin_classes = {class_names[pin.identity] for pin in pins}
        self.assertEqual(len(pin_classes), 2,
                         'the two Pin products must get two distinct classes')
        self.assertIn('part_index = 1', source)
        self.assertIn('part_index = 2', source)


##############################################
# Section 3: assembly.py content (task 5.3, 5.4)


class GeneratedAssemblyTest(ColdCacheTestCase):

    def test_a_placement_becomes_a_rest_operation(self):
        assembly = StepAssembly(SIMPLE_STEP)
        _, class_names = generate_parts(assembly, SIMPLE_STEP, PROJECT)

        source, root_class = generate_assembly(
            assembly, 'actuator', SIMPLE_STEP, class_names)

        self.assertEqual(root_class, 'Actuator')
        self.assertIn('class Actuator(AssemblyNode):', source)
        self.assertIn('fixed_ring = FixedRing()', source)
        self.assertIn('def render(self):', source)

        rotate_match = re.search(
            r'self\.fixed_ring\.rotate\(([^,]+), \(([^)]+)\)\)', source)
        self.assertIsNotNone(rotate_match, source)
        angle = float(rotate_match.group(1))
        axis = tuple(float(v) for v in rotate_match.group(2).split(', '))
        # Design D2's ratification note: the axis's largest-magnitude
        # component is positive, angle negated to match -- the form
        # the actuator's own record uses.
        self.assertAlmostEqual(angle, -79.0959, places=6)
        self.assertEqual(axis, (0.0, 1.0, 0.0))

        translate_match = re.search(
            r'self\.fixed_ring\.translate\(\(([^)]+)\)\)', source)
        self.assertIsNotNone(translate_match, source)
        translation = tuple(float(v)
                            for v in translate_match.group(1).split(', '))
        self.assertEqual(translation, (1.5, -2.5, 3.0))

        self.assertIn('Fixed_Ring', source)  # occurrence comment
        self.assertIn(os.path.basename(SIMPLE_STEP), source)
        self.assertNotIn('Driver', source)
        self.assertNotIn('def simulate', source)

    def test_a_repeated_part_is_repeated_declarations_never_repeat(self):
        assembly = StepAssembly(REPEATED_STEP)
        _, class_names = generate_parts(assembly, REPEATED_STEP, PROJECT)

        source, root_class = generate_assembly(
            assembly, 'bracket', REPEATED_STEP, class_names)

        self.assertNotIn('.repeat(', source)
        for suffix in ('_1', '_2', '_3'):
            self.assertIn(f'bolt0{suffix} = Bolt0()', source)
        self.assertEqual(source.count('self.bolt0_1.translate'), 1)
        self.assertEqual(source.count('self.bolt0_2.translate'), 1)
        self.assertEqual(source.count('self.bolt0_3.translate'), 1)

    def test_a_sub_assembly_becomes_a_class_placed_as_a_child(self):
        assembly = StepAssembly(NESTED_STEP)
        _, class_names = generate_parts(assembly, NESTED_STEP, PROJECT)

        source, root_class = generate_assembly(
            assembly, 'machine', NESTED_STEP, class_names)

        self.assertEqual(root_class, 'Machine')
        gearbox_at = source.index('class Gearbox(AssemblyNode):')
        machine_at = source.index('class Machine(AssemblyNode):')
        self.assertLess(gearbox_at, machine_at,
                        'the sub-assembly class must be defined first')
        self.assertIn('gear = Gear()', source)
        self.assertIn('gearbox = Gearbox()', source)
        self.assertIn('self.gearbox.rotate(90.0, (1.0, 0.0, 0.0))', source)
        self.assertIn('self.gearbox.translate((10.0, 20.0, 0.0))', source)
        self.assertIn('self.gear.translate((3.0, 0.0, 0.0))', source)
        # Gear's own placement carries no rotation: no rotate() call for it.
        self.assertNotIn('self.gear.rotate', source)

    def test_the_generated_machine_does_not_move(self):
        assembly = StepAssembly(NESTED_STEP)
        _, class_names = generate_parts(assembly, NESTED_STEP, PROJECT)

        source, _ = generate_assembly(
            assembly, 'machine', NESTED_STEP, class_names)

        self.assertNotIn('Driver', source)
        self.assertNotIn('def simulate', source)

    def test_same_named_sub_assemblies_become_distinct_classes(self):
        """Task 1.5: two distinct `Stage` sub-assemblies must not merge
        into one class holding both children (evidence.md §3). It fails
        today with one `Stage` class holding both `Alpha` and `Beta`."""
        assembly = StepAssembly(DUP_SUBASSEMBLY_STEP)
        _, class_names = generate_parts(
            assembly, DUP_SUBASSEMBLY_STEP, PROJECT)

        source, root_class = generate_assembly(
            assembly, 'dup', DUP_SUBASSEMBLY_STEP, class_names)

        self.assertIn('class Stage(AssemblyNode):', source)
        self.assertIn('class Stage_2(AssemblyNode):', source)
        first_body = _class_body(source, 'Stage')
        second_body = _class_body(source, 'Stage_2')
        self.assertIn('alpha = Alpha()', first_body)
        self.assertNotIn('beta', first_body)
        self.assertIn('beta = Beta()', second_body)
        self.assertNotIn('alpha', second_body)


##############################################
# Section 3 (continued): every generated module parses (task 1.7)


class GeneratedSourceCompilesTest(ColdCacheTestCase):
    """A `render()` with no executable placement must still carry `pass`
    (design D4): compiling `assembly.py` and `parts.py` for every fixture
    this module and `test_step_node.py` author. Three of them raise
    `IndentationError` today (evidence.md §4)."""

    def _compile(self, step_path, into_dir=PROJECT):
        assembly = StepAssembly(step_path)
        parts_source, class_names = generate_parts(
            assembly, step_path, into_dir)
        assembly_source, _ = generate_assembly(
            assembly, 'model', step_path, class_names)
        compile(parts_source, 'parts.py', 'exec')
        compile(assembly_source, 'assembly.py', 'exec')

    def test_every_fixture_compiles(self):
        directory = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, directory, ignore_errors=True)

        fixtures = {
            'import_simple': SIMPLE_STEP,
            'import_nested': NESTED_STEP,
            'import_repeated': REPEATED_STEP,
            'duplicate_names': DUPLICATE_NAMES_STEP,
            'dup_subassembly': DUP_SUBASSEMBLY_STEP,
        }

        # `test_step_node.py`'s own fixtures, authored again here so this
        # test does not depend on that module having run first.
        single_product = os.path.join(directory, 'single_product.step')
        cq.exporters.export(cq.Workplane('XY').box(5, 5, 5), single_product)
        fixtures['single_product'] = single_product

        wrapped_single_part = os.path.join(
            directory, 'wrapped_single_part.step')
        wrapper = cq.Assembly(name='Wrapper')
        wrapper.add(cq.Workplane('XY').box(6, 6, 6), name='SoloPart')
        wrapper.export(wrapped_single_part, exportType='STEP')
        fixtures['wrapped_single_part'] = wrapped_single_part

        two_products = os.path.join(directory, 'two_products.step')
        two = cq.Assembly(name='TwoProducts')
        two.add(cq.Workplane('XY').box(4, 4, 4), name='ColouredPart')
        two.add(cq.Workplane('XY').box(2, 2, 2), name='PlainPart')
        two.export(two_products, exportType='STEP')
        fixtures['two_products'] = two_products

        for name, path in fixtures.items():
            with self.subTest(fixture=name):
                self._compile(path, into_dir=directory)


##############################################
# Section 4: faithfulness -- the generated model composes what the
# reader read (task 5.5)


class GeneratedModelFaithfulnessTest(ColdCacheTestCase):

    def _write_and_import(self, step_path, model_name):
        assembly = StepAssembly(step_path)
        parts_source, class_names = generate_parts(
            assembly, step_path, self._package_dir)
        assembly_source, root_class = generate_assembly(
            assembly, model_name, step_path, class_names)

        with open(os.path.join(self._package_dir, 'parts.py'), 'w') as f:
            f.write(parts_source)
        with open(os.path.join(self._package_dir, 'assembly.py'), 'w') as f:
            f.write(assembly_source)

        module = importlib.import_module(f'{self._package_name}.assembly')
        return assembly, getattr(module, root_class)

    def setUp(self):
        super().setUp()
        self._root_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._root_dir.cleanup)
        self._package_name = f'import_step_fixture_{next(PACKAGE_NAMES)}'
        self._package_dir = os.path.join(self._root_dir.name,
                                         self._package_name)
        os.makedirs(self._package_dir)
        open(os.path.join(self._package_dir, '__init__.py'), 'w').close()
        # A node's __init__ resolves its project root by walking up for
        # a pyproject.toml carrying [tool.machinome] -- constructing
        # the generated root class needs one to exist, even though this
        # test never builds or reads a manifest model reference.
        with open(os.path.join(self._root_dir.name, 'pyproject.toml'),
                 'w') as handle:
            handle.write('[tool.machinome]\n'
                        f'model = "{self._package_name}.assembly:X"\n')
        sys.path.insert(0, self._root_dir.name)
        self.addCleanup(sys.path.remove, self._root_dir.name)
        self.addCleanup(self._forget_package)

    def _forget_package(self):
        for name in list(sys.modules):
            if name == self._package_name or \
                    name.startswith(self._package_name + '.'):
                del sys.modules[name]

    def _assert_faithful(self, assembly, root_node, atol=0.01):
        """Every StepNode leaf's composed world matrix agrees with the
        reader's world matrix for its occurrence, at the product's
        origin (a stand-in for its bounding-box centre on these
        centred fixtures) -- design D11.

        `root_node.children` stays empty until `assemble()` links it
        (`internal.py`'s `as_scad`); render() itself does not run on
        bare construction either -- `set_state()` is what forces one
        render/simulate pass through the tree (the same call
        `test_simulate_split.py`'s own render-composition tests use
        before reading a child's operations). Declared children are
        walked directly rather than through `.children`, so this proof
        needs neither a build nor a linked tree.

        A leaf is paired to the occurrence of the product it actually
        selects -- `(leaf.part, leaf.part_index)` resolved through
        `assembly.products` to that product's own identity (task 1.8) --
        never by `leaf.part` alone: on a document with two same-named
        products, matching by name alone would silently pair a leaf with
        WHICHEVER of them the name-only lookup found first, the exact
        defect this change repairs."""
        from machinome.node.adapters.step import StepNode
        from machinome.node.declarative import declared_child_nodes

        root_node.set_state()

        # `ProductInfo.part_index` is always populated -- 1 for a name no
        # other product shares -- so a leaf declaring no `part_index`
        # (the ordinary case) still resolves to the one product its name
        # names.
        product_by_selector = {
            (product.name, product.part_index): product
            for product in assembly.products}

        by_product_identity = {}
        for occurrence in assembly.occurrences:
            by_product_identity.setdefault(
                occurrence.product_identity, []).append(occurrence)

        leaves = []

        def walk(node):
            if isinstance(node, StepNode):
                leaves.append(node)
            for child in declared_child_nodes(node):
                walk(child)

        walk(root_node)

        self.assertGreater(len(leaves), 0)
        matched = set()
        for leaf in leaves:
            # Every generated part class declares `part` (spec
            # "Generated part source"), so this is always the exact
            # product name; `part_index` is declared only where the
            # generator emitted one (design D3).
            selector = (leaf.part, leaf.part_index if leaf.part_index
                       is not None else 1)
            product = product_by_selector.get(selector)
            self.assertIsNotNone(product, f'no product for {selector}')
            candidates = by_product_identity.get(product.identity, [])
            unmatched = [o for o in candidates
                        if id(o) not in matched]
            self.assertTrue(unmatched,
                            f'no free occurrence for {product.identity}')
            occurrence = unmatched[0]
            matched.add(id(occurrence))
            composed = _compose_world_matrix(leaf)
            np.testing.assert_allclose(
                composed, occurrence.world_matrix, atol=atol)

    def test_a_single_part_model_is_faithful(self):
        assembly, root_class = self._write_and_import(SIMPLE_STEP, 'actuator')
        root_node = root_class()

        self._assert_faithful(assembly, root_node)

    def test_a_nested_model_is_faithful(self):
        assembly, root_class = self._write_and_import(NESTED_STEP, 'machine')
        root_node = root_class()

        self._assert_faithful(assembly, root_node)

    def test_a_repeated_model_is_faithful(self):
        assembly, root_class = self._write_and_import(REPEATED_STEP, 'bracket')
        root_node = root_class()

        self._assert_faithful(assembly, root_node)

    def test_a_duplicate_named_model_is_faithful(self):
        """Task 1.8: the scaffold's own generated selector must resolve
        each `Pin` to its OWN occurrence, not to whichever occurrence a
        name-only lookup happens to find first. It fails today because
        both generated classes carry the same unusable `part = 'Pin'`
        selector and the build itself raises the ambiguity error."""
        assembly, root_class = self._write_and_import(
            DUPLICATE_NAMES_STEP, 'dup')
        root_node = root_class()

        self._assert_faithful(assembly, root_node)


##############################################
# Section 5: the command (task 6)


class ImportStepCommandTestCase(ColdCacheTestCase):

    def setUp(self):
        super().setUp()
        self._project_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self._project_dir.cleanup)
        self._previous_cwd = os.getcwd()
        os.chdir(self._project_dir.name)
        self.addCleanup(os.chdir, self._previous_cwd)

    def run_command(self, file, into='.', model=None):
        args = Namespace(file=file, into=into, model=model)
        return ImportStep().handle(args)


class ImportStepScaffoldTest(ImportStepCommandTestCase):

    def test_a_vendor_assembly_is_scaffolded(self):
        """The success path never calls sys.exit(): only a refusal
        does (CLI spec exit-status scenarios)."""
        self.run_command(SIMPLE_STEP, into='actuator', model='actuator')

        self.assertTrue(os.path.exists('actuator/parts.py'))
        self.assertTrue(os.path.exists('actuator/assembly.py'))

    def test_it_writes_both_files_and_an_init(self):
        self.run_command(SIMPLE_STEP, into='actuator', model='actuator')

        self.assertTrue(os.path.exists('actuator/parts.py'))
        self.assertTrue(os.path.exists('actuator/assembly.py'))
        self.assertTrue(os.path.exists('actuator/__init__.py'))

    def test_into_defaults_to_the_current_directory(self):
        try:
            self.run_command(SIMPLE_STEP)
        except SystemExit:
            pass

        self.assertTrue(os.path.exists('parts.py'))
        self.assertTrue(os.path.exists('assembly.py'))

    def test_model_defaults_from_the_root_product_name(self):
        try:
            self.run_command(SIMPLE_STEP, into='actuator')
        except SystemExit:
            pass

        with open('actuator/assembly.py') as handle:
            source = handle.read()
        # SIMPLE_STEP's root product is named 'Actuator'.
        self.assertIn('class Actuator(AssemblyNode):', source)

    def test_never_overwrites_either_file(self):
        try:
            self.run_command(SIMPLE_STEP, into='actuator', model='actuator')
        except SystemExit:
            pass

        with self.assertRaises(SystemExit) as raised:
            self.run_command(SIMPLE_STEP, into='actuator', model='actuator')

        self.assertEqual(raised.exception.code, 1)

    def test_refuses_when_only_one_file_exists(self):
        os.makedirs('actuator')
        open(os.path.join('actuator', 'parts.py'), 'w').close()

        with self.assertRaises(SystemExit) as raised:
            self.run_command(SIMPLE_STEP, into='actuator', model='actuator')

        self.assertEqual(raised.exception.code, 1)
        self.assertFalse(os.path.exists('actuator/assembly.py'))

    def test_prints_manifest_lines_and_never_touches_pyproject(self):
        with open('pyproject.toml', 'w') as handle:
            handle.write('[tool.machinome]\nmodel = "x"\n')
        with open('pyproject.toml') as handle:
            before = handle.read()

        with patch('sys.stdout') as stdout:
            try:
                self.run_command(SIMPLE_STEP, into='actuator',
                                model='actuator')
            except SystemExit:
                pass
        printed = ''.join(call.args[0] for call in stdout.write.call_args_list)

        with open('pyproject.toml') as handle:
            after = handle.read()

        self.assertEqual(before, after)
        self.assertIn('[tool.machinome.models]', printed)
        self.assertIn('actuator', printed)
        self.assertIn('assembly:Actuator', printed)

    def test_an_improper_placement_stops_the_scaffold(self):
        """No mirrored or scaled occurrence is authorable through this
        toolchain's own STEP writer (see
        `test_step_assembly.PropertyGateUnitTest`'s docstring: OCCT's
        `STEPCAFControl_Writer` resets such a location to the identity
        on write, for every route tried in this session). The gate
        itself is forced instead, the same way the reader's own test
        proves the walk is unaffected by an improper occurrence."""
        real_propriety = step_module._propriety

        def fake_propriety(matrix, trsf):
            proper, determinant, scale_factor = real_propriety(matrix, trsf)
            return False, -1.0, 1.0

        with patch.object(step_module, '_propriety', side_effect=fake_propriety):
            with self.assertRaises(SystemExit) as raised:
                self.run_command(SIMPLE_STEP, into='bad')

        self.assertEqual(raised.exception.code, 1)
        self.assertFalse(os.path.exists('bad'))

    def test_a_missing_file_is_reported_and_writes_nothing(self):
        with self.assertRaises(SystemExit) as raised:
            self.run_command('/no/such/file.step', into='nowhere')

        self.assertEqual(raised.exception.code, 1)
        self.assertFalse(os.path.exists('nowhere'))

    def test_the_kernel_missing_is_a_checked_failure(self):
        with patch.object(import_step, '_load_step_assembly',
                          side_effect=ImportError('no module named cadquery')):
            with self.assertRaises(SystemExit) as raised:
                self.run_command(SIMPLE_STEP, into='actuator')

        self.assertEqual(raised.exception.code, 1)
        self.assertFalse(os.path.exists('actuator'))

    def test_it_loads_no_node(self):
        """needs_node is False, and the command never imports project
        source -- there is none to import, but the generated modules
        themselves must not be imported as a side effect of writing
        them (models command precedent)."""
        self.assertFalse(ImportStep.needs_node)

        try:
            self.run_command(SIMPLE_STEP, into='actuator', model='actuator')
        except SystemExit:
            pass

        self.assertNotIn('actuator.assembly', sys.modules)
        self.assertNotIn('actuator.parts', sys.modules)


class ImportStepCliHelpTest(TestCase):

    def test_import_step_appears_in_cli_help(self):
        from machinome.cli import COMMANDS

        self.assertIn('import-step', COMMANDS)
        module, class_name = COMMANDS['import-step']
        self.assertEqual(module, 'machinome.manager.import_step')
        self.assertEqual(class_name, 'ImportStep')
