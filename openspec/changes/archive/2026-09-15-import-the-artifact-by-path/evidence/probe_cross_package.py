# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Measure how a parent spells the import of a leaf declared in another
package, for every leaf kind, over two builds.

Writes a throwaway project outside the repository, builds each declared
model TWICE with the real `solid build`, and prints, for every generated
`.scad`, each `import(file = ...)` it holds and whether that path exists
relative to the directory holding the `.scad` -- which is how OpenSCAD
resolves it.

    PYTHONPATH=$PWD python openspec/changes/import-the-artifact-by-path/\\
        evidence/probe_cross_package.py /tmp/probe-dir

The generated `.scad` files are copied next to this script under
`generated/` when a second argument `--save <dir>` is given.
"""

import os
import shutil
import subprocess
import sys

PARTS = '''\
"""Three leaves, one per kind, and a fourth that imports a file of its
own -- all declared in package `sim`."""
import cadquery
from molejo import Circle, Helix, P, Shape
from solid2 import cube, cylinder, import_stl

from solid_node.node import CadQueryNode, MolejoNode, Solid2Node
from solid_node.motion.ports import TranslationalPort


class RigidLeaf(Solid2Node):
    def render(self):
        return cube(10, 10, 10)


class ExactLeaf(CadQueryNode):
    def render(self):
        return cadquery.Workplane('XY').box(8, 8, 8)


class FlexLeaf(MolejoNode):
    height = TranslationalPort(unit='mm')

    def render(self):
        return Shape(
            profile=Circle(radius=1.0),
            path=[Helix(radius=5.0, turns=3.0, height=P.height)],
            path_samples=60,
            profile_samples=8,
        )


class UnoptimizedLeaf(Solid2Node):
    """A rigid leaf that declines the STL-import optimization."""
    optimize = False

    def render(self):
        return cylinder(r=4, h=12)
'''

BENCH = '''\
"""An assembly in package `sim.tools` placing leaves declared in `sim`."""
from solid_node.node import AssemblyNode

from ..parts import ExactLeaf, FlexLeaf, RigidLeaf, UnoptimizedLeaf


class Bench(AssemblyNode):

    def render(self):
        flex = FlexLeaf()
        flex.height = 30.0
        return [
            RigidLeaf(),
            ExactLeaf().translate([20, 0, 0]),
            flex.translate([40, 0, 0]),
        ]


class UnoptBench(AssemblyNode):
    """Cross-package parent of a leaf that declines optimization."""

    def render(self):
        return [UnoptimizedLeaf()]
'''

SAMEBENCH = '''\
"""The control: a parent in the SAME package as the leaves."""
from solid_node.node import AssemblyNode

from .parts import ExactLeaf, FlexLeaf, RigidLeaf


class SameBench(AssemblyNode):

    def render(self):
        flex = FlexLeaf()
        flex.height = 30.0
        return [RigidLeaf(), ExactLeaf(), flex]
'''

GROUP = '''\
"""An intermediate assembly, three packages away from the root."""
from solid_node.node import AssemblyNode

from ...parts import RigidLeaf


class Group(AssemblyNode):
    def render(self):
        return [RigidLeaf()]
'''

DEEP_BENCH = '''\
"""A root in `sim.tools` over an intermediate assembly in `sim.sub.deep`."""
from solid_node.node import AssemblyNode

from ..sub.deep.group import Group


class DeepBench(AssemblyNode):
    def render(self):
        return [Group()]
'''

MANIFEST = '''\
[tool.solid-node.models]
bench = "sim.tools.bench:Bench"
unopt = "sim.tools.bench:UnoptBench"
same = "sim.samebench:SameBench"
deep = "sim.tools.deep_bench:DeepBench"
'''


def write_project(root):
    for package in ('sim', 'sim/tools', 'sim/sub', 'sim/sub/deep'):
        os.makedirs(os.path.join(root, package), exist_ok=True)
        open(os.path.join(root, package, '__init__.py'), 'w').close()
    files = {
        'pyproject.toml': MANIFEST,
        'sim/parts.py': PARTS,
        'sim/tools/bench.py': BENCH,
        'sim/samebench.py': SAMEBENCH,
        'sim/sub/deep/group.py': GROUP,
        'sim/tools/deep_bench.py': DEEP_BENCH,
    }
    for name, content in files.items():
        with open(os.path.join(root, name), 'w') as handle:
            handle.write(content)


def build(root, model):
    env = dict(os.environ)
    env['PYTHONPATH'] = os.pathsep.join(
        [p for p in (env.get('PYTHONPATH'), root) if p])
    solid = os.path.join(os.path.dirname(sys.executable), 'solid')
    result = subprocess.run([solid, 'build', model], cwd=root, env=env,
                            capture_output=True, text=True)
    if result.returncode:
        print(result.stdout[-3000:])
        print(result.stderr[-3000:])
        raise SystemExit(f'build {model} failed')


def report(root, label):
    print(f'\n######## {label}')
    for directory, _, names in sorted(os.walk(os.path.join(root, '_build'))):
        for name in sorted(names):
            if not name.endswith('.scad'):
                continue
            path = os.path.join(directory, name)
            with open(path) as handle:
                text = handle.read()
            print(f'\n=== {os.path.relpath(path, root)}')
            print(text.rstrip())
            for line in text.splitlines():
                if 'import(file = ' not in line:
                    continue
                imported = line.split('import(file = "')[1].split('"')[0]
                exists = os.path.exists(os.path.join(directory, imported))
                print(f'    {"OK  " if exists else "MISS"} {imported}')


def main():
    root = os.path.abspath(sys.argv[1])
    if os.path.exists(root):
        shutil.rmtree(root)
    os.makedirs(root)
    write_project(root)
    models = ['bench', 'unopt', 'same', 'deep']
    for pass_number in (1, 2):
        for model in models:
            build(root, model)
        report(root, f'after build pass {pass_number}')
    if '--save' in sys.argv:
        target = sys.argv[sys.argv.index('--save') + 1]
        os.makedirs(target, exist_ok=True)
        for directory, _, names in os.walk(os.path.join(root, '_build')):
            for name in names:
                if name.endswith('.scad'):
                    relative = os.path.relpath(
                        os.path.join(directory, name),
                        os.path.join(root, '_build'))
                    destination = os.path.join(target, relative)
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    shutil.copy(os.path.join(directory, name), destination)


if __name__ == '__main__':
    main()
