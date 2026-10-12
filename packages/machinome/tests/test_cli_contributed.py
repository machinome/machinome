# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Commands an installed package contributes to `machinome`.

The `cli` capability's requirement "An installed package may contribute a
command" and the grammar's position rule (OpenSpec change
`commands-contributed-by-packages`, ADR-189). Each test installs fake
distributions written by `tests/contributed_commands.py` into temporary
directories: on a fresh interpreter's `PYTHONPATH` where what was imported
is under test (`import_probe.probe`), on this process's `sys.path` where a
handler is patched.
"""

import io
import os
import sys
from contextlib import redirect_stderr
from unittest import TestCase
from unittest.mock import patch

from machinome.cli import manage

from .contributed_commands import distributions, installed
from .import_probe import probe


#: Every framework command module and the order `machinome -h` lists the
#: commands in, spelled independently of the registry as
#: `tests/test_cli_lazy_imports.py` spells them.
COMMAND_MODULES = {
    'machinome.manager.build', 'machinome.manager.develop',
    'machinome.manager.test', 'machinome.manager.snapshot',
    'machinome.manager.new', 'machinome.manager.export',
    'machinome.manager.viewer', 'machinome.manager.models',
    'machinome.manager.import_step', 'machinome.manager.vet',
}
COMMAND_ORDER = ['build', 'develop', 'test', 'snapshot', 'new', 'export',
                 'viewer', 'models', 'import-step', 'vet']

MIGRATION_HINT = ('The CLI grammar changed in 0.4: commands come first. '
                  'Try: machinome {command} {path} [options]\n')

DISPATCH = 'from machinome.cli import manage; manage()\n'

MOVIE_DOC = 'Make films of machines (a fake contributed command).'
SKILLS_DOC = 'Install the agent skills (a fake contributed command).'


def run(*fakes, argv):
    """`machinome <argv>` in a fresh interpreter with `fakes` installed."""
    with distributions(*fakes) as env:
        return probe(DISPATCH, argv=argv, env=env)


def squeezed(text):
    """`text` without whitespace: argparse wraps help where it likes."""
    return ''.join(text.split())


class ContributedCommandTest(TestCase):
    """Requirement "An installed package may contribute a command"."""

    def test_help_lists_contributed_commands_after_the_framework(self):
        """Scenario "A contributed command is listed"."""
        result = run('fake-movie', 'fake-skills', argv=['-h'])

        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertIn('{' + ','.join([*COMMAND_ORDER, 'movie', 'skills']) + '}',
                      result.stdout)
        help_text = squeezed(result.stdout)
        self.assertIn('movie' + squeezed(MOVIE_DOC), help_text)
        self.assertIn('skills' + squeezed(SKILLS_DOC), help_text)

    def test_a_contributed_command_runs_with_its_own_verbs(self):
        """Scenarios "A contributed command runs" and "A later argument
        spells a framework command": a verb or a source spelling a framework
        command (`build`) is the contributed command's argument."""
        for argv in (['movie', 'build', 'film.yaml'],
                     ['movie', 'list', 'build'],
                     ['movie', 'render', 'film.yaml']):
            with self.subTest(argv=argv):
                result = run('fake-movie', argv=argv)

                self.assertEqual(result.status, 0, result.stderr)
                self.assertEqual(result.stdout, ' '.join(argv) + '\n')
                self.assertTrue(result.imported('machinome_fake_movie'))
                self.assertEqual(sorted(COMMAND_MODULES & result.modules), [])

    def test_a_second_contributor_runs(self):
        """Scenario "A contributed command runs", for a second package."""
        result = run('fake-skills', argv=['skills', 'install'])

        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout, 'skills install\n')

    def test_a_command_shipped_as_a_namespace_portion_runs(self):
        """Scenario "A contributed command runs", its module a portion of
        the `machinome` namespace with no `__init__.py` of its own."""
        result = run('fake-portion', argv=['portioned', 'hello'])

        self.assertEqual(result.status, 0, result.stderr)
        self.assertEqual(result.stdout, 'portioned hello\n')

    def test_a_contributed_command_operates_on_a_node(self):
        """Scenario "A contributed command operates on a node"."""
        with installed('fake-node'):
            with patch.object(sys, 'argv', ['machinome', 'measure', 'model.py',
                                            '--set', 'bore=3']):
                with patch('machinome_fake_node.Measure.handle') as handle:
                    manage()
            self.assertTrue(handle.called)
            args = handle.call_args[0][0]
            self.assertEqual(args.path, 'model.py')
            self.assertEqual(args.set, ['bore=3'])

            directory = os.path.dirname(os.path.abspath(__file__))
            stderr = io.StringIO()
            with patch.object(sys, 'argv', ['machinome', 'measure', directory]):
                with patch('machinome_fake_node.Measure.handle') as handle:
                    with redirect_stderr(stderr):
                        with self.assertRaises(SystemExit) as stop:
                            manage()
        self.assertEqual(stop.exception.code, 2)
        self.assertFalse(handle.called)
        message = stderr.getvalue()
        self.assertIn('package.module:Class', message)
        self.assertIn('path/to/file.py', message)
        self.assertIn('path/to/file.py:Class', message)

    def test_a_framework_command_reads_no_entry_point(self):
        """Scenario "A framework command reads no entry point" of
        `cli-startup-cost`: green before the change, a guard."""
        result = run('fake-movie', argv=['vet', '-h'])

        self.assertEqual(result.status, 0, result.stderr)
        self.assertFalse(result.imported('importlib.metadata'))
        self.assertFalse(result.imported('machinome_fake_movie'))
        self.assertEqual(sorted(COMMAND_MODULES & result.modules),
                         ['machinome.manager.vet'])

    def test_an_unknown_name_names_the_contributed_commands(self):
        """`cli-startup-cost`: an unknown name's error names the valid
        commands, the contributed ones included."""
        result = run('fake-movie', argv=['frobnicate'])

        self.assertEqual(result.status, 2)
        for name in [*COMMAND_ORDER, 'movie']:
            self.assertIn(name, result.stderr)
        self.assertEqual(sorted(COMMAND_MODULES & result.modules), [])
        self.assertFalse(result.imported('machinome_fake_movie'))

    def test_the_legacy_grammar_reads_the_contributed_names(self):
        """Scenario "Legacy grammar with a contributed command"."""
        result = run('fake-movie', argv=['film.yaml', 'movie'])

        self.assertEqual(result.status, 2)
        self.assertEqual(result.stderr, MIGRATION_HINT)
        self.assertEqual(result.stdout, '')
        self.assertFalse(result.imported('machinome_fake_movie'))


class ContributedCollisionTest(TestCase):
    """The collisions of the requirement: never resolved by install order."""

    def test_a_framework_name_is_never_taken(self):
        """Scenario "A contributed name is a framework command's"."""
        clean_help = run(argv=['-h'])
        clean_build = run(argv=['build', '-h'])

        shadowed_help = run('fake-shadow', argv=['-h'])
        self.assertEqual(shadowed_help.status, 0, shadowed_help.stderr)
        self.assertEqual(shadowed_help.stdout, clean_help.stdout)
        self.assertEqual(
            shadowed_help.stderr,
            "Warning: fake-shadow contributes the command build "
            "(machinome_fake_shadow:Build), which is machinome's own; "
            "it is not used\n")
        self.assertFalse(shadowed_help.imported('machinome_fake_shadow'))

        shadowed_build = run('fake-shadow', argv=['build', '-h'])
        self.assertEqual(shadowed_build.status, 0, shadowed_build.stderr)
        self.assertEqual(shadowed_build.stdout, clean_build.stdout)
        self.assertEqual(shadowed_build.stderr, '')
        self.assertFalse(shadowed_build.imported('machinome_fake_shadow'))

    def test_a_name_two_packages_contribute_runs_neither(self):
        """Scenario "Two packages contribute one name"."""
        located = ('fake-movie (machinome_fake_movie:Movie), '
                   'fake-movie-two (machinome_fake_movie_two:Movie)')
        result = run('fake-movie', 'fake-movie-two',
                     argv=['movie', 'list', 'x'])

        self.assertEqual(result.status, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(
            result.stderr,
            f'Error: machinome movie is contributed by more than one '
            f'package: {located}\n')
        self.assertFalse(result.imported('machinome_fake_movie'))
        self.assertFalse(result.imported('machinome_fake_movie_two'))

        listed = run('fake-movie', 'fake-movie-two', argv=['-h'])
        self.assertEqual(listed.status, 0, listed.stderr)
        listing = [line.split()[:2] for line in listed.stdout.splitlines()
                   if line.split()[:1] == ['movie']]
        self.assertEqual(listing, [['movie', '(unavailable:']])
        self.assertIn(
            squeezed(f'movie (unavailable: contributed by more than one '
                     f'package: {located})'),
            squeezed(listed.stdout))


class ContributedFailureTest(TestCase):
    """A contributed command that cannot run is named, and never takes the
    help from the other commands."""

    def test_a_command_lacking_its_extra_is_answered_by_it(self):
        """Scenario "A contributed command lacks its extra"."""
        refusal = ('the needy fake command needs cadquery, which is not '
                   'installed; install it with \'pip install '
                   '"machinome[step]"\'')
        result = run('fake-needy', argv=['needy', 'model.py'])

        self.assertEqual(result.status, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr,
                         f'Error: machinome needy needs the step extra: '
                         f'{refusal}\n')

        listed = run('fake-needy', argv=['-h'])
        self.assertEqual(listed.status, 0, listed.stderr)
        self.assertIn(squeezed(f'needy (unavailable: needs the step extra: '
                               f'{refusal})'),
                      squeezed(listed.stdout))

    def test_a_class_not_meeting_the_contract_is_refused(self):
        """Scenario "A contributed class does not meet the contract"."""
        reason = ('fake-bare (machinome_fake_bare:Bare) does not meet the '
                  'command contract: no docstring')
        result = run('fake-bare', argv=['bare'])

        self.assertEqual(result.status, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, f'Error: machinome bare: {reason}\n')

        listed = run('fake-bare', argv=['-h'])
        self.assertEqual(listed.status, 0, listed.stderr)
        self.assertIn(squeezed(f'bare (unavailable: {reason})'),
                      squeezed(listed.stdout))

    def test_a_module_that_cannot_be_imported(self):
        """Scenario "A contributed module cannot be imported"."""
        listed = run('fake-gone', argv=['-h'])

        self.assertEqual(listed.status, 0, listed.stderr)
        self.assertNotIn('Traceback', listed.stderr)
        self.assertIn(squeezed(
            "gone (unavailable: fake-gone (machinome_fake_gone:Gone) cannot "
            "be loaded: ModuleNotFoundError: No module named "
            "'machinome_fake_gone')"), squeezed(listed.stdout))
        # Every other command is listed as it would be without it.
        self.assertIn('{' + ','.join([*COMMAND_ORDER, 'gone']) + '}',
                      listed.stdout)

        result = run('fake-gone', argv=['gone'])
        self.assertEqual(result.status, 1)
        self.assertIn('Traceback', result.stderr)
        self.assertIn("ModuleNotFoundError: No module named "
                      "'machinome_fake_gone'", result.stderr)
