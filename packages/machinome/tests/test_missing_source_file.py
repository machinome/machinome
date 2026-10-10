# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""A source-bound leaf whose declared file is not there.

`StlNode`, `StepNode`, `JScadNode` and `OpenScadNode` each bind a node to
a file outside Python. Before this change, a missing one was not caught
until `mtime_ns` (or, for `OpenScadNode`, `coherent_read`) stat'ed it and
raised a bare `FileNotFoundError` naming only the path -- not the node,
not the class, not the attribute that declared it -- and a declared
source that existed but was a directory was not caught at all: it was
handed to trimesh or the STEP reader, which failed on it deep inside a
foreign library. `Internal-Cycloidal-Actuator` paid for the first gap
and grew its own `source.require()` preamble to work around it
(`workflow/warts.md`); see `openspec/changes/name-the-missing-file/`.

`AbsentBracket`/`DirectoryBracket` (`tests/stl_project/parts.py`) and
`AbsentPart`/`DirectoryPart` (`tests/step_project/parts.py`) are
constructed nowhere but here, and the directory their `Directory*`
sibling names is this module's own fixture -- created and removed by
`setUpModule`/`tearDownModule` below, never by `test_stl_node.py` or
`test_step_node.py` -- so this file passes alone, on a clean checkout
(reviewer's note 3 of `design.md`).

There is no fixture project for `JScadNode` or `OpenScadNode`; each test
that needs one writes its own scratch project, the same way
`tests/test_meta.py`'s `FailedOpenScadRenderMetaTest` and
`tests/test_builder_reload_resilience.py`'s `VANISHING_JSCAD_PIPE` do.
"""

import errno
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
from unittest import TestCase

from unittest.mock import patch

from machinome.node.assembly import AssemblyNode
from machinome.node.solid2 import Solid2Node
from machinome.node.step import StepNode
from machinome.node.stl import StlNode
from machinome.node.declarative import ChildDeclaration
from machinome.node.markings import Marking, Svg, Wrapped

from .stl_project import parts as stl_parts
from .step_project import parts as step_parts

#: This test module's own directory: the wrapper directory every source
#: attribute declared inline (in `test_a_source_removed_after_...`
#: below) resolves against, matching how the node itself resolves it.
TEST_DIR = os.path.dirname(os.path.realpath(__file__))

STL_PROJECT = os.path.dirname(os.path.realpath(stl_parts.__file__))
STEP_PROJECT = os.path.dirname(os.path.realpath(step_parts.__file__))

#: `DirectoryBracket`/`DirectoryPart` declare `stl_source`/`step_source
#: = 'a_directory'`; this module creates and removes the directory that
#: value resolves to, in each fixture project, so it never depends on
#: another test module's `setUpModule` having authored anything there.
STL_DIRECTORY_SOURCE = os.path.join(STL_PROJECT, 'a_directory')
STEP_DIRECTORY_SOURCE = os.path.join(STEP_PROJECT, 'a_directory')


#: The fixtures' project root: `tests/`, by `tests/pyproject.toml`.
TESTS_ROOT = TEST_DIR
#: The repository's own manifest, a regular file above that root, which
#: `EscapingBracket`/`EscapingPart` declare through `../../`.
ABOVE_ROOT = os.path.join(os.path.dirname(TEST_DIR), 'pyproject.toml')

#: `LinkedBracket`/`LinkedPart` declare a source through these symbolic
#: links, which point into a temporary directory outside the project and
#: exist only while this module runs.
STL_LINK = os.path.join(STL_PROJECT, 'linked_outside.stl')
#: A source beside `stl_parts`, this module's own: `bracket.stl` there is
#: written by `test_stl_node.py`, which a clean checkout runs later.
STL_BESIDE = os.path.join(STL_PROJECT, 'declared_alone.stl')
STEP_LINK = os.path.join(STEP_PROJECT, 'linked_outside.step')
OUTSIDE = None


def setUpModule():
    global OUTSIDE
    os.makedirs(STL_DIRECTORY_SOURCE, exist_ok=True)
    os.makedirs(STEP_DIRECTORY_SOURCE, exist_ok=True)
    open(STL_BESIDE, 'w').close()
    OUTSIDE = os.path.realpath(tempfile.mkdtemp(prefix='machinome_outside_'))
    for link, name in ((STL_LINK, 'part.stl'), (STEP_LINK, 'part.step')):
        target = os.path.join(OUTSIDE, name)
        open(target, 'w').close()
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(target, link)


def tearDownModule():
    shutil.rmtree(STL_DIRECTORY_SOURCE, ignore_errors=True)
    shutil.rmtree(STEP_DIRECTORY_SOURCE, ignore_errors=True)
    if os.path.lexists(STL_BESIDE):
        os.remove(STL_BESIDE)
    for link in (STL_LINK, STEP_LINK):
        if os.path.lexists(link):
            os.remove(link)
    if OUTSIDE:
        shutil.rmtree(OUTSIDE, ignore_errors=True)


class MissingChildRig(AssemblyNode):
    """A class body may declare an absent leaf as a child -- the
    declarative API defers construction to the parent, so this must
    import cleanly whatever `part`'s file does. Only instantiating the
    assembly realizes `part` and may fail."""

    part = stl_parts.AbsentBracket()


class MissingSourceFileTest(TestCase):
    """`StlNode`/`StepNode` share a fixture project with every other STL
    and STEP test (`tests/stl_project`, `tests/step_project`), already a
    real Solid project by way of `tests/pyproject.toml`; this file adds
    no project of its own for these two adapters."""

    def test_an_absent_stl_source_fails_at_construction(self):
        path = os.path.join(STL_PROJECT, 'no-such-bracket.stl')

        with self.assertRaises(FileNotFoundError) as raised:
            stl_parts.AbsentBracket()

        message = str(raised.exception)
        self.assertIn('AbsentBracket', message)
        self.assertIn('stl_source', message)
        self.assertIn("'no-such-bracket.stl'", message)
        self.assertIn(path, message)
        self.assertNotIn('committed', message)

    def test_an_absent_step_source_fails_at_construction(self):
        path = os.path.join(STEP_PROJECT, 'no-such-part.step')

        with self.assertRaises(FileNotFoundError) as raised:
            step_parts.AbsentPart()

        message = str(raised.exception)
        self.assertIn('AbsentPart', message)
        self.assertIn('step_source', message)
        self.assertIn("'no-such-part.step'", message)
        self.assertIn(path, message)
        self.assertNotIn('committed', message)

    def test_a_directory_stl_source_fails_as_not_a_file(self):
        with self.assertRaises(ValueError) as raised:
            stl_parts.DirectoryBracket()

        message = str(raised.exception)
        self.assertIn('DirectoryBracket', message)
        self.assertIn('stl_source', message)
        self.assertIn(STL_DIRECTORY_SOURCE, message)

    def test_a_directory_step_source_fails_as_not_a_file(self):
        with self.assertRaises(ValueError) as raised:
            step_parts.DirectoryPart()

        message = str(raised.exception)
        self.assertIn('DirectoryPart', message)
        self.assertIn('step_source', message)
        self.assertIn(STEP_DIRECTORY_SOURCE, message)

    def test_the_declared_childs_class_body_constructs_nothing(self):
        # Green today and after: the deferral this change must not move.
        self.assertIsInstance(MissingChildRig.__dict__['part'],
                              ChildDeclaration)

    def test_the_failure_arrives_when_the_parent_realizes_the_child(self):
        with self.assertRaises(FileNotFoundError) as raised:
            MissingChildRig()

        message = str(raised.exception)
        self.assertIn('AbsentBracket', message)
        self.assertIn('stl_source', message)

    def test_the_exception_carries_the_resolved_path_as_filename(self):
        """`Builder._on_reload_exception`'s reload-repair fix (design.md,
        "Amendment at implementation") reads `exc.filename` to watch the
        exact foreign path a construction-time refusal names, so both
        exceptions this function raises must carry it -- and `str(error)`
        must stay the plain one-sentence message, not `FileNotFoundError`'s
        own "[Errno N] message: path" rendering, which constructing with
        `(errno, msg, path)` would add."""
        absent_path = os.path.join(STL_PROJECT, 'no-such-bracket.stl')
        with self.assertRaises(FileNotFoundError) as raised:
            stl_parts.AbsentBracket()
        self.assertEqual(raised.exception.filename, absent_path)
        self.assertFalse(str(raised.exception).startswith('[Errno'))
        self.assertIsInstance(raised.exception, FileNotFoundError)
        self.assertEqual(raised.exception.errno, errno.ENOENT)

        with self.assertRaises(ValueError) as raised:
            stl_parts.DirectoryBracket()
        self.assertEqual(raised.exception.filename, STL_DIRECTORY_SOURCE)
        self.assertFalse(str(raised.exception).startswith('[Errno'))

    def test_a_source_removed_after_construction_still_raises_from_mtime_ns(self):
        """The guard (design.md, "What deliberately does not change"):
        a source present at construction and removed afterwards is a
        currency question, not a declaration question, and keeps
        `mtime_ns`'s own bare `FileNotFoundError` -- this change does
        not touch that path at all."""
        fd, path = tempfile.mkstemp(suffix='.stl', dir=TEST_DIR)
        os.close(fd)
        self.addCleanup(lambda: os.path.exists(path) and os.remove(path))

        class VanishingBracket(StlNode):
            stl_source = os.path.basename(path)

        node = VanishingBracket()
        os.remove(path)

        with self.assertRaises(FileNotFoundError) as raised:
            node.mtime_ns

        # Still the bare path-only message mtime_ns has always raised --
        # naming the node is exactly what construction-time refusal adds,
        # and this failure does not come from construction-time refusal.
        self.assertNotIn('VanishingBracket', str(raised.exception))


class ForeignScratchSourceTest(TestCase):
    """No fixture project exists for `JScadNode`/`OpenScadNode`, so each
    test here writes its own scratch project and imports it directly --
    the same shape `tests/test_meta.py`'s `FailedOpenScadRenderMetaTest`
    and `tests/test_joints.py`'s
    `CapturePosesSeesSiteJointTest` use for a module outside any
    package."""

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix='machinome_missing_source_')
        self.addCleanup(shutil.rmtree, self.project, ignore_errors=True)
        with open(os.path.join(self.project, 'pyproject.toml'), 'w') as manifest:
            manifest.write('[tool.machinome]\n')

    def _load_leaf(self, source):
        path = os.path.join(self.project, 'leaf.py')
        with open(path, 'w') as module_file:
            module_file.write(source)

        name = f'_missing_source_scratch_{uuid.uuid4().hex}'
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(module)
        return module

    def test_an_absent_jscad_source_fails_at_construction(self):
        module = self._load_leaf(
            'from machinome.node.jscad import JScadNode\n\n\n'
            'class AbsentJscad(JScadNode):\n'
            '    jscad_source = "no-such-shape.js"\n')
        path = os.path.join(self.project, 'no-such-shape.js')

        with self.assertRaises(FileNotFoundError) as raised:
            module.AbsentJscad()

        message = str(raised.exception)
        self.assertIn('AbsentJscad', message)
        self.assertIn('jscad_source', message)
        self.assertIn('no-such-shape.js', message)
        self.assertIn(path, message)
        self.assertNotIn('committed', message)

    def test_an_absent_openscad_source_names_the_class(self):
        module = self._load_leaf(
            'from machinome.node.openscad import OpenScadNode\n\n\n'
            'class AbsentScad(OpenScadNode):\n'
            '    scad_source = "no-such-shape.scad"\n')
        path = os.path.join(self.project, 'no-such-shape.scad')

        with self.assertRaises(FileNotFoundError) as raised:
            module.AbsentScad()

        message = str(raised.exception)
        self.assertIn('AbsentScad', message)
        self.assertIn('scad_source', message)
        self.assertIn('no-such-shape.scad', message)
        self.assertIn(path, message)
        self.assertNotIn('committed', message)


class ContainmentTest(TestCase):
    """A declared source outside the declaring module's project is refused
    at construction (OpenSpec change ``vet-the-project``, design D10),
    whatever expression computed it and whether or not it exists."""

    def assertOutside(self, construct, klass, attribute, declared, resolved,
                      root=TESTS_ROOT):
        with self.assertRaises(ValueError) as raised:
            construct()

        error = raised.exception
        self.assertNotIsInstance(error, FileNotFoundError)
        message = str(error)
        self.assertIn(klass, message)
        self.assertIn(attribute, message)
        self.assertIn(repr(declared), message)
        self.assertIn(resolved, message)
        self.assertIn(root, message)
        self.assertIn('outside the project', message)

    def test_an_stl_source_above_the_root(self):
        self.assertOutside(stl_parts.EscapingBracket, 'EscapingBracket',
                           'stl_source', '../../pyproject.toml', ABOVE_ROOT)

    def test_an_absent_stl_source_above_the_root(self):
        self.assertOutside(
            stl_parts.EscapingAbsentBracket, 'EscapingAbsentBracket',
            'stl_source', '../../no-such-outside-bracket.stl',
            os.path.join(os.path.dirname(TEST_DIR),
                         'no-such-outside-bracket.stl'))

    def test_an_stl_source_through_a_symbolic_link(self):
        self.assertOutside(stl_parts.LinkedBracket, 'LinkedBracket',
                           'stl_source', 'linked_outside.stl',
                           os.path.join(OUTSIDE, 'part.stl'))

    def test_a_step_source_above_the_root(self):
        self.assertOutside(step_parts.EscapingPart, 'EscapingPart',
                           'step_source', '../../pyproject.toml', ABOVE_ROOT)

    def test_an_absent_step_source_above_the_root(self):
        self.assertOutside(
            step_parts.EscapingAbsentPart, 'EscapingAbsentPart',
            'step_source', '../../no-such-outside-part.step',
            os.path.join(os.path.dirname(TEST_DIR),
                         'no-such-outside-part.step'))

    def test_a_step_source_through_a_symbolic_link(self):
        self.assertOutside(step_parts.LinkedPart, 'LinkedPart',
                           'step_source', 'linked_outside.step',
                           os.path.join(OUTSIDE, 'part.step'))

    def test_an_artwork_above_the_root(self):
        def declare():
            class EscapingArtwork(Solid2Node):
                digits = Marking(Svg('../pyproject.toml'),
                                 Wrapped(axis=(0, 0, 1), radius=9.45,
                                         at=(0, 0, 0)),
                                 color='#FFFFFF')

        self.assertOutside(declare, 'EscapingArtwork', 'digits',
                           '../pyproject.toml', ABOVE_ROOT)

    def test_a_computed_source_under_the_root_constructs(self):
        fd, path = tempfile.mkstemp(suffix='.stl', dir=STL_PROJECT)
        os.close(fd)
        self.addCleanup(os.remove, path)

        class ComputedBracket(StlNode):
            stl_source = os.path.join(STL_PROJECT, os.path.basename(path))

        self.assertEqual(ComputedBracket().stl_source, os.path.realpath(path))

    def test_an_absolute_step_source_under_the_root_is_admitted(self):
        fd, path = tempfile.mkstemp(suffix='.step', dir=STEP_PROJECT)
        os.close(fd)
        self.addCleanup(os.remove, path)

        class AbsolutePart(StepNode):
            step_source = path

        self.assertEqual(AbsolutePart().step_source, os.path.realpath(path))


class ScratchContainmentTest(TestCase):
    """The OpenSCAD and JSCAD adapters, in scratch projects laid out as
    `<base>/project/` beside `<base>/outside.*`."""

    def setUp(self):
        self.base = os.path.realpath(
            tempfile.mkdtemp(prefix='machinome_containment_'))
        self.addCleanup(shutil.rmtree, self.base, ignore_errors=True)
        self.project = os.path.join(self.base, 'project')
        os.makedirs(self.project)
        for name in ('outside.scad', 'outside.js'):
            with open(os.path.join(self.base, name), 'w') as source:
                source.write('cube(1);\n')

    def manifest(self):
        with open(os.path.join(self.project, 'pyproject.toml'), 'w') as stream:
            stream.write('[tool.machinome]\n')

    def load(self, source):
        path = os.path.join(self.project, 'leaf.py')
        with open(path, 'w') as module_file:
            module_file.write(source)
        name = f'_containment_scratch_{uuid.uuid4().hex}'
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(module)
        return module

    def assertOutside(self, construct, klass, attribute, declared, resolved):
        with self.assertRaises(ValueError) as raised:
            construct()
        message = str(raised.exception)
        for part in (klass, attribute, repr(declared), resolved,
                     self.project, 'outside the project'):
            self.assertIn(part, message)

    def test_an_openscad_source_above_the_root_runs_nothing(self):
        self.manifest()
        module = self.load(
            'from machinome.node.openscad import OpenScadNode\n\n\n'
            'class Outside(OpenScadNode):\n'
            '    scad_source = "../outside.scad"\n')

        with patch('machinome.node.openscad.coherent_read') as read:
            self.assertOutside(module.Outside, 'Outside', 'scad_source',
                               '../outside.scad',
                               os.path.join(self.base, 'outside.scad'))
        read.assert_not_called()

    def test_an_openscad_source_through_a_symbolic_link(self):
        self.manifest()
        os.symlink(os.path.join(self.base, 'outside.scad'),
                   os.path.join(self.project, 'link.scad'))
        module = self.load(
            'from machinome.node.openscad import OpenScadNode\n\n\n'
            'class Linked(OpenScadNode):\n'
            '    scad_source = "link.scad"\n')

        self.assertOutside(module.Linked, 'Linked', 'scad_source',
                           'link.scad', os.path.join(self.base, 'outside.scad'))

    def test_a_jscad_source_above_the_root(self):
        self.manifest()
        module = self.load(
            'from machinome.node.jscad import JScadNode\n\n\n'
            'class Outside(JScadNode):\n'
            '    jscad_source = "../outside.js"\n')

        self.assertOutside(module.Outside, 'Outside', 'jscad_source',
                           '../outside.js',
                           os.path.join(self.base, 'outside.js'))

    def test_a_jscad_source_through_a_symbolic_link(self):
        self.manifest()
        os.symlink(os.path.join(self.base, 'outside.js'),
                   os.path.join(self.project, 'link.js'))
        module = self.load(
            'from machinome.node.jscad import JScadNode\n\n\n'
            'class Linked(JScadNode):\n'
            '    jscad_source = "link.js"\n')

        self.assertOutside(module.Linked, 'Linked', 'jscad_source',
                           'link.js', os.path.join(self.base, 'outside.js'))

    def test_a_class_outside_any_project_is_not_judged(self):
        # (6.4) No manifest above the declaring module, so there is no
        # project to contain its source in. The source itself lies in a
        # project, because a node's build directory mirrors its source's
        # place in one (`AbstractBaseNode.__init__`), as it always has.
        elsewhere = os.path.join(self.base, 'elsewhere')
        os.makedirs(elsewhere)
        with open(os.path.join(elsewhere, 'pyproject.toml'), 'w') as stream:
            stream.write('[tool.machinome]\n')
        with open(os.path.join(elsewhere, 'shape.scad'), 'w') as source:
            source.write('cube(1);\n')
        module = self.load(
            'from machinome.node.openscad import OpenScadNode\n\n\n'
            'class Loose(OpenScadNode):\n'
            '    scad_source = "../elsewhere/shape.scad"\n')

        node = module.Loose()

        self.assertEqual(node.openscad_source,
                         os.path.join(elsewhere, 'shape.scad'))


#: The four core adapters, by the name of the attribute each one reads.
ADAPTERS = (
    ('Stl', 'machinome.node.stl', 'StlNode', 'stl_source'),
    ('Step', 'machinome.node.step', 'StepNode', 'step_source'),
    ('Jscad', 'machinome.node.jscad', 'JScadNode', 'jscad_source'),
    ('Scad', 'machinome.node.openscad', 'OpenScadNode', 'scad_source'),
)


class UndeclaredSourceTest(TestCase):
    """A source-bound leaf that declares no source file, or declares it
    empty, is refused in one shape whatever its adapter (OpenSpec change
    `refuse-the-undeclared-file-by-name`): `ValueError` naming the class,
    the attribute and the module the declaration belongs in, before
    anything is resolved, read or run. Each test writes its own scratch
    project, as `ForeignScratchSourceTest` does."""

    def setUp(self):
        self.project = tempfile.mkdtemp(prefix='machinome_undeclared_source_')
        self.addCleanup(shutil.rmtree, self.project, ignore_errors=True)
        with open(os.path.join(self.project, 'pyproject.toml'), 'w') as manifest:
            manifest.write('[tool.machinome]\n')
        self.leaf = os.path.realpath(os.path.join(self.project, 'leaf.py'))

    def _load_leaf(self, source):
        with open(self.leaf, 'w') as module_file:
            module_file.write(source)

        name = f'_undeclared_source_scratch_{uuid.uuid4().hex}'
        spec = importlib.util.spec_from_file_location(name, self.leaf)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        self.addCleanup(sys.modules.pop, name, None)
        spec.loader.exec_module(module)
        return module

    def _adapters(self, prefix, body):
        """A scratch module declaring `<prefix><kind>` for every adapter,
        with `body` (formatted with the attribute) as its class body."""
        source = ''.join(
            f'from {module} import {base}\n' for _, module, base, _ in ADAPTERS)
        for kind, _, base, attribute in ADAPTERS:
            source += (f'\n\nclass {prefix}{kind}({base}):\n'
                       f'    {body.format(attribute=attribute)}\n')
        return self._load_leaf(source)

    def _refusal(self, construct):
        with patch('machinome.node.openscad.coherent_read') as read:
            with self.assertRaises(Exception) as raised:
                construct()
        read.assert_not_called()
        return raised.exception

    def test_an_undeclared_source_is_refused_naming_class_attribute_and_module(self):
        module = self._adapters('Bare', 'pass')

        for kind, _, _, attribute in ADAPTERS:
            with self.subTest(attribute=attribute):
                error = self._refusal(getattr(module, f'Bare{kind}'))

                self.assertIs(type(error), ValueError, repr(error))
                message = str(error)
                for part in (f'Bare{kind}', attribute, self.leaf,
                             'does not declare'):
                    self.assertIn(part, message)
                for stale in ('join()', 'OpenJScadNode', 'must declare'):
                    self.assertNotIn(stale, message)

    def test_an_empty_declaration_names_no_file(self):
        module = self._adapters('Empty', "{attribute} = ''")

        for kind, _, _, attribute in ADAPTERS:
            with self.subTest(attribute=attribute):
                error = self._refusal(getattr(module, f'Empty{kind}'))

                self.assertIs(type(error), ValueError, repr(error))
                message = str(error)
                for part in (f'Empty{kind}', attribute, "= ''",
                             'names no file', self.leaf):
                    self.assertIn(part, message)
                self.assertNotIn('is not a file', message)

    def test_a_leaf_written_outside_the_core_refuses_it_the_same_way(self):
        module = self._load_leaf(
            'from tests.contract_package.faceted_stand_in import MeshPart\n\n\n'
            'class BareMesh(MeshPart):\n'
            '    pass\n')

        with self.assertRaises(Exception) as raised:
            module.BareMesh()

        error = raised.exception
        self.assertIs(type(error), ValueError, repr(error))
        for part in ('BareMesh', 'mesh_source', self.leaf, 'does not declare'):
            self.assertIn(part, str(error))

    def test_a_declaration_given_alone_is_resolved_beside_its_module(self):
        from machinome.node.sources import require_source_file

        path = os.path.realpath(STL_BESIDE)

        self.assertEqual(
            require_source_file(stl_parts.Bracket, 'stl_source',
                                'declared_alone.stl'),
            path)
        self.assertEqual(
            require_source_file(stl_parts.Bracket, 'stl_source',
                                'declared_alone.stl', path),
            path)


#: The repository root, which a CLI subprocess needs on its `PYTHONPATH`.
REPOSITORY = os.path.dirname(TEST_DIR)


class UndeclaredNestedBuildTest(TestCase):
    """`machinome build` on a model whose leaf, two levels below the root,
    declares no source: one line naming the model and what was being done
    with it, then the refusal naming the leaf's class."""

    def test_a_failure_at_launch_names_the_model_and_the_step(self):
        project = tempfile.mkdtemp(prefix='machinome_undeclared_build_')
        self.addCleanup(shutil.rmtree, project, ignore_errors=True)
        files = {
            'pyproject.toml': '[tool.machinome]\n',
            'parts.py': ('from machinome.node.stl import StlNode\n\n\n'
                         'class BareStl(StlNode):\n'
                         '    pass\n'),
            'assembly.py': ('from machinome.node.assembly import AssemblyNode\n'
                            '\n'
                            'from parts import BareStl\n\n\n'
                            'class Arm(AssemblyNode):\n'
                            '    bracket = BareStl()\n\n\n'
                            'class Rig(AssemblyNode):\n'
                            '    arm = Arm()\n'),
        }
        for name, text in files.items():
            with open(os.path.join(project, name), 'w') as stream:
                stream.write(text)

        environment = dict(os.environ, PYTHONPATH=REPOSITORY,
                           PYTHONDONTWRITEBYTECODE='1')
        environment.pop('SOLID_BUILD_DIR', None)
        environment.pop('SOLID_TEST_ENGINE', None)
        result = subprocess.run(
            [sys.executable, '-c', 'from machinome.cli import manage; manage()',
             'build', 'assembly:Rig'],
            cwd=project, env=environment, capture_output=True, text=True)

        self.assertEqual(result.returncode, 1, result.stderr)
        with open(os.path.join(project, '_build', 'errors.json')) as stream:
            self.assertIn('Traceback', json.load(stream)['error'])
        self.assertIn('The model assembly:Rig could not be loaded: BareStl '
                      'does not declare stl_source', result.stderr)
        self.assertNotIn('failed to load project', result.stderr)
