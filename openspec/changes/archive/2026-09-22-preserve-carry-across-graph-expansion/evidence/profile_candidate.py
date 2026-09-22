"""Print per-law progress without changing candidate arithmetic."""
import json
import time
from unittest.mock import patch
from machinome.simulation import Sim
from machinome.simulation import trajectory
from simulation.tools.result_carry_graph_scope import result_graph

original = trajectory.law_motion

def measured(edge, index, motions, *args, **kwargs):
    started = time.monotonic()
    print(json.dumps({'enter': edge.driven[index],
                      'curved': [name for name, m in motions.items() if not m.affine],
                      'moving': [name for name, m in motions.items() if not m.constant],
                      'pieces': sum(len(m.pieces) for m in motions.values())}), flush=True)
    result = original(edge, index, motions, *args, **kwargs)
    print(json.dumps({'exit': edge.driven[index], 'seconds': time.monotonic()-started,
                      'affine': result[0].affine, 'constant': result[0].constant,
                      'start': result[0].start, 'end': result[0].end,
                      'pieces': len(result[0].pieces)}), flush=True)
    return result

sim = Sim(result_graph(6)(), dt=.1)
with patch.object(trajectory, 'law_motion', measured):
    for name, target in (('digit', 0), ('height', 9),
                         ('crank_angle', 90), ('crank_angle', 180)):
        print(json.dumps({'request': name, 'to': target}), flush=True)
        command = sim.move(name, to=target)
        print(json.dumps({'status': command.status, 'bank': dict(sim.state)}), flush=True)
