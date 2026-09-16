# Solid Node - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import re
import os
import shutil
from unittest import TestCase
from solid_node.node import StlRenderStart
from .utils import format_codes


BASEDIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASEDIR, '_build')

os.environ['SOLID_BUILD_DIR'] = BUILD_DIR

def _forget_assembly(node):
    node._assembled = False
    for child in node.children:
        _forget_assembly(child)


class BaseNodeTest(TestCase):

    def setUp(self):
        if os.path.exists(BUILD_DIR):
            shutil.rmtree(BUILD_DIR)
        self.basedir = BASEDIR
        self.build_dir = BUILD_DIR
        self.preserve_result = None

    def tearDown(self):
        if not os.path.exists(BUILD_DIR):
            return
        if not self.preserve_result:
            shutil.rmtree(BUILD_DIR)
            return
        dirs = BUILD_DIR.split('/')
        dirs[-1] = f'_build_{self.preserve_result}'
        new_dir = '/'.join(dirs)
        if os.path.exists(new_dir):
            shutil.rmtree(new_dir)
        os.rename(BUILD_DIR, new_dir)

    def get_scad(self, NodeClass, *args, **kwargs):
        solid = NodeClass(*args, **kwargs)
        solid.assemble()
        return solid.scad_code.strip()

    def load_solid(self, index, stl_level=0):
        self.solid = self.models[index]()
        self.solid.assemble()

        if not stl_level:
            return self.solid

        for _ in range(stl_level):
            try:
                self.solid.trigger_stl()
            except StlRenderStart as job:
                job.wait()

        # Re-assemble the same tree. An assembly keeps its rest render,
        # so the children are the same instances and each must forget
        # its memoized assembly too, or the leaves would answer from
        # memory instead of importing the STLs just built.
        _forget_assembly(self.solid)
        self.solid.assemble()

        return self.solid

    def assertCode(self, code):
        scad_code, code = format_codes(self.solid.scad_code, code)

        expected = re.sub(r'\s+', ' ', code.strip())
        generated = re.sub(r'\s+', ' ', scad_code.strip())

        if expected == generated:
            return

        print('EXPECTED:')
        print(code.strip())
        print('GOT:')
        print(scad_code.strip())

        # Compare the full token sequences (not just as far as the
        # shorter one reaches): a strict-prefix generated used to pass
        # silently here, and a shorter expected used to raise a raw
        # IndexError instead of a clean assertion failure.
        self.assertEqual(generated.split(), expected.split())



def preserve(test):
    def new_test(self, *args):
        self.preserve_result = test.__qualname__
        test(self, *args)

    return new_test


def graph_evaluations(sim, ticks):
    """How many times a compiled graph is evaluated over `ticks` of
    `sim` -- the run's own cost, counted where the run computes it.

    Shared because it is the probe that says whether a followed quantity
    was SOLVED or SEARCHED: a solve is a handful of evaluations and a
    search is one per sub-interval plus the bisection behind each
    bracket.
    """
    import solid_node.simulation.program as program_module

    original = program_module._evaluated
    counted = [0]

    def counting(graph, inputs):
        counted[0] += 1
        return original(graph, inputs)

    program_module._evaluated = counting
    try:
        sim.run(sim.dt * ticks)
    finally:
        program_module._evaluated = original
    return counted[0]


def expression_evaluations(sim, ticks):
    """How many times an EXPRESSION GRAPH is evaluated over `ticks` --
    `GraphValue.evaluate`, which is every skeleton and every jump level a
    partition, a walk or a search asks for, and not only the whole-law
    evaluations `graph_evaluations` sees.

    It is the probe the `cut-at-the-kink` proposal's 2 861.3 per tick was
    measured with (`openspec/changes/.../spikes/kink_baseline.py`), and
    the only one that can see a self-read walk's cost at all: a law with
    a jump plan never reaches `_evaluated`.
    """
    from solid_node.scad_expression import GraphValue

    original = GraphValue.evaluate
    counted = [0]

    def counting(self, inputs):
        counted[0] += 1
        return original(self, inputs)

    GraphValue.evaluate = counting
    try:
        sim.run(sim.dt * ticks)
    finally:
        GraphValue.evaluate = original
    return counted[0]
