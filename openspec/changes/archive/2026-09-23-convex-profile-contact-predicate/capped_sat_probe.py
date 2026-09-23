"""Bounded SAT graph probe using actual intersection-cover triangles only.

This is an in-memory diagnostic, not a contact law or geometry certificate.
It stops at 256 polygon pairs, about 50,000 unique nodes, or 12 CPU seconds.
"""
import json
import math
import sys
import time
from machinome import math as mm
from machinome.expression_graph import postorder
from machinome.scad_expression import symbol


def fold(fn, values):
    values = list(values)
    while len(values) > 1:
        values = [fn(values[i], values[i + 1]) if i + 1 < len(values)
                  else values[i] for i in range(0, len(values), 2)]
    return values[0]


def placed(points, angle):
    c, s = mm.cos(angle), mm.sin(angle)
    return [(c*x-s*y, s*x+c*y) for x, y in points]


def axes(poly):
    return [(poly[(i+1) % len(poly)][1]-poly[i][1],
             poly[i][0]-poly[(i+1) % len(poly)][0])
            for i in range(len(poly))]


def gap(a, b):
    gaps = []
    for axis in axes(a)+axes(b):
        pa = [x*axis[0]+y*axis[1] for x, y in a]
        pb = [x*axis[0]+y*axis[1] for x, y in b]
        gaps.append(mm.max(fold(mm.min,pb)-fold(mm.max,pa),
                           fold(mm.min,pa)-fold(mm.max,pb)))
    return -fold(mm.max,gaps)


reports = {row['part']:row for row in
           map(json.loads, open(sys.argv[1], encoding='utf8'))}
gear = reports['FittedCounterPinion']
drum = reports['NineToothTurnsStepDrumSegment']
gtris = [p for p in gear['polygons'] if len(p)==3][:16]
dtris = [p for p in drum['polygons'] if len(p)==3][:16]
ga, da = symbol('gear_angle'), symbol('drum_angle')
gpoints, dpoints = placed(gear['points'], ga), placed(drum['points'], da)
root = None
count = 0
start = time.process_time()
for gp in gtris:
    for dp in dtris:
        a, b = [gpoints[i] for i in gp], [dpoints[i] for i in dp]
        pair = gap(a,b)
        root = pair if root is None else mm.max(root,pair)
        count += 1
        if count in (16,64,128,256):
            nodes = len(tuple(postorder([root._expression_node])))
            then = time.process_time()
            value = root.evaluate({'gear_angle':12.0,'drum_angle':33.0})
            eval_cpu = time.process_time()-then
            warm_start = time.process_time()
            for _ in range(10):
                root.evaluate({'gear_angle':12.0,'drum_angle':33.0})
            warm_cpu = time.process_time()-warm_start
            print(json.dumps(dict(pairs=count,unique_nodes=nodes,
                                  assembly_cpu_s=then-start,
                                  one_evaluation_cpu_s=eval_cpu,
                                  ten_warm_evaluations_cpu_s=warm_cpu,
                                  value=value)),flush=True)
            if nodes >= 50000 or time.process_time()-start >= 12:
                sys.exit(0)
assert count == 256
