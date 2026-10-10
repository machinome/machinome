"""Spike 5: how a member edge's `increments` is called over a PIECE of the
stretch, and what the crossing fractions come back in.

A block runs its members piece by piece. `Edge.increments(values, deltas)`
takes ABSOLUTE values at the piece's left end and the increments over the
piece, so the block's job per piece is:

    values[k] = v0[k] + D[k] * a   for a coordinate the block does NOT give
    values[k] = whatever the block advanced it to                (in-block)
    deltas[k] = D[k] * (b - a)     for a coordinate the block does NOT give
    deltas[k] = the in-block increment computed on THIS piece     (in-block)

and to rescale every reported crossing from the piece's fraction to the
stretch's, `a + t * (b - a)` -- the same map `run._record` then applies
from the segment to the tick.
"""

import json

from solid_node.simulation import Sim
from reduced import FixedZero

sim = Sim(FixedZero(), dt=.02)
program = sim._run.program
keys = program.keys
edges = {edge.description: edge for edge in program.edges}
carry = next(edge for edge in program.edges
             if 'carry.travel' in edge.description.split(' drives ')[1])
print('edge under test:', carry.description)
print('  needs', [program.nodes[k].name for k in carry.needs],
      'gives', [program.nodes[k].name for k in carry.gives])

v0 = program.values_of(dict(sim.state))
# lower.turn sweeps 0 -> 2 over the stretch; carry.travel holds at 0 and is
# gated by `carry.travel < 1`, which the walk cuts at.
D = {key: 0.0 for key in program.nodes}
D[keys['lower.turn']] = 2.0

KEY = None  # set below


def over(a, b, values, own=None):
    """`values` are the stretch's own start values; `own` overrides the
    IN-BLOCK coordinate with what the block advanced it to."""
    piece_values = {key: values[key] + D[key] * a for key in values}
    if own is not None:
        piece_values[KEY] = own
    piece_deltas = {key: D[key] * (b - a) for key in D}
    found, landings = [], {}
    got = dict(carry.increments(piece_values, piece_deltas, found, 0, landings))
    return got, found, landings, piece_values

KEY = keys['carry.travel']
whole, found, whole_landings, _ = over(0.0, 1.0, v0)
print('\nWHOLE stretch  [0, 1]')
print('  increment', whole[keys['carry.travel']])
print('  landing  ', whole_landings.get(KEY))
print('  crossings', [(c.primitive, c.level, c.t) for c in found])

print('\nPIECE BY PIECE, cut at 0.25 and 0.6, the in-block coordinate ADVANCED')
total = 0.0
own = v0[KEY]
final_landing = None
for a, b in ((0.0, .25), (.25, .6), (.6, 1.0)):
    got, found, landings, piece_values = over(a, b, v0, own)
    increment = got[KEY]
    landing = landings.get(KEY)
    total += increment
    own = landing if landing is not None else own + increment
    if landing is not None:
        final_landing = own
    rescaled = [(c.primitive, c.level, a + c.t * (b - a)) for c in found]
    print(f'  [{a}, {b}] increment={increment!r} landing={landing!r} '
          f'-> own={own!r} crossings(rescaled)={rescaled}')
print(f'  sum over pieces = {total!r}   final landing = {final_landing!r}')
print(f'  whole stretch   = {whole[KEY]!r}   landing = '
      f'{whole_landings.get(KEY)!r}')
print(f'  own at end, piecewise = {own!r}, whole = '
      f'{v0[KEY] + whole[KEY]!r}')

print('\nTHE SAME PIECES, the in-block coordinate NOT advanced -- the one '
      'thing\nthe implementation must not get wrong')
total = 0.0
for a, b in ((0.0, .25), (.25, .6), (.6, 1.0)):
    got, _found, _landings, _ = over(a, b, v0)
    total += got[KEY]
    print(f'  [{a}, {b}] increment={got[KEY]!r}')
print(f'  sum over pieces = {total!r}   (whole stretch = {whole[KEY]!r})')
