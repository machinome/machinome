# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""Fake installed distributions that contribute commands to `machinome`.

A package adds a command through the entry-point group `machinome.commands`
(OpenSpec change `commands-contributed-by-packages`, ADR-189). What the
standard library reports as installed is any `<name>.dist-info` directory
on `sys.path`, so a test installs a command without installing anything:
`write_distribution` writes the `.dist-info` with its `METADATA` and its
`entry_points.txt`, and the module beside it, into a temporary directory.

Two ways to put those directories on the path, for the two kinds of test:

- `distributions(*fakes)` gives the environment of a fresh interpreter
  (`import_probe.probe(..., env=...)`): a `PYTHONPATH` with the framework's
  directory first, as the probe sets it, then one directory per fake.
- `installed(*fakes)` prepends them to this process's `sys.path`, and on
  exit takes them off and forgets the fake modules, so no test leaves a
  command installed for the next.

Nothing is ever written under the repository, and nothing of the suite's
environment is installed or uninstalled.
"""

import importlib
import os
import sys
import tempfile
from contextlib import ExitStack, contextmanager

from .import_probe import REPO_DIR


#: The group the fakes declare their commands in, spelled here rather than
#: read from `machinome.cli`, so a renamed group fails the tests.
GROUP = 'machinome.commands'


# Named as no package of the set is: the suite's environment installs the
# movie package, whose command is `machinome movie` (`join-movie`).
FILM = '''
class Film:
    """Make films of machines (a fake contributed command)."""

    needs_node = False

    def add_arguments(self, parser):
        verbs = parser.add_subparsers(dest='verb', required=True)
        for verb in ('list', 'build', 'render'):
            verbs.add_parser(verb).add_argument('source')

    def handle(self, args):
        print(f'film {args.verb} {args.source}')
'''

# A second contributor, named as no package of the set is, so the fake
# never meets a command the suite's environment installs (`join-skills`).
LESSONS = '''
class Lessons:
    """Teach a lesson (a fake contributed command)."""

    needs_node = False

    def add_arguments(self, parser):
        verbs = parser.add_subparsers(dest='verb', required=True)
        for verb in ('install', 'list'):
            verbs.add_parser(verb)

    def handle(self, args):
        print(f'lessons {args.verb}')
'''

NODE = '''
class Measure:
    """Measure a node (a fake contributed command that operates on one)."""

    needs_node = True

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        print(f'measure {args.path} {args.set}')
'''

SHADOW = '''
class Build:
    """Build something else (a fake that takes a framework command's name)."""

    needs_node = False

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        print('shadow build ran')
'''

FILM_TWO = '''
class Film:
    """Make other films (a second fake contributing the name film)."""

    needs_node = False

    def add_arguments(self, parser):
        pass

    def handle(self, args):
        print('the other film ran')
'''

NEEDY = '''
from machinome.extras import ExtraUnavailable

raise ExtraUnavailable('step', 'the needy fake command', 'cadquery')
'''

BARE = '''
class Bare:
    pass
'''

PORTION = '''
class Portioned:
    """Shipped as a portion of the machinome namespace (a fake)."""

    needs_node = False

    def add_arguments(self, parser):
        parser.add_argument('word')

    def handle(self, args):
        print(f'portioned {args.word}')
'''


#: Each fake: its distribution's name, its entries, and its module's path
#: below the directory with the module's source (None: no module is
#: written, so the entry names a module that does not exist).
FAKES = {
    'fake-film': (['film = machinome_fake_film:Film'],
                  'machinome_fake_film.py', FILM),
    'fake-lessons': (['lessons = machinome_fake_lessons:Lessons'],
                     'machinome_fake_lessons.py', LESSONS),
    'fake-node': (['measure = machinome_fake_node:Measure'],
                  'machinome_fake_node.py', NODE),
    'fake-shadow': (['build = machinome_fake_shadow:Build'],
                    'machinome_fake_shadow.py', SHADOW),
    'fake-film-two': (['film = machinome_fake_film_two:Film'],
                      'machinome_fake_film_two.py', FILM_TWO),
    'fake-needy': (['needy = machinome_fake_needy:Needy'],
                   'machinome_fake_needy.py', NEEDY),
    'fake-bare': (['bare = machinome_fake_bare:Bare'],
                  'machinome_fake_bare.py', BARE),
    'fake-gone': (['gone = machinome_fake_gone:Gone'], None, None),
    # A command shipped as a portion of the `machinome` namespace, as the
    # movie package's `machinome.movie` ships (`join-movie`): its module
    # under a `machinome/` directory holding no `__init__.py`.
    'fake-portion': (['portioned = machinome.fake_portion_command:Portioned'],
                     os.path.join('machinome', 'fake_portion_command.py'),
                     PORTION),
}

#: Every module the fakes define, forgotten when `installed` exits.
FAKE_MODULES = ('machinome_fake_film', 'machinome_fake_lessons',
                'machinome_fake_node', 'machinome_fake_shadow',
                'machinome_fake_film_two', 'machinome_fake_needy',
                'machinome_fake_bare', 'machinome_fake_gone',
                'machinome.fake_portion_command')


def write_distribution(root, dist, entries, module_path=None, source=None):
    """Write the installed distribution `dist` into the directory `root`.

    `<dist>-0.0.0.dist-info` holds `METADATA` and an `entry_points.txt`
    declaring `entries` (`'name = module:Class'`) in the group; the
    module's source, when there is one, is written at `module_path` below
    `root`.
    """
    info = os.path.join(root, f'{dist.replace("-", "_")}-0.0.0.dist-info')
    os.makedirs(info)
    with open(os.path.join(info, 'METADATA'), 'w') as handle:
        handle.write(f'Metadata-Version: 2.1\nName: {dist}\nVersion: 0.0.0\n')
    with open(os.path.join(info, 'entry_points.txt'), 'w') as handle:
        handle.write(f'[{GROUP}]\n' + ''.join(f'{entry}\n' for entry in entries))
    if module_path is not None:
        path = os.path.join(root, module_path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as handle:
            handle.write(source)
    return root


@contextmanager
def fake_directories(*fakes):
    """One temporary directory per fake of `FAKES`, each holding that fake
    installed; removed on exit."""
    with ExitStack() as stack:
        directories = []
        for fake in fakes:
            entries, module_path, source = FAKES[fake]
            root = stack.enter_context(tempfile.TemporaryDirectory(
                prefix=f'machinome-{fake}-'))
            directories.append(write_distribution(root, fake, entries,
                                                  module_path, source))
        yield directories


@contextmanager
def distributions(*fakes):
    """The environment of a fresh interpreter with `fakes` installed: the
    `env` of `import_probe.probe`."""
    with fake_directories(*fakes) as directories:
        yield {'PYTHONPATH': os.pathsep.join([REPO_DIR, *directories])}


@contextmanager
def installed(*fakes):
    """`fakes` installed in this process for the length of the block."""
    with fake_directories(*fakes) as directories:
        sys.path[:0] = directories
        importlib.invalidate_caches()
        try:
            yield directories
        finally:
            for directory in directories:
                sys.path.remove(directory)
            for module in FAKE_MODULES:
                sys.modules.pop(module, None)
            importlib.invalidate_caches()
