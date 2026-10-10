"""Capture the placed operands of one named pair whose common is empty, as
BREP files, then stop the run. usage: MEASURE_PAIR=first,second
MEASURE_OUT=dir python capture.py test <model> --brep --no-verdict-store"""
import os, sys, time
import machinome.engine.brep as brep
OUT = os.environ['MEASURE_OUT']; os.makedirs(OUT, exist_ok=True)
TARGET = tuple(os.environ['MEASURE_PAIR'].split(','))
_intersect = brep.intersect_shapes
seen = [0]

def intersect_shapes(first, second, first_name, second_name):
    seen[0] += 1
    if (first_name, second_name) == TARGET or (second_name, first_name) == TARGET:
        f, s = brep.as_shape(first), brep.as_shape(second)
        common = brep._boolean('intersection', f, s, first_name, second_name)
        if not brep._solids(common):
            brep.write_brep(f, f'{OUT}/{first_name}.brep')
            brep.write_brep(s, f'{OUT}/{second_name}.brep')
            sys.stderr.write(f'CAPTURED {first_name},{second_name} after {seen[0]} commons\n')
            os._exit(0)
    return _intersect(first, second, first_name, second_name)

brep.intersect_shapes = intersect_shapes
from machinome.cli import manage
sys.argv = ['machinome'] + sys.argv[1:]
manage()
