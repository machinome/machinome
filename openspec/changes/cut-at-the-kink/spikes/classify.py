"""How many skeletons and jump levels of a real program are AFFINE,
KINKED (piecewise affine over min/max/abs), or genuinely curved."""
import os, sys
ROOT = os.environ['WT']
sys.path.insert(0, ROOT)

from solid_node.expression_graph import postorder
from solid_node.scad_expression import as_node
import solid_node.simulation.program as P

KINKS = ('min', 'max', 'abs')


def shape_of(root):
    """'constant' | 'affine' | 'kinked' | None."""
    degree = {}
    for node in postorder([root]):
        degree[node] = _degree(node, degree)
    return degree[root]


def _degree(node, degree):
    if node.kind == 'num':
        return 'constant'
    if node.kind == 'name':
        return 'constant' if node.text.startswith('$') else 'affine'
    if not node.children:
        return None
    children = [degree[c] for c in node.children]
    if all(c == 'constant' for c in children):
        return 'constant'
    moving = ('constant', 'affine', 'kinked')
    def joined(*parts):
        return 'kinked' if 'kinked' in parts else 'affine'
    if node.kind == 'call':
        if node.op in KINKS and all(c in moving for c in children):
            return 'kinked'
        return None
    if node.kind == 'unary':
        return children[0] if children[0] in ('affine', 'kinked') else None
    if node.kind != 'binop':
        return None
    left, right = children
    if node.op in ('+', '-'):
        return joined(left, right) if left in moving and right in moving else None
    if node.op == '*':
        if left == 'constant' and right in moving:
            return joined(right)
        if right == 'constant' and left in moving:
            return joined(left)
        return None
    if node.op == '/':
        return joined(left) if right == 'constant' and left in moving else None
    return None


def report(name, program):
    tally = {}
    def note(what, shape):
        tally[(what, shape)] = tally.get((what, shape), 0) + 1
    for edge in program.edges:
        members = [edge]
        if edge.kind == 'block' and edge.block is not None:
            members = list(edge.block.members)
        for member in members:
            plans = getattr(member, 'plans', ())
            graphs = getattr(member, 'graphs', ())
            for index, graph in enumerate(graphs):
                plan = plans[index] if plans else None
                if plan is None:
                    if graph is None:
                        continue
                    note('law without a plan', shape_of(as_node(graph)))
                    continue
                note('skeleton', shape_of(as_node(plan.skeleton)))
                for jump in plan.jumps:
                    note('jump level', shape_of(as_node(jump.argument)))
    print(f'--- {name}')
    for key in sorted(tally, key=lambda k: (k[0], str(k[1]))):
        print(f'   {key[0]:20s} {str(key[1]):10s} {tally[key]}')


def blame(root):
    """The lowest nodes that make `root` unclassifiable."""
    degree = {}
    order = list(postorder([root]))
    for node in order:
        degree[node] = _degree(node, degree)
    found = []
    for node in order:
        if degree[node] is not None:
            continue
        if all(degree[c] is not None for c in node.children):
            found.append(f'{node.kind}:{node.op}')
    return found


def blame_report(name, program):
    from collections import Counter
    tally = Counter()
    for edge in program.edges:
        members = [edge]
        if edge.kind == 'block' and edge.block is not None:
            members = list(edge.block.members)
        for member in members:
            plans = getattr(member, 'plans', ())
            for index, plan in enumerate(plans or ()):
                if plan is None:
                    continue
                root = as_node(plan.skeleton)
                if shape_of(root) is None:
                    tally.update(blame(root))
    print(f'--- blame {name}')
    for op, count in tally.most_common():
        print(f'   {op:20s} {count}')
