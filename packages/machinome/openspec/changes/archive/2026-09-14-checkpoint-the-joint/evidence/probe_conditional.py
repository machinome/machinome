"""Finding A: does the proposed restore seam strand a re-placed operation
when the NEXT enumeration does not re-bind the joint?

Run from `evidence/bench/` with the worktree and the bench on PYTHONPATH:

    cd openspec/changes/checkpoint-the-joint/evidence/bench
    PYTHONPATH="<worktree>:$PWD" <venv>/bin/python ../probe_conditional.py

Part 1 runs the runner's real checkpoint pair over an untimed root whose
author's `simulate()` binds a root-level leaf's joint only under a guard,
across two instants: the first binds, the second does not.  It runs the
sequence TWICE -- once with the framework as it stands, once with the
proposed design applied at the seam (decision 1's mark-based `clear` and
decisions 2/3's re-place-after-restore).

Part 2 measures what `slot.binder` and `slot._bound_by` hold for every
binding path a joint coordinate has.
"""
import logging

logging.disable(logging.INFO)

from solid_node.manager.test import Test as Runner                # noqa: E402
from solid_node.motion.joints import Joint, declared_joints       # noqa: E402
from solid_node.motion.ports import (binding_as, get_coordinate,  # noqa: E402
                                     run_owned, set_coordinate)
from solid_node.simulation import Sim                             # noqa: E402
from solid_node.simulation.enumeration import (                   # noqa: E402
    bind_declared_defaults)

from conditional import (Conditional, Formula,                    # noqa: E402
                         Wired)


class Checkpoints:
    save = Runner.save_children_checkpoints
    restore = Runner.restore_children_checkpoints


def motion(node):
    return [(operation.serialized,
             getattr(operation, '_joint_slot', None),
             'tagged' if getattr(operation, '_animator', None) is not None
             else 'untagged')
            for operation in node.operations
            if getattr(operation, '_motion', False)]


def show(label, node, coordinate):
    slot = get_coordinate(node, coordinate)
    print(f"    {label}: {coordinate}={slot._value!r}, "
          f"motion={motion(node)}")


def built(klass):
    node = klass()
    bind_declared_defaults(node)
    node.set_keyframe(0)
    node._prepare()
    return node


#####################################################################
# The proposed design, applied at the seam and nowhere else.

_original_clear = Joint.clear


def clear_by_mark(self, node):
    """Decision 1: drop every motion operation carrying this joint's
    own declaration slot, whatever happened to the list."""
    node.__dict__.get('_joint_motion', {}).pop(self.name, None)
    slot = list(declared_joints(type(node))).index(self.name)
    node.operations[:] = [
        operation for operation in node.operations
        if not (getattr(operation, '_motion', False)
                and getattr(operation, '_joint_slot', None) == slot)]


def replace_from_coordinates(node):
    """Decision 2: the seam. Re-place every joint the node declares from
    the values its own coordinates hold; clear one whose coordinates are
    not all bound."""
    for joint in declared_joints(type(node)).values():
        held = [get_coordinate(node, name)._value
                for name in joint.coordinates]
        if any(one is None for one in held):
            joint.clear(node)
        else:
            joint.place(node, held[0] if len(held) == 1 else None)


def restore_with_seam(runner, root):
    """Decision 3: the content restore unchanged, then the seam."""
    runner.restore(root)
    for child in root.children:
        replace_from_coordinates(child)


#####################################################################
# Part 1: the guarded binding across two instants.

def sequence(root, runner, restore):
    """What `run_test` does for one method over instants [0, 1]."""
    runner.save(root)
    root.set_keyframe(0)
    show('instant 0 (the guard binds)', root.gate, 'travel')
    restore(runner, root)
    show('instant 0: the runner restores', root.gate, 'travel')
    root.set_keyframe(1)
    show('instant 1 (the guard does NOT bind: rest)', root.gate, 'travel')
    restore(runner, root)
    show('instant 1: the runner restores', root.gate, 'travel')


print('=== A1. TODAY: an untimed guarded binding, two instants')
today = built(Conditional)
sequence(today, Checkpoints(), lambda runner, root: runner.restore(root))

print('=== A2. UNDER THE PROPOSED DESIGN (decisions 1 + 2 + 3)')
Joint.clear = clear_by_mark
proposed = built(Conditional)
sequence(proposed, Checkpoints(), restore_with_seam)
Joint.clear = _original_clear


#####################################################################
# Part 2: what every binding path records.

print('=== A3. What `slot.binder` and `slot._bound_by` hold, by path')

from machine import Bench, BenchBody                              # noqa: E402


def report(label, slot):
    binder = slot.binder
    print(f"    {label}:")
    print(f"        value      = {slot._value!r}")
    print(f"        binder     = {type(binder).__name__}  {binder!r}")
    print(f"        _bound_by  = {type(slot._bound_by).__name__}")
    print(f"        run_owned  = {run_owned(slot)}")


# 1. the author's own simulate() assignment (untimed, in phase)
author = built(Conditional)
author.set_keyframe(0)
report("author's simulate() assignment", get_coordinate(author.gate,
                                                        'travel'))

# 2. a relation (a driver driving a joint coordinate)
related = built(BenchBody)
related.set_keyframe(0)
report('a relation (push.drives(slide.travel))',
       get_coordinate(related.slide, 'travel'))

# 3. a hand assignment, outside any phase
hand = built(BenchBody)
hand.slide.travel = 7.0
report('a hand assignment outside any phase',
       get_coordinate(hand.slide, 'travel'))

# 4. the run
running = built(Bench)
sim = Sim(running, 0.1)
sim.move('push', to=12.0, duration=0.2)
sim.run(0.2)
report('a running simulation', get_coordinate(running.slide, 'travel'))

# 5. a publication (the document producer's CoordinateDelivery)
from solid_node.core.serializer import _coordinate_publication     # noqa: E402
from solid_node.core.serializer import _publish_coordinates        # noqa: E402

published = built(BenchBody)
published.set_keyframe(0)
delivery = _coordinate_publication(published)
_publish_coordinates(delivery, published.slide, ())
report('a publication (document producer)',
       get_coordinate(published.slide, 'travel'))
delivery.restore()
report('the same slot after the publication restores',
       get_coordinate(published.slide, 'travel'))


# 6. a wiring into a leaf's joint coordinate
wired = built(Wired)
wired.set_keyframe(0)
report("a wiring into a leaf's joint coordinate",
       get_coordinate(wired.gate, 'travel'))

# 7. a derived formula driving a leaf's joint coordinate
formula = built(Formula)
formula.set_keyframe(0)
report('a derived formula driving a joint coordinate',
       get_coordinate(formula.gate, 'travel'))

# 8. a hand assignment on a slot NO phase ever bound
fresh = built(Conditional)
fresh.set_keyframe(1)          # the guard does not bind: nothing in phase
show('the guarded leaf at instant 1', fresh.gate, 'travel')
report('the same slot, never bound in a phase', get_coordinate(fresh.gate,
                                                               'travel'))
fresh.gate.travel = 3.0
report('...then bound BY HAND outside any phase',
       get_coordinate(fresh.gate, 'travel'))


#####################################################################
# Part 3: direction (ii) applied -- the motion goes with the value.

print('=== A4. UNDER (ii): clear_solved clears the joint of every '
      'coordinate whose value it drops')

import solid_node.motion.couplings as couplings                   # noqa: E402
import solid_node.node.assembly as assembly_module                # noqa: E402

_original_clear_solved = couplings.clear_solved


def clear_solved_with_motion(assembly):
    """`clear_solved`, plus: the motion goes with the value.

    The records it already walks are SLOTS, and a slot carries `.node`
    and `.name` -- exactly the node and coordinate name a joint clear
    needs, so nothing new has to be recorded.
    """
    current = couplings._current_enumeration()
    for slot in assembly.__dict__.pop('_solver_bound', ()):
        if slot._enum_marker is current:
            continue
        if run_owned(slot):
            continue
        slot._value = None
        slot.binder = None
        node = slot.node
        for joint in declared_joints(type(node)).values():
            if slot.name in joint.coordinates:
                joint.clear(node)
                break


couplings.clear_solved = clear_solved_with_motion
assembly_module.clear_solved = clear_solved_with_motion
Joint.clear = clear_by_mark
both = built(Conditional)
sequence(both, Checkpoints(), restore_with_seam)

print('=== A5. UNDER (ii): the untimed HAND binding of open question 2')
hand2 = built(BenchBody)
show('built', hand2.slide, 'travel')
hand2.slide.travel = 7.0
show('a test binds the coordinate by hand', hand2.slide, 'travel')
runner = Checkpoints()
runner.save(hand2)
hand2.slide.travel = 7.0
show('test 1: bound by hand again', hand2.slide, 'travel')
restore_with_seam(runner, hand2)
runner.save(hand2)
hand2.slide.travel = 7.0
show('test 2: bound by hand again', hand2.slide, 'travel')
hand2.set_keyframe(0)
show('test 2: after the next set_keyframe(0)', hand2.slide, 'travel')

print('=== A6. UNDER (ii): the running root of sections 1 and 7 is '
      'untouched by the new clear')
run_root = built(Bench)
runner = Checkpoints()
sim = Sim(run_root, 0.1)
sim.move('push', to=12.0, duration=0.2)
sim.run(0.2)
show('a scenario has stepped the run', run_root.slide, 'travel')
runner.save(run_root)
Sim(run_root, 0.1)
restore_with_seam(runner, run_root)
show('test 1: the runner restores', run_root.slide, 'travel')
runner.save(run_root)
Sim(run_root, 0.1)
show('test 2: a third scenario binds the bank', run_root.slide, 'travel')
restore_with_seam(runner, run_root)
run_root.set_keyframe(0)
show('test 2: after the next set_keyframe(0)', run_root.slide, 'travel')

couplings.clear_solved = _original_clear_solved
assembly_module.clear_solved = _original_clear_solved
Joint.clear = _original_clear
