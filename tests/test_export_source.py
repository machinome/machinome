# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""An export records the source revision it was made from.

Born of filming the clocked Curta: the film is held to the model it filmed
by the revision of the project the export came from, and `machinome
export` recorded none, so the film's export carried a
`source-revision.txt` written by hand. The manifest now carries
`source: {revision, dirty}` when the project root is inside a Git work
tree with a commit, and is byte for byte what it was everywhere else
(OpenSpec change `export-records-its-revision`, ADR-158).

Every export here goes through the real `machinome export` command in a
fresh interpreter, from a project built in a temporary directory, with Git
confined to that directory and blind to the user's configuration.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


FRAMEWORK = Path(__file__).resolve().parents[1]

#: The manifest this project exported at the base commit of the change,
#: before the source record existed. Captured twice, from two locations,
#: with identical bytes.
PINNED = Path(__file__).resolve().parent / 'fixtures' / \
    'export_outside_a_repository.json'

#: Every source file's mtime, so each node's published `mtime` is fixed.
SOURCE_TIME_NS = 1_700_000_000 * 10**9

PROJECT = {
    'pyproject.toml': '[tool.machinome]\nmodel = "design.part:Part"\n',
    # What `machinome new` writes.
    '.gitignore': '_build*\n__pycache__/\nsnapshot.png\n.env\n',
    'design/__init__.py': '',
    'design/part.py': (
        'from machinome.node import Solid2Node\n'
        'from solid2 import cube\n'
        'class Part(Solid2Node):\n'
        '    def render(self):\n'
        '        return cube(1)\n'
    ),
}


class ExportSourceRecordTest(TestCase):

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(
            prefix='machinome-export-source-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.project = self.base / 'project'
        (self.project / 'design').mkdir(parents=True)
        for name, text in PROJECT.items():
            path = self.project / name
            path.write_text(text)
            os.utime(path, ns=(SOURCE_TIME_NS, SOURCE_TIME_NS))
        self.exports = 0

    def environment(self):
        """Git confined to the temporary directory, with no user or
        system configuration, for the fixture's commands and the
        export's alike."""
        environment = {key: value for key, value in os.environ.items()
                       if not key.startswith('GIT_')}
        environment.pop('SOLID_BUILD_DIR', None)
        environment.update({
            'GIT_CEILING_DIRECTORIES': str(self.base),
            'GIT_CONFIG_GLOBAL': os.devnull,
            'GIT_CONFIG_NOSYSTEM': '1',
            'GIT_AUTHOR_NAME': 'Fixture',
            'GIT_AUTHOR_EMAIL': 'fixture@example.invalid',
            'GIT_COMMITTER_NAME': 'Fixture',
            'GIT_COMMITTER_EMAIL': 'fixture@example.invalid',
            'PYTHONPATH': str(FRAMEWORK),
            'PYTHONDONTWRITEBYTECODE': '1',
        })
        return environment

    def git(self, *arguments):
        return subprocess.run(
            ['git', *arguments], cwd=self.project, env=self.environment(),
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def commit(self):
        """One commit holding the whole project; its full hash."""
        self.git('init', '-q')
        self.git('add', '-A')
        self.git('-c', 'commit.gpgsign=false', 'commit', '-q', '-m', 'fixture')
        return self.git('rev-parse', 'HEAD')

    def export(self):
        """`machinome export --no-widget` run in the project, written
        outside it; the manifest's bytes and the command's stderr."""
        self.exports += 1
        output = self.base / 'exports' / f'export-{self.exports}'
        result = subprocess.run(
            [sys.executable, '-c', 'from machinome.cli import manage; manage()',
             'export', '--no-widget', '-o', str(output)],
            cwd=self.project, env=self.environment(),
            capture_output=True, text=True, timeout=300,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return (output / 'manifest.json').read_bytes(), result.stderr

    def source(self):
        manifest = json.loads(self.export()[0])
        self.assertIn('source', manifest)
        return manifest['source']

    def test_a_committed_project_records_its_revision(self):
        head = self.commit()
        self.assertRegex(head, r'^[0-9a-f]{40}$')

        manifest = json.loads(self.export()[0])

        self.assertEqual(manifest.get('source'),
                         {'revision': head, 'dirty': False})
        # Additive: the version is the one the content needs, and the
        # record is the last key, so every earlier byte is where it was.
        self.assertEqual(manifest['version'], 2)
        self.assertEqual(list(manifest)[-1], 'source')

    def test_a_modified_tracked_file_marks_the_record_dirty(self):
        head = self.commit()
        with open(self.project / 'design' / 'part.py', 'a') as part:
            part.write('# work in progress\n')

        self.assertEqual(self.source(), {'revision': head, 'dirty': True})

    def test_an_untracked_file_marks_the_record_dirty(self):
        head = self.commit()
        (self.project / 'notes.txt').write_text('not yet committed\n')

        self.assertEqual(self.source(), {'revision': head, 'dirty': True})

    def test_an_ignored_file_leaves_the_record_clean(self):
        head = self.commit()
        # The first export leaves its build directory and lock behind.
        self.assertEqual(self.source(), {'revision': head, 'dirty': False})
        self.assertTrue((self.project / '_build').is_dir())
        (self.project / 'snapshot.png').write_bytes(b'not a source')

        self.assertEqual(self.source(), {'revision': head, 'dirty': False})

    def test_an_export_outside_a_repository_is_unchanged_in_every_byte(self):
        written, stderr = self.export()

        self.assertNotIn('source', json.loads(written))
        self.assertEqual(written, PINNED.read_bytes())
        self.assertNotIn('WARNING', stderr)
        self.assertNotIn('git', stderr.lower())

    def test_a_repository_with_no_commit_is_unchanged_in_every_byte(self):
        self.git('init', '-q')

        written, stderr = self.export()

        self.assertNotIn('source', json.loads(written))
        self.assertEqual(written, PINNED.read_bytes())
        self.assertNotIn('WARNING', stderr)

    def test_no_git_records_nothing_and_says_nothing(self):
        from machinome.core.export import _source_record

        self.commit()
        empty = self.base / 'no-git-here'
        empty.mkdir()
        with patch.dict(os.environ, {'PATH': str(empty)}):
            with self.assertNoLogs(level='DEBUG'):
                self.assertIsNone(_source_record(str(self.project)))

    def test_the_record_writes_nothing_in_the_repository(self):
        """`git status` refreshes the index when it may; the record asks
        it not to, so an export leaves `.git` as it found it."""
        from machinome.core.export import _source_record

        self.commit()
        index = self.project / '.git' / 'index'
        # A stat-dirty but content-clean file: plain `git status` would
        # rewrite the index to record the new stat information.
        os.utime(self.project / 'design' / 'part.py')
        before = index.stat().st_mtime_ns, index.read_bytes()

        with patch.dict(os.environ, self.environment(), clear=True):
            record = _source_record(str(self.project))

        self.assertEqual(record['dirty'], False)
        self.assertEqual((index.stat().st_mtime_ns, index.read_bytes()),
                         before)
