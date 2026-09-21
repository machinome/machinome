# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: Apache-2.0

"""Conservative zero-motion certificates, never replacement bank arithmetic.

Finite binary constants are exact rationals here. A result certifies one affine
expression over u in [0, 1]; a kink inside that interval returns None and
its exact split, while unsupported operations cannot furnish a certificate.
In particular, a tiny nonzero slope is never zeroed.
"""

from fractions import Fraction

from machinome.expression_graph import postorder


def affine_piece(root, inputs, splits=None):
    """Return exact (constant, slope), or None when not proved affine."""
    found = {}
    zero = (Fraction(0), Fraction(0))
    for node in postorder([root]):
        result = None
        args = [found[child] for child in node.children]
        if node.kind == 'num':
            try:
                result = (Fraction(float(node.text)), zero[1])
            except (ValueError, OverflowError):
                pass
        elif node.kind == 'name':
            result = inputs.get(node.text)
        elif node.kind == 'unary' and node.op in ('+', '-') and args[0] is not None:
            result = tuple(-x for x in args[0]) if node.op == '-' else args[0]
        elif node.kind == 'binop':
            a, b = args
            if node.op == '*' and (a == zero or b == zero):
                result = zero
            elif a is not None and b is not None:
                if node.op == '+':
                    result = (a[0]+b[0], a[1]+b[1])
                elif node.op == '-':
                    result = (a[0]-b[0], a[1]-b[1])
                elif node.op == '*' and (not a[1] or not b[1]):
                    result = (a[0]*b[0], a[0]*b[1]+a[1]*b[0])
                elif node.op == '/' and not b[1] and b[0]:
                    result = (a[0]/b[0], a[1]/b[0])
        elif node.kind == 'call' and all(a is not None for a in args):
            if node.op == 'abs':
                a = args[0]
                if a[0] >= 0 and a[0]+a[1] >= 0:
                    result = a
                elif a[0] <= 0 and a[0]+a[1] <= 0:
                    result = (-a[0], -a[1])
                elif splits is not None:
                    splits.append(-a[0]/a[1])
            elif node.op in ('min', 'max'):
                a, b = args
                diff = (a[0]-b[0], a[0]+a[1]-b[0]-b[1])
                if min(diff) >= 0:
                    result = a if node.op == 'max' else b
                elif max(diff) <= 0:
                    result = b if node.op == 'max' else a
                elif splits is not None:
                    splits.append(-diff[0]/(diff[1]-diff[0]))
        found[node] = result
    return found[root]


def constant_contact(skeleton, level, values, delta, own, own_value, width,
                     max_pieces=1024):
    """Prove that composing the driven increment into its level has slope 0."""
    try:
        span = Fraction(width)
        inputs = {name: (Fraction(value), Fraction(delta.get(name, 0))*span)
                  for name, value in values.items()}
        origin = affine_piece(skeleton, {n: (v[0], Fraction(0))
                                         for n, v in inputs.items()})
        if origin is None:
            return False
        pending = [(Fraction(0), Fraction(1))]
        for _ in range(max_pieces):
            if not pending:
                return True
            left, right = pending.pop()
            local = {n: (v[0]+v[1]*left, v[1]*(right-left))
                     for n, v in inputs.items()}
            splits = []
            path = affine_piece(skeleton, local, splits)
            contact = None
            if path is not None:
                local[own] = (Fraction(own_value)+path[0]-origin[0], path[1])
                contact = affine_piece(level, local, splits)
                if contact is not None:
                    if contact[1] != 0:
                        return False
                    continue
            if not splits:
                return False
            # Split only at an exact selection crossing proved above. This is
            # not more point sampling and introduces no tolerance. A bounded
            # proof that runs out of work falls back to the ordinary executor.
            middle = left+(right-left)*splits[0]
            if not left < middle < right:
                return False
            pending.extend(((middle, right), (left, middle)))
        return False
    except (ValueError, OverflowError):
        # Non-finite input is not a certificate. The ordinary executor retains
        # its existing named refusal/validation rather than a proof error.
        return False
