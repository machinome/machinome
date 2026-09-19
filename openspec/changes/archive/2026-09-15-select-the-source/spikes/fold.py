"""Spike 3: is the SWITCHED-SOURCE test computable off the compiled plan?

Prints, for every relation of the reduced fixture, its graph, its
skeleton and its jump nodes with their level quantities -- then folds the
skeleton with a chosen set of placeholders set to ZERO (`x*0 -> 0`,
`0+y -> y`, ...) and reports which coordinates the edge STILL reads on
such a piece, following a surviving placeholder into its own level.

Nothing in the worktree is touched: this drives `_law_graphs`,
`_skeleton` and `_plan_of` directly.
"""

from solid_node.expression_graph import ExpressionNode, free_names, postorder
from solid_node.scad_expression import as_node, symbol, GraphValue
from solid_node.simulation import program as P
from reduced import ShiftedCarry


def _fold(root, zero):
    """`root` with every placeholder in `zero` set to 0 and the result
    folded: 0*x -> 0, x*0 -> 0, 0+y -> y, y+0 -> y, 0-y -> -y, y-0 -> y,
    0/x -> 0."""
    ZERO = ExpressionNode('num', text='0')

    def is_zero(node):
        return node.kind == 'num' and float(node.text) == 0.0

    replaced = {}
    for node in postorder([root]):
        if node.kind == 'name' and node.text in zero:
            replaced[node] = ZERO
            continue
        if not node.children:
            continue
        children = tuple(replaced.get(child, child) for child in node.children)
        if node.kind == 'binop' and node.op == '*' and any(map(is_zero, children)):
            replaced[node] = ZERO
        elif node.kind == 'binop' and node.op == '/' and is_zero(children[0]):
            replaced[node] = ZERO
        elif node.kind == 'binop' and node.op == '+' and is_zero(children[0]):
            replaced[node] = children[1]
        elif node.kind == 'binop' and node.op in ('+', '-') and is_zero(children[1]):
            replaced[node] = children[0]
        elif node.kind == 'binop' and node.op == '-' and is_zero(children[0]):
            replaced[node] = ExpressionNode('unary', '-', (children[1],))
        elif children != node.children:
            replaced[node] = ExpressionNode(node.kind, node.op, children,
                                            node.text)
    return replaced.get(root, root)


def reads(skeleton, jumps, zero):
    """Every coordinate the edge still reads with `zero`'s placeholders
    at branch 0: the folded skeleton's free names, following any
    surviving placeholder into its own level quantity, transitively."""
    by_name = {jump.placeholder: jump for jump in jumps}
    seen, pending, found = set(), list(free_names(_fold(skeleton, zero))), set()
    while pending:
        name = pending.pop()
        if name in seen:
            continue
        seen.add(name)
        jump = by_name.get(name)
        if jump is None:
            found.add(name)
            continue
        pending.extend(free_names(as_node(_fold(as_node(jump.argument), zero))))
    return found


root = ShiftedCarry()
for assembly, path, records, formulas, wirings in P._units(root):
    for record in records:
        record.direction = 'forward'
        names = [P._qualified(root, end)[0] for end in record.driver_ends]
        targets = [P._qualified(root, end)[0] for end in record.driven_ends]
        tokens = [symbol(name) for name in names]
        value = record.law.forward(*tokens)
        graph, plan = P._graph_of(value, lambda d: (_ for _ in ()).throw(
            RuntimeError(d)))
        print(f'=== {names} -> {targets} ===')
        print(f'  graph    : {graph}')
        if plan is None:
            print('  no jumps')
            continue
        print(f'  skeleton : {plan.skeleton}')
        for jump in plan.jumps:
            print(f'    {jump.placeholder}: {jump.primitive} on '
                  f'{jump.argument}  affine={jump.affine}  '
                  f'level reads {sorted(free_names(as_node(jump.argument)))}')
        print(f'  reads with nothing folded: '
              f'{sorted(reads(as_node(plan.skeleton), plan.jumps, set()))}')
        for jump in plan.jumps:
            got = sorted(reads(as_node(plan.skeleton), plan.jumps,
                               {jump.placeholder}))
            print(f'  reads with {jump.placeholder}=0: {got}')
