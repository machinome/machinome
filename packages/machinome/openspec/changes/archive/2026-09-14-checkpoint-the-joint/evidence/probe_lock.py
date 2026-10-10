"""The wart's OWN reproduction, transcribed verbatim from workflow/warts.md
("Pin tumbler lock (2026-09-14 ...)", first bullet), with the operation list
printed at each step.

Run from the originating project, with this worktree on PYTHONPATH:

    cd <projects>/Locks/Pin_tumbler_lock
    PYTHONPATH="<worktree>" <venv>/bin/python <this file>

It writes nothing in the project beyond the build artifacts a `solid` command
writes there anyway; the run below found every STL up to date.
"""
from solid_node.core.loader import load_node


def show(node, label):
    ops = node.operations
    print(f"  {label}: {len(ops)} operations")
    for i, op in enumerate(ops):
        print(f"    [{i}] {type(op).__name__} {op.serialized!r} "
              f"motion={getattr(op, '_motion', False)} "
              f"slot={getattr(op, '_joint_slot', None)} "
              f"animator={type(getattr(op, '_animator', None)).__name__} "
              f"id={id(op)}")
    jm = node.__dict__.get('_joint_motion', {})
    print(f"    _joint_motion: {{{', '.join(f'{k}: {[id(o) for o in v]}' for k, v in jm.items())}}}")


a = load_node('simulation/lock.py:PinTumblerLock')
a.set_keyframe(0)
a._prepare()
a.build_stls()
print("-- after build")
show(a.d1, 'd1')
for n in (1, 2):
    saved = {c: list(c.operations) for c in a.children}
    a.set_keyframe(0)
    for c, ops in saved.items():
        c.operations[:] = list(ops)
    print(f"-- after test {n}")
    show(a.d1, 'd1')
a.set_keyframe(0)
print("-- final set_keyframe(0)")
show(a.d1, 'd1')
