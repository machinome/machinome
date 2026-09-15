"""Spike 2/3: the jump plan of a gated law, and where a self-read cut lands.

Nothing here changes the framework. It applies the framework's OWN
compile-time machinery (`_graph_of`, `_plan_of`, `JumpPlan`) to the law
shape the cycle proposes, with the driven coordinate entering as an
ordinary source token -- which is exactly what a self-read would compile
to -- and asks the three questions the design has to answer:

1. what the plan's jump nodes and level quantities are;
2. where the plan cuts a tick whose path takes the wheel through 360;
3. what float the wheel lands on if the run commits `start + rate * t*`
   rather than the surface value.
"""

import json
import math

from solid_node.math import clamp01
from solid_node.scad_expression import GraphValue, as_node, symbol
from solid_node.simulation.program import (_affine_in_sources, _graph_of,
                                           _plan_of, _only_jumps)
from solid2.core.object_base import OpenSCADConstant


def refuse(detail):
    raise AssertionError(detail)


def compiled(builder, names):
    tokens = [symbol(name) for name in names]
    value = builder(*tokens)
    graph, plan = _graph_of(value, refuse)
    return graph, plan


def described(plan):
    return [{'primitive': jump.primitive,
             'placeholder': jump.placeholder,
             'level': str(jump.argument),
             'affine': jump.affine} for jump in plan.jumps]


##############################################
# 1. The gate `wheel % 360 > 0`, with the wheel entering as a source.

def modulo_gate(rack, wheel):
    return rack * (wheel % 360 > 0)


##############################################
# 2. A WINDOW gate: engaged while the remaining travel is positive.
#    `remaining = modulo(-position, 10)` is the Curta's own form; here
#    the wheel is in degrees and one tooth is 36 degrees.

def window_gate(rack, wheel):
    remaining = (-wheel) % 360.0
    return rack * (remaining > 0)


##############################################
# 3. The 'level' form the Curta pose law uses: the wheel advances by
#    `remaining` over the rack's own pitch window, which is CONTINUOUS
#    in the rack and steps only in the wheel.

def pitched(rack, wheel):
    remaining = (-wheel) % 360.0
    return rack * clamp01(remaining / 36.0)


def plan_report(name, builder):
    graph, plan = compiled(builder, ('rack', 'wheel'))
    entry = {'law': name, 'graph': str(graph),
             'only_jumps': _only_jumps(as_node(graph))}
    if plan is None:
        entry['plan'] = None
        return entry
    entry['skeleton'] = str(plan.skeleton)
    entry['skeleton_affine'] = _affine_in_sources(as_node(plan.skeleton))
    entry['jumps'] = described(plan)
    return entry


##############################################
# The cut, with the wheel moving along the path as a source would.

def cuts_of(builder, start, delta):
    graph, plan = compiled(builder, ('rack', 'wheel'))
    if plan is None:
        return {'cuts': None}
    crossings = []
    increment = plan.increment(start, delta, 'spike', 'wheel', crossings, 1)
    return {'cuts': list(plan.cuts(start, delta, 'spike', 'wheel')),
            'increment': increment,
            'crossings': [(c.primitive, c.level, c.t) for c in crossings]}


##############################################
# 3. Where the float lands.

def landing():
    start, surface, travel = 108.0, 360.0, 500.0
    t_star = (surface - start) / travel
    landed = start + travel * t_star
    # the same with the ratio spelled out, as an affine edge computes it
    ratio = 1.0
    t_ratio = (surface - start) / (ratio * travel)
    landed_ratio = start + ratio * travel * t_ratio
    return {'t_star': t_star,
            'start + travel * t_star': landed,
            'exact?': landed == surface,
            'ulps_off': 0 if landed == surface else
                        round((landed - surface) / math.ulp(surface)),
            'with an explicit ratio': landed_ratio,
            'ratio path exact?': landed_ratio == surface,
            'level at the landed value': landed % 360.0,
            'gate reads at the landed value': float(landed % 360.0 > 0)}


def awkward_landing():
    """A surface a division cannot reproduce: 0.1-shaped arithmetic."""
    found = []
    for start, travel, surface in ((108.0, 500.0, 360.0),
                                   (3.7, 1.1, 36.0),
                                   (0.0, 7.0, 360.0),
                                   (359.9, 0.30000000000000004, 360.0),
                                   (12.345, 97.531, 360.0)):
        t_star = (surface - start) / travel
        landed = start + travel * t_star
        found.append({'start': start, 'travel': travel, 'surface': surface,
                      't_star': t_star, 'landed': landed,
                      'exact?': landed == surface,
                      'ulps': 0 if landed == surface
                              else round((landed - surface)
                                         / math.ulp(surface)),
                      'remainder at landed': landed % surface,
                      'gate (> 0) at landed': float(landed % surface > 0)})
    return found


if __name__ == '__main__':
    out = {
        'plans': [plan_report('rack * (wheel % 360 > 0)', modulo_gate),
                  plan_report('rack * ((-wheel) % 360 > 0)', window_gate),
                  plan_report('rack * clamp01(((-wheel) % 360) / 36)',
                              pitched)],
        'cut_modulo_gate': cuts_of(
            modulo_gate, {'rack': 0.0, 'wheel': 108.0},
            {'rack': 500.0, 'wheel': 500.0}),
        'cut_pitched': cuts_of(
            pitched, {'rack': 0.0, 'wheel': 108.0},
            {'rack': 500.0, 'wheel': 500.0}),
        'landing': landing(),
        'awkward_landings': awkward_landing(),
    }
    print(json.dumps(out, indent=2, default=repr))
