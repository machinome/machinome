"""The proposed design applied at its three seams, as a pytest plugin,
so the existing suites can be run against it BEFORE any framework file
is changed.

    PYTHONPATH="<worktree>:<evidence>" <venv>/bin/python -m pytest \
        tests/<file> -q -p proposed_design

Decision 1  -- `Joint.clear` drops by the joint's own declaration slot.
Decision 2/3 -- `restore_children_checkpoints` re-places each restored
                child's joints from the coordinates it holds.
Decision 6  -- `clear_solved` clears the joint of every coordinate whose
                value it drops (revision 1, direction (ii)).
"""
import solid_node.motion.couplings as couplings
import solid_node.node.assembly as assembly_module
from solid_node.manager.test import Test as Runner
from solid_node.motion.joints import Joint, declared_joints
from solid_node.motion.ports import get_coordinate, run_owned


def clear_by_mark(self, node):
    node.__dict__.get('_joint_motion', {}).pop(self.name, None)
    slot = list(declared_joints(type(node))).index(self.name)
    node.operations[:] = [
        operation for operation in node.operations
        if not (getattr(operation, '_motion', False)
                and getattr(operation, '_joint_slot', None) == slot)]


def replace_from_coordinates(node):
    for joint in declared_joints(type(node)).values():
        held = [get_coordinate(node, name)._value
                for name in joint.coordinates]
        if any(one is None for one in held):
            joint.clear(node)
        else:
            joint.place(node, held[0] if len(held) == 1 else None)


def restore_children_checkpoints(self, node):
    for child, operations in getattr(
            self, '_children_operations', {}).items():
        child.operations[:] = list(operations)
        replace_from_coordinates(child)


def clear_solved(assembly):
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


Joint.clear = clear_by_mark
Runner.restore_children_checkpoints = restore_children_checkpoints
couplings.clear_solved = clear_solved
assembly_module.clear_solved = clear_solved
