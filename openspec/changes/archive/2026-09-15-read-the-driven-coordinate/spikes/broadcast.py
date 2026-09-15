"""Spike 6: can a BROADCAST source member be paired PER COPY with the
driven member it repeats over?

The couplings delta admits one exception to "a broadcast is never a
source": the very broadcast the relation drives, which resolves per copy
as that copy's read of ITSELF.  This spike measures whether that pairing
is implementable at the RECORD level -- one record per copy, the copy's
own coordinate on both sides -- with the machinery that already exists
(`BroadcastRef.resolve_all`, `BroadcastRef.copy_nodes`,
`_resolve_ends_per_copy`), or whether it needs a new resolution path.

Two refusals are monkeypatched out at runtime -- no worktree file is
touched: `BroadcastRef.check('driver')` and `_refuse_shared_coordinate`.
Everything else is the framework's own.
"""

import json

from solid_node.motion import couplings
from solid_node.motion.couplings import BroadcastRef, _end_refs

couplings._refuse_shared_coordinate = lambda driver_ref, driven_ref: None

_check = BroadcastRef.check
BroadcastRef.check = lambda self, role: None if role == 'driver' \
    else _check(self, role)

from solid_node.motion.joints import Revolute          # noqa: E402
from solid_node.motion.ports import Time               # noqa: E402
from solid_node.node import AssemblyNode, Solid2Node    # noqa: E402
from solid_node.simulation import Driver               # noqa: E402
from solid2 import cylinder                            # noqa: E402


def gate(sources, target):
    return lambda ring, wheel: ring * wheel


class Dial(Solid2Node):
    turn = Revolute(axis=(0, 0, 1), unit='deg')

    def simulate(self):
        if self.turn.value is None:
            self.turn = 0.0

    def render(self):
        return cylinder(r=5, h=2)


class Register(AssemblyNode):
    time = Time.running()
    ring = Driver(default=0.0, unit='deg')
    wheels = Dial().repeat(4)

    clearing = (ring & wheels.turn).drives(wheels.turn, law=gate)

    def render(self):
        pass


def source_per_copy(ref, instance, driven_keys):
    """The candidate implementation, in full: each member of the SOURCE
    group resolved PER COPY where it is the broadcast the relation
    drives, and once for every copy where it is not.

    Eleven lines, over `BroadcastRef.resolve_all` -- the same call the
    driven side already makes."""
    members = _end_refs(ref)
    per_member = [member.resolve_all(instance)
                  if isinstance(member, BroadcastRef)
                  and member.key() in driven_keys else None
                  for member in members]
    count = len(next(found for found in per_member if found is not None))
    columns = [[member.resolve(instance)] * count if found is None else found
               for member, found in zip(members, per_member)]
    return list(zip(*columns))


def patched_resolve(self, instance):
    """`Relation.resolve`'s broadcast branch with the source group
    resolved per copy too. Everything else is the framework's own."""
    driven_keys = {member.key() for member in _end_refs(self.driven)}
    per_copy_driven = couplings._resolve_ends_per_copy(self.driven, instance)
    per_copy_source = source_per_copy(self.driver, instance, driven_keys)
    records = []
    for (copy_node, driven_ends), driver_ends in zip(per_copy_driven,
                                                     per_copy_source):
        returned = self.callable_law(couplings._law_argument(driver_ends),
                                     couplings._law_argument(driven_ends))
        law = couplings.as_law(returned, self.described())
        records.append(couplings.RelationRecord(
            self, driver_ends, driven_ends, law, copy=copy_node))
    return records


if __name__ == '__main__':
    relation = Register.__dict__['clearing']
    driver_ref, driven_ref = relation.driver, relation.driven
    driven_members = _end_refs(driven_ref)
    source_members = _end_refs(driver_ref)
    out = {
        'driven key': repr(driven_members[0].key()),
        'source keys': [repr(member.key()) for member in source_members],
        'the repeated source member has the SAME key as the driven end':
            source_members[1].key() == driven_members[0].key(),
        'unpatched Relation.resolve': None,
    }
    try:
        Register()
    except Exception as failure:                        # noqa: BLE001
        out['unpatched Relation.resolve'] = {
            'error': type(failure).__name__, 'message': str(failure)}

    couplings.Relation.resolve = patched_resolve
    node = Register()
    records = node.__dict__['_relations']
    out['copies'] = len(records)
    pairing = []
    for record in records:
        pairing.append({
            'copy': record.copy.name,
            'source ends': [end.node.name for end in record.driver_ends],
            'driven end': record.driven_ends[0].node.name,
            'same owner on both sides':
                record.driver_ends[1].node is record.driven_ends[0].node,
            'same SLOT on both sides':
                record.driver_ends[1].slot is record.driven_ends[0].slot,
            "the plain source member is the parent's driver":
                record.driver_ends[0].node is node,
        })
    out['pairing'] = pairing
    out['every copy reads ITSELF'] = all(
        row['same SLOT on both sides'] for row in pairing)
    out['no two copies share a slot'] = len({
        id(record.driver_ends[1].slot) for record in records}) == len(records)
    print(json.dumps(out, indent=2, default=repr))
