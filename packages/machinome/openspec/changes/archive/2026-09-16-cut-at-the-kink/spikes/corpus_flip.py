import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classify import shape_of
from solid_node.scad_expression import as_node
from solid_node.simulation import Sim
from tests.running_project import machine as machines
from tests.carriage_project import machine as carriage

names = sorted({e['name'] for e in json.load(open('tests/running-corpus.json'))['machines']})
for name in names:
    cls = getattr(machines, name, None) or getattr(carriage, name)
    sim = Sim(cls(), 0.1)
    flips, levels = [], []
    for edge in sim.program.edges:
        members = [edge]
        if edge.kind == 'block' and edge.block is not None:
            members = list(edge.block.members)
        for member in members:
            for index, graph in enumerate(member.graphs):
                plan = member.plans[index] if member.plans else None
                root = as_node(plan.skeleton) if plan is not None else (
                    as_node(graph) if graph is not None else None)
                if root is not None and shape_of(root) == 'kinked':
                    flips.append(f'{member.description} [{member.gives[index]}]')
                for jump in (plan.jumps if plan is not None else ()):
                    if not jump.affine and shape_of(as_node(jump.argument)) == 'kinked':
                        levels.append(f'{member.description}: {jump.primitive}')
    if flips or levels:
        print(f'{name}:')
        for one in flips:
            print(f'   skeleton/graph now kinked: {one}')
        for one in levels:
            print(f'   jump level now kinked:     {one}')
