"""Voron-2's six thread seats under `intersect_shapes`, both orders.

Builds the nut and screw pairs of the project's
`simulation/test_thread_seat_contacts.py` (an assembled
`ThreadSeatContacts`'s `.nuts` and `.screws`, each `cq_shape(part)`
translated by `-BED_DATUM` as that test places its bodies) and prints,
for each pair in each order, what `machinome.engine.brep.intersect_shapes`
returns or raises, with the refusal's point. Calls nothing that writes the
project's CACHE and builds no STL. Run from the project with
PYTHONPATH=<bench>:<project>, PYTHONDONTWRITEBYTECODE=1 and a scratch
SOLID_BUILD_DIR.
"""

import re
import sys
import time

sys.dont_write_bytecode = True

from machinome.engine import (BrepCommonInconsistency,  # noqa: E402
                              BrepCommonVerificationError)
from machinome.engine import brep  # noqa: E402
from simulation.configuration import BED_DATUM  # noqa: E402
from simulation.source_shapes import cq_shape  # noqa: E402
from simulation.thread_seat_contacts import ThreadSeatContacts  # noqa: E402

started = time.perf_counter()
node = ThreadSeatContacts()
node.assemble()
bodies = {}
for part in (*node.nuts, *node.screws):
    bodies[part.source_id] = cq_shape(part).copy().translate(
        tuple(-value for value in BED_DATUM)).wrapped
print(f'loaded {len(bodies)} bodies in {time.perf_counter() - started:.1f} s',
      flush=True)

for nut, screw in zip(node.nuts, node.screws):
    for left, right in ((nut.source_id, screw.source_id),
                        (screw.source_id, nut.source_id)):
        started = time.perf_counter()
        try:
            common = brep.intersect_shapes(bodies[left], bodies[right],
                                           str(left), str(right))
            verdict = (f'returned {brep.solid_count(common)} solids, volume '
                       f'{brep.solid_volume(common):.6g}')
        except BrepCommonInconsistency as error:
            point = re.search(r'solids: (\([^)]*\))', str(error)).group(1)
            verdict = f'BrepCommonInconsistency at {point}'
        except BrepCommonVerificationError as error:
            verdict = f'BrepCommonVerificationError: {error}'
        print(f'{left} {right}: {verdict} '
              f'({time.perf_counter() - started:.2f} s)', flush=True)
