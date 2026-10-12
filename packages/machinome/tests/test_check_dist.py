# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
"""`scripts/check-dist --out DIR` keeps the archives it proved.

The repository's `scripts/check-dist` builds every member's sdist and wheel
outside the repository, checks them with `twine check --strict`, installs
and smokes them, and uploads nothing. With `--out DIR` it refuses, before it
builds anything, a `DIR` that exists and is not an empty folder, and once
every check has passed it copies every archive it built, flat, into `DIR`,
which `make dist` names `dist/vX.Y.Z` and `make upload` uploads (change
`release-tooling`, ADR-192). A check that fails leaves no `DIR`.

These tests load the script from the checkout, as the layout tests read it,
and drive its functions with stand-ins: they build nothing.
"""

import ast
import importlib.machinery
import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


REPOSITORY = Path(__file__).resolve().parents[3]
SCRIPT = REPOSITORY / 'scripts' / 'check-dist'


def load():
    """The script as a module, its `main` not run."""
    loader = importlib.machinery.SourceFileLoader('check_dist', str(SCRIPT))
    spec = importlib.util.spec_from_loader('check_dist', loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class CheckDistOutTest(unittest.TestCase):

    def setUp(self):
        self.script = load()
        self.tmp = Path(tempfile.mkdtemp(prefix='test-check-dist-'))
        self.addCleanup(shutil.rmtree, self.tmp)

    def never(self, *args, **kwargs):
        self.fail('check-dist reached the members before refusing the folder')

    def test_the_script_parses(self):
        ast.parse(SCRIPT.read_text(), filename=str(SCRIPT))

    def test_out_refuses_a_folder_that_is_not_empty(self):
        out = self.tmp / 'v0.8.1'
        out.mkdir()
        (out / 'machinome-0.8.1.tar.gz').write_bytes(b'kept before')
        with mock.patch.object(self.script, 'members', self.never):
            with self.assertRaises(self.script.Failure) as refused:
                self.script.main(['--out', str(out)])
        self.assertIn(str(out), str(refused.exception))
        self.assertIn('not an empty folder', str(refused.exception))
        self.assertEqual([path.name for path in out.iterdir()],
                         ['machinome-0.8.1.tar.gz'])

    def test_out_refuses_a_file(self):
        out = self.tmp / 'v0.8.1'
        out.write_text('a file')
        with mock.patch.object(self.script, 'members', self.never):
            with self.assertRaises(self.script.Failure) as refused:
                self.script.main(['--out', str(out)])
        self.assertIn(str(out), str(refused.exception))
        self.assertEqual(out.read_text(), 'a file')

    def built(self, scratch, member, *names):
        folder = scratch / 'dist' / member
        folder.mkdir(parents=True)
        for name in names:
            (folder / name).write_bytes(f'{member}/{name}'.encode())
        return folder

    def test_keep_copies_every_archive_flat(self):
        scratch = self.tmp / 'scratch'
        first = self.built(scratch, 'machinome', 'machinome-0.8.1.tar.gz',
                           'machinome-0.8.1-py3-none-any.whl', 'stray.txt')
        second = self.built(scratch, 'machinome-skills',
                            'machinome_skills-0.8.1.tar.gz',
                            'machinome_skills-0.8.1-py3-none-any.whl')
        wheels = {'machinome': first / 'machinome-0.8.1-py3-none-any.whl',
                  'machinome-skills':
                      second / 'machinome_skills-0.8.1-py3-none-any.whl'}
        out = self.tmp / 'dist' / 'v0.8.1'
        self.script.keep(out, scratch, wheels)
        kept = sorted(path.name for path in out.iterdir())
        self.assertEqual(kept, ['machinome-0.8.1-py3-none-any.whl',
                                'machinome-0.8.1.tar.gz',
                                'machinome_skills-0.8.1-py3-none-any.whl',
                                'machinome_skills-0.8.1.tar.gz'])
        for name in kept:
            with self.subTest(archive=name):
                source = next(folder / name for folder in (first, second)
                              if (folder / name).exists())
                self.assertEqual((out / name).read_bytes(),
                                 source.read_bytes())
        self.assertTrue((first / 'stray.txt').exists())

    def test_keep_refuses_two_archives_of_one_name(self):
        scratch = self.tmp / 'scratch'
        first = self.built(scratch, 'one', 'same-0.8.1.tar.gz')
        second = self.built(scratch, 'two', 'same-0.8.1.tar.gz')
        out = self.tmp / 'dist' / 'v0.8.1'
        with self.assertRaises(self.script.Failure) as refused:
            self.script.keep(out, scratch, {'one': first, 'two': second})
        self.assertIn('same-0.8.1.tar.gz', str(refused.exception))
        self.assertFalse(out.exists(), f'{out} was created')

    def test_nothing_is_kept_when_a_check_fails(self):
        out = self.tmp / 'dist' / 'v0.8.1'
        member = self.tmp / 'packages' / 'machinome-skills'
        member.mkdir(parents=True)

        def fails(directory, name, scratch):
            raise self.script.Failure(f'{name}: twine check failed')

        with mock.patch.object(self.script, 'members',
                               lambda: [(member, 'machinome-skills')]), \
                mock.patch.object(self.script, 'build', fails):
            with self.assertRaises(self.script.Failure):
                self.script.main(['--out', str(out)])
        self.assertFalse(out.exists(), f'{out} was created')
        self.assertFalse(out.parent.exists(), f'{out.parent} was created')


if __name__ == '__main__':
    unittest.main()
