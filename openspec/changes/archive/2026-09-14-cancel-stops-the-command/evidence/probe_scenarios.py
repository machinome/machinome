"""What cancellation does today, over the scenarios the fix must cover.

Run from this directory with the worktree on PYTHONPATH.
"""
from solid_node.node import AssemblyNode
from solid_node.motion.ports import Time
from solid_node.motion.joints import Prismatic
from solid_node.simulation import Driver, Sim


class Carriage(AssemblyNode):
    travel = Prismatic(axis=(1, 0, 0), range=(0, 12), unit="mm")


class Feed(AssemblyNode):
    time = Time.running()
    feed = Driver(default=0, unit="mm")
    other = Driver(default=0, unit="mm")
    carriage = Carriage()
    second = Carriage()
    feed.drives(carriage.travel)
    other.drives(second.travel)


def fresh(dt=0.02):
    return Sim(Feed(), dt=dt)


def show(label, sim, *handles):
    print(f'{label}:')
    for handle in handles:
        print(f'    {handle!r}')
    print(f'    state={sim.state} commands={sim.commands} tick={sim.tick}')


print('== 1. cancel before the first tick ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
move.cancel()
sim.run(0.02)
show('after one tick', sim, move)

print('== 2. cancel midway through a move ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
sim.run(0.06)
move.cancel()
sim.run(0.06)
show('three ticks, cancel, three ticks', sim, move)

print('== 3. cancel midway through a rate ==')
sim = fresh()
rate = sim.rate('feed', 10)
sim.run(0.06)
rate.cancel()
sim.run(0.06)
show('three ticks, cancel, three ticks', sim, rate)

print('== 4. immediate replacement after cancel ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
move.cancel()
try:
    second = sim.move('feed', by=1, duration=0.02)
except ValueError as error:
    print(f'    replacement refused: {error}')
else:
    show('replacement accepted', sim, move, second)

print('== 5. repeated cancel ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
print('   ', move.cancel() is move, move.cancel().status, len(sim.commands))

print('== 6. unrelated input continues ==')
sim = fresh()
one = sim.move('feed', by=5, duration=0.2)
two = sim.move('other', by=5, duration=0.2)
one.cancel()
sim.run(0.2)
show('feed cancelled, other left alone', sim, one, two)

print('== 7. a blocked command cancelled ==')
sim = fresh()
move = sim.move('feed', by=20, duration=0.2)
sim.run(0.2)
print('   ', repr(move), 'commands=', sim.commands)
move.cancel()
print('    after cancel:', repr(move))

print('== 8. a completed command cancelled ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
sim.run(0.2)
move.cancel()
print('   ', repr(move))

print('== 9. a zero-duration move cancelled ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0)
move.cancel()
print('   ', repr(move), 'commands=', sim.commands)

print('== 10. snapshot taken AFTER a cancel, restored ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
sim.run(0.04)
move.cancel()
shot = sim.snapshot()
print('    snapshot commands:', shot.commands)
sim.run(0.04)
sim.restore(shot)
print('    after restore:', repr(move), sim.commands, sim.state)
sim.run(0.04)
print('    two ticks past the restore:', sim.state, sim.commands)

print('== 11. snapshot taken BEFORE a cancel, restored after it ==')
sim = fresh()
move = sim.move('feed', by=5, duration=0.2)
sim.run(0.04)
shot = sim.snapshot()
move.cancel()
sim.restore(shot)
print('    after restore:', repr(move), sim.commands, sim.state)

print('== 12. determinism: the same script twice ==')
runs = []
for _ in range(2):
    sim = fresh()
    move = sim.move('feed', by=5, duration=0.2)
    sim.run(0.04)
    move.cancel()
    sim.run(0.1)
    runs.append((move.status, move.admitted, sim.state))
print('   ', runs[0] == runs[1], runs[0])
