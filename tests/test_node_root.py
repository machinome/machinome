# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""`machinome.node` is a package path, a refusal and submodule access, and
exports nothing (OpenSpec change `root-cleanup`; before it, this module
pinned the root's lazy exports).

The root used to resolve twenty-one names a second time, lazily, from the
modules that define them. One address per name is the split's readiness
condition: a name a project imports has exactly one import path, the module
that defines it, so that cutting a node package moves a module and never a
second spelling. So the root now resolves none of them, and refuses each
with `ImportError` naming its module; the acceptance gate,
`tests/test_node_root_exports_nothing.py`, pins every refusal's text.

What stays pinned here is what the root still is. Importing it imports no
backend and no node type's module: a node type is reached by importing the
module that defines it, which imports what that module needs and nothing
else. A submodule is reachable through the package (`machinome.node.step`,
`from machinome.node import step`), and a submodule that cannot be imported
reports why: an absent extra by the module's own refusal, unmodified, a
broken install by its own error with the requested name spliced in. The
moved port names and the parameter kinds stay out.

What a fresh process imports is only observable in a process that has not
already imported the framework, so those assertions run through
`tests/import_probe.py` in a fresh interpreter. The rest run in-process.
"""

import importlib
from unittest import TestCase

from .import_probe import probe

import machinome.node


# The names `machinome/node/__init__.py` resolved until `root-cleanup`,
# each with the module that defines it. Written out here rather than read
# from the package under test.
FORMER_EXPORTS = {
    'StlRenderStart': 'machinome.node.base',
    'AssemblyNode': 'machinome.node.assembly',
    'FusionNode': 'machinome.node.fusion',
    'CadQueryNode': 'machinome.node.cadquery',
    'Build123dNode': 'machinome.node.build123d',
    'SheetLeafNode': 'machinome.node.sheet_leaf',
    'Build123dSheetNode': 'machinome.node.build123d',
    'FlexibleNode': 'machinome.node.flexible',
    'MolejoNode': 'machinome.node.molejo',
    'Solid2Node': 'machinome.node.solid2',
    'OpenScadNode': 'machinome.node.openscad',
    'JScadNode': 'machinome.node.jscad',
    'StlNode': 'machinome.node.stl',
    'StepNode': 'machinome.node.step',
    'property_as_number': 'machinome.node.decorators',
    'declared_children': 'machinome.node.declarative',
    'Marking': 'machinome.node.markings',
    'Wrapped': 'machinome.node.markings',
    'Flat': 'machinome.node.markings',
    'Svg': 'machinome.node.markings',
    'Frame': 'machinome.node.frames',
}

# What the node package must NOT answer for. A build parameter is imported
# from `machinome.parameters`, and one import line saying which of its
# names is a node kind and which is a knob is the whole point of the split;
# a re-export here would quietly restore the ambiguity.
PARAMETER_NAMES = ('Quantity', 'Length', 'Angle', 'Count', 'Ratio', 'Scalar',
                   'Flag', 'declared_parameters')

# The names and the two submodules `motion-package` moved out of the node
# package entirely, each now answering for `machinome.motion.ports`
# instead. No re-export, no alias, no shim: reading any of these off
# `machinome.node` must fail naming the new home.
MOVED_NAMES = ('Port', 'RotationalPort', 'TranslationalPort', 'SignalPort',
              'declared_ports', 'Time', 'ports', 'timebase')

# The B-rep node classes. Since the exact engine change (OpenSpec
# `exact-engine`) B-rep geometry is the B-rep engine's and the core imports
# no CAD front end for it, so only `StepNode`, whose reader and `adjust`
# still use CadQuery, reaches `cadquery` when its module is imported; the
# others reach it only when a project's own module imports it to render.
BREP_CLASSES = ('FusionNode', 'CadQueryNode', 'Build123dNode',
                'Build123dSheetNode', 'StepNode')
CADQUERY_CLASSES = ('StepNode',)

# The modules of the node types (the table of supported node types' keys),
# none of which importing the package may import.
NODE_TYPE_MODULES = ('machinome.node.cadquery', 'machinome.node.build123d',
                     'machinome.node.step', 'machinome.node.molejo',
                     'machinome.node.solid2', 'machinome.node.openscad',
                     'machinome.node.jscad', 'machinome.node.stl')

# Refuse `cadquery` the way an interpreter without the wheel does, in the
# shape of the finders of tests/brep_engine_absent.py and
# tests/mesh_engine_absent.py: a `sys.meta_path` finder that raises, rather
# than a stub, so the deferred import fails for the real reason an install
# without the `step` extra fails.
CADQUERY_ABSENT = '''
import sys


class _CadQueryAbsent:

    def find_spec(self, name, target=None, path=None):
        if name == 'cadquery' or name.startswith('cadquery.'):
            raise ModuleNotFoundError(
                "No module named 'cadquery'", name='cadquery')
        return None


sys.meta_path.insert(0, _CadQueryAbsent())
sys.modules.pop('cadquery', None)
'''

# Find `cadquery`, then fail to import it from inside, as an installed
# kernel that cannot load does: a broken install, not an absent extra.
CADQUERY_BROKEN = '''
import importlib.machinery
import sys


class _CadQueryBroken:

    def find_spec(self, name, target=None, path=None):
        if name == 'cadquery' or name.startswith('cadquery.'):
            return importlib.machinery.ModuleSpec(name, self)
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        raise ImportError('broken cadquery')


sys.meta_path.insert(0, _CadQueryBroken())
sys.modules.pop('cadquery', None)
'''

#: The `step` module's refusal where CadQuery is absent.
STEP_REFUSAL = ('machinome.node.step (StepNode, StepAssembly) needs '
                'cadquery, which is not installed; install it with '
                '\'pip install "machinome[step]"\'')


def root_import(name):
    """`from machinome.node import <name>`, composed at run time: this
    file spells no former root name as a literal import line."""
    return f'from machinome.node import {name}\n'


class NodePackageImportCost(TestCase):
    """What importing the package, and only the package, costs."""

    def _ran(self, snippet):
        """Probe `snippet`, insisting it reached the end.

        The probe reports whichever modules were loaded before the child
        died, so a snippet that raised would satisfy "cadquery is
        absent" for entirely the wrong reason. The marker makes the run
        prove it completed.
        """
        result = probe(snippet + "print('DONE')\n")
        self.assertEqual(result.stdout.strip(), 'DONE', result.stderr)
        return result

    def test_importing_the_node_package_does_not_import_cadquery(self):
        result = self._ran('import machinome.node\n')
        self.assertFalse(result.imported('cadquery'),
                         'importing machinome.node imported cadquery')
        self.assertFalse(result.imported('machinome.engine.brep'),
                         'importing machinome.node imported the B-rep engine')

    def test_importing_the_node_package_imports_no_node_type(self):
        result = self._ran('import machinome.node\n')
        for module in NODE_TYPE_MODULES:
            with self.subTest(module=module):
                self.assertFalse(result.imported(module),
                                 f'importing machinome.node imported {module}')

    def test_importing_the_node_base_does_not_import_cadquery(self):
        # The path that actually hurts: every core consumer imports
        # `machinome.node.base`, which runs the package __init__ first.
        result = self._ran(
            'from machinome.node.base import AbstractBaseNode\n')
        self.assertFalse(result.imported('cadquery'),
                         'importing machinome.node.base imported cadquery')

    def test_importing_an_openscad_node_type_does_not_import_cadquery(self):
        # An OpenSCAD/solid2-only project imports Solid2Node from its
        # module and nothing else; it must not pay for the B-rep stack.
        result = self._ran('from machinome.node.solid2 import Solid2Node\n')
        self.assertFalse(result.imported('cadquery'),
                         'importing Solid2Node imported cadquery')

    def test_importing_a_brep_node_class_imports_what_it_needs(self):
        # Every B-rep class is imported from its module; the one whose
        # module reads with CadQuery imports it, and the others need no
        # front end.
        for name in BREP_CLASSES:
            module = FORMER_EXPORTS[name]
            with self.subTest(name=name):
                result = self._ran(
                    f'from {module} import {name}\n'
                    f'assert isinstance({name}, type), {name!r}\n')
                self.assertEqual(result.imported('cadquery'),
                                 name in CADQUERY_CLASSES,
                                 f'importing {name}: cadquery imported is '
                                 f'{result.imported("cadquery")}')

    def test_importing_the_node_package_does_not_import_the_step_reader(self):
        # design D10 / ADR-078: OCP is the boundary-representation
        # kernel's own package, and StepNode's reader lives inside it;
        # a bare package import must not pull it in.
        result = self._ran('import machinome.node\n')
        self.assertFalse(result.imported('OCP'),
                         'importing machinome.node imported OCP')

    def test_importing_the_step_module_imports_the_step_reader(self):
        result = self._ran(
            'from machinome.node.step import StepNode\n'
            'assert isinstance(StepNode, type), StepNode\n')
        self.assertTrue(result.imported('OCP'),
                        'importing machinome.node.step did not import OCP')

    def test_a_refused_name_imports_no_node_type(self):
        # The refusal reads the table of supported node types and nothing
        # else: it never imports the module it names.
        result = probe(
            'import sys\n'
            'try:\n'
            f'    {root_import("StepNode").strip()}\n'
            'except ImportError as refused:\n'
            "    print('REFUSED', refused)\n"
            "print('LOADED', sorted(m for m in sys.modules\n"
            f"                      if m in {NODE_TYPE_MODULES!r}))\n")
        self.assertEqual(result.status, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertTrue(lines[0].startswith('REFUSED '), result.stdout)
        self.assertIn("'machinome.node.step'", lines[0])
        self.assertEqual(lines[1], 'LOADED []')


class NodePackageRefusals(TestCase):
    """The package resolves none of the names it used to export: each is
    refused naming its module, and the module answers for it."""

    def test_all_is_empty(self):
        self.assertEqual(machinome.node.__all__, [])

    def test_every_former_export_is_refused_naming_its_module(self):
        for name, module_name in FORMER_EXPORTS.items():
            with self.subTest(name=name):
                with self.assertRaises(ImportError) as raised:
                    getattr(machinome.node, name)
                message = str(raised.exception)
                self.assertIn('exports nothing', message)
                self.assertIn(f'from {module_name} import {name}', message)

    def test_every_former_export_is_defined_by_its_module(self):
        # The module the refusal names is the one that defines the name,
        # not one that re-exports it: the one address.
        for name, module_name in FORMER_EXPORTS.items():
            with self.subTest(name=name):
                module = importlib.import_module(module_name)
                self.assertEqual(getattr(module, name).__module__,
                                 module_name)

    def test_a_class_from_its_module_is_a_real_class_not_a_proxy(self):
        # CadQueryNode is built by the CheckCQEditor metaclass and
        # consumers test it with issubclass, so a proxy would break them
        # in ways an attribute-forwarding test would not notice.
        from machinome.node.cadquery import CadQueryNode, CheckCQEditor
        from machinome.node.brep_leaf import BrepLeafNode

        self.assertIsInstance(CadQueryNode, type)
        self.assertIs(type(CadQueryNode), CheckCQEditor)
        self.assertTrue(issubclass(CadQueryNode, BrepLeafNode))

    def test_star_import_binds_nothing(self):
        result = probe(
            'before = set(dir())\n'
            'from machinome.node ' 'import *\n'
            "print(sorted(set(dir()) - before - {'before'}))\n")
        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), '[]')

    def test_dir_offers_no_former_export(self):
        listed = dir(machinome.node)
        for name in FORMER_EXPORTS:
            with self.subTest(name=name):
                self.assertNotIn(name, listed)

    def test_a_refused_name_is_never_cached(self):
        # A refusal binds nothing in the package's namespace, so a second
        # read is refused again rather than answered from a stale binding.
        result = probe(
            'import machinome.node as node\n'
            'for attempt in (1, 2):\n'
            '    try:\n'
            "        getattr(node, 'StlNode')\n"
            '    except ImportError:\n'
            "        print('REFUSED', 'StlNode' in vars(node))\n")
        self.assertEqual(result.stdout.split(),
                         ['REFUSED', 'False', 'REFUSED', 'False'],
                         result.stderr)

    def test_an_unknown_name_still_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            machinome.node.NoSuchNode

    def test_an_unknown_name_is_not_reported_as_an_import_failure(self):
        result = probe(
            'import machinome.node\n'
            'try:\n'
            '    machinome.node.NoSuchNode\n'
            'except AttributeError:\n'
            "    print('ATTRIBUTE_ERROR')\n"
            'except Exception as other:\n'
            "    print('OTHER', type(other).__name__, other)\n"
            'else:\n'
            "    print('NO_ERROR')\n")
        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'ATTRIBUTE_ERROR')


class NodePackageSubmodules(TestCase):
    """Submodules are reachable through the package.

    A consumer reads `machinome.node.assembly` after importing only the
    package, or writes `from machinome.node import supported`; the
    accessor resolves submodule names, or that quietly breaks.
    """

    def test_a_submodule_is_reachable_after_a_bare_package_import(self):
        for submodule in ('assembly', 'operations', 'cadquery'):
            with self.subTest(submodule=submodule):
                result = probe(
                    'import machinome.node\n'
                    f'module = machinome.node.{submodule}\n'
                    'print(module.__name__)\n')
                self.assertEqual(result.status, 0, result.stderr)
                self.assertEqual(result.stdout.strip(),
                                 f'machinome.node.{submodule}')

    def test_submodules_are_imported_through_the_package(self):
        result = probe(
            'from machinome.node import supported, phase, step\n'
            'print(supported.__name__, phase.__name__, step.__name__)\n')
        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout.split(),
                         ['machinome.node.supported', 'machinome.node.phase',
                          'machinome.node.step'])

    def test_a_submodule_attribute_is_the_imported_module(self):
        module = importlib.import_module('machinome.node.assembly')
        self.assertIs(machinome.node.assembly, module)

    def test_reading_a_submodule_does_not_import_its_siblings(self):
        result = probe('import machinome.node\n'
                       'machinome.node.assembly\n'
                       "print('DONE')\n")
        self.assertEqual(result.stdout.strip(), 'DONE', result.stderr)
        self.assertFalse(result.imported('cadquery'),
                         'reading one submodule imported the B-rep stack')


class NodePackageMovedNames(TestCase):
    """Ports and the declared time base answer from `machinome.motion.ports`
    now, not from this package -- `motion-package`'s deliberate,
    unshimmed break. `tests/test_motion_package.py` owns the fuller
    behavioural pin; this class keeps the moved names inside the same
    discipline as every other name here.
    """

    def test_a_moved_name_is_not_in_all(self):
        for name in MOVED_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, machinome.node.__all__)

    def test_reading_a_moved_name_names_its_new_home(self):
        # ImportError, not AttributeError: CPython's `from X import Y`
        # discards an AttributeError's message and substitutes its own
        # generic "cannot import name" text, so only an exception outside
        # AttributeError's hierarchy can carry this message all the way
        # through the import line below.
        for name in MOVED_NAMES:
            with self.subTest(name=name):
                with self.assertRaises(ImportError) as raised:
                    getattr(machinome.node, name)
                self.assertIn('machinome.motion.ports', str(raised.exception))

    def test_importing_a_moved_name_raises_import_error(self):
        for name in ('Port', 'RotationalPort', 'TranslationalPort',
                     'SignalPort', 'declared_ports', 'Time'):
            with self.subTest(name=name):
                result = probe(
                    f'from machinome.node import {name}\n'
                    "print('NO_ERROR')\n")
                self.assertNotEqual(result.stdout.strip(), 'NO_ERROR')
                self.assertIn('machinome.motion.ports', result.stderr)


class NodePackageBrokenBackend(TestCase):
    """A submodule that fails to import reports its own failure.

    This is the classic PEP 562 trap: an `ImportError` raised inside
    `__getattr__` looks, to anything that treats the accessor as a
    lookup, like the name simply not being there. A broken install must
    not be reported as a missing attribute, and an absent extra must not
    be reported as a broken install: since the `lean-install` change the
    CAD kernels are extras, so a missing cadquery is an install that has
    not asked for the `step` extra, and the step module's own refusal,
    naming the extra, reaches the caller unmodified. The package's
    deferred names are its submodules, so the doors are
    `machinome.node.step` and `from machinome.node import step`.
    """

    def _access(self, expression, blocker=CADQUERY_ABSENT):
        return probe(
            blocker +
            'import machinome.node\n'
            'try:\n'
            f'    {expression}\n'
            'except AttributeError as wrong:\n'
            "    print('ATTRIBUTE_ERROR', wrong)\n"
            'except ModuleNotFoundError as absent:\n'
            "    print('ABSENT', type(absent).__name__, absent.name,\n"
            "          getattr(absent, 'extra', None), '|', absent)\n"
            'except ImportError as failure:\n'
            "    print('IMPORT_ERROR', failure)\n"
            'except Exception as other:\n'
            "    print('OTHER', type(other).__name__, other)\n"
            'else:\n'
            "    print('NO_ERROR')\n")

    def test_the_package_still_imports_without_the_brep_stack(self):
        # cadquery is the `step` and `cadquery` extras' kernel, not a
        # required dependency: the package imports without it, and the
        # failure is allowed only at first use of a module that needs it.
        result = probe(CADQUERY_ABSENT +
                       'import machinome.node\n'
                       "print('IMPORTED')\n")
        self.assertEqual(result.stdout.strip(), 'IMPORTED', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    # `step` is the node type whose module needs cadquery itself; the
    # CadQuery module imports none (it reached cadquery only through the
    # exact layer before the `exact-engine` change).
    def test_an_absent_extra_raises_the_modules_refusal_unmodified(self):
        result = self._access('machinome.node.step')
        self.assertEqual(result.status, 0, result.stderr)
        reported = result.stdout.strip()
        self.assertTrue(reported.startswith('ABSENT ExtraUnavailable '
                                            'cadquery step |'), reported)
        self.assertIn('StepNode', reported)
        self.assertIn('pip install "machinome[step]"', reported)
        self.assertNotIn('raised resolving', reported)

    def test_from_import_carries_the_refusal(self):
        result = probe(
            CADQUERY_ABSENT +
            'try:\n'
            '    from machinome.node import step\n'
            'except ImportError as failure:\n'
            "    print(type(failure).__name__, '|', failure)\n")
        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout.strip(),
                         f'ExtraUnavailable | {STEP_REFUSAL}')

    def test_the_root_refuses_a_class_before_the_module_refuses_its_kernel(
            self):
        # The root's refusal imports no node type, so where CadQuery is
        # absent the class name meets the root's refusal naming the
        # module, and the line it suggests meets the module's refusal
        # naming the extra.
        result = probe(
            CADQUERY_ABSENT +
            'for line in (' + repr(root_import('StepNode')) + ',\n'
            "             'from machinome.node.step import StepNode\\n'):\n"
            '    try:\n'
            '        exec(line, {})\n'
            '    except ImportError as failure:\n'
            "        print(type(failure).__name__, '|', failure)\n")
        self.assertEqual(result.status, 0, result.stderr)
        root, module = result.stdout.strip().splitlines()
        self.assertTrue(root.startswith('ImportError | '), root)
        self.assertIn("is imported from its module, 'machinome.node.step'",
                      root)
        self.assertEqual(module, f'ExtraUnavailable | {STEP_REFUSAL}')

    def test_hasattr_does_not_turn_an_absent_extra_into_a_missing_name(self):
        result = probe(
            CADQUERY_ABSENT +
            'import machinome.node\n'
            'try:\n'
            "    present = hasattr(machinome.node, 'step')\n"
            'except ImportError as failure:\n'
            "    print('IMPORT_ERROR', failure)\n"
            'else:\n'
            "    print('SWALLOWED', present)\n")
        self.assertEqual(result.status, 0, result.stderr)
        reported = result.stdout.strip()
        self.assertTrue(reported.startswith('IMPORT_ERROR'), reported)
        self.assertIn('machinome[step]', reported)
        self.assertNotIn('raised resolving', reported)

    def test_a_broken_backend_raises_the_underlying_import_error(self):
        result = self._access('machinome.node.step',
                              blocker=CADQUERY_BROKEN)
        self.assertEqual(result.status, 0, result.stderr)
        reported = result.stdout.strip()
        self.assertTrue(reported.startswith('IMPORT_ERROR broken cadquery'),
                        reported)

    def test_the_reported_failure_names_the_requested_submodule(self):
        result = self._access('machinome.node.step',
                              blocker=CADQUERY_BROKEN)
        self.assertEqual(result.status, 0, result.stderr)
        self.assertIn('(raised resolving machinome.node.step from .step)',
                      result.stdout)

    def test_from_import_reports_a_broken_backend_naming_the_submodule(self):
        result = probe(
            CADQUERY_BROKEN +
            'try:\n'
            '    from machinome.node import step\n'
            'except ImportError as failure:\n'
            "    print(type(failure).__name__, '|', failure)\n")
        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(
            result.stdout.strip(),
            'ImportError | broken cadquery (raised resolving '
            'machinome.node.step from .step)')

    def test_hasattr_does_not_turn_a_broken_backend_into_a_missing_name(self):
        result = probe(
            CADQUERY_BROKEN +
            'import machinome.node\n'
            'try:\n'
            "    present = hasattr(machinome.node, 'step')\n"
            'except ImportError as failure:\n'
            "    print('IMPORT_ERROR', failure)\n"
            'else:\n'
            "    print('SWALLOWED', present)\n")
        self.assertEqual(result.status, 0, result.stderr)
        reported = result.stdout.strip()
        self.assertTrue(reported.startswith('IMPORT_ERROR'), reported)
        self.assertIn('machinome.node.step', reported)


class ParameterModuleSurface(TestCase):
    """Build parameters come from `machinome.parameters`, and only there.

    Two properties, and the second is the one that decays: a module can
    be created without anyone noticing that the old path still works, and
    then every import line is ambiguous again for no reason a reader can
    see. So the absence is pinned as hard as the presence.

    The import cost is pinned too. This module sits at the top of every
    node module in every project, and it holds nothing but declarations
    and arithmetic over exponents, so it must reach no framework module
    and no CAD backend at all -- which is also why it needs no lazy
    accessor of its own.
    """

    # Everything a project or the framework may name. The kinds and the
    # `Quantity` base a project subclasses to extend the ontology, the
    # algebra types a formula is built from, the enumerator, and the two
    # errors a bad declaration raises.
    EXPECTED = ('Quantity', 'Length', 'Angle', 'Count', 'Ratio', 'Scalar',
                'Flag', 'Expression', 'Formula', 'declared_parameters',
                'DimensionError', 'ParameterError')

    def test_the_module_exports_the_parameter_vocabulary(self):
        import machinome.parameters as parameters

        self.assertEqual(sorted(parameters.__all__), sorted(self.EXPECTED))

    def test_the_node_package_does_not_export_a_parameter(self):
        for name in PARAMETER_NAMES:
            with self.subTest(name=name):
                self.assertNotIn(name, machinome.node.__all__)
                with self.assertRaises(AttributeError) as raised:
                    getattr(machinome.node, name)
                self.assertIn(name, str(raised.exception))

    def test_importing_parameters_imports_nothing_else(self):
        result = probe('import machinome.parameters\n'
                       "print('DONE')\n")
        self.assertEqual(result.stdout.strip(), 'DONE', result.stderr)
        self.assertFalse(result.imported('cadquery'),
                         'importing machinome.parameters imported cadquery')
        self.assertEqual(
            result.imported_under('machinome'),
            {'machinome', 'machinome.parameters'},
            'importing machinome.parameters reached another framework '
            'module')

    def test_the_names_are_bound_eagerly(self):
        # No `__getattr__` accessor here: there is nothing expensive to
        # defer, and deferral would be indirection a reader has to unpick
        # for no gain. Read out of the module dict, which an accessor
        # would not have populated.
        import machinome.parameters as parameters

        for name in self.EXPECTED:
            with self.subTest(name=name):
                self.assertIn(name, vars(parameters))

    def test_a_declaration_module_defines_no_parameter_kind(self):
        # The other half of the cut. `declarative` keeps the structure
        # declarations, so no kind is DEFINED there any more and a
        # caller reaching for one is reaching into the wrong module. It
        # does borrow three names -- the declaration base the declaring
        # namespace tests against, the operand evaluator a child
        # declaration resolves its arguments with, and the enumerator
        # construction reads -- and those are imports, pinned here to
        # come from the parameter module and nowhere else.
        from machinome.node import declarative

        for name in ('Length', 'Angle', 'Count', 'Ratio', 'Scalar',
                     'Quantity', 'Flag', 'Expression', 'Formula'):
            with self.subTest(name=name):
                self.assertNotIn(name, vars(declarative))

        for name in ('Declaration', 'evaluate', 'declared_parameters'):
            with self.subTest(name=name):
                self.assertEqual(getattr(declarative, name).__module__,
                                 'machinome.parameters')
