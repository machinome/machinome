# Copyright (C) 2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+

"""The framework's symbolic value and its native, immutable graph. No
modelling backend or global arena.

`ExpressionNode` is one operation of a shared graph; `GraphValue` is the
value a project composes -- animation time, a driver read, a port value,
everything `machinome.math` returns for them -- a handle on one node. It
is the core's own type: it derives from no backend class, defines every
operator it supports, and refuses to be asked for its truth with
`SymbolicTruthError`. Its text, `str()`, is the core's compact closed
scalar (`machinome.core.expressions.scad_expression`), which is OpenSCAD's
scalar syntax and the standalone serialization alike.

A value SolidPython built (`solid2.get_animation_time()`, `scad_inline`,
text SolidPython's own operators produced) is recognised as an expression
only through the OpenSCAD engine, which adopts it as a graph node
(`machinome.scad_engine`, `machinome.openscad.engine`); without the
engine it is not an expression.

Values own their reachable operands. Identity hashing is intentional:
structural interning is the document compiler's job, and must never
recursively hash a DAG.
"""

from dataclasses import dataclass

from machinome import scad_engine as _seam


@dataclass(frozen=True, eq=False, slots=True, repr=False, weakref_slot=True)
class ExpressionNode:
    kind: str
    op: str = ''
    children: tuple = ()
    text: str = ''
    value: object = None

    def __repr__(self):
        detail = self.text if self.kind in ('name', 'num', 'raw') else self.op
        return f'<ExpressionNode {self.kind} {detail[:80]!r}>'


def postorder(roots):
    """Visit each reachable identity once, operands before their consumers."""
    seen = set()
    for root in roots:
        stack = [(root, False)]
        while stack:
            node, ready = stack.pop()
            if node in seen:
                continue
            if ready:
                seen.add(node)
                yield node
            else:
                stack.append((node, True))
                stack.extend((child, False) for child in reversed(node.children))


def free_names(node):
    return {item.text for item in postorder([node]) if item.kind == 'name'}


class SymbolicTruthError(Exception):
    """A symbolic value was asked for its truth.

    An `Exception` and deliberately not a `TypeError`, as SolidPython's
    refusal was: a framework `except TypeError` around a truth test must
    not turn this refusal into a silent branch.
    """

    def __init__(self, value):
        super().__init__(
            f'{value!r} is symbolic: its truth depends on animation time or '
            f'a driver, which have no value until they are bound, so it '
            f'cannot steer `if`, `and`, `or` or `not`. Compose it with '
            f'machinome.math instead (min, max, clamp, sign), or bind the '
            f'drivers first.')


#: The plain numbers, decided before any other test: the numeric face pays
#: one membership test and never consults the OpenSCAD engine.
_NUMBERS = frozenset((int, float))


def symbolic(value):
    """The graph node of `value` when it is symbolic, else None.

    A `GraphValue` is its node and an `ExpressionNode` itself; a plain
    `int` or `float` is never symbolic; anything else is symbolic only when
    the OpenSCAD engine resolves and adopts it (a value SolidPython built).
    """
    if value.__class__ in _NUMBERS:
        return None
    if isinstance(value, GraphValue):
        return value._expression_node
    if isinstance(value, ExpressionNode):
        return value
    engine = _seam.scad_engine()
    if engine is None:
        return None
    return engine.adopt(value)


def as_node(value):
    """`value` as a graph node: its own when it is symbolic, otherwise a
    number node of its text."""
    if isinstance(value, GraphValue):
        return value._expression_node
    node = symbolic(value)
    if node is None:
        return ExpressionNode('num', text=str(value))
    return node


class GraphValue:
    """A symbolic value: a handle on one immutable `ExpressionNode`.

    Arithmetic and comparison with a number or another symbolic value
    build a new node, in the written operand order; `**` is published as
    `^`. Unhashable (it defines `__eq__`), not iterable, and `+value` is a
    `TypeError`.
    """

    def __init__(self, node):
        self._expression_node = node
        self._evaluation_order = None

    @property
    def value(self):
        return str(self)

    def __str__(self):
        from machinome.core.expressions import scad_expression
        if any(node.kind == 'profile' for node in
               postorder([self._expression_node])):
            raise ValueError('profileOverlap is symbolic only in a running Bound')
        return scad_expression(self._expression_node)

    def __repr__(self):
        return repr(self._expression_node)

    def __bool__(self):
        raise SymbolicTruthError(self)

    def __float__(self):
        return float(self.evaluate({}))

    def evaluate(self, inputs):
        """Resolve a restored scalar with explicit inputs, never implicit time.

        Normal poses still rerun the author's law with numbers. This small
        iterative evaluator is for expression/operation round-trips only.
        """
        import math
        import operator
        from machinome import math as degree_math
        operators = {'+': operator.add, '-': operator.sub, '*': operator.mul,
                     '/': operator.truediv, '%': math.fmod, '^': operator.pow,
                     '<': operator.lt, '<=': operator.le, '>': operator.gt,
                     '>=': operator.ge, '==': operator.eq, '!=': operator.ne}
        # The DAG is immutable: only the input values change between calls.
        # Keep its order and child positions on this value, not in a
        # process-wide registry that would retain discarded machines.
        # Compile structure without evaluating an operation: an earlier
        # input/arithmetic error must still precede a later invalid node.
        if self._evaluation_order is None:
            ordered = tuple(postorder([self._expression_node]))
            positions = {node: index for index, node in enumerate(ordered)}
            self._evaluation_order = tuple(
                (node, tuple(positions[child] for child in node.children))
                for node in ordered)
        values = [None] * len(self._evaluation_order)
        for index, (node, children) in enumerate(self._evaluation_order):
            if node.kind == 'num':
                value = float(node.text)
            elif node.kind == 'profile':
                value = node.value
            elif node.kind == 'name':
                if node.text not in inputs:
                    raise ValueError(f'Unresolved motion input {node.text[:80]!r}')
                value = float(inputs[node.text])
            elif node.kind == 'binop':
                if len(children) == 2:
                    value = operators[node.op](values[children[0]],
                                               values[children[1]])
                else:
                    # Retain Python's original arity error for malformed
                    # graphs; supported binary nodes need no temporary list.
                    args = [values[child] for child in children]
                    value = operators[node.op](*args)
            elif node.kind == 'unary':
                args = [values[child] for child in children]
                value = -args[0] if node.op == '-' else +args[0]
            elif node.kind == 'call' and node.op in degree_math.SYMBOLIC_BUILTINS:
                args = [values[child] for child in children]
                # Every child is numeric. These are precisely the built-ins
                # used by the numeric faces of degree_math.min/max.
                if node.op == 'min':
                    value = (min(*args) if len(args) == 2
                             else degree_math.min(*args))
                elif node.op == 'max':
                    value = (max(*args) if len(args) == 2
                             else degree_math.max(*args))
                else:
                    value = getattr(degree_math, node.op)(*args)
            elif node.kind == 'call' and node.op == 'profileOverlap':
                from machinome.simulation.profile import _profile_call
                args = [values[child] for child in children]
                value = _profile_call(*args)
            else:
                raise ValueError(f'Cannot numerically resolve {node!r}')
            values[index] = value
        return values[-1]

    # Each operator builds its node directly: one call per operation.
    def __add__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '+', (self._expression_node, as_node(other))))

    def __sub__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '-', (self._expression_node, as_node(other))))

    def __mul__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '*', (self._expression_node, as_node(other))))

    def __truediv__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '/', (self._expression_node, as_node(other))))

    def __mod__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '%', (self._expression_node, as_node(other))))

    def __pow__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '^', (self._expression_node, as_node(other))))

    def __radd__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '+', (as_node(other), self._expression_node)))

    def __rsub__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '-', (as_node(other), self._expression_node)))

    def __rmul__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '*', (as_node(other), self._expression_node)))

    def __rtruediv__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '/', (as_node(other), self._expression_node)))

    def __rmod__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '%', (as_node(other), self._expression_node)))

    def __rpow__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '^', (as_node(other), self._expression_node)))

    def __lt__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '<', (self._expression_node, as_node(other))))

    def __le__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '<=', (self._expression_node, as_node(other))))

    def __gt__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '>', (self._expression_node, as_node(other))))

    def __ge__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '>=', (self._expression_node, as_node(other))))

    def __eq__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '==', (self._expression_node, as_node(other))))

    def __ne__(self, other):
        return GraphValue(ExpressionNode(
            'binop', '!=', (self._expression_node, as_node(other))))

    def __neg__(self):
        return GraphValue(ExpressionNode('unary', '-', (self._expression_node,)))

    def __abs__(self):
        return call('abs', self)


def call(name, *args):
    return GraphValue(ExpressionNode('call', name, tuple(as_node(x) for x in args)))


def symbol(name):
    return GraphValue(ExpressionNode('name', text=name))


def get_animation_time():
    return symbol('$t')


def depends_on_time(value):
    node = symbolic(value)
    if node is None:
        return False
    return any((item.kind == 'name' and item.text == '$t') or
               (item.kind == 'raw' and '$t' in item.text)
               for item in postorder([node]))


def scalar(value, graph=False):
    """A producer collects native roots; standalone callers get closed SCAD."""
    if graph:
        node = symbolic(value)
        if node is not None:
            return node
    return str(value)


def restore_scalar(value):
    if isinstance(value, str):
        from machinome.core.expressions import parse, ExpressionError
        try:
            node = parse(value)
        except ExpressionError:
            return GraphValue(ExpressionNode('raw', text=value))
        if node.kind == 'num':
            return value
        return GraphValue(node)
    return value
