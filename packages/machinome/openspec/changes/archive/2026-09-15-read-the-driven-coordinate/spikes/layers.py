"""Do the TWO LAYERS compose? A law carrying an INDEPENDENT jump (a rack
station window over the ring alone) and a DEPENDENT one (the band gate
over the wheel's own angle), integrated by landing2's prototype walk.
"""

import json

import landing2 as L
from solid_node.math import floor
from solid_node.motion.joints import Revolute
from solid_node.motion.ports import Time
from solid_node.node import AssemblyNode
from solid_node.simulation import Driver, Sim
from solid_node.simulation.run import RunSnapshot

PERIOD = 360.0
GAP = 3.6
OPEN, SHUT = 100.0, 400.0          # the rack's station window, in ring degrees


def clearing(sources, target):
    def law(ring, wheel):
        # INDEPENDENT: the station window, a comparison over the ring alone.
        inside = (floor((ring - OPEN) / (SHUT - OPEN)) == 0.0)
        # DEPENDENT: the band about every multiple of PERIOD.
        shifted = wheel + GAP
        engaged = shifted - PERIOD * floor(shifted / PERIOD) >= 2 * GAP
        return ring * inside * engaged
    return law


class Dial(AssemblyNode):
    rotation = Revolute(axis=(0, 0, 1), unit='deg')

    def simulate(self):
        if self.rotation.value is None:
            self.rotation = 108.0

    def render(self):
        pass


class Clearing(AssemblyNode):
    time = Time.running()
    ring = Driver(default=0.0, unit='deg')
    wheel = Dial()
    (ring & wheel.rotation).drives(wheel.rotation, law=clearing)

    def render(self):
        pass


if __name__ == '__main__':
    sim = Sim(Clearing(), dt=1.0, record=64)
    plan = sim.program.edges[0].plans[0]
    out = {'skeleton': str(plan.skeleton),
           'jumps': [(j.primitive, j.placeholder, str(j.argument), j.affine)
                     for j in plan.jumps]}
    dependence = L._dependence(plan, 'wheel.rotation')
    out['dependent'] = [j.placeholder for j in plan.jumps
                        if dependence[j.placeholder]]
    out['independent'] = [j.placeholder for j in plan.jumps
                          if not dependence[j.placeholder]]

    def place(own, ring=0.0):
        sim.restore(RunSnapshot(sim.program.identity, sim.dt, 0,
                                (('ring', ring), ('wheel.rotation', own)), ()))

    runs = {}
    for name, own, travel in (('one tick through the whole window', 108.0, 900.0),
                              ('short of the window', 108.0, 90.0),
                              ('backward through the window', 108.0, -900.0)):
        place(own, 0.0 if travel > 0 else 900.0)
        handle = sim.move('ring', by=travel, duration=1.0)
        sim.run(1.0)
        landed = sim.state['wheel.rotation']
        runs[name] = {'wheel': landed, 'ring': sim.state['ring'],
                      'engaged after': L.engaged(landed, PERIOD, GAP),
                      'status': handle.status,
                      'crossings': [(c.primitive, c.t) for c in sim.crossings]}
        # And again, with the ring running on: the wheel must not move.
        sim.move('ring', by=travel, duration=1.0)
        sim.run(1.0)
        runs[name]['unchanged on a second sweep'] = (
            sim.state['wheel.rotation'] == landed)
    out['runs'] = runs

    # The same sweep taken in 1, 12 and 240 ticks.
    agreed = {}
    for ticks in (1, 12, 240):
        cadence = Sim(Clearing(), dt=1.0 / ticks)
        cadence.restore(RunSnapshot(cadence.program.identity, cadence.dt, 0,
                                    (('ring', 0.0),
                                     ('wheel.rotation', 108.0)), ()))
        cadence.move('ring', by=900.0, duration=1.0)
        cadence.run(1.0)
        agreed[ticks] = cadence.state['wheel.rotation']
    out['cadences'] = agreed
    window = 1e-9 * max(1.0, *(abs(v) for v in agreed.values()))
    out['cadences agree'] = (max(agreed.values()) - min(agreed.values())
                             <= window)
    print(json.dumps(out, indent=2, default=repr))
