# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The framework works without the mechanics helpers.

The helpers are the repository's distribution machinome-mechanics, the
package `machinome.mechanics` beneath the core's own (change
`join-mechanics`): the core admits that portion and never imports it, so the
guard below refuses the dotted address as well as the two former top-level
names.
"""

from importlib.machinery import PathFinder
from pathlib import Path
import subprocess
import sys
import tomllib
from unittest import TestCase

import machinome


ROOT = Path(__file__).resolve().parents[1]

#: A meta-path finder that refuses the helpers: their address
#: `machinome.mechanics` and every name beneath it, and the former top-level
#: names `machinome_mechanics` and `machinome_mechanisms`.
GUARD = """
import importlib.abc
import sys

class RefuseHelpers(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if (fullname.split('.')[0] in {'machinome_mechanics',
                                       'machinome_mechanisms'}
                or fullname == 'machinome.mechanics'
                or fullname.startswith('machinome.mechanics.')):
            raise AssertionError('framework imported helpers: ' + fullname)

sys.meta_path.insert(0, RefuseHelpers())
"""


class MechanicsBoundaryTest(TestCase):
    def test_old_package_is_not_available(self):
        # Inspect the selected framework package. A development environment may
        # also register a PEP 660 finder for another, older framework checkout.
        self.assertIsNone(
            PathFinder.find_spec("machinome.mechanisms", machinome.__path__)
        )

    def test_only_the_mechanics_extra_installs_helpers(self):
        project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
        dependencies = list(project["dependencies"])
        extras = project.get("optional-dependencies", {})
        self.assertEqual(extras.get("mechanics"),
                         [f"machinome-mechanics~={project['version']}"])
        for name, extra in extras.items():
            if name != "mechanics":
                dependencies.extend(extra)
        for dependency in dependencies:
            self.assertNotIn("machinome-mechanics", dependency.lower().replace("_", "-"))
            self.assertNotIn("machinome-mechanisms", dependency.lower().replace("_", "-"))

    def test_math_and_motion_work_with_helpers_refused(self):
        probe = GUARD + """
from machinome.math import sin
from machinome.motion.couplings import Affine
from machinome.motion.joints import Revolute, Prismatic
from machinome.node.assembly import AssemblyNode
assert sin(90) == 1
assert Affine(2, 3).inverse(11) == 4
assert Revolute(axis=(0, 0, 1)).coordinate is not None
assert Prismatic(axis=(0, 0, 1)).coordinate is not None
"""
        result = subprocess.run(
            [sys.executable, "-c", probe], cwd=ROOT,
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_the_guard_refuses_the_helpers_address(self):
        # The positive control: the guard watches the dotted name, so the
        # helpers' own address is refused, not only the former top-level names.
        result = subprocess.run(
            [sys.executable, "-c", GUARD + "import machinome.mechanics\n"],
            cwd=ROOT, text=True, capture_output=True,
        )
        output = result.stdout + result.stderr
        self.assertEqual(result.returncode, 1, output)
        self.assertIn("framework imported helpers: machinome.mechanics", output)
