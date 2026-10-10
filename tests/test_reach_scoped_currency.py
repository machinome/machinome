# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Currency when the digest covers what the node names across its whole
closure, not only its own file (ADR-182, amending ADR-071).

build-pipeline's content-verified fallback used to scope a node's digest to
its own file alone: every OTHER tracked file always contributed its whole
bytes, so an edit to a constant, a helper function or an import nothing the
node reads ever named still re-derived it, as long as the edit lived in a
file the node's import closure reached. The rule here covers every tracked
Python file: a top-level definition is left out of a node's digest only
when nothing the node's retained text ever names it, resolved as Python
resolves a name.

The fixture is a scratch package with `spec.py` (constants `X` and `Y`, a
function, a non-node class, an import nothing uses), `parts.py` with leaves
`A` (reads `spec.X`) and `B` (reads `spec.Y`, the function and the class),
and an assembly; each leaf records its `render()` in the trace log, as
`tests/test_node_scoped_currency.py`'s fixture does.
"""

import ast
import hashlib
import json
import os

from machinome import currency
from machinome.core.loader import load_node

from tests.test_content_verified_currency import TRACE, ScratchProjectTest


SPEC = '''\
X = 1.0

Y = 2.0


def helper():
    return 'ok'


class NotANode:
    pass


import sys
'''

PARTS = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(spec.X, spec.X, spec.X)


class B(CadQueryNode):

    def render(self):
        trace.record('B')
        spec.helper()
        spec.NotANode
        return cq.Workplane('XY').circle(spec.Y).extrude(1.0)
'''

# R1's second form: names imported directly, read bare, rather than
# through the module.
PARTS_BARE = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from .spec import X, Y

from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(X, X, X)


class B(CadQueryNode):

    def render(self):
        trace.record('B')
        return cq.Workplane('XY').circle(Y).extrude(1.0)
'''

MACHINE = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A, B


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        self.b = B()
        super().__init__()

    def render(self):
        self.b.translate([10, 0, 0])
        return [self.a, self.b]
'''

# R3 and R5's fixture: A reaches a sibling's class attribute through a
# helper function in another tracked file, by a function-level import.
HELPER = '''\
def read_hint():
    from . import parts
    return parts.B.HINT
'''

PARTS_SIBLING = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import helper
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        hint = helper.read_hint()
        return cq.Workplane('XY').box(1.0 + hint, 1.0, 1.0)


class B(CadQueryNode):

    HINT = 0.0

    def render(self):
        trace.record('B')
        return cq.Workplane('XY').circle(1.0).extrude(1.0)
'''

MACHINE_SIBLING = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A, B


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        self.b = B()
        super().__init__()

    def render(self):
        self.b.translate([10, 0, 0])
        return [self.a, self.b]
'''


class ReachScopedProjectTest(ScratchProjectTest):
    """The base fixture: `spec.py`, `parts.py` (`A`, `B`), `machine.py`."""

    def project_files(self):
        return (('__init__.py', ''), ('trace.py', TRACE),
                ('spec.py', SPEC), ('parts.py', PARTS),
                ('machine.py', MACHINE))

    def mkdir(self, name):
        os.makedirs(os.path.join(self.root, self.package, name),
                    exist_ok=True)

    def previous_digest_without_b(self):
        """ADR-071's digest of the current `node.a`'s tracked files: every
        file by its bytes except `parts.py`, whose entry is the sha256 of
        its lines without `B`'s class statement -- R4 and R5's shared
        helper, in `whole_file_digest`'s encoding
        (`tests/test_node_scoped_currency.py`)."""
        self.forget_project()
        node = load_node(self.reference)
        entries = {}
        for path in node.a.files:
            real = os.path.realpath(path)
            relative = os.path.relpath(real, self.root)
            with open(real, 'rb') as source:
                data = source.read()
            if os.path.basename(real) == 'parts.py':
                tree = ast.parse(data, filename=real)
                span = next(
                    (statement.lineno, statement.end_lineno)
                    for statement in tree.body
                    if isinstance(statement, ast.ClassDef)
                    and statement.name == 'B')
                lines = data.splitlines(keepends=True)
                skipped = set(range(span[0] - 1, span[1]))
                digest = hashlib.sha256()
                for number, line in enumerate(lines):
                    if number not in skipped:
                        digest.update(line)
                content = digest.hexdigest()
            else:
                content = hashlib.sha256(data).hexdigest()
            entries[relative] = content
        digest = hashlib.sha256()
        for relative, content in sorted(entries.items()):
            digest.update(os.fsencode(relative))
            digest.update(b'\0')
            digest.update(content.encode('ascii'))
            digest.update(b'\n')
        return digest.hexdigest(), node

    def plant_previous_record(self, node):
        """Replace `node.a`'s STL and BREP records with version 2 records
        holding ADR-071's digest and the node's current fingerprint."""
        digest, fresh = self.previous_digest_without_b()
        fingerprint = fresh.a.source_fingerprint
        for artifact in (node.a.stl_file, node.a.brep_file):
            with open(currency.sidecar(artifact), 'w') as sidecar:
                json.dump({'version': 2, 'digest': digest,
                          'fingerprint': fingerprint}, sidecar)

    def read_record(self, artifact):
        with open(currency.sidecar(artifact)) as sidecar:
            return json.load(sidecar)


class ReachScopedCurrencyTest(ReachScopedProjectTest):
    """Task 2.1: R1, by module attribute."""

    def test_an_edit_to_a_definition_one_node_never_names_spares_it(self):
        with self.subTest('Y, read by B alone'):
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace('Y = 2.0', 'Y = 2.5'))
            self.build()
            self.assertEqual(self.renders(), ['B'])

        with self.subTest('X, read by A alone'):
            self.write('spec.py', SPEC)
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace('X = 1.0', 'X = 1.5'))
            self.build()
            self.assertEqual(self.renders(), ['A'])

        with self.subTest('the function, read by B alone'):
            self.write('spec.py', SPEC)
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace("return 'ok'", "return 'ko'"))
            self.build()
            self.assertEqual(self.renders(), ['B'])

        with self.subTest('the non-node class, read by B alone'):
            self.write('spec.py', SPEC)
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace(
                'class NotANode:\n    pass',
                'class NotANode:\n    tag = 1'))
            self.build()
            self.assertEqual(self.renders(), ['B'])

        with self.subTest('the import nothing names'):
            self.write('spec.py', SPEC)
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace('import sys', 'import json'))
            self.build()
            self.assertEqual(self.renders(), [])

    def test_an_edit_to_a_name_imported_directly_spares_the_other_leaf(self):
        """R1's second form: `from .spec import X, Y` read as bare `X` by
        `A` and bare `Y` by `B`."""
        self.write('parts.py', PARTS_BARE)

        with self.subTest('Y, read bare by B alone'):
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace('Y = 2.0', 'Y = 2.5'))
            self.build()
            self.assertEqual(self.renders(), ['B'])

        with self.subTest('X, read bare by A alone'):
            self.write('spec.py', SPEC)
            self.build()
            self.renders()
            self.write('spec.py', SPEC.replace('X = 1.0', 'X = 1.5'))
            self.build()
            self.assertEqual(self.renders(), ['A'])


class SiblingNamedFromAnotherFileTest(ReachScopedProjectTest):
    """Task 2.1: R3 and R5, sharing one fixture."""

    def project_files(self):
        return (('__init__.py', ''), ('trace.py', TRACE),
                ('helper.py', HELPER), ('parts.py', PARTS_SIBLING),
                ('machine.py', MACHINE_SIBLING))

    def test_a_sibling_named_from_another_file_is_followed(self):
        self.build()
        self.renders()
        self.write('parts.py', PARTS_SIBLING.replace(
            'HINT = 0.0', 'HINT = 0.5'))
        self.build()
        # B re-derives because its own body changed; A re-derives too,
        # which ADR-071 would not have done, because the sibling it
        # reaches through helper.py's function is now part of its closure.
        self.assertEqual(sorted(self.renders()), ['A', 'B'],
                         "a sibling reached through another tracked file's "
                         'helper was not followed')

    def test_a_previous_rule_record_is_not_carried_past_a_sibling_it_left_out(
            self):
        node = self.build()
        self.renders()
        self.plant_previous_record(node)

        self.rewrite_timestamps()
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         "a previous-rule record that left out a sibling "
                         'the current rule retains was carried forward')


class PreviousRuleMigrationTest(ReachScopedProjectTest):
    """Task 2.1: R4, on the base fixture."""

    def test_a_previous_rule_record_is_verified_once_and_re_recorded(self):
        node = self.build()
        self.renders()
        self.plant_previous_record(node)

        self.rewrite_timestamps()
        rebuilt = self.build()
        self.assertEqual(self.renders(), [],
                         'a previous-rule record whose digest still '
                         'matches was re-derived rather than re-recorded')

        for artifact in (rebuilt.a.stl_file, rebuilt.a.brep_file):
            record = self.read_record(artifact)
            self.assertEqual(record['version'], 4)
            self.assertEqual(record['digest'], rebuilt.a.source_digest)

        self.write('spec.py', SPEC.replace('Y = 2.0', 'Y = 2.5'))
        self.build()
        self.assertEqual(self.renders(), ['B'])


##############################################
# Guards (task 2.3): green on the unchanged tree and green after, except
# the companion half of G15, which is red for R1's reason.

GETATTR_SPEC = '''\
Y = 2.0

NAMES = ('Y',)
'''


class GuardsTest(ReachScopedProjectTest):

    def test_g1_a_definition_reached_through_import_re_export_and_star(self):
        self.mkdir('lib')
        self.write('lib/__init__.py', "from .inner import W\n")
        self.write('lib/inner.py', 'W = 1.0\n')
        self.write('stars.py', "V = 1.0\n")
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from .spec import Z
from .lib import W
from .stars import *

from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(Z, W, V)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('spec.py', SPEC + '\nZ = 1.0\n')
        self.write('parts.py', parts)
        self.write('machine.py', machine)

        with self.subTest('direct import, Z'):
            self.build()
            self.renders()
            self.write('spec.py', SPEC + '\nZ = 1.5\n')
            self.build()
            self.assertEqual(self.renders(), ['A'])

        with self.subTest('package re-export, W'):
            self.write('spec.py', SPEC + '\nZ = 1.0\n')
            self.build()
            self.renders()
            self.write('lib/inner.py', 'W = 1.5\n')
            self.build()
            self.assertEqual(self.renders(), ['A'])

        with self.subTest('star import, V'):
            self.write('lib/inner.py', 'W = 1.0\n')
            self.build()
            self.renders()
            self.write('stars.py', 'V = 1.5\n')
            self.build()
            self.assertEqual(self.renders(), ['A'])

    def test_g2_a_definition_named_only_by_a_string_is_kept(self):
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        value = getattr(spec, 'S')
        return cq.Workplane('XY').box(value, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('spec.py', SPEC + '\nS = 1.0\n')
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('spec.py', SPEC + '\nS = 1.5\n')
        self.build()
        self.assertEqual(self.renders(), ['A'])

    def test_g3_a_non_definition_statement_keeps_what_it_names(self):
        spec = SPEC + '''
K = 1.0

ALL = []
ALL.append(K)
'''
        self.write('spec.py', spec)
        self.build()
        self.renders()

        self.write('spec.py', spec.replace('K = 1.0', 'K = 1.5'))
        self.build()
        self.assertEqual(sorted(self.renders()), ['A', 'B'],
                         'a non-definition statement did not keep what it '
                         'names for every node of the file')

    def test_g4_a_decorated_non_node_definition_is_never_left_out(self):
        spec = SPEC + '''
import functools

H = 1.0


@functools.lru_cache
def helper2():
    return H
'''
        self.write('spec.py', spec)
        self.build()
        self.renders()

        self.write('spec.py', spec.replace('H = 1.0', 'H = 1.5'))
        self.build()
        self.assertEqual(sorted(self.renders()), ['A', 'B'],
                         'a decorated non-node definition was left out, '
                         'hiding an edit to what it names')

    def test_g5_vars_on_a_module_keeps_it_whole(self):
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        vars(spec)
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('spec.py', SPEC.replace('Y = 2.0', 'Y = 2.5'))
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         "a dynamic vars(module) call did not keep the "
                         'module whole')

    def test_g6_a_factory_made_node_class_keeps_its_file_whole(self):
        # The factory lives in parts.py, one level below its own node
        # class, and is not itself a top-level class.
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode


def make_gear(teeth):
    class Gear(CadQueryNode):

        TEETH = teeth

        def render(self):
            from . import trace
            trace.record('Gear')
            return cq.Workplane('XY').box(self.TEETH, 1.0, 1.0)
    return Gear


Gear = make_gear(20)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import Gear


class Machine(AssemblyNode):

    def __init__(self):
        self.gear = Gear()
        super().__init__()

    def render(self):
        return [self.gear]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('parts.py', parts.replace(
            'Gear = make_gear(20)', 'Gear = make_gear(24)'))
        self.build()
        self.assertEqual(self.renders(), ['Gear'],
                         "a node class made by a factory was not kept "
                         'whole in its own file')

    def test_g7___all___in_a_star_imported_module_is_never_left_out(self):
        self.write('stars.py', "V = 1.0\n\n\n__all__ = ['V']\n")
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from .stars import *

from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('stars.py', "V = 1.0\n\n\n__all__ = []\n")
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         '__all__ of a star-imported module was left out')

    def test_g8_a_definition_sharing_a_line_with_a_retained_one_is_kept(self):
        spec = SPEC + '\nimport os; Y2 = 2.0\n'
        parts = PARTS.replace('spec.Y', 'spec.Y2')
        self.write('spec.py', spec)
        self.write('parts.py', parts)
        self.build()
        self.renders()

        self.write('spec.py', spec.replace('Y2 = 2.0', 'Y2 = 2.5'))
        self.build()
        # Never left out for ANY node tracking spec.py, not only one that
        # names it: a shared line cannot be removed for one node and kept
        # for another, so both A and B see the edit.
        self.assertEqual(sorted(self.renders()), ['A', 'B'])

    def test_g9_a_file_a_leaf_adds_after_construction_digests_whole(self):
        extra = 'EXTRA = 1.0\n'
        self.write('extra.py', extra)
        parts = PARTS + '''

class Extra(CadQueryNode):

    def __init__(self):
        super().__init__()
        import os
        self.files.add(os.path.join(os.path.dirname(self.src), 'extra.py'))

    def render(self):
        trace.record('Extra')
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = MACHINE.replace(
            'from .parts import A, B', 'from .parts import A, B, Extra'
        ).replace(
            'self.b = B()', 'self.b = B()\n        self.extra = Extra()'
        ).replace(
            'return [self.a, self.b]', 'return [self.a, self.b, self.extra]')
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('extra.py', 'EXTRA = 1.5\n')
        self.build()
        self.assertEqual(self.renders(), ['Extra'],
                         "a file a leaf tracks beyond its own closure was "
                         'not digested whole')

    def test_g10_a_closure_that_leaves_nothing_out_equals_the_whole_digest(
            self):
        """Guard 1.5 (`SingleClassFileTest`) covers the conventional
        layout; this adds one node of the new fixture that names
        everything its one tracked file holds, so nothing is left out."""
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class Full(CadQueryNode):

    def render(self):
        trace.record('Full')
        spec.helper()
        spec.NotANode
        spec.sys
        return cq.Workplane('XY').box(spec.X, spec.X, spec.Y)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import Full


class Machine(AssemblyNode):

    def __init__(self):
        self.full = Full()
        super().__init__()

    def render(self):
        return [self.full]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        node = self.build()
        from tests.test_node_scoped_currency import SharedFileTest
        self.assertEqual(
            node.full.source_digest,
            SharedFileTest.whole_file_digest(self, node.full))

    def test_g11_each_tracked_file_is_analysed_at_most_once_per_process(self):
        node = self.build()
        from unittest.mock import patch
        calls = []
        original = currency._reach_analyse

        def counting(path, data):
            calls.append(path)
            return original(path, data)

        with patch('machinome.currency._reach_analyse', counting):
            node.assemble()
            node.a.source_digest
            node.b.source_digest
        self.assertEqual(len(calls), len(set(calls)),
                         'a tracked file was analysed more than once')

    def test_g13_imports_nested_in_a_retained_statement_bind(self):
        spec = SPEC + '''
X2 = 1.0


def make_default():
    K = 1
    return K
'''
        self.write('spec.py', spec)
        defs = 'K = 1.0\n'
        self.write('defs.py', defs)
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import trace
# Loaded unconditionally so sys.modules carries them before any node in
# this file is constructed -- source_closure resolves a nested import's
# target through the loaded-module index, which needs the module loaded
# first, exactly as a project's own eager top-level imports do.
from . import spec as _spec_loaded
from . import defs as _defs_loaded


class A(CadQueryNode):

    def render(self):
        from .spec import X2
        trace.record('A')
        return cq.Workplane('XY').box(X2, 1.0, 1.0)


class B(CadQueryNode):

    def render(self):
        from . import spec
        trace.record('B')
        return cq.Workplane('XY').box(spec.X2, 1.0, 1.0)


class C(CadQueryNode):

    def render(self):
        try:
            from .defs import K
        except ImportError:
            K = 0.0
        trace.record('C')
        return cq.Workplane('XY').box(K, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A, B, C


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        self.b = B()
        self.c = C()
        super().__init__()

    def render(self):
        self.b.translate([5, 0, 0])
        self.c.translate([10, 0, 0])
        return [self.a, self.b, self.c]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        with self.subTest('X2, read bare inside a function'):
            self.write('spec.py', spec.replace('X2 = 1.0', 'X2 = 1.5'))
            self.build()
            self.assertEqual(sorted(self.renders()), ['A', 'B'],
                             'a nested import inside a retained statement '
                             'did not bind for resolution')

        with self.subTest('K, read through a try/except ImportError'):
            self.write('defs.py', 'K = 1.5\n')
            self.build()
            self.assertEqual(self.renders(), ['C'])

    def test_g13_a_top_level_if_type_checking_import_binds_by_bare_name(
            self):
        """The `if TYPE_CHECKING:` form of G13. The `if` itself is a
        top-level non-definition statement, always retained for every
        node of the file (D2); with I1's fix its own nested import's
        bound name is therefore a mention for every one of them, not
        only the node that also happens to spell it bare -- so both `A`
        (which does) and `B` (which never mentions `_K` at all) are
        re-derived when `K` changes."""
        self.write('defs.py', 'K = 1.0\n')
        parts = '''\
import typing

import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import trace
from . import defs as _defs_loaded

if typing.TYPE_CHECKING:
    from .defs import K as _K


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        if typing.TYPE_CHECKING:
            size = _K
        else:
            size = 1.0
        return cq.Workplane('XY').box(size, 1.0, 1.0)


class B(CadQueryNode):

    def render(self):
        trace.record('B')
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A, B


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        self.b = B()
        super().__init__()

    def render(self):
        self.b.translate([5, 0, 0])
        return [self.a, self.b]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('defs.py', 'K = 1.5\n')
        self.build()
        self.assertEqual(sorted(self.renders()), ['A', 'B'],
                         'an if TYPE_CHECKING import did not bind for every '
                         'node of the file it is always retained in')

    def test_i1_a_top_level_try_binds_even_when_nothing_else_spells_the_name(
            self):
        """design.md's revision after apply evidence, I1: a top-level
        `try: from .defs import K / except ImportError: pass` binds `K`
        into the module whether or not the `except` arm also spells it,
        so a node sharing the file still retains `defs.py`'s `K` even
        though nothing in the whole file ever writes the bare name `K`."""
        self.write('defs.py', 'K = 1.0\n')
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import trace

try:
    from .defs import K
except ImportError:
    pass


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        node = self.build()
        self.renders()

        left_out = currency._retained(
            node.a.files, node.a._project_root, node.a.scope,
            node.a._effective_whole_files(), None)
        defs_path = os.path.realpath(
            os.path.join(self.root, self.package, 'defs.py'))
        self.assertNotIn(defs_path, left_out,
                         'defs.py was left out even though the module '
                         'binds K unconditionally at the top level')

        self.write('defs.py', 'K = 1.5\n')
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         'a top-level try/except import that nothing '
                         'spells again did not retain the name it binds')

    def test_g14_a_non_python_leaf_digests_as_today(self):
        import tests.test_stl_node as stl_test
        import tests.test_step_node as step_test
        from tests.stl_project.parts import Bracket as StlPart
        from tests.step_project.parts import WrappedSinglePart as StepPart

        stl_test.setUpModule()
        step_test.setUpModule()

        def whole_file_digest(node):
            entries = {}
            for path in node.files:
                real = os.path.realpath(path)
                relative = os.path.relpath(real, node._project_root)
                with open(real, 'rb') as source:
                    entries[relative] = hashlib.sha256(
                        source.read()).hexdigest()
            digest = hashlib.sha256()
            for relative, content in sorted(entries.items()):
                digest.update(os.fsencode(relative))
                digest.update(b'\0')
                digest.update(content.encode('ascii'))
                digest.update(b'\n')
            return digest.hexdigest()

        for part in (StlPart(), StepPart()):
            part.assemble()
            self.assertEqual(part.scope, {})
            self.assertEqual(part.source_digest, whole_file_digest(part))

    def test_g15_a_computed_module_getattr_keeps_the_module_whole(self):
        self.write('spec.py', GETATTR_SPEC)
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        total = 0.0
        for name in spec.NAMES:
            total += getattr(spec, name)
        return cq.Workplane('XY').box(1.0 + total, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('spec.py', GETATTR_SPEC.replace('Y = 2.0', 'Y = 2.5'))
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         'a computed getattr on a module-bound name did '
                         'not keep the module whole')

    def test_g15_companion_getattr_on_self_does_not_retain_spec_whole(self):
        """Red on the unchanged tree for R1's reason (`spec.py` digested
        whole)."""
        spec = SPEC + '\nZ = 3.0\n'
        parts = PARTS.replace(
            'class B(CadQueryNode):\n',
            "class B(CadQueryNode):\n\n"
            "    def computed(self, name):\n"
            "        return getattr(self, name)\n"
        )
        self.write('spec.py', spec)
        self.write('parts.py', parts)
        self.build()
        self.renders()

        spec = spec.replace('Y = 2.0', 'Y = 2.5')
        self.write('spec.py', spec)
        self.build()
        self.assertEqual(self.renders(), ['B'])

        # Z is named by neither A nor B: if getattr(self, name) wrongly
        # retained spec.py whole, this edit would re-derive both.
        self.write('spec.py', spec.replace('Z = 3.0', 'Z = 3.5'))
        self.build()
        self.assertEqual(self.renders(), [],
                         'getattr(self, name) retained spec.py whole')

    def test_g16_a_whole_file_follows_the_names_its_imports_bind(self):
        self.write('defs.py', 'K = 1.0\n')
        spec = GETATTR_SPEC + "\nfrom .defs import K\n"
        self.write('spec.py', spec)
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import spec
from . import trace


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        total = 0.0
        for name in spec.NAMES:
            total += getattr(spec, name)
        return cq.Workplane('XY').box(1.0 + total, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('defs.py', 'K = 1.5\n')
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         'a module kept whole by a computed getattr did '
                         "not follow the names its own imports bind")

    def test_i2_a_root_bound_to_two_tracked_modules_resolves_into_both(self):
        """design.md's revision after apply evidence, I2: `_resolve_chain`
        used to stop at the first module binding of a name; a name bound
        conditionally to two tracked modules (`if X: from . import a as
        m` / `else: from . import b as m`) must resolve into both,
        since which one wins depends on runtime state the static walk
        does not evaluate."""
        self.write('a_module.py', 'W = 1.0\n')
        self.write('b_module.py', 'W = 2.0\n')
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import trace
# Loaded unconditionally so both are tracked, even though only one
# branch below ever actually runs.
from . import a_module as _a_loaded
from . import b_module as _b_loaded

FLAG = True
if FLAG:
    from . import a_module as m
else:
    from . import b_module as m


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        return cq.Workplane('XY').box(m.W, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        with self.subTest('the branch taken at runtime'):
            self.write('a_module.py', 'W = 1.5\n')
            self.build()
            self.assertEqual(self.renders(), ['A'])

        with self.subTest('the branch never taken at runtime'):
            self.write('b_module.py', 'W = 2.5\n')
            self.build()
            self.assertEqual(self.renders(), ['A'],
                             'a name bound to two tracked modules was not '
                             'resolved into the one the static walk never '
                             'sees taken')

    def test_i2_an_unresolvable_relative_import_falls_to_the_catch_all(self):
        """design.md's revision after apply evidence, I2: an `ImportFrom`
        whose relative import cannot be resolved used to register no
        binding at all, so `_resolve_bare` never reached the catch-all
        for the name it tried and failed to bind. `from .. import
        SOMETHING` inside `if False:` goes one level above this
        single-component top-level package, so `resolve_name` raises --
        exactly the branch the fix covers -- without the statement ever
        actually running (real Python would refuse the import itself at
        that point). `A` mentions the failed import's own local alias,
        bare, inside a dead branch (so it never raises `NameError`),
        which is what the catch-all needs something to ask for; the
        name it finds is a plain module-level constant of the same
        spelling in another tracked file, `other.py`."""
        self.write('other.py', '_unreachable = 1.0\n')
        parts = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import trace
from . import other as _other_loaded

if False:
    from .. import SOMETHING as _unreachable


class A(CadQueryNode):

    def render(self):
        trace.record('A')
        if False:
            _ = _unreachable
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''
        machine = '''\
from machinome.node.assembly import AssemblyNode

from .parts import A


class Machine(AssemblyNode):

    def __init__(self):
        self.a = A()
        super().__init__()

    def render(self):
        return [self.a]
'''
        self.write('parts.py', parts)
        self.write('machine.py', machine)
        self.build()
        self.renders()

        self.write('other.py', '_unreachable = 1.5\n')
        self.build()
        self.assertEqual(self.renders(), ['A'],
                         'an unresolvable relative import did not fall to '
                         'the catch-all for the name it tried to bind')


FRAME_HELPER = '''\
from machinome.node.frames import Frame


def make_frame():
    return Frame()
'''

FRAME_PARTS = '''\
import cadquery as cq

from machinome.node.cadquery import CadQueryNode

from . import helper
from . import trace


class Frame(CadQueryNode):
    """The project's own node class, deliberately shadowing the
    framework's machinome.node.frames.Frame by name."""

    SIZE = 1.0

    def render(self):
        trace.record('Frame')
        return cq.Workplane('XY').box(self.SIZE, 1.0, 1.0)


class Arbor(CadQueryNode):
    """Never names the project's own Frame class; only reaches the
    FRAMEWORK's Frame, transitively, through helper.py."""

    def render(self):
        trace.record('Arbor')
        helper.make_frame()
        return cq.Workplane('XY').box(1.0, 1.0, 1.0)
'''

FRAME_MACHINE = '''\
from machinome.node.assembly import AssemblyNode

from .parts import Arbor, Frame


class Machine(AssemblyNode):

    def __init__(self):
        self.frame = Frame()
        self.arbor = Arbor()
        super().__init__()

    def render(self):
        self.arbor.translate([10, 0, 0])
        return [self.frame, self.arbor]
'''


class FrameworkImportGuardTest(ReachScopedProjectTest):
    """design.md's revision after apply evidence, I3: an import of a
    module the interpreter has loaded whose file lies outside the
    project (here, the framework's own `machinome.node.frames`) binds a
    name no tracked definition can be, and must not fall to the
    catch-all merely because it cannot be tracked."""

    def project_files(self):
        return (('__init__.py', ''), ('trace.py', TRACE),
                ('helper.py', FRAME_HELPER), ('parts.py', FRAME_PARTS),
                ('machine.py', FRAME_MACHINE))

    def test_i3_a_framework_import_in_a_sibling_file_does_not_retain_a_same_named_project_class(  # noqa: E501
            self):
        self.build()
        self.renders()

        self.write('parts.py', FRAME_PARTS.replace('SIZE = 1.0', 'SIZE = 1.5'))
        self.build()
        self.assertEqual(self.renders(), ['Frame'],
                         "a sibling file's import of the framework's "
                         'same-named class wrongly retained the project '
                         "class through the catch-all")

    def test_i3_the_previous_rule_still_carries_with_a_framework_import_in_the_closure(  # noqa: E501
            self):
        node = self.build()
        self.renders()

        self.forget_project()
        fresh = load_node(self.reference)
        entries = {}
        for path in fresh.arbor.files:
            real = os.path.realpath(path)
            relative = os.path.relpath(real, self.root)
            with open(real, 'rb') as source:
                data = source.read()
            if os.path.basename(real) == 'parts.py':
                tree = ast.parse(data, filename=real)
                span = next(
                    (statement.lineno, statement.end_lineno)
                    for statement in tree.body
                    if isinstance(statement, ast.ClassDef)
                    and statement.name == 'Frame')
                lines = data.splitlines(keepends=True)
                skipped = set(range(span[0] - 1, span[1]))
                digest = hashlib.sha256()
                for number, line in enumerate(lines):
                    if number not in skipped:
                        digest.update(line)
                content = digest.hexdigest()
            else:
                content = hashlib.sha256(data).hexdigest()
            entries[relative] = content
        digest = hashlib.sha256()
        for relative, content in sorted(entries.items()):
            digest.update(os.fsencode(relative))
            digest.update(b'\0')
            digest.update(content.encode('ascii'))
            digest.update(b'\n')
        previous_digest = digest.hexdigest()
        fingerprint = fresh.arbor.source_fingerprint

        for artifact in (node.arbor.stl_file, node.arbor.brep_file):
            with open(currency.sidecar(artifact), 'w') as sidecar:
                json.dump({'version': 2, 'digest': previous_digest,
                          'fingerprint': fingerprint}, sidecar)

        self.rewrite_timestamps()
        self.build()
        self.assertEqual(self.renders(), [],
                         'a previous-rule record whose digest still '
                         'matches, with a framework import in the '
                         'closure, was re-derived rather than carried')
