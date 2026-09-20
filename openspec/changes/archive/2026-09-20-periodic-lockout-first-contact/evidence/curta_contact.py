"""Cycle acceptance on real Curta parts; not a framework feature or test dependency.

Run from the Curta project root with this framework worktree and the project
on PYTHONPATH. The project remains responsible for its measured contact law.
No model file, geometry or operating manifest is changed by this diagnostic.
"""

import argparse
import json
import logging

from machinome.simulation import Sim
from simulation.result_locking import ResultLocking
from simulation.tools.locking_envelope import contact_reader


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--motion-only', action='store_true')
    args = parser.parse_args()
    logging.disable(logging.INFO)
    poses = []
    # Five different actual retained flats, plus both ends of the measured
    # withdrawal-phase acceptance range. The request is deliberately long.
    for turns, withdrawal in [(n, 120) for n in range(5)] + [(0, 115), (0, 123)]:
        sim = Sim(ResultLocking(), dt=.1, state={'digit': 3, 'crank_height': 0})
        sim.move('crank_angle', to=360*turns + withdrawal)
        sim.move('digit', to=0)
        held = sim.state['ones.turn']
        request = sim.move('crank_angle', to=360*turns + 840)
        assert request.status == 'blocked'
        assert sim.state['ones.turn'] == held
        pose = {'turns': turns, 'withdrawal': withdrawal,
                'crank': sim.state['crank_angle'], 'shaft': held,
                'status': request.status}
        poses.append(pose)
        print(json.dumps({'admitted_pose': pose}), flush=True)

    if args.motion_only:
        return

    # Sequential kernel preparation, complete printed bodies, no volume
    # threshold. The extra .2 degrees is a posed negative control, not a
    # movement ever admitted by the operating simulation.
    for kernel in ('exact', 'faceted'):
        reader = contact_reader(kernel)
        for pose in poses:
            volume = reader(pose['shaft'])
            stopped = volume(pose['crank'])
            beyond = volume(pose['crank'] + .2)
            print(json.dumps({'kernel': kernel, **pose,
                              'overlap_mm3': stopped,
                              'beyond_contact_mm3': beyond}), flush=True)
            assert stopped == 0, (kernel, pose, stopped)
            assert beyond > 0, (kernel, pose, beyond)


if __name__ == '__main__':
    main()
