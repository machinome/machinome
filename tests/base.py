# Machinome - A framework for mechanical CAD projects
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

import re
import os
import shutil
from unittest import TestCase
from machinome.node import StlRenderStart
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
    import machinome.simulation.program as program_module

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

    `evaluate-only-what-moves` gives a followed quantity a SECOND way to
    be asked for its value at one point: `_PathValue.bind` (a piece's
    first point) and `_PathValue.at` (every later point of it). Both are
    counted here as ONE evaluation each, exactly as a whole-graph
    `GraphValue.evaluate` call was counted before this cycle -- so the
    evaluation COUNT a probe reports is unmoved (`Clearing`'s 98.6,
    `CurtaInterface`'s 602.6 per tick, design.md section 10) even though
    what falls is the cost INSIDE one evaluation, which
    `graph_node_visits` below is the probe that can see.
    """
    from machinome.scad_expression import GraphValue
    import machinome.simulation.program as program_module

    original_evaluate = GraphValue.evaluate
    original_bind = program_module._PathValue.bind
    original_at = program_module._PathValue.at
    counted = [0]

    def counting_evaluate(self, inputs):
        counted[0] += 1
        return original_evaluate(self, inputs)

    def counting_bind(self, values):
        counted[0] += 1
        return original_bind(self, values)

    def counting_at(self, values):
        counted[0] += 1
        return original_at(self, values)

    GraphValue.evaluate = counting_evaluate
    program_module._PathValue.bind = counting_bind
    program_module._PathValue.at = counting_at
    try:
        sim.run(sim.dt * ticks)
    finally:
        GraphValue.evaluate = original_evaluate
        program_module._PathValue.bind = original_bind
        program_module._PathValue.at = original_at
    return counted[0]


def graph_node_visits(sim, ticks):
    """The postorder STEPS a run charges over `ticks` -- the unit
    `evaluate-only-what-moves` actually reduces.

    Once a path value amortises most of a graph's nodes over its many
    points, `expression_evaluations`'s COUNT can no longer tell a cheap
    evaluation from an expensive one: a searched crossing is still one
    evaluation per sample, whether that evaluation walks the whole graph
    or only the dozen nodes that move. This probe counts what actually
    happened underneath: every node a full walk visits --
    `GraphValue.evaluate`'s own postorder walk, and `_PathValue.bind`'s,
    which walks the same way the first time a piece is bound -- plus
    every node a bound `_PathValue.at` visits, reported through
    `program_module._visited` because a fast walk never calls
    `postorder` at all.
    """
    import machinome.expression_graph as expression_graph_module
    import machinome.simulation.program as program_module

    original_postorder = expression_graph_module.postorder
    original_visited = program_module._visited
    counted = [0]

    def counting_postorder(roots):
        for node in original_postorder(roots):
            counted[0] += 1
            yield node

    def counting_visited(count):
        counted[0] += count

    expression_graph_module.postorder = counting_postorder
    program_module.postorder = counting_postorder
    program_module._visited = counting_visited
    try:
        sim.run(sim.dt * ticks)
    finally:
        expression_graph_module.postorder = original_postorder
        program_module.postorder = original_postorder
        program_module._visited = original_visited
    return counted[0]
