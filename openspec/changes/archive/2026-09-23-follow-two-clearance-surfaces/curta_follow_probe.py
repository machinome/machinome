"""Read-only originating-project Follow proof; not a framework product test.

Run from this framework worktree with the project's path on PYTHONPATH and
SOLID_BUILD_DIR set to an absolute framework-worktree-local build directory.
The project trial/profile source is imported but never edited.
"""

from machinome.motion.joints import Bound
from machinome.simulation import Follow, Sim
from simulation.running import OperatingCurta
from simulation.positioning_ball_trial import RadialCarriageTrial
from simulation.positioning_ball_profiles import bell_limit, collar_limit


class FollowTrial(OperatingCurta):
    __module__ = 'simulation.positioning_ball_trial'
    carriage = RadialCarriageTrial()
    carriage.positioning.p_6mm_ball_419094.slide.constrain(range=(
        Bound(lambda travel, turn: bell_limit(turn),
              reads=(OperatingCurta.carry_mechanism.tens_bell.turn,)),
        Bound(lambda travel, lift: collar_limit(lift),
              reads=(carriage.registers.lift,))))
    (OperatingCurta.carry_mechanism.tens_bell.turn & carriage.registers.lift &
     carriage.positioning.p_6mm_ball_419094.slide).drives(
        carriage.positioning.p_6mm_ball_419094.slide,
        law=Follow(lower=lambda turn, lift: bell_limit(turn),
                   upper=lambda turn, lift: collar_limit(lift)))


if __name__ == '__main__':
    sim = Sim(FollowTrial(), dt=.1)
    ball = 'carriage.positioning.p_6mm_ball_419094.slide'
    print('rest', sim.state[ball], flush=True)
    print('keys', len(sim.state), len(sim._running('probe').keys),
          len(sim.program.coordinates), flush=True)
    from machinome.simulation.trajectory import Motion, law_motion
    edge = next(edge for edge in sim.program.edges if edge.kind == 'follow')
    sources = {edge.names[0]: Motion.line(sim.state[edge.names[0]], -90),
               edge.names[1]: Motion.line(sim.state[edge.names[1]], 0)}
    bell, _ = law_motion(edge.lower_path, 0, sources,
                         edge.lower_graph.evaluate({
                             name: motion.start for name, motion in sources.items()}),
                         None, 0)
    cut = 6 / 90
    earlier = next(piece for piece in bell.pieces
                   if abs(piece[1] - cut) < 1e-12)
    later = next(piece for piece in bell.pieces
                 if abs(piece[0] - cut) < 1e-12)
    print('bell6 integrated', earlier[2](cut).hex(),
          later[2](cut).hex(), flush=True)
    print('bell6 authored', edge.lower_graph.evaluate({
        name: motion.at(cut) for name, motion in sources.items()}).hex(),
          flush=True)
    command = sim.move('carriage_elevation', to=6)
    print('lift', command.status, sim.state[ball], flush=True)
    saved = sim.snapshot()
    command = sim.move('crank_rotation', to=90, duration=.5)
    sim.run(.1)
    print('crank', command.status, sim.state['crank_rotation'],
          sim.state[ball], flush=True)
    stopped = sim.snapshot()
    sim.restore(saved)
    command = sim.move('crank_rotation', to=90, duration=.5)
    sim.run(.1)
    print('replay', command.status, sim.state['crank_rotation'],
          sim.snapshot() == stopped, flush=True)
    command = sim.move('carriage_elevation', to=0)
    print('relief', command.status, sim.state[ball], flush=True)
    command = sim.move('crank_rotation', to=90, duration=.5)
    sim.run(.5)
    print('post-relief', command.status, sim.state['crank_rotation'],
          sim.state[ball], flush=True)
    sim = Sim(FollowTrial(), dt=.1)
    command = sim.move('crank_rotation', by=90, duration=.5)
    sim.run(.5)
    outward = sim.state[ball]
    print('outward', command.status, sim.state['crank_rotation'], outward,
          flush=True)
    command = sim.move('crank_rotation', to=360, duration=1.5)
    sim.run(1.5)
    print('return', command.status, sim.state['crank_rotation'],
          sim.state[ball], sim.state[ball] == outward, flush=True)
