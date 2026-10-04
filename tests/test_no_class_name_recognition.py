# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The core recognises no node type by the spelling of its class name.

The `node-model` requirement "No node type is recognised by its class
name" (the `backend-switch` change, ADR-166): whatever a core path needs
to know about a node it learns from members the node declares or
inherits, so a node type written outside the core is treated exactly as a
core type declaring the same members. Three things hold it here:

- an AST scan of every module under `machinome/`, with no allowed
  exception;
- the missing-OpenSCAD refusal for a node's STL, which names the node and
  its own class, for a core `Solid2Node` subclass and for a SCAD-presented
  leaf written outside the core alike;
- the behaviour the retired class-name lookup stood for: an exact adapter,
  whatever bases it shares, never reaches the OpenSCAD path.

Displaying a class name -- in an f-string, a `repr`, a file name or a
refusal -- is not a comparison, and the scan does not look at it.
"""

import ast
import os
import pathlib
import tempfile
from unittest import TestCase
from unittest.mock import patch

from solid2 import cube

from machinome.node import Solid2Node
from machinome.node.openscad.binary import OpenScadUnavailable, openscad_binary

from .contract_package.scad_stand_in import MeshScad
from .test_openscad_dependency import Build123dBox, ExactBox
from .test_sheet_leaf import Plate


PACKAGE = pathlib.Path(__file__).resolve().parent.parent / 'machinome'

REQUIREMENT = ('node-model, "No node type is recognised by its class '
               'name" (ADR-166)')

NAME_ATTRIBUTES = ('__name__', '__qualname__')

#: Words no refusal for a node's STL may carry: the core's adapter names
#: the retired lookup knew, and the word for what it named.
CORE_LABELS = ('Solid2Node', 'OpenScadNode', 'FusionNode', 'backend')


class ScadPart(Solid2Node):
    """A project's own SCAD part, as splitflap's is."""

    def render(self):
        return cube(2)


def _is_name_attribute(node):
    return isinstance(node, ast.Attribute) and node.attr in NAME_ATTRIBUTES


def _string_constants(node):
    """The string constants of a literal or of a tuple, list or set of
    them."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.value
    elif isinstance(node, (ast.Tuple, ast.List, ast.Set)):
        for element in node.elts:
            yield from _string_constants(element)


def class_name_recognitions(sources):
    """Every site in `sources` ({label: source text}) that recognises a
    class by its name, as (label, line, source, why) tuples.

    A site is a comparison with a `__name__`/`__qualname__` attribute on
    one side and a string constant, or a collection holding one, on
    another; a comparison holding a string constant that spells a class
    defined in `sources`; or `.startswith`/`.endswith` called on a
    `__name__`/`__qualname__` attribute.
    """
    trees = {label: ast.parse(text, label) for label, text in sources.items()}
    classes = {node.name for tree in trees.values()
               for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}
    found = []
    for label, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.Compare):
                sides = [node.left, *node.comparators]
                strings = {value for side in sides
                           for value in _string_constants(side)}
                if strings and any(_is_name_attribute(side)
                                   for side in sides):
                    found.append((label, node.lineno, ast.unparse(node),
                                  'compares a class name with a string'))
                elif strings & classes:
                    found.append((label, node.lineno, ast.unparse(node),
                                  'compares a string spelling the class '
                                  f'{sorted(strings & classes)[0]}'))
            elif (isinstance(node, ast.Call)
                  and isinstance(node.func, ast.Attribute)
                  and node.func.attr in ('startswith', 'endswith')
                  and _is_name_attribute(node.func.value)):
                found.append((label, node.lineno, ast.unparse(node),
                              f'matches a class name with {node.func.attr}'))
    return found


class NoClassNameComparisonTest(TestCase):
    """No module under `machinome/` compares a class name to a string."""

    def test_no_core_module_compares_a_class_name_to_a_string(self):
        sources = {str(path.relative_to(PACKAGE.parent)): path.read_text()
                   for path in sorted(PACKAGE.rglob('*.py'))}
        self.assertGreater(len(sources), 50)

        found = class_name_recognitions(sources)

        self.assertEqual(found, [], '\n'.join(
            [f'the core recognises a node type by its class name, which '
             f'{REQUIREMENT} forbids:'] +
            [f'  {label}:{line}: {source}  ({why})'
             for label, line, source, why in found]))

    def test_the_scan_finds_each_form_it_forbids(self):
        """A scan that finds nothing must be a scan that can find
        something: each forbidden form, planted, is reported."""
        planted = (
            'class Widget:\n'
            '    pass\n'
            'a = cls.__name__ in ("Widget", "Gadget")\n'
            'b = type(x).__qualname__ == "Anything"\n'
            'c = kind == "Widget"\n'
            'd = cls.__name__.startswith("Wid")\n'
            'e = type(x).__qualname__.endswith("get")\n'
            'f = f"{cls.__name__} is shown, not compared"\n'
            'g = a.__name__ == b.__name__\n')

        found = class_name_recognitions({'planted.py': planted})

        self.assertEqual([line for _, line, _, _ in found], [3, 4, 5, 6, 7])


class OpenScadRefusalNamesTheNodeTest(TestCase):
    """The missing-OpenSCAD refusal for a node's STL names the node and its
    own class, whoever wrote the class."""

    def setUp(self):
        openscad_binary.cache_clear()
        self.addCleanup(openscad_binary.cache_clear)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        old_build_dir = os.environ.get('SOLID_BUILD_DIR')
        os.environ['SOLID_BUILD_DIR'] = directory.name
        self.addCleanup(self._restore_build_dir, old_build_dir)

    @staticmethod
    def _restore_build_dir(old_build_dir):
        if old_build_dir is None:
            os.environ.pop('SOLID_BUILD_DIR', None)
        else:
            os.environ['SOLID_BUILD_DIR'] = old_build_dir

    def _refusal(self, node):
        node.assemble()
        with patch('machinome.node.openscad.binary.shutil.which', return_value=None), \
             patch('machinome.node.openscad.leaf.Popen', side_effect=AssertionError(
                 'the subprocess must not be attempted')):
            with self.assertRaises(OpenScadUnavailable) as raised:
                node.generate_stl()
        return str(raised.exception)

    def test_a_scad_presented_leaf_outside_the_core_is_reported_the_same_way(self):
        self.assertEqual(
            self._refusal(MeshScad()),
            "node MeshScad (MeshScad) requires the OpenSCAD binary because "
            "its STL is rendered from SCAD by OpenSCAD; install OpenSCAD and "
            "ensure 'openscad' is on PATH")

    def test_a_refusal_describes_a_node_by_its_own_class_only(self):
        refusals = {
            'ScadPart': self._refusal(ScadPart(name='sensor')),
            'MeshScad': self._refusal(MeshScad(name='panel')),
        }

        for kind, text in refusals.items():
            for label in CORE_LABELS:
                with self.subTest(node=kind, label=label):
                    self.assertNotIn(label, text)
        prefix = ' requires the OpenSCAD binary because'
        self.assertEqual(refusals['ScadPart'].split(prefix)[0],
                         'node sensor (ScadPart)')
        self.assertEqual(refusals['MeshScad'].split(prefix)[0],
                         'node panel (MeshScad)')


class SharedBaseRoutingTest(TestCase):
    """A shared base does not route an exact adapter through OpenSCAD.

    The behaviour the retired class-name lookup's scenario stood for, pinned
    without the lookup: an exact leaf publishes its STL in `materialize`,
    so STL generation never checks for OpenSCAD or launches it. A
    characterization, green before and after the change.
    """

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        old_build_dir = os.environ.get('SOLID_BUILD_DIR')
        os.environ['SOLID_BUILD_DIR'] = directory.name
        self.addCleanup(OpenScadRefusalNamesTheNodeTest._restore_build_dir,
                        old_build_dir)

    def test_no_exact_adapter_reaches_the_openscad_path(self):
        for leaf in (ExactBox, Build123dBox, Plate):
            with self.subTest(adapter=leaf.__mro__[1].__name__):
                node = leaf()
                node.assemble()

                with patch('machinome.node.openscad.binary.require_openscad',
                           side_effect=AssertionError(
                               'an exact adapter must not check OpenSCAD')), \
                     patch('machinome.node.openscad.leaf.Popen',
                           side_effect=AssertionError(
                               'an exact adapter must not launch OpenSCAD')):
                    node.generate_stl()

                self.assertTrue(os.path.exists(node.stl_file))
