"""What the runner's checkpoint does to a joint's placement.

Run from `evidence/bench/` (the fixture project) with the worktree and the
bench on PYTHONPATH:

    cd openspec/changes/checkpoint-the-joint/evidence/bench
    PYTHONPATH="<worktree>:$PWD" <venv>/bin/python ../probe_checkpoint.py

Every step below is the runner's OWN code: `save_children_checkpoints` and
`restore_children_checkpoints` are taken unchanged off `solid_node.manager.
test.Test`, and everything else is public API.
"""
import logging

logging.disable(logging.INFO)

from solid_node.manager.test import Test as Runner            # noqa: E402
from solid_node.motion.ports import get_coordinate            # noqa: E402
from solid_node.simulation import Sim                         # noqa: E402
from solid_node.simulation.enumeration import (               # noqa: E402
    bind_declared_defaults)

from machine import Bench, BenchBody                          # noqa: E402


class Checkpoints:
    """The runner's checkpoint pair, and nothing else of it."""

    save = Runner.save_children_checkpoints
    restore = Runner.restore_children_checkpoints


def motion(node):
    return [(operation.serialized,
             getattr(operation, '_joint_slot', None),
             'tagged' if getattr(operation, '_animator', None) is not None
             else 'untagged')
            for operation in node.operations
            if getattr(operation, '_motion', False)]


def show(label, node, coordinate=None):
    held = ('' if coordinate is None
            else f", coordinate {coordinate}="
                 f"{get_coordinate(node, coordinate)._value!r}")
    print(f"    {label}: {len(node.operations)} operations{held}, "
          f"motion={motion(node)}")


def built(klass):
    node = klass()
    bind_declared_defaults(node)
    node.set_keyframe(0)
    node._prepare()
    return node


print("=== 1. A running root: the checkpoint doubles a root-level leaf's "
      "joint displacement")
root = built(Bench)
runner = Checkpoints()
show('built', root.slide, 'travel')
sim = Sim(root, 0.1)
sim.move('push', to=12.0, duration=0.2)
sim.run(0.2)
show('a scenario has stepped the run', root.slide, 'travel')
runner.save(root)
Sim(root, 0.1)
show('test 1: a second scenario binds the bank', root.slide, 'travel')
runner.restore(root)
show('test 1: the runner restores', root.slide, 'travel')
runner.save(root)
Sim(root, 0.1)
show('test 2: a third scenario binds the bank', root.slide, 'travel')
runner.restore(root)
show('test 2: the runner restores', root.slide, 'travel')
runner.save(root)
Sim(root, 0.1)
show('test 3: a fourth scenario binds the bank', root.slide, 'travel')

print("=== 2. The same tree's SUB-ASSEMBLY leaf, through the same steps")
show('arm.slide', root.arm.slide, 'travel')

print("=== 3. A Free joint on a root-level leaf: several operations, one "
      "placement")
free = built(Bench)
runner = Checkpoints()
sim = Sim(free, 0.1)
sim.move('rise', to=6.0, duration=0.2)
sim.run(0.2)
show('a scenario has stepped the run', free.floater)
runner.save(free)
Sim(free, 0.1)
show('test 1: a second scenario binds the bank', free.floater)
runner.restore(free)
runner.save(free)
Sim(free, 0.1)
show('test 2: a third scenario binds the bank', free.floater)

print("=== 4. The UNTIMED control: the same steps, no run to bind the bank")
untimed = built(BenchBody)
runner = Checkpoints()
show('built', untimed.slide, 'travel')
for number in (1, 2, 3):
    runner.save(untimed)
    untimed.set_keyframe(0)
    show(f'test {number}: after set_keyframe(0)', untimed.slide, 'travel')
    runner.restore(untimed)
    show(f'test {number}: the runner restores', untimed.slide, 'travel')

print("=== 5. A running root the runner NEVER checkpoints")
clean = built(Bench)
sim = Sim(clean, 0.1)
sim.move('push', to=12.0, duration=0.2)
sim.run(0.2)
show('a scenario has stepped the run', clean.slide, 'travel')
for number in (1, 2, 3):
    Sim(clean, 0.1)
    show(f'scenario {number + 1}', clean.slide, 'travel')

print("=== 6. An UNTIMED root whose test binds a coordinate BY HAND "
      "(the one out-of-phase placement an untimed tree has)")
hand = built(BenchBody)
runner = Checkpoints()
show('built', hand.slide, 'travel')
hand.slide.travel = 7.0
show('a test binds the coordinate by hand', hand.slide, 'travel')
runner.save(hand)
hand.slide.travel = 7.0
show('test 1: bound by hand again', hand.slide, 'travel')
runner.restore(hand)
runner.save(hand)
hand.slide.travel = 7.0
show('test 2: bound by hand again', hand.slide, 'travel')
hand.set_keyframe(0)
show('test 2: after the next set_keyframe(0)', hand.slide, 'travel')
