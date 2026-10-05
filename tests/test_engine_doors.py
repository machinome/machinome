# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The three doors of each engine (OpenSpec change `brep-mesh`, design.md
Decision 15 item 3, and Decision 13's texts, written out here verbatim).

Each engine refuses its absence at three doors, each with one actionable
error naming the extra that installs it: the provider's own import (R5,
R6), the seam asked at a point of use (R1, R3), and the command that needs
it (the B-rep engine's command door is its point of use, a stale B-rep
fusion's build; the mesh engine's is `machinome test --mesh`, at its start,
before building). The workspace and CI install every kernel, so an install
without one is stood in for by the `sys.meta_path` finders of
`tests/brep_engine_absent.py` and `tests/mesh_engine_absent.py`.
"""

import glob
import json
import os
import shutil
import tempfile
from unittest import TestCase

from . import brep_engine_absent as brep_absent
from . import mesh_engine_absent as mesh_absent

FUSION = 'tests/meta_project/exact_fusion_current.py:PinnedHub'

R1 = ('{needed_by} requires the B-rep engine because {reason}; install it '
      'with \'pip install "machinome[brep]"\'. A model with no B-rep node '
      'never needs it')
R3 = ('{needed_by} requires the mesh engine because {reason}; install it '
      'with \'pip install "machinome[mesh]"\'. B-rep geometry does not need '
      'it: a model whose every compared part has B-rep geometry is decided '
      'by the B-rep engine')
R5 = ('the B-rep engine (machinome.engine.brep) needs OCP, which is not '
      'installed; install it with \'pip install "machinome[brep]"\'')
R6 = ('the mesh engine (machinome.engine.mesh) needs manifold3d, which is '
      'not installed; install it with \'pip install "machinome[mesh]"\'')

#: Import the provider, then ask the seam and require it, and report all
#: three as JSON on the last line.
DOORS = '''
import importlib, json
report = {{}}
try:
    importlib.import_module({provider!r})
except ImportError as raised:
    report['imported'] = [type(raised).__name__, getattr(raised, 'extra', None),
                          str(raised)]
else:
    report['imported'] = None
try:
    import machinome.engine as seam
    report['asked'] = repr(seam.{ask}())
    getattr(seam, {require!r})({needed_by!r}, {reason!r})
except Exception as raised:
    report['required'] = f'{{type(raised).__name__}}: {{raised}}'
else:
    report['required'] = None
print(json.dumps(report))
'''


def last_json(run):
    lines = run.stdout.strip().splitlines()
    assert lines, run.output
    return json.loads(lines[-1])


class TheBrepEngineDoorsTest(TestCase):

    def test_the_provider_the_seam_and_the_point_of_use_refuse(self):
        run = brep_absent.run_python(DOORS.format(
            provider='machinome.engine.brep', ask='brep_engine',
            require='require_brep_engine', needed_by='B-rep fusion Bracket',
            reason='fusing its B-rep children'), absent=('OCP',))
        report = last_json(run)

        self.assertEqual(report['imported'], ['ExtraUnavailable', 'brep', R5],
                         run.output)
        self.assertEqual(report['asked'], 'None')
        self.assertEqual(report['required'], 'BrepEngineUnavailable: ' + R1.format(
            needed_by='B-rep fusion Bracket',
            reason='fusing its B-rep children'))

    def test_the_memos_and_publication_name_their_needs(self):
        run = brep_absent.run_python(
            'import json\n'
            'from machinome import brep_artifacts, brep_cache\n'
            'report = []\n'
            'for call in (lambda: brep_artifacts.write_brep(None, "p.brep", 0),\n'
            '             lambda: brep_cache._engine("it is asked")):\n'
            '    try:\n'
            '        call()\n'
            '    except Exception as raised:\n'
            '        report.append(str(raised))\n'
            'print(json.dumps(report))\n', absent=('OCP',))
        report = last_json(run)

        self.assertEqual(report, [
            R1.format(needed_by='writing p.brep',
                      reason="it is a B-rep node's BREP artifact"),
            R1.format(needed_by='reading B-rep geometry',
                      reason='it is asked')], run.output)

    def test_a_stale_brep_fusion_refuses_at_its_build(self):
        build_dir = tempfile.mkdtemp(prefix='brep-door-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)
        for _ in range(2):
            settled = brep_absent.run_machinome('build', FUSION, blocked=False,
                                                build_dir=build_dir)
            self.assertEqual(settled.returncode, 0, settled.output)
        fused = [path for path in glob.glob(
            os.path.join(build_dir, '**', '*'), recursive=True)
            if os.path.basename(path).startswith(
                'exact_fusion_current-PinnedHub-')]
        self.assertTrue(fused)
        for path in fused:
            os.remove(path)

        run = brep_absent.run_machinome(
            'build', FUSION, build_dir=build_dir,
            absent=('machinome.engine.brep',))

        self.assertNotEqual(run.returncode, 0, run.output)
        self.assertIn(R1.format(needed_by='B-rep fusion PinnedHub',
                                reason='writing its fused B-rep artifacts'),
                      run.output)


class TheMeshEngineDoorsTest(TestCase):

    def test_the_provider_and_the_seam_refuse(self):
        run = mesh_absent.run_python(DOORS.format(
            provider='machinome.engine.mesh', ask='mesh_engine',
            require='require_mesh_engine',
            needed_by='mesh fusion Fused',
            reason="directly unioning its children's mesh artifacts"),
            absent=('manifold3d',))
        report = last_json(run)

        self.assertEqual(report['imported'], ['ExtraUnavailable', 'mesh', R6],
                         run.output)
        self.assertEqual(report['asked'], 'None')
        self.assertEqual(report['required'], 'MeshEngineUnavailable: ' + R3.format(
            needed_by='mesh fusion Fused',
            reason="directly unioning its children's mesh artifacts"))

    def test_a_mesh_run_refuses_at_its_start_before_building(self):
        build_dir = tempfile.mkdtemp(prefix='mesh-door-')
        self.addCleanup(shutil.rmtree, build_dir, ignore_errors=True)

        run = mesh_absent.run_machinome(
            'test', '--mesh', 'tests/meta_project/flush.py',
            build_dir=build_dir, absent=('manifold3d',))

        self.assertEqual(run.returncode, 1, run.output)
        self.assertIn('Error: ' + R3.format(
            needed_by='machinome test on the mesh engine',
            reason="every pair the run compares is compared on the parts' "
                   'meshes'), run.stderr.splitlines(), run.output)
        self.assertEqual(glob.glob(os.path.join(build_dir, '**', '*.stl'),
                                   recursive=True), [])
