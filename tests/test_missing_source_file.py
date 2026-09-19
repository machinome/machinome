# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

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
import os
import shutil
import sys
import tempfile
import uuid
from unittest import TestCase

from machinome.node import AssemblyNode, StepNode, StlNode
from machinome.node.declarative import ChildDeclaration

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


def setUpModule():
    os.makedirs(STL_DIRECTORY_SOURCE, exist_ok=True)
    os.makedirs(STEP_DIRECTORY_SOURCE, exist_ok=True)


def tearDownModule():
    shutil.rmtree(STL_DIRECTORY_SOURCE, ignore_errors=True)
    shutil.rmtree(STEP_DIRECTORY_SOURCE, ignore_errors=True)


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
            'from machinome.node import JScadNode\n\n\n'
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
            'from machinome.node import OpenScadNode\n\n\n'
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
